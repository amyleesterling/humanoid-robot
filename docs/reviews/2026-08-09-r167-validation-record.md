# R167 validation record

R167 issues `HR-V0-BOSTON-FAB-ROUTE-P0.3` as a current Boston/US machining-capability screen.

- Controlled parts: C01, C04, C05, C06 and C07.
- Controlled material: 6061-T651.
- Ten provider routes and ten current official source records.
- Ten open numerical/application inputs; none is accepted by assumption.
- Strongest published local evidence: Kontrast4D, Salem MA.
- Strongest online review routes: Protolabs and Xometry.
- Provider qualification, contact, upload, quotation, first article, fabrication, assembly, motion and energization all remain false or prohibited.

`python tools/check_hr_v0_boston_fabrication_route_p03.py` passes with ten route records, ten official source records and ten open design/application inputs. Repository-wide regression passes **124/124 checkers**: 96 standard Python checks, 14 CadQuery geometry checks, 13 KiCad-native checks and the deterministic release-manifest check. The staged manifest controls **2,789 package files**.

The interactive guide was inspected in the in-app browser at 1,280 x 720 and 390 x 844 requested viewports (1,265 x 720 and 375 x 844 effective content viewports). Body and filter text remain 16 px, page-level horizontal overflow is zero at both sizes, the preliminary warning remains visible, all six route cards render, the Boston/New England filter exposes only Kontrast4D and the grouped local research candidates, and the browser console reports no errors.

Passing proves internal completeness and fail-closed state only; it is not supplier qualification or physical evidence. The energization register remains **0 closed / 22 partial / 8 open**.
