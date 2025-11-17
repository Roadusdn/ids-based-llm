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

## 빠른 시작
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r llm_reasoner/requirements.txt
pip install -r response/requirements.txt
# 필요 시 다른 모듈 요구사항도 설치
```

### Response API 실행
```bash
./response/run.sh  # uvicorn response.app:app --host 0.0.0.0 --port 9001 --reload
```

### Reasoner 테스트
```bash
pytest test_reasoner.py
```

### Response 정책 테스트
```bash
pytest response/tests
```

## 정책 기반 자동 대응
- 정책 파일: `response/config/policies.yaml`
- 기본값: `dry_run: true` (실제 조치 없이 로그만). 운영 전환 시 `false`.
- LLM `confidence`가 `min_confidence` 미만이면 액션 미적용.

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
