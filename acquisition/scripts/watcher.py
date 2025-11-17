import os
import time

SURICATA_LOG = "/var/log/suricata/eve.json"
ZEEK_LOG_DIR = "/usr/local/zeek/logs/current/"

def watch_file(path):
    print(f"[*] Watching file: {path}")
    last_size = 0
    while True:
        try:
            size = os.path.getsize(path)
            if size > last_size:
                print(f"[+] New data appended to {path}")
                last_size = size
        except FileNotFoundError:
            pass
        time.sleep(1)


def watch_directory(path):
    print(f"[*] Watching directory: {path}")
    known_files = set()

    while True:
        current_files = set(os.listdir(path))

        new_files = current_files - known_files
        if new_files:
            print(f"[+] New Zeek log files detected: {new_files}")

        known_files = current_files
        time.sleep(1)


if __name__ == "__main__":
    from multiprocessing import Process

    p1 = Process(target=watch_file, args=(SURICATA_LOG,))
    p2 = Process(target=watch_directory, args=(ZEEK_LOG_DIR,))

    p1.start()
    p2.start()

    p1.join()
    p2.join()

