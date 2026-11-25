# Product Backlog

## Completed through Week 7

| Priority | Story | Acceptance status |
|---|---|---|
| P0 | As a user, I sign in and see only actions for my role. | Done and tested |
| P0 | As Placement Admin, I publish a round with required documents. | Done and tested |
| P0 | As a Student, I complete the round checklist and see readiness. | Done and browser-verified |
| P0 | As the system, I log the T-24h reminder when a round is published. | Done and tested |
| P0 | As a TA, I publish an assignment with a late policy. | Done and browser-verified |
| P0 | As a Student, I submit work and receive the automatic policy outcome. | Done and tested |
| P0 | As a TA, I review and grade a submission. | Done and tested |
| P1 | As an evaluator, I trace requirements to automated tests and CI. | Done |
| P1 | As an evaluator, I open each diagram as an editable draw.io source with matching PDF and PNG exports (`make diagrams`). | Done |

## Final preparation, 25 November 2026

| Priority | Completed scope | Evidence |
|---|---|---|
| P0 | Restrict academic rosters, review, grading and files to the assignment owner; preserve student-owned access. | Ownership regression tests in the [final test catalogue](test-cases/README.md) |
| P0 | Scope dashboard audit activity to the current user and block checklist changes outside an open round. | Privacy/timing regression tests |
| P1 | Supply eight UML types in separate folders, a final schedule and test-case catalogue. | [UML](uml/README.md), [Gantt](gantt-chart/README.md), [tests](test-cases/README.md) |
| P1 | Assemble final report and presentation in the instructor's required structure. | [Final submission index](submission/index.md) |
| P1 | Provide an isolated Gunicorn demo runner and temporary public HTTPS access. | [Demo guide](live-demo.md); actual observations in [verification](final-verification.md) |

Publication and browser verification status belongs in the [final checklist](FINAL_SUBMISSION_CHECKLIST.md). This table records implemented scope, not an uptime guarantee.

## Remaining improvement candidates

| Priority | Story | Reason |
|---|---|---|
| P0 | Add course/section membership beyond assignment ownership. | Assignment-owner checks now exist; institutional course scoping needs a data model. |
| P0 | Add edit/cancel flows with audit detail. | Correct mistakes without database-admin access. |
| P1 | Add resubmission policy and version history. | One submission is too restrictive for real courses. |
| P1 | Add a reminder worker with retry-safe email adapter. | Convert the Week 7 log into delivery. |
| P1 | Add persistent hosting with PostgreSQL and managed files. | The temporary public demo still depends on its application host and tunnel. |
| P2 | Add assignment/round filters and pagination. | Prepare for larger deadline volume. |

## Deferred by scope decision

- NLP plagiarism detection
- Mobile native app
- WhatsApp integration
- Placement interview scoring
- Advanced analytics dashboard

These remain outside the final demonstration scope.
