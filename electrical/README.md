# Electrical release area

The independently reviewed preliminary native ECAD is stored at [`kicad/project-button-v2/`](kicad/project-button-v2/). A separate connected correction candidate is stored at [`kicad/project-button-v3/`](kicad/project-button-v3/).

Current electrical identifier: **Project Button Electrical V2.1**  
Native tool: **KiCad 10.0.5**  
Status: **PRELIMINARY—NOT APPROVED FOR ENERGIZATION**

The directory contains the root `.kicad_pro`, root and 14 child `.kicad_sch` sheets, project symbol library, schedules, BOM, unresolved-selection register, primary-source register, native validation outputs, and synchronized review exports. `SOURCE-MANIFEST.csv` records the authoritative file hashes.

This is connected preliminary ECAD, not a build release. Clean ERC establishes modeled connectivity and annotation only. Exact physical selections, pinouts, ratings, protection coordination, conductor sizing, enclosure/panel design, functional-safety analysis, firmware, and physical fault tests remain unresolved. Do not fabricate, wire, or energize from this package.

## Electrical V3-P0.1 correction candidate

V3 is a generated native KiCad candidate that addresses the V2.1 automatic-restart blocker and removes project-built mains wiring from the proposed HR-V0 architecture. It has one index and nine child sheets, separate RESET and ARM stages, two PNOZ s4 devices, two watchdog-contact channels, explicit K1/K2 mirror contacts and series power poles, external adapters, separately protected actuator branches, and VDD-isolating data/power injection modules.

Current generated counts are 41 component blocks, 198 modeled terminals, 76 native nets (53 named connected nets plus 23 deliberate auto-generated unconnected nets), 175 unique wire labels, 29 unresolved component/interface rows, and 85 deliberately unresolved `TBD-*` terminal designations. KiCad 10.0.5 ERC reports 0 errors and 0 warnings; native netlist, ten-page PDF, and ten SVG exports succeed. Run:

```powershell
python tools/generate_hr_v0_electrical_v3.py --validate
python tools/check_hr_v0_electrical_v3.py
```

V3 remains **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**. It has not yet received the independent review or physical evidence required to supersede V2.1.
