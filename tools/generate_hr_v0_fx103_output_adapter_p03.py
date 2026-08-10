"""Generate the R107 FX103 output-adapter P0.3 correction candidate.

R107 corrects a second R106 buildability defect: the 2.20 mm counterbore
left 5.80 mm of flange grip, so the HN12 kit's supplied M2x3 screws could not
reach the horn face.  P0.3 deepens the counterbore to 3.00 mm and identifies
held SCB2-8 and CB4-15 fastener candidates without releasing torque, locking,
procurement, assembly, powered work, motion, or energization.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import generate_hr_v0_fx103_output_adapter as r106

ROOT = Path(__file__).resolve().parents[1]
IDENTIFIER = "HR-V0-FX103-OUTPUT-ADAPTER-FAB-P0.3"
OUT = ROOT / "cad" / "hr-v0" / "generated" / "fx103-output-adapter-p0.3"
WEB = ROOT / "release" / "hr-v0" / "fx103-output-adapter-p0.3"
MISUMI = ROOT / "cad" / "vendor" / "misumi" / "fasteners-r107"
WARNING = (
    "PRELIMINARY - FASTENER-STACK CORRECTION CANDIDATE ONLY - NOT RELEASED "
    "FOR QUOTATION, PROCUREMENT, MACHINING, ASSEMBLY, CONNECTION, POWERED "
    "TEST, MOTION, OR ENERGIZATION"
)

M2_PART = "SCB2-8"
M2_LENGTH = 8.0
M2_HEAD_D = 3.8
M2_HEAD_H = 2.0
M4_PART = "CB4-15"
M4_LENGTH = 15.0
M4_HEAD_D = 7.0
M4_HEAD_H = 4.0
COUNTERBORE_DEPTH = 3.0


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, records: list[dict[str, object]]) -> None:
    r106.write_csv(path, records)


def replace_text(path: Path, replacements: list[tuple[str, str]]) -> None:
    text = path.read_text(encoding="utf-8")
    for old, new in replacements:
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8", newline="\n")


def rename(old: str, new: str) -> Path:
    source = OUT / old
    target = OUT / new
    source.replace(target)
    return target


def main() -> int:
    # Reuse the controlled P0.2 geometry generator with only deliberate global
    # inputs changed, then rewrite the machine-readable configuration records.
    r106.IDENTIFIER = IDENTIFIER
    r106.WARNING = WARNING
    r106.OUT = OUT
    r106.WEB = WEB
    r106.HN12_CBORE_DEPTH = COUNTERBORE_DEPTH
    result = r106.main()
    if result:
        return result

    c01_step = rename("FX103-C01_P0.2_horn_flange.step", "FX103-C01_P0.3_horn_flange.step")
    drawing = rename("FX103_output_adapter_P0.2_drawing.svg", "FX103_output_adapter_P0.3_drawing.svg")
    review_glb = rename("FX103_output_adapter_P0.2_review.glb", "FX103_output_adapter_P0.3_review.glb")
    review_step = rename("FX103_output_adapter_P0.2_review.step", "FX103_output_adapter_P0.3_review.step")

    common_replacements = [
        ("FX103-C01 P0.2", "FX103-C01 P0.3"),
        ("FX103-C01_P0.2", "FX103-C01_P0.3"),
        ("FX103_output_adapter_P0.2", "FX103_output_adapter_P0.3"),
        ("fx103-output-adapter-p0.2", "fx103-output-adapter-p0.3"),
        ("hr-v0-fx103-output-adapter-fabrication-candidate-p0.2.md", "hr-v0-fx103-output-adapter-fabrication-candidate-p0.3.md"),
        ("R106", "R107"),
    ]
    replace_text(drawing, common_replacements + [
        ("C'BORE Ø4.0 +0.10/0 ↧2.20 ±0.05", "C'BORE Ø4.0 +0.10/0 ↧3.00 ±0.05"),
        ("13. EXACT M2/M4 FASTENERS, LENGTHS, PRELOAD, LOCKING AND REUSE:", "13. HELD FASTENER CANDIDATES: SCB2-8 (M2) AND CB4-15 (M4)."),
        ("    SELECTION REQUIRED. ROBOTIS/RULAND APPLICATION ACCEPTANCE OPEN.", "    TORQUE, LOCKING, REUSE AND MANUFACTURER ACCEPTANCE REMAIN OPEN."),
        ("and attaches at the separate PCD-28 M4 pattern, leaving the Ø15 stub and", "and attaches with CB4-15 candidates before the coupling hub is installed."),
        ("transfer fasteners accessible. This resolves nominal geometry/tool access only.", "Hub removal is required for later M4 service. Geometry/tool access only."),
    ])

    guide = WEB / "index.html"
    replace_text(guide, common_replacements + [
        ("A non-buildable one-piece shaft adapter is now a two-piece, inspectable interface.", "The two-piece adapter now has a reachable horn screw stack and controlled service order."),
        ("<section class=\"finding\"><h2>Defect found in R103</h2>", "<section class=\"finding\"><h2>Two defects are now controlled</h2>"),
        ("The one-piece geometry is rejected.</p>", "The one-piece geometry is rejected. R107 also found that P0.2 left 5.80 mm of grip under the horn counterbore, so the supplied M2x3 screws stopped 2.80 mm before even reaching the horn face.</p>"),
        ("is a horn flange installed first through eight recessed PCD-16 holes.", "is a horn flange with 3.00 mm counterbores, installed first using held SCB2-8 candidates through eight PCD-16 holes."),
        ("is a separate piloted shaft flange attached by four M4 transfer screws", "is a separate piloted shaft flange attached by four held CB4-15 candidates"),
        ("The Ø15 shaft remains clear", "The nominal M2 engagement is 3.00 mm and nominal M4 engagement is 7.00 mm. The Ø15 shaft remains clear"),
        ("<article class=\"card\"><strong>11.95 MPa</strong>", "<article class=\"card\"><strong>3.00 mm</strong><p>Nominal SCB2-8 engagement after the corrected 5.00 mm flange grip; ROBOTIS acceptance remains open.</p></article><article class=\"card\"><strong>7.00 mm</strong><p>Nominal CB4-15 engagement through the 8.00 mm C02 flange; torque and locking remain open.</p></article><article class=\"card\"><strong>11.95 MPa</strong>"),
        ("<th>R107 state</th>", "<th>R107 state</th>"),
        ("Exact fasteners, engagement, preload, locking and manufacturer acceptance.", "SCB2-8 and CB4-15 are exact held candidates; lot identity, measured stack, torque, locking, reuse and manufacturer acceptance remain open."),
        ("ROBOTIS, Ruland and Magtrol application acceptance; exact screws;", "ROBOTIS, Ruland and Magtrol application acceptance; received screw identity and stack;"),
        (
            "Feature register</a> · <a href=\"../../../cad/hr-v0/generated/fx103-output-adapter-p0.3/analysis-register.csv\">Analysis register</a>",
            "Feature register</a> · <a href=\"../../../cad/hr-v0/generated/fx103-output-adapter-p0.3/fastener-candidate-register.csv\">Fastener candidates</a> · <a href=\"../../../cad/hr-v0/generated/fx103-output-adapter-p0.3/assembly-sequence.csv\">Assembly sequence</a> · <a href=\"../../../cad/hr-v0/generated/fx103-output-adapter-p0.3/analysis-register.csv\">Analysis register</a>",
        ),
    ])

    features = rows(OUT / "feature-register.csv")
    for row in features:
        row["part"] = row["part"].replace("FX103-C01 P0.2", "FX103-C01 P0.3")
        if row["feature"] == "C01-F04":
            row["nominal"] = "8X Ø2.2 +0.05/0 THRU; CBORE Ø4.0 +0.10/0 x 3.00 ±0.05; PCD Ø16 BASIC"
            row["state"] = "DEFINED CANDIDATE; SCB2-8 HELD"
        if row["feature"] == "C01-F05":
            row["state"] = "DEFINED CANDIDATE; CB4-15 HELD"
    write_csv(OUT / "feature-register.csv", features)

    old_grip = r106.C01_T - 2.2
    new_grip = r106.C01_T - COUNTERBORE_DEPTH
    analysis = rows(OUT / "analysis-register.csv")
    for row in analysis:
        row["screen"] = row["screen"].replace("R106-", "R107-")
        row["inputs"] = row["inputs"].replace("candidate M2 head", "SCB2-8 head").replace("candidate M4 head", "CB4-15 head")
        row["authority"] = row["authority"].replace("EXACT HEAD STILL SELECTION REQUIRED", "SCB2-8 CANDIDATE; ROBOTIS ACCEPTANCE OPEN").replace("EXACT FASTENER/TOOL OPEN", "SCB2-8 CANDIDATE; TOOL/STACK PROOF OPEN").replace("EXACT HEAD/TOOL OPEN", "CB4-15 CANDIDATE; TOOL/STACK PROOF OPEN")
    analysis.extend([
        {"screen":"R107-A16","inputs":f"P0.2 grip {old_grip:.2f} - supplied WB M2x3 length 3.00","result":f"{old_grip - 3.0:.6f} mm nominal shortfall before horn engagement","authority":"P0.2 FASTENER STACK REJECTED"},
        {"screen":"R107-A17","inputs":f"SCB2-8 length {M2_LENGTH:.2f} - corrected grip {new_grip:.2f}","result":f"{M2_LENGTH - new_grip:.6f} mm nominal horn engagement","authority":"CANDIDATE SCREEN; TOLERANCE/THREAD/PROTRUSION/ROBOTIS ACCEPTANCE OPEN"},
        {"screen":"R107-A18","inputs":f"CB4-15 length {M4_LENGTH:.2f} - C02 grip {r106.C02_T:.2f}","result":f"{M4_LENGTH - r106.C02_T:.6f} mm nominal C01 engagement","authority":"CANDIDATE SCREEN; TOLERANCE/THREAD/PRELOAD/LOCKING OPEN"},
        {"screen":"R107-A19","inputs":f"hub gap {r106.COUPLING_GAP_TO_FLANGE:.2f} - CB4 head height {M4_HEAD_H:.2f}","result":f"{r106.COUPLING_GAP_TO_FLANGE - M4_HEAD_H:.6f} mm nominal axial head/hub clearance","authority":"ASSEMBLE M4 BEFORE HUB; REMOVE HUB BEFORE M4 SERVICE; PHYSICAL PROOF OPEN"},
    ])
    write_csv(OUT / "analysis-register.csv", analysis)

    write_csv(OUT / "fastener-candidate-register.csv", [
        {"interface":"HN12 to C01","candidate":M2_PART,"quantity":"8","definition":"MISUMI M2 x 0.4 x 8 mm fully threaded socket head cap screw; JIS SUSXM7; A2-70; head Ø3.8 x 2 mm; 1.5 mm hex","nominal_grip_mm":f"{new_grip:.3f}","nominal_engagement_mm":f"{M2_LENGTH-new_grip:.3f}","state":"EXACT CANDIDATE HOLD","open":"ROBOTIS acceptance; received lot identity/dimensions; tolerance stack; protrusion; torque; locking; reuse; thread/horn proof"},
        {"interface":"C02 to C01","candidate":M4_PART,"quantity":"4","definition":"MISUMI M4 x 0.7 x 15 mm fully threaded socket head cap screw; SCM435; black oxide; 38-43 HRC; catalog strength rank 12.9; head Ø7 x 4 mm; 3 mm hex","nominal_grip_mm":f"{r106.C02_T:.3f}","nominal_engagement_mm":f"{M4_LENGTH-r106.C02_T:.3f}","state":"EXACT CANDIDATE HOLD","open":"current orderability; received lot/certificate/dimensions; corrosion; bearing/friction; torque/preload; locking; reuse; thread/joint proof"},
    ])
    write_csv(OUT / "assembly-sequence.csv", [
        {"step":"AS-01","operation":"verify received HN12, C01, C02 and both fastener lots against signed receiving/FAI records","prerequisite":"all physical records executed and accepted","authority":"NOT EXECUTED; NO ASSEMBLY RELEASE"},
        {"step":"AS-02","operation":"seat C01 on HN12 datum face and install eight SCB2-8 candidates in controlled cross pattern","prerequisite":"ROBOTIS acceptance plus released torque/locking/reuse procedure","authority":"NOT EXECUTED; NO ASSEMBLY RELEASE"},
        {"step":"AS-03","operation":"verify no M2 bottoming/protrusion/interference and record face seating/runout","prerequisite":"released metrology method and acceptance","authority":"NOT EXECUTED; NO ASSEMBLY RELEASE"},
        {"step":"AS-04","operation":"pilot C02 onto C01 and install four CB4-15 candidates in controlled cross pattern","prerequisite":"released torque/preload/locking procedure","authority":"NOT EXECUTED; NO ASSEMBLY RELEASE"},
        {"step":"AS-05","operation":"verify M4 head seating, engagement and tool withdrawal before coupling installation","prerequisite":"released inspection method and acceptance","authority":"NOT EXECUTED; NO ASSEMBLY RELEASE"},
        {"step":"AS-06","operation":"install coupling hub only after M4 inspection; remove hub before any later M4 service","prerequisite":"Ruland acceptance and released hub procedure","authority":"NOT EXECUTED; NO ASSEMBLY RELEASE"},
    ])

    inspections = rows(OUT / "inspection-plan.csv")
    inspections.extend([
        {"record":"FAI-15","characteristic":"received SCB2-8 identity, M2x0.4 thread, length/head/hex, material-class evidence and quantity","method":"certificate/packaging review, micrometer/comparator and thread gage","acceptance":"signed lot-specific fastener record; no substitution","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"FAI-16","characteristic":"received CB4-15 identity, M4x0.7 thread, length/head/hex, material-class/finish evidence and quantity","method":"certificate/packaging review, micrometer/comparator and thread gage","acceptance":"signed lot-specific fastener record; no substitution","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"FAI-17","characteristic":"assembled M2/M4 engagement, no bottoming/protrusion, head seating, hub/tool clearance and service order","method":"released stack measurement, witness/feeler check and signed assembly traveler","acceptance":"SELECTION REQUIRED","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
    ])
    for row in inspections:
        row["acceptance"] = row["acceptance"].replace("all 15 features", "all 15 features plus both fastener candidates")
    write_csv(OUT / "inspection-plan.csv", inspections)

    sources = rows(OUT / "source-register.csv")
    for row in sources:
        row["source"] = row["source"].replace("R106-", "R107-")
    sources.extend([
        {"source":"R107-SRC-07","organization":"MISUMI USA","record":"SCB socket-head cap screws live product page","revision_date":"live page accessed 2026-08-08","locator":"https://us.misumi-ec.com/vona2/detail/110300239250/?HissuCode=SCB2-8","sha256":"LIVE PAGE - NOT DOWNLOADED","use":"SCB2-8 identity, availability, M2x0.4x8 fully threaded, JIS SUSXM7, A2-70 and head/hex dimensions"},
        {"source":"R107-SRC-08","organization":"MISUMI USA","record":"CB/BOX-CB hexagon socket-head cap screw catalog page 809-810","revision_date":"PDF metadata 2015-11-05; no printed revision/date; accessed 2026-08-08","locator":"cad/vendor/misumi/fasteners-r107/MISUMI_CB_socket_head_cap_screws.pdf","sha256":sha256(MISUMI / "MISUMI_CB_socket_head_cap_screws.pdf"),"use":"CB4-15 catalog identity, M4x0.7, full thread, SCM435, black oxide, 38-43 HRC, catalog strength rank 12.9 and head/hex dimensions"},
    ])
    write_csv(OUT / "source-register.csv", sources)

    parents = rows(OUT / "parent-artifact-register.csv")
    parents.extend([
        {"parent":"HR-V0-FX103-OUTPUT-ADAPTER-FAB-P0.2","artifact":"cad/hr-v0/generated/fx103-output-adapter-p0.2/feature-register.csv","sha256":sha256(ROOT / "cad/hr-v0/generated/fx103-output-adapter-p0.2/feature-register.csv"),"use":"superseded 2.20 mm counterbore and exact-fastener hold"},
        {"parent":"HR-V0-FX103-OUTPUT-ADAPTER-FAB-P0.2","artifact":"cad/hr-v0/generated/fx103-output-adapter-p0.2/geometry-check.json","sha256":sha256(ROOT / "cad/hr-v0/generated/fx103-output-adapter-p0.2/geometry-check.json"),"use":"controlled P0.2 nominal geometry and mass/hash baseline"},
    ])
    write_csv(OUT / "parent-artifact-register.csv", parents)

    holds = rows(OUT / "open-hold-register.csv")
    for row in holds:
        if row["hold_id"] == "OA-HOLD-05":
            row["missing_evidence"] = "SCB2-8 and CB4-15 candidates identified; received lot identity, tolerance stack, protrusion, torque/preload, locking, corrosion, reuse and proof remain open"
            row["state"] = "PARTIAL"
        row["missing_evidence"] = row["missing_evidence"].replace("exact horn fastener", "SCB2-8 candidate and exact horn fastener")
    write_csv(OUT / "open-hold-register.csv", holds)

    rfis = rows(OUT / "dfm-rfi.csv")
    for row in rfis:
        if row["rfi"] == "OA-RFI-01":
            row["question"] = "Review SCB2-8 with 3.00 mm nominal engagement in the HN12 8-M2x4 TAP THRU pattern; confirm or correct screw, engagement, protrusion, torque, locking/reuse, horn/thread/serration and extraneous-load limits."
        if row["rfi"] == "OA-RFI-03":
            row["question"] = "DFM-review both H1150 parts including the corrected 3.00 mm C01 counterbores, SCB2-8/CB4-15 stack, tool/service order, PCD-28 threads, pilot fit, stub, runout, R1 root and complete FAI. No quote or machining authorized."
    write_csv(OUT / "dfm-rfi.csv", rfis)

    geometry_path = OUT / "geometry-check.json"
    geometry = json.loads(geometry_path.read_text(encoding="utf-8"))
    geometry["identifier"] = IDENTIFIER
    geometry["supersession"] = {"rejected":"FX103-C01 P0.2 fastener stack; supplied WB M2x3 cannot reach HN12 face","replacement":["FX103-C01 P0.3 horn flange","FX103-C02 P0.1 shaft flange"]}
    geometry["c01"]["counterbore_depth_mm"] = COUNTERBORE_DEPTH
    geometry["c01"]["step_sha256"] = sha256(c01_step)
    geometry["fastener_candidates"] = {"horn":M2_PART,"transfer":M4_PART,"selected_for_release":False}
    geometry["nominal_engagement_mm"] = {"horn":M2_LENGTH-new_grip,"transfer":M4_LENGTH-r106.C02_T}
    geometry["p02_supplied_m2_shortfall_mm"] = old_grip - 3.0
    geometry_path.write_text(json.dumps(geometry, indent=2) + "\n", encoding="utf-8")

    status_path = OUT / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({"identifier":IDENTIFIER,"p02_fastener_stack_rejected":True,"exact_fastener_candidates_identified":True,"exact_fasteners_selected":False,"partial_hold_count":4,"open_hold_count":7})
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    # Ensure every renamed/rewritten artifact is reflected in the hash manifest.
    r106.write_generated_source_manifest()
    print(f"generated {IDENTIFIER}: P0.2 M2 reach defect rejected; 19 screens; 17 unexecuted inspections; 4 partial + 7 open holds; all release flags false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
