"""Run every non-pcbnew HR-30 checker in one process with visible results.

The routed PCB checkers import KiCad's ``pcbnew`` module and are therefore run
separately with KiCad's Python.  Every other checker shares the CadQuery
runtime and can be executed here without the Windows venv launcher's detached
child-process behavior obscuring its exit status.
"""

from __future__ import annotations

import importlib.util
import json
import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
SELF = Path(__file__).name
PCBNEW_CHECKERS = {
    "check_hr30_actuator_interface_carriers_p01.py",
    "check_hr30_swd_adapter_p01.py",
}
RESULT = ROOT / "validation" / "hr30-whole-body-p0.1-checks.json"


def load_checker(path: Path):
    spec = importlib.util.spec_from_file_location(f"hr30_check_{path.stem}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="run one checker filename")
    parser.add_argument("--result", type=Path, default=RESULT)
    args = parser.parse_args()
    result_path = args.result if args.result.is_absolute() else ROOT / args.result
    result_path.parent.mkdir(parents=True, exist_ok=True)
    if result_path.exists():
        result_path.unlink()
    checks = [
        path
        for path in sorted(TOOLS.glob("check_hr30*.py"))
        if path.name != SELF and path.name not in PCBNEW_CHECKERS
    ]
    if args.only:
        checks = [path for path in checks if path.name == args.only]
        if len(checks) != 1:
            raise SystemExit(f"unknown or excluded checker: {args.only}")
    failures: list[str] = []
    for path in checks:
        print(f"RUN {path.name}", flush=True)
        try:
            result = load_checker(path).main()
            if result not in (None, 0):
                failures.append(f"{path.name}: returned {result}")
        except BaseException as exc:  # preserve fail-closed SystemExit messages
            failures.append(f"{path.name}: {exc}")
            print(f"FAILED {path.name}: {exc}", flush=True)
    summary = {
        "identifier": "HR30-WHOLE-BODY-P0.1-CHECKS",
        "cad_runtime_validator_count": len(checks),
        "separate_kicad_python_validators": sorted(PCBNEW_CHECKERS),
        "failure_count": len(failures),
        "failures": failures,
        "pass": not failures,
    }
    result_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"CAD_RUNTIME_VALIDATORS={len(checks)} FAILURES={len(failures)}", flush=True)
    for failure in failures:
        print(failure, flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
