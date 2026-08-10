# HR-V0 compute storage candidate P0.2

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, INSTALLATION, IMAGING, CONNECTION, POWERED TEST, OR ENERGIZATION**

Identifier: `HR-V0-COMPUTE-STORAGE-P0.2`

Review round: R170

Date: 2026-08-09

## Decision

R170 supersedes only the unresolved `STORE1` product branch in `HR-V0-COMPUTE-SUBASM-P0.1`. It freezes one exact candidate on hold:

- Manufacturer: Kingston Technology
- Part number: `SDCIT2/64GBSP`
- Description: Industrial microSD Memory Card, 64 GB, card only
- Quantity: one candidate unit
- Published interface: microSDXC, UHS-I, 3.3 V
- Published performance classes: Class 10, U3, V30, A1

Kingston's current datasheet lists pSLC-mode TLC, 30K program/erase cycles, bad-block management, a strong ECC engine, power-failure protection, wear levelling, data-refresh features and health monitoring for the family. The same document publishes an "up to 3840 TBW" family figure derived from the highest capacity. R170 deliberately does **not** assign that TBW value to the 64 GB part.

The Raspberry Pi 5 has a microSD slot and SDR104 host capability. Raspberry Pi's current boot-media documentation says Raspberry Pi OS Lite needs at least 8 GB and accepts cards below 2 TB. Those facts make the 64 GB microSDXC candidate dimensionally and capacity plausible; they do not prove negotiated performance, boot reliability, current, temperature, retention or power-loss behavior for this exact card and board.

## Why the earlier branch changed

The prior Raspberry Pi-branded 64 GB branch had useful Pi-specific performance data but no unambiguous public order code and no published endurance or power-failure feature in the controlled record. `SDCIT2/64GBSP` supplies an exact manufacturer part number and stronger storage-risk evidence. It remains an exact-candidate hold because catalog features are not Project Button validation.

## Fail-closed boundaries

- No purchase or supplier is authorized.
- No card has been received, inserted, formatted or written.
- No operating-system image has been downloaded or hash-verified locally.
- No card-specific TBW value is claimed.
- "Power-failure protection" is a manufacturer feature statement, not proof that the Project Button filesystem survives arbitrary interruption.
- `STORE1` and the Raspberry Pi heartbeat retain zero functional-safety credit.
- Motion outputs must remain inactive through boot, corruption, recovery, update and rollback, but that behavior is not yet demonstrated.

Twelve holds cover seller/identity evidence, destructive capacity checking, host compatibility, endurance allocation, controlled imaging, filesystem policy, abrupt-loss testing, health monitoring, retention/service/ESD, backup/rollback, current/thermal characterization and qualified review.

## Controlled artifacts

- `electrical/vendor/kingston/storage-r170/source-manifest-p0.1.csv`
- `bom/hr-v0-compute-storage-p0.2.csv`
- `electrical/interfaces/hr-v0-compute-storage-p0.2.csv`
- `electrical/interfaces/hr-v0-compute-storage-holds-p0.2.csv`
- `tests/forms/hr-v0-compute-storage-receiving-template-p0.2.csv`
- `release/hr-v0/compute-storage-p0.2/index.html`
- `tools/check_hr_v0_compute_storage_p02.py`

Passing digital checks proves source and register consistency only. `EG-002`, `EG-003`, `EG-005`, `EG-010`, `EG-017`, `EG-021`, `EG-022` and `EG-027` remain unresolved.
