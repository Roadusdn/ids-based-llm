#!/bin/bash

set -e

PIPELINE="presentation/elk/logstash/logstash.conf"

if [ ! -f "$PIPELINE" ]; then
    echo "[!] Logstash pipeline not found: $PIPELINE"
    exit 1
fi

echo "[*] Running Logstash pipeline test..."
logstash -t -f "$PIPELINE"

echo "[*] Starting Logstash..."
logstash -f "$PIPELINE"

