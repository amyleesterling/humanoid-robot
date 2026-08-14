"""Fail-closed validation of the native HR-30 whole-body KiCad P0.1 project."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "hr30" / "whole-body-p0.1"
REL_PACKAGE = ROOT / "release" / "hr30" / "whole-body-p0.1"
PROJECT = "hr30-whole-body-electrical-p0.1"
ECAD = PACKAGE / "electrical" / "kicad" / PROJECT
WARNING = "PRELIMINARY - NOT APPROVED FOR CONNECTION, FABRICATION, MOTION OR ENERGIZATION"


def require(condition: bool, message: str):
    if not condition:
        raise SystemExit("FAIL: " + message)


def rows(name: str) -> list[dict]:
    with (ECAD / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    schematics = sorted(ECAD.glob("*.kicad_sch"))
    require(len(schematics) == 18, "root plus seventeen native sheets required")
    require((ECAD / f"{PROJECT}.kicad_pro").is_file(), "native KiCad project missing")
    require(all(WARNING in path.read_text(encoding="utf-8") for path in schematics), "preliminary warning missing from schematic")
    connector = rows("connector-schedule.csv")
    axis_refs = {row["reference"] for row in connector if row["reference"].startswith("AX_")}
    allocation = list(csv.DictReader((PACKAGE / "actuator-transmission-allocation.csv").open(encoding="utf-8")))
    require(axis_refs == {"AX_" + row["axis_id"] for row in allocation} and len(axis_refs) == 25, "native schematic does not contain exact 25-axis allocation")
    axis_rows = [row for row in connector if row["reference"].startswith("AX_")]
    physical_prefixes = ("MCU_IO_", "JMCU_", "JCA", "JCB", "J_RS", "J_TTL", "ISO_", "LVL_")
    other_rows = [row for row in connector if not row["reference"].startswith(("AX_",) + physical_prefixes)]
    require(all(row["terminal"].startswith("LOG-") for row in other_rows), "unselected non-interface physical terminal number was inferred")
    for ref in axis_refs:
        pins = {row["terminal"]: row["pin_name"] for row in axis_rows if row["reference"] == ref}
        if ref in {"AX_" + row["axis_id"] for row in allocation if "XC330" in row["candidate_actuator"]}:
            require(pins == {"1": "GND", "2": "VDD", "3": "DATA"}, f"TTL actuator-side pinout drift at {ref}")
        else:
            require(pins == {"1": "GND", "2": "VDD", "3": "DATA+", "4": "DATA-"}, f"RS-485 actuator-side pinout drift at {ref}")
    bus_topology = list(csv.DictReader((PACKAGE / "actuator-bus-topology.csv").open(encoding="utf-8")))
    require(len(bus_topology) == 8, "eight-segment source topology missing")
    nets = rows("net-schedule.csv")
    net_names = {row["net"] for row in nets}
    for row in bus_topology:
        bus = row["bus_id"]
        expected = {f"{bus}_VDD", f"{bus}_RET"}
        expected |= {f"{bus}_DP", f"{bus}_DN"} if row["protocol"].startswith("RS-485") else {f"{bus}_DATA"}
        require(expected <= net_names, f"native nets missing for {bus}")
    require({"BATT_POS_RAW", "CONTACTOR_POS_IN", "K1_POS_OUT", "ACT_14V8_SAFE", "ACT_12V_SAFE", "SAFETY_PERMIT_HARDWIRED"} <= net_names, "power/interruption net chain incomplete")
    require({"AUX_5V_SAFE", "PELVIS_IMU_DATA", "L_FOOT_SENSOR_DATA", "R_FOOT_SENSOR_DATA", "HEAD_DISPLAY_IPC", "HEAD_CAM_L_IPC", "HEAD_CAM_R_IPC"} <= net_names, "whole-body auxiliary sensing/HMI nets incomplete")
    refs = {row["reference"] for row in connector}
    require({"AUXD1", "IMU1", "DISP1", "MIC1", "AMP1", "SPK1", "SPK2", "FAN1", "ADC_L_FOOT", "ADC_R_FOOT"} <= refs, "whole-body sensing/HMI components incomplete")
    require(len({ref for ref in refs if ref.startswith("LOAD_")}) == 8, "bilateral four-point foot sensing incomplete")
    pinout = rows("interface-carrier-pinout.csv")
    require(len(pinout) == 8 and {row["bus_id"] for row in pinout} == {row["bus_id"] for row in bus_topology}, "eight-channel carrier pinout missing")
    require(sum(row["interface_device"] == "ISOW1432DFMR" for row in pinout) == 5 and sum(row["interface_device"] == "SN74LVC1T45DCKR" for row in pinout) == 3, "interface-device allocation drift")
    require(all("package pin" in row["mcu_tx_or_io"] and "BM0" in row["field_header"] and "NO VDD" in row["field_header"] for row in pinout), "physical MCU/field connector boundary incomplete")
    erc = (ECAD / "validation" / f"{PROJECT}-erc.rpt").read_text(encoding="utf-8")
    require(re.search(r"ERC messages:\s+0\s+Errors\s+0\s+Warnings", erc) is not None, "KiCad ERC is not 0 errors / 0 warnings")
    log = (ECAD / "validation" / "kicad-cli.log").read_text(encoding="utf-8")
    require(log.count("exit=0") == 3, "parse/netlist/SVG command did not all pass")
    netlist = (ECAD / "validation" / f"{PROJECT}.net").read_text(encoding="utf-8")
    require(all(ref in netlist for ref in axis_refs), "netlist omits an actuator reference")
    svg = ECAD / "output" / f"{PROJECT}.svg"
    require(svg.is_file() and svg.stat().st_size > 5000, "native hierarchy SVG missing")
    guide = (ECAD / "index.html").read_text(encoding="utf-8")
    require(guide.count("<object ") == 18 and "Explore all 18 native KiCad sheets" in guide and "font:17px/1.55" in guide and "font-size:14px" in guide, "interactive 18-sheet electrical guide missing or illegible")
    status = json.loads((ECAD / "electrical-status.json").read_text(encoding="utf-8"))
    require(status["native_kicad_parsed"] and status["logical_connectivity_reconciled"] and status["actuator_side_physical_pin_mapping_reconciled"] and status["actuator_bus_controller_physical_pin_mapping_reconciled"] and status["actuator_bus_interface_device_candidates_selected"] and status["actuator_bus_data_only_connector_candidates_selected"] and status["erc_errors"] == status["erc_warnings"] == 0, "native electrical status incomplete")
    require(not any(status[k] for k in ("physical_pin_mapping_reconciled", "interface_devices_selected", "protection_values_selected", "functional_safety_validated", "connection_authority", "fabrication_authority", "powered_test_authority", "motion_authority", "energization_authority")), "native status overclaims release")
    package_status = json.loads((PACKAGE / "package-status.json").read_text(encoding="utf-8"))
    require(package_status["native_hr30_kicad_present"] and package_status["native_hr30_kicad_logical_connectivity_reconciled"] and package_status["native_hr30_kicad_actuator_side_pins_reconciled"], "whole-body package does not expose reconciled actuator-side KiCad pins")
    require(not package_status["native_hr30_kicad_reconciled"] and not package_status["native_hr30_kicad_physical_pins_selected"], "full physical reconciliation overclaimed")
    require(sha(ECAD / "native-kicad-source.py") == sha(ROOT / "tools" / "generate_hr30_whole_body_electrical_p01.py"), "native generator snapshot drift")
    manifest = rows("SOURCE-MANIFEST.csv")
    files = {p.relative_to(ECAD).as_posix() for p in ECAD.rglob("*") if p.is_file()}
    require({r["path"] for r in manifest} == files - {"SOURCE-MANIFEST.csv"}, "native manifest set mismatch")
    require(all(int(r["bytes"]) == (ECAD / r["path"]).stat().st_size and r["sha256"] == sha(ECAD / r["path"]) for r in manifest), "native manifest hash/byte mismatch")
    rel_ecad = REL_PACKAGE / "electrical" / "kicad" / PROJECT
    require({p.relative_to(ECAD).as_posix() for p in ECAD.rglob("*") if p.is_file()} == {p.relative_to(rel_ecad).as_posix() for p in rel_ecad.rglob("*") if p.is_file()}, "native source/release file-set mismatch")
    require(all(sha(p) == sha(rel_ecad / p.relative_to(ECAD)) for p in ECAD.rglob("*") if p.is_file()), "native source/release byte mismatch")
    page = (PACKAGE / "index.html").read_text(encoding="utf-8")
    require(page.count("HR30-NATIVE-KICAD-P01-START") == 1 and 'id="native-electrical"' in page and "18 native sheets" in page and f"{PROJECT}.kicad_pro" in page and f"{PROJECT}/index.html" in page, "interactive native electrical guide missing")
    print("PASS: native HR-30 KiCad parses as 18 populated sheets with 25 actuator axes, explicit head/pelvis/foot interfaces, sourced actuator and controller pins, five isolated RS-485 plus three translated TTL channels, exact data-only connector candidates and ERC 0/0; PCB validation, protection, safety validation and all work authority remain open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
