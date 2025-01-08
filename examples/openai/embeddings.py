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

import numpy as np
import openai

EMBEDDINGS_MODEL = os.environ.get("EMBEDDINGS_MODEL", "text-embedding-3-small")


def main():
    client = openai.Client()

    products = [
        "Search: Ingest your data, and explore Elastic's machine learning and retrieval augmented generation (RAG) capabilities."
        "Observability: Unify your logs, metrics, traces, and profiling at scale in a single platform.",
        "Security: Protect, investigate, and respond to cyber threats with AI-driven security analytics."
        "Elasticsearch: Distributed, RESTful search and analytics.",
        "Kibana: Visualize your data. Navigate the Stack.",
        "Beats: Collect, parse, and ship in a lightweight fashion.",
        "Connectors: Connect popular databases, file systems, collaboration tools, and more.",
        "Logstash: Ingest, transform, enrich, and output.",
    ]

    # Generate embeddings for each product. Keep them in an array instead of a vector DB.
    product_embeddings = []
    for product in products:
        product_embeddings.append(create_embedding(client, product))

    query_embedding = create_embedding(client, "What can help me connect to a database?")

    # Calculate cosine similarity between the query and document embeddings
    similarities = []
    for product_embedding in product_embeddings:
        similarity = np.dot(query_embedding, product_embedding) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(product_embedding)
        )
        similarities.append(similarity)

    # Get the index of the most similar document
    most_similar_index = np.argmax(similarities)

    print(products[most_similar_index])


def create_embedding(client, text):
    return client.embeddings.create(input=[text], model=EMBEDDINGS_MODEL, encoding_format="float").data[0].embedding


if __name__ == "__main__":
    main()
