"""Template-driven OpenFOAM case generation for the CFD MVP domain pack."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence

from .schema import CFDExtension, PhysicsProblemSchema
from .validation import validate_schema


@dataclass(frozen=True)
class OpenFOAMCaseManifest:
    """Generation manifest for reproducibility."""

    schema_hash: str
    domain_pack: str
    adapter: str
    solver: str
    case_family: str
    rationale: str
    assumptions: Sequence[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schemaHash": self.schema_hash,
            "domainPack": self.domain_pack,
            "adapter": self.adapter,
            "solver": self.solver,
            "caseFamily": self.case_family,
            "rationale": self.rationale,
            "assumptions": list(self.assumptions),
        }


def generate_openfoam_case(schema: PhysicsProblemSchema, workspace: str | Path) -> Path:
    """Generate an OpenFOAM case directory from a validated CFD schema."""

    validation = validate_schema(schema)
    if validation.status != "valid":
        issue_text = "; ".join(f"{issue.code}: {issue.message}" for issue in validation.issues)
        raise ValueError(f"Cannot generate OpenFOAM case from invalid schema: {issue_text}")

    extension = schema.domain_extensions.get("cfdOpenfoam")
    if isinstance(extension, Mapping):
        extension = CFDExtension.from_dict(extension)
    if not isinstance(extension, CFDExtension):
        raise ValueError("Cannot generate OpenFOAM case without cfdOpenfoam extension.")

    case_dir = Path(workspace) / "solver-input" / "openfoam-case"
    _ensure_case_dirs(case_dir)

    solver = choose_openfoam_solver(schema, extension)
    mesh = _mesh_for_case(schema, extension)
    fields = _field_values(schema)
    fluid = _fluid_properties(schema)

    _write(case_dir / "system" / "blockMeshDict", _block_mesh_dict(mesh))
    _write(case_dir / "system" / "controlDict", _control_dict(solver))
    _write(case_dir / "system" / "fvSchemes", _fv_schemes())
    _write(case_dir / "system" / "fvSolution", _fv_solution(solver))
    _write(case_dir / "constant" / "transportProperties", _transport_properties(fluid))
    _write(case_dir / "constant" / "turbulenceProperties", _turbulence_properties(extension))
    _write(case_dir / "0" / "U", _u_field(fields, mesh["boundaries"]))
    _write(case_dir / "0" / "p", _p_field(fields, mesh["boundaries"]))
    _write(case_dir / "run.sh", _run_script(solver))
    os.chmod(case_dir / "run.sh", 0o755)

    manifest = OpenFOAMCaseManifest(
        schema_hash=_schema_hash(schema),
        domain_pack="domain-pack-cfd-openfoam",
        adapter="OpenFOAMAdapter",
        solver=solver,
        case_family=extension.case_family,
        rationale=_solver_rationale(solver, extension),
        assumptions=_case_assumptions(schema, extension),
    )
    _write(
        case_dir / "generation-manifest.json",
        json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )
    schema.save(case_dir / "problem.schema.json")
    return case_dir


def choose_openfoam_solver(schema: PhysicsProblemSchema, extension: CFDExtension) -> str:
    """Map schema strategy to an MVP OpenFOAM solver."""

    requested = schema.solver_strategy.get("candidate")
    if requested:
        return str(requested)
    if extension.transient:
        return "pimpleFoam"
    if extension.turbulence_model:
        return "simpleFoam"
    return "simpleFoam"


def _ensure_case_dirs(case_dir: Path) -> None:
    for relative in ("0", "constant", "system"):
        (case_dir / relative).mkdir(parents=True, exist_ok=True)


def _schema_hash(schema: PhysicsProblemSchema) -> str:
    return hashlib.sha256(schema.to_json().encode("utf-8")).hexdigest()


def _quantity_value(data: Mapping[str, Any], key: str, default: float) -> float:
    value = data.get(key)
    if isinstance(value, Mapping):
        raw = value.get("value", default)
        try:
            return float(raw)
        except (TypeError, ValueError):
            return default
    return default


def _mesh_for_case(schema: PhysicsProblemSchema, extension: CFDExtension) -> Dict[str, Any]:
    dimensions = schema.geometry.get("dimensions", {})
    if extension.case_family == "straight_pipe":
        length = _quantity_value(dimensions, "length", 1.0)
        height = _quantity_value(dimensions, "diameter", 0.1)
        boundaries = ("inlet", "outlet", "walls", "frontAndBack")
    elif extension.case_family == "bent_pipe":
        length = _quantity_value(dimensions, "inlet_length", 1.0) + _quantity_value(dimensions, "outlet_length", 1.0)
        height = _quantity_value(dimensions, "diameter", 0.1)
        boundaries = ("inlet", "outlet", "walls", "frontAndBack")
    elif extension.case_family == "room_ventilation":
        length = _quantity_value(dimensions, "room_length", 5.0)
        height = _quantity_value(dimensions, "room_width", 3.0)
        boundaries = ("inlet", "outlet", "walls", "frontAndBack")
    else:
        length = _quantity_value(dimensions, "domain_length", 2.0)
        height = _quantity_value(dimensions, "domain_height", 1.0)
        boundaries = ("inlet", "outlet", "object", "farfield", "frontAndBack")

    return {
        "length": max(length, 1e-6),
        "height": max(height, 1e-6),
        "thickness": 0.01,
        "cells_x": 40,
        "cells_y": 12,
        "cells_z": 1,
        "boundaries": boundaries,
        "case_family": extension.case_family,
    }


def _field_values(schema: PhysicsProblemSchema) -> Dict[str, Any]:
    inlet_velocity = 1.0
    outlet_pressure = 0.0
    for boundary in schema.boundary_conditions:
        values = boundary.get("values", {})
        if boundary.get("type") == "inlet" and isinstance(values.get("velocity"), Mapping):
            inlet_velocity = float(values["velocity"].get("value", inlet_velocity))
        if boundary.get("type") == "outlet" and isinstance(values.get("pressure"), Mapping):
            outlet_pressure = float(values["pressure"].get("value", outlet_pressure))
    return {"inlet_velocity": inlet_velocity, "outlet_pressure": outlet_pressure}


def _fluid_properties(schema: PhysicsProblemSchema) -> Dict[str, float]:
    for material in schema.materials:
        if material.get("role") in {"fluid", "working_fluid"}:
            properties = material.get("properties", {})
            density = _quantity_value(properties, "density", 1.0)
            if "kinematic_viscosity" in properties:
                nu = _quantity_value(properties, "kinematic_viscosity", 1e-5)
            else:
                mu = _quantity_value(properties, "dynamic_viscosity", 1e-5)
                nu = mu / density if density else 1e-5
            return {"nu": nu}
    return {"nu": 1e-5}


def _block_mesh_dict(mesh: Mapping[str, Any]) -> str:
    length = mesh["length"]
    height = mesh["height"]
    thickness = mesh["thickness"]
    cells_x = mesh["cells_x"]
    cells_y = mesh["cells_y"]
    cells_z = mesh["cells_z"]
    boundaries = mesh["boundaries"]
    extra_object = ""
    if "object" in boundaries:
        extra_object = """
    object
    {
        type wall;
        faces ();
    }
