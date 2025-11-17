#!/bin/bash

set -e

echo "[*] Updating system..."
sudo apt update -y

echo "[*] Installing dependencies..."
sudo apt install apt-transport-https wget gnupg -y

echo "[*] Adding Elastic GPG key..."
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -

echo "[*] Adding Elastic repository..."
echo "deb https://artifacts.elastic.co/packages/8.x/apt stable main" | \
  sudo tee /etc/apt/sources.list.d/elastic-8.x.list

echo "[*] Updating package lists..."
sudo apt update -y

echo "[*] Installing Elasticsearch, Kibana, Logstash..."
sudo apt install elasticsearch kibana logstash -y

echo "[*] Enabling and starting Elasticsearch..."
sudo systemctl enable elasticsearch
sudo systemctl start elasticsearch

echo "[*] Enabling and starting Kibana..."
sudo systemctl enable kibana
sudo systemctl start kibana

echo "------------------------------------------"
echo "[✔] ELK installation complete."
echo "Elasticsearch: http://localhost:9200"
echo "Kibana:        http://localhost:5601"
echo "------------------------------------------"

