# Humanoid Robot Program

Package baseline: **HR-30-SYS-R0.2**  
Status: **concept systems baseline, not approved for fabrication, procurement, or energization**  
Baseline date: 2026-08-06

This repository is the engineering source of truth for a staged **30-inch (762 mm) humanoid-robot program**. The first build is **not a walking humanoid**. It is HR-V0, a bench-mounted, guarded handoff demonstrator with one shoulder axis, one elbow axis, and one parallel gripper. Its validated architecture then becomes HR-30, a child-sized but not child-safe robot.

## Program sequence

1. HR-V0 proves the power, communications, watchdog, emergency-stop, joint-control, thermal, and handoff-test architecture on a bench.
2. HR-30A adds a 13-DOF head, torso, two arms, and two grippers on a bolted child-height pedestal.
3. HR-30B adds the full 30-inch silhouette and supported legs, with fall restraint attached at all times.
4. HR-30C proves powered stance and weight transfer after structural, thermal, fall, and safety gates pass.
5. HR-30D demonstrates dynamic walking under a slack overhead fall-arrest tether.
6. HR-30W is the required end-state: untethered level-floor walking in a controlled test area. Human-facing walking requires a later safety release.

No child may enter the test area during V0. Any later child-adjacent demonstration requires an independent risk assessment, qualified mechanical/electrical review, validated force and stopping limits, and a new released revision.

## Start here

