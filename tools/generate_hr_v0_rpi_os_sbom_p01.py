#!/usr/bin/env python3
"""Normalize the publisher-provided Raspberry Pi OS Lite SPDX SBOM.

This does not download or write a disk image, install a package, select a GPIO
backend, or authorize powered work. It creates reviewable package-inventory
evidence from the exact controlled SBOM payload already present in the tree.
"""

from __future__ import annotations

import csv
import hashlib
import json
import lzma
from collections import Counter
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "software/images/hr-v0-rpi-os-lite-sbom-p0.1"
PAYLOAD = OUT / "official/2026-06-18-raspios-trixie-arm64-lite.sbom.xz"
LOCK = OUT / "dpkg-package-lock.csv"
CRITICAL = OUT / "critical-package-register.csv"
SUMMARY = OUT / "sbom-summary.json"
MANIFEST = OUT / "SOURCE-MANIFEST.csv"
EXPECTED_PAYLOAD_SHA256 = "7a82f353f58d925543ed196e56b551342138551132fcb59111917df64c683959"
WARNING = "PRELIMINARY - NOT APPROVED FOR IMAGING INSTALLATION CONNECTION POWERED TEST MOTION OR ENERGIZATION"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def purl_for(package: dict[str, object], prefix: str) -> str:
    for ref in package.get("externalRefs", []):
        if ref.get("referenceType") == "purl" and str(ref.get("referenceLocator", "")).startswith(prefix):
            return str(ref["referenceLocator"])
    return ""


