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

from unittest import TestCase

from elasticotel.distro.sanitization import _sanitize_headers_env_vars


class TestSanitizeHeadersEnvVars(TestCase):
    def test_ignores_non_headers(self):
        sanitized = _sanitize_headers_env_vars("ENDPOINT", "api-key=secret")
        self.assertEqual(sanitized, ("ENDPOINT", "api-key=secret"))

    def test_sanitizes_single_item(self):
        sanitized = _sanitize_headers_env_vars("HEADERS", "api-key=secret")
        self.assertEqual(sanitized, ("HEADERS", "api-key=[REDACTED]"))

    def test_sanitizes_list_of_items(self):
        sanitized = _sanitize_headers_env_vars(
            "HEADERS",
            "api-key=secret,password=secret,passwd=secret,pwd=secret,secret=secret,key=secret,sessionid=secret,auth-token=secret,token=secret,bearer-token=auth,auth=secret",
        )
        self.assertEqual(
            sanitized,
            (
                "HEADERS",
                "api-key=[REDACTED],password=[REDACTED],passwd=[REDACTED],pwd=[REDACTED],secret=[REDACTED],key=[REDACTED],sessionid=[REDACTED],auth-token=[REDACTED],token=[REDACTED],bearer-token=[REDACTED],auth=[REDACTED]",
            ),
        )

    def test_ignores_other_values_single_item(self):
        sanitized = _sanitize_headers_env_vars("HEADERS", "content-type=no-secret")
        self.assertEqual(sanitized, ("HEADERS", "content-type=no-secret"))

    def test_ignores_other_values_list_of_items(self):
        sanitized = _sanitize_headers_env_vars("HEADERS", "content-type=no-secret,other-header=no-secret")
        self.assertEqual(sanitized, ("HEADERS", "content-type=no-secret,other-header=no-secret"))

    def test_handles_mixed_list_of_items(self):
        sanitized = _sanitize_headers_env_vars("HEADERS", "api-key=secret,content-type=no-secret")
        self.assertEqual(sanitized, ("HEADERS", "api-key=[REDACTED],content-type=no-secret"))

    def test_drops_invalid_entries(self):
        sanitized = _sanitize_headers_env_vars("HEADERS", "content-type:no-secret")
        self.assertEqual(sanitized, ("HEADERS", ""))

    def test_case_insensitive(self):
        sanitized = _sanitize_headers_env_vars("HEADERS", "Authorization=ApiKey")
        self.assertEqual(sanitized, ("HEADERS", "authorization=[REDACTED]"))

    def test_handles_spaces(self):
        sanitized = _sanitize_headers_env_vars("HEADERS", "authorization=api-key secret")
        self.assertEqual(sanitized, ("HEADERS", "authorization=[REDACTED]"))
