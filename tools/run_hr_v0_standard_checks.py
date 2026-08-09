#!/usr/bin/env python3
"""Run the repository's non-pcbnew checkers concurrently.

The individual checkers are read-only. Native pcbnew checks remain a separate
KiCad-runtime step because they require KiCad's Python environment.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PCBNEW_IMPORT = re.compile(r"^\s*(?:import|from)\s+pcbnew\b", re.MULTILINE)


def run_one(python: str, script: Path) -> tuple[str, int, str]:
    completed = subprocess.run(
        [python, str(script)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return script.name, completed.returncode, completed.stdout


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--jobs", type=int, default=8)
    args = parser.parse_args()
    scripts = []
    for path in sorted((ROOT / "tools").glob("check*.py")):
        if not PCBNEW_IMPORT.search(path.read_text(encoding="utf-8")):
            scripts.append(path)
    failures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        futures = [pool.submit(run_one, args.python, script) for script in scripts]
        for future in concurrent.futures.as_completed(futures):
            name, code, output = future.result()
            if code:
                failures.append((name, code, output))
    if failures:
        print(f"HR-V0 standard checker sweep FAILED: {len(failures)} / {len(scripts)}")
        for name, code, output in sorted(failures):
            print(f"\n--- {name} (exit {code}) ---\n{output.rstrip()}")
        return 1
    print(f"HR-V0 standard checker sweep PASS: {len(scripts)} / {len(scripts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
