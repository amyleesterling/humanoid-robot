# R249 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R249 products: `HR-V0-PROP-PROPAGATION-P0.1` and `HR-V0-CONFIG-REC-P0.13`.

## Deterministic result

The dedicated checker verifies exactly six blank configuration/axis property inputs, twelve existing downstream consumers, eight existing historical/planning artifacts prohibited from release use, ten unexecuted rebuild steps, twelve blank downstream records, twelve open holds and ten open acceptances. It verifies all bound source hashes, source/release parity, package manifests, warning propagation and configuration counts.

Synthetic accepted data exercise the compiler's canonical output. The compiler rejects the actual blank template with exit code 78. Even its synthetic successful path leaves every authorization and safety-credit flag false.

## Executed results

- Python compile for compiler, generator and checker: **PASS**.
- Dedicated R249 checker: **PASS**.
- Blank-template fail-closed compiler check: **PASS**, exit code 78.
- Standard repository checker sweep: **192/192 PASS**.
- Native KiCad 10.0 checker sweep: **18/18 PASS**.
- Release-candidate manifest: **5,396 package files before adding this validation record; regenerated afterward**.
- Desktop browser QA at 1280 x 720:
  - property-propagation guide: exact warning and no-bundle/stale-input status visible; 16 px body, 14 px minimum technical text, no page-level horizontal overflow, eight tables, eight downloads and 75 body rows;
  - configuration P0.13 guide: exact warning and no-bundle status visible; 16 px body, 14 px minimum technical text, no page-level horizontal overflow, five tables, five downloads and 200 body rows; and
  - both first-view screenshots were visually inspected; headings, warnings, status text and initial controls were readable and nonoverlapping.
- Narrow/mobile browser execution: **NOT COMPLETED**. Responsive CSS preserves the 16/14 px floors and local table scrolling, but no executed mobile screenshot is claimed.

## Boundary

These checks prove configuration, hash, template, compiler, stale-input and desktop-presentation behavior only. They do not establish any measured property, coordinate transform, torque, actuator duty, stopping performance, contact load, structural capacity, firmware motion limit, functional safety or work authority. Sol B-010, B-011 and B-013 remain open; zero gates close.
