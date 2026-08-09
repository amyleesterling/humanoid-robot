#!/usr/bin/env python3
"""Generate the P0.3 carrier and supplier-neutral DFM inquiry package.

P0.3 preserves the R158 RPW geometry, raises the native board-rule floor to
the screened provider minimums, adds three board-level fiducials and creates a
controlled, non-authorizing DFM / first-article inquiry package.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path

import pcbnew

import generate_hr_v0_dxl_protection_carrier_p02 as p02


base = p02.base
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "electrical" / "kicad" / "hr-v0-dxl-protection-carrier-p0.3"
RELEASE = ROOT / "release" / "hr-v0" / "dxl-protection-carrier-p0.3"
MFG = ROOT / "electrical" / "manufacturing" / "hr-v0-dxl-protection-carrier-dfm-p0.1"
PROJECT = "hr-v0-dxl-protection-carrier-p0.3"
IDENTIFIER = "HR-V0-DXL-PROT-CARRIER-P0.3"
DFM_IDENTIFIER = "HR-V0-DXL-PROT-DFM-P0.1"
ROUND = "R159"
DATE = "2026-08-09"
WARNING = base.WARNING
MACROFAB_URL = "https://www.macrofab.com/capabilities"

base.OUT = OUT
base.RELEASE = RELEASE
base.PROJECT = PROJECT
base.IDENTIFIER = IDENTIFIER
base.REVISION = "DXL-PROT-CARRIER-P0.3"
base.SILK_REVISION = "P0.3"
base.DATE = DATE
p02.OUT = OUT
p02.RELEASE = RELEASE
p02.PROJECT = PROJECT


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def circuit_fingerprint(path: Path) -> str:
    board = pcbnew.LoadBoard(str(path))
    tracks = []
    vias = []
    for item in board.GetTracks():
        net = item.GetNetname()
        if isinstance(item, pcbnew.PCB_VIA):
            position = item.GetPosition()
            vias.append((net, position.x, position.y, item.GetWidth(pcbnew.F_Cu), item.GetDrillValue(), item.TopLayer(), item.BottomLayer()))
        else:
            start, end = item.GetStart(), item.GetEnd()
            tracks.append((net, item.GetLayer(), start.x, start.y, end.x, end.y, item.GetWidth()))
    pads = []
    for footprint in board.GetFootprints():
        if footprint.GetReference().startswith("FD"):
            continue
        for pad in footprint.Pads():
            position, size, drill = pad.GetPosition(), pad.GetSize(), pad.GetDrillSize()
            layers = tuple(layer for layer in range(pcbnew.PCB_LAYER_ID_COUNT) if pad.GetLayerSet().Contains(layer))
            pads.append((footprint.GetReference(), pad.GetNumber(), position.x, position.y, size.x, size.y, drill.x, drill.y, int(pad.GetShape()), pad.GetNetname(), layers))
    edges = []
    for drawing in board.GetDrawings():
        if drawing.GetLayer() == pcbnew.Edge_Cuts and isinstance(drawing, pcbnew.PCB_SHAPE):
            start, end = drawing.GetStart(), drawing.GetEnd()
            edges.append((int(drawing.GetShape()), start.x, start.y, end.x, end.y, drawing.GetWidth()))
    zones = []
    for zone in board.Zones():
        bounds = zone.GetBoundingBox()
        zones.append((zone.GetNetname(), zone.GetLayer(), bounds.GetX(), bounds.GetY(), bounds.GetWidth(), bounds.GetHeight(), zone.GetLocalClearance(), zone.GetMinThickness()))
    payload = {
        "tracks": sorted(tracks), "vias": sorted(vias), "pads_excluding_fiducials": sorted(pads),
        "edges": sorted(edges), "zones": sorted(zones), "copper_layers": board.GetCopperLayerCount(),
        "thickness": board.GetDesignSettings().GetBoardThickness(),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest().upper()


def add_fiducial(board: pcbnew.BOARD, reference: str, x: float, y: float) -> None:
    footprint = pcbnew.FOOTPRINT(board)
    footprint.SetReference(reference)
    footprint.SetValue("BOARD-LEVEL GLOBAL FIDUCIAL 1.0/2.0 mm; PROVIDER DFM REQUIRED")
    footprint.SetPosition(pcbnew.VECTOR2I_MM(x, y))
    footprint.SetBoardOnly(True)
    footprint.SetExcludedFromBOM(True)
    footprint.SetExcludedFromPosFiles(True)
    footprint.Reference().SetVisible(False)
    pad = pcbnew.PAD(footprint)
    pad.SetNumber("")
    pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    pad.SetSize(pcbnew.VECTOR2I_MM(1.0, 1.0))
    layers = pcbnew.LSET()
    layers.AddLayer(pcbnew.F_Cu)
    layers.AddLayer(pcbnew.F_Mask)
    pad.SetLayerSet(layers)
    pad.SetLocalSolderMaskMargin(pcbnew.FromMM(0.5))
    footprint.Add(pad)
    board.Add(footprint)


original_write_board = base.write_board


def write_board(items) -> None:
    original_write_board(items)
    board_path = OUT / f"{PROJECT}.kicad_pcb"
    board = pcbnew.LoadBoard(str(board_path))
    settings = board.GetDesignSettings()
    settings.m_MinClearance = pcbnew.FromMM(0.10)
    settings.m_SolderMaskMinWidth = pcbnew.FromMM(0.10)
    settings.m_TrackMinWidth = pcbnew.FromMM(0.15)
    settings.m_HoleClearance = pcbnew.FromMM(0.15)
    settings.m_NetSettings.GetDefaultNetclass().SetClearance(pcbnew.FromMM(0.10))
    for reference, x, y in (("FD1", 10.0, 10.0), ("FD2", 90.0, 10.0), ("FD3", 10.0, 50.0)):
        add_fiducial(board, reference, x, y)
    pcbnew.SaveBoard(str(board_path), board)


original_components = base.components


def components(model):
    items = original_components(model)
    for item in items:
        if item.ref == "U1":
            item.description = (
                "Forward current limiting only; reverse current remains unbounded while ON. "
                "P0.3 retains the R158/TI land geometry and adds manufacturing-rule/fiducial controls."
            )
            item.evidence = (
                "TI SLVSGA8B Rev B drawing 4225183/A; MacroFab live capability screen accessed 2026-08-09; "
                "provider response and application validation remain open."
            )
    return items


def board_metrics() -> dict[str, object]:
    board = pcbnew.LoadBoard(str(OUT / f"{PROJECT}.kicad_pcb"))
    tracks = list(board.GetTracks())
    vias = [item for item in tracks if isinstance(item, pcbnew.PCB_VIA)]
    segments = [item for item in tracks if not isinstance(item, pcbnew.PCB_VIA)]
    footprints = list(board.GetFootprints())
    pads = [pad for footprint in footprints for pad in footprint.Pads()]
    pth = [pad for pad in pads if pad.GetDrillSize().x > 0]
    settings = board.GetDesignSettings()
    edge_points = []
    for drawing in board.GetDrawings():
        if drawing.GetLayer() == pcbnew.Edge_Cuts and isinstance(drawing, pcbnew.PCB_SHAPE):
            edge_points.extend((drawing.GetStart(), drawing.GetEnd()))
    edge_x = [pcbnew.ToMM(point.x) for point in edge_points]
    edge_y = [pcbnew.ToMM(point.y) for point in edge_points]
    return {
        "identifier": IDENTIFIER,
        "review_round": ROUND,
        "board_width_mm": round(max(edge_x) - min(edge_x), 6),
        "board_height_mm": round(max(edge_y) - min(edge_y), 6),
        "board_thickness_mm": round(pcbnew.ToMM(settings.GetBoardThickness()), 6),
        "copper_layers": board.GetCopperLayerCount(),
        "footprints_total": len(footprints),
        "bom_placements": 20,
        "board_only_mounting_holes": 4,
        "board_only_global_fiducials": 3,
        "track_segments": len(segments),
        "vias": len(vias),
        "min_track_mm": min(round(pcbnew.ToMM(item.GetWidth()), 6) for item in segments),
        "max_track_mm": max(round(pcbnew.ToMM(item.GetWidth()), 6) for item in segments),
        "min_via_diameter_mm": min(round(pcbnew.ToMM(item.GetWidth(pcbnew.F_Cu)), 6) for item in vias),
        "min_via_drill_mm": min(round(pcbnew.ToMM(item.GetDrillValue()), 6) for item in vias),
        "min_via_annular_ring_mm": min(round((pcbnew.ToMM(item.GetWidth(pcbnew.F_Cu)) - pcbnew.ToMM(item.GetDrillValue())) / 2, 6) for item in vias),
        "min_pth_drill_mm": min(round(pcbnew.ToMM(pad.GetDrillSize().x), 6) for pad in pth),
        "minimum_clearance_rule_mm": round(pcbnew.ToMM(settings.m_MinClearance), 6),
        "default_clearance_rule_mm": round(pcbnew.ToMM(settings.m_NetSettings.GetDefaultNetclass().GetClearance()), 6),
        "minimum_track_rule_mm": round(pcbnew.ToMM(settings.m_TrackMinWidth), 6),
        "minimum_soldermask_dam_rule_mm": round(pcbnew.ToMM(settings.m_SolderMaskMinWidth), 6),
        "hole_clearance_rule_mm": round(pcbnew.ToMM(settings.m_HoleClearance), 6),
        "rpw_min_paste_aperture_mm": 0.225,
        "rpw_min_distinct_paste_gap_mm": 0.20,
        "rpw_min_distinct_mask_dam_mm": 0.10,
        "tests_executed": 0,
    }


def capability_rows(metrics: dict[str, object]) -> list[dict[str, object]]:
    rows = [
        ("CAP-001", "copper layers", "4", "2-36 layers", "INTERNAL SCREEN PASS", "provider configuration response still required", "lines 30-36, 62-65"),
        ("CAP-002", "board dimensions", "100 x 60 mm", "maximum 378.46 x 378.46 mm", "INTERNAL SCREEN PASS", "panelization and tooling rails open", "lines 104-108"),
        ("CAP-003", "board thickness", "1.6 mm", "1.6 mm standard; +/-10% at >=1.6 mm", "INTERNAL SCREEN PASS", "finished stackup and tolerance acceptance open", "lines 110-114, 204-208"),
        ("CAP-004", "leadless package pitch", "0.45 mm RPW QFN", "0.3 mm minimum QFN/TQFN pitch", "INTERNAL SCREEN PASS", "exact RPW footprint and process review open", "lines 155-159"),
        ("CAP-005", "assembly mix", "SMD plus PTH", "SMD and through-hole supported", "INTERNAL SCREEN PASS", "process order and hand/selective solder response open", "lines 145-153"),
        ("CAP-006", "minimum routed track", f"{metrics['min_track_mm']:.3f} mm", "0.0762 mm minimum", "INTERNAL SCREEN PASS", "provider CAM measurement required", "lines 186-193"),
        ("CAP-007", "minimum clearance rule", f"{metrics['minimum_clearance_rule_mm']:.3f} mm", "0.0762 mm minimum", "INTERNAL SCREEN PASS", "0.0238 mm rule margin; actual CAM DFM required", "lines 186-193"),
        ("CAP-008", "minimum via drill", f"{metrics['min_via_drill_mm']:.3f} mm", "0.1016 mm minimum drill", "INTERNAL SCREEN PASS", "finished drill and plating response open", "lines 190-195"),
        ("CAP-009", "minimum via annular ring", f"{metrics['min_via_annular_ring_mm']:.3f} mm", "0.0762 mm minimum", "INTERNAL SCREEN PASS", "provider CAM measurement required", "lines 190-195"),
        ("CAP-010", "minimum RPW paste aperture width", "0.225 mm", "0.1524 mm minimum", "INTERNAL SCREEN PASS", "stencil thickness and area-ratio review open", "lines 197-198"),
        ("CAP-011", "distinct RPW paste gap", "0.200 mm minimum; compound L apertures overlap intentionally", "0.1524 mm clearance", "PARTIAL - PROVIDER RESPONSE REQUIRED", "confirm compound aperture union and stencil web", "lines 197-198"),
        ("CAP-012", "minimum RPW soldermask dam", "0.100 mm", "0.100 mm minimum", "PARTIAL - AT PUBLISHED LIMIT", "no tolerance margin; provider acceptance mandatory", "lines 199-203"),
        ("CAP-013", "native soldermask dam rule", f"{metrics['minimum_soldermask_dam_rule_mm']:.3f} mm", "0.100 mm minimum", "INTERNAL RULE CORRECTED TO LIMIT", "P0.2 0.05 mm rule superseded by P0.3", "lines 199-203"),
        ("CAP-014", "global fiducials", "three 1.0 mm copper / 2.0 mm mask board fiducials", "provider page does not publish fiducial rule", "PARTIAL - PROVIDER RESPONSE REQUIRED", "confirm board/panel/local fiducial scheme", "provider response required"),
        ("CAP-015", "surface finish", "SELECTION REQUIRED", "ENIG standard; alternatives listed", "SELECTION REQUIRED", "provider must propose exact finish and thickness", "lines 67-75"),
        ("CAP-016", "laminate", "SELECTION REQUIRED", "FR4 Tg178.5 standard", "SELECTION REQUIRED", "provider must propose exact laminate/stackup", "lines 77-84"),
        ("CAP-017", "copper weight", "SELECTION REQUIRED", "0.5/1/2 oz listed", "SELECTION REQUIRED", "thermal/current/fault study and provider stackup required", "lines 86-91"),
        ("CAP-018", "dielectric stackup", "SELECTION REQUIRED", "default and custom stackups available", "SELECTION REQUIRED", "exact layer buildup and finished thickness required", "lines 62-65"),
        ("CAP-019", "SMT alloy/flux", "SELECTION REQUIRED", "SAC305; no-clean standard commercial", "SELECTION REQUIRED", "exact paste, flux, profile and cleaning response required", "lines 133-143"),
        ("CAP-020", "stencil", "TI example apertures encoded; thickness SELECTION REQUIRED", "screen/jet printing supported", "SELECTION REQUIRED", "stencil thickness, reductions, nano-coat and aperture disposition required", "lines 167-175"),
        ("CAP-021", "QFN inspection", "AOI plus X-ray requested for every first article", "AOI, first-article images, QFN X-ray listed", "PARTIAL - EXACT DELIVERABLES OPEN", "confirm image set, views, void/bridge criteria and traceability", "lines 232-239"),
        ("CAP-022", "workmanship class", "SELECTION REQUIRED", "IPC-A-610 Class 2; Class 3 available", "SELECTION REQUIRED", "qualified reviewer must select class and acceptance clauses", "lines 224-248"),
        ("CAP-023", "file intake", "Gerber/job, drill, BOM, position, native source available", "BOM/Gerber/native intake advertised", "INTERNAL SCREEN PASS", "provider-specific import report required", "lines 251-256"),
        ("CAP-024", "first-article build quantity", "three serialized evaluation variants proposed", "no minimum advertised", "PARTIAL - QUOTE REQUIRED", "lot split, serialization, tooling and first-article terms open", "lines 251-256"),
    ]
    return [
        {
            "capability_id": item[0], "feature": item[1], "p0_3_value": item[2],
            "provider_published_value": item[3], "screen_result": item[4], "required_closure": item[5],
            "official_source": MACROFAB_URL, "source_locator": item[6], "source_accessed": DATE,
            "provider_selected": "NO", "upload_authorized": "NO", "warning": WARNING,
        }
        for item in rows
    ]


def rfi_rows() -> list[dict[str, object]]:
    questions = [
        ("DFM-001", "Confirm exact 4-layer finished stackup, dielectric materials/thicknesses and finished board thickness tolerance."),
        ("DFM-002", "Confirm exact laminate manufacturer/grade/Tg and lot traceability."),
        ("DFM-003", "Propose outer/inner finished copper weights and confirm 3.0 mm power-route current/temperature review method."),
        ("DFM-004", "Propose surface finish and finished thickness for RPW0010A and JST VH solderability."),
        ("DFM-005", "Confirm all CAM-measured trace, spacing, annular-ring, drill and edge clearances with no silent edits."),
        ("DFM-006", "Confirm 0.100 mm minimum soldermask dams at the RPW pattern are manufacturable with process tolerance."),
        ("DFM-007", "State whether mask dams at the published minimum will be preserved or merged; identify every proposed CAM change."),
        ("DFM-008", "Confirm three board fiducials are sufficient and specify required panel/local fiducials and tooling rails."),
        ("DFM-009", "Confirm exact stencil thickness, alloy, paste type, flux and aperture modification for the TI RPW example."),
        ("DFM-010", "Confirm whether overlapping corner paste primitives are unioned as intended and provide final stencil aperture data."),
        ("DFM-011", "Confirm center-pad 82% and corner-pad 93% TI example paste treatment or return a redlined alternative."),
        ("DFM-012", "Provide solder-paste inspection coverage and acceptance evidence for the RPW deposits."),
        ("DFM-013", "Provide AOI coverage and images for every serialized first article."),
        ("DFM-014", "Provide QFN X-ray views for every serialized first article and propose void/bridge/insufficient-solder criteria."),
        ("DFM-015", "Confirm reflow profile development, thermocouple locations and profile record availability."),
        ("DFM-016", "Confirm PTH JST VH and Keystone test-point process, order after SMT, cleaning and inspection."),
        ("DFM-017", "Confirm no-clean/water-soluble choice, cleaning process and ionic-residue evidence if applicable."),
        ("DFM-018", "Confirm exact workmanship standard/class and any exclusions; do not infer Project Button acceptance."),
        ("DFM-019", "Confirm component sourcing channels, date/lot traceability and prohibition on unapproved alternates."),
        ("DFM-020", "Confirm serialization method linking PCB lot, assembly lot, BOM variant and inspection records."),
        ("DFM-021", "Return the provider-imported BOM and placement data for exact reference/MPN/rotation reconciliation."),
        ("DFM-022", "Return DFM/DFA report and every proposed file, footprint, mask, paste, drill or outline modification."),
        ("DFM-023", "Quote fabrication/assembly/inspection separately for two 1.65 k and one 3.32 k evaluation variants."),
        ("DFM-024", "State first-article hold/review point: no remaining units proceed until written Project Button disposition."),
    ]
    return [
        {
            "question_id": key, "question": question, "priority": "BLOCKING",
            "transmission_state": "NOT SENT", "provider_response": "SELECTION REQUIRED",
            "response_evidence_uri": "", "project_disposition": "OPEN",
            "upload_authorized": "NO", "quotation_authorized": "NO", "order_authorized": "NO", "warning": WARNING,
        }
        for key, question in questions
    ]


def first_article_rows() -> list[dict[str, object]]:
    checks = [
        "received quantity, serialization and variant identity", "bare-board dimensions/thickness and damage",
        "fabrication lot and stackup certificate", "component MPN/date-lot/alternate reconciliation",
        "provider-imported placement/rotation parity", "RPW pin-1 orientation", "RPW solder-paste inspection record",
        "RPW AOI images", "RPW X-ray top and oblique views", "RPW void/bridge/insufficient-solder disposition",
        "PTH JST/test-point solder inspection", "cleanliness/flux process record", "unpowered resistance/short screen",
        "point-to-point continuity and polarity", "isolation/no-backfeed unpowered screen", "rework/deviation record",
        "independent engineering disposition", "configuration-manager release or quarantine decision",
    ]
    return [
        {
            "check_id": f"FAI-{index:03d}", "check": check, "acceptance_criterion": "SELECTION REQUIRED",
            "execution_state": "NOT EXECUTED", "result": "", "evidence_uri": "", "inspector": "SELECTION REQUIRED",
            "independent_reviewer": "SELECTION REQUIRED", "article_released": "NO", "warning": WARNING,
        }
        for index, check in enumerate(checks, 1)
    ]


def submission_rows() -> list[dict[str, object]]:
    candidates: list[tuple[Path, str]] = []
    for path in sorted((RELEASE / "cam" / "gerbers").glob("*")):
        candidates.append((path, "fabrication_gerber_or_job"))
    for path in sorted((RELEASE / "cam" / "drill").glob("*.drl")):
        candidates.append((path, "fabrication_drill"))
    candidates.extend([
        (RELEASE / "cam" / f"{PROJECT}-all-pos.csv", "assembly_position"),
        (OUT / "bom.csv", "assembly_bom"),
        (RELEASE / "assembly-variants.csv", "assembly_variant_control"),
        (RELEASE / "footprint-audit.csv", "critical_footprint_control"),
        (RELEASE / "rpw-land-pattern-parity.csv", "critical_footprint_control"),
        (OUT / f"{PROJECT}.kicad_pcb", "native_ecad"),
        (OUT / "ProjectButton_RPW.pretty" / f"{p02.FOOTPRINT_NAME}.kicad_mod", "native_footprint"),
        (RELEASE / "output" / f"{PROJECT}-top.png", "assembly_reference_render"),
        (RELEASE / "validation" / f"{PROJECT}-drc.rpt", "internal_validation_only"),
    ])
    rows = []
    for path, role in candidates:
        rows.append({
            "file_id": f"SUB-{len(rows)+1:03d}", "role": role,
            "repository_path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path),
            "size_bytes": path.stat().st_size, "transmission_state": "NOT UPLOADED",
            "upload_authorized": "NO", "provider_import_verified": "NO", "warning": WARNING,
        })
    return rows


original_release_files = base.release_files


def release_files(items) -> None:
    original_release_files(items)
    # Convert inherited R158 record identifiers to this separately versioned pass.
    for filename in ("residual-holds.csv", "test-plan.csv", "test-data-template.csv"):
        path = RELEASE / filename
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace("R158-", "R159-"), encoding="utf-8")
    status_path = RELEASE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "identifier": IDENTIFIER, "review_round": ROUND,
        "configuration_state": "DFM-INQUIRY NATIVE CARRIER CANDIDATE",
        "p0_2_native_rule_superseded": True, "board_only_global_fiducials": 3,
        "provider_selected": False, "provider_contacted": False, "files_uploaded": False,
        "quotation_requested": False, "quotation_received": False, "order_authorized": False,
        "tests_executed": 0,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    metrics = board_metrics()
    MFG.mkdir(parents=True, exist_ok=True)
    (MFG / "board-rule-metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    p02_board = ROOT / "electrical" / "kicad" / "hr-v0-dxl-protection-carrier-p0.2" / "hr-v0-dxl-protection-carrier-p0.2.kicad_pcb"
    p03_board = OUT / f"{PROJECT}.kicad_pcb"
    p02_fingerprint = circuit_fingerprint(p02_board)
    p03_fingerprint = circuit_fingerprint(p03_board)
    parity = {
        "identifier": "HR-V0-DXL-PROT-P02-P03-PARITY-P0.1", "review_round": ROUND,
        "p0_2_board": p02_board.relative_to(ROOT).as_posix(), "p0_3_board": p03_board.relative_to(ROOT).as_posix(),
        "fingerprint_scope": "tracks, vias, all non-fiducial pads/nets, Edge.Cuts, zones, layer count and thickness",
        "excluded_intentional_changes": ["native design-rule values", "three FD* board-only fiducials", "revision/status text and metadata"],
        "p0_2_fingerprint_sha256": p02_fingerprint, "p0_3_fingerprint_sha256": p03_fingerprint,
        "circuit_geometry_parity": p02_fingerprint == p03_fingerprint, "physical_tests_executed": 0, "warning": WARNING,
    }
    (MFG / "p0.2-p0.3-circuit-parity.json").write_text(json.dumps(parity, indent=2) + "\n", encoding="utf-8")
    write_csv(MFG / "provider-capability-screen.csv", list(capability_rows(metrics)[0]), capability_rows(metrics))
    write_csv(MFG / "provider-rfi.csv", list(rfi_rows()[0]), rfi_rows())
    write_csv(MFG / "first-article-template.csv", list(first_article_rows()[0]), first_article_rows())
    write_csv(MFG / "submission-file-register.csv", list(submission_rows()[0]), submission_rows())
    source_rows = [
        {
            "source_id": "DFM-SRC-001", "organization": "MacroFab", "document": "Manufacturing capabilities",
            "revision": "live capability page; no document revision shown", "date": "accessed 2026-08-09",
            "url": MACROFAB_URL, "used_for": "provider-route capability screen only",
            "status": "PRIMARY PROVIDER SOURCE VERIFIED; PROVIDER NOT SELECTED", "warning": WARNING,
        },
        {
            "source_id": "DFM-SRC-002", "organization": "Texas Instruments", "document": "TPS25946 datasheet",
            "revision": "SLVSGA8B Rev B; package drawing 4225183/A", "date": "April 2022 / drawing 08/2019",
            "url": "https://www.ti.com/lit/ds/symlink/tps25946.pdf", "used_for": "RPW copper/mask/stencil geometry",
            "status": "PRIMARY MANUFACTURER SOURCE VERIFIED; APPLICATION NOT VALIDATED", "warning": WARNING,
        },
    ]
    write_csv(MFG / "source-register.csv", list(source_rows[0]), source_rows)
    dfm_status = {
        "identifier": DFM_IDENTIFIER, "carrier_identifier": IDENTIFIER, "review_round": ROUND, "date": DATE,
        "warning": WARNING, "preferred_inquiry_route": "MacroFab capability screen only",
        "provider_selected": False, "provider_contacted": False, "files_uploaded": False,
        "quotation_requested": False, "quotation_received": False, "purchase_authorized": False,
        "fabrication_authorized": False, "assembly_authorized": False, "connection_authorized": False,
        "energization_authorized": False, "functional_safety_credit": False,
        "physical_articles": 0, "tests_executed": 0, "qualified_approvals": 0,
    }
    (MFG / "package-status.json").write_text(json.dumps(dfm_status, indent=2) + "\n", encoding="utf-8")
    for path in MFG.iterdir():
        if path.is_file():
            shutil.copy2(path, RELEASE / path.name)
    write_readme()
    write_html()
    # Re-normalize after the inherited release writer and the new web guide.
    for path in list(RELEASE.rglob("*.svg")) + [RELEASE / "validation" / "kicad-cli.log"]:
        if path.exists():
            content = path.read_text(encoding="utf-8")
            path.write_text("\n".join(line.rstrip() for line in content.splitlines()) + "\n", encoding="utf-8")


def write_readme() -> None:
    (RELEASE / "README.md").write_text(f"""# {IDENTIFIER} / {DFM_IDENTIFIER}

