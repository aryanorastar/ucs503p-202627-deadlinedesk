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

## Week 8 improvement candidates

| Priority | Story | Reason |
|---|---|---|
| P0 | Restrict TAs to their own course sections. | Close authorization gap found in threat review. |
| P0 | Add edit/cancel flows with audit detail. | Correct mistakes without database-admin access. |
| P1 | Add resubmission policy and version history. | One submission is too restrictive for real courses. |
| P1 | Add a reminder worker with retry-safe email adapter. | Convert the Week 7 log into delivery. |
| P1 | Deploy staging with PostgreSQL and managed files. | Enable pilot access and concurrency testing. |
| P2 | Add assignment/round filters and pagination. | Prepare for larger deadline volume. |

## Deferred by scope decision

- NLP plagiarism detection
- Mobile native app
- WhatsApp integration
- Placement interview scoring
- Advanced analytics dashboard

These do not improve the Week 7 end-to-end proof enough to justify their delivery risk.
