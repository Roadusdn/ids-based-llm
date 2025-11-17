#!/bin/bash

TEMPLATE="presentation/elk/elasticsearch/index_template.json"
ES_URL="http://localhost:9200"

if [ ! -f "$TEMPLATE" ]; then
    echo "[!] index_template.json not found!"
    exit 1
fi

echo "[*] Uploading index template to Elasticsearch..."

curl -X PUT "$ES_URL/_index_template/ids-llm-template" \
     -H "Content-Type: application/json" \
     -d @"$TEMPLATE"

echo "[✔] Index template uploaded successfully."

