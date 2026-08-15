#!/usr/bin/env python3
"""Synchronize current R214 mechanical identity across gates and release metadata."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GATES = ROOT / "requirements/hr-v0-energization-gates.csv"
RELEASE = ROOT / "release/hr-v0/release-candidate.json"
MECHANICAL = "HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE"
CONFIG = "HR-V0-CONFIG-REC-P0.3"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, records: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def add_paths(existing: str, *paths: str) -> str:
    items = [item.strip() for item in existing.split(";") if item.strip()]
    for path in paths:
        if path not in items:
            items.append(path)
    return "; ".join(items)


def remove_paths(existing: str, *paths: str) -> str:
    rejected = set(paths)
    return "; ".join(item.strip() for item in existing.split(";") if item.strip() and item.strip() not in rejected)


def sync_gates() -> None:
    records = read_csv(GATES)
    by_id = {row["gate_id"]: row for row in records}
    eg3 = by_id["EG-003"]
    eg3["evidence_location"] = remove_paths(
        eg3["evidence_location"],
        "bom/hr-v0-mechanical-custom-part-binding.csv",
        "docs/hr-v0-mechanical-bom-binding-p0.1.md",
        "release/hr-v0/mechanical-bom-binding-p0.1/",
        "tools/check_hr_v0_mechanical_bom_binding_p01.py",
    )
    eg3["evidence_location"] = add_paths(
        eg3["evidence_location"],
        "bom/hr-v0-mechanical-custom-part-binding-p0.2.csv",
        "docs/hr-v0-mechanical-bom-binding-p0.2.md",
        "release/hr-v0/mechanical-bom-binding-p0.2/",
        "tools/check_hr_v0_mechanical_bom_binding_p02.py",
        "configuration/hr-v0-config-reconciliation-p0.3/",
        "release/hr-v0/configuration-reconciliation-p0.3/",
        "requirements/hr-v0-gate-evidence-supplement-r214.csv",
    )
    eg5 = by_id["EG-005"]
    eg5["evidence_location"] = add_paths(
        eg5["evidence_location"],
        "cad/hr-v0/generated/arm-architecture-p0.8-dwg-integrated/",
        "docs/hr-v0-arm-architecture-p0.8-dwg-integrated.md",
        "release/hr-v0/arm-architecture-p0.8-dwg-integrated/",
        "tools/generate_hr_v0_arm_architecture_p08.py",
        "tools/check_hr_v0_arm_architecture_p08.py",
        "configuration/hr-v0-config-reconciliation-p0.3/",
        "requirements/hr-v0-gate-evidence-supplement-r214.csv",
    )
    eg6 = by_id["EG-006"]
    eg6["evidence_location"] = add_paths(
        eg6["evidence_location"],
        "bom/hr-v0-mechanical-custom-part-binding-p0.2.csv",
        "cad/hr-v0/generated/mechanical-drawing-p0.1/",
        "release/hr-v0/mechanical-bom-binding-p0.2/",
        "release/hr-v0/arm-architecture-p0.8-dwg-integrated/",
        "tests/forms/hr-v0-mechanical-custom-part-fai-template-p0.2.csv",
        "tools/check_hr_v0_arm_architecture_p08.py",
        "requirements/hr-v0-gate-evidence-supplement-r214.csv",
    )
    for gate_id in ("EG-003", "EG-005", "EG-006"):
        by_id[gate_id]["status"] = "partial"
    write_csv(GATES, records)

    supplement = [
        {"gate_id": "EG-003", "round": "R214", "evidence_added": f"{CONFIG}; {MECHANICAL}; HR-V0-MECH-BOM-BIND-P0.2", "maturity": "source-controlled configuration and nominal model-space evidence only", "status_after": "partial", "remaining_evidence": "complete orderable BOM, provider/process acceptance, received evidence, FAI, physical proof and signed configuration release", "warning": WARNING},
        {"gate_id": "EG-005", "round": "R214", "evidence_added": f"{MECHANICAL}; exact five-file import; regenerated collision, continuous-clearance and J2 stop evidence", "maturity": "source-controlled nominal model-space evidence only", "status_after": "partial", "remaining_evidence": "qualified acceptance, received fit, mass/inertia, as-built dimensional survey, structural proof, cables/guards and physical stop/collision validation", "warning": WARNING},
        {"gate_id": "EG-006", "round": "R214", "evidence_added": "HR-V0-MECH-BOM-BIND-P0.2; P0.8 integrated arm; drawing-controlled STEP/DXF/SVG chain and blank FAI operations", "maturity": "source-controlled manufacturing candidate only", "status_after": "partial", "remaining_evidence": "provider DFM, material/MTR, completed FAI, proof tests and qualified drawing/fabrication release", "warning": WARNING},
    ]
    write_csv(ROOT / "requirements/hr-v0-gate-evidence-supplement-r214.csv", supplement)


def replace_support(product: dict[str, object], old: str, new: str) -> None:
    support = list(product.get("supporting_identifiers", []))
    support = [new if item == old else item for item in support]
    if new not in support:
        support.append(new)
    product["supporting_identifiers"] = support


def sync_release() -> None:
    release = json.loads(RELEASE.read_text(encoding="utf-8"))
    products = {row["domain"]: row for row in release["current_products"]}
    for domain in ("electrical", "bill_of_materials", "assembly"):
        replace_support(products[domain], "HR-V0-CONFIG-REC-P0.2", CONFIG)

    mechanical = products["mechanical"]
    mechanical["identifier"] = "HR-V0-MECH-P0.6"
    support = list(mechanical["supporting_identifiers"])
    for item in ("HR-V0-ARM-ARCH-P0.7", MECHANICAL, "HR-V0-MECH-BOM-BIND-P0.2", CONFIG):
        if item not in support:
            support.append(item)
    mechanical["supporting_identifiers"] = support
    mechanical["current_arm_architecture"] = MECHANICAL
    mechanical["inherited_analytical_basis"] = ["HR-V0-MECH-P0.6", "HR-V0-ARM-ARCH-P0.7"]
    mechanical["manufacturing_identity"] = "HR-V0-MECH-BOM-BIND-P0.2"
    mechanical["release_state"] = "integrated_p06_hold_with_exact_p08_complete_arm_p07_inherited_basis_physical_evidence_open_qualified_release_open"

    firmware = products["firmware"]
    firmware["supporting_identifiers"] = [item for item in firmware["supporting_identifiers"] if item not in {"HR-V0-MECH-P0.6", "HR-V0-ARM-ARCH-P0.7"}]
    for item in (MECHANICAL, "HR-V0-MECH-BOM-BIND-P0.2"):
        if item not in firmware["supporting_identifiers"]:
            firmware["supporting_identifiers"].append(item)
    firmware["inherited_kinematic_basis"] = "HR-V0-ARM-ARCH-P0.7"
    firmware["release_state"] = "source_transport_reproducible_fail_closed_integrated_p08_mechanical_identity_with_p07_kinematic_basis_acceptance_hashes_target_hil_and_physical_evidence_unresolved"

    assembly = products["assembly"]
    assembly["supporting_identifiers"] = [MECHANICAL if item == "HR-V0-MECH-P0.6" else item for item in assembly["supporting_identifiers"]]
    if "HR-V0-MECH-BOM-BIND-P0.2" not in assembly["supporting_identifiers"]:
        assembly["supporting_identifiers"].append("HR-V0-MECH-BOM-BIND-P0.2")
    assembly["release_state"] = "integrated_unpowered_sequence_bound_to_held_p08_mechanics_all_steps_not_authorized_not_executed_connection_and_energization_prohibited_not_approved"
    RELEASE.write_text(json.dumps(release, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    sync_gates()
    sync_release()


if __name__ == "__main__":
    main()
