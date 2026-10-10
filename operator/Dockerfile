ARG PYTHON_GLIBC_IMAGE="docker.elastic.co/wolfi/python"
ARG PYTHON_GLIBC_IMAGE_VERSION="v3.14.8-dev@sha256:9c4f141a4a9fd67ef9f66c3d78bec63a5cf07d3f85f04dec48ff7198c843994a"

ARG IMAGE="docker.elastic.co/wolfi/chainguard-base"
ARG IMAGE_VERSION="latest@sha256:ac3e46f28be65489e286f4af9244790b9c56e6acfa686a14c77ab365b4796b6b"

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
