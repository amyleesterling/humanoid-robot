#!/usr/bin/env python3
"""Generate the R288 exact C07 analysis-zone CAD partition.

This stage creates exact OpenCASCADE solids for every C07 pocket-edge,
pocket-floor, hole-rim and nonsingular ligament zone, fragments the authoritative
P0.13 C07 solid conformally with those tools, and retains the resulting B-Rep.
It deliberately creates no mesh and performs no structural solve.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import platform
import shutil
import sys
from pathlib import Path

import gmsh


ROOT = Path(__file__).resolve().parents[1]
STEP = ROOT / "cad/hr-v0/generated/arm-architecture-p0.13-pad-pocket-stop/parts/MV0-C07_J2_positive_fixed_catch_adapter.step"
R282_ZONES = ROOT / "mechanical/analysis/hr-v0-j2-refinement-erratum-p0.1/exact-zone-register.csv"
R283_DEFINITION = ROOT / "mechanical/analysis/hr-v0-j2-exact-zone-submodel-architecture-p0.1/exact-zone-definition.json"
OUT = ROOT / "mechanical/analysis/hr-v0-j2-c07-exact-zone-partition-p0.1"
RELEASE = ROOT / "release/hr-v0/j2-c07-exact-zone-partition-p0.1"
IDENT = "HR-V0-J2-C07-EXACT-ZONE-PARTITION-P0.1"
ROUND = "R288"
WARNING = (
    "PRELIMINARY - EXACT ANALYSIS-ZONE CAD PARTITION ONLY - NOT APPROVED FOR "
    "PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED "
    "TESTING, MOTION, OR ENERGIZATION"
)
TOL = 1.0e-8


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise RuntimeError(f"refusing to write empty table: {path}")
    fields: list[str] = []
    for row in rows:
        for field in row:
            if field not in fields:
                fields.append(field)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def bbox(dim: int, tag: int) -> list[float]:
    return [round(float(value), 9) for value in gmsh.model.getBoundingBox(dim, tag)]


def entity_signature(dim: int, tag: int) -> str:
    record: dict[str, object] = {
        "dimension": dim,
        "geometry_type": gmsh.model.getType(dim, tag),
        "bbox_mm": bbox(dim, tag),
        "measure": round(float(gmsh.model.occ.getMass(dim, tag)), 9),
        "center_of_mass_mm": [round(float(value), 9) for value in gmsh.model.occ.getCenterOfMass(dim, tag)],
    }
    if dim > 0:
        children = []
        for child_dim, child_tag in gmsh.model.getBoundary([(dim, tag)], combined=False, oriented=False):
            children.append({
                "dimension": child_dim,
                "geometry_type": gmsh.model.getType(child_dim, child_tag),
                "bbox_mm": bbox(child_dim, child_tag),
                "measure": round(float(gmsh.model.occ.getMass(child_dim, child_tag)), 9),
            })
        record["boundary"] = sorted(children, key=lambda item: json.dumps(item, sort_keys=True))
    return stable(record)


def only_volume(dimtags: list[tuple[int, int]], label: str) -> int:
    volumes = [tag for dim, tag in dimtags if dim == 3]
    if len(volumes) != 1:
        raise RuntimeError(f"{label}: expected one volume, found {dimtags}")
    return volumes[0]


def annular_cylinder(cx: float, y0: float, cz: float, height: float, inner: float, outer: float) -> int:
    outer_tag = gmsh.model.occ.addCylinder(cx, y0, cz, 0.0, height, 0.0, outer)
    inner_tag = gmsh.model.occ.addCylinder(cx, y0, cz, 0.0, height, 0.0, inner)
    out, _ = gmsh.model.occ.cut([(3, outer_tag)], [(3, inner_tag)], removeObject=True, removeTool=True)
    return only_volume(out, "annular cylinder")


def quarter_annulus(cx: float, y0: float, cz: float, height: float, sx: int, sz: int) -> int:
    ring = annular_cylinder(cx, y0, cz, height, 1.0, 3.0)
    xmin = cx if sx > 0 else cx - 3.0
    zmin = cz if sz > 0 else cz - 3.0
    quadrant = gmsh.model.occ.addBox(xmin, y0, zmin, 3.0, height, 3.0)
    out, _ = gmsh.model.occ.intersect([(3, ring)], [(3, quadrant)], removeObject=True, removeTool=True)
    return only_volume(out, "quarter annulus")


def fuse_volumes(tags: list[int], label: str) -> int:
    current = tags[0]
    for tag in tags[1:]:
        out, _ = gmsh.model.occ.fuse([(3, current)], [(3, tag)], removeObject=True, removeTool=True)
        current = only_volume(out, label)
    return current


def rounded_rectangle_volume(cx: float, y0: float, cz: float, width: float, height_z: float, radius: float, depth_y: float) -> int:
    xmin = cx - width / 2.0
    zmin = cz - height_z / 2.0
    vertical = gmsh.model.occ.addBox(xmin + radius, y0, zmin, width - 2.0 * radius, depth_y, height_z)
    horizontal = gmsh.model.occ.addBox(xmin, y0, zmin + radius, width, depth_y, height_z - 2.0 * radius)
    corners = []
    for x in (xmin + radius, xmin + width - radius):
        for z in (zmin + radius, zmin + height_z - radius):
            corners.append(gmsh.model.occ.addCylinder(x, y0, z, 0.0, depth_y, 0.0, radius))
    return fuse_volumes([vertical, horizontal, *corners], "rounded rectangle")


def add_zone_tools() -> list[dict[str, object]]:
    zones: list[dict[str, object]] = []

    def add(zone_id: str, family: str, tag: int, definition: str, singular: bool) -> None:
        zones.append({
            "zone_id": zone_id,
            "family": family,
            "tool_tag": tag,
            "definition": definition,
            "singular_zone": singular,
        })

    y0 = 7.005
    depth = 1.520
    # Exact 1 mm in-plane bands around the eight tangent pieces of the
    # W12.4 x H40.4 x R2 pocket perimeter.  Tangent end planes make the eight
    # solids a zero-overlap partition rather than overlapping capsules.
    add("C07-PE-WEST-STRAIGHT", "C07-PE", gmsh.model.occ.addBox(36.8, y0, -17.2, 2.0, depth, 36.4), "x=37.8 +/-1; z=-17.2..19.2; y=7.005..8.525", False)
    add("C07-PE-NORTH-STRAIGHT", "C07-PE", gmsh.model.occ.addBox(39.8, y0, 20.2, 8.4, depth, 2.0), "z=21.2 +/-1; x=39.8..48.2; y=7.005..8.525", False)
    add("C07-PE-EAST-STRAIGHT", "C07-PE", gmsh.model.occ.addBox(49.2, y0, -17.2, 2.0, depth, 36.4), "x=50.2 +/-1; z=-17.2..19.2; y=7.005..8.525", False)
    add("C07-PE-SOUTH-STRAIGHT", "C07-PE", gmsh.model.occ.addBox(39.8, y0, -20.2, 8.4, depth, 2.0), "z=-19.2 +/-1; x=39.8..48.2; y=7.005..8.525", False)
    add("C07-PE-SOUTH-WEST-R2", "C07-PE", quarter_annulus(39.8, y0, -17.2, depth, -1, -1), "quarter annulus r=1..3 about (39.8,-17.2), southwest", False)
    add("C07-PE-NORTH-WEST-R2", "C07-PE", quarter_annulus(39.8, y0, 19.2, depth, -1, 1), "quarter annulus r=1..3 about (39.8,19.2), northwest", False)
    add("C07-PE-NORTH-EAST-R2", "C07-PE", quarter_annulus(48.2, y0, 19.2, depth, 1, 1), "quarter annulus r=1..3 about (48.2,19.2), northeast", False)
    add("C07-PE-SOUTH-EAST-R2", "C07-PE", quarter_annulus(48.2, y0, -17.2, depth, 1, -1), "quarter annulus r=1..3 about (48.2,-17.2), southeast", False)
    add("C07-PF", "C07-PF", rounded_rectangle_volume(44.0, 7.005, 1.0, 10.4, 38.4, 1.0, 1.0), "pocket plan inset 1.0 mm; y=7.005..8.005", False)

    holes = (
        ("H1", -16.0, -8.0, 1.35, 0.0, 9.525),
        ("H2", -16.0, 8.0, 1.35, 0.0, 9.525),
        ("H3", 16.0, -8.0, 1.35, 0.0, 9.525),
        ("H4", 16.0, 8.0, 1.35, 0.0, 9.525),
        # Exact P0.13 C07 geometry: the M5 bores start at y=2.9, not y=0.
        ("E1", 0.0, -10.0, 2.75, 2.9, 9.525),
        ("E2", 0.0, 10.0, 2.75, 2.9, 9.525),
    )
    for hole_id, cx, cz, radius, front_y, back_y in holes:
        front = gmsh.model.occ.addTorus(cx, front_y, cz, radius, 1.0, zAxis=[0.0, 1.0, 0.0])
        back = gmsh.model.occ.addTorus(cx, back_y, cz, radius, 1.0, zAxis=[0.0, 1.0, 0.0])
        add(f"{hole_id}-SINGULAR-RIM-FRONT", "HOLE-SINGULAR-RIM", front, f"distance <=1 mm from exact {hole_id} front rim at y={front_y}", True)
        add(f"{hole_id}-SINGULAR-RIM-BACK", "HOLE-SINGULAR-RIM", back, f"distance <=1 mm from exact {hole_id} back rim at y={back_y}", True)
        core_y0 = front_y + 1.0
        core_height = back_y - front_y - 2.0
        ligament = annular_cylinder(cx, core_y0, cz, core_height, radius + 1.0, radius + 3.0)
        add(f"{hole_id}-LIGAMENT", "HOLE-LIGAMENT", ligament, f"radial band r={radius + 1.0}..{radius + 3.0}; y={core_y0}..{back_y - 1.0}", False)
    return zones


def main() -> int:
    if sha(STEP) != "fc4178769862d39bf1eee881391de2852e4fc0e4424af4e5c1814981737365de":
        raise RuntimeError("authoritative P0.13 C07 STEP identity drift")
    if "C07-PE" not in R282_ZONES.read_text(encoding="utf-8"):
        raise RuntimeError("R282 exact-zone control missing C07-PE")
    if "clipped_volume_required_for_production" not in R283_DEFINITION.read_text(encoding="utf-8"):
        raise RuntimeError("R283 production clipping boundary missing")

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    gmsh.initialize(["-nopopup"])
    gmsh.option.setNumber("General.Terminal", 0)
    try:
        gmsh.model.add("R288_C07_EXACT_ZONE_PARTITION")
        imported = gmsh.model.occ.importShapes(str(STEP))
        if len(imported) != 1 or imported[0][0] != 3:
            raise RuntimeError(f"unexpected C07 STEP volumes: {imported}")
        part_tag = imported[0][1]
        original_part_volume = float(gmsh.model.occ.getMass(3, part_tag))
        zones = add_zone_tools()
        expected = {"C07-PE": 8, "C07-PF": 1, "HOLE-SINGULAR-RIM": 12, "HOLE-LIGAMENT": 6}
        actual = {family: sum(zone["family"] == family for zone in zones) for family in expected}
        if actual != expected:
            raise RuntimeError(f"zone-tool count drift: expected={expected}, actual={actual}")

        tools = [(3, int(zone["tool_tag"])) for zone in zones]
        _out, mapping = gmsh.model.occ.fragment([(3, part_tag)], tools, removeObject=True, removeTool=True)
        gmsh.model.occ.synchronize()
        if len(mapping) != 1 + len(zones):
            raise RuntimeError(f"fragment mapping count drift: {len(mapping)}")
        part_fragments = {tag for dim, tag in mapping[0] if dim == 3}
        if not part_fragments:
            raise RuntimeError("fragmented part has no material volumes")
        all_volumes = {tag for dim, tag in gmsh.model.getEntities(3)}
        outside = sorted(all_volumes - part_fragments)
        if outside:
            gmsh.model.occ.remove([(3, tag) for tag in outside], recursive=True)
            gmsh.model.occ.synchronize()

        memberships: dict[int, list[str]] = {tag: [] for tag in part_fragments}
        zone_fragment_sets: dict[str, set[int]] = {}
        for zone, mapped in zip(zones, mapping[1:]):
            fragments = {tag for dim, tag in mapped if dim == 3 and tag in part_fragments}
            if not fragments:
                raise RuntimeError(f"exact zone has no material intersection: {zone['zone_id']}")
            zone_fragment_sets[str(zone["zone_id"])] = fragments
            for tag in fragments:
                memberships[tag].append(str(zone["zone_id"]))
        multiply_assigned = {tag: ids for tag, ids in memberships.items() if len(ids) > 1}
        if multiply_assigned:
            raise RuntimeError(f"primary exact zones overlap by positive volume: {multiply_assigned}")

        zone_rows: list[dict[str, object]] = []
        for zone in zones:
            fragments = sorted(zone_fragment_sets[str(zone["zone_id"])])
            volume = sum(float(gmsh.model.occ.getMass(3, tag)) for tag in fragments)
            zone_rows.append({
                "zone_id": zone["zone_id"],
                "family": zone["family"],
                "definition": zone["definition"],
                "singular_zone": zone["singular_zone"],
                "material_fragment_count": len(fragments),
                "material_volume_mm3": volume,
                "fragment_tags_diagnostic_only_json": json.dumps(fragments, separators=(",", ":")),
                "fragment_signatures_sha256_json": json.dumps(sorted(entity_signature(3, tag) for tag in fragments), separators=(",", ":")),
                "classification": "EXACT OCC FRAGMENT MEMBERSHIP - NO CENTROID OR SAMPLED-DISTANCE SUBSTITUTE",
                "warning": WARNING,
            })
        write_csv(OUT / "exact-zone-register.csv", zone_rows)

        fragment_rows: list[dict[str, object]] = []
        total_fragment_volume = 0.0
        for tag in sorted(part_fragments):
            volume = float(gmsh.model.occ.getMass(3, tag))
            total_fragment_volume += volume
            zone_ids = memberships[tag]
            fragment_rows.append({
                "fragment_tag_diagnostic_only": tag,
                "fragment_signature_sha256": entity_signature(3, tag),
                "bbox_mm_json": json.dumps(bbox(3, tag), separators=(",", ":")),
                "center_of_mass_mm_json": json.dumps([round(float(value), 9) for value in gmsh.model.occ.getCenterOfMass(3, tag)], separators=(",", ":")),
                "volume_mm3": volume,
                "zone_membership_count": len(zone_ids),
                "zone_id": zone_ids[0] if zone_ids else "C07-MATRIX",
                "membership_rule": "OCC fragment provenance map intersected with authoritative part fragments",
                "warning": WARNING,
            })
        write_csv(OUT / "fragment-volume-register.csv", fragment_rows)
        closure_error = abs(total_fragment_volume - original_part_volume) / original_part_volume
        if closure_error > 1.0e-10:
            raise RuntimeError(f"fragment volume closure failed: {closure_error}")

        # Freeze exact hole wall extents and the corrected M5 front-rim datum.
        hole_rows = []
        for hole_id, cx, cz, radius, front_y, back_y in (
            ("H1", -16.0, -8.0, 1.35, 0.0, 9.525), ("H2", -16.0, 8.0, 1.35, 0.0, 9.525),
            ("H3", 16.0, -8.0, 1.35, 0.0, 9.525), ("H4", 16.0, 8.0, 1.35, 0.0, 9.525),
            ("E1", 0.0, -10.0, 2.75, 2.9, 9.525), ("E2", 0.0, 10.0, 2.75, 2.9, 9.525),
        ):
            hole_rows.append({
                "hole_id": hole_id, "axis_x_mm": cx, "axis_z_mm": cz, "radius_mm": radius,
                "exact_wall_front_y_mm": front_y, "exact_wall_back_y_mm": back_y,
                "protocol_correction": "NONE" if hole_id.startswith("H") else "R282 aggregate y=0 assumption corrected to exact P0.13 C07 M5 bore front y=2.9",
                "fixed_offset_gauge_volume_definition": "OPEN - radial thickness was not frozen by R282; no value invented",
                "warning": WARNING,
            })
        write_csv(OUT / "hole-geometry-erratum.csv", hole_rows)

        gmsh.write(str(OUT / "c07-exact-zone-fragmented.brep"))
        brep_path = OUT / "c07-exact-zone-fragmented.brep"
        status = {
            "identifier": IDENT, "round": ROUND, "date": "2026-08-13",
            "step_sha256": sha(STEP), "primary_exact_zone_count": len(zones),
            "fragmented_material_volume_count": len(part_fragments),
            "exact_occ_fragment_membership_complete": True,
            "primary_zone_positive_volume_overlap_count": 0,
            "fragment_volume_relative_closure_error": closure_error,
            "brep_sha256": sha(brep_path),
            "hole_fixed_offset_gauge_volume_definition_complete": False,
            "conformal_mesh_generated": False, "exact_zone_quality_histograms_complete": False,
            "structural_solution_executed": False, "mesh_convergence_complete": False,
            "r279_c02_complete": False, "r278_h02_closed": False,
            "capacity_credit": False, "selected": False, "safety_credit": False,
            "procurement_authorized": False, "fabrication_authorized": False,
            "assembly_authorized": False, "connection_authorized": False,
            "powered_testing_authorized": False, "motion_authorized": False,
            "energization_authorized": False, "warning": WARNING,
        }
        (OUT / "analysis-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
        provenance = {
            "identifier": IDENT, "generator_path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
            "generator_sha256": sha(Path(__file__).resolve()), "step_path": STEP.relative_to(ROOT).as_posix(),
            "step_sha256": sha(STEP), "r282_exact_zone_register_sha256": sha(R282_ZONES),
            "r283_exact_zone_definition_sha256": sha(R283_DEFINITION),
            "python": sys.version, "platform": platform.platform(), "gmsh_build": gmsh.option.getString("General.BuildInfo"),
            "warning": WARNING,
        }
        (OUT / "execution-provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
        holds = [
            "Freeze and independently accept a physical thickness for the four fixed-offset hole gauge volumes.",
            "Generate a curved Tet10 mesh conformal to every exact R288 primary zone and retain exact entity maps.",
            "Execute full global and per-zone SICN histograms plus actual-quadrature signed-Jacobian checks.",
            "Execute structural fields, direct quadrature statistics, sections, probes, singularity trends and L0-L3/L4 convergence.",
            "Close nonlinear contact, joined hardware, dynamics, material, physical correlation and qualified capacity separately.",
        ]
        write_csv(OUT / "open-holds.csv", [{
            "hold_id": f"R288-H{i:02d}", "hold": hold, "state": "OPEN", "closure_evidence": "NOT EXECUTED",
            "effect": "R279-C02, R278-H02, CAPACITY AND ALL WORK AUTHORITY REMAIN OPEN", "warning": WARNING,
        } for i, hold in enumerate(holds, 1)])
        validation = [
            {"check_id": "R288-V01", "check": "authoritative STEP identity", "result": "PASS", "evidence": sha(STEP), "credit": "SOURCE IDENTITY", "warning": WARNING},
            {"check_id": "R288-V02", "check": "exact primary zone count", "result": "PASS", "evidence": f"{len(zones)} zones: 8 PE + 1 PF + 12 rims + 6 ligaments", "credit": "EXACT ZONE CAD", "warning": WARNING},
            {"check_id": "R288-V03", "check": "exact fragment membership", "result": "PASS", "evidence": f"{len(part_fragments)} material volumes; zero multiply assigned", "credit": "CONFORMAL CAD PARTITION", "warning": WARNING},
            {"check_id": "R288-V04", "check": "material volume closure", "result": "PASS", "evidence": f"relative error {closure_error}", "credit": "BOOLEAN CONSERVATION", "warning": WARNING},
            {"check_id": "R288-V05", "check": "M5 bore front datum correction", "result": "PASS", "evidence": "E1/E2 exact P0.13 front y=2.9 mm; aggregate y=0 assumption rejected", "credit": "PROTOCOL ERRATUM", "warning": WARNING},
            {"check_id": "R288-V06", "check": "fixed-offset gauge volume thickness", "result": "NOT EXECUTED", "evidence": "R282 did not freeze a thickness; no value invented", "credit": "NONE", "warning": WARNING},
        ]
        write_csv(OUT / "validation-register.csv", validation)
        readme = f"""# {IDENT}\n\n**{WARNING}**\n\nR288 creates an exact OpenCASCADE partition of the authoritative P0.13 C07 part into {len(zones)} primary analysis zones: eight separately named pocket-perimeter bands, the pocket-floor backing volume, twelve Euclidean 1 mm hole-rim neighborhoods, and six nonsingular ligament bands. The retained B-Rep is partitioned by Boolean provenance; no centroid, sampled-polyline, or element-mean membership substitute is used.\n\nThe exact C07 M5 bores E1/E2 begin at y=2.9 mm. R288 therefore rejects the earlier aggregate y=0 hole assumption for those two bores. It does not invent the missing radial thickness for fixed-offset hole gauge volumes.\n\nNo mesh or structural solve is executed. R279-C02, R278-H02, capacity, safety credit and every work authority remain open.\n"""
        (OUT / "README.md").write_text(readme, encoding="utf-8")
        files = []
        for path in sorted(OUT.iterdir()):
            if path.is_file() and path.name != "file-manifest.csv":
                files.append({"relative_path": path.name, "sha256": sha(path), "bytes": path.stat().st_size, "warning": WARNING})
        write_csv(OUT / "file-manifest.csv", files)
        if RELEASE.exists():
            shutil.rmtree(RELEASE)
        RELEASE.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(OUT, RELEASE)
        print(json.dumps(status, indent=2))
        return 0
    finally:
        gmsh.finalize()


if __name__ == "__main__":
    raise SystemExit(main())
