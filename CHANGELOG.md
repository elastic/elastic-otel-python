# Elastic Distribution of OpenTelemetry Python Changelog

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
