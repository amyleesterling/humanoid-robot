"""Generate deterministic, non-orderable HR-V0 fabrication capability packets."""

from __future__ import annotations

import csv
import hashlib
import io
import zipfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release" / "hr-v0" / "fabrication-rfi"
REVISION = "HR-V0-FAB-RFI-P0.1"
FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)
WARNING = "PRELIMINARY - CAPABILITY/DFM REQUEST ONLY - NOT A PURCHASE ORDER - DO NOT FABRICATE"


@dataclass(frozen=True)
class Packet:
    packet_id: str
    routes: str
    filename: str
    purpose: str
    inputs: tuple[str, ...]
    questions: tuple[str, ...]


FINISHED_STEPS = (
    "cad/hr-v0/generated/parts/MV0-001_upper_link_plate.step",
    "cad/hr-v0/generated/parts/MV0-002_forearm_link_plate.step",
    "cad/hr-v0/generated/parts/MV0-003_shoulder_adapter.step",
)
FINISHED_DRAWINGS = (
    "cad/hr-v0/generated/drawings/MV0-001_upper_link.svg",
    "cad/hr-v0/generated/drawings/MV0-002_forearm_link.svg",
    "cad/hr-v0/generated/drawings/MV0-003_adapter_s102.svg",
)
PROFILE_BLANKS = (
    "cad/hr-v0/generated/manufacturing-blanks/MV0-001_upper_link_PROFILE_ONLY_RFQ.dxf",
    "cad/hr-v0/generated/manufacturing-blanks/MV0-001_upper_link_PROFILE_ONLY_RFQ.step",
    "cad/hr-v0/generated/manufacturing-blanks/MV0-002_forearm_link_PROFILE_ONLY_RFQ.dxf",
    "cad/hr-v0/generated/manufacturing-blanks/MV0-002_forearm_link_PROFILE_ONLY_RFQ.step",
    "cad/hr-v0/generated/manufacturing-blanks/MV0-003_shoulder_adapter_PROFILE_ONLY_RFQ.dxf",
    "cad/hr-v0/generated/manufacturing-blanks/MV0-003_shoulder_adapter_PROFILE_ONLY_RFQ.step",
    "cad/hr-v0/generated/manufacturing-blanks/profile-only-blanks.csv",
    "cad/hr-v0/generated/manufacturing-blanks/HR-V0_profile-only-blank-RFQ-guide.svg",
)

PACKETS = (
    Packet(
        "RFI-001",
        "FAB-001;FAB-002",
        "HR-V0-RFI-FAB-001-002-one-stop-CNC-P0.1.zip",
        "Ask a one-stop CNC supplier whether it can machine the three candidate finished geometries and provide written DFM, inspection and material evidence.",
        FINISHED_STEPS + FINISHED_DRAWINGS,
        (
            "Can you supply certified 6061-T6 at the stated nominal thicknesses? If not, identify the exact proposed temper and consequences.",
            "Can your process hold the candidate 2.70 mm holes and a drawing-controlled location tolerance after those tolerances are released? State minimum achievable values.",
            "State stock-thickness tolerance, profile tolerance, flatness basis, edge/deburr condition and inspection method.",
            "State material-certificate and first-article inspection options, lead time, setup assumptions and budgetary cost.",
            "Identify every geometry, tolerance or documentation issue that must be resolved before a first-article order could be accepted.",
        ),
    ),
    Packet(
        "RFI-002",
        "FAB-003 profile operation only",
        "HR-V0-RFI-FAB-003-profile-blanks-P0.1.zip",
        "Ask a profile-cutting supplier about producing deliberately hole-free blanks only. No finished holes or secondary machining are requested.",
        PROFILE_BLANKS,
        (
            "Can you profile-cut these zero-hole 6061-T6 blanks at the stated nominal thicknesses without adding or inferring any holes?",
            "State available stock thicknesses/tolerances, profile tolerance, flatness basis, edge/deburr condition and material-certificate options.",
            "Identify process lead-in, tab, edge, minimum-radius or file-preparation changes required for a later controlled first-blank order.",
            "Provide budgetary cost and lead time for quantities 1, 1 and 1; this inquiry is not an order.",
        ),
    ),
    Packet(
        "RFI-003",
        "FAB-004 local secondary operation",
        "HR-V0-RFI-FAB-004-local-secondary-machining-P0.1.zip",
        "Ask a local shop whether it can fixture traceable profile blanks, drill/mill the later-released finished geometry and support inspection. No work is authorized.",
        PROFILE_BLANKS + FINISHED_STEPS + FINISHED_DRAWINGS,
        (
            "Identify the exact machine, workholding/datum strategy and operator/training route proposed for these parts.",
            "Can the shop machine candidate 2.70 mm holes after final sizes/locations/tolerances are released? State achievable size and position capability.",
            "Explain how blank identity and material traceability would be preserved across secondary machining.",
            "List available calibrated inspection equipment, FAI records, supervision, scheduling, insurance/site rules and estimated cost.",
            "Do not fabricate from this packet; return capability and DFM comments only.",
        ),
    ),
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=FIXED_ZIP_TIME)
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    return info


