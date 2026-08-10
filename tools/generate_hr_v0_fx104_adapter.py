"""Generate the R105 FX104-C01 fabrication-candidate package.

This defines the custom adapter itself. It does not release the surrounding
Magtrol accessory, PT hardware, assembly, proof test, or powered work.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path

import cadquery as cq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import generate_hr_v0_arm_architecture as base  # noqa: E402
import generate_hr_v0_x430_brake_support as r104  # noqa: E402

IDENTIFIER = "HR-V0-FX104-C01-FAB-P0.1"
PART = "FX104-C01"
WARNING = "PRELIMINARY - ADAPTER FABRICATION CANDIDATE ONLY - NOT RELEASED FOR QUOTATION, PROCUREMENT, MACHINING, ASSEMBLY, CONNECTION, POWERED TEST, MOTION, OR ENERGIZATION"
OUT = ROOT / "cad" / "hr-v0" / "generated" / "fx104-c01-p0.1"
WEB = ROOT / "release" / "hr-v0" / "fx104-c01-p0.1"
KAISER = ROOT / "cad" / "vendor" / "kaiser" / "6061-t651-r105"
GENERATED_ROOT = ROOT / "cad" / "hr-v0" / "generated"
GENERATED_SOURCE_MANIFEST = GENERATED_ROOT / "SOURCE-MANIFEST.csv"
MECHANICAL_REVISION = "HR-V0-MECH-R0.1-PRELIMINARY"
GENERATED_TEXT_SUFFIXES = {".csv", ".dxf", ".json", ".step", ".svg", ".txt"}

LENGTH_X = 90.0
WIDTH_Y = 160.0
THICKNESS = 24.0
UPPER_Y = 52.0
LOWER_X = 30.0
LOWER_Y = 50.0
UPPER_DRILL_DIA = 5.0
UPPER_THREAD = "M6 x 1 - 6H"
UPPER_THREAD_DEPTH = 12.0
UPPER_DRILL_DEPTH = 18.0
LOWER_HOLE_DIA = 6.6
MATERIAL = "6061-T651 aluminum plate, ASTM B209, certified"
DENSITY_G_CM3 = 2.70
ELASTIC_MODULUS_MPA = 68_300.0
TYPICAL_YIELD_MPA = 276.0
SCREEN_YIELD_MPA = 240.0
GRAVITY_FACTOR = 3.0
TORQUE_FACTOR = 2.0
BRAKE_WEIGHT_N = 5.85 * 9.80665
WEIGHT_MOMENT_NM = BRAKE_WEIGHT_N * 0.1000082
STALL_TORQUE_NM = 4.1


def write_csv(path: Path, records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def generated_sha256(path: Path) -> str:
    if path.suffix.lower() in GENERATED_TEXT_SUFFIXES:
        data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        return hashlib.sha256(data).hexdigest().upper()
    return sha256(path)


def write_generated_source_manifest() -> None:
    """Synchronize the existing root generated-artifact manifest."""
    records = []
    for path in sorted(GENERATED_ROOT.rglob("*"), key=lambda item: item.as_posix().lower()):
        if path.is_file() and path != GENERATED_SOURCE_MANIFEST:
            records.append({
                "file":path.relative_to(GENERATED_ROOT).as_posix(),
                "sha256":generated_sha256(path),
                "revision":MECHANICAL_REVISION,
                "status":"PRELIMINARY - NOT RELEASED FOR FABRICATION OR ENERGIZATION",
            })
    write_csv(GENERATED_SOURCE_MANIFEST, records)


def part_geometry() -> cq.Shape:
    """Nominal solid. Thread callout is controlled by the drawing/feature table."""
    shape = cq.Solid.makeBox(LENGTH_X, WIDTH_Y, THICKNESS, cq.Vector(-LENGTH_X / 2, -WIDTH_Y / 2, 0))
    for y in (-UPPER_Y, UPPER_Y):
        shape = shape.cut(cq.Solid.makeCylinder(UPPER_DRILL_DIA / 2, UPPER_DRILL_DEPTH, cq.Vector(0, y, THICKNESS - UPPER_DRILL_DEPTH), cq.Vector(0, 0, 1)))
    for x in (-LOWER_X, LOWER_X):
        for y in (-LOWER_Y, LOWER_Y):
            shape = shape.cut(cq.Solid.makeCylinder(LOWER_HOLE_DIA / 2, THICKNESS + 0.4, cq.Vector(x, y, -0.2), cq.Vector(0, 0, 1)))
    return shape


def drawing_svg(path: Path) -> None:
    path.write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1250" viewBox="0 0 1800 1250" style="max-width:100%;height:auto"><style>
text{{font-family:Arial,sans-serif;fill:#102a43;font-size:20px}}.h1{{font-size:38px;font-weight:700;fill:#082b55}}.h2{{font-size:27px;font-weight:700;fill:#082b55}}.warn{{font-size:20px;font-weight:700;fill:#8b1e1e}}.note{{font-size:20px}}.dim{{font-size:20px;fill:#082b55}}.part{{fill:#dff3ff;stroke:#082b55;stroke-width:4}}.hole{{fill:#fff;stroke:#082b55;stroke-width:3}}.ctr{{stroke:#0b63a3;stroke-width:2;stroke-dasharray:12 7}}.dl{{stroke:#082b55;stroke-width:2;fill:none}}.ext{{stroke:#6284a2;stroke-width:1.5}}.datum{{fill:#f4b942;stroke:#8a5b00;stroke-width:2}}.box{{fill:#fff;stroke:#afd5e9;stroke-width:3}}.red{{fill:#fff7ed;stroke:#8b1e1e;stroke-width:3}}</style><defs><marker id="a" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M8 0L0 4L8 8Z" fill="#082b55"/></marker></defs><rect width="1800" height="1250" fill="#f7fbff"/>
<text x="45" y="55" class="h1">{PART} · adapter fabrication candidate · sheet 1 of 1</text><text x="45" y="92" class="warn">PRELIMINARY - ADAPTER FABRICATION CANDIDATE ONLY - NOT RELEASED FOR QUOTATION, PROCUREMENT, MACHINING,</text><text x="45" y="121" class="warn">ASSEMBLY, CONNECTION, POWERED TEST, MOTION, OR ENERGIZATION</text><text x="45" y="151" class="note">UNITS: mm · THIRD-ANGLE PROJECTION · ASME Y14.5-2018 (R2024) INTERPRETATION · SCALE: NTS</text>
<text x="110" y="185" class="h2">TOP VIEW</text><rect x="190" y="230" width="360" height="640" class="part"/><line x1="370" y1="200" x2="370" y2="900" class="ctr"/><line x1="160" y1="550" x2="580" y2="550" class="ctr"/>
<circle cx="370" cy="342" r="11" class="hole"/><circle cx="370" cy="758" r="11" class="hole"/><circle cx="250" cy="350" r="13.2" class="hole"/><circle cx="490" cy="350" r="13.2" class="hole"/><circle cx="250" cy="750" r="13.2" class="hole"/><circle cx="490" cy="750" r="13.2" class="hole"/>
<text x="590" y="270" class="dim">2X {UPPER_THREAD}, ↧ {UPPER_THREAD_DEPTH:.0f} MIN</text><text x="590" y="300" class="dim">DRILL Ø{UPPER_DRILL_DIA:.1f} ↧ {UPPER_DRILL_DEPTH:.0f} MIN</text><line x1="700" y1="300" x2="382" y2="342" class="dl" marker-end="url(#a)"/>
<text x="590" y="825" class="dim">4X Ø{LOWER_HOLE_DIA:.1f} THRU</text><text x="590" y="855" class="dim">POSITION Ø0.20 | A | B | C</text><line x1="740" y1="795" x2="505" y2="750" class="dl" marker-end="url(#a)"/>
<line x1="190" y1="205" x2="550" y2="205" class="dl" marker-start="url(#a)" marker-end="url(#a)"/><line x1="190" y1="215" x2="190" y2="180" class="ext"/><line x1="550" y1="215" x2="550" y2="180" class="ext"/><text x="346" y="193" class="dim">90.00 ±0.10</text>
<line x1="150" y1="230" x2="150" y2="870" class="dl" marker-start="url(#a)" marker-end="url(#a)"/><line x1="180" y1="230" x2="125" y2="230" class="ext"/><line x1="180" y1="870" x2="125" y2="870" class="ext"/><text x="68" y="555" class="dim" transform="rotate(-90 68 555)">160.00 ±0.10</text>
<line x1="250" y1="910" x2="490" y2="910" class="dl" marker-start="url(#a)" marker-end="url(#a)"/><line x1="250" y1="870" x2="250" y2="930" class="ext"/><line x1="490" y1="870" x2="490" y2="930" class="ext"/><text x="345" y="900" class="dim">60 BASIC</text>
<line x1="760" y1="350" x2="760" y2="750" class="dl" marker-start="url(#a)" marker-end="url(#a)"/><line x1="550" y1="350" x2="785" y2="350" class="ext"/><line x1="550" y1="750" x2="785" y2="750" class="ext"/><text x="775" y="565" class="dim" transform="rotate(-90 775 565)">100 BASIC · PT SLOT AXES</text>
<line x1="825" y1="342" x2="825" y2="758" class="dl" marker-start="url(#a)" marker-end="url(#a)"/><line x1="550" y1="342" x2="850" y2="342" class="ext"/><line x1="550" y1="758" x2="850" y2="758" class="ext"/><text x="840" y="570" class="dim" transform="rotate(-90 840 570)">104 BASIC · MAGTROL 4866 AXES</text>
<polygon points="180,510 150,495 150,525" class="datum"/><rect x="105" y="492" width="42" height="36" class="datum"/><text x="118" y="519" font-weight="700">B</text><polygon points="330,880 315,910 345,910" class="datum"/><rect x="307" y="912" width="46" height="36" class="datum"/><text x="320" y="939" font-weight="700">C</text>
<text x="110" y="1010" class="h2">SIDE VIEW</text><rect x="190" y="1050" width="480" height="96" class="part"/><line x1="710" y1="1050" x2="710" y2="1146" class="dl" marker-start="url(#a)" marker-end="url(#a)"/><line x1="670" y1="1050" x2="735" y2="1050" class="ext"/><line x1="670" y1="1146" x2="735" y2="1146" class="ext"/><text x="725" y="1115" class="dim" transform="rotate(-90 725 1115)">24.00 ±0.05</text><polygon points="430,1150 415,1180 445,1180" class="datum"/><rect x="407" y="1182" width="46" height="36" class="datum"/><text x="420" y="1209" font-weight="700">A</text>
<rect x="900" y="175" width="835" height="725" rx="12" class="box"/><text x="940" y="220" class="h2">FABRICATION NOTES</text>
<text x="940" y="265" class="note">1. MATERIAL: {MATERIAL}.</text><text x="940" y="300" class="note">   MACHINE FROM ≥25.4 mm STOCK; MATERIAL CERTIFICATE REQUIRED.</text><text x="940" y="345" class="note">2. FINISH: AS-MACHINED, NO ANODIZE OR CONVERSION COATING.</text><text x="940" y="390" class="note">3. DATUM A: BOTTOM PT-CONTACT FACE. FLATNESS 0.05.</text><text x="940" y="425" class="note">   TOP FACE PARALLELISM 0.05 TO A; BOTH FACES Ra 3.2 µm MAX.</text><text x="940" y="470" class="note">4. DATUM B: X-MIN LONG SIDE. DATUM C: Y-MIN SHORT SIDE.</text><text x="940" y="515" class="note">5. 2X TAPPED-HOLE POSITION Ø0.10 | A | B | C.</text><text x="940" y="560" class="note">6. BREAK ALL EDGES 0.2-0.5; REMOVE BURRS; NO SHARP EDGES.</text><text x="940" y="605" class="note">7. DO NOT SUBSTITUTE ALLOY/TEMPER OR WELD/HEAT-TREAT.</text><text x="940" y="650" class="note">8. CLEAN AND DRY. IDENTIFY PART/REV WITH NON-DAMAGING TAG.</text><text x="940" y="695" class="note">9. MODEL THREADS ARE COSMETIC/ABSENT; DRAWING CALLOUT CONTROLS.</text><text x="940" y="740" class="note">10. ALL DIMENSIONS REQUIRE FAI; SEE INSPECTION REGISTER.</text><text x="940" y="785" class="note">11. UNSPECIFIED LINEAR DIMENSIONS ±0.10; ANGLES ±0.5°.</text><text x="940" y="830" class="note">12. NO CAPACITY CREDIT UNTIL QUALIFIED REVIEW AND PROOF.</text>
<rect x="900" y="930" width="835" height="250" rx="12" class="red"/><text x="940" y="975" class="h2">RELEASE BOUNDARY</text><text x="940" y="1020" class="warn">DO NOT QUOTE, MACHINE, ASSEMBLE OR POWER FROM THIS CANDIDATE.</text><text x="940" y="1060" class="note">Magtrol 4866/PT application acceptance, exact hardware, DFM,</text><text x="940" y="1095" class="note">independent calculation review, FAI, proof, alignment and the</text><text x="940" y="1130" class="note">complete guarded load rig remain blocking evidence.</text><text x="940" y="1165" class="note">PART: {PART} · REV: P0.1 · IDENTIFIER: {IDENTIFIER}</text></svg>''', encoding="utf-8", newline="\n")


def html(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{IDENTIFIER}</title><script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/4.1.0/model-viewer.min.js"></script><style>
:root{{--deep:#041a35;--navy:#082b55;--sky:#7dd3fc;--pale:#e4f6ff;--gold:#f4b942;--ink:#102a43;--red:#8b1e1e;--mint:#83c5be;--line:#afd5e9}}*{{box-sizing:border-box}}body{{margin:0;background:#f7fbff;color:var(--ink);font:17px/1.55 system-ui,"Segoe UI",sans-serif}}header{{padding:clamp(34px,6vw,72px) 20px;background:linear-gradient(135deg,var(--deep),var(--navy));color:#fff}}header>div,main{{max-width:1200px;margin:auto}}h1{{font-size:clamp(36px,6vw,62px);line-height:1.08}}h2{{font-size:clamp(27px,3vw,39px);color:var(--navy)}}.eyebrow{{font-size:14px;font-weight:850;color:var(--sky)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #8a5b00;padding:15px 18px;font-weight:850}}main{{padding:30px 20px 80px}}.decision,.card,.boundary{{background:#fff;border:2px solid var(--line);border-radius:16px;padding:20px}}.decision{{border-left:9px solid var(--mint)}}.boundary{{border-left:9px solid var(--red)}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(235px,1fr));gap:18px}}.card strong{{display:block;font-size:clamp(25px,4vw,38px);color:var(--navy)}}model-viewer{{width:100%;height:590px;background:#dff3ff;border:3px solid var(--navy);border-radius:16px}}img{{display:block;width:100%;height:auto;border:3px solid var(--navy);border-radius:16px;background:#fff}}.table{{overflow:auto;border:2px solid var(--line);border-radius:12px}}table{{border-collapse:collapse;width:100%;min-width:860px}}th,td{{padding:13px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--navy);color:#fff}}.hold{{color:var(--red);font-weight:850}}a{{color:#075b9b;font-weight:750}}code{{font-size:16px}}footer{{padding:30px 20px;background:var(--deep);color:#fff}}footer p{{max-width:1200px;margin:auto}}@media(max-width:720px){{body{{font-size:16px}}model-viewer{{height:460px}}}}
</style></head><body><header><div><div class="eyebrow">{IDENTIFIER} · R105</div><h1>The brake-support adapter now has a real part definition.</h1><div class="warning">{WARNING}</div></div></header><main>
<section class="decision"><h2>Controlled design decision</h2><p><code>{PART}</code> is a 90 x 160 x 24 mm adapter machined from certified ASTM B209 6061-T651 plate. It carries two M6 tapped axes at the Magtrol 4866 ±52 mm pattern and four Ø6.6 through axes at the PT ±50 mm slot pattern. Datum, surface, thread, position, edge and inspection requirements are explicit.</p></section>
<section><h2>Inspect the exact candidate</h2><model-viewer src="../../../cad/hr-v0/generated/fx104-c01-p0.1/FX104-C01_P0.1_fabrication_candidate.glb" alt="FX104-C01 preliminary 6061-T651 brake-support adapter with six controlled holes" camera-controls shadow-intensity="0.8"></model-viewer></section>
<section><h2>Dimensioned drawing</h2><p>The SVG is the human-readable control view; the STEP is nominal 3D geometry. Thread notes and tolerances control over cosmetic STEP threads.</p><img src="../../../cad/hr-v0/generated/fx104-c01-p0.1/FX104-C01_P0.1_drawing.svg" alt="Dimensioned preliminary FX104-C01 fabrication-candidate drawing"></section>
<section><h2>Material and calculation basis</h2><div class="grid"><article class="card"><strong>6061-T651</strong><p>Certified ASTM B209 plate; machine from at least 25.4 mm stock.</p></article><article class="card"><strong>0.922 kg</strong><p>Nominal CAD mass at Kaiser's 2.70 g/cm³ density.</p></article><article class="card"><strong>17.21 N·m</strong><p>Three-times brake-weight moment screen.</p></article><article class="card"><strong>8.20 N·m</strong><p>Two-times X430 stall-endpoint torque screen.</p></article></div><p>Kaiser's 276 MPa yield value is typical. R105 uses 240 MPa only as a conservative project screen and requires the received material certificate; neither value is a released allowable.</p></section>
<section><h2>What this closes—and what it does not</h2><div class="table"><table><thead><tr><th>Subject</th><th>R105 state</th><th>Boundary</th></tr></thead><tbody><tr><td>Adapter material and geometry</td><td>Defined candidate</td><td>Certificate, DFM and qualified approval required.</td></tr><tr><td>Feature tolerances and inspection</td><td>Defined candidate</td><td>FAI remains unexecuted.</td></tr><tr><td>Adapter-only hand calculations</td><td>Screened</td><td>Independent calculation review and proof remain open.</td></tr><tr><td>Magtrol 4866 and PT hardware</td><td>Unresolved</td><td>Manufacturer files, hardware and application acceptance remain blocking.</td></tr><tr><td>Assembly and powered work</td><td>Prohibited</td><td>All release flags remain false.</td></tr></tbody></table></div></section>
<section class="boundary"><h2>Release boundary</h2><p class="hold">This is not a machining release.</p><p>The 4866 body model, PT T-nuts, exact fasteners, torque/preload, manufacturer acceptance, DFM, independent structural review, first-article inspection, proof, alignment and the complete guarded load rig remain unresolved. No supplier was contacted.</p></section>
<section><h2>Evidence files</h2><p><a href="../../../docs/hr-v0-fx104-c01-fabrication-candidate-p0.1.md">Design record</a> · <a href="../../../cad/hr-v0/generated/fx104-c01-p0.1/feature-register.csv">Feature register</a> · <a href="../../../cad/hr-v0/generated/fx104-c01-p0.1/analysis-register.csv">Analysis register</a> · <a href="../../../cad/hr-v0/generated/fx104-c01-p0.1/inspection-plan.csv">Inspection plan</a> · <a href="../../../cad/hr-v0/generated/fx104-c01-p0.1/open-hold-register.csv">Hold register</a></p></section>
</main><footer><p>{WARNING}. Automated geometry and arithmetic are not physical evidence or permission to act.</p></footer></body></html>''', encoding="utf-8", newline="\n")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    if WEB.exists():
        shutil.rmtree(WEB)
    OUT.mkdir(parents=True)
    WEB.mkdir(parents=True)

    part = part_geometry()
    step = OUT / "FX104-C01_P0.1_fabrication_candidate.step"
    cq.exporters.export(part, str(step)); base.canonicalize_step(step)
    assembly = cq.Assembly(name="FX104_C01_P01_FABRICATION_CANDIDATE")
    assembly.add(part, name="FX104_C01_6061_T651_CANDIDATE", color=cq.Color(0.49, 0.83, 0.99))
    assembly.save(str(OUT / "FX104-C01_P0.1_fabrication_candidate.glb"))
    drawing_svg(OUT / "FX104-C01_P0.1_drawing.svg")
    html(WEB / "index.html")

    volume = part.Volume()
    mass_g = volume * DENSITY_G_CM3 / 1000.0
    design_weight_moment = WEIGHT_MOMENT_NM * GRAVITY_FACTOR
    design_torque = STALL_TORQUE_NM * TORQUE_FACTOR
    lower_couple_n = design_weight_moment / (2 * LOWER_X / 1000.0)
    lower_tension_per_bolt_n = lower_couple_n / 2.0
    lower_shear_per_bolt_n = BRAKE_WEIGHT_N * GRAVITY_FACTOR / 4.0
    lower_resultant_n = math.hypot(lower_tension_per_bolt_n, lower_shear_per_bolt_n)
    section_modulus_mm3 = LENGTH_X * THICKNESS**2 / 6.0
    nominal_bending_mpa = design_weight_moment * 1000.0 / section_modulus_mm3
    yield_ratio = SCREEN_YIELD_MPA / nominal_bending_mpa
    lower_bearing_mpa = lower_resultant_n / (THICKNESS * LOWER_HOLE_DIA)
    upper_couple_n = design_torque / (2 * UPPER_Y / 1000.0)
    upper_thread_shear_area_mm2 = math.pi * 4.917 * UPPER_THREAD_DEPTH
    upper_thread_nominal_shear_mpa = upper_couple_n / upper_thread_shear_area_mm2

    write_csv(OUT / "feature-register.csv", [
        {"feature":"F01","definition":"overall X","nominal":"90.00 mm","tolerance":"±0.10 mm","datum":"B/C","inspection":"calibrated micrometer or CMM","state":"DEFINED CANDIDATE"},
        {"feature":"F02","definition":"overall Y","nominal":"160.00 mm","tolerance":"±0.10 mm","datum":"B/C","inspection":"calibrated micrometer or CMM","state":"DEFINED CANDIDATE"},
        {"feature":"F03","definition":"thickness","nominal":"24.00 mm","tolerance":"±0.05 mm","datum":"A","inspection":"five-point micrometer map","state":"DEFINED CANDIDATE"},
        {"feature":"F04","definition":"datum A bottom face","nominal":"PT contact","tolerance":"flatness 0.05 mm; Ra 3.2 µm max","datum":"A","inspection":"surface plate/indicator plus profilometer","state":"DEFINED CANDIDATE"},
        {"feature":"F05","definition":"top face","nominal":"parallel to A","tolerance":"parallelism 0.05 mm; Ra 3.2 µm max","datum":"A","inspection":"surface plate/indicator plus profilometer","state":"DEFINED CANDIDATE"},
        {"feature":"F06","definition":"4866 mounting threads","nominal":"2X M6 x 1 - 6H at X=0, Y=±52 BASIC","tolerance":"position Ø0.10 to A|B|C; 12 mm min full thread; Ø5 drill 18 mm min","datum":"A|B|C","inspection":"CMM, GO/NO-GO thread gage, depth gage","state":"DEFINED CANDIDATE"},
        {"feature":"F07","definition":"PT attachment holes","nominal":"4X Ø6.6 THRU at X=±30, Y=±50 BASIC","tolerance":"position Ø0.20 to A|B|C","datum":"A|B|C","inspection":"CMM and calibrated pin gage","state":"DEFINED CANDIDATE"},
        {"feature":"F08","definition":"edges","nominal":"all edges","tolerance":"break 0.2-0.5 mm; burr-free","datum":"none","inspection":"visual and edge comparator","state":"DEFINED CANDIDATE"},
        {"feature":"F09","definition":"material","nominal":MATERIAL,"tolerance":"no substitution; certificate required","datum":"none","inspection":"certificate and trace review","state":"DEFINED CANDIDATE"},
        {"feature":"F10","definition":"finish/marking","nominal":"as-machined, no coating; non-damaging part/rev tag","tolerance":"clean/dry; no permanent mark on datum faces","datum":"A/B/C protected","inspection":"visual","state":"DEFINED CANDIDATE"},
    ])
    write_csv(OUT / "analysis-register.csv", [
        {"screen":"A01","inputs":f"CAD volume {volume:.3f} mm^3 x {DENSITY_G_CM3:.2f} g/cm^3","result":f"{mass_g:.6f} g","authority":"NOMINAL CAD MASS; RECEIVED MASS OPEN"},
        {"screen":"A02","inputs":f"{WEIGHT_MOMENT_NM:.6f} N m x gravity factor {GRAVITY_FACTOR:.1f}","result":f"{design_weight_moment:.6f} N m","authority":"PROJECT SCREEN; NOT A RELEASED LOAD CASE"},
        {"screen":"A03","inputs":f"{STALL_TORQUE_NM:.1f} N m x torque factor {TORQUE_FACTOR:.1f}","result":f"{design_torque:.6f} N m","authority":"STALL-ENDPOINT PROJECT SCREEN; NOT CONTINUOUS DUTY"},
        {"screen":"A04","inputs":f"design weight moment / 60 mm lower-row span / 2 bolts","result":f"{lower_tension_per_bolt_n:.6f} N tension per bolt on ideal row","authority":"IDEAL DISTRIBUTION; PT HARDWARE/PRELOAD/SLIP OPEN"},
        {"screen":"A05","inputs":f"3x brake weight / 4 plus A04 orthogonal","result":f"{lower_resultant_n:.6f} N resultant per lower bolt","authority":"IDEAL DISTRIBUTION ONLY"},
        {"screen":"A06","inputs":f"M={design_weight_moment:.6f} N m; conservative Z=90x24^2/6={section_modulus_mm3:.3f} mm^3","result":f"{nominal_bending_mpa:.6f} MPa nominal bending stress","authority":"ADAPTER-ONLY GROSS-SECTION SCREEN; LOCAL/CONTACT/FATIGUE REVIEW OPEN"},
        {"screen":"A07","inputs":f"project yield basis {SCREEN_YIELD_MPA:.1f} MPa / A06","result":f"{yield_ratio:.6f} ratio","authority":"SCREENING RATIO ONLY; MATERIAL CERTIFICATE/ALLOWABLE/QUALIFIED REVIEW OPEN"},
        {"screen":"A08","inputs":f"A05 / (24 mm x Ø6.6 mm)","result":f"{lower_bearing_mpa:.6f} MPa nominal lower-hole bearing","authority":"ADAPTER-ONLY NOMINAL SCREEN"},
        {"screen":"A09","inputs":f"{design_torque:.3f} N m / 104 mm","result":f"{upper_couple_n:.6f} N upper-hole ideal torque couple","authority":"PILLOW-BLOCK LOAD TRANSFER/CONTACT OPEN"},
        {"screen":"A10","inputs":f"A09 / (π x 4.917 mm x {UPPER_THREAD_DEPTH:.1f} mm)","result":f"{upper_thread_nominal_shear_mpa:.6f} MPa nominal internal-thread shear","authority":"SIMPLIFIED UNIFORM-SHEAR SCREEN; THREAD ENGAGEMENT/FASTENER/PRELOAD REVIEW OPEN"},
        {"screen":"A11","inputs":f"Kaiser typical T651 yield {TYPICAL_YIELD_MPA:.1f} MPa; project basis {SCREEN_YIELD_MPA:.1f} MPa","result":"project basis is 86.956522% of published typical","authority":"TYPICAL DATA IS NOT A MINIMUM OR DESIGN ALLOWABLE"},
        {"screen":"A12","inputs":f"PT 20 + adapter {THICKNESS:.2f} + 4866 R 76","result":"120.000000 mm nominal axis height","authority":"PT/4866 TOLERANCES AND INSTALLED ALIGNMENT OPEN"},
    ])
    write_csv(OUT / "material-process-register.csv", [
        {"control":"MP01","requirement":MATERIAL,"evidence":"material certificate with alloy, temper, product form, heat/lot and applicable ASTM B209 compliance","state":"DEFINED; RECEIVED EVIDENCE OPEN"},
        {"control":"MP02","requirement":"stock thickness at least 25.4 mm; face both datum surfaces to 24.00 ±0.05 mm","evidence":"shop traveler and FAI thickness map","state":"DEFINED; DFM/FAI OPEN"},
        {"control":"MP03","requirement":"as-machined; no anodize, conversion coat, welding or heat treatment","evidence":"shop traveler and visual inspection","state":"DEFINED; EXECUTION OPEN"},
        {"control":"MP04","requirement":"deburr and break all edges 0.2-0.5 mm; clean and dry","evidence":"visual inspection","state":"DEFINED; EXECUTION OPEN"},
        {"control":"MP05","requirement":"protect A/B/C and threads during storage; identify part/revision by removable tag","evidence":"receiving inspection","state":"DEFINED; EXECUTION OPEN"},
    ])
    write_csv(OUT / "inspection-plan.csv", [
        {"record":"FAI-01","characteristic":"material certificate and trace","method":"document review","acceptance":"F09/MP01","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"FAI-02","characteristic":"overall X/Y and thickness map","method":"calibrated micrometer/CMM","acceptance":"F01/F02/F03","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"FAI-03","characteristic":"datum A flatness and top parallelism","method":"surface plate and calibrated indicator","acceptance":"F04/F05","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"FAI-04","characteristic":"datum-face surface finish","method":"calibrated profilometer","acceptance":"Ra 3.2 µm max","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"FAI-05","characteristic":"M6 thread size, position and depths","method":"CMM, GO/NO-GO gage, depth gage","acceptance":"F06","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"FAI-06","characteristic":"four through-hole diameters and position","method":"CMM and pin gage","acceptance":"F07","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"FAI-07","characteristic":"edges, burrs, finish, cleaning and marking","method":"visual/comparator","acceptance":"F08/F10 and MP03-MP05","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"FAI-08","characteristic":"nominal STEP-to-FAI feature reconciliation","method":"ballooned drawing and signed FAI report","acceptance":"all F01-F10 accounted","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"FAI-09","characteristic":"adapter-only proof and post-proof reinspection","method":"qualified procedure required","acceptance":"SELECTION REQUIRED","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
    ])
    write_csv(OUT / "source-register.csv", [
        {"source":"FX-SRC-01","organization":"Kaiser Aluminum","record":"Sheet Coil & Plate Alloy 6061 Technical Data","revision_date":"Rev. 05/06; accessed 2026-08-08","locator":"cad/vendor/kaiser/6061-t651-r105/Kaiser_Aluminum_6061_Sheet_Coil_and_Plate.pdf","sha256":sha256(KAISER / "Kaiser_Aluminum_6061_Sheet_Coil_and_Plate.pdf"),"use":"typical T651 mechanical/physical properties; not allowables"},
        {"source":"FX-SRC-02","organization":"Kaiser Aluminum","record":"KaiserSelect General Engineering Plate","revision_date":"publisher revision/date not printed; accessed 2026-08-08","locator":"cad/vendor/kaiser/6061-t651-r105/KaiserSelect_General_Engineering_Plate.pdf","sha256":sha256(KAISER / "KaiserSelect_General_Engineering_Plate.pdf"),"use":"6061-T651 general-engineering plate thickness range and machining/flatness context"},
        {"source":"FX-SRC-03","organization":"ASME","record":"Y14.5-2018 (R2024)","revision_date":"2018; reaffirmed 2024; accessed 2026-08-08","locator":"https://www.asme.org/codes-standards/find-codes-standards/y14-5-dimensiones-y-tolerancias/2018","sha256":"LIVE PAGE - NOT DOWNLOADED","use":"drawing/GD&T interpretation identifier only; standard text not reproduced"},
        {"source":"FX-SRC-04","organization":"Project Button","record":"R104 controlled Magtrol/PT support evidence","revision_date":"R104 2026-08-08","locator":"cad/hr-v0/generated/fx104-c01-p0.1/parent-artifact-register.csv","sha256":"SEE PARENT REGISTER","use":"published 4866/PT nominal interface axes and release boundary"},
    ])
    write_csv(OUT / "parent-artifact-register.csv", [
        {"parent":"HR-V0-X430-BRAKE-SUP-P0.1","artifact":"test-fixtures/hr-v0/x430-brake-support-p0.1/geometry-check.json","sha256":sha256(ROOT / "test-fixtures/hr-v0/x430-brake-support-p0.1/geometry-check.json"),"use":"4866/PT axes, 20 mm PT thickness and 120 mm nominal axis chain"},
        {"parent":"HR-V0-X430-BRAKE-SUP-P0.1","artifact":"test-fixtures/hr-v0/x430-brake-support-p0.1/dimension-register.csv","sha256":sha256(ROOT / "test-fixtures/hr-v0/x430-brake-support-p0.1/dimension-register.csv"),"use":"drawing-controlled Magtrol/PT values and open tolerances"},
        {"parent":"HR-V0-X430-LOAD-RIG-P0.1","artifact":"test-fixtures/hr-v0/x430-load-rig-p0.1/load-capacity-screen.csv","sha256":sha256(ROOT / "test-fixtures/hr-v0/x430-load-rig-p0.1/load-capacity-screen.csv"),"use":"brake mass/torque and X430 endpoint context"},
    ])
    holds = [
        ("AF-HOLD-01","4866 current availability, body CAD, material, supplied hardware, allowables and Magtrol application acceptance","PARTIAL"),
        ("AF-HOLD-02","PT-600 tolerances, countersunk pattern, exact T-slot hardware, clamp/structural allowables and Magtrol application acceptance","PARTIAL"),
        ("AF-HOLD-03","qualified review of R105 material, drawing, GD&T, load cases, calculations and proof basis","PARTIAL"),
        ("AF-HOLD-04","machine-shop DFM including tool access, blind-thread manufacture, inspection feasibility, stock/lot availability and quote","OPEN"),
        ("AF-HOLD-05","exact 4866-to-adapter and adapter-to-PT fastener/T-nut stacks, preload, locking, torque and reuse controls","OPEN"),
        ("AF-HOLD-06","received material certificate and complete signed FAI","OPEN"),
        ("AF-HOLD-07","qualified adapter/support proof procedure, acceptance values and executed results","OPEN"),
        ("AF-HOLD-08","installed center height, coaxiality, parallelism, runout, end float, shimming and uncertainty","OPEN"),
        ("AF-HOLD-09","complete guarded rig, brake controls, instrumentation, anchoring and powered-work authorization","OPEN"),
        ("AF-HOLD-10","final configured FR12-H101 test and qualified acceptance","OPEN"),
    ]
    write_csv(OUT / "open-hold-register.csv", [{"hold_id":i,"missing_evidence":m,"state":s,"effect":"BLOCKS QUOTATION/PROCUREMENT/MACHINING/ASSEMBLY/CONNECTION/POWERED TEST/MOTION/ENERGIZATION"} for i,m,s in holds])
    write_csv(OUT / "dfm-rfi.csv", [
        {"rfi":"DFM-01","recipient":"candidate machine shop","question":"Can FX104-C01 be machined and inspected exactly as defined from certified ASTM B209 6061-T651 plate at least 25.4 mm thick? Identify all required drawing changes.","state":"NOT SENT"},
        {"rfi":"DFM-02","recipient":"candidate machine shop","question":"Confirm achievable datum A flatness, top-face parallelism, Ra limits, M6 thread position/depth and Ø6.6 position; propose inspection methods and quote FAI separately.","state":"NOT SENT"},
        {"rfi":"DFM-03","recipient":"candidate machine shop","question":"State proposed stock producer, product form, heat/lot trace, material certificate contents and whether 24.00 ±0.05 mm is produced by facing both sides.","state":"NOT SENT"},
        {"rfi":"DFM-04","recipient":"qualified mechanical reviewer","question":"Independently review R105 load cases, project factors, gross-section/bearing/thread screens, unmodeled 4866 load transfer, fatigue/local/contact risks and proof requirements.","state":"NOT SENT"},
        {"rfi":"DFM-05","recipient":"Magtrol applications","question":"Review FX104-C01's 2X M6 axes at 104 mm and 4X Ø6.6 PT axes at 100 mm; provide 4866/PT tolerances, hardware, load limits and written application acceptance or corrections.","state":"NOT SENT"},
    ])
    geometry = {
        "identifier":IDENTIFIER,"part":PART,"material":MATERIAL,"envelope_mm":{"x":LENGTH_X,"y":WIDTH_Y,"z":THICKNESS},
        "upper_features":{"quantity":2,"thread":UPPER_THREAD,"axes_mm":[[0,-UPPER_Y],[0,UPPER_Y]],"thread_depth_min_mm":UPPER_THREAD_DEPTH,"drill_diameter_mm":UPPER_DRILL_DIA,"drill_depth_min_mm":UPPER_DRILL_DEPTH,"position_diameter_mm":0.10},
        "lower_features":{"quantity":4,"diameter_mm":LOWER_HOLE_DIA,"through":True,"axes_mm":[[-LOWER_X,-LOWER_Y],[-LOWER_X,LOWER_Y],[LOWER_X,-LOWER_Y],[LOWER_X,LOWER_Y]],"position_diameter_mm":0.20},
        "volume_mm3":volume,"mass_g":mass_g,"nominal_axis_height_mm":120.0,"step_sha256":sha256(step),
        "thread_geometry_in_step":False,"drawing_controls_threads":True,"fabrication_release":False,"capacity_credit":False,
    }
    (OUT / "geometry-check.json").write_text(json.dumps(geometry, indent=2) + "\n", encoding="utf-8")
    status = {
        "identifier":IDENTIFIER,"parent":"HR-V0-X430-BRAKE-SUP-P0.1","part_definition_complete_for_independent_review":True,
        "material_candidate_defined":True,"feature_tolerances_defined":True,"inspection_plan_defined":True,"adapter_only_calculation_screens_present":True,
        "supplier_contacted":False,"dfm_complete":False,"qualified_analysis_approved":False,"manufacturer_application_accepted":False,"fasteners_selected":False,"fai_executed":False,"proof_executed":False,
        "partial_hold_count":3,"open_hold_count":7,"rfi_count":5,"rfi_state":"NOT SENT",
        "release_flags":{key:False for key in ("quotation","procurement","machining","assembly","connection","powered_test","motion","energization","safety_credit","build_release")},
        "warning":WARNING,
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    write_generated_source_manifest()
    print(f"generated {IDENTIFIER}: exact adapter candidate; 10 features; 12 screens; 9 unexecuted inspections; 3 partial + 7 open holds; all release flags false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
