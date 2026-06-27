"""Input intake, domain classification, and schema draft generation."""

from __future__ import annotations

import csv
import io
import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple
from xml.etree import ElementTree

from .registry import create_default_registry
from .schema import (
    Assumption,
    CFDExtension,
    PhysicsProblemSchema,
    Provenance,
    Quantity,
    ValidationIssue,
)
from .validation import validate_schema


@dataclass
class InputArtifact:
    """Normalized user input artifact."""

    kind: str
    source_ref: str
    content: str = ""
    rows: List[Dict[str, str]] = field(default_factory=list)
    confidence: Optional[float] = None
    confirmed: bool = True


@dataclass
class DomainClassification:
    """Physics domain classifier output."""

    domain: str
    confidence: float
    rationale: str
    scores: Dict[str, int]


@dataclass
class ClarificationQuestion:
    """A user-facing question derived from validation and capability state."""

    field: str
    question: str
    reason: str
    severity: str


@dataclass
class IntakeDraft:
    """Combined result of intake and schema drafting."""

    schema: PhysicsProblemSchema
    classification: DomainClassification
    clarifications: List[ClarificationQuestion]


DOMAIN_KEYWORDS: Dict[str, Sequence[str]] = {
    "multiphysics": (
        "fluid structure",
        "fluid-structure",
        "fsi",
        "thermal structural",
        "coupled",
        "多物理",
        "流固耦合",
        "热结构",
    ),
    "cfd": (
        "airflow",
        "flow",
        "fluid",
        "pipe",
        "tube",
        "inlet",
        "outlet",
        "pressure drop",
        "velocity",
        "ventilation",
        "wake",
        "cylinder",
        "流体",
        "流动",
        "空气",
        "管道",
        "弯管",
        "入口",
        "出口",
        "压降",
        "速度",
        "通风",
        "绕流",
    ),
    "heat-transfer": (
        "heat",
        "thermal",
        "temperature",
        "conduction",
        "diffusion of heat",
        "温度",
        "热传导",
        "导热",
        "传热",
    ),
    "solid-mechanics": (
        "stress",
        "strain",
        "beam",
        "plate deformation",
        "load",
        "displacement",
        "elastic",
        "结构",
        "应力",
        "应变",
        "梁",
        "变形",
        "载荷",
    ),
    "pde": (
        "poisson",
        "wave equation",
        "diffusion equation",
        "partial differential",
        "pde",
        "泊松",
        "扩散方程",
        "波动方程",
        "偏微分",
    ),
    "multibody": (
        "spring mass",
        "pendulum",
        "rigid body",
        "mechanism",
        "vehicle dynamics",
        "多体",
        "弹簧质量",
        "摆",
        "刚体",
        "机构",
    ),
}


PARAMETER_ALIASES: Dict[str, str] = {
    "length": "length",
    "pipe_length": "length",
    "l": "length",
    "diameter": "diameter",
    "pipe_diameter": "diameter",
    "d": "diameter",
    "inlet_velocity": "inlet_velocity",
    "velocity": "inlet_velocity",
    "u": "inlet_velocity",
    "outlet_pressure": "outlet_pressure",
    "pressure": "outlet_pressure",
    "density": "density",
    "rho": "density",
    "dynamic_viscosity": "dynamic_viscosity",
    "viscosity": "dynamic_viscosity",
    "mu": "dynamic_viscosity",
    "kinematic_viscosity": "kinematic_viscosity",
    "nu": "kinematic_viscosity",
    "inlet_length": "inlet_length",
    "outlet_length": "outlet_length",
    "bend_radius": "bend_radius",
    "room_length": "room_length",
    "room_width": "room_width",
    "inlet_size": "inlet_size",
    "outlet_size": "outlet_size",
    "domain_length": "domain_length",
    "domain_height": "domain_height",
    "object_diameter": "object_diameter",
    "thermal_conductivity": "thermal_conductivity",
    "k": "thermal_conductivity",
}


