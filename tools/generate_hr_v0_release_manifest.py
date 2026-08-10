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
    return sorted(path for path in index_entries() if path != MANIFEST_REL)


def index_entries() -> dict[str, str]:
    result = subprocess.run(
        ["git", "ls-files", "--stage", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    entries: dict[str, str] = {}
    for record in result.stdout.split(b"\0"):
        if not record:
            continue
        metadata, raw_path = record.split(b"\t", 1)
        _mode, object_id, stage = metadata.decode("ascii").split()
        if stage != "0":
            raise SystemExit(f"Unmerged index entry is not allowed: {raw_path.decode('utf-8')}")
        entries[raw_path.decode("utf-8")] = object_id
    return entries


def untracked_package_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return sorted(
        item.decode("utf-8")
        for item in result.stdout.split(b"\0")
        if item and item.decode("utf-8") != MANIFEST_REL
    )


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
    if path.startswith("test-equipment/"):
        return "test_instrumentation_candidate"
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


def index_blobs(paths: list[str]) -> dict[str, bytes]:
    entries = index_entries()
    missing = sorted(set(paths) - set(entries))
    if missing:
        raise SystemExit(f"Paths are missing from the Git index: {missing}")

    query = b"".join(entries[path].encode("ascii") + b"\n" for path in paths)
    result = subprocess.run(
        ["git", "cat-file", "--batch"],
        cwd=ROOT,
        input=query,
        check=True,
        capture_output=True,
    )

    blobs: dict[str, bytes] = {}
    position = 0
    for path in paths:
        header_end = result.stdout.find(b"\n", position)
        if header_end < 0:
            raise SystemExit(f"Missing git cat-file header for {path}")
        header = result.stdout[position:header_end].decode("ascii").split()
        if len(header) != 3 or header[1] != "blob":
            raise SystemExit(f"Unexpected git cat-file response for {path}: {header}")
        if header[0] != entries[path]:
            raise SystemExit(f"Git blob identity mismatch for {path}")
        size = int(header[2])
        content_start = header_end + 1
        content_end = content_start + size
        content = result.stdout[content_start:content_end]
        delimiter = result.stdout[content_end:content_end + 1]
        if len(content) != size or delimiter != b"\n":
            raise SystemExit(f"Truncated git blob response for {path}")
        blobs[path] = content
        position = content_end + 1

    if position != len(result.stdout):
        raise SystemExit("Unexpected trailing data from git cat-file")
    return blobs


def main() -> None:
    untracked = untracked_package_files()
    if untracked:
        raise SystemExit(
            "Stage every candidate package file before generating the manifest; "
            f"untracked files remain: {untracked}"
        )

    rows: list[dict[str, str | int]] = []
    paths = package_files()
    blobs = index_blobs(paths)
    for relative in paths:
        content = blobs[relative]
        rows.append(
            {
                "path": relative,
                "role": role_for(relative),
                "sha256": hashlib.sha256(content).hexdigest(),
                "size_bytes": len(content),
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
