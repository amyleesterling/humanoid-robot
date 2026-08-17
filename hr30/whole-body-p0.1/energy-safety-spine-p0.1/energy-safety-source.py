"""Generate the HR-30 whole-body energy and safety spine P0.1.

This package resolves the system-level power topology enough to guide the next
ECAD pass.  It does not release protection values, conductor sizes, wiring, a
functional-safety claim, or permission to energize.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WB = ROOT / "hr30" / "whole-body-p0.1"
OUT = WB / "energy-safety-spine-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "energy-safety-spine-p0.1"
IDENTIFIER = "HR30-WHOLE-BODY-ENERGY-SAFETY-SPINE-P0.1"
WARNING = "PRELIMINARY - ENERGY/SAFETY ARCHITECTURE ONLY - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
AUTHORITY = "NO PROCUREMENT, FABRICATION, CONNECTION, POWERED TEST, MOTION OR ENERGIZATION AUTHORITY"
OPEN = "SELECTION REQUIRED"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"empty controlled register: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


SOURCES = [
    ("SRC-01", "ROBOTIS", "XH540-W270-R", "https://docs.robotis.com/docs/dxl/model_reference/x_series/xh_series/xh540-w270/", "ROBOTIS-GIT b0c64501, 2025-06-19; accessed 2026-08-14", "10.0-14.8 V; 4.9 A stall at 12 V; stall is a momentary endpoint"),
    ("SRC-02", "ROBOTIS", "XM540-W270-R", "https://docs.robotis.com/docs/dxl/model_reference/x_series/xm_series/xm540-w270/", "ROBOTIS-GIT b0c64501, 2025-06-19; accessed 2026-08-14", "10.0-14.8 V; 4.4 A stall at 12 V; stall is a momentary endpoint"),
    ("SRC-03", "ROBOTIS", "XM430-W350-R", "https://docs.robotis.com/docs/dxl/model_reference/x_series/xm_series/xm430-w350/", "ROBOTIS-GIT b0c64501, 2025-06-19; accessed 2026-08-14", "10.0-14.8 V; 2.3 A stall at 12 V; stall is a momentary endpoint"),
    ("SRC-04", "ROBOTIS", "XC330-T288-T", "https://docs.robotis.com/docs/dxl/model_reference/x_series/xc_series/xc330-t288/", "ROBOTIS-GIT 91f72d1, 2026-01-27; accessed 2026-08-14", "6.5-12.0 V; 0.88 A stall at 12 V; 11.1 V recommended"),
    ("SRC-05", "Mean Well", "RSP-500-12", "https://www.meanwell.com/Upload/PDF/RSP-500/RSP-500-SPEC.PDF", "official datasheet; accessed 2026-08-14", "12 V, 41.7 A, 500.4 W, 10-13.2 V adjustment, constant-current limiting; enclosed mains panel required"),
    ("SRC-06", "Pilz", "PNOZ s4 750104", "https://www.pilz.com/en-US/eshop/product/750104", "manual 21396-EN-23, 2026-06-22; accessed 2026-08-14", "24 VDC, manual/automatic start, 3NO+1NC+semiconductor; exact application and validation open"),
    ("SRC-07", "Mean Well", "SD-15A-24", "https://www.meanwell.com/Upload/PDF/SD-15/SD-15-SPEC.PDF", "official datasheet; accessed 2026-08-14", "isolated 9.2-18 V input to 24 V 0.625 A / 15 W candidate for control supply"),
    ("SRC-08", "Schneider Electric", "TeSys Deca LC1D40ABD", "https://shop.se.com/pro/us/en/product/iec-contactor-tesys-deca-nonreversing-40a-30hp-at-480vac-up-to-100ka-sccr-3-phase-3-no-24vdc-coil-open-style/", "MKTED210011EN v17.1, 2026-07-10, A5/120-A5/123; product page accessed 2026-08-16", "24 VDC coil; 3 NO main poles; 1 NO + 1 NC built-in auxiliary; 21-22 NC mirror certified; catalog lists 50 A at 24 VDC with 1-3 series poles under DC table conditions; HR-30 application validation remains open"),
    ("SRC-09", "IDEC", "XW emergency-stop family", "https://us.idec.com/idec-us/en/USD/medias/EP1430-Estop.pdf", "official catalog EP1430; accessed 2026-08-14", "Safe Break/direct-opening family; exact two-NC order code and enclosure selection open"),
    ("SRC-10", "IDEC", "HW1B-M1F11-G", "https://www.idec.com/en-ca/switches-indicator-lights/switches-pushbuttons/22mm-25mm-30mm-switches/hw-22mm-heavy-duty/hw1b-m1f11-g", "live official product page; accessed 2026-08-14", "momentary green 1NO/1NC candidate; NO contact proposed for monitored manual reset"),
    ("SRC-11", "Bioenno Power", "BLF-1209WS", "https://www.bioennopower.com/products/12v-9ah-lfp-battery-abs-sealed-green-case-1", "live official product page; accessed 2026-08-14", "12 V 9 Ah LiFePO4; 18 A continuous, 40 A/2 s; built-in PCM/balance/protection; 151x65x95 mm; 1.18 kg"),
    ("SRC-12", "Bioenno Power", "BPC-1502C", "https://www.bioennopower.com/products/14-6v-2a-ac-to-dc-charger-for-12v-lifepo4-batteries-black-anderson", "live official product page; accessed 2026-08-14", "14.6 V 2 A charger recommended by BLF-1209WS page; exact interlock/docking implementation open"),
    ("SRC-13", "Pololu", "S18V20F9 item 2576", "https://www.pololu.com/product/2576", "live official product page; accessed 2026-08-14", "9 V fixed buck-boost, 3-30 V input, typical 2 A near output voltage; one candidate per TTL branch"),
]


def build() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    budget = read_csv(WB / "power-energy-budget.csv")
    terminals = read_csv(WB / "electrical/kicad/hr30-whole-body-electrical-p0.1/connector-schedule.csv")
    energy_terms = [r for r in terminals if r["sheet"].startswith(("01_", "02_", "18_"))]
    write_csv(OUT / "source-register.csv", [{"source_id": i, "manufacturer": m, "candidate": c, "official_url": u, "document_revision_or_date": d, "verified_scope": s, "warning": WARNING} for i,m,c,u,d,s in SOURCES])

    configurations = [
        {"configuration_id":"CFG-TETHER-FIRST","intended_stage":"first restrained commissioning and early walking development","energy_source":"RSP-500-12 in qualified external mains enclosure","main_voltage":"12.0 V nominal; set/lock/measure limits required","safety_equipment_location":"external panel","interruption":"two series DC contactors upstream of robot inlet","on_robot_mass_change":"removes battery and both large contactors from robot","state":"PRIMARY P0.1 ARCHITECTURE - PHYSICAL DESIGN/VALIDATION OPEN","authority":AUTHORITY},
        {"configuration_id":"CFG-ONBOARD-LATER","intended_stage":"untethered walking only after tether architecture and load data are validated","energy_source":"Bioenno BLF-1209WS evaluation candidate","main_voltage":"12 V nominal LiFePO4; received voltage envelope and load behavior required","safety_equipment_location":"battery/PCM onboard; final redundant interruption location unresolved","interruption":"onboard DC-rated redundant interruption SELECTION REQUIRED","on_robot_mass_change":"pack +0.123 kg vs current LiPo allowance; cassette depth redesign required","state":"EVALUATION ONLY - DOES NOT CLOSE 727 W / 60.6 A PROVISIONAL PEAK","authority":AUTHORITY},
    ]
    write_csv(OUT / "configuration-register.csv", configurations)

    tree = [
        ("PWR-01","facility AC","external enclosed RSP-500-12","mains PE","external panel DC bus","qualified enclosure, branch protection, disconnect, PE and jurisdiction review"),
        ("PWR-02","external panel DC bus","K1 then K2 series contactors","DC return","touch-safe robot tether inlet","both contactors drop on safety-relay demand; DC duty/coordination open"),
        ("PWR-03","external panel DC bus","SD-15A-24","DC return","24 V safety-control rail","powers PNOZ only; detailed load and protection study open"),
        ("PWR-04","robot tether inlet","robot PDU","ACT_0V_CONTROLLED","19 separately protected RS-485 actuator feeds","12 V main candidate; one unresolved protection/telemetry boundary per actuator"),
        ("PWR-05","robot tether inlet","three S18V20F9 candidates then six protected feeds","ACT_0V_CONTROLLED","six XC330 actuators on three 9 V data segments","one 2 A-typical regulator per two-axis segment; each actuator feed separately protected; thermal/transient proof open"),
        ("PWR-06","robot tether inlet","separate 5.1 V compute and 5 V control/HMI converters","controlled returns","compute/control/HMI rails","exact converters, isolation, grounding and hold-up open"),
        ("PWR-07","BLF-1209WS later candidate","service disconnect/precharge/redundant interruption","battery return","same robot PDU boundary","not substituted until cassette/current/fault/charge evidence closes"),
    ]
    write_csv(OUT / "power-tree-register.csv", [{"path_id":i,"source":s,"device_or_function":d,"return_or_reference":r,"destination":o,"hold":h,"authority":AUTHORITY} for i,s,d,r,o,h in tree])

    devices = [
        ("DEV-01","tether supply","RSP-500-12","EVALUATION CANDIDATE","external only","41.7 A maximum output is below the provisional 60.6 A whole-robot peak; current caps mandatory"),
        ("DEV-02","safety relay","PNOZ s4 750104","EVALUATION CANDIDATE","external only","manual monitored start + EDM application requires exact circuit and qualified validation"),
        ("DEV-03","safety-control converter","SD-15A-24","EVALUATION CANDIDATE","external only","load/protection/thermal/EMC integration open"),
        ("DEV-04","series interruption K1/K2","two Schneider LC1D40ABD contactors; three main poles in series per device","EVALUATION CANDIDATE","external only","21-22 NC auxiliary is mirror certified; exact order code and terminal functions are verified; fault current, L/R, durability, regeneration, protection, opening time, common-cause and whole-machine validation remain open"),
        ("DEV-05","emergency stop","IDEC XW two-NC family","FAMILY CANDIDATE","panel/robot stations","exact order code, contact blocks, enclosure and span-of-control open"),
        ("DEV-06","manual reset","IDEC HW1B-M1F11-G","EVALUATION CANDIDATE","external panel","reset creates eligibility only and cannot issue a motion command"),
        ("DEV-07","onboard battery","Bioenno BLF-1209WS","LATER EVALUATION CANDIDATE","rear torso cassette redesign","18 A continuous covers only 216 W nominal; 40 A/2 s is below provisional 60.6 A peak"),
        ("DEV-08","TTL rail conversion","3x Pololu S18V20F9","EVALUATION CANDIDATE","robot PDU","typical 2 A at near-equal input/output narrowly exceeds each 1.76 A endpoint sum; test/thermal margin open"),
        ("DEV-09","legacy 4S LiPo","Grepow/Tattu TAA12K4S30EC5","REJECT FOR DIRECT ACTUATOR BUS","none","14.8 V nominal equals XH/XM published maximum; charged maximum/protection not closed; no BMS/PCM claim"),
    ]
    write_csv(OUT / "candidate-device-register.csv", [{"device_id":i,"function":f,"candidate":c,"disposition":d,"location":l,"engineering_boundary":b,"authority":AUTHORITY} for i,f,c,d,l,b in devices])

    volts = [
        ("V-01","XH540/XM540/XM430","10.0-14.8 V","12.0 V controlled main candidate","CONDITIONALLY COMPATIBLE","source setpoint/tolerance/transients and branch drop must be measured"),
        ("V-02","XC330-T288-T","6.5-12.0 V; 11.1 V recommended","9.0 V regulated branch candidate","COMPATIBLE BY PUBLISHED RANGE","regulator accuracy/transients/current/thermal proof required"),
        ("V-03","legacy direct 4S LiPo","14.8 V actuator maximum","14.8 V pack nominal; charged maximum unspecified in project evidence","REJECT","nominal equality to maximum leaves no tolerance/transient margin"),
        ("V-04","BLF-1209WS onboard candidate","XH/XM 10.0-14.8 V; XC330 6.5-12 V","12 V nominal main plus regulated 9 V TTL","EVALUATION","received min/max voltage, PCM behavior and brownout/recovery tests required"),
    ]
    write_csv(OUT / "voltage-compatibility-register.csv", [{"check_id":i,"load":l,"published_range":p,"proposed_rail":r,"result":s,"remaining_evidence":e,"authority":AUTHORITY} for i,l,p,r,s,e in volts])

    loads = []
    for r in budget:
        op, peak = float(r["operating_budget_w"]), float(r["short_peak_budget_w"])
        loads.append({"load":r["load"],"domain":r["domain"],"source_budget_voltage":r["candidate_voltage_v"],"operating_w":f"{op:.1f}","short_peak_w":f"{peak:.1f}","equivalent_at_12v_operating_a":f"{op/12:.3f}","equivalent_at_12v_peak_a":f"{peak/12:.3f}","boundary":r["basis_and_hold"],"authority":AUTHORITY})
    write_csv(OUT / "current-power-budget.csv", loads)

    safety = [
        ("SF-01","emergency stop","dual direct-opening NC channels to PNOZ","de-energize both series contactors","reset cannot energize motion command","PLr/SIL allocation, stop time and validation open"),
        ("SF-02","manual reset","monitored manual start input after E-stop channels and EDM healthy","makes safety output eligible","motion controller must remain disabled until a separate motion command","falling-edge/start-mode wiring and location validation open"),
        ("SF-03","external-device monitoring","K1 and K2 built-in 21-22 mirror-certified NC contacts in series in the monitored reset loop","block reset after failed opening","no automatic restart","received-device inspection, diagnostic coverage, common-cause analysis and whole-machine validation open"),
        ("SF-04","watchdog permit","diagnostic request into deterministic controller/safety boundary","remove motion enable on heartbeat fault","cannot bypass E-stop or directly energize contactors","not safety-rated; safety allocation open"),
        ("SF-05","charger interlock","hardwired charger-present channel","prevent actuator-power permit while charging","unplugging charger still requires manual reset and separate motion command","contact sensing and fault behavior open"),
        ("SF-06","power interruption","two series positive-pole contactors","remove actuator source","control/compute may remain powered for diagnostics","DC opening duty, regeneration and discharge time open"),
    ]
    write_csv(OUT / "safety-function-boundary.csv", [{"function_id":i,"function":f,"input_architecture":inp,"safe_response":resp,"restart_inhibition":rst,"unresolved_validation":u,"functional_safety_approval":False,"authority":AUTHORITY} for i,f,inp,resp,rst,u in safety])

    fault = [
        ("F-01","either E-stop channel opens","PNOZ removes outputs; K1 and K2 coils de-energize","actuator energy removed after unverified device/mechanical stop delay"),
        ("F-02","K1 main contact welded","K2 remains series interruption; EDM must block reset","single-fault response requires exact feedback/contact validation"),
        ("F-03","K2 main contact welded","K1 remains series interruption; EDM must block reset","single-fault response requires exact feedback/contact validation"),
        ("F-04","watchdog heartbeat lost","deterministic layer removes motion enable/permit request","watchdog is diagnostic, not credited as sole safety function"),
        ("F-05","charger connected","hardwired interlock prevents permit","charger detection circuit/fault injection open"),
        ("F-06","branch short/overcurrent","branch protection/current limit should isolate affected segment","fault current, fuse/limiter, conductor and connector selection open"),
        ("F-07","tether removed or supply collapses","actuator rails decay; controller enters power-loss state","controlled posture/fall restraint/rail discharge evidence open"),
        ("F-08","reset pressed","only safety-output eligibility may change","must never generate trajectory, torque, or motion command"),
    ]
    write_csv(OUT / "fault-response-register.csv", [{"fault_id":i,"initiating_condition":c,"intended_response":r,"unverified_boundary":u,"test":"NOT EXECUTED","authority":AUTHORITY} for i,c,r,u in fault])

    term_rows = [{**r,"proposed_physical_location":"external panel" if r["sheet"].startswith("02_") else "external panel / robot inlet boundary","physical_pin_or_terminal":OPEN,"wire_protection_rating":OPEN,"native_kicad_correction":"REQUIRED: replace 14.8 V-specific naming/direct LiPo assumption with controlled main-rail configuration","authority":AUTHORITY} for r in energy_terms]
    write_csv(OUT / "terminal-interface-register.csv", term_rows)

    mass = [
        ("M-01","remove current Grepow LiPo allowance from tether configuration",-1.057,"tether source is external"),
        ("M-02","remove current battery cassette from tether configuration",-0.220,"retain interface reservation; exact blanking/ballast decision open"),
        ("M-03","keep two LC1D40ABD contactors external",0.000,"avoids about 1.70 kg onboard penalty from two 0.848 kg product candidates"),
        ("M-04","later BLF-1209WS vs current LiPo allowance",0.123,"cassette depth grows from 49 mm external envelope toward 95 mm pack depth plus clearance"),
        ("M-05","three TTL branch regulator planning allowance",0.030,"exact installed mass and heat open"),
    ]
    write_csv(OUT / "mass-envelope-impact.csv", [{"item":i,"change":c,"delta_on_robot_mass_kg":f"{d:.3f}","boundary":b,"authority":AUTHORITY} for i,c,d,b in mass])

    unresolved = [
        ("ES-01","prospective DC fault current at tether and battery configurations","source impedance, pack PCM behavior, wiring impedance and fault study"),
        ("ES-02","branch protection values and DC interrupt ratings","fault current, cable length/gauge, connector limit, inrush, duty, ambient, bundling and coordination"),
        ("ES-03","K1/K2 exact order codes and EDM contacts","manufacturer application confirmation, auxiliary/main linkage semantics, coil suppression and DC load profile"),
        ("ES-04","functional-safety requirements/allocation","hazard analysis, PLr/SIL target, architecture category, common-cause analysis and qualified validation plan"),
        ("ES-05","maximum stopping time/distance","measured detection, control, contactor, drive, mechanical and fall-restraint timing"),
        ("ES-06","regeneration/overvoltage/precharge/discharge","measured bus capacitance/inertia, braking energy, supply reverse-current behavior and clamp design"),
        ("ES-07","PE/frame/0 V/shield topology","installation class, mains enclosure, jurisdiction, EMC and touch-current review"),
        ("ES-08","tether connector/cable/service disconnect","touch-safe keyed DC rating, current, flex, strain relief, trip hazard, breakaway and retention"),
        ("ES-09","onboard pack/cassette/charger","received min/max voltage, PCM limits, containment, retention, venting, impact, connector and interlock tests"),
        ("ES-10","TTL and 5 V converter selections","line/load/transient regulation, current limit, thermal/EMC, branch fault and enable behavior"),
        ("ES-11","first energization procedure approval","qualified electrical and functional-safety review, locked limits, guarded restraint, instrumentation and signed test authority"),
        ("ES-12","jurisdiction and makerspace constraints","Boston venue rules, equipment classification, inspection and qualified responsible persons"),
    ]
    write_csv(OUT / "unresolved-input-register.csv", [{"hold_id":i,"unresolved_selection":u,"evidence_needed":e,"state":OPEN,"authority":AUTHORITY} for i,u,e in unresolved])

    sequence = [
        ("G0","document freeze","pin-level corrected ECAD, harness, settings and test plan signed","NO CONNECTION"),
        ("G1","unpowered inspection","PE/bond, isolation, polarity, branch separation, E-stop contacts and restraint inspected","NO CONNECTION TO ACTUATORS"),
        ("G2","current-limited panel test","external panel only into dummy load; E-stop/reset/EDM/fault injection","QUALIFIED TEST AUTHORITY REQUIRED"),
        ("G3","logic-only robot test","compute/control with actuator-power branches physically isolated","NO ACTUATOR POWER"),
        ("G4","one unloaded actuator branch","guarded restrained single branch at approved current limit","SEPARATE SIGNED TEST AUTHORITY"),
        ("G5","restrained whole-body static","fall restraint, reduced torque/speed, contactors and stop-time instrumentation","SEPARATE SIGNED TEST AUTHORITY"),
        ("G6","supported weight transfer","overhead restraint and controlled floor area","MOTION AUTHORITY NOT PROVIDED BY THIS PACKAGE"),
    ]
    write_csv(OUT / "first-energization-sequence.csv", [{"gate":g,"scope":s,"entry_evidence":e,"authority_state":a,"result":"NOT EXECUTED"} for g,s,e,a in sequence])

    stats = {"source_count":len(SOURCES),"configuration_count":len(configurations),"energy_safety_terminal_count":len(term_rows),"operating_budget_w":179.0,"short_peak_budget_w":727.0,"operating_current_at_12v_a":round(179/12,3),"short_peak_current_at_12v_a":round(727/12,3),"tether_supply_limit_a":41.7,"onboard_candidate_continuous_a":18.0,"onboard_candidate_2s_a":40.0}
    write_visuals(stats)
    status = {"identifier":IDENTIFIER,"warning":WARNING,**stats,"tether_first_configuration_defined":True,"direct_4s_lipo_architecture_rejected":True,"onboard_lifepo4_candidate_evaluated":True,"native_kicad_topology_correction_complete":True,"pin_level_kicad_correction_required":False,"physical_energy_safety_terminal_release_required":True,"individual_actuator_power_feed_count":25,"functional_safety_approved":False,"protection_values_released":False,"conductor_sizes_released":False,"source_selected":False,"connection_authority":False,"powered_test_authority":False,"motion_authority":False,"energization_authority":False}
    (OUT / "energy-safety-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    (OUT / "README.md").write_text(f"""# HR-30 energy and safety spine P0.1

