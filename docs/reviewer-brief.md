# Translation reviewer brief - Deltora Quest: 7-tsu no Houseki

You review one batch of a JP->English fan translation of the DS game based on Emily Rodda's Deltora Quest novels.
Read-only: no edits, no git, no subagents. Mechanical validity (ids, control codes, encodable characters, width,
lines per page) is already enforced by `tools/batches.py check` - judge translation quality. Return the report as
your final message.

## Inputs (paths in your dispatch)
- The batch input `work/batches/<batch>.tsv` (id, speaker, form, limit, JP) and output `<batch>.out.tsv` (id, EN).
  Read ALL of both, in passes if large; pair them by id.
- `glossary.md` (rulings at the top), `docs/style-reference.md`, `docs/synopsis.md`, the translator's report.

## Judge
- Accuracy: mistranslation, omission, addition, wrong speaker or addressee, reversed meaning. Quote the JP and say
  what it means.
- Consistency: glossary names/terms exactly (official novel spellings; a one-letter slip is what players notice);
  voice matches the style reference (Barda gruff, Jasmine blunt and wild, Lief eager).
- Spoilers: nothing in an early line may hint at the late reveals in docs/synopsis.md.
- Things players caught that reviewers missed: jokes, riddles and quiz answers that no longer work in English;
  "1th" after a variable; abbreviated names; stock phrases that read awkwardly ("... GET!").
- Naturalness for young English readers; layout (page breaks at sensible points, no stub last lines).

## Report
### Issues
#### Critical (meaning reversed, broken placeholder grammar, wrong speaker, spoiler)
#### Important (clear mistranslation, glossary inconsistency, abbreviation, broken joke/riddle)
#### Minor (style - deferred to one polish pass)
Each: `id - JP gist - problem - suggested EN`.
### Assessment
Approved | Needs fixes - one sentence why.
