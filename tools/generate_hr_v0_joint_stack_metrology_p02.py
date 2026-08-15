#!/usr/bin/env python3
"""Generate R254 task-specific HR-V0 joint-stack metrology P0.2."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "test-fixtures/hr-v0/joint-stack-metrology-p0.2"
REL = ROOT / "release/hr-v0/joint-stack-metrology-p0.2"
CFG0 = ROOT / "configuration/hr-v0-config-reconciliation-p0.17"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.18"
CFGR = ROOT / "release/hr-v0/configuration-reconciliation-p0.18"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
ID = "HR-V0-JOINT-MET-P0.2"


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
        writer.writerows({key: row.get(key, "") for key in fields} for row in rows)


def warned(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [dict(row, warning=WARNING) for row in rows]


def write_manifest(directory: Path) -> None:
    rows = []
    for path in sorted(p for p in directory.rglob("*") if p.is_file() and p.name != "file-manifest.csv"):
        rows.append({"path": path.relative_to(directory).as_posix(), "bytes": path.stat().st_size, "sha256": sha(path)})
    write_csv(directory / "file-manifest.csv", ["path", "bytes", "sha256"], rows)


def table(title: str, rows: list[dict[str, object]], fields: list[str], method_field: str = "") -> str:
    head = "".join(f"<th>{html.escape(f.replace('_', ' ').title())}</th>" for f in fields)
    body = []
    for row in rows:
        method = str(row.get(method_field, "")) if method_field else ""
        cells = "".join(f"<td>{html.escape(str(row.get(f, '')))}</td>" for f in fields)
        body.append(f'<tr data-method="{html.escape(method)}">{cells}</tr>')
    return f"<section><h2>{html.escape(title)}</h2><div class=scroll><table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table></div></section>"


def guide(methods, applicability, phases, hsi, holds, operations, uncertainty) -> str:
    buttons = "".join(f'<button data-filter="{m["method_id"]}">{m["method_id"]}</button>' for m in methods)
    return f"""<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>
