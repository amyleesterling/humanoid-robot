"""Bind the HR-30 physical harness to the 25-axis current policy.

This is deliberately a reconciliation artifact.  It carries the current-limit
candidate and published stall endpoint beside each geometry-derived power-pair
length, but it does not select conductors, branch protection, or normal demand.
"""

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
CURRENT = WHOLE / "current-constrained-actuation-p0.1"
HARNESS = WHOLE / "harness" / "physical-p0.1"
OUT = WHOLE / "harness" / "current-policy-binding-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "harness" / "current-policy-binding-p0.1"
IDENTIFIER = "HR30-HARNESS-CURRENT-POLICY-BINDING-P0.1"
WARNING = "PRELIMINARY - HARNESS/CURRENT-POLICY RECONCILIATION ONLY - NOT APPROVED FOR PROCUREMENT, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
AUTHORITY = "NO PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION AUTHORITY"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def manifest(folder: Path) -> None:
    rows = []
    for path in sorted(p for p in folder.rglob("*") if p.is_file() and p.name != "file-manifest.csv"):
        rows.append({"path": path.relative_to(folder).as_posix(), "bytes": path.stat().st_size, "sha256": sha(path), "warning": WARNING})
    write_csv(folder / "file-manifest.csv", rows)


def root_integration(axis_rows: list[dict], stall_sum: float, cap_sum: float) -> None:
    status_path = WHOLE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "harness_current_policy_binding_present": True,
        "harness_current_policy_bound_axis_count": len(axis_rows),
        "harness_published_stall_endpoint_sum_a": round(stall_sum, 6),
        "harness_candidate_internal_cap_sum_a": round(cap_sum, 6),
        "harness_stall_endpoint_used_as_normal_demand": False,
        "harness_normal_rms_demand_selected": False,
        "harness_conductor_sizing_released": False,
        "harness_branch_protection_released": False,
        "connection_authority": False,
        "powered_test_authority": False,
        "motion_authority": False,
        "energization_authority": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    readme_path = WHOLE / "README.md"
    text = readme_path.read_text(encoding="utf-8")
    start = "<!-- HR30-HARNESS-CURRENT-BINDING-P01-README-START -->"
    end = "<!-- HR30-HARNESS-CURRENT-BINDING-P01-README-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    block = f'''{start}
## Harness/current-policy reconciliation

