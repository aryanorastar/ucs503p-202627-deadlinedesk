![Tiet Logo](assets/tiet-logo.svg){ .tiet-logo }

**UCS503: Software Engineering (Project)**  
**TIET Patiala**

# DeadlineDesk

**Author(s)**:

`(AG)` Aryan Gupta `<agupta15_be24 -at- thapar -dot- edu>`

`(AK)` Aksh Goyal `<agoyal2_be24 -at- thapar -dot- edu>`

`(NB)` Naveen Bansal `<nbansal3_be24 -at- thapar -dot- edu>`

DeadlineDesk is a campus web system for placement
rounds and academic assignment deadlines.  It provides
a placement track (companies, rounds, document
checklists, reminders) and an academic dropbox
(submission, late policy, similarity stub, TA grading)
behind shared authentication and roles.

## Week 7 prototype

The working Django prototype now implements both proposed thin paths, three role-based portals, automated late-policy evaluation, grading, reminder persistence, and an audit trail. See the [SRS](srs.md), [architecture and design](design.md), [test evidence](testing.md), [backlog](backlog.md), and [demo guide](demo.md).

## Reports

- Project proposal: [PDF](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/main.pdf) · [LaTeX source](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-proposal/main.tex)
- Week 4 presentation: [PDF](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/w4/presentation.pdf)
- Prototype-stage report: [PDF](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-report-prototype-stage/main.pdf) · [LaTeX source](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/project-report-prototype-stage/main.tex)
- Complete Week 4–7 submission package: [documents, diagrams, and journals](submission/index.md)

## Installation

The working Django application lives under `code/`.
From the repository root, install the requirements,
apply migrations, seed the demo records, and start the
development server:

``` shell
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python code/manage.py migrate
./.venv/bin/python code/manage.py seed_demo
./.venv/bin/python code/manage.py runserver
```

## Documentation

``` shell
make docs
```

Project page:
[aryanorastar.github.io/ucs503p-202627-deadlinedesk](https://aryanorastar.github.io/ucs503p-202627-deadlinedesk/)
