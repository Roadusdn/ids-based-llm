import json
from typing import List
from .schemas import Event, ThreatResult
from .llm_client import LLMClient


class ThreatAnalyzer:
    def __init__(self):
        self.llm = LLMClient()

    # ------------------------------
    # 1) Static Score
    # ------------------------------
    def static_score(self, events: List[Event]) -> int:
        score = 0

        # Suricata alerts
        alerts = [e for e in events if e.event_type == "suricata_alert"]
        if len(alerts) >= 1:
            score += 2
        if len(alerts) >= 3:
            score += 2

        # Port scan heuristic
        port_map = {}
        for e in events:
            port_map.setdefault(e.src_ip, set()).add(e.dst_port)

        max_port_variants = max(
            (len(v) for v in port_map.values()), 
            default=0
        )

        if max_port_variants > 20:
            score += 3
        elif max_port_variants > 10:
            score += 1

        return score

    # ------------------------------
    # 2) Prompt template generator
    # ------------------------------
    def make_prompt(self, events: List[Event], static_score: int) -> str:
        events_dict = [e.model_dump() for e in events]

        return f"""
당신은 네트워크 보안 분석가입니다.
아래는 최근 10초 동안 수집된 Suricata/Zeek 이벤트입니다.

[정적 분석 요약]
static_score: {static_score}

[이벤트 목록]
{json.dumps(events_dict, indent=2, default=str)}

위 정보를 바탕으로 아래 JSON 형식으로 반드시 응답하세요:

{{
  "threat_level": "none | low | medium | high | critical",
  "attack_type": "",
  "reasoning": "",
  "recommended_actions": [],
  "involved_ips": []
}}
"""

    # ------------------------------
    # 3) Full analysis pipeline
    # ------------------------------
    def analyze(self, events: List[Event]) -> ThreatResult:
        score = self.static_score(events)
        prompt = self.make_prompt(events, score)

        # LLM call
        raw_text = self.llm.generate(prompt)

        # Try to extract JSON
        try:
            json_start = raw_text.index("{")
            json_end = raw_text.rindex("}") + 1
            extracted_json = raw_text[json_start:json_end]
            data = json.loads(extracted_json)
        except Exception:
            # fallback
            data = {
                "threat_level": "low",
                "attack_type": "unknown",
                "reasoning": raw_text,
                "recommended_actions": ["alert_admin"],
                "involved_ips": []
            }

        return ThreatResult(
            threat_level=str(data.get("threat_level", "low") or "low"),
            attack_type=str(data.get("attack_type", "unknown") or "unknown"),
            reasoning=str(data.get("reasoning", "") or ""),
            recommended_actions=data.get("recommended_actions") or [],
            score_static=score,
            involved_ips=data.get("involved_ips") or []
        )

