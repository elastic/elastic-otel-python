FROM docker.elastic.co/wolfi/python:3.13.0-r0-dev@sha256:9ba9f49f42208f570058ec1b7faf0c58de7c5a6794416b9b4b7711a381de139d AS build

ENV LANG=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ARG DISTRO_DIR

COPY ${DISTRO_DIR} /opt/distro

WORKDIR /operator-build

ADD operator/requirements.txt .

RUN mkdir workspace

RUN pip install --no-cache-dir --target workspace /opt/distro/*.whl -r requirements.txt

FROM docker.elastic.co/wolfi/chainguard-base:latest@sha256:bf163e1977002301f7b9fd28fe6837a8cb2dd5c83e4cd45fb67fb28d15d5d40f

COPY --from=build /operator-build/workspace /autoinstrumentation

RUN chmod -R go+r /autoinstrumentation
