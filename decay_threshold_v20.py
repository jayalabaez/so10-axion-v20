#!/usr/bin/env python3
"""Finite two-loop matching for the decay-safe v20 ``P=8`` closure.

Four dimension-five portals and one dimension-eight spectator spurion form
a connected two-loop graph after inserting only renormalizable masses and
decay Yukawas.  The two loop momenta factorize.  Each loop contains two
spectator propagators, two heavy-anomalon propagators and two family
propagators, with one momentum numerator from each family line.

Unknown Wilson, flavour, Yukawa, group and RG contractions are kept in one
dimensionless normalized coefficient.  The finite momentum kernel and all
displayed mass/vev dependence are evaluated exactly.
"""

from __future__ import annotations

from decimal import Decimal, localcontext
import math

from two_loop_amplitude_v19 import (
    direct_scalar_amplitude,
    p12_two_loop_amplitude,
    uv_dressed_two_loop_amplitude,
)


PI_DECIMAL = Decimal(
    "3.141592653589793238462643383279502884197169399375105820974944592307816406286"
)


def _repeated_pole_coefficients(
    pole: Decimal,
    other_a: Decimal,
    other_b: Decimal,
) -> tuple[Decimal, Decimal]:
    """Return A,B for A/(t+pole)+B/(t+pole)^2."""
    differences = (other_a - pole, other_b - pole)
    double = pole**2 / (differences[0] ** 2 * differences[1] ** 2)
    simple = double * (
        -Decimal(2) / pole
        - Decimal(2) / differences[0]
        - Decimal(2) / differences[1]
    )
    return simple, double


def scalar_chain_integral(
    heavy_mass: float,
    spectator_mass: float,
    family_mass: float,
    decimal_precision: int = 100,
) -> float:
    r"""Return the finite scalar part of one v20 loop.

    .. math::
       I_{222}^{(p^2)}=\int\!\frac{d^4p_E}{(2\pi)^4}
       \frac{p^2}{(p^2+M_H^2)^2(p^2+M_s^2)^2(p^2+m_f^2)^2}.

    The radial rational function is decomposed into its three repeated
    poles with high-precision decimal arithmetic, avoiding cancellation
    across the hierarchy ``M_H >> M_s >> m_f``.
    """
    if min(heavy_mass, spectator_mass, family_mass) <= 0.0:
        raise ValueError("all masses must be positive")
    with localcontext() as context:
        context.prec = int(decimal_precision)
        poles = tuple(
            Decimal(str(value)) ** 2
            for value in (heavy_mass, spectator_mass, family_mass)
        )
        if len(set(poles)) != 3:
            raise ValueError("scalar_chain_integral currently requires distinct masses")
        simples: list[Decimal] = []
        doubles: list[Decimal] = []
        for index, pole in enumerate(poles):
            others = [poles[j] for j in range(3) if j != index]
            simple, double = _repeated_pole_coefficients(pole, *others)
            simples.append(simple)
            doubles.append(double)
        radial = -sum(
            (coefficient * pole.ln() for coefficient, pole in zip(simples, poles)),
            Decimal(0),
        ) + sum(
            (coefficient / pole for coefficient, pole in zip(doubles, poles)),
            Decimal(0),
        )
        return float(radial / (Decimal(16) * PI_DECIMAL**2))


def chirality_chain(
    heavy_mass: float,
    spectator_mass: float,
    family_mass: float,
) -> float:
    r"""One-loop chain including four chirality-mass numerators.

    ``K = M_H^2 M_s^2 I_222^(p^2)`` has mass dimension ``-2``.
    """
    return (
        heavy_mass**2
        * spectator_mass**2
        * scalar_chain_integral(heavy_mass, spectator_mass, family_mass)
    )


def p8_decay_threshold_amplitude(
    v_s: float,
    spectator_mass: float,
    heavy_mass: float,
    family_mass: float,
    higgs_vev_upper: float,
    reduced_planck_mass: float = 2.435e18,
    coefficient: float = 1.0,
) -> float:
    r"""One-sided coefficient of the factorized v20 two-loop graph.

    .. math::
       |A_8|=|C_8|\frac{s_0^{14}h^2}{M_{\rm Pl}^8}
       K(M_H,M_s,m_f)^2,
       \qquad s_0=v_S/\sqrt2.

    ``C_8`` contains the four decay Yukawas, two family Yukawas and the
    normalized Wilson/group/flavour/RG contraction.  Setting the explicit
    Higgs insertion to 246 GeV and ``|C_8|=1`` is a conservative benchmark,
    not a prediction of those couplings.
    """
    if min(v_s, spectator_mass, heavy_mass, family_mass, higgs_vev_upper) <= 0.0:
        raise ValueError("all scales must be positive")
    s0 = v_s / math.sqrt(2.0)
    loop = chirality_chain(heavy_mass, spectator_mass, family_mass)
    logarithm = (
        math.log(abs(coefficient))
        + 14.0 * math.log(s0)
        + 2.0 * math.log(higgs_vev_upper)
        - 8.0 * math.log(reduced_planck_mass)
        + 2.0 * math.log(loop)
    )
    return math.exp(logarithm)


