<!--
Goal of this doc:
The user is able to manually instrument their Python application
-->

# Manual instrumentation

This guide shows you how to use the Elastic Distribution of OpenTelemetry Python (EDOT Python) to manually instrument your Python application and send OpenTelemetry data to an Elastic Observability deployment.

**Already familiar with OpenTelemetry?** It's an explicit goal of this distribution to introduce _no new concepts_ outside those defined by the wider OpenTelemetry community.

**New to OpenTelemetry?** If your are new to OpenTelemetry we encourage you to take a look at our [get started documentation](./get-started.md) instead that will introduce you to autoinstrumentation.

**Already added autoinstrumentation with OpenTelemetry to your application?** Skip to the [Manually instrument your Python application chapter](#Manually-instrument-your-Python-application).

<!-- ✅ What the user needs to know and/or do before they install EDOT Python -->
## Prerequisites

Before getting started, you'll need somewhere to send the gathered OpenTelemetry data, so it can be viewed and analyzed. EDOT Python supports sending data to any OpenTelemetry protocol (OTLP) endpoint, but this guide assumes you are sending data to an [Elastic Observability](https://www.elastic.co/observability) cloud deployment. You can use an existing one or set up a new one.

<details>
<summary><strong>Expand for setup instructions</strong></summary>

To create your first Elastic Observability deployment:

1. Sign up for a [free Elastic Cloud trial](https://cloud.elastic.co/registration) or sign into an existing account.
1. Go to <https://cloud.elastic.co/home>.
1. Click **Create deployment**.
1. When the deployment is ready, click **Open** to visit your Kibana home page (for example, `https://{DEPLOYMENT_NAME}.kb.{REGION}.cloud.es.io/app/home#/getting_started`).
</details>

<!-- ✅ How to install EDOT Python -->
## Install

### Install the distribution

Install EDOT Python:

```bash
pip install elastic-opentelemetry
```

### Install the available instrumentation

EDOT Python does not install any instrumentation package by default, instead it relies on the
`opentelemetry-bootstrap` command to scan the installed packages and install the available instrumentation.
The following command will install all the instrumentations available for libraries found installed
in your environment:

```bash
opentelemetry-bootstrap --action=install
```

> [!NOTE]
> Add this command every time you deploy an updated version of your application (in other words, add it to your container image build process).

<!-- ✅ Start-to-finish operation -->
## Send data to Elastic

After installing EDOT Python, configure and initialize it to start sending data to Elastic.

<!-- ✅ Provide _minimal_ configuration/setup -->
### Configure EDOT Python

To configure EDOT Python, at a minimum you'll need your Elastic Observability cloud deployment's OTLP endpoint and
authorization data to set a few `OTLP_*` environment variables that will be available when running EDOT Python:

* `OTEL_RESOURCE_ATTRIBUTES`: Use this to add a service name that will make it easier to recognize your application when reviewing data sent to Elastic.
* `OTEL_EXPORTER_OTLP_ENDPOINT`: The full URL of the endpoint where data will be sent.
* `OTEL_EXPORTER_OTLP_HEADERS`: A comma-separated list of `key=value` pairs that will
be added to the headers of every request. This is typically used for authentication information.

You can find the values of the endpoint and header variables in Kibana's APM tutorial. In Kibana:

1. Go to **Setup guides**.
1. Select **Observability**.
1. Select **Monitor my application performance**.
1. Scroll down and select the **OpenTelemetry** option.
1. The appropriate values for `OTEL_EXPORTER_OTLP_ENDPOINT` and `OTEL_EXPORTER_OTLP_HEADERS` are shown there.

Here's an example:

```sh
export OTEL_RESOURCE_ATTRIBUTES=service.name=<app-name>
export OTEL_EXPORTER_OTLP_ENDPOINT=https://my-deployment.apm.us-west1.gcp.cloud.es.io
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Bearer P....l"
```

> [!NOTE]
> Alternatively, you can use an [APM agent key](https://www.elastic.co/guide/en/observability/current/apm-api-key.html) to authorize requests to an Elastic Observability endpoint. APM agent keys are revocable, you can have more than one of them, and you can add or remove them without restarting APM Server.
>
> To create and manage APM Agent keys in Kibana:
>
> 1. Go to **APM Settings**.
> 1. Select the **Agent Keys** tab.
>
> When using an APM Agent key, the `OTEL_EXPORTER_OTLP_HEADERS` is set using different auth schema (`ApiKey` rather than `Bearer`). For example:
> ```sh
> export OTEL_EXPORTER_OTLP_HEADERS="Authorization=ApiKey TkpXUkx...dVZGQQ=="
> ```

<!-- ✅ Manually instrument the application and start sending data to Elastic -->
### Manually instrument your Python application

FIXME 

<!--  ✅ What success looks like -->
## Confirm that EDOT Python is working

To confirm that EDOT Python has successfully connected to Elastic:

1. Go to **APM** → **Traces**.
1. You should see the name of the service to which you just added EDOT Python. It can take several minutes after initializing EDOT Python for the service to show up in this list.
1. Click on the name in the list to see trace data.

> [!NOTE]
> There may be no trace data to visualize unless you have _used_ your application since initializing EDOT Python.

<!-- ✅ What they should do next -->
## Next steps

* Reference all available [configuration options](./configure.md).
* Learn more about viewing and interpreting data in the [Observability guide](https://www.elastic.co/guide/en/observability/current/apm.html).
