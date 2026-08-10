# R180 independent review request

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**

Please independently review controlled artifact **HR-V0-EVENT-OBS-CORR-P0.1** at the exact commit supplied with this request.

## Review focus

1. Verify from P1.15 that `EDM_K1_OUT` and `SRA1_START_RETURN` are locations in one series NC mirror-contact EDM path and cannot supply two independent K1/K2 state observations.
2. Challenge the corrected distinction between one common EDM-chain current witness and the individual `K1_STATUS`/`K2_STATUS` NO auxiliary diagnostic channels.
3. Confirm that the NO auxiliaries receive zero safety credit and cannot replace the NC mirror-contact EDM safety function.
4. Audit both eight-channel allocations for simultaneity, missing channels and the claim that RESET alone cannot command motion.
5. Check the `MSO58B`, four-`TCP0030A` and three-`TIVP02/TIVPMX10X` evaluation-candidate records against the cited current Tektronix documents, including probe-power allocation, delay, loading and compatibility.
6. Reject any diagnostic-load proposal that lacks exact parts, rail/tolerance/temperature bounds, single-fault analysis, protection, thresholds and automatic-restart/EDM noninterference evidence.
7. Confirm that all limits, motion sensing, source test points, work authority and physical evidence remain unresolved and that no instrument receives safety credit.

Return exact file/row references, severity, primary-source evidence and a clear disposition. Do not approve procurement, connection, powered testing, motion or energization.
