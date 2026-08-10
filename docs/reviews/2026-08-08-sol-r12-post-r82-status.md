# Sol R12 findings rechecked after R82

> **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION.**

Sol's supplied 18 BLOCKER / 30 MAJOR / 8 MINOR verdict remains independent review round R12 against the historical pre-correction baseline. The newly supplied summary is the same R12 analysis and is not counted again at R82.

R82 closes one configuration defect, not a physical gate. The current schematic no longer invents an installed watchdog debug connector or leaves the Pi heartbeat terminal unnamed. It binds Pi BCM GPIO17 to physical header pin 11, physical pin 6 to the compute return, and limits debug access to exact TP15/TP16/TP2 test points already present on PCB-P0.5.

Sol's buildability and energization verdict does not change. Exact heartbeat cable/contact/housing, GPIO runtime and software image, boot/shutdown/brownout waveform, timing/HIL, programmer, unpowered debug fixture, no-back-power proof, EMC/retention, received hardware, installed access and qualified review remain absent. The entire path retains zero functional-safety credit.

Mechanical definition, stopping behavior, power-loss behavior, mass/inertia closure, actuator continuous torque/thermal evidence, guard/restraint dynamics, protection, grounding, physical panel/harness/PCB evidence and HR-30 walking evidence remain open. R82 is a project-owned correction pass, not an independent approval, physical verification, fabrication release or energization release.
