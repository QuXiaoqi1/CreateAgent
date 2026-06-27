"""Local workspace, task state, artifact, and checkpoint primitives."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field as dataclass_field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Sequence


WORKSPACE_DIRS = (
    "inputs",
    "state",
    "schema",
    "solver-input",
    "logs",
    "results",
    "reports",
    "package",
    "tasks",
)

WORKFLOW_STAGES = (
    "created",
    "input_registered",
    "schema_drafted",
    "validated",
    "solver_selected",
    "solver_input_generated",
    "run_completed",
    "report_generated",
    "package_ready",
)


@dataclass
class ArtifactRecord:
    id: str
    kind: str
    path: str
    stage: str
    source: str = ""
    metadata: Dict[str, Any] = dataclass_field(default_factory=dict)
    created_at: str = dataclass_field(default_factory=lambda: _now())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArtifactRecord":
        return cls(
            id=str(data.get("id", "")),
            kind=str(data.get("kind", "")),
            path=str(data.get("path", "")),
            stage=str(data.get("stage", "")),
            source=str(data.get("source", "")),
            metadata=dict(data.get("metadata", {})),
            created_at=str(data.get("createdAt", data.get("created_at", _now()))),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "path": self.path,
            "stage": self.stage,
            "source": self.source,
            "metadata": self.metadata,
            "createdAt": self.created_at,
        }


@dataclass
class CheckpointDecision:
    id: str
    kind: str
    question: str
    status: str = "pending"
    field: str = ""
    answer: Any = None
    risk: str = ""
    created_at: str = dataclass_field(default_factory=lambda: _now())
    resolved_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CheckpointDecision":
        return cls(
            id=str(data.get("id", "")),
            kind=str(data.get("kind", "")),
            question=str(data.get("question", "")),
            status=str(data.get("status", "pending")),
            field=str(data.get("field", "")),
            answer=data.get("answer"),
            risk=str(data.get("risk", "")),
            created_at=str(data.get("createdAt", data.get("created_at", _now()))),
            resolved_at=str(data.get("resolvedAt", data.get("resolved_at", ""))),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "question": self.question,
            "status": self.status,
            "field": self.field,
            "answer": self.answer,
            "risk": self.risk,
            "createdAt": self.created_at,
            "resolvedAt": self.resolved_at,
        }


@dataclass
class TaskState:
    id: str
    title: str
    language: str = ""
    physics_domain: str = ""
    domain_pack: str = ""
    stage: str = "created"
    mode: str = "mock"
    artifacts: List[ArtifactRecord] = dataclass_field(default_factory=list)
    checkpoints: List[CheckpointDecision] = dataclass_field(default_factory=list)
    errors: List[Dict[str, Any]] = dataclass_field(default_factory=list)
    created_at: str = dataclass_field(default_factory=lambda: _now())
    updated_at: str = dataclass_field(default_factory=lambda: _now())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskState":
        return cls(
            id=str(data.get("id", "")),
            title=str(data.get("title", data.get("problem", ""))),
            language=str(data.get("language", "")),
            physics_domain=str(data.get("physicsDomain", data.get("physics_domain", ""))),
            domain_pack=str(data.get("domainPack", data.get("domain_pack", ""))),
            stage=str(data.get("stage", "created")),
            mode=str(data.get("mode", "mock")),
            artifacts=[ArtifactRecord.from_dict(item) for item in data.get("artifacts", [])],
            checkpoints=[CheckpointDecision.from_dict(item) for item in data.get("checkpoints", [])],
            errors=list(data.get("errors", [])),
            created_at=str(data.get("createdAt", data.get("created_at", _now()))),
            updated_at=str(data.get("updatedAt", data.get("updated_at", _now()))),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "problem": self.title,
            "language": self.language,
            "physicsDomain": self.physics_domain,
            "domainPack": self.domain_pack,
            "stage": self.stage,
            "mode": self.mode,
            "artifacts": [artifact.to_dict() for artifact in self.artifacts],
            "checkpoints": [checkpoint.to_dict() for checkpoint in self.checkpoints],
            "errors": list(self.errors),
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }


@dataclass
class WorkflowStep:
    name: str
    inputs: Sequence[str]
    outputs: Sequence[str]
    checkpoint: bool = False


DEFAULT_WORKFLOW = (
    WorkflowStep("intake", ("text", "table", "screenshot"), ("schema_draft",), True),
    WorkflowStep("validate", ("schema_draft",), ("validation",), True),
    WorkflowStep("generate", ("validated_schema",), ("solver_input",), False),
    WorkflowStep("execute", ("solver_input",), ("logs", "results"), False),
    WorkflowStep("deliver", ("schema", "logs", "results"), ("report", "package"), False),
)


class PlatformWorkspace:
    """Filesystem-backed local task workspace."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    def initialize(self) -> Path:
        for directory in WORKSPACE_DIRS:
            (self.root / directory).mkdir(parents=True, exist_ok=True)
        self._write_json(
            self.root / "state" / "workspace.json",
            {
                "version": "0.1.0",
                "workspace": str(self.root),
                "directories": list(WORKSPACE_DIRS),
                "workflowStages": list(WORKFLOW_STAGES),
            },
        )
        return self.root

    def create_task(
        self,
        task_id: str,
        title: str,
        language: str = "",
        mode: str = "mock",
    ) -> TaskState:
        self.initialize()
        task = TaskState(id=task_id, title=title, language=language, mode=mode)
        self.save_task(task)
        (self.root / "state" / "current_task").write_text(task_id + "\n", encoding="utf-8")
        return task

    def current_task_id(self) -> str:
        path = self.root / "state" / "current_task"
        if not path.exists():
            raise FileNotFoundError("No current task is recorded.")
        return path.read_text(encoding="utf-8").strip()

    def load_task(self, task_id: str | None = None) -> TaskState:
        selected = task_id or self.current_task_id()
        path = self._task_path(selected)
        return TaskState.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def save_task(self, task: TaskState) -> None:
        task.updated_at = _now()
        path = self._task_path(task.id)
        self._write_json(path, task.to_dict())

    def set_stage(self, stage: str, task_id: str | None = None) -> TaskState:
        if stage not in WORKFLOW_STAGES:
            raise ValueError(f"Unknown workflow stage: {stage}")
        task = self.load_task(task_id)
        task.stage = stage
        self.save_task(task)
        (self.root / "state" / "last_stage").write_text(stage + "\n", encoding="utf-8")
        return task

    def attach_input(self, source_path: str | Path, kind: str, task_id: str | None = None) -> ArtifactRecord:
        self.initialize()
        source = Path(source_path)
        if not source.is_file():
            raise FileNotFoundError(str(source))
        target = self._unique_input_path(source.name)
        shutil.copy2(source, target)
        return self.register_artifact(kind=kind, path=target, stage="input_registered", source=str(source), task_id=task_id)

    def register_artifact(
        self,
        kind: str,
        path: str | Path,
        stage: str,
        source: str = "",
        metadata: Dict[str, Any] | None = None,
        task_id: str | None = None,
    ) -> ArtifactRecord:
        task = self.load_task(task_id)
        relative = self._display_path(path)
        artifact = ArtifactRecord(
            id=f"artifact-{len(task.artifacts) + 1}",
            kind=kind,
            path=relative,
            stage=stage,
            source=source,
            metadata=metadata or {},
        )
        task.artifacts.append(artifact)
        task.stage = stage
        self.save_task(task)
        return artifact

    def add_checkpoint(
        self,
        kind: str,
        question: str,
        field: str = "",
        risk: str = "",
        task_id: str | None = None,
    ) -> CheckpointDecision:
        task = self.load_task(task_id)
        checkpoint = CheckpointDecision(
            id=f"checkpoint-{len(task.checkpoints) + 1}",
            kind=kind,
            question=question,
            field=field,
            risk=risk,
        )
        task.checkpoints.append(checkpoint)
        self.save_task(task)
        return checkpoint

    def resolve_checkpoint(
        self,
        checkpoint_id: str,
        answer: Any,
        status: str = "approved",
        task_id: str | None = None,
    ) -> CheckpointDecision:
        task = self.load_task(task_id)
        for checkpoint in task.checkpoints:
            if checkpoint.id == checkpoint_id:
                checkpoint.answer = answer
                checkpoint.status = status
                checkpoint.resolved_at = _now()
                self.save_task(task)
                return checkpoint
        raise KeyError(checkpoint_id)

    def record_error(self, stage: str, message: str, task_id: str | None = None) -> TaskState:
        task = self.load_task(task_id)
        task.errors.append({"stage": stage, "message": message, "createdAt": _now()})
        task.stage = stage
        self.save_task(task)
        return task

    def _task_path(self, task_id: str) -> Path:
        return self.root / "tasks" / task_id / "task.json"

    def _unique_input_path(self, filename: str) -> Path:
        base = self.root / "inputs" / filename
        if not base.exists():
            return base
        stem = base.stem
        suffix = base.suffix
        counter = 2
        while True:
            candidate = base.with_name(f"{stem}-{counter}{suffix}")
            if not candidate.exists():
                return candidate
            counter += 1

    def _display_path(self, path: str | Path) -> str:
        candidate = Path(path)
        try:
            return str(candidate.relative_to(self.root))
        except ValueError:
            return str(candidate)

    @staticmethod
    def _write_json(path: Path, data: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
