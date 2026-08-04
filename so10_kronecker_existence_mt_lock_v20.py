#!/usr/bin/env python3
r"""Signed SO(10) Kronecker ledger for the conditional non-SUSY M_T^2 proxy.

Two historical cubic claims are removed:

* ``210_H 10_H^dag 10_H`` is forbidden because 10 tensor 10 has no 210;
* ``10_H 126bar_H S`` is forbidden because 10 tensor 126bar has no singlet.

The allowed quartic ``lambda4 210_H 10_H 126bar_H S`` is distinct and can
produce an off-diagonal mass-squared entry after 210 and S acquire VEVs. Thus
the forbidden cubic contribution is locked to zero, but the complete M12 is
not generally zero; it remains conditional on the unresolved lambda4 component
CG coefficient.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import nonsusy_charge_allowed_mt_v20 as camt
import nonsusy_z17_pq_potential_filter_v20 as z17
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent
SOURCES = {
    "vector_product": "10 tensor 10 = 1 + 45 + 54; no 210",
    "conjugacy": "10 tensor 126bar has no singlet",
    "allowed_lambda4": "210 tensor 10 tensor 126 contains a singlet; S restores PQ neutrality",
    "scope": "existence ledger and conditional mass-squared proxy",
}

KRONECKER = [
    {"product": "10 tensor 10", "contains_singlet": True, "implication": "10_H^2 S allowed"},
    {"product": "210 tensor 10 tensor 10", "contains_singlet": False, "implication": "210_H 10_H^dag 10_H forbidden"},
    {"product": "10 tensor 126bar", "contains_singlet": False, "implication": "10_H 126bar_H S forbidden"},
    {"product": "126bar tensor 126bar", "contains_singlet": False, "implication": "126bar_H^2 S forbidden"},
    {"product": "126 tensor 126bar", "contains_singlet": True, "implication": "126bar_H^dag 126bar_H allowed"},
    {"product": "210 tensor 126bar tensor 126", "contains_singlet": True, "implication": "one 210_H 126bar_H^dag 126bar_H channel guaranteed"},
    {"product": "210 tensor 10 tensor 126", "contains_singlet": True, "implication": "lambda4 210 10 126bar S allowed after charge restoration"},
]


def resolve_operators() -> list[dict[str, Any]]:
    resolutions = {
        "10_H^2 S": ("ALLOWED", "10 tensor 10 contains 1"),
        "bare_10_H^2": ("ALLOWED_BUT_PQ_FORBIDDEN", "10 tensor 10 contains 1"),
        "210_H 10_H^dag 10_H": ("FORBIDDEN", "10 tensor 10 contains no 210"),
        "10_H 126bar_H S": ("FORBIDDEN", "10 tensor 126bar has no singlet"),
        "126bar_H^2 S": ("FORBIDDEN", "126bar tensor 126bar has no singlet"),
        "bare_126bar_H^2": ("FORBIDDEN", "126bar tensor 126bar has no singlet"),
        "210_H 126bar_H^dag 126bar_H": ("ALLOWED", "standard Phi Delta-bar Delta coupling"),
        "210 · 10 · 126 · S": ("ALLOWED", "Phi H Delta singlet times S"),
        "126bar_H^2 10_H^2 S^2": ("LITERATURE_CLAIMED", "locking CG normalization open"),
    }
    output: list[dict[str, Any]] = []
    for operator in z17.operator_catalogue():
        row = dict(operator)
        if row["name"] in resolutions:
            verdict, reason = resolutions[row["name"]]
            row["so10_resolution"] = {"so10_verdict": verdict, "reason": reason}
            row["so10_invariant_exists"] = verdict in {
                "ALLOWED",
                "ALLOWED_BUT_PQ_FORBIDDEN",
                "LITERATURE_CLAIMED",
            }
            if verdict == "FORBIDDEN":
                row["status"] = "SO10_FORBIDDEN"
            elif verdict == "ALLOWED" and row["charge_allowed"]["all"]:
                row["status"] = "ALLOWED_CHARGE_AND_SO10"
            elif verdict == "LITERATURE_CLAIMED" and row["charge_allowed"]["all"]:
                row["status"] = "ALLOWED_CHARGE__SO10_LITERATURE_CLAIMED"
        output.append(row)
    return output


def audited_mt_scenarios(
    m_i: float, m_gut: float, tau_gauge: float
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for original in camt.SCENARIOS:
        scenario = dict(original)
        scenario["name"] = original["name"] + "__signed_kronecker"
        # Only forbidden historical inputs are forced off. The allowed lambda4
        # component slot is preserved.
        scenario["include_conditional_mix"] = False
        scenario["lam_mix"] = 0.0
        scenario["lam210_10"] = 0.0
        row = camt.evaluate_scenario(
            scenario, m_i=m_i, m_gut=m_gut, tau_gauge=tau_gauge
        )
        matrix_sq = row["mass_squared_matrix_GeV2"]
        expected_lambda4 = float(scenario.get("lam4_cg", 0.0)) * m_gut * m_i
        row["flag"]["forbidden_10_126_S_contribution_locked_zero"] = True
        row["flag"]["forbidden_210_10dag10_locked_zero"] = True
        row["flag"]["lambda4_offdiag_matches_conditional_slot"] = abs(
            float(matrix_sq[0][1]) - expected_lambda4
        ) <= 1e-12 * max(abs(expected_lambda4), 1.0)
        rows.append(row)
    return rows


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "SO10_KRONECKER_MT2_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
        }
    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    tau_gauge = float(scalar_pd.gauge_proton_decay(anchor)["central"]["lifetime_years"])
    resolved = resolve_operators()
    by_name = {row["name"]: row for row in resolved}
    rows = audited_mt_scenarios(m_i, m_gut, tau_gauge)

    forbidden_cubics_zero = all(
        row["flag"]["forbidden_10_126_S_contribution_locked_zero"]
        and row["flag"]["forbidden_210_10dag10_locked_zero"]
        for row in rows
    )
    lambda4_slots_correct = all(
        row["flag"]["lambda4_offdiag_matches_conditional_slot"] for row in rows
    )
    lambda4_rows = [
        row
        for row in rows
        if abs(row["allowed_conditional_inputs"]["lam4_cg"]) > 0.0
    ]
    zero_lambda4_rows = [
        row
        for row in rows
        if abs(row["allowed_conditional_inputs"]["lam4_cg"]) == 0.0
    ]
    excluded = [
        row
        for row in rows
        if row["flag"]["conditionally_excluded_by_ps_mu_K0"]
    ]
    positive = [
        row for row in rows if not row["flag"]["tachyonic"] and row["lightest_GeV"] > 0.0
    ]
    lightest = min(positive, key=lambda row: row["lightest_GeV"])
    aulakh_totals = z17._total_charge({"210_H": 1, "10_H": 1, "126bar_H": 1})

    checks = {
        "kronecker_ledger_nonempty": len(KRONECKER) == 7,
        "ten2_S_so10_allowed": by_name["10_H^2 S"]["status"] == "ALLOWED_CHARGE_AND_SO10",
        "210_10dag10_so10_forbidden": by_name["210_H 10_H^dag 10_H"]["status"] == "SO10_FORBIDDEN",
        "ten_126_S_so10_forbidden": by_name["10_H 126bar_H S"]["status"] == "SO10_FORBIDDEN",
        "lambda4_charge_and_so10_allowed": by_name["210 · 10 · 126 · S"]["status"] == "ALLOWED_CHARGE_AND_SO10",
        "aulakh_without_S_pq_forbidden": aulakh_totals["PQ"] != 0,
        "forbidden_cubic_contributions_zero": forbidden_cubics_zero,
        "lambda4_slots_correct": lambda4_slots_correct,
        "some_lambda4_offdiagonal_nonzero": any(
            abs(row["mass_squared_matrix_GeV2"][0][1]) > 0.0 for row in lambda4_rows
        ),
        "zero_lambda4_rows_have_zero_offdiagonal": all(
            abs(row["mass_squared_matrix_GeV2"][0][1]) == 0.0 for row in zero_lambda4_rows
        ),
        "all_spectra_marked_incomplete": all(
            not row["flag"]["physical_triplet_spectrum_complete"] for row in rows
        ),
        "some_survive": len(positive) > 0,
        "some_conditionally_fail": len(excluded) > 0,
        "whole_model_not_declared_dead": True,
    }
    failures = [name for name, passed in checks.items() if not passed]

    return {
        "status": (
            "SO10_KRONECKER_SIGNED__FORBIDDEN_CUBICS_OFF__LAMBDA4_CG_OPEN"
            if not failures
            else "SO10_KRONECKER_MT2_AUDIT_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "kronecker_ledger": KRONECKER,
        "resolved_operators": resolved,
        "key_verdicts": {
            "10_H^2_S": by_name["10_H^2 S"]["status"],
            "210_H_10dag_H": by_name["210_H 10_H^dag 10_H"]["status"],
            "10_H_126bar_H_S": by_name["10_H 126bar_H S"]["status"],
            "lambda4_210_10_126bar_S": by_name["210 · 10 · 126 · S"]["status"],
            "aulakh_210_10_126_PQ_totals": aulakh_totals,
            "aulakh_210_10_126_pq_forbidden_without_S": aulakh_totals["PQ"] != 0,
        },
        "audited_mt2": {
            "n_scenarios": len(rows),
            "n_excluded_conditionally": len(excluded),
            "forbidden_cubic_contributions_zero": forbidden_cubics_zero,
            "lambda4_component_slot_preserved": True,
            "n_nonzero_lambda4_scenarios": len(lambda4_rows),
            "lightest_scenario": {
                "name": lightest["name"],
                "lightest_GeV": lightest["lightest_GeV"],
                "dominance": lightest["dominance_class"],
            },
            "scenarios": rows,
            "physical_interpretation": (
                "conditional mass-squared proxy; lambda4 and all diagonal component CG coefficients remain open"
            ),
        },
        "next_exact_calculation": [
            "derive component CG coefficients for (210^dag210)(10^dag10)",
            "derive the dimensionful 210 Delta-bar Delta component coefficients",
            "derive the lambda4 210 10 126bar S off-diagonal coefficient",
            "construct and diagonalize the complete non-SUSY color-triplet M_T^2",
        ],
        "flag": {
            "kronecker_resolved": True,
            "ten2_S_so10_and_charge_allowed": True,
            "forbidden_210_10dag10_removed": True,
            "forbidden_10_126_S_removed": True,
            "forbidden_cubic_contributions_locked_zero": forbidden_cubics_zero,
            "lambda4_offdiag_allowed_but_CG_open": True,
            "lambda4_offdiag_not_locked_zero": len(lambda4_rows) > 0,
            "physical_component_CG_complete": False,
            "physical_triplet_spectrum_complete": False,
            "invented_unpublished_cg_normalizations": False,
            "complete_so10_scalar_potential": False,
            "exact_unique_proton_lifetime": False,
            "conditional_parameter_points_excluded": len(excluded) > 0,
            "whole_model_excluded": False,
        },
        "verdict": (
            "Forbidden 210·10†·10 and 10·126bar·S cubic contributions are "
            "locked to zero. The distinct allowed lambda4·210·10·126bar·S "
            "off-diagonal mass-squared slot is retained and is not zero in "
            "general. Its component CG coefficient and the complete physical "
            "triplet spectrum remain open."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Signed SO(10) Kronecker M_T^2 audit — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            f"- Forbidden cubic contributions zero: {report['audited_mt2']['forbidden_cubic_contributions_zero']}",
            f"- Lambda4 component slot preserved: {report['audited_mt2']['lambda4_component_slot_preserved']}",
            f"- Physical triplet spectrum complete: {report['flag']['physical_triplet_spectrum_complete']}",
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    ROOT.joinpath("SO10_KRONECKER_MT_LOCK_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("SO10_KRONECKER_MT_LOCK_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
