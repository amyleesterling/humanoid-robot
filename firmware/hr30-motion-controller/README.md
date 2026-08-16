# HR-30 deterministic motion-controller source P0.1

**PRELIMINARY - HOST AND UNFLASHED TARGET NO-MOTION EVIDENCE ONLY - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

This is the canonical portable C source for the `FIRST_POWER_NO_MOTION` profile. Build the controlled host vector evidence with `tools/build_hr30_motion_host_runner.ps1`; generate the synchronized whole-body engineering package with `tools/generate_hr30_motion_firmware_p01.py`.

The source forces all 25 torque-enable bits, all eight bus-transmit paths, precharge request and action-ready inactive. A reproducible freestanding STM32H743 target now exists in `output/stm32h743-p0.1`; it remains unflashed and has no physical or HIL result.
