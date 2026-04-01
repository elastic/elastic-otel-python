# Docker images for Kubernetes OpenTelemetry Operator

In this directory there are two *Dockerfile*s:
- `Dockerfile`, that build the published image, based on Wolfi a glibc based image
- `Dockerfile.alpine`, that can be used for building a testing musl based image

These `Dockerfile`s are used to build our docker images and they will install a locally built `elastic-opentelemetry` package.

## Local build

From the root of this repository you can build and make available the image locally with:

```bash
docker buildx build -f operator/Dockerfile --build-arg DISTRO_DIR=./dist -t elastic-otel-python-operator:test-wolfi --load .
```
