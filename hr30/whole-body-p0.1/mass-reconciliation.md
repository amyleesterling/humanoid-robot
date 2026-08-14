# HR-30 whole-body mass reconciliation P0.1

**PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION**

The former 9.63 kg value was an allocation, not a physical mass model. This pass inventories 66 materialized fabrication-CAD parts, 25 actuators, and 142 joint-hardware candidate solids. The gross identified planning subtotal is **8.693 kg** before the unmodeled electrical, compute, sensing, audio, harness, fastener, cooling, sole, restraint and energy-storage items.

Relative to commit `dfb9a7d`, the lightweight topology reduces the gross identified candidate subtotal by **4.631 kg**. The body retains all 25 axes, complete limbs and hands while using hollow torso rails, windowed and slotted load-path plates, thinner service covers, hollow aluminum shaft screens, topology-lightened carrier frames and pulleys, and actuator-plus-one-external-bearing support on direct axes. Those changes are geometry candidates, not strength or bearing-life evidence.

To keep the dynamics model from understating geometry already present, each link now uses the greater of its previous allocation and its identified planning subtotal. This produces a provisional dynamics mass of **13.227 kg** and neutral COM **(-0.001, -0.000, 0.331) m**. The resulting margin to the 10 kg program maximum is **-3.227 kg**; because major items remain unmodeled, this is not evidence that the maximum closes.

The actuator planning subtotal uses published masses from current official ROBOTIS e-Manual pages checked 2026-08-14. The two elbows remain an XM430/XM540 decision, so the planning and maximum columns use the heavier 165 g candidate while the minimum column uses 82 g. CAD actuator placement is the geometric centroid of the SHA-bound manufacturer packaging body, not a published center of gravity.

Fabrication and joint-hardware values are volume-times-density screens. Candidate solids may interpenetrate and manufacturing redesign will change them; no overlap deduction is taken. The URDF and MJCF inertias remain box approximations for development simulation. Physical mass, COM and inertia identification, exact selections, structural closure, gait validation and qualified review remain mandatory.
