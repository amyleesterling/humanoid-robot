# Independent review request - HR-V0 guard impact-energy basis P0.1

Review `HR-V0-GUARD-IMPACT-P0.1` against `HR-V0-GUARD-P0.3`, `HR-V0-GUARD-RET-P0.1`, `SYS-002` through `SYS-004`, `SAFE-004`, `SAFE-010`, `SAFE-011`, `MASS-002`, `EG-008`, and risks `R-001`, `R-002`, `R-003`, `R-006`, and `R-022`.

Reproduce and challenge:

1. all eight numeric arithmetic and sensitivity results, including units and rounding;
2. the deliberate separation of payload, moving-link, drive-persistence, detached-part and static-access hazards;
3. whether the full 0.750 kg point-mass screens are conservative for their stated limited purpose without being misrepresented as credible maxima;
4. the use of ROBOTIS 12 V no-load speed and stall endpoints, including the prohibition on treating them as simultaneous or continuous output;
5. the unresolved reflected inertia, gravity, supply/regen, contact compliance, stop latency and current-persistence terms;
6. the six-direction hazard matrix and whether any panel, corner, joint, anchor, receiver or cable-entry case is absent;
7. the open detached-hardware and static push-out load definitions;
8. the proposed full-assembly versus coupon test boundary; and
9. whether every artifact prevents selecting nominal 3 mm or 6 mm sheet, `12004`, test energy or acceptance criteria.

Use current primary documentation and record revision/date. Identify every BLOCKER / MAJOR / MINOR finding by file, row/control and calculation. Do not infer an impact rating, test multiplier, static load, projectile, material allowable, panel thickness or safety distance.

**This package requests technical criticism, not approval to procure, fabricate, move, connect or energize.**
