"""Run a synthetic-data demonstration without modifying the normal local database."""
import os
from pathlib import Path
import secrets
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
runtime = ROOT / ".demo-runtime"
runtime.mkdir(exist_ok=True)
if not os.environ.get("DEADLINEDESK_SECRET_KEY"):
    secret_path = runtime / "secret.key"
    try:
        descriptor = os.open(secret_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w") as secret_file:
            secret_file.write(secrets.token_urlsafe(48))
    except FileExistsError:
        pass
    os.environ["DEADLINEDESK_SECRET_KEY"] = secret_path.read_text().strip()
os.environ.setdefault("DEADLINEDESK_DEBUG", "0")
os.environ.setdefault("DEADLINEDESK_DB", str(runtime / "demo.sqlite3"))
os.environ.setdefault("DEADLINEDESK_MEDIA", str(runtime / "media"))
os.environ.setdefault("DEADLINEDESK_ALLOWED_HOSTS", "localhost,127.0.0.1,.trycloudflare.com")
os.environ.setdefault("DEADLINEDESK_CSRF_ORIGINS", "https://*.trycloudflare.com")
os.environ.setdefault("DEADLINEDESK_BEHIND_PROXY", "1")
os.environ.setdefault("DEADLINEDESK_SECURE_COOKIES", "1")
for command in (["migrate", "--noinput"], ["collectstatic", "--noinput"], ["seed_demo"]):
    subprocess.run([sys.executable, str(ROOT / "code/manage.py"), *command], check=True, cwd=ROOT)
os.chdir(ROOT / "code")
os.execv(sys.executable, [sys.executable, "-m", "gunicorn", "deadlinedesk.wsgi:application", "--bind", "127.0.0.1:8000", "--workers", "1", "--access-logfile", "-", "--timeout", "60"])
