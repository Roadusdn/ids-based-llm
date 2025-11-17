import json
from pathlib import Path
from llm_reasoner.app.analyzer import ThreatAnalyzer
from llm_reasoner.app.schemas import Event

def load_events():
    path = Path(__file__).parent / "sample_events.json"
    with open(path, "r") as f:
        raw = json.load(f)
    return [Event(**e) for e in raw]

def test_static_score():
    events = load_events()
    analyzer = ThreatAnalyzer()
    score = analyzer.static_score(events)
    assert score >= 2   # suricata_alert 1개 이상 → 최소 2점

def test_prompt_generation():
    events = load_events()
    analyzer = ThreatAnalyzer()
    score = analyzer.static_score(events)
    prompt = analyzer.make_prompt(events, score)
    assert "suricata_alert" in prompt
    assert "static_score:" in prompt

def test_threat_analysis_end_to_end():
    """
    LLM이 실제 JSON을 반환하지 않더라도
    최소한 analyzer 내부 예외처리가 정상 동작하는지 확인
    """
    events = load_events()
    analyzer = ThreatAnalyzer()

    result = analyzer.analyze(events)
    assert result.threat_level in ["none", "low", "medium", "high", "critical"]
    assert isinstance(result.attack_type, str)
    assert isinstance(result.reasoning, str)

