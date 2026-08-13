#!/usr/bin/env python3
"""Localize every R289 SICN and sampled curved-Jacobian failure."""
from __future__ import annotations

import csv
import gzip
import hashlib
import html
import json
import shutil
from pathlib import Path

import gmsh
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
R289 = ROOT / "mechanical/analysis/hr-v0-j2-c07-conformal-zone-mesh-p0.1"
R288 = ROOT / "mechanical/analysis/hr-v0-j2-c07-exact-zone-partition-p0.1"
MSH_GZIP = R289 / "c07-conformal-zone-mesh.msh.gz"
RAW = R289 / "raw-conformal-zone-mesh.npz"
BREP = R288 / "c07-exact-zone-fragmented.brep"
OUT = ROOT / "mechanical/analysis/hr-v0-j2-c07-conformal-mesh-failure-localization-p0.1"
RELEASE = ROOT / "release/hr-v0/j2-c07-conformal-mesh-failure-localization-p0.1"
IDENT = "HR-V0-J2-C07-CONFORMAL-MESH-FAILURE-LOCALIZATION-P0.1"
WARNING = "PRELIMINARY - CONFORMAL MESH FAILURE LOCALIZATION ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


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


def html_table(rows: list[dict[str, object]], fields: list[str]) -> str:
    head = "".join(f"<th>{html.escape(field.replace('_', ' '))}</th>" for field in fields)
    body = "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(row.get(field, '')))}</td>" for field in fields) + "</tr>"
        for row in rows
    )
    return f"<div class='scroll'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"


def face_signature(tag: int) -> str:
    bbox = [round(float(value), 9) for value in gmsh.model.getBoundingBox(2, tag)]
    record = {
        "geometry_type": gmsh.model.getType(2, tag), "bbox_mm": bbox,
        "area_mm2": round(float(gmsh.model.occ.getMass(2, tag)), 9),
        "center_mm": [round(float(value), 9) for value in gmsh.model.occ.getCenterOfMass(2, tag)],
    }
    return stable(record)


