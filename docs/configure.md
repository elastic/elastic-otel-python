<!--
Goal of this doc:
Provide a complete reference of all available configuration options and where/how they can be set.
Any Elastic-specific configuration options are listed directly.
General OpenTelemetry configuration options are linked.
-->

# Configuration

Configure the Elastic Distribution of OpenTelemetry Python (EDOT Python) to send data to Elastic.

<!-- How users set configuration options -->
## Configuration method

<!-- Is this the right link to OpenTelemetry docs? -->
Configuration of the OpenTelemetry SDK should be performed through the mechanisms [documented on the OpenTelemetry website](https://opentelemetry.io/docs/zero-code/python/configuration/). EDOT Python is typically configured with `OTEL_*` environment variables defined by the OpenTelemetry spec. For example:

<!-- Would this example work? -->
```sh
export OTEL_RESOURCE_ATTRIBUTES=service.name=<app-name>
export OTEL_EXPORTER_OTLP_ENDPOINT=https://my-deployment.apm.us-west1.gcp.cloud.es.io
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Bearer P....l"
opentelemetry-instrument <command to start your service>
```

<!-- List all available configuration options -->
## Configuration options

<!-- Is the distro an extension of the OTel Python SDK? The agent? Or neither? -->
Because the Elastic Distribution of OpenTelemetry Python is an extension of the OpenTelemetry Python SDK, it supports:

* [OpenTelemetry configuration options](#opentelemetry-configuration-options)
* [Configuration options that are _only_ available in EDOT Python](#configuration-options-that-are-only-available-in-edot-python)

### OpenTelemetry configuration options

EDOT Python supports all configuration options listed in the [OpenTelemetry General SDK Configuration documentation](https://opentelemetry.io/docs/languages/sdk-configuration/general/) and [OpenTelemetry Python SDK](https://opentelemetry.io/docs/languages/python).

<!-- Is this true? Or did you list these in the README for some other reason? -->
EDOT Python uses different defaults than the OpenTelemetry Python SDK for the following configuration options:

| Option | EDOT Python default | OpenTelemetry Python agent default |
|---|---|---|
| `OTEL_TRACES_EXPORTER` | `otlp` | ?? ([docs](#)) |
| `OTEL_METRICS_EXPORTER` | `otlp` | ?? ([docs](#)) |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | `grpc` | ?? ([docs](#)) |
| `OTEL_EXPERIMENTAL_RESOURCE_DETECTORS` | `process_runtime,otel,telemetry_distro` | ?? ([docs](#)) |


### Configuration options that are _only_ available in EDOT Python

In addition to general OpenTelemetry configuration options, there are two kinds of configuration options that are _only_ available in EDOT Python.

<!-- This is true for the Java distro, is it also true of the Python distro? -->
**Elastic-authored options that are not yet available upstream**

Additional `OTEL_` options that Elastic plans to contribute upstream to the OpenTelemetry Python SDK, but are not yet available in the OpenTelemetry Python SDK.

_Currently there are no additional `OTEL_` options waiting to be contributed upstream._

**Elastic-specific options**

`ELASTIC_OTEL_` options that are specific to Elastic and will always live in EDOT Python (in other words, they will _not_ be added upstream):

| Option(s) | Default | Description |
|---|---|---|
| `ELASTIC_OTEL_SYSTEM_METRICS_ENABLED` | `false` | When sets to `true`, sends *system namespace* metrics. |
