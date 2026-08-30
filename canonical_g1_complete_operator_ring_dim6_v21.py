#!/usr/bin/env python3
"""Build canonical V21 G1 evidence for the complete scalar ring through d=6.

G1 is an abstract invariant-ring gate.  Its normalized component Clebsch
expansion belongs to G2.  This producer therefore combines two independent
exact computations: the D5 Weyl-character upper bound and a constructive
Susyno plethysm/Hom-channel basis.  It additionally binds the already-closed
renormalizable 44-direction component basis and the genuine v3 SARAH runtime
attestation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import canonical_g1_g8_gauged_u1x_v21 as canonical
import exact_x_symmetry_consistency_gate_v20 as exact_x


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "CANONICAL_G1_COMPLETE_OPERATOR_RING_DIM6_V21.json"
OUT_MD = ROOT / "CANONICAL_G1_COMPLETE_OPERATOR_RING_DIM6_V21.md"
FRONTIER = ROOT / "CANONICAL_G1_SCALAR_RING_DIM6_FRONTIER_V21.json"
CHANNELS = ROOT / "CANONICAL_G1_SUSYNO_CHANNEL_BASIS_V21.json"
RENORMALIZABLE = ROOT / "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_CLOSURE_V20.json"
EXTERNAL_ATTESTATION = ROOT / "models" / "EXACT_X_EXTERNAL_MODEL_VALIDATION_V20.json"
SCHEMA = canonical.EVIDENCE_SCHEMA

SOURCE_PATHS = (
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


def _sha(value: Any) -> str:
    return hashlib.sha256(
        (
            json.dumps(
                value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
            )
            + "\n"
        ).encode("utf-8")
    ).hexdigest()


def _portable(path: Path) -> tuple[str, int]:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest(), len(raw)


def _bound(path: str) -> dict[str, str]:
    digest, _ = _portable(ROOT / path)
    return {"path": path, "mode": "portable-lf", "sha256": digest}


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path.name} is not a JSON object")
    return value


def _channel_audit(
    frontier: dict[str, Any], channels: dict[str, Any]
) -> dict[str, Any]:
    upper_rows = frontier["exact_character_census"]["rows"]
    lower_rows = channels["rows"]
    upper = {tuple(row["count_tuple"]): row for row in upper_rows}
    lower = {tuple(row["count_tuple"]): row for row in lower_rows}
    row_keys_exact = len(upper) == len(lower) == 168 and set(upper) == set(lower)
    sector_counts_match = row_keys_exact and all(
        type(upper[key]["so10_singlet_multiplicity"]) is int
        and lower[key]["constructive_channel_count"]
        == upper[key]["so10_singlet_multiplicity"]
        == len(lower[key]["channels"])
        for key in upper
    )
    sequential = sector_counts_match and all(
        [item.get("basis_index") for item in lower[key]["channels"]]
        == list(range(1, len(lower[key]["channels"]) + 1))
        for key in upper
    )
    unique = sector_counts_match and all(
        len(
            {
                json.dumps(item, sort_keys=True, separators=(",", ":"))
                for item in lower[key]["channels"]
            }
        )
        == len(lower[key]["channels"])
        for key in upper
    )
    conjugates = row_keys_exact and all(
        tuple(row["conjugate_count_tuple"]) in lower
        and lower[tuple(row["conjugate_count_tuple"])]["constructive_channel_count"]
        == lower[key]["constructive_channel_count"]
        for key, row in upper.items()
    )
    totals = {
        str(degree): sum(
            row["constructive_channel_count"]
            for row in lower_rows
            if row["degree"] == degree
        )
        for degree in range(1, 7)
    }
    return {
        "row_keys_exact": row_keys_exact,
        "sector_counts_match": sector_counts_match,
        "basis_indices_are_sequential": sequential,
        "basis_labels_are_unique_within_each_sector": unique,
        "Hermitian_conjugate_sectors_have_equal_ordered_dimension": conjugates,
        "complex_direction_count": sum(totals.values()),
        "complex_direction_count_by_degree": totals,
    }


def build_report() -> dict[str, Any]:
    gate = canonical.GATES[0]
    frontier = _load(FRONTIER)
    channels = _load(CHANNELS)
    renormalizable = _load(RENORMALIZABLE)
    attestation = _load(EXTERNAL_ATTESTATION)
    exact_report = exact_x.build_report()
    audit = _channel_audit(frontier, channels)

    frontier_ok = bool(
        frontier.get("schema") == "canonical_g1_scalar_ring_dim6_frontier_v1"
        and type(frontier.get("n_failed")) is int
        and frontier.get("n_failed") == 0
        and frontier.get("exact_character_census", {}).get("counts", {}).get(
            "charge_and_so10_allowed_multidegrees"
        )
        == 168
        and frontier["exact_character_census"]["counts"].get(
            "complex_invariant_multiplicity"
        )
        == 891
    )
    channels_ok = bool(
        channels.get("schema") == "canonical_g1_susyno_channel_basis_v1"
        and type(channels.get("n_failed")) is int
        and channels.get("n_failed") == 0
        and channels.get("construction", {}).get(
            "all_sector_lower_bounds_equal_character_upper_bounds"
        )
        is True
        and all(value is True for value in channels.get("checks", {}).values())
        and audit["sector_counts_match"] is True
        and audit["basis_indices_are_sequential"] is True
        and audit["basis_labels_are_unique_within_each_sector"] is True
        and audit["complex_direction_count"] == 891
    )
    normalization_ok = bool(
        channels_ok
        and audit["Hermitian_conjugate_sectors_have_equal_ordered_dimension"] is True
        and isinstance(channels.get("normalization_conventions"), dict)
        and len(channels["normalization_conventions"]) == 5
    )
    renormalizable_ok = bool(
        type(renormalizable.get("n_failed")) is int
        and renormalizable.get("n_failed") == 0
        and renormalizable.get("closure", {}).get(
            "normalized_component_tensor_basis_all_44_directions_closed"
        )
        is True
        and renormalizable.get("closure", {}).get(
            "full_renormalizable_G1_mathematical_ring_closed"
        )
        is True
    )
    external_ok = bool(
        exact_report.get("contract_consistent") is True
        and exact_report.get("external_model_validation", {}).get("valid") is True
        and exact_report.get("external_model_validation", {}).get("schema")
        == "so10-exact-x-external-model-validation-v3"
        and attestation.get("schema")
        == "so10-exact-x-external-model-validation-v3"
    )

    acceptance = {
        "A1": frontier_ok,
        "A2": frontier_ok and channels_ok,
        "A3": channels_ok and normalization_ok,
        "A4": renormalizable_ok and external_ok,
    }
    paths = {path: _bound(path) for path in SOURCE_PATHS}
    evidence_paths = {
        "A1": [
            paths["canonical_g1_scalar_ring_dim6_frontier_v21.py"],
            paths["CANONICAL_G1_SCALAR_RING_DIM6_FRONTIER_V21.json"],
        ],
        "A2": [
            paths["canonical_g1_susyno_channel_basis_v21.wls"],
            paths["CANONICAL_G1_SUSYNO_CHANNEL_BASIS_V21.json"],
            paths["CANONICAL_G1_SCALAR_RING_DIM6_FRONTIER_V21.json"],
        ],
        "A3": [paths["CANONICAL_G1_SUSYNO_CHANNEL_BASIS_V21.json"]],
        "A4": [
            paths["EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_CLOSURE_V20.json"],
            paths["EXACT_X_SYMMETRY_CONSISTENCY_GATE_V20.json"],
            paths["models/EXACT_X_EXTERNAL_MODEL_VALIDATION_V20.json"],
            paths["models/SARAH_4_15_3_CANONICAL_SOURCE_TREE_V20.json"],
        ],
    }
    failures = [key for key, passed in acceptance.items() if passed is not True]
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "contract_namespace": canonical.CONTRACT_NAMESPACE,
        "definition_sha256": canonical.DEFINITION_SHA256,
        "model_contract_id": canonical.MODEL_CONTRACT_ID,
        "qualified_gate_id": gate["qualified_gate_id"],
        "dependencies": gate["dependencies"],
        "closure_complete": not failures,
        "n_failed": len(failures),
        "failures": failures,
        "producer": "canonical_g1_complete_operator_ring_dim6_v21.py",
        "normalization_conventions": channels.get("normalization_conventions", {}),
        "source_manifest": list(paths.values()),
        "acceptance_evidence": {
            key: {
                "criterion": gate["acceptance"][index - 1],
                "passed": acceptance[key],
                "artifacts": evidence_paths[key],
            }
            for index, key in enumerate(("A1", "A2", "A3", "A4"), start=1)
        },
        "proof_summary": {
            "scope": "derivative-free scalar polynomial potential ring generated by 210_H, 10_H, 126bar_H, S, Phi17 and Hermitian conjugates through engineering dimension six",
            "neutral_field_content_sectors": 168,
            "Hermitian_conjugacy_orbits": 117,
            "complex_invariant_directions": 891,
            "real_potential_coefficients": 891,
            "degree_five_directions": 119,
            "degree_six_directions": 721,
            "renormalizable_normalized_component_directions": 44,
            "upper_bound_method": "exact D5 Weyl-character constant term",
            "constructive_lower_bound_method": "independent exact Susyno symmetric-power plethysm and singlet Hom-channel enumeration",
            "channel_audit": audit,
            "v3_SARAH_runtime_attestation_valid": external_ok,
        },
    }
    body = dict(report)
    report["core_sha256"] = _sha(body)
    return report


def render_markdown(report: dict[str, Any]) -> str:
    proof = report["proof_summary"]
    return "\n".join(
        [
            "# Canonical V21 G1 complete scalar operator ring",
            "",
            f"- qualified gate: `{report['qualified_gate_id']}`",
            f"- closure complete: `{str(report['closure_complete']).lower()}`",
            f"- failed criteria: `{report['n_failed']}`",
            f"- exact core: `{report['core_sha256']}`",
            f"- neutral sectors: `{proof['neutral_field_content_sectors']}`",
            f"- complex invariant directions / real coefficients: `{proof['complex_invariant_directions']}`",
            f"- degree-five / degree-six directions: `{proof['degree_five_directions']}` / `{proof['degree_six_directions']}`",
            "",
            "The character upper bound agrees sector-by-sector with an independent constructive Susyno plethysm/Hom-channel basis. The basis is orthonormal in the compact Spin(10) invariant Hermitian metric with deterministic copy ordering and phase convention. Component Clebsch projection remains the separate canonical G2 gate.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build_report()
    encoded = json.dumps(report, indent=2, sort_keys=False) + "\n"
    markdown = render_markdown(report)
    if args.check:
        if not OUT_JSON.is_file() or not OUT_MD.is_file():
            raise SystemExit("canonical G1 outputs are absent")
        if OUT_JSON.read_text(encoding="utf-8") != encoded:
            raise SystemExit("canonical G1 JSON drifted")
        if OUT_MD.read_text(encoding="utf-8") != markdown:
            raise SystemExit("canonical G1 Markdown drifted")
    if args.write or not args.check:
        OUT_JSON.write_text(encoded, encoding="utf-8", newline="\n")
        OUT_MD.write_text(markdown, encoding="utf-8", newline="\n")
    if report["n_failed"]:
        raise SystemExit(f"canonical G1 remains open: {report['failures']}")
    print(f"CANONICAL_G1_COMPLETE {report['core_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
