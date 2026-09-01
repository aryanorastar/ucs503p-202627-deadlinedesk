# Week 5: Academic Workflow and Policy Specification

## Objective

Turn the proposal's late-policy idea into unambiguous, testable rules.

## Work completed

- Defined Assignment, Submission, and Grade responsibilities.
- Separated review state from late outcome.
- Specified exact-boundary behavior: a server timestamp equal to the due time is on time.
- Defined reject, accept-with-penalty, and grace-window decisions.
- Wrote the initial black-box test table and requirements traceability IDs.

## Technical decision

Rejected attempts do not create a Submission row. This prevents a blocked upload from later appearing as accepted work and gives tests a clear database oracle.
