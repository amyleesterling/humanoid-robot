# R70 validation record — same-interface moving-mass reduction study

> **PRELIMINARY—NOT APPROVED FOR FABRICATION, MOTION, OR ENERGIZATION.**

Date: 2026-08-07

Round owner: Codex project correction pass

Independent review status: not executed

R70 responds to the R69 mass-budget blocker without changing the controlled P0.7 configuration. `HR-V0-MASS-REDUCTION-P0.1` introduces C01R/C04R/C06R/C07R as nonselected subtractive candidates.

Verified analytical results:

- all four candidates are exact B-Rep subsets of their P0.7 parents within `0.000010 mm³`;
- controlled plate thickness, hole axes, countersinks and stop contact features are unchanged;
- four-part CAD-estimated mass falls from 231.110 g to 173.127 g, a 57.983 g reduction;
- known/CAD-estimated moving subtotal would fall from 692.758 g to 634.775 g;
- unresolved headroom would increase from 57.242 g to 115.225 g;
- nominal positive-stop first contact remains 117.999985°;
- seven ligament/load study screens pass as analytical screens only.

The study remains blocked from selection by missing exact stock/material closure, local bending/prying/notch/fatigue/impact analysis, manufacturing tolerance, received fit, FAI, measured mass/COM, proof correlation, stop-impact evidence and independent qualified mechanical disposition. `MASS-002`, `MECH-005`, `MECH-006` and every fabrication/energization authorization remain open or partial.

Validation command:

`C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe tools/check_hr_v0_mass_reduction_study.py`

Expected result: four exact-subset candidates, 57.983 g CAD reduction and 115.225 g provisional unresolved headroom, while explicitly retaining the mass blocker and preliminary warning.
