<!--
Goal of this doc:
The user is able to understand the differences between the APM Python agent and EDOT
-->

# Compare EDOT Python and the Elastic APM Python agent 

This guide will highlight the major differences between the [Elastic APM Python agent](https://www.elastic.co/guide/en/apm/agent/python/current/getting-started.html) and the Elastic Distribution of OpenTelemetry Python (EDOT Python).
For step-by-step instructions on setting up EDOT Python refer to the [Get started guide](./get-started.md).

## We are a distribution

As a distribution of OpenTelemetry, EDOT Python follows certain standards, but there is still some space for innovation.

## Bold on autoinstrumentation

We have chosen to make autoinstrumentation as simple as possible so you can just focus on your code; we favored an experience that requires minimal changes to your application code. The upstream OpenTelemetry configuration has more options than the distribution requires.

## Bring your own instrumentation

In EDOT Python we decided to not ship all the available instrumentations in order to accommodate environments where installing more packages than requested may be an issue.
We provide a tool to discover available instrumentations automatically that can be added to your build workflow. See [Get started](https://github.com/elastic/elastic-otel-python/blob/main/docs/get-started.md#install-the-available-instrumentation).

## Limitations

### Central configuration

Currently EDOT Python does not have an equivalent of the [central configuration feature](https://www.elastic.co/guide/en/observability/current/apm-agent-configuration.html) that the Elastic APM Python agent supports. When using EDOT Python, all the configurations are static and should be provided to the application with other configurations.

### AWS lambda

At the moment, we are not building a custom lambda layer for our Python distribution. You can refer to the upstream [Lambda Auto-Instrumentation](https://opentelemetry.io/docs/faas/lambda-auto-instrument/).

### Missing instrumentations

Not all instrumentations we have in Elastic APM Python Agent have an OpenTelemetry counterpart. But we may port them if they are requested by users.

At the moment of writing these docs, the following libraries are missing an OpenTelemetry instrumentation:
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
