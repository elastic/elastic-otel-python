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

from elasticotel.sdk.resources import ProcessRuntimeResourceDetector
from opentelemetry.sdk.resources import (
    PROCESS_RUNTIME_NAME,
    PROCESS_RUNTIME_DESCRIPTION,
    PROCESS_RUNTIME_VERSION,
    Resource,
    get_aggregated_resources,
)


class TestProcessRuntimeDetector(TestCase):
    def test_process_runtime_detector(self):
        initial_resource = Resource(attributes={})
        aggregated_resource = get_aggregated_resources([ProcessRuntimeResourceDetector()], initial_resource)

        self.assertEqual(
            sorted(aggregated_resource.attributes.keys()),
            [PROCESS_RUNTIME_DESCRIPTION, PROCESS_RUNTIME_NAME, PROCESS_RUNTIME_VERSION],
        )