<title>HR-V0 joint-stack metrology P0.2</title><style>
:root{{--sky:#dff3ff;--blue:#092f57;--gold:#f4bd27;--ink:#102338;--paper:#f8fbfe;--line:#8eb9d8}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.15vw,19px)/1.55 system-ui,sans-serif}}
header{{padding:clamp(24px,5vw,68px);background:linear-gradient(135deg,var(--sky),#fff);border-bottom:8px solid var(--gold)}}main{{max-width:1500px;margin:auto;padding:24px}}
h1{{font-size:clamp(34px,5vw,72px);line-height:1.05;color:var(--blue);margin:.2em 0}}h2{{color:var(--blue);font-size:clamp(24px,2.4vw,36px)}}
.warn{{background:#fff4c7;border:3px solid var(--gold);padding:16px;font-weight:800}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;margin:24px 0}}
.card,section{{background:#fff;border:2px solid var(--line);border-radius:14px;padding:18px;margin:18px 0}}.big{{font-size:2rem;font-weight:800;color:var(--blue)}}
button{{font:inherit;font-weight:750;padding:10px 14px;margin:5px;border:2px solid var(--blue);border-radius:999px;background:#fff;color:var(--blue)}}button.active{{background:var(--blue);color:#fff}}
.scroll{{overflow:auto}}table{{width:100%;border-collapse:collapse;min-width:860px;font-size:14px}}th,td{{text-align:left;vertical-align:top;padding:10px;border-bottom:1px solid #bed5e6}}th{{background:var(--blue);color:#fff;position:sticky;top:0}}
.note{{font-size:14px}}@media(max-width:700px){{main{{padding:12px}}table{{font-size:14px}}}}
</style></head><body><header><p class=warn>{WARNING}</p><h1>Joint-stack metrology P0.2</h1><p>Five task-specific methods. Zero executed measurements. P0.2 fixture use is limited, not universal.</p></header><main>
<div class=cards><div class=card><div class=big>5</div>measurement methods</div><div class=card><div class=big>20</div>HSI records routed</div><div class=card><div class=big>40</div>uncertainty inputs open</div><div class=card><div class=big>0</div>authorizations or results</div></div>
<section><h2>Filter by method</h2><button class=active data-filter=ALL>All</button>{buttons}<p class=note>Filtering changes the visible planning rows only; it does not authorize work.</p></section>
{table('Method register', methods, ['method_id','measurement','article_state','fixture_or_support','datum_realization','instrument_class','overall_uncertainty_boundary','execution_state'], 'method_id')}
{table('P0.2 fixture applicability', applicability, ['method_id','p02_fixture_disposition','reason','required_successor_or_addition','use_authorized'], 'method_id')}
{table('Phase and authorization gates', phases, ['phase_id','scope','entry_gate','exit_evidence','authorization_state','execution_state'])}
{table('HSI routing', hsi, ['hsi_id','method_id','evidence_scope','closure_boundary','state'], 'method_id')}
{table('Open hold points', holds, ['hold_id','method_id','hold','closure_evidence','state'], 'method_id')}
{table('Operation sequence', operations, ['operation_id','phase_id','method_id','operation','entry_hold','authorization','execution_state'], 'method_id')}
{table('Uncertainty inputs', uncertainty, ['budget_id','method_id','contributor','numeric_input','distribution','divisor','sensitivity','standard_uncertainty','state'], 'method_id')}
<section><h2>Release boundary</h2><p>This guide is an execution contract, not measurement evidence. No article has been ordered, received, assembled or measured. It grants no procurement, fabrication, assembly, connection, powered-test, motion, energization or safety authority.</p></section>
</main><script>const buttons=[...document.querySelectorAll('button[data-filter]')];buttons.forEach(b=>b.onclick=()=>{{buttons.forEach(x=>x.classList.remove('active'));b.classList.add('active');const f=b.dataset.filter;document.querySelectorAll('tr[data-method]').forEach(r=>r.hidden=f!=='ALL'&&r.dataset.method!==f)}});</script></body></html>"""


def main() -> None:
    for path in (OUT, REL, CFG, CFGR):
        if path.exists():
            shutil.rmtree(path)
    OUT.mkdir(parents=True)

    methods = [
        {"method_id":"JSM2-M01","measurement":"Loose-part depth, face and feature-coordinate metrology","article_state":"Received, quarantined, loose and unthreaded","fixture_or_support":"Qualified nonmarring free-state support; three-point rest or provider-selected nest; no measured face obstructed","datum_realization":"Part-specific external datums from received geometry; S102 edges are not datums unless qualified","instrument_class":"CMM or surface plate/height/depth system","overall_uncertainty_boundary":"R84 provisional U <= 0.05 mm screening boundary; component budget not calculable","execution_state":"NOT EXECUTED"},
        {"method_id":"JSM2-M02","measurement":"Assembled axial stack and joint-axis realization","article_state":"Temporary threaded stack only after exact signed instruction","fixture_or_support":"Independent support that leaves measured outer faces accessible and does not load connector/case/threads","datum_realization":"External construction from accepted cylindrical/center features on output and idler sides; P0.2 frame alone cannot realize axis","instrument_class":"CMM or surface plate plus accepted axis artifacts","overall_uncertainty_boundary":"R84 provisional U <= 0.05 mm screening boundary; component budget not calculable","execution_state":"NOT EXECUTED"},
        {"method_id":"JSM2-M03","measurement":"External mechanical angle and bidirectional unpowered backlash","article_state":"Temporary stack restrained against gravity; actuator unpowered and unconnected","fixture_or_support":"Fixed S102 datum candidate plus separate moving-angle reference and independent gravity restraint","datum_realization":"Calibrated external rotary/optical reference; no actuator encoder value","instrument_class":"Rotary table, autocollimator or qualified optical angle system","overall_uncertainty_boundary":"R84 provisional U <= 0.20 deg screening boundary; component budget not calculable","execution_state":"NOT EXECUTED"},
        {"method_id":"JSM2-M04","measurement":"Both-side envelope and occlusion-controlled geometry scan","article_state":"Loose or temporary stack in at least two reviewed orientations","fixture_or_support":"Low-occlusion reconfigurable support with reference artifact/fiducials; P0.2 frame not sole scan fixture","datum_realization":"Registered common reference artifact with reported residuals and orientation transforms","instrument_class":"Qualified 3D scanner; screening only","overall_uncertainty_boundary":"R84 <= 0.25 mm point spacing and <= 0.50 mm verified volumetric error; not tolerance acceptance","execution_state":"NOT EXECUTED"},
        {"method_id":"JSM2-M05","measurement":"Loose and assembled mass","article_state":"Received loose articles first; assembled stack only after assembly authorization","fixture_or_support":"Tared nonmarring tray or container only","datum_realization":"Calibrated balance zero/tare; immutable article/configuration identity","instrument_class":"Calibrated balance","overall_uncertainty_boundary":"R84 provisional 0.1 g resolution and U <= 0.5 g screening boundary; budget not calculable","execution_state":"NOT EXECUTED"},
    ]
    applicability = [
        {"method_id":"JSM2-M01","p02_fixture_disposition":"NOT APPLICABLE","reason":"A universal S102 locator obstructs or biases loose-part free-state measurements","required_successor_or_addition":"Part-specific nonmarring support and accepted datum plan","use_authorized":"NO"},
        {"method_id":"JSM2-M02","p02_fixture_disposition":"CONDITIONAL SUPPORT CANDIDATE ONLY","reason":"Rank-6 S102 location does not itself realize the output-to-idler joint axis or protect measured faces","required_successor_or_addition":"External axis-realization method, access proof, restraint/load review and physical FAI","use_authorized":"NO"},
        {"method_id":"JSM2-M03","p02_fixture_disposition":"CONDITIONAL FIXED-DATUM CANDIDATE ONLY","reason":"It can orient S102 but provides neither moving-angle reference nor gravity restraint","required_successor_or_addition":"Independent angle reference, counterbalance/restraint and qualified contact-load review","use_authorized":"NO"},
        {"method_id":"JSM2-M04","p02_fixture_disposition":"NOT ACCEPTABLE AS SOLE FIXTURE","reason":"The frame and contacts create occlusion; both sides require controlled re-fixturing","required_successor_or_addition":"Low-occlusion multi-orientation support, fiducial artifact and registration validation","use_authorized":"NO"},
        {"method_id":"JSM2-M05","p02_fixture_disposition":"NOT APPLICABLE","reason":"Fixture mass would add needless tare and stability uncertainty","required_successor_or_addition":"Tared tray/container and accepted balance method","use_authorized":"NO"},
    ]
    phases = [
        {"phase_id":"JSM2-PH0","scope":"Work authorization, exact article acquisition and receiving","entry_gate":"Program-owner written authorization; supplier identity resolved","exit_evidence":"Received/quarantined identities, counts, photos, source records","authorization_state":"NOT AUTHORIZED","execution_state":"NOT EXECUTED"},
        {"phase_id":"JSM2-PHL","scope":"Loose-part metrology and loose mass","entry_gate":"PH0 complete; instruments/calibration/uncertainty and M01/M05 supports accepted; zero source/power equipment","exit_evidence":"Raw dimensional and mass records with hashes and qualified disposition","authorization_state":"NOT AUTHORIZED","execution_state":"NOT EXECUTED"},
        {"phase_id":"JSM2-PHA","scope":"Temporary threaded assembly","entry_gate":"Exact screws, depths, spacers, torque, reuse, locking and stop-work instruction signed","exit_evidence":"Frozen as-assembled manifest, photographs and witness record","authorization_state":"NOT AUTHORIZED","execution_state":"NOT EXECUTED"},
        {"phase_id":"JSM2-PHM","scope":"Assembled axial, angle/backlash, envelope and mass methods","entry_gate":"PHA complete; each M02-M05 fixture/method and configuration accepted separately","exit_evidence":"Raw results, uncertainty, transforms, photos, hashes and qualified dispositions","authorization_state":"NOT AUTHORIZED","execution_state":"NOT EXECUTED"},
        {"phase_id":"JSM2-PHT","scope":"Controlled teardown and re-quarantine","entry_gate":"All authorized measurements stopped and evidence completeness checked","exit_evidence":"Teardown condition, separated kit inventory, nonconformance and disposition","authorization_state":"NOT AUTHORIZED","execution_state":"NOT EXECUTED"},
    ]
    hsi_map = {
        1:("JSM2-PH0","Received actuator identities only"),2:("JSM2-PH0","Received frame/horn identities only"),
        3:("JSM2-M01 + JSM2-M02","Received and assembled axial geometry"),4:("JSM2-M01 + JSM2-M02","Received and assembled axial geometry"),5:("JSM2-M01 + JSM2-M02","Received and assembled axial geometry"),6:("JSM2-M01 + JSM2-M02","Received and assembled axial geometry"),
        7:("JSM2-M04","Envelope screening; cable/guard remains external"),8:("JSM2-M04","Envelope screening; cable/guard remains external"),
        9:("JSM2-M01","Loose-part attachment geometry"),10:("JSM2-M01","Loose-part attachment geometry"),11:("JSM2-M01","Loose-part attachment geometry"),12:("JSM2-M01","Loose-part attachment geometry"),
        13:("JSM2-M03","External unpowered angle/backlash only"),14:("JSM2-M03","External unpowered angle/backlash only"),
        15:("EXTERNAL","Harness topology/strain relief not present"),16:("EXTERNAL","Guard/tool integration not present"),
        17:("JSM2-M05","Measured mass input; COM/inertia remains external"),18:("JSM2-M05","Measured mass input; COM/inertia remains external"),
        19:("EXTERNAL","Dynamic/structural evidence not present"),20:("EXTERNAL","Bumper/supplier DFM/FAI not present"),
    }
    hsi = [{"hsi_id":f"HSI-{i:03d}","method_id":method,"evidence_scope":scope,"closure_boundary":"Requires received execution, immutable raw evidence, uncertainty and qualified acceptance; EXTERNAL rows cannot close here","state":"OPEN"} for i,(method,scope) in hsi_map.items()]
    hold_specs = [
        ("HP01","ALL","Written campaign and purchase authorization"),("HP02","ALL","Received identities, quarantine and source reconciliation"),("HP03","ALL","Instrument calibration, capability and uncertainty method accepted"),
        ("HP04","JSM2-M01","Loose-part support, datum and no-damage method accepted"),("HP05","JSM2-M05","Balance, tare, stability and article-identity method accepted"),
        ("HP06","JSM2-M02","Exact temporary-assembly hardware, torque, reuse, locking and stop-work instruction signed"),("HP07","JSM2-M02","Axial support/access and external axis-realization method accepted"),
        ("HP08","JSM2-M03","Angle reference, restraint/counterbalance and contact-load method accepted"),("HP09","JSM2-M04","Low-occlusion supports, pose set, fiducials and registration validation accepted"),
        ("HP10","ALL","Zero electrical source, actuator connection and power equipment verified"),("HP11","ALL","Frozen article/configuration/fixture/transform manifest"),("HP12","ALL","Raw evidence complete; teardown and qualified disposition accepted"),
    ]
    holds = [{"hold_id":f"JSM2-{n}","method_id":m,"hold":d,"closure_evidence":"Dated controlled record with exact article/method, result, evidence URI, qualified reviewer and approval","state":"OPEN"} for n,m,d in hold_specs]
    opspec = [
        ("PH0","ALL","Confirm written scope and stop-work authority","HP01"),("PH0","ALL","Resolve supplier identity and acquire exact six-article batch","HP01"),("PH0","ALL","Receive, quarantine, photograph and inventory","HP02"),("PH0","ALL","Reconcile live manufacturer sources and received markings","HP02"),("PH0","ALL","Qualify instruments, calibration and uncertainty plans","HP03"),
        ("PHL","JSM2-M01","Review and accept loose-part support/datum plan","HP04"),("PHL","JSM2-M01","Measure loose depths, faces and coordinates","HP04"),("PHL","JSM2-M01","Repeat reseat series and preserve raw dimensional evidence","HP04"),("PHL","JSM2-M05","Tare and measure each loose article mass","HP05"),("PHL","ALL","Review loose evidence and authorize stop or continuation","HP03"),
        ("PHA","JSM2-M02","Approve exact temporary-assembly instruction","HP06"),("PHA","JSM2-M02","Assemble J1 and J2 stacks without electrical connection","HP06"),("PHA","ALL","Freeze as-assembled identities and configuration","HP11"),
        ("PHM","JSM2-M02","Accept axial support/access and axis realization","HP07"),("PHM","JSM2-M02","Measure outer faces against externally realized joint axis","HP07"),("PHM","JSM2-M03","Accept angle reference and independent gravity restraint","HP08"),("PHM","JSM2-M03","Execute repeated bidirectional external angle/backlash series","HP08"),("PHM","JSM2-M04","Scan first low-occlusion orientation","HP09"),("PHM","JSM2-M04","Re-fixture and scan second orientation","HP09"),("PHM","JSM2-M04","Register scans and report residuals/transforms","HP09"),("PHM","JSM2-M05","Tare and measure frozen assembled-stack mass","HP05"),
        ("PHT","ALL","Completeness check, controlled teardown, condition inspection and re-quarantine","HP12"),
    ]
    operations = [{"operation_id":f"JSM2-OP-{i:03d}","phase_id":f"JSM2-{p}","method_id":m,"operation":op,"entry_hold":f"JSM2-{hp}","authorization":"NONE","execution_state":"NOT EXECUTED"} for i,(p,m,op,hp) in enumerate(opspec,1)]
    contributors = ["instrument calibration","resolution and quantization","repeatability","fixture reseat or support","datum or axis realization","environment and temperature","probe, scan or model fit","operator and processing"]
    uncertainty = []
    for method in methods:
        for i, contributor in enumerate(contributors, 1):
            uncertainty.append({"budget_id":f"{method['method_id']}-U{i:02d}","method_id":method["method_id"],"contributor":contributor,"numeric_input":"","distribution":"","divisor":"","sensitivity":"","standard_uncertainty":"","state":"SELECTION REQUIRED"})
    acceptance = [{"acceptance_id":f"JSM2-ACC-{i:02d}","criterion":hold[2],"execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":""} for i,hold in enumerate(hold_specs,1)]
    sources = [
        {"source_id":"JSM2-SRC-01","authority":"Project Button","title":"Joint-stack metrology P0.1 historical campaign","revision_or_date":"HR-V0-JOINT-MET-P0.1 / 2026-08-08","path_or_url":"docs/hr-v0-joint-stack-metrology-p0.1.md","sha256":sha(ROOT/"docs/hr-v0-joint-stack-metrology-p0.1.md"),"use":"Preserved requirements and provisional screening boundaries; superseded for execution planning"},
        {"source_id":"JSM2-SRC-02","authority":"Project Button","title":"Rank-6 joint-stack fixture candidate","revision_or_date":"HR-V0-JOINT-STACK-FIXTURE-P0.2 / 2026-08-11","path_or_url":"docs/hr-v0-joint-stack-fixture-p0.2.md","sha256":sha(ROOT/"docs/hr-v0-joint-stack-fixture-p0.2.md"),"use":"Applicability assessed; no universal-use inference"},
        {"source_id":"JSM2-SRC-03","authority":"NIST","title":"Technical Note 1297","revision_or_date":"1994 edition; official page rechecked 2026-08-11","path_or_url":"https://www.nist.gov/pml/nist-technical-note-1297","sha256":"","use":"Uncertainty reporting framework; no project uncertainty inferred"},
        {"source_id":"JSM2-SRC-04","authority":"ASME","title":"Y14.43 Dimensioning and Tolerancing Principles for Gages and Fixtures","revision_or_date":"2011 (R2020); official catalog record rechecked 2026-08-11","path_or_url":"https://www.asme.org/codes-standards/find-codes-standards/y14-43-dimensioning-tolerancing-principles-gages-fixtures","sha256":"","use":"Fixture/datum review route; edition access and applicability require qualified review"},
        {"source_id":"JSM2-SRC-05","authority":"ROBOTIS","title":"DYNAMIXEL X540 assembly instructions","revision_or_date":"live e-Manual; rechecked 2026-08-11","path_or_url":"https://emanual.robotis.com/docs/en/dxl/x/xh540-w270/#how-to-assemble","sha256":"","use":"Assembly boundary only; no project torque/reuse value published"},
    ]
    fields = {
        "method-register.csv": (list(methods[0])+["warning"], warned(methods)),
        "fixture-applicability.csv": (list(applicability[0])+["warning"], warned(applicability)),
        "phase-gate-register.csv": (list(phases[0])+["warning"], warned(phases)),
        "hsi-method-map.csv": (list(hsi[0])+["warning"], warned(hsi)),
        "hold-point-register.csv": (list(holds[0])+["warning"], warned(holds)),
        "operation-sequence.csv": (list(operations[0])+["warning"], warned(operations)),
        "uncertainty-input-register.csv": (list(uncertainty[0])+["warning"], warned(uncertainty)),
        "acceptance-matrix.csv": (list(acceptance[0])+["warning"], warned(acceptance)),
        "source-register.csv": (list(sources[0])+["warning"], warned(sources)),
    }
    for name,(headers,rows) in fields.items():
        write_csv(OUT/name, headers, rows)
    status = {"identifier":ID,"round":"R254","date":"2026-08-11","methods":5,"hsi_records":20,"uncertainty_inputs":40,"hold_points":12,"operations":22,"operations_executed":0,"authorizations_granted":0,"physical_articles_received":False,"threaded_assembly_authorized":False,"fixture_use_authorized":False,"qualified_review_complete":False,"procurement_authorized":False,"fabrication_authorized":False,"assembly_authorized":False,"connection_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False,"warning":WARNING}
    (OUT/"package-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    (OUT/"HR-V0_joint-stack-metrology-guide.html").write_text(guide(methods,applicability,phases,hsi,holds,operations,uncertainty),encoding="utf-8")
    write_manifest(OUT)
    shutil.copytree(OUT, REL)
    shutil.copy2(REL/"HR-V0_joint-stack-metrology-guide.html", REL/"index.html")
    write_manifest(REL)

    shutil.copytree(CFG0, CFG)
    current, current_fields = read_csv(CFG/"current-configuration-map.csv")
    current.append({"record_id":"CFG-37","role":"task-specific unpowered joint-stack metrology execution contract","identifier":ID,"source_path":"release/hr-v0/joint-stack-metrology-p0.2/package-status.json","configuration_state":"CURRENT FAIL-CLOSED METHOD CONTRACT - NOTHING AUTHORIZED","release_boundary":"five task-specific methods; P0.2 fixture applicability limited; 40 uncertainty inputs and all physical evidence open","warning":WARNING})
    write_csv(CFG/"current-configuration-map.csv",current_fields,current)
    supers, supers_fields = read_csv(CFG/"supersession-map.csv")
    supers.extend([
        {"record_id":"SUP-26","prior_identifier":"HR-V0-JOINT-MET-P0.1","current_or_required_successor":ID,"disposition":"SUPERSEDED FOR EXECUTION PLANNING - HISTORICAL REQUIREMENTS RETAINED","use_authorized":"NO","warning":WARNING},
        {"record_id":"SUP-27","prior_identifier":"HR-V0-CONFIG-REC-P0.17","current_or_required_successor":"HR-V0-CONFIG-REC-P0.18","disposition":"SUPERSEDED BY R254 CONFIGURATION RECORD ONLY","use_authorized":"NO","warning":WARNING},
    ])
    write_csv(CFG/"supersession-map.csv",supers_fields,supers)
    cfg_holds, hold_fields = read_csv(CFG/"open-holds.csv")
    for i,row in enumerate(holds,1):
        cfg_holds.append({"hold_id":f"HOLD-{70+i:02d}","hold":f"{ID}: {row['hold']}","state":"OPEN","closure_evidence":row["closure_evidence"],"warning":WARNING})
    write_csv(CFG/"open-holds.csv",hold_fields,cfg_holds)
    cfg_acc, acc_fields = read_csv(CFG/"acceptance-matrix.csv")
    for i,row in enumerate(acceptance,1):
        cfg_acc.append({"acceptance_id":f"ACC-{103+i:03d}","criterion":f"{ID}: {row['criterion']}","execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":"","warning":WARNING})
    write_csv(CFG/"acceptance-matrix.csv",acc_fields,cfg_acc)
    gates, gate_fields = read_csv(CFG/"gate-impact.csv")
    for row in gates:
        if row["gate_id"] in {"EG-002","EG-005","EG-006","EG-007"}:
            row["evidence_added"] += f"; {ID} five-method metrology split and fail-closed uncertainty-input register"
            row["remaining_evidence"] += "; received articles; accepted method-specific supports/datums/instruments/uncertainty budgets; signed temporary assembly instruction where applicable; executed raw evidence and qualified disposition"
    write_csv(CFG/"gate-impact.csv",gate_fields,gates)
    hashes, hash_fields = read_csv(CFG/"source-hash-register.csv")
    hashes.append({"source_path":"release/hr-v0/joint-stack-metrology-p0.2/package-status.json","sha256":sha(REL/"package-status.json"),"role":"task-specific joint-stack metrology execution contract","warning":WARNING})
    write_csv(CFG/"source-hash-register.csv",hash_fields,hashes)
    cfg_status = json.loads((CFG/"package-status.json").read_text(encoding="utf-8"))
    cfg_status.update({"identifier":"HR-V0-CONFIG-REC-P0.18","round":"R254","current_records":len(current),"supersession_records":len(supers),"open_holds":len(cfg_holds),"acceptance_rows":len(cfg_acc)})
    (CFG/"package-status.json").write_text(json.dumps(cfg_status,indent=2)+"\n",encoding="utf-8")
    (CFG/"README.md").write_text(f"# HR-V0-CONFIG-REC-P0.18\n\n> **{WARNING}**\n\nR254 adds {ID}, supersedes P0.1 for execution planning, and limits P0.2 fixture applicability. {len(cfg_holds)} holds and {len(cfg_acc)} unexecuted acceptances remain.\n",encoding="utf-8")
    (CFG/"index.html").write_text(guide(methods,applicability,phases,hsi,holds,operations,uncertainty),encoding="utf-8")
    write_manifest(CFG)
    shutil.copytree(CFG, CFGR)
    write_manifest(CFGR)
    print(f"Generated {ID}; 5 methods, 40 blank uncertainty inputs, 0 authorizations; configuration P0.18")


if __name__ == "__main__":
    main()
