# Text engine

## Where the text is (verified: roundtrip test `tests/test_text.py`, decoded known on-screen strings)
- FILEDATA files **2178-2200**: all dialogue, system prompts, menus, item names, credits (3,665 strings).
  Found by encoding on-screen phrases ("あたらしいぼうけんをはじめます" -> 2192, "ぼうけんをはじめる" -> 2199).
- No Shift-JIS or UTF-16 text in arm9/overlays (scan found only graphics noise).

## File format
- u32 offset table (first offset = table size), then the strings back to back.
- Each string: 2 header words (speaker / portrait or window style; `0000 0000` = none), then 16-bit LE codes,
  ending `FFFD`. Header kept as hex in `script/*.json` `hdr`.

## Codes
- `0000-00FF`: FILEDATA **2916** is the game's own charset (256 x UTF-16): punctuation, hiragana, katakana, A-Z a-z,
  digits. Duplicate entries FE/FF (U+3000) are `{dupFE}`/`{dupFF}` in the table.
- `0100`: heart; `0101-0103`: colour icons (`{icon1..3}`, item-type icons in lists); `0104-0113` circled 5-20;
  `0114-012D` circled A-Z; `012E-013F` circled a-r.
- `0140-04FF`: kanji, in no standard order. Code = font cell. Read from the font by OCR + eye (docs/re/kanji.md).
- Controls: `FFFD` {end}, `FFFF` {n} newline, `FFFE` {p} page, `FFF4` {sp} (space between phrases, kana text),
  `FFF5` {var} (number/name insert), `FFF7` {c1} / `FFF8` {c2} colour on, `FFFC` {/c} colour off,
  `FFF6` {f6}, `FFF9` {f9} (unknown: guess).

## Font (verified: rendered, matches the screen)
- FILEDATA **506**: RGCN 4bpp, 256 px wide (32 tiles), 1280 cells of 16x16 (2x2 tiles), cell index = code.
  Glyphs ~12x14 px with a 1 px outline. Pixel values 1-4 fill (shaded), E/F outline. 509 is another copy.
- `tools/font.py` reads cells; `tools/font_sheet.py` makes labelled sheets.
