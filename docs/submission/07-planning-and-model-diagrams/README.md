# Planning and model diagrams

The diagram sources are editable in [diagrams.net / Draw.io](https://app.diagrams.net/). The canonical source files and their PDF/PNG previews live together in `project-proposal/figures/`; this index links to them rather than storing a second copy.

| Diagram | Editable Draw.io source | PDF preview | PNG preview |
|---|---|---|---|
| Project Gantt chart, Weeks 3–7 | [gantt-chart.drawio](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/gantt-chart.drawio) | [PDF](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/gantt-chart.pdf) | [PNG](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/gantt-chart.png) |
| Placement Track activity | [activity-placement.drawio](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/activity-placement.drawio) | [PDF](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/activity-placement.pdf) | [PNG](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/activity-placement.png) |
| Academic Dropbox activity | [activity-academic.drawio](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/activity-academic.drawio) | [PDF](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/activity-academic.pdf) | [PNG](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/activity-academic.png) |
| Django entity-relationship (ER) model | [er-diagram.drawio](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/er-diagram.drawio) | [PDF](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/er-diagram.pdf) | [PNG](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/er-diagram.png) |

- **ER model.** Taken from `code/core/models.py` and `migrations/0001_initial.py`. It shows every foreign key, including the four `User` links (`created_by`, `student`, `graded_by`, `actor`), the two unique-together constraints, and the one-to-one `Grade`. `AuditLog.entity_id` is a generic reference, not a foreign key.
- **Activity diagrams.** UML swimlanes for each role and the system. Each decision matches a branch in the views and forms: publishing needs at least one required item; a submission is rejected if it is a duplicate or blocked by the late policy; uploads must be at most 5 MB and an allowed type; the score cannot exceed the maximum.
- **Gantt chart.** Week-level only. Weeks 4–7 come from the team journals; Week 3 is reconstructed from the proposal's combined W3–W4 row and drawn dashed. It makes no day-level estimates.

## Editing and exporting

Each `.drawio` file is the only source for its diagram. After editing one in draw.io, rebuild every PDF and PNG with:

```bash
make diagrams
```

This uses draw.io Desktop's command-line tool and only exports. Nothing in the repository writes `.drawio` files.

## Inline previews

### Project schedule

![DeadlineDesk Gantt chart](https://raw.githubusercontent.com/aryanorastar/ucs503p-202627-deadlinedesk/master/project-proposal/figures/gantt-chart.png)

### Placement Track activity

![Placement Track activity diagram](https://raw.githubusercontent.com/aryanorastar/ucs503p-202627-deadlinedesk/master/project-proposal/figures/activity-placement.png)

### Academic Dropbox activity

![Academic Dropbox activity diagram](https://raw.githubusercontent.com/aryanorastar/ucs503p-202627-deadlinedesk/master/project-proposal/figures/activity-academic.png)

### Django entity-relationship model

![DeadlineDesk entity-relationship diagram](https://raw.githubusercontent.com/aryanorastar/ucs503p-202627-deadlinedesk/master/project-proposal/figures/er-diagram.png)
