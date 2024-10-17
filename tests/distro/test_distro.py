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

import os
from unittest import TestCase, mock

from elasticotel.distro import ElasticOpenTelemetryDistro
from elasticotel.distro.environment_variables import ELASTIC_OTEL_SYSTEM_METRICS_ENABLED
from opentelemetry.environment_variables import (
    OTEL_LOGS_EXPORTER,
    OTEL_METRICS_EXPORTER,
    OTEL_TRACES_EXPORTER,
)
from opentelemetry.sdk.environment_variables import (
    OTEL_EXPERIMENTAL_RESOURCE_DETECTORS,
    OTEL_EXPORTER_OTLP_PROTOCOL,
)


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
            "process_runtime,os,otel,telemetry_distro", os.environ.get(OTEL_EXPERIMENTAL_RESOURCE_DETECTORS)
        )

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

    def test_load_instrumentor_handles_import_error_from_instrumentor_loading(self):
        distro = ElasticOpenTelemetryDistro()
        entryPoint_mock = mock.Mock()
        entryPoint_mock.load.side_effect = ImportError

        distro.load_instrumentor(entryPoint_mock)

    def test_load_instrumentor_forwards_exceptions(self):
        distro = ElasticOpenTelemetryDistro()
        entryPoint_mock = mock.Mock()
        entryPoint_mock.load.side_effect = ValueError

        with self.assertRaises(ValueError):
            distro.load_instrumentor(entryPoint_mock)
