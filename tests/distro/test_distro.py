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

import json
import logging
import os
from unittest import TestCase, mock

from elasticotel.distro import ElasticOpenTelemetryConfigurator, ElasticOpenTelemetryDistro, logger as distro_logger
from elasticotel.distro.config import opamp_handler, logger as config_logger
from elasticotel.distro.environment_variables import ELASTIC_OTEL_OPAMP_ENDPOINT, ELASTIC_OTEL_SYSTEM_METRICS_ENABLED
from opentelemetry.environment_variables import (
    OTEL_LOGS_EXPORTER,
    OTEL_METRICS_EXPORTER,
    OTEL_TRACES_EXPORTER,
)
from opentelemetry.sdk.environment_variables import (
    OTEL_METRICS_EXEMPLAR_FILTER,
    OTEL_EXPERIMENTAL_RESOURCE_DETECTORS,
    OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE,
    OTEL_EXPORTER_OTLP_PROTOCOL,
    OTEL_TRACES_SAMPLER,
    OTEL_TRACES_SAMPLER_ARG,
)
from opentelemetry.sdk.trace import sampling
from opentelemetry._opamp.proto import opamp_pb2 as opamp_pb2


class TestDistribution(TestCase):
    @mock.patch.dict("os.environ", {}, clear=True)
    def test_default_configuration(self):
        distro = ElasticOpenTelemetryDistro()
        distro.configure()
        self.assertEqual("otlp", os.environ.get(OTEL_TRACES_EXPORTER))
        self.assertEqual("otlp", os.environ.get(OTEL_METRICS_EXPORTER))
        self.assertEqual("otlp", os.environ.get(OTEL_LOGS_EXPORTER))
        self.assertEqual("grpc", os.environ.get(OTEL_EXPORTER_OTLP_PROTOCOL))
        self.assertEqual(
            "process_runtime,os,otel,telemetry_distro,service_instance,_gcp,aws_ec2,aws_ecs,aws_elastic_beanstalk,azure_app_service,azure_vm",
            os.environ.get(OTEL_EXPERIMENTAL_RESOURCE_DETECTORS),
        )
        self.assertEqual("always_off", os.environ.get(OTEL_METRICS_EXEMPLAR_FILTER))
        self.assertEqual("DELTA", os.environ.get(OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE))
        self.assertEqual("parentbased_traceidratio", os.environ.get(OTEL_TRACES_SAMPLER))
        self.assertEqual("1.0", os.environ.get(OTEL_TRACES_SAMPLER_ARG))

    @mock.patch.dict("os.environ", {}, clear=True)
    def test_sampler_configuration(self):
        distro = ElasticOpenTelemetryDistro()
        distro._configure()
        parent_sampler = sampling._get_from_env_or_default()

        assert isinstance(parent_sampler, sampling.ParentBasedTraceIdRatio)

        sampler = parent_sampler._root

        assert isinstance(sampler, sampling.TraceIdRatioBased)
        assert sampler.rate == 1.0

    @mock.patch.dict("os.environ", {}, clear=True)
    def test_load_instrumentor_call_with_default_kwargs_for_SystemMetricsInstrumentor(self):
        distro = ElasticOpenTelemetryDistro()
        instrumentor_mock = mock.Mock()
        instrumentor_mock.__eq__ = lambda self, other: True
        entryPoint_mock = mock.Mock()
        entryPoint_mock.load.return_value = instrumentor_mock

        distro.load_instrumentor(entryPoint_mock)

        instrumentor_mock.assert_called_once_with(
            config={
                "process.runtime.memory": ["rss", "vms"],
                "process.runtime.cpu.time": ["user", "system"],
                "process.runtime.gc_count": None,
                "process.runtime.thread_count": None,
                "process.runtime.cpu.utilization": None,
                "process.runtime.context_switches": ["involuntary", "voluntary"],
            }
        )

    @mock.patch.dict("os.environ", {ELASTIC_OTEL_SYSTEM_METRICS_ENABLED: "true"}, clear=True)
    def test_load_instrumentor_call_with_system_metrics_configuration_enabled(self):
        distro = ElasticOpenTelemetryDistro()
        instrumentor_mock = mock.Mock()
        instrumentor_mock.__eq__ = lambda self, other: True
        entryPoint_mock = mock.Mock()
        entryPoint_mock.load.return_value = instrumentor_mock

        distro.load_instrumentor(entryPoint_mock)

        instrumentor_mock.assert_called_once_with()

    def test_load_instrumentor_default_kwargs_for_instrumentors(self):
        distro = ElasticOpenTelemetryDistro()
        instrumentor_mock = mock.Mock()
        entryPoint_mock = mock.Mock()
        entryPoint_mock.load.return_value = instrumentor_mock

        distro.load_instrumentor(entryPoint_mock)

        instrumentor_mock.assert_called_once_with()

    @mock.patch.dict(
        "os.environ",
        {
            ELASTIC_OTEL_OPAMP_ENDPOINT: "http://localhost:4320/v1/opamp",
            "OTEL_RESOURCE_ATTRIBUTES": "service.name=service,deployment.environment.name=dev",
        },
        clear=True,
    )
    @mock.patch("elasticotel.distro.OpAMPAgent")
    @mock.patch("elasticotel.distro.OpAMPClient")
    def test_configurator_sets_up_opamp_with_http_endpoint(self, client_mock, agent_mock):
        client_mock.return_value = client_mock
        agent_mock.return_value = agent_mock

        ElasticOpenTelemetryConfigurator()._configure()

        client_mock.assert_called_once_with(
            endpoint="http://localhost:4320/v1/opamp",
            agent_identifying_attributes={"service.name": "service", "deployment.environment.name": "dev"},
        )
        agent_mock.assert_called_once_with(interval=30, message_handler=opamp_handler, client=client_mock)
        agent_mock.start.assert_called_once_with()

    @mock.patch.dict(
        "os.environ",
        {
            ELASTIC_OTEL_OPAMP_ENDPOINT: "https://localhost:4320/v1/opamp",
            "OTEL_RESOURCE_ATTRIBUTES": "service.name=service,deployment.environment.name=dev",
        },
        clear=True,
    )
    @mock.patch("elasticotel.distro.OpAMPAgent")
    @mock.patch("elasticotel.distro.OpAMPClient")
    def test_configurator_sets_up_opamp_with_https_endpoint(self, client_mock, agent_mock):
        client_mock.return_value = client_mock
        agent_mock.return_value = agent_mock

        ElasticOpenTelemetryConfigurator()._configure()

        client_mock.assert_called_once_with(
            endpoint="https://localhost:4320/v1/opamp",
            agent_identifying_attributes={"service.name": "service", "deployment.environment.name": "dev"},
        )
        agent_mock.assert_called_once_with(interval=30, message_handler=opamp_handler, client=client_mock)
        agent_mock.start.assert_called_once_with()

    @mock.patch.dict(
        "os.environ",
        {
            ELASTIC_OTEL_OPAMP_ENDPOINT: "https://localhost:4320",
            "OTEL_RESOURCE_ATTRIBUTES": "service.name=service,deployment.environment.name=dev",
        },
        clear=True,
    )
    @mock.patch("elasticotel.distro.OpAMPAgent")
    @mock.patch("elasticotel.distro.OpAMPClient")
    def test_configurator_adds_path_to_opamp_endpoint_if_missing(self, client_mock, agent_mock):
        client_mock.return_value = client_mock
        agent_mock.return_value = agent_mock

        ElasticOpenTelemetryConfigurator()._configure()

        client_mock.assert_called_once_with(
            endpoint="https://localhost:4320/v1/opamp",
            agent_identifying_attributes={"service.name": "service", "deployment.environment.name": "dev"},
        )
        agent_mock.assert_called_once_with(interval=30, message_handler=opamp_handler, client=client_mock)
        agent_mock.start.assert_called_once_with()

    @mock.patch.dict(
        "os.environ",
        {
            ELASTIC_OTEL_OPAMP_ENDPOINT: "https://localhost:4320/v1/opamp",
            "OTEL_RESOURCE_ATTRIBUTES": "service.name=service",
        },
        clear=True,
    )
    @mock.patch("elasticotel.distro.OpAMPAgent")
    @mock.patch("elasticotel.distro.OpAMPClient")
    def test_configurator_sets_up_opamp_without_deployment_environment_name(self, client_mock, agent_mock):
        client_mock.return_value = client_mock
        agent_mock.return_value = agent_mock

        ElasticOpenTelemetryConfigurator()._configure()

        client_mock.assert_called_once_with(
            endpoint="https://localhost:4320/v1/opamp",
            agent_identifying_attributes={"service.name": "service"},
        )
        agent_mock.assert_called_once_with(interval=30, message_handler=opamp_handler, client=client_mock)
        agent_mock.start.assert_called_once_with()

    @mock.patch.dict("os.environ", {ELASTIC_OTEL_OPAMP_ENDPOINT: "localhost:4320/v1/opamp"}, clear=True)
    @mock.patch("elasticotel.distro.OpAMPAgent")
    @mock.patch("elasticotel.distro.OpAMPClient")
    def test_configurator_ignores_invalid_url(self, client_mock, agent_mock):
        with self.assertLogs(distro_logger, logging.WARNING):
            ElasticOpenTelemetryConfigurator()._configure()

        client_mock.assert_not_called()
        agent_mock.assert_not_called()

    @mock.patch.dict("os.environ", {ELASTIC_OTEL_OPAMP_ENDPOINT: "ws://localhost:4320/v1/opamp"}, clear=True)
    @mock.patch("elasticotel.distro.OpAMPAgent")
    @mock.patch("elasticotel.distro.OpAMPClient")
    def test_configurator_ignores_ws_url(self, client_mock, agent_mock):
        with self.assertLogs(distro_logger, logging.WARNING):
            ElasticOpenTelemetryConfigurator()._configure()
        client_mock.assert_not_called()
        agent_mock.assert_not_called()

    @mock.patch.dict("os.environ", {}, clear=True)
    @mock.patch("elasticotel.distro.OpAMPAgent")
    @mock.patch("elasticotel.distro.OpAMPClient")
    def test_configurator_ignores_opamp_without_endpoint(self, client_mock, agent_mock):
        ElasticOpenTelemetryConfigurator()._configure()
        client_mock.assert_not_called()
        agent_mock.assert_not_called()


