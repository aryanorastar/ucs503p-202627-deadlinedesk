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

The prototype was exercised in the local browser on 25 August 2026.

- Student login, dashboard, placement details, and readiness transition
- Student academic list and policy visibility
- TA login, assignment list, and review queue
- Placement Admin login, reminder log, and effective round status
- Default desktop viewport and 390 x 844 responsive viewport
- Visible labels, focusable native controls, skip link, navigation, and sign-out
- Browser console checked with zero warnings or errors

## Policy oracle

The test oracle follows the SRS table rather than duplicating view implementation. The boundary suite is fixed and deterministic; all six policy cases must pass for the stated 100% agreement metric.

## Remaining test backlog

- Concurrent last-second submission tests on PostgreSQL
- File malware and archive-bomb scanning tests
- Reminder worker retry/idempotency tests
- Grade ownership and course-section authorization tests
- Accessibility automation with axe-core
- Load tests for indexed deadline/status queries
