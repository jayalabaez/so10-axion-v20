#!/usr/bin/env python3
"""Trusted, self-contained verifier for canonical gauged-X G1.

The canonical runner executes this file with ``python -I -B`` and raw-hash
pins it in the gate definition.  No repository module is imported here.
"""
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
EXPECTED_ARTIFACT = "CANONICAL_G1_COMPLETE_OPERATOR_RING_DIM6_V21.json"
EXPECTED_SOURCE_PATHS = (
    "canonical_g1_complete_operator_ring_dim6_v21.py",
    "canonical_g1_scalar_ring_dim6_frontier_v21.py",
    "CANONICAL_G1_SCALAR_RING_DIM6_FRONTIER_V21.json",
    "canonical_g1_susyno_channel_basis_v21.wls",
    "CANONICAL_G1_SUSYNO_CHANNEL_BASIS_V21.json",
    "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_CLOSURE_V20.json",
    "exact_x_symmetry_consistency_gate_v20.py",
    "EXACT_X_SYMMETRY_CONSISTENCY_GATE_V20.json",
    "models/EXACT_X_EXTERNAL_MODEL_VALIDATION_V20.json",
    "models/EXACT_X_EXTERNAL_INPUT_MANIFEST_V20.json",
    "models/SARAH_4_15_3_CANONICAL_SOURCE_TREE_V20.json",
    "models/SO10Z17AxionV20.m",
    "tools/validate-exact-x-model.wls",
    "canonical_g1_g8_gauged_u1x_v21.py",
)

# These are the reviewed, terminal portable-LF bytes of every non-cyclic proof
# input.  The canonical contract source is intentionally excluded from this
# table because it raw-hash-pins this verifier; its exact definition hash is
# supplied by the isolated canonical runner and checked below.
EXPECTED_PORTABLE_PINS = {
    "canonical_g1_complete_operator_ring_dim6_v21.py": "37f6343b16f231b87a4e9b4f97c7ac563fe19f5b7a196bde02dfd286b13902e9",
    "canonical_g1_scalar_ring_dim6_frontier_v21.py": "b9b48b93a2e440a2393b6e9b9c3d02a044293aecf7184834e01cf67f0df787a1",
    "CANONICAL_G1_SCALAR_RING_DIM6_FRONTIER_V21.json": "30df5a88f55d0a4d5c683e4f63a013574fdd96ebd7ccb4ed3d8a214d09d24a95",
    "canonical_g1_susyno_channel_basis_v21.wls": "3fae45e08c291ad80f916a2d851bba869c787eea0da50576177781cc9d8fe34e",
    "CANONICAL_G1_SUSYNO_CHANNEL_BASIS_V21.json": "066e2ccd746d97ca562ca4f84957816a2d6babed10574112e8f7118ac23cd309",
    "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_CLOSURE_V20.json": "c2e4692d1e1cf991265ffd5d054f9d6aa99cf1143a7e8e7d6db06284fb1c04ee",
    "exact_x_symmetry_consistency_gate_v20.py": "5c70efb039b795f94a6b03e8681ad512af837c48f4496948f918eae7faa529d8",
    "EXACT_X_SYMMETRY_CONSISTENCY_GATE_V20.json": "1bfd1e5e3ad0e2cdcbb51e39b8845eb0f18c36504592099104882ca7ce244255",
    "models/EXACT_X_EXTERNAL_MODEL_VALIDATION_V20.json": "f5108d94770b9525deff58ddd42f1ba623b54670f13b4809c3c0965217f4dc09",
    "models/EXACT_X_EXTERNAL_INPUT_MANIFEST_V20.json": "1a6c8f8d79186801c840ddb63c30ee518b73c1929642be2139a7d01ed8c41a2f",
    "models/SARAH_4_15_3_CANONICAL_SOURCE_TREE_V20.json": "c28f08d56a488050b96ce3491473f22fe1b673aad8ac3ac3d0e590dd60e70d91",
    "models/SO10Z17AxionV20.m": "66a2ce2c3491d0b3079ec93a16ab79d3e8a7e4e35cb54aadf21100b9fdd90cc1",
    "tools/validate-exact-x-model.wls": "1d1dea122de1d3465cd0af14e10574b87bf72594de69e3a888fc7bcba5d1e281",
}


