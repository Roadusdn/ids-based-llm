import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from response import policy_engine
import response.app as app_module


def test_respond_function(monkeypatch):
    # Force dry-run and stub execute to avoid system commands
    def fake_eval(self, event, reasoning):
        return {
            "rule": "block_high_risk",
            "dry_run": True,
            "blocked_by_confidence": False,
            "applied_actions": ["block_ip", "terminate_session", "notify"],
        }

    monkeypatch.setattr(policy_engine.PolicyEngine, "evaluate", fake_eval)
    monkeypatch.setattr(app_module, "execute", lambda name, **kwargs: {"mocked": name})

    req = app_module.RequestModel(
        event={"severity": 5, "src_ip": "1.1.1.1", "dst_ip": "2.2.2.2", "raw": {"conn_id": "C123"}},
        reasoning={
            "threat_level": "high",
            "attack_type": "malware",
            "recommended_actions": ["block_ip"],
            "reasoning": "test",
            "score_static": 5,
            "confidence": 0.9,
        },
        webhook_url="https://example.com/webhook",
    )

    result = app_module.respond(req)
    assert result["rule"] == "block_high_risk"
    assert result["dry_run"] is True
    assert any(a["action"] == "block_ip" for a in result["actions"])
