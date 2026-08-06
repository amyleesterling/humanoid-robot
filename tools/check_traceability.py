from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


requirements = rows(ROOT / "requirements" / "requirements.csv")
risks = rows(ROOT / "safety" / "risk-register.csv")
requirement_ids = {row["id"] for row in requirements}
errors: list[str] = []

if len(requirement_ids) != len(requirements):
    errors.append("requirements.csv contains duplicate requirement IDs")
if len({row["risk_id"] for row in risks}) != len(risks):
    errors.append("risk-register.csv contains duplicate risk IDs")

for row in requirements:
    if not row["verification_id"].strip():
        errors.append(f'{row["id"]}: missing verification_id')
    if row["priority"] == "MUST" and row["status"] not in {"draft", "approved", "passed"}:
        errors.append(f'{row["id"]}: invalid MUST status {row["status"]!r}')

for risk in risks:
    linked = {value.strip() for value in risk["linked_requirements"].split(";") if value.strip()}
    unknown = linked - requirement_ids
    if not linked:
        errors.append(f'{risk["risk_id"]}: no linked requirements')
    if unknown:
        errors.append(f'{risk["risk_id"]}: unknown requirements {sorted(unknown)}')

if errors:
    raise SystemExit("Traceability check failed:\n- " + "\n- ".join(errors))

print(
    f"Traceability OK: {len(requirements)} requirements, "
    f"{len(risks)} risks, all links valid."
)
