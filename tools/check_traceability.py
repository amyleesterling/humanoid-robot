from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROCEDURE_REGISTRY = ROOT / "tests" / "procedures" / "procedure-registry.csv"
TRACEABILITY_DOCS = (
    ROOT / "docs" / "verification.md",
    ROOT / "docs" / "walking-verification.md",
    *(ROOT / "docs" / "releases").glob("*.md"),
)

PROCEDURE_COLUMNS = {
    "verification_id",
    "linked_requirement_ids",
    "verification_type",
    "objective_method",
    "required_instrumentation",
    "acceptance_criteria",
    "evidence_required",
    "status",
    "selection_required",
    "notes",
}
PROCEDURE_ID_RE = re.compile(
    r"\b(?:TEST|INSPECT|AUDIT|ANALYSIS|DEMO|REVIEW)-[A-Z0-9]+(?:-[A-Z0-9]+)*\b"
)
PROCEDURE_RANGE_RE = re.compile(
    r"\b((?:TEST|INSPECT|AUDIT|ANALYSIS|DEMO|REVIEW)-[A-Z0-9]+(?:-[A-Z0-9]+)*)"
    r"-(\d{3})\s+(?:through|to)\s+\1-(\d{3})\b"
)
VALID_PROCEDURE_TYPES = {"test", "inspection", "audit", "analysis", "demonstration", "review"}
VALID_PROCEDURE_STATUSES = {
    "draft",
    "selection_required",
    "planned",
    "approved",
    "passed",
    "failed",
    "blocked",
    "retired",
}


def table(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def linked_ids(value: str) -> set[str]:
    return {item.strip() for item in value.split(";") if item.strip()}


def procedure_ids_in(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    found = set(PROCEDURE_ID_RE.findall(text))
    for prefix, first_text, last_text in PROCEDURE_RANGE_RE.findall(text):
        first = int(first_text)
        last = int(last_text)
        if last < first or last - first > 100:
            continue
        found.update(f"{prefix}-{number:03d}" for number in range(first, last + 1))
    return found


requirements, _ = table(ROOT / "requirements" / "requirements.csv")
risks, _ = table(ROOT / "safety" / "risk-register.csv")
procedures, procedure_headers = table(PROCEDURE_REGISTRY)
requirement_ids = {row["id"] for row in requirements}
procedure_ids = {row["verification_id"] for row in procedures}
errors: list[str] = []

missing_columns = PROCEDURE_COLUMNS - set(procedure_headers)
if missing_columns:
    errors.append(f"procedure-registry.csv: missing columns {sorted(missing_columns)}")

if len(requirement_ids) != len(requirements):
    errors.append("requirements.csv contains duplicate requirement IDs")
if len({row["risk_id"] for row in risks}) != len(risks):
    errors.append("risk-register.csv contains duplicate risk IDs")
if len(procedure_ids) != len(procedures):
    errors.append("procedure-registry.csv contains duplicate verification IDs")

for row in requirements:
    verification_id = row["verification_id"].strip()
    if not verification_id:
        errors.append(f'{row["id"]}: missing verification_id')
    elif verification_id not in procedure_ids:
        errors.append(f'{row["id"]}: unresolved verification_id {verification_id!r}')
    if row["priority"] == "MUST" and row["status"] not in {"draft", "approved", "passed"}:
        errors.append(f'{row["id"]}: invalid MUST status {row["status"]!r}')

for risk in risks:
    linked = linked_ids(risk["linked_requirements"])
    unknown = linked - requirement_ids
    if not linked:
        errors.append(f'{risk["risk_id"]}: no linked requirements')
    if unknown:
        errors.append(f'{risk["risk_id"]}: unknown requirements {sorted(unknown)}')

for row_number, procedure in enumerate(procedures, start=2):
    verification_id = procedure["verification_id"].strip()
    required_values = {
        column: procedure[column].strip()
        for column in PROCEDURE_COLUMNS - {"notes"}
        if column in procedure
    }
    blank = sorted(column for column, value in required_values.items() if not value)
    if blank:
        errors.append(f"procedure-registry.csv:{row_number}: blank fields {blank}")

    unknown = linked_ids(procedure["linked_requirement_ids"]) - requirement_ids
    if unknown:
        errors.append(f"{verification_id}: unknown linked requirements {sorted(unknown)}")

    verification_type = procedure["verification_type"].strip()
    if verification_type not in VALID_PROCEDURE_TYPES:
        errors.append(f"{verification_id}: invalid verification_type {verification_type!r}")

    status = procedure["status"].strip()
    if status not in VALID_PROCEDURE_STATUSES:
        errors.append(f"{verification_id}: invalid status {status!r}")

    selection_required = procedure["selection_required"].strip().lower()
    if selection_required not in {"yes", "no"}:
        errors.append(f"{verification_id}: selection_required must be 'yes' or 'no'")
    combined_text = " ".join(procedure.values())
    if "SELECTION REQUIRED" in combined_text and selection_required != "yes":
        errors.append(f"{verification_id}: contains SELECTION REQUIRED but is not flagged")
    if status == "selection_required" and selection_required != "yes":
        errors.append(f"{verification_id}: selection_required status is not flagged")
    if status in {"approved", "passed"} and selection_required == "yes":
        errors.append(f"{verification_id}: unresolved selection cannot be {status}")

document_references: dict[Path, set[str]] = {}
for path in TRACEABILITY_DOCS:
    if not path.is_file():
        errors.append(f"traceability document missing: {path.relative_to(ROOT)}")
        continue
    references = procedure_ids_in(path)
    document_references[path] = references
    unresolved = references - procedure_ids
    if unresolved:
        errors.append(f"{path.relative_to(ROOT)}: unresolved procedure IDs {sorted(unresolved)}")

if errors:
    raise SystemExit("Traceability check failed:\n- " + "\n- ".join(errors))

document_reference_count = sum(len(values) for values in document_references.values())
print(
    f"Traceability OK: {len(requirements)} requirements, {len(risks)} risks, "
    f"{len(procedures)} procedures, and {document_reference_count} release/walking-document "
    "procedure references resolve."
)