- [R310 current surface-imprint disposition](release/hr-v0/j2-c07-pe-surface-imprint-disposition-p0.1/README.md)
- [R308 exact-facet failure handoff](docs/hr-v0-j2-c07-pe-mesh-progression-r308.md)
- [R308 independent review request](docs/reviews/2026-08-13-r308-independent-review-request.md)
- [R308 validation record](docs/reviews/2026-08-13-r308-validation-record.md)
- [Interactive R307 CAD-resident curving preregistration](release/hr-v0/j2-c07-pe-cad-curving-prereg-p0.1/index.html)
- [R307 numerical progression handoff](docs/hr-v0-j2-c07-pe-mesh-progression-r307.md)
- [Interactive R302 rail-transition Jacobian successor preregistration](release/hr-v0/j2-c07-pe-rail-jacobian-prereg-p0.1/index.html)
- [Interactive R296 pocket-edge topology disposition](release/hr-v0/j2-c07-pe-frontal-disposition-p0.1/index.html)
- [R302 numerical progression handoff](docs/hr-v0-j2-c07-pe-mesh-progression-r302.md)
- [R285 J2 targeted-remesh disposition](docs/hr-v0-j2-targeted-remesh-disposition-p0.1.md)
- [R285 independent review request](docs/reviews/2026-08-13-r285-independent-review-request.md)
- [R285 validation draft](docs/reviews/2026-08-13-r285-validation-record.md)
- [Interactive R285 targeted-remesh guide](release/hr-v0/j2-targeted-remesh-disposition-p0.1/index.html)
- [Interactive configuration reconciliation P0.49](release/hr-v0/configuration-reconciliation-p0.49/index.html)
- [R284 J2 curved-mesh development](docs/hr-v0-j2-curved-mesh-development-p0.1.md)
- [R284 independent review request](docs/reviews/2026-08-12-r284-independent-review-request.md)
- [R284 validation record](docs/reviews/2026-08-12-r284-validation-record.md)
- [Interactive R284 curved-mesh guide](release/hr-v0/j2-curved-mesh-development-p0.1/index.html)
- [Interactive configuration reconciliation P0.48](release/hr-v0/configuration-reconciliation-p0.48/index.html)
- [R283 J2 execution architecture](docs/hr-v0-j2-execution-architecture-p0.1.md)
- [R283 independent review request](docs/reviews/2026-08-12-r283-independent-review-request.md)
- [R283 validation record](docs/reviews/2026-08-12-r283-validation-record.md)
- [Interactive R283 execution guide](release/hr-v0/j2-execution-architecture-p0.1/index.html)
- [Interactive configuration reconciliation P0.47](release/hr-v0/configuration-reconciliation-p0.47/index.html)
- [R282 J2 refinement erratum](docs/hr-v0-j2-refinement-erratum-p0.1.md)
- [R282 independent review request](docs/reviews/2026-08-12-r282-independent-review-request.md)
- [R282 validation draft](docs/reviews/2026-08-12-r282-validation-record.md)
- [Interactive R282 fail-closed guide](release/hr-v0/j2-refinement-erratum-p0.1/index.html)
- [Interactive configuration reconciliation P0.46](release/hr-v0/configuration-reconciliation-p0.46/index.html)
- [R281 bounded J2 numerical backend](docs/hr-v0-j2-numerical-backend-p0.1.md)
- [R281 independent review request](docs/reviews/2026-08-12-r281-independent-review-request.md)
- [R281 validation record](docs/reviews/2026-08-12-r281-validation-record.md)
- [Interactive R281 numerical guide](release/hr-v0/j2-numerical-backend-p0.1/index.html)
- [Interactive configuration reconciliation P0.45](release/hr-v0/configuration-reconciliation-p0.45/index.html)
- [R280 bounded J2 refinement execution](docs/hr-v0-j2-stop-refinement-execution-p0.1.md)
- [R280 independent review request](docs/reviews/2026-08-12-r280-independent-review-request.md)
- [R280 validation record](docs/reviews/2026-08-12-r280-validation-record.md)
- [Interactive R280 execution guide](release/hr-v0/j2-stop-refinement-execution-p0.1/index.html)
- [Interactive configuration reconciliation P0.44](release/hr-v0/configuration-reconciliation-p0.44/index.html)
- [R279 exact local J2 convergence protocol](docs/hr-v0-j2-stop-refinement-protocol-p0.1.md)
- [R279 independent review request](docs/reviews/2026-08-12-r279-independent-review-request.md)
- [R279 validation record](docs/reviews/2026-08-12-r279-validation-record.md)
- [Interactive R279 convergence guide](release/hr-v0/j2-stop-refinement-protocol-p0.1/index.html)
- [Interactive configuration reconciliation P0.43](release/hr-v0/configuration-reconciliation-p0.43/index.html)
- [R278 exact-normal P0.13 stop analysis](docs/hr-v0-j2-stop-pad-pocket-fea-p0.1.md)
- [R278 calculation correction](docs/reviews/2026-08-12-r278-calculation-correction.md)
- [R278 independent review request](docs/reviews/2026-08-12-r278-independent-review-request.md)
- [R278 validation record](docs/reviews/2026-08-12-r278-validation-record.md)
- [Interactive R278 structural guide](release/hr-v0/j2-stop-pad-pocket-fea-p0.1/index.html)
- [Interactive configuration reconciliation P0.42](release/hr-v0/configuration-reconciliation-p0.42/index.html)
- [R277 dimensioned J2 pad-pocket candidate](docs/hr-v0-j2-pad-pocket-p0.1.md)
- [R277 independent review request](docs/reviews/2026-08-12-r277-independent-review-request.md)
- [R277 validation record](docs/reviews/2026-08-12-r277-validation-record.md)
- [Interactive R277 pad-pocket guide](release/hr-v0/j2-pad-pocket-p0.1/index.html)
- [Interactive configuration reconciliation P0.41](release/hr-v0/configuration-reconciliation-p0.41/index.html)
- [R276 exact-contact J2 pad boundary](docs/hr-v0-j2-soft-contact-pad-p0.2.md)
- [R276 independent review request](docs/reviews/2026-08-12-r276-independent-review-request.md)
- [R276 validation record](docs/reviews/2026-08-12-r276-validation-record.md)
- [Interactive R276 exact-contact guide](release/hr-v0/j2-soft-contact-pad-p0.2/index.html)
- [Interactive configuration reconciliation P0.40](release/hr-v0/configuration-reconciliation-p0.40/index.html)
- [R275 J2 soft-contact pad candidate](docs/hr-v0-j2-soft-contact-pad-p0.1.md)
- [R275 independent review request](docs/reviews/2026-08-12-r275-independent-review-request.md)
- [R275 validation record](docs/reviews/2026-08-12-r275-validation-record.md)
- [Interactive R275 pad guide](release/hr-v0/j2-soft-contact-pad-p0.1/index.html)
- [Interactive configuration reconciliation P0.39](release/hr-v0/configuration-reconciliation-p0.39/index.html)
- [R274 A04 exact-candidate joint package](docs/hr-v0-a04-joint-p0.1.md)
- [R274 independent review request](docs/reviews/2026-08-12-r274-independent-review-request.md)
- [R274 validation record](docs/reviews/2026-08-12-r274-validation-record.md)
- [Interactive R274 A04 guide](release/hr-v0/a04-joint-p0.1/index.html)
- [Interactive configuration reconciliation P0.38](release/hr-v0/configuration-reconciliation-p0.38/index.html)
- [R273 P0.12 access-well J2 stop candidate](docs/hr-v0-j2-stop-access-well-p0.1.md)
- [R273 validation record](docs/reviews/2026-08-12-r273-validation-record.md)
- [R273 independent review request](docs/reviews/2026-08-12-r273-independent-review-request.md)
- [Interactive R273 structural review](release/hr-v0/j2-stop-access-well-fea-p0.1/index.html)
- [Interactive configuration reconciliation P0.37](release/hr-v0/configuration-reconciliation-p0.37/index.html)
- [R272 P0.11 mixed-side J2 stop candidate](docs/hr-v0-j2-stop-sideweb-p0.1.md)
- [Interactive R272 structural review](release/hr-v0/j2-stop-sideweb-fea-p0.1/index.html)
- [Interactive configuration reconciliation P0.36](release/hr-v0/configuration-reconciliation-p0.36/index.html)
- [R271 C06 full-part FEA screen](docs/hr-v0-j2-stop-fea-p0.1.md)
- [Interactive R271 FEA review](release/hr-v0/j2-stop-fea-p0.1/index.html)
- [Interactive configuration reconciliation P0.35](release/hr-v0/configuration-reconciliation-p0.35/index.html)
- [R271 validation record](docs/reviews/2026-08-12-r271-validation-record.md)
- [R271 independent structural-analysis review request](docs/reviews/2026-08-12-r271-independent-review-request.md)
- [R270 corrected J2 stop model and bossed candidate](docs/hr-v0-j2-stop-bossed-p0.1.md)
- [Interactive R270 J2 stop review](release/hr-v0/j2-stop-bossed-p0.1/index.html)
- [Interactive configuration reconciliation P0.34](release/hr-v0/configuration-reconciliation-p0.34/index.html)
- [R270 validation record](docs/reviews/2026-08-12-r270-validation-record.md)
- [R270 independent review request](docs/reviews/2026-08-12-r270-independent-review-request.md)
- [R269 J2 hard-stop strength correction](docs/hr-v0-j2-stop-strength-p0.1.md)
- [Interactive R269 stop-strength review guide](release/hr-v0/j2-stop-strength-p0.1/index.html)
- [Interactive configuration reconciliation P0.33](release/hr-v0/configuration-reconciliation-p0.33/index.html)
- [R269 independent review request](docs/reviews/2026-08-12-r269-independent-review-request.md)
- [Sol R12 status after R269](docs/reviews/2026-08-12-sol-r12-post-r269-status.md)
- [R268 functional datum/GD&T correction](docs/hr-v0-gdt-review-p0.2.md)
- [Interactive R268 GD&T review guide](release/hr-v0/gdt-review-p0.2/index.html)
- [Interactive configuration reconciliation P0.32](release/hr-v0/configuration-reconciliation-p0.32/index.html)
- [R268 independent review request](docs/reviews/2026-08-12-r268-independent-review-request.md)
- [Sol R12 status after R268](docs/reviews/2026-08-12-sol-r12-post-r268-status.md)
- [R267 Lot A alternate acquisition route](docs/hr-v0-lot-a-alternate-route-p0.1.md)
- [Interactive R267 route guide](release/hr-v0/lot-a-alternate-route-p0.1/index.html)
- [Interactive configuration reconciliation P0.31](release/hr-v0/configuration-reconciliation-p0.31/index.html)
- [R267 independent review request](docs/reviews/2026-08-12-r267-independent-review-request.md)
- [Sol R12 status after R267](docs/reviews/2026-08-12-sol-r12-post-r267-status.md)
- [R266 Lot A decision capsule](docs/hr-v0-lot-a-decision-capsule-p0.1.md)
- [Interactive R266 draft decision guide](release/hr-v0/lot-a-decision-capsule-p0.1/index.html)
- [Interactive configuration reconciliation P0.30](release/hr-v0/configuration-reconciliation-p0.30/index.html)
- [R266 independent review request](docs/reviews/2026-08-12-r266-independent-review-request.md)
- [Sol R12 status after R266](docs/reviews/2026-08-12-sol-r12-post-r266-status.md)
- [R265 `HR-V0-CARRIER-FIT-EVID-CAP-P0.1` unpowered evidence capture](docs/hr-v0-carrier-fit-evidence-capture-p0.1.md)
- [Interactive R265 carrier-fit measurement guide](release/hr-v0/carrier-fit-evidence-capture-p0.1/index.html)
- [Interactive configuration reconciliation P0.29](release/hr-v0/configuration-reconciliation-p0.29/index.html)
- [R265 independent review request](docs/reviews/2026-08-12-r265-independent-review-request.md)
- [Sol R12 status after R265](docs/reviews/2026-08-12-sol-r12-post-r265-status.md)
- [R264 `HR-V0-DXL-CARRIER-MOUNT-IF-P0.2` connector- and datum-aware carrier mounting](docs/hr-v0-dxl-carrier-mount-p0.2.md)
- [Interactive R264 no-drill mounting guide](release/hr-v0/dxl-carrier-mount-p0.2/index.html)
- [Interactive configuration reconciliation P0.28](release/hr-v0/configuration-reconciliation-p0.28/index.html)
- [R264 independent review request](docs/reviews/2026-08-12-r264-independent-review-request.md)
- [Sol R12 status after R264](docs/reviews/2026-08-12-sol-r12-post-r264-status.md)
- [R263 carrier power-harness and panel-placement correction P0.2](docs/hr-v0-dxl-protection-carrier-harness-p0.2.md)
- [Interactive R263 six-harness and collision guide](release/hr-v0/dxl-protection-carrier-harness-p0.2/index.html)
- [Interactive configuration reconciliation P0.27](release/hr-v0/configuration-reconciliation-p0.27/index.html)
- [R263 independent review request](docs/reviews/2026-08-12-r263-independent-review-request.md)
- [Sol R12 status after R263](docs/reviews/2026-08-12-sol-r12-post-r263-status.md)
- [R262 U2D2-to-JC1 manufacturer-build request P0.1](docs/hr-v0-u2d2-jc1-harness-rfq-p0.1.md)
- [Interactive R262 RFQ guide](release/hr-v0/u2d2-jc1-harness-rfq-p0.1/index.html)
- [Interactive configuration reconciliation P0.26](release/hr-v0/configuration-reconciliation-p0.26/index.html)
- [R262 independent review request](docs/reviews/2026-08-12-r262-independent-review-request.md)
- [R262 validation record](docs/reviews/2026-08-12-r262-validation-record.md)
- [Sol R12 status after R262](docs/reviews/2026-08-12-sol-r12-post-r262-status.md)
- [R261 U2D2-to-JC1 controller harness P0.1](docs/hr-v0-u2d2-jc1-harness-p0.1.md)
- [Interactive R261 harness guide](release/hr-v0/u2d2-jc1-harness-p0.1/index.html)
- [Interactive configuration reconciliation P0.25](release/hr-v0/configuration-reconciliation-p0.25/index.html)
- [R261 independent review request](docs/reviews/2026-08-12-r261-independent-review-request.md)
- [R261 validation record](docs/reviews/2026-08-12-r261-validation-record.md)
- [Sol R12 status after R261](docs/reviews/2026-08-12-sol-r12-post-r261-status.md)
- [R260 observation-carrier mounting stack P0.1](docs/hr-v0-observation-mount-stack-p0.1.md)
- [Interactive R260 mounting-stack guide](release/hr-v0/observation-mount-stack-p0.1/index.html)
- [Interactive configuration reconciliation P0.24](release/hr-v0/configuration-reconciliation-p0.24/index.html)
- [R260 independent review request](docs/reviews/2026-08-12-r260-independent-review-request.md)
- [R260 validation record](docs/reviews/2026-08-12-r260-validation-record.md)
- [Sol R12 status after R260](docs/reviews/2026-08-12-sol-r12-post-r260-status.md)
- [R259 observation electronics BOM integration P0.1](docs/hr-v0-observation-bom-integration-p0.1.md)
- [Interactive R259 observation BOM guide](release/hr-v0/observation-bom-integration-p0.1/index.html)
- [Interactive configuration reconciliation P0.23](release/hr-v0/configuration-reconciliation-p0.23/index.html)
- [R259 independent review request](docs/reviews/2026-08-12-r259-independent-review-request.md)
- [R259 validation record](docs/reviews/2026-08-12-r259-validation-record.md)
- [Sol R12 status after R259](docs/reviews/2026-08-12-sol-r12-post-r259-status.md)
- [R258 deterministic recipient transmission bundles P0.1](docs/hr-v0-lot-a-transmission-bundles-p0.1.md)
- [Interactive R258 bundle and checksum guide](release/hr-v0/lot-a-transmission-bundles-p0.1/index.html)
- [Interactive configuration reconciliation P0.22](release/hr-v0/configuration-reconciliation-p0.22/index.html)
- [R258 independent review request](docs/reviews/2026-08-12-r258-independent-review-request.md)
- [R258 validation record](docs/reviews/2026-08-12-r258-validation-record.md)
- [Sol R12 status after R258](docs/reviews/2026-08-12-sol-r12-post-r258-status.md)
- [R257 exact-feature Lot A inquiry P0.3](docs/hr-v0-lot-a-inquiry-p0.3.md)
- [Interactive R257 inquiry and bid guide](release/hr-v0/lot-a-inquiry-p0.3/index.html)
- [Interactive configuration reconciliation P0.21](release/hr-v0/configuration-reconciliation-p0.21/index.html)
- [R257 independent review request](docs/reviews/2026-08-12-r257-independent-review-request.md)
- [R257 validation record](docs/reviews/2026-08-12-r257-validation-record.md)
- [Sol R12 status after R257](docs/reviews/2026-08-12-sol-r12-post-r257-status.md)
- [R256 source-bound joint measurement definition P0.1](docs/hr-v0-joint-measurement-definition-p0.1.md)
- [Interactive R256 joint feature and measurand guide](release/hr-v0/joint-measurement-definition-p0.1/index.html)
- [Interactive configuration reconciliation P0.20](release/hr-v0/configuration-reconciliation-p0.20/index.html)
- [R256 independent review request](docs/reviews/2026-08-11-r256-independent-review-request.md)
- [R256 validation record](docs/reviews/2026-08-11-r256-validation-record.md)
- [Sol R12 status after R256](docs/reviews/2026-08-11-sol-r12-post-r256-status.md)
- [R255 Lot A supplier and metrology inquiry P0.2](docs/hr-v0-lot-a-inquiry-p0.2.md)
- [Interactive R255 inquiry and decision guide](release/hr-v0/lot-a-inquiry-p0.2/index.html)
- [Interactive configuration reconciliation P0.19](release/hr-v0/configuration-reconciliation-p0.19/index.html)
- [R255 independent review request](docs/reviews/2026-08-11-r255-independent-review-request.md)
- [R255 validation record](docs/reviews/2026-08-11-r255-validation-record.md)
- [Sol R12 status after R255](docs/reviews/2026-08-11-sol-r12-post-r255-status.md)
- [R254 task-specific joint-stack metrology correction](docs/hr-v0-joint-stack-metrology-p0.2.md)
- [Interactive R254 metrology guide](release/hr-v0/joint-stack-metrology-p0.2/index.html)
- [Interactive configuration reconciliation P0.18](release/hr-v0/configuration-reconciliation-p0.18/index.html)
- [R254 independent review request](docs/reviews/2026-08-11-r254-independent-review-request.md)
- [R254 validation record](docs/reviews/2026-08-11-r254-validation-record.md)
- [Sol R12 status after R254](docs/reviews/2026-08-11-sol-r12-post-r254-status.md)
- [R253 rank-6 3-2-1 joint-stack fixture correction](docs/hr-v0-joint-stack-fixture-p0.2.md)
- [Interactive R253 fixture guide](release/hr-v0/joint-stack-fixture-p0.2/index.html)
- [Interactive configuration reconciliation P0.17](release/hr-v0/configuration-reconciliation-p0.17/index.html)
- [R253 independent review request](docs/reviews/2026-08-11-r253-independent-review-request.md)
- [R253 validation record](docs/reviews/2026-08-11-r253-validation-record.md)
- [Sol R12 status after R253](docs/reviews/2026-08-11-sol-r12-post-r253-status.md)
- [R252 zero-energy joint-stack fixture candidate](docs/hr-v0-joint-stack-fixture-p0.1.md)
- [Interactive R252 joint-stack fixture guide](release/hr-v0/joint-stack-fixture-p0.1/index.html)
- [Interactive configuration reconciliation P0.16](release/hr-v0/configuration-reconciliation-p0.16/index.html)
- [R252 independent review request](docs/reviews/2026-08-11-r252-independent-review-request.md)
- [R252 validation record](docs/reviews/2026-08-11-r252-validation-record.md)
- [Sol R12 status after R252](docs/reviews/2026-08-11-sol-r12-post-r252-status.md)
- [R251 first physical shop-session contract](docs/hr-v0-first-shop-session-p0.1.md)
- [Interactive R251 first-shop-session guide](release/hr-v0/first-shop-session-p0.1/index.html)
- [Interactive configuration reconciliation P0.15](release/hr-v0/configuration-reconciliation-p0.15/index.html)
- [R251 independent review request](docs/reviews/2026-08-11-r251-independent-review-request.md)
- [R251 validation record](docs/reviews/2026-08-11-r251-validation-record.md)
- [R250 datum/GD&T qualified-review proposal](docs/hr-v0-gdt-review-p0.1.md)
- [Interactive R250 datum/GD&T guide](release/hr-v0/gdt-review-p0.1/index.html)
- [Interactive configuration reconciliation P0.14](release/hr-v0/configuration-reconciliation-p0.14/index.html)
- [R250 independent review request](docs/reviews/2026-08-11-r250-independent-review-request.md)
- [R250 validation record](docs/reviews/2026-08-11-r250-validation-record.md)
- [R249 accepted-property propagation and stale-analysis control](docs/hr-v0-property-propagation-p0.1.md)
- [Interactive R249 property-propagation guide](release/hr-v0/property-propagation-p0.1/index.html)
- [Interactive configuration reconciliation P0.13](release/hr-v0/configuration-reconciliation-p0.13/index.html)
- [R249 independent review request](docs/reviews/2026-08-11-r249-independent-review-request.md)
- [R249 validation record](docs/reviews/2026-08-11-r249-validation-record.md)
- [Sol R12 status after R249](docs/reviews/2026-08-11-sol-r12-post-r249-status.md)
- [R248 complete moving mass, COM and inertia evidence contract](docs/hr-v0-moving-properties-closure-p0.1.md)
- [Interactive R248 moving-properties guide](release/hr-v0/moving-properties-closure-p0.1/index.html)
- [Interactive configuration reconciliation P0.12](release/hr-v0/configuration-reconciliation-p0.12/index.html)
- [R248 independent review request](docs/reviews/2026-08-11-r248-independent-review-request.md)
- [R248 validation record](docs/reviews/2026-08-11-r248-validation-record.md)
- [Sol R12 status after R248](docs/reviews/2026-08-11-sol-r12-post-r248-status.md)
- [R247 mechanical shop, RFQ and unpowered assembly candidate](docs/hr-v0-mechanical-shop-rfq-assembly-p0.1.md)
- [Interactive R247 mechanical shop/RFQ/assembly guide](release/hr-v0/mechanical-shop-rfq-assembly-p0.1/index.html)
- [Interactive configuration reconciliation P0.11](release/hr-v0/configuration-reconciliation-p0.11/index.html)
- [R247 independent review request](docs/reviews/2026-08-11-r247-independent-review-request.md)
- [R247 validation record](docs/reviews/2026-08-11-r247-validation-record.md)
- [Sol R12 status after R247](docs/reviews/2026-08-11-sol-r12-post-r247-status.md)
- [R245 integrated mechanical and firmware source binding](docs/hr-v0-firmware-mechanical-source-binding-p0.1.md)
- [R246 P1.21 static 24 V voltage budget](docs/hr-v0-p121-static-voltage-budget-p0.1.md)
- [Interactive corrected five-part binding](release/hr-v0/mechanical-bom-binding-p0.3/index.html)
- [Interactive firmware source-binding guide](release/hr-v0/firmware-mechanical-source-binding-p0.1/index.html)
- [R245 independent review request](docs/reviews/2026-08-11-r245-independent-review-request.md)
- [R245 validation record](docs/reviews/2026-08-11-r245-validation-record.md)
- [Sol R12 status after R245](docs/reviews/2026-08-11-sol-r12-post-r245-status.md)
- [R246 independent review request](docs/reviews/2026-08-11-r246-independent-review-request.md)
- [R246 validation record](docs/reviews/2026-08-11-r246-validation-record.md)
- [Sol R12 status after R246](docs/reviews/2026-08-11-sol-r12-post-r246-status.md)
- [R244 P1.21 nominal DCR and voltage-drop screen](docs/hr-v0-p121-dcr-drop-p0.1.md)
- [Interactive DCR and voltage-drop guide](release/hr-v0/p121-dcr-drop-p0.1/index.html)
- [R244 independent review request](docs/reviews/2026-08-11-r244-independent-review-request.md)
- [R244 validation record](docs/reviews/2026-08-11-r244-validation-record.md)
- [Sol R12 status after R244](docs/reviews/2026-08-11-sol-r12-post-r244-status.md)
- [R243 P1.21 endpoint termination evidence](docs/hr-v0-p121-termination-p0.1.md)
- [Interactive termination guide](release/hr-v0/p121-termination-p0.1/index.html)
- [R243 independent review request](docs/reviews/2026-08-11-r243-independent-review-request.md)
- [R243 validation record](docs/reviews/2026-08-11-r243-validation-record.md)
- [Sol R12 status after R243](docs/reviews/2026-08-11-sol-r12-post-r243-status.md)
- [R242 P1.21 conductor and duct-occupancy evidence](docs/hr-v0-p121-conductor-fill-p0.1.md)
- [Interactive conductor and fill guide](release/hr-v0/p121-conductor-fill-p0.1/index.html)
- [R242 independent review request](docs/reviews/2026-08-11-r242-independent-review-request.md)
- [R242 validation record](docs/reviews/2026-08-11-r242-validation-record.md)
- [Sol R12 status after R242](docs/reviews/2026-08-11-sol-r12-post-r242-status.md)
- [R241 P1.21 segregation-hardware candidate](docs/hr-v0-p121-segregation-hardware-p0.1.md)
- [Interactive segregation-hardware guide](release/hr-v0/p121-segregation-hardware-p0.1/index.html)
- [R241 independent review request](docs/reviews/2026-08-11-r241-independent-review-request.md)
- [R241 validation record](docs/reviews/2026-08-11-r241-validation-record.md)
- [R240 P1.21 protected-routing candidate](docs/hr-v0-p121-protected-routing-p0.1.md)
- [Interactive protected-routing guide](release/hr-v0/p121-protected-routing-p0.1/index.html)
- [R240 independent review request](docs/reviews/2026-08-11-r240-independent-review-request.md)
- [R240 validation record](docs/reviews/2026-08-11-r240-validation-record.md)
- [R239 P1.21 project visual review](docs/hr-v0-p121-visual-review-p0.1.md)
- [Interactive changed-sheet review](release/hr-v0/p121-visual-review-p0.1/index.html)
- [R239 independent review request](docs/reviews/2026-08-11-r239-independent-review-request.md)
- [R239 validation record](docs/reviews/2026-08-11-r239-validation-record.md)
- [R238 P1.21 consolidated native-KiCad review candidate](docs/hr-v0-p121-consolidated-review-p0.1.md)
- [Interactive thirteen-sheet P1.21 review guide](release/hr-v0/p121-consolidated-review-p0.1/index.html)
- [R238 independent review request](docs/reviews/2026-08-11-r238-independent-review-request.md)
- [R238 validation record](docs/reviews/2026-08-11-r238-validation-record.md)
- [R237 Lot A source reconciliation P0.1](docs/hr-v0-lot-a-source-reconciliation-p0.1.md)
- [Interactive Lot A purchase-gate guide](release/hr-v0/lot-a-source-reconciliation-p0.1/index.html)
- [R237 independent review request](docs/reviews/2026-08-11-r237-independent-review-request.md)
- [R237 validation record](docs/reviews/2026-08-11-r237-validation-record.md)
- [R236 runtime evidence-log contract P0.1](docs/hr-v0-runtime-evidence-log-p0.1.md)
- [Interactive runtime evidence guide](release/hr-v0/runtime-evidence-log-p0.1/index.html)
- [R236 independent review request](docs/reviews/2026-08-11-r236-independent-review-request.md)
- [R236 validation record](docs/reviews/2026-08-11-r236-validation-record.md)
- [P1.21 manufacturer and no-load evidence route P0.1](docs/hr-v0-p121-application-evidence-p0.1.md)
- [Interactive P1.21 application-evidence guide](release/hr-v0/p121-application-evidence-p0.1/index.html)
- [R235 independent review request](docs/reviews/2026-08-11-r235-independent-review-request.md)
- [R235 validation record](docs/reviews/2026-08-11-r235-validation-record.md)
- [P1.21 SRA1-supply watchdog candidate and R234 disposition](docs/hr-v0-p121-sra1-supply-watchdog-p0.1.md)
- [Interactive P1.21 topology and fault guide](release/hr-v0/p121-sra1-supply-watchdog-p0.1/index.html)
- [R234 independent review request](docs/reviews/2026-08-11-r234-independent-review-request.md)
- [R234 validation record](docs/reviews/2026-08-11-r234-validation-record.md)
- [P1.20 PNOZ/KWD application dossier and R233 disposition](docs/hr-v0-pnoz-kwd-application-p0.2.md)
- [Interactive P1.20 contact-load and fault guide](release/hr-v0/pnoz-kwd-application-p0.2/index.html)
- [R233 independent review request](docs/reviews/2026-08-11-r233-independent-review-request.md)
- [R233 validation record](docs/reviews/2026-08-11-r233-validation-record.md)
- [P1.20 watchdog-interlock candidate and R232 disposition](docs/hr-v0-p120-watchdog-interlock-p0.1.md)
- [Interactive P1.20 topology and fault guide](release/hr-v0/p120-watchdog-interlock-p0.1/index.html)
- [Sol R12 current blocker disposition after R230](docs/sol-r12-current-disposition-r231.md)
- [Interactive Sol R12 blocker register](release/hr-v0/sol-r12-current-disposition-r231/index.html)
- [HR-V0 explicit panel point-to-point candidate P0.1](docs/hr-v0-panel-point-to-point-p0.1.md)
- [Interactive panel point-to-point guide](release/hr-v0/panel-point-to-point-p0.1/index.html)
- [HR-V0 panel node placement and stock allocation P0.1](docs/hr-v0-panel-node-placement-p0.1.md)
- [Interactive panel node-placement guide](release/hr-v0/panel-node-placement-p0.1/index.html)
- [HR-V0 connected-ECAD web review P0.1](docs/hr-v0-ecad-web-review-p0.1.md)
- [Interactive 13-sheet native KiCad viewer](release/hr-v0/ecad-web-review-p1.18-p0.1/index.html)
- [HR-V0 watchdog permit topology proof P0.1](docs/hr-v0-watchdog-permit-topology-p0.1.md)
- [Interactive watchdog permit and welded-contact guide](release/hr-v0/watchdog-permit-topology-p0.1/index.html)
- [HR-V0 K1/K2 contactor application P0.3](docs/hr-v0-contactor-application-p0.3.md)
- [Interactive current-baseline contactor guide](release/hr-v0/contactor-application-p0.3/index.html)
- [Interactive current configuration reconciliation P0.4](release/hr-v0/configuration-reconciliation-p0.4/index.html)
- [Current HR-V0 mechanical manufacturing-review package P0.1](docs/hr-v0-mechanical-manufacturing-review-p0.1.md)
- [Interactive mechanical manufacturing-review guide](release/hr-v0/mechanical-manufacturing-review-p0.1/index.html)
- [Current Boston fabrication route P0.4](docs/hr-v0-boston-fabrication-decision-p0.4.md)
- [Interactive Boston fabrication route guide](release/hr-v0/boston-fabrication-route-p0.4/index.html)
- [HR-V0 carrier-integrated configuration reconciliation P0.1](docs/hr-v0-configuration-reconciliation-p0.1.md)
- [Interactive carrier-integrated configuration guide](release/hr-v0/configuration-reconciliation-p0.1/index.html)
- [Current P0.2 DXL-star manufacturing review](docs/hr-v0-dxl-star-manufacturing-p0.2.md)
- [Interactive P0.2 DXL-star CAM review guide](release/hr-v0/dxl-star-manufacturing-p0.2/index.html)
- [Configuration management and revision hierarchy](docs/configuration-management.md)
- [HR-V0 deterministic release-candidate configuration P0.1](docs/hr-v0-release-candidate-p0.1.md)
- [HR-V0 integrated arm architecture P0.7](docs/hr-v0-arm-architecture-p0.7.md)
- [HR-V0 integrated X430 arm comparison P0.9](docs/hr-v0-x430-integrated-arm-p0.9.md)
- [Interactive P0.9 full-arm review guide](release/hr-v0/arm-architecture-p0.9-x430/index.html)
- [HR-V0 X430 arm clearance candidate P1.0](docs/hr-v0-x430-arm-p1.0.md)
- [Interactive P1.0 stop-clearance review guide](release/hr-v0/arm-architecture-p1.0-x430-clearance/index.html)
- [HR-V0 X430 lowered-forearm candidate P1.1](docs/hr-v0-x430-lowered-forearm-p1.1.md)
- [Interactive P1.1 lowered-forearm review guide](release/hr-v0/arm-architecture-p1.1-x430-lowered-forearm/index.html)
- [HR-V0 P1.1 X430 load basis](docs/hr-v0-x430-load-basis-p1.1.md)
- [Interactive P1.1 load and stop-sensitivity guide](release/hr-v0/arm-load-basis-p1.1-x430/index.html)
- [HR-V0 FR12 moving-subassembly mass metrology P0.1](docs/hr-v0-fr12-moving-mass-metrology-p0.1.md)
- [Interactive FR12 mass-metrology guide](release/hr-v0/fr12-moving-mass-metrology-p0.1/index.html)
- [HR-V0 X430 continuous/cyclic duty characterization P0.1](docs/hr-v0-x430-duty-characterization-p0.1.md)
- [Interactive X430 duty-characterization guide](release/hr-v0/x430-duty-characterization-p0.1/index.html)
- [HR-V0 same-interface mass-reduction study P0.1](docs/hr-v0-mass-reduction-study-p0.1.md)
- [HR-V0 elbow actuator and moving-mass trade P0.1](docs/hr-v0-elbow-actuator-trade-p0.1.md)
- [Interactive elbow and mass decision guide](release/hr-v0/elbow-actuator-trade-p0.1/index.html)
- [HR-V0 integrated mechanical release candidate P0.6](docs/hr-v0-mechanical-release-p0.6.md)
- [HR-V0 hard-stop design basis P0.3](docs/hr-v0-hard-stop-design-basis-p0.3.md)
- [HR-V0 hard-stop region clearance and interface acquisition P0.1](docs/hr-v0-stop-region-clearance-p0.1.md)
- [HR-V0 unpowered J1/J2 acquisition and metrology P0.1](docs/hr-v0-joint-stack-metrology-p0.1.md)
- [HR-V0 evaluation acquisition and Boston metrology quote packet P0.1](docs/hr-v0-evaluation-acquisition-metrology-p0.1.md)
- [HR-V0 watchdog dependent-failure and common-cause analysis P0.1](docs/hr-v0-watchdog-common-cause-p0.1.md)
- [HR-V0 watchdog-gated SR1 supply correction P0.1](docs/hr-v0-watchdog-supply-gate-p0.1.md)
- [Interactive watchdog supply-gate correction guide](safety/hr-v0-watchdog-supply-gate-p0.1/index.html)
- [HR-V0 firmware implementation candidate P0.4](docs/hr-v0-firmware-p0.4.md)
- [HR-V0 conservative kinematic speed bound P0.1](docs/hr-v0-kinematic-speed-bound-p0.1.md)
- [Interactive kinematic speed-bound calculator](release/hr-v0/kinematic-speed-bound-p0.1/index.html)
- [HR-V0 runtime execution boundary P0.1](docs/hr-v0-runtime-execution-boundary-p0.1.md)
- [HR-V0 runtime backend source candidates P0.1](docs/hr-v0-runtime-backends-p0.1.md)
- [HR-V0 Raspberry Pi observation pin map P0.1](docs/hr-v0-runtime-observation-pi-pinmap-p0.1.md)
- [Interactive Raspberry Pi observation pin-map guide](release/hr-v0/runtime-observation-pi-pinmap-p0.1/index.html)
- [HR-V0 Raspberry Pi observation interface carrier P0.1](docs/hr-v0-pi-observation-carrier-p0.1.md)
- [Interactive Raspberry Pi observation carrier and harness guide](release/hr-v0/pi-observation-carrier-p0.1/index.html)
- [HR-V0 fail-closed host deployment candidate P0.1](docs/hr-v0-host-deployment-p0.1.md)
- [Interactive host deployment guide](release/hr-v0/host-deployment-p0.1/index.html)
- [HR-V0 Raspberry Pi OS publisher-SBOM lock P0.1](docs/hr-v0-rpi-os-sbom-p0.1.md)
- [Interactive Raspberry Pi OS SBOM guide](release/hr-v0/rpi-os-sbom-p0.1/index.html)
- [HR-V0 DYNAMIXEL transport candidate P0.3](docs/hr-v0-dynamixel-transport-p0.3.md)
- [HR-V0 E2 control-only commissioning package P0.1](docs/hr-v0-e2-control-only-energization-p0.1.md)
- [HR-V0 E2 evidence parity contract P0.2](docs/hr-v0-e2-evidence-parity-p0.2.md)
- [Interactive E2 evidence guide](release/hr-v0/e2-evidence-parity-p0.2/index.html)
- [HR-V0 BOM closure and evaluation boundary P0.1](docs/hr-v0-bom-closure-p0.1.md)
- [HR-V0 Evaluation Batch A candidates](bom/hr-v0-evaluation-batch-a.csv)
- [HR-V0 unpowered mechanical evaluation subset P0.1](docs/hr-v0-unpowered-mechanical-evaluation-p0.1.md)
- [HR-V0 mechanical release coordination P0.2](docs/hr-v0-mechanical-release-p0.2.md)
- [HR-V0 web-readable general arrangement](cad/hr-v0/generated/assembly/HR-V0_general-arrangement.svg)
- [Current engineering handoff](docs/handoff-current.md)
- [Complete review ledger](docs/review-ledger.md)
- [System specification](docs/system-specification.md)
- [30-inch product specification](docs/full-body-specification.md)
- [Dimension-control specification](docs/dimension-control.md)
- [Full-body load and power budget](docs/full-body-loads.md)
- [R11 independent engineering calculations](docs/r11-engineering-calculations.md)
- [Sub-meter humanoid benchmark](docs/architecture-benchmark.md)
- [Walking-system specification](docs/walking-system.md)
- [Walking verification matrix](docs/walking-verification.md)
- [Mechanical concept and load model](docs/mechanical.md)
- [HR-V0 native CAD, RFQ geometry and first-article controls](cad/hr-v0/README.md)
- [HR-V0 Mechanical R0.1 historical baseline (superseded arm)](docs/hr-v0-mechanical-r0.1.md)
- [HR-V0 flat-plate manufacturing P0.1 (withdrawn by R53)](docs/hr-v0-flat-plate-manufacturing-p0.1.md)
- [HR-V0 Boston fabrication and RFQ route P0.1](docs/hr-v0-boston-fabrication-route-p0.1.md)
- [HR-V0 deterministic fabrication capability/DFM packets P0.1](docs/hr-v0-fabrication-rfi-p0.1.md)
- [HR-V0 Boston bench survey and anchor-release procedure P0.1](docs/hr-v0-bench-survey-p0.1.md)
- [HR-V0 PCD22 fit-coupon procedure P0.1](docs/hr-v0-fit-coupon-procedure-p0.1.md)
- [HR-V0 S102 fit-coupon procedure P0.1](docs/hr-v0-s102-fit-procedure-p0.1.md)
- [HR-V0 gripper architecture and exact-source integration inputs P0.2](docs/hr-v0-gripper-architecture-p0.2.md)
- [HR-V0 gripper-kit contents schedule](bom/hr-v0-gripper-kit-contents.csv)
- [HR-V0 guard, receiver and moving-cable architecture P0.1](docs/hr-v0-guard-receiver-cable-p0.1.md)
- [HR-V0 catalog-bound fixed guard and receiver candidate P0.3](docs/hr-v0-fixed-guard-receiver-p0.3.md)
- [HR-V0 guard retention and mass evaluation study P0.1](docs/hr-v0-guard-retention-mass-study-p0.1.md)
- [HR-V0 guard impact-energy basis P0.1](docs/hr-v0-guard-impact-basis-p0.1.md)
- [HR-V0 passive power-loss containment P0.1](docs/hr-v0-power-loss-containment-p0.1.md)
- [Interactive power-loss containment guide](release/hr-v0/power-loss-containment-p0.1/index.html)
- [HR-V0 continuous collapse-envelope and receiver-role correction P0.1](docs/hr-v0-collapse-envelope-p0.1.md)
- [Interactive collapse-envelope guide](release/hr-v0/collapse-envelope-p0.1/index.html)
- [HR-V0 passive arm-receiver candidate P0.1](docs/hr-v0-passive-arm-receiver-p0.1.md)
- [Interactive passive arm-receiver guide](release/hr-v0/passive-arm-receiver-p0.1/index.html)
- [HR-V0 passive arm-receiver second-method verification P0.1](docs/hr-v0-passive-arm-receiver-verification-p0.1.md)
- [Interactive passive arm-receiver verification guide](release/hr-v0/passive-arm-receiver-verification-p0.1/index.html)
- [HR-V0 dimensioned fixed guard and receiver candidate P0.2 (superseded)](docs/hr-v0-fixed-guard-receiver-p0.2.md)
- [HR-V0 joint-interface and fastener evidence basis](docs/hr-v0-joint-interface-fasteners-p0.1.md)
- [HR-V0 hard-stop design basis P0.1](docs/hr-v0-hard-stop-design-basis-p0.1.md)
- [HR-V0 hard-stop validation procedure P0.1](docs/hr-v0-hard-stop-validation-p0.1.md)
- [HR-V0 frame-kit contents schedule](bom/hr-v0-frame-kit-contents.csv)
- [Electrical and safety architecture](docs/electrical.md)
- [Safety-function requirements](docs/safety-functions.md)
- [HR-V0 functional-safety allocation and diagnostic-credit boundary P0.1](docs/hr-v0-functional-safety-allocation-p0.1.md)
- [HR-V0 measurable safety-requirements candidate P0.2](docs/hr-v0-safety-requirements-p0.2.md)
- [Interactive HR-V0 safety-requirements guide](release/hr-v0/safety-requirements-p0.2/index.html)
- [HR-V0 functional-safety reviewer route P0.1](docs/hr-v0-functional-safety-review-route-p0.1.md)
- [Interactive functional-safety reviewer-route guide](release/hr-v0/functional-safety-review-route-p0.1/index.html)
- [HR-V0 current control-panel configuration P0.1](docs/hr-v0-control-panel-configuration-p0.1.md)
- [Interactive current panel-configuration guide](release/hr-v0/control-panel-configuration-p0.1/index.html)
- [Actuator and harness interface constraints](docs/actuator-interface.md)
- [Native KiCad Electrical V2.1 source](electrical/kicad/project-button-v2/README.md)
- [Native KiCad Electrical V3-P1.15 carrier-aware candidate](electrical/kicad/project-button-v3-p1.15-carrier-candidate/README.md)
- [HR-V0 control-panel physical-definition candidate P0.5](docs/hr-v0-control-panel-p0.5.md)
- [HR-V0 24 V source-interface candidate P0.2](docs/hr-v0-24v-interface-p0.2.md)
- [HR-V0 compute-heartbeat and watchdog-debug interface P0.1](docs/hr-v0-compute-debug-interface-p0.1.md)
- [HR-V0 exact compute and compute-power candidates P0.1](docs/hr-v0-compute-selection-p0.1.md)
- [Interactive compute selection guide](release/hr-v0/compute-selection-p0.1/index.html)
- [HR-V0 compute subassembly candidate P0.1](docs/hr-v0-compute-subassembly-p0.1.md)
- [Interactive compute subassembly guide](release/hr-v0/compute-subassembly-p0.1/index.html)
- [HR-V0 control-panel and compute-installation candidate P0.6](docs/hr-v0-control-panel-p0.6.md)
- [Interactive compute installation guide](release/hr-v0/compute-installation-p0.1/index.html)
- [E2 control-only hardware slice P0.2](electrical/e2/hr-v0-e2-hardware-p0.2/HR-V0_e2-hardware-guide.html)
- [Native KiCad DXL-STAR-P0.2 carrier-aware candidate](electrical/kicad/hr-v0-dxl-star-p0.2-carrier-candidate/README.md)
- [HR-V0 DYNAMIXEL star-injection evidence basis](docs/hr-v0-dxl-star-injection-p0.1.md)
- [HR-V0 DYNAMIXEL star manufacturing review package P0.1](docs/hr-v0-dxl-star-manufacturing-p0.1.md)
- [Interactive DYNAMIXEL star manufacturing review guide](release/hr-v0/dxl-star-manufacturing-p0.1/index.html)
- [HR-V0 Electrical V3 candidate architecture](docs/hr-v0-electrical-v3-candidate.md)
- [HR-V0 Electrical terminal closure R27](docs/hr-v0-electrical-terminal-closure-r27.md)
- [HR-V0 RESET/ARM received-lot closure P0.1](docs/hr-v0-reset-arm-receiving-p0.1.md)
- [HR-V0 source-interface closure R28](docs/hr-v0-source-interface-closure-r28.md)
- [HR-V0 heartbeat and relay-driver closure R29](docs/hr-v0-heartbeat-driver-closure-r29.md)
- [HR-V0 watchdog-feedback passive closure R30](docs/hr-v0-watchdog-feedback-passive-closure-r30.md)
- [HR-V0 watchdog PCB constrained-placement candidate P0.2](docs/hr-v0-watchdog-pcb-p0.2.md)
- [HR-V0 watchdog PCB routed-copper candidate P0.3](docs/hr-v0-watchdog-pcb-p0.3.md)
- [HR-V0 watchdog PCB test-access candidate P0.4](docs/hr-v0-watchdog-pcb-p0.4.md)
- [HR-V0 watchdog PCB fabrication-envelope candidate P0.5](docs/hr-v0-watchdog-pcb-p0.5.md)
- [HR-V0 watchdog PCB land-pattern and assembly-process correction P0.1 / PCB-P0.6](docs/hr-v0-watchdog-pcb-land-pattern-p0.1.md)
- [Interactive PCB-P0.6 reference audit](release/hr-v0/watchdog-pcb-land-pattern-audit-p0.1/index.html)
- [HR-V0 protection and conductor coordination P0.4](docs/hr-v0-protection-coordination-p0.4.md)
- [HR-V0 DC service-disconnect candidate P0.2](docs/hr-v0-service-disconnect-p0.2.md)
- [HR-V0 actuator current and torque envelope P0.1](docs/hr-v0-actuator-current-envelope-p0.1.md)
- [HR-V0 Boston build-site basis](docs/hr-v0-build-site-basis.md)
- [Boston fabrication and custom-metal sourcing](docs/hr-v0-fabrication-sourcing-boston.md)
- [Boston custom-metal decision package P0.2](docs/hr-v0-boston-fabrication-decision-p0.2.md)
- [Interactive Boston fabrication route guide](release/hr-v0/boston-fabrication-route-p0.2/index.html)
- [R167 Boston/US custom-metal route P0.3](docs/hr-v0-boston-fabrication-decision-p0.3.md)
- [R167 interactive fabrication route guide](release/hr-v0/boston-fabrication-route-p0.3/index.html)
- [Control and fault-state specification](docs/control.md)
- [HR-V0 Firmware P0.1 implementation candidate](docs/hr-v0-firmware-p0.1.md)
- [HR-V0 watchdog hardware interface P0.2](docs/hr-v0-watchdog-interface-p0.2.md)
- [HR-V0 calculated watchdog feedback receiver P0.1](docs/hr-v0-watchdog-feedback-p0.1.md)
- [HR-V0 watchdog build and compiled-C evidence P0.2](docs/hr-v0-watchdog-build-p0.2.md)
- [HR-V0 firmware implementation candidate P0.2](docs/hr-v0-firmware-p0.2.md)
- [HR-V0 DYNAMIXEL transport and execution boundary P0.1](docs/hr-v0-dynamixel-transport-p0.1.md)
- [HR-V0 Pico watchdog historical build P0.1](docs/hr-v0-watchdog-build-p0.1.md)
- [Firmware source area](firmware/README.md)
- [Verification plan](docs/verification.md)
- [Verification scope and applicability](docs/verification-scope.md)
- [Verification procedure registry](tests/procedures/procedure-registry.csv)
- [Open decisions](docs/open-decisions.md)
- [Evidence maturity dashboard](docs/evidence-maturity.md)
- [HR-V0 moving-mass closure screen](docs/hr-v0-moving-mass-closure-p0.1.md)
- [HR-V0 moving-mass ledger](bom/hr-v0-moving-mass-ledger.csv)
- [Independent review disposition](docs/independent-review-disposition.md)
- [Fable R11 review and disposition](docs/reviews/2026-08-06-fable-review-disposition.md)
- [Sol R12 review and disposition](docs/reviews/2026-08-06-sol-r12-review-disposition.md)
- [Sol R12 findings rechecked against R17](docs/reviews/2026-08-06-sol-r12-post-r17-status.md)
- [Sol R12 findings rechecked against R18](docs/reviews/2026-08-06-sol-r12-post-r18-status.md)
- [Sol R12 findings rechecked against R19](docs/reviews/2026-08-06-sol-r12-post-r19-status.md)
- [Sol R12 findings rechecked against R20](docs/reviews/2026-08-06-sol-r12-post-r20-status.md)
- [Sol R12 findings rechecked against R21](docs/reviews/2026-08-06-sol-r12-post-r21-status.md)
- [Sol R12 findings rechecked against R22](docs/reviews/2026-08-06-sol-r12-post-r22-status.md)
- [Sol R12 findings rechecked against R23](docs/reviews/2026-08-06-sol-r12-post-r23-status.md)
- [Sol R12 findings rechecked against R24](docs/reviews/2026-08-06-sol-r12-post-r24-status.md)
- [Sol R12 findings rechecked against R25](docs/reviews/2026-08-06-sol-r12-post-r25-status.md)
- [Sol R12 findings rechecked against R26](docs/reviews/2026-08-06-sol-r12-post-r26-status.md)
- [Sol R12 findings rechecked against R27](docs/reviews/2026-08-06-sol-r12-post-r27-status.md)
- [Sol R12 findings rechecked against R28](docs/reviews/2026-08-06-sol-r12-post-r28-status.md)
- [Sol R12 findings rechecked against R29](docs/reviews/2026-08-06-sol-r12-post-r29-status.md)
- [Sol R12 findings rechecked against R30](docs/reviews/2026-08-06-sol-r12-post-r30-status.md)
- [Sol R12 findings rechecked against R31](docs/reviews/2026-08-06-sol-r12-post-r31-status.md)
- [Sol R12 findings rechecked against R32](docs/reviews/2026-08-06-sol-r12-post-r32-status.md)
- [Sol R12 findings rechecked against R33](docs/reviews/2026-08-06-sol-r12-post-r33-status.md)
- [Sol R12 findings rechecked against R34](docs/reviews/2026-08-06-sol-r12-post-r34-status.md)
- [Sol R12 findings rechecked against R35](docs/reviews/2026-08-06-sol-r12-post-r35-status.md)
- [Sol R12 findings rechecked against R36](docs/reviews/2026-08-06-sol-r12-post-r36-status.md)
- [Sol R12 findings rechecked against R37](docs/reviews/2026-08-07-sol-r12-post-r37-status.md)
- [Sol supplied review summary](docs/reviews/2026-08-07-sol-independent-engineering-review-summary.md)
- [Sol R12 findings rechecked against R38](docs/reviews/2026-08-07-sol-r12-post-r38-status.md)
- [Sol R12 findings rechecked against R39](docs/reviews/2026-08-07-sol-r12-post-r39-status.md)
- [Sol R12 findings rechecked against R40](docs/reviews/2026-08-07-sol-r12-post-r40-status.md)
- [Sol R12 findings rechecked against R41](docs/reviews/2026-08-07-sol-r12-post-r41-status.md)
- [Sol R12 findings rechecked against R42](docs/reviews/2026-08-07-sol-r12-post-r42-status.md)
- [Sol R12 findings rechecked against R43](docs/reviews/2026-08-07-sol-r12-post-r43-status.md)
- [Sol R12 findings rechecked against R44](docs/reviews/2026-08-07-sol-r12-post-r44-status.md)
- [Sol R12 findings rechecked against R45](docs/reviews/2026-08-07-sol-r12-post-r45-status.md)
- [Sol R12 findings rechecked against R46](docs/reviews/2026-08-07-sol-r12-post-r46-status.md)
- [Sol R12 findings rechecked against R47](docs/reviews/2026-08-07-sol-r12-post-r47-status.md)
- [Sol R12 findings rechecked against R49](docs/reviews/2026-08-07-sol-r12-post-r49-status.md)
- [Sol R12 findings rechecked against R50](docs/reviews/2026-08-07-sol-r12-post-r50-status.md)
- [Sol R12 findings rechecked against R51](docs/reviews/2026-08-07-sol-r12-post-r51-status.md)
- [Sol R12 findings rechecked against R52](docs/reviews/2026-08-07-sol-r12-post-r52-status.md)
- [R53 exact-frame supersession and Sol R12 reconciliation](docs/reviews/2026-08-07-sol-r12-post-r53-status.md)
- [R54 exact-coordinate arm candidate and Sol R12 reconciliation](docs/reviews/2026-08-07-sol-r12-post-r54-status.md)
- [R55 corrected arm architecture and Sol R12 reconciliation](docs/reviews/2026-08-07-sol-r12-post-r55-status.md)
- [R56 strengthened adapter/fastener stack and Sol R12 reconciliation](docs/reviews/2026-08-07-sol-r12-post-r56-status.md)
- [R57 adapter fabrication-definition and Sol R12 reconciliation](docs/reviews/2026-08-07-sol-r12-post-r57-status.md)
- [R58 E2 control-only commissioning boundary and Sol R12 reconciliation](docs/reviews/2026-08-07-sol-r12-post-r58-status.md)
- [R59 current Boston fabrication-sourcing reconciliation](docs/reviews/2026-08-07-sol-r12-post-r59-status.md)
- [R60 control-panel physical-definition reconciliation](docs/reviews/2026-08-07-sol-r12-post-r60-status.md)
- [R61 H1 pilot-light selection and terminal-placeholder reconciliation](docs/reviews/2026-08-07-sol-r12-post-r61-status.md)
- [R62 panel-fit and protection-holder reconciliation](docs/reviews/2026-08-07-sol-r12-post-r62-status.md)
- [R63 end-cover and service-disconnect reconciliation](docs/reviews/2026-08-07-sol-r12-post-r63-status.md)
- [R64 exact SD1 and control-panel reconciliation](docs/reviews/2026-08-07-sol-r12-post-r64-status.md)
- [R65 DYNAMIXEL transport reconciliation](docs/reviews/2026-08-07-sol-r12-post-r65-status.md)
- [HR-V0 control-panel physical-definition candidate](docs/hr-v0-control-panel-p0.4.md)
- [HR-V0 H1 receiving and characterization procedure](docs/hr-v0-h1-receiving-p0.1.md)
- [Electrical V3 independent review request](docs/reviews/2026-08-06-electrical-v3-independent-review-request.md)
- [Current 24 V interface P0.2 independent review request](docs/reviews/2026-08-08-24v-interface-p0.2-independent-review-request.md)
- [Current compute/debug interface P0.1 independent review request](docs/reviews/2026-08-08-compute-debug-interface-p0.1-independent-review-request.md)
- [R82 validation record](docs/reviews/2026-08-08-r82-validation-record.md)
- [Sol R12 findings rechecked after R82](docs/reviews/2026-08-08-sol-r12-post-r82-status.md)
- [R83 hard-stop region validation record](docs/reviews/2026-08-08-r83-validation-record.md)
- [R83 hard-stop region independent review request](docs/reviews/2026-08-08-stop-region-p0.1-independent-review-request.md)
- [Sol R12 findings rechecked after R83](docs/reviews/2026-08-08-sol-r12-post-r83-status.md)
- [R89 watchdog PCB land-pattern validation record](docs/reviews/2026-08-08-r89-validation-record.md)
- [R89 watchdog PCB land-pattern independent review request](docs/reviews/2026-08-08-watchdog-pcb-land-pattern-p0.1-independent-review-request.md)
- [Sol R12 findings rechecked after R89](docs/reviews/2026-08-08-sol-r12-post-r89-status.md)
- [R90 Boston fabrication-route validation record](docs/reviews/2026-08-08-r90-validation-record.md)
- [R90 Boston fabrication-route independent review request](docs/reviews/2026-08-08-boston-fabrication-route-p0.2-independent-review-request.md)
- [Sol R12 findings rechecked after R90](docs/reviews/2026-08-08-sol-r12-post-r90-status.md)
- [R91 elbow/mass architecture validation record](docs/reviews/2026-08-08-r91-validation-record.md)
- [R91 elbow/mass independent review request](docs/reviews/2026-08-08-elbow-actuator-trade-p0.1-independent-review-request.md)
- [Sol R12 findings rechecked after R91](docs/reviews/2026-08-08-sol-r12-post-r91-status.md)
- [R92 X430 elbow P0.8 design record](docs/hr-v0-x430-elbow-architecture-p0.8.md)
- [R92 X430 elbow P0.8 interactive guide](release/hr-v0/elbow-architecture-p0.8/index.html)
- [R92 validation record](docs/reviews/2026-08-08-r92-validation-record.md)
- [R92 independent review request](docs/reviews/2026-08-08-x430-elbow-p0.8-independent-review-request.md)
- [Sol R12 findings rechecked after R92](docs/reviews/2026-08-08-sol-r12-post-r92-status.md)
- [R93 integrated X430 arm P0.9 design record](docs/hr-v0-x430-integrated-arm-p0.9.md)
- [R93 integrated X430 arm interactive guide](release/hr-v0/arm-architecture-p0.9-x430/index.html)
- [R93 validation record](docs/reviews/2026-08-08-r93-validation-record.md)
- [R93 independent review request](docs/reviews/2026-08-08-x430-integrated-arm-p0.9-independent-review-request.md)
- [Sol R12 findings rechecked after R93](docs/reviews/2026-08-08-sol-r12-post-r93-status.md)
- [R94 X430 arm P1.0 clearance record](docs/hr-v0-x430-arm-p1.0.md)
- [R94 P1.0 interactive guide](release/hr-v0/arm-architecture-p1.0-x430-clearance/index.html)
- [R94 validation record](docs/reviews/2026-08-08-r94-validation-record.md)
- [R94 independent review request](docs/reviews/2026-08-08-x430-arm-p1.0-independent-review-request.md)
- [Sol R12 findings rechecked after R94](docs/reviews/2026-08-08-sol-r12-post-r94-status.md)
- [R95 X430 lowered-forearm P1.1 record](docs/hr-v0-x430-lowered-forearm-p1.1.md)
- [R95 P1.1 interactive guide](release/hr-v0/arm-architecture-p1.1-x430-lowered-forearm/index.html)
- [R95 validation record](docs/reviews/2026-08-08-r95-validation-record.md)
- [R95 independent review request](docs/reviews/2026-08-08-x430-lowered-forearm-p1.1-independent-review-request.md)
- [Sol R12 findings rechecked after R95](docs/reviews/2026-08-08-sol-r12-post-r95-status.md)
- [R96 P1.1 X430 load-basis validation record](docs/reviews/2026-08-08-r96-validation-record.md)
- [R96 P1.1 X430 load-basis independent review request](docs/reviews/2026-08-08-x430-load-basis-p1.1-independent-review-request.md)
- [Sol R12 findings rechecked after R96](docs/reviews/2026-08-08-sol-r12-post-r96-status.md)
- [R97 FR12 moving-mass validation record](docs/reviews/2026-08-08-r97-validation-record.md)
- [R97 FR12 moving-mass independent review request](docs/reviews/2026-08-08-fr12-moving-mass-metrology-p0.1-independent-review-request.md)
- [Sol R12 findings rechecked after R97](docs/reviews/2026-08-08-sol-r12-post-r97-status.md)
- [R98 X430 duty-characterization validation record](docs/reviews/2026-08-08-r98-validation-record.md)
- [R98 X430 duty-characterization independent review request](docs/reviews/2026-08-08-x430-duty-characterization-p0.1-independent-review-request.md)
- [Sol R12 findings rechecked after R98](docs/reviews/2026-08-08-sol-r12-post-r98-status.md)
- [R99 X430 duty-fixture topology record](docs/hr-v0-x430-duty-fixture-p0.1.md)
- [R99 interactive X430 duty-fixture guide](release/hr-v0/x430-duty-fixture-p0.1/index.html)
- [R99 X430 duty-fixture validation record](docs/reviews/2026-08-08-r99-validation-record.md)
- [R99 X430 duty-fixture independent review request](docs/reviews/2026-08-08-x430-duty-fixture-p0.1-independent-review-request.md)
- [Sol R12 findings rechecked after R99](docs/reviews/2026-08-08-sol-r12-post-r99-status.md)
- [R100 X430 duty-fixture adapter-interface record](docs/hr-v0-x430-duty-fixture-interface-p0.2.md)
- [R100 interactive adapter-interface guide](release/hr-v0/x430-duty-fixture-p0.2/index.html)
- [R100 validation record](docs/reviews/2026-08-08-r100-validation-record.md)
- [R100 independent review request](docs/reviews/2026-08-08-x430-duty-fixture-interface-p0.2-independent-review-request.md)
- [Sol R12 findings rechecked after R100](docs/reviews/2026-08-08-sol-r12-post-r100-status.md)
- [R101 X430 fixture-support route](docs/hr-v0-x430-fixture-support-p0.1.md)
- [R101 interactive fixture-support guide](release/hr-v0/x430-fixture-support-p0.1/index.html)
- [R101 validation record](docs/reviews/2026-08-08-r101-validation-record.md)
- [R101 independent review request](docs/reviews/2026-08-08-x430-fixture-support-p0.1-independent-review-request.md)
- [Sol R12 findings rechecked after R101](docs/reviews/2026-08-08-sol-r12-post-r101-status.md)
- [R102 horizontal X430 load-rig route](docs/hr-v0-x430-load-rig-p0.1.md)
- [R102 interactive load-rig guide](release/hr-v0/x430-load-rig-p0.1/index.html)
- [R102 validation record](docs/reviews/2026-08-08-r102-validation-record.md)
- [R102 independent review request](docs/reviews/2026-08-08-x430-load-rig-p0.1-independent-review-request.md)
- [Sol R12 findings rechecked after R102](docs/reviews/2026-08-08-sol-r12-post-r102-status.md)
- [R103 X430 output-interface record](docs/hr-v0-x430-output-interface-p0.1.md)
- [R103 interactive output-interface guide](release/hr-v0/x430-output-interface-p0.1/index.html)
- [R103 validation record](docs/reviews/2026-08-08-r103-validation-record.md)
- [R103 independent review request](docs/reviews/2026-08-08-x430-output-interface-p0.1-independent-review-request.md)
- [Sol R12 findings rechecked after R103](docs/reviews/2026-08-08-sol-r12-post-r103-status.md)
- [R104 X430 brake-support and PT erratum record](docs/hr-v0-x430-brake-support-p0.1.md)
- [R104 interactive brake-support guide](release/hr-v0/x430-brake-support-p0.1/index.html)
- [R104 validation record](docs/reviews/2026-08-08-r104-validation-record.md)
- [R104 independent review request](docs/reviews/2026-08-08-x430-brake-support-p0.1-independent-review-request.md)
- [Sol R12 findings rechecked after R104](docs/reviews/2026-08-08-sol-r12-post-r104-status.md)
- [R105 FX104-C01 fabrication-candidate record](docs/hr-v0-fx104-c01-fabrication-candidate-p0.1.md)
- [R105 interactive adapter guide](release/hr-v0/fx104-c01-p0.1/index.html)
- [R105 validation record](docs/reviews/2026-08-08-r105-validation-record.md)
- [R105 independent review request](docs/reviews/2026-08-08-fx104-c01-p0.1-independent-review-request.md)
- [Sol R12 findings rechecked after R105](docs/reviews/2026-08-08-sol-r12-post-r105-status.md)
- [R106 FX103 two-piece output-adapter record](docs/hr-v0-fx103-output-adapter-fabrication-candidate-p0.2.md)
- [R106 interactive output-adapter guide](release/hr-v0/fx103-output-adapter-p0.2/index.html)
- [R106 validation record](docs/reviews/2026-08-08-r106-validation-record.md)
- [R106 independent review request](docs/reviews/2026-08-08-fx103-output-adapter-p0.2-independent-review-request.md)
- [Sol R12 findings rechecked after R106](docs/reviews/2026-08-08-sol-r12-post-r106-status.md)
- [R107 FX103 fastener-stack correction](docs/hr-v0-fx103-output-adapter-fabrication-candidate-p0.3.md)
- [R107 interactive output-adapter guide](release/hr-v0/fx103-output-adapter-p0.3/index.html)
- [R107 validation record](docs/reviews/2026-08-08-r107-validation-record.md)
- [R107 independent review request](docs/reviews/2026-08-08-fx103-output-adapter-p0.3-independent-review-request.md)
- [Sol R12 findings rechecked after R107](docs/reviews/2026-08-08-sol-r12-post-r107-status.md)
- [R108 gripper acquisition correction](docs/hr-v0-gripper-acquisition-correction-p0.2.md)
- [R108 gripper acquisition web guide](release/hr-v0/gripper-acquisition-p0.2/index.html)
- [R108 validation record](docs/reviews/2026-08-08-r108-validation-record.md)
- [R108 independent review request](docs/reviews/2026-08-08-gripper-acquisition-p0.2-independent-review-request.md)
- [Sol R12 findings rechecked after R108](docs/reviews/2026-08-08-sol-r12-post-r108-status.md)
- [R109 official gripper-frame source correction](docs/hr-v0-gripper-frame-source-correction-p0.3.md)
- [R109 interactive source guide](release/hr-v0/gripper-frame-source-p0.3/index.html)
- [R109 validation record](docs/reviews/2026-08-08-r109-validation-record.md)
- [R109 independent review request](docs/reviews/2026-08-08-gripper-frame-source-p0.3-independent-review-request.md)
- [Sol R12 findings rechecked after R109](docs/reviews/2026-08-08-sol-r12-post-r109-status.md)
- [R110 gripper source-route correction](docs/hr-v0-gripper-source-route-correction-p0.4.md)
- [R110 interactive source-route guide](release/hr-v0/gripper-source-route-p0.4/index.html)
- [R110 validation record](docs/reviews/2026-08-08-r110-validation-record.md)
- [R110 independent review request](docs/reviews/2026-08-08-gripper-source-route-p0.4-independent-review-request.md)
- [Sol R12 findings rechecked after R110](docs/reviews/2026-08-08-sol-r12-post-r110-status.md)
- [R111 source-controlled gripper alternative trade study](docs/hr-v0-gripper-alternative-trade-p0.1.md)
- [R111 interactive candidate guide](release/hr-v0/gripper-alternative-p0.1/index.html)
- [R111 validation record](docs/reviews/2026-08-08-r111-validation-record.md)
- [R111 independent review request](docs/reviews/2026-08-08-gripper-alternative-p0.1-independent-review-request.md)
- [Sol R12 findings rechecked after R111](docs/reviews/2026-08-08-sol-r12-post-r111-status.md)
- [R112 direct gripper adapter candidate](docs/hr-v0-pololu-gripper-adapter-p0.1.md)
- [R112 interactive 3D adapter guide](release/hr-v0/gripper-adapter-p0.1/index.html)
- [R112 native KiCad gripper interface](docs/hr-v0-gripper-electrical-interface-p0.1.md)
- [R112 interactive power/control/reset guide](release/hr-v0/gripper-interface-p0.1/index.html)
- [R112 validation record](docs/reviews/2026-08-08-r112-validation-record.md)
- [R112 independent review request](docs/reviews/2026-08-08-r112-independent-review-request.md)
- [Sol R12 findings rechecked after R112](docs/reviews/2026-08-08-sol-r12-post-r112-status.md)
- [R113 gripper requirement and selection correction](docs/hr-v0-gripper-selection-correction-p0.1.md)
- [R113 interactive gripper decision guide](release/hr-v0/gripper-selection-p0.1/index.html)
- [R113 validation record](docs/reviews/2026-08-08-r113-validation-record.md)
- [R113 independent review request](docs/reviews/2026-08-08-r113-independent-review-request.md)
- [Sol R12 findings rechecked after R113](docs/reviews/2026-08-08-sol-r12-post-r113-status.md)
- [R114 controlled-object and handoff evidence package](docs/hr-v0-controlled-object-handoff-p0.1.md)
- [R114 interactive object/evidence guide](release/hr-v0/controlled-object-p0.1/index.html)
- [R114 validation record](docs/reviews/2026-08-08-r114-validation-record.md)
- [R114 independent review request](docs/reviews/2026-08-08-r114-independent-review-request.md)
- [Sol R12 findings rechecked after R114](docs/reviews/2026-08-08-sol-r12-post-r114-status.md)
- [R115 H104 source-provenance correction](docs/hr-v0-gripper-h104-source-correction-p0.1.md)
- [R115 interactive H104 source guide](release/hr-v0/gripper-h104-source-p0.1/index.html)
- [R115 validation record](docs/reviews/2026-08-08-r115-validation-record.md)
- [R115 independent review request](docs/reviews/2026-08-08-r115-independent-review-request.md)
- [Sol R12 findings rechecked after R115](docs/reviews/2026-08-08-sol-r12-post-r115-status.md)
- [R116 PNOZ source and terminal-path conformance](docs/hr-v0-pnoz-path-conformance-p0.1.md)
- [R116 interactive PNOZ path guide](release/hr-v0/pnoz-path-conformance-p0.1/index.html)
- [R116 validation record](docs/reviews/2026-08-08-r116-validation-record.md)
- [R116 independent review request](docs/reviews/2026-08-08-r116-independent-review-request.md)
- [Sol R12 findings rechecked after R116](docs/reviews/2026-08-08-sol-r12-post-r116-status.md)
- [R117 K1/K2 contactor application closure packet](docs/hr-v0-contactor-application-p0.2.md)
- [R117 interactive contactor evidence guide](release/hr-v0/contactor-application-p0.2/index.html)
- [R117 validation record](docs/reviews/2026-08-08-r117-validation-record.md)
- [R117 independent review request](docs/reviews/2026-08-08-r117-independent-review-request.md)
- [Sol R12 findings rechecked after R117](docs/reviews/2026-08-08-sol-r12-post-r117-status.md)
- [R118 grounding, bonding, and shield closure packet](docs/hr-v0-grounding-bonding-closure-p0.1.md)
- [R118 interactive grounding guide](release/hr-v0/grounding-bonding-p0.1/index.html)
- [R118 validation record](docs/reviews/2026-08-08-r118-validation-record.md)
- [R118 independent review request](docs/reviews/2026-08-08-r118-independent-review-request.md)
- [Sol R12 findings rechecked after R118](docs/reviews/2026-08-08-sol-r12-post-r118-status.md)
- [R119 compute selection correction](docs/hr-v0-compute-selection-p0.1.md)
- [R119 validation record](docs/reviews/2026-08-08-r119-validation-record.md)
- [R119 independent review request](docs/reviews/2026-08-08-r119-independent-review-request.md)
- [Sol R12 findings rechecked after R119](docs/reviews/2026-08-08-sol-r12-post-r119-status.md)
- [R120 compute subassembly correction](docs/hr-v0-compute-subassembly-p0.1.md)
- [R120 validation record](docs/reviews/2026-08-08-r120-validation-record.md)
- [R120 independent review request](docs/reviews/2026-08-08-r120-independent-review-request.md)
- [Sol R12 findings rechecked after R120](docs/reviews/2026-08-08-sol-r12-post-r120-status.md)
- [R121 compute-installation correction](docs/hr-v0-control-panel-p0.6.md)
- [R121 validation record](docs/reviews/2026-08-08-r121-validation-record.md)
- [R121 independent review request](docs/reviews/2026-08-08-r121-independent-review-request.md)
- [Sol R12 findings rechecked after R121](docs/reviews/2026-08-08-sol-r12-post-r121-status.md)
- [R122 Pi-to-U2D2 cable candidate](docs/hr-v0-u2d2-usb-cable-p0.1.md)
- [R122 interactive cable guide](release/hr-v0/u2d2-usb-cable-p0.1/index.html)
- [R122 validation record](docs/reviews/2026-08-08-r122-validation-record.md)
- [R122 independent review request](docs/reviews/2026-08-08-r122-independent-review-request.md)
- [Sol R12 findings rechecked after R122](docs/reviews/2026-08-08-sol-r12-post-r122-status.md)
- [R123 panel rail/duct correction](docs/hr-v0-panel-rail-duct-p0.1.md)
- [R123 interactive rail/duct guide](release/hr-v0/panel-rail-duct-p0.1/index.html)
- [R123 validation record](docs/reviews/2026-08-08-r123-validation-record.md)
- [R123 independent review request](docs/reviews/2026-08-08-r123-independent-review-request.md)
- [Sol R12 findings rechecked after R123](docs/reviews/2026-08-08-sol-r12-post-r123-status.md)
- [R124 stopping-budget and active J2-limit correction](docs/hr-v0-stopping-budget-p0.1.md)
- [R124 interactive stopping-budget screen](release/hr-v0/stopping-budget-p0.1/index.html)
- [R124 validation record](docs/reviews/2026-08-08-r124-validation-record.md)
- [R124 independent review request](docs/reviews/2026-08-08-r124-independent-review-request.md)
- [Sol R12 findings rechecked after R124](docs/reviews/2026-08-08-sol-r12-post-r124-status.md)
- [R125 passive power-loss containment correction](docs/hr-v0-power-loss-containment-p0.1.md)
- [R125 interactive power-loss containment guide](release/hr-v0/power-loss-containment-p0.1/index.html)
- [R125 validation record](docs/reviews/2026-08-08-r125-validation-record.md)
- [R125 independent review request](docs/reviews/2026-08-08-r125-independent-review-request.md)
- [Sol R12 findings rechecked after R125](docs/reviews/2026-08-08-sol-r12-post-r125-status.md)
- [R126 continuous collapse-envelope correction](docs/hr-v0-collapse-envelope-p0.1.md)
- [R126 interactive collapse-envelope guide](release/hr-v0/collapse-envelope-p0.1/index.html)
- [R126 validation record](docs/reviews/2026-08-08-r126-validation-record.md)
- [R126 independent review request](docs/reviews/2026-08-08-r126-independent-review-request.md)
- [Sol R12 findings rechecked after R126](docs/reviews/2026-08-08-sol-r12-post-r126-status.md)
- [R127 passive arm-receiver candidate](docs/hr-v0-passive-arm-receiver-p0.1.md)
- [R127 interactive passive arm-receiver guide](release/hr-v0/passive-arm-receiver-p0.1/index.html)
- [R127 validation record](docs/reviews/2026-08-09-r127-validation-record.md)
- [R127 independent review request](docs/reviews/2026-08-09-r127-independent-review-request.md)
- [Sol R12 findings rechecked after R127](docs/reviews/2026-08-09-sol-r12-post-r127-status.md)
- [R128 passive arm-receiver second-method verification](docs/hr-v0-passive-arm-receiver-verification-p0.1.md)
- [R128 interactive verification guide](release/hr-v0/passive-arm-receiver-verification-p0.1/index.html)
- [R128 validation record](docs/reviews/2026-08-09-r128-validation-record.md)
- [R128 independent review request](docs/reviews/2026-08-09-r128-independent-review-request.md)
- [Sol R12 findings rechecked after R128](docs/reviews/2026-08-09-sol-r12-post-r128-status.md)
- [R129 passive arm-receiver detailed candidate](docs/hr-v0-passive-arm-receiver-detail-p0.2.md)
- [R129 interactive receiver-detail guide](release/hr-v0/passive-arm-receiver-detail-p0.2/index.html)
- [R129 validation record](docs/reviews/2026-08-09-r129-validation-record.md)
- [R129 independent review request](docs/reviews/2026-08-09-r129-independent-review-request.md)
- [Sol R12 findings rechecked after R129](docs/reviews/2026-08-09-sol-r12-post-r129-status.md)
- [R130 corrected receiver guide interface](docs/hr-v0-receiver-guide-interface-p0.1.md)
- [R130 interactive guide-interface review](release/hr-v0/receiver-guide-interface-p0.1/index.html)
- [R130 validation record](docs/reviews/2026-08-09-r130-validation-record.md)
- [R130 independent review request](docs/reviews/2026-08-09-r130-independent-review-request.md)
- [Sol R12 findings rechecked after R130](docs/reviews/2026-08-09-sol-r12-post-r130-status.md)
- [R131 watchdog PCB current-source and mounting interface](docs/hr-v0-watchdog-pcb-mounting-interface-p0.1.md)
- [R131 interactive watchdog PCB mounting guide](release/hr-v0/watchdog-pcb-mounting-p0.1/index.html)
- [R131 validation record](docs/reviews/2026-08-09-r131-validation-record.md)
- [R131 independent review request](docs/reviews/2026-08-09-r131-independent-review-request.md)
- [Sol R12 findings rechecked after R131](docs/reviews/2026-08-09-sol-r12-post-r131-status.md)
- [R132 watchdog PCBA capability and DFM inquiry](docs/hr-v0-watchdog-pcba-capability-inquiry-p0.1.md)
- [R132 interactive watchdog PCBA inquiry guide](release/hr-v0/watchdog-pcba-rfi-p0.1/index.html)
- [R132 validation record](docs/reviews/2026-08-09-r132-validation-record.md)
- [R132 independent review request](docs/reviews/2026-08-09-r132-independent-review-request.md)
- [Sol R12 findings rechecked after R132](docs/reviews/2026-08-09-sol-r12-post-r132-status.md)
- [R133 watchdog PCBA assembly-data review package](docs/hr-v0-watchdog-pcba-assembly-data-p0.1.md)
- [R133 interactive assembly-data guide](release/hr-v0/watchdog-pcba-assembly-data-p0.1/index.html)
- [R133 validation record](docs/reviews/2026-08-09-r133-validation-record.md)
- [R133 independent review request](docs/reviews/2026-08-09-r133-independent-review-request.md)
- [Sol R12 findings rechecked after R133](docs/reviews/2026-08-09-sol-r12-post-r133-status.md)
- [R134 mechanical DFM/FAI internal-review package](docs/hr-v0-mechanical-dfm-data-p0.1.md)
- [R134 interactive mechanical review guide](release/hr-v0/mechanical-dfm-data-p0.1/index.html)
- [R134 validation record](docs/reviews/2026-08-09-r134-validation-record.md)
- [R134 independent review request](docs/reviews/2026-08-09-r134-independent-review-request.md)
- [Sol R12 findings rechecked after R134](docs/reviews/2026-08-09-sol-r12-post-r134-status.md)
- [R135 STEP/DXF/drawing parity audit](docs/hr-v0-mechanical-parity-p0.1.md)
- [R135 interactive geometry-parity guide](release/hr-v0/mechanical-parity-p0.1/index.html)
- [R135 validation record](docs/reviews/2026-08-09-r135-validation-record.md)
- [R135 independent review request](docs/reviews/2026-08-09-r135-independent-review-request.md)
- [Sol R12 findings rechecked after R135](docs/reviews/2026-08-09-sol-r12-post-r135-status.md)
- [R136 countersink model-definition correction candidate](docs/hr-v0-countersink-mbd-p0.1.md)
- [R136 interactive countersink comparison guide](release/hr-v0/countersink-mbd-p0.1/index.html)
- [R136 validation record](docs/reviews/2026-08-09-r136-validation-record.md)
- [R136 independent review request](docs/reviews/2026-08-09-r136-independent-review-request.md)
- [Sol R12 findings rechecked after R136](docs/reviews/2026-08-09-sol-r12-post-r136-status.md)
- [R137 conventional drawing and finished-DXF candidate](docs/hr-v0-manufacturing-drawing-p0.1.md)
- [R137 interactive drawing-definition guide](release/hr-v0/mechanical-drawing-p0.1/index.html)
- [R137 validation record](docs/reviews/2026-08-09-r137-validation-record.md)
- [R137 independent review request](docs/reviews/2026-08-09-r137-independent-review-request.md)
- [Sol R12 findings rechecked after R137](docs/reviews/2026-08-09-sol-r12-post-r137-status.md)
- [R138 watchdog critical-IC native metadata correction](docs/hr-v0-watchdog-footprint-metadata-p0.1.md)
- [R138 interactive native-metadata guide](release/hr-v0/watchdog-footprint-metadata-p0.1/index.html)
- [R138 validation record](docs/reviews/2026-08-09-r138-validation-record.md)
- [R138 independent review request](docs/reviews/2026-08-09-r138-independent-review-request.md)
- [Sol R12 findings rechecked after R138](docs/reviews/2026-08-09-sol-r12-post-r138-status.md)
- [R139 current PCB-P0.9 native identity and assembly-data correction](docs/hr-v0-watchdog-pcba-assembly-data-p0.2.md)
- [R139 interactive P0.9 assembly guide](release/hr-v0/watchdog-pcba-assembly-data-p0.2/index.html)
- [R139 synchronized E2 hardware slice P0.3](docs/hr-v0-e2-hardware-slice-p0.3.md)
- [R139 validation record](docs/reviews/2026-08-09-r139-validation-record.md)
- [R139 independent review request](docs/reviews/2026-08-09-r139-independent-review-request.md)
- [Sol R12 findings rechecked after R139](docs/reviews/2026-08-09-sol-r12-post-r139-status.md)
- [R140 HR-V0 coordinate and sign convention](docs/hr-v0-coordinate-sign-convention-p0.1.md)
- [R140 interactive frame/sign guide](release/hr-v0/coordinate-convention-p0.1/index.html)
- [R140 validation record](docs/reviews/2026-08-09-r140-validation-record.md)
- [R140 independent review request](docs/reviews/2026-08-09-r140-independent-review-request.md)
- [Sol R12 findings rechecked after R140](docs/reviews/2026-08-09-sol-r12-post-r140-status.md)
- [R141 HR-V0 governance control](docs/hr-v0-governance-control-p0.1.md)
- [R141 interactive governance register](release/hr-v0/governance-p0.1/index.html)
- [R141 validation record](docs/reviews/2026-08-09-r141-validation-record.md)
- [R141 independent review request](docs/reviews/2026-08-09-r141-independent-review-request.md)
- [Sol R12 findings rechecked after R141](docs/reviews/2026-08-09-sol-r12-post-r141-status.md)
- [R142 atomic requirement candidates](docs/hr-v0-atomic-requirements-p0.1.md)
- [R142 current governance control P0.2](docs/hr-v0-governance-control-p0.2.md)
- [R142 interactive atomic-requirement register](release/hr-v0/atomic-requirements-p0.1/index.html)
- [R142 interactive governance register](release/hr-v0/governance-p0.2/index.html)
- [R142 independent review request](docs/reviews/2026-08-09-r142-independent-review-request.md)
- [R142 validation record](docs/reviews/2026-08-09-r142-validation-record.md)
- [Sol R12 findings rechecked after R142](docs/reviews/2026-08-09-sol-r12-post-r142-status.md)
- [R143 internally audited atomic requirement candidates P0.2](docs/hr-v0-atomic-requirements-p0.2.md)
- [R143 current governance control P0.3](docs/hr-v0-governance-control-p0.3.md)
- [R143 interactive atomic-requirement register](release/hr-v0/atomic-requirements-p0.2/index.html)
- [R143 interactive governance register](release/hr-v0/governance-p0.3/index.html)
- [R143 independent review request](docs/reviews/2026-08-09-r143-independent-review-request.md)
- [R143 validation record](docs/reviews/2026-08-09-r143-validation-record.md)
- [Sol R12 findings rechecked after R143](docs/reviews/2026-08-09-sol-r12-post-r143-status.md)
- [R144 integrated unpowered build traveler](docs/hr-v0-build-traveler-p0.1.md)
- [R144 interactive build guide](release/hr-v0/build-traveler-p0.1/index.html)
- [R144 independent review request](docs/reviews/2026-08-09-r144-independent-review-request.md)
- [R144 validation record](docs/reviews/2026-08-09-r144-validation-record.md)
- [Sol R12 findings rechecked after R144](docs/reviews/2026-08-09-sol-r12-post-r144-status.md)
- [R145 complete Evaluation Batch A acquisition decision](docs/hr-v0-evaluation-batch-a-acquisition-p0.1.md)
- [R145 interactive acquisition guide](procurement/hr-v0/evaluation-batch-a-acquisition-p0.1/index.html)
- [R145 independent review request](docs/reviews/2026-08-09-r145-independent-review-request.md)
- [R145 validation record](docs/reviews/2026-08-09-r145-validation-record.md)
- [Sol R12 findings rechecked after R145](docs/reviews/2026-08-09-sol-r12-post-r145-status.md)
- [R146 Evaluation Batch A unit receiving campaign](docs/hr-v0-evaluation-batch-a-receiving-p0.1.md)
- [R146 interactive receiving guide and printable quarantine labels](release/hr-v0/evaluation-batch-a-receiving-p0.1/index.html)
- [R146 independent review request](docs/reviews/2026-08-09-r146-independent-review-request.md)
- [R146 validation record](docs/reviews/2026-08-09-r146-validation-record.md)
- [Sol R12 findings rechecked after R146](docs/reviews/2026-08-09-sol-r12-post-r146-status.md)
- [R147 actuator-source AC cord candidate](docs/hr-v0-actuator-ac-cord-p0.1.md)
- [R147 interactive AC cord selection guide](release/hr-v0/actuator-ac-cord-p0.1/index.html)
- [R147 independent review request](docs/reviews/2026-08-09-r147-independent-review-request.md)
- [R147 validation record](docs/reviews/2026-08-09-r147-validation-record.md)
- [Sol R12 findings rechecked after R147](docs/reviews/2026-08-09-sol-r12-post-r147-status.md)
- [R148 P0.7 mechanical BOM binding](docs/hr-v0-mechanical-bom-binding-p0.1.md)
- [R148 interactive mechanical BOM binding guide](release/hr-v0/mechanical-bom-binding-p0.1/index.html)
- [R148 five-row mechanical part binding](bom/hr-v0-mechanical-custom-part-binding.csv)
- [R148 independent review request](docs/reviews/2026-08-09-r148-independent-review-request.md)
- [R148 validation record](docs/reviews/2026-08-09-r148-validation-record.md)
- [Sol R12 findings rechecked after R148](docs/reviews/2026-08-09-sol-r12-post-r148-status.md)
- [R149 watchdog PCB BOM binding](docs/hr-v0-watchdog-pcb-bom-binding-p0.1.md)
- [R149 interactive watchdog PCB binding guide](release/hr-v0/watchdog-pcb-bom-binding-p0.1/index.html)
- [R149 machine-readable watchdog PCB binding](bom/hr-v0-watchdog-pcb-binding.csv)
- [R149 independent review request](docs/reviews/2026-08-09-r149-independent-review-request.md)
- [R149 validation record](docs/reviews/2026-08-09-r149-validation-record.md)
- [Sol R12 findings rechecked after R149](docs/reviews/2026-08-09-sol-r12-post-r149-status.md)
- [R150 current PCB-P0.9 CAM review package](docs/hr-v0-watchdog-cam-p0.1.md)
- [R150 interactive CAM review guide](release/hr-v0/watchdog-pcb-cam-p0.1/index.html)
- [R150 CAM output register](release/hr-v0/watchdog-pcb-cam-p0.1/cam-output-register.csv)
- [R150 42-reference position parity](release/hr-v0/watchdog-pcb-cam-p0.1/cam-assembly-parity.csv)
- [R150 independent review request](docs/reviews/2026-08-09-r150-independent-review-request.md)
- [R150 validation record](docs/reviews/2026-08-09-r150-validation-record.md)
- [Sol R12 findings rechecked after R150](docs/reviews/2026-08-09-sol-r12-post-r150-status.md)
- [R151 DXL-STAR-P0.1 manufacturing review package](docs/hr-v0-dxl-star-manufacturing-p0.1.md)
- [R151 interactive DXL-star manufacturing review guide](release/hr-v0/dxl-star-manufacturing-p0.1/index.html)
- [R151 terminal parity register](release/hr-v0/dxl-star-manufacturing-p0.1/terminal-parity-register.csv)
- [R151 independent review request](docs/reviews/2026-08-09-r151-independent-review-request.md)
- [R151 validation record](docs/reviews/2026-08-09-r151-validation-record.md)
- [Sol R12 findings rechecked after R151](docs/reviews/2026-08-09-sol-r12-post-r151-status.md)
- [R152 DXL injection allocation binding](docs/hr-v0-dxl-injection-binding-p0.1.md)
- [R152 interactive allocation guide](release/hr-v0/dxl-injection-binding-p0.1/index.html)
- [R152 eighteen-terminal allocation parity](release/hr-v0/dxl-injection-binding-p0.1/allocation-parity.csv)
- [R152 independent review request](docs/reviews/2026-08-09-r152-independent-review-request.md)
- [Sol R12 findings rechecked after R152](docs/reviews/2026-08-09-sol-r12-post-r152-status.md)
- [R152 validation record](docs/reviews/2026-08-09-r152-validation-record.md)
- [R153 DXL harness allocation correction](docs/hr-v0-dxl-harness-allocation-p0.1.md)
- [R153 interactive harness guide](release/hr-v0/dxl-harness-allocation-p0.1/index.html)
- [R153 controller cable pin map](release/hr-v0/dxl-harness-allocation-p0.1/controller-cable-pinmap.csv)
- [R153 independent review request](docs/reviews/2026-08-09-r153-independent-review-request.md)
- [Sol R12 findings rechecked after R153](docs/reviews/2026-08-09-sol-r12-post-r153-status.md)
- [R153 validation record](docs/reviews/2026-08-09-r153-validation-record.md)
- [R154 DXL current-envelope correction](docs/hr-v0-dxl-current-envelope-p0.1.md)
- [R154 interactive current guide](release/hr-v0/dxl-current-envelope-p0.1/index.html)
- [R154 measurement plan](release/hr-v0/dxl-current-envelope-p0.1/measurement-plan.csv)
- [R154 independent review request](docs/reviews/2026-08-09-r154-independent-review-request.md)
- [Sol R12 findings rechecked after R154](docs/reviews/2026-08-09-sol-r12-post-r154-status.md)
- [R154 validation record](docs/reviews/2026-08-09-r154-validation-record.md)
- [R155 DXL protection evaluation](docs/hr-v0-dxl-protection-evaluation-p0.1.md)
- [R155 interactive native-schematic guide](release/hr-v0/dxl-protection-evaluation-p0.1/index.html)
- [R155 independent review request](docs/reviews/2026-08-09-r155-independent-review-request.md)
- [R155 validation record](docs/reviews/2026-08-09-r155-validation-record.md)
- [Sol R12 findings rechecked after R155](docs/reviews/2026-08-09-sol-r12-post-r155-status.md)
- [R156 DXL protection carrier](docs/hr-v0-dxl-protection-carrier-p0.1.md)
- [R156 interactive carrier guide](release/hr-v0/dxl-protection-carrier-p0.1/index.html)
- [R156 independent review request](docs/reviews/2026-08-09-r156-independent-review-request.md)
- [R156 validation record](docs/reviews/2026-08-09-r156-validation-record.md)
- [Sol R12 findings rechecked after R156](docs/reviews/2026-08-09-sol-r12-post-r156-status.md)
- [R157 branch-fault validation definition](docs/hr-v0-branch-fault-validation-p0.1.md)
- [R157 interactive fault/no-backfeed guide](release/hr-v0/branch-fault-validation-p0.1/index.html)
- [R157 independent review request](docs/reviews/2026-08-09-r157-independent-review-request.md)
- [R157 validation record](docs/reviews/2026-08-09-r157-validation-record.md)
- [Sol R12 findings rechecked after R157](docs/reviews/2026-08-09-sol-r12-post-r157-status.md)
- [R158 corrected RPW carrier candidate](docs/hr-v0-dxl-protection-carrier-p0.2.md)
- [R158 interactive footprint-correction guide](release/hr-v0/dxl-protection-carrier-p0.2/index.html)
- [R158 exact RPW parity register](release/hr-v0/dxl-protection-carrier-p0.2/rpw-land-pattern-parity.csv)
- [R158 independent review request](docs/reviews/2026-08-09-r158-independent-review-request.md)
- [R158 validation record](docs/reviews/2026-08-09-r158-validation-record.md)
- [Sol R12 findings rechecked after R158](docs/reviews/2026-08-09-sol-r12-post-r158-status.md)
- [R159 P0.3 carrier and PCBA DFM inquiry](docs/hr-v0-dxl-protection-carrier-p0.3.md)
- [R159 interactive DFM inquiry guide](release/hr-v0/dxl-protection-carrier-p0.3/index.html)
- [R159 provider capability screen](electrical/manufacturing/hr-v0-dxl-protection-carrier-dfm-p0.1/provider-capability-screen.csv)
- [R159 unsent provider RFI](electrical/manufacturing/hr-v0-dxl-protection-carrier-dfm-p0.1/provider-rfi.csv)
- [R159 independent review request](docs/reviews/2026-08-09-r159-independent-review-request.md)
- [R159 validation record](docs/reviews/2026-08-09-r159-validation-record.md)
- [Sol R12 findings rechecked after R159](docs/reviews/2026-08-09-sol-r12-post-r159-status.md)
- [R160 carrier harness interface-control candidate](docs/hr-v0-dxl-protection-carrier-harness-p0.1.md)
- [R160 interactive carrier harness guide](release/hr-v0/dxl-protection-carrier-harness-p0.1/index.html)
- [R160 harness acceptance matrix](electrical/harness/hr-v0-dxl-protection-carrier-harness-p0.1/acceptance-matrix.csv)
- [R160 independent review request](docs/reviews/2026-08-09-r160-independent-review-request.md)
- [R160 validation record](docs/reviews/2026-08-09-r160-validation-record.md)
- [Sol R12 findings rechecked after R160](docs/reviews/2026-08-09-sol-r12-post-r160-status.md)
- [R161 carrier-integrated ECAD candidate](docs/hr-v0-dxl-carrier-integration-p0.1.md)
- [R161 interactive carrier-integration guide](release/hr-v0/dxl-carrier-integration-p0.1/index.html)
- [R161 net-transition matrix](electrical/integration/hr-v0-dxl-carrier-integration-p0.1/net-transition-matrix.csv)
- [R161 independent review request](docs/reviews/2026-08-09-r161-independent-review-request.md)
- [R161 validation record](docs/reviews/2026-08-09-r161-validation-record.md)
- [Sol R12 findings rechecked after R161](docs/reviews/2026-08-09-sol-r12-post-r161-status.md)
- [R162 carrier mounting-interface candidate](docs/hr-v0-dxl-carrier-mount-p0.1.md)
- [R162 interactive no-drill mounting guide](release/hr-v0/dxl-carrier-mount-p0.1/index.html)
- [R162 no-drill metrology form](electrical/mechanical/hr-v0-dxl-carrier-mount-p0.1/no-drill-metrology-form.csv)
- [R162 independent review request](docs/reviews/2026-08-09-r162-independent-review-request.md)
- [R162 validation record](docs/reviews/2026-08-09-r162-validation-record.md)
- [Sol R12 findings rechecked after R162](docs/reviews/2026-08-09-sol-r12-post-r162-status.md)
- [R163 current-configuration reconciliation](docs/hr-v0-configuration-reconciliation-p0.1.md)
- [R163/R164/R165 synchronized configuration guide](release/hr-v0/configuration-reconciliation-p0.1/index.html)
- [R164 current P0.2 DXL-star manufacturing review](docs/hr-v0-dxl-star-manufacturing-p0.2.md)
- [R164 interactive P0.2 manufacturing guide](release/hr-v0/dxl-star-manufacturing-p0.2/index.html)
- [R165 P1.15 watchdog/E2 parity evidence](docs/hr-v0-e2-p115-parity-p0.1.md)
- [R165 interactive P1.15 parity guide](release/hr-v0/e2-p115-parity-p0.1/index.html)
- [R165 P1.15-bound E2 hardware slice P0.4](docs/hr-v0-e2-hardware-p0.4.md)
- [R165 interactive E2 P0.4 guide](release/hr-v0/e2-hardware-p0.4/HR-V0_e2-hardware-guide.html)
- [R165 independent review request](docs/reviews/2026-08-09-r165-independent-review-request.md)
- [R165 validation record](docs/reviews/2026-08-09-r165-validation-record.md)
- [Sol R12 findings rechecked after R165](docs/reviews/2026-08-09-sol-r12-post-r165-status.md)
- [R166 P1.15-bound watchdog CAM review](docs/hr-v0-watchdog-cam-p0.2.md)
- [R166 interactive watchdog CAM guide](release/hr-v0/watchdog-pcb-cam-p0.2/index.html)
- [R166 CAM output register](release/hr-v0/watchdog-pcb-cam-p0.2/cam-output-register.csv)
- [R166 independent review request](docs/reviews/2026-08-09-r166-independent-review-request.md)
- [R166 validation record](docs/reviews/2026-08-09-r166-validation-record.md)
- [Sol R12 findings rechecked after R166](docs/reviews/2026-08-09-sol-r12-post-r166-status.md)
- [R167 Boston/US fabrication-route validation](docs/reviews/2026-08-09-r167-validation-record.md)
- [R167 fabrication-route independent review request](docs/reviews/2026-08-09-r167-independent-review-request.md)
- [Sol R12 findings rechecked after R167](docs/reviews/2026-08-09-sol-r12-post-r167-status.md)
- [R168 XT1 control-terminal group](docs/hr-v0-xt1-terminal-group-p0.1.md)
- [R168 interactive XT1 position guide](release/hr-v0/xt1-terminal-group-p0.1/index.html)
- [R168 XT1 independent review request](docs/reviews/2026-08-09-r168-independent-review-request.md)
- [R168 XT1 validation record](docs/reviews/2026-08-09-r168-validation-record.md)
- [Sol R12 findings rechecked after R168](docs/reviews/2026-08-09-sol-r12-post-r168-status.md)
- [R169 panel identification system](docs/hr-v0-label-system-p0.1.md)
- [R169 interactive label guide](release/hr-v0/label-system-p0.1/index.html)
- [R169 label-system independent review request](docs/reviews/2026-08-09-r169-independent-review-request.md)
- [R169 label-system validation record](docs/reviews/2026-08-09-r169-validation-record.md)
- [Sol R12 findings rechecked after R169](docs/reviews/2026-08-09-sol-r12-post-r169-status.md)
- [R170 compute-storage candidate](docs/hr-v0-compute-storage-p0.2.md)
- [R170 interactive compute-storage guide](release/hr-v0/compute-storage-p0.2/index.html)
- [R170 compute-storage independent review request](docs/reviews/2026-08-09-r170-independent-review-request.md)
- [R170 compute-storage validation record](docs/reviews/2026-08-09-r170-validation-record.md)
- [Sol R12 findings rechecked after R170](docs/reviews/2026-08-09-sol-r12-post-r170-status.md)
- [R171 fail-closed host deployment candidate](docs/hr-v0-host-deployment-p0.1.md)
- [R171 interactive host deployment guide](release/hr-v0/host-deployment-p0.1/index.html)
- [R171 host deployment independent review request](docs/reviews/2026-08-09-r171-independent-review-request.md)
- [R171 host deployment validation record](docs/reviews/2026-08-09-r171-validation-record.md)
- [Sol R12 findings rechecked after R171](docs/reviews/2026-08-09-sol-r12-post-r171-status.md)
- [R172 Raspberry Pi OS publisher-SBOM lock](docs/hr-v0-rpi-os-sbom-p0.1.md)
- [R172 interactive publisher-SBOM guide](release/hr-v0/rpi-os-sbom-p0.1/index.html)
- [R172 publisher-SBOM independent review request](docs/reviews/2026-08-09-r172-independent-review-request.md)
- [R172 publisher-SBOM validation record](docs/reviews/2026-08-09-r172-validation-record.md)
- [Sol R12 findings rechecked after R172](docs/reviews/2026-08-09-sol-r12-post-r172-status.md)
- [R173 fabrication-input basis](docs/hr-v0-fabrication-input-basis-p0.1.md)
- [R173 interactive fabrication-input guide](release/hr-v0/fabrication-input-basis-p0.1/index.html)
- [R173 fabrication-input independent review request](docs/reviews/2026-08-10-r173-independent-review-request.md)
- [R173 fabrication-input validation record](docs/reviews/2026-08-10-r173-validation-record.md)
- [Sol R12 findings rechecked after R173](docs/reviews/2026-08-10-sol-r12-post-r173-status.md)
- [R174 historical dynamic trace analysis (superseded by R181)](docs/hr-v0-dynamic-trace-analysis-p0.1.md)
- [R174 historical trace-analysis guide (superseded by R181)](release/hr-v0/dynamic-trace-analysis-p0.1/index.html)
- [R174 independent review request](docs/reviews/2026-08-10-r174-independent-review-request.md)
- [R174 validation record](docs/reviews/2026-08-10-r174-validation-record.md)
- [Sol R12 findings rechecked after R174](docs/reviews/2026-08-10-sol-r12-post-r174-status.md)
- [R175 dynamic instrumentation backbone](docs/hr-v0-dynamic-instrumentation-p0.1.md)
- [R175 interactive instrumentation guide](release/hr-v0/dynamic-instrumentation-p0.1/index.html)
- [R175 independent review request](docs/reviews/2026-08-10-r175-independent-review-request.md)
- [R175 validation record](docs/reviews/2026-08-10-r175-validation-record.md)
- [Sol R12 findings rechecked after R175](docs/reviews/2026-08-10-sol-r12-post-r175-status.md)
- [R176 isolated dynamic-event interface](docs/hr-v0-dynamic-event-interface-p0.1.md)
- [R176 interactive event-interface guide](release/hr-v0/dynamic-event-interface-p0.1/index.html)
- [R176 native KiCad event-interface source](electrical/kicad/hr-v0-dynamic-event-interface-p0.1/)
- [R176 independent review request](docs/reviews/2026-08-10-r176-independent-review-request.md)
- [R176 validation record](docs/reviews/2026-08-10-r176-validation-record.md)
- [Sol R12 findings rechecked after R176](docs/reviews/2026-08-10-sol-r12-post-r176-status.md)
- [R177 low-loading isolated event acquisition](docs/hr-v0-dynamic-event-ain-p0.1.md)
- [R177 interactive event-acquisition guide](release/hr-v0/dynamic-event-ain-p0.1/index.html)
- [R177 native KiCad event-acquisition source](electrical/kicad/hr-v0-dynamic-event-ain-p0.1/)
- [R177 independent review request](docs/reviews/2026-08-10-r177-independent-review-request.md)
- [R177 validation record](docs/reviews/2026-08-10-r177-validation-record.md)
- [Sol R12 findings rechecked after R177](docs/reviews/2026-08-10-sol-r12-post-r177-status.md)
- [R178 event-tap disposition](docs/hr-v0-event-tap-disposition-p0.1.md)
- [R178 interactive event-tap guide](release/hr-v0/event-tap-disposition-p0.1/index.html)
- [R178 native KiCad disposition source](electrical/kicad/hr-v0-event-tap-disposition-p0.1/)
- [R178 independent review request](docs/reviews/2026-08-10-r178-independent-review-request.md)
- [R178 validation record](docs/reviews/2026-08-10-r178-validation-record.md)
- [Sol R12 findings rechecked after R178](docs/reviews/2026-08-10-sol-r12-post-r178-status.md)
- [R179 non-contact event observation](docs/hr-v0-noncontact-event-observation-p0.1.md)
- [R179 interactive non-contact event guide](release/hr-v0/noncontact-event-observation-p0.1/index.html)
- [R179 independent review request](docs/reviews/2026-08-10-r179-independent-review-request.md)
- [R179 validation record](docs/reviews/2026-08-10-r179-validation-record.md)
- [Sol R12 findings rechecked after R179](docs/reviews/2026-08-10-sol-r12-post-r179-status.md)
- [R180 event-observation independence correction](docs/hr-v0-event-observation-correction-p0.1.md)
- [R180 interactive eight-channel correction guide](release/hr-v0/event-observation-correction-p0.1/index.html)
- [R180 independent review request](docs/reviews/2026-08-10-r180-independent-review-request.md)
- [R180 validation record](docs/reviews/2026-08-10-r180-validation-record.md)
- [Sol R12 findings rechecked after R180](docs/reviews/2026-08-10-sol-r12-post-r180-status.md)
- [R181 corrected two-run dynamic-trace analysis](docs/hr-v0-dynamic-trace-analysis-p0.2.md)
- [R181 interactive two-run analysis guide](release/hr-v0/dynamic-trace-analysis-p0.2/index.html)
- [R181 independent review request](docs/reviews/2026-08-10-r181-independent-review-request.md)
- [R181 validation record](docs/reviews/2026-08-10-r181-validation-record.md)
- [Sol R12 findings rechecked after R181](docs/reviews/2026-08-10-sol-r12-post-r181-status.md)
- [R182 E2 acquisition compatibility](docs/hr-v0-e2-acquisition-compatibility-p0.1.md)
- [R182 interactive acquisition guide](release/hr-v0/e2-acquisition-compatibility-p0.1/index.html)
- [R182 independent review request](docs/reviews/2026-08-10-r182-independent-review-request.md)
- [R182 validation record](docs/reviews/2026-08-10-r182-validation-record.md)
- [Sol R12 findings rechecked after R182](docs/reviews/2026-08-10-sol-r12-post-r182-status.md)
- [R183 Q4X witness physical-interface candidate](docs/hr-v0-q4x-interface-p0.1.md)
- [R183 interactive Q4X interface guide](release/hr-v0/q4x-interface-p0.1/index.html)
- [R183 independent review request](docs/reviews/2026-08-10-r183-independent-review-request.md)
- [R183 validation record](docs/reviews/2026-08-10-r183-validation-record.md)
- [Sol R12 findings rechecked after R183](docs/reviews/2026-08-10-sol-r12-post-r183-status.md)
- [R184 Q4X temporary interface-box candidate](docs/hr-v0-q4x-box-p0.1.md)
- [R184 interactive Q4X interface-box guide](release/hr-v0/q4x-box-p0.1/index.html)
- [R184 native connected KiCad source](electrical/kicad/hr-v0-q4x-box-p0.1/)
- [R184 independent review request](docs/reviews/2026-08-10-r184-independent-review-request.md)
- [R184 validation record](docs/reviews/2026-08-10-r184-validation-record.md)
- [Sol R12 findings rechecked after R184](docs/reviews/2026-08-10-sol-r12-post-r184-status.md)
- [R185 dimensioned Q4X box-layout candidate](docs/hr-v0-q4x-box-layout-p0.1.md)
- [R185 interactive box-layout guide](release/hr-v0/q4x-box-layout-p0.1/index.html)
- [R185 review-only panel CAD](cad/hr-v0-q4x-box-layout-p0.1/)
- [R185 independent review request](docs/reviews/2026-08-10-r185-independent-review-request.md)
- [R185 validation record](docs/reviews/2026-08-10-r185-validation-record.md)
- [Sol R12 findings rechecked after R185](docs/reviews/2026-08-10-sol-r12-post-r185-status.md)
- [R186 Q4X installation-evidence package](docs/hr-v0-q4x-installation-evidence-p0.1.md)
- [R186 interactive receiving/metrology guide](release/hr-v0/q4x-installation-evidence-p0.1/index.html)
- [R186 independent review request](docs/reviews/2026-08-10-r186-independent-review-request.md)
- [R186 validation record](docs/reviews/2026-08-10-r186-validation-record.md)
- [Sol R12 findings rechecked after R186](docs/reviews/2026-08-10-sol-r12-post-r186-status.md)
- [R187 Q4X unpowered acquisition decision](docs/hr-v0-q4x-unpowered-acquisition-p0.1.md)
- [R187 interactive acquisition guide](procurement/hr-v0/q4x-unpowered-acquisition-p0.1/index.html)
- [R187 independent review request](docs/reviews/2026-08-10-r187-independent-review-request.md)
- [R187 validation record](docs/reviews/2026-08-10-r187-validation-record.md)
- [Sol R12 findings rechecked after R187](docs/reviews/2026-08-10-sol-r12-post-r187-status.md)
- [R188 Q4X quote-readiness amendment](docs/hr-v0-q4x-quote-readiness-p0.1.md)
- [R188 interactive quote-readiness guide](procurement/hr-v0/q4x-quote-readiness-p0.1/index.html)
- [R188 independent review request](docs/reviews/2026-08-10-r188-independent-review-request.md)
- [R188 validation record](docs/reviews/2026-08-10-r188-validation-record.md)
- [Sol R12 findings rechecked after R188](docs/reviews/2026-08-10-sol-r12-post-r188-status.md)
- [R189 clean-clone reproducibility audit](docs/hr-v0-clean-clone-audit-p0.1.md)
- [R189 independent review request](docs/reviews/2026-08-10-r189-independent-review-request.md)
- [R189 validation record](docs/reviews/2026-08-10-r189-validation-record.md)
- [Sol R12 findings rechecked after R189](docs/reviews/2026-08-10-sol-r12-post-r189-status.md)
- [R190 lightweight gripper feasibility branch](docs/hr-v0-xc330-gripper-feasibility-p0.1.md)
- [R190 interactive gripper guide](release/hr-v0/xc330-gripper-feasibility-p0.1/index.html)
- [R190 independent review request](docs/reviews/2026-08-10-r190-independent-review-request.md)
- [R190 validation record](docs/reviews/2026-08-10-r190-validation-record.md)
- [Sol R12 findings rechecked after R190](docs/reviews/2026-08-10-sol-r12-post-r190-status.md)
- [R191 source-bound XC330 gripper interface](docs/hr-v0-xc330-gripper-interface-p0.2.md)
- [R191 interactive gripper interface guide](release/hr-v0/xc330-gripper-interface-p0.2/index.html)
- [R191 independent review request](docs/reviews/2026-08-10-r191-independent-review-request.md)
- [R191 validation record](docs/reviews/2026-08-10-r191-validation-record.md)
- [Sol R12 findings rechecked after R191](docs/reviews/2026-08-10-sol-r12-post-r191-status.md)
- [R192 source-bound XC330 wrist integration](docs/hr-v0-xc330-wrist-integration-p0.1.md)
- [R192 interactive wrist integration guide](release/hr-v0/xc330-wrist-integration-p0.1/index.html)
- [R192 independent review request](docs/reviews/2026-08-10-r192-independent-review-request.md)
- [R192 validation record](docs/reviews/2026-08-10-r192-validation-record.md)
- [Sol R12 findings rechecked after R192](docs/reviews/2026-08-10-sol-r12-post-r192-status.md)
- [R193 gripper native-source correction](docs/hr-v0-gripper-cad-source-correction-p0.2.md)
- [R193 interactive source/branch guide](release/hr-v0/gripper-cad-source-p0.2/index.html)
- [R193 independent review request](docs/reviews/2026-08-10-r193-independent-review-request.md)
- [R193 validation record](docs/reviews/2026-08-10-r193-validation-record.md)
- [Sol R12 findings rechecked after R193](docs/reviews/2026-08-10-sol-r12-post-r193-status.md)
- [R194 Boston site and jurisdiction basis](docs/hr-v0-boston-site-jurisdiction-p0.2.md)
- [R194 interactive site-readiness guide](release/hr-v0/boston-site-p0.2/index.html)
- [R194 independent review request](docs/reviews/2026-08-10-r194-independent-review-request.md)
- [R194 validation record](docs/reviews/2026-08-10-r194-validation-record.md)
- [Sol R12 findings rechecked after R194](docs/reviews/2026-08-10-sol-r12-post-r194-status.md)
- [R195 watchdog PCB P1.15 native-identity correction](docs/hr-v0-watchdog-p115-identity-correction-p0.1.md)
- [R195 interactive watchdog identity guide](release/hr-v0/watchdog-p115-identity-p0.1/index.html)
- [R195 independent review request](docs/reviews/2026-08-10-r195-independent-review-request.md)
- [R195 validation record](docs/reviews/2026-08-10-r195-validation-record.md)
- [Sol R12 findings rechecked after R195](docs/reviews/2026-08-10-sol-r12-post-r195-status.md)
- [Mechanical P0.7/P0.6 positive-stop independent review request](docs/reviews/2026-08-07-mechanical-p0.7-independent-review-request.md)
- [Mass-reduction P0.1 independent review request](docs/reviews/2026-08-07-mass-reduction-p0.1-independent-review-request.md)
- [Gripper P0.2 independent review request](docs/reviews/2026-08-07-gripper-p0.2-independent-review-request.md)
- [Firmware P0.3 independent review request](docs/reviews/2026-08-07-firmware-p0.3-independent-review-request.md)
- [Firmware P0.2 historical independent review request](docs/reviews/2026-08-07-firmware-p0.2-independent-review-request.md)
- [Firmware P0.1 historical independent review request](docs/reviews/2026-08-06-firmware-p0.1-independent-review-request.md)
- [Requirements](requirements/requirements.csv)
- [HR-V0 energization gate register](requirements/hr-v0-energization-gates.csv)
- [Proposed bill of materials](bom/bom.csv)
- [Risk register](safety/risk-register.csv)

