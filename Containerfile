# Start with a base image that has Python and other necessary components
FROM python:3.10-slim

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Elasticsearch
RUN wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.15.3-linux-x86_64.tar.gz \
    && wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.15.3-linux-x86_64.tar.gz.sha512 \
    && shasum -a 512 -c elasticsearch-8.15.3-linux-x86_64.tar.gz.sha512 \
    && tar -xzf elasticsearch-8.15.3-linux-x86_64.tar.gz \
    && cd elasticsearch-8.15.3/

# Expose the necessary ports for Elasticsearch and vLLM
EXPOSE 9200 8000

# Run Elasticsearch
CMD ./bin/elasticsearch &

# Install vLLM and required Python packages
RUN pip install --no-cache-dir vllm haystack-ai elasticsearch elasticsearch-haystack transformers[torch,sentencepiece] sentence-transformers

# Set the working directory in the container
WORKDIR /app

# Clone the Haystack application source code from the Github repository
RUN git clone https://github.com/ilya-kolchinsky/RHOAI-RAG.git /app

# Define environment variables for Elasticsearch
ENV ES_JAVA_OPTS="-Xms512m -Xmx512m"

# Disable Haystack telemetry collection
ENV HAYSTACK_TELEMETRY_ENABLED="False"

# Setup Transformers cache
RUN mkdir cache
RUN chmod -R 777 /app/cache
ENV TRANSFORMERS_CACHE="/app/cache"

# Run vLLM server
CMD vllm serve --host 0.0.0.0 --port 8000 --model mistralai/Mistral-7B-Instruct-v0.1 &

# Run Haystack pipeline in indexing mode
CMD python main.py -i
