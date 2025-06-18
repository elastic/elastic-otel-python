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

## 1.3.0 [edot-python-1.3.0-release-notes]

- Bump to OTel 1.34.1: dropped support for Python 3.8 (#321)

  Upstream changes:
  * https://github.com/open-telemetry/opentelemetry-python/discussions/4613
  * https://github.com/open-telemetry/opentelemetry-python-contrib/discussions/3558

## 1.2.0 [edot-python-1.2.0-release-notes]

- Bump to OTel 1.33.1: logs OTLP serialization improvements, stable `code` attributes used in logs (#307).

  Upstream changes:
  * https://github.com/open-telemetry/opentelemetry-python/discussions/4574
  * https://github.com/open-telemetry/opentelemetry-python-contrib/discussions/3487
- Bump openai instrumentation to 1.1.1 in docker image (#308).

## 1.1.0 [edot-python-1.1.0-release-notes]

- Bump to OTel 1.32.1: logging module autoinstrumentation improvements, explicit bucket advisory fixes, asyncclick instrumentation (#293).
- Bump openai instrumentation to 1.1.0 in docker image (#297).

## 1.0.0 [edot-python-1.0.0-release-notes]

- Enabled opentelemetry-instrumentation-vertexai in edot-bootstrap (#283).
- Bump openai instrumentation to 1.0.0 in docker image (#275).
- Moved docs to https://elastic.github.io/opentelemetry/ (#282).

## 0.8.1 [edot-python-0.8.1-release-notes]

- Bump to OTel 1.31.1 (#270).

## 0.8.0 [edot-python-0.8.0-release-notes]

- Removed some custom code in ElasticOpenTelemetryConfigurator (#250).
- Introduced a resource detector sending server.instance.id (#259).
- Bump to OTel 1.31.0: programmatic auto-instrumentation, added metrics and events for AWS Bedrock instrumentation (#263).
- Bump elastic-opentelemetry-instrumentation-openai to 0.6.1 in Docker image and relax version dependency to (#264).

## 0.7.0 [edot-python-0.7.0-release-notes]

- Bump to OTel 1.30.0: Python 3.13 support, pymssql instrumentation, basic GenAI tracing with AWS Bedrock (#241).

## 0.6.1 [edot-python-0.6.1-release-notes]

- Bump opentelemetry-sdk-extension-aws to 2.1.0 (#222).
- Bump opentelemetry-resourcedetector-gcp to 1.8.0a0 (#229).
- Added OpenAI examples (#226).

## 0.6.0 [edot-python-0.6.0-release-notes]

- Bump to OTel 1.29.0 (#211).
- Bump elastic-opentelemetry-instrumentation-openai dependency to 0.6.0 (#210).

## 0.5.0 [edot-python-0.5.0-release-notes]

- Enabled by default cloud resource detectors for AWS, Azure and GCP (#198).
- Introduced edot-bootstrap, like opentelemetry-bootstrap but with EDOT Openai instrumentation (#196).
- Added docs for tracing with manual spans and metrics (#189).
- Set OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE to DELTA (#197).
- Bump elastic-opentelemetry-instrumentation-openai dependency to 0.5.0 (#204).

## 0.4.1 [edot-python-0.4.1-release-notes]

- Bump to OTel 1.28.2 (#185).

## 0.4.0 [edot-python-0.4.0-release-notes]

- Bump to OTel 1.28.1 (#169).
- Enabled log events by default (#154).
- Added musl autoinstrumentation to Docker image for OTel Kubernetes operator (#162).
- Added documentation for logging enablement (#153).
- Added flask autoinstrumentation example (#168).

## 0.3.0 [edot-python-0.3.0-release-notes]

- Built Python 3.12 Docker image for OTel Kubernetes operator (#132, #136. #137).
- Made the distro loading more robust against ImportError.Exception when loading instrumentations (#132).
- Added some types in resource detectors (#133).

## 0.2.0 [edot-python-0.2.0-release-notes]

- Added some documentation (#110).
- Bump to OTel 1.27.0 (#117).
- Enabled `os` resource detector by default (#117).

## 0.1.0 [edot-python-0.1.0-release-notes]

First release.
