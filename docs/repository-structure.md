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
| Use-case diagram | `docs/submission/03-use-case-diagrams/` | same folder |
| Data-flow diagrams | `docs/submission/04-data-flow-diagrams/` | same folder |
| Team journals | `journals/` | `docs/submission/05-team-journals/` |
| Week 7 prototype report | `project-report-prototype-stage/` | `docs/submission/06-week7-prototype-report/` |
| Gantt, activity and ER diagrams | `project-proposal/figures/` | `docs/submission/07-planning-and-model-diagrams/` (links to canonical files) |