class TestOpAMPHandler(TestCase):
    @mock.patch.object(logging, "getLogger")
    def test_does_nothing_without_remote_config(self, get_logger_mock):
        message = opamp_pb2.ServerToAgent()
        agent = mock.Mock()
        client = mock.Mock()
        opamp_handler(agent, client, message)

        get_logger_mock.assert_not_called()

    @mock.patch.object(logging, "getLogger")
    def test_ignores_non_elastic_filename(self, get_logger_mock):
        agent = mock.Mock()
        client = mock.Mock()
        config = opamp_pb2.AgentConfigMap()
        config.config_map["non-elastic"].body = json.dumps({"logging_level": "trace"}).encode()
        config.config_map["non-elastic"].content_type = "application/json"
        remote_config = opamp_pb2.AgentRemoteConfig(config=config, config_hash=b"1234")
        message = opamp_pb2.ServerToAgent(remote_config=remote_config)
        opamp_handler(agent, client, message)

        get_logger_mock.assert_not_called()

        client._update_remote_config_status.assert_called_once_with(
            remote_config_hash=b"1234", status=opamp_pb2.RemoteConfigStatuses_APPLIED, error_message=""
        )
        client._build_remote_config_status_response_message.assert_called_once_with(
            client._update_remote_config_status()
        )
        agent.send.assert_called_once_with(payload=mock.ANY)

    @mock.patch.object(logging, "getLogger")
    def test_sets_matching_logging_level(self, get_logger_mock):
        agent = mock.Mock()
        client = mock.Mock()
        config = opamp_pb2.AgentConfigMap()
        config.config_map["elastic"].body = json.dumps({"logging_level": "trace"}).encode()
        config.config_map["elastic"].content_type = "application/json"
        remote_config = opamp_pb2.AgentRemoteConfig(config=config, config_hash=b"1234")
        message = opamp_pb2.ServerToAgent(remote_config=remote_config)
        opamp_handler(agent, client, message)

        get_logger_mock.assert_has_calls(
            [mock.call("opentelemetry"), mock.call().setLevel(5), mock.call("elasticotel"), mock.call().setLevel(5)]
        )

        client._update_remote_config_status.assert_called_once_with(
            remote_config_hash=b"1234", status=opamp_pb2.RemoteConfigStatuses_APPLIED, error_message=""
        )
        client._build_remote_config_status_response_message.assert_called_once_with(
            client._update_remote_config_status()
        )
        agent.send.assert_called_once_with(payload=mock.ANY)

    @mock.patch.object(logging, "getLogger")
    def test_sets_logging_to_default_info_without_logging_level_entry_in_config(self, get_logger_mock):
        agent = mock.Mock()
        client = mock.Mock()
        config = opamp_pb2.AgentConfigMap()
        config.config_map["elastic"].body = json.dumps({}).encode()
        config.config_map["elastic"].content_type = "application/json"
        remote_config = opamp_pb2.AgentRemoteConfig(config=config, config_hash=b"1234")
        message = opamp_pb2.ServerToAgent(remote_config=remote_config)
        opamp_handler(agent, client, message)

        get_logger_mock.assert_has_calls(
            [
                mock.call("opentelemetry"),
                mock.call().setLevel(logging.INFO),
                mock.call("elasticotel"),
                mock.call().setLevel(logging.INFO),
            ]
        )

        client._update_remote_config_status.assert_called_once_with(
            remote_config_hash=b"1234", status=opamp_pb2.RemoteConfigStatuses_APPLIED, error_message=""
        )
        client._build_remote_config_status_response_message.assert_called_once_with(
            client._update_remote_config_status()
        )
        agent.send.assert_called_once_with(payload=mock.ANY)

    @mock.patch.object(logging, "getLogger")
    def test_warns_if_logging_level_does_not_match_our_map(self, get_logger_mock):
        agent = mock.Mock()
        client = mock.Mock()
        config = opamp_pb2.AgentConfigMap()
        config.config_map["elastic"].body = json.dumps({"logging_level": "unexpected"}).encode()
        config.config_map["elastic"].content_type = "application/json"
        remote_config = opamp_pb2.AgentRemoteConfig(config=config, config_hash=b"1234")
        message = opamp_pb2.ServerToAgent(remote_config=remote_config)

        with self.assertLogs(config_logger, logging.WARNING):
            opamp_handler(agent, client, message)

        client._build_remote_config_status_response_message.assert_called_once_with(
            client._update_remote_config_status()
        )
        agent.send.assert_called_once_with(payload=mock.ANY)
