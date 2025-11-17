import json

def normalize_suricata(event):
    return {
        "timestamp": event.get("timestamp"),
        "src_ip": event.get("src_ip"),
        "dst_ip": event.get("dest_ip"),
        "event_type": event.get("event_type", "suricata"),
        "raw": event
    }