def dpkg_rows(document: dict[str, object]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for package in document["packages"]:
        purl = purl_for(package, "pkg:deb/")
        if not purl:
            continue
        parsed = urlsplit(purl)
        query = parse_qs(parsed.query)
        verification = package.get("packageVerificationCode", {})
        rows.append({
            "name": str(package.get("name", "")),
            "version": str(package.get("versionInfo", "")),
            "architecture": query.get("arch", [""])[0],
            "distro": query.get("distro", [""])[0],
            "upstream": query.get("upstream", [""])[0],
            "purl": unquote(purl),
            "spdx_id": str(package.get("SPDXID", "")),
            "files_analyzed": str(bool(package.get("filesAnalyzed"))).lower(),
            "package_verification_code": str(verification.get("packageVerificationCodeValue", "")),
            "supplier": str(package.get("supplier", "")),
            "source_info": str(package.get("sourceInfo", "")),
            "evidence_state": "PUBLISHER_SBOM_EXTRACT_NOT_TARGET_READBACK",
            "warning": WARNING,
        })
    return sorted(rows, key=lambda row: (row["name"], row["version"], row["architecture"], row["spdx_id"]))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    compressed = PAYLOAD.read_bytes()
    if digest(compressed) != EXPECTED_PAYLOAD_SHA256:
        raise SystemExit("controlled publisher SBOM hash mismatch")
    decompressed = lzma.decompress(compressed)
    document = json.loads(decompressed)
    rows = dpkg_rows(document)
    if len(rows) != 632 or len({(row["name"], row["version"]) for row in rows}) != 632:
        raise SystemExit("publisher DPKG package count or uniqueness changed")
    write_csv(LOCK, rows)

    by_name = {row["name"]: row for row in rows}
    critical_basis = [
        ("python3", "runtime interpreter metapackage", "BASE_IDENTITY_CANDIDATE"),
        ("python3-minimal", "minimal runtime interpreter", "BASE_IDENTITY_CANDIDATE"),
        ("systemd", "service manager", "BASE_IDENTITY_CANDIDATE"),
        ("systemd-sysv", "boot integration", "BASE_IDENTITY_CANDIDATE"),
        ("libgpiod3", "GPIO character-device library", "PRESENT_BACKEND_NOT_SELECTED"),
        ("gpiod", "GPIO command tools", "PRESENT_BACKEND_NOT_SELECTED"),
        ("python3-gpiozero", "Python GPIO abstraction", "PRESENT_BACKEND_NOT_SELECTED"),
        ("python3-lgpio", "Python lgpio backend", "PRESENT_BACKEND_NOT_SELECTED"),
        ("python3-serial", "Python serial transport", "NOT_PRESENT_SELECTION_REQUIRED"),
        ("dynamixel-sdk", "ROBOTIS Python transport", "NOT_PRESENT_SEPARATE_LOCK_REQUIRED"),
        ("openssh-server", "remote access service", "PRESENT_POLICY_REQUIRED"),
        ("raspi-config", "Raspberry Pi configuration tool", "BASE_IDENTITY_CANDIDATE"),
        ("raspberrypi-sys-mods", "Raspberry Pi system integration", "BASE_IDENTITY_CANDIDATE"),
        ("linux-image-rpi-2712", "Raspberry Pi 5 kernel image", "PRESENT_BOOT_READBACK_REQUIRED"),
        ("linux-image-rpi-v8", "alternate Raspberry Pi kernel image", "PRESENT_BOOT_READBACK_REQUIRED"),
    ]
    critical_rows: list[dict[str, str]] = []
    for name, role, state in critical_basis:
        source = by_name.get(name, {})
        critical_rows.append({
            "package": name,
            "role": role,
            "presence_in_publisher_sbom": "PRESENT" if source else "ABSENT",
            "version": source.get("version", "SELECTION REQUIRED"),
            "architecture": source.get("architecture", "SELECTION REQUIRED"),
            "purl": source.get("purl", "SELECTION REQUIRED"),
            "selection_state": state,
            "target_verification": "NOT_EXECUTED",
            "safety_credit": "NONE",
            "warning": WARNING,
        })
    write_csv(CRITICAL, critical_rows)

    purl_types = Counter()
    for package in document["packages"]:
        if purl_for(package, "pkg:deb/"):
            purl_types["deb"] += 1
        elif purl_for(package, "pkg:generic/"):
            purl_types["generic"] += 1
        else:
            purl_types["no_supported_purl"] += 1
    lock_sha256 = digest(LOCK.read_bytes())
    summary = {
        "schema": "project-button-publisher-sbom-lock-v1",
        "identifier": "HR-V0-RPI-OS-SBOM-P0.1",
        "status": "PUBLISHER_SBOM_LOCKED_TARGET_NOT_VERIFIED",
        "parent_image_identifier": "HR-V0-RPI-OS-LITE-P0.1",
        "document_name": document["name"],
        "spdx_version": document["spdxVersion"],
        "document_namespace": document["documentNamespace"],
        "created_utc": document["creationInfo"]["created"],
        "creators": document["creationInfo"]["creators"],
        "compressed_payload_bytes": len(compressed),
        "compressed_payload_sha256": digest(compressed),
        "decompressed_bytes": len(decompressed),
        "decompressed_sha256": digest(decompressed),
        "total_spdx_packages": len(document["packages"]),
        "dpkg_packages": len(rows),
        "generic_packages": purl_types["generic"],
        "packages_without_supported_purl": purl_types["no_supported_purl"],
        "unique_dpkg_name_version_pairs": len({(row["name"], row["version"]) for row in rows}),
        "dpkg_package_lock_sha256": lock_sha256,
        "image_download_state": "NOT_EXECUTED",
        "target_dpkg_readback_state": "NOT_EXECUTED",
        "gpio_backend_selection": "SELECTION REQUIRED",
        "serial_runtime_selection": "SELECTION REQUIRED",
        "motion_authority": "NONE",
        "functional_safety_credit": "NONE",
        "warning": WARNING,
    }
    SUMMARY.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    controlled = [
        path for path in sorted(OUT.rglob("*"))
        if path.is_file() and path != MANIFEST
    ]
    with MANIFEST.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["file", "sha256", "bytes"])
        for path in controlled:
            writer.writerow([
                path.relative_to(OUT).as_posix(),
                digest(path.read_bytes()),
                path.stat().st_size,
            ])
    print(f"HR-V0-RPI-OS-SBOM-P0.1: {len(document['packages'])} SPDX packages / {len(rows)} DPKG identities")
    print(f"DPKG lock SHA-256: {lock_sha256}")
    print(WARNING)


if __name__ == "__main__":
    main()
