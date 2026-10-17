# Window budgets (width gate)

Measured on the marker build with the text viewer (`tools/debug/show.py`, ruler lines of 6 px digits) and the
glyph torture line (all English glyphs + double space: clean, work/qa/torture). Enforced by `tools/lint.py`.

| Window | Which lines | Measured | Budget |
|---|---|---|---|
| Portrait dialogue box (bottom screen, name tag, portrait) | header word 2 != 0000 (2,370 lines) | centred, visible 0-256 px, 2 lines per page (3rd falls below the box) | 240 px, 2 lines/page, add pages with {p} |
| Narration (over pictures / room, no portrait) | header 0000 0000 in story files | centred, visible 0-256 px, 4 lines fit | 240 px; lines/page <= JP's for that line (warn) |
| Title button (2199_001), はじめから panel (2192_014), top-screen prompts (2192) | system | marker "[2199_001] The quick brown fox" (~150 px) fits the button | 240 px; keep labels near the JP width |
| Menus, item names/descriptions (2197, 2191), shop (2195), status (2194), link (2200) | | **not measured** (screens not reachable yet) | 240 px; lines/page <= JP's (warn) |

Notes
- Line height 16 px; the bitmap is allocated as (most lines on a page) x 16 px, so a window grows with the text,
  but the portrait box frame only shows 2 lines.
- `{sp}` (FFF4) is 6 px; English uses normal spaces (3 px).
- Glyph advances come from `fonts/en_font.txt` (width + 1); the lint uses the same numbers via `tools/fontgen.py`.
