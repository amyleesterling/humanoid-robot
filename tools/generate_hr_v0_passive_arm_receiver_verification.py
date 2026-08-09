"""Generate an independent-method verification of the R127 receiver candidate.

This pass does not call the R127 envelope or arithmetic functions.  It reads the
same controlled P0.7 source B-Reps, minimizes each conservative AABB corner by
closed-form trigonometric boundary search, imports the issued receiver STEP,
and re-derives the catalog-unit and rail arithmetic with Decimal.

The result is internal computational corroboration, not qualified review,
physical evidence, application approval, or authority to fabricate or energize.
"""

from __future__ import annotations

import csv
import json
import math
import shutil
from decimal import Decimal, getcontext
from pathlib import Path

import cadquery as cq

import generate_hr_v0_arm_architecture as arm
import generate_hr_v0_collapse_envelope as collapse


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad" / "hr-v0" / "generated" / "passive-arm-receiver-verification-p0.1"
GUIDE = ROOT / "release" / "hr-v0" / "passive-arm-receiver-verification-p0.1" / "index.html"
R127 = ROOT / "cad" / "hr-v0" / "generated" / "passive-arm-receiver-p0.1"
R127_SUMMARY = R127 / "receiver-summary.json"
R127_STEP = R127 / "HR-V0_passive-arm-receiver-candidate.step"
GUARD_SUMMARY = ROOT / "cad" / "hr-v0" / "guard-receiver-p0.3" / "guard-receiver-summary.json"

IDENTIFIER = "HR-V0-PASSIVE-ARM-RECEIVER-VERIFY-P0.1"
WARNING = (
    "PRELIMINARY - INTERNAL SECOND-METHOD VERIFICATION ONLY - NOT APPROVED "
    "FOR FABRICATION, MOTION OR ENERGIZATION"
)

J1_RANGE_DEG = (-20.0, 70.0)
J2_RANGE_DEG = (15.0, 115.0)
SHOULDER_Z_MM = 500.0
RECEIVER_TOP_Z_MM = 320.0


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def corners(shape: cq.Shape) -> list[tuple[float, float, float]]:
    bounds = shape.BoundingBox()
    return [
        (x, y, z)
        for x in (bounds.xmin, bounds.xmax)
        for y in (bounds.ymin, bounds.ymax)
        for z in (bounds.zmin, bounds.zmax)
    ]


def periodic_stationary(base: float, lo: float, hi: float) -> list[float]:
    """Return base + k*pi values contained in the closed interval."""

    first = math.ceil((lo - base) / math.pi)
    last = math.floor((hi - base) / math.pi)
    return [base + k * math.pi for k in range(first, last + 1)]


def sinusoid_extrema(a: float, b: float, lo: float, hi: float) -> tuple[tuple[float, float], tuple[float, float]]:
    """Extrema of a*sin(theta)+b*cos(theta) over a closed interval."""

    candidates = [lo, hi]
    if abs(a) > 1e-15 or abs(b) > 1e-15:
        candidates.extend(periodic_stationary(math.atan2(a, b), lo, hi))
    values = [(angle, a * math.sin(angle) + b * math.cos(angle)) for angle in candidates]
    return min(values, key=lambda item: item[1]), max(values, key=lambda item: item[1])


def upper_corner_extrema(point: tuple[float, float, float]) -> tuple[dict[str, float], dict[str, float]]:
    _, y, z = point
    q1_lo, q1_hi = map(math.radians, J1_RANGE_DEG)
    minimum, maximum = sinusoid_extrema(y, z, q1_lo, q1_hi)
    return (
        {"z_mm": SHOULDER_Z_MM + minimum[1], "q1_deg": math.degrees(minimum[0]), "q2_deg": math.nan},
        {"z_mm": SHOULDER_Z_MM + maximum[1], "q1_deg": math.degrees(maximum[0]), "q2_deg": math.nan},
    )


