"""Generate the HR-V0 watchdog-gated SR1 supply correction package."""

from __future__ import annotations

import csv
import html
import json
import shutil
from pathlib import Path

import generate_hr_v0_watchdog_ccf as r86


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "safety" / "hr-v0-watchdog-supply-gate-p0.1"
CANONICAL_FMEA = ROOT / "safety" / "hr-v0-watchdog-boundary-fmea.csv"
WARNING = "PRELIMINARY - ANALYSIS AND UNEXECUTED TEST CONTROL ONLY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"
REVISION = "HR-V0-WD-SUPPLY-P0.1"
CONFIGURATION = "Electrical V3-P1.13 / PCB-P0.7 / HR-V0-CP-P0.5"


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


PATHS = [
    ("SGP-001", "SF-01 channel 1", "SR1:S11 -> S0:R-1/R-2 NC -> SR1:S12", "direct; no KWD terminal"),
    ("SGP-002", "SF-01 channel 2", "SR1:S21 -> S0:L-1/L-2 NC -> SR1:S22", "direct; no KWD terminal"),
    ("SGP-003", "diagnostic gate stage 1", "SAFETY_24V -> KWD1:11/14 -> WD_SUPPLY_INTERMEDIATE", "ordinary diagnostic; zero safety credit"),
    ("SGP-004", "diagnostic gate stage 2", "WD_SUPPLY_INTERMEDIATE -> KWD2:11/14 -> SR1_A1_WD_GATED", "ordinary diagnostic; zero safety credit"),
    ("SGP-005", "SR1 supply", "SR1_A1_WD_GATED -> SR1:A1; SR1:A2 -> SAFETY_0V", "contact duty, protection and recovery open"),
    ("SGP-006", "KWD1 coil", "SAFETY_24V -> KWD1:A1/A2 -> WD1_COIL_N -> UDRV1", "ordinary diagnostic"),
    ("SGP-007", "KWD2 coil", "SAFETY_24V -> KWD2:A1/A2 -> WD2_COIL_N -> UDRV2", "ordinary diagnostic"),
    ("SGP-008", "KWD1 feedback", "SAFETY_24V -> KWD1:21/22 -> WD1_NC_24V -> UFB1", "read-only intent; proof open"),
    ("SGP-009", "KWD2 feedback", "SAFETY_24V -> KWD2:21/22 -> WD2_NC_24V -> UFB1", "read-only intent; proof open"),
    ("SGP-010", "SR1 reset", "SR1:S12 -> S1 -> SR1:S34", "physical monitored RESET; received mapping/test open"),
    ("SGP-011", "SRA1 ARM/EDM", "SRA1:S12 -> S2 -> K1:21/22 -> K2:21/22 -> SRA1:S34", "physical ARM and EDM; proof open"),
    ("SGP-012", "restart sequence", "heartbeat loss -> SR1 supply loss -> RESET -> ARM -> fresh trajectory", "not executed"),
    ("SGP-013", "panel routing", "P0.5 SGR-001..SGR-012", "no conductor or barrier release"),
    ("SGP-014", "configuration boundary", CONFIGURATION, "hash/as-built identity required"),
]

OPTIONS = [
    ("OPT-001", "KWD contacts in SR1 input returns", "REJECTED", "A1/21-to-14 fault can inject downstream of S0"),
    ("OPT-002", "KWD contacts only in reset/start loop", "NOT SELECTED", "may not drop an already latched relay; manufacturer validation absent"),
    ("OPT-003", "KWD contacts only downstream at contactor coils", "REJECTED", "restored heartbeat could repower coils while upstream eligibility remains latched"),
    ("OPT-004", "KWD contacts series-gate SR1:A1; S0 direct", "SELECTED CANDIDATE", "removes encoded KWD-to-E-stop-return injection; physical/qualified proof open"),
]