Run `python tools/check_traceability.py` from this directory to ensure every requirement has at least one verification method and all risk controls reference valid requirements. Run `python tools/generate_hr_v0_governance_control.py` and `python tools/check_hr_v0_governance_control_p01.py` after any requirement, risk, gate, procedure, ownership or approval-state change. Run `python tools/generate_hr_v0_electrical_v3.py --validate` and `python tools/check_hr_v0_electrical_v3.py` to regenerate and cross-check V3. Run the current PCB chain with KiCad's bundled Python: `"C:\Program Files\KiCad\10.0\bin\python.exe" tools/generate_hr_v0_watchdog_pcb.py`, `"C:\Program Files\KiCad\10.0\bin\python.exe" tools/generate_hr_v0_watchdog_pcba_assembly_data_p02.py`, `"C:\Program Files\KiCad\10.0\bin\python.exe" tools/check_hr_v0_watchdog_pcba_assembly_data_p02.py`, `"C:\Program Files\KiCad\10.0\bin\python.exe" tools/check_hr_v0_watchdog_footprint_metadata.py`, and `"C:\Program Files\KiCad\10.0\bin\python.exe" tools/check_hr_v0_watchdog_pcb.py`. The R138 P0.7/P0.8 snapshots are immutable history; never recapture or overwrite them during ordinary regeneration. PCB-P1.0 is current and directly names Electrical V3-P1.15; its internal CAM review is not a supplier release. PCB-P0.5 through P0.9 are historical; do not upload or order any of them. Run `python tools/check_hr_v0_watchdog_p115_identity_p01.py`, `python tools/generate_hr_v0_e2_hardware_slice_p04.py` and `python tools/check_hr_v0_e2_hardware_slice_p04.py` to keep the current direct P1.15 E2 exclusion boundary synchronized. `HR-V0-E2-P115-PARITY-P0.1` is historical audit evidence, not a current dependency. Run `python tools/generate_hr_v0_coordinate_convention.py` and `python tools/check_hr_v0_coordinate_convention_p01.py` after any A0/J1/J2/G1 transform, joint limit, actuator-calibration field or guard-axis change. `python tools/check_energization_gates.py --through E2 --require-ready` must remain nonzero until every applicable gate is evidenced and closed.

