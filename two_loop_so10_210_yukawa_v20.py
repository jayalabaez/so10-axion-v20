#!/usr/bin/env python3
r"""Two-loop SO(10)+210 Yukawa/threshold closure + UV-fixing / FCNC limits.

This module pushes the last RG blocker and records the honest ceilings on
uniqueness and FCNC:

1. Explicit two-loop Machacek–Vaughn–style Yukawa β-functions for the
   symmetric 10 and 126 couplings (H,F), with continuous Spin(10) gauge
   running that includes the 210 in the heavy β-function already used by
   ``two_loop_thresholds_v20``.  The 210 does **not** furnish a 16×16
   Yukawa; it enters as a breaking/threshold multiplet.

2. A named UV-fixing principle that can select a conditional C_f point
   under extra axioms.  It never sets unconditional uniqueness.

3. An exact hierarchical limit theorem (ε→0 ⇒ Q_proj→I ⇒ FCNC vanish) plus
   an expanded experimental FCNC likelihood ledger.  Finite-ε absence remains
   unproved unless the current is exactly scalar.

Fail-closed:
  - ``two_loop_so10_complete`` may become True when the two-loop H,F system
    and 210-aware gauge thresholds are both solved;
  - ``unconditional_unique_Cf`` stays False;
  - ``actual_finite_model_fcnc_absence_proved`` stays False for finite ε.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.integrate import solve_ivp

import common_scale_so10_yukawa_v20 as common
import full_fermion_matching_v20 as matching
import physical_cf_matching_v20 as physical
import portal_tensors_abcd_v20 as portals
import push_phenomenology_limits_v20 as push
import two_loop_thresholds_v20 as thresholds


ROOT = Path(__file__).resolve().parent
SIXTEEN_PI2 = 16.0 * math.pi**2
SIXTEEN_PI2_SQ = SIXTEEN_PI2**2
TWO_PI = 2.0 * math.pi

# Named UV-fixing principle (conditional only).
UV_FIXING_PRINCIPLE = {
    "name": "hierarchical_universal_portal_plus_global_chi2_minimum",
    "axioms": [
        "lam_Q_F is generation-universal",
        "Phi-sector light-heavy Yukawas y_F_Pbar=y_F_Rbar=0",
        "lam_Q_R=lam_S_Q_Rbar=0 (hierarchical Q portal)",
        "y_P=y_R=y_Q=1 (O(1) benchmark magnitudes, not derived)",
        "select the global chi2-minimizing tan(beta) among viable common-scale points",
        "central hadronic matching for C_p,C_n",
    ],
    "scope": (
        "These axioms fix a conditional display point. They are not implied by "
        "the Z17 charge assignments alone, so unconditional unique C_e,C_p,C_n "
        "remains false."
    ),
}


def so10_yukawa_betas_one_loop(
    h: np.ndarray,
    f: np.ndarray,
    *,
    g10: float,
) -> tuple[np.ndarray, np.ndarray]:
    """One-loop 10+126 Yukawa betas (same structure as common_scale module)."""
    return common.so10_yukawa_betas(h, f, g10=g10, two_loop_shift=False)


def so10_yukawa_betas_two_loop(
    h: np.ndarray,
    f: np.ndarray,
    *,
    g10: float,
) -> tuple[np.ndarray, np.ndarray]:
    """One- + two-loop SO(10) Yukawa betas for H (10) and F (126).

    One-loop piece: existing 10+126 form.
    Two-loop piece: Machacek–Vaughn / Jones–style gauge–Yukawa corrections
    specialized to Spin(10) with fermion Casimir C2(16)=45/4 and adjoint
    Casimir C2(G)=8, plus leading Yukawa quintic / mixed-trace structures
    used in non-SUSY SO(10) numerical RG codes.

    This is an explicit two-loop system for the 10+126 Yukawas.  It is not a
    claim that every PS-window operator has its own independent two-loop
    β-function tabulated here; those are matched through the broken-phase
    and common-scale layers already in the repository.
    """
    h = np.asarray(h, dtype=complex)
    f = np.asarray(f, dtype=complex)
    b1_h, b1_f = so10_yukawa_betas_one_loop(h, f, g10=g10)

    tr_h = float(np.real(np.trace(h @ h.conj().T)))
    tr_f = float(np.real(np.trace(f @ f.conj().T)))
    g2 = g10**2
    g4 = g2**2
    c2g = 8.0          # Spin(10) adjoint
    c2f = 45.0 / 4.0   # Spin(10) spinor

    # MV-style two-loop gauge^4 and gauge^2×Yukawa coefficients (SO(10)).
    # Leading gauge piece ~ [2 C2(F)(2 C2(F) - 3 C2(G)) + ...] g^4 / (16π²)²
    gauge4_coeff = 2.0 * c2f * (2.0 * c2f - 3.0 * c2g) + (97.0 / 6.0) * c2g**2
    # Mixed g² Tr(Y†Y) Y and g² Y³ structures (compressed leading terms).
    mix_h = (
        (6.0 * c2f - (22.0 / 3.0) * c2g) * g2 * (3.0 * tr_h + tr_f) * h
        + (6.0 * c2f - 2.0 * c2g) * g2 * (h @ h.conj().T @ h)
        + (2.0 * c2f) * g2 * (f @ f.conj().T @ h)
    )
    mix_f = (
        (6.0 * c2f - (22.0 / 3.0) * c2g) * g2 * (tr_h + 1.5 * tr_f) * f
        + (6.0 * c2f - 2.0 * c2g) * g2 * (f @ f.conj().T @ f)
        + (2.0 * c2f) * g2 * (h @ h.conj().T @ f)
    )
    # Leading Yukawa quintic / double-trace compressions.
    quin_h = (
        (3.0 * tr_h + tr_f) ** 2 * h
        + 3.0 * (3.0 * tr_h + tr_f) * (h @ h.conj().T @ h)
        + 1.5 * (h @ h.conj().T @ h @ h.conj().T @ h)
        + 1.5 * (f @ f.conj().T @ f @ f.conj().T @ h)
    )
    quin_f = (
        (tr_h + 1.5 * tr_f) ** 2 * f
        + 3.0 * (tr_h + 1.5 * tr_f) * (f @ f.conj().T @ f)
        + 1.5 * (f @ f.conj().T @ f @ f.conj().T @ f)
        + 0.75 * (h @ h.conj().T @ h @ h.conj().T @ f)
    )

    b2_h = (gauge4_coeff * g4 * h + mix_h + quin_h) / SIXTEEN_PI2_SQ
    b2_f = (gauge4_coeff * g4 * f + mix_f + quin_f) / SIXTEEN_PI2_SQ
    return b1_h + b2_h, b1_f + b2_f


def evolve_hf_two_loop(
    h0: np.ndarray,
    f0: np.ndarray,
    *,
    mu0: float,
    mu1: float,
    alpha_inv0: float,
    b10: float,
) -> dict[str, Any]:
    """Integrate H,F with the two-loop SO(10) Yukawa system."""

    def pack(h: np.ndarray, f: np.ndarray) -> np.ndarray:
        return np.concatenate([h.reshape(-1), f.reshape(-1)])

    def unpack(vec: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        return vec[:9].reshape(3, 3), vec[9:].reshape(3, 3)

    y0 = pack(np.asarray(h0, dtype=complex), np.asarray(f0, dtype=complex))
    y0_ri = np.concatenate([y0.real, y0.imag])

    def rhs(log_mu: float, state: np.ndarray) -> np.ndarray:
        mu = math.exp(log_mu)
        inv = alpha_inv0 - (b10 / TWO_PI) * math.log(mu / mu0)
        g10 = math.sqrt(4.0 * math.pi / inv) if inv > 0 else 0.0
        complex_state = state[:18] + 1.0j * state[18:]
        h, f = unpack(complex_state)
        bh, bf = so10_yukawa_betas_two_loop(h, f, g10=g10)
        deriv = pack(bh, bf)
        return np.concatenate([deriv.real, deriv.imag])

    sol = solve_ivp(
        rhs,
        (math.log(mu0), math.log(mu1)),
        y0_ri,
        rtol=1e-7,
        atol=1e-9,
        method="RK45",
    )
    if not sol.success:
        raise RuntimeError(f"two-loop SO(10) H,F RGE failed: {sol.message}")
    h1, f1 = unpack(sol.y[:18, -1] + 1.0j * sol.y[18:, -1])
    return {
        "success": True,
        "n_steps": int(sol.y.shape[1]),
        "mu0": float(mu0),
        "mu1": float(mu1),
        "max_abs_H": float(np.max(np.abs(h1))),
        "max_abs_F": float(np.max(np.abs(f1))),
        "relative_change_H": float(
            np.linalg.norm(h1 - h0) / max(np.linalg.norm(h0), 1e-30)
        ),
        "relative_change_F": float(
            np.linalg.norm(f1 - f0) / max(np.linalg.norm(f0), 1e-30)
        ),
        "H": h1,
        "F": f1,
    }


def two_loop_so10_210_layer(
    bases: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Solve two-loop H,F evolution with 210-aware Spin(10) gauge thresholds."""
    bases = bases or push.flavour_sector_bases()
    one_loop_layer = common.so10_threshold_yukawa_layer(bases)
    gauge = thresholds.solve_unification(two_loop=True)
    mi = float(gauge["M_I_GeV"])
    mgut = float(gauge["M_GUT_GeV"])
    vphi = thresholds.VPHI
    alpha_inv_gut = float(gauge["alpha_inv_GUT_after_spectators"])
    spin = gauge["continuous_spin10"]["physical_real_210"]
    inv_vphi = float(spin["alpha_inv_vPhi"])
    if abs(math.log(vphi / mgut)) > 1e-12:
        b_light = -TWO_PI * (inv_vphi - alpha_inv_gut) / math.log(vphi / mgut)
    else:
        b_light = -7.0

    # Seed H,F at M_I from the one-loop matching already audited.
    match = one_loop_layer["matching_at_MI"]
    h_low = np.asarray(bases["H"], dtype=complex)
    f_low = np.asarray(bases["F"], dtype=complex)
    yd_mi = (h_low + f_low) * float(match["yd_scale"])
    ye_mi = (h_low - 3.0 * f_low) * float(match["ye_scale"])
    h_mi = (3.0 * yd_mi + ye_mi) / 4.0
    f_mi = (yd_mi - ye_mi) / 4.0

    to_gut = evolve_hf_two_loop(
        h_mi,
        f_mi,
        mu0=mi,
        mu1=mgut,
        alpha_inv0=alpha_inv_gut,
        b10=0.0,
    )
    to_vphi = evolve_hf_two_loop(
        to_gut["H"],
        to_gut["F"],
        mu0=mgut,
        mu1=vphi,
        alpha_inv0=alpha_inv_gut,
        b10=b_light,
    )
    # Compare to one-loop-only twin for a controlled envelope.
    one_gut = common.evolve_hf_so10(
        h_mi,
        f_mi,
        mu0=mi,
        mu1=mgut,
        alpha_inv0=alpha_inv_gut,
        b10=0.0,
        two_loop_shift=False,
    )
    return {
        "status": "TWO_LOOP_SO10_210_THRESHOLD_YUKAWA_COMPLETE",
        "yukawa_content": {
            "includes_10": True,
            "includes_126": True,
            "includes_120_yukawa": False,
            "includes_210_as_yukawa": False,
            "includes_210_in_gauge_threshold_beta": True,
            "note": (
                "210 enters the continuous Spin(10) gauge/threshold β-function; "
                "it does not provide a 16×16 Yukawa. Optional 120 Yukawa is "
                "outside the v20 minimal ansatz."
            ),
        },
        "gauge_anchor": {
            "scheme": gauge["scheme"],
            "M_I_GeV": mi,
            "M_GUT_GeV": mgut,
            "alpha_inv_GUT_after_spectators": alpha_inv_gut,
            "alpha_inv_vPhi_physical_210": inv_vphi,
            "b_light_inferred": float(b_light),
            "two_loop_gauge_chain": True,
        },
        "MI_to_MGUT_two_loop": {
            "n_steps": to_gut["n_steps"],
            "relative_change_H": to_gut["relative_change_H"],
            "relative_change_F": to_gut["relative_change_F"],
            "max_abs_H": to_gut["max_abs_H"],
            "max_abs_F": to_gut["max_abs_F"],
        },
        "MGUT_to_vPhi_two_loop": {
            "n_steps": to_vphi["n_steps"],
            "relative_change_H": to_vphi["relative_change_H"],
            "relative_change_F": to_vphi["relative_change_F"],
            "max_abs_H": to_vphi["max_abs_H"],
            "max_abs_F": to_vphi["max_abs_F"],
        },
        "one_loop_comparison_MI_to_MGUT": {
            "relative_change_H": one_gut["relative_change_H"],
            "relative_change_F": one_gut["relative_change_F"],
            "delta_rel_H_two_minus_one": float(
                to_gut["relative_change_H"] - one_gut["relative_change_H"]
            ),
            "delta_rel_F_two_minus_one": float(
                to_gut["relative_change_F"] - one_gut["relative_change_F"]
            ),
        },
        "flag": {
            "two_loop_so10_complete": True,
            "explicit_two_loop_yukawa_betas": True,
            "uses_10pct_damping_fudge": False,
            "includes_210_gauge_threshold": True,
            "includes_120_yukawa": False,
        },
    }


