FROM docker.elastic.co/wolfi/python:3.13.0-r0-dev@sha256:7df1e5268d3016f23265bfae4863880c5246109799ce614804b214b448145127 AS build

ENV LANG=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ARG DISTRO_DIR

COPY ${DISTRO_DIR} /opt/distro

WORKDIR /operator-build

ADD operator/requirements.txt .

RUN mkdir workspace

RUN pip install --no-cache-dir --target workspace /opt/distro/*.whl -r requirements.txt

FROM docker.elastic.co/wolfi/chainguard-base:latest@sha256:5bc7518045103e085b07842c4362ca5366e117abfdcd3010030f1c072a5607ac

COPY --from=build /operator-build/workspace /autoinstrumentation

RUN chmod -R go+r /autoinstrumentation
