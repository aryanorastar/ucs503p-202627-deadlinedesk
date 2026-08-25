# Week 6: Dropbox and Grading Implementation

## Objective

Implement the complete academic thin path from assignment publication through grading.

## Work completed

- Built the assignment form with policy-specific validation.
- Added 5 MB file validation and supported academic/source/archive extensions.
- Applied the server timestamp and late decision inside a database transaction.
- Added a transparent token-overlap similarity stub for UTF-8 text.
- Added submitted, under-review, and graded state transitions.
- Added grade score/max validation and student-visible feedback.

## Scope note

The similarity output is explicitly labeled as a stub and not a plagiarism verdict. Binary files receive a zero stub score.
