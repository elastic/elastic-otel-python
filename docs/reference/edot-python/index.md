---
navigation_title: Elastic OTel Python
description: The Elastic OTel Python is a customized version of OpenTelemetry Python.
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

# Elastic OTel Python [elastic-distribution-of-opentelemetry-python]

The [Elastic OTel Python](https://github.com/elastic/elastic-otel-python) is a customized version of [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python), configured for the best experience with Elastic Observability. 

Use Elastic OTel Python to start the OpenTelemetry SDK with your Python application, and automatically capture tracing data, performance metrics, and logs. Traces, metrics, and logs can be sent to any OpenTelemetry Protocol (OTLP) Collector you choose.

A goal of this distribution is to avoid introducing proprietary concepts in addition to those defined by the wider OpenTelemetry community. For any additional features introduced, Elastic aims at contributing them back to the OpenTelemetry project.

## Features

In addition to all the features of the OpenTelemetry Python agent, with Elastic OTel Python you have access to the following:

* Improvements and bug fixes contributed by the Elastic team before the changes are available in OpenTelemetry repositories.
* Optional features that can enhance OpenTelemetry data that is being sent to Elastic.
* Elastic-specific processors that ensure optimal compatibility when exporting OpenTelemetry signal data to an Elastic backend like an Elastic Observability deployment.
* Preconfigured collection of tracing and metrics signals, applying some opinionated defaults, such as which sources are collected by default.
* Compatibility with APM Agent Central Configuration to modify the settings of the Elastic OTel Python agent without having to restart the application.

Follow the step-by-step instructions in [Setup](/reference/edot-python/setup/index.md) to get started.

## Release notes

For the latest release notes, including known issues, deprecations, and breaking changes, refer to [Elastic OTel Python release notes](/release-notes/index.md)