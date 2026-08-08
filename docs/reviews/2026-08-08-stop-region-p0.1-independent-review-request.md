# Independent review request - HR-V0 stop-region clearance P0.1

Please review `HR-V0-STOP-REGION-P0.1` for technical accuracy and completeness. This is an evidence-quality review, not an approval request.

## Review scope

1. Reproduce the `6,411` sampled boundary poses and verify the intentional-interface exclusions.
2. Audit the continuous interval method, all `131` pair-region certificates, `133` leaf cells and the `5.743912 mm` minimum lower bound.
3. Confirm that the tested union covers J1 `-25..-20 deg`, J1 `70..75 deg` and J2 `10..15 deg` against the stated companion-axis domains.
4. Challenge whether any missing body, cable, connector, strain relief, guard, fastener or service envelope invalidates the nominal-only interpretation.
5. Audit `HSI-001..020` for every physical input needed before a stop topology can be selected.
6. Review the candidate/rejected topology dispositions and identify any safer feasible route or prohibited load path.
7. Confirm that no historic angle, topology, physical part, motion envelope or release has been inferred from nominal CAD.

## Files

- `docs/hr-v0-stop-region-clearance-p0.1.md`
- `cad/hr-v0/generated/stop-region-clearance-p0.1/`
- `tools/generate_hr_v0_stop_region_clearance.py`
- `tools/check_hr_v0_stop_region_clearance.py`
- parent source `tools/generate_hr_v0_arm_architecture.py`
- parent evidence `cad/hr-v0/generated/arm-architecture-p0.7/`

Report findings as `BLOCKER`, `MAJOR` or `MINOR`, with exact file/row/pair/pose references and reproducible corrections. Do not mark the design approved for fabrication, motion or energization.
