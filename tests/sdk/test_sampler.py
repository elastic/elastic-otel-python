# Copyright Elasticsearch B.V. and/or licensed to Elasticsearch B.V. under one
# or more contributor license agreements. See the NOTICE file distributed with
# this work for additional information regarding copyright
# ownership. Elasticsearch B.V. licenses this file to you under
# the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from unittest import TestCase, mock

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.sampling import Decision, SamplingResult
from opentelemetry.trace import TraceState

from elasticotel.sdk.sampler import DefaultSampler


class TestDefaultSampler(TestCase):
    def test_keeps_start_attributes(self):
        tracer = TracerProvider(sampler=DefaultSampler("1.0")).get_tracer("test")

        with tracer.start_as_current_span("span", attributes={"http.method": "GET", "http.target": "/"}) as span:
            self.assertEqual(dict(span.attributes), {"http.method": "GET", "http.target": "/"})

    def test_without_start_attributes(self):
        tracer = TracerProvider(sampler=DefaultSampler("1.0")).get_tracer("test")

        with tracer.start_as_current_span("span") as span:
            self.assertEqual(dict(span.attributes), {})

    def test_not_sampled(self):
        tracer = TracerProvider(sampler=DefaultSampler("0")).get_tracer("test")

        with tracer.start_as_current_span("span", attributes={"http.method": "GET"}) as span:
            self.assertFalse(span.is_recording())

    def test_sampler_attributes_take_precedence(self):
        sampler = DefaultSampler("1.0")
        trace_state = TraceState([("ot", "th:0")])
        sampler._delegate = mock.Mock()
        sampler._delegate.should_sample.return_value = SamplingResult(
            Decision.RECORD_AND_SAMPLE, {"sampler": "value", "both": "sampler"}, trace_state
        )

        result = sampler.should_sample(None, 1, "span", attributes={"start": "value", "both": "start"})

        self.assertEqual(result.decision, Decision.RECORD_AND_SAMPLE)
        self.assertEqual(dict(result.attributes), {"start": "value", "sampler": "value", "both": "sampler"})
        self.assertIs(result.trace_state, trace_state)

    def test_set_ratio_keeps_start_attributes(self):
        sampler = DefaultSampler("0")
        sampler.set_ratio(1.0)
        tracer = TracerProvider(sampler=sampler).get_tracer("test")

        with tracer.start_as_current_span("span", attributes={"http.method": "GET"}) as span:
            self.assertEqual(dict(span.attributes), {"http.method": "GET"})