UNIT_CONVERSIONS: Dict[str, Tuple[str, float]] = {
    "m": ("m", 1.0),
    "meter": ("m", 1.0),
    "meters": ("m", 1.0),
    "mm": ("m", 0.001),
    "millimeter": ("m", 0.001),
    "millimeters": ("m", 0.001),
    "cm": ("m", 0.01),
    "centimeter": ("m", 0.01),
    "centimeters": ("m", 0.01),
    "m/s": ("m/s", 1.0),
    "meter/s": ("m/s", 1.0),
    "meters/s": ("m/s", 1.0),
    "pa": ("Pa", 1.0),
    "kpa": ("Pa", 1000.0),
    "mpa": ("Pa", 1_000_000.0),
    "kg/m^3": ("kg/m^3", 1.0),
    "kg/m3": ("kg/m^3", 1.0),
    "pa*s": ("Pa*s", 1.0),
    "pas": ("Pa*s", 1.0),
    "m^2/s": ("m^2/s", 1.0),
    "m2/s": ("m^2/s", 1.0),
    "w/(m*k)": ("W/(m*K)", 1.0),
    "w/m/k": ("W/(m*K)", 1.0),
}


def text_artifact(text: str, source_ref: str = "prompt") -> InputArtifact:
    return InputArtifact(kind="text", source_ref=source_ref, content=text)


def screenshot_text_artifact(
    text: str,
    source_ref: str = "screenshot",
    confidence: Optional[float] = None,
    confirmed: bool = False,
) -> InputArtifact:
    return InputArtifact(
        kind="screenshot_text",
        source_ref=source_ref,
        content=text,
        confidence=confidence,
        confirmed=confirmed,
    )


def table_text_artifact(text: str, source_ref: str = "pasted-table") -> InputArtifact:
    return InputArtifact(
        kind="table",
        source_ref=source_ref,
        content=text,
        rows=parse_table_text(text),
    )


def table_file_artifact(path: str | Path) -> InputArtifact:
    table_path = Path(path)
    suffix = table_path.suffix.lower()
    if suffix == ".csv":
        rows = parse_csv_file(table_path)
    elif suffix == ".xlsx":
        rows = parse_xlsx_file(table_path)
    else:
        raise ValueError(f"Unsupported table file type: {table_path.suffix}")
    return InputArtifact(
        kind="table",
        source_ref=str(table_path),
        rows=rows,
    )


def parse_table_text(text: str) -> List[Dict[str, str]]:
    sample = text.strip()
    if not sample:
        return []

    delimiter = _detect_delimiter(sample)
    reader = csv.DictReader(io.StringIO(sample), delimiter=delimiter)
    if reader.fieldnames and len(reader.fieldnames) > 1:
        return [
            {str(key).strip(): str(value).strip() for key, value in row.items() if key is not None}
            for row in reader
        ]

    rows: List[Dict[str, str]] = []
    for line in sample.splitlines():
        if not line.strip():
            continue
        if ":" in line:
            key, value = line.split(":", 1)
        elif "=" in line:
            key, value = line.split("=", 1)
        else:
            parts = line.split()
            if len(parts) < 2:
                continue
            key, value = parts[0], " ".join(parts[1:])
        rows.append({"parameter": key.strip(), "value": value.strip()})
    return rows


