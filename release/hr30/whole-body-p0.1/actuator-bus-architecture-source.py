"""Generate the protocol-compatible HR-30 P0.1 actuator-bus architecture.

This is a whole-body allocation artifact.  It binds all 25 candidate axes to
five RS-485 and three TTL half-duplex segments.  Current official ROBOTIS
manuals establish the actuator-side connector pin order and listed JST parts;
controller hardware, branch protection and installed harness construction stay open.
"""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "hr30" / "whole-body-p0.1"
IDENTIFIER = "HR30-ACTUATOR-BUS-P01"
WARNING = (
    "PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR "
    "PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"
)
ACCESSED = "2026-08-14"


BUS_AXES = {
    "RS-LLEG": ["L_HIP_YAW", "L_HIP_ROLL", "L_HIP_PITCH", "L_KNEE_PITCH", "L_ANKLE_PITCH", "L_ANKLE_ROLL"],
    "RS-RLEG": ["R_HIP_YAW", "R_HIP_ROLL", "R_HIP_PITCH", "R_KNEE_PITCH", "R_ANKLE_PITCH", "R_ANKLE_ROLL"],
    "RS-LARM": ["L_SHOULDER_PITCH", "L_SHOULDER_ROLL", "L_ELBOW_PITCH"],
    "RS-RARM": ["R_SHOULDER_PITCH", "R_SHOULDER_ROLL", "R_ELBOW_PITCH"],
    "RS-WAIST": ["WAIST_YAW"],
    "TTL-LDIST": ["L_WRIST_ROTATION", "L_GRIPPER"],
    "TTL-RDIST": ["R_WRIST_ROTATION", "R_GRIPPER"],
    "TTL-HEAD": ["HEAD_PAN", "HEAD_TILT"],
}


SOURCES = {
    "XH540": "https://docs.robotis.com/docs/dxl/model_reference/x_series/xh_series/xh540-w270/",
    "XM540": "https://docs.robotis.com/docs/dxl/model_reference/x_series/xm_series/xm540-w270/",
    "XM430": "https://docs.robotis.com/docs/dxl/model_reference/x_series/xm_series/xm430-w350/",
    "XC330": "https://docs.robotis.com/docs/dxl/model_reference/x_series/xc_series/xc330-t288/",
}


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def family(candidate: str) -> str:
    for name in ("XH540", "XM540", "XM430", "XC330"):
        if name in candidate:
            return name
    raise SystemExit(f"unclassified actuator candidate: {candidate}")


def update_budget_and_bom() -> None:
    compute_path = OUT / "compute-sensor-network-budget.csv"
    compute = read_csv(compute_path)
    matches = [row for row in compute if row["function"] == "Actuator buses"]
    if len(matches) != 1:
        raise SystemExit("controlled Actuator buses budget row missing or duplicated")
    matches[0].update({
        "candidate": "five RS-485 plus three TTL half-duplex segments",
        "quantity": "8",
        "role_boundary": "RS-485: legs, proximal arms, waist; TTL: head and distal hands",
        "interface": "STM32H743ZIT6 plus 5x complete ISOW1432DFMR and 3x complete SN74LVC1T45DCKR carrier application circuits; native PCB placement exists; routing, stackup/isolation, shield/return and data-only cable assemblies remain open",
    })
    write_csv(compute_path, compute)

    bom_path = OUT / "whole-robot-candidate-bom.csv"
    bom = read_csv(bom_path)
    matches = [row for row in bom if row["item_id"] == "HR30-BOM-010"]
    if len(matches) != 1:
        raise SystemExit("controlled HR30-BOM-010 row missing or duplicated")
    matches[0].update({
        "function": "actuator bus interfaces",
        "candidate": "5x complete ISOW1432DFMR isolated RS-485 plus 3x complete SN74LVC1T45DCKR translated TTL carrier application circuits; two native PCB placement candidates; routing open",
        "quantity": "8",
    })
    write_csv(bom_path, bom)