The [harness/current-policy guide](harness/current-policy-binding-p0.1/index.html) binds all 25 individual actuator power pairs to the candidate Current Limit register values and their geometry-derived planning lengths. It separates the **{stall_sum:.2f} A** arithmetic sum of published momentary stall endpoints from the **{cap_sum:.3f} A** arithmetic sum of candidate internal limits. Neither number is normal RMS demand, a conductor rating, a fuse value, or permission to connect power. Conductors, protection, voltage drop, temperature rise, duty, regeneration, received connectors and physical test evidence remain open.
{end}
'''
    marker = "<!-- HR30-CURRENT-CONSTRAINED-P01-README-START -->"
    readme_path.write_text(text.replace(marker, block + marker), encoding="utf-8", newline="\n")

    page_path = WHOLE / "index.html"
    text = page_path.read_text(encoding="utf-8")
    start = "<!-- HR30-HARNESS-CURRENT-BINDING-P01-START -->"
    end = "<!-- HR30-HARNESS-CURRENT-BINDING-P01-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    section = f'''{start}<section id="harness-current-binding"><h2>The current policy now reaches every actuator cable</h2><div class="grid"><article class="card pass"><div class="metric">25 / 25</div><p>individual power pairs are bound to one axis current policy and one routed planning length.</p></article><article class="card"><div class="metric">{cap_sum:.3f} A</div><p>candidate internal-limit sum; not normal demand or a source rating.</p></article><article class="card hold"><div class="metric">{stall_sum:.2f} A</div><p>published momentary stall-endpoint sum retained only as a separate fault boundary.</p></article><article class="card hold"><h3>Physical selections remain open</h3><p>RMS demand, wire construction, branch protection, voltage drop, temperature and regeneration still require evidence.</p></article></div><p><a href="harness/current-policy-binding-p0.1/index.html">Open the harness/current-policy guide</a> &middot; <a href="harness/current-policy-binding-p0.1/axis-power-policy-binding.csv">25-axis binding</a> &middot; <a href="harness/current-policy-binding-p0.1/bus-power-boundary.csv">eight-bus boundary</a>.</p></section>{end}'''
    marker = "<!-- HR30-CURRENT-CONSTRAINED-P01-START -->"
    page_path.write_text(text.replace(marker, section + marker), encoding="utf-8", newline="\n")

    holds_path = WHOLE / "open-holds.csv"
    holds = read_csv(holds_path)
    updates = {
        "HR30-P01-H03": "All twelve leg axes have static load screens and exact MISUMI candidate drivetrain geometry; all 45 nominal inter-drive pairs have zero common volume in the installed nominal CAD screen. The knees use dedicated 2.5:1 16:40 modules because the former 2:1 design required about 3.07 A at the published stall-line endpoint. All 25 axes now have candidate internal current limits and every routed actuator power pair is bound one-to-one to that policy. Published stall endpoints remain a separate fault boundary. Normal RMS demand, external-current correlation, continuous torque, connector temperature, branch protection, accepted trajectories, regeneration, fall restraint, gait correlation and physical proof remain open.",
        "HR30-P01-H07": "The physical harness accounts for every logical terminal, eight serial-data trunks, 25 isolated actuator power pairs, 25 current-policy bindings and joint service loops. Exact conductor construction, RMS/fault current, voltage drop, branch protection, dynamic-flex life, service slack, retention, shielding, derating, EMC, thermal and received-harness tests remain open.",
    }
    seen = set()
    for row in holds:
        if row["hold_id"] in updates:
            row["unresolved_item"] = updates[row["hold_id"]]
            seen.add(row["hold_id"])
    if seen != set(updates):
        raise RuntimeError(f"controlled root holds missing: {set(updates) - seen}")
    write_csv(holds_path, holds)


def render_index(axis_rows: list[dict], bus_rows: list[dict], stall_sum: float, cap_sum: float) -> str:
    body = "".join(
        f"<tr><td>{html.escape(r['axis_id'])}</td><td>{html.escape(r['bus_id'])}</td><td>{html.escape(r['actuator_model'])}</td><td>{r['candidate_internal_limit_a']} A</td><td>{r['published_stall_endpoint_a']} A</td><td>{r['round_trip_planning_length_mm']} mm</td><td>{html.escape(r['selection_state'])}</td></tr>"
        for r in axis_rows
    )
    buses = "".join(
        f"<tr><td>{html.escape(r['bus_id'])}</td><td>{r['axis_count']}</td><td>{r['candidate_internal_cap_sum_a']} A</td><td>{r['published_stall_endpoint_sum_a']} A</td><td>{html.escape(r['boundary'])}</td></tr>"
        for r in bus_rows
    )
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 harness/current-policy binding</title><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#d9f2ff;--gold:#f2b91d;--paper:#f6fbff;--ink:#142a40;--line:#91cbe7}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1280px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white}}h1{{font-size:clamp(38px,6vw,68px);line-height:1.05}}h2{{font-size:clamp(28px,4vw,42px)}}h3{{font-size:22px}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px}}article,.panel{{background:white;border:2px solid var(--line);border-radius:16px;padding:19px}}.metric{{font-size:clamp(30px,5vw,48px);font-weight:900;color:var(--blue)}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:14px;background:white}}table{{border-collapse:collapse;width:100%;min-width:1020px}}th,td{{padding:14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--deep);color:white;position:sticky;top:0}}a{{color:#075b9b;font-weight:800}}@media(max-width:560px){{body{{font-size:16px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>HR-30 whole-body P0.1</p><h1>The wiring now knows each joint's current ceiling.</h1><p>Every routed actuator power pair is reconciled with the deterministic local current policy while unresolved physical selections remain visibly open.</p></header><main><section class="grid"><article><div class="metric">25 / 25</div><p>axis power pairs bound</p></article><article><div class="metric">{cap_sum:.3f} A</div><p>candidate internal-limit sum</p></article><article><div class="metric">{stall_sum:.2f} A</div><p>published stall-endpoint sum, kept separate</p></article><article><div class="metric">0</div><p>released conductors, fuses, eFuses or powered-test permissions</p></article></section><section><h2>What changed</h2><div class="panel"><p>The old harness register correctly warned that {stall_sum:.2f} A was not expected demand, but it did not carry the later per-axis control limits. This package joins the two datasets. The connector screen only confirms that each candidate internal limit is numerically below the JST EH 3 A catalogue boundary; it does <strong>not</strong> establish application derating, thermal suitability or fault clearing.</p></div></section><section><h2>Eight bus boundaries</h2><div class="scroll"><table><thead><tr><th>Bus</th><th>Axes</th><th>Internal-cap sum</th><th>Stall-endpoint sum</th><th>Interpretation</th></tr></thead><tbody>{buses}</tbody></table></div></section><section><h2>All 25 actuator feeds</h2><div class="scroll"><table><thead><tr><th>Axis</th><th>Bus</th><th>Actuator</th><th>Candidate internal limit</th><th>Published stall endpoint</th><th>Round-trip planning length</th><th>Physical selection</th></tr></thead><tbody>{body}</tbody></table></div></section><section><h2>Still required before selection</h2><div class="panel"><p>Measured RMS and peak waveforms; available fault current; wire construction and temperature class; routing ambient and bundling; dynamic-flex life; inrush and regeneration; connector temperature rise; fuse/eFuse coordination; voltage-drop limits; received-part inspection; and jurisdiction-specific review.</p><p><a href="axis-power-policy-binding.csv">Axis binding CSV</a> &middot; <a href="bus-power-boundary.csv">Bus boundary CSV</a> &middot; <a href="open-holds.csv">Open evidence</a> &middot; <a href="source-binding.csv">Source binding</a></p></div></section></main><footer>{html.escape(WARNING)}</footer></body></html>'''


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    policy_path = CURRENT / "axis-current-torque-register.csv"
    bus_policy_path = CURRENT / "bus-current-budget.csv"
    pairs_path = HARNESS / "individual-power-pair-register.csv"
    derating_path = HARNESS / "current-derating-register.csv"
    policy = read_csv(policy_path)
    bus_policy = read_csv(bus_policy_path)
    pairs = read_csv(pairs_path)
    derating = read_csv(derating_path)
    if not (len(policy) == len(pairs) == len(derating) == 25 and len(bus_policy) == 8):
        raise RuntimeError("expected 25 axes/pairs/derating rows and 8 buses")

    policy_by_axis = {r["axis_id"]: r for r in policy}
    pair_by_axis = {r["axis_id"]: r for r in pairs}
    derating_by_axis = {r["circuit"].removeprefix("PWR-"): r for r in derating}
    if not (set(policy_by_axis) == set(pair_by_axis) == set(derating_by_axis)):
        raise RuntimeError("axis identity mismatch between current policy and physical harness")

    axis_rows = []
    by_bus: dict[str, list[dict]] = defaultdict(list)
    for axis_id in policy_by_axis:
        current = policy_by_axis[axis_id]
        pair = pair_by_axis[axis_id]
        old = derating_by_axis[axis_id]
        if current["bus_id"] != pair["bus_id"] or current["bus_id"] != old["bus_branch"]:
            raise RuntimeError(f"bus mismatch for {axis_id}")
        if abs(float(current["published_stall_current_a"]) - float(old["endpoint_current_a"])) > 1e-9:
            raise RuntimeError(f"published endpoint mismatch for {axis_id}")
        cap = float(current["candidate_current_a"])
        connector = float(old["connector_limit_a"].split()[0]) if old["connector_limit_a"].split()[0].replace('.', '', 1).isdigit() else 3.0
        row = {
            "axis_id": axis_id,
            "pair_id": pair["pair_id"],
            "bus_id": current["bus_id"],
            "actuator_model": current["actuator_model"],
            "candidate_current_limit_raw": current["current_limit_raw_candidate"],
            "candidate_internal_limit_a": f"{cap:.6f}",
            "published_stall_endpoint_a": f"{float(current['published_stall_current_a']):.3f}",
            "catalog_connector_boundary_a": f"{connector:.3f}",
            "internal_limit_below_catalog_boundary": "YES" if cap < connector else "NO",
            "one_way_planning_length_mm": pair["one_way_planning_length_mm"],
            "round_trip_planning_length_mm": pair["round_trip_planning_length_mm"],
            "positive_net": pair["positive_net"],
            "return_net": pair["return_net"],
            "destination_connector": pair["destination_connector"],
            "normal_rms_current_a": "SELECTION REQUIRED - MEASURED DUTY CYCLE NEEDED",
            "fault_current_a": "SELECTION REQUIRED - SOURCE/BRANCH IMPEDANCE NEEDED",
            "wire_construction": "SELECTION REQUIRED",
            "branch_protection": "SELECTION REQUIRED",
            "voltage_drop_and_temperature": "NOT CALCULATED - WIRE/TEMPERATURE/DUTY OPEN",
            "selection_state": "CURRENT POLICY BOUND; PHYSICAL CONDUCTOR/PROTECTION OPEN",
            "authority": AUTHORITY,
            "warning": WARNING,
        }
        if row["internal_limit_below_catalog_boundary"] != "YES":
            raise RuntimeError(f"candidate internal limit exceeds catalogue connector boundary: {axis_id}")
        axis_rows.append(row)
        by_bus[row["bus_id"]].append(row)

    bus_rows = []
    published_bus = {r["bus_id"]: r for r in bus_policy}
    for bus_id in sorted(by_bus):
        rows = by_bus[bus_id]
        cap = sum(float(r["candidate_internal_limit_a"]) for r in rows)
        stall = sum(float(r["published_stall_endpoint_a"]) for r in rows)
        if abs(cap - float(published_bus[bus_id]["simultaneous_candidate_cap_a"])) > 1e-6:
            raise RuntimeError(f"current-policy bus sum mismatch: {bus_id}")
        bus_rows.append({
            "bus_id": bus_id,
            "axis_count": len(rows),
            "axes": "; ".join(r["axis_id"] for r in rows),
            "candidate_internal_cap_sum_a": f"{cap:.6f}",
            "published_stall_endpoint_sum_a": f"{stall:.3f}",
            "normal_rms_demand_a": "SELECTION REQUIRED",
            "regenerative_return_a": "SELECTION REQUIRED",
            "branch_source_and_protection": "SELECTION REQUIRED",
            "boundary": "BOTH SUMS ARE ARITHMETIC BOUNDARIES; NEITHER IS A NORMAL-DEMAND, WIRE, FUSE OR SUPPLY RATING",
            "authority": AUTHORITY,
            "warning": WARNING,
        })

    stall_sum = sum(float(r["published_stall_endpoint_a"]) for r in axis_rows)
    cap_sum = sum(float(r["candidate_internal_limit_a"]) for r in axis_rows)
    if abs(stall_sum - 71.88) > 1e-9 or abs(cap_sum - 46.67779) > 1e-6:
        raise RuntimeError(f"whole-body boundary drift: stall={stall_sum}, cap={cap_sum}")

    decisions = [
        {"decision_id": "HCP-D01", "subject": "71.88 A published-stall sum", "disposition": "RETAIN ONLY AS SEPARATE MOMENTARY ENDPOINT/FAULT BOUNDARY", "reason": "not normal demand and not a conductor, protection or source rating", "authority": AUTHORITY, "warning": WARNING},
        {"decision_id": "HCP-D02", "subject": "46.67779 A candidate internal-cap sum", "disposition": "BIND TO 25 AXES; DO NOT PROMOTE TO HARNESS RATING", "reason": "internal register arithmetic lacks external-current, duty, diversity, regeneration and thermal correlation", "authority": AUTHORITY, "warning": WARNING},
        {"decision_id": "HCP-D03", "subject": "JST EH 3 A catalogue boundary", "disposition": "NUMERIC PER-AXIS SCREEN PASSES; APPLICATION VALIDATION OPEN", "reason": "catalogue boundary does not close contact temperature, flex cable, crimp, bundling or fault clearing", "authority": AUTHORITY, "warning": WARNING},
        {"decision_id": "HCP-D04", "subject": "standard ROBOTIS daisy cables", "disposition": "REJECT FOR DATA-ONLY INTER-ACTUATOR LINKS", "reason": "standard X3P/X4P includes VDD and would parallel individually protected feeds", "authority": AUTHORITY, "warning": WARNING},
        {"decision_id": "HCP-D05", "subject": "U2D2 Power Hub", "disposition": "REJECT FOR SUMMED WHOLE-BODY OR LEG POWER", "reason": "documented 10 A aggregate maximum is below either leg boundary and is not a 25-branch PDU", "authority": AUTHORITY, "warning": WARNING},
    ]
    holds = [
        ("HCP-H01", "normal RMS, peak duration, diversity and regeneration waveforms", "accepted standing/transfer/stepping trajectories with synchronized branch current and bus voltage"),
        ("HCP-H02", "available fault current and branch clearing requirement", "selected source/PDU topology, impedance, interruption time and applicable jurisdiction"),
        ("HCP-H03", "wire construction, cross-section, insulation, flex class and temperature rating", "supplier data plus geometry, ambient, bundling, duty and dynamic-cycle evidence"),
        ("HCP-H04", "branch fuse/eFuse/current-limiter selection and coordination", "fault clearing, inrush, regeneration, nuisance-trip and downstream connector protection tests"),
        ("HCP-H05", "JST EH contact/crimp/cable application temperature and voltage drop", "received harness coupons, correct tooling, pull tests and instrumented thermal tests"),
        ("HCP-H06", "data-only breakout/depinning construction", "controlled drawing, cavity blocking, continuity/no-backfeed inspection and fault injection"),
        ("HCP-H07", "qualified electrical and functional-safety review", "signed review of frozen as-built configuration and controlled test results"),
    ]
    hold_rows = [{"hold_id": i, "unresolved_item": item, "evidence_required": evidence, "state": "OPEN", "authority": AUTHORITY, "warning": WARNING} for i, item, evidence in holds]
    source_paths = [policy_path, bus_policy_path, pairs_path, derating_path]
    sources = [{"source_id": f"HCP-S{n:02d}", "path": p.relative_to(ROOT).as_posix(), "sha256": sha(p), "role": role, "warning": WARNING} for n, (p, role) in enumerate(zip(source_paths, ["25-axis candidate internal-current policy", "eight-bus cap arithmetic", "25 geometry-derived individual power pairs", "published endpoint and unresolved derating inputs"]), 1)]
    sources += [
        {"source_id": "HCP-S05", "path": "https://www.jst-mfg.com/product/pdf/eng/eEH.pdf", "sha256": "N/A - LIVE PRIMARY DOCUMENT", "role": "JST EH 3 A series boundary at AWG22; application derating remains open; accessed 2026-08-15", "warning": WARNING},
        {"source_id": "HCP-S06", "path": "https://docs.robotis.com/docs/parts/interface/u2d2_power_hub/", "sha256": "N/A - LIVE PRIMARY DOCUMENT", "role": "U2D2 Power Hub 10 A aggregate boundary; accessed 2026-08-15", "warning": WARNING},
    ]

    write_csv(OUT / "axis-power-policy-binding.csv", axis_rows)
    write_csv(OUT / "bus-power-boundary.csv", bus_rows)
    write_csv(OUT / "architecture-decision-register.csv", decisions)
    write_csv(OUT / "open-holds.csv", hold_rows)
    write_csv(OUT / "source-binding.csv", sources)
    status = {
        "identifier": IDENTIFIER,
        "axis_binding_count": len(axis_rows),
        "bus_binding_count": len(bus_rows),
        "published_stall_endpoint_sum_a": round(stall_sum, 6),
        "candidate_internal_cap_sum_a": round(cap_sum, 6),
        "candidate_internal_cap_reduction_from_stall_percent": round((1.0 - cap_sum / stall_sum) * 100.0, 6),
        "stall_endpoint_used_as_normal_demand": False,
        "internal_cap_used_as_harness_rating": False,
        "per_axis_catalog_connector_numeric_screen_pass_count": sum(r["internal_limit_below_catalog_boundary"] == "YES" for r in axis_rows),
        "normal_rms_demand_selected": False,
        "wire_construction_selected": False,
        "branch_protection_selected": False,
        "voltage_drop_calculated": False,
        "thermal_validated": False,
        "procurement_authority": False,
        "connection_authority": False,
        "powered_test_authority": False,
        "motion_authority": False,
        "energization_authority": False,
        "warning": WARNING,
    }
    (OUT / "status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(f"# HR-30 harness/current-policy binding P0.1\n\n**{WARNING}**\n\nAll 25 physical actuator power pairs are now bound to the deterministic local current-policy candidate and a geometry-derived planning length. The {stall_sum:.2f} A published-stall sum and {cap_sum:.5f} A internal-cap sum remain separate engineering boundaries. Neither is normal RMS demand or a released harness rating.\n", encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(render_index(axis_rows, bus_rows, stall_sum, cap_sum), encoding="utf-8", newline="\n")
    shutil.copy2(Path(__file__), OUT / "harness-current-policy-binding-source.py")
    manifest(OUT)
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    shutil.copytree(OUT, RELEASE)
    root_integration(axis_rows, stall_sum, cap_sum)
    import generate_hr30_system_package_p01 as system
    system.refresh_manifest_and_release()
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
