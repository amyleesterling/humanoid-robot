# Independent review request - HR-V0 frame/sign convention P0.1

> **PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION, CONNECTION, OR ENERGIZATION.**

Review `HR-V0-FRAME-CONV-P0.1` against the current `HR-V0-MECH-P0.6 / HR-V0-ARM-ARCH-P0.7 / HR-V0-ACT-P0.3 / HR-V0-SUP-P0.3` candidate.

Please independently check:

1. Whether A0 `+X right / +Y front / +Z up` is right-handed and consistent with the base, frame-joint and arm-coordinate artifacts.
2. Whether the J1, J2 and H104 origins/orientations reproduce the controlled P0.7 transform schedule exactly.
3. Whether positive J1/J2 engineering rotation is correctly described as right-hand rotation about local `+X`, with outgoing local `+Y` moving toward local `+Z`.
4. Whether J2 geometric zero is clearly separated from its candidate `15..115 degree` command domain and its nominal `117.999985 degree` positive-metal stop contact.
5. Whether the legacy guard `x=depth / y=width / z=height` labels are correctly classified as a layout convention with determinant `-1`, and whether the mapping to right-handed `G0_RH` is unambiguous.
6. Whether the package avoids inferring DYNAMIXEL raw direction, raw scale, raw zero, received identity, start tolerance or gripper opening from native CAD or meshes.
7. Whether the blank calibration form is sufficient to bind two independent references, measurement uncertainty, received identity, raw results and witness evidence for every axis.
8. Whether HR-V0's no-mirroring statement and HR-30's separate left/right convention hold correctly implement `CFG-002` without implying full-body closure.
9. Whether source hashes, firmware limits and current mechanical identifiers are synchronized and fail closed on drift.
10. Whether any text, diagram or interactive behavior could be misread as motion authorization, physical validation or functional-safety approval.

Report findings as BLOCKER / MAJOR / MINOR with exact file/row references. Do not approve fabrication, connection, motion or energization.
