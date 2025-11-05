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

ELASTIC_OTEL_SYSTEM_METRICS_ENABLED = "ELASTIC_OTEL_SYSTEM_METRICS_ENABLED"
"""
.. envvar:: ELASTIC_OTEL_SYSTEM_METRICS_ENABLED

Enables sending system metrics.

**Default value:** ``false``
"""

ELASTIC_OTEL_OPAMP_ENDPOINT = "ELASTIC_OTEL_OPAMP_ENDPOINT"
"""
.. envvar:: ELASTIC_OTEL_OPAMP_ENDPOINT

OpAMP Endpoint URL.

**Default value:** ``not set``
"""

ELASTIC_OTEL_OPAMP_HEADERS = "ELASTIC_OTEL_OPAMP_HEADERS"
"""
.. envvar:: ELASTIC_OTEL_OPAMP_HEADERS

HTTP headers to be sento do the OpAMP endpoint.

**Default value:** ``not set``
"""

ELASTIC_OTEL_OPAMP_CERTIFICATE = "ELASTIC_OTEL_OPAMP_CERTIFICATE"
"""
.. envvar:: ELASTIC_OTEL_OPAMP_CERTIFICATE

The path of the trusted certificate to use when verifying a server’s TLS credentials, this is needed for mTLS or when the server is using a self-signed certificate.

**Default value:** ``not set``
"""

ELASTIC_OTEL_OPAMP_CLIENT_CERTIFICATE = "ELASTIC_OTEL_OPAMP_CLIENT_CERTIFICATE"
"""
.. envvar:: ELASTIC_OTEL_OPAMP_CLIENT_CERTIFICATE

Client certificate/chain trust for clients private key path to use in mTLS communication in PEM format.

**Default value:** ``not set``
"""

ELASTIC_OTEL_OPAMP_CLIENT_KEY = "ELASTIC_OTEL_OPAMP_CLIENT_KEY"
"""
.. envvar:: ELASTIC_OTEL_OPAMP_CLIENT_KEY

Client private key path to use in mTLS communication in PEM format.

**Default value:** ``not set``
"""
