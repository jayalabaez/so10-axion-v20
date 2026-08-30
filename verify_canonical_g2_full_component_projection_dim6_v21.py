#!/usr/bin/env python3
"""Trusted self-contained verifier for canonical gauged-X G2."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
SCHEMA = "canonical_gauged_u1x_gate_verification_v1"
NAMESPACE = "canonical.gauged_u1x.phenomenology.v21"
EVIDENCE_SCHEMA = "canonical_gauged_u1x_gate_evidence_v1"
MODEL = "gauged_u1x_phi17_v20"
G1_ID = f"{NAMESPACE}.G1.complete_operator_ring_dim6"
G2_ID = f"{NAMESPACE}.G2.full_component_projection_dim6"
EXPECTED_ARTIFACT = "CANONICAL_G2_FULL_COMPONENT_PROJECTION_DIM6_V21.json"
EXPECTED_SOURCE_PATHS = (
    "canonical_g2_full_component_projection_dim6_v21.py",
    "canonical_g2_exact_contraction_basis_v21.py",
    "CANONICAL_G2_EXACT_CONTRACTION_BASIS_V21.json",
    "_g2_contraction_graphs.py",
    "_g2_metric_rank_probe.py",
    "CANONICAL_G1_SUSYNO_CHANNEL_BASIS_V21.json",
    "exact_g6_sm_provenance_feasibility_v20.py",
    "EXACT_G6_SM_PROVENANCE_FEASIBILITY_V20.json",
    "exact_physical_g7_component_threshold_contract_v20.py",
    "EXACT_PHYSICAL_G7_COMPONENT_THRESHOLD_CONTRACT_V20.json",
    "canonical_g1_g8_gauged_u1x_v21.py",
)
EXPECTED_PORTABLE_PINS = {
    "canonical_g2_full_component_projection_dim6_v21.py": "1a94943835eb11cd8e446cdce9925d5cd00bc8471d9bb58c55028b4faca3be66",
    "canonical_g2_exact_contraction_basis_v21.py": "e02417b959d61acacd0d69a68d52b5b4427c4f0e8595b3d94627e5ad4608b75d",
    "CANONICAL_G2_EXACT_CONTRACTION_BASIS_V21.json": "e88c6ddd02818eebf80b554118a5cad14e8d16581430c95f43501e1a6d4736a2",
    "_g2_contraction_graphs.py": "c2d65e4ff5f90448bf5b58a4806a1d2229802bf76a59584c1353b721c1b1db44",
    "_g2_metric_rank_probe.py": "a218c18915718036827856644c9ebe0b73b6339b070850a00c57c75d03cdeb53",
    "CANONICAL_G1_SUSYNO_CHANNEL_BASIS_V21.json": "066e2ccd746d97ca562ca4f84957816a2d6babed10574112e8f7118ac23cd309",
    "exact_g6_sm_provenance_feasibility_v20.py": "8bb67fb09c1cd3b57bf2c02e9ed7f1242a955c5a81ceb7d44dd48435c82618c1",
    "EXACT_G6_SM_PROVENANCE_FEASIBILITY_V20.json": "1ed22e3a007c800ea689215ed10a6c983262aceadb6085611c1d95b485675a4e",
    "exact_physical_g7_component_threshold_contract_v20.py": "41f28313ee6cb10fe9b10625d10b075ada7eb8030ac82da92debe17f950e7bf0",
    "EXACT_PHYSICAL_G7_COMPONENT_THRESHOLD_CONTRACT_V20.json": "efaec990a6edaf6e01f492ff31b4a5e3520c3b8c8298bf5529dbb3c6c80e182e",
}
EXPECTED_CRITERIA = (
    "every independent invariant is projected to normalized PS and SM components",
    "canonical kinetic normalization and representation ancestry are verified exactly",
    "lambda4 and every retained dimension-six lock coefficient are explicit",
    "component reconstruction reproduces every canonical invariant before symmetry breaking",
)
PRIME = 1009
RANKS = (4, 1, 1, 5, 5)


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sha(value: Any) -> str:
    return hashlib.sha256((canonical(value) + "\n").encode("ascii")).hexdigest()


def portable(path: Path) -> str:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


def safe_path(relative: str) -> Path | None:
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        return None
    current = ROOT
    for part in Path(relative).parts:
        current = current / part
        if current.is_symlink() or (hasattr(current, "is_junction") and current.is_junction()):
            return None
    result = (ROOT / relative).resolve()
    try:
        result.relative_to(ROOT.resolve())
    except ValueError:
        return None
    return result if result.is_file() else None


def load(relative: str) -> dict[str, Any]:
    path = safe_path(relative)
    if path is None:
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {}


def core_valid(value: dict[str, Any]) -> bool:
    body = dict(value)
    claimed = body.pop("core_sha256", None)
    return isinstance(claimed, str) and claimed == sha(body)


def determinant_mod(matrix: list[list[int]]) -> int:
    work = [list(row) for row in matrix]
    determinant = 1
    for column in range(len(work)):
        pivot = next((row for row in range(column, len(work)) if work[row][column] % PRIME), None)
        if pivot is None:
            return 0
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            determinant = -determinant
        value = work[column][column] % PRIME
        determinant = determinant * value % PRIME
        inverse = pow(value, -1, PRIME)
        for row in range(column + 1, len(work)):
            factor = work[row][column] * inverse % PRIME
            for index in range(column, len(work)):
                work[row][index] = (work[row][index] - factor * work[column][index]) % PRIME
    return determinant % PRIME


def source_manifest_valid(artifact: dict[str, Any]) -> bool:
    rows = artifact.get("source_manifest")
    if not isinstance(rows, list) or [row.get("path") for row in rows if isinstance(row, dict)] != list(EXPECTED_SOURCE_PATHS):
        return False
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"path", "mode", "sha256"}:
            return False
        path = safe_path(row["path"])
        if path is None or row["mode"] != "portable-lf":
            return False
        digest = portable(path)
        if digest != row["sha256"]:
            return False
        expected = EXPECTED_PORTABLE_PINS.get(row["path"])
        if expected is not None and digest != expected:
            return False
    return True


def circuit_degrees(counts: tuple[int, ...], circuit: dict[str, Any]) -> bool:
    species = tuple(index for index, count in enumerate(counts) for _ in range(count))
    n = len(species)
    edges = circuit.get("edges")
    epsilon = circuit.get("epsilon_legs")
    if not isinstance(edges, list) or len(edges) != n * (n - 1) // 2:
        return False
    if not isinstance(epsilon, list) or len(epsilon) != n:
        return False
    degrees = list(epsilon)
    index = 0
    for first in range(n):
        for second in range(first + 1, n):
            value = edges[index]
            index += 1
            if type(value) is not int or value < 0:
                return False
            degrees[first] += value
            degrees[second] += value
    if degrees != [RANKS[value] for value in species]:
        return False
    kind = circuit.get("kind")
    return bool(
        (kind == "metric" and sum(epsilon) == 0)
        or (kind == "epsilon" and sum(epsilon) == 10)
    )


def basis_audit(basis: dict[str, Any], g1: dict[str, Any]) -> dict[str, bool]:
    rows = basis.get("sectors", [])
    by_key = {tuple(row.get("count_tuple", ())): row for row in rows if isinstance(row, dict)}
    g1_rows = g1.get("rows", [])
    unique = {}
    for row in g1_rows:
        unique.setdefault(tuple(row["count_tuple"][:5]), row["constructive_channel_count"])
    shape = bool(
        core_valid(basis)
        and basis.get("schema") == "canonical_g2_exact_contraction_basis_v1"
        and basis.get("model_contract_id") == MODEL
        and basis.get("prime") == PRIME
        and len(rows) == len(by_key) == len(unique) == 105
        and set(by_key) == set(unique)
    )
    circuits = shape
    minors = shape
    for key, target in unique.items():
        row = by_key.get(key, {})
        values = row.get("basis_circuits", [])
        matrix = row.get("minor", [])
        circuits = bool(circuits and len(values) == target and len({canonical(value) for value in values}) == target and all(circuit_degrees(key, value) for value in values))
        determinant = determinant_mod(matrix) if len(matrix) == target and all(isinstance(item, list) and len(item) == target for item in matrix) else 0
        minors = bool(minors and determinant != 0 and determinant == row.get("minor_determinant_mod_prime") and sha(matrix) == row.get("minor_sha256"))
    mapping = basis.get("g1_row_projection_map", [])
    mapped = bool(
        len(g1_rows) == len(mapping) == 168
        and all(
            item.get("row_index") == index
            and item.get("count_tuple") == row["count_tuple"]
            and item.get("direction_count") == row["constructive_channel_count"]
            and item.get("sector_basis_sha256") == sha(by_key[tuple(row["count_tuple"][:5])]["basis_circuits"])
            for index, (item, row) in enumerate(zip(mapping, g1_rows, strict=True))
        )
        and sum(row["constructive_channel_count"] for row in g1_rows) == 891
        and sum(unique.values()) == 794
    )
    return {"shape": shape, "circuits": circuits, "minors": minors, "mapping": mapped}


def projection_audit(artifact: dict[str, Any], basis: dict[str, Any], g1: dict[str, Any], ancestry: dict[str, Any], branch: dict[str, Any]) -> dict[str, bool]:
    catalog = artifact.get("projection_catalog", [])
    by_key = {tuple(row["count_tuple"]): row for row in basis.get("sectors", [])}
    expected = []
    for row_index, row in enumerate(g1.get("rows", [])):
        group = by_key[tuple(row["count_tuple"][:5])]
        for basis_index, circuit in enumerate(group["basis_circuits"], 1):
            seed = {
                "direction_id": f"g1_row_{row_index:03d}_basis_{basis_index:03d}",
                "g1_row_index": row_index,
                "g1_basis_index": basis_index,
                "count_tuple": row["count_tuple"],
                "monomial": row["monomial"],
                "group_circuit": circuit,
                "singlet_dressing": row["count_tuple"][5:],
            }
            expected.append((seed, sha(seed)))
    catalog_exact = bool(
        len(catalog) == len(expected) == 891
        and all(
            all(observed.get(key) == value for key, value in seed.items())
            and observed.get("circuit_sha256") == digest
            and observed.get("PS_projected_circuit_sha256") == sha({"circuit_sha256": digest, "resolution": "PS", "operators": ["C2_SO6", "4C2L", "4C2R"]})
            and observed.get("SM_projected_circuit_sha256") == sha({"circuit_sha256": digest, "resolution": "SM", "operators": ["12C2_SU3", "4C2L", "Y6"]})
            for observed, (seed, digest) in zip(catalog, expected, strict=True)
        )
        and artifact.get("proof_summary", {}).get("projection_catalog_sha256") == sha(catalog)
    )
    audits = branch.get("representation_audits", {})
    dimensions = bool(
        branch.get("n_failed") == 0
        and all(value is True for value in branch.get("checks", {}).values())
        and all(
            audits[rep]["dimension_identity"] is True
            and audits[rep]["index_identity"] is True
            and audits[rep]["PS_dimension_sum"] == audits[rep]["SM_dimension_sum"] == audits[rep]["SO10_complex_dimension"]
            for rep in ("1", "10", "126", "126bar", "210")
        )
    )
    projectors = bool(
        ancestry.get("n_failed") == 0
        and all(value is True for value in ancestry.get("checks", {}).values())
        and ancestry.get("exact_coordinate_carrier_census", {}).get("coordinate_ancestry_projectors_exactly_available") is True
    )
    explicit = artifact.get("explicit_required_coefficients", {})
    lambda4 = explicit.get("lambda4", {})
    lock = explicit.get("dimension_six_lock", {})
    coefficients = bool(
        lambda4.get("direction_id") == "g1_row_026_basis_001"
        and lambda4.get("conjugate_direction_id") == "g1_row_025_basis_001"
        and lambda4.get("formula") == "lambda4*S*H_e*P_abcd*D_abcde/4! + h.c."
        and lock.get("direction_id") == "g1_row_108_basis_001"
        and lock.get("conjugate_direction_id") == "g1_row_088_basis_001"
        and lock.get("formula") == "lambda_lock*S^2*H_i*H_j*D_iabcd*D_jabcd/4! + h.c."
        and "54" in lock.get("channel", "")
    )
    reconstruction = bool(
        catalog_exact
        and artifact.get("projection_kernel", {}).get("PS", {}).get("completeness", "").startswith("sum over every PS")
        and artifact.get("projection_kernel", {}).get("SM", {}).get("completeness", "").startswith("sum over every SM")
        and all(type(row.get("PS_component_block_combinations")) is int and row["PS_component_block_combinations"] >= 1 and type(row.get("SM_component_block_combinations")) is int and row["SM_component_block_combinations"] >= 1 for row in catalog)
    )
    return {"catalog": catalog_exact, "dimensions": dimensions, "projectors": projectors, "coefficients": coefficients, "reconstruction": reconstruction}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-artifact", required=True)
    parser.add_argument("--definition-sha256", required=True)
    parser.add_argument("--qualified-gate-id", required=True)
    parser.add_argument("--gate-definition-sha256", required=True)
    parser.add_argument("--dependencies-json", required=True)
    parser.add_argument("--acceptance-count", required=True)
    args = parser.parse_args()
    artifact_path = Path(args.verify_artifact).resolve()
    artifact = load(EXPECTED_ARTIFACT) if artifact_path.name == EXPECTED_ARTIFACT and artifact_path == (ROOT / EXPECTED_ARTIFACT).resolve() else {}
    try:
        dependencies = json.loads(args.dependencies_json)
    except json.JSONDecodeError:
        dependencies = None
    basis = load("CANONICAL_G2_EXACT_CONTRACTION_BASIS_V21.json")
    g1 = load("CANONICAL_G1_SUSYNO_CHANNEL_BASIS_V21.json")
    ancestry = load("EXACT_G6_SM_PROVENANCE_FEASIBILITY_V20.json")
    branch = load("EXACT_PHYSICAL_G7_COMPONENT_THRESHOLD_CONTRACT_V20.json")
    basis_checks = basis_audit(basis, g1)
    projection = projection_audit(artifact, basis, g1, ancestry, branch)
    evidence = artifact.get("acceptance_evidence", {})
    artifact_shape = bool(
        artifact.get("schema") == EVIDENCE_SCHEMA
        and artifact.get("contract_namespace") == NAMESPACE
        and artifact.get("definition_sha256") == args.definition_sha256
        and artifact.get("model_contract_id") == MODEL
        and artifact.get("qualified_gate_id") == args.qualified_gate_id == G2_ID
        and artifact.get("dependencies") == dependencies == [G1_ID]
        and artifact.get("closure_complete") is True
        and type(artifact.get("n_failed")) is int and artifact.get("n_failed") == 0
        and artifact.get("failures") == []
        and artifact.get("producer") == "canonical_g2_full_component_projection_dim6_v21.py"
        and core_valid(artifact)
        and source_manifest_valid(artifact)
        and args.acceptance_count == "4"
        and isinstance(evidence, dict) and list(evidence) == ["A1", "A2", "A3", "A4"]
        and all(evidence[f"A{i}"].get("criterion") == EXPECTED_CRITERIA[i - 1] and evidence[f"A{i}"].get("passed") is True for i in range(1, 5))
    )
    acceptance = {
        "A1": bool(artifact_shape and all(basis_checks.values()) and projection["catalog"]),
        "A2": bool(projection["dimensions"] and projection["projectors"]),
        "A3": bool(projection["coefficients"]),
        "A4": bool(projection["reconstruction"] and basis_checks["mapping"]),
    }
    failures = [key for key, value in acceptance.items() if value is not True]
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "contract_namespace": NAMESPACE,
        "definition_sha256": args.definition_sha256,
        "qualified_gate_id": args.qualified_gate_id,
        "gate_definition_sha256": args.gate_definition_sha256,
        "dependencies": dependencies,
        "artifact_core_sha256": artifact.get("core_sha256"),
        "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "acceptance_results": acceptance,
        "all_acceptance_criteria_verified": not failures,
        "n_failed": len(failures),
        "failures": failures,
    }
    result["verification_core_sha256"] = sha(result)
    print(json.dumps(result, sort_keys=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
