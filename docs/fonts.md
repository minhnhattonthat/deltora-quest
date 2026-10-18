# Fonts

Every font or glyph sheet the build reads ends up inside the released patch, so its licence must allow that. One row
per file; a font with no known licence doesn't go into a release.

| File | Source (URL, version) | Licence | Redistributable in a patch | Used for | Changes made |
|---|---|---|---|---|---|
| fonts/en_font.txt | drawn for this project (2026-10-18) | MIT, same as repo | yes | dialogue/menu VWF glyphs in FILEDATA 506 and 509; speaker name tags (tools/tags.py) | - |
| C:/Windows/Fonts/georgiab.ttf, arial.ttf (via the skill's typeset.py) | Windows | Microsoft; only rasterized into gfx/logo_*.png, the font files are not read by the build or shipped | the pixels yes (images made with the font) | logo subtitle "The Seven Gems", title (C) lines (tools/logo.py) | thresholded / outlined, red-gold ramp |
| fonts/tag_small.txt | drawn for this project (2026-10-18) | MIT, same as repo | yes | name tags too wide in en_font (Mother Brightly) | - |
