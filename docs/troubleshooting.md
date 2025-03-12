<!--
Goal of this doc:
The user is able to overcome on their own some basic issues
-->

# Troubleshooting

Below are some resources and tips for troubleshooting and debugging the Elastic Distribution of OpenTelemetry Python (EDOT Python).

- [Easy Fixes](#easy-fixes)
- [Disable EDOT](#easy-fixes)

## Easy Fixes

Before you try anything else, go through the following sections to ensure that
EDOT Python is configured correctly. This is not an exhaustive list, but rather
a list of common problems that users run into.

### Debug and development modes

Most frameworks support a debug mode. Generally, this mode is intended for
non-production environments and provides detailed error messages and logging of
potentially sensitive data.

#### Django

Django applications running with the Django `runserver` need to use the `--noreload` parameter in order to be instrumented with `opentelemetry-instrument`.
Remember that you also need to set the `DJANGO_SETTINGS_MODULE` environment variable pointing to the application settings module.

#### FastAPI

FastAPI application started with `fastapi dev` requires the reloader to be disabled with `--no-reload` in order to be instrumented with `opentelemetry-instrument`.

#### Flask

Flask applications running in debug mode will require to disable the reloader in order to being traced, see [OpenTelemetry zero code documentation](https://opentelemetry.io/docs/zero-code/python/example/#instrumentation-while-debugging).

## Disable EDOT

In the unlikely event EDOT Python causes disruptions to a production application, you can disable it while you troubleshoot.

To disable the underlying OpenTelemetry SDK you set the following environment variable `OTEL_SDK_DISABLED=true`.

If only a subset of instrumentation are causing disruptions you can disable them with the `OTEL_PYTHON_DISABLED_INSTRUMENTATIONS`
environment variable. It accepts a list of comma separated instrumentations to disable, see [OpenTelemetry zero code documentation](https://opentelemetry.io/docs/zero-code/python/configuration/#disabling-specific-instrumentations)
