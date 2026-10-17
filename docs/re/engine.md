# Engine changes

## VWF (verified: marker build boots, menus and narration render proportional, centred lines centre; work/qa/m2)
`tools/codepatch.py`, applied by `tools/build.py` for any non-identity build.
- Hook code + 0x200-byte advance table live in ITCM 0x01FFFB00 (the game's ITCM block is 0x7B00 of 0x8000 bytes;
  the tail stayed zero through boot + opening, `tools/debug/itcm_check.lua`). The autoload block grows; the autoload
  list and module params (arm9 0xB64) are shifted.
- 0x0204DFCC `ldr r1,[sb,#0x40]` -> `bl vwf_adv`: advance = table[code], 0 = window's fixed pitch.
- The 4 glyph-loop `bl putpixel` (0x0204DEF8/DF38/DF7C/DFBC) -> `putpixel_nz`: pixel value 0 isn't drawn, so an
  overlapping next glyph doesn't erase the previous one's edge.
- 0x0204D9C4 (line start X: right / centre / left by [w+0x38]) -> `b linex`: same rules with table widths.
- Original words at the sites are asserted at build time.

## Font (fonts/en_font.txt -> tools/fontgen.py)
- Project-drawn proportional font: 9 px caps, 6 px x-height, 2 px descenders; 1 px outline added by the tool.
- Drawn into both game fonts (FILEDATA 506 and its bolder variant 509) over the kana cells: ASCII -> 0x10 + (c-0x20),
  '…' 0x6F. `tbl/en.tbl` is generated from that mapping (test_engine checks it).
- Advance = fill width + 1 (outlines overlap by one column); space 3 px; `{sp}` (FFF4) stays half pitch (6 px).

## Open
- Width gate: box widths per window type not measured yet (dialogue with portrait, narration, menus, name tag).
- Palette of 509-variant glyphs is fill 1 / outline F like 506; check where 509 is used.
