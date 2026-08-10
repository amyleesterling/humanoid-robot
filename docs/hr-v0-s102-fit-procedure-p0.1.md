# HR-V0 FR13-S102K Tapped-Pattern Fit Procedure P0.1

**PRELIMINARY - UNPOWERED FIT INSPECTION ONLY. NOT A FABRICATION OR ENERGIZATION RELEASE.**

Procedure ID: `INSPECT-MECH-004`  
Coupon: `MV0-FC02_s102_32x16_tapped_pattern_coupon`  
Record template: `tests/forms/hr-v0-fit-coupon-inspection-template.csv`

## Scope

Verify that the selected four-hole `32 x 16 mm` M2.5 x 0.45 tapped-through pattern on the received FR13-S102K broad face aligns with the controlled clearance-hole coupon. This inspection does not qualify the threads, fastener length, engagement, material, torque, locking method, frame strength, or structural joint.

## Controlled evidence

- DXF/STEP/STL and 1:1 overlay under `cad/hr-v0/generated/fit-coupons/`;
- generated-artifact hashes in `cad/hr-v0/generated/SOURCE-MANIFEST.csv`;
- manufacturer drawing and STEP hashes in `cad/vendor/robotis/vendor-manifest.csv`; and
- interface/fastener boundary in `docs/hr-v0-joint-interface-fasteners-p0.1.md`.

## Inspection

1. Keep the robot and all actuators unpowered. Inspect the loose frame on a clean surface.
2. Record the kit SKU, received label, serial/lot if present, frame photograph, repository commit, coupon hash, and drawing hash.
3. If using the A4 overlay, print at actual size/100%, disable all fit/shrink options, and record both 100 mm scale-bar measurements.
4. Make `MV0-FC02` from a low-cost nonstructural material. Record method, material, measured thickness, warp, burrs and damaged holes.
5. Orient the coupon to the S102 broad face using the drawing datum and photographed frame features. Do not assume rotational symmetry.
6. Seat the coupon without bending, prying, filing, or drawing it into alignment.
7. At each of the four positions, insert the identified M2.5 gauge or candidate fastener by hand only. Stop immediately on resistance. Do not bottom a screw in an unknown thread depth.
8. Record each position separately, including flat seating, entry without force, observed angular/positional offset, thread condition, and photograph reference.
9. Any mismatch, uncertain orientation, damaged thread, or forced entry blocks the selected pattern. Revise only through configuration control and repeat all four positions.

## Disposition

Exact dimensional tolerances and the thread/gauge acceptance method remain `SELECTION REQUIRED`. A geometrically successful coupon check supports only the selected pattern interpretation. It does not release production metal or a screw stack.
