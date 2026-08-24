#!/usr/bin/env python3
"""Generate the HR-30 first-energization-cell hardware successor P0.1.

This package turns the earlier cell envelope into a fastened construction
candidate: framed doors, captured panels, corner hardware, anchored base-plate
interfaces, and a T-slot pelvis cradle.  Purchased hardware is represented by
interface/envelope geometry, not manufacturing geometry.  No structural,
guard, restraint, work, motion, or energization authority follows.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import re
import shutil
import subprocess
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "first-energization-cell-hardware-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "first-energization-cell-hardware-p0.1"
ROBOT_STEP = WHOLE / "HR-30_p00_neutral_stand_candidate.step"
PREDECESSOR_SOURCE = ROOT / "tools" / "generate_hr30_first_energization_cell_p01.py"
CAD_PYTHON = ROOT.parent / ".venvs" / "hr-v0-cad" / "Scripts" / "python.exe"
IDENTIFIER = "HR30-FIRST-ENERGIZATION-CELL-HARDWARE-P0.1"
DATE = "2026-08-18"
WARNING = (
    "PRELIMINARY - UNBUILT FASTENED CELL HARDWARE CANDIDATE - PURCHASED-PART "
    "ENVELOPES ARE NOT MANUFACTURING MODELS - NOT A WALKING GANTRY OR RATED "
    "FALL-ARREST SYSTEM - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, "
    "CONNECTION, POWERED TESTING, MOTION, WALKING OR ENERGIZATION"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean_step(path: Path) -> None:
    path.write_bytes(re.sub(rb"[ \t]+(?=\r?\n)", b"", path.read_bytes()))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty register: {path}")
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def box(center: tuple[float, float, float], size: tuple[float, float, float]) -> cq.Shape:
    return cq.Workplane("XY").box(*size).translate(center).val()


def cylinder(center: tuple[float, float, float], radius: float, length: float, axis: str = "Z") -> cq.Shape:
    plane = {"Z": "XY", "Y": "XZ", "X": "YZ"}[axis]
    return cq.Workplane(plane).circle(radius).extrude(length / 2, both=True).translate(center).val()


def rod(a: tuple[float, float, float], b: tuple[float, float, float], radius: float) -> cq.Shape:
    start = cq.Vector(*a)
    vector = cq.Vector(b[0] - a[0], b[1] - a[1], b[2] - a[2])
    return cq.Solid.makeCylinder(radius, vector.Length, start, vector.normalized())


def add_profile(rows: list[dict], shapes: dict[str, cq.Shape], member_id: str, subsystem: str,
                role: str, center: tuple[float, float, float], size: tuple[float, float, float],
                cut_length: float, end_prep: str, joint_ids: str) -> None:
    rows.append({
        "member_id": member_id, "subsystem": subsystem, "role": role,
        "candidate_profile": "80/20 40-4040-Lite; 40 x 40 mm; 6063-T6",
        "center_x_mm": center[0], "center_y_mm": center[1], "center_z_mm": center[2],
        "size_x_mm": size[0], "size_y_mm": size[1], "size_z_mm": size[2],
        "cut_length_mm": cut_length, "quantity": 1, "end_preparation": end_prep,
        "joint_ids": joint_ids, "cut_released": "NO - DFM/FAI REQUIRED", "warning": WARNING,
    })
    shapes[member_id] = box(center, size)


def build_profiles() -> tuple[list[dict], dict[str, cq.Shape]]:
    rows: list[dict] = []
    shapes: dict[str, cq.Shape] = {}
    # Main 1200 x 1000 x 1400 frame.
    for ident, role, center, size, length in (
        ("MF-BXF","BASE FRONT",(0,-480,20),(1200,40,40),1200),
        ("MF-BXR","BASE REAR",(0,480,20),(1200,40,40),1200),
        ("MF-BYL","BASE LEFT",(-580,0,20),(40,920,40),920),
        ("MF-BYR","BASE RIGHT",(580,0,20),(40,920,40),920),
        ("MF-UFL","UPRIGHT FRONT LEFT",(-580,-480,700),(40,40,1360),1360),
        ("MF-UFR","UPRIGHT FRONT RIGHT",(580,-480,700),(40,40,1360),1360),
        ("MF-URL","UPRIGHT REAR LEFT",(-580,480,700),(40,40,1360),1360),
        ("MF-URR","UPRIGHT REAR RIGHT",(580,480,700),(40,40,1360),1360),
        ("MF-TXF","TOP FRONT",(0,-480,1380),(1200,40,40),1200),
        ("MF-TXR","TOP REAR",(0,480,1380),(1200,40,40),1200),
        ("MF-TYL","TOP LEFT",(-580,0,1380),(40,920,40),920),
        ("MF-TYR","TOP RIGHT",(580,0,1380),(40,920,40),920),
        ("MF-TC","ZERO-CREDIT TETHER CROSSBAR",(0,0,1360),(1120,40,40),1120),
    ):
        add_profile(rows, shapes, ident, "MAIN FRAME", role, center, size, length, "SQUARE CUT", "SEE FRAME-JOINT-REGISTER")

    # Two independently framed 546 x 1280 mm doors; 12 mm center gap.
    door_specs = (
        ("L", -532, -26, -279),
        ("R", 26, 532, 279),
    )
    for side, x_outer, x_inner, x_center in door_specs:
        add_profile(rows, shapes, f"DR-{side}-VO", f"DOOR {side}", "OUTER STILE", (x_outer,-457,700),(40,40,1280),1280,"SQUARE CUT + ANCHOR COUNTERBORES","DOOR-ANCHOR JOINTS")
        add_profile(rows, shapes, f"DR-{side}-VI", f"DOOR {side}", "INNER STILE", (x_inner,-457,700),(40,40,1280),1280,"SQUARE CUT + ANCHOR COUNTERBORES","DOOR-ANCHOR JOINTS")
        add_profile(rows, shapes, f"DR-{side}-HB", f"DOOR {side}", "BOTTOM RAIL", (x_center,-457,80),(466,40,40),466,"SQUARE CUT","DOOR-ANCHOR JOINTS")
        add_profile(rows, shapes, f"DR-{side}-HT", f"DOOR {side}", "TOP RAIL", (x_center,-457,1320),(466,40,40),466,"SQUARE CUT","DOOR-ANCHOR JOINTS")

    # Foot-platform subframe and buildable T-slot pelvis cradle.
    for ident, role, center, size, length in (
        ("PF-XF","PLATFORM FRONT",(0,-310,50),(620,40,40),620),
        ("PF-XR","PLATFORM REAR",(0,310,50),(620,40,40),620),
        ("PF-YL","PLATFORM LEFT",(-310,0,50),(40,580,40),580),
        ("PF-YR","PLATFORM RIGHT",(310,0,50),(40,580,40),580),
        ("CR-BASE","CRADLE BASE CROSSMEMBER",(0,185,90),(400,40,40),400),
        ("CR-POST-L","CRADLE LEFT POST",(-95,185,290),(40,40,400),400),
        ("CR-POST-R","CRADLE RIGHT POST",(95,185,290),(40,40,400),400),
        ("CR-ARM-L","CRADLE LEFT CANTILEVER",(-70,95,510),(40,220,40),220),
        ("CR-ARM-R","CRADLE RIGHT CANTILEVER",(70,95,510),(40,220,40),220),
        ("CR-BRACE","CRADLE POST CROSS-BRACE",(0,185,450),(230,40,40),230),
    ):
        add_profile(rows, shapes, ident, "SUPPORT/CRADLE", role, center, size, length,
                    "SQUARE CUT + JOINT-SPECIFIC MACHINING", "SEE CRADLE-HARDWARE-REGISTER")
    return rows, shapes


def build_panels() -> tuple[list[dict], dict[str, cq.Shape], list[dict], dict[str, cq.Shape]]:
    panels = (
        ("PN-L","FIXED LEFT",(-557,0,720),(6,880,1280),"CAPTURED IN MAIN-FRAME SLOTS"),
        ("PN-R","FIXED RIGHT",(557,0,720),(6,880,1280),"CAPTURED IN MAIN-FRAME SLOTS"),
        ("PN-REAR","FIXED REAR",(0,457,720),(1090,6,1280),"CAPTURED IN MAIN-FRAME SLOTS"),
        ("PN-ROOF","FIXED ROOF",(0,0,1357),(1090,880,6),"CAPTURED IN MAIN-FRAME SLOTS"),
        ("PN-DL","LEFT DOOR INFILL",(-279,-434,700),(466,6,1200),"CAPTURED IN FRAMED DOOR"),
        ("PN-DR","RIGHT DOOR INFILL",(279,-434,700),(466,6,1200),"CAPTURED IN FRAMED DOOR"),
    )
    rows: list[dict] = []
    shapes: dict[str, cq.Shape] = {}
    gasket_rows: list[dict] = []
    gasket_shapes: dict[str, cq.Shape] = {}
    for ident, role, center, size, mounting in panels:
        rows.append({
            "panel_id": ident, "role": role, "center_xyz_mm": json.dumps(center),
            "finished_size_xyz_mm": json.dumps(size),
            "candidate_material": "SABIC LEXAN 9030 OR 9034; 6 mm; EXACT GRADE SELECTION REQUIRED",
            "edge_finish": "DEBUR; NO SHARP EDGES; SHOP DRAWING/DFM REQUIRED", "mounting": mounting,
            "impact_containment_credit": "NONE", "door_interlock_credit": "NONE",
            "fabrication_release": "NO", "warning": WARNING,
        })
        shapes[ident] = box(center, size)
        dims = sorted(size, reverse=True)[:2]
        perimeter = 2 * sum(dims)
        gasket_rows.append({
            "retention_id": f"GK-{ident}", "panel_id": ident,
            "candidate_product": "80/20 40-2120 gasket for 6 mm panels",
            "calculated_cut_length_mm": perimeter, "quantity": 1,
            "installation": "FOUR EDGE SEGMENTS; MITER/BUTT DETAIL PER DFM",
            "retention_capacity_credit": "NONE", "released": "NO", "warning": WARNING,
        })
        # Visible edge strips; illustrative gasket path, not extrusion section geometry.
        x, y, z = center
        sx, sy, sz = size
        if sx == 6:
            pieces = [box((x,y-sy/2,z),(8,6,sz)),box((x,y+sy/2,z),(8,6,sz)),box((x,y,z-sz/2),(8,sy,6)),box((x,y,z+sz/2),(8,sy,6))]
        elif sy == 6:
            pieces = [box((x-sx/2,y,z),(6,8,sz)),box((x+sx/2,y,z),(6,8,sz)),box((x,y,z-sz/2),(sx,8,6)),box((x,y,z+sz/2),(sx,8,6))]
        else:
            pieces = [box((x-sx/2,y,z),(6,sy,8)),box((x+sx/2,y,z),(6,sy,8)),box((x,y-sy/2,z),(sx,6,8)),box((x,y+sy/2,z),(sx,6,8))]
        gasket_shapes[f"GK-{ident}"] = cq.Compound.makeCompound(pieces)
    return rows, shapes, gasket_rows, gasket_shapes


def bracket_shape(x: float, y: float, z: float, sx: int, sy: int, upper: bool) -> cq.Shape:
    # Purchased 40-4338 interface envelope: two 80 x 80 x 6 legs and a gusset block.
    dz = -37 if upper else 37
    a = box((x + sx*37, y, z + dz),(74,6,74))
    b = box((x, y + sy*37, z + dz),(6,74,74))
    g = box((x + sx*24, y + sy*24, z + dz),(36,36,40))
    return cq.Compound.makeCompound([a,b,g])


def build_hardware() -> tuple[list[dict], dict[str, cq.Shape], list[dict]]:
    shapes: dict[str, cq.Shape] = {}
    joints: list[dict] = []
    fasteners: list[dict] = []
    joint_no = 0
    # Two 40-4338 brackets at each three-member main-frame corner.
    for level, z, upper in (("B",40,False),("T",1360,True)):
        for corner, x, y, sx, sy in (("FL",-560,-460,1,1),("FR",560,-460,-1,1),("RL",-560,460,1,-1),("RR",560,460,-1,-1)):
            for plane in ("X","Y"):
                joint_no += 1
                jid = f"J-MF-{level}{corner}-{plane}"
                shapes[jid] = bracket_shape(x,y,z,sx,sy,upper)
                joints.append({
                    "joint_id": jid, "subsystem": "MAIN FRAME", "location": f"{level} {corner} {plane}-PLANE",
                    "members": "THREE-MEMBER CORNER; SEE PROFILE CUT LIST",
                    "candidate_joint_hardware": "1 x 80/20 40-4338 8-hole gusseted inside bracket",
                    "fastener_set": "8 x 80/20 75-3422 M8 x 16 BHSCS/T-NUT ASSEMBLY",
                    "joint_capacity_released": "NO", "inspection": "FULL SEATING; TORQUE MARK; NO GAP; FAI REQUIRED",
                    "warning": WARNING,
                })
                for n in range(8):
                    fasteners.append({"fastener_id":f"F-{jid}-{n+1:02d}","joint_id":jid,"candidate":"80/20 75-3422 M8 x 16 BHSCS/T-NUT ASSEMBLY","quantity":1,"torque_nm":"PER CURRENT MANUFACTURER GUIDANCE + QUALIFIED JOINT PROCEDURE","released":"NO","warning":WARNING})
    # Crossbar joints use two further gusseted brackets.
    for side, x, sx in (("L",-540,1),("R",540,-1)):
        jid=f"J-TETHER-{side}"
        shapes[jid]=bracket_shape(x,0,1340,sx,1,True)
        joints.append({"joint_id":jid,"subsystem":"ZERO-CREDIT TETHER CROSSBAR","location":side,"members":"MF-TC TO TOP SIDE RAIL","candidate_joint_hardware":"1 x 80/20 40-4338","fastener_set":"8 x 75-3422","joint_capacity_released":"NO","inspection":"FULL SEATING; TORQUE MARK; FAI REQUIRED","warning":WARNING})
        for n in range(8):
            fasteners.append({"fastener_id":f"F-{jid}-{n+1:02d}","joint_id":jid,"candidate":"80/20 75-3422 M8 x 16 BHSCS/T-NUT ASSEMBLY","quantity":1,"torque_nm":"SELECTION/PROCEDURE REQUIRED","released":"NO","warning":WARNING})

    # Eight purchased internal anchor assemblies close the framed-door rectangles.
    for side, x_outer, x_inner in (("L",-532,-26),("R",26,532)):
        for edge, x in (("O",x_outer),("I",x_inner)):
            for level,z in (("B",80),("T",1320)):
                jid=f"J-DR-{side}-{edge}{level}"
                shapes[jid]=cylinder((x,-457,z),8,32,"Y")
                joints.append({"joint_id":jid,"subsystem":f"DOOR {side}","location":f"{edge} {level}","members":"DOOR STILE TO RAIL","candidate_joint_hardware":"1 x 80/20 40-3897 M8 ANCHOR FASTENER ASSEMBLY","fastener_set":"INCLUDED M8 x 30 SHCS; COUNTERBORE REQUIRED","joint_capacity_released":"NO","inspection":"COUNTERBORE/ACCESS HOLE FAI; TORQUE MARK","warning":WARNING})
                fasteners.append({"fastener_id":f"F-{jid}","joint_id":jid,"candidate":"80/20 40-3897 M8 anchor assembly","quantity":1,"torque_nm":"PER CURRENT MANUFACTURER GUIDANCE + QUALIFIED JOINT PROCEDURE","released":"NO","warning":WARNING})
    # Platform subframe corners use the same controlled internal-anchor family.
    for corner,x,y in (("FL",-310,-310),("FR",310,-310),("RL",-310,310),("RR",310,310)):
        jid=f"J-PF-{corner}"
        shapes[jid]=cylinder((x,y,50),8,32,"Z")
        joints.append({"joint_id":jid,"subsystem":"FOOT PLATFORM SUBFRAME","location":corner,"members":"PF-X MEMBER TO PF-Y MEMBER","candidate_joint_hardware":"1 x 80/20 40-3897 M8 ANCHOR FASTENER ASSEMBLY","fastener_set":"INCLUDED M8 x 30 SHCS; COUNTERBORE REQUIRED","joint_capacity_released":"NO","inspection":"COUNTERBORE/ACCESS HOLE FAI; TORQUE MARK","warning":WARNING})
        fasteners.append({"fastener_id":f"F-{jid}","joint_id":jid,"candidate":"80/20 40-3897 M8 anchor assembly","quantity":1,"torque_nm":"PER CURRENT MANUFACTURER GUIDANCE + QUALIFIED JOINT PROCEDURE","released":"NO","warning":WARNING})
    # Four gusseted cradle joints: each post-to-base and arm-to-post connection.
    for side,x,sx in (("L",-95,1),("R",95,-1)):
        for role,z,sy in (("POST-BASE",110,1),("ARM-POST",490,-1)):
            jid=f"J-CR-{side}-{role}"
            shapes[jid]=bracket_shape(x,185,z,sx,sy,role=="ARM-POST")
            joints.append({"joint_id":jid,"subsystem":"PELVIS CRADLE","location":f"{side} {role}","members":"40-4040-LITE CRADLE MEMBERS","candidate_joint_hardware":"1 x 80/20 40-4338 8-hole gusseted inside bracket","fastener_set":"8 x 80/20 75-3422 M8 x 16 BHSCS/T-NUT ASSEMBLY","joint_capacity_released":"NO","inspection":"FULL SEATING; TORQUE MARK; NO GAP; FAI REQUIRED","warning":WARNING})
            for n in range(8):
                fasteners.append({"fastener_id":f"F-{jid}-{n+1:02d}","joint_id":jid,"candidate":"80/20 75-3422 M8 x 16 BHSCS/T-NUT ASSEMBLY","quantity":1,"torque_nm":"PER CURRENT MANUFACTURER GUIDANCE + QUALIFIED JOINT PROCEDURE","released":"NO","warning":WARNING})
    # Cross-brace ends use internal anchors to keep the support envelope clear.
    for side,x in (("L",-95),("R",95)):
        jid=f"J-CR-{side}-BRACE"
        shapes[jid]=cylinder((x,185,450),8,32,"Y")
        joints.append({"joint_id":jid,"subsystem":"PELVIS CRADLE","location":f"{side} CROSS-BRACE END","members":"CR-BRACE TO CR-POST","candidate_joint_hardware":"1 x 80/20 40-3897 M8 ANCHOR FASTENER ASSEMBLY","fastener_set":"INCLUDED M8 x 30 SHCS; COUNTERBORE REQUIRED","joint_capacity_released":"NO","inspection":"COUNTERBORE/ACCESS HOLE FAI; TORQUE MARK","warning":WARNING})
        fasteners.append({"fastener_id":f"F-{jid}","joint_id":jid,"candidate":"80/20 40-3897 M8 anchor assembly","quantity":1,"torque_nm":"PER CURRENT MANUFACTURER GUIDANCE + QUALIFIED JOINT PROCEDURE","released":"NO","warning":WARNING})
    # Controlled custom-interface fastener rows for the platform plate and pad plates.
    jid="J-PF-PLATE"
    joints.append({"joint_id":jid,"subsystem":"FOOT PLATFORM","location":"PLATE TO SUBFRAME","members":"700 x 700 x 18 PLATE TO FOUR PF PROFILES","candidate_joint_hardware":"8 x 80/20 75-3422 CANDIDATE THROUGH CONTROLLED PLATE HOLES","fastener_set":"8 x M8 BHSCS/T-NUT ASSEMBLY; LENGTH/HOLE DETAIL DFM REQUIRED","joint_capacity_released":"NO","inspection":"HOLE POSITION/EDGE DISTANCE/FLATNESS/SEATING FAI","warning":WARNING})
    shapes[jid]=cq.Compound.makeCompound([cylinder((x,y,82),6,14) for x in (-280,280) for y in (-280,280)] + [cylinder((x,y,82),6,14) for x,y in ((-140,-310),(140,-310),(-140,310),(140,310))])
    for n in range(8): fasteners.append({"fastener_id":f"F-{jid}-{n+1:02d}","joint_id":jid,"candidate":"80/20 75-3422 M8 x 16 BHSCS/T-NUT ASSEMBLY - LENGTH REVIEW REQUIRED","quantity":1,"torque_nm":"QUALIFIED PROCEDURE REQUIRED","released":"NO","warning":WARNING})
    for side,x in (("L",-70),("R",70)):
        jid=f"J-CR-PADPLATE-{side}"
        shapes[jid]=cq.Compound.makeCompound([cylinder((x-16,15,500),5,18,"Y"),cylinder((x+16,15,500),5,18,"Y"),cylinder((x-16,15,540),5,18,"Y"),cylinder((x+16,15,540),5,18,"Y")])
        joints.append({"joint_id":jid,"subsystem":"PELVIS CRADLE","location":f"{side} PAD PLATE","members":"CUSTOM PAD PLATE TO CRADLE ARM","candidate_joint_hardware":"4 x M8 BHSCS/T-NUT CANDIDATE","fastener_set":"4 x 75-3422 CANDIDATE; PLATE HOLES/EDGE DISTANCE DFM REQUIRED","joint_capacity_released":"NO","inspection":"PLATE FAI; FULL SEATING; TORQUE MARK","warning":WARNING})
        for n in range(4): fasteners.append({"fastener_id":f"F-{jid}-{n+1:02d}","joint_id":jid,"candidate":"80/20 75-3422 M8 x 16 BHSCS/T-NUT ASSEMBLY","quantity":1,"torque_nm":"QUALIFIED PROCEDURE REQUIRED","released":"NO","warning":WARNING})
    return joints, shapes, fasteners


def build_door_hardware() -> tuple[list[dict], dict[str, cq.Shape]]:
    rows: list[dict] = []
    shapes: dict[str, cq.Shape] = {}
    for side, x_hinge, x_handle in (("L",-556,-48),("R",556,48)):
        for idx,z in enumerate((300,700,1100),1):
            ident=f"HG-{side}-{idx}"
            leaf1=box((x_hinge,-468,z),(48,8,80)); leaf2=box((x_hinge,-444,z),(48,8,80)); pin=cylinder((x_hinge,-456,z),5,92,"Z")
            shapes[ident]=cq.Compound.makeCompound([leaf1,leaf2,pin])
            rows.append({"hardware_id":ident,"door":side,"role":"PROFILE-TO-PROFILE HINGE","candidate":"80/20 12088 SLOTTED ZINC HINGE; 250 N m PUBLISHED MAX LOAD","quantity":1,"mounting":"4 x 75-3627 M8 x 18 CANDIDATE; VERIFY CURRENT PRODUCT CONFIGURATION","safety_interlock_credit":"NONE","capacity_credit":"NONE UNTIL DOOR LOAD/JOINERY REVIEW","warning":WARNING})
        handle=f"HD-{side}"
        shapes[handle]=cq.Compound.makeCompound([box((x_handle,-410,700),(18,18,180)),box((x_handle,-422,620),(18,40,18)),box((x_handle,-422,780),(18,40,18))])
        rows.append({"hardware_id":handle,"door":side,"role":"HANDLE","candidate":"80/20 40-2060; 179 mm GLASS-FILLED NYLON HANDLE","quantity":1,"mounting":"CURRENT PRODUCT HARDWARE SET; RECEIPT/DFM VERIFY","safety_interlock_credit":"NONE","capacity_credit":"ERGONOMIC HANDLE ONLY","warning":WARNING})
        catch=f"CT-{side}"
        shapes[catch]=box(((-8 if side=="L" else 8),-452,980),(16,20,60))
        rows.append({"hardware_id":catch,"door":side,"role":"POSITION CATCH","candidate":"80/20 65-2090 MAGNETIC CATCH; PUBLISHED 12 lb / 5.443 kg PULL","quantity":1,"mounting":"65-2745 BRACKET WHERE REQUIRED; VERIFY FIT","safety_interlock_credit":"NONE - NOT A PROTECTIVE INTERLOCK","capacity_credit":"DOOR POSITION RETENTION ONLY; VALIDATION OPEN","warning":WARNING})
    rows.append({"hardware_id":"DI-01","door":"BOTH","role":"PROTECTIVE DOOR INTERLOCK","candidate":"SELECTION REQUIRED","quantity":2,"mounting":"CODE/HAZARD-ASSESSMENT DEPENDENT","safety_interlock_credit":"NONE","capacity_credit":"NOT SELECTED OR VALIDATED","warning":WARNING})
    return rows, shapes


def build_base_and_support() -> tuple[list[dict], dict[str, cq.Shape], list[dict], dict[str, cq.Shape]]:
    base_rows: list[dict] = []
    base_shapes: dict[str, cq.Shape] = {}
    for ident,x,y in (("BP-FL",-580,-480),("BP-FR",580,-480),("BP-RL",-580,480),("BP-RR",580,480)):
        plate=box((x,y,7.5),(130,160,15)); upright=box((x,y,55),(80,12,80)); anchors=[cylinder((x-42,y,0),7,30),cylinder((x+42,y,0),7,30)]
        base_shapes[ident]=cq.Compound.makeCompound([plate,upright,*anchors])
        base_rows.append({"base_id":ident,"candidate":"80/20 40-2400 FLOOR MOUNT PLATE","purchased_part_geometry":"DIMENSIONED INTERFACE ENVELOPE ONLY; USE MANUFACTURER CAD/RECEIVED PART","profile_fasteners":"4-8 x 75-3500 OR 75-3422 PER FINAL CONFIGURATION","floor_anchor_quantity":2,"floor_anchor":"SELECTION REQUIRED AFTER SUBSTRATE SURVEY","leveling":"SHIM/GROUT/LEVELING PROCEDURE SELECTION REQUIRED","anchorage_capacity_credit":"NONE","caster_permitted_for_E7":"NO","warning":WARNING})

    support_rows: list[dict] = []
    support_shapes: dict[str, cq.Shape] = {
        "PLATFORM": box((0,0,81),(700,700,18)),
        "PAD-L": box((-43,20,520),(34,26,40)),
        "PAD-R": box((43,20,520),(34,26,40)),
        "PAD-PLATE-L": box((-70,15,520),(58,6,70)),
        "PAD-PLATE-R": box((70,15,520),(58,6,70)),
    }
    for ident,role,construction,joints in (
        ("PLATFORM","FOOT PLATFORM","700 x 700 x 18 mm PLATE ON FOUR 40-4040-LITE SUBFRAME MEMBERS","4 CORNER ANCHOR JOINTS + PLATE FASTENERS SELECTION REQUIRED"),
        ("CRADLE","PELVIS CRADLE","6 x 40-4040-Lite MEMBERS + TWO CUSTOM 58 x 70 x 6 mm PAD PLATES","T-SLOT JOINT SET; EXACT BRACKETS/PRELOAD REVIEW OPEN"),
        ("PAD-L","LEFT COMPLIANT PELVIS PAD","34 x 26 x 40 mm PAD ON CUSTOM PLATE","PAD MATERIAL/ADHESIVE/SECONDARY RETENTION SELECTION REQUIRED"),
        ("PAD-R","RIGHT COMPLIANT PELVIS PAD","34 x 26 x 40 mm PAD ON CUSTOM PLATE","PAD MATERIAL/ADHESIVE/SECONDARY RETENTION SELECTION REQUIRED"),
    ):
        support_rows.append({"support_id":ident,"role":role,"construction":construction,"joint_definition":joints,"static_profile_screen":"SEE STRUCTURAL-SCREEN.CSV","joint_capacity_credit":"NONE","proof_state":"NOT EXECUTED","walking_credit":"NONE","warning":WARNING})
    return base_rows, base_shapes, support_rows, support_shapes


def structural_registers() -> tuple[list[dict], list[dict], list[dict]]:
    mass_kg=9.831
    g=9.80665
    weight_n=mass_kg*g
    load_n=weight_n  # deliberately one-side full-weight screen; no load-sharing credit.
    length_mm=165.0
    inertia_mm4=9.3983*10000.0
    elastic_modulus=68947.6
    section_modulus=inertia_mm4/20.0
    moment_nmm=load_n*length_mm
    stress=moment_nmm/section_modulus
    deflection=load_n*length_mm**3/(3*elastic_modulus*inertia_mm4)
    cases=[
        {"case_id":"LC-01","case":"ROBOT GRAVITY - ONE CRADLE ARM CARRIES FULL ROBOT WEIGHT","input":"mass=9.831 kg; g=9.80665 m/s2; no two-arm load-sharing credit","resultant_n":round(load_n,4),"status":"CALCULATED PROFILE-ONLY SCREEN","acceptance":"NO SYSTEM ACCEPTANCE; JOINT/PAD/BASE LOAD PATH OPEN","warning":WARNING},
        {"case_id":"LC-02","case":"ROBOT GRAVITY - FOOT PLATFORM","input":"mass=9.831 kg; actual support distribution unmeasured","resultant_n":round(weight_n,4),"status":"LOAD DEFINED; PLATE/SUBFRAME/JOINT CALCULATION OPEN","acceptance":"SELECTION REQUIRED","warning":WARNING},
        {"case_id":"LC-03","case":"ROBOT CONTACT/IMPACT ON GUARD","input":"APPROACH SPEED, EFFECTIVE INERTIA, CONTACT LOCATION AND FORCE-STROKE MISSING","resultant_n":"SELECTION REQUIRED","status":"NOT CALCULATED","acceptance":"REQUIRES ENERGY-BASED LOAD + GUARD ANALYSIS/TEST","warning":WARNING},
        {"case_id":"LC-04","case":"CELL TIP/RACK/ANCHOR LOAD","input":"FLOOR SUBSTRATE, EXTERNAL FORCE, APPLICATION HEIGHT, CELL MASS/COM MISSING","resultant_n":"SELECTION REQUIRED","status":"NOT CALCULATED","acceptance":"SITE SURVEY + STRUCTURAL DESIGN REQUIRED","warning":WARNING},
        {"case_id":"LC-05","case":"SECONDARY TETHER / POWER-LOSS COLLAPSE","input":"TETHER SLACK, ROBOT TRAJECTORY, FORCE-STROKE, ANCHOR LOAD MISSING","resultant_n":"SELECTION REQUIRED","status":"NOT CALCULATED","acceptance":"NO FALL-ARREST CREDIT","warning":WARNING},
        {"case_id":"LC-06","case":"DOOR SELF-WEIGHT / OPERATOR LOAD","input":"AS-BUILT DOOR MASS, HINGE SPACING, ABUSE LOAD MISSING","resultant_n":"SELECTION REQUIRED","status":"NOT CALCULATED","acceptance":"HINGE/FRAME/JOINT VALIDATION REQUIRED","warning":WARNING},
    ]
    screens=[
        {"screen_id":"SC-01","component":"ONE 40-4040-LITE CRADLE ARM","load_case":"LC-01","model":"PRISMATIC CANTILEVER; L=165 mm; FULL ROBOT WEIGHT ON ONE ARM","source_inputs":"I=9.3983 cm4; E=68947.6 N/mm2; c=20 mm","bending_moment_n_mm":round(moment_nmm,3),"bending_stress_mpa":round(stress,5),"tip_deflection_mm":round(deflection,6),"yield_ratio_using_172_37_mpa":round(172.37/stress,3),"credit":"PROFILE ELASTIC SCREEN ONLY; NO JOINT/PAD/SYSTEM CAPACITY CREDIT","warning":WARNING},
    ]
    proof=[
        {"proof_id":"PT-01","item":"MAIN FRAME JOINTS/RACKING","prerequisite":"APPROVED LOAD CASE, JOINT PROCEDURE, FLOOR ANCHORS, INSTRUMENTS","proof_load":"SELECTION REQUIRED; DO NOT INVENT FROM CATALOG PART LOADS","method":"QUALIFIED STATIC LOAD AT DEFINED HEIGHT/DIRECTION; MEASURE RACK/SLIP/SET","state":"NOT EXECUTED","authority":"NONE","warning":WARNING},
        {"proof_id":"PT-02","item":"PELVIS CRADLE/PLATFORM","prerequisite":"PAD FORCE-STROKE, JOINT DESIGN, ACCEPTED DESIGN LOAD/FACTOR","proof_load":"SELECTION REQUIRED","method":"INSTRUMENTED VERTICAL/LATERAL LOAD; INSPECT SLIP/SET/DAMAGE","state":"NOT EXECUTED","authority":"NONE","warning":WARNING},
        {"proof_id":"PT-03","item":"PANELS/DOORS/RETENTION","prerequisite":"ENERGY-BASED CONTACT LOAD, RETAINER DESIGN, DOOR LOAD CASE","proof_load":"SELECTION REQUIRED","method":"REPRESENTATIVE PANEL/DOOR COUPON THEN ASSEMBLY PROOF/IMPACT TEST","state":"NOT EXECUTED","authority":"NONE","warning":WARNING},
        {"proof_id":"PT-04","item":"FLOOR ANCHORAGE/TIP","prerequisite":"SUBSTRATE SURVEY, ANCHOR SELECTION, APPROVED INSTALLATION PROCEDURE","proof_load":"SELECTION REQUIRED","method":"INSTALLATION INSPECTION + QUALIFIED PULL/SHEAR OR CODE-DEFINED ACCEPTANCE","state":"NOT EXECUTED","authority":"NONE","warning":WARNING},
        {"proof_id":"PT-05","item":"SECONDARY TETHER PATH","prerequisite":"DYNAMIC LOAD, HARDWARE, ANCHORS, SLACK, EVENT DEFINITION","proof_load":"SELECTION REQUIRED","method":"SEPARATE GUARDED PROOF; NO ROBOT AS TEST MASS UNTIL APPROVED","state":"NOT EXECUTED","authority":"NONE","warning":WARNING},
    ]
    return cases,screens,proof


def build_cad() -> dict:
    profile_rows, profiles=build_profiles()
    panel_rows, panels, gasket_rows, gaskets=build_panels()
    joint_rows, brackets, fastener_rows=build_hardware()
    door_rows, door_hw=build_door_hardware()
    base_rows, bases, support_rows, supports=build_base_and_support()
    robot=cq.importers.importStep(str(ROBOT_STEP)).val().translate((0,0,92.5))
    tethers={
        "TETHER-L":rod((-210,0,1335),(-45,42,535),4),
        "TETHER-R":rod((210,0,1335),(45,42,535),4),
    }
    exclusion={
        "EZ-F":box((0,-900,2),(2000,24,4)),"EZ-R":box((0,900,2),(2000,24,4)),
        "EZ-L":box((-988,0,2),(24,1776,4)),"EZ-RIGHT":box((988,0,2),(24,1776,4)),
    }
    stations={
        "ESTOP-STATION":cq.Compound.makeCompound([box((-880,-700,420),(110,110,800)),box((-880,-700,845),(160,160,50))]),
        "INSTRUMENT-STATION":box((860,-650,500),(500,360,1000)),
        "FIRE-STATION":cq.Compound.makeCompound([box((865,680,140),(220,220,280)),rod((865,680,280),(865,680,620),45)]),
    }
    groups=[profiles,panels,gaskets,brackets,door_hw,bases,supports,tethers,exclusion,stations]
    colors=[cq.Color(.08,.25,.48,1),cq.Color(.42,.82,1,.16),cq.Color(.04,.12,.24,1),cq.Color(.92,.68,.08,1),cq.Color(.80,.52,.10,1),cq.Color(.22,.25,.29,1),cq.Color(.92,.68,.08,1),cq.Color(.95,.42,.08,1),cq.Color(1,.68,0,1),cq.Color(.10,.45,.72,.18)]
    assembly=cq.Assembly(name="HR30_FIRST_ENERGIZATION_CELL_HARDWARE_P01_NOT_RELEASED")
    all_shapes=[]
    for group,color in zip(groups,colors):
        for name,shape in group.items():
            assembly.add(shape,name=name,color=color); all_shapes.append(shape)
    hardware=cq.Compound.makeCompound(all_shapes)
    hardware_step=OUT/"HR30_first_energization_cell_hardware_candidate.step"
    cq.exporters.export(hardware,str(hardware_step)); clean_step(hardware_step)
    assembly.save(str(OUT/"HR30_first_energization_cell_hardware_candidate.glb"),tolerance=.75,angularTolerance=.20)
    whole=cq.Compound.makeCompound([hardware,robot])
    whole_step=OUT/"HR30_first_energization_cell_hardware_with_robot_candidate.step"
    cq.exporters.export(whole,str(whole_step)); clean_step(whole_step)
    assembly.add(robot,name="HR30_P00_NEUTRAL_ROBOT_SHA_BOUND",color=cq.Color(.98,.70,.08,1))
    assembly.save(str(OUT/"HR30_first_energization_cell_hardware_with_robot_candidate.glb"),tolerance=.75,angularTolerance=.20)

    write_csv(OUT/"profile-cut-list.csv",profile_rows)
    write_csv(OUT/"frame-joint-register.csv",joint_rows)
    write_csv(OUT/"bracket-fastener-register.csv",fastener_rows)
    write_csv(OUT/"guard-panel-machining-register.csv",panel_rows)
    write_csv(OUT/"panel-retention-register.csv",gasket_rows)
    write_csv(OUT/"door-hardware-register.csv",door_rows)
    write_csv(OUT/"base-anchor-register.csv",base_rows)
    write_csv(OUT/"cradle-hardware-register.csv",support_rows)
    cases,screens,proof=structural_registers()
    write_csv(OUT/"structural-load-case-register.csv",cases)
    write_csv(OUT/"structural-screen.csv",screens)
    write_csv(OUT/"proof-plan.csv",proof)
    return {
        "profile_member_count":len(profile_rows),"main_frame_member_count":13,"door_frame_member_count":8,
        "platform_cradle_profile_count":10,"guard_panel_count":len(panel_rows),"joint_count":len(joint_rows),
        "fastener_assembly_count":len(fastener_rows),"door_hardware_record_count":len(door_rows),
        "base_plate_count":len(base_rows),"robot_step_sha256":sha(ROBOT_STEP),
        "hardware_extent_mm":[round(v,3) for v in (hardware.BoundingBox().xlen,hardware.BoundingBox().ylen,hardware.BoundingBox().zlen)],
    }


def publish(meta: dict) -> None:
    sources=[
        ("SRC-01","80/20","40-4040-Lite product page","LIVE OFFICIAL PAGE; ACCESSED 2026-08-18","https://8020.net/40-4040-lite.html","40 x 40 mm 6063-T6 profile; I=9.3983 cm4; yield=172.37 N/mm2; 0.0998 lb/in"),
        ("SRC-02","80/20","40-4338 product page","LIVE OFFICIAL PAGE; ACCESSED 2026-08-18","https://8020.net/40-4338.html","80 x 80 x 6 mm 8-hole gusseted inside bracket; eight 75-3422 fasteners"),
        ("SRC-03","80/20","40-3897 product page","LIVE OFFICIAL PAGE; ACCESSED 2026-08-18","https://8020.net/40-3897.html","M8 anchor fastener assembly; counterbore machining required"),
        ("SRC-04","80/20","40-2400 product page","LIVE OFFICIAL PAGE; ACCESSED 2026-08-18","https://8020.net/40-2400-black.html","floor mount plate family; anchor/substrate design not supplied by this package"),
        ("SRC-05","80/20","40-2120 product page","LIVE OFFICIAL PAGE; ACCESSED 2026-08-18","https://8020.net/40-2120.html","gasket for 6 mm panels; 1841.5 mm listed length"),
        ("SRC-06","80/20","12088 product page","LIVE OFFICIAL PAGE; ACCESSED 2026-08-18","https://8020.net/12088.html","profile/panel slotted zinc hinge; published maximum load 250 N m"),
        ("SRC-07","80/20","65-2090 product page","LIVE OFFICIAL PAGE; ACCESSED 2026-08-18","https://8020.net/65-2090.html","magnetic catch; published 12 lb / 5.443 kg pull; no interlock credit"),
        ("SRC-08","80/20","40-2060 product page","LIVE OFFICIAL PAGE; ACCESSED 2026-08-18","https://8020.net/40-2060.html","179 mm glass-filled nylon handle family"),
        ("SRC-09","SABIC","LEXAN sheet portfolio brochure","OFFICIAL AMERICAS PORTFOLIO; ACCESSED 2026-08-18","https://www.sabic.com/en/images/sabic-lexan-sheet-portfolio-brochure-english-americas_tcm1010-5016.pdf","9030/9034 general-purpose polycarbonate; 6 mm offered; no cell impact rating"),
    ]
    write_csv(OUT/"primary-source-register.csv",[{"source_id":a,"manufacturer":b,"document":c,"revision_or_access_date":d,"url":e,"verified_scope":f,"system_capacity_verified":"NO","warning":WARNING} for a,b,c,d,e,f in sources])
    unresolved=[
        ("SEL-01","FLOOR SUBSTRATE AND ANCHORS","SLAB MATERIAL/THICKNESS/REINFORCEMENT/EDGE DISTANCE; SITE JURISDICTION; ANCHOR LOADS","SITE SURVEY + QUALIFIED ANCHOR DESIGN"),
        ("SEL-02","GUARD IMPACT LOAD AND POLYCARBONATE GRADE","ROBOT EFFECTIVE INERTIA/SPEED/CONTACT; SPAN/EDGE CONDITION; GRADE CERTIFICATE","ENERGY MODEL + PANEL/RETENTION ANALYSIS AND TEST"),
        ("SEL-03","PELVIS PAD SYSTEM","FORCE-STROKE, HARDNESS, TEMPERATURE/AGING, RETENTION, CONTACT PRESSURE","COUPON + ASSEMBLY TEST"),
        ("SEL-04","CRADLE/FRAME JOINT CAPACITY","EXACT PRELOAD/TORQUE; FRICTION; SLIP/PRYING; RECEIVED HARDWARE","JOINT CALCULATION + PROOF"),
        ("SEL-05","DOOR PROTECTIVE INTERLOCK","HAZARD-BASED SAFETY FUNCTION/PLr; DEVICE/ACTUATOR; DEFEAT RESISTANCE","SAFETY DESIGN + VALIDATION"),
        ("SEL-06","SECONDARY TETHER SYSTEM","SLACK, DYNAMIC LOAD, TERMINATIONS, ANCHORS, INSPECTION/LIFE","DYNAMIC ANALYSIS + QUALIFIED PROOF"),
        ("SEL-07","PLATFORM MATERIAL/FASTENERS","PLATE MATERIAL, FLATNESS, FASTENERS, FOOT FRICTION/RETENTION","DFM + STATIC/SLIP TEST"),
        ("SEL-08","DOOR LOAD AND HINGE CONFIGURATION","AS-BUILT MASS, OPERATOR/ABUSE LOAD, HINGE FASTENERS, SAG LIMIT","DOOR CALCULATION + CYCLE/PROOF TEST"),
        ("SEL-09","FRAME RACK/TIP LOAD","CELL MASS/COM, EXTERNAL FORCE/HEIGHT, ROBOT FAULT LOAD, FLOOR CONDITION","STRUCTURAL MODEL + SITE PROOF"),
        ("SEL-10","FASTENER TORQUE/LOCKING/INSPECTION","CURRENT MANUFACTURER DATA, LUBRICATION, REUSE, MARKING, RETORQUE","QUALIFIED ASSEMBLY PROCEDURE"),
    ]
    write_csv(OUT/"unresolved-inputs.csv",[{"selection_id":a,"item":b,"missing_evidence":c,"closure_evidence":d,"state":"SELECTION REQUIRED","work_authority":"NONE","warning":WARNING} for a,b,c,d in unresolved])
    bom=[
        ("B-01","40-4040-Lite profile","80/20","40-4040-Lite",31,"CUT LIST CONTROLS LENGTH; DFM/QUOTE REQUIRED"),
        ("B-02","8-hole gusseted inside bracket","80/20","40-4338",22,"MAIN FRAME/CROSSBAR/CRADLE CANDIDATE"),
        ("B-03","M8 x 16 bracket/interface fastener/T-nut assemblies","80/20","75-3422",192,"176 BRACKET + 16 CUSTOM INTERFACE; TORQUE/LENGTH PROCEDURE OPEN"),
        ("B-04","M8 anchor fastener assembly","80/20","40-3897",14,"DOOR, PLATFORM AND CRADLE-BRACE JOINTS; MACHINING REQUIRED"),
        ("B-05","slotted zinc hinge","80/20","12088",6,"THREE PER DOOR; CAPACITY VALIDATION OPEN"),
        ("B-06","handle","80/20","40-2060",2,"ONE PER DOOR"),
        ("B-07","magnetic catch","80/20","65-2090",2,"ZERO PROTECTIVE-INTERLOCK CREDIT"),
        ("B-08","floor mount plate","80/20","40-2400",4,"ANCHORS/SUBSTRATE SELECTION REQUIRED"),
        ("B-09","6 mm clear polycarbonate panels","SABIC","LEXAN 9030 OR 9034 - SELECTION REQUIRED",6,"DIMENSIONS IN PANEL REGISTER; IMPACT VALIDATION OPEN"),
        ("B-10","6 mm panel gasket stock","80/20","40-2120",14,"23984 mm NET LENGTH; CUT/WASTE PLAN REQUIRES DFM"),
        ("B-11","platform plate","SELECTION REQUIRED","700 x 700 x 18 mm",1,"MATERIAL/FASTENERS/FLATNESS OPEN"),
        ("B-12","custom pelvis pad plates","CUSTOM","58 x 70 x 6 mm",2,"MATERIAL/HOLES/FINISH DFM REQUIRED"),
        ("B-13","compliant pelvis pads","SELECTION REQUIRED","34 x 26 x 40 mm ENVELOPE",2,"FORCE-STROKE/RETENTION OPEN"),
        ("B-14","protective door interlock set","SELECTION REQUIRED","SELECTION REQUIRED",2,"SAFETY FUNCTION NOT SELECTED"),
        ("B-15","floor anchor set","SELECTION REQUIRED","SELECTION REQUIRED",8,"SITE/SUBSTRATE DEPENDENT"),
    ]
    write_csv(OUT/"candidate-bom.csv",[{"item_id":a,"item":b,"manufacturer":c,"candidate_part_or_family":d,"quantity":e,"selection_state":f,"procurement_released":"NO","warning":WARNING} for a,b,c,d,e,f in bom])
    status={
        "identifier":IDENTIFIER,"date":DATE,"warning":WARNING,"predecessor":"HR30-FIRST-ENERGIZATION-CELL-P0.1",
        **meta,"complete_humanoid_visible":True,"framed_doors_present":True,"captured_panels_present":True,
        "physical_joint_hardware_present":True,"base_anchor_interfaces_present":True,"pelvis_cradle_build_path_present":True,
        "purchased_part_geometry_is_manufacturing_source":False,"profile_only_static_screen_complete":True,
        "whole_cell_structure_released":False,"guard_impact_validated":False,"restraint_rated":False,
        "door_interlock_selected":False,"floor_anchor_selected":False,"proof_tests_executed":False,
        "fer_g02_closed":False,"fer_g10_closed":False,"fer_g11_closed":False,
        "procurement_authority":False,"fabrication_authority":False,"assembly_authority":False,
        "connection_authority":False,"powered_test_authority":False,"motion_authority":False,
        "walking_authority":False,"energization_authority":False,
    }
    (OUT/"hardware-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    binding={"identifier":IDENTIFIER,"warning":WARNING,"robot_step":ROBOT_STEP.relative_to(ROOT).as_posix(),"robot_step_sha256":sha(ROBOT_STEP),"predecessor_generator":PREDECESSOR_SOURCE.relative_to(ROOT).as_posix(),"predecessor_generator_sha256":sha(PREDECESSOR_SOURCE),"robot_translation_xyz_mm":[0,0,92.5],"cell_outer_xyz_mm":[1200,1000,1400]}
    (OUT/"source-binding.json").write_text(json.dumps(binding,indent=2)+"\n",encoding="utf-8")

    readme=f"""# HR-30 first-energization-cell hardware P0.1

