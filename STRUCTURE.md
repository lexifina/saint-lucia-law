# Structure

How the law of Saint Lucia is laid out in this repository. Folders are by type, then by year; no folder holds more than 1,000 entries.

| Folder | What it holds | One folder per | Files |
| --- | --- | --- | --- |
| `constitution/` | The Constitution of Saint Lucia (Schedule 1 to the Saint Lucia Constitution Order 1978) | - | `preamble.md`, `sec-NNN.md`, `sch-N.md` |
| `laws/cap-<n>-<slug>/` | Chapters of the Revised Laws of Saint Lucia, as consolidated | chapter | one file per section and schedule (not built yet: see the README) |
| `acts/<year>/<NNN>-<slug>/` | Acts of Parliament as enacted, by the year and number of the Act | Act | `front-matter.md` (title, arrangement, long title, enacting formula), `section-NNN.md`, `schedule-NN.md` |
| `statutory-instruments/<year>/<NNN>-<slug>/` | Statutory Instruments as made, by the year and number of the S.I. | instrument | as for Acts |
| `data/` | Tables about the record (`held.json`: instruments not taken, and why) | - | - |
| `tools/` | The scripts that fetch the sources and write this history | - | - |

`<NNN>` is the Act's or instrument's number, zero-padded to three digits; `<slug>` is its short title in lower case with hyphens. Section files are numbered `section-001.md`, `section-002.md`, `section-002a.md`; a section's marginal heading is the first line of its file. When the text layer of an instrument gives no section numbering to split on, the instrument is one file, `text.md`.

## Commits

One commit per version: an Act as enacted, an instrument as made, or a consolidated text. Each is dated noon America/St_Lucia (UTC-4) on the day it came into force, and carries:

- `In-force:` the day, as `YYYY-MM-DD`;
- `In-force-basis:` where the day comes from (a commencement day stated in the text, a day appointed by a commencement instrument, the date printed in square brackets under the long title, which is the day of publication in the Gazette, the Governor-General's assent, or the day the instrument was made);
- `Text-source:` the PDF text layer as served (no OCR is run here);
- `Source:`, `Source-sha256:` and `Source-listing:` the file the text was read from, its hash and the page that lists it.

The author of each commit is the Act or instrument (`Act No. 9 of 2004`, `S.I. No. 88 of 2004`). An Act that commences on a day to be appointed is dated by the commencement instrument when one is found, otherwise by its Gazette day, and its `In-force-basis:` says so.
