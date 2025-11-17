# normalizer/normalize.py

import uuid
from datetime import datetime


def generate_event_id():
    return str(uuid.uuid4())


def normalize_timestamp(ts):
    """UNIX timestamp 또는 문자열 일 경우 ISO8601로 변환"""
    if ts is None:
        return None

    # Suricata timestamp → "2025-02-18T12:45:30.123456+0000"
    if isinstance(ts, str):
        try:
            # Suricata 기본 timestamp 형식
            return datetime.fromisoformat(ts.replace("Z", "+00:00")).isoformat()
        except:
            return ts  # 변환 실패하면 원본 유지

    # Zeek timestamp (float)
    try:
        return datetime.utcfromtimestamp(float(ts)).isoformat() + "Z"
    except:
        return None


def protocol_map(proto):
    if not proto:
        return "ANY"
    p = proto.lower()
    if p in ["tcp", "udp", "icmp"]:
        return p.upper()
    if p in ["http", "dns", "tls", "ssl"]:
        return p.upper()
    return p.upper()


def severity_from_suricata(alert):
    if alert is None:
        return 2
    sig = alert.get("signature", "").lower()
    if any(x in sig for x in ["malware", "exploit", "trojan"]):
        return 5
    if any(x in sig for x in ["scan", "probe"]):
        return 3
    return 2


def severity_from_zeek(event_type):
    if "http" in event_type:
        return 2
    if "dns" in event_type:
        return 1
    if "ssl" in event_type:
        return 3
    return 1


def category_from_type(event_type):
    if "suricata" in event_type:
        return "IDS Alert"
    if "http" in event_type:
        return "Web"
    if "dns" in event_type:
        return "DNS"
    if "conn" in event_type:
        return "Connection"
    return "General"


def to_common_schema(source, extracted):
    """Suricata/Zeek 필드 → 공통 스키마 변환"""

    event = {}
    event["event_id"] = generate_event_id()
    event["timestamp"] = normalize_timestamp(extracted.get("timestamp"))
    event["src_ip"] = extracted.get("src_ip")
    event["dst_ip"] = extracted.get("dst_ip")
    event["src_port"] = extracted.get("src_port")
    event["dst_port"] = extracted.get("dst_port")
    event["protocol"] = protocol_map(extracted.get("protocol"))
    event["event_type"] = extracted.get("event_type", source)
    event["raw_source"] = source
    event["raw"] = extracted

    # severity
    if source == "suricata":
        event["severity"] = severity_from_suricata(extracted.get("alert"))
    else:
        event["severity"] = severity_from_zeek(event["event_type"])

    # category
    event["category"] = category_from_type(event["event_type"])

    return event
