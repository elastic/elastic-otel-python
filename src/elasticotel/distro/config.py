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

import logging

from opentelemetry._opamp import messages
from opentelemetry._opamp.agent import OpAMPAgent
from opentelemetry._opamp.client import OpAMPClient
from opentelemetry._opamp.proto import opamp_pb2 as opamp_pb2


logger = logging.getLogger(__name__)

_LOG_LEVELS_MAP = {
    "trace": 5,
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warn": logging.WARNING,
    "error": logging.ERROR,
    "fatal": logging.CRITICAL,
    "off": 1000,
}


def opamp_handler(agent: OpAMPAgent, client: OpAMPClient, message: opamp_pb2.ServerToAgent):
    # we check config_hash because we need to track last received config and remote_config seems to be always truthy
    if not message.remote_config or not message.remote_config.config_hash:
        return

    error_message = ""
    for config_filename, config in messages._decode_remote_config(message.remote_config):
        # we don't have standardized config values so limit to configs coming from our backend
        if config_filename == "elastic":
            logger.debug("Config %s: %s", config_filename, config)
            # when config option has default value you don't get it so need to handle the default
            config_logging_level = config.get("logging_level")
            if config_logging_level is not None:
                logging_level = _LOG_LEVELS_MAP.get(config_logging_level)  # type: ignore[reportArgumentType]
            else:
                logging_level = logging.INFO

            if logging_level is None:
                logger.warning("Logging level not handled: %s", config_logging_level)
                error_message = f"Logging level not handled: {config_logging_level}"
            else:
                # update upstream and distro logging levels
                logging.getLogger("opentelemetry").setLevel(logging_level)
                logging.getLogger("elasticotel").setLevel(logging_level)

    status = opamp_pb2.RemoteConfigStatuses_FAILED if error_message else opamp_pb2.RemoteConfigStatuses_APPLIED
    updated_remote_config = client._update_remote_config_status(
        remote_config_hash=message.remote_config.config_hash, status=status, error_message=error_message
    )
    # if we changed the config send an ack to the server so we don't receive the same config at every heartbeat response
    if updated_remote_config is not None:
        payload = client._build_remote_config_status_response_message(updated_remote_config)
        agent.send(payload=payload)
