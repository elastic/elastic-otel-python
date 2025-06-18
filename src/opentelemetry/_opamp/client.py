from __future__ import annotations

from logging import getLogger
from typing import Any, Callable, Generator

from uuid_utils import uuid7
from opentelemetry.util.types import AnyValue

import opentelemetry._opamp.messages as messages
from opentelemetry._opamp.transport.requests import RequestsTransport
from opentelemetry._opamp.version import __version__
from opentelemetry._opamp.proto import opamp_pb2


_logger = getLogger(__name__)

_DEFAULT_OPAMP_TIMEOUT_MS = 5_000

_OTLP_HTTP_HEADERS = {
    "Content-Type": "application/x-protobuf",
    "User-Agent": "OTel-Opamp-Python/" + __version__,
}

_HANDLED_CAPABILITIES = (
    opamp_pb2.AgentCapabilities.AgentCapabilities_ReportsStatus
    | opamp_pb2.AgentCapabilities.AgentCapabilities_ReportsHeartbeat
    | opamp_pb2.AgentCapabilities.AgentCapabilities_AcceptsRemoteConfig
    | opamp_pb2.AgentCapabilities.AgentCapabilities_ReportsRemoteConfig
)


class OpAMPClient:
    def __init__(
        self,
        *,
        endpoint: str,
        headers: dict[str, str] | None = None,
        timeout_millis: int = _DEFAULT_OPAMP_TIMEOUT_MS,
        agent_identifying_attributes: dict[str, AnyValue],
        agent_non_identifying_attributes: dict[str, AnyValue] | None = None,
    ):
        self._timeout_millis = timeout_millis
        self._transport = RequestsTransport()

        self._endpoint = endpoint
        headers = headers or {}
        self._headers = {**_OTLP_HTTP_HEADERS, **headers}

        self._agent_description = messages._build_agent_description(
            identifying_attributes=agent_identifying_attributes,
            non_identifying_attributes=agent_non_identifying_attributes,
        )
        self._sequence_num: int = 0
        self._instance_uid: bytes = uuid7().bytes

    def _build_connection_message(self):
        message = messages._build_presentation_message(
            instance_uid=self._instance_uid,
            agent_description=self._agent_description,
            sequence_num=self._sequence_num,
            capabilities=_HANDLED_CAPABILITIES,
        )
        data = messages._encode_message(message)
        return data

    def _build_heartbeat_message(self):
        message = messages._build_poll_message(instance_uid=self._instance_uid, sequence_num=self._sequence_num)
        data = messages._encode_message(message)
        return data

    def _send(self, data):
        try:
            response = self._transport.send(
                url=self._endpoint, headers=self._headers, data=data, timeout_millis=self._timeout_millis
            )
            return response
        except:
            raise
        finally:
            self._sequence_num += 1

    def _decode_response(self, response_content: bytes, callbacks: dict[str, Callable[[Any], Any]]):
        server_message = messages._decode_message(response_content)
        return server_message

    def _decode_remote_config(self, remote_config) -> Generator[tuple[str, dict[str, AnyValue]]]:
        for config_file, config in messages._decode_remote_config(remote_config):
            yield config_file, config
