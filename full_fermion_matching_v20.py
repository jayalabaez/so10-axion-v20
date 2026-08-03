#!/usr/bin/env python3
r"""Fail-closed heavy-light current matching for v20.

The axion-dependent light basis has two distinct matrices:

    Q_proj = B^\dagger Q_UV B,
    A_B    = i B^\dagger dB/dalpha.

Their sum can be made proportional to the identity by a moving-frame field
convention.  That algebraic identity is not the physical regular current.
The projected current Q_proj remains portal dependent and may be
flavour-off-diagonal after rotation to SM mass bases.

This module implements the complete singlet-VEV block

                  U(5)          Q
      (Pbar,Rbar)   A            C
      Qbar           B            D

including the allowed S Q Rbar portal C.  For D nonzero, the light subspace
is controlled by the Schur complement A-C D^{-1} B.

The ERT/DFSZ-like C_f(tan beta) formulas are retained only as the aligned
benchmark Q_proj=I.  They are not promoted to full-v20 predictions.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent

VS_GEV = 6.313855e11
VPHI_GEV = 1.0e17
X_PHI = 17.0
X_S = 4.0
N_COVER = 17.0

ME_GEV = 0.00051099895
MP_GEV = 0.93827208816
MN_GEV = 0.93956542052

GAE_TRGB_95CL = 1.3e-13
SN1987A_QUADRATIC_BOUND = 8.26e-19
FA_UNIVERSAL_SN_GEV = 1.1e8

TAN_BETA_COMMITTED = 1.5000000000002063
TAN_BETA_HIGH_EXAMPLE = 41.2996623
TAN_BETA_DECLARED_RANGE = (1.5, 50.0)


def exact_normalization(
    v_s: float = VS_GEV,
    v_phi: float = VPHI_GEV,
) -> dict:
    """Exact reduced (Phi,S) projection used by the v20 manuscript."""
    if min(v_s, v_phi) <= 0.0:
        raise ValueError("VEVs must be positive")
    d = math.hypot(X_PHI * v_phi, X_S * v_s)
    f_a = v_s * v_phi / d
    xi = X_PHI * v_phi**2 / d**2
    return {
        "D_GeV": d,
        "f_a_GeV": f_a,
        "xi": xi,
        "one_over_17": 1.0 / N_COVER,
        "xi_minus_one_over_17": xi - 1.0 / N_COVER,
        "relative_fa_correction_vs_vS_over_17": f_a / (v_s / N_COVER) - 1.0,
        "scope": (
            "Exact in the reduced (a_Phi,a_S) phase theory. Electroweak-Higgs "
            "components are O(v_EW^2/v_S^2), below 1e-19."
        ),
    }


NORMALIZATION = exact_normalization()
FA_GEV = NORMALIZATION["f_a_GeV"]
XI = NORMALIZATION["xi"]


def beta_fractions(tan_beta: float) -> tuple[float, float]:
    if not math.isfinite(tan_beta) or tan_beta <= 0.0:
        raise ValueError("tan_beta must be finite and positive")
    sin2 = tan_beta**2 / (1.0 + tan_beta**2)
    return sin2, 1.0 - sin2


def sn1987a_quadratic(*, g_an: float, g_ap: float) -> float:
    return g_an**2 + 0.61 * g_ap**2 + 0.53 * g_an * g_ap


def coefficients_at_tan_beta(tan_beta: float) -> dict:
    """Aligned-current tree coefficients plus central hadronic matching.

    This is exact only conditional on Q_proj=I in each relevant SM mass basis.
    """
    sin2, cos2 = beta_fractions(tan_beta)
    c_up = XI * cos2
    c_down = XI * sin2
    c_e = c_down
    c_p = -0.47 + 0.8645 * c_up - 0.437 * c_down
    c_n = -0.02 - 0.4055 * c_up + 0.833 * c_down
    g_ae = c_e * ME_GEV / FA_GEV
    g_ap = c_p * MP_GEV / FA_GEV
    g_an = c_n * MN_GEV / FA_GEV
    sn_lhs = sn1987a_quadratic(g_an=g_an, g_ap=g_ap)
    return {
        "classification": "ALIGNED_CURRENT_BENCHMARK_NOT_FULL_V20",
        "tan_beta": tan_beta,
        "sin2_beta": sin2,
        "cos2_beta": cos2,
        "tree": {
            "C_u0": c_up,
            "C_c0": c_up,
            "C_t0": c_up,
            "C_d0": c_down,
            "C_s0": c_down,
            "C_b0": c_down,
            "C_e0": c_e,
        },
        "C_e": c_e,
        "C_p_central": c_p,
        "C_n_central": c_n,
        "g_ae": g_ae,
        "g_ap_central": g_ap,
        "g_an_central": g_an,
        "TRGB_limit_over_abs_g_ae": GAE_TRGB_95CL / abs(g_ae),
        "SN1987A_quadratic_lhs_central": sn_lhs,
        "SN1987A_amplitude_margin_central": math.sqrt(
            SN1987A_QUADRATIC_BOUND / sn_lhs
        ),
        "hadronic_uncertainty": {
            "model_independent_Cp": 0.03,
            "model_independent_Cn": 0.03,
            "note": (
                "Central di Cortona/PDG matching; coefficients are correlated "
                "and the small C_n central value is not statistically robust."
            ),
        },
    }


def symbolic_aligned_formulas() -> dict:
    return {
        "scope": "conditional on aligned projected current Q_proj=I",
        "xi": "17 v_Phi^2 / ((17 v_Phi)^2 + (4 v_S)^2)",
        "C_u0_Cc0_Ct0": "xi cos^2(beta)",
        "C_d0_Cs0_Cb0_Ce": "xi sin^2(beta)",
        "C_p_central": "-0.47 + xi*(0.8645 cos^2(beta) - 0.437 sin^2(beta))",
        "C_n_central": "-0.02 + xi*(-0.4055 cos^2(beta) + 0.833 sin^2(beta))",
        "precision_status": (
            "Tree formulas are aligned-current benchmarks. Nucleon constants "
            "are central hadronic values and require threshold/RG matching."
        ),
    }


def _nullspace(matrix: np.ndarray, rtol: float = 1e-12) -> np.ndarray:
    matrix = np.asarray(matrix, dtype=complex)
    _u, singular, vh = np.linalg.svd(matrix, full_matrices=True)
    scale = max(float(singular[0]) if len(singular) else 0.0, 1.0)
    rank = int(np.sum(singular > rtol * scale))
    return vh.conj().T[:, rank:]


def _inverse_sqrt_hermitian(matrix: np.ndarray) -> np.ndarray:
    values, vectors = np.linalg.eigh(matrix)
    if np.min(values) <= 0.0:
        raise ValueError("Gram matrix is not positive definite")
    return (vectors * (1.0 / np.sqrt(values))) @ vectors.conj().T


def portal_current_match(
    a: np.ndarray,
    b: np.ndarray,
    c: np.ndarray,
    d: complex,
    *,
    alpha: float = 0.371,
    gauge_admixture: float = 0.0,
) -> dict:
    """Match the full A,B,C,D heavy-light block.

    Shapes are A=(2,5), B=(1,5), C=(2,1), D=scalar.  Entries are understood
    to include their VEV/Yukawa magnitudes at alpha=0.
    """
    a = np.asarray(a, dtype=complex)
    b = np.asarray(b, dtype=complex).reshape(1, 5)
    c = np.asarray(c, dtype=complex).reshape(2, 1)
    if a.shape != (2, 5):
        raise ValueError("A must have shape (2,5)")
    if d == 0:
        raise ValueError("D must be nonzero")

    schur = a - c @ (b / d)
    light_u = _nullspace(schur)
    if light_u.shape != (5, 3):
        raise ValueError("Schur complement must have rank two")
    k = -(b @ light_u) / d
    gram = light_u.conj().T @ light_u + k.conj().T @ k
    invsqrt = _inverse_sqrt_hermitian(gram)

    q_u = 1.0 + gauge_admixture
    q_q = -3.0 + 14.0 * gauge_admixture
    delta_q = q_u - q_q
    phase = np.exp(-1.0j * delta_q * alpha)
    raw = np.vstack([light_u, phase * k])
    embedding = raw @ invsqrt
    d_embedding = np.vstack(
        [
            np.zeros_like(light_u),
            -1.0j * delta_q * phase * k,
        ]
    ) @ invsqrt

    q_uv = np.diag([q_u] * 5 + [q_q])
    q_projected = embedding.conj().T @ q_uv @ embedding
    berry = 1.0j * embedding.conj().T @ d_embedding
    moving_sum = q_projected + berry
    moving_expected = q_u * np.eye(3, dtype=complex)

    # W is the normalized Q-component weight. Analytically:
    # Q_proj=q_u I-(q_u-q_q)W, Berry=(q_u-q_q)W.
    w = invsqrt @ k.conj().T @ k @ invsqrt
    projected_expected = q_u * np.eye(3) - delta_q * w
    berry_expected = delta_q * w

    return {
        "n_light": 3,
        "schur_rank": 2,
        "Q_projected": q_projected,
        "berry_connection": berry,
        "moving_frame_sum": moving_sum,
        "W": w,
        "projected_formula_error": float(
            np.linalg.norm(q_projected - projected_expected)
        ),
        "berry_formula_error": float(np.linalg.norm(berry - berry_expected)),
        "moving_identity_error": float(
            np.linalg.norm(moving_sum - moving_expected)
        ),
        "projected_shift_norm": float(
            np.linalg.norm(q_projected - q_u * np.eye(3))
        ),
        "projected_off_diagonal_norm": float(
            np.linalg.norm(
                q_projected - np.diag(np.diag(q_projected))
            )
        ),
        "berry_norm": float(np.linalg.norm(berry)),
        "portal_weight_trace": float(np.real(np.trace(w))),
        "expected_coordinate_charge": q_u,
    }


def one_family_equal_mixing_counterexample() -> dict:
    """Construct eta=pi/4: moving charge 1 but physical projected charge -1."""
    a = np.zeros((2, 5), dtype=complex)
    a[0, 3] = 1.0
    a[1, 4] = 1.0
    b = np.zeros((1, 5), dtype=complex)
    b[0, 0] = 1.0
    c = np.zeros((2, 1), dtype=complex)
    row = portal_current_match(a, b, c, 1.0)
    eigenvalues = np.linalg.eigvalsh(row["Q_projected"])
    return {
        "Q_projected_eigenvalues": [float(x) for x in eigenvalues],
        "berry_eigenvalues": [
            float(x) for x in np.linalg.eigvalsh(row["berry_connection"])
        ],
        "moving_sum_eigenvalues": [
            float(x) for x in np.linalg.eigvalsh(row["moving_frame_sum"])
        ],
        "contains_minus_one_projected_charge": bool(
            np.min(np.abs(eigenvalues + 1.0)) < 1e-12
        ),
        "moving_sum_is_identity": row["moving_identity_error"] < 1e-12,
    }


def _random_unitary(rng: np.random.Generator, n: int) -> np.ndarray:
    q, r = np.linalg.qr(
        rng.normal(size=(n, n)) + 1.0j * rng.normal(size=(n, n))
    )
    phases = np.diag(r)
    phases = np.where(np.abs(phases) > 0.0, phases / np.abs(phases), 1.0)
    return q @ np.diag(np.conj(phases))


def random_portal_scan(
    *,
    trials: int = 256,
    seed: int = 20260803,
) -> dict:
    """Exercise moving-frame identity and physical portal dependence."""
    if trials < 1:
        raise ValueError("trials must be positive")
    rng = np.random.default_rng(seed)
    worst_formula = 0.0
    worst_moving = 0.0
    largest_shift = 0.0
    largest_mass_basis_offdiag = 0.0
    c_portal_exercised = False
    for _ in range(trials):
        a = rng.normal(size=(2, 5)) + 1.0j * rng.normal(size=(2, 5))
        b = rng.normal(size=(1, 5)) + 1.0j * rng.normal(size=(1, 5))
        c = rng.normal(size=(2, 1)) + 1.0j * rng.normal(size=(2, 1))
        # Scan from tiny to strong light-heavy mixing.
        b *= 10.0 ** rng.uniform(-3.0, 3.0)
        c *= 10.0 ** rng.uniform(-3.0, 3.0)
        d = np.exp(1.0j * rng.uniform(-math.pi, math.pi))
        row = portal_current_match(a, b, c, d, alpha=rng.uniform(-math.pi, math.pi))
        worst_formula = max(
            worst_formula,
            row["projected_formula_error"],
            row["berry_formula_error"],
        )
        worst_moving = max(worst_moving, row["moving_identity_error"])
        largest_shift = max(largest_shift, row["projected_shift_norm"])
        rotation = _random_unitary(rng, 3)
        mass_basis = rotation.conj().T @ row["Q_projected"] @ rotation
        offdiag = mass_basis - np.diag(np.diag(mass_basis))
        largest_mass_basis_offdiag = max(
            largest_mass_basis_offdiag, float(np.linalg.norm(offdiag))
        )
        c_portal_exercised = bool(
            c_portal_exercised or bool(np.linalg.norm(c) > 0.0)
        )

    counterexample = one_family_equal_mixing_counterexample()
    return {
        "trials": trials,
        "seed": seed,
        "worst_analytic_formula_error": worst_formula,
        "worst_moving_identity_error": worst_moving,
        "largest_projected_current_shift": largest_shift,
        "largest_random_mass_basis_offdiagonal": largest_mass_basis_offdiag,
        "C_portal_exercised": bool(c_portal_exercised),
        "one_family_counterexample": counterexample,
        "passes_fail_closed_detection": bool(
            worst_formula < 1e-8
            and worst_moving < 1e-8
            and largest_shift > 0.1
            and largest_mass_basis_offdiag > 1e-3
            and c_portal_exercised
            and counterexample["contains_minus_one_projected_charge"]
        ),
    }


def coefficient_envelope(
    tan_beta_min: float = TAN_BETA_DECLARED_RANGE[0],
    tan_beta_max: float = TAN_BETA_DECLARED_RANGE[1],
    points: int = 2001,
) -> dict:
    """Aligned-current benchmark envelope only."""
    if not 0.0 < tan_beta_min < tan_beta_max:
        raise ValueError("invalid tan_beta interval")
    grid = np.geomspace(tan_beta_min, tan_beta_max, points)
    rows = [coefficients_at_tan_beta(float(t)) for t in grid]
    keys = (
        "C_e",
        "C_p_central",
        "C_n_central",
        "g_ae",
        "g_ap_central",
        "g_an_central",
    )
    ranges = {
        key: [
            float(min(row[key] for row in rows)),
            float(max(row[key] for row in rows)),
        ]
        for key in keys
    }
    max_sn = max(row["SN1987A_quadratic_lhs_central"] for row in rows)
    max_gae = max(abs(row["g_ae"]) for row in rows)
    return {
        "scope": "aligned-current benchmark only; not full-v20 portal envelope",
        "tan_beta_interval": [tan_beta_min, tan_beta_max],
        "points": points,
        "ranges": ranges,
        "aligned_TRGB_safe_central": max_gae < GAE_TRGB_95CL,
        "aligned_SN1987A_safe_central": max_sn < SN1987A_QUADRATIC_BOUND,
        "model_independent_SN_fa_safe": FA_GEV > FA_UNIVERSAL_SN_GEV,
    }


def build_report() -> dict:
    portal = random_portal_scan()
    committed = coefficients_at_tan_beta(TAN_BETA_COMMITTED)
    high = coefficients_at_tan_beta(TAN_BETA_HIGH_EXAMPLE)
    aligned_envelope = coefficient_envelope()
    checks = {
        "projected_and_berry_formulas_verified": (
            portal["worst_analytic_formula_error"] < 1e-8
        ),
        "moving_frame_identity_verified": portal["worst_moving_identity_error"] < 1e-8,
        "physical_portal_dependence_detected": portal[
            "largest_projected_current_shift"
        ]
        > 0.1,
        "possible_FCNC_detected": portal[
            "largest_random_mass_basis_offdiagonal"
        ]
        > 1e-3,
        "allowed_C_portal_included": portal["C_portal_exercised"],
        "equal_mixing_counterexample": portal["one_family_counterexample"][
            "contains_minus_one_projected_charge"
        ],
        "exact_xi_finite": math.isfinite(XI) and XI > 0.0,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "PORTAL_DEPENDENT_PHYSICAL_CURRENT__"
            "FULL_FERMION_MATCHING_OPEN__ALIGNED_BENCHMARK_ONLY"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "normalization": NORMALIZATION,
        "portal_current_result": {
            "physical_regular_current": "Q_proj = I_3 - 4 W (pure PQ basis)",
            "berry_connection": "A_B = +4 W",
            "moving_frame_identity": "Q_proj + A_B = I_3",
            "interpretation": (
                "The moving-frame sum is coordinate-convention dependent. "
                "Physical derivative/Yukawa couplings retain Q_proj and are "
                "portal dependent."
            ),
            "full_block": (
                "A,B,C,D with Schur complement A-C D^{-1}B; rank two is "
                "required for three light modes"
            ),
            "scan": portal,
        },
        "aligned_symbolic_benchmark": symbolic_aligned_formulas(),
        "aligned_numerical_examples_not_full_predictions": {
            "tan_beta_1p5": committed,
            "tan_beta_high": high,
        },
        "aligned_beta_envelope": aligned_envelope,
        "full_model_status": {
            "portal_matrices_required": True,
            "SM_Yukawa_alignment_required": True,
            "tree_FCNC_absence_proved": False,
            "unique_symbolic_full_model_Ce_Cp_Cn": False,
            "unique_numerical_Ce_Cp_Cn": False,
            "full_model_stellar_SN_pass": None,
        },
        "missing_for_full_matching": [
            "complete representation-aware A,B,C,D portal tensors",
            "component-level 10_H and 126_H Yukawa tensors",
            "rotation of Q_proj into each SM fermion mass basis",
            "heavy-threshold Wess-Zumino/anomaly matching",
            "correct Takagi/PMNS flavour fit and a defensible tan(beta)",
            "threshold/RG evolution and correlated hadronic matching",
        ],
        "checks": {name: bool(value) for name, value in checks.items()},
        "verdict": (
            "The Berry cancellation identity is verified but does not close the "
            "physical portal gap. Q_proj=I-4W is portal dependent and can be "
            "flavour off-diagonal. The displayed C_f(tan beta) remain aligned "
            "benchmarks only. Exact full-v20 C_e,C_p,C_n are not derived."
        ),
    }


def write_markdown(report: dict) -> str:
    portal = report["portal_current_result"]["scan"]
    low = report["aligned_numerical_examples_not_full_predictions"]["tan_beta_1p5"]
    high = report["aligned_numerical_examples_not_full_predictions"]["tan_beta_high"]
    lines = [
        "# Full heavy-light fermion matching — fail-closed v20 status",
        "",
        f"**Status:** `{report['status']}`",
        "",
        "## Correct current decomposition",
        "",
        "- Physical projected current: `Q_proj = I_3 - 4 W`",
        "- Berry connection: `A_B = +4 W`",
        "- Moving-coordinate sum: `Q_proj + A_B = I_3`",
        "- The sum is basis/convention dependent; it is not the observable current.",
        "",
        f"- Random full-block trials: {portal['trials']}",
        f"- Largest physical projected shift: `{portal['largest_projected_current_shift']:.3e}`",
        f"- Largest random mass-basis off-diagonal: `{portal['largest_random_mass_basis_offdiagonal']:.3e}`",
        f"- Moving-frame identity error: `{portal['worst_moving_identity_error']:.3e}`",
        "",
        "The scan includes the additionally allowed `S Q Rbar` portal through",
        "the full `A,B,C,D` Schur-complement block.",
        "",
        "## Explicit equal-mixing counterexample",
        "",
        f"- Projected-current eigenvalues: `{portal['one_family_counterexample']['Q_projected_eigenvalues']}`",
        f"- Berry eigenvalues: `{portal['one_family_counterexample']['berry_eigenvalues']}`",
        f"- Moving-sum eigenvalues: `{portal['one_family_counterexample']['moving_sum_eigenvalues']}`",
        "",
        "## Aligned-current examples only",
        "",
        "| tan(beta) | C_e | C_p central | C_n central |",
        "|---:|---:|---:|---:|",
        f"| {low['tan_beta']:.6g} | {low['C_e']:.12g} | {low['C_p_central']:.12g} | {low['C_n_central']:.12g} |",
        f"| {high['tan_beta']:.6g} | {high['C_e']:.12g} | {high['C_p_central']:.12g} | {high['C_n_central']:.12g} |",
        "",
        "These numbers require `Q_proj=I` aligned with each SM Yukawa matrix.",
        "They are not exact full-v20 predictions.",
        "",
        "## Missing for closure",
        "",
        *[f"- {item}" for item in report["missing_for_full_matching"]],
        "",
        "## Verdict",
        "",
        report["verdict"],
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    ROOT.joinpath("FULL_FERMION_MATCHING_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("FULL_FERMION_MATCHING_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "largest_projected_shift": report["portal_current_result"]["scan"][
                    "largest_projected_current_shift"
                ],
                "possible_FCNC": report["full_model_status"][
                    "tree_FCNC_absence_proved"
                ]
                is False,
                "unique_full_model_coefficients": False,
                "verdict": report["verdict"],
            },
            indent=2,
        )
    )
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