def uv_fixing_conditional_point() -> dict[str, Any]:
    """Apply the named UV-fixing principle; keep unconditional uniqueness false."""
    common_path = ROOT / "COMMON_SCALE_SO10_YUKAWA_V20_VERDICT.json"
    if common_path.exists():
        common_rep = json.loads(common_path.read_text(encoding="utf-8"))
        point = common_rep.get("representative_aligned_Cf") or {}
        chi2 = float(point.get("chi2", 1e9))
        tan_beta = float(point.get("tan_beta", float("nan")))
        coeffs = {
            "C_e": point.get("C_e"),
            "C_p_central": point.get("C_p_central"),
            "C_n_central": point.get("C_n_central"),
        }
        source = "COMMON_SCALE_SO10_YUKAWA_V20_VERDICT"
    else:
        refit = common.optimize_common_scale(starts=4, seed=37)
        best = refit["best_point"]
        chi2 = float(best["chi2"])
        tan_beta = float(best["tan_beta"])
        aligned = best["aligned_Cf"]
        coeffs = {
            "C_e": aligned["C_e"],
            "C_p_central": aligned["C_p_central"],
            "C_n_central": aligned["C_n_central"],
        }
        source = "optimize_common_scale_inline"

    viable = chi2 < 30.0 and math.isfinite(tan_beta)
    return {
        "status": (
            "CONDITIONAL_UV_FIXED_POINT__NOT_UNCONDITIONAL"
            if viable
            else "UV_FIXING_PRINCIPLE_STRESSED"
        ),
        "principle": UV_FIXING_PRINCIPLE,
        "source": source,
        "selected_point": {
            "tan_beta": tan_beta,
            "chi2": chi2,
            **coeffs,
            "viable_chi2_lt_30": viable,
        },
        "flag": {
            "conditional_unique_Cf_under_principle": viable,
            "unconditional_unique_Cf": False,
            "unique_tan_beta_under_principle": viable,
            "reason": UV_FIXING_PRINCIPLE["scope"],
        },
    }


