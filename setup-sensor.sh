#!/usr/bin/env bash
set -euo pipefail

# Sensor VM bootstrap: install system deps, create venv, install Python deps,
# and optionally build Suricata/Zeek.
#
# Env knobs:
#   SKIP_APT=1           # skip apt install (default 0)
#   INSTALL_SURICATA=1   # run acquisition/suricata/build-suricata.sh (default 0)
#   INSTALL_ZEEK=1       # run acquisition/zeek/build-zeek.sh (default 0)
#   SKIP_IF_READY=1      # if venv exists and deps present, skip installs (default 1)
#   PYTHON=python3       # override python command

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON:-python3}"
SKIP_APT="${SKIP_APT:-0}"
INSTALL_SURICATA="${INSTALL_SURICATA:-0}"
INSTALL_ZEEK="${INSTALL_ZEEK:-0}"
SKIP_IF_READY="${SKIP_IF_READY:-1}"

check_python_ready() {
  local pkgs=(fastapi uvicorn pydantic requests PyYAML httpx python-iptables streamlit)
  for p in "${pkgs[@]}"; do
    if ! python -m pip show "$p" >/dev/null 2>&1; then
      return 1
    fi
  done
  return 0
}

echo "[1/4] create/upgrade virtualenv"
cd "${ROOT_DIR}"
if [[ ! -d ".venv" ]]; then
  "${PYTHON_BIN}" -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip

if check_python_ready && [[ "${SKIP_IF_READY}" == "1" && "${INSTALL_SURICATA}" != "1" && "${INSTALL_ZEEK}" != "1" ]]; then
  echo "[ready] venv found and Python deps already installed; skipping installs."
else
  if [[ "${SKIP_APT}" != "1" ]]; then
    echo "[2/4] apt install base dependencies"
    sudo apt update
    sudo apt install -y \
      python3 python3-venv python3-pip python3-dev \
      build-essential libffi-dev libssl-dev \
      iptables iptables-persistent
  else
    echo "[2/4] skipping apt install (SKIP_APT=${SKIP_APT})"
  fi

  echo "[3/4] install Python requirements (Reasoner/Response/Streamlit)"
  pip install -r "${ROOT_DIR}/llm_reasoner/requirements.txt"
  pip install -r "${ROOT_DIR}/response/requirements.txt"
  pip install streamlit
fi

echo "[4/4] optional: build Suricata/Zeek"
if [[ "${INSTALL_SURICATA}" == "1" ]]; then
  echo "Installing Suricata (sudo)..."
  sudo bash "${ROOT_DIR}/acquisition/suricata/build-suricata.sh"
else
  echo "Skipping Suricata build (INSTALL_SURICATA=${INSTALL_SURICATA})"
fi

if [[ "${INSTALL_ZEEK}" == "1" ]]; then
  echo "Installing Zeek (sudo)..."
  sudo bash "${ROOT_DIR}/acquisition/zeek/build-zeek.sh"
else
  echo "Skipping Zeek build (INSTALL_ZEEK=${INSTALL_ZEEK})"
fi

echo "Setup complete. Activate venv with: source .venv/bin/activate"
