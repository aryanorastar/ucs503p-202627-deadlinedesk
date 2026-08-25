# Software Requirements Specification

**Product:** DeadlineDesk<br>
**Version:** Week 7 prototype, 0.1<br>
**Date:** 25 August 2026

## Purpose and scope

DeadlineDesk provides one authenticated system for two campus deadline workflows: placement-round readiness and academic assignment submission. The Week 7 scope is intentionally thin but end-to-end. Email reminders, production hosting, PostgreSQL, analytics dashboards, and advanced similarity detection are outside this increment.

## Stakeholders and actors

| Actor | Goal | Authorized actions |
|---|---|---|
| Student | Meet deadlines and see outcomes | View published rounds and assignments, complete checklist items, upload one submission, view late status and grade |
| TA / Faculty | Apply academic policy consistently | Publish assignments, inspect submissions, start review, publish score and feedback |
| Placement Admin | Publish structured placement windows | Create companies/rounds/checklists, publish rounds, inspect reminder logs |
| Course evaluator | Verify software-engineering evidence | Run tests, inspect CI, follow demo script, trace requirements to tests |

## Functional requirements

| ID | Requirement | Week 7 acceptance criterion |
|---|---|---|
| FR-AUTH-01 | The system shall authenticate users with a server-side session. | Valid demo credentials open the matching portal; invalid credentials do not authenticate. |
| FR-AUTH-02 | The system shall enforce Student, TA, and Placement Admin permissions. | A Student request to an admin-only creation page returns HTTP 403. |
| FR-PL-01 | A Placement Admin shall create companies and placement rounds. | A round persists with opening, closing, and draft status. |
| FR-PL-02 | A Placement Admin shall add required or optional checklist items. | Items appear in the round in configured order. |
| FR-PL-03 | Publishing a round shall expose it to students. | A published round is listed for Student users; drafts are hidden. |
| FR-PL-04 | Publishing shall persist a T-24h reminder record. | Reminder time equals closing time minus 24 hours. |
| FR-PL-05 | A Student shall toggle checklist completion. | Completion is unique per student/item and readiness becomes true when all required items are complete. |
| FR-AC-01 | A TA shall publish an assignment with a due time and late policy. | Assignment is visible with reject, penalty, or grace configuration. |
| FR-AC-02 | A Student shall upload one file per assignment. | Accepted file is stored with server submission timestamp. |
| FR-AC-03 | The system shall evaluate lateness automatically. | Boundary tests agree with the configured policy for exact deadline, rejection, penalty, and grace cases. |
| FR-AC-04 | The system shall calculate an explicit similarity stub. | Text uploads receive maximum Jaccard token overlap against earlier submissions; unsupported content returns 0. |
| FR-AC-05 | A TA shall review and grade a submission. | Status becomes graded and the Student sees score and feedback. |
| FR-AUD-01 | The system shall persist important domain actions. | Audit rows record actor, action, entity, detail, and timestamp. |

## Late-policy rules

Let `t` be the server submission timestamp and `d` be the assignment due time.

| Policy | Decision |
|---|---|
| Any policy, `t <= d` | Accept as on time; penalty 0% |
| Reject, `t > d` | Reject; do not create a submission |
| Accept with penalty, `t > d` | Accept as late; apply configured percentage |
| Grace window, `d < t <= d + grace` | Accept in grace; penalty 0% |
| Grace window, `t > d + grace` | Reject; do not create a submission |

The server timestamp is authoritative. Browser time is not used for the decision.

## Non-functional requirements

| ID | Requirement | Measure |
|---|---|---|
| NFR-SEC-01 | State-changing browser requests shall use CSRF protection. | Django CSRF middleware and form tokens enabled. |
| NFR-SEC-02 | Passwords shall never be stored in plaintext. | Django password hashers used through `set_password` / `create_user`. |
| NFR-SEC-03 | Student uploads shall be accessible only to the owner and staff roles. | Files are served through an authenticated download view; cross-student access returns HTTP 403. |
| NFR-REL-01 | The fixed late-policy suite shall have 100% agreement. | Six of six late-policy tests pass. |
| NFR-MNT-01 | Domain decisions shall be isolated from request rendering. | Late evaluation and similarity stub live in `core/services.py`. |
| NFR-ACC-01 | Core flows shall be keyboard accessible. | Semantic labels, visible focus, skip link, native controls, and contrast-aware themes. |
| NFR-RSP-01 | Pages shall support phone and desktop widths. | Browser QA at default width and 390 px without horizontal content loss. |
| NFR-OPS-01 | Every push shall run build checks and tests. | GitHub Actions application CI. |

## Data and retention

The prototype uses SQLite and local media storage. Uploaded files are limited to 5 MB and selected academic/source/archive extensions. No automated deletion policy is implemented in Week 7. Production use requires managed storage, malware scanning, retention rules, backups, and privacy approval.

## Assumptions and constraints

- One active submission per student per assignment.
- Placement reminder delivery is a database log only.
- A TA may grade any academic submission in the prototype.
- Staff accounts are simulated for the pilot.
- All displayed deadline times use Asia/Kolkata.
