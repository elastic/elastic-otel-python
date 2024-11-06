# Flask autoinstrumented application

This is a barebone Flask app used for demonstrating autoinstrumentation with EDOT.

You can build the application image it with:

```
docker build --load -t edot-flask:latest .
```

You can run the application with:

```
export OTEL_EXPORTER_OTLP_ENDPOINT=https://my-deployment.apm.us-west1.gcp.cloud.es.io
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Bearer P....l"
docker run -e OTEL_EXPORTER_OTLP_ENDPOINT="$OTEL_EXPORTER_OTLP_ENDPOINT" \
  -e OTEL_EXPORTER_OTLP_HEADERS="$OTEL_EXPORTER_OTLP_HEADERS" \
  -p 5000:5000 -it --rm edot-flask:latest
```

You can access the application from [http://127.0.0.1:5000](http://127.0.0.1:5000).
