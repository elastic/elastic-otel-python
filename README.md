# elastic-opentelemetry -- Elastic Distribution of OpenTelemetry Python

`elastic-opentelemetry` is the Elastic Distribution of OpenTelemetry Python.

## Installation

```bash
pip install elastic-opentelemetry
```

## Usage

Our distribution does not install any instrumentation package by default, instead it relies on the
`opentelemetry-bootstrap` command to scan the installed packages and install the available instrumentation.
The following command will install all the instrumentations available for libraries found installed
in your environment:

```bash
opentelemetry-bootstrap --action=install
```

It will be useful to add this command every time you need to deploy an updated version of your application,
e.g. into your container image build process.

At runtime you have to make some environment variables available to provide the needed configuration.
A *service name* is required to have your app easily recognizable from the other. Then you need to provide
the *authorization* headers for authentication with Elastic cloud and the project endpoint where to send your data.
For details about the authentication format see the chapter below.

```bash
OTEL_RESOURCE_ATTRIBUTES=service.name=<app-name>
OTEL_EXPORTER_OTLP_HEADERS="Authorization=<url encoded apikey header value>"
OTEL_EXPORTER_OTLP_ENDPOINT=<your elastic cloud url>
```

We are done with the configuration and the last piece of the puzzle is wrapping your service invocation with
`opentelemetry-instrument` that is the wrapper that provides *automatic instrumentation*:

```bash
opentelemetry-instrument <command to start your service>
```

For a web service running with gunicorn it may looks like:

```bash
opentelemetry-instrument gunicorn main:app
```

## Authentication

Authentication is done passing an URL encoded API Key as `Authorization` header, given the Api Key available
from your project dashboard you can encode it this way:

```python
from urllib.parse import quote
quote("ApiKey <your api key>")
```

In the end it will look something like the following:

"ApiKey%20RM2sVN55Su49RgCYNI7SvYoeyWCyt3sbdFirjvmtin6IavUfZrBXCInwao%3D%3D"

## Configuration

The distribution supports all the configuration variables from OpenTelemetry Python project version 1.25.0.

### Default configuration variables

This distribution sets the following defaults:

- `OTEL_TRACES_EXPORTER`: `otlp`
- `OTEL_METRICS_EXPORTER`: `otlp`
- `OTEL_EXPORTER_OTLP_PROTOCOL`: `grpc`
- `OTEL_EXPERIMENTAL_RESOURCE_DETECTORS`: `process_runtime,otel,telemetry_distro`

### Distribution specific configuration variables

- `ELASTIC_OTEL_SYSTEM_METRICS_ENABLED` (default: `false`): when sets to `true` sends *system namespace* metrics.

## License

This software is licensed under the Apache License, version 2 ("Apache-2.0").
