"""Validation rules for Physics Problem Schema."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional, Set

from .schema import CFDExtension, PhysicsProblemSchema, Provenance, ValidationIssue, ValidationResult


MVP_SOLVABLE_DOMAINS: Set[str] = {"cfd"}
NON_MVP_DRAFT_DOMAINS: Set[str] = {
    "heat-transfer",
    "solid-mechanics",
    "pde",
    "multibody",
    "multiphysics",
}

SUPPORTED_CFD_CASES: Set[str] = {
    "straight_pipe",
    "bent_pipe",
    "room_ventilation",
    "flow_around_object",
}

CFD_REQUIRED_GEOMETRY: Dict[str, Set[str]] = {
    "straight_pipe": {"length", "diameter"},
    "bent_pipe": {"inlet_length", "outlet_length", "bend_radius", "diameter"},
    "room_ventilation": {"room_length", "room_width", "inlet_size", "outlet_size"},
    "flow_around_object": {"domain_length", "domain_height", "object_diameter"},
}

CFD_REQUIRED_BOUNDARIES: Dict[str, Set[str]] = {
    "straight_pipe": {"inlet", "outlet", "wall"},
    "bent_pipe": {"inlet", "outlet", "wall"},
    "room_ventilation": {"inlet", "outlet", "wall"},
    "flow_around_object": {"inlet", "outlet", "object", "farfield"},
}


def validate_schema(schema: PhysicsProblemSchema) -> ValidationResult:
    """Validate a schema and update `schema.validation` in place."""

    issues: List[ValidationIssue] = []
    domain = schema.physics_domain

    _validate_generic(schema, issues)
    _validate_assumptions(schema, issues)
    _validate_provenance(schema.provenance, "provenance", issues)
    _validate_nested_provenance(schema.to_dict(), issues)

    if not domain:
        issues.append(_blocking("missing_physics_domain", "Physics domain is required.", "physicsDomain", "Which physics domain does this simulation belong to?"))
    elif domain in NON_MVP_DRAFT_DOMAINS:
        issues.append(
            ValidationIssue(
                code="domain_not_implemented",
                message=f"Domain '{domain}' can be drafted but is not executable in the MVP.",
                severity="unsupported_domain",
                field="physicsDomain",
                question="Use draft-only mode, or choose an implemented CFD/OpenFOAM MVP case.",
            )
        )
    elif domain not in MVP_SOLVABLE_DOMAINS:
        issues.append(
            ValidationIssue(
                code="unknown_domain",
                message=f"Domain '{domain}' is not recognized as an MVP-solvable domain.",
                severity="human_review",
                field="physicsDomain",
                question="Please confirm the physics domain or provide a supported CFD/OpenFOAM problem.",
            )
        )

    if domain == "cfd":
        _validate_cfd(schema, issues)

    status = _status_from_issues(issues)
    result = ValidationResult(status=status, issues=issues)
    schema.validation = result
    return result


def _validate_generic(schema: PhysicsProblemSchema, issues: List[ValidationIssue]) -> None:
    if not schema.simulation_objective.get("description"):
        issues.append(_blocking("missing_objective", "Simulation objective is required.", "simulationObjective.description", "What should the simulation answer?"))

    if not schema.geometry.get("kind"):
        issues.append(_blocking("missing_geometry_kind", "Geometry kind is required.", "geometry.kind", "What geometry should be simulated?"))

    if not schema.materials:
        issues.append(_blocking("missing_materials", "At least one material or fluid is required.", "materials", "What material or fluid properties should be used?"))


def _validate_assumptions(schema: PhysicsProblemSchema, issues: List[ValidationIssue]) -> None:
    for assumption in schema.assumptions:
        if not assumption.approved:
            issues.append(
                _blocking(
                    "unapproved_assumption",
                    f"Assumption '{assumption.key}' must be approved before solver input generation.",
                    f"assumptions.{assumption.key}",
                    f"Approve or replace assumption '{assumption.key}'.",
                )
            )


def _validate_cfd(schema: PhysicsProblemSchema, issues: List[ValidationIssue]) -> None:
    extension = schema.domain_extensions.get("cfdOpenfoam")
    if isinstance(extension, Mapping):
        extension = CFDExtension.from_dict(extension)

    if not isinstance(extension, CFDExtension):
        issues.append(_blocking("missing_cfd_extension", "CFD/OpenFOAM extension is required for CFD MVP solving.", "domainExtensions.cfdOpenfoam", "Which CFD case family should be used?"))
        return

    if extension.case_family not in SUPPORTED_CFD_CASES:
        issues.append(
            ValidationIssue(
                code="unsupported_cfd_case",
                message=f"CFD case family '{extension.case_family}' is not supported in the MVP.",
                severity="unsupported_domain",
                field="domainExtensions.cfdOpenfoam.caseFamily",
                question="Choose straight_pipe, bent_pipe, room_ventilation, or flow_around_object.",
            )
        )
        return

    if extension.flow_regime != "incompressible":
        issues.append(
            ValidationIssue(
                code="unsupported_flow_regime",
                message=f"Flow regime '{extension.flow_regime}' is outside the MVP.",
                severity="unsupported_domain",
                field="domainExtensions.cfdOpenfoam.flowRegime",
                question="Use an incompressible single-phase CFD setup for the MVP.",
            )
        )

    geometry_values = schema.geometry.get("dimensions", {})
    for key in sorted(CFD_REQUIRED_GEOMETRY[extension.case_family]):
        value = geometry_values.get(key)
        if value is None:
            issues.append(_blocking("missing_geometry_dimension", f"Required geometry dimension '{key}' is missing.", f"geometry.dimensions.{key}", f"What is the {key.replace('_', ' ')}?"))
        else:
            _validate_quantity_has_unit(value, f"geometry.dimensions.{key}", issues)

    boundary_types = {
        str(boundary.get("type", ""))
        for boundary in schema.boundary_conditions
    }
    for boundary_type in sorted(CFD_REQUIRED_BOUNDARIES[extension.case_family] - boundary_types):
        issues.append(_blocking("missing_boundary_condition", f"Required boundary '{boundary_type}' is missing.", "boundaryConditions", f"What is the {boundary_type} boundary condition?"))

    _validate_cfd_material(schema.materials, issues)


def _validate_cfd_material(materials: Iterable[Mapping[str, Any]], issues: List[ValidationIssue]) -> None:
    fluid = next((item for item in materials if item.get("role") in {"fluid", "working_fluid"}), None)
    if not fluid:
        issues.append(_blocking("missing_fluid", "A CFD schema requires a fluid material.", "materials", "What fluid should be simulated?"))
        return

    properties = fluid.get("properties", {})
    has_density = "density" in properties
    has_dynamic_viscosity = "dynamic_viscosity" in properties
    has_kinematic_viscosity = "kinematic_viscosity" in properties

    if not has_density:
        issues.append(_blocking("missing_density", "Fluid density is required.", "materials.fluid.properties.density", "What is the fluid density?"))
    else:
        _validate_quantity_has_unit(properties["density"], "materials.fluid.properties.density", issues)

    if not (has_dynamic_viscosity or has_kinematic_viscosity):
        issues.append(_blocking("missing_viscosity", "Fluid dynamic or kinematic viscosity is required.", "materials.fluid.properties", "What is the fluid viscosity?"))
    else:
        if has_dynamic_viscosity:
            _validate_quantity_has_unit(properties["dynamic_viscosity"], "materials.fluid.properties.dynamic_viscosity", issues)
        if has_kinematic_viscosity:
            _validate_quantity_has_unit(properties["kinematic_viscosity"], "materials.fluid.properties.kinematic_viscosity", issues)


def _validate_quantity_has_unit(value: Any, field: str, issues: List[ValidationIssue]) -> None:
    if not isinstance(value, Mapping) or "value" not in value:
        issues.append(_blocking("invalid_quantity", f"Field '{field}' must be a quantity with value and unit.", field, f"Provide value and unit for {field}."))
        return
    if value.get("unit") in (None, ""):
        issues.append(_blocking("missing_unit", f"Field '{field}' is missing a unit.", field, f"What unit should be used for {field}?"))


def _validate_nested_provenance(value: Any, issues: List[ValidationIssue], path: str = "") -> None:
    if isinstance(value, Mapping):
        if "provenance" in value and isinstance(value["provenance"], list):
            _validate_provenance(
                [Provenance.from_dict(item) for item in value["provenance"]],
                path or "value",
                issues,
            )
        for key, child in value.items():
            _validate_nested_provenance(child, issues, f"{path}.{key}" if path else str(key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _validate_nested_provenance(child, issues, f"{path}.{index}" if path else str(index))


def _validate_provenance(provenance: Iterable[Provenance], field: str, issues: List[ValidationIssue]) -> None:
    for item in provenance:
        if item.source == "screenshot" and not item.confirmed:
            issues.append(
                _blocking(
                    "unconfirmed_screenshot_value",
                    f"Screenshot-derived value at '{field}' must be confirmed before solver input generation.",
                    field,
                    "Please confirm the value extracted from the screenshot.",
                )
            )
        if item.source == "screenshot" and item.confidence is not None and item.confidence < 0.8:
            issues.append(
                _blocking(
                    "low_confidence_screenshot_value",
                    f"Screenshot-derived value at '{field}' has low confidence.",
                    field,
                    "Please confirm or replace the low-confidence screenshot value.",
                )
            )


def _status_from_issues(issues: List[ValidationIssue]) -> str:
    severities = {issue.severity for issue in issues}
    if "blocking" in severities:
        return "blocked"
    if "unsupported_domain" in severities:
        return "draft_only"
    if "human_review" in severities:
        return "human_review"
    return "valid"


def _blocking(code: str, message: str, field: str, question: str) -> ValidationIssue:
    return ValidationIssue(
        code=code,
        message=message,
        severity="blocking",
        field=field,
        question=question,
    )