def sha(value: Any) -> str:
    return hashlib.sha256(
        (
            json.dumps(
                value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
            )
            + "\n"
        ).encode("utf-8")
    ).hexdigest()


def portable(path: Path) -> str:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


def safe_path(relative: str) -> Path | None:
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        return None
    current = ROOT
    for part in Path(relative).parts:
        current = current / part
        if current.is_symlink() or (
            hasattr(current, "is_junction") and current.is_junction()
        ):
            return None
    candidate = (ROOT / relative).resolve()
    try:
        candidate.relative_to(ROOT.resolve())
    except ValueError:
        return None
    return candidate if candidate.is_file() else None


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {}


def core_valid(value: dict[str, Any]) -> bool:
    body = dict(value)
    claimed = body.pop("core_sha256", None)
    return isinstance(claimed, str) and claimed == sha(body)


def source_manifest_valid(artifact: dict[str, Any]) -> bool:
    rows = artifact.get("source_manifest")
    if not isinstance(rows, list) or [row.get("path") for row in rows if isinstance(row, dict)] != list(EXPECTED_SOURCE_PATHS):
        return False
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"path", "mode", "sha256"}:
            return False
        relative = row.get("path")
        if relative in seen:
            return False
        seen.add(relative)
        path = safe_path(relative)
        if path is None or row.get("mode") != "portable-lf":
            return False
        digest = portable(path)
        if digest != row.get("sha256"):
            return False
        expected = EXPECTED_PORTABLE_PINS.get(relative)
        if expected is not None and digest != expected:
            return False
    return seen == set(EXPECTED_SOURCE_PATHS)


def channel_audit() -> dict[str, bool | int]:
    frontier = load(ROOT / "CANONICAL_G1_SCALAR_RING_DIM6_FRONTIER_V21.json")
    channels = load(ROOT / "CANONICAL_G1_SUSYNO_CHANNEL_BASIS_V21.json")
    try:
        upper_rows = frontier["exact_character_census"]["rows"]
        lower_rows = channels["rows"]
        upper = {tuple(row["count_tuple"]): row for row in upper_rows}
        lower = {tuple(row["count_tuple"]): row for row in lower_rows}
        keys = len(upper) == len(lower) == 168 and set(upper) == set(lower)
        counts = keys and all(
            type(upper[key]["so10_singlet_multiplicity"]) is int
            and upper[key]["so10_singlet_multiplicity"]
            == lower[key]["constructive_channel_count"]
            == len(lower[key]["channels"])
            for key in upper
        )
        indices = counts and all(
            [row.get("basis_index") for row in lower[key]["channels"]]
            == list(range(1, len(lower[key]["channels"]) + 1))
            for key in upper
        )
        labels = counts and all(
            len(
                {
                    json.dumps(row, sort_keys=True, separators=(",", ":"))
                    for row in lower[key]["channels"]
                }
            )
            == len(lower[key]["channels"])
            for key in upper
        )
        conjugates = keys and all(
            tuple(row["conjugate_count_tuple"]) in lower
            and lower[tuple(row["conjugate_count_tuple"])]["constructive_channel_count"]
            == lower[key]["constructive_channel_count"]
            for key, row in upper.items()
        )
        degree = {
            d: sum(row["constructive_channel_count"] for row in lower_rows if row["degree"] == d)
            for d in range(1, 7)
        }
        total = sum(degree.values())
        return {
            "keys": keys,
            "counts": counts,
            "indices": indices,
            "labels": labels,
            "conjugates": conjugates,
            "total": total,
            "degree5": degree[5],
            "degree6": degree[6],
            "frontier": type(frontier.get("n_failed")) is int
            and frontier.get("n_failed") == 0
            and frontier.get("schema") == "canonical_g1_scalar_ring_dim6_frontier_v1",
            "channels": type(channels.get("n_failed")) is int
            and channels.get("n_failed") == 0
            and channels.get("schema") == "canonical_g1_susyno_channel_basis_v1"
            and all(value is True for value in channels.get("checks", {}).values()),
            "normalization": isinstance(channels.get("normalization_conventions"), dict)
            and len(channels["normalization_conventions"]) == 5,
        }
    except (KeyError, TypeError, ValueError):
        return {"keys": False, "counts": False, "indices": False, "labels": False,
                "conjugates": False, "total": -1, "degree5": -1, "degree6": -1,
                "frontier": False, "channels": False, "normalization": False}


