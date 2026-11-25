"""Build a traceable test-case catalogue from a real pytest JUnit result."""
from pathlib import Path
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/test-cases"
RESULT = ROOT / "tmp/final-qa/junit.xml"
CASES = {
    "test_demo_seed_refreshes_without_duplicating_schedule": ("Repeatable demo startup", "NFR-REL-01", "Run the synthetic demo seed command twice.", "Exactly three users, one company, one round, three checklist items, one assignment and one updated reminder. Existing reminder identity is preserved."),
    "test_submission_at_exact_deadline_is_on_time": ("Exact deadline", "FR-AC-03", "Evaluate an upload at the exact due timestamp.", "Accepted on time with no penalty."),
    "test_reject_policy_blocks_one_second_late": ("One second late", "FR-AC-03", "Apply reject policy one second after the due timestamp.", "Rejected, with no accepted late status."),
    "test_penalty_policy_accepts_and_applies_configured_percentage": ("Configured penalty", "FR-AC-03", "Apply penalty policy to a late timestamp with a 15 percent penalty.", "Accepted with penalty status and the configured 15 percent."),
    "test_grace_policy_accepts_at_grace_boundary": ("Grace boundary", "FR-AC-03", "Submit exactly 30 minutes after the due time with 30 minutes of grace.", "Accepted in the grace window."),
    "test_grace_policy_rejects_after_grace_boundary": ("After grace", "FR-AC-03", "Submit one second after the configured grace boundary.", "Rejected."),
    "test_unknown_policy_fails_closed": ("Unsupported late policy", "NFR-REL-01", "Evaluate a late timestamp using an unknown policy name.", "ValueError prevents silently accepting an unsupported late policy."),
    "test_student_cannot_open_placement_admin_create_page": ("Placement role denial", "FR-AUTH-02", "Sign in as Student and request the company-create page.", "HTTP 403."),
    "test_publishing_round_creates_t_minus_24_hour_reminder": ("Publication reminder", "FR-PL-03 / FR-PL-04", "Publish a draft round containing a required checklist item.", "Published state and a reminder record exactly 24 hours before closing."),
    "test_student_checklist_completion_is_idempotent_toggle": ("Checklist toggle", "FR-PL-05", "Toggle an open round item twice as the same Student.", "First request adds completion, second removes it. This is a toggle, not HTTP retry idempotency."),
    "test_late_penalty_submission_and_ta_grade_complete_academic_path": ("Penalty-to-grade workflow", "FR-AC-02 to FR-AC-05", "Upload late under a 20 percent penalty, then grade as the assignment owner.", "One accepted submission with penalty 20 and a stored grade of 82/100."),
    "test_reject_policy_does_not_create_late_submission": ("Rejected upload persistence", "FR-AC-03", "Upload after a reject-policy deadline.", "Redirect with rejection feedback and no Submission row."),
    "test_student_cannot_download_another_students_submission": ("Student file privacy", "NFR-SEC-03", "Request another student's uploaded file.", "HTTP 403 without file disclosure."),
    "test_submission_access_rejects_unrelated_users": ("Submission ownership", "NFR-SEC-03", "Create an unrelated user in the parameterized role and request the indicated detail/download/review/grade route.", "HTTP 403 and no grade creation for each role and route combination."),
    "test_checklist_changes_require_open_round": ("Checklist time guard", "FR-PL-05", "Post a checklist change against a draft, archived, closed or future round, as indicated by the parameters.", "HTTP 403 and no ChecklistCompletion row."),
    "test_dashboard_does_not_expose_other_users_activity": ("Audit feed privacy", "NFR-SEC-03", "Create an audit event for a TA, then load the Student dashboard.", "Dashboard loads and its activity context excludes the TA event."),
    "test_ta_cannot_view_other_assignment_roster": ("TA roster ownership", "FR-AUTH-02", "Open another TA's assignment and list assignments as the unrelated TA.", "Detail returns 403, and the list excludes the other TA's assignment."),
    "test_invalid_upload_creates_no_submission": ("Upload validation", "FR-AC-02", "Upload the parameterized blocked extension or file exceeding 5 MiB.", "Form reports a file error and creates no submission."),
    "test_login_logout_and_csrf_boundary": ("Login, logout and CSRF", "FR-AUTH-01 / NFR-SEC-01", "Try anonymous dashboard access, login without CSRF, invalid credentials, valid CSRF login and POST logout.", "Anonymous access redirects, missing CSRF returns 403, bad credentials stay on the form, valid login reaches dashboard and logout ends access."),
    "test_publish_without_required_item_fails_and_repeat_is_deduplicated": ("Publication precondition and repeat", "FR-PL-03", "Publish without an item, add a required item, then publish twice.", "First attempt remains draft without reminder. Later attempts leave exactly one matching reminder."),
    "test_duplicate_upload_and_invalid_grade_preserve_existing_data": ("Duplicate, grade validation and persistence", "FR-AC-02 / FR-AC-05", "Upload twice, submit a score above the maximum, then review and grade correctly. Try reviewing the graded record and download as the student.", "Original file remains the only submission. Invalid score creates no grade. Final state stays graded and the student sees feedback and original bytes."),
}


