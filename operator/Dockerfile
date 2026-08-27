ARG PYTHON_GLIBC_IMAGE="docker.elastic.co/wolfi/python"
ARG PYTHON_GLIBC_IMAGE_VERSION="v3.12.14-r3-dev@sha256:2036987d7e2509a18740ea2182bacbcee483105923dabf3dd1650704f6aa6adc"

ARG IMAGE="docker.elastic.co/wolfi/chainguard-base"
ARG IMAGE_VERSION="latest@sha256:e8b23e9bccb0559f1a5cc3ee7c1e7ba3cd44eab5738897b43d7145f4cea5ce76"

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