LOADS = [
    ("LOAD-001", "PNOZ s4 750104 steady input", "2.5 W / 24 V", "0.10417 A", "catalog arithmetic only"),
    ("LOAD-002", "PNOZ s4 750104 startup pulse", "manufacturer maximum A1 pulse", "0.5 A for 5 ms", "catalog value; received measurement open"),
    ("LOAD-003", "Phoenix 2967060 minimum switching", "manufacturer catalog", "10 mA at 5 V", "does not prove electronic-load suitability"),
    ("LOAD-004", "Phoenix 2967060 limiting continuous current", "manufacturer catalog", "6 A", "terminal/ambient/application derating open"),
    ("LOAD-005", "Phoenix 2967060 inrush statement", "manufacturer catalog", "15 A for 300 ms", "load class/endurance coordination open"),
    ("LOAD-006", "steady-current margin screen", "6 A / 0.10417 A", "57.6x nominal", "not a release criterion"),
    ("LOAD-007", "application conclusion", "electronic supply load plus switching cycles", "SELECTION REQUIRED", "manufacturer confirmation, protection and physical endurance test required"),
]

SEPARATION = [
    ("SEP-001", "KWD gate versus SR1:S11/S12", "separate duct/terminal region; inspect and fault-test"),
    ("SEP-002", "KWD gate versus SR1:S21/S22", "separate duct/terminal region; inspect and fault-test"),
    ("SEP-003", "KWD gate versus RESET S1/S34", "no shared unprotected route"),
    ("SEP-004", "KWD gate versus ARM/EDM", "no shared unprotected route"),
    ("SEP-005", "KWD1 stage versus KWD2 stage", "controlled terminals, covers, ferrules and inspection"),
    ("SEP-006", "KWD coils versus input returns", "segregated route and short matrix"),
    ("SEP-007", "KWD feedback versus input returns", "segregated route and read-only proof"),
    ("SEP-008", "watchdog PCB/test access versus safety wiring", "barrier/route and unpowered fixture"),
    ("SEP-009", "SAFETY_24V distribution", "fault-current and branch-protection evidence"),
    ("SEP-010", "SAFETY_0V distribution", "open/high-impedance/brownout evidence"),
    ("SEP-011", "enclosure contamination/workmanship", "environment, cleaning, strand and torque controls"),
    ("SEP-012", "configuration identity", "commit, ECAD, PCB, panel, harness and firmware hashes"),
]

DECISIONS = [
    ("HOLD-001", "KWD contact application to PNOZ A1 electronic load", "manufacturer confirmation plus qualified review"),
    ("HOLD-002", "contact switching/endurance cycle target", "defined mission profile and endurance evidence"),
    ("HOLD-003", "gate-branch fault protection", "fault current, conductor, terminal, fuse and coordination study"),
    ("HOLD-004", "brownout/dropout/recovery window", "measured voltage/time behavior and acceptance limits"),
    ("HOLD-005", "manual reset behavior after gated A1 restore", "received-article test for every relevant state"),
    ("HOLD-006", "physical separation/protected wiring", "released drawing and inspected as-built evidence"),
    ("HOLD-007", "KWD internal/pole-to-pole fault consequences", "manufacturer evidence and qualified fault analysis"),
    ("HOLD-008", "functional-safety allocation", "SRS, PLr/SIL, category, CCF and validation by qualified reviewer"),
    ("HOLD-009", "fault-injection fixture and limits", "approved no-load fixture, instruments and numerical criteria"),
    ("HOLD-010", "motion restart prevention", "hardware/firmware integration test proving fresh trajectory required"),
]

