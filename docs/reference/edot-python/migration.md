---
navigation_title: Migration
description: Migrate from the Elastic APM Python agent to the Elastic Distribution of OpenTelemetry Python (EDOT Python).
applies_to:
  stack:
  serverless:
    observability:
  product:
    edot_python: ga
products:
  - id: cloud-serverless
  - id: observability
  - id: edot-sdk
  - id: apm-agent
---

# Migrate to EDOT Python from the Elastic APM Python agent

Learn the differences between the [Elastic APM Python agent](apm-agent-python://reference/index.md) and the {{edot}} Python (EDOT Python).

Follow the steps to migrate your instrumentation and settings. For step-by-step instructions on setting up EDOT Python refer to [Setup](/reference/edot-python/setup/index.md).

## Migration steps

Follow these steps to migrate:

1. Remove any configuration and setup code needed by Elastic APM Python Agent from your application source code.
2. Migrate any usage of Elastic APM Python Agent API to manual instrumentation with OpenTelemetry API in the application source code.
3. Follow the [setup documentation](setup/index.md) on to install and configure EDOT Python.

## Configuration mapping

The following are Elastic APM Python agent settings that you can migrate to EDOT Python.

### `api_key`

The Elastic [`api_key`](apm-agent-python://reference/configuration.md#config-api-key) option corresponds to the OpenTelemetry [OTEL_EXPORTER_OTLP_HEADERS](https://opentelemetry.io/docs/concepts/sdk-configuration/otlp-exporter-configuration/#otel_exporter_otlp_headers) environment variable.

For example: `OTEL_EXPORTER_OTLP_HEADERS="Authorization=ApiKey an_api_key"`.

### `capture_headers`

The Elastic [`capture_headers`](apm-agent-python://reference/configuration.md#config-capture-headers) option corresponds to the OpenTelemetry Python `OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST` and `OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_RESPONSE` environment variables, see [OpenTelemetry documentation](https://github.com/open-telemetry/opentelemetry.io/edit/main/content/en/docs/zero-code/python/example.md/#capture-http-request-and-response-headers).

For sanitization of these captured headers you can use the `OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SANITIZE_FIELDS` environment variable.
For example `OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SANITIZE_FIELDS=".*session.*,set-cookie"` will replace the value of headers such as `session-id` and `set-cookie` with `[REDACTED]` in the span.

### `cloud_provider`

The Elastic [`cloud_provider`](apm-agent-python://reference/configuration.md#config-cloud-provider) option corresponds to listing individual resource detectors using the OpenTelemetry Python `OTEL_EXPERIMENTAL_RESOURCE_DETECTORS` environment variable, see [default value of OTEL_EXPERIMENTAL_RESOURCE_DETECTORS](/reference/edot-python/setup/configuration.md##differences-from-opentelemetry-python). The default value is dynamic based on the platform and is analogous to `auto`.

### `django_autoinsert_middleware`

The Elastic [`django_transaction_name_from_route`](apm-agent-python://reference/configuration.md#config-django-autoinsert-middleware) option does not have a correspondant option but is enabled by default in OpenTelemetry Python.

### `django_transaction_name_from_route`

The Elastic [`django_transaction_name_from_route`](apm-agent-python://reference/configuration.md#config-django-transaction-name-from-route) option does not have a correspondant option but is enabled by default in OpenTelemetry Python.

### `enabled`

The Elastic [`enabled`](apm-agent-python://reference/configuration.md#config-enabled) option corresponds to the OpenTelemetry [OTEL_SDK_DISABLED](https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/#general-sdk-configuration) environment_variable.

### `environment`

The Elastic [`environment`](apm-agent-python://reference/configuration.md#config-environment) option corresponds to setting the `deployment.environment.name` key in [OTEL_RESOURCE_ATTRIBUTES](https://opentelemetry.io/docs/concepts/sdk-configuration/general-sdk-configuration/#otel_resource_attributes).

For example: `OTEL_RESOURCE_ATTRIBUTES=deployment.environment.name=testing`.

### `global_labels`

The Elastic [`global_labels`](apm-agent-python://reference/configuration.md#config-global_labels) option corresponds to adding `key=value` comma separated pairs in [OTEL_RESOURCE_ATTRIBUTES](https://opentelemetry.io/docs/concepts/sdk-configuration/general-sdk-configuration/#otel_resource_attributes).

For example: `OTEL_RESOURCE_ATTRIBUTES=alice=first,bob=second`. Such labels will result in resource.attributes.key=value attributes on the server, e.g. resource.attributes.alice=first

### `include_process_args`

The Elastic [`include_process_args`](apm-agent-python://reference/configuration.md#config-include-process-args) option corresponds to include the `ProcessResourceDetector` to `OTEL_EXPERIMENTAL_RESOURCE_DETECTORS` environment variable, see [default value of OTEL_EXPERIMENTAL_RESOURCE_DETECTORS](/reference/edot-python/setup/configuration.md##differences-from-opentelemetry-python).

### `metrics_interval`

The Elastic [`metrics_interval`](apm-agent-python://reference/configuration.md#config-metrics_interval) corresponds to the OpenTelemetry [OTEL_METRIC_EXPORT_INTERVAL](https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/#periodic-exporting-metricreader) environment variable.

For example: `OTEL_METRIC_EXPORT_INTERVAL=30000`.

### `sanitize_field_names`

The Elastic [`sanitize_field_names`](apm-agent-python://reference/configuration.md#config-sanitize-fieldnames) option used not have a complete counterpart, for captured headers sanitization see [capture_headers](#capture-headers).

### `secret_token`

The Elastic [`secret_token`](apm-agent-python://reference/configuration.md#config-secret-token) option corresponds to the OpenTelemetry [OTEL_EXPORTER_OTLP_HEADERS](https://opentelemetry.io/docs/concepts/sdk-configuration/otlp-exporter-configuration/#otel_exporter_otlp_headers) environment variable.

For example: `OTEL_EXPORTER_OTLP_HEADERS="Authorization=ApiKey an_apm_secret_token"`.

### `server_timeout`

The Elastic [`server_timeout`](apm-agent-python://reference/configuration.md#config-server-timeout) option corresponds to the OpenTelemetry [`OTEL_EXPORTER_OTLP_TIMEOUT`](https://opentelemetry.io/docs/languages/sdk-configuration/otlp-exporter/#otel_exporter_otlp_timeout) environment variable.

### `server_url`

The Elastic [`server_url`](apm-agent-python://reference/configuration.md#config-server-url) option corresponds to the OpenTelemetry [`OTEL_EXPORTER_OTLP_ENDPOINT`](https://opentelemetry.io/docs/concepts/sdk-configuration/otlp-exporter-configuration/#otel_exporter_otlp_endpoint) environment variable.

### `service_name`

The Elastic [`service_name`](apm-agent-python://reference/configuration.md#config-service-name) option corresponds to the OpenTelemetry [OTEL_SERVICE_NAME](https://opentelemetry.io/docs/concepts/sdk-configuration/general-sdk-configuration/#otel_service_name) environment variable.

You can also set the service name using [OTEL_RESOURCE_ATTRIBUTES](https://opentelemetry.io/docs/concepts/sdk-configuration/general-sdk-configuration/#otel_resource_attributes).

For example: `OTEL_RESOURCE_ATTRIBUTES=service.name=myservice`. If `OTEL_SERVICE_NAME` is set, it takes precedence over the resource attribute.

### `service_version`

The Elastic [`service_version`](apm-agent-python://reference/configuration.md#config-service-version) option corresponds to setting the `service.version` key in [OTEL_RESOURCE_ATTRIBUTES](https://opentelemetry.io/docs/concepts/sdk-configuration/general-sdk-configuration/#otel_resource_attributes).

For example: `OTEL_RESOURCE_ATTRIBUTES=service.version=1.2.3`.

### `transaction_ignore_patterns` and `transaction_ignore_urls`

The Elastic [`transaction_ignore_patterns`](apm-agent-python://reference/configuration.md#config-transaction-ignore-patterns) and [`transaction_ignore_urls`](apm-agent-python://reference/configuration.md#config-transaction-ignore-urls) options correspond to setting the [OTEL_PYTHON_EXCLUDED_URLS](https://opentelemetry.io/docs/zero-code/python/configuration/#excluded-urls) environment variable.

## Performance overhead

Evaluate the [differences in performance overhead](/reference/edot-python/overhead.md) between EDOT Python and Elastic APM Python agent.

## Limitations

The following limitations apply when migrating to EDOT Python.

### Central and dynamic configuration

You can manage EDOT Python configurations through the [central configuration feature](docs-content://solutions/observability/apm/apm-agent-central-configuration.md) in the Applications UI.

Refer to [Central configuration](opentelemetry://reference/central-configuration.md) for more information.

### AWS Lambda

A custom lambda layer for the {{edot}} Python is not currently available. Refer to the [Lambda Auto-Instrumentation](https://opentelemetry.io/docs/faas/lambda-auto-instrument/).

### Missing instrumentations

The following libraries are currently missing an OpenTelemetry equivalent:

- Azure storage and Azure queue
- `aiobotocore`
- `aiomysql`
- `aioredis`
- `Graphene`
- `httplib2`
- `pylibmc`
- `pyodbc`
- `python-memcached`
- `Sanic`
- `zlib`

### Integration with structured logging

EDOT Python lacks a [structlog integration](apm-agent-python://reference/logs.md#structlog) at the moment.

### Span compression

EDOT Python does not implement [span compression](docs-content://solutions/observability/apm/spans.md#apm-spans-span-compression).

### Breakdown metrics

EDOT Python is not sending metrics that power the [Breakdown metrics](docs-content://solutions/observability/apm/metrics.md#_breakdown_metrics).

## Troubleshooting

If you're encountering issues during migration, refer to the [EDOT Python troubleshooting guide](docs-content://troubleshoot/ingest/opentelemetry/edot-sdks/python/index.md).
