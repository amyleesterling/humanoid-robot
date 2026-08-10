"""Generate the fail-closed FR12-H101 moving-subassembly mass/metrology package.

The package does not invent a mass from storefront shipping fields.  It turns
the remaining LOAD-OPEN-01 input into an executable, unpowered evidence route
and supplies conservative inertia/gravity formulas for accepted measurements.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "cad" / "vendor" / "robotis" / "x430-fr12-r91"
OUT = ROOT / "cad" / "hr-v0" / "generated" / "fr12-moving-mass-metrology-p0.1"
FORM = ROOT / "tests" / "forms" / "hr-v0-fr12-moving-subassembly-measurement-template.csv"
REPEAT_FORM = ROOT / "tests" / "forms" / "hr-v0-fr12-mass-repeat-template.csv"
GUIDE = ROOT / "release" / "hr-v0" / "fr12-moving-mass-metrology-p0.1" / "index.html"
G = 9.80665


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise RuntimeError(f"refusing empty CSV: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    h101_path = VENDOR / "fr12_h101.stp"
    h101 = cq.importers.importStep(str(h101_path)).val()
    box = h101.BoundingBox()
    center = h101.Center()
    matrix = cq.Shape.matrixOfInertia(h101)
    volume = h101.Volume()
    vertex_radius = max(math.hypot(vertex.Y, vertex.Z) for vertex in h101.Vertices())
    bbox_radius = math.hypot(max(abs(box.ymin), abs(box.ymax)), max(abs(box.zmin), abs(box.zmax)))
    uniform_ixx_per_mass_mm2 = matrix[0][0] / volume + center.y**2 + center.z**2

    geometry = {
        "identifier": "HR-V0-FR12-MASS-MET-P0.1",
        "status": "PRELIMINARY - UNPOWERED MEASUREMENT ROUTE ONLY",
        "source_step": str(h101_path.relative_to(ROOT)).replace("\\", "/"),
        "source_sha256": sha256(h101_path),
        "solid_count": len(h101.Solids()),
        "volume_mm3": round(volume, 9),
        "uniform_geometry_centroid_mm": {"x": round(center.x, 9), "y": round(center.y, 9), "z": round(center.z, 9)},
        "bounding_box_mm": {
            "x_min": round(box.xmin, 9), "x_max": round(box.xmax, 9),
            "y_min": round(box.ymin, 9), "y_max": round(box.ymax, 9),
            "z_min": round(box.zmin, 9), "z_max": round(box.zmax, 9),
        },
        "maximum_vertex_radius_about_j2_x_mm": round(vertex_radius, 9),
        "conservative_bbox_corner_radius_about_j2_x_mm": round(bbox_radius, 9),
        "uniform_geometry_ixx_about_j2_per_unit_mass_mm2": round(uniform_ixx_per_mass_mm2, 9),
        "boundary": "FRAME GEOMETRY ONLY; IDLER, OUTPUT-SIDE MOVING HARDWARE, FASTENERS AND RECEIVED VARIATION EXCLUDED",
    }
    (OUT / "frame-geometry-audit.json").write_text(json.dumps(geometry, indent=2) + "\n", encoding="utf-8")

    conflict_rows = [
        {
            "record_id": "FR12-WEIGHT-01",
            "official_product": "FR12-H101K Set",
            "sku": "903-0239-000",
            "commerce_weight_field": "0.10 lb",
            "package_relationship": "contains one HN12-I101 Set plus frame, bolts and spacer rings",
            "source": "https://www.robotis.us/fr12-h101k-set/",
            "checked": "2026-08-08",
            "disposition": "REJECT FOR MASS CREDIT",
            "reason": "rounded storefront field is lower than the separately listed included idler-set field; semantics and rounding are not a component mass-property record",
        },
        {
            "record_id": "FR12-WEIGHT-02",
            "official_product": "HN12-I101 Set",
            "sku": "903-0240-000",
            "commerce_weight_field": "0.20 lb",
            "package_relationship": "included within FR12-H101K Set",
            "source": "https://www.robotis.us/hn12-i101-set/",
            "checked": "2026-08-08",
            "disposition": "REJECT FOR MASS CREDIT",
            "reason": "field conflicts with the containing kit field and cannot establish installed moving mass, COM or inertia",
        },
    ]
    write_csv(OUT / "commerce-weight-conflict.csv", conflict_rows)

    allocation_rows = [
        {"allocation_id": "FR12-EA-01", "source_line": "EVA-010 / BOM-018", "article": "OpenMANIPULATOR-X Frame Set RM-X52", "order_code": "ROBOTIS SKU 905-0023-000", "quantity_needed": "1", "measurement_use": "source one FR12-H101 frame and one HN12-I101 set; retain kit traceability", "state": "PROGRAM OWNER APPROVAL REQUIRED - NOT PURCHASED OR RECEIVED"},
        {"allocation_id": "FR12-EA-02", "source_line": "EVA-004 / BOM-007", "article": "XM430-W350-T", "order_code": "ROBOTIS SKU 902-0124-000", "quantity_needed": "1", "measurement_use": "unpowered temporary fit article only after fastener/assembly hold closes", "state": "PROGRAM OWNER APPROVAL REQUIRED - NOT PURCHASED OR RECEIVED"},
        {"allocation_id": "FR12-EA-03", "source_line": "RM-X52 received contents", "article": "installed bolts, spacer rings, idler and output-side moving hardware", "order_code": "RECEIVED ALLOCATION REQUIRED", "quantity_needed": "SELECTION REQUIRED", "measurement_use": "freeze exact installed moving subset and prevent double counting", "state": "NOT ALLOCATED"},
    ]
    write_csv(OUT / "evaluation-article-allocation.csv", allocation_rows)

    plan_rows = [
        {"operation": "FR12-MET-01", "stage": "CONFIGURATION", "method": "Freeze repository commit, P1.1 geometry identifier, received kit/actuator identities and measurement work authorization.", "acceptance": "One immutable configuration and named unpowered scope; no source connection or motion.", "state": "NOT EXECUTED"},
        {"operation": "FR12-MET-02", "stage": "RECEIVING", "method": "Quarantine and inventory RM-X52, FR12-H101, HN12-I101, XM430 and every candidate installed fastener/spacer against official and controlled kit records.", "acceptance": "Counts, labels, lots, photos and discrepancies recorded; articles remain segregated.", "state": "NOT EXECUTED"},
        {"operation": "FR12-MET-03", "stage": "SOURCE PARITY", "method": "Compare received FR12-H101 envelope and selected datums with the hash-controlled STEP/drawing without assuming material or mass.", "acceptance": "Qualified reviewer accepts source applicability and dimensional method/uncertainty.", "state": "NOT EXECUTED"},
        {"operation": "FR12-MET-04", "stage": "INSTRUMENT", "method": "Select a calibrated balance with <=0.01 g readability and accepted uncertainty over the bracketing working range; run repeatability/tare checks.", "acceptance": "Calibration, traceability, environment, tare stability and measurement-system analysis accepted.", "state": "NOT EXECUTED"},
        {"operation": "FR12-MET-05", "stage": "LOOSE MASS", "method": "Record at least ten readings each for frame alone, idler/output moving hardware group, and exact installed fastener/spacer group using the raw template.", "acceptance": "No omitted/double-counted item; mean and expanded uncertainty calculated from an approved method.", "state": "NOT EXECUTED"},
        {"operation": "FR12-HOLD-01", "stage": "HOLD", "method": "Do not temporarily assemble until exact screw length, engagement, spacer, torque, locking, reuse and teardown instructions are signed.", "acceptance": "All instructions and stop conditions accepted; otherwise remain loose-part only.", "state": "OPEN"},
        {"operation": "FR12-MET-06", "stage": "ASSEMBLED MASS", "method": "After FR12-HOLD-01, weigh the complete unpowered moving subassembly and reconcile it to the sum of individually measured items.", "acceptance": "Difference is within the accepted combined uncertainty or a nonconformance is opened.", "state": "NOT EXECUTED"},
        {"operation": "FR12-MET-07", "stage": "ENVELOPE", "method": "Measure y/z extrema of every moving item about the physical J2 axis; add signed expanded coordinate uncertainty before calculating radius.", "acceptance": "As-built radius bound includes frame, idler, output hardware, fasteners and accepted uncertainty.", "state": "NOT EXECUTED"},
        {"operation": "FR12-MET-08", "stage": "COM", "method": "Measure two orthogonal reaction pairs on an accepted rigid two-support fixture; subtract fixture reactions and calculate COM from R_B*L/(R_A+R_B) plus the surveyed support-to-J2 datum.", "acceptance": "Mass closure, reaction sum, repeatability, fixture deflection and y/z COM uncertainty pass accepted limits.", "state": "NOT EXECUTED"},
        {"operation": "FR12-MET-09", "stage": "INERTIA BOUND", "method": "Calculate Ixx <= m_upper*r_upper^2 for the complete received moving subset; optionally scale the uniform frame STEP only after source/material-uniformity acceptance.", "acceptance": "Bound and assumptions independently reproduced; no reflected-drive inertia is hidden in this row.", "state": "NOT EXECUTED"},
        {"operation": "FR12-MET-10", "stage": "LOAD UPDATE", "method": "Replace LOAD-OPEN-01 only after accepted mass, COM, envelope and inertia evidence; regenerate gravity/energy/stop models from the same commit.", "acceptance": "All hashes match and LOAD-OPEN-01 disposition is signed; other R96 inputs stay open.", "state": "NOT EXECUTED"},
        {"operation": "FR12-HOLD-02", "stage": "RELEASE HOLD", "method": "Qualified mechanical/metrology review of raw data, uncertainty, reconciliation, source parity and calculations.", "acceptance": "No fabrication, motion, connection or energization authority; disposition applies only to LOAD-OPEN-01 evidence.", "state": "OPEN"},
    ]
    write_csv(OUT / "received-measurement-plan.csv", plan_rows)

    sensitivity_rows: list[dict[str, object]] = []
    for mass_g in (20, 30, 40, 50, 60):
        for radius_mm in (bbox_radius, 35.0, 40.0, 45.0, 50.0):
            mass_kg = mass_g / 1000.0
            radius_m = radius_mm / 1000.0
            sensitivity_rows.append({
                "mass_upper_g": f"{mass_g:.3f}",
                "radius_upper_mm": f"{radius_mm:.9f}",
                "ixx_upper_bound_kg_m2": f"{mass_kg * radius_m**2:.12f}",
                "gravity_upper_bound_nm": f"{mass_kg * G * radius_m:.9f}",
                "status": "SENSITIVITY ONLY - NOT A MEASURED VALUE OR ACCEPTANCE LIMIT",
            })
    write_csv(OUT / "mass-radius-bound-sensitivity.csv", sensitivity_rows)

    form_fields = [
        "record_id", "verification_id", "execution_state", "date", "inspector", "repo_commit",
        "received_article_id", "source_kit_sku", "source_kit_lot", "component_scope", "part_identity",
        "installed_configuration_hash", "scale_id", "calibration_reference", "scale_readability_g",
        "tare_reference", "repeat_count", "mean_mass_g", "expanded_uncertainty_mass_g",
        "y_min_mm", "y_max_mm", "z_min_mm", "z_max_mm", "expanded_uncertainty_y_mm",
        "expanded_uncertainty_z_mm", "radius_bound_mm", "ixx_upper_bound_kg_m2",
        "gravity_upper_bound_nm", "com_method", "reaction_support_span_mm", "reaction_a_g",
        "reaction_b_g", "support_a_to_j2_datum_mm", "com_y_mm", "com_z_mm",
        "expanded_uncertainty_com_y_mm", "expanded_uncertainty_com_z_mm", "raw_data_reference",
        "photo_reference", "qualified_disposition", "notes",
    ]
    form_rows = []
    for record_id, scope in (
        ("NOT-EXECUTED-FR12-FRAME", "FR12-H101 FRAME ONLY"),
        ("NOT-EXECUTED-FR12-IDLER", "HN12-I101 / OUTPUT MOVING HARDWARE / INSTALLED FASTENERS"),
        ("NOT-EXECUTED-FR12-COMPLETE", "COMPLETE RECEIVED J2 MOVING FRAME SUBASSEMBLY"),
    ):
        row = {field: "" for field in form_fields}
        row.update({"record_id": record_id, "verification_id": "INSPECT-MECH-007", "execution_state": "NOT EXECUTED", "component_scope": scope, "qualified_disposition": "OPEN", "notes": "TEMPLATE ROW - NO PHYSICAL RESULT"})
        form_rows.append(row)
    write_csv(FORM, form_rows)

    repeat_rows = []
    for scope in ("FR12-H101 FRAME ONLY", "HN12-I101 / OUTPUT MOVING HARDWARE / INSTALLED FASTENERS", "COMPLETE RECEIVED J2 MOVING FRAME SUBASSEMBLY"):
        for index in range(1, 11):
            repeat_rows.append({"record_id": "NOT-EXECUTED", "component_scope": scope, "reading_index": index, "balance_reading_g": "", "tare_before_g": "", "tare_after_g": "", "ambient_temperature_c": "", "raw_file_or_photo": "", "execution_state": "NOT EXECUTED", "notes": "TEMPLATE ROW"})
    write_csv(REPEAT_FORM, repeat_rows)

    sources = [
        {"source_id": "FR12-SRC-01", "title": "ROBOTIS FR12-H101K Set", "locator": "https://www.robotis.us/fr12-h101k-set/", "revision_or_date": "live page; no formal revision displayed; checked 2026-08-08", "use": "SKU, included HN12-I101, hardware contents and conflicting 0.10 lb commerce field", "sha256": "LIVE PRIMARY PAGE - NO LOCAL SNAPSHOT"},
        {"source_id": "FR12-SRC-02", "title": "ROBOTIS HN12-I101 Set", "locator": "https://www.robotis.us/hn12-i101-set/", "revision_or_date": "live page; no formal revision displayed; checked 2026-08-08", "use": "SKU, component contents and conflicting 0.20 lb commerce field", "sha256": "LIVE PRIMARY PAGE - NO LOCAL SNAPSHOT"},
        {"source_id": "FR12-SRC-03", "title": "ROBOTIS X430 model reference drawings", "locator": "https://docs.robotis.com/docs/dxl/model_reference/x_series/xh_series/xh430-v210/", "revision_or_date": "live page; checked 2026-08-08; FR12 drawing dated 2026-01-07", "use": "official FR12-H101 drawing/STEP provenance", "sha256": "LIVE PRIMARY PAGE - LOCAL FILES HASHED SEPARATELY"},
        {"source_id": "FR12-SRC-04", "title": "controlled FR12-H101 STEP", "locator": str(h101_path.relative_to(ROOT)).replace("\\", "/"), "revision_or_date": "manufacturer file acquired R91", "use": "frame-only geometry and support envelope", "sha256": sha256(h101_path)},
        {"source_id": "FR12-SRC-05", "title": "controlled FR12-H101 drawing", "locator": str((VENDOR / "fr12_h101_ref.pdf").relative_to(ROOT)).replace("\\", "/"), "revision_or_date": "drawing date 2026-01-07", "use": "received source-parity reference", "sha256": sha256(VENDOR / "fr12_h101_ref.pdf")},
        {"source_id": "FR12-SRC-06", "title": "R97 generator", "locator": "tools/generate_hr_v0_fr12_mass_metrology.py", "revision_or_date": "repository-controlled", "use": "reproduce geometry, bounds, templates and guide", "sha256": sha256(Path(__file__))},
    ]
    write_csv(OUT / "source-register.csv", sources)

    status = {
        "identifier": "HR-V0-FR12-MASS-MET-P0.1",
        "state": "MEASUREMENT ROUTE DEFINED - ZERO PHYSICAL EXECUTION",
        "commerce_weight_credit": False,
        "received_article_exists": False,
        "measurement_executed": False,
        "load_open_01_closed": False,
        "mass_closed": False,
        "com_closed": False,
        "inertia_closed": False,
        "x430_selected": False,
        "p1_1_selected": False,
        "fabrication_released": False,
        "motion_released": False,
        "connection_released": False,
        "energization_released": False,
        "open_holds": ["FR12-HOLD-01", "FR12-HOLD-02"],
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    html = f"""<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>HR-V0 FR12 moving-mass metrology</title><style>
:root{{--sky:#66c7f4;--navy:#082b4c;--blue:#0b4f8a;--gold:#f3b61f;--paper:#f7fbff;--hold:#fff4cc}}*{{box-sizing:border-box}}body{{margin:0;font:clamp(16px,1.2vw,18px)/1.55 Arial,sans-serif;color:var(--navy);background:#fff}}header{{padding:clamp(1.25rem,4vw,3rem);background:linear-gradient(135deg,var(--sky),#e9f8ff);border-bottom:6px solid var(--gold)}}h1{{font-size:clamp(2rem,5vw,4.5rem);line-height:1.05;margin:.3rem 0 1rem}}h2{{font-size:clamp(1.45rem,2.6vw,2.3rem)}}main{{max-width:1250px;margin:auto;padding:clamp(1rem,4vw,3rem)}}.warning{{font-weight:700;padding:1rem;border:3px solid var(--gold);background:var(--hold);border-radius:.8rem}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:1rem}}.card{{padding:1.1rem;border:3px solid var(--blue);border-radius:1rem;background:var(--paper)}}.meta,.tag{{font-size:13px;font-weight:700}}label{{display:block;font-weight:700;margin-top:1rem}}input{{width:100%;font:inherit;padding:.65rem;border:2px solid var(--blue);border-radius:.5rem}}output{{display:block;font-size:clamp(1.25rem,2vw,1.8rem);font-weight:700;color:var(--blue)}}table{{width:100%;border-collapse:collapse;display:block;overflow:auto}}th,td{{font-size:16px;text-align:left;vertical-align:top;padding:.75rem;border-bottom:1px solid #9db7ca;min-width:150px}}th{{background:var(--navy);color:#fff}}a{{color:var(--blue);font-weight:700}}footer{{padding:1.5rem;background:var(--navy);color:#fff}}@media(max-width:600px){{body{{font-size:16px}}th,td{{font-size:16px}}}}
</style></head><body><header><div class=\"meta\">HR-V0-FR12-MASS-MET-P0.1 · R97</div><h1>Measure the missing frame. Do not guess it.</h1><div class=\"warning\">PRELIMINARY — UNPOWERED MEASUREMENT ROUTE ONLY. NOT APPROVED FOR PURCHASE, ASSEMBLY, MOTION, CONNECTION, FABRICATION, OR ENERGIZATION.</div></header><main><section><h2>Why the storefront weights are rejected</h2><div class=\"grid\"><article class=\"card\"><span class=\"tag\">FR12-H101K SET</span><output>0.10 lb</output><p>Official commerce field for a kit that includes the idler set.</p></article><article class=\"card\"><span class=\"tag\">INCLUDED HN12-I101 SET</span><output>0.20 lb</output><p>Official commerce field for the included sub-kit. The two values cannot establish installed component mass.</p></article><article class=\"card\"><span class=\"tag\">DISPOSITION</span><output>NO MASS CREDIT</output><p>Use calibrated received-part measurements and controlled uncertainty.</p></article></div></section><section><h2>Exact frame geometry we can use</h2><div class=\"grid\"><article class=\"card\"><strong>Frame-only STEP volume</strong><output>{volume:.6f} mm³</output></article><article class=\"card\"><strong>Frame-only uniform centroid Y</strong><output>{center.y:.6f} mm</output></article><article class=\"card\"><strong>Conservative frame bounding radius</strong><output>{bbox_radius:.6f} mm</output></article></div><p>The radius covers only the manufacturer FR12-H101 STEP. Received idler, output hardware, spacers and fasteners must be measured as an installed envelope.</p></section><section><h2>Measured-bound calculator</h2><p>Enter accepted upper mass and radial envelope values only. The calculator is exploratory and stores no evidence.</p><div class=\"grid\"><article class=\"card\"><label for=\"mass\">Upper mass including uncertainty (g)</label><input id=\"mass\" type=\"number\" min=\"0\" step=\"0.01\" value=\"40\"><label for=\"radius\">Upper radial envelope including uncertainty (mm)</label><input id=\"radius\" type=\"number\" min=\"0\" step=\"0.01\" value=\"40\"></article><article class=\"card\"><strong>Conservative Ixx bound</strong><output id=\"ixx\">—</output><strong>Gravity-moment bound</strong><output id=\"grav\">—</output></article></div></section><section><h2>Reaction-fixture COM calculator</h2><div class=\"grid\"><article class=\"card\"><label for=\"ra\">Reaction A after fixture tare (g-equivalent)</label><input id=\"ra\" type=\"number\" min=\"0\" step=\"0.01\" value=\"20\"><label for=\"rb\">Reaction B after fixture tare (g-equivalent)</label><input id=\"rb\" type=\"number\" min=\"0\" step=\"0.01\" value=\"20\"><label for=\"span\">Support span (mm)</label><input id=\"span\" type=\"number\" min=\"0\" step=\"0.01\" value=\"100\"><label for=\"offset\">Support A coordinate from J2 datum (mm)</label><input id=\"offset\" type=\"number\" step=\"0.01\" value=\"-50\"></article><article class=\"card\"><strong>Calculated COM coordinate</strong><output id=\"com\">—</output><p>Repeat in two orthogonal orientations. Fixture deflection, reaction closure and uncertainty require qualified acceptance.</p></article></div></section><section><h2>Execution sequence</h2><table><thead><tr><th>Stage</th><th>What must happen</th><th>Current state</th></tr></thead><tbody><tr><td>Receive</td><td>Acquire only after separate program-owner approval; quarantine and inventory RM-X52/XM430 articles.</td><td>NOT EXECUTED</td></tr><tr><td>Measure loose</td><td>Ten calibrated readings each for frame, idler/hardware and exact fastener group.</td><td>NOT EXECUTED</td></tr><tr><td>Assembly hold</td><td>Approve screw length, engagement, spacers, torque, locking and reuse before temporary assembly.</td><td>OPEN</td></tr><tr><td>Measure installed</td><td>Reconcile combined mass, envelope, COM and conservative inertia bound.</td><td>NOT EXECUTED</td></tr><tr><td>Qualified disposition</td><td>Review raw data, uncertainty and source parity before replacing LOAD-OPEN-01.</td><td>OPEN</td></tr></tbody></table></section><p><a href=\"../../../docs/hr-v0-fr12-moving-mass-metrology-p0.1.md\">Controlled design record</a> · <a href=\"../../../cad/hr-v0/generated/fr12-moving-mass-metrology-p0.1/received-measurement-plan.csv\">Measurement plan</a> · <a href=\"../../../tests/forms/hr-v0-fr12-moving-subassembly-measurement-template.csv\">Result form</a> · <a href=\"../../../tests/forms/hr-v0-fr12-mass-repeat-template.csv\">Raw repeats</a></p></main><footer>LOAD-OPEN-01 remains OPEN. P0.7 remains controlled; P1.1 and X430 remain unselected. No physical result or work authorization exists.</footer><script>
const ids=['mass','radius','ra','rb','span','offset'];const e=Object.fromEntries(ids.map(x=>[x,document.getElementById(x)]));function calc(){{const m=Number(e.mass.value)/1000,r=Number(e.radius.value)/1000;document.getElementById('ixx').textContent=(m*r*r).toFixed(12)+' kg·m²';document.getElementById('grav').textContent=(m*{G}*r).toFixed(6)+' N·m';const a=Number(e.ra.value),b=Number(e.rb.value),s=Number(e.span.value),o=Number(e.offset.value);document.getElementById('com').textContent=(a+b)>0?(o+b*s/(a+b)).toFixed(3)+' mm':'SELECTION REQUIRED'}}ids.forEach(x=>e[x].addEventListener('input',calc));calc();
</script></body></html>"""
    GUIDE.parent.mkdir(parents=True, exist_ok=True)
    GUIDE.write_text(html, encoding="utf-8")

    print(json.dumps({
        "identifier": status["identifier"],
        "frame_volume_mm3": round(volume, 6),
        "frame_bbox_radius_mm": round(bbox_radius, 6),
        "commerce_weight_credit": False,
        "measurement_rows": len(form_rows),
        "raw_repeat_rows": len(repeat_rows),
        "plan_rows": len(plan_rows),
        "load_open_01_closed": False,
    }, indent=2))


if __name__ == "__main__":
    main()
