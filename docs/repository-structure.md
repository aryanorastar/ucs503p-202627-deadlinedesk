# Repository structure

DeadlineDesk keeps implementation, documentation, and submission artifacts separate so each file has one obvious home.

```text
assets/                         Shared TIET branding and static assets
code/                           Django application, migrations, templates, tests
docs/                           MkDocs source: SRS, design, testing, demo and backlog
docs/submission/                Final evaluation index and preserved milestone artifacts
docs/uml/<type>/                Eight UML types, each in its own folder
docs/gantt-chart/               Final Gantt chart source, PDF and PNG
docs/test-cases/                Test-case LaTeX, PDF and recorded results
journals/<roll>-<name>/         Canonical weekly journals and consolidated journal.md
project-proposal/               Updated proposal source, figures and PDF (through Week 7)
project-report-prototype-stage/ Editable Week 7 report source and compiled PDF
project-report-final/           Final report source and compiled PDF
scripts/                        Demo runner and artifact preparation/export scripts
w4/                             Week 4 one-page handout and presentation PDF
```

The `docs/submission/` folder is an evaluation index. Root folders remain the canonical locations for code, proposal, reports and journals. Relative symlinks and links expose existing artifacts without maintaining duplicate editable copies. The final presentation is canonical in its own submission folder.

## Deliverable map

| Deliverable | Canonical location | Submission entry |
|---|---|---|
| Presentation | Week 7 deck in `docs/submission/01-presentation/`; Week 4 PDF in `w4/` | `docs/submission/01-presentation/` |
| Proposal | `project-proposal/` | `docs/submission/02-project-proposal/` |
| Use-case diagram | `project-proposal/figures/` | `docs/submission/03-use-case-diagrams/` (symlinks to canonical files) |
| Data-flow diagrams | `project-proposal/figures/` | `docs/submission/04-data-flow-diagrams/` (symlinks to canonical files) |
| Team journals | `journals/` | `docs/submission/05-team-journals/` |
| Week 7 prototype report | `project-report-prototype-stage/` | `docs/submission/06-week7-prototype-report/` |
| Gantt, activity, ER, class and sequence diagrams | `project-proposal/figures/` | `docs/submission/07-planning-and-model-diagrams/` (links to canonical files) |
| Final report | `project-report-final/main.tex` and `main.pdf` | `docs/submission/08-final-report/` (relative symlinks) |
| Final presentation | `docs/submission/09-final-presentation/DeadlineDesk_Final_Presentation.pdf` and `.pptx` | same folder, with a README and inline slide previews |
| Eight UML types | `docs/uml/01-use-case/` through `08-package/` | individual folders; the unchanged sequence links to its canonical source |
| Final Gantt chart | `docs/gantt-chart/` | same folder |
| Test cases | `docs/test-cases/` | same folder |

## Diagram sources and exports

Each diagram has one editable `.drawio` source with matching PDF/PNG exports. Baseline sources remain in `project-proposal/figures/`. Final use-case, class and activity revisions have their own sources because they document the final ownership and timing guards. The unchanged submission sequence is shared by relative symlink. State-machine, component, deployment and package diagrams live in their individual `docs/uml/` folders, and the final schedule lives in `docs/gantt-chart/`. DFD and ER diagrams are supporting material outside the eight UML types.

1. Edit the `.drawio` file in draw.io (desktop or app.diagrams.net).
2. Run `python scripts/export_diagrams.py`. It calls draw.io Desktop's CLI to export baseline and final sources, resolving symlinks so a shared source is exported once.
3. Rebuild affected LaTeX reports from their source directory, for example `cd project-report-final && tectonic main.tex`.

The export script never writes `.drawio` sources. `scripts/prepare_final_diagrams.py` creates missing final source files once; rerunning it preserves existing editable sources. The earlier baseline generators (`render_diagrams.py`, `render_additional_diagrams.py`) remain retired because they overwrote edited layouts.

## Report, test and demonstration state

The final report embeds canonical diagram PDFs and `docs/test-cases/catalog.tex`. The test catalogue is generated from a real passing pytest JUnit result using `scripts/build_test_catalog.py`. Re-run tests before regenerating it; a failed run must not produce passing evidence.

The normal local database and the `.demo-runtime/` synthetic demonstration database are separate. Runtime data, private uploads and temporary build files are ignored by Git. [Demo startup and public-link lifetime](live-demo.md) and [final verification](final-verification.md) document the application separately from GitHub Pages publication.