**{WARNING}**

R159 retains R158's drawing-correct RPW geometry, corrects the native soldermask-dam rule from 0.05 mm to 0.10 mm, raises the clearance floor to 0.10 mm, adds three global board fiducials, and creates a controlled supplier-neutral DFM / first-article inquiry package.

MacroFab is only a preferred capability-screen route. No account action, upload, request, quotation, supplier selection, purchase, fabrication, assembly, connection or energization is authorized. Published capability is not project acceptance. Every provider answer, stackup, material, copper, finish, paste, workmanship, inspection and first-article disposition remains open.

The interactive guide is `index.html`; exact machine records are the CSV/JSON files in this directory. Generate with KiCad 10 Python using `tools/generate_hr_v0_dxl_protection_carrier_p03.py`.
""", encoding="utf-8")


def write_html() -> None:
    (RELEASE / "index.html").write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R159 carrier DFM inquiry</title><style>
:root{{--sky:#a8ddff;--deep:#082d5b;--blue:#155b98;--gold:#f5bd24;--paper:#f7fbff;--ink:#10243d;--line:#9bbbd5}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:18px/1.55 system-ui,sans-serif}}.warning{{background:var(--gold);padding:16px 20px;font-weight:850;border-bottom:4px solid var(--deep)}}header{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white;padding:clamp(28px,6vw,70px)}}h1{{font-size:clamp(34px,5vw,62px);line-height:1.05;margin:.3rem 0}}main{{max-width:1200px;margin:auto;padding:24px}}section{{background:white;border:2px solid var(--line);border-radius:16px;padding:20px;margin:20px 0}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}}.card{{border-left:8px solid var(--gold);padding:16px;background:#f8fcff}}h2{{font-size:clamp(25px,3vw,38px);color:var(--deep)}}h3{{font-size:22px}}img{{width:100%;border:2px solid var(--deep);border-radius:10px;background:white}}a{{color:#1557a5;font-weight:750}}.meta{{font-size:14px}}.deny{{color:#8b1e2d;font-weight:800}}@media(max-width:650px){{body{{font-size:16px}}main{{padding:14px}}}}
</style></head><body><div class="warning">{html.escape(WARNING)}</div><header><div class="meta">PROJECT BUTTON · {ROUND} · {IDENTIFIER}</div><h1>Ready for DFM questions—not production.</h1><p>P0.3 corrects the native manufacturing-rule floor, adds three global fiducials and binds every proposed supplier file to a hash. MacroFab is screened only as a possible North American PCBA inquiry route.</p></header><main>
<section><h2>What changed</h2><div class="grid"><div class="card"><h3>Rule correction</h3><p>P0.2 allowed a 0.05 mm soldermask dam in native DRC. P0.3 enforces 0.10 mm, matching the screened provider's published minimum.</p></div><div class="card"><h3>Registration</h3><p>Three 1.0 mm copper / 2.0 mm mask global fiducials are encoded. Panel and local-fiducial requirements remain a provider question.</p></div><div class="card"><h3>Fail closed</h3><p class="deny">0 uploads · 0 quotes · 0 orders · 0 articles · 0 tests · 0 approvals</p></div></div></section>
<section><h2>Provider screen</h2><p>Published capability is a screening input, not acceptance. At-limit mask geometry, compound paste apertures, exact stackup, materials and inspection deliverables require written disposition.</p><p><a href="provider-capability-screen.csv">24 capability rows</a> · <a href="source-register.csv">primary-source register</a> · <a href="board-rule-metrics.json">native board metrics</a></p></section>
<section><h2>Controlled inquiry</h2><p><a href="provider-rfi.csv">24 blocking DFM questions</a> · <a href="submission-file-register.csv">hash-bound proposed submission files</a> · <a href="first-article-template.csv">18 blank first-article checks</a> · <a href="package-status.json">denial state</a></p></section>
<section><h2>Native candidate</h2><div class="grid"><img src="output/{PROJECT}-top.png" alt="Top render of the P0.3 carrier with global fiducials"><img src="rpw-parity.svg" alt="RPW land-pattern comparison retained from R158"></div><p><a href="source/{PROJECT}.kicad_pro">KiCad project</a> · <a href="source/{PROJECT}.kicad_pcb">KiCad PCB</a> · <a href="validation/{PROJECT}-erc.rpt">ERC</a> · <a href="validation/{PROJECT}-drc.rpt">DRC</a></p></section>
</main></body></html>''', encoding="utf-8")


base.write_board = write_board
base.components = components
base.release_files = release_files
base.write_readme = write_readme
base.write_html = write_html


def main() -> int:
    if MFG.exists():
        shutil.rmtree(MFG)
    return base.main()


if __name__ == "__main__":
    raise SystemExit(main())