**{WARNING}**

This is the fabrication-level successor to the earlier envelope model. It is a complete fastened candidate with **31 profile members**, two framed doors, six captured 6 mm panels, 22 gusset brackets, 206 controlled fastener assemblies, six profile hinges, four floor-mount interfaces, a platform subframe, and a T-slot pelvis cradle around the SHA-bound complete HR-30.

The STEP/GLB model is an editable construction assembly. Purchased brackets, hinges, catches, handles, gaskets, and base plates are interface/envelope representations; their manufacturer CAD and received parts control. Custom panel and profile dimensions are in the registers, but no cut, purchase, assembly, or powered-work release is granted.

The one completed calculation is deliberately narrow: a single 40-4040-Lite cradle arm carrying the full robot gravity load. It screens the profile only. Joint slip/prying, pad behavior, platform behavior, frame racking/tip, floor anchors, guard impact, door load, tether dynamics, proof tests, and FER-G02/G10/G11 remain open.

Open `index.html` for the interactive assembly and human-readable fabrication guide.
"""
    (OUT/"README.md").write_text(readme,encoding="utf-8")
    make_html(meta)


def table_html(filename: str, title: str) -> str:
    with (OUT/filename).open(encoding="utf-8",newline="") as handle:
        records=list(csv.DictReader(handle))
    fields=list(records[0])
    head="".join(f"<th>{html.escape(f.replace('_',' ').title())}</th>" for f in fields)
    body="".join("<tr>"+"".join(f"<td>{html.escape(str(row[f]))}</td>" for f in fields)+"</tr>" for row in records)
    return f"<section><h2>{html.escape(title)}</h2><div class='table-wrap'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div></section>"


def make_html(meta: dict) -> None:
    tables="".join([
        table_html("profile-cut-list.csv","Profile cut list"),
        table_html("frame-joint-register.csv","Frame and door joints"),
        table_html("door-hardware-register.csv","Door hardware"),
        table_html("guard-panel-machining-register.csv","Panel schedule"),
        table_html("base-anchor-register.csv","Base and anchoring interfaces"),
        table_html("structural-load-case-register.csv","Structural load cases"),
        table_html("structural-screen.csv","Completed calculation"),
        table_html("proof-plan.csv","Proof plan"),
        table_html("unresolved-inputs.csv","Selections still required"),
        table_html("candidate-bom.csv","Candidate BOM"),
    ])
    text=f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>HR-30 cell hardware P0.1</title><script type='module' src='https://ajax.googleapis.com/ajax/libs/model-viewer/4.0.0/model-viewer.min.js'></script><style>
:root{{--sky:#9ddcff;--blue:#082d67;--mid:#145ca8;--gold:#ffc83d;--ink:#0b1d35;--paper:#f7fbff;--hold:#fff1bf}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,sans-serif}}header{{background:linear-gradient(135deg,var(--blue),var(--mid));color:white;padding:clamp(28px,6vw,72px)}}header h1{{font-size:clamp(34px,6vw,72px);line-height:1;margin:.2em 0}}header p{{max-width:80ch}}.warning{{background:var(--gold);color:#241900;padding:16px;font-weight:800;border:3px solid #6d4d00}}main{{max-width:1500px;margin:auto;padding:clamp(18px,4vw,52px)}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px}}.card{{background:white;border:2px solid var(--blue);border-radius:16px;padding:20px;box-shadow:6px 6px 0 var(--sky)}}.metric{{font-size:clamp(28px,4vw,48px);font-weight:900;color:var(--blue)}}model-viewer{{width:100%;height:min(72vh,760px);min-height:520px;background:linear-gradient(#dff4ff,#fff);border:3px solid var(--blue);border-radius:18px}}section{{margin:46px 0}}h2{{font-size:clamp(26px,3vw,40px);color:var(--blue)}}.table-wrap{{overflow:auto;border:2px solid var(--blue);border-radius:12px;background:white}}table{{border-collapse:collapse;width:max-content;min-width:100%}}th,td{{padding:12px 14px;border-bottom:1px solid #a8c4e4;vertical-align:top;max-width:430px;white-space:normal}}th{{position:sticky;top:0;background:var(--blue);color:white;font-size:14px;text-align:left}}td{{font-size:16px}}a{{color:#064e9d;font-weight:750}}code{{font-size:16px}}@media(max-width:650px){{model-viewer{{min-height:430px}}th,td{{min-width:180px}}}}
</style></head><body><header><div class='warning'>{html.escape(WARNING)}</div><p>HR-30 / whole-body P0.1 / cell hardware</p><h1>The static cell now has buildable hardware.</h1><p>Framed doors, captured panels, physical joints, floor-mount interfaces, and a T-slot pelvis cradle surround the complete robot. This is a coherent construction candidate—not a structural approval.</p></header><main><section><div class='grid'><article class='card'><div class='metric'>{meta['profile_member_count']}</div><h2>profile members</h2><p>Main frame, doors, platform and cradle have exact cut lengths.</p></article><article class='card'><div class='metric'>{meta['joint_count']}</div><h2>defined joints</h2><p>Every modeled frame/door joint names its candidate purchased hardware.</p></article><article class='card'><div class='metric'>0</div><h2>released proof loads</h2><p>Dynamic, guard, anchor, door and tether loads still require physical inputs.</p></article></div></section><section><h2>Complete cell assembly</h2><model-viewer src='HR30_first_energization_cell_hardware_with_robot_candidate.glb' camera-controls shadow-intensity='1' exposure='1.05' camera-orbit='25deg 72deg 78%' interaction-prompt='auto'></model-viewer><p><a href='HR30_first_energization_cell_hardware_with_robot_candidate.step'>Download editable STEP</a> · <a href='HR30_first_energization_cell_hardware_candidate.step'>Download hardware-only STEP</a></p></section><section><h2>What this changes</h2><div class='grid'><article class='card'><h3>Framed doors</h3><p>Each clear infill is captured by four 40 mm profiles and carried by three profile-to-profile hinges. Magnetic catches receive no protective-interlock credit.</p></article><article class='card'><h3>Anchored base intent</h3><p>Caster hardware is rejected for E7. Four floor-mount interfaces and eight anchor locations are visible; exact anchors remain site-dependent.</p></article><article class='card'><h3>Calculated honestly</h3><p>The profile-only cradle screen uses the entire robot weight on one arm. No equal-sharing or arbitrary impact multiplier is credited.</p></article></div></section>{tables}</main></body></html>"""
    (OUT/"index.html").write_text(text,encoding="utf-8")


