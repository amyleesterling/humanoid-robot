"""Generate the HR-30 whole-body current-constrained actuation candidate.

This package turns the 25-axis actuator allocation into an explicit register,
current, endpoint-torque and bus-current plan.  Published stall points are used
only for transparent linear endpoint screening, never as continuous ratings.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import shutil
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "current-constrained-actuation-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "current-constrained-actuation-p0.1"
IDENTIFIER = "HR30-CURRENT-CONSTRAINED-ACTUATION-P0.1"
WARNING = "PRELIMINARY - CURRENT/TORQUE ARCHITECTURE CANDIDATE ONLY - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"

MODELS = {
    "ROBOTIS XH540-W270-R": {
        "family": "XH540", "unit_ma": 2.69, "max_raw": 2047, "default_raw": 2047,
        "candidate_a": 2.5, "stall_nm": 9.9, "stall_a": 4.9, "rpm": 39.0,
        "url": "https://docs.robotis.com/docs/dxl/model_reference/x_series/xh_series/xh540-w270/",
    },
    "ROBOTIS XM540-W270-R": {
        "family": "XM540", "unit_ma": 2.69, "max_raw": 2047, "default_raw": 2047,
        "candidate_a": 2.5, "stall_nm": 10.6, "stall_a": 4.4, "rpm": 30.0,
        "url": "https://docs.robotis.com/docs/dxl/model_reference/x_series/xm_series/xm540-w270/",
    },
    "ROBOTIS XM430-W350-R": {
        "family": "XM430", "unit_ma": 2.69, "max_raw": 1193, "default_raw": 1193,
        "candidate_a": 2.0, "stall_nm": 4.1, "stall_a": 2.3, "rpm": 46.0,
        "url": "https://docs.robotis.com/docs/dxl/model_reference/x_series/xm_series/xm430-w350/",
    },
    "ROBOTIS XC330-T288-T": {
        "family": "XC330", "unit_ma": 1.0, "max_raw": 910, "default_raw": 910,
        "candidate_a": 0.7, "stall_nm": 1.0, "stall_a": 0.88, "rpm": 71.0,
        "url": "https://docs.robotis.com/docs/dxl/model_reference/x_series/xc_series/xc330-t288/",
    },
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, records: list[dict]) -> None:
    if not records:
        raise RuntimeError(f"refusing empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def model_key(candidate: str) -> str:
    for key in MODELS:
        if key in candidate:
            return key
    raise RuntimeError(f"unknown actuator allocation: {candidate}")


def integrate_root(axis_rows: list[dict], bus_rows: list[dict]) -> None:
    status_path = WHOLE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "current_constrained_actuation_package_present": True,
        "current_constrained_axis_count": 25,
        "current_constrained_bus_count": 8,
        "current_candidate_static_screen_pass_count": sum(row["screen_result"] == "PASS" for row in axis_rows),
        "current_candidate_static_screen_not_applicable_count": sum(row["screen_result"] == "NOT APPLICABLE" for row in axis_rows),
        "current_candidate_simultaneous_cap_sum_a": round(sum(float(row["candidate_current_a"]) for row in axis_rows), 6),
        "knee_ratio_current_boundary_correction_present": True,
        "current_policy_released": False,
        "branch_protection_released": False,
        "motion_authority": False,
        "energization_authority": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    readme_path = WHOLE / "README.md"
    text = readme_path.read_text(encoding="utf-8")
    start = "<!-- HR30-CURRENT-CONSTRAINED-P01-README-START -->"
    end = "<!-- HR30-CURRENT-CONSTRAINED-P01-README-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    block = f'''{start}\n## Current-constrained whole-body actuation\n\nThe [current-constrained actuation guide](current-constrained-actuation-p0.1/index.html) binds all 25 axes to candidate Current Limit register values and an eight-bus simultaneous-cap budget. XH/XM540 axes use raw 929 (2.499 A), XM430 axes raw 743 (1.999 A), and XC330 axes raw 700 (0.700 A). A dedicated 2.5:1 knee drive replaces the former 2:1 architecture because the old knee required about 3.07 A to reach its static development screen. All numeric torque comparisons remain linear published-stall endpoint screens, not continuous capability. External current, branch protection, temperature, dynamics and physical validation remain open.\n{end}\n'''
    marker = "<!-- HR30-ASSEMBLY-GUIDE-P01-START -->"
    readme_path.write_text(text.replace(marker, block + marker), encoding="utf-8", newline="\n")

    page_path = WHOLE / "index.html"
    text = page_path.read_text(encoding="utf-8")
    start = "<!-- HR30-CURRENT-CONSTRAINED-P01-START -->"
    end = "<!-- HR30-CURRENT-CONSTRAINED-P01-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    section = f'''{start}<section id="current-policy"><h2>Every joint now has a current ceiling</h2><div class="grid"><article class="card pass"><div class="metric">25 / 25</div><p>Axes have explicit candidate Current Limit values.</p></article><article class="card pass"><div class="metric">2.5:1</div><p>The knee ratio is corrected so its static endpoint screen fits below 3 A.</p></article><article class="card"><div class="metric">{sum(float(row['simultaneous_candidate_cap_a']) for row in bus_rows):.1f} A</div><p>Arithmetic sum of all eight bus caps; not a normal-demand or supply rating.</p></article><article class="card hold"><h3>Physical proof remains open</h3><p>External branch current, connector temperature, protection coordination, continuous torque and gait duty are unvalidated.</p></article></div><p><a href="current-constrained-actuation-p0.1/index.html">Open the current/torque guide</a> · <a href="current-constrained-actuation-p0.1/axis-current-torque-register.csv">25-axis register</a> · <a href="current-constrained-actuation-p0.1/bus-current-budget.csv">bus budget</a>.</p></section>{end}'''
    page_path.write_text(text.replace(marker, section + marker), encoding="utf-8", newline="\n")

    holds_path = WHOLE / "open-holds.csv"
    holds = read_csv(holds_path)
    for hold in holds:
        if hold["hold_id"] == "HR30-P01-H03":
            hold["unresolved_item"] = (
                "All twelve leg axes have static load screens and exact MISUMI candidate drivetrain geometry; all 45 nominal "
                "inter-drive pairs have zero common volume in the installed nominal CAD screen. The knees now use "
                "dedicated 2.5:1 16:40 modules because the former 2:1 design required about 3.07 A at the published "
                "stall-line endpoint, beyond the JST EH 3 A catalogue boundary before application derating. All 25 axes "
                "have candidate internal current registers, but external current, continuous torque, connector temperature, "
                "branch protection, accepted trajectories, regeneration, fall restraint, gait correlation and physical proof remain open."
            )
            break
    else:
        raise RuntimeError("controlled hold HR30-P01-H03 missing")
    write_csv(holds_path, holds)


def render_index(axis_rows: list[dict], bus_rows: list[dict]) -> str:
    family_cards = []
    for model, data in MODELS.items():
        raw = math.floor(data["candidate_a"] * 1000.0 / data["unit_ma"])
        actual = raw * data["unit_ma"] / 1000.0
        family_cards.append(f"<article><h3>{html.escape(data['family'])}</h3><div class='metric'>{actual:.3f} A</div><p>Current Limit raw {raw}; candidate only.</p></article>")
    bus_html = "".join(
        f"<tr><td>{html.escape(row['bus_id'])}</td><td>{row['axis_count']}</td><td>{row['simultaneous_candidate_cap_a']} A</td><td>{html.escape(row['boundary'])}</td></tr>"
        for row in bus_rows
    )
    pass_count = sum(row["screen_result"] == "PASS" for row in axis_rows)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 current-constrained actuation P0.1</title><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#84d8ff;--gold:#f2b91d;--paper:#eef8fe;--line:#9acfe8;--ink:#142a40}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:32px max(18px,calc((100vw - 1220px)/2))}}header,footer{{background:var(--deep);color:white}}h1{{font-size:clamp(38px,6vw,68px);line-height:1.04}}h2{{font-size:clamp(28px,4vw,42px)}}h3{{font-size:22px}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px}}article,.panel{{background:white;border:2px solid var(--line);border-radius:16px;padding:18px}}.metric{{font-size:clamp(30px,5vw,48px);font-weight:900;color:var(--blue)}}.table{{overflow:auto;border:2px solid var(--line);border-radius:14px}}table{{border-collapse:collapse;width:100%;min-width:820px}}th,td{{padding:13px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line)}}th{{background:var(--deep);color:white}}a{{color:#075b9b;font-weight:800}}small{{font-size:14px}}@media(max-width:560px){{body{{font-size:16px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><h1>Current is now allocated before motion.</h1><p>All 25 joints have candidate register values, current-limited endpoint arithmetic and bus totals. The knee transmission was changed where the electrical boundary and the static load screen disagreed.</p></header><main><section><h2>Four actuator-family ceilings</h2><div class="grid">{''.join(family_cards)}</div></section><section><h2>What the screen says</h2><div class="grid"><article><div class="metric">{pass_count}</div><p>nonzero static development screens pass the current-limited published-stall endpoint arithmetic.</p></article><article><div class="metric">2.5:1</div><p>bilateral knee ratio; previous 2:1 candidate rejected for this current boundary.</p></article><article><div class="metric">0</div><p>continuous-torque, thermal, protection or motion approvals.</p></article></div></section><section><h2>Eight physical bus segments</h2><div class="table"><table><thead><tr><th>Bus</th><th>Axes</th><th>Sum of caps</th><th>Boundary</th></tr></thead><tbody>{bus_html}</tbody></table></div></section><section class="panel"><h2>Deterministic local-control rule</h2><p>Torque remains disabled while identity, operating mode, Current Limit, Goal Current, watchdog, temperature and voltage bounds are written and read back. A safety permit transition never creates a motion command; a fresh bounded trajectory command is separately required.</p><p><a href="control-sequence.md">Control sequence</a> · <a href="actuator-control-register.csv">Control-table map</a> · <a href="axis-current-torque-register.csv">Axis calculations</a> · <a href="bus-current-budget.csv">Bus budget</a> · <a href="open-holds.csv">Open evidence</a></p></section></main><footer>{html.escape(WARNING)}</footer></body></html>'''


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    loads = read_csv(WHOLE / "joint-load-screen.csv")
    bus_bindings = read_csv(WHOLE / "actuator-bus-axis-binding.csv")
    bus_for_axis = {row["axis_id"]: row["bus_id"] for row in bus_bindings}
    if len(loads) != 25 or len(bus_for_axis) != 25:
        raise RuntimeError("25-axis source coverage missing")

    control_rows = []
    for model, data in MODELS.items():
        raw = math.floor(data["candidate_a"] * 1000.0 / data["unit_ma"])
        actual = raw * data["unit_ma"] / 1000.0
        control_rows.append({
            "actuator_model": model, "family": data["family"], "operating_mode_address": 11,
            "current_based_position_mode_value": 5, "torque_enable_address": 64,
            "bus_watchdog_address": 98, "bus_watchdog_unit_ms": 20,
            "goal_current_address": 102, "current_limit_address": 38,
            "current_limit_size_bytes": 2, "current_unit_ma_per_raw": f"{data['unit_ma']:.2f}",
            "published_current_limit_max_raw": data["max_raw"], "published_default_raw": data["default_raw"],
            "candidate_current_limit_raw": raw, "candidate_current_a": f"{actual:.6f}",
            "write_condition": "TORQUE DISABLED; EEPROM WRITE; READ-BACK REQUIRED",
            "release_state": "CANDIDATE - EXTERNAL CURRENT/THERMAL/PROTECTION VALIDATION OPEN",
            "authority": "NO CONNECTION, POWERED TEST, MOTION OR ENERGIZATION AUTHORITY", "warning": WARNING,
        })

    axis_rows = []
    bus_sums: dict[str, float] = defaultdict(float)
    for load in loads:
        model = model_key(load["candidate_actuator"])
        data = MODELS[model]
        raw = math.floor(data["candidate_a"] * 1000.0 / data["unit_ma"])
        current_a = raw * data["unit_ma"] / 1000.0
        ratio = float(load["candidate_ratio"])
        efficiency = float(load["assumed_transmission_efficiency"])
        endpoint = data["stall_nm"] * current_a / data["stall_a"] * ratio * efficiency
        development_text = load["development_endpoint_screen_nm"]
        if development_text == "SELECTION REQUIRED" or float(development_text) <= 0:
            screen = "NOT APPLICABLE"
            reserve = "N/A"
        else:
            development = float(development_text)
            screen = "PASS" if endpoint >= development else "FAIL"
            reserve = f"{endpoint / development:.6f}"
        bus_id = bus_for_axis[load["axis_id"]]
        bus_sums[bus_id] += current_a
        axis_rows.append({
            "axis_id": load["axis_id"], "bus_id": bus_id, "actuator_model": model,
            "current_limit_raw_candidate": raw, "candidate_current_a": f"{current_a:.6f}",
            "published_stall_current_a": f"{data['stall_a']:.3f}", "published_stall_torque_nm": f"{data['stall_nm']:.3f}",
            "transmission_ratio": f"{ratio:.3f}", "transmission_efficiency_assumption": f"{efficiency:.3f}",
            "current_limited_linear_endpoint_nm": f"{endpoint:.6f}",
            "development_endpoint_screen_nm": development_text, "endpoint_to_screen_ratio": reserve,
            "screen_result": screen,
            "output_no_load_speed_deg_s": f"{data['rpm'] * 6.0 / ratio:.3f}",
            "connector_catalog_boundary": "JST EH 3 A SERIES BASIS; APPLICATION DERATING/THERMAL PROOF OPEN",
            "calculation_boundary": "LINEAR INTERPOLATION TO PUBLISHED 12 V STALL ENDPOINT; NOT CONTINUOUS TORQUE OR EXTERNAL-CURRENT PROOF",
            "authority": "NO CONNECTION, POWERED TEST, MOTION OR ENERGIZATION AUTHORITY", "warning": WARNING,
        })
    axis_rows.sort(key=lambda row: [item["axis_id"] for item in loads].index(row["axis_id"]))
    failures = [row for row in axis_rows if row["screen_result"] == "FAIL"]
    if failures:
        raise RuntimeError(f"current-constrained static screen failed: {[row['axis_id'] for row in failures]}")

    axes_by_bus: dict[str, list[str]] = defaultdict(list)
    for row in axis_rows:
        axes_by_bus[row["bus_id"]].append(row["axis_id"])
    bus_rows = [{
        "bus_id": bus_id, "axis_count": len(axes_by_bus[bus_id]), "axes": "; ".join(axes_by_bus[bus_id]),
        "simultaneous_candidate_cap_a": f"{bus_sums[bus_id]:.6f}",
        "normal_rms_demand_a": "SELECTION REQUIRED", "regenerative_return_a": "SELECTION REQUIRED",
        "boundary": "ARITHMETIC SUM OF INTERNAL CAPS ONLY; NOT PDU, WIRE, CONNECTOR OR SUPPLY RATING",
        "authority": "NO CONNECTION, POWERED TEST, MOTION OR ENERGIZATION AUTHORITY", "warning": WARNING,
    } for bus_id in sorted(axes_by_bus)]

    source_rows = [{
        "source_id": f"CCS-{index:02d}", "manufacturer": "ROBOTIS", "record": model,
        "official_url": data["url"], "revision_or_date": "ROBOTIS-GIT source revision recorded in repository research; live docs page has no visible revision date",
        "accessed_date": "2026-08-15", "use": "Current Limit, Goal Current, Operating Mode, Torque Enable, Bus Watchdog, current unit/range and published 12 V endpoint",
        "warning": WARNING,
    } for index, (model, data) in enumerate(MODELS.items(), 1)]
    source_rows += [{
        "source_id": "CCS-05", "manufacturer": "JST", "record": "EH connector series",
        "official_url": "https://www.jst-mfg.com/product/pdf/eng/eEH.pdf", "revision_or_date": "live official series PDF; revision/date not stated",
        "accessed_date": "2026-08-15", "use": "3 A AC/DC catalogue boundary at AWG22; application derating still required", "warning": WARNING,
    }, {
        "source_id": "CCS-06", "manufacturer": "MISUMI", "record": "High Torque Timing Pulleys 5GT",
        "official_url": "https://uk.misumi-ec.com/pdf/fa/p1_1117.pdf", "revision_or_date": "current official catalogue page available 2026-08-15; document revision not stated",
        "accessed_date": "2026-08-15", "use": "GPA16GT5090 P round-hole-plus-tap supports 10 mm bore for dedicated knee candidate", "warning": WARNING,
    }]

    holds = [
        ("CCA-H01", "External branch current waveform versus internal Present Current and Current Limit", "guarded instrumented actuator fixture across startup, reversal, stall, disable and regeneration"),
        ("CCA-H02", "JST EH contact/cable temperature rise and voltage drop", "received harness, actual routing/bundling, ambient extremes and representative duty"),
        ("CCA-H03", "Continuous torque and thermal envelope for every actuator family", "manufacturer-approved data or project dynamometer map with winding/case limits"),
        ("CCA-H04", "PDU branch fuse/eFuse values, conductors and fault clearing", "available fault current, lengths, connector limits, inrush, duty, ambient, bundling and jurisdiction"),
        ("CCA-H05", "2.5:1 knee belt, pulley, adapter, shaft and bearing capacity", "received parts, tension calculation, tooth load, fatigue, fit/runout and physical proof"),
        ("CCA-H06", "Eight-bus communication timing and watchdog values", "25-axis worst-case cycle timing, fault injection and stop-time validation"),
        ("CCA-H07", "Motion trajectories and simultaneous current demand", "accepted standing/transfer/step trajectories with synchronized current, temperature and voltage data"),
        ("CCA-H08", "Regenerative-energy path and overvoltage behavior", "four-quadrant test evidence and selected absorption/clamp architecture"),
        ("CCA-H09", "Qualified electrical, controls and functional-safety review", "signed review against as-built configuration and applicable requirements"),
    ]
    hold_rows = [{"hold_id": key, "unresolved_item": item, "evidence_required": evidence, "state": "OPEN", "authority": "NO CONNECTION, POWERED TEST, MOTION OR ENERGIZATION AUTHORITY", "warning": WARNING} for key, item, evidence in holds]

    write_csv(OUT / "actuator-control-register.csv", control_rows)
    write_csv(OUT / "axis-current-torque-register.csv", axis_rows)
    write_csv(OUT / "bus-current-budget.csv", bus_rows)
    write_csv(OUT / "source-register.csv", source_rows)
    write_csv(OUT / "open-holds.csv", hold_rows)
    (OUT / "control-sequence.md").write_text(f"""# Deterministic current-constrained control sequence\n\n**{WARNING}**\n\n1. Keep actuator power interrupted and Torque Enable = 0.\n2. Verify the physical bus, actuator model, firmware, unique ID and configured baud rate against the configuration record.\n3. With torque disabled, write Operating Mode 5 only where the exact model supports Current-based Position Control; read it back.\n4. Write the model-family Current Limit candidate from `actuator-control-register.csv`; read it back twice. Any mismatch latches a fault.\n5. Write Goal Current no higher than the approved per-axis candidate; read it back. This value may be reduced by the deterministic local controller but never increased by a conversational agent.\n6. Configure the Bus Watchdog only after measured cycle-time evidence establishes a bounded value. Until then the value is SELECTION REQUIRED and no motion is authorized.\n7. Verify voltage, temperature, hardware error, position limits and output-encoder plausibility before any torque-enable request.\n8. A safety-permit transition only permits the local state machine to consider torque enable. It never creates a position, velocity or current command.\n9. Require a fresh, bounded trajectory command issued after the permit transition. High-level OpenAI action requests are schema-checked and converted locally; they never write actuator registers directly.\n10. During motion, re-read Current Limit, Goal Current, watchdog, voltage, temperature, hardware error, present current and encoder agreement. Drift or stale communication commands torque-off and removes the motion permit.\n11. Reset requires the initiating command to be absent, all faults acknowledged, and another fresh trajectory command. E-stop release or reset cannot resume the previous command.\n\nThis sequence is an architecture definition. Exact watchdog time, stop time, temperature limits, current telemetry tolerances and fault reactions require physical validation and qualified review.\n""", encoding="utf-8", newline="\n")
    status = {
        "identifier": IDENTIFIER, "axis_count": len(axis_rows), "bus_count": len(bus_rows),
        "model_family_count": len(control_rows), "nonzero_static_screen_pass_count": sum(row["screen_result"] == "PASS" for row in axis_rows),
        "static_screen_not_applicable_count": sum(row["screen_result"] == "NOT APPLICABLE" for row in axis_rows),
        "simultaneous_candidate_cap_sum_a": round(sum(float(row["candidate_current_a"]) for row in axis_rows), 6),
        "knee_ratio": 2.5, "knee_ratio_changed_from": 2.0, "old_knee_required_endpoint_current_a": 3.066,
        "published_stall_used_as_continuous_rating": False, "external_current_validated": False,
        "connector_thermal_validated": False, "branch_protection_released": False, "continuous_torque_validated": False,
        "current_policy_released": False, "connection_authority": False, "powered_test_authority": False,
        "motion_authority": False, "energization_authority": False, "warning": WARNING,
    }
    (OUT / "status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(f"# HR-30 current-constrained actuation P0.1\n\n**{WARNING}**\n\nAll 25 axes now have candidate current-register values, current-limited endpoint arithmetic and eight-bus current sums. The bilateral knee ratio changes from 2.0:1 to 2.5:1 because the former architecture required about 3.07 A to reach its static development screen. This is a coherent design correction, not a released current limit, fuse value, continuous-torque rating or motion approval.\n", encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(render_index(axis_rows, bus_rows), encoding="utf-8", newline="\n")
    shutil.copy2(Path(__file__), OUT / "current-constrained-actuation-source.py")
    files = sorted(path for path in OUT.rglob("*") if path.is_file() and path.name != "file-manifest.csv")
    write_csv(OUT / "file-manifest.csv", [{"path": path.relative_to(OUT).as_posix(), "bytes": path.stat().st_size, "sha256": sha(path), "warning": WARNING} for path in files])
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    shutil.copytree(OUT, RELEASE)
    integrate_root(axis_rows, bus_rows)
    import generate_hr30_system_package_p01 as system
    system.refresh_manifest_and_release()
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
