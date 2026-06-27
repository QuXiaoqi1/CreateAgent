"""Production-readiness checks for the MVP platform."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Sequence

from .adapters import OpenFOAMAdapter
from .delivery import build_delivery_package
from .execution import ExecutionSummary, detect_environment, execute_openfoam_case
from .intake import build_schema_draft, table_text_artifact, text_artifact
from .schema import PhysicsProblemSchema
from .validation import validate_schema


PASS = "pass"
FAIL = "fail"
SKIP = "skip"
RISK = "risk"


@dataclass
class ReadinessItem:
    name: str
    status: str
    message: str
    evidence: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "evidence": list(self.evidence),
        }


@dataclass
class MockWorkflowResult:
    item: ReadinessItem
    package_dir: Path
    case_dir: Path
    execution: ExecutionSummary


@dataclass
class ReleaseReadinessReport:
    overall_status: str
    generated_at: str
    items: List[ReadinessItem]
    limitations: List[str]
    risks: List[str]
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overallStatus": self.overall_status,
            "generatedAt": self.generated_at,
            "items": [item.to_dict() for item in self.items],
            "limitations": list(self.limitations),
            "risks": list(self.risks),
            "recommendations": list(self.recommendations),
        }

    def to_markdown(self) -> str:
        rows = ["| Check | Status | Message |", "| --- | --- | --- |"]
        for item in self.items:
            rows.append(
                f"| {_md_escape(item.name)} | {_md_escape(item.status)} | {_md_escape(item.message)} |"
            )
        return f"""# Physics Simulation Agent Release Readiness

Overall status: `{self.overall_status}`
Generated at: `{self.generated_at}`

## Checks

{chr(10).join(rows)}

## Limitations

{_markdown_list(self.limitations)}

## Risks

{_markdown_list(self.risks)}

## Recommendations

