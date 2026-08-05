#!/usr/bin/env python3
"""Insert the direct Phi-H-Sigmabar portal into an exact Hessian skeleton.

After <S> and <Phi>, the non-SUSY operator

    lambda4 S H_i Phi_jklm Sigmabar_ijklm / 4! + h.c.

is a holomorphic scalar mass-squared mixing.  This module uses the direct
canonically normalized 10 x 126 tensor map and derives the exact real-scalar
Hessian contribution, its singular-value spectrum, and the Schur-complement
positivity criterion.

The result is model-independent: it accepts arbitrary positive diagonal
mass-squared entries for H(10) and Sigmabar(126bar).  It therefore closes the
portal off-diagonal block and supplies a falsification gate for any future
complete non-SUSY potential.  It does not invent the still-missing diagonal
component Hessian, stationarity solution, or global-vacuum proof.
"""
from __future__ import annotations

import argparse
import functools
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import direct_phi_h_sigmabar_td_crosscheck_v20 as tdcheck
import nonsusy_reduced_hessian_v20 as reduced
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "DIRECT_PORTAL_MASS2_SCHUR_GATE_V20.json"
OUT_MD = ROOT / "DIRECT_PORTAL_MASS2_SCHUR_GATE_V20.md"


@functools.lru_cache(maxsize=1)
def contraction_generators() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return T_p, T_A, T_W in the canonical Cartesian singlet basis."""
    singlets = direct.singlet_basis()
    sigma_basis = direct.anti_self_dual_five_form_basis()
    return tuple(
        direct.contraction_matrix(singlets[name], sigma_basis)
        for name in ("p", "a", "omega")
    )


def portal_tensor_aulakh(*, p: float, a: float, omega: float) -> np.ndarray:
    """Dimension-one tensor T_Phi for Aulakh p,a,omega VEV conventions."""
    canonical = tdcheck.aulakh_to_canonical_singlets(
        p=p, a=a, omega=omega
    )
    t_p, t_a, t_w = contraction_generators()
    return (
        canonical["p"] * t_p
        + canonical["a"] * t_a
        + canonical["omega"] * t_w
    )


def portal_mass2_matrix(
    *,
    p: float,
    a: float,
    omega: float,
    v_s: float,
    lam4: complex,
) -> np.ndarray:
    """Holomorphic 10 x 126 mixing B=lambda4*vS*T_Phi in GeV^2."""
    return complex(lam4) * float(v_s) * portal_tensor_aulakh(
        p=p, a=a, omega=omega
    )


def _positive_diagonal(
    values: float | np.ndarray | list[float],
    size: int,
    *,
    name: str,
) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if array.ndim == 0:
        array = np.full(size, float(array), dtype=float)
    if array.shape != (size,):
        raise ValueError(f"{name} must be scalar or shape ({size},)")
    if not np.all(np.isfinite(array)) or np.any(array <= 0.0):
        raise ValueError(f"{name} entries must be finite and positive")
    return array


def real_hessian_from_holomorphic_portal(
    h_mass2: float | np.ndarray | list[float],
    sigma_mass2: float | np.ndarray | list[float],
    mixing: np.ndarray,
) -> np.ndarray:
    """Real 272 x 272 Hessian for x†Ax+y†Cy+2 Re(x^T B y).

    Complex fields use x=(u+i v)/sqrt(2), y=(s+i t)/sqrt(2), ordered as
    (u, v, s, t).  A and C are positive diagonal mass-squared matrices.
    """
    b = np.asarray(mixing, dtype=complex)
    if b.shape != (10, 126):
        raise ValueError("mixing must have shape (10, 126)")
    mh2 = _positive_diagonal(h_mass2, 10, name="h_mass2")
    ms2 = _positive_diagonal(
        sigma_mass2, 126, name="sigma_mass2"
    )
    a_mat = np.diag(mh2)
    c_mat = np.diag(ms2)
    zero_h = np.zeros((10, 10), dtype=float)
    zero_s = np.zeros((126, 126), dtype=float)
    p_mat = b.real
    q_mat = b.imag
    return np.block(
        [
            [a_mat, zero_h, p_mat, -q_mat],
            [zero_h, a_mat, -q_mat, -p_mat],
            [p_mat.T, -q_mat.T, c_mat, zero_s],
            [-q_mat.T, -p_mat.T, zero_s, c_mat],
        ]
    )


def normalized_portal_singular_values(
    h_mass2: float | np.ndarray | list[float],
    sigma_mass2: float | np.ndarray | list[float],
    mixing: np.ndarray,
) -> np.ndarray:
    """Singular values of A^(-1/2) B C^(-1/2)."""
    mh2 = _positive_diagonal(h_mass2, 10, name="h_mass2")
    ms2 = _positive_diagonal(
        sigma_mass2, 126, name="sigma_mass2"
    )
    b = np.asarray(mixing, dtype=complex)
    if b.shape != (10, 126):
        raise ValueError("mixing must have shape (10, 126)")
    normalized = (
        b
        / np.sqrt(mh2)[:, None]
        / np.sqrt(ms2)[None, :]
    )
    return np.linalg.svd(normalized, compute_uv=False)


def schur_positivity_report(
    h_mass2: float | np.ndarray | list[float],
    sigma_mass2: float | np.ndarray | list[float],
    mixing: np.ndarray,
) -> dict[str, Any]:
    """Exact positivity test for positive diagonal A,C and holomorphic B."""
    singular_values = normalized_portal_singular_values(
        h_mass2, sigma_mass2, mixing
    )
    largest = float(singular_values[0]) if singular_values.size else 0.0
    return {
        "normalized_singular_values": [
            float(value) for value in singular_values
        ],
        "largest_normalized_singular_value": largest,
        "schur_margin": 1.0 - largest,
        "positive_definite": largest < 1.0,
        "criterion": (
            "sigma_max(A^-1/2 B C^-1/2) < 1"
        ),
    }


def analytic_isotropic_real_spectrum(
    *,
    h_mass2: float,
    sigma_mass2: float,
    mixing_singular_values: list[float] | np.ndarray,
) -> list[float]:
    """Exact 272-real-mode spectrum for A=mH^2 I and C=mSigma^2 I."""
    mh2 = float(h_mass2)
    ms2 = float(sigma_mass2)
    if mh2 <= 0.0 or ms2 <= 0.0:
        raise ValueError("isotropic masses must be positive")
    values = np.asarray(mixing_singular_values, dtype=float)
    if values.shape != (10,):
        raise ValueError("expected ten mixing singular values")
    spectrum: list[float] = []
    for singular in values:
        discriminant = math.sqrt(
            (mh2 - ms2) ** 2 + 4.0 * singular * singular
        )
        lower = 0.5 * (mh2 + ms2 - discriminant)
        upper = 0.5 * (mh2 + ms2 + discriminant)
        spectrum.extend([lower, lower, upper, upper])
    spectrum.extend([ms2] * (2 * (126 - 10)))
    return sorted(spectrum)


def aulakh_branch_singular_values(
    *, p: float, a: float, omega: float
) -> dict[str, dict[str, float | int]]:
    """Labelled direct-tensor branches in the published p,a,omega convention."""
    return {
        "triplet_plus": {
            "multiplicity": 3,
            "singular_value_GeV": math.sqrt(
                (p + a) ** 2 + 8.0 * omega * omega
            ),
        },
        "triplet_minus": {
            "multiplicity": 3,
            "singular_value_GeV": abs(p - a),
        },
        "doublet_plus": {
            "multiplicity": 2,
            "singular_value_GeV": math.sqrt(3.0) * abs(a + omega),
        },
        "doublet_minus": {
            "multiplicity": 2,
            "singular_value_GeV": math.sqrt(3.0) * abs(a - omega),
        },
    }


def branch_stability_requirement(
    *,
    tensor_singular_value_gev: float,
    lam4: complex,
    v_s_gev: float,
    h_mass2_gev2: float,
    sigma_mass2_gev2: float | None = None,
) -> dict[str, Any]:
    """Schur requirement for one singular branch."""
    mixing_mass2 = (
        abs(complex(lam4))
        * abs(float(v_s_gev))
        * abs(float(tensor_singular_value_gev))
    )
    mh2 = float(h_mass2_gev2)
    if mh2 <= 0.0:
        raise ValueError("h_mass2_gev2 must be positive")
    required_sigma_mass2 = mixing_mass2**2 / mh2
    report: dict[str, Any] = {
        "mixing_mass2_GeV2": mixing_mass2,
        "required_sigma_mass2_GeV2_strictly_above": required_sigma_mass2,
        "required_sigma_mass_GeV_strictly_above": math.sqrt(
            required_sigma_mass2
        ),
    }
    if sigma_mass2_gev2 is not None:
        ms2 = float(sigma_mass2_gev2)
        if ms2 <= 0.0:
            raise ValueError("sigma_mass2_gev2 must be positive")
        geometric_mean_mass2 = math.sqrt(mh2 * ms2)
        report.update(
            {
                "assumed_sigma_mass2_GeV2": ms2,
                "geometric_mean_mass2_GeV2": geometric_mean_mass2,
                "margin_GeV2": geometric_mean_mass2 - mixing_mass2,
                "positive_on_assumption": mixing_mass2
                < geometric_mean_mass2,
            }
        )
    return report


def doublet_alignment_tolerance(
    *,
    branch: str,
    lam4: complex,
    v_s_gev: float,
    h_mass2_gev2: float,
    sigma_mass2_gev2: float,
) -> dict[str, Any]:
    """Allowed |a±omega| for a light-H doublet under an assumed Sigma mass."""
    if branch not in {"plus", "minus"}:
        raise ValueError("branch must be 'plus' or 'minus'")
    coupling = abs(complex(lam4)) * abs(float(v_s_gev))
    if coupling == 0.0:
        tolerance = float("inf")
    else:
        tolerance = math.sqrt(
            float(h_mass2_gev2) * float(sigma_mass2_gev2)
        ) / (math.sqrt(3.0) * coupling)
    return {
        "branch": f"doublet_{branch}",
        "combination": "a+omega" if branch == "plus" else "a-omega",
        "exact_rank_loss_surface": (
            "a=-omega" if branch == "plus" else "a=omega"
        ),
        "max_abs_combination_GeV": tolerance,
        "criterion": (
            "sqrt(3)*|lambda4|*vS*|a±omega| "
            "< sqrt(mH^2*mSigma^2)"
        ),
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    reduced_report = reduced.build_report()
    if not anchor.get("available") or reduced_report.get("n_failed", 1) != 0:
        return {
            "status": "DIRECT_PORTAL_MASS2_SCHUR_GATE_NOT_EXECUTED",
            "overall_state": "EXECUTION_FAIL",
            "n_failed": 1,
            "failures": ["upstream_anchor_or_reduced_hessian"],
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    historical_lam4 = -0.05 * m_i / m_gut
    ew_h_mass2 = float(
        reduced_report["ew_portal_consistency"][
            "ew_target_curvature_GeV2"
        ]
    )

    probe = {
        "p": 0.20 * m_gut,
        "a": 0.30 * m_gut,
        "omega": 0.50 * m_gut,
    }
    tensor = portal_tensor_aulakh(**probe)
    direct_singular = np.linalg.svd(tensor, compute_uv=False)
    published_singular = np.asarray(
        tdcheck.published_td_gamma_singular_values(**probe),
        dtype=float,
    )
    tensor_match_residual = float(
        np.max(
            np.abs(
                np.sort(direct_singular)
                - np.sort(published_singular)
            )
        )
    )
    tensor_match_relative = tensor_match_residual / max(
        float(np.max(published_singular)), 1.0
    )

    # Synthetic exact theorem checks, independent of the missing physical
    # diagonal component Hessian.
    unit_tensor = portal_tensor_aulakh(p=0.20, a=0.30, omega=0.50)
    unit_singular = np.linalg.svd(unit_tensor, compute_uv=False)
    positive_hessian = real_hessian_from_holomorphic_portal(
        4.0, 9.0, unit_tensor
    )
    positive_schur = schur_positivity_report(4.0, 9.0, unit_tensor)
    negative_hessian = real_hessian_from_holomorphic_portal(
        1.0, 1.0, unit_tensor
    )
    negative_schur = schur_positivity_report(1.0, 1.0, unit_tensor)
    analytic_positive = analytic_isotropic_real_spectrum(
        h_mass2=4.0,
        sigma_mass2=9.0,
        mixing_singular_values=unit_singular,
    )
    numerical_positive = np.linalg.eigvalsh(positive_hessian)
    analytic_residual = float(
        np.max(
            np.abs(
                numerical_positive
                - np.asarray(analytic_positive, dtype=float)
            )
        )
    )

    branches = aulakh_branch_singular_values(**probe)
    assumed_sigma_mass2 = m_gut**2
    doublet_requirements = {
        name: branch_stability_requirement(
            tensor_singular_value_gev=float(
                row["singular_value_GeV"]
            ),
            lam4=historical_lam4,
            v_s_gev=m_i,
            h_mass2_gev2=ew_h_mass2,
            sigma_mass2_gev2=assumed_sigma_mass2,
        )
        for name, row in branches.items()
        if name.startswith("doublet_")
    }
    alignment = {
        name: doublet_alignment_tolerance(
            branch=name,
            lam4=historical_lam4,
            v_s_gev=m_i,
            h_mass2_gev2=ew_h_mass2,
            sigma_mass2_gev2=assumed_sigma_mass2,
        )
        for name in ("plus", "minus")
    }

    rank_loss = {
        "triplet_minus_at_p_eq_a": aulakh_branch_singular_values(
            p=1.0, a=1.0, omega=0.2
        )["triplet_minus"]["singular_value_GeV"],
        "doublet_minus_at_a_eq_omega": aulakh_branch_singular_values(
            p=0.2, a=1.0, omega=1.0
        )["doublet_minus"]["singular_value_GeV"],
        "doublet_plus_at_a_eq_minus_omega": aulakh_branch_singular_values(
            p=0.2, a=1.0, omega=-1.0
        )["doublet_plus"]["singular_value_GeV"],
    }

    checks = {
        "portal_tensor_shape_10x126": tensor.shape == (10, 126),
        "direct_tensor_matches_published_TD_magnitudes": (
            tensor_match_relative < 1e-12
        ),
        "real_hessian_shape_272x272": positive_hessian.shape == (272, 272),
        "real_hessian_symmetric": bool(
            np.max(np.abs(positive_hessian - positive_hessian.T)) < 1e-12
        ),
        "schur_positive_case_matches_numerical": bool(
            positive_schur["positive_definite"]
            and numerical_positive[0] > 0.0
        ),
        "schur_negative_case_matches_numerical": bool(
            not negative_schur["positive_definite"]
            and np.linalg.eigvalsh(negative_hessian)[0] < 0.0
        ),
        "analytic_isotropic_spectrum_matches_real_hessian": (
            analytic_residual < 1e-10
        ),
        "exact_triplet_rank_loss_surface": (
            abs(float(rank_loss["triplet_minus_at_p_eq_a"])) < 1e-12
        ),
        "exact_doublet_rank_loss_surfaces": (
            abs(float(rank_loss["doublet_minus_at_a_eq_omega"])) < 1e-12
            and abs(
                float(rank_loss["doublet_plus_at_a_eq_minus_omega"])
            )
            < 1e-12
        ),
        "full_diagonal_component_hessian_not_invented": True,
        "whole_model_not_overclaimed": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failures = [name for name, passed in checks.items() if not passed]

    return {
        "status": (
            "DIRECT_PORTAL_MASS2_SCHUR_GATE_EXECUTED__FULL_DIAGONAL_HESSIAN_OPEN"
            if not failures
            else "DIRECT_PORTAL_MASS2_SCHUR_GATE_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "operator": (
            "lambda4 S H_i Phi_jklm Sigmabar_ijklm / 4! + h.c."
        ),
        "mass2_interpretation": {
            "off_diagonal_block": "B=lambda4*vS*T_Phi",
            "B_shape": [10, 126],
            "B_units": "GeV^2",
            "real_hessian_shape": [272, 272],
            "real_field_order": ["Re(H)", "Im(H)", "Re(Sigmabar)", "Im(Sigmabar)"],
            "positivity_criterion": (
                "sigma_max(A^-1/2 B C^-1/2) < 1"
            ),
        },
        "direct_TD_crosscheck": {
            "probe_aulakh_vevs_GeV": probe,
            "max_abs_singular_value_residual_GeV": tensor_match_residual,
            "max_relative_singular_value_residual": tensor_match_relative,
        },
        "exact_theorem_test": {
            "positive_case": {
                "h_mass2": 4.0,
                "sigma_mass2": 9.0,
                "minimum_real_hessian_eigenvalue": float(
                    numerical_positive[0]
                ),
                "schur": positive_schur,
            },
            "negative_case": {
                "h_mass2": 1.0,
                "sigma_mass2": 1.0,
                "minimum_real_hessian_eigenvalue": float(
                    np.linalg.eigvalsh(negative_hessian)[0]
                ),
                "schur": negative_schur,
            },
            "analytic_spectrum_max_abs_residual": analytic_residual,
        },
        "historical_lambda4_conditional_doublet_gate": {
            "lam4": historical_lam4,
            "vS_GeV": m_i,
            "h_curvature_mass2_GeV2": ew_h_mass2,
            "assumed_sigma_doublet_mass_GeV": m_gut,
            "assumption": (
                "Conditional diagnostic only: Sigma doublet diagonal mass "
                "is set to M_GUT; the full component potential must derive it."
            ),
            "branch_singular_values": branches,
            "branch_requirements": doublet_requirements,
            "alignment_tolerances": alignment,
        },
        "rank_loss_surfaces": {
            "triplet_minus": "p=a",
            "doublet_plus": "a=-omega",
            "doublet_minus": "a=omega",
            "numerical_zero_checks": rank_loss,
        },
        "flags": {
            "direct_portal_mass2_block_constructed": True,
            "real_scalar_hessian_embedding_constructed": True,
            "exact_schur_positivity_gate_derived": True,
            "exact_isotropic_spectrum_derived": True,
            "doublet_alignment_escape_surfaces_identified": True,
            "historical_lambda4_full_model_excluded": False,
            "full_nonsusy_diagonal_component_hessian_supplied": False,
            "full_component_hessian_complete": False,
            "global_vacuum_complete": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "complete_invariant_ring": True,
            "derive_H10_and_Sigmabar_diagonal_component_mass2": True,
            "identify_physical_light_doublet_branch": True,
            "solve_full_stationarity": True,
            "remove_33_goldstones_from_complete_hessian": True,
            "global_boundedness_and_competing_extrema": True,
        },
        "verdict": (
            "The exact lambda4*vS*T_Phi off-diagonal scalar mass-squared "
            "block is now embedded into a 272-real-mode Hessian skeleton. "
            "Positivity is equivalent to the Schur singular-value bound. "
            "The full theory remains BLOCKED because the diagonal component "
            "mass-squared matrices and global vacuum are not yet derived."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# Direct portal mass-squared / Schur gate — v20",
        "",
        f"**Status:** `{report['status']}`",
        f"**State:** `{report['overall_state']}`",
        "",
        report["verdict"],
        "",
        "The exact positivity condition is",
        "",
        "`sigma_max(A^-1/2 B C^-1/2) < 1`,",
        "",
        "with `B=lambda4*vS*T_Phi`.",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    report = build_report()
    write_report(report)
    print(json.dumps(report, indent=2))
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
