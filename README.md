# Saint Lucia: law history in git


The law of Saint Lucia as a git history: one file per section, one commit per version on the day it took effect, and the act that made each change as the commit's author. `git blame` names the act (or the publisher) behind every line; `git log` lists every change to a section; picking a date gives the text in force that day.

Part of [lexifina/global-law](https://github.com/lexifina/global-law), one git history for every country's law: this is Saint Lucia's national law, which global-law reads at `saint-lucia/national/acts/`.

**What is in it now:** the Constitution of Saint Lucia, in one version so far (129 files: the preamble, sections 1 to 124 and 108A, and Schedules 1 to 3), its current text from the Revised Laws of Saint Lucia (2023). There is no `PLAN.md`; [`REPRODUCE.md`](REPRODUCE.md) lists the act and its version, and [`data/laws.csv`](data/laws.csv) the four laws the source names as having made the text.

The Constitution is in [`constitution/`](constitution/), with one file per section, schedule and the preamble, plus a `README.md` listing them (`constitution/sec-010.md` is section 10, Protection of freedom of expression).

The text is in English, as the Revised Laws print it; the amendment notes printed under each section are left out.

## Questions as git commands

| Question | Command |
| --- | --- |
| Every change to section 10 of the Constitution | `git log -p --word-diff -- constitution/sec-010.md` |
| Which act wrote each line of section 10? | `git blame constitution/sec-010.md` |
| Every version of the Constitution, with the day each took effect | `git log --format="%h %(trailers:key=In-force,valueonly,separator=) %an" -- constitution ':!*/README.md'` |
| Section 10 as in force on 1 January 2026 | `python tools/on.py 2026-01-01 constitution 10` |

**Outside git**, we also host this record publicly, for free:

- **[Ask Claude about Saint Lucian law](https://global-law.lexifina.com/v1/try_claude?country=saint-lucia)**: opens Claude with a first question ready.
- **[Ask ChatGPT](https://global-law.lexifina.com/v1/try_chatgpt?country=saint-lucia)**: the same question in ChatGPT.
- **[Search Saint Lucian law on our site](https://lexifina.com/law?country=saint-lucia&q=freedom+of+expression)**: a search for "freedom of expression", with each provision's text and its versions, no account needed.
- **[Developer REST API](https://global-law.lexifina.com/v1/search_law?query=freedom+of+expression&jurisdiction=saint-lucia)**: the same search as JSON, with no key. See the [documentation here](https://lexifina.com/api/global-law).

Both assistants read the record through the free Global law connector (MCP, `https://global-law.lexifina.com/mcp`); the first time, the chat gives you the link that adds it. Ask in English.

**Host it yourself easily.** All it takes is git and Python, and the tools run on your machine:

```sh
git clone --depth 1 https://github.com/lexifina/global-law && cd global-law
python3 tools/countries.py add saint-lucia/national/acts
python3 tools/law.py show 2026-01-01 saint-lucia/national/acts/constitution/sec-010.md
```

Opened in Claude Code, Cursor, VS Code or Codex, the clone also starts a local MCP server with the same tools ([MCP.md](https://github.com/lexifina/global-law/blob/main/MCP.md)).

## Dates

Each commit is dated at noon, America/St_Lucia, on the day the version took effect, and carries it in its `In-force:` trailer. The Revised Laws publish only the current text, so:

- the one version is dated 27 March 2023, the day the source gives for the newest amendment it lists (Act 7 of 2023).

That version is the "oldest version available", credited to the publisher, `Attorney General's Chambers of Saint Lucia (Revised Laws of Saint Lucia)`; its message names the laws the source lists as having made the text (the Saint Lucia Constitution Order 1978, Act 17 of 1980, Act 2 of 2023 and Act 7 of 2023).

## How it is checked

- `tools/check_repo.py` reads the act back from git on the day its version took effect, choosing the commit by its `In-force:` trailer, and compares it file by file with the corpus it was built from; it also checks that every commit's trailers parse and that there are no merge commits. [`REPRODUCE.md`](REPRODUCE.md) records no run of it for this build yet.
- On 30 October 2026 the whole text was read again from the source and compared with the stored text: all 129 units matched.
- `tools/build.py` writes the history from the corpus in one pass, and the same corpus always gives the same commit hashes; `REPRODUCE.md` gives the corpus's sha256 and the builder's hashes.
- History is append-only: no merge commits and nothing rewritten.

## What it does not show

- **Earlier versions of the Constitution.** The Order as made in 1979, the 1980 change to section 25, the 2006 revised edition and Act 2 of 2023 are not built.
- **The rest of the Order.** Only Schedule 1 to the Saint Lucia Constitution Order 1978 (the Constitution) is here, not the Order itself or later instruments on the same pages.
- **Other law.** No other act (the Criminal Code and the Data Protection Act among them), no subsidiary legislation and no case law.
- **The amendment notes** printed under each section, which say which act changed it.

## Sources

| Source | Kind | Past versions | Notes |
| --- | --- | --- | --- |
| [Revised Laws of Saint Lucia (2023)](https://attorneygeneralchambers.com/laws-of-saint-lucia/) (Attorney General's Chambers) | Consolidated laws | no, current text only | Each section's text and the amending acts the act page lists, with their in-force days |

## Licence

See [`LICENSE`](LICENSE). The Attorney General's Chambers state no licence; under the Copyright Act (Cap. 13.07), section 24(4) and (5), copyright in works made or first published by or under the direction of the Government belongs to the Crown. The text is reproduced without change to its wording, as a public record of the law, with attribution to its publisher; Lexifina's own contributions (the arrangement, commit messages, tables and tools) are CC0 1.0.

No AI model wrote, translated or corrected legal text; the scripts that read the sources and build this repository were written by an AI model (see [`REPRODUCE.md`](REPRODUCE.md)).

## More

From [lexifina/global-law](https://github.com/lexifina/global-law):

- [FEATURES.md](https://github.com/lexifina/global-law/blob/main/FEATURES.md): every feature, and what every corpus must support (`git blame`, `law.py`, the MCP tools)
- [FAQ.md](https://github.com/lexifina/global-law/blob/main/FAQ.md): questions and answers · [CONTRIBUTING.md](https://github.com/lexifina/global-law/blob/main/CONTRIBUTING.md): proposing changes · [MCP.md](https://github.com/lexifina/global-law/blob/main/MCP.md): the MCP server · [REPRODUCE.md](https://github.com/lexifina/global-law/blob/main/REPRODUCE.md): how it was built · [CHANGELOG.md](https://github.com/lexifina/global-law/blob/main/CHANGELOG.md)
- [FRESHNESS.md](https://github.com/lexifina/global-law/blob/main/FRESHNESS.md): how current each corpus is · [Monitoring](https://github.com/lexifina/global-law/tree/main/monitoring): whether updates are running · [WATCHING.md](https://github.com/lexifina/global-law/blob/main/WATCHING.md): how each official source is watched for changes
- [performance/](https://github.com/lexifina/global-law/tree/main/performance): how fast the tools are, measured
- [visualisations/](https://github.com/lexifina/global-law/tree/main/visualisations): charts and bridges across the world's law
- [Vulnerabilities](https://github.com/lexifina/global-law/tree/main/vulnerabilities): mistakes in legislation as published
