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

from opentelemetry.instrumentation.bootstrap import run as orig_run
from opentelemetry.instrumentation.bootstrap_gen import (
    default_instrumentations as gen_default_instrumentations,
)
from opentelemetry.instrumentation.bootstrap_gen import (
    libraries as gen_libraries,
)
from packaging.requirements import Requirement


# the instrumentations available in opentelemetry-bootstrap we want to skip
_EXCLUDED_INSTRUMENTATIONS = {"opentelemetry-instrumentation-openai-v2"}

# update with:
# $ python3.12 scripts/build_edot_bootstrap_instrumentations.py | ruff format -
_EDOT_INSTRUMENTATIONS = [
    {
        "library": "openai >= 1.2.0",
        "instrumentation": "elastic-opentelemetry-instrumentation-openai",
    }
]


def _get_instrumentation_name(library_entry):
    instrumentation = library_entry["instrumentation"]
    instrumentation_name = Requirement(instrumentation)
    return instrumentation_name.name


def run() -> None:
    """This is a tiny wrapper around the upstream opentelemetry-boostrap implementation that let us decide which instrumentation to use"""
    libraries = [
        lib for lib in gen_libraries if _get_instrumentation_name(lib) not in _EXCLUDED_INSTRUMENTATIONS
    ] + _EDOT_INSTRUMENTATIONS
    return orig_run(default_instrumentations=gen_default_instrumentations, libraries=libraries)
