# Architecture and Design

## Architectural view

DeadlineDesk uses Django's layered monolith pattern for the Week 7 prototype.

```text
Browser
  -> URL router and role-protected views
      -> Forms and application services
          -> Domain models and policy decisions
              -> Django ORM
                  -> SQLite database and local media
```

This shape keeps deployment simple while preserving boundaries that can later support PostgreSQL, background workers, or an API frontend.

## Component responsibilities

| Component | Responsibility |
|---|---|
| Templates and CSS | Role-specific pages, forms, messages, responsive layout, light/dark tokens |
| Views and decorators | Authentication, authorization, request orchestration, transactions |
| Forms | Server validation for times, policy configuration, uploads, and grades |
| Services | Pure late-policy decision and transparent similarity stub |
| Models | Users, roles, placement/academic entities, constraints, audit log |
| Management command | Deterministic local demo accounts and sample data |
| Test suite | Black-box policy boundaries, authorization, and workflow integration |

## Primary use cases

### Placement Track

```text
Placement Admin -> Create company -> Create draft round
                -> Add required checklist items -> Publish
                -> Persist T-24h reminder log

Student -> Open published round -> Complete each required item
        -> System reports "Ready to apply"
```

### Academic Dropbox

```text
TA -> Publish assignment and late policy
Student -> Upload file
System -> Timestamp -> Evaluate policy -> Similarity stub -> Persist submission
TA -> Start review -> Publish score and feedback
Student -> View late outcome and grade
```

## State models

### Placement round

```text
draft -> published -> open -> closed -> archived
```

`open` and `closed` are calculated from the published round's timestamps. Draft and archived remain explicit states.

### Submission

```text
submitted -> under_review -> graded
```

Late outcome is an orthogonal attribute: `on_time`, `grace`, or `penalty`. A rejected attempt creates no submission.

## Domain model

| Entity | Important relationships / constraints |
|---|---|
| User | Role is Student, TA, or Placement Admin |
| Company | Created by Placement Admin; has many rounds |
| PlacementRound | Belongs to Company; has checklist items and reminder logs |
| ChecklistItem | Required/optional and ordered within a round |
| ChecklistCompletion | Unique for one Student and one ChecklistItem |
| ReminderLog | Belongs to a round; scheduled/sent status |
| Assignment | Created by TA; due time and one late-policy configuration |
| Submission | Unique for one Student and one Assignment; owns uploaded file |
| Grade | One-to-one with Submission |
| AuditLog | Actor plus action and generic entity reference |

## Design decisions

### Django and server-rendered pages

Django was selected because the prototype needs secure sessions, role guards, forms, file uploads, persistence, migrations, and tests more than it needs frontend framework complexity. Server rendering reduces integration risk for the Week 7 demonstration.

### SQLite now, PostgreSQL later

SQLite makes setup deterministic for evaluators. The application uses the ORM and avoids SQLite-specific queries, so later migration to PostgreSQL is straightforward.

### Similarity as an explicit stub

For UTF-8 text, the system computes the maximum Jaccard overlap of normalized tokens against earlier submissions to the same assignment. Binary and unsupported text return 0. The UI explicitly warns that this is not a plagiarism verdict.

### Reminder database-first design

Publishing stores the intended T-24h delivery record. A future background worker can consume scheduled rows and send email without changing the placement workflow.

## Security controls and known gaps

Implemented controls: password hashing, CSRF, session authentication, route-level authorization, server validation, upload size/type limits, unique database constraints, and transactional publish/grade flows.

Known prototype gaps: development secret fallback, debug mode default, no malware scanning, no object-storage isolation, no rate limiting, no staff ownership restriction during grading, no email verification, and no production deployment hardening.
