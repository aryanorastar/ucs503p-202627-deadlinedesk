# Repository structure

DeadlineDesk keeps implementation, documentation, and submission artifacts separate so each file has one obvious home.

```text
assets/                         Shared TIET branding and static assets
code/                           Django prototype, migrations, templates, tests
docs/                           MkDocs source: SRS, design, testing, demo and backlog
docs/submission/                Self-contained Week 4–7 evaluation bundle
journals/<roll>-<name>/         Canonical weekly journals and consolidated journal.md
project-proposal/               Updated proposal source, figures and PDF (through Week 7)
project-report-prototype-stage/ Editable Week 7 report source and compiled PDF
w4/                             Week 4 one-page handout and presentation PDF
```

The `docs/submission/` folder is intentionally a packaged copy for evaluation downloads. The root folders remain the canonical working locations for code, proposal, report, and journals.

## Deliverable map

| Deliverable | Canonical location | Submission copy |
|---|---|---|
| Presentation | Week 7 deck in `docs/submission/01-presentation/`; Week 4 PDF in `w4/` | `docs/submission/01-presentation/` |
| Proposal | `project-proposal/` | `docs/submission/02-project-proposal/` |
| Use-case diagram | `project-proposal/figures/` | `docs/submission/03-use-case-diagrams/` (symlinks to canonical files) |
| Data-flow diagrams | `project-proposal/figures/` | `docs/submission/04-data-flow-diagrams/` (symlinks to canonical files) |
| Team journals | `journals/` | `docs/submission/05-team-journals/` |
| Week 7 prototype report | `project-report-prototype-stage/` | `docs/submission/06-week7-prototype-report/` |
| Gantt, activity and ER diagrams | `project-proposal/figures/` | `docs/submission/07-planning-and-model-diagrams/` (links to canonical files) |

## Diagram sources and exports

Every diagram has exactly one editable source, `project-proposal/figures/<name>.drawio`, with its `<name>.pdf` and `<name>.png` exports next to it. The proposal embeds the PDFs, the submission pages show the PNGs, and folders `03` and `04` symlink to the same files rather than keeping copies.

1. Edit the `.drawio` file in draw.io (desktop or app.diagrams.net).
2. Run `make diagrams`. It calls draw.io Desktop's CLI (`DRAWIO ?= drawio`) to export every page to PDF and the first page to PNG at 2× scale.
3. Rebuild the proposal (`tectonic project-proposal/main.tex`) if a figure it embeds changed.

No script generates or overwrites `.drawio` files. The earlier Python generators (`render_diagrams.py`, `render_additional_diagrams.py`) were removed, because re-running them would have replaced hand-edited draw.io sources with stale layouts.
