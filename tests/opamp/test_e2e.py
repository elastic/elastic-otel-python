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

import atexit
import logging
import sys
from threading import Event
from unittest import mock

import pytest
from opentelemetry._opamp.agent import OpAMPAgent
from opentelemetry._opamp.callbacks import OpAMPCallbacks
from opentelemetry._opamp.client import OpAMPClient
from opentelemetry._opamp.proto import opamp_pb2
from opentelemetry._opamp.transport.base import HttpTransport
from opentelemetry._opamp.transport.exceptions import OpAMPException
from opentelemetry._opamp.transport.requests import RequestsTransport

from elasticotel.distro.config import EDOTOpAMPCallbacks


# match recorded OpAMP request comparing body without variable fields
def _match_opamp_body(live_request, recorded_request):
    live_message = opamp_pb2.AgentToServer.FromString(live_request.body)
    recorded_message = opamp_pb2.AgentToServer.FromString(recorded_request.body)
    for message in (live_message, recorded_message):
        message.ClearField("instance_uid")
        message.ClearField("sequence_num")
    assert live_message == recorded_message


@pytest.fixture
def recorded_opamp_exchange(vcr):
    vcr.register_matcher("opamp_body", _match_opamp_body)
    # This cassette includes the remote config acknowledgment as well as the heartbeat and disconnect.
    with vcr.use_cassette(
        "test_default_callbacks", match_on=("method", "uri", "opamp_body"), allow_playback_repeats=True
    ):
        yield


def _is_heartbeat(message):
    return all(field.name in {"instance_uid", "sequence_num", "capabilities"} for field, _ in message.ListFields())


def _assert_opamp_exchange(callbacks, caplog):
    exchanges = []
    heartbeat_received = Event()

    class TrackingTransport(RequestsTransport):
        def send(self, *, data, **kwargs):
            response = super().send(data=data, **kwargs)
            message = opamp_pb2.AgentToServer.FromString(data)
            exchanges.append((message, response))
            if _is_heartbeat(message):
                heartbeat_received.set()
            return response

    client = OpAMPClient(
        endpoint="http://localhost:4320/v1/opamp",
        agent_identifying_attributes={"service.name": "foo", "deployment.environment.name": "foo"},
        transport=TrackingTransport(),
    )
    agent = OpAMPAgent(interval=1, callbacks=callbacks, client=client)
    try:
        agent.start()
        assert heartbeat_received.wait(timeout=10), "OpAMP client did not receive a heartbeat response"
    finally:
        # The cassette is closed by the time the process exits.
        atexit.unregister(agent.stop)
        agent.stop()

    messages = [message for message, _ in exchanges]
    assert len(messages) >= 4, messages
    registration, acknowledgment, *heartbeats, disconnect = messages
    assert registration.HasField("agent_description")
    config_hash = exchanges[0][1].remote_config.config_hash
    assert config_hash
    assert acknowledgment.remote_config_status == opamp_pb2.RemoteConfigStatus(
        last_remote_config_hash=config_hash,
        status=opamp_pb2.RemoteConfigStatuses_APPLIED,
    )
    assert all(_is_heartbeat(message) for message in heartbeats)
    assert disconnect.HasField("agent_disconnect")
    assert registration.instance_uid
    assert all(message.instance_uid == registration.instance_uid for message in messages)
    assert not [
        record
        for record in caplog.records
        if record.name == "opentelemetry._opamp.agent" and record.levelno >= logging.ERROR
    ]


@pytest.mark.skipif(sys.version_info < (3, 10), reason="vcr.py not working with urllib 2 and older Pythons")
@pytest.mark.usefixtures("recorded_opamp_exchange")
def test_connection_remote_config_status_heartbeat_disconnection(caplog):
    class TestCallbacks(OpAMPCallbacks):
        def on_message(self, agent, client, message):
            if message.remote_config is None or not message.remote_config.config_hash:
                return

            updated_remote_config = client.update_remote_config_status(
                remote_config_hash=message.remote_config.config_hash,
                status=opamp_pb2.RemoteConfigStatuses_APPLIED,
                error_message="",
            )
            if updated_remote_config is not None:
                payload = client.build_remote_config_status_response_message(updated_remote_config)
                agent.send(payload=payload)

    _assert_opamp_exchange(TestCallbacks(), caplog)


def test_with_server_not_responding():
    connection_error = OpAMPException("Connection refused")
    transport = mock.Mock(spec=HttpTransport)
    transport.send.side_effect = connection_error

    connection_failed = Event()
    connection_errors = []
    received_messages = []

    class TestCallbacks(OpAMPCallbacks):
        def on_connect_failed(self, agent, client, error):
            connection_errors.append(error)
            connection_failed.set()

        def on_message(self, agent, client, message):
            received_messages.append(message)

    opamp_client = OpAMPClient(
        endpoint="http://opamp.invalid/v1/opamp",
        agent_identifying_attributes={
            "service.name": "foo",
            "deployment.environment.name": "foo",
        },
        transport=transport,
    )
    opamp_agent = OpAMPAgent(
        interval=1,
        callbacks=TestCallbacks(),
        client=opamp_client,
    )
    try:
        opamp_agent.start()
        assert connection_failed.wait(timeout=10), "OpAMP agent did not report the connection failure"
    finally:
        atexit.unregister(opamp_agent.stop)
        opamp_agent.stop()

    assert connection_errors[0] is connection_error
    assert not received_messages


@pytest.mark.skipif(sys.version_info < (3, 10), reason="vcr.py not working with urllib 2 and older Pythons")
@pytest.mark.usefixtures("recorded_opamp_exchange")
def test_default_callbacks(caplog):
    _assert_opamp_exchange(EDOTOpAMPCallbacks(), caplog)
