import sys
from pathlib import Path

import pytest

# Ensure project root on path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from normalizer.normalize_suricata import normalize_suricata
from normalizer.normalize_zeek import parse_line
from normalizer import normalize


def test_suricata_normalization():
    raw = {
        "timestamp": "2024-01-01T00:00:00.000000+0000",
        "src_ip": "10.0.0.1",
        "dst_ip": "10.0.0.2",
        "src_port": 1234,
        "dest_port": 80,
        "proto": "tcp",
        "alert": {"signature": "Test malware alert"},
    }
    event = normalize_suricata(raw)
    assert event["event_type"] == "suricata_alert"
    assert event["severity"] == 5  # malware keyword → severity 5
    assert event["src_ip"] == "10.0.0.1"
    assert event["dst_port"] == 80


def test_zeek_normalization():
    # Simulate Zeek header + data line
    header = "#fields\tts\tid.orig_h\tid.orig_p\tid.resp_h\tid.resp_p\tproto\t_path"
    data = "1700000000.0\t192.168.0.1\t5555\t192.168.0.2\t80\ttcp\thttp"
    parse_line(header)  # defines FIELDS
    event = parse_line(data)
    assert event["event_type"] == "zeek_http"
    assert event["severity"] >= 1
    assert event["src_ip"] == "192.168.0.1"
    assert event["dst_port"] == "80" or event["dst_port"] == 80  # zeek values often str


def test_protocol_map():
    assert normalize.protocol_map("tcp") == "TCP"
    assert normalize.protocol_map("dns") == "DNS"
    assert normalize.protocol_map(None) == "ANY"
