# normalizer/zeek_normalizer.py

from normalizer.normalize import to_common_schema

FIELDS = None

def parse_line(line):
    global FIELDS

    # 필드 정의
    if line.startswith("#fields"):
        FIELDS = line.strip().split("\t")[1:]
        return None

    # 주석 또는 필드 미정의일 때 무시
    if line.startswith("#") or FIELDS is None:
        return None

    values = line.strip().split("\t")
    raw = dict(zip(FIELDS, values))

    # Zeek 로그 타입 확인
    log_type = "zeek_" + raw.get("_path", "log") if "_path" in raw else "zeek_log"

    extracted = {
        "timestamp": raw.get("ts"),
        "src_ip": raw.get("id.orig_h"),
        "dst_ip": raw.get("id.resp_h"),
        "src_port": raw.get("id.orig_p"),
        "dst_port": raw.get("id.resp_p"),
        "protocol": raw.get("proto"),
        "event_type": log_type,
        "raw": raw
    }

    return to_common_schema("zeek", extracted)


