"""Generate the R106 FX103 two-piece output-adapter fabrication candidate.

R106 rejects the R103 one-piece geometry because its 15 mm stub overlaps the
PCD-16 horn-hole and screw-access envelope.  The replacement separates the
horn flange from the shaft flange so both fastener patterns remain accessible.
Nothing produced here is a machining, assembly, powered-test, or energization
release.
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
import generate_hr_v0_x430_output_interface as r103  # noqa: E402

IDENTIFIER = "HR-V0-FX103-OUTPUT-ADAPTER-FAB-P0.2"
WARNING = (
    "PRELIMINARY - TWO-PIECE OUTPUT-ADAPTER FABRICATION CANDIDATE ONLY - "
    "NOT RELEASED FOR QUOTATION, PROCUREMENT, MACHINING, ASSEMBLY, "
    "CONNECTION, POWERED TEST, MOTION, OR ENERGIZATION"
)
OUT = ROOT / "cad" / "hr-v0" / "generated" / "fx103-output-adapter-p0.2"
WEB = ROOT / "release" / "hr-v0" / "fx103-output-adapter-p0.2"
CARPENTER = ROOT / "cad" / "vendor" / "carpenter" / "custom-630-r106"
HN12 = ROOT / "cad" / "vendor" / "robotis" / "hn12-n101-r103"
R103 = ROOT / "test-fixtures" / "hr-v0" / "x430-output-interface-p0.1"
GENERATED_ROOT = ROOT / "cad" / "hr-v0" / "generated"
GENERATED_SOURCE_MANIFEST = GENERATED_ROOT / "SOURCE-MANIFEST.csv"
MECHANICAL_REVISION = "HR-V0-MECH-R0.1-PRELIMINARY"
GENERATED_TEXT_SUFFIXES = {".csv", ".dxf", ".json", ".step", ".svg", ".txt"}

MATERIAL = "17-4 PH stainless steel, UNS S17400, ASTM A564/A564M Type 630, H1150, certified"
DENSITY_KG_M3 = 7820.0
TYPICAL_YIELD_MPA = 869.0
PROJECT_SCREEN_MPA = 600.0
FLANGE_OD = 40.0
C01_T = 8.0
C01_PILOT_D = 10.0
C01_PILOT_L = 2.0
HN12_PCD = 16.0
HN12_HOLE_D = 2.2
HN12_CBORE_D = 4.0
HN12_CBORE_DEPTH = 2.2
TRANSFER_PCD = 28.0
TRANSFER_TAP_DRILL_D = 3.3
TRANSFER_THREAD_DEPTH = 6.0
C02_X0 = C01_T
C02_T = 8.0
C02_PILOT_BORE_NOMINAL = 10.008
C02_PILOT_DEPTH = 2.2
C02_CLEARANCE_D = 4.5
STUB_X0 = C02_X0 + C02_T
STUB_D_MAX = 15.000
STUB_D_MIN = 14.987
STUB_D_NOMINAL = (STUB_D_MAX + STUB_D_MIN) / 2.0
STUB_L = 20.0
ROOT_FILLET = 1.0
COUPLING_INSERTION = 14.95
COUPLING_GAP_TO_FLANGE = STUB_L - COUPLING_INSERTION
PEAK_TORQUE_NM = 7.9
RATED_TORQUE_NM = 3.96


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
    records = []
    for path in sorted(GENERATED_ROOT.rglob("*"), key=lambda item: item.as_posix().lower()):
        if path.is_file() and path != GENERATED_SOURCE_MANIFEST:
            records.append({
                "file": path.relative_to(GENERATED_ROOT).as_posix(),
                "sha256": generated_sha256(path),
                "revision": MECHANICAL_REVISION,
                "status": "PRELIMINARY - NOT RELEASED FOR FABRICATION OR ENERGIZATION",
            })
    write_csv(GENERATED_SOURCE_MANIFEST, records)


def cylinder_x(radius: float, length: float, x0: float, y: float = 0.0, z: float = 0.0) -> cq.Shape:
    return cq.Solid.makeCylinder(radius, length, cq.Vector(x0, y, z), cq.Vector(1, 0, 0))


def pattern_points(pcd: float, quantity: int, phase_deg: float = 0.0) -> list[tuple[float, float]]:
    radius = pcd / 2.0
    return [
        (
            radius * math.cos(math.radians(phase_deg + index * 360.0 / quantity)),
            radius * math.sin(math.radians(phase_deg + index * 360.0 / quantity)),
        )
        for index in range(quantity)
    ]


def c01_shape() -> cq.Shape:
    """Horn flange: eight accessible horn screws plus four transfer threads."""
    shape = cylinder_x(FLANGE_OD / 2.0, C01_T, 0.0).fuse(
        cylinder_x(C01_PILOT_D / 2.0, C01_PILOT_L, C01_T)
    )
    for y, z in pattern_points(HN12_PCD, 8):
        shape = shape.cut(cylinder_x(HN12_HOLE_D / 2.0, C01_T + 0.4, -0.2, y, z))
        shape = shape.cut(cylinder_x(HN12_CBORE_D / 2.0, HN12_CBORE_DEPTH + 0.2, C01_T - HN12_CBORE_DEPTH, y, z))
    for y, z in pattern_points(TRANSFER_PCD, 4, 22.5):
        shape = shape.cut(cylinder_x(TRANSFER_TAP_DRILL_D / 2.0, TRANSFER_THREAD_DEPTH + 0.2, C01_T - TRANSFER_THREAD_DEPTH, y, z))
    return shape


def c02_shape() -> cq.Shape:
    """Shaft flange: piloted transfer flange and Ruland-fit 15 mm stub."""
    flange = cylinder_x(FLANGE_OD / 2.0, C02_T, C02_X0)
    stub = cylinder_x(STUB_D_NOMINAL / 2.0, STUB_L, STUB_X0)
    shape = flange.fuse(stub)
    root_edges = [
        edge for edge in shape.Edges()
        if edge.geomType() == "CIRCLE"
        and abs(edge.Center().x - STUB_X0) < 0.01
        and abs(edge.Length() - math.pi * STUB_D_NOMINAL) < 0.1
    ]
    if len(root_edges) != 1:
        raise RuntimeError(f"expected one shaft-root edge, found {len(root_edges)}")
    shape = shape.fillet(ROOT_FILLET, root_edges)
    shape = shape.cut(cylinder_x(C02_PILOT_BORE_NOMINAL / 2.0, C02_PILOT_DEPTH + 0.2, C02_X0 - 0.1))
    for y, z in pattern_points(TRANSFER_PCD, 4, 22.5):
        shape = shape.cut(cylinder_x(C02_CLEARANCE_D / 2.0, C02_T + 0.4, C02_X0 - 0.2, y, z))
    return shape


def drawing_svg(path: Path) -> None:
    path.write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="2000" height="1450" viewBox="0 0 2000 1450" style="max-width:100%;height:auto"><style>
text{{font-family:Arial,sans-serif;fill:#102a43;font-size:21px}}.h1{{font-size:39px;font-weight:700;fill:#082b55}}.h2{{font-size:28px;font-weight:700;fill:#082b55}}.warn{{font-size:20px;font-weight:700;fill:#8b1e1e}}.dim{{font-size:20px;fill:#082b55}}.part{{fill:#dff3ff;stroke:#082b55;stroke-width:4}}.part2{{fill:#ffe29a;stroke:#082b55;stroke-width:4}}.hole{{fill:#fff;stroke:#082b55;stroke-width:3}}.ctr{{stroke:#0b63a3;stroke-width:2;stroke-dasharray:12 7}}.dl{{stroke:#082b55;stroke-width:2;fill:none}}.ext{{stroke:#6284a2;stroke-width:1.5}}.box{{fill:#fff;stroke:#afd5e9;stroke-width:3}}.red{{fill:#fff7ed;stroke:#8b1e1e;stroke-width:3}}</style><defs><marker id="a" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M8 0L0 4L8 8Z" fill="#082b55"/></marker></defs><rect width="2000" height="1450" fill="#f7fbff"/>
<text x="45" y="55" class="h1">FX103-C01 P0.2 + FX103-C02 P0.1 · two-piece output adapter · sheet 1 of 1</text><text x="45" y="92" class="warn">PRELIMINARY - FABRICATION CANDIDATE ONLY - NOT RELEASED FOR QUOTATION, PROCUREMENT, MACHINING, ASSEMBLY,</text><text x="45" y="121" class="warn">CONNECTION, POWERED TEST, MOTION, OR ENERGIZATION</text><text x="45" y="154">UNITS: mm · THIRD-ANGLE PROJECTION · ASME Y14.5-2018 (R2024) INTERPRETATION · SCALE: NTS</text>
<text x="70" y="205" class="h2">FX103-C01 P0.2 · HORN FLANGE · FRONT</text><circle cx="310" cy="470" r="180" class="part2"/><circle cx="310" cy="470" r="45" class="part"/><line x1="90" y1="470" x2="530" y2="470" class="ctr"/><line x1="310" y1="250" x2="310" y2="690" class="ctr"/>
{''.join(f'<circle cx="{310 + 72*math.cos(math.radians(i*45)):.2f}" cy="{470 + 72*math.sin(math.radians(i*45)):.2f}" r="18" class="hole"/>' for i in range(8))}
{''.join(f'<circle cx="{310 + 126*math.cos(math.radians(22.5+i*90)):.2f}" cy="{470 + 126*math.sin(math.radians(22.5+i*90)):.2f}" r="15" class="hole"/>' for i in range(4))}
<text x="545" y="320" class="dim">8X Ø2.2 +0.05/0 THRU</text><text x="545" y="352" class="dim">C'BORE Ø4.0 +0.10/0 ↧2.20 ±0.05</text><text x="545" y="384" class="dim">PCD Ø16 BASIC · POSITION Ø0.05 | A | B</text><line x1="555" y1="395" x2="375" y2="440" class="dl" marker-end="url(#a)"/>
<text x="545" y="520" class="dim">4X M4 × 0.7 - 6H ↧6.0 MIN</text><text x="545" y="552" class="dim">PCD Ø28 BASIC · PHASE 22.5° BASIC</text><text x="545" y="584" class="dim">POSITION Ø0.05 | A | B | C</text><line x1="560" y1="595" x2="430" y2="520" class="dl" marker-end="url(#a)"/>
<text x="545" y="640" class="dim">FLANGE Ø40.00 ±0.05 × 8.00 ±0.03</text><text x="545" y="672" class="dim">PILOT Ø10 h6 × 2.00 ±0.03</text>
<line x1="130" y1="735" x2="490" y2="735" class="dl" marker-start="url(#a)" marker-end="url(#a)"/><text x="255" y="725" class="dim">Ø40.00 ±0.05</text>
<text x="70" y="815" class="h2">FX103-C02 P0.1 · SHAFT FLANGE · FRONT</text><circle cx="310" cy="1080" r="180" class="part"/><circle cx="310" cy="1080" r="67.5" class="part2"/><line x1="90" y1="1080" x2="530" y2="1080" class="ctr"/><line x1="310" y1="860" x2="310" y2="1300" class="ctr"/>
{''.join(f'<circle cx="{310 + 126*math.cos(math.radians(22.5+i*90)):.2f}" cy="{1080 + 126*math.sin(math.radians(22.5+i*90)):.2f}" r="20.25" class="hole"/>' for i in range(4))}
<text x="545" y="965" class="dim">4X Ø4.5 +0.10/0 THRU</text><text x="545" y="997" class="dim">PCD Ø28 BASIC · PHASE 22.5° BASIC</text><text x="545" y="1029" class="dim">POSITION Ø0.05 | A | B</text><line x1="560" y1="1040" x2="430" y2="1025" class="dl" marker-end="url(#a)"/>
<text x="545" y="1135" class="dim">STUB Ø15.000 +0/-0.013</text><text x="545" y="1167" class="dim">TOTAL RUNOUT 0.03 | A | B</text><text x="545" y="1199" class="dim">Ra 0.8 µm MAX · ROOT R1.0 ±0.1</text><line x1="560" y1="1210" x2="375" y2="1130" class="dl" marker-end="url(#a)"/>
<text x="545" y="1250" class="dim">FLANGE Ø40.00 ±0.05 × 8.00 ±0.03</text><text x="545" y="1282" class="dim">STUB LENGTH 20.00 ±0.05</text>
<rect x="980" y="185" width="950" height="785" rx="12" class="box"/><text x="1020" y="230" class="h2">PART AND PROCESS NOTES</text>
<text x="1020" y="275">1. MATERIAL BOTH PARTS: 17-4 PH STAINLESS STEEL, UNS S17400.</text><text x="1020" y="310">   ASTM A564/A564M TYPE 630, H1150, CERTIFIED.</text><text x="1020" y="345">2. CERTIFICATE SHALL IDENTIFY SPEC, TYPE, CONDITION, HEAT/LOT.</text><text x="1020" y="380">3. FINISHED CONDITION A IS PROHIBITED. MACHINE FROM H1150 BAR.</text><text x="1020" y="415">4. DATUM A: REAR MATING FACE. FLATNESS 0.03; Ra 1.6 µm MAX.</text><text x="1020" y="450">5. DATUM B: CONTROLLED CYLINDRICAL AXIS. DATUM C: C01 H1 CLOCK HOLE.</text><text x="1020" y="485">6. OPPOSITE FLANGE FACE PARALLELISM 0.03 TO A; Ra 1.6 µm MAX.</text><text x="1020" y="520">7. C01 PILOT Ø10 h6 × 2.00 ±0.03. C02 POCKET Ø10 H7 ↧2.20 ±0.05.</text><text x="1020" y="555">8. BREAK EDGES 0.2-0.4 EXCEPT CONTROLLED FILLET; REMOVE BURRS.</text><text x="1020" y="590">9. CLEAN/PASSIVATION PROCESS: SELECTION REQUIRED AFTER DFM/REVIEW.</text><text x="1020" y="625">10. NO WELD, PLATING, REPAIR OR MATERIAL/CONDITION SUBSTITUTION.</text><text x="1020" y="660">11. STEP HAS NOMINAL TAP-DRILL GEOMETRY; THREAD CALLOUT CONTROLS.</text><text x="1020" y="695">12. UNSPECIFIED LINEAR ±0.10; ANGLES ±0.5°; ALL FEATURES REQUIRE FAI.</text><text x="1020" y="730">13. EXACT M2/M4 FASTENERS, LENGTHS, PRELOAD, LOCKING AND REUSE:</text><text x="1020" y="765">    SELECTION REQUIRED. ROBOTIS/RULAND APPLICATION ACCEPTANCE OPEN.</text><text x="1020" y="800">14. H1150 PROPERTY VALUES ARE TYPICAL, NOT RELEASED ALLOWABLES.</text><text x="1020" y="835">15. NO CAPACITY CREDIT UNTIL QUALIFIED REVIEW AND PHYSICAL PROOF.</text><text x="1020" y="885">PARTS: FX103-C01 P0.2 / FX103-C02 P0.1</text><text x="1020" y="920">IDENTIFIER: {IDENTIFIER}</text>
<rect x="980" y="1000" width="950" height="330" rx="12" class="red"/><text x="1020" y="1045" class="h2">R106 CORRECTION AND RELEASE BOUNDARY</text><text x="1020" y="1090" class="warn">R103 ONE-PIECE FX103-C01 IS REJECTED: STUB/HORN-HOLE ACCESS OVERLAP.</text><text x="1020" y="1130">C01 mounts first with eight recessed horn fasteners. C02 then pilots onto C01</text><text x="1020" y="1165">and attaches at the separate PCD-28 M4 pattern, leaving the Ø15 stub and</text><text x="1020" y="1200">transfer fasteners accessible. This resolves nominal geometry/tool access only.</text><text x="1020" y="1240">Do not quote, machine or assemble until manufacturer acceptance, exact hardware,</text><text x="1020" y="1275">DFM, qualified analysis, signed FAI/proof and rig authorization are complete.</text></svg>''', encoding="utf-8", newline="\n")


def guide_html(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{IDENTIFIER}</title><script type="module" src="../../vendor/model-viewer/4.1.0/model-viewer.min.js"></script><style>
:root{{--deep:#041a35;--navy:#082b55;--sky:#7dd3fc;--pale:#e4f6ff;--gold:#f4b942;--ink:#102a43;--red:#8b1e1e;--mint:#83c5be;--line:#afd5e9}}*{{box-sizing:border-box}}body{{margin:0;background:#f7fbff;color:var(--ink);font:17px/1.55 system-ui,"Segoe UI",sans-serif}}header{{padding:clamp(34px,6vw,72px) 20px;background:linear-gradient(135deg,var(--deep),var(--navy));color:#fff}}header>div,main{{max-width:1240px;margin:auto}}h1{{font-size:clamp(36px,6vw,62px);line-height:1.08}}h2{{font-size:clamp(27px,3vw,39px);color:var(--navy)}}.eyebrow{{font-size:14px;font-weight:850;color:var(--sky)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #8a5b00;padding:15px 18px;font-weight:850}}main{{padding:30px 20px 80px}}.decision,.card,.boundary,.finding{{background:#fff;border:2px solid var(--line);border-radius:16px;padding:20px}}.finding{{border-left:9px solid var(--red)}}.decision{{border-left:9px solid var(--mint)}}.boundary{{border-left:9px solid var(--red)}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(235px,1fr));gap:18px}}.card strong{{display:block;font-size:clamp(25px,4vw,38px);color:var(--navy)}}model-viewer{{width:100%;height:620px;background:#dff3ff;border:3px solid var(--navy);border-radius:16px}}.drawing-scroll{{overflow:auto;border:3px solid var(--navy);border-radius:16px;background:#fff}}.drawing-scroll img{{display:block;width:1200px;max-width:none;height:auto;border:0}}.table{{overflow:auto;border:2px solid var(--line);border-radius:12px}}table{{border-collapse:collapse;width:100%;min-width:900px}}th,td{{padding:13px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--navy);color:#fff}}.hold{{color:var(--red);font-weight:850}}a{{color:#075b9b;font-weight:750}}code{{font-size:16px}}footer{{padding:30px 20px;background:var(--deep);color:#fff}}footer p{{max-width:1240px;margin:auto}}@media(max-width:720px){{body{{font-size:16px}}model-viewer{{height:470px}}}}
</style></head><body><header><div><div class="eyebrow">{IDENTIFIER} · R106</div><h1>A non-buildable one-piece shaft adapter is now a two-piece, inspectable interface.</h1><div class="warning">{WARNING}</div></div></header><main>
<section class="finding"><h2>Defect found in R103</h2><p>The proposed Ø15 stub radius was 7.5 mm while the HN12 hole centers are only 8 mm from the axis. A Ø2.2 hole therefore intruded 0.6 mm into the stub envelope, and even a nominal Ø3.8 M2 head would intrude 1.4 mm. Straight screw and driver access was impossible. The one-piece geometry is rejected.</p></section>
<section class="decision"><h2>Controlled correction</h2><p><code>FX103-C01 P0.2</code> is a horn flange installed first through eight recessed PCD-16 holes. <code>FX103-C02 P0.1</code> is a separate piloted shaft flange attached by four M4 transfer screws on PCD 28. The Ø15 shaft remains clear of the transfer-head envelope and matches Ruland's published +0/-0.013 mm shaft recommendation.</p></section>
<section><h2>Inspect the exact candidate</h2><model-viewer src="../../../cad/hr-v0/generated/fx103-output-adapter-p0.2/FX103_output_adapter_P0.2_review.glb" alt="Preliminary two-piece HN12 horn flange and 15 millimeter shaft flange with separated fastener patterns" camera-controls shadow-intensity="0.8"></model-viewer><p>Gold is the exact ROBOTIS HN12 horn. Yellow is C01. Sky blue is C02. Gray is the first Ruland hub envelope. The hub placement is a nominal catalog-envelope layout; controlled STEP parts remain unreleased candidates.</p></section>
<section><h2>Dimensioned drawing</h2><p>On narrow screens, scroll horizontally; the control view is not shrunk below its 12-pixel annotation floor.</p><div class="drawing-scroll"><img src="../../../cad/hr-v0/generated/fx103-output-adapter-p0.2/FX103_output_adapter_P0.2_drawing.svg" alt="Dimensioned preliminary two-piece FX103 output-adapter fabrication-candidate drawing"></div></section>
<section><h2>Geometry and load-path screens</h2><div class="grid"><article class="card"><strong>0.60 mm</strong><p>Old nominal hole/stub overlap that invalidates the R103 one-piece part.</p></article><article class="card"><strong>1.10 mm</strong><p>New nominal C01 pilot-to-M2-head radial clearance using a Ø3.8 review envelope.</p></article><article class="card"><strong>3.00 mm</strong><p>New nominal C02 stub-to-M4-head radial clearance using a Ø7 review envelope.</p></article><article class="card"><strong>11.95 MPa</strong><p>Nominal 7.9 N·m torsional shear at the minimum 14.987 mm shaft diameter; not an allowable check.</p></article></div></section>
<section><h2>Evidence state</h2><div class="table"><table><thead><tr><th>Subject</th><th>R106 state</th><th>Still required</th></tr></thead><tbody><tr><td>Part material and nominal geometry</td><td>Defined candidate</td><td>Material certificate, DFM and qualified approval.</td></tr><tr><td>Horn and transfer feature controls</td><td>Defined candidate</td><td>Exact fasteners, engagement, preload, locking and manufacturer acceptance.</td></tr><tr><td>Stub fit and runout</td><td>Defined candidate</td><td>Ruland application acceptance, FAI and assembled metrology.</td></tr><tr><td>Static arithmetic</td><td>Screened</td><td>Joint slip, fatigue, horn/serration, thread and proof analysis.</td></tr><tr><td>Fabrication and powered work</td><td>Prohibited</td><td>Every release flag remains false.</td></tr></tbody></table></div></section>
<section class="boundary"><h2>Release boundary</h2><p class="hold">This is not a machining or assembly release.</p><p>ROBOTIS, Ruland and Magtrol application acceptance; exact screws; DFM; certified stock; independent calculation review; signed FAI; proof; alignment; guard/catch; brake controls; instrumentation; anchoring; and qualified powered-work authorization remain open.</p></section>
<section><h2>Evidence files</h2><p><a href="../../../docs/hr-v0-fx103-output-adapter-fabrication-candidate-p0.2.md">Design record</a> · <a href="../../../cad/hr-v0/generated/fx103-output-adapter-p0.2/feature-register.csv">Feature register</a> · <a href="../../../cad/hr-v0/generated/fx103-output-adapter-p0.2/analysis-register.csv">Analysis register</a> · <a href="../../../cad/hr-v0/generated/fx103-output-adapter-p0.2/inspection-plan.csv">Inspection plan</a> · <a href="../../../cad/hr-v0/generated/fx103-output-adapter-p0.2/open-hold-register.csv">Hold register</a></p></section>
</main><footer><p>{WARNING}. Automated geometry and arithmetic are not physical evidence or permission to act.</p></footer></body></html>''', encoding="utf-8", newline="\n")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    if WEB.exists():
        shutil.rmtree(WEB)
    OUT.mkdir(parents=True)
    WEB.mkdir(parents=True)

    c01 = c01_shape()
    c02 = c02_shape()
    c01_step = OUT / "FX103-C01_P0.2_horn_flange.step"
    c02_step = OUT / "FX103-C02_P0.1_shaft_flange.step"
    cq.exporters.export(c01, str(c01_step)); base.canonicalize_step(c01_step)
    cq.exporters.export(c02, str(c02_step)); base.canonicalize_step(c02_step)

    global_x = r103.FLANGE_X0
    horn = r103.horn_shape()
    c01_global = c01.translate((global_x, 0, r103.AXIS_Z))
    c02_global = c02.translate((global_x, 0, r103.AXIS_Z))
    hub_x = global_x + STUB_X0 + STUB_L - COUPLING_INSERTION
    hub = cylinder_x(r103.COUPLING_OD / 2.0, r103.HUB_L, hub_x, 0, r103.AXIS_Z).cut(
        cylinder_x(STUB_D_MAX / 2.0, r103.HUB_L + 0.2, hub_x - 0.1, 0, r103.AXIS_Z)
    )
    assembly = cq.Assembly(name="FX103_OUTPUT_ADAPTER_P02_REVIEW")
    assembly.add(horn, name="HN12_N101_EXACT_VENDOR_GEOMETRY", color=cq.Color(0.96, 0.73, 0.26))
    assembly.add(c01_global, name="FX103_C01_P02_HORN_FLANGE_CANDIDATE", color=cq.Color(1.0, 0.88, 0.55))
    assembly.add(c02_global, name="FX103_C02_P01_SHAFT_FLANGE_CANDIDATE", color=cq.Color(0.49, 0.83, 0.99))
    assembly.add(hub, name="RULAND_MJC33_15_A_CATALOG_ENVELOPE_NOT_SELECTED", color=cq.Color(0.45, 0.50, 0.55))
    assembly.save(str(OUT / "FX103_output_adapter_P0.2_review.glb"))
    assembly.save(str(OUT / "FX103_output_adapter_P0.2_review.step"))
    base.canonicalize_step(OUT / "FX103_output_adapter_P0.2_review.step")
    drawing_svg(OUT / "FX103_output_adapter_P0.2_drawing.svg")
    guide_html(WEB / "index.html")

    old_hole_stub_overlap = STUB_D_MAX / 2.0 - (HN12_PCD / 2.0 - HN12_HOLE_D / 2.0)
    old_head_stub_overlap = STUB_D_MAX / 2.0 - (HN12_PCD / 2.0 - 3.8 / 2.0)
    c01_head_pilot_clearance = HN12_PCD / 2.0 - 3.8 / 2.0 - C01_PILOT_D / 2.0
    pattern_radial_clearance = TRANSFER_PCD / 2.0 - TRANSFER_TAP_DRILL_D / 2.0 - (HN12_PCD / 2.0 + HN12_CBORE_D / 2.0)
    c02_head_stub_clearance = TRANSFER_PCD / 2.0 - 7.0 / 2.0 - STUB_D_MAX / 2.0
    tangential_m2_peak_n = PEAK_TORQUE_NM / (8 * HN12_PCD / 2000.0)
    tangential_m4_peak_n = PEAK_TORQUE_NM / (4 * TRANSFER_PCD / 2000.0)
    shaft_shear_peak_mpa = 16 * PEAK_TORQUE_NM * 1000.0 / (math.pi * STUB_D_MIN**3)
    shaft_shear_rated_mpa = 16 * RATED_TORQUE_NM * 1000.0 / (math.pi * STUB_D_MIN**3)
    c01_thread_shear_area = math.pi * 3.242 * TRANSFER_THREAD_DEPTH
    c01_thread_shear_mpa = tangential_m4_peak_n / c01_thread_shear_area
    c01_mass_g = c01.Volume() * DENSITY_KG_M3 / 1_000_000.0
    c02_mass_g = c02.Volume() * DENSITY_KG_M3 / 1_000_000.0

    write_csv(OUT / "feature-register.csv", [
        {"feature":"C01-F01","part":"FX103-C01 P0.2","definition":"outer diameter","nominal":"Ø40.00 mm","tolerance":"±0.05 mm; datum feature B axis","datum":"B","inspection":"CMM or roundness instrument","state":"DEFINED CANDIDATE"},
        {"feature":"C01-F02","part":"FX103-C01 P0.2","definition":"horn-contact face and flange thickness","nominal":"A; 8.00 mm","tolerance":"flatness 0.03; thickness ±0.03; Ra 1.6 µm max","datum":"A","inspection":"surface plate/CMM/profilometer","state":"DEFINED CANDIDATE"},
        {"feature":"C01-F03","part":"FX103-C01 P0.2","definition":"opposite transfer face","nominal":"front face","tolerance":"parallelism 0.03 to A; Ra 1.6 µm max","datum":"A","inspection":"CMM/profilometer","state":"DEFINED CANDIDATE"},
        {"feature":"C01-F04","part":"FX103-C01 P0.2","definition":"HN12 holes and recessed head envelopes","nominal":"8X Ø2.2 +0.05/0 THRU; CBORE Ø4.0 +0.10/0 x 2.20 ±0.05; PCD Ø16 BASIC","tolerance":"position Ø0.05 to A|B; H1 designated datum C clock hole","datum":"A|B; C=H1","inspection":"CMM and pin/depth gages","state":"DEFINED CANDIDATE; EXACT SCREW OPEN"},
        {"feature":"C01-F05","part":"FX103-C01 P0.2","definition":"transfer threads","nominal":"4X M4 x 0.7 - 6H; 6.0 mm min full thread; PCD Ø28 BASIC; phase 22.5° BASIC","tolerance":"position Ø0.05 to A|B|C","datum":"A|B|C","inspection":"CMM, GO/NO-GO thread and depth gages","state":"DEFINED CANDIDATE"},
        {"feature":"C01-F06","part":"FX103-C01 P0.2","definition":"transfer pilot","nominal":"Ø10 h6 x 2.00 mm","tolerance":"length ±0.03; total runout 0.03 to A|B","datum":"A|B","inspection":"CMM/micrometer/indicator","state":"DEFINED CANDIDATE"},
        {"feature":"C01-F07","part":"FX103-C01 P0.2","definition":"edges","nominal":"all uncontrolled edges","tolerance":"break 0.2-0.4 mm; burr-free","datum":"none","inspection":"visual/comparator","state":"DEFINED CANDIDATE"},
        {"feature":"C02-F01","part":"FX103-C02 P0.1","definition":"outer diameter and flange thickness","nominal":"Ø40.00 x 8.00 mm","tolerance":"OD ±0.05; thickness ±0.03","datum":"A|B","inspection":"CMM/micrometer","state":"DEFINED CANDIDATE"},
        {"feature":"C02-F02","part":"FX103-C02 P0.1","definition":"rear mating face","nominal":"datum A","tolerance":"flatness 0.03; Ra 1.6 µm max","datum":"A","inspection":"surface plate/CMM/profilometer","state":"DEFINED CANDIDATE"},
        {"feature":"C02-F03","part":"FX103-C02 P0.1","definition":"pilot pocket","nominal":"Ø10 H7 x 2.20 mm deep","tolerance":"depth ±0.05; datum feature B axis","datum":"B","inspection":"CMM/bore gage/depth gage","state":"DEFINED CANDIDATE"},
        {"feature":"C02-F04","part":"FX103-C02 P0.1","definition":"transfer clearance holes","nominal":"4X Ø4.5 +0.10/0 THRU; PCD Ø28 BASIC; phase 22.5° BASIC","tolerance":"position Ø0.05 to A|B","datum":"A|B","inspection":"CMM/pin gage","state":"DEFINED CANDIDATE"},
        {"feature":"C02-F05","part":"FX103-C02 P0.1","definition":"coupling stub","nominal":"Ø15.000 +0/-0.013 x 20.00 mm","tolerance":"length ±0.05; total runout 0.03 to A|B; Ra 0.8 µm max","datum":"A|B","inspection":"micrometer/CMM/indicator/profilometer","state":"DEFINED CANDIDATE; RULAND ACCEPTANCE OPEN"},
        {"feature":"C02-F06","part":"FX103-C02 P0.1","definition":"shaft-root fillet","nominal":"R1.0 mm","tolerance":"±0.1 mm; smooth blend; no undercut","datum":"A|B","inspection":"optical comparator/CMM","state":"DEFINED CANDIDATE"},
        {"feature":"C02-F07","part":"FX103-C02 P0.1","definition":"front flange face and edges","nominal":"front face; uncontrolled edges","tolerance":"parallelism 0.03 to A; Ra 1.6 µm max; edge break 0.2-0.4 mm","datum":"A","inspection":"CMM/profilometer/visual","state":"DEFINED CANDIDATE"},
        {"feature":"MAT-F01","part":"both","definition":"material and condition","nominal":MATERIAL,"tolerance":"no substitution; condition A finished parts prohibited; certificate required","datum":"none","inspection":"certificate, heat/lot trace and PMI if required","state":"DEFINED CANDIDATE"},
    ])
    write_csv(OUT / "analysis-register.csv", [
        {"screen":"R106-A01","inputs":"old radius 7.5 - (hole radius 8 - hole radius 1.1)","result":f"{old_hole_stub_overlap:.6f} mm nominal hole/stub overlap","authority":"R103 ONE-PIECE GEOMETRY REJECTED"},
        {"screen":"R106-A02","inputs":"old radius 7.5 - (hole radius 8 - candidate M2 head radius 1.9)","result":f"{old_head_stub_overlap:.6f} mm nominal head/stub overlap","authority":"SCREW/DRIVER ACCESS IMPOSSIBLE; EXACT HEAD STILL SELECTION REQUIRED"},
        {"screen":"R106-A03","inputs":"new hole radius 8 - head radius 1.9 - pilot radius 5","result":f"{c01_head_pilot_clearance:.6f} mm nominal C01 pilot/head radial clearance","authority":"GEOMETRY SCREEN; EXACT FASTENER/TOOL OPEN"},
        {"screen":"R106-A04","inputs":"M4 tap inner edge minus M2 counterbore outer edge","result":f"{pattern_radial_clearance:.6f} mm nominal pattern-to-pattern radial clearance","authority":"GEOMETRY SCREEN; POSITION/TOLERANCE/LOCAL STRESS REVIEW OPEN"},
        {"screen":"R106-A05","inputs":"PCD28 radius - candidate M4 head radius 3.5 - shaft radius 7.5","result":f"{c02_head_stub_clearance:.6f} mm nominal C02 head/stub radial clearance","authority":"GEOMETRY SCREEN; EXACT HEAD/TOOL OPEN"},
        {"screen":"R106-A06","inputs":f"stub length {STUB_L:.2f} - insertion {COUPLING_INSERTION:.2f}","result":f"{COUPLING_GAP_TO_FLANGE:.6f} mm nominal exposed stub before hub","authority":"CATALOG LAYOUT ONLY; RULAND ACCEPTANCE OPEN"},
        {"screen":"R106-A07","inputs":f"7.9 N m / 8 screws / 8 mm radius","result":f"{tangential_m2_peak_n:.6f} N ideal peak tangential load per horn screw","authority":"EQUAL-SHARE ARITHMETIC; NO HORN/SCREW/THREAD/SLIP CREDIT"},
        {"screen":"R106-A08","inputs":f"7.9 N m / 4 screws / 14 mm radius","result":f"{tangential_m4_peak_n:.6f} N ideal peak tangential load per transfer screw","authority":"EQUAL-SHARE ARITHMETIC; PRELOAD/SLIP/THREAD REVIEW OPEN"},
        {"screen":"R106-A09","inputs":f"16T/(pi*d^3), T=7.9 N m, d={STUB_D_MIN:.3f} mm","result":f"{shaft_shear_peak_mpa:.6f} MPa nominal shaft torsional shear","authority":"GROSS SOLID-SHAFT SCREEN; FILLET/FATIGUE/FAULT/ALIGNMENT OPEN"},
        {"screen":"R106-A10","inputs":f"16T/(pi*d^3), T=3.96 N m, d={STUB_D_MIN:.3f} mm","result":f"{shaft_shear_rated_mpa:.6f} MPa nominal shaft torsional shear","authority":"RULAND RATED ENDPOINT SCREEN; NOT A PROJECT DUTY ALLOWABLE"},
        {"screen":"R106-A11","inputs":"A08 / (pi x M4 internal thread minor-diameter screen 3.242 x 6 mm)","result":f"{c01_thread_shear_mpa:.6f} MPa simplified uniform internal-thread shear","authority":"SIMPLIFIED SCREEN; FASTENER/PRELOAD/ENGAGEMENT/LOCAL STRESS OPEN"},
        {"screen":"R106-A12","inputs":f"C01 CAD volume {c01.Volume():.3f} mm3 x 7820 kg/m3","result":f"{c01_mass_g:.6f} g nominal C01 mass","authority":"CAD/DENSITY MASS; RECEIVED MASS OPEN"},
        {"screen":"R106-A13","inputs":f"C02 CAD volume {c02.Volume():.3f} mm3 x 7820 kg/m3","result":f"{c02_mass_g:.6f} g nominal C02 mass","authority":"CAD/DENSITY MASS; RECEIVED MASS OPEN"},
        {"screen":"R106-A14","inputs":f"Carpenter typical H1150 yield {TYPICAL_YIELD_MPA:.0f} MPa; project screen {PROJECT_SCREEN_MPA:.0f} MPa","result":f"{PROJECT_SCREEN_MPA / TYPICAL_YIELD_MPA * 100:.6f}% of published typical","authority":"TYPICAL VALUE IS NOT A MINIMUM OR RELEASED ALLOWABLE"},
        {"screen":"R106-A15","inputs":"smooth circular Ø10 pilot without interference, key or accepted friction preload","result":"0 N m positive torque-transfer credit","authority":"PILOT IS ALIGNMENT-ONLY; TORQUE REQUIRES ACCEPTED CLAMPED JOINT"},
    ])
    write_csv(OUT / "material-process-register.csv", [
        {"control":"MP01","requirement":MATERIAL,"evidence":"certificate with specification, type, H1150 condition, heat/lot and product form","state":"DEFINED; RECEIVED EVIDENCE OPEN"},
        {"control":"MP02","requirement":"machine both parts from certified H1150 round bar at least Ø40 mm; finished Condition A prohibited","evidence":"shop traveler, certificate and receiving inspection","state":"DEFINED; DFM/EXECUTION OPEN"},
        {"control":"MP03","requirement":"finish critical faces, pilot, bore and shaft after all heat treatment","evidence":"shop traveler and FAI","state":"DEFINED; DFM/EXECUTION OPEN"},
        {"control":"MP04","requirement":"passivation/cleaning process SELECTION REQUIRED after galvanic, fit and manufacturer review","evidence":"qualified process disposition","state":"OPEN; NO COATING OR PASSIVATION RELEASE"},
        {"control":"MP05","requirement":"no welding, plating, repair or material/condition substitution","evidence":"shop traveler and visual/certificate review","state":"DEFINED; EXECUTION OPEN"},
        {"control":"MP06","requirement":"protect A/B/C, threads, pilot, bore and stub; removable part/revision tag only","evidence":"receiving inspection","state":"DEFINED; EXECUTION OPEN"},
    ])
    write_csv(OUT / "inspection-plan.csv", [
        {"record":"FAI-01","characteristic":"both material certificates, heat/lot and H1150 condition","method":"document review; PMI if qualified reviewer requires","acceptance":"MAT-F01/MP01-MP03","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"FAI-02","characteristic":"C01 OD, thickness, datum A flatness, face parallelism and finishes","method":"CMM/surface plate/profilometer","acceptance":"C01-F01/F02/F03","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"FAI-03","characteristic":"C01 eight HN12 holes/counterbores and H1 clock datum","method":"CMM/pin/depth gages","acceptance":"C01-F04","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"FAI-04","characteristic":"C01 four M4 threads, depth, position and phase","method":"CMM/GO-NO-GO/depth gage","acceptance":"C01-F05","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"FAI-05","characteristic":"C01 pilot size, length and runout","method":"CMM/micrometer/indicator","acceptance":"C01-F06","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"FAI-06","characteristic":"C02 OD, thickness, datum A flatness, face parallelism and finishes","method":"CMM/surface plate/profilometer","acceptance":"C02-F01/F02/F07","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"FAI-07","characteristic":"C02 H7 pilot pocket and depth","method":"CMM/bore/depth gages","acceptance":"C02-F03","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"FAI-08","characteristic":"C02 four transfer holes, position and phase","method":"CMM/pin gage","acceptance":"C02-F04","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"FAI-09","characteristic":"C02 stub diameter, length, runout and finish","method":"micrometer/CMM/indicator/profilometer","acceptance":"C02-F05","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"FAI-10","characteristic":"C02 root fillet","method":"optical comparator/CMM","acceptance":"C02-F06","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"FAI-11","characteristic":"all edges, burrs, prohibited processes and protection","method":"visual/process record","acceptance":"C01-F07/C02-F07/MP04-MP06","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"FAI-12","characteristic":"ballooned drawing and STEP reconciliation","method":"signed dimensional FAI","acceptance":"all 15 features accounted","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"FAI-13","characteristic":"assembled C01/C02/HN12 static torque proof and post-proof inspection","method":"qualified procedure required","acceptance":"SELECTION REQUIRED","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"FAI-14","characteristic":"assembled shaft coaxiality/runout under released stack","method":"qualified metrology procedure","acceptance":"SELECTION REQUIRED","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
    ])
    write_csv(OUT / "source-register.csv", [
        {"source":"R106-SRC-01","organization":"Carpenter Technology","record":"Custom 630 (17-4) datasheet","revision_date":"PDF metadata 2024-10-03; no printed revision; accessed 2026-08-08","locator":"cad/vendor/carpenter/custom-630-r106/Carpenter_Custom_630_17-4_PH.pdf","sha256":sha256(CARPENTER / "Carpenter_Custom_630_17-4_PH.pdf"),"use":"UNS S17400/A564 identity, bar forms, H1150 typical density/properties and process cautions"},
        {"source":"R106-SRC-02","organization":"ROBOTIS","record":"HN12-N101 official STEP and reference drawing","revision_date":"drawing 2019-05-22; accessed 2026-08-08","locator":"cad/vendor/robotis/hn12-n101-r103/","sha256":sha256(HN12 / "HN12-N101-official.step"),"use":"exact horn geometry and PCD-16/M2 pattern; drawing marked reference only"},
        {"source":"R106-SRC-03","organization":"ROBOTIS","record":"HN12-N101 Set product page","revision_date":"live page accessed 2026-08-08","locator":"https://robotis.us/hn12-n101-set/","sha256":"LIVE PAGE - NOT DOWNLOADED","use":"current compatibility and supplied WB M2x3 quantity; no project load approval"},
        {"source":"R106-SRC-04","organization":"Ruland Manufacturing","record":"MJC33-15-A clamp hub product data","revision_date":"live page accessed 2026-08-08","locator":"https://www.ruland.com/mjc33-15-a.html","sha256":"LIVE PAGE - NOT DOWNLOADED","use":"shaft +0/-0.013, bore +0.03/0, 15 mm penetration, M3 seating torque and full-bearing-support requirement"},
        {"source":"R106-SRC-05","organization":"Ruland Manufacturing","record":"MJC33-15-A + JD21/33-92Y two-clamp bundle data","revision_date":"live page accessed 2026-08-08","locator":"https://www.ruland.com/de/mjc33-15-a-jd21-33-92y.html","sha256":"LIVE PAGE - NOT DOWNLOADED","use":"two-clamp-hub topology, 92Y insert compatibility, 3.96/7.9 N m rated/peak endpoints and hub-gap data"},
        {"source":"R106-SRC-06","organization":"ASME","record":"Y14.5-2018 (R2024)","revision_date":"2018; reaffirmed 2024; accessed 2026-08-08","locator":"https://www.asme.org/codes-standards/find-codes-standards/y14-5-dimensiones-y-tolerancias/2018","sha256":"LIVE PAGE - NOT DOWNLOADED","use":"drawing/GD&T interpretation identifier only; standard text not reproduced"},
    ])
    write_csv(OUT / "parent-artifact-register.csv", [
        {"parent":"HR-V0-X430-OUTPUT-IF-P0.1","artifact":"test-fixtures/hr-v0/x430-output-interface-p0.1/adapter-feature-register.csv","sha256":sha256(R103 / "adapter-feature-register.csv"),"use":"R103 one-piece allocation and open feature controls"},
        {"parent":"HR-V0-X430-OUTPUT-IF-P0.1","artifact":"test-fixtures/hr-v0/x430-output-interface-p0.1/geometry-check.json","sha256":sha256(R103 / "geometry-check.json"),"use":"controlled HN12 placement and original review geometry"},
        {"parent":"HR-V0-X430-OUTPUT-IF-P0.1","artifact":"test-fixtures/hr-v0/x430-output-interface-p0.1/interface-tolerance-register.csv","sha256":sha256(R103 / "interface-tolerance-register.csv"),"use":"HN12/coupling fit and application holds"},
    ])
    holds = [
        ("OA-HOLD-01","independent mechanical/GD&T review of the two-piece topology, stress path, fatigue, fits, fasteners and proof basis","PARTIAL"),
        ("OA-HOLD-02","ROBOTIS written acceptance of HN12 for external-brake characterization plus exact horn fastener, engagement, torque, locking and reuse controls","PARTIAL"),
        ("OA-HOLD-03","Ruland written acceptance of MJC33-15-A/JD21-33-92Y for the spectrum, support, fit, insertion, gap, reversal and proof","PARTIAL"),
        ("OA-HOLD-04","machine-shop DFM for both parts, thread/counterbore access, H7/h6 fit, runout, finish, root fillet, stock and inspection","OPEN"),
        ("OA-HOLD-05","exact M2 and M4 fastener order identities, material/class, head envelopes, lengths, engagement, preload, tightening, locking and reuse","OPEN"),
        ("OA-HOLD-06","received H1150 material certificates, heat/lot trace and completed signed FAI","OPEN"),
        ("OA-HOLD-07","qualified horn/adapter/coupling static, fatigue, slip and fault-load analysis plus approved proof procedure","OPEN"),
        ("OA-HOLD-08","executed proof and post-proof dimensional/visual inspection","OPEN"),
        ("OA-HOLD-09","assembled HN12/C01/C02/coupling coaxiality, runout, end float, uncertainty and full-bearing-support evidence","OPEN"),
        ("OA-HOLD-10","complete brake mount, guard/catch, controls, instrumentation, anchoring and powered-work authorization","OPEN"),
        ("OA-HOLD-11","final configured FR12-H101 gravity/bearing/cable/moving-mass test and qualified acceptance","OPEN"),
    ]
    write_csv(OUT / "open-hold-register.csv", [
        {"hold_id":hold_id,"missing_evidence":missing,"state":state,"effect":"BLOCKS QUOTATION/PROCUREMENT/MACHINING/ASSEMBLY/CONNECTION/POWERED TEST/MOTION/ENERGIZATION"}
        for hold_id, missing, state in holds
    ])
    write_csv(OUT / "dfm-rfi.csv", [
        {"rfi":"OA-RFI-01","recipient":"ROBOTIS applications","question":"Review the separated HN12-to-C01 PCD-16 interface for guarded low-speed external-brake characterization; provide accepted screw type/length, engagement, torque, locking/reuse, horn/thread/serration limits and extraneous-load limits.","state":"NOT SENT"},
        {"rfi":"OA-RFI-02","recipient":"Ruland applications","question":"Review C02 Ø15.000 +0/-0.013 stub, 14.95 mm insertion, 5.05 mm flange gap and the full two-hub 92Y coupling for the bidirectional spectrum; confirm support, alignment, gap, seating torque and proof requirements.","state":"NOT SENT"},
        {"rfi":"OA-RFI-03","recipient":"candidate machine shop","question":"DFM-review both H1150 parts, including PCD-16 recessed holes, PCD-28 M4 threads, Ø10 H7/h6 pilot pair, Ø15 +0/-0.013 stub, 0.03 runout/face controls, R1 root and complete FAI. No quote or machining authorized.","state":"NOT SENT"},
        {"rfi":"OA-RFI-04","recipient":"qualified mechanical reviewer","question":"Review rejection of the one-piece geometry and the two-piece load path, fastener/joint slip, pilot zero-torque-credit rule, stress concentration, fatigue/fault loads, proof multiplier and containment.","state":"NOT SENT"},
        {"rfi":"OA-RFI-05","recipient":"qualified materials reviewer","question":"Confirm or correct ASTM A564/A564M Type 630 H1150, stock/heat-treatment route, certificate/PMI requirements, passivation/galvanic disposition and released design allowables.","state":"NOT SENT"},
        {"rfi":"OA-RFI-06","recipient":"qualified metrology provider","question":"Confirm inspectability and uncertainty for pattern position, H7/h6 pilot, shaft diameter/runout, root radius, face flatness/parallelism and assembled coaxiality; return a ballooned FAI plan.","state":"NOT SENT"},
        {"rfi":"OA-RFI-07","recipient":"qualified test/facility reviewer","question":"Define a guarded static proof and post-proof inspection that does not energize the actuator, then separately disposition the full brake rig before powered work.","state":"NOT SENT"},
    ])
    geometry = {
        "identifier": IDENTIFIER,
        "supersession": {"rejected":"FX103-C01 R103 one-piece review geometry","replacement":["FX103-C01 P0.2 horn flange","FX103-C02 P0.1 shaft flange"]},
        "material": MATERIAL,
        "c01": {"od_mm":FLANGE_OD,"thickness_mm":C01_T,"pilot_diameter_mm":C01_PILOT_D,"pilot_length_mm":C01_PILOT_L,"volume_mm3":c01.Volume(),"mass_g":c01_mass_g,"step_sha256":sha256(c01_step)},
        "c02": {"od_mm":FLANGE_OD,"thickness_mm":C02_T,"pilot_bore_nominal_mm":C02_PILOT_BORE_NOMINAL,"stub_diameter_limits_mm":[STUB_D_MIN,STUB_D_MAX],"stub_length_mm":STUB_L,"root_fillet_mm":ROOT_FILLET,"volume_mm3":c02.Volume(),"mass_g":c02_mass_g,"step_sha256":sha256(c02_step)},
        "patterns": {"horn":{"quantity":8,"pcd_mm":HN12_PCD,"hole_diameter_mm":HN12_HOLE_D,"counterbore_diameter_mm":HN12_CBORE_D},"transfer":{"quantity":4,"pcd_mm":TRANSFER_PCD,"phase_deg":22.5,"c01_thread":"M4 x 0.7 - 6H","c02_clearance_diameter_mm":C02_CLEARANCE_D}},
        "nominal_intersections_mm3": {"c01_c02":c01.intersect(c02).Volume(),"c02_hub":c02_global.intersect(hub).Volume()},
        "old_one_piece_hole_stub_overlap_mm":old_hole_stub_overlap,
        "old_one_piece_rejected":True,
        "thread_geometry_in_step":False,
        "fabrication_release":False,
        "capacity_credit":False,
    }
    (OUT / "geometry-check.json").write_text(json.dumps(geometry, indent=2) + "\n", encoding="utf-8")
    status = {
        "identifier":IDENTIFIER,"parent":"HR-V0-X430-OUTPUT-IF-P0.1","old_one_piece_geometry_rejected":True,
        "two_piece_part_definition_complete_for_independent_review":True,"material_candidate_defined":True,
        "feature_tolerances_defined":True,"inspection_plan_defined":True,"adapter_only_calculation_screens_present":True,
        "supplier_contacted":False,"dfm_complete":False,"qualified_analysis_approved":False,"manufacturer_application_accepted":False,
        "exact_fasteners_selected":False,"fai_executed":False,"proof_executed":False,"assembled_alignment_verified":False,
        "partial_hold_count":3,"open_hold_count":8,"rfi_count":7,"rfi_state":"NOT SENT",
        "release_flags":{key:False for key in ("quotation","procurement","machining","assembly","connection","powered_test","motion","energization","safety_credit","build_release")},
        "warning":WARNING,
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    write_generated_source_manifest()
    print(f"generated {IDENTIFIER}: rejected one-piece overlap; 15 features; 15 screens; 14 unexecuted inspections; 3 partial + 8 open holds; all release flags false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
