## Acquisition Scripts

본 디렉터리는 Suricata 및 Zeek에서 생성된 로그를
LLM 기반 분석 모듈로 전달하기 위한 전처리/감시 스크립트를 포함합니다.

---

## 파일 구성

scripts/
├── normalize_suricata.py # Suricata EVE JSON → 표준 JSON 정규화
├── normalize_zeek.py # Zeek TSV 로그 → 표준 JSON 정규화
├── route_logs.py # Suricata/Zeek 로그 → JSONL로 통합 라우팅
├── watcher.py # Suricata/Zeek 로그 실시간 감시
└── README.md

1. Suricata의 `eve.json`과  
2. Zeek의 `conn.log`, `dns.log`, `http.log`, `ssl.log`

에서 생성되는 로그를 실시간으로 감지하고  
LLM 분석 모듈이 사용할 수 있도록 표준 구조(JSON Lines)로 변환합니다.
