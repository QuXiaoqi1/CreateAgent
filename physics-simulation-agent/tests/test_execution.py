import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from physics_sim_agent import (
    CommandResult,
    EnvironmentCapability,
    OpenFOAMAdapter,
    detect_environment,
    diagnose_failure,
    execute_openfoam_case,
    parse_check_mesh_log,
    parse_solver_log,
    run_command,
)
from test_schema import valid_cfd_schema


class ExecutionEngineTests(unittest.TestCase):
    def test_detects_local_openfoam_when_commands_exist(self):
        def fake_which(name):
            if name in {"blockMesh", "checkMesh", "simpleFoam"}:
                return f"/usr/local/bin/{name}"
            return None

        with mock.patch("physics_sim_agent.execution.shutil.which", side_effect=fake_which), mock.patch(
            "physics_sim_agent.execution._detect_openfoam_version", return_value="OpenFOAM mock"
        ):
            env = detect_environment()

        self.assertTrue(env.available)
        self.assertEqual(env.mode, "local")
        self.assertEqual(env.version, "OpenFOAM mock")

    def test_detects_docker_fallback(self):
        def fake_which(name):
            return "/usr/local/bin/docker" if name == "docker" else None

        with mock.patch("physics_sim_agent.execution.shutil.which", side_effect=fake_which):
            env = detect_environment()

        self.assertTrue(env.available)
        self.assertEqual(env.mode, "docker")
        self.assertIn("Docker fallback selected", env.limitations[0])

    def test_unavailable_environment_reports_limitations(self):
        with mock.patch("physics_sim_agent.execution.shutil.which", return_value=None):
            env = detect_environment()

        self.assertFalse(env.available)
        self.assertEqual(env.mode, "unavailable")
        self.assertGreaterEqual(len(env.limitations), 2)

    def test_run_command_captures_output_and_log(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "command.log"
            result = run_command(
                [sys.executable, "-c", "print('hello command')"],
                cwd=temp_dir,
                log_path=log_path,
            )

            self.assertTrue(result.ok)
            self.assertIn("hello command", result.stdout)
            self.assertIn("hello command", log_path.read_text(encoding="utf-8"))

    def test_parses_check_mesh_and_solver_logs(self):
        mesh = parse_check_mesh_log("Checking mesh...\nMesh OK.\nEnd")
        solver = parse_solver_log(
            "Solving for Ux, Initial residual = 0.01, Final residual = 1e-06\nExecutionTime = 1 s\nEnd"
        )

        self.assertTrue(mesh["passed"])
        self.assertTrue(solver["completed"])
        self.assertEqual(solver["residuals"][0]["field"], "Ux")

    def test_diagnoses_common_failures(self):
        diagnosis = diagnose_failure("FOAM FATAL ERROR: cannot find file 0/U")

        self.assertIn("missing", diagnosis.probable_cause.lower())

    def test_mock_execution_writes_stage_logs_and_summary(self):
        adapter = OpenFOAMAdapter()
        schema = valid_cfd_schema()

        with tempfile.TemporaryDirectory() as temp_dir:
            case_dir = adapter.generate_solver_input(schema, Path(temp_dir))
            summary = execute_openfoam_case(case_dir, mode="mock")
            summary_path = case_dir / "logs" / "execution-summary.json"
            loaded = json.loads(summary_path.read_text(encoding="utf-8"))

        self.assertEqual(summary.status, "completed")
        self.assertEqual(summary.mode, "mock")
        self.assertEqual(len(summary.stages), 4)
        self.assertEqual(loaded["status"], "completed")

    def test_docker_execution_runs_staged_container_commands(self):
        adapter = OpenFOAMAdapter()
        schema = valid_cfd_schema()
        commands = []

        def fake_run_command(command, cwd, log_path, timeout_seconds=600):
            commands.append(command)
            inner = command[-1]
            if "checkMesh" in inner:
                stdout = "Checking mesh...\nMesh OK.\nEnd\n"
            elif "simpleFoam" in inner:
                stdout = "Solving for Ux, Initial residual = 0.01, Final residual = 1e-06\nExecutionTime = 1 s\nEnd\n"
            else:
                stdout = "End\n"
            Path(log_path).parent.mkdir(parents=True, exist_ok=True)
            Path(log_path).write_text(stdout, encoding="utf-8")
            return CommandResult(command, str(cwd), 0, 0.0, stdout, "", str(log_path))

        with tempfile.TemporaryDirectory() as temp_dir:
            case_dir = adapter.generate_solver_input(schema, Path(temp_dir))
            env = EnvironmentCapability(mode="docker", available=True, docker_path="/usr/local/bin/docker")
            with mock.patch("physics_sim_agent.execution.detect_environment", return_value=env), mock.patch(
                "physics_sim_agent.execution.run_command", side_effect=fake_run_command
            ):
                summary = execute_openfoam_case(case_dir, mode="auto")

        self.assertEqual(summary.mode, "docker")
        self.assertEqual(summary.status, "completed")
        self.assertEqual(commands[0][0], "/usr/local/bin/docker")
        self.assertIn("run", commands[0])

    def test_adapter_parse_logs_uses_execution_parsers(self):
        adapter = OpenFOAMAdapter()

        with tempfile.TemporaryDirectory() as temp_dir:
            log = Path(temp_dir) / "checkMesh.log"
            log.write_text("Mesh OK.\nEnd\n", encoding="utf-8")
            parsed = adapter.parse_logs([log])

        self.assertTrue(parsed["checkMesh.log"]["passed"])


if __name__ == "__main__":
    unittest.main()
