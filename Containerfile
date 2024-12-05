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

# Install the required Python packages
RUN pip install haystack-ai trafilatura lxml_html_clean pymilvus milvus-haystack transformers[torch,sentencepiece] sentence-transformers docling ragas ragas-haystack

# Clone the Haystack application source code from the Github repository
RUN git clone https://github.com/redhat-et/RHELAI-RHOAI-RAG.git /app

# Set the working directory in the container
WORKDIR /app

# Install project dependencies
RUN pip install -r requirements.txt

# Disable Haystack telemetry collection
ENV HAYSTACK_TELEMETRY_ENABLED="False"

# Setup the directory for the documents to be indexed
RUN mkdir docs
#RUN docling --to json --output docs --verbose https://docs.redhat.com/en-us/documentation/red_hat_enterprise_linux/7/pdf/developer_guide/Red_Hat_Enterprise_Linux-7-Developer_Guide-en-US.pdf

# Setup Transformers cache
RUN mkdir cache
ENV TRANSFORMERS_CACHE="/app/cache"

# Make sure no permission issues arise
RUN chmod -R 777 /app
RUN chmod -R 777 /app/docs
RUN chmod -R 777 /app/cache

# Default command to keep the container running
CMD ["sleep", "infinity"]
