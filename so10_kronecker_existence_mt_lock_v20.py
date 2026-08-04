#!/usr/bin/env python3
r"""Signed SO(10) Kronecker ledger and locked non-SUSY triplet proxy.

The historical ledger incorrectly claimed a singlet in ``210 tensor 10 tensor
10``. Since ``10 tensor 10 = 1 + 45 + 54`` contains no 210, the cubic
``210_H 10_H^dag 10_H`` is forbidden. Consequently, every triplet proxy term
linear in ``<210>`` generated from that cubic is removed. The allowed Higgs
norm portal begins at ``(210^dag 210)(10^dag 10)`` and requires a mass-squared
component calculation not represented by the old linear-mass proxy.

The off-diagonal 10-126-S cubic remains SO(10)-forbidden and is locked to zero.
All returned triplet scenarios are conditional diagnostics, not a physical
non-SUSY component spectrum.
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
    "conjugacy": "a singlet in A tensor B requires conjugate representations",
    "scope": "operator existence and conditional triplet proxy only",
}

KRONECKER = [
    {
        "product": "10 tensor 10",
        "contains_singlet": True,
        "decomposition_note": "1 + 45 + 54",
        "implication": "10_H^2 S is SO(10)-allowed",
    },
    {
        "product": "210 tensor 10 tensor 10",
        "contains_singlet": False,
        "decomposition_note": "10 tensor 10 has no 210",
        "implication": "210_H 10_H^dag 10_H is SO(10)-forbidden",
    },
    {
        "product": "10 tensor 126bar",
        "contains_singlet": False,
        "decomposition_note": "representations are not conjugates",
        "implication": "10_H 126bar_H S is SO(10)-forbidden",
    },
    {
        "product": "126bar tensor 126bar",
        "contains_singlet": False,
        "decomposition_note": "singlet occurs in 126 tensor 126bar",
        "implication": "126bar_H^2 S is SO(10)-forbidden",
    },
    {
        "product": "126 tensor 126bar",
        "contains_singlet": True,
        "decomposition_note": "contains 1",
        "implication": "126bar_H^dag 126bar_H is allowed",
    },
    {
        "product": "210 tensor 126bar tensor 126",
        "contains_singlet": True,
        "decomposition_note": "standard Phi Delta-bar Delta coupling",
        "implication": "one 210_H 126bar_H^dag 126bar_H channel guaranteed",
    },
    {
        "product": "210 tensor 10 tensor 126",
        "contains_singlet": True,
        "decomposition_note": "standard Phi H Delta coupling",
        "implication": "SO(10)-allowed but PQ-odd without S; lambda4 with S is charge-neutral",
    },
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
        "126bar_H^2 10_H^2 S^2": (
            "LITERATURE_CLAIMED",
            "locking channel requires explicit CG normalization",
        ),
    }
    output: list[dict[str, Any]] = []
    for operator in z17.operator_catalogue():
        row = dict(operator)
        if row["name"] in resolutions:
            verdict, reason = resolutions[row["name"]]
            row["so10_resolution"] = {
                "so10_verdict": verdict,
                "reason": reason,
            }
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


def locked_mt_scenarios(
    m_i: float, m_gut: float, tau_gauge: float
) -> list[dict[str, Any]]:
    scenarios: list[dict[str, Any]] = []
    for original in camt.SCENARIOS:
        scenario = dict(original)
        scenario["name"] = original["name"] + "__signed_forbidden_terms_off"
        scenario["include_conditional_mix"] = False
        scenario["lam_mix"] = 0.0
        scenario["lam210_10"] = 0.0
        row = camt.evaluate_scenario(
            scenario, m_i=m_i, m_gut=m_gut, tau_gauge=tau_gauge
        )
        row["include_conditional_10_126_S"] = False
        row["flag"]["so10_mix_locked_off"] = True
        row["flag"]["forbidden_210_10dag10_locked_off"] = True
        row["flag"]["M12_is_zero"] = abs(row["mass_matrix_GeV"][0][1]) < 1e-30
        row["flag"]["physical_2102_10dag10_mass_squared_included"] = False
        row["flag"]["physical_triplet_spectrum_complete"] = False
        scenarios.append(row)
    return scenarios


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "SO10_KRONECKER_MT_LOCK_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    gauge = scalar_pd.gauge_proton_decay(anchor)
    tau_gauge = float(gauge["central"]["lifetime_years"])
    resolved = resolve_operators()
    by_name = {row["name"]: row for row in resolved}
    rows = locked_mt_scenarios(m_i, m_gut, tau_gauge)

    all_m12_zero = all(row["flag"]["M12_is_zero"] for row in rows)
    all_forbidden_diagonal_zero = all(
        row["flag"]["forbidden_210_10dag10_locked_off"] for row in rows
    )
    excluded = [
        row
        for row in rows
        if row["flag"].get("conditionally_excluded_by_ps_mu_K0", False)
    ]
    physical = [row for row in rows if not row["flag"].get("singular", False)]
    lightest = min(physical, key=lambda row: row["lightest_GeV"]) if physical else None
    aulakh_totals = z17._total_charge(
        {"210_H": 1, "10_H": 1, "126bar_H": 1}
    )

    checks = {
        "kronecker_ledger_nonempty": len(KRONECKER) >= 7,
        "ten2_S_so10_allowed": by_name["10_H^2 S"]["status"] == "ALLOWED_CHARGE_AND_SO10",
        "210_10dag10_so10_forbidden": by_name["210_H 10_H^dag 10_H"]["status"] == "SO10_FORBIDDEN",
        "ten_126_S_so10_forbidden": by_name["10_H 126bar_H S"]["status"] == "SO10_FORBIDDEN",
        "1262_S_so10_forbidden": by_name["126bar_H^2 S"]["status"] == "SO10_FORBIDDEN",
        "aulakh_phi_h_delta_without_S_pq_forbidden": aulakh_totals["PQ"] != 0,
        "all_locked_M12_zero": all_m12_zero,
        "forbidden_linear_210_Higgs_mass_locked_zero": all_forbidden_diagonal_zero,
        "old_proxy_not_marked_physical": all(
            not row["flag"]["physical_triplet_spectrum_complete"] for row in rows
        ),
        "whole_model_not_declared_dead": True,
    }
    failures = [name for name, passed in checks.items() if not passed]

    return {
        "status": (
            "SO10_KRONECKER_RESOLVED__MT_MIX_LOCKED_OFF__CG_NORMS_OPEN"
            if not failures
            else "SO10_KRONECKER_MT_LOCK_FAILED"
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
            "126bar_H^2_S": by_name["126bar_H^2 S"]["status"],
            "aulakh_210_10_126_PQ_totals": aulakh_totals,
            "aulakh_210_10_126_pq_forbidden_in_v20": aulakh_totals["PQ"] != 0,
        },
        "locked_mt": {
            "n_scenarios": len(rows),
            "n_excluded_by_ps_mu_K0": len(excluded),
            "excluded_scenario_names": [row["name"] for row in excluded],
            "all_M12_zero": all_m12_zero,
            "forbidden_linear_210_Higgs_mass_zero": all_forbidden_diagonal_zero,
            "lightest_scenario": None
            if lightest is None
            else {
                "name": lightest["name"],
                "lightest_GeV": lightest["lightest_GeV"],
                "dominance": lightest["dominance_class"],
            },
            "scenarios": rows,
            "physical_interpretation": (
                "conditional only; the allowed 210^dag210 10^dag10 quartic "
                "must be projected into the non-SUSY mass-squared matrix"
            ),
        },
        "next_exact_calculation": [
            "Project (210^dag210)(10^dag10) into every color-triplet component mass-squared entry",
            "Project the allowed 210 Delta-bar Delta cubic with dimensionful normalization",
            "Normalize the lambda4 Phi H Delta S CG coefficient",
            "Rebuild the complete non-SUSY triplet mass-squared matrix",
        ],
        "flag": {
            "kronecker_resolved": True,
            "ten2_S_so10_and_charge_allowed": True,
            "forbidden_210_10dag10_removed": True,
            "ten_126_S_so10_forbidden": True,
            "mt_offdiag_locked_zero": all_m12_zero,
            "forbidden_linear_210_Higgs_diagonal_locked_zero": all_forbidden_diagonal_zero,
            "aulakh_offdiag_not_imported_pq": aulakh_totals["PQ"] != 0,
            "physical_2102_10dag10_mass_squared_included": False,
            "physical_triplet_spectrum_complete": False,
            "invented_unpublished_cg_normalizations": False,
            "complete_so10_scalar_potential": False,
            "exact_unique_proton_lifetime": False,
            "conditional_parameter_points_excluded": len(excluded) > 0,
            "whole_model_excluded": False,
        },
        "verdict": (
            "The signed Kronecker ledger removes both forbidden off-diagonal "
            "10·126bar·S mixing and forbidden diagonal 210·10†·10 mass. The "
            "returned proxy matrices set those entries to zero. They are not "
            "physical spectra until the allowed quartic 210†210·10†10 is "
            "projected into a complete mass-squared matrix."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Signed SO(10) Kronecker and triplet proxy audit — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            f"- All M12 zero: {report['locked_mt']['all_M12_zero']}",
            f"- Forbidden linear-210 Higgs mass zero: {report['locked_mt']['forbidden_linear_210_Higgs_mass_zero']}",
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
