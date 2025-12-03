#!/usr/bin/env bash
set -euo pipefail

# Start all layers: Suricata/Zeek capture, normalizer router, Response API,
# LLM Reasoner API, Presentation API, and Streamlit dashboard.
# Key env vars:
#   PORT_API (8000), PORT_REASONER (8001), PORT_UI (8501), PORT_RESPONSE (9001)
#   ENABLE_SURICATA (1), ENABLE_ZEEK (1)
#   SURICATA_CMD (/usr/local/suricata/bin/suricata), SURICATA_CONFIG (/etc/suricata/suricata.yaml), SURICATA_IFACE (eth0), SURICATA_LOG (/var/log/suricata/eve.json)
#   ZEEK_CMD (zeek), ZEEK_IFACE (eth0) or ZEEK_PCAP (pcap file), ZEEK_LOG_DIR (/usr/local/zeek/logs/current/)
#   NORMALIZER_OUTPUT (/tmp/ids-llm-events.jsonl)

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${ROOT_DIR}:${PYTHONPATH:-}"

PORT_API="${PORT_API:-8000}"
PORT_REASONER="${PORT_REASONER:-8001}"
PORT_UI="${PORT_UI:-8501}"
PORT_RESPONSE="${PORT_RESPONSE:-9001}"

ENABLE_SURICATA="${ENABLE_SURICATA:-1}"
SURICATA_CMD="${SURICATA_CMD:-/usr/local/suricata/bin/suricata}"
SURICATA_CONFIG="${SURICATA_CONFIG:-/etc/suricata/suricata.yaml}"
SURICATA_IFACE="${SURICATA_IFACE:-eth0}"
SURICATA_LOG="${SURICATA_LOG:-/var/log/suricata/eve.json}"
SURICATA_SUDO="${SURICATA_SUDO:-0}"

ENABLE_ZEEK="${ENABLE_ZEEK:-1}"
ZEEK_CMD="${ZEEK_CMD:-zeek}"
ZEEK_IFACE="${ZEEK_IFACE:-eth0}"
ZEEK_PCAP="${ZEEK_PCAP:-}"
ZEEK_LOG_DIR="${ZEEK_LOG_DIR:-/usr/local/zeek/logs/current/}"
ZEEK_SUDO="${ZEEK_SUDO:-0}"

NORMALIZER_OUTPUT="${NORMALIZER_OUTPUT:-/tmp/ids-llm-events.jsonl}"

need_cmds=(uvicorn streamlit python3)
if [[ "${ENABLE_SURICATA}" == "1" ]]; then
  need_cmds+=("${SURICATA_CMD}")
fi
if [[ "${ENABLE_ZEEK}" == "1" ]]; then
  need_cmds+=("${ZEEK_CMD}")
fi

for cmd in "${need_cmds[@]}"; do
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    echo "Missing command: ${cmd}. Activate venv and install deps before running." >&2
    exit 1
  fi
done

if [[ -n "${VIRTUAL_ENV:-}" ]]; then
  echo "Using venv: ${VIRTUAL_ENV}"
else
  echo "No venv detected (optional): activate one if you need specific deps."
fi

mkdir -p "${ROOT_DIR}/logs"
pids=()

cleanup() {
  echo "Stopping services..."
  for pid in "${pids[@]:-}"; do
    kill "${pid}" 2>/dev/null || true
  done
}
trap cleanup EXIT

start_suricata() {
  if [[ "${ENABLE_SURICATA}" != "1" ]]; then
    echo "Skipping Suricata (ENABLE_SURICATA=${ENABLE_SURICATA})"
    return
  fi

  echo "Starting Suricata on ${SURICATA_IFACE} (config: ${SURICATA_CONFIG}, log: ${SURICATA_LOG})"
  local cmd=("${SURICATA_CMD}" -c "${SURICATA_CONFIG}" -i "${SURICATA_IFACE}")
  if [[ "${SURICATA_SUDO}" == "1" ]]; then
    cmd=(sudo "${cmd[@]}")
  fi
  "${cmd[@]}" >"${ROOT_DIR}/logs/suricata.log" 2>&1 &
  pids+=("$!")
}

