# R172 independent review request

Review `HR-V0-RPI-OS-SBOM-P0.1` as publisher-inventory evidence, not as a promoted target image.

1. Reproduce the controlled compressed-SBOM byte count and SHA-256.
2. Confirm SPDX document identity, creation time, creator/tool and the 4,743/632/3,791/320 classification.
3. Reproduce the 632-row DPKG lock and its SHA-256 from the controlled payload.
4. Check every critical-package version and the explicit absence findings for `python3-serial` and `dynamixel-sdk`.
5. Challenge the distinction between publisher inventory, image acquisition, media readback, target `dpkg-query`, executable hashes and running-kernel evidence.
6. Confirm no GPIO/serial backend, remote-access policy, installation, HIL, safety credit or energization authority is implied.

Everything remains **PRELIMINARY - NOT APPROVED FOR IMAGING, INSTALLATION, CONNECTION, POWERED TEST, MOTION, OR ENERGIZATION**.
