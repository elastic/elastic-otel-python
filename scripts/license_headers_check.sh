#!/usr/bin/env sh
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

if [ $# -eq 0 ]
then
    FILES=$(git ls-files | grep -e "\.py$" -e "\.c$" -e "\.sh$" | grep -v -e "/proto/" | xargs -r -d'\n' -I{} find {} -size +1c)
else
    FILES=$@
fi

LICENSE_HEADER="Copyright Elasticsearch B.V. and/or licensed to Elasticsearch B.V. under one"
UPSTREAM_LICENSE_HEADER="Copyright The OpenTelemetry Authors"

MISSING=$(grep --files-without-match -e "$LICENSE_HEADER" -e "$UPSTREAM_LICENSE_HEADER" ${FILES})

if [ -z "$MISSING" ]
then
    exit 0
else
    echo "Files with missing copyright header:"
    echo $MISSING
    exit 1
fi
