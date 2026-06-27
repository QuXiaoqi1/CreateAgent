import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from physics_sim_agent import (
    CFDExtension,
    DomainPackMetadata,
    OpenFOAMAdapter,
    PhysicsProblemSchema,
    SolverRegistry,
    create_default_registry,
    validate_schema,
)
from test_schema import valid_cfd_schema


class SolverRegistryTests(unittest.TestCase):
    def test_default_registry_selects_openfoam_for_valid_cfd(self):
        registry = create_default_registry()
        schema = valid_cfd_schema()
        validate_schema(schema)

        selection = registry.select_adapter(schema)

        self.assertTrue(selection.selected)
        self.assertIsInstance(selection.adapter, OpenFOAMAdapter)
        self.assertEqual(selection.capability.status, "supported")
        self.assertEqual(selection.capability.adapter_name, "OpenFOAMAdapter")
        self.assertEqual(selection.capability.domain_pack, "domain-pack-cfd-openfoam")
        self.assertIn("straight_pipe", selection.capability.rationale)

    def test_blocked_cfd_returns_needs_clarification(self):
        registry = create_default_registry()
        schema = valid_cfd_schema()
        schema.geometry["dimensions"]["length"]["unit"] = None

        selection = registry.select_adapter(schema)

        self.assertFalse(selection.selected)
        self.assertEqual(selection.capability.status, "needs_clarification")
        self.assertIn("missing_unit", {issue.code for issue in selection.capability.issues})

    def test_future_heat_domain_is_draft_only_without_false_support(self):
        registry = create_default_registry()
        fixture = Path(__file__).resolve().parents[1] / "fixtures" / "heat_transfer_draft.schema.json"
        schema = PhysicsProblemSchema.load(fixture)

        selection = registry.select_adapter(schema)

        self.assertFalse(selection.selected)
        self.assertIsNone(selection.adapter)
        self.assertEqual(selection.capability.status, "draft_only")
        self.assertEqual(selection.capability.domain_pack, "domain-pack-heat-transfer")
        self.assertIn("not implemented", selection.capability.rationale)

    def test_unknown_domain_requires_human_review(self):
        registry = create_default_registry()
        schema = PhysicsProblemSchema(
            simulation_objective={"description": "Simulate a magnetic field."},
            physics_domain="electromagnetics",
            governing_model={"equation": "unknown"},
            geometry={"kind": "2d_domain"},
            materials=[{"name": "air", "role": "medium", "properties": {}}],
        )

        selection = registry.select_adapter(schema)

        self.assertFalse(selection.selected)
        self.assertEqual(selection.capability.status, "human_review")

    def test_custom_adapter_registration_records_domain_pack(self):
        registry = SolverRegistry()
        adapter = OpenFOAMAdapter()

        registry.register_adapter(adapter)

        self.assertEqual(registry.get_domain_pack("cfd").name, "domain-pack-cfd-openfoam")
        self.assertEqual(len(registry.adapters()), 1)

    def test_unimplemented_future_metadata_has_no_adapter(self):
        registry = create_default_registry()

        pack_names = {pack.name for pack in registry.domain_packs()}
        adapter_names = {adapter.name for adapter in registry.adapters()}

        self.assertIn("domain-pack-pde-fenicsx", pack_names)
        self.assertIn("domain-pack-multibody-chrono", pack_names)
        self.assertEqual(adapter_names, {"OpenFOAMAdapter"})

    def test_unsupported_solver_family_is_not_selected(self):
        registry = create_default_registry()
        schema = valid_cfd_schema()
        schema.attach_cfd_extension(
            CFDExtension(case_family="straight_pipe", solver_family="fenicsx")
        )

        selection = registry.select_adapter(schema)

        self.assertFalse(selection.selected)
        self.assertEqual(selection.capability.status, "unsupported")


if __name__ == "__main__":
    unittest.main()
