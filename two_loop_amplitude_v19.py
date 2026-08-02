#!/usr/bin/env python3
"""Mass-dependent vacuum amplitudes for the v17 graph and v19 UV closure.

The unknown Wilson, flavour, Spin(10), Lorentz and renormalisation-group
contraction is denoted by a dimensionless coefficient.  The momentum
integrals and all displayed vev/mass dependence are evaluated explicitly.
This separation is essential: the EFT does not predict the Planck-scale
Wilson tensors, so there is no unique coefficient-free physical number.

Conventions
-----------
``s0 = v_s/sqrt(2)`` and ``phi0 = v_phi/sqrt(2)``.  A one-sided complex
vacuum coefficient ``A`` means ``V_break = A exp(i a/f_a) + h.c.``; hence
the worst-phase small-shift bound is ``2 |A| / chi``.  We also report
``|A|/chi`` for direct comparison with the convention used in v17.
"""

from __future__ import annotations

from decimal import Decimal, localcontext
import math


PI16 = 16.0 * math.pi**2


def triangle_scalar_equal(heavy_mass: float, family_mass: float) -> float:
    r"""Return the finite zero-momentum scalar triangle.

    .. math::

       I_3(M,M,m)=\int\!\frac{d^4p_E}{(2\pi)^4}
       \frac{1}{(p^2+M^2)^2(p^2+m^2)}
       =\frac{1}{16\pi^2M^2}
       \frac{1-r+r\log r}{(1-r)^2},\quad r=m^2/M^2.
    """
    mass = float(heavy_mass)
    light = float(family_mass)
    if mass <= 0.0 or light < 0.0:
        raise ValueError("masses must satisfy M>0 and m>=0")
    ratio = (light / mass) ** 2
    if ratio == 0.0:
        shape = 1.0
    elif abs(ratio - 1.0) < 1.0e-5:
        # Stable Feynman-parameter representation near the removable limit.
        # Simpson integration is deterministic and far more accurate here
        # than subtracting nearly equal logarithms.
        intervals = 20_000
        step = 1.0 / intervals

        def integrand(x: float) -> float:
            return x / (x + (1.0 - x) * ratio)

        total = integrand(0.0) + integrand(1.0)
        total += 4.0 * sum(integrand(i * step) for i in range(1, intervals, 2))
        total += 2.0 * sum(integrand(i * step) for i in range(2, intervals, 2))
        shape = total * step / 3.0
    else:
        shape = (1.0 - ratio + ratio * math.log(ratio)) / (1.0 - ratio) ** 2
    return shape / (PI16 * mass**2)


def chirality_triangle_equal(heavy_mass: float, family_mass: float) -> float:
    """Triangle including two heavy and one family chirality numerators."""
    return (
        heavy_mass**2
        * family_mass
        * triangle_scalar_equal(heavy_mass, family_mass)
    )


def divided_difference_triangle(m1: float, m2: float, m3: float) -> float:
    r"""General distinct-mass scalar triangle.

    For pairwise distinct positive squared masses ``a,b,c`` this is

    .. math:: I_3=\frac1{16\pi^2}\sum_x
       \frac{x\log x}{\prod_{y\ne x}(x-y)}.

    Degenerate cases are evaluated by the exact limiting expression.
    """
    masses = (float(m1), float(m2), float(m3))
    if any(value <= 0.0 for value in masses):
        raise ValueError("the general divided-difference form requires positive masses")
    squares = tuple(value**2 for value in masses)
    scale = max(squares)
    close = [
        abs(squares[i] - squares[j]) <= 1.0e-10 * scale
        for i in range(3)
        for j in range(i + 1, 3)
    ]
    if all(close):
        return 1.0 / (32.0 * math.pi**2 * scale)
    if close[0] and not close[1] and not close[2]:
        return triangle_scalar_equal(m1, m3)
    if close[1] and not close[0] and not close[2]:
        return triangle_scalar_equal(m1, m2)
    if close[2] and not close[0] and not close[1]:
        return triangle_scalar_equal(m2, m1)
    answer = 0.0
    for i, value in enumerate(squares):
        others = [squares[j] for j in range(3) if j != i]
        answer += value * math.log(value / scale) / (
            (value - others[0]) * (value - others[1])
        )
    return answer / PI16


def chirality_triangle(m1: float, m2: float, m3: float) -> float:
    return m1 * m2 * m3 * divided_difference_triangle(m1, m2, m3)


