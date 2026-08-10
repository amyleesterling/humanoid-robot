from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock


PACKAGE = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class HostDeployTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import sys
        sys.path.insert(0, str(PACKAGE))
        from project_button_host import launcher, preflight
        cls.launcher = launcher
        cls.preflight = preflight

    def test_committed_configuration_fails_closed(self):
        result = self.preflight.evaluate(PACKAGE / "host-deploy-config.json")
        self.assertFalse(result.ready)
        self.assertGreaterEqual(len(result.holds), 15)
        self.assertTrue(any("runtime_backend unresolved" in hold for hold in result.holds))

    def test_launcher_does_not_spawn_for_committed_configuration(self):
        with mock.patch.object(self.launcher.subprocess, "run") as run:
            code = self.launcher.launch(PACKAGE / "host-deploy-config.json")
        self.assertEqual(code, 78)
        run.assert_not_called()

    def test_malformed_json_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text("{", encoding="utf-8")
            result = self.preflight.evaluate(path)
        self.assertFalse(result.ready)
        self.assertTrue(any("unreadable JSON" in hold for hold in result.holds))

    def test_missing_bound_files_fail_closed(self):
        config = json.loads((PACKAGE / "host-deploy-config.json").read_text(encoding="utf-8"))
        config.update({
            "release_state": "RELEASED_FOR_ISOLATED_HOST_HIL",
            "authorized_stage": "ISOLATED_HOST_HIL_AUTHORIZED",
            "service_identity": "project-button",
            "service_group": "project-button",
            "python_interpreter": "/usr/bin/python3",
            "runtime_entrypoint": "/opt/project-button/runtime.py",
            "runtime_backend": "candidate-backend",
            "serial_device": "/dev/serial/by-id/candidate",
            "gpio_backend": "candidate-gpio",
        })
        for key in [key for key in config if key.endswith("_sha256")]:
            config[key] = "0" * 64
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps(config), encoding="utf-8")
            result = self.preflight.evaluate(path, Path(directory))
        self.assertFalse(result.ready)
        self.assertTrue(any("target absent" in hold for hold in result.holds))

    def test_sources_have_no_hardware_backend_import(self):
        source = "\n".join((PACKAGE / "project_button_host" / name).read_text(encoding="utf-8") for name in ("preflight.py", "launcher.py"))
        for forbidden in ("import gpiod", "import gpiozero", "import serial", "import dynamixel_sdk"):
            self.assertNotIn(forbidden, source)

    def test_preset_is_disabled_and_restart_is_off(self):
        preset = (PACKAGE / "systemd/00-project-button.preset").read_text(encoding="utf-8")
        unit = (PACKAGE / "systemd/project-button-supervisor.service").read_text(encoding="utf-8")
        self.assertEqual(preset.strip(), "disable project-button-supervisor.service")
        self.assertIn("Restart=no", unit)
        self.assertIn("ExecStart=/usr/bin/python3 /opt/project-button/lib/project_button_host/launcher.py", unit)


if __name__ == "__main__":
    unittest.main()
