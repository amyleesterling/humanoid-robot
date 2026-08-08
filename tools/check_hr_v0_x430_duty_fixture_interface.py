from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "test-fixtures" / "hr-v0" / "x430-duty-fixture-p0.2"
WEB = ROOT / "release" / "hr-v0" / "x430-duty-fixture-p0.2"
VENDOR = ROOT / "cad" / "vendor" / "robotis" / "x430-fr12-r91"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    errors: list[str] = []
    required = [
        "HR-V0_X430_fixture_interface_P0.2_review.step",
        "HR-V0_X430_fixture_interface_P0.2_review.glb",
        "parts/FX100-C01_fixed_adapter_review.step",
        "parts/FX100-C02_active_adapter_review.step",
        "adapter-interface-drawing.svg",
        "adapter-interface-stack.csv",
        "fastener-stack.csv",
        "tolerance-stack.csv",
        "collision-clearance.csv",
        "load-screen.csv",
        "vendor-rfi.csv",
        "open-hold-register.csv",
        "source-register.csv",
        "package-status.json",
    ]
    errors.extend(f"missing {name}" for name in required if not (OUT / name).exists())
    if not (WEB / "index.html").exists():
        errors.append("missing interactive guide")
    if errors:
        raise SystemExit("\n".join(errors))

    interfaces = rows("adapter-interface-stack.csv")
    if len(interfaces) != 5 or any("OPEN" not in row["status"] for row in interfaces):
        errors.append("interface count/state changed")
    fasteners = rows("fastener-stack.csv")
    if len(fasteners) != 2 or any("NOT SELECTED" not in row["status"] for row in fasteners):
        errors.append("fastener selection boundary changed")
    if fasteners[0]["calculated_engagement_mm"] != "4.688..5.650":
        errors.append("#8 engagement stack changed")
    tolerances = rows("tolerance-stack.csv")
    if len(tolerances) != 5 or any("OPEN" not in row["authority"] and "CANDIDATE" not in row["authority"] and "ARITHMETIC" not in row["authority"] for row in tolerances):
        errors.append("tolerance authority boundary changed")
    clearances = rows("collision-clearance.csv")
    if len(clearances) != 5 or clearances[2]["result"] != "0.000000000 mm3; gap 1.900000 mm":
        errors.append("nominal clearance evidence changed")
    if any("NOMINAL" not in row["state"] and "OPEN" not in row["state"] for row in clearances):
        errors.append("clearance authority boundary changed")
    loads = rows("load-screen.csv")
    if len(loads) != 4:
        errors.append("load screen count changed")
    expected_stress = [149 * nm * 8.85074579 for nm in (1.087329823, 4.1, 11.0, 16.5)]
    actual_stress = [float(row["tff_mz_stress_screen_psi"]) for row in loads]
    if any(not math.isclose(a, b, abs_tol=0.001) for a, b in zip(actual_stress, expected_stress)):
        errors.append("FUTEK coefficient arithmetic changed")
    if any("ARITHMETIC ONLY" not in row["authority"] for row in loads):
        errors.append("load screen authority boundary missing")
    rfi = rows("vendor-rfi.csv")
    if len(rfi) != 8 or any(row["state"] != "NOT SENT" for row in rfi):
        errors.append("vendor RFI was changed or represented as sent")
    holds = rows("open-hold-register.csv")
    if len(holds) != 14 or any(row["state"] != "OPEN" for row in holds):
        errors.append("open holds promoted or count changed")
    sources = rows("source-register.csv")
    if len(sources) != 8 or sources[0]["record"] != "TFF400 drawing FI1251-F":
        errors.append("source register changed")

    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    if status.get("identifier") != "HR-V0-X430-FIXTURE-IF-P0.2" or status.get("parent") != "HR-V0-X430-FIXTURE-P0.1":
        errors.append("package identity/parent changed")
    if status.get("open_hold_count") != 14 or status.get("rfi_state") != "NOT SENT":
        errors.append("package hold/RFI state changed")
    if any(value is not False for value in status.get("release_flags", {}).values()):
        errors.append("release flag promoted")
    collision = status.get("nominal_collision_check", {})
    for key in ("active_adapter_x430_mm3", "active_adapter_s102_mm3", "fixed_adapter_x430_mm3", "screw_head_x430_mm3"):
        if not math.isclose(float(collision.get(key, -1)), 0.0, abs_tol=1e-7):
            errors.append(f"nominal collision changed: {key}")
    if not math.isclose(float(collision.get("nominal_screw_head_x430_gap_mm", -1)), 1.9, abs_tol=1e-9):
        errors.append("nominal screw-head gap changed")
    for name, expected in status.get("source_sha256", {}).items():
        if sha256(VENDOR / name) != expected:
            errors.append(f"controlled ROBOTIS source changed: {name}")

    guide = (WEB / "index.html").read_text(encoding="utf-8")
    for phrase in (
        "The bridge is gone",
        "Neither result includes manufacturing variation",
        "Why it still cannot be fabricated",
        "font-size:13px",
        "font-size:16px",
        "all release flags remain false",
    ):
        if phrase not in guide:
            errors.append(f"guide boundary/readability missing: {phrase}")
    drawing = (OUT / "adapter-interface-drawing.svg").read_text(encoding="utf-8")
    for phrase in ("font-size:17px", "max-width:100%;height:auto", "DO NOT FABRICATE FROM THIS DRAWING", "1.900 mm"):
        if phrase not in drawing:
            errors.append(f"drawing boundary/readability missing: {phrase}")

    if errors:
        raise SystemExit("HR-V0 X430 fixture interface check FAILED:\n- " + "\n- ".join(errors))
    print("HR-V0 X430 fixture interface check: PASS")
    print("2 adapter candidates; 5 interfaces; 5 tolerance stacks; 8 unsent RFI rows; 14 open holds")
    print("all procurement, fabrication, assembly, powered-test, motion and energization flags remain false")


if __name__ == "__main__":
    main()
