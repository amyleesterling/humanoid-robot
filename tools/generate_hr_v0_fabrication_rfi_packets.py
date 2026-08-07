"""Generate the fail-closed R53 withdrawal record for HR-V0 fabrication RFIs."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release" / "hr-v0" / "fabrication-rfi"
REVISION = "HR-V0-FAB-RFI-P0.2-WITHDRAWN"
WARNING = "WITHDRAWN - INVALID ARM INTERFACE GEOMETRY - DO NOT QUOTE OR FABRICATE"


ROWS = (
    ("RFI-001", "FAB-001;FAB-002", "WITHDRAWN", "P0.1 finished geometry assumed coplanar H101/S102 interfaces; exact vendor STEP disproves that assumption"),
    ("RFI-002", "FAB-003 profile operation only", "WITHDRAWN", "P0.1 blanks derive from the same invalid flat-link architecture"),
    ("RFI-003", "FAB-004 local secondary operation", "WITHDRAWN", "P0.1 blank and finished context derive from the same invalid flat-link architecture"),
    ("RFI-004", "FAB-005", "WITHDRAWN", "No structural prototype route is active"),
    ("RFI-005", "FAB-006", "WITHDRAWN", "No structural-metal assignment is active"),
    ("RFI-006", "FAB-007", "SITE HOLD", "MV0-004 remains blocked by the exact Boston bench survey"),
)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for path in OUT.glob("*.zip"):
        path.unlink()
    index = OUT / "withdrawal-register.csv"
    with index.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("packet_id", "routes", "state", "reason", "superseded_revision", "replacement_condition"))
        for packet_id, routes, state, reason in ROWS:
            writer.writerow((packet_id, routes, state, reason, "HR-V0-FAB-RFI-P0.1", "Released replacement arm architecture and separately authorized inquiry packet"))
    readme = OUT / "WITHDRAWN.md"
    readme.write_text(
        "# HR-V0 fabrication inquiry withdrawal\n\n"
        "**WITHDRAWN - INVALID ARM INTERFACE GEOMETRY - DO NOT QUOTE OR FABRICATE**\n\n"
        "R53 withdrew every P0.1 supplier ZIP after exact ROBOTIS STEP geometry showed that the "
        "FR13-H101K output frame and FR13-S102K body frame do not provide the coplanar interfaces "
        "assumed by MV0-001 and MV0-003. The ZIP bytes remain recoverable in Git history at R52 "
        "commit `978119f`; they are not current engineering inputs.\n\n"
        "No replacement packet may be generated until `MECH-005` / `AUDIT-MECH-012` close with a "
        "released exact-coordinate assembly, parallel-axis proof, collision/tool-access review, "
        "load path, drawings, tolerances and qualified mechanical disposition. MV0-004 remains on "
        "its separate Boston bench-site hold.\n",
        encoding="utf-8",
        newline="\n",
    )
    old_index = OUT / "packet-index.csv"
    if old_index.exists():
        old_index.unlink()
    print(f"Generated {REVISION}: 0 active ZIPs; {len(ROWS)} withdrawal/hold records")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
