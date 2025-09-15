---
navigation_title: EDOT Python
description: The Elastic Distribution of OpenTelemetry Python (EDOT Python) is a customized version of OpenTelemetry Python.
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

# Elastic Distribution of OpenTelemetry Python

The [{{edot}} (EDOT) Python](https://github.com/elastic/elastic-otel-python) is a customized version of [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python), configured for the best experience with Elastic Observability. 

Use EDOT Python to start the OpenTelemetry SDK with your Python application, and automatically capture tracing data, performance metrics, and logs. Traces, metrics, and logs can be sent to any OpenTelemetry Protocol (OTLP) Collector you choose.

A goal of this distribution is to avoid introducing proprietary concepts in addition to those defined by the wider OpenTelemetry community. For any additional features introduced, Elastic aims at contributing them back to the OpenTelemetry project.

## Features

In addition to all the features of the OpenTelemetry Python agent, with EDOT Python you have access to the following:

* Improvements and bug fixes contributed by the Elastic team before the changes are available in OpenTelemetry repositories.
* Optional features that can enhance OpenTelemetry data that is being sent to Elastic.
* Elastic-specific processors that ensure optimal compatibility when exporting OpenTelemetry signal data to an Elastic backend like an Elastic Observability deployment.
* Preconfigured collection of tracing and metrics signals, applying some opinionated defaults, such as which sources are collected by default.
* Compatibility with APM Agent Central Configuration to modify the settings of the EDOT Python agent without having to restart the application.

Follow the step-by-step instructions in [Setup](/reference/setup/index.md) to get started.

## Release notes

For the latest release notes, including known issues, deprecations, and breaking changes, refer to [EDOT Python release notes](/release-notes/index.md)