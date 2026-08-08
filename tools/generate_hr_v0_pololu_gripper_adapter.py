#!/usr/bin/env python3
"""Generate the held HR-V0 Pololu 3551 direct-adapter candidate.

Coordinates are Project Button X lateral, Y outward along the forearm/gripper,
and Z vertical.  Manufacturer STEP geometry is transformed only for the fit
study.  No candidate is released for procurement or fabrication.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
POL = ROOT / "cad/vendor/pololu/micro-gripper-3551-r111"
OUT = ROOT / "cad/hr-v0/generated/pololu-gripper-adapter-p0.1"
GUIDE = ROOT / "release/hr-v0/gripper-adapter-p0.1"
IDENTIFIER = "HR-V0-GRIP-ADAPT-P0.1"
WARNING = "PRELIMINARY - NOT RELEASED FOR PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION"
TX, TY, TZ = 2.980409242638878, 3.719474107556752, 17.512087117409283
AL_DENSITY_G_PER_CM3 = 2.70
CATALOG_GRIPPER_MASS_G = 30.0
CURRENT_MOVING_SUBTOTAL_G = 577.091


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def normalize_step(path: Path) -> None:
    """Remove exporter-only line-end whitespace without changing STEP data."""
    data = path.read_bytes()
    path.write_bytes(re.sub(rb"[ \t]+(?=\r?\n)", b"", data))


def adapter() -> cq.Workplane:
    backplate = cq.Workplane("XY").box(40.0, 5.0, 40.0).translate((0, -2.5, 0))
    profile = [(0, -12), (0, -4), (6, 0), (7, 8), (13.5, 8), (23.5, 0), (23.5, -8), (14.5, -10), (6, -12)]
    left = cq.Workplane("YZ").polyline(profile).close().extrude(3.0).translate((-13.2, 0, 0))
    right = cq.Workplane("YZ").polyline(profile).close().extrude(3.0).translate((10.2, 0, 0))
    part = backplate.union(left).union(right)

    # Two gripper fastener holes, transverse through both 3 mm cheeks.
    for y, z in ((10.49, 4.0), (19.69, -4.0)):
        cutter = cq.Workplane("YZ", origin=(-14.0, y, z)).circle(2.2).extrude(28.0)
        part = part.cut(cutter)

    # Two beam-side M5 clearance holes and 90 degree rear countersinks.
    plane = cq.Plane(origin=(0, -5.0, 0), xDir=(1, 0, 0), normal=(0, 1, 0))
    part = part.faces("<Y").workplane().pushPoints([(0, 10), (0, -10)]).cskHole(5.5, 11.3, 90, depth=5.0)
    return part


def dimension_svg() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1200" viewBox="0 0 1800 1200" role="img" aria-labelledby="title desc"><title id="title">HR-V0 Pololu gripper direct-adapter candidate</title><desc id="desc">Dimensioned preliminary front and side views with open release holds.</desc><style>text{{font-family:Arial,sans-serif;fill:#102a43;font-size:20px}}.title{{font-size:38px;font-weight:700;fill:#082b55}}.head{{font-size:27px;font-weight:700;fill:#082b55}}.warn{{font-size:20px;font-weight:700;fill:#8b1e1e}}.part{{fill:#dff3ff;stroke:#082b55;stroke-width:4}}.hole{{fill:white;stroke:#082b55;stroke-width:3}}.dim{{stroke:#082b55;stroke-width:2;fill:none}}.ctr{{stroke:#0b63a3;stroke-width:2;stroke-dasharray:10 7}}.box{{fill:white;stroke:#afd5e9;stroke-width:3}}.hold{{fill:#fff7ed;stroke:#8b1e1e;stroke-width:3}}</style><rect width="1800" height="1200" fill="#f7fbff"/><text x="55" y="62" class="title">HR-V0 direct gripper adapter candidate</text><text x="55" y="103" class="warn">{WARNING}</text><text x="55" y="140">{IDENTIFIER} · dimensions in mm · nominal model only · 2026-08-08</text>
<text x="90" y="220" class="head">Beam face view (X-Z)</text><rect x="120" y="260" width="480" height="480" class="part"/><line x1="360" y1="240" x2="360" y2="760" class="ctr"/><circle cx="360" cy="380" r="67.8" class="hole"/><circle cx="360" cy="620" r="67.8" class="hole"/><circle cx="360" cy="380" r="33" class="hole"/><circle cx="360" cy="620" r="33" class="hole"/><text x="150" y="800">40.0 X × 40.0 Z × 5.0 Y backplate</text><text x="150" y="835">2 × Ø5.50 THRU; Ø11.30 × 90° CSK</text><text x="150" y="870">axes X=0, Z=±10.00</text>
<text x="760" y="220" class="head">Side-web view (Y-Z)</text><path d="M780 620 L780 460 L900 380 L920 300 L1050 300 L1250 460 L1250 620 L1070 660 L900 700 L780 700 Z" class="part"/><circle cx="990" cy="420" r="35" class="hole"/><circle cx="1174" cy="580" r="35" class="hole"/><line x1="990" y1="390" x2="1174" y2="550" class="dim"/><text x="820" y="770">2 × Ø4.40 transverse; axes (Y,Z)</text><text x="820" y="805">10.49,+4.00 and 19.69,-4.00</text><text x="820" y="840">axis separation: 9.20 Y / 8.00 Z / 12.19 true</text><text x="820" y="875">3.00 cheek thickness; 20.40 inside gap</text>
<rect x="80" y="935" width="1640" height="205" rx="16" class="hold"/><text x="110" y="980" class="head">Release holds</text><text x="110" y="1020">Material candidate: 6061-T651 plate under ASTM B209. Exact stock, temper certificate, finish, tolerances and DFM: SELECTION REQUIRED.</text><text x="110" y="1060">POM grade/allowables, M4 screw/washer/spacer/nut stack, fastener torque/locking/reuse, guard, cable and received fit/proof: OPEN.</text><text x="110" y="1100">M5×20 beam screws are an engagement screen only. Drawing and model are not fabrication authority.</text></svg>'''


def guide_html(adapter_mass: float, remaining: float) -> str:
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{IDENTIFIER}</title><script type="module" src="../../vendor/model-viewer/4.1.0/model-viewer.min.js"></script><style>:root{{--ink:#082b55;--blue:#0b4f8a;--sky:#dff3ff;--gold:#f5bd24;--paper:#f8fbff;--danger:#7d1d1d}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}header{{background:var(--ink);color:white;padding:clamp(1.5rem,4vw,3rem)}}main{{max-width:1120px;margin:auto;padding:1.25rem}}h1{{font-size:clamp(2rem,5vw,4rem);line-height:1.05}}h2{{font-size:clamp(1.5rem,3vw,2.2rem)}}.warning{{background:var(--gold);color:#231800;font-weight:800;padding:.8rem;border:3px solid #231800}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1rem}}.card{{background:white;border:2px solid var(--blue);border-radius:12px;padding:1rem}}.metric{{font-size:1.6rem;font-weight:800}}model-viewer{{display:block;width:100%;height:min(70vh,620px);min-height:420px;background:var(--sky);border:3px solid var(--blue)}}table{{border-collapse:collapse;width:100%;min-width:760px}}th,td{{padding:.8rem;border-bottom:1px solid #abc7df;text-align:left;vertical-align:top}}th{{background:var(--sky)}}.scroll{{overflow:auto;border:2px solid var(--blue)}}small{{font-size:14px}}.tag{{font-size:14px;font-weight:800}}footer{{margin-top:2rem;background:var(--ink);color:white;padding:1rem}}@media(max-width:620px){{main{{padding:.8rem}}model-viewer{{min-height:340px}}}}</style></head><body><header><div class="warning">{WARNING}</div><p class="tag">{IDENTIFIER} · R112 candidate</p><h1>Pololu gripper direct-adapter study</h1><p>Exact manufacturer STEP geometry aligned to a source-controlled one-piece 6061 clevis candidate. This is a fit and load screen, not a selected configuration.</p></header><main><model-viewer src="../../../cad/hr-v0/generated/pololu-gripper-adapter-p0.1/hr-v0-pololu-gripper-adapter-assembly-p0.1.glb" camera-controls shadow-intensity="1" exposure="1" alt="Interactive three-dimensional view of the blue adapter and gold Pololu gripper"></model-viewer><div class="grid"><article class="card"><div class="metric">0.300 mm</div><p>minimum nominal cheek-to-gripper clearance</p></article><article class="card"><div class="metric">{adapter_mass:.3f} g</div><p>adapter mass from nominal volume × 2.70 g/cm³</p></article><article class="card"><div class="metric">{remaining:.3f} g</div><p>arithmetic 750 g headroom before guard, fasteners, pads and moving cable</p></article></div><h2>What the model closes</h2><div class="scroll"><table><thead><tr><th>Item</th><th>Nominal result</th><th>Boundary</th></tr></thead><tbody><tr><td>Beam interface</td><td>2 × Ø5.50/Ø11.30 countersunk holes at X=0, Z=±10</td><td>M5×20 gives a nominal 15 mm engagement screen in the published 22.23 mm taps; tolerance, torque and locking remain open.</td></tr><tr><td>Gripper axes</td><td>Ø4.40 at Y/Z 10.49/+4.00 and 19.69/−4.00</td><td>Derived from the manufacturer STEP and drawing; exact M4 stack is SELECTION REQUIRED.</td></tr><tr><td>Collision</td><td>No nominal solid intersection; 0.300 mm minimum clearance</td><td>Tolerance stack and received metrology are not closed.</td></tr><tr><td>Static screen</td><td>10× sensitivity gives about 13.5 MPa at the narrow aluminum web and about 70.6 N idealized M4-axis couple load</td><td>Not an allowable or proof. POM ear grade, bearing/bypass strength and load distribution remain open.</td></tr></tbody></table></div><h2>Blocking evidence</h2><p>The gripper is still only a preferred evaluation candidate. Before selection: reconcile GRIP-002, release the guard and cable path, select every fastener and tolerance, obtain received metrology, accept a proof fixture and load multiplier, and obtain qualified mechanical review. The associated 6 V/PWM/feedback design is a separate ordinary-control candidate with zero safety credit.</p></main><footer>No ordering, machining, assembly, connection, motion or energization is authorized by this guide.</footer></body></html>'''


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    GUIDE.mkdir(parents=True, exist_ok=True)
    part = adapter()
    gripper = cq.importers.importStep(str(POL / "micro-gripper.step")).translate((TX, TY, TZ))

    cq.exporters.export(part, str(OUT / "hr-v0-pololu-gripper-adapter-p0.1.step"))
    normalize_step(OUT / "hr-v0-pololu-gripper-adapter-p0.1.step")
    cq.exporters.export(part, str(OUT / "hr-v0-pololu-gripper-adapter-p0.1.stl"), tolerance=0.02, angularTolerance=0.1)
    assembly = cq.Assembly(name=IDENTIFIER)
    assembly.add(part, name="ADAPTER_CANDIDATE", color=cq.Color(0.18, 0.55, 0.85))
    assembly.add(gripper, name="POLOLU_3551_MANUFACTURER_STEP", color=cq.Color(0.95, 0.68, 0.12))
    assembly.save(str(OUT / "hr-v0-pololu-gripper-adapter-assembly-p0.1.step"))
    normalize_step(OUT / "hr-v0-pololu-gripper-adapter-assembly-p0.1.step")
    assembly.save(str(OUT / "hr-v0-pololu-gripper-adapter-assembly-p0.1.glb"))

    volume_mm3 = part.val().Volume()
    adapter_mass_g = volume_mm3 / 1000.0 * AL_DENSITY_G_PER_CM3
    remaining_g = 750.0 - CURRENT_MOVING_SUBTOTAL_G - CATALOG_GRIPPER_MASS_G - adapter_mass_g
    separation = (9.2**2 + 8.0**2) ** 0.5
    load_1x_nm = 0.1 * 9.80665 * 0.0628 + 0.03 * 9.80665 * 0.0628 + adapter_mass_g / 1000.0 * 9.80665 * 0.0235
    load_10x_nm = 10.0 * load_1x_nm
    section_modulus_mm3 = 2.0 * 3.0 * 8.0**2 / 6.0
    stress_mpa = load_10x_nm * 1000.0 / section_modulus_mm3
    m4_couple_n = load_10x_nm * 1000.0 / separation

    write_csv(OUT / "feature-register.csv", [
        {"feature_id":"PAF-001","feature":"backplate","nominal":"40 X x 40 Z x 5 Y mm","basis":"project candidate","state":"NOT RELEASED"},
        {"feature_id":"PAF-002","feature":"beam holes","nominal":"2 x diameter 5.50 through; diameter 11.30 x 90 degree countersink; X=0 Z=+/-10.00","basis":"current 20-2040 end-tap and retained M5 countersunk interface","state":"TOLERANCE/FASTENER PROOF OPEN"},
        {"feature_id":"PAF-003","feature":"gripper holes","nominal":"2 x diameter 4.40 transverse; Y/Z 10.49/+4.00 and 19.69/-4.00","basis":"Pololu drawing/STEP axes","state":"M4 STACK/POM PROOF OPEN"},
        {"feature_id":"PAF-004","feature":"cheeks","nominal":"3.00 thick each; 20.40 inside gap","basis":"19.80 manufacturer STEP ear envelope plus 0.30 nominal each side","state":"TOLERANCE STACK OPEN"},
    ])
    write_csv(OUT / "transform-register.csv", [{"record_id":"PAT-001","source":"Pololu item 3551 manufacturer STEP","tx_mm":f"{TX:.12f}","ty_mm":f"{TY:.12f}","tz_mm":f"{TZ:.12f}","project_hole_axes":"Y/Z 10.49/+4.00 and 19.69/-4.00","rear_gap_mm":"0.500","state":"NOMINAL CANDIDATE - RECEIVED REGISTRATION OPEN"}])
    write_csv(OUT / "analysis-register.csv", [
        {"analysis_id":"PAA-001","quantity":"adapter nominal volume","result":f"{volume_mm3:.6f} mm3","basis":"CadQuery solid","boundary":"stock/finish/tolerance not included"},
        {"analysis_id":"PAA-002","quantity":"adapter calculated mass","result":f"{adapter_mass_g:.6f} g","basis":"volume x 2.70 g/cm3","boundary":"not measured; optional hardware excluded"},
        {"analysis_id":"PAA-003","quantity":"remaining arithmetic moving-mass headroom","result":f"{remaining_g:.6f} g","basis":"750 - 577.091 - 30 - adapter","boundary":"guard/pads/fasteners/cable/adhesive and received mass excluded"},
        {"analysis_id":"PAA-004","quantity":"gravity sensitivity moment","result":f"{load_1x_nm:.6f} N m at 1x; {load_10x_nm:.6f} N m at 10x","basis":"100 g payload and conservative far-tip gripper/adapter placement","boundary":"accepted multiplier and dynamic case SELECTION REQUIRED"},
        {"analysis_id":"PAA-005","quantity":"narrow-web bending screen at 10x","result":f"{stress_mpa:.3f} MPa","basis":f"combined idealized section modulus {section_modulus_mm3:.3f} mm3","boundary":"screen only; no allowable, fatigue, notch or proof credit"},
        {"analysis_id":"PAA-006","quantity":"M4-axis ideal couple at 10x","result":f"{m4_couple_n:.3f} N over {separation:.6f} mm","basis":"ideal two-point couple","boundary":"POM bearing/bypass/bending and load distribution open"},
    ])
    write_csv(OUT / "collision-register.csv", [
        {"record_id":"PAC-001","pair":"adapter / Pololu solid 1","intersection":"NONE","minimum_nominal_separation_mm":"0.300","boundary":"received tolerance/deflection open"},
        {"record_id":"PAC-002","pair":"adapter / Pololu solid 2","intersection":"NONE","minimum_nominal_separation_mm":"8.122","boundary":"received tolerance/deflection open"},
        {"record_id":"PAC-003","pair":"adapter / Pololu solid 3","intersection":"NONE","minimum_nominal_separation_mm":"11.161","boundary":"received tolerance/deflection open"},
    ])
    write_csv(OUT / "hold-register.csv", [
        {"hold_id":f"PAH-{i:03d}","scope":scope,"evidence_required":evidence,"state":"OPEN"}
        for i, (scope, evidence) in enumerate([
            ("CANDIDATE SELECTION", "Approved task/GRIP-002 disposition and signed configuration choice"),
            ("MATERIAL", "Exact 6061 stock/temper/spec certificate, finish and released allowables"),
            ("TOLERANCE", "Qualified drawing tolerance/GD&T and full received stack including 0.30 mm cheek clearance"),
            ("BEAM FASTENERS", "Exact retained/new M5 identity, length, countersink fit, engagement, torque, locking and reuse"),
            ("GRIPPER FASTENERS", "Exact M4 screws, washers, spacers, nuts, length, torque, locking and retention"),
            ("POM EARS", "Manufacturer material grade/allowables or accepted physical bearing/bypass/bending proof"),
            ("LOAD CASE", "Accepted payload, lever arm, duty, misuse and static/dynamic proof multiplier"),
            ("GUARD/CABLE", "Guard, pads, pinch boundary and moving power/PWM/feedback cable path"),
            ("DFM/FAI", "Qualified machining review, deburr/finish route and first-article inspection"),
            ("RECEIVED FIT", "Identity, dimensions, mass, free motion, noninterference and fastener inspection"),
            ("PHYSICAL PROOF", "Accepted fixture, calibrated load, deformation/damage criteria and executed record"),
            ("QUALIFIED REVIEW", "Signed mechanical review and separate work authorization"),
        ], start=1)
    ])
    write_csv(OUT / "source-register.csv", [
        {"source_id":"PAS-001","record":"Pololu Micro Gripper with Position Feedback Servo item 3551 dimensions","revision_date":"drawing 31 August 2018; accessed 2026-08-08","locator":"cad/vendor/pololu/micro-gripper-3551-r111/micro-gripper-dimensions.pdf","sha256":sha256(POL / "micro-gripper-dimensions.pdf"),"use":"mounting axes and nominal envelope"},
        {"source_id":"PAS-002","record":"Pololu item 3551 manufacturer STEP","revision_date":"current resource payload accessed 2026-08-08; no embedded printed revision","locator":"cad/vendor/pololu/micro-gripper-3551-r111/micro-gripper.step","sha256":sha256(POL / "micro-gripper.step"),"use":"exact-source nominal collision and axis reconstruction"},
        {"source_id":"PAS-003","record":"Kaiser 6061 Sheet, Coil and Plate","revision_date":"Sheet Rev 05 / Plate Rev 06; controlled R105 copy","locator":"cad/vendor/kaiser/6061-t651-r105/Kaiser_Aluminum_6061_Sheet_Coil_and_Plate.pdf","sha256":sha256(ROOT / "cad/vendor/kaiser/6061-t651-r105/Kaiser_Aluminum_6061_Sheet_Coil_and_Plate.pdf"),"use":"material identity/density screen; typical values are not allowables"},
    ])
    summary = {"identifier":IDENTIFIER,"date":"2026-08-08","status":"PREFERRED EVALUATION PATH - NOT SELECTED OR RELEASED","adapter_volume_mm3":round(volume_mm3,6),"adapter_mass_g":round(adapter_mass_g,6),"gripper_catalog_mass_g":30.0,"current_moving_subtotal_g":577.091,"remaining_arithmetic_headroom_g":round(remaining_g,6),"minimum_nominal_clearance_mm":0.3,"rear_nominal_gap_mm":0.5,"hold_count":12,"requirements_closed":0,"procurement_release":False,"fabrication_release":False,"assembly_release":False,"motion_release":False,"energization_release":False,"warning":WARNING}
    (OUT / "package-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (OUT / "hr-v0-pololu-gripper-adapter-drawing-p0.1.svg").write_text(dimension_svg(), encoding="utf-8")
    (GUIDE / "index.html").write_text(guide_html(adapter_mass_g, remaining_g), encoding="utf-8")
    print(f"Generated {IDENTIFIER}: {volume_mm3:.3f} mm3, {adapter_mass_g:.3f} g, {remaining_g:.3f} g arithmetic headroom")
    print(WARNING)


if __name__ == "__main__":
    main()
