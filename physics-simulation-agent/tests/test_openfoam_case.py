import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from physics_sim_agent import OpenFOAMAdapter, build_schema_draft, table_text_artifact, text_artifact


class OpenFOAMCaseGenerationTests(unittest.TestCase):
    def test_generates_openfoam_case_for_four_golden_cases(self):
        adapter = OpenFOAMAdapter()
        fixture = Path(__file__).resolve().parents[1] / "fixtures" / "cfd_golden_cases.json"
        golden_cases = json.loads(fixture.read_text(encoding="utf-8"))

        for golden_case in golden_cases:
            expected_case = golden_case["caseFamily"]
            with self.subTest(case=expected_case):
                draft = build_schema_draft(
                    [
                        text_artifact(golden_case["prompt"]),
                        table_text_artifact(golden_case["table"]),
                    ]
                )
                self.assertEqual(draft.schema.validation.status, "valid")

                with tempfile.TemporaryDirectory() as temp_dir:
                    case_dir = adapter.generate_solver_input(draft.schema, Path(temp_dir))

                    self.assert_case_structure(case_dir)
                    manifest = json.loads((case_dir / "generation-manifest.json").read_text(encoding="utf-8"))

                self.assertEqual(manifest["caseFamily"], expected_case)
                self.assertEqual(manifest["domainPack"], "domain-pack-cfd-openfoam")
                self.assertEqual(manifest["adapter"], "OpenFOAMAdapter")
                self.assertEqual(manifest["solver"], "simpleFoam")
                self.assertIn("schemaHash", manifest)

    def test_invalid_schema_blocks_generation(self):
        adapter = OpenFOAMAdapter()
        draft = build_schema_draft([text_artifact("simulate airflow through a 2D straight pipe")])

        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(ValueError):
                adapter.generate_solver_input(draft.schema, Path(temp_dir))

    def assert_case_structure(self, case_dir):
        required = [
            "0/U",
            "0/p",
            "constant/transportProperties",
            "constant/turbulenceProperties",
            "system/blockMeshDict",
            "system/controlDict",
            "system/fvSchemes",
            "system/fvSolution",
            "run.sh",
            "generation-manifest.json",
            "problem.schema.json",
        ]
        for relative in required:
            self.assertTrue((case_dir / relative).exists(), relative)
        self.assertTrue(os.access(case_dir / "run.sh", os.X_OK))
        self.assertIn("blockMesh", (case_dir / "run.sh").read_text(encoding="utf-8"))
        self.assertIn("application simpleFoam", (case_dir / "system/controlDict").read_text(encoding="utf-8"))
        self.assertIn("nu [0 2 -1 0 0 0 0]", (case_dir / "constant/transportProperties").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