def integrate() -> None:
    status_path=WHOLE/"package-status.json"
    status=json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "first_energization_cell_hardware_present":True,"first_energization_cell_hardware_fastened_candidate":True,
        "first_energization_cell_hardware_framed_doors":True,"first_energization_cell_hardware_anchor_interfaces":True,
        "first_energization_cell_hardware_profile_screen_only":True,"first_energization_cell_hardware_released":False,
        "first_energization_cell_hardware_guard_validated":False,"first_energization_cell_hardware_restraint_rated":False,
        "fer_g02_closed":False,"fer_g10_closed":False,"fer_g11_closed":False,
    })
    status_path.write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    start,end="<!-- HR30-CELL-HARDWARE-P01-START -->","<!-- HR30-CELL-HARDWARE-P01-END -->"
    readme=WHOLE/"README.md"; text=readme.read_text(encoding="utf-8")
    if start in text and end in text: text=text.split(start,1)[0]+text.split(end,1)[1]
    block=f"""{start}
## Fastened first-energization-cell hardware

The [interactive hardware guide](first-energization-cell-hardware-p0.1/index.html) replaces the earlier loose-panel/caster concept with a **31-member fastened construction candidate**: framed doors, six captured 6 mm panels, 22 gusset brackets, 206 controlled fastener assemblies, six profile hinges, four floor-mount interfaces, a platform subframe, and a T-slot pelvis cradle. Purchased parts are modeled as interface envelopes, not machining sources. Floor anchors, guard impact, door interlocking, restraint dynamics, proof testing and FER-G02/G10/G11 remain open.
{end}
"""
    readme.write_text(text.rstrip()+"\n\n"+block,encoding="utf-8")
    page=WHOLE/"index.html"; text=page.read_text(encoding="utf-8")
    if start in text and end in text: text=text.split(start,1)[0]+text.split(end,1)[1]
    section=f"""{start}<section id='cell-hardware'><h2>The static cell now has physical construction hardware</h2><div class='grid'><article class='card pass'><div class='metric'>31</div><p>dimensioned T-slot members across frame, doors, platform and pelvis cradle.</p></article><article class='card pass'><h3>Framed and captured</h3><p>Both doors are profile-framed and all six clear panels have a controlled gasket path.</p></article><article class='card hold'><h3>Still unvalidated</h3><p>Anchors, guard impact, interlocking, restraint dynamics and proof loads remain open.</p></article></div><p><a href='first-energization-cell-hardware-p0.1/index.html'>Open the interactive hardware guide</a>.</p></section>{end}"""
    text=text.replace("</main>",section+"</main>",1); page.write_text(text,encoding="utf-8")


def manifest_release() -> None:
    shutil.copy2(Path(__file__),OUT/"first-energization-cell-hardware-source.py")
    files=[p for p in OUT.rglob("*") if p.is_file() and p.name!="file-manifest.csv"]
    write_csv(OUT/"file-manifest.csv",[{"path":p.relative_to(OUT).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p),"warning":WARNING} for p in sorted(files)])
    if RELEASE.exists(): shutil.rmtree(RELEASE)
    shutil.copytree(OUT,RELEASE)
    code="import sys;sys.path.insert(0,'tools');import generate_hr30_system_package_p01 as s;s.refresh_manifest_and_release()"
    result=subprocess.run([str(CAD_PYTHON),"-c",code],cwd=ROOT)
    if result.returncode: raise RuntimeError("whole-body manifest/release refresh failed")


def main() -> int:
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    print("cell hardware: CAD and registers",flush=True)
    meta=build_cad()
    publish(meta)
    integrate()
    manifest_release()
    print(json.dumps({"identifier":IDENTIFIER,**meta,"authorities":0},indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
