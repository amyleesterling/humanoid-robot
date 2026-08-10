# Independent review request — HR-V0 FR12 moving-mass metrology P0.1

> **PRELIMINARY — REVIEW REQUEST ONLY — NOT APPROVED FOR PURCHASE, ASSEMBLY, FABRICATION, MOTION, CONNECTION, OR ENERGIZATION.**

Review `HR-V0-FR12-MASS-MET-P0.1` for accuracy, completeness and executability. This is a project-owned R97 correction responding to Sol R12/R96 mass-property blockers, not a reviewer approval.

Please report `BLOCKER / MAJOR / MINOR` findings with exact file, row, formula, datum and source references. At minimum challenge:

1. rejection of the official `0.10 lb` containing-kit and `0.20 lb` included-sub-kit commerce fields for mass credit;
2. STEP hash, axis convention, frame-only centroid, bounding box, 30.463092 mm support radius and excluded geometry;
3. RM-X52/XM430 evaluation-article allocation and possible gripper/J2 double counting;
4. balance range, readability, traceability, repeatability, tare, environment, uncertainty and MSA requirements;
5. the two-reaction COM method, fixture tare/deflection, support datum and uncertainty propagation;
6. the validity and limitations of `Ixx <= m r²` and `m g r` bounds;
7. temporary-assembly screw/engagement/spacer/torque/locking/reuse/teardown hold;
8. raw/result templates, reconciliation and nonconformance route;
9. whether execution could close only `LOAD-OPEN-01` without hiding reflected drive inertia or other R96 inputs; and
10. every fail-closed authorization boundary.

Reproduce with the controlled CadQuery interpreter:

```powershell
& 'C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe' tools/generate_hr_v0_fr12_mass_metrology.py
& 'C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe' tools/check_hr_v0_fr12_mass_metrology.py
```

Do not infer a physical result, select X430/P1.1, authorize acquisition/work, or reduce any gate from clean automation.
