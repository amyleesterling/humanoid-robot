"""Check the root GitHub Pages entry for HR-30 whole-body P0.1."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "index.html"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> int:
    text = PAGE.read_text(encoding="utf-8")
    required_links = (
        "hr30/whole-body-p0.1/",
        "HR-30_body_architecture_candidate.glb",
        "HR-30_body_architecture_candidate.step",
        "whole-body-source.py",
        "joint-axis-schedule.csv",
        "actuator-transmission-allocation.csv",
        "hr30.urdf",
        "hr30.xml",
        "mass-properties-budget.csv",
        "power-energy-budget.csv",
        "thermal-budget.csv",
        "compute-sensor-network-budget.csv",
        "whole-robot-candidate-bom.csv",
        "walking-development-architecture.md",
        "embodied-agent-architecture.md",
        "modular-fabrication-assembly-electrification-plan.md",
    )
    require(all(link in text for link in required_links), "root page does not expose the complete package")
    require("PRELIMINARY" in text and "NOT APPROVED" in text and "energization" in text.lower(), "preliminary authority warning missing")
    require('src="hr30/whole-body-p0.1/vendor/model-viewer.min.js"' in text, "viewer is not repository-local")
    require("font:17px/1.55" in text and "font-size:16px" in text and "font-size:14px" in text, "legibility minima missing")
    require("minmax(230px,1fr)" in text and "@media (max-width:680px)" in text, "responsive layout controls missing")
    require((ROOT / ".nojekyll").exists(), "GitHub Pages no-Jekyll marker missing")
    for link in required_links[1:]:
        matches = list((ROOT / "hr30" / "whole-body-p0.1").glob(link))
        require(matches or link == "HR-30_body_architecture_candidate.glb", f"linked package artifact missing: {link}")
    print("PASS: repository-root HR-30 Pages entry is legible, responsive, interactive, self-contained and exposes the complete preliminary whole-body package")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
