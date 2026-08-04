#!/usr/bin/env python3
"""Machine-checkable closure contract for the remaining v20 theory gaps.

This module does not pretend that missing SO(10) Clebsch tensors, a complete
mixed-representation invariant ring, or a unique proton lifetime can be
recovered from reduced proxies.  It defines the exact artifacts and acceptance
conditions required to close each gap and fails closed until those artifacts
exist and pass their validators.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "IRREDUCIBLE_GAP_CLOSURE_CONTRACT_V20.json"
OUT_MD = ROOT / "IRREDUCIBLE_GAP_CLOSURE_CONTRACT_V20.md"

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
        "depends_on": ["G2_full_tensor_projection", "G3_global_vacuum_and_component_hessian"],
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
        "depends_on": ["G3_global_vacuum_and_component_hessian", "G4_viable_odd_H_or_hierarchy_mechanism"],
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
        "depends_on": ["G2_full_tensor_projection", "G3_global_vacuum_and_component_hessian"],
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
        "depends_on": ["G2_full_tensor_projection", "G3_global_vacuum_and_component_hessian"],
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


def _artifact_state(gap: dict[str, Any]) -> dict[str, Any]:
    path = ROOT / gap["required_artifact"]
    if not path.exists():
        return {"exists": False, "closed": False, "reason": "required artifact absent"}
    try:
        data = json.loads(path.read_text())
    except Exception as exc:
        return {"exists": True, "closed": False, "reason": f"invalid JSON: {exc}"}
    closed = bool(data.get("closure_complete")) and int(data.get("n_failed", 1)) == 0
    return {
        "exists": True,
        "closed": closed,
        "reason": "accepted" if closed else "artifact present but closure flags fail",
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
        rows.append({**gap, "artifact_state": state, "dependencies_closed": dependencies_closed, "closed": closed})

    n_closed = sum(int(row["closed"]) for row in rows)
    return {
        "status": "IRREDUCIBLE_GAP_CLOSURE_CONTRACT_EVALUATED",
        "overall_state": "PASS" if n_closed == len(rows) else "BLOCKED",
        "n_gaps": len(rows),
        "n_closed": n_closed,
        "n_open": len(rows) - n_closed,
        "n_failed": 0,
        "gaps": rows,
        "flags": {
            "dependency_order_enforced": True,
            "proxy_substitution_forbidden": True,
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
        "",
    ]
    for row in report["gaps"]:
        mark = "CLOSED" if row["closed"] else "OPEN"
        lines.extend([
            f"## {row['id']} — {mark}",
            f"Required artifact: `{row['required_artifact']}`",
            f"Producer: {row['producer']}",
            f"Proxy forbidden: {row['proxy_forbidden']}",
            "",
        ])
    OUT_MD.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    report = build_report()
    write_report(report)
    print(json.dumps(report, indent=2, sort_keys=True))
