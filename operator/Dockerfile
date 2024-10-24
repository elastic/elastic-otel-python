FROM docker.elastic.co/wolfi/python:3.13.0-r0-dev@sha256:76e4af091bdd7f1d2d10b44e9b75a856ad5a608dbafddc21dba66705f6b2e71b AS build

ENV LANG=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ARG DISTRO_DIR

COPY ${DISTRO_DIR} /opt/distro

WORKDIR /operator-build

ADD operator/requirements.txt .

RUN mkdir workspace

RUN pip install --no-cache-dir --target workspace /opt/distro/*.whl -r requirements.txt

FROM docker.elastic.co/wolfi/chainguard-base:latest@sha256:973431347ad45f40e01afbbd010bf9de929c088a63382239b90dd84f39618bc8

COPY --from=build /operator-build/workspace /autoinstrumentation

RUN chmod -R go+r /autoinstrumentation
