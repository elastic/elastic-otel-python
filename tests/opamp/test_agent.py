from time import sleep
from unittest import mock

from opentelemetry._opamp.agent import _Job as Job, OpAMPAgent


def test_can_instantiate_agent():
    agent = OpAMPAgent(interval=30, client=mock.Mock(), message_handler=mock.Mock())
    assert isinstance(agent, OpAMPAgent)


def test_can_start_agent():
    agent = OpAMPAgent(interval=30, client=mock.Mock(), message_handler=mock.Mock())
    agent.start()
    agent.stop()


def test_agent_start_will_send_connection_and_disconnetion_messages():
    client_mock = mock.Mock()
    mock_message = {"mock": "message"}
    client_mock._send.return_value = mock_message
    message_handler = mock.Mock()
    agent = OpAMPAgent(interval=30, client=client_mock, message_handler=message_handler)
    agent.start()
    # wait for the queue to be consumed
    sleep(0.1)
    agent.stop()

    # one send for connection message, one for disconnect agent message
    assert client_mock._send.call_count == 2
    # connection callback has been called
    assert agent._schedule is True
    # connection message response has been received
    message_handler.assert_called_once_with(mock_message)


def test_agent_can_call_agent_stop_multiple_times():
    agent = OpAMPAgent(interval=30, client=mock.Mock(), message_handler=mock.Mock())
    agent.start()
    agent.stop()
    agent.stop()


def test_agent_can_call_agent_stop_before_start():
    agent = OpAMPAgent(interval=30, client=mock.Mock(), message_handler=mock.Mock())
    agent.stop()


def test_can_instantiate_job():
    job = Job(payload="payload")

    assert isinstance(job, Job)


def test_job_should_retry():
    job = Job(payload="payload")
    assert job.attempt == 0
    assert job.max_retries == 1
    assert job.should_retry() is True

    job.attempt += 1
    assert job.should_retry() is True

    job.attempt += 1
    assert job.should_retry() is False


def test_job_delay():
    job = Job(payload="payload")

    assert job.initial_backoff == 1
    job.attempt = 1
    assert job.initial_backoff * 0.8 <= job.delay() <= job.initial_backoff * 1.2

    job.attempt = 2
    assert 2 * job.initial_backoff * 0.8 <= job.delay() <= 2 * job.initial_backoff * 1.2

    job.attempt = 3
    assert (2**2) * job.initial_backoff * 0.8 <= job.delay() <= (2**2) * job.initial_backoff * 1.2


def test_job_delay_has_jitter():
    job = Job(payload="payload")
    job.attempt = 1
    assert len(set([job.delay() for i in range(10)])) > 1