def nearest_exact_face(point: np.ndarray, faces: list[int]) -> dict[str, object]:
    best = None
    for tag in faces:
        closest, _param = gmsh.model.getClosestPoint(2, tag, point.tolist())
        xyz = np.asarray(closest[:3], dtype=float)
        distance = float(np.linalg.norm(xyz - point))
        if best is None or distance < best[0]:
            best = (distance, tag, xyz)
    assert best is not None
    distance, tag, xyz = best
    return {
        "nearest_exact_face_tag_diagnostic_only": tag,
        "nearest_exact_face_signature_sha256": face_signature(tag),
        "nearest_exact_face_type": gmsh.model.getType(2, tag),
        "nearest_exact_face_bbox_mm_json": json.dumps([round(float(value), 9) for value in gmsh.model.getBoundingBox(2, tag)], separators=(",", ":")),
        "nearest_exact_face_distance_mm": distance,
        "nearest_exact_point_mm_json": json.dumps([float(value) for value in xyz], separators=(",", ":")),
    }


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    working_mesh = OUT / "_working-r289-conformal-zone-mesh.msh"
    mesh_uncompressed_digest = hashlib.sha256()
    with gzip.open(MSH_GZIP, "rb") as source, working_mesh.open("wb") as target:
        while True:
            block = source.read(1024 * 1024)
            if not block:
                break
            target.write(block)
            mesh_uncompressed_digest.update(block)
    status289 = json.loads((R289 / "analysis-status.json").read_text(encoding="utf-8"))
    if status289["r279_c02_complete"] or status289["monitored_zone_minimum_gate"] or status289["actual_quadrature_signed_jacobian_gate"]:
        raise RuntimeError("R289 failure-state identity drift")

    raw = np.load(RAW)
    tags = raw["linear_element_tags"]
    conn = raw["linear_tet4_connectivity"]
    quality = raw["linear_sicn"]
    zone_codes = raw["element_zone_code"]
    node_tags = raw["linear_node_tags"]
    xyz = raw["linear_node_xyz"]
    lookup = {int(tag): xyz[index] for index, tag in enumerate(node_tags)}
    zone_names = sorted(row["zone_id"] for row in csv.DictReader((R289 / "zone-quality-summary.csv").open(newline="", encoding="utf-8")))

    sicn_failures: list[dict[str, object]] = []
    failure_indices = np.flatnonzero(quality < 0.20)
    for index in failure_indices:
        corners = np.vstack([lookup[int(tag)] for tag in conn[index]])
        edges = [float(np.linalg.norm(corners[a] - corners[b])) for a, b in ((0,1),(0,2),(0,3),(1,2),(1,3),(2,3))]
        sicn_failures.append({
            "failure_kind": "LINEAR_SICN_BELOW_0P20", "element_tag": int(tags[index]),
            "exact_zone_id": zone_names[int(zone_codes[index])], "sicn": float(quality[index]),
            "corner_centroid_x_mm": float(np.mean(corners[:,0])), "corner_centroid_y_mm": float(np.mean(corners[:,1])),
            "corner_centroid_z_mm": float(np.mean(corners[:,2])), "minimum_corner_edge_mm": min(edges),
            "mean_corner_edge_mm": float(np.mean(edges)), "maximum_corner_edge_mm": max(edges),
            "credit": "DIAGNOSTIC LOCALIZATION; EXACT ZONE MEMBERSHIP FROM R289 VOLUME PROVENANCE", "warning": WARNING,
        })
    write_csv(OUT / "sicn-failure-localization.csv", sicn_failures)

    gmsh.initialize(["-nopopup"])
    gmsh.option.setNumber("General.Terminal", 0)
    jac_failures: list[dict[str, object]] = []
    try:
        gmsh.open(str(working_mesh))
        tet10 = gmsh.model.mesh.getElementType("tetrahedron", 2)
        physical_name_to_entity = {}
        for dim, physical in gmsh.model.getPhysicalGroups(3):
            name = gmsh.model.getPhysicalName(dim, physical)
            entities = gmsh.model.getEntitiesForPhysicalGroup(dim, physical)
            if len(entities) != 1:
                raise RuntimeError(f"physical zone does not resolve to one exact volume: {name}={entities}")
            physical_name_to_entity[name] = int(entities[0])
        matrix_entity = physical_name_to_entity["C07-MATRIX"]
        types, tag_blocks, _node_blocks = gmsh.model.mesh.getElements(3, matrix_entity)
        element_tags = None
        for element_type, block in zip(types, tag_blocks):
            if int(element_type) == int(tet10):
                element_tags = np.asarray(block, dtype=np.int64)
        if element_tags is None:
            raise RuntimeError("C07-MATRIX Tet10 elements missing")
        for order in (4, 6, 8):
            local, _weights = gmsh.model.mesh.getIntegrationPoints(tet10, f"Gauss{order}")
            local_points = np.asarray(local, dtype=float).reshape((-1, 3))
            jac_raw, det_raw, coord_raw = gmsh.model.mesh.getJacobians(tet10, local, matrix_entity)
            det = np.asarray(det_raw, dtype=float).reshape((len(element_tags), len(local_points)))
            jac = np.asarray(jac_raw, dtype=float).reshape((len(element_tags), len(local_points), 3, 3))
            coords = np.asarray(coord_raw, dtype=float).reshape((len(element_tags), len(local_points), 3))
            frob = np.sqrt(np.sum(jac * jac, axis=(2,3)))
            normalized = det / np.maximum(frob**3, np.finfo(float).tiny)
            for element_index, qp_index in np.argwhere((det <= 0.0) | (normalized <= 1.0e-10)):
                point = coords[element_index, qp_index]
                jac_failures.append({
                    "failure_kind": "CURVED_TET10_ACTUAL_QUADRATURE", "quadrature_order": order,
                    "element_tag": int(element_tags[element_index]), "quadrature_point_index": int(qp_index),
                    "physical_x_mm": float(point[0]), "physical_y_mm": float(point[1]), "physical_z_mm": float(point[2]),
                    "determinant": float(det[element_index, qp_index]),
                    "normalized_determinant": float(normalized[element_index, qp_index]),
                    "credit": "DIAGNOSTIC LOCALIZATION; FULL-DOMAIN POSITIVITY UNVERIFIED", "warning": WARNING,
                })

        # Reopen the exact partition and bind each failed QP to the nearest
        # exact B-Rep face.  Tags are diagnostic; geometric signatures persist.
        gmsh.clear()
        gmsh.model.add("R290_EXACT_FACE_LOCALIZATION")
        gmsh.model.occ.importShapes(str(BREP))
        gmsh.model.occ.synchronize()
        faces = [tag for dim, tag in gmsh.model.getEntities(2)]
        for row in jac_failures:
            point = np.asarray((row["physical_x_mm"], row["physical_y_mm"], row["physical_z_mm"]), dtype=float)
            row.update(nearest_exact_face(point, faces))
    finally:
        gmsh.finalize()
    working_mesh.unlink()
    write_csv(OUT / "curved-jacobian-failure-localization.csv", jac_failures)

    sicn_by_zone: dict[str, int] = {}
    for row in sicn_failures:
        sicn_by_zone[row["exact_zone_id"]] = sicn_by_zone.get(row["exact_zone_id"], 0) + 1
    jac_elements = sorted({int(row["element_tag"]) for row in jac_failures})
    face_clusters: dict[str, int] = {}
    for row in jac_failures:
        signature = str(row["nearest_exact_face_signature_sha256"])
        face_clusters[signature] = face_clusters.get(signature, 0) + 1
    disposition = {
        "identifier": IDENT, "round": "R290", "date": "2026-08-13",
        "r289_raw_sha256": sha(RAW), "r289_mesh_gzip_sha256": sha(MSH_GZIP),
        "r289_mesh_uncompressed_sha256": mesh_uncompressed_digest.hexdigest(),
        "sicn_failure_elements": len(sicn_failures), "sicn_failures_by_exact_zone": sicn_by_zone,
        "curved_jacobian_failed_order_qp_pairs": len(jac_failures),
        "curved_jacobian_unique_failed_elements": len(jac_elements),
        "curved_jacobian_nearest_exact_face_clusters": face_clusters,
        "successor_rule": "start from frozen R289 settings; add local fields only to the four failed exact PE straight volumes and the exact B-Rep faces localized here; execute as a new preregistered variant; retain R289 unchanged",
        "thresholds_unchanged": True, "remesh_executed": False,
        "r279_c02_complete": False, "r278_h02_closed": False, "capacity_credit": False,
        "selected": False, "safety_credit": False, "fabrication_authorized": False,
        "powered_testing_authorized": False, "motion_authorized": False,
        "energization_authorized": False, "warning": WARNING,
    }
    (OUT / "analysis-status.json").write_text(json.dumps(disposition, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(
        f"# {IDENT}\n\n**{WARNING}**\n\nR290 localizes every R289 linear SICN value below 0.20 and every wrong/zero or normalized-floor Tet10 Jacobian at the actual Gauss4/Gauss6/Gauss8 points. Exact-zone membership comes from the R289 physical-volume provenance. Curved failures are additionally bound to the nearest exact R288 B-Rep face.\n\nNo threshold changes, remesh, structural solve, capacity or work authority follow from this diagnostic package.\n",
        encoding="utf-8",
    )
    sicn_table = html_table(sicn_failures, ["exact_zone_id", "element_tag", "sicn", "corner_centroid_x_mm", "corner_centroid_y_mm", "corner_centroid_z_mm"])
    jac_table = html_table(jac_failures, ["quadrature_order", "element_tag", "determinant", "normalized_determinant", "physical_x_mm", "physical_y_mm", "physical_z_mm", "nearest_exact_face_type", "nearest_exact_face_signature_sha256"])
    cluster_rows = [
        {"exact_face_signature_sha256": signature, "failed_order_qp_pairs": count}
        for signature, count in sorted(face_clusters.items(), key=lambda item: (-item[1], item[0]))
    ]
    cluster_table = html_table(cluster_rows, ["exact_face_signature_sha256", "failed_order_qp_pairs"])
    guide = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{IDENT}</title><style>:root{{--navy:#082b55;--blue:#245aa6;--sky:#8ed8f8;--gold:#f4b942;--paper:#f7fbff;--ink:#102a43;--line:#9ccfe8}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}header{{padding:clamp(28px,6vw,68px) 20px;background:linear-gradient(135deg,var(--navy),var(--blue));color:white}}header>div,main{{max-width:1240px;margin:auto}}main{{padding:28px 20px 80px}}h1{{font-size:clamp(34px,6vw,64px);line-height:1.08}}h2{{font-size:clamp(25px,3vw,38px);color:var(--navy)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805800;padding:15px 18px;font-weight:900;font-size:16px}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}}.card,details{{background:white;border:2px solid var(--sky);border-radius:14px;padding:18px}}.metric{{font-size:clamp(30px,5vw,48px);font-weight:900;color:var(--blue)}}details{{margin-top:18px}}summary{{font-size:20px;font-weight:800;cursor:pointer}}.scroll{{overflow-x:auto;margin-top:14px;border:2px solid var(--line);border-radius:10px}}table{{border-collapse:collapse;width:100%;min-width:1050px}}th,td{{padding:12px 14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--navy);color:white}}code{{overflow-wrap:anywhere}}@media(max-width:620px){{main{{padding-inline:14px}}}}</style></head><body><header><div><p class='warning'>{WARNING}</p><p>R288 → R289 → R290</p><h1>The exact zones work. The first conformal mesh does not pass yet.</h1><p>Every failure is retained and localized before the successor prescription is changed.</p></div></header><main><section class='cards'><article class='card'><div class='metric'>27</div><p>exact positive-volume analysis zones</p></article><article class='card'><div class='metric'>722,457</div><p>R289 conformal tetrahedra</p></article><article class='card'><div class='metric'>{len(sicn_failures)}</div><p>linear cells below the 0.20 monitored-zone floor</p></article><article class='card'><div class='metric'>{len(jac_elements)}</div><p>unique curved elements failing sampled Jacobian gates</p></article></section><h2>Disposition</h2><p><strong>R279-C02 remains open.</strong> The global SICN gate passes, but the four straight pocket bands fail their monitored-zone minimum and the curved matrix contains six failed elements. Thresholds remain unchanged.</p><details open><summary>Low-SICN cells at pocket-band junctions</summary>{sicn_table}</details><details><summary>Curved Jacobian failure points</summary>{jac_table}</details><details><summary>Exact CAD face clusters</summary>{cluster_table}</details><h2>Next controlled action</h2><p>{html.escape(disposition['successor_rule'])}</p><p>No structural solve, capacity conclusion, fabrication authority, motion authority, or energization authority follows from this page.</p></main></body></html>"""
    (OUT / "index.html").write_text(guide, encoding="utf-8")
    provenance = {
        "generator_sha256": sha(Path(__file__).resolve()), "r289_raw_sha256": sha(RAW),
        "r289_mesh_gzip_sha256": sha(MSH_GZIP),
        "r289_mesh_uncompressed_sha256": mesh_uncompressed_digest.hexdigest(),
        "r288_brep_sha256": sha(BREP), "warning": WARNING,
    }
    (OUT / "execution-provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    manifest = []
    for path in sorted(OUT.iterdir()):
        if path.is_file() and path.name != "file-manifest.csv":
            manifest.append({"relative_path": path.name, "sha256": sha(path), "bytes": path.stat().st_size, "warning": WARNING})
    write_csv(OUT / "file-manifest.csv", manifest)
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    RELEASE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(OUT, RELEASE)
    print(json.dumps(disposition, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
