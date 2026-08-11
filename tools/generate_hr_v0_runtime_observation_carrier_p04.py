#!/usr/bin/env python3
"""Generate R210/P0.4 source-audited buffered observation carrier.

P0.4 preserves P0.3's four-channel architecture but corrects the DBV0005A
land geometry to TI drawing 4214839/K and adds temperature allowance to the
two fault-current screens. It grants no work or safety authority.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
P03_TOOL = ROOT / "tools/generate_hr_v0_runtime_observation_carrier_p03.py"
ECAD = ROOT / "electrical/kicad/hr-v0-runtime-observation-carrier-p0.4"
WEB = ROOT / "release/hr-v0/runtime-observation-carrier-p0.4"
DOC = ROOT / "docs/hr-v0-runtime-observation-carrier-p0.4.md"
PROJECT = "hr-v0-runtime-observation-carrier-p0.4"
IDENTIFIER = "HR-V0-RUNTIME-OBS-CARRIER-P0.4"
REV = "R210 / P0.4 / PCB-P0.3"
DATE = "2026-08-10"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def load_p03():
    spec = importlib.util.spec_from_file_location("obs_p03_for_p04", P03_TOOL)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {P03_TOOL}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def exact_dbv_land(p03, legacy) -> pcbnew.FOOTPRINT:
    fp = pcbnew.FOOTPRINT(None)
    fp.SetFPID(pcbnew.LIB_ID(p03.LIB_NAME, p03.BUFFER_FOOTPRINT))
    fp.SetValue(p03.BUFFER_FOOTPRINT)
    # TI 4214839/K, 08/2024: 5 x 1.10 by 0.60 mm, 0.95 mm pitch,
    # 1.90 mm span along each row and 2.60 mm between row centers.
    for number, x, y in (("1", -1.30, -0.95), ("2", -1.30, 0.0), ("3", -1.30, 0.95), ("4", 1.30, 0.95), ("5", 1.30, -0.95)):
        legacy.add_smd_pad(fp, number, x, y, 1.10, 0.60, 0.07)
    legacy.add_outline(fp, -1.75, -1.45, 1.75, 1.45)
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
    return fp


def configure(p03) -> None:
    p03.ECAD = ECAD
    p03.WEB = WEB
    p03.DOC = DOC
    p03.PROJECT = PROJECT
    p03.IDENTIFIER = IDENTIFIER
    p03.REV = REV
    p03.DATE = DATE
    p03.LIB_NAME = "PB_RUNTIME_OBS_P04"
    p03.LIB_DIR = ECAD / "PB_RUNTIME_OBS_P04.pretty"
    p03.RGP_VALUE = "39.0 kohm 1% 0.125 W 0805"
    p03.RGP_MPN = "Panasonic ERJ6ENF3902V"
    p03.NEW_SOURCES = [
        row for row in p03.NEW_SOURCES if row[0] != "OBS3-SRC-020"
    ] + [
        ("OBS4-SRC-020", "Panasonic Industry", "ERJ6ENF3902V product record", "39.0 kohm 1% 0805; TCR +/-100 ppm/K", "rechecked 2026-08-10", "https://industrial.panasonic.com/ww/products/pt/general-purpose-chip-resistors/models/ERJ6ENF3902V", "Exact GPIO-path series candidate; tolerance and TCR included in R210 screens"),
        ("OBS4-SRC-022", "Texas Instruments", "DBV0005A package drawing and board-layout example", "4214839/K", "2024-08; rechecked 2026-08-10", "https://www.ti.com/lit/ds/symlink/sn74lvc1g125.pdf", "Controls five 1.10 x 0.60 mm lands, 0.95 mm pitch, 1.90 mm row span and 2.60 mm row-center spacing"),
    ]
    p03.HOLDS = [
        (hold_id, scope, evidence.replace("updated DBV-5/0805 lands", "TI 4214839/K DBV-5 and Panasonic 0805 lands"))
        for hold_id, scope, evidence in p03.HOLDS
    ]
    p03.LOADS = [
        ("OBS4-LOAD-001", "PI_3V3_CANDIDATE", "two ISO1212 logic sides", "2 x 1.9 mA maximum ICC1", "3.800 mA", "TI ISO1212 bound", "SCREEN ONLY"),
        ("OBS4-LOAD-002", "PI_3V3_CANDIDATE", "four SN74LVC1G125 static supplies", "4 x 10 uA maximum ICC", "0.040 mA", "does not include delta-ICC", "SCREEN ONLY"),
        ("OBS4-LOAD-003", "PI_3V3_CANDIDATE", "four LVC inputs near VCC-0.6", "4 x 0.5 mA maximum delta-ICC row", "2.000 mA", "conservative simultaneous-high screen", "SELECTION/MEASUREMENT REQUIRED"),
        ("OBS4-LOAD-004", "PI_3V3_CANDIDATE", "four 47k input pulldown paths", "4 x 3.6 V/(1.47015k+46.0647k)", "0.303 mA", "1% tolerance plus +/-100 ppm/K over -40..125 C", "SCREEN ONLY"),
        ("OBS4-LOAD-005", "PI_3V3_CANDIDATE", "four 330k output pulldown paths", "4 x 3.6 V/(38.2239k+323.433k)", "0.040 mA", "1% tolerance plus +/-100 ppm/K over -40..125 C", "SCREEN ONLY"),
        ("OBS4-LOAD-006", "PI_3V3_CANDIDATE", "combined steady worst-case screen", "3.800 + 0.040 + 2.000 + 0.303 + 0.040", "6.183 mA", "not Pi 5 source approval; switching current absent", "SELECTION REQUIRED"),
    ]
    p03.make_sot23_5 = lambda legacy: exact_dbv_land(p03, legacy)


def write_corrected_docs(p03) -> None:
    DOC.write_text(f"""# HR-V0 source-audited buffered runtime-observation carrier {REV}

