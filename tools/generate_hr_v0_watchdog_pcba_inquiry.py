"""Generate the R132 watchdog-PCBA capability inquiry package.

Run with KiCad 10's bundled Python. The output is a review/inquiry package,
not CAM, a purchase request, or a fabrication/assembly release.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "electrical" / "kicad" / "project-button-v3" / "project-button-v3.kicad_pcb"
LAND_AUDIT = ROOT / "release" / "hr-v0" / "watchdog-pcb-land-pattern-audit-p0.1" / "land-pattern-audit.csv"
OUT = ROOT / "electrical" / "manufacturing" / "hr-v0-watchdog-pcba-rfi-p0.1"
WEB = ROOT / "release" / "hr-v0" / "watchdog-pcba-rfi-p0.1"
IDENTIFIER = "HR-V0-WD-PCBA-RFI-P0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"
THT = {"DC1", "JWP1", "JWF1", "JWH1"}


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def mm(value) -> str:
    if value is None:
        return "INHERITED / NONE ENCODED"
    return f"{pcbnew.ToMM(value):.3f}"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    WEB.mkdir(parents=True, exist_ok=True)
    board = pcbnew.LoadBoard(str(BOARD_PATH))
    with LAND_AUDIT.open(newline="", encoding="utf-8") as handle:
        audit = {row["reference"]: row for row in csv.DictReader(handle)}

    placements = []
    for footprint in sorted(board.GetFootprints(), key=lambda item: item.GetReference()):
        ref = footprint.GetReference()
        source = audit[ref]
        pos = footprint.GetPosition()
        process = "MECHANICAL_NPTH" if ref.startswith("MH") else ("MANUAL_THT_POST_REFLOW" if ref in THT else "SMD_REFLOW")
        placements.append({
            "reference": ref,
            "manufacturer_part": source["manufacturer_part"],
            "footprint": footprint.GetFPID().GetLibItemName(),
            "process_class": process,
            "process_authority": "PROPOSED ONLY - SUPPLIER AND PROJECT ACCEPTANCE REQUIRED" if process != "MECHANICAL_NPTH" else "MECHANICAL FEATURE - STACK SELECTION REQUIRED",
            "side": footprint.GetLayerName(),
            "board_x_mm": f"{pcbnew.ToMM(pos.x) - 20.0:.3f}",
            "board_y_mm": f"{pcbnew.ToMM(pos.y) - 20.0:.3f}",
            "rotation_deg": f"{footprint.GetOrientationDegrees():.3f}",
            "numbered_pad_count": str(sum(bool(p.GetNumber()) for p in footprint.Pads())),
            "local_mask_margin_mm": mm(footprint.GetLocalSolderMaskMargin()),
            "local_paste_margin_mm": mm(footprint.GetLocalSolderPasteMargin()),
            "local_paste_ratio": "INHERITED / NONE ENCODED" if footprint.GetLocalSolderPasteMarginRatio() is None else f"{footprint.GetLocalSolderPasteMarginRatio():.6f}",
            "land_audit_disposition": "R132_RECTANGULAR_SHAPE_CORRECTED" if ref.startswith("TP") else source["disposition"],
            "release_state": source["release_state"],
            "warning": WARNING,
        })
    write_csv(OUT / "placement-process-register.csv", placements)

    conformance_data = [
        ("PCBA-CONF-001","CDRV1;CDRV2;CDEC1",3,"Murata GRM21","0.95 x 0.95 mm lands; 2.05 mm centers","CONFORMS IF REFLOW SELECTED","NONE","select reflow; obtain exact-current-part lifecycle/approval sheet; assembler mask/stencil/paste acceptance","GRM21 land guide dated 2025-01-09","https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM21BC81H475KE11-01A.pdf"),
        ("PCBA-CONF-002","CFI1;CFI2",2,"TDK CGA3","0.70 x 0.70 mm lands; 1.40 mm centers","CONFORMS IF REFLOW SELECTED","NONE","select reflow; assembler mask/stencil/paste acceptance; DC-bias evidence","AC11010023; 2026-06","https://product.tdk.com/system/files/dam/doc/product/capacitor/ceramic/mlcc/specification/mlccspec_automotive_general_en.pdf"),
        ("PCBA-CONF-003","RHB1;RHP1;RSN1;RSN2;RSO1;RSO2;RPD1;RPD2",8,"Panasonic ERJ6","1.15 x 1.15 mm lands; 2.35 mm centers","CONFORMS TO GENERAL MANUFACTURER ENVELOPE","NONE","assembler mask/stencil/paste/process acceptance and first article","DMM0000COL17; 2025-12-24","https://industrial.panasonic.com/cdbs/www-data/pdf/RDM0000/DMM0000COL17.pdf"),
        ("PCBA-CONF-004","RTH1;RTH2",2,"Vishay MMA0204","1.40 x 1.55 mm lands; 3.00 mm centers","EXACT MATCH IF IPC-7351 REFLOW SELECTED","NONE","explicitly select IPC-7351 reflow basis; record received date code; assembler acceptance","28950 Rev 2022-07-12","https://www.vishay.com/doc/?28950="),
        ("PCBA-CONF-005","RW1;RW2",2,"Vishay CRCW1210","1.10 x 2.80 mm lands; 2.80 mm centers","EXACT MATCH IF REFLOW SELECTED","NONE","select reflow; assembler mask/stencil/paste acceptance; thermal/pulse evidence","20035 Rev 2026-04-14","https://www.vishay.com/docs/20035/dcrcwe3.pdf"),
        ("PCBA-CONF-006","UDRV1;UDRV2",2,"Texas Instruments TPL7407LPWR","1.50 x 0.45 mm; 0.65 mm pitch; 5.80 mm row centers","EXACT COPPER AND ORIENTATION MATCH","NONE","TI example is not assembler selection; accept mask/stencil/paste/reflow/AOI","SLRS066D Rev D 2016-03; PW0016A 4220204/B 2023-12","https://www.ti.com/lit/ds/symlink/tpl7407l.pdf"),
        ("PCBA-CONF-007","UFB1",1,"Texas Instruments ISO1212DBQ","1.60 x 0.41 mm; 0.635 mm pitch; 5.40 mm row centers","EXACT BOUNDING COPPER AND ORIENTATION MATCH","NONE","R0.05 corner is project-controlled; accept corner/mask/stencil/paste/reflow/AOI","SLLSEY7G Rev G 2025-02; DBQ0016A 4214846/A 2014-03","https://www.ti.com/lit/ds/symlink/iso1212.pdf"),
        ("PCBA-CONF-008","ISO1",1,"Vishay VO618A-4X017T","1.52 x 1.78 mm; 8.010 mm inner gap; 11.050 mm span","EXACT COPPER AND ORIENTATION MATCH","NONE","mask/paste/cleaning/system insulation and first-article spacing remain selection required","83432 Rev 2.1 2025-01-22","https://www.vishay.com/docs/83432/vo618a.pdf"),
        ("PCBA-CONF-009","TP1;TP2;TP3;TP4;TP5;TP6;TP7;TP8;TP9;TP10;TP11;TP12;TP13;TP14;TP15;TP16",16,"Harwin S1751-46R","rectangular 3.45 x 1.85 mm land; source positions unchanged","EXACT BOUNDING SIZE AND SHAPE MATCH IN PCB-P0.7","RECTANGLE APPLIED IN PCB-P0.7","assembler paste/mask/stencil acceptance; probe approach; vertical clearance; centroid/reel convention; first article","DRG 02202 issue 10 2023-02-15","https://content.harwin.com/asset/e4e6a5e1-de35-4a2b-8b49-ff06562cba9d/DRG-02202-Technical-Drawing-Datasheet-S1751R-pdf.pdf"),
    ]
    conformance = [{"group_id":i,"references":r,"quantity":q,"family":f,"current_geometry":g,"current_disposition":d,"current_geometry_correction":c,"remaining_evidence":e,"primary_document_revision_date":p,"source_url":u,"verified_date":"2026-08-09","warning":WARNING} for i,r,q,f,g,d,c,e,p,u in conformance_data]
    write_csv(OUT / "current-geometry-conformance-register.csv", conformance)

    providers = [
        {"provider_id":"PCBA-PROV-001","provider":"MacroFab","route":"North American manufacturing network","public_capability":"2-36 layer PCB; SMD/THT/hybrid/modules; SAC305 SMT; SN100 THT; no-clean standard; IPC-A-610 Class 2/3 inspection; J-STD-001 assembly; customer consignment","disposition":"PRIMARY CAPABILITY-INQUIRY CANDIDATE - NOT SELECTED","source_url":"https://www.macrofab.com/capabilities","source_state":"live official page; accessed 2026-08-09","missing_acceptance":"exact factory; laminate/finish; board class; land/mask/stencil; Pico module; mixed-alloy sequence; cleaning/ionic residue; traceability; first article; inspection/test; price and schedule","contact_state":"NOT CONTACTED","warning":WARNING},
        {"provider_id":"PCBA-PROV-002","provider":"NEOTech Westborough","route":"Westborough Massachusetts facility","public_capability":"about 30 minutes from Boston; quick-turn prototyping; NPI; low-to-medium-volume high-mix PCBA; system integration; ISO 9001/13485 and AS9100 listed","disposition":"LOCAL HIGH-MIX CAPABILITY-INQUIRY CANDIDATE - NOT SELECTED","source_url":"https://www.neotech.com/about-neo-tech/locations/westborough-massachusetts/","source_state":"live official page; accessed 2026-08-09","missing_acceptance":"prototype minimum; exact processes; material/finish; land/mask/stencil; THT/module assembly; cleanliness; traceability; first article; test; price and schedule","contact_state":"NOT CONTACTED","warning":WARNING},
        {"provider_id":"PCBA-PROV-003","provider":"Screaming Circuits","route":"Canby Oregon prototype service","public_capability":"prototype MOQ 1; turnkey/partial-turnkey/customer-supplied; cut tape/reels/trays/tubes; nonstandard jobs require direct review","disposition":"PROTOTYPE CAPABILITY-INQUIRY CANDIDATE - NOT SELECTED","source_url":"https://www.screamingcircuits.com/assets/pdfs/SC-ServicesOverview.pdf","source_state":"official services overview; published 2025; accessed 2026-08-09","missing_acceptance":"exact mixed SMD/THT/module process; board fabrication source; land/mask/stencil; cleanliness; traceability; inspection/test; first article; price and schedule","contact_state":"NOT CONTACTED","warning":WARNING},
        {"provider_id":"PCBA-PROV-004","provider":"Cirtronics","route":"Milford New Hampshire regional EMS","public_capability":"robotics/industrial PCBA; DFM support; automated inspection and test; IPC-A-610-trained technicians; ISO 9001/13485 listed; low-to-mid-volume support","disposition":"REGIONAL EMS CAPABILITY-INQUIRY CANDIDATE - NOT SELECTED","source_url":"https://www.cirtronics.com/pcb-assembly-manufacturer-new-hampshire/","source_state":"live official page; accessed 2026-08-09","missing_acceptance":"prototype minimum; exact processes; material/finish; land/mask/stencil; THT/module assembly; cleanliness; traceability; first article; test; price and schedule","contact_state":"NOT CONTACTED","warning":WARNING},
    ]
    write_csv(OUT / "provider-capability-screen.csv", providers)

    requirements_data = [
        ("PCBA-REQ-001","configuration","Bind response and any later quote to repository commit, PCB-P0.7, Electrical V3-P1.13 and this inquiry identifier.","written configuration acknowledgement"),
        ("PCBA-REQ-002","substitution","No component, footprint, laminate, finish, solder alloy, flux, cleaning or process substitution without written Project Button disposition.","supplier exception register"),
        ("PCBA-REQ-003","bare board","Review 160 x 100 x 1.6 mm, two-layer source; material, copper weight, finish, mask, legend, panelization, routing and electrical test remain selection required.","supplier DFM plus exact proposed stack/process"),
        ("PCBA-REQ-004","land review","Review all 46 references and the controlled land audit; explicitly accept or redline every alternate/process-dependent land.","reference-level signed DFM disposition"),
        ("PCBA-REQ-005","TI PW0016A","Review 2 x TPL7407LPWR, 1.50 x 0.45 mm pads, 0.65 mm pitch, 5.80 mm row centers and provisional 0.05 mm NSMD margin.","written land/stencil/mask acceptance"),
        ("PCBA-REQ-006","TI DBQ0016A","Review ISO1212DBQ, 1.60 x 0.41 mm pads, 0.635 mm pitch, 5.40 mm row centers and provisional 0.05 mm NSMD margin.","written land/stencil/mask acceptance"),
        ("PCBA-REQ-007","Vishay option 7","Review VO618A-4X017T 1.52 x 1.78 mm lands, 8.010 mm inner copper gap and 11.050 mm span; preserve the isolation region.","written land/mask/stencil/cleanliness acceptance"),
        ("PCBA-REQ-008","passives","Review Murata/TDK/Panasonic/Vishay manufacturer-traced lands and provisional 0.05 mm NSMD margin; explicitly select reflow for nine conditional placements and IPC-7351 reflow for RTH1/RTH2.","family/reference-level acceptance; process-basis disposition; received MMA0204 date-code record"),
        ("PCBA-REQ-009","Pico module","Confirm Raspberry Pi Pico SC0915 module presentation, reflow profile/fixture, enlarged paste zones, overhang, USB access and inspection method.","written module process and acceptance criteria"),
        ("PCBA-REQ-010","test points","Confirm 16 Harwin S1751-46R parts, 3.45 x 1.85 mm lands, placement convention and probe-access inspection.","written placement/inspection acceptance"),
        ("PCBA-REQ-011","THT sequence","Confirm post-reflow assembly for TSR 1-2450 and three Phoenix terminal blocks; specify selective/wave/manual method, fixtures, lead trim and underside envelope.","written THT traveler"),
        ("PCBA-REQ-012","solder system","State exact SMT and THT alloys, paste, flux, stencil thickness/aperture rules, thermal profile ownership and mixed-alloy compatibility.","controlled process specification"),
        ("PCBA-REQ-013","cleanliness","State no-clean/water-soluble process, cleaning, ionic-residue criterion, isolation-region handling and objective evidence.","cleanliness process and records"),
        ("PCBA-REQ-014","inspection","Provide AOI/manual criteria for polarity, bridges, opens, wetting, heel/toe fillets, Pico joints, terminal blocks and ISO1 spacing.","first-article inspection plan"),
        ("PCBA-REQ-015","traceability","Record PCB lot, component manufacturer/date/lot, substitutions, process route, nonconformances, rework and inspector.","lot traveler and traceability schema"),
        ("PCBA-REQ-016","rework","State allowed rework/repair limits, approval path and post-rework cleaning/inspection/test.","rework procedure and exception rule"),
        ("PCBA-REQ-017","bare-board test","Require netlist electrical test plus visual/dimensional inspection before assembly; test limits remain to be agreed.","bare-board certificate and raw result form"),
        ("PCBA-REQ-018","assembled test","Quote optional unpowered continuity/isolation/no-backfeed fixture support; no powered functional test is released.","fixture/data requirement response"),
        ("PCBA-REQ-019","first article","Separate first article from production; provide photos, AOI/manual records, measured critical geometry and all deviations before continuation.","first-article hold point"),
        ("PCBA-REQ-020","authorization","Do not fabricate or assemble from this inquiry. A later hash-bound CAM/BOM/placement/traveler release and written work authorization are mandatory.","supplier acknowledgement"),
    ]
    requirements = [{"requirement_id":i,"topic":t,"requirement":r,"evidence_needed":e,"state":"OPEN - SUPPLIER RESPONSE REQUIRED","warning":WARNING} for i,t,r,e in requirements_data]
    write_csv(OUT / "assembly-requirements.csv", requirements)

    questions_data = [
        ("PCBA-Q-001","all","Can you review this package without a portal upload or order and return a reference-level DFM disposition?"),
        ("PCBA-Q-002","bare board","What exact laminate, Tg, copper weight, board thickness tolerance, finish, mask and legend system would you propose?"),
        ("PCBA-Q-003","bare board","What panelization, tooling rails, fiducials, coupons, serialization and breakaway features are required?"),
        ("PCBA-Q-004","bare board","What IPC class and acceptability standards would govern bare board and assembly, and what objective records are supplied?"),
        ("PCBA-Q-005","lands","Will you accept every R89/R132 land verbatim; if not, identify reference, dimension, reason and proposed controlled change?"),
        ("PCBA-Q-006","mask","What solder-mask expansion and registration capability applies to each land family and the ISO1 isolation region?"),
        ("PCBA-Q-007","stencil","What stencil thickness, aperture geometry, area-ratio rule and step-stencil need applies across TI, Pico, passives, optocoupler and test points?"),
        ("PCBA-Q-008","SMT","State paste, alloy, flux, placement equipment, reflow profile method and profile-record availability."),
        ("PCBA-Q-009","Pico","Can you place/reflow SC0915 as a module using Raspberry Pi's official footprint, and how will hidden/edge joints be inspected?"),
        ("PCBA-Q-010","THT","State the exact post-reflow method for DC1/JWP1/JWF1/JWH1 and how terminal-block seating/torque loads are controlled."),
        ("PCBA-Q-011","mixed process","Are the proposed SMT and THT alloys/fluxes compatible with the sequence and later rework?"),
        ("PCBA-Q-012","cleanliness","What cleaning/no-clean process and ionic-residue evidence can be supplied, especially across ISO1?"),
        ("PCBA-Q-013","inspection","Which AOI, optical, X-ray or manual inspections cover each package family and polarity/orientation?"),
        ("PCBA-Q-014","test","Can you provide netlist bare-board electrical test and an unpowered assembled continuity/isolation fixture service?"),
        ("PCBA-Q-015","traceability","What component lot/date-code, PCB lot, process, inspection, deviation and rework traceability is standard or optional?"),
        ("PCBA-Q-016","sourcing","Can exact MPN-only sourcing and customer-consigned SC0915/other parts be enforced with no alternates?"),
        ("PCBA-Q-017","first article","Can one first article be held for Project Button review before remaining quantity proceeds?"),
        ("PCBA-Q-018","nonconformance","How are DFM exceptions, substitutions, deviations and rework requests presented for written approval?"),
        ("PCBA-Q-019","data","Which native KiCad, Gerber/drill, IPC-356, BOM, centroid, drawing and traveler inputs are required?"),
        ("PCBA-Q-020","data","Can every received file be bound to name, revision and SHA-256 in the work order/traveler?"),
        ("PCBA-Q-021","quantity","State prototype minimum, attrition quantities, overage rules and consignment packaging requirements."),
        ("PCBA-Q-022","commercial","State DFM/NRE, first-article, fabrication, assembly, test, documentation, shipping cost and lead time separately."),
        ("PCBA-Q-023","quality","Identify the actual facility, certifications, standards, responsible quality contact and record-retention period."),
        ("PCBA-Q-024","release boundary","Confirm that no upload, quote, acknowledgment or DFM response by itself starts fabrication or assembly."),
    ]
    questions = [{"question_id":i,"topic":t,"question":q,"response":"","state":"NOT SENT","warning":WARNING} for i,t,q in questions_data]
    write_csv(OUT / "capability-question-register.csv", questions)

    files_data = [
        ("PCBA-FILE-001","native KiCad board","project-button-v3.kicad_pcb","CURRENT SOURCE - WITHHELD FROM PROVIDER PENDING AUTHORIZATION"),
        ("PCBA-FILE-002","native KiCad schematic hierarchy","project-button-v3.kicad_sch plus 12 child sheets","CURRENT SOURCE - WITHHELD FROM PROVIDER PENDING AUTHORIZATION"),
        ("PCBA-FILE-003","Gerber/drill package","SELECTION REQUIRED","DOES NOT EXIST FOR CURRENT PCB-P0.7"),
        ("PCBA-FILE-004","IPC-356/netlist","SELECTION REQUIRED","NOT RELEASED"),
        ("PCBA-FILE-005","assembly BOM","exact board-only BOM with MPN and approved sourcing route","INTERNAL REVIEW CANDIDATE HR-V0-WD-PCBA-DATA-P0.1 - NOT RELEASED"),
        ("PCBA-FILE-006","centroid/XYRS","assembler convention plus written returned transform required","BOARD-ORIGIN PLACEMENT REFERENCE EXISTS - NOT ASSEMBLER-NORMALIZED OR RELEASED"),
        ("PCBA-FILE-007","assembly drawing","top/bottom polarity, orientation, special process and DNP notes","TOP REFERENCE MAP EXISTS FOR INTERNAL REVIEW - NOT RELEASED"),
        ("PCBA-FILE-008","fabrication drawing/stackup","material, copper, finish, mask, legend, panel and impedance choices","NOT RELEASED"),
        ("PCBA-FILE-009","traveler/inspection/test plan","lot, process, hold, FAI, rework, bare-board and unpowered assembly tests","NOT RELEASED"),
        ("PCBA-FILE-010","release manifest","file names, bytes and SHA-256 for one immutable supplier packet","NOT RELEASED"),
    ]
    files = [{"file_id":i,"artifact":a,"required_definition":d,"state":s,"warning":WARNING} for i,a,d,s in files_data]
    write_csv(OUT / "controlled-file-release-register.csv", files)

    holds_data = [
        ("PCBA-HOLD-001","provider and actual facility selection","OPEN","written capability/DFM responses plus quality/commercial review"),
        ("PCBA-HOLD-002","bare-board material/stack/finish","OPEN","exact selected laminate, thickness tolerance, copper, finish, mask, legend, panel and applicable standard"),
        ("PCBA-HOLD-003","all-reference land acceptance","PARTIAL","current 46-reference audit plus assembler reference-level acceptance/redlines"),
        ("PCBA-HOLD-004","mask/stencil/paste/reflow","OPEN","exact accepted process including ISO1/TI/Pico/passives/test points"),
        ("PCBA-HOLD-005","THT sequence and underside envelope","OPEN","accepted method, fixture, seating, solder/flux, trim, cleaning and measured lead envelope"),
        ("PCBA-HOLD-006","cleanliness/isolation system","OPEN","working-voltage/environment determination plus process/ionic evidence and qualified review"),
        ("PCBA-HOLD-007","component sourcing/traceability","PARTIAL","exact MPN register exists; facility sourcing, lot/date code, attrition and no-alternate controls open"),
        ("PCBA-HOLD-008","inspection and rework","OPEN","AOI/manual criteria, first-article plan, rework limits and record schema"),
        ("PCBA-HOLD-009","bare-board test","OPEN","agreed netlist method, acceptance criteria, raw records and certificate"),
        ("PCBA-HOLD-010","unpowered assembly test","OPEN","fixture, pin map, continuity/isolation/no-backfeed limits and approved work instruction"),
        ("PCBA-HOLD-011","mounting stack/panel interface","PARTIAL","R131 candidates exist; received THT envelope, exact hardware, drilling, torque and load proof open"),
        ("PCBA-HOLD-012","supplier data package","OPEN","R133 internal BOM/placement/map review data exist; accepted hash-bound CAM/BOM/normalized XYRS/drawings/traveler packet still requires prior holds and separate release"),
        ("PCBA-HOLD-013","independent/qualified review","OPEN","independent PCB/assembly and qualified electrical/insulation/mechanical disposition"),
        ("PCBA-HOLD-014","work authorization","OPEN","separate written quotation/upload/fabrication/assembly authorization for accepted immutable configuration"),
    ]
    holds = [{"hold_id":i,"subject":s,"status":st,"evidence_needed":e,"warning":WARNING} for i,s,st,e in holds_data]
    write_csv(OUT / "closure-holds.csv", holds)

    inspection_items = [
        "supplier/facility identity", "board lot and serialization", "board dimensions/thickness", "mount-hole diameter/position",
        "finish/mask/legend", "bare-board electrical test", "ISO1 copper/mask/contamination spacing", "UDRV1/UDRV2 lead joints",
        "UFB1 lead joints", "Pico module seating/joints", "passive placement/joints", "Harwin test-point placement/joints",
        "DC1 seating/polarity/lead trim", "JWP1 seating/orientation", "JWF1 seating/orientation", "JWH1 seating/orientation",
        "THT underside maximum protrusion", "flux/cleanliness evidence", "AOI/manual report", "rework/deviation record",
        "unpowered continuity", "unpowered isolation", "no-backfeed fixture result", "qualified receiving disposition",
    ]
    inspection = [{"record_id":f"PCBA-FAI-{index:03d}","inspection":item,"instrument_or_method":"","acceptance_criterion":"SELECTION REQUIRED","result":"","state":"NOT EXECUTED - NO ARTICLE","inspector":"","date":"","warning":WARNING} for index,item in enumerate(inspection_items,1)]
    write_csv(OUT / "first-article-receiving-template.csv", inspection)

    sources_data = [
        ("PCBA-SRC-001","Project Button","PCB-P0.7 native KiCad board","KiCad 10.0.5; repository state 2026-08-09",str(BOARD_PATH.relative_to(ROOT)).replace('\\','/'),"board geometry, placements and process split"),
        ("PCBA-SRC-002","Project Button","HR-V0-WD-LAND-P0.1 46-reference audit","R89; rechecked 2026-08-09",str(LAND_AUDIT.relative_to(ROOT)).replace('\\','/'),"exact part/footprint evidence and remaining holds"),
        ("PCBA-SRC-003","Texas Instruments","TPL7407L and PW0016A example land","SLRS066D Rev D 2016-03; 4220204/B 2023-12; rechecked 2026-08-09","https://www.ti.com/lit/ds/symlink/tpl7407l.pdf","UDRV1/UDRV2 land/orientation and process-example boundary"),
        ("PCBA-SRC-004","Texas Instruments","ISO1212 and DBQ0016A example land","SLLSEY7G Rev G 2025-02; 4214846/A 2014-03; rechecked 2026-08-09","https://www.ti.com/lit/ds/symlink/iso1212.pdf","UFB1 land/orientation and process-example boundary"),
        ("PCBA-SRC-005","Vishay","VO618A option-7 land","83432 Rev 2.1 2025-01-22; rechecked 2026-08-09","https://www.vishay.com/docs/83432/vo618a.pdf","ISO1 exact copper/orientation and absent mask/paste guidance"),
        ("PCBA-SRC-006","Murata","GRM21 same-series land guidance","2025-01-09; rechecked 2026-08-09","https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM21BC81H475KE11-01A.pdf","three conditional reflow lands"),
        ("PCBA-SRC-007","TDK","CGA3 land guidance","AC11010023; 2026-06; rechecked 2026-08-09","https://product.tdk.com/system/files/dam/doc/product/capacitor/ceramic/mlcc/specification/mlccspec_automotive_general_en.pdf","two conditional reflow lands"),
        ("PCBA-SRC-008","Panasonic Industry","ERJ surface-mount resistor land pattern","DMM0000COL17; 2025-12-24; rechecked 2026-08-09","https://industrial.panasonic.com/cdbs/www-data/pdf/RDM0000/DMM0000COL17.pdf","eight general-envelope lands"),
        ("PCBA-SRC-009","Vishay","MMA0204 recommended pads","28950 Rev 2022-07-12; rechecked 2026-08-09","https://www.vishay.com/doc/?28950=","two IPC-7351 reflow conditional lands"),
        ("PCBA-SRC-010","Vishay","CRCW1210 family and reflow pad","20035 Rev 2026-04-14; rechecked 2026-08-09","https://www.vishay.com/docs/20035/dcrcwe3.pdf","two conditional reflow lands"),
        ("PCBA-SRC-011","Harwin","S1751-XXR recommended land","DRG 02202 issue 10 2023-02-15; rechecked 2026-08-09","https://content.harwin.com/asset/e4e6a5e1-de35-4a2b-8b49-ff06562cba9d/DRG-02202-Technical-Drawing-Datasheet-S1751R-pdf.pdf","sixteen rectangular test-point copper lands"),
        ("PCBA-SRC-012","MacroFab","Capabilities","live page; accessed 2026-08-09","https://www.macrofab.com/capabilities","public fabrication, assembly, process, inspection and consignment screen"),
        ("PCBA-SRC-013","MacroFab","Capabilities PDF","published 2025; accessed 2026-08-09","https://macrofab.com/assets/uploads/documents/macrofab-capabilities.pdf","formal public capability summary"),
        ("PCBA-SRC-014","NEOTech","Westborough Massachusetts facility","live page; accessed 2026-08-09","https://www.neotech.com/about-neo-tech/locations/westborough-massachusetts/","local quick-turn/NPI/high-mix PCBA screen"),
        ("PCBA-SRC-015","Screaming Circuits","Overview of Assembly Services","published 2025; accessed 2026-08-09","https://www.screamingcircuits.com/assets/pdfs/SC-ServicesOverview.pdf","prototype MOQ, supply and nonstandard review screen"),
        ("PCBA-SRC-016","Cirtronics","New Hampshire PCBA manufacturing","live page; accessed 2026-08-09","https://www.cirtronics.com/pcb-assembly-manufacturer-new-hampshire/","regional robotics/high-mix/inspection screen"),
    ]
    sources = [{"source_id":i,"organization":o,"record":r,"revision_date":d,"locator":l,"use":u,"warning":WARNING} for i,o,r,d,l,u in sources_data]
    write_csv(OUT / "source-register.csv", sources)

    counts = {"footprints":len(placements),"smd":sum(r["process_class"]=="SMD_REFLOW" for r in placements),"tht":sum(r["process_class"]=="MANUAL_THT_POST_REFLOW" for r in placements),"mechanical":sum(r["process_class"]=="MECHANICAL_NPTH" for r in placements)}
    status = {
        "identifier": IDENTIFIER, "round": "R132", "current_board": "PCB-P0.7", "board_changed": True,
        "board_sha256": hashlib.sha256(BOARD_PATH.read_bytes()).hexdigest(), "counts": counts, "current_conformance_groups": len(conformance), "current_conformance_references": sum(int(row["quantity"]) for row in conformance), "providers_screened": len(providers), "questions": len(questions), "holds": len(holds),
        "provider_selected": False, "provider_contacted": False, "files_uploaded": False, "quote_requested": False,
        "cam_released": False, "fabrication_authorized": False, "assembly_authorized": False,
        "physical_article_exists": False, "energization_authorized": False, "warning": WARNING,
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    provider_cards = "".join(f'<article class="card"><span>{p["disposition"]}</span><h3>{p["provider"]}</h3><p>{p["public_capability"]}</p><p><strong>Contact state:</strong> {p["contact_state"]}</p><p><strong>Still needed:</strong> {p["missing_acceptance"]}</p></article>' for p in providers)
    html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Project Button PCBA inquiry</title><style>
:root{{--sky:#dff3ff;--blue:#07579f;--dark:#082f5b;--gold:#f4bd28;--ink:#10253d;--paper:#f8fcff}}*{{box-sizing:border-box}}body{{margin:0;font:17px/1.55 system-ui,sans-serif;color:var(--ink);background:var(--paper)}}header,main,footer{{max-width:1180px;margin:auto;padding:28px}}header{{background:var(--sky);border-bottom:8px solid var(--gold)}}.warning{{background:var(--dark);color:white;padding:14px 18px;font-weight:800}}.meta{{font-size:14px}}h1{{font-size:clamp(34px,6vw,68px);line-height:1.05;color:var(--dark)}}h2{{font-size:clamp(26px,4vw,40px);color:var(--blue)}}.metrics,.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px}}.metric,.card{{background:white;border:2px solid var(--blue);border-radius:14px;padding:20px;box-shadow:6px 6px 0 var(--gold)}}.metric strong{{display:block;font-size:32px;color:var(--dark)}}.card span{{display:inline-block;font-size:14px;font-weight:800;background:var(--gold);padding:5px 8px}}.flow{{display:flex;align-items:center;gap:12px;overflow-x:auto;padding:18px 2px}}.node{{min-width:205px;border:2px solid var(--blue);background:white;padding:16px;border-radius:12px}}.arrow{{font-size:28px;color:var(--blue)}}a{{color:var(--blue);font-weight:700}}footer{{font-size:14px;border-top:2px solid var(--blue);margin-top:28px}}@media(max-width:600px){{body{{font-size:16px}}header,main,footer{{padding:20px}}.flow{{align-items:stretch;flex-direction:column}}.arrow{{transform:rotate(90deg);align-self:center}}}}
</style></head><body><header><div class="warning">{WARNING}</div><p class="meta">{IDENTIFIER} · R132 · 2026-08-09</p><h1>A real assembler must answer before CAM exists.</h1><p>PCB-P0.7 retains the controlled R89 lands and corrects the sixteen Harwin copper shapes. This package converts the remaining assembly-process ambiguity into an exact, answerable capability inquiry without uploading files or starting work.</p></header><main>
<section><h2>The controlled board</h2><div class="metrics"><div class="metric"><strong>{counts['footprints']}</strong>footprints</div><div class="metric"><strong>{counts['smd']}</strong>SMD placements</div><div class="metric"><strong>{counts['tht']}</strong>post-reflow THT</div><div class="metric"><strong>{counts['mechanical']}</strong>NPTH holes</div></div><div class="flow"><div class="node">PCB-P0.7 native source<br><small>160 × 100 × 1.6 mm · 2 layers</small></div><div class="arrow">→</div><div class="node">Reference-level DFM<br><small>lands, mask, stencil, Pico and THT</small></div><div class="arrow">→</div><div class="node">Written redlines<br><small>no silent substitutions</small></div><div class="arrow">→</div><div class="node">Later release decision<br><small>separate authorization mandatory</small></div></div></section>
<section><h2>Capability routes—not selected suppliers</h2><div class="grid">{provider_cards}</div></section>
<section><h2>What the packet controls</h2><div class="grid"><article class="card"><h3>Every placement</h3><p>Reference, exact part, footprint, side, board-relative coordinate, rotation, pad count and local mask/paste settings.</p></article><article class="card"><h3>Twenty requirements</h3><p>Configuration binding, no-substitution, lands, solder system, cleanliness, inspection, traceability, test and first article.</p></article><article class="card"><h3>Twenty-four questions</h3><p>Blank response cells and NOT SENT state prevent a web page from masquerading as supplier evidence.</p></article><article class="card"><h3>Fourteen holds</h3><p>Provider, process, insulation, testing, data release, qualified review and work authorization remain open or partial.</p></article></div></section>
<section><h2>Evidence files</h2><p><a href="../../../electrical/manufacturing/hr-v0-watchdog-pcba-rfi-p0.1/placement-process-register.csv">Placement/process register</a> · <a href="../../../electrical/manufacturing/hr-v0-watchdog-pcba-rfi-p0.1/current-geometry-conformance-register.csv">Current geometry reconciliation</a> · <a href="../../../electrical/manufacturing/hr-v0-watchdog-pcba-rfi-p0.1/assembly-requirements.csv">Assembly requirements</a> · <a href="../../../electrical/manufacturing/hr-v0-watchdog-pcba-rfi-p0.1/capability-question-register.csv">Question register</a> · <a href="../../../electrical/manufacturing/hr-v0-watchdog-pcba-rfi-p0.1/controlled-file-release-register.csv">File-release register</a> · <a href="../../../electrical/manufacturing/hr-v0-watchdog-pcba-rfi-p0.1/first-article-receiving-template.csv">First-article template</a> · <a href="../../../docs/hr-v0-watchdog-pcba-capability-inquiry-p0.1.md">Controlled record</a></p></section></main><footer>{WARNING}. No provider has been contacted or selected. No file has been uploaded. No quote, CAM, fabrication, assembly, test, connection or energization is authorized.</footer></body></html>'''
    (WEB / "index.html").write_text(html, encoding="utf-8")

    print(f"Generated {IDENTIFIER}: {counts['smd']} SMD, {counts['tht']} THT, {counts['mechanical']} NPTH; {len(providers)} provider routes; {len(holds)} holds")
    print("No provider contact, upload, quote, CAM, fabrication, assembly or energization authorization exists")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
