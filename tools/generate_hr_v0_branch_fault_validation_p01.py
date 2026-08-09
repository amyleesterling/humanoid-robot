#!/usr/bin/env python3
"""Generate the fail-closed HR-V0 branch-fault validation package.

This generator creates planning and blank evidence artifacts only. It does not
authorize a test, select protection values, or record physical results.
"""

from __future__ import annotations

import csv
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WARNING = (
    "PRELIMINARY - NOT APPROVED FOR FABRICATION, ASSEMBLY, CONNECTION, "
    "MOTION, OR ENERGIZATION"
)

MATRIX_PATH = ROOT / "electrical" / "hr-v0-branch-fault-matrix-p0.1.csv"
FORM_PATH = ROOT / "tests" / "forms" / "hr-v0-branch-fault-validation-template.csv"
DOC_PATH = ROOT / "docs" / "hr-v0-branch-fault-validation-p0.1.md"
WEB_DIR = ROOT / "release" / "hr-v0" / "branch-fault-validation-p0.1"
WEB_PATH = WEB_DIR / "index.html"

FIELDS = [
    "case_id", "stage", "circuit", "references", "nets", "source_state",
    "injection_or_action", "required_monitors", "acceptance_basis",
    "mandatory_prerequisites", "execution_state", "warning",
]


def case(case_id: str, stage: str, circuit: str, references: str, nets: str,
         source_state: str, action: str, monitors: str, acceptance: str,
         prerequisites: str) -> dict[str, str]:
    return {
        "case_id": case_id,
        "stage": stage,
        "circuit": circuit,
        "references": references,
        "nets": nets,
        "source_state": source_state,
        "injection_or_action": action,
        "required_monitors": monitors,
        "acceptance_basis": acceptance,
        "mandatory_prerequisites": prerequisites,
        "execution_state": "NOT EXECUTED",
        "warning": WARNING,
    }


