import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from physics_sim_agent import (
    build_schema_draft,
    classify_physics_domain,
    screenshot_text_artifact,
    table_file_artifact,
    table_text_artifact,
    text_artifact,
)


CFD_TABLE = """parameter,value,unit
length,2,m
diameter,100,mm
inlet_velocity,5,m/s
outlet_pressure,0,Pa
density,1.225,kg/m^3
dynamic_viscosity,1.8e-5,Pa*s
"""


class IntakeTests(unittest.TestCase):
    def test_classifies_major_physics_domains(self):
        fixture = Path(__file__).resolve().parents[1] / "fixtures" / "domain_examples.json"
        examples = json.loads(fixture.read_text(encoding="utf-8"))

        for example in examples:
            with self.subTest(text=example["text"]):
                self.assertEqual(
                    classify_physics_domain(example["text"]).domain,
                    example["domain"],
                )

    def test_table_text_parsing_and_unit_normalization(self):
        draft = build_schema_draft(
            [
                text_artifact("simulate airflow through a 2D straight pipe pressure drop"),
                table_text_artifact(CFD_TABLE),
            ]
        )

        schema = draft.schema
        self.assertEqual(schema.physics_domain, "cfd")
        self.assertEqual(schema.validation.status, "valid")
        self.assertEqual(schema.domain_extensions["cfdOpenfoam"].case_family, "straight_pipe")
        self.assertEqual(schema.geometry["dimensions"]["diameter"]["value"], 0.1)
        self.assertEqual(schema.geometry["dimensions"]["diameter"]["unit"], "m")
        self.assertEqual(draft.clarifications, [])

    def test_missing_cfd_dimensions_generate_targeted_questions(self):
        draft = build_schema_draft(
            [
                text_artifact("simulate airflow through a 2D straight pipe"),
                table_text_artifact(
                    """parameter,value,unit
inlet_velocity,5,m/s
density,1.225,kg/m^3
dynamic_viscosity,1.8e-5,Pa*s
"""
                ),
            ]
        )

        self.assertEqual(draft.schema.validation.status, "blocked")
        questions = {question.field for question in draft.clarifications}
        self.assertIn("geometry.dimensions.length", questions)
        self.assertIn("geometry.dimensions.diameter", questions)

    def test_non_mvp_heat_transfer_is_draft_only(self):
        draft = build_schema_draft(
            [
                text_artifact("solve steady heat conduction temperature in a 2d plate"),
                table_text_artifact(
                    """parameter,value,unit
length,1,m
thermal_conductivity,205,W/(m*K)
"""
                ),
            ]
        )

        self.assertEqual(draft.classification.domain, "heat-transfer")
        self.assertEqual(draft.schema.validation.status, "draft_only")
        self.assertFalse(draft.schema.validation.can_generate_solver_input)
        self.assertTrue(any(question.severity == "draft_only" for question in draft.clarifications))

    def test_screenshot_values_require_confirmation(self):
        draft = build_schema_draft(
            [
                text_artifact("simulate airflow through a 2D straight pipe pressure drop"),
                screenshot_text_artifact(
                    "length 2 m diameter 0.1 m inlet_velocity 5 m/s outlet_pressure 0 Pa density 1.225 kg/m^3 dynamic_viscosity 1.8e-5 Pa*s",
                    confidence=0.55,
                    confirmed=False,
                ),
            ]
        )

        codes = {issue.code for issue in draft.schema.validation.issues}
        self.assertIn("unconfirmed_screenshot_value", codes)
        self.assertIn("low_confidence_screenshot_value", codes)

    def test_csv_file_artifact(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "params.csv"
            path.write_text(CFD_TABLE, encoding="utf-8")

            draft = build_schema_draft(
                [
                    text_artifact("simulate airflow through a 2D straight pipe"),
                    table_file_artifact(path),
                ]
            )

        self.assertEqual(draft.schema.validation.status, "valid")

    def test_xlsx_file_artifact(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "params.xlsx"
            _write_minimal_xlsx(path)

            draft = build_schema_draft(
                [
                    text_artifact("simulate airflow through a 2D straight pipe"),
                    table_file_artifact(path),
                ]
            )

        self.assertEqual(draft.schema.validation.status, "valid")

    def test_pipe_delimited_table_text(self):
        draft = build_schema_draft(
            [
                text_artifact("simulate airflow through a 2D straight pipe"),
                table_text_artifact(
                    """parameter|value|unit
length|2|m
diameter|0.1|m
inlet_velocity|5|m/s
outlet_pressure|0|Pa
density|1.225|kg/m^3
dynamic_viscosity|1.8e-5|Pa*s
"""
                ),
            ]
        )

        self.assertEqual(draft.schema.validation.status, "valid")


if __name__ == "__main__":
    unittest.main()


def _write_minimal_xlsx(path):
    values = [
        "parameter",
        "value",
        "unit",
        "length",
        "2",
        "m",
        "diameter",
        "100",
        "mm",
        "inlet_velocity",
        "5",
        "m/s",
        "outlet_pressure",
        "0",
        "Pa",
        "density",
        "1.225",
        "kg/m^3",
        "dynamic_viscosity",
        "1.8e-5",
        "Pa*s",
    ]
    shared = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        + "".join(f"<si><t>{value}</t></si>" for value in values)
        + "</sst>"
    )
    rows = []
    index = 0
    for row_number in range(1, 8):
        cells = []
        for column in ("A", "B", "C"):
            cells.append(f'<c r="{column}{row_number}" t="s"><v>{index}</v></c>')
            index += 1
        rows.append(f'<row r="{row_number}">{"".join(cells)}</row>')
    sheet = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(rows)}</sheetData></worksheet>'
    )
    with zipfile.ZipFile(path, "w") as workbook:
        workbook.writestr("xl/sharedStrings.xml", shared)
        workbook.writestr("xl/worksheets/sheet1.xml", sheet)
