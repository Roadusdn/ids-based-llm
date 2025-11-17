#!/bin/bash

KIBANA_URL="http://localhost:5601"
DASHBOARD_FILE="presentation/elk/kibana/dashboard.ndjson"

if [ ! -f "$DASHBOARD_FILE" ]; then
    echo "[!] dashboard.ndjson not found!"
    exit 1
fi

echo "[*] Importing Kibana dashboard..."

curl -X POST "$KIBANA_URL/api/saved_objects/_import?overwrite=true" \
     -H "kbn-xsrf: true" \
     --form file=@"$DASHBOARD_FILE"

echo "[✔] Dashboard imported successfully."

