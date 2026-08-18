#!/usr/bin/env python3
"""Generate the HR-30 actuator cable-kit engineering candidate.

This package turns the verified ROBOTIS/JST device interface and the existing
25-axis physical/current-policy datasets into explicit incoming and outgoing
connector cavity records.  Cable families remain test-coupon candidates where
manufacturer compatibility, bus behavior, or flex behavior is unresolved.
Nothing generated here releases procurement, fabrication, connection or power.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
PHYSICAL = WHOLE / "harness" / "physical-p0.1"
POLICY = WHOLE / "harness" / "current-policy-binding-p0.1"
BRACKETS = WHOLE / "harness" / "actuator-transition-brackets-p0.1"
OUT = WHOLE / "harness" / "actuator-cable-kit-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "harness" / OUT.name
IDENTIFIER = "HR30-ACTUATOR-CABLE-KIT-P0.1"
DATE = "2026-08-17"
WARNING = "PRELIMINARY - UNBUILT ACTUATOR CABLE-KIT CANDIDATE - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"
AUTHORITY = "NO PROCUREMENT, FABRICATION, CONNECTION, POWERED-TEST, MOTION OR ENERGIZATION AUTHORITY"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def common(row: dict[str, object]) -> dict[str, object]:
    return {**row, "execution_state": "NOT EXECUTED", "authority": AUTHORITY, "warning": WARNING}


def source_rows() -> list[dict[str, object]]:
    local = [
        ("ACK-S01", POLICY / "axis-power-policy-binding.csv", "25-axis current-cap and routed-length binding"),
        ("ACK-S02", PHYSICAL / "bus-physical-link-register.csv", "25 physical bus links and outgoing-link topology"),
        ("ACK-S03", PHYSICAL / "actuator-interface-verification-register.csv", "manufacturer actuator interface verification"),
        ("ACK-S04", PHYSICAL / "manufacturer-interface-discrepancy-register.csv", "existing interface discrepancy register"),
        ("ACK-S24", BRACKETS / "bracket-status.json", "dimensioned 25-axis transition-bracket status"),
        ("ACK-S25", BRACKETS / "placement-register.csv", "25 module-specific transition-bracket placements"),
    ]
    rows = []
    for ident, path, role in local:
        if not path.is_file():
            raise FileNotFoundError(path)
        rows.append(common({"source_id": ident, "publisher": "Project Button", "document": role, "revision_or_date": "current generated P0.1 input", "official_url_or_path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "verified_scope": role}))
    official = [
        ("ACK-S05", "JST", "EH connector series product page", "live official page; accessed 2026-08-16", "https://www.jst-mfg.com/product/index.php?lang=2&series=58", "2.5 mm pitch; 3 A at AWG22; AWG32-22 / 0.032-0.33 mm2; EHR-3 and EHR-4 housings"),
        ("ACK-S06", "JST", "EH connector series data sheet", "current official PDF; accessed 2026-08-16", "https://www.jst-mfg.com/product/pdf/eng/eEH.pdf", "SEH-001T-P0.6 standard contact; AWG30-22; low-insertion-force contacts less vibration resistant"),
        ("ACK-S07", "ROBOTIS", "DYNAMIXEL X-series and U2D2 interface documentation", "live official documentation; accessed 2026-08-16", "https://docs.robotis.com/docs/parts/interface/u2d2/", "RS-485 pin 1 GND/2 VDD/3 D+/4 D-; TTL pin 1 GND/2 VDD/3 DATA; EHR-04/EHR-03 notation"),
        ("ACK-S08", "igus", "chainflex CF9.UL product page", "live official page; accessed 2026-08-16", "https://www.igus.com/product/CF9_UL", "CF9.UL.02.02 is 2 x 0.25 mm2 / 24 AWG, TPE, continuous-flex and torsion-rated up to +/-90 degrees per metre under published conditions"),
        ("ACK-S09", "igus", "chainflex CF9.UL English data sheet", "current official PDF; accessed 2026-08-16; visible footer 2014", "https://www.igus.com/contentData/Product_Files/Download/pdf/CF9-UL_en.pdf", "CF9.UL.02.02 construction, 5xd minimum bend radius in normal temperature band, and published flex/torsion application limits"),
        ("ACK-S10", "igus", "chainflex CF9.UL.02.02 current product data", "live official product page; accessed 2026-08-16", "https://www.igus.cn/zh-CN/product/CF9_UL?artNr=CF9.UL.02.02&category=control-cable", "maximum conductor resistance at 20 C is 79 ohm/km for the exact CF9.UL.02.02 article"),
        ("ACK-S11", "igus", "chainflex CFBUS.PVC product page", "live official page; accessed 2026-08-16", "https://www.igus.com/product/CFBUS_PVC", "CFBUS.PVC.001 is a shielded 2 x 0.25 mm2 PROFIBUS cable; published characteristic impedance approximately 150 ohm"),
        ("ACK-S12", "igus", "chainflex CFROBOT3 product page", "live official page; accessed 2026-08-16", "https://www.igus.com/product/CFROBOT3", "CFROBOT3.02.03.02 is a shielded twistable 3-pair 24 AWG robot cable; pair impedance is not published on the cited page"),
        ("ACK-S13", "Alpha Wire", "86202 Xtra-Guard Flex product page", "live official page; accessed 2026-08-16", "https://www.alphawire.com/en/products/cable/xtra-guard-performance-cable/xtra-guard-flex/86202", "2 x 24 AWG twisted continuous-flex cable; nominal characteristic impedance 87 ohm and 29 ohm/1000 ft conductor DCR at 20 C"),
        ("ACK-S14", "Alpha Wire", "AZ221934 hook-up wire product page", "live official page; accessed 2026-08-16", "https://www.alphawire.com/products/wire/hook-up-wire/premium/az221934", "22 AWG ETFE hook-up wire, -55 to 150 C, 600 V and nominal 15.1 ohm/1000 ft DCR at 20 C; no continuous-flex robot qualification claimed"),
        ("ACK-S15", "igus", "chainflex CF240 product page", "live official page; accessed 2026-08-16", "https://www.igus.com/product/CF240", "CF240.01.03 is shielded 3 x 26 AWG / 0.14 mm2; twist/controlled impedance not established on page"),
        ("ACK-S16", "Alpha Wire", "3051 product page and customer specification", "live official page/specification; accessed 2026-08-17", "https://www.alphawire.com/products/wire/hook-up-wire/premium/3051", "22 AWG 7/30 tinned copper; 1.575 +/- 0.051 mm OD; nominal DCR 16.2 ohm/1000 ft at 20 C; 10xd bend radius; static suspended-commissioning coupon candidate only"),
        ("ACK-S17", "igus", "chainflex CF130-UL product page", "live official page; accessed 2026-08-17", "https://www.igus.com/product/CF130_UL", "CF130.03.02.UL is 2 x 22 AWG / 0.34 mm2 medium-duty moving cable; published 7.5xd minimum radius at +15 to +60 C for five million double strokes"),
        ("ACK-S18", "Molex", "Micro-Fit 3.0 series 43025 receptacle-housing chart", "live official page; accessed 2026-08-17", "https://www.molex.com/en-us/products/series-chart/43025", "430250200 is a 2-circuit dual-row receptacle housing; polarized and locked to its mating part; -40 to +105 C"),
        ("ACK-S19", "Molex", "Micro-Fit 3.0 series 43020 plug-housing chart", "live official page; accessed 2026-08-17", "https://www.molex.com/en-us/products/series-chart/43020", "430200200 is a 2-circuit dual-row plug housing with panel-mount ears; polarized and locked to its mating part; -40 to +105 C"),
        ("ACK-S20", "Molex", "Micro-Fit 3.0 series 43030 female-terminal chart", "live official page; accessed 2026-08-17", "https://www.molex.com/en-us/products/series-chart/43030", "430300001 is the tin-plated female crimp terminal for 24-20 AWG and 1.85 mm maximum insulation diameter; 30 mating cycles"),
        ("ACK-S21", "Molex", "Micro-Fit 3.0 series 43031 male-terminal chart", "live official page; accessed 2026-08-17", "https://www.molex.com/en-us/products/series-chart/43031", "430310001 is the tin-plated male crimp terminal for 24-20 AWG and 1.85 mm maximum insulation diameter; 30 mating cycles"),
        ("ACK-S22", "Molex", "Micro-Fit 3.0 dual-row product specification PS-43045", "revision R; 2025-11-14", "https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/productspecificationpdf/430/43045/PS-43045-001.pdf", "wire-to-wire system scope and 43025/43020/43030/43031 family relationship; application-specific current derating remains required"),
        ("ACK-S23", "Molex", "Micro-Fit 3.0 application specification 430450001-AS", "revision A1; approved 2025-11-21", "https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/applicationspecificationspdf/430/43045/430450001-AS-000.pdf", "crimp/application guidance for 18-30 AWG stranded copper wire and standard Micro-Fit families"),
    ]
    rows.extend(common({"source_id": i, "publisher": p, "document": d, "revision_or_date": rev, "official_url_or_path": url, "sha256": "N/A - LIVE PRIMARY SOURCE", "verified_scope": scope}) for i, p, d, rev, url, scope in official)
    return rows


def connector_rows() -> list[dict[str, object]]:
    data = [
        ("ACK-C01", "RS-485 actuator input", "JST EHR-4", "JST SEH-001T-P0.6", "JST B4B-EH-A device header", "4", "CANONICAL CANDIDATE ORDER CODES BOUND; RECEIVED FIT/KEYING/RETENTION AND CRIMP VALIDATION OPEN"),
        ("ACK-C02", "TTL actuator input", "JST EHR-3", "JST SEH-001T-P0.6", "JST B3B-EH-A device header", "3", "CANONICAL CANDIDATE ORDER CODES BOUND; RECEIVED FIT/KEYING/RETENTION AND CRIMP VALIDATION OPEN"),
        ("ACK-C03", "contact style", "standard insertion-force contact", "JST SEH-001T-P0.6", "EHR-3/EHR-4", "N/A", "CANDIDATE - LOW-INSERTION-FORCE L-CONTACTS REJECTED FOR WALKING-VIBRATION APPLICATION"),
        ("ACK-C04", "ROBOTIS EHR-03/EHR-04 notation", "JST canonical EHR-3/EHR-4", "JST SEH-001T-P0.6", "ROBOTIS device headers", "3/4", "NOMENCLATURE RECONCILED AT CANDIDATE ORDER-CODE LEVEL; RECEIVED MATING INSPECTION OPEN"),
        ("ACK-C05", "dynamic-cable side of fixed transition", "Molex 430250200", "Molex 430300001", "Molex 430200200 panel-mount plug", "2", "CANDIDATE FAMILY BOUND; CF130 CORE OD, CRIMP, DERATING, RETENTION AND RECEIVED FIT REMAIN OPEN"),
        ("ACK-C06", "restrained actuator-pigtail side of fixed transition", "Molex 430200200", "Molex 430310001", "Molex 430250200 receptacle", "2", "CANDIDATE FAMILY BOUND; PANEL MOUNT, 3051 CRIMP, POLARITY, RETENTION AND RECEIVED FIT REMAIN OPEN"),
    ]
    return [common({"decision_id": i, "interface": interface, "candidate_housing": housing, "candidate_contact": contact, "mating_boundary": mate, "positions": positions, "disposition": disposition, "procurement_released": "NO"}) for i, interface, housing, contact, mate, positions, disposition in data]


def axis_rows() -> list[dict[str, object]]:
    policy = read_csv(POLICY / "axis-power-policy-binding.csv")
    if len(policy) != 25:
        raise RuntimeError("25-axis policy input required")
    rows = []
    for source in policy:
        cap = float(source["candidate_internal_limit_a"])
        stall = float(source["published_stall_endpoint_a"])
        if cap > 2.499010 + 1e-9:
            raise RuntimeError(f"unexpected current-cap drift: {source['axis_id']}")
        round_trip_m = float(source["round_trip_planning_length_mm"]) / 1000.0
        loop_resistance_20c = 0.079 * round_trip_m
        drop_20c = cap * loop_resistance_20c
        loss_20c = cap * cap * loop_resistance_20c
        rows.append(common({
            "axis_id": source["axis_id"], "bus_id": source["bus_id"], "actuator_model": source["actuator_model"],
            "destination_connector": source["destination_connector"], "positive_net": source["positive_net"], "return_net": source["return_net"],
            "candidate_internal_limit_a": f"{cap:.6f}", "published_stall_endpoint_a": f"{stall:.3f}",
            "stall_is_normal_demand": "NO", "one_way_planning_length_mm": source["one_way_planning_length_mm"],
            "round_trip_planning_length_mm": source["round_trip_planning_length_mm"],
            "power_pair_test_coupon_candidate": "DYNAMIC: igus CF130.03.02.UL to Molex 430250200/430300001; FIXED PIGTAIL: Alpha Wire 3051 to Molex 430200200/430310001 and JST EH; CF9.UL.02.02 REJECTED FOR ACTUATOR POWER",
            "candidate_conductor_mm2": "STATIC AWG22 / published 7x30 construction; DYNAMIC 0.34 mm2 nominal with written-disposition hold",
            "manufacturer_max_conductor_resistance_20c_ohm_per_km": "79.000",
            "calculation_material": "REJECTED CF9.UL.02.02 PREDECESSOR COMPARISON ONLY - NOT A POWER-CABLE SELECTION",
            "jst_eh_published_conductor_range": "AWG30-22; maximum 0.33 mm2 for SEH-001T-P0.6",
            "wire_contact_geometric_compatibility": "ALPHA 3051 TO JST/MICRO-FIT SIZE TABLES PASS AT PUBLISHED AWG22 / 1.575 MM OD; CF130 TO MICRO-FIT AWG22 PASS BUT 1.85 MM CORE-OD LIMIT REMAINS UNVERIFIED",
            "connector_current_evidence": "JST SERIES HEADLINE 3 A IS AT AWG22; STATIC CANDIDATE MATCHES SIZE CONDITION BUT APPLICATION/CRIMP/TEMPERATURE VALIDATION REMAINS OPEN",
            "loop_resistance_20c_planning_ohm": f"{loop_resistance_20c:.6f}",
            "voltage_drop_20c_at_candidate_cap_v": f"{drop_20c:.6f}",
            "conductor_loss_20c_at_candidate_cap_w": f"{loss_20c:.6f}",
            "calculation_boundary": "REJECTED CF9 PREDECESSOR MAX-DCR COMPARISON AT 20 C; NOT A CANDIDATE-WIRE DROP, AMPACITY, THERMAL OR REGENERATION RATING",
            "current_capacity_disposition": "OPEN - STATIC ALPHA 3051 AND DYNAMIC CF130 REQUIRE SEPARATE AMPACITY, DERATING, CRIMP AND CONNECTOR TEMPERATURE-RISE TESTS",
            "dynamic_route_disposition": "CF130 STOPS AT FIXED-SIDE MICRO-FIT TRANSITION; NO DIRECT CF130-TO-JST CRIMP; CORE OD, CRIMP, BEND/TORSION DISTRIBUTION AND CYCLE LIFE REQUIRE TEST",
            "branch_protection": "SELECTION REQUIRED", "cut_length_and_service_slack": "SELECTION REQUIRED",
            "selection_state": "25 FIXED-SIDE MICRO-FIT TRANSITIONS AND RESTRAINED ALPHA-3051-TO-JST PIGTAILS DEFINED AS TEST-COUPON CANDIDATES; NOT RELEASED",
        }))
    return rows


def transition_rows(axis: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for source in axis:
        axis_id = str(source["axis_id"])
        rows.append(common({
            "transition_id": f"TR-{axis_id}", "axis_id": axis_id, "quantity": 1,
            "location_basis": f"FIXED SIDE OF LOOP-{axis_id}-PWR; EXACT XYZ/BRACKET SELECTION REQUIRED",
            "dynamic_cable": "igus CF130.03.02.UL 2 x 22 AWG / 0.34 mm2",
            "dynamic_housing": "Molex 430250200", "dynamic_terminal": "Molex 430300001; 2 required",
            "fixed_panel_housing": "Molex 430200200", "fixed_terminal": "Molex 430310001; 2 required",
            "fixed_pigtail": "2 x Alpha Wire 3051 22 AWG; red/black or accepted keyed color code",
            "actuator_end": "JST EHR-3 or EHR-4 with SEH-001T-P0.6 power contacts by actuator protocol",
            "polarity": "CONTACT 1 RETURN; CONTACT 2 VDD; 100% KEYING/POLARITY/CONTINUITY TEST REQUIRED",
            "load_isolation": "PANEL-MOUNT TRANSITION PLUS PIGTAIL CLAMP MUST ISOLATE JST EH FROM JOINT FLEX AND CONNECTOR MASS",
            "pigtail_length_mm": "SELECTION REQUIRED FROM MODULE CAD; NO PRODUCTION CUT LENGTH RELEASED",
            "candidate_state": "COHERENT INLINE-TRANSITION CANDIDATE; RECEIVED FIT, CRIMP, BRACKET, DERATING AND DYNAMIC TESTS OPEN",
        }))
    return rows


def data_candidates() -> list[dict[str, object]]:
    data = [
        ("ACK-D01", "RS-485 differential pair", "igus CFBUS.PVC.001", "shielded 2 x 0.25 mm2 PROFIBUS cable; characteristic impedance approximately 150 ohm", "TEST-COUPON CANDIDATE", "150 ohm cable is not assumed equivalent to the final RS-485 termination; waveform, termination, common-mode and EMC validation required"),
        ("ACK-D02", "torsional RS-485 route alternative", "igus CFROBOT3.02.03.02", "3 twisted pairs x 24 AWG / 0.25 mm2; overall shield; robot torsion cable", "HOLD", "cited manufacturer page does not publish pair impedance or ROBOTIS RS-485 suitability"),
        ("ACK-D03", "RS-485 differential pair", "Alpha Wire 86202", "2 x 24 AWG twisted continuous-flex; nominal characteristic impedance 87 ohm", "REJECT FOR RS-485 CANDIDATE", "87 ohm nominal impedance is materially separated from the provisional bus termination; no topology-specific validation exists"),
        ("ACK-D04", "TTL data conductor candidate", "igus CF240.01.03", "3 x 26 AWG / 0.14 mm2; overall shield", "TEST-COUPON CANDIDATE", "TTL reference path, ground offset, waveform, bend, connector and EMC tests required"),
        ("ACK-D05", "fixed-zone actuator power alternative", "Alpha Wire AZ221934", "22 AWG ETFE hook-up wire; 600 V; -55 to 150 C", "REJECT FOR MOVING JOINTS", "manufacturer classifies it as hook-up wire and does not claim continuous-flex or torsional robot service"),
        ("ACK-D06", "inter-actuator X4P links", "standard ROBOTIS X4P cable", "contains GND, VDD, DATA+, DATA-", "REJECT", "would parallel separately protected actuator power branches"),
        ("ACK-D07", "inter-actuator X3P links", "standard ROBOTIS X3P cable", "contains GND, VDD, DATA", "REJECT", "would parallel separately protected actuator power branches"),
    ]
    return [common({"candidate_id": i, "service": service, "candidate": candidate, "published_construction": construction, "disposition": disposition, "remaining_evidence": evidence, "selected": "NO"}) for i, service, candidate, construction, disposition, evidence in data]


def cavity_rows() -> list[dict[str, object]]:
    links = read_csv(PHYSICAL / "bus-physical-link-register.csv")
    if len(links) != 25:
        raise RuntimeError("25 physical bus links required")
    rows: list[dict[str, object]] = []
    for link in links:
        rs485 = link["protocol"].startswith("RS-485")
        pins = ((1, "GND", "INDIVIDUAL BRANCH RETURN", "POPULATED"), (2, "VDD", "INDIVIDUAL PROTECTED BRANCH POSITIVE", "POPULATED"), (3, "DATA+" if rs485 else "DATA", "SERIAL DATA", "POPULATED"))
        if rs485:
            pins += ((4, "DATA-", "SERIAL DATA", "POPULATED"),)
        for pin, signal, role, state in pins:
            rows.append(common({"cavity_id": f"IN-{link['axis_id']}-{pin}", "connector_id": link["to_endpoint"], "connector_role": "ACTUATOR INPUT", "axis_id": link["axis_id"], "bus_id": link["bus_id"], "pin": pin, "signal": signal, "physical_role": role, "required_population": state, "actual_population": "NOT INSPECTED", "continuity_target": "INDIVIDUAL PBR" if pin in (1, 2) else link["bus_id"], "no_backfeed_requirement": "VERIFY ISOLATED FROM ADJACENT POWER BRANCHES" if pin in (1, 2) else "N/A"}))
        if link["next_endpoint"].startswith("J-OUT-"):
            outgoing = ((1, "GND", "MUST REMAIN EMPTY", "EMPTY"), (2, "VDD", "MUST REMAIN EMPTY", "EMPTY"), (3, "DATA+" if rs485 else "DATA", "SERIAL DATA", "POPULATED"))
            if rs485:
                outgoing += ((4, "DATA-", "SERIAL DATA", "POPULATED"),)
            for pin, signal, role, state in outgoing:
                rows.append(common({"cavity_id": f"OUT-{link['axis_id']}-{pin}", "connector_id": link["next_endpoint"], "connector_role": "DATA-ONLY OUTGOING", "axis_id": link["axis_id"], "bus_id": link["bus_id"], "pin": pin, "signal": signal, "physical_role": role, "required_population": state, "actual_population": "NOT INSPECTED", "continuity_target": "OPEN CIRCUIT" if state == "EMPTY" else link["bus_id"], "no_backfeed_requirement": "NO CONTINUITY TO GND/VDD OR ANY ADJACENT ACTUATOR BRANCH" if state == "EMPTY" else "N/A"}))
    return rows


def inspection_rows() -> list[dict[str, object]]:
    data = [
        ("ACK-T01", "verify received EHR-3/EHR-4 and SEH-001T-P0.6 identity and lot", "100% visual/label/CoC", "exact candidate family and traceable lot"),
        ("ACK-T02", "approve conductor/contact compatibility before crimping production harness", "supplier application review", "written approval or revised compatible wire/contact selection"),
        ("ACK-T03", "prepare representative crimp coupons with controlled tooling", "tool/height/cross-section record", "SELECTION REQUIRED"),
        ("ACK-T04", "perform crimp pull tests by wire lot and setup", "N and failure mode", "SELECTION REQUIRED BY ACCEPTED STANDARD/REVIEWER"),
        ("ACK-T05", "inspect all 94 actuator-input cavities", "100% visual and pin gauge", "correct position, latch and polarity"),
        ("ACK-T06", "inspect all 65 outgoing data-only cavities", "100% visual and pin gauge", "GND/VDD empty; data contacts populated as specified"),
        ("ACK-T07", "continuity test every populated contact end-to-end", "ohm", "SELECTION REQUIRED; recorded by serialized assembly"),
        ("ACK-T08", "verify every outgoing GND/VDD cavity is open to every power branch", "ohm/insulation", "SELECTION REQUIRED; no measurable backfeed path"),
        ("ACK-T09", "measure branch voltage drop and connector temperature rise at accepted current waveform", "V/degC/time", "SELECTION REQUIRED"),
        ("ACK-T10", "cycle every service loop through joint travel without power", "cycles/visual", "SELECTION REQUIRED; no snag, twist, latch damage or bend violation"),
        ("ACK-T11", "validate RS-485 and TTL waveforms at the final cable lengths/topology", "scope/error count", "SELECTION REQUIRED"),
        ("ACK-T12", "fault-inject adjacent-branch short/backfeed conditions on protected fixture", "A/V/clearing time", "SELECTION REQUIRED; protection and isolation response accepted"),
        ("ACK-T13", "inspect and pull-test every fixed-side Micro-Fit panel transition and restrained pigtail", "100% visual/pull/polarity", "SELECTION REQUIRED; no panel motion, latch release, wire load transfer or polarity error"),
        ("ACK-T14", "cycle CF130 moving cable while instrumenting the fixed transition and JST pigtail", "cycles/temperature/resistance/visual", "SELECTION REQUIRED; transition remains fixed and EH pigtail sees no cyclic bending"),
    ]
    return [common({"test_id": i, "inspection_or_test": test, "method_or_unit": method, "acceptance_limit": limit, "measured_value": "NONE", "result": "NOT EXECUTED", "evidence": "NONE"}) for i, test, method, limit in data]


def hold_rows() -> list[dict[str, object]]:
    data = [
        ("ACK-H01", "Alpha Wire 3051 is a static suspended-commissioning candidate only; received construction, crimp quality, current/temperature behavior and external restraint remain unverified", "received-lot measurement plus crimp/pull/resistance/temperature coupons and a dimensioned non-moving restraint plan"),
        ("ACK-H02", "normal RMS, peak duration, diversity and regeneration waveforms are unmeasured", "accepted whole-body trajectories with synchronized current/voltage/temperature records"),
        ("ACK-H03", "branch fuse/eFuse/current-limiter coordination is unselected", "fault current, impedance, inrush, regeneration, interruption and connector-protection tests"),
        ("ACK-H04", "CF130.03.02.UL is the dynamic candidate, but individual-core OD and 0.34 versus 0.33 mm2 contact boundary plus every HR-30 route remain unresolved", "written igus/JST application disposition, received measurements and route-specific bend/twist/temperature/life testing"),
        ("ACK-H05", "no RS-485 or TTL data cable is validated in the final eight-bus topology", "manufacturer suitability evidence plus waveform, termination, common-mode, error-rate and EMC tests at final lengths"),
        ("ACK-H06", "cut lengths, service slack, clamp positions and retention hardware are unselected", "as-built route measurement and dimensioned assembly drawings"),
        ("ACK-H07", "contact crimp tooling, setup, pull limit and cross-section acceptance are unselected", "controlled process specification, coupons and qualified inspection"),
        ("ACK-H08", "data-only outgoing cavity construction is unbuilt and uninspected", "serialized 100% cavity, continuity, isolation and no-backfeed records"),
        ("ACK-H09", "whole-body bus termination, bias, baud and shielding remain unvalidated", "final controller, cable and topology tests across motion/power states"),
        ("ACK-H10", "qualified electrical and functional-safety review is absent", "signed review of the identical frozen as-built harness and test evidence"),
        ("ACK-H11", "outgoing data-only connectors omit GND as well as VDD, leaving signal reference through individual branch returns", "approved reference/isolation architecture and measured RS-485 common-mode plus TTL ground-offset/waveform evidence without power-branch paralleling"),
        ("ACK-H12", "CF130 individual-core insulation diameter is unpublished against the Micro-Fit terminal's 1.85 mm maximum", "igus construction drawing or written confirmation plus received-lot core-OD measurements before any crimp trial"),
        ("ACK-H13", "dimensioned bracket CAD and 25 nominal module placements exist, but the official connector cutout, received fit, material, fasteners, clamp force, pigtail length and production-body tolerance sweep remain unverified", "revision-controlled Micro-Fit cutout review, received-part fit coupon, DFM/material/fastener release, cable-clamp tests, selected pigtail lengths and joined production-CAD collision/service review"),
        ("ACK-H14", "Micro-Fit current/temperature capability is not released for the HR-30 two-circuit 22 AWG duty", "measured RMS/peak/regeneration waveform, ambient/bundling model and connector temperature-rise/fault tests using exact received terminals and tooling"),
    ]
    return [common({"hold_id": i, "unresolved_item": item, "closure_evidence": evidence, "state": "OPEN"}) for i, item, evidence in data]


def _legacy_drawing() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="980" viewBox="0 0 1600 980" role="img" aria-labelledby="title desc"><title id="title">HR-30 actuator cable-kit architecture</title><desc id="desc">Each actuator receives an individual protected power pair and serial data. Outgoing inter-actuator connectors omit ground and voltage contacts.</desc><style>text{{font:600 18px system-ui;fill:#102b46}}.h{{font-size:34px;font-weight:900}}.s{{font-size:16px}}.box{{fill:#fff;stroke:#0b4f91;stroke-width:4}}.data{{stroke:#28a9df;stroke-width:8;fill:none}}.power{{stroke:#f2b91d;stroke-width:9;fill:none}}.empty{{fill:#fff;stroke:#982520;stroke-width:5}}.pin{{fill:#d9f2ff;stroke:#0b4f91;stroke-width:3}}.warn{{fill:#fff0b5;stroke:#982520;stroke-width:4}}</style><rect width="1600" height="980" fill="#eef8ff"/><text class="h" x="50" y="60">HR-30 split actuator harness candidate</text><rect class="box" x="55" y="180" width="330" height="270" rx="20"/><text x="90" y="225">25-channel protected PDU</text><text class="s" x="90" y="270">one positive + return pair per axis</text><text class="s" x="90" y="310">candidate internal cap ≤ 2.499 A</text><text class="s" x="90" y="350">branch protection: selection required</text><rect class="box" x="620" y="130" width="390" height="380" rx="20"/><text x="655" y="175">Actuator input EHR-4 / EHR-3</text><circle class="pin" cx="690" cy="235" r="24"/><text x="680" y="242">1</text><text class="s" x="735" y="242">GND — individual return</text><circle class="pin" cx="690" cy="300" r="24"/><text x="680" y="307">2</text><text class="s" x="735" y="307">VDD — individual protected feed</text><circle class="pin" cx="690" cy="365" r="24"/><text x="680" y="372">3</text><text class="s" x="735" y="372">DATA / DATA+</text><circle class="pin" cx="690" cy="430" r="24"/><text x="680" y="437">4</text><text class="s" x="735" y="437">DATA− on RS-485 only</text><path class="power" d="M385 270 C500 270 520 235 620 235"/><path class="power" d="M385 340 C500 340 520 300 620 300"/><rect class="box" x="1160" y="130" width="370" height="380" rx="20"/><text x="1195" y="175">Outgoing data-only housing</text><circle class="empty" cx="1230" cy="235" r="24"/><text x="1220" y="242">1</text><text class="s" x="1275" y="242">EMPTY — no GND pass-through</text><circle class="empty" cx="1230" cy="300" r="24"/><text x="1220" y="307">2</text><text class="s" x="1275" y="307">EMPTY — no VDD pass-through</text><circle class="pin" cx="1230" cy="365" r="24"/><text x="1220" y="372">3</text><text class="s" x="1275" y="372">DATA / DATA+</text><circle class="pin" cx="1230" cy="430" r="24"/><text x="1220" y="437">4</text><text class="s" x="1275" y="437">DATA− on RS-485 only</text><path class="data" d="M1010 365 L1160 365"/><path class="data" d="M1010 430 L1160 430"/><rect class="warn" x="110" y="610" width="1380" height="230" rx="20"/><text class="h" x="155" y="665">Unresolved physical interface</text><text x="155" y="720">CF130.03.02.UL is a test-coupon candidate only: 0.34 mm² nominal exceeds JST's 0.33 mm² maximum.</text><text x="155" y="765">CF240.01.03 is shielded and flexible, but RS-485 twist/impedance suitability is not established.</text><text x="155" y="810">No cable is approved to crimp, connect or energize.</text><text class="s" x="50" y="940">{html.escape(WARNING)}</text></svg>'''


def _legacy_render(axis: list[dict[str, object]], cavities: list[dict[str, object]]) -> str:
    axis_table = "".join(f"<tr><td>{html.escape(str(r['axis_id']))}</td><td>{html.escape(str(r['bus_id']))}</td><td>{r['candidate_internal_limit_a']} A</td><td>{r['published_stall_endpoint_a']} A</td><td>{r['round_trip_planning_length_mm']} mm</td><td>{html.escape(str(r['wire_contact_geometric_compatibility']))}</td></tr>" for r in axis)
    empty_count = sum(r["required_population"] == "EMPTY" for r in cavities)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 actuator cable kit</title><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#d9f2ff;--gold:#f2b91d;--paper:#f7fbff;--ink:#142a40;--line:#82c4e6;--red:#982520}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1280px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white}}h1{{font-size:clamp(38px,6vw,70px);line-height:1.04;max-width:18ch}}h2{{font-size:clamp(28px,4vw,44px)}}h3{{font-size:22px}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px}}article,.panel{{background:white;border:2px solid var(--line);border-radius:16px;padding:19px}}.metric{{font-size:clamp(34px,5vw,54px);font-weight:900;color:var(--blue)}}.hold{{border-color:var(--red)}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:14px;background:white}}table{{border-collapse:collapse;width:100%;min-width:1180px}}th,td{{padding:14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--deep);color:white;position:sticky;top:0}}img{{max-width:100%;height:auto;border:2px solid var(--line);border-radius:16px}}a{{color:#075b9b;font-weight:800}}small{{font-size:14px}}@media(max-width:560px){{body{{font-size:16px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>HR-30 whole-body P0.1</p><h1>The 25 actuator cables now have explicit pin populations.</h1><p>Every actuator gets an individual protected power pair. Every inter-actuator outgoing housing is data-only, with power cavities intentionally empty.</p></header><main><section class="grid"><article><div class="metric">25 / 25</div><p>axis power pairs bound to current caps and planning lengths</p></article><article><div class="metric">159</div><p>controlled actuator connector-cavity records</p></article><article><div class="metric">{empty_count}</div><p>outgoing GND/VDD cavities required empty</p></article><article class="hold"><div class="metric">0</div><p>released cables, crimp processes, protection devices or powered permissions</p></article></section><section><h2>Physical topology</h2><img src="actuator-cable-kit.svg" alt="Individual actuator power pair and data-only outgoing connector architecture"></section><section><h2>Connector disposition</h2><div class="panel"><p>ROBOTIS uses EHR-03/EHR-04 notation. JST's current canonical housing models are <strong>EHR-3</strong> and <strong>EHR-4</strong>, with standard contact <strong>SEH-001T-P0.6</strong>. Low-insertion-force contacts are rejected for this walking-vibration candidate because JST identifies reduced vibration resistance.</p><p>The order-code family is now explicit, but received mating fit, tooling, crimp quality and retention are still unverified.</p></div></section><section><h2>Power-cable blocker</h2><div class="panel hold"><p><strong>Do not crimp CF130.03.02.UL into this contact yet.</strong> igus publishes 0.34 mm² nominal conductors; JST publishes a 0.33 mm² maximum for the standard EH contact. The 0.01 mm² mismatch requires written supplier approval or a different cable/contact choice plus coupon tests.</p></div></section><section><h2>All 25 axis feeds</h2><div class="scroll"><table><thead><tr><th>Axis</th><th>Bus</th><th>Candidate cap</th><th>Published stall endpoint</th><th>Round-trip planning length</th><th>Wire/contact disposition</th></tr></thead><tbody>{axis_table}</tbody></table></div></section><section><h2>Controlled records</h2><div class="panel"><p><a href="connector-family-disposition.csv">Connector family</a> · <a href="axis-power-cable-candidate.csv">25 axis candidates</a> · <a href="connector-cavity-population.csv">159 cavity records</a> · <a href="data-cable-candidate.csv">Data candidates</a> · <a href="inspection-test-plan.csv">Inspection/test plan</a> · <a href="open-holds.csv">Open holds</a> · <a href="primary-source-register.csv">Primary sources</a></p><small>All measured values remain NONE and every execution state remains NOT EXECUTED.</small></div></section></main><footer>{html.escape(WARNING)}</footer></body></html>'''


def drawing() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="980" viewBox="0 0 1600 980" role="img" aria-labelledby="title desc"><title id="title">HR-30 actuator cable-kit architecture</title><desc id="desc">Each actuator receives an individual protected power pair and serial data. Outgoing inter-actuator connectors omit ground and voltage contacts.</desc><style>text{{font:600 18px system-ui;fill:#102b46}}.h{{font-size:34px;font-weight:900}}.s{{font-size:16px}}.box{{fill:#fff;stroke:#0b4f91;stroke-width:4}}.data{{stroke:#28a9df;stroke-width:8;fill:none}}.power{{stroke:#f2b91d;stroke-width:9;fill:none}}.empty{{fill:#fff;stroke:#982520;stroke-width:5}}.pin{{fill:#d9f2ff;stroke:#0b4f91;stroke-width:3}}.warn{{fill:#fff0b5;stroke:#982520;stroke-width:4}}</style><rect width="1600" height="980" fill="#eef8ff"/><text class="h" x="50" y="60">HR-30 split actuator harness candidate</text><rect class="box" x="55" y="180" width="330" height="270" rx="20"/><text x="90" y="225">25-channel protected PDU</text><text class="s" x="90" y="270">one positive + return pair per axis</text><text class="s" x="90" y="310">candidate internal cap &lt;= 2.499 A</text><text class="s" x="90" y="350">branch protection: selection required</text><rect class="box" x="620" y="130" width="390" height="380" rx="20"/><text x="655" y="175">Actuator input EHR-4 / EHR-3</text><circle class="pin" cx="690" cy="235" r="24"/><text x="680" y="242">1</text><text class="s" x="735" y="242">GND - individual return</text><circle class="pin" cx="690" cy="300" r="24"/><text x="680" y="307">2</text><text class="s" x="735" y="307">VDD - individual protected feed</text><circle class="pin" cx="690" cy="365" r="24"/><text x="680" y="372">3</text><text class="s" x="735" y="372">DATA / DATA+</text><circle class="pin" cx="690" cy="430" r="24"/><text x="680" y="437">4</text><text class="s" x="735" y="437">DATA- on RS-485 only</text><path class="power" d="M385 270 C500 270 520 235 620 235"/><path class="power" d="M385 340 C500 340 520 300 620 300"/><rect class="box" x="1160" y="130" width="370" height="380" rx="20"/><text x="1195" y="175">Outgoing data-only housing</text><circle class="empty" cx="1230" cy="235" r="24"/><text x="1220" y="242">1</text><text class="s" x="1275" y="242">EMPTY - no GND pass-through</text><circle class="empty" cx="1230" cy="300" r="24"/><text x="1220" y="307">2</text><text class="s" x="1275" y="307">EMPTY - no VDD pass-through</text><circle class="pin" cx="1230" cy="365" r="24"/><text x="1220" y="372">3</text><text class="s" x="1275" y="372">DATA / DATA+</text><circle class="pin" cx="1230" cy="430" r="24"/><text x="1220" y="437">4</text><text class="s" x="1275" y="437">DATA- on RS-485 only</text><path class="data" d="M1010 365 L1160 365"/><path class="data" d="M1010 430 L1160 430"/><rect class="warn" x="110" y="610" width="1380" height="230" rx="20"/><text class="h" x="155" y="665">Candidate advanced; release gates remain open</text><text x="155" y="720">CF9.UL.02.02 at 0.25 mm2 fits JST's published 0.032-0.33 mm2 contact range.</text><text x="155" y="765">The 3 A JST headline applies at AWG22, not this AWG24 candidate. Hot/bundled ampacity remains unproven.</text><text x="155" y="810">No cable is approved to crimp, connect or energize.</text><text class="s" x="50" y="940">{html.escape(WARNING)}</text></svg>'''


def render(axis: list[dict[str, object]], cavities: list[dict[str, object]]) -> str:
    axis_table = "".join(
        f"<tr><td>{html.escape(str(r['axis_id']))}</td><td>{html.escape(str(r['bus_id']))}</td>"
        f"<td>{r['candidate_internal_limit_a']} A</td><td>{r['round_trip_planning_length_mm']} mm</td>"
        f"<td>{r['loop_resistance_20c_planning_ohm']} ohm</td><td>{r['voltage_drop_20c_at_candidate_cap_v']} V</td>"
        f"<td>{r['conductor_loss_20c_at_candidate_cap_w']} W</td><td>{html.escape(str(r['current_capacity_disposition']))}</td></tr>"
        for r in axis
    )
    max_drop = max(float(r["voltage_drop_20c_at_candidate_cap_v"]) for r in axis)
    max_loss = max(float(r["conductor_loss_20c_at_candidate_cap_w"]) for r in axis)
    empty_count = sum(r["required_population"] == "EMPTY" for r in cavities)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 actuator cable kit</title><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#d9f2ff;--gold:#f2b91d;--paper:#f7fbff;--ink:#142a40;--line:#82c4e6;--red:#982520}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1280px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white}}h1{{font-size:clamp(38px,6vw,70px);line-height:1.04;max-width:18ch}}h2{{font-size:clamp(28px,4vw,44px)}}h3{{font-size:22px}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px}}article,.panel{{background:white;border:2px solid var(--line);border-radius:16px;padding:19px}}.metric{{font-size:clamp(34px,5vw,54px);font-weight:900;color:var(--blue)}}.hold{{border-color:var(--red)}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:14px;background:white}}table{{border-collapse:collapse;width:100%;min-width:1480px}}th,td{{padding:14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--deep);color:white;position:sticky;top:0}}img{{max-width:100%;height:auto;border:2px solid var(--line);border-radius:16px}}a{{color:#075b9b;font-weight:800}}small{{font-size:14px}}@media(max-width:560px){{body{{font-size:16px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>HR-30 whole-body P0.1</p><h1>The 25 actuator feeds now have a compatible-size flex-cable candidate.</h1><p>CF9.UL.02.02 fits the contact's published conductor range. Per-axis 20 C resistance, voltage-drop and conductor-loss planning values are calculated from the manufacturer's maximum DCR.</p></header><main><section class="grid"><article><div class="metric">25 / 25</div><p>axis power pairs have a geometric wire/contact candidate</p></article><article><div class="metric">{max_drop:.3f} V</div><p>largest calculated 20 C drop at a candidate current cap</p></article><article><div class="metric">{max_loss:.3f} W</div><p>largest calculated 20 C pair loss at that cap</p></article><article class="hold"><div class="metric">0</div><p>released cables, crimp processes, protection devices or powered permissions</p></article></section><section><h2>Physical topology</h2><img src="actuator-cable-kit.svg" alt="Individual actuator power pair and data-only outgoing connector architecture"></section><section><h2>What advanced</h2><div class="panel"><p><strong>igus CF9.UL.02.02</strong> is a 2 x 0.25 mm2 / 24 AWG continuous-flex candidate. Its conductor size is inside JST's published 0.032-0.33 mm2 range for SEH-001T-P0.6. igus publishes a maximum 20 C conductor resistance of 79 ohm/km, which now drives every planning value below.</p></div></section><section><h2>What remains blocked</h2><div class="panel hold"><p><strong>Do not crimp or connect this candidate yet.</strong> JST's 3 A series headline is specified at AWG22, not this AWG24 candidate. Actual RMS duty, ambient, bundling, connector temperature rise, branch protection, crimp quality and route-specific flex life remain unverified. The calculations are 20 C planning values, not ampacity or thermal release.</p></div></section><section><h2>All 25 axis feeds</h2><div class="scroll"><table><thead><tr><th>Axis</th><th>Bus</th><th>Candidate cap</th><th>Round-trip length</th><th>20 C loop R</th><th>20 C drop</th><th>20 C pair loss</th><th>Release boundary</th></tr></thead><tbody>{axis_table}</tbody></table></div></section><section><h2>Data-cable disposition</h2><div class="panel"><p>CFBUS.PVC.001 is now an RS-485 test-coupon candidate, not a selection: its published approximately 150 ohm characteristic impedance must be reconciled with the final topology and termination. CFROBOT3 remains a torsional-route hold because pair impedance is unpublished. Alpha Wire 86202 is rejected as the RS-485 candidate at its published 87 ohm nominal impedance. Standard powered ROBOTIS daisy cables remain rejected because they would parallel the separately protected branches.</p></div></section><section><h2>Controlled records</h2><div class="panel"><p><a href="connector-family-disposition.csv">Connector family</a> | <a href="axis-power-cable-candidate.csv">25 calculated axis candidates</a> | <a href="connector-cavity-population.csv">159 cavity records</a> | <a href="data-cable-candidate.csv">Data candidates</a> | <a href="inspection-test-plan.csv">Inspection/test plan</a> | <a href="open-holds.csv">Open holds</a> | <a href="primary-source-register.csv">Primary sources</a></p><small>{empty_count} outgoing power/reference cavities remain controlled EMPTY. All physical measured values remain NONE and every execution state remains NOT EXECUTED.</small></div></section></main><footer>{html.escape(WARNING)}</footer></body></html>'''


def drawing() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900" role="img" aria-labelledby="title desc"><title id="title">HR-30 fixed-side actuator power transition</title><desc id="desc">Each protected branch uses moving CF130 cable, a fixed panel-mounted Micro-Fit transition, a restrained Alpha 3051 pigtail and a JST EH actuator connector.</desc><style>text{{font:600 18px system-ui;fill:#102b46}}.h{{font-size:34px;font-weight:900}}.s{{font-size:16px}}.box{{fill:#fff;stroke:#0b4f91;stroke-width:4}}.power{{stroke:#f2b91d;stroke-width:10;fill:none}}.fixed{{stroke:#982520;stroke-width:4;stroke-dasharray:12 8}}.warn{{fill:#fff0b5;stroke:#982520;stroke-width:4}}</style><rect width="1600" height="900" fill="#eef8ff"/><text class="h" x="55" y="65">One of 25 actuator-power branches</text><rect class="box" x="55" y="190" width="260" height="190" rx="20"/><text x="88" y="235">Protected output</text><text class="s" x="88" y="280">individual VDD + return</text><text class="s" x="88" y="320">cap &lt;= 2.499 A candidate</text><path class="power" d="M315 285 H520"/><text x="350" y="255">CF130 moving pair</text><rect class="box" x="520" y="150" width="420" height="270" rx="20"/><text x="555" y="200">Fixed panel transition</text><text class="s" x="555" y="245">430250200 + 2 x 430300001</text><text class="s" x="555" y="285">mates with</text><text class="s" x="555" y="325">430200200 + 2 x 430310001</text><path class="fixed" d="M500 430 H960"/><text class="s" x="575" y="465">dimensioned bracket candidate / 25 nominal placements</text><path class="power" d="M940 285 H1135"/><text x="965" y="255">Alpha 3051 pigtail</text><rect class="box" x="1135" y="190" width="400" height="190" rx="20"/><text x="1170" y="235">JST EH actuator input</text><text class="s" x="1170" y="280">pin 1 return / pin 2 VDD</text><text class="s" x="1170" y="320">pigtail clamped; no joint flex</text><rect class="warn" x="110" y="570" width="1380" height="190" rx="20"/><text class="h" x="155" y="625">Candidate architecture, not a released cable</text><text x="155" y="675">Official cutout, received fit, clamp force, crimp, derating and thermal proof remain open.</text><text x="155" y="715">No procurement, fabrication, connection, powered testing, motion or energization authority.</text><text class="s" x="55" y="850">{html.escape(WARNING)}</text></svg>'''


def render(axis: list[dict[str, object]], cavities: list[dict[str, object]]) -> str:
    page = _legacy_render(axis, cavities)
    page = page.replace("min-width:1180px", "min-width:1480px")
    page = page.replace("The 25 actuator cables now have explicit pin populations.", "The 25 actuator feeds now separate static and dynamic 22 AWG candidates.")
    page = page.replace("Every actuator gets an individual protected power pair. Every inter-actuator outgoing housing is data-only, with power cavities intentionally empty.", "Alpha Wire 3051 is the static suspended-commissioning coupon candidate. CF130.03.02.UL is the dynamic coupon candidate. CF9 is rejected for actuator power, and outgoing bus links remain data-only.")
    page = page.replace("axis power pairs bound to current caps and planning lengths", "axis power pairs have static/dynamic 22 AWG coupon candidates")
    page = page.replace("<strong>Do not crimp CF130.03.02.UL into this contact yet.</strong>", "<strong>Do not crimp or connect either candidate yet.</strong>")
    page = page.replace("The 25 actuator feeds now separate static and dynamic 22 AWG candidates.", "All 25 actuator feeds now use a fixed-side transition candidate.")
    page = page.replace("Alpha Wire 3051 is the static suspended-commissioning coupon candidate. CF130.03.02.UL is the dynamic coupon candidate. CF9 is rejected for actuator power, and outgoing bus links remain data-only.", "CF130 is the moving-cable candidate to a panel-mounted Molex Micro-Fit 3.0 pair; a restrained Alpha Wire 3051 pigtail continues to JST EH. Direct CF130-to-JST crimping is rejected.")
    page = page.replace("axis power pairs have static/dynamic 22 AWG coupon candidates", "axis power pairs have fixed-transition plus restrained-pigtail candidates")
    transition_section = '''<section><h2>Fixed-side transition for every joint</h2><div class="grid"><article><h3>Moving side</h3><p><strong>igus CF130.03.02.UL</strong> terminates in Molex <strong>430250200</strong> with two <strong>430300001</strong> female terminals.</p></article><article><h3>Fixed panel side</h3><p>Molex <strong>430200200</strong> with two <strong>430310001</strong> male terminals mounts in the dimensioned bracket candidate. All 25 nominal placements are bound to the whole-body CAD.</p></article><article><h3>Actuator pigtail</h3><p>Two restrained <strong>Alpha Wire 3051</strong> conductors continue to the JST EH power cavities. The pigtail must not flex with the joint.</p></article></div><div class="panel hold"><p>The bracket and connector families are candidates, not released parts. Official cutout geometry, received fit, production material/fasteners, clamp force, pigtail lengths, tolerance-aware integration, crimp tooling, pull strength, temperature rise and cycle testing remain open.</p><p><a href="../actuator-transition-brackets-p0.1/index.html">Open the 25-placement transition-bracket guide</a>.</p></div></section>'''
    page = page.replace("<section><h2>All 25 axis feeds</h2>", transition_section + "<section><h2>All 25 axis feeds</h2>")
    page = page.replace('<a href="connector-family-disposition.csv">Connector family</a> |', '<a href="connector-family-disposition.csv">Connector family</a> | <a href="actuator-power-transition-register.csv">25 fixed transitions</a> |')
    return page


def integrate_root(axis: list[dict[str, object]], cavities: list[dict[str, object]]) -> None:
    max_drop = max(float(r["voltage_drop_20c_at_candidate_cap_v"]) for r in axis)
    status_path = WHOLE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "actuator_cable_kit_present": True,
        "actuator_cable_kit_axis_count": len(axis),
        "actuator_cable_kit_cavity_record_count": len(cavities),
        "actuator_cable_kit_required_empty_cavity_count": sum(r["required_population"] == "EMPTY" for r in cavities),
        "actuator_cable_kit_current_caps_propagated": True,
        "actuator_connector_candidate_order_codes_bound": True,
        "actuator_power_cable_geometric_candidate_bound": True,
        "actuator_power_fixed_transition_candidate_bound": True,
        "actuator_power_direct_cf130_to_jst_rejected": True,
        "actuator_power_transition_brackets_dimensioned": True,
        "actuator_power_transition_bracket_placement_count": 25,
        "actuator_power_cf130_core_od_verified": False,
        "actuator_power_cable_20c_planning_calculated": True,
        "actuator_power_cable_hot_ampacity_verified": False,
        "actuator_power_cable_selected": False,
        "actuator_data_cable_selected": False,
        "actuator_crimp_process_selected": False,
        "actuator_cable_kit_built": False,
        "procurement_authority": False, "fabrication_authority": False, "connection_authority": False,
        "powered_test_authority": False, "motion_authority": False, "energization_authority": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    readme = WHOLE / "README.md"
    text = readme.read_text(encoding="utf-8")
    start, end = "<!-- HR30-ACTUATOR-CABLE-KIT-P01-README-START -->", "<!-- HR30-ACTUATOR-CABLE-KIT-P01-README-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    block = f'''{start}\n## Actuator cable kit\n\nThe [interactive actuator cable-kit guide](harness/actuator-cable-kit-p0.1/index.html) assigns all **25 axis feeds** their accepted candidate current caps and planning lengths, binds JST **EHR-3/EHR-4 + SEH-001T-P0.6** candidate order-code families, and defines **{len(cavities)} connector-cavity records**. Outgoing inter-actuator housings intentionally leave every GND/VDD cavity empty so the 25 separately protected power branches cannot be paralleled. No wire is released: the current CF130 0.34 mm² test-coupon candidate exceeds JST's published 0.33 mm² maximum and stays blocked pending supplier disposition or reselection.\n{end}\n'''
    block = f'''{start}\n## Actuator cable kit\n\nThe [interactive actuator cable-kit guide](harness/actuator-cable-kit-p0.1/index.html) assigns all **25 axis feeds** their candidate current caps and planning lengths, binds JST **EHR-3/EHR-4 + SEH-001T-P0.6** candidate order-code families, and defines **{len(cavities)} connector-cavity records**. The dimensioned transition-bracket candidate and all **25 nominal module placements** are configuration-bound. The retained rejected-CF9 predecessor calculation has a largest 20 C planning drop of **{max_drop:.3f} V**; it is not an ampacity or thermal release. Outgoing inter-actuator housings leave GND/VDD cavities empty so the 25 separately protected power branches cannot be paralleled; signal-reference behavior and every physical validation gate remain open.\n{end}\n'''
    marker = "<!-- HR30-FIRST-ENERGIZATION-P01-README-START -->"
    if marker in text:
        text = text.replace(marker, block + marker)
    else:
        text = text.rstrip() + "\n\n" + block
    readme.write_text(text, encoding="utf-8", newline="\n")

    page = WHOLE / "index.html"
    text = page.read_text(encoding="utf-8")
    start, end = "<!-- HR30-ACTUATOR-CABLE-KIT-P01-START -->", "<!-- HR30-ACTUATOR-CABLE-KIT-P01-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    section = f'''{start}<section id="actuator-cable-kit"><h2>The actuator pin population is explicit</h2><div class="grid"><article class="card pass"><div class="metric">25 / 25</div><p>axis feeds carry their deterministic candidate current caps and routed planning lengths.</p></article><article class="card"><div class="metric">{len(cavities)}</div><p>controlled actuator connector-cavity records.</p></article><article class="card"><div class="metric">34</div><p>outgoing GND/VDD cavities required to remain empty across 17 data-only links.</p></article><article class="card hold"><h3>Wire remains unselected</h3><p>CF130's 0.34 mm² nominal conductor exceeds JST's 0.33 mm² maximum; supplier disposition or reselection is required.</p></article></div><p><a href="harness/actuator-cable-kit-p0.1/index.html">Open the interactive actuator cable-kit guide</a>. It defines the candidate architecture but grants no procurement, crimping, connection or powered-work authority.</p></section>{end}'''
    section = f'''{start}<section id="actuator-cable-kit"><h2>The actuator wire candidate now fits the contact range</h2><div class="grid"><article class="card pass"><div class="metric">25 / 25</div><p>axis feeds carry calculated 20 C resistance, drop and loss values.</p></article><article class="card"><div class="metric">{max_drop:.3f} V</div><p>largest planning drop at a candidate current cap.</p></article><article class="card"><div class="metric">34</div><p>outgoing GND/VDD cavities required to remain empty across 17 data-only links.</p></article><article class="card hold"><h3>Thermal release remains open</h3><p>CF9.UL.02.02 fits the JST conductor range, but AWG24 current capacity, hot bundling, crimp temperature rise and route life are not validated.</p></article></div><p><a href="harness/actuator-cable-kit-p0.1/index.html">Open the interactive actuator cable-kit guide</a>. It defines a test-coupon candidate but grants no procurement, crimping, connection or powered-work authority.</p></section>{end}'''
    marker = "<!-- HR30-FIRST-ENERGIZATION-P01-START -->"
    if marker in text:
        text = text.replace(marker, section + marker)
    elif "</main>" in text:
        text = text.replace("</main>", section + "</main>", 1)
    else:
        raise RuntimeError("root page main boundary missing")
    page.write_text(text, encoding="utf-8", newline="\n")


def correct_root_copy() -> None:
    """Remove the superseded CF9 power-selection wording from root artifacts."""
    readme = WHOLE / "README.md"
    text = readme.read_text(encoding="utf-8")
    text = text.replace(
        "The igus **CF9.UL.02.02** 0.25 mm2 continuous-flex test-coupon candidate is inside JST's published conductor-size range; the largest manufacturer-DCR-based 20 C planning drop is **",
        "The power-wire path is split: **Alpha Wire 3051 22 AWG** for static suspended-commissioning coupons and **igus CF130.03.02.UL 2 x 22 AWG** for dynamic coupons. The retained rejected-CF9 predecessor comparison has a largest 20 C planning drop of **",
    )
    text = text.replace("This is not an ampacity or thermal release.", "That comparison is not a cable selection, ampacity or thermal release.")
    text = text.replace("The power-wire path is split: **Alpha Wire 3051 22 AWG** for static suspended-commissioning coupons and **igus CF130.03.02.UL 2 x 22 AWG** for dynamic coupons.", "Each actuator-power path now uses **igus CF130.03.02.UL** only on the moving side, a fixed panel-mounted **Molex 430250200 / 430200200** transition, and a restrained **Alpha Wire 3051** pigtail to JST EH. Direct CF130-to-JST crimping is rejected.")
    readme.write_text(text, encoding="utf-8", newline="\n")

    page = WHOLE / "index.html"
    text = page.read_text(encoding="utf-8")
    text = text.replace("The actuator wire candidate now fits the contact range", "Static and dynamic actuator power-wire candidates are now separated")
    text = text.replace("axis feeds carry calculated 20 C resistance, drop and loss values", "axis feeds carry static/dynamic 22 AWG coupon-candidate bindings")
    text = text.replace("CF9.UL.02.02 fits the JST conductor range, but AWG24 current capacity, hot bundling, crimp temperature rise and route life are not validated.", "Alpha 3051 is static-only; CF130 requires written contact-boundary disposition and dynamic qualification. CF9 receives no actuator-power credit.")
    text = text.replace("It defines a test-coupon candidate but grants no procurement", "It defines separate static/dynamic coupon candidates but grants no procurement")
    text = text.replace("Static and dynamic actuator power-wire candidates are now separated", "All 25 actuator power branches now have a fixed-transition candidate")
    text = text.replace("axis feeds carry static/dynamic 22 AWG coupon-candidate bindings", "axis feeds bind moving cable, fixed transition and restrained pigtail")
    text = text.replace("Alpha 3051 is static-only; CF130 requires written contact-boundary disposition and dynamic qualification. CF9 receives no actuator-power credit.", "CF130 stops at a fixed panel-mounted Micro-Fit pair; Alpha 3051 continues to JST EH under restraint. Core OD, bracket CAD, crimp and thermal qualification remain open.")
    text = text.replace("It defines separate static/dynamic coupon candidates but grants no procurement", "It defines 25 fixed-transition candidates but grants no procurement")
    page.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    sources, connectors = source_rows(), connector_rows()
    axes, data, cavities = axis_rows(), data_candidates(), cavity_rows()
    transitions = transition_rows(axes)
    tests, holds = inspection_rows(), hold_rows()
    write_csv(OUT / "primary-source-register.csv", sources)
    write_csv(OUT / "connector-family-disposition.csv", connectors)
    write_csv(OUT / "axis-power-cable-candidate.csv", axes)
    write_csv(OUT / "actuator-power-transition-register.csv", transitions)
    write_csv(OUT / "data-cable-candidate.csv", data)
    write_csv(OUT / "connector-cavity-population.csv", cavities)
    write_csv(OUT / "inspection-test-plan.csv", tests)
    write_csv(OUT / "open-holds.csv", holds)
    status = {
        "identifier": IDENTIFIER, "warning": WARNING, "source_count": len(sources), "connector_decision_count": len(connectors),
        "axis_count": len(axes), "transition_count": len(transitions), "data_candidate_count": len(data), "cavity_record_count": len(cavities),
        "required_empty_cavity_count": sum(r["required_population"] == "EMPTY" for r in cavities),
        "inspection_test_count": len(tests), "open_hold_count": len(holds), "current_caps_propagated": True,
        "canonical_jst_order_code_family_bound": True,
        "cf9_jst_cross_section_geometry_compatible": True,
        "cf9_power_candidate_rejected": True,
        "static_alpha_3051_coupon_candidate_defined": True,
        "dynamic_cf130_coupon_candidate_defined": True,
        "direct_cf130_to_jst_eh_crimp_rejected": True,
        "microfit_fixed_transition_candidate_defined": True,
        "microfit_fixed_transition_exact_order_codes_bound": True,
        "microfit_cf130_core_od_verified": False,
        "transition_brackets_dimensioned": True,
        "transition_bracket_placement_count": 25,
        "cf9_current_capacity_released": False,
        "cf9_route_life_verified": False,
        "planning_resistance_basis_ohm_per_km_at_20c": 79.0,
        "maximum_planning_voltage_drop_20c_at_candidate_cap_v": max(float(r["voltage_drop_20c_at_candidate_cap_v"]) for r in axes),
        "maximum_planning_conductor_loss_20c_at_candidate_cap_w": max(float(r["conductor_loss_20c_at_candidate_cap_w"]) for r in axes),
        "power_cable_selected": False, "data_cable_selected": False, "crimp_process_selected": False,
        "built_cable_count": 0, "executed_test_count": 0, "procurement_authority": False, "fabrication_authority": False,
        "connection_authority": False, "powered_test_authority": False, "motion_authority": False, "energization_authority": False,
    }
    (OUT / "actuator-cable-kit-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(f"# HR-30 actuator cable kit P0.1\n\n**{WARNING}**\n\nThis package defines all 25 actuator-power branches as a moving igus CF130.03.02.UL pair ending at a fixed, panel-mounted Molex Micro-Fit 3.0 transition, followed by a restrained Alpha Wire 3051 pigtail into the JST EH actuator housing. Direct CF130-to-JST crimping is rejected. The dimensioned bracket candidate and all 25 nominal module placements are configuration-bound. The official connector cutout, received fit, material, fasteners, clamp force, pigtail lengths, tolerance-aware production-body integration, crimp qualification, derating, temperature rise, flex life and every physical work authority remain open.\n", encoding="utf-8", newline="\n")
    (OUT / "actuator-cable-kit.svg").write_text(drawing(), encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(render(axes, cavities), encoding="utf-8", newline="\n")
    shutil.copy2(Path(__file__), OUT / "actuator-cable-kit-source.py")
    manifest = [{"path": p.relative_to(OUT).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p), "warning": WARNING} for p in sorted(OUT.rglob("*")) if p.is_file() and p.name != "file-manifest.csv"]
    write_csv(OUT / "file-manifest.csv", manifest)
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    shutil.copytree(OUT, RELEASE)
    integrate_root(axes, cavities)
    correct_root_copy()
    import generate_hr30_system_package_p01 as system
    system.refresh_manifest_and_release()
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
