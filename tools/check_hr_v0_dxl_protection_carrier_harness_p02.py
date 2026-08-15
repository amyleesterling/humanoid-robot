#!/usr/bin/env python3
"""Validate R263 without granting physical-work or energization authority."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ID = "HR-V0-DXL-PROT-CARRIER-HARNESS-P0.2"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
ENG = ROOT / "electrical/harness/hr-v0-dxl-protection-carrier-harness-p0.2"
REL = ROOT / "release/hr-v0/dxl-protection-carrier-harness-p0.2"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.27"
CFGR = ROOT / "release/hr-v0/configuration-reconciliation-p0.27"
SOURCES = {
    "carrier_terminals": ROOT / "electrical/kicad/hr-v0-dxl-protection-carrier-p0.3/terminal-schedule.csv",
    "star_terminals": ROOT / "electrical/kicad/hr-v0-dxl-star-p0.2-carrier-candidate/connector-schedule.csv",
    "system_terminals": ROOT / "electrical/kicad/project-button-v3-p1.15-carrier-candidate/connector-schedule.csv",
    "old_placement": ROOT / "electrical/integration/hr-v0-dxl-carrier-integration-p0.1/panel-placement-screen.csv",
    "old_route": ROOT / "electrical/integration/hr-v0-dxl-carrier-integration-p0.1/route-bound-screen.csv",
    "panel_p07": ROOT / "electrical/panel/hr-v0-control-panel-p0.7-node-placement/candidate-backplate-layout.csv",
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig",newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    failures: list[str] = []
    def need(value: bool, message: str) -> None:
        if not value:
            failures.append(message)

    common = {"README.md","package-status.json","file-manifest.csv","primary-source-register.csv","harness-schedule.csv","interface-control.csv","cut-crimp-schedule.csv","harness-bom.csv","stale-placement-collisions.csv","placement-candidate.csv","route-lower-bound.csv","manufacturing-process.csv","open-holds.csv","acceptance-matrix.csv","harness-topology.svg"}
    for directory, expected in ((ENG,common),(REL,common|{"index.html"})):
        actual = {path.name for path in directory.iterdir() if path.is_file()}
        need(actual == expected, f"membership mismatch {directory.name}: {sorted(actual ^ expected)}")
        need(not any(path.suffix.lower() in {".zip",".7z",".rar"} for path in directory.iterdir()), "archive prohibited")

    status = json.loads((REL/"package-status.json").read_text(encoding="utf-8"))
    for key,value in {"identifier":ID,"round":"R263","harnesses":6,"conductors":12,"interface_rows":24,"vhr_2n_minimum_population":9,"svh_21t_p11_minimum_population":18,"pn18_8r_e_population":6,"stale_placement_collisions":13,"candidate_placements":3,"candidate_planar_collisions":0}.items():
        need(status.get(key) == value, f"status mismatch {key}")
    for key in ("cut_lengths_released","termination_process_released","physical_article_exists","physical_test_executed","qualified_review_complete","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit"):
        need(status.get(key) is False, f"{key} must remain false")
    need(status.get("warning") == WARNING, "warning mismatch")
    need(set(status.get("source_hashes",{})) == set(SOURCES), "source membership mismatch")
    for key,path in SOURCES.items():
        need(status["source_hashes"].get(key) == sha(path), f"source hash mismatch {key}")

    carrier = {(r["reference"],r["terminal"]):r["net"] for r in rows(SOURCES["carrier_terminals"])}
    need(carrier.get(("JIN1","1")) == "BRANCH_FUSED_IN" and carrier.get(("JIN1","2")) == "ACT_0V_PE_BONDED", "carrier input map changed")
    need(carrier.get(("JOUT1","1")) == "BRANCH_LIMITED_OUT" and carrier.get(("JOUT1","2")) == "ACT_0V_PE_BONDED", "carrier output map changed")
    star = {(r["reference"],r["terminal"]):r["net"] for r in rows(SOURCES["star_terminals"])}
    for ref,net in (("JP1","J1_LIMITED_VDD"),("JP2","J2_LIMITED_VDD"),("JP3","J3_LIMITED_VDD")):
        need(star.get((ref,"1")) == net and star.get((ref,"2")) == "ACT_0V_PE_BONDED", f"{ref} map changed")

    harness = rows(REL/"harness-schedule.csv")
    need(len(harness) == 6 and {r["harness_id"] for r in harness} == {"HAR-CIN-J1","HAR-CIN-J2","HAR-CIN-G1","HAR-COUT-J1","HAR-COUT-J2","HAR-COUT-G1"}, "six harness identities required")
    need(all(r["cut_length_mm"] == "SELECTION REQUIRED" and "DO NOT BUILD" in r["release_state"] for r in harness), "harness cuts/build state changed")
    iface = rows(REL/"interface-control.csv")
    need(len(iface) == 24, "24 endpoint rows required")
    need(sum(r["termination"] == "Panduit PN18-8R-E" for r in iface) == 6, "six source ring endpoints required")
    need(sum(r["termination"] == "VHR-2N / SVH-21T-P1.1" for r in iface) == 18, "eighteen JST terminated endpoints required")
    need(all(r["terminal_or_cavity"] in {"1","2","#8-32 screw interface candidate"} for r in iface), "unexpected inferred terminal")
    cuts = rows(REL/"cut-crimp-schedule.csv")
    need(len(cuts) == 12 and all(r["cut_length_mm"] == r["strip_end_a_mm"] == r["strip_end_b_mm"] == "SELECTION REQUIRED" for r in cuts), "all cuts and strips must remain open")
    need(all(r["state"] == "DO NOT CUT OR CRIMP" for r in cuts), "cut authority leak")
    hbom = rows(REL/"harness-bom.csv")
    hby = {r["manufacturer_part_number"]:r for r in hbom}
    need(hby.get("VHR-2N",{}).get("required_population") == "9", "VHR count incorrect")
    need(hby.get("SVH-21T-P1.1",{}).get("required_population") == "18", "SVH count incorrect")
    need(hby.get("PN18-8R-E",{}).get("required_population") == "6", "ring count incorrect")
    collisions = rows(REL/"stale-placement-collisions.csv")
    need(len(collisions) == 13 and all(float(r["overlap_area_mm2"]) > 0 and "HARD PLANAR COLLISION" in r["disposition"] for r in collisions), "thirteen positive-area stale collisions required")
    placements = rows(REL/"placement-candidate.csv")
    need(len(placements) == 3 and all(r["rotation_deg"] == "90" and r["planar_collision_count"] == "0" and "ANALYTICAL CANDIDATE" in r["release_state"] for r in placements), "three zero-planar-collision held placements required")
    routes = rows(REL/"route-lower-bound.csv")
    need(len(routes) == 6 and all(r["cut_length_mm"] == "SELECTION REQUIRED" and r["state"] == "SCREEN ONLY - DO NOT CUT" for r in routes), "route screen must not release cuts")
    need(len(rows(REL/"manufacturing-process.csv")) == 13 and all(r["execution_state"] == "NOT EXECUTED" for r in rows(REL/"manufacturing-process.csv")), "process must remain unexecuted")
    need(len(rows(REL/"open-holds.csv")) == 10 and all(r["state"] == "OPEN" for r in rows(REL/"open-holds.csv")), "ten holds required")
    need(len(rows(REL/"acceptance-matrix.csv")) == 18 and all(r["execution_state"] == "NOT EXECUTED" and r["result"] == "OPEN" and not r["approver"] for r in rows(REL/"acceptance-matrix.csv")), "acceptance must remain blank")
    sources = rows(REL/"primary-source-register.csv")
    need(len(sources) == 7 and all(r["url"].startswith("https://") and "accessed 2026-08-12" in r["revision_or_date"] for r in sources), "source register incomplete")
    need(all(r["warning"] == WARNING for name in common if name.endswith(".csv") and name != "file-manifest.csv" for r in rows(REL/name)), "warning missing from package CSV")

    master = {r["item_id"]:r for r in rows(ROOT/"bom/bom.csv")}
    need(master["BOM-056"]["quantity"] == "9", "master BOM VHR count stale")
    need(master["BOM-057"]["quantity"] == "18 plus process scrap SELECTION REQUIRED", "master BOM SVH count stale")
    need(master.get("BOM-109",{}).get("manufacturer_part_number") == "PN18-8R-E", "BOM-109 missing")
    config = json.loads((CFG/"package-status.json").read_text(encoding="utf-8"))
    for key,value in {"identifier":"HR-V0-CONFIG-REC-P0.27","round":"R263","system_bom_groups":109,"current_records":45,"supersession_records":40,"bom_integration_records":30,"open_holds":185,"acceptance_rows":234,"dxl_carrier_power_harness":ID}.items():
        need(config.get(key) == value, f"configuration mismatch {key}")
    need(config.get("energization_authorized") is False and config.get("safety_credit") is False, "configuration authority leak")
    current = {r["record_id"]:r for r in rows(CFG/"current-configuration-map.csv")}
    need(current["CFG-04"]["identifier"] == ID, "current harness binding stale")
    bmap = {r["item_id"]:r for r in rows(CFG/"bom-integration-map.csv")}
    need(all(bmap[item]["bound_identifier"] == ID for item in ("BOM-088","BOM-089","BOM-109")), "BOM integration binding stale")

    page = (REL/"index.html").read_text(encoding="utf-8")
    for token in ("font:clamp(16px","font-size:14px","Six real harness identities. Zero released cuts.",">13</div>",">0</div>",WARNING):
        need(token in page, f"guide token missing: {token}")
    svg = (REL/"harness-topology.svg").read_text(encoding="utf-8")
    need("font-size:19px" in svg and "font-size:22px" in svg and "font-size:30px" in svg, "SVG text below project legibility basis")

    for name in common - {"file-manifest.csv"}:
        need((ENG/name).read_bytes() == (REL/name).read_bytes(), f"engineering/release mismatch {name}")
    for directory in (ENG,REL,CFG,CFGR):
        mrows = rows(directory/"file-manifest.csv")
        actual = {path.name for path in directory.iterdir() if path.is_file() and path.name != "file-manifest.csv"}
        need({r["path"] for r in mrows} == actual, f"manifest membership mismatch {directory.name}")
        for row in mrows:
            path = directory/row["path"]
            need(row["sha256"] == sha(path) and int(row["bytes"]) == path.stat().st_size, f"manifest mismatch {directory.name}/{row['path']}")

    if failures:
        print(f"{ID} check FAILED")
        for failure in failures:
            print("-",failure)
        return 1
    print(f"{ID} PASS")
    print("  6 harnesses / 24 endpoints / 9 VHR / 18 SVH / 6 held #8 rings")
    print("  13 stale collisions rejected / 3 zero-planar-collision candidates / 0 released cuts")
    print("  no procurement, fabrication, connection, powered test, motion, energization or safety credit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
