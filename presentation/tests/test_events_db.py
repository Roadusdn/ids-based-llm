import sqlite3
import sys
from pathlib import Path

# Ensure project root on path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from presentation.db import events


def setup_temp_db(tmp_path: Path):
    # point DB_PATH to temp file
    events.DB_PATH = tmp_path / "events.db"
    schema_path = ROOT / "presentation" / "db" / "schema.sql"
    conn = events.get_conn()
    with open(schema_path, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


def test_save_and_query_event(tmp_path: Path):
    setup_temp_db(tmp_path)
    event = {
        "event_id": "e1",
        "timestamp": "2024-01-01T00:00:00Z",
        "src_ip": "1.1.1.1",
        "dst_ip": "2.2.2.2",
        "src_port": 12345,
        "dst_port": 80,
        "protocol": "TCP",
        "event_type": "suricata_alert",
        "severity": 5,
        "category": "IDS Alert",
        "raw_source": "suricata",
        "raw": {"foo": "bar"},
        "llm_threat_level": "high",
        "llm_attack_type": "malware",
        "llm_confidence": 0.9,
        "llm_summary": "test",
        "llm_recommendation": {"actions": ["block_ip"]},
    }
    events.save_event(event)

    recent = events.query_recent_events(limit=10, min_severity=1)
    assert len(recent) == 1
    assert recent[0]["src_ip"] == "1.1.1.1"

    by_id = events.query_event_by_id("e1")
    assert by_id["id"] == "e1"
    stats = events.query_overview_stats()
    assert stats["total"] == 1
    assert stats["high"] == 1


def test_query_timeline(tmp_path: Path):
    setup_temp_db(tmp_path)
    event = {
        "event_id": "e1",
        "timestamp": "2024-01-01T00:00:00Z",
        "src_ip": "1.1.1.1",
        "dst_ip": "2.2.2.2",
        "src_port": 1111,
        "dst_port": 80,
        "protocol": "TCP",
        "event_type": "suricata_alert",
        "severity": 3,
        "category": "IDS Alert",
        "raw_source": "suricata",
        "raw": {},
        "llm_threat_level": "medium",
        "llm_attack_type": "scan",
        "llm_confidence": 0.7,
        "llm_summary": "test",
        "llm_recommendation": {},
    }
    events.save_event(event)
    timeline = events.query_timeline(minutes=10)
    assert len(timeline) >= 1