def p12_two_loop_amplitude(
    v_s: float,
    spectator_mass: float,
    family_mass_1: float,
    family_mass_2: float,
    reduced_planck_mass: float = 2.435e18,
    coefficient: float = 1.0,
) -> float:
    r"""One-sided coefficient of the factorised v17 two-loop graph.

    In a diagonal, degenerate spectator benchmark,

    .. math::
       |A_{2\ell}|=|C_{2\ell}|\frac{s_0^{14}}{M_{\rm Pl}^{12}}
       J(M_s,m_1)J(M_s,m_2),

    where ``C_2l`` contains the specified Wilson/group/flavour contraction.
    """
    s0 = v_s / math.sqrt(2.0)
    first = chirality_triangle_equal(spectator_mass, family_mass_1)
    second = chirality_triangle_equal(spectator_mass, family_mass_2)
    return abs(coefficient) * s0**14 * first * second / reduced_planck_mass**12


def uv_dressed_two_loop_amplitude(
    v_s: float,
    v_phi: float,
    spectator_mass: float,
    family_mass_1: float,
    family_mass_2: float,
    reduced_planck_mass: float = 2.435e18,
    coefficient: float = 1.0,
) -> float:
    """The v17 graph after four mandatory ``Phi/M_Pl`` dressings."""
    phi0 = v_phi / math.sqrt(2.0)
    return p12_two_loop_amplitude(
        v_s,
        spectator_mass,
        family_mass_1,
        family_mass_2,
        reduced_planck_mass,
        coefficient,
    ) * (phi0 / reduced_planck_mass) ** 4


def _double_pole_coefficients(
    pole: Decimal,
    other_double: Decimal,
    simple: Decimal,
) -> tuple[Decimal, Decimal]:
    d1 = other_double - pole
    d2 = simple - pole
    double_coefficient = -pole / (d1**2 * d2)
    simple_coefficient = (
        Decimal(1) / (d1**2 * d2)
        + Decimal(2) * pole / (d1**3 * d2)
        + pole / (d1**2 * d2**2)
    )
    return simple_coefficient, double_coefficient


def pentagon_scalar(
    heavy_spin_mass: float,
    spectator_mass: float,
    family_mass: float,
    decimal_precision: int = 90,
) -> float:
    r"""Exact five-propagator scalar integral for the UV ``P=13`` graph.

    .. math:: I_5=\int\!\frac{d^4p_E}{(2\pi)^4}
      \frac1{(p^2+M_\Psi^2)^2(p^2+M_s^2)^2(p^2+m_f^2)}.

    Partial fractions are evaluated with high-precision decimal arithmetic;
    this avoids catastrophic cancellation for ``M_Psi >> M_s >> m_f``.
    """
    if min(heavy_spin_mass, spectator_mass, family_mass) <= 0.0:
        raise ValueError("all masses must be positive")
    with localcontext() as context:
        context.prec = int(decimal_precision)
        a = Decimal(str(heavy_spin_mass)) ** 2
        b = Decimal(str(spectator_mass)) ** 2
        c = Decimal(str(family_mass)) ** 2
        if a == b or a == c or b == c:
            raise ValueError("pentagon_scalar currently expects distinct mass scales")
        ua, va = _double_pole_coefficients(a, b, c)
        ub, vb = _double_pole_coefficients(b, a, c)
        uc = -c / ((a - c) ** 2 * (b - c) ** 2)
        # The arbitrary logarithm scale cancels because ua+ub+uc=0.
        radial = -(ua * a.ln() + ub * b.ln() + uc * c.ln()) + va / a + vb / b
        return float(radial / Decimal(str(PI16)))


def p13_one_loop_amplitude(
    v_s: float,
    v_phi: float,
    spectator_mass: float,
    heavy_spin_mass: float,
    explicit_higgs_vev: float,
    family_mass: float,
    reduced_planck_mass: float = 2.435e18,
    coefficient: float = 1.0,
) -> float:
    """One-sided coefficient of the explicit UV ``P=13`` polygon."""
    s0 = v_s / math.sqrt(2.0)
    phi0 = v_phi / math.sqrt(2.0)
    loop = (
        heavy_spin_mass**2
        * spectator_mass**2
        * family_mass
        * pentagon_scalar(heavy_spin_mass, spectator_mass, family_mass)
    )
    background = s0**15 * phi0**2 * explicit_higgs_vev
    return abs(coefficient) * background * loop / reduced_planck_mass**13


