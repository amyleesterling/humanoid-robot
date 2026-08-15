# HR-V0 integrated mechanical and firmware source binding P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Date: 2026-08-11  
Round: R245  
Identifiers: `HR-V0-MECH-BOM-BIND-P0.3`, `HR-V0-FW-MECH-SRC-BIND-P0.1`, `HR-V0-CONFIG-REC-P0.9`

## Correction made

The active custom-part binding contradicted the current arm configuration. Its five rows named the pre-integration `HR-V0-ARM-ARCH-P0.8-DWG-CANDIDATE`, while the current complete arm is `HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE`.

P0.3 corrects that configuration identity for one each of `MV0-C01`, `C04`, `C05`, `C06` and `C07`. It deliberately retains all fifteen STEP, finished-DXF and drawing hashes from P0.2; no geometry was silently changed. P0.2 and the R137 drawing package remain historical records.

Both firmware configuration files now bind an exact SHA-256 manifest covering eight records from the integrated P0.8 assembly, corrected P0.3 custom-part binding, inherited P0.7 transform/interface/stop allocation basis and P0.3 hard-stop datum basis.

The supervisor rejects a stale manifest hash exactly as it rejects a stale arm revision. The configuration-controlled source identity is therefore separate from physical acceptance.

## What did not close

The source binding does not prove that a part was made, measured, assembled or safe. The separate mechanical acceptance hash remains `SELECTION REQUIRED`, release state remains `CANDIDATE-NOT-RELEASED`, and the transport remains fail-closed.

The active fabrication gap is now explicit: successor shop drawings must name the integrated configuration and receive qualified disposition of datum/GD&T, title blocks, general tolerances, surface finish, material purchase requirements, RFQ payload, part-specific assembly instructions, DFM/FAI and physical proof. No supplier transmission or work is authorized.

## Sol R12 disposition

This correction addresses one configuration-management defect within Sol's missing buildable-mechanical-definition finding. It does not close any Sol blocker. The pasted Sol summary remains the already controlled R12 review and is not counted as a new independent round.
