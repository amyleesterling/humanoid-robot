"""Fail-closed validation for HR-V0-EVAL-ACQ-P0.1."""

from __future__ import annotations

import csv
import json
import sys
import xml.etree.ElementTree as ET
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "procurement" / "hr-v0" / "evaluation-acquisition-p0.1"
FORM = ROOT / "tests" / "forms" / "hr-v0-evaluation-acquisition-authorization-template.csv"
PROVIDER_FORM = ROOT / "tests" / "forms" / "hr-v0-metrology-provider-response-template.csv"
REVISION = "HR-V0-EVAL-ACQ-P0.1"
EXPECTED = {"HR-V0_evaluation-acquisition-guide.html", "HR-V0_evaluation-acquisition.svg", "UNSENT-metrology-rfq-draft.md", "cost-snapshot.csv", "decision-hold-register.csv", "metrology-rfq-question-register.csv", "package-status.json", "provider-capability-register.csv", "purchase-authorization-register.csv", "source-register.csv"}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    errors: list[str] = []
    if not OUT.is_dir() or {p.name for p in OUT.iterdir() if p.is_file()} != EXPECTED:
        errors.append("artifact directory is absent or membership changed")
    if not FORM.is_file() or not PROVIDER_FORM.is_file():
        errors.append("authorization or provider-response template is absent")
    if not errors:
        costs = rows(OUT / "cost-snapshot.csv")
        auth = rows(OUT / "purchase-authorization-register.csv")
        providers = rows(OUT / "provider-capability-register.csv")
        questions = rows(OUT / "metrology-rfq-question-register.csv")
        holds = rows(OUT / "decision-hold-register.csv")
        sources = rows(OUT / "source-register.csv")
        form = rows(FORM)
        provider_form = rows(PROVIDER_FORM)
        status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
        expected_costs = [("EAC-001", "902-0137-000", "2", "482.89", "965.78"), ("EAC-002", "903-0270-300", "2", "76.71", "153.42"), ("EAC-003", "903-0269-300", "2", "31.51", "63.02")]
        actual_costs = [(r["cost_id"], r["order_code"].replace("SKU ", ""), r["quantity"], r["unit_web_price_usd"], r["extended_web_price_usd"]) for r in costs]
        if actual_costs != expected_costs:
            errors.append("exact cost snapshot changed")
        if sum(Decimal(r["extended_web_price_usd"]) for r in costs) != Decimal("1182.22"):
            errors.append("web-price subtotal changed")
        if any("NOT VERIFIED" not in r["availability_boundary"] or "excluded" not in r["price_boundary"] for r in costs):
            errors.append("price/availability boundary weakened")
        if len(auth) != 3 or any(r["program_owner_decision"] != "NOT AUTHORIZED" or r["maximum_authorized_usd"] != "NOT AUTHORIZED" for r in auth):
            errors.append("purchase authorization was promoted")
        if len(providers) != 4 or any(r["research_state"] != "RESEARCH CANDIDATE - NOT CONTACTED" or r["selection_state"] != "NOT SELECTED" for r in providers):
            errors.append("provider research/selection state changed")
        if "accredited scope" not in providers[0]["qualification_boundary"] or "resolution is not measurement uncertainty" not in providers[1]["qualification_boundary"] or "ISO 9001 is not an ISO/IEC 17025" not in providers[2]["qualification_boundary"] or not providers[3]["candidate_role"].startswith("FIXTURE/TRAINING"):
            errors.append("provider qualification boundaries changed")
        if len(questions) != 24 or [r["question_id"] for r in questions] != [f"EAR-{i:03d}" for i in range(1, 25)] or any(r["state"] != "OPEN" or r["provider_response"] != "REQUIRED - NOT RECEIVED" for r in questions):
            errors.append("24-question RFQ register changed or was promoted")
        if len(holds) != 10 or any(r["state"] != "OPEN" for r in holds):
            errors.append("ten open decision holds changed")
        if len(sources) != 8 or any(not r["revision_or_access"].endswith("2026-08-08") for r in sources):
            errors.append("source register changed")
        if len(form) != 1 or form[0].get("decision") != "NOT AUTHORIZED" or len(provider_form) != 1 or provider_form[0].get("response_id") != "NOT-RECEIVED":
            errors.append("authorization/provider template was promoted")
        expected_status = {"revision": REVISION, "cost_line_count": 3, "physical_article_count": 6, "web_price_subtotal_usd": "1182.22", "shipping_tax_fees_included": False, "provider_candidate_count": 4, "provider_selected": False, "provider_contacted": False, "rfq_question_count": 24, "decision_hold_count": 10, "purchase_authorized": False, "order_placed": False, "physical_evidence_received": False, "warning": "PRELIMINARY - QUOTE AND AUTHORIZATION PACKET ONLY - NO ORDER, ASSEMBLY, MOTION OR ENERGIZATION RELEASE"}
        if status != expected_status:
            errors.append("package status or authorization boundary changed")
        draft = (OUT / "UNSENT-metrology-rfq-draft.md").read_text(encoding="utf-8")
        if "UNSENT - PROVIDER NOT SELECTED - NO WORK AUTHORIZATION" not in draft or "This request is not an order" not in draft:
            errors.append("unsent draft boundary changed")
        try:
            root = ET.parse(OUT / "HR-V0_evaluation-acquisition.svg").getroot()
            text = " ".join(n.text or "" for n in root.iter() if n.tag.endswith("text"))
            for token in (REVISION, "$1,182.22", "All four remain NOT CONTACTED and NOT SELECTED", "No order button exists"):
                if token not in text:
                    errors.append(f"SVG omits {token}")
            style = " ".join(n.text or "" for n in root.iter() if n.tag.endswith("style"))
            if "font-size:18px" not in style or "font-size:36px" not in style:
                errors.append("SVG legibility controls changed")
        except ET.ParseError as exc:
            errors.append(f"SVG does not parse: {exc}")
        html = (OUT / "HR-V0_evaluation-acquisition-guide.html").read_text(encoding="utf-8")
        for token in (REVISION, "$1,182.22", "font:clamp(16px", "data-filter=\"PRIMARY\"", "No checkout, contact or work authorization has occurred"):
            if token not in html:
                errors.append(f"HTML omits {token}")
    if errors:
        print(f"{REVISION} validation: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"{REVISION} validation: PASS")
    print("6 exact articles; $1,182.22 web subtotal before extras; 4 uncontacted candidates; 24 unanswered questions; 10 open holds")
    print("PRELIMINARY - QUOTE AND AUTHORIZATION PACKET ONLY - NO ORDER, ASSEMBLY, MOTION OR ENERGIZATION RELEASE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
