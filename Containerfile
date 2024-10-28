# Start with a base image that has Python and other necessary components
FROM python:3.10-slim

# Switch to root to avoid permissions issues
USER root

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    unzip \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.15.3-linux-x86_64.tar.gz \
    && wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.15.3-linux-x86_64.tar.gz.sha512 \
    && shasum -a 512 -c elasticsearch-8.15.3-linux-x86_64.tar.gz.sha512 \
    && tar -xzf elasticsearch-8.15.3-linux-x86_64.tar.gz \
    && mv elasticsearch-8.15.3 /elasticsearch \
    && chmod -R 777 /elasticsearch

# Create the Elasticsearch keystore during the image build process to avoid running into permissions issues
RUN /elasticsearch/bin/elasticsearch-keystore create

# Expose the necessary ports for Elasticsearch and vLLM
EXPOSE 9200 8000

# Install vLLM and required Python packages
RUN pip install --no-cache-dir vllm haystack-ai trafilatura lxml_html_clean elasticsearch elasticsearch-haystack transformers[torch,sentencepiece] sentence-transformers

# Set the working directory in the container
WORKDIR /app

# Make sure to permission issues arise
RUN chmod -R 777 /app

# Clone the Haystack application source code from the Github repository
RUN git clone https://github.com/ilya-kolchinsky/RHOAI-RAG.git /app

# Define environment variables for Elasticsearch
ENV ES_JAVA_OPTS="-Xms512m -Xmx512m"

# Disable Haystack telemetry collection
ENV HAYSTACK_TELEMETRY_ENABLED="False"

# Setup Transformers cache
RUN mkdir cache
RUN chmod -R 777 /app
ENV TRANSFORMERS_CACHE="/app/cache"

# Use the script as the entrypoint
CMD ["./finish_setup.sh"]
