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

from opentelemetry.util.re import parse_env_headers
import re

MASK = "[REDACTED]"

# entries are regexes
_KEYS_TO_SANITIZE = [
    "password",
    "passwd",
    "pwd",
    "secret",
    ".*key",
    ".*session.*",
    ".*token.*",
    ".*auth.*",
]
KEYS_TO_SANITIZE = [re.compile(entry) for entry in _KEYS_TO_SANITIZE]


def _sanitize_headers_env_vars(env_var_name: str, env_var_value: str):
    # we take care only of headers because that's where secrets may be stored
    if "HEADERS" not in env_var_name:
        return (env_var_name, env_var_value)

    headers = parse_env_headers(env_var_value)

    sanitized = []
    for key, value in headers.items():
        if any(key_re.search(key) for key_re in KEYS_TO_SANITIZE):
            sanitized.append(f"{key}={MASK}")
        else:
            sanitized.append(f"{key}={value}")

    return (env_var_name, ",".join(sanitized))
