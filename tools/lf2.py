"""lf2.py: FILEDATA.BIN ("LF 2") archive: read, rebuild, extract.

Layout (docs/re/filedata.md): u32 magic 'LF 2', u32 data_start/4, u32 count, u32 header size (0x10),
then count x (u32 offset/4, u32 size). Files are stored raw, each starting on a 4-byte boundary.

    python -X utf8 tools/lf2.py extract FILEDATA.BIN OUTDIR
"""
import struct
import sys
from pathlib import Path

MAGIC = b"LF 2"


def read(data, pads=None):
    """Files in order. Pass a list as `pads` to also collect each file's alignment padding (leftover garbage
    in the original, kept so an unedited repack is byte-identical)."""
    magic, start4, count, hsize = struct.unpack_from("<4s3I", data)
    assert magic == MAGIC and hsize == 0x10, (magic, hsize)
    assert start4 * 4 == hsize + 8 * count, "data start doesn't follow the table"
    files = []
    for i in range(count):
        off4, size = struct.unpack_from("<2I", data, hsize + 8 * i)
        end = off4 * 4 + size
        files.append(bytes(data[off4 * 4:end]))
        if pads is not None:
            pads.append(bytes(data[end:end + (-size % 4)]))
    return files


def build(files, pads=None):
    """Repack. `pads` from read(); a file whose padding length changed gets zeros."""
    hsize = 0x10
    start = hsize + 8 * len(files)
    table, body = bytearray(), bytearray()
    for i, f in enumerate(files):
        off = start + len(body)
        table += struct.pack("<2I", off // 4, len(f))
        pad = pads[i] if pads and len(pads[i]) == -len(f) % 4 else b"\0" * (-len(f) % 4)
        body += f + pad
    return struct.pack("<4s3I", MAGIC, start // 4, len(files), hsize) + table + body


if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[1] != "extract":
        sys.exit(__doc__)
    out = Path(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)
    for i, f in enumerate(read(Path(sys.argv[2]).read_bytes())):
        (out / f"{i:04d}.bin").write_bytes(f)