Run `python tools/check_hr_v0_e2_commissioning.py` to validate the fail-closed 15-step E2 sequence, 20 disconnected-load logic cases, five unexecuted evidence forms and partial-only authorization boundary. Run `python tools/check_hr_v0_r57_fabrication_sourcing.py` to verify that the current Boston route contains only held/excluded R57 candidates and unexecuted inquiry records. A passing checker is not permission to order, fabricate, or connect a source.

Run `python tools/check_hr_v0_boston_fabrication_route_p03.py` for the R167 Boston/US provider-capability refresh. Passing proves only that ten routes, ten official source records, ten open inputs and every denial flag remain synchronized; it is not provider qualification or authority to contact, upload, quote, purchase, fabricate, assemble, move or energize.

Run `python tools/check_hr_v0_xt1_terminal_group_p01.py` for R168. Passing proves exact catalog/position parity for six XT1 bodies, one end cover, zero jumpers and shared-accessory ownership without releasing a conductor, termination, label, installed terminal, point-to-point result or work authority.

Run `python tools/check_hr_v0_label_system_p01.py` for R169. Passing proves six physically short XT1 texts, 34 small device/operator records, four large legends, exact candidate material stocks and twelve open holds. It does not select a printer/service, wire markers, adhesion, regulatory markings or installed evidence, and authorizes no work.

Run `python tools/check_hr_v0_compute_storage_p02.py` for R170. Passing proves exact Kingston `SDCIT2/64GBSP` identity, three current primary source records, thirteen evidence-classed interfaces, twelve open holds and ten unexecuted receiving checks. It does not prove Pi 5 compatibility, capacity integrity, card-specific endurance, imaging, filesystem resilience, recovery, retention, current/thermal behavior or safety performance.

Run `python tools/check_hr_v0_host_deploy_p01.py` for R171. Passing proves a six-file disabled overlay, 23 current preflight failures, eighteen open closure holds, 21 unexecuted target evidence rows, six host source tests and source-manifest integrity. It does not prove an installed target image, package/interpreter identity, service permissions, GPIO or serial behavior, HIL timing, power-loss recovery, rollback, motion safety or functional-safety performance.

Run `python tools/generate_hr_v0_rpi_os_sbom_p01.py` and `python tools/check_hr_v0_rpi_os_sbom_p01.py` for R172. Passing reproduces the official 5,336,108-byte SPDX payload hash, 4,743 package records, 632 unique DPKG identities, fifteen critical-package rows and twelve blank target-verification records. It does not prove disk-image acquisition, media write/readback, target package or executable identity, booted kernel, backend selection, security, HIL, recovery, rollback or safety performance.

Run `python tools/check_hr_v0_fabrication_input_basis_p01.py` for R173. Passing proves exact trace from the existing draft 100 g / 40-70 mm object and 0.15 m/s TCP / 30 deg/s automatic-joint / 10 deg/s setup limits to ten fabrication-input rows and five arithmetic screens. It does not supply duty, acceleration, jerk, restraint, safety factors, complete loads, physical evidence, qualified acceptance or work authority.

Run `python tools/generate_hr_v0_dynamic_trace_analysis_p01.py` and `python tools/check_hr_v0_dynamic_trace_analysis_p01.py` for R174. The checker proves the unresolved physical configuration is rejected, the nominal synthetic trace computes 0.030 s / 0.435 degree / 6.065 degree results but remains on qualified HOLD, reset-driven motion fails `DTA-007`, and a sample-index/drop fault fails `DTA-001`. It does not select a physical threshold, authorize a test, or supply executed stopping/reset evidence.

Run `python tools/check_hr_v0_dynamic_instrumentation_p01.py` for R175. It verifies ten equipment rows, all fifteen dynamic channels, eight no-connect/interface boundaries, fifteen open holds, four blank receiving records, zero work authority, `EG-025` open and `EG-026` partial. It does not accept a sensor range, release procurement, authorize connection, or supply physical evidence.

Run `python tools/generate_hr_v0_dynamic_event_interface_p01.py` and `python tools/check_hr_v0_dynamic_event_interface_p01.py` for R176. Passing verifies two exact TI `ISO1212EVM` evaluation units, seven field events, exact J4/J2/J1 and T7 DB37 mappings, one FIO0-FIO7 `FIO_STATE` capture word, root plus four native KiCad child sheets at ERC 0/0, fifteen open holds and four blank receiving rows. It does not authorize a field tap: Pilz/Schneider loading, diagnostic-pulse, EDM, dropout, field-ground, timing, fault-injection, physical and qualified noninterference evidence remains open, and all test equipment has zero safety credit.

Run `python tools/generate_hr_v0_dynamic_event_ain_p01.py` and `python tools/check_hr_v0_dynamic_event_ain_p01.py` for R177. Passing verifies seven exact TI `AMC3330EVM` evaluation candidates, all seven T7 adjacent differential pairs, exact J1/J2/J3 and DB37 mappings, an eight-address sequential scan model, root plus five readable native KiCad child sheets at ERC 0/0, fifteen open holds and four blank receiving rows. It does not authorize procurement or connection: the EVM accepts only +/-1 V, is not certified by TI for high-voltage operation, and every field divider, protection value, node envelope, loading limit, timing threshold, physical result and qualified disposition remains `SELECTION REQUIRED`.

Run `python tools/generate_hr_v0_event_tap_disposition_p01.py` and `python tools/check_hr_v0_event_tap_disposition_p01.py` for R178. Passing verifies seven exact P1.15 node/terminal groups, five source-controlled manufacturer records, ten open closure holds and root plus three native KiCad disposition sheets at ERC 0/0. It proves no catalog-only field tap or divider has been released; it does not establish allowable parallel loading, transient limits, noninterference, physical timing, safety credit or work authority.
Run `python tools/generate_hr_v0_noncontact_event_observation_p01.py` and `python tools/check_hr_v0_noncontact_event_observation_p01.py` for R179. Passing verifies seven exact logical conductor locations, one exact current-probe evaluation candidate, five source records, twelve open holds, nine unexecuted E2 comparison steps, zero electrical field taps and zero safety credit. It does not prove as-built wire identity, jaw fit, compatible-host selection, simultaneity, calibration, thresholds, source/motion witnesses, noninterference, timing uncertainty or permission to perform a powered test.

Run `python tools/generate_hr_v0_event_observation_correction_p01.py` and `python tools/check_hr_v0_event_observation_correction_p01.py` for R180. Passing verifies that one false EDM-channel-independence assumption is superseded, both STOP and RESET/ARM plans allocate eight simultaneous channels, the `MSO58B`/`TCP0030A`/`TIVP02` records remain evaluation-only, no diagnostic load or connection is released and zero physical tests or safety credit exist. It does not prove probe-power compatibility, diagnostic-contact application, as-built identity, motion/source sensing, noninterference, thresholds, uncertainty or work authority.

Run `python tools/generate_hr_v0_dynamic_trace_analysis_p02.py` and `python tools/check_hr_v0_dynamic_trace_analysis_p02.py` for R181. Passing verifies two distinct eight-channel disconnected-load E2 trace schemas, nine fail-closed rules, six synthetic algorithm fixtures, one common series-EDM channel, two zero-credit diagnostic auxiliaries, control-source-valid/no-motion enforcement, unresolved physical configuration rejection and zero executed physical runs. It does not prove any physical threshold, calibration, probe compatibility, diagnostic load, powered-motion stopping result, reset behavior or work authority.

Run `python tools/generate_hr_v0_e2_acquisition_compatibility_p01.py` and `python tools/check_hr_v0_e2_acquisition_compatibility_p01.py` for R182. Passing verifies a balanced eight-channel candidate population of four `TCP0030A` and four `TIVP02/TIVPMX10X` probes at 35.8 W per MSO58B bank and 71.6 W total, plus the exact Banner `Q4XFULAF110-Q8` E2 displacement-witness candidate, six current primary-source records, fifteen open holds, zero physical compatibility runs and zero safety credit. It does not release the host configuration, cable, supply, diagnostic loads, test points, mount, target, thresholds, connection, physical test or powered-motion stopping architecture.

Run `python tools/generate_hr_v0_q4x_interface_p01.py` and `python tools/check_hr_v0_q4x_interface_p01.py` for R183. Passing verifies the exact Banner sensor, 2 m shielded cordset and pan/tilt bracket candidates; the exact Keithley isolated-supply-channel and Tektronix probe candidates; eight unreleased pin rows; six held domain boundaries; ten unexecuted calibration steps; seven current primary-source records; fourteen open holds; zero released connections/protection devices; zero robot-baseline changes; and zero safety credit. It does not select protection, terminals, enclosure, current limit, shield treatment, target, support geometry, configuration, threshold, physical evidence or work authority.

Run `python tools/generate_hr_v0_q4x_box_p01.py` and `python tools/check_hr_v0_q4x_box_p01.py` for R184. Passing verifies root plus two connected native KiCad sheets at ERC 0/0; nineteen candidate-BOM rows; fourteen current primary-source records; exact protection, terminal, enclosure, panel, gland, lock-nut, ferrule/tool and cable identities; eleven unreleased connection rows; explicit drain/remote parking; fourteen open holds; and zero procurement, fabrication, connection, powered-run or safety authority. It does not release the source current limit, exact cable procurement form/length, drilling coordinates, crimp/termination process, isolation/grounding, closed-box thermal behavior, analog fixture, calibration, physical execution or qualified review.

Run `python tools/generate_hr_v0_q4x_box_layout_p01.py`, the controlled CadQuery `cad/hr-v0-q4x-box-layout-p0.1/build.py`, and `python tools/check_hr_v0_q4x_box_layout_p01.py` for R185. Passing verifies the corrected 174.498 x 222.250 x 3.175 mm panel geometry, four catalog hole coordinates, centered 150.000 mm rail envelope, 60.800 mm device-width arithmetic, two interactive SVGs, proxy STEP/STL, twelve open holds and zero released drill holes. It does not select rail hardware, bore diameter, G1/G2 coordinates, torque, finished rating, physical assembly or work authority.

Run `python tools/generate_hr_v0_q4x_installation_evidence_p01.py` and `python tools/check_hr_v0_q4x_installation_evidence_p01.py` for R186. Passing verifies twelve source-bounded installation rows, LAPP's 1.5 N m M12 installation/cap-nut baseline, the blank separate locknut-torque certificate field, ten exact but unauthorized receiving lines, ten unexecuted metrology steps, eleven open holds and zero released holes. It does not define a through-bore, coordinates, rail hardware, modified-enclosure rating, purchase, physical work or energization authority.

Run `python tools/generate_hr_v0_q4x_unpowered_acquisition_p01.py` and `python tools/check_hr_v0_q4x_unpowered_acquisition_p01.py` for R187. Passing verifies parity with all ten R186 receiving lines, two separately decidable unpowered lots, eighteen needed evidence articles, 21 seller units including three quarantined spare locknuts, ten dated commercial-source records, a $211.30 fit-lot snapshot, a $22.83 PTCB-lot snapshot and a $234.13 combined subtotal before shipping, sales tax, fees and price movement. It does not create a cart, purchase decision, order, received part, measurement, drilling, fabrication, connection, powered test, motion or energization authority.

Run `python tools/generate_hr_v0_q4x_quote_readiness_p01.py` and `python tools/check_hr_v0_q4x_quote_readiness_p01.py` for R188. Passing verifies two direct DigiKey product-line records, exact seller codes `14F0907-ND` and `277-1464484-ND`, the corrected $211.63 fit-lot / $22.83 PTCB / $234.46 combined snapshots, and one explicit zero-stock PTCB hold. It does not prove delivery, landed cost, purchase authority, physical evidence, work authority or energization readiness.

Run `python tools/generate_hr_v0_checkout_eol_contract.py` only when deliberately changing the controlled checkout-byte contract, then run `python tools/check_hr_v0_clean_clone_audit_p01.py` for R189. The recorded external clone of commit `221035ed307f4e3501abad82cf7afa42f6e7cc36` passed 145/145 checkers under Windows with `core.autocrlf=true` and remained clean. This is reproducibility evidence only; `EG-002` remains partial and no physical or energization gate closes.

Run `python tools/generate_hr_v0_xc330_gripper_feasibility_p01.py` with the controlled CadQuery interpreter and `python tools/check_hr_v0_xc330_gripper_feasibility_p01.py` for R190. Passing verifies the exact official XC330 STEP hash and 15-solid parse, nine native custom part pairs, three mechanism poses, nominal 38-74 mm padded range, 673.774625 g incomplete feasibility subtotal, 76.225375 g shared incomplete headroom and fifteen open holds. It does not select the branch, release a gripper, close mass or force, or authorize procurement, fabrication, connection, powered test, motion or energization.

Run `python tools/generate_hr_v0_xc330_gripper_interface_p02.py` with the controlled CadQuery interpreter and `python tools/check_hr_v0_xc330_gripper_interface_p02.py` for R191. Passing verifies all four official XC330/FPX330 source hashes, the 15-solid actuator and one-solid frame imports, exact nominal two-frame registration, seven native custom part pairs, three assembly poses, the module 0.8 / 20-tooth / 20-degree involute arithmetic, the 38-74 mm nominal padded range, 679.124713 g incomplete subtotal, 70.875287 g incomplete headroom and sixteen open holds. It does not select the branch, release a tolerance, fastener, print process, guard, gripper or electrical change, or authorize procurement, fabrication, connection, powered test, motion or energization.

Run `python tools/generate_hr_v0_xc330_wrist_integration_p01.py` with the controlled CadQuery interpreter and `python tools/check_hr_v0_xc330_wrist_integration_p01.py` for R192. Passing verifies the exact H104 source hashes and one-solid parse, the H104/gripper/world transform chain, two native bridge pairs, twelve represented hole axes, seven nominal contact records, 399 endpoint-aligned 5-degree joint samples, 688.961224 g incomplete subtotal, 61.038776 g incomplete headroom and eighteen open holds. It does not select XC330, disposition `GRIP-002`, prove continuous/physical clearance or strength, release a bridge/fastener/cable/guard, or authorize procurement, fabrication, connection, powered test, motion or energization.
Run `python tools/check_hr_v0_gripper_cad_source_correction_p02.py` for R193. Passing verifies six current source states, six unique public Onshape element identities, three fail-closed branch decisions, twelve open holds and zero EG-003/005/028 closure. It does not turn the mutable Main workspace into a manufacturing release, export a file, select a gripper, permit XC330 connection to the current rail, or authorize procurement, fabrication, assembly, connection, powered testing, motion or energization.

Run `python tools/check_hr_v0_boston_site_p02.py` for R194. Passing verifies eight controlled jurisdiction/program records, eight current source records, six site-role dispositions, twenty deliberately blank premises inputs, eight open holds and zero EG-001/022 closure. It does not select a premises, determine legal applicability, qualify a fabrication provider, approve a branch/receptacle, or authorize connection, powered testing, motion or energization.

Run `python tools/check_hr_v0_control_panel.py` to cross-check the R64 25-row panel BOM, nominal allocations, exact XT1 mapping, all 66 bounded V3 wire endpoints, one fail-closed SD1 sidewall option, unreleased physical-wire fields, cable-entry holds, thermal/space screens, readable SVG warning content and twenty-two unexecuted panel records. Run `python tools/check_hr_v0_service_disconnect.py` to prove the exact `75920-01` catalog candidate remains application-held, all 15 SD1 rows remain unexecuted, and no cutout, conductor, lockout procedure or wiring release exists. Passing either checker releases no drilling, cutting, wiring, assembly, PCB fabrication, or energization work.

Run `python tools/check_hr_v0_fabrication_rfi_packets.py` to verify that every obsolete P0.1 supplier packet remains withdrawn and that zero ZIPs are active. The earlier manufacturing/route artifacts are historical inputs only until a replacement arm architecture closes `MECH-005`.
Run `python tools/check_hr_v0_safety_allocation.py` to verify that the ordinary heartbeat path retains zero safety credit and every PLr/SIL allocation remains unresolved until qualified execution.
Run `python tools/generate_hr_v0_release_manifest.py` only after deliberate package changes, then run `python tools/check_hr_v0_release_manifest.py`. A committed clean clone must additionally pass `python tools/check_hr_v0_release_manifest.py --require-clean`; this proves package identity, not fabrication or energization readiness.
Run `python tools/generate_hr_v0_bom_closure.py` after deliberate system-BOM changes, then `python tools/check_hr_v0_bom.py`. Run `python tools/generate_hr_v0_evaluation_batch_a_acquisition.py` and `python tools/check_hr_v0_evaluation_batch_a_acquisition.py` after any Evaluation Batch A identity, quantity, source, lot or price-snapshot change. Then regenerate and check the unit-level campaign with `python tools/generate_hr_v0_evaluation_batch_a_receiving.py` and `python tools/check_hr_v0_evaluation_batch_a_receiving.py`. The checkers must retain `EG-003` as partial until a complete signed machine BOM and executed receiving evidence exist; Evaluation Batch A, the R73 unpowered subset, R145 decision packet and R146 unexecuted receiving scaffold are not purchase, installation or machine-use authority.
Run `python tools/check_hr_v0_compute_selection_p01.py` for the R119 `SC1112` / `SC1158` identity package. Passing proves source/BOM/ECAD/receiving-form synchronization only; cooling, storage/image, harness, retention, site, load, PD, brownout, thermal, physical and qualified-review evidence remain open.
Run `python tools/check_hr_v0_compute_subassembly_p01.py` for R120. Passing proves synchronization of the held `SC1112` / `SC1158` / `SC1148` identities, order-code-open 64 GB storage branch, pinned/unexecuted OS image, receiving forms and partial gates only. It does not prove mounting, retention, installed load, thermal behavior, power-loss recovery, HIL or readiness.
Run `python tools/check_hr_v0_compute_installation_p01.py` for the R121 installation package as synchronized through R122. Passing proves that the enlarged `PJ302410RT` / `18P2721` branch, `PI5-CASE-D`, U2D2, three exact base/strap candidates, held `USB2AC50CM`, 26 planning envelopes, 34 panel-BOM rows, sixteen holds and twenty blank receiving records stay synchronized. It does not prove holes, fasteners, received connector/fit, bend/retention, pull/vibration, depth, thermal behavior, grounding/EMC or readiness.

Run `python tools/check_hr_v0_u2d2_usb_cable_p01.py` for R122. Passing proves that StarTech.com `USB2AC50CM`, fourteen interface controls, four trade records, four current primary-source records, eighteen blank receiving rows, sixteen blank test rows, the P0.6 panel route and fail-closed gate references stay synchronized. It does not prove received identity, connector revision, fit, bend, retention, thermal limits, enumeration, waveform/error performance, common-mode behavior, no-backfeed, EMC, HIL or readiness.

Run `python tools/generate_hr_v0_actuator_ac_cord.py` and `python tools/check_hr_v0_actuator_ac_cord_p01.py` for R147. Passing proves the held Eaton `P006-006` identity, current MEAN WELL/Eaton source facts, eighteen controls, twelve open holds, thirty blank physical records, BOM-063 exact-candidate classification and partial site/BOM/PE/mains gates. It does not prove purchase authority, received construction, premises branch, code applicability, C13/C14 fit, PE/isolation, 95 A catalog-inrush compatibility, route, temperature, connection or readiness.

Run `python tools/generate_hr_v0_mechanical_bom_binding.py` and `python tools/check_hr_v0_mechanical_bom_binding_p01.py` for R148. Passing proves that `BOM-027` binds exactly one each P0.7 `MV0-C01/C04/C05/C06/C07` to the fifteen existing hashed STEP/DXF/SVG identities and remains an exact-candidate hold with all fifteen DFM holds open. It does not authorize provider contact, file upload, quotation, purchase, first article, fabrication, assembly, motion or energization.

Run `python tools/generate_hr_v0_watchdog_pcb_bom_binding.py` and `python tools/check_hr_v0_watchdog_pcb_bom_binding_p01.py` for R149 as synchronized through R166. Passing proves that `BOM-048` binds PCB-P0.9 and `HR-V0-WD-PCBA-DATA-P0.2`, including one native PCB hash, sixteen BOM lines totaling 42 populated references, 42 placement rows, four NPTH features and twelve open assembly holds. R166 also binds current CAM P0.2 to the active P1.15 source and R165 parity evidence. Supplier-normalized XYRS, provider release, fabrication, assembly, connection, motion, energization and safety credit remain absent or false.

Generate R150 with `python tools/generate_hr_v0_watchdog_cam_p01.py`, then run `"C:\Program Files\KiCad\10.0\bin\python.exe" tools/check_hr_v0_watchdog_cam_p01.py`. Passing proves the current PCB-P0.9 source generated ten Gerber/job and five drill/map/report files, IPC-D-356, board statistics, native DRC 0 and exact 42-reference internal position parity. It also proves the position file is not supplier-normalized XYRS, all eighteen holds remain open, eleven manufacturing selections remain unresolved, no upload archive exists and every supplier/contact/quotation/fabrication/assembly/physical/connection/motion/energization/safety-credit flag remains false.

Generate R151 with `"C:\Program Files\KiCad\10.0\bin\python.exe" tools/generate_hr_v0_dxl_star_manufacturing_p01.py`, then run the matching `tools/check_hr_v0_dxl_star_manufacturing_p01.py` with the same interpreter. Passing proves DXL-STAR-P0.1 generated ten Gerber/job and five drill/map/report files, IPC-D-356, statistics, native DRC 0, exact parity for seven connector placements and eighteen terminal mappings, and four NPTH records. It also proves JC1.2 remains no-net/no-copper, all eighteen holds and eleven manufacturing selections remain open, no upload archive exists and every supplier/contact/quotation/fabrication/assembly/physical/connection/motion/energization/safety-credit flag remains false.

Generate R152 with `python tools/generate_hr_v0_dxl_injection_binding.py`, then run `python tools/check_hr_v0_dxl_injection_binding_p01.py`. Passing proves that one Electrical V3 `INJ1` and one DXL-STAR-P0.1/BOM-051 parent implement the three legacy injection branches with exact parity across eighteen terminals. It also proves BOM-035 requires no separate purchase, the parent remains held, all twelve residual boundaries remain open and every external-work flag remains false.

Generate R153 with `python tools/generate_hr_v0_dxl_harness_allocation.py`, then run `python tools/check_hr_v0_dxl_harness_allocation_p01.py`. Passing proves the three held actuator packages each already allocate one assembled 180 mm JST-JST X3P branch cable, the loose connector/contact quantities are not double-counted, and only the custom two-conductor U2D2-to-JC1 data/return cable remains to be selected and fabricated. It does not close the JST EH/XM540 current conflict or any physical-work gate.

Generate R154 with `python tools/generate_hr_v0_dxl_current_envelope.py`, then run `python tools/check_hr_v0_dxl_current_envelope_p01.py`. Passing proves the raw-current arithmetic, source binding, current-register drift monitoring, architecture disposition, blank physical records and fourteen open evidence groups are synchronized. It does not prove external current, temperature, fuse clearing, connector suitability, HIL behavior or permission to work.