def parse_csv_file(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [
            {str(key).strip(): str(value).strip() for key, value in row.items() if key is not None}
            for row in csv.DictReader(handle)
        ]


def parse_xlsx_file(path: Path) -> List[Dict[str, str]]:
    with zipfile.ZipFile(path) as workbook:
        shared_strings = _read_shared_strings(workbook)
        sheet_name = "xl/worksheets/sheet1.xml"
        if sheet_name not in workbook.namelist():
            return []
        root = ElementTree.fromstring(workbook.read(sheet_name))

    ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    matrix: List[List[str]] = []
    for row in root.findall(".//x:sheetData/x:row", ns):
        values: List[str] = []
        for cell in row.findall("x:c", ns):
            values.append(_xlsx_cell_text(cell, shared_strings, ns))
        matrix.append(values)

    if not matrix:
        return []
    headers = [header.strip() for header in matrix[0]]
    rows: List[Dict[str, str]] = []
    for row in matrix[1:]:
        rows.append({headers[index]: row[index].strip() for index in range(min(len(headers), len(row)))})
    return rows


def classify_physics_domain(text: str) -> DomainClassification:
    lowered = text.lower()
    scores: Dict[str, int] = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        scores[domain] = sum(1 for keyword in keywords if keyword.lower() in lowered)

    domain = max(scores, key=scores.get)
    score = scores[domain]
    if score == 0:
        return DomainClassification(
            domain="unknown",
            confidence=0.0,
            rationale="No physics-domain keywords matched.",
            scores=scores,
        )

    total = sum(scores.values()) or 1
    return DomainClassification(
        domain=domain,
        confidence=score / total,
        rationale=f"Matched {score} keyword(s) for {domain}.",
        scores=scores,
    )


def build_schema_draft(artifacts: Sequence[InputArtifact]) -> IntakeDraft:
    combined_text = "\n".join(artifact.content for artifact in artifacts if artifact.content)
    classification = classify_physics_domain(combined_text)
    parameters = _extract_parameters(artifacts)
    schema = _schema_for_domain(classification, combined_text, parameters, artifacts)
    validate_schema(schema)
    clarifications = plan_clarifications(schema)
    return IntakeDraft(
        schema=schema,
        classification=classification,
        clarifications=clarifications,
    )


def plan_clarifications(schema: PhysicsProblemSchema) -> List[ClarificationQuestion]:
    validation = validate_schema(schema)
    questions = [
        ClarificationQuestion(
            field=issue.field,
            question=issue.question,
            reason=issue.message,
            severity=issue.severity,
        )
        for issue in validation.issues
        if issue.question
    ]

    selection = create_default_registry().select_adapter(schema)
    if selection.capability.status in {"draft_only", "human_review", "unsupported"}:
        questions.append(
            ClarificationQuestion(
                field="physicsDomain",
                question="This domain is not automatically executable in the MVP. Continue as a structured draft or provide a supported CFD/OpenFOAM case?",
                reason=selection.capability.rationale,
                severity=selection.capability.status,
            )
        )
    return questions


def normalize_quantity(
    raw_value: Any,
    raw_unit: Optional[str],
    provenance: Provenance,
) -> Dict[str, Any]:
    value = _parse_number(raw_value)
    unit = _clean_unit(raw_unit)
    if unit and unit.lower() in UNIT_CONVERSIONS:
        canonical_unit, factor = UNIT_CONVERSIONS[unit.lower()]
        if isinstance(value, (int, float)):
            value = value * factor
        unit = canonical_unit
    return Quantity(value=value, unit=unit, provenance=[provenance]).to_dict()


def _schema_for_domain(
    classification: DomainClassification,
    text: str,
    parameters: Mapping[str, Dict[str, Any]],
    artifacts: Sequence[InputArtifact],
) -> PhysicsProblemSchema:
    provenance = [_artifact_provenance(artifact) for artifact in artifacts]

    if classification.domain == "cfd":
        return _cfd_schema(text, parameters, provenance)

    schema = PhysicsProblemSchema(
        simulation_objective={"description": text.strip() or "Physical simulation request."},
        physics_domain=classification.domain,
        governing_model={},
        geometry={"kind": _infer_generic_geometry_kind(text), "dimensions": _geometry_dimensions(parameters)},
        materials=_generic_materials(parameters),
        provenance=provenance,
    )
    return schema


def _cfd_schema(
    text: str,
    parameters: Mapping[str, Dict[str, Any]],
    provenance: Sequence[Provenance],
) -> PhysicsProblemSchema:
    case_family = _infer_cfd_case_family(text)
    geometry_dimensions = _geometry_dimensions(parameters)
    fluid_properties: Dict[str, Any] = {}
    for key in ("density", "dynamic_viscosity", "kinematic_viscosity"):
        if key in parameters:
            fluid_properties[key] = parameters[key]

    materials: List[Dict[str, Any]] = []
    if fluid_properties:
        materials.append({"name": _infer_fluid_name(text), "role": "fluid", "properties": fluid_properties})

    boundary_conditions = _cfd_boundary_conditions(parameters)

    schema = PhysicsProblemSchema(
        simulation_objective={"description": text.strip() or "CFD simulation request."},
        physics_domain="cfd",
        governing_model={"flow": "single_phase_incompressible", "time": "steady"},
        geometry={"kind": f"2d_{case_family}", "dimensions": geometry_dimensions},
        materials=materials,
        boundary_conditions=boundary_conditions,
        mesh_strategy={"method": "blockMesh", "dimension": "2d"},
        time_strategy={"mode": "steady"},
        solver_strategy={"family": "openfoam", "candidate": "simpleFoam"},
        postprocessing_targets=_cfd_targets(text),
        provenance=list(provenance),
    )
    schema.attach_cfd_extension(CFDExtension(case_family=case_family))
    return schema


def _extract_parameters(artifacts: Sequence[InputArtifact]) -> Dict[str, Dict[str, Any]]:
    parameters: Dict[str, Dict[str, Any]] = {}
    for artifact in artifacts:
        provenance = _artifact_provenance(artifact)
        for key, raw_value, raw_unit in _parameter_triples_from_artifact(artifact):
            canonical = _canonical_parameter_name(key)
            if not canonical:
                continue
            parameters[canonical] = normalize_quantity(raw_value, raw_unit, provenance)
    return parameters


def _parameter_triples_from_artifact(artifact: InputArtifact) -> Iterable[Tuple[str, Any, Optional[str]]]:
    for row in artifact.rows:
        key = row.get("parameter") or row.get("name") or row.get("key") or row.get("field") or ""
        value = row.get("value", "")
        unit = row.get("unit")
        if not unit:
            parsed_value, parsed_unit = _split_value_unit(value)
            value = parsed_value
            unit = parsed_unit
        yield key, value, unit

    for key, value, unit in _extract_parameters_from_text(artifact.content):
        yield key, value, unit


def _extract_parameters_from_text(text: str) -> Iterable[Tuple[str, Any, Optional[str]]]:
    label_pattern = "|".join(sorted(map(re.escape, PARAMETER_ALIASES.keys()), key=len, reverse=True))
    pattern = re.compile(
        rf"\b({label_pattern})\b\s*(?:=|:|is|of)?\s*(-?\d+(?:\.\d+)?(?:e[-+]?\d+)?)\s*([A-Za-z/^\*\(\)0-9]+)?",
        re.IGNORECASE,
    )
    for match in pattern.finditer(text):
        yield match.group(1), match.group(2), match.group(3)


def _cfd_boundary_conditions(parameters: Mapping[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    boundaries: List[Dict[str, Any]] = []
    if "inlet_velocity" in parameters:
        boundaries.append({"name": "inlet", "type": "inlet", "values": {"velocity": parameters["inlet_velocity"]}})
    if "outlet_pressure" in parameters:
        boundaries.append({"name": "outlet", "type": "outlet", "values": {"pressure": parameters["outlet_pressure"]}})
    if "inlet_velocity" in parameters or "outlet_pressure" in parameters:
        boundaries.append({"name": "walls", "type": "wall", "values": {"velocity": Quantity(0.0, "m/s", []).to_dict()}})
    if any(key in parameters for key in ("object_diameter", "domain_length", "domain_height")):
        boundaries.append({"name": "object", "type": "object", "values": {"velocity": Quantity(0.0, "m/s", []).to_dict()}})
        boundaries.append({"name": "farfield", "type": "farfield", "values": {}})
    return boundaries


def _cfd_targets(text: str) -> List[Dict[str, str]]:
    lowered = text.lower()
    targets: List[Dict[str, str]] = []
    if "pressure drop" in lowered or "压降" in lowered:
        targets.append({"name": "pressure_drop"})
    if "ventilation" in lowered or "通风" in lowered:
        targets.append({"name": "low_velocity_zones"})
    if "wake" in lowered or "绕流" in lowered:
        targets.append({"name": "wake_region"})
    return targets or [{"name": "primary_flow_summary"}]


def _generic_materials(parameters: Mapping[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    properties = {
        key: value
        for key, value in parameters.items()
        if key in {"thermal_conductivity", "density", "dynamic_viscosity"}
    }
    if not properties:
        return []
    return [{"name": "material", "role": "medium", "properties": properties}]


def _geometry_dimensions(parameters: Mapping[str, Dict[str, Any]]) -> Dict[str, Any]:
    geometry_keys = {
        "length",
        "diameter",
        "inlet_length",
        "outlet_length",
        "bend_radius",
        "room_length",
        "room_width",
        "inlet_size",
        "outlet_size",
        "domain_length",
        "domain_height",
        "object_diameter",
    }
    return {key: value for key, value in parameters.items() if key in geometry_keys}


def _infer_cfd_case_family(text: str) -> str:
    lowered = text.lower()
    if any(keyword in lowered for keyword in ("bend", "elbow", "弯管")):
        return "bent_pipe"
    if any(keyword in lowered for keyword in ("ventilation", "room", "房间", "通风")):
        return "room_ventilation"
    if any(keyword in lowered for keyword in ("around", "cylinder", "obstacle", "wake", "绕流", "圆柱")):
        return "flow_around_object"
    return "straight_pipe"


def _infer_generic_geometry_kind(text: str) -> str:
    lowered = text.lower()
    if "plate" in lowered or "板" in lowered:
        return "2d_plate"
    if "beam" in lowered or "梁" in lowered:
        return "beam"
    if "pendulum" in lowered or "摆" in lowered:
        return "pendulum"
    return ""


def _infer_fluid_name(text: str) -> str:
    lowered = text.lower()
    if "water" in lowered or "水" in lowered:
        return "water"
    return "air"


def _artifact_provenance(artifact: InputArtifact) -> Provenance:
    if artifact.kind == "screenshot_text":
        return Provenance(
            source="screenshot",
            source_ref=artifact.source_ref,
            method="ocr_or_manual_extraction",
            confidence=artifact.confidence,
            confirmed=artifact.confirmed,
        )
    if artifact.kind == "table":
        return Provenance(
            source="table",
            source_ref=artifact.source_ref,
            method="table_parse",
        )
    return Provenance(source="user", source_ref=artifact.source_ref)


def _canonical_parameter_name(key: str) -> Optional[str]:
    normalized = re.sub(r"[^a-zA-Z0-9_]+", "_", key.strip().lower()).strip("_")
    return PARAMETER_ALIASES.get(normalized)


def _split_value_unit(value: Any) -> Tuple[Any, Optional[str]]:
    if not isinstance(value, str):
        return value, None
    match = re.match(r"^\s*(-?\d+(?:\.\d+)?(?:e[-+]?\d+)?)\s*([A-Za-z/^\*\(\)0-9]+)?\s*$", value, flags=re.IGNORECASE)
    if not match:
        return value, None
    return match.group(1), match.group(2)


def _parse_number(value: Any) -> Any:
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return value
    return value


def _clean_unit(unit: Optional[str]) -> Optional[str]:
    if unit is None:
        return None
    cleaned = str(unit).strip()
    return cleaned or None


def _detect_delimiter(text: str) -> str:
    first_line = text.splitlines()[0]
    if "\t" in first_line:
        return "\t"
    if "|" in first_line:
        return "|"
    return ","


def _read_shared_strings(workbook: zipfile.ZipFile) -> List[str]:
    name = "xl/sharedStrings.xml"
    if name not in workbook.namelist():
        return []
    root = ElementTree.fromstring(workbook.read(name))
    ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    return ["".join(node.itertext()) for node in root.findall(".//x:si", ns)]


def _xlsx_cell_text(cell: ElementTree.Element, shared_strings: Sequence[str], ns: Mapping[str, str]) -> str:
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        inline = cell.find("x:is", ns)
        return "".join(inline.itertext()) if inline is not None else ""
    value = cell.find("x:v", ns)
    if value is None or value.text is None:
        return ""
    if cell_type == "s":
        index = int(value.text)
        return shared_strings[index] if index < len(shared_strings) else ""
    return value.text
