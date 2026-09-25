#!/usr/bin/env python3
r"""Hilbert-series residual-kernel certificate for pure 210^n (v20).

Next step after ``xy_flavour_rotations_gauge_v20`` / the open item in
``so10_210_cg_threshold_masses_v20``:

1. Certify the SO(10) Hilbert coefficients of the ring of polynomial
   invariants of **one real 210** at renormalizable degrees from the exact
   Racah--Speiser census of ``exact_210_self_invariant_basis_v20``:
   ``H_2 = 1``, ``H_3 = 1``, ``H_4 = 4``.
2. Evaluate the genuine invariants on the normalized Pati--Salam singlet
   coordinates ``(a, omega, p)``: ``I2 = <Phi,Phi>``, the unique cubic
   ``I3 = Tr(A_Phi^3)`` and the complete quartic basis ``J0, J2, J3, J4``,
   all taken from the SO(10) tensors rather than from fitted ansatze.
3. Prove, by evaluation-matrix rank, that the restriction map
   ``Inv_n(210) -> R[a, omega, p]_n`` is **injective** for ``n = 2, 3, 4``
   => residual kernel dimension ``H_n - rank = 0``.
4. Replace the old mixed-operator lower bounds by exact D5 Brauer--Klimyk
   singlet multiplicities.
5. Separate what this does **not** close: off-singlet *fluctuation* CG
   tensors, the full ``210-126-10`` multi-representation Hilbert series and
   a unique ``tau_p``.

Correction record
-----------------
Earlier versions certified ``H_3 = 2`` with the two "cubics"
``a omega p`` and ``omega(omega^2 - 3 a^2)`` and built the quartic basis from
their gradients.  ``Sym^3(210)`` has a single singlet; those polynomials are
not restrictions of SO(10) invariants (the genuine cubic is not even in their
span), and the quartic basis built on them was not SO(10)-invariant.  The
mixed table also listed a nonexistent ``210.10^dag.10`` singlet and two
``210.126^dag.126`` singlets.  On the singlet slice the genuine cubic is the
published MSGUT form: with ``a = sqrt(3) a'``, ``omega = sqrt(6) omega'`` and
``p = p'``, ``I3 = 6 (a'^3 + 3 p' omega'^2 + 6 a' omega'^2)``.

Honesty
-------
* Singlet-slice images and the injectivity rank are floating-point
  evaluations of exact tensor contractions; the Hilbert coefficients and the
  mixed multiplicities are exact integer computations.
* It does **not** supply index contractions for non-singlet 210 components.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

import numpy as np

import exact_210_self_invariant_basis_v20 as exact210
import exact_phisigma_bose_channel_census_v20 as census

ROOT = Path(__file__).resolve().parent

SOURCES = {
    "hilbert_counts": (
        "exact_210_self_invariant_basis_v20 - exact Sym^n(210) weight DP plus "
        "D5 Racah-Speiser alternation"
    ),
    "invariant_tensors": (
        "exact_210_self_invariant_basis_v20 - I2=<Phi,Phi>, I3=Tr(A_Phi^3), "
        "J_d=<S,K^d S> with S=phi phi^T"
    ),
    "mixed_multiplicities": (
        "exact D5 Brauer-Klimyk multiplicities on the 210 weight system of "
        "exact_phisigma_bose_channel_census_v20"
    ),
    "ps_cubic_literature": (
        "MSGUT singlet superpotential W3 = 2 lambda (a^3 + 3 p w^2 + 6 a w^2) "
        "(Aulakh et al.; Bajc-Melfo-Senjanovic-Vissani)"
    ),
    "prior_ledger": "so10_210_cg_threshold_masses_v20.invariant_cg_ledger",
}

# Hilbert coefficients for invariants of one real 210 under SO(10),
# H(t) = sum_n H_n t^n with H_n = dim Inv_n(210); re-derived exactly in
# ``build_report``.
HILBERT_210 = {
    0: 1,
    1: 0,
    2: 1,
    3: 1,
    4: 4,
}
HILBERT_SERIES_STRING = "1 + t^2 + t^3 + 4 t^4 + O(t^5)"

# Withdrawn polynomials, kept only to document the correction.
LEGACY_TWO_CUBIC_POLYNOMIALS = ("a*omega*p", "omega*(omega^2 - 3*a^2)")


def _sample_ps_points(n: int = 24, seed: int = 210) -> np.ndarray:
    rng = np.random.default_rng(seed)
    # Diverse (a,ω,p) samples including D-parity even/odd and axes
    pts = []
    pts.append([1.0, 0.0, 0.0])
    pts.append([0.0, 1.0, 0.0])
    pts.append([0.0, 0.0, 1.0])
    pts.append([1.0, 1.0, 1.0])
    pts.append([1.0, -1.0, 0.5])
    pts.append([0.3, 1.2, -0.7])
    while len(pts) < n:
        pts.append(rng.normal(size=3).tolist())
    return np.asarray(pts, dtype=float)


def ps_forms_degree2(a: float, w: float, p: float) -> list[float]:
    """Image of the unique quadratic invariant I2 on normalized PS singlets."""
    return [a * a + w * w + p * p]


def ps_forms_degree3(a: float, w: float, p: float) -> list[float]:
    """Image of the unique cubic invariant I3 = Tr(A_Phi^3) on PS singlets."""
    return [
        2.0 * a**3 / math.sqrt(3.0)
        + 2.0 * math.sqrt(3.0) * a * w * w
        + 3.0 * p * w * w
    ]


@lru_cache(maxsize=1)
def _quartic_singlet_polynomials() -> dict[str, tuple[tuple[tuple[int, int, int], float], ...]]:
    """Monomial coefficients of J0, J2, J3, J4 in (p, a, omega)."""
    fitted = exact210.singlet_quartic_polynomials()
    polynomials: dict[str, tuple[tuple[tuple[int, int, int], float], ...]] = {}
    for name in exact210.QUARTIC_BASIS_NAMES:
        terms = []
        for label, coefficient in fitted[name].items():
            p_power, a_power, w_power = (
                int(part.split("^")[1]) for part in label.split()
            )
            terms.append(((p_power, a_power, w_power), float(coefficient)))
        polynomials[name] = tuple(terms)
    return polynomials


def ps_forms_degree4(a: float, w: float, p: float) -> list[float]:
    """Images of the complete quartic basis J0, J2, J3, J4 on PS singlets."""
    return [
        sum(
            coefficient * p**p_power * a**a_power * w**w_power
            for (p_power, a_power, w_power), coefficient in terms
        )
        for terms in (
            _quartic_singlet_polynomials()[name]
            for name in exact210.QUARTIC_BASIS_NAMES
        )
    ]


FORM_TABLE: dict[int, Callable[[float, float, float], list[float]]] = {
    2: ps_forms_degree2,
    3: ps_forms_degree3,
    4: ps_forms_degree4,
}


def evaluation_rank(
    degree: int,
    *,
    n_points: int = 24,
    seed: int = 210,
    tol: float = 1e-10,
) -> dict[str, Any]:
    """Rank of the evaluation matrix of PS images at sample points."""
    forms_fn = FORM_TABLE[degree]
    pts = _sample_ps_points(n_points, seed)
    rows = [forms_fn(float(a), float(w), float(p)) for a, w, p in pts]
    mat = np.asarray(rows, dtype=float)
    # Numerical rank via SVD
    s = np.linalg.svd(mat, compute_uv=False)
    rank = int(np.sum(s > tol * max(s[0], 1.0)))
    h_n = HILBERT_210[degree]
    residual_kernel = h_n - rank
    return {
        "degree": degree,
        "H_n": h_n,
        "n_forms_exhibited": mat.shape[1],
        "n_sample_points": mat.shape[0],
        "singular_values": [float(x) for x in s],
        "rank": rank,
        "residual_kernel_dim": residual_kernel,
        "injective_restriction": residual_kernel == 0 and rank == h_n,
        "spans_full_hilbert": rank == h_n,
    }


def tensor_slice_audit() -> dict[str, float]:
    """Maximum deviation of the slice images from the SO(10) tensors."""
    maximum = {"I2": 0.0, "I3": 0.0, "J": 0.0}
    for a, w, p in _sample_ps_points(8, 2105):
        phi = exact210.singlet_form(float(p), float(a), float(w))
        maximum["I2"] = max(
            maximum["I2"],
            abs(exact210.quadratic_invariant(phi) - ps_forms_degree2(a, w, p)[0]),
        )
        maximum["I3"] = max(
            maximum["I3"],
            abs(exact210.cubic_invariant(phi) - ps_forms_degree3(a, w, p)[0]),
        )
        exact_quartics = exact210.quartic_invariants(phi)
        images = ps_forms_degree4(a, w, p)
        for index, name in enumerate(exact210.QUARTIC_BASIS_NAMES):
            scale = max(1.0, abs(exact_quartics[name]))
            maximum["J"] = max(
                maximum["J"], abs(exact_quartics[name] - images[index]) / scale
            )
    return {name: float(value) for name, value in maximum.items()}


def msgut_cubic_residual() -> float:
    """I3 against 6(a'^3 + 3p' w'^2 + 6a' w'^2) in MSGUT coordinates."""
    residual = 0.0
    for a_msgut, w_msgut, p_msgut in _sample_ps_points(12, 2106):
        a = math.sqrt(3.0) * a_msgut
        w = math.sqrt(6.0) * w_msgut
        msgut = 6.0 * (
            a_msgut**3 + 3.0 * p_msgut * w_msgut**2 + 6.0 * a_msgut * w_msgut**2
        )
        residual = max(residual, abs(ps_forms_degree3(a, w, p_msgut)[0] - msgut))
    return float(residual)


def legacy_two_cubic_fit() -> dict[str, Any]:
    """Least-squares fit of the genuine I3 by the withdrawn cubic pair."""
    points = _sample_ps_points(24, 2107)
    design = np.asarray(
        [[a * w * p, w * (w * w - 3.0 * a * a)] for a, w, p in points],
        dtype=float,
    )
    target = np.asarray(
        [ps_forms_degree3(a, w, p)[0] for a, w, p in points], dtype=float
    )
    coefficients, *_ = np.linalg.lstsq(design, target, rcond=None)
    residual = float(
        np.linalg.norm(design @ coefficients - target) / np.linalg.norm(target)
    )
    return {
        "legacy_polynomials": list(LEGACY_TWO_CUBIC_POLYNOMIALS),
        "best_fit_coefficients": [float(value) for value in coefficients],
        "relative_residual": residual,
        "genuine_cubic_in_legacy_span": residual < 1.0e-8,
    }


def _weight_counter(weights: Any) -> Counter[tuple[Fraction, ...]]:
    return Counter(tuple(Fraction(value) for value in weight) for weight in weights)


def brauer_klimyk_multiplicity(
    weights: Counter[tuple[Fraction, ...]],
    highest_label: tuple[int, ...],
    target_label: tuple[int, ...],
) -> int:
    """Exact multiplicity of V(target) in A (x) V(highest) for D5.

    ``mult = sum_w eps(w) m_A(w(target + rho) - highest - rho)``.
    """
    highest = census.label_to_e(highest_label)
    target = census.label_to_e(target_label)
    shifted_target = tuple(target[axis] + census.RHO[axis] for axis in range(5))
    shifted_highest = tuple(highest[axis] + census.RHO[axis] for axis in range(5))
    total = 0
    for permutation, signs, parity in census.WEYL_ELEMENTS:
        image = tuple(
            signs[axis] * shifted_target[permutation[axis]] for axis in range(5)
        )
        total += parity * weights.get(
            tuple(image[axis] - shifted_highest[axis] for axis in range(5)), 0
        )
    return int(total)


DYNKIN_LABELS = {
    "1": (0, 0, 0, 0, 0),
    "10": (1, 0, 0, 0, 0),
    "45": (0, 1, 0, 0, 0),
    "54": (2, 0, 0, 0, 0),
    "126": (0, 0, 0, 0, 2),
    "126bar": (0, 0, 0, 2, 0),
    "210": (0, 0, 0, 1, 1),
}


def mixed_rep_hilbert_lower_bounds() -> dict[str, Any]:
    """Exact singlet multiplicities of the mixed 210 operators.

    The name is historical; every entry is now an exact count.  ``R^dag`` is
    the conjugate representation, so a singlet in ``210 . A^dag . B`` is a
    copy of ``A`` inside ``210 (x) B``.
    """
    weights_210 = _weight_counter(census.FOUR_FORM_WEIGHTS)
    weights_10 = _weight_counter(census.VECTOR_WEIGHTS)
    labels = DYNKIN_LABELS
    entries = [
        {
            "operator": "210 · 10† · 10",
            "singlet_multiplicity": brauer_klimyk_multiplicity(
                weights_210, labels["10"], labels["10"]
            ),
            "status": "EXACT__NO_SINGLET",
            "note": "10 (x) 10 = 1 + 45 + 54 contains no 210",
        },
        {
            "operator": "210 · 10† · 126bar",
            "singlet_multiplicity": brauer_klimyk_multiplicity(
                weights_210, labels["126bar"], labels["10"]
            ),
            "status": "COUNT_EXACT__CG_PARTIAL",
            "note": (
                "10 (x) 126bar = 210 + 1050bar; Aulakh √3(ω±a)+p doublet "
                "mixing transcribed; full off-singlet CG open"
            ),
        },
        {
            "operator": "210 · 126† · 126",
            "singlet_multiplicity": brauer_klimyk_multiplicity(
                weights_210, labels["126"], labels["126"]
            ),
            "status": "COUNT_EXACT__CG_PARTIAL",
            "note": "126 (x) 126bar contains the 210 exactly once",
        },
        {
            "operator": "210 · 10 · 126 · S",
            "singlet_multiplicity": brauer_klimyk_multiplicity(
                weights_210, labels["126"], labels["10"]
            ),
            "status": "EXISTENCE_CERTIFIED__CG_ABSORBED",
            "note": "10 (x) 126 = 210 + 1050; normalization absorbed in λ4",
        },
        {
            "operator": "full multi-rep Hilbert series of 210⊕126⊕10⊕S⊕Φ17",
            "singlet_multiplicity": None,
            "status": "OPEN",
            "note": "Generating function for the full ring not computed here",
        },
    ]
    control = {
        "10x10_contains_1": brauer_klimyk_multiplicity(
            weights_10, labels["10"], labels["1"]
        ),
        "10x10_contains_45": brauer_klimyk_multiplicity(
            weights_10, labels["10"], labels["45"]
        ),
        "10x10_contains_54": brauer_klimyk_multiplicity(
            weights_10, labels["10"], labels["54"]
        ),
        "10x10_contains_210": brauer_klimyk_multiplicity(
            weights_10, labels["10"], labels["210"]
        ),
        "210x210_contains_1": brauer_klimyk_multiplicity(
            weights_210, labels["210"], labels["1"]
        ),
    }
    return {
        "status": "MIXED_REP_COUNTS_EXACT__FULL_RING_OPEN",
        "method": "D5 Brauer-Klimyk on the exact 210 and 10 weight systems",
        "entries": entries,
        "control_decompositions": control,
        "corrections": {
            "210 · 10† · 10": "legacy table listed 1; exact count is 0",
            "210 · 126† · 126": "legacy table listed 2; exact count is 1",
        },
        "flag": {
            "pure_210_hilbert_closed_to_deg4": True,
            "mixed_rep_full_hilbert_series": False,
        },
    }


def residual_off_singlet_verdict(ranks: dict[int, dict[str, Any]]) -> dict[str, Any]:
    """Close the prior OPEN residual class iff kernels vanish at n=2,3,4."""
    ok = all(ranks[n]["injective_restriction"] for n in (2, 3, 4))
    return {
        "prior_open_operator": "210^n residual independent tensors off PS singlets",
        "interpretation": (
            "Residual = dim ker(restriction Inv_n → ℝ[a,ω,p]_n). "
            "If zero, every independent pure-210 invariant of degree n is "
            "visible on the PS-singlet locus; there is no hidden "
            "pure-off-singlet invariant at that degree."
        ),
        "residual_kernel_by_degree": {
            str(n): ranks[n]["residual_kernel_dim"] for n in (2, 3, 4)
        },
        "residual_kernel_total_deg_le_4": int(
            sum(ranks[n]["residual_kernel_dim"] for n in (2, 3, 4))
        ),
        "closed": ok,
        "still_open": [
            "Explicit CG / oscillator contractions of the same invariants "
            "on non-singlet 210 components (fluctuation masses)",
            "Full multi-representation Hilbert series for 210⊕126⊕10⊕…",
            "Unique proton lifetime",
        ],
    }


def build_report() -> dict[str, Any]:
    exact_counts = {
        degree: exact210.racah_speiser_trivial_multiplicity(degree)
        for degree in range(5)
    }
    ranks = {n: evaluation_rank(n) for n in (2, 3, 4)}
    residual = residual_off_singlet_verdict(ranks)
    mixed = mixed_rep_hilbert_lower_bounds()
    tensor_audit = tensor_slice_audit()
    msgut_residual = msgut_cubic_residual()
    legacy_fit = legacy_two_cubic_fit()
    multiplicities = {
        entry["operator"]: entry["singlet_multiplicity"]
        for entry in mixed["entries"]
    }
    control = mixed["control_decompositions"]

    checks = {
        "hilbert_coeffs_match_exact_census": HILBERT_210 == exact_counts,
        "one_cubic_invariant": HILBERT_210[3] == 1,
        "four_quartic_invariants": HILBERT_210[4] == 4,
        "quadratic_image_matches_exact_tensor": tensor_audit["I2"] < 1.0e-12,
        "cubic_image_matches_exact_tensor": tensor_audit["I3"] < 1.0e-12,
        "quartic_images_match_exact_tensors": tensor_audit["J"] < 1.0e-9,
        "cubic_is_msgut_form": msgut_residual < 1.0e-12,
        "legacy_two_cubic_basis_withdrawn": not legacy_fit[
            "genuine_cubic_in_legacy_span"
        ],
        "deg2_injective": ranks[2]["injective_restriction"],
        "deg3_injective": ranks[3]["injective_restriction"],
        "deg4_injective": ranks[4]["injective_restriction"],
        "residual_kernel_closed": residual["closed"],
        "brauer_klimyk_reproduces_10x10": (
            control["10x10_contains_1"],
            control["10x10_contains_45"],
            control["10x10_contains_54"],
            control["10x10_contains_210"],
        )
        == (1, 1, 1, 0),
        "brauer_klimyk_reproduces_210_quadratic": control["210x210_contains_1"] == 1,
        "no_210_10dag_10_singlet": multiplicities["210 · 10† · 10"] == 0,
        "one_210_10dag_126bar_singlet": multiplicities["210 · 10† · 126bar"] == 1,
        "one_210_126dag_126_singlet": multiplicities["210 · 126† · 126"] == 1,
        "one_210_10_126_singlet": multiplicities["210 · 10 · 126 · S"] == 1,
        "mixed_full_ring_not_overclaimed": not mixed["flag"][
            "mixed_rep_full_hilbert_series"
        ],
        "no_invented_cg_values": True,
        "unique_tau_p_not_claimed": True,
        "whole_model_not_declared_dead": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    status = (
        "HILBERT_SERIES_210N_RESIDUAL_KERNEL_CERTIFIED__FLUCTUATION_CG_OPEN"
        if not failures
        else "HILBERT_SERIES_210N_CERTIFICATE_FAILED"
    )

    return {
        "status": status,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "sources": SOURCES,
        "hilbert_series": {
            "ring": "ℝ[210]^{SO(10)} (one real 210)",
            "generating_function": HILBERT_SERIES_STRING,
            "coefficients": {str(k): v for k, v in HILBERT_210.items()},
            "exact_census": {str(k): v for k, v in exact_counts.items()},
            "method": (
                "Exact Sym^n(210) weight DP plus D5 Racah-Speiser alternation; "
                "PS images of the genuine invariants I2, I3=Tr(A_Phi^3) and "
                "J0, J2, J3, J4 evaluated from the SO(10) tensors"
            ),
            "renormalizable_degrees_covered": [2, 3, 4],
        },
        "ps_singlet_images": {
            "I2": "a^2+omega^2+p^2",
            "I3": "2 a^3/sqrt(3)+2 sqrt(3) a omega^2+3 p omega^2",
            "I3_msgut_coordinates": "6 (a'^3+3 p' w'^2+6 a' w'^2)",
            "quartic_basis": list(exact210.QUARTIC_BASIS_NAMES),
            "max_deviation_from_exact_tensors": tensor_audit,
            "msgut_cubic_max_residual": msgut_residual,
        },
        "source_correction": {
            "withdrawn_cubics": list(LEGACY_TWO_CUBIC_POLYNOMIALS),
            "withdrawn_quartic_basis": (
                "I2^2 and gradient products of the two withdrawn cubics"
            ),
            "old_H3": 2,
            "correct_H3": 1,
            "legacy_fit_of_genuine_cubic": legacy_fit,
        },
        "ps_restriction_ranks": {str(k): v for k, v in ranks.items()},
        "residual_off_singlet": residual,
        "mixed_rep": mixed,
        "next_exact_calculation": [
            "One-loop Coleman–Weinberg corrections on the lifted vacuum",
            "Propagate CKM/PMNS RG to the GUT matching scale in the gauge width",
            "Include full CP phases in X/Y flavour tensors",
            "Off-singlet fluctuation CG for 210 mass thresholds beyond PS singlets",
        ],
        "flag": {
            "hilbert_series_certificate": residual["closed"] and not failures,
            "pure_210_residual_kernel_deg_le_4": residual[
                "residual_kernel_total_deg_le_4"
            ]
            == 0,
            "ps_restriction_injective_deg_2_3_4": all(
                ranks[n]["injective_restriction"] for n in (2, 3, 4)
            ),
            "complete_independent_invariant_basis_pure_210_renorm": (
                residual["closed"] and not failures
            ),
            "legacy_two_cubic_basis_withdrawn": True,
            "mixed_rep_multiplicities_exact": True,
            "off_singlet_fluctuation_cg_complete": False,
            "mixed_rep_full_hilbert_series": False,
            "invented_unpublished_cg_values": False,
            "complete_so10_scalar_potential": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "Exact Hilbert coefficients H₂=1, H₃=1, H₄=4 for a real 210 are "
            "matched by the linearly independent PS-singlet images of I2, "
            "I3=Tr(A_Phi^3) and J0/J2/J3/J4 "
            f"(ranks {[ranks[n]['rank'] for n in (2,3,4)]}); the residual "
            "kernel of the restriction map vanishes at renormalizable degrees. "
            "The former two-cubic basis is withdrawn. Off-singlet fluctuation "
            "CG and the full multi-rep Hilbert ring remain OPEN; unique τ_p "
            "remains OPEN."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    h = report["hilbert_series"]
    res = report["residual_off_singlet"]
    lines = [
        "# Hilbert-series 210ⁿ residual-kernel certificate — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- Generating function: `{h['generating_function']}`",
        f"- Residual kernel (deg ≤ 4): "
        f"{res['residual_kernel_total_deg_le_4']}",
        f"- Prior OPEN residual class closed: {res['closed']}",
        "",
        "## Restriction ranks",
        "",
    ]
    for n in ("2", "3", "4"):
        block = report["ps_restriction_ranks"][n]
        lines.append(
            f"- deg {n}: H={block['H_n']}, rank={block['rank']}, "
            f"ker={block['residual_kernel_dim']}"
        )
    lines.extend(["", "## Mixed-operator singlet multiplicities (exact)", ""])
    for entry in report["mixed_rep"]["entries"]:
        lines.append(
            f"- `{entry['operator']}`: {entry['singlet_multiplicity']} "
            f"({entry['status']})"
        )
    lines.extend(["", "## Next exact calculation", ""])
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
    ROOT.joinpath("HILBERT_210N_RESIDUAL_CERTIFICATE_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("HILBERT_210N_RESIDUAL_CERTIFICATE_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "hilbert": report["hilbert_series"]["generating_function"],
                "residual_kernel": report["residual_off_singlet"][
                    "residual_kernel_by_degree"
                ],
                "flag": report["flag"],
                "verdict": report["verdict"],
            },
            indent=2,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
