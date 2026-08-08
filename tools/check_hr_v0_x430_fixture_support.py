from __future__ import annotations

import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "test-fixtures" / "hr-v0" / "x430-fixture-support-p0.1"
WEB = ROOT / "release" / "hr-v0" / "x430-fixture-support-p0.1"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    errors: list[str] = []
    required = ["HR-V0_X430_fixture_support_P0.1_review.step","HR-V0_X430_fixture_support_P0.1_review.glb","FX101-C01_40006-BP_central-machining-review.step","support-route-drawing.svg","topology-trade.csv","support-bom.csv","support-load-screen.csv","support-rfi.csv","open-hold-register.csv","source-register.csv","package-status.json"]
    errors.extend(f"missing {p}" for p in required if not (OUT/p).exists())
    if not (WEB/"index.html").exists(): errors.append("missing guide")
    if errors: raise SystemExit("\n".join(errors))

    trade=rows("topology-trade.csv")
    if len(trade)!=4 or trade[0]["disposition"]!="PREFERRED INQUIRY CANDIDATE - NOT SELECTED": errors.append("topology trade changed")
    if trade[2]["disposition"]!="REJECT FOR CATALOG TORQUE CREDIT" or trade[3]["disposition"]!="PROHIBITED AS PRIMARY SUPPORT": errors.append("unsafe support disposition changed")
    bom=rows("support-bom.csv")
    if len(bom)!=6 or any("SELECTED" not in r["state"] and "REQUIRED" not in r["state"] and "CANDIDATE" not in r["state"] for r in bom): errors.append("BOM selection boundary changed")
    screens=rows("support-load-screen.csv")
    if len(screens)!=4: errors.append("screen count changed")
    if not math.isclose(float(screens[0]["result"].split("=")[1]),2040/16.5,abs_tol=1e-6): errors.append("catalog ratio changed")
    if screens[1]["result"]!="0 N m ideal" or "DOES NOT REPLACE" not in screens[1]["authority"]: errors.append("vertical gravity boundary changed")
    if screens[3]["result"]!="4.613..5.675 mm": errors.append("fastener arithmetic changed")
    rfi=rows("support-rfi.csv")
    if len(rfi)!=8 or any(r["state"]!="NOT SENT" for r in rfi): errors.append("RFI state changed")
    holds=rows("open-hold-register.csv")
    if len(holds)!=10 or any(r["state"]!="OPEN" for r in holds): errors.append("hold state changed")
    sources=rows("source-register.csv")
    if len(sources)!=4 or sources[0]["record"]!="40200-SP-K static robotic pedestal": errors.append("source register changed")
    status=json.loads((OUT/"package-status.json").read_text(encoding="utf-8"))
    if status.get("identifier")!="HR-V0-X430-FIXTURE-SUP-P0.1" or status.get("preferred_route")!="SUP-A": errors.append("package identity changed")
    if status.get("pedestal_body_cad_present") is not False or status.get("horizontal_test_still_required") is not True: errors.append("evidence boundary changed")
    if status.get("rfi_state")!="NOT SENT" or status.get("open_hold_count")!=10: errors.append("status hold/RFI changed")
    if any(v is not False for v in status.get("release_flags",{}).values()): errors.append("release flag promoted")
    guide=(WEB/"index.html").read_text(encoding="utf-8")
    for phrase in ("A rated support route—with a floor-sized condition","Gravity torque about the vertical joint axis","font-size:13px","font-size:16px","All release flags remain false"):
        if phrase not in guide: errors.append(f"guide boundary missing: {phrase}")
    drawing=(OUT/"support-route-drawing.svg").read_text(encoding="utf-8")
    for phrase in ("max-width:100%;height:auto","DO NOT MACHINE OR ANCHOR FROM THIS DRAWING","centerline is not pedestal body CAD"):
        if phrase not in drawing: errors.append(f"drawing boundary missing: {phrase}")
    if errors: raise SystemExit("HR-V0 X430 fixture support check FAILED:\n- "+"\n- ".join(errors))
    print("HR-V0 X430 fixture support check: PASS")
    print("4 routes; 6 BOM rows; 4 screens; 8 unsent RFIs; 10 open holds")
    print("pedestal body CAD absent; horizontal test required; all release flags false")

if __name__=="__main__": main()
