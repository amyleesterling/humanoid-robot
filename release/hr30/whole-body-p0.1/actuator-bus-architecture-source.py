"""Generate the protocol-compatible HR-30 P0.1 actuator-bus architecture.

This is a whole-body allocation artifact.  It binds all 25 candidate axes to
five RS-485 and three TTL half-duplex segments without selecting controller
hardware, connector mating parts, pin assignments, protection or harnesses.
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
    "XH540": "https://emanual.robotis.com/docs/en/dxl/x/xh540-w270/",
    "XM540": "https://emanual.robotis.com/docs/en/dxl/x/xm540-w270/",
    "XM430": "https://emanual.robotis.com/docs/en/dxl/x/xm430-w350/",
    "XC330": "https://emanual.robotis.com/docs/en/dxl/x/xc330-m288/",
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
        "interface": "exact transceivers, pins, termination/bias, level shifting, protection, shield/return and data-only harnesses SELECTION REQUIRED",
    })
    write_csv(compute_path, compute)

    bom_path = OUT / "whole-robot-candidate-bom.csv"
    bom = read_csv(bom_path)
    matches = [row for row in bom if row["item_id"] == "HR30-BOM-010"]
    if len(matches) != 1:
        raise SystemExit("controlled HR30-BOM-010 row missing or duplicated")
    matches[0].update({
        "function": "actuator bus interfaces",
        "candidate": "five isolated RS-485 plus three protected TTL half-duplex interfaces; exact devices and pins SELECTION REQUIRED",
        "quantity": "8",
    })
    write_csv(bom_path, bom)


def generate_into_package(refresh: bool = True) -> None:
    allocation = read_csv(OUT / "actuator-transmission-allocation.csv")
    by_axis = {row["axis_id"]: row for row in allocation}
    expected = {axis for axes in BUS_AXES.values() for axis in axes}
    if len(allocation) != 25 or set(by_axis) != expected:
        raise SystemExit("25-axis actuator allocation does not match frozen bus architecture")

    topology = []
    for bus_id, axes in BUS_AXES.items():
        protocol = "RS-485 HALF-DUPLEX" if bus_id.startswith("RS-") else "TTL HALF-DUPLEX"
        topology.append({
            "bus_id": bus_id,
            "protocol": protocol,
            "axis_count": len(axes),
            "axis_ids": " | ".join(axes),
            "physical_layer_candidate": "isolated RS-485 transceiver" if protocol.startswith("RS-485") else "protected 3.3 V TTL interface compatible with ROBOTIS TTL input",
            "actuator_connector_contacts": 4 if protocol.startswith("RS-485") else 3,
            "controller_interface": "SELECTION REQUIRED",
            "termination_bias_level_shift": "SELECTION REQUIRED; verify against selected controller, topology and current manufacturer documentation",
            "power_data_boundary": "DATA-ONLY SEGMENT INTENT; do not backfeed independently protected actuator branches through daisy-chain VDD; exact breakout/harness SELECTION REQUIRED",
            "status": "P0.1 PROTOCOL-COMPATIBLE ALLOCATION; PHYSICAL IMPLEMENTATION UNVALIDATED",
            "authority": "NO CONNECTION, POWERED TEST, MOTION OR ENERGIZATION AUTHORITY",
        })
    write_csv(OUT / "actuator-bus-topology.csv", topology)

    binding = []
    for bus_id, axes in BUS_AXES.items():
        protocol = "RS-485 HALF-DUPLEX" if bus_id.startswith("RS-") else "TTL HALF-DUPLEX"
        for position, axis in enumerate(axes, 1):
            row = by_axis[axis]
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
                "actuator_id": "SELECTION REQUIRED",
                "connector_pin_mapping": "SELECTION REQUIRED; do not infer from family name or presentation diagrams",
                "branch_power_injection": "SELECTION REQUIRED; individually protected branch must not be paralleled through data daisy harness",
                "authority": "NO CONNECTION, POWERED TEST, MOTION OR ENERGIZATION AUTHORITY",
            })
    write_csv(OUT / "actuator-bus-axis-binding.csv", binding)

    sources = []
    for name, title, scope in (
        ("XH540", "DYNAMIXEL XH540-W270/W150 e-Manual", "-R/-T physical variants and 4-contact RS-485 versus 3-contact TTL connector distinction"),
        ("XM540", "DYNAMIXEL XM540-W270 e-Manual", "-R/-T physical variants and connector/interface distinction"),
        ("XM430", "DYNAMIXEL XM430-W350 e-Manual", "-R/-T physical variants and connector/interface distinction"),
        ("XC330", "DYNAMIXEL XC330-M288/M181 e-Manual", "TTL half-duplex physical connection and three-contact connector pin categories"),
    ):
        sources.append({
            "manufacturer": "ROBOTIS",
            "actuator_family": name,
            "document_title": title,
            "official_url": SOURCES[name],
            "accessed_date": ACCESSED,
            "published_revision_or_date": "NOT STATED ON CURRENT WEB MANUAL - UNRESOLVED",
            "verified_scope": scope,
            "not_verified": "exact order code, mating connector, controller interface, pin-level robot wiring, termination/bias, protection and installed EMC",
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

This allocation does **not** select eight controller interfaces or release wiring. Exact controller boards/transceivers, isolation, voltage-domain compatibility, direction control, pins, mating connectors, termination, bias, protection, shield/return treatment, grounding, cable type, routing, actuator IDs, bus timing and failure behavior remain **SELECTION REQUIRED**.

The intended harness separates communication from branch-power distribution. A data daisy chain must not connect actuator VDD between independently protected power branches. An exact connector/breakout design and manufacturer-supported implementation must prove that boundary before connection.

## Relationship to KiCad

The historical `project-button-v2` native KiCad package is mixed HR-V0/HR-30 preliminary architecture and is **not synchronized** to this eight-segment whole-body allocation. A new HR-30-only native KiCad reconciliation must bind all 25 axes, selected interface devices, pins, connectors, protection, grounding, cable/shield rules and shutdown behavior. Until that work exists and receives qualified review, this package grants no connection, powered-test, motion, or energization authority.

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
        "unresolved_item": "The 25 axes are protocol-matched to five RS-485 and three TTL segments, but the HR-30-only native KiCad design, exact controller interfaces and pins, connector/breakout hardware, protection, termination/bias/level shifting, data-only harness isolation, EMC, timing/latency and physical fault tests remain open.",
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
    section = f'''{start}<section id="actuator-buses"><h2>Every actuator now has a protocol-compatible bus</h2><div class="grid"><article class="card pass"><h3>19 RS-485 axes</h3><p>Left leg, right leg, left proximal arm, right proximal arm, and waist are five independently identified RS-485 segments.</p></article><article class="card pass"><h3>6 TTL axes</h3><p>Left wrist/gripper, right wrist/gripper, and head pan/tilt are three protected TTL half-duplex segments.</p></article><article class="card hold"><h3>25 of 25 axes bound</h3><p>The allocation is complete and protocol-compatible. Actuator IDs, interface devices, pins, protection, termination, and harnesses remain selection work.</p></article><article class="card hold"><h3>KiCad remains open</h3><p>The historical mixed project is not an HR-30 whole-body wiring release. A native HR-30-only eight-segment schematic must follow this allocation.</p></article></div><div class="panel"><p><a href="actuator-bus-topology.csv">Eight-segment topology</a> · <a href="actuator-bus-axis-binding.csv">25-axis binding</a> · <a href="actuator-bus-source-register.csv">Official source register</a> · <a href="whole-body-electrical-integration.md">Electrical integration boundary</a></p></div></section>{end}'''
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
