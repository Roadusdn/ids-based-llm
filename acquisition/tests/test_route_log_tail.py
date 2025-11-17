import importlib
import sys
import types
import threading
import time
from pathlib import Path


def load_route_log_with_stubs():
    """
    route_log.py has hard-coded imports to non-existent modules in this tree.
    We stub them so we can import and test tail_f behavior without changing production code.
    """
    # stub normalizer.normalizer_suricata
    mod_sur = types.ModuleType("normalizer.normalizer_suricata")
    mod_sur.normalize_suricata = lambda x: x
    sys.modules["normalizer.normalizer_suricata"] = mod_sur

    # stub normalizer.normalizer_zeek
    mod_zeek = types.ModuleType("normalizer.normalizer_zeek")
    mod_zeek.parse_line = lambda line: {"line": line}
    sys.modules["normalizer.normalizer_zeek"] = mod_zeek

    return importlib.import_module("acquisition.scripts.route_log")


def test_tail_f_yields_new_lines(tmp_path: Path):
    route_log = load_route_log_with_stubs()
    log_file = tmp_path / "test.log"
    log_file.write_text("")  # create file
    gen = route_log.tail_f(log_file)

    def writer():
        time.sleep(0.2)
        with open(log_file, "a") as f:
            f.write("hello\n")

    t = threading.Thread(target=writer)
    t.start()
    line = next(gen)
    t.join(timeout=1)

    assert "hello" in line
