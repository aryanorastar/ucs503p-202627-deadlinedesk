# Week 7: Late-Policy and Integration Testing

## Objective

Demonstrate 100% policy agreement on a fixed automated suite.

## Work completed

- Tested exact deadline acceptance.
- Tested one-second-late rejection.
- Tested configured late penalty.
- Tested grace-window boundary acceptance and one-second-after rejection.
- Tested unknown policy failure.
- Tested a full late-penalty upload through TA grading.
- Tested that a rejected late attempt creates no submission.

## Result

All six policy cases and six workflow/authorization cases pass: 12 tests total.

## Next improvement

Add concurrency testing at the deadline boundary against PostgreSQL and define resubmission/version rules.