start_zeek() {
  if [[ "${ENABLE_ZEEK}" != "1" ]]; then
    echo "Skipping Zeek (ENABLE_ZEEK=${ENABLE_ZEEK})"
    return
  fi

  mkdir -p "${ZEEK_LOG_DIR}"

  if [[ -n "${ZEEK_PCAP}" ]]; then
    echo "Starting Zeek offline on ${ZEEK_PCAP} (logs: ${ZEEK_LOG_DIR})"
    local cmd=("${ZEEK_CMD}" -Cr "${ZEEK_PCAP}" -e "redef Log::default_logdir=\"${ZEEK_LOG_DIR}\";")
    if [[ "${ZEEK_SUDO}" == "1" ]]; then
      cmd=(sudo "${cmd[@]}")
    fi
    "${cmd[@]}" >"${ROOT_DIR}/logs/zeek.log" 2>&1 &
  else
    echo "Starting Zeek live on ${ZEEK_IFACE} (logs: ${ZEEK_LOG_DIR})"
    local cmd=("${ZEEK_CMD}" -i "${ZEEK_IFACE}" -e "redef Log::default_logdir=\"${ZEEK_LOG_DIR}\";")
    if [[ "${ZEEK_SUDO}" == "1" ]]; then
      cmd=(sudo "${cmd[@]}")
    fi
    "${cmd[@]}" >"${ROOT_DIR}/logs/zeek.log" 2>&1 &
  fi
  pids+=("$!")
}

start_router() {
  echo "Starting acquisition→normalizer router"
  SURICATA_LOG="${SURICATA_LOG}" \
  ZEEK_LOG_DIR="${ZEEK_LOG_DIR}" \
  NORMALIZER_OUTPUT="${NORMALIZER_OUTPUT}" \
    python3 "${ROOT_DIR}/acquisition/scripts/route_log.py" \
    >"${ROOT_DIR}/logs/acquisition-router.log" 2>&1 &
  pids+=("$!")
}

start_response_api() {
  echo "Starting Response API on :${PORT_RESPONSE}"
  uvicorn response.app:app \
    --host 0.0.0.0 --port "${PORT_RESPONSE}" --reload \
    >"${ROOT_DIR}/logs/response-api.log" 2>&1 &
  pids+=("$!")
}

start_presentation_api() {
  echo "Starting Presentation API on :${PORT_API}"
  uvicorn presentation.api.server:app \
    --host 0.0.0.0 --port "${PORT_API}" --reload \
    >"${ROOT_DIR}/logs/presentation-api.log" 2>&1 &
  pids+=("$!")
}

start_reasoner_api() {
  echo "Starting LLM Reasoner API on :${PORT_REASONER}"
  uvicorn app.api:app \
    --host 0.0.0.0 --port "${PORT_REASONER}" --reload \
    --app-dir "${ROOT_DIR}/llm_reasoner" \
    >"${ROOT_DIR}/logs/llm-reasoner.log" 2>&1 &
  pids+=("$!")
}

start_dashboard() {
  echo "Starting Streamlit dashboard on :${PORT_UI}"
  (cd "${ROOT_DIR}" && streamlit run presentation/ui/streamlit_app.py \
    --server.port "${PORT_UI}" --server.address 0.0.0.0) \
    >"${ROOT_DIR}/logs/streamlit.log" 2>&1 &
  pids+=("$!")
}

start_suricata
start_zeek
start_router
start_response_api
start_presentation_api
start_reasoner_api
start_dashboard

echo "Dashboard URL: http://localhost:${PORT_UI}"
echo "APIs: Presentation:${PORT_API} Reasoner:${PORT_REASONER} Response:${PORT_RESPONSE}"
echo "Acquisition logs: Suricata -> ${SURICATA_LOG}, Zeek -> ${ZEEK_LOG_DIR}, Normalizer output -> ${NORMALIZER_OUTPUT}"
echo "Logs: ${ROOT_DIR}/logs/{suricata.log,zeek.log,acquisition-router.log,response-api.log,presentation-api.log,llm-reasoner.log,streamlit.log}"
echo "Press Ctrl+C to stop all."

wait
