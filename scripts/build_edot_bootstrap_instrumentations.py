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

import ast

# this requires python 3.11
import tomllib
from pathlib import Path

root_dir = Path(__file__).parent.parent
instrumentations_repo_dir = root_dir.parent / "elastic-otel-python-instrumentations"
instrumentations_dir = instrumentations_repo_dir / "instrumentation"

pyprojects = instrumentations_dir.glob("*/pyproject.toml")

instrumentations = []

for pyproject in pyprojects:
    with pyproject.open("rb") as f:
        data = tomllib.load(f)

        instrumentation_name = data["project"]["name"]
        instruments = data["project"]["optional-dependencies"]["instruments"]

        version = None
        for version_module in pyproject.parent.glob("src/opentelemetry/instrumentation/*/version.py"):
            with version_module.open("rb") as vf:
                for line in vf:
                    if line.startswith(b"__version__"):
                        tree = ast.parse(line)
                        assignment_value = tree.body[0].value
                        version = assignment_value.value
                        break
            break

        # not a fan of creating multiple entries is we require more than one library but that's the status
        # see https://github.com/open-telemetry/opentelemetry-python-contrib/pull/2409
        for instrument in instruments:
            instrumentations.append(
                {
                    "library": instrument,
                    "instrumentation": f"{instrumentation_name}=={version}",
                }
            )

print(instrumentations)
