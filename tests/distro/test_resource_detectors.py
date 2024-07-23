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

from unittest import TestCase, mock

from elasticotel.distro.resource_detectors import get_cloud_resource_detectors


class TestGetCloudResourceDetectors(TestCase):
    @mock.patch.dict("os.environ", {"AWS_LAMBDA_FUNCTION_NAME": "lambda"}, clear=True)
    def test_aws_lambda(self):
        resource_detectors = get_cloud_resource_detectors()
        self.assertEqual(resource_detectors, ["aws_lambda"])

    @mock.patch.dict("os.environ", {"FUNCTIONS_WORKER_RUNTIME": "azure"}, clear=True)
    def test_azure_functions(self):
        resource_detectors = get_cloud_resource_detectors()
        self.assertEqual(resource_detectors, ["azure_functions"])

    @mock.patch.dict("os.environ", {"K_CONFIGURATION": "cloudrun"}, clear=True)
    def test_gcp_cloud_run(self):
        resource_detectors = get_cloud_resource_detectors()
        self.assertEqual(resource_detectors, ["_gcp"])

    @mock.patch.dict("os.environ", {"KUBERNETES_SERVICE_HOST": "k8s"}, clear=True)
    def test_kubernetes_pod(self):
        resource_detectors = get_cloud_resource_detectors()
        self.assertEqual(resource_detectors, ["_gcp", "aws_eks", "container"])

    @mock.patch.dict("os.environ", {}, clear=True)
    def test_other_cloud_detectors(self):
        resource_detectors = get_cloud_resource_detectors()
        self.assertEqual(
            resource_detectors,
            ["_gcp", "aws_ec2", "aws_ecs", "aws_elastic_beanstalk", "azure_app_service", "azure_vm", "container"],
        )
