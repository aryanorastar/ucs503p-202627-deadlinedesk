# Week 7 Demo Guide

## Prepare

```shell
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python code/manage.py migrate
./.venv/bin/python code/manage.py seed_demo
./.venv/bin/python code/manage.py runserver
```

Keep a second terminal ready for:

```shell
./.venv/bin/python -m pytest
```

## Seven-minute demonstration

### 1. Frame the problem (30 seconds)

Placement and academic deadlines currently arrive through disconnected channels. DeadlineDesk proves that both workflows can share authentication, policy decisions, status history, and audit evidence.

### 2. Placement Admin path (90 seconds)

Sign in as `placement / Placement@W7`.

1. Open Placement and show the sample company/round.
2. Explain draft versus effective published/open/closed state.
3. Show the required document checklist.
4. Show the T-24h reminder log created at publish time.

### 3. Student placement path (60 seconds)

Sign in as `student / Student@W7`.

1. Open the published Northstar Systems round.
2. Toggle each required document.
3. Show the readiness result change to "Ready to apply."

### 4. Academic path (150 seconds)

Sign in as `ta / Faculty@W7` and show the assignment plus its grace-window policy. Then sign in as Student.

1. Open the assignment and point out the authoritative due time.
2. Upload a small text file.
3. Show submitted time, late decision, penalty, and similarity-stub warning.
4. Return as TA, start review, and publish a score/feedback.
5. Return as Student and show the grade.

### 5. Engineering evidence (60 seconds)

Run the test suite. Explain the six late-policy boundary tests, authorization test, reminder test, checklist test, and full submission-to-grade integration test.

### 6. Scope honesty (30 seconds)

State clearly: reminders are database logs, similarity is simple text-token overlap, and SQLite/local files are prototype choices. Week 8 prioritizes authorization hardening and staging deployment.

## Likely viva questions

**Why Django?** It provides mature authentication, CSRF, ORM migrations, forms, file handling, and testing, which reduces Week 7 integration risk.

**Why not combine late status with submission state?** Review status and late outcome are independent. A late submission can still move from submitted to reviewed to graded.

**What happens exactly at the deadline?** `submitted_at <= due_at` is on time. The boundary is covered by an automated test.

**Is the similarity score plagiarism detection?** No. It is a labeled Jaccard token-overlap stub for text and returns 0 for unsupported content.

**How will email be added?** A retry-safe worker will consume scheduled ReminderLog rows and record sent time without changing the round-publishing transaction.

**What is the main security gap?** The prototype TA role is global. Production must scope staff actions to their assigned courses or sections.
