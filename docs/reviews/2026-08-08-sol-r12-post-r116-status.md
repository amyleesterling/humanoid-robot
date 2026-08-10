# Sol R12 findings rechecked after R116

This is a project-owned reconciliation, not a new Sol review. The summary resupplied on 2026-08-08 is materially the existing R12 verdict and is not double-counted. Sol's baseline totals remain **18 BLOCKER, 30 MAJOR and 8 MINOR**, with 62/62 requirements draft, 106 historical V2.1 electrical selections unresolved, and zero approved executed verification records at the reviewed baseline.

R116 corrects one configuration-management defect exposed during the reconciliation: current narrative files no longer describe the superseded P1.12 watchdog-in-SR1-input topology as current. They now consistently state V3-P1.13: both S0 NC channels connect directly to SR1, while KWD1/KWD2 gate only `SR1:A1` and retain zero safety credit.

R116 also controls the current Pilz PNOZ s4 manual, hashes it, and maps fourteen exact source-to-terminal/net checks. The mapping supports the intended RESET-then-ARM/EDM sequence at schematic level. It does not prove received terminals, physical routing, selector settings, protection, contact duty, brownout/recovery, total stopping time, fault tolerance, PLr/category, ISO 13849 validation or permission to energize.

No Sol build or energization finding closes. HR-V0 remains a preliminary architecture with increasingly complete source and review evidence, not a released buildable machine. HR-30W remains physically plausible but unproven.
