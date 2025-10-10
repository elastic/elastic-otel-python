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

from __future__ import annotations

from typing import Sequence

from opentelemetry.context import Context
from opentelemetry.sdk.trace.sampling import Sampler, SamplingResult
from opentelemetry.trace import Link, SpanKind, TraceState
from opentelemetry.sdk.trace._sampling_experimental import (
    composite_sampler,
    composable_parent_threshold,
    composable_traceid_ratio_based,
)
from opentelemetry.util.types import Attributes


class DynamicCompositeParentThresholdTraceIdRatioBasedSampler(Sampler):
    def __init__(self, ratio: float = 1.0):
        self._delegate = _new_sampler(ratio)

    def should_sample(
        self,
        parent_context: Context | None,
        trace_id: int,
        name: str,
        kind: SpanKind | None = None,
        attributes: Attributes | None = None,
        links: Sequence[Link] | None = None,
        trace_state: TraceState | None = None,
    ) -> SamplingResult:
        return self._delegate.should_sample(
            parent_context,
            trace_id,
            name,
            kind,
            attributes,
            links,
            trace_state,
        )

    def set_ratio(self, ratio: float):
        self._delegate = _new_sampler(ratio)

    def get_description(self) -> str:
        return self._delegate.get_description()


def _new_sampler(ratio: float):
    return composite_sampler(composable_parent_threshold(composable_traceid_ratio_based(ratio)))


def dynamic_composite_parent_threshold_traceid_ratio_based_sampler(ratio: float = 1.0) -> Sampler:
    """Returns a new DynamicCompositeParentThresholdTraceIdRatioBasedSampler.

    This sampler behaves like ParentBasedTraceIdRatio, but the sampling rate can be changed
    at runtime.

    Args:
        ratio: The sampling ratio to use for root spans. Must be between 0.0 and 1.0.

    Returns:
        A new DynamicCompositeParentThresholdTraceIdRatioBasedSampler.
    """
    return DynamicCompositeParentThresholdTraceIdRatioBasedSampler(ratio)
