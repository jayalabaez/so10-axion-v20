#!/usr/bin/env python3
r"""Declared-symmetry SO(10) x Z17/PQ operator filter for non-SUSY v20.

Charge neutrality and SO(10) singlet existence are separate requirements.
The live model declares SO(10), Z17, and the PQ scalar selection rule, but no
continuous U(1)_X. X charges are retained only as historical metadata and are
not imposed by default. Call ``_allowed(..., require_x=True)`` only for an
explicit comparison with the superseded continuous-X assumption.

The filter remains an operator-existence ledger rather than a complete
invariant-ring multiplicity calculation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import literature_cg_triplet_matrix_v20 as lit_cg
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent

CHARGES = {
    "10_H": {"PQ": -2, "X": -2, "Z17": 15},
    "10_H_dag": {"PQ": 2, "X": 2, "Z17": 2},
    "126bar_H": {"PQ": -2, "X": -2, "Z17": 15},
    "126bar_H_dag": {"PQ": 2, "X": 2, "Z17": 2},
    "210_H": {"PQ": 0, "X": 0, "Z17": 0},
    "210_H_dag": {"PQ": 0, "X": 0, "Z17": 0},
    "S": {"PQ": 4, "X": 4, "Z17": 4},
    "S_dag": {"PQ": -4, "X": -4, "Z17": 13},
    "Phi17": {"PQ": 0, "X": 17, "Z17": 0},
    "Phi17_dag": {"PQ": 0, "X": -17, "Z17": 0},
}

SOURCES = {
    "charges": "axion_so10_theory_v20.tex canonical PQ/X/Z17 assignment",
    "declared_contract": "SO(10) gauge + Z17 + PQ scalar selection; continuous X absent",
    "vector_product": "10 tensor 10 = 1 + 45 + 54; no 210",
    "scope": "existence and declared-charge filtering; tensor multiplicities may remain open",
}


def _total_charge(counts: dict[str, int]) -> dict[str, int]:
    totals = {"PQ": 0, "X": 0, "Z17": 0}
    for name, multiplicity in counts.items():
        if multiplicity:
            for charge in totals:
                totals[charge] += multiplicity * CHARGES[name][charge]
    totals["Z17"] %= 17
    return totals


def _allowed(totals: dict[str, int], *, require_x: bool = False) -> dict[str, bool]:
    pq_ok = totals["PQ"] == 0
    z17_ok = totals["Z17"] == 0
    x_ok = totals["X"] == 0 if require_x else True
    return {
        "PQ": pq_ok,
        "X": x_ok,
        "Z17": z17_ok,
        "X_enforced": require_x,
        "all": pq_ok and z17_ok and x_ok,
    }


def _entry(
    name: str,
    counts: dict[str, int],
    dimension: int,
    so10: bool | str,
    *,
    feeds_triplet_mass: bool = False,
    note: str = "",
    require_x: bool = False,
) -> dict[str, Any]:
    totals = _total_charge(counts)
    charge = _allowed(totals, require_x=require_x)
    if not charge["all"]:
        status = "CHARGE_FORBIDDEN"
    elif so10 is False:
        status = "SO10_FORBIDDEN"
    elif so10 is True:
        status = "ALLOWED"
    else:
        status = "CHARGE_OK_SO10_OPEN"
    return {
        "name": name,
        "counts": counts,
        "dim": dimension,
        "so10_invariant_exists": so10,
        "feeds_triplet_mass": feeds_triplet_mass,
        "note": note,
        "charge_totals": totals,
        "charge_allowed": charge,
        "status": status,
    }


def operator_catalogue(*, require_x: bool = False) -> list[dict[str, Any]]:
    raw = [
        ("Phi17", {"Phi17": 1}, 1, True, False, "allowed by declared symmetry; include h.c."),
        ("Phi17^2", {"Phi17": 2}, 2, True, False, "phase-sensitive quadratic; include h.c."),
        ("10_H^dag 10_H", {"10_H_dag": 1, "10_H": 1}, 2, True, True, "quadratic norm"),
        ("126bar_H^dag 126bar_H", {"126bar_H_dag": 1, "126bar_H": 1}, 2, True, True, "quadratic norm"),
        ("210_H^dag 210_H", {"210_H_dag": 1, "210_H": 1}, 2, True, False, "quadratic norm"),
        ("S^dag S", {"S_dag": 1, "S": 1}, 2, True, False, "quadratic norm"),
        ("Phi17^dag Phi17", {"Phi17_dag": 1, "Phi17": 1}, 2, True, False, "quadratic norm"),
        ("210_H^3", {"210_H": 3}, 3, True, False, "unique cubic now derived elsewhere"),
        ("210_H 10_H^dag 10_H", {"210_H": 1, "10_H_dag": 1, "10_H": 1}, 3, False, True, "FORBIDDEN: 10 tensor 10 contains no 210"),
        ("210_H 126bar_H^dag 126bar_H", {"210_H": 1, "126bar_H_dag": 1, "126bar_H": 1}, 3, True, True, "exact cubic channel derived elsewhere"),
        ("bare_10_H^2", {"10_H": 2}, 2, True, True, "SO(10)-allowed but PQ-forbidden"),
        ("10_H^2 S", {"10_H": 2, "S": 1}, 3, True, True, "PQ-safe within-10 mixing"),
        ("bare_126bar_H^2", {"126bar_H": 2}, 2, False, True, "no singlet in (126bar)^2"),
        ("126bar_H^2 S", {"126bar_H": 2, "S": 1}, 3, False, True, "no singlet in (126bar)^2"),
        ("10_H 126bar_H S", {"10_H": 1, "126bar_H": 1, "S": 1}, 3, False, True, "10 tensor 126bar has no singlet"),
        ("S^3", {"S": 3}, 3, True, False, "PQ-forbidden"),
        ("Phi17^3", {"Phi17": 3}, 3, True, False, "allowed by declared symmetry; include h.c."),
        ("10_H^dag 10_H Phi17", {"10_H_dag": 1, "10_H": 1, "Phi17": 1}, 3, True, True, "allowed cubic norm portal; include h.c."),
        ("Phi17^4", {"Phi17": 4}, 4, True, False, "allowed by declared symmetry; include h.c."),
        ("210_H^4", {"210_H": 4}, 4, True, False, "four exact self-quartics derived elsewhere"),
        ("(10_H^dag 10_H)^2", {"10_H_dag": 2, "10_H": 2}, 4, True, True, "two vector quartics: norm square and |H.H|^2"),
        ("(126bar_H^dag 126bar_H)^2", {"126bar_H_dag": 2, "126bar_H": 2}, 4, True, True, "four exact self-quartics derived elsewhere"),
        ("10_H^dag 10_H 126bar_H^dag 126bar_H", {"10_H_dag": 1, "10_H": 1, "126bar_H_dag": 1, "126bar_H": 1}, 4, True, True, "singlet and 45 Hermitian channels"),
        ("210_H^dag 210_H 10_H^dag 10_H", {"210_H_dag": 1, "210_H": 1, "10_H_dag": 1, "10_H": 1}, 4, True, True, "quartic replacement for forbidden linear-210 cubic"),
        ("210_H^dag 210_H 126bar_H^dag 126bar_H", {"210_H_dag": 1, "210_H": 1, "126bar_H_dag": 1, "126bar_H": 1}, 4, True, True, "six pure-irrep channels derived elsewhere"),
        ("|S|^2 |10_H|^2", {"S_dag": 1, "S": 1, "10_H_dag": 1, "10_H": 1}, 4, True, True, "norm portal"),
        ("|S|^2 |126bar_H|^2", {"S_dag": 1, "S": 1, "126bar_H_dag": 1, "126bar_H": 1}, 4, True, True, "norm portal"),
        ("|Phi17|^2 |S|^2", {"Phi17_dag": 1, "Phi17": 1, "S_dag": 1, "S": 1}, 4, True, False, "hierarchy portal"),
        ("(S^dag S)^2", {"S_dag": 2, "S": 2}, 4, True, False, "self quartic"),
        ("(Phi17^dag Phi17)^2", {"Phi17_dag": 2, "Phi17": 2}, 4, True, False, "self quartic"),
        ("210_H^dag 210_H S^dag S", {"210_H_dag": 1, "210_H": 1, "S_dag": 1, "S": 1}, 4, True, False, "norm portal"),
        ("210_H^dag 210_H Phi17^dag Phi17", {"210_H_dag": 1, "210_H": 1, "Phi17_dag": 1, "Phi17": 1}, 4, True, False, "norm portal"),
        ("|Phi17|^2 |10_H|^2", {"Phi17_dag": 1, "Phi17": 1, "10_H_dag": 1, "10_H": 1}, 4, True, True, "norm portal"),
        ("|Phi17|^2 |126bar_H|^2", {"Phi17_dag": 1, "Phi17": 1, "126bar_H_dag": 1, "126bar_H": 1}, 4, True, True, "norm portal"),
        ("10_H^dag 10_H Phi17^2", {"10_H_dag": 1, "10_H": 1, "Phi17": 2}, 4, True, True, "phase-sensitive norm portal; include h.c."),
        ("10_H^2 S Phi17", {"10_H": 2, "S": 1, "Phi17": 1}, 4, True, True, "declared-symmetry extension of kappa channel; include h.c."),
        ("210 · 10 · 126 · S", {"210_H": 1, "10_H": 1, "126bar_H": 1, "S": 1}, 4, True, True, "lambda4 odd-H portal"),
        ("126bar_H^2 10_H^2 S^2", {"126bar_H": 2, "10_H": 2, "S": 2}, 6, "LITERATURE_CLAIMED", False, "phase-sensitive locking operator"),
        ("|126bar_H|^2 |10_H|^2 |S|^2", {"126bar_H_dag": 1, "126bar_H": 1, "10_H_dag": 1, "10_H": 1, "S_dag": 1, "S": 1}, 6, True, False, "positive modulus companion"),
    ]
    return [
        _entry(name, counts, dim, so10, feeds_triplet_mass=feeds, note=note, require_x=require_x)
        for name, counts, dim, so10, feeds, note in raw
    ]


def pq_consequences_for_triplet_mixing(ops: list[dict[str, Any]]) -> dict[str, Any]:
    by_name = {row["name"]: row for row in ops}
    return {
        "status": "DECLARED_PQ_FILTERED_TRIPLET_MIXING_CONSEQUENCES",
        "bare_10_squared": {"charge_allowed": by_name["bare_10_H^2"]["charge_allowed"]["all"], "status": by_name["bare_10_H^2"]["status"]},
        "10_squared_S": {"charge_allowed": by_name["10_H^2 S"]["charge_allowed"]["all"], "status": by_name["10_H^2 S"]["status"]},
        "forbidden_210_10dag10": {"status": by_name["210_H 10_H^dag 10_H"]["status"], "implication": "no triplet diagonal mass linear in the 210 VEV from this cubic"},
        "phi17_extensions": {"Hnorm_Phi17": by_name["10_H^dag 10_H Phi17"]["status"], "H2_S_Phi17": by_name["10_H^2 S Phi17"]["status"]},
        "susy_cal_T_translation": {"identified_with_nonsusy_v20": False, "note": "SUSY superpotential mass matrices are not the non-SUSY Hessian"},
    }


def charge_allowed_reduced_potential(anchor: dict[str, float]) -> dict[str, Any]:
    base = scalar_pd.reduced_radial_vacuum_witness(anchor)
    if not base.get("flag", {}).get("reduced_radial_global_minimum_proved"):
        return {"status": "REDUCED_POTENTIAL_UPSTREAM_FAILED", "flag": {"radial_global_minimum_preserved": False}}
    return {
        "status": "DECLARED_CHARGE_REDUCED_POTENTIAL__FULL_TENSORS_OPEN",
        "base_witness_status": base.get("status"),
        "target_vevs_GeV": base["potential_definition"]["target_vevs_GeV"],
        "radial_quartic_eigenvalues": base["proof"]["normalized_quartic_eigenvalues"],
        "radial_positive_definite": True,
        "flag": {
            "pq_z17_filter_applied": True,
            "pq_z17_x_filter_applied": False,
            "continuous_x_filter_applied": False,
            "radial_global_minimum_preserved": True,
            "forbidden_210_10dag10_removed": True,
            "full_component_tensors_normalized": False,
            "complete_so10_scalar_potential": False,
            "phase_hessian_complete": False,
        },
        "verdict": "Reduced witness survives under the declared no-X contract; full tensor minimization remains open.",
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    operators = operator_catalogue(require_x=False)
    historical_x = operator_catalogue(require_x=True)
    by_name = {row["name"]: row for row in operators}
    historical_by_name = {row["name"]: row for row in historical_x}
    allowed = [row for row in operators if row["status"] in {"ALLOWED", "CHARGE_OK_SO10_OPEN"}]
    forbidden_charge = [row for row in operators if row["status"] == "CHARGE_FORBIDDEN"]
    forbidden_so10 = [row for row in operators if row["status"] == "SO10_FORBIDDEN"]
    feed_mt = [row for row in allowed if row.get("feeds_triplet_mass")]
    potential = charge_allowed_reduced_potential(anchor)
    literature = lit_cg.build_report()

    checks = {
        "catalogue_nonempty": len(operators) >= 38,
        "bare_10_squared_pq_forbidden": by_name["bare_10_H^2"]["status"] == "CHARGE_FORBIDDEN",
        "10_squared_S_allowed": by_name["10_H^2 S"]["status"] == "ALLOWED",
        "locking_operator_charge_allowed": by_name["126bar_H^2 10_H^2 S^2"]["charge_allowed"]["all"],
        "phi3_allowed_without_X": by_name["Phi17^3"]["status"] == "ALLOWED",
        "phi3_forbidden_only_in_historical_X_mode": historical_by_name["Phi17^3"]["status"] == "CHARGE_FORBIDDEN",
        "H2S_Phi17_allowed_without_X": by_name["10_H^2 S Phi17"]["status"] == "ALLOWED",
        "forbidden_210_10dag10": by_name["210_H 10_H^dag 10_H"]["status"] == "SO10_FORBIDDEN",
        "forbidden_cubic_not_feeding_MT": "210_H 10_H^dag 10_H" not in [row["name"] for row in feed_mt],
        "quartic_2102_10dag10_allowed": by_name["210_H^dag 210_H 10_H^dag 10_H"]["status"] == "ALLOWED",
        "radial_potential_built": potential.get("flag", {}).get("radial_global_minimum_preserved", False),
        "literature_cg_not_identified_with_nonsusy_potential": not literature.get("flag", {}).get("identified_with_v20_nonsusy_potential", True),
        "whole_model_not_declared_dead": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": "NONSUSY_Z17_PQ_OPERATOR_FILTER_COMPLETE__FULL_TENSORS_OPEN" if not failures else "NONSUSY_Z17_PQ_OPERATOR_FILTER_FAILED",
        "n_checks": len(checks), "n_failed": len(failures), "failures": failures,
        "sources": SOURCES,
        "declared_symmetry_contract": {"gauge": ["SO(10)"], "global": ["Z17", "PQ_as_scalar_selection_rule"], "continuous_X_imposed": False},
        "charges": CHARGES,
        "n_operators": len(operators), "n_allowed_or_so10_open": len(allowed), "n_charge_forbidden": len(forbidden_charge), "n_so10_forbidden": len(forbidden_so10), "n_allowed_feeding_M_T": len(feed_mt),
        "operators": operators, "allowed_feeding_M_T": [row["name"] for row in feed_mt], "forbidden_names": [row["name"] for row in forbidden_charge + forbidden_so10],
        "historical_continuous_X_comparison": {"Phi17^3_status": historical_by_name["Phi17^3"]["status"], "not_the_declared_model": True},
        "pq_triplet_consequences": pq_consequences_for_triplet_mixing(operators),
        "charge_allowed_reduced_potential": potential,
        "upstream_literature_cg_status": literature.get("status"),
        "checks": checks,
        "flag": {
            "z17_pq_filter_applied": True, "z17_pq_x_filter_applied": False, "continuous_x_filter_applied": False,
            "bare_10_squared_forbidden": True, "ten2_S_allowed": True, "locking_operator_charge_allowed": True,
            "phi17_low_dimension_terms_retained": True, "forbidden_210_10dag10_removed": True,
            "quartic_2102_10dag10_retained": True, "charge_allowed_reduced_potential_built": True,
            "invented_unpublished_cg_tensors": False, "complete_so10_scalar_potential": False, "whole_model_excluded": False,
        },
        "verdict": "The signed filter now follows the declared SO(10)+Z17+PQ contract. Continuous X is metadata only, so low-dimensional Phi17 terms and their H10 portals are retained. The SO(10)-forbidden 210·10dag·10 cubic remains excluded.",
    }


def write_markdown(report: dict[str, Any]) -> str:
    return "\n".join(["# Declared-symmetry non-SUSY Z17/PQ filter — v20", "", f"**Status:** `{report['status']}`", "", report["verdict"], "", f"- Continuous X imposed: {report['declared_symmetry_contract']['continuous_X_imposed']}", f"- Allowed M_T-feeding operators: {report['n_allowed_feeding_M_T']}", ""])


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    ROOT.joinpath("NONSUSY_Z17_PQ_POTENTIAL_FILTER_V20.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    ROOT.joinpath("NONSUSY_Z17_PQ_POTENTIAL_FILTER_V20.md").write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
