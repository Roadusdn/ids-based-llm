# Response Layer (4단계)

이 모듈은 LLM Reasoner의 판단 결과를 정책 기반으로 평가하여 실제 대응(또는 드라이런)까지 수행하는 계층입니다.

## 구성 요소
- `policy_engine.py`  
  - `policies.yaml`을 읽어 룰을 평가하고 실행할 액션 리스트를 결정합니다.  
  - `min_confidence` 게이트로 LLM 확신도가 낮으면 액션을 막습니다.
- `actions/`  
  - `firewall.py`: `block_ip`, `throttle_ip` (iptables).  
  - `zeekctl.py`: ZeekControl을 통한 세션 종료(`conn_id` 필요).  
  - `notifier.py`: 웹훅 알림 전송.  
  - `__init__.py`: 액션 이름 ↔ 실행 함수 매핑(`execute` 헬퍼).
- `config/policies.yaml`  
  - 기본값(dry_run, min_confidence)과 룰(조건별 액션)을 정의합니다.
- `app.py`  
  - FastAPI `/respond` 엔드포인트: {event, reasoning, webhook_url} 입력 → 정책 평가 → 액션 실행(dry-run/실행) → 결과 JSON 반환.
- `run.sh`  
  - Uvicorn 개발 서버 실행 스크립트.
- `tests/`  
  - `test_policy_engine.py`: 룰 매칭 및 confidence 게이트 테스트.
  - `conftest.py`: 프로젝트 루트 경로 세팅.

## 정책 설정
- 기본 정책 경로: `response/config/policies.yaml` (환경변수 `POLICY_PATH`로 재정의 가능).
- `default.dry_run`: `true`면 실제 조치 없이 로그만 남깁니다. 운영 전환 시 `false`로 변경하세요.
- `default.min_confidence`: LLM `confidence`가 이 값 미만이면 액션을 적용하지 않습니다.
- 룰 조건 키 예시: `threat_level`, `attack_type`, `severity_min`, `score_static_min`, `confidence_min`.

## API 사용 예시
```
POST /respond
{
  "event": {
    "severity": 5,
    "src_ip": "1.1.1.1",
    "raw": {"conn_id": "Cxyz"}
  },
  "reasoning": {
    "threat_level": "high",
    "attack_type": "malware",
    "score_static": 5,
    "confidence": 0.9
  },
  "webhook_url": "https://hooks.slack.com/..."
}
```
응답 예:
```
{
  "rule": "block_high_risk",
  "dry_run": true,
  "blocked_by_confidence": false,
  "actions": [
    {"action": "block_ip", "result": {...}},
    {"action": "terminate_session", "result": {...}},
    {"action": "notify", "result": {...}}
  ]
}
```

## 실행
```
./response/run.sh    # uvicorn response.app:app --host 0.0.0.0 --port 9001 --reload
```

## 운영 전 체크리스트
- `dry_run` → `false`로 전환하기 전에 비운영 환경에서 iptables/zeekctl/웹훅 동작 검증.
- Reasoner 출력에 `confidence`가 포함되고 정규화 이벤트에 `severity`/`src_ip` 등이 채워지는지 확인.
- 필요 시 정책 룰 확장(예: 시간대, allowlist, 공격 타입별 세분화).
