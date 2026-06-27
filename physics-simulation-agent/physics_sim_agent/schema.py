"""Canonical Physics Problem Schema.

The schema is intentionally solver-neutral. Domain packs may attach typed
extensions, but downstream solver adapters should only receive schemas that pass
validation without blockers.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional


SCHEMA_VERSION = "0.1.0"


@dataclass
class Provenance:
    """Where a value came from and whether it is safe to use."""

    source: str
    source_ref: str
    method: str = "user_provided"
    confidence: Optional[float] = None
    confirmed: bool = True
    notes: str = ""

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Provenance":
        return cls(
            source=str(data.get("source", "")),
            source_ref=str(data.get("sourceRef", data.get("source_ref", ""))),
            method=str(data.get("method", "user_provided")),
            confidence=data.get("confidence"),
            confirmed=bool(data.get("confirmed", True)),
            notes=str(data.get("notes", "")),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "sourceRef": self.source_ref,
            "method": self.method,
            "confidence": self.confidence,
            "confirmed": self.confirmed,
            "notes": self.notes,
        }


@dataclass
class Quantity:
    """A numeric, textual, or structured value with unit and provenance."""

    value: Any
    unit: Optional[str] = None
    provenance: List[Provenance] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Quantity":
        return cls(
            value=data.get("value"),
            unit=data.get("unit"),
            provenance=[
                Provenance.from_dict(item)
                for item in data.get("provenance", [])
            ],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "unit": self.unit,
            "provenance": [item.to_dict() for item in self.provenance],
        }


@dataclass
class Assumption:
    """A default or inferred value that requires explicit approval."""

    key: str
    value: Any
    rationale: str
    risk: str
    source: str = "default"
    approved: bool = False

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Assumption":
        return cls(
            key=str(data.get("key", "")),
            value=data.get("value"),
            rationale=str(data.get("rationale", "")),
            risk=str(data.get("risk", "")),
            source=str(data.get("source", "default")),
            approved=bool(data.get("approved", False)),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationIssue:
    """A structured validation message suitable for CLI or UI display."""

    code: str
    message: str
    severity: str = "blocking"
    field: str = ""
    question: str = ""

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ValidationIssue":
        return cls(
            code=str(data.get("code", "")),
            message=str(data.get("message", "")),
            severity=str(data.get("severity", "blocking")),
            field=str(data.get("field", "")),
            question=str(data.get("question", "")),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationResult:
    """Validation status for a schema draft or confirmed problem."""

    status: str = "draft"
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def blockers(self) -> List[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == "blocking"]

    @property
    def can_generate_solver_input(self) -> bool:
        return self.status == "valid" and not self.blockers

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ValidationResult":
        return cls(
            status=str(data.get("status", "draft")),
            issues=[
                ValidationIssue.from_dict(item)
                for item in data.get("issues", [])
            ],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "canGenerateSolverInput": self.can_generate_solver_input,
            "issues": [issue.to_dict() for issue in self.issues],
        }


@dataclass
class CFDExtension:
    """MVP CFD/OpenFOAM domain extension."""

    case_family: str
    flow_regime: str = "incompressible"
    dimensionality: str = "2d"
    solver_family: str = "openfoam"
    turbulence_model: Optional[str] = None
    transient: bool = False

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "CFDExtension":
        return cls(
            case_family=str(data.get("caseFamily", data.get("case_family", ""))),
            flow_regime=str(data.get("flowRegime", data.get("flow_regime", "incompressible"))),
            dimensionality=str(data.get("dimensionality", "2d")),
            solver_family=str(data.get("solverFamily", data.get("solver_family", "openfoam"))),
            turbulence_model=data.get("turbulenceModel", data.get("turbulence_model")),
            transient=bool(data.get("transient", False)),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "caseFamily": self.case_family,
            "flowRegime": self.flow_regime,
            "dimensionality": self.dimensionality,
            "solverFamily": self.solver_family,
            "turbulenceModel": self.turbulence_model,
            "transient": self.transient,
        }


def _quantity_map_to_dict(values: Mapping[str, Quantity]) -> Dict[str, Any]:
    return {key: value.to_dict() for key, value in values.items()}


def _quantity_map_from_dict(values: Mapping[str, Any]) -> Dict[str, Quantity]:
    return {key: Quantity.from_dict(value) for key, value in values.items()}


@dataclass
class PhysicsProblemSchema:
    """Solver-neutral representation of a physical simulation problem."""

    simulation_objective: Dict[str, Any]
    physics_domain: str
    governing_model: Dict[str, Any]
    geometry: Dict[str, Any]
    materials: List[Dict[str, Any]]
    initial_conditions: List[Dict[str, Any]] = field(default_factory=list)
    boundary_conditions: List[Dict[str, Any]] = field(default_factory=list)
    mesh_strategy: Dict[str, Any] = field(default_factory=dict)
    time_strategy: Dict[str, Any] = field(default_factory=dict)
    solver_strategy: Dict[str, Any] = field(default_factory=dict)
    postprocessing_targets: List[Dict[str, Any]] = field(default_factory=list)
    assumptions: List[Assumption] = field(default_factory=list)
    provenance: List[Provenance] = field(default_factory=list)
    domain_extensions: Dict[str, Any] = field(default_factory=dict)
    validation: ValidationResult = field(default_factory=ValidationResult)
    schema_version: str = SCHEMA_VERSION

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "PhysicsProblemSchema":
        extensions = dict(data.get("domainExtensions", data.get("domain_extensions", {})))
        if "cfdOpenfoam" in extensions and not isinstance(extensions["cfdOpenfoam"], CFDExtension):
            extensions["cfdOpenfoam"] = CFDExtension.from_dict(extensions["cfdOpenfoam"])

        return cls(
            schema_version=str(data.get("schemaVersion", data.get("schema_version", SCHEMA_VERSION))),
            simulation_objective=dict(data.get("simulationObjective", data.get("simulation_objective", {}))),
            physics_domain=str(data.get("physicsDomain", data.get("physics_domain", ""))),
            governing_model=dict(data.get("governingModel", data.get("governing_model", {}))),
            geometry=dict(data.get("geometry", {})),
            materials=list(data.get("materials", [])),
            initial_conditions=list(data.get("initialConditions", data.get("initial_conditions", []))),
            boundary_conditions=list(data.get("boundaryConditions", data.get("boundary_conditions", []))),
            mesh_strategy=dict(data.get("meshStrategy", data.get("mesh_strategy", {}))),
            time_strategy=dict(data.get("timeStrategy", data.get("time_strategy", {}))),
            solver_strategy=dict(data.get("solverStrategy", data.get("solver_strategy", {}))),
            postprocessing_targets=list(data.get("postprocessingTargets", data.get("postprocessing_targets", []))),
            assumptions=[
                Assumption.from_dict(item)
                for item in data.get("assumptions", [])
            ],
            provenance=[
                Provenance.from_dict(item)
                for item in data.get("provenance", [])
            ],
            domain_extensions=extensions,
            validation=ValidationResult.from_dict(data.get("validation", {})),
        )

    def attach_cfd_extension(self, extension: CFDExtension) -> None:
        self.domain_extensions["cfdOpenfoam"] = extension

    def to_dict(self) -> Dict[str, Any]:
        extensions: Dict[str, Any] = {}
        for key, value in self.domain_extensions.items():
            if hasattr(value, "to_dict"):
                extensions[key] = value.to_dict()
            else:
                extensions[key] = value

        return {
            "schemaVersion": self.schema_version,
            "simulationObjective": self.simulation_objective,
            "physicsDomain": self.physics_domain,
            "governingModel": self.governing_model,
            "geometry": self.geometry,
            "materials": self.materials,
            "initialConditions": self.initial_conditions,
            "boundaryConditions": self.boundary_conditions,
            "meshStrategy": self.mesh_strategy,
            "timeStrategy": self.time_strategy,
            "solverStrategy": self.solver_strategy,
            "postprocessingTargets": self.postprocessing_targets,
            "assumptions": [item.to_dict() for item in self.assumptions],
            "provenance": [item.to_dict() for item in self.provenance],
            "domainExtensions": extensions,
            "validation": self.validation.to_dict(),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2, sort_keys=True)

    def save(self, path: str | Path) -> None:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(self.to_json() + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "PhysicsProblemSchema":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_dict(data)


def quantity(value: Any, unit: Optional[str], source_ref: str = "user") -> Dict[str, Any]:
    """Convenience helper for nested schema values in fixtures and tests."""

    return Quantity(
        value=value,
        unit=unit,
        provenance=[Provenance(source="user", source_ref=source_ref)],
    ).to_dict()
