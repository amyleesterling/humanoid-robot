"""Recompute the bounded HR-30 P0.1 neutral-pose joint packaging screen."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import generate_hr30_body_architecture_p01 as arch  # noqa: E402


def main() -> int:
    components, axes, _bindings, _transforms = arch.build()
    actual = arch.joint_packaging_screen(components, axes)
    retained_path = ROOT / "hr30" / "whole-body-p0.1" / "joint-packaging-screen.json"
    retained = json.loads(retained_path.read_text(encoding="utf-8")) if retained_path.exists() else None
    synchronized = retained == actual
    print(arch.WARNING)
    print(
        f"screened {actual['module_part_count']} physical joint-module parts and "
        f"{actual['exact_actuator_count']} exact actuator bodies; "
        f"detached={len(actual['detached'])}; "
        f"cross-assembly actuator collisions={len(actual['cross_assembly_actuator_collisions'])}; "
        f"floor failures={len(actual['floor_crossings'])}; retained_sync={synchronized}"
    )
    if actual["detached"]:
        print(json.dumps({"detached": actual["detached"]}, indent=2))
    if actual["cross_assembly_actuator_collisions"]:
        print(json.dumps({"cross_assembly_actuator_collisions": actual["cross_assembly_actuator_collisions"]}, indent=2))
    if actual["floor_crossings"]:
        print(json.dumps({"floor_crossings": actual["floor_crossings"]}, indent=2))
    return 0 if actual["pass"] and synchronized else 1


if __name__ == "__main__":
    raise SystemExit(main())
