#!/usr/bin/env python3
"""Fail-closed checks for HR-V0-PANEL-P2P-P0.1 / R222."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release/hr-v0/panel-point-to-point-p0.1"
P118 = ROOT / "electrical/kicad/project-button-v3-p1.18-panel-topology-candidate"
R221 = ROOT / "release/hr-v0/panel-conductor-basis-p0.1/endpoint-conductor-candidate-schedule.csv"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def need(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    errors: list[str] = []
    required = {
        "point-to-point-wire-schedule.csv", "endpoint-to-wire-map.csv", "terminal-node-register.csv",
        "source-register.csv", "open-holds.csv", "authority-boundary.csv", "package-status.json", "index.html",
    }
    need(required <= {path.name for path in OUT.iterdir()}, "package file set incomplete", errors)
    wires = rows(OUT / "point-to-point-wire-schedule.csv")
    mapping = rows(OUT / "endpoint-to-wire-map.csv")
    nodes = rows(OUT / "terminal-node-register.csv")
    sources = rows(OUT / "source-register.csv")
    holds = rows(OUT / "open-holds.csv")
    authority = rows(OUT / "authority-boundary.csv")
    legacy = rows(R221)
    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))

    need(len(wires) == 55 and len({r["wire_id"] for r in wires}) == 55, "expected 55 unique physical wires", errors)
    need(len(mapping) == 66 and len({r["legacy_endpoint_id"] for r in mapping}) == 66, "expected 66 unique legacy mappings", errors)
    need({r["legacy_endpoint_id"] for r in mapping} == {r["wire_number"] for r in legacy}, "legacy endpoint coverage changed", errors)
    need(all(r["physical_wire_id"] in {w["wire_id"] for w in wires} for r in mapping), "mapping references unknown wire", errors)
    need(all(r["from_reference"] and r["from_terminal"] and r["to_reference"] and r["to_terminal"] for r in wires), "blank wire end found", errors)
    need(all((r["from_reference"], r["from_terminal"]) != (r["to_reference"], r["to_terminal"]) for r in wires), "self-connected wire found", errors)

    state_counts = Counter(r["candidate_state"] for r in wires)
    need(state_counts == {"FIXED-INTERNAL FAMILY/GAUGE CANDIDATE ONLY": 45, "NO DYNAMIC-FLEX CANDIDATE": 10}, "conductor-state count changed", errors)
    door_ids = {r["wire_number"] for r in legacy if r["reference"] in {"S0", "S1", "S2", "H1"}}
    door_wires = {r["physical_wire_id"] for r in mapping if r["legacy_endpoint_id"] in door_ids}
    need(len(door_ids) == 10 and len(door_wires) == 10, "door endpoint/wire count changed", errors)
    need(all(next(w for w in wires if w["wire_id"] == wid)["conductor_family_candidate"] == "SELECTION REQUIRED" for wid in door_wires), "door wire falsely selected", errors)
    need(all(r["exact_color_order_code"] == "SELECTION REQUIRED" and r["cut_length_mm"] == "SELECTION REQUIRED" and r["termination_from"] == "SELECTION REQUIRED" and r["termination_to"] == "SELECTION REQUIRED" and r["release_state"] == "NOT RELEASED" for r in wires), "wire release boundary changed", errors)

    expected_nodes = {"XD24": "3273114", "XD0": "3273112", "XN1": "3209549", "XN2": "3209549", "XN3": "3209549"}
    need({r["reference"]: r["mpn"] for r in nodes} == expected_nodes, "terminal-node identity changed", errors)
    endpoint_counts = Counter()
    for wire in wires:
        endpoint_counts[wire["from_reference"]] += 1
        endpoint_counts[wire["to_reference"]] += 1
    need({ref: endpoint_counts[ref] for ref in expected_nodes} == {"XD24": 15, "XD0": 8, "XN1": 3, "XN2": 3, "XN3": 3}, "terminal-node allocation changed", errors)
    need(len(sources) == 6 and {r["source_id"] for r in sources} == {f"P2P-SRC-{i:03d}" for i in range(1, 7)}, "source register changed", errors)
    need(len(holds) == 10 and all(r["accepted"] == "FALSE" for r in holds), "open-hold boundary changed", errors)
    need(len(authority) == 4 and sum(r["allowed"] == "TRUE" for r in authority) == 1, "authority boundary changed", errors)

    p118_connectors = rows(P118 / "connector-schedule.csv")
    p118_map = {(r["reference"], r["terminal"]): r["net"] for r in p118_connectors}
    expected_pins = {
        **{("XD24", "LINE"): "SAFETY_24V"}, **{("XD24", f"{i:02d}"): "SAFETY_24V" for i in range(1, 15)},
        **{("XD0", "LINE"): "SAFETY_0V"}, **{("XD0", f"{i:02d}"): "SAFETY_0V" for i in range(1, 8)},
        **{(node, str(i)): net for node, net in (("XN1", "SR1_S12"), ("XN2", "SRA1_S12"), ("XN3", "SR1_STATUS")) for i in range(1, 4)},
    }
    need({key: p118_map.get(key) for key in expected_pins} == expected_pins, "P1.18 terminal pin/net map changed", errors)
    erc = (P118 / "validation/project-button-v3-p1.18-panel-topology-candidate-erc.rpt").read_text(encoding="utf-8-sig")
    need("ERC messages: 0  Errors 0  Warnings 0" in erc, "P1.18 ERC is not 0/0", errors)
    need(status.get("identifier") == "HR-V0-PANEL-P2P-P0.1" and status.get("round") == "R222", "package identity changed", errors)
    need(status.get("source_endpoint_count") == 66 and status.get("physical_conductor_count") == 55 and status.get("explicit_terminal_nodes") == 5, "package counts changed", errors)
    need(not status.get("fabrication_approved") and not status.get("connection_approved") and not status.get("energization_approved"), "false authority asserted", errors)

    page = (OUT / "index.html").read_text(encoding="utf-8")
    for token in (WARNING, "66/66", "55", "XD24", "XD0", "XN1", "font:16px", "font-size:14px"):
        need(token in page, f"web guide missing {token}", errors)
    for path in [*OUT.iterdir(), P118 / "README.md"]:
        if path.is_file() and path.suffix.lower() in {".csv", ".json", ".html", ".md"}:
            need(WARNING in path.read_text(encoding="utf-8-sig"), f"warning absent: {path.relative_to(ROOT)}", errors)

    if errors:
        print("HR-V0 panel point-to-point P0.1: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("HR-V0 panel point-to-point P0.1: PASS")
    print("55 two-ended conductors; 66/66 legacy endpoints mapped once; 5 explicit nodes; P1.18 ERC 0/0")
    print("10 door conductors and all lengths/colors/terminations remain unselected; no work authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
