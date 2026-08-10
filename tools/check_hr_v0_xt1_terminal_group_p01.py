#!/usr/bin/env python3
"""Fail-closed checks for HR-V0-XT1-P0.1 / R168."""
from __future__ import annotations
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "electrical" / "panel" / "hr-v0-xt1-terminal-group-p0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR WIRING OR ENERGIZATION"

def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle: return list(csv.DictReader(handle))

def main() -> None:
    failures: list[str] = []
    def need(value: bool, message: str) -> None:
        if not value: failures.append(message)
    pos, acc, src, holds = [rows(PKG / name) for name in ("terminal-position-register.csv","accessory-allocation.csv","source-register.csv","open-holds.csv")]
    status = json.loads((PKG / "package-status.json").read_text(encoding="utf-8"))
    panel = rows(ROOT / "electrical" / "panel" / "hr-v0-control-panel-p0.6" / "panel-bom.csv")
    e2 = rows(ROOT / "electrical" / "e2" / "hr-v0-e2-hardware-p0.4" / "e2-terminal-register.csv")
    alloc = rows(ROOT / "electrical" / "panel" / "hr-v0-control-panel-p0.2" / "terminal-allocation.csv")
    bom = {r["item_id"]:r for r in rows(ROOT / "bom" / "bom.csv")}
    closure = {r["item_id"]:r for r in rows(ROOT / "bom" / "hr-v0-bom-closure.csv")}
    gates = {r["gate_id"]:r for r in rows(ROOT / "requirements" / "hr-v0-energization-gates.csv")}
    supplement = {r["gate_id"]:r for r in rows(ROOT / "requirements" / "hr-v0-gate-evidence-supplement-r168.csv")}
    guide = (ROOT / "release" / "hr-v0" / "xt1-terminal-group-p0.1" / "index.html").read_text(encoding="utf-8")
    doc = (ROOT / "docs" / "hr-v0-xt1-terminal-group-p0.1.md").read_text(encoding="utf-8")
    expected = {
      "XT1-01":("SAFETY_24V","3209510","gray"),"XT1-02":("SAFETY_0V","3209523","blue"),
      "XT1-03":("SR1_STATUS","3209510","gray"),"XT1-04":("SRA1_STATUS","3209510","gray"),
      "XT1-05":("K1_STATUS","3209510","gray"),"XT1-06":("K2_STATUS","3209510","gray")}
    need(len(pos)==6 and {r["position"] for r in pos}==set(expected), "position set changed")
    for r in pos:
        need((r["net"],r["item_number"],r["color"])==expected[r["position"]], f"{r['position']} mapping changed")
        need(r["bridge_state"]=="NO BRIDGE" and r["warning"]==WARNING, f"{r['position']} bridge/warning changed")
        need(r["published_width_mm"]=="5.2" and r["published_strip_length_mm"]=="8..10", f"{r['position']} source dimensions changed")
    e2map={r["terminal"]:(r["net"],r["catalog_body"]) for r in e2}
    allocmap={r["position"]:(r["net"],r["manufacturer_part_number"],r["bridge_state"]) for r in alloc}
    for p,(net,item,color) in expected.items():
        need(e2map.get(p)==(net,f"{item} {color}"), f"{p} E2 parity changed")
        need(allocmap.get(p)==(net,item,"NO BRIDGE"), f"{p} panel allocation parity changed")
    need(len(acc)==4 and {r["item_number"] for r in acc}=={"3030417","3022218","0828734","NO JUMPER"}, "accessory allocation changed")
    need(next(r for r in acc if r["item_number"]=="3022218")["bom_owner"]=="BOM-085", "CLIPFIX duplicate ownership")
    need(next(r for r in acc if r["item_number"]=="0828734")["bom_owner"]=="BOM-062", "marker duplicate ownership")
    need(len(src)==5 and all(r["manufacturer"]=="Phoenix Contact" and r["url"].startswith("https://www.phoenixcontact.com/") for r in src), "source register changed")
    need(len(holds)==12 and all(r["authorization"]=="NOT AUTHORIZED" and r["state"] in {"OPEN","SELECTION REQUIRED","NOT EXECUTED"} for r in holds), "hold state weakened")
    b=bom.get("BOM-039",{}); c=closure.get("BOM-039",{})
    need(b.get("manufacturer")=="Phoenix Contact" and "3209510 x5" in b.get("manufacturer_part_number","") and "3209523 x1" in b.get("manufacturer_part_number","") and "3030417 x1" in b.get("manufacturer_part_number","") and "NO JUMPERS" in b.get("manufacturer_part_number","") and b.get("baseline_status")=="exact_candidate_hold", "BOM-039 identity/state changed")
    need(c.get("closure_class")=="exact_candidate_hold" and c.get("allowed_action")=="HOLD", "BOM-039 closure weakened")
    need(bom.get("BOM-085",{}).get("manufacturer_part_number")=="CLIPFIX 35; item 3022218" and bom.get("BOM-085",{}).get("quantity")=="6", "shared CLIPFIX stock changed")
    need(bom.get("BOM-062",{}).get("baseline_status") in {"selection_required","design_required"}, "label group was falsely closed")
    for gate in ("EG-003","EG-015"):
        need(gates.get(gate,{}).get("status")=="partial", f"{gate} must remain partial")
        need(supplement.get(gate,{}).get("package_id")=="HR-V0-XT1-P0.1" and supplement.get(gate,{}).get("status_effect")=="REMAINS PARTIAL" and "check_hr_v0_xt1_terminal_group_p01.py" in supplement.get(gate,{}).get("evidence_locations",""), f"{gate} supplement missing or weakened")
    for key in ("procurement_authorized","assembly_authorized","wiring_authorized","energization_authorized","safety_credit_claimed"):
        need(status.get(key) is False, f"{key} must remain false")
    combined=guide+doc
    for token in ("HR-V0-XT1-P0.1","3209510","3209523","3030417","NO BRIDGE","BOM-085","BOM-062","not a project rating","EG-015"):
        need(token.lower() in combined.lower(), f"missing controlled token {token}")
    need("font:16px" in guide and "font-size:14px" in guide and "data-filter=\"power\"" in guide and "data-filter=\"status\"" in guide, "guide legibility/filter controls missing")
    if failures: raise SystemExit("HR-V0 XT1 P0.1 check failed:\n- " + "\n- ".join(failures))
    print("HR-V0 XT1 P0.1 check passed: six exact positions, five gray plus one blue body, one end cover, zero jumpers, twelve open holds")
    print("BOM-039 remains an exact-candidate HOLD; conductors, terminations, labels, physical evidence, qualified review and every work authority remain open")
    print(WARNING)

if __name__ == "__main__": main()
