import pytest
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric, HallucinationMetric

# Note: We don't opt out of telemetry like below because we override the otel
# config to send to our own collector.
# os.environ["DEEPEVAL_TELEMETRY_OPT_OUT"] = "YES"


@pytest.mark.parametrize(
    "module_name, context",
    [
        ("chat", ["Atlantic Ocean"]),
        ("embeddings", ["Connectors can help you connect to a database"]),
    ],
    ids=["chat", "embeddings"],
)
def test_evals(capsys, module_name, context):
    module = __import__(module_name)
    module.main()
    actual_output = capsys.readouterr().out.strip()

    test_case = LLMTestCase(
        input=module.INPUT,
        actual_output=actual_output,
        context=context,
    )

    metrics = [
        AnswerRelevancyMetric(threshold=0.7),
        HallucinationMetric(threshold=0.8),
    ]
    for metric in metrics:
        metric.measure(test_case, False)

        if not metric.success:
            pytest.fail(f"{type(metric).__name__} scored the following output {metric.score:.1f}: {actual_output}")
