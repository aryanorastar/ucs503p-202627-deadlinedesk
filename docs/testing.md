# Test Strategy and Evidence

## Verification commands

```shell
./.venv/bin/python -m pytest
./.venv/bin/python code/manage.py check
./.venv/bin/python code/manage.py makemigrations --check
```

Expected Week 7 result: `12 passed` and zero Django system-check issues.

## Requirements traceability

| Test | Requirement(s) | Evidence |
|---|---|---|
| Exact deadline accepted | FR-AC-03 | `test_submission_at_exact_deadline_is_on_time` |
| Reject one second late | FR-AC-03 | `test_reject_policy_blocks_one_second_late` |
| Configured penalty applied | FR-AC-03 | `test_penalty_policy_accepts_and_applies_configured_percentage` |
| Grace boundary accepted | FR-AC-03 | `test_grace_policy_accepts_at_grace_boundary` |
| After grace rejected | FR-AC-03 | `test_grace_policy_rejects_after_grace_boundary` |
| Unknown policy fails closed | NFR-REL-01 | `test_unknown_policy_fails_closed` |
| Student blocked from admin route | FR-AUTH-02 | `test_student_cannot_open_placement_admin_create_page` |
| Publish creates T-24h reminder | FR-PL-03, FR-PL-04 | `test_publishing_round_creates_t_minus_24_hour_reminder` |
| Checklist toggles per student | FR-PL-05 | `test_student_checklist_completion_is_idempotent_toggle` |
| Penalty submission through grade | FR-AC-02 to FR-AC-05 | `test_late_penalty_submission_and_ta_grade_complete_academic_path` |
| Rejected attempt creates no row | FR-AC-03 | `test_reject_policy_does_not_create_late_submission` |
| Student cannot download another student's file | NFR-SEC-03 | `test_student_cannot_download_another_students_submission` |

## Browser QA

The prototype was exercised again in an isolated local browser session on 1 September 2026.

- Placement Admin created a company and round, added a required checklist item, published the round, and verified the T-24h reminder log.
- Student completed that checklist and the UI changed from **Checklist in progress** to **Ready to apply**.
- Student uploaded a real file to the seeded assignment and received an on-time submission record with the similarity stub result.
- TA moved the submission to **Under review**, graded it `92/100`, and added feedback; the student immediately saw the final grade and feedback.
- Direct role violations were checked for Student, TA/Faculty, and Placement Admin; each returned the custom `403` page.
- The Placement Admin dashboard and Student submission record were checked at `390 x 844` with no horizontal overflow.
- Browser console logs were checked after the workflows with zero warnings or errors.

## Policy oracle

The test oracle follows the SRS table rather than duplicating view implementation. The boundary suite is fixed and deterministic; all six policy cases must pass for the stated 100% agreement metric.

## Remaining test backlog

- Concurrent last-second submission tests on PostgreSQL
- File malware and archive-bomb scanning tests
- Reminder worker retry/idempotency tests
- Grade ownership and course-section authorization tests
- Accessibility automation with axe-core
- Load tests for indexed deadline/status queries
