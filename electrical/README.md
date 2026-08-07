# Electrical release area

The independently reviewed preliminary native ECAD is stored at [`kicad/project-button-v2/`](kicad/project-button-v2/). A separate connected correction candidate is stored at [`kicad/project-button-v3/`](kicad/project-button-v3/).

Current electrical identifier: **Project Button Electrical V2.1**  
Native tool: **KiCad 10.0.5**  
Status: **PRELIMINARY—NOT APPROVED FOR ENERGIZATION**

The directory contains the root `.kicad_pro`, root and 14 child `.kicad_sch` sheets, project symbol library, schedules, BOM, unresolved-selection register, primary-source register, native validation outputs, and synchronized review exports. `SOURCE-MANIFEST.csv` records the authoritative file hashes.

This is connected preliminary ECAD, not a build release. Clean ERC establishes modeled connectivity and annotation only. Exact physical selections, pinouts, ratings, protection coordination, conductor sizing, released enclosure/panel drawings, functional-safety analysis, firmware, and physical fault tests remain unresolved. Do not fabricate, wire, or energize from this package. R62's separate [`panel/hr-v0-control-panel-p0.2/`](panel/hr-v0-control-panel-p0.2/) directory corrects the impossible P0.1 protection reserve and is tied to V3 wire numbers; it releases no drilling, cutting, wiring, assembly, or energization work.

## Electrical V3-P1.6 correction candidate

V3 is a generated native KiCad candidate that addresses the V2.1 automatic-restart blocker and removes project-built mains wiring from the proposed HR-V0 architecture. It has one index and twelve child sheets, separate RESET and ARM stages, two PNOZ s4 devices, two watchdog-contact channels, an explicit calculated ISO1212DBQ feedback sheet, K1/K2 mirror contacts and series power poles, external adapters, separately protected actuator branches, and one exact central DYNAMIXEL star-injection board boundary.

Current generated counts are 76 component blocks, 295 modeled terminals, 100 native nets (64 named connected nets plus 36 deliberate auto-generated unconnected nets), 259 unique wire labels, 63 unresolved component/interface rows, and 24 deliberately unresolved `TBD-*` terminal designations. P1.2 replaced three undefined inline injection modules with one exact 18-terminal `INJ1` representation synchronized to the separate native `DXL-STAR-P0.1` project; P1.3 corrected the K1/K2 application record; P1.4 retains received-lot terminal control for RESET and ARM without inventing four terminal marks; P1.5 freezes exact amber H1 while replacing misleading `SAFE ELIGIBLE` and `+/-` labels with diagnostic-only wording and `TBD-HA/TBD-HB` project placeholders. U2D2 VDD is omitted; three actuator-positive rails remain isolated; common TTL data and return are explicit. The routed star board passes native ERC/DRC 0/0, but fabrication, harness, protection, connector-current, thermal, waveform, no-backfeed, received H1 evidence and qualified review remain open. KiCad 10.0.5 ERC reports 0 errors and 0 warnings; native netlist, thirteen-page PDF, and thirteen SVG exports succeed. Run:

```powershell
python tools/generate_hr_v0_electrical_v3.py --validate
python tools/check_hr_v0_electrical_v3.py
python tools/check_hr_v0_control_panel.py
"C:\Program Files\KiCad\10.0\bin\python.exe" tools/generate_hr_v0_dxl_star.py
"C:\Program Files\KiCad\10.0\bin\python.exe" tools/check_hr_v0_dxl_star.py
```

V3 remains **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**. It has not yet received the independent review or physical evidence required to supersede V2.1.

The separate star-board source and synchronized review outputs are at [`kicad/hr-v0-dxl-star/`](kicad/hr-v0-dxl-star/). No Gerber, drill, placement, or assembly outputs are released.
