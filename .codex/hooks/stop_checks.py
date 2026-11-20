"""Run local verification for the parts of VLA-RLX with pending changes."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


REPO_ROOT = Path(__file__).resolve().parents[2]
PAGES_WORKFLOW = ".github/workflows/pages.yml"


def changed_paths():
    scope = ["--", "results/", "website/", PAGES_WORKFLOW]
    tracked = subprocess.check_output(
        ["git", "diff", "--name-only", "-z", "--no-renames", "HEAD", *scope],
        cwd=REPO_ROOT,
    )
    untracked = subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard", "-z", *scope],
        cwd=REPO_ROOT,
    )
    return os.fsdecode(tracked + untracked).split("\0")


def verify(stop_hook_active):
    paths = changed_paths()
    checks = [("Git diff whitespace", REPO_ROOT, ["git", "diff", "--check", "HEAD", "--"])]
    skipped = []

    if any(path.startswith("results/") for path in paths):
        python = REPO_ROOT / "results/.venv/bin/python"
        if os.access(python, os.X_OK):
            checks.append(("Results tests", REPO_ROOT, [
                str(python), "-B", "-m", "unittest", "discover", "-s", "results", "-p", "test_*.py",
            ]))
        else:
            skipped.append("Results tests skipped. Set up with `uv sync --locked --project results`.")

    if PAGES_WORKFLOW in paths or any(path.startswith("website/") for path in paths):
        website = REPO_ROOT / "website"
        binaries = website / "node_modules/.bin"
        if shutil.which("bun") and all(os.access(binaries / name, os.X_OK) for name in ("eslint", "tsc", "astro")):
            checks.extend([
                ("Website lint", website, ["bun", "run", "lint"]),
                ("Website typecheck", website, ["bun", "run", "typecheck"]),
            ])
        else:
            skipped.append("Website checks skipped. Install Bun and run `cd website && bun install --frozen-lockfile`.")

    env = {**os.environ, "CI": "1", "ASTRO_TELEMETRY_DISABLED": "1", "PYTHONDONTWRITEBYTECODE": "1"}
    failures = []
    for name, cwd, command in checks:
        result = subprocess.run(
            command, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace",
        )
        if result.returncode:
            failures.append((name, result.stdout))

    response = {}
    if failures:
        with tempfile.NamedTemporaryFile(mode="w", prefix="vla-rlx-stop-", suffix=".log", delete=False) as log:
            for name, output in failures:
                print(f"{name}\n{output}", file=log)
        names = ", ".join(name for name, _ in failures)
        message = f"VLA-RLX verification failed for {names}. See {log.name}."
        if stop_hook_active:
            skipped.insert(0, message)
        else:
            response.update(decision="block", reason=f"{message} Address failures related to this task and report any remaining ones.")
    if skipped:
        response["systemMessage"] = " ".join(skipped)
    return response


if __name__ == "__main__":
    try:
        payload = json.loads(sys.stdin.read() or "{}")
        if not isinstance(payload, dict):
            raise ValueError("Expected a JSON object on stdin.")
        response = verify(payload.get("stop_hook_active") is True)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        response = {"systemMessage": f"VLA-RLX Stop hook could not finish verification. {error}"}
    print(json.dumps(response))
