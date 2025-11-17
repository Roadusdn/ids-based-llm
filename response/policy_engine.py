import os
from typing import Any, Dict, List, Tuple

import yaml


class PolicyEngine:
    """Load policies and decide which actions to take."""

    def __init__(self, policy_path: str | None = None):
        self.policy_path = policy_path or os.environ.get(
            "POLICY_PATH", "response/config/policies.yaml"
        )
        self.policies = self._load_policies()

    def _load_policies(self) -> Dict[str, Any]:
        with open(self.policy_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        data = data or {}
        data.setdefault("default", {})
        data.setdefault("rules", [])
        return data

    def evaluate(self, event: Dict[str, Any], reasoning: Dict[str, Any]) -> Dict[str, Any]:
        """
        event: normalized event (severity, src_ip, dst_ip ...)
        reasoning: output from reasoner (threat_level, attack_type, recommended_actions, reasoning, score_static, confidence)
        """
        matched_actions: List[str] = []
        matched_rule = None

        for rule in self.policies.get("rules", []):
            if self._match_rule(rule, event, reasoning):
                matched_rule = rule.get("name")
                matched_actions = rule.get("actions", [])
                break

        default_cfg = self.policies.get("default", {})
        dry_run = bool(default_cfg.get("dry_run", False))
        min_confidence = float(default_cfg.get("min_confidence", 0.0))
        confidence = float(reasoning.get("confidence", 1.0))

        # Confidence gate
        effective_actions = matched_actions if confidence >= min_confidence else []

        return {
            "rule": matched_rule,
            "dry_run": dry_run,
            "applied_actions": effective_actions,
            "blocked_by_confidence": confidence < min_confidence,
            "context": {
                "event": event,
                "reasoning": reasoning,
                "min_confidence": min_confidence,
                "confidence": confidence,
            },
        }

    def _match_rule(
        self, rule: Dict[str, Any], event: Dict[str, Any], reasoning: Dict[str, Any]
    ) -> bool:
        cond = rule.get("if", {})

        def _matches_list(value: Any, expected: List[Any] | None) -> bool:
            if expected is None:
                return True
            return value in expected

        threat_level = reasoning.get("threat_level")
        attack_type = reasoning.get("attack_type")
        severity = int(event.get("severity", 0))
        score_static = int(reasoning.get("score_static", 0))

        return all(
            [
                _matches_list(threat_level, cond.get("threat_level")),
                _matches_list(attack_type, cond.get("attack_type")),
                severity >= cond.get("severity_min", 0),
                score_static >= cond.get("score_static_min", 0),
                float(reasoning.get("confidence", 1.0))
                >= float(cond.get("confidence_min", 0.0)),
            ]
        )


def evaluate(event: Dict[str, Any], reasoning: Dict[str, Any]) -> Dict[str, Any]:
    return PolicyEngine().evaluate(event, reasoning)
