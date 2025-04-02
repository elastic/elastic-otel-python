# Elastic Distribution of OpenTelemetry Python

The Elastic Distribution of OpenTelemetry Python (EDOT Python) is a customized version of [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python).
EDOT Python makes it easier to get started using OpenTelemetry in your Python applications through strictly OpenTelemetry native means, while also providing a smooth and rich out of the box experience with [Elastic Observability](https://www.elastic.co/observability). It's an explicit goal of this distribution to introduce **no new concepts** in addition to those defined by the wider OpenTelemetry community.

With EDOT Python you have access to all the features of the OpenTelemetry Python agent plus:

* Access to improvements and bug fixes contributed by the Elastic team _before_ the changes are available upstream in OpenTelemetry repositories.
* Access to optional features that can enhance OpenTelemetry data that is being sent to Elastic.
* Elastic-specific processors that ensure optimal compatibility when exporting OpenTelemetry signal data to an Elastic backend like an Elastic Observability deployment.
* Preconfigured collection of tracing and metrics signals, applying some opinionated defaults, such as which sources are collected by default.

**Ready to try out EDOT Python?** Follow the step-by-step instructions in [Setting up EDOT Python](https://elastic.github.io/opentelemetry/edot-sdks/python/setup/index.html).

## Configuration

The distribution supports all the configuration variables from OpenTelemetry Python project version 1.31.1.

See [Configuration](https://elastic.github.io/opentelemetry/edot-sdks/python/configuration.html) for more details.

## License

This software is licensed under the Apache License, version 2 ("Apache-2.0").
