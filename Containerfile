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

# Install Haystack and required Python packages
RUN pip install haystack-ai trafilatura lxml_html_clean elasticsearch-haystack transformers[torch,sentencepiece] sentence-transformers

# Set the working directory in the container
WORKDIR /app

# Clone the Haystack application source code from the Github repository
RUN git clone https://github.com/ilya-kolchinsky/RHOAI-RAG.git /app

# Disable Haystack telemetry collection
ENV HAYSTACK_TELEMETRY_ENABLED="False"

# Setup Transformers cache
RUN mkdir cache
ENV TRANSFORMERS_CACHE="/app/cache"

# Make sure no permission issues arise
RUN chmod -R 777 /app

# Default command to keep the container running
CMD ["sleep", "infinity"]