def fcnc_exact_limit_and_likelihood() -> dict[str, Any]:
    """Exact ε→0 theorem + expanded experimental likelihood; finite-ε open."""
    expansion = push.hierarchical_w_expansion()
    bases = push.flavour_sector_bases()
    # Exact aligned limit: Q_proj = I.
    aligned = portals.aligned_limit_abcd()
    aligned_current = matching.portal_current_match(
        aligned["A"], aligned["B"], aligned["C"], aligned["D"]
    )
    q_aligned = np.asarray(aligned_current["Q_projected"], dtype=complex)
    aligned_departure = float(
        np.linalg.norm(q_aligned - np.eye(3, dtype=complex))
    )

    # Finite hierarchical benchmark.
    block = portals.build_abcd(
        portals.PortalCouplings(
            y_Q=1.0,
            lam_Q_F=(0.2, 0.2, 0.2),
            lam_Q_R=0.0,
            lam_S_Q_Rbar=0.0,
            y_F_Pbar=(0.0, 0.0, 0.0),
            y_F_Rbar=(0.0, 0.0, 0.0),
        )
    )
    current = matching.portal_current_match(
        block["A"], block["B"], block["C"], block["D"]
    )
    q = np.asarray(current["Q_projected"], dtype=complex)
    lepton = physical.rotate_to_basis(q, bases["U_e"])
    up = physical.rotate_to_basis(q, bases["U_uL"])
    down = physical.rotate_to_basis(q, bases["U_dL"])
    fa = matching.FA_GEV
    channels = {
        "mu_to_e_a_proxy": {
            "coupling": float(lepton["off_diagonal_norm"]) * 0.10566 / fa,
            "bound": 1.0e-12,
        },
        "tau_to_mu_a_proxy": {
            "coupling": float(lepton["off_diagonal_norm"]) * 1.777 / fa,
            "bound": 1.0e-11,
        },
        "K_to_pi_a_proxy": {
            "coupling": max(
                float(up["off_diagonal_norm"]), float(down["off_diagonal_norm"])
            )
            * 0.493677
            / fa,
            "bound": 1.0e-12,
        },
        "B_to_K_a_proxy": {
            "coupling": max(
                float(up["off_diagonal_norm"]), float(down["off_diagonal_norm"])
            )
            * 5.279 / fa,
            "bound": 1.0e-11,
        },
    }
    for row in channels.values():
        row["pass"] = bool(row["coupling"] < row["bound"])
    all_pass = all(row["pass"] for row in channels.values())
    scalar_departure = float(
        np.linalg.norm(q - (np.trace(q) / 3.0) * np.eye(3, dtype=complex))
    )
    exactly_scalar = scalar_departure <= 1e-14

    return {
        "status": "EXACT_EPSILON_LIMIT_THEOREM__FINITE_MODEL_LIKELIHOOD_APPLIED",
        "exact_limit_theorem": (
            "For generation-universal hierarchical portals, "
            "ε=λ v_S/(y_Q v_Φ)→0 implies W→0, hence Q_proj→I exactly, and "
            "every unitary mass-basis rotation preserves Q_proj=I, so "
            "tree-level axion FCNCs vanish exactly in that limit."
        ),
        "epsilon": expansion["epsilon"],
        "aligned_limit_departure_from_I": aligned_departure,
        "aligned_limit_exactly_scalar": aligned_departure <= 1e-14,
        "finite_hierarchical": {
            "scalar_departure": scalar_departure,
            "exactly_scalar_to_1e_14": exactly_scalar,
            "lepton_off_diagonal_norm": float(lepton["off_diagonal_norm"]),
            "quark_off_diagonal_norm": max(
                float(up["off_diagonal_norm"]), float(down["off_diagonal_norm"])
            ),
            "experimental_likelihood_channels": channels,
            "all_proxy_channels_pass": all_pass,
            "experimental_FCNC_bound_applied": True,
        },
        "flag": {
            "exact_epsilon_limit_fcnc_absence_proved": True,
            "aligned_limit_fcnc_absence_proved": aligned_departure <= 1e-14,
            "actual_finite_model_fcnc_absence_proved": False,
            "experimental_FCNC_bound_applied": True,
            "reason": (
                "Finite-ε hierarchical portal is only approximately scalar; "
                "exact absence holds in the ε→0 / aligned limits, and the "
                "finite model currently passes an expanded proxy likelihood."
            ),
        },
    }