**{WARNING}**

This package replaces the unsafe architectural assumption that a nominal 14.8 V 4S LiPo can directly feed actuators whose published maximum is also 14.8 V. The first whole-robot configuration is now **tether-first**: a qualified external enclosure contains the mains supply, safety relay and two series contactors, while the robot receives a controlled touch-safe DC feed and distributes it through eight still-unselected protected branches.

The 179 W operating budget is 14.92 A at 12 V. The 727 W short-peak estimate is 60.58 A. The 41.7 A tether-supply candidate and the later 18 A continuous / 40 A for 2 s battery candidate therefore both require deterministic current and torque caps; neither closes the provisional peak by itself.

The three XC330 TTL branches use a 9 V regulator candidate rather than an unregulated 12 V rail. The XH/XM branches use the controlled main rail. Exact regulation, protection, wiring, thermal behavior and fault response remain open.

Reset only makes the safety outputs eligible. It cannot command motion. No functional-safety approval, wiring release, protection selection, connection approval or permission to energize is granted here.

Open the [interactive energy and safety guide](index.html), then inspect `configuration-register.csv`, `power-tree-register.csv`, `safety-function-boundary.csv`, `terminal-interface-register.csv`, and `unresolved-input-register.csv`.
""",encoding="utf-8")
    return stats


def write_visuals(stats: dict) -> None:
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 720" role="img" aria-labelledby="t d"><title id="t">HR-30 tether-first energy and safety spine</title><desc id="d">External mains enclosure containing supply, safety relay and two series contactors feeding the robot power distribution and regulated rails.</desc><style>text{{font-family:Arial,sans-serif;fill:#0d2d57}}.box{{fill:#fff;stroke:#123f73;stroke-width:3}}.safe{{fill:#d8f1ff}}.hold{{fill:#fff2bf}}.line{{stroke:#123f73;stroke-width:5;fill:none;marker-end:url(#a)}}.dash{{stroke:#d79800;stroke-dasharray:10 8}}.h{{font-size:22px;font-weight:700}}.b{{font-size:16px}}.s{{font-size:14px}}</style><defs><marker id="a" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0 0L9 3L0 6z" fill="#123f73"/></marker></defs><rect width="1400" height="720" rx="28" fill="#f7fcff"/><text x="42" y="50" class="h">Tether-first P0.1: high-energy and mains equipment stays in the external panel</text><rect class="box hold" x="40" y="90" width="515" height="550" rx="22"/><text x="68" y="130" class="h">Qualified external enclosure</text><rect class="box" x="75" y="170" width="190" height="105" rx="16"/><text x="95" y="205" class="h">RSP-500-12</text><text x="95" y="235" class="b">12 V / 41.7 A candidate</text><text x="95" y="260" class="s">Mains/PE/protection open</text><rect class="box safe" x="315" y="170" width="205" height="105" rx="16"/><text x="335" y="205" class="h">PNOZ s4</text><text x="335" y="235" class="b">E-stop + manual reset</text><text x="335" y="260" class="s">EDM / validation open</text><rect class="box" x="75" y="340" width="180" height="100" rx="16"/><text x="100" y="378" class="h">K1</text><text x="100" y="410" class="b">DC contactor</text><rect class="box" x="325" y="340" width="180" height="100" rx="16"/><text x="350" y="378" class="h">K2</text><text x="350" y="410" class="b">DC contactor</text><path class="line" d="M265 222H305"/><path class="line dash" d="M420 275V330"/><path class="line" d="M165 275V330"/><path class="line" d="M255 390H315"/><rect class="box safe" x="75" y="500" width="430" height="100" rx="16"/><text x="98" y="535" class="h">Touch-safe tether boundary</text><text x="98" y="567" class="b">strain relief / breakaway / rating: SELECTION REQUIRED</text><path class="line" d="M415 440V490"/><rect class="box safe" x="660" y="90" width="700" height="550" rx="22"/><text x="690" y="130" class="h">HR-30 robot</text><rect class="box" x="705" y="180" width="220" height="105" rx="16"/><text x="730" y="216" class="h">Robot PDU</text><text x="730" y="246" class="b">25 protected feeds</text><text x="730" y="270" class="s">all values unresolved</text><path class="line" d="M505 550H650V232H695"/><rect class="box" x="1010" y="155" width="290" height="105" rx="16"/><text x="1035" y="193" class="h">19 XH/XM feeds</text><text x="1035" y="225" class="b">controlled 12 V main rail</text><path class="line" d="M925 220H1000"/><rect class="box" x="1010" y="310" width="290" height="115" rx="16"/><text x="1035" y="348" class="h">6 XC330 feeds</text><text x="1035" y="380" class="b">three 9 V regulators</text><text x="1035" y="406" class="s">2 A typical each; proof open</text><path class="line" d="M925 235H965V367H1000"/><rect class="box hold" x="705" y="485" width="595" height="110" rx="16"/><text x="730" y="522" class="h">Onboard later: BLF-1209WS LiFePO4 candidate</text><text x="730" y="554" class="b">18 A continuous / 40 A for 2 s &lt; 60.58 A provisional peak</text><text x="730" y="580" class="s">cassette, interruption, charge and fault architecture remain open</text></svg>'''
    svg = svg.replace("Robot PDU", "Five PDU boards").replace("25 protected feeds", "25 actuator branch slots")
    (OUT / "energy-safety-spine.svg").write_text(svg,encoding="utf-8")
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 energy and safety spine</title><style>:root{{--navy:#0d2d57;--blue:#179de3;--sky:#d8f1ff;--gold:#f4b400;--paper:#f7fcff}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--navy);font:16px/1.5 system-ui,sans-serif}}header{{padding:30px max(20px,calc((100% - 1180px)/2));color:white;background:linear-gradient(135deg,var(--navy),#1769aa)}}main{{max-width:1180px;margin:auto;padding:28px 20px 70px}}h1{{font-size:clamp(34px,5vw,62px);line-height:1.05}}h2{{font-size:clamp(25px,3vw,38px);margin-top:44px}}.warning{{padding:14px 18px;border-radius:12px;background:var(--gold);color:#19273d;font-weight:800}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}}.card,.panel{{background:#fff;border:2px solid #9bd5f5;border-radius:16px;padding:18px;box-shadow:0 6px 18px #0d2d5712}}.card strong{{display:block;font-size:30px}}.hold{{border-left:8px solid var(--gold)}}img{{display:block;width:100%;height:auto}}a{{color:#075f9f;font-weight:700}}li{{margin:.7em 0}}@media(max-width:600px){{header{{padding:24px 18px}}main{{padding:20px 14px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>HR-30 whole humanoid / P0.1</p><h1>Energy &amp; safety spine</h1><p>The whole-robot candidate starts tethered, keeps mains and heavy safety equipment off the body, and keeps reset separate from motion.</p></header><main><div class="grid"><div class="card"><strong>{stats['operating_budget_w']:.0f} W</strong>provisional operating budget</div><div class="card hold"><strong>{stats['short_peak_budget_w']:.0f} W</strong>unclosed short-peak estimate</div><div class="card"><strong>{stats['tether_supply_limit_a']:.1f} A</strong>tether candidate output limit</div><div class="card hold"><strong>25</strong>separate actuator-feed boundaries</div></div><h2>Tether-first topology</h2><div class="panel"><img src="energy-safety-spine.svg" alt="Tether-first HR-30 energy and safety architecture diagram"></div><h2>Implemented candidate correction</h2><div class="grid"><div class="card"><h3>Two independent contactors</h3><p>K1 and K2 are now exact Schneider LC1D40ABD candidates. All three main poles of each device are explicitly wired in series.</p></div><div class="card"><h3>Mirror-contact EDM</h3><p>Each built-in 21-22 NC contact is mirror certified and participates in the monitored reset loop. Received-device and whole-machine validation remain open.</p></div><div class="card"><h3>Reset is not run</h3><p>Manual reset can only restore safety-output eligibility. A separate fresh deterministic motion command is always required.</p></div><div class="card hold"><h3>No achieved safety level</h3><p>Category, PL, SIL, stopping time, diagnostic coverage, fault exclusions and common-cause performance remain unvalidated.</p></div></div><h2>Power boundaries</h2><div class="panel"><ul><li><b>Tether-first:</b> external enclosed supply, PNOZ s4, two independent series contactors, robot-side PDU and regulated branch rails.</li><li><b>Direct 4S LiPo:</b> rejected because 14.8 V nominal equals the XH/XM published maximum.</li><li><b>Onboard later:</b> LiFePO4 evaluation candidate only after load, cassette, fault-current, charge and interruption evidence close.</li></ul></div><h2>Controlled registers</h2><div class="panel"><p><a href="configuration-register.csv">configurations</a> / <a href="power-tree-register.csv">power tree</a> / <a href="candidate-device-register.csv">devices</a> / <a href="voltage-compatibility-register.csv">voltage checks</a> / <a href="current-power-budget.csv">current and power budget</a> / <a href="safety-function-boundary.csv">safety boundary</a> / <a href="fault-response-register.csv">fault responses</a> / <a href="terminal-interface-register.csv">current ECAD terminals</a> / <a href="first-energization-sequence.csv">staged test gates</a> / <a href="unresolved-input-register.csv">open inputs</a> / <a href="source-register.csv">primary sources</a></p></div><h2>No energization claim</h2><div class="panel hold"><p>Exact non-contactor terminal selections, protection values, conductors, fault current, L/R, PE/0 V topology, stopping time, regeneration, precharge and physical validation remain open. This is a design candidate, not approval.</p></div></main></body></html>'''
    (OUT / "index.html").write_text(page,encoding="utf-8")


def manifest_release_integrate(stats: dict) -> None:
    shutil.copy2(Path(__file__),OUT/"energy-safety-source.py")
    manifest=OUT/"file-manifest.csv"
    if manifest.exists(): manifest.unlink()
    rows=[{"path":p.relative_to(OUT).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p),"warning":WARNING} for p in sorted(OUT.rglob("*")) if p.is_file()]
    write_csv(manifest,rows)
    if RELEASE.exists(): shutil.rmtree(RELEASE)
    shutil.copytree(OUT,RELEASE)
    battery_rows=read_csv(WB/"battery-energy-source-register.csv")
    battery_rows[0]["protection_boundary"]="NO INTEGRATED BMS/PCM CLAIM; REJECTED FOR DIRECT ACTUATOR BUS: 14.8 V nominal equals the XH/XM published maximum and the page does not close charged maximum; envelope retained as legacy geometry only"
    battery_rows[0]["selection_state"]="REJECTED DIRECT SOURCE - LEGACY GEOMETRY ONLY - SUPERSEDED BY ENERGY-SAFETY-SPINE-P0.1"
    write_csv(WB/"battery-energy-source-register.csv",battery_rows)
    power_rows=read_csv(WB/"power-energy-budget.csv")
    for row in power_rows:
        if row["load"]=="WHOLE ROBOT":
            row["candidate_voltage_v"]="12 V controlled tether main / regulated auxiliaries"
            row["basis_and_hold"]="Tether-first RSP-500-12 evaluation candidate; 179 W operating = 14.92 A and 727 W short peak = 60.58 A at 12 V; 41.7 A supply limit requires deterministic caps. BLF-1209WS onboard-later candidate is 18 A continuous / 40 A for 2 s. Exact source, protection, wiring and validation remain open."
    write_csv(WB/"power-energy-budget.csv",power_rows)
    equipment_rows=read_csv(WB/"installed-equipment-register.csv")
    for row in equipment_rows:
        if row["item_id"]=="EQ-T01-BATTERY-PACK":
            row["candidate"]="LEGACY Grepow/Tattu TAA12K4S30EC5 envelope only - REJECTED as direct actuator source; BLF-1209WS later evaluation candidate requires cassette redesign"
            row["evidence_state"]="legacy 193 x 72 x 37 mm / 1.057 kg geometry retained only to expose the superseded packaging assumption; no source selection"
    write_csv(WB/"installed-equipment-register.csv",equipment_rows)
    bom_rows=read_csv(WB/"whole-robot-candidate-bom.csv")
    for row in bom_rows:
        if row["item_id"]=="HR30-BOM-026":
            row["manufacturer"]="Bioenno evaluation / legacy Grepow envelope"
            row["candidate"]="BLF-1209WS onboard-later evaluation candidate; legacy TAA12K4S30EC5 geometry is rejected for direct actuator use and must be replaced by a redesigned cassette"
    write_csv(WB/"whole-robot-candidate-bom.csv",bom_rows)
    rp=WB/"README.md"; text=rp.read_text(encoding="utf-8"); marker="## Whole-body energy and safety spine P0.1"
    text=text.replace("The primary whole-body candidate now includes the exact published envelope and mass of a Grepow/Tattu TAA12K4S30EC5 4S 12 Ah pack in a removable rear-torso cassette, plus a distinct protection/telemetry reservation because the pack page does not state an integrated BMS/PCM. The tether inlet remains for controlled development. Battery protection, current delivery, containment, retention, connector, charger, thermal and abuse evidence remain open.","The rear-torso model still shows the former Grepow/Tattu pack envelope so the superseded packaging assumption remains visible, but that direct 4S source is now rejected. Tether-first is the primary development configuration; Bioenno BLF-1209WS is an onboard-later evaluation candidate requiring a new cassette. Battery current delivery, containment, retention, connector, charger, thermal and abuse evidence remain open.")
    block=f"""{marker}\n\nThe [interactive energy and safety guide](energy-safety-spine-p0.1/index.html) defines the tether-first whole-robot power path and a separate later onboard LiFePO4 evaluation path. The direct 14.8 V nominal 4S LiPo architecture is rejected because its nominal voltage equals the XH/XM published maximum. Three regulated 9 V TTL branches replace the unregulated 12 V assumption for the XC330 axes, and all 25 actuators now have distinct unresolved protection/telemetry boundaries.\n\nThe native KiCad topology correction is synchronized, but exact physical energy/safety terminals remain unselected. The 179 W operating and 727 W short-peak budgets are not source or wiring ratings. Protection, conductor sizing, fault current, stopping time, PE/0 V and functional-safety validation remain open. Reset can never command motion.\n"""
    if marker in text:
        start=text.index(marker); end=text.find("\n## ",start+len(marker))
        text=text[:start].rstrip()+"\n\n"+block.strip()+("\n\n"+text[end+1:] if end>=0 else "\n")
    else:
        text=text.rstrip()+"\n\n"+block.strip()+"\n"
    rp.write_text(text,encoding="utf-8")
    ip=WB/"index.html"; page=ip.read_text(encoding="utf-8"); link='<a href="energy-safety-spine-p0.1/index.html">Energy and safety spine</a>'
    page=page.replace("The rear-torso battery cassette and exact pack envelope are visible; protection, retention, thermal behavior and every electrical selection remain open.","The rear-torso battery cassette model deliberately retains the rejected legacy pack envelope so the redesign is visible as open work; tether-first is primary and every physical energy selection remains open.")
    page=page.replace("The rear-torso model deliberately retains the rejected legacy pack envelope so the cassette redesign is visible as open work; tether-first is primary and every physical energy selection remains open.","The rear-torso battery cassette model deliberately retains the rejected legacy pack envelope so the redesign is visible as open work; tether-first is primary and every physical energy selection remains open.")
    if link not in page:
        needle='<a href="harness/physical-p0.1/index.html">Interactive physical harness</a>'
        if needle not in page:
            # Clean regeneration reaches energy before the physical-harness
            # stage.  The stage-2 system artifact is the stable fallback.
            needle='<a href="whole-body-electrical-integration.md">Electrical integration</a>'
        if needle not in page: raise SystemExit("whole-body integration anchor missing")
        page=page.replace(needle,needle+' · '+link,1)
    ip.write_text(page,encoding="utf-8")
    sp=WB/"package-status.json"; status=json.loads(sp.read_text(encoding="utf-8")); status.update({"energy_safety_spine_present":True,"tether_first_equipment_configuration":True,"direct_4s_lipo_architecture_rejected":True,"onboard_lifepo4_candidate":"Bioenno BLF-1209WS evaluation candidate","energy_safety_native_kicad_correction_required":False,"energy_safety_native_kicad_topology_corrected":True,"energy_safety_physical_terminal_release_required":True,"energy_safety_individual_actuator_power_feed_count":25,"energy_safety_protection_released":False,"energy_safety_functional_safety_approved":False,"energization_authority":False}); sp.write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    import generate_hr30_system_package_p01 as system_package
    system_package.refresh_manifest_and_release()


def main() -> int:
    stats=build(); manifest_release_integrate(stats); print(json.dumps({"identifier":IDENTIFIER,**stats},indent=2)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
