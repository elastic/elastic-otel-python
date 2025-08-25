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
from urllib.parse import urlparse, urlunparse

from opentelemetry.environment_variables import (
    OTEL_LOGS_EXPORTER,
    OTEL_METRICS_EXPORTER,
    OTEL_TRACES_EXPORTER,
)
from opentelemetry.exporter.otlp.proto.grpc import _USER_AGENT_HEADER_VALUE
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter as GRPCOTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter as GRPCOTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter as GRPCOTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http import _OTLP_HTTP_HEADERS
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter as HTTPOTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter as HTTPOTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter as HTTPOTLPSpanExporter
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
    OTEL_TRACES_SAMPLER,
    OTEL_TRACES_SAMPLER_ARG,
)
from opentelemetry.sdk.resources import OTELResourceDetector
from opentelemetry.util._importlib_metadata import EntryPoint
from opentelemetry._opamp.agent import OpAMPAgent
from opentelemetry._opamp.client import OpAMPClient
from opentelemetry._opamp.proto import opamp_pb2 as opamp_pb2

from elasticotel.distro import version
from elasticotel.distro.environment_variables import ELASTIC_OTEL_OPAMP_ENDPOINT, ELASTIC_OTEL_SYSTEM_METRICS_ENABLED
from elasticotel.distro.resource_detectors import get_cloud_resource_detectors
from elasticotel.distro.config import opamp_handler, DEFAULT_SAMPLING_RATE


logger = logging.getLogger(__name__)

EDOT_GRPC_USER_AGENT_HEADER_VALUE = "elastic-otlp-grpc-python/" + version.__version__
EDOT_HTTP_USER_AGENT_HEADER_VALUE = "elastic-otlp-http-python/" + version.__version__


class ElasticOpenTelemetryConfigurator(_OTelSDKConfigurator):
    def _configure(self, **kwargs):
        # override GRPC and HTTP user agent headers, GRPC works since OTel SDK 1.35.0, HTTP currently requires an hack
        otlp_grpc_exporter_options = {
            "channel_options": (
                ("grpc.primary_user_agent", f"{EDOT_GRPC_USER_AGENT_HEADER_VALUE} {_USER_AGENT_HEADER_VALUE}"),
            )
        }
        otlp_http_exporter_options = {
            "headers": {
                **_OTLP_HTTP_HEADERS,
                "User-Agent": f"{EDOT_HTTP_USER_AGENT_HEADER_VALUE} {_OTLP_HTTP_HEADERS['User-Agent']}",
            }
        }
        kwargs["exporter_args_map"] = {
            GRPCOTLPLogExporter: otlp_grpc_exporter_options,
            GRPCOTLPMetricExporter: otlp_grpc_exporter_options,
            GRPCOTLPSpanExporter: otlp_grpc_exporter_options,
            HTTPOTLPLogExporter: otlp_http_exporter_options,
            HTTPOTLPMetricExporter: otlp_http_exporter_options,
            HTTPOTLPSpanExporter: otlp_http_exporter_options,
        }
        # TODO: Remove the following line after rebasing on top of upstream 1.37.0
        _OTLP_HTTP_HEADERS["User-Agent"] = otlp_http_exporter_options["headers"]["User-Agent"]

        super()._configure(**kwargs)

        enable_opamp = False
        endpoint = os.environ.get(ELASTIC_OTEL_OPAMP_ENDPOINT)
        if endpoint:
            parsed = urlparse(endpoint)
            enable_opamp = parsed.scheme in ("http", "https") and parsed.netloc
            if enable_opamp:
                if not parsed.path:
                    parsed = parsed._replace(path="/v1/opamp")

                endpoint_url = urlunparse(parsed)
                # this is not great but we don't have the calculated resource attributes around
                resource = OTELResourceDetector().detect()
                agent_identifying_attributes = {
                    "service.name": resource.attributes.get("service.name"),
                }
                if deployment_environment_name := resource.attributes.get(
                    "deployment.environment.name", resource.attributes.get("deployment.environment")
                ):
                    agent_identifying_attributes["deployment.environment.name"] = deployment_environment_name

                opamp_client = OpAMPClient(
                    endpoint=endpoint_url,
                    agent_identifying_attributes=agent_identifying_attributes,
                )
                opamp_agent = OpAMPAgent(
                    interval=30,
                    message_handler=opamp_handler,
                    client=opamp_client,
                )
                opamp_agent.start()
            else:
                logger.warning("Found invalid value for OpAMP endpoint")


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
        instrumentor_class(**instrumentor_kwargs).instrument(**kwargs)  # type: ignore[reportCallIssue]

    def _configure(self, **kwargs):
        os.environ.setdefault(OTEL_TRACES_EXPORTER, "otlp")
        os.environ.setdefault(OTEL_METRICS_EXPORTER, "otlp")
        os.environ.setdefault(OTEL_LOGS_EXPORTER, "otlp")
        os.environ.setdefault(OTEL_EXPORTER_OTLP_PROTOCOL, "grpc")
        # disable exemplars by default for now
        os.environ.setdefault(OTEL_METRICS_EXEMPLAR_FILTER, "always_off")
        # preference to use DELTA temporality as we can handle only this kind of Histograms
        os.environ.setdefault(OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE, "DELTA")
        os.environ.setdefault(OTEL_TRACES_SAMPLER, "parentbased_traceidratio")
        os.environ.setdefault(OTEL_TRACES_SAMPLER_ARG, str(DEFAULT_SAMPLING_RATE))

        base_resource_detectors = [
            "process_runtime",
            "os",
            "otel",
            "telemetry_distro",
            "service_instance",
            "containerid",
        ]
        detectors = base_resource_detectors + get_cloud_resource_detectors()
        os.environ.setdefault(OTEL_EXPERIMENTAL_RESOURCE_DETECTORS, ",".join(detectors))
