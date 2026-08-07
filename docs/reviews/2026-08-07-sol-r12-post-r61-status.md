# Sol R12 status after R61 H1 pilot-light correction

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, PANEL WIRING, FABRICATION, OR ENERGIZATION**

Date: 2026-08-07

Independent review: Sol R12, resupplied 2026-08-07

Project response: R61 / Electrical `V3-P1.5` / `HR-V0-H1-RCV-P0.1`

The supplied Sol summary remains the already controlled R12 independent review: 18 BLOCKER, 30 MAJOR, and 8 MINOR findings against the historical pre-correction baseline. It is not a new review round. R61 is a project-owned electrical/configuration correction and is not an approval.

## Defect corrected

R60 selected an exact amber H1 candidate in the physical panel overlay, but Electrical V3-P1.4 still represented H1 as `SAFE ELIGIBLE indicator interface`, marked it `SELECTION REQUIRED`, and labeled the two unverified device terminals `+` and `-`. That created three problems:

- the authoritative circuit BOM disagreed with the panel BOM;
- `SAFE ELIGIBLE` could imply a broader safety state than the `SR1_STATUS` net proves; and
- `+/-` inferred terminal polarity that the retained manufacturer evidence and received-device record did not establish.

## Correction made

Electrical V3-P1.5:

- freezes H1 as IDEC `HW1P-1FQD-A-24V`, supported by the current official IDEC USA page and `HW Series Catalog_Screw` dated 2026-07-23;
- describes it as an amber 22 mm round-flush, black-plastic-bezel, screw-terminal, 24 VAC/DC pilot-light candidate;
- labels it **RESET STAGE READY - DIAGNOSTIC ONLY / NO MOTION AUTHORITY**;
- replaces the inferred `TBD-H+ / TBD-H-` designators and `+/-` pin names with `TBD-HA / TBD-HB` and unverified-terminal wording;
- states that those are project placeholders, not manufacturer markings;
- assigns H1 zero safety credit and prohibits calling it safe or armed;
- synchronizes the native KiCad source, BOM, connector/net/wire/unresolved schedules, netlist, PDF/SVG exports and source manifest; and
- synchronizes system `BOM-041`, moving H1 from `selection_required` to `exact_candidate_hold` and changing the system counts to eighteen exact holds / twenty-nine selection-required groups without adding H1 to Evaluation Batch A; and
- adds `HR-V0-H1-RCV-P0.1` plus fourteen `NOT EXECUTED` receiving, dimensional, terminal, controlled-component-test, human-factors, HIL and disposition records.

The generated project remains thirteen pages, 76 component blocks, 295 terminals, 100 native nets, 259 wire labels, 63 unresolved rows and 24 `TBD-*` terminal designations. KiCad 10.0.5 ERC remains 0 errors / 0 warnings.

## Sol finding disposition

| Sol concern | R61 state | Still required |
|---|---|---|
| Component identity/configuration mismatch | Exact H1 value and evidence now agree between V3 and the panel package. | Authorized procurement/receiving; exact received construction; immutable evidence; independent acceptance. |
| Unverified terminal/pin claims | Polarity-looking labels are removed; project placeholders are explicit. | Received markings/orientation/internal-circuit evidence and controlled DC characterization before terminal replacement or wiring release. |
| Misleading state indication | H1 reports only the SR1 reset-stage status and is explicitly diagnostic-only with no motion authority or safety credit. | Actual-context legend/brightness/human-factors validation and disconnected-load HIL/fault evidence. |
| Physical build evidence absent | Fourteen fail-closed evidence rows now define the required closure route. | Every row remains unexecuted; instruments, source/protection/test bounds, responsible reviewers and raw records are still missing. |

Sol's central verdict remains correct: HR-V0 is not build-ready, energization remains prohibited, and HR-30W walking is not demonstrated. R61 closes no procurement, fabrication, panel-wiring, energization, or functional-safety gate.
