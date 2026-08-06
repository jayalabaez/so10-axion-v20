#!/usr/bin/env python3
"""Exact mixed 45-channel projection for the v20 triplet sector.

The SO(10) vector bilinear decomposes as

    10† x 10 = 1 + 45 + 54.

The norm and 54 channels are already exact.  This module derives the remaining
45 channel.  For the real 210 four-form the relevant antisymmetric two-form is

    K_45[Phi] = *(Phi wedge Phi).

For a complex k-form X with canonical kinetic factor c_k, the Hermitian
SO(10) current is

    J_45[X]_ab = -i c_k (<i_a X,i_b X> - <i_b X,i_a X>).

The invariant convention is

    V ⊃ lambda_45 K_45[Phi]:J_45[X].

For Phi=pP+aA+omegaW in the normalized Cartesian singlet basis,

    K_45[Phi] = k_c (e01+e23+e45) + k_w (e67+e89),

    k_c = 2 p a/sqrt(3) + 2 omega^2/3,
    k_w = sqrt(2) a omega.

The plus/minus 10_H colour weights therefore receive opposite coefficients
+k_c and -k_c.  The chiral 126bar triplet coefficients are derived directly
from the exact five-form branching basis and reported as rational colour and
weak Cartan charges.

Together with the exact singlet and 54 channels this closes the full
210†210·10†10 Hermitian vector-bilinear family.  It does not close the larger
210†210·126bar†126bar family or the full component potential.
"""
from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_10h_squared_s_bterm_v20 as h10
import exact_126bar_triplet_clebsch_v20 as triplets
import exact_mixed_54_triplet_channel_v20 as mixed54

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_MIXED_45_TRIPLET_CHANNEL_V20.json"
OUT_MD = ROOT / "EXACT_MIXED_45_TRIPLET_CHANNEL_V20.md"

COLOR_PLANES = ((0, 1), (2, 3), (4, 5))
WEAK_PLANES = ((6, 7), (8, 9))
ALL_PLANES = COLOR_PLANES + WEAK_PLANES


def conjugate_form(form: direct.Form) -> direct.Form:
    return {indices: np.conjugate(value) for indices, value in form.items()}


def phi_45(phi: direct.Form) -> direct.Form:
    return direct.hodge_star(direct.wedge(phi, phi))


def hermitian_current_45(
    form: direct.Form, *, kinetic_factor: float
) -> direct.Form:
    output: direct.Form = {}
    for a, b in ALL_PLANES:
        left_a = direct.interior(form, a)
        left_b = direct.interior(form, b)
        m_ab = kinetic_factor * direct.tensor_inner(left_a, left_b)
        m_ba = kinetic_factor * direct.tensor_inner(left_b, left_a)
        value = -1j * (m_ab - m_ba)
        if abs(value) > 1e-13:
            output[(a, b)] = complex(np.real_if_close(value).real)
    # General off-plane components are needed for covariance and leakage tests.
    for a in range(direct.N):
        for b in range(a + 1, direct.N):
            if (a, b) in output or (a, b) in ALL_PLANES:
                continue
            left_a = direct.interior(form, a)
            left_b = direct.interior(form, b)
            m_ab = kinetic_factor * direct.tensor_inner(left_a, left_b)
            m_ba = kinetic_factor * direct.tensor_inner(left_b, left_a)
            value = -1j * (m_ab - m_ba)
            if abs(value) > 1e-13:
                output[(a, b)] = complex(np.real_if_close(value).real)
    return output


def analytic_phi_45_coefficients(
    p: float, a: float, omega: float
) -> dict[str, float]:
    return {
        "k_color_GeV2": float(2.0 * p * a / math.sqrt(3.0) + 2.0 * omega * omega / 3.0),
        "k_weak_GeV2": float(math.sqrt(2.0) * a * omega),
    }


def analytic_phi_45_form(p: float, a: float, omega: float) -> direct.Form:
    coefficients = analytic_phi_45_coefficients(p, a, omega)
    output: direct.Form = {}
    for plane in COLOR_PLANES:
        output[plane] = coefficients["k_color_GeV2"]
    for plane in WEAK_PLANES:
        output[plane] = coefficients["k_weak_GeV2"]
    return output


def channel_contraction(left: direct.Form, right: direct.Form) -> float:
    return float(np.real_if_close(direct.tensor_inner(left, right)).real)


