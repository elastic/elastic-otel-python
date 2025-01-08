# OpenAI Zero-Code Instrumentation Examples

This is an example of how to instrument OpenAI calls with zero code changes,
using `opentelemetry-instrument` included in the Elastic Distribution of
OpenTelemetry Python ([EDOT Python][edot-python]).

When OpenAI examples run, they export traces, metrics and logs to an OTLP
compatible endpoint. Traces and metrics include details such as the model used
and the duration of the LLM request. In the case of chat, Logs capture the
request and the generated response. The combination of these provide a
comprehensive view of the performance and behavior of your OpenAI usage.

## Install

First, set up a Python virtual environment like this:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Next, install [EDOT Python][edot-python] and dotenv which is a portable way to
load environment variables.
```bash
pip install "python-dotenv[cli]" elastic-opentelemetry
```

Finally, run `edot-bootstrap` which analyzes the code to add relevant
instrumentation, to record traces, metrics and logs.
```bash
edot-bootstrap --action=install
```

## Configure

Copy [env.example](env.example) to `.env` and update its `OPENAI_API_KEY`.

An OTLP compatible endpoint should be listening for traces, metrics and logs on
`http://localhost:4317`. If not, update `OTEL_EXPORTER_OTLP_ENDPOINT` as well.

For example, if Elastic APM server is running locally, edit `.env` like this:
```
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:8200
```

## Run

There are two examples, and they run the same way:

### Chat

[chat.py](chat.py) asks the LLM a geography question and prints the response.

Run it like this:
```bash
dotenv run -- opentelemetry-instrument python chat.py
```

You should see something like "Atlantic Ocean" unless your LLM hallucinates!

### Embeddings


[embeddings.py](embeddings.py) creates in-memory VectorDB embeddings about
Elastic products. Then, it searches for one similar to a question.

Run it like this:
```bash
dotenv run -- opentelemetry-instrument python embeddings.py
```

You should see something like "Connectors can help you connect to a database",
unless your LLM hallucinates!

---

[edot-python]: https://github.com/elastic/elastic-otel-python/blob/main/docs/get-started.md
