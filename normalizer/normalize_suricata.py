import json

# normalizer/suricata_normalizer.py

from normalizer.normalize import to_common_schema


def normalize_suricata(event):
    extracted = {
        "timestamp": event.get("timestamp"),
        "src_ip": event.get("src_ip"),
        "dst_ip": event.get("dst_ip"),  # <-- dest_ip → dst_ip 수정됨
        "src_port": event.get("src_port"),
        "dst_port": event.get("dest_port"),
        "protocol": event.get("proto"),
        "alert": event.get("alert"),
        "event_type": "suricata_alert",
    }

    return to_common_schema("suricata", extracted)
