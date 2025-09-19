---
navigation_title: EDOT Python
description: Release notes for Elastic Distribution of OpenTelemetry Python.
applies_to:
  stack:
  serverless:
    observability:
products:
  - id: cloud-serverless
  - id: observability
  - id: edot-sdk
---

# Elastic Distribution of OpenTelemetry Python release notes [edot-python-release-notes]

Review the changes, fixes, and more in each version of Elastic Distribution of OpenTelemetry Python.

To check for security updates, go to [Security announcements for the Elastic stack](https://discuss.elastic.co/c/announcements/security-announcements/31).

% Release notes include only features, enhancements, and fixes. Add breaking changes, deprecations, and known issues to the applicable release notes files.

% ## version.next [edot-python-X.X.X-release-notes]

% ### Features and enhancements [edot-python-X.X.X-features-enhancements]
% *

% ### Fixes [edot-python-X.X.X-fixes]
% *

## 1.8.0 [edot-python-1.8.0-release-notes]

### Features and enhancements [edot-python-1.8.0-features-enhancements]

- Central configuration: make the OpAMP agent more robust against server restarts ([#388](https://github.com/elastic/elastic-otel-python/pull/388))
- Bump OpenTelemetry to 1.37.0/0.58b0 ([#389](https://github.com/elastic/elastic-otel-python/pull/389))

  Upstream changes:
  * [opentelemetry-python](https://github.com/open-telemetry/opentelemetry-python/discussions/4747)
  * [opentelemetry-python-contrib](https://github.com/open-telemetry/opentelemetry-python-contrib/discussions/3750)

### Fixes [edot-python-1.8.0-fixes]

- Central configuration: suppress instrumentations for OpAMP client requests ([#384](https://github.com/elastic/elastic-otel-python/pull/384))

## 1.7.0 [edot-python-1.7.0-release-notes]

### Features and enhancements [edot-python-1.7.0-features-enhancements]

- distro: handle dynamic tracing sampling rate from central config (Tech Preview, requires stack 9.2) ([#367](https://github.com/elastic/elastic-otel-python/pull/367))
- Bump OpenTelemetry to 1.36.0/0.57b0 ([#373](https://github.com/elastic/elastic-otel-python/pull/373))

  Upstream changes:
  * [opentelemetry-python](https://github.com/open-telemetry/opentelemetry-python/discussions/4706)
  * [opentelemetry-python-contrib](https://github.com/open-telemetry/opentelemetry-python-contrib/discussions/3710)

## 1.6.0 [edot-python-1.6.0-release-notes]

### Features and enhancements [edot-python-1.6.0-features-enhancements]

- Prepend our own User agent to the OpenTelemetry SDK one ([#363](https://github.com/elastic/elastic-otel-python/pull/363))

  For the GRPC exported they will look like `elastic-otlp-grpc-python/1.6.0 OTel-OTLP-Exporter-Python/1.35.0 grpc-python/1.74.0 grpc-c/49.0.0 (linux; chttp2)` and for the http exporter like `elastic-otlp-http-python/1.6.0 OTel-OTLP-Exporter-Python/1.35.0`.
- Enable containerid resource detector to set the `container.id` attribute when running under a container using Linux cgroups ([#361](https://github.com/elastic/elastic-otel-python/pull/361))
- Bump to OTel 1.35.0: better handling of exporters timeout ([#360](https://github.com/elastic/elastic-otel-python/pull/360))

  Upstream changes:
  * [opentelemetry-python](https://github.com/open-telemetry/opentelemetry-python/discussions/4682)
  * [opentelemetry-python-contrib](https://github.com/open-telemetry/opentelemetry-python-contrib/discussions/3634)

### Fixes [edot-python-1.6.0-fixes]

- Silence harmless warning about trace sampler rate not set ([#356](https://github.com/elastic/elastic-otel-python/pull/356))

## 1.5.0 [edot-python-1.5.0-release-notes]

### Features and enhancements [edot-python-1.5.0-features-enhancements]

- Switch default Tracing Sampler to `parentbased_traceidratio` ([#351](https://github.com/elastic/elastic-otel-python/pull/351))
- Acknowledge OpAMP remote config status changes ([#340](https://github.com/elastic/elastic-otel-python/pull/340))

## 1.4.0 [edot-python-1.4.0-release-notes]

### Features and enhancements [edot-python-1.4.0-features-enhancements]

* Introduced OpAMP agent for Central configuration in Tech Preview: the first option implemented is changing the logging level of EDOT Python. Central configuration will be available as Tech Preview in Elastic Stack 9.1 ([#320](https://github.com/elastic/elastic-otel-python/pull/320))

## 1.3.0 [edot-python-1.3.0-release-notes]

- Bump to OTel 1.34.1: dropped support for Python 3.8 ([#321](https://github.com/elastic/elastic-otel-python/pull/321))

  Upstream changes:
  * [https://github.com/open-telemetry/opentelemetry-python/discussions/4613](https://github.com/open-telemetry/opentelemetry-python/discussions/4613)
  * [https://github.com/open-telemetry/opentelemetry-python-contrib/discussions/3558](https://github.com/open-telemetry/opentelemetry-python-contrib/discussions/3558)

## 1.2.0 [edot-python-1.2.0-release-notes]

- Bump to OTel 1.33.1: logs OTLP serialization improvements, stable `code` attributes used in logs ([#307](https://github.com/elastic/elastic-otel-python/pull/307))

  Upstream changes:
  * [https://github.com/open-telemetry/opentelemetry-python/discussions/4574](https://github.com/open-telemetry/opentelemetry-python/discussions/4574)
  * [https://github.com/open-telemetry/opentelemetry-python-contrib/discussions/3487](https://github.com/open-telemetry/opentelemetry-python-contrib/discussions/3487)
- Bump openai instrumentation to 1.1.1 in docker image ([#308](https://github.com/elastic/elastic-otel-python/pull/308))

## 1.1.0 [edot-python-1.1.0-release-notes]

- Bump to OTel 1.32.1: logging module autoinstrumentation improvements, explicit bucket advisory fixes, asyncclick instrumentation ([#293](https://github.com/elastic/elastic-otel-python/pull/293))
- Bump openai instrumentation to 1.1.0 in docker image ([#297](https://github.com/elastic/elastic-otel-python/pull/297))

## 1.0.0 [edot-python-1.0.0-release-notes]

- Enable opentelemetry-instrumentation-vertexai in edot-bootstrap ([#283](https://github.com/elastic/elastic-otel-python/pull/283))
- Bump openai instrumentation to 1.0.0 in docker image ([#275](https://github.com/elastic/elastic-otel-python/pull/275))
- Move docs to https://elastic.github.io/opentelemetry/ ([#282](https://github.com/elastic/elastic-otel-python/pull/282))

## 0.8.1 [edot-python-0.8.1-release-notes]

- Bump to OTel 1.31.1 ([#270](https://github.com/elastic/elastic-otel-python/pull/270))

## 0.8.0 [edot-python-0.8.0-release-notes]

- Remove some custom code in ElasticOpenTelemetryConfigurator ([#250](https://github.com/elastic/elastic-otel-python/pull/250))
- Introduce a resource detector sending server.instance.id ([#259](https://github.com/elastic/elastic-otel-python/pull/259))
- Bump to OTel 1.31.0: programmatic auto-instrumentation, added metrics and events for AWS Bedrock instrumentation ([#263](https://github.com/elastic/elastic-otel-python/pull/263))
- Bump elastic-opentelemetry-instrumentation-openai to 0.6.1 in Docker image and relax version dependency to ([#264](https://github.com/elastic/elastic-otel-python/pull/264))

## 0.7.0 [edot-python-0.7.0-release-notes]

- Bump to OTel 1.30.0: Python 3.13 support, pymssql instrumentation, basic GenAI tracing with AWS Bedrock ([#241](https://github.com/elastic/elastic-otel-python/pull/241))

## 0.6.1 [edot-python-0.6.1-release-notes]

- Bump opentelemetry-sdk-extension-aws to 2.1.0 ([#222](https://github.com/elastic/elastic-otel-python/pull/222))
- Bump opentelemetry-resourcedetector-gcp to 1.8.0a0 ([#229](https://github.com/elastic/elastic-otel-python/pull/229))
- Add OpenAI examples ([#226](https://github.com/elastic/elastic-otel-python/pull/226))

## 0.6.0 [edot-python-0.6.0-release-notes]

- Bump to OTel 1.29.0 ([#211](https://github.com/elastic/elastic-otel-python/pull/211))
- Bump elastic-opentelemetry-instrumentation-openai dependency to 0.6.0 ([#210](https://github.com/elastic/elastic-otel-python/pull/210))

## 0.5.0 [edot-python-0.5.0-release-notes]

- Enable by default cloud resource detectors for AWS, Azure and GCP ([#198](https://github.com/elastic/elastic-otel-python/pull/198))
- Introduce edot-bootstrap, like opentelemetry-bootstrap but with EDOT Openai instrumentation ([#196](https://github.com/elastic/elastic-otel-python/pull/196))
- Add docs for tracing with manual spans and metrics ([#189](https://github.com/elastic/elastic-otel-python/pull/189))
- Set OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE to DELTA ([#197](https://github.com/elastic/elastic-otel-python/pull/197))
- Bump elastic-opentelemetry-instrumentation-openai dependency to 0.5.0 ([#204](https://github.com/elastic/elastic-otel-python/pull/204))

## 0.4.1 [edot-python-0.4.1-release-notes]

- Bump to OTel 1.28.2 ([#185](https://github.com/elastic/elastic-otel-python/pull/185))

## 0.4.0 [edot-python-0.4.0-release-notes]

- Bump to OTel 1.28.1 ([#169](https://github.com/elastic/elastic-otel-python/pull/169))
- Enable log events by default ([#154](https://github.com/elastic/elastic-otel-python/pull/154))
- Add musl autoinstrumentation to Docker image for OTel Kubernetes operator ([#162](https://github.com/elastic/elastic-otel-python/pull/162))
- Add documentation for logging enablement ([#153](https://github.com/elastic/elastic-otel-python/pull/153))
- Add flask autoinstrumentation example ([#168](https://github.com/elastic/elastic-otel-python/pull/168))

## 0.3.0 [edot-python-0.3.0-release-notes]

- Build Python 3.12 Docker image for OTel Kubernetes operator ([#132](https://github.com/elastic/elastic-otel-python/pull/132), [#136](https://github.com/elastic/elastic-otel-python/pull/136), [#137](https://github.com/elastic/elastic-otel-python/pull/137))
- Make the distro loading more robust against ImportError
  Exception when loading instrumentations ([#132](https://github.com/elastic/elastic-otel-python/pull/132))
- Add some types in resource detectors ([#133](https://github.com/elastic/elastic-otel-python/pull/133))

## 0.2.0 [edot-python-0.2.0-release-notes]

- Added some documentation ([#110](https://github.com/elastic/elastic-otel-python/pull/110))
- Bump to OTel 1.27.0 ([#117](https://github.com/elastic/elastic-otel-python/pull/117))
- Enabled `os` resource detector by default ([#117](https://github.com/elastic/elastic-otel-python/pull/117))

## 0.1.0 [edot-python-0.1.0-release-notes]

First release.
