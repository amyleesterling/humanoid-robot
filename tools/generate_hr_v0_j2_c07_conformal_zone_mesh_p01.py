#!/usr/bin/env python3
"""Generate the R289 bounded curved Tet10 mesh on the exact R288 partition."""
from __future__ import annotations

import csv
import gzip
import hashlib
import importlib.metadata
import json
import math
import platform
import shutil
import sys
import time
from pathlib import Path

import gmsh
import numpy as np
from scipy.spatial import cKDTree


ROOT = Path(__file__).resolve().parents[1]
R288 = ROOT / "mechanical/analysis/hr-v0-j2-c07-exact-zone-partition-p0.1"
BREP = R288 / "c07-exact-zone-fragmented.brep"
FRAGMENTS = R288 / "fragment-volume-register.csv"
ZONES = R288 / "exact-zone-register.csv"
OUT = ROOT / "mechanical/analysis/hr-v0-j2-c07-conformal-zone-mesh-p0.1"
RELEASE = ROOT / "release/hr-v0/j2-c07-conformal-zone-mesh-p0.1"
IDENT = "HR-V0-J2-C07-CONFORMAL-ZONE-MESH-P0.1"
ROUND = "R289"
WARNING = (
    "PRELIMINARY - EXACT-ZONE CONFORMAL MESH EVIDENCE ONLY - NOT APPROVED FOR "
    "PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED "
    "TESTING, MOTION, OR ENERGIZATION"
)
BINS = np.asarray((0.0, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00), dtype=float)
NORMALIZED_DET_FLOOR = 1.0e-10
CORNER_TOL_MM = 1.0e-9
FAMILY_SIZE = {"C07-PE": 0.25, "C07-PF": 0.25, "HOLE-SINGULAR-RIM": 0.25, "HOLE-LIGAMENT": 0.40, "C07-MATRIX": 3.0}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise RuntimeError(f"empty table: {path}")
    fields: list[str] = []
    for row in rows:
        for field in row:
            if field not in fields:
                fields.append(field)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def bbox(dim: int, tag: int) -> list[float]:
    return [round(float(value), 9) for value in gmsh.model.getBoundingBox(dim, tag)]


def entity_signature(dim: int, tag: int) -> str:
    record: dict[str, object] = {
        "dimension": dim, "geometry_type": gmsh.model.getType(dim, tag), "bbox_mm": bbox(dim, tag),
        "measure": round(float(gmsh.model.occ.getMass(dim, tag)), 9),
        "center_of_mass_mm": [round(float(value), 9) for value in gmsh.model.occ.getCenterOfMass(dim, tag)],
    }
    children = []
    for child_dim, child_tag in gmsh.model.getBoundary([(dim, tag)], combined=False, oriented=False):
        children.append({
            "dimension": child_dim, "geometry_type": gmsh.model.getType(child_dim, child_tag),
            "bbox_mm": bbox(child_dim, child_tag),
            "measure": round(float(gmsh.model.occ.getMass(child_dim, child_tag)), 9),
        })
    record["boundary"] = sorted(children, key=lambda item: json.dumps(item, sort_keys=True))
    return stable(record)


def add_threshold(surfaces: list[int], size_min: float, dist_max: float) -> int:
    distance = gmsh.model.mesh.field.add("Distance")
    gmsh.model.mesh.field.setNumbers(distance, "FacesList", surfaces)
    gmsh.model.mesh.field.setNumber(distance, "Sampling", 80)
    threshold = gmsh.model.mesh.field.add("Threshold")
    gmsh.model.mesh.field.setNumber(threshold, "InField", distance)
    gmsh.model.mesh.field.setNumber(threshold, "SizeMin", size_min)
    gmsh.model.mesh.field.setNumber(threshold, "SizeMax", 3.0)
    gmsh.model.mesh.field.setNumber(threshold, "DistMin", 0.0)
    gmsh.model.mesh.field.setNumber(threshold, "DistMax", dist_max)
    return threshold


