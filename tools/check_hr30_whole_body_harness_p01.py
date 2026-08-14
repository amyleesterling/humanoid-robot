"""Fail-closed checks for the HR-30 P0.1 whole-body harness package."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "hr30" / "whole-body-p0.1"
OUT = PKG / "harness"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / "harness"
WARNING = "PRELIMINARY - NOT APPROVED FOR CONNECTION, FABRICATION, MOTION OR ENERGIZATION"

def need(ok: bool, message: str):
    if not ok: raise SystemExit("FAIL: " + message)

def rows(name: str) -> list[dict]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle: return list(csv.DictReader(handle))

def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    pins, buses, drops = rows("actuator-side-pinout-register.csv"), rows("bus-harness-assembly-register.csv"), rows("actuator-drop-register.csv")
    corridors, boundaries, sources = rows("corridor-fill-budget.csv"), rows("connector-boundary-register.csv"), rows("harness-source-register.csv")
    assemblies, equipment = rows("harness-assembly-register.csv"), rows("equipment-interface-register.csv")
    loops, termination, terminal_binding = rows("service-loop-register.csv"), rows("bus-termination-register.csv"), rows("logical-terminal-binding.csv")
    need(len(pins) == 4 and {r["family"] for r in pins} == {"XH540","XM540","XM430","XC330"}, "four actuator families missing")
    need(all(r["accessed_date"] == "2026-08-14" and r["closure_state"] == "VERIFIED AT ACTUATOR INTERFACE ONLY" and r["manufacturer_published_dynamixel_wire_gauge"] == "21 AWG" for r in pins), "actuator-side evidence state drift")
    need(len(buses) == 8 and len(drops) == 25 and len({r["axis_id"] for r in drops}) == 25, "whole-body bus/drop coverage incomplete")
    need(abs(sum(float(r["candidate_12v_stall_endpoint_sum_a"]) for r in buses) - 76.08) < 1e-9, "published stall endpoint arithmetic drift")
    need(all("NOT NORMAL DEMAND" in r["endpoint_use_boundary"] and r["controller_interface"] == "SELECTION REQUIRED" for r in buses), "endpoint/controller release boundary missing")
    need(len(corridors) == 12 and {"HN01_HEAD_BRANCH","HN01_HEAD_POWER_BRANCH"} <= {r["route_id"] for r in corridors}, "twelve routes or separate head routes missing")
    need(sum(r["service_class"] == "ACTUATOR POWER" for r in corridors) == 6, "six power routes required")
    need(len(boundaries) == 33 and sum(r["boundary_type"] == "CONTROLLER / SEGMENT" for r in boundaries) == 8, "connector boundaries incomplete")
    need(len(assemblies) == 14 and len({r["assembly_id"] for r in assemblies}) == 14, "fourteen whole-body harness assemblies missing")
    installed = list(csv.DictReader((PKG / "installed-equipment-register.csv").open(encoding="utf-8")))
    need(len(equipment) == len(installed) == 57 and {r["item_id"] for r in equipment} == {r["item_id"] for r in installed}, "installed equipment harness completeness missing")
    need(len(loops) == 25 and {r["axis_id"] for r in loops} == {r["axis_id"] for r in drops} and all(r["cycle_life_test"] == "NOT EXECUTED" for r in loops), "moving service-loop obligations incomplete")
    need(len(termination) == 8 and all(r["controller_end_termination"] == "SELECTION REQUIRED" for r in termination), "bus termination register incomplete")
    connector_schedule = list(csv.DictReader((PKG / "electrical" / "kicad" / "hr30-whole-body-electrical-p0.1" / "connector-schedule.csv").open(encoding="utf-8")))
    need(len(terminal_binding) == len(connector_schedule) == 283, "logical terminal completeness spine missing")
    need(len(sources) == 7 and {"U2D2","U2D2-PHB","JST-EH"} <= {r["source_id"] for r in sources}, "primary source register incomplete")
    status = json.loads((OUT / "harness-status.json").read_text(encoding="utf-8"))
    need((status["axis_drop_count"], status["bus_branch_count"], status["corridor_count"], status["connector_boundary_count"], status["harness_assembly_count"], status["installed_equipment_binding_count"], status["service_loop_obligation_count"], status["logical_terminal_binding_count"]) == (25,8,12,33,14,57,25,283), "status counts drift")
    need(status["u2d2_final_controller_role"] == status["u2d2_power_hub_whole_body_role"] == "REJECT", "U2D2 role boundary drift")
    need(not any(status[k] for k in ("controller_side_connectors_selected","assembled_cables_selected","protection_selected","conductor_sizing_released","harness_validated","connection_authority","fabrication_authority","powered_test_authority","motion_authority","energization_authority")), "harness package overclaims release")
    page = (OUT / "index.html").read_text(encoding="utf-8")
    need("font:17px" in page and "font-size:14px" in page and "12 located corridors" in page and "overflow:auto" in page, "web guide legibility/content drift")
    root_page = (PKG / "index.html").read_text(encoding="utf-8")
    need(root_page.count("HR30-HARNESS-P01-START") == 1 and 'id="whole-body-harness"' in root_page and "harness/index.html" in root_page, "whole-body guide does not expose harness package")
    need((OUT / "whole-body-harness-map.svg").stat().st_size > 3000, "whole-body harness SVG missing")
    need(sha(OUT / "whole-body-harness-source.py") == sha(ROOT / "tools" / "generate_hr30_whole_body_harness_p01.py"), "generator snapshot drift")
    manifest = rows("file-manifest.csv")
    files = {p.name for p in OUT.iterdir() if p.is_file()}
    need({r["path"] for r in manifest} == files - {"file-manifest.csv"}, "manifest set drift")
    need(all(r["warning"] == WARNING and r["sha256"] == sha(OUT / r["path"]) and int(r["bytes"]) == (OUT / r["path"]).stat().st_size for r in manifest), "manifest content drift")
    need(files == {p.name for p in REL.iterdir() if p.is_file()} and all(sha(p) == sha(REL / p.name) for p in OUT.iterdir() if p.is_file()), "source/release harness mismatch")
    print("PASS: HR-30 harness maps 8 protected bus branches, 25 drops, 33 connector boundaries and 12 corridors; actuator-side pins are verified while selection, validation and all work authority remain open")
    return 0

if __name__ == "__main__": raise SystemExit(main())
