import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXTENSION = ROOT / "gh-physics-sim" / "gh-physics-sim"
CORE = ROOT / "physics-simulation-agent"


class GhPhysicsSimCliTests(unittest.TestCase):
    def test_local_core_workflow(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cwd = Path(temp_dir)
            workspace = cwd / ".physics-sim"
            table = cwd / "params.csv"
            table.write_text(
                "parameter,value,unit\n"
                "length,2,m\n"
                "diameter,0.1,m\n"
                "inlet_velocity,5,m/s\n"
                "outlet_pressure,0,Pa\n"
                "density,1.225,kg/m^3\n"
                "dynamic_viscosity,1.8e-5,Pa*s\n",
                encoding="utf-8",
            )

            self.run_cli(cwd, "init", "--workspace", str(workspace))
            self.run_cli(
                cwd,
                "new",
                "simulate airflow through a 2D straight pipe pressure drop",
                "--case-name",
                "pipe-demo",
                "--workspace",
                str(workspace),
            )
            self.run_cli(cwd, "add-table", str(table), "--workspace", str(workspace))
            self.run_cli(cwd, "draft", "--workspace", str(workspace))
            self.run_cli(cwd, "validate", "--workspace", str(workspace))
            self.run_cli(cwd, "generate", "--workspace", str(workspace))
            self.run_cli(cwd, "run", "--workspace", str(workspace))
            self.run_cli(cwd, "report", "--workspace", str(workspace))
            self.run_cli(cwd, "package", "--workspace", str(workspace))

            task = json.loads((workspace / "tasks" / "pipe-demo" / "task.json").read_text(encoding="utf-8"))
            package_report_exists = (workspace / "package" / "report.md").exists()
            run_script_exists = (workspace / "solver-input" / "openfoam-case" / "run.sh").exists()

        self.assertEqual(task["stage"], "package_ready")
        self.assertTrue(package_report_exists)
        self.assertTrue(run_script_exists)

    def run_cli(self, cwd, *args):
        env = os.environ.copy()
        env["PHYSICS_SIM_AGENT_ROOT"] = str(CORE)
        completed = subprocess.run(
            [str(EXTENSION), *args],
            cwd=str(cwd),
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            self.fail(
                "command failed: "
                + " ".join(args)
                + f"\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
            )
        return completed


if __name__ == "__main__":
    unittest.main()