def manifest_bytes(packet: Packet) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(
        stream,
        fieldnames=("packet_path", "source_repo_path", "sha256", "size_bytes", "role"),
        lineterminator="\n",
    )
    writer.writeheader()
    for source in packet.inputs:
        data = (ROOT / source).read_bytes()
        writer.writerow(
            {
                "packet_path": f"payload/{source}",
                "source_repo_path": source,
                "sha256": sha256_bytes(data),
                "size_bytes": len(data),
                "role": "CAPABILITY/DFM INPUT - NOT FABRICATION RELEASE",
            }
        )
    return stream.getvalue().encode("utf-8")


def readme_bytes(packet: Packet) -> bytes:
    question_lines = "\n".join(f"{index}. {question}" for index, question in enumerate(packet.questions, start=1))
    text = f"""PROJECT BUTTON HR-V0 FABRICATION CAPABILITY / DFM INQUIRY

Packet: {packet.packet_id}
Routes: {packet.routes}
Revision: {REVISION}
Status: {WARNING}

PURPOSE
{packet.purpose}

AUTHORIZATION BOUNDARY
- This packet requests capability, DFM, budgetary cost and lead-time information only.
- It is not a purchase order, request to start work, fabrication release or first-article authorization.
- Dimensions and tolerance notes remain preliminary. Critical finished-hole size and location tolerances remain SELECTION REQUIRED.
- Do not fabricate, procure material, program production, or infer omitted geometry from this packet.
- Any later work requires a separately signed authorization tied to an exact repository commit, drawing revision and SHA-256 manifest.

QUESTIONS TO RETURN IN WRITING
{question_lines}

CONFIGURATION CONTROL
- MANIFEST.csv hashes every payload file. It intentionally excludes README-FIRST.txt and itself.
- The commit containing this packet plus its outer repository release manifest is the configuration record.
- Return all assumptions, substitutions and exceptions explicitly; silence is not acceptance.

{WARNING}
"""
    return text.encode("utf-8")


def write_packet(packet: Packet) -> dict[str, str | int]:
    output = OUT / packet.filename
    readme = readme_bytes(packet)
    manifest = manifest_bytes(packet)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as archive:
        archive.writestr(zip_info("README-FIRST.txt"), readme)
        archive.writestr(zip_info("MANIFEST.csv"), manifest)
        for source in packet.inputs:
            archive.writestr(zip_info(f"payload/{source}"), (ROOT / source).read_bytes())
    data = output.read_bytes()
    return {
        "packet_id": packet.packet_id,
        "routes": packet.routes,
        "artifact": output.relative_to(ROOT).as_posix(),
        "sha256": sha256_bytes(data),
        "size_bytes": len(data),
        "payload_file_count": len(packet.inputs),
        "permitted_action": "Return written capability DFM budgetary cost and lead time only",
        "forbidden_action": "No procurement material commitment programming fabrication or shipment",
        "state": "PRELIMINARY - INQUIRY ONLY",
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = [write_packet(packet) for packet in PACKETS]
    rows.extend(
        [
            {
                "packet_id": "RFI-004",
                "routes": "FAB-005",
                "artifact": "NOT GENERATED",
                "sha256": "",
                "size_bytes": 0,
                "payload_file_count": 0,
                "permitted_action": "Prototype or training capability discussion only",
                "forbidden_action": "No structural-part production assignment",
                "state": "PROTOTYPING ONLY",
            },
            {
                "packet_id": "RFI-005",
                "routes": "FAB-006",
                "artifact": "NOT GENERATED",
                "sha256": "",
                "size_bytes": 0,
                "payload_file_count": 0,
                "permitted_action": "Design support or nonstructural PLA aids only",
                "forbidden_action": "No structural-metal assignment",
                "state": "EXCLUDED FROM STRUCTURAL METAL ROUTE",
            },
            {
                "packet_id": "RFI-006",
                "routes": "FAB-007",
                "artifact": "NOT GENERATED - SITE HOLD",
                "sha256": "",
                "size_bytes": 0,
                "payload_file_count": 0,
                "permitted_action": "Execute Boston bench survey",
                "forbidden_action": "No MV0-004 quote or fabrication before geometry freeze",
                "state": "SITE HOLD",
            },
        ]
    )
    index_path = OUT / "packet-index.csv"
    with index_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generated {len(PACKETS)} deterministic inquiry packets and {index_path.relative_to(ROOT).as_posix()}")
    print(WARNING)


if __name__ == "__main__":
    main()
