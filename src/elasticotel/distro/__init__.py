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

from opentelemetry._logs import set_logger_provider
from opentelemetry._events import set_event_logger_provider
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
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.sdk._configuration import (
    _OTelSDKConfigurator,
    _import_exporters,
    _get_exporter_names,
    _get_sampler,
    _import_sampler,
    _get_id_generator,
    _import_id_generator,
    _init_tracing,
    _init_metrics,
)
from opentelemetry.sdk._events import EventLoggerProvider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.environment_variables import (
    OTEL_METRICS_EXEMPLAR_FILTER,
    OTEL_EXPERIMENTAL_RESOURCE_DETECTORS,
    OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE,
    OTEL_EXPORTER_OTLP_PROTOCOL,
    _OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.util._importlib_metadata import EntryPoint

from elasticotel.distro.environment_variables import ELASTIC_OTEL_SYSTEM_METRICS_ENABLED
from elasticotel.distro.resource_detectors import get_cloud_resource_detectors


logger = logging.getLogger(__name__)


class ElasticOpenTelemetryConfigurator(_OTelSDKConfigurator):
    def _configure(self, **kwargs):
        """This is overriden to enable the log machinery (and thus log events) without
        attaching the OTel handler to the Python logging module.

        This code is a simplified version of _initialize_components plus the changes
        required to have log events enabled out of the box"""
        span_exporters, metric_exporters, log_exporters = _import_exporters(
            _get_exporter_names("traces"),
            _get_exporter_names("metrics"),
            _get_exporter_names("logs"),
        )
        sampler_name = _get_sampler()
        sampler = _import_sampler(sampler_name)
        id_generator_name = _get_id_generator()
        id_generator = _import_id_generator(id_generator_name)

        resource_attributes = {}
        # populate version if using auto-instrumentation
        auto_instrumentation_version = kwargs.get("auto_instrumentation_version")
        if auto_instrumentation_version:
            resource_attributes[ResourceAttributes.TELEMETRY_AUTO_VERSION] = auto_instrumentation_version
        # if env var OTEL_RESOURCE_ATTRIBUTES is given, it will read the service_name
        # from the env variable else defaults to "unknown_service"
        resource = Resource.create(resource_attributes)

        _init_tracing(
            exporters=span_exporters,
            id_generator=id_generator,
            sampler=sampler,
            resource=resource,
        )
        _init_metrics(metric_exporters, resource)

        # from here we change the semantics of _OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED from
        # controlling all the logging support to just the logging handler. So we can use log events without
        # exporting all the logs to OTLP
        logger_provider = LoggerProvider(resource=resource)
        set_logger_provider(logger_provider)

        for _, exporter_class in log_exporters.items():
            exporter_args = {}
            logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter_class(**exporter_args)))

        setup_logging_handler = (
            os.getenv(_OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED, "false").strip().lower() == "true"
        )
        if setup_logging_handler:
            handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
            logging.getLogger().addHandler(handler)

        # now setup the event logger
        event_logger_provider = EventLoggerProvider(logger_provider=logger_provider)
        set_event_logger_provider(event_logger_provider)


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

        base_resource_detectors = ["process_runtime", "os", "otel", "telemetry_distro"]
        detectors = base_resource_detectors + get_cloud_resource_detectors()
        os.environ.setdefault(OTEL_EXPERIMENTAL_RESOURCE_DETECTORS, ",".join(detectors))
