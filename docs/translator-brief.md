# Translator brief - Deltora Quest: 7-tsu no Houseki (Nintendo DS, 2007)

You translate part of the Japanese script of the DS action RPG based on Emily Rodda's Deltora Quest novels into
English for a fan patch. Young-reader adventure: plain, warm, lively English; the original is written for children
(mostly kana), so keep it simple but not babyish. Hero: Lief, 16, with Barda and Jasmine.
Work only on the batch named in your dispatch. Do all translation yourself; do not dispatch subagents.

## Read first
1. `docs/style-reference.md` - character voices and approved example pairs. Match this voice.
2. `work/batches/<batch>.terms.md` - binding glossary rows for this batch (full table: `glossary.md`).
3. `docs/synopsis.md` - order of events, who is who, the late reveals. Never give a reveal away early.

## Input: `work/batches/<batch>.tsv`
`id<TAB>speaker<TAB>form<TAB>limit<TAB>Japanese`, in story order (use neighbours for context).
- speaker: the portrait code (`p0118` = slot 01, variant 18) and a name hint. Slots are a per-chapter cast: in
  Lief's chapters slot 01 is usually Lief, 02 Barda, 03 Jasmine (hints end in `?`); in 2179 (prologue) slot 01 is
  young Jarred until "16年後" (2179_244), then Lief. Same code = same speaker within a scene. Confirm from context.
- form: `dlg` (dialogue box with portrait), `narration` (no portrait: story narration, letters, prompts), `menu` (item/place names,
  descriptions, recipes), `system` (title, prompts, shop, tower, wireless).
- Tokens in the Japanese: `{n}` line break inside a page, `{p}` new page (player taps), `{sp}` a small gap
  (Japanese word spacing: do NOT copy it; use normal spaces), `{var}` a number or name the game inserts, `{c1}`
  `{c2}` colour on, `{/c}` colour off, `{f6}` `{f9}` engine codes, `{icon1-3}` item icons, `♥` heart.

## Output: `work/batches/<batch>.out.tsv`, written with your file-write tool (not a shell heredoc)
`id<TAB>English`, every input id exactly once, same order. Plain ASCII: straight quotes "...", '...', `...` for
ellipses, `--` for a dash; no tabs inside the English, no Japanese or fullwidth characters, no backslashes.
Use `{n}` and `{p}` yourself to lay out the text (you choose where lines and pages break):
- `dlg`: at most **2 lines per page**, each **<= 240 px** (about 45 characters). Add pages with `{p}` freely.
- other forms: each line <= 240 px; no more lines per page than the Japanese page had (limit column says how many).
  Menu names should stay short (a list column): about as long as the Japanese or shorter.
- Break lines at natural phrase boundaries; never leave a 1-5 character stub as the last line of a page.
- Check widths before writing: `python -X utf8 tools/batches.py fit "Your line{n}second line" --portrait`.

## Validate
Run `python -X utf8 tools/batches.py check <batch>` from the repo root and fix every reported id until it prints OK.

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Don't add or skip content.
  Adapt wordplay and riddles so they still work in English (no translator notes).
- Names and terms exactly as in the glossary (official novel names: Lief, Barda, Jasmine, the Shadow Lord, Grey
  Guards, the Belt of Deltora...). Never abbreviate. If a line can't fit, keep the meaning and report `LONG: id`.
- No honorifics (様, さん, 殿: drop them, or use "King Endon", "Lord", "sir" where the tone needs it). Western order.
- Punctuation: 「」 -> "...", 『』 (item/term emphasis) -> keep the colour codes, drop the brackets or use
  'single quotes' when needed; …… / ・・・ -> `...`; ！？ -> `?!`; ー stretched vowels -> natural English
  ("Caw!", "Nooo!").
- `{var}`: copy every control token exactly, same count. Nothing glued to `{var}` ("No. {var}", not "{var}th");
  no a/an right before a name `{var}`; write numbers around it so singular and plural both read ("x{var}").
- Kree's cries カー -> "Caw!". Sound effects: plain words in asterisks only if the JP is clearly a sound (*crash*).
- Debug/unused lines (2197 menu lists of STAGE/SOUND/EVENT, 2198): translate plainly; keep the padding spaces short.

## Consistency
Never edit `glossary.md` or any file but your output. For a recurring name or term not in the glossary, pick a form,
use it consistently, and report it.

## Notes from earlier batches
- A line whose Japanese is empty: write the id alone on its line (no tab needed); it stays empty.
- The glossary check matches whole words; if it still flags a false hit, report it as `UNSURE: id - false glossary
  hit <term>` and leave the line as is (the controller fixes the checker).
- Japanese written backwards (signs like 『！いなぶあ　！んけき』) = backwards English, keep it readable ("!regnaD").
- Staff credits (2178): company names in their official English forms (e.g. "Bandai Namco Games Inc."); person
  names in Western order, readings you can't verify marked UNSURE.

## Report (reply with only this)
Files written and entry count; then any lines: `NEW TERM: jp -> en`, `UNSURE: id - note`, `LONG: id - note`.
