# HR-V0 Raspberry Pi OS publisher-SBOM lock P0.1

> **PRELIMINARY - NOT APPROVED FOR IMAGING, INSTALLATION, CONNECTION, POWERED TEST, MOTION, OR ENERGIZATION.**

Identifier: `HR-V0-RPI-OS-SBOM-P0.1`

Review round: R172

Date: 2026-08-09 America/New_York / 2026-08-10 UTC

Parent: `HR-V0-RPI-OS-LITE-P0.1`

## Result

R172 retrieves and controls Raspberry Pi's versioned SPDX SBOM for the already-pinned 18 June 2026 Raspberry Pi OS Lite 64-bit release. It does **not** download the 501 MB disk image, write media, install packages, boot a Raspberry Pi or authorize work.

The official compressed SBOM is 5,336,108 bytes with locally reproduced SHA-256 `7a82f353f58d925543ed196e56b551342138551132fcb59111917df64c683959`. Its SPDX 2.3 document was created at `2026-06-18T00:27:22Z` by Anchore Syft 1.45.1. The decompressed JSON is 50,522,646 bytes with SHA-256 `ff04dbd1ffb6742bec8778a8c455b7f20ed84f218b0c140fcf786e0a29ad27c0`.

The normalized inventory contains:

- 4,743 total SPDX package records;
- 632 unique DPKG name/version identities;
- 3,791 generic package records, predominantly kernel modules; and
- 320 records without a supported DPKG or generic purl.

The 632-row normalized lock hashes to `8146766fb15bc3a5cbceaed00ef53cc5aa0af2d9a085762df6a34a23f9174e02`.

## Critical base identities

The publisher SBOM reports these exact candidates:

| Role | Package | Publisher-SBOM version | R172 boundary |
|---|---|---|---|
| Python runtime | `python3` | `3.13.5-1` | target executable path/hash unverified |
| service manager | `systemd` | `257.13-1~deb13u1` | target unit compatibility unverified |
| Pi 5 kernel | `linux-image-rpi-2712` | `1:6.18.34-1+rpt1` | selected booted kernel unverified |
| GPIO library | `libgpiod3` | `2.2.1-2+deb13u1` | present, backend not selected |
| GPIO abstraction | `python3-gpiozero` | `2.0.1-0+rpt1+trixie` | present, backend not selected |
| GPIO backend | `python3-lgpio` | `0.2.2-1~rpt1+trixie` | present, backend not selected |
| remote access | `openssh-server` | `1:10.0p1-7+deb13u4` | explicit security policy required |

`python3-serial` and a package named `dynamixel-sdk` are absent from the publisher DPKG inventory. This does not prove that their functionality is absent by every mechanism; it proves only that no such DPKG package identity appears in this SBOM. Their exact source, version, hash, installation and target behavior remain `SELECTION REQUIRED`.

## What this closes—and what it does not

R172 replaces the undifferentiated `package_manifest_state: SELECTION_REQUIRED` with a publisher-SBOM lock. It provides an exact, reproducible base-inventory comparison source for a later isolated target boot.

It does not prove:

- the disk image was downloaded or matches the published image hash;
- the received card was written or read back correctly;
- the running target matches the publisher SBOM;
- package installation state, conffiles, executable bytes, repositories or later updates;
- which kernel a Pi 5 actually boots;
- GPIO or serial timing, permissions, device identity or no-backfeed behavior;
- security hardening, vulnerability disposition, power-loss recovery or rollback; or
- any functional-safety property.

The SBOM, compute, heartbeat and supervisor retain **zero functional-safety credit**. `EG-002`, `EG-017` and `EG-022` remain partial.

## Controlled artifacts

- `software/images/hr-v0-rpi-os-lite-sbom-p0.1/official/2026-06-18-raspios-trixie-arm64-lite.sbom.xz`
- `software/images/hr-v0-rpi-os-lite-sbom-p0.1/dpkg-package-lock.csv`
- `software/images/hr-v0-rpi-os-lite-sbom-p0.1/critical-package-register.csv`
- `software/images/hr-v0-rpi-os-lite-sbom-p0.1/sbom-summary.json`
- `software/images/hr-v0-rpi-os-lite-sbom-p0.1/source-register.csv`
- `software/images/hr-v0-rpi-os-lite-sbom-p0.1/SOURCE-MANIFEST.csv`
- `tests/forms/hr-v0-rpi-os-sbom-target-verification-template-p0.1.csv`
- `release/hr-v0/rpi-os-sbom-p0.1/index.html`
- `tools/generate_hr_v0_rpi_os_sbom_p01.py`
- `tools/check_hr_v0_rpi_os_sbom_p01.py`
