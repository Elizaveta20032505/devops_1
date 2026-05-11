from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

try:
    import yaml
except ImportError:
    print("pip install pyyaml", file=sys.stderr)
    raise SystemExit(1)


def _git_hashes(n: int = 5) -> list[str]:
    out = subprocess.run(
        ["git", "log", f"-{n}", "--format=%H"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [ln.strip() for ln in out.stdout.splitlines() if ln.strip()]


def _branch() -> str:
    out = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return out.stdout.strip()


def _coverage() -> int | None:
    try:
        subprocess.run(
            [sys.executable, "-m", "pytest", "--cov=src", "--cov-report=json", "-q"],
            cwd=ROOT,
            check=True,
            capture_output=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    cov_file = ROOT / "coverage.json"
    if not cov_file.is_file():
        return None
    import json

    data = json.loads(cov_file.read_text(encoding="utf-8"))
    return int(round(float(data["totals"]["percent_covered"])))


def main() -> None:
    path = ROOT / "dev_sec_ops.yml"
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) if path.is_file() else {"version": 1}
    doc.setdefault("docker", {})
    doc["docker"]["image_digest"] = os.environ.get("IMAGE_DIGEST", doc.get("docker", {}).get("image_digest", ""))
    doc.setdefault("git", {})
    doc["git"]["branch"] = _branch()
    doc["git"]["last_5_commit_hashes"] = _git_hashes(5)
    doc.setdefault("quality", {})
    cov = _coverage()
    if cov is not None:
        doc["quality"]["pytest_coverage_src_total_percent"] = cov
    path.write_text(yaml.dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print("Обновлено:", path)


if __name__ == "__main__":
    main()
