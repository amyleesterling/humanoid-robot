#!/usr/bin/env python3
"""Validate HR-V0-RPI-OS-SBOM-P0.1 without installing or booting it."""

from __future__ import annotations

import csv
import hashlib
import json
import lzma
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "software/images/hr-v0-rpi-os-lite-sbom-p0.1"
PAYLOAD = OUT / "official/2026-06-18-raspios-trixie-arm64-lite.sbom.xz"
IDENTIFIER = "HR-V0-RPI-OS-SBOM-P0.1"
PAYLOAD_SHA256 = "7a82f353f58d925543ed196e56b551342138551132fcb59111917df64c683959"
LOCK_SHA256 = "8146766fb15bc3a5cbceaed00ef53cc5aa0af2d9a085762df6a34a23f9174e02"
WARNING = "PRELIMINARY - NOT APPROVED FOR IMAGING INSTALLATION CONNECTION POWERED TEST MOTION OR ENERGIZATION"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    compressed = PAYLOAD.read_bytes()
    decompressed = lzma.decompress(compressed)
    document = json.loads(decompressed)
    lock_path = OUT / "dpkg-package-lock.csv"
    lock = rows(lock_path)
    critical = rows(OUT / "critical-package-register.csv")
    sources = rows(OUT / "source-register.csv")
    manifest = rows(OUT / "SOURCE-MANIFEST.csv")
    summary = json.loads((OUT / "sbom-summary.json").read_text(encoding="utf-8"))
    image = json.loads((ROOT / "software/images/hr-v0-rpi-os-lite-p0.1.json").read_text(encoding="utf-8"))
    target = rows(ROOT / "tests/forms/hr-v0-rpi-os-sbom-target-verification-template-p0.1.csv")
    supplement = rows(ROOT / "requirements/hr-v0-gate-evidence-supplement-r172.csv")
    gates = {row["gate_id"]: row for row in rows(ROOT / "requirements/hr-v0-energization-gates.csv")}
    metadata = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))
    doc = (ROOT / "docs/hr-v0-rpi-os-sbom-p0.1.md").read_text(encoding="utf-8")
    guide = (ROOT / "release/hr-v0/rpi-os-sbom-p0.1/index.html").read_text(encoding="utf-8")

    require(len(compressed) == 5336108 and digest(compressed) == PAYLOAD_SHA256, "publisher SBOM payload identity changed")
    require(len(decompressed) == 50522646 and digest(decompressed) == "ff04dbd1ffb6742bec8778a8c455b7f20ed84f218b0c140fcf786e0a29ad27c0", "decompressed SBOM identity changed")
    require(document.get("spdxVersion") == "SPDX-2.3" and document.get("name") == "raspios-trixie-arm64-lite", "SPDX document identity changed")
    creation = document.get("creationInfo", {})
    require(creation.get("created") == "2026-06-18T00:27:22Z" and "Tool: syft-1.45.1" in creation.get("creators", []), "SBOM creation identity changed")
    require(len(document.get("packages", [])) == 4743, "total SPDX package count changed")
    require(len(lock) == 632 and len({(row["name"], row["version"]) for row in lock}) == 632, "DPKG lock count or uniqueness changed")
    require(digest(lock_path.read_bytes()) == LOCK_SHA256, "normalized DPKG lock hash changed")
    require(all(row["evidence_state"] == "PUBLISHER_SBOM_EXTRACT_NOT_TARGET_READBACK" and row["warning"] == WARNING for row in lock), "DPKG lock evidence boundary changed")

    require(summary.get("identifier") == IDENTIFIER and summary.get("status") == "PUBLISHER_SBOM_LOCKED_TARGET_NOT_VERIFIED", "summary identity/state changed")
    for key, expected in (("total_spdx_packages", 4743), ("dpkg_packages", 632), ("generic_packages", 3791), ("packages_without_supported_purl", 320)):
        require(summary.get(key) == expected, f"summary count changed: {key}")
    require(summary.get("dpkg_package_lock_sha256") == LOCK_SHA256, "summary lock hash changed")
    require(summary.get("image_download_state") == "NOT_EXECUTED" and summary.get("target_dpkg_readback_state") == "NOT_EXECUTED", "summary improperly claims image/target execution")
    require(summary.get("functional_safety_credit") == "NONE" and summary.get("motion_authority") == "NONE", "summary claims authority or safety credit")

    require(len(critical) == 15, "critical-package register must contain fifteen rows")
    by_name = {row["package"]: row for row in critical}
    expected_versions = {
        "python3": "3.13.5-1",
        "systemd": "257.13-1~deb13u1",
        "libgpiod3": "2.2.1-2+deb13u1",
        "python3-gpiozero": "2.0.1-0+rpt1+trixie",
        "python3-lgpio": "0.2.2-1~rpt1+trixie",
        "openssh-server": "1:10.0p1-7+deb13u4",
        "linux-image-rpi-2712": "1:6.18.34-1+rpt1",
    }
    for package, version in expected_versions.items():
        require(by_name.get(package, {}).get("version") == version, f"critical package version changed: {package}")
    for package in ("python3-serial", "dynamixel-sdk"):
        require(by_name.get(package, {}).get("presence_in_publisher_sbom") == "ABSENT" and by_name.get(package, {}).get("version") == "SELECTION REQUIRED", f"absent-package boundary changed: {package}")
    require(all(row["target_verification"] == "NOT_EXECUTED" and row["safety_credit"] == "NONE" and row["warning"] == WARNING for row in critical), "critical package target/safety boundary changed")

    require(len(sources) == 2 and sources[1]["source_id"] == "RPI172-SRC-002" and PAYLOAD_SHA256 in sources[1]["controlled_fact"], "source register changed")
    controlled = {
        path.relative_to(OUT).as_posix(): (digest(path.read_bytes()), str(path.stat().st_size))
        for path in sorted(OUT.rglob("*")) if path.is_file() and path.name != "SOURCE-MANIFEST.csv"
    }
    recorded = {row["file"]: (row["sha256"], row["bytes"]) for row in manifest}
    require(recorded == controlled, "SBOM SOURCE-MANIFEST.csv is stale or incomplete")

    require(image.get("official_sbom_download_state") == "EXECUTED_READ_ONLY_NO_DISK_IMAGE_OR_MEDIA_WRITE", "image record lacks read-only SBOM acquisition")
    require(image.get("official_sbom_local_sha256") == PAYLOAD_SHA256 and image.get("official_sbom_dpkg_lock_sha256") == LOCK_SHA256, "image record SBOM/lock hashes changed")
    require(image.get("local_download_state") == "NOT_EXECUTED" and image.get("media_write_state") == "NOT_EXECUTED" and image.get("boot_validation_state") == "NOT_EXECUTED", "image record improperly claims disk-image/media/boot execution")
    require(image.get("package_manifest_state") == "PUBLISHER_SBOM_LOCKED_TARGET_DPKG_READBACK_NOT_EXECUTED", "image package-manifest state changed")

    require(len(target) == 12 and all(row["authorization"] == "NOT_AUTHORIZED" and row["state"] == "NOT_EXECUTED" and not row["actual_result"] and not row["evidence_hash"] for row in target), "target verification form contains execution or authority")
    require(len(supplement) == 3 and {row["gate_id"] for row in supplement} == {"EG-002", "EG-017", "EG-022"}, "R172 gate supplement changed")
    require(all(row["disposition"] == "REMAINS PARTIAL" for row in supplement), "R172 improperly advances a gate")
    require(all(gates.get(gate, {}).get("status") == "partial" for gate in ("EG-002", "EG-017", "EG-022")), "R172-related gate was improperly closed")

    firmware = next((item for item in metadata.get("current_products", []) if item.get("domain") == "firmware"), {})
    require(IDENTIFIER in firmware.get("supporting_identifiers", []), "release metadata lacks R172 identifier")
    combined = doc + guide
    for token in (IDENTIFIER, "4,743", "632", LOCK_SHA256, "python3-serial", "zero functional-safety credit", "not approved"):
        require(token.lower() in combined.lower(), f"document/guide boundary missing: {token}")
    require("font:16px" in guide and "font-size:16px" in guide and "font-size:14px" in guide, "guide text floors are not explicit")
    require(guide.count("data-filter=") == 4 and guide.count("data-kind=") == 4, "guide filter/card structure changed")

    if failures:
        raise SystemExit("HR-V0 Raspberry Pi OS SBOM P0.1 check failed:\n- " + "\n- ".join(failures))
    print("HR-V0 Raspberry Pi OS SBOM P0.1 check passed: 5,336,108-byte publisher payload, 4,743 SPDX records, 632 exact DPKG identities, 15 critical rows, 12 unexecuted target checks")
    print("Disk image, media write/readback, target dpkg inventory, backend selection, boot, HIL and energization remain NOT EXECUTED / NOT AUTHORIZED")
    print(WARNING)


if __name__ == "__main__":
    main()
