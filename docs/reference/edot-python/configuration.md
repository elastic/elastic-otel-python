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

Configure the {{edot}} Python (EDOT Python) to send data to Elastic!

## Configuration method

Configure the OpenTelemetry SDK through the mechanisms [documented on the OpenTelemetry website](https://opentelemetry.io/docs/zero-code/python/configuration/). EDOT Python is typically configured with `OTEL_*` environment variables defined by the OpenTelemetry spec. For example:

```sh
export OTEL_RESOURCE_ATTRIBUTES=service.name=<app-name>,deployment.environment.name=<env-name>
export OTEL_EXPORTER_OTLP_ENDPOINT=https://my-deployment.ingest.us-west1.gcp.cloud.es.io
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=ApiKey P....l"
opentelemetry-instrument <command to start your service>
```

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

Instrument Python `logging` module to format and forward logs in OTLP format is turned off by default and gated under a configuration environment variable:

```sh
export OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true
```

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
Set the environment variable to a comma delimited list of HTTP header names to be sanitized. You can use use regular expressions. 
All header names are matched in a case-insensitive manner.

This example replaces the values of the `set-cookie` header and headers such as `session-id` that matches the provided regular expression with `[REDACTED]` in the span:

```sh
export OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SANITIZE_FIELDS=".*session.*,set-cookie"
```
#### Differences from OpenTelemetry Python

EDOT Python uses different defaults than OpenTelemetry Python for the following configuration options:

| Option | EDOT Python default | OpenTelemetry Python default | Notes |
|---|---|---|---|
| `OTEL_EXPERIMENTAL_RESOURCE_DETECTORS` | `process_runtime,os,otel,telemetry_distro,service_instance,containerid,_gcp,aws_ec2,aws_ecs,aws_elastic_beanstalk,azure_app_service,azure_vm` | `otel` | |
| `OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE` | `DELTA` | `CUMULATIVE` | |
| `OTEL_LOG_LEVEL` | `warn` | | {applies_to}`edot_python: ga 1.9.0` |
| `OTEL_METRICS_EXEMPLAR_FILTER` | `always_off` | `trace_based` | |
| `OTEL_TRACES_SAMPLER` | `experimental_composite_parentbased_traceidratio` | `parentbased_always_on` | {applies_to}`edot_python: ga 1.10.0`<br><br>The EDOT Python default was previously `parentbased_traceidratio` {applies_to}`edot_python: ga 1.5-1.9` |
| `OTEL_TRACES_SAMPLER_ARG` | `1.0` | | {applies_to}`edot_python: ga 1.6.0`|

:::{note}
`OTEL_EXPERIMENTAL_RESOURCE_DETECTORS` cloud resource detectors are dynamically set. When running in a Kubernetes Pod it will be set to `process_runtime,os,otel,telemetry_distro,service_instance,_gcp,aws_eks`.
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
