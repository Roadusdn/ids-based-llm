import json
import uuid
from llm_reasoner.app.analyzer import ThreatAnalyzer
from llm_reasoner.app.schemas import Event
from presentation.db.events import save_event

# JSONL 파일에서 첫 번째 이벤트 읽기
line = open("/tmp/ids-llm-events.jsonl").readlines()[0]
event_raw = json.loads(line)

# dict → Event 모델 변환
event = Event(**event_raw)

# Reasoner 실행
ta = ThreatAnalyzer()
result = ta.analyze([event])

# DB 저장
save_event({
    "event_id": str(uuid.uuid4()),     # 필수
    "raw_source": "suricata",          # ★ 새로 추가!
    **event_raw,
    "llm_threat_level": result.threat_level,
    "llm_attack_type": result.attack_type,
    "reasoning": result.reasoning,
    "recommended_actions": result.recommended_actions
})

print("OK saved.")


