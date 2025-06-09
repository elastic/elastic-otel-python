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

import json

from opentelemetry.util.types import AnyValue as AnyValueType

from elasticotel.opamp.proto import opamp_pb2 as opamp_pb2
from elasticotel.opamp.proto.anyvalue_pb2 import KeyValue, AnyValue
from elasticotel.opamp.exceptions import OpAMPRemoteConfigParseException, OpAMPRemoteConfigDecodeException


def _decode_message(data: bytes) -> opamp_pb2.ServerToAgent:
    message = opamp_pb2.ServerToAgent()
    message.ParseFromString(data)
    return message


# TODO: copy / share full fledged _encode_value from exporter?
def _encode_value(value: AnyValueType) -> AnyValue:
    if value is None:
        return AnyValue()
    if isinstance(value, str):
        return AnyValue(string_value=value)
    if isinstance(value, bytes):
        return AnyValue(bytes_value=value)
    raise ValueError(f"Invalid type {type(value)} of value {value}")


def _encode_attributes(attributes: dict[str, AnyValueType]):
    return [KeyValue(key=key, value=_encode_value(value)) for key, value in attributes.items()]


def _build_agent_description(
    identifying_attributes: dict[str, AnyValueType], non_identifying_attributes: dict[str, AnyValueType] | None = None
) -> opamp_pb2.AgentDescription:
    identifying_attrs = _encode_attributes(identifying_attributes) if identifying_attributes else None
    non_identifying_attrs = _encode_attributes(non_identifying_attributes) if non_identifying_attributes else None
    return opamp_pb2.AgentDescription(
        identifying_attributes=identifying_attrs, non_identifying_attributes=non_identifying_attrs
    )


def _build_presentation_message(
    instance_uid: bytes, sequence_num: int, agent_description: opamp_pb2.AgentDescription, capabilities: int
) -> opamp_pb2.AgentToServer:
    command = opamp_pb2.AgentToServer(
        instance_uid=instance_uid,
        sequence_num=sequence_num,
        agent_description=agent_description,
        capabilities=capabilities,
    )
    return command


def _build_poll_message(instance_uid: bytes, sequence_num: int) -> opamp_pb2.AgentToServer:
    command = opamp_pb2.AgentToServer(instance_uid=instance_uid, sequence_num=sequence_num)
    return command


def _encode_message(data: opamp_pb2.AgentToServer) -> bytes:
    return data.SerializeToString()


def _decode_remote_config(remote_config: opamp_pb2.AgentRemoteConfig) -> tuple[str, dict[str, AnyValueType]]:
    for config_file_name, config_file in remote_config.config.config_map.items():
        if config_file.content_type == "text/json":
            try:
                body = config_file.body.decode()
                config_data = json.loads(body)
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise OpAMPRemoteConfigDecodeException(
                    f"Failed to decode {config_file} with content type {config_file.content_type}: {exc}"
                )
                continue

            yield config_file_name, config_data
        else:
            raise OpAMPRemoteConfigParseException(
                f"Cannot parse {config_file_name} with content type {config_file.content_type}"
            )
