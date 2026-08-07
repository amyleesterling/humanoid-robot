# HR-V0 release-candidate configuration P0.1

Status: **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Candidate identifier: `HR-V0-RC-P0.1`

System baseline: `HR-30-SYS-R0.2`

## Purpose

This package makes the current HR-V0 review configuration reproducible. It does not convert proposed parts into selected parts, close physical evidence, or authorize a build. The exact Git commit containing `release/hr-v0/release-candidate.json` and its verified file manifest identifies the candidate reviewed at that commit.

The manifest covers every Git-tracked or non-ignored candidate file except the manifest itself. That exception prevents a recursive self-hash. The manifest includes its own metadata, generator, checker, engineering sources, generated candidates, BOMs, requirements, risks, procedures, primary/vendor references, review history and configuration files.

The manifest hashes Git's canonical staged blobs, not platform-dependent checkout bytes. Repository text also uses controlled LF checkout through `.gitattributes`, with explicit binary and firmware-HEX exceptions. Clean-worktree enforcement then proves that the checkout corresponds to the committed candidate without making SHA-256 evidence depend on a reviewer's platform defaults.

## Current product set

| Domain | Current candidate | Release boundary |
|---|---|---|
| Systems | `HR-30-SYS-R0.2` | integrated preliminary baseline |
| Electrical | `Project Button Electrical V3-P1.4` | connected correction candidate; not a released schematic |
| Watchdog PCB | `PCB-P0.5` | routed/test-access candidate; no fabrication outputs |
| Actuator star PCB | `DXL-STAR-P0.1` | routed candidate; no fabrication outputs |
| Mechanical | `HR-V0-MECH-R0.1-PRELIMINARY` | RFQ/first-article geometry only |
| Plate manufacturing | `HR-V0-PLATE-RFQ-P0.1` | quotation and DFM control only |
| Firmware | `HR-V0-FW-P0.1` / `HR-V0-WD-BUILD-P0.2` | source and reproducible artifacts; not flashed or HIL validated |
| Functional safety | `HR-V0-FSA-P0.1` | allocation candidate; `DF-01` has zero safety credit; no PLr/SIL assigned |

Electrical V2.1 remains preserved as a reviewed historical baseline. It does not override V3's HR-V0 correction intent. HR-30A/B/C/D/W remain later program stages and are not released by this HR-V0 candidate.

## Generate and verify

From the repository root with Python 3, first stage every deliberate candidate change except the generated manifest. Generation fails if any non-ignored package file remains untracked. Then run:

```powershell
python tools/generate_hr_v0_release_manifest.py
git add release/hr-v0/HR-V0-RC-P0.1-file-manifest.csv
python tools/check_hr_v0_release_manifest.py
```

After committing all candidate files, a clean clone must pass:

```powershell
python tools/check_hr_v0_release_manifest.py --require-clean
```

Any content change, added package file, deleted package file, role change, size change, or hash change invalidates the manifest until it is deliberately regenerated and reviewed.

## Why EG-002 remains partial

The deterministic file set closes the earlier ambiguity about which artifacts travel together. It cannot itself prove acceptance. `EG-002` remains partial until:

1. the candidate commit is merged or otherwise immutably accepted by the configuration manager;
2. the exact remote commit is recorded in the controlled release record;
3. a clean clone reproduces the manifest and every applicable domain checker;
4. deviations and unresolved selections are dispositioned; and
5. accountable engineering and qualified safety reviewers sign the applicable release stage.

This configuration candidate does not close any fabrication or energization gate.
