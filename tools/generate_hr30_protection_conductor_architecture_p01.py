#!/usr/bin/env python3
"""Generate the HR-30 staged protection and conductor architecture package."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "electrical" / "protection-conductor-architecture-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "electrical" / OUT.name
IDENTIFIER = "HR30-PROTECTION-CONDUCTOR-ARCHITECTURE-P0.1"
DATE = "2026-08-17"
WARNING = (
    "PRELIMINARY - PROTECTION AND CONDUCTOR ARCHITECTURE ONLY - NOT APPROVED "
    "FOR PROCUREMENT, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"
)
AUTHORITY = "NO PROCUREMENT, CONNECTION, POWERED-TEST, MOTION OR ENERGIZATION AUTHORITY"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def common(row: dict[str, object]) -> dict[str, object]:
    return {**row, "execution_state": "NOT EXECUTED", "authority": AUTHORITY, "warning": WARNING}


def source_bindings() -> list[dict[str, object]]:
    paths = [
        ("PCA-B01", "first-energization state ladder", WHOLE / "first-energization-readiness-p0.1/power-state-ladder.csv"),
        ("PCA-B02", "logic-only fixture status", WHOLE / "electrical/logic-power-kit-p0.1/logic-power-status.json"),
        ("PCA-B03", "logic-only supply settings", WHOLE / "electrical/logic-power-kit-p0.1/supply-configuration-register.csv"),
        ("PCA-B04", "eight-bus current boundary", WHOLE / "harness/current-policy-binding-p0.1/bus-power-boundary.csv"),
        ("PCA-B05", "25-axis cable screen", WHOLE / "harness/actuator-cable-kit-p0.1/axis-power-cable-candidate.csv"),
        ("PCA-B06", "five PDU feed boundary", WHOLE / "electrical/tether-power-core-p0.1/five-pdu-feed-register.csv"),
        ("PCA-B07", "PDU implementation status", WHOLE / "electrical/actuator-branch-pdu-p0.1/pdu-status.json"),
        ("PCA-B08", "PDU unresolved holds", WHOLE / "electrical/actuator-branch-pdu-p0.1/open-holds.csv"),
        ("PCA-B09", "tether primary sources", WHOLE / "electrical/tether-power-core-p0.1/primary-source-register.csv"),
    ]
    return [
        common({
            "binding_id": item_id,
            "role": role,
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": sha(path),
            "bytes": path.stat().st_size,
        })
        for item_id, role, path in paths
    ]


def primary_sources() -> list[dict[str, object]]:
    rows = [
        ("PCA-S01", "Mean Well", "RSP-500 series specification", "RSP-500-SPEC; 2025-09-26", "https://www.meanwell.com/Upload/PDF/RSP-500/RSP-500-SPEC.PDF", "RSP-500-12 nominal 12 V, 41.7 A, 500.4 W source endpoint; source protection and application behavior still require review"),
        ("PCA-S02", "Texas Instruments", "TPS25947xx datasheet", "SLVSFC9C Rev C; May 2026", "https://www.ti.com/lit/ds/symlink/tps25947.pdf", "2.7-23 V eFuse family; adjustable 0.5-6 A current limit; stated +/-10% accuracy above 1 A; true reverse-current blocking"),
        ("PCA-S03", "Littelfuse", "MIDI 498 fuse-holder datasheet", "current official datasheet; accessed 2026-08-17", "https://www.littelfuse.com/assetdocs/littelfuse-fuse-holder-midi-498-datasheet-rd1?assetguid=b38a61f3-7d0b-4081-bfb5-86c4b4ea4f26", "04980923ZXT holder family boundary; fuse is separate and no fuse value is released"),
        ("PCA-S04", "Phoenix Contact", "MKDS 5/2-9.5 product page", "order 1714971; accessed 2026-08-17", "https://www.phoenixcontact.com/en-us/products/pcb-terminal-block-mkds-5-2-95-1714971", "32 A nominal terminal candidate; application derating, conductor and thermal proof remain open"),
        ("PCA-S05", "JST", "EH connector-series datasheet", "revision/date not stated; accessed 2026-08-17", "https://www.jst-mfg.com/product/pdf/eng/eEH.pdf", "3 A headline is associated with AWG22; selected AWG24 candidate requires separate current/temperature validation"),
        ("PCA-S06", "igus", "chainflex CF9.UL product data", "live official page; accessed 2026-08-17", "https://www.igus.com/product/CF9_UL", "CF9.UL.02.02 2 x 0.25 mm2 / 24 AWG continuous-flex candidate; hot bundled ampacity is not released"),
        ("PCA-S07", "SIGLENT", "SPD3303X/X-E series product page and datasheet", "datasheet EN03A; 2024-09-02", "https://www.siglent.com/na/products-overview/spd3303x-x-e/", "separate current-limited logic-only bench-source candidate; receipt, calibration and settings remain open"),
    ]
    return [common({"source_id": i, "manufacturer": m, "document": d, "revision_or_date": rev, "accessed": DATE, "url": url, "verified_use": use}) for i, m, d, rev, url, use in rows]


def power_states() -> list[dict[str, object]]:
    rows = [
        ("FER-E0", "MECHANICAL INSPECTION", "NONE", "NONE", "NONE", "all sources physically absent", "NO"),
        ("FER-E1", "UNPOWERED ELECTRICAL INSPECTION", "NONE", "NONE", "NONE", "all sources and stored energy absent; discharge verified", "NO"),
        ("FER-E2", "LOGIC-ONLY CONTROLLER", "SPD3303X CH1 candidate to J1 only", "NONE", "NONE", "all actuator carriers, buses and actuator connectors physically absent", "NO"),
        ("FER-E3", "SAFETY-LOGIC TEST", "24 V control source candidate", "NONE", "NONE", "contactor load side and actuator buses physically absent", "NO"),
        ("FER-E4", "ONE-AXIS BENCH", "separate 11.0 V / 0.25 A candidate bench source", "one isolated actuator", "NONE", "never connected to whole-body power; torque disabled", "NO"),
        ("FER-E5", "ONE-PDU-BRANCH LOAD TEST", "RSP path through dual contactors", "one selected feed into approved electronic load", "one PDU only", "no actuators attached; all other feeds absent", "NO"),
        ("FER-E6", "WHOLE DISTRIBUTION NO LOAD", "RSP path through dual contactors", "five feeds with individually selected protection", "five PDUs; actuators absent", "source current limited below separately approved inspection limit", "NO"),
        ("FER-E7", "RESTRAINED WHOLE-ROBOT RAIL TEST", "RSP path through dual contactors", "five feeds", "25 eFuse branches", "all prior gates complete; torque disabled; zero motion request", "NO"),
    ]
    return [common({"state_id": i, "name": name, "source_present": source, "feed_scope": feed, "axis_branch_scope": axis, "mandatory_physical_separation": separation, "motion_permitted": motion, "state_release": "OPEN - NOT EXECUTED"}) for i, name, source, feed, axis, separation, motion in rows]


def protection_layers() -> list[dict[str, object]]:
    rows = [
        ("PCA-L01", "logic-only source", "SIGLENT SPD3303X CH1 current limit and OCP", "FER-E2", "SELECTION REQUIRED", "received controller inrush, steady load, input protection and fault response"),
        ("PCA-L02", "12 V source boundary", "RSP-500-12 internal protection plus external main fuse F0", "FER-E5 through FER-E7", "SELECTION REQUIRED", "available fault current/time behavior, cable/contact limits, coordination and jurisdiction"),
        ("PCA-L03", "redundant rail interruption", "K1 and K2 LC1D40ABD main poles", "FER-E5 through FER-E7", "CONTACTOR CANDIDATE; APPLICATION RELEASE OPEN", "received hardware, DC utilization, opening time, fault duty, series-pole jumpers and regeneration"),
        ("PCA-L04", "five robot feed branches", "FB1-FB5 Littelfuse 04980923ZXT holders", "FER-E5 through FER-E7", "FUSE VALUES SELECTION REQUIRED", "RMS demand, fault current, inrush, regeneration, conductor/contact limits and coordination"),
        ("PCA-L05", "25 actuator branches", "TPS259474L eFuse channels", "FER-E7", "THRESHOLDS SELECTION REQUIRED", "threshold tolerance, hot PCB/connector tests, short-circuit behavior and reverse-energy architecture"),
        ("PCA-L06", "actuator electronic limit", "25 candidate DYNAMIXEL Current Limit values", "FER-E7 and later", "CONTROL POLICY CANDIDATE ONLY", "external current correlation, torque/duty/thermal proof and deterministic enforcement"),
        ("PCA-L07", "stored/regenerative energy", "no released sink or bidirectional return path", "FER-E5 and later", "ARCHITECTURE SELECTION REQUIRED", "measured regeneration, source absorption, clamp/dump sizing, overvoltage and power-loss tests"),
    ]
    return [common({"layer_id": i, "boundary": boundary, "candidate_mechanism": mechanism, "applicable_states": states, "selection_state": state, "closure_evidence": evidence}) for i, boundary, mechanism, states, state, evidence in rows]


def bus_and_feed_rows() -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, float]]:
    buses = read_csv(WHOLE / "harness/current-policy-binding-p0.1/bus-power-boundary.csv")
    feeds = read_csv(WHOLE / "electrical/tether-power-core-p0.1/five-pdu-feed-register.csv")
    feed_map = {
        "FB1": ["RS-LLEG"], "FB2": ["RS-RLEG"], "FB3": ["RS-LARM", "RS-RARM"],
        "FB4": ["TTL-HEAD", "TTL-LDIST", "TTL-RDIST"], "FB5": ["RS-WAIST"],
    }
    by_bus = {r["bus_id"]: r for r in buses}
    bus_rows: list[dict[str, object]] = []
    for row in buses:
        cap = float(row["candidate_internal_cap_sum_a"])
        stall = float(row["published_stall_endpoint_sum_a"])
        bus_rows.append(common({
            "bus_id": row["bus_id"], "axis_count": row["axis_count"], "candidate_cap_sum_a": f"{cap:.6f}",
            "published_stall_endpoint_sum_a": f"{stall:.3f}", "normal_rms_demand_a": "SELECTION REQUIRED",
            "regenerative_return_a": "SELECTION REQUIRED", "source_or_fuse_rating_credit": "NONE",
            "disposition": "ARITHMETIC BOUNDARIES ONLY - NOT NORMAL DEMAND OR A PROTECTION RATING",
        }))
    feed_rows: list[dict[str, object]] = []
    for feed in feeds:
        members = feed_map[feed["branch_id"]]
        cap = sum(float(by_bus[m]["candidate_internal_cap_sum_a"]) for m in members)
        stall = sum(float(by_bus[m]["published_stall_endpoint_sum_a"]) for m in members)
        feed_rows.append(common({
            "branch_id": feed["branch_id"], "pdu": feed["board_instance"], "included_buses": "; ".join(members),
            "candidate_cap_sum_a": f"{cap:.6f}", "published_stall_endpoint_sum_a": f"{stall:.3f}",
            "terminal_nominal_a": feed["terminal_nominal_current_a"], "holder_order_code": feed["holder_order_code"],
            "fuse_order_code": "SELECTION REQUIRED", "fuse_value_a": "SELECTION REQUIRED", "feed_conductor": "SELECTION REQUIRED",
            "required_closure": feed["required_closure"],
        }))
    totals = {
        "candidate_cap_sum_a": sum(float(r["candidate_internal_cap_sum_a"]) for r in buses),
        "stall_endpoint_sum_a": sum(float(r["published_stall_endpoint_sum_a"]) for r in buses),
        "source_continuous_a": 41.7,
    }
    return bus_rows, feed_rows, totals


def axis_screens() -> list[dict[str, object]]:
    source = read_csv(WHOLE / "harness/actuator-cable-kit-p0.1/axis-power-cable-candidate.csv")
    rows: list[dict[str, object]] = []
    for item in source:
        cap = float(item["candidate_internal_limit_a"])
        rows.append(common({
            "axis_id": item["axis_id"], "bus_id": item["bus_id"], "actuator_model": item["actuator_model"],
            "candidate_internal_limit_a": f"{cap:.6f}", "published_stall_endpoint_a": item["published_stall_endpoint_a"],
            "one_way_planning_length_mm": item["one_way_planning_length_mm"], "candidate_conductor": item["power_pair_test_coupon_candidate"],
            "loop_resistance_20c_ohm": item["loop_resistance_20c_planning_ohm"],
            "drop_at_candidate_cap_20c_v": item["voltage_drop_20c_at_candidate_cap_v"],
            "loss_at_candidate_cap_20c_w": item["conductor_loss_20c_at_candidate_cap_w"],
            "jst_3a_headline_minus_cap_a": f"{3.0-cap:.6f}",
            "headline_margin_is_ampacity_credit": "NO - JST 3 A HEADLINE IS AWG22; THIS CANDIDATE IS AWG24",
            "normal_rms_a": "SELECTION REQUIRED", "fault_current_a": "SELECTION REQUIRED",
            "hot_bundled_ampacity": "SELECTION REQUIRED", "branch_protection": "SELECTION REQUIRED",
        }))
    return rows


def connector_boundaries() -> list[dict[str, object]]:
    rows = [
        ("PCA-C01", "RSP-500-12 output", "source screw terminal", "41.7 A source endpoint", "exact received terminal/conductor/torque and thermal evidence required", "OPEN"),
        ("PCA-C02", "tether quick disconnect", "Anderson SBS75G family", "catalogue family only", "exact shell/contact/wire/assembly/derating and disconnect duty required", "OPEN"),
        ("PCA-C03", "five PDU inputs", "Phoenix Contact 1714971", "32 A nominal candidate", "feed RMS/fault/inrush/thermal and conductor fit required", "OPEN"),
        ("PCA-C04", "25 actuator outputs", "JST VH at PDU boundary", "candidate connector family", "exact contact/wire/crimp/current-rise/retention evidence required", "OPEN"),
        ("PCA-C05", "25 actuator device inputs", "JST EH", "3 A headline at AWG22", "AWG24 CF9 coupon hot-current and crimp-rise validation required", "OPEN"),
        ("PCA-C06", "logic-only J1", "JST VHR-2N / SVH-21T-P1.1", "22 AWG candidate cable", "received board, cable build, polarity, pull, current-limit and temperature evidence required", "OPEN"),
    ]
    return [common({"boundary_id": i, "interface": interface, "candidate": candidate, "published_or_project_boundary": limit, "evidence_required": evidence, "state": state}) for i, interface, candidate, limit, evidence, state in rows]


def closure_inputs() -> list[dict[str, object]]:
    data = [
        ("PCA-I01", "available prospective short-circuit current at RSP output and at each remote branch", "A and clearing-time trace", "source characterization with calibrated load/fault fixture", "MAIN AND BRANCH FUSES"),
        ("PCA-I02", "as-built one-way feed lengths and return topology", "mm", "measured harness drawing and continuity record", "CONDUCTOR DROP/FAULT LOOP"),
        ("PCA-I03", "maximum enclosure and harness ambient", "degC", "instrumented thermal test", "DERATING"),
        ("PCA-I04", "bundle count, fill and adjacent heat sources", "count/layout", "as-built route inspection", "DERATING"),
        ("PCA-I05", "connector/contact/lug exact order codes and received variants", "part/lot", "CoC plus incoming inspection", "CONTACT LIMITS"),
        ("PCA-I06", "controller, PDU and actuator inrush by state", "A versus ms", "oscilloscope/current-probe capture", "NUISANCE TRIP/COORDINATION"),
        ("PCA-I07", "normal RMS and peak current for each axis and five feeds", "A; duty cycle", "restrained staged motion measurements", "WIRE/FUSE THERMAL"),
        ("PCA-I08", "regenerative return energy/current and rail overvoltage", "J; A; V versus ms", "dynamometer/restrained deceleration and power-loss tests", "REGENERATION ARCHITECTURE"),
        ("PCA-I09", "PDU copper, eFuse and connector temperature rise", "degC", "instrumented maximum-duty board test", "PDU CAPACITY"),
        ("PCA-I10", "fuse time-current curves and interrupt ratings at selected voltage", "curve/rating", "exact fuse datasheet and coordination study", "FUSE SELECTION"),
        ("PCA-I11", "source current-limit/foldback and absorption behavior", "A/V versus ms", "manufacturer-approved application basis plus bench characterization", "SOURCE COMPATIBILITY"),
        ("PCA-I12", "Boston site branch circuit, disconnect and AHJ basis", "installation record", "qualified electrical review and site inspection", "JURISDICTION"),
        ("PCA-I13", "strain relief, bend, flex and crimp process capability", "test records", "coupon lots, pull/microsection/flex/torsion evidence", "HARNESS RELEASE"),
        ("PCA-I14", "single-fault and backfeed behavior across all five feeds and 25 branches", "fault-injection record", "guarded staged fault tests", "COORDINATION/SEPARATION"),
    ]
    return [common({"input_id": i, "missing_input": name, "required_units_or_record": units, "closure_method": method, "decisions_blocked": blocked, "state": "OPEN"}) for i, name, units, method, blocked in data]


def holds() -> list[dict[str, object]]:
    data = [
        ("PCA-H01", "logic-only voltage, current-limit and OCP settings remain unreleased", "received controller inspection, inrush/steady/fault measurements and qualified setting disposition"),
        ("PCA-H02", "RSP source and main F0 protection are uncoordinated", "prospective-fault/current-limit behavior, exact conductor/contact limits, fuse curve and interrupt-rating study"),
        ("PCA-H03", "FB1-FB5 fuse values and order codes remain unselected", "five-feed RMS/peak/inrush/regeneration/fault measurements and coordination study"),
        ("PCA-H04", "five PDU-feed conductor assemblies remain unselected", "as-built lengths, ambient, bundling, flex, termination, voltage-drop and fault-loop evidence"),
        ("PCA-H05", "25 AWG24 actuator pairs have geometry/drop screens but no hot ampacity release", "received-lot crimp, current-rise, bundle, duty, flex/torsion and connector-temperature tests"),
        ("PCA-H06", "whole-body cap sum 46.67779 A exceeds 41.7 A source endpoint", "measured state-dependent demand plus enforced aggregate policy or a different qualified source architecture"),
        ("PCA-H07", "TPS25947 reverse blocking prevents regenerative return through the individual branch eFuses", "select and validate local absorption/clamp/dump or a qualified bidirectional power architecture"),
        ("PCA-H08", "protection hardware is unbuilt and fault tests are unexecuted", "received assemblies, inspections, calibrated measurements and guarded fault-injection evidence"),
        ("PCA-H09", "Boston installation and jurisdictional requirements remain open", "site circuit/disconnect/enclosure review and applicable AHJ disposition"),
        ("PCA-H10", "qualified electrical and safety review has not accepted the frozen as-built system", "signed disposition covering the identical hardware, software, settings and test evidence"),
    ]
    return [common({"hold_id": i, "unresolved_item": item, "closure_evidence": evidence, "state": "OPEN"}) for i, item, evidence in data]


def diagram() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="980" viewBox="0 0 1500 980" role="img" aria-labelledby="title desc"><title id="title">HR-30 staged protection architecture</title><desc id="desc">The isolated 5 volt logic-only path is physically separate from the twelve volt whole-body path. The whole-body path contains the source, main protection, dual contactors, five protected feeds, five PDU boards, twenty-five eFuse branches and actuators.</desc><style>text{{font:600 18px system-ui;fill:#102b46}}.h{{font-size:32px;font-weight:900}}.s{{font-size:15px}}.box{{fill:#fff;stroke:#0b4f91;stroke-width:4}}.gold{{fill:#fff0b5;stroke:#8a6200;stroke-width:4}}.hold{{fill:#ffe4e0;stroke:#982520;stroke-width:4}}.line{{stroke:#0b4f91;stroke-width:6;fill:none}}.dash{{stroke:#982520;stroke-width:5;stroke-dasharray:13 10;fill:none}}</style><rect width="1500" height="980" fill="#eef8ff"/><text class="h" x="50" y="58">HR-30 staged power and protection boundary</text><text x="50" y="96">Two physically separate paths. Every value and physical result shown as open remains unreleased.</text><rect class="gold" x="50" y="150" width="1400" height="220" rx="22"/><text class="h" x="84" y="197">FER-E2 · logic only</text><rect class="box" x="90" y="235" width="270" height="90" rx="14"/><text x="120" y="273">SPD3303X CH1</text><text class="s" x="120" y="301">settings: SELECTION REQUIRED</text><path class="line" d="M360 280H535"/><rect class="box" x="535" y="235" width="300" height="90" rx="14"/><text x="565" y="273">Motion controller J1</text><text class="s" x="565" y="301">AUX_5V_SAFE / CTRL_GND</text><path class="dash" d="M890 230V335"/><text x="925" y="270">Actuator carriers, buses and</text><text x="925" y="302">connectors physically absent</text><rect class="box" x="50" y="425" width="220" height="110" rx="16"/><text x="80" y="468">RSP-500-12</text><text class="s" x="80" y="499">12 V · 41.7 A endpoint</text><path class="line" d="M270 480H360"/><rect class="hold" x="360" y="425" width="210" height="110" rx="16"/><text x="397" y="468">Main fuse F0</text><text class="s" x="397" y="499">SELECTION REQUIRED</text><path class="line" d="M570 480H650"/><rect class="box" x="650" y="425" width="250" height="110" rx="16"/><text x="690" y="468">K1 + K2</text><text class="s" x="690" y="499">dual interruption candidate</text><path class="line" d="M900 480H980"/><rect class="hold" x="980" y="425" width="300" height="110" rx="16"/><text x="1020" y="468">FB1–FB5</text><text class="s" x="1020" y="499">all fuse values required</text><path class="line" d="M1130 535V600"/><rect class="box" x="810" y="600" width="640" height="120" rx="18"/><text class="h" x="850" y="648">Five PDU boards</text><text x="850" y="682">25 TPS25947 eFuse branches · thresholds open</text><path class="line" d="M1130 720V785"/><rect class="box" x="810" y="785" width="640" height="120" rx="18"/><text class="h" x="850" y="833">25 actuator power pairs</text><text x="850" y="868">AWG24 candidate · hot ampacity and protection open</text><rect class="hold" x="50" y="600" width="650" height="305" rx="20"/><text class="h" x="90" y="650">System constraints</text><text x="90" y="700">Candidate current-cap sum: 46.678 A</text><text x="90" y="742">Source continuous endpoint: 41.7 A</text><text x="90" y="784">Published stall-endpoint sum: 76.08 A</text><text x="90" y="835">Reverse-blocking eFuses do not provide a</text><text x="90" y="870">released regenerative-energy path.</text><text class="s" x="50" y="950">PRELIMINARY · no procurement, connection, powered-test, motion or energization authority</text></svg>'''


def page(status: dict[str, object], feed_rows: list[dict[str, object]], state_rows: list[dict[str, object]], hold_rows: list[dict[str, object]]) -> str:
    feed_html = "".join(
        f'<tr><td>{html.escape(str(r["branch_id"]))}</td><td>{html.escape(str(r["included_buses"]))}</td><td>{r["candidate_cap_sum_a"]}</td><td>{r["published_stall_endpoint_sum_a"]}</td><td>SELECTION REQUIRED</td></tr>'
        for r in feed_rows
    )
    states = "".join(
        f'<article><b>{r["state_id"]}</b><h3>{html.escape(str(r["name"]))}</h3><p>{html.escape(str(r["mandatory_physical_separation"]))}</p><strong>OPEN · NO MOTION</strong></article>'
        for r in state_rows
    )
    holds_html = "".join(f'<li><b>{r["hold_id"]}</b> {html.escape(str(r["unresolved_item"]))}</li>' for r in hold_rows)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 protection and conductors</title><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#d9f2ff;--gold:#f2b91d;--paper:#f7fbff;--ink:#142a40;--line:#82c4e6;--red:#982520}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1280px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white}}h1{{font-size:clamp(38px,6vw,70px);line-height:1.04;max-width:18ch}}h2{{font-size:clamp(28px,4vw,44px)}}h3{{font-size:21px}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px}}article,.panel,li{{background:white;border:2px solid var(--line);border-radius:16px;padding:19px}}article strong{{color:var(--red)}}.metric{{font-size:clamp(34px,5vw,54px);font-weight:900;color:var(--blue)}}.bad{{color:var(--red)}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:16px;background:white}}object{{display:block;width:100%;min-width:900px}}table{{border-collapse:collapse;width:100%;min-width:850px}}th,td{{padding:14px;text-align:left;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--sky)}}a{{color:#075b9b;font-weight:800}}li{{margin:12px 0}}small{{font-size:14px}}@media(max-width:560px){{body{{font-size:16px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>HR-30 whole-body P0.1</p><h1>The power hierarchy is coherent. Its ratings are not released.</h1><p>The controller-only path is physically separated from actuator power. The whole-body path now binds one source, dual interruption, five protected feeds, five PDU boards and 25 individual actuator branches.</p></header><main><section class="grid"><article><div class="metric">41.7 A</div><p>candidate source continuous endpoint</p></article><article><div class="metric bad">46.678 A</div><p>arithmetic sum of candidate axis caps</p></article><article><div class="metric bad">76.08 A</div><p>published stall-endpoint sum; not normal demand</p></article><article><div class="metric">0</div><p>released fuse values or hot conductor ratings</p></article></section><section><h2>Two intentionally separate power paths</h2><div class="scroll"><object data="protection-hierarchy.svg" type="image/svg+xml" aria-label="HR-30 staged protection hierarchy"></object></div></section><section><h2>Five whole-robot feeds</h2><p>These current figures are arithmetic boundaries. They are not fuse, wire, connector or supply ratings.</p><div class="scroll"><table><thead><tr><th>Feed</th><th>Buses</th><th>Cap sum A</th><th>Stall endpoint A</th><th>Fuse</th></tr></thead><tbody>{feed_html}</tbody></table></div><p><a href="pdu-feed-envelope.csv">Open the complete five-feed register</a> · <a href="bus-envelope.csv">eight-bus register</a> · <a href="axis-conductor-screen.csv">25-axis conductor screen</a></p></section><section><h2>Staged separation rules</h2><div class="grid">{states}</div></section><section class="panel"><h2>What must be measured before selecting protection</h2><p><a href="closure-input-register.csv">Fourteen missing-input records</a> cover prospective fault current, measured load, ambient, bundling, inrush, regeneration, connector limits and jurisdiction.</p><h2>Open holds</h2><ul>{holds_html}</ul><p><a href="protection-conductor-status.json">Machine-readable status</a> · <a href="primary-source-register.csv">primary manufacturer sources</a> · <a href="protection-layer-register.csv">seven protection layers</a></p></section></main><footer>{html.escape(WARNING)}</footer></body></html>'''


def integrate_root(status: dict[str, object]) -> None:
    status_path = WHOLE / "package-status.json"
    root_status = json.loads(status_path.read_text(encoding="utf-8"))
    root_status.update({
        "protection_conductor_architecture_present": True,
        "protection_conductor_power_state_count": status["power_state_count"],
        "protection_conductor_feed_count": status["pdu_feed_count"],
        "protection_conductor_axis_count": status["axis_screen_count"],
        "candidate_source_continuous_a": status["candidate_source_continuous_a"],
        "candidate_cap_sum_exceeds_source": True,
        "candidate_cap_sum_source_shortfall_a": status["candidate_cap_sum_source_shortfall_a"],
        "logic_only_actuator_power_physically_absent_by_plan": True,
        "main_fuse_selected": False,
        "five_feed_fuses_selected": False,
        "hot_conductor_ampacity_released": False,
        "regenerative_energy_architecture_released": False,
        "protection_conductor_connection_authority": False,
        "protection_conductor_energization_authority": False,
    })
    status_path.write_text(json.dumps(root_status, indent=2) + "\n", encoding="utf-8")

    readme = WHOLE / "README.md"
    text = readme.read_text(encoding="utf-8")
    start, end = "<!-- HR30-PROTECTION-CONDUCTOR-P01-README-START -->", "<!-- HR30-PROTECTION-CONDUCTOR-P01-README-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    block = f'''{start}\n## Staged protection and conductor architecture\n\nThe [interactive protection/conductor guide](electrical/protection-conductor-architecture-p0.1/index.html) binds the isolated 5 V logic-only path and the 12 V whole-body path into one staged hierarchy. The eight candidate axis-cap sums total 46.67779 A, above the 41.7 A source endpoint; the separate published stall endpoints total 76.08 A. These are constraints, not demand predictions or protection ratings. All fuse values, hot ampacity, regeneration handling and physical evidence remain open.\n{end}\n'''
    block = block.replace("76.08 A", "71.88 A")
    marker = "<!-- HR30-GROUNDING-REFERENCE-P01-README-START -->"
    text = text.replace(marker, block + marker) if marker in text else text.rstrip() + "\n\n" + block
    readme.write_text(text, encoding="utf-8", newline="\n")

    page_path = WHOLE / "index.html"
    text = page_path.read_text(encoding="utf-8")
    start, end = "<!-- HR30-PROTECTION-CONDUCTOR-P01-START -->", "<!-- HR30-PROTECTION-CONDUCTOR-P01-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    section = f'''{start}<section id="protection-conductor"><h2>The whole-body power hierarchy now exposes its real limits</h2><div class="grid"><article class="card pass"><div class="metric">5 V</div><p>logic-only path with every actuator connection physically absent.</p></article><article class="card"><div class="metric">5 + 25</div><p>whole-robot feed branches and individual actuator branches.</p></article><article class="card hold"><div class="metric">46.678 &gt; 41.7 A</div><p>candidate cap sum exceeds the source endpoint; measured demand or a new source architecture is required.</p></article><article class="card hold"><div class="metric">0</div><p>released fuse values or hot conductor ratings.</p></article></div><p><a href="electrical/protection-conductor-architecture-p0.1/index.html">Open the interactive protection/conductor guide</a>. Regeneration, coordination, physical tests and all connection authority remain open.</p></section>{end}'''
    marker = "<!-- HR30-GROUNDING-REFERENCE-P01-START -->"
    text = text.replace(marker, section + marker) if marker in text else text.replace("</main>", section + "</main>", 1)
    page_path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    bus_rows, feed_rows, totals = bus_and_feed_rows()
    state_rows = power_states()
    axis_rows = axis_screens()
    hold_rows = holds()
    shortfall = totals["candidate_cap_sum_a"] - totals["source_continuous_a"]
    status = {
        "identifier": IDENTIFIER, "warning": WARNING,
        "source_binding_count": 9, "primary_source_count": 7, "power_state_count": len(state_rows),
        "protection_layer_count": 7, "bus_count": len(bus_rows), "pdu_feed_count": len(feed_rows),
        "axis_screen_count": len(axis_rows), "connector_boundary_count": 6, "closure_input_count": 14,
        "open_hold_count": len(hold_rows), "candidate_source_continuous_a": totals["source_continuous_a"],
        "candidate_cap_sum_a": round(totals["candidate_cap_sum_a"], 6),
        "published_stall_endpoint_sum_a": round(totals["stall_endpoint_sum_a"], 3),
        "candidate_cap_sum_source_shortfall_a": round(shortfall, 6),
        "candidate_cap_sum_percent_of_source": round(100 * totals["candidate_cap_sum_a"] / totals["source_continuous_a"], 3),
        "stall_endpoint_sum_percent_of_source": round(100 * totals["stall_endpoint_sum_a"] / totals["source_continuous_a"], 3),
        "logic_only_path_physically_separated_by_plan": True,
        "main_fuse_selected": False, "five_feed_fuses_selected": False, "hot_conductor_ampacity_released": False,
        "regenerative_energy_architecture_released": False, "physical_measurements_executed": 0,
        "procurement_authority": False, "connection_authority": False, "powered_test_authority": False,
        "motion_authority": False, "energization_authority": False,
    }
    write_csv(OUT / "source-binding.csv", source_bindings())
    write_csv(OUT / "primary-source-register.csv", primary_sources())
    write_csv(OUT / "power-state-separation-register.csv", state_rows)
    write_csv(OUT / "protection-layer-register.csv", protection_layers())
    write_csv(OUT / "bus-envelope.csv", bus_rows)
    write_csv(OUT / "pdu-feed-envelope.csv", feed_rows)
    write_csv(OUT / "axis-conductor-screen.csv", axis_rows)
    write_csv(OUT / "connector-bottleneck-register.csv", connector_boundaries())
    write_csv(OUT / "closure-input-register.csv", closure_inputs())
    write_csv(OUT / "open-holds.csv", hold_rows)
    (OUT / "protection-hierarchy.svg").write_text(diagram().replace("76.08 A", "71.88 A"), encoding="utf-8", newline="\n")
    (OUT / "protection-conductor-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "index.html").write_text(page(status, feed_rows, state_rows, hold_rows).replace("76.08 A", "71.88 A"), encoding="utf-8", newline="\n")
    (OUT / "README.md").write_text(
        f"# HR-30 protection and conductor architecture P0.1\n\n**{WARNING}**\n\nThis package separates the 5 V logic-only state from the 12 V actuator path and binds the latter through one source, dual interruption, five protected feeds and 25 eFuse branches. It deliberately releases no fuse value or conductor ampacity. Open [index.html](index.html) for the interactive guide.\n",
        encoding="utf-8", newline="\n",
    )
    manifest_rows = []
    for path in sorted(p for p in OUT.iterdir() if p.name != "file-manifest.csv"):
        manifest_rows.append({"path": path.name, "sha256": sha(path), "bytes": path.stat().st_size, "warning": WARNING})
    write_csv(OUT / "file-manifest.csv", manifest_rows)
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    RELEASE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(OUT, RELEASE)
    integrate_root(status)
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    import generate_hr30_system_package_p01 as system_package
    system_package.refresh_manifest_and_release()
    print(f"generated {OUT.relative_to(ROOT)}: {len(axis_rows)} axes, {len(feed_rows)} feeds, {len(state_rows)} states")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
