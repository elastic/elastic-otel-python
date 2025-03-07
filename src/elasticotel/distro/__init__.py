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

import logging
import os

from opentelemetry.environment_variables import (
    OTEL_LOGS_EXPORTER,
    OTEL_METRICS_EXPORTER,
    OTEL_TRACES_EXPORTER,
)
from opentelemetry.instrumentation.distro import BaseDistro
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.system_metrics import (
    _DEFAULT_CONFIG as SYSTEM_METRICS_DEFAULT_CONFIG,
    SystemMetricsInstrumentor,
)
from opentelemetry.sdk._configuration import _OTelSDKConfigurator
from opentelemetry.sdk.environment_variables import (
    OTEL_METRICS_EXEMPLAR_FILTER,
    OTEL_EXPERIMENTAL_RESOURCE_DETECTORS,
    OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE,
    OTEL_EXPORTER_OTLP_PROTOCOL,
)
from opentelemetry.util._importlib_metadata import EntryPoint

from elasticotel.distro.environment_variables import ELASTIC_OTEL_SYSTEM_METRICS_ENABLED
from elasticotel.distro.resource_detectors import get_cloud_resource_detectors


logger = logging.getLogger(__name__)


class ElasticOpenTelemetryConfigurator(_OTelSDKConfigurator):
    pass


class ElasticOpenTelemetryDistro(BaseDistro):
    def load_instrumentor(self, entry_point: EntryPoint, **kwargs):
        # When running in the k8s operator loading of an instrumentor may fail because the environment
        # in which python extensions are built does not match the one from the running container but
        # ImportErrors raised here are handled by the autoinstrumentation code
        instrumentor_class: BaseInstrumentor = entry_point.load()

        instrumentor_kwargs = {}
        if instrumentor_class == SystemMetricsInstrumentor:
            system_metrics_configuration = os.environ.get(ELASTIC_OTEL_SYSTEM_METRICS_ENABLED, "false")
            system_metrics_enabled = system_metrics_configuration.lower() == "true"
            if not system_metrics_enabled:
                instrumentor_kwargs["config"] = {
                    k: v for k, v in SYSTEM_METRICS_DEFAULT_CONFIG.items() if k.startswith("process.runtime")
                }
        instrumentor_class(**instrumentor_kwargs).instrument(**kwargs)

    def _configure(self, **kwargs):
        os.environ.setdefault(OTEL_TRACES_EXPORTER, "otlp")
        os.environ.setdefault(OTEL_METRICS_EXPORTER, "otlp")
        os.environ.setdefault(OTEL_LOGS_EXPORTER, "otlp")
        os.environ.setdefault(OTEL_EXPORTER_OTLP_PROTOCOL, "grpc")
        # disable exemplars by default for now
        os.environ.setdefault(OTEL_METRICS_EXEMPLAR_FILTER, "always_off")
        # preference to use DELTA temporality as we can handle only this kind of Histograms
        os.environ.setdefault(OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE, "DELTA")

        base_resource_detectors = ["process_runtime", "os", "otel", "telemetry_distro", "service_instance"]
        detectors = base_resource_detectors + get_cloud_resource_detectors()
        os.environ.setdefault(OTEL_EXPERIMENTAL_RESOURCE_DETECTORS, ",".join(detectors))
