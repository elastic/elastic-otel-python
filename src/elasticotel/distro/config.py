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
import os
from dataclasses import dataclass
from typing import cast

from opentelemetry import trace
from opentelemetry._opamp import messages
from opentelemetry._opamp.agent import OpAMPAgent
from opentelemetry._opamp.callbacks import MessageData, OpAMPCallbacks
from opentelemetry._opamp.client import OpAMPClient
from opentelemetry._opamp.exceptions import (
    OpAMPRemoteConfigDecodeException,
    OpAMPRemoteConfigParseException,
)
from opentelemetry._opamp.proto import opamp_pb2

try:
    from opentelemetry.instrumentation.logging.handler import LoggingHandler  # type: ignore[reportAssignmentType]
except ImportError:

    class LoggingHandler:
        pass


from opentelemetry.sdk._logs import LoggingHandler as SDKLoggingHandler
from opentelemetry.sdk.environment_variables import OTEL_LOG_LEVEL, OTEL_TRACES_SAMPLER_ARG
from opentelemetry.sdk.trace import _TracerConfig
from opentelemetry.sdk.util._configurator import ConfiguratorRulesT
from opentelemetry.sdk.util.instrumentation import _scope_name_matches_glob

from elasticotel.distro.environment_variables import (
    ELASTIC_OTEL_SPAN_NAME_GROUPS,
    ELASTIC_OTEL_USE_PATH_AS_SPAN_NAME,
)
from elasticotel.distro.sanitization import _sanitize_headers_env_vars
from elasticotel.sdk.sampler import DefaultSampler
from elasticotel.sdk.trace import tracer_configurator
from elasticotel.sdk.trace.span_name import parse_span_name_groups, span_name_settings

logger = logging.getLogger(__name__)

_LOG_LEVELS_MAP: dict[str, int] = {
    "trace": 5,
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warn": logging.WARNING,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "fatal": logging.CRITICAL,
    "off": 1000,
}

DEFAULT_SAMPLING_RATE = 1.0
DEFAULT_LOGGING_LEVEL = "warn"
DEFAULT_USE_PATH_AS_SPAN_NAME = "false"
DEFAULT_SPAN_NAME_GROUPS = ""

DEACTIVATE_INSTRUMENTATIONS_CONFIG_KEY = "deactivate_instrumentations"
LOGGING_LEVEL_CONFIG_KEY = "logging_level"
SAMPLING_RATE_CONFIG_KEY = "sampling_rate"
USE_PATH_AS_SPAN_NAME_CONFIG_KEY = "use_path_as_span_name"
SPAN_NAME_GROUPS_CONFIG_KEY = "span_name_groups"

_config: Config | None = None


