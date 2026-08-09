"""Fail-closed checks for HR-V0-PNOZ-CONF-P0.1."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "electrical/vendor/pilz/pnoz-s4-750104-r116"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def net_nodes() -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for row in rows(ROOT / "electrical/kicad/project-button-v3/net-schedule.csv"):
        result[row["net"]] = set(row["connections"].split(" | "))
    return result


def main() -> int:
    manifest = rows(VENDOR / "source-manifest-p0.1.csv")
    assert len(manifest) == 1
    source = manifest[0]
    assert source["artifact_id"] == "R116-PILZ-001"
    assert source["manufacturer"] == "Pilz GmbH & Co. KG"
    assert source["order_code"] == "750104"
    assert source["document_edition"] == "21396-EN-23"
    assert source["portal_file_date"] == "2026-06-22"
    assert source["pdf_metadata_creation_date"] == "2026-06-17"
    assert source["access_date"] == "2026-08-08"
    pdf = VENDOR / "PNOZ_s4_21396-EN-23.pdf"
    assert pdf.is_file() and pdf.stat().st_size == int(source["size_bytes"]) == 2428340
    assert pdf.read_bytes().startswith(b"%PDF")
    assert sha256(pdf) == source["sha256"] == "4B6E4768CEFAEDAF54F006347D32A8A04964B59A16F3616D8AC43698D3626BB4"

    matrix = rows(ROOT / "safety/hr-v0-pnoz-path-conformance-p0.1.csv")
    assert [row["check_id"] for row in matrix] == [f"PZC-{i:03d}" for i in range(1, 15)]
    assert {row["disposition"] for row in matrix} == {"PARTIAL", "OPEN"}
    assert all(row["warning"] == WARNING for row in matrix)
    assert not any(row["disposition"] in {"CLOSED", "RELEASED", "APPROVED", "PASS"} for row in matrix)

    nets = net_nodes()
    expected = {
        "SR1_S12": {"02_estop_eligibility.kicad_sch:S0:R-2", "02_estop_eligibility.kicad_sch:SR1:S12", "02_estop_eligibility.kicad_sch:S1:TBD-R1"},
        "SR1_START_RETURN": {"02_estop_eligibility.kicad_sch:SR1:S34", "02_estop_eligibility.kicad_sch:S1:TBD-R2"},
        "SRA1_S11": {"02_estop_eligibility.kicad_sch:SR1:13", "03_arm_watchdog_eligibility.kicad_sch:SRA1:S11"},
        "SRA1_S12": {"02_estop_eligibility.kicad_sch:SR1:14", "03_arm_watchdog_eligibility.kicad_sch:SRA1:S12", "03_arm_watchdog_eligibility.kicad_sch:S2:TBD-A1"},
        "ARM_AFTER_S2": {"03_arm_watchdog_eligibility.kicad_sch:S2:TBD-A2", "04_contactor_edm.kicad_sch:K1:21"},
        "EDM_K1_OUT": {"04_contactor_edm.kicad_sch:K1:22", "04_contactor_edm.kicad_sch:K2:21"},
        "SRA1_START_RETURN": {"03_arm_watchdog_eligibility.kicad_sch:SRA1:S34", "04_contactor_edm.kicad_sch:K2:22"},
        "SR1_A1_WD_GATED": {"02_estop_eligibility.kicad_sch:SR1:A1", "03_arm_watchdog_eligibility.kicad_sch:KWD2:14"},
    }
    for net, nodes in expected.items():
        assert nets[net] == nodes, (net, nets[net], nodes)
    assert all("KWD" not in node for net in ("SR1_S12", "SR1_S22") for node in nets[net])

    generator = (ROOT / "tools/generate_hr_v0_electrical_v3.py").read_text(encoding="utf-8")
    for token in ("21396-EN-23", "4B6E4768CEFAEDAF54F006347D32A8A04964B59A16F3616D8AC43698D3626BB4", "rechecked 2026-08-08"):
        assert token in generator

    doc = (ROOT / "docs/hr-v0-pnoz-path-conformance-p0.1.md").read_text(encoding="utf-8")
    for token in (WARNING, "Project Button Electrical V3-P1.13", "S1:TBD-R1/TBD-R2", "ZERO SAFETY CREDIT", "Clean ERC does not close"):
        assert token in doc
    guide = (ROOT / "release/hr-v0/pnoz-path-conformance-p0.1/index.html").read_text(encoding="utf-8")
    for token in (WARNING, "font:16px", "font-size:14px", "font-size:12px", "data-filter", "addEventListener", "ZERO SAFETY CREDIT"):
        assert token in guide

    print("HR-V0 PNOZ path conformance P0.1 check passed: source hash and exact V3 terminal paths controlled")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
