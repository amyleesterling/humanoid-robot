#!/usr/bin/env python3
"""Generate R263 carrier-power harness and panel-placement reconciliation P0.2."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import shutil
from pathlib import Path

from generate_hr_v0_bom_closure import classification


ROOT = Path(__file__).resolve().parents[1]
ID = "HR-V0-DXL-PROT-CARRIER-HARNESS-P0.2"
CID = "HR-V0-CONFIG-REC-P0.27"
ROUND = "R263"
DATE = "2026-08-12"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
ENG = ROOT / "electrical/harness/hr-v0-dxl-protection-carrier-harness-p0.2"
REL = ROOT / "release/hr-v0/dxl-protection-carrier-harness-p0.2"
CFG0 = ROOT / "configuration/hr-v0-config-reconciliation-p0.26"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.27"
CFGR = ROOT / "release/hr-v0/configuration-reconciliation-p0.27"
BOM = ROOT / "bom/bom.csv"
CLOSURE = ROOT / "bom/hr-v0-bom-closure.csv"
RELEASE = ROOT / "release/hr-v0/release-candidate.json"
SOURCES = {
    "carrier_terminals": ROOT / "electrical/kicad/hr-v0-dxl-protection-carrier-p0.3/terminal-schedule.csv",
    "star_terminals": ROOT / "electrical/kicad/hr-v0-dxl-star-p0.2-carrier-candidate/connector-schedule.csv",
    "system_terminals": ROOT / "electrical/kicad/project-button-v3-p1.15-carrier-candidate/connector-schedule.csv",
    "old_placement": ROOT / "electrical/integration/hr-v0-dxl-carrier-integration-p0.1/panel-placement-screen.csv",
    "old_route": ROOT / "electrical/integration/hr-v0-dxl-carrier-integration-p0.1/route-bound-screen.csv",
    "panel_p07": ROOT / "electrical/panel/hr-v0-control-panel-p0.7-node-placement/candidate-backplate-layout.csv",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def warned(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [row | {"warning": WARNING} for row in rows]


def manifest(directory: Path) -> None:
    files = sorted(path for path in directory.iterdir() if path.is_file() and path.name != "file-manifest.csv")
    write_csv(directory / "file-manifest.csv", ["path", "bytes", "sha256"], [
        {"path": path.name, "bytes": path.stat().st_size, "sha256": sha(path)} for path in files
    ])


def intersects(a: dict[str, object], b: dict[str, str]) -> tuple[float, float] | None:
    ax, ay, aw, ah = (float(a[k]) for k in ("x_mm", "y_mm", "width_mm", "height_mm"))
    bx, by, bw, bh = (float(b[k]) for k in ("x_mm", "y_mm", "width_mm", "height_mm"))
    ox = min(ax + aw, bx + bw) - max(ax, bx)
    oy = min(ay + ah, by + bh) - max(ay, by)
    return (ox, oy) if ox > 0 and oy > 0 else None


def package_rows() -> dict[str, tuple[list[str], list[dict[str, object]]]]:
    sources = [
        {"source_id":"SRC-01","organization":"JST","document":"VH connector English catalog eVH.pdf","revision_or_date":"current catalog asset accessed 2026-08-12","url":"https://www.jst-mfg.com/product/pdf/eng/eVH.pdf","controlled_fact":"B2P-VH/VHR-2N mating family; SVH-21T-P1.1 accepts AWG 22-18 and 1.7-3.0 mm insulation OD; AWG 18 shrouded-header rating statement is 7 A","not_proved":"installed current, crimp geometry, process, thermal rise, retention or system acceptance"},
        {"source_id":"SRC-02","organization":"JST","document":"Handling Precautions for Terminals and Connectors","revision_or_date":"official English asset accessed 2026-08-12","url":"https://www.jst-mfg.com/precaution/eP-Handling.pdf","controlled_fact":"application suitability and controlled processing remain user responsibilities; connector must not carry structural load","not_proved":"project workmanship acceptance or safety function"},
        {"source_id":"SRC-03","organization":"Belden","document":"9918 live product record","revision_or_date":"revision 0.515 dated 2026-02-20; accessed 2026-08-12","url":"https://www.belden.com/products/cable/electronic-wire-cable/lead-wire-hook-up-wire/9918","controlled_fact":"18 AWG 16x30 tinned copper; nominal 2.0 mm OD; red 9918 002100 and black 9918 010100 100 ft items; 20 mm stationary/installation minimum bend radius","not_proved":"installed ampacity, flex life, route, bundling, voltage drop or fault clearing"},
        {"source_id":"SRC-04","organization":"Blue Sea Systems","document":"5025 live product page","revision_or_date":"live page accessed 2026-08-12","url":"https://www.bluesea.com/products/5025","controlled_fact":"six-circuit block; branch screw terminals are #8-32 with captive star washers; ring or snap-fork terminals accepted; published screw-terminal torque 18 in-lb (2.03 N m)","not_proved":"physical F1/F2/F3 position assignment, fuse rating, conductor/terminal application, stacking, thermal or project approval"},
        {"source_id":"SRC-05","organization":"Blue Sea Systems","document":"Wiring-Diagram-5025_5030.pdf","revision_or_date":"no revision/date printed in retrieved record; accessed 2026-08-12","url":"https://d2pyqm2yd3fw2i.cloudfront.net/files/resources/instructions/Wiring-Diagram-5025_5030.pdf","controlled_fact":"official 5025/5030 wiring-diagram identity","not_proved":"received orientation, circuit-number assignment or Project Button wiring acceptance"},
        {"source_id":"SRC-06","organization":"Panduit","document":"Convenience Pack Terminals 41222.pdf","revision_or_date":"current official asset accessed 2026-08-12","url":"https://www.panduit.com/content/dam/panduit/en/products/media/2/22/222/1222/41222.pdf","controlled_fact":"PN18-8R-E is a nylon-insulated ring terminal for 22-18 AWG and #8 stud, package quantity 20","not_proved":"Belden 9918 process qualification, exact strip/crimp limits, tool combination, pull result, stacking or installed thermal suitability"},
        {"source_id":"SRC-07","organization":"Panduit","document":"CT-100B operation instructions PA29563A01","revision_or_date":"Rev 01 dated 2024-02; accessed 2026-08-12","url":"https://www.panduit.com/content/dam/panduit/en/products/media/2/72/472/3472/111343472.pdf","controlled_fact":"CT-100B processes Panduit insulated terminals on 22-10 AWG stranded wire and is not electrically insulating","not_proved":"approved PN18-8R-E/Belden 9918 combination, calibration, controlled-cycle behavior or project release"},
    ]

    axes = [("J1", "F1.2", "JP1", "J1_FUSED_PRELIMIT", "J1_LIMITED_VDD"), ("J2", "F2.2", "JP2", "J2_FUSED_PRELIMIT", "J2_LIMITED_VDD"), ("G1", "F3.2", "JP3", "J3_FUSED_PRELIMIT", "J3_LIMITED_VDD")]
    harnesses: list[dict[str, object]] = []
    interfaces: list[dict[str, object]] = []
    cuts: list[dict[str, object]] = []
    for axis, fuse, star, pre, limited in axes:
        cin = f"HAR-CIN-{axis}"
        cout = f"HAR-COUT-{axis}"
        harnesses.extend([
            {"harness_id":cin,"function":f"{fuse} and 5025 negative-bus branch terminal to LIM{1 if axis=='J1' else 2 if axis=='J2' else 3}.JIN1","conductors":2,"end_a_population":"2 x Panduit PN18-8R-E exact candidate","end_b_population":"1 x VHR-2N + 2 x SVH-21T-P1.1","cut_length_mm":"SELECTION REQUIRED","release_state":"DEFINITION ADVANCED; DO NOT BUILD"},
            {"harness_id":cout,"function":f"LIM{1 if axis=='J1' else 2 if axis=='J2' else 3}.JOUT1 to INJ1.{star}","conductors":2,"end_a_population":"1 x VHR-2N + 2 x SVH-21T-P1.1","end_b_population":"1 x VHR-2N + 2 x SVH-21T-P1.1","cut_length_mm":"SELECTION REQUIRED","release_state":"DEFINITION ADVANCED; DO NOT BUILD"},
        ])
        lim = f"LIM{1 if axis=='J1' else 2 if axis=='J2' else 3}"
        for conductor, color, mpn, net in (("P","RED","9918 002100",pre),("R","BLACK","9918 010100","ACT_0V_PE_BONDED")):
            source_ref = f"{fuse}; physical 5025 circuit position SELECTION REQUIRED" if conductor == "P" else "5025 negative-bus branch screw; physical position SELECTION REQUIRED"
            interfaces.extend([
                {"harness_id":cin,"conductor":conductor,"end":"A","reference":source_ref,"terminal_or_cavity":"#8-32 screw interface candidate","project_net":net,"termination":"Panduit PN18-8R-E","wire":f"Belden {mpn} {color}","acceptance_boundary":"physical circuit/return position, received fit, torque and stacking remain open"},
                {"harness_id":cin,"conductor":conductor,"end":"B","reference":f"{lim}.JIN1","terminal_or_cavity":"1" if conductor == "P" else "2","project_net":net,"termination":"VHR-2N / SVH-21T-P1.1","wire":f"Belden {mpn} {color}","acceptance_boundary":"received orientation, process, continuity and retention remain open"},
                {"harness_id":cout,"conductor":conductor,"end":"A","reference":f"{lim}.JOUT1","terminal_or_cavity":"1" if conductor == "P" else "2","project_net":limited if conductor == "P" else net,"termination":"VHR-2N / SVH-21T-P1.1","wire":f"Belden {mpn} {color}","acceptance_boundary":"received orientation, process, continuity and retention remain open"},
                {"harness_id":cout,"conductor":conductor,"end":"B","reference":f"INJ1.{star}","terminal_or_cavity":"1" if conductor == "P" else "2","project_net":limited if conductor == "P" else net,"termination":"VHR-2N / SVH-21T-P1.1","wire":f"Belden {mpn} {color}","acceptance_boundary":"received orientation, process, continuity and retention remain open"},
            ])
            for harness, end_a, end_b in ((cin,"PN18-8R-E","SVH-21T-P1.1"),(cout,"SVH-21T-P1.1","SVH-21T-P1.1")):
                cuts.append({"wire_id":f"{harness}-{conductor}","harness_id":harness,"signal":net if harness == cin else (limited if conductor == "P" else net),"wire_mpn":mpn,"color":color,"cut_length_mm":"SELECTION REQUIRED","strip_end_a_mm":"SELECTION REQUIRED","strip_end_b_mm":"SELECTION REQUIRED","end_a_termination":end_a,"end_b_termination":end_b,"label":f"{harness}-{conductor}","state":"DO NOT CUT OR CRIMP"})

    bom = [
        {"item_id":"HB-01","manufacturer":"JST","manufacturer_part_number":"VHR-2N","description":"2-circuit VH mating housing","required_population":9,"process_spares":"SELECTION REQUIRED","state":"EXACT CANDIDATE HOLD"},
        {"item_id":"HB-02","manufacturer":"JST","manufacturer_part_number":"SVH-21T-P1.1","description":"tin-plated contact for AWG 22-18","required_population":18,"process_spares":"SELECTION REQUIRED","state":"EXACT CANDIDATE HOLD"},
        {"item_id":"HB-03","manufacturer":"Panduit","manufacturer_part_number":"PN18-8R-E","description":"nylon-insulated 22-18 AWG #8 ring terminal; 20-piece package","required_population":6,"process_spares":14,"state":"EXACT CANDIDATE HOLD; TOOL/PROCESS OPEN"},
        {"item_id":"HB-04","manufacturer":"Belden","manufacturer_part_number":"9918 002100","description":"18 AWG red PVC hook-up wire, 100 ft","required_population":"6 route-dependent cuts","process_spares":"SELECTION REQUIRED","state":"EXACT CANDIDATE HOLD"},
        {"item_id":"HB-05","manufacturer":"Belden","manufacturer_part_number":"9918 010100","description":"18 AWG black PVC hook-up wire, 100 ft","required_population":"6 route-dependent cuts","process_spares":"SELECTION REQUIRED","state":"EXACT CANDIDATE HOLD"},
        {"item_id":"HB-06","manufacturer":"SELECTION REQUIRED","manufacturer_part_number":"SELECTION REQUIRED","description":"labels, abrasion protection, support and tie-down hardware","required_population":"SELECTION REQUIRED","process_spares":"SELECTION REQUIRED","state":"SELECTION REQUIRED"},
    ]

    old, _ = read_csv(SOURCES["old_placement"])
    panel, _ = read_csv(SOURCES["panel_p07"])
    physical = [row for row in panel if row["layout_id"] in {"BP-027","BP-028","BP-029","BP-030","BP-031","BP-032","BP-033"}]
    collisions: list[dict[str, object]] = []
    for carrier in old:
        for obj in physical:
            overlap = intersects(carrier, obj)
            if overlap:
                collisions.append({"finding_id":f"COL-{len(collisions)+1:02d}","stale_reference":carrier["reference"],"current_p07_reference":obj["reference"],"overlap_x_mm":f"{overlap[0]:.3f}","overlap_y_mm":f"{overlap[1]:.3f}","overlap_area_mm2":f"{overlap[0]*overlap[1]:.3f}","disposition":"HARD PLANAR COLLISION; R161 PLACEMENT NOT CURRENT"})

    candidates = [
        {"reference":"LIM1","axis":"J1 shoulder","x_mm":438,"y_mm":300,"width_mm":60,"height_mm":100,"rotation_deg":90,"boundary":"P0.7 right-side strip x=428..533.4; below compute retention y>275.4","planar_collision_count":0,"release_state":"ANALYTICAL CANDIDATE ONLY - NO DRILLING"},
        {"reference":"LIM2","axis":"J2 elbow","x_mm":438,"y_mm":410,"width_mm":60,"height_mm":100,"rotation_deg":90,"boundary":"P0.7 right-side strip x=428..533.4","planar_collision_count":0,"release_state":"ANALYTICAL CANDIDATE ONLY - NO DRILLING"},
        {"reference":"LIM3","axis":"G1 gripper","x_mm":438,"y_mm":520,"width_mm":60,"height_mm":100,"rotation_deg":90,"boundary":"P0.7 right-side strip x=428..533.4; above backplate bottom y=685.8","planar_collision_count":0,"release_state":"ANALYTICAL CANDIDATE ONLY - NO DRILLING"},
    ]
    fixed = [row for row in panel if row["object_type"] != "reserved_unallocated_envelope"]
    for candidate in candidates:
        hits = [row["reference"] for row in fixed if row["reference"] not in {"BP1"} and intersects(candidate, row)]
        candidate["planar_collision_count"] = len(hits)
        if hits:
            candidate["release_state"] = "REJECTED BY PLANAR COLLISION: " + "/".join(hits)

    fuse_center = (104.0, 450.0)
    star_center = (274.0, 260.0)
    routes = []
    for candidate in candidates:
        center = (float(candidate["x_mm"]) + float(candidate["width_mm"])/2, float(candidate["y_mm"]) + float(candidate["height_mm"])/2)
        axis = str(candidate["axis"]).split()[0]
        for kind, start, end in (("CIN",fuse_center,center),("COUT",center,star_center)):
            routes.append({"harness_id":f"HAR-{kind}-{axis}","from_surrogate":f"({start[0]:.1f},{start[1]:.1f})","to_surrogate":f"({end[0]:.1f},{end[1]:.1f})","direct_centerline_lower_bound_mm":f"{math.dist(start,end):.1f}","cut_length_mm":"SELECTION REQUIRED","why_not_cut_length":"centers omit connector exits, duct path, 20 mm bend radius, service loop, support, termination allowance and received tolerances","state":"SCREEN ONLY - DO NOT CUT"})

    process = [
        ("MP-01","receive and identify","verify every housing, contact, terminal and wire lot against exact manufacturer identity"),
        ("MP-02","received fit","verify 5025 #8 branch screw interface and one-ring-per-screw arrangement; no stacking inference"),
        ("MP-03","placement mock-up","install inert dimensional articles at the P0.2 rotated candidates; verify enclosure depth, covers, sweeps, support and service access"),
        ("MP-04","route survey","measure each installed centerline through selected duct/support path with 20 mm minimum wire bend radius"),
        ("MP-05","cut","apply accepted route-specific allowance and record actual cut length; no project value exists yet"),
        ("MP-06","strip JST end","use controlled SVH-21T-P1.1/9918 process; inspect for strand or insulation damage"),
        ("MP-07","crimp JST end","use manufacturer/qualified-provider controlled tooling and numeric acceptance; no generic plier"),
        ("MP-08","strip Panduit end","use accepted PN18-8R-E/9918 process and numeric strip acceptance"),
        ("MP-09","crimp Panduit end","use accepted tooling/product combination and record inspection/pull evidence"),
        ("MP-10","populate","positive to cavity 1 and return to cavity 2; verify latch and contact seating"),
        ("MP-11","label and support","apply accepted labels and support so no connector or screw terminal carries cable mass"),
        ("MP-12","unpowered inspection","100 percent continuity, polarity, isolation, retention and second-person point-to-point check"),
        ("MP-13","qualified testing","only after separate authority, execute protected current, drop, thermal, fault and reverse-energy tests"),
    ]
    process_rows = [{"step_id":sid,"operation":op,"controlled_requirement":req,"numeric_acceptance":"SELECTION REQUIRED / TEST REQUIRED","execution_state":"NOT EXECUTED","evidence_uri":""} for sid,op,req in process]
    holds = [
        ("H-01","P0.2 carrier placement","received carrier/enclosure dimensions, depth, connector sweeps, standoffs, airflow, cover and service-access proof for all three rotated candidates"),
        ("H-02","5025 circuit/return assignment","received block orientation and a controlled one-ring-per-branch-screw F1/F2/F3 positive/return assignment"),
        ("H-03","route and cut lengths","installed route measurement for all six harnesses including duct transitions, 20 mm bends, supports, service loops and termination allowances"),
        ("H-04","JST processing","manufacturer/qualified-provider strip, crimp, tool, inspection, pull and sampling limits for SVH-21T-P1.1 with Belden 9918"),
        ("H-05","Panduit processing","approved PN18-8R-E/Belden 9918 tooling/product combination, strip/crimp limits, inspection, pull and sampling evidence"),
        ("H-06","labels and supports","exact label, abrasion protection, tie-down and strain-relief materials plus placement/retention evidence"),
        ("H-07","installed electrical limits","fault current, fuse, source foldback, ambient, bundling, connector/terminal limits, inrush, regeneration, duty and jurisdiction evidence"),
        ("H-08","received electrical inspection","configuration-bound continuity, polarity, isolation, torque and retention results for every harness"),
        ("H-09","protected physical tests","accepted limited-energy voltage-drop, temperature-rise, fault-clearing and reverse-energy results"),
        ("H-10","qualified review and authority","qualified electrical/mechanical review plus separate written authority for procurement and each physical stage"),
    ]
    hold_rows = [{"hold_id":hid,"scope":scope,"state":"OPEN","closure_evidence":evidence} for hid,scope,evidence in holds]
    criteria = [
        "All six harness identities and 24 end/interface rows match current ECAD terminals",
        "Nine VHR-2N housings and eighteen SVH-21T-P1.1 production contacts are the minimum populated count before process scrap",
        "Six PN18-8R-E terminals are candidate source-side branch terminations and no main-bus-stud stacking is inferred",
        "The obsolete R161 lower-zone placements are rejected by all thirteen P0.7 collision rows",
        "The three rotated right-side planning candidates remain inside the nominal backplate and have zero nominal planar intersections",
        "Received depth, connector sweep, bend, service, thermal and enclosure evidence accepts the P0.2 placement",
        "Physical 5025 circuit and return screw positions are frozen from received orientation evidence",
        "All twelve conductor cut lengths are measured and accepted from installed routes",
        "JST and Panduit terminations use accepted controlled processes and process-coupon evidence",
        "One hundred percent continuity, polarity and isolation inspection passes before any mating",
        "Every screw termination has received torque/retention evidence without stacked-ring inference",
        "Installed voltage drop and temperature rise pass at accepted duty and ambient",
        "Protection/fault/reverse-energy evidence passes with selected fuses and source behavior",
        "Cable support and abrasion control prevent connector and terminal mechanical loading",
        "Qualified electrical review accepts conductor, terminal, protection and grounding application",
        "Qualified mechanical/enclosure review accepts all placement, access, retention and heat evidence",
        "No procurement, fabrication, assembly, connection or powered test occurs without separate written authority",
        "No safety credit or energization authority is inferred from this package",
    ]
    acceptance = [{"acceptance_id":f"ACC-{i:02d}","criterion":criterion,"execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":""} for i,criterion in enumerate(criteria,1)]
    return {
        "primary-source-register.csv": (["source_id","organization","document","revision_or_date","url","controlled_fact","not_proved","warning"], warned(sources)),
        "harness-schedule.csv": (["harness_id","function","conductors","end_a_population","end_b_population","cut_length_mm","release_state","warning"], warned(harnesses)),
        "interface-control.csv": (["harness_id","conductor","end","reference","terminal_or_cavity","project_net","termination","wire","acceptance_boundary","warning"], warned(interfaces)),
        "cut-crimp-schedule.csv": (["wire_id","harness_id","signal","wire_mpn","color","cut_length_mm","strip_end_a_mm","strip_end_b_mm","end_a_termination","end_b_termination","label","state","warning"], warned(cuts)),
        "harness-bom.csv": (["item_id","manufacturer","manufacturer_part_number","description","required_population","process_spares","state","warning"], warned(bom)),
        "stale-placement-collisions.csv": (["finding_id","stale_reference","current_p07_reference","overlap_x_mm","overlap_y_mm","overlap_area_mm2","disposition","warning"], warned(collisions)),
        "placement-candidate.csv": (["reference","axis","x_mm","y_mm","width_mm","height_mm","rotation_deg","boundary","planar_collision_count","release_state","warning"], warned(candidates)),
        "route-lower-bound.csv": (["harness_id","from_surrogate","to_surrogate","direct_centerline_lower_bound_mm","cut_length_mm","why_not_cut_length","state","warning"], warned(routes)),
        "manufacturing-process.csv": (["step_id","operation","controlled_requirement","numeric_acceptance","execution_state","evidence_uri","warning"], warned(process_rows)),
        "open-holds.csv": (["hold_id","scope","state","closure_evidence","warning"], warned(hold_rows)),
        "acceptance-matrix.csv": (["acceptance_id","criterion","execution_state","result","evidence_uri","approver","warning"], warned(acceptance)),
    }


def topology_svg() -> str:
    return f"""<svg xmlns='http://www.w3.org/2000/svg' width='1400' height='620' viewBox='0 0 1400 620' role='img' aria-labelledby='title desc'><title id='title'>Six carrier power harnesses</title><desc id='desc'>Three protected branches enter three current limiter carriers and three limited outputs feed the DXL star.</desc><style>text{{font-family:system-ui,sans-serif;fill:#092f57}}.h{{font-size:30px;font-weight:800}}.t{{font-size:19px}}.n{{font-size:22px;font-weight:800}}.b{{fill:#dff3ff;stroke:#092f57;stroke-width:4}}.c{{fill:#fff4c7;stroke:#092f57;stroke-width:4}}.p{{stroke:#d69b00;stroke-width:10}}.r{{stroke:#20252b;stroke-width:10}}</style><rect width='1400' height='620' fill='#f8fbfe'/><text x='45' y='55' class='h'>HR-V0 carrier power path — six harnesses, twelve conductors</text><rect x='45' y='105' width='290' height='430' rx='18' class='b'/><text x='75' y='150' class='h'>Blue Sea 5025</text><text x='75' y='205' class='n'>F1.2 + branch return</text><text x='75' y='325' class='n'>F2.2 + branch return</text><text x='75' y='445' class='n'>F3.2 + branch return</text><rect x='565' y='105' width='280' height='430' rx='18' class='c'/><text x='600' y='150' class='h'>Limiter carriers</text><text x='625' y='205' class='n'>LIM1 · JIN1/JOUT1</text><text x='625' y='325' class='n'>LIM2 · JIN1/JOUT1</text><text x='625' y='445' class='n'>LIM3 · JIN1/JOUT1</text><rect x='1080' y='105' width='275' height='430' rx='18' class='b'/><text x='1135' y='150' class='h'>DXL star</text><text x='1160' y='205' class='n'>JP1 · J1</text><text x='1160' y='325' class='n'>JP2 · J2</text><text x='1160' y='445' class='n'>JP3 · G1</text>""" + "".join(f"<line x1='335' y1='{y}' x2='565' y2='{y}' class='p'/><line x1='845' y1='{y}' x2='1080' y2='{y}' class='p'/><text x='355' y='{y-16}' class='t'>HAR-CIN-{a}</text><text x='865' y='{y-16}' class='t'>HAR-COUT-{a}</text>" for a,y in (("J1",205),("J2",325),("G1",445))) + f"""<text x='45' y='585' class='t'>RED positive and BLACK return are independently terminated. Exact cuts, processes, physical circuit positions and every test remain open.</text></svg>"""


def table(title: str, rows: list[dict[str, object]], fields: list[str]) -> str:
    head = "".join(f"<th>{html.escape(field.replace('_',' ').title())}</th>" for field in fields)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(row.get(field,'')))}</td>" for field in fields) + "</tr>" for row in rows)
    return f"<section><h2>{html.escape(title)}</h2><div class='scroll'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div></section>"


