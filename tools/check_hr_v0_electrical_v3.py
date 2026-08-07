"""Validate the generated HR-V0 Electrical V3 connected candidate.

This checker proves generated-source consistency and KiCad export health only.
It does not validate component suitability, functional safety, fabrication, or
permission to energize.
"""

from __future__ import annotations

import csv
import hashlib
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_hr_v0_electrical_v3 as gen  # noqa: E402


OUT = ROOT / "electrical" / "kicad" / "project-button-v3"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"


def read_csv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def pin_map(components: dict[str, gen.Component], ref: str) -> dict[str, str]:
    return {pin.number: pin.net for pin in components[ref].pins}


def sexpr_blocks(text: str, head: str) -> list[str]:
    """Return balanced top-level blocks whose opening line is ``(head``."""
    blocks: list[str] = []
    for match in re.finditer(rf"(?m)^\s*\({re.escape(head)}\s*$", text):
        start = text.find("(", match.start())
        depth = 0
        in_string = False
        escaped = False
        for index in range(start, len(text)):
            char = text[index]
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
                continue
            if char == '"':
                in_string = True
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    blocks.append(text[start:index + 1])
                    break
    return blocks


def main() -> int:
    failures: list[str] = []
    require(gen.REV == "V3-P1.4", f"unexpected generated revision {gen.REV}", failures)
    sheets = gen.sheets()
    components = {comp.ref: comp for sheet in sheets for comp in sheet.components}
    all_components = [(sheet, comp) for sheet in sheets for comp in sheet.components]
    all_pins = [(sheet, comp, pin) for sheet, comp in all_components for pin in comp.pins]

    require(len(sheets) == 12, f"expected 12 child sheets, found {len(sheets)}", failures)
    require(len(components) == 76, f"expected 76 unique component blocks, found {len(components)}", failures)
    require(len(all_components) == len(components), "duplicate component reference exists", failures)
    require(len(all_pins) == 295, f"expected 295 modeled terminals, found {len(all_pins)}", failures)
    require(all(re.fullmatch(r"[A-Za-z]+[0-9]+", ref) for ref in components),
            "one or more references violate KiCad annotation syntax", failures)

    contactor_status = "PROPOSED - CATALOG DC ENVELOPE FOUND; CRITICAL-CURRENT AND APPLICATION CONFIRMATION REQUIRED; TEST REQUIRED"
    for ref in ("K1", "K2"):
        require(components[ref].status == contactor_status,
                f"{ref} contactor application status is not the controlled critical-current disposition", failures)
        require("MKTED210011EN" in components[ref].evidence,
                f"{ref} lacks current Schneider catalog evidence", failures)
        require("critical-current" in components[ref].description.lower(),
                f"{ref} description omits the lower-current critical-current boundary", failures)

    expected_schematics = {f"{gen.PROJECT}.kicad_sch", *(sheet.filename for sheet in sheets)}
    actual_schematics = {path.name for path in OUT.glob("*.kicad_sch")}
    require(actual_schematics == expected_schematics,
            f"schematic file set mismatch: expected {sorted(expected_schematics)}, found {sorted(actual_schematics)}", failures)

    manifest_rows = read_csv("SOURCE-MANIFEST.csv")
    actual_manifest = {row["file"]: row["sha256"] for row in manifest_rows}
    expected_manifest = {
        path.relative_to(OUT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest().upper()
        for path in OUT.rglob("*")
        if path.is_file() and path.name != "SOURCE-MANIFEST.csv"
    }
    require(actual_manifest == expected_manifest, "source manifest differs from the current V3 file set", failures)

    connector_rows = read_csv("connector-schedule.csv")
    expected_connector = Counter(
        (sheet.filename, comp.ref, pin.number, pin.name, pin.net, comp.status)
        for sheet, comp, pin in all_pins
    )
    actual_connector = Counter(
        (row["sheet"], row["reference"], row["terminal"], row["pin_name"], row["net"], row["status"])
        for row in connector_rows
    )
    require(actual_connector == expected_connector, "connector schedule differs from generated model", failures)
    require(sum(row["terminal"].startswith("TBD-") for row in connector_rows) == 24,
            "controlled TBD-terminal count changed; review and update checker intentionally", failures)

    expected_net_counts = Counter(pin.net for _, _, pin in all_pins)
    expected_wire_numbers = gen.build_wire_numbers(sheets, expected_net_counts)
    wire_rows = read_csv("wire-number-table.csv")
    expected_wires = Counter(
        (wire_number, sheet.filename, comp.ref, pin.number, pin.name, pin.net)
        for sheet, comp, pin in all_pins
        if (wire_number := expected_wire_numbers.get((comp.ref, pin.number))) is not None
    )
    actual_wires = Counter(
        (row["wire_number"], row["sheet"], row["reference"], row["terminal"], row["pin_name"], row["net"])
        for row in wire_rows
    )
    require(actual_wires == expected_wires, "wire-number table differs from generated schematic labels", failures)
    require(len(wire_rows) == 259, f"expected 259 labeled connected terminals, found {len(wire_rows)}", failures)
    require(len({row["wire_number"] for row in wire_rows}) == len(wire_rows),
            "wire numbers are not unique", failures)

    expected_nets: dict[str, list[str]] = {}
    for sheet, comp, pin in all_pins:
        expected_nets.setdefault(pin.net, []).append(f"{sheet.filename}:{comp.ref}:{pin.number}")
    net_rows = read_csv("net-schedule.csv")
    actual_nets = {
        row["net"]: (int(row["connection_count"]), row["connections"].split(" | "))
        for row in net_rows
    }
    require(set(actual_nets) == set(expected_nets), "net schedule name set differs from generated model", failures)
    for net, connections in expected_nets.items():
        count, actual_connections = actual_nets.get(net, (-1, []))
        require(count == len(connections) and actual_connections == connections,
                f"net schedule mismatch for {net}", failures)
    require(len(expected_nets) == 100, f"expected 100 modeled nets, found {len(expected_nets)}", failures)

    native_text = (OUT / "validation" / f"{gen.PROJECT}.net").read_text(encoding="utf-8-sig")
    native_refs = set(re.findall(r'\(comp\s+\(ref "([^"]+)"\)', native_text))
    require(native_refs == set(components), "native KiCad netlist component set differs from generator", failures)
    native_node_net: dict[tuple[str, str], str] = {}
    native_net_names: list[str] = []
    for block in sexpr_blocks(native_text, "net"):
        name_match = re.search(r'\(name "([^"]+)"\)', block)
        require(name_match is not None, "native KiCad net without a name", failures)
        if name_match is None:
            continue
        name = name_match.group(1)
        native_net_names.append(name)
        for ref, pin in re.findall(r'\(node\s+\(ref "([^"]+)"\)\s+\(pin "([^"]+)"\)', block):
            key = (ref, pin)
            require(key not in native_node_net, f"native terminal {ref}:{pin} appears on multiple nets", failures)
            native_node_net[key] = name
    require(len(native_net_names) == 100, f"expected 100 native KiCad nets, found {len(native_net_names)}", failures)
    require(sum(name.startswith("unconnected-(") for name in native_net_names) == 36,
            "expected 36 deliberate native unconnected nets", failures)
    require(len(native_node_net) == 295, f"expected 295 native KiCad netlist nodes, found {len(native_node_net)}", failures)
    for _, comp, pin in all_pins:
        native_name = native_node_net.get((comp.ref, pin.number), "")
        if expected_net_counts[pin.net] == 1:
            require(native_name.startswith("unconnected-("),
                    f"singleton terminal {comp.ref}:{pin.number} is not a native unconnected net", failures)
        else:
            require(native_name == pin.net,
                    f"native net mismatch at {comp.ref}:{pin.number}: expected {pin.net}, found {native_name or 'MISSING'}", failures)
    require('(tool "Eeschema 10.0.5")' in native_text, "native netlist tool version is not Eeschema 10.0.5", failures)
    require(f'(rev "{gen.REV}")' in native_text, f"native netlist does not identify {gen.REV}", failures)

    bom_rows = read_csv("bom.csv")
    expected_bom_refs = {comp.ref for _, comp in all_components if comp.quantity}
    require({row["reference"] for row in bom_rows} == expected_bom_refs,
            "V3 BOM reference set differs from nonzero-quantity generated components", failures)
    require(len(bom_rows) == 74, f"expected 74 BOM records, found {len(bom_rows)}", failures)

    unresolved_rows = read_csv("unresolved-selections.csv")
    unresolved_keys = ("SELECTION REQUIRED", "DESIGN REQUIRED", "CONFIRMATION REQUIRED", "VERIFICATION REQUIRED", "MAPPING REQUIRED", "RELEASE OPEN")
    expected_unresolved = {
        (sheet.filename, comp.ref, comp.status, comp.description)
        for sheet, comp in all_components
        if any(key in comp.status for key in unresolved_keys)
    }
    actual_unresolved = {
        (row["sheet"], row["reference"], row["status"], row["evidence_needed"])
        for row in unresolved_rows
    }
    require(actual_unresolved == expected_unresolved, "unresolved-selection register differs from model", failures)
    require(len(unresolved_rows) == 63, f"expected 63 unresolved component/interface rows, found {len(unresolved_rows)}", failures)

    require(pin_map(components, "S0") == {
        "R-1": "SR1_S11", "R-2": "WD1_SAFETY_IN",
        "L-1": "SR1_S21", "L-2": "WD2_SAFETY_IN",
    }, "E-stop channel mapping changed", failures)
    require(pin_map(components, "KWD1")["11"] == "WD1_SAFETY_IN" and
            pin_map(components, "KWD1")["14"] == "SR1_S12" and
            pin_map(components, "KWD2")["11"] == "WD2_SAFETY_IN" and
            pin_map(components, "KWD2")["14"] == "SR1_S22",
            "watchdog contacts no longer interrupt both SR1 input returns", failures)
    require(pin_map(components, "SR1")["13"] == "SRA1_S11" and
            pin_map(components, "SR1")["14"] == "SRA1_S12" and
            pin_map(components, "SR1")["23"] == "SRA1_S21" and
            pin_map(components, "SR1")["24"] == "SRA1_S22",
            "SR1 safety outputs no longer feed the two SRA1 input channels directly", failures)
    require(pin_map(components, "S1")["TBD-R2"] == "SR1_START_RETURN",
            "RESET no longer returns only to SR1 monitored start", failures)
    require(pin_map(components, "S2")["TBD-A2"] == "ARM_AFTER_S2",
            "ARM output mapping changed", failures)
    for ref in ("S1", "S2"):
        device = components[ref]
        require("COMPLETE ORDER CODE FROZEN" in device.status and
                "RECEIVED-LOT TERMINAL MAPPING REQUIRED" in device.status,
                f"{ref} received-lot terminal-mapping gate changed", failures)
        require("2026-06-15" in device.description and
                "no component detail" in device.description and
                "Do not copy legacy or push-in terminal numbers" in device.description,
                f"{ref} IDEC production-transition evidence changed", failures)
    require(pin_map(components, "K1")["22"] == "EDM_K1_OUT" and
            pin_map(components, "K2")["21"] == "EDM_K1_OUT" and
            pin_map(components, "K2")["22"] == "SRA1_START_RETURN",
            "K1/K2 mirror-contact EDM chain changed", failures)
    require(pin_map(components, "KWD1")["A1"] == "SAFETY_24V" and
            pin_map(components, "KWD1")["A2"] == "WD1_COIL_N" and
            pin_map(components, "UDRV1")["16"] == "WD1_COIL_N" and
            pin_map(components, "KWD2")["A1"] == "SAFETY_24V" and
            pin_map(components, "KWD2")["A2"] == "WD2_COIL_N" and
            pin_map(components, "UDRV2")["16"] == "WD2_COIL_N",
            "watchdog relay low-side coil routing changed", failures)
    require(pin_map(components, "KWD1")["21"] == "SAFETY_24V" and
            pin_map(components, "KWD1")["22"] == "WD1_NC_24V" and
            pin_map(components, "KWD2")["21"] == "SAFETY_24V" and
            pin_map(components, "KWD2")["22"] == "WD2_NC_24V",
            "watchdog NC feedback source mapping changed", failures)
    require(pin_map(components, "UFB1") == {
        "1": "SAFETY_0V", "2": "WD_3V3", "3": "WD_3V3", "4": "UFB_OUT1",
        "5": "UFB_OUT2", "6": "INTENTIONALLY_UNUSED_UFB1_6",
        "7": "INTENTIONALLY_UNUSED_UFB1_7", "8": "SAFETY_0V", "9": "SAFETY_0V",
        "10": "FB_IN2", "11": "FB_SENSE2", "12": "INTENTIONALLY_UNUSED_UFB1_12",
        "13": "INTENTIONALLY_UNUSED_UFB1_13", "14": "SAFETY_0V", "15": "FB_IN1",
        "16": "FB_SENSE1",
    }, "ISO1212DBQ pin-level mapping changed", failures)
    require(components["UFB1"].footprint == "Package_SO:SSOP-16_3.9x4.9mm_P0.635mm",
            "ISO1212DBQ package candidate no longer matches the 3.9 x 4.9 mm, 0.635 mm-pitch DBQ body", failures)
    require(pin_map(components, "RTH1") == {"1": "WD1_NC_24V", "2": "FB_SENSE1"} and
            pin_map(components, "RSN1") == {"1": "FB_SENSE1", "2": "FB_IN1"} and
            pin_map(components, "CFI1") == {"1": "FB_SENSE1", "2": "SAFETY_0V"} and
            pin_map(components, "RW1") == {"1": "WD1_NC_24V", "2": "SAFETY_0V"} and
            pin_map(components, "RSO1") == {"1": "UFB_OUT1", "2": "WD1_NC_DIAG"} and
            pin_map(components, "RPD1") == {"1": "WD1_NC_DIAG", "2": "SAFETY_0V"},
            "watchdog feedback channel 1 network changed", failures)
    require(pin_map(components, "RTH2") == {"1": "WD2_NC_24V", "2": "FB_SENSE2"} and
            pin_map(components, "RSN2") == {"1": "FB_SENSE2", "2": "FB_IN2"} and
            pin_map(components, "CFI2") == {"1": "FB_SENSE2", "2": "SAFETY_0V"} and
            pin_map(components, "RW2") == {"1": "WD2_NC_24V", "2": "SAFETY_0V"} and
            pin_map(components, "RSO2") == {"1": "UFB_OUT2", "2": "WD2_NC_DIAG"} and
            pin_map(components, "RPD2") == {"1": "WD2_NC_DIAG", "2": "SAFETY_0V"},
            "watchdog feedback channel 2 network changed", failures)
    require(pin_map(components, "CDEC1") == {"1": "WD_3V3", "2": "SAFETY_0V"},
            "ISO1212 logic-side decoupling mapping changed", failures)
    require(components["CDEC1"].footprint == "Capacitor_SMD:C_0805_2012Metric",
            "CDEC1 footprint changed from the controlled compact 0805 candidate", failures)
    expected_feedback_values = {
        "RTH1": "Vishay MMA02040C1001FB300, 1.00 kOhm 1% 0.4 W MELF",
        "RTH2": "Vishay MMA02040C1001FB300, 1.00 kOhm 1% 0.4 W MELF",
        "RSN1": "Panasonic ERJ6ENF5620V, 562 Ohm 1% 0805",
        "RSN2": "Panasonic ERJ6ENF5620V, 562 Ohm 1% 0805",
        "CFI1": "TDK CGA3E2X7R1H103K080AA, 10 nF 50 V X7R 0603",
        "CFI2": "TDK CGA3E2X7R1H103K080AA, 10 nF 50 V X7R 0603",
        "RW1": "Vishay CRCW12102K70FKEA, 2.70 kOhm 1% 0.5 W 1210",
        "RW2": "Vishay CRCW12102K70FKEA, 2.70 kOhm 1% 0.5 W 1210",
        "CDEC1": "Murata GRM21BR71H104KA01L, 100 nF 50 V X7R 0805",
        "RSO1": "Panasonic ERJ6ENF1001V, 1.00 kOhm 1% 0805",
        "RSO2": "Panasonic ERJ6ENF1001V, 1.00 kOhm 1% 0805",
        "RPD1": "Panasonic ERJ6ENF1002V, 10.0 kOhm 1% 0805",
        "RPD2": "Panasonic ERJ6ENF1002V, 10.0 kOhm 1% 0805",
    }
    require(all(components[ref].value == value for ref, value in expected_feedback_values.items()),
            "watchdog feedback passive identity changed", failures)
    require(pin_map(components, "ISO1") == {
        "1": "HB_LED_A", "2": "COMPUTE_0V", "3": "SAFETY_0V", "4": "WD_HEARTBEAT",
    }, "VO618A heartbeat optocoupler pin mapping changed", failures)
    require(pin_map(components, "RHB1") == {"1": "PI_HEARTBEAT", "2": "HB_LED_A"} and
            pin_map(components, "RHP1") == {"1": "WD_3V3", "2": "WD_HEARTBEAT"},
            "heartbeat input resistor or watchdog pullup mapping changed", failures)
    expected_unused_1 = {str(pin): f"INTENTIONALLY_UNUSED_UDRV1_{pin}" for pin in range(10, 16)}
    expected_unused_2 = {str(pin): f"INTENTIONALLY_UNUSED_UDRV2_{pin}" for pin in range(10, 16)}
    require(pin_map(components, "UDRV1") == {
        "1": "WD1_DRIVE", **{str(pin): "SAFETY_0V" for pin in range(2, 9)},
        "9": "SAFETY_24V", **expected_unused_1, "16": "WD1_COIL_N",
    }, "TPL7407LPWR channel-1 pin mapping changed", failures)
    require(pin_map(components, "UDRV2") == {
        "1": "WD2_DRIVE", **{str(pin): "SAFETY_0V" for pin in range(2, 9)},
        "9": "SAFETY_24V", **expected_unused_2, "16": "WD2_COIL_N",
    }, "TPL7407LPWR channel-2 pin mapping changed", failures)
    require(pin_map(components, "CDRV1") == {"1": "SAFETY_24V", "2": "SAFETY_0V"} and
            pin_map(components, "CDRV2") == {"1": "SAFETY_24V", "2": "SAFETY_0V"},
            "driver COM bypass mapping changed", failures)
    require(pin_map(components, "WDCTRL1") == {
        "39": "WD_5V", "38": "SAFETY_0V", "36": "WD_3V3", "4": "WD_HEARTBEAT",
        "5": "WD1_DRIVE", "6": "WD2_DRIVE", "9": "WD1_NC_DIAG", "10": "WD2_NC_DIAG",
        "D3": "WD_SWDIO", "D1": "WD_SWCLK", "D2": "SAFETY_0V",
    }, "Pico power/GPIO assignment changed", failures)
    require(pin_map(components, "JWP1") == {
        "1": "SAFETY_24V", "2": "SAFETY_0V", "3": "WD1_COIL_N", "4": "WD2_COIL_N",
    }, "watchdog PCB power/coil connector pin allocation changed", failures)
    require(pin_map(components, "JWF1") == {
        "1": "WD1_NC_24V", "2": "WD2_NC_24V",
    }, "watchdog PCB feedback connector pin allocation changed", failures)
    require(pin_map(components, "JWH1") == {
        "1": "PI_HEARTBEAT", "2": "COMPUTE_0V",
    }, "watchdog PCB heartbeat connector pin allocation changed", failures)
    expected_testpoints = {
        "TP1": "SAFETY_24V", "TP2": "SAFETY_0V", "TP3": "WD_5V", "TP4": "WD_3V3",
        "TP5": "PI_HEARTBEAT", "TP6": "WD_HEARTBEAT", "TP7": "WD1_DRIVE", "TP8": "WD2_DRIVE",
        "TP9": "WD1_COIL_N", "TP10": "WD2_COIL_N", "TP11": "WD1_NC_24V", "TP12": "WD2_NC_24V",
        "TP13": "UFB_OUT1", "TP14": "UFB_OUT2", "TP15": "WD_SWDIO", "TP16": "WD_SWCLK",
    }
    require(all(pin_map(components, ref) == {"1": net} for ref, net in expected_testpoints.items()),
            "watchdog PCB test-point net allocation changed", failures)
    require(all(components[ref].footprint == "PBV3_Footprints:Harwin_S1751_46R" for ref in expected_testpoints),
            "one or more test points no longer use the frozen Harwin footprint", failures)
    expected_board_refs = {
        "DC1", "ISO1", "RHB1", "RHP1", "WDCTRL1", "UDRV1", "UDRV2", "CDRV1", "CDRV2",
        "UFB1", "RTH1", "RSN1", "CFI1", "RW1", "RTH2", "RSN2", "CFI2", "RW2",
        "CDEC1", "RSO1", "RSO2", "RPD1", "RPD2", "JWP1", "JWF1", "JWH1",
        *expected_testpoints,
    }
    require({ref for ref, comp in components.items() if comp.watchdog_pcb} == expected_board_refs,
            "watchdog PCB membership changed", failures)
    require(all(components[ref].footprint for ref in expected_board_refs),
            "one or more board-mounted references lack a footprint", failures)
    require(pin_map(components, "KP1") == {
        "1L1": "K1_P1_IN", "2T1": "K1_J12", "3L2": "K1_J12",
        "4T2": "K1_J23", "5L3": "K1_J23", "6T3": "K1_OUT",
    }, "K1 three-pole series representation changed", failures)
    require(pin_map(components, "KP2") == {
        "1L1": "K1_OUT", "2T1": "K2_J12", "3L2": "K2_J12",
        "4T2": "K2_J23", "5L3": "K2_J23", "6T3": "ACT_12V_BUS",
    }, "K2 three-pole series representation changed", failures)
    require(pin_map(components, "U1")["TTL-2"].startswith("INTENTIONALLY_UNUSED"),
            "U2D2 VDD is no longer explicitly omitted", failures)
    injection = pin_map(components, "INJ1")
    require(pin_map(components, "U1")["TTL-1"] == "ACT_0V_PE_BONDED" and
            injection["CTRL:1"] == "ACT_0V_PE_BONDED" and
            injection["CTRL:2"].startswith("INTENTIONALLY_UNUSED") and
            injection["CTRL:3"] == "DXL_TTL_DATA",
            "U2D2/star-board reference, omitted VDD or DATA mapping changed", failures)
    require({injection[f"PWR{index}:1"] for index in (1, 2, 3)} == {"J1_VDD", "J2_VDD", "J3_VDD"} and
            all(injection[f"PWR{index}:2"] == "ACT_0V_PE_BONDED" for index in (1, 2, 3)),
            "star-board branch-power inputs are no longer three separate VDD rails with common return", failures)
    require({injection[f"ACT{index}:2"] for index in (1, 2, 3)} == {"J1_VDD", "J2_VDD", "J3_VDD"} and
            all(injection[f"ACT{index}:1"] == "ACT_0V_PE_BONDED" and
                injection[f"ACT{index}:3"] == "DXL_TTL_DATA" for index in (1, 2, 3)),
            "star-board actuator outputs changed or positive rails are no longer isolated", failures)
    require({pin_map(components, ref)["2"] for ref in ("J1", "J2", "J3")} == {"J1_VDD", "J2_VDD", "J3_VDD"},
            "actuator VDD branches are no longer separate", failures)
    require({pin_map(components, ref)["3"] for ref in ("J1", "J2", "J3")} == {"DXL_TTL_DATA"},
            "actuator data net is no longer common", failures)
    require(components["SP1"].status.startswith("DNP - PROHIBITED"),
            "prohibited extra 0V/PE star point is no longer DNP", failures)
    for ref in ("F0", "F1", "F2", "F3", "FSR1", "FSR2"):
        require("SELECTION REQUIRED" in components[ref].status,
                f"{ref} appears released despite unresolved sizing", failures)

    erc = (OUT / "validation" / f"{gen.PROJECT}-erc.rpt").read_text(encoding="utf-8-sig")
    require("ERC messages: 0  Errors 0  Warnings 0" in erc, "KiCad ERC is not 0 errors / 0 warnings", failures)
    log = (OUT / "validation" / "kicad-cli.log").read_text(encoding="utf-8-sig")
    require(log.count("exit=0") == 4, "not all four KiCad CLI validation/export commands exited 0", failures)
    require("annotation errors" not in log.lower(), "KiCad reported annotation errors", failures)

    svg_files = sorted((OUT / "output").glob("*.svg"))
    require(len(svg_files) == 13, f"expected 13 SVG pages including index, found {len(svg_files)}", failures)
    for path in svg_files:
        require(WARNING.encode() in path.read_bytes(), f"warning missing from {path.name}", failures)
    pdf = OUT / "output" / f"{gen.PROJECT}-preliminary.pdf"
    require(pdf.is_file() and pdf.stat().st_size > 100_000, "native PDF export missing or unexpectedly small", failures)
    pdfinfo_candidates = (
        Path(r"C:\Users\amyle\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdfinfo.exe"),
        Path(r"C:\Program Files\poppler\Library\bin\pdfinfo.exe"),
    )
    pdfinfo = next((candidate for candidate in pdfinfo_candidates if candidate.exists()), None)
    if pdfinfo is not None and pdf.is_file():
        info = subprocess.run(
            [str(pdfinfo), "-f", "1", "-l", "13", "-box", str(pdf)],
            check=False,
            capture_output=True,
            text=True,
        )
        a3_pages = re.findall(r"Page\s+\d+ size:\s+[0-9.]+ x [0-9.]+ pts \(A3\)", info.stdout)
        require(info.returncode == 0, "pdfinfo failed for synchronized PDF", failures)
        require(len(a3_pages) == 13, f"expected all 13 PDF pages to be A3, found {len(a3_pages)}", failures)
    readme = (OUT / "README.md").read_text(encoding="utf-8-sig")
    require(WARNING in readme and f"# Project Button HR-V0 Electrical {gen.REV}" in readme and
            "Generated ERC proves only modeled connectivity/annotation" in readme,
            "README warning/ERC caveat missing", failures)

    if failures:
        print("HR-V0 Electrical V3 validation: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("HR-V0 Electrical V3 validation: PASS")
    print("13 native pages; 76 component blocks; 295 terminals; 64 named connected + 36 unconnected nets; 259 unique wire labels; 63 unresolved rows")
    print(WARNING)
    print("ERC/export consistency is not design approval or permission to energize.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
