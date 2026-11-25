# DeadlineDesk

DeadlineDesk is a role-based campus web system for placement rounds and academic assignment deadlines. This repository is the UCS503P 2026-27 ODD semester project of Aryan Gupta, Aksh Goyal, and Naveen Bansal.

The application connects two campus workflows:

1. Placement Admin creates a company and round, adds required checklist items, publishes the round, and creates a T-24h reminder log. A Student completes the checklist and receives a readiness result.
2. TA publishes an assignment with a late policy. A Student submits a file, the system evaluates lateness and runs a transparent similarity stub, and the TA reviews and grades the submission.

## Final submission

Evaluation: **Tuesday, 1 December 2026, 8:00 AM, Lab 105**.

- [Complete submission index](docs/submission/index.md)
- [Final report: PDF and LaTeX](docs/submission/08-final-report/README.md)
- [Final presentation: PDF, PowerPoint and slide previews](docs/submission/09-final-presentation/README.md)
- [Eight UML diagram types in individual folders](docs/uml/README.md)
- [Gantt chart PDF and editable source](docs/gantt-chart/README.md)
- [Test cases and recorded results](docs/test-cases/README.md)
- [Public application demo and startup guide](docs/live-demo.md)
- [Final verification evidence](docs/final-verification.md)
- [GitHub Pages documentation](https://aryanorastar.github.io/ucs503p-202627-deadlinedesk/)

The final presentation follows the required order: Introduction, Background, Problem Statement, Your Solution, Results. The final report has a dedicated section containing all eight UML diagrams, the Gantt chart and the test cases. The proposal and Week 7 prototype artifacts remain as milestone records.

## Implemented behavior

- Role-based session authentication: Student, TA / Faculty, Placement Admin
- Placement round state and effective open/closed window
- Per-student document checklist and readiness decision
- T-24h reminder persistence
- Assignment late policies: reject, accept with penalty, grace window
- File upload with server timestamp and size/type validation
- Text-token overlap similarity stub, explicitly not a plagiarism detector
- Submission review, grading and downloads restricted to the assignment owner and submitting student
- Current-user audit activity and checklist changes only during an open round
- 36 automated tests, including six late-policy boundary tests, ownership/privacy regression cases and demo-seed repeat safety
- GitHub Actions for application tests and MkDocs deployment
- SRS, architecture/design, backlog, testing evidence, demo script, and weekly journals

## Run locally

Python 3.11 or newer is required.

```shell
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python code/manage.py migrate
./.venv/bin/python code/manage.py seed_demo
./.venv/bin/python code/manage.py runserver
```

Open <http://127.0.0.1:8000/>.

### Demo accounts

| Role | Username | Password |
|---|---|---|
| Student | `student` | `Student@W7` |
| TA / Faculty | `ta` | `Faculty@W7` |
| Placement Admin | `placement` | `Placement@W7` |

These accounts are for the isolated synthetic-data demonstration. A permanent service must use a strong `DEADLINEDESK_SECRET_KEY`, disable debug mode, and create real accounts. The [demo guide](docs/live-demo.md) explains the temporary public URL and its host/tunnel lifetime.

## Test

```shell
./.venv/bin/python -m pytest
./.venv/bin/python code/manage.py check
./.venv/bin/python code/manage.py makemigrations --check
```

## Repository map

| Path | Purpose |
|---|---|
| `code/` | Django application, migrations, templates, CSS, tests, demo seed command |
| `docs/` | SRS, design, testing, backlog, demo guide, course documentation |
| `docs/submission/` | Final evaluation index and preserved Week 4/7 milestone artifacts |
| `docs/uml/` | Eight UML types in individual folders, with draw.io/PDF/PNG files |
| `docs/gantt-chart/`, `docs/test-cases/` | Final schedule and test-case catalogue |
| `journals/` | Weekly technical journal for each team member |
| `project-proposal/` | Updated proposal source, diagrams and PDF (scope through Week 7) |
| `project-report-prototype-stage/` | Week 7 prototype report source and PDF |
| `project-report-final/` | Final report LaTeX source and PDF |
| `scripts/` | Isolated demo runner and artifact preparation/export commands |
| `w4/` | Week 4 presentation PDF and one-page handout |

See [`docs/repository-structure.md`](docs/repository-structure.md) for the canonical-versus-submission folder map.

## Team

| Name | Roll No. | Primary responsibility |
|---|---|---|
| Aryan Gupta | 1024030764 | Architecture, CI/CD, Placement Track |
| Aksh Goyal | 1024030766 | Academic Dropbox, late-policy tests |
| Naveen Bansal | 1024030767 | UI flows, documentation, demo script |

## Submission links

- [Complete final submission bundle](docs/submission/index.md)
- [Week 7 presentation preview (PDF and all 13 inline slides)](docs/submission/01-presentation/README.md)
- [Editable Week 7 PowerPoint](docs/submission/01-presentation/DeadlineDesk_Week7_Presentation.pptx)
- [Project proposal PDF](project-proposal/main.pdf)
- [Week 4 presentation PDF](w4/presentation.pdf)
- [Use-case diagram PDF](project-proposal/figures/use-case-diagram.pdf)
- [DFD Level 0 PDF](project-proposal/figures/dfd-level-0.pdf)
- [DFD Level 1 PDF](project-proposal/figures/dfd-level-1.pdf)
- [Gantt, activity, ER, class and sequence diagrams (editable Draw.io sources and previews)](docs/submission/07-planning-and-model-diagrams/README.md)
- [Individual team journals](journals/README.md) · [submission copy](docs/submission/05-team-journals/)
- [Week 7 prototype report PDF](project-report-prototype-stage/main.pdf)
- [Project page](https://aryanorastar.github.io/ucs503p-202627-deadlinedesk/)
- [Repository](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk)

## Scope boundary

Reminder publication stores a database record; email delivery remains future work. The similarity score is a token-overlap teaching stub, with possible non-zero results for binary files. The public demo uses SQLite and local media under a single application host. Managed PostgreSQL, malware scanning, institutional SSO and durable production hosting remain future work.
