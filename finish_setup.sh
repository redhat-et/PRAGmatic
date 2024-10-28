#!/bin/bash

# Start the Elasticsearch server
/elasticsearch/bin/elasticsearch > /app/elasticsearch.log 2>&1 &

# Wait for Elasticsearch to be up and running
until curl -s http://localhost:9200 >/dev/null; do
    sleep 5
done

echo y | /elasticsearch/bin/elasticsearch-reset-password -u elastic > /app/elastic_password.log

# Start the vLLM server
python -m vllm.entrypoints.openai.api_server --host 0.0.0.0 --port 8000 --model ibm-granite/granite-3.0-2b-instruct > /app/vllm.log 2>&1 &
wait
