# Reverse-engineering notes

One file per subsystem (text engine, pointers, compression, font, graphics). Mark every finding with how far it is
proven, so a later session doesn't build on a guess:

- **verified** - and how: a decoded known string, a corrupt-and-boot test, a breakpoint hit on the drawing path, a
  passing roundtrip test. Name the test or savestate.
- **guess** - and why it seems likely (byte pattern, another game, an earlier patch's notes). Promote it to verified
  before code depends on it.

Addresses are for the dump in `rom.sha1` unless a note says otherwise.

| File | Covers | State |
|---|---|---|
| filedata.md | NitroFS, LF2 archive, ROM rebuild quirks | verified |
| text.md | text files, codes, charset, font, renderer | verified; FFF6/FFF9 meaning guessed |
| engine.md | VWF hooks in ITCM, English font | verified in marker build |
| debug.md | scene warps, text viewer, probes | route scenes only |
