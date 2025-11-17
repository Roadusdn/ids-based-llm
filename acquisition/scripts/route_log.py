import json
import os
import time
from normalize_suricata import normalize_suricata
from normalize_zeek import parse_line as parse_zeek_line

SURICATA_LOG = "/var/log/suricata/eve.json"
ZEEK_LOG_DIR = "/usr/local/zeek/logs/current/"
OUTPUT_PATH = "/tmp/ids-llm-events.jsonl"  # 이후 LLM 모듈로 전달할 파일

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

