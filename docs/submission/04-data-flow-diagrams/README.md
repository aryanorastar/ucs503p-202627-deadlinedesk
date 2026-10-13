# Data-Flow Diagrams

The Level 0 context diagram treats DeadlineDesk as one process. The Level 1 diagram decomposes it into six processes that match the role-protected views in `code/core/views.py`: authentication, round management and publishing, checklist readiness, assignment publishing, submission acceptance, and review/grading. Its eight stores are the Django models in SQLite (D6 also covers uploaded files in the local media folder).

## Canonical files

Both diagrams are maintained once in `project-proposal/figures/`. The entries in this folder are symlinks to those files, so there is a single source of truth and nothing is duplicated.

| Entry | Canonical path | Purpose |
|---|---|---|
| `dfd-level-0.drawio` | `project-proposal/figures/dfd-level-0.drawio` | Editable draw.io source (Level 0) |
| `dfd-level-0.pdf` | `project-proposal/figures/dfd-level-0.pdf` | Vector export embedded in the proposal |
| `dfd-level-0.png` | `project-proposal/figures/dfd-level-0.png` | Raster export for this documentation site |
| `dfd-level-1.drawio` | `project-proposal/figures/dfd-level-1.drawio` | Editable draw.io source (Level 1) |
| `dfd-level-1.pdf` | `project-proposal/figures/dfd-level-1.pdf` | Vector export embedded in the proposal |
| `dfd-level-1.png` | `project-proposal/figures/dfd-level-1.png` | Raster export for this documentation site |

## Reading the diagrams

- Rectangles are external entities, ovals are processes, and open-ended rectangles are data stores.
- Arrows describe data movement, not interface navigation or execution order.
- Level 1 reads left to right: external entity, then process, then data store. An entity marked `*` is drawn a second time to avoid crossing lines.
- The two levels are balanced: every flow between an external role and DeadlineDesk in Level 0 appears in Level 1 between that role and one of the processes.
- There is no email or other external service. The T-24h reminder is a row in D2, and the audit trail is D8.

## Previews

### Level 0 — system context

![DeadlineDesk Level 0 data-flow diagram](https://raw.githubusercontent.com/aryanorastar/ucs503p-202627-deadlinedesk/master/project-proposal/figures/dfd-level-0.png)

### Level 1 — implemented processes and data stores

![DeadlineDesk Level 1 data-flow diagram](https://raw.githubusercontent.com/aryanorastar/ucs503p-202627-deadlinedesk/master/project-proposal/figures/dfd-level-1.png)

## Editing and exporting

The `.drawio` files are the only sources. Edit them in draw.io, then export the PDF and PNG from them with draw.io Desktop's command-line tool:

```bash
make diagrams
```

This only exports; nothing in the repository writes `.drawio` files.
