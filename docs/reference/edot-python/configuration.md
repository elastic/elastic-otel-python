---
navigation_title: Configuration
description: Configure the Elastic Distribution of OpenTelemetry Python (EDOT Python) to send data to Elastic.
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
---

# Configure the EDOT Python agent

Configure the {{edot}} Python (EDOT Python) to send data to Elastic.

## Configuration method

Configure the OpenTelemetry SDK through the mechanisms [documented on the OpenTelemetry website](https://opentelemetry.io/docs/zero-code/python/configuration/). EDOT Python is typically configured with `OTEL_*` environment variables defined by the OpenTelemetry spec. For example:

```sh
export OTEL_RESOURCE_ATTRIBUTES=service.name=<app-name>,deployment.environment.name=<env-name>
export OTEL_EXPORTER_OTLP_ENDPOINT=https://my-deployment.ingest.us-west1.gcp.cloud.es.io
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=ApiKey P....l"
opentelemetry-instrument <command to start your service>
```

## Declarative configuration

```{applies_to}
product:
  edot_python: preview 1.19.0
```

Declarative configuration describes resources, telemetry pipelines, sampling, and propagation in a YAML or JSON file. EDOT Python can load this file through the experimental OpenTelemetry configuration package. For details, refer to the [upstream Python declarative configuration documentation](https://opentelemetry-python.readthedocs.io/en/latest/sdk/configuration.html).

### Install configuration support

Install EDOT Python with the `config` extra in your application's environment, then install the instrumentations for your application's libraries:

```sh
pip install 'elastic-opentelemetry[config]'
edot-bootstrap --action=install
```

### Create the configuration file

Save the following as `edot-python-config.yaml`. It reproduces EDOT's default OTLP/gRPC pipelines, initial sampling policy, delta metric temporality, turned off exemplars, and resource detector order. The cloud-detector list must be adjusted for the environments in the following section.

```yaml
# Install elastic-opentelemetry[config] and set OTEL_CONFIG_FILE to this file.
# Run through EDOT's opentelemetry-instrument entry point to retain its
# instrumentation setup, runtime-metric filtering, and central configuration.
# Declarative SDK construction does not retain EDOT's exporter user-agent or
# DefaultSampler wrapper, so central sampling-rate updates are unavailable.
file_format: "1.0"
disabled: ${OTEL_SDK_DISABLED:-false}
log_level: ${OTEL_LOG_LEVEL:-warn}

resource:
  detection/development:
    detectors:
      - process_runtime: {}
      - os: {}
      - telemetry_distro: {}
      - service_instance: {}
      - containerid: {}

      # EDOT's cloud-detector list when none of its environment checks match.
      # YAML cannot select detectors conditionally. Replace these six entries
      # with the appropriate list for your environment (first match wins):
      # AWS_LAMBDA_FUNCTION_NAME set: aws_lambda
      # FUNCTIONS_WORKER_RUNTIME set: azure_functions
      # K_CONFIGURATION set: gcp_resource_detector
      # KUBERNETES_SERVICE_HOST set: gcp_resource_detector, aws_eks
      - gcp_resource_detector: {}
      - aws_ec2: {}
      - aws_ecs: {}
      - aws_elastic_beanstalk: {}
      - azure_app_service: {}
      - azure_vm: {}

      # Keep last: applies OTEL_RESOURCE_ATTRIBUTES and then OTEL_SERVICE_NAME,
      # preserving EDOT's environment-variable precedence over detection.
      - otel: {}

propagator:
  composite_list: ${OTEL_PROPAGATORS:-tracecontext,baggage}

tracer_provider:
  processors:
    - batch:
        exporter:
          otlp_grpc:
            endpoint: ${OTEL_EXPORTER_OTLP_ENDPOINT}
            headers_list: ${OTEL_EXPORTER_OTLP_HEADERS}
  sampler:
    composite/development:
      parent_threshold:
        root:
          probability:
            ratio: ${OTEL_TRACES_SAMPLER_ARG:-1.0}

meter_provider:
  exemplar_filter: ${OTEL_METRICS_EXEMPLAR_FILTER:-always_off}
  readers:
    - periodic:
        exporter:
          otlp_grpc:
            endpoint: ${OTEL_EXPORTER_OTLP_ENDPOINT}
            headers_list: ${OTEL_EXPORTER_OTLP_HEADERS}
            temporality_preference: ${OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE:-delta}

logger_provider:
  processors:
    - batch:
        exporter:
          otlp_grpc:
            endpoint: ${OTEL_EXPORTER_OTLP_ENDPOINT}
            headers_list: ${OTEL_EXPORTER_OTLP_HEADERS}
```

The `otel` detector reads `OTEL_RESOURCE_ATTRIBUTES` and `OTEL_SERVICE_NAME`. Keeping it last lets those values override detected resource attributes, with `OTEL_SERVICE_NAME` taking precedence when both variables specify a service name.

EDOT normally selects cloud detectors automatically. A static YAML file cannot express that selection. The example uses EDOT's fallback list for environments outside AWS Lambda, Azure Functions, Google Cloud Run, and Kubernetes. In those environments, replace the six cloud detectors according to the comments in the example. Preserve the base detectors and the final `otel` detector.

### Start your application

Set `OTEL_CONFIG_FILE` to the file's path and start your application with `opentelemetry-instrument`:

```sh
export OTEL_CONFIG_FILE="$PWD/edot-python-config.yaml"
export OTEL_SERVICE_NAME=my-service
export OTEL_EXPORTER_OTLP_ENDPOINT=https://my-deployment.ingest.us-west1.gcp.cloud.es.io
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=ApiKey P....l"
opentelemetry-instrument python app.py
```

The example reads the endpoint and authentication headers from the environment. If no endpoint is set, the exporters use their local collector default. To change the initial sampling ratio, set `OTEL_TRACES_SAMPLER_ARG` to a number between `0.0` and `1.0`. Metric temporality values must be lowercase, for example `delta`.

The file controls SDK construction. Environment settings with declarative equivalents must be represented in the file, for example through `${VAR}` or `${VAR:-default}` references. The example keeps the default gRPC exporters; changing `OTEL_EXPORTER_OTLP_PROTOCOL` alone does not switch these exporters to HTTP. The same applies to selecting a different sampler with `OTEL_TRACES_SAMPLER`: edit the sampler in the file instead.

### Rule-based sampling

Use the experimental rule-based sampler to exclude requests based on attributes available when a span starts. For example, the following configuration drops HTTP root spans whose `url.path` is `/rolldice` and samples all other root spans.

In a copy of the configuration above named `config.yaml`, replace `tracer_provider.sampler` with the following sampler block. Keep the existing processors, exporters, and other provider settings:

```yaml
tracer_provider:
  ...
  sampler:
    composite/development:
      parent_threshold:
        root:
          rule_based:
            rules:
              - attribute_patterns:
                  key: url.path
                  included:
                    - "/rolldice"
                sampler:
                  always_off:
              - sampler:
                  probability:
                    ratio: 1.0
```

Rules are evaluated in order, and the first matching rule selects the sampler. The first rule uses `always_off` for the matching path. The final rule has no conditions and samples all remaining root spans, including spans without a `url.path` attribute. Patterns are case-sensitive; use `/rolldice/*` to match paths below `/rolldice/`. Refer to the [upstream rule-based sampler configuration reference](https://opentelemetry.io/docs/specs/otel-config/types/#experimentalcomposablerulebasedsampler) for other conditions.

This example uses the [stable HTTP semantic conventions](https://opentelemetry.io/docs/specs/semconv/http/), including `url.path`. With Flask and its instrumentation installed, opt in to those conventions when starting the application:

```sh
OTEL_SEMCONV_STABILITY_OPT_IN=http OTEL_CONFIG_FILE=config.yaml opentelemetry-instrument flask run
```

The rules are under `parent_threshold.root`, so they apply only when there is no valid parent span context. Requests with an incoming parent context follow the parent's sampling decision, even when the path matches `/rolldice`. Child spans also follow their parent's sampling decision.

Sampling runs when the span is created. Rules can only inspect attributes supplied at that point; attributes added later, such as the HTTP response status code, cannot affect this decision.

### Differences from environment-based configuration

This example preserves the settings in the preceding section, with these limitations:

- Cloud detector selection is manual, as earlier on this page.
- The declarative loader creates the upstream composite sampler instead of EDOT updateable sampler wrapper. Initial sampling works, but central configuration cannot update the sampling rate.
- Exporters use the upstream user-agent because declarative construction bypasses EDOT exporter customization.

Continue using EDOT's `opentelemetry-instrument` startup path to retain EDOT's instrumentation setup and runtime-metric filtering. Calling the upstream `configure_sdk()` function directly does not run that setup.

### Upstream SDK compatibility

This configuration requires EDOT Python. A clean upstream OpenTelemetry SDK installation with the `opentelemetry-configuration` package installed accepts the file's schema, but is missing the `process_runtime` and `telemetry_distro` resource detectors supplied by EDOT.
Cloud and container detectors require their respective packages to be installed.

## Configuration options

Because the {{edot}} Python is an extension of OpenTelemetry Python, it supports both:

* [General OpenTelemetry configuration options](#opentelemetry-configuration-options)
* [Specific configuration options that are only available in EDOT Python](#configuration-options-only-available-in-edot-python)

## Central configuration

```{applies_to}
serverless: unavailable
stack: preview 9.1
product:
  edot_python: preview 1.4.0
```

APM Agent Central Configuration lets you configure EDOT Python instances remotely, see [Central configuration docs](opentelemetry://reference/central-configuration.md) for more details.

### Turn on central configuration

To activate central configuration, set the `ELASTIC_OTEL_OPAMP_ENDPOINT` environment variable to the OpAMP server endpoint.

```sh
export ELASTIC_OTEL_OPAMP_ENDPOINT=http://localhost:4320/v1/opamp
```

To deactivate central configuration, remove the `ELASTIC_OTEL_OPAMP_ENDPOINT` environment variable and restart the instrumented application.

### Central configuration authentication

```{applies_to}
serverless: unavailable
stack: preview 9.1
product:
  edot_python: preview 1.10.0
```

If the OpAMP server is configured to require authentication set the `ELASTIC_OTEL_OPAMP_HEADERS` environment variable.

```sh
export ELASTIC_OTEL_OPAMP_HEADERS="Authorization=ApiKey an_api_key"
```

### Configure mTLS for Central configuration

```{applies_to}
serverless: unavailable
stack: preview 9.1
product:
  edot_python: preview 1.10.0
```

If the OpAMP Central configuration server requires mutual TLS to encrypt data in transit you need to set the following environment variables:

- `ELASTIC_OTEL_OPAMP_CERTIFICATE`: The path of the trusted certificate, in PEM format, to use when verifying a server’s TLS credentials, this may also be used if the server is using a self-signed certificate.
- `ELASTIC_OTEL_OPAMP_CLIENT_CERTIFICATE`: Client certificate/chain trust for clients private key path to use in mTLS communication in PEM format.
- `ELASTIC_OTEL_OPAMP_CLIENT_KEY`: Client private key path to use in mTLS communication in PEM format.

```sh
export ELASTIC_OTEL_OPAMP_CERTIFICATE=/path/to/rootCA.pem
export ELASTIC_OTEL_OPAMP_CLIENT_CERTIFICATE=/path/to/client.pem
export ELASTIC_OTEL_OPAMP_CLIENT_KEY=/path/to/client-key.pem
```

### Central configuration settings

You can modify the following settings for EDOT Python through APM Agent Central Configuration:

| Settings      | Description                                  | Type    | Versions |
|---------------|----------------------------------------------|---------|---------|
| Logging level | Configure EDOT Python agent logging level.   | Dynamic | {applies_to}`stack: preview 9.1` <br> {applies_to}`edot_python: preview 1.4.0` |
| Sampling rate | Configure EDOT Python tracing sampling rate. | Dynamic | {applies_to}`stack: preview 9.2` <br> {applies_to}`edot_python: preview 1.7.0` |
| Deactivate instrumentations | Configure EDOT Python to deactivate tracers for specific instrumentations, supports globbing. Refer to [EDOT Python Supported technologies](/reference/edot-python/supported-technologies.md) for the names of the tracers. | Dynamic | {applies_to}`stack: preview 9.4` <br> {applies_to}`edot_python: preview 1.12.0` |

Dynamic settings can be changed without having to restart the application.

### OpenTelemetry configuration options

EDOT Python supports all configuration options listed in the [OpenTelemetry General SDK Configuration documentation](https://opentelemetry.io/docs/languages/sdk-configuration/general/) and [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python).

#### TLS configuration for OTLP endpoint

To secure the connection to the OTLP endpoint using TLS, you can configure the following environment variables:

| Option | Description |
|---|---|
| `OTEL_EXPORTER_OTLP_CERTIFICATE` | The path of the trusted certificate, in PEM format, to use when verifying a server’s TLS credentials, this may also be used if the server is using a self-signed certificate. |
| `OTEL_EXPORTER_OTLP_CLIENT_CERTIFICATE` | Client certificate/chain trust for clients private key path to use in mTLS communication in PEM format. |
| `OTEL_EXPORTER_OTLP_CLIENT_KEY` | Client private key path to use in mTLS communication in PEM format. |

Signal-specific variants are also supported: `OTEL_EXPORTER_OTLP_{TRACES,METRICS,LOGS}_CERTIFICATE`, `OTEL_EXPORTER_OTLP_{TRACES,METRICS,LOGS}_CLIENT_CERTIFICATE`, and `OTEL_EXPORTER_OTLP_{TRACES,METRICS,LOGS}_CLIENT_KEY`.

For more details, refer to the [OpenTelemetry OTLP Exporter documentation](https://opentelemetry.io/docs/specs/otel/protocol/exporter/).

#### Logs

```{applies_to}
product:
  edot_python: preview 1.12.0
```

Instrument Python `logging` module to format and forward logs in OTLP format is handled by the `opentelemetry-instrumentation-logging` package and enabled by default. You can deactivate it using an environment variable:

```sh
export OTEL_PYTHON_LOG_AUTO_INSTRUMENTATION=false
```

Refer to [opentelemetry-instrumentation-logging documentation](https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/logging/logging.html) for more configuration options.

:::{note}
{applies_to}`edot_python: ga 1.0.0-1.11.0`

On earlier versions the `logging` module instrumentation was available in the `opentelemetry-sdk` package, turned off by default and gated under a configuration environment variable:

```sh
export OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true
```
:::

#### HTTP headers capture

You can capture HTTP headers as span attributes on both client and server HTTP instrumentations according to [HTTP semantic conventions](https://opentelemetry.io/docs/specs/semconv/http-spans/). Refer to [`http.request.header.<key>`](https://opentelemetry.io/docs/specs/semconv/registry/attributes/http/#http-request-header) and [`http.response.header.<key>`](https://opentelemetry.io/docs/specs/semconv/registry/attributes/http/#http-response-header) attributes.

##### server

```{applies_to}
product:
  edot_python: preview 1.11.0
```

To define which HTTP headers you want to capture, provide a comma-separated list
of HTTP header names through the environment variables
`OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST` and
`OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_RESPONSE`, for example:

```sh
export OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST="Accept-Encoding,User-Agent,Referer"
export OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_RESPONSE="Last-Modified,Content-Type"
```

These configuration options are supported by the following HTTP server instrumentations:

- Aiohttp-server
- ASGI
- Django
- Falcon
- FastAPI
- Flask
- Pyramid
- Starlette
- Tornado
- WSGI

##### client

```{applies_to}
product:
  edot_python: preview 1.12.0
```

To define which HTTP headers you want to capture, provide a comma-separated list
of HTTP header names through the environment variables
`OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_CLIENT_REQUEST` and
`OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_CLIENT_RESPONSE`, for example:

```sh
export OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_CLIENT_REQUEST="Accept-Encoding,User-Agent,Referer"
export OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_CLIENT_RESPONSE="Last-Modified,Content-Type"
```

These configuration options are supported by the following HTTP client instrumentations:

- Aiohttp-client
- httpx
- requests
- urllib
- urllib3

##### Sanitization of captured headers

```{applies_to}
product:
  edot_python: preview 1.11.0
```

Some headers might contain sensitive data such as personally identifiable information (PII), session keys, passwords, and so on. To avoid storing this data, OpenTelemetry Python provides a sanitization system through the `OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SANITIZE_FIELDS`
environment variable.
Set the environment variable to a comma delimited list of HTTP header names to be sanitized. You can use regular expressions.
All header names are matched in a case-insensitive manner.

This example replaces the values of the `set-cookie` header and headers such as `session-id` that matches the provided regular expression with `[REDACTED]` in the span:

```sh
export OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SANITIZE_FIELDS=".*session.*,set-cookie"
```

#### OpenTelemetry SDK metrics

```{applies_to}
product:
  edot_python: preview 1.14.0
```

[OpenTelemetry SDK metrics](https://opentelemetry.io/docs/specs/semconv/otel/sdk-metrics/) are not enabled by default, you can enable them setting the `OTEL_PYTHON_SDK_INTERNAL_METRICS_ENABLED` environment variable to `true`:

```sh
export OTEL_PYTHON_SDK_INTERNAL_METRICS_ENABLED=true
```

#### Differences from OpenTelemetry Python

EDOT Python uses different defaults than OpenTelemetry Python for the following configuration options:

| Option | EDOT Python default | OpenTelemetry Python default | Notes |
|---|---|---|---|
| `OTEL_EXPERIMENTAL_RESOURCE_DETECTORS` | `process_runtime,os,telemetry_distro,service_instance,containerid,gcp_resource_detector,aws_ec2,aws_ecs,aws_elastic_beanstalk,azure_app_service,azure_vm,otel` | `service_instance,otel` | |
| `OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE` | `DELTA` | `CUMULATIVE` | |
| `OTEL_LOG_LEVEL` | `warn` | | {applies_to}`edot_python: ga 1.9.0` |
| `OTEL_METRICS_EXEMPLAR_FILTER` | `always_off` | `trace_based` | |
| `OTEL_TRACES_SAMPLER` | `experimental_composite_parentbased_traceidratio` | `parentbased_always_on` | {applies_to}`edot_python: ga 1.10.0`<br><br>The EDOT Python default was previously `parentbased_traceidratio` {applies_to}`edot_python: ga 1.5-1.9` |
| `OTEL_TRACES_SAMPLER_ARG` | `1.0` | | {applies_to}`edot_python: ga 1.6.0`|

:::{note}
`OTEL_EXPERIMENTAL_RESOURCE_DETECTORS` cloud resource detectors are dynamically set. When running in a Kubernetes Pod it will be set to `process_runtime,os,telemetry_distro,service_instance,gcp_resource_detector,aws_eks,otel`.
:::

:::{note}
`OTEL_LOG_LEVEL` accepts the following levels: `trace`, `debug`, `info`, `warn`, `error`, `fatal`, `off`.
:::

### Configuration options only available in EDOT Python

`ELASTIC_OTEL_` options are specific to Elastic and will always live in EDOT Python include the following.

| Option(s) | Default | Description |
|---|---|---|
| `ELASTIC_OTEL_SYSTEM_METRICS_ENABLED` | `false` | When set to `true`, sends *system namespace* metrics. |

## LLM settings

LLM instrumentations implement the following configuration options:

| Option                                                | default | description               |
|-------------------------------------------------------|---------|:--------------------------|
| `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT`  | `false`| If set to `true`, enables the capturing of request and response content in the log events outputted by the agent.


## Prevent logs export

To prevent logs from being exported, set `OTEL_LOGS_EXPORTER` to `none`. However, application logs might still be gathered and exported by the Collector through the `filelog` receiver.

To prevent application logs from being collected and exported by the Collector, refer to [Exclude paths from logs collection](elastic-agent://reference/edot-collector/config/configure-logs-collection.md#exclude-logs-paths).
