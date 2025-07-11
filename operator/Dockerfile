ARG PYTHON_GLIBC_IMAGE="docker.elastic.co/wolfi/python"
ARG PYTHON_GLIBC_IMAGE_VERSION="3.13.5-r2-dev@sha256:d52394fa7cadadae5336e537e70425b05a2d53850f5c27a44f899f9b49ec78e3"

ARG IMAGE="docker.elastic.co/wolfi/chainguard-base"
ARG IMAGE_VERSION="latest@sha256:bbc60f1a2dbdd8e6ae4fee4fdf83adbac275b9821b2ac05ca72b1d597babd51f"

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

RUN apk add gcc g++ python3-dev musl-dev linux-headers

RUN pip install --no-cache-dir --target workspace /opt/distro/*.whl -r requirements.txt

FROM ${IMAGE}:${IMAGE_VERSION}

COPY --from=build /operator-build/workspace /autoinstrumentation
COPY --from=build-musl /operator-build/workspace /autoinstrumentation-musl

RUN chmod -R go+r /autoinstrumentation
RUN chmod -R go+r /autoinstrumentation-musl
