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

import os.path

import pytest

from .utils import ElasticIntegrationTestCase, OTEL_INSTRUMENTATION_VERSION, ROOT_DIR


@pytest.mark.integration
class IntegrationTestCase(ElasticIntegrationTestCase):
    @classmethod
    def requirements(cls):
        requirements = super().requirements()
        return requirements + [f"opentelemetry-instrumentation-sqlite3=={OTEL_INSTRUMENTATION_VERSION}"]

    def script(self):
        import sqlite3

        connection = sqlite3.connect(":memory:")
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE movie(title, year, score)")

    def test_traces_default_resource_attributes(self):
        stdout, stderr, returncode = self.run_script(self.script, wrapper_script="opentelemetry-instrument")

        telemetry = self.get_telemetry()
        (span,) = telemetry["traces"]
        resource = span["resource"]
        self.assertEqual(resource["telemetry.distro.name"], "elastic")
        self.assertTrue(resource["telemetry.distro.version"])
        self.assertTrue(resource["process.runtime.description"])
        self.assertTrue(resource["process.runtime.name"])
        self.assertTrue(resource["process.runtime.version"])
        self.assertTrue(resource["os.type"])
        self.assertTrue(resource["os.version"])

    def test_traces_sets_resource_attributes_from_env(self):
        env = {"OTEL_RESOURCE_ATTRIBUTES": "service.name=my-service"}
        stdout, stderr, returncode = self.run_script(
            self.script, environment_variables=env, wrapper_script="opentelemetry-instrument"
        )

        telemetry = self.get_telemetry()
        (span,) = telemetry["traces"]
        resource = span["resource"]
        self.assertEqual(resource["service.name"], "my-service")

    def test_metrics_default_does_not_contain_system_metrics(self):
        stdout, stderr, returncode = self.run_script(self.script, wrapper_script="opentelemetry-instrument")

        telemetry = self.get_telemetry()
        (metrics,) = telemetry["metrics"]
        (metrics_item,) = metrics["resourceMetrics"]
        scope_metrics_item = metrics_item["scopeMetrics"][0]["metrics"]
        process_runtime_metrics_names = [m["name"] for m in scope_metrics_item]
        self.assertEqual(
            process_runtime_metrics_names,
            [
                "process.runtime.cpython.memory",
                "process.runtime.cpython.cpu_time",
                "process.runtime.cpython.gc_count",
                "process.runtime.cpython.thread_count",
                "process.runtime.cpython.cpu.utilization",
                "process.runtime.cpython.context_switches",
            ],
        )

    def test_metrics_with_system_metrics(self):
        env = {"ELASTIC_OTEL_SYSTEM_METRICS_ENABLED": "true"}
        stdout, stderr, returncode = self.run_script(
            self.script, environment_variables=env, wrapper_script="opentelemetry-instrument"
        )

        telemetry = self.get_telemetry()
        (metrics,) = telemetry["metrics"]
        (metrics_item,) = metrics["resourceMetrics"]
        scope_metrics_item = metrics_item["scopeMetrics"][0]["metrics"]
        process_runtime_metrics_names = [m["name"] for m in scope_metrics_item]
        self.maxDiff = None
        self.assertEqual(
            process_runtime_metrics_names,
            [
                "system.cpu.time",
                "system.cpu.utilization",
                "system.memory.usage",
                "system.memory.utilization",
                "system.swap.usage",
                "system.swap.utilization",
                "system.disk.io",
                "system.disk.operations",
                "system.disk.time",
                "system.network.dropped_packets",
                "system.network.packets",
                "system.network.errors",
                "system.network.io",
                "system.network.connections",
                "system.thread_count",
                "process.cpu.time",
                "process.cpu.utilization",
                "process.context_switches",
                "process.memory.usage",
                "process.memory.virtual",
                "process.open_file_descriptor.count",
                "process.thread.count",
                "process.runtime.cpython.memory",
                "process.runtime.cpython.cpu_time",
                "process.runtime.cpython.gc_count",
                "process.runtime.cpython.thread_count",
                "process.runtime.cpython.cpu.utilization",
                "process.runtime.cpython.context_switches",
            ],
        )

    def test_log_events_are_sent(self):
        def send_event():
            from opentelemetry._events import Event
            from opentelemetry._events import get_event_logger

            event = Event(name="test.event", attributes={}, body={"key": "value", "dict": {"nestedkey": "nestedvalue"}})
            event_logger = get_event_logger(__name__)
            event_logger.emit(event)

        stdout, stderr, returncode = self.run_script(send_event, wrapper_script="opentelemetry-instrument")

        telemetry = self.get_telemetry()
        (log,) = telemetry["logs"]
        self.assertEqual(log["attributes"]["event.name"], "test.event")
        self.assertEqual(log["body"], {"key": "value", "dict": {"nestedkey": "nestedvalue"}})


@pytest.mark.integration
class OperatorTestCase(ElasticIntegrationTestCase):
    @staticmethod
    def _read_operator_requirements():
        requirements = []
        with open(os.path.join(ROOT_DIR, "operator", "requirements.txt")) as reqf:
            for line in reqf:
                req = line.strip()
                if req:
                    requirements.append(req)
        return requirements

    @classmethod
    def requirements(cls):
        requirements = super().requirements()
        return requirements + cls._read_operator_requirements()

    def script(self):
        import sqlite3

        connection = sqlite3.connect(":memory:")
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE movie(title, year, score)")

    def test_auto_instrumentation_works(self):
        stdout, stderr, returncode = self.run_script(self.script, wrapper_script="opentelemetry-instrument")

        telemetry = self.get_telemetry()
        (span,) = telemetry["traces"]
        self.assertTrue(span)

        self.assertEqual(returncode, 0)