CASES = [
    case("BF-001", "A - UNPOWERED", "U2D2 VDD exclusion", "U1 TTL-2",
         "INTENTIONALLY_UNUSED_U2D2_VDD", "ALL SOURCES PHYSICALLY ABSENT",
         "Inspect and continuity-test the U2D2 VDD position; no contact or copper path may be present.",
         "four-wire resistance/continuity record; connector photos",
         "No conductive path to ACT_12V_BUS or J1_VDD/J2_VDD/J3_VDD; instrument threshold is SELECTION REQUIRED.",
         "Received U2D2 and released harness article; calibrated meter; signed unpowered test authorization."),
    case("BF-002", "A - UNPOWERED", "Controller-cable VDD omission", "INJ1 CTRL:2; JC1:2",
         "NO NET / VDD OMITTED", "ALL SOURCES PHYSICALLY ABSENT",
         "Inspect both cavity-2 positions and prove the custom controller cable contains no VDD contact or conductor.",
         "connector microscopy/photos; end-to-end continuity matrix",
         "Both cavity-2 positions are empty and isolated from all VDD rails; threshold is SELECTION REQUIRED.",
         "Exact received housings/contacts/tooling; released harness drawing; crimp inspection acceptance."),
    case("BF-003", "A - UNPOWERED", "Branch-1 isolation", "F1; INJ1 PWR1/ACT1; J1",
         "ACT_12V_BUS; J1_VDD; ACT_0V_PE_BONDED", "ALL SOURCES PHYSICALLY ABSENT",
         "Remove F1 and map continuity from J1 pin 2 to the common bus and the other branch VDD pins.",
         "four-wire resistance matrix; fuse-position photos",
         "J1_VDD is open from ACT_12V_BUS, J2_VDD and J3_VDD while the common return remains as designed.",
         "Exact assembled distribution; accepted INJ1 first article; selected holder and conductor identities."),
    case("BF-004", "A - UNPOWERED", "Branch-2 isolation", "F2; INJ1 PWR2/ACT2; J2",
         "ACT_12V_BUS; J2_VDD; ACT_0V_PE_BONDED", "ALL SOURCES PHYSICALLY ABSENT",
         "Remove F2 and map continuity from J2 pin 2 to the common bus and the other branch VDD pins.",
         "four-wire resistance matrix; fuse-position photos",
         "J2_VDD is open from ACT_12V_BUS, J1_VDD and J3_VDD while the common return remains as designed.",
         "Exact assembled distribution; accepted INJ1 first article; selected holder and conductor identities."),
    case("BF-005", "A - UNPOWERED", "Branch-3 isolation", "F3; INJ1 PWR3/ACT3; J3",
         "ACT_12V_BUS; J3_VDD; ACT_0V_PE_BONDED", "ALL SOURCES PHYSICALLY ABSENT",
         "Remove F3 and map continuity from J3 pin 2 to the common bus and the other branch VDD pins.",
         "four-wire resistance matrix; fuse-position photos",
         "J3_VDD is open from ACT_12V_BUS, J1_VDD and J2_VDD while the common return remains as designed.",
         "Exact assembled distribution; accepted INJ1 first article; selected holder and conductor identities."),
    case("BF-006", "A - UNPOWERED", "TTL/data isolation", "U1 TTL-3; INJ1 CTRL:3/ACT1:3/ACT2:3/ACT3:3; J1/J2/J3 pin 3",
         "DXL_TTL_DATA", "ALL SOURCES PHYSICALLY ABSENT",
         "Map the intended shared data path and test isolation from every VDD net and enclosure/frame.",
         "continuity/insulation matrix; connector pin photos",
         "Only intended DXL_TTL_DATA endpoints are continuous; isolation thresholds are SELECTION REQUIRED.",
         "Released harness topology; grounding disposition; accepted test voltage that cannot damage electronics."),
    case("BF-007", "A - UNPOWERED", "Main interruption chain", "F0; SD1; KP1; KP2",
         "ACT_12V_RAW; ACT_12V_FUSED; K1_P1_IN; K1_OUT; ACT_12V_BUS", "ALL SOURCES PHYSICALLY ABSENT",
         "Prove each deliberate open (F0 removed, SD1 open, K1 open, K2 open) interrupts the positive path.",
         "four-wire continuity matrix at each deliberate-open state; photos",
         "Each deliberate open independently removes continuity to ACT_12V_BUS; no alternate positive path exists.",
         "Exact received contactors/disconnect/holders; accepted pole mapping; point-to-point inspection complete."),
    case("BF-008", "A - UNPOWERED", "Coil-branch isolation", "FSR1; FSR2; K1 A1/A2; K2 A1/A2",
         "SRA1_K1_RAW; K1_A1; SRA1_K2_RAW; K2_A1; SAFETY_0V", "ALL SOURCES PHYSICALLY ABSENT",
         "Remove each coil fuse link in turn and map isolation plus absence of crossfeed between K1 and K2 commands.",
         "continuity matrix; coil-resistance record; fuse-position photos",
         "The removed branch cannot energize its coil and cannot source the other branch; limits are SELECTION REQUIRED.",
         "Exact fuse links/holders and received coil identities; coil suppression topology accepted."),
    case("BF-009", "B - LIMITED ENERGY", "FSR1 open response", "FSR1; K1; SRA1",
         "SRA1_K1_RAW; K1_A1; K1_STATUS", "SEPARATE CURRENT-LIMITED 24 V FIXTURE ONLY",
         "Command an otherwise eligible state with FSR1 removed; no robot actuator source is present.",
         "K1 coil voltage/current; K1 main state; K1_STATUS; reset/permit state",
         "K1 remains de-energized; no automatic restart or motion command is generated; numeric limits are SELECTION REQUIRED.",
         "Qualified low-energy fixture plan; selected FSR1; accepted coil application; calibrated isolated monitors."),
    case("BF-010", "B - LIMITED ENERGY", "FSR2 open response", "FSR2; K2; SRA1",
         "SRA1_K2_RAW; K2_A1; K2_STATUS", "SEPARATE CURRENT-LIMITED 24 V FIXTURE ONLY",
         "Command an otherwise eligible state with FSR2 removed; no robot actuator source is present.",
         "K2 coil voltage/current; K2 main state; K2_STATUS; reset/permit state",
         "K2 remains de-energized; no automatic restart or motion command is generated; numeric limits are SELECTION REQUIRED.",
         "Qualified low-energy fixture plan; selected FSR2; accepted coil application; calibrated isolated monitors."),
    case("BF-011", "B - LIMITED ENERGY", "K1 feedback discrepancy", "K1 terminals 21/22 and 13/14; XT1-05",
         "EDM_K1_OUT; K1_STATUS", "SEPARATE CURRENT-LIMITED 24 V FIXTURE ONLY",
         "Inject an accepted K1 auxiliary/mirror-contact discrepancy without modifying released hardware.",
         "EDM chain; K1_STATUS; safety-relay state; reset acceptance; watchdog permit",
         "Restart is inhibited, actuator-power eligibility is denied, and clearing the injection alone cannot command motion.",
         "Qualified injection method; contact classification accepted; reset/EDM safety requirements allocated."),
    case("BF-012", "B - LIMITED ENERGY", "K2 feedback discrepancy", "K2 terminals 21/22 and 13/14; XT1-06",
         "EDM_K1_OUT; K2_STATUS", "SEPARATE CURRENT-LIMITED 24 V FIXTURE ONLY",
         "Inject an accepted K2 auxiliary/mirror-contact discrepancy without modifying released hardware.",
         "EDM chain; K2_STATUS; safety-relay state; reset acceptance; watchdog permit",
         "Restart is inhibited, actuator-power eligibility is denied, and clearing the injection alone cannot command motion.",
         "Qualified injection method; contact classification accepted; reset/EDM safety requirements allocated."),
    case("BF-013", "B - LIMITED ENERGY", "TTL-to-VDD miswire", "INJ1/J1/J2/J3 pins 2-3",
         "DXL_TTL_DATA; J1_VDD; J2_VDD; J3_VDD", "SEPARATE DAMAGE-LIMITED INTERFACE FIXTURE ONLY",
         "Apply the approved miswire emulator between DATA and one VDD output in turn; no actuator is connected.",
         "fixture source current; DATA voltage; all VDD rails; U2D2 port state",
         "Energy stays within accepted fixture/component limits, no unintended VDD reaches U1, and the fault is detected before reuse.",
         "Damage-energy bound; sacrificial interface article; U2D2 manufacturer/application disposition; qualified plan."),
    case("BF-014", "C - GUARDED FAULT FIXTURE", "Branch-1 downstream short", "F1; INJ1 PWR1/ACT1; J1 pin 2",
         "ACT_12V_BUS; J1_VDD; ACT_0V_PE_BONDED", "PROGRAMMABLE CURRENT-LIMITED SOURCE IN GUARDED FIXTURE; NO ACTUATOR",
         "Close a rated remote fault element from J1_VDD to return at the released worst-case branch impedance.",
         "bidirectional source/branch current; source and branch voltage; fuse state; conductor/connector/holder temperatures",
         "Selected protection clears or source limitation holds before any selected conductor/connector/holder limit; no damage or cross-branch energization.",
         "EG-014 coordination accepted; exact F1/harness/connector selected; fault energy analysis; remote guarded fixture; qualified authorization."),
    case("BF-015", "C - GUARDED FAULT FIXTURE", "Branch-2 downstream short", "F2; INJ1 PWR2/ACT2; J2 pin 2",
         "ACT_12V_BUS; J2_VDD; ACT_0V_PE_BONDED", "PROGRAMMABLE CURRENT-LIMITED SOURCE IN GUARDED FIXTURE; NO ACTUATOR",
         "Close a rated remote fault element from J2_VDD to return at the released worst-case branch impedance.",
         "bidirectional source/branch current; source and branch voltage; fuse state; conductor/connector/holder temperatures",
         "Selected protection clears or source limitation holds before any selected conductor/connector/holder limit; no damage or cross-branch energization.",
         "EG-014 coordination accepted; exact F2/harness/connector selected; fault energy analysis; remote guarded fixture; qualified authorization."),
    case("BF-016", "C - GUARDED FAULT FIXTURE", "Branch-3 downstream short", "F3; INJ1 PWR3/ACT3; J3 pin 2",
         "ACT_12V_BUS; J3_VDD; ACT_0V_PE_BONDED", "PROGRAMMABLE CURRENT-LIMITED SOURCE IN GUARDED FIXTURE; NO ACTUATOR",
         "Close a rated remote fault element from J3_VDD to return at the released worst-case branch impedance.",
         "bidirectional source/branch current; source and branch voltage; fuse state; conductor/connector/holder temperatures",
         "Selected protection clears or source limitation holds before any selected conductor/connector/holder limit; no damage or cross-branch energization.",
         "EG-014 coordination accepted; exact F3/harness/connector selected; fault energy analysis; remote guarded fixture; qualified authorization."),
    case("BF-017", "C - GUARDED FAULT FIXTURE", "K1 coil downstream short", "FSR1; K1 A1/A2",
         "SRA1_K1_RAW; K1_A1; SAFETY_0V", "PROGRAMMABLE CURRENT-LIMITED 24 V SOURCE IN GUARDED FIXTURE",
         "Close a rated remote fault element downstream of FSR1 with the contactor coil replaced by the approved fixture load.",
         "source/branch current; voltage; fuse state; holder/conductor temperature; K1/K2 command and feedback",
         "Selected FSR1 protection clears/limits before damage and cannot energize K1, K2, or create a restart command.",
         "EG-014 coordination accepted; exact FSR1 and conductors selected; guarded fixture; qualified authorization."),
    case("BF-018", "C - GUARDED FAULT FIXTURE", "K2 coil downstream short", "FSR2; K2 A1/A2",
         "SRA1_K2_RAW; K2_A1; SAFETY_0V", "PROGRAMMABLE CURRENT-LIMITED 24 V SOURCE IN GUARDED FIXTURE",
         "Close a rated remote fault element downstream of FSR2 with the contactor coil replaced by the approved fixture load.",
         "source/branch current; voltage; fuse state; holder/conductor temperature; K1/K2 command and feedback",
         "Selected FSR2 protection clears/limits before damage and cannot energize K1, K2, or create a restart command.",
         "EG-014 coordination accepted; exact FSR2 and conductors selected; guarded fixture; qualified authorization."),
    case("BF-019", "C - GUARDED FAULT FIXTURE", "Main-bus downstream short", "F0; SD1; KP1; KP2",
         "ACT_12V_FUSED; K1_P1_IN; K1_OUT; ACT_12V_BUS", "PROGRAMMABLE CURRENT-LIMITED SOURCE IN GUARDED FIXTURE; BRANCHES REPLACED BY FIXTURE",
         "Close a rated remote fault element at ACT_12V_BUS using the accepted worst-case loop impedance; never short the robot supply directly.",
         "source/bus current; all chain voltages; F0/SD1/KP1/KP2 temperatures and state; enclosure event video",
         "Selected upstream protection/source limitation prevents conductor, holder, disconnect or contactor damage and leaves the bus de-energized after isolation.",
         "EG-014 accepted; exact source characterization; contactor/DC application accepted; arc/energy study; guarded qualified authorization."),
    case("BF-020", "C - GUARDED FAULT FIXTURE", "Cross-branch fault", "F1; F2; INJ1; J1 pin 2; J2 pin 2",
         "J1_VDD; J2_VDD", "TWO GALVANICALLY CONTROLLED DAMAGE-LIMITED FIXTURE CHANNELS; NO ACTUATORS",
         "Apply the approved cross-branch potential through a rated remote fault element between J1_VDD and J2_VDD.",
         "both branch currents/voltages; fuse states; common bus; temperatures; isolation monitor",
         "No branch exceeds accepted limits, fault response is deterministic, and removal leaves neither branch unexpectedly energized.",
         "Cross-source energy analysis; exact protection; accepted grounding topology; guarded fixture and qualified authorization."),
    case("BF-021", "C - GUARDED FAULT FIXTURE", "Output backfeed attempt", "F1; INJ1; J1 pin 2",
         "J1_VDD; ACT_12V_BUS; ACT_12V_RAW", "PRIMARY SOURCE ABSENT; DAMAGE-LIMITED FOUR-QUADRANT FIXTURE SOURCE",
         "Apply the bounded reverse-polarity-correct source at J1_VDD and observe propagation toward ACT_12V_BUS/RAW.",
         "bidirectional branch/bus current; all bus voltages; F1/carrier state; source sink status; temperature",
         "Reverse energy follows the qualified disposition and remains within every selected component/source limit; unexpected upstream energization is a failure.",
         "R156 reverse-current hold closed; sink capability accepted; exact carrier variant and branch hardware; guarded authorization."),
    case("BF-022", "D - CONFIGURED DISTRIBUTION", "Regenerative pulse response", "J1/J2/J3; candidate branch carrier; F1/F2/F3",
         "J1_VDD; J2_VDD; J3_VDD; ACT_12V_BUS", "PRIMARY SOURCE/LOAD EMULATORS ONLY; NO ROBOT MECHANISM",
         "Inject the qualified branch-by-branch and simultaneous bidirectional pulse envelopes using programmable emulators.",
         "synchronized bidirectional branch/bus currents; all rail voltages; source status; shunt/eFuse temperatures; fault flags",
         "No voltage/current/energy/thermal limit is exceeded; no false reset or motion command occurs; repeated behavior matches accepted tolerances.",
         "Measured actuator regenerative envelope; R156 H05/H06/H07 closed; source sink/foldback disposition; qualified test authorization."),
    case("BF-023", "D - CONFIGURED DISTRIBUTION", "Contactor opening under bounded load", "KP1; KP2; F0-F3; SD1",
         "K1_P1_IN; K1_OUT; ACT_12V_BUS; J1_VDD; J2_VDD; J3_VDD", "PROGRAMMABLE LOADS ONLY; NO ROBOT MECHANISM",
         "Open K1 and K2 in every accepted sequence at bounded forward and reverse current; include one commanded device failing to open by fixture injection.",
         "individual contactor voltage/current; mirror/status; rail decay; source status; arc/event video; post-test resistance",
         "Redundant interruption and diagnostics satisfy the allocated numeric stopping/power-removal requirements without automatic restart.",
         "Qualified contactor DC application; numeric SRS/PLr allocation; source/protection coordination; guarded authorization."),
    case("BF-024", "D - CONFIGURED DISTRIBUTION", "Single-branch open while peers remain available", "F1/F2/F3; INJ1; J1/J2/J3",
         "ACT_12V_BUS; J1_VDD; J2_VDD; J3_VDD; DXL_TTL_DATA", "PROGRAMMABLE LOADS OR RESTRAINED ACTUATORS ONLY UNDER LATER AUTHORIZATION",
         "Open each branch in turn during a zero-motion diagnostic state; verify peers, supervisor fault handling, reset and re-enable behavior.",
         "all branch currents/voltages; DXL status; supervisor log; safety state; motion-command trace",
         "The affected branch is detected and held nonmoving; reset/reconnection cannot command motion; re-enable requires a separate deliberate command.",
         "Cases BF-001 through BF-023 accepted; restrained setup; released zero-motion procedure; qualified electrical/safety authorization."),
]


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def build_doc() -> str:
    counts: dict[str, int] = {}
    for row in CASES:
        counts[row["stage"]] = counts.get(row["stage"], 0) + 1
    stage_lines = "\n".join(f"- `{stage}`: {count} cases" for stage, count in counts.items())
    return f"""# HR-V0 branch fault and no-backfeed validation P0.1

> **{WARNING}**

Date: 2026-08-09

Applies to: Electrical V3-P1.14; `F0`, `F1`, `F2`, `F3`, `FSR1`, `FSR2`, `SD1`, `KP1`, `KP2`, `INJ1`, `U1`, `J1`, `J2`, and `J3`

Status: executable evidence schema only; all physical results and authorization remain open

## Decision

R157 supplies the previously missing evidence location for energization gate `EG-024`. It defines 24 exact-reference cases for unpowered isolation, low-energy control faults, guarded protection faults, output backfeed, regenerative pulses, redundant interruption, and no-motion recovery.

It does **not** select fuse values, conductors, fault energy, source limits, test equipment, acceptance thresholds, or contactor duty. It does not authorize a direct short, connection to the robot supply, actuator motion, or energization. Gate `EG-024` remains `open` until every applicable row is executed against a frozen configuration, raw evidence is accepted, nonconformances are closed, and qualified reviewers sign the result.

## Controlled evidence

- Matrix: `electrical/hr-v0-branch-fault-matrix-p0.1.csv`
- Blank execution record: `tests/forms/hr-v0-branch-fault-validation-template.csv`
- Interactive guide: `release/hr-v0/branch-fault-validation-p0.1/index.html`
- Machine check: `tools/check_hr_v0_branch_fault_validation_p01.py`

{stage_lines}

## Mandatory sequence

1. Complete Stage A with every energy source physically absent and prove live-dead-live instrument function using an approved method.
2. Complete Stage B only on separately protected, current-limited interface fixtures. The actuator source and robot mechanism remain absent.
3. Complete Stage C only after `EG-014` coordination inputs, exact protection/harness identities, prospective fault energy, enclosure, remote switching, guarding, instruments, emergency response, and qualified test authorization are accepted. A direct uncontrolled short across the robot source is prohibited.
4. Complete Stage D only after the preceding cases and their nonconformances are accepted. Programmable loads/emulators precede any restrained actuator article.
5. Every recovery check must prove that clearing a fault, releasing/resetting E-stop, restoring a branch, or rebooting ordinary control cannot itself command motion. A separate deliberate command remains mandatory.

## Fail-closed acceptance rule

Blank or `SELECTION REQUIRED` numeric thresholds are not permission to improvise. Before execution, the controlled test plan must state exact source serials, source limit/foldback/sink behavior, fuse and holder order codes, conductor and connector identities, loop impedance, fault energy, instrument ranges/bandwidth/calibration, remote switching rating, guards, PPE/emergency response, thermal limits, clearing limits, rail-decay/stopping limits, sample rate, uncertainty, and named authorized roles.

Any unexpected upstream energization, cross-branch energization, connector/conductor/holder damage, uncontrolled arc, source instability, automatic restart, motion command, lost diagnostic, exceeded limit, missing trace, or ambiguous configuration is a failed test and blocks progression.

## Sol R12 disposition

This is a project-owned correction to the Sol R12 architecture-only protection and missing executed-evidence findings. It is not a new Sol review, physical proof, independent approval, or functional-safety validation. The original 18 BLOCKER / 30 MAJOR / 8 MINOR totals are not changed by this pass.

## Release state

All 24 cases are `NOT EXECUTED`. Gate `EG-024` remains `open`. HR-V0 remains not ready for fabrication, assembly, connection, motion, or energization; HR-30W remains a later feasibility program.
"""


