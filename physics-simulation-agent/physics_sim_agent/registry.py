"""Solver registry for domain packs and solver adapters."""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from .adapters import (
    CapabilityResult,
    DomainPackMetadata,
    FUTURE_DOMAIN_PACKS,
    OpenFOAMAdapter,
    SolverAdapter,
    SolverSelection,
)
from .schema import PhysicsProblemSchema
from .validation import validate_schema


class SolverRegistry:
    """Registry that routes validated schemas to solver adapters."""

    def __init__(self) -> None:
        self._adapters: Dict[str, SolverAdapter] = {}
        self._domain_packs: Dict[str, DomainPackMetadata] = {}

    def register_adapter(self, adapter: SolverAdapter) -> None:
        self._adapters[adapter.name] = adapter
        self._domain_packs[adapter.domain_pack.physics_domain] = adapter.domain_pack

    def register_domain_pack(self, metadata: DomainPackMetadata) -> None:
        self._domain_packs[metadata.physics_domain] = metadata

    def adapters(self) -> List[SolverAdapter]:
        return list(self._adapters.values())

    def domain_packs(self) -> List[DomainPackMetadata]:
        return list(self._domain_packs.values())

    def get_domain_pack(self, physics_domain: str) -> Optional[DomainPackMetadata]:
        return self._domain_packs.get(physics_domain)

    def capabilities_for(self, schema: PhysicsProblemSchema) -> List[CapabilityResult]:
        return [adapter.explain_capability(schema) for adapter in self.adapters()]

    def select_adapter(self, schema: PhysicsProblemSchema) -> SolverSelection:
        candidates = self.capabilities_for(schema)
        supported = [candidate for candidate in candidates if candidate.supported]
        if supported:
            selected_capability = supported[0]
            adapter = self._adapters.get(selected_capability.adapter_name or "")
            return SolverSelection(
                capability=selected_capability,
                adapter=adapter,
                candidates=candidates,
            )

        validation = validate_schema(schema)
        metadata = self.get_domain_pack(schema.physics_domain)
        if metadata and metadata.status != "implemented":
            capability = CapabilityResult(
                status="draft_only",
                domain_pack=metadata.name,
                rationale=(
                    f"Domain '{schema.physics_domain}' is known but {metadata.name} is "
                    "not implemented in the MVP, so the problem can only be drafted."
                ),
                limitations=list(metadata.limitations),
                issues=validation.issues,
            )
        elif validation.status == "blocked":
            capability = CapabilityResult(
                status="needs_clarification",
                rationale="No adapter can be selected until blocking validation issues are resolved.",
                issues=validation.issues,
            )
        elif validation.status == "human_review":
            capability = CapabilityResult(
                status="human_review",
                rationale="The physics domain is not recognized by the current registry and needs human review.",
                issues=validation.issues,
            )
        else:
            capability = CapabilityResult(
                status="unsupported",
                rationale=f"No registered adapter supports physics domain '{schema.physics_domain}'.",
                issues=validation.issues,
            )

        return SolverSelection(capability=capability, candidates=candidates)


def create_default_registry() -> SolverRegistry:
    """Create the MVP registry with OpenFOAM implemented and future packs planned."""

    registry = SolverRegistry()
    registry.register_adapter(OpenFOAMAdapter())
    for metadata in FUTURE_DOMAIN_PACKS.values():
        registry.register_domain_pack(metadata)
    return registry
