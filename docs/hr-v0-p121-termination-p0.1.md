# HR-V0 P1.21 endpoint termination evidence P0.1

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-P121-TERM-P0.1`

Date: 2026-08-11

Round: R243

Configuration: Project Button Electrical `V3-P1.21-SRA1-SUPPLY-WATCHDOG-CANDIDATE`, unaccepted; P1.15 remains current

## Outcome

The fourteen ends of the seven R242 conductor candidates now have an exact, endpoint-specific termination candidate instead of one generic `SELECTION REQUIRED` field:

- twelve XD24/KWD ends use held Phoenix Contact `AI 1,5 - 8 BK`, item `3200043`, with an 8 mm contact sleeve;
- the two Pilz `SR1:A1` and `SRA1:A1` ends use held Phoenix Contact `A 1,5 - 7`, item `3200263`, with a 7 mm uninsulated sleeve matching Pilz's current 7 mm strip requirement.

The split is deliberate. It avoids forcing an 8 mm contact sleeve into a Pilz application whose current manual specifies 7 mm preparation. It remains an application candidate, not Pilz, Phoenix Contact, code, or functional-safety approval.

## Exact process-tool candidates

- Phoenix Contact `CRIMPFOX 6`, item `1212034`, station 2 for 1.0 to 1.5 mm2 / AWG 18 to 16;
- Phoenix Contact `WIREFOX 10`, item `1212150`, for the 7 mm and 11 mm preparation lengths; and
- Phoenix Contact `TSD-M 1,2NM`, item `1212224`, covering the source-published 0.5 N m Pilz setting and 0.6 to 0.8 N m Phoenix relay range.

Exact screwdriver bits remain `SELECTION REQUIRED` because neither terminal's drive geometry is inferred from a catalog photo. The torque tool requires current calibration and access verification before use.

## Pull-test boundary

Phoenix Contact's current tool handbook publishes 40 N for 1.5 mm2 / AWG 16 ferrule pull-out testing and describes applying the force for 60 seconds without damage to the crimp point. R243 carries that only as a sacrificial received-lot coupon criterion. It proposes at least three coupons per ferrule format, but the final sample plan, fixture, grips, calibration, uncertainty and qualified acceptance remain open.

The 40 N coupon value is not inferred as an installed-terminal pull criterion. No destructive coupon load may be applied to a robot device without a separate manufacturer-supported, qualified procedure.

## Controlled package

Interactive guide: `release/hr-v0/p121-termination-p0.1/index.html`

Machine-readable records include eleven dated source records, two exact ferrule candidates, four tool/equipment rows, all fourteen endpoint assignments, six process steps, three terminal-family plans, three pull-test rows, the explicit partial disposition of `R242-H02`, twelve open holds and twenty blank inspection rows.

`BOM-098` and `HR-V0-CONFIG-REC-P0.7` raise configuration coverage to 98 groups without promoting P1.21 or releasing any work.

Generate with `tools/generate_hr_v0_p121_termination_p01.py`, synchronize with `tools/generate_hr_v0_r243_sync.py`, and validate with `tools/check_hr_v0_p121_termination_p01.py`.

No result in this package grants functional-safety credit or authorizes procurement, cutting, fabrication, assembly, wiring, connection, powered testing, motion or energization.
