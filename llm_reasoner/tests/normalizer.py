from llm_reasoner.app.normalizer import normalize_suricata

def test_normalize_suricata():
    raw = {
        "timestamp": "2025-11-17T12:00:00",
        "src_ip": "1.1.1.1",
        "dest_ip": "8.8.8.8",
        "event_type": "alert",
        "alert": {"severity": 3}
    }

    event = normalize_suricata(raw)
    assert event.src_ip == "1.1.1.1"
    assert event.dst_ip == "8.8.8.8"
    assert event.severity == 3