Generate R155 with `python tools/generate_hr_v0_dxl_protection_evaluation.py`, then run `python tools/check_hr_v0_dxl_protection_evaluation_p01.py`. Passing proves the five-sheet native KiCad evaluation source, ERC 0/0, source identities, arithmetic, blank tests and eighteen open holds are synchronized. It does not select the candidate, release a PCB, bound reverse current or shunt pulse energy, or authorize physical work.

Generate R156 with KiCad's bundled Python using `"C:\Program Files\KiCad\10.0\bin\python.exe" tools/generate_hr_v0_dxl_protection_carrier_p01.py`, then run the matching checker with the same interpreter. Passing proves five native sheets, the four-layer single-channel carrier, 20 physical placements, three controlled assembly variants, ERC/DRC 0/0, review CAM outputs, ten blank tests and sixteen open holds are synchronized. It does not accept the drawing-derived RPW footprint, select a fabricator, release a robot PCB/BOM change, bound reverse current or authorize physical work.

Run `python tools/check_hr_v0_panel_rail_duct_p01.py` for R123. Passing proves the corrected two-stock `1207648` rail branch, `3240189` duct, six `3022218` DR1-DR3 brackets, seven planning cuts, twelve holds, three current primary sources, eighteen blank receiving rows and sixteen blank installation rows stay synchronized. It does not prove received identity, final lengths, kerf, tools, holes, fasteners, DR4 retention, bonding, pull/vibration, fill, thermal behavior, qualified review or readiness.

Run `python tools/check_hr_v0_stopping_budget_p01.py` for R124. Passing proves the active control narrative and firmware both retain J2 `15..115°`, the nominal positive metal backup remains `118°`, the 3-degree/10-degree-per-second and 3-degree/30-degree-per-second arithmetic remains 300/100 ms, all sixteen physical-test rows remain unexecuted and unauthorized, and `DF-01` retains zero safety credit. It does not establish total stopping time, release either provisional speed, validate contactors or stops, close any missing stop direction, or authorize motion or energization.
Run `python tools/check_hr_v0_power_loss_containment_p01.py` for R125. Passing reproduces the controlled `0.750 kg` mass ceiling, `0.360 m` radius, `0.720 m` vertical-excursion bound and `5.295591 J` gravitational-only input; it also proves that all seventy-two physical cases remain unexecuted/unauthorized and `EG-009` remains partial. It does not rate a guard or receiver, model continued drive/regeneration/stored energy, prove every pose, authorize physical testing or permit motion or energization.
Generate and check R126 with the controlled CadQuery interpreter using `tools/generate_hr_v0_collapse_envelope.py` and `tools/check_hr_v0_collapse_envelope_p01.py`. Passing proves the eleven known rigid bodies remain inside a continuous 338.740914 mm no-stop-credit bound, the controlled 360 mm input remains inside the 450 mm guard reservation and the P0.3 floor tray remains 114 mm below the arm envelope. It explicitly reclassifies the tray as object-catch-only; it does not prove complete gripper/cable geometry, a safety distance, an arm receiver, a physical stop, any impact/load capacity or readiness.
Generate and check R127 with the controlled CadQuery interpreter using `tools/generate_hr_v0_passive_arm_receiver.py` and `tools/check_hr_v0_passive_arm_receiver_p01.py`. Passing proves the known commanded B-Reps remain continuously above `Z = 383.106478 mm`, the candidate receiver top remains at `Z = 320 mm` with `63.106478 mm` nominal residual, and three MA30M catalog entries arithmetically total `10.507589 J`. It does not approve the absorber application, complete geometry, guides, contact layer, peak force, load path, stops, physical tests, fabrication, motion or energization.

Generate and check R128 with the controlled CadQuery interpreter using `tools/generate_hr_v0_passive_arm_receiver_verification.py` and `tools/check_hr_v0_passive_arm_receiver_verification_p01.py`. Passing proves a closed-form trigonometric method reproduces the `384.142619 mm` known-AABB boundary minimum, the serialized receiver STEP remains nominally inside the guard with a limiting `20 mm` Y margin, and Decimal arithmetic reproduces the R127 ACE and rail values. R127's lower `383.106478 mm` bound and `63.106478 mm` clearance remain the controlled candidate. R128 is internal corroboration only and closes no physical, fabrication, motion, energization or qualified-review hold.
Generate and check R129 with the controlled CadQuery interpreter using `tools/generate_hr_v0_passive_arm_receiver_detail.py` and `tools/check_hr_v0_passive_arm_receiver_detail_p02.py`. Passing proves synchronization of 16 BOM rows, seven interfaces, twelve fail-closed holds, three hole-free fabricated blanks, exact held igus `TWA-01-20` / `TS-01-20`, Sorbothane `0212037-50-10`, 80/20 `20-4113` / `11-5308` / `14122`, and ACE `MA30M` evaluation identities. It also reproduces the nominal `9.625 mm` backup gap and `1.497 mm` residual after catalog stroke. Configured rail identity, received CAD, holes, fasteners, retention, application acceptance, tolerance closure, structural allowables, anchors, physical tests and qualified review remain open. R129 is not a fabrication, motion or energization release.
Generate and check R130 with the controlled CadQuery interpreter using `tools/generate_hr_v0_receiver_guide_interface.py` and `tools/check_hr_v0_receiver_guide_interface_p01.py`. Passing proves the R129 `20 x 50 mm` tab fails the official `53 x 40 mm` TWA-01-20 K2 pattern in both orientations; synchronizes twelve manufacturer-coordinate rows, 24 controlled hole centers and ten fail-closed holds; and validates a `73 x 80 x 6.35 mm` hole-free right-angle face envelope. It does not supply received CAD, configured rail identity, hole diameters, fasteners, application approval, load proof, machining or work authorization. R130 corrects an invalid interface without releasing fabrication, motion or energization.
Generate and check R131 using `tools/generate_hr_v0_watchdog_pcb_mounting_interface.py` and `tools/check_hr_v0_watchdog_pcb_mounting_interface_p01.py`, with native KiCad DRC recorded in `project-button-v3-r131-audit-drc.rpt`. Passing reproduces the historical PCB-P0.5 VO618A defect, proves the current PCB-P0.6 source already contains the controlled 8.010 mm / 11.050 mm option-7 inner-gap/span geometry, and synchronizes four source-hole coordinates, three exact but unselected Harwin standoff candidates, twelve holds and eight blank physical-evidence rows. It does not select standoff height, screws, washers, drilling, torque, assembly process or insulation classification, and it releases no CAM, fabrication, connection or energization.
Generate and check R132 using KiCad's bundled Python for `tools/generate_hr_v0_watchdog_pcba_inquiry.py` and the controlled project Python for `tools/check_hr_v0_watchdog_pcba_inquiry.py`. Passing proves PCB-P0.7 changes only TP1-TP16 from rounded-rectangle to Harwin's exact 3.45 x 1.85 mm rectangular copper while retaining their centroids, sizes, nets and placements; synchronizes 46 board references, four provider capability routes, twenty assembly requirements, twenty-four unsent questions, fourteen holds and twenty-four blank first-article rows; and confirms every contact, upload, quote, CAM, fabrication, assembly and physical-result flag remains false. It does not constitute DFM acceptance, workmanship/process selection, a supplier response, a first article, fabrication permission or energization authority.
Generate R133 with KiCad's bundled Python using `tools/generate_hr_v0_watchdog_pcba_assembly_data.py`, then run `tools/check_hr_v0_watchdog_pcba_assembly_data.py` with the controlled project Python. Passing proves exact synchronization of 42 populated references, sixteen exact-MPN BOM lines, 38 SMD / four THT placements, four NPTH features, the 160 x 100 mm board-origin convention, native rotations, orientation controls, ten file states and twelve open holds. The coordinates are internal board-relative review data, not assembler-normalized XYRS. No Gerber/drill, fabrication stack, supplier packet, upload, fabrication, assembly or energization release exists.
Generate exact vendor-coordinate evidence with `C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe tools/generate_hr_v0_robotis_interface.py`, then run its checker. Generate the current R69 / `HR-V0-ARM-ARCH-P0.7` candidate with the same interpreter using `tools/generate_hr_v0_arm_architecture.py`, then run `tools/check_hr_v0_arm_architecture.py`. Run `tools/generate_hr_v0_mechanical_release.py` and its checker after deliberate mechanical-control changes. `HR-V0-MECH-P0.6` remains the release hold. The certificate closes nominal body between-sample clearance only and C06/C07 are analytical only; all fabrication packets remain withdrawn until bumper selection, received MTR/FAI/fit, T-slot/fastener/stop analysis, cables/guard, physical contact/stopping/tolerance proof and qualified review close `MECH-005` and `MECH-006`.
Generate and check `HR-V0-STOP-REGION-P0.1` with the CAD interpreter using `tools/generate_hr_v0_stop_region_clearance.py` and `tools/check_hr_v0_stop_region_clearance.py`. Its 6,411 sampled poses and 131 continuous certificates establish nominal free space only in the J1-minimum, J1-maximum and J2-minimum study regions. All 20 received/interface inputs remain open; no stop topology, angle, part, fabrication or motion envelope is released.
Generate and check the nonselected R70 mass-reduction study with the CAD interpreter using `tools/generate_hr_v0_mass_reduction_study.py` and `tools/check_hr_v0_mass_reduction_study.py`. Its exact-subset result and 57.983 g CAD reduction do not supersede P0.7, close `MASS-002`, or release C01R/C04R/C06R/C07R for quotation or fabrication.
Generate and check the R71 gripper integration-input package with the CAD interpreter using `tools/generate_hr_v0_gripper_integration.py` and `tools/check_hr_v0_gripper_integration.py`. It freezes official ROBOTIS meshes/URDF at exact commit `9187eca...`, provides a responsive interactive reference viewer, checks three URDF poses and records seven open holds. It is not manufacturing CAD and takes no mass, fit, guard, motion or safety credit. Generate and check the R75 fixed-guard candidate with `tools/generate_hr_v0_guard_receiver.py` and `tools/check_hr_v0_guard_receiver.py`; its 16 frame lengths, 13 sheet envelopes, 20 catalog-candidate joints and interactive guide are design evidence only. Its incomplete 30.799798 kg profile-and-sheet subtotal omits brackets, hardware, retainers, anchors, nests and cable entry; twelve explicit holds remain and no safety-distance or structural credit is taken. Generate and check the R76 retention study with `tools/generate_hr_v0_guard_retention_study.py` and `tools/check_hr_v0_guard_retention_study.py`. It excludes the drill-through `20-2496` route, adds an exact nonselected nominal 3 mm / `12004` continuous-gasket evaluation branch and screens a 19.415878 kg known subtotal. Generate and check the R77 impact basis with `tools/generate_hr_v0_guard_impact_basis.py` and `tools/check_hr_v0_guard_impact_basis.py`; it separates payload, link, runaway, detached-part and static-access cases and retains three blocking energy classes as `SELECTION REQUIRED`. No finished panel dimensions, impact rating, retention allowable, proof energy or selection is released. Generate and check the R78 dynamic-characterization input with `tools/generate_hr_v0_dynamic_characterization.py` and `tools/check_hr_v0_dynamic_characterization.py`; it defines 15 channels, 12 fail-closed stages, eight timing-evidence records and a 35-field raw schema. DYNAMIXEL telemetry remains supplemental, LabJack T7 remains a nonselected evaluation candidate, and every powered stage remains `NOT AUTHORIZED`. Generate and check the current E2 hardware slice with `tools/generate_hr_v0_e2_hardware_slice.py` and `tools/check_hr_v0_e2_hardware_slice.py`; it freezes XT1's exact catalog family and six position-to-net candidates, distinguishes 23 installed/absent/DNP/selection states, and carries twelve explicit blocking holds. Generate and check the R81 24 V interface package with `tools/generate_hr_v0_24v_interface.py` and `tools/check_hr_v0_24v_interface.py`; it freezes the exact GlobTek factory cord pin assignment and held Kycon jack allocation, plus a five-load 27.024 W control-power screen, while retaining eight protection, fit, received and physical holds. Generate and check the R82 compute/debug package with `tools/generate_hr_v0_compute_debug_interface.py` and `tools/check_hr_v0_compute_debug_interface.py`; it binds GPIO17/header pin 11 and header pin 6 return, removes the invented installed debug connector, and retains ten physical/runtime/HIL/review holds. None of these packages releases a conductor, cable, fixture, fuse link, hole, connection or powered test.

Run `python tools/check_hr_v0_gripper_cad_acquisition.py` for the R72 `HR-V0-GRIP-CAD-ACQ-P0.1` fail-closed source and datum package. It records the broken official Onshape indirection, the metadata-only Thingiverse state, the frozen GitHub reference set, two allowed closure routes, ten open datum controls, and zero measurements. The prepared ROBOTIS support query has not been sent; no complete gripper CAD or H104 transform is released.
Run `python tools/check_hr_v0_gripper_acquisition_p02.py` for the R108 orderable-subassembly correction. It must retain RM-X52 as proposed and unreleased, reject FR12-G101GM as the sole mechanism source, require HN12-I101 only as a held supplement to that alternate route, and preserve every physical and authorization hold.
Run `C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe tools/check_hr_v0_gripper_frame_source_p03.py` for the R109 source correction. It must hash/type-check all six manufacturer payloads, parse both one-solid STEP files, retain the drawings' `FOR REFERENCE ONLY` boundary, reject native coordinates as an assembly transform, and leave the complete-mechanism and H104 holds open.
Run `python tools/check_hr_v0_gripper_source_route_p04.py` for the R110 source-route correction. It must reproduce official endpoint 767, the exact Onshape identities, the view-only/export boundary, the UNSENT supplier request, and open GRH-001/GRH-002 holds without claiming a CAD payload.
Run `C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe tools/check_hr_v0_gripper_h104_source_p01.py` for the R115 H104 source-provenance correction. It must hash/type-check official endpoints 646/647/648, prove the PDF/STEP byte identity, parse the one-solid STEP, and keep GDC-001..007, GRH-001/002 and every physical/release hold open.
Run `C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe tools/check_hr_v0_pnoz_path_conformance_p01.py` for the R116 Pilz source and exact-terminal conformance record. It must hash-check manual `21396-EN-23`, verify fourteen PARTIAL/OPEN rows and exact V3-P1.13 RESET/ARM/EDM nets, prove KWD contacts are absent from both S0 returns, and retain zero safety credit plus every physical/application/authorization hold.
Run `C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe tools/check_hr_v0_contactor_application_p02.py` for the R117 K1/K2 application packet. It must verify five current source records, 33 application inputs, all 18 required-before-query rows still open, twelve NOT EXECUTED/NOT_AUTHORIZED test stages, the UNSENT Schneider request and partial `EG-013` disposition.
Run `python tools/generate_hr_v0_contactor_application_p03.py`, `python tools/generate_hr_v0_r226_contactor_sync.py`, and `python tools/check_hr_v0_contactor_application_p03.py` for R226. Passing proves exactly 16 coil/EDM plus 16 main-power terminal/net rows are identical between current P1.15 and unaccepted P1.18; binds ten local and three current Schneider sources; retains eleven open holds and partial `EG-002/004/013`; and authorizes no supplier contact, DC application, physical work, motion or energization.
Run `C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe tools/check_hr_v0_grounding_bonding_p01.py` for the R118 grounding/bonding packet. It must verify eight current source identities, exact V3 return/frame/shield node counts, fifteen controlled nodes, twelve open/partial holds, eighteen NOT EXECUTED/NOT_AUTHORIZED surveys and partial `EG-016` disposition.
Run `C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe tools/check_hr_v0_gripper_alternative_p01.py` for the R111 alternate-gripper trade study. It must hash/type-check seven manufacturer payloads, parse the Pololu and ServoCity STEP files, retain Pololu 3551 as preferred evaluation only, keep all twelve GAH holds open and release no purchase, fabrication, motion or energization authority.
Generate and check the R112 adapter with the controlled CadQuery interpreter using `tools/generate_hr_v0_pololu_gripper_adapter.py` and `tools/check_hr_v0_pololu_gripper_adapter.py`. It must reproduce the exact manufacturer transform, one-solid adapter, four-solid assembly, 25.289709 g calculated adapter mass, 117.619291 g incomplete headroom and twelve open PAH holds while keeping every release flag false.
Generate the R112 gripper electrical candidate with KiCad's bundled Python using `tools/generate_hr_v0_gripper_interface.py`; run `tools/check_hr_v0_gripper_interface.py` with the controlled CadQuery interpreter. It must hash-check five manufacturer payloads, parse four Maestro/regulator STEP solids, verify the native two-sheet project at ERC 0/0, retain logical-terminal-only pin mapping, keep FGRIP/settings/hardware/HIL evidence open and assign zero functional-safety credit.
Run `python tools/generate_hr_v0_x430_duty_characterization.py` and `python tools/check_hr_v0_x430_duty_characterization.py` for the R98 `HR-V0-X430-DUTY-P0.1` package. It must retain fifteen channels, twelve open fixture controls, twelve stages with all seven powered stages blocked, ten `SELECTION REQUIRED` acceptance equations, twelve open holds and twelve blank result rows. Its ideal current/torque table is a sensitivity only and releases no current, duty, thermal, powered-test, motion or energization value.
Generate and check the R100 adapter-interface candidate with the CadQuery interpreter using `tools/generate_hr_v0_x430_duty_fixture_interface.py` and `tools/check_hr_v0_x430_duty_fixture_interface.py`. It must preserve two nonreleased adapter candidates, five open interfaces, five provisional tolerance records, eight unsent RFI rows, fourteen open holds and every release flag false. The STEP files are RFI/RFQ-review geometry and must not be uploaded for production or fabricated.
Generate and check the R101 support-route candidate with the CadQuery interpreter using `tools/generate_hr_v0_x430_fixture_support.py` and `tools/check_hr_v0_x430_fixture_support.py`. It must retain the floor-mounted static pedestal as an inquiry candidate only, omit invented pedestal/anchor geometry, preserve the required horizontal configured-joint test, keep eight RFIs unsent, ten holds open and every release flag false. Its STEP/GLB and modified-plate model are review geometry only; they release no quotation, procurement, machining, floor work, assembly, powered test, motion or energization.
Generate and check the R102 load-rig candidate with the CadQuery interpreter using `tools/generate_hr_v0_x430_load_rig.py` and `tools/check_hr_v0_x430_load_rig.py`. It must retain the PT-600/HB-450M-2 common-bed route as an inquiry candidate only, omit buildable output-adapter, brake-riser, base-slot, anchor and guard geometry, keep eight RFIs unsent, fourteen holds open, the final configured H101 test required and every release flag false. The dedicated brake source may not be carried by the robot 24 V control rail.
Generate and check the R103 output-interface candidate with the CadQuery interpreter using `tools/generate_hr_v0_x430_output_interface.py` and `tools/check_hr_v0_x430_output_interface.py`. It must preserve the official HN12 source hashes, two-clamp-hub inquiry route, eight Ø2.2 review holes on PCD Ø16, seven non-authorizing screens, eight unsent RFIs, one partial plus eleven open holds and every release flag false. `FX103-C01` is dimensioned review geometry only: no material, GD&T, fastener, machining, assembly, powered-test or energization release exists.
Generate and check the R104 brake-support candidate with the CadQuery interpreter using `tools/generate_hr_v0_x430_brake_support.py` and `tools/check_hr_v0_x430_brake_support.py`. It must retain the corrected 20 mm PT thickness, drawing-derived 15-slot profile, Magtrol `4866` preferred inquiry route, nonfabrication Ø50 visual clearance, 104 mm/100 mm mismatch, eight unsent RFIs, two partial plus ten open holds and every release flag false. It also regenerates R102 with the corrected PT envelope. Neither the 4866 envelope nor `FX104-C01` is production CAD.
Generate and check the R105 adapter candidate with the CadQuery interpreter using `tools/generate_hr_v0_fx104_adapter.py` and `tools/check_hr_v0_fx104_adapter.py`. It must retain certified ASTM B209 6061-T651 as the material candidate, ten defined features, twelve adapter-only screens, nine unexecuted inspections, five unsent RFIs, three partial plus seven open holds and every release flag false. The STEP and SVG are a part-definition candidate for independent review, not a quotation or machining release.
Generate and check the R106 output-adapter candidate with the CadQuery interpreter using `tools/generate_hr_v0_fx103_output_adapter.py` and `tools/check_hr_v0_fx103_output_adapter.py`. It must reject the overlapping R103 one-piece geometry; retain the separate C01/C02 topology, certified ASTM A564/A564M Type 630 H1150 material candidate, fifteen feature controls, fifteen non-authorizing screens, fourteen unexecuted inspections, seven unsent RFIs, three partial plus eight open holds and every release flag false. The two STEP parts and drawing are for independent review only, not quotation, machining, assembly or powered work.
Generate and check the superseding R107 fastener-stack candidate with the CadQuery interpreter using `tools/generate_hr_v0_fx103_output_adapter_p03.py` and `tools/check_hr_v0_fx103_output_adapter_p03.py`. It must reject P0.2's 2.80 mm M2 reach shortfall, retain the two-part H1150 geometry with the corrected 3.00 mm counterbores, identify SCB2-8 and CB4-15 only as held candidates, preserve nineteen non-authorizing screens, seventeen unexecuted inspections, seven unsent RFIs, four partial plus seven open holds and every release flag false. P0.3 is not a procurement, machining, assembly or powered-work release.
Run `python tools/check_hr_v0_frame_joints.py` after any frame profile, bracket, hardware, orientation, torque-guidance, load-screen or inspection-route change. It must retain all six joints as exact candidates on hold until `INSPECT-MECH-010` and qualified mechanical disposition are executed.

## Review history through R194

One hundred ninety-four review/control rounds are complete: R01-R194. R11 Fable and R12 Sol are independent parallel reviews of the same pre-correction baseline. The resupplied Sol verdict is the same R12 analysis and is not double-counted. R13-R194 are project-owned correction, evidence-control, or validation passes, not additional independent reviews. R181 supersedes the inaccurate combined P0.1 trace contract; R182 closes only documented probe-power arithmetic and names the exact E2 displacement-witness candidate; R183 adds an unreleased cordset/bracket/supply route and calibration scaffold; R184 adds connected native KiCad with exact but unreleased protection/termination/enclosure families; R185 corrects the panel geometry and defines the centered rail/device layout; R186 binds LAPP's installation torque while preserving the blank locknut-certificate and through-bore fields; R187 creates a two-lot unsigned unpowered acquisition decision; R188 replaces two commercial ambiguities with direct seller evidence while exposing a zero-stock PTCB hold; R189 corrects machine-dependent checkout bytes plus absolute synthetic-result paths and records a 145/145 clean-clone pass; R190 adds a source-controlled nonselected XC330 gripper feasibility branch; R191 replaces its provisional frame and trapezoidal teeth with official FPX330-S101 source, exact nominal registration and a project-owned involute candidate; R192 composes that branch into the exact H104/world chain with two native bridge candidates and a 399-pose sampled screen; R193 corrects the stale broken-source record by binding the current ROBOTIS public Onshape assembly and five native part elements while retaining mutable-workspace, no-export, no-selection and XC330/current-rail holds; and R194 freezes the Boston jurisdiction basis, separates fabrication-provider capability from energization-site authority and replaces the vague site hold with twenty blank premises inputs and eight open holds. Every cart, quote, site, branch/receptacle, source-setting, procurement-form, drilling, termination, isolation, thermal, support, target, threshold, noninterference, uncertainty, gripper/wrist hardware/tolerance/strength/force/duty/guard, physical, powered-stopping, qualified-review and work-authority hold remains.

## Review state through R239

Two hundred thirty-nine review/control rounds are complete: R01-R239. R11 Fable and R12 Sol are independent parallel reviews of the original pre-correction baseline. R13-R239 are project-owned correction, evidence-control or validation passes, not additional independent approvals. R219 adds a provider-neutral route to a named competent independent functional-safety reviewer. R220-R222 reconcile current panel identities, conductor basis and explicit two-ended topology. R223 places the five unaccepted P1.18 nodes on a catalog-envelope DR5/WD4 candidate, reconciles 95 covered BOM groups and supplies 37 planning-route screens that are prohibited as cut lengths. R224 SHA-binds all thirteen actual P1.18 native KiCad sheets to their SVG exports and adds a searchable, zoomable, full-width web-review surface; it does not promote P1.18. R225-R228 bind watchdog, contactor, grounding and pre-power evidence to the current configurations. R229 proves the exact P1.15-to-P1.18 semantic boundary. R230 adds unaccepted P1.19 with identical electrical semantics and corrected visual layout. R231 reconciles all 18 Sol blockers against R230: 12 were partially addressed/open, B-005 remained an HR-V0 blocker, five remained HR-30 blockers and zero had qualified closure. R232 issues unaccepted P1.20. R233 binds its path to current Pilz/Phoenix data. R234 rejects an automatic-restart-prone low-side alternative and issues unaccepted P1.21 with direct SR1-to-SRA1 inputs and an ordinary two-contact SRA1 A1 diagnostic gate. R235 converts the remaining application gap into 13 unsent manufacturer questions, 12 response controls, ten authorization prerequisites, 15 required signals and 18 unexecuted no-load tests. R236 makes configuration-bound hash-chained logging a runtime dependency, tightens the source period bound to 10 ms and supplies blank clock, calibration and target-test acceptance routes. R237 source-reconciles the six-article Lot A metrology purchase and blocks ordering because the official XM540 page requests `-T`/TTL while its package table names `-R`; all eight supplier questions remain unsent. R238 proves P1.21 is already the single consolidated native-KiCad review candidate, with the P1.19 readable layout, P1.18 panel nodes and six exact P1.19-to-P1.21 keyed terminal changes; it does not promote P1.21. R239 freshly inspects the two logic-changed P1.21 sheets and records thirteen project visual passes with zero observed clipping/collision findings; only the project visual hold closes. Nothing was ordered, installed or physically tested and no timing/calibration result was invented. B-005 remains `PARTIALLY_ADDRESSED_OPEN`; Sol M-022 remains `PARTIALLY_ADDRESSED_OPEN`; DF-01 and the logger have zero safety credit, and manufacturer responses, protected routing, target timing, physical proof, functional-safety allocation and qualified closure remain open. P1.15 remains current; P1.18-P1.21 remain unaccepted pending independent and qualified disposition. All physical selection, calculation, received/installed and work-authorization evidence remains open. No provider is selected, contacted, quoted or supplied files. Native/repository checks do not supply DFM acceptance, FAI, received fit, structural allowables, achieved stopping performance, continuous-duty, functional-safety, qualified-review or work-authorization evidence.

## Current review state

Three hundred ten rounds are logged: R01-R310. R286-R292 established exact exterior-facet/load geometry, corrected B-Rep fidelity, exact analysis zones, a conformal mesh, failure localization, and a preregistered successor that still failed the pocket-edge quality gate. R293-R296 identified artificial tangent seams in the analysis partition rather than the physical part. R297 removed those analysis seams while preserving exact physical geometry. R298 passed every linear quality gate; R300 retained every linear gate and reduced the curved failure to three Q8 points. R303's rail refinement was rejected and R306's discrete-mesh `HighOrder` attempt produced no result. R307's CAD-resident operation reproduced R300 exactly, restored all corners and passed finite Q4/Q6/Q8 samples, but R308 found 77 of 112,646 exterior facets did not map to one exact OCC face. R309 localized them to seven zero-distance planar trimmed-face clusters. R310 proves all 255 affected nodes are unchanged from R300 and preregisters an unexecuted exterior surface-imprint correction. R279-C02, structural fields, convergence, H02, capacity, safety credit, qualified review, and every physical-work authority remain open. R11/R12 remain the independent parallel reviews; later rounds are project responses, not additional independent approvals. Nothing has been sent, ordered, received, selected, fabricated, cut, crimped, assembled, connected, powered or measured. The complete round-by-round record is in the [review ledger](docs/review-ledger.md).

Historical compatibility checkpoint: Two hundred eighty-five rounds are complete: R01-R285. R286-R302 are later controlled project responses and do not revise the evidence or authority state recorded at that checkpoint.

- [R201 interactive runtime-observation interface guide](release/hr-v0/runtime-observation-interface-p0.1/index.html)
- [R201 connected native KiCad source](electrical/kicad/hr-v0-runtime-observation-interface-p0.1/)
- [R202 interactive routed-carrier guide](release/hr-v0/runtime-observation-carrier-p0.2/index.html)
- [R202 native schematic and routed PCB source](electrical/kicad/hr-v0-runtime-observation-carrier-p0.2/)
- [R203 interactive Raspberry Pi observation pin-map guide](release/hr-v0/runtime-observation-pi-pinmap-p0.1/index.html)
- [R203 machine-readable pin allocation and holds](electrical/interfaces/hr-v0-runtime-observation-pi-pinmap-p0.1/)
- [R204 interactive Raspberry Pi observation carrier and harness guide](release/hr-v0/pi-observation-carrier-p0.1/index.html)
- [R204 native schematic, routed PCB and controlled schedules](electrical/kicad/hr-v0-pi-observation-carrier-p0.1/)
- [R205 interactive Pi/observation panel integration guide](release/hr-v0/pi-observation-integration-p0.1/index.html)
- [R205 placement, clearance, route and interface schedules](electrical/integration/hr-v0-pi-observation-integration-p0.1/)
- [R206 interactive observation field-harness guide](release/hr-v0/observation-field-harness-p0.1/index.html)
- [R206 native fourteen-page observation-integrated KiCad candidate](electrical/kicad/project-button-v3-p1.16-observation-candidate/README.md)
- [R206 field-harness engineering schedules](electrical/harness/hr-v0-observation-field-harness-p0.1/)
- [R207 interactive observation compute-harness guide](release/hr-v0/observation-compute-harness-p0.1/index.html)
- [R207 compute-harness engineering schedules](electrical/harness/hr-v0-observation-compute-harness-p0.1/)
- [R208 interactive observation compute-power guide](release/hr-v0/observation-compute-power-boundary-p0.1/index.html)
- [R208 compute-power, signal and fault schedules](electrical/interfaces/hr-v0-observation-compute-power-boundary-p0.1/)
- [R209 historical buffered observation-carrier guide — superseded](release/hr-v0/runtime-observation-carrier-p0.3/index.html)
- [R210 historical push-pull observation-carrier guide - superseded](release/hr-v0/runtime-observation-carrier-p0.4/index.html)
- [R211 current open-drain observation-carrier guide](release/hr-v0/runtime-observation-carrier-p0.5/index.html)
- [R211 native schematic, routed PCB and controlled schedules](electrical/kicad/hr-v0-runtime-observation-carrier-p0.5/)
- [R211 primary-source audit](docs/reviews/2026-08-10-r211-primary-source-audit.md)
- [R211 validation record](docs/reviews/2026-08-10-r211-validation-record.md)
- [R211 independent review request](docs/reviews/2026-08-10-r211-independent-review-request.md)
- [R212 native P1.17 observation-integrated system view](electrical/kicad/project-button-v3-p1.17-observation-p05-candidate/README.md)
- [R212 interactive configuration reconciliation P0.2](release/hr-v0/configuration-reconciliation-p0.2/index.html)
- [R212 engineering disposition](docs/hr-v0-observation-system-integration-p0.2.md)
- [R212 validation record](docs/reviews/2026-08-10-r212-validation-record.md)
- [R212 independent review request](docs/reviews/2026-08-10-r212-independent-review-request.md)
- [R213 corrected custom-part/BOM binding](docs/hr-v0-mechanical-bom-binding-p0.2.md)
- [R213 interactive corrected custom-part guide](release/hr-v0/mechanical-bom-binding-p0.2/index.html)
- [R213 validation record](docs/reviews/2026-08-10-r213-validation-record.md)
- [R213 independent review request](docs/reviews/2026-08-10-r213-independent-review-request.md)
- [R214 Sol review intake](docs/reviews/2026-08-10-sol-r214-independent-review-intake.md)
- [R214 integrated complete-arm engineering note](docs/hr-v0-arm-architecture-p0.8-dwg-integrated.md)
- [R214 interactive complete-arm evidence guide](release/hr-v0/arm-architecture-p0.8-dwg-integrated/index.html)
- [R214 interactive configuration reconciliation](release/hr-v0/configuration-reconciliation-p0.3/index.html)
- [R214 validation record](docs/reviews/2026-08-10-r214-validation-record.md)
- [R214 independent review request](docs/reviews/2026-08-10-r214-independent-review-request.md)

