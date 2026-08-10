from __future__ import annotations

import sys
import unittest
from dataclasses import replace
from pathlib import Path


SUPERVISOR_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SUPERVISOR_ROOT))

from project_button_supervisor import (  # noqa: E402
    FaultCode,
    HardwareSnapshot,
    JointRule,
    MotionMode,
    OperatingState,
    Supervisor,
    SupervisorConfig,
    TrajectoryCommand,
    TrajectorySample,
)


JOINTS = {
    "J1": JointRule(-20.0, 70.0, "deg", 1.0),
    "J2": JointRule(15.0, 115.0, "deg", 1.0),
    "GRIPPER": JointRule(20.0, 75.0, "mm", 1.0),
}
START = {"J1": 0.0, "J2": 30.0, "GRIPPER": 40.0}
END = {"J1": 5.0, "J2": 35.0, "GRIPPER": 42.0}


def config() -> SupervisorConfig:
    return SupervisorConfig(
        configuration_id="HR-V0-SUP-P0.3",
        configuration_hash="A" * 64,
        maximum_command_age_ms=100,
        maximum_tcp_speed_m_s=0.15,
        automatic_joint_speed_deg_s=30.0,
        setup_joint_speed_deg_s=10.0,
        automatic_gripper_speed_mm_s=20.0,
        setup_gripper_speed_mm_s=10.0,
        joints=JOINTS,
        kinematic_model_hash="B" * 64,
        mechanical_limit_binding={
            "limit_set_id": "HR-V0-LIMITS-P0.2",
            "mechanical_revision": "HR-V0-MECH-P0.6",
            "arm_architecture_revision": "HR-V0-ARM-ARCH-P0.7",
            "hard_stop_revision": "HR-V0-HS-P0.3",
            "release_state": "ACCEPTED-FOR-GUARDED-HIL",
            "acceptance_evidence_hash": "C" * 64,
        },
    )


def snapshot(**changes: object) -> HardwareSnapshot:
    values: dict[str, object] = {
        "control_power": True,
        "estop_healthy": True,
        "watchdog_healthy": True,
        "edm_healthy": True,
        "bus_healthy": True,
        "compute_undervoltage": False,
        "sr1_ready": False,
        "sra1_armed": False,
        "k1_feedback": False,
        "k2_feedback": False,
        "positions": START,
    }
    values.update(changes)
    return HardwareSnapshot(**values)  # type: ignore[arg-type]


def command(sequence: int = 1, now_ms: int = 1000, mode: MotionMode = MotionMode.AUTOMATIC) -> TrajectoryCommand:
    samples = (
        TrajectorySample(0, START, {"J1": 0.0, "J2": 0.0, "GRIPPER": 0.0}),
        TrajectorySample(200, END, {"J1": 25.0, "J2": 25.0, "GRIPPER": 10.0}),
    )
    return TrajectoryCommand(
        trajectory_id=f"trajectory-{sequence}",
        session_id="SESSION-TEST",
        sequence=sequence,
        source_time_ms=now_ms,
        validity_deadline_ms=now_ms + 100,
        execution_deadline_ms=now_ms + 250,
        configuration_hash="A" * 64,
        kinematic_model_hash="B" * 64,
        sender_state=OperatingState.ARMED.value,
        mode=mode,
        starting_positions=START,
        samples=samples,
        expected_terminal_positions=END,
    )


def armed_supervisor() -> Supervisor:
    supervisor = Supervisor(config(), lambda samples: [0.0, 0.10], session_id="SESSION-TEST")
    supervisor.observe_hardware(snapshot(sr1_ready=False), 900)
    supervisor.observe_hardware(snapshot(sr1_ready=True), 910)
    supervisor.observe_hardware(
        snapshot(sr1_ready=True, sra1_armed=True, k1_feedback=True, k2_feedback=True), 920
    )
    return supervisor