def generate_into_package(refresh: bool = True) -> None:
    allocation = read_csv(OUT / "actuator-transmission-allocation.csv")
    carrier_pinout = read_csv(OUT / "electrical" / "kicad" / "hr30-whole-body-electrical-p0.1" / "interface-carrier-pinout.csv")
    by_axis = {row["axis_id"]: row for row in allocation}
    by_bus_pinout = {row["bus_id"]: row for row in carrier_pinout}
    expected = {axis for axes in BUS_AXES.values() for axis in axes}
    if len(allocation) != 25 or set(by_axis) != expected or set(by_bus_pinout) != set(BUS_AXES):
        raise SystemExit("25-axis actuator allocation does not match frozen bus architecture")

    topology = []
    for bus_id, axes in BUS_AXES.items():
        protocol = "RS-485 HALF-DUPLEX" if bus_id.startswith("RS-") else "TTL HALF-DUPLEX"
        pinout = by_bus_pinout[bus_id]
        topology.append({
            "bus_id": bus_id,
            "protocol": protocol,
            "axis_count": len(axes),
            "axis_ids": " | ".join(axes),
            "physical_layer_candidate": pinout["interface_device"],
            "actuator_connector_contacts": 4 if protocol.startswith("RS-485") else 3,
            "controller_interface": f"Carrier {pinout['carrier']}; {pinout['stm32_peripheral']}; {pinout['mcu_tx_or_io']}; {pinout['mcu_rx']}; {pinout['mcu_de']}; {pinout['field_header']}",
            "termination_bias_level_shift": "INTERFACE DEVICE PINOUT SELECTED; PCB PASSIVES/LAYOUT, TERMINATION/BIAS, PROTECTION AND VALIDATION REQUIRED",
            "power_data_boundary": "ONE DISTINCT PROTECTED POWER FEED PER ACTUATOR; data-only field connector has no VDD contact; exact power-injection breakout/cable and no-backfeed validation remain open",
            "status": "P0.1 PIN-LEVEL CANDIDATE; PHYSICAL IMPLEMENTATION UNVALIDATED",
            "authority": "NO CONNECTION, POWERED TEST, MOTION OR ENERGIZATION AUTHORITY",
        })
    write_csv(OUT / "actuator-bus-topology.csv", topology)

    binding = []
    for bus_id, axes in BUS_AXES.items():
        protocol = "RS-485 HALF-DUPLEX" if bus_id.startswith("RS-") else "TTL HALF-DUPLEX"
        for position, axis in enumerate(axes, 1):
            row = by_axis[axis]
            pinout = by_bus_pinout[bus_id]
            actuator_family = family(row["candidate_actuator"])
            expected_protocol = "TTL HALF-DUPLEX" if actuator_family == "XC330" else "RS-485 HALF-DUPLEX"
            binding.append({
                "axis_id": axis,
                "region": row["region"],
                "candidate_actuator": row["candidate_actuator"],
                "actuator_family": actuator_family,
                "bus_id": bus_id,
                "segment_position_provisional": position,
                "protocol": protocol,
                "protocol_compatibility": "MATCH" if protocol == expected_protocol else "MISMATCH",
                "actuator_connector_contacts": 3 if actuator_family == "XC330" else 4,
                "official_interface_source": SOURCES[actuator_family],
                "official_interface_accessed_date": ACCESSED,
                "actuator_id": "SELECTION REQUIRED",
                "connector_pin_mapping": (
                    "ACTUATOR SIDE VERIFIED: 1=GND; 2=VDD; 3=DATA"
                    if actuator_family == "XC330"
                    else "ACTUATOR SIDE VERIFIED: 1=GND; 2=VDD; 3=DATA+; 4=DATA-"
                ),
                "actuator_side_housing": "JST EHR-03" if actuator_family == "XC330" else "JST EHR-04",
                "actuator_pcb_header": "JST B3B-EH-A" if actuator_family == "XC330" else "JST B4B-EH-A",
                "actuator_side_crimp_terminal": "JST SEH-001T-P0.6",
                "manufacturer_published_dynamixel_wire_gauge": "21 AWG",
                "controller_side_connector_and_pin_mapping": pinout["field_header"],
                "branch_power_injection": "ONE SEPARATELY PROTECTED ACTUATOR FEED; this axis does not share VDD; data daisy carries only reference and data",
                "authority": "NO CONNECTION, POWERED TEST, MOTION OR ENERGIZATION AUTHORITY",
            })
    write_csv(OUT / "actuator-bus-axis-binding.csv", binding)

    sources = []
    for name, title, scope in (
        ("XH540", "DYNAMIXEL XH540-W270/W150 e-Manual", "-R RS-485 actuator side: pin 1 GND, 2 VDD, 3 DATA+, 4 DATA-; JST EHR-04/B4B-EH-A/SEH-001T-P0.6; published DYNAMIXEL wire gauge 21 AWG"),
        ("XM540", "DYNAMIXEL XM540-W270 e-Manual", "-R RS-485 actuator side: pin 1 GND, 2 VDD, 3 DATA+, 4 DATA-; JST EHR-04/B4B-EH-A/SEH-001T-P0.6; published DYNAMIXEL wire gauge 21 AWG"),
        ("XM430", "DYNAMIXEL XM430-W350 e-Manual", "-R RS-485 actuator side: pin 1 GND, 2 VDD, 3 DATA+, 4 DATA-; JST EHR-04/B4B-EH-A/SEH-001T-P0.6; published DYNAMIXEL wire gauge 21 AWG"),
        ("XC330", "DYNAMIXEL XC330-T288 Docs", "TTL actuator side: pin 1 GND, 2 VDD, 3 DATA; JST EHR-03/B3B-EH-A/SEH-001T-P0.6; published DYNAMIXEL wire gauge 21 AWG"),
    ):
        sources.append({
            "manufacturer": "ROBOTIS",
            "actuator_family": name,
            "document_title": title,
            "official_url": SOURCES[name],
            "accessed_date": ACCESSED,
            "published_revision_or_date": "NOT STATED ON CURRENT WEB MANUAL - UNRESOLVED",
            "verified_scope": scope,
            "not_verified": "exact actuator procurement order code, assembled cable product, controller-side connector/interface, termination/bias, protection, conductor application sizing and installed EMC",
        })
    write_csv(OUT / "actuator-bus-source-register.csv", sources)

    (OUT / "whole-body-electrical-integration.md").write_text(f"""# HR-30 whole-body electrical integration P0.1

**{WARNING}**

## What changed

The 25-axis candidate population is not one electrical protocol. The nineteen selected `-R` XH540/XM540/XM430 candidates are assigned to five RS-485 half-duplex segments. The six XC330 candidates are assigned to three TTL half-duplex segments. Every axis appears exactly once in `actuator-bus-axis-binding.csv`.

| Segment | Protocol | Axes | Role |
|---|---:|---:|---|
| RS-LLEG / RS-RLEG | RS-485 | 6 + 6 | independently serviceable left and right legs |
| RS-LARM / RS-RARM | RS-485 | 3 + 3 | proximal arms only |
| RS-WAIST | RS-485 | 1 | waist yaw |
| TTL-LDIST / TTL-RDIST | TTL | 2 + 2 | wrist and gripper on each side |
| TTL-HEAD | TTL | 2 | head pan and tilt |

## Physical implementation boundary

Current primary manufacturer documentation closes the actuator-side pin order and listed connector piece parts: RS-485 pin 1 GND, 2 VDD, 3 DATA+, 4 DATA-; TTL pin 1 GND, 2 VDD, 3 DATA. It also closes the STM32H743ZIT6 LQFP144 UART package pins, five ISOW1432DFMR isolated RS-485 device pinouts, three SN74LVC1T45DCKR 3.3/5 V translator pinouts, and eight JST PA data-only field connector candidates sized for the planning conductors. The field connectors intentionally contain reference and data only, with no actuator-VDD contact. Assembled cables, received conductor insulation O.D., crimp tooling, actuator power-injection breakout, termination, bias, protection, shield/return treatment, grounding, routing, actuator IDs, bus timing, EMC and failure behavior remain **SELECTION REQUIRED**.

The P0.1 candidate now allocates one separately protected power feed per actuator. Axes listed on one bus share only reference and data; they do not share VDD. Standard ROBOTIS X3P/X4P cables include VDD and therefore require a custom/de-pinned data-only construction or breakout. Exact protection values, connector/breakout design and physical no-backfeed verification remain required before connection.

## Relationship to KiCad

The HR-30-only native KiCad project now binds all 25 axes and the eight sourced pin-level interface candidates across nineteen populated sheets with ERC 0/0. That is encoded connectivity and annotation evidence only. Carrier PCB passives/layout, protection, grounding, cable/shield rules, timing, shutdown behavior and physical fault validation remain open, so this package grants no connection, powered-test, motion, or energization authority.

## Primary manufacturer evidence

The protocol classification is taken from current official ROBOTIS e-Manual pages recorded in `actuator-bus-source-register.csv`, accessed {ACCESSED}. The web manuals did not expose an explicit publication revision/date in the verified page content, so that field remains unresolved rather than inferred.
""", encoding="utf-8", newline="\n")

    update_budget_and_bom()
    status_path = OUT / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "whole_body_actuator_bus_architecture_present": True,
        "actuator_bus_segment_count": 8,
        "actuator_bus_axis_binding_count": 25,
        "rs485_actuator_axis_count": 19,
        "ttl_actuator_axis_count": 6,
        "protocol_compatibility_screen_complete": True,
        "actuator_side_connector_pinout_verified": True,
        "actuator_bus_controller_pin_map_selected": True,
        "actuator_bus_interface_device_candidates_selected": True,
        "actuator_bus_data_only_connector_candidates_selected": True,
        "native_hr30_kicad_reconciled": False,
        "actuator_bus_interface_selected": False,
        "actuator_bus_connector_harness_validated": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    holds_path = OUT / "open-holds.csv"
    holds = read_csv(holds_path)
    holds = [row for row in holds if row["hold_id"] != "HR30-P01-H11"]
    holds.append({
        "hold_id": "HR30-P01-H11",
        "unresolved_item": "The native HR-30 KiCad project now binds all 25 axes, eight STM32 UART pin groups, five ISOW1432DFMR plus three SN74LVC1T45DCKR interfaces, and JST PA data-only connector candidates whose published contact ranges include the planning conductors. Received insulation O.D., crimp tooling, assembled cable and power-injection breakout hardware, protection, termination/bias, EMC, timing/latency, grounding and physical fault tests remain open.",
        "state": "OPEN",
        "release_effect": "BLOCKS CONNECTION, POWERED TEST, MOTION AND ENERGIZATION",
    })
    write_csv(holds_path, holds)

    page_path = OUT / "index.html"
    page = page_path.read_text(encoding="utf-8")
    start = "<!-- HR30-ACTUATOR-BUS-P01-START -->"
    end = "<!-- HR30-ACTUATOR-BUS-P01-END -->"
    if start in page and end in page:
        page = page.split(start, 1)[0] + page.split(end, 1)[1]
    marker = "<section><h2>System artifacts</h2>"
    section = f'''{start}<section id="actuator-buses"><h2>Every actuator now has a protocol-compatible bus</h2><div class="grid"><article class="card pass"><h3>19 RS-485 axes</h3><p>Left leg, right leg, left proximal arm, right proximal arm, and waist are five independently identified RS-485 segments.</p></article><article class="card pass"><h3>6 TTL axes</h3><p>Left wrist/gripper, right wrist/gripper, and head pan/tilt are three protected TTL half-duplex segments.</p></article><article class="card pass"><h3>Both ends pinned</h3><p>Primary sources bind the actuator pins, eight STM32 channels, interface-device pins, and exact data-only field connectors.</p></article><article class="card hold"><h3>Harness remains preliminary</h3><p>PCB layout/passives, assembled cables, branch protection, sizing, termination and physical tests remain selection work.</p></article></div><div class="panel"><p><a href="actuator-bus-topology.csv">Eight-segment topology</a> · <a href="actuator-bus-axis-binding.csv">25-axis binding</a> · <a href="actuator-bus-source-register.csv">Official source register</a> · <a href="whole-body-electrical-integration.md">Electrical integration boundary</a></p></div></section>{end}'''
    if marker not in page:
        raise SystemExit("system artifact marker missing from web guide")
    page_path.write_text(page.replace(marker, section + marker), encoding="utf-8", newline="\n")

    shutil.copy2(Path(__file__), OUT / "actuator-bus-architecture-source.py")
    if refresh:
        import generate_hr30_system_package_p01 as system
        shutil.copy2(ROOT / "tools" / "generate_hr30_system_package_p01.py", OUT / "system-package-source.py")
        system.refresh_manifest_and_release()


def main() -> int:
    generate_into_package(refresh=True)
    print(json.dumps({"identifier": IDENTIFIER, "segments": 8, "axes": 25, "rs485_axes": 19, "ttl_axes": 6, "native_hr30_kicad_reconciled": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
