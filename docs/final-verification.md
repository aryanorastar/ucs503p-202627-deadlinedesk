# Final application and artifact verification

Verified on **25 November 2026** against the final-submission working tree. The public demo uses synthetic data, Gunicorn 23.0.0, Django 5.2.5 and Python 3.12 with debug disabled. GitHub Actions records the checks for the published commit.

## Automated verification

**36 cases passed, zero failed.** The [test-case catalogue](test-cases/README.md) records each parameterized case, its steps, expected result and observed pass. Tests use isolated databases and temporary media rather than the normal development database.

```shell
python -m pytest -q --tb=short --junitxml=tmp/final-qa/junit.xml
python code/manage.py check
python code/manage.py makemigrations --check
python code/manage.py collectstatic --noinput
python -m mkdocs build --strict
```

The suite covers six late-policy boundaries, placement publication/reminders, student checklist changes, upload-to-grade integration, private downloads, twelve unrelated-user route combinations, four non-open checklist states, current-user audit feeds, TA roster ownership, invalid uploads, CSRF/login/logout, duplicate/grade preservation and repeated demo seeding.

## Public HTTPS browser walkthrough

The browser exercised the [running temporary application](live-demo.md), not only a Django test client.

| Check | Observed result |
|---|---|
| Incorrect password | Sign-in form showed an error and stayed unauthenticated. |
| Student, TA and Placement Admin sign-in | Each reached its corresponding dashboard. POST sign-out returned to sign-in. |
| Placement Admin company and round creation | A synthetic company and draft round persisted. |
| Publish without required item | Form feedback requested a required checklist item; round stayed draft. |
| Add item and publish | Round became Open and a T-24h reminder record appeared. |
| Student checklist | Completing every required item changed the result to **Ready to apply**. |
| TA assignment publication | Missing grace duration showed a validation error; entering 60 minutes published the assignment and displayed its policy. |
| Student real file upload | A synthetic source-code file produced an accepted on-time submission with a server timestamp and labeled similarity stub. |
| TA review | Status changed from Submitted to Under review. |
| Invalid score | 101/100 showed **Score cannot exceed the maximum score** and did not publish a grade. |
| Valid grade | 92/100 and feedback persisted. The student saw the same result after a fresh sign-in. |
| Authenticated download | The student's download completed. The automated test also verifies exact original file bytes. |
| Placement Admin opens academic submission | Custom **403 Access denied** page. |
| Student opens company-create route | Custom **403 Access denied** page. |
| Console | Zero captured application console errors or warnings during the reviewed workflows. |

## Responsive regression

A long submitted filename initially caused horizontal overflow on a narrow screen. The fix gives grid children a zero minimum width and wraps long file links and feedback. The final browser check measured **325 CSS pixels** for both viewport and document width on the narrow view, and **1200 CSS pixels** for both on the desktop view. No horizontal document overflow remained on the submission page. This is a targeted responsive check, not an accessibility certification.

The measurements came from the browser's actual CSS viewport and document dimensions, rather than the requested device preset. Browser screenshot exports were clipped by the capture surface's scaling, so those captures are retained privately and are not used as published layout evidence.

## Document and diagram checks

The final report compiles from LaTeX and includes its dedicated section containing eight UML types, Gantt chart and all test cases. Each UML folder supplies editable draw.io XML, a one-page PDF and PNG. Diagram review checked labels, edge routing, unique XML IDs and valid edge references. Historical milestone sources remain available.

The final presentation has 16 slides in the instructor's five-section order: Introduction, Background, Problem Statement, Your Solution, Results. Its editable PowerPoint passed package, layout and font validation and a first-party import check. All slides were visually inspected. PDF conversion used LibreOffice after the authoring runtime's native PDF export was unavailable; the resulting PDF has searchable text. No PowerPoint-native visual verification is claimed.

The application changes also received an independent source review focused on private records, ownership checks, CSRF, debug-off startup, static files and the synthetic deployment. No concrete blocking defect was found within that review scope.

## Limits and demonstration lifetime

The public endpoint is a temporary tunnel and requires this host, Gunicorn and the tunnel process to remain active. Restarting the tunnel changes its URL. Reopen the live link before evaluation and follow the [startup guide](live-demo.md) if it has expired. The Dockerfile is supplied for persistent hosting but has not been built or deployed in this verification.

No claim is made for production uptime, malware detection, institutional SSO, external reminder delivery, high load or PostgreSQL concurrency. Similarity remains a token-overlap teaching stub. Test passes and a working demonstration do not remove those boundaries.
