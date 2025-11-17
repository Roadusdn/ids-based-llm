from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any, List

class Event(BaseModel):
    timestamp: datetime
    src_ip: str
    src_port: Optional[int] = None
    dst_ip: str
    dst_port: Optional[int] = None
    protocol: Optional[str] = None
    event_type: str        # "suricata_alert", "zeek_conn" 등
    severity: int = 1
    category: Optional[str] = None
    raw: Dict[str, Any]

class ThreatResult(BaseModel):
    threat_level: str
    attack_type: str
    reasoning: str
    recommended_actions: List[str]
    score_static: int
    involved_ips: List[str]

