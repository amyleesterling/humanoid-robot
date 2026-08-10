from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "test-fixtures" / "hr-v0" / "x430-brake-support-p0.1"
WEB = ROOT / "release" / "hr-v0" / "x430-brake-support-p0.1"
HB = ROOT / "cad" / "vendor" / "magtrol" / "hb-450m-r102"
PT = ROOT / "cad" / "vendor" / "magtrol" / "pt-series-r104"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    errors: list[str] = []
    required = [
        "FX104-C01_4866_to_PT_adapter_review.step", "HR-V0_X430_brake_support_P0.1_review.step",
        "HR-V0_X430_brake_support_P0.1_review.glb", "brake-support-layout.svg", "erratum-register.csv",
        "topology-trade.csv", "brake-support-bom.csv", "dimension-register.csv", "interface-register.csv",
        "calculation-screen.csv", "vendor-rfi.csv", "open-hold-register.csv", "received-inspection-template.csv",
        "source-register.csv", "geometry-check.json", "package-status.json",
    ]
    errors.extend(f"missing {name}" for name in required if not (OUT / name).exists())
    if not (WEB / "index.html").exists(): errors.append("missing interactive guide")
    if errors: raise SystemExit("\n".join(errors))

    expected_hashes = {
        HB / "HB-MHB-datasheet-2025.pdf":"51B4AB9868D6E1380DFADA6E7A489A6D37F6A4B202AFF6107C75209AB61A6DC0",
        HB / "hb-450m-rev-a.pdf":"B60AE3A2B5E4CB18BA8F9875AD1C44B6AD78002DC2E2E880331C67FFE1FEB77F",
        HB / "HB-450M_B_EF.step":"2EE1136C6CA3B2202A13BC11DEA1A18EEB9D261B7E7D776EE940699C7F89EDE1",
        PT / "PT-series-US-02-2022.pdf":"5B1B991767A5801975485F22430931EBB6990B1E957D554CD8AE9B8D2CC00655",
    }
    for path, expected in expected_hashes.items():
        if not path.exists() or sha256(path) != expected: errors.append(f"controlled source changed: {path.name}")

    errata = rows("erratum-register.csv")
    if len(errata) != 1 or "20.0 mm plate thickness" not in errata[0]["corrected_interpretation"] or "14.5 mm lower T-slot width" not in errata[0]["corrected_interpretation"]:
        errors.append("PT thickness erratum missing")
    trade = rows("topology-trade.csv")
    if len(trade) != 4 or trade[0]["disposition"] != "PREFERRED INQUIRY - NOT SELECTED" or trade[-1]["disposition"] != "PROHIBITED": errors.append("topology disposition changed")
    bom = rows("brake-support-bom.csv")
    if len(bom) != 7 or bom[1]["order_identity"].split()[0] != "4866" or any("SELECTED" not in row["state"] and "CANDIDATE" not in row["state"] for row in bom): errors.append("BOM boundary changed")
    dims = rows("dimension-register.csv")
    if len(dims) != 9 or dims[1]["value_mm"] != "20.0" or dims[4]["value_mm"] != "117.3 / 104 / 12.7 / 76 / 120.4" or dims[8]["state"] != "NOT A FABRICATION DIMENSION": errors.append("controlled dimensions changed")
    interfaces = rows("interface-register.csv")
    if len(interfaces) != 6 or sum(row["state"] == "PARTIAL" for row in interfaces) != 1 or sum(row["state"] == "OPEN" for row in interfaces) != 5: errors.append("interface state changed")
    calculations = rows("calculation-screen.csv")
    if len(calculations) != 8: errors.append("calculation count changed")
    else:
        expected = [9.042, 5.85*9.80665, (5.85*9.80665)*0.1000082, 3.2/0.104, 4.1/0.104, 4.0, 120.0]
        actual = [float(row["result"].split()[0]) for row in calculations[:7]]
        if any(not math.isclose(a, b, abs_tol=1e-6) for a, b in zip(actual, expected)): errors.append("bounded arithmetic changed")
    rfi = rows("vendor-rfi.csv")
    if len(rfi) != 8 or any(row["state"] != "NOT SENT" for row in rfi): errors.append("RFI state changed")
    holds = rows("open-hold-register.csv")
    if len(holds) != 12 or sum(row["state"] == "PARTIAL" for row in holds) != 2 or sum(row["state"] == "OPEN" for row in holds) != 10: errors.append("hold state changed")
    received = rows("received-inspection-template.csv")
    if len(received) != 8 or any(row["result"] != "NOT EXECUTED" for row in received): errors.append("physical inspection was asserted")
    sources = rows("source-register.csv")
    if len(sources) != 5 or [row["local_sha256"] for row in sources[:4]] != list(expected_hashes.values()): errors.append("source register changed")

    geometry = json.loads((OUT / "geometry-check.json").read_text(encoding="utf-8"))
    pt = geometry.get("pt_profile", {})
    if pt != {"length_mm":600.0,"width_mm":375.0,"thickness_mm":20.0,"slot_count":15,"pitch_mm":25.0,"opening_mm":8.0,"lower_width_mm":14.5,"depth_mm":12.0,"lip_mm":5.0}: errors.append("PT profile changed")
    pb = geometry.get("pillow_block", {})
    if pb.get("model") != "4866" or pb.get("P_mm") != 104.0 or pb.get("R_mm") != 76.0 or pb.get("visual_clearance_diameter_mm") != 50.0 or pb.get("visual_clearance_is_fabrication_dimension") is not False or pb.get("body_cad_present") is not False: errors.append("4866 evidence boundary changed")
    if not math.isclose(geometry.get("nominal_axis_height_mm", 0), 120.0, abs_tol=1e-9): errors.append("axis-height arithmetic changed")
    if any(abs(value) > 1e-7 for value in geometry.get("nominal_intersections_mm3", {}).values()): errors.append("nominal B-Rep collision detected")
    if geometry.get("tolerance_credit") is not False or geometry.get("capacity_credit") is not False: errors.append("geometry promoted to capacity evidence")

    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    if status.get("identifier") != "HR-V0-X430-BRAKE-SUP-P0.1" or status.get("preferred_route") != "BS-A": errors.append("package identity changed")
    if status.get("r102_pt_thickness_erratum_applied") is not True or status.get("pt_drawing_profile_present") is not True: errors.append("erratum/profile state changed")
    for field in ("pillow_block_body_cad_present","adapter_fabrication_release_present","manufacturer_application_acceptance","fastener_selection_complete"):
        if status.get(field) is not False: errors.append(f"fail-closed field promoted: {field}")
    if status.get("open_hold_count") != 10 or status.get("partial_hold_count") != 2 or status.get("rfi_count") != 8 or status.get("rfi_state") != "NOT SENT": errors.append("hold/RFI state changed")
    if status.get("configured_h101_test_still_required") is not True or any(value is not False for value in status.get("release_flags", {}).values()): errors.append("release/test boundary changed")

    guide = (WEB / "index.html").read_text(encoding="utf-8")
    for phrase in ("A manufacturer support route", "C = 20.0 mm", "4866", "Two partial evidence holds and ten open holds", "font-size:14px", "font-size:16px", "No supplier was contacted"):
        if phrase not in guide: errors.append(f"guide boundary/readability missing: {phrase}")
    drawing = (OUT / "brake-support-layout.svg").read_text(encoding="utf-8")
    for phrase in ("max-width:100%;height:auto", "PT profile erratum", "DO NOT ORDER, MACHINE, ASSEMBLE OR POWER FROM THIS DRAWING", "R102's former 14.5 mm thickness interpretation is superseded"):
        if phrase not in drawing: errors.append(f"layout boundary missing: {phrase}")
    if errors: raise SystemExit("HR-V0 X430 brake-support check FAILED:\n- " + "\n- ".join(errors))
    print("HR-V0 X430 brake-support check: PASS")
    print("PT thickness erratum; 4866 route; 4 topologies; 7 BOM rows; 8 screens; 8 unsent RFIs")
    print("2 partial + 10 open holds; configured H101 test required; all release flags false")


if __name__ == "__main__":
    main()
