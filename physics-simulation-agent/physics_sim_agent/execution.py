"""Execution environment detection and staged solver orchestration."""

from __future__ import annotations

import json
import re
import shlex
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


@dataclass
class EnvironmentCapability:
    """Detected execution environment."""

    mode: str
    available: bool
    openfoam_commands: Dict[str, Optional[str]] = field(default_factory=dict)
    docker_path: Optional[str] = None
    docker_image: str = "openfoam/openfoam:latest"
    version: str = ""
    limitations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "available": self.available,
            "openfoamCommands": self.openfoam_commands,
            "dockerPath": self.docker_path,
            "dockerImage": self.docker_image,
            "version": self.version,
            "limitations": list(self.limitations),
        }


@dataclass
class CommandResult:
    """Result from a command execution."""

    command: List[str]
    cwd: str
    exit_code: int
    duration_seconds: float
    stdout: str
    stderr: str
    log_path: str

    @property
    def ok(self) -> bool:
        return self.exit_code == 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "command": self.command,
            "cwd": self.cwd,
            "exitCode": self.exit_code,
            "durationSeconds": self.duration_seconds,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "logPath": self.log_path,
        }


@dataclass
class Diagnosis:
    """Human-readable failure diagnosis."""

    probable_cause: str
    recommended_action: str
    severity: str = "error"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "probableCause": self.probable_cause,
            "recommendedAction": self.recommended_action,
            "severity": self.severity,
        }


@dataclass
class StageResult:
    """Result for one execution stage."""

    name: str
    status: str
    command_result: Optional[CommandResult] = None
    parsed: Dict[str, Any] = field(default_factory=dict)
    diagnosis: Optional[Diagnosis] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "commandResult": self.command_result.to_dict() if self.command_result else None,
            "parsed": self.parsed,
            "diagnosis": self.diagnosis.to_dict() if self.diagnosis else None,
        }


@dataclass
class ExecutionSummary:
    """Overall execution output for reports and packages."""

    mode: str
    status: str
    environment: EnvironmentCapability
    stages: List[StageResult]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "status": self.status,
            "environment": self.environment.to_dict(),
            "stages": [stage.to_dict() for stage in self.stages],
        }


def detect_environment(docker_image: str = "openfoam/openfoam:latest") -> EnvironmentCapability:
    """Prefer local OpenFOAM, then Docker, otherwise report unavailable."""

    commands = {
        "blockMesh": shutil.which("blockMesh"),
        "checkMesh": shutil.which("checkMesh"),
        "simpleFoam": shutil.which("simpleFoam"),
        "pimpleFoam": shutil.which("pimpleFoam"),
        "pisoFoam": shutil.which("pisoFoam"),
        "postProcess": shutil.which("postProcess"),
    }
    has_local = bool(commands["blockMesh"] and commands["checkMesh"] and (commands["simpleFoam"] or commands["pimpleFoam"] or commands["pisoFoam"]))
    if has_local:
        return EnvironmentCapability(
            mode="local",
            available=True,
            openfoam_commands=commands,
            version=_detect_openfoam_version(commands),
        )

    docker_path = shutil.which("docker")
    if docker_path:
        return EnvironmentCapability(
            mode="docker",
            available=True,
            openfoam_commands=commands,
            docker_path=docker_path,
            docker_image=docker_image,
            limitations=["Local OpenFOAM commands were not found; Docker fallback selected."],
        )

    return EnvironmentCapability(
        mode="unavailable",
        available=False,
        openfoam_commands=commands,
        limitations=[
            "Local OpenFOAM commands were not found.",
            "Docker was not found, so Docker/OpenFOAM fallback is unavailable.",
        ],
    )


def run_command(command: Sequence[str], cwd: str | Path, log_path: str | Path, timeout_seconds: int = 600) -> CommandResult:
    """Run a command and write raw stdout/stderr to a log file."""

    start = time.time()
    completed = subprocess.run(
        list(command),
        cwd=str(cwd),
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
        check=False,
    )
    duration = time.time() - start
    log = Path(log_path)
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(
        "$ " + " ".join(command) + "\n\nSTDOUT:\n" + completed.stdout + "\nSTDERR:\n" + completed.stderr,
        encoding="utf-8",
    )
    return CommandResult(
        command=list(command),
        cwd=str(cwd),
        exit_code=completed.returncode,
        duration_seconds=duration,
        stdout=completed.stdout,
        stderr=completed.stderr,
        log_path=str(log),
    )