**{WARNING}**

R210 supersedes P0.3 for current review. The R209 electrical architecture is retained, but its project-owned DBV land pattern was not equal to TI drawing 4214839/K: R209 encoded 1.20 x 0.70 mm lands on 2.20 mm row spacing, while TI's current example specifies 1.10 x 0.60 mm lands on 2.60 mm row spacing. P0.4 corrects that native footprint and preserves the four independent `SN74LVC1G125DBVR` channels, connector numbering, field networks, board outline, mounting datums, planes and isolation corridor.

P0.4 also replaces the 36.5 kohm GPIO series candidate with exact Panasonic `ERJ6ENF3902V` 39.0 kohm. The R209 99.63 uA hard-short result left only 0.37 uA below TI's 100 uA output-level characterization point before temperature effects. R210 includes 1% resistance tolerance and +/-100 ppm/K over -40 to 125 C: the ISO-side short screen is 2.449 mA, the GPIO-side screen is 94.18 uA, the buffer-input HIGH floor is 2.516 V, the cable-side source-HIGH screen is 2.582 V, and the conservative steady 3V3 screen is 6.183 mA. These are analytical component screens, not Raspberry Pi acceptance.

Pi 5 header-source capability, RP1 GPIO thresholds/leakage/clamps, installed capacitance and timing, back-power, DFM, assembly, EMC, thermal, received-part, first-article, fault-injection and qualified-review evidence remain open. Every observation is an ordinary diagnostic with zero functional-safety credit. All fourteen holds remain open and no procurement, fabrication, connection, powered test, motion or energization is authorized.
""", encoding="utf-8")

    guide = WEB / "index.html"
    text = guide.read_text(encoding="utf-8")
    replacements = {
        "R209": "R210", "p0.3": "p0.4", "P0.3": "P0.4",
        "36.5 kohm": "39.0 kohm", "36.135 kohm": "38.2239 kohm",
        "36.865": "39.7839", "326.7": "323.433",
        "1.485 kohm": "1.47015 kohm", "46.53/(46.53+1.515)": "46.0647/(46.0647+1.53015)",
        "2.424 mA": "2.449 mA", "99.63 uA": "94.18 uA",
        "2.426 V": "2.582 V", "6.180 mA": "6.183 mA",
        "(3.0-0.3)": "(3.0-0.1)",
        "The ISO output no longer drives the cable directly.": "The buffer geometry and fault margins now match the controlled sources.",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    marker = '<p class="hold">Pi 5/RP1 DC limits'
    text = text.replace(marker, '<p class="hold">R209 used the wrong DBV land dimensions and is superseded. P0.4 uses TI 4214839/K: 1.10 x 0.60 mm lands on 2.60 mm row spacing.</p>' + marker)
    guide.write_text(text, encoding="utf-8")


def main() -> int:
    p03 = load_p03()
    configure(p03)
    legacy, base = p03.prepare_modules()
    p03.build_schematic(legacy, base)
    summary = p03.build_board(legacy)
    p03.run_native(summary)
    p03.write_docs_web(summary)
    write_corrected_docs(p03)
    p03.manifest()
    print(f"Generated {IDENTIFIER}: 5 native sheets / {summary['footprints']} footprints / {summary['track_segments']} tracks / {summary['vias']} vias")
    print("R209 land-pattern and narrow GPIO-current margins corrected in candidate; all holds remain open")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