def build_html() -> str:
    payload = json.dumps(CASES, ensure_ascii=False).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>HR-V0 branch fault validation P0.1</title>
<style>
:root{{--sky:#9edcff;--deep:#082d5b;--gold:#f5bd24;--paper:#f7fbff;--ink:#10243d;--line:#aac6df;--danger:#8b1e2d}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--paper);color:var(--ink);font:18px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}}
header{{background:linear-gradient(135deg,var(--deep),#155b98);color:white;padding:clamp(24px,5vw,64px)}}
header h1{{font-size:clamp(32px,5vw,60px);line-height:1.05;margin:.25rem 0 1rem}} header p{{max-width:950px;margin:.5rem 0}}
.warning{{background:var(--gold);color:#181818;font-weight:800;padding:16px 20px;border-bottom:4px solid var(--deep)}}
main{{max-width:1240px;margin:auto;padding:24px}} .summary{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:16px;margin:20px 0}}
.metric,.card{{background:white;border:2px solid var(--line);border-radius:16px;padding:18px;box-shadow:0 5px 0 rgba(8,45,91,.08)}}
.metric strong{{display:block;color:var(--deep);font-size:32px}} .controls{{display:flex;flex-wrap:wrap;gap:10px;margin:24px 0}}
button{{font:inherit;font-weight:750;border:2px solid var(--deep);background:white;color:var(--deep);border-radius:999px;padding:10px 16px;cursor:pointer}}
button.active{{background:var(--deep);color:white}} .grid{{display:grid;gap:18px}} .card h2{{font-size:24px;margin:0 0 8px;color:var(--deep)}}
.tag{{display:inline-block;background:var(--sky);border-radius:999px;padding:4px 10px;font-size:14px;font-weight:750;margin:0 6px 8px 0}}
.state{{background:#ffe4e7;color:var(--danger)}} dl{{display:grid;grid-template-columns:minmax(160px,230px) 1fr;gap:8px 14px;margin:12px 0}} dt{{font-weight:800}} dd{{margin:0;overflow-wrap:anywhere}}
.hold{{border-left:8px solid var(--gold);padding-left:14px}} footer{{padding:30px 24px 60px;text-align:center;font-size:16px}}
@media(max-width:700px){{body{{font-size:16px}} main{{padding:16px}} dl{{grid-template-columns:1fr;gap:2px}} dd{{margin-bottom:10px}}}}
</style></head><body>
<div class="warning">{html.escape(WARNING)}</div>
<header><p>PROJECT BUTTON · HR-V0 · R157</p><h1>Branch fault &amp; no-backfeed validation</h1><p>Twenty-four controlled cases tied to the actual V3 references and nets. This is a blank test plan—not test evidence and not permission to power hardware.</p></header>
<main><section class="summary"><div class="metric"><strong>24</strong>unexecuted cases</div><div class="metric"><strong>4</strong>dependency stages</div><div class="metric"><strong>0</strong>released fuse values</div><div class="metric"><strong>OPEN</strong>gate EG-024</div></section>
<section class="card hold"><h2>Safe boundary</h2><p>Stages A and B begin unpowered or on separate limited-energy fixtures. Guarded fault work cannot start until protection coordination, exact hardware, energy bounds, guarding, instruments, emergency response, and qualified authorization are accepted. Never apply a direct uncontrolled short across the robot source.</p></section>
<div class="controls" id="filters"><button class="active" data-stage="ALL">All cases</button><button data-stage="A - UNPOWERED">A · unpowered</button><button data-stage="B - LIMITED ENERGY">B · limited energy</button><button data-stage="C - GUARDED FAULT FIXTURE">C · guarded fixture</button><button data-stage="D - CONFIGURED DISTRIBUTION">D · configured distribution</button></div>
<section class="grid" id="cases"></section></main>
<footer>{html.escape(WARNING)}<br>All results remain NOT EXECUTED.</footer>
<script>const rows={payload};const host=document.getElementById('cases');function esc(v){{return String(v).replace(/[&<>\"]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}}[c]))}}function render(stage='ALL'){{host.innerHTML=rows.filter(r=>stage==='ALL'||r.stage===stage).map(r=>`<article class="card"><span class="tag">${{esc(r.stage)}}</span><span class="tag state">${{esc(r.execution_state)}}</span><h2>${{esc(r.case_id)}} · ${{esc(r.circuit)}}</h2><dl><dt>References</dt><dd>${{esc(r.references)}}</dd><dt>Nets</dt><dd>${{esc(r.nets)}}</dd><dt>Source state</dt><dd>${{esc(r.source_state)}}</dd><dt>Action</dt><dd>${{esc(r.injection_or_action)}}</dd><dt>Monitors</dt><dd>${{esc(r.required_monitors)}}</dd><dt>Acceptance basis</dt><dd>${{esc(r.acceptance_basis)}}</dd><dt>Prerequisites</dt><dd>${{esc(r.mandatory_prerequisites)}}</dd></dl></article>`).join('')}}document.getElementById('filters').addEventListener('click',e=>{{if(e.target.tagName!=='BUTTON')return;document.querySelectorAll('button').forEach(b=>b.classList.remove('active'));e.target.classList.add('active');render(e.target.dataset.stage)}});render();</script>
</body></html>"""


def main() -> None:
    write_csv(MATRIX_PATH, CASES, FIELDS)
    form_fields = [
        "case_id", "execution_state", "date_utc", "operator", "qualified_test_owner",
        "repo_commit", "electrical_revision", "article_ids", "source_ids",
        "protection_order_codes", "harness_ids", "fixture_id", "authorization_record",
        "instrument_calibration_records", "raw_trace_directory", "photo_video_directory",
        "measured_result_summary", "acceptance_reference", "result", "nonconformance_ids",
        "reviewer_disposition", "warning",
    ]
    form_rows = [{field: "" for field in form_fields} for _ in CASES]
    for row, source in zip(form_rows, CASES):
        row["case_id"] = source["case_id"]
        row["execution_state"] = "NOT EXECUTED"
        row["electrical_revision"] = "V3-P1.14"
        row["result"] = "NOT EXECUTED"
        row["warning"] = WARNING
    write_csv(FORM_PATH, form_rows, form_fields)
    DOC_PATH.write_text(build_doc(), encoding="utf-8")
    WEB_DIR.mkdir(parents=True, exist_ok=True)
    WEB_PATH.write_text(build_html(), encoding="utf-8")
    print(f"Generated {len(CASES)} branch-fault cases and synchronized blank evidence artifacts.")


if __name__ == "__main__":
    main()
