#!/bin/bash

# Start the Elasticsearch server
/elasticsearch/bin/elasticsearch > /app/elasticsearch.log 2>&1 &

# Wait for Elasticsearch to be up and running
until curl -s http://localhost:9200 >/dev/null; do
    sleep 5
done

# Set the password for the elastic user using REST API
curl -X POST "http://localhost:9200/_security/user/elastic/_password" \
    -H "Content-Type: application/json" \
    -u elastic:<default_password> -d '{"password": "<password"}'

# Start the vLLM server
python -m vllm.entrypoints.openai.api_server --host 0.0.0.0 --port 8000 --model mistralai/Mistral-7B-Instruct-v0.1 > /app/vllm.log 2>&1 &
wait
