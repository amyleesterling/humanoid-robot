from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "test-fixtures" / "hr-v0" / "x430-load-rig-p0.1"
WEB = ROOT / "release" / "hr-v0" / "x430-load-rig-p0.1"
MAGTROL = ROOT / "cad" / "vendor" / "magtrol" / "hb-450m-r102"
PT_SOURCE = ROOT / "cad" / "vendor" / "magtrol" / "pt-series-r104"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    errors: list[str] = []
    required = [
        "HR-V0_X430_load_rig_P0.1_review.step", "HR-V0_X430_load_rig_P0.1_review.glb",
        "load-rig-layout.svg", "topology-trade.csv", "load-device-bom.csv",
        "load-capacity-screen.csv", "interface-register.csv", "alignment-tolerance-register.csv",
        "power-thermal-register.csv", "vendor-rfi.csv", "open-hold-register.csv",
        "source-register.csv", "package-status.json",
    ]
    errors.extend(f"missing {name}" for name in required if not (OUT / name).exists())
    if not (WEB / "index.html").exists(): errors.append("missing interactive guide")
    if errors: raise SystemExit("\n".join(errors))

    trade = rows("topology-trade.csv")
    if len(trade) != 4 or trade[0]["disposition"] != "PREFERRED INQUIRY - NOT SELECTED": errors.append("topology preference changed")
    if trade[2]["disposition"] != "REJECT FOR CURRENT LOAD RIG" or trade[3]["disposition"] != "PROHIBITED FOR POWERED CHARACTERIZATION": errors.append("unsafe topology disposition changed")
    bom = rows("load-device-bom.csv")
    if len(bom) != 8 or any("SELECTED" not in r["state"] and "DEFINED" not in r["state"] for r in bom): errors.append("BOM selection boundary changed")
    screens = rows("load-capacity-screen.csv")
    if len(screens) != 6: errors.append("screen count changed")
    expected = [3.2/4.1, 3.96/3.2, 7.9/4.1]
    actual = [float(r["result"].split()[0]) for r in screens[:3]]
    if any(not math.isclose(a,b,abs_tol=1e-6) for a,b in zip(actual,expected)): errors.append("torque arithmetic changed")
    if not math.isclose(float(screens[3]["result"].split()[0]), 3.2*2*math.pi*30/60, abs_tol=1e-6): errors.append("power arithmetic changed")
    if not math.isclose(float(screens[4]["result"].split()[0]), 3.2/2.52, abs_tol=1e-6): errors.append("coupling twist arithmetic changed")
    if screens[5]["result"] != "9.042000 kg": errors.append("PT-600 mass screen changed")
    interfaces = rows("interface-register.csv")
    if len(interfaces) != 6 or any(r["state"] != "OPEN" for r in interfaces): errors.append("interface state changed")
    align = rows("alignment-tolerance-register.csv")
    if len(align) != 5 or sum("SELECTION REQUIRED" in r["candidate_limit"] for r in align) < 4: errors.append("alignment boundary changed")
    power = rows("power-thermal-register.csv")
    if len(power) != 6 or power[-1]["state"] != "REQUIRED": errors.append("power/control boundary changed")
    rfi = rows("vendor-rfi.csv")
    if len(rfi) != 8 or any(r["state"] != "NOT SENT" for r in rfi): errors.append("RFI state changed")
    holds = rows("open-hold-register.csv")
    if len(holds) != 14 or any(r["state"] != "OPEN" for r in holds): errors.append("hold state changed")
    sources = rows("source-register.csv")
    if len(sources) != 6 or sources[2]["local_sha256"] != "2EE1136C6CA3B2202A13BC11DEA1A18EEB9D261B7E7D776EE940699C7F89EDE1" or sources[3]["local_sha256"] != "5B1B991767A5801975485F22430931EBB6990B1E957D554CD8AE9B8D2CC00655": errors.append("source register changed")
    expected_hashes = {
        "HB-450M_B_EF.step":"2EE1136C6CA3B2202A13BC11DEA1A18EEB9D261B7E7D776EE940699C7F89EDE1",
        "hb-450m-rev-a.pdf":"B60AE3A2B5E4CB18BA8F9875AD1C44B6AD78002DC2E2E880331C67FFE1FEB77F",
    }
    for name, expected_hash in expected_hashes.items():
        if sha256(MAGTROL / name) != expected_hash: errors.append(f"controlled Magtrol source changed: {name}")
    if sha256(PT_SOURCE / "PT-series-US-02-2022.pdf") != "5B1B991767A5801975485F22430931EBB6990B1E957D554CD8AE9B8D2CC00655": errors.append("controlled PT-series source changed")

    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    if status.get("identifier") != "HR-V0-X430-LOAD-RIG-P0.1" or status.get("preferred_route") != "LOAD-A": errors.append("package identity changed")
    if status.get("open_hold_count") != 14 or status.get("rfi_count") != 8 or status.get("rfi_state") != "NOT SENT": errors.append("package hold/RFI state changed")
    if status.get("pt_body_cad_present") is not False or status.get("output_adapter_fabrication_geometry_present") is not False: errors.append("fabrication evidence boundary changed")
    if status.get("configured_h101_test_still_required") is not True or status.get("robot_24v_brake_supply_allowed") is not False: errors.append("test/power boundary changed")
    if any(v is not False for v in status.get("release_flags", {}).values()): errors.append("release flag promoted")

    guide = (WEB / "index.html").read_text(encoding="utf-8")
    for phrase in ("A controllable load device", "final configured FR12-H101 gravity test remains mandatory", "font-size:14px", "font-size:16px", "No hardware was connected or energized"):
        if phrase not in guide: errors.append(f"guide boundary/readability missing: {phrase}")
    drawing = (OUT / "load-rig-layout.svg").read_text(encoding="utf-8")
    for phrase in ("max-width:100%;height:auto", "600×375×20 mm corrected envelope", "DO NOT BUILD OR POWER FROM THIS LAYOUT", "does not reproduce the final FR12-H101 configured joint"):
        if phrase not in drawing: errors.append(f"layout boundary missing: {phrase}")
    if errors: raise SystemExit("HR-V0 X430 load-rig check FAILED:\n- " + "\n- ".join(errors))
    print("HR-V0 X430 load-rig check: PASS")
    print("4 routes; 8 BOM rows; 6 screens; 8 unsent RFIs; 14 open holds")
    print("configured H101 test required; robot 24 V brake supply prohibited; all release flags false")


if __name__ == "__main__": main()
