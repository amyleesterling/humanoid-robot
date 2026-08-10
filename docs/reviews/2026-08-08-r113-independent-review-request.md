# R113 independent review request

Review identifier `HR-V0-GRIP-SEL-P0.1` as a fail-closed configuration correction. Do not interpret this request as procurement, fabrication, assembly, motion or energization authority.

## Review these artifacts

- `docs/hr-v0-gripper-selection-correction-p0.1.md`
- `references/gripper/hr-v0-gripper-requirement-compliance-p0.1.csv`
- `requirements/hr-v0-gripper-requirement-decision-p0.1.csv`
- `release/hr-v0/gripper-selection-p0.1/index.html`
- historical `docs/hr-v0-gripper-alternative-trade-p0.1.md`
- `requirements/requirements.csv` rows `SYS-002` and `GRIP-002`
- `docs/system-specification.md` section 2, revision 0.1

## Questions

1. Does the 40-70 mm each-principal-dimension baseline govern candidate selection unless formally changed?
2. Does the Pololu 32 mm internal opening fail that baseline by at least 8 mm before installed pads and uncertainty?
3. Is the ROBOTIS 20-75 mm catalog stroke correctly limited to conditional compatibility rather than installed-opening proof?
4. Did the controlled ServoCity evidence omit a usable-opening value, and is `UNVERIFIED` the correct disposition?
5. Is the 25-30 mm object correctly separated as an unapproved change proposal?
6. Are the authority, exact-object, test, risk, tolerance and configuration records sufficient prerequisites for any change?
7. Does `GRIP-002` require separate formal disposition before any non-ROBOTIS selection?
8. Are any current pages or records still likely to mislead a reader into treating Pololu as preferred or selected?

Return BLOCKER / MAJOR / MINOR findings with exact file and field/section references. Use current primary manufacturer documentation with revision/date for any challenged product fact. State separately whether the correction is accurate, whether any gripper is build-ready, and whether any action is ready for qualified mechanical, electrical or functional-safety review.

No approval for fabrication or energization is requested.
