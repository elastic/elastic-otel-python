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

from typing import Mapping

import requests

from opentelemetry._opamp import messages
from opentelemetry._opamp.transport.exceptions import OpAMPException
from opentelemetry._opamp.transport.base import HttpTransport, base_headers


class RequestsTransport(HttpTransport):
    # TODO: move some stuff here instead of send?
    def __init__(self):
        self.session = requests.Session()

    # TODO: support basic-auth?
    def send(self, url: str, headers: Mapping[str, str], data: bytes, timeout_millis: int):
        headers = {**base_headers, **headers}
        timeout: float = timeout_millis / 1e3
        try:
            response = self.session.post(url, headers=headers, data=data, timeout=timeout)
            response.raise_for_status()
        except Exception:
            raise OpAMPException

        message = messages._decode_message(response.content)

        return message
