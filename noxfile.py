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

import nox
import sys


def run_tests(session: nox.Session, pytest_extra_args: list[str] = []):
    python_version = (sys.version_info.major, sys.version_info.minor, sys.version_info.micro)
    vcrpy_is_supported = python_version >= (3, 10, 0)

    session.install("-r", "dev-requirements.txt")
    if vcrpy_is_supported:
        session.install("pytest-vcr")
    # install the package for being able to use the entry points we define
    session.install("-e", ".")

    session.run("pytest", *pytest_extra_args, env={"EDOT_IN_NOX": "1"})


@nox.session
def tests(session):
    run_tests(session)


@nox.session(default=False)
def with_integration_tests(session):
    run_tests(session, ["--with-integration-tests"])
