from response.policy_engine import PolicyEngine


def test_high_risk_blocks():
    engine = PolicyEngine()
    event = {"severity": 5, "src_ip": "1.1.1.1"}
    reasoning = {
        "threat_level": "high",
        "attack_type": "malware",
        "score_static": 5,
        "confidence": 0.9,
    }
    result = engine.evaluate(event, reasoning)
    assert "block_ip" in result["applied_actions"]
    assert not result["blocked_by_confidence"]


def test_low_confidence_blocks_actions():
    engine = PolicyEngine()
    event = {"severity": 5, "src_ip": "1.1.1.1"}
    reasoning = {
        "threat_level": "high",
        "attack_type": "malware",
        "score_static": 5,
        "confidence": 0.5,
    }
    result = engine.evaluate(event, reasoning)
    assert result["blocked_by_confidence"]
    assert result["applied_actions"] == []
