# Start with a base image that has Python and other necessary components
FROM python:3.10-slim

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    unzip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Elasticsearch
RUN curl -fsSL https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add - \
    && echo "deb https://artifacts.elastic.co/packages/oss-7.x/apt stable main" | tee -a /etc/apt/sources.list.d/elastic-7.x.list \
    && apt-get update && apt-get install -y elasticsearch-oss \
    && rm -rf /var/lib/apt/lists/*

# Install vLLM and required Python packages
RUN pip install --no-cache-dir vllm haystack-ai elasticsearch elasticsearch-haystack

# Set the working directory in the container
WORKDIR /app

# Clone the Haystack application source code from the Github repository
RUN git clone https://github.com/ilya-kolchinsky/RHOAI-RAG.git /app

# Expose the necessary ports for Elasticsearch and vLLM
EXPOSE 9200 8000

# Define environment variables for Elasticsearch
ENV ES_JAVA_OPTS="-Xms512m -Xmx512m"

# Configure Elasticsearch
RUN echo "network.host: 0.0.0.0" >> /etc/elasticsearch/elasticsearch.yml

# Run Elasticsearch
CMD service elasticsearch start &

# Run Haystack pipeline in indexing mode
CMD python main.py -i

# Run vLLM server
CMD vllm serve --host 0.0.0.0 --port 8000 --model mistralai/Mistral-7B-Instruct-v0.1 &
