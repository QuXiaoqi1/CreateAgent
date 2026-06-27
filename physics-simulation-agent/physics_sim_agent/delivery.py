"""Validation evidence, report generation, and delivery packaging."""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Sequence

from .execution import ExecutionSummary
from .schema import PhysicsProblemSchema
from .validation import validate_schema


@dataclass
class SanityCheck:
    name: str
    status: str
    message: str

    def to_dict(self) -> Dict[str, str]:
        return {"name": self.name, "status": self.status, "message": self.message}


@dataclass
class ValidationEvidence:
    runnable_status: str
    convergence_status: str
    mesh_status: str
    confidence: str
    sanity_checks: List[SanityCheck] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "runnableStatus": self.runnable_status,
            "convergenceStatus": self.convergence_status,
            "meshStatus": self.mesh_status,
            "confidence": self.confidence,
            "sanityChecks": [check.to_dict() for check in self.sanity_checks],
            "metrics": self.metrics,
            "warnings": list(self.warnings),
        }


def build_validation_evidence(
    schema: PhysicsProblemSchema,
    case_dir: str | Path,
    execution: ExecutionSummary,
) -> ValidationEvidence:
    validation = validate_schema(schema)
    mesh_status = "not_run"
    convergence_status = "not_run"
    warnings: List[str] = []

    for stage in execution.stages:
        if stage.name == "checkMesh":
            mesh_status = "passed" if stage.parsed.get("passed") else "failed"
        if stage.name == "solver":
            if stage.status != "completed" or stage.parsed.get("hasFatalError"):
                convergence_status = "failed"
            elif stage.parsed.get("completed"):
                residuals = stage.parsed.get("residuals", [])
                if residuals:
                    convergence_status = "residuals_recorded"
                else:
                    convergence_status = "completed_without_residuals"

    if execution.status == "skipped":
        warnings.append("Execution was skipped because no compatible runtime was available or enabled.")
    if validation.status != "valid":
        warnings.append(f"Schema validation status is {validation.status}.")

    checks = [
        SanityCheck(
            name="schema_valid",
            status="pass" if validation.status == "valid" else "fail",
            message="Schema passed validation." if validation.status == "valid" else "Schema has validation issues.",
        ),
        SanityCheck(
            name="mesh_check",
            status="pass" if mesh_status == "passed" else "warning",
            message=f"Mesh status: {mesh_status}.",
        ),
        SanityCheck(
            name="execution_completed",
            status="pass" if execution.status == "completed" else "warning",
            message=f"Execution status: {execution.status}.",
        ),
    ]

    confidence = "workflow_verified"
    if execution.status != "completed" or mesh_status != "passed":
        confidence = "limited"

    return ValidationEvidence(
        runnable_status=execution.status,
        convergence_status=convergence_status,
        mesh_status=mesh_status,
        confidence=confidence,
        sanity_checks=checks,
        metrics=extract_openfoam_metrics(schema, case_dir, execution),
        warnings=warnings,
    )


def extract_openfoam_metrics(
    schema: PhysicsProblemSchema,
    case_dir: str | Path,
    execution: ExecutionSummary,
) -> Dict[str, Any]:
    extension = schema.domain_extensions.get("cfdOpenfoam")
    case_family = getattr(extension, "case_family", "unknown")
    metrics: Dict[str, Any] = {"caseFamily": case_family}

    solver_stage = next((stage for stage in execution.stages if stage.name == "solver"), None)
    if solver_stage:
        metrics["residualCount"] = len(solver_stage.parsed.get("residuals", []))
        metrics["solverCompleted"] = solver_stage.parsed.get("completed", False)

    post_log = Path(case_dir) / "logs" / "postProcess.log"
    if post_log.exists():
        text = post_log.read_text(encoding="utf-8")
        numbers = [float(item) for item in re.findall(r"[-+]?\d+(?:\.\d+)?(?:e[-+]?\d+)?", text)]
        if numbers:
            metrics["postProcessNumericSamples"] = numbers[-5:]

    if case_family == "straight_pipe":
        metrics["primaryMetric"] = "pressure_drop"
    elif case_family == "bent_pipe":
        metrics["primaryMetric"] = "bend_loss_indicator"
    elif case_family == "room_ventilation":
        metrics["primaryMetric"] = "low_velocity_zone_summary"
    elif case_family == "flow_around_object":
        metrics["primaryMetric"] = "wake_region_summary"
    else:
        metrics["primaryMetric"] = "simulation_summary"
    return metrics


def select_report_languages(user_text: str) -> List[str]:
    if re.search(r"[\u4e00-\u9fff]", user_text):
        return ["zh", "en"]
    return ["zh", "en"]


