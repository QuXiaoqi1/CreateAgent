import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from physics_sim_agent import DEFAULT_WORKFLOW, WORKSPACE_DIRS, PlatformWorkspace


class PlatformWorkspaceTests(unittest.TestCase):
    def test_initializes_workspace_layout(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = PlatformWorkspace(Path(temp_dir) / ".physics-sim")
            root = workspace.initialize()

            for directory in WORKSPACE_DIRS:
                self.assertTrue((root / directory).is_dir(), directory)
            metadata = json.loads((root / "state" / "workspace.json").read_text(encoding="utf-8"))

        self.assertIn("schema", metadata["directories"])

    def test_creates_and_loads_task_state(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = PlatformWorkspace(Path(temp_dir) / ".physics-sim")
            created = workspace.create_task("pipe-demo", "simulate pipe flow", language="en")
            loaded = workspace.load_task()

        self.assertEqual(created.id, "pipe-demo")
        self.assertEqual(loaded.title, "simulate pipe flow")
        self.assertEqual(loaded.stage, "created")

    def test_attaches_input_without_mutating_original(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "params.csv"
            source.write_text("parameter,value,unit\nlength,2,m\n", encoding="utf-8")
            workspace = PlatformWorkspace(root / ".physics-sim")
            workspace.create_task("pipe-demo", "simulate pipe flow")

            artifact = workspace.attach_input(source, kind="table")
            loaded = workspace.load_task("pipe-demo")

            self.assertEqual(source.read_text(encoding="utf-8"), "parameter,value,unit\nlength,2,m\n")
            self.assertEqual(artifact.path, "inputs/params.csv")
            self.assertEqual(loaded.artifacts[0].kind, "table")
            self.assertTrue((workspace.root / artifact.path).exists())

    def test_persists_checkpoint_decisions(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = PlatformWorkspace(Path(temp_dir) / ".physics-sim")
            workspace.create_task("pipe-demo", "simulate pipe flow")
            checkpoint = workspace.add_checkpoint(
                kind="assumption_approval",
                question="Approve incompressible isothermal flow?",
                field="assumptions.isothermal_flow",
                risk="Invalid if density changes.",
            )
            resolved = workspace.resolve_checkpoint(checkpoint.id, answer=True)
            loaded = workspace.load_task()

        self.assertEqual(resolved.status, "approved")
        self.assertTrue(loaded.checkpoints[0].answer)
        self.assertTrue(loaded.checkpoints[0].resolved_at)

    def test_rejects_unknown_workflow_stage(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = PlatformWorkspace(Path(temp_dir) / ".physics-sim")
            workspace.create_task("pipe-demo", "simulate pipe flow")

            with self.assertRaises(ValueError):
                workspace.set_stage("teleport")

        self.assertEqual(DEFAULT_WORKFLOW[0].name, "intake")


if __name__ == "__main__":
    unittest.main()
