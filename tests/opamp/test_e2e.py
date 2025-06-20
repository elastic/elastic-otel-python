import logging
import sys
from time import sleep
from unittest import mock

import pytest

from opentelemetry._opamp.agent import OpAMPAgent
from opentelemetry._opamp.client import OpAMPClient


@pytest.mark.skipif(sys.version_info < (3, 10), reason="vcr.py not working with urllib 2 and older Pythons")
@pytest.mark.vcr()
def test_e2e(caplog):
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
