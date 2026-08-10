# Independent mechanical review request — HR-V0 mass reduction P0.1

> **PRELIMINARY—REVIEW INPUT ONLY—NOT APPROVED FOR FABRICATION, MOTION, OR ENERGIZATION.**

Please review `HR-V0-MASS-REDUCTION-P0.1` as a proposed same-interface replacement study, not as the active arm configuration.

Review questions:

1. Confirm each C01R/C04R/C06R/C07R solid is a true subset of its named P0.7 parent and that no controlled interface or stop-contact surface was removed.
2. Independently recompute CAD volumes/masses and the resulting 634.775 g incomplete moving subtotal.
3. Check the 2.300/1.300/3.650/4.650 mm nominal ligament calculations and whether the chosen screening criteria are adequate for a feasibility down-select.
4. Review load paths around both M5 countersinks, the four M2.5 interfaces and the C06R/C07R stop rails for prying, local bending, load-sharing, notch, fatigue and impact cases missing from the current screens.
5. Confirm that the subset argument is sufficient only for nominal rigid-body collision non-regression and does not improperly claim manufactured, cable, guard or deformation clearance.
6. Confirm the nominal J2 positive-stop contact geometry is unchanged and identify all physical tolerance/impact evidence required before selection.
7. Recommend whether to reject, revise or advance the candidates to prototype-only FAI/proof planning. Do not authorize fabrication or energization.

Primary files:

- `docs/hr-v0-mass-reduction-study-p0.1.md`
- `cad/hr-v0/generated/mass-reduction-p0.1/`
- `tools/generate_hr_v0_mass_reduction_study.py`
- `tools/check_hr_v0_mass_reduction_study.py`
- parent `cad/hr-v0/generated/arm-architecture-p0.7/`

Record exact repository commit, tool versions, calculations, assumptions and finding severity. Distinguish independent verification from project-generated checker output.
