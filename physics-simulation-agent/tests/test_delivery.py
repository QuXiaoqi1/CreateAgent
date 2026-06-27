import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from physics_sim_agent import (
    Diagnosis,
    EnvironmentCapability,
    ExecutionSummary,
    OpenFOAMAdapter,
    StageResult,
    build_delivery_package,
    build_validation_evidence,
    execute_openfoam_case,
    generate_report,
    select_report_languages,
)
from test_schema import valid_cfd_schema


class DeliveryTests(unittest.TestCase):
    def test_builds_success_delivery_package(self):
        adapter = OpenFOAMAdapter()
        schema = valid_cfd_schema()

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            case_dir = adapter.generate_solver_input(schema, root)
            execution = execute_openfoam_case(case_dir, mode="mock")
            package = build_delivery_package(schema, case_dir, execution, root / "delivery", user_text="模拟管道流动")

            required = [
                "README.md",
                "problem.schema.json",
                "assumptions.md",
                "solver-input/openfoam-case/run.sh",
                "logs/execution-summary.json",
                "results",
                "report.md",
                "metadata.json",
                "validation-evidence.json",
            ]
            for relative in required:
                self.assertTrue((package / relative).exists(), relative)

            report = (package / "report.md").read_text(encoding="utf-8")
            metadata = json.loads((package / "metadata.json").read_text(encoding="utf-8"))

        self.assertIn("物理模拟分析报告", report)
        self.assertIn("Physics Simulation Analysis Report", report)
        self.assertEqual(metadata["execution"]["status"], "completed")

    def test_validation_evidence_distinguishes_limited_confidence(self):
        schema = valid_cfd_schema()
        execution = ExecutionSummary(
            mode="unavailable",
            status="skipped",
            environment=EnvironmentCapability(mode="unavailable", available=False),
            stages=[
                StageResult(
                    name="environment",
                    status="skipped",
                    diagnosis=Diagnosis(
                        probable_cause="No OpenFOAM runtime.",
                        recommended_action="Install OpenFOAM or use Docker.",
                    ),
                )
            ],
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            evidence = build_validation_evidence(schema, Path(temp_dir), execution)
            report = generate_report(schema, evidence, execution)

        self.assertEqual(evidence.confidence, "limited")
        self.assertIn("Execution was skipped", evidence.warnings[0])
        self.assertIn("Runnable status", report)

    def test_language_selection_defaults_to_bilingual(self):
        self.assertEqual(select_report_languages("simulate pipe flow"), ["zh", "en"])
        self.assertEqual(select_report_languages("模拟管道流动"), ["zh", "en"])


if __name__ == "__main__":
    unittest.main()
