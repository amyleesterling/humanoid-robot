from __future__ import annotations

import csv
import hashlib
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "release" / "hr-v0" / "HR-V0-RC-P0.1-file-manifest.csv"
MANIFEST_REL = MANIFEST.relative_to(ROOT).as_posix()
FIELDS = ("path", "role", "sha256", "size_bytes")


def package_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    paths = [item.decode("utf-8") for item in result.stdout.split(b"\0") if item]
    return sorted(path for path in paths if path != MANIFEST_REL)


def role_for(path: str) -> str:
    if path.startswith("docs/reviews/"):
        return "review_history"
    if path.startswith("docs/releases/"):
        return "staged_release_specification"
    if path.startswith("docs/vendor-queries/"):
        return "vendor_query"
    if path.startswith("docs/") or path == "README.md":
        return "controlled_engineering_document"
    if path.startswith("requirements/"):
        return "requirement_and_gate_control"
    if path.startswith("safety/"):
        return "risk_and_safety_control"
    if path.startswith("bom/"):
        return "bill_of_materials_control"
    if path.startswith("tests/"):
        return "verification_procedure_or_form"
    if path.startswith("references/") or "/vendor/" in path:
        return "primary_or_vendor_reference"
    if path.startswith("cad/"):
        return "mechanical_source_or_generated_candidate"
    if path.startswith("electrical/"):
        return "electrical_source_or_validation_candidate"
    if path.startswith("firmware/"):
        return "firmware_source_build_or_test_evidence"
    if path.startswith("tools/"):
        return "reproduction_and_validation_tool"
    if path.startswith("release/"):
        return "release_configuration_control"
    return "repository_configuration"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    rows: list[dict[str, str | int]] = []
    for relative in package_files():
        path = ROOT / relative
        if not path.is_file():
            raise SystemExit(f"Package path is not a regular file: {relative}")
        rows.append(
            {
                "path": relative,
                "role": role_for(relative),
                "sha256": sha256(path),
                "size_bytes": path.stat().st_size,
            }
        )

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {MANIFEST_REL}: {len(rows)} package files")
    print("PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION")


if __name__ == "__main__":
    main()
