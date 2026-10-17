# ROM layout and FILEDATA.BIN

Dump: `rom.sha1`. Game code AQUJ, 128 MiB cartridge, 0xFF-padded after the used area (0x7CB7580).

## NitroFS (verified: ndspy listing)
| id | name | what |
|---|---|---|
| 0-3 | overlays 0-3 | uncompressed, all load at 0x21F0760 |
| 4 | `_dtq.vx` | VX video (intro movie) |
| 5 | `FILEDATA.BIN` | everything else, the "LF 2" archive below |
| 6 | `sound_data.sdat` | sound |

## LF 2 archive (verified: `tests/test_identity.py` repacks it byte-identical)
- Header 0x10: `'LF 2'`, u32 data_start/4, u32 count (5749), u32 header size (0x10).
- Then count x (u32 offset/4, u32 size). Files are in order, no gaps, each starts 4-aligned.
- The alignment padding holds leftover garbage, not zeros; `lf2.read(data, pads)` keeps it for the identity repack.
- No names. Many files are duplicated (same RGCN under several ids).
- Contents: Nitro graphics (RGCN 1682, RLCN 907, RNAN/RECN 654, RCSN 422), `SCR0` (625, layout?), BMD0 (19),
  LZ10 files (first byte 0x10; decompress to `QQ` tilemaps), small raw records (2003-2175, 2621-2915: map/event data?).
- 2916: charset table (text.md). 2917: a stray Windows .lnk shortcut left in by the developers.

## ROM rebuild (verified: identity test)
ndspy `save()` differs from the original only in a size word it writes at 0x1000 (zero in the original) and in not
padding to 128 MiB; `tools/build.py` restores both.