| Round | Review or control pass | Result |
|---|---|---|
| R01 | Initial evidence and public-claim audit | Established that the concept site was not a build package. |
| R02 | Integrated-site accuracy review | Rechecked claims, artifacts, warnings, links, and legibility. |
| R03 | Fable preliminary electrical review | Found zero connected symbols/nets and 368 ERC violations. |
| R04 | Connected electrical V2 review | Introduced reviewable native ECAD and identified residual blockers. |
| R05 | Independent Fable V2 review | Reproduced improvements and found monitored-reset and selection gaps. |
| R06 | Electrical V2.1 correction review | Reached connected 15-sheet ERC 0/0 while preserving 106 unresolved items. |
| R07 | Independent Sol system review | Identified collapse-on-power-loss, drivetrain, CAD, mass, sensing, and governance blockers. |
| R08 | Sol finding disposition pass | Added requirements, risks, gates, evidence controls, and explicit unresolved decisions. |
| R09 | Independent Fable claim/configuration audit | Confirmed electrical counts and found revision and deployment drift. |
| R10 | Systems-baseline correction | Established `HR-30-SYS-R0.2` and synchronized the corrected deployment. |
| R11 | Independent Fable engineering review | Complete: 7 BLOCKER, 11 MAJOR, and 12 MINOR findings; disposition recorded. |
| R12 | Independent GPT Sol engineering review | Complete: 18 BLOCKER, 30 MAJOR, and 8 MINOR findings against the same baseline as R11. |
| R13 | ECAD provenance correction | Added the controlled native KiCad V2.1 tree and hash manifest to the authoritative repository. |
| R14 | R11 engineering correction pass | Corrected mass, torque, speed, battery, TCP, watchdog, safety-function, verification, interface, and public-fabrication-control defects without releasing unresolved hardware. |
| R15 | R12 archival and reconciliation pass | Preserved Sol's complete dossier, dispositioned all 56 findings, and corrected processor ownership, duplicate release evidence, and qualitative IMU labeling. |
| R16 | Native Electrical V3 candidate correction | Added and validated the ten-page connected V3-P0.1 candidate while retaining 29 unresolved interfaces and no energization approval. |
| R17 | Restart-chain and firmware implementation candidate | Moved watchdog contacts into the two SR1 input returns, added fail-closed watchdog/supervisor source, 17 executable unit tests and a source manifest; compiled binaries and HIL remain open. |
| R18 | Watchdog terminal and feedback-interface correction | Froze official Phoenix/Pico terminals, removed a modeled 24 V-to-GPIO path, and added explicit unreleased feedback-interface blocks as Electrical V3-P0.3. |
| R19 | Watchdog feedback circuit correction | Replaced the opaque blocks with an exact ISO1212DBQ pinout and calculated threshold, wetting, filter, GPIO and decoupling networks as Electrical V3-P0.4; PCB, order codes and physical evidence remain open. |
| R20 | Mechanical frame-interface evidence correction | Added a hashed `MV0-FC01` PCD22 coupon package, controlled 1:1 overlay, unpowered inspection procedure and record template; execution and production release remain open. |
| R21 | Mechanical interface-topology correction | Found and removed an invalid symmetric PCD22 assumption; separated H101 output, S102 body-frame, and unresolved gripper interfaces; added `MV0-FC02`, frame-kit receiving controls, fastener stack math, and manifest-pipeline validation. |
| R22 | Hard-stop kinematic and load-case definition | Added checked stop datums, allocated-mass energy and drive-force screens, an unpowered inspection, and a guarded incremental validation route without inventing a bumper or impact rating. |
| R23 | HR-V0 moving-mass traceability and closure correction | Added `MASS-002`, a 13-row controlled ledger, reproducible 565.4 g known subtotal, 184.6 g unresolved headroom, measurement form, and review procedure while keeping mass closure open. |
| R24 | HR-V0 gripper interface and evidence correction | Selected an orderable ROBOTIS parent kit and exact mechanism allocation, added the `MV0-FC03` 24 x 12 mm physical-fit coupon, guarded-use requirement, receiving/interface records, and primary-source hashes while keeping force, guard, mass, fasteners and proof open. |
| R25 | HR-V0 guard, receiver and moving-cable space correction | Added a generated enclosure/catch STEP envelope, readable layouts, explicit provisional stopping/clearance terms, five cable zones, three requirements, three procedures and unexecuted guard/cable/drop records; no panel, harness or safety distance is released. |
| R26 | Electrical operator and regional-source identity correction | Advanced the connected candidate to V3-P0.5; froze black RESET and green ARM IDEC operator order codes plus the official Raspberry Pi US regional model, added receiving/continuity evidence controls, regenerated all native/exported artifacts, and retained 43 unresolved rows and 64 `TBD-*` terminals. |
| R27 | E-stop terminal-position closure | Advanced the connected candidate to V3-P0.6; replaced four anonymous S0 terminals with controlled right/left NC position designators, retained received positive-opening verification, documented the active IDEC HW production transition, and kept RESET/ARM terminals unresolved. ERC remains 0/0; 43 unresolved rows and 60 `TBD-*` terminals remain. |
| R28 | Source-interface candidate closure | Advanced the connected candidate to V3-P0.7; froze the project-side Molex JA1 housing/HCS contact/tool system and TRACO watchdog-regulator order code/pins, added receiving/current-division/thermal/brownout evidence controls, reduced anonymous terminals to 56, retained 43 unresolved rows, and closed no energization gate. |
| R29 | Heartbeat and relay-driver circuit closure | Advanced the candidate to V3-P0.8; replaced anonymous heartbeat and coil-driver blocks with an exact VO618A optical path, exact passives, two separate TPL7407LPWR packages and COM bypass candidates; added pin/net assertions and a physical HIL/fault test record; retained 47 unresolved evidence rows and closed no energization gate. |
| R30 | Watchdog-feedback passive closure | Advanced the candidate to V3-P0.9; froze exact proposed order codes for all 13 ISO1212 support passives, added pin/value assertions plus a receiving/derating record, retained 47 unresolved evidence rows, and closed no energization gate. |
| R31 | Watchdog PCB boundary and placement-source pass | Advanced the schematic candidate to V3-P1.0; added exact board terminal candidates and project pin allocation, a native 26-reference PCB-P0.1 placement source, custom footprints, DRC/render evidence and an inspection record. The board intentionally has zero tracks/zones and 68 unconnected pads, so fabrication and energization remain blocked. |
| R32 | Watchdog PCB package and constrained-placement correction | Found that P0.1 used a non-matching ISO1212 footprint and placed the field-input network on the wrong side. Issued unrouted PCB-P0.2 with the correct 3.9 x 4.9 mm, 0.635 mm-pitch DBQ candidate, corrected field/control zoning, machine-checked TI placement screens, zero non-routing DRC violations and the same explicit 68-pad routing gate. |
| R33 | Watchdog PCB routed-copper candidate and independent connectivity pass | Issued PCB-P0.3 with 160 segments, 45 vias and one filled return zone; native KiCad DRC is 0/0 and the checker proves every multi-pad net connected, 18 deliberate singleton nets isolated and 89 no-net pads untouched. No fabrication outputs, physical evidence or energization approval were released. |
| R34 | Watchdog PCB test-access and ISO1212 SUB-copper pass | Issued Electrical V3-P1.1 / PCB-P0.4 with 16 Harwin S1751-46R test points, separate 2 mm x 2 mm floating SUB planes, 200 segments, 56 vias and three filled zones. Native DRC remains 0/0 and no fabrication or energization release was issued. |
| R35 | Watchdog PCB fabrication-envelope pass | Issued PCB-P0.5 with every former 0.10 mm feature rerouted at 0.1524 mm minimum and a proposed source-backed OSH Park two-layer process. Native DRC remains 0/0; no fabrication outputs or energization release were issued. |
| R36 | Protection and conductor-coordination input pass | Added exact proposed holder/distribution hardware and fuse family, six machine-checked input rows, three procedures and an unexecuted evidence form while retaining zero fuse ampere ratings. Exposed the XM540 4.4 A stall versus JST EH 3 A series conflict; EG-014 is partial, not closed. |
| R37 | DYNAMIXEL star-injection native-ECAD correction | Issued Electrical V3-P1.2 plus a separate routed DXL-STAR-P0.1 source with three isolated positive branches, common TTL data/return, an unrouted U2D2 VDD pin, ERC/DRC 0/0 and physical evidence controls. Cable, current, thermal, waveform, no-backfeed and fabrication evidence remain open. |
| R38 | Actuator current-envelope and torque-enable configuration correction | Added a guarded raw 800/300 current candidate, exact mode/readback rules, a fail-closed executable validator, eight tests and an external characterization route. Internal current is not treated as branch-current proof; the XM540/JST conflict and all physical gates remain open. |
| R39 | Pico watchdog platform and reproducible-build correction | Added exact default-off Pico GPIO binding, a 100 ms hardware watchdog, pinned publisher-verified tools, strict target compilation, static size/stack evidence and matching ELF/UF2/BIN/HEX/map/disassembly across two clean builds. The binary remains unflashed; HIL and EG-017 remain open. |
| R40 | Watchdog clock-model and compiled-C correction | Reconciled C/Python 32-bit wrap and regression semantics, added a latched clock fault, matched compiled C to the model for 44 steps in nine scenarios, and issued reproducible Pico P0.2 plus host-vector artifacts. Target HIL and EG-017 remain open. |
| R41 | K1/K2 DC application-evidence correction | Issued Electrical V3-P1.3 with current Schneider three-pole-series and mirror-contact evidence, corrected the misleading 25 A BOM shorthand, and exposed the catalog's lower-current critical-current warning for the 11.1 A HR-V0 screen. EG-013 remains partial pending written application disposition and physical loaded tests. |
| R42 | RESET/ARM received-lot terminal-control correction | Issued Electrical V3-P1.4 after current IDEC evidence confirmed that prior or redesigned HW internals may ship under unchanged complete order codes and the live BOM exposes no component identity. Retained exact black RESET and green ARM complete assemblies, kept all four terminals `TBD-*`, added a lot-specific inspection/continuity form and vendor query, and left EG-011 partial. |
| R43 | HR-V0 flat-plate process and first-article correction | Reclassified `MV0-001` through `MV0-003` as CNC mill/drill RFQ parts, held `MV0-004` behind the bench survey, added machine-checked process evidence, drawing RFQ notes, supplier DFM/FAI records and `INSPECT-MECH-009`. EG-006 remains partial; no cutting or energization release was issued. |
| R44 | Functional-safety allocation and watchdog-credit correction | Classified the ordinary heartbeat path as zero-credit `DF-01`, separated credited-candidate `SF-01/SF-03`, physical `PG-01`, and future `SF-02`, added an eleven-case FMEA plus qualified allocation controls, and left EG-012 partial. No PLr/SIL or energization release was issued. |
| R45 | Deterministic HR-V0 release-candidate configuration | Issued `HR-V0-RC-P0.1` metadata plus an all-file SHA-256 manifest and clean-clone checker, reconciled the stale V3 identifier in configuration management, and kept EG-002 partial pending immutable acceptance and signatures. No build or energization release was issued. |
| R46 | HR-V0 BOM closure and evaluation boundary | Expanded the system BOM from 57 to 70 groups, exposed thirteen missing assembly dependencies, classified every row, froze seventeen exact evaluation-only candidates with receiving routes, and advanced EG-003 from open to partial. Thirty-three groups remain `SELECTION REQUIRED`; no blanket procurement, fabrication or energization release was issued. |
| R47 | HR-V0 mechanical datum/interface correction | Issued `HR-V0-MECH-P0.2` with 24 parameters, 12 interfaces, 19 assembly groups, five exact extrusion cuts, six datums, a generated general arrangement and inspection route. Corrected inconsistent assembly transforms/anchor orientation and removed misleading structural STL. EG-005 through EG-008 remain partial; no cutting, assembly or energization release was issued. |
| R48 | HR-V0 exact catalog frame-joint correction | Issued `HR-V0-FRAME-P0.1`: six enumerated `40-4334` brackets, twenty-four `75-3422` assemblies, an 11.49 N m load-path screen, manufacturer 13–20 N m trial guidance, and `INSPECT-MECH-010`. Actual-joint torque, slip/proof, bench anchors and qualified disposition remain open; no assembly or energization release was issued. |
| R49 | HR-V0 frame collision and bracket-topology correction | Superseded defective `HR-V0-FRAME-P0.1` with `P0.2`; changed the two transverse cuts from 320 to 240 mm, placed the upright on the base top, replaced incompatible two-slot-wide `40-4334` with six `40-4332` brackets and twelve `75-3422` assemblies, enumerated six bracket ridges, and added a fail-closed positive-volume overlap check. Received fit/tool access, torque, slip/proof and qualified review remain open; no procurement, fabrication, assembly or energization release was issued. |
| R50 | Boston fabrication-route and profile-blank correction | Issued `HR-V0-FAB-RFQ-P0.1` with seven machine-checked routes, two one-stop CNC candidates, a controlled two-process route, three native hole-free STEP/DXF blank packages, a quote/DFM form and explicit BPL/FabVille limitations. Supplier selection, coupon execution, finished tolerances, first article, FAI and qualified review remain open; no procurement, fabrication, assembly or energization release was issued. |
| R51 | Deterministic supplier-inquiry and exact-bench control | Issued `HR-V0-FAB-RFI-P0.1` with three route-bounded deterministic ZIPs, internal/outer SHA-256 manifests, fail-closed membership checks, an exact-bench survey form, `MECH-004` and `INSPECT-MECH-011`. No packet exists for the site-held anchor part; no supplier response, drilling, fabrication, assembly or energization release was issued. |
| R52 | Cross-checkout packet-portability correction | Clean-clone validation found R51 packet payloads depended on CRLF/LF checkout state. Canonicalized controlled text inputs and release CSV output to LF, regenerated all packet identities, and required committed-packet verification plus zero-diff, clean-worktree regeneration in a fresh clone. No supplier, fabrication, assembly or energization release was issued. |
| R53 | Exact ROBOTIS frame-orientation supersession | Imported the controlled XM540/H101/S101/S102/H104 STEP files without transforms, proved the P0.2 flat-link/adapter assumption did not define the required 3D frame interfaces, blanked the J1/J2/G1/OMAX chain, withdrew MV0-001 through MV0-003 and every supplier ZIP, and added `MECH-005` / `AUDIT-MECH-012` for a replacement exact-coordinate architecture. No fabrication or energization gate closed. |
| R54 | Exact-coordinate arm architecture candidate | Rolled the J2 XM540/S102 +90° with a -90° output reference, proved parallel J1/J2 axes at a candidate 191.5 mm spacing, reserved 50.5 mm for the gripper/TCP inside the 360 mm reach ceiling, generated STEP/GLB/SVG and explicit transforms/interfaces, sampled 23 collision-free elbow poses, and updated gravity screens to 1.762/0.478 N·m. Exact member/end machining, adapters, fasteners, cables, complete sweep and proof remain open; no fabrication or energization gate closed. |
| R55 | Corrected actuator/frame/link architecture and collision boundary | Superseded R54 after finding its raw XM540 orientation, PCD22 link pattern and horizontal end-tap pair were incorrect. `HR-V0-ARM-ARCH-P0.2` registers the XM540 to S102, uses the ROBOTIS rectangular frame pattern and vertical 20-2040 members, adds candidate fastener/tool/load screens, and records first modeled contact at 122° from a 221-pose sweep. The 120° software ceiling is provisional pending a hard stop, stopping-overtravel/uncertainty proof, continuous collision proof, adapter local-strength closure, received fit, FAI and qualified review; no physical gate closed. |
| R56 | Strengthened adapter and exact fastener-candidate correction | Superseded the 4.7625 mm P0.2 adapter with a 9.525 mm nominal, 9.0–10.0 mm finished P0.3 candidate; minimum residual below the worst-case countersink is now 5.9 mm. Froze `WF2563`, `WF2339`, and `WF1254` as exact candidates on hold and regenerated the 202.55/129.05 mm datum chain, load screens and deterministic STEP/GLB/SVG evidence. Typical material values are not allowables; certified material, local analysis, received stacks, torque/locking rules, proof, FAI and qualified review remain open. No physical gate closed. |
| R57 | Adapter fabrication-definition correction | Superseded P0.3 with `HR-V0-ARM-ARCH-P0.4`: exact OnlineMetals `1249` certified-stock candidate, controlled drawing/DXF and ten FAI controls, exact current Accu/MISUMI fasteners, receiving records and ten analytical screens using a three-times-gravity proof-load candidate. Physical fit, MTR/FAI, torque/locking, proof, collision/stopping margin and qualified acceptance remain open. No physical gate closed. |
| R58 | E2 control-only commissioning boundary | Added `HR-V0-E2-SEQ-P0.1`, a 15-step fail-closed sequence, five evidence forms, 20 disconnected-load safety-logic cases and a checker. Corrected the stage ambiguity: E2 may verify logic with the actuator source physically absent, but it cannot claim loaded interruption, stopping distance or PL/SIL validation. EG-018 through EG-022 advance from empty/open to template/partial only; all 21 E2 gates remain unresolved and no authorization exists. |
| R59 | Current Boston fabrication-sourcing reconciliation | Replaced stale live guidance for withdrawn `MV0-001/002/003` with `HR-V0-FAB-SRC-P0.2`, tied to four R57 `MV0-C01` adapter candidates, two 20-2040 members and a separate bench-anchor hold. Added eight held/excluded routes, seven unexecuted inquiry rows and a checker. No supplier, upload artifact, quote, first article or fabrication authorization exists. |
| R60 | HR-V0 control-panel physical-definition correction | Issued `HR-V0-CP-P0.1` with exact enclosure/backplate, rail/duct/terminal and amber H1 catalog candidates on hold; 16 backplate allocations; five door rows; six XT1 positions; all 66 bounded V3 wire endpoints; six no-hole cable-entry zones; ten thermal/space screens; 20 unexecuted evidence rows; and a checker. No holes, cuts, conductors, protection ratings, PE bond, glands, PCB fabrication, assembly or energization work is released. |
| R61 | H1 pilot-light configuration and received-evidence correction | Issued Electrical V3-P1.5 with exact amber IDEC `HW1P-1FQD-A-24V`, replaced misleading `SAFE ELIGIBLE` and `+/-` labels with diagnostic-only wording and `TBD-HA/TBD-HB` project placeholders, moved system `BOM-041` to exact-candidate hold (18 exact / 29 selection-required), synchronized all native/exported artifacts, and added fourteen unexecuted receiving/characterization records. ERC remains 0/0; 63 unresolved rows and 24 `TBD-*` terminals remain. No wiring or energization release exists. |
| R62 | Control-panel fit and protection-holder correction | Proved the P0.1 protection reserve could not contain the catalog fuse hardware; issued `HR-V0-CP-P0.2` around Hammond `PJ242010RT` / `18P2117`, exact Phoenix `3211861` FSR1/FSR2 holder candidates and the exact Blue Sea/Littelfuse branch/main holder envelopes. Issued Electrical V3-P1.6 and synchronized the holder identity while leaving all six fuse links, end cover, coordination, conductors, holes and assembly unresolved. The system BOM is now 72 groups (19 exact holds / 29 selection-required); ERC remains 0/0 and no gate closed. |
| R63 | FSR end-cover identity and SD1 application-screen correction | Issued Electrical V3-P1.7 / `HR-V0-CP-P0.3`; froze Phoenix `D-ST 4` item `3030420` only as the FSR group end-cover candidate; expanded the system BOM to 73 groups (20 exact holds / 29 selection-required); and added a 15-row unexecuted SD1 application/receiving route. Blue Sea `6004200` remains a screened candidate, not a selected disconnect, because conductor, fault/load-break, lockout, placement and jurisdiction evidence are open. ERC remains 0/0 and no gate closed. |
| R64 | Exact SD1 catalog-candidate and sidewall-integration correction | Issued Electrical V3-P1.8 / `HR-V0-CP-P0.4` / `HR-V0-SD-P0.2`; froze active Littelfuse `75920-01` as the exact SPST high-side catalog candidate while retaining `TBD-IN/TBD-OUT`, conductor/lug, source-fault, load-break, touch-protection, placement, padlock procedure, human-factors and Boston application holds. The system BOM remains 73 groups (21 exact holds / 28 selection-required). No hole, wire, lockout, fabrication, gate closure or energization release exists. |
| R65 | Fail-closed DYNAMIXEL transport and execution-boundary correction | Issued `HR-V0-FW-P0.2` / `HR-V0-DXL-TRANSPORT-P0.1`; pinned official SDK 4.0.5, implemented torque-off-before-discovery, exact identity/configuration readback, trajectory-bound synchronous writes and fault-triggered torque removal, and added nine physical HIL cases. The committed configuration still refuses to open a serial port because received identities, calibration, profiles, device path and physical limits are unresolved. EG-017 remains partial; no hardware was connected or energized. |
| R66 | Integrated column-to-gripper mechanical candidate | Issued `HR-V0-MECH-P0.4` / `HR-V0-ARM-ARCH-P0.5`; closed A00 and A07 source geometry with native C05 and C04 STEP/DXF/drawing controls, synchronized J1/J2/G1 datums, exact candidate hardware and H104/S102 feature evidence, and expanded collision screening to 40,001 J1/J2 poses. No sampled contact occurs through provisional J2=120°; first nominal contact is 122°. Received fit/MTR/FAI, T-slot proof, torque/locking/reuse, continuous collision, cables/guard, backed-up hard stop, stopping overtravel, physical proof and qualified review remain open. No quotation, fabrication, motion or energization gate closed. |
| R67 | Continuous nominal collision and J2 allocation correction | Issued `HR-V0-MECH-P0.5` / `HR-V0-ARM-ARCH-P0.6` / `HR-V0-HS-P0.2`. Certified all 70 non-intentional rigid-body pairs continuously through J2=120° with a 0.75 mm required floor and 0.765783 mm minimum guaranteed lower bound; numerically located first nominal contact at 121.643289°; lowered the candidate software ceiling to 115° and recorded an unreleased 118° backed-up-stop datum with explicit 3° stopping and 2.643289° physical-uncertainty budgets. Tolerances, deformation, cables/guard, actual stop CAD, measured stopping, physical proof and qualified review remain open. No quotation, fabrication, motion or energization gate closed. |
| R68 | Mechanical-to-control limit binding correction | Found that the active supervisor still allowed J2 to 125° after R67 allocated 115°. Issued `HR-V0-FW-P0.3` / `HR-V0-SUP-P0.2` / `HR-V0-ACT-P0.2` / `HR-V0-DXL-TRANSPORT-P0.2`; bound command screening and raw conversion to the exact P0.5/P0.6/P0.2 mechanical identifiers and 15–115° envelope; and added fail-closed tests for stale 120°, revision mismatch and missing acceptance evidence. The committed binding remains unreleased and cannot open the actuator port. No hardware, HIL, fabrication, motion or energization gate closed. |
| R69 | J2 positive-stop CAD and binding synchronization | Issued `HR-V0-ARM-ARCH-P0.7`, `HR-V0-MECH-P0.6`, `HR-V0-HS-P0.3`, and `HR-V0-J2-STOP-P0.1` with twin outside C06/C07 rails, nominal metal contact at 117.999985°, separate stop/tolerance/load evidence, and a 69-pair body-clearance certificate. Issued fail-closed firmware/configuration P0.4/P0.3 identifiers for the current mechanical binding. Bumper selection, physical contact/stopping/proof, received evidence and qualified review remain open; no fabrication, motion or energization gate closed. |
| R70 | Same-interface moving-adapter mass-reduction study | Issued nonselected `HR-V0-MASS-REDUCTION-P0.1` with four exact-subset relieved candidates. Four-part CAD-estimated mass falls by 57.983 g and the incomplete subtotal would become 634.775 g, but detailed stress/impact/fatigue, material, tolerance, received fit, FAI, measured mass/COM, proof and independent review remain open. P0.7 remains controlled; no fabrication, motion or energization gate closed. |
| R71 | Exact-source gripper integration-input correction | Froze official ROBOTIS `link5`/palm meshes and URDF at commit `9187eca...`; added a responsive interactive geometry guide, three checked URDF poses, a parameterized mass/load table and seven explicit integration holds; and corrected the stale gripper mass-ledger references to `V0M-014..016`. The public meshes are not manufacturing CAD, the H104 transform and usable opening are unverified, and no mass, guard, motion or safety credit was taken. |
| R72 | Gripper CAD acquisition and datum-control correction | Recorded six current primary-source states, including the broken official Onshape indirection and metadata-only Thingiverse route; added publisher-file and received-part-metrology closure paths, ten open datum controls, 27 unexecuted acquisition/metrology rows and `AUDIT-GRIP-002`. No vendor was contacted, no geometry or measurement was received, and every gripper hold remains open. |
| R73 | Unpowered mechanical evaluation reconciliation | Restored two exact FR13-S102K sets to Evaluation Batch A after R69 fixed the P0.7 architecture; changed BOM-023 from exact hold to evaluation candidate; added a seven-line, nine-article unpowered receiving subset; and machine-checked exact parent/order-code/quantity parity. The batch remains program-owner-approval-required and supplies no purchase, assembly, motion or energization authority. |
| R74 | Dimensioned fixed guard and receiver correction | Issued `HR-V0-GUARD-P0.2` with source STEP/GLB, readable SVG, responsive interactive guide, sixteen frame-length and eight panel-envelope candidates, twelve explicit holds, and twelve current P0.7 inspection cases. Frame/profile products, transparent-sheet grade, joints, retention, anchors, stopping, sweep, access, impact and qualified review remain open; the 450 mm radius is not a safety distance and no fabrication or motion authority exists. |
| R75 | Guard catalog-candidate, cut-schedule and mass correction | Issued `HR-V0-GUARD-P0.3`; bound the 16-member frame to exact 80/20 `20-2020`, `14201` and `75-3581` catalog candidates; bound all 13 sheet pieces to Plaskolite TUFFAK GP clear nominal 6 mm; and screened a 30.799798 kg incomplete profile-and-sheet subtotal. Retainer quantity/pattern, received identity, allowables, joints, anchors, cable entry, proof and qualified review remain open. No purchase, fabrication, assembly, motion or energization authority exists. |
| R76 | Guard retention and mass-branch correction | Excluded the drill-through `20-2496` route from the current retention baseline; added exact `12004` only as a nonselected continuous-gasket candidate for nominal 3 mm outer panels; retained the 6 mm receiver; and screened a 19.415878 kg known subtotal, 11.383920 kg below P0.3. Finished panel dimensions, impact energy, retention capacity, temperature fit, physical proof and qualified selection remain open. |
| R77 | Guard impact-energy allocation correction | Separated foam-payload, moving-link, continued-drive, detached-hardware and static-access hazards; calculated eight bounded subcases/sensitivities; retained three blocking cases as `SELECTION REQUIRED`; and added six direction rows plus twelve fail-closed test controls. No panel, retention system, test energy, impact rating or physical gate was released. |
| R78 | Dynamic-characterization measurement correction | Defined an external hardware-timed evidence chain with 15 channels, 12 gated stages, eight open timing records and a 35-field raw schema. ROBOTIS bus data is supplemental, the T7 is a nonselected evaluation candidate, and all powered stages remain `NOT AUTHORIZED`. |
| R79 | E2 configuration and XT1 reconciliation | Issued Electrical V3-P1.9 and `HR-V0-E2-HW-P0.1`; froze XT1's five Phoenix item identities and six position-to-net candidates, reduced deliberate `TBD-*` terminals from 24 to 18, and separated 22 installed/absent/DNP states. The unresolved register remains 63 because XT1 still requires conductor, protection and physical verification. Twelve E2 hardware holds remain; no procurement, wiring, connection or energization is released. |
| R80 | 24 V source-interface correction | Issued Electrical V3-P1.10 and `HR-V0-24V-IF-P0.1`; replaced the ambiguous system `JC1` block with standard KiCad references `J24` and `F24`, froze the held Mean Well `DC PLUG-P1J-R7B` / Kycon `KPJX-PM-4S` catalog and pin-allocation candidates, and separated branch protection. Deliberate `TBD-*` terminals fall to 14 while unresolved rows rise to 65 because PSU2 compatibility, J24 application/physical evidence and F24 selection are all explicit holds. No order, hole, PCB/harness, connection or energization is released. |
| R81 | 24 V factory-cord and load-budget correction | Issued Electrical V3-P1.11, `HR-V0-24V-IF-P0.2` and `HR-V0-E2-HW-P0.2`; replaced the unsupported P1J conversion chain with exact GlobTek `WR9QI1660YL4NKITR6B` and its factory YL4/C40337 cord, mapped pin 1 to +24 V and pin 3/shield to return while keeping pins 2/4 intentionally unconnected, retained Kycon `KPJX-PM-4S` as an application-held candidate, and added a 27.024 W / 1.126 A control-load screen. Received plug identity/fit, exact H1 current, startup/simultaneous pickup, F24, conductors, thermal and fault behavior remain open. No order, hole, wiring, connection, powered test or energization is released. |
| R82 | Compute-heartbeat and watchdog-debug reconciliation | Issued Electrical V3-P1.12 and `HR-V0-COMPUTE-IF-P0.1`; removed the invented installed `JDBG1` connector; bound Pi BCM GPIO17 to physical header pin 11 with pin 6 compute return; and limited debug access to existing exact Harwin TP15/TP16/TP2 test points. Harness, GPIO runtime, startup, waveform/timing, HIL, programmer, unpowered fixture, no-back-power proof, EMC/retention, receiving and qualified review remain open. No cable, fixture, programming connection, powered debug, safety credit, fabrication or energization is released. |
| R83 | Hard-stop region clearance and interface acquisition | Issued `HR-V0-STOP-REGION-P0.1`; checked 6,411 boundary poses and 131 continuous pair-region certificates with a 5.743912 mm conservative nominal lower bound; and defined 20 open received/interface inputs plus candidate/rejected topology controls. The historic study regions are nominally free, but no angle, topology, stop part, fabrication, motion or energization is released. |
| R84 | Unpowered J1/J2 acquisition and metrology correction | Issued `HR-V0-JOINT-MET-P0.1`; allocated six exact received articles, eighteen operations, eight hard hold points, six instrument classes, a raw evidence form and a route for all twenty HSI inputs. Corrected unpowered angle evidence to use an external mechanical datum rather than an unavailable encoder reading. No purchase, threaded temporary assembly, physical result, motion or energization is authorized. |
| R85 | Evaluation acquisition and Boston metrology quote correction | Issued `HR-V0-EVAL-ACQ-P0.1`; recorded three exact cost lines covering six articles and a $1,182.22 official-web-price subtotal before extras; screened four uncontacted provider candidates; and added twenty-four quote questions, ten open holds and separate unsigned authorization/response templates. No cart, contact, order, shipment, work, measurement, motion or energization is authorized. |
| R86 | Watchdog dependent-failure and common-cause correction | Issued `HR-V0-WD-CCF-P0.1`; mapped 18 exact V3 paths, expanded the FMEA to 32 cases, defined 12 common-cause groups, 28 unexecuted cases and 16 separation controls, and exposed the KWD A1/21-to-14 voltage-injection blocker. Topology non-interference is not proved; DF-01 retains zero safety credit; no test, wiring, motion or energization is authorized. |
| R87 | Watchdog-gated SR1 supply correction | Issued Electrical V3-P1.13, `HR-V0-CP-P0.5` and `HR-V0-WD-SUPPLY-P0.1`; made both S0 channels direct to SR1 and moved KWD1/KWD2 into a series gate on `SR1:A1`. The old encoded KWD-to-E-stop-return injection path is removed, but physical noninterference, contact duty, routing, recovery, fault injection, PLr/category and qualified review remain open. No fabrication, wiring, motion or energization is authorized. |
| R88 | Watchdog PCB CAM and physical-evidence route | Issued `HR-V0-WD-FAB-P0.1` and `HR-V0-WD-TRAVELER-P0.1`; generated a checksummed KiCad 10.0.5 CAM review candidate with DRC, Gerbers, PTH/NPTH drills, placement, IPC-D-356, statistics and a 42-reference candidate BOM; added 24 CAM, 18 receiving/assembly, 16 current-limited bring-up and 13 inspection records. Fourteen fabrication holds and all physical rows remain open/unexecuted. No supplier upload, order, fabrication, assembly, energization or safety credit is authorized. |
| R89 | Watchdog PCB land-pattern and assembly-process correction | Audited all 42 schematic references and four board-only holes; found the ISO1 isolation-land blocker, undocumented TI alternate lands and seventeen passive-process mismatches; issued PCB-P0.6 with 86 corrected source lands and a proposed mixed reflow/manual-THT sequence; preserved DRC 0/0; and superseded the immutable PCB-P0.5 CAM set for current fabrication review. No PCB-P0.6 CAM, assembler acceptance, physical evidence, fabrication, assembly or energization authority exists. |
| R90 | Boston custom-metal route and thickness correction | Rejected the incompatible 4.75 mm SendCutSend advice against P0.7's 9.525 mm parts; compared six provider/process routes against nine current primary records; excluded SendCutSend as a finished-part route because its published tolerance and M5 countersink conflict with the controlled features; identified Xometry/Protolabs as held high-requirement CNC inquiry candidates and Artisans Asylum's Bridgeport mill as local capability only; and issued an interactive route guide. No contact, upload, quotation, supplier selection, first article, fabrication, assembly or energization authority exists. |
| R91 | Elbow actuator and moving-mass architecture hold | Held the P0.7 custom-metal route because only 57.242 g remains before mandatory missing moving items; acquired and hash-controlled five official X430/FR12 source files; quantified nonselecting X430 mass/current/torque/speed sensitivities; and required an exact-coordinate P0.8 comparison with twelve open holds. P0.7 remains controlled, XM430 is not selected, and no quote, procurement, fabrication, motion, connection or energization authority exists. |
| R92 | Exact-coordinate X430 elbow P0.8 comparison | Registered the X430/FR12 assembly datums, corrected the S102 local-origin interpretation, generated integrated STEP/GLB and two separately identified adapter candidates, modeled a nominal 118-degree stop, sampled 221 rigid-body poses, and recalculated an incomplete 577.091 g subtotal and 1.104 N m elbow screen. Nine holds remain open and three partial; P0.7 remains controlled, XM430 is not selected, and every authorization flag is false. |
| R93 | Full-arm X430 P0.9 integration and continuous-clearance correction | Joined the corrected P0.8 elbow to the P0.7 column/J1/upper-link/forearm/H104 assembly; sampled 9,464 full-arm poses; continuously certified 69 nominal solid-pair groups through the 115-degree software limit with a 0.862928 mm conservative minimum; and added four fastener-stack plus five tolerance-control closure records. Eight holds remain open and four partial; P0.7 remains controlled, XM430 is not selected, and every authorization flag is false. |
| R94 | X430 P1.0 stop-sequencing clearance correction | Recontoured only the moving-striker upper edge while preserving the stop surface and hole axes; retained 60 SHA-bound identical-solid certificates; recomputed all nine changed-part pair groups at a 3.0 mm requirement with a 3.242248 mm conservative minimum; preserved nominal 118-degree contact; raised stop-contact X430 clearance to 2.491516 mm; and exposed a still-unallocated <=1.491516 mm adverse-variation limit. Eight holds remain open and four partial; P0.7 remains controlled, P0.9/P1.0 are unselected, and every authorization flag is false. |
| R95 | X430 P1.1 lowered-forearm and tolerance-allocation correction | Shifted the member-side forearm subassembly 7 mm downward while preserving the J2 axis, FR12 pattern and nominal 118-degree external stop datum; retained 30 SHA-bound unchanged-solid certificates and recomputed all 39 changed-solid pairs; certified 4.798163 mm for X430/striker through the command domain; raised stop-contact clearance to 4.369402 mm; restored 4.300 mm nominal M5 countersink edge lands; and allocated six unverified adverse-variation limits totaling 2.500 mm while preserving a 1.500 mm residual plus 0.369402 mm nominal arithmetic margin. Eight holds remain open and four partial; P0.7 remains controlled, P1.1/X430 are unselected, and every authorization flag is false. |
| R96 | X430 P1.1 moving-load, gravity and stop-sensitivity correction | Issued `HR-V0-ARM-LOAD-P1.1-X430-CANDIDATE`; separated exact CAD, catalog-envelope estimates, program allocations and unresolved physical inputs; calculated a 143.485169 g known subset and 453.485169 g incomplete reference allocation; swept gravity over J2 15..115 degrees; and published inertia, kinetic-energy, static-contact and average-energy/stroke sensitivities. The reference model is explicitly not an upper bound or actuator/stop rating. Ten inputs and every release flag remain open/false. |
| R97 | FR12-H101/idler received-mass metrology correction | Issued `HR-V0-FR12-MASS-MET-P0.1`; rejected the official 0.10 lb containing-kit and 0.20 lb included-idler commerce fields for mass credit; SHA-bound the frame-only 2,854.117032 mm³ STEP and 30.463092 mm bounding radius; and defined a twelve-operation unpowered mass/COM/envelope/inertia-bound route with two holds, three blank result rows and thirty blank repeats. Nothing is purchased, received or measured; `LOAD-OPEN-01` and every release flag remain open/false. |
| R98 | X430 continuous/cyclic duty evidence-route correction | Issued `HR-V0-X430-DUTY-P0.1`; verified the current ROBOTIS stall-versus-continuous warning and relevant control-table units; defined seven non-authorizing current sensitivities, fifteen channels, twelve fixture controls, twelve stages, ten acceptance equations, twelve open holds and a blank traveler. All seven powered stages are blocked, all limits are `SELECTION REQUIRED`, no run is executed and `LOAD-OPEN-08` remains open. |
| R99 | X430 reaction-torque duty-fixture topology correction | Issued `HR-V0-X430-FIXTURE-P0.1`; registered exact X430/FR12 source geometry; retained a stationary FUTEK TFF400 `FSH04015` reaction-torque topology only as a preferred evaluation candidate; generated STEP/GLB, a readable dimensioned SVG, a responsive 3D guide, four topology dispositions, five non-authorizing screens, twelve open interfaces, six instrument candidates and fourteen open holds. The model intentionally omits fabrication holes/tolerances, final adapters, anchors, catch, full guard, load device, calibrated acquisition and structural proof. `DUTY-HOLD-08` remains open and every fabrication, powered-test, motion, connection and energization flag remains false. |
| R100 | X430 duty-fixture adapter-interface correction | Rejected the R99 bridge because it reused the factory S102 side-ear attachment; issued `HR-V0-X430-FIXTURE-IF-P0.2` with separate fixed and active CNC adapter review candidates, exact S102 center-face registration, nominal B-Rep collision checks, a 1.900 mm unallocated fastener gap, candidate fastener/tolerance stacks, eight unsent RFI rows and fourteen open holds. No FUTEK CAD/application acceptance, qualified analysis, first article, support, guard/catch, powered test or energization authority exists. |
| R101 | X430 fixture-support and anchor-boundary correction | Replaced the generic fixture base/upright with a preferred but nonselected 80/20 `40200-SP-K` 300 mm static-pedestal inquiry route and review-only `FX101-C01` modification of `40006-BP`; rotated the controlled stack vertical, rejected mobile/weighted rating transfer and prohibited clamp-only support. The package deliberately omits pedestal-body and anchor CAD, requires site/facilities and manufacturer closure, preserves a later horizontal configured-joint test, and keeps eight RFIs unsent, ten holds open and every release flag false. |
| R102 | X430 horizontal load-device and common-bed correction | Issued `HR-V0-X430-LOAD-RIG-P0.1` with a preferred but nonselected PT-600 / standard HB-450M-2 / Ruland jaw-coupling inquiry route, exact Magtrol and ROBOTIS review geometry, six bounded catalog screens and a dedicated-brake-source boundary. Buildable output-adapter, brake-riser, base attachment, anchors and guard geometry are intentionally absent; eight RFIs remain unsent, fourteen holds remain open, the configured H101 test remains required and every release flag is false. |
| R103 | X430 HN12/output-interface correction | Issued `HR-V0-X430-OUTPUT-IF-P0.1`; controlled the official HN12 STEP and reference drawing; replaced R102's anonymous adapter with dimensioned but unreleased `FX103-C01` review geometry; changed the coupling inquiry to two clamp hubs; and added feature, tolerance, collision, arithmetic, RFI and unexecuted-inspection records. Material, GD&T, fasteners, manufacturer acceptance, DFM, FAI, proof and every inherited load-rig hold remain open; every release flag is false. |
| R104 | X430 brake-support and PT-profile correction | Corrected R102's PT-series interpretation from 14.5 mm to the official 20 mm plate thickness; controlled the current PT and HB/MHB PDFs; identified Magtrol `4866` as the HB/MHB-450M pillow-block inquiry route; exposed its 104 mm spacing against a 100 mm PT pitch span; and issued drawing-derived profile/support geometry plus unreleased `FX104-C01`. Accessory CAD, hardware, allowables, adapter material/GD&T/analysis/FAI/proof, alignment and every powered-work hold remain open; every release flag is false. |
| R105 | FX104-C01 adapter part-definition correction | Issued a controlled 6061-T651 material candidate, exact nominal STEP, dimensioned SVG, datums/GD&T/process requirements, ten-feature register, twelve adapter-only calculation screens, nine unexecuted FAI/proof records and five unsent DFM/reviewer RFIs. Manufacturer evidence, hardware, qualified review, DFM, FAI, proof, alignment and the guarded rig remain open; every release flag is false. |
| R106 | FX103 output-adapter geometry and part-definition correction | Proved the R103 Ø15 one-piece stub overlapped the PCD-16 horn-hole and screw-access envelope, rejected it, and issued separate H1150 C01 horn-flange and C02 shaft-flange candidates with exact STEP/drawing, fifteen features, fifteen screens, fourteen unexecuted inspections and seven unsent RFIs. Exact fasteners, manufacturer acceptance, DFM, qualified analysis, FAI, proof, alignment and the guarded rig remain open; every release flag is false. |
| R107 | FX103 output-adapter fastener-stack correction | Proved P0.2's 5.80 mm flange grip made the supplied M2x3 stop 2.80 mm before the HN12 face; issued C01 P0.3 with 3.00 mm counterbores and held SCB2-8/CB4-15 candidates, nineteen screens, six unexecuted assembly steps and seventeen unexecuted inspections. Torque, locking, manufacturer acceptance, DFM, proof and all work authority remain open. |
| R108 | Gripper orderable-subassembly correction | Verified current ROBOTIS FR12-G101GM and HN12-I101 scope, rejected the frame set as a sole complete-mechanism source, retained RM-X52 only as a proposed parent kit, and preserved all manufacturing-CAD, datum, mass, guard, force and physical-evidence holds. |
| R109 | Official gripper-frame source correction | Controlled six ROBOTIS DWG/PDF/STEP payloads for FR12-E170/E171, verified the reference-only drawings and solid STEP geometry, corrected the R108 source gap, and left complete-mechanism, H104, material, tolerance, physical-evidence and authorization holds open. |
| R110 | Current gripper source-route correction | Verified official ROBOTIS endpoint 767 and froze exact public Onshape document/workspace/assembly/blob identities; recorded that anonymous export was not exposed and no CAD payload was acquired; prepared an UNSENT publisher request; and left complete-mechanism, H104, manufacturing, physical-evidence and authorization holds open. |
| R111 | Source-controlled alternate-gripper trade study | Controlled seven Pololu/ServoCity manufacturer payloads and parsed 46 STEP solids; historically identified 30 g Pololu item 3551 as preferred evaluation only, a conclusion superseded by R113; defined twelve mechanical/evidence holds and six held electrical/control interfaces; left every physical gate and energization prohibition unchanged. |
| R112 | Direct gripper adapter and native ordinary-control interface | Added an exact-source 25.289709 g 6061 clevis candidate, 12 open mechanical holds, five controlled Maestro/regulator payloads, a native KiCad logical candidate at ERC 0/0 and responsive 3D/power/reset guides; selected no hardware, closed no requirement or gate and retained zero functional-safety credit. |
| R113 | Gripper requirement and selection correction | Found that R111 omitted the 40 mm minimum object dimension; retained the 40-70 mm baseline, marked Pololu 3551 incompatible by at least 8 mm, left ServoCity unverified and ROBOTIS conditionally compatible, selected nothing and separated the smaller-object idea into an unapproved change proposal. |
| R114 | Controlled-object and handoff evidence correction | Synchronized `SYS-002`, `INSPECT-OBJ-001` and `TEST-HAND-001`; added blank 12-row object, 100-cycle handoff and eight-row summary evidence forms plus a responsive arithmetic-only guide; selected and executed nothing and closed no physical or energization gate. |
| R115 | FR12-H104K source-provenance correction | Bound current official ROBOTIS endpoints 646/647/648 to the DWG/PDF/STEP hashes, added the DWG, proved PDF/STEP byte identity and left the H104-to-carrier transform, complete mechanism and every physical/release hold open. |
| R116 | PNOZ source/path conformance and narrative correction | Hash-controlled Pilz manual 21396-EN-23, mapped fourteen exact V3-P1.13 terminal/net checks, removed stale watchdog-in-input-loop claims, recorded anonymous gripper routes exhausted and retained every physical, application, safety-allocation and energization hold. |
| R117 | K1/K2 contactor application closure packet | Controlled current Schneider source identities, 33 application inputs, 18 pre-query holds, twelve unexecuted stages and an exact UNSENT manufacturer request while retaining partial EG-013 and every physical/application hold. |
| R118 | Grounding, bonding, and shield closure packet | Distinguished the source-internal actuator-return/PE relationship from equipment protective bonding and EMC shield decisions; controlled eight sources, fifteen nodes, twelve holds and eighteen unexecuted surveys while retaining partial EG-016 and every physical/site/qualified-review hold. |
| R119 | Exact compute and compute-power identity correction | Mapped Raspberry Pi's current configurators to PI1 `SC1112` and PSU3 `SC1158`; advanced Electrical V3 to P1.14 and BOM-001/BOM-002 to exact-candidate holds while retaining all receiving, cooling, storage/image, harness, retention, site, PD/load/brownout/thermal, grounding, runtime, physical and review holds. |
| R120 | Compute cooling, storage and OS-image evidence correction | Added held Active Cooler `SC1148`, retained the 64 GB unprogrammed official SD-card branch with exact order code `SELECTION REQUIRED`, pinned the official 2026-06-18 Raspberry Pi OS Lite image/hash without claiming download or deployment, and retained all enclosure, mounting, cable, installed-load, thermal, recovery, EMC/HIL and review holds. |
| R121 | Compute physical-installation and enclosure-fit correction | Confirmed P0.5 could not honestly absorb the compute installation; issued `HR-V0-CP-P0.6` / `HR-V0-COMPUTE-INSTALL-P0.1` with exact held `PJ302410RT`, `18P2721`, `PI5-CASE-D`, `GTM500C2` and `GT.50X80C2` candidates; allocated a separated compute column and added lower reserve; retained `BOM-070`, every hole/fastener, fit, pull/vibration, depth, thermal, grounding/EMC and review hold. |
| R122 | Pi-to-U2D2 physical-link selection correction | Advanced `BOM-070` from selection-required to an exact held StarTech.com `USB2AC50CM` candidate using current official StarTech, ROBOTIS and Raspberry Pi records; synchronized P0.6 as 34 panel-BOM rows; issued receiving and E1 test templates plus an interactive guide; retained received revision/fit, bend/retention, local 35 C limit, enumeration, waveform/error, common-mode, no-backfeed, EMC, HIL, qualified-review and all authorization holds. |
| R123 | Panel rail/duct stock and cut-feasibility correction | Found that one 500 mm perforated rail could not cover four segments totaling 642.6 mm and that the 65/100 mm segments conflicted with its published minimum; replaced it with two exact held `1207648` unperforated rails, retained exact `3240189` duct, allocated six `3022218` brackets only to DR1-DR3, issued a seven-segment stock plan and evidence forms, and left `BOM-059`, DR4 end retention, every final cut/hole/fastener/bonding/physical-proof input and all authorization gates open. |
| R124 | Stopping-budget and active J2-limit correction | Found and corrected the stale `15-125°` J2 position row in the active control narrative to the current fail-closed `15-115°` binding. Issued `HR-V0-STOP-BUDGET-P0.1`: twelve calculation/hold rows, sixteen blank test cases and an interactive screen. Proved that the 300 ms ordinary heartbeat detection alone consumes 3° at 10°/s and 9° at 30°/s before downstream delay, so `DF-01` retains zero stopping-distance and safety credit. `EG-026`, all physical timing, all missing stop directions and every motion/energization gate remain open. |
| R125 | Passive power-loss containment strategy and energy bound | Issued `HR-V0-POWERLOSS-P0.1`; selected fixed guard plus passive arm receiver and object catch with zero actuator/software/watchdog credit. The controlled 0.750 kg / 0.360 m allocation yields a 5.295591 J gravitational-only bound. Twelve calculation/hold rows, ten strategy rows, seventy-two blank cases and a responsive guide are controlled. The value is not an impact rating; `EG-009` remains partial and no physical or work-authorization gate closes. |
| R126 | Continuous collapse-envelope and floor-tray role correction | Issued `HR-V0-COLLAPSE-ENV-P0.1`; continuously bounded eleven known moving B-Reps at 338.740914 mm under arbitrary no-stop-credit J1/J2 rotations. The 360 mm controlled input fits the 450 mm reservation with 90 mm unallocated. Found the P0.3 tray top 114 mm below the arm envelope and corrected it to object-catch-only with zero arm-support credit. Complete gripper/cables/stops/receiver/physical proof remain open; `EG-008` and `EG-009` remain partial. |
| R127 | Raised passive arm-receiver geometry and sizing candidate | Issued `HR-V0-PASSIVE-ARM-RECEIVER-P0.1`; continuously bounded the known commanded B-Reps above Z 383.106478 mm and placed a guided receiver top at Z 320 mm with 63.106478 mm nominal residual. Three exact ACE MA30M evaluation candidates arithmetically total 10.507589 J, but application approval, guides, contact layer, peak force, load path, stops and all 28 physical records remain open; `EG-008` and `EG-009` remain partial. |
| R128 | Passive arm-receiver independent-method verification | Issued `HR-V0-PASSIVE-ARM-RECEIVER-VERIFY-P0.1`; closed-form trigonometric minimization reproduces the 384.142619 mm known-AABB boundary minimum, serialized-STEP inspection confirms 110 mm X and 20 mm Y nominal guard margins, and Decimal arithmetic reproduces the ACE/rail screen. R127's conservative 63.106478 mm clearance is retained; all twelve hold groups, 28 physical records and `EG-008/009` remain open/partial. |
| R129 | Detailed passive receiver hardware-candidate and blank-drawing correction | Issued `HR-V0-PASSIVE-ARM-RECEIVER-DETAIL-P0.2`; advances exact held igus guide, Sorbothane contact-layer, 80/20 joint-hardware and ACE evaluation identities; adds 16 BOM rows, seven interfaces, twelve holds, hole-free STEP/DXF blanks and a responsive 3D guide. The nominal catch gap is 9.625 mm and the residual after catalog stroke is 1.497 mm, but the tolerance stack is open. No configured rail code, received CAD, hole, retention, application approval, structural allowable, anchor, proof or authorization is released. |
| R130 | Receiver guide-interface geometry correction | Issued `HR-V0-RECEIVER-GUIDE-IF-P0.1`; proves the R129 20 x 50 mm tab cannot cover the official 53 x 40 mm TWA-01-20 K2 pattern, rejects it, and advances a 73 x 80 mm hole-free right-angle face envelope. Twelve catalog-coordinate rows, 24 controlled centers, ten holds, a supplier RFI draft and responsive 3D guide are synchronized. Received CAD, configured rail code, diameters, fasteners, application approval, structural proof, machining and authorization remain open. |
| R131 | Watchdog PCB current-source and mounting-interface reconciliation | Issued `HR-V0-WD-MOUNT-IF-P0.1`; reproduces the ISO1 land defect in immutable PCB-P0.5, verifies current PCB-P0.6 already encodes the corrected 8.010 mm / 11.050 mm option-7 geometry and native DRC 0/0/0, and controls four mounting centers plus three exact unselected Harwin standoff variants. Twelve holds retain every screw, washer, height, drilling, torque, insulation/process, physical-proof and authorization requirement. |
| R132 | Watchdog PCBA capability/DFM inquiry and Harwin land-shape correction | Issued `PCB-P0.7 / HR-V0-WD-PCBA-RFI-P0.1`; changes only TP1-TP16 to Harwin's exact rectangular 3.45 x 1.85 mm copper, preserves native DRC 0/0/0, and controls 46 references, four provider routes, twenty requirements, twenty-four unsent questions, fourteen holds and twenty-four blank first-article rows. No provider, CAM, process, fabrication, assembly, physical result or energization is released. |
| R133 | Watchdog PCBA assembly-data definition | Issued `HR-V0-WD-PCBA-DATA-P0.1`; reconciles 42 populated references into sixteen exact-MPN BOM lines, controls 38 SMD / four THT placements plus four NPTH features, derives the 160 x 100 mm board-relative coordinate convention, and adds explicit orientation notes and an interactive map. Supplier-normalized XYRS, CAM, process acceptance, fabrication, assembly, physical evidence and energization remain unreleased. |
| R134 | Mechanical DFM and first-article review-data correction | Issued `HR-V0-MECH-DFM-DATA-P0.1`; corrected the stale statement that the X430 comparison had not been produced, retained P1.1/X430 as nonselected and P0.7 as controlled, and bound five parts to fifteen exact geometry identities, twenty-six source controls, thirty unexecuted FAI operations, twelve unsent DFM questions and fifteen open holds. No provider contact, upload, quote, purchase, first article, fabrication, assembly, motion or energization is authorized. |
| R135 | Mechanical STEP/DXF/drawing parity audit | Issued `HR-V0-MECH-PARITY-P0.1`; independently parsed all five DXFs and STEP solids, matched five profile extents, thirty exact nominal holes and eight countersink positions at the controlled upper-limit model diameter, traced all twenty-six drawing controls and published interactive feature maps. Four findings remain open; no file alone is a machining authority and no provider, fabrication, assembly, motion or energization action is authorized. |
| R136 | Countersink model-definition correction candidate | Preserved P0.7 and issued `HR-V0-CSK-MBD-P0.1` plus four nonselected P0.8 candidate STEP parts. Eight countersinks now represent the controlled Ø11.30 nominal and exact 90° geometry at 2.90 mm depth; maximum Ø11.40 and 3.10 mm depth remain separate conservative screens. External envelopes are unchanged; five decisions and three findings remain open; no external action is authorized. |
| R137 | Conventional drawing and finished-profile definition candidate | Issued `HR-V0-MECH-DWG-P0.1`: five conventional SVG drawings, five STEP-derived finished-feature DXFs and five exact STEP bindings. C06/C07 each carry twelve LINE plus twelve ARC finished-profile entities; all 26 source controls are drawing-explicit; five ICF-01 CMM registrations and all 30 FAI rows remain candidate/unexecuted. P0.7 remains controlled and no external action is authorized. |
| R138 | Watchdog critical-IC native metadata correction | Issued `PCB-P0.8 / HR-V0-WD-IC-META-P0.1`; adds 36 hidden native fields across UDRV1/UDRV2/UFB1/ISO1. The P0.7/P0.8 structural digest is identical across placement, pads, nets, tracks, vias, outline and zones; DRC remains 0/0/0. Assembly process and all manufacturing/energization authority remain open/false. |
| R139 | Current watchdog native identity and assembly-data correction | Issued `PCB-P0.9 / HR-V0-WD-PCBA-DATA-P0.2 / HR-V0-E2-HW-P0.3`; all 42 populated references carry 294 exact hidden base fields, sixteen BOM lines total 42 parts, 42 placements and four NPTH features reconcile to historical P0.7, and P0.8/P0.9 structural parity passes. Supplier-normalized XYRS, process acceptance, CAM, fabrication, assembly, physical evidence and energization remain false/open. |
| R140 | HR-V0 frame/sign and raw-calibration boundary correction | Issued `HR-V0-FRAME-CONV-P0.1`; controls six frames, four proper transforms, three engineering axes, four legacy-layout mappings, a blank six-record calibration form and ten open holds. A0 is +X right / +Y front / +Z up; J1/J2 positive rotation is right-hand about +X; legacy G0 axes are layout-only. Raw direction/scale/zero, physical datum proof, gripper registration, HR-30 mirroring, motion and energization remain open. |
| R141 | Requirement/risk/gate governance-control correction | Issued `HR-V0-GOV-P0.1`; covers 151 source-bound records, identifies candidate owner/approver roles, catalogs 66 compound requirements and keeps nine governance holds open. No person, evidence, signature, approval, residual-risk decision, atomic child register or energization authority is invented. |
| R142 | Atomic-requirement and governance P0.2 correction | Issued `HR-V0-REQ-ATOMIC-P0.1` with 396 stable draft children covering all 66 compound parents and `HR-V0-GOV-P0.2` binding the child register. Eight atomic and nine governance holds remain open; zero named people, evidence, approvals or work authority are represented. |
| R143 | Second-method atomicity and acceptance-schema correction | Issued `HR-V0-REQ-ATOMIC-P0.2` with 458 draft children after separating 62 R142 multi-duty records, 458 blank acceptance rows and `HR-V0-GOV-P0.3`. Internal screening is not independent acceptance; zero people, evidence, approvals or work authority are represented. |
| R144 | Integrated unpowered build-traveler correction | Issued `HR-V0-BUILD-TRAVELER-P0.1`: 14 dependency-ordered phases, 85 concrete steps, 21 through-E2 gate mappings and 14 hold points. Zero steps are authorized or executed; BT-P13 prohibits connection and energization. |
| R145 | Complete Evaluation Batch A acquisition-decision and manifest-cycle correction | Issued `HR-V0-EVAL-BATCH-A-ACQ-P0.1`: all 17 controlled lines / 21 units grouped into four lots; current known manufacturer-price floor $1,864.73; eight quote-required lines; 15 current official product records. Removed the inherited unsatisfiable manifest/build-traveler hash cycle with an explicit machine-checked self-reference marker while retaining the independent manifest check. Zero lines/lots are authorized, ordered or received; no checkout, fabrication, connection, motion or energization is authorized. |
| R146 | Evaluation Batch A unit receiving, quarantine and historical-governance-snapshot correction | Issued `HR-V0-EVAL-BATCH-A-RCV-P0.1`: 21 deterministic unit IDs, twelve receiving steps per unit, seven evidence placeholders per unit and 21 printable quarantine labels. Corrected P0.1/P0.2 governance checkers to validate their recorded historical hashes while current P0.3 follows live sources. All 252 traveler records and 147 evidence records are unexecuted; zero units are authorized, ordered, received or accepted for machine use. |
| R147 | Actuator-source AC cord catalog-selection correction | Issued `HR-V0-ACT-AC-CORD-P0.1`; advanced BOM-063 to exact-candidate hold for Eaton `P006-006` against the MEAN WELL GST280A12-C6P C14/Class-I basis. Eighteen controls, twelve holds and thirty physical records retain the exact site, branch, code, PE, fit, inrush, route, thermal and qualified-review boundaries. No purchase, connection or energization authority exists. |
| R148 | P0.7 mechanical BOM binding correction | Issued `HR-V0-MECH-BOM-BIND-P0.1`; replaced the live P0.5 `BOM-027` mix with one each `MV0-C01/C04/C05/C06/C07`, bound all five to fifteen existing hashed STEP/DXF/SVG identities, and advanced the row to exact-candidate hold. All fifteen DFM holds remain open; no provider contact, upload, quote, purchase, fabrication, assembly, motion or energization authority exists. |
| R149 | Watchdog PCB BOM binding correction | Issued `HR-V0-WD-BOM-BIND-P0.1`; replaced historical PCB-P0.5 in live `BOM-048` with current PCB-P0.9 / Electrical V3-P1.14 and P0.2 assembly data, hash-binding 42 populated references, sixteen BOM lines, 42 placements and four NPTH features. CAM was absent at issuance; supplier XYRS, provider/process, physical and qualified evidence remain absent; no physical-work or energization authority exists. |
| R150 | Current PCB-P0.9 CAM review correction | Issued `HR-V0-WD-CAM-P0.1`; generated ten Gerber/job and five drill/map/report files, IPC-D-356, statistics and native DRC 0 from current PCB-P0.9; proved exact internal parity for all 42 placement references. No archive, supplier XYRS, provider/process acceptance, physical article, fabrication, assembly, connection, motion or energization authority exists. |
| R151 | DXL-STAR-P0.1 manufacturing-evidence correction | Issued `HR-V0-DXL-STAR-MFG-P0.1`; generated ten Gerber/job and five drill/map/report files, IPC-D-356, statistics and native DRC 0; proved exact encoded parity for seven connector placements and eighteen terminals and recorded four NPTH features. Advanced BOM-051 to exact-candidate hold. Eighteen release holds and eleven manufacturing selections remain open; no external work or energization authority exists. |
| R152 | DXL injection allocation/BOM correction | Issued `HR-V0-DXL-INJECT-BIND-P0.1`; proved that one Electrical V3 INJ1 and one DXL-STAR-P0.1/BOM-051 parent implement all three isolated VDD branches with exact parity across eighteen terminals. Integrated legacy BOM-035 with no separate purchase. Twelve residual holds and every external-work boundary remain open. |
| R153 | DXL harness allocation/BOM correction | Issued `HR-V0-DXL-HARNESS-ALLOC-P0.1`; allocated the three included 180 mm JST-JST actuator cables as integrated BOM-086, reduced loose EHR-3/SEH quantities to the one custom U2D2-to-JC1 data/return cable, and retained fourteen connector-current, harness, physical-evidence and work-authority holds. |
| R154 | DXL current-envelope and runtime-invariant correction | Issued `HR-V0-DXL-CURRENT-ENV-P0.1`; derived the 2.152 A raw-800 internal screen, rejected fuse-only connector protection, retained the present architecture for guarded qualification only, added per-sample Current Limit/Goal Current drift checks, and preserved fourteen open physical/qualified/work-authority gates. |
| R155 | Native DXL branch-protection and regeneration evaluation | Issued `HR-V0-DXL-PROT-EVAL-P0.1`; added five connected KiCad sheets at ERC 0/0 for three exact TPS259461LRPWR branch candidates and one Pololu 3771 pulse-shunt candidate, rejected true reverse blocking for the present regenerative path, and retained fourteen blank tests, eighteen open holds and an unchanged robot baseline. |
| R156 | Native DXL protection-carrier correction | Issued `HR-V0-DXL-PROT-CARRIER-P0.1`; added five legible native KiCad sheets, a routed four-layer single-channel carrier, exact source-backed part candidates, 20 placements, three controlled variants, review CAM, ten blank tests and sixteen open holds at ERC/DRC 0/0; rejected the initial crowded export and retained zero robot-baseline, fabrication or energization authority. |
| R157 | Branch-fault and no-backfeed validation definition | Issued `HR-V0-BRANCH-FAULT-P0.1`; bound 24 blank cases to the exact V3 refs/nets across unpowered, limited-energy, guarded-fault and configured-distribution stages; supplied the missing EG-024 evidence location and an interactive guide while keeping the gate open and every physical result/authorization absent. |
| R158 | RPW0010A footprint defect correction | Found eight material P0.1 transcription failures against TI drawing `4225183/A`; prohibited P0.1 for supplier use and issued a separate P0.2 candidate with exact 14-copper/16-paste primitive parity and KiCad ERC/DRC 0/0. Independent footprint, assembler/stencil DFM, first-article and every physical/work-authority hold remain open. |
| R159 | Carrier native-rule and PCBA DFM inquiry correction | Issued P0.3 with a 0.100 mm mask/clearance floor and three global fiducials; added 24 provider capability rows, 24 unsent DFM questions, 23 hash-bound proposed files and 18 blank first-article checks. No provider action, external work, physical evidence or energization authority exists. |
| R160 | P0.3 carrier harness interface-control correction | Froze exact `VHR-2N` / `SVH-21T-P1.1` and Belden 9918 red/black candidates; bound two harness identities across eight pin/interface rows; added four held cut/crimp rows, ten unexecuted process steps, eighteen blank acceptance rows and nine unresolved selections. No harness, physical result or work authority exists. |
| R161 | Carrier-integrated ECAD and panel-route correction | Issued `V3-P1.15-CARRIER-CANDIDATE`, `DXL-STAR-P0.2-CARRIER-CANDIDATE` and `HR-V0-DXL-CARRIER-INTEGRATION-P0.1`; separated all three fused-prelimit and limited-postcarrier rails, preserved star-board copper geometry under the explicit net map, and added three nominal placement/twelve-hole/six held-route screens. Twelve selections and 24 acceptance rows remain open; no drilling, harness, physical result or work authority exists. |
| R162 | DXL carrier mounting-interface and no-drill fit correction | Issued `HR-V0-DXL-CARRIER-MOUNT-IF-P0.1`; corrected the R161 zero-left-margin placement, proposed exact 10 mm M3 insulating standoffs and M3 x 6 mm nylon screws, derived twelve center-only coordinates and added a ten-row received-fit procedure. Hole/process, tolerance, torque, creep/load, connector/cover/rear clearance, route recomputation, fourteen selections and twelve acceptance rows remain open; no procurement, drilling, assembly or work authority exists. |
| R163 | Current-configuration reconciliation | Issued `HR-V0-CONFIG-REC-P0.1`; reconciled the carrier-aware P1.15 system, P0.2 DXL star, P0.3 protection carriers, harness, mounting and 91-group BOM while quarantining P1.14/P0.1 CAM as historical. Thirty energization gates remain unresolved; no fabrication, assembly, motion or energization authority exists. |
| R164 | Current P0.2 DXL-star manufacturing-review evidence | Issued `HR-V0-DXL-STAR-MFG-P0.2` directly from `DXL-STAR-P0.2-CARRIER-CANDIDATE`; recorded native DRC 0, ten Gerber/job outputs, five drill/map/report outputs, seven placement references, eighteen terminal-parity rows and eighteen explicit holds. This closes only the absence of current internal CAM evidence; provider/process/XYRS/DFM/FAI/current/harness/physical validation and all work authority remain open. |
| R165 | P1.15 watchdog/E2 parity and current control-only slice | Issued `HR-V0-E2-P115-PARITY-P0.1` and `HR-V0-E2-HW-P0.4`; proved 69 unchanged references and 263 terminals, including 28 explicit E2 references, at exact P1.14/P1.15 schedule and native-net parity. The only declared system changes are seven actuator references plus three limiter carriers. P0.4 remains fail-closed with the complete actuator subset absent or unwired, twelve holds open and no test or work authorization. |
| R166 | P1.15-bound watchdog CAM review | Issued `HR-V0-WD-CAM-P0.2`; regenerated the PCB-P0.9 CAM set with KiCad 10.0.5 and hash-bound it to the complete P1.15 source manifest plus R165 parity evidence. Native DRC remains zero and all 42 placements retain exact internal parity. P0.1 is historical; supplier-normalized XYRS, provider/process acceptance, DFM, first article, physical evidence and all work authority remain open. |
| R167 | Boston/US custom-metal capability refresh | Issued `HR-V0-BOSTON-FAB-ROUTE-P0.3`; screened ten routes against ten current official records, identified Kontrast4D as the strongest published local candidate and Protolabs/Xometry as the strongest online review routes, preserved exact 6061-T651, and exposed ten open design/application inputs. No provider is qualified or contacted; no upload, quote, first article, fabrication, assembly, motion or energization authority exists. |
| R168 | XT1 control-terminal group reconciliation | Issued `HR-V0-XT1-P0.1`; reconciled BOM-039 to five gray 3209510 bodies, one blue 3209523 body, one 3030417 end cover, six exact position/net mappings and zero jumpers. Kept shared 3022218 restraint under BOM-085 and labels under BOM-062. Twelve holds and all work-authority boundaries remain open; EG-003/015 remain partial. |
| R169 | Panel identification and XT1 marker correction | Issued `HR-V0-LABEL-P0.1`; replaced overlong XT1 marker prose with `01` through `06`, added separate group/device/operator/status schedules, and advanced BOM-062 to an exact-candidate material/text hold. Printing, artwork, adhesion, placement, wire markers, code marking and physical/qualified evidence remain open; EG-003/015 remain partial. |
| R170 | Exact compute-storage candidate | Issued `HR-V0-COMPUTE-STORAGE-P0.2`; superseded only the order-code-open STORE1 branch with exact Kingston `SDCIT2/64GBSP` on hold. Recorded pSLC-mode TLC, 30K P/E and power-failure/ECC/wear/monitoring family claims without assigning the family maximum TBW to 64 GB. Pi 5 compatibility, receiving, media integrity, imaging, filesystem, abrupt-loss, recovery, retention, thermal/current and qualified evidence remain open. |
| R171 | Fail-closed host deployment candidate | Issued `HR-V0-HOST-DEPLOY-P0.1`; added a six-file disabled overlay, pure-file preflight, exit-78 launcher, 23 current preflight holds, eighteen open closure groups, 21 blank execution rows and six source tests. No target image, hardware backend, installation, HIL, safety credit, gate closure or work authority exists. |
| R172 | Raspberry Pi OS publisher-SBOM lock | Issued `HR-V0-RPI-OS-SBOM-P0.1`; controlled the official 5,336,108-byte SPDX payload and local hash, normalized 4,743 package records into 632 unique DPKG identities, and recorded fifteen critical rows plus twelve blank target checks. No disk image, media write/readback, target inventory, backend, HIL, safety credit, gate closure or work authority exists. |
| R173 | Fabrication-input requirements reconciliation | Issued `HR-V0-FAB-INPUT-P0.1`; bound the existing draft 100 g / 40-70 mm object and 0.15 m/s TCP / 30 deg/s automatic-joint / 10 deg/s setup limits to ten fabrication inputs and reproduced five energy/kinematic screens. One false wholly-unknown label is corrected; seven dynamic, physical or work-authority inputs remain partial/open/unauthorized and EG-006/007 remain partial. |
| R174 | Dynamic trace analysis and reset-rejection path | Issued `HR-V0-DYN-TRACE-P0.1`; added nine deterministic rules, four common-clock event channels, four synthetic fixtures and four blank qualified dispositions. Nominal computation remains on HOLD; reset-motion, early-start and data-integrity faults are rejected. EG-026 advances to partial, with every physical input/result and work authority still open. |
| R175 | Dynamic instrumentation backbone candidate | Issued `HR-V0-DYN-INST-P0.1`; named four exact evaluation candidates, mapped all fifteen channels, imposed eight no-connect/interface boundaries and retained fifteen open holds. Rejected a ground-referenced divider as a completed isolated 24 V event interface. EG-025 remains open and EG-026 partial; no procurement, connection, physical evidence, safety credit or work authority exists. |
| R176 | Isolated dynamic-event interface candidate | Issued `HR-V0-DYN-EVENT-IF-P0.1`; named two exact TI `ISO1212EVM` evaluation units, mapped seven field events plus FIO0 trigger witness into one T7 `FIO_STATE` word and created four legible connected KiCad child sheets at ERC 0/0. Every field tap remains prohibited pending noninterference, timing, physical and qualified evidence; EG-025 remains open and EG-026 partial. |
| R177 | Low-loading isolated event-acquisition candidate | Issued `HR-V0-DYN-EVENT-AIN-P0.1`; retained R176 as historical/not preferred, named seven exact TI `AMC3330EVM` units, mapped their outputs to all seven T7 differential pairs and issued five readable native KiCad child sheets at ERC 0/0. Every field adapter remains `SELECTION REQUIRED`; direct 24 V-class connection is prohibited; EG-025 remains open and EG-026 partial. |
| R178 | Event-tap noninterference disposition | Issued `HR-V0-EVENT-TAP-DISP-P0.1`; traced all seven proposed taps to exact P1.15 terminals, verified current Pilz/Schneider/TI application limits, corrected the LC1D25BD built-in suppressor record and rejected catalog-only field-adapter selection. Three native disposition sheets parse at ERC 0/0; zero taps or divider designs are released and EG-025/026 remain open/partial. |
| R179 | Non-contact event-observation correction | Issued `HR-V0-NONCONTACT-EVENT-OBS-P0.1`; rejected the permanent passive-divider/AMC3330 route for the current baseline and mapped an exact Tektronix `TCP0030A` evaluation candidate to seven logical P1.15 conductors. Zero electrical taps and zero physical tests exist; twelve holds retain as-built identity, jaw fit, host, simultaneity, calibration, thresholds, source/motion witnesses, noninterference, uncertainty and qualified review. EG-025/026 remain open/partial. |
| R180 | Event-observation independence correction | Issued `HR-V0-EVENT-OBS-CORR-P0.1`; corrected the false independence assigned to two points in one series EDM chain, allocated one common-chain witness plus individual K1/K2 diagnostic auxiliaries, and named an eight-input Tektronix evaluation population. No diagnostic load, connection or physical result exists; EG-025/026 remain open/partial. |
| R181 | Corrected two-run E2 trace analysis | Issued `HR-V0-DYN-TRACE-P0.2`; replaced the P0.1 combined trace with separate eight-channel E2 STOP and RESET/ARM contracts, corrected common-EDM transition direction, required a valid control source and no motion, retained both auxiliaries as zero-credit diagnostics, and added six synthetic pass/reject fixtures. It makes no powered-motion stopping claim; EG-025/026 remain open/partial. |
| R182 | E2 acquisition compatibility and motion-witness candidate | Issued `HR-V0-E2-ACQ-COMPAT-P0.1`; balanced four `TCP0030A` plus four `TIVP02` probes at 35.8 W in each 40 W MSO58B bank and 71.6 W against the 80 W total limit, and named exact Banner `Q4XFULAF110-Q8` / part 97540 for guarded disconnected-load no-motion evidence. Fifteen holds, zero physical runs, zero released connections and zero safety credit remain; EG-025/026 stay open/partial. |
| R183 | Q4X witness physical-interface candidate | Issued `HR-V0-Q4X-IF-P0.1`; named exact Banner `BC-M12F5-22-2-SF` cordset and `SMBQ4XFA` bracket plus Keithley `2220-30-1` isolated-channel candidates, defined eight unreleased pin rows and six held domain boundaries, and added receiving/calibration scaffolds. Protection, current limit, terminals, enclosure, shield, support, target, configuration, threshold, every physical result and qualified review remain open. Zero baseline changes, released connections, safety credit or work authority exist; EG-025/026 stay open/partial. |
| R184 | Q4X temporary interface-box candidate | Issued `HR-V0-Q4X-BOX-P0.1`; added exact Phoenix 0.1 A electronic protection and terminal/ferrule/tool candidates, Hammond fiberglass enclosure/panel, LAPP glands/lock nuts and Alpha source-cable designation. Root plus two connected native KiCad sheets pass ERC 0/0. Drain park, separate analog ground and DNP remote contact are explicit. Fourteen holds, zero released physical work and zero safety credit remain; EG-025/026 stay open/partial. |
| R185 | Q4X box physical-layout correction | Issued `HR-V0-Q4X-BOX-LAYOUT-P0.1`; corrected `14F0907` to 174.498 x 222.250 x 3.175 mm, bound its four-hole pattern, centered the 150.000 mm rail and calculated the 60.800 mm catalog-width device envelope. Bore diameter, gland/rail coordinates, exact fasteners, torque, finished rating and all physical evidence remain held. Zero drill holes or work authority are released; EG-025/026 stay open/partial. |
| R186 | Q4X installation evidence and receiving route | Issued `HR-V0-Q4X-INSTALL-EVIDENCE-P0.1`; bound the LAPP M12 1.5 N m installation/cap-nut baseline, retained the VDE blank separate locknut-torque field and the unpublished through-bore, and defined ten exact receiving lines plus ten blank metrology steps. Eleven holds, zero received parts, zero released holes and zero procurement or physical-work authority remain; EG-025/026 stay open/partial. |
| R187 | Q4X unpowered acquisition decision | Issued `HR-V0-Q4X-UNPOWERED-ACQ-P0.1`; reconciled the ten R186 lines into a $211.30 fit lot and $22.83 PTCB lot, with a $234.13 dated subtotal before shipping/tax/fees. Live TME evidence separates seller multiplicity from LAPP's bag-of-100 packaging. Every cart, decision, order, received article, physical result and work authority remains zero; no Sol R12 blocker closes. |
| R188 | Q4X quote-readiness amendment | Issued `HR-V0-Q4X-QUOTE-READINESS-P0.1`; replaced the `14F0907` associated-product observation with exact direct code `14F0907-ND` at $29.80 and replaced unknown `1464484` availability with direct code `277-1464484-ND`, $22.83 and zero stock. Corrected the fit/combined snapshots to $211.63/$234.46. No cart, quote, purchase, order, physical result or work authority exists; no Sol R12 blocker closes. |
| R189 | Clean-clone reproducibility correction | Issued `HR-V0-CLEAN-CLONE-AUDIT-P0.1`; preserved failed 112/145, 99/145 and 144/145 attempts, added an exact generated checkout-EOL contract, removed six originating-machine absolute paths, and recorded a clean 145/145 pass for exact commit `221035e...` under `core.autocrlf=true`. `EG-002` remains partial; no physical or Sol R12 blocker closes. |
| R190 | Lightweight gripper feasibility branch | Issued `HR-V0-GRIP-XC330-P0.1`; archived exact official XC330 source geometry, generated nine native custom part pairs and three mechanism poses, and calculated a nominal 38-74 mm padded range with a 673.774625 g incomplete moving subtotal and 76.225375 g shared incomplete headroom. Fifteen holds remain; the active XM430 baseline is unchanged and no requirement, gate, Sol R12 blocker or work authority closes. |
| R191 | Source-bound XC330 gripper interface correction | Issued `HR-V0-GRIP-XC330-P0.2`; archived official XC330/FPX330 drawings and frame source, registered two exact frames to the actuator, replaced trapezoidal teeth with a module 0.8 / 20-tooth / 20-degree involute candidate, generated seven native custom part pairs plus three poses, and browser-validated the interactive guide. The incomplete subtotal is 679.124713 g with 70.875287 g headroom. Sixteen holds remain; the active XM430 baseline is unchanged and no requirement, gate, Sol R12 blocker or work authority closes. |
| R192 | Source-bound XC330 wrist integration | Issued `HR-V0-XC330-WRIST-P0.1`; composed the exact H104, XC330 and FPX330 sources into one world-coordinate chain; generated two native bridge pairs and two interactive reference assemblies; registered twelve candidate hole axes and seven intentional nominal contacts; and checked 399 endpoint-aligned 5-degree joint samples with zero positive intersections. The incomplete subtotal is 688.961224 g with 61.038776 g headroom. Eighteen holds remain; `GRIP-002` and the active XM430 baseline are unchanged and no requirement, gate, Sol R12 blocker or work authority closes. |
| R193 | Gripper native-source correction | Issued `HR-V0-GRIP-CAD-ACQ-P0.2`; corrected the historical broken-link claim, bound the current public ROBOTIS Onshape gripper assembly plus five native part elements, and documented the mutable Main/no-export boundary. The XM430/OpenMANIPULATOR route remains proposed but unselected; XC330 remains an alternate and may not connect to the current rail because its 12.0 V maximum is below the GST280A12 catalog 12.6 V tolerance endpoint. Twelve holds remain and zero requirement, gate, Sol R12 blocker or work authority closes. |
| R194 | Boston site and jurisdiction basis | Issued `HR-V0-BOSTON-SITE-P0.2`; froze Boston, Massachusetts, USA and current official code/permit routes while leaving the exact premises, branch, bench, environment, emergency plan and E2 authority blank. BPL and Hatch receive only their published prototype capability; the R167 commercial CNC screen remains separate. Twenty premises inputs and eight holds remain open; EG-001 and EG-022 stay partial. |
| R195 | Watchdog PCB P1.15 native-identity correction | Issued `HR-V0-WD-P115-ID-P0.1` and PCB-P1.0; directly bound the unchanged watchdog geometry/topology/placement/native assembly fields to Electrical V3-P1.15 and regenerated current assembly/CAM/BOM/E2 evidence. R165 parity remains historical. All 18 CAM/manufacturing and 12 E2 holds remain open; EG-002/004 stay partial. |
| R196 | Stale-command and restart-authority correction | Issued `HR-V0-STALE-AUTH-P0.1`; bound all twenty E2 logic cases to supervisor state, active-target, torque-request and replay observations. Added a source regression proving dropout clears the target, valid RESET/ARM does not request torque, the old sequence is rejected and only a later fresh sequence may request torque. The entire E2 evidence form remains unexecuted; zero safety credit and no gate/work authority close. |
| R197 | Conservative kinematic speed-bound correction | Issued `HR-V0-KIN-P0.1`; bound the current J1/J2/H104 candidate geometry to a triangle-inequality TCP-rate model, exact configuration hashing and a same-file supervisor constructor. Tool reach and acceptance hashes remain `SELECTION REQUIRED`, so the repository validator refuses construction. No physical evidence, safety credit, gate or work authority closes. |
| R198 | Runtime execution-boundary correction | Issued `HR-V0-RUNTIME-P0.1`; added the exact entrypoint, nineteen-source overlay, received-position conversion, torque/goal-current parity and deterministic heartbeat/authority/sample/terminal/shutdown sequencing. The committed preflight still exits 78 with 24 holds; target backends, image, HIL and approvals remain absent. No gate or work authority closes. |
| R199 | Runtime backend and heartbeat correction | Issued `HR-V0-RUNTIME-BACKENDS-P0.1`; added hash-bound libgpiod and AF_UNIX source candidates, monotonic heartbeat edge generation, strict credential/schema parsing and unreleased trajectory resource bounds. The overlay has 21 rows and preflight exits 78 with 50 holds. No physical observation circuit, target/HIL evidence, safety credit, gate or work authority closes. |
| R200 | Runtime observation-semantics correction | Issued `HR-V0-RUNTIME-OBS-P0.1`; traced four positive panel statuses, separated five unselected health providers plus software-derived bus health, rejected NC-contact inversion and made unknown values fail closed. Preflight exits 78 with 45 holds; twelve interface holds remain open. No connected receiver, target/HIL evidence, safety credit, gate or work authority closes. |
| R201 | Four-channel runtime-observation receiver correction | Issued `HR-V0-RUNTIME-OBS-IF-P0.1`; added root plus four connected native KiCad sheets for two `ISO1212DBQ` devices, four Type-3 input networks, three 2.70 kohm wetting/bleed shunts, isolated field/compute returns and fail-low outputs. ERC is 0/0; 33 component blocks and 33 nets reconcile. SR1 H1 current/brightness, Pi GPIOs, PCB/layout, harness, EMC, fault injection and all ten evidence holds remain open. Zero safety credit and no work authority close. |
| R202 | Routed runtime-observation carrier correction | Issued `HR-V0-RUNTIME-OBS-CARRIER-P0.2`; replaced the compound 4+2 connector candidate with exact six-position Phoenix Contact item 1751280 and added a 120 x 90 mm four-layer PCB candidate. Root plus four sheets, 29 mounted parts, four holes, 143 tracks, 56 vias and three internal zones check at ERC/DRC 0 with pad/net parity. Fourteen physical-evidence holds remain; no CAM, fabrication, connection, safety or energization authority exists. |
| R203 | Raspberry Pi diagnostic-input allocation correction | Issued `HR-V0-RUNTIME-OBS-PINMAP-P0.1`; bound JLOGIC1 to Pi physical pins 17/20/15/16/18/22, allocated active-high GPIO22-25 to SR1/SRA1/K1/K2, preserved heartbeat GPIO17/pin 11 plus pin 6 return, and recorded JTAG/DPI conflicts. Host preflight remains fail-closed at exit 78 with 36 holds. Eight local physical/target/review holds remain; no mate, harness, installed gpiochip/readback, HIL, safety credit or work authority exists. |
| R204 | Raspberry Pi observation carrier and harness correction | Issued `HR-V0-PI-OBS-CARRIER-P0.1`; added exact held Samtec `ESQ-120-33-G-D` and Phoenix Contact `1751280` identities, a native 65 x 56.5 mm two-layer passive carrier with six routed nets and 34 deliberate no-copper header positions, plus six exact Belden 3051 color/order-code stock candidates. ERC/DRC are 0; ten received-fit/DFM/stack/case/harness/target/physical/review holds remain open. No CAM, procurement, fabrication, assembly, connection, powered-test, safety or energization authority exists. |
| R205 | Pi observation panel and harness integration correction | Issued `HR-V0-PI-OBS-INTEGRATION-P0.1`; detected that the R161 DXL candidates already consume the lower reserve, rotated R202 into a nominal 90 x 120 mm compute-column placement, transformed its two connectors and four holes, checked ten planar clearances and source-matched eleven field/compute conductors. The 335.4 mm compute and 276.0 mm field values are geometric screens only; every cut length remains `SELECTION REQUIRED`. Thirteen holds and sixteen unexecuted acceptance rows remain open. No procurement, fabrication, assembly, connection, powered-test, safety or energization authority exists. |
| R206 | Connected observation-system and exact field-harness candidate correction | Issued nonselected Electrical `V3-P1.16-OBSERVATION-CANDIDATE` and `HR-V0-OBSERVATION-FIELD-HARNESS-P0.1`. Corrected a generated root-hierarchy defect that initially omitted page 13 despite green ERC; final native ERC parses all fourteen pages at 0/0. Exact XT1/R202/R204/Pi mappings, five Belden 3051 wire/color candidates and Phoenix direct-strip envelopes are controlled. All cut lengths remain `SELECTION REQUIRED`; twelve holds and twelve acceptance rows remain open. No physical, safety or work authority closes. |
| R207 | Exact observation compute-harness candidate correction | Issued `HR-V0-OBSERVATION-COMPUTE-HARNESS-P0.1`; promoted six existing R204 candidates into W14001-W14006 and source-matched R202 JLOGIC1, R204 JOBS1 and P1.16. Both-end Phoenix 1751280 direct-strip envelopes, a 322.5 mm rounded geometry screen and 12.06 mm2 bare-area input are controlled. All cut lengths, installed duct-fill results, Pi loading/back-power decisions and physical results remain open; thirteen holds and thirteen acceptance rows are unexecuted. No physical, safety or work authority closes. |
| R208 | Observation compute-power and partial-power correction | Issued `HR-V0-OBSERVATION-COMPUTE-POWER-BOUNDARY-P0.1`; proved the one-source 3V3 topology, seven partial-power states and eight faults. The 5.00 mA steady-load and 2.364 V source-high figures remain screens, not Pi 5 approval. A new BLOCKER records that the current 1.00 kohm RSO candidate screens at 3.300-3.333 mA under a hard short against TI's 3 mA recommended output-current envelope. Pi 5 load/DC limits, RSO correction, margins, back-power and all fourteen acceptance results remain open. No physical, safety or work authority closes. |
| R209 | Buffered observation-carrier correction — superseded | Introduced the four single-gate topology, but R210 found its 1.20 x 0.70 mm / 2.20 mm-row-spacing DBV lands did not match TI 4214839/K and its 99.63 uA GPIO short screen left negligible margin below TI's 100 uA characterization point. P0.3 is historical and not current for fabrication review. |
| R210 | Source-audited push-pull observation-carrier correction - superseded | Issued `HR-V0-RUNTIME-OBS-CARRIER-P0.4` and corrected the R209 land-pattern and narrow-margin defects, but R211 found the hard-grounded OE and positive push-pull power-state path. P0.4 is historical and prohibited for current fabrication review. |
| R211 | Open-drain observation-carrier power-state correction | Issued `HR-V0-RUNTIME-OBS-CARRIER-P0.5`; replaced all four G125 stages with exact `SN74LVC1G07DBVR`, added exact Panasonic `ERJ6ENF1002V` 10.0 kohm pull-ups ahead of the retained 39.0 kohm limiters and retained 330 kohm fail-low biases. The 2.598 V HIGH, 0.356 V LOW, 0.367 mA pull-up hard-short and 7.612 mA steady 3V3 values are analytical screens. Native ERC/DRC and the dedicated checker pass; Pi acceptance, power-state testing, physical evidence, qualified review and all work authority remain open. |
| R212 | P0.5 system-integration and configuration reconciliation | Issued `V3-P1.17-OBSERVATION-P0.5-CANDIDATE` and `HR-V0-CONFIG-REC-P0.2`. Machine checks prove all 79 P1.15 core component definitions are unchanged, only OBS1/PIOBS1 are added, the P0.5 and Pi-carrier terminal maps match exactly, and the bound source/connector hashes are current. P1.16, observation P0.2-P0.4 and configuration P0.1 are historical. Seven affected gates remain partial; 15 configuration holds and 12 acceptance rows remain open. No work authority exists. |
| R213 | Corrected custom-metal/BOM manufacturing baseline | Issued `HR-V0-MECH-BOM-BIND-P0.2`; replaced BOM-027's P0.7 manufacturing identities with the corrected P0.8 five-part STEP/DXF/drawing chain while retaining P0.7 only as the unchanged placement/collision basis. The binding controls 15 geometry identities, 26 drawing-explicit controls and 30 blank FAI operations. Twelve holds remain open; provider contact, quotation, purchase, fabrication, assembly, motion and energization remain prohibited. |
| R214 | Sol-review intake and exact-part complete-arm integration | Logged the supplied review summary, imported all five exact P0.8 custom-part STEP identities into `HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE`, regenerated the complete STEP/GLB and nominal collision/clearance/stop evidence, and synchronized firmware, gates, build traveler and `HR-V0-CONFIG-REC-P0.3`. P0.7 is inherited analytical/kinematic basis only. Every physical, DFM, FAI, stopping, structural, continuous-duty, functional-safety, qualified-review and work-authorization hold remains open. |
| R215 | Mechanical manufacturing qualified-review front door | Issued `HR-V0-MECH-MFG-REVIEW-P0.1`; collected the five current drawing/DXF/STEP sets, 26 controls, 30 blank FAI operations, nine interfaces, six fastener candidates, twelve DFM questions and twelve holds behind explicit precedence and authority rules. Current 80/20 source identities were refreshed; MISUMI/Accu live availability remains unresolved. No provider contact, quote, purchase, fabrication, assembly, connection, motion or energization authority exists. |
| R216 | E2 configuration and software-authority evidence parity | Issued `HR-V0-E2-EVIDENCE-P0.2`; corrected obsolete P1.8/P0.6 future-use form defaults and the shifted release-candidate field, hash-bound seven inputs, controlled eight current identities and made all twenty hardware cases inseparable from software evidence requiring trajectory `NONE`, torque request `FALSE` and stale replay `REJECTED`. Seven holds remain open; EG-018 through EG-022 remain partial; zero cases are executed and no run is authorized. |
| R217 | Current Boston fabrication-route reconciliation | Issued `HR-V0-BOSTON-FAB-ROUTE-P0.4`; bound five exact P0.8/R215/R173 inputs, screened six local/online/training/excluded routes against ten current official records, corrected the stale payload/motion statement and added nine unsent capability questions plus a no-file `NOT AUTHORIZED` template. No provider is selected, contacted, quoted or supplied geometry; EG-003/006/007 remain partial. |
| R218 | Measurable HR-V0 safety-requirements candidate | Issued `HR-V0-SRS-P0.2` with fifteen candidate requirements, seven timing records, sixteen unexecuted validation scenarios, twelve open common-cause records and two blank qualified-allocation rows. The J2-positive E4 setup candidate is 200 ms / 2.000 degrees at no more than 10 degrees/s; automatic motion remains prohibited pending a separately accepted bound. No PLr/SIL, achieved performance, safety approval or work authority is claimed; EG-012/021/022/026 remain partial. |
| R219 | Functional-safety reviewer route | Issued `HR-V0-FS-REVIEW-ROUTE-P0.1`; screened four official capability leads, required twelve competence/independence checks, ten phased scope records, ten unsent inquiry questions and sixteen unreceived deliverables. No provider is selected/contacted, no files or quote are authorized, and no PLr/SIL, physical validation, approval or work authority is claimed; EG-012/021/022/026 remain partial. |
| R220 | Current control-panel configuration overlay | Issued `HR-V0-CP-CONFIG-P0.1`; retained P0.6 only as planning geometry, bound it to current P1.15 / PCB-P1.0 / DXL-STAR-P0.2 identities, proved 66/66 panel endpoint parity, and generated current 34-row BOM and 26-row layout views. Twelve installation holds remain open; no supplier, procurement, fabrication, wiring, connection or energization authority is claimed; EG-002/003/004/018/020 remain partial. |
| R221 | Panel conductor and termination engineering basis | Issued `HR-V0-PANEL-COND-P0.1`; rejected 22 AWG at LC1D25BD control terminals, assigned a Belden 3057 16 AWG family/gauge candidate to 56 fixed internal endpoints, retained ten door-loom endpoints as `SELECTION REQUIRED`, and preserved all color/order-code, length, route, termination, DCR/voltage-drop, ampacity/bundling and protection holds. Twelve holds remain open; no procurement, fabrication, wiring, connection or energization authority is claimed; EG-003/004/010/015/018/020 remain partial. |
| R222 | Explicit panel point-to-point topology candidate | Issued `HR-V0-PANEL-P2P-P0.1` and unaccepted `V3-P1.18-PANEL-TOPOLOGY-CANDIDATE`; converted 66 one-ended labels into 55 explicit two-ended conductors and five physical distribution/junction nodes with no hidden-splice assumption. P1.15 remains current; ten door conductors plus every exact color/order code, length, route, termination, sizing/protection calculation and physical result remain open. EG-002/003/004/010/014/015/018/020 remain partial; no wiring or energization authority exists. |
| R223 | Panel node placement, stock and configuration reconciliation | Issued `HR-V0-PANEL-NODE-PLACEMENT-P0.1` and `HR-V0-CONFIG-REC-P0.4`; placed five node envelopes on candidate DR5/WD4, retained positive pre-kerf rail/duct stock arithmetic, and expanded the covered BOM to 95 groups. Thirty-seven route screens are explicitly not cut lengths. P1.15 remains current and P1.18 unaccepted; twelve placement and 26 configuration holds remain open; no procurement, cutting, drilling, wiring, connection or energization authority exists. |
| R224 | Native connected-ECAD web review surface | Issued `HR-V0-ECAD-WEB-REVIEW-P0.1`; SHA-bound thirteen actual P1.18 `.kicad_sch` files to thirteen KiCad SVG exports and added search, sheet-addressable navigation, zoom, direct SVG access and focus mode. ERC remains 0/0 but proves connectivity/annotation only. P1.15 remains current, P1.18 unaccepted, eight review/selection/physical/configuration holds remain open, and no physical or energization authority exists. |
| R225 | Source-bound watchdog permit topology proof | Issued `HR-V0-WD-PERMIT-TOPOLOGY-P0.1`; proves from P1.18 native source/netlist/wire parity that KWD1 and KWD2 ordinary NO contacts are in series before `SR1:A1`, with no KWD endpoint in either direct E-stop input loop. Nine Boolean screens retain the dual-weld/common-cause hazard. Both stages have zero safety credit, P1.18 remains unaccepted, eight holds and EG-004/012 remain partial, and no physical or energization authority exists. |
| R226 | Current-baseline K1/K2 application binding | Issued `HR-V0-K1K2-APP-P0.3`; proves 16 coil/EDM and 16 six-pole power-path terminal/net rows are identical between current P1.15 and unaccepted P1.18, and rechecks the current Schneider catalog/product/FAQ identities. It closes the stale P1.13 dossier binding only. Eleven holds and EG-002/004/013 remain partial; measured DC break/regeneration duty, protection, Schneider disposition, received/loaded/stopping/endurance evidence and qualified review remain open. |
| R227 | E2 control-only grounding/bonding boundary | Issued `HR-V0-E2-GND-BOUNDARY-P0.1`; binds 26 exact source/frame/shield endpoint rows across P1.15/P1.18, records the intentional `SAFETY_0V` 41-to-49 `XD0` delta, and freezes an external-factory-adapter/ELV-only enclosure boundary. `PSA1`, actuator power, `SP1` and `JFRAME1` remain absent/DNP. Fifteen evidence rows are unexecuted, twelve holds remain open, and EG-001/004/016/022 remain partial. |
| R228 | E2 configuration-bound pre-power verification candidate | Issued `HR-V0-E2-PREPOWER-P0.1`; maps all 55 unaccepted P1.18 conductors into exact continuity rows, with 45 fixed-internal method candidates and ten blocked moving-door rows, plus 16 isolation pairs, eight prohibited-pending-qualification backfeed cases and twelve live-dead-live absence-of-voltage points. Every numeric limit and result remains blank/unreleased, ten holds remain open, P1.18 remains unaccepted and EG-004/019/020/022 remain partial. |
| R229 | P1.18 configuration-disposition dossier | Issued `HR-V0-P118-DISPOSITION-P0.1`; proves all 77 original BOM rows, 308 original terminal/net rows, 106 named nets, 269 semantic wire-table rows and 63 unresolved records are preserved. P1.18 adds only five terminal devices and 32 controlled node-terminal rows on five existing nets. Nine child sheets are canonically identical after narrow administrative normalization. P1.15 remains current, P1.18 remains unaccepted, seven holds remain open and EG-002/004/020 remain partial. |
| R230 | P1.19 visual-correction and semantic-parity pass | Issued unaccepted `V3-P1.19-VISUAL-CORRECTION-CANDIDATE` and `HR-V0-P119-VISUAL-CORRECTION-P0.1`; reflows sheets 01/02/03/07/10 to A2, bounds every title block and records thirteen project visual passes. Machine checks prove 84 components, 106 native nets, five synchronized schedules and native netlist membership are unchanged; KiCad 10.0.5 ERC remains 0/0. P1.15 remains current; P1.18/P1.19 remain unaccepted; seven holds and EG-002/004/020 remain partial. |
| R231 | Sol R12 blocker reconciliation against R230 | Issued `HR-V0-SOL-R12-STATUS-R231`; maps every B-001 through B-018 finding to current evidence and remaining closure needs. Twelve were partially addressed/open, B-005 remained the HR-V0 source-level safety-architecture blocker, five remained HR-30 walking blockers and zero had qualified closure. This is project-owned reconciliation, not a new independent review. |
| R232 | P1.20 dual-SRA1-input watchdog-interlock correction | Issued unaccepted `V3-P1.20-WATCHDOG-INTERLOCK-CANDIDATE` and `HR-V0-P120-WD-INTERLOCK-P0.1`. Exactly seven terminal/net and seven native-net-membership changes place KWD1 and KWD2 on separate SRA1 input returns; all 84 component identities remain unchanged and ERC is 0/0. Twelve fault screens show either single weld is defeated while three dual/common-cause cases remain hazardous. Nine holds and EG-002/004/012/020/021/022 remain partial. P1.15 stays current; P1.20 has zero safety credit and no work authority. |
| R233 | P1.20 PNOZ/KWD application screen | Issued `HR-V0-PNOZ-KWD-APP-P0.2`; source-bound 31 P1.20 path terminals, 12 electrical screens, 10 fault cases and nine open holds. The proposed Pilz 24 V/50 mA input clears Phoenix item 2967060's published minimum-load and inrush envelopes on paper. B-005 becomes partially addressed/open, not closed. P1.15 stays current; P1.20 remains unaccepted with zero safety credit and no work authority. |
| R234 | P1.21 SRA1-supply watchdog correction | Issued unaccepted `V3-P1.21-SRA1-SUPPLY-WATCHDOG-CANDIDATE` and `HR-V0-P121-SRA1-SUPPLY-WD-P0.1`. Exactly seven terminal changes remove KWD1/KWD2 from PNOZ input loops, restore direct SR1-to-SRA1 inputs and series-gate only SRA1 A1. Fourteen fault cases, nine supply/contact screens and eleven holds retain manufacturer, routing, physical, PLr/SIL and qualified-review closure. KiCad ERC is 0/0. P1.15 remains current; P1.21 has zero safety credit and no work authority. |
| R235 | P1.21 manufacturer and no-load evidence route | Issued `HR-V0-P121-APP-EVID-P0.1` with 13 exact unsent Pilz/Phoenix questions, six official US routes, 12 response controls, ten authorization prerequisites, 15 required signals, 18 unexecuted tests and 14 open holds. No message was sent, no response or test exists, no dynamic limit was inferred, P1.15 remains current and P1.21 remains unaccepted with zero watchdog safety credit and no work authority. |
| R236 | Runtime evidence-log and calibration-route correction | Issued `HR-V0-EVID-LOG-P0.1`; requires an exclusive configuration-bound JSONL sink, fourteen event classes and per-record SHA-256 chaining; tightens the host source period to no more than 10 ms; and adds ten clock rows, twelve blank calibrations, fifteen unexecuted tests and fifteen open holds. Seventy-five supervisor/logging tests pass, but target timing, UTC, storage, calibration, HIL, qualified acceptance and all work authority remain open. Sol M-022 is partially addressed/open with zero safety credit. |
| R237 | Lot A source reconciliation and purchase-blocking variant correction | Issued `HR-V0-LOT-A-SRC-P0.1`; source-reconciles two XM540, two H101 and two S102 articles at a $1,182.22 visible subtotal. The official XM540 sales page title/TTL field requests `-T` while its package table names `-R`, so ordering is blocked pending written SKU binding. Four anomalies, eight unsent questions, ten open decision gates and twelve unexecuted receiving rows preserve zero procurement or work authority. |
| R238 | P1.21 consolidated native-KiCad review baseline | Proved P1.21 transitively inherits the P1.19 readable layout and P1.18 panel nodes; exposed all thirteen P1.21 sheets in one interactive guide; and controlled the six keyed P1.19-to-P1.21 terminal changes. P1.15 remains current, P1.21 remains unaccepted, eleven holds remain open and the supplied Sol text remains the existing R12 review rather than a new round. |
| R239 | P1.21 project visual review | Freshly inspected complete P1.21 pages 2 and 3 after the logic change and inherited the completed P1.19 project visual disposition for the other eleven pages. All thirteen receive a project visual PASS with zero observed clipping/collision findings. Only the project-owned visual hold closes; ten substantive holds and all independent/qualified decisions remain open. |
| R240 | P1.21 protected-routing candidate | Corrected seven P0.7 route meanings against P1.21, defined nine coordinate-bound planning routes and screened fourteen watchdog/supply-hot versus credited-input pairs with zero nominal centerline crossings. Nine physical/selection/qualified holds remain open; no route, P1.21 promotion or work authority is released. |
| R241 | P1.21 segregation-hardware and configuration P0.5 candidate | Replaced an undocumented divider concept with exact held Phoenix Contact item 3240187; placed a 369.8 mm WD5 envelope with nominal 10 mm/20 mm gaps; rejected the 20.8 mm existing-stock residual; exposed the WD5/WD2 junction, seven physical conductors, fill, thermal, separation and installation as open; and reconciled 96 BOM groups through `HR-V0-CONFIG-REC-P0.5`. P1.15 remains current, P1.21 unaccepted and no procurement or work authority exists. |
| R242 | P1.21 conductor and duct-occupancy candidate | Assigned held Belden 3057 BL005 to the seven planning routes and reproduced geometry-only WD5/WD2 fill screens while retaining color, DCR, cut, protection, thermal, termination, physical and qualified-review holds. `BOM-097` and configuration P0.6 reconcile the historical 97-group state; P1.15 remains current and P1.21 remains unaccepted. |
| R243 | P1.21 endpoint-termination candidate | Mapped fourteen endpoints to held Phoenix Contact ferrule candidates: twelve item 3200043 insulated 8 mm and two item 3200263 uninsulated 7 mm. Bound exact crimper, stripper and torque-driver candidates; limited the 40 N/60 s criterion to sacrificial crimp coupons; retained exact-bit, calibration, received-material, installed-retention, terminal-application and qualified-review holds; and reconciled 98 BOM groups through `HR-V0-CONFIG-REC-P0.7`. P1.15 remains current, P1.21/R243 remain unaccepted and no work authority exists. |
| R244 | P1.21 nominal DCR/drop and bit-evidence boundary | Converted the current manufacturer-nominal 4.4 ohm/1000 ft at 20 C to 0.014435695538 ohm/m and calculated four one-way centerline conductor-only planning drops while leaving C-05 uncalculated. Confirmed that current Pilz and Phoenix sources do not justify a purchase-ready exact bit; Phoenix 1212568 remains only the strongest held relay-terminal candidate. Twelve holds remain; the 98-group BOM is unchanged; P1.15 remains current and P1.21/R244 remain unaccepted. |
| R245 | Integrated custom-part and firmware mechanical-source binding correction | Corrected all five custom-part rows to the integrated P0.8 arm without changing any of fifteen artifact hashes; bound both firmware configurations to the same eight-record SHA-256 source manifest; and reconciled P0.9. Physical/HIL acceptance remains absent, motion remains fail-closed, and shop-document/DFM/FAI/qualified-review work remains open. |
| R246 | P1.21 static 24 V control-rail budget | Bound GlobTek as the 24 V control source, excluded the separate 12 V Mean Well actuator source, traced eight terminal-addressed loops and reproduced six raw-headroom screens. Eighteen missing inputs, ten open holds and seven unexecuted acceptances keep every installed margin `NOT CALCULABLE`; P1.21 remains unaccepted. |
| R247 | Mechanical shop, RFQ and unpowered assembly candidate | Corrected the five current custom-part drawing identifiers, warning and title blocks without changing geometry; bound five drawings, five DXFs and five STEP files into an exact unsent RFQ payload; and defined 21 zero-energy assembly steps plus nine interface checks. Formal datum/GD&T, provider DFM, FAI, physical fit/proof, exact joint controls and every work authority remain open. |
| R248 | Complete moving-system mass, COM and inertia evidence contract | Mapped all 17 moving-mass ledger rows to blank received-evidence records; added 170 repeat slots, four assembly mass closures, eight two-axis COM rows, four calibrated-bifilar records and six inertia rows. No physical result exists; B-010, R247-H11 and all work authority remain open. |
| R249 | Accepted-property propagation and stale-analysis control | Added a six-row fail-closed accepted-property compiler, twelve downstream consumers, eight prohibited stale planning inputs and a ten-step rebuild sequence. No accepted property or downstream analysis exists; zero blockers or gates close. |
| R250 | Datum/GD&T qualified-review proposal | Proposed five functional datum schemes, twenty FCF candidates and inspection uncertainty controls. Geometry is unchanged; formal GD&T and fabrication authority remain false. |
| R251 | First physical shop-session contract | Bound ten purchase gates, eight supplier questions, six articles, seven roles, six instruments, eight holds, eighteen operations and all twenty HSI records. Nothing is authorized or executed. |
| R252 | Zero-energy joint-stack fixture candidate | Bound exact XM540/H101/S102 STEP sources to six nominal S102-face contact candidates, six keepouts, twelve fail-closed steps, twelve open selections and configuration P0.16. The fixture is not buildable; zero operations or acceptances are executed and nothing is authorized. |
| R253 | Rank-6 3-2-1 joint-stack fixture correction | Found P0.1's six coplanar contacts have rank 3; prohibited that scheme; issued nominal rank-6 P0.2 with three A, two B and one C contacts, current ROBOTIS evidence, fourteen steps and fourteen selections. P0.2 remains not buildable and nothing is authorized. |

See [the review ledger](docs/review-ledger.md) for dates, configurations, evidence, reviewer independence, and counting rules. No review has approved fabrication or energization.

## Release rule

Only revisions tagged `BUILD-RELEASE-*` after the review gates in the system specification may be fabricated or energized. Documents labeled concept, draft, or preliminary are planning artifacts, not assembly instructions.
