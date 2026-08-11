#!/usr/bin/env python3
"""Generate the R231 current disposition of Sol's existing R12 review."""

from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release" / "hr-v0" / "sol-r12-current-disposition-r231"
WARNING = (
    "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, "
    "CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
)
IDENTIFIER = "HR-V0-SOL-R12-STATUS-R231"


ROWS = [
    ("B-001", "Authoritative native engineering implementation", "PARTIALLY_ADDRESSED_OPEN", "Native KiCad, CAD, firmware, deterministic manifests and checkers are now present; authoritative merge, formal acceptance and physical evidence remain open.", "release/hr-v0/HR-V0-RC-P0.1-file-manifest.csv; electrical/kicad/; cad/hr-v0/; firmware/"),
    ("B-002", "Electrical revision and metrics consistency", "PARTIALLY_ADDRESSED_OPEN", "Configuration identities and counts are machine controlled. P1.15 remains current while P1.18/P1.19 remain unaccepted, so promotion and independent disposition are still open.", "release/hr-v0/release-candidate.json; configuration/hr-v0-config-reconciliation-p0.4/; release/hr-v0/p119-visual-correction-p0.1/"),
    ("B-003", "Buildable HR-V0 mechanical definition", "PARTIALLY_ADDRESSED_OPEN", "The complete P0.8 arm, five drawing sets and manufacturing review surface now exist. Qualified drawing review, provider DFM, first articles, fit, mass and proof evidence do not.", "release/hr-v0/arm-architecture-p0.8-dwg-integrated/; release/hr-v0/mechanical-manufacturing-review-p0.1/"),
    ("B-004", "Wireable HR-V0 electrical implementation", "PARTIALLY_ADDRESSED_OPEN", "Native connected ECAD, explicit nodes, two-ended conductors and placement candidates exist. P1.19 still carries 63 unresolved selection/interface records and no installed inspection evidence.", "electrical/kicad/project-button-v3-p1.19-visual-correction-candidate/; release/hr-v0/panel-point-to-point-p0.1/; release/hr-v0/panel-conductor-basis-p0.1/"),
    ("B-005", "Watchdog permit fault tolerance", "OPEN_BLOCKER", "Two ordinary series permit contacts remove the single-weld defeat claimed against the earlier baseline, but dual/common-cause bypass, diagnostic coverage and safety allocation remain open; the watchdog retains zero safety credit.", "release/hr-v0/watchdog-permit-topology-p0.1/"),
    ("B-006", "Safety requirements and PLr/SIL allocation", "PARTIALLY_ADDRESSED_OPEN", "A measurable SRS candidate and review route exist. PLr/SIL, architecture/category, MTTFd/B10d, DCavg, CCF and qualified validation remain unselected or unexecuted.", "release/hr-v0/safety-requirements-p0.2/; release/hr-v0/functional-safety-review-route-p0.1/"),
    ("B-007", "Total response time and stopping distance", "PARTIALLY_ADDRESSED_OPEN", "The first-motion candidate is 200 ms total response and 2.000 degrees residual J2-positive travel at no more than 10 degrees/s. No physical trace or accepted uncertainty budget exists.", "release/hr-v0/safety-requirements-p0.2/; release/hr-v0/stopping-budget-p0.1/"),
    ("B-008", "K1/K2 DC interruption suitability", "PARTIALLY_ADDRESSED_OPEN", "Current terminal parity and manufacturer catalog envelopes are controlled. Critical current, regenerative interruption, suppression, SCCR, life and manufacturer/application acceptance remain open.", "release/hr-v0/contactor-application-p0.3/"),
    ("B-009", "PE, DC bonding, shielding and enclosure", "PARTIALLY_ADDRESSED_OPEN", "The exact proposed source/frame/shield boundary and pre-power methods are controlled. Site inputs, fault/clearing analysis, installed bonding, isolation and first-fault results remain open.", "release/hr-v0/e2-grounding-boundary-p0.1/; release/hr-v0/e2-prepower-test-p0.1/"),
    ("B-010", "Mass, center of mass and inertia closure", "PARTIALLY_ADDRESSED_OPEN", "CAD and moving-mass ledgers exist, including the current P0.8 arm identity. Received masses, complete cable/guard/end-effector values, as-built COM and inertia correlation remain open.", "bom/hr-v0-moving-mass-ledger.csv; release/hr-v0/arm-architecture-p0.8-dwg-integrated/"),
    ("B-011", "Walking drivetrain continuous and impact margin", "OPEN_HR30_BLOCKER", "HR-V0 has an unexecuted X430 duty-characterization route. HR-30W XH540 plus 1.5:1 continuous, thermal, impact, life and control-bandwidth evidence remains absent.", "release/hr-v0/x430-duty-characterization-p0.1/; docs/walking-system.md; docs/walking-verification.md"),
    ("B-012", "Leg drivetrain and structural load paths", "OPEN_HR30_BLOCKER", "The staged walking program is defined, but no released HR-30 leg joint, belt, shaft, bearing, fastener, fatigue or proof-tested structure exists.", "docs/walking-system.md; docs/walking-verification.md; docs/releases/hr-30w.md"),
    ("B-013", "Safe power-loss behavior", "PARTIALLY_ADDRESSED_OPEN", "HR-V0 has passive receiver/collapse candidates and an unexecuted containment route. Accepted as-built arm behavior is absent, and HR-30 walking power-loss behavior remains unresolved.", "release/hr-v0/power-loss-containment-p0.1/; release/hr-v0/passive-arm-receiver-detail-p0.2/"),
    ("B-014", "Dynamic fall-restraint definition", "OPEN_HR30_BLOCKER", "Walking stages require restraint, but exact drop, stroke, peak load, acceleration, elasticity, attachment loads, dynamic qualification and retirement criteria remain open.", "docs/walking-verification.md; docs/releases/hr-30b.md; docs/releases/hr-30d.md"),
    ("B-015", "Battery, isolation, charging and regeneration", "OPEN_HR30_BLOCKER", "No selected and validated HR-30 pack, BMS, fuse, precharge, disconnect, contactors, charger interlock, telemetry, enclosure or regenerative sink exists.", "docs/walking-system.md; docs/walking-verification.md; docs/open-decisions.md"),
    ("B-016", "Foot-force and IMU implementable electronics", "OPEN_HR30_BLOCKER", "Walking sensor functions remain architectural; exact sensors, analog front ends, excitation/reference, filtering, calibration, protection, PCB, EMC and fault evidence are absent.", "docs/walking-system.md; docs/walking-verification.md"),
    ("B-017", "Real-time controller, firmware and bus timing", "PARTIALLY_ADDRESSED_OPEN", "Fail-closed HR-V0 supervisor/watchdog source and tests now exist. Deployed-image, target HIL and measured HR-V0 timing remain open; HR-30 balance firmware and measured segmented-bus timing are absent.", "firmware/supervisor/; firmware/watchdog/; software/host/hr-v0-host-deploy-p0.1/; docs/walking-system.md"),
    ("B-018", "Requirements maturity and governance", "PARTIALLY_ADDRESSED_OPEN", "Atomic child requirements, gate control and governance audit packages now exist. All requirements remain draft/unexecuted/unapproved and named independent approval remains open.", "requirements/atomic-p0.2/; requirements/governance-p0.3/; requirements/hr-v0-energization-gates.csv"),
]


