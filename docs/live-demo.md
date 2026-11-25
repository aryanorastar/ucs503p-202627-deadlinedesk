# Live application demonstration

Evaluation: **1 December 2026, 8:00 AM, Lab 105**.

[Open the temporary DeadlineDesk application](https://complete-guarantee-probability-learned.trycloudflare.com/)

This URL exposes a Gunicorn/Django process through a temporary HTTPS tunnel. It uses an isolated synthetic database and media directory. The application host and tunnel must remain running. Restarting the tunnel creates a new URL, which must be updated here before sharing. There is no uptime guarantee through evaluation day.

The [GitHub Pages site](https://aryanorastar.github.io/ucs503p-202627-deadlinedesk/) contains documentation and artifacts. It does not run Python; use the application link above for sign-in and workflows. See [final verification](final-verification.md) for the checks actually completed.

The preparation run on 25 November verified all three role logins, invalid-login feedback, student readiness, a real synthetic-file upload, owner review and a 92/100 grade, rejection of 101/100, feedback after student sign-in, placement publication preconditions and reminder persistence, and a 403 response when Placement Admin requested a private submission. The checked browser console reported zero errors. Responsive verification and publication status are recorded separately in the final verification page.

## Synthetic demo accounts

| Role | Username | Password |
|---|---|---|
| Student | `student` | `Student@W7` |
| TA / Faculty | `ta` | `Faculty@W7` |
| Placement Admin | `placement` | `Placement@W7` |

These publicly documented accounts are only for synthetic demonstration data. Do not upload real student records or personal documents.

## Start the demonstration

Install Python 3.11 or newer and the repository requirements. From the repository root:

```shell
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python scripts/run_demo.py
```

The runner disables debug mode, persists a random runtime secret in the ignored `.demo-runtime/secret.key` with owner-only file permissions when none is configured, uses `.demo-runtime/demo.sqlite3` and `.demo-runtime/media`, applies migrations, collects static assets, seeds the synthetic accounts and starts Gunicorn on <http://127.0.0.1:8000/>. It does not modify the normal development database. Rerunning the seed refreshes the synthetic round/assignment windows and demo account passwords without adding another scheduled reminder. HTTPS cookies are enabled by default. For a local HTTP-only walkthrough, set `DEADLINEDESK_SECURE_COOKIES=0` before launching the runner.

In a separate terminal, with the installed official `cloudflared` CLI:

```shell
cloudflared tunnel --url http://127.0.0.1:8000 --protocol http2 --no-autoupdate
```

Open the HTTPS URL printed by the tunnel, check sign-in from another browser/device and update this page with that URL. Keep both terminals and the host running. Close the tunnel process to stop public access. The active preparation environment uses `.venv-submit/`; a new checkout may use the `.venv/` commands above.

## Live walkthrough

1. Sign in as Placement Admin. Create a company and draft round with an opening time before now and a future closing time. Add a required checklist item and publish. Show the T-24h reminder record.
2. Sign out and sign in as Student. Open that round, complete the required items and show **Ready to apply**. Explain that changes are rejected outside the open window.
3. Sign in as TA. Publish an assignment with a due time and late policy.
4. As Student, upload a small synthetic text file. Show the accepted timestamp, late result and similarity stub label.
5. As the assignment's TA, start review and publish a valid score and feedback. As Student, open the result and download the same submitted file.
6. Demonstrate a role denial and an invalid form. Open the [test-case catalogue](test-cases/README.md) for deterministic deadline boundaries and ownership checks.

## Persistent hosting option

The repository Dockerfile supports a permanent host. Configure a strong `DEADLINEDESK_SECRET_KEY`, explicit `DEADLINEDESK_ALLOWED_HOSTS`, the HTTPS origin in `DEADLINEDESK_CSRF_ORIGINS`, and secure cookies for an HTTPS deployment. Mount durable storage at `/data` for SQLite and private media, and configure trusted-proxy behavior only behind the intended reverse proxy. The image applies migrations and runs Gunicorn. Create demo accounts explicitly with `python code/manage.py seed_demo` only on a synthetic demonstration deployment.

The temporary tunnel is the preparation demo. A Dockerfile alone is not evidence of a permanent deployed service.
