"""Regenerate the complete HR-30 whole-body P0.1 package in dependency order.

The first generator intentionally replaces the whole package.  Every later
generator adds a controlled derived artifact and must therefore succeed before
the synchronized release is considered current.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
KICAD_PYTHON = Path(r"C:\Program Files\KiCad\10.0\bin\python.exe")

PIPELINE = (
    "generate_hr30_body_architecture_p01.py",
    "generate_hr30_system_package_p01.py",
    "generate_hr30_fabrication_architecture_p01.py",
    "generate_hr30_installed_equipment_p01.py",
    "generate_hr30_joint_load_architecture_p01.py",
    "generate_hr30_whole_body_pose_architecture_p01.py",
    "generate_hr30_whole_body_collision_architecture_p01.py",
    "generate_hr30_whole_body_electrical_p01.py",
    "generate_hr30_actuator_bus_architecture_p01.py",
    "generate_hr30_whole_body_interface_atlas_p01.py",
    "generate_hr30_module_cad_exports_p01.py",
    "generate_hr30_joint_fasteners_p01.py",
    "generate_hr30_joint_family_cad_p01.py",
    "generate_hr30_manufacturing_files_p01.py",
    "generate_hr30_actuator_interface_carriers_p01.py",
    "generate_hr30_actuator_branch_pdu_p01.py",
    "generate_hr30_energy_safety_spine_p01.py",
    "generate_hr30_tether_power_core_p01.py",
    "generate_hr30_whole_body_harness_p01.py",
    "generate_hr30_physical_harness_p01.py",
    "generate_hr30_assembly_guide_p01.py",
    "generate_hr30_detailed_grippers_p01.py",
    "generate_hr30_mass_reconciliation_p01.py",
    "generate_hr30_leg_drivetrain_p01.py",
    "generate_hr30_leg_drivetrain_adapters_p01.py",
    "generate_hr30_installed_leg_drivetrains_p01.py",
    "generate_hr30_fabrication_sourcing_p01.py",
    "generate_hr30_joint_hardware_manufacturing_p01.py",
    "generate_hr30_transmission_closure_p01.py",
    "generate_hr30_current_constrained_actuation_p01.py",
    "generate_hr30_axis_commissioning_station_p01.py",
    "generate_hr30_bench_harness_p01.py",
    "generate_hr30_no_motion_inspection_p01.py",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--from-stage",
        choices=PIPELINE,
        help="resume at this generator after all earlier stages have passed",
    )
    args = parser.parse_args()
    first = PIPELINE.index(args.from_stage) if args.from_stage else 0
    for number, script_name in enumerate(PIPELINE[first:], start=first + 1):
        script = TOOLS / script_name
        if not script.is_file():
            raise FileNotFoundError(script)
        interpreter = KICAD_PYTHON if script_name in {
            "generate_hr30_actuator_interface_carriers_p01.py",
            "generate_hr30_actuator_branch_pdu_p01.py",
        } else Path(sys.executable)
        if not interpreter.is_file():
            raise FileNotFoundError(interpreter)
        print(f"[{number:02d}/{len(PIPELINE):02d}] {script_name}", flush=True)
        completed = subprocess.run([str(interpreter), str(script)], cwd=ROOT, check=False)
        if completed.returncode != 0:
            print(f"STOPPED: {script_name} returned {completed.returncode}", flush=True)
            return completed.returncode
    print(f"PASS: regenerated {len(PIPELINE)} HR-30 whole-body stages", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
