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
    require(len(schematics) == 19, "root plus eighteen native sheets required")
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
        expected = {f"{bus}_RET"}
        expected |= {f"{bus}_DP", f"{bus}_DN"} if row["protocol"].startswith("RS-485") else {f"{bus}_DATA"}
        require(expected <= net_names, f"native nets missing for {bus}")
    axis_power_nets = {row["axis_id"] + "_VDD" for row in allocation}
    require(axis_power_nets <= net_names and len(axis_power_nets) == 25, "25 separate actuator VDD feeds are not encoded")
    require({"PANEL_DC_POS_RAW", "K1_POS_OUT", "TETHER_MAIN_POS", "ACT_MAIN_SAFE_12V", "ACT_0V_CONTROLLED", "SAFETY_24V", "SAFETY_0V", "SAFETY_OUT_K1", "SAFETY_OUT_K2", "SAFETY_PERMIT_HARDWIRED"} <= net_names, "tether-first power/interruption net chain incomplete")
    require({"TTL_LDIST_SAFE_9V", "TTL_RDIST_SAFE_9V", "TTL_HEAD_SAFE_9V"} <= net_names, "three regulated TTL branch rails are incomplete")
    require(not ({"ACT_14V8_SAFE", "ACT_12V_SAFE", "BATT_POS_RAW", "CONTACTOR_POS_IN"} & net_names), "rejected direct 14.8 V architecture remains in native nets")
    require({"ONBOARD_LATER_POS", "ONBOARD_LATER_SD_POS", "ONBOARD_LATER_SOURCE_OUT", "ONBOARD_LATER_RET"} <= net_names, "disconnected onboard-later evaluation path missing")
    require("ONBOARD_LATER_SOURCE_OUT" in net_names and all(row["net"] != "ACT_MAIN_SAFE_12V" or row["reference"] != "PRE_LATER" for row in connector), "onboard-later path is incorrectly tied to controlled main")
    require({"COMPUTE_5V1", "HMI_5V0", "AUX_5V_SAFE", "AUX_0V_STAR", "PELVIS_IMU_DATA", "L_FOOT_SENSOR_DATA", "R_FOOT_SENSOR_DATA", "HEAD_DISPLAY_IPC", "HEAD_CAM_L_IPC", "HEAD_CAM_R_IPC"} <= net_names, "whole-body three-rail auxiliary/sensing/HMI nets incomplete")
    refs = {row["reference"] for row in connector}
    require({"ACB1", "PS1", "CTRLPS1", "TETH1", "REG_TTL_L", "REG_TTL_R", "REG_TTL_H", "BATT_LATER", "SD_LATER", "PRE_LATER", "CHG_LATER", "S0", "S1", "SR1", "WD_INH1", "K1", "K2", "AUXCOM1", "AUXHMI1", "AUXCTL1", "AUXSTAR1", "IMU1", "DISP1", "MIC1", "AMP1", "SPK1", "SPK2", "FAN1", "ADC_L_FOOT", "ADC_R_FOOT"} <= refs, "whole-body energy/safety/three-rail auxiliary/sensing/HMI components incomplete")
    require("AUXD1" not in refs, "obsolete single auxiliary-converter block remains")
    cpu_power = {row["terminal"]: row["net"] for row in connector if row["reference"] == "CPU1" and row["terminal"] in {"LOG-5V", "LOG-RET"}}
    require(cpu_power == {"LOG-5V": "COMPUTE_5V1", "LOG-RET": "AUX_0V_STAR"}, "compute rail binding drift")
    head_power = {row["terminal"]: row["net"] for row in connector if row["reference"] == "HPWR1" and row["terminal"] in {"LOG-IN", "LOG-RET-IN"}}
    require(head_power == {"LOG-IN": "HMI_5V0", "LOG-RET-IN": "AUX_0V_STAR"}, "HMI rail binding drift")
    require(len({ref for ref in refs if ref.startswith("PBR_")}) == 25, "one protection/telemetry boundary per actuator is required")
    require(len({ref for ref in refs if ref.startswith("LOAD_")}) == 8, "bilateral four-point foot sensing incomplete")
    schedule_text = (ECAD / "connector-schedule.csv").read_text(encoding="utf-8")
    require("WITH MIRROR CONTACT" not in schedule_text and "MIRROR / EDM" not in schedule_text, "unsupported mirror-contact claim remains")
    require("MECHANICALLY LINKED AUXILIARY" in schedule_text, "contactor linked-auxiliary EDM boundary missing")
    pinout = rows("interface-carrier-pinout.csv")
    require(len(pinout) == 8 and {row["bus_id"] for row in pinout} == {row["bus_id"] for row in bus_topology}, "eight-channel carrier pinout missing")
    require(sum(row["interface_device"] == "ISOW1432DFMR" for row in pinout) == 5 and sum(row["interface_device"] == "SN74LVC1T45DCKR" for row in pinout) == 3, "interface-device allocation drift")
    require(all("package pin" in row["mcu_tx_or_io"] and "PASK-1" in row["field_header"] and "NO VDD" in row["field_header"] for row in pinout), "physical MCU/field connector boundary incomplete")
    right_distal = next(row for row in pinout if row["bus_id"] == "TTL-RDIST")
    require(right_distal["mcu_tx_or_io"].startswith("PE8 package pin 59 ") and right_distal["mcu_rx"].startswith("PE7 package pin 58 ") and right_distal["mcu_de"].startswith("PE9 package pin 60 "), "TTL-RDIST UART7 package pins overlap or drift from STM32H743ZIT6 LQFP144")
    for ref in ("JMCU_A", "JMCU_B", "JCA1", "JCB1"):
        power = {row["terminal"]: row["net"] for row in connector if row["reference"] == ref and row["terminal"] in {"1", "2", "3"}}
        require(power == {"1": "CTRL_GND", "2": "CTRL_5V", "3": "CTRL_3V3"}, f"{ref} power-contact mapping drift")
    erc = (ECAD / "validation" / f"{PROJECT}-erc.rpt").read_text(encoding="utf-8")
    require(re.search(r"ERC messages:\s+0\s+Errors\s+0\s+Warnings", erc) is not None, "KiCad ERC is not 0 errors / 0 warnings")
    log = (ECAD / "validation" / "kicad-cli.log").read_text(encoding="utf-8")
    require(log.count("exit=0") == 3, "parse/netlist/SVG command did not all pass")
    netlist = (ECAD / "validation" / f"{PROJECT}.net").read_text(encoding="utf-8")
    require(all(ref in netlist for ref in axis_refs), "netlist omits an actuator reference")
    svg = ECAD / "output" / f"{PROJECT}.svg"
    require(svg.is_file() and svg.stat().st_size > 5000, "native hierarchy SVG missing")
    guide = (ECAD / "index.html").read_text(encoding="utf-8")
    require(guide.count("<object ") == 19 and "Explore all 19 native KiCad sheets" in guide and "font:17px/1.55" in guide and "font-size:14px" in guide, "interactive 19-sheet electrical guide missing or illegible")
    status = json.loads((ECAD / "electrical-status.json").read_text(encoding="utf-8"))
    require(status["native_kicad_parsed"] and status["logical_connectivity_reconciled"] and status["actuator_side_physical_pin_mapping_reconciled"] and status["actuator_bus_controller_physical_pin_mapping_reconciled"] and status["actuator_bus_interface_device_candidates_selected"] and status["actuator_bus_data_only_connector_candidates_selected"] and status["tether_first_energy_topology_encoded"] and status["direct_14v8_actuator_source_absent"] and status["individual_actuator_power_feed_count"] == 25 and status["regulated_ttl_branch_count"] == 3 and status["three_rail_auxiliary_architecture_encoded"] and status["auxiliary_converter_candidate"] == "2x RECOM REC30E-2405SZ + 1x TRACO POWER TEN 40-1211E" and status["auxiliary_positive_rails"] == ["COMPUTE_5V1", "HMI_5V0", "AUX_5V_SAFE"] and status["auxiliary_return_star"] == "AUX_0V_STAR" and status["auxiliary_hmi_peak_headroom_w"] == 10 and status["auxiliary_hmi_zero_peak_headroom_blocker"] is False and status["reset_can_command_motion"] is False and status["erc_errors"] == status["erc_warnings"] == 0, "native electrical status incomplete")
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
    require(page.count("HR30-NATIVE-KICAD-P01-START") == 1 and 'id="native-electrical"' in page and "19 native sheets" in page and f"{PROJECT}.kicad_pro" in page and f"{PROJECT}/index.html" in page, "interactive native electrical guide missing")
    print("PASS: native HR-30 KiCad parses as 18 populated sheets with a tether-first 12 V source, three regulated 9 V TTL rails, two series interruption candidates, 25 distinct protected actuator feeds, data-only multidrop buses, complete whole-body interfaces and ERC 0/0; physical energy/safety terminals, protection, functional-safety validation and all work authority remain open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
