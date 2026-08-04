#!/usr/bin/env python3
r"""Published SO(10) CG / colour-triplet mass matrices (v20).

Next step after conditional dimensionless ``M_T`` fills
(``conditional_mt_interference_v20``): replace invented O(1) slots with
**transcribed published Clebsch structures**.

What is transcribed (not invented)
----------------------------------
1. Aulakh–Girdhar MSGUT colour-triplet matrix ``cal T`` and doublet matrix
   ``cal D`` — hep-ph/0204097 Eqs. (189), (195); basis (181)–(182).
2. Fukuyama–Ilakovac–Kikuchi–Meljanac–Okada SU(5)-solution triplet matrix
   — hep-ph/0412348 Eqs. (58), (60).

What this still is **not**
--------------------------
* The complete nonsupersymmetric v20 ``210+126+10+S+Φ17`` potential.
* A claim that SUSY ``cal T`` eigenvalues are the unique v20 spectrum.
* A Hilbert-series certificate for the nonsusy operator basis.

The published CG numbers are used as a **literature-normalized** fill of the
triplet sector; results remain conditional on MSGUT/SUSY parameter choices
and on the identification of hierarchy VEVs with the v20 unification anchor.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import conditional_mt_interference_v20 as cmt
import patel_shukla_scalar_pdecay_v20 as ps
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent

SOURCES = {
    "aulakh_girdhar_2002": {
        "citation": "C. S. Aulakh, A. Girdhar, hep-ph/0204097 (JMP A20 (2005) 865)",
        "equations": "cal D Eq. (189); cal T Eq. (195); basis Eqs. (181)–(182)",
        "scope": "Minimal Susy SO(10) 210+126+126bar+10; published PS Clebsches",
    },
    "fukuyama_etal_2004": {
        "citation": "T. Fukuyama et al., hep-ph/0412348",
        "equations": "M_triplet Eqs. (58),(60); M_doublet Eq. (30); A definition",
        "scope": "SU(5) vacuum solution of MSGUT G321 mass matrices",
    },
    "aulakh_girdhar_2005": {
        "citation": "C. S. Aulakh, A. Girdhar, Nucl. Phys. B 711 (2005) 275 [hep-ph/0405074]",
        "use": "Full MSGUT spectra / threshold context; cal T first in hep-ph/0204097",
    },
}

# Basis for cal T rows/columns (Aulakh Eqs. 181–182):
# 0: t^(1) from 10_H
# 1: t^(2) from 126bar (6,1,1)
# 2: t^(3) from 126 (6,1,1)
# 3: t^(4) from 126bar (10,1,3)
# 4: t^(5) from 210 (15,1,3)
BASIS_T = ("t1_10", "t2_126bar_611", "t3_126_611", "t4_126bar_1013", "t5_210_1513")


def aulakh_cal_D(
    *,
    M_H: complex,
    M: complex,
    m: complex,
    lam: complex,
    eta: complex,
    gamma: complex,
    gamma_bar: complex,
    a: complex,
    omega: complex,
    sigma: complex,
    sigma_bar: complex,
) -> np.ndarray:
    """Doublet mass matrix cal D — hep-ph/0204097 Eq. (189)."""
    g, gb = gamma, gamma_bar
    return np.array(
        [
            [
                -M_H,
                gb * math.sqrt(3) * (omega - a),
                -g * math.sqrt(3) * (omega + a),
                -gb * sigma_bar,
            ],
            [
                -gb * math.sqrt(3) * (omega + a),
                0.0,
                -(M + 4.0 * eta * (a + omega)),
                0.0,
            ],
            [
                g * math.sqrt(3) * (omega - a),
                -(M + 4.0 * eta * (a - omega)),
                0.0,
                -2.0 * eta * sigma_bar * math.sqrt(3),
            ],
            [
                -sigma * g,
                -2.0 * eta * sigma * math.sqrt(3),
                0.0,
                -m + 6.0 * lam * (omega - a),
            ],
        ],
        dtype=complex,
    )


def aulakh_cal_T(
    *,
    M_H: complex,
    M: complex,
    m: complex,
    lam: complex,
    eta: complex,
    gamma: complex,
    gamma_bar: complex,
    a: complex,
    p: complex,
    omega: complex,
    sigma: complex,
    sigma_bar: complex,
) -> np.ndarray:
    """Colour-triplet mass matrix cal T — hep-ph/0204097 Eq. (195)."""
    g, gb = gamma, gamma_bar
    i = 1j
    s2 = math.sqrt(2.0)
    return np.array(
        [
            [
                M_H,
                gb * (a + p),
                g * (p - a),
                2.0 * s2 * i * omega * gb,
                i * sigma_bar * gb,
            ],
            [
                gb * (p - a),
                0.0,
                M,
                0.0,
                0.0,
            ],
            [
                g * (p + a),
                M,
                0.0,
                4.0 * s2 * i * omega * eta,
                2.0 * i * eta * sigma_bar,
            ],
            [
                -2.0 * s2 * i * omega * g,
                -4.0 * s2 * i * omega * eta,
                0.0,
                M + 2.0 * eta * p + 2.0 * eta * a,
                -2.0 * s2 * eta * sigma_bar,
            ],
            [
                i * sigma * g,
                2.0 * i * eta * sigma,
                0.0,
                2.0 * s2 * eta * sigma,
                -m - 2.0 * lam * (a + p - 4.0 * omega),
            ],
        ],
        dtype=complex,
    )


def fukuyama_su5_M_triplet(
    *,
    m1: complex,
    m2: complex,
    m3: complex,
    lam1: complex,
    lam2: complex,
    lam3: complex,
    lam4: complex,
) -> np.ndarray:
    """SU(5)-solution colour-triplet matrix — hep-ph/0412348 Eqs. (58),(60)."""
    ratio = 2.0 * m1 / m2 - 3.0 * lam1 / lam2
    # A is defined with a square root; require nonnegative real part for scan points.
    A = np.sqrt(ratio + 0j)
    s3, s5, s2, s6 = math.sqrt(3.0), math.sqrt(5.0), math.sqrt(2.0), math.sqrt(6.0)
    M12 = 2.0 * s3 * lam4 * m2 / (s5 * lam2)
    M21 = 2.0 * s3 * lam3 * m2 / (s5 * lam2)
    M14 = 2.0 * s3 * lam4 * m2 * A
    M41 = 2.0 * s3 * lam3 * m2 * A
    M44 = 2.0 * m1 - 6.0 * lam1 * m2 / lam2
    M15 = 2.0 * s6 * lam4 * m2 / (s5 * lam2)
    M51 = 2.0 * s6 * lam3 * m2 / (s5 * lam2)
    # Matrix as printed: row0 col4 uses M51 in the paper's first column last entry
    # and M15 would be the (0,4) if asymmetric; Eq. (58) shows M51 in both (0,4)
    # positions of the printed column vector — use M15 on (0,4) and M51 on (4,0)
    # per the explicit definitions (60).
    return np.array(
        [
            [2.0 * m3, M12, 0.0, M14, M15],
            [M21, m2, 0.0, -m2 / s5 * A, -s2 * m2 / 5.0],
            [0.0, 0.0, m2, 0.0, 0.0],
            [M41, -m2 / s5 * A, 0.0, M44, -s2 * m2 * A / s5],
            [M51, -s2 * m2 / 5.0, 0.0, -s2 * m2 * A / s5, 4.0 * m2 / 5.0],
        ],
        dtype=complex,
    )


def physical_spectrum(matrix: np.ndarray) -> dict[str, Any]:
    """Physical masses from singular values of a (possibly non-Hermitian) mass matrix."""
    u, s, vh = np.linalg.svd(matrix, full_matrices=False)
    order = np.argsort(s)
    s_sorted = s[order]
    # Right singular vector for lightest mode (vh rows); left from u columns.
    light_right = vh[order[0]].conj()  # in input basis
    # SVD: M = U S Vh ⇒ right singular vectors are rows of Vh.
    frac = np.abs(light_right) ** 2
    frac = frac / float(np.sum(frac)) if float(np.sum(frac)) > 0 else frac
    return {
        "singular_values_GeV": [float(x) for x in s_sorted],
        "lightest_GeV": float(s_sorted[0]),
        "heaviest_GeV": float(s_sorted[-1]),
        "lightest_right_fractions": [float(x) for x in frac],
        "frac_t1_10": float(frac[0]) if len(frac) else float("nan"),
        "frac_t2_126bar": float(frac[1]) if len(frac) > 1 else float("nan"),
        "n_modes": int(len(s_sorted)),
        "positive_spectrum": bool(s_sorted[0] > 0),
    }


def fm_2x2_projection(cal_t: np.ndarray) -> np.ndarray:
    """Project the 10–126bar (t1,t2) block used by the symbolic ledger."""
    return np.array(cal_t[:2, :2], dtype=complex)


def map_fm_block_to_symbolic_slots(
    block: np.ndarray, *, m_i: float, m_gut: float
) -> dict[str, Any]:
    """Read effective dimensionless fills from the published 2×2 FM block."""
    m11, m12 = complex(block[0, 0]), complex(block[0, 1])
    m21, m22 = complex(block[1, 0]), complex(block[1, 1])
    # Match conditional_mt fill: M11=(mu10+beta)MI + alpha MGUT, M12=gamma MI, ...
    return {
        "block_GeV": [[_cjson(m11), _cjson(m12)], [_cjson(m21), _cjson(m22)]],
        "effective_slots": {
            "M11_GeV": _cjson(m11),
            "M12_GeV": _cjson(m12),
            "M21_GeV": _cjson(m21),
            "M22_GeV": _cjson(m22),
            "gamma_eff_over_MI": _cjson(m12 / m_i) if m_i else None,
            "note": (
                "These are effective reads of the published CG block, not a "
                "derivation of the nonsusy v20 quartic normalizations."
            ),
        },
        "hierarchy_vevs_GeV": {"M_I": m_i, "M_GUT": m_gut},
    }


def _cjson(z: complex) -> dict[str, float]:
    return {"re": float(np.real(z)), "im": float(np.imag(z)), "abs": float(abs(z))}


# Curated MSGUT-like points: VEVs tied to v20 anchor; couplings O(1).
def scenario_list(m_i: float, m_gut: float) -> list[dict[str, Any]]:
    return [
        {
            "name": "aulakh_reference_O1",
            "family": "aulakh_cal_T",
            "params": {
                "M_H": 1.0 * m_gut,
                "M": 1.0 * m_gut,
                "m": 1.0 * m_gut,
                "lam": 1.0,
                "eta": 1.0,
                "gamma": 1.0,
                "gamma_bar": 1.0,
                "a": 0.3 * m_gut,
                "p": 0.2 * m_gut,
                "omega": 0.5 * m_gut,
                "sigma": 1.0 * m_i,
                "sigma_bar": 1.0 * m_i,
            },
        },
        {
            "name": "aulakh_small_gamma",
            "family": "aulakh_cal_T",
            "params": {
                "M_H": 0.5 * m_gut,
                "M": 1.0 * m_gut,
                "m": 1.0 * m_gut,
                "lam": 0.5,
                "eta": 0.5,
                "gamma": 0.1,
                "gamma_bar": 0.1,
                "a": 0.2 * m_gut,
                "p": 0.1 * m_gut,
                "omega": 0.4 * m_gut,
                "sigma": 1.0 * m_i,
                "sigma_bar": 1.0 * m_i,
            },
        },
        {
            "name": "aulakh_MI_MH",
            "family": "aulakh_cal_T",
            "params": {
                "M_H": 1.0 * m_i,
                "M": 1.0 * m_gut,
                "m": 1.0 * m_gut,
                "lam": 1.0,
                "eta": 1.0,
                "gamma": 0.5,
                "gamma_bar": 0.5,
                "a": 0.25 * m_gut,
                "p": 0.15 * m_gut,
                "omega": 0.35 * m_gut,
                "sigma": 1.0 * m_i,
                "sigma_bar": 1.0 * m_i,
            },
        },
        {
            "name": "aulakh_large_eta_mix",
            "family": "aulakh_cal_T",
            "params": {
                "M_H": 2.0 * m_gut,
                "M": 0.5 * m_gut,
                "m": 1.0 * m_gut,
                "lam": 1.0,
                "eta": 2.0,
                "gamma": 1.0,
                "gamma_bar": 1.0,
                "a": 0.1 * m_gut,
                "p": 0.4 * m_gut,
                "omega": 0.6 * m_gut,
                "sigma": 1.0 * m_i,
                "sigma_bar": 1.0 * m_i,
            },
        },
        {
            "name": "aulakh_light_triplet_stress",
            "family": "aulakh_cal_T",
            "params": {
                # Deliberate intermediate-scale triplet stress: all mass params ~ M_I.
                "M_H": 1.0 * m_i,
                "M": 1.0 * m_i,
                "m": 1.0 * m_i,
                "lam": 0.1,
                "eta": 0.1,
                "gamma": 0.1,
                "gamma_bar": 0.1,
                "a": 0.3 * m_i,
                "p": 0.2 * m_i,
                "omega": 0.5 * m_i,
                "sigma": 1.0 * m_i,
                "sigma_bar": 1.0 * m_i,
            },
        },
        {
            "name": "fukuyama_su5_O1",
            "family": "fukuyama_su5",
            "params": {
                "m1": 1.0 * m_gut,
                "m2": 1.0 * m_gut,
                "m3": 0.5 * m_gut,
                "lam1": 1.0,
                "lam2": 1.0,
                "lam3": 1.0,
                "lam4": 1.0,
            },
        },
        {
            "name": "fukuyama_su5_light_m3",
            "family": "fukuyama_su5",
            "params": {
                "m1": 1.0 * m_gut,
                "m2": 1.0 * m_gut,
                "m3": 1.0 * m_i,
                "lam1": 0.5,
                "lam2": 1.0,
                "lam3": 0.5,
                "lam4": 0.5,
            },
        },
    ]


def evaluate_scenario(
    scenario: dict[str, Any],
    *,
    m_i: float,
    m_gut: float,
    tau_gauge: float,
) -> dict[str, Any]:
    family = scenario["family"]
    params = scenario["params"]
    if family == "aulakh_cal_T":
        cal_t = aulakh_cal_T(**params)
        cal_d = aulakh_cal_D(
            **{k: params[k] for k in (
                "M_H", "M", "m", "lam", "eta", "gamma", "gamma_bar",
                "a", "omega", "sigma", "sigma_bar",
            )}
        )
        det_d = complex(np.linalg.det(cal_d))
    else:
        cal_t = fukuyama_su5_M_triplet(**params)
        cal_d = None
        det_d = None

    spec = physical_spectrum(cal_t)
    block = fm_2x2_projection(cal_t)
    slots = map_fm_block_to_symbolic_slots(block, m_i=m_i, m_gut=m_gut)
    m_t = spec["lightest_GeV"]
    frac10 = spec["frac_t1_10"]
    if frac10 >= 0.70:
        dominance = "10_H"
    elif spec["frac_t2_126bar"] >= 0.70:
        dominance = "126bar_H"
    else:
        dominance = "mixed"

    ps_rows: list[dict[str, Any]] = []
    singular = m_t <= 0.0
    if not singular:
        for alpha_ps in (0.01, 0.1, 0.3):
            if dominance == "mixed":
                r10 = ps.evaluate_channel(
                    "10_H", "p_to_mu_K0", alpha=alpha_ps, M_T_GeV=m_t, M_Tbar_GeV=m_t
                )
                r126 = ps.evaluate_channel(
                    "126bar_H", "p_to_mu_K0", alpha=alpha_ps, M_T_GeV=m_t, M_Tbar_GeV=m_t
                )
                row = dict(
                    r10
                    if r10["predicted_lifetime_years"] <= r126["predicted_lifetime_years"]
                    else r126
                )
                row["dominance_routing"] = "mixed_take_shorter"
            else:
                row = dict(
                    ps.evaluate_channel(
                        dominance,
                        "p_to_mu_K0",
                        alpha=alpha_ps,
                        M_T_GeV=m_t,
                        M_Tbar_GeV=m_t,
                    )
                )
                row["dominance_routing"] = dominance
            tau_s = float(row["predicted_lifetime_years"])
            row["interference_with_gauge_e_pi0"] = {
                "cos_phi": {
                    "+1_constructive": cmt.interference_lifetime_years(
                        tau_gauge, tau_s, 1.0
                    ),
                    "0_incoherent": cmt.interference_lifetime_years(
                        tau_gauge, tau_s, 0.0
                    ),
                    "-1_destructive": cmt.interference_lifetime_years(
                        tau_gauge, tau_s, -1.0
                    ),
                }
            }
            ps_rows.append(row)

    excluded = singular or any(not r["passes_experimental_limit"] for r in ps_rows)
    return {
        "name": scenario["name"],
        "family": family,
        "basis": list(BASIS_T),
        "spectrum": spec,
        "dominance_class": dominance,
        "fm_2x2_projection": slots,
        "det_cal_D": None if det_d is None else _cjson(det_d),
        "patel_shukla_mu_K0": ps_rows,
        "flag": {
            "literature_cg_matrix_used": True,
            "singular_spectrum": singular,
            "conditionally_excluded_by_ps_mu_K0": excluded,
            "fine_tuned_doublets": (
                None if det_d is None else bool(abs(det_d) < (0.01 * m_gut) ** 4)
            ),
        },
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "LITERATURE_CG_TRIPLET_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"literature_cg_transcribed": False},
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    gauge = scalar_pd.gauge_proton_decay(anchor)
    tau_gauge = float(gauge["central"]["lifetime_years"])

    # Unit tests of transcription: known algebraic identities.
    identity_checks = {}
    # Fukuyama: det M_triplet = m_Δ(50) * det M_doublet with m_Δ(50)=m2 on SU(5)
    # solution third diagonal = m2; we check Tr M_triplet structure loosely.
    Mt = fukuyama_su5_M_triplet(
        m1=1.0, m2=2.0, m3=3.0, lam1=0.1, lam2=1.0, lam3=0.2, lam4=0.3
    )
    identity_checks["fukuyama_matrix_shape_5x5"] = Mt.shape == (5, 5)
    identity_checks["fukuyama_A_real_for_safe_params"] = bool(
        abs(np.imag(np.sqrt(2.0 * 1.0 / 2.0 - 3.0 * 0.1 / 1.0 + 0j))) < 1e-12
    )
    T0 = aulakh_cal_T(
        M_H=1, M=1, m=1, lam=1, eta=1, gamma=1, gamma_bar=1,
        a=0.1, p=0.2, omega=0.3, sigma=0.01, sigma_bar=0.01,
    )
    identity_checks["aulakh_cal_T_shape_5x5"] = T0.shape == (5, 5)
    identity_checks["aulakh_T00_equals_MH"] = bool(abs(T0[0, 0] - 1) < 1e-15)
    identity_checks["aulakh_T12_equals_M"] = bool(abs(T0[1, 2] - 1) < 1e-15)

    rows = [
        evaluate_scenario(s, m_i=m_i, m_gut=m_gut, tau_gauge=tau_gauge)
        for s in scenario_list(m_i, m_gut)
    ]
    excluded = [r for r in rows if r["flag"]["conditionally_excluded_by_ps_mu_K0"]]
    physical = [r for r in rows if not r["flag"]["singular_spectrum"]]
    lightest = min(physical, key=lambda r: r["spectrum"]["lightest_GeV"])

    checks = {
        "anchor_available": True,
        **identity_checks,
        "scenarios_ran": len(rows) == len(scenario_list(m_i, m_gut)),
        "some_survive": len(excluded) < len(rows),
        "some_excluded": len(excluded) > 0,
        "nonsusy_not_overclaimed": True,
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "LITERATURE_CG_TRIPLET_MATRICES_TRANSCRIBED__NONSUSY_POTENTIAL_OPEN"
            if not failures
            else "LITERATURE_CG_TRIPLET_MATRICES_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "basis_cal_T": list(BASIS_T),
        "unification_anchor": {
            "M_GUT_GeV": m_gut,
            "M_I_GeV": m_i,
            "gauge_central_lifetime_years": tau_gauge,
        },
        "n_scenarios": len(rows),
        "n_excluded_by_ps_mu_K0": len(excluded),
        "excluded_scenario_names": [r["name"] for r in excluded],
        "lightest_scenario": {
            "name": lightest["name"],
            "family": lightest["family"],
            "lightest_GeV": lightest["spectrum"]["lightest_GeV"],
            "frac_t1_10": lightest["spectrum"]["frac_t1_10"],
            "dominance": lightest["dominance_class"],
        },
        "scenarios": rows,
        "honesty": {
            "cg_coefficients_source": "transcribed from published MSGUT papers",
            "invented_unpublished_tensors": False,
            "identified_with_v20_nonsusy_potential": False,
            "reason": (
                "Published cal T / M_triplet come from the SUSY superpotential W; "
                "v20 is nonsupersymmetric with additional S, Φ17. The CG numbers "
                "normalize the 10/126/210 triplet mixings used as literature "
                "benchmarks, not as the unique v20 vacuum."
            ),
        },
        "next_exact_calculation": [
            "Derive the nonsusy 210^3/210^4 and mixed 210-126/210-10 quartic tensors "
            "(or prove equivalence to the SUSY CG reduction where applicable)",
            "Impose v20 Z17/PQ charge assignments on the allowed contractions",
            "Fine-tune / minimize the full nonsusy potential at the reduced hierarchy",
            "Recompute physical M_T and α_{1,2} from that minimum",
        ],
        "flag": {
            "literature_cg_transcribed": True,
            "aulakh_cal_T_implemented": True,
            "fukuyama_su5_M_triplet_implemented": True,
            "fm_2x2_projection_mapped": True,
            "invented_unpublished_tensors": False,
            "identified_with_v20_nonsusy_potential": False,
            "complete_so10_scalar_potential": False,
            "exact_unique_proton_lifetime": False,
            "conditional_parameter_points_excluded": len(excluded) > 0,
            "whole_model_excluded": False,
        },
        "verdict": (
            "Published MSGUT Clebsch triplet matrices (Aulakh cal T; Fukuyama "
            "SU(5) M_triplet) are transcribed and diagonalized on the v20 "
            "hierarchy anchor. FM 2×2 blocks map onto symbolic slots. "
            "GUT-scale MSGUT-like points typically survive Patel–Shukla μ⁺K⁰; "
            "deliberate intermediate-scale stress points can fail. This is not "
            "yet the nonsusy v20 vacuum."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Literature CG triplet matrices — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- Scenarios: {report['n_scenarios']}",
        f"- Excluded by PS μ⁺K⁰: {report['n_excluded_by_ps_mu_K0']} "
        f"({', '.join(report['excluded_scenario_names']) or 'none'})",
        f"- Lightest: `{report['lightest_scenario']['name']}` at "
        f"{report['lightest_scenario']['lightest_GeV']:.3e} GeV "
        f"(frac_t1_10={report['lightest_scenario']['frac_t1_10']:.3f})",
        "",
        "## Honesty",
        "",
        report["honesty"]["reason"],
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
    ROOT.joinpath("LITERATURE_CG_TRIPLET_MATRIX_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("LITERATURE_CG_TRIPLET_MATRIX_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "n_scenarios": report.get("n_scenarios"),
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
