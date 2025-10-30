FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip install fastapi uvicorn elastic-opentelemetry

# Install all the instrumentations available for the installed packages
RUN edot-bootstrap -a install

EXPOSE 5000

# Set some resource attributes to make our service recognizable
ENV OTEL_RESOURCE_ATTRIBUTES="service.name=FastAPIService,service.version=0.0.1,deployment.environment=development"

CMD ["opentelemetry-instrument", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
