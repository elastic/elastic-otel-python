FROM python:3.13-slim

WORKDIR /app

COPY . /app

RUN pip install aiohttp elastic-opentelemetry

# Install all the instrumentations available for the installed packages
RUN edot-bootstrap -a install

EXPOSE 8080

# Set some resource attributes to make our service recognizable
ENV OTEL_RESOURCE_ATTRIBUTES="service.name=AioHttpService,service.version=0.0.1,deployment.environment=development"

CMD ["opentelemetry-instrument", "python", "app.py"]
