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

import base64
import inspect
import subprocess
import os
import tempfile
import unittest
from pathlib import Path
from typing import Callable, Mapping, Optional

import leb128
from opentelemetry.util._importlib_metadata import version
from oteltest import private as ot

OTEL_VERSION = version("opentelemetry-api")
OTEL_INSTRUMENTATION_VERSION = version("opentelemetry-instrumentation")

ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


class ElasticIntegrationTestCase(unittest.TestCase):
    """This is an experimental reimplementation of OtelTest using unittest

    The idea is to do integration testing by creating a separate virtualenv for each TestCase inheriting
    from ElasticIntegrationTestCase, run a script, collect OTLP grpc calls and make the received data
    available in order to add assertions.

    A basic TestCase would look like:

    class MyTestCase(ElasticIntegrationTestCase):
        @classmethod
        def requirements(cls):
            requirements = super().requirements()
            return requirements + [f"my-library"]

        def script(self):
            import sqlite3

            connection = sqlite3.connect(":memory:")
            cursor = connection.cursor()
            cursor.execute("CREATE TABLE movie(title, year, score)")

        def test_one_span_generated(self):
            stdout, stderr, returncode = self.run_script(self.script, wrapper_script="opentelemetry-instrument")

            telemetry.get_telemetry()
            assert len(telemetry["traces"], 1)


    Each TestCase costs around 10 seconds for settings up the virtualenv so split tests accordingly.
    """

    @classmethod
    def requirements(cls) -> list:
        """Installs requirements in a virtualenv

        The virtualenv is reused in all TestCase tests.
        By default it installs this OTel distribution."""

        return [f"{ROOT_DIR}"]

    @classmethod
    def setUpClass(cls):
        venv_parent = tempfile.mkdtemp()
        cls.script_venv = ot.Venv(str(Path(venv_parent) / cls.__name__))
        cls.script_venv.create()

        pip_path = cls.script_venv.path_to_executable("pip")
        requirements = cls.requirements()
        if requirements:
            _ = subprocess.run(
                [pip_path, "install", *requirements],
                capture_output=True,
                text=True,
                check=True,
            )

    @classmethod
    def tearDownClass(cls):
        cls.script_venv.rm()

    def setUp(self):
        self.handler = ot.AccumulatingHandler()
        self.sink = ot.GrpcSink(self.handler)
        self.sink.start()

    def tearDown(self):
        self.sink.stop()

    def get_telemetry(self) -> dict:
        """Convert to a more user friendly format than the one provided by oteltest Telemetry"""

        telemetry = self.handler.telemetry.to_dict()

        def decode_id(pb_id: str) -> str:
            """Decode protobuf encoded ids to something more recognizable"""
            encoded_id = base64.b64decode(pb_id)
            decoded_id = leb128.u.decode(encoded_id)
            return hex(decoded_id)

        def normalize_attributes(attributes) -> dict:
            """
            oteltest attributes are in the form:
            {
              "key": "telemetry.sdk.language",
              "value": {
                "stringValue": "python"
              }
            },
            ...
            but we want
            {
              "telemetry.sdk.language": "python",
              ...
            }
            """
            return {
                a["key"]: a["value"]["stringValue"] if "stringValue" in a["value"] else a["value"]["intValue"]
                for a in attributes
            }

        def normalize_kvlist(body) -> dict:
            """
            normalizes oteltest values in the form
            {'kvlistValue': {'values': [{'key': 'key', 'value': {'stringValue': 'value'}},
                            {'key': 'dict',
                             'value': {'kvlistValue': {'values': [{'key': 'nestedkey',
                                                                   'value': {'stringValue': 'nestedvalue'}}]}}}]}}
            to plain dicts
            """
            dict_values = {}
            values = body["kvlistValue"]["values"]
            for value in values:
                key = value["key"]
                if "kvlistValue" in value["value"]:
                    dict_values[key] = normalize_kvlist(value["value"])
                elif "stringValue" in value["value"]:
                    dict_values[key] = value["value"]["stringValue"]
                elif "intValue" in value["value"]:
                    dict_values[key] = value["value"]["intValue"]
            return dict_values

        metrics = []
        for request in telemetry["metric_requests"]:
            elems = []
            for proto_elem in request["pbreq"]["resourceMetrics"]:
                scope_metrics = []
                for proto_scope_metric in proto_elem["scopeMetrics"]:
                    scope_metric = proto_scope_metric.copy()
                    for metric in scope_metric["metrics"]:
                        if "sum" in metric:
                            for data_point in metric["sum"]["dataPoints"]:
                                if "attributes" in data_point:
                                    data_point["attributes"] = normalize_attributes(data_point["attributes"])
                    scope_metrics.append(scope_metric)
                elem = {
                    "resource": {"attributes": normalize_attributes(proto_elem["resource"]["attributes"])},
                    "scopeMetrics": scope_metrics,
                }
                elems.append(elem)
            metric = {"resourceMetrics": elems}
            metrics.append(metric)

        traces = []
        for request in telemetry["trace_requests"]:
            for resource_span in request["pbreq"]["resourceSpans"]:
                resource_attributes = normalize_attributes(resource_span["resource"]["attributes"])
                for proto_scope_spans in resource_span["scopeSpans"]:
                    for proto_span in proto_scope_spans["spans"]:
                        span = proto_span.copy()
                        span["attributes"] = normalize_attributes(span["attributes"])
                        span["resource"] = resource_attributes
                        span["spanId"] = decode_id(span["spanId"])
                        span["traceId"] = decode_id(span["traceId"])
                        traces.append(span)

        logs = []
        for request in telemetry["log_requests"]:
            for resource_log in request["pbreq"]["resourceLogs"]:
                resource_attributes = normalize_attributes(resource_log["resource"]["attributes"])
                for proto_scope_logs in resource_log["scopeLogs"]:
                    for proto_log in proto_scope_logs["logRecords"]:
                        log = proto_log.copy()
                        log["attributes"] = normalize_attributes(log["attributes"])
                        log["body"] = normalize_kvlist(log["body"])
                        log["resource"] = resource_attributes
                        logs.append(log)

        return {
            "logs": logs,
            "metrics": metrics,
            "traces": traces,
        }

    def run_script(
        self,
        script_func: Callable[[], None],
        environment_variables: Optional[Mapping[str, str]] = None,
        wrapper_script: Optional[str] = None,
        on_start: Optional[Callable[[], Optional[float]]] = None,
    ):
        """Entry point for running the test scenario

        Runs the provided callable `script_func` inside the TestCase virtualenv. It is possible to optionally
        pass the environment variables to be set via `environment_variables` and a wrapper for our code in
        `wrapper_script`, e.g. opentelemetry-instrument to test auto instrumentation.
        It is possible to pass to `on_start` a callable that may be used to run another process, e.g. a client
        sending requests to the code running in `script_func`. This callable should return the number of seconds
        of timeout set for the `script_func` code to exit. None will make waiting indefinetely. for the script
        to exit.
        """
        source = inspect.getsource(script_func)
        python_script_cmd = [
            self.script_venv.path_to_executable("python"),
        ]
        if wrapper_script is not None:
            python_script_cmd.insert(0, self.script_venv.path_to_executable(wrapper_script))

        with tempfile.NamedTemporaryFile() as fp:
            # handle script_func implemented both as method or as free function
            if inspect.ismethod(script_func):
                fp.write("class Script:\n    ".encode())
                fp.write(source.strip().encode())
                fp.write(f"\nScript().{script_func.__name__}()\n".encode())
            else:
                fp.write(source.strip().encode())
                fp.write(f"\n{script_func.__name__}()\n".encode())
            fp.seek(0)

            python_script_cmd += [fp.name]

            proc = subprocess.Popen(
                python_script_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=environment_variables,
            )

            timeout = None
            if on_start is not None:
                timeout = on_start()
            try:
                stdout, stderr = proc.communicate(timeout=timeout)
                return stdout, stderr, proc.returncode
            except subprocess.TimeoutExpired as ex:
                return (
                    ex.stdout.decode() if ex.stdout else None,
                    ex.stderr.decode() if ex.stderr else None,
                    proc.returncode,
                )
