#!/usr/bin/env python3
"""Generate the R273 linear C06/C07 screen for exact P0.12 CAD.

This retains the prior small-displacement rejection model while moving C07's
idealized restraint back to the original 9.525 mm A04 clamped land.  It is not
a joined-bolt, nonlinear-contact, dynamic, fatigue, or release analysis.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

import generate_hr_v0_j2_stop_sideweb_fea_p01 as prior


ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / "cad/hr-v0/generated/arm-architecture-p0.12-access-well-stop"
OUT = ROOT / "mechanical/analysis/hr-v0-j2-stop-access-well-fea-p0.1"
ID = "HR-V0-J2-STOP-ACCESS-WELL-FEA-P0.1"
CAD_ID = "HR-V0-ARM-ARCH-P0.12-ACCESS-WELL-STOP-CANDIDATE"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def c07_boundary(mesh):
    boundary = mesh.boundary_facets()
    centers = mesh.p[:, mesh.facets[:, boundary]].mean(axis=1)
    positive = boundary[(np.abs(centers[1] - 8.525) < 1e-5) & (centers[0] > 34.0)]
    negative = boundary[(np.abs(centers[1] - 8.525) < 1e-5) & (centers[0] < -34.0)]
    fixed = prior.fixed_hole_nodes(mesh)
    if len(fixed) < 80 or len(positive) < 8 or len(negative) < 8:
        raise RuntimeError(f"C07 boundary selection failed: fixed={len(fixed)} positive={len(positive)} negative={len(negative)}")
    return fixed, positive, negative, prior.facets_area(mesh, positive), prior.facets_area(mesh, negative)


def write_csv(path: Path, records: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def main() -> int:
    prior.CAD = CAD
    prior.OUT = OUT
    prior.ID = ID
    prior.CAD_ID = CAD_ID
    prior.STATIC = CAD / "corrected-static-stop-screen.csv"
    prior.c07_boundary = c07_boundary
    result = prior.main()
    if result:
        return result
    for path in OUT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".csv", ".json", ".md", ".html"}:
            continue
        text = path.read_text(encoding="utf-8")
        text = text.replace("R272", "R273").replace("P0.11", "P0.12").replace("sideweb", "access-well")
        path.write_text(text, encoding="utf-8", newline="\n")
    status_path = OUT / "analysis-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "identifier": ID,
        "round": "R273",
        "cad_identifier": CAD_ID,
        "c07_restraint_boundary": "idealized fixed cylindrical surfaces only in original 0..9.525 mm A04 land; access-well web and real joined stack not fixed",
        "joined_fastener_model_complete": False,
        "selected": False,
        "fabrication_authorized": False,
        "motion_authorized": False,
        "energization_authorized": False,
        "safety_credit": False,
        "warning": WARNING,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    holds = list(csv.DictReader((OUT / "open-holds.csv").open(newline="", encoding="utf-8")))
    holds.extend([
        {"hold_id":"R273-H13","hold":"Exact currently purchasable A04 hardware and installation tool are selected, received and inspected","state":"OPEN","closure_evidence":"supplier quote, datasheets, certificates, dimensional/fit record","release_effect":"BLOCKS P0.12 SELECTION/FABRICATION/MOTION","warning":WARNING},
        {"hold_id":"R273-H14","hold":"A04 joined-load model includes preload, friction/slip, prying, S102 flexibility, bearing, thread/head/nut/washer behavior and tolerances","state":"OPEN","closure_evidence":"accepted calculation/FEA and calibrated physical correlation","release_effect":"BLOCKS P0.12 SELECTION/FABRICATION/MOTION","warning":WARNING},
        {"hold_id":"R273-H15","hold":"Access-well geometry and A04 installation pass FAI, tool-access, torque/locking and proof tests","state":"OPEN","closure_evidence":"completed FAI/traveler, calibrated torque/prevailing-torque records, witness marks and proof report","release_effect":"BLOCKS P0.12 SELECTION/FABRICATION/MOTION","warning":WARNING},
    ])
    write_csv(OUT / "open-holds.csv", holds)
    acceptance = list(csv.DictReader((OUT / "acceptance-matrix.csv").open(newline="", encoding="utf-8")))
    for index, hold in enumerate(holds[-3:], 13):
        acceptance.append({"acceptance_id":f"R273-ACC-{index:02d}","criterion":hold["hold"],"execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":"","warning":WARNING})
    write_csv(OUT / "acceptance-matrix.csv", acceptance)
    print(f"Generated {ID}; P0.12 remains unselected and joined-load closure remains open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
