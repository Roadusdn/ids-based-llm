import json
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


def mark_for_review(event: Dict[str, Any] | None = None, reasoning: Dict[str, Any] | None = None, dry_run: bool = True, log_path: str = "/tmp/ids-llm-review.log"):
    """
    Append event/reasoning context to a review log file for human triage.
    """
    record = {"event": event or {}, "reasoning": reasoning or {}}
    if dry_run:
        logger.info("[dry-run] mark_for_review: %s", record)
        return {"dry_run": True, "record": record}

    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    return {"dry_run": False, "log_path": str(path)}


def open_ticket(payload: Dict[str, Any], url: str | None = None, dry_run: bool = True):
    """
    Ticket-style webhook (reuses notify semantics but separated for policy clarity).
    """
    from response.actions.notifier import send_webhook

    ticket_payload = {"type": "ticket", "payload": payload}
    return send_webhook(ticket_payload, url=url, dry_run=dry_run)
