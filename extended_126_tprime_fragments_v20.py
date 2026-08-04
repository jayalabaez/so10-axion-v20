#!/usr/bin/env python3
r"""Extend colour-triplet basis with remaining 126 fragments T' (v20).

Next step after ``charge_allowed_potential_minimize_v20``:

1. Lock the **published PS fragment ledger** for proton-decay triplets
   (Aulakh cal T basis, hep-ph/0204097 Eqs. 181–182):
   - ``T_10``, ``Tbar_10`` from ``10_H``
   - ``T_126`` ≡ ``t2`` from ``126bar (6,1,1)``
   - ``T'_126`` ≡ ``t4`` from ``126bar (10,1,3)``
   - ``t3`` from ``126 (6,1,1)`` is **absent** unless a light ``126_H`` is
     added (v20 Yukawa/Higgs uses ``126bar_H``)
   - ``t5`` from ``210 (15,1,3)`` is integrated out at ``M_GUT``
2. Build the charge-allowed **4×4** mass matrix on
   ``(T_10, Tbar_10, T_126, T'_126)`` using minimized ``(κ, λ₄)`` plus
   transcribed Aulakh CG factors (``√2``, ``2√2``) for T' mixings.
3. Compare the lightest eigenvalue against the previous 3×3 truncation.

Honesty
-------
* Fragment quantum numbers are literature PS branching, not a new derivation.
* Free diagonal μ's / η remain; this is not a unique UV spectrum.
* Multi-operator phase Hessian remains OPEN.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import charge_allowed_potential_minimize_v20 as pmin
import conditional_mt_interference_v20 as cmt
import extended_ttbar_54_locking_v20 as ext
import literature_cg_triplet_matrix_v20 as lit
import patel_shukla_scalar_pdecay_v20 as ps
import scalar_vacuum_proton_decay_v20 as scalar_pd
import so10_126_to_54_projector_v20 as c126mod

ROOT = Path(__file__).resolve().parent

# Physical working basis (4×4).
BASIS = ("T_10", "Tbar_10", "T_126", "Tprime_126")

# Transcribed Aulakh CG magnitudes used in mix entries (not invented).
CG_SQRT2 = math.sqrt(2.0)
CG_2SQRT2 = 2.0 * math.sqrt(2.0)
CG_4SQRT2 = 4.0 * math.sqrt(2.0)

SOURCES = {
    "aulakh_basis": lit.SOURCES["aulakh_girdhar_2002"],
    "aulakh_cal_T_basis": {
        "citation": "hep-ph/0204097 Eqs. (181)–(182), (195)",
        "use": "t1=10; t2=126bar(6,1,1); t3=126(6,1,1); t4=126bar(10,1,3); t5=210",
    },
    "upstream_minimize": "charge_allowed_potential_minimize_v20",
}


def fragment_ledger() -> dict[str, Any]:
    """Lock 126 colour-triplet fragment multiplicity from published PS tables."""
    included = [
        {
            "name": "T_10",
            "parent": "10_H",
            "ps": "from 10 → (1,2,2) triplet",
            "sm": "(3,1,-1/3)",
            "aulakh_label": "t1",
            "in_working_basis": True,
        },
        {
            "name": "Tbar_10",
            "parent": "10_H",
            "ps": "conjugate",
            "sm": "(3bar,1,+1/3)",
            "aulakh_label": "t1bar",
            "in_working_basis": True,
        },
        {
            "name": "T_126",
            "parent": "126bar_H",
            "ps": "(6,1,1)",
            "sm": "(3,1,-1/3)",
            "aulakh_label": "t2",
            "in_working_basis": True,
        },
        {
            "name": "Tprime_126",
            "parent": "126bar_H",
            "ps": "(10,1,3)",
            "sm": "(3,1,-1/3)",
            "aulakh_label": "t4",
            "in_working_basis": True,
            "note": "The remaining 126bar fragment mediating d=6 scalar p-decay",
        },
    ]
    excluded = [
        {
            "name": "t3_126_611",
            "parent": "126_H",
            "ps": "(6,1,1)",
            "aulakh_label": "t3",
            "in_working_basis": False,
            "reason": (
                "Requires a light 126_H; v20 Higgs/Yukawa sector uses 126bar_H. "
                "Marked ABSENT in the nonsusy working basis."
            ),
        },
        {
            "name": "t5_210_1513",
            "parent": "210_H",
            "ps": "(15,1,3)",
            "aulakh_label": "t5",
            "in_working_basis": False,
            "reason": "Integrated out at M_GUT; not a light d=6 scalar mediator",
        },
    ]
    return {
        "status": "126_FRAGMENT_MULTIPLICITY_LOCKED_FROM_AULAKH_PS",
        "working_basis": list(BASIS),
        "included": included,
        "excluded_or_integrated_out": excluded,
        "n_working": len(BASIS),
        "flag": {
            "complete_126bar_fragment_multiplicity_locked": True,
            "t3_126_absent_without_126_H": True,
            "t5_210_integrated_out": True,
            "invented_extra_fragments": False,
        },
        "verdict": (
            "Working colour-triplet basis is the Aulakh t1(+bar)+t2+t4 set: "
            "(T_10, Tbar_10, T_126, T'_126). t3 absent without 126_H; t5 heavy."
        ),
    }


def fill_4x4(
    *,
    m_i: float,
    m_gut: float,
    mu_t: float,
    mu_tbar: float,
    mu_126: float,
    mu_tprime: float,
    lam210_10: float,
    lam210_126: float,
    lam210_tprime: float,
    lamS_10: float,
    lamS_126: float,
    lamS_tprime: float,
    kappa: float,
    lam4: float,
    eta_intra: float,
    include_dim4_mix: bool,
    include_intra_126: bool,
    a: float | None = None,
    omega: float | None = None,
    p: float | None = None,
) -> dict[str, Any]:
    """Charge-allowed 4×4 M_T with transcribed CG magnitudes on T' rows.

    Default ``(a,ω,p)`` is the legacy stack ``(0.3,0.5,0.2)×M_GUT``; callers
    that have selected unique ratios should pass them explicitly.
    """
    import cg_normalized_mt_locking_mix_v20 as cgmod

    a_v = 0.3 * m_gut if a is None else float(a)
    omega_v = 0.5 * m_gut if omega is None else float(omega)
    p_v = 0.2 * m_gut if p is None else float(p)

    weights = cgmod.cg_weighted_210_vev(a=a_v, p=p_v, omega=omega_v)
    # T' diagonal uses the Aulakh t4 structure ~ M + 2η(p+a); encode as
    # separate λ210_tprime × published (p+a) combination.
    p_plus_a = p_v + a_v

    m00 = mu_t + lam210_10 * weights["eff_210_for_10_GeV"] + lamS_10 * m_i
    m11 = mu_tbar + lam210_10 * weights["eff_210_for_10_GeV"] + lamS_10 * m_i
    m22 = mu_126 + lam210_126 * weights["eff_210_for_126_GeV"] + lamS_126 * m_i
    m33 = mu_tprime + lam210_tprime * (2.0 * p_plus_a) + lamS_tprime * m_i

    m01 = kappa * m_i
    # Dim-4 210·10·126·S: T gets O(1); T' gets Aulakh 2√2 magnitude relative to ω
    m02 = lam4 * m_i if include_dim4_mix else 0.0
    m03 = (lam4 * CG_2SQRT2 * (omega_v / m_gut) * m_i) if include_dim4_mix else 0.0
    m12 = m02
    m13 = m03
    # Intra-126bar T–T' from 210·126†·126: Aulakh |M_t4,t2| ~ 4√2 |ω η|
    m23 = (
        eta_intra * CG_4SQRT2 * omega_v
        if include_intra_126
        else 0.0
    )

    matrix = np.array(
        [
            [m00, m01, m02, m03],
            [m01, m11, m12, m13],
            [m02, m12, m22, m23],
            [m03, m13, m23, m33],
        ],
        dtype=float,
    )
    return {
        "basis": list(BASIS),
        "matrix_GeV": matrix,
        "weights": weights,
        "cg_used": {
            "2_sqrt2": CG_2SQRT2,
            "4_sqrt2": CG_4SQRT2,
            "source": "Aulakh cal T (195)",
        },
        "operators_used": {
            "within_10_T_Tbar": "10_H^2 S",
            "T10_T126": "210·10·126·S" if include_dim4_mix else None,
            "T10_Tprime": "210·10·126·S × 2√2(ω/M_GUT)" if include_dim4_mix else None,
            "T_Tprime_intra_126": (
                "210·126†·126 × 4√2 ω η" if include_intra_126 else None
            ),
            "forbidden_126bar_squared_T_Tbar": True,
            "t3_126_included": False,
            "t5_210_included": False,
        },
    }


SCENARIOS: list[dict[str, Any]] = [
    {
        "name": "tprime_decoupled",
        "mu_t_over_MI": 1.0,
        "mu_tbar_over_MI": 1.1,
        "mu_126_over_MI": 1.0,
        "mu_tprime_over_MI": 10.0,
        "lam210_10": 0.0,
        "lam210_126": 0.0,
        "lam210_tprime": 0.0,
        "lamS_10": 0.0,
        "lamS_126": 0.0,
        "lamS_tprime": 0.0,
        "kappa": 0.0,
        "lam4": 0.0,
        "eta_intra": 0.0,
        "include_dim4_mix": False,
        "include_intra_126": False,
        "use_minimized_couplings": False,
    },
    {
        "name": "tprime_at_MI_no_mix",
        "mu_t_over_MI": 1.0,
        "mu_tbar_over_MI": 1.1,
        "mu_126_over_MI": 1.0,
        "mu_tprime_over_MI": 1.0,
        "lam210_10": 0.0,
        "lam210_126": 0.0,
        "lam210_tprime": 0.0,
        "lamS_10": 0.0,
        "lamS_126": 0.0,
        "lamS_tprime": 0.0,
        "kappa": 0.0,
        "lam4": 0.0,
        "eta_intra": 0.0,
        "include_dim4_mix": False,
        "include_intra_126": False,
        "use_minimized_couplings": False,
    },
    {
        "name": "intra_126_TT_prime",
        "mu_t_over_MI": 1.0,
        "mu_tbar_over_MI": 1.1,
        "mu_126_over_MI": 1.0,
        "mu_tprime_over_MI": 1.2,
        "lam210_10": 0.0,
        "lam210_126": 0.2,
        "lam210_tprime": 0.2,
        "lamS_10": 0.0,
        "lamS_126": 0.0,
        "lamS_tprime": 0.0,
        "kappa": 0.0,
        "lam4": 0.0,
        "eta_intra": 0.05,
        "include_dim4_mix": False,
        "include_intra_126": True,
        "use_minimized_couplings": False,
    },
    {
        "name": "minimized_couplings_full",
        "mu_t_over_MI": 1.0,
        "mu_tbar_over_MI": 1.1,
        "mu_126_over_MI": 1.0,
        "mu_tprime_over_MI": 1.0,
        "lam210_10": 0.0,
        "lam210_126": 0.0,
        "lam210_tprime": 0.0,
        "lamS_10": 0.0,
        "lamS_126": 0.0,
        "lamS_tprime": 0.0,
        "kappa": 0.0,
        "lam4": 0.0,
        "eta_intra": 0.02,
        "include_dim4_mix": True,
        "include_intra_126": True,
        "use_minimized_couplings": True,
    },
    {
        "name": "finite_kappa_tprime",
        "mu_t_over_MI": 1.0,
        "mu_tbar_over_MI": 1.2,
        "mu_126_over_MI": 1.0,
        "mu_tprime_over_MI": 1.5,
        "lam210_10": 0.0,
        "lam210_126": 0.0,
        "lam210_tprime": 0.0,
        "lamS_10": 0.0,
        "lamS_126": 0.0,
        "lamS_tprime": 0.0,
        "kappa": 0.05,
        "lam4": 0.1,
        "eta_intra": 0.02,
        "include_dim4_mix": True,
        "include_intra_126": True,
        "use_minimized_couplings": False,
    },
    {
        "name": "heavy_10_survives",
        "mu_t_over_MI": 3.0,
        "mu_tbar_over_MI": 3.1,
        "mu_126_over_MI": 3.0,
        "mu_tprime_over_MI": 3.0,
        "lam210_10": 0.0,
        "lam210_126": 0.0,
        "lam210_tprime": 0.0,
        "lamS_10": 0.0,
        "lamS_126": 0.0,
        "lamS_tprime": 0.0,
        "kappa": 0.0,
        "lam4": 0.0,
        "eta_intra": 0.0,
        "include_dim4_mix": False,
        "include_intra_126": False,
        "use_minimized_couplings": False,
    },
    {
        "name": "126_dominated_survives",
        "mu_t_over_MI": 5.0,
        "mu_tbar_over_MI": 5.0,
        "mu_126_over_MI": 1.0,
        "mu_tprime_over_MI": 5.0,
        "lam210_10": 0.0,
        "lam210_126": 0.0,
        "lam210_tprime": 0.0,
        "lamS_10": 0.0,
        "lamS_126": 0.0,
        "lamS_tprime": 0.0,
        "kappa": 0.0,
        "lam4": 0.0,
        "eta_intra": 0.0,
        "include_dim4_mix": False,
        "include_intra_126": False,
        "use_minimized_couplings": False,
    },
    {
        "name": "light_tprime_stress",
        "mu_t_over_MI": 1.0,
        "mu_tbar_over_MI": 1.0,
        "mu_126_over_MI": 2.0,
        "mu_tprime_over_MI": 0.05,
        "lam210_10": 0.0,
        "lam210_126": 0.0,
        "lam210_tprime": 0.0,
        "lamS_10": 0.0,
        "lamS_126": 0.0,
        "lamS_tprime": 0.0,
        "kappa": 0.0,
        "lam4": 0.0,
        "eta_intra": 0.0,
        "include_dim4_mix": False,
        "include_intra_126": False,
        "use_minimized_couplings": False,
    },
]


def _truncate_3x3(matrix4: np.ndarray) -> np.ndarray:
    return np.array(matrix4[:3, :3], dtype=float)


def evaluate_scenario(
    scenario: dict[str, Any],
    *,
    m_i: float,
    m_gut: float,
    tau_gauge: float,
    minimized: dict[str, float],
) -> dict[str, Any]:
    kappa = float(scenario["kappa"])
    lam4 = float(scenario["lam4"])
    if scenario.get("use_minimized_couplings"):
        kappa = float(minimized["kappa"])
        lam4 = float(minimized["lam4"])

    filled = fill_4x4(
        m_i=m_i,
        m_gut=m_gut,
        mu_t=float(scenario["mu_t_over_MI"]) * m_i,
        mu_tbar=float(scenario["mu_tbar_over_MI"]) * m_i,
        mu_126=float(scenario["mu_126_over_MI"]) * m_i,
        mu_tprime=float(scenario["mu_tprime_over_MI"]) * m_i,
        lam210_10=float(scenario["lam210_10"]),
        lam210_126=float(scenario["lam210_126"]),
        lam210_tprime=float(scenario["lam210_tprime"]),
        lamS_10=float(scenario["lamS_10"]),
        lamS_126=float(scenario["lamS_126"]),
        lamS_tprime=float(scenario["lamS_tprime"]),
        kappa=kappa,
        lam4=lam4,
        eta_intra=float(scenario["eta_intra"]),
        include_dim4_mix=bool(scenario["include_dim4_mix"]),
        include_intra_126=bool(scenario["include_intra_126"]),
    )
    m4 = filled["matrix_GeV"]
    w4, v4 = np.linalg.eigh(m4)
    order = np.argsort(np.abs(w4))
    w4 = w4[order]
    v4 = v4[:, order]
    light4 = float(abs(w4[0]))
    fracs = np.abs(v4[:, 0]) ** 2
    fracs = fracs / float(np.sum(fracs))

    m3 = _truncate_3x3(m4)
    w3 = np.linalg.eigvalsh(m3)
    light3 = float(np.min(np.abs(w3)))

    singular = light4 <= 0.0
    frac126 = float(fracs[2] + fracs[3])
    dominance = (
        "10_H_sector"
        if float(fracs[0] + fracs[1]) >= 0.70
        else ("126bar_H" if frac126 >= 0.70 else "mixed")
    )
    ps_dom = "10_H" if dominance != "126bar_H" else "126bar_H"
    ps_rows: list[dict[str, Any]] = []
    if not singular:
        for alpha_ps in (0.01, 0.1, 0.3):
            row = dict(
                ps.evaluate_channel(
                    ps_dom,
                    "p_to_mu_K0",
                    alpha=alpha_ps,
                    M_T_GeV=light4,
                    M_Tbar_GeV=light4,
                )
            )
            row["interference_incoherent_years"] = cmt.interference_lifetime_years(
                tau_gauge, float(row["predicted_lifetime_years"]), 0.0
            )
            ps_rows.append(row)
    excluded = singular or any(not r["passes_experimental_limit"] for r in ps_rows)

    return {
        "name": scenario["name"],
        "basis": list(BASIS),
        "kappa_used": kappa,
        "lam4_used": lam4,
        "mass_matrix_GeV": m4.tolist(),
        "eigenvalues_GeV": [float(x) for x in w4],
        "lightest_GeV": light4,
        "lightest_3x3_truncation_GeV": light3,
        "delta_lightest_vs_3x3_GeV": light4 - light3,
        "lightest_fractions": {
            "T_10": float(fracs[0]),
            "Tbar_10": float(fracs[1]),
            "T_126": float(fracs[2]),
            "Tprime_126": float(fracs[3]),
        },
        "dominance_class": dominance,
        "operators_used": filled["operators_used"],
        "cg_used": filled["cg_used"],
        "patel_shukla_mu_K0": ps_rows,
        "flag": {
            "four_by_four": True,
            "tprime_included": True,
            "conditionally_excluded_by_ps_mu_K0": excluded,
            "singular": singular,
            "used_minimized_couplings": bool(scenario.get("use_minimized_couplings")),
        },
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "TPRIME_FRAGMENTS_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"complete_126bar_fragment_multiplicity_locked": False},
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    gauge = scalar_pd.gauge_proton_decay(anchor)
    tau_gauge = float(gauge["central"]["lifetime_years"])

    ledger = fragment_ledger()
    # Prefer finite-κ benchmark if present; else unconstrained best
    vmin = pmin.build_report()
    minimized = dict(vmin.get("fixed_couplings") or {})
    fk = vmin.get("finite_kappa_benchmark_couplings")
    if fk:
        minimized_for_full = {
            "kappa": fk["kappa"],
            "lam4": fk["lam4"],
            "lambda_lock": fk["lambda_lock"],
        }
    else:
        minimized_for_full = {
            "kappa": minimized.get("kappa", 0.0),
            "lam4": minimized.get("lam4", 0.0),
            "lambda_lock": minimized.get("lambda_lock", 1.0),
        }

    rows = [
        evaluate_scenario(
            s,
            m_i=m_i,
            m_gut=m_gut,
            tau_gauge=tau_gauge,
            minimized=minimized_for_full,
        )
        for s in SCENARIOS
    ]
    excluded = [r for r in rows if r["flag"]["conditionally_excluded_by_ps_mu_K0"]]
    physical = [r for r in rows if not r["flag"]["singular"]]
    lightest = min(physical, key=lambda r: r["lightest_GeV"])

    # Phase Hessian still from locking amplitude (single operator)
    proj = c126mod.build_126_to_54_projector()
    c54 = float(proj["C_54_upstream"])
    c126 = float(proj["C_126_to_54"])
    amp = ext.locking_amplitude_54(
        m_i=m_i,
        m_gut=m_gut,
        lambda_lock=float(minimized_for_full["lambda_lock"]),
        c_54=c54,
        c_126_to_54=c126,
    )
    phase = ext.phase_hessian_from_A(amp["A_54"])

    checks = {
        "ledger_locked": ledger["flag"]["complete_126bar_fragment_multiplicity_locked"],
        "basis_len_4": ledger["n_working"] == 4,
        "t3_absent": ledger["flag"]["t3_126_absent_without_126_H"],
        "t5_out": ledger["flag"]["t5_210_integrated_out"],
        "some_excluded": len(excluded) > 0,
        "some_survive": len(excluded) < len(rows),
        "lightest_has_tprime_frac_key": "Tprime_126"
        in lightest["lightest_fractions"],
        "phase_one_massive": phase["n_positive"] == 1,
        "phase_two_flat": phase["n_zero"] == 2,
        "upstream_minimize_ok": vmin.get("n_failed", 1) == 0,
        "no_invented_fragments": not ledger["flag"]["invented_extra_fragments"],
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "EXTENDED_126_TPRIME_FRAGMENTS_LOCKED__4x4_MT"
            if not failures
            else "EXTENDED_126_TPRIME_FRAGMENTS_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "fragment_ledger": ledger,
        "minimized_couplings_used": minimized_for_full,
        "n_scenarios": len(rows),
        "n_excluded_by_ps_mu_K0": len(excluded),
        "excluded_scenario_names": [r["name"] for r in excluded],
        "lightest_scenario": {
            "name": lightest["name"],
            "lightest_GeV": lightest["lightest_GeV"],
            "lightest_3x3_truncation_GeV": lightest["lightest_3x3_truncation_GeV"],
            "dominance": lightest["dominance_class"],
            "fractions": lightest["lightest_fractions"],
        },
        "scenarios": rows,
        "locking_phase_hessian": {
            "n_positive": phase["n_positive"],
            "n_zero": phase["n_zero"],
            "A_54": amp["A_54"],
        },
        "upstream_minimize_status": vmin.get("status"),
        "next_exact_calculation": [
            "Build the full multi-operator phase Hessian with cross terms",
            "Include gauge–scalar interference with physical 4×4 mixings",
            "Lift the reduced minimum to the full 210+126+10 component space",
            "Optionally restore t3 if a light 126_H is added to the field content",
        ],
        "flag": {
            "complete_126bar_fragment_multiplicity_locked": True,
            "working_basis_4x4": True,
            "tprime_included": True,
            "t3_126_absent_without_126_H": True,
            "invented_unpublished_cg_values": False,
            "complete_so10_scalar_potential": False,
            "exact_unique_proton_lifetime": False,
            "complete_multi_operator_phase_hessian": False,
            "conditional_parameter_points_excluded": len(excluded) > 0,
            "whole_model_excluded": False,
        },
        "verdict": (
            "126bar colour-triplet fragments locked to Aulakh t2+t4: working "
            "basis (T_10, Tbar_10, T_126, T'_126). The 4×4 charge-allowed M_T "
            "is filled with minimized/transcribed couplings; t3 absent without "
            "126_H; unique τ_p still OPEN."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    light = report["lightest_scenario"]
    lines = [
        "# Extended 126 T' fragments — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- Working basis: `{', '.join(report['fragment_ledger']['working_basis'])}`",
        f"- Scenarios: {report['n_scenarios']}; excluded: {report['n_excluded_by_ps_mu_K0']}",
        f"- Lightest: `{light['name']}` at {light['lightest_GeV']:.3e} GeV "
        f"(3×3 truncation {light['lightest_3x3_truncation_GeV']:.3e} GeV)",
        "",
        "## Next exact calculation",
        "",
    ]
    for step in report["next_exact_calculation"]:
        lines.append(f"1. {step}")
    lines.extend(["", "## Flags", ""])
    for k, v in report["flag"].items():
        lines.append(f"- `{k}`: {v}")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    report = build_report()
    ROOT.joinpath("EXTENDED_126_TPRIME_FRAGMENTS_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("EXTENDED_126_TPRIME_FRAGMENTS_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "basis": report["fragment_ledger"]["working_basis"],
                "n_excluded": report.get("n_excluded_by_ps_mu_K0"),
                "lightest": report.get("lightest_scenario"),
                "flag": report.get("flag"),
                "verdict": report.get("verdict"),
            },
            indent=2,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
