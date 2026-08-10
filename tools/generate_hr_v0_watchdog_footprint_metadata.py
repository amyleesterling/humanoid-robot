"""Generate the R138 critical-IC footprint metadata evidence package.

Run with KiCad 10's bundled Python. ``--capture-baseline`` is a controlled
one-time operation used before the metadata-only PCB regeneration.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
from pathlib import Path

import pcbnew

from hr_v0_watchdog_footprint_metadata import FOOTPRINT_METADATA, WARNING


ROOT = Path(__file__).resolve().parents[1]
BOARD = ROOT / "electrical" / "kicad" / "project-button-v3" / "project-button-v3.kicad_pcb"
OUT = ROOT / "electrical" / "manufacturing" / "hr-v0-watchdog-footprint-metadata-p0.1"
WEB = ROOT / "release" / "hr-v0" / "watchdog-footprint-metadata-p0.1"
BASELINE = OUT / "pcb-p0.7-geometry-topology-baseline.json"
IDENTIFIER = "HR-V0-WD-IC-META-P0.1"


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def point(value) -> list[int]:
    return [int(value.x), int(value.y)]


def snapshot(board) -> dict:
    """Return a field-independent native geometry/topology representation."""
    footprints = []
    for fp in sorted(board.GetFootprints(), key=lambda item: item.GetReference()):
        pads = []
        for pad in sorted(fp.Pads(), key=lambda item: (item.GetNumber(), item.GetPosition().x, item.GetPosition().y)):
            pads.append({
                "number": pad.GetNumber(),
                "position_nm": point(pad.GetPosition()),
                "size_nm": point(pad.GetSize()),
                "drill_nm": point(pad.GetDrillSize()),
                "shape": int(pad.GetShape()),
                "attribute": int(pad.GetAttribute()),
                "layers": pad.GetLayerSet().FmtHex(),
                "net": pad.GetNetname(),
            })
        footprints.append({
            "reference": fp.GetReference(),
            "library_item": str(fp.GetFPID().GetLibItemName()),
            "position_nm": point(fp.GetPosition()),
            "orientation_deg": round(fp.GetOrientationDegrees(), 9),
            "layer": int(fp.GetLayer()),
            "pads": pads,
        })

    tracks = []
    for item in board.GetTracks():
        is_via = isinstance(item, pcbnew.PCB_VIA)
        row = {
            "kind": "via" if is_via else "segment",
            "start_nm": point(item.GetStart()),
            "end_nm": point(item.GetEnd()),
            "width_nm": int(item.GetWidth(pcbnew.F_Cu) if is_via else item.GetWidth()),
            "layer": int(item.GetLayer()),
            "net": item.GetNetname(),
        }
        if is_via:
            row["drill_nm"] = int(item.GetDrillValue())
            row["layers"] = item.GetLayerSet().FmtHex()
        tracks.append(row)
    tracks.sort(key=lambda row: json.dumps(row, sort_keys=True))

    edges = []
    for item in board.GetDrawings():
        if item.GetLayer() == pcbnew.Edge_Cuts:
            edges.append({
                "shape": int(item.GetShape()),
                "start_nm": point(item.GetStart()),
                "end_nm": point(item.GetEnd()),
                "width_nm": int(item.GetWidth()),
            })
    edges.sort(key=lambda row: json.dumps(row, sort_keys=True))

    zones = []
    for zone in board.Zones():
        outlines = []
        poly = zone.Outline()
        for index in range(poly.OutlineCount()):
            chain = poly.COutline(index)
            outlines.append([point(chain.CPoint(vertex)) for vertex in range(chain.PointCount())])
        zones.append({
            "net": zone.GetNetname(),
            "layers": zone.GetLayerSet().FmtHex(),
            "outlines_nm": outlines,
        })
    zones.sort(key=lambda row: json.dumps(row, sort_keys=True))
    return {"footprints": footprints, "tracks_and_vias": tracks, "edge_cuts": edges, "zones": zones}


def digest_snapshot(data: dict) -> str:
    return sha256_bytes(json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture-baseline", action="store_true")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    WEB.mkdir(parents=True, exist_ok=True)
    board = pcbnew.LoadBoard(str(BOARD))
    current = snapshot(board)
    current_digest = digest_snapshot(current)

    if args.capture_baseline:
        payload = {
            "configuration": "PCB-P0.7 / Electrical V3-P1.13 before R138 metadata",
            "purpose": "field-independent geometry/topology baseline",
            "snapshot_sha256": current_digest,
            "snapshot": current,
            "warning": WARNING,
        }
        BASELINE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"captured {BASELINE.relative_to(ROOT)} {current_digest}")
        return 0

    if not BASELINE.exists():
        raise RuntimeError("controlled P0.7 geometry/topology baseline is absent")
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    parity = baseline["snapshot_sha256"] == current_digest and baseline["snapshot"] == current
    (OUT / "pcb-p0.8-geometry-topology-current.json").write_text(
        json.dumps({"snapshot_sha256": current_digest, "snapshot": current, "warning": WARNING}, indent=2) + "\n",
        encoding="utf-8",
    )
    comparison = {
        "identifier": IDENTIFIER,
        "baseline_configuration": "PCB-P0.7 / Electrical V3-P1.13",
        "current_configuration": "PCB-P0.8 / Electrical V3-P1.14",
        "baseline_snapshot_sha256": baseline["snapshot_sha256"],
        "current_snapshot_sha256": current_digest,
        "geometry_topology_equal": parity,
        "compared_domains": ["footprint identity", "placement", "pad geometry", "pad net", "tracks", "vias", "Edge.Cuts", "zones"],
        "excluded_domains": ["footprint fields", "title-block metadata"],
        "warning": WARNING,
    }
    (OUT / "geometry-topology-parity.json").write_text(json.dumps(comparison, indent=2) + "\n", encoding="utf-8")

    footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}
    rows = []
    for ref, expected in FOOTPRINT_METADATA.items():
        fp = footprints[ref]
        for field, expected_value in expected.items():
            actual = fp.GetField(field).GetText() if fp.HasField(field) else ""
            rows.append({
                "reference": ref,
                "field": field,
                "expected_value": expected_value,
                "native_kicad_value": actual,
                "match": str(actual == expected_value).upper(),
                "field_visible": str(fp.GetField(field).IsVisible()).upper() if fp.HasField(field) else "N/A",
                "release_effect": "IDENTITY/EVIDENCE ONLY - NO PROCESS OR FABRICATION AUTHORITY",
                "warning": WARNING,
            })
    write_csv(OUT / "footprint-metadata-register.csv", rows)
    sources = [
        {"source_id": "ICMETA-SRC-001", "manufacturer": "Texas Instruments", "document": "TPL7407L datasheet SLRS066D and PW0016A drawing 4220204/B", "revision_date": "Rev D March 2016; package drawing December 2023", "official_url": "https://www.ti.com/lit/ds/symlink/tpl7407l.pdf", "controlled_use": "UDRV1/UDRV2 identity, package, pin-1 and example-land basis", "boundary": "assembly process remains SELECTION REQUIRED", "warning": WARNING},
        {"source_id": "ICMETA-SRC-002", "manufacturer": "Texas Instruments", "document": "ISO1212 datasheet SLLSEY7G and DBQ0016A drawing 4214846/A", "revision_date": "Rev G February 2025; package drawing March 2014", "official_url": "https://www.ti.com/lit/ds/symlink/iso1212.pdf", "controlled_use": "UFB1 identity, package, pin-1 and example-land basis", "boundary": "R0.05 pad corner and assembly process remain project-controlled/open", "warning": WARNING},
        {"source_id": "ICMETA-SRC-003", "manufacturer": "Vishay", "document": "VO618A datasheet 83432", "revision_date": "Rev 2.1 / 22 January 2025", "official_url": "https://www.vishay.com/docs/83432/vo618a.pdf", "controlled_use": "ISO1 option-7 identity, package, pin-1 and dimensioned land basis", "boundary": "assembly process remains SELECTION REQUIRED", "warning": WARNING},
    ]
    write_csv(OUT / "source-register.csv", sources)
    status = {
        "identifier": IDENTIFIER,
        "round": "R138",
        "board": "PCB-P0.8 / Electrical V3-P1.14",
        "critical_references": 4,
        "native_fields": len(rows),
        "geometry_topology_equal_to_p0_7": parity,
        "copper_changed": False,
        "placement_changed": False,
        "nets_changed": False,
        "assembly_process_selected": False,
        "fabrication_authorized": False,
        "energization_authorized": False,
        "safety_credit": False,
        "warning": WARNING,
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    cards = []
    for ref, fields in FOOTPRINT_METADATA.items():
        cards.append(f'<article><h2>{ref}</h2><p><strong>{html.escape(fields["ManufacturerPartNumber"])}</strong><br>{html.escape(fields["PackageCode"])}</p><p>{html.escape(fields["LandBasis"])}</p><p class="hold">Assembly process: SELECTION REQUIRED</p></article>')
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{IDENTIFIER}</title><style>
body{{margin:0;font:16px/1.55 system-ui,sans-serif;color:#09294f;background:#f3f9ff}}.warn{{padding:14px 5vw;background:#f4bd28;color:#071c36;font-weight:800}}header,main,footer{{padding:28px 5vw}}header{{background:#8ed5ff}}h1{{font-size:clamp(30px,5vw,56px);line-height:1.05;max-width:950px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px}}article{{background:white;border:2px solid #0d579c;border-radius:14px;padding:20px}}.metric{{font-size:22px;font-weight:750}}.hold{{color:#7b4200;font-weight:750}}a{{color:#064f91}}footer{{background:#082f5b;color:white;margin-top:30px}}
</style></head><body><div class="warn">{WARNING}</div><header><p>{IDENTIFIER} · R138 · PCB-P0.8</p><h1>Critical IC identity now travels with the native board.</h1><p class="metric">4 references · {len(rows)} native fields · geometry/topology digest equal: {str(parity).upper()}</p><p>This correction adds manufacturer, exact part, package, document and land-basis fields. It does not select paste, stencil, reflow, cleaning, inspection, fabrication, assembly or energization.</p></header><main><div class="grid">{''.join(cards)}</div><h2>Evidence</h2><p><a href="../../../electrical/manufacturing/hr-v0-watchdog-footprint-metadata-p0.1/footprint-metadata-register.csv">Native-field register</a> · <a href="../../../electrical/manufacturing/hr-v0-watchdog-footprint-metadata-p0.1/geometry-topology-parity.json">Geometry/topology parity</a> · <a href="../../../electrical/manufacturing/hr-v0-watchdog-footprint-metadata-p0.1/source-register.csv">Primary-source register</a> · <a href="../../../electrical/manufacturing/hr-v0-watchdog-footprint-metadata-p0.1/package-status.json">Package status</a></p></main><footer>{WARNING}. No supplier upload, quotation, fabrication, assembly, connection or energization authority.</footer></body></html>'''
    (WEB / "index.html").write_text(page, encoding="utf-8")
    print(f"{IDENTIFIER}: {len(rows)} native fields; geometry/topology parity={parity}")
    return 0 if parity else 1


if __name__ == "__main__":
    raise SystemExit(main())
