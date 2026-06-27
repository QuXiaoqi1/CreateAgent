import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from physics_sim_agent import (
    Assumption,
    CFDExtension,
    PhysicsProblemSchema,
    Provenance,
    Quantity,
    validate_schema,
)


def q(value, unit="m", source="user", confirmed=True, confidence=None):
    return Quantity(
        value=value,
        unit=unit,
        provenance=[
            Provenance(
                source=source,
                source_ref="test-fixture",
                confidence=confidence,
                confirmed=confirmed,
            )
        ],
    ).to_dict()


def valid_cfd_schema():
    schema = PhysicsProblemSchema(
        simulation_objective={
            "description": "Estimate pressure drop through a 2D straight pipe.",
            "targets": ["pressure_drop", "velocity_profile"],
        },
        physics_domain="cfd",
        governing_model={
            "flow": "single_phase_incompressible",
            "time": "steady",
        },
        geometry={
            "kind": "2d_straight_pipe",
            "dimensions": {
                "length": q(2.0, "m"),
                "diameter": q(0.1, "m"),
            },
        },
        materials=[
            {
                "name": "air",
                "role": "fluid",
                "properties": {
                    "density": q(1.225, "kg/m^3"),
                    "dynamic_viscosity": q(1.8e-5, "Pa*s"),
                },
            }
        ],
        boundary_conditions=[
            {"name": "inlet", "type": "inlet", "values": {"velocity": q(5.0, "m/s")}},
            {"name": "outlet", "type": "outlet", "values": {"pressure": q(0.0, "Pa")}},
            {"name": "walls", "type": "wall", "values": {"velocity": q(0.0, "m/s")}},
        ],
        mesh_strategy={"method": "blockMesh", "dimension": "2d"},
        time_strategy={"mode": "steady"},
        solver_strategy={"family": "openfoam", "candidate": "simpleFoam"},
        postprocessing_targets=[{"name": "pressure_drop"}],
        assumptions=[
            Assumption(
                key="isothermal_flow",
                value=True,
                rationale="The MVP straight-pipe case ignores heat transfer.",
                risk="Invalid if temperature changes materially affect density.",
                approved=True,
            )
        ],
        provenance=[Provenance(source="user", source_ref="prompt")],
    )
    schema.attach_cfd_extension(CFDExtension(case_family="straight_pipe"))
    return schema


class PhysicsProblemSchemaTests(unittest.TestCase):
    def test_fixture_files_load_and_validate(self):
        fixture_dir = Path(__file__).resolve().parents[1] / "fixtures"

        cfd = PhysicsProblemSchema.load(fixture_dir / "straight_pipe.schema.json")
        heat = PhysicsProblemSchema.load(fixture_dir / "heat_transfer_draft.schema.json")
        solid = PhysicsProblemSchema.load(fixture_dir / "solid_mechanics_draft.schema.json")

        self.assertEqual(validate_schema(cfd).status, "valid")
        self.assertEqual(validate_schema(heat).status, "draft_only")
        self.assertEqual(validate_schema(solid).status, "draft_only")

    def test_valid_cfd_schema_can_generate_solver_input(self):
        schema = valid_cfd_schema()

        result = validate_schema(schema)

        self.assertEqual(result.status, "valid")
        self.assertTrue(result.can_generate_solver_input)
        self.assertEqual(result.blockers, [])
        self.assertIn("cfdOpenfoam", schema.to_dict()["domainExtensions"])

    def test_schema_serializes_to_problem_schema_json(self):
        schema = valid_cfd_schema()
        validate_schema(schema)

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "problem.schema.json"
            schema.save(path)
            loaded = PhysicsProblemSchema.load(path)

        self.assertEqual(loaded.physics_domain, "cfd")
        self.assertEqual(loaded.validation.status, "valid")
        self.assertIsInstance(loaded.domain_extensions["cfdOpenfoam"], CFDExtension)

    def test_missing_unit_blocks_solver_generation(self):
        schema = valid_cfd_schema()
        schema.geometry["dimensions"]["length"]["unit"] = None

        result = validate_schema(schema)

        self.assertEqual(result.status, "blocked")
        self.assertFalse(result.can_generate_solver_input)
        self.assertIn("missing_unit", {issue.code for issue in result.issues})

    def test_unapproved_assumption_blocks_solver_generation(self):
        schema = valid_cfd_schema()
        schema.assumptions[0].approved = False

        result = validate_schema(schema)

        self.assertEqual(result.status, "blocked")
        self.assertIn("unapproved_assumption", {issue.code for issue in result.issues})

    def test_low_confidence_screenshot_value_blocks_solver_generation(self):
        schema = valid_cfd_schema()
        schema.geometry["dimensions"]["diameter"] = q(
            0.1,
            "m",
            source="screenshot",
            confirmed=False,
            confidence=0.42,
        )

        result = validate_schema(schema)

        self.assertEqual(result.status, "blocked")
        codes = {issue.code for issue in result.issues}
        self.assertIn("unconfirmed_screenshot_value", codes)
        self.assertIn("low_confidence_screenshot_value", codes)

    def test_non_mvp_domain_is_draft_only_not_executable(self):
        schema = PhysicsProblemSchema(
            simulation_objective={"description": "Solve steady heat conduction in a plate."},
            physics_domain="heat-transfer",
            governing_model={"equation": "steady_heat_conduction"},
            geometry={"kind": "2d_plate", "dimensions": {"length": q(1.0), "height": q(0.2)}},
            materials=[
                {
                    "name": "aluminum",
                    "role": "solid",
                    "properties": {"thermal_conductivity": q(205.0, "W/(m*K)")},
                }
            ],
        )

        result = validate_schema(schema)

        self.assertEqual(result.status, "draft_only")
        self.assertFalse(result.can_generate_solver_input)
        self.assertIn("domain_not_implemented", {issue.code for issue in result.issues})

    def test_round_trip_from_dict_preserves_extension(self):
        schema = valid_cfd_schema()
        validate_schema(schema)
        data = json.loads(schema.to_json())

        loaded = PhysicsProblemSchema.from_dict(data)

        self.assertIsInstance(loaded.domain_extensions["cfdOpenfoam"], CFDExtension)
        self.assertEqual(loaded.domain_extensions["cfdOpenfoam"].case_family, "straight_pipe")


if __name__ == "__main__":
    unittest.main()
