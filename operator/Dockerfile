FROM docker.elastic.co/wolfi/python:3.12.6-r2-dev@sha256:4fe5047eae66c2d69978aff60f22bcc75b66790b43587acde827133d0a2e9dbe AS build

ENV LANG=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ARG DISTRO_DIR

COPY ${DISTRO_DIR} /opt/distro

WORKDIR /operator-build

ADD operator/requirements.txt .

RUN mkdir workspace

RUN pip install --no-cache-dir --target workspace /opt/distro/*.whl -r requirements.txt

FROM docker.elastic.co/wolfi/chainguard-base:latest@sha256:a51a1cd55a717b170058395f65cd16c3ede419b4fd400f0abaae7244c7a421f9

COPY --from=build /operator-build/workspace /autoinstrumentation

RUN chmod -R go+r /autoinstrumentation
