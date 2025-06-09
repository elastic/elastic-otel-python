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
import os
from urllib.parse import urlparse

from opentelemetry import trace
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
from elasticotel.opamp import messages
from elasticotel.opamp.agent import OpAMPAgent
from elasticotel.opamp.client import OpAMPClient
from elasticotel.opamp.environment_variables import ELASTIC_OTEL_OPAMP_INTERVAL, ELASTIC_OTEL_OPAMP_ENDPOINT


logger = logging.getLogger(__name__)


class ElasticOpenTelemetryConfigurator(_OTelSDKConfigurator):
    def _configure(self, **kwargs):
        super()._configure(**kwargs)

        enable_opamp = False
        endpoint = os.environ.get(ELASTIC_OTEL_OPAMP_ENDPOINT)
        if endpoint:
            parsed = urlparse(endpoint)
            enable_opamp = parsed.scheme in ("http", "https") and parsed.netloc and parsed.path
            if not enable_opamp:
                logger.warning("Found invalid value for OpAMP endpoint")

        if enable_opamp:
            # FIXME: this is not great but we don't have the calculated resource attributes around
            # won't be an issue once the code is upstreamed
            tracer_provider = trace.get_tracer_provider()
            resource_attributes = tracer_provider.resource.attributes
            service_name = resource_attributes.get("service.name")
            deployment_environment_name = resource_attributes.get(
                "deployment.environment.name", resource_attributes.get("deployment.environment")
            )
            try:
                interval = float(os.environ.get(ELASTIC_OTEL_OPAMP_INTERVAL, 30))
            except ValueError:
                logger.warning("Found invalid value for OpAMP interval, using default")
                interval = 30

            agent = OpAMPAgent(
                endpoint=endpoint,
                interval=interval,
                handler=self._opamp_handler,
                identifying_attributes={
                    "service.name": service_name,
                    "deployment.environment.name": deployment_environment_name,
                },
            )
            agent.start()
            atexit.register(agent.stop)

    def _opamp_handler(self, client: OpAMPClient, response):
        response_content = client._get_content(response)
        message = client._decode_response(response_content)
        if message.remote_config:
            for config_filename, config in messages._decode_remote_config(message.remote_config):
                print(config_filename, config)


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
