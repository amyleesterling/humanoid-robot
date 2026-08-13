# HR-V0 J2 C07 pocket-edge mesh progression through R302

**PRELIMINARY—NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

This handoff reconciles the controlled R286-R302 numerical-method chain. It is analysis-development evidence only. It does not select P0.13, close R279-C02 or R278-H02, establish structural capacity, or authorize physical work.

## Outcome

The C07 mesh now has a defensible seam-free exact-zone analysis partition and a linear tetrahedral mesh that passes the frozen global and monitored-zone SICN gates. Curved Tet10 Jacobian screening remains open. R300 reduced the remaining failure to three Q8 quadrature points in two elements on one exact rail-transition cylindrical face. R302 freezes a single successor: add the same local field to that face and its actual X mirror. The R302 mesh has not been executed.

| Rounds | Controlled result | Disposition |
|---|---|---|
| R286-R287 | Exact exterior facet/OCC mapping and load geometry were evaluated; a targeted fidelity remesh reduced maximum Q8 surface deviation to 0.004976 mm and passed the single-level/last-pair geometry screens. | Exact-zone clipping, full-domain positivity, structural solution, and R279-C02 remained open. |
| R288-R292 | Twenty-seven exact zones were partitioned and conformally meshed. Four straight pocket-edge zones remained below the 0.20 monitored-zone SICN limit. A preregistered successor fixed sampled curved Jacobians but did not fix linear quality. | Pocket-only refinement method rejected. |
| R293-R296 | Topology-preserving relocation and Frontal meshing independently reproduced the same four straight-zone failures. | Evidence identified artificial tangent seams in the eight-piece analysis partition as the shared defect; no physical CAD change was authorized. |
| R297 | The eight pocket-edge analysis fragments were fused into one exact pocket-edge volume and all 21 analysis volumes were re-fragmented conformally. Physical material volume and interfaces were preserved within the recorded numerical tolerances. | Seam-free analysis partition accepted for numerical development only. |
| R298-R299 | Frontal/Netgen mesh of the seam-free partition passed global and all monitored-zone linear quality gates. Six curved-Jacobian failures in two elements were localized to H3 bore-wall geometry. | Curved Jacobian gate remained false. |
| R300-R301 | A preregistered 0.25 mm H1-H4 bore-wall field produced 1,244,636 Tet10 elements, global minimum SICN 0.203978, zero cells below 0.20, and all monitored zones passing. Three remaining Q8 failures in two elements were localized to one exact rail-transition cylinder. | Linear quality is closed only for this mesh; curved Jacobian and R279-C02 remain open. |
| R302 | Exact failed rail-transition face plus its real X mirror were frozen with a 0.25 mm / 1.5 mm local field. A requested Z mirror was rejected because no such exact counterpart exists. | Preregistration complete; mesh unexecuted. |

## Controlled next action

Execute exactly the R302 two-face candidate once, preserve all R300 settings and thresholds, and evaluate global/per-zone SICN plus actual Q4/Q6/Q8 signed and normalized Jacobians. A pass may advance only the curved-mesh method. It cannot close R279-C02 without the remaining exact-zone, facet/load, full-domain, and structural requirements.

## Holds that remain open

- certified full-reference-domain curved-Jacobian positivity;
- exact-zone direct-quadrature structural fields and fixed probes;
- section resultants, reaction force/moment balance, and singularity trends;
- L0-L3/L4 convergence, observed order, GCI, and independent numerical acceptance;
- nonlinear one/two-rail contact and bumper compression/bottom-out behavior;
- exact A04 joined fastener/frame load path, preload, slip, bearing, prying, and separation;
- energy-based stopping loads from accepted inertia, speed, force-stroke, and current/torque decay;
- material certification, DFM/FAI, received-part inspection, and guarded physical correlation;
- qualified mechanical, electrical, and functional-safety review;
- procurement, fabrication, assembly, connection, powered testing, motion, and energization authority.

The source and mirrored release packages retain their own manifests, warnings, hashes, raw evidence, and fail-closed status records.
