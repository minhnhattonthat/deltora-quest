"""cmdtable.py: list the event-script command table in arm9 (docs/re/events.md): name -> handler address.

    python -X utf8 tools/debug/cmdtable.py [--lua tools/debug/cmds_all.lua] [NAME ...]
Entries are 16 bytes {name ptr, signature ptr, handler, flags}; found by locating the entry whose name is
"LoadExecEvent" and walking both ways while the name pointers stay valid ASCII strings in arm9.
--lua writes CMDS = {[handler] = "name", ...} for a probe to hook every command (see cmdlog.lua).
"""
import argparse
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = 0x02000000


def table():
    arm9 = (ROOT / "work/fs/arm9.bin").read_bytes()

    def name(ptr):
        o = ptr - BASE
        if not 0 <= o < len(arm9):
            return None
        m = re.match(rb"[A-Za-z][A-Za-z0-9_]{2,40}\x00", arm9[o:o + 42])
        return m.group()[:-1].decode() if m else None

    anchor = arm9.find(b"LoadExecEvent\x00")
    ptr = struct.pack("<I", BASE + anchor)
    at = next(k for k in range(0, len(arm9) - 16, 4) if arm9[k:k + 4] == ptr and
              name(struct.unpack_from("<I", arm9, k + 8)[0]) is None)
    lo = at
    while lo >= 16 and name(struct.unpack_from("<I", arm9, lo - 16)[0]):
        lo -= 16
    out = {}
    k = lo
    while name(struct.unpack_from("<I", arm9, k)[0]):
        n, _, h, _ = struct.unpack_from("<IIII", arm9, k)
        out[name(n)] = h
        k += 16
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*")
    ap.add_argument("--lua")
    a = ap.parse_args()
    t = table()
    for n, h in t.items():
        if not a.names or n in a.names:
            print(f"{h:#010x} {n}")
    print(len(t), "commands")
    if a.lua:
        body = "".join(f'  [{h:#010x}] = "{n}",\n' for n, h in t.items() if h & ~1)
        Path(a.lua).write_text("CMDS = {\n" + body + "}\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
