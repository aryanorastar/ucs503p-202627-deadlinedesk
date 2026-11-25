"""Export editable sources without ever rewriting them."""
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
cli = shutil.which("drawio")
if not cli:
    sys.exit("Install draw.io Desktop and put its drawio CLI on PATH.")
sources = [*ROOT.glob("project-proposal/figures/*.drawio"), *ROOT.glob("docs/uml/*/*.drawio"), *ROOT.glob("docs/gantt-chart/*.drawio")]
for source in sorted(set(p.resolve() for p in sources)):
    for ext in ("pdf", "png"):
        args = [cli, "-x", "-f", ext, "-b", "20", "-o", str(source.with_suffix("."+ext)), str(source)]
        args[2:2] = ["--crop"] if ext == "pdf" else ["-s", "2"]
        subprocess.run(args, check=True, cwd=ROOT, stdout=subprocess.DEVNULL)
    print(source.relative_to(ROOT))
