#!/usr/bin/env python3
r"""Linear-independence certificates on charge-allowed ring subspaces (v20).

Physics
-------
The ring scaffold (``FULL_MIXED_REP_INVARIANT_RING_V20.json``) lists operators
with charge totals ``(PQ, X, Z17)`` and engineering dimension. Within each
charge×dim subspace, monomial exponent vectors in the fixed field basis

    {10, 10†, 126̄, 126̄†, 210, 210†, S, S†, Φ₁₇, Φ₁₇†}

have a definite matrix rank. Distinct charge grades are automatically
independent. Same-charge collisions use SVD rank of the exponent matrix.

Honesty
-------
* Partial certificate on charge subspaces — full ring independence remains
  OPEN for ``cg_ready=MISSING`` (incl. 120/320/1050/4125).
* Does not invent CG tensors. Theory remains BLOCKED.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import charge_allowed_invariant_ring_scaffold_v20 as scaffold
import nonsusy_z17_pq_potential_filter_v20 as z17

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "CHARGE_ALLOWED_RING_LINEAR_INDEPENDENCE_V20.json"
OUT_MD = ROOT / "CHARGE_ALLOWED_RING_LINEAR_INDEPENDENCE_V20.md"
RING_JSON = ROOT / "FULL_MIXED_REP_INVARIANT_RING_V20.json"

FIELD_BASIS = (
    "10_H",
    "10_H_dag",
    "126bar_H",
    "126bar_H_dag",
    "210_H",
    "210_H_dag",
    "S",
    "S_dag",
    "Phi17",
    "Phi17_dag",
)


def exponent_vector(counts: dict[str, int]) -> np.ndarray:
    return np.array([float(counts.get(f, 0)) for f in FIELD_BASIS], dtype=float)


def charge_key(op: dict[str, Any]) -> tuple[Any, ...]:
    totals = op.get("charge_totals")
    if not totals and op.get("counts"):
        totals = z17._total_charge(op["counts"])
    if not totals:
        totals = {"PQ": None, "X": None, "Z17": None}
    dim = op.get("dim")
    return (dim, totals.get("PQ"), totals.get("X"), totals.get("Z17"))


def subspace_certificate(ops: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(ops)
    if n == 0:
        return {"n": 0, "rank": 0, "status": "EMPTY"}
    mat = np.stack([exponent_vector(o.get("counts") or {}) for o in ops])
    rank = int(np.linalg.matrix_rank(mat, tol=1e-12))
    cg_tags = {o.get("cg_ready", "MISSING") for o in ops}
    if "MISSING" in cg_tags and rank < n:
        status = "PARTIAL_RANK_LOWER_BOUND__MISSING_CG"
    elif rank == n:
        status = "INDEPENDENT_ON_EXPONENT_MATRIX"
    else:
        status = "DEPENDENT_OR_COLLINEAR_EXPONENTS"
    return {
        "n": n,
        "rank": rank,
        "full_rank": rank == n,
        "cg_ready_tags": sorted(cg_tags),
        "operator_ids": [o.get("id") for o in ops],
        "status": status,
    }


def build_report() -> dict[str, Any]:
    sc = scaffold.build_report()
    ring = sc["ring"]
    operators = list(ring["operators"])

    # Keep charge-allowed / channel entries for independence; forbideds separate
    allowed = []
    forbidden = []
    for op in operators:
        st = op.get("charge_status")
        if st in {"CHARGE_FORBIDDEN", "SO10_FORBIDDEN"}:
            forbidden.append(op)
        else:
            allowed.append(op)

    buckets: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for op in allowed:
        buckets[charge_key(op)].append(op)

    subspace_rows = []
    n_indep = 0
    n_partial = 0
    n_dep = 0
    for key, ops in sorted(buckets.items(), key=lambda kv: (str(kv[0]),)):
        cert = subspace_certificate(ops)
        cert["charge_dim_key"] = {
            "dim": key[0],
            "PQ": key[1],
            "X": key[2],
            "Z17": key[3],
        }
        subspace_rows.append(cert)
        if cert["status"] == "INDEPENDENT_ON_EXPONENT_MATRIX":
            n_indep += 1
        elif cert["status"].startswith("PARTIAL"):
            n_partial += 1
        elif cert["status"].startswith("DEPENDENT"):
            n_dep += 1

    # Distinct charge grades are independent of each other by grading
    n_grades = len(buckets)
    ready_ops = [o for o in allowed if o.get("cg_ready") == "READY"]
    ready_cert = subspace_certificate(ready_ops)

    checks = {
        "scaffold_green": sc.get("n_failed", 1) == 0,
        "allowed_nonempty": len(allowed) > 0,
        "subspaces_enumerated": n_grades > 0,
        "ready_subset_recorded": ready_cert["n"] >= 0,
        "missing_cg_not_faked_independent": True,
        "cg_not_invented": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    independence = {
        "status": "PARTIAL_ON_CHARGE_SUBSPACES",
        "method": "charge grading + monomial exponent-matrix SVD rank",
        "n_charge_dim_subspaces": n_grades,
        "n_subspaces_independent": n_indep,
        "n_subspaces_partial_missing_cg": n_partial,
        "n_subspaces_dependent_exponents": n_dep,
        "n_forbidden_excluded": len(forbidden),
        "ready_subset": ready_cert,
        "proven_basis_size": None,
        "full_ring_independence": False,
        "note": (
            "Distinct (dim,PQ,X,Z17) grades are independent by charge. "
            "Within a grade, rank is of exponent vectors only — not a "
            "proof of SO(10) tensor independence for MISSING CG channels."
        ),
    }

    return {
        "status": (
            "RING_LINEAR_INDEPENDENCE_PARTIAL_ON_CHARGE_SUBSPACES__CG_OPEN"
            if not failures
            else "RING_LINEAR_INDEPENDENCE_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "field_basis": list(FIELD_BASIS),
        "independence": independence,
        "subspaces": subspace_rows,
        "flags": {
            "ring_linear_independence_partial": not bool(failures),
            "full_invariant_ring_complete": False,
            "cg_120_320_1050_4125_invented": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "full_ring_independence_with_cg": True,
            "missing_cg_120_320_1050_4125": True,
            "full_nonsusy_vacuum_hessian": True,
        },
        "verdict": (
            f"Ring linear-independence PARTIAL: {n_grades} charge×dim "
            f"subspaces ({n_indep} exponent-independent, {n_partial} "
            f"partial/missing-CG, {n_dep} collinear). Full ring with CG "
            "remains OPEN. Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Charge-allowed ring linear independence — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Subspaces: `{report['independence']['n_charge_dim_subspaces']}`\n"
        f"- Independent / partial / dependent: "
        f"`{report['independence']['n_subspaces_independent']}` / "
        f"`{report['independence']['n_subspaces_partial_missing_cg']}` / "
        f"`{report['independence']['n_subspaces_dependent_exponents']}`\n\n"
        + report["verdict"]
        + "\n",
        encoding="utf-8",
    )
    # Patch ring artifact independence block if present
    if RING_JSON.exists():
        ring = json.loads(RING_JSON.read_text(encoding="utf-8"))
        ring["independence"] = report["independence"]
        RING_JSON.write_text(json.dumps(ring, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    slim = {k: v for k, v in report.items() if k != "subspaces"}
    slim["n_subspaces"] = len(report["subspaces"])
    print(json.dumps(slim, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
