ARG PYTHON_GLIBC_IMAGE="docker.elastic.co/wolfi/python"
ARG PYTHON_GLIBC_IMAGE_VERSION="3.13.7-r2-dev@sha256:0f3c2935a7fff5b53cf7936d498547d34446b5f37a1a9caeb074b49acabca034"

ARG IMAGE="docker.elastic.co/wolfi/chainguard-base"
ARG IMAGE_VERSION="latest@sha256:ec172778d432abfcd18641ec25270b2fff7c22ff9956d44c495860cdb0477357"

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