class SupervisorTests(unittest.TestCase):
    def test_reset_and_arm_never_create_motion(self) -> None:
        supervisor = Supervisor(config(), lambda samples: [0.0 for _ in samples], session_id="SESSION-TEST")
        supervisor.observe_hardware(snapshot(sr1_ready=False), 0)
        self.assertEqual(supervisor.state, OperatingState.RESET_REQUIRED)
        self.assertFalse(supervisor.outputs.torque_enable_request)

        supervisor.observe_hardware(snapshot(sr1_ready=True), 10)
        self.assertEqual(supervisor.state, OperatingState.SAFE_READY)
        self.assertFalse(supervisor.outputs.torque_enable_request)

        supervisor.observe_hardware(
            snapshot(sr1_ready=True, sra1_armed=True, k1_feedback=True, k2_feedback=True), 20
        )
        self.assertEqual(supervisor.state, OperatingState.ARMED)
        self.assertFalse(supervisor.outputs.torque_enable_request)

    def test_only_fresh_valid_trajectory_requests_torque(self) -> None:
        supervisor = armed_supervisor()
        self.assertTrue(supervisor.accept_trajectory(command(), 1000))
        self.assertEqual(supervisor.state, OperatingState.DRIVE_ENABLED)
        self.assertTrue(supervisor.outputs.torque_enable_request)
        self.assertTrue(supervisor.complete_trajectory(1200, True, END))
        self.assertEqual(supervisor.state, OperatingState.ARMED)
        self.assertFalse(supervisor.outputs.torque_enable_request)

    def test_fault_invalidates_target_and_hardware_restore_cannot_resume(self) -> None:
        supervisor = armed_supervisor()
        self.assertTrue(supervisor.accept_trajectory(command(), 1000))
        supervisor.observe_hardware(snapshot(estop_healthy=False), 1010)
        self.assertEqual(supervisor.fault, FaultCode.ESTOP_OPEN)
        self.assertEqual(supervisor.state, OperatingState.FAULT_LATCHED)
        self.assertIsNone(supervisor.active_command)
        self.assertFalse(supervisor.outputs.heartbeat_allowed)
        self.assertFalse(supervisor.outputs.torque_enable_request)

        supervisor.observe_hardware(snapshot(sr1_ready=True), 1020)
        supervisor.observe_hardware(
            snapshot(sr1_ready=True, sra1_armed=True, k1_feedback=True, k2_feedback=True), 1030
        )
        self.assertEqual(supervisor.state, OperatingState.FAULT_LATCHED)
        self.assertFalse(supervisor.outputs.torque_enable_request)

        supervisor.observe_hardware(snapshot(sr1_ready=False), 1040)
        self.assertTrue(supervisor.acknowledge_fault(1050, operator_acknowledged=True))
        self.assertEqual(supervisor.state, OperatingState.RESET_REQUIRED)
        self.assertFalse(supervisor.outputs.torque_enable_request)

    def test_dropout_rearm_rejects_stale_replay_and_requires_new_sequence(self) -> None:
        supervisor = armed_supervisor()
        stale = command(sequence=1, now_ms=1000)
        self.assertTrue(supervisor.accept_trajectory(stale, 1000))

        supervisor.observe_hardware(snapshot(estop_healthy=False), 1010)
        self.assertIsNone(supervisor.active_command)
        self.assertFalse(supervisor.outputs.torque_enable_request)

        supervisor.observe_hardware(snapshot(sr1_ready=False), 1020)
        self.assertTrue(supervisor.acknowledge_fault(1030, operator_acknowledged=True))
        supervisor.observe_hardware(snapshot(sr1_ready=False), 1040)
        supervisor.observe_hardware(snapshot(sr1_ready=True), 1050)
        supervisor.observe_hardware(
            snapshot(sr1_ready=True, sra1_armed=True, k1_feedback=True, k2_feedback=True), 1060
        )

        self.assertEqual(supervisor.state, OperatingState.ARMED)
        self.assertIsNone(supervisor.active_command)
        self.assertFalse(supervisor.outputs.torque_enable_request)
        replay = replace(
            stale,
            source_time_ms=1070,
            validity_deadline_ms=1170,
            execution_deadline_ms=1320,
        )
        self.assertFalse(supervisor.accept_trajectory(replay, 1070))
        self.assertIn("duplicate or out-of-order sequence", supervisor.events[-1].detail)
        self.assertFalse(supervisor.outputs.torque_enable_request)

        fresh = command(sequence=2, now_ms=1080)
        self.assertTrue(supervisor.accept_trajectory(fresh, 1080))
        self.assertTrue(supervisor.outputs.torque_enable_request)

    def test_arm_without_observed_safe_ready_latches_fault(self) -> None:
        supervisor = Supervisor(config(), lambda samples: [0.0 for _ in samples], session_id="SESSION-TEST")
        supervisor.observe_hardware(
            snapshot(sr1_ready=True, sra1_armed=True, k1_feedback=True, k2_feedback=True), 0
        )
        self.assertEqual(supervisor.fault, FaultCode.UNEXPECTED_ARM_ORDER)
        self.assertFalse(supervisor.outputs.torque_enable_request)

    def test_invalid_commands_are_rejected_and_recorded(self) -> None:
        cases = (
            replace(command(), configuration_hash="wrong"),
            replace(command(), session_id="wrong-session"),
            replace(command(), kinematic_model_hash="wrong"),
            replace(command(), source_time_ms=1100),
            replace(command(), validity_deadline_ms=1200),
            replace(command(), sender_state=OperatingState.SAFE_READY.value),
            replace(command(), starting_positions={**START, "J1": 10.0}),
            replace(command(), samples=(command().samples[0], replace(command().samples[1], positions={**END, "J1": 80.0}))),
            replace(command(), samples=(command().samples[0], replace(command().samples[1], velocities={**command().samples[1].velocities, "J1": 31.0}))),
        )
        for bad in cases:
            with self.subTest(bad=bad):
                supervisor = armed_supervisor()
                self.assertFalse(supervisor.accept_trajectory(bad, 1000))
                self.assertEqual(supervisor.state, OperatingState.ARMED)
                self.assertFalse(supervisor.outputs.torque_enable_request)
                self.assertEqual(supervisor.events[-1].event, "COMMAND_REJECTED")

    def test_tcp_limit_and_sequence_replay_are_rejected(self) -> None:
        supervisor = Supervisor(config(), lambda samples: [0.0, 0.151], session_id="SESSION-TEST")
        supervisor.observe_hardware(snapshot(sr1_ready=False), 900)
        supervisor.observe_hardware(snapshot(sr1_ready=True), 910)
        supervisor.observe_hardware(
            snapshot(sr1_ready=True, sra1_armed=True, k1_feedback=True, k2_feedback=True), 920
        )
        self.assertFalse(supervisor.accept_trajectory(command(), 1000))

        supervisor = armed_supervisor()
        self.assertTrue(supervisor.accept_trajectory(command(), 1000))
        self.assertTrue(supervisor.complete_trajectory(1200, True, END))
        supervisor.observe_hardware(
            snapshot(sr1_ready=True, sra1_armed=True, k1_feedback=True, k2_feedback=True, positions=START), 1300
        )
        self.assertFalse(supervisor.accept_trajectory(command(), 1300))

    def test_execution_deadline_latches_and_clears_target(self) -> None:
        supervisor = armed_supervisor()
        self.assertTrue(supervisor.accept_trajectory(command(), 1000))
        supervisor.tick(1251)
        self.assertEqual(supervisor.fault, FaultCode.COMMAND_EXPIRED)
        self.assertIsNone(supervisor.active_command)
        self.assertFalse(supervisor.outputs.torque_enable_request)

    def test_repository_config_fails_closed_while_hashes_are_unselected(self) -> None:
        repository_config = SupervisorConfig.from_json(SUPERVISOR_ROOT / "supervisor-config.json")
        supervisor = Supervisor(repository_config, lambda samples: [0.0 for _ in samples], session_id="SESSION-TEST")
        supervisor.observe_hardware(snapshot(sr1_ready=False), 900)
        supervisor.observe_hardware(snapshot(sr1_ready=True), 910)
        supervisor.observe_hardware(
            snapshot(sr1_ready=True, sra1_armed=True, k1_feedback=True, k2_feedback=True), 920
        )
        candidate = replace(
            command(),
            configuration_hash=repository_config.configuration_hash,
            kinematic_model_hash=repository_config.kinematic_model_hash,
        )
        self.assertFalse(supervisor.accept_trajectory(candidate, 1000))
        self.assertFalse(supervisor.outputs.torque_enable_request)

    def test_current_j2_ceiling_is_accepted_and_above_ceiling_is_rejected(self) -> None:
        at_limit = replace(
            command(),
            samples=(
                command().samples[0],
                replace(command().samples[1], positions={**END, "J2": 115.0}),
            ),
            expected_terminal_positions={**END, "J2": 115.0},
        )
        supervisor = armed_supervisor()
        self.assertTrue(supervisor.accept_trajectory(at_limit, 1000))

        above_limit = replace(
            at_limit,
            trajectory_id="trajectory-above-limit",
            samples=(
                at_limit.samples[0],
                replace(at_limit.samples[1], positions={**END, "J2": 115.001}),
            ),
            expected_terminal_positions={**END, "J2": 115.001},
        )
        supervisor = armed_supervisor()
        self.assertFalse(supervisor.accept_trajectory(above_limit, 1000))
        self.assertFalse(supervisor.outputs.torque_enable_request)

    def test_stale_120_degree_limit_or_revision_mismatch_fails_closed(self) -> None:
        stale_joints = {**JOINTS, "J2": JointRule(15.0, 120.0, "deg", 1.0)}
        self.assertFalse(replace(config(), joints=stale_joints).selections_closed)
        stale_binding = {
            **config().mechanical_limit_binding,
            "arm_architecture_revision": "HR-V0-ARM-ARCH-P0.5",
        }
        self.assertFalse(replace(config(), mechanical_limit_binding=stale_binding).selections_closed)

    def test_unaccepted_mechanical_limit_evidence_fails_closed(self) -> None:
        unreleased = {
            **config().mechanical_limit_binding,
            "release_state": "CANDIDATE-NOT-RELEASED",
            "acceptance_evidence_hash": "SELECTION REQUIRED",
        }
        self.assertFalse(replace(config(), mechanical_limit_binding=unreleased).selections_closed)
        malformed_hash = {
            **config().mechanical_limit_binding,
            "acceptance_evidence_hash": "NOT-A-SHA256",
        }
        self.assertFalse(replace(config(), mechanical_limit_binding=malformed_hash).selections_closed)
        self.assertFalse(replace(config(), configuration_id="HR-V0-SUP-P0.1").selections_closed)

    def test_watchdog_startup_grace_allows_heartbeat_to_begin_fail_closed(self) -> None:
        supervisor = Supervisor(config(), lambda samples: [0.0 for _ in samples], session_id="SESSION-TEST")
        supervisor.observe_hardware(snapshot(watchdog_healthy=False), 0)
        self.assertEqual(supervisor.state, OperatingState.SAFE_DISABLED)
        self.assertIsNone(supervisor.fault)
        self.assertTrue(supervisor.outputs.heartbeat_allowed)
        supervisor.observe_hardware(snapshot(watchdog_healthy=True, sr1_ready=False), 300)
        self.assertEqual(supervisor.state, OperatingState.RESET_REQUIRED)

    def test_watchdog_or_hardware_permit_dropout_after_arm_latches(self) -> None:
        supervisor = armed_supervisor()
        supervisor.observe_hardware(
            snapshot(watchdog_healthy=False, sr1_ready=False, sra1_armed=False, k1_feedback=False, k2_feedback=False), 1000
        )
        self.assertEqual(supervisor.fault, FaultCode.WATCHDOG_UNHEALTHY)
        self.assertFalse(supervisor.outputs.torque_enable_request)

        supervisor = armed_supervisor()
        supervisor.observe_hardware(snapshot(sr1_ready=False), 1000)
        self.assertEqual(supervisor.fault, FaultCode.HARDWARE_PERMIT_DROPPED)
        self.assertFalse(supervisor.outputs.torque_enable_request)


if __name__ == "__main__":
    unittest.main()
