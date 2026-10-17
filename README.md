# Deltora Quest: 7-tsu no Houseki English translation

Unofficial English fan translation of **Deltora Quest: 7-tsu no Houseki** (Nintendo DS, Bandai Namco Games, 2007): the source text and tools
that build the patch.

**Just want to play?** Download the patch from [Releases](../../releases) and follow its README. This repository holds
no game data you can play; you need your own dump of the Japanese game.

## What's here

| Path | What it is |
|---|---|
| `script/` | Every text block: original Japanese and English. Translation fixes go here. |
| `glossary.md` | Binding names, terms and style rules. |
| `tools/` | Python build chain: extract, insert, lint, release. |
| `tests/` | pytest suite (ROM-dependent tests skip when the ROM is absent). |
| `docs/re/` | Reverse-engineering notes. |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |

## Build your own patched ROM

Needs Python 3.12+ and your own dump of the Japanese game.

```sh
git clone https://github.com/minhnhattonthat/deltora-quest
cd deltora-quest
# copy your dump to: rom/1415 - Deltora Quest - 7-tsu no Houseki (J)(Caravan).nds
#   (134217728 bytes, SHA-1 5a28815f68e78e2da5b486951a158a374150e459; the build refuses any other dump, see rom.sha1)
python -X utf8 tools/build.py                          # -> build/deltora_en.nds
python -X utf8 tools/check.py                          # tests + text lint
```

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

## Licence

Tools and English translation: MIT. The original Japanese text in `script/` is Bandai Namco Games' and is included only so
the translation can be checked against it. Deltora Quest is (c) Emily Rodda; the game is (c) Bandai Namco Games; this project is not affiliated with them.
Do not share patched ROMs.

The translation was made with extensive AI assistance (Claude by Anthropic). Corrections are very welcome.
