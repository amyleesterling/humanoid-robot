#!/usr/bin/env python3
"""Disposition the failed R293 relocation candidate and freeze its next boundary."""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
R291 = ROOT / "mechanical/analysis/hr-v0-j2-c07-conformal-successor-mesh-p0.1"
R293 = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-topology-mesh-p0.1"
PREREG = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-topology-prereg-p0.1"
OUT = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-topology-disposition-p0.1"
RELEASE = ROOT / "release/hr-v0/j2-c07-pe-topology-disposition-p0.1"
IDENT = "HR-V0-J2-C07-PE-TOPOLOGY-DISPOSITION-P0.1"
WARNING = (
    "PRELIMINARY - PE-JUNCTION MESH-METHOD DISPOSITION ONLY - NOT APPROVED FOR "
    "PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, "
    "MOTION, OR ENERGIZATION"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def table(rows: list[dict[str, object]]) -> str:
    fields = list(rows[0])
    head = "".join(f"<th>{field.replace('_', ' ')}</th>" for field in fields)
    body = "".join(
        "<tr>" + "".join(f"<td>{row[field]}</td>" for field in fields) + "</tr>"
        for row in rows
    )
    return f"<div class='scroll'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"


def main() -> int:
    status291 = json.loads((R291 / "analysis-status.json").read_text(encoding="utf-8"))
    status293 = json.loads((R293 / "analysis-status.json").read_text(encoding="utf-8"))
    if status293["r279_c02_complete"] or status293["global_sicn_gate"]:
        raise RuntimeError("R293 is not the retained failed candidate")
    if status293["actual_quadrature_signed_jacobian_gate"] is not True:
        raise RuntimeError("R293 did not retain the R291 curved-Jacobian success")
    data291 = np.load(R291 / "raw-conformal-zone-mesh.npz")
    data293 = np.load(R293 / "raw-conformal-zone-mesh.npz")
    tags291 = data291["linear_element_tags"]
    tags293 = data293["linear_element_tags"]
    conn291 = data291["linear_tet4_connectivity"]
    conn293 = data293["linear_tet4_connectivity"]
    if not np.array_equal(tags291, tags293) or not np.array_equal(conn291, conn293):
        raise RuntimeError("R293 changed linear tetrahedral topology; relocation-only comparison invalid")
    q291 = data291["linear_sicn"]
    q293 = data293["linear_sicn"]
    delta = q293 - q291
    tolerance = 1.0e-14
    changed = np.abs(delta) > tolerance
    improved = delta > tolerance
    worsened = delta < -tolerance
    unchanged = ~changed
    nodes = {int(tag): xyz for tag, xyz in zip(data293["linear_node_tags"], data293["linear_node_xyz"])}
    zone_names = sorted(row["zone_id"] for row in read_csv(R293 / "zone-quality-summary.csv"))
    zone_code = data293["element_zone_code"]
    low = np.flatnonzero(q293 < 0.20)
    localization = []
    for index in low:
        corners = conn293[index]
        xyz = np.vstack([nodes[int(tag)] for tag in corners])
        localization.append({
            "element_tag": int(tags293[index]),
            "exact_zone_id": zone_names[int(zone_code[index])],
            "r291_sicn": float(q291[index]),
            "r293_sicn": float(q293[index]),
            "delta_sicn": float(delta[index]),
            "change_class": "WORSENED" if worsened[index] else "IMPROVED" if improved[index] else "UNCHANGED",
            "centroid_x_mm": float(np.mean(xyz[:, 0])),
            "centroid_y_mm": float(np.mean(xyz[:, 1])),
            "centroid_z_mm": float(np.mean(xyz[:, 2])),
            "warning": WARNING,
        })

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    comparison = [
        {
            "metric": "linear_tetrahedra", "r291_netgen": status291["linear_tetrahedra"],
            "r293_netgen_relocate3d": status293["linear_tetrahedra"], "disposition": "UNCHANGED TOPOLOGY",
            "warning": WARNING,
        },
        {
            "metric": "global_minimum_sicn", "r291_netgen": status291["global_sicn_minimum"],
            "r293_netgen_relocate3d": status293["global_sicn_minimum"], "disposition": "REGRESSED",
            "warning": WARNING,
        },
        {
            "metric": "global_cells_below_0p20", "r291_netgen": int(np.count_nonzero(q291 < 0.20)),
            "r293_netgen_relocate3d": int(np.count_nonzero(q293 < 0.20)), "disposition": "REGRESSED",
            "warning": WARNING,
        },
        {
            "metric": "monitored_zone_failures", "r291_netgen": len(status291["monitored_zone_failures"]),
            "r293_netgen_relocate3d": len(status293["monitored_zone_failures"]), "disposition": "NO ADVANCE",
            "warning": WARNING,
        },
        {
            "metric": "actual_quadrature_jacobian_gate", "r291_netgen": status291["actual_quadrature_signed_jacobian_gate"],
            "r293_netgen_relocate3d": status293["actual_quadrature_signed_jacobian_gate"], "disposition": "RETAINED PASS",
            "warning": WARNING,
        },
        {
            "metric": "quality_change_counts", "r291_netgen": "baseline",
            "r293_netgen_relocate3d": f"improved={int(np.count_nonzero(improved))};worsened={int(np.count_nonzero(worsened))};unchanged={int(np.count_nonzero(unchanged))}",
            "disposition": "RELOCATION DOES NOT CLOSE DEFECT", "warning": WARNING,
        },
    ]
    write_csv(OUT / "r291-r293-comparison.csv", comparison)
    write_csv(OUT / "r293-low-sicn-localization.csv", localization)
    next_boundary = {
        "identifier": IDENT,
        "round": "R294",
        "date": "2026-08-13",
        "retained_success": "R291/R293 exact CAD, fields, target identity, and sampled actual-quadrature curved-Jacobian pass",
        "rejected_method": "Netgen followed by Relocate3D on an unchanged Delaunay tetrahedralization; it leaves all four PE straight-zone failures and adds low-quality C07-MATRIX cells",
        "required_next_preregistration": "preserve exact CAD, R291 fields and thresholds; generate a genuinely different linear tetrahedral topology using Gmsh Algorithm3D=4 (Frontal) followed by Netgen only; one candidate, one execution, no relocation and no high-order optimizer",
        "next_candidate_id": "R295-C07-PE-FRONTAL-V01",
        "acceptance_thresholds_unchanged": True,
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
    (OUT / "next-method-boundary.json").write_text(json.dumps(next_boundary, indent=2) + "\n", encoding="utf-8")
    status = {
        "identifier": IDENT,
        "round": "R294",
        "r293_candidate_rejected": True,
        "linear_topology_unchanged": True,
        "r293_low_sicn_cells": len(localization),
        "r293_monitored_zone_failures": status293["monitored_zone_failures"],
        "r293_actual_quadrature_jacobian_gate": True,
        "next_candidate_frozen": "R295-C07-PE-FRONTAL-V01",
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
    (OUT / "analysis-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "execution-provenance.json").write_text(json.dumps({
        "identifier": IDENT,
        "generator_path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
        "generator_sha256": sha(Path(__file__).resolve()),
        "r291_status_sha256": sha(R291 / "analysis-status.json"),
        "r291_raw_sha256": sha(R291 / "raw-conformal-zone-mesh.npz"),
        "r293_preregistration_sha256": sha(PREREG / "frozen-pe-topology-protocol.json"),
        "r293_status_sha256": sha(R293 / "analysis-status.json"),
        "r293_raw_sha256": sha(R293 / "raw-conformal-zone-mesh.npz"),
        "warning": WARNING,
    }, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(
        f"# {IDENT}\n\n**{WARNING}**\n\n"
        f"R294 rejects the preregistered R293 relocation candidate. It retains the same {len(tags293):,} tetrahedral topology, changes {int(np.count_nonzero(changed)):,} element-quality values, and leaves {len(localization)} cells below SICN 0.20 across the same four PE straight zones plus C07-MATRIX. The actual-quadrature curved-Jacobian gate remains clean.\n\n"
        "The next candidate changes the tetrahedralization itself: Gmsh Frontal Algorithm3D=4 followed by Netgen only, with exact CAD, fields, and thresholds unchanged. It is not executed by this disposition package.\n",
        encoding="utf-8",
    )
    page = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>R294 PE-junction method disposition</title><style>:root{{--navy:#082b55;--deep:#041a35;--gold:#f4b942;--paper:#f7fbff;--ink:#102a43;--line:#94c7e3}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,sans-serif}}header{{background:linear-gradient(135deg,var(--deep),var(--navy));color:white;padding:clamp(30px,6vw,72px) 20px}}header>div,main{{max-width:1240px;margin:auto}}main{{padding:30px 20px 80px}}h1{{font-size:clamp(34px,6vw,64px);line-height:1.05}}h2{{font-size:clamp(25px,3vw,38px);color:var(--navy)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805800;padding:15px 18px;font-weight:900}}.decision{{background:white;border:2px solid var(--line);border-left:10px solid #aa2e25;border-radius:14px;padding:20px;margin:24px 0}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:12px;background:white}}table{{border-collapse:collapse;width:100%;min-width:900px}}th,td{{padding:13px 14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--navy);color:white}}@media(max-width:620px){{body{{font-size:16px}}main{{padding-inline:14px}}}}</style></head><body><header><div><p class='warning'>{WARNING}</p><p>R294 · {IDENT}</p><h1>Relocation does not repair the PE-junction topology.</h1><p>The curved-Jacobian improvement remains, but the mesh-quality gate still fails.</p></div></header><main><section class='decision'><h2>R293 rejected; structural work remains gated</h2><p>All four pocket-edge straight zones still fail, and five additional low-quality cells appear in C07-MATRIX. The next experiment changes the tetrahedralization with the Frontal algorithm instead of moving the same nodes.</p></section><section><h2>R291 to R293 comparison</h2>{table(comparison)}</section><section><h2>Low-quality cell evidence</h2>{table(localization)}</section></main></body></html>"""
    (OUT / "index.html").write_text(page, encoding="utf-8")
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
