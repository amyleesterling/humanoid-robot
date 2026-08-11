# HR-V0 P1.21 protected-routing candidate P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-P121-ROUTING-P0.1`
Review round: R240
Date: 2026-08-11

## Outcome

R240 corrects the stale P0.7 routing overlay against the actual P1.21 conductor semantics and creates a coordinate-bound routing candidate. It does not release a harness or physical panel route.

- `P2P-005` changes from the obsolete `SR1:A1 -> KWD2:14 / SR1_A1_WD_GATED` meaning to `KWD2:14 -> SRA1:A1 / SRA1_A1_WD_GATED`.
- `P2P-015` retains `KWD1:14 -> KWD2:11` but uses the P1.21 net `WD_SRA1_SUPPLY_INTERMEDIATE`.
- `P2P-035` is proposed, not inferred, as `XD24:02 -> SR1:A1 / SAFETY_24V`; the terminal allocation remains unaccepted and marked `SELECTION REQUIRED`.
- Four existing XD24/KWD allocations remain explicit planning candidates.
- Nine route records bind planning polylines to the 533.4 x 685.8 mm backplate frame.
- Fourteen pairwise screens find zero intersections between the declared watchdog/supply-hot and credited-input centerlines.

The zero-crossing result applies only to ideal centerlines. It does not account for conductor diameter, bend radius, terminal position, duct fill, divider thickness, cover displacement, strand escape, installation tolerance or service loops.

## Fail-closed routing concept

Candidate credited-input conductors use the left/node corridor. Ordinary watchdog and supply-hot conductors use the bottom duct, right duct and a reserved top band, then stop at component-envelope boundaries. They do not share an unpartitioned planning corridor.

`DF-01`, KWD1 and KWD2 retain zero safety credit. The routing concept does not establish PLr, SIL, category, diagnostic coverage or common-cause exclusion.

## Unresolved selections

The following remain `SELECTION REQUIRED`: actual terminal positions and orientation; duct/divider/barrier/cover products; numeric separation; conductor family, gauge, color and order code; fill, bend and thermal limits; cut lengths; service loops; ferrules and terminal covers; protection coordination; fault current; inrush; duty; ambient; bundling; door loom; jurisdictional interpretation; inspection acceptance limits; and qualified disposition.

## Review boundary

P1.15 remains current. P1.21 remains the preferred consolidated review candidate but is not accepted. Nine R240 holds remain open, physical inspection records are blank, and no work authority exists.

The supplied Sol verdict is the same R12 independent review already controlled in the ledger. R240 records its continuing applicability but does not count it as a new independent review or close any Sol finding.

## Controlled artifacts

- [Interactive routing guide](../release/hr-v0/p121-protected-routing-p0.1/index.html)
- [Engineering dataset](../electrical/routing/hr-v0-p121-protected-routing-p0.1/)
- [Independent review request](reviews/2026-08-11-r240-independent-review-request.md)
- [Validation record](reviews/2026-08-11-r240-validation-record.md)