def write_csv(path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("finding_id", "subject", "current_disposition", "current_evidence", "evidence_location", "warning"))
        for row in ROWS:
            writer.writerow((*row, WARNING))


def page() -> str:
    body = "".join(
        "<tr data-state='{state}'><td><strong>{fid}</strong></td><td>{subject}</td>"
        "<td><span class='badge'>{state}</span></td><td>{evidence}</td><td><code>{paths}</code></td></tr>".format(
            fid=html.escape(fid), subject=html.escape(subject), state=html.escape(state),
            evidence=html.escape(evidence), paths=html.escape(paths)
        )
        for fid, subject, state, evidence, paths in ROWS
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sol R12 current disposition after R230</title><style>
:root{{--sky:#78cef2;--navy:#082b4c;--blue:#155d91;--gold:#f3b61f;--paper:#f6fbff;--line:#8eb4cb}}
*{{box-sizing:border-box}}body{{margin:0;color:var(--navy);background:#fff;font:clamp(16px,1.15vw,19px)/1.5 Arial,sans-serif}}
header{{padding:clamp(1.5rem,5vw,4rem);background:linear-gradient(135deg,var(--sky),#edfaff);border-bottom:7px solid var(--gold)}}
h1{{font-size:clamp(2rem,5vw,4.5rem);line-height:1.05;margin:.3rem 0 1rem;max-width:18ch}}h2{{font-size:clamp(1.4rem,2.2vw,2.1rem)}}
main{{max-width:1500px;margin:auto;padding:2rem clamp(1rem,4vw,3rem)}}.warning{{padding:1rem;border:3px solid #a87400;background:#fff3c4;border-radius:.8rem;font-weight:700}}
.summary{{font-size:clamp(1.15rem,1.8vw,1.5rem);max-width:70rem}}button{{font:inherit;font-weight:700;color:var(--navy);background:#fff;border:3px solid var(--blue);border-radius:.6rem;padding:.65rem .9rem;margin:.25rem}}
button[aria-pressed="true"]{{background:var(--gold)}}.table-wrap{{overflow:auto;border:2px solid var(--line);border-radius:.8rem;margin-top:1rem}}
table{{width:100%;border-collapse:collapse;min-width:1100px}}th,td{{padding:.8rem;text-align:left;vertical-align:top;border-bottom:1px solid #b6ccd9}}th{{background:var(--navy);color:#fff;position:sticky;top:0}}
.badge{{font-size:14px;font-weight:700;background:#fff0b3;border:1px solid #9b7000;border-radius:.35rem;padding:.2rem .4rem;white-space:nowrap}}code{{font-size:14px;white-space:normal}}[hidden]{{display:none!important}}
</style></head><body><header><div><strong>{IDENTIFIER}</strong> / project-owned reconciliation of existing R12</div><h1>What Sol’s blockers mean now</h1><div class="warning">{WARNING}</div></header>
<main><p class="summary">Sol’s 18 blockers were valid against the reviewed 2026-08-06 baseline. After 218 project-owned correction rounds, source and configuration maturity is much stronger—but <strong>zero of the 18 findings has qualified closure evidence</strong>. Five remain HR-30 walking blockers; the rest remain open or partially addressed for HR-V0.</p>
<h2>Filter the blocker register</h2><div><button data-filter="ALL" aria-pressed="true">All 18</button><button data-filter="OPEN_BLOCKER">Open HR-V0</button><button data-filter="OPEN_HR30_BLOCKER">Open HR-30</button><button data-filter="PARTIALLY_ADDRESSED_OPEN">Partially addressed</button></div>
<div class="table-wrap"><table><thead><tr><th>ID</th><th>Subject</th><th>Current disposition</th><th>Current evidence and boundary</th><th>Evidence locations</th></tr></thead><tbody>{body}</tbody></table></div>
<h2>Immediate engineering priority</h2><p>Do not spend the next round polishing diagrams. The shortest route toward a controlled first HR-V0 energization is: independent disposition of P1.19 and the P0.8 mechanical packet; exact physical component and conductor selections; received-part/first-article metrology; released pre-power limits; then separately authorized unpowered inspection and physical validation. HR-30 walking blockers remain downstream and receive no inheritance until HR-V0 is validated.</p>
</main><script>const buttons=[...document.querySelectorAll('button[data-filter]')],rows=[...document.querySelectorAll('tbody tr')];buttons.forEach(b=>b.addEventListener('click',()=>{{buttons.forEach(x=>x.setAttribute('aria-pressed','false'));b.setAttribute('aria-pressed','true');const f=b.dataset.filter;rows.forEach(r=>r.hidden=f!=='ALL'&&r.dataset.state!==f)}}));</script></body></html>"""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    write_csv(OUT / "blocker-disposition.csv")
    (OUT / "index.html").write_text(page(), encoding="utf-8", newline="\n")
    status = {
        "identifier": IDENTIFIER,
        "round": "R231",
        "source_review": "Sol R12",
        "source_review_findings": {"blocker": 18, "major": 30, "minor": 8},
        "blockers_qualified_closed": 0,
        "partially_addressed_open": 12,
        "open_hr_v0_blocker": 1,
        "open_hr30_blocker": 5,
        "independent_review": False,
        "qualified_review": False,
        "work_authority": False,
        "warning": WARNING,
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
    manifest_rows = []
    for path in sorted(p for p in OUT.iterdir() if p.is_file() and p.name != "file-manifest.csv"):
        data = path.read_bytes()
        manifest_rows.append((path.name, len(data), hashlib.sha256(data).hexdigest(), WARNING))
    with (OUT / "file-manifest.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("file", "size_bytes", "sha256", "warning"))
        writer.writerows(manifest_rows)
    print(f"Wrote {OUT.relative_to(ROOT)} with {len(ROWS)} blocker dispositions")
    print(WARNING)


if __name__ == "__main__":
    main()
