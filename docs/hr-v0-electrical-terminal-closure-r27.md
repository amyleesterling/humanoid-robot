# HR-V0 Electrical Terminal Closure R27

> **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Date: 2026-08-06  
Configuration: Electrical `V3-P0.6`

## Outcome

Four E-stop terminals are no longer anonymous `TBD-*` placeholders. IDEC's current XW product page identifies `XW1E-BV402M-R` as the proposed 40 mm, turn/pull-reset, 2NC screw-terminal assembly. IDEC's XW bottom-view drawing shows that a non-illuminated screw-terminal 2NC device has one right-side NC pair marked `1-2` and one left-side NC pair marked `1-2`.

The project allocation is now:

| Project terminal | Manufacturer position and mark | Net |
|---|---|---|
| `S0:R-1` | bottom-view right NC, mark `1` | `SR1_S11` |
| `S0:R-2` | bottom-view right NC, mark `2` | `WD1_SAFETY_IN` |
| `S0:L-1` | bottom-view left NC, mark `1` | `SR1_S21` |
| `S0:L-2` | bottom-view left NC, mark `2` | `WD2_SAFETY_IN` |

`R-` and `L-` are project-unique KiCad prefixes needed because the manufacturer repeats marks `1-2` on two physical contact positions. They are not claimed manufacturer markings. The orientation is always the manufacturer bottom view with `TOP` up.

## Evidence and limits

- Exact proposed device: IDEC US product page, checked 2026-08-06: https://www.idec.com/en-us/switches-indicator-lights/switches-pushbuttons/emergency-stop-switches/xw-22mm-estop/xw1e-bv402m-r
- Contact-position evidence: IDEC `XW-Indicator-Datasheet`, terminal arrangement (bottom view), checked 2026-08-06: https://us.idec.com/idec-us/en/USD/medias/XW-Indicator-Datasheet.pdf?context=bWFzdGVyfGRvY3VtZW50c3wxOTg4ODY2fGFwcGxpY2F0aW9uL3BkZnxkb2N1bWVudHMvaDU3L2hiMC84OTMyMzA0MzIyNTkwLnBkZnw5MmUwZTUyYzNiYWJjMTVjM2Y2ZjQ2ZTc5MGYzOGQ0OTdkZjE0ZGE4NmExOTFkNjkxZWNmY2M3M2QyZDA3YTQw
- S0 remains proposed. `INSPECT-ELEC-003` must confirm the received order code, `TOP` orientation, right/left positions, physical markings, mechanical action, rest-state closure, actuated-state opening and channel separation before wiring.
- Clean ERC validates modeled annotation/connectivity only. It does not prove the switch, wiring, positive-opening action, diagnostic coverage or functional-safety performance.

## Why RESET and ARM terminals remain unresolved

S1 and S2 order codes and colors remain frozen, but their terminal numbers do not. IDEC's 2026-07-14 HW specification-change notice says shipments have been transitioning since 2026-06-15, either previous or updated designs may arrive under the same complete-switch part number, and some individual BOM component part numbers changed. The notice is current primary evidence: https://www.idec.com/en-us/news/usa-idec-hw-series-product-specification-change

The package therefore does not copy a legacy or push-in terminal drawing onto the received screw-terminal assembly. `S1:TBD-R1/TBD-R2` and `S2:TBD-A1/TBD-A2` remain `SELECTION REQUIRED` until received bottom-view photographs and continuity records close them.

## Regeneration result

- 11 native KiCad pages
- 55 component blocks
- 241 terminals
- 62 named connected nets plus 25 deliberate unconnected nets
- 216 unique wire labels
- 43 unresolved component/interface rows
- 60 remaining `TBD-*` terminal designations
- KiCad 10.0.5 ERC: 0 errors, 0 warnings

No energization gate closed in this pass.
