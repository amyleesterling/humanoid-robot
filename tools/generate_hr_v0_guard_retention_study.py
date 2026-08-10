from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad" / "hr-v0" / "guard-retention-study-p0.1"
REVISION = "HR-V0-GUARD-RET-P0.1"
WARNING = (
    "PRELIMINARY - EVALUATION STUDY ONLY - NOT APPROVED FOR PROCUREMENT, "
    "FABRICATION, ASSEMBLY, MOTION, CONNECTION, OR ENERGIZATION"
)
SHEET_DENSITY_KG_M3 = 1200.0
PROFILE_MASS_KG = 5.213705


def write_csv(name: str, fields: tuple[str, ...], rows: list[dict[str, object]]) -> None:
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sheet_mass(pieces: list[tuple[float, float, int]], thickness_mm: float) -> float:
    area_mm2 = sum(x_mm * y_mm * quantity for x_mm, y_mm, quantity in pieces)
    return area_mm2 * thickness_mm * 1e-9 * SHEET_DENSITY_KG_M3


def fmt(value: float) -> str:
    return f"{value:.6f}"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    outer = [
        (485.0, 970.0, 4),
        (440.0, 970.0, 2),
        (440.0, 485.0, 2),
    ]
    receiver = [
        (332.0, 832.0, 1),
        (832.0, 50.0, 2),
        (320.0, 50.0, 2),
    ]

    outer_3 = sheet_mass(outer, 3.0)
    outer_4_5 = sheet_mass(outer, 4.5)
    outer_6 = sheet_mass(outer, 6.0)
    receiver_3 = sheet_mass(receiver, 3.0)
    receiver_4_5 = sheet_mass(receiver, 4.5)
    receiver_6 = sheet_mass(receiver, 6.0)

    mass_rows = [
        {
            "option_id": "GMASS-BASE-6",
            "outer_thickness_mm": "6.0",
            "receiver_thickness_mm": "6.0",
            "profile_mass_kg": fmt(PROFILE_MASS_KG),
            "outer_sheet_mass_kg": fmt(outer_6),
            "receiver_sheet_mass_kg": fmt(receiver_6),
            "known_subtotal_kg": fmt(PROFILE_MASS_KG + outer_6 + receiver_6),
            "change_from_p0_3_kg": fmt(0.0),
            "state": "CURRENT P0.3 MASS BASIS; RETENTION AND IMPACT OPEN",
        },
        {
            "option_id": "GMASS-ALL-4P5",
            "outer_thickness_mm": "4.5",
            "receiver_thickness_mm": "4.5",
            "profile_mass_kg": fmt(PROFILE_MASS_KG),
            "outer_sheet_mass_kg": fmt(outer_4_5),
            "receiver_sheet_mass_kg": fmt(receiver_4_5),
            "known_subtotal_kg": fmt(PROFILE_MASS_KG + outer_4_5 + receiver_4_5),
            "change_from_p0_3_kg": fmt(PROFILE_MASS_KG + outer_4_5 + receiver_4_5 - (PROFILE_MASS_KG + outer_6 + receiver_6)),
            "state": "MASS SCREEN ONLY; NO COMPATIBLE 20-SERIES GASKET OR IMPACT BASIS RELEASED",
        },
        {
            "option_id": "GMASS-ALL-3",
            "outer_thickness_mm": "3.0",
            "receiver_thickness_mm": "3.0",
            "profile_mass_kg": fmt(PROFILE_MASS_KG),
            "outer_sheet_mass_kg": fmt(outer_3),
            "receiver_sheet_mass_kg": fmt(receiver_3),
            "known_subtotal_kg": fmt(PROFILE_MASS_KG + outer_3 + receiver_3),
            "change_from_p0_3_kg": fmt(PROFILE_MASS_KG + outer_3 + receiver_3 - (PROFILE_MASS_KG + outer_6 + receiver_6)),
            "state": "NONSELECTED SCREEN; RECEIVER STIFFNESS DROP AND IMPACT PROOF OPEN",
        },
        {
            "option_id": "GMASS-HYBRID-3-6",
            "outer_thickness_mm": "3.0",
            "receiver_thickness_mm": "6.0",
            "profile_mass_kg": fmt(PROFILE_MASS_KG),
            "outer_sheet_mass_kg": fmt(outer_3),
            "receiver_sheet_mass_kg": fmt(receiver_6),
            "known_subtotal_kg": fmt(PROFILE_MASS_KG + outer_3 + receiver_6),
            "change_from_p0_3_kg": fmt(PROFILE_MASS_KG + outer_3 + receiver_6 - (PROFILE_MASS_KG + outer_6 + receiver_6)),
            "state": "PREFERRED EVALUATION BRANCH ONLY; NOT SELECTED OR SAFETY-RATED",
        },
    ]
    write_csv(
        "guard-mass-options.csv",
        (
            "option_id", "outer_thickness_mm", "receiver_thickness_mm", "profile_mass_kg",
            "outer_sheet_mass_kg", "receiver_sheet_mass_kg", "known_subtotal_kg",
            "change_from_p0_3_kg", "state",
        ),
        mass_rows,
    )

    edge_rows = [
        {"edge_id": "GE-970", "cut_length_mm": "970", "quantity": "12", "used_length_mm": "11640", "basis": "four front/rear halves plus two sides"},
        {"edge_id": "GE-485", "cut_length_mm": "485", "quantity": "12", "used_length_mm": "5820", "basis": "four front/rear halves plus two top halves"},
        {"edge_id": "GE-440", "cut_length_mm": "440", "quantity": "8", "used_length_mm": "3520", "basis": "two sides plus two top halves"},
    ]
    write_csv(
        "guard-gasket-edge-schedule.csv",
        ("edge_id", "cut_length_mm", "quantity", "used_length_mm", "basis"),
        edge_rows,
    )

    stock_rows: list[dict[str, object]] = []
    for index in range(1, 7):
        stock_rows.append({
            "stock_id": f"GSK-{index:02d}", "stock_length_mm": "2000",
            "cuts_mm": "970+970", "used_mm": "1940", "offcut_mm": "60",
            "state": "PACKING SCREEN; SAW KERF AND RECEIVED LENGTH OPEN",
        })
    for index in range(7, 11):
        stock_rows.append({
            "stock_id": f"GSK-{index:02d}", "stock_length_mm": "2000",
            "cuts_mm": "485+485+485+440", "used_mm": "1895", "offcut_mm": "105",
            "state": "PACKING SCREEN; SAW KERF AND RECEIVED LENGTH OPEN",
        })
    stock_rows.append({
        "stock_id": "GSK-11", "stock_length_mm": "2000", "cuts_mm": "440+440+440+440",
        "used_mm": "1760", "offcut_mm": "240",
        "state": "PACKING SCREEN; SAW KERF AND RECEIVED LENGTH OPEN",
    })
    write_csv(
        "guard-gasket-stock-plan.csv",
        ("stock_id", "stock_length_mm", "cuts_mm", "used_mm", "offcut_mm", "state"),
        stock_rows,
    )

    thermal_rows = []
    for dimension in (970.0, 485.0, 440.0):
        allowance = dimension / 304.8 * 1.52
        thermal_rows.append({
            "dimension_mm": f"{dimension:.0f}",
            "plaskolite_guideline_mm": f"{allowance:.3f}",
            "expression": f"{dimension:.0f} mm / 304.8 mm per foot x 1.52 mm per foot",
            "state": "GUIDELINE SCREEN ONLY; INSTALLATION TEMPERATURE RANGE AND GASKET FIT OPEN",
        })
    write_csv(
        "guard-thermal-movement-screen.csv",
        ("dimension_mm", "plaskolite_guideline_mm", "expression", "state"),
        thermal_rows,
    )

    decision_rows = [
        {
            "candidate_id": "GRET-001", "candidate": "80/20 20-2496 with 75-3581",
            "configuration": "through-drilled external point retainer",
            "disposition": "EXCLUDED FROM CURRENT RETENTION BASELINE",
            "reason": "requires panel drilling; Plaskolite says through-bolting glazing should be used only when unavoidable and reviewed for thermal movement; no project load/spacing proof exists",
        },
        {
            "candidate_id": "GRET-002", "candidate": "80/20 12004 with TUFFAK GP clear nominal 3 mm",
            "configuration": "continuous four-edge 20-Series gasket branch",
            "disposition": "EXACT EVALUATION CANDIDATE; NOT SELECTED",
            "reason": "12004 explicitly covers 1-4 mm panels and avoids point drilling; no retention/impact allowable or application approval is published",
        },
        {
            "candidate_id": "GRET-003", "candidate": "TUFFAK GP clear nominal 6 mm with continuous external clamp/channel",
            "configuration": "four-edge custom or larger-series retention",
            "disposition": "DESIGN REQUIRED",
            "reason": "preserves P0.3 thickness but no exact 20-Series continuous 6 mm retention system or released design exists",
        },
    ]
    write_csv(
        "guard-retention-decisions.csv",
        ("candidate_id", "candidate", "configuration", "disposition", "reason"),
        decision_rows,
    )

    control_rows = [
        {"control_id": "GRC-001", "control": "Engage all four edges of every outer panel; no point-fastener-only retention receives credit.", "evidence_required": "accepted section drawing and installed-fit inspection", "state": "OPEN"},
        {"control_id": "GRC-002", "control": "Do not release finished panel dimensions until exact slot/gasket engagement and temperature range are accepted.", "evidence_required": "manufacturer CAD, tolerance stack and thermal calculation", "state": "OPEN"},
        {"control_id": "GRC-003", "control": "The 20,980 mm gasket schedule requires eleven nominal 2 m sticks before saw kerf and received-length allowance.", "evidence_required": "supplier configuration and cut plan", "state": "SCREEN ONLY"},
        {"control_id": "GRC-004", "control": "Derive the panel test energy and direction from the complete credible payload, tool, hardware and runaway envelope.", "evidence_required": "signed hazard/energy allocation", "state": "SELECTION REQUIRED"},
        {"control_id": "GRC-005", "control": "Test the exact panel, edge finish, gasket, frame, joints and support spacing; record residual engagement and damage.", "evidence_required": "released fixture/procedure and signed raw results", "state": "NOT EXECUTED"},
        {"control_id": "GRC-006", "control": "Retain the 6 mm receiver in the hybrid branch until receiver deflection, rebound and support proof close.", "evidence_required": "receiver calculation and TEST-DROP-001", "state": "OPEN"},
        {"control_id": "GRC-007", "control": "Do not count manufacturer typical density, product wording or a passing fit mock-up as an impact rating.", "evidence_required": "qualified application review and physical proof", "state": "OPEN"},
        {"control_id": "GRC-008", "control": "No retention branch may be procured for the machine or fabricated from these envelope dimensions.", "evidence_required": "separate approved evaluation purchase plus released coupon/fixture drawings", "state": "HOLD"},
    ]
    write_csv(
        "guard-retention-controls.csv",
        ("control_id", "control", "evidence_required", "state"),
        control_rows,
    )

    sources = [
        {"source_id": "GRS-001", "manufacturer": "80/20", "document": "20-2496 product page", "revision_or_date": "live page; no formal revision exposed; accessed 2026-08-07", "url": "https://8020.net/20-2496.html", "verified_fact": "requires drill-through machining on panel; suggests one 75-3581"},
        {"source_id": "GRS-002", "manufacturer": "80/20", "document": "12004 product page", "revision_or_date": "live page; no formal revision exposed; accessed 2026-08-07", "url": "https://8020.net/12004.html", "verified_fact": "20-Series polypropylene reduction T-slot cover usable as panel gasket for 1-4 mm panels; 2 m length"},
        {"source_id": "GRS-003", "manufacturer": "Plaskolite", "document": "TUFFAK fabrication guide FAB015", "revision_or_date": "current 68-page guide; no printed revision exposed; accessed 2026-08-07", "url": "https://plaskolite.com/docs/default-source/fab/fab015_tuf_en.pdf", "verified_fact": "3/4.5/6 mm gauges; drilling and edge-distance guidance; thermal movement; all-edge engagement; through-bolting only when unavoidable"},
        {"source_id": "GRS-004", "manufacturer": "Plaskolite", "document": "TUFFAK GP PDS004", "revision_or_date": "code 122022; accessed 2026-08-07", "url": "https://plaskolite.com/docs/default-source/pds/pds004_tuf_gp.pdf", "verified_fact": "specific gravity 1.2 is typical and not for specification purposes"},
        {"source_id": "GRS-005", "manufacturer": "80/20", "document": "20-2020 product page", "revision_or_date": "live page; no formal revision exposed; accessed 2026-08-07", "url": "https://8020.net/20-2020.html", "verified_fact": "profile identity and 0.0247 lb/in mass basis retained from P0.3"},
    ]
    write_csv(
        "guard-retention-source-register.csv",
        ("source_id", "manufacturer", "document", "revision_or_date", "url", "verified_fact"),
        sources,
    )

    summary = {
        "revision": REVISION,
        "status": WARNING,
        "parent_guard": "HR-V0-GUARD-P0.3",
        "current_known_subtotal_kg": float(mass_rows[0]["known_subtotal_kg"]),
        "preferred_evaluation_known_subtotal_kg": float(mass_rows[3]["known_subtotal_kg"]),
        "preferred_evaluation_reduction_kg": abs(float(mass_rows[3]["change_from_p0_3_kg"])),
        "gasket_candidate": "80/20 12004",
        "gasket_stock_length_mm": 2000,
        "gasket_stock_quantity_screen": 11,
        "gasket_used_length_mm": 20980,
        "gasket_offcut_before_kerf_mm": 1020,
        "retention_decisions": len(decision_rows),
        "controls": len(control_rows),
        "sources": len(sources),
        "selection_state": "NONSELECTED EVALUATION BRANCH; IMPACT AND RETENTION PROOF OPEN",
    }
    (OUT / "guard-retention-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )

    table_rows = "\n".join(
        f"<tr><td>{row['option_id']}</td><td>{row['outer_thickness_mm']}</td>"
        f"<td>{row['receiver_thickness_mm']}</td><td>{row['known_subtotal_kg']}</td>"
        f"<td>{row['change_from_p0_3_kg']}</td><td>{row['state']}</td></tr>"
        for row in mass_rows
    )
    decision_html = "\n".join(
        f"<article><h3>{row['candidate_id']}: {row['candidate']}</h3>"
        f"<p class='state'>{row['disposition']}</p><p>{row['reason']}</p></article>"
        for row in decision_rows
    )
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{REVISION} guard retention study</title>
<style>
:root{{--ink:#10244a;--blue:#1769aa;--sky:#dff3ff;--gold:#f5bd24;--paper:#f8fbff;--danger:#8b1e1e}}
*{{box-sizing:border-box}}html,body{{max-width:100%;overflow-x:hidden}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.5 system-ui,sans-serif}}
header,main{{max-width:1180px;margin:auto;padding:24px}}header{{background:var(--ink);color:white;max-width:none}}
header>div{{max-width:1180px;margin:auto}}h1{{font-size:clamp(30px,5vw,56px);line-height:1.05;margin:.25rem 0}}
h2{{font-size:clamp(24px,3vw,34px);margin-top:2rem}}h3{{font-size:19px;margin:.2rem 0}}.warning{{background:#fff1c2;color:#391d00;border:3px solid var(--gold);padding:16px;font-weight:800}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;margin:24px 0;min-width:0}}.card,article{{background:white;border:2px solid #9fc9e7;border-radius:12px;padding:18px;box-shadow:0 4px 0 #c9e8fa;min-width:0}}
.big{{font-size:clamp(28px,4vw,44px);font-weight:800;color:var(--blue)}}.state{{font-weight:800;color:var(--danger)}}
.table-wrap{{overflow-x:auto;max-width:100%;min-width:0;background:white;border:2px solid #9fc9e7;border-radius:12px}}table{{border-collapse:collapse;width:100%;min-width:860px}}th,td{{padding:13px;text-align:left;border-bottom:1px solid #b9d8eb;vertical-align:top;font-size:16px}}th{{background:var(--sky)}}code{{font-size:16px}}
@media(max-width:800px){{header,main{{padding:18px;min-width:0}}.cards{{grid-template-columns:minmax(0,1fr)}}h1,p,.big{{overflow-wrap:anywhere}}.table-wrap{{border-radius:8px}}}}
</style></head><body>
<header><div><p>PROJECT BUTTON · {REVISION}</p><h1>Guard retention and mass study</h1><p>Exact evaluation branch; no safety or fabrication release.</p></div></header>
<main><p class="warning">{WARNING}</p>
<section class="cards"><div class="card"><div class="big">30.800 kg</div><p>Current 6 mm profile-and-sheet subtotal.</p></div><div class="card"><div class="big">19.416 kg</div><p>Nonselected 3 mm outer / 6 mm receiver evaluation subtotal.</p></div><div class="card"><div class="big">−11.384 kg</div><p>Planning reduction; no impact or retention credit.</p></div><div class="card"><div class="big">11 × 2 m</div><p>Exact 12004 gasket stock packing screen before saw kerf.</p></div></section>
<h2>Mass branches</h2><div class="table-wrap"><table><thead><tr><th>Option</th><th>Outer mm</th><th>Receiver mm</th><th>Known subtotal kg</th><th>Change kg</th><th>State</th></tr></thead><tbody>{table_rows}</tbody></table></div>
<h2>Retention decisions</h2><div class="cards">{decision_html}</div>
<h2>What this changes</h2><p>The prior <code>20-2496</code> point-retainer route is excluded from the current retention baseline. It requires panel drilling, while the sheet manufacturer says through-fastening glazing should be used only when unavoidable and reviewed for thermal movement. <code>12004</code> is an exact continuous-gasket candidate for a 3 mm evaluation branch because its published range is 1–4 mm. Its retention and impact capacity are not published and receive no credit.</p>
<h2>Release boundary</h2><p>Finished panel dimensions, gasket compression, temperature range, impact energy, proof load, frame/joint capacity and physical results remain open. Do not buy machine parts, cut panels, assemble a guard, connect an actuator or energize from this study.</p>
</main></body></html>"""
    (OUT / "HR-V0_guard-retention-study.html").write_text(html, encoding="utf-8")

    print(
        f"Generated {REVISION}: 4 mass branches, 32 gasket edge pieces, "
        "11 stock lengths, 3 decisions, 8 controls"
    )
    print(WARNING)


if __name__ == "__main__":
    main()
