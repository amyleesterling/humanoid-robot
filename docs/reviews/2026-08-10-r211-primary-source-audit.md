# R211 primary-source audit and correction disposition

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R211 rechecks the R210/P0.4 observation-carrier power-state assumptions against current official Texas Instruments, Raspberry Pi and Panasonic records. This is a project-owned source audit, not an independent or qualified electrical or functional-safety review.

## Findings

1. **BLOCKER - avoidable positive drive during power-state disagreement.** P0.4 permanently asserted all four active-low `SN74LVC1G125` output enables by tying OE to ground. Texas Instruments states that, to ensure high impedance during power up or power down, OE should be tied to VCC through a pull-up resistor. The hard-enabled push-pull stages also retained a positive source toward the Pi through the 39.0 kohm limiter. P0.4 is superseded and prohibited for current fabrication review.
2. **CORRECTION - open-drain partial-power device.** P0.5 uses exact active `SN74LVC1G07DBVR` open-drain buffers. TI SCES296AG Rev AG, revised October 2025, specifies partial-power-down operation using Ioff and identifies DBV pin 1 as no-connect, pin 2 as A, pin 3 as GND, pin 4 as Y and pin 5 as VCC. The project-owned DBV land geometry remains bound to TI drawing 4214839/K.
3. **CORRECTION - explicit pull-up identity.** Each output uses exact Panasonic `ERJ6ENF1002V`, 10.0 kohm, 1%, 0805, 0.125 W, +/-100 ppm/K, connected to the same proposed Pi 3V3 rail ahead of the retained 39.0 kohm GPIO limiter. The pull-up source is therefore absent when carrier 3V3 is absent; this removes the prior positive push-pull source but does not prove Pi compatibility.
4. **MAJOR - Raspberry Pi electrical limits remain unavailable.** The official RP1 Peripherals reference publishes bank-0 3.3 V selection and 2/4/8/12 mA drive settings, but the controlled official source set does not publish the required Pi 5/RP1 VIH, VIL, leakage, capacitance, clamp-current or unpowered-pin limits. No Raspberry Pi input acceptance is claimed.
5. **MAJOR - system power states remain untested.** The official HAT+ specification release 2024-12-05 requires compatibility with STANDBY, in which 5 V is present while 3.3 V is absent. P0.5 is not represented as a HAT+, but STANDBY, rail ramp, brownout, recovery and back-power behavior remain relevant application boundaries requiring manufacturer disposition and physical testing.

## Analytical screens

- loaded logic-HIGH floor: 2.598 V;
- asserted logic-LOW ceiling: 0.356 V;
- pull-up hard-short current: 0.367 mA; and
- proposed Pi 3V3 steady-load screen: 7.612 mA.

These are analytical screens with encoded assumptions, not Raspberry Pi acceptance, production limits, test results or safety evidence. Fourteen application, manufacturing, physical-test and review holds remain open. Every channel is an ordinary diagnostic with zero functional-safety credit.

Primary sources:

- Texas Instruments, `SN74LVC1G125`, SCES223T Rev T: <https://www.ti.com/lit/ds/symlink/sn74lvc1g125.pdf>
- Texas Instruments, `SN74LVC1G07`, SCES296AG Rev AG and DBV package drawing: <https://www.ti.com/lit/ds/symlink/sn74lvc1g07.pdf>
- Texas Instruments active `SN74LVC1G07` product record: <https://www.ti.com/product/SN74LVC1G07>
- Panasonic `ERJ6ENF1002V` product record: <https://industrial.panasonic.com/ww/products/pt/general-purpose-chip-resistors/models/ERJ6ENF1002V>
- Raspberry Pi, RP1 Peripherals: <https://datasheets.raspberrypi.com/rp1/rp1-peripherals.pdf>
- Raspberry Pi, HAT+ Specification, release 2024-12-05: <https://datasheets.raspberrypi.com/hat/hat_plus_specification.pdf>
