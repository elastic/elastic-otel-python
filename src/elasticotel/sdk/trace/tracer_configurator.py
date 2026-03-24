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

import inspect
from functools import lru_cache

from opentelemetry.sdk.trace import _TracerConfig, _TracerConfiguratorRulesT, _InstrumentationScopePredicateT
from opentelemetry.sdk.util.instrumentation import InstrumentationScope


class _UpdatableRuleBasedTracerConfigurator:
    """Updatatable version of what's available upstream"""

    def __init__(
        self,
        *,
        rules: _TracerConfiguratorRulesT,
        default_config: _TracerConfig,
    ):
        self._rules = rules
        self._default_config = default_config

    def __call__(self, tracer_scope: InstrumentationScope) -> _TracerConfig:
        for predicate, tracer_config in list(self._rules):
            if predicate(tracer_scope):
                return tracer_config

        # if no rule matched return the default config
        return self._default_config

    @property
    def rules(self):
        return self._rules

    def _comparable_rules(
        self, rules: _TracerConfiguratorRulesT
    ) -> list[tuple[str | _InstrumentationScopePredicateT, _TracerConfig]]:
        """Transform the rules to be comparable"""

        def unpack_pattern(predicate) -> str | _InstrumentationScopePredicateT:
            # this assumes _scope_name_matches_glob is used to match
            pattern = inspect.getclosurevars(predicate).nonlocals.get("glob_pattern")
            if pattern is not None:
                return pattern
            return predicate

        comparable_rules = [(unpack_pattern(predicate), config) for predicate, config in rules]
        return comparable_rules

    def update_rules(self, rules: _TracerConfiguratorRulesT) -> bool:
        """Updates rules if they are different than the current ones"""
        if self._comparable_rules(rules) == self._comparable_rules(self.rules):
            return False

        self._rules = rules
        return True


_tracer_configurator = _UpdatableRuleBasedTracerConfigurator(rules=[], default_config=_TracerConfig(is_enabled=True))


def _get_tracer_configurator():
    global _tracer_configurator
    return _tracer_configurator


@lru_cache
def _updatable_tracer_configurator(
    tracer_scope: InstrumentationScope,
) -> _TracerConfig:
    tracer_configurator = _get_tracer_configurator()
    return tracer_configurator(tracer_scope=tracer_scope)
