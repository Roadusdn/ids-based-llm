#!/usr/bin/env bash
set -euo pipefail

# Start Presentation API, LLM Reasoner API, and Streamlit dashboard together.
# Ports are configurable via env: PORT_API (default 8000), PORT_REASONER (8001), PORT_UI (8501).

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${ROOT_DIR}:${PYTHONPATH:-}"

PORT_API="${PORT_API:-8000}"
PORT_REASONER="${PORT_REASONER:-8001}"
PORT_UI="${PORT_UI:-8501}"

need_cmds=(uvicorn streamlit)
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

start_presentation_api
start_reasoner_api
start_dashboard

echo "Dashboard URL: http://localhost:${PORT_UI}"
echo "Logs: ${ROOT_DIR}/logs/{presentation-api.log,llm-reasoner.log,streamlit.log}"
echo "Press Ctrl+C to stop all."

wait
