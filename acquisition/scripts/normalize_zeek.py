import json
import sys

FIELDS = None

def parse_line(line):
    global FIELDS

    if line.startswith("#fields"):
        FIELDS = line.strip().split("\t")[1:]
        return None

    if line.startswith("#") or FIELDS is None:
        return None

    values = line.strip().split("\t")
    raw = dict(zip(FIELDS, values))

    return {
        "timestamp": raw.get("ts"),
        "src_ip": raw.get("id.orig_h"),
        "dst_ip": raw.get("id.resp_h"),
        "proto": raw.get("proto"),
        "event_type": "zeek_log",
        "raw": raw
    }

