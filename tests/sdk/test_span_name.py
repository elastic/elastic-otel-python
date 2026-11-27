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

from opentelemetry.sdk.trace import SpanLimits, TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExportResult
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import SpanKind

from elasticotel.sdk.trace.span_name import (
    SpanNameSettings,
    SpanNamingSpanExporter,
    _NameGroup,
    parse_span_name_groups,
)


class TestNameGroup(TestCase):
    def test_matches(self):
        cases = [
            ("GET /users", "GET /users", True),
            ("GET /users", "GET /users/42", False),
            ("GET /users/*", "GET /users/42", True),
            ("GET /users/*", "GET /users/", True),
            ("GET /users/*", "GET /users", False),
            ("GET /users/*/cart", "GET /users/42/cart", True),
            ("GET /users/*/cart", "GET /users/42/7/cart", True),
            ("GET /users/*/cart", "GET /users/42/cart/items", False),
            ("*", "", True),
            ("*", "anything / at all", True),
            ("*/cart", "GET /users/42/cart", True),
            ("GET *", "POST /users", False),
            ("**", "GET", True),
            ("a*b*c", "abc", True),
            ("a*b*c", "aXbYc", True),
            ("a*b*c", "acb", False),
            ("GET /Users/*", "GET /users/42", False),
            # only * is a wildcard
            ("GET /items/?", "GET /items/1", False),
            ("GET /items/?", "GET /items/?", True),
            ("GET /items/[slug]", "GET /items/s", False),
            ("GET /items/[slug]", "GET /items/[slug]", True),
            ("GET /items/(.*)", "GET /items/42", False),
            ("multi\nline*", "multi\nline\nname", True),
        ]
        for pattern, name, expected in cases:
            with self.subTest(pattern=pattern, name=name):
                self.assertEqual(_NameGroup(pattern).matches(name), expected)

    def test_parse_span_name_groups(self):
        self.assertEqual(parse_span_name_groups(""), [])
        self.assertEqual(parse_span_name_groups(" , ,"), [])
        self.assertEqual(
            parse_span_name_groups("GET /users/*/cart, GET /orders/* ,,process *"),
            ["GET /users/*/cart", "GET /orders/*", "process *"],
        )


