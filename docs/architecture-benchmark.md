# Sub-Meter Humanoid Architecture Benchmark

This benchmark establishes feasibility context; it is not a license to copy dimensions or assume equivalent safety.

| Platform | Published scale | Published mass | DOF | Relevance to HR-30 |
|---|---:|---:|---:|---|
| ROBOTIS OP3 | about 510 mm | about 3.5 kg without skin | 20 | Demonstrates an integrated small humanoid using XM430-W350 actuators, current-based control, an IMU, and a subordinate real-time controller. HR-30 is roughly 1.49× taller, so loads cannot be scaled by height alone. |
| Poppy Humanoid | sub-meter educational humanoid | configuration-dependent | 25 | Demonstrates a printable 25-axis body split across legs, torso, arms, and head. Its documented MX/AX-era BOM is architecture reference only; obsolete parts are not copied into HR-30 procurement. |

HR-30 deliberately differs from both references by starting with a fixed pedestal, external actuator power, independent hardware energy isolation, a 100 g human-facing payload, and explicit fall restraint before any leg power.

Primary references:

- https://emanual.robotis.com/docs/en/platform/op3/introduction/
- https://docs.poppy-project.org/en/getting-started/
- https://docs.poppy-project.org/en/assembly-guides/poppy-humanoid/
