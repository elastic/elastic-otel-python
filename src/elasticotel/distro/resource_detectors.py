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

import os

AWS_LAMBDA_DETECTORS = ["aws_lambda"]
AZURE_FUNCTIONS_DETECTORS = ["azure_functions"]
GCP_CLOUD_RUN_DETECTORS = ["_gcp"]
KUBERNETES_DETECTORS = ["_gcp", "aws_eks"]
OTHER_CLOUD_DETECTORS = [
    "_gcp",
    "aws_ec2",
    "aws_ecs",
    "aws_elastic_beanstalk",
    "azure_app_service",
    "azure_vm",
]


def _on_aws_lambda():
    """Cheap check to detect if we are running on AWS lambda"""
    return "AWS_LAMBDA_FUNCTION_NAME" in os.environ


def _on_azure_functions():
    """Cheap check to detect if we are running on Azure functions"""
    return "FUNCTIONS_WORKER_RUNTIME" in os.environ


def _on_gcp_cloud_run():
    """Cheap check to detect if we are running inside Google Cloud Run"""
    return "K_CONFIGURATION" in os.environ


def _on_k8s():
    """Cheap check to detect if we are running inside a Kubernetes pod or not"""
    return "KUBERNETES_SERVICE_HOST" in os.environ


def get_cloud_resource_detectors():
    """Helper to get a subset of the available cloud resource detectors depending on the environment

    This is done to avoid loading resource detectors doing HTTP requests for metadata that will fail"""
    if _on_aws_lambda():
        return AWS_LAMBDA_DETECTORS
    elif _on_azure_functions():
        return AZURE_FUNCTIONS_DETECTORS
    elif _on_gcp_cloud_run():
        return GCP_CLOUD_RUN_DETECTORS
    elif _on_k8s():
        return KUBERNETES_DETECTORS
    return OTHER_CLOUD_DETECTORS