"""
    farfield = ""
    if "farfield" in boundaries:
        farfield = """
    farfield
    {
        type patch;
        faces ((0 3 7 4));
    }
"""
    return f"""FoamFile
{{
    version 2.0;
    format ascii;
    class dictionary;
    object blockMeshDict;
}}
convertToMeters 1;

vertices
(
    (0 0 0)
    ({length} 0 0)
    ({length} {height} 0)
    (0 {height} 0)
    (0 0 {thickness})
    ({length} 0 {thickness})
    ({length} {height} {thickness})
    (0 {height} {thickness})
);

blocks
(
    hex (0 1 2 3 4 5 6 7) ({cells_x} {cells_y} {cells_z}) simpleGrading (1 1 1)
);

edges
(
);

boundary
(
    inlet
    {{
        type patch;
        faces ((0 4 7 3));
    }}
    outlet
    {{
        type patch;
        faces ((1 2 6 5));
    }}
    walls
    {{
        type wall;
        faces ((0 1 5 4) (3 7 6 2));
    }}
{extra_object}{farfield}
    frontAndBack
    {{
        type empty;
        faces ((0 3 2 1) (4 5 6 7));
    }}
);

mergePatchPairs
(
);
"""


def _control_dict(solver: str) -> str:
    return f"""FoamFile
{{
    version 2.0;
    format ascii;
    class dictionary;
    object controlDict;
}}
application {solver};
startFrom startTime;
startTime 0;
stopAt endTime;
endTime 500;
deltaT 1;
writeControl timeStep;
writeInterval 100;
purgeWrite 0;
writeFormat ascii;
writePrecision 6;
writeCompression off;
timeFormat general;
timePrecision 6;
runTimeModifiable true;
"""


def _fv_schemes() -> str:
    return """FoamFile
{
    version 2.0;
    format ascii;
    class dictionary;
    object fvSchemes;
}
ddtSchemes { default steadyState; }
gradSchemes { default Gauss linear; }
divSchemes
{
    default none;
    div(phi,U) bounded Gauss upwind;
}
laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes { default corrected; }
"""


def _fv_solution(solver: str) -> str:
    return """FoamFile
{
    version 2.0;
    format ascii;
    class dictionary;
    object fvSolution;
}
solvers
{
    p
    {
        solver GAMG;
        tolerance 1e-06;
        relTol 0.1;
        smoother GaussSeidel;
    }
    U
    {
        solver smoothSolver;
        smoother symGaussSeidel;
        tolerance 1e-05;
        relTol 0.1;
    }
}
SIMPLE
{
    nNonOrthogonalCorrectors 0;
}
relaxationFactors
{
    fields { p 0.3; }
    equations { U 0.7; }
}
"""


def _transport_properties(fluid: Mapping[str, float]) -> str:
    return f"""FoamFile
{{
    version 2.0;
    format ascii;
    class dictionary;
    object transportProperties;
}}
transportModel Newtonian;
nu [0 2 -1 0 0 0 0] {fluid["nu"]};
"""


def _turbulence_properties(extension: CFDExtension) -> str:
    if extension.turbulence_model:
        return f"""FoamFile
{{
    version 2.0;
    format ascii;
    class dictionary;
    object turbulenceProperties;
}}
simulationType RAS;
RAS
{{
    RASModel {extension.turbulence_model};
    turbulence on;
    printCoeffs on;
}}
"""
    return """FoamFile
{
    version 2.0;
    format ascii;
    class dictionary;
    object turbulenceProperties;
}
simulationType laminar;
"""


def _u_field(fields: Mapping[str, Any], boundaries: Sequence[str]) -> str:
    u = fields["inlet_velocity"]
    optional = ""
    if "object" in boundaries:
        optional += "    object { type noSlip; }\n"
    if "farfield" in boundaries:
        optional += "    farfield { type slip; }\n"
    return f"""FoamFile
{{
    version 2.0;
    format ascii;
    class volVectorField;
    object U;
}}
dimensions [0 1 -1 0 0 0 0];
internalField uniform ({u} 0 0);
boundaryField
{{
    inlet {{ type fixedValue; value uniform ({u} 0 0); }}
    outlet {{ type zeroGradient; }}
    walls {{ type noSlip; }}
{optional}    frontAndBack {{ type empty; }}
}}
"""


def _p_field(fields: Mapping[str, Any], boundaries: Sequence[str]) -> str:
    p = fields["outlet_pressure"]
    optional = ""
    if "object" in boundaries:
        optional += "    object { type zeroGradient; }\n"
    if "farfield" in boundaries:
        optional += "    farfield { type zeroGradient; }\n"
    return f"""FoamFile
{{
    version 2.0;
    format ascii;
    class volScalarField;
    object p;
}}
dimensions [0 2 -2 0 0 0 0];
internalField uniform {p};
boundaryField
{{
    inlet {{ type zeroGradient; }}
    outlet {{ type fixedValue; value uniform {p}; }}
    walls {{ type zeroGradient; }}
{optional}    frontAndBack {{ type empty; }}
}}
"""


def _run_script(solver: str) -> str:
    return f"""#!/usr/bin/env bash
set -euo pipefail

blockMesh | tee log.blockMesh
checkMesh | tee log.checkMesh
{solver} | tee log.{solver}
postProcess -func "patchAverage(name=outlet,p)" -latestTime | tee log.postProcess || true
"""


def _solver_rationale(solver: str, extension: CFDExtension) -> str:
    if extension.transient:
        return f"Selected {solver} for a simple transient incompressible CFD MVP case."
    return f"Selected {solver} for a steady incompressible CFD MVP case."


def _case_assumptions(schema: PhysicsProblemSchema, extension: CFDExtension) -> Sequence[Dict[str, Any]]:
    assumptions = [assumption.to_dict() for assumption in schema.assumptions]
    if extension.case_family in {"bent_pipe", "flow_around_object"}:
        assumptions.append(
            {
                "key": "simplified_blockmesh_geometry",
                "value": True,
                "rationale": f"{extension.case_family} uses a simplified MVP blockMesh representation.",
                "risk": "Geometry is suitable for workflow verification, not high-fidelity engineering conclusions.",
                "source": "domain-pack-cfd-openfoam",
                "approved": True,
            }
        )
    return assumptions


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
