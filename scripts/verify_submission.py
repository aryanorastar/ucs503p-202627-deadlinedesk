"""Validate the instructor's required artifact paths and local Markdown targets."""
from pathlib import Path
import json
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
required = [
    "code/manage.py", "project-proposal/main.tex", "project-proposal/main.pdf",
    "w4/presentation.pdf", "project-report-prototype-stage/main.tex",
    "project-report-prototype-stage/main.pdf",
    "docs/submission/01-presentation/DeadlineDesk_Week7_Presentation.pdf",
    "project-report-final/main.tex", "project-report-final/main.pdf",
    "docs/submission/09-final-presentation/DeadlineDesk_Final_Presentation.pdf",
    "docs/submission/09-final-presentation/DeadlineDesk_Final_Presentation.pptx",
    "docs/test-cases/test-cases.pdf", "docs/gantt-chart/gantt-chart.pdf",
    "docs/final-verification.md", "docs/live-demo.md",
]
required += [f"journals/{member}/journal.md" for member in ("1024030764-aryan", "1024030766-aksh", "1024030767-naveen")]
folders=sorted((ROOT/"docs/uml").glob("[0-9][0-9]-*"))
assert len(folders) == 8, "Exactly eight UML folders are required."
for folder in folders:
    required += [str((folder/name).relative_to(ROOT)) for name in ("README.md", "diagram.drawio", "diagram.pdf", "diagram.png")]
missing=[name for name in required if not (ROOT/name).is_file() or (ROOT/name).stat().st_size == 0]
assert not missing, f"Missing required artifacts: {missing}"
results=json.loads((ROOT/"docs/test-cases/results.json").read_text())
assert results["passed"] == len(results["cases"])
assert all(case["result"] == "PASS" for case in results["cases"])
broken=[]
files=[ROOT/"README.md", *ROOT.glob("docs/**/*.md"), *ROOT.glob("journals/**/*.md")]
for file in files:
    for target in re.findall(r"\]\(([^)]+)\)", file.read_text()):
        target=target.strip("<>").split(' "')[0]
        if urlsplit(target).scheme or target.startswith("#"):
            continue
        path=unquote(target.split("#")[0])
        if path and not (file.parent/path).exists():
            broken.append(f"{file.relative_to(ROOT)} -> {target}")
assert not broken, "Broken links:\n"+"\n".join(broken)
print(f"Required artifacts present; 8 UML folders; {results['passed']} passing test records; Markdown targets resolve.")
