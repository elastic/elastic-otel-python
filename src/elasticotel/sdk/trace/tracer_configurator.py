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

from opentelemetry.sdk.trace import _TracerConfig, _RuleBasedTracerConfigurator
from opentelemetry.sdk.util._configurator import ConfiguratorRulesT
from opentelemetry.sdk.util.instrumentation import InstrumentationScope, _InstrumentationScopePredicateT


class _UpdatableRuleBasedTracerConfigurator(_RuleBasedTracerConfigurator):
    """Updatatable version of what's available upstream

    The updatable_rules return an hint if the rules changed or not so that
    we can avoid updating them at every configuration update if they haven't
    changed"""

    @property
    def rules(self):
        return self._rules

    def _comparable_rules(
        self, rules: ConfiguratorRulesT
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

    def rules_changed(self, rules: ConfiguratorRulesT) -> bool:
        return self._comparable_rules(rules) != self._comparable_rules(self.rules)


_tracer_configurator = _UpdatableRuleBasedTracerConfigurator(rules=[], default_config=_TracerConfig(is_enabled=True))


def _get_tracer_configurator() -> _UpdatableRuleBasedTracerConfigurator:
    global _tracer_configurator
    return _tracer_configurator


def _updatable_tracer_configurator(
    tracer_scope: InstrumentationScope,
) -> _TracerConfig:
    tracer_configurator = _get_tracer_configurator()
    return tracer_configurator(tracer_scope)
