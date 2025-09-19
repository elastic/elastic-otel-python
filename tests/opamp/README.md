# How to record e2e tests

We use [VCR.py](https://vcrpy.readthedocs.io/en/latest/) to automatically record HTTP responses from
an OpAMP server.

We use a build of [opentelemetry-collector-components](https://github.com/elastic/opentelemetry-collector-components/) as
OpAMP server. To build on a linux machine run:

`make genelasticcol`

You then need an Elastic Cloud Deployment setup, an APIKey and the ElasticSearch endpoint URL.


You can use the following configuration:

```
extensions:
  bearertokenauth:
    scheme: "APIKey"
    token: "<api key>"
  apmconfig:
   source:
    elasticsearch:
      endpoint: "<es endpoint>"
      auth:
        authenticator: bearertokenauth
      cache_duration: 10s
   opamp:
     protocols:
       http:
         endpoint: "localhost:4320"

receivers:
  # Receiver for logs, traces, and metrics from SDKs
  otlp/fromsdk:
    protocols:
      grpc:
      http:

  elasticapm:

processors:
  elasticapm:

exporters:
  elasticsearch/otel:
    endpoints: ["<es endpoint>"]
    auth:
      authenticator: bearertokenauth
    mapping:
      mode: otel
    logs_dynamic_index:
      enabled: true
    metrics_dynamic_index:
      enabled: true
    traces_dynamic_index:
      enabled: true

  debug:
    verbosity: detailed

service:
  telemetry:
    logs:
      level: debug
  extensions: [bearertokenauth, apmconfig]
  pipelines:
    traces/fromsdk:
      receivers: [otlp/fromsdk]
      processors: [elasticapm]
      exporters: [elasticsearch/otel, debug]

    metrics/fromsdk:
      receivers: [otlp/fromsdk]
      processors: [elasticapm]
      exporters: [elasticsearch/otel]

    metrics/aggregated-metrics:
      receivers: [elasticapm]
      processors: []
      exporters: [elasticsearch/otel]

    logs/fromsdk:
      receivers: [otlp/fromsdk]
      processors: [elasticapm]
      exporters: [elasticsearch/otel]
```

And you can start a collector instance with:

`./_build/elastic-collector-components --config config.yml`

Now you need to send some OTLP data from a service with `service.name` set (`foo` is currently used in tests) so we can
create an Agent configuration (`/app/apm/settings/agent-configuration/create`) for the very same `Service`.

Once you have the configuration you can write tests using the proper `service.name` as configured in the backend.
