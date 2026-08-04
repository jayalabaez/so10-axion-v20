#!/usr/bin/env python3
"""Machine-checkable closure contract for the remaining v20 theory gaps.

Missing SO(10) Clebsch tensors, a complete mixed-representation invariant ring,
or a unique proton lifetime cannot be recovered from reduced proxies. This
contract defines the exact artifacts and evidence required to close each gap
and rejects bare ``closure_complete`` flags without provenance.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "IRREDUCIBLE_GAP_CLOSURE_CONTRACT_V20.json"
OUT_MD = ROOT / "IRREDUCIBLE_GAP_CLOSURE_CONTRACT_V20.md"
CONTRACT_SCHEMA_VERSION = 1

GAPS: tuple[dict[str, Any], ...] = (
    {
        "id": "G1_complete_invariant_ring",
        "depends_on": [],
        "required_artifact": "FULL_MIXED_REP_INVARIANT_RING_V20.json",
        "producer": "exact SO(10) tensor-contraction or Molien/Haar calculation",
        "acceptance": [
            "all charge-neutral operators through engineering dimension six enumerated",
            "linear independence proved with exact arithmetic",
            "upper bound equals constructive lower bound in every field-content sector",
            "normalization and Hermitian-conjugation conventions recorded",
        ],
        "proxy_forbidden": "signed floor34 is a lower bound, not a complete ring",
    },
    {
        "id": "G2_full_tensor_projection",
        "depends_on": ["G1_complete_invariant_ring"],
        "required_artifact": "FULL_TENSOR_PROJECTED_POTENTIAL_V20.json",
        "producer": "component projection of every independent invariant",
        "acceptance": [
            "all PS and SM component Clebsch coefficients emitted",
            "canonical kinetic normalization verified",
            "lambda4 and dimension-six lock coefficients explicitly encoded",
            "reconstruction reproduces every invariant before symmetry breaking",
        ],
        "proxy_forbidden": "radial amplitudes and imported SUSY matrices cannot substitute",
    },
    {
        "id": "G3_global_vacuum_and_component_hessian",
        "depends_on": ["G2_full_tensor_projection"],
        "required_artifact": "FULL_NONSUSY_VACUUM_HESSIAN_V20.json",
        "producer": "exact stationarity plus global competing-extrema search",
        "acceptance": [
            "physical-EW vacuum stationary to declared precision",
            "exactly 33 gauge Goldstones after gauge projection",
            "all remaining component eigenvalues positive",
            "target vacuum below every enumerated competing extremum",
            "boundedness certificate applies to the complete potential",
        ],
        "proxy_forbidden": "positive reduced radial Hessian is insufficient",
    },
    {
        "id": "G4_viable_odd_H_or_hierarchy_mechanism",
        "depends_on": [
            "G2_full_tensor_projection",
            "G3_global_vacuum_and_component_hessian",
        ],
        "required_artifact": "EW_HIERARCHY_MECHANISM_V20.json",
        "producer": "explicit technically stable mechanism on the physical-EW branch",
        "acceptance": [
            "h=174 GeV obtained without the excluded historical lambda4 point",
            "all required dimensionless couplings remain perturbative",
            "radiative stability or symmetry protection demonstrated",
            "no new tachyon or deeper unwanted vacuum introduced",
        ],
        "proxy_forbidden": "fine-tuned cancellation without stability proof is not closure",
    },
    {
        "id": "G5_calG_lock_revalidation",
        "depends_on": [
            "G3_global_vacuum_and_component_hessian",
            "G4_viable_odd_H_or_hierarchy_mechanism",
        ],
        "required_artifact": "CAL_G_LOCK_PHYSICAL_EW_REVALIDATION_V20.json",
        "producer": "full phase/component Hessian on surviving physical-EW branch",
        "acceptance": [
            "cal-G mode lifted above declared tolerance",
            "axion direction remains the only intended light phase direction",
            "selected vacuum and scalar spectrum remain positive",
            "result uses live lambda-lock component tensors",
        ],
        "proxy_forbidden": "intermediate-scale H10 proxy is invalid",
    },
    {
        "id": "G6_full_tensor_two_loop_RGE_thresholds",
        "depends_on": [
            "G2_full_tensor_projection",
            "G3_global_vacuum_and_component_hessian",
        ],
        "required_artifact": "FULL_TWO_LOOP_RGE_THRESHOLD_CHAIN_V20.json",
        "producer": "live SARAH/PyR@TE or independently derived two-loop tensor system",
        "acceptance": [
            "complete tensor-valued scalar, Yukawa, gauge and soft beta functions included",
            "SO10-to-PS and PS-to-SM matching uses physical component masses",
            "scheme and normalization conventions declared",
            "independent one-loop limit and numerical reproducibility checks pass",
        ],
        "proxy_forbidden": "reduced one-loop delta-contracted dump is not complete",
    },
    {
        "id": "G7_physical_triplet_and_threshold_spectrum",
        "depends_on": [
            "G2_full_tensor_projection",
            "G3_global_vacuum_and_component_hessian",
        ],
        "required_artifact": "PHYSICAL_TRIPLET_THRESHOLD_SPECTRUM_V20.json",
        "producer": "dimensionally correct component mass-squared matrices",
        "acceptance": [
            "forbidden 210*10dag*10 and 10*126bar*S contributions absent",
            "allowed lambda4 off-diagonal CG entries explicit",
            "all physical masses are square roots of positive mass-squared eigenvalues",
            "threshold multiplicities and SM quantum numbers complete",
        ],
        "proxy_forbidden": "legacy dimension-one scalar triplet matrices are invalid",
    },
    {
        "id": "G8_exact_unique_proton_lifetime",
        "depends_on": [
            "G5_calG_lock_revalidation",
            "G6_full_tensor_two_loop_RGE_thresholds",
            "G7_physical_triplet_and_threshold_spectrum",
        ],
        "required_artifact": "EXACT_UNIQUE_PROTON_LIFETIME_V20.json",
        "producer": "complete gauge plus scalar amplitude with fixed flavour solution",
        "acceptance": [
            "all gauge and scalar mediators included with physical masses",
            "Wilson coefficients matched and run with declared scheme",
            "flavour/Clebsch solution unique or uncertainty distribution propagated",
            "interference phases fixed by the same physical vacuum",
            "all reported channels compared with current experimental limits",
        ],
        "proxy_forbidden": "a selected conditional benchmark is not a unique prediction",
    },
)


def _evidence_passes(item: Any) -> bool:
    return bool(
        isinstance(item, dict)
        and item.get("passed") is True
        and isinstance(item.get("artifacts"), list)
        and item["artifacts"]
        and all(isinstance(path, str) and path.strip() for path in item["artifacts"])
    )


def _artifact_state(gap: dict[str, Any]) -> dict[str, Any]:
    path = ROOT / gap["required_artifact"]
    if not path.exists():
        return {
            "exists": False,
            "closed": False,
            "reason": "required artifact absent",
            "validation_errors": [],
        }

    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    try:
        data = json.loads(raw)
    except Exception as exc:
        return {
            "exists": True,
            "closed": False,
            "reason": f"invalid JSON: {exc}",
            "sha256": digest,
            "validation_errors": ["invalid_json"],
        }

    errors: list[str] = []
    if data.get("schema_version") != CONTRACT_SCHEMA_VERSION:
        errors.append("schema_version_mismatch")
    if data.get("gap_id") != gap["id"]:
        errors.append("gap_id_mismatch")
    if data.get("closure_complete") is not True:
        errors.append("closure_complete_not_true")
    try:
        if int(data.get("n_failed", 1)) != 0:
            errors.append("n_failed_nonzero")
    except (TypeError, ValueError):
        errors.append("n_failed_invalid")
    if not isinstance(data.get("producer"), str) or not data["producer"].strip():
        errors.append("producer_missing")
    if not isinstance(data.get("source_manifest"), list) or not data["source_manifest"]:
        errors.append("source_manifest_missing")
    if not data.get("normalization_conventions"):
        errors.append("normalization_conventions_missing")

    declared_dependencies = data.get("dependencies")
    if not isinstance(declared_dependencies, list) or set(declared_dependencies) != set(
        gap["depends_on"]
    ):
        errors.append("dependency_manifest_mismatch")

    evidence = data.get("acceptance_evidence")
    if not isinstance(evidence, dict):
        errors.append("acceptance_evidence_missing")
    else:
        for index, criterion in enumerate(gap["acceptance"], start=1):
            key = f"A{index}"
            item = evidence.get(key)
            if not _evidence_passes(item):
                errors.append(f"{key}_evidence_invalid")
            elif item.get("criterion") != criterion:
                errors.append(f"{key}_criterion_mismatch")

    closed = not errors
    return {
        "exists": True,
        "closed": closed,
        "reason": "accepted" if closed else "artifact schema/evidence validation failed",
        "sha256": digest,
        "validation_errors": errors,
    }


def build_report() -> dict[str, Any]:
    rows = []
    closed_ids: set[str] = set()
    for gap in GAPS:
        state = _artifact_state(gap)
        dependencies_closed = all(dep in closed_ids for dep in gap["depends_on"])
        closed = bool(state["closed"] and dependencies_closed)
        if closed:
            closed_ids.add(gap["id"])
        rows.append(
            {
                **gap,
                "required_schema": {
                    "schema_version": CONTRACT_SCHEMA_VERSION,
                    "gap_id": gap["id"],
                    "dependencies": gap["depends_on"],
                    "acceptance_evidence_keys": [
                        f"A{index}"
                        for index in range(1, len(gap["acceptance"]) + 1)
                    ],
                },
                "artifact_state": state,
                "dependencies_closed": dependencies_closed,
                "closed": closed,
            }
        )

    n_closed = sum(int(row["closed"]) for row in rows)
    return {
        "status": "IRREDUCIBLE_GAP_CLOSURE_CONTRACT_EVALUATED",
        "overall_state": "PASS" if n_closed == len(rows) else "BLOCKED",
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "n_gaps": len(rows),
        "n_closed": n_closed,
        "n_open": len(rows) - n_closed,
        "n_failed": 0,
        "gaps": rows,
        "flags": {
            "dependency_order_enforced": True,
            "proxy_substitution_forbidden": True,
            "artifact_schema_and_acceptance_evidence_enforced": True,
            "artifact_sha256_recorded": True,
            "all_required_artifacts_machine_named": True,
            "whole_model_validated": n_closed == len(rows),
            "whole_model_excluded": False,
        },
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Irreducible Gap Closure Contract v20",
        "",
        f"Overall state: **{report['overall_state']}**",
        f"Closed: {report['n_closed']} / {report['n_gaps']}",
        f"Artifact schema: v{report['schema_version']}",
        "",
    ]
    for row in report["gaps"]:
        mark = "CLOSED" if row["closed"] else "OPEN"
        lines.extend(
            [
                f"## {row['id']} — {mark}",
                f"Required artifact: `{row['required_artifact']}`",
                f"Producer: {row['producer']}",
                f"Proxy forbidden: {row['proxy_forbidden']}",
                f"Artifact reason: {row['artifact_state']['reason']}",
                "",
            ]
        )
    OUT_MD.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    report = build_report()
    write_report(report)
    print(json.dumps(report, indent=2, sort_keys=True))
