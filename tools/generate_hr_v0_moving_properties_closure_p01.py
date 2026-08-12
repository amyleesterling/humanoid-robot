#!/usr/bin/env python3
"""Generate R248 full moving-system mass, COM and inertia evidence contract."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDENT = "HR-V0-MOVING-PROP-CLOSURE-P0.1"
CFG_IDENT = "HR-V0-CONFIG-REC-P0.12"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
SRC = ROOT / "mechanical/metrology/hr-v0-moving-properties-closure-p0.1"
REL = ROOT / "release/hr-v0/moving-properties-closure-p0.1"
CFG_OLD = ROOT / "configuration/hr-v0-config-reconciliation-p0.11"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.12"
CFG_REL = ROOT / "release/hr-v0/configuration-reconciliation-p0.12"
LEDGER = ROOT / "bom/hr-v0-moving-mass-ledger.csv"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def digest(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest(directory: Path):
    rows = []
    for path in sorted(p for p in directory.rglob("*") if p.is_file() and p.name != "file-manifest.csv"):
        rows.append({"path": path.relative_to(directory).as_posix(), "bytes": path.stat().st_size, "sha256": digest(path)})
    write_csv(directory / "file-manifest.csv", ["path", "bytes", "sha256"], rows)


def common(rows):
    return [dict(row, warning=WARNING) for row in rows]


def page(title, intro, directory, csv_names):
    sections = []
    for name in csv_names:
        rows, fields = read_csv(directory / name)
        head = "".join(f"<th>{html.escape(f.replace('_', ' '))}</th>" for f in fields)
        body = "".join("<tr>" + "".join(f"<td>{html.escape(str(row[f]))}</td>" for f in fields) + "</tr>" for row in rows)
        sections.append(f"<section><h2>{html.escape(name[:-4].replace('-', ' ').title())}</h2><p><a href='{html.escape(name)}'>Download {html.escape(name)}</a></p><div class='table'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div></section>")
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{html.escape(title)}</title><style>
:root{{--ink:#082a4a;--blue:#075ea8;--sky:#dff3ff;--gold:#f3bd28;--paper:#f8fbfd;--line:#9bc6e4;--danger:#8d1721}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.2vw,18px)/1.55 system-ui,sans-serif}}header,main{{max-width:1500px;margin:auto;padding:clamp(18px,3vw,42px)}}header{{background:linear-gradient(135deg,var(--ink),var(--blue));color:white;max-width:none}}header>div{{max-width:1500px;margin:auto}}.warning{{font-size:clamp(16px,1.3vw,20px);font-weight:800;color:#fff2bd;border:3px solid var(--gold);padding:14px;border-radius:12px}}h1{{font-size:clamp(32px,5vw,62px);line-height:1.05;margin:.5em 0 .2em}}h2{{font-size:clamp(24px,2.6vw,36px);margin-top:1.7em}}.status{{font-size:18px;font-weight:800;color:var(--danger)}}a{{font-size:16px;font-weight:700;color:var(--blue)}}.table{{overflow:auto;background:white;border:2px solid var(--line);border-radius:12px}}table{{border-collapse:collapse;width:100%;min-width:1050px}}th,td{{padding:12px 14px;text-align:left;vertical-align:top;border-bottom:1px solid #cce1ef;font-size:14px;line-height:1.45}}th{{position:sticky;top:0;background:var(--sky)}}code{{font-size:14px}}@media(max-width:600px){{header,main{{padding:18px}}h1{{font-size:34px}}}}
</style></head><body><header><div><p class='warning'>{html.escape(WARNING)}</p><h1>{html.escape(title)}</h1><p>{html.escape(intro)}</p></div></header><main><p class='status'>BLANK EXECUTION CONTRACT · NO PHYSICAL RESULT · B-010 AND R247-H11 REMAIN OPEN</p><p>Use <code>tools/calculate_hr_v0_moving_properties_p01.py</code> only after configuration-bound measurements exist. Exit code 78 means required evidence is absent.</p>{''.join(sections)}</main></body></html>"""