def escape(value):
    return "".join({"&":r"\&", "%":r"\%", "$":r"\$", "#":r"\#", "_":r"\_", "{":r"\{", "}":r"\}"}.get(c,c) for c in value)


root = ET.parse(RESULT).getroot()
rows=[]
for i,test in enumerate(root.iter("testcase"), 1):
    name=test.attrib["name"]
    base=name.split("[")[0]
    title, requirement, steps, expected=CASES[base]
    parameters=name[len(base):]
    status="PASS" if not any(test.find(tag) is not None for tag in ("failure","error","skipped")) else "NOT PASSED"
    rows.append(dict(id=f"TC-{i:02}", title=title, parameters=parameters, requirement=requirement, steps=steps, expected=expected, source=name, result=status))
if any(r["result"] != "PASS" for r in rows):
    raise SystemExit("Cannot publish passing evidence: one or more tests did not pass.")
OUT.mkdir(exist_ok=True)
(OUT/"results.json").write_text(json.dumps({"date":"2026-11-25", "command":"python -m pytest -q --junitxml=tmp/final-qa/junit.xml", "passed":len(rows), "cases":rows}, indent=2)+"\n")
body=[r"\subsection*{Automated test catalogue}", f"Run date: 25 November 2026. Result: {len(rows)} passed, zero failed. Python 3.12 with Django 5.2.5. The Django client exercises the application and database; live browser checks are recorded separately.", r"\begingroup\raggedright\emergencystretch=3em", r"\begin{enumerate}"]
for row in rows:
    body += [r"\item \begin{minipage}[t]{\linewidth}\textbf{"+escape(row["id"]+" "+row["title"]+" "+row["parameters"])+r"} ("+escape(row["requirement"])+r")\par", r"\textbf{Steps:} "+escape(row["steps"])+r"\par", r"\textbf{Expected and observed:} "+escape(row["expected"])+r" \textbf{PASS}.\par", r"{\footnotesize Source: \nolinkurl{"+row["source"]+r"}}\end{minipage}"]
body += [r"\end{enumerate}", r"\endgroup"]
(OUT/"catalog.tex").write_text("\n\n".join(body)+"\n")
(OUT/"test-cases.tex").write_text(r"""\documentclass[11pt,a4paper]{article}
\usepackage[margin=22mm]{geometry}
\usepackage{hyperref,xurl,enumitem}
\setlist{itemsep=12pt}
\title{DeadlineDesk: Test Cases and Results}
\author{Aryan Gupta, Aksh Goyal and Naveen Bansal}
\date{25 November 2026}
\begin{document}
\maketitle
\input{catalog.tex}
\section*{Verification limits}
This catalogue covers deterministic policy boundaries and application integration. It does not claim load, malware-scanning or concurrent PostgreSQL verification. Test users and media are isolated fixtures. The binary-file similarity measure can be non-zero and remains a teaching stub.
\end{document}
""")
(OUT/"README.md").write_text(f"# Test cases and results\n\n[PDF catalogue](test-cases.pdf) · [LaTeX source](test-cases.tex) · [Machine-readable results](results.json)\n\nRun on **25 November 2026**: **{len(rows)} passed**, zero failed. Each parameterized role/route combination is a separate test case. The PDF records steps, expected behavior, observed result and the source test name.\n\n[Live demonstration and browser evidence](../final-verification.md)\n\n```shell\npython -m pytest -q --junitxml=tmp/final-qa/junit.xml\npython scripts/build_test_catalog.py\ncd docs/test-cases && tectonic test-cases.tex\n```\n")
print(f"Published catalogue source for {len(rows)} passing test cases.")