def external_audit() -> bool:
    gate = load(ROOT / "EXACT_X_SYMMETRY_CONSISTENCY_GATE_V20.json")
    attestation = load(ROOT / "models" / "EXACT_X_EXTERNAL_MODEL_VALIDATION_V20.json")
    renormalizable = load(ROOT / "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_CLOSURE_V20.json")
    required = {
        "model_parse_succeeded",
        "model_initialization_succeeded",
        "lagrangian_construction_succeeded",
        "gauge_invariance_check_succeeded",
        "anomaly_check_succeeded",
    }
    try:
        execution = attestation["execution"]
        marker_checks = attestation["checks"]
        external = gate["external_model_validation"]
        return bool(
            attestation.get("schema") == "so10-exact-x-external-model-validation-v3"
            and execution.get("external_process_executed") is True
            and type(execution.get("process_exit_code")) is int
            and execution.get("process_exit_code") == 0
            and type(execution.get("runtime_probe_exit_code")) is int
            and execution.get("runtime_probe_exit_code") == 0
            and required <= set(marker_checks)
            and all(marker_checks[name] is True for name in required)
            and gate.get("contract_consistent") is True
            and external.get("valid") is True
            and external.get("schema") == "so10-exact-x-external-model-validation-v3"
            and type(renormalizable.get("n_failed")) is int
            and renormalizable.get("n_failed") == 0
            and renormalizable["closure"]["full_renormalizable_G1_mathematical_ring_closed"] is True
            and renormalizable["closure"]["normalized_component_tensor_basis_all_44_directions_closed"] is True
        )
    except (KeyError, TypeError):
        return False


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
    artifact = load(artifact_path) if artifact_path.name == EXPECTED_ARTIFACT else {}
    try:
        dependencies = json.loads(args.dependencies_json)
    except json.JSONDecodeError:
        dependencies = None
    audit = channel_audit()
    artifact_shape = bool(
        artifact.get("schema") == EVIDENCE_SCHEMA
        and artifact.get("contract_namespace") == NAMESPACE
        and artifact.get("definition_sha256") == args.definition_sha256
        and artifact.get("qualified_gate_id") == args.qualified_gate_id
        and artifact.get("dependencies") == dependencies == []
        and artifact.get("closure_complete") is True
        and type(artifact.get("n_failed")) is int
        and artifact.get("n_failed") == 0
        and artifact.get("failures") == []
        and core_valid(artifact)
        and source_manifest_valid(artifact)
        and args.acceptance_count == "4"
    )
    evidence = artifact.get("acceptance_evidence", {})
    evidence_shape = bool(
        isinstance(evidence, dict)
        and list(evidence) == ["A1", "A2", "A3", "A4"]
        and all(isinstance(evidence[key], dict) and evidence[key].get("passed") is True
                for key in ("A1", "A2", "A3", "A4"))
    )
    acceptance = {
        "A1": bool(artifact_shape and evidence_shape and audit["frontier"]
                   and audit["keys"] and audit["total"] == 891),
        "A2": bool(audit["channels"] and audit["counts"] and audit["degree5"] == 119
                   and audit["degree6"] == 721),
        "A3": bool(audit["indices"] and audit["labels"] and audit["conjugates"]
                   and audit["normalization"]),
        "A4": external_audit(),
    }
    failures = [key for key, passed in acceptance.items() if passed is not True]
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