def _parse_bool(value: object) -> bool | None:
    """Parses a boolean config value, returning None if it is not a valid boolean"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        value = value.strip().lower()
        if value == "true":
            return True
        if value == "false":
            return False
    return None


class ConfigItem:
    def __init__(self, default: str, from_env_var: str | None = None):
        self._default = default
        self._env_var = from_env_var

    def init(self):
        if self._env_var is not None:
            value = os.environ.get(self._env_var, self._default)
        else:
            value = self._default
        self.value = value

    def update(self, value: str):
        """Update value"""
        self.value = value

    def reset(self) -> str:
        """Value is not good, reset to default"""
        self.value = self._default
        return self.value


@dataclass
class ConfigUpdate:
    error_message: str = ""


# TODO: this should grow into a proper configuration store in the OpenTelemetry SDK
@dataclass
class Config:
    sampling_rate = ConfigItem(default=str(DEFAULT_SAMPLING_RATE), from_env_var=OTEL_TRACES_SAMPLER_ARG)
    # currently the sdk does not handle OTEL_LOG_LEVEL, so we use handle it on our own
    logging_level = ConfigItem(default=DEFAULT_LOGGING_LEVEL, from_env_var=OTEL_LOG_LEVEL)
    deactivate_instrumentations = ConfigItem(default="")
    use_path_as_span_name = ConfigItem(
        default=DEFAULT_USE_PATH_AS_SPAN_NAME, from_env_var=ELASTIC_OTEL_USE_PATH_AS_SPAN_NAME
    )
    span_name_groups = ConfigItem(default=DEFAULT_SPAN_NAME_GROUPS, from_env_var=ELASTIC_OTEL_SPAN_NAME_GROUPS)

    def to_dict(self):
        return {
            LOGGING_LEVEL_CONFIG_KEY: self.logging_level.value,
            SAMPLING_RATE_CONFIG_KEY: self.sampling_rate.value,
            DEACTIVATE_INSTRUMENTATIONS_CONFIG_KEY: self.deactivate_instrumentations.value,
            USE_PATH_AS_SPAN_NAME_CONFIG_KEY: self.use_path_as_span_name.value,
            SPAN_NAME_GROUPS_CONFIG_KEY: self.span_name_groups.value,
        }

    def log_env_vars(self):
        # log all the environment variables that starts with OTEL_ or ELASTIC_OTEL_ to ease troubleshooting
        env_vars = [
            _sanitize_headers_env_vars(k, v) for k, v in os.environ.items() if k.startswith(("OTEL_", "ELASTIC_OTEL_"))
        ]

        logger.info("EDOT Configuration")
        for k, v in sorted(env_vars):
            logger.info("%s: %s", k, v)

    def _setup_logging(self):
        # Ensure these loggers have a handler so logs are actually output
        # Without a handler, logs won't be displayed when running without a TTY (e.g., docker run without -it)
        # We only add a handler if neither the logger nor root has any handlers configured
        for _logger in self._get_loggers():
            if not _logger.handlers:
                handler = logging.StreamHandler()
                handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
                _logger.addHandler(handler)
                # We need to propagate if we have the OTel handler otherwise we don't see logs shipped, in the other
                # cases we shouldn't
                _logger.propagate = any(
                    isinstance(
                        _handler,
                        (
                            LoggingHandler,
                            SDKLoggingHandler,
                        ),
                    )
                    for _handler in logging.root.handlers
                )

        # do validation, we only validate logging_level because sampling_rate is handled by the sdk already
        logging_level = _LOG_LEVELS_MAP.get(self.logging_level.value)
        if logging_level is None:
            logger.error("Logging level not handled: %s", self.logging_level.value)
            self.logging_level.reset()
            return

        # apply logging_level changes since these are not handled by the sdk
        self.update_loggers(logging_level)

    @staticmethod
    def _get_loggers() -> list[logging.Logger]:
        return [logging.getLogger("opentelemetry"), logging.getLogger("elasticotel")]

    def update_loggers(self, logging_level: int):
        """Update upstream and distro logging levels"""
        for logger in self._get_loggers():
            logger.setLevel(logging_level)

    def _setup_span_names(self):
        use_path = _parse_bool(self.use_path_as_span_name.value)
        if use_path is None:
            logger.warning(
                "Invalid value for %s: %s, using %s",
                ELASTIC_OTEL_USE_PATH_AS_SPAN_NAME,
                self.use_path_as_span_name.value,
                DEFAULT_USE_PATH_AS_SPAN_NAME,
            )
            use_path = False
        self.use_path_as_span_name.update(value=str(use_path).lower())
        span_name_settings.set_use_path_as_span_name(use_path)
        span_name_settings.set_span_name_groups(parse_span_name_groups(self.span_name_groups.value))

    def __post_init__(self):
        # we need to initialize each config item when we instantiate the Config and not at declaration time
        self.sampling_rate.init()
        self.logging_level.init()
        self.deactivate_instrumentations.init()
        self.use_path_as_span_name.init()
        self.span_name_groups.init()

        self._setup_logging()
        self._setup_span_names()


def _handle_logging_level(remote_config) -> ConfigUpdate:
    _config = _get_config()
    # when config option has default value you don't get it so need to handle the default
    config_logging_level = remote_config.get(LOGGING_LEVEL_CONFIG_KEY, DEFAULT_LOGGING_LEVEL)
    logging_level = _LOG_LEVELS_MAP.get(config_logging_level)

    if logging_level is None:
        logger.error("Logging level not handled: %s", config_logging_level)
        error_message = f"Logging level not handled: {config_logging_level}"
    else:
        if _config:
            _config.update_loggers(logging_level)
            _config.logging_level.update(value=config_logging_level)
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

    config_sampling_rate = cast(str, config_sampling_rate)

    sampler = getattr(trace.get_tracer_provider(), "sampler", None)
    if sampler is None:
        logger.debug("Cannot get sampler from tracer provider.")
        return ConfigUpdate()

    if not isinstance(sampler, DefaultSampler):
        logger.warning("Sampler %s is not supported, not applying sampling_rate.", type(sampler))
        return ConfigUpdate()

    sampler.set_ratio(sampling_rate)
    logger.debug("Updated sampler rate to %s", sampling_rate)
    if _config:
        _config.sampling_rate.update(value=config_sampling_rate)
    return ConfigUpdate()


def _rules_from_deactivate_instrumentations(csv: str) -> ConfiguratorRulesT:
    patterns = [pattern.strip() for pattern in csv.split(",") if pattern.strip()]
    if not patterns:
        return []

    tracer_off_config = _TracerConfig(is_enabled=False)
    # remember that python instrumentations scope name are in the form opentelemetry.instrumentation.<module>
    return [(_scope_name_matches_glob(pattern), tracer_off_config) for pattern in patterns]


def _handle_deactivate_instrumentations(remote_config) -> ConfigUpdate:
    tracer_provider = trace.get_tracer_provider()
    set_tracer_configurator = getattr(tracer_provider, "_set_tracer_configurator", None)
    if set_tracer_configurator is None:
        logger.debug("Cannot get _set_tracer_configurator from tracer provider.")
        return ConfigUpdate()

    config_deactivate_instrumentations = remote_config.get(DEACTIVATE_INSTRUMENTATIONS_CONFIG_KEY, "")

    rules = _rules_from_deactivate_instrumentations(config_deactivate_instrumentations)
    current_tracer_configurator = tracer_configurator._get_tracer_configurator()
    try:
        rules_changed = current_tracer_configurator.rules_changed(rules)
    except AttributeError:
        rules_changed = True
    current_tracer_configurator.update_rules(rules)
    # if the rules did not change we are fine
    if not rules_changed:
        return ConfigUpdate()

    set_tracer_configurator(tracer_configurator=tracer_configurator._updatable_tracer_configurator)
    logger.debug('Updated deactivate instrumentations to "%s".', config_deactivate_instrumentations)
    _config = _get_config()
    if _config:
        _config.deactivate_instrumentations.update(value=config_deactivate_instrumentations)
    return ConfigUpdate()


def _handle_use_path_as_span_name(remote_config) -> ConfigUpdate:
    # when config option has default value you don't get it so need to handle the default
    config_use_path = remote_config.get(USE_PATH_AS_SPAN_NAME_CONFIG_KEY, DEFAULT_USE_PATH_AS_SPAN_NAME)
    use_path = _parse_bool(config_use_path)
    if use_path is None:
        logger.error("Invalid `use_path_as_span_name` from config `%s`", config_use_path)
        return ConfigUpdate(error_message=f"Invalid use_path_as_span_name {config_use_path}")

    span_name_settings.set_use_path_as_span_name(use_path)
    logger.debug("Updated use_path_as_span_name to %s", use_path)
    _config = _get_config()
    if _config:
        _config.use_path_as_span_name.update(value=str(use_path).lower())
    return ConfigUpdate()


def _handle_span_name_groups(remote_config) -> ConfigUpdate:
    config_span_name_groups = remote_config.get(SPAN_NAME_GROUPS_CONFIG_KEY, DEFAULT_SPAN_NAME_GROUPS)
    if not isinstance(config_span_name_groups, str):
        logger.error("Invalid `span_name_groups` from config `%s`", config_span_name_groups)
        return ConfigUpdate(error_message=f"Invalid span_name_groups {config_span_name_groups}")

    span_name_settings.set_span_name_groups(parse_span_name_groups(config_span_name_groups))
    logger.debug('Updated span_name_groups to "%s"', config_span_name_groups)
    _config = _get_config()
    if _config:
        _config.span_name_groups.update(value=config_span_name_groups)
    return ConfigUpdate()


def _report_full_state(message: opamp_pb2.ServerToAgent):
    return message.flags & opamp_pb2.ServerToAgentFlags_ReportFullState


def _initialize_config():
    """This is called by the SDK Configurator"""
    global _config
    _config = Config()
    return _config


def _get_config():
    return _config


class EDOTOpAMPCallbacks(OpAMPCallbacks):
    def on_message(self, agent: OpAMPAgent, client: OpAMPClient, message: MessageData):
        # we check config_hash because we need to track last received config and remote_config seems to be always truthy
        if not message.remote_config or not message.remote_config.config_hash:
            return

        _config = _get_config()
        error_messages = []
        try:
            for config_filename, remote_config in messages.decode_remote_config(message.remote_config):
                # we don't have standardized config values so limit to configs coming from our backend
                if config_filename == "elastic":
                    logger.debug("Config %s: %s", config_filename, remote_config)
                    config_update = _handle_logging_level(remote_config)
                    if config_update.error_message:
                        error_messages.append(config_update.error_message)

                    config_update = _handle_sampling_rate(remote_config)
                    if config_update.error_message:
                        error_messages.append(config_update.error_message)

                    config_update = _handle_deactivate_instrumentations(remote_config)
                    if config_update.error_message:
                        error_messages.append(config_update.error_message)

                    config_update = _handle_use_path_as_span_name(remote_config)
                    if config_update.error_message:
                        error_messages.append(config_update.error_message)

                    config_update = _handle_span_name_groups(remote_config)
                    if config_update.error_message:
                        error_messages.append(config_update.error_message)
        except (OpAMPRemoteConfigParseException, OpAMPRemoteConfigDecodeException) as exc:
            logger.error(str(exc))
            error_messages.append(str(exc))

        error_message = "\n".join(error_messages)
        status = opamp_pb2.RemoteConfigStatuses_FAILED if error_message else opamp_pb2.RemoteConfigStatuses_APPLIED
        updated_remote_config = client.update_remote_config_status(
            remote_config_hash=message.remote_config.config_hash, status=status, error_message=error_message
        )

        # update the cached effective config with what we updated
        if _config:
            effective_config = {"elastic": _config.to_dict()}
            client.update_effective_config(effective_config, content_type="application/json")

        # if we changed the config send an ack to the server so we don't receive the same config at every heartbeat response
        if updated_remote_config is not None:
            payload = client.build_remote_config_status_response_message(updated_remote_config)
            agent.send(payload=payload)
