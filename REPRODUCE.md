# How this repository was made (Saint Lucia)

This file is written by the build on 2026-10-30, the day the source data was retrieved.

## Sources

| Source | Address | Retrieved | Licence |
| --- | --- | --- | --- |
| Revised Laws of Saint Lucia (2023), Attorney General's Chambers | <https://attorneygeneralchambers.com/laws-of-saint-lucia/> | 2026-10-28 | none stated |

Every word of law in this repository comes from these sources. Lexifina reads them and records each act's dated versions, and the laws that made each change, in one corpus file. This repository is built from that file.

## What is in it

| Act | Title | Versions | Span |
| --- | --- | ---: | --- |
| `constitution` | Constitution of Saint Lucia | 1 | 2023-03-27 to 2023-03-27 |

The build made 1 commits:

| Commits | Kind |
| ---: | --- |
| 1 | first version of an act |
| 0 | one law on its in-force day |
| 0 | changes no amendment note explains, credited to the publisher |

Other counts:
- 0 commits on the branch `future`: laws not yet in force on 2026-10-30.
- 0 commits dated 1 January 1970: in force before 1970, with the real day in their `In-force` trailer.
- 4 laws in the record.
- 1 tags.

## Dates

Each commit is dated at noon (America/St_Lucia) on the day the change took effect. The other dates, enacted and published, are trailers.

When a law gives no date of its own, the default rule applies: Interpretation Act, Cap. 1.06: an Act comes into operation on publication in the Gazette unless it provides otherwise (not yet cited from the source; to verify) https://attorneygeneralchambers.com/laws-of-saint-lucia/interpretation-act

## How the history is built

`tools/build.py` turns the corpus into this history in one pass: one commit per law, on the day it took effect. The same corpus always gives the same commit hashes. `tools/check_repo.py` reads every version back from git and compares it with the corpus. `tools/on.py` shows the law as it stood on any date. The corpus format is described in `tools/SCHEMA.md`.

- Corpus: sha256 `3316f42a1bd3e06fc61eb24c6b73f6b7f217cbb1fa29cdffef35ee473570c48d` (256353 bytes).
- Builder blob hashes (`git hash-object`): `build.py` `a4faa25af85facb64b956b372f6b528aafdd7ec1`, `check.py` `3e59cb6f05eccb94a9ec14431a7f6781221e83ef`, `on.py` `644a6c0857fbcc72562032b58d57aa113fee0641`.
- Python 3.12.10; git version 2.46.0.windows.1.

## Checks

Not yet run for this build.

No second build of this corpus has been compared yet.

## Decisions made by hand

- First cut at wind-down: the Constitution is committed as one "oldest version available" version (FORK.md rule 1).
- The version is dated 2023-03-27, the in-force day the source gives for Act 7 of 2023, its newest listed amendment.
- Amendment notes such as "(Amended by Act 2 of 2023)" are removed from the text; they are the basis for crediting once older versions are built.
- Only Schedule 1 to the Order (the Constitution) is built; the Order itself and later instruments shown on the same pages are left out.

## What AI did and did not do

The scripts that read the sources and build this repository were written by Claude Code running Claude Opus 5.5 (`claude-opus-5-5`) under Lexifina's direction.

No model wrote, translated or corrected legal text. No model runs at build time. Every word of law in this repository comes from the official sources above.

The commit messages are written by `build.py` from the source data.

Model use at data-build time:
- none: text parsed by code from the official HTML; no model wrote or edited legal text.
