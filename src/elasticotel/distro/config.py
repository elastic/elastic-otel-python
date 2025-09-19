# Copyright Elasticsearch B.V. and/or licensed to Elasticsearch B.V. under one
# or more contributor license agreements. See the NOTICE file distributed with
# this work for additional information regarding copyright
# ownership. Elasticsearch B.V. licenses this file to you under
# the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import logging
from dataclasses import dataclass

from opentelemetry import trace

from opentelemetry.sdk.trace.sampling import ParentBasedTraceIdRatio
from opentelemetry._opamp import messages
from opentelemetry._opamp.agent import OpAMPAgent
from opentelemetry._opamp.client import OpAMPClient
from opentelemetry._opamp.proto import opamp_pb2 as opamp_pb2


logger = logging.getLogger(__name__)

_LOG_LEVELS_MAP: dict[str, int] = {
    "trace": 5,
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warn": logging.WARNING,
    "error": logging.ERROR,
    "fatal": logging.CRITICAL,
    "off": 1000,
}

DEFAULT_SAMPLING_RATE = 1.0
DEFAULT_LOGGING_LEVEL = "info"

LOGGING_LEVEL_CONFIG_KEY = "logging_level"
SAMPLING_RATE_CONFIG_KEY = "sampling_rate"


@dataclass
class ConfigItem:
    value: str


@dataclass
class ConfigUpdate:
    error_message: str = ""


# TODO: this should grow into a proper configuration store initialized from env vars and so on
@dataclass
class Config:
    sampling_rate = ConfigItem(value=str(DEFAULT_SAMPLING_RATE))
    logging_level = ConfigItem(value=DEFAULT_LOGGING_LEVEL)

    def to_dict(self):
        return {LOGGING_LEVEL_CONFIG_KEY: self.logging_level.value, SAMPLING_RATE_CONFIG_KEY: self.sampling_rate.value}


_config = Config()


def _handle_logging_level(remote_config) -> ConfigUpdate:
    _config = _get_config()
    # when config option has default value you don't get it so need to handle the default
    config_logging_level = remote_config.get(LOGGING_LEVEL_CONFIG_KEY, DEFAULT_LOGGING_LEVEL)
    logging_level = _LOG_LEVELS_MAP.get(config_logging_level)

    if logging_level is None:
        logger.error("Logging level not handled: %s", config_logging_level)
        error_message = f"Logging level not handled: {config_logging_level}"
    else:
        # update upstream and distro logging levels
        logging.getLogger("opentelemetry").setLevel(logging_level)
        logging.getLogger("elasticotel").setLevel(logging_level)
        _config.logging_level = ConfigItem(value=config_logging_level)
        error_message = ""
    return ConfigUpdate(error_message=error_message)


def _handle_sampling_rate(remote_config) -> ConfigUpdate:
    _config = _get_config()
    config_sampling_rate = remote_config.get(SAMPLING_RATE_CONFIG_KEY, str(DEFAULT_SAMPLING_RATE))
    sampling_rate = DEFAULT_SAMPLING_RATE
    if config_sampling_rate is not None:
        try:
            sampling_rate = float(config_sampling_rate)
            if sampling_rate < 0 or sampling_rate > 1.0:
                raise ValueError()
        except ValueError:
            logger.error("Invalid `sampling_rate` from config `%s`", config_sampling_rate)
            return ConfigUpdate(error_message=f"Invalid sampling_rate {config_sampling_rate}")

    sampler = getattr(trace.get_tracer_provider(), "sampler", None)
    if sampler is None:
        logger.debug("Cannot get sampler from tracer provider.")
        return ConfigUpdate()

    # FIXME: this needs to be updated for the consistent probability samplers
    if not isinstance(sampler, ParentBasedTraceIdRatio):
        logger.warning("Sampler %s is not supported, not applying sampling_rate.", type(sampler))
        return ConfigUpdate()

    # since sampler is parent based we need to update its root sampler
    root_sampler = sampler._root  # type: ignore[reportAttributeAccessIssue]
    if root_sampler.rate != sampling_rate:  # type: ignore[reportAttributeAccessIssue]
        # we don't have a proper way to update it :)
        root_sampler._rate = sampling_rate  # type: ignore[reportAttributeAccessIssue]
        root_sampler._bound = root_sampler.get_bound_for_rate(root_sampler._rate)  # type: ignore[reportAttributeAccessIssue]
        logger.debug("Updated sampler rate to %s", sampling_rate)
        _config.sampling_rate = ConfigItem(value=config_sampling_rate)
    return ConfigUpdate()


def _report_full_state(message: opamp_pb2.ServerToAgent):
    return message.flags & opamp_pb2.ServerToAgentFlags_ReportFullState


def _get_config():
    global _config
    return _config


def opamp_handler(agent: OpAMPAgent, client: OpAMPClient, message: opamp_pb2.ServerToAgent):
    # server wants us to report full state as it cannot recognize us as agent because
    # e.g it may have been restarted and lost state.
    if _report_full_state(message):
        # here we're not returning explicitly but usually we don't get a remote config when we get the flag set
        payload = client._build_full_state_message()
        agent.send(payload=payload)

    # we check config_hash because we need to track last received config and remote_config seems to be always truthy
    if not message.remote_config or not message.remote_config.config_hash:
        return

    _config = _get_config()
    error_messages = []
    for config_filename, remote_config in messages._decode_remote_config(message.remote_config):
        # we don't have standardized config values so limit to configs coming from our backend
        if config_filename == "elastic":
            logger.debug("Config %s: %s", config_filename, remote_config)
            config_update = _handle_logging_level(remote_config)
            if config_update.error_message:
                error_messages.append(config_update.error_message)

            config_update = _handle_sampling_rate(remote_config)
            if config_update.error_message:
                error_messages.append(config_update.error_message)

    error_message = "\n".join(error_messages)
    status = opamp_pb2.RemoteConfigStatuses_FAILED if error_message else opamp_pb2.RemoteConfigStatuses_APPLIED
    updated_remote_config = client._update_remote_config_status(
        remote_config_hash=message.remote_config.config_hash, status=status, error_message=error_message
    )

    # update the cached effective config with what we updated
    effective_config = {"elastic": _config.to_dict()}
    client._update_effective_config(effective_config)

    # if we changed the config send an ack to the server so we don't receive the same config at every heartbeat response
    if updated_remote_config is not None:
        payload = client._build_remote_config_status_response_message(updated_remote_config)
        agent.send(payload=payload)
