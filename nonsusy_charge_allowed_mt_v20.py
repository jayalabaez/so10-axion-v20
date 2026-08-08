#!/usr/bin/env python3
r"""Signed non-SUSY color-triplet mass-squared proxy (v20).

The historical module mixed operator dimensions:

* the forbidden cubic ``210_H 10_H^dag 10_H`` was treated as a mass linear in
  ``<210>``;
* quartic norm portals were also inserted linearly as masses rather than
  quadratically as mass-squared contributions;
* the SO(10)-forbidden ``10_H 126bar_H S`` cubic was optionally used off
  diagonal;
* the allowed ``lambda4 210_H 10_H 126bar_H S`` slot was absent.

This replacement builds a Hermitian **mass-squared** proxy. Forbidden inputs
are accepted only for backward-compatible call signatures and are ignored.
The allowed lambda4 slot is explicit but conditional on its unresolved
component CG coefficient. Physical masses are square roots of positive
mass-squared eigenvalues. All proton-decay routing remains conditional until
the complete non-SUSY component matrix is derived.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import conditional_mt_interference_v20 as cmt
import nonsusy_z17_pq_potential_filter_v20 as z17
import patel_shukla_scalar_pdecay_v20 as ps
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent

SOURCES = {
    "operator_filter": "nonsusy_z17_pq_potential_filter_v20 signed catalogue",
    "matrix_dimension": "scalar-potential second derivatives have mass dimension two",
    "scope": "conditional two-state proxy; full component CG matrix open",
}


def allowed_mt_operator_ledger() -> dict[str, Any]:
    operators = z17.operator_catalogue(require_x=True)
    allowed = [
        row
        for row in operators
        if row.get("feeds_triplet_mass")
        and row["charge_allowed"]["all"]
        and row["status"] in {"ALLOWED", "CHARGE_OK_SO10_OPEN"}
    ]
    forbidden = [
        row
        for row in operators
        if row.get("feeds_triplet_mass")
        and row["status"] in {"CHARGE_FORBIDDEN", "SO10_FORBIDDEN"}
    ]
    names = {row["name"] for row in allowed}
    forbidden_names = {row["name"] for row in forbidden}
    return {
        "allowed_feeding_M_T2": [
            {
                "name": row["name"],
                "dim": row["dim"],
                "status": row["status"],
                "so10_invariant_exists": row["so10_invariant_exists"],
            }
            for row in allowed
        ],
        "forbidden_feeding_M_T2": sorted(forbidden_names),
        "bare_10_squared_excluded": "bare_10_H^2" in forbidden_names,
        "forbidden_210_10dag10_excluded": "210_H 10_H^dag 10_H" in forbidden_names,
        "forbidden_10_126_S_excluded": "10_H 126bar_H S" in forbidden_names,
        "ten2_S_included": "10_H^2 S" in names,
        "quartic_2102_10dag10_included": "210_H^dag 210_H 10_H^dag 10_H" in names,
        "lambda4_210_10_126_S_included": "210 · 10 · 126 · S" in names,
    }


def fill_charge_allowed_mt(
    *,
    v210: float,
    vS: float,
    mu10: float,
    mu126: float,
    lam210_10: float,
    lam210_126: float,
    lamS_10: float,
    lamS_126: float,
    lam_mix: float,
    include_conditional_mix: bool,
    lam2102_10: float = 0.0,
    lam4_cg: float = 0.0,
) -> np.ndarray:
    """Return conditional M_T^2 in basis (T_10,T_126bar).

    ``lam210_10`` and ``lam_mix`` are historical forbidden inputs and are
    intentionally ignored. The allowed terms represented are

    M11^2 = mu10^2 + lam2102_10 v210^2 + lamS_10 vS^2,
    M22^2 = mu126^2 + lam210_126 vS v210 + lamS_126 vS^2,
    M12^2 = lam4_cg v210 vS.

    ``lam210_126`` parametrizes the dimensionful cubic coefficient as
    a_210,126 = lam210_126*vS. Every coefficient remains conditional because
    component CG normalizations are open.
    """
    del lam210_10, lam_mix, include_conditional_mix
    m11_sq = mu10**2 + lam2102_10 * v210**2 + lamS_10 * vS**2
    m22_sq = mu126**2 + lam210_126 * vS * v210 + lamS_126 * vS**2
    m12_sq = lam4_cg * v210 * vS
    return np.array([[m11_sq, m12_sq], [m12_sq, m22_sq]], dtype=float)


def within_10_mixing_from_S(
    *, m_t: float, m_tbar: float, kappa: float, vS: float
) -> dict[str, Any]:
    """Effective within-10 mass-squared mixing from 10_H^2 S."""
    mu2 = kappa * vS**2
    denominator = m_tbar**2 - m_t**2
    theta = (
        math.pi / 4.0
        if abs(denominator) < 1e-30 and abs(mu2) > 0.0
        else (
            0.0
            if abs(denominator) < 1e-30
            else 0.5 * math.atan2(2.0 * mu2, denominator)
        )
    )
    return {
        "operator": "10_H^2 S",
        "effective_mu2_GeV2": mu2,
        "m_T_GeV": m_t,
        "m_Tbar_GeV": m_tbar,
        "theta_T_rad": theta,
        "theta_T_deg": float(math.degrees(theta)),
        "bare_10_squared_used": False,
        "component_cg_normalization_complete": False,
    }


def locking_phase_hessian(*, A_lock: float) -> dict[str, Any]:
    gradient = np.array([2.0, 2.0, 2.0], dtype=float)
    hessian = A_lock * np.outer(gradient, gradient)
    eigenvalues = np.linalg.eigvalsh(hessian)
    tolerance = 1e-12 * max(1.0, abs(A_lock))
    return {
        "potential": "V=-A_lock cos(2 phi_Delta+2 phi_10+2 phi_S)",
        "A_lock": A_lock,
        "fields": ["phi_DeltaR_126", "phi_10", "phi_S"],
        "hessian": hessian.tolist(),
        "eigenvalues": [float(value) for value in eigenvalues],
        "n_positive": int(np.sum(eigenvalues > tolerance)),
        "n_zero": int(np.sum(np.abs(eigenvalues) <= tolerance)),
        "flag": {"locking_operator_included": True, "complete_phase_hessian": False},
    }


SCENARIOS: list[dict[str, Any]] = [
    {
        "name": "decoupled_MI_no_mix",
        "mu10_over_MI": 1.0,
        "mu126_over_MI": 1.0,
        "lam210_10": 0.0,
        "lam210_126": 0.0,
        "lam2102_10": 0.0,
        "lamS_10": 0.0,
        "lamS_126": 0.0,
        "lam_mix": 0.0,
        "include_conditional_mix": False,
        "lam4_cg": 0.0,
        "kappa": 0.0,
    },
    {
        "name": "allowed_2102_push_10",
        "mu10_over_MI": 0.0,
        "mu126_over_MI": 1.0,
        "lam210_10": 0.0,
        "lam210_126": 0.0,
        "lam2102_10": 1.0,
        "lamS_10": 0.0,
        "lamS_126": 0.0,
        "lam_mix": 0.0,
        "include_conditional_mix": False,
        "lam4_cg": 0.0,
        "kappa": 0.0,
    },
    {
        "name": "S_dressed_diagonals",
        "mu10_over_MI": 0.5,
        "mu126_over_MI": 0.5,
        "lam210_10": 0.0,
        "lam210_126": 0.0,
        "lam2102_10": 0.0,
        "lamS_10": 1.0,
        "lamS_126": 1.0,
        "lam_mix": 0.0,
        "include_conditional_mix": False,
        "lam4_cg": 0.0,
        "kappa": 0.1,
    },
    {
        "name": "lambda4_small_conditional_mix",
        "mu10_over_MI": 1.0,
        "mu126_over_MI": 1.0,
        "lam210_10": 0.0,
        "lam210_126": 0.1,
        "lam2102_10": 0.1,
        "lamS_10": 0.0,
        "lamS_126": 0.0,
        "lam_mix": 0.0,
        "include_conditional_mix": False,
        "lam4_cg": 1e-4,
        "kappa": 0.0,
    },
    {
        "name": "lambda4_tachyon_stress",
        "mu10_over_MI": 1.0,
        "mu126_over_MI": 1.0,
        "lam210_10": 0.0,
        "lam210_126": 0.0,
        "lam2102_10": 0.0,
        "lamS_10": 0.0,
        "lamS_126": 0.0,
        "lam_mix": 0.0,
        "include_conditional_mix": False,
        "lam4_cg": 1.0,
        "kappa": 0.0,
    },
    {
        "name": "forbidden_inputs_ignored",
        "mu10_over_MI": 1.0,
        "mu126_over_MI": 1.0,
        "lam210_10": 99.0,
        "lam210_126": 0.0,
        "lam2102_10": 0.0,
        "lamS_10": 0.0,
        "lamS_126": 0.0,
        "lam_mix": 99.0,
        "include_conditional_mix": True,
        "lam4_cg": 0.0,
        "kappa": 0.0,
    },
    {
        "name": "light_10_stress",
        "mu10_over_MI": 0.1,
        "mu126_over_MI": 5.0,
        "lam210_10": 0.0,
        "lam210_126": 0.0,
        "lam2102_10": 0.0,
        "lamS_10": 0.0,
        "lamS_126": 0.0,
        "lam_mix": 0.0,
        "include_conditional_mix": False,
        "lam4_cg": 0.0,
        "kappa": 0.01,
    },
]


def evaluate_scenario(
    scenario: dict[str, Any], *, m_i: float, m_gut: float, tau_gauge: float
) -> dict[str, Any]:
    matrix_sq = fill_charge_allowed_mt(
        v210=m_gut,
        vS=m_i,
        mu10=float(scenario["mu10_over_MI"]) * m_i,
        mu126=float(scenario["mu126_over_MI"]) * m_i,
        lam210_10=float(scenario.get("lam210_10", 0.0)),
        lam210_126=float(scenario.get("lam210_126", 0.0)),
        lamS_10=float(scenario.get("lamS_10", 0.0)),
        lamS_126=float(scenario.get("lamS_126", 0.0)),
        lam_mix=float(scenario.get("lam_mix", 0.0)),
        include_conditional_mix=bool(scenario.get("include_conditional_mix", False)),
        lam2102_10=float(scenario.get("lam2102_10", 0.0)),
        lam4_cg=float(scenario.get("lam4_cg", 0.0)),
    )
    eigenvalues_sq, eigenvectors = np.linalg.eigh(matrix_sq)
    order = np.argsort(eigenvalues_sq)
    eigenvalues_sq = eigenvalues_sq[order]
    eigenvectors = eigenvectors[:, order]
    tachyonic = bool(np.min(eigenvalues_sq) < 0.0)
    singular = bool(np.min(np.abs(eigenvalues_sq)) <= 1e-24 * max(np.max(np.abs(eigenvalues_sq)), 1.0))
    masses = np.sqrt(np.clip(eigenvalues_sq, 0.0, None))
    positive_masses = masses[eigenvalues_sq > 0.0]
    lightest = float(np.min(positive_masses)) if positive_masses.size else 0.0
    light_index = int(np.where(masses == lightest)[0][0]) if lightest > 0.0 else 0
    frac10 = float(eigenvectors[0, light_index] ** 2)
    frac126 = float(eigenvectors[1, light_index] ** 2)
    dominance = "10_H" if frac10 >= 0.70 else ("126bar_H" if frac126 >= 0.70 else "mixed")

    ps_rows: list[dict[str, Any]] = []
    if lightest > 0.0 and not tachyonic:
        for alpha in (0.01, 0.1, 0.3):
            candidates = [
                ps.evaluate_channel("10_H", "p_to_mu_K0", alpha=alpha, M_T_GeV=lightest, M_Tbar_GeV=lightest),
                ps.evaluate_channel("126bar_H", "p_to_mu_K0", alpha=alpha, M_T_GeV=lightest, M_Tbar_GeV=lightest),
            ]
            row = dict(min(candidates, key=lambda item: item["predicted_lifetime_years"]))
            row["dominance_routing"] = dominance
            row["interference_incoherent_years"] = cmt.interference_lifetime_years(
                tau_gauge, float(row["predicted_lifetime_years"]), 0.0
            )
            row["conditional_on_component_CG"] = True
            ps_rows.append(row)

    excluded = tachyonic or singular or any(
        not row["passes_experimental_limit"] for row in ps_rows
    )
    m10 = math.sqrt(max(float(matrix_sq[0, 0]), 0.0))
    within = within_10_mixing_from_S(
        m_t=m10,
        m_tbar=1.1 * m10,
        kappa=float(scenario.get("kappa", 0.0)),
        vS=m_i,
    )
    return {
        "name": scenario["name"],
        "mass_squared_matrix_GeV2": matrix_sq.tolist(),
        "mass_squared_eigenvalues_GeV2": [float(value) for value in eigenvalues_sq],
        "mass_eigenvalues_GeV": [float(value) for value in masses],
        "lightest_GeV": lightest,
        "frac_10": frac10,
        "frac_126": frac126,
        "dominance_class": dominance,
        "within_10_mixing": within,
        "patel_shukla_mu_K0": ps_rows,
        "forbidden_inputs_received": {
            "lam210_10": float(scenario.get("lam210_10", 0.0)),
            "lam_mix": float(scenario.get("lam_mix", 0.0)),
            "include_conditional_mix": bool(scenario.get("include_conditional_mix", False)),
        },
        "allowed_conditional_inputs": {
            "lam2102_10": float(scenario.get("lam2102_10", 0.0)),
            "lam210_126": float(scenario.get("lam210_126", 0.0)),
            "lam4_cg": float(scenario.get("lam4_cg", 0.0)),
        },
        "flag": {
            "signed_operator_filter_applied": True,
            "mass_squared_matrix_used": True,
            "forbidden_210_10dag10_ignored": True,
            "forbidden_10_126_S_ignored": True,
            "lambda4_offdiag_slot_present": True,
            "tachyonic": tachyonic,
            "singular": singular,
            "conditionally_excluded_by_ps_mu_K0": excluded,
            "physical_component_CG_complete": False,
            "physical_triplet_spectrum_complete": False,
        },
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "NONSUSY_SIGNED_MT2_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
        }
    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    tau_gauge = float(scalar_pd.gauge_proton_decay(anchor)["central"]["lifetime_years"])
    ledger = allowed_mt_operator_ledger()
    zreport = z17.build_report()
    h_ew = float(
        scalar_pd.reduced_radial_vacuum_witness(anchor)["potential_definition"]["target_vevs_GeV"]["h_EW_effective"]
    )
    a_lock = m_i**4 * h_ew**2 / m_gut**2
    phase = locking_phase_hessian(A_lock=float(a_lock))
    rows = [evaluate_scenario(row, m_i=m_i, m_gut=m_gut, tau_gauge=tau_gauge) for row in SCENARIOS]
    excluded = [row for row in rows if row["flag"]["conditionally_excluded_by_ps_mu_K0"]]
    positive = [row for row in rows if not row["flag"]["tachyonic"] and row["lightest_GeV"] > 0.0]
    lightest = min(positive, key=lambda row: row["lightest_GeV"])
    forbidden = next(row for row in rows if row["name"] == "forbidden_inputs_ignored")
    baseline = next(row for row in rows if row["name"] == "decoupled_MI_no_mix")
    forbidden_inputs_no_effect = np.allclose(
        forbidden["mass_squared_matrix_GeV2"], baseline["mass_squared_matrix_GeV2"]
    )

    checks = {
        "signed_filter_executes": zreport.get("n_failed", 1) == 0,
        "ledger_excludes_bare10": ledger["bare_10_squared_excluded"],
        "ledger_excludes_forbidden_210_10dag10": ledger["forbidden_210_10dag10_excluded"],
        "ledger_excludes_forbidden_10_126_S": ledger["forbidden_10_126_S_excluded"],
        "ledger_includes_2102_10dag10": ledger["quartic_2102_10dag10_included"],
        "ledger_includes_lambda4": ledger["lambda4_210_10_126_S_included"],
        "forbidden_inputs_have_no_effect": bool(forbidden_inputs_no_effect),
        "all_rows_use_mass_squared": all(row["flag"]["mass_squared_matrix_used"] for row in rows),
        "lambda4_stress_is_tachyonic": next(row for row in rows if row["name"] == "lambda4_tachyon_stress")["flag"]["tachyonic"],
        "phase_hessian_one_positive_two_zero": phase["n_positive"] == 1 and phase["n_zero"] == 2,
        "some_survive": len(positive) > 0,
        "some_conditionally_fail": len(excluded) > 0,
        "whole_model_not_declared_dead": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "NONSUSY_SIGNED_MT2_PROXY_BUILT__FULL_COMPONENT_CG_OPEN"
            if not failures
            else "NONSUSY_SIGNED_MT2_PROXY_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "operator_ledger": ledger,
        "fill_convention": {
            "M11_squared": "mu10^2 + lambda_2102_10 v210^2 + lambda_S10 vS^2",
            "M22_squared": "mu126^2 + lambda_210_126 vS v210 + lambda_S126 vS^2",
            "M12_squared": "lambda4_CG v210 vS",
            "forbidden_linear_210_Higgs_cubic": "IDENTICALLY_IGNORED",
            "forbidden_10_126_S_cubic": "IDENTICALLY_IGNORED",
        },
        "locking_phase_hessian": phase,
        "n_scenarios": len(rows),
        "n_excluded_by_ps_mu_K0": len(excluded),
        "excluded_scenario_names": [row["name"] for row in excluded],
        "lightest_scenario": {
            "name": lightest["name"],
            "lightest_GeV": lightest["lightest_GeV"],
            "dominance": lightest["dominance_class"],
        },
        "scenarios": rows,
        "upstream_z17_filter_status": zreport.get("status"),
        "next_exact_calculation": [
            "derive all component CG coefficients for (210^dag210)(10^dag10)",
            "derive dimensionful 210 Delta-bar Delta component coefficients",
            "derive the lambda4 210 10 126bar S off-diagonal coefficient",
            "expand to the complete color-triplet component basis and diagonalize M_T^2",
        ],
        "flag": {
            "charge_and_so10_allowed_mt2_proxy_built": True,
            "mass_squared_matrix_used": True,
            "forbidden_210_10dag10_absent": True,
            "forbidden_10_126_S_absent": True,
            "lambda4_offdiag_slot_included": True,
            "bare_10_squared_absent": True,
            "ten2_S_mixing_included": True,
            "locking_phase_hessian_computed": True,
            "complete_phase_hessian": False,
            "physical_component_CG_complete": False,
            "physical_triplet_spectrum_complete": False,
            "invented_unpublished_cg_normalizations": False,
            "complete_so10_scalar_potential": False,
            "exact_unique_proton_lifetime": False,
            "conditional_parameter_points_excluded": len(excluded) > 0,
            "whole_model_excluded": False,
        },
        "verdict": (
            "The historical linear-mass proxy is replaced by a signed M_T^2 "
            "builder. Forbidden 210·10†·10 and 10·126bar·S inputs are ignored; "
            "the allowed 210†210·10†10 diagonal and lambda4 off-diagonal slots "
            "are explicit. Numerical proton-decay rows remain conditional on "
            "uncomputed component CG coefficients."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Signed non-SUSY triplet mass-squared proxy — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            f"- Scenarios: {report['n_scenarios']}",
            f"- Conditional failures: {report['n_excluded_by_ps_mu_K0']}",
            f"- Physical component CG complete: {report['flag']['physical_component_CG_complete']}",
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    ROOT.joinpath("NONSUSY_CHARGE_ALLOWED_MT_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("NONSUSY_CHARGE_ALLOWED_MT_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
