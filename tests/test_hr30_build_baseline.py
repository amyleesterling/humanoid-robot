"""Synthetic counterexamples for the read-only planning audit, not hardware tests."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("baseline_audit", ROOT / "tools/check_hr30_build_baseline.py")
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)

class BaselineTests(unittest.TestCase):
    def setUp(self):
        self.lock = audit.read_json(ROOT / "hr30/build-release/baseline.lock.json")
        self.budget = audit.read_json(ROOT / "hr30/build-release/first-tranche-budget.json")
        self.status = {k: False for k in audit.FALSE_FIELDS}
        self.status.update(identifier=self.lock["baseline_id"], mass_kg=9.879813509,
                           margin_to_10kg_kg=10-9.879813509, mass_reconciled_link_count=26,
                           hip_transmission_ratio=4.0,
                           whole_body_step_sha256=self.lock["assets"]["whole_body_step"]["sha256"],
                           whole_body_glb_sha256=self.lock["assets"]["whole_body_glb"]["sha256"])
        self.rows = [dict(axis_id=a, peak_contact_inverse_torque_nm="1", rms_contact_inverse_torque_nm="0.5",
                          candidate_current_endpoint_nm="10", peak_to_current_endpoint_ratio="0.1")
                     for a in sorted(audit.ROTARY_AXES)]
        self.selected = next(r for r in self.rows if r["axis_id"] == "R_ANKLE_PITCH")
        self.selected.update(peak_contact_inverse_torque_nm="6.433361747", rms_contact_inverse_torque_nm="5.644891650",
                             candidate_current_endpoint_nm="7.571049000", peak_to_current_endpoint_ratio="0.849731886")
        self.alloc = [dict(axis_id=a, ratio="2.500:1") for a in sorted(audit.LEG_AXES) if not a.endswith("HIP_YAW")]
        for row in self.alloc:
            if row["axis_id"].endswith("HIP_PITCH"): row["ratio"] = "1.500:1"
            if row["axis_id"].endswith("HIP_ROLL"): row["ratio"] = "2.000:1"
        joint = next(r for r in self.alloc if r["axis_id"] == "R_ANKLE_PITCH")
        joint.update({k:self.lock["critical_joint"][k] for k in ("drive_id","motor_pulley","output_pulley","belt")})
        joint["horn_to_pulley_adapter"] = "MA-HN12-P8 - SYNTHETIC TEST ONLY"

    def run_analysis(self):
        return audit.analyze(self.status, self.rows, self.alloc, self.lock)

    def test_valid_synthetic_case(self):
        result = self.run_analysis()
        self.assertEqual(result["rotary_axes_checked"], 23)
        self.assertAlmostEqual(result["rms_to_manufacturer_heuristic_ratio"], 3.23953609756)
        self.assertFalse(result["build_release"])

    def test_missing_axis(self):
        self.rows.pop()
        with self.assertRaises(audit.AuditError): self.run_analysis()

    def test_duplicate_axis(self):
        self.rows.append(copy.deepcopy(self.rows[0]))
        with self.assertRaises(audit.AuditError): self.run_analysis()

    def test_unknown_axis_same_count(self):
        self.rows[0]["axis_id"] = "INVENTED"
        with self.assertRaises(audit.AuditError): self.run_analysis()

    def test_gripper_not_rotary_torque_row(self):
        self.rows[0]["axis_id"] = "R_GRIPPER"
        with self.assertRaises(audit.AuditError): self.run_analysis()

    def test_nan_rejected(self):
        self.selected["rms_contact_inverse_torque_nm"] = "NaN"
        with self.assertRaises(audit.AuditError): self.run_analysis()

    def test_infinity_rejected(self):
        self.selected["peak_contact_inverse_torque_nm"] = "Infinity"
        with self.assertRaises(audit.AuditError): self.run_analysis()

    def test_zero_endpoint(self):
        self.selected["candidate_current_endpoint_nm"] = "0"
        with self.assertRaises(audit.AuditError): self.run_analysis()

    def test_negative_rms(self):
        self.selected["rms_contact_inverse_torque_nm"] = "-1"
        with self.assertRaises(audit.AuditError): self.run_analysis()

    def test_rms_above_peak(self):
        self.selected["rms_contact_inverse_torque_nm"] = "7"
        with self.assertRaises(audit.AuditError): self.run_analysis()

    def test_wrong_ratio(self):
        self.selected["peak_to_current_endpoint_ratio"] = ".5"
        with self.assertRaises(audit.AuditError): self.run_analysis()

    def test_new_critical_axis_requires_review(self):
        other = next(r for r in self.rows if r["axis_id"] == "R_KNEE_PITCH")
        other.update(peak_contact_inverse_torque_nm="9.5", peak_to_current_endpoint_ratio=".95")
        with self.assertRaises(audit.AuditError): self.run_analysis()

    def test_authority_promotion_rejected(self):
        for key in audit.FALSE_FIELDS:
            with self.subTest(key=key):
                self.status[key] = True
                with self.assertRaises(audit.AuditError): self.run_analysis()
                self.status[key] = False

    def test_missing_false_is_not_false(self):
        self.status.pop("free_balance_validated")
        with self.assertRaises(audit.AuditError): self.run_analysis()

    def test_integer_false_not_accepted(self):
        self.lock["permissions"]["motion"] = 0
        with self.assertRaises(audit.AuditError): self.run_analysis()

    def test_no_silent_mass_revision(self):
        self.status["mass_kg"] = 9.928
        with self.assertRaises(audit.AuditError): self.run_analysis()

    def test_wrong_margin(self):
        self.status["margin_to_10kg_kg"] = 1
        with self.assertRaises(audit.AuditError): self.run_analysis()

    def test_hip_ratio_not_old(self):
        self.status["hip_transmission_ratio"] = 2
        with self.assertRaises(audit.AuditError): self.run_analysis()

    def test_historical_allocation_change_requires_disposition(self):
        next(r for r in self.alloc if r["axis_id"] == "R_HIP_PITCH")["ratio"] = "4.000:1"
        with self.assertRaises(audit.AuditError): self.run_analysis()

    def test_wrong_ankle_adapter(self):
        next(r for r in self.alloc if r["axis_id"] == "R_ANKLE_PITCH")["horn_to_pulley_adapter"] = "MA-HN13-P10 - knee"
        with self.assertRaises(audit.AuditError): self.run_analysis()

    def test_changed_geometry_binding(self):
        self.status["whole_body_step_sha256"] = "0"*64
        with self.assertRaises(audit.AuditError): self.run_analysis()

    def test_budget_totals(self):
        result = audit.budget_totals(self.budget)
        self.assertEqual(result["catalog_subtotal_usd"], "392.16")
        self.assertEqual(result["planning_low_usd"], "3542.16")
        self.assertEqual(result["planning_high_usd"], "8592.16")
        self.assertFalse(result["supplier_quote"])

    def test_budget_negative(self):
        self.budget["allowances"][0]["low_usd"] = "-1"
        with self.assertRaises(audit.AuditError): audit.budget_totals(self.budget)

    def test_budget_nan(self):
        self.budget["catalog_items"][0]["unit_usd"] = "NaN"
        with self.assertRaises(audit.AuditError): audit.budget_totals(self.budget)

    def test_budget_bool_quantity(self):
        self.budget["catalog_items"][0]["quantity"] = True
        with self.assertRaises(audit.AuditError): audit.budget_totals(self.budget)

    def test_budget_reversed_range(self):
        self.budget["allowances"][0]["low_usd"] = "99999"
        with self.assertRaises(audit.AuditError): audit.budget_totals(self.budget)

    def test_budget_missing_source(self):
        self.budget["catalog_items"][0].pop("source")
        with self.assertRaises(audit.AuditError): audit.budget_totals(self.budget)

    def test_hash_then_mutation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); path = root / "source.txt"; path.write_bytes(b"original\n")
            entry = dict(path="source.txt", sha256=hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertEqual(audit.verified_path(root, entry), path)
            path.write_bytes(b"changed\n")
            with self.assertRaises(audit.AuditError): audit.verified_path(root, entry)

    def test_missing_source(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(audit.AuditError):
                audit.verified_path(Path(temp), dict(path="missing",sha256="0"*64))

    def test_path_escape(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(audit.AuditError):
                audit.verified_path(Path(temp), dict(path="../outside",sha256="0"*64))

    def test_duplicate_json_key(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/"bad.json";path.write_text('{"a":1,"a":2}')
            with self.assertRaises(audit.AuditError): audit.read_json(path)

if __name__ == "__main__":
    unittest.main()
