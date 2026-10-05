# Use-Case Diagram

The diagram captures the Week 7 DeadlineDesk scope for the three supported roles: Student, TA / Faculty, and Placement Admin.

## Canonical files

The diagram is maintained once in `project-proposal/figures/`. The entries in this folder are symlinks to those files, so there is a single source of truth and nothing is duplicated.

| Entry | Canonical path | Purpose |
|---|---|---|
| `use-case-diagram.drawio` | `project-proposal/figures/use-case-diagram.drawio` | Editable draw.io source |
| `use-case-diagram.pdf` | `project-proposal/figures/use-case-diagram.pdf` | Vector export embedded in the proposal |
| `use-case-diagram.png` | `project-proposal/figures/use-case-diagram.png` | Raster export for this documentation site |

## Reading the diagram

- The rectangle is the DeadlineDesk system boundary; the three stick figures are the actors outside it.
- Ovals are coloured by the actor that owns the use case: blue for Student, green for TA / Faculty, amber for Placement Admin.
- Plain lines are actor–use-case associations. There are no `include` or `extend` dependencies in the Week 7 scope.

## Regenerating

The `.drawio` file is the source of truth; the PDF and PNG are rendered from it.

```bash
python3 project-proposal/scripts/render_diagrams.py
```
