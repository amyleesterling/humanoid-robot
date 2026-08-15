# R208 independent review request

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Independently review `HR-V0-OBSERVATION-COMPUTE-POWER-BOUNDARY-P0.1` against the current native R202/R204/P1.16 sources and the controlled R203/R207 interfaces. This is a diagnostic-only path with zero functional-safety credit.

1. Reproduce the exact PI1 pin 17/20, W14001-W14006, R202 VCC1/EN/output, 1.00 kohm series, 10.0 kohm pulldown and GPIO22-25 topology. Confirm that no intended 5 V or independent compute-side source exists.
2. Reopen Raspberry Pi HAT+ Specification revision 05 December 2024, current Raspberry Pi hardware documentation, RP1 Peripherals release 1.1 dated 07 November 2023, and TI ISO1212 SLLSEY7G revised February 2025.
3. Recalculate the 3.80 mA IC quiescent maximum, 1.20 mA four-high pulldown screen, 5.00 mA steady source-load screen, 200 nF decoupling and 1.089 uJ ideal stored-energy screen. Determine whether any current official Raspberry Pi record actually approves that load from Pi 5 physical pin 17.
4. Recalculate the 2.364 V source-side high floor and determine whether a Pi 5/RP1 VIH, VIL, leakage, clamp or injection-current guarantee exists in a current primary record. Do not reuse electrical data published only for earlier SoCs.
5. Recalculate the 3.300 mA nominal and 3.333 mA at -1% RSO hard-short screens against TI's +/-3 mA recommended output-current envelope at 3.3 V. Review the BLOCKER disposition and propose a value/topology only if both fault current and Pi 5 input margin can be proved.
6. Audit all seven partial-power states and all eight faults. Treat TI's powered-down/UVLO output state as undetermined and require physical no-backfeed, ramp, brownout and fault-injection evidence.
7. Confirm all six manufacturer questions remain unsent, all twelve selection holds remain open, and all fourteen acceptance rows remain unexecuted.

Report BLOCKER/MAJOR/MINOR findings with exact file, row, net, reference and primary-source support. Do not approve connection, powered testing, motion or energization.
