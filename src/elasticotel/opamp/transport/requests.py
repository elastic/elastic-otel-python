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

import requests

from elasticotel.omamp.messages import decode_message
from ..exceptions import OpAMPException
from .base import HttpTransport


class RequestsTransport(HttpTransport):
    # TODO: move some stuff here instead of send?
    def __init__(self):
        self.session = requests.Session()

    # TODO: We don't have a specific connection phase ATM but specs says:
    # If the Client is unable to establish a connection to the Server
    # it SHOULD retry connection attempts and use exponential backoff strategy
    # with jitter to avoid overwhelming the Server
    # TODO: support basic-auth
    def send(self, url: str, headers: dict[str, str], data: bytes, timeout_millis: int):
        timeout: float = timeout_millis / 1e3
        try:
            response = self.session.post(url, headers=headers, data=data, timeout=timeout)
            response.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            print(exc, response.status_code)
            # 401 and 404 should raise, 400 should be decoded instead
            if response.status_code not in (400, 503, 429):
                # TODO: we may retry in case of 429 or 503
                raise OpAMPException
        except requests.exception.ConnectionError:
            # TODO: we MAY retry here
            raise OpAMPException
        except Exception:
            raise OpAMPException

        message = decode_message(response.content)

        return message
