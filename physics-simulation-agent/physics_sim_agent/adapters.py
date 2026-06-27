"""Solver adapter contracts and MVP adapter shells."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Sequence

from .openfoam_case import generate_openfoam_case
from .schema import CFDExtension, PhysicsProblemSchema, ValidationIssue
from .validation import SUPPORTED_CFD_CASES, validate_schema


@dataclass(frozen=True)
class DomainPackMetadata:
    """Metadata that describes a domain pack without claiming execution support."""

    name: str
    physics_domain: str
    status: str
    supported_case_families: Sequence[str] = field(default_factory=tuple)
    solver_adapters: Sequence[str] = field(default_factory=tuple)
    supported_solver_versions: Sequence[str] = field(default_factory=tuple)
    limitations: Sequence[str] = field(default_factory=tuple)
    golden_cases: Sequence[str] = field(default_factory=tuple)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "physicsDomain": self.physics_domain,
            "status": self.status,
            "supportedCaseFamilies": list(self.supported_case_families),
            "solverAdapters": list(self.solver_adapters),
            "supportedSolverVersions": list(self.supported_solver_versions),
            "limitations": list(self.limitations),
            "goldenCases": list(self.golden_cases),
        }


@dataclass
class CapabilityResult:
    """Adapter or registry decision about a schema."""

    status: str
    rationale: str
    adapter_name: Optional[str] = None
    domain_pack: Optional[str] = None
    limitations: List[str] = field(default_factory=list)
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def supported(self) -> bool:
        return self.status == "supported"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "rationale": self.rationale,
            "adapterName": self.adapter_name,
            "domainPack": self.domain_pack,
            "limitations": list(self.limitations),
            "issues": [issue.to_dict() for issue in self.issues],
        }


@dataclass
class SolverSelection:
    """Registry output for downstream workflow controllers."""

    capability: CapabilityResult
    adapter: Optional["SolverAdapter"] = None
    candidates: List[CapabilityResult] = field(default_factory=list)

    @property
    def selected(self) -> bool:
        return self.adapter is not None and self.capability.supported


class SolverAdapter(Protocol):
    """Interface every concrete solver adapter must satisfy."""

    name: str
    domain_pack: DomainPackMetadata

    def can_handle(self, schema: PhysicsProblemSchema) -> CapabilityResult:
        ...

    def explain_capability(self, schema: PhysicsProblemSchema) -> CapabilityResult:
        ...

    def generate_solver_input(self, schema: PhysicsProblemSchema, workspace: Path) -> Path:
        ...

    def get_execution_plan(self, schema: PhysicsProblemSchema, workspace: Path) -> Dict[str, Any]:
        ...

    def parse_logs(self, logs: Sequence[Path]) -> Dict[str, Any]:
        ...

    def parse_results(self, results: Sequence[Path]) -> Dict[str, Any]:
        ...

    def describe_limitations(self) -> Sequence[str]:
        ...


OPENFOAM_DOMAIN_PACK = DomainPackMetadata(
    name="domain-pack-cfd-openfoam",
    physics_domain="cfd",
    status="implemented",
    supported_case_families=tuple(sorted(SUPPORTED_CFD_CASES)),
    solver_adapters=("OpenFOAMAdapter",),
    supported_solver_versions=("local-compatible", "docker-compatible"),
    limitations=(
        "MVP supports single-phase incompressible CFD only.",
        "MVP supports simple 2D geometries for straight pipe, bent pipe, room ventilation, and flow around object.",
        "Solver input generation is implemented in the CFD/OpenFOAM domain-pack milestone, not in the registry shell.",
    ),
    golden_cases=(
        "cfd_straight_pipe",
        "cfd_bent_pipe",
        "cfd_room_ventilation",
        "cfd_flow_around_object",
    ),
)


FUTURE_DOMAIN_PACKS: Dict[str, DomainPackMetadata] = {
    "heat-transfer": DomainPackMetadata(
        name="domain-pack-heat-transfer",
        physics_domain="heat-transfer",
        status="planned",
        solver_adapters=("FutureHeatTransferAdapter",),
        limitations=("Draft-only in the MVP; no automatic solver execution is claimed.",),
        golden_cases=("steady_plate_conduction",),
    ),
    "solid-mechanics": DomainPackMetadata(
        name="domain-pack-solid-mechanics",
        physics_domain="solid-mechanics",
        status="planned",
        solver_adapters=("FutureSolidMechanicsAdapter",),
        limitations=("Draft-only in the MVP; no automatic solver execution is claimed.",),
        golden_cases=("cantilever_beam_static",),
    ),
    "pde": DomainPackMetadata(
        name="domain-pack-pde-fenicsx",
        physics_domain="pde",
        status="planned",
        solver_adapters=("FutureFenicsxAdapter",),
        limitations=("Draft-only in the MVP; FEniCSx execution is not implemented.",),
        golden_cases=("poisson_equation", "diffusion_equation"),
    ),
    "multibody": DomainPackMetadata(
        name="domain-pack-multibody-chrono",
        physics_domain="multibody",
        status="planned",
        solver_adapters=("FutureChronoAdapter",),
        limitations=("Draft-only in the MVP; Chrono execution is not implemented.",),
        golden_cases=("spring_mass_system", "simple_pendulum"),
    ),
    "multiphysics": DomainPackMetadata(
        name="domain-pack-multiphysics-moose",
        physics_domain="multiphysics",
        status="planned",
        solver_adapters=("FutureMooseAdapter",),
        limitations=("Draft-only in the MVP; MOOSE execution is not implemented.",),
        golden_cases=("thermal_structural_demo",),
    ),
}


class OpenFOAMAdapter:
    """Registration shell for the MVP CFD/OpenFOAM adapter."""

    name = "OpenFOAMAdapter"
    domain_pack = OPENFOAM_DOMAIN_PACK

    def can_handle(self, schema: PhysicsProblemSchema) -> CapabilityResult:
        return self.explain_capability(schema)

    def explain_capability(self, schema: PhysicsProblemSchema) -> CapabilityResult:
        validation = validate_schema(schema)
        limitations = list(self.domain_pack.limitations)

        if schema.physics_domain != "cfd":
            return CapabilityResult(
                status="unsupported",
                adapter_name=self.name,
                domain_pack=self.domain_pack.name,
                rationale=f"{self.name} only handles CFD/OpenFOAM schemas.",
                limitations=limitations,
                issues=validation.issues,
            )

        if validation.status == "blocked":
            return CapabilityResult(
                status="needs_clarification",
                adapter_name=self.name,
                domain_pack=self.domain_pack.name,
                rationale="The CFD schema has blocking validation issues that must be resolved before selecting OpenFOAM.",
                limitations=limitations,
                issues=validation.issues,
            )

        if validation.status in {"draft_only", "human_review"}:
            return CapabilityResult(
                status=validation.status,
                adapter_name=self.name,
                domain_pack=self.domain_pack.name,
                rationale="The schema is not ready for OpenFOAM execution.",
                limitations=limitations,
                issues=validation.issues,
            )

        extension = schema.domain_extensions.get("cfdOpenfoam")
        if isinstance(extension, dict):
            extension = CFDExtension.from_dict(extension)

        if not isinstance(extension, CFDExtension):
            return CapabilityResult(
                status="needs_clarification",
                adapter_name=self.name,
                domain_pack=self.domain_pack.name,
                rationale="CFD schema lacks the cfdOpenfoam domain extension.",
                limitations=limitations,
                issues=validation.issues,
            )

        if extension.solver_family != "openfoam":
            return CapabilityResult(
                status="unsupported",
                adapter_name=self.name,
                domain_pack=self.domain_pack.name,
                rationale=f"Requested solver family '{extension.solver_family}' is not OpenFOAM.",
                limitations=limitations,
                issues=validation.issues,
            )

        return CapabilityResult(
            status="supported",
            adapter_name=self.name,
            domain_pack=self.domain_pack.name,
            rationale=f"Validated CFD schema matches OpenFOAM MVP case family '{extension.case_family}'.",
            limitations=limitations,
            issues=validation.issues,
        )

    def generate_solver_input(self, schema: PhysicsProblemSchema, workspace: Path) -> Path:
        return generate_openfoam_case(schema, workspace)

    def get_execution_plan(self, schema: PhysicsProblemSchema, workspace: Path) -> Dict[str, Any]:
        return {
            "adapter": self.name,
            "domainPack": self.domain_pack.name,
            "stages": ["blockMesh", "checkMesh", "solver", "postProcess"],
            "workspace": str(workspace),
        }

    def parse_logs(self, logs: Sequence[Path]) -> Dict[str, Any]:
        from .execution import parse_check_mesh_log, parse_solver_log

        parsed: Dict[str, Any] = {}
        for log in logs:
            text = Path(log).read_text(encoding="utf-8")
            if "checkMesh" in log.name:
                parsed[log.name] = parse_check_mesh_log(text)
            else:
                parsed[log.name] = parse_solver_log(text)
        return parsed

    def parse_results(self, results: Sequence[Path]) -> Dict[str, Any]:
        raise NotImplementedError(
            "OpenFOAM result parsing belongs to the report/delivery milestone."
        )

    def describe_limitations(self) -> Sequence[str]:
        return self.domain_pack.limitations
