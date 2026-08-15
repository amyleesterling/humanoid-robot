# HR-V0 observation-carrier mounting stack P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R260 defines exact, unreleased mounting-hardware candidates for both observation carriers. It does not release an order, panel hole, assembly operation, harness cut or powered test.

The runtime observation carrier candidate uses four Essentra `TNM3-6.5-10-1` M3 female/female nylon standoffs and eight M3 x 6 nylon pan screws. The legacy screw identity `0120070000VR` is retained only under hold because the live manufacturer page also names replacement `NSE-1580-M3-6`; written order-code equivalence is required.

The Pi carrier candidate uses four Essentra `300251659935` M2.5 female/female 16 mm glass-filled-nylon standoffs and eight `50M025045P006` M2.5 x 6 nylon screws. Samtec's current `ESQ-120-33-G-D` page restricts the part to existing customers. Its series print gives a nominal 16.13 mm dimension for lead style 33, while Raspberry Pi calls 16 mm spacer height ideal with the Active Cooler. The 0.13 mm nominal difference is not accepted by calculation; the received stack must fit freely without clamp force, board bow, incomplete insertion or connector side load.

Runtime candidate panel centers are recorded as DO NOT DRILL. Pi mounting remains a received-stack operation; the Raspberry Pi mechanical drawing is reference-only and cannot serve as production acceptance evidence. Exact routes and cable cuts remain selection required until the physical placements, duct, case and endpoints are frozen.

Controlled files are in `electrical/integration/hr-v0-observation-mount-stack-p0.1/`; the interactive mirror is `release/hr-v0/observation-mount-stack-p0.1/`. All fit, torque, load, creep, thermal and qualified-review rows are blank and open.
