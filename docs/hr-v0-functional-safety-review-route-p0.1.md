# HR-V0 functional-safety review route P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**

Identifier: `HR-V0-FS-REVIEW-ROUTE-P0.1`

Round: R219

Date: 2026-08-11

## Decision

Project Button needs a named, competent and sufficiently independent machinery functional-safety reviewer before PLr/SIL allocation, credited-function design acceptance, E2 authorization or physical validation can close. This package defines how to find and qualify that reviewer. It does not select one.

Four official capability routes were screened:

- TÜV SÜD America has a Massachusetts office and publishes the closest match to the complete requested lifecycle: ISO 12100 risk assessment, safety requirements, PLr/SIL determination, achieved-performance evaluation and validation.
- TÜV Rheinland publishes a broad US machinery functional-safety assessment and validation route; the exact US team and Boston coverage remain unverified.
- Pilz publishes machinery risk-assessment and validation services, but Project Button uses a Pilz safety-relay candidate. Any design, sales or component overlap must be disclosed and separated from independent validation.
- Schmersal tec.nicum publishes ISO 12100/ISO 13849 consulting and a named US contact, but its public consulting page does not prove complete independent ISO 13849-2 validation scope.

These are capability leads, not endorsements. No provider is selected or contacted, no files were transmitted, no quote was requested and no contract is authorized.

## Required review sequence

1. Phase A, before detailed safety-control release: complete the ISO 12100 hazard/risk review; allocate PLr or SIL; confirm safety functions, architecture, reliability, diagnostics, common-cause measures, systematic measures and fault exclusions; redline the SRS and current P1.15 electrical core.
2. Phase B, before E2: accept the disconnected-load validation plan, measurement chain and fault fixtures; review the received control-only configuration. E2 work authority remains a separate four-role gate.
3. Phase C, before any E4 motion: review received final elements, DC application, guards/stops and loaded traces; execute and sign analysis plus physical fault-injection validation under the selected method.

The P1.17 observation project is a presentation/integration view only. P1.15 remains the direct core electrical review input.

## Competence and independence

Company brand is not reviewer competence. Acceptance requires named people, documented standards and machinery experience, PLr/SIL and quantitative design competence, validation/fault-injection experience, signed conflict disclosure, explicit role separation, Boston site capability, configuration-bound deliverables and defined change invalidation.

No person may approve their own design contribution. If one organization advises design and later validates it, different named personnel and an accepted organizational-independence disposition are mandatory. A provider's certificate, marketing statement or component supply relationship never grants Project Button work authority.

## Required deliverables

The controlled acceptance matrix requires signed SRS and risk assessment, PLr/SIL allocation, editable calculations, category/subsystem decomposition, reliability/DC/CCF/systematic/fault-exclusion evidence, validation plan, raw physical evidence, signed ISO 13849-2 validation, residual-risk and issue registers, reviewer declarations and exact configuration/commit/manifest binding.

All sixteen deliverables are presently not received and not accepted.

## Authority

Internal comparison is allowed. Sending an inquiry, uploading a file, requesting or accepting a quote, selecting a provider, signing a contract, connecting hardware, powered testing, motion and energization are not authorized by this package.

## Web guide

The [interactive provider-route guide](../release/hr-v0/functional-safety-review-route-p0.1/index.html) filters the four routes without hiding unresolved scope or independence conditions.

This package closes only the absence of a controlled reviewer-selection route. EG-012, EG-021, EG-022 and EG-026 remain partial. It does not close any Sol blocker requiring buildable CAD, received hardware, physical tests, stopping evidence or qualified signatures.
