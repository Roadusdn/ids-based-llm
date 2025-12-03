
#!/usr/bin/env bash
set -euo pipefail

# Run end-to-end validation across all layers using existing pytest suites.
# Usage:
#   ./run_full_validation.sh           # Core suites
#   INCLUDE_LLM_CLIENT=1 ./run_full_validation.sh  # Include Ollama-dependent client test

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${ROOT_DIR}:${PYTHONPATH:-}"

run_suite() {
  local suite="$1"
  echo "\n=== Running ${suite} ==="
  pytest "${suite}"
}

run_suite "llm_reasoner/tests/test_analyzer.py"
run_suite "response/tests"
run_suite "normalizer/tests"
run_suite "acquisition/tests"
run_suite "presentation/tests"

if [[ "${INCLUDE_LLM_CLIENT:-1}" == "1" ]]; then
  run_suite "llm_reasoner/tests/test_llm_client.py"
else
  echo "\nSkipping llm_reasoner/tests/test_llm_client.py (set INCLUDE_LLM_CLIENT=1 to include)"
fi
