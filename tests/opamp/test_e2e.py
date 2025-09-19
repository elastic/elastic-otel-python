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
import sys
from time import sleep
from unittest import mock

import pytest

from opentelemetry._opamp.agent import OpAMPAgent
from opentelemetry._opamp.client import OpAMPClient
from opentelemetry._opamp.proto import opamp_pb2 as opamp_pb2


@pytest.mark.skipif(sys.version_info < (3, 10), reason="vcr.py not working with urllib 2 and older Pythons")
@pytest.mark.vcr()
def test_connection_remote_config_status_heartbeat_disconnection(caplog):
    caplog.set_level(logging.DEBUG, logger="opentelemetry._opamp.agent")

    def opamp_handler(agent, client, message):
        logger = logging.getLogger("opentelemetry._opamp.agent.opamp_handler")

        logger.debug("In opamp_handler")

        # we need to update the config only if we have a config
        if not message.remote_config.config_hash:
            return

        updated_remote_config = client._update_remote_config_status(
            remote_config_hash=message.remote_config.config_hash,
            status=opamp_pb2.RemoteConfigStatuses_APPLIED,
            error_message="",
        )
        if updated_remote_config is not None:
            logger.debug("Updated Remote Config")
            payload = client._build_remote_config_status_response_message(updated_remote_config)
            agent.send(payload=payload)

    opamp_client = OpAMPClient(
        endpoint="http://localhost:4320/v1/opamp",
        agent_identifying_attributes={
            "service.name": "foo",
            "deployment.environment.name": "foo",
        },
    )
    opamp_agent = OpAMPAgent(
        interval=1,
        message_handler=opamp_handler,
        client=opamp_client,
    )
    opamp_agent.start()

    # this should be enough for the heartbeat message to be sent
    sleep(1.5)

    opamp_agent.stop()

    handler_records = [
        record[2] for record in caplog.record_tuples if record[0] == "opentelemetry._opamp.agent.opamp_handler"
    ]
    # one call is for connection, one is remote config status, one is heartbeat
    assert handler_records == [
        "In opamp_handler",
        "Updated Remote Config",
        "In opamp_handler",
        "In opamp_handler",
    ]


@pytest.mark.skipif(sys.version_info < (3, 10), reason="vcr.py not working with urllib 2 and older Pythons")
@pytest.mark.vcr()
def test_with_server_not_responding(caplog):
    caplog.set_level(logging.DEBUG, logger="opentelemetry._opamp.agent")

    opamp_handler = mock.Mock()

    opamp_client = OpAMPClient(
        endpoint="http://localhost:4321/v1/opamp",
        agent_identifying_attributes={
            "service.name": "foo",
            "deployment.environment.name": "foo",
        },
    )
    opamp_agent = OpAMPAgent(
        interval=1,
        message_handler=opamp_handler,
        client=opamp_client,
    )
    opamp_agent.start()

    opamp_agent.stop()

    assert opamp_handler.call_count == 0


@pytest.mark.skipif(sys.version_info < (3, 10), reason="vcr.py not working with urllib 2 and older Pythons")
@pytest.mark.vcr()
def test_agent_send_full_state_when_asked(caplog):
    caplog.set_level(logging.DEBUG, logger="opentelemetry._opamp.agent")

    def opamp_handler(agent, client, message):
        logger = logging.getLogger("opentelemetry._opamp.agent.opamp_handler")

        logger.debug("In opamp_handler")

        if message.flags & opamp_pb2.ServerToAgentFlags_ReportFullState:
            logger.debug("Sent Full State")
            payload = client._build_full_state_message()
            agent.send(payload=payload)

        # we need to update the config only if we have a config
        if not message.remote_config.config_hash:
            return

        updated_remote_config = client._update_remote_config_status(
            remote_config_hash=message.remote_config.config_hash,
            status=opamp_pb2.RemoteConfigStatuses_APPLIED,
            error_message="",
        )
        if updated_remote_config is not None:
            logger.debug("Updated Remote Config")
            payload = client._build_remote_config_status_response_message(updated_remote_config)
            agent.send(payload=payload)

    opamp_client = OpAMPClient(
        endpoint="http://localhost:4320/v1/opamp",
        agent_identifying_attributes={
            "service.name": "foo",
            "deployment.environment.name": "foo",
        },
    )
    opamp_agent = OpAMPAgent(
        interval=1,
        message_handler=opamp_handler,
        client=opamp_client,
    )
    opamp_agent.start()

    # this should be enough for the heartbeat message to be sent
    sleep(1)

    # when recording tests here you should restart your collector with
    # os.kill(<pid of server>, signal.SIGHUP)

    # here the server has been restarted, wait for more heartbeats
    sleep(1.5)

    opamp_agent.stop()

    handler_records = [
        record[2] for record in caplog.record_tuples if record[0] == "opentelemetry._opamp.agent.opamp_handler"
    ]
    # If you look at the agent debug messages you'll see that after the restart the server will error about
    # not being able to identify the agent while setting the ReportFullState flag and then being happy again
    # after we send it.
    assert handler_records == [
        "In opamp_handler",
        "Updated Remote Config",
        "In opamp_handler",
        "In opamp_handler",
        "In opamp_handler",
        "Sent Full State",
        "In opamp_handler",
    ]