def _shift_record(amplitude: float, chi: float) -> dict:
    ratio = amplitude / chi
    return {
        "one_sided_amplitude_GeV4": amplitude,
        "A_over_chi": ratio,
        "worst_phase_2A_over_chi": 2.0 * ratio,
        "safe_below_1e-10_for_unit_coefficient": 2.0 * ratio < 1.0e-10,
    }


def build_amplitude_report(
    v_s: float = 6.313855e11,
    v_phi: float = 1.0e17,
    reduced_planck_mass: float = 2.435e18,
    chi_fourth_root: float = 75.5e-3,
    spectator_mass: float | None = None,
    family_mass_upper: float = 246.0,
    higgs_vev_upper: float = 246.0,
    heavy_yukawa: float = 1.0,
) -> dict:
    ms = v_s if spectator_mass is None else spectator_mass
    heavy = heavy_yukawa * v_phi / math.sqrt(2.0)
    chi = chi_fourth_root**4
    undressed = p12_two_loop_amplitude(
        v_s,
        ms,
        family_mass_upper,
        family_mass_upper,
        reduced_planck_mass,
    )
    dressed = uv_dressed_two_loop_amplitude(
        v_s,
        v_phi,
        ms,
        family_mass_upper,
        family_mass_upper,
        reduced_planck_mass,
    )
    p8 = p8_decay_threshold_amplitude(
        v_s,
        ms,
        heavy,
        family_mass_upper,
        higgs_vev_upper,
        reduced_planck_mass,
    )
    direct = direct_scalar_amplitude(v_s, v_phi, reduced_planck_mass)
    entries = {
        "v17_EFT_P12_two_loop_undressed_diagnostic": _shift_record(undressed, chi),
        "v20_U1X_P16_old_graph_dressed": _shift_record(dressed, chi),
        "v20_U1X_P8_decay_threshold_two_loop": _shift_record(p8, chi),
        "v20_U1X_direct_scalar_dimension21": _shift_record(direct, chi),
    }
    dominant_name, dominant = max(
        entries.items(), key=lambda item: item[1]["worst_phase_2A_over_chi"]
    )
    chain = chirality_chain(heavy, ms, family_mass_upper)
    return {
        "status": (
            "finite decay-threshold kernel evaluated; normalized Wilson/flavour/"
            "Yukawa/group/RG contraction remains explicit"
        ),
        "benchmark": {
            "v_s_GeV": v_s,
            "v_phi_GeV": v_phi,
            "s_vev_GeV": v_s / math.sqrt(2.0),
            "spectator_mass_GeV": ms,
            "heavy_mass_GeV": heavy,
            "family_mass_GeV": family_mass_upper,
            "higgs_insertion_upper_GeV": higgs_vev_upper,
            "chi_GeV4": chi,
        },
        "normalization": {
            "coefficient": (
                "per unit normalized Wilson x decay Yukawa x family Yukawa x "
                "group x flavour x RG contraction"
            ),
            "potential": "V_break = A exp(i a/f_a) + h.c.",
            "shift": "worst phase |Delta theta_bar| <= 2 |A| / chi",
        },
        "exact_kernel": {
            "integral": "I_222^(p2) with all three masses retained",
            "chirality_chain_GeV_inverse2": chain,
            "hierarchy_shape_16pi2_Mheavy2_K": (
                16.0 * math.pi**2 * heavy**2 * chain
            ),
            "two_loop_factorizes": True,
        },
        "results": entries,
        "dominant_computed_unit_coefficient_term": dominant_name,
        "dominant_worst_phase_shift": dominant["worst_phase_2A_over_chi"],
        "margin_below_1e-10": 1.0e-10 / dominant["worst_phase_2A_over_chi"],
    }


__all__ = [
    "build_amplitude_report",
    "chirality_chain",
    "p8_decay_threshold_amplitude",
    "scalar_chain_integral",
]


if __name__ == "__main__":
    import json

    print(json.dumps(build_amplitude_report(), indent=2))
