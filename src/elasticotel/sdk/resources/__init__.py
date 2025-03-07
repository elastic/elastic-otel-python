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

import sys
import uuid

from opentelemetry.semconv._incubating.attributes import telemetry_attributes
from opentelemetry.semconv._incubating.attributes import service_attributes
from opentelemetry.sdk.resources import (
    Attributes,
    Resource,
    ResourceDetector,
    PROCESS_RUNTIME_DESCRIPTION,
    PROCESS_RUNTIME_NAME,
    PROCESS_RUNTIME_VERSION,
)

from elasticotel.distro import version


class ProcessRuntimeResourceDetector(ResourceDetector):
    """Subset of upstream ProcessResourceDetector to only fill process runtime attributes"""

    def detect(self) -> "Resource":
        runtime_version = ".".join(
            map(
                str,
                (
                    sys.version_info[:3]
                    if sys.version_info.releaselevel == "final" and not sys.version_info.serial
                    else sys.version_info
                ),
            )
        )
        resource_info: Attributes = {
            PROCESS_RUNTIME_DESCRIPTION: sys.version,
            PROCESS_RUNTIME_NAME: sys.implementation.name,
            PROCESS_RUNTIME_VERSION: runtime_version,
        }
        return Resource(resource_info)


class ServiceInstanceResourceDetector(ResourceDetector):
    """Resource detector to fill service instance attributes

    NOTE: with multi-process services this is shared between processes"""

    def detect(self) -> "Resource":
        resource_info: Attributes = {service_attributes.SERVICE_INSTANCE_ID: str(uuid.uuid4())}
        return Resource(resource_info)


class TelemetryDistroResourceDetector(ResourceDetector):
    """Resource detector to fill telemetry.distro attributes"""

    def detect(self) -> "Resource":
        resource_info: Attributes = {
            telemetry_attributes.TELEMETRY_DISTRO_NAME: "elastic",
            telemetry_attributes.TELEMETRY_DISTRO_VERSION: version.__version__,
        }
        return Resource(resource_info)
