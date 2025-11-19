FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip install flask elastic-opentelemetry

# Install all the instrumentations available for the installed packages
RUN edot-bootstrap -a install

# default flask run port
EXPOSE 5000

# Set some resource attributes to make our service recognizable
ENV OTEL_RESOURCE_ATTRIBUTES="service.name=FlaskService,service.version=0.0.1,deployment.environment.name=development"

CMD ["opentelemetry-instrument", "flask", "run"]
