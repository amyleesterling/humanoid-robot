# R149 independent review request - watchdog PCB BOM binding

**PRELIMINARY - NOT APPROVED FOR FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

Please independently verify that live `BOM-048` now names `PCB-P0.9 / Project Button Electrical V3-P1.14` and `HR-V0-WD-PCBA-DATA-P0.2`, not historical PCB-P0.5.

Recompute the native PCB, assembly-BOM, placement and binding SHA-256 identities. Confirm sixteen assembly-BOM lines total 42 populated references, all 42 placement references reconcile, four NPTH features remain separate, and all twelve P0.2 assembly holds remain open.

Confirm that no current Gerber/drill CAM, supplier-normalized XYRS or supplier packet exists and that historical PCB-P0.5 CAM cannot be treated as current. Search current configuration guidance for any remaining live PCB-P0.5 claim.

Finally, verify that `BOM-048` remains an exact-candidate hold only; `EG-003` and `EG-004` remain partial; and provider selection/contact, upload, quotation, fabrication, assembly, physical article, connection, motion, energization and safety credit all remain false or prohibited.
