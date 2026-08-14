"""Generate the HR-30 P0.1 whole-robot assembly traveler.

This package binds the existing full-body CAD, fabrication parts, actuators,
fasteners, installed equipment and harness assemblies into module-specific,
human-readable work instructions.  It deliberately does not release any
unselected hardware, tolerance, torque, powered test or motion authority.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "hr30" / "whole-body-p0.1"
OUT = PACKAGE / "assembly-guide-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "assembly-guide-p0.1"
IDENTIFIER = "HR30-WHOLE-ROBOT-ASSEMBLY-GUIDE-P0.1"
WARNING = "PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"
MODULES = ["F01", "F02", "L01", "L02", "P01", "T01", "N01", "H01", "A01", "A02", "G01", "G02"]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def module_for_equipment(module: str, item_id: str) -> str:
    if module in MODULES:
        return module
    if module in {"C01", "S01", "T01/P01/H01"}:
        return "T01"
    combined = {"A01/G01": "A01", "A02/G02": "A02", "L01/F01": "L01", "L02/F02": "L02"}
    if module in combined:
        return combined[module]
    if module == "HN01":
        for token, owner in (("HEAD", "H01"), ("L_ARM", "A01"), ("R_ARM", "A02"), ("L_LEG", "L01"), ("R_LEG", "L02")):
            if token in item_id:
                return owner
        return "T01"
    raise RuntimeError(f"unmapped equipment module {module}: {item_id}")


def module_for_harness(row: dict[str, str]) -> str:
    text = row["modules_or_boundary"]
    for module in MODULES:
        if module in text:
            return module
    return "T01"  # external/service is controlled at the torso system boundary


def semicolon(values: list[str]) -> str:
    return "; ".join(values) if values else "NONE"


def build_registers() -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    exports = {row["module_id"]: row for row in read_csv(PACKAGE / "module-cad" / "module-export-register.csv")}
    interfaces = {row["module_id"]: row for row in read_csv(PACKAGE / "module-interface-control-register.csv")}
    sequence = {row["module_id"]: row for row in read_csv(PACKAGE / "module-assembly-sequence.csv")}
    parts = read_csv(PACKAGE / "manufacturing-files" / "part-file-register.csv")
    axes = read_csv(PACKAGE / "actuator-transmission-allocation.csv")
    fasteners = read_csv(PACKAGE / "fasteners" / "joint-fastener-register.csv")
    equipment = read_csv(PACKAGE / "installed-equipment-register.csv")
    harnesses = read_csv(PACKAGE / "harness" / "physical-p0.1" / "harness-assembly-register.csv")

    parts_by: dict[str, list[dict[str, str]]] = defaultdict(list)
    axes_by: dict[str, list[dict[str, str]]] = defaultdict(list)
    fasteners_by: dict[str, list[dict[str, str]]] = defaultdict(list)
    equipment_by: dict[str, list[dict[str, str]]] = defaultdict(list)
    harness_by: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in parts:
        parts_by[row["module"]].append(row)
    for row in axes:
        axes_by[{"head": "N01", "waist": "P01", "arm": "A01" if row["axis_id"].startswith("L_") else "A02", "hand": "G01" if row["axis_id"].startswith("L_") else "G02", "leg": "L01" if row["axis_id"].startswith("L_") else "L02"}[row["region"]]].append(row)
    for row in fasteners:
        fasteners_by[row["module_id"]].append(row)
    for row in equipment:
        equipment_by[module_for_equipment(row["module"], row["item_id"])].append(row)
    for row in harnesses:
        harness_by[module_for_harness(row)].append(row)

    kits: list[dict[str, object]] = []
    operations: list[dict[str, object]] = []
    checkpoints: list[dict[str, object]] = []
    for module in MODULES:
        exp, interface, seq = exports[module], interfaces[module], sequence[module]
        module_parts = sorted(parts_by[module], key=lambda row: row["part_id"])
        module_axes = sorted(axes_by[module], key=lambda row: row["axis_id"])
        module_fasteners = sorted(fasteners_by[module], key=lambda row: row["fastener_id"])
        module_equipment = sorted(equipment_by[module], key=lambda row: row["item_id"])
        module_harnesses = sorted(harness_by[module], key=lambda row: row["assembly_id"])
        kit = {
            "assembly_step": seq["assembly_step"],
            "parallel_group": seq["parallel_group"],
            "module_id": module,
            "body_segment": exp["body_segment"],
            "prerequisite_modules": seq["prerequisite_modules"],
            "candidate_operation": seq["candidate_operation"],
            "fabrication_part_count": len(module_parts),
            "fabrication_part_ids": semicolon([row["part_id"] for row in module_parts]),
            "axis_count": len(module_axes),
            "axis_ids": semicolon([row["axis_id"] for row in module_axes]),
            "candidate_actuators": semicolon([f'{row["axis_id"]}: {row["candidate_actuator"]}' for row in module_axes]),
            "joint_fastener_count": len(module_fasteners),
            "joint_fastener_sizes": semicolon(sorted({row["candidate_size"] for row in module_fasteners})),
            "installed_equipment_count": len(module_equipment),
            "installed_equipment_ids": semicolon([row["item_id"] for row in module_equipment]),
            "harness_assembly_count": len(module_harnesses),
            "harness_assembly_ids": semicolon([row["assembly_id"] for row in module_harnesses]),
            "planning_mass_kg": interface["planning_mass_kg"],
            "fabrication_step": f'../module-cad/{exp["fabrication_step"]}',
            "integration_reference_step": f'../module-cad/{exp["integration_reference_step"]}',
            "primary_datum": interface["primary_datum"],
            "upstream_interface": interface["upstream_interface"],
            "downstream_interface": interface["downstream_interface"],
            "release_state": "ASSEMBLY TRAVELER CANDIDATE - PHYSICAL HARDWARE, TORQUE, TOLERANCE AND VALIDATION OPEN",
            "warning": WARNING,
        }
        kits.append(kit)

        operation_specs = [
            ("KIT", "Inventory and identify", f'Verify the {len(module_parts)} fabrication files, {len(module_axes)} axis allocations, {len(module_equipment)} equipment items and {len(module_harnesses)} harness assemblies listed in the module kit; quarantine any identity or revision mismatch.'),
            ("FRAME", "Build the unpowered structure", f'Assemble only these fabrication candidates to the {module} fabrication STEP: {semicolon([row["part_id"] for row in module_parts])}. Do not drill, tap or substitute from envelope dimensions.'),
            ("JOINT", "Install joint modules unpowered", f'Install and manually articulate: {semicolon([row["axis_id"] for row in module_axes])}. The {len(module_fasteners)} located joint screws are geometry candidates only; exact product, torque, preload and locking remain SELECTION REQUIRED.'),
            ("EQUIPMENT", "Locate equipment and service access", f'Locate these registered items without connecting power: {semicolon([row["item_id"] for row in module_equipment])}. Preserve the registered mounting planes, service directions and connector boundaries.'),
            ("HARNESS", "Fit stationary routes and moving loops", f'Fit these controlled harness assemblies with all conductors unselected and disconnected: {semicolon([row["assembly_id"] for row in module_harnesses])}. Verify bend, sweep, retention and cover clearance manually.'),
            ("JOIN", "Join to prerequisite module", f'Join {module} only after prerequisite {seq["prerequisite_modules"]} is complete. Use datum {interface["primary_datum"]}; upstream: {interface["upstream_interface"]}; downstream: {interface["downstream_interface"]}.'),
        ]
        for order, (kind, title, instruction) in enumerate(operation_specs, 1):
            operations.append({
                "operation_id": f"{module}-OP{order:02d}", "assembly_step": seq["assembly_step"], "parallel_group": seq["parallel_group"],
                "module_id": module, "operation_kind": kind, "title": title, "instruction": instruction,
                "required_input": f"module-kit-register.csv row {module}; {exp['fabrication_step']}; {exp['integration_reference_step']}",
                "completion_evidence": "SIGNED PHYSICAL TRAVELER REQUIRED - NOT EXECUTED",
                "authority": "UNPOWERED FIT-UP ONLY AFTER SEPARATE FABRICATION RELEASE",
                "warning": WARNING,
            })

        checkpoint_specs = [
            ("IDENTITY", "All listed part/equipment/axis/harness identities and revisions match the controlled kit."),
            ("DATUM", f'Module is located from {interface["primary_datum"]}; no envelope-only drilling or shimming.'),
            ("MANUAL_MOTION", "Every installed joint moves manually through the intended candidate range with no hard interference, cable snag or cover contact."),
            ("FASTENERS", "Every installed fastener is present and witness-marked only after an exact product, torque and locking instruction is released."),
            ("HARNESS", "All fitted routes retain service loops, bend clearance, strain relief and connector keying; conductors remain disconnected."),
            ("MASS", f'Measured module mass and local balance are recorded against the {float(interface["planning_mass_kg"]):.6f} kg planning allocation.'),
        ]
        for order, (kind, criterion) in enumerate(checkpoint_specs, 1):
            checkpoints.append({
                "checkpoint_id": f"{module}-CP{order:02d}", "module_id": module, "checkpoint_kind": kind,
                "criterion": criterion, "result": "NOT EXECUTED", "record_required": "AS-BUILT SERIAL/REVISION, INSPECTOR, DATE, RESULT AND DEVIATION",
                "blocks_next_step_if_open": "YES", "warning": WARNING,
            })

    if len(kits) != 12 or sum(int(row["fabrication_part_count"]) for row in kits) != 66:
        raise RuntimeError("whole-body fabrication kit coverage drift")
    if sum(int(row["axis_count"]) for row in kits) != 25 or sum(int(row["joint_fastener_count"]) for row in kits) != 156:
        raise RuntimeError("axis or joint-fastener coverage drift")
    if sum(int(row["installed_equipment_count"]) for row in kits) != 54 or sum(int(row["harness_assembly_count"]) for row in kits) != 14:
        raise RuntimeError("equipment or harness coverage drift")
    return kits, operations, checkpoints


def flow_svg(kits: list[dict[str, object]]) -> str:
    positions = {"F01": (90, 120), "F02": (90, 310), "L01": (320, 120), "L02": (320, 310), "P01": (550, 215), "T01": (770, 215), "N01": (990, 90), "H01": (1210, 90), "A01": (990, 215), "G01": (1210, 215), "A02": (990, 340), "G02": (1210, 340)}
    arrows = [("F01", "L01"), ("F02", "L02"), ("L01", "P01"), ("L02", "P01"), ("P01", "T01"), ("T01", "N01"), ("N01", "H01"), ("T01", "A01"), ("A01", "G01"), ("T01", "A02"), ("A02", "G02")]
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 460" role="img" aria-labelledby="title desc"><title id="title">HR-30 whole-robot module assembly flow</title><desc id="desc">Feet lead to legs, pelvis, torso, then head and both arms and hands.</desc><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#0b4f91"/></marker></defs><rect width="1400" height="460" fill="#eef8fe"/>']
    for source, target in arrows:
        x1, y1 = positions[source]; x2, y2 = positions[target]
        parts.append(f'<path d="M{x1+150} {y1+45} L{x2} {y2+45}" fill="none" stroke="#0b4f91" stroke-width="5" marker-end="url(#arrow)"/>')
    by_id = {str(row["module_id"]): row for row in kits}
    for module, (x, y) in positions.items():
        row = by_id[module]
        parts.append(f'<g><rect x="{x}" y="{y}" width="150" height="90" rx="14" fill="white" stroke="#0b4f91" stroke-width="4"/><text x="{x+14}" y="{y+31}" font-family="system-ui,sans-serif" font-size="22" font-weight="800" fill="#071d36">{module}</text><text x="{x+14}" y="{y+58}" font-family="system-ui,sans-serif" font-size="15" fill="#071d36">step {html.escape(str(row["assembly_step"]))}</text><text x="{x+14}" y="{y+79}" font-family="system-ui,sans-serif" font-size="14" fill="#075b9b">{row["fabrication_part_count"]} parts · {row["axis_count"]} axes</text></g>')
    parts.append('</svg>')
    return "".join(parts)


def write_web(kits: list[dict[str, object]], operations: list[dict[str, object]], checkpoints: list[dict[str, object]]) -> None:
    by_ops: dict[str, list[dict[str, object]]] = defaultdict(list)
    by_cp: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in operations: by_ops[str(row["module_id"])].append(row)
    for row in checkpoints: by_cp[str(row["module_id"])].append(row)
    cards = []
    for kit in kits:
        module = str(kit["module_id"])
        op_items = ''.join(f'<li><label><input type="checkbox" data-key="{html.escape(str(row["operation_id"]))}"> <strong>{html.escape(str(row["title"]))}</strong></label><p>{html.escape(str(row["instruction"]))}</p></li>' for row in by_ops[module])
        cp_items = ''.join(f'<li><label><input type="checkbox" data-key="{html.escape(str(row["checkpoint_id"]))}"> {html.escape(str(row["criterion"]))}</label></li>' for row in by_cp[module])
        cards.append(f'''<article class="module" data-search="{html.escape(' '.join(str(value) for value in kit.values()).lower())}"><header><span class="step">Step {kit['assembly_step']}{html.escape(str(kit['parallel_group']))}</span><h2>{module} · {html.escape(str(kit['body_segment']))}</h2><p>{html.escape(str(kit['candidate_operation']))}</p></header><div class="facts"><p><strong>{kit['fabrication_part_count']}</strong> fabricated parts</p><p><strong>{kit['axis_count']}</strong> axes</p><p><strong>{kit['joint_fastener_count']}</strong> located joint screws</p><p><strong>{kit['installed_equipment_count']}</strong> equipment items</p><p><strong>{kit['harness_assembly_count']}</strong> harness assemblies</p><p><strong>{float(kit['planning_mass_kg']):.3f} kg</strong> planning mass</p></div><details><summary>Controlled module kit</summary><dl><dt>Prerequisites</dt><dd>{html.escape(str(kit['prerequisite_modules']))}</dd><dt>Fabricated parts</dt><dd>{html.escape(str(kit['fabrication_part_ids']))}</dd><dt>Axes and candidates</dt><dd>{html.escape(str(kit['candidate_actuators']))}</dd><dt>Equipment</dt><dd>{html.escape(str(kit['installed_equipment_ids']))}</dd><dt>Harness</dt><dd>{html.escape(str(kit['harness_assembly_ids']))}</dd><dt>Datum</dt><dd>{html.escape(str(kit['primary_datum']))}</dd></dl><p><a href="{html.escape(str(kit['fabrication_step']))}">Fabrication STEP</a> · <a href="{html.escape(str(kit['integration_reference_step']))}">Integration-reference STEP</a></p></details><details open><summary>Unpowered operations</summary><ol class="traveler">{op_items}</ol></details><details><summary>Blocking inspection checkpoints</summary><ul class="checks">{cp_items}</ul></details></article>''')
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 whole-robot assembly guide P0.1</title><script type="module" src="../vendor/model-viewer.min.js"></script><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#84d8ff;--gold:#f2b91d;--paper:#eef8fe;--line:#9acfe8;--ink:#142a40}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}body>header,main{{max-width:1280px;margin:auto;padding:28px 20px}}body>header{{max-width:none;background:var(--deep);color:white;padding-block:34px}}body>header>div{{max-width:1280px;margin:auto}}h1{{font-size:clamp(36px,6vw,68px);line-height:1.05;margin:.25em 0}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:15px 18px;font-weight:900}}.viewer,.module,.panel{{background:white;border:2px solid var(--line);border-radius:16px;overflow:hidden;margin:20px 0;box-shadow:0 3px 0 #c3e2f1}}model-viewer{{display:block;width:100%;height:clamp(520px,70vh,760px);background:radial-gradient(circle,#fff,var(--paper))}}.viewer p,.panel{{padding:16px 20px}}object{{display:block;width:100%;min-width:900px}}.flow{{overflow:auto}}.toolbar{{position:sticky;top:0;z-index:2;background:var(--paper);padding:12px 0}}input[type=search]{{width:100%;font:inherit;padding:13px 15px;border:2px solid var(--blue);border-radius:10px}}.module>header{{background:var(--deep);color:white;padding:20px}}.module h2{{font-size:clamp(26px,4vw,40px);line-height:1.15;margin:.2em 0}}.step{{display:inline-block;background:var(--gold);color:#17243a;padding:6px 10px;border-radius:999px;font-weight:900}}.facts{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;padding:14px}}.facts p{{margin:0;padding:12px;background:#e7f6fd;border-radius:10px}}details{{border-top:1px solid var(--line)}}summary{{cursor:pointer;padding:15px 18px;font-size:19px;font-weight:850;color:var(--blue)}}details>p,details>dl,details>ol,details>ul{{margin:0;padding:8px 28px 22px}}dt{{font-weight:900;margin-top:10px}}dd{{margin-left:0;overflow-wrap:anywhere}}.traveler,.checks{{list-style:none}}.traveler li,.checks li{{padding:12px;border-bottom:1px solid var(--line)}}.traveler p{{margin:.4em 0 0 28px}}input[type=checkbox]{{width:20px;height:20px;vertical-align:-4px;margin-right:8px}}a{{color:#075b9b;font-weight:800}}small{{font-size:14px}}@media(max-width:600px){{body{{font-size:16px}}body>header,main{{padding-inline:13px}}object{{min-width:760px}}}}</style></head><body><header><div><div class="warning">{WARNING}</div><h1>Assemble the complete robot, module by module.</h1><p>This traveler binds the actual full-body CAD and registers into twelve controlled kits. Checkboxes are local planning aids only; they are not signed inspection evidence or work authorization.</p></div></header><main><section class="viewer"><model-viewer src="../module-cad/HR-30_module_exploded_candidate.glb" poster="../front-elevation.svg" alt="Interactive exploded view of all twelve HR-30 humanoid modules" camera-controls camera-orbit="35deg 76deg 115%" field-of-view="28deg" shadow-intensity="0.85" exposure="1.05"></model-viewer><p><a href="module-kit-register.csv">Module kits</a> · <a href="assembly-operation-register.csv">72 operations</a> · <a href="assembly-checkpoint-register.csv">72 checkpoints</a></p></section><section class="panel flow"><object data="assembly-flow.svg" type="image/svg+xml" aria-label="HR-30 module assembly dependency flow"></object></section><div class="toolbar"><label for="filter"><strong>Find a module, part, axis, actuator, equipment item or harness:</strong></label><input id="filter" type="search" placeholder="Try L_KNEE_PITCH, Raspberry Pi, HN-NH01, or F01"></div><section id="modules">{''.join(cards)}</section><section class="panel"><h2>Authority boundary</h2><p>No checkbox, file, or completed browser state authorizes fabrication or assembly. Exact materials, tolerances, hardware, torque/preload, locking, cable construction, inspection acceptance and physical validation remain required. Powered work, motion and energization require separate signed authorization tied to the as-built configuration.</p></section></main><script>const key='hr30-assembly-p01';const saved=JSON.parse(localStorage.getItem(key)||'{{}}');document.querySelectorAll('[data-key]').forEach(c=>{{c.checked=!!saved[c.dataset.key];c.addEventListener('change',()=>{{saved[c.dataset.key]=c.checked;localStorage.setItem(key,JSON.stringify(saved))}})}});document.getElementById('filter').addEventListener('input',e=>{{const q=e.target.value.toLowerCase().trim();document.querySelectorAll('.module').forEach(card=>card.hidden=q&&!card.dataset.search.includes(q))}});</script></body></html>'''
    (OUT / "index.html").write_text(page, encoding="utf-8", newline="\n")


def integrate_root() -> None:
    readme = PACKAGE / "README.md"
    text = readme.read_text(encoding="utf-8")
    start, end = "<!-- HR30-ASSEMBLY-GUIDE-P01-START -->", "<!-- HR30-ASSEMBLY-GUIDE-P01-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    block = f'''\n{start}\n## Whole-robot assembly traveler\n\nThe [interactive assembly guide](assembly-guide-p0.1/index.html) binds all 12 physical modules, 66 fabrication candidates, 25 axes, 156 located joint fasteners, 54 installed equipment items and 14 harness assemblies into a dependency-ordered unpowered traveler. It does not release materials, tolerances, hardware, torque, assembly, powered work, motion or energization.\n{end}\n'''
    readme.write_text(text.rstrip() + block, encoding="utf-8", newline="\n")

    index = PACKAGE / "index.html"
    page = index.read_text(encoding="utf-8")
    if start in page and end in page:
        page = page.split(start, 1)[0] + page.split(end, 1)[1]
    marker = "<!-- HR30-MODULE-CAD-P01-END -->"
    if marker not in page:
        raise RuntimeError("module CAD web marker missing")
    section = f'''{start}<section id="assembly-guide"><h2>Build the whole robot in twelve controlled module kits</h2><div class="grid"><article class="card pass"><div class="metric">12</div><p>Dependency-ordered body modules.</p></article><article class="card pass"><div class="metric">66 + 25</div><p>Fabricated parts and actuated axes bound to the traveler.</p></article><article class="card pass"><div class="metric">156 + 54</div><p>Located joint screws and installed equipment records.</p></article><article class="card hold"><h3>Unpowered traveler only</h3><p>Materials, tolerances, exact hardware, torque and physical inspection remain open.</p></article></div><div class="viewer"><object data="assembly-guide-p0.1/assembly-flow.svg" type="image/svg+xml" aria-label="Whole-robot module assembly sequence"></object><p><a href="assembly-guide-p0.1/index.html">Open the interactive assembly traveler</a> · <a href="assembly-guide-p0.1/module-kit-register.csv">12 module kits</a> · <a href="assembly-guide-p0.1/assembly-operation-register.csv">operations</a>.</p></div></section>{end}'''
    index.write_text(page.replace(marker, marker + section), encoding="utf-8", newline="\n")

    status_path = PACKAGE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "whole_robot_assembly_traveler_present": True,
        "assembly_traveler_module_count": 12,
        "assembly_traveler_fabrication_part_count": 66,
        "assembly_traveler_axis_count": 25,
        "assembly_traveler_joint_fastener_count": 156,
        "assembly_traveler_equipment_count": 54,
        "assembly_traveler_harness_assembly_count": 14,
        "assembly_traveler_physical_execution_complete": False,
        "assembly_authority": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    kits, operations, checkpoints = build_registers()
    write_csv(OUT / "module-kit-register.csv", kits)
    write_csv(OUT / "assembly-operation-register.csv", operations)
    write_csv(OUT / "assembly-checkpoint-register.csv", checkpoints)
    (OUT / "assembly-flow.svg").write_text(flow_svg(kits), encoding="utf-8", newline="\n")
    write_web(kits, operations, checkpoints)
    status = {
        "identifier": IDENTIFIER, "module_count": 12, "fabrication_part_count": 66, "axis_count": 25,
        "joint_fastener_count": 156, "installed_equipment_count": 54, "harness_assembly_count": 14,
        "operation_count": len(operations), "checkpoint_count": len(checkpoints),
        "physical_execution_complete": False, "fabrication_released": False, "assembly_authority": False,
        "powered_test_authority": False, "motion_authority": False, "energization_authority": False,
        "warning": WARNING,
    }
    (OUT / "assembly-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(f"# HR-30 whole-robot assembly guide P0.1\n\n**{WARNING}**\n\nThis package converts the complete P0.1 humanoid into twelve dependency-ordered, module-specific unpowered assembly travelers. Open `index.html` for the interactive guide. Browser checkboxes are planning aids only and are not signed evidence.\n", encoding="utf-8")
    shutil.copy2(__file__, OUT / "assembly-guide-source.py")
    files = sorted(path for path in OUT.rglob("*") if path.is_file() and path.name != "file-manifest.csv")
    write_csv(OUT / "file-manifest.csv", [{"path": path.relative_to(OUT).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path), "warning": WARNING} for path in files])
    integrate_root()
    import generate_hr30_system_package_p01 as system
    system.refresh_manifest_and_release()
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
