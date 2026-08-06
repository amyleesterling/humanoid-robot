"""Reproducible HR-V0 preliminary structural screens.

PRELIMINARY—NOT A STRUCTURAL RELEASE.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


OUT = Path(__file__).resolve().parents[1] / "generated" / "mechanical-checks.json"


def main():
    # Controlled preliminary inputs, N and mm.
    proof_moment = 3.83e3 * 3.0
    link_length = 160.0
    link_depth = 44.0
    plate_t = 4.75
    hole_d = 2.70
    e_al = 69_000.0
    yield_al = 240.0  # minimum screening value only; certify supplied stock
    bolt_circle_r = 11.0
    column_i = 13.787 * 10_000.0  # 80/20 40-4040 published 13.787 cm^4
    column_l = 500.0
    anchor_spacing = 420.0

    gross_i = plate_t * link_depth ** 3 / 12.0
    net_depth = link_depth - 2.0 * hole_d
    net_i = plate_t * net_depth ** 3 / 12.0
    eq_end_force = proof_moment / link_length
    results = {
        "status": "PRELIMINARY—NOT A STRUCTURAL OR FABRICATION RELEASE",
        "inputs": {
            "proof_moment_Nmm": proof_moment,
            "basis": "3.83 N·m intermittent shoulder screen times project 3.0 proof factor",
            "6061_yield_screen_MPa": yield_al,
            "link_mm": [link_length, link_depth, plate_t],
            "candidate_hole_d_mm": hole_d,
            "column_I_mm4": column_i,
        },
        "screens": {
            "link_gross_I_mm4": gross_i,
            "link_net_I_mm4_conservative_two_holes": net_i,
            "link_net_bending_stress_MPa": proof_moment * (net_depth / 2.0) / net_i,
            "link_yield_ratio_on_screen": yield_al / (proof_moment * (net_depth / 2.0) / net_i),
            "link_cantilever_deflection_mm": eq_end_force * link_length ** 3 / (3.0 * e_al * gross_i),
            "conservative_two_bolt_force_each_N": proof_moment / (2.0 * bolt_circle_r),
            "candidate_plate_bearing_stress_MPa": (proof_moment / (2.0 * bolt_circle_r)) / (plate_t * 2.5),
            "column_tip_deflection_pure_moment_mm": proof_moment * column_l ** 2 / (2.0 * e_al * column_i),
            "minimum_anchor_couple_force_each_N": proof_moment / anchor_spacing,
        },
        "not_credited_or_unresolved": [
            "Actual alloy/temper certificate, thickness tolerance, flatness and finish",
            "ROBOTIS frame material, measured mass, permissible load and fatigue behavior",
            "Exact M2.5 and M8 fastener part, grade, engagement, preload, torque and locking",
            "Joint backlash, alignment, combined load, shock, fatigue and hard-stop impact",
            "Bench substrate, anchor part, edge distance, pull-out, shear and site permission",
            "Guard and receiver-fixture impact/retention",
            "Correlation to measured first article and independent mechanical review",
        ],
        "calculation_result": "GEOMETRY SCREEN PASSES; RELEASE REMAINS OPEN",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()

