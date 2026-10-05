# Data-Flow Diagrams

The Level 0 context diagram treats DeadlineDesk as one process. The Level 1 diagram decomposes it into authentication, Placement Track, Academic Dropbox, and reminder/audit processes with their persistent stores.

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
- Level 1 reads left to right: external entity, then process, then data store. Process-to-process events run vertically down the centre column.

## Regenerating

The `.drawio` files are the source of truth; the PDF and PNG exports are rendered from them.

```bash
python3 project-proposal/scripts/render_diagrams.py
```
