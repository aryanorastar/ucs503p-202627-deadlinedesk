# Planning and model diagrams

The diagram sources are editable in [diagrams.net / Draw.io](https://app.diagrams.net/). The canonical source files and their PDF/PNG previews live together in `project-proposal/figures/`; this index links to them rather than storing a second copy.

| Diagram | Editable Draw.io source | PDF preview | PNG preview |
|---|---|---|---|
| Project Gantt chart, Weeks 3–7 | [gantt-chart.drawio](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/gantt-chart.drawio) | [PDF](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/gantt-chart.pdf) | [PNG](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/gantt-chart.png) |
| Placement Track activity | [activity-placement.drawio](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/activity-placement.drawio) | [PDF](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/activity-placement.pdf) | [PNG](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/activity-placement.png) |
| Academic Dropbox activity | [activity-academic.drawio](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/activity-academic.drawio) | [PDF](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/activity-academic.pdf) | [PNG](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/activity-academic.png) |
| Django entity-relationship (ER) model | [er-diagram.drawio](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/er-diagram.drawio) | [PDF](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/er-diagram.pdf) | [PNG](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/er-diagram.png) |
| UML class diagram | [class-diagram.drawio](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/class-diagram.drawio) | [PDF](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/class-diagram.pdf) | [PNG](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/class-diagram.png) |
| Sequence: sign-in and role-based access | [sequence-authentication.drawio](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/sequence-authentication.drawio) | [PDF](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/sequence-authentication.pdf) | [PNG](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/sequence-authentication.png) |
| Sequence: Placement Admin publishes a round | [sequence-placement-publish.drawio](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/sequence-placement-publish.drawio) | [PDF](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/sequence-placement-publish.pdf) | [PNG](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/sequence-placement-publish.png) |
| Sequence: student views a round and completes checklist items | [sequence-placement-readiness.drawio](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/sequence-placement-readiness.drawio) | [PDF](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/sequence-placement-readiness.pdf) | [PNG](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/sequence-placement-readiness.png) |
| Sequence: student submits an assignment | [sequence-submission.drawio](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/sequence-submission.drawio) | [PDF](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/sequence-submission.pdf) | [PNG](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/sequence-submission.png) |
| Sequence: TA reviews and grades a submission | [sequence-review-grade.drawio](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/sequence-review-grade.drawio) | [PDF](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/sequence-review-grade.pdf) | [PNG](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/figures/sequence-review-grade.png) |

- **ER model.** Taken from `code/core/models.py` and `migrations/0001_initial.py`. It shows every foreign key, including the four `User` links (`created_by`, `student`, `graded_by`, `actor`), the two unique-together constraints, and the one-to-one `Grade`. `AuditLog.entity_id` is a generic reference, not a foreign key.
- **Activity diagrams.** UML swimlanes for each role and the system. Each decision matches a branch in the views and forms: publishing needs at least one required item; a submission is rejected if it is a duplicate or blocked by the late policy; uploads must be at most 5 MB and an allowed type; the score cannot exceed the maximum.
- **Gantt chart.** Week-level only. Weeks 4–7 come from the team journals; Week 3 is reconstructed from the proposal's combined W3–W4 row and drawn dashed. It makes no day-level estimates.
- **Class diagram.** Shows the Week 7 code in `code/core`: the ten models with their fields, enumerations and foreign-key associations, plus the views, forms, services and decorators. Views and services are module-level functions, so they appear as `«module»` classifiers. `LateDecision` is the frozen dataclass returned by `evaluate_lateness`.
- **Sequence diagrams.** Each one traces a single view in `code/core/views.py`. An `alt` or `opt` fragment appears only where that view actually branches. Notes mark behaviour the code does not have, for example that publishing records a reminder as `scheduled` but sends nothing.

### Implemented flows without a sequence diagram

`company_create`, `round_create`, `checklist_create` and `assignment_create` are single-form create views (validate, save, write an audit row), and `submission_download` streams the stored file after an ownership check. These views appear in the class diagram but have no sequence diagram of their own.

### Not implemented in Week 7 (future work)

These flows are not drawn because they are not in the code:

- Reminder delivery. Nothing sends a reminder, sets `ReminderLog.status` to `sent` or fills in `sent_at`, and there is no scheduler or background job.
- Email or any other notification channel.
- Resubmission. A student can submit once per assignment, enforced by the view and by a database constraint.
- TA course scoping. Any TA can review or grade any submission.
- Blocking checklist changes after a round closes. `checklist_toggle` does not check the round status.

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

### UML class diagram

![UML class diagram](https://raw.githubusercontent.com/aryanorastar/ucs503p-202627-deadlinedesk/master/project-proposal/figures/class-diagram.png)

### Sequence: sign-in and role-based access

![Sequence: sign-in and role-based access](https://raw.githubusercontent.com/aryanorastar/ucs503p-202627-deadlinedesk/master/project-proposal/figures/sequence-authentication.png)

### Sequence: Placement Admin publishes a round

![Sequence: Placement Admin publishes a round](https://raw.githubusercontent.com/aryanorastar/ucs503p-202627-deadlinedesk/master/project-proposal/figures/sequence-placement-publish.png)

### Sequence: student views a round and completes checklist items

![Sequence: student views a round and completes checklist items](https://raw.githubusercontent.com/aryanorastar/ucs503p-202627-deadlinedesk/master/project-proposal/figures/sequence-placement-readiness.png)

### Sequence: student submits an assignment

![Sequence: student submits an assignment](https://raw.githubusercontent.com/aryanorastar/ucs503p-202627-deadlinedesk/master/project-proposal/figures/sequence-submission.png)

### Sequence: TA reviews and grades a submission

![Sequence: TA reviews and grades a submission](https://raw.githubusercontent.com/aryanorastar/ucs503p-202627-deadlinedesk/master/project-proposal/figures/sequence-review-grade.png)
