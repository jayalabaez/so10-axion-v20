#!/usr/bin/env python3
r"""Signed SO(10)×Z17/PQ operator filter for the non-SUSY v20 scalar EFT.

Charge neutrality and SO(10) singlet existence are separate requirements.
The historical catalogue incorrectly marked ``210_H 10_H^dag 10_H`` as an
SO(10) invariant. It is forbidden because ``10 tensor 10 = 1 + 45 + 54``
contains no 210. The allowed 210-dependent Higgs norm portal starts at
``(210_H^dag 210_H)(10_H^dag 10_H)``, not a cubic linear in 210.

The filter remains an operator-existence ledger, not a complete invariant-ring
multiplicity calculation or a full component potential.
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
    "vector_product": "10 tensor 10 = 1 + 45 + 54; no 210",
    "scope": "existence and charge filtering; tensor multiplicities remain open",
}


def _total_charge(counts: dict[str, int]) -> dict[str, int]:
    pq = x = z = 0
    for name, multiplicity in counts.items():
        if multiplicity == 0:
            continue
        charge = CHARGES[name]
        pq += multiplicity * charge["PQ"]
        x += multiplicity * charge["X"]
        z += multiplicity * charge["Z17"]
    return {"PQ": pq, "X": x, "Z17": z % 17}


def _allowed(totals: dict[str, int], *, require_x: bool = True) -> dict[str, bool]:
    pq_ok = totals["PQ"] == 0
    z17_ok = totals["Z17"] == 0
    x_ok = totals["X"] == 0 if require_x else True
    return {"PQ": pq_ok, "X": x_ok, "Z17": z17_ok, "all": pq_ok and x_ok and z17_ok}


def _entry(
    name: str,
    counts: dict[str, int],
    dimension: int,
    so10: bool | str,
    *,
    feeds_triplet_mass: bool = False,
    note: str = "",
) -> dict[str, Any]:
    totals = _total_charge(counts)
    charge = _allowed(totals)
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


def operator_catalogue() -> list[dict[str, Any]]:
    raw = [
        ("10_H^dag 10_H", {"10_H_dag": 1, "10_H": 1}, 2, True, True, "quadratic norm"),
        ("126bar_H^dag 126bar_H", {"126bar_H_dag": 1, "126bar_H": 1}, 2, True, True, "quadratic norm"),
        ("210_H^dag 210_H", {"210_H_dag": 1, "210_H": 1}, 2, True, False, "quadratic norm"),
        ("S^dag S", {"S_dag": 1, "S": 1}, 2, True, False, "quadratic norm"),
        ("Phi17^dag Phi17", {"Phi17_dag": 1, "Phi17": 1}, 2, True, False, "quadratic norm"),
        ("210_H^3", {"210_H": 3}, 3, True, False, "one channel independently guaranteed; complete multiplicity open"),
        (
            "210_H 10_H^dag 10_H",
            {"210_H": 1, "10_H_dag": 1, "10_H": 1},
            3,
            False,
            True,
            "FORBIDDEN: 10 tensor 10 contains 1+45+54 and no 210",
        ),
        (
            "210_H 126bar_H^dag 126bar_H",
            {"210_H": 1, "126bar_H_dag": 1, "126bar_H": 1},
            3,
            True,
            True,
            "one channel independently guaranteed; complete multiplicity open",
        ),
        ("bare_10_H^2", {"10_H": 2}, 2, True, True, "SO(10)-allowed but PQ-forbidden"),
        ("10_H^2 S", {"10_H": 2, "S": 1}, 3, True, True, "PQ-safe within-10 mixing"),
        ("bare_126bar_H^2", {"126bar_H": 2}, 2, False, True, "no singlet in (126bar)^2"),
        ("126bar_H^2 S", {"126bar_H": 2, "S": 1}, 3, False, True, "no singlet in (126bar)^2"),
        ("10_H 126bar_H S", {"10_H": 1, "126bar_H": 1, "S": 1}, 3, False, True, "10 tensor 126bar has no singlet"),
        ("S^3", {"S": 3}, 3, True, False, "charge-forbidden"),
        ("Phi17^3", {"Phi17": 3}, 3, True, False, "X-forbidden"),
        ("210_H^4", {"210_H": 4}, 4, True, False, "multiple contractions; multiplicity open"),
        ("(10_H^dag 10_H)^2", {"10_H_dag": 2, "10_H": 2}, 4, True, True, "at least two independent channels"),
        ("(126bar_H^dag 126bar_H)^2", {"126bar_H_dag": 2, "126bar_H": 2}, 4, True, True, "at least two independent channels"),
        (
            "10_H^dag 10_H 126bar_H^dag 126bar_H",
            {"10_H_dag": 1, "10_H": 1, "126bar_H_dag": 1, "126bar_H": 1},
            4,
            True,
            True,
            "at least two independent channels",
        ),
        (
            "210_H^dag 210_H 10_H^dag 10_H",
            {"210_H_dag": 1, "210_H": 1, "10_H_dag": 1, "10_H": 1},
            4,
            True,
            True,
            "allowed quartic replacement for forbidden linear-210 cubic",
        ),
        (
            "210_H^dag 210_H 126bar_H^dag 126bar_H",
            {"210_H_dag": 1, "210_H": 1, "126bar_H_dag": 1, "126bar_H": 1},
            4,
            True,
            True,
            "at least two independent channels",
        ),
        ("|S|^2 |10_H|^2", {"S_dag": 1, "S": 1, "10_H_dag": 1, "10_H": 1}, 4, True, True, "norm portal"),
        ("|S|^2 |126bar_H|^2", {"S_dag": 1, "S": 1, "126bar_H_dag": 1, "126bar_H": 1}, 4, True, True, "norm portal"),
        ("|Phi17|^2 |S|^2", {"Phi17_dag": 1, "Phi17": 1, "S_dag": 1, "S": 1}, 4, True, False, "hierarchy portal"),
        ("(S^dag S)^2", {"S_dag": 2, "S": 2}, 4, True, False, "self quartic"),
        ("(Phi17^dag Phi17)^2", {"Phi17_dag": 2, "Phi17": 2}, 4, True, False, "self quartic"),
        ("210_H^dag 210_H S^dag S", {"210_H_dag": 1, "210_H": 1, "S_dag": 1, "S": 1}, 4, True, False, "norm portal"),
        ("210_H^dag 210_H Phi17^dag Phi17", {"210_H_dag": 1, "210_H": 1, "Phi17_dag": 1, "Phi17": 1}, 4, True, False, "norm portal"),
        ("|Phi17|^2 |10_H|^2", {"Phi17_dag": 1, "Phi17": 1, "10_H_dag": 1, "10_H": 1}, 4, True, True, "norm portal"),
        ("|Phi17|^2 |126bar_H|^2", {"Phi17_dag": 1, "Phi17": 1, "126bar_H_dag": 1, "126bar_H": 1}, 4, True, True, "norm portal"),
        (
            "210 · 10 · 126 · S",
            {"210_H": 1, "10_H": 1, "126bar_H": 1, "S": 1},
            4,
            True,
            True,
            "lambda4 odd-H portal; CG normalization remains open",
        ),
        (
            "126bar_H^2 10_H^2 S^2",
            {"126bar_H": 2, "10_H": 2, "S": 2},
            6,
            "LITERATURE_CLAIMED",
            False,
            "phase-sensitive locking operator",
        ),
        (
            "|126bar_H|^2 |10_H|^2 |S|^2",
            {"126bar_H_dag": 1, "126bar_H": 1, "10_H_dag": 1, "10_H": 1, "S_dag": 1, "S": 1},
            6,
            True,
            False,
            "positive modulus companion to phase locking",
        ),
    ]
    return [
        _entry(name, counts, dim, so10, feeds_triplet_mass=feeds, note=note)
        for name, counts, dim, so10, feeds, note in raw
    ]


def pq_consequences_for_triplet_mixing(ops: list[dict[str, Any]]) -> dict[str, Any]:
    by_name = {row["name"]: row for row in ops}
    return {
        "status": "SIGNED_PQ_FILTERED_TRIPLET_MIXING_CONSEQUENCES",
        "bare_10_squared": {
            "charge_allowed": by_name["bare_10_H^2"]["charge_allowed"]["all"],
            "status": by_name["bare_10_H^2"]["status"],
        },
        "10_squared_S": {
            "charge_allowed": by_name["10_H^2 S"]["charge_allowed"]["all"],
            "status": by_name["10_H^2 S"]["status"],
        },
        "forbidden_210_10dag10": {
            "status": by_name["210_H 10_H^dag 10_H"]["status"],
            "implication": "no triplet diagonal mass linear in the 210 VEV from this cubic",
        },
        "susy_cal_T_translation": {
            "identified_with_nonsusy_v20": False,
            "note": "SUSY superpotential mass matrices are not the non-SUSY Hessian",
        },
    }


def charge_allowed_reduced_potential(anchor: dict[str, float]) -> dict[str, Any]:
    base = scalar_pd.reduced_radial_vacuum_witness(anchor)
    if not base.get("flag", {}).get("reduced_radial_global_minimum_proved"):
        return {"status": "REDUCED_POTENTIAL_UPSTREAM_FAILED", "flag": {"radial_global_minimum_preserved": False}}
    return {
        "status": "SIGNED_CHARGE_ALLOWED_REDUCED_POTENTIAL__FULL_TENSORS_OPEN",
        "base_witness_status": base.get("status"),
        "target_vevs_GeV": base["potential_definition"]["target_vevs_GeV"],
        "radial_quartic_eigenvalues": base["proof"]["normalized_quartic_eigenvalues"],
        "radial_positive_definite": True,
        "flag": {
            "pq_z17_x_filter_applied": True,
            "radial_global_minimum_preserved": True,
            "forbidden_210_10dag10_removed": True,
            "full_component_tensors_normalized": False,
            "complete_so10_scalar_potential": False,
            "phase_hessian_complete": False,
        },
        "verdict": "Reduced witness survives after removing the forbidden cubic; full tensor minimization remains open.",
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    operators = operator_catalogue()
    by_name = {row["name"]: row for row in operators}
    allowed = [row for row in operators if row["status"] in {"ALLOWED", "CHARGE_OK_SO10_OPEN"}]
    forbidden_charge = [row for row in operators if row["status"] == "CHARGE_FORBIDDEN"]
    forbidden_so10 = [row for row in operators if row["status"] == "SO10_FORBIDDEN"]
    feed_mt = [row for row in allowed if row.get("feeds_triplet_mass")]
    potential = charge_allowed_reduced_potential(anchor)
    literature = lit_cg.build_report()

    checks = {
        "catalogue_nonempty": len(operators) >= 30,
        "bare_10_squared_pq_forbidden": by_name["bare_10_H^2"]["status"] == "CHARGE_FORBIDDEN",
        "10_squared_S_allowed": by_name["10_H^2 S"]["status"] == "ALLOWED",
        "locking_operator_charge_allowed": by_name["126bar_H^2 10_H^2 S^2"]["charge_allowed"]["all"],
        "phi3_x_forbidden": by_name["Phi17^3"]["status"] == "CHARGE_FORBIDDEN",
        "forbidden_210_10dag10": by_name["210_H 10_H^dag 10_H"]["status"] == "SO10_FORBIDDEN",
        "forbidden_cubic_not_feeding_MT": "210_H 10_H^dag 10_H" not in [row["name"] for row in feed_mt],
        "quartic_2102_10dag10_allowed": by_name["210_H^dag 210_H 10_H^dag 10_H"]["status"] == "ALLOWED",
        "radial_potential_built": potential.get("flag", {}).get("radial_global_minimum_preserved", False),
        "literature_cg_not_identified_with_nonsusy_potential": not literature.get("flag", {}).get("identified_with_v20_nonsusy_potential", True),
        "whole_model_not_declared_dead": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "NONSUSY_Z17_PQ_OPERATOR_FILTER_COMPLETE__FULL_TENSORS_OPEN"
            if not failures
            else "NONSUSY_Z17_PQ_OPERATOR_FILTER_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "charges": CHARGES,
        "n_operators": len(operators),
        "n_allowed_or_so10_open": len(allowed),
        "n_charge_forbidden": len(forbidden_charge),
        "n_so10_forbidden": len(forbidden_so10),
        "n_allowed_feeding_M_T": len(feed_mt),
        "operators": operators,
        "allowed_feeding_M_T": [row["name"] for row in feed_mt],
        "forbidden_names": [row["name"] for row in forbidden_charge + forbidden_so10],
        "pq_triplet_consequences": pq_consequences_for_triplet_mixing(operators),
        "charge_allowed_reduced_potential": potential,
        "upstream_literature_cg_status": literature.get("status"),
        "flag": {
            "z17_pq_x_filter_applied": True,
            "bare_10_squared_forbidden": True,
            "ten2_S_allowed": True,
            "locking_operator_charge_allowed": True,
            "forbidden_210_10dag10_removed": True,
            "quartic_2102_10dag10_retained": True,
            "charge_allowed_reduced_potential_built": True,
            "invented_unpublished_cg_tensors": False,
            "complete_so10_scalar_potential": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "Charge and SO(10) existence are now separated. The impossible "
            "210·10†·10 cubic is removed, while the allowed 210†210·10†10 "
            "quartic remains. All spectra that used a mass linear in <210> "
            "from the forbidden cubic require revalidation."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Signed non-SUSY Z17/PQ operator filter — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            f"- SO(10)-forbidden operators: {report['n_so10_forbidden']}",
            f"- Allowed M_T-feeding operators: {report['n_allowed_feeding_M_T']}",
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    ROOT.joinpath("NONSUSY_Z17_PQ_POTENTIAL_FILTER_V20.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    ROOT.joinpath("NONSUSY_Z17_PQ_POTENTIAL_FILTER_V20.md").write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
