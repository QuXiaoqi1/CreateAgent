#!/usr/bin/env python3
"""Bridge from the gh extension shell to Physics Simulation Agent modules."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple


def _bootstrap() -> None:
    root = os.environ.get("PHYSICS_SIM_AGENT_ROOT")
    if root:
        candidate = Path(root)
    else:
        candidate = Path(__file__).resolve().parents[2] / "physics-simulation-agent"
    if not (candidate / "physics_sim_agent").is_dir():
        print(
            "error: Physics Simulation Agent core not found. Set PHYSICS_SIM_AGENT_ROOT to the core directory.",
            file=sys.stderr,
        )
        sys.exit(2)
    sys.path.insert(0, str(candidate))


_bootstrap()

from physics_sim_agent import (  # noqa: E402
    CommandResult,
    Diagnosis,
    EnvironmentCapability,
    ExecutionSummary,
    OpenFOAMAdapter,
    PhysicsProblemSchema,
    StageResult,
    build_delivery_package,
    build_schema_draft,
    build_validation_evidence,
    execute_openfoam_case,
    generate_report,
    table_file_artifact,
    text_artifact,
    validate_schema,
)


DEFAULT_WORKSPACE = ".physics-sim"


def main(argv: Sequence[str]) -> int:
    if not argv:
        return _die("missing bridge command")
    command, args = argv[0], list(argv[1:])
    try:
        if command == "draft":
            return cmd_draft(args)
        if command == "validate":
            return cmd_validate(args)
        if command == "generate":
            return cmd_generate(args)
        if command == "run":
            return cmd_run(args)
        if command == "report":
            return cmd_report(args)
        if command == "package":
            return cmd_package(args)
        return _die(f"unknown bridge command: {command}")
    except PlatformError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exc.exit_code
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def cmd_draft(args: Sequence[str]) -> int:
    workspace, _ = _workspace_from_args(args)
    task = _load_current_task(workspace)
    artifacts = [text_artifact(str(task.get("problem", "")))]
    artifacts.extend(_table_artifacts(workspace))

    draft = build_schema_draft(artifacts)
    schema_path = workspace / "schema" / "problem.schema.json"
    draft.schema.save(schema_path)
    _write_json(
        workspace / "schema" / "clarifications.json",
        {
            "classification": {
                "domain": draft.classification.domain,
                "confidence": draft.classification.confidence,
                "rationale": draft.classification.rationale,
            },
            "questions": [
                {
                    "field": question.field,
                    "question": question.question,
                    "reason": question.reason,
                    "severity": question.severity,
                }
                for question in draft.clarifications
            ],
        },
    )
    _update_task(workspace, stage="schema_drafted")
    print(f"Drafted Physics Problem Schema: {schema_path}")
    print(f"Validation status: {draft.schema.validation.status}")
    if draft.clarifications:
        print("Clarifications:")
        for question in draft.clarifications:
            print(f"- {question.field}: {question.question}")
    return 0


def cmd_validate(args: Sequence[str]) -> int:
    workspace, _ = _workspace_from_args(args)
    schema = _load_schema(workspace)
    result = validate_schema(schema)
    schema.save(_schema_path(workspace))
    _write_json(workspace / "state" / "validation.json", result.to_dict())
    _update_task(workspace, stage="validated" if result.status == "valid" else result.status)
    if result.status == "valid":
        print("Validation passed.")
        return 0
    print(f"Validation status: {result.status}")
    for issue in result.issues:
        print(f"- {issue.severity}: {issue.code} - {issue.message}")
        if issue.question:
            print(f"  question: {issue.question}")
    return 1 if result.blockers else 0


def cmd_generate(args: Sequence[str]) -> int:
    workspace, _ = _workspace_from_args(args)
    schema = _load_schema(workspace)
    result = validate_schema(schema)
    if not result.can_generate_solver_input:
        return _print_validation_block(result)
    case_dir = OpenFOAMAdapter().generate_solver_input(schema, workspace)
    _update_task(workspace, stage="solver_input_generated")
    print(f"Generated OpenFOAM solver input: {case_dir}")
    return 0


def cmd_run(args: Sequence[str]) -> int:
    workspace, remaining = _workspace_from_args(args)
    mode = _flag_value(remaining, "--mode")
    task = _load_current_task(workspace)
    if mode is None:
        mode = str(task.get("mode", "mock") or "mock")
    if mode not in {"mock", "auto"}:
        raise PlatformError("--mode must be mock or auto")

    case_dir = _case_dir(workspace)
    if not case_dir.exists():
        raise PlatformError("solver input not found; run generate first")
    summary = execute_openfoam_case(case_dir, mode=mode)
    _update_task(workspace, stage="run_completed" if summary.status == "completed" else summary.status)
    print(f"Execution status: {summary.status}")
    print(f"Execution mode: {summary.mode}")
    print(f"Logs: {case_dir / 'logs'}")
    return 0 if summary.status in {"completed", "skipped"} else 1


def cmd_report(args: Sequence[str]) -> int:
    workspace, _ = _workspace_from_args(args)
    schema = _load_schema(workspace)
    execution = _load_execution_summary(workspace)
    evidence = build_validation_evidence(schema, _case_dir(workspace), execution)
    report = generate_report(schema, evidence, execution)
    report_path = workspace / "reports" / "report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    _write_json(workspace / "reports" / "validation-evidence.json", evidence.to_dict())
    _update_task(workspace, stage="report_generated")
    print(f"Generated report: {report_path}")
    return 0


def cmd_package(args: Sequence[str]) -> int:
    workspace, _ = _workspace_from_args(args)
    schema = _load_schema(workspace)
    execution = _load_execution_summary(workspace)
    task = _load_current_task(workspace)
    package_dir = build_delivery_package(
        schema,
        _case_dir(workspace),
        execution,
        workspace / "package",
        user_text=str(task.get("problem", "")),
    )
    _update_task(workspace, stage="package_ready")
    print(f"Generated delivery package: {package_dir}")
    return 0


class PlatformError(Exception):
    def __init__(self, message: str, exit_code: int = 1) -> None:
        super().__init__(message)
        self.exit_code = exit_code


def _workspace_from_args(args: Sequence[str]) -> Tuple[Path, List[str]]:
    workspace = DEFAULT_WORKSPACE
    remaining: List[str] = []
    index = 0
    while index < len(args):
        arg = args[index]
        if arg == "--workspace":
            index += 1
            if index >= len(args):
                raise PlatformError("--workspace requires a value")
            workspace = args[index]
        else:
            remaining.append(arg)
        index += 1
    workspace_path = Path(workspace)
    if not workspace_path.is_dir():
        raise PlatformError(f"workspace not found: {workspace_path}")
    return workspace_path, remaining


def _flag_value(args: Sequence[str], flag: str) -> str | None:
    index = 0
    while index < len(args):
        if args[index] == flag:
            if index + 1 >= len(args):
                raise PlatformError(f"{flag} requires a value")
            return args[index + 1]
        index += 1
    return None


def _load_current_task(workspace: Path) -> Dict[str, Any]:
    current = workspace / "state" / "current_task"
    if not current.exists():
        raise PlatformError("no current task; run new first")
    task_id = current.read_text(encoding="utf-8").strip()
    task_path = workspace / "tasks" / task_id / "task.json"
    if not task_path.exists():
        raise PlatformError(f"task file missing: {task_path}")
    return json.loads(task_path.read_text(encoding="utf-8"))


def _update_task(workspace: Path, stage: str) -> None:
    current = workspace / "state" / "current_task"
    task_id = current.read_text(encoding="utf-8").strip()
    task_path = workspace / "tasks" / task_id / "task.json"
    task = json.loads(task_path.read_text(encoding="utf-8"))
    task["stage"] = stage
    task_path.write_text(json.dumps(task, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (workspace / "state" / "last_stage").write_text(stage + "\n", encoding="utf-8")


def _table_artifacts(workspace: Path) -> Iterable[Any]:
    inputs = workspace / "inputs"
    if not inputs.exists():
        return []
    artifacts = []
    for path in sorted(inputs.iterdir()):
        if path.suffix.lower() in {".csv", ".xlsx"}:
            artifacts.append(table_file_artifact(path))
    return artifacts


def _schema_path(workspace: Path) -> Path:
    return workspace / "schema" / "problem.schema.json"


def _load_schema(workspace: Path) -> PhysicsProblemSchema:
    path = _schema_path(workspace)
    if not path.exists():
        raise PlatformError("schema not found; run draft first")
    return PhysicsProblemSchema.load(path)


def _case_dir(workspace: Path) -> Path:
    return workspace / "solver-input" / "openfoam-case"


def _load_execution_summary(workspace: Path) -> ExecutionSummary:
    path = _case_dir(workspace) / "logs" / "execution-summary.json"
    if not path.exists():
        raise PlatformError("execution summary not found; run first")
    return _execution_summary_from_dict(json.loads(path.read_text(encoding="utf-8")))


def _execution_summary_from_dict(data: Dict[str, Any]) -> ExecutionSummary:
    env_data = data.get("environment", {})
    environment = EnvironmentCapability(
        mode=str(env_data.get("mode", "")),
        available=bool(env_data.get("available", False)),
        openfoam_commands=dict(env_data.get("openfoamCommands", {})),
        docker_path=env_data.get("dockerPath"),
        docker_image=str(env_data.get("dockerImage", "openfoam/openfoam:latest")),
        version=str(env_data.get("version", "")),
        limitations=list(env_data.get("limitations", [])),
    )
    stages = [_stage_from_dict(item) for item in data.get("stages", [])]
    return ExecutionSummary(
        mode=str(data.get("mode", "")),
        status=str(data.get("status", "")),
        environment=environment,
        stages=stages,
    )


def _stage_from_dict(data: Dict[str, Any]) -> StageResult:
    command_data = data.get("commandResult")
    command = None
    if command_data:
        command = CommandResult(
            command=list(command_data.get("command", [])),
            cwd=str(command_data.get("cwd", "")),
            exit_code=int(command_data.get("exitCode", 1)),
            duration_seconds=float(command_data.get("durationSeconds", 0.0)),
            stdout=str(command_data.get("stdout", "")),
            stderr=str(command_data.get("stderr", "")),
            log_path=str(command_data.get("logPath", "")),
        )

    diagnosis_data = data.get("diagnosis")
    diagnosis = None
    if diagnosis_data:
        diagnosis = Diagnosis(
            probable_cause=str(diagnosis_data.get("probableCause", "")),
            recommended_action=str(diagnosis_data.get("recommendedAction", "")),
            severity=str(diagnosis_data.get("severity", "error")),
        )

    return StageResult(
        name=str(data.get("name", "")),
        status=str(data.get("status", "")),
        command_result=command,
        parsed=dict(data.get("parsed", {})),
        diagnosis=diagnosis,
    )


def _write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _print_validation_block(result: Any) -> int:
    print(f"Cannot generate solver input; validation status: {result.status}", file=sys.stderr)
    for issue in result.issues:
        print(f"- {issue.code}: {issue.message}", file=sys.stderr)
    return 1


def _die(message: str) -> int:
    print(f"error: {message}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