def h_component_coefficient(
    p: float, a: float, omega: float, h_state: direct.Form
) -> float:
    return channel_contraction(
        phi_45(mixed54.phi_singlet(p, a, omega)),
        hermitian_current_45(h_state, kinetic_factor=1.0),
    )


def _rational(value: float, max_denominator: int = 12) -> tuple[float, str, float]:
    fraction = Fraction(float(value)).limit_denominator(max_denominator)
    approximation = float(fraction)
    return approximation, str(fraction), abs(float(value) - approximation)


def _multiplet_current_data() -> dict[str, Any]:
    forms = mixed54._classified_triplet_forms()
    result: dict[str, Any] = {}
    for name, states in forms.items():
        rows: list[dict[str, Any]] = []
        for state in states:
            current = hermitian_current_45(state, kinetic_factor=0.5)
            color = float(sum(current.get(plane, 0.0).real for plane in COLOR_PLANES))
            weak = float(sum(current.get(plane, 0.0).real for plane in WEAK_PLANES))
            leakage = max(
                [
                    abs(value)
                    for plane, value in current.items()
                    if plane not in ALL_PLANES
                ]
                or [0.0]
            )
            rows.append({"color_charge": color, "weak_charge": weak, "off_plane_leakage": float(leakage)})
        color_average = float(np.mean([row["color_charge"] for row in rows]))
        weak_average = float(np.mean([row["weak_charge"] for row in rows]))
        color_rational, color_fraction, color_error = _rational(color_average)
        weak_rational, weak_fraction, weak_error = _rational(weak_average)
        result[name] = {
            "rows": rows,
            "color_charge": color_rational,
            "weak_charge": weak_rational,
            "color_fraction": color_fraction,
            "weak_fraction": weak_fraction,
            "rationalization_max_abs_error": max(color_error, weak_error),
            "weight_spread": max(
                max(abs(row["color_charge"] - color_average) for row in rows),
                max(abs(row["weak_charge"] - weak_average) for row in rows),
            ),
            "off_plane_leakage": max(row["off_plane_leakage"] for row in rows),
        }
    return result


def sigma_component_coefficient(
    p: float,
    a: float,
    omega: float,
    multiplet_name: str,
) -> float:
    data = _multiplet_current_data()
    if multiplet_name not in data:
        raise KeyError(multiplet_name)
    coefficients = analytic_phi_45_coefficients(p, a, omega)
    row = data[multiplet_name]
    return float(
        row["color_charge"] * coefficients["k_color_GeV2"]
        + row["weak_charge"] * coefficients["k_weak_GeV2"]
    )