SOURCES = [
    ("SRC-001", "Project Button Electrical V3-P1.13", "electrical/kicad/project-button-v3/", "native connectivity"),
    ("SRC-002", "HR-V0 control panel P0.5", "electrical/panel/hr-v0-control-panel-p0.5/", "held physical-route controls"),
    ("SRC-003", "Pilz PNOZ s4 manual 21396-EN-23", "https://www.pilz.com/download/open/OM_PNOZ_s4_21396-EN-23.pdf", "terminal/start/power data; Rev 23, 2026-02"),
    ("SRC-004", "Pilz 750104 product page", "https://www.pilz.com/en-INT/eshop/Relay-modules/Safety-relays-protection-relays/PNOZsigma-safety-relays/PNOZ-s4-24VDC-3-n-o-1-n-c/p/750104", "current product identity; rechecked 2026-08-08"),
    ("SRC-005", "Phoenix Contact 2967060 product PDF", "https://www.phoenixcontact.com/en-pc/products/relay-module-plc-rsc-24dc-21-21-2967060?type=pdf", "contact/coil catalog; data-maintenance 2026-04-01"),
    ("SRC-006", "ISO 13849-1:2023 official record", "https://www.iso.org/standard/73481.html", "method identity only; controlled standard required"),
    ("SRC-007", "R86 dependent-failure package", "safety/hr-v0-watchdog-ccf-p0.1/", "superseded topology finding and retained fault set"),
    ("SRC-008", "Canonical watchdog FMEA", "safety/hr-v0-watchdog-boundary-fmea.csv", "32 controlled-open cases"),
]


CURRENT_OVERRIDES = {
    "WDF-005": ("KWD1 contact 11-14", "welded/shorted closed", "diagnostic gate stage 1 defeated", "direct S0 loops remain encoded; physical proof open", "FI-006;FI-019", "conditional"),
    "WDF-006": ("KWD1 and KWD2 contacts 11-14", "both welded/bypassed", "DF-01 completely lost and SR1 A1 remains supplied", "direct S0 loops remain encoded; manual restart and physical proof open", "FI-007;FI-020", "conditional"),
    "WDF-012": ("KWD1 internal boundary", "A1 or 21 short to terminal 14", "KWD1 gate stage bypassed or WD_SUPPLY_INTERMEDIATE forced", "no direct S0-return bypass in P1.13; physical separation and qualified proof open", "FI-024", "conditional"),
    "WDF-013": ("KWD2 internal boundary", "A1 or 21 short to terminal 14", "SR1_A1_WD_GATED may be forced", "no direct S0-return bypass in P1.13; direct inputs still require qualified proof", "FI-025", "conditional"),
    "WDF-014": ("KWD1 pole-to-pole boundary", "terminal 21 short to terminal 14", "KWD1 gate stage bypassed", "no direct S0-return bypass in P1.13; internal-fault proof open", "FI-024", "conditional"),
    "WDF-015": ("KWD2 pole-to-pole boundary", "terminal 21 short to terminal 14", "SR1 A1 gate may be bypassed", "no direct S0-return bypass in P1.13; internal-fault proof open", "FI-025", "conditional"),
    "WDF-016": ("adjacent KWD modules/panel wiring", "common bridge from SAFETY_24V to SR1_A1_WD_GATED", "diagnostic supply gate defeated", "direct S0 loops remain encoded; physical bridge matrix open", "FI-026", "conditional"),
    "WDF-030": ("RESET/ARM conductor proximity", "watchdog gate conductor bridges S1/S2/EDM return", "restart sequence can be corrupted", "SF-03 impairment remains possible; routing and fault injection open", "FI-022;FI-026", "no"),
}


def canonical_fmea() -> list[dict[str, str]]:
    result = []
    for fid, item, mode, df_effect, sf_effect, verification in r86.FAILURES:
        safe = "conditional" if fid in {"WDF-001", "WDF-007"} else "no"
        if fid in CURRENT_OVERRIDES:
            item, mode, df_effect, sf_effect, verification, safe = CURRENT_OVERRIDES[fid]
        result.append({
            "fmea_id": fid,
            "item_or_boundary": item,
            "failure_mode": mode,
            "local_effect": df_effect,
            "df01_effect": df_effect,
            "sf01_effect": sf_effect,
            "sf03_effect": sf_effect,
            "safe_by_design": safe,
            "required_control": "Configuration-bound analysis, physical segregation and controlled fault verification; no safety credit to diagnostic success",
            "verification": verification,
            "status": "open",
        })
    return result


def dict_rows(items, headers):
    return [{**dict(zip(headers, item)), "warning": WARNING} for item in items]