def generate_report(
    schema: PhysicsProblemSchema,
    evidence: ValidationEvidence,
    execution: ExecutionSummary,
    languages: Sequence[str] | None = None,
) -> str:
    languages = list(languages or ["zh", "en"])
    sections: List[str] = []
    objective = schema.simulation_objective.get("description", "Simulation request")

    if "zh" in languages:
        sections.append(
            f"""# 物理模拟分析报告

## 问题摘要

{objective}

## 运行状态

- 可运行状态：{evidence.runnable_status}
- 网格检查：{evidence.mesh_status}
- 收敛/日志状态：{evidence.convergence_status}
- 可信度：{evidence.confidence}

## 关键指标

```json
{json.dumps(evidence.metrics, ensure_ascii=False, indent=2, sort_keys=True)}
```

## Sanity Check

{_checks_markdown(evidence.sanity_checks)}

## 假设与限制

{_assumptions_markdown(schema)}

本报告区分“流程可运行”和“工程结论可信”。当前结果只能作为 MVP 工作流证据，不能替代专业工程审查。
"""
        )

    if "en" in languages:
        sections.append(
            f"""# Physics Simulation Analysis Report

## Problem Summary

{objective}

## Run Status

- Runnable status: {evidence.runnable_status}
- Mesh status: {evidence.mesh_status}
- Convergence/log status: {evidence.convergence_status}
- Confidence: {evidence.confidence}

## Key Metrics

```json
{json.dumps(evidence.metrics, ensure_ascii=False, indent=2, sort_keys=True)}
```

## Sanity Checks

{_checks_markdown(evidence.sanity_checks)}

## Assumptions And Limitations

{_assumptions_markdown(schema)}

This report separates "runnable workflow" from "trusted engineering conclusion". The current result is MVP workflow evidence and does not replace expert engineering review.
"""
        )

    sections.append(
        f"""## Reproduction

1. Open the delivery package.
2. Inspect `problem.schema.json`, `solver-input/openfoam-case`, and `logs/`.
3. In a compatible OpenFOAM environment, run `solver-input/openfoam-case/run.sh`.

Execution mode used for this package: `{execution.mode}`.
"""
    )
    return "\n\n".join(sections)


def build_delivery_package(
    schema: PhysicsProblemSchema,
    case_dir: str | Path,
    execution: ExecutionSummary,
    package_dir: str | Path,
    user_text: str = "",
) -> Path:
    case_path = Path(case_dir)
    package_path = Path(package_dir)
    if package_path.exists():
        shutil.rmtree(package_path)
    package_path.mkdir(parents=True)

    evidence = build_validation_evidence(schema, case_path, execution)
    languages = select_report_languages(user_text or schema.simulation_objective.get("description", ""))
    report = generate_report(schema, evidence, execution, languages)

    schema.save(package_path / "problem.schema.json")
    _write_assumptions(schema, package_path / "assumptions.md")
    (package_path / "report.md").write_text(report, encoding="utf-8")
    (package_path / "validation-evidence.json").write_text(
        json.dumps(evidence.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (package_path / "metadata.json").write_text(
        json.dumps(
            {
                "platform": "Physics Simulation Agent",
                "domainPack": "domain-pack-cfd-openfoam",
                "execution": execution.to_dict(),
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (package_path / "README.md").write_text(_readme_text(evidence), encoding="utf-8")

    solver_target = package_path / "solver-input" / "openfoam-case"
    shutil.copytree(case_path, solver_target)

    logs_target = package_path / "logs"
    logs_target.mkdir(exist_ok=True)
    if (case_path / "logs").exists():
        for log in (case_path / "logs").iterdir():
            if log.is_file():
                shutil.copy2(log, logs_target / log.name)

    (package_path / "results").mkdir(exist_ok=True)
    return package_path


def _checks_markdown(checks: Sequence[SanityCheck]) -> str:
    return "\n".join(f"- {check.name}: {check.status} - {check.message}" for check in checks)


def _assumptions_markdown(schema: PhysicsProblemSchema) -> str:
    if not schema.assumptions:
        return "- No explicit user-approved assumptions were recorded."
    return "\n".join(
        f"- {assumption.key}: {assumption.value} | approved={assumption.approved} | risk={assumption.risk}"
        for assumption in schema.assumptions
    )


def _write_assumptions(schema: PhysicsProblemSchema, path: Path) -> None:
    path.write_text("# Assumptions\n\n" + _assumptions_markdown(schema) + "\n", encoding="utf-8")


def _readme_text(evidence: ValidationEvidence) -> str:
    return f"""# Physics Simulation Delivery Package

Runnable status: {evidence.runnable_status}
Mesh status: {evidence.mesh_status}
Convergence/log status: {evidence.convergence_status}

Contents:

- `problem.schema.json`
- `assumptions.md`
- `solver-input/openfoam-case/`
- `logs/`
- `results/`
- `report.md`
- `metadata.json`
- `validation-evidence.json`
"""