{_markdown_list(self.recommendations)}
"""

    def save(self, output_dir: str | Path) -> Path:
        destination = Path(output_dir)
        destination.mkdir(parents=True, exist_ok=True)
        (destination / "release-readiness.json").write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (destination / "release-readiness.md").write_text(self.to_markdown(), encoding="utf-8")
        return destination


def run_release_readiness(
    project_root: str | Path,
    output_dir: str | Path | None = None,
    run_real_smoke: bool = True,
) -> ReleaseReadinessReport:
    project = resolve_project_root(project_root)
    output = Path(output_dir) if output_dir is not None else project / "release-readiness"
    output.mkdir(parents=True, exist_ok=True)

    items: List[ReadinessItem] = [
        check_fixture_structure(project),
        check_test_surface(project),
        check_non_mvp_draft_only(project),
    ]
    workflow = run_mock_full_workflow(project, output / "mock-full-workflow")
    items.append(workflow.item)

    if run_real_smoke:
        items.append(run_conditional_real_smoke(project, output / "real-smoke"))
    else:
        items.append(
            ReadinessItem(
                name="conditional_real_openfoam_smoke",
                status=SKIP,
                message="Real OpenFOAM smoke test was disabled for this readiness run.",
                evidence=["run_real_smoke=False"],
            )
        )

    limitations = _limitations_from_items(items)
    risks = _risks_from_items(items)
    report = ReleaseReadinessReport(
        overall_status=_overall_status(items),
        generated_at=datetime.now(timezone.utc).isoformat(),
        items=items,
        limitations=limitations,
        risks=risks,
        recommendations=[
            "Wire readiness checks into the GitHub CLI command surface.",
            "Enable Docker/OpenFOAM image configuration before claiming container execution support.",
            "Use heat-transfer as the next domain pack only after CFD MVP reliability is stable.",
        ],
    )
    report.save(output)
    return report


def resolve_project_root(path: str | Path) -> Path:
    candidate = Path(path)
    if (candidate / "physics_sim_agent").is_dir():
        return candidate
    nested = candidate / "physics-simulation-agent"
    if (nested / "physics_sim_agent").is_dir():
        return nested
    return candidate


def check_fixture_structure(project_root: str | Path) -> ReadinessItem:
    project = resolve_project_root(project_root)
    fixture_dir = project / "fixtures"
    required_files = [
        fixture_dir / "cfd_golden_cases.json",
        fixture_dir / "straight_pipe.schema.json",
        fixture_dir / "heat_transfer_draft.schema.json",
        fixture_dir / "solid_mechanics_draft.schema.json",
    ]
    missing = [str(path) for path in required_files if not path.exists()]
    if missing:
        return ReadinessItem(
            name="fixture_structure",
            status=FAIL,
            message="Required fixture files are missing.",
            evidence=missing,
        )

    golden_cases = _load_golden_cases(project)
    expected_families = {"straight_pipe", "bent_pipe", "room_ventilation", "flow_around_object"}
    actual_families = {str(case.get("caseFamily")) for case in golden_cases}
    missing_families = sorted(expected_families - actual_families)
    if missing_families:
        return ReadinessItem(
            name="fixture_structure",
            status=FAIL,
            message="CFD golden-case fixture is incomplete.",
            evidence=missing_families,
        )

    return ReadinessItem(
        name="fixture_structure",
        status=PASS,
        message="Golden cases and draft-only fixtures are present.",
        evidence=[str(path.relative_to(project)) for path in required_files],
    )


def check_test_surface(project_root: str | Path) -> ReadinessItem:
    project = resolve_project_root(project_root)
    expected_tests = [
        "test_schema.py",
        "test_intake.py",
        "test_registry.py",
        "test_openfoam_case.py",
        "test_execution.py",
        "test_delivery.py",
        "test_readiness.py",
        "test_workspace.py",
    ]
    missing = [name for name in expected_tests if not (project / "tests" / name).exists()]
    if missing:
        return ReadinessItem(
            name="test_surface",
            status=FAIL,
            message="Expected production-readiness test files are missing.",
            evidence=missing,
        )
    return ReadinessItem(
        name="test_surface",
        status=PASS,
        message="Workspace, schema, intake, registry, case generation, execution, delivery, and readiness tests are present.",
        evidence=["python3 -m unittest discover physics-simulation-agent/tests"],
    )


def check_non_mvp_draft_only(project_root: str | Path) -> ReadinessItem:
    project = resolve_project_root(project_root)
    fixture_dir = project / "fixtures"
    fixtures = [
        fixture_dir / "heat_transfer_draft.schema.json",
        fixture_dir / "solid_mechanics_draft.schema.json",
    ]
    evidence: List[str] = []
    failures: List[str] = []
    for path in fixtures:
        schema = PhysicsProblemSchema.load(path)
        result = validate_schema(schema)
        evidence.append(f"{path.name}: {result.status}")
        if result.status != "draft_only" or result.can_generate_solver_input:
            failures.append(path.name)

    if failures:
        return ReadinessItem(
            name="non_mvp_draft_only",
            status=FAIL,
            message="A non-MVP domain can incorrectly proceed toward solver generation.",
            evidence=failures,
        )
    return ReadinessItem(
        name="non_mvp_draft_only",
        status=PASS,
        message="Heat-transfer and solid-mechanics remain draft-only.",
        evidence=evidence,
    )


def run_mock_full_workflow(project_root: str | Path, workspace: str | Path) -> MockWorkflowResult:
    project = resolve_project_root(project_root)
    workspace_path = Path(workspace)
    workspace_path.mkdir(parents=True, exist_ok=True)

    golden_case = _load_golden_cases(project)[0]
    draft = build_schema_draft(
        [
            text_artifact(str(golden_case["prompt"])),
            table_text_artifact(str(golden_case["table"])),
        ]
    )
    if draft.schema.validation.status != "valid":
        item = ReadinessItem(
            name="mock_full_workflow",
            status=FAIL,
            message="Intake did not produce a valid CFD schema.",
            evidence=[issue.to_dict().get("message", "") for issue in draft.schema.validation.issues],
        )
        placeholder = workspace_path / "delivery-package"
        return MockWorkflowResult(item=item, package_dir=placeholder, case_dir=workspace_path, execution=_empty_execution())

    adapter = OpenFOAMAdapter()
    case_dir = adapter.generate_solver_input(draft.schema, workspace_path)
    execution = execute_openfoam_case(case_dir, mode="mock")
    package_dir = build_delivery_package(
        draft.schema,
        case_dir,
        execution,
        workspace_path / "delivery-package",
        user_text=str(golden_case["prompt"]),
    )
    required = [
        package_dir / "problem.schema.json",
        package_dir / "solver-input" / "openfoam-case" / "run.sh",
        package_dir / "logs" / "execution-summary.json",
        package_dir / "report.md",
        package_dir / "validation-evidence.json",
    ]
    missing = [str(path.relative_to(package_dir)) for path in required if not path.exists()]
    if execution.status != "completed" or missing:
        item = ReadinessItem(
            name="mock_full_workflow",
            status=FAIL,
            message="Mock workflow did not complete with a reproducible delivery package.",
            evidence=missing or [f"execution.status={execution.status}"],
        )
    else:
        item = ReadinessItem(
            name="mock_full_workflow",
            status=PASS,
            message="Natural-language/table input reached a complete mock delivery package.",
            evidence=[str(package_dir)],
        )
    return MockWorkflowResult(item=item, package_dir=package_dir, case_dir=case_dir, execution=execution)


def run_conditional_real_smoke(project_root: str | Path, workspace: str | Path) -> ReadinessItem:
    project = resolve_project_root(project_root)
    environment = detect_environment()
    if not environment.available:
        return ReadinessItem(
            name="conditional_real_openfoam_smoke",
            status=SKIP,
            message="No local OpenFOAM or Docker/OpenFOAM runtime is available; real smoke test skipped.",
            evidence=environment.limitations,
        )

    golden_case = _load_golden_cases(project)[0]
    draft = build_schema_draft(
        [
            text_artifact(str(golden_case["prompt"])),
            table_text_artifact(str(golden_case["table"])),
        ]
    )
    case_dir = OpenFOAMAdapter().generate_solver_input(draft.schema, Path(workspace))
    execution = execute_openfoam_case(case_dir, mode="auto")
    summary_path = case_dir / "logs" / "execution-summary.json"

    if execution.status == "completed":
        return ReadinessItem(
            name="conditional_real_openfoam_smoke",
            status=PASS,
            message=f"Real smoke test completed through {execution.mode} execution.",
            evidence=[str(summary_path)],
        )

    diagnostics = [
        stage.diagnosis.recommended_action
        for stage in execution.stages
        if stage.diagnosis is not None
    ]
    return ReadinessItem(
        name="conditional_real_openfoam_smoke",
        status=FAIL,
        message=f"Real smoke test detected {environment.mode} runtime but did not complete.",
        evidence=diagnostics or [str(summary_path)],
    )


def _load_golden_cases(project: Path) -> Sequence[Dict[str, Any]]:
    fixture = project / "fixtures" / "cfd_golden_cases.json"
    return json.loads(fixture.read_text(encoding="utf-8"))


def _empty_execution() -> ExecutionSummary:
    from .execution import EnvironmentCapability

    return ExecutionSummary(
        mode="not_started",
        status="failed",
        environment=EnvironmentCapability(mode="unknown", available=False),
        stages=[],
    )


def _overall_status(items: Sequence[ReadinessItem]) -> str:
    statuses = {item.status for item in items}
    if FAIL in statuses:
        return "not_ready"
    if RISK in statuses:
        return "ready_with_risks"
    if SKIP in statuses:
        return "ready_with_limitations"
    return "ready"


def _limitations_from_items(items: Sequence[ReadinessItem]) -> List[str]:
    limitations = [
        item.message
        for item in items
        if item.status == SKIP
    ]
    limitations.append("MVP numerical credibility is limited to simple CFD/OpenFOAM golden cases.")
    return limitations


def _risks_from_items(items: Sequence[ReadinessItem]) -> List[str]:
    risks = [item.message for item in items if item.status in {FAIL, RISK}]
    risks.append("Generated simulation evidence still requires professional engineering review before operational use.")
    return risks


def _markdown_list(items: Sequence[str]) -> str:
    if not items:
        return "- None."
    return "\n".join(f"- {item}" for item in items)


def _md_escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")
