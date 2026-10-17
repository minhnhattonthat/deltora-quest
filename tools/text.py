"""text.py: the dialogue/system text (FILEDATA files 2178-2200) <-> script/*.json.

File layout (docs/re/text.md): u32 offsets to each string, then strings of 16-bit LE codes. Every string starts
with two header words (speaker/portrait; 0 = none) and ends with FFFD.

    python -X utf8 tools/text.py dump            # write script/<file>.json for files that don't exist yet
    python -X utf8 tools/text.py dump --refresh  # re-decode `jp` (after a table fix); keeps `en`, prints changed ids
"""
import argparse
import json
import struct
import sys
from pathlib import Path

import ndspy.rom

import build
import lf2
from tbl import Table

ROOT = build.ROOT
SCRIPT = ROOT / "script"
TEXT_FILES = range(2178, 2201)
LANG = "en"


def table(name="jp"):
    return Table.load(ROOT / f"tbl/{name}.tbl")


def split(data):
    """[(header bytes, body bytes incl. FFFD)] for one text file."""
    first = struct.unpack_from("<I", data)[0]
    offs = list(struct.unpack_from(f"<{first // 4}I", data)) + [len(data)]
    return [(data[a:a + 4], data[a + 4:b]) for a, b in zip(offs, offs[1:])]


def join(strings):
    """Inverse of split: [(header, body)] -> file bytes."""
    table_size = 4 * len(strings)
    offs, body = [], bytearray()
    for hdr, s in strings:
        offs.append(table_size + len(body))
        body += hdr + s
    return struct.pack(f"<{len(offs)}I", *offs) + body


def decode(t, body):
    text, used = t.decode(body, 0)
    assert used == len(body) and text.endswith("{end}"), (text, used, len(body))
    return text[:-len("{end}")]


def encode(t, text):
    return t.encode(text + "{end}")


def rom_files():
    return lf2.read(ndspy.rom.NintendoDSRom(build.ROM.read_bytes()).files[build.FILEDATA])


def dump(refresh=False):
    t = table()
    files = rom_files()
    SCRIPT.mkdir(exist_ok=True)
    for n in TEXT_FILES:
        path = SCRIPT / f"{n}.json"
        old = {e["id"]: e for e in json.loads(path.read_text(encoding="utf-8"))} if path.exists() else None
        if old is not None and not refresh:
            continue
        rows = []
        for i, (hdr, body) in enumerate(split(files[n])):
            e = {"id": f"{n}_{i:03d}", "hdr": hdr.hex().upper(), "jp": decode(t, body), LANG: ""}
            if old and e["id"] in old:
                prev = old[e["id"]]
                if prev["jp"] != e["jp"] and prev.get(LANG):
                    print("jp changed, re-check translation:", e["id"])
                e = {**prev, "hdr": e["hdr"], "jp": e["jp"]}
            rows.append(e)
        path.write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["dump"])
    ap.add_argument("--refresh", action="store_true")
    a = ap.parse_args()
    dump(a.refresh)
