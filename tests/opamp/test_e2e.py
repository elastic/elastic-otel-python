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


@pytest.mark.skipif(sys.version_info < (3, 10), reason="vcr.py not working with urllib 2 and older Pythons")
@pytest.mark.vcr()
def test_connection_heartbeat_disconnection(caplog):
    caplog.set_level(logging.DEBUG, logger="opentelemetry._opamp.agent")

    opamp_handler = mock.Mock()

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

    # one call is for connection and the other one is heartbeat
    assert opamp_handler.call_count == 2


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
