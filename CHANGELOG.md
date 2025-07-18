# Elastic Distribution of OpenTelemetry Python Changelog

## v1.4.0

- Introduce OpAMP agent for Central configuration. Central configuration will be available in Elastic Stack 9.1 (#320)

## v1.3.0

- Bump to OTel 1.34.1: dropped support for Python 3.8 (#321)

  Upstream changes:
  * https://github.com/open-telemetry/opentelemetry-python/discussions/4613
  * https://github.com/open-telemetry/opentelemetry-python-contrib/discussions/3558

## v1.2.0

- Bump to OTel 1.33.1: logs OTLP serialization improvements, stable `code` attributes used in logs (#307)

  Upstream changes:
  * https://github.com/open-telemetry/opentelemetry-python/discussions/4574
  * https://github.com/open-telemetry/opentelemetry-python-contrib/discussions/3487
- Bump openai instrumentation to 1.1.1 in docker image (#308)

## v1.1.0

- Bump to OTel 1.32.1: logging module autoinstrumentation improvements, explicit bucket advisory fixes, asyncclick instrumentation (#293)
- Bump openai instrumentation to 1.1.0 in docker image (#297)

## v1.0.0

- Enable opentelemetry-instrumentation-vertexai in edot-bootstrap (#283)
- Bump openai instrumentation to 1.0.0 in docker image (#275)
- Move docs to https://elastic.github.io/opentelemetry/ (#282)

## v0.8.1

- Bump to OTel 1.31.1 (#270)

## v0.8.0

- Remove some custom code in ElasticOpenTelemetryConfigurator (#250)
- Introduce a resource detector sending server.instance.id (#259)
- Bump to OTel 1.31.0: programmatic auto-instrumentation, added metrics and events for AWS Bedrock instrumentation (#263)
- Bump elastic-opentelemetry-instrumentation-openai to 0.6.1 in Docker image and relax version dependency to (#264)

## v0.7.0

- Bump to OTel 1.30.0: Python 3.13 support, pymssql instrumentation, basic GenAI tracing with AWS Bedrock (#241)

## v0.6.1

- Bump opentelemetry-sdk-extension-aws to 2.1.0 (#222)
- Bump opentelemetry-resourcedetector-gcp to 1.8.0a0 (#229)
- Add OpenAI examples (#226)

## v0.6.0

- Bump to OTel 1.29.0 (#211)
- Bump elastic-opentelemetry-instrumentation-openai dependency to 0.6.0 (#210)

## v0.5.0

- Enable by default cloud resource detectors for AWS, Azure and GCP (#198)
- Introduce edot-bootstrap, like opentelemetry-bootstrap but with EDOT Openai instrumentation (#196)
- Add docs for tracing with manual spans and metrics (#189)
- Set OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE to DELTA (#197)
- Bump elastic-opentelemetry-instrumentation-openai dependency to 0.5.0 (#204)

## v0.4.1

- Bump to OTel 1.28.2 (#185)

## v0.4.0

- Bump to OTel 1.28.1 (#169)
- Enable log events by default (#154)
- Add musl autoinstrumentation to Docker image for OTel Kubernetes operator (#162)
- Add documentation for logging enablement (#153)
- Add flask autoinstrumentation example (#168)

## v0.3.0

- Build Python 3.12 Docker image for OTel Kubernetes operator (#132, #136. #137)
- Make the distro loading more robust against ImportError
  Exception when loading instrumentations (#132)
- Add some types in resource detectors (#133)

## v0.2.0

- Added some documentation (#110)
- Bump to OTel 1.27.0 (#117)
- Enabled `os` resource detector by default (#117)

## v0.1.0

First release.
