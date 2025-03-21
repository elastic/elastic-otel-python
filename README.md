# Elastic Distribution of OpenTelemetry Python

> [!WARNING]
> The Elastic Distribution of OpenTelemetry Python is not yet recommended for production use. Functionality may be changed or removed in future releases. Alpha releases are not subject to the support SLA of official GA features.
>
> We welcome your feedback! You can reach us by [opening a GitHub issue](https://github.com/elastic/elastic-otel-python/issues) or starting a discussion thread on the [Elastic Discuss forum](https://discuss.elastic.co/tags/c/observability/apm/58/python).

The Elastic Distribution of OpenTelemetry Python (EDOT Python) is a customized version of [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python).
EDOT Python makes it easier to get started using OpenTelemetry in your Python applications through strictly OpenTelemetry native means, while also providing a smooth and rich out of the box experience with [Elastic Observability](https://www.elastic.co/observability). It's an explicit goal of this distribution to introduce **no new concepts** in addition to those defined by the wider OpenTelemetry community.

With EDOT Python you have access to all the features of the OpenTelemetry Python agent plus:

* Access to improvements and bug fixes contributed by the Elastic team _before_ the changes are available upstream in OpenTelemetry repositories.
* Access to optional features that can enhance OpenTelemetry data that is being sent to Elastic.
* Elastic-specific processors that ensure optimal compatibility when exporting OpenTelemetry signal data to an Elastic backend like an Elastic Observability deployment.
* Preconfigured collection of tracing and metrics signals, applying some opinionated defaults, such as which sources are collected by default.

**Ready to try out EDOT Python?** Follow the step-by-step instructions in [Get started](./docs/get-started.md).

## Read the docs

* [Get started](./docs/get-started.md)
* [Supported technologies](./docs/supported-techologies.md)
* [Manual instrumentation](./docs/manual-instrumentation.md)
* [Configuration](./docs/configure.md)
* [Migrating from Elastic APM Python Agent](./docs/migrate-from-apm.md)
* [Troubleshooting](./docs/troubleshooting.md)

## Install

```bash
pip install elastic-opentelemetry
```

<!-- I'll let you decide how much to keep here from the content below vs rely on content in the docs directory -->

## Usage

Our distribution does not install any instrumentation package by default, instead it relies on the
`edot-bootstrap` command to scan the installed packages and install the available instrumentation, preferring EDOT variants when available.
The following command will install all the instrumentations available for libraries found installed
in your environment:

```bash
edot-bootstrap --action=install
```

It will be useful to add this command every time you need to deploy an updated version of your application,
e.g. into your container image build process.

At runtime you have to make some environment variables available to provide the needed configuration.
A *service name* is required to have your app easily recognizable from the other. Then you need to provide
the *authorization* headers for authentication with Elastic cloud and the project endpoint where to send your data.

```bash
OTEL_RESOURCE_ATTRIBUTES=service.name=<app-name>
OTEL_EXPORTER_OTLP_HEADERS="Authorization=<authorization header value>"
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

## Configuration

The distribution supports all the configuration variables from OpenTelemetry Python project version 1.31.1.

See [Configuration](./docs/configure.md) for more details.

## License

This software is licensed under the Apache License, version 2 ("Apache-2.0").
