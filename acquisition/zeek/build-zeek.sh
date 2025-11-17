#!/bin/bash
set -e

###############################################################################
# Zeek 자동 설치 스크립트
# IDS-LLM 네트워크 침입탐지 시스템 - Acquisition Module
#
# 기능:
# - 의존성 자동 설치
# - 소스코드 다운로드 및 빌드
# - PATH 자동 등록
# - 커스텀 Zeek 스크립트 자동 복사
# - local.zeek 자동 패치
# - zeekctl 배포 자동 수행
###############################################################################

USER_HOME=$(eval echo "~$USER")
PROJECT_HOME="$USER_HOME/ids-based-llm/acquisition/zeek"
SITE_DIR="/usr/local/zeek/share/zeek/site"

echo "[1/7] 시스템 업데이트"
sudo apt update

echo "[2/7] 의존성 설치"
sudo apt install -y \
    cmake make gcc g++ flex bison \
    libpcap-dev python3 python3-dev python3-pip swig \
    zlib1g-dev libssl-dev libcurl4-openssl-dev git \
    libmaxminddb-dev libzmq3-dev libczmq-dev

echo "[3/7] Zeek 소스코드 다운로드"
git clone --recursive https://github.com/zeek/zeek
cd zeek

echo "[4/7] Configure 실행"
./configure

echo "[5/7] 컴파일 및 설치"
make -j$(nproc)
sudo make install

echo "[6/7] PATH 등록"
grep -qxF 'export PATH=/usr/local/zeek/bin:$PATH' ~/.bashrc || \
echo 'export PATH=/usr/local/zeek/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

echo "[7/7] 커스텀 Zeek 스크립트 자동 복사"
sudo cp "$PROJECT_HOME/scripts/local.zeek" $SITE_DIR/
sudo cp "$PROJECT_HOME/scripts/http-extend.zeek" $SITE_DIR/ 2>/dev/null || true
sudo cp "$PROJECT_HOME/scripts/dns-extend.zeek" $SITE_DIR/ 2>/dev/null || true

echo "@load local.zeek" | sudo tee -a $SITE_DIR/local.zeek > /dev/null

echo "Zeekctl 배포"
sudo zeekctl deploy

echo "모든 설치 및 설정 완료!"
echo "Zeek 버전 확인: zeek --version"

