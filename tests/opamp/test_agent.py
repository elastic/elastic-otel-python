from unittest import mock

from opentelemetry._opamp.agent import OpAMPAgent


def test_can_instantiate_agent():
    agent = OpAMPAgent(interval=30, client=mock.Mock(), message_handler=mock.Mock())
    assert isinstance(agent, OpAMPAgent)


def test_can_start_agent():
    agent = OpAMPAgent(interval=30, client=mock.Mock(), message_handler=mock.Mock())
    agent.start()
    agent.stop()


def test_agent_can_call_agent_stop_multiple_times():
    agent = OpAMPAgent(interval=30, client=mock.Mock(), message_handler=mock.Mock())
    agent.start()
    agent.stop()
    agent.stop()


def test_agent_can_call_agent_stop_before_start():
    agent = OpAMPAgent(interval=30, client=mock.Mock(), message_handler=mock.Mock())
    agent.stop()
