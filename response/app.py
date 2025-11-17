import logging
import os
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from response import policy_engine
from response.actions import execute

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="IDS Response API", version="0.1.0")


class EventModel(BaseModel):
    event_id: str | None = None
    severity: int | None = None
    src_ip: str | None = None
    dst_ip: str | None = None
    raw: Dict[str, Any] | None = None


class ReasoningModel(BaseModel):
    threat_level: str | None = None
    attack_type: str | None = None
    recommended_actions: list[str] | None = None
    reasoning: str | None = None
    score_static: int | None = None
    confidence: float | None = 1.0


class RequestModel(BaseModel):
    event: EventModel
    reasoning: ReasoningModel
    webhook_url: str | None = None


@app.post("/respond")
def respond(req: RequestModel):
    evaluator = policy_engine.PolicyEngine()
    event_data = req.event.model_dump()
    reasoning_data = req.reasoning.model_dump()
    result = evaluator.evaluate(event_data, reasoning_data)
    dry_run = result.get("dry_run", False)

    responses = []
    for action_name in result.get("applied_actions", []):
        params = {"dry_run": dry_run}
        if action_name in ("block_ip", "throttle_ip"):
            params["ip"] = req.event.src_ip or req.event.dst_ip
        if action_name == "terminate_session":
            params["conn_id"] = (req.event.raw or {}).get("conn_id", "")
        if action_name == "notify":
            params["payload"] = {"event": event_data, "reasoning": reasoning_data}
            params["url"] = req.webhook_url or os.environ.get("WEBHOOK_URL")

        try:
            res = execute(action_name, **params)
            responses.append({"action": action_name, "result": res})
        except Exception as e:
            logger.exception("action failed: %s", action_name)
            responses.append({"action": action_name, "error": str(e)})

    return {
        "rule": result.get("rule"),
        "dry_run": dry_run,
        "blocked_by_confidence": result.get("blocked_by_confidence"),
        "actions": responses,
    }
