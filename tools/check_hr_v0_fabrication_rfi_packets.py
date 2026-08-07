"""Fail-closed validation for deterministic HR-V0 fabrication inquiry packets."""

from __future__ import annotations

import csv
import hashlib
import io
import sys
import zipfile
from pathlib import Path

from generate_hr_v0_fabrication_rfi_packets import (
    CANONICAL_TEXT_SUFFIXES,
    FIXED_ZIP_TIME,
    OUT,
    PACKETS,
    ROOT,
    WARNING,
)


INDEX = OUT / "packet-index.csv"
SURVEY = ROOT / "tests" / "forms" / "hr-v0-boston-bench-survey-template.csv"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def canonical_source_bytes(source: str) -> bytes:
    data = (ROOT / source).read_bytes()
    if Path(source).suffix.lower() in CANONICAL_TEXT_SUFFIXES:
        return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return data


def read_csv_bytes(data: bytes) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(data.decode("utf-8"))))


def main() -> int:
    errors: list[str] = []
    expected_artifacts = {packet.filename for packet in PACKETS} | {"packet-index.csv"}
    actual_artifacts = {path.name for path in OUT.glob("*") if path.is_file()}
    if actual_artifacts != expected_artifacts:
        errors.append(f"packet directory mismatch: {sorted(actual_artifacts)}")

    packet_rows: dict[str, dict[str, str]] = {}
    for packet in PACKETS:
        path = OUT / packet.filename
        expected_names = {"README-FIRST.txt", "MANIFEST.csv"} | {
            f"payload/{source}" for source in packet.inputs
        }
        try:
            with zipfile.ZipFile(path) as archive:
                infos = archive.infolist()
                names = [info.filename for info in infos]
                if set(names) != expected_names or len(names) != len(expected_names):
                    errors.append(f"{packet.packet_id} member set mismatch: {names}")
                for info in infos:
                    if info.date_time != FIXED_ZIP_TIME:
                        errors.append(f"{packet.packet_id} has nondeterministic timestamp: {info.filename}")
                    if info.compress_type != zipfile.ZIP_STORED or info.is_dir():
                        errors.append(f"{packet.packet_id} has unsupported member encoding: {info.filename}")
                    if info.create_system != 3 or ((info.external_attr >> 16) & 0o777) != 0o644:
                        errors.append(f"{packet.packet_id} has nondeterministic member permissions: {info.filename}")
                    if info.filename.startswith(("/", "\\")) or ".." in Path(info.filename).parts:
                        errors.append(f"{packet.packet_id} has unsafe member path: {info.filename}")
                    if info.filename.lower().endswith(".pdf"):
                        errors.append(f"{packet.packet_id} contains prohibited PDF: {info.filename}")
                readme = archive.read("README-FIRST.txt").decode("utf-8")
                for required in (
                    WARNING,
                    "not a purchase order",
                    "Do not fabricate",
                    "Critical finished-hole size and location tolerances remain SELECTION REQUIRED",
                ):
                    if required not in readme:
                        errors.append(f"{packet.packet_id} README omits: {required}")
                manifest_rows = read_csv_bytes(archive.read("MANIFEST.csv"))
                if [row.get("source_repo_path") for row in manifest_rows] != list(packet.inputs):
                    errors.append(f"{packet.packet_id} internal manifest source order changed")
                for row in manifest_rows:
                    source = row.get("source_repo_path", "")
                    packet_path = row.get("packet_path", "")
                    if packet_path != f"payload/{source}" or packet_path not in expected_names:
                        errors.append(f"{packet.packet_id} invalid manifest mapping: {source}")
                        continue
                    source_data = canonical_source_bytes(source)
                    packet_data = archive.read(packet_path)
                    if packet_data != source_data:
                        errors.append(f"{packet.packet_id} payload differs from repository source: {source}")
                    if row.get("sha256") != sha256_bytes(source_data) or row.get("size_bytes") != str(len(source_data)):
                        errors.append(f"{packet.packet_id} manifest hash/size mismatch: {source}")
                    if row.get("role") != "CAPABILITY/DFM INPUT - NOT FABRICATION RELEASE":
                        errors.append(f"{packet.packet_id} manifest role changed: {source}")
        except (FileNotFoundError, KeyError, zipfile.BadZipFile, UnicodeDecodeError) as exc:
            errors.append(f"{packet.packet_id} unreadable packet: {exc}")
            continue
        packet_rows[packet.packet_id] = {
            "sha256": sha256_bytes(path.read_bytes()),
            "size_bytes": str(path.stat().st_size),
            "payload_file_count": str(len(packet.inputs)),
            "artifact": path.relative_to(ROOT).as_posix(),
        }

    one_stop_names = set(PACKETS[0].inputs)
    if any("PROFILE_ONLY_RFQ" in name or name.lower().endswith(".dxf") for name in one_stop_names):
        errors.append("RFI-001 must contain finished STEP plus drawings only")
    profile_names = set(PACKETS[1].inputs)
    if any("generated/parts/" in name or "generated/drawings/" in name for name in profile_names):
        errors.append("RFI-002 profile packet contains finished geometry or drawings")
    if not all("manufacturing-blanks/" in name for name in profile_names):
        errors.append("RFI-002 contains a source outside the controlled blank directory")
    secondary_names = set(PACKETS[2].inputs)
    if not one_stop_names.issubset(secondary_names) or not profile_names.issubset(secondary_names):
        errors.append("RFI-003 secondary-operation packet lacks blank and finished context")
    if any("MV0-004" in name for packet in PACKETS for name in packet.inputs):
        errors.append("site-held MV0-004 appears in an inquiry packet")

    try:
        with INDEX.open(newline="", encoding="utf-8") as handle:
            index_rows = list(csv.DictReader(handle))
    except FileNotFoundError as exc:
        errors.append(f"packet index missing: {exc}")
        index_rows = []
    expected_ids = {f"RFI-{index:03d}" for index in range(1, 7)}
    by_id = {row.get("packet_id"): row for row in index_rows}
    if set(by_id) != expected_ids or len(index_rows) != 6:
        errors.append(f"packet index expected RFI-001 through RFI-006, found {sorted(by_id)}")
    for packet in PACKETS:
        row = by_id.get(packet.packet_id, {})
        for field, expected in packet_rows.get(packet.packet_id, {}).items():
            if row.get(field) != expected:
                errors.append(f"{packet.packet_id} index {field} mismatch")
        if row.get("state") != "PRELIMINARY - INQUIRY ONLY":
            errors.append(f"{packet.packet_id} falsely appears released")
        if "No procurement" not in row.get("forbidden_action", ""):
            errors.append(f"{packet.packet_id} index lost procurement prohibition")
    holds = {
        "RFI-004": ("NOT GENERATED", "PROTOTYPING ONLY"),
        "RFI-005": ("NOT GENERATED", "EXCLUDED FROM STRUCTURAL METAL ROUTE"),
        "RFI-006": ("NOT GENERATED - SITE HOLD", "SITE HOLD"),
    }
    for packet_id, (artifact, state) in holds.items():
        row = by_id.get(packet_id, {})
        if row.get("artifact") != artifact or row.get("state") != state or row.get("payload_file_count") != "0":
            errors.append(f"{packet_id} hold/exclusion record changed")

    try:
        with SURVEY.open(newline="", encoding="utf-8") as handle:
            survey_rows = list(csv.DictReader(handle))
        if len(survey_rows) != 1 or survey_rows[0].get("record_id") != "NOT-EXECUTED":
            errors.append("Boston bench-survey template contains executed-looking records")
        if "NOT EXECUTED" not in survey_rows[0].get("status", ""):
            errors.append("Boston bench-survey status lost its unexecuted hold")
        for required_field in (
            "permission_reference",
            "bench_top_material",
            "bench_top_thickness_mm",
            "underbench_access",
            "drilling_permitted",
            "through_bolting_permitted",
            "candidate_anchor_type",
            "design_shear_load_n",
            "design_tension_load_n",
            "proof_load_and_duration",
            "facility_approval",
            "mechanical_reviewer",
        ):
            if required_field not in survey_rows[0]:
                errors.append(f"Boston bench-survey template omits {required_field}")
    except (FileNotFoundError, IndexError) as exc:
        errors.append(f"Boston bench-survey template missing or empty: {exc}")

    if errors:
        print("HR-V0 fabrication inquiry packet check FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"HR-V0 fabrication inquiry packet check passed: 3 deterministic packets; {sum(len(packet.inputs) for packet in PACKETS)} controlled payload entries")
    print("FAB-005 remains prototyping-only; FAB-006 excluded; FAB-007 site-held")
    print(WARNING)
    return 0


if __name__ == "__main__":
    sys.exit(main())
