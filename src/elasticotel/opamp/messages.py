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

from .proto import opamp_pb2 as opamp_pb2
from .proto.anyvalue_pb2 import KeyValue, AnyValue


def _decode_message(data: bytes) -> opamp_pb2.ServerToAgentCommand:
    message = opamp_pb2.ServerToAgentCommand()
    message.ParseFromString(data)
    return message


# TODO: copy / share full fledged _encode_value from exporter?
def _encode_value(value: str | bytes | None) -> AnyValue:
    if value is None:
        return AnyValue()
    if isinstance(value, str):
        return AnyValue(string_value=value)
    if isinstance(value, bytes):
        return AnyValue(bytes_value=value)
    raise ValueError(f"Invalid type {type(value)} of value {value}")


def _encode_attributes(attributes: dict[str, str, bytes]):
    return [KeyValue(key=key, value=_encode_value(value)) for key, value in attributes.items()]


def _build_agent_description(
    identifying_attributes: dict[str, str | bytes], non_identifying_attributes: dict[str, str | bytes]
) -> opamp_pb2.AgentDescription:
    identifying_attrs = _encode_attributes(identifying_attributes)
    non_identifying_attrs = _encode_attributes(non_identifying_attributes)
    return opamp_pb2.AgentDescription(
        identifying_attributes=identifying_attrs, non_identifying_attributes=non_identifying_attrs
    )


def _build_presentation_message(
    instance_uid: bytes, agent_description=opamp_pb2.AgentDescription
) -> opamp_pb2.AgentToServerCommand:
    command = opamp_pb2.AgentToServerCommand(
        instance_uid=instance_uid,
        agent_description=agent_description,
    )
    return command


def _build_poll_message(instance_uid: bytes) -> opamp_pb2.AgentToServerCommand:
    command = opamp_pb2.AgentToServerCommand(instance_uid=instance_uid)
    return command


def _encode_message(data: opamp_pb2.AgentToServerCommand) -> bytes:
    return data.serializeToString()
