# HR-V0 Raspberry Pi observation pin map P0.1

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-RUNTIME-OBS-PINMAP-P0.1`

Date: 2026-08-10
Carrier baseline: `HR-V0-RUNTIME-OBS-CARRIER-P0.2`

## What R203 resolves

R203 freezes the source-level Raspberry Pi 5 header allocation for the four diagnostic outputs of the R202 carrier without claiming that a cable, installed image, GPIO device, physical circuit or powered test exists.

| Carrier terminal | Function | BCM/RP1 GPIO | Pi physical pin | Polarity |
| --- | --- | ---: | ---: | --- |
| JLOGIC1.1 | 3.3 V carrier supply candidate | — | 17 | — |
| JLOGIC1.2 | Compute return | — | 20 | — |
| JLOGIC1.3 | SR1 diagnostic input | 22 | 15 | Active-high |
| JLOGIC1.4 | SRA1 diagnostic input | 23 | 16 | Active-high |
| JLOGIC1.5 | K1 diagnostic input | 24 | 18 | Active-high |
| JLOGIC1.6 | K2 diagnostic input | 25 | 22 | Active-high |

The previously controlled ordinary heartbeat remains BCM/RP1 GPIO17 at physical pin 11 with physical pin 6 as its return. It is distinct from physical pin 17, which is a 3.3 V supply. The diagnostic inputs have zero motion authority and zero functional-safety credit.

## Source and conflict basis

Current Raspberry Pi documentation identifies the standard 40-pin 2.54 mm header, 3.3 V GPIO behavior, configurable pulls, and input state at power-on. The official pinout diagram supplies the physical-pin mapping. RP1 documentation identifies the relevant pad-control registers and shows output-disable asserted at reset, while pull reset state varies. Therefore the application requires explicit input ownership with software bias disabled and physical proof of the external fail-low behavior.

The allocation is not conflict-free merely because no duplicate appears in this repository. Raspberry Pi documents `enable_jtag_gpio=1` as assigning GPIO22 through GPIO27 to Arm JTAG, and DPI can also use GPIO17 and GPIO22 through GPIO25. The proposed Project Button overlay contains no such setting, but the installed image does not exist. Exact `config.txt`, command line, device-tree overlay inventory, `pinctrl` and `gpioinfo` evidence remain mandatory before any isolated HIL authorization.

`/dev/gpiochip*` is deliberately not frozen from online documentation. Its status remains `SELECTION REQUIRED`. The exact installed distribution, kernel, libgpiod version, chip label/path, line ownership and numbering must be read from the controlled target image. The committed host configuration therefore remains fail-closed.

## Harness boundary

The electrical mapping is frozen; the physical harness is not. No Pi-side housing, socket, contact, adapter PCB, wire, ferrule, strip length, torque, label, length, retention or strain-relief order code is released. Those selections require primary manufacturer evidence, received geometry, cooler/enclosure clearance, grounding review, continuity, back-power tests and qualified acceptance. Loose unretained individual jumper contacts are not a released construction.

## Remaining gates

Eight local holds remain open: exact Pi-side mate, wire and JLOGIC termination, mechanical routing/retention, target gpiochip identity, boot/overlay ownership, startup/power-loss evidence, isolated HIL and qualified review/work authority. `ROH-006` advances only to partial on controlled source allocation. No Sol R12 finding, energization gate or work authority closes.

Passing the repository checker proves row counts, mapping parity, source records, host-configuration consistency and fail-closed warnings only. It does not prove a connected or functioning machine.