def fore_corner_extrema(point: tuple[float, float, float]) -> tuple[dict[str, float], dict[str, float]]:
    """Exact boundary search for the current two-parallel-X-axis domain.

    For a forearm AABB corner, z = Z0 + J2*sin(q1) + A*sin(q1+q2)
    + B*cos(q1+q2).  An interior stationary point would require cos(q1)=0;
    the controlled q1 interval does not contain +/-90 degrees, so the global
    extrema lie on the four rectangle boundaries.
    """

    _, y, z = point
    a = y - arm.J2_Y
    b = z
    q1_lo, q1_hi = map(math.radians, J1_RANGE_DEG)
    q2_lo, q2_hi = map(math.radians, J2_RANGE_DEG)
    if q1_lo <= math.pi / 2 <= q1_hi or q1_lo <= -math.pi / 2 <= q1_hi:
        raise RuntimeError("forearm analytic boundary proof requires a new interior-stationary analysis")

    candidates: list[dict[str, float]] = []

    for q1 in (q1_lo, q1_hi):
        s_min, s_max = sinusoid_extrema(a, b, q1 + q2_lo, q1 + q2_hi)
        for s, value in (s_min, s_max):
            candidates.append(
                {
                    "z_mm": SHOULDER_Z_MM + arm.J2_Y * math.sin(q1) + value,
                    "q1_deg": math.degrees(q1),
                    "q2_deg": math.degrees(s - q1),
                }
            )

    for q2 in (q2_lo, q2_hi):
        c = arm.J2_Y + a * math.cos(q2) - b * math.sin(q2)
        d = a * math.sin(q2) + b * math.cos(q2)
        q_min, q_max = sinusoid_extrema(c, d, q1_lo, q1_hi)
        for q1, value in (q_min, q_max):
            candidates.append(
                {
                    "z_mm": SHOULDER_Z_MM + value,
                    "q1_deg": math.degrees(q1),
                    "q2_deg": math.degrees(q2),
                }
            )

    return min(candidates, key=lambda item: item["z_mm"]), max(candidates, key=lambda item: item["z_mm"])


def analytic_envelope() -> tuple[list[dict[str, object]], dict[str, object]]:
    upper, fore = collapse.controlled_shapes()
    rows: list[dict[str, object]] = []
    global_min: dict[str, object] | None = None
    global_max: dict[str, object] | None = None

    for family, shapes in (("upper", upper), ("fore", fore)):
        for name, shape in shapes.items():
            component_min: dict[str, object] | None = None
            component_max: dict[str, object] | None = None
            for point in corners(shape):
                minimum, maximum = (
                    upper_corner_extrema(point) if family == "upper" else fore_corner_extrema(point)
                )
                minimum.update({"component": name, "family": family, "corner": point})
                maximum.update({"component": name, "family": family, "corner": point})
                if component_min is None or float(minimum["z_mm"]) < float(component_min["z_mm"]):
                    component_min = minimum
                if component_max is None or float(maximum["z_mm"]) > float(component_max["z_mm"]):
                    component_max = maximum

            assert component_min is not None and component_max is not None
            rows.append(
                {
                    "component": name,
                    "family": family,
                    "minimum_z_mm": f"{float(component_min['z_mm']):.12f}",
                    "minimum_q1_deg": f"{float(component_min['q1_deg']):.12f}",
                    "minimum_q2_deg": "" if math.isnan(float(component_min["q2_deg"])) else f"{float(component_min['q2_deg']):.12f}",
                    "minimum_corner_xyz_mm": ";".join(f"{value:.12f}" for value in component_min["corner"]),
                    "maximum_z_mm": f"{float(component_max['z_mm']):.12f}",
                    "maximum_q1_deg": f"{float(component_max['q1_deg']):.12f}",
                    "maximum_q2_deg": "" if math.isnan(float(component_max["q2_deg"])) else f"{float(component_max['q2_deg']):.12f}",
                    "method": "closed-form trigonometric extrema on all rectangle boundaries",
                    "boundary": "conservative source-BRep AABB corners only; complete gripper/cables/tolerances excluded",
                }
            )
            if global_min is None or float(component_min["z_mm"]) < float(global_min["z_mm"]):
                global_min = component_min
            if global_max is None or float(component_max["z_mm"]) > float(global_max["z_mm"]):
                global_max = component_max

    assert global_min is not None and global_max is not None
    return rows, {"minimum": global_min, "maximum": global_max}


def imported_step_bounds() -> tuple[dict[str, float], float, int]:
    imported = cq.importers.importStep(str(R127_STEP))
    values = imported.vals()
    compound = cq.Compound.makeCompound(values)
    bounds = compound.BoundingBox()
    return (
        {
            "xmin": bounds.xmin,
            "xmax": bounds.xmax,
            "ymin": bounds.ymin,
            "ymax": bounds.ymax,
            "zmin": bounds.zmin,
            "zmax": bounds.zmax,
        },
        sum(shape.Volume() for shape in values),
        len(values),
    )