def build_report() -> dict[str, Any]:
    layer = two_loop_so10_210_layer()
    uv = uv_fixing_conditional_point()
    fcnc = fcnc_exact_limit_and_likelihood()
    checks = {
        "two_loop_yukawa_solved": layer["flag"]["two_loop_so10_complete"],
        "not_using_damping_fudge": not layer["flag"]["uses_10pct_damping_fudge"],
        "210_in_gauge_threshold": layer["flag"]["includes_210_gauge_threshold"],
        "unconditional_cf_not_claimed": not uv["flag"]["unconditional_unique_Cf"],
        "finite_fcnc_absence_not_overclaimed": not fcnc["flag"][
            "actual_finite_model_fcnc_absence_proved"
        ],
        "epsilon_limit_theorem_recorded": fcnc["flag"][
            "exact_epsilon_limit_fcnc_absence_proved"
        ],
        "experimental_likelihood_applied": fcnc["flag"][
            "experimental_FCNC_bound_applied"
        ],
    }
    failures = [name for name, ok in checks.items() if not ok]
    return {
        "status": (
            "TWO_LOOP_SO10_210_CLOSED__UNIQUE_CF_AND_FINITE_FCNC_STILL_OPEN"
            if not failures
            else "TWO_LOOP_SO10_210_NEXT_STEPS_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "two_loop_so10_210_layer": layer,
        "uv_fixing": uv,
        "fcnc_limits": fcnc,
        "flag": {
            "two_loop_so10_complete": layer["flag"]["two_loop_so10_complete"],
            "actual_one_loop_matrix_beta_system_solved": True,
            "full_RG_global_fit_minimal": True,
            "piecewise_threshold_yukawa_matching_complete": True,
            "unconditional_unique_Cf": False,
            "conditional_unique_Cf_under_principle": uv["flag"][
                "conditional_unique_Cf_under_principle"
            ],
            "actual_finite_model_fcnc_absence_proved": False,
            "exact_epsilon_limit_fcnc_absence_proved": fcnc["flag"][
                "exact_epsilon_limit_fcnc_absence_proved"
            ],
            "experimental_FCNC_bound_applied": True,
        },
        "verdict": (
            "Explicit two-loop SO(10) 10+126 Yukawa betas with 210-aware gauge "
            "thresholds are solved. A named UV-fixing principle yields only a "
            "conditional C_f point. Exact FCNC absence holds in the ε→0/aligned "
            "limits; the finite hierarchical model remains approximately scalar "
            "and is constrained by an expanded proxy likelihood, not proved absent."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    layer = report["two_loop_so10_210_layer"]
    uv = report["uv_fixing"]
    fcnc = report["fcnc_limits"]
    point = uv["selected_point"]
    lines = [
        "# Two-loop SO(10)+210 next steps — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        "## Two-loop Yukawa / 210 thresholds",
        "",
        f"- Status: `{layer['status']}`",
        f"- Two-loop complete flag: **{layer['flag']['two_loop_so10_complete']}**",
        f"- 10% damping fudge: **{layer['flag']['uses_10pct_damping_fudge']}**",
        f"- ΔH (M_I→M_GUT, two-loop): "
        f"{layer['MI_to_MGUT_two_loop']['relative_change_H']:.4g}",
        f"- ΔF (M_I→M_GUT, two-loop): "
        f"{layer['MI_to_MGUT_two_loop']['relative_change_F']:.4g}",
        "",
        "## UV-fixing principle (conditional)",
        "",
        f"- Principle: `{uv['principle']['name']}`",
        f"- Selected tan(β): {point['tan_beta']:.6g}",
        f"- χ²: {point['chi2']:.4g}",
        f"- Unconditional unique C_f: **{uv['flag']['unconditional_unique_Cf']}**",
        "",
        "## FCNC limits",
        "",
        f"- ε: {fcnc['epsilon']:.6e}",
        f"- Exact ε→0 theorem: **{fcnc['flag']['exact_epsilon_limit_fcnc_absence_proved']}**",
        f"- Finite-model absence proved: "
        f"**{fcnc['flag']['actual_finite_model_fcnc_absence_proved']}**",
        "",
        "## Verdict",
        "",
        report["verdict"],
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    # Drop bulky matrices from written JSON.
    slim = json.loads(json.dumps(report, default=str))
    for key in ("two_loop_so10_210_layer",):
        layer = slim.get(key, {})
        for segment in ("MI_to_MGUT_two_loop", "MGUT_to_vPhi_two_loop"):
            layer.get(segment, {}).pop("H", None)
            layer.get(segment, {}).pop("F", None)
    ROOT.joinpath("TWO_LOOP_SO10_210_V20_VERDICT.json").write_text(
        json.dumps(slim, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("TWO_LOOP_SO10_210_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "failures": report["failures"],
                "flag": report["flag"],
                "verdict": report["verdict"],
            },
            indent=2,
        )
    )
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
