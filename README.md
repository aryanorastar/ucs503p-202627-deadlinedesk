# DeadlineDesk

DeadlineDesk is a role-based campus web system for placement rounds and academic assignment deadlines. This repository is the UCS503P 2026-27 ODD semester project of Aryan Gupta, Aksh Goyal, and Naveen Bansal.

The Week 7 prototype contains two complete thin paths:

1. Placement Admin creates a company and round, adds required checklist items, publishes the round, and creates a T-24h reminder log. A Student completes the checklist and receives a readiness result.
2. TA publishes an assignment with a late policy. A Student submits a file, the system evaluates lateness and runs a transparent similarity stub, and the TA reviews and grades the submission.

## Week 7 status

- Role-based session authentication: Student, TA / Faculty, Placement Admin
- Placement round state and effective open/closed window
- Per-student document checklist and readiness decision
- T-24h reminder persistence
- Assignment late policies: reject, accept with penalty, grace window
- File upload with server timestamp and size/type validation
- Text-token overlap similarity stub, explicitly not a plagiarism detector
- Submission review, grading, feedback, and audit log
- 12 automated tests, including six late-policy boundary tests
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

These credentials are for local demonstration only. Production deployment must set a strong `DEADLINEDESK_SECRET_KEY`, disable debug mode, and create real accounts.

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
| `docs/submission/` | Organized Week 4–7 submission bundle: PPT/PDF, proposal, diagrams, journals, report |
| `journals/` | Weekly technical journal for each team member |
| `project-proposal/` | Week 4 LaTeX proposal and PDF |
| `project-report-prototype-stage/` | Week 7 prototype report source and PDF |
| `w4/` | Week 4 presentation PDF and one-page handout |

## Team

| Name | Roll No. | Primary responsibility |
|---|---|---|
| Aryan Gupta | 1024030764 | Architecture, CI/CD, Placement Track |
| Aksh Goyal | 1024030766 | Academic Dropbox, late-policy tests |
| Naveen Bansal | 1024030767 | UI flows, documentation, demo script |

## Submission links

- [Complete Week 4–7 submission bundle](docs/submission/index.md)
- [PowerPoint presentation](docs/submission/01-presentation/DeadlineDesk_Week4_Presentation.pptx)
- [Project proposal PDF](project-proposal/main.pdf)
- [Week 4 presentation PDF](w4/presentation.pdf)
- [Use-case diagram](docs/submission/03-use-case-diagrams/use-case-diagram.svg)
- [Data-flow diagrams](docs/submission/04-data-flow-diagrams/)
- [Individual team journals](docs/submission/05-team-journals/)
- [Week 7 prototype report PDF](project-report-prototype-stage/main.pdf)
- [Project page](https://aryanorastar.github.io/ucs503p-202627-deadlinedesk/)
- [Repository](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk)

## Scope boundary

The Week 7 reminder channel is a persistent database log, not email delivery. The similarity score is a deterministic token-overlap stub for text files, not an NLP plagiarism system. PostgreSQL and hosted deployment remain later increments.