def histogram_rows(scope: str, zone_id: str, values: np.ndarray, exact_volume: float, count: int) -> list[dict[str, object]]:
    counts, _ = np.histogram(values, bins=BINS)
    minimum = float(np.min(values))
    below = float(np.mean(values < 0.20))
    rows = []
    for index, bin_count in enumerate(counts):
        rows.append({
            "scope": scope, "zone_id": zone_id, "bin_lower_inclusive": BINS[index],
            "bin_upper_inclusive_last_otherwise_exclusive": BINS[index + 1], "count": int(bin_count),
            "fraction": float(bin_count / len(values)), "total_tetrahedra": len(values),
            "minimum_sicn": minimum, "fraction_below_0p20": below,
            "exact_zone_volume_mm3": exact_volume,
            "effective_h_mm": float((exact_volume / count) ** (1.0 / 3.0)),
            "global_gate": "PASS" if minimum >= 0.10 and below <= 0.001 else "FAIL",
            "monitored_zone_min_0p20_gate": "PASS" if minimum >= 0.20 else "FAIL",
            "warning": WARNING,
        })
    return rows


def main() -> int:
    if sha(BREP) != json.loads((R288 / "analysis-status.json").read_text(encoding="utf-8"))["brep_sha256"]:
        raise RuntimeError("R288 retained B-Rep identity drift")
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    started = time.perf_counter()
    fragment_rows = read_csv(FRAGMENTS)
    zone_rows = {row["zone_id"]: row for row in read_csv(ZONES)}
    expected_by_signature = {row["fragment_signature_sha256"]: row for row in fragment_rows}

    gmsh.initialize(["-nopopup"])
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.option.setNumber("General.NumThreads", 1)
    try:
        gmsh.model.add("R289_C07_CONFORMAL_ZONE_MESH")
        gmsh.model.occ.importShapes(str(BREP))
        gmsh.model.occ.synchronize()
        volume_zone: dict[int, str] = {}
        volume_signature: dict[int, str] = {}
        for _dim, tag in gmsh.model.getEntities(3):
            signature = entity_signature(3, tag)
            if signature not in expected_by_signature:
                raise RuntimeError(f"R288 fragment signature not found after B-Rep import: {signature}")
            volume_zone[tag] = expected_by_signature[signature]["zone_id"]
            volume_signature[tag] = signature
        if set(volume_signature.values()) != set(expected_by_signature):
            raise RuntimeError("R288 fragment signature set did not reproduce on import")

        # Freeze physical groups before meshing.  Zone membership is entity
        # provenance from the exact Boolean partition, never cell-centroid classification.
        for zone_id in sorted(set(volume_zone.values())):
            tags = [tag for tag, value in volume_zone.items() if value == zone_id]
            physical = gmsh.model.addPhysicalGroup(3, tags)
            gmsh.model.setPhysicalName(3, physical, zone_id)

        gmsh.option.setNumber("Mesh.MeshSizeMin", 0.20)
        gmsh.option.setNumber("Mesh.MeshSizeMax", 3.0)
        gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
        gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 1)
        gmsh.option.setNumber("Mesh.Algorithm3D", 1)
        fields = []
        for family, size in FAMILY_SIZE.items():
            if family == "C07-MATRIX":
                continue
            volume_tags = [tag for tag, zone_id in volume_zone.items() if zone_id != "C07-MATRIX" and zone_rows[zone_id]["family"] == family]
            surfaces = sorted({surface for tag in volume_tags for dim, surface in gmsh.model.getBoundary([(3, tag)], combined=False, oriented=False) if dim == 2})
            if not surfaces:
                raise RuntimeError(f"empty exact-zone surface group: {family}")
            fields.append(add_threshold(surfaces, size, 1.5 if size <= 0.25 else 2.0))
        minimum = gmsh.model.mesh.field.add("Min")
        gmsh.model.mesh.field.setNumbers(minimum, "FieldsList", fields)
        gmsh.model.mesh.field.setAsBackgroundMesh(minimum)

        gmsh.model.mesh.generate(3)
        gmsh.model.mesh.optimize("Netgen")
        tet4 = gmsh.model.mesh.getElementType("tetrahedron", 1)
        linear_tags_raw, linear_conn_raw = gmsh.model.mesh.getElementsByType(tet4)
        linear_tags = np.asarray(linear_tags_raw, dtype=np.int64)
        linear_conn = np.asarray(linear_conn_raw, dtype=np.int64).reshape((-1, 4))
        linear_sicn = np.asarray(gmsh.model.mesh.getElementQualities(linear_tags.tolist(), "minSICN"), dtype=float)
        linear_node_tags_raw, linear_coords_raw, _ = gmsh.model.mesh.getNodes()
        linear_node_tags = np.asarray(linear_node_tags_raw, dtype=np.int64)
        linear_xyz = np.asarray(linear_coords_raw, dtype=float).reshape((-1, 3))
        linear_lookup = {int(tag): linear_xyz[index] for index, tag in enumerate(linear_node_tags)}

        element_zone: dict[int, str] = {}
        zone_element_tags: dict[str, list[int]] = {}
        for volume_tag, zone_id in volume_zone.items():
            types, tags_blocks, _nodes_blocks = gmsh.model.mesh.getElements(3, volume_tag)
            tags: list[int] = []
            for element_type, block in zip(types, tags_blocks):
                if int(element_type) == int(tet4):
                    tags.extend(int(value) for value in block)
            if not tags:
                raise RuntimeError(f"zone volume has no tetrahedra: volume={volume_tag} zone={zone_id}")
            zone_element_tags.setdefault(zone_id, []).extend(tags)
            for element_tag in tags:
                if element_tag in element_zone:
                    raise RuntimeError(f"element has duplicate volume provenance: {element_tag}")
                element_zone[element_tag] = zone_id
        if set(element_zone) != set(int(tag) for tag in linear_tags):
            raise RuntimeError("linear element-to-exact-zone provenance is incomplete")

        global_volume = sum(float(row["volume_mm3"]) for row in fragment_rows)
        histogram = histogram_rows("GLOBAL", "ALL", linear_sicn, global_volume, len(linear_sicn))
        tag_to_quality = {int(tag): linear_sicn[index] for index, tag in enumerate(linear_tags)}
        zone_quality_summary = []
        for zone_id, tags in sorted(zone_element_tags.items()):
            values = np.asarray([tag_to_quality[tag] for tag in tags], dtype=float)
            exact_volume = sum(float(row["volume_mm3"]) for row in fragment_rows if row["zone_id"] == zone_id)
            histogram.extend(histogram_rows("EXACT_ZONE", zone_id, values, exact_volume, len(tags)))
            zone_quality_summary.append({
                "zone_id": zone_id, "family": "C07-MATRIX" if zone_id == "C07-MATRIX" else zone_rows[zone_id]["family"],
                "tetrahedra": len(tags), "minimum_sicn": float(np.min(values)),
                "fraction_below_0p20": float(np.mean(values < 0.20)),
                "monitored_min_0p20_gate": "PASS" if float(np.min(values)) >= 0.20 else "FAIL",
                "warning": WARNING,
            })
        write_csv(OUT / "sicn-histogram.csv", histogram)
        write_csv(OUT / "zone-quality-summary.csv", zone_quality_summary)

        gmsh.model.mesh.setOrder(2)
        tet10 = gmsh.model.mesh.getElementType("tetrahedron", 2)
        tet10_tags_raw, tet10_conn_raw = gmsh.model.mesh.getElementsByType(tet10)
        tet10_tags = np.asarray(tet10_tags_raw, dtype=np.int64)
        tet10_conn = np.asarray(tet10_conn_raw, dtype=np.int64).reshape((-1, 10))
        node_tags_raw, coords_raw, _ = gmsh.model.mesh.getNodes()
        node_tags = np.asarray(node_tags_raw, dtype=np.int64)
        node_xyz = np.asarray(coords_raw, dtype=float).reshape((-1, 3))
        node_lookup = {int(tag): node_xyz[index] for index, tag in enumerate(node_tags)}
        old_corners = sorted(set(int(value) for value in linear_conn.ravel()))
        new_corners = sorted(set(int(value) for value in tet10_conn[:, :4].ravel()))
        old_points = np.vstack([linear_lookup[tag] for tag in old_corners])
        new_points = np.vstack([node_lookup[tag] for tag in new_corners])
        distances, targets = cKDTree(new_points).query(old_points, k=1, workers=1)
        corner_bijection = bool(
            len(old_corners) == len(new_corners)
            and len(set(int(value) for value in targets)) == len(new_corners)
            and float(np.max(distances)) <= CORNER_TOL_MM
        )
        if not corner_bijection:
            raise RuntimeError(f"linear-to-Tet10 corner bijection failed: max={float(np.max(distances))}")

        # Signed Jacobian checks at the actual Gmsh Tet10 integration points.
        jacobian_rows = []
        q8_zone_volume: dict[str, float] = {zone_id: 0.0 for zone_id in zone_element_tags}
        all_jacobian_pass = True
        for order in (4, 6, 8):
            local_coord, weights_raw = gmsh.model.mesh.getIntegrationPoints(tet10, f"Gauss{order}")
            weights = np.asarray(weights_raw, dtype=float)
            for volume_tag, zone_id in sorted(volume_zone.items()):
                jac_raw, det_raw, _coord_raw = gmsh.model.mesh.getJacobians(tet10, local_coord, volume_tag)
                det = np.asarray(det_raw, dtype=float)
                if det.size == 0:
                    raise RuntimeError(f"empty Jacobian block: volume={volume_tag}")
                matrices = np.asarray(jac_raw, dtype=float).reshape((-1, 3, 3))
                frobenius = np.sqrt(np.sum(matrices * matrices, axis=(1, 2)))
                normalized = det / np.maximum(frobenius**3, np.finfo(float).tiny)
                wrong = int(np.count_nonzero(det <= 0.0))
                normalized_fail = int(np.count_nonzero(normalized <= NORMALIZED_DET_FLOOR))
                passed = wrong == 0 and normalized_fail == 0
                all_jacobian_pass = all_jacobian_pass and passed
                jacobian_rows.append({
                    "quadrature_order": order, "zone_id": zone_id,
                    "volume_tag_diagnostic_only": volume_tag, "quadrature_samples": det.size,
                    "wrong_or_zero_count": wrong, "normalized_floor_fail_count": normalized_fail,
                    "minimum_determinant": float(np.min(det)), "minimum_normalized_determinant": float(np.min(normalized)),
                    "normalized_floor": NORMALIZED_DET_FLOOR, "actual_gmsh_tet10_quadrature_gate": "PASS" if passed else "FAIL",
                    "full_reference_domain_positivity": "UNVERIFIED", "warning": WARNING,
                })
                if order == 8:
                    element_count = det.size // len(weights)
                    q8_zone_volume[zone_id] += float(np.sum(det.reshape((element_count, len(weights))) * weights[None, :]))
        write_csv(OUT / "actual-quadrature-jacobian-register.csv", jacobian_rows)

        volume_rows = []
        for zone_id, integrated in sorted(q8_zone_volume.items()):
            exact = sum(float(row["volume_mm3"]) for row in fragment_rows if row["zone_id"] == zone_id)
            volume_rows.append({
                "zone_id": zone_id, "exact_occ_volume_mm3": exact, "tet10_q8_integrated_volume_mm3": integrated,
                "relative_error": abs(integrated - exact) / exact,
                "credit": "CURVED-MESH GEOMETRY CONSERVATION SCREEN ONLY", "warning": WARNING,
            })
        write_csv(OUT / "zone-volume-integration.csv", volume_rows)

        zone_codes = {zone_id: index for index, zone_id in enumerate(sorted(zone_element_tags))}
        element_zone_code = np.asarray([zone_codes[element_zone[int(tag)]] for tag in linear_tags], dtype=np.int32)
        raw_path = OUT / "raw-conformal-zone-mesh.npz"
        np.savez_compressed(
            raw_path, linear_node_tags=linear_node_tags, linear_node_xyz=linear_xyz,
            linear_element_tags=linear_tags, linear_tet4_connectivity=linear_conn,
            linear_sicn=linear_sicn, element_zone_code=element_zone_code,
            node_tags=node_tags, node_xyz=node_xyz, tet10_element_tags=tet10_tags,
            tet10_connectivity=tet10_conn,
        )
        mesh_path = OUT / "c07-conformal-zone-mesh.msh"
        mesh_gzip_path = OUT / "c07-conformal-zone-mesh.msh.gz"
        gmsh.write(str(mesh_path))
        mesh_uncompressed_sha256 = sha(mesh_path)
        mesh_uncompressed_bytes = mesh_path.stat().st_size
        with mesh_path.open("rb") as source, mesh_gzip_path.open("wb") as compressed_stream:
            with gzip.GzipFile(filename="", mode="wb", fileobj=compressed_stream, compresslevel=9, mtime=0) as target:
                shutil.copyfileobj(source, target, length=1024 * 1024)
        mesh_path.unlink()

        global_min = float(np.min(linear_sicn))
        global_fraction = float(np.mean(linear_sicn < 0.20))
        monitored_failures = [row["zone_id"] for row in zone_quality_summary if row["zone_id"] != "C07-MATRIX" and row["monitored_min_0p20_gate"] != "PASS"]
        global_quality = global_min >= 0.10 and global_fraction <= 0.001
        r279_c02 = bool(global_quality and not monitored_failures and all_jacobian_pass)
        status = {
            "identifier": IDENT, "round": ROUND, "date": "2026-08-13",
            "r288_brep_sha256": sha(BREP), "linear_tetrahedra": len(linear_tags),
            "tet10_tetrahedra": len(tet10_tags), "vertices": len(new_corners),
            "exact_zone_element_provenance_complete": True,
            "global_sicn_minimum": global_min, "global_sicn_fraction_below_0p20": global_fraction,
            "global_sicn_gate": global_quality, "monitored_zone_histograms_complete": True,
            "monitored_zone_minimum_gate": not monitored_failures,
            "monitored_zone_failures": monitored_failures,
            "actual_quadrature_signed_jacobian_gate": all_jacobian_pass,
            "full_reference_domain_curved_jacobian_positive": False,
            "corner_bijection_gate": corner_bijection,
            "mesh_gzip_sha256": sha(mesh_gzip_path),
            "mesh_uncompressed_sha256": mesh_uncompressed_sha256,
            "mesh_uncompressed_bytes": mesh_uncompressed_bytes,
            "r279_c02_complete": r279_c02,
            "structural_solution_executed": False, "mesh_convergence_complete": False,
            "r278_h02_closed": False, "capacity_credit": False, "selected": False,
            "safety_credit": False, "procurement_authorized": False,
            "fabrication_authorized": False, "assembly_authorized": False,
            "connection_authorized": False, "powered_testing_authorized": False,
            "motion_authorized": False, "energization_authorized": False,
            "seconds": time.perf_counter() - started, "warning": WARNING,
        }
        (OUT / "analysis-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
        provenance = {
            "identifier": IDENT, "generator_path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
            "generator_sha256": sha(Path(__file__).resolve()), "r288_brep_path": BREP.relative_to(ROOT).as_posix(),
            "r288_brep_sha256": sha(BREP), "r288_fragment_register_sha256": sha(FRAGMENTS),
            "r288_zone_register_sha256": sha(ZONES), "python": sys.version, "platform": platform.platform(),
            "gmsh_version": importlib.metadata.version("gmsh"), "numpy_version": importlib.metadata.version("numpy"),
            "scipy_version": importlib.metadata.version("scipy"), "gmsh_build": gmsh.option.getString("General.BuildInfo"),
            "general_num_threads": 1, "algorithm3d": 1, "linear_optimizer": "Netgen",
            "high_order_optimizer": "NONE", "size_fields_mm": FAMILY_SIZE,
            "warning": WARNING,
        }
        (OUT / "execution-provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
        holds = [
            "Any R279-C02 failure reported by this bounded mesh must be corrected under a preregistered successor mesh; thresholds may not be loosened.",
            "Prove full-reference-tetra curved Jacobian positivity or retain the finite actual-quadrature boundary.",
            "Map every exterior Tet10 facet to exact B-Rep faces and rerun load area/resultant/location/moment preservation.",
            "Freeze fixed-offset hole gauge thickness and add those exact domains.",
            "Execute structural fields, sections, probes, direct zone quadrature, singularity trends and L0-L3/L4 convergence.",
            "Close contact, joined hardware, dynamics, physical correlation, material and qualified capacity separately.",
        ]
        write_csv(OUT / "open-holds.csv", [{
            "hold_id": f"R289-H{i:02d}", "hold": hold, "state": "OPEN", "closure_evidence": "NOT EXECUTED",
            "effect": "R278-H02, CAPACITY AND ALL WORK AUTHORITY REMAIN OPEN", "warning": WARNING,
        } for i, hold in enumerate(holds, 1)])
        (OUT / "README.md").write_text(
            f"# {IDENT}\n\n**{WARNING}**\n\nR289 meshes the exact R288 Boolean partition. Every tetrahedron inherits one exact volume-entity provenance; no centroid or sampled-distance zone membership is used. Full fixed-bin SICN histograms are retained globally and for every exact zone, and signed/normalized Tet10 Jacobians are evaluated at the actual Gmsh Gauss4/Gauss6/Gauss8 points.\n\nThe result is a bounded mesh-quality execution only. Full-domain Jacobian positivity, exterior facet fidelity, structural fields, convergence, H02, capacity, safety credit and every work authority remain open.\n",
            encoding="utf-8",
        )
        manifest_rows = []
        for path in sorted(OUT.iterdir()):
            if path.is_file() and path.name != "file-manifest.csv":
                manifest_rows.append({"relative_path": path.name, "sha256": sha(path), "bytes": path.stat().st_size, "warning": WARNING})
        write_csv(OUT / "file-manifest.csv", manifest_rows)
        if RELEASE.exists():
            shutil.rmtree(RELEASE)
        RELEASE.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(OUT, RELEASE)
        print(json.dumps(status, indent=2))
        return 0 if r279_c02 else 2
    finally:
        gmsh.finalize()


if __name__ == "__main__":
    raise SystemExit(main())
