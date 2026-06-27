import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from physics_sim_agent import (
    EnvironmentCapability,
    check_fixture_structure,
    check_non_mvp_draft_only,
    run_conditional_real_smoke,
    run_mock_full_workflow,
    run_release_readiness,
)


PROJECT = Path(__file__).resolve().parents[1]


class ReadinessTests(unittest.TestCase):
    def test_fixture_and_non_mvp_checks_pass(self):
        fixture = check_fixture_structure(PROJECT)
        draft_only = check_non_mvp_draft_only(PROJECT)

        self.assertEqual(fixture.status, "pass")
        self.assertEqual(draft_only.status, "pass")
        self.assertIn("solid_mechanics_draft.schema.json: draft_only", draft_only.evidence)

    def test_mock_full_workflow_builds_delivery_package(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_mock_full_workflow(PROJECT, Path(temp_dir) / "workflow")

            self.assertEqual(result.item.status, "pass")
            self.assertEqual(result.execution.status, "completed")
            self.assertTrue((result.package_dir / "report.md").exists())
            self.assertTrue((result.package_dir / "solver-input" / "openfoam-case" / "run.sh").exists())

    def test_conditional_real_smoke_skips_when_runtime_missing(self):
        env = EnvironmentCapability(
            mode="unavailable",
            available=False,
            limitations=["Local OpenFOAM commands were not found.", "Docker was not found."],
        )
        with tempfile.TemporaryDirectory() as temp_dir, mock.patch(
            "physics_sim_agent.readiness.detect_environment", return_value=env
        ):
            item = run_conditional_real_smoke(PROJECT, Path(temp_dir) / "smoke")

        self.assertEqual(item.status, "skip")
        self.assertIn("skipped", item.message)

    def test_release_readiness_saves_report(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            report = run_release_readiness(PROJECT, temp_dir, run_real_smoke=False)
            json_path = Path(temp_dir) / "release-readiness.json"
            markdown_path = Path(temp_dir) / "release-readiness.md"
            saved = json.loads(json_path.read_text(encoding="utf-8"))
            markdown_exists = markdown_path.exists()

        self.assertEqual(report.overall_status, "ready_with_limitations")
        self.assertTrue(markdown_exists)
        self.assertEqual(saved["overallStatus"], "ready_with_limitations")
        self.assertIn("mock_full_workflow", {item["name"] for item in saved["items"]})


if __name__ == "__main__":
    unittest.main()
