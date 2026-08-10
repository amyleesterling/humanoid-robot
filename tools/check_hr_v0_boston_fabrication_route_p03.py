#!/usr/bin/env python3
"""Fail-closed checks for HR-V0-BOSTON-FAB-ROUTE-P0.3 / R167."""
from __future__ import annotations
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "release" / "hr-v0" / "boston-fabrication-route-p0.3"
WARNING = "PRELIMINARY - NOT APPROVED FOR QUOTATION FABRICATION OR ENERGIZATION"

def rows(name: str) -> list[dict[str, str]]:
    with (PKG / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))

def main() -> None:
    failures: list[str] = []
    def require(value: bool, message: str) -> None:
        if not value: failures.append(message)
    routes, sources, inputs = rows("route-comparison.csv"), rows("source-register.csv"), rows("open-design-inputs.csv")
    status = json.loads((PKG / "package-status.json").read_text(encoding="utf-8"))
    guide = (PKG / "index.html").read_text(encoding="utf-8")
    doc = (ROOT / "docs" / "hr-v0-boston-fabrication-decision-p0.3.md").read_text(encoding="utf-8")
    require(len(routes) == 10, "route register must contain 10 records")
    require(len(sources) == 10, "source register must contain 10 official records")
    require(len(inputs) == 10, "open input register must contain 10 records")
    require(all(r["warning"] == WARNING for r in routes + sources + inputs), "warning changed")
    require({r["route_id"] for r in routes} == {"BOS-K4D","ONLINE-PROTOLABS","ONLINE-XOMETRY","ONLINE-FICTIV","BOS-ACCURATE","BOS-TD","BOS-TUCKER","NE-UPM","ONLINE-SCS","ONLINE-EMS"}, "route identity set changed")
    require("6061-T651" in routes[0]["explicit_unknowns"], "local T651 hold missing")
    require("6061-T651" in next(r for r in routes if r["route_id"] == "ONLINE-PROTOLABS")["process_material_thickness_evidence"], "Protolabs T651 evidence missing")
    require(all(r["state"] in {"SELECTION REQUIRED","OPEN","NOT AUTHORIZED"} for r in inputs), "an input was falsely closed")
    for key in ("qualified_provider_selected","supplier_contacted","files_uploaded","quote_requested","fabrication_authorized","energization_authorized"):
        require(status.get(key) is False, f"{key} must remain false")
    combined = guide + doc
    for token in ("Kontrast4D","Protolabs","Xometry","6061‑T651","C06/C07","not authorize","R167"):
        require(token.lower() in combined.lower(), f"missing controlled token {token}")
    require("font:16px" in guide and "font-size:14px" in guide, "guide text floors missing")
    require("data-filter=\"local\"" in guide and "data-filter=\"online\"" in guide, "interactive filters missing")
    if failures: raise SystemExit("HR-V0 Boston fabrication route P0.3 check failed:\n- " + "\n- ".join(failures))
    print("HR-V0 Boston fabrication route P0.3 check passed: 10 routes, 10 official sources, 10 open design inputs")
    print("No provider is selected or qualified; no contact, upload, quote, fabrication, assembly, motion, or energization is authorized")
    print(WARNING)

if __name__ == "__main__": main()
