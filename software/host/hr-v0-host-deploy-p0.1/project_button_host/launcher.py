#!/usr/bin/env python3
"""Preflight-gated launcher for a future HR-V0 runtime.

The committed configuration is on HOLD, so this candidate exits before any
runtime process is started. It provides no motion or heartbeat implementation.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from project_button_host.preflight import evaluate


def launch(config_path: Path, root: Path = Path("/")) -> int:
    result = evaluate(config_path, root)
    if not result.ready:
        print(json.dumps(result.as_dict(), sort_keys=True))
        return 78

    config = json.loads(config_path.read_text(encoding="utf-8"))
    interpreter = Path(config["python_interpreter"])
    entrypoint = Path(config["runtime_entrypoint"])
    if not interpreter.is_absolute() or not entrypoint.is_absolute():
        print(json.dumps({"ready": False, "holds": ["runtime paths are not absolute"], "motion_authority": "NONE"}, sort_keys=True))
        return 78
    if not interpreter.is_file() or not entrypoint.is_file():
        print(json.dumps({"ready": False, "holds": ["runtime path is absent"], "motion_authority": "NONE"}, sort_keys=True))
        return 78
    completed = subprocess.run([str(interpreter), str(entrypoint), "--config", str(config_path)], check=False)
    return int(completed.returncode)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path("/"))
    args = parser.parse_args()
    return launch(args.config, args.root)


if __name__ == "__main__":
    raise SystemExit(main())