def guide(data: dict[str, tuple[list[str], list[dict[str, object]]]]) -> str:
    collisions = data["stale-placement-collisions.csv"][1]
    placements = data["placement-candidate.csv"][1]
    harnesses = data["harness-schedule.csv"][1]
    holds = data["open-holds.csv"][1]
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{ID}</title><style>:root{{--sky:#dff3ff;--blue:#092f57;--gold:#f3bd28;--ink:#102338;--paper:#f8fbfe;--line:#8eb9d8;--danger:#8d1721}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.15vw,19px)/1.55 system-ui,sans-serif}}header{{padding:clamp(24px,5vw,68px);background:linear-gradient(135deg,var(--sky),#fff);border-bottom:8px solid var(--gold)}}main{{max-width:1500px;margin:auto;padding:24px}}h1{{font-size:clamp(34px,5vw,70px);line-height:1.05;color:var(--blue)}}h2{{font-size:clamp(23px,2.3vw,34px);color:var(--blue)}}.warn{{background:#fff4c7;border:3px solid var(--gold);padding:16px;font-weight:800}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin:24px 0}}.card,section{{background:#fff;border:2px solid var(--line);border-radius:14px;padding:18px;margin:18px 0}}.big{{font-size:2.2rem;font-weight:850;color:var(--blue)}}.bad{{color:var(--danger)}}object{{width:100%;min-height:520px;border:0}}.scroll{{overflow-x:auto}}table{{width:100%;border-collapse:collapse;min-width:980px;font-size:14px}}th,td{{text-align:left;vertical-align:top;padding:11px;border-bottom:1px solid #bed5e6;line-height:1.45}}th{{background:var(--blue);color:#fff}}a{{font-size:16px;font-weight:750;color:#075ea8}}@media(max-width:700px){{main{{padding:12px}}object{{min-height:320px}}table{{min-width:820px}}}}</style></head><body><header><p class='warn'>{WARNING}</p><h1>Six real harness identities. Zero released cuts.</h1><p>R263 corrects the undercounted JST population, advances the 5025 source end to an exact #8 ring-terminal candidate, rejects stale colliding carrier placements, and screens a rotated non-overlapping arrangement.</p></header><main><div class='cards'><article class='card'><div class='big'>6</div><strong>carrier power harnesses</strong></article><article class='card'><div class='big'>9 / 18</div><strong>VHR housings / SVH contacts before scrap</strong></article><article class='card'><div class='big bad'>13</div><strong>stale-placement collisions</strong></article><article class='card'><div class='big'>0</div><strong>executed acceptance rows</strong></article></div><section><h2>Topology</h2><object type='image/svg+xml' data='harness-topology.svg'>Three protected branches, three limiter carriers and three DXL-star inputs.</object></section>{table('Harness schedule',harnesses,['harness_id','function','end_a_population','end_b_population','cut_length_mm','release_state'])}{table('Why the old placement is rejected',collisions,['finding_id','stale_reference','current_p07_reference','overlap_x_mm','overlap_y_mm','overlap_area_mm2','disposition'])}{table('Non-overlapping planning candidate',placements,['reference','axis','x_mm','y_mm','width_mm','height_mm','rotation_deg','planar_collision_count','release_state'])}{table('Evidence still required',holds,['hold_id','scope','state','closure_evidence'])}<section><h2>Controlled files</h2><p><a href='interface-control.csv'>24 endpoint rows</a> · <a href='cut-crimp-schedule.csv'>12 held conductor cuts</a> · <a href='harness-bom.csv'>corrected population</a> · <a href='route-lower-bound.csv'>route screens</a> · <a href='manufacturing-process.csv'>traveler</a> · <a href='acceptance-matrix.csv'>blank acceptance</a></p></section><p class='warn'>{WARNING}</p></main></body></html>"""


def update_bom() -> None:
    rows, fields = read_csv(BOM)
    by_id = {row["item_id"]: row for row in rows}
    by_id["BOM-056"].update(quantity="9", selection_basis="R263 corrects the minimum populated quantity to nine VHR-2N housings: three carrier-input ends plus both ends of three carrier-output harnesses. Process spares, receiving, assembly process, retention, thermal and procurement authority remain open.")
    by_id["BOM-057"].update(quantity="18 plus process scrap SELECTION REQUIRED", selection_basis="R263 corrects the minimum populated quantity to eighteen SVH-21T-P1.1 contacts for nine two-cavity housings. Exact process scrap, tooling, crimp geometry, pull/inspection, receiving, thermal and procurement authority remain open.")
    by_id["BOM-088"].update(manufacturer="Custom harness / exact candidates on hold", manufacturer_part_number="HAR-CIN-J1 / HAR-CIN-J2 / HAR-CIN-G1; PN18-8R-E to VHR-2N/SVH-21T-P1.1 on Belden 9918; cuts SELECTION REQUIRED", selection_basis="R263 defines three input harnesses and advances both 5025 source conductors to Panduit PN18-8R-E #8 ring-terminal candidates. Physical positive/return screw positions, received one-ring-per-screw fit, cut lengths, both termination processes, route, thermal/fault evidence, qualified review and authority remain open.")
    by_id["BOM-089"].update(manufacturer="Custom harness / exact candidates on hold", manufacturer_part_number="HAR-COUT-J1 / HAR-COUT-J2 / HAR-COUT-G1; VHR-2N/SVH-21T-P1.1 both ends on Belden 9918; cuts SELECTION REQUIRED", selection_basis="R263 defines three output harnesses with exact candidate populations at carrier JOUT1 and DXL-star JP1/JP2/JP3. Exact cuts, JST process, route, retention, thermal/fault evidence, qualified review and authority remain open.")
    if "BOM-109" not in by_id:
        rows.append({"item_id":"BOM-109","subsystem":"actuator_branch_source_ring_terminal","manufacturer":"Panduit","manufacturer_part_number":"PN18-8R-E","quantity":"1 package of 20; 6 production positions and 14 unallocated process/spare pieces","baseline_status":"exact_candidate_hold","selection_basis":"R263 exact #8 ring-terminal candidate for Belden 9918 at six Blue Sea 5025 branch positive/return screw interfaces. Exact physical screw assignments, tool/product approval, strip/crimp process, samples, pull/inspection, received fit, torque, thermal and procurement authority remain open."})
    write_csv(BOM, fields, sorted(rows, key=lambda row: int(row["item_id"].split("-")[1])))
    closure_fields = read_csv(CLOSURE)[1]
    write_csv(CLOSURE, closure_fields, [{"item_id": row["item_id"], **classification(row)} for row in sorted(rows, key=lambda row: int(row["item_id"].split("-")[1]))])


def update_release() -> None:
    data = json.loads(RELEASE.read_text(encoding="utf-8"))
    for product in data["current_products"]:
        if product.get("domain") in {"electrical","bill_of_materials","assembly"}:
            for value in (ID,CID):
                if value not in product.get("supporting_identifiers",[]):
                    product.setdefault("supporting_identifiers",[]).append(value)
            product["configuration_reconciliation"] = CID
            product["dxl_carrier_power_harness"] = ID
        if product.get("domain") == "bill_of_materials":
            product["system_group_count"] = 109
        if product.get("domain") == "electrical":
            product["dxl_carrier_power_harness_summary"] = "six harnesses / 24 endpoint rows / corrected 9 VHR + 18 SVH populated minimum / exact PN18-8R-E source candidate / 13 stale-placement collisions rejected / three zero-planar-collision rotated candidates / cuts and all physical acceptance open"
        if product.get("domain") == "bill_of_materials":
            product["release_state"] = "r263_109_group_bom_lot_a_purchase_blocker_carrier_harness_population_and_source_terminal_corrected_placement_route_process_physical_qualified_and_authority_evidence_open_no_complete_machine_procurement_release"
    RELEASE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def update_config() -> None:
    shutil.copytree(CFG0, CFG)
    current, fields = read_csv(CFG / "current-configuration-map.csv")
    row = next(row for row in current if row["record_id"] == "CFG-04")
    row.update(identifier=ID, source_path="release/hr-v0/dxl-protection-carrier-harness-p0.2/package-status.json", configuration_state="CURRENT CORRECTED CANDIDATE", release_boundary="six identities and exact populated minimum/source terminal candidates; placement, cuts, processes, physical evidence and authority open")
    write_csv(CFG / "current-configuration-map.csv", fields, current)
    supersession, fields = read_csv(CFG / "supersession-map.csv")
    supersession.extend([
        {"record_id":"SUP-39","prior_identifier":"HR-V0-DXL-PROT-CARRIER-HARNESS-P0.1","current_or_required_successor":ID,"disposition":"SUPERSEDED: quantity undercount and stale P0.6 placement basis corrected; historical evidence only","use_authorized":"NO","warning":WARNING},
        {"record_id":"SUP-40","prior_identifier":"HR-V0-CONFIG-REC-P0.26","current_or_required_successor":CID,"disposition":"SUPERSEDED BY R263 CONFIGURATION RECORD ONLY","use_authorized":"NO","warning":WARNING},
    ])
    write_csv(CFG / "supersession-map.csv", fields, supersession)
    bommap, fields = read_csv(CFG / "bom-integration-map.csv")
    for row in bommap:
        if row["item_id"] in {"BOM-088","BOM-089"}:
            row["bound_identifier"] = ID
    bommap.append({"item_id":"BOM-109","role":"six carrier-input source ring terminals","bound_identifier":ID,"closure_class":"exact_candidate_hold","physical_evidence":"OPEN","procurement_released":"NO","warning":WARNING})
    write_csv(CFG / "bom-integration-map.csv", fields, bommap)
    gates, fields = read_csv(CFG / "gate-impact.csv")
    for row in gates:
        if row["gate_id"] in {"EG-002","EG-003","EG-014","EG-018","EG-020"}:
            row["evidence_added"] += f"; {ID} six-identity harness, corrected population, source-terminal candidate and panel-collision reconciliation"
            row["remaining_evidence"] += "; received placement/sweep; exact circuit assignment; measured cuts; qualified termination processes; physical electrical/thermal/fault results; qualified acceptance and authority"
    write_csv(CFG / "gate-impact.csv", fields, gates)
    holds, fields = read_csv(CFG / "open-holds.csv")
    for index,row in enumerate(package_rows()["open-holds.csv"][1],176):
        holds.append({"hold_id":f"HOLD-{index:03d}","hold":f"{ID}: {row['scope']}","state":row["state"],"closure_evidence":row["closure_evidence"],"warning":WARNING})
    write_csv(CFG / "open-holds.csv", fields, holds)
    acceptance, fields = read_csv(CFG / "acceptance-matrix.csv")
    for index,row in enumerate(package_rows()["acceptance-matrix.csv"][1],217):
        acceptance.append({"acceptance_id":f"ACC-{index:03d}","criterion":f"{ID}: {row['criterion']}","execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":"","warning":WARNING})
    write_csv(CFG / "acceptance-matrix.csv", fields, acceptance)
    status = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    status.update({"identifier":CID,"round":ROUND,"date":DATE,"system_bom_groups":109,"current_records":45,"supersession_records":40,"bom_integration_records":30,"gate_records":11,"open_holds":len(holds),"acceptance_rows":len(acceptance),"dxl_carrier_power_harness":ID})
    (CFG / "package-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    (CFG / "README.md").write_text(f"# {CID}\n\n> **{WARNING}**\n\nR263 adds {ID}: six exact harness identities, corrected minimum JST population, an exact held #8 source-terminal candidate, rejection of thirteen stale-placement collisions and a zero-planar-collision rotated planning screen. Placement, cuts, process, physical/qualified evidence and all work authority remain open. {len(holds)} holds and {len(acceptance)} blank acceptances remain.\n",encoding="utf-8")
    (CFG / "index.html").write_text((REL / "index.html").read_text(encoding="utf-8"),encoding="utf-8")
    source_rows = []
    for row in current:
        path = ROOT / row["source_path"]
        source_rows.append({"source_path":row["source_path"],"sha256":sha(path),"role":row["role"],"warning":WARNING})
    write_csv(CFG / "source-hash-register.csv", ["source_path","sha256","role","warning"], source_rows)
    manifest(CFG)
    shutil.copytree(CFG, CFGR)
    manifest(CFGR)


def docs() -> None:
    (ROOT / "docs/hr-v0-dxl-protection-carrier-harness-p0.2.md").write_text(f"""# HR-V0 carrier power harness P0.2

> **{WARNING}**

R263 corrects the carrier-power harness definition against the current electrical and panel sources. It defines six harnesses and 24 endpoint rows, corrects the populated minimum from three to nine `VHR-2N` housings and from six to eighteen `SVH-21T-P1.1` contacts, and advances six Blue Sea 5025 branch interfaces to exact held Panduit `PN18-8R-E` #8 ring-terminal candidates.

The R161 carrier placements are not current: they intersect P0.7 rail, duct and node objects in thirteen positive-area rectangle collisions. P0.2 screens three 90-degree right-side placements with zero nominal planar intersections. Those are planning candidates only; enclosure depth, connector sweep, standoffs, bends, access, thermal behavior and received dimensions remain unproved.

No cut length is released. The twelve conductor rows remain `SELECTION REQUIRED` because direct centerline distances are only lower bounds and omit connector exits, duct paths, the Belden 20 mm bend radius, supports, service loops and termination allowances. JST and Panduit processing, physical 5025 circuit/return assignment, protection coordination, voltage drop, temperature, fault behavior, qualified review and all work authority remain open.

Interactive guide: [release package](../release/hr-v0/dxl-protection-carrier-harness-p0.2/index.html).
""",encoding="utf-8")
    (ROOT / "docs/reviews/2026-08-12-sol-r12-post-r263-status.md").write_text(f"""# Sol R12 status after R263

The supplied Sol analysis is the already controlled independent R12 review of the historical pre-correction baseline. It is not a new independent review round and the linked sandbox deliverables were not present in this workspace. Its reviewer-reported totals remain 18 BLOCKER, 30 MAJOR and 8 MINOR findings; 62/62 reviewed requirements draft; 106 historical electrical selection records unresolved; and zero approved executed verification records at that reviewed baseline.

R263 addresses only a newly reproduced repository defect in the carrier-power-harness chain: the system BOM undercounted the six-harness JST population and the R161 carrier placements collided with the later P0.7 panel layout. P0.2 corrects the populated minimum, defines exact held #8 source-ring candidates, rejects thirteen stale-placement collisions and provides a zero-planar-collision rotated planning screen.

No Sol blocker is closed. HR-V0 remains not build-ready and energization remains prohibited because placement depth/sweep, circuit assignment, cuts, crimp processes, protection, grounding, physical tests, functional-safety validation, qualified reviews and separate work authorization remain absent.

> **{WARNING}**
""",encoding="utf-8")
    (ROOT / "docs/reviews/2026-08-12-r263-independent-review-request.md").write_text(f"""# R263 independent review request

> **{WARNING}**

Independently audit `{ID}` against current JST, Belden, Blue Sea Systems and Panduit primary documentation and the current KiCad/panel sources. Recount all six harnesses, 24 endpoint rows, nine housings, eighteen production contacts and six source ring terminals. Reproduce all thirteen stale-placement collisions and verify that the three rotated planning rectangles have zero nominal intersections without treating a rectangle screen as physical fit. Check every pin/net, source screw assumption, conductor identity, lower-bound distance, open selection and warning. Confirm that no cut, crimp, torque, fuse, current, test, procurement or energization value is released and that no Sol R12 blocker receives closure.
""",encoding="utf-8")


def main() -> None:
    for source in SOURCES.values():
        if not source.is_file():
            raise FileNotFoundError(source)
    for directory in (ENG,REL,CFG,CFGR):
        if directory.exists():
            shutil.rmtree(directory)
    data = package_rows()
    ENG.mkdir(parents=True)
    for name,(fields,rows) in data.items():
        write_csv(ENG/name,fields,rows)
    (ENG/"harness-topology.svg").write_text(topology_svg(),encoding="utf-8")
    status = {"identifier":ID,"round":ROUND,"date":DATE,"harnesses":6,"conductors":12,"interface_rows":24,"vhr_2n_minimum_population":9,"svh_21t_p11_minimum_population":18,"pn18_8r_e_population":6,"stale_placement_collisions":13,"candidate_placements":3,"candidate_planar_collisions":sum(int(row["planar_collision_count"]) for row in data["placement-candidate.csv"][1]),"cut_lengths_released":False,"termination_process_released":False,"physical_article_exists":False,"physical_test_executed":False,"qualified_review_complete":False,"procurement_authorized":False,"fabrication_authorized":False,"assembly_authorized":False,"connection_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False,"source_hashes":{key:sha(path) for key,path in SOURCES.items()},"warning":WARNING}
    (ENG/"package-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    (ENG/"README.md").write_text(f"# {ID}\n\n> **{WARNING}**\n\nR263 corrects the six-harness population and stale panel placement. Exact cuts, termination processes, physical fit, protection evidence, qualified review and every work authority remain open.\n",encoding="utf-8")
    manifest(ENG)
    shutil.copytree(ENG,REL)
    (REL/"index.html").write_text(guide(data),encoding="utf-8")
    manifest(REL)
    update_bom()
    update_release()
    update_config()
    docs()
    print(f"Generated {ID}: 6 harnesses / 24 endpoints / 13 stale collisions / 0 released cuts")
    print(WARNING)


if __name__ == "__main__":
    main()
