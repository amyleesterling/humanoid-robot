"""Check the root GitHub Pages entry for HR-30 whole-body P0.1."""

import json

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "index.html"
MASS_SUMMARY = ROOT / "hr30" / "whole-body-p0.1" / "mass-reconciliation-summary.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> int:
    text = PAGE.read_text(encoding="utf-8")
    mass_summary = json.loads(MASS_SUMMARY.read_text(encoding="utf-8"))
    reconciled_mass = float(mass_summary["reconciled_dynamics_planning_mass_kg"])
    displayed_mass = f"{reconciled_mass:.3f} kg"
    required_links = (
        "hr30/whole-body-p0.1/",
        "HR-30_body_architecture_candidate.glb",
        "HR-30_body_architecture_candidate.step",
        "whole-body-source.py",
        "joint-axis-schedule.csv",
        "actuator-transmission-allocation.csv",
        "joint-family-cad/index.html",
        "manufacturing-files/index.html",
        "grippers-p0.1/index.html",
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
    require(displayed_mass in text, f"root page mass is not synchronized to the authoritative reconciliation: {displayed_mass}")
    require("only 0.050 kg remains" in text, "narrow P0.1 mass margin is not visible on the root page")
    require("9.63 kg" not in text, "historical allocation mass remains on the current root page")
    require('src="hr30/whole-body-p0.1/vendor/model-viewer.min.js"' in text, "viewer is not repository-local")
    require('src="hr30/whole-body-p0.1/grippers-p0.1/HR-30_detailed_hands_installed_open_candidate.glb"' in text, "root viewer does not show the hand-integrated whole robot")
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
