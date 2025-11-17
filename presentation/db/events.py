# presentation/db/events.py

import sqlite3
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "presentation" / "db" / "events.db"


def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    return conn


def save_event(event):
    """LLM까지 적용된 최종 이벤트를 DB에 저장"""
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT OR REPLACE INTO events
        (id, timestamp, src_ip, dst_ip, src_port, dst_port, protocol,
         event_type, severity, category, raw_source, raw_json,
         llm_threat_level, llm_attack_type, llm_confidence,
         llm_summary, llm_recommendation_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        event["event_id"],
        event["timestamp"],
        event["src_ip"],
        event["dst_ip"],
        event["src_port"],
        event["dst_port"],
        event["protocol"],
        event["event_type"],
        event["severity"],
        event["category"],
        event["raw_source"],
        json.dumps(event["raw"]),
        event.get("llm_threat_level"),
        event.get("llm_attack_type"),
        event.get("llm_confidence"),
        event.get("llm_summary"),
        json.dumps(event.get("llm_recommendation")),
    ))

    conn.commit()
    conn.close()


# -------------------------------
# 조회 함수들
# -------------------------------
def query_recent_events(limit=50, min_severity=1):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(f"""
        SELECT id, timestamp, src_ip, dst_ip, src_port, dst_port,
               protocol, event_type, severity, category,
               llm_threat_level, llm_attack_type, llm_confidence
        FROM events
        WHERE severity >= ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (min_severity, limit))

    rows = cur.fetchall()
    conn.close()

    keys = ["id", "timestamp", "src_ip", "dst_ip", "src_port", "dst_port",
            "protocol", "event_type", "severity", "category",
            "llm_threat_level", "llm_attack_type", "llm_confidence"]

    return [dict(zip(keys, row)) for row in rows]


def query_event_by_id(event_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM events
        WHERE id = ?
    """, (event_id,))

    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    cols = [desc[0] for desc in cur.description]
    return dict(zip(cols, row))


def query_overview_stats():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM events")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM events WHERE severity >= 4")
    high = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM events WHERE severity = 3")
    medium = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM events WHERE severity <= 2")
    low = cur.fetchone()[0]

    conn.close()

    return {
        "total": total,
        "high": high,
        "medium": medium,
        "low": low
    }


def query_timeline(minutes=60):
    """최근 60분 동안 시간대별 이벤트 수"""
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(f"""
        SELECT substr(timestamp, 1, 16) as ts, COUNT(*)
        FROM events
        GROUP BY ts
        ORDER BY ts DESC
        LIMIT ?
    """, (minutes,))

    rows = cur.fetchall()
    conn.close()

    return {r[0]: r[1] for r in rows}

