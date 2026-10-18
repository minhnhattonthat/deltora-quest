# Graphics text survey

Japanese that stayed Japanese in the marker build (so it is not script text). Surveyed on every scene in
`tools/debug/scenes.json` (19 scenes, marker build, work/qa/survey; full notes in work/qa/survey/graphics_survey.md).
Source = first guess until confirmed by VRAM dump + corrupt-and-boot.

| # | Element | Japanese | Where | Source guess | State |
|---|---|---|---|---|---|
| G1 | logo katakana above QUEST | デルトラクエスト | top screen (sub BG), title and every story screen | FILEDATA 465 (RGCN, 767 tiles; vramfind exact match at sub-BG VRAM 0x06200020, work/qa/tag) | todo: redraw or remove |
| G2 | logo subtitle | 7つの宝石 | top screen, under DELTORA | FILEDATA 465 (same) | todo: "The Seven Gems" |
| G3 | copyright line | (C)2006 デルトラクエスト製作委員会・テレビ愛知 (C)2007 NBGI | title, top | graphic (grey, antialiased) | todo: translate (legal line) |
| G4 | yes / no labels | はい / いいえ | entry-card confirm, above the two Lief portraits | font-styled but no script string has them: sprite in the font's look? | check: VRAM/OAM dump |
| G5 | speaker name tags | リーフ, バルダ, ジャード, ... | dialogue box top edge (cyan) | FILEDATA 4533+n (verified, below) | done: tools/tags.py; English in a cold-boot shot (work/qa/tags_cold) and via the text viewer |

## G5 name tags (verified: vramfind exact match on OBJ-A VRAM 0x06402300, English redraw shows in-game)
- Header word 2 low byte = n * 4 picks tag n (1..45 = 0x01..0x2D); tag n = FILEDATA 4533 + n, RGCN, 560 bytes:
  0x30 header + one 64x16 picture = 16 4bpp tiles, shown as two 32x16 OBJ (1D) side by side, OBJ palette 2.
- Palette (FILEDATA 4530/4531 RLCN?, not checked): 0 transparent, 1 brightest cyan .. 15 darkest; the Japanese glyphs
  are antialiased with that ramp, caps on rows 4-12. All 45 names and their English: `tools/tags.py` NAMES.
- Tag sits top-left of the box when the portrait is on the left, top-right when on the right.

Already English in the original: Bandai Namco splash, entry card, book cover, map scroll labels, HUD icons.
Not surveyed yet (no scene reaches them): in-game menu (items, equipment, recipes), shop, mixing room, smithing
minigame, game over, staff roll, chapter-clear screens. Add scenes for them, then extend this table.
