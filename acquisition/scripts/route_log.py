import json
import os
import time
import sys
from pathlib import Path

# ---------------------------
#  정상적으로 normalizer import 가능하게 설정
# ---------------------------
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

from normalizer.normalize_suricata import normalize_suricata
from normalizer.normalize_zeek import parse_line as parse_zeek_line

# 경로와 출력 위치를 env로 오버라이드 가능하게 설정
SURICATA_LOG = os.getenv("SURICATA_LOG", "/var/log/suricata/eve.json")
ZEEK_LOG_DIR = os.getenv("ZEEK_LOG_DIR", "/usr/local/zeek/logs/current/")
OUTPUT_PATH = os.getenv("NORMALIZER_OUTPUT", "/tmp/ids-llm-events.jsonl")


def tail_f(path):
    with open(path, "r") as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            yield line


def route_suricata():
    print("[*] Suricata log routing 시작")
    for line in tail_f(SURICATA_LOG):
        try:
            event = json.loads(line)
            norm = normalize_suricata(event)
            write_output(norm)
        except:
            continue


def route_zeek():
    print("[*] Zeek log routing 시작")
    log_files = ["conn.log", "dns.log", "http.log", "ssl.log"]

    open_files = {}
    for file in log_files:
        path = os.path.join(ZEEK_LOG_DIR, file)
        if os.path.exists(path):
            open_files[file] = tail_f(path)

    while True:
        for file, generator in open_files.items():
            try:
                line = next(generator)
                parsed = parse_zeek_line(line)
                if parsed:
                    write_output(parsed)
            except StopIteration:
                continue
            except:
                continue


def write_output(obj):
    """정규화된 이벤트를 JSON Lines 형식으로 기록"""
    with open(OUTPUT_PATH, "a") as f:
        f.write(json.dumps(obj) + "\n")


if __name__ == "__main__":
    from multiprocessing import Process

    p1 = Process(target=route_suricata)
    p2 = Process(target=route_zeek)

    p1.start()
    p2.start()

    p1.join()
    p2.join()