class TestSpanNamingSpanExporter(TestCase):
    def setUp(self):
        self.memory_exporter = InMemorySpanExporter()
        self.settings = SpanNameSettings()
        self.exporter = SpanNamingSpanExporter(self.memory_exporter, self.settings)
        self.tracer_provider = TracerProvider(span_limits=SpanLimits(max_span_attributes=4))
        self.tracer_provider.add_span_processor(SimpleSpanProcessor(self.exporter))
        self.tracer = self.tracer_provider.get_tracer("test")

    def tearDown(self):
        self.tracer_provider.shutdown()

    def exported_names(self):
        names = [span.name for span in self.memory_exporter.get_finished_spans()]
        self.memory_exporter.clear()
        return names

    def span(self, name, kind=SpanKind.INTERNAL, attributes=None):
        self.tracer.start_span(name, kind=kind, attributes=attributes).end()

    def server_span(self, name, path, method=None):
        if method is None:
            method = "_OTHER" if name == "HTTP" else name
        self.span(name, kind=SpanKind.SERVER, attributes={"http.request.method": method, "url.path": path})

    def old_semconv_server_span(self, name, target, method=None):
        if method is None:
            method = "_OTHER" if name == "HTTP" else name
        self.span(name, kind=SpanKind.SERVER, attributes={"http.method": method, "http.target": target})

    def test_disabled_by_default(self):
        self.server_span("GET", "/users/42/cart")

        self.assertEqual(self.exported_names(), ["GET"])

    def test_disabled_passes_spans_through(self):
        delegate = mock.Mock()
        delegate.export.return_value = SpanExportResult.SUCCESS
        exporter = SpanNamingSpanExporter(delegate, self.settings)
        spans = (mock.Mock(),)

        self.assertEqual(exporter.export(spans), SpanExportResult.SUCCESS)

        delegate.export.assert_called_once()
        self.assertIs(delegate.export.call_args.args[0], spans)

    def test_nothing_renamed_passes_spans_through(self):
        self.settings.set_span_name_groups(["no match"])
        delegate = mock.Mock()
        exporter = SpanNamingSpanExporter(delegate, self.settings)
        spans = [mock.Mock(name="span")]
        spans[0].name = "GET"

        exporter.export(spans)

        self.assertIs(delegate.export.call_args.args[0], spans)

    def test_use_path_as_span_name(self):
        self.settings.set_use_path_as_span_name(True)

        self.server_span("GET", "/users/42/cart")
        self.server_span("HTTP", "/users/42/cart")

        self.assertEqual(self.exported_names(), ["GET /users/42/cart", "HTTP /users/42/cart"])

    def test_use_path_as_span_name_method_original(self):
        self.settings.set_use_path_as_span_name(True)

        self.span(
            "PURGE",
            kind=SpanKind.SERVER,
            attributes={
                "http.request.method": "_OTHER",
                "http.request.method_original": "PURGE",
                "url.path": "/cache",
            },
        )

        self.assertEqual(self.exported_names(), ["PURGE /cache"])

    def test_use_path_as_span_name_old_semconv(self):
        self.settings.set_use_path_as_span_name(True)

        self.old_semconv_server_span("GET", "/users/42/cart?item=1")
        self.old_semconv_server_span("HTTP", "/users/42/cart")
        self.old_semconv_server_span("GET", "/users/42")

        self.assertEqual(self.exported_names(), ["GET /users/42/cart", "HTTP /users/42/cart", "GET /users/42"])

    def test_use_path_as_span_name_dup_semconv(self):
        self.settings.set_use_path_as_span_name(True)

        self.span(
            "GET",
            kind=SpanKind.SERVER,
            attributes={
                "http.request.method": "GET",
                "url.path": "/users/42",
                "http.method": "GET",
                "http.target": "/users/42?item=1",
            },
        )

        self.assertEqual(self.exported_names(), ["GET /users/42"])

    def test_use_path_as_span_name_keeps_route_name(self):
        self.settings.set_use_path_as_span_name(True)

        self.server_span("GET /users/{id}/cart", "/users/42/cart", method="GET")
        self.old_semconv_server_span("GET /users/{id}/cart", "/users/42/cart", method="GET")

        self.assertEqual(self.exported_names(), ["GET /users/{id}/cart", "GET /users/{id}/cart"])

    def test_use_path_as_span_name_without_path(self):
        self.settings.set_use_path_as_span_name(True)

        self.span("GET", kind=SpanKind.SERVER, attributes={"http.request.method": "GET"})
        self.span("GET", kind=SpanKind.SERVER, attributes={"http.request.method": "GET", "url.path": ""})

        self.assertEqual(self.exported_names(), ["GET", "GET"])

    def test_use_path_as_span_name_only_server_spans(self):
        self.settings.set_use_path_as_span_name(True)

        for kind in (SpanKind.CLIENT, SpanKind.INTERNAL, SpanKind.CONSUMER):
            self.span("GET", kind=kind, attributes={"http.request.method": "GET", "url.path": "/users/42/cart"})

        self.assertEqual(self.exported_names(), ["GET", "GET", "GET"])

    def test_span_name_groups(self):
        self.settings.set_use_path_as_span_name(True)
        self.settings.set_span_name_groups(["GET /users/*/cart", "GET /orders/*"])

        self.server_span("GET", "/users/42/cart")
        self.server_span("GET", "/users/73/cart")
        self.server_span("GET", "/orders/1")
        self.server_span("GET", "/users/42")
        self.server_span("POST", "/users/42/cart")

        self.assertEqual(
            self.exported_names(),
            ["GET /users/*/cart", "GET /users/*/cart", "GET /orders/*", "GET /users/42", "POST /users/42/cart"],
        )

    def test_span_name_groups_first_match_wins(self):
        self.settings.set_span_name_groups(["GET /users/*", "GET *"])

        self.span("GET /users/42")
        self.span("GET /orders/1")

        self.assertEqual(self.exported_names(), ["GET /users/*", "GET *"])

    def test_span_name_groups_case_sensitivity(self):
        self.settings.set_use_path_as_span_name(True)
        self.settings.set_span_name_groups(["GET /Users/*"])

        self.server_span("GET", "/Users/42")
        self.server_span("GET", "/users/42")

        self.assertEqual(self.exported_names(), ["GET /Users/*", "GET /users/42"])

    def test_span_name_groups_without_use_path(self):
        self.settings.set_span_name_groups(["GET /users/*", "process orders-*"])

        # WSGI and ASGI instrumentations already name spans with the path when there is no route
        self.span("GET /users/42", kind=SpanKind.SERVER, attributes={"http.method": "GET", "http.target": "/users/42"})
        self.span("process orders-123")
        # path is not used to build the name, so the group does not apply
        self.server_span("GET", "/users/42")

        self.assertEqual(self.exported_names(), ["GET /users/*", "process orders-*", "GET"])

    def test_span_name_groups_all_spans(self):
        self.settings.set_span_name_groups(["child *"])

        with self.tracer.start_as_current_span("child root"):
            self.span("child 1")

        self.assertEqual(self.exported_names(), ["child *", "child *"])

    def test_runtime_updates(self):
        self.settings.set_use_path_as_span_name(True)
        self.settings.set_span_name_groups(["GET /users/*"])

        self.settings.set_use_path_as_span_name(False)
        self.settings.set_span_name_groups(["GET /orders/*"])
        self.server_span("GET", "/users/42")
        self.span("GET /orders/{id}")
        self.assertEqual(self.exported_names(), ["GET", "GET /orders/*"])

        self.settings.set_use_path_as_span_name(True)
        self.settings.set_span_name_groups([])
        self.server_span("GET", "/users/42")
        self.assertEqual(self.exported_names(), ["GET /users/42"])

    def test_renamed_span_keeps_everything_else(self):
        self.settings.set_use_path_as_span_name(True)

        with self.tracer.start_as_current_span(
            "GET",
            kind=SpanKind.SERVER,
            # max_span_attributes is 4, the oldest attribute is dropped
            attributes={"dropped": 0, "http.request.method": "GET", "url.path": "/users/42", "a": 1, "b": 2},
        ) as span:
            span.add_event("event")

        (exported,) = self.memory_exporter.get_finished_spans()
        self.assertEqual(exported.name, "GET /users/42")
        self.assertEqual(exported.context, span.get_span_context())
        self.assertEqual(exported.kind, SpanKind.SERVER)
        self.assertEqual(exported.start_time, span.start_time)
        self.assertEqual(exported.end_time, span.end_time)
        self.assertEqual(exported.instrumentation_scope.name, "test")
        self.assertEqual(len(exported.events), 1)
        self.assertEqual(len(exported.attributes), 4)
        self.assertEqual(exported.dropped_attributes, 1)

    def test_does_not_rename_spans_seen_by_other_processors(self):
        other_exporter = InMemorySpanExporter()
        self.tracer_provider.add_span_processor(SimpleSpanProcessor(other_exporter))
        self.settings.set_span_name_groups(["GET *"])

        self.span("GET /users/42")

        self.assertEqual(self.exported_names(), ["GET *"])
        self.assertEqual([span.name for span in other_exporter.get_finished_spans()], ["GET /users/42"])

    def test_delegates_shutdown_and_force_flush(self):
        delegate = mock.Mock()
        delegate.force_flush.return_value = True
        exporter = SpanNamingSpanExporter(delegate, self.settings)

        self.assertTrue(exporter.force_flush(1000))
        exporter.shutdown()

        delegate.force_flush.assert_called_once_with(1000)
        delegate.shutdown.assert_called_once_with()
