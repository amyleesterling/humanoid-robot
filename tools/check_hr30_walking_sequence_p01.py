"""Check the HR-30 P0.1 simulator-only whole-body walking sequences."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BODY = ROOT / "hr30" / "whole-body-p0.1"
SRC = BODY / "walking-sequence-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / "walking-sequence-p0.1"


def need(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    status = json.loads((SRC / "walking-sequence-status.json").read_text(encoding="utf-8"))
    sequences = rows(SRC / "trajectory-sequence-register.csv")
    keyframes = rows(SRC / "trajectory-keyframe-register.csv")
    samples = rows(SRC / "trajectory-samples.csv")
    joints = rows(SRC / "joint-trajectory.csv")
    mass_summary = json.loads((BODY / "mass-reconciliation-summary.json").read_text(encoding="utf-8"))
    expected_mass = float(mass_summary["active_tether_dynamics_planning_mass_kg"])
    need(status["dynamics_source"] == "hr30_tether.urdf" and abs(float(status["dynamics_mass_kg"]) - expected_mass) < 5e-6, "walking sequence is not bound to the active tether-first model")
    need(len(sequences) == 2 and {row["sequence_id"] for row in sequences} == {"WS-R01", "WS-L01"}, "bilateral sequence inventory incomplete")
    need(len(keyframes) == 12 and all(int(sum(row["sequence_id"] == seq for row in keyframes)) == 6 for seq in ("WS-R01", "WS-L01")), "bilateral keyframe inventory incomplete")
    need(len(samples) == int(status["sample_count"]) and len(joints) == len(samples) * 25 == int(status["joint_sample_count"]), "trajectory sample/joint cardinality drift")
    need(all(abs(float(row["mass_kg"]) - expected_mass) < 5e-6 for row in samples), "sample mass drift from tether-first dynamics")
    need(min(float(row["support_margin_mm"]) for row in samples) > 0.0, "a sample leaves its declared support polygon")
    need(min(float(row["swing_foot_clearance_mm"]) for row in samples) >= -0.02, "a sample penetrates the floor")
    need(max(float(row["velocity_limit_ratio"]) for row in joints) <= 1.0 + 1e-9, "a joint sample exceeds its URDF velocity limit")
    need(all(abs(float(row["final_forward_placement_mm"]) - 40.0) <= 0.02 for row in sequences), "bilateral 40 mm touchdown drift")
    for sequence_id in ("WS-R01", "WS-L01"):
        seq_samples = [row for row in samples if row["sequence_id"] == sequence_id]
        need(seq_samples[0]["support_mode"] == "DOUBLE" and seq_samples[-1]["support_mode"] == "DOUBLE", f"{sequence_id} does not start/end in double support")
        need(all(abs(float(b["time_s"]) - float(a["time_s"]) - 0.02) < 1e-7 for a, b in zip(seq_samples, seq_samples[1:])), f"{sequence_id} is not a continuous 50 Hz trajectory")
    mjcf = ET.parse(SRC / "hr30_tether_walking_keyframes.xml").getroot()
    keys = mjcf.findall("keyframe/key")
    need(len(keys) == 12 and all(len(key.attrib["qpos"].split()) == 32 for key in keys), "MJCF keyframe count/qpos width drift")
    preview = json.loads((SRC / "trajectory-preview.json").read_text(encoding="utf-8"))
    need(set(preview) == {"WS-R01", "WS-L01"} and all(len(value) > 50 for value in preview.values()), "interactive preview data incomplete")
    need(all(len(frame["links"]) == 26 for value in preview.values() for frame in value), "preview does not animate every body link")

    bindings = rows(SRC / "source-binding.csv")
    need(len(bindings) == 6, "source binding count drift")
    for row in bindings:
        path = ROOT / row["path"]
        need(path.exists() and sha(path) == row["sha256"], f"source binding drift: {row['role']}")
    need(sha(SRC / "walking-sequence-source.py") == sha(ROOT / "tools" / "generate_hr30_walking_sequence_p01.py"), "walking generator snapshot drift")

    page = (SRC / "index.html").read_text(encoding="utf-8")
    need(all(token in page for token in ("Interactive whole-body sequence", "trajectory-preview.json", "hr30_tether_walking_keyframes.xml", "HR-30_whole_body_pose_lineup_candidate.glb")), "interactive walking guide incomplete")
    css_sizes = [float(value) for value in re.findall(r"font-size\s*:\s*([0-9.]+)px", page)]
    need(not css_sizes or min(css_sizes) >= 12.0, "walking guide contains text below 12 px")
    need("font:17px" in page and "body{font-size:16px}" in page, "walking guide body/mobile legibility boundary missing")

    manifest = rows(SRC / "file-manifest.csv")
    expected = sorted(path.relative_to(SRC).as_posix() for path in SRC.rglob("*") if path.is_file() and path.name != "file-manifest.csv")
    need(sorted(row["path"] for row in manifest) == expected, "walking package manifest file set drift")
    for row in manifest:
        path = SRC / row["path"]
        need(path.stat().st_size == int(row["bytes"]) and sha(path) == row["sha256"], f"walking package manifest drift: {row['path']}")
    source_files = sorted(path.relative_to(SRC).as_posix() for path in SRC.rglob("*") if path.is_file())
    release_files = sorted(path.relative_to(REL).as_posix() for path in REL.rglob("*") if path.is_file())
    need(source_files == release_files, "walking source/release file set drift")
    need(all(sha(SRC / name) == sha(REL / name) for name in source_files), "walking source/release byte drift")

    body_status = json.loads((BODY / "package-status.json").read_text(encoding="utf-8"))
    need(body_status["whole_body_walking_sequence_present"] and body_status["walking_sequence_count"] == 2 and body_status["bilateral_grounded_touchdown_present"], "whole-body status does not expose walking sequence")
    authority_keys = ("hardware_command_encoding_present", "continuous_collision_validated", "balance_validated", "actuator_capacity_validated", "connection_authority", "powered_test_authority", "motion_authority", "walking_authority", "energization_authority")
    need(not any(bool(status[key]) for key in authority_keys), "walking package overclaims validation or authority")
    print(f"PASS: two bilateral 50 Hz tether-first step candidates, {len(samples)} body samples and {len(joints)} joint samples; minimum projected support margin {float(status['minimum_support_margin_mm']):.2f} mm, both grounded touchdowns 40 mm, zero physical execution or motion authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
