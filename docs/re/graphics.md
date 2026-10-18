# Graphics text survey

Japanese that stayed Japanese in the marker build (so it is not script text). Surveyed on every scene in
`tools/debug/scenes.json` (19 scenes, marker build, work/qa/survey; full notes in work/qa/survey/graphics_survey.md).
Source = first guess until confirmed by VRAM dump + corrupt-and-boot.

| # | Element | Japanese | Where | Source guess | State |
|---|---|---|---|---|---|
| G1 | logo katakana above QUEST | デルトラクエスト | top screen (sub BG), title and every story screen | FILEDATA 465 / 1620 / 1625 (below) | done: removed (tools/logo.py), cold-boot shots work/qa/logo_title, logo_story |
| G2 | logo subtitle | 7つの宝石 | top screen, under DELTORA | same | done: "The Seven Gems" |
| G3 | copyright line | (C)2006 デルトラクエスト製作委員会・テレビ愛知 (C)2007 NBGI | title, top | FILEDATA 1620 (part of the title logo screen) | done: 3 lines, "(C)2006 Deltora Quest Production Committee / TV Aichi / (C)2007 NBGI" |
| G4 | yes / no labels | はい / いいえ | entry-card confirm, above the two Lief portraits | OBJ cells in sprite sheets FILEDATA 5373 (3 copies) and 5378 (2; screen not seen yet), vramfind on OBJ-A 0x06401380 / 0x06401C80 (work/qa/yesno) | done: tools/tags.py LABELS, cold-boot shot work/qa/yesno_cold |
| G5 | speaker name tags | リーフ, バルダ, ジャード, ... | dialogue box top edge (cyan) | FILEDATA 4533+n (verified, below) | done: tools/tags.py; English in a cold-boot shot (work/qa/tags_cold) and via the text viewer |

## G1-G3 logo screens (verified: rendered from the files with tools/nitro.py; English import shows in cold boot)
- Three 256x192 4bpp BG screens, each an RLCN/RGCN/RCSN triple (palette, chr, screen): 464/465/466 dark story
  background (vramfind match, work/qa/tag), 1621/1620/1622 title with the (C) lines (vramfind, work/qa/title_dump),
  1624/1625/1626 light, no (C) (where shown: not seen yet). No byte-identical copies elsewhere.
- 465 and 1625: one tile per cell; 1620 shares some tiles (128 ids free). 16 palettes per screen, index 0 unused.
- `tools/logo.py` writes gfx/logo_<chr>.png once (Windows fonts); the build re-encodes only the changed 8x8 cells.

## G5 name tags (verified: vramfind exact match on OBJ-A VRAM 0x06402300, English redraw shows in-game)
- Header word 2 low byte = n * 4 picks tag n (1..45 = 0x01..0x2D); tag n = FILEDATA 4533 + n, RGCN, 560 bytes:
  0x30 header + one 64x16 picture = 16 4bpp tiles, shown as two 32x16 OBJ (1D) side by side, OBJ palette 2.
- Palette (FILEDATA 4530/4531 RLCN?, not checked): 0 transparent, 1 brightest cyan .. 15 darkest; the Japanese glyphs
  are antialiased with that ramp, caps on rows 4-12. All 45 names and their English: `tools/tags.py` NAMES.
- Tag sits top-left of the box when the portrait is on the left, top-right when on the right.

| G6 | field menu labels | そうび / だいじ / そざい / カード / アイテム | field menu (bottom-right icon; scene `menu`) | 32x16 OBJ cells in sheet FILEDATA 5311 (3 copies each; objcell.py) | blocked: 32 px wide, fixed by the cell's 0x300 VRAM slot (icon + label); wording for the user |
| G7 | item menu header | フィールドでつかうアイテム | scene `menu_item`, BG3 | BG screen 542 over chr 541 (pal 540) | todo |
| G8 | chapter title cards | 第1章 沈黙の森 ... 最終章 帰還 デルへ (8) | chapter start | BG screens 1694 1701 1708 1715 1722 1729 1736 1743 (gfxsurvey) | todo |
| G9 | area title cards | あたたかい キャンプ, TOMの店, ジャスミンの まぜまぜ部屋, スペシャルステージ モキートの館, ジャックの グランドファーム, エクストラステージ 夢幻の塔, ひみつの オーディオルーム | area entry | BG screens 1750 1757 1764 1771 1778 1785 1792 | todo |
| G10 | game over line | リーフたちは力つきた… | game over (GAME OVER already English) | BG screen 425 | todo |
| G11 | card trade headers | デルトラカードこうかん / こうかん中… | wireless card trade | BG screens 1675, 1678 | todo |
| G12 | Emily Rodda letter | 親愛なるデルトラ・ファンのみなさまへ ... エミリー | letter screen, Japanese half under her English handwriting | BG screen 357 | todo: probably drop the JP half (English original above) |
| G13 | demo leftovers? | 7つの宝石(仮) logo; 画面をタッチして次の人に...; ことし発売予定 | unknown; look like store-demo screens | BG 354, 374, 376 | check if retail shows them |
| G14 | bitmap font sheet | A-Z a-z 0-9, kana | which screen draws with it? | chr in screen group 513/512/510 | find its user |

## Survey method (tools/debug/gfxsurvey.py, objsurvey.py)
Every RCSN rendered with the RGCN/RLCN just before it (work/qa/gfxsurvey, 418 screens; read by 4 reviewer agents,
all sheets) and every RECN cell bank with the RGCN after it (work/qa/objsurvey, 6330 unique cells; not read yet).
The pairing is a guess: 1623 renders as a plausible second title layout over 1620's tiles but really is the bottom
title screen's map over other tiles (VRAM dump work/qa/title_dump2). Confirm a pairing in VRAM before editing.

Already English in the original: Bandai Namco splash, entry card, book cover, map scroll labels, HUD icons.
Not surveyed yet (no scene reaches them): in-game menu (items, equipment, recipes), shop, mixing room, smithing
minigame, game over, staff roll, chapter-clear screens. Add scenes for them, then extend this table.