def generate_package():
    for directory in (SRC, REL):
        if directory.exists(): shutil.rmtree(directory)
        directory.mkdir(parents=True)
    ledger, _ = read_csv(LEDGER)
    if len(ledger) != 17:
        raise SystemExit("expected 17 moving-mass ledger rows")
    coverage = []
    for index, row in enumerate(ledger, 1):
        coverage.append({
            "coverage_id": f"MPC-{index:02d}", "ledger_id": row.get("mass_id", row.get("item_id", "")),
            "assembly": row.get("allocation_bucket", ""), "item": row.get("component", ""),
            "prior_mass_g": row.get("mass_each_g", ""), "prior_evidence": row.get("source", ""),
            "received_mass_required": "YES", "itemization_required": "YES" if not row.get("mass_each_g", "") else "VERIFY",
            "execution_state": "NOT EXECUTED", "accepted_result": "", "evidence_uri": "", "warning": WARNING,
        })
    configs = [
        ("CFG-MP-01", "J2 moving group", "Exact received J2 moving-frame/idler, forearm, gripper and routed moving harness", "J2 axis"),
        ("CFG-MP-02", "J1 moving group", "Exact received upper-arm and complete downstream J2 moving group", "J1 axis"),
        ("CFG-MP-03", "Complete moving arm, zero payload", "Configuration-bound full moving assembly, guards and cables", "J1 and J2 axes"),
        ("CFG-MP-04", "Complete moving arm, maximum test payload", "CFG-MP-03 plus exact retained 100 g ceiling article", "J1 and J2 axes"),
    ]
    datasets = {}
    datasets["ledger-coverage.csv"] = (["coverage_id","ledger_id","assembly","item","prior_mass_g","prior_evidence","received_mass_required","itemization_required","execution_state","accepted_result","evidence_uri","warning"], coverage)
    datasets["measurement-configuration.csv"] = (["configuration_id","name","included_items","axes","configuration_hash","photo_uri","assembly_traveler_uri","state","warning"], common([{"configuration_id":a,"name":b,"included_items":c,"axes":d,"configuration_hash":"","photo_uri":"","assembly_traveler_uri":"","state":"NOT EXECUTED"} for a,b,c,d in configs]))
    instruments = [
        ("INST-01","Mass comparator or balance","Received loose items and assembled configurations","SELECTION REQUIRED","Calibration certificate; resolution; capacity; linearity; repeatability; eccentricity; environment limits"),
        ("INST-02","Two reaction-force instruments","Two-axis center-of-mass","SELECTION REQUIRED","Matched calibration, resolution, capacity, drift and support-interface characterization"),
        ("INST-03","Length instrument","Support span, pendulum spacing and length","SELECTION REQUIRED","Traceable calibration, resolution and environmental correction"),
        ("INST-04","Timing instrument or optical acquisition","Pendulum period over 10–50 cycles","SELECTION REQUIRED","Clock traceability, sample rate, trigger/fit method and repeatability"),
        ("INST-05","Bifilar pendulum fixture","Calibrated inertia measurement","SELECTION REQUIRED","Fixture mass, unloaded behavior, cable geometry, rigidity, alignment and two known calibration bodies"),
        ("INST-06","Environmental instruments","Temperature, pressure and humidity where required","SELECTION REQUIRED","Calibration and applicability to uncertainty budget"),
    ]
    datasets["instrument-register.csv"] = (["instrument_id","instrument","use","selection","required_evidence","received_state","use_authorized","warning"], common([{"instrument_id":a,"instrument":b,"use":c,"selection":d,"required_evidence":e,"received_state":"NOT RECEIVED / NOT RECORDED","use_authorized":"FALSE"} for a,b,c,d,e in instruments]))
    datasets["loose-mass-result-template.csv"] = (["coverage_id","ledger_id","received_part_or_lot","configuration_hash","tare_g","mean_mass_g","standard_deviation_g","expanded_uncertainty_g","coverage_factor_k","calibration_uri","raw_repeat_uri","execution_state","acceptance","approver","warning"], common([{"coverage_id":r["coverage_id"],"ledger_id":r["ledger_id"],"received_part_or_lot":"","configuration_hash":"","tare_g":"","mean_mass_g":"","standard_deviation_g":"","expanded_uncertainty_g":"","coverage_factor_k":"","calibration_uri":"","raw_repeat_uri":"","execution_state":"NOT EXECUTED","acceptance":"OPEN","approver":""} for r in coverage]))
    repeats=[]
    for row in coverage:
        for n in range(1,11):
            repeats.append({"coverage_id":row["coverage_id"],"repeat":n,"gross_g":"","tare_g":"","net_g":"","instrument_id":"","timestamp":"","operator":"","environment_record_uri":"","state":"NOT EXECUTED","warning":WARNING})
    datasets["mass-repeat-template.csv"] = (["coverage_id","repeat","gross_g","tare_g","net_g","instrument_id","timestamp","operator","environment_record_uri","state","warning"], repeats)
    datasets["assembly-mass-closure-template.csv"] = (["configuration_id","loose_item_sum_g","loose_sum_expanded_uncertainty_g","assembled_mass_g","assembled_expanded_uncertainty_g","difference_g","acceptance_limit_g","configuration_hash","raw_evidence_uri","execution_state","acceptance","approver","warning"], common([{"configuration_id":a,"loose_item_sum_g":"","loose_sum_expanded_uncertainty_g":"","assembled_mass_g":"","assembled_expanded_uncertainty_g":"","difference_g":"","acceptance_limit_g":"SELECTION REQUIRED","configuration_hash":"","raw_evidence_uri":"","execution_state":"NOT EXECUTED","acceptance":"OPEN","approver":""} for a,_,_,_ in configs]))
    com_rows=[]
    for cfg,_,_,_ in configs:
        for axis in ("X","Y"):
            com_rows.append({"configuration_id":cfg,"axis":axis,"support_a_coordinate_mm":"","support_b_coordinate_mm":"","reaction_a_N":"","reaction_b_N":"","reaction_sum_N":"","independent_mass_kg":"","calculated_com_mm":"","expanded_uncertainty_mm":"","reaction_mass_tolerance":"SELECTION REQUIRED","fixture_correction_uri":"","raw_evidence_uri":"","execution_state":"NOT EXECUTED","acceptance":"OPEN","approver":"","warning":WARNING})
    datasets["reaction-com-template.csv"] = (["configuration_id","axis","support_a_coordinate_mm","support_b_coordinate_mm","reaction_a_N","reaction_b_N","reaction_sum_N","independent_mass_kg","calculated_com_mm","expanded_uncertainty_mm","reaction_mass_tolerance","fixture_correction_uri","raw_evidence_uri","execution_state","acceptance","approver","warning"], com_rows)
    cal_rows=[]
    for axis in ("J1","J2"):
        for body in ("CAL-1","CAL-2"):
            cal_rows.append({"axis":axis,"calibration_body":body,"pendulum_mass_kg":"","body_mass_kg":"","known_body_inertia_kg_m2":"","mean_period_s":"","cycles_per_observation":"","repeat_count":"","configuration_hash":"","certificate_uri":"","raw_timing_uri":"","execution_state":"NOT EXECUTED","acceptance":"OPEN","approver":"","warning":WARNING})
    datasets["pendulum-calibration-template.csv"] = (["axis","calibration_body","pendulum_mass_kg","body_mass_kg","known_body_inertia_kg_m2","mean_period_s","cycles_per_observation","repeat_count","configuration_hash","certificate_uri","raw_timing_uri","execution_state","acceptance","approver","warning"], cal_rows)
    inertia_rows=[]
    for cfg,_,_,axes in configs:
        for axis in ("J1","J2"):
            if axis in axes:
                inertia_rows.append({"configuration_id":cfg,"axis":axis,"article_mass_kg":"","mean_period_s":"","cycles_per_observation":"","repeat_count":"","fitted_K":"","fitted_fixture_inertia_kg_m2":"","calculated_inertia_kg_m2":"","expanded_uncertainty_kg_m2":"","geometry_screen_kg_m2":"","configuration_hash":"","raw_timing_uri":"","execution_state":"NOT EXECUTED","acceptance":"OPEN","approver":"","warning":WARNING})
    datasets["inertia-result-template.csv"] = (["configuration_id","axis","article_mass_kg","mean_period_s","cycles_per_observation","repeat_count","fitted_K","fitted_fixture_inertia_kg_m2","calculated_inertia_kg_m2","expanded_uncertainty_kg_m2","geometry_screen_kg_m2","configuration_hash","raw_timing_uri","execution_state","acceptance","approver","warning"], inertia_rows)
    components = ["balance calibration","balance resolution","balance repeatability","balance linearity/eccentricity","tare","drift","environment","reaction instrument calibration","reaction fixture/alignment","support coordinates","pendulum calibration-body inertia","pendulum mass","period fit/timing","axis/CG alignment","swing/parasitic motion","fixture rigidity","configuration repeatability"]
    datasets["uncertainty-budget-template.csv"] = (["measurand","component","distribution","divisor","sensitivity_coefficient","standard_uncertainty","unit","degrees_of_freedom","source_uri","included","qualified_review","warning"], common([{"measurand":"SELECTION REQUIRED","component":c,"distribution":"SELECTION REQUIRED","divisor":"","sensitivity_coefficient":"","standard_uncertainty":"","unit":"SELECTION REQUIRED","degrees_of_freedom":"","source_uri":"","included":"NOT EXECUTED","qualified_review":"OPEN"} for c in components]))
    formulas = [
        ("CALC-01","two-support COM","x = xA + (xB-xA) RB/(RA+RB)","RA>0; RB>0; xA!=xB; reaction sum reconciles to independent mass"),
        ("CALC-02","calibrated bifilar constant","K=(I1-I2)/(A1-A2), A=(Mp+Mb)T^2","two accepted similar-mass calibration bodies; nonzero denominator; K>0"),
        ("CALC-03","fixture inertia","Ip=K A1-I1","Ip>=0 and independently plausible"),
        ("CALC-04","article inertia","Ia=K(Mp+Ma)Ta^2-Ip","accepted configuration; pure rotation; Ia>0"),
        ("CALC-05","mass closure","delta=assembled mass-sum(received loose masses)","qualified limit and combined uncertainty selected before result acceptance"),
        ("CALC-06","expanded uncertainty","U=k uc","RSS standard uncertainty, units consistent, k and coverage statement documented"),
    ]
    datasets["calculation-contract.csv"] = (["calculation_id","measurand","formula","mandatory_preconditions","accepted_result_state","warning"], common([{"calculation_id":a,"measurand":b,"formula":c,"mandatory_preconditions":d,"accepted_result_state":"NOT EXECUTED"} for a,b,c,d in formulas]))
    sources = [
        ("SRC-01","NISTIR 6969 (2019)","https://doi.org/10.6028/NIST.IR.6969-2019","2019-05-07","laboratory practice, traceability and basic mass calibration"),
        ("SRC-02","NISTIR 6919","https://www.nist.gov/document/nistir6919pdf","2002-01","balance/scale uncertainty; RSS combined standard uncertainty; expanded U=k uc; reproducible reporting"),
        ("SRC-03","NASA/TP-2006-212490-VOL2-PT 2","https://ntrs.nasa.gov/citations/20070008370","2006-11-01","bifilar fixture calibration, CG alignment, pure rotation and 10-50 cycle timing"),
        ("SRC-04","HR-V0 moving-mass ledger","bom/hr-v0-moving-mass-ledger.csv","repository current","17-row design-input ledger; not received evidence"),
    ]
    datasets["source-register.csv"] = (["source_id","document","url_or_path","revision_or_date","use","verification_state","warning"], common([{"source_id":a,"document":b,"url_or_path":c,"revision_or_date":d,"use":e,"verification_state":"PRIMARY SOURCE RECORDED / PHYSICAL APPLICATION NOT EXECUTED"} for a,b,c,d,e in sources]))
    holds = [
        "Exact configuration and 17-row physical itemization frozen",
        "All received parts/lots identified and ten mass repeats recorded",
        "Balance selection, calibration and uncertainty accepted",
        "Four assembled configurations reconciled to loose-item sums",
        "Two reaction instruments and support fixture calibrated",
        "Two-axis COM measurements completed and mass-sum checks passed",
        "Bifilar fixture built, aligned and characterized",
        "Two similar-mass traceable calibration bodies accepted per axis",
        "Pure rotation and 10-50 cycle timing demonstrated",
        "J1/J2 inertia measurements and provisional geometry screens reconciled",
        "Complete uncertainty budgets and qualified technical review accepted",
        "Configuration-bound results incorporated into torque, stop, structure and controls analyses",
    ]
    datasets["open-holds.csv"] = (["hold_id","hold","state","closure_evidence","work_effect","warning"], common([{"hold_id":f"R248-H{i:02d}","hold":v,"state":"OPEN","closure_evidence":"NOT EXECUTED","work_effect":"BLOCKS B-010 / R247-H11 CLOSURE AND MOTION CREDIT"} for i,v in enumerate(holds,1)]))
    accepts = [
        "Every moving-mass ledger row maps to an exact received item or explicitly itemized share.",
        "Ten repeat observations and a traceable uncertainty statement support every accepted received mass.",
        "Loose-to-assembled mass closure passes a preselected configuration-bound limit.",
        "Two orthogonal support-reaction COM results reconcile with independent mass.",
        "Bifilar fixture calibration uses two accepted similar-mass known-inertia bodies per axis.",
        "Period observations use pure rotation and documented 10-50 cycle timing.",
        "Calibrated J1 and J2 inertia results carry qualified expanded uncertainties.",
        "All configuration hashes, photos, raw files and instrument certificates reproduce.",
        "Torque, stopping, structural and control analyses consume the accepted properties.",
        "Qualified reviewers sign the evidence and separately release its downstream use.",
    ]
    datasets["acceptance-matrix.csv"] = (["acceptance_id","criterion","execution_state","result","evidence_uri","approver","warning"], common([{"acceptance_id":f"R248-ACC-{i:02d}","criterion":v,"execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":""} for i,v in enumerate(accepts,1)]))
    for name,(fields,rows) in datasets.items(): write_csv(SRC/name,fields,rows)
    status={"identifier":IDENT,"round":"R248","date":"2026-08-11","state":"BLANK EXECUTION CONTRACT","ledger_rows":17,"configurations":4,"mass_repeat_rows":170,"com_rows":8,"pendulum_calibration_rows":4,"inertia_rows":6,"open_holds":12,"acceptance_rows":10,"physical_measurements":0,"accepted_properties":0,"b010_closed":False,"r247_h11_closed":False,"procurement_authorized":False,"fabrication_authorized":False,"assembly_authorized":False,"connection_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False,"warning":WARNING}
    (SRC/"package-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8",newline="\n")
    (SRC/"README.md").write_text(f"# {IDENT}\n\n> **{WARNING}**\n\nR248 defines the complete blank physical-evidence contract for all 17 moving-mass ledger rows, four assembly configurations, two-axis COM and calibrated bifilar inertia. It contains no physical result and does not close Sol B-010 or R247-H11.\n",encoding="utf-8",newline="\n")
    for path in SRC.iterdir():
        if path.is_file() and path.name != "file-manifest.csv": shutil.copy2(path,REL/path.name)
    csv_names=list(datasets)
    (REL/"index.html").write_text(page("HR-V0 moving mass, COM and inertia closure","An executable but wholly unexecuted evidence contract for the complete moving system.",REL,csv_names),encoding="utf-8",newline="\n")
    manifest(SRC); manifest(REL)


def generate_config():
    for directory in (CFG,CFG_REL):
        if directory.exists(): shutil.rmtree(directory)
        shutil.copytree(CFG_OLD,directory)
    current,fields=read_csv(CFG/"current-configuration-map.csv")
    current.append({"record_id":"CFG-32","role":"complete moving-system physical-properties evidence contract","identifier":IDENT,"source_path":"release/hr-v0/moving-properties-closure-p0.1/package-status.json","configuration_state":"CURRENT BLANK EXECUTION CONTRACT - NO PHYSICAL RESULT","release_boundary":"17-row received mass, assembly closure, two-axis COM and calibrated inertia remain unexecuted; B-010/R247-H11 open","warning":WARNING})
    write_csv(CFG/"current-configuration-map.csv",fields,current)
    supersession,fields=read_csv(CFG/"supersession-map.csv")
    supersession.append({"record_id":"SUP-19","prior_identifier":"HR-V0-CONFIG-REC-P0.11","current_or_required_successor":CFG_IDENT,"disposition":"SUPERSEDED BY R248 CONFIGURATION RECORD ONLY","use_authorized":"NO","warning":WARNING})
    write_csv(CFG/"supersession-map.csv",fields,supersession)
    holds,fields=read_csv(CFG/"open-holds.csv")
    for i,text in enumerate(["Received 17-row moving-mass measurement and itemization","Loose-to-assembled mass reconciliation","Two-axis reaction COM measurement and uncertainty","Calibrated J1/J2 bifilar inertia and uncertainty","Qualified acceptance and downstream analysis reconciliation"],46):
        holds.append({"hold_id":f"HOLD-{i}","hold":text,"state":"NOT EXECUTED","closure_evidence":"Configuration-bound physical evidence and signed review","warning":WARNING})
    write_csv(CFG/"open-holds.csv",fields,holds)
    accept,fields=read_csv(CFG/"acceptance-matrix.csv")
    criteria=["R248 17-row coverage and itemization accepted","R248 received-mass evidence accepted","R248 assembly mass closure accepted","R248 two-axis COM evidence accepted","R248 bifilar calibration accepted","R248 J1/J2 inertia evidence accepted","R248 uncertainty budgets accepted","R248 downstream analyses reconciled"]
    for i,text in enumerate(criteria,66): accept.append({"acceptance_id":f"ACC-{i:02d}","criterion":text,"execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":"","warning":WARNING})
    write_csv(CFG/"acceptance-matrix.csv",fields,accept)
    impacts,fields=read_csv(CFG/"gate-impact.csv")
    for row in impacts:
        if row["gate_id"] in {"EG-005","EG-006"}:
            row["evidence_added"] += f"; {IDENT} blank complete moving-properties execution contract"
            row["remaining_evidence"] += "; received masses, assembly closure, two-axis COM, calibrated inertia, uncertainty and qualified downstream acceptance"
            row["gate_closed"]="NO"
    write_csv(CFG/"gate-impact.csv",fields,impacts)
    status=json.loads((CFG/"package-status.json").read_text(encoding="utf-8"))
    status.update({"identifier":CFG_IDENT,"round":"R248","current_records":32,"supersession_records":19,"open_holds":50,"acceptance_rows":73,"moving_properties_closure":IDENT})
    (CFG/"package-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8",newline="\n")
    (CFG/"README.md").write_text(f"# {CFG_IDENT}\n\n> **{WARNING}**\n\nR248 carries P0.11 forward and adds a blank physical-properties evidence contract. It does not add physical evidence or close B-010. Fifty holds and seventy-three unexecuted acceptance rows remain.\n",encoding="utf-8",newline="\n")
    hashes=[]
    for row in current:
        path=ROOT/row["source_path"]
        if not path.is_file(): raise SystemExit(f"missing config source: {path}")
        hashes.append({"source_path":row["source_path"],"sha256":digest(path),"role":row["role"],"warning":WARNING})
    write_csv(CFG/"source-hash-register.csv",["source_path","sha256","role","warning"],hashes)
    manifest(CFG)
    for path in CFG.iterdir():
        if path.is_file() and path.name != "file-manifest.csv": shutil.copy2(path,CFG_REL/path.name)
    (CFG_REL/"index.html").write_text(page("HR-V0 configuration reconciliation P0.12","Current identifiers and open evidence after adding the R248 moving-properties execution contract.",CFG_REL,["current-configuration-map.csv","supersession-map.csv","gate-impact.csv","open-holds.csv","acceptance-matrix.csv"]),encoding="utf-8",newline="\n")
    manifest(CFG_REL)


def main():
    generate_package(); generate_config()
    print(f"Generated {IDENT} and {CFG_IDENT}: blank contract; 0 physical measurements; B-010 open")


if __name__ == "__main__": main()
