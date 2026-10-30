# Saint Lucia: law history in git

The Constitution of Saint Lucia as a git repository: one file per provision, with the publisher of the text as the commit's author. It follows the shared design of [lexifina/global-law](https://github.com/lexifina/global-law), which places it at `lc/`.

**What is in it now**

| Folder | Act | Versions | History |
| --- | --- | ---: | --- |
| `constitution/` | The Constitution of Saint Lucia (Schedule 1 to the Saint Lucia Constitution Order 1978) | 1 | The current text from the Revised Laws of Saint Lucia (2023), dated 27 March 2023 |

**What it is not, yet: a history.** The Revised Laws of Saint Lucia (Attorney General's Chambers) publish only the current text of each law. This is one version, the oldest available, dated by the in-force day of the newest amendment the source lists (Act 7 of 2023, 27 March 2023). The earlier versions (the Order as made in 1979, the 1980 change to section 25, the 2006 revised edition, Act 2 of 2023) are not built. Amendment notes printed under each provision in the source are left out of the text. Other laws, including the Criminal Code and the Data Protection Act, are not built.

**How it was checked.** The whole text was read again from the source on 30 October 2026 and compared with the stored text: every unit matched.

## Dates

The commit is dated at noon, America/St_Lucia, on 27 March 2023.

## What "author" means

The author of a commit is the law that made the change, with an e-mail address that cannot exist. The committer is Lexifina.

This is a research aid, not an official version and not legal advice. For anything that matters, read the original.

## How it is built

Lexifina reads the sources listed here and records each act's dated versions, and the laws that made each change, in one corpus file. `tools/build.py` writes this repository from that file, and the same corpus always gives the same commit hashes; `REPRODUCE.md` gives the details and the checks. A model (Claude) wrote Lexifina's code; it wrote no legal text, and no model runs when the history is built.

See [REPRODUCE.md](REPRODUCE.md).
