# HR-V0 Pi observation panel integration P0.1

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

`HR-V0-PI-OBS-INTEGRATION-P0.1` is a configuration-controlled analytical overlay, not a modification or release of control-panel P0.6. It resolves a source-level placement conflict: R161 already occupies the lower reserve with three DXL carrier candidates, so R202 is instead rotated 90 degrees counterclockwise at nominal panel origin `(433.0, 300.0)` in the compute column.

The source transform places `JLOGIC1` at `(478.00, 306.00)` and `JFIELD1` at `(478.00, 414.00)`. A reference-only centred R204 transform places `JOBS1` at `(478.25, 119.25)`; its real position remains unknown until received stack metrology. The resulting WD2 route screens are 335.4 mm on the six-wire compute side and 276.0 mm on the five-wire field side. Both final cut lengths remain `SELECTION REQUIRED`.

The overlay records ten planar clearance screens, four transformed mounting-hole coordinates, eleven interface-parity rows, thirteen open evidence holds and sixteen unexecuted acceptance rows. It proves no depth, mounting, duct fill, separation, cut length, termination, physical fit, electrical performance, functional safety or work authority.
