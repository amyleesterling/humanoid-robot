# HR-V0 DYNAMIXEL star injection DXL-STAR-P0.1

**PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

This native KiCad candidate implements one fixed central branch-isolating board:

- `JC1` is JST `B3B-EH-A`; pins 1/3 carry GND/DATA and pin 2 has no PCB net or route.
- `JP1`-`JP3` are JST `B2P-VH` protected branch inputs; project pin 1 is VDD and pin 2 return.
- `JA1`-`JA3` are JST `B3B-EH-A` actuator outputs using standard ROBOTIS TTL pin order.
- `J1_VDD`, `J2_VDD`, and `J3_VDD` are routed separately and never join.
- `DXL_TTL_DATA` and `ACT_0V_PE_BONDED` are common by design.

The source contains no released cable lengths, branch conductors, fuse ratings, assembly outputs, Gerber/drill package or permission to fabricate. U2D2 pin-2 omission, VDD isolation, grounding, star-bus signal integrity, connector temperature, no-backfeed and fault behavior require physical evidence and qualified review.

Generate with KiCad 10 bundled Python:

`"C:\Program Files\KiCad\10.0\bin\python.exe" tools/generate_hr_v0_dxl_star.py`

Then run `tools/check_hr_v0_dxl_star.py` with the same interpreter. ERC/DRC prove encoded connectivity only.