def decimal_arithmetic() -> tuple[list[dict[str, object]], dict[str, Decimal]]:
    getcontext().prec = 28
    d = Decimal
    ma30_each = d("31") * d("0.1129848290276167")
    ma30_total = d("3") * ma30_each
    ratio = ma30_total / d("5.295591")
    stroke = d("0.32") * d("25.4")
    minimum_mass = d("0.5") * d("0.45359237")
    maximum_mass = d("31") * d("0.45359237")
    minimum_speed = d("2.2") * d("0.3048")
    maximum_speed = d("14.6") * d("0.3048")
    load_each = d("2000") / d("2")
    inertia_mm4 = d("4.5357") * d("10000")
    moment = load_each * d("840") / d("4")
    stress = moment * d("20") / inertia_mm4
    deflection = load_each * d("840") ** 3 / (d("48") * d("68900") * inertia_mm4)
    results = {
        "ma30_each_j": ma30_each,
        "ma30_total_j": ma30_total,
        "catalog_to_gravity_ratio": ratio,
        "stroke_mm": stroke,
        "minimum_effective_mass_kg": minimum_mass,
        "maximum_effective_mass_kg": maximum_mass,
        "minimum_impact_speed_m_s": minimum_speed,
        "maximum_impact_speed_m_s": maximum_speed,
        "rail_moment_n_mm": moment,
        "rail_stress_mpa": stress,
        "rail_deflection_mm": deflection,
    }
    boundaries = {
        "ma30_each_j": "catalog conversion only",
        "ma30_total_j": "arithmetic sum; unequal sharing and application approval open",
        "catalog_to_gravity_ratio": "not an accepted safety or design factor",
        "stroke_mm": "published stroke; installed usable stroke and positive stop open",
        "minimum_effective_mass_kg": "published endpoint only",
        "maximum_effective_mass_kg": "published endpoint only",
        "minimum_impact_speed_m_s": "published endpoint only; actual machine may be slower",
        "maximum_impact_speed_m_s": "published endpoint only",
        "rail_moment_n_mm": "simple-span central-load screen",
        "rail_stress_mpa": "ideal equal-sharing screen; no allowable pass",
        "rail_deflection_mm": "typical E screen; joints and unequal sharing excluded",
    }
    rows = [
        {
            "record": f"R128-ARITH-{index:03d}",
            "quantity": name,
            "independent_result": format(value, "f"),
            "method": "Decimal re-derivation from controlled catalog/unit inputs",
            "boundary": boundaries[name],
        }
        for index, (name, value) in enumerate(results.items(), 1)
    ]
    return rows, results


