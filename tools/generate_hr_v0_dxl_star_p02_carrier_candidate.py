"""Generate DXL-STAR-P0.2 carrier-integrated native KiCad candidate."""

from __future__ import annotations

from pathlib import Path
import sys
import types


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "tools" / "generate_hr_v0_dxl_star.py"


def once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one source match, found {count}")
    return text.replace(old, new, 1)


def transformed_source() -> str:
    text = BASE.read_text(encoding="utf-8-sig")
    text = once(text, 'OUT = ROOT / "electrical" / "kicad" / "hr-v0-dxl-star"', 'OUT = ROOT / "electrical" / "kicad" / "hr-v0-dxl-star-p0.2-carrier-candidate"', "output path")
    text = once(text, 'PROJECT = "hr-v0-dxl-star"', 'PROJECT = "hr-v0-dxl-star-p0.2-carrier-candidate"', "project name")
    text = once(text, 'REV = "DXL-STAR-P0.1"', 'REV = "DXL-STAR-P0.2-CARRIER-CANDIDATE"', "revision")
    text = text.replace("DXL-STAR-P0.1", "DXL-STAR-P0.2-CARRIER-CANDIDATE")
    for axis in (1, 2, 3):
        text = text.replace(f"J{axis}_VDD", f"J{axis}_LIMITED_VDD")
    text = text.replace('f"J{index}_VDD"', 'f"J{index}_LIMITED_VDD"')
    text = text.replace("protected branch", "post-limiter branch")
    text = text.replace("protected positive rails", "post-limiter positive rails")
    text = text.replace("No fabrication outputs were generated", "No supplier-release fabrication archive was generated")
    return text


def main() -> int:
    name = "carrier_integrated_dxl_star_generator"
    module = types.ModuleType(name)
    module.__file__ = str(BASE)
    sys.modules[name] = module
    exec(compile(transformed_source(), str(BASE), "exec"), module.__dict__)
    return int(module.main())


if __name__ == "__main__":
    raise SystemExit(main())
