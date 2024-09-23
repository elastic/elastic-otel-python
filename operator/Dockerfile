FROM docker.elastic.co/wolfi/python:3.12-dev AS build

ENV LANG=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ARG DISTRO_DIR

COPY ${DISTRO_DIR} /opt/distro

WORKDIR /operator-build

ADD operator/requirements.txt .

RUN mkdir workspace

RUN pip install --no-cache-dir --target workspace /opt/distro/*.whl -r requirements.txt

FROM docker.elastic.co/wolfi/chainguard-base:latest@sha256:6fbf07849a440c8dca9aa7e9cb56ed3ecaa9eb40f8a4f36b39393d7b32d78ecc

COPY --from=build /operator-build/workspace /autoinstrumentation

RUN chmod -R go+r /autoinstrumentation