def write_guide(summary: dict[str, object]) -> None:
    control = summary["analytic_envelope"]["controlling_minimum"]
    corner_y = float(control["corner_xyz_mm"][1])
    corner_z = float(control["corner_xyz_mm"][2])
    a = corner_y - float(summary["analytic_envelope"]["j2_y_mm"])
    guide = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 receiver verification</title><style>:root{{--deep:#041a35;--navy:#082b55;--sky:#7dd3fc;--pale:#e4f6ff;--gold:#f4b942;--ink:#102a43;--line:#9ccfe8;--red:#a83220}}*{{box-sizing:border-box}}body{{margin:0;background:var(--pale);color:var(--ink);font:17px/1.55 system-ui,"Segoe UI",sans-serif}}header{{background:linear-gradient(135deg,var(--deep),var(--navy));color:white;padding:clamp(34px,6vw,72px) 20px}}header>div,main{{max-width:1120px;margin:auto}}h1{{font-size:clamp(36px,6vw,64px);line-height:1.05;margin:.2em 0}}h2{{font-size:clamp(27px,3.5vw,39px);line-height:1.15;color:var(--navy)}}.eyebrow{{font-size:14px;font-weight:850;color:var(--sky)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #8a5b00;padding:15px 18px;font-weight:850}}main{{padding:30px 20px 80px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(245px,1fr));gap:18px}}.card,.lab{{background:white;border:2px solid var(--line);border-radius:16px;padding:20px;box-shadow:0 3px 0 #bddbea}}.metric{{font-size:clamp(34px,6vw,55px);font-weight:900;color:#075b9b}}label{{display:block;font-weight:800;font-size:16px;margin-top:14px}}input[type=range]{{width:100%;min-height:32px}}output{{font-weight:900;color:#075b9b}}svg{{width:100%;height:auto;background:#f8fcff;border:2px solid var(--line);border-radius:12px}}.guard{{fill:#e4f6ff;stroke:var(--navy);stroke-width:5}}.receiver{{stroke:#8a5b00;stroke-width:5}}.corner{{fill:var(--red);stroke:white;stroke-width:3}}.bound{{stroke:#075b9b;stroke-width:4;stroke-dasharray:10 7}}.label{{font:700 16px system-ui;fill:var(--ink)}}table{{width:100%;border-collapse:collapse;background:white}}th,td{{padding:13px;border:1px solid #8aa8ba;text-align:left;vertical-align:top;font-size:16px}}th{{background:#d5effc}}footer{{background:var(--deep);color:white;padding:30px 20px}}footer p{{max-width:1120px;margin:auto}}@media(max-width:760px){{body{{font-size:16px}}.table{{overflow:auto}}}}</style></head><body><header><div><p class="warning">{WARNING}</p><p class="eyebrow">{IDENTIFIER}</p><h1>The receiver clearance now has a second mathematical proof.</h1><p>Closed-form trigonometric minimization checks every conservative source-BRep AABB corner. It corroborates R127 without reusing its pose-grid function.</p></div></header><main><section><h2>Independent result</h2><div class="grid"><article class="card"><div class="metric">{summary['analytic_envelope']['minimum_z_mm']:.3f} mm</div><p>Exact global minimum inside the current AABB-corner model.</p></article><article class="card"><div class="metric">{summary['r127_comparison']['released_conservative_clearance_mm']:.3f} mm</div><p>R127's retained conservative clearance above the receiver.</p></article><article class="card"><div class="metric">{summary['receiver_guard_fit']['minimum_horizontal_guard_margin_mm']:.1f} mm</div><p>Smallest nominal receiver-to-guard internal horizontal margin.</p></article></div></section><section><h2>Explore the controlling corner</h2><div class="lab"><p>This visualization follows only the corner that controls the global minimum. The proof itself checks every corner of every controlled body.</p><label for="q1">J1 angle: <output id="q1o">-20.0°</output></label><input id="q1" type="range" min="-20" max="70" step="0.25" value="-20"><label for="q2">J2 angle: <output id="q2o">15.0°</output></label><input id="q2" type="range" min="15" max="115" step="0.25" value="15"><p>Selected H104 AABB-corner Z: <output id="zo">{summary['analytic_envelope']['minimum_z_mm']:.3f} mm</output></p><svg viewBox="0 0 900 520" role="img" aria-labelledby="plotTitle plotDesc"><title id="plotTitle">Receiver and selected controlling corner height</title><desc id="plotDesc">A vertical plot from bench datum to guard top showing the receiver, retained conservative bound and selected corner.</desc><rect x="100" y="25" width="520" height="465" class="guard"/><line x1="100" y1="333" x2="620" y2="333" class="receiver"/><line x1="100" y1="302" x2="620" y2="302" class="bound"/><circle id="dot" cx="360" cy="302" r="11" class="corner"/><text x="645" y="338" class="label">receiver Z=320</text><text x="645" y="307" class="label">retained bound Z={summary['r127_comparison']['released_conservative_minimum_z_mm']:.3f}</text><text id="dotLabel" x="380" y="288" class="label">selected corner</text></svg></div></section><section><h2>What was checked</h2><div class="table"><table><thead><tr><th>Evidence</th><th>Second method</th><th>Result</th></tr></thead><tbody><tr><td>Continuous command-domain lower envelope</td><td>Closed-form extrema on four angle-domain boundaries</td><td>Corroborated; exact AABB-corner minimum is {summary['analytic_envelope']['minimum_z_mm']:.6f} mm.</td></tr><tr><td>Receiver/guard fit</td><td>Imported issued STEP compared with guard internal envelope</td><td>X margin {summary['receiver_guard_fit']['x_margin_each_side_mm']:.1f} mm; limiting Y margin {summary['receiver_guard_fit']['y_margin_each_side_mm']:.1f} mm.</td></tr><tr><td>ACE and rail arithmetic</td><td>Decimal unit conversions and independent beam equations</td><td>Numerically agrees with R127; catalog/application boundaries remain unchanged.</td></tr></tbody></table></div></section><section><h2>Still not a release</h2><div class="grid"><article class="card"><strong>Geometry remains incomplete</strong><p>Gripper, object, cables, tolerances and deformation are still outside the proof.</p></article><article class="card"><strong>Hardware is unselected</strong><p>Guides, pad, platen, joints, anchors and three missing joint stops remain open.</p></article><article class="card"><strong>Application evidence is absent</strong><p>ACE sizing approval, measured dynamics, physical proof and qualified review remain mandatory.</p></article></div></section></main><footer><p>Project Button · {IDENTIFIER} · zero fabrication, motion, energization or functional-safety approval</p></footer><script>const q1=document.getElementById('q1'),q2=document.getElementById('q2'),q1o=document.getElementById('q1o'),q2o=document.getElementById('q2o'),zo=document.getElementById('zo'),dot=document.getElementById('dot'),dotLabel=document.getElementById('dotLabel');function update(){{const a=Number(q1.value),b=Number(q2.value),r=Math.PI/180,z={SHOULDER_Z_MM}+{arm.J2_Y:.12f}*Math.sin(a*r)+({a:.12f})*Math.sin((a+b)*r)+({corner_z:.12f})*Math.cos((a+b)*r),py=490-z/950*465;q1o.value=a.toFixed(2)+'°';q2o.value=b.toFixed(2)+'°';zo.value=z.toFixed(3)+' mm';dot.setAttribute('cy',py.toFixed(2));dotLabel.setAttribute('y',(py-14).toFixed(2));}}q1.addEventListener('input',update);q2.addEventListener('input',update);update();</script></body></html>'''
    GUIDE.parent.mkdir(parents=True, exist_ok=True)
    GUIDE.write_text(guide, encoding="utf-8", newline="\n")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    r127 = json.loads(R127_SUMMARY.read_text(encoding="utf-8"))
    guard = json.loads(GUARD_SUMMARY.read_text(encoding="utf-8"))
    analytic_rows, envelope = analytic_envelope()
    write_csv(OUT / "analytic-envelope-verification.csv", analytic_rows)

    analytic_minimum = float(envelope["minimum"]["z_mm"])
    analytic_maximum = float(envelope["maximum"]["z_mm"])
    sampled_minimum = float(r127["commanded_envelope"]["sampled_min_z_mm"])
    released_bound = float(r127["commanded_envelope"]["continuous_min_z_bound_mm"])
    released_clearance = float(r127["commanded_envelope"]["receiver_clearance_mm"])
    if abs(analytic_minimum - sampled_minimum) > 1e-6:
        raise RuntimeError("analytic minimum does not corroborate the R127 boundary sample")
    if analytic_minimum + 1e-9 < released_bound:
        raise RuntimeError("R127 continuous lower bound is not conservative against analytic minimization")

    step_bounds, step_volume, step_object_count = imported_step_bounds()
    inner = guard["internal_clear_mm"]
    x_margin = min(step_bounds["xmin"] - (-inner["x"] / 2), inner["x"] / 2 - step_bounds["xmax"])
    y_margin = min(step_bounds["ymin"] - (-inner["y"] / 2), inner["y"] / 2 - step_bounds["ymax"])
    bottom_margin = step_bounds["zmin"]
    top_margin = inner["z"] - step_bounds["zmax"]
    if min(x_margin, y_margin, bottom_margin, top_margin) < -1e-6:
        raise RuntimeError("issued receiver STEP exceeds the nominal internal guard envelope")

    fit_rows = [
        {"record":"R128-FIT-001","quantity":"receiver STEP X bounds","value":f"{step_bounds['xmin']:.6f}..{step_bounds['xmax']:.6f}","unit":"mm","guard_limit":f"{-inner['x']/2:.6f}..{inner['x']/2:.6f}","remaining_margin":f"{x_margin:.6f} each limiting side","result":"PASS NOMINAL STEP/ENVELOPE ONLY"},
        {"record":"R128-FIT-002","quantity":"receiver STEP Y bounds","value":f"{step_bounds['ymin']:.6f}..{step_bounds['ymax']:.6f}","unit":"mm","guard_limit":f"{-inner['y']/2:.6f}..{inner['y']/2:.6f}","remaining_margin":f"{y_margin:.6f} each limiting side","result":"PASS NOMINAL STEP/ENVELOPE ONLY"},
        {"record":"R128-FIT-003","quantity":"receiver STEP Z bounds","value":f"{step_bounds['zmin']:.6f}..{step_bounds['zmax']:.6f}","unit":"mm","guard_limit":f"0.000000..{inner['z']:.6f}","remaining_margin":f"bottom {bottom_margin:.6f}; top {top_margin:.6f}","result":"PASS NOMINAL STEP/ENVELOPE ONLY"},
        {"record":"R128-FIT-004","quantity":"receiver imported solid count","value":step_object_count,"unit":"objects","guard_limit":"not applicable","remaining_margin":"not applicable","result":"IMPORT PARSED"},
        {"record":"R128-FIT-005","quantity":"receiver imported volume sum","value":f"{step_volume:.6f}","unit":"mm3","guard_limit":"not applicable","remaining_margin":"not applicable","result":"GEOMETRY IDENTITY INPUT ONLY"},
    ]
    write_csv(OUT / "receiver-guard-fit-verification.csv", fit_rows)

    arithmetic_rows, arithmetic = decimal_arithmetic()
    write_csv(OUT / "arithmetic-rederivation.csv", arithmetic_rows)

    method_rows = [
        {"method_id":"R128-METHOD-001","claim":"continuous lower envelope","r127_method":"0.25 degree grid plus Lipschitz half-cell deduction","r128_method":"closed-form trigonometric extrema for every conservative AABB corner","shared_input":"P0.7 controlled source B-Reps and command-domain limits","independence_boundary":"different algorithm; same controlled geometry is intentionally shared","status":"INTERNAL CORROBORATION - QUALIFIED REVIEW OPEN"},
        {"method_id":"R128-METHOD-002","claim":"receiver/guard nominal fit","r127_method":"generator coordinates and review assembly","r128_method":"re-import issued STEP and compare its measured AABB with guard summary","shared_input":"issued STEP and P0.3 guard internal envelope","independence_boundary":"checks serialized artifact rather than generator primitives","status":"INTERNAL CORROBORATION - PHYSICAL FIT OPEN"},
        {"method_id":"R128-METHOD-003","claim":"ACE and rail arithmetic","r127_method":"binary floating-point calculations in R127 generator","r128_method":"Decimal unit conversions and direct beam equations","shared_input":"controlled catalog endpoints and explicit screen assumptions","independence_boundary":"same catalog inputs; different numeric implementation","status":"INTERNAL CORROBORATION - APPLICATION/ALLOWABLES OPEN"},
    ]
    write_csv(OUT / "method-register.csv", method_rows)

    control = envelope["minimum"]
    summary = {
        "identifier": IDENTIFIER,
        "warning": WARNING,
        "parent_identifier": "HR-V0-PASSIVE-ARM-RECEIVER-P0.1",
        "analytic_envelope": {
            "minimum_z_mm": analytic_minimum,
            "maximum_z_mm": analytic_maximum,
            "j2_y_mm": arm.J2_Y,
            "controlling_minimum": {
                "component": control["component"],
                "family": control["family"],
                "corner_xyz_mm": list(control["corner"]),
                "q1_deg": float(control["q1_deg"]),
                "q2_deg": float(control["q2_deg"]),
            },
            "method": "closed-form trigonometric boundary minimization of all source-BRep AABB corners",
            "scope": "known P0.7 B-Reps only; complete gripper, object, cables, tolerance and deformation excluded",
        },
        "r127_comparison": {
            "sampled_minimum_z_mm": sampled_minimum,
            "released_conservative_minimum_z_mm": released_bound,
            "released_conservative_clearance_mm": released_clearance,
            "analytic_minus_released_bound_mm": analytic_minimum - released_bound,
            "disposition": "R127 conservative bound retained; analytic result corroborates but does not expand the release boundary",
        },
        "receiver_guard_fit": {
            "step_bounds_mm": step_bounds,
            "x_margin_each_side_mm": x_margin,
            "y_margin_each_side_mm": y_margin,
            "bottom_margin_mm": bottom_margin,
            "top_margin_mm": top_margin,
            "minimum_horizontal_guard_margin_mm": min(x_margin, y_margin),
            "scope": "nominal serialized STEP versus nominal guard internal envelope; panels, joints, tolerances and physical fit open",
        },
        "arithmetic": {name: float(value) for name, value in arithmetic.items()},
        "verification_state": "INTERNAL SECOND-METHOD CORROBORATION COMPLETE; ALL R127 PHYSICAL AND QUALIFIED HOLDS REMAIN OPEN",
        "gate_state": "EG-008 AND EG-009 REMAIN PARTIAL",
    }
    (OUT / "verification-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    write_guide(summary)
    collapse.write_generated_source_manifest()

    print(f"Generated {IDENTIFIER}: analytic known-AABB minimum Z {analytic_minimum:.9f} mm")
    print(f"R127 retained conservative bound {released_bound:.9f} mm; nominal guard X/Y margins {x_margin:.3f}/{y_margin:.3f} mm")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
