# Sol Independent Engineering Review — Supplied Summary

> **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Received: 2026-08-07  
Reviewed baseline stated by reviewer: `HR-30-SYS-R0.2`  
Configuration-control note: this is the user-supplied summary of the same 18 BLOCKER / 30 MAJOR / 8 MINOR, 56-finding Sol dossier already controlled as R12. It is preserved without counting a duplicate independent-review round. The linked sandbox files were not present in this repository when this summary was received.

## Reviewer verdict

Project Button is a strong preliminary systems architecture, not yet a buildable machine. HR-V0 build readiness is **NOT READY** and energization readiness is **PROHIBITED**. HR-30W walking is physically plausible but not demonstrated.

The reviewer reported:

- 18 BLOCKER findings;
- 30 MAJOR findings;
- 8 MINOR findings;
- 62 of 62 requirements still draft on the reviewed baseline;
- 106 unresolved electrical selection records; and
- zero requirements with executed, approved verification evidence.

The principal issues named were missing native source in the authoritative repository; electrical revision mismatch; no buildable mechanical definition; a watchdog-permit single-fault concern; absent functional-safety allocation and stopping-time requirement; unproven DC contactor duty and PE/grounding; no closed mass/inertia model; unproven continuous leg torque; no safe-power-loss strategy; incomplete restraint definition; and architecture-only battery, sensor, bus and real-time-control designs.

The reviewer independently reproduced approximately 1.70 N·m shoulder and 0.62 N·m elbow gravity loads for HR-V0 and judged the bench demonstrator technically achievable. The review explicitly rejected treating the XM540's 11.7 N·m at 14.8 V as continuous torque or multiplying it by an external ratio as evidence of continuous-duty capability.

Primary links supplied with the summary:

- Project Button preliminary electrical PDF: <https://project-button-workshop.amysterling.chatgpt.site/engineering/electrical/hr30/v2/project-button-electrical-v2-preliminary.pdf>
- ROBOTIS XH540-W270 e-Manual: <https://emanual.robotis.com/docs/en/dxl/x/xh540-w270/>

## Current project disposition

R13–R48 made several baseline claims stale by adding native source, connected V3 candidates, mechanical quote geometry, firmware source, deterministic release control, a complete BOM closure register, a controlled datum/interface package and an exact catalog frame-joint candidate. Those are project corrections, not executed physical proof or independent approval. The central Sol verdict remains open: no fabrication or energization release exists.

R48 removes the ambiguous frame-gusset/order-code allocation and adds an unexecuted torque/slip/proof route. It does not close the XM540/JST connector conflict, continuous torque, protection coordination, actual frame-joint proof, bench anchoring, physical-build, functional-safety, or energization findings.
