## LLM-Network-IDS – Reasoner Layer (2단계)

본 저장소는 Suricata·Zeek 기반 네트워크 침입 탐지 시스템에서  
LLM 기반 위협 분석(Reasoning Layer) 구현한 모듈이다.  

이 모듈은 4단계 전체 아키텍처 중 2단계를 담당한다.

# 1. Features (핵심 기능)

## 공통 스키마 기반 로그 정규화 지원
- Suricata(EVE JSON), Zeek(conn/http/ssl 등)의 다양한 로그를  
  **단일 Event 스키마**로 통합 처리할 수 있도록 설계.

## 정적 분석(Static Scoring)
- Suricata Alert 개수 기반 기본 위험 점수  
- Port scan을 탐지하기 위한 IP별 포트 다양성 분석  
- 저비용 휴리스틱을 활용한 1차 필터링 기능

## Prompt 기반 LLM Reasoning
- 10초 단위 Event Batch  
- 이벤트 전체 구조 정보 + 정적 점수를 포함한 Prompt 생성  
- LLM(기본: Ollama + Phi3-mini)로 위협 수준·공격 유형 추론

## JSON 기반 표준 Response 생성
LLM 분석 결과 또는 Fallback을 다음 스키마로 반환:

json
{
  "threat_level": "low | medium | high | critical",
  "attack_type": "string",
  "reasoning": "string",
  "recommended_actions": ["block_ip", "alert_admin", ...],
  "score_static": 3,
  "involved_ips": []
}


# FastAPI API 제공

- /analyze 엔드포인트

- Event 리스트 입력 → ThreatResult 출력

# Unit Test 포함

- Static Score 테스트

- Prompt 생성 테스트

- End-to-End Reasoning 테스트

- Ollama 서버 연결성 테스트