def execute_openfoam_case(case_dir: str | Path, mode: str = "auto") -> ExecutionSummary:
    """Execute or mock-execute an OpenFOAM case by stage."""

    case_path = Path(case_dir)
    environment = detect_environment()
    if mode == "mock":
        return _mock_execution(case_path, environment)
    if mode == "auto" and not environment.available:
        stages = [
            StageResult(
                name="environment",
                status="skipped",
                diagnosis=Diagnosis(
                    probable_cause="No local OpenFOAM or Docker/OpenFOAM environment is available.",
                    recommended_action="Install OpenFOAM locally or install Docker and configure an OpenFOAM image; mock execution remains available.",
                    severity="warning",
                ),
            )
        ]
        summary = ExecutionSummary(mode="unavailable", status="skipped", environment=environment, stages=stages)
        _write_execution_summary(case_path, summary)
        return summary

    if environment.mode == "docker":
        stages = _run_docker_openfoam(case_path, environment)
        status = "completed" if all(stage.status == "completed" for stage in stages) else "failed"
        summary = ExecutionSummary(mode="docker", status=status, environment=environment, stages=stages)
        _write_execution_summary(case_path, summary)
        return summary

    stages = _run_local_openfoam(case_path, environment)
    status = "completed" if all(stage.status == "completed" for stage in stages) else "failed"
    summary = ExecutionSummary(mode="local", status=status, environment=environment, stages=stages)
    _write_execution_summary(case_path, summary)
    return summary


def parse_check_mesh_log(text: str) -> Dict[str, Any]:
    lowered = text.lower()
    passed = "mesh ok" in lowered and "failed" not in lowered and "fatal error" not in lowered
    return {
        "passed": passed,
        "hasFatalError": "fatal error" in lowered,
        "summary": "Mesh OK" if passed else "Mesh check did not report Mesh OK.",
    }


def parse_solver_log(text: str) -> Dict[str, Any]:
    residuals = []
    for match in re.finditer(r"Solving for\s+(\w+),\s+Initial residual\s+=\s+([0-9.eE+-]+),\s+Final residual\s+=\s+([0-9.eE+-]+)", text):
        residuals.append(
            {
                "field": match.group(1),
                "initial": float(match.group(2)),
                "final": float(match.group(3)),
            }
        )
    lowered = text.lower()
    return {
        "residuals": residuals,
        "completed": "end" in lowered or "executiontime" in lowered,
        "hasFloatingPointError": "floating point" in lowered,
        "hasFatalError": "fatal error" in lowered,
        "missingFile": "cannot find file" in lowered or "no such file" in lowered,
    }


def diagnose_failure(text: str) -> Diagnosis:
    lowered = text.lower()
    if "cannot find file" in lowered or "no such file" in lowered:
        return Diagnosis("Required OpenFOAM input file is missing.", "Regenerate the case and verify 0/, constant/, and system/ files exist.")
    if "floating point" in lowered:
        return Diagnosis("The solver hit a floating point error.", "Check boundary conditions, mesh quality, and initial values.")
    if "boundary" in lowered and "not found" in lowered:
        return Diagnosis("A boundary field does not match the mesh patches.", "Regenerate fields and blockMeshDict from the same schema.")
    if "unable to find image" in lowered or "pull access denied" in lowered or "no such image" in lowered:
        return Diagnosis("The configured Docker/OpenFOAM image is not available locally.", "Pull or configure a compatible OpenFOAM Docker image, then rerun the smoke test.")
    if "docker daemon" in lowered or "cannot connect to the docker daemon" in lowered:
        return Diagnosis("Docker is installed but the Docker daemon is not reachable.", "Start Docker Desktop or the Docker daemon, then rerun the smoke test.")
    if "fatal error" in lowered:
        return Diagnosis("OpenFOAM reported a fatal error.", "Inspect the raw log and fix the referenced dictionary or mesh issue.")
    return Diagnosis("Command failed for an unclassified reason.", "Inspect the raw command log for details.")