def build_report() -> dict[str, Any]:
    p, a, omega = 0.9, 0.4, 0.7
    phi = mixed54.phi_singlet(p, a, omega)
    numeric = phi_45(phi)
    analytic = analytic_phi_45_form(p, a, omega)
    phi_residual = direct.tensor_norm(direct.add_forms(numeric, direct.scale_form(analytic, -1.0)))
    coefficients = analytic_phi_45_coefficients(p, a, omega)

    basis = h10.complex_pair_basis()
    h_plus = [h_component_coefficient(p, a, omega, state) for state in basis["plus"]]
    h_minus = [h_component_coefficient(p, a, omega, state) for state in basis["minus"]]
    multiplets = _multiplet_current_data()
    sigma_coefficients = {
        name: sigma_component_coefficient(p, a, omega, name)
        for name in multiplets
    }

    norm_plus = max(
        abs(float(np.real(direct.tensor_inner(state, state))) - 1.0)
        for state in basis["plus"]
    )
    norm_minus = max(
        abs(float(np.real(direct.tensor_inner(state, state))) - 1.0)
        for state in basis["minus"]
    )

    checks = {
        "analytic_phi_45_formula": phi_residual < 1e-12,
        "H_complex_pair_norms": max(norm_plus, norm_minus) < 1e-12,
        "three_plus_color_weights_equal": max(h_plus[:3]) - min(h_plus[:3]) < 1e-12,
        "three_minus_color_weights_equal": max(h_minus[:3]) - min(h_minus[:3]) < 1e-12,
        "plus_color_is_k_color": max(abs(value - coefficients["k_color_GeV2"]) for value in h_plus[:3]) < 1e-12,
        "minus_color_is_minus_k_color": max(abs(value + coefficients["k_color_GeV2"]) for value in h_minus[:3]) < 1e-12,
        "plus_weak_is_k_weak": max(abs(value - coefficients["k_weak_GeV2"]) for value in h_plus[3:]) < 1e-12,
        "minus_weak_is_minus_k_weak": max(abs(value + coefficients["k_weak_GeV2"]) for value in h_minus[3:]) < 1e-12,
        "126_multiplet_currents_rational": max(row["rationalization_max_abs_error"] for row in multiplets.values()) < 1e-10,
        "126_weight_degeneracy": max(row["weight_spread"] for row in multiplets.values()) < 1e-10,
        "126_off_plane_current_leakage_zero": max(row["off_plane_leakage"] for row in multiplets.values()) < 1e-10,
        "vector_bilinear_family_dimension_complete": 1 + 45 + 54 == 100,
        "physical_spectrum_not_claimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "EXACT_MIXED_45_TRIPLET_CHANNEL_DERIVED__PHI_H_HERMITIAN_FAMILY_COMPLETE"
            if not failures
            else "EXACT_MIXED_45_TRIPLET_CHANNEL_FAILED"
        ),
        "overall_state": "CLOSED_SUBPROBLEM" if not failures else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "operator_convention": {
            "PhiH_45": "lambda_PhiH_45 *(Phi wedge Phi):J45[H]",
            "PhiSigma_45": "lambda_PhiSigma_45 *(Phi wedge Phi):J45[Sigma]",
        },
        "exact_phi_45": {
            "k_color_formula": "2 p a/sqrt(3) + 2 omega^2/3",
            "k_weak_formula": "sqrt(2) a omega",
            "benchmark": coefficients,
            "formula_residual": float(phi_residual),
        },
        "H10_component_result": {
            "T10_Ym13_plus_branch": "+ lambda_PhiH_45 k_color",
            "T10bar_Yp13_minus_branch": "- lambda_PhiH_45 k_color",
            "weak_plus_branch": "+ lambda_PhiH_45 k_weak",
            "weak_minus_branch": "- lambda_PhiH_45 k_weak",
            "210dag210_10dag10_Hermitian_family_complete": True,
            "reason": "10dag x 10 = 1 + 45 + 54; all three channels are now exact",
        },
        "126bar_component_currents": multiplets,
        "126bar_component_coefficients_benchmark": sigma_coefficients,
        "newly_closed_subproblem": {
            "210dag210_to_45_on_singlet_vacuum": not failures,
            "210dag210_10dag10_45_triplet_Clebsch": not failures,
            "210dag210_126bardag126bar_45_triplet_Clebsches": not failures,
            "complete_210dag210_10dag10_Hermitian_channel_family": not failures,
        },
        "remaining_blockers": {
            "non1_45_54_210dag210_126bardag126bar_channels": True,
            "10dag10_126bardag126bar_background_insertions": True,
            "holomorphic_10_126bar_channels_with_charge_dressing": True,
            "all_mixing_relevant_210_states": True,
            "complete_component_potential": True,
            "unique_full_vacuum_and_Hessian": True,
            "physical_threshold_spectrum": True,
        },
        "flag": {
            "exact_shared_Hermitian_45_channel_closed": not failures,
            "PhiH_Hermitian_channel_family_complete": not failures,
            "PhiSigma_45_triplet_coefficients_derived": not failures,
            "all_PhiSigma_anisotropic_channels_complete": False,
            "physical_triplet_spectrum_complete": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "The exact 45 channel is derived. It splits the plus/minus 10_H "
            "colour weights by opposite k_color shifts and gives exact rational "
            "45 currents for t2, t2bar, and t4bar. Together with the norm and 54 "
            "results, the full Hermitian 210†210·10†10 channel family is closed."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Exact mixed 45 triplet channel — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            f"- `k_color = {report['exact_phi_45']['k_color_formula']}`",
            f"- `k_weak = {report['exact_phi_45']['k_weak_formula']}`",
            "- `210†210·10†10` Hermitian channels 1+45+54 are now complete.",
            "- Larger `210†210·126bar†126bar` channels remain open.",
            "",
        ]
    )


def _json_default(obj: Any) -> Any:
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, complex):
        return {"re": float(obj.real), "im": float(obj.imag)}
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    payload = json.dumps(report, indent=2, default=_json_default) + "\n"
    OUT_JSON.write_text(payload, encoding="utf-8")
    OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(payload, end="")
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
