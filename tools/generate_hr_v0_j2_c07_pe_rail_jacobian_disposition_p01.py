#!/usr/bin/env python3
"""Dispose R303 and freeze the next high-order-curving method boundary."""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
from pathlib import Path

import numpy as np

from hr_v0_mesh_raw_shards import load_shards

ROOT = Path(__file__).resolve().parents[1]
R300 = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-seam-free-jacobian-mesh-p0.1"
R301 = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-seam-free-jacobian-failure-localization-p0.1"
R303 = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-rail-jacobian-mesh-p0.1"
R304 = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-rail-jacobian-failure-localization-p0.1"
OUT = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-rail-jacobian-disposition-p0.1"
RELEASE = ROOT / "release/hr-v0/j2-c07-pe-rail-jacobian-disposition-p0.1"
IDENT = "HR-V0-J2-C07-PE-RAIL-JACOBIAN-DISPOSITION-P0.1"
WARNING = "PRELIMINARY - RAIL-JACOBIAN SUCCESSOR DISPOSITION ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, data: list[dict[str, object]]) -> None:
    fields: list[str] = []
    for row in data:
        for field in row:
            if field not in fields:
                fields.append(field)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)


def main() -> int:
    r300 = json.loads((R300 / "analysis-status.json").read_text(encoding="utf-8"))
    r303 = json.loads((R303 / "analysis-status.json").read_text(encoding="utf-8"))
    r301 = json.loads((R301 / "analysis-status.json").read_text(encoding="utf-8"))
    r304 = json.loads((R304 / "analysis-status.json").read_text(encoding="utf-8"))
    if not (r300["global_sicn_gate"] and r300["monitored_zone_minimum_gate"] and r303["global_sicn_gate"] and r303["monitored_zone_minimum_gate"]):
        raise RuntimeError("linear quality boundary drift")
    if r300["actual_quadrature_signed_jacobian_gate"] or r303["actual_quadrature_signed_jacobian_gate"]:
        raise RuntimeError("curved failure boundary drift")
    if r301["failed_order_qp_pairs"] != 3 or r304["failed_order_qp_pairs"] != 10:
        raise RuntimeError("failure-count boundary drift")

    failures = read_csv(R304 / "curved-jacobian-failure-localization.csv")
    element_tags = {int(row["element_tag"]) for row in failures}
    if len(element_tags) != 1:
        raise RuntimeError("expected one R303 failed element")
    failed_tag = next(iter(element_tags))
    raw = load_shards(R303)
    indexes = np.where(raw["tet10_element_tags"] == failed_tag)[0]
    if len(indexes) != 1:
        raise RuntimeError("failed element identity")
    connectivity = raw["tet10_connectivity"][int(indexes[0])]
    node_index = {int(tag): index for index, tag in enumerate(raw["node_tags"])}
    xyz = np.asarray([raw["node_xyz"][node_index[int(tag)]] for tag in connectivity])
    corners = xyz[:4]
    edge_pairs = ((0, 1), (1, 2), (2, 0), (0, 3), (2, 3), (3, 1))
    edge_lengths = [float(np.linalg.norm(corners[b] - corners[a])) for a, b in edge_pairs]
    surface_triangle_area = float(np.linalg.norm(np.cross(corners[2] - corners[0], corners[3] - corners[0])) / 2.0)
    competing_midside_gap = float(np.linalg.norm(xyz[7] - xyz[8]))
    linear_index = np.where(raw["linear_element_tags"] == failed_tag)[0]
    if len(linear_index) != 1:
        raise RuntimeError("failed linear element identity")

    comparison = [
        {
            "metric": "tet10_elements",
            "R300": r300["tet10_tetrahedra"],
            "R303": r303["tet10_tetrahedra"],
            "preferred": "R300",
            "reason": "additional rail field did not close curved gate",
            "warning": WARNING,
        },
        {
            "metric": "global_minimum_sicn",
            "R300": r300["global_sicn_minimum"],
            "R303": r303["global_sicn_minimum"],
            "preferred": "R300",
            "reason": "R303 reduces linear quality reserve",
            "warning": WARNING,
        },
        {
            "metric": "failed_order_qp_pairs",
            "R300": r301["failed_order_qp_pairs"],
            "R303": r304["failed_order_qp_pairs"],
            "preferred": "R300",
            "reason": "R303 increases sampled curved failures",
            "warning": WARNING,
        },
        {
            "metric": "unique_failed_elements",
            "R300": r301["unique_failed_elements"],
            "R303": r304["unique_failed_elements"],
            "preferred": "R303",
            "reason": "fewer elements, but worse aggregate and determinant minima",
            "warning": WARNING,
        },
    ]
    geometry = [
        {
            "element_tag": failed_tag,
            "linear_sicn": float(raw["linear_sicn"][int(linear_index[0])]),
            "minimum_corner_edge_mm": min(edge_lengths),
            "maximum_corner_edge_mm": max(edge_lengths),
            "surface_triangle_area_mm2": surface_triangle_area,
            "competing_surface_midside_gap_mm": competing_midside_gap,
            "corner_node_tags_json": json.dumps([int(tag) for tag in connectivity[:4]], separators=(",", ":")),
            "midside_node_tags_json": json.dumps([int(tag) for tag in connectivity[4:]], separators=(",", ":")),
            "diagnosis": "near-coincident surface corner/edge geometry remains vulnerable after face-size refinement; use a constrained high-order curving method, not another smaller face field",
            "warning": WARNING,
        }
    ]
    status = {
        "identifier": IDENT,
        "round": "R305",
        "date": "2026-08-13",
        "r300_status_sha256": sha(R300 / "analysis-status.json"),
        "r301_status_sha256": sha(R301 / "analysis-status.json"),
        "r303_status_sha256": sha(R303 / "analysis-status.json"),
        "r304_status_sha256": sha(R304 / "analysis-status.json"),
        "r303_face_refinement_rejected": True,
        "r300_restored_as_next_method_baseline": True,
        "next_method": "single constrained HighOrder optimization of R300 C07-MATRIX with exact corner restoration and mandatory B-Rep/facet/load revalidation",
        "next_mesh_executed": False,
        "structural_solution_executed": False,
        "r279_c02_complete": False,
        "r278_h02_closed": False,
        "capacity_credit": False,
        "selected": False,
        "safety_credit": False,
        "work_authority": False,
        "warning": WARNING,
    }
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    write_csv(OUT / "r300-r303-comparison.csv", comparison)
    write_csv(OUT / "failed-element-geometry.csv", geometry)
    (OUT / "analysis-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "execution-provenance.json").write_text(
        json.dumps(
            {
                "identifier": IDENT,
                "generator_sha256": sha(Path(__file__).resolve()),
                "r300_status_sha256": sha(R300 / "analysis-status.json"),
                "r301_status_sha256": sha(R301 / "analysis-status.json"),
                "r303_status_sha256": sha(R303 / "analysis-status.json"),
                "r304_status_sha256": sha(R304 / "analysis-status.json"),
                "r303_raw_linear_sha256": sha(R303 / "raw-linear-mesh.npz"),
                "r303_raw_tet10_sha256": sha(R303 / "raw-tet10-mesh.npz"),
                "warning": WARNING,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (OUT / "README.md").write_text(
        f"# {IDENT}\n\n**{WARNING}**\n\n"
        "R305 rejects the R303 rail-face refinement. R303 retains the linear gates but degrades the global minimum SICN "
        "and increases failed Q4/Q6/Q8 points from 3 to 10. R300 is restored as the next numerical-method baseline. "
        "The next candidate must change only high-order curving, restore every linear corner exactly, and revalidate "
        "exact B-Rep facets, surface deviation, area, and load geometry before any structural work.\n",
        encoding="utf-8",
    )
    manifest = []
    for path in sorted(OUT.iterdir()):
        if path.name != "file-manifest.csv":
            manifest.append({"relative_path": path.name, "sha256": sha(path), "bytes": path.stat().st_size, "warning": WARNING})
    write_csv(OUT / "file-manifest.csv", manifest)
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    RELEASE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(OUT, RELEASE)
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
