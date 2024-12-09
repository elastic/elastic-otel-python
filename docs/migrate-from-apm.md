<!--
Goal of this doc:
The user is able to understand the differences between the APM Python agent and EDOT
-->

# Get started

This guide will highlight the major differences between APM Python Agent and the Elastic Distribution of OpenTelemetry Python (EDOT Python).
For an hands-on approach on setting up EDOT Python refer to the [Get started guide](./get-started.md).

## We are a distribution

EDOT Python being a distribution of OpenTelemetry means we should follow standards and can't always drift from that. That does not mean there isn't still space for innovation.

## Bold on autoinstrumentation

We have choosen to be bold on autoinstrumentation - that is instrument your Python application without change the application code - so you can just focus on your code. This is because OpenTelemetry configuration has more options and configuration knobs that may complicate things.

## Bring your own instrumentation

In EDOT Python we decided to not ship all the available instrumentations in order to accomodate environments where installing more packages than requested may be an issue.
We provide a tool to discover available instrumentations automatically that can be added to your build workflow. See [Get started](https://github.com/elastic/elastic-otel-python/blob/main/docs/get-started.md#install-the-available-instrumentation).

## Limitations

### Central configuration

At the moment we don't have a Central configuration replacement so all the configurations would be static and should be provided to the application with other manners.

### AWS lambda

At the moment we are not building any custom lambda layer for the Python instrumentation. You can refer to the upstream [Lambda Auto-Instrumentation](https://opentelemetry.io/docs/faas/lambda-auto-instrument/).

### Missing instrumentations

Not all instrumentation we have in APM Python Agent have an OpenTelemetry counterpart, we may port them if there is customer request.

At the moment of writing the following libraries are missing an OpenTelemetry instrumentation:
- aiobotocore
- aiomysql
- aiopg
- aioredis
- Azure storage and Azure queue
- Graphene
- httplib2
- pylibmc
- pyodbc
- pymssql
- Sanic
- zlib

<!-- ✅ What they should do next -->
## Next steps

* [Get started](./get-started.md) with EDOT Python.
* Learn how to add [manual instrumentation](./manual-instrumentation.md).
* Learn more about viewing and interpreting data in the [Observability guide](https://www.elastic.co/guide/en/observability/current/apm.html).