def direct_scalar_amplitude(
    v_s: float,
    v_phi: float,
    reduced_planck_mass: float = 2.435e18,
    coefficient: float = 1.0,
) -> float:
    r"""One-sided ``Phi^4 (S_dagger)^17 / M_Pl^17`` coefficient."""
    s0 = v_s / math.sqrt(2.0)
    phi0 = v_phi / math.sqrt(2.0)
    logarithm = (
        math.log(abs(coefficient))
        + 4.0 * math.log(phi0)
        + 17.0 * math.log(s0)
        - 17.0 * math.log(reduced_planck_mass)
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
    explicit_higgs_vev_upper: float = 246.0,
    heavy_spin_yukawa: float = 1.0,
) -> dict:
    ms = v_s if spectator_mass is None else spectator_mass
    phi0 = v_phi / math.sqrt(2.0)
    heavy = heavy_spin_yukawa * phi0
    chi = chi_fourth_root**4
    undressed = p12_two_loop_amplitude(
        v_s, ms, family_mass_upper, family_mass_upper, reduced_planck_mass
    )
    dressed = uv_dressed_two_loop_amplitude(
        v_s,
        v_phi,
        ms,
        family_mass_upper,
        family_mass_upper,
        reduced_planck_mass,
    )
    p13 = p13_one_loop_amplitude(
        v_s,
        v_phi,
        ms,
        heavy,
        explicit_higgs_vev_upper,
        family_mass_upper,
        reduced_planck_mass,
    )
    direct = direct_scalar_amplitude(v_s, v_phi, reduced_planck_mass)
    entries = {
        "v17_EFT_P12_two_loop_undressed": _shift_record(undressed, chi),
        "v19_U1X_P16_two_loop_dressed": _shift_record(dressed, chi),
        "v19_U1X_P13_one_loop_heavy_threshold": _shift_record(p13, chi),
        "v19_U1X_direct_scalar_dimension21": _shift_record(direct, chi),
    }
    dominant_name, dominant = max(
        entries.items(), key=lambda item: item[1]["worst_phase_2A_over_chi"]
    )
    return {
        "status": "finite mass-dependent loop kernels evaluated; Wilson/flavour contraction remains an explicit parameter",
        "benchmark": {
            "v_s_GeV": v_s,
            "v_phi_GeV": v_phi,
            "s_vev_GeV": v_s / math.sqrt(2.0),
            "phi_vev_GeV": phi0,
            "spectator_mass_GeV": ms,
            "heavy_spin_mass_GeV": heavy,
            "family_mass_and_Higgs_insertion_upper_GeV": family_mass_upper,
            "chi_GeV4": chi,
        },
        "normalization": {
            "coefficient": "all numbers are per unit normalized Wilson x group x flavour x RG contraction",
            "potential": "V_break = A exp(i a/f_a) + h.c.",
            "shift": "worst phase |Delta theta_bar| <= 2 |A| / chi",
        },
        "exact_kernels": {
            "two_loop": "factorized product of two finite massive zero-momentum triangles",
            "P13_one_loop": "finite five-propagator integral with masses retained",
            "two_loop_scalar_kernel_GeV-2": triangle_scalar_equal(ms, family_mass_upper),
            "two_loop_chirality_kernel_GeV": chirality_triangle_equal(ms, family_mass_upper),
            "P13_scalar_kernel_GeV-6": pentagon_scalar(heavy, ms, family_mass_upper),
        },
        "results": entries,
        "dominant_computed_unit_coefficient_term": dominant_name,
        "dominant_worst_phase_shift": dominant["worst_phase_2A_over_chi"],
        "margin_below_1e-10": 1.0e-10 / dominant["worst_phase_2A_over_chi"],
        "interpretation": [
            "The old P=12 two-loop graph is not U(1)_X invariant without four Phi insertions.",
            "At vPhi=1e17 GeV the direct dimension-21 scalar operator dominates the explicitly calculated terms.",
            "None of these numbers predicts an unknown Planck-scale Wilson/flavour tensor.",
        ],
    }


__all__ = [
    "build_amplitude_report",
    "chirality_triangle",
    "chirality_triangle_equal",
    "direct_scalar_amplitude",
    "divided_difference_triangle",
    "p12_two_loop_amplitude",
    "p13_one_loop_amplitude",
    "pentagon_scalar",
    "triangle_scalar_equal",
    "uv_dressed_two_loop_amplitude",
]


if __name__ == "__main__":
    import json

    print(json.dumps(build_amplitude_report(), indent=2))
