#!/bin/bash

################################################################################
# Suricata Installation Script (Source Build or APT)
# IDS-LLM Hybrid Intrusion Detection System
#
# 사용 환경: VMware Ubuntu 22.0
# 역할: Suricata 설치 및 설정 자동화
################################################################################

#!/bin/bash

#!/bin/bash

set -e

USER_HOME=$(eval echo "~$USER")

echo "[1/6] 시스템 패키지 업데이트"
sudo apt update

echo "[2/6] Suricata 빌드 의존성 설치"
sudo apt install -y \
  build-essential autoconf automake libtool \
  libpcap-dev libpcre3-dev libpcre2-dev \
  libyaml-dev pkg-config zlib1g-dev \
  libcap-ng-dev libjansson-dev libmagic-dev \
  rustc cargo libnfnetlink-dev wget

echo "[3/6] Suricata 다운로드"
wget https://www.openinfosecfoundation.org/download/suricata-7.0.4.tar.gz
tar -xvf suricata-7.0.4.tar.gz
cd suricata-7.0.4

echo "[4/6] Suricata configure"
./configure --prefix=/usr/local/suricata

echo "[5/6] Suricata 빌드 및 설치"
make -j$(nproc)
sudo make install
sudo ldconfig
sudo suricata-update

echo "[6/6] Suricata 설정 파일 자동 패칭"

CONFIG_FILE="/etc/suricata/suricata.yaml"

sudo cp /usr/local/suricata/etc/suricata/* /etc/suricata/

sudo sed -i '/^outputs:/a \
  - eve-log:\n\
      enabled: yes\n\
      filetype: regular\n\
      filename: '"$USER_HOME"'/ids-based-llm/acquisition/suricata/eve.json\n\
      types:\n\
        - alert\n\
        - http\n\
        - dns\n\
        - tls\n\
        - flow\n\
        - anomaly\n' $CONFIG_FILE

echo "Suricata 설치 및 설정 자동화 완료"
echo "실행: sudo /usr/local/suricata/bin/suricata -c /etc/suricata/suricata.yaml -i eth0"

