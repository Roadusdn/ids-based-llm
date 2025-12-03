# IDS-Based-LLM (End-to-End 4계층)

Suricata/Zeek 로그를 정규화하고 LLM으로 위협을 해석·상관분석한 뒤, 정책 기반 Response와 대시보드까지 연결하는 4단계 IDS 파이프라인입니다.

## 레이어별 구성
- **Acquisition (수집/탐지)**: `acquisition/`  
  - Suricata·Zeek 서비스 데몬, EVE JSON/TSV 수집.
- **Normalizer**: `normalizer/`  
  - Suricata/Zeek 로그를 공통 스키마로 변환.
- **LLM Reasoner**: `llm_reasoner/`  
  - 배치 단위(예: 10초) 이벤트 묶음 → 프롬프트 생성 → 위협 수준/공격 유형/추천 액션 산출.
- **Response**: `response/`  
  - 정책(`config/policies.yaml`) 평가 후 액션(iptables 차단, Zeek 세션 종료, 웹훅 알림) 실행. FastAPI `/respond`.
- **Presentation**: `presentation/`  
  - ELK/Streamlit 기반 대시보드(LLM 결과·정책 적용 현황 시각화).

## 빠른 시작 (센서 VM)
```bash
# 1) 의존성/venv/필수 패키지 설치 (이미 설치돼 있으면 건너뜀)
./setup-sensor.sh               # 기본은 apt+pip, Suricata/Zeek 미설치
INSTALL_SURICATA=1 INSTALL_ZEEK=1 ./setup-sensor.sh  # 필요 시 IDS 엔진까지 빌드

# 2) venv 활성화
source .venv/bin/activate

# 3) 모든 레이어 실행
SURICATA_IFACE=eth0 ZEEK_IFACE=eth0 \
NORMALIZER_OUTPUT=/tmp/ids-llm-events.jsonl \
PORT_API=8000 PORT_REASONER=8001 PORT_RESPONSE=9001 PORT_UI=8501 \
SURICATA_SUDO=1 ZEEK_SUDO=1 \
./run-all.sh
# 대시보드: http://<센서IP>:8501
```

### 개별 실행/테스트
- Reasoner API 단독: `uvicorn app.api:app --host 0.0.0.0 --port 8001 --app-dir llm_reasoner`
- Response API 단독: `./response/run.sh` (포트 9001)
- 테스트:  
  - `pytest llm_reasoner/tests/test_analyzer.py`  
  - `pytest response/tests`  
  - `pytest normalizer/tests`  
  - `pytest acquisition/tests`  
  - `pytest presentation/tests`  
  - Ollama 연결 필요: `pytest llm_reasoner/tests/test_llm_client.py`

## 정책 기반 자동 대응
- 정책 파일: `response/config/policies.yaml`
- 기본값: `dry_run: false` (iptables/zeekctl/웹훅 실제 적용). 안전 테스트 시 `true`로 바꿔 실행.
- LLM `confidence`가 `min_confidence` 미만이면 액션 미적용.
- 지원 액션: `block_ip`, `throttle_ip`, `terminate_session`, `notify`, `quarantine_ip`, `mark_for_review`, `open_ticket`

## 데이터 스키마 (정규화)
```json
{
  "timestamp": "...",
  "src_ip": "...",
  "dst_ip": "...",
  "protocol": "HTTP/TLS/ANY",
  "event_type": "suricata_alert | zeek_http | system | ...",
  "severity": 1,
  "raw": { ... }
}
```

## 전체 흐름
```
[NIC/PCAP] → Suricata/Zeek → Normalizer → LLM Reasoner → Response API → Dashboard(ELK/Streamlit)
```

## 실험(예: VMware/WSL) 체크리스트
- 네트워크: 센서/공격자/타깃 VM을 동일 브리지/미러링으로 연결해 센서 NIC가 트래픽을 관찰하는지 확인 (`tcpdump -i <iface>`).
- 입력: pcap 재생(hping, Metasploit 등) → Suricata/Zeek 로그 쌓이는지 확인.
- Normalizer: `acquisition/scripts/route_log.py`가 `SURICATA_LOG`/`ZEEK_LOG_DIR`를 읽어 `NORMALIZER_OUTPUT`(기본 `/tmp/ids-llm-events.jsonl`)에 이벤트 적재하는지 확인.
- Reasoner: Ollama(또는 지정 LLM) 구동 후 `/analyze` 호출 또는 end-to-end 흐름 확인.
- Response: `dry_run` 설정과 정책 적용 여부를 `logs/response-api.log` 및 iptables/웹훅 결과로 확인.
- Presentation: Streamlit 대시보드(`:8501`)나 ELK로 정규화+LLM+Response 결과 확인.
