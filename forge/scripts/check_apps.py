"""Run the existing standalone exercises' checks without changing their gaps."""
from pathlib import Path
import concurrent.futures
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]
APPS = sorted(path.parent.parent.parent for path in (ROOT / "projects").rglob("src/services/qa-service.ts"))

def check(app):
    commands = [["npm", "run", "check"], ["npm", "run", "build"], ["npm", "test", "--", "--passWithNoTests"]]
    if (app / "scripts/check-architecture.sh").exists():
        commands.append(["bash", "scripts/check-architecture.sh"])
    results = []
    for command in commands:
        run = subprocess.run(command, cwd=app, text=True, capture_output=True)
        results.append({"command": command, "exitCode": run.returncode, "stdout": run.stdout, "stderr": run.stderr})
    return {"app": str(app.relative_to(ROOT)), "passed": all(r["exitCode"] == 0 for r in results), "checks": results}

if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(check, APPS))
    output = ROOT / "forge/local-results/app-checks.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(results, indent=2))
    for result in results:
        print(result["app"], "PASS" if result["passed"] else "FAIL")
    raise SystemExit(0 if all(r["passed"] for r in results) else 1)
