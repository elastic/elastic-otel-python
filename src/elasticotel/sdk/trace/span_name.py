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

"""Renaming of spans at export time.

Supports:
- ``ELASTIC_OTEL_USE_PATH_AS_SPAN_NAME`` / ``use_path_as_span_name``
- ``ELASTIC_OTEL_SPAN_NAME_GROUPS`` / ``span_name_groups``
"""

from __future__ import annotations

import copy
import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, replace

from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from opentelemetry.semconv.attributes.http_attributes import (
    HTTP_REQUEST_METHOD,
    HTTP_REQUEST_METHOD_ORIGINAL,
)
from opentelemetry.semconv.attributes.url_attributes import URL_PATH
from opentelemetry.trace import SpanKind

# Attributes from the old HTTP semantic conventions, which Python instrumentations emit unless
# OTEL_SEMCONV_STABILITY_OPT_IN is set to http or http/dup.
_HTTP_METHOD = "http.method"
_HTTP_TARGET = "http.target"

# The span name used by HTTP server instrumentations when the request method is not a known one.
_UNKNOWN_METHOD_SPAN_NAME = "HTTP"


class _NameGroup:
    """A wildcard pattern where ``*`` matches zero or more characters. Matching is case-sensitive."""

    __slots__ = ("_regex", "name")

    def __init__(self, pattern: str):
        self.name = pattern
        self._regex = re.compile(".*".join(re.escape(segment) for segment in pattern.split("*")), re.DOTALL)

    def matches(self, name: str) -> bool:
        return self._regex.fullmatch(name) is not None


@dataclass(frozen=True)
class _SpanNameConfig:
    use_path: bool = False
    groups: tuple[_NameGroup, ...] = ()


class SpanNameSettings:
    """Holds the current span naming configuration.

    Updates replace an immutable snapshot so that an exporter reading it on another thread always sees a consistent
    pair of values.
    """

    def __init__(self):
        self._config = _SpanNameConfig()

    def set_use_path_as_span_name(self, use_path: bool):
        self._config = replace(self._config, use_path=use_path)

    def set_span_name_groups(self, patterns: Iterable[str]):
        self._config = replace(self._config, groups=tuple(_NameGroup(pattern) for pattern in patterns))

    def _get(self) -> _SpanNameConfig:
        return self._config


span_name_settings = SpanNameSettings()


def parse_span_name_groups(value: str) -> list[str]:
    """Parses a comma-separated list of patterns, dropping empty entries."""
    return [pattern.strip() for pattern in value.split(",") if pattern.strip()]


def _name_with_path(span: ReadableSpan) -> str | None:
    if span.kind != SpanKind.SERVER:
        return None
    attributes = span.attributes or {}
    method = attributes.get(HTTP_REQUEST_METHOD, attributes.get(_HTTP_METHOD))
    path = attributes.get(URL_PATH)
    if path is None:
        target = attributes.get(_HTTP_TARGET)
        if isinstance(target, str):
            path = target.split("?", 1)[0]
    if not isinstance(method, str) or not isinstance(path, str) or not path:
        return None
    # Without a route, HTTP server instrumentations name the span with just the method, with the method as received
    # or with HTTP for unknown methods.
    name = span.name
    if name != method and name != _UNKNOWN_METHOD_SPAN_NAME and name != attributes.get(HTTP_REQUEST_METHOD_ORIGINAL):
        return None
    return f"{name} {path}"


def _span_name(span: ReadableSpan, config: _SpanNameConfig) -> str | None:
    """Returns the new name of the span, or None if it is unchanged."""
    name = span.name
    changed = False
    if config.use_path:
        name_with_path = _name_with_path(span)
        if name_with_path is not None:
            name = name_with_path
            changed = True
    for group in config.groups:
        if group.matches(name):
            name = group.name
            changed = True
            break
    return name if changed else None


def _renamed_span(span: ReadableSpan, name: str) -> ReadableSpan:
    # A shallow copy keeps everything else about the span, including dropped attribute counts, which are lost
    # when constructing a ReadableSpan from its public properties.
    renamed = copy.copy(span)
    renamed._name = name
    return renamed


class SpanNamingSpanExporter(SpanExporter):
    """A SpanExporter that renames spans according to SpanNameSettings before delegating."""

    def __init__(self, delegate: SpanExporter, settings: SpanNameSettings | None = None):
        self._delegate = delegate
        self._settings = settings if settings is not None else span_name_settings

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        config = self._settings._get()
        if not config.use_path and not config.groups:
            return self._delegate.export(spans)

        renamed: list[ReadableSpan] | None = None
        for i, span in enumerate(spans):
            name = _span_name(span, config)
            if name is not None:
                if renamed is None:
                    renamed = list(spans)
                renamed[i] = _renamed_span(span, name)
        return self._delegate.export(spans if renamed is None else renamed)

    def shutdown(self) -> None:
        self._delegate.shutdown()

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return self._delegate.force_flush(timeout_millis)

    def __repr__(self) -> str:
        return f"SpanNamingSpanExporter({self._delegate!r})"
