"""Fail-closed checks for HR-30 whole-body energy/safety spine P0.1."""
from __future__ import annotations
import csv, hashlib, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; WB=ROOT/"hr30"/"whole-body-p0.1"; OUT=WB/"energy-safety-spine-p0.1"; RELEASE=ROOT/"release"/"hr30"/"whole-body-p0.1"/"energy-safety-spine-p0.1"
def rows(name):
    with (OUT/name).open(encoding="utf-8-sig",newline="") as h: return list(csv.DictReader(h))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def req(x,m):
    if not x: raise SystemExit("FAIL: "+m)
def main():
    status=json.loads((OUT/"energy-safety-status.json").read_text(encoding="utf-8")); configs=rows("configuration-register.csv"); dev=rows("candidate-device-register.csv"); volts=rows("voltage-compatibility-register.csv"); power=rows("current-power-budget.csv"); safety=rows("safety-function-boundary.csv"); terms=rows("terminal-interface-register.csv"); unresolved=rows("unresolved-input-register.csv")
    req(len(configs)==2 and {r['configuration_id'] for r in configs}=={'CFG-TETHER-FIRST','CFG-ONBOARD-LATER'},"two-configuration boundary drift")
    req(len(dev)==9 and any(r['device_id']=='DEV-09' and r['disposition']=='REJECT FOR DIRECT ACTUATOR BUS' for r in dev),"direct 4S rejection missing")
    req(any(r['load']=='XC330-T288-T' and r['proposed_rail'].startswith('9.0 V') for r in volts),"regulated TTL rail missing")
    total=next(r for r in power if r['load']=='WHOLE ROBOT'); req(abs(float(total['operating_w'])-179)<1e-9 and abs(float(total['short_peak_w'])-727)<1e-9,"whole-robot power budget drift")
    req(abs(float(total['equivalent_at_12v_peak_a'])-60.583)<0.001,"12 V peak arithmetic drift")
    req(len(safety)==6 and all(r['functional_safety_approval']=='False' for r in safety),"safety function approval overclaim")
    req(any(r['function']=='manual reset' and 'motion command' in r['restart_inhibition'] for r in safety),"reset/motion separation missing")
    req(len(terms)>=40 and all(r['physical_pin_or_terminal']=='SELECTION REQUIRED' for r in terms),"energy/safety terminal spine incomplete or overclaimed")
    req(len(unresolved)>=12,"unresolved evidence spine incomplete")
    false=['functional_safety_approved','protection_values_released','conductor_sizes_released','source_selected','connection_authority','powered_test_authority','motion_authority','energization_authority']; req(all(status[k] is False for k in false),"authority or release gate overclaimed")
    req(status['tether_first_configuration_defined'] and status['direct_4s_lipo_architecture_rejected'],"status architecture drift")
    manifest=rows('file-manifest.csv'); listed={r['path'] for r in manifest}; actual={p.relative_to(OUT).as_posix() for p in OUT.rglob('*') if p.is_file() and p.name!='file-manifest.csv'}; req(listed==actual,"manifest file set mismatch")
    for r in manifest:
        p=OUT/r['path']; req(p.stat().st_size==int(r['bytes']) and sha(p)==r['sha256'],f"manifest mismatch {r['path']}")
    src={p.relative_to(OUT).as_posix():p for p in OUT.rglob('*') if p.is_file()}; rel={p.relative_to(RELEASE).as_posix():p for p in RELEASE.rglob('*') if p.is_file()}; req(src.keys()==rel.keys() and all(sha(p)==sha(rel[n]) for n,p in src.items()),"release mirror mismatch")
    page=(OUT/'index.html').read_text(encoding='utf-8'); req('font:16px/1.5' in page and not re.search(r'font-size\s*:\s*(?:[0-9]|1[01])px',page),"web legibility floor missing"); req(not list(OUT.rglob('*.pdf')),"web-native package must not contain PDFs")
    wbstatus=json.loads((WB/'package-status.json').read_text(encoding='utf-8')); req(wbstatus.get('energy_safety_spine_present') is True and wbstatus.get('tether_first_equipment_configuration') is True and wbstatus.get('energization_authority') is False,"whole-body integration status missing/overclaimed")
    with (WB/'battery-energy-source-register.csv').open(encoding='utf-8-sig',newline='') as h: legacy=list(csv.DictReader(h))
    req(len(legacy)==1 and legacy[0]['selection_state'].startswith('REJECTED DIRECT SOURCE'),"legacy battery disposition not synchronized")
    with (WB/'whole-robot-candidate-bom.csv').open(encoding='utf-8-sig',newline='') as h: root_bom=list(csv.DictReader(h))
    req(any(r['item_id']=='HR30-BOM-026' and 'onboard-later' in r['candidate'] and 'rejected' in r['candidate'] for r in root_bom),"whole-robot BOM energy disposition drift")
    req('Whole-body energy and safety spine P0.1' in (WB/'README.md').read_text(encoding='utf-8') and 'energy-safety-spine-p0.1/index.html' in (WB/'index.html').read_text(encoding='utf-8'),"whole-body guide integration missing")
    print(f"PASS: HR-30 energy/safety spine: {len(terms)} logical terminals retained; tether-first and onboard-later separated; all authority gates false"); return 0
if __name__=='__main__': raise SystemExit(main())
