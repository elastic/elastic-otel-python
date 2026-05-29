ARG PYTHON_GLIBC_IMAGE="docker.elastic.co/wolfi/python"
ARG PYTHON_GLIBC_IMAGE_VERSION="v3.14.5-r2-dev@sha256:a5fc8731103e53bc8eeb2069785d5bf0f2fe4be2de455f5a4cdc409dc83555e4"

ARG IMAGE="docker.elastic.co/wolfi/chainguard-base"
ARG IMAGE_VERSION="latest@sha256:ec3de092c5f71d1b439965e3234f572eebfc3228f1ace528b1a3bf468f5a33f7"

FROM ${PYTHON_GLIBC_IMAGE}:${PYTHON_GLIBC_IMAGE_VERSION} AS build

ENV LANG=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ARG DISTRO_DIR

COPY ${DISTRO_DIR} /opt/distro

WORKDIR /operator-build

ADD operator/requirements.txt .

RUN mkdir workspace

RUN pip install --no-cache-dir --target workspace /opt/distro/*.whl -r requirements.txt

FROM python:3.12-alpine AS build-musl

ARG DISTRO_DIR

COPY ${DISTRO_DIR} /opt/distro

WORKDIR /operator-build

ADD operator/requirements.txt .

RUN mkdir workspace

RUN pip install --no-cache-dir --target workspace /opt/distro/*.whl -r requirements.txt

FROM ${IMAGE}:${IMAGE_VERSION}

COPY --chown=65532:65532 --from=build /operator-build/workspace /autoinstrumentation
COPY --chown=65532:65532 --from=build-musl /operator-build/workspace /autoinstrumentation-musl

# Use wolfi's "nonroot" user/group to satisfy k8s runAsNonRoot security policies.
USER 65532:65532

RUN chmod -R go+r /autoinstrumentation
RUN chmod -R go+r /autoinstrumentation-musl
