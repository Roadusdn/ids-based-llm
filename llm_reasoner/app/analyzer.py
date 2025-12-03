import json
from typing import List
from .schemas import Event, ThreatResult
from .llm_client import LLMClient


class ThreatAnalyzer:
    def __init__(self, model: str | None = None, api_url: str | None = None):
        # model/api_url은 기본값(Ollama) 사용, 필요 시 인자로 또는 env로 오버라이드
        self.llm = LLMClient(url=api_url, model=model)

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

        allowed_actions = [
            "block_ip",
            "throttle_ip",
            "terminate_session",
            "notify",
            "quarantine_ip",
            "mark_for_review",
            "open_ticket",
        ]
        example_json = {
            "threat_level": "high",
            "attack_type": "port_scan",
            "reasoning": "Summary of why this is high risk",
            "recommended_actions": ["block_ip", "notify"],
            "involved_ips": ["1.2.3.4"]
        }

        return f"""
당신은 네트워크 보안 분석가입니다.
아래는 최근 10초 동안 수집된 Suricata/Zeek 이벤트입니다.

[정적 분석 요약]
static_score: {static_score}

[이벤트 목록]
{json.dumps(events_dict, indent=2, default=str)}

반드시 JSON 객체만 출력하세요. JSON 밖의 여분 텍스트나 설명은 금지합니다.
규칙:
- threat_level 은 none|low|medium|high|critical 중 하나
- recommended_actions 값은 {allowed_actions} 중에서만 선택 (필요 시 여러 개)
- involved_ips 는 공격에 연관된 IP 배열

출력 예시 (형식만 참고, 내용은 실제 이벤트 기반으로 작성):
{json.dumps(example_json, indent=2)}
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
                "recommended_actions": ["mark_for_review"],
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
