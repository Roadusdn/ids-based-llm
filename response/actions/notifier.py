import logging
from typing import Dict, Any

import httpx

logger = logging.getLogger(__name__)


def send_webhook(payload: Dict[str, Any], url: str | None = None, dry_run: bool = True):
    if url is None:
        logger.info("notify skipped: no webhook url provided")
        return {"skipped": True}
    if dry_run:
        logger.info("[dry-run] notify payload: %s", payload)
        return {"dry_run": True, "payload": payload}
    try:
        resp = httpx.post(url, json=payload, timeout=5)
        return {"status_code": resp.status_code, "text": resp.text}
    except httpx.HTTPError as e:
        logger.error("notify failed: %s", e)
        return {"error": str(e)}
