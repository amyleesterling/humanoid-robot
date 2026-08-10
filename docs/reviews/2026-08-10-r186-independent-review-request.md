# R186 independent review request — Q4X installation evidence

> **PRELIMINARY - RECEIVING AND METROLOGY PLAN ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, DRILLING, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Review exact commit containing artifact `HR-V0-Q4X-INSTALL-EVIDENCE-P0.1`.

## Reproduce

```text
python tools/generate_hr_v0_q4x_installation_evidence_p01.py
python tools/check_hr_v0_q4x_installation_evidence_p01.py
```

## Required challenge

1. Open LAPP instruction `99990621 / BS00/2622 VS20` and VDE certificate 40010604 appendix 200A. Confirm that M12 installation and cap-nut torque are 1.5 N m, that the instruction applies M to locknut installation, and that the certificate's separate locknut-torque field is blank.
2. Confirm no reviewed primary record supplies a Project Button through-hole diameter or tolerance.
3. Reconcile all ten receiving lines to R184/R185 identities and quantities. Flag any inferred supplier, pack, price, availability or substitution.
4. Audit all ten metrology steps and eleven holds for missing irreversible-work boundaries, required calibration, competence, uncertainty, evidence or quarantine controls.
5. Confirm the web guide, CSVs, JSON and Markdown agree and that every result remains `NOT EXECUTED`.
6. State separately whether the package is ready for acquisition decision, received-part metrology, drilling, fabrication, connection or energization. Do not combine those decisions.

Report BLOCKER / MAJOR / MINOR findings with exact file, row, source and proposed correction. This review provides no work authority or functional-safety approval.