def table(title: str, rows: list[dict[str, str]]) -> str:
    heads = [key for key in rows[0] if key != "warning"]
    th = "".join(f"<th>{html.escape(h.replace('_', ' ').title())}</th>" for h in heads)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(row[h])}</td>" for h in heads) + "</tr>" for row in rows)
    return f'<section><h2>{html.escape(title)}</h2><div class="scroll"><table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div></section>'


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    path_rows = dict_rows(PATHS, ("path_id", "function", "exact_path", "disposition"))
    option_rows = dict_rows(OPTIONS, ("option_id", "architecture", "decision", "basis"))
    load_rows = dict_rows(LOADS, ("screen_id", "parameter", "basis", "result", "limitation"))
    separation_rows = dict_rows(SEPARATION, ("control_id", "boundary", "required_evidence"))
    for row in separation_rows:
        row.update(release_state="NOT RELEASED", execution_state="NOT EXECUTED")
    decision_rows = dict_rows(DECISIONS, ("hold_id", "unresolved_selection", "closure_evidence"))
    for row in decision_rows:
        row.update(state="SELECTION REQUIRED")
    source_rows = dict_rows(SOURCES, ("source_id", "document", "url_or_path", "use_revision_boundary"))
    fmea = canonical_fmea()
    fault_rows = []
    for case_id, injection, acceptance in r86.CASES:
        if case_id in {"FI-024", "FI-025", "FI-026"}:
            acceptance = "direct S0 paths remain effective with supply gate defeated; no test until qualified method"
        fault_rows.append({"case_id": case_id, "injection_or_analysis": injection, "minimum_acceptance_boundary": acceptance, "fixture": "SELECTION REQUIRED", "numerical_limit": "SELECTION REQUIRED", "execution_state": "NOT EXECUTED", "authorization": "NOT AUTHORIZED", "warning": WARNING})
    files = {
        "exact-path-register.csv": path_rows,
        "topology-option-register.csv": option_rows,
        "contact-load-screen.csv": load_rows,
        "separation-control-register.csv": separation_rows,
        "open-decision-register.csv": decision_rows,
        "source-register.csv": source_rows,
        "failure-mode-register.csv": [{**row, "warning": WARNING} for row in fmea],
        "fault-injection-matrix.csv": fault_rows,
    }
    for name, rows in files.items():
        write_csv(OUT / name, rows)
    write_csv(CANONICAL_FMEA, fmea)
    status = {
        "revision": REVISION,
        "configuration": CONFIGURATION,
        "path_count": len(path_rows),
        "fmea_count": len(fmea),
        "fault_case_count": len(fault_rows),
        "separation_control_count": len(separation_rows),
        "open_decision_count": len(decision_rows),
        "df01_safety_credit": "ZERO",
        "encoded_internal_kwd_to_estop_return_path_removed": True,
        "physical_noninterference_proved": False,
        "physical_test_executed": False,
        "qualified_review_executed": False,
        "energization_authorized": False,
        "warning": WARNING,
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="760" viewBox="0 0 1600 760" role="img"><style>text{{font-family:Arial,sans-serif;fill:#082b4c;font-size:18px}}.title{{font-size:34px;font-weight:800}}.head{{font-size:24px;font-weight:800}}.warn{{fill:#7a3500;font-size:20px;font-weight:800}}.s{{fill:#e4f6ee;stroke:#17663b;stroke-width:4}}.d{{fill:#fff3cc;stroke:#c48700;stroke-width:4}}</style><rect width="1600" height="760" fill="#e7f6ff"/><text x="50" y="58" class="title">HR-V0 watchdog supply-gate correction</text><text x="50" y="98" class="warn">{WARNING}</text><rect x="50" y="155" width="650" height="235" rx="18" class="s"/><text x="80" y="205" class="head">Credited candidate path: direct E-stop</text><text x="80" y="260">SR1:S11 - S0 channel 1 NC - SR1:S12</text><text x="80" y="305">SR1:S21 - S0 channel 2 NC - SR1:S22</text><text x="80" y="350">No KWD terminal in either input return</text><rect x="790" y="155" width="760" height="235" rx="18" class="d"/><text x="820" y="205" class="head">Ordinary diagnostic gate: ZERO SAFETY CREDIT</text><text x="820" y="260">SAFETY_24V - KWD1:11/14 - KWD2:11/14 - SR1:A1</text><text x="820" y="305">A welded/shorted contact can defeat DF-01 availability</text><text x="820" y="350">It does not connect directly to S0 returns in P1.13</text><rect x="50" y="455" width="1500" height="230" rx="18" fill="#f5fbff" stroke="#0b4f8a" stroke-width="3"/><text x="80" y="505" class="head">Release boundary</text><text x="80" y="555">Encoded internal injection path removed. Physical noninterference: NOT PROVED.</text><text x="80" y="600">Contact duty, protection, routing, brownout, reset recovery and fault injection: OPEN.</text><text x="80" y="645" class="warn">NOT APPROVED FOR FABRICATION, ENERGIZATION OR MOTION.</text></svg>'''
    (OUT / "watchdog-supply-gate.svg").write_text(svg, encoding="utf-8")
    sections = [
        table("Exact paths", path_rows), table("Architecture options", option_rows), table("Contact-load screen", load_rows),
        table("Open decisions", decision_rows), table("Separation controls", separation_rows), table("Fault cases", fault_rows),
    ]
    page = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{REVISION}</title><style>:root{{--sky:#e7f6ff;--blue:#082b4c;--gold:#f5b82e}}*{{box-sizing:border-box}}body{{margin:0;background:var(--sky);color:var(--blue);font:16px/1.5 system-ui,sans-serif}}header,main{{max-width:1500px;margin:auto;padding:28px}}header{{background:#fff;border-bottom:6px solid var(--gold)}}h1{{font-size:clamp(30px,4vw,52px);margin:.2em 0}}h2{{font-size:28px}}.warning{{font-size:18px;font-weight:800;color:#7a3500}}.summary{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px}}.card,section{{background:#fff;border:2px solid #0b4f8a;border-radius:14px;padding:20px;margin:20px 0}}.card strong{{display:block;font-size:28px}}input{{font:inherit;width:100%;padding:14px;border:2px solid #0b4f8a;border-radius:8px}}.scroll{{overflow:auto}}table{{border-collapse:collapse;width:100%;min-width:900px}}th,td{{border:1px solid #7795ad;padding:12px;vertical-align:top;text-align:left;font-size:16px}}th{{background:#d6efff}}img{{max-width:100%;height:auto}}@media(max-width:700px){{header,main{{padding:18px}}}}</style><header><p class="warning">{WARNING}</p><h1>Watchdog-gated SR1 supply correction</h1><p>{CONFIGURATION}</p></header><main><div class="summary"><div class="card"><strong>0</strong>safety credit assigned to DF-01</div><div class="card"><strong>32</strong>open failure modes</div><div class="card"><strong>28</strong>unexecuted fault cases</div><div class="card"><strong>10</strong>release holds</div></div><section><h2>What changed</h2><p>The two E-stop channels now connect directly to SR1. KWD1 and KWD2 series-gate only SR1:A1. This removes the source-encoded internal KWD-to-E-stop-return injection path found in R86. It does not prove the physical build, safety allocation, contact application, recovery sequence or fault response.</p><img src="watchdog-supply-gate.svg" alt="Direct E-stop paths separated from ordinary watchdog supply gate"></section><label for="filter"><strong>Filter all tables</strong></label><input id="filter" placeholder="Type a net, terminal, hold or fault ID">{''.join(sections)}</main><script>const q=document.querySelector('#filter');q.addEventListener('input',()=>{{const s=q.value.toLowerCase();document.querySelectorAll('tbody tr').forEach(r=>r.hidden=!r.textContent.toLowerCase().includes(s))}});</script></html>'''
    (OUT / "index.html").write_text(page, encoding="utf-8")
    print(f"Generated {REVISION}: {len(path_rows)} paths, {len(fmea)} open FMEA cases, {len(fault_rows)} unexecuted fault cases")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