def _run_local_openfoam(case_path: Path, environment: EnvironmentCapability) -> List[StageResult]:
    commands = [
        ("blockMesh", ["blockMesh"], parse_solverless),
        ("checkMesh", ["checkMesh"], parse_check_mesh_log),
        ("solver", [_solver_from_case(case_path)], parse_solver_log),
        ("postProcess", ["postProcess", "-func", "patchAverage(name=outlet,p)", "-latestTime"], parse_solverless),
    ]
    stages: List[StageResult] = []
    for stage_name, command, parser in commands:
        result = run_command(command, case_path, case_path / "logs" / f"{stage_name}.log")
        parsed = parser(result.stdout + "\n" + result.stderr)
        diagnosis = None if result.ok else diagnose_failure(result.stdout + "\n" + result.stderr)
        stages.append(
            StageResult(
                name=stage_name,
                status="completed" if result.ok else "failed",
                command_result=result,
                parsed=parsed,
                diagnosis=diagnosis,
            )
        )
        if not result.ok:
            break
    return stages


def _run_docker_openfoam(case_path: Path, environment: EnvironmentCapability) -> List[StageResult]:
    commands = [
        ("blockMesh", ["blockMesh"], parse_solverless),
        ("checkMesh", ["checkMesh"], parse_check_mesh_log),
        ("solver", [_solver_from_case(case_path)], parse_solver_log),
        ("postProcess", ["postProcess", "-func", "patchAverage(name=outlet,p)", "-latestTime"], parse_solverless),
    ]
    stages: List[StageResult] = []
    docker = environment.docker_path or "docker"
    volume = f"{case_path.resolve()}:/case"
    for stage_name, inner_command, parser in commands:
        command = [
            docker,
            "run",
            "--rm",
            "-v",
            volume,
            "-w",
            "/case",
            environment.docker_image,
            "bash",
            "-lc",
            " ".join(shlex.quote(part) for part in inner_command),
        ]
        result = run_command(command, case_path, case_path / "logs" / f"{stage_name}.log")
        parsed = parser(result.stdout + "\n" + result.stderr)
        diagnosis = None if result.ok else diagnose_failure(result.stdout + "\n" + result.stderr)
        stages.append(
            StageResult(
                name=stage_name,
                status="completed" if result.ok else "failed",
                command_result=result,
                parsed=parsed,
                diagnosis=diagnosis,
            )
        )
        if not result.ok:
            break
    return stages


def parse_solverless(text: str) -> Dict[str, Any]:
    return {"hasFatalError": "fatal error" in text.lower()}


def _mock_execution(case_path: Path, environment: EnvironmentCapability) -> ExecutionSummary:
    logs = case_path / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    mock_logs = {
        "blockMesh": "Creating block mesh\nEnd\n",
        "checkMesh": "Checking mesh...\nMesh OK.\nEnd\n",
        "solver": "Solving for Ux, Initial residual = 0.01, Final residual = 1e-06\nExecutionTime = 1 s\nEnd\n",
        "postProcess": "patchAverage outlet p = 0\nEnd\n",
    }
    stages: List[StageResult] = []
    for name, content in mock_logs.items():
        log_path = logs / f"{name}.log"
        log_path.write_text(content, encoding="utf-8")
        parsed = parse_check_mesh_log(content) if name == "checkMesh" else parse_solver_log(content) if name == "solver" else parse_solverless(content)
        stages.append(
            StageResult(
                name=name,
                status="completed",
                command_result=CommandResult(
                    command=["mock", name],
                    cwd=str(case_path),
                    exit_code=0,
                    duration_seconds=0.0,
                    stdout=content,
                    stderr="",
                    log_path=str(log_path),
                ),
                parsed=parsed,
            )
        )
    summary = ExecutionSummary(mode="mock", status="completed", environment=environment, stages=stages)
    _write_execution_summary(case_path, summary)
    return summary


def _solver_from_case(case_path: Path) -> str:
    control_dict = case_path / "system" / "controlDict"
    if not control_dict.exists():
        return "simpleFoam"
    match = re.search(r"application\s+(\w+)\s*;", control_dict.read_text(encoding="utf-8"))
    return match.group(1) if match else "simpleFoam"


def _write_execution_summary(case_path: Path, summary: ExecutionSummary) -> None:
    target = case_path / "logs" / "execution-summary.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(summary.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _detect_openfoam_version(commands: Mapping[str, Optional[str]]) -> str:
    solver = commands.get("simpleFoam") or commands.get("pimpleFoam") or commands.get("pisoFoam")
    if not solver:
        return ""
    try:
        completed = subprocess.run([solver, "-help"], capture_output=True, text=True, timeout=5, check=False)
    except Exception:
        return "detected"
    first_line = (completed.stdout or completed.stderr).splitlines()
    return first_line[0] if first_line else "detected"
