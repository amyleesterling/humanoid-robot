# Project Button Configuration Management

Package baseline: **HR-30-SYS-R0.2**  
Baseline date: 2026-08-06  
Status: preliminary engineering baseline; not approved for fabrication, procurement, or energization

## Identifier hierarchy

- **HR-30-SYS-R0.2** identifies this integrated systems-specification package.
- Each controlled document retains its own document ID and revision. A document revision is not the package baseline.
- **Project Button Electrical V2.1** identifies the connected KiCad electrical package. Its revision is independent of the systems package.
- **Project Button Electrical V3-P0.1** identifies the historical R16 connected candidate retained in Git history.
- **Project Button Electrical V3-P0.2** identifies the historical R17 restart-chain correction candidate.
- **Project Button Electrical V3-P0.3** identifies the historical R18 voltage-boundary correction with opaque feedback-interface blocks.
- **Project Button Electrical V3-P0.8** identifies the current R29 correction candidate. It retains P0.4's pin-level `ISO1212DBQ` circuit, P0.5's operator/compute-source identities, P0.6's XW E-stop contact positions, and P0.7's JA1/DC1 selections. P0.8 freezes a `VO618A-4X017T` heartbeat path, exact 910 ohm/10 kilohm passives, two separate `TPL7407LPWR` relay-driver packages, and 100 nF COM bypass candidates. Source-side contact construction, harness current sharing, protection/distribution, feedback-network passive order codes, PCB layout, COM-slew, brownout/EMC, HIL/fault evidence, received terminals, panel human factors and qualified review remain open. `P0.8` has not superseded V2.1 and is not a released electrical baseline.
- **HR-V0-FW-P0.1** identifies the preliminary watchdog/supervisor source candidate. It has executable source tests but no released binary or HIL evidence.
- **HR-V0-MECH-R0.1-PRELIMINARY** identifies the current native mechanical quote-geometry baseline. R21 corrected its interface topology without advancing the revision: `MV0-FC01` checks the selected H101 PCD22 candidate pattern and `MV0-FC02` checks the selected S102 32 x 16 mm candidate pattern. R22 adds a hard-stop kinematic/load-case study and validation plan, not fabricable stop parts. R23 adds a controlled moving-mass ledger and measurement route; its 565.4 g known subtotal and 184.6 g unresolved headroom are not mass closure. R24 selects the proposed RM-X52 gripper-mechanism parent kit and the FR12-H104K 24 x 12 mm four-hole subset, adding `MV0-FC03` and receiving/inspection records. R25 adds the generated guard/catch space study and five cable-route zones; its 25 mm stopping and clearance allowances are provisional planning inputs, not safety distances. No coupon, datum study, mass screen, or space claim releases a production part, fastener stack, bumper, impact capacity, panel, receiver, harness, grip-force limit, or gripper load path.
- Website releases are identified by their website Git commit and hosted version. A website release is a presentation of controlled artifacts, not an engineering revision.

The label **V2.2** is not a released engineering identifier and must not be used for this package.

## Controlled baseline summary

This baseline contains 67 draft requirements and 40 open risks. HR-V0 and HR-30 release specifications remain unbuilt and unvalidated. Individual files may advance only through a recorded change that updates their revision, linked requirements, evidence, and review disposition as applicable.

## Release rule

Neither a clean ERC result nor a website deployment constitutes design approval. The package remains **PRELIMINARY—NOT APPROVED FOR ENERGIZATION** until the applicable selections, calculations, physical tests, and qualified electrical and functional-safety reviews are complete.
