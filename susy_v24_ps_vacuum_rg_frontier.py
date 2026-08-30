#!/usr/bin/env python3
"""Exact Z11-primary V24 vacuum/RG/phenomenology frontier for minimal SUSY PS.

The gauge/vacuum architecture and published Z5 control are the minimal N=5
model of Kawamura and Raby, arXiv:2009.04582.  The selected V24 selector is the
derived Z4R x Z11, rP=2 variant.  This producer deliberately separates exact
algebraic witnesses from phenomenological assumptions.  In particular, a
zero-energy global-SUSY PS-breaking branch, the colored/exotic mass ranks, the
discrete mixed-anomaly residues, and one/two-loop gauge-only running are
executable.  The Green--Schwarz sector, soft/Kahler stabilization, complete
thresholds, domain-wall history, flavour prediction, and proton pole
calculation remain open and no full G1--G8 gate is claimed.

Because the selected Z11 has a universal nonzero mixed anomaly, it is only
Green--Schwarz eligible.  Its P-only two-cosine arithmetic is retained as a
diagnostic, but it is not a discrete-gauge wall solution until the shifting GS
axion, gauge quotient, and full vacuum lattice are supplied.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


HERE = Path(__file__).resolve().parent
JSON_PATH = HERE / "SUSY_V24_PS_VACUUM_RG_FRONTIER.json"
MD_PATH = HERE / "SUSY_V24_PS_VACUUM_RG_FRONTIER.md"

SOURCE_URL = "https://arxiv.org/abs/2009.04582"
SOURCE_HTML = "https://arxiv.org/html/2009.04582v1"

GROUPS_PS = ("SU4C", "SU2L", "SU2R")
GROUPS_SM = ("U1Y_GUT", "SU2L", "SU3C")


def fstr(value: Fraction | int) -> int | str:
    value = Fraction(value)
    return value.numerator if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def canonical_sha(value: Mapping[str, Any]) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def matrix_rank(matrix: Sequence[Sequence[Fraction | int]]) -> int:
    rows = [[Fraction(x) for x in row] for row in matrix]
    if not rows:
        return 0
    nrows, ncols = len(rows), len(rows[0])
    rank = 0
    for col in range(ncols):
        pivot = next((r for r in range(rank, nrows) if rows[r][col]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][col]
        rows[rank] = [x / scale for x in rows[rank]]
        for r in range(nrows):
            if r != rank and rows[r][col]:
                factor = rows[r][col]
                rows[r] = [x - factor * y for x, y in zip(rows[r], rows[rank])]
        rank += 1
        if rank == nrows:
            break
    return rank


def determinant_2x2(matrix: Sequence[Sequence[Fraction | int]]) -> Fraction:
    return Fraction(matrix[0][0]) * Fraction(matrix[1][1]) - Fraction(matrix[0][1]) * Fraction(matrix[1][0])


def ps_fields() -> tuple[dict[str, Any], ...]:
    """Minimal Table-3 fields, including the one complete vectorlike family."""
    return (
        {"name": "H", "PS_rep": [1, 2, 2], "multiplicity": 1, "Z4R": 0, "Z5": 0, "PQ": 0, "role": "MSSM_bidoublet"},
        {"name": "Q", "PS_rep": [4, 2, 1], "multiplicity": 3, "Z4R": 1, "Z5": 0, "PQ": 0, "role": "three_families"},
        {"name": "Qc", "PS_rep": [4, 1, 2], "multiplicity": 3, "Z4R": 1, "Z5": 0, "PQ": 0, "role": "three_families_conjugate_SU4_rep"},
        {"name": "X", "PS_rep": [1, 1, 1], "multiplicity": 1, "Z4R": 2, "Z5": 0, "PQ": 0, "role": "PS_F_term_driver"},
        {"name": "Sc", "PS_rep": [4, 1, 2], "multiplicity": 1, "Z4R": 0, "Z5": 0, "PQ": 0, "role": "PS_breaking_conjugate_SU4_rep"},
        {"name": "Sbarc", "PS_rep": [4, 1, 2], "multiplicity": 1, "Z4R": 0, "Z5": 0, "PQ": 0, "role": "PS_breaking_SU4_rep"},
        {"name": "Sigma", "PS_rep": [6, 1, 1], "multiplicity": 1, "Z4R": 2, "Z5": 0, "PQ": 0, "role": "colored_partner"},
        {"name": "PsiBar", "PS_rep": [4, 2, 1], "multiplicity": 1, "Z4R": 0, "Z5": 4, "PQ": -1, "role": "KSVZ_vectorlike_left_conjugate"},
        {"name": "Psi", "PS_rep": [4, 2, 1], "multiplicity": 1, "Z4R": 1, "Z5": 0, "PQ": 0, "role": "KSVZ_vectorlike_left"},
        {"name": "Psic", "PS_rep": [4, 1, 2], "multiplicity": 1, "Z4R": 1, "Z5": 0, "PQ": 0, "role": "KSVZ_vectorlike_right_conjugate_SU4_rep"},
        {"name": "PsiBarc", "PS_rep": [4, 1, 2], "multiplicity": 1, "Z4R": 0, "Z5": 4, "PQ": -1, "role": "KSVZ_vectorlike_right"},
        {"name": "P", "PS_rep": [1, 1, 1], "multiplicity": 1, "Z4R": 1, "Z5": 1, "PQ": 1, "role": "PQ_breaking"},
    )


def selected_z11_fields() -> tuple[dict[str, Any], ...]:
    """Apply the derived Z11,rP=2 charges without changing gauge content."""
    selected: list[dict[str, Any]] = []
    for source_row in ps_fields():
        row = dict(source_row)
        row.pop("Z5")
        row["Z11"] = 0
        if row["name"] == "P":
            row["Z4R"], row["Z11"] = 2, 1
        elif row["name"] in ("PsiBar", "PsiBarc"):
            row["Z4R"], row["Z11"] = 3, 10
        elif row["name"] in ("Psi", "Psic"):
            row["Z4R"], row["Z11"] = 1, 0
        selected.append(row)
    return tuple(selected)


def dynkin_and_casimir(group: str, dimension: int) -> tuple[Fraction, Fraction]:
    if dimension == 1:
        return Fraction(0), Fraction(0)
    if group == "SU4C" and dimension == 4:
        return Fraction(1, 2), Fraction(15, 8)
    if group == "SU4C" and dimension == 6:
        return Fraction(1), Fraction(5, 2)
    if group in ("SU2L", "SU2R") and dimension == 2:
        return Fraction(1, 2), Fraction(3, 4)
    raise ValueError((group, dimension))


def ps_rg_coefficients(fields: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    cg = {"SU4C": Fraction(4), "SU2L": Fraction(2), "SU2R": Fraction(2)}
    ledgers: list[dict[str, Any]] = []
    sums = {g: Fraction(0) for g in GROUPS_PS}
    for row in fields:
        dims = dict(zip(GROUPS_PS, row["PS_rep"]))
        mult = Fraction(row["multiplicity"])
        srow: dict[str, Fraction] = {}
        for group in GROUPS_PS:
            t, _ = dynkin_and_casimir(group, dims[group])
            spectators = math.prod(dims[g] for g in GROUPS_PS if g != group)
            srow[group] = mult * t * spectators
            sums[group] += srow[group]
        ledgers.append({"name": row["name"], "dims": dims, "S": srow})

    b = {g: sums[g] - 3 * cg[g] for g in GROUPS_PS}
    big_b: dict[str, dict[str, Fraction]] = {g: {} for g in GROUPS_PS}
    for ga in GROUPS_PS:
        for gb in GROUPS_PS:
            value = Fraction(0)
            if ga == gb:
                value += -6 * cg[ga] ** 2 + 2 * cg[ga] * sums[ga]
            for row in ledgers:
                _, cb = dynkin_and_casimir(gb, row["dims"][gb])
                value += 4 * row["S"][ga] * cb
            big_b[ga][gb] = value

    return {
        "scheme": "N=1_SUSY_DRbar_gauge_only",
        "group_order": list(GROUPS_PS),
        "sum_Dynkin": {g: fstr(sums[g]) for g in GROUPS_PS},
        "b": [fstr(b[g]) for g in GROUPS_PS],
        "B": [[fstr(big_b[a][c]) for c in GROUPS_PS] for a in GROUPS_PS],
        "field_contributions": [
            {"name": row["name"], "S": {g: fstr(row["S"][g]) for g in GROUPS_PS}}
            for row in ledgers
        ],
        "formula": "b_a=S_a-3C_a(G); B_ab=delta_ab[-6C_a(G)^2+2C_a(G)S_a]+4 sum_i S_a(i) C_b(i)",
    }


def sm_stage_matrices() -> dict[str, Any]:
    mssm_b = (Fraction(33, 5), Fraction(1), Fraction(-3))
    mssm_b2 = (
        (Fraction(199, 25), Fraction(27, 5), Fraction(88, 5)),
        (Fraction(9, 5), Fraction(25), Fraction(24)),
        (Fraction(11, 5), Fraction(9), Fraction(14)),
    )
    delta_b = (Fraction(4), Fraction(4), Fraction(4))
    delta_b2 = (
        (Fraction(76, 15), Fraction(12, 5), Fraction(176, 15)),
        (Fraction(4, 5), Fraction(28), Fraction(16)),
        (Fraction(22, 15), Fraction(6), Fraction(136, 3)),
    )
    total_b = tuple(x + y for x, y in zip(mssm_b, delta_b))
    total_b2 = tuple(tuple(mssm_b2[i][j] + delta_b2[i][j] for j in range(3)) for i in range(3))
    return {
        "group_order": list(GROUPS_SM),
        "MSSM": {
            "b": [fstr(x) for x in mssm_b],
            "B": [[fstr(x) for x in row] for row in mssm_b2],
        },
        "one_complete_vectorlike_PS_family": {
            "representation": "(4,2,1)+(bar4,2,1)+(bar4,1,2)+(4,1,2)",
            "Delta_b": [fstr(x) for x in delta_b],
            "Delta_B": [[fstr(x) for x in row] for row in delta_b2],
            "universal_one_loop_threshold": True,
        },
        "MSSM_plus_vectorlike_family": {
            "b": [fstr(x) for x in total_b],
            "B": [[fstr(x) for x in row] for row in total_b2],
        },
    }


def rk4_gauge(
    alpha_initial: Sequence[float],
    b: Sequence[float],
    big_b: Sequence[Sequence[float]],
    scale_ratio: float,
    steps: int = 60000,
) -> list[float]:
    alpha = [float(x) for x in alpha_initial]
    h = math.log(scale_ratio) / steps

    def derivative(values: Sequence[float]) -> list[float]:
        return [
            values[i] ** 2 / (2 * math.pi)
            * (b[i] + sum(big_b[i][j] * values[j] for j in range(len(values))) / (4 * math.pi))
            for i in range(len(values))
        ]

    for _ in range(steps):
        k1 = derivative(alpha)
        k2 = derivative([alpha[i] + h * k1[i] / 2 for i in range(len(alpha))])
        k3 = derivative([alpha[i] + h * k2[i] / 2 for i in range(len(alpha))])
        k4 = derivative([alpha[i] + h * k3[i] for i in range(len(alpha))])
        alpha = [alpha[i] + h * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) / 6 for i in range(len(alpha))]
    return alpha


def running_witness(ps_rg: Mapping[str, Any]) -> dict[str, Any]:
    f_pq, v_ps, cutoff, reduced_planck = 1.0e10, 1.0e16, 1.0e18, 2.435e18
    alpha_baseline_inverse = 24.0
    delta_b = 4.0
    shifted_inverse = alpha_baseline_inverse - delta_b / (2 * math.pi) * math.log(v_ps / f_pq)
    b = [float(Fraction(str(x))) for x in ps_rg["b"]]
    big_b = [[float(Fraction(str(x))) for x in row] for row in ps_rg["B"]]
    endpoint = rk4_gauge([1 / shifted_inverse] * 3, b, big_b, cutoff / v_ps)
    planck_endpoint = rk4_gauge([1 / shifted_inverse] * 3, b, big_b, reduced_planck / v_ps)
    two_loop_terms = [sum(big_b[i][j] * endpoint[j] for j in range(3)) / (4 * math.pi) for i in range(3)]
    planck_two_loop_terms = [sum(big_b[i][j] * planck_endpoint[j] for j in range(3)) / (4 * math.pi) for i in range(3)]
    return {
        "benchmark_scales_GeV": {
            "fPQ": f_pq,
            "vPS": v_ps,
            "source_cutoff": cutoff,
            "reduced_Planck": reduced_planck,
        },
        "baseline_MSSM_alphaG_inverse_without_PQ_family": alpha_baseline_inverse,
        "complete_vectorlike_Delta_b": [4, 4, 4],
        "threshold_formula": "alphaG^-1 -> alphaG^-1 - 4/(2*pi)*ln(vPS/fPQ)",
        "alphaPS_inverse_at_vPS_after_complete_family": round(shifted_inverse, 12),
        "coupled_two_loop_gauge_only": {
            "steps": 60000,
            "scale_ratio": cutoff / v_ps,
            "alpha_at_cutoff": [round(x, 15) for x in endpoint],
            "alpha_inverse_at_cutoff": [round(1 / x, 12) for x in endpoint],
            "finite_to_cutoff": all(math.isfinite(x) and 0 < x < 1 for x in endpoint),
            "two_loop_bracket_terms_at_cutoff": [round(x, 12) for x in two_loop_terms],
            "two_loop_over_one_loop_bracket_at_cutoff": [round(two_loop_terms[i] / b[i], 12) for i in range(3)],
            "precision_warning": "SU4C has b=1, so its two-loop gauge bracket is comparable to its one-loop bracket; Yukawa and three-loop terms are required for precision unification.",
        },
        "coupled_two_loop_gauge_only_reduced_Planck": {
            "steps": 60000,
            "scale_ratio": reduced_planck / v_ps,
            "alpha_at_reduced_Planck": [round(x, 15) for x in planck_endpoint],
            "alpha_inverse_at_reduced_Planck": [round(1 / x, 12) for x in planck_endpoint],
            "finite_to_reduced_Planck": all(math.isfinite(x) and 0 < x < 1 for x in planck_endpoint),
            "two_loop_bracket_terms_at_reduced_Planck": [round(x, 12) for x in planck_two_loop_terms],
            "two_loop_over_one_loop_bracket_at_reduced_Planck": [round(planck_two_loop_terms[i] / b[i], 12) for i in range(3)],
            "interpretation": "Formal gauge-only continuation to MPlanck(reduced), beyond the source Lambda=1e18 cutoff; this is the Planck-window perturbativity diagnostic, not an EFT precision prediction.",
        },
        "abelian_kinetic_mixing": {
            "present": False,
            "reason": "Above vPS all three factors are simple non-Abelian groups; below one-step PS breaking only U1Y remains. There is no interval with two unbroken U(1) factors.",
            "one_step_matching": "alpha1^-1=(2/5) alpha4^-1+(3/5) alphaR^-1",
            "staged_U1xU1_breaking_assumed": False,
        },
        "scope": "common-boundary gauge-only benchmark; physical superpartner, PS, Yukawa, and scheme thresholds are not fitted",
    }


def selector_and_anomalies() -> dict[str, Any]:
    r = p = 1
    h = s = 0
    npsi = 1
    a4r = {
        "SU4C": 1 - (r + r) * npsi,
        "SU2L": 1 - 2 * r * npsi,
        "SU2R": 1 - 2 * r * npsi,
    }
    a5 = {
        "SU4C": -2 * s - 3 * h - (p + p) * npsi,
        "SU2L": h - 2 * (h + s) * 3 - 2 * p * npsi,
        "SU2R": h + 2 * s * 3 - 2 * p * npsi,
    }
    pure_w = next(m for m in range(1, 101) if m % 4 == 2 and m % 5 == 0)
    pure_k = next(m for m in range(1, 101) if m % 4 == 0 and m % 5 == 0)

    def allowed(names: Sequence[str], target_r: int = 2, target_z: int = 0) -> bool:
        rows = {row["name"]: row for row in ps_fields()}
        return sum(rows[n]["Z4R"] for n in names) % 4 == target_r and sum(rows[n]["Z5"] for n in names) % 5 == target_z

    return {
        "minimal_choice_Eq46": {"N": 5, "r": 1, "p": 1, "rPsi": 1, "h": 0, "pPsi": 0, "s": 0, "Npsi": 1},
        "mixed_discrete_anomalies": {
            "Z4R_raw": a4r,
            "Z4R_mod2": {g: value % 2 for g, value in a4r.items()},
            "Z4R_universal": len({value % 2 for value in a4r.values()}) == 1,
            "Z4R_zero": all(value % 2 == 0 for value in a4r.values()),
            "Z5_raw": a5,
            "Z5_mod5": {g: value % 5 for g, value in a5.items()},
            "Z5_universal": len({value % 5 for value in a5.values()}) == 1,
            "Z5_zero": all(value % 5 == 0 for value in a5.values()),
            "interpretation": "Both residue triples are universal but nonzero; a discrete Green--Schwarz completion is required and is not specified by the four-dimensional source model.",
        },
        "operator_checks": {
            "Q_H_Qc": allowed(("Q", "H", "Qc")),
            "X_Sbarc_Sc": allowed(("X", "Sbarc", "Sc")),
            "Sc_Sigma_Sc": allowed(("Sc", "Sigma", "Sc")),
            "Sbarc_Sigma_Sbarc": allowed(("Sbarc", "Sigma", "Sbarc")),
            "P_PsiBar_Psi": allowed(("P", "PsiBar", "Psi")),
            "P_PsiBarc_Psic": allowed(("P", "PsiBarc", "Psic")),
            "bare_H2_forbidden": not allowed(("H", "H")),
        },
        "leading_pure_P_superpotential_power": pure_w,
        "leading_pure_P_Kahler_holomorphic_power": pure_k,
        "PQ_quality_operator": "P^10/Lambda^7",
    }


def z11_rp2_repair_variant() -> dict[str, Any]:
    """Derived GS-eligible selector with conditional P-only harmonic arithmetic."""
    ndw = 4
    r_p, p_p, r_psi, p_psi = 2, 1, 1, 0
    r_bar = (2 - r_p - r_psi) % 4
    p_bar = (-p_p - p_psi) % 11
    npsi, h, s = 1, 0, 0
    anomalies_r = {
        "SU4C": 1 - 2 * r_p * npsi,
        "SU2L": 1 - 2 * r_p * npsi,
        "SU2R": 1 - 2 * r_p * npsi,
    }
    anomalies_11 = {
        "SU4C": -2 * s - 3 * h - 2 * p_p * npsi,
        "SU2L": h - 2 * (h + s) * 3 - 2 * p_p * npsi,
        "SU2R": h + 2 * s * 3 - 2 * p_p * npsi,
    }
    leading_w = next(m for m in range(1, 200) if m * r_p % 4 == 2 and m * p_p % 11 == 0)
    leading_k = next(m for m in range(1, 300) if m * r_p % 4 == 0 and m * p_p % 11 == 0)

    chi = 0.0756**4
    w0, cutoff = 1.0e5, 1.0e18
    axion_mass_at_fa_1e12_eV = 5.6925e-6
    mplanck_reduced = 2.435e18
    gstar_bbn = 10.75
    h_bbn = math.sqrt(math.pi**2 * gstar_bbn / 90) * (1.0e-3) ** 2 / mplanck_reduced
    # With NDW=4 and canonical single-P normalization, sigma=8 sqrt(chi) f_a=2 sqrt(chi)<P>.
    # The A term plus its Hermitian conjugate has cosine amplitude epsilon=2*c11*w0*f^11/Lambda^8.
    maximum_f_quality = (1.0e-10 * chi * ndw / leading_w * cutoff**8 / (2 * w0)) ** (1 / 11)
    minimum_f_bbn = (2 * math.sqrt(chi) * h_bbn * cutoff**8 / (2 * w0)) ** (1 / 10)
    minimum_f_domination = (4 * chi * cutoff**8 / (6 * w0 * mplanck_reduced**2)) ** (1 / 9)
    lower = max(minimum_f_bbn, minimum_f_domination)
    witness_f = 1.76e11
    witness_fa = witness_f / ndw
    witness_monomial = w0 * witness_f**11 / cutoff**8
    witness_bias = 2 * witness_monomial
    witness_sigma = 8 * math.sqrt(chi) * witness_fa
    witness_h_decay = witness_bias / witness_sigma
    witness_T_decay = math.sqrt(
        witness_h_decay * mplanck_reduced / math.sqrt(math.pi**2 * gstar_bbn / 90)
    )
    witness_alpha_inverse = 24.0 - 4 / (2 * math.pi) * math.log(1.0e16 / witness_f)
    witness_endpoint = rk4_gauge(
        [1 / witness_alpha_inverse] * 3,
        [1, 5, 9],
        [[108, 15, 21], [75, 53, 3], [105, 3, 81]],
        100,
        60000,
    )
    witness_planck_endpoint = rk4_gauge(
        [1 / witness_alpha_inverse] * 3,
        [1, 5, 9],
        [[108, 15, 21], [75, 53, 3], [105, 3, 81]],
        mplanck_reduced / 1.0e16,
        60000,
    )
    target_f = 1.5e11
    target_fa = target_f / ndw
    target_monomial = w0 * target_f**11 / cutoff**8
    target_epsilon = 2 * target_monomial
    target_sigma = 8 * math.sqrt(chi) * target_fa
    target_h_decay = target_epsilon / target_sigma
    target_h_domination = target_sigma / (3 * mplanck_reduced**2)
    hbar_GeV_s = 6.582119569e-25
    target_t_decay_s = hbar_GeV_s / (2 * target_h_decay)
    target_mass_eV = axion_mass_at_fa_1e12_eV * 1.0e12 / target_fa
    target_frequency_GHz = target_mass_eV * 241.79893e3
    return {
        "name": "derived_Z4R_x_Z11_rP2_GS_eligible_P_only_arithmetic",
        "status": "P_ONLY_EFT_QUALITY_AND_TIMING_ARITHMETIC_EXISTS__GS_INCLUSIVE_WALL_SYSTEM_OPEN",
        "charge_ledger": {
            "H_Q_Qc_X_Sc_Sbarc_Sigma": "same as minimal Z5 with all Z11 charges zero",
            "P": {"Z4R": r_p, "Z11": p_p, "PQ": 1},
            "Psi_and_Psic": {"Z4R": r_psi, "Z11": p_psi, "PQ": 0},
            "PsiBar_and_PsiBarc": {"Z4R": r_bar, "Z11": p_bar, "PQ": -1},
            "P_vector_mass_operators_allowed": (r_p + r_psi + r_bar) % 4 == 2 and (p_p + p_psi + p_bar) % 11 == 0,
            "P_VEV_preserves_R_parity": r_p % 2 == 0,
        },
        "mixed_anomalies": {
            "Z4R_raw": anomalies_r,
            "Z4R_mod2": {g: value % 2 for g, value in anomalies_r.items()},
            "Z11_raw": anomalies_11,
            "Z11_mod11": {g: value % 11 for g, value in anomalies_11.items()},
            "universal_but_nonzero": len({value % 2 for value in anomalies_r.values()}) == 1
            and len({value % 11 for value in anomalies_11.values()}) == 1
            and any(value % 2 for value in anomalies_r.values())
            and any(value % 11 for value in anomalies_11.values()),
            "Green_Schwarz_completion_required": True,
            "dynamical_shifting_GS_axion_required": True,
            "P_only_QCD_cosine_is_a_complete_discrete_gauge_potential": False,
            "interpretation": "Universality makes the selector GS-eligible, not anomaly-free. The shifting GS axion and discrete-gauge quotient must be included before the physical axion periodicity or wall-vacuum lattice can be counted.",
        },
        "harmonics": {
            "leading_superpotential_P_power": leading_w,
            "leading_holomorphic_Kahler_P_power": leading_k,
            "conditional_P_only_QCD_harmonic": ndw,
            "conditional_P_only_EFT_gcd": math.gcd(leading_w, ndw),
            "conditional_P_only_formal_residual_degeneracy_from_two_cosines": math.gcd(leading_w, ndw),
            "scope": "Integer arithmetic for a provisional P-only EFT potential cos(4*aP/fP)+cos(11*aP/fP+delta); it is not the GS-inclusive discrete-gauge vacuum count.",
            "GS_inclusive_vacuum_lattice_computed": False,
            "GS_inclusive_residual_degeneracy": None,
            "GS_inclusive_wall_collapse_demonstrated": False,
        },
        "bias_model": {
            "operator": "W=c11*P^11/Lambda^8",
            "c11": 1.0,
            "soft_monomial": "A=w0*c11*<P>^11/Lambda^8",
            "cosine_amplitude": "epsilon=2*A after adding the Hermitian conjugate",
            "w0_GeV": w0,
            "Lambda_GeV": cutoff,
            "theta_bound": 1.0e-10,
            "generic_theta_formula": "Delta theta=(11/NDW)*Vbias/chi for unit relative sine",
            "relative_phase_sine_for_interval": 1.0,
            "BBN_temperature_boundary_GeV": 1.0e-3,
            "axion_mass_normalization_eV_at_fa_1e12GeV": axion_mass_at_fa_1e12_eV,
            "scope": "Conditional P-only EFT estimate. A physical bias and wall gap require the dynamical GS axion and gauge quotient.",
        },
        "conditional_P_only_EFT_interval_GeV": {
            "minimum_before_wall_domination": minimum_f_domination,
            "minimum_decay_by_1MeV": minimum_f_bbn,
            "effective_lower_bound": lower,
            "maximum_from_theta": maximum_f_quality,
            "nonempty_P_only_arithmetic": lower < maximum_f_quality,
            "upper_over_lower": maximum_f_quality / lower,
            "physical_GS_inclusive_wall_window_claim": False,
            "scope": "Coefficient-one, unit-sine, thin-wall inequalities in the conditional P-only EFT; not a GS-inclusive cosmological interval.",
        },
        "conditional_P_only_EFT_parameter_witness": {
            "P_VEV_GeV": witness_f,
            "physical_fa_GeV_if_single_P_canonical": witness_fa,
            "axion_mass_eV": axion_mass_at_fa_1e12_eV * 1.0e12 / witness_fa,
            "bias_GeV4": witness_bias,
            "soft_monomial_before_hc_GeV4": witness_monomial,
            "bias_over_chi": witness_bias / chi,
            "Delta_theta_generic_harmonic_estimate": leading_w / ndw * witness_bias / chi,
            "wall_tension_GeV3": witness_sigma,
            "H_decay_GeV": witness_h_decay,
            "T_decay_GeV_order_estimate": witness_T_decay,
            "bias_over_minimum_for_decay_by_1MeV": witness_bias / (witness_sigma * h_bbn),
            "bias_over_sigma2_over_3MPlanck2": witness_bias / (witness_sigma**2 / (3 * mplanck_reduced**2)),
            "alphaPS_inverse_after_complete_family_threshold": witness_alpha_inverse,
            "coupled_gauge_only_alpha_inverse_at_1e18GeV": [1 / value for value in witness_endpoint],
            "coupled_gauge_only_alpha_inverse_at_reduced_Planck": [1 / value for value in witness_planck_endpoint],
            "finite_and_perturbative_to_reduced_Planck_gauge_only": all(
                math.isfinite(value) and 0 < value < 1 for value in witness_planck_endpoint
            ),
            "P_only_quality_inequality_pass": leading_w / ndw * witness_bias / chi < 1.0e-10,
            "P_only_decay_by_1MeV_order_inequality_pass": witness_T_decay > 1.0e-3,
            "P_only_decay_before_domination_order_inequality_pass": witness_bias > witness_sigma**2 / (3 * mplanck_reduced**2),
            "P_only_integer_gcd_is_one": math.gcd(leading_w, ndw) == 1,
            "GS_inclusive_wall_collapse_pass": False,
            "scope": "Numerical P-only EFT arithmetic benchmark; it does not attest a consistent anomalous-discrete wall system.",
        },
        "conditional_P_only_EFT_37GHz_benchmark": {
            "P_VEV_GeV": target_f,
            "physical_fa_GeV_if_single_P_canonical": target_fa,
            "axion_mass_micro_eV": target_mass_eV * 1.0e6,
            "photon_frequency_GHz": target_frequency_GHz,
            "soft_monomial_before_hc_GeV4": target_monomial,
            "cosine_epsilon_GeV4": target_epsilon,
            "worst_phase_Delta_theta_11_over_4_epsilon_over_chi": leading_w / ndw * target_epsilon / chi,
            "wall_gap_factor": 1.0,
            "H_decay_GeV": target_h_decay,
            "H_domination_GeV_sigma_over_3MPlanck2": target_h_domination,
            "H_decay_over_H_domination": target_h_decay / target_h_domination,
            "wall_energy_fraction_at_decay_order": target_h_domination / target_h_decay,
            "radiation_era_decay_time_s": target_t_decay_s,
            "phase_and_gap_dependence": "Delta theta scales as c11*abs(sin(delta)); Hdec scales as c11 times the adjacent-vacuum gap factor, and tdec scales inversely.",
            "full_BBN_wall_axion_relic_calculation_closed": False,
            "GS_inclusive_wall_vacuum_and_collapse_closed": False,
            "scope": "P-only frequency, quality, and thin-wall timing diagnostic. The actual GS-inclusive wall gap and decay time are not computed.",
        },
        "promotion_boundary": {
            "conditional_axion_field_theory_witness": False,
            "conditional_P_only_EFT_arithmetic_witness": True,
            "GS_axion_dynamics_included": False,
            "GS_inclusive_wall_vacuum_structure_attested": False,
            "GS_inclusive_wall_collapse_attested": False,
            "actual_domain_wall_solution": False,
            "full_domain_wall_network_attested": False,
            "radiative_generation_of_P_VEV_attested": False,
            "axino_saxion_neutralino_relic_history_attested": False,
            "complete_discrete_operator_census_and_GS_UV_completion_attested": False,
            "sensitivity": "The allowed fPQ interval is only about 2.7 percent wide for c11=1 and the stated thin-wall inputs; O(1) coefficients, phases, gap factors, and thermal history must be computed, not assumed.",
            "hard_boundary": "The anomalous Z11 needs a shifting GS axion. Therefore gcd(11,4)=1 and the numerical interval are P-only EFT arithmetic, not the vacuum count or collapse proof of the physical discrete-gauge theory.",
        },
    }


def vacuum_and_ranks() -> dict[str, Any]:
    neutral_mass = (
        (0, 1, 1),
        (1, 0, 0),
        (1, 0, 0),
    )
    colored_mass = ((0, 1), (1, 0))
    exotic_mass = ((1, 0), (0, 1))
    return {
        "superpotential_scope": "W=X(Sbarc*Sc-vPS^2)+X^3/3+Sc*Sigma*Sc+Sbarc*Sigma*Sbarc plus matter/PQ terms; nonzero O(1) coefficients absorbed in field normalizations for the rank witness",
        "witness": {
            "X_over_vPS": 0,
            "Sigma_over_vPS": 0,
            "Sc_neutral_over_vPS": 1,
            "Sbarc_neutral_over_vPS": 1,
            "all_matter_Higgs_PQ_fields_at_PS_witness": 0,
        },
        "F_terms": {
            "F_X_over_vPS2": 0,
            "F_Sc_over_vPS2": 0,
            "F_Sbarc_over_vPS2": 0,
            "F_Sigma_over_vPS2": 0,
            "why_FSigma_zero": "The antisymmetric SU4 and SU2R contraction of two identical neutral VEV directions vanishes.",
        },
        "D_terms": {
            "all_zero": True,
            "reason": "Equal conjugate Sc and Sbarc VEV magnitudes cancel every broken-generator D term.",
        },
        "global_SUSY_energy_over_vPS4": 0,
        "global_minimum_proof": "The global-SUSY potential is a sum of nonnegative F and D squares and the witness makes every square zero.",
        "neutral_chiral_mass_matrix_units_vPS": [list(row) for row in neutral_mass],
        "neutral_chiral_rank": matrix_rank(neutral_mass),
        "neutral_zero_mode_interpretation": "broken-gauge chiral direction eaten by the massive vector multiplet; this does not attest the full soft/Kahler Hessian",
        "colored_mass_matrix_units_vPS": [list(row) for row in colored_mass],
        "colored_determinant": fstr(determinant_2x2(colored_mass)),
        "colored_rank": matrix_rank(colored_mass),
        "colored_interpretation": "The uneaten Y=+/-1/3 components of Sc/Sbarc pair with the two Sigma triplets. The orthogonal colored PS-breaking components are gauge Goldstones.",
        "PQ_exotic_pair_mass_matrix_units_fPQ": [list(row) for row in exotic_mass],
        "PQ_exotic_pair_rank": matrix_rank(exotic_mass),
        "MSSM_doublet_pair": "H=(1,2,2) contains one Hu,Hd pair and no colored partner; mu~w0 is generated only after Z4R/SUSY breaking.",
        "full_F_D_soft_Kahler_hessian_closed": False,
    }


def axion_neutrino_phenomenology() -> dict[str, Any]:
    f_pq, v_ps, cutoff, w0 = 1.0e10, 1.0e16, 1.0e18, 1.0e5
    ndw = 4
    fa = f_pq / ndw
    chi = 0.0756**4
    bias = w0 * f_pq**10 / cutoff**7
    sigma_wall = 8 * math.sqrt(chi) * fa
    mplanck_reduced = 2.435e18
    h_decay = bias / sigma_wall
    h_domination = sigma_wall / mplanck_reduced**2
    gstar_bbn = 10.75
    h_bbn = math.sqrt(math.pi**2 * gstar_bbn / 90) * (1.0e-3) ** 2 / mplanck_reduced
    bias_for_bbn = sigma_wall * h_bbn
    t_decay = math.sqrt(h_decay * mplanck_reduced / math.sqrt(math.pi**2 * gstar_bbn / 90))

    axion_scan: list[dict[str, Any]] = []
    for scan_f_pq in (1.0e10, 2.0e10, 4.0e10):
        scan_fa = scan_f_pq / ndw
        scan_bias = w0 * scan_f_pq**10 / cutoff**7
        scan_sigma = 8 * math.sqrt(chi) * scan_fa
        scan_h_decay = scan_bias / scan_sigma
        scan_h_domination = scan_sigma / mplanck_reduced**2
        scan_t_decay = math.sqrt(
            scan_h_decay * mplanck_reduced / math.sqrt(math.pi**2 * gstar_bbn / 90)
        )
        scan_bias_bbn = scan_sigma * h_bbn
        source_scaled_theta = 1.0e-17 * (scan_f_pq / 1.0e10) ** 10
        direct_bias_theta = scan_bias / chi
        generic_harmonic_theta = 10 / ndw * direct_bias_theta
        timing_quality_pass = (
            source_scaled_theta < 1.0e-10
            and generic_harmonic_theta < 1.0e-10
            and scan_t_decay >= 1.0e-3
            and scan_bias > scan_sigma**2 / mplanck_reduced**2
        )
        axion_scan.append(
            {
                "P_VEV_GeV": scan_f_pq,
                "physical_fa_GeV_if_single_P_canonical": scan_fa,
                "axion_mass_eV": 5.7e-6 * 1.0e12 / scan_fa,
                "P10_soft_bias_GeV4_coefficient_one": scan_bias,
                "Delta_theta_scaled_from_source_1e_minus17_anchor": source_scaled_theta,
                "Delta_theta_direct_bias_over_chi": direct_bias_theta,
                "Delta_theta_generic_harmonic_estimate_10_over_4": generic_harmonic_theta,
                "wall_tension_GeV3": scan_sigma,
                "bias_over_sigma2_over_MPlanck2": scan_bias / (scan_sigma**2 / mplanck_reduced**2),
                "H_decay_GeV": scan_h_decay,
                "H_domination_GeV": scan_h_domination,
                "T_decay_GeV_order_estimate": scan_t_decay,
                "bias_over_minimum_for_decay_by_1MeV": scan_bias / scan_bias_bbn,
                "timing_and_quality_inequalities_pass": timing_quality_pass,
                "coprime_harmonic_landed": False,
                "complete_domain_wall_solution": False,
            }
        )

    dm21, dm31, m1 = 7.49e-5, 2.513e-3, 1.0e-3
    masses = (m1, math.sqrt(m1**2 + dm21), math.sqrt(m1**2 + dm31))
    mr, vu = v_ps**2 / cutoff, 174.0
    yukawa_singular = [math.sqrt(m * 1.0e-9 * mr) / vu for m in masses]

    return {
        "axion": {
            "KSVZ_QCD_anomaly_2N": -4,
            "NDW_source_convention": ndw,
            "E_over_N": "8/3",
            "P_VEV_GeV": f_pq,
            "physical_fa_if_single_P_canonical_GeV": fa,
            "axion_mass_eV_using_5p7_microeV_relation": round(5.7e-6 * 1.0e12 / fa, 12),
            "leading_P10_soft_bias_GeV4": bias,
            "QCD_susceptibility_GeV4_using_75p6MeV": round(chi, 15),
            "bias_over_QCD_susceptibility": bias / chi,
            "source_order_theta_shift": 1.0e-17,
            "fPQ_scan": axion_scan,
            "conditional_timing_window": {
                "P_VEV_GeV": 4.0e10,
                "timing_and_quality_inequalities_pass": axion_scan[-1]["timing_and_quality_inequalities_pass"],
                "promoted_to_domain_wall_solution": False,
                "assumptions": "unit P10 soft coefficient, generic O(1) phase, single-P canonical normalization, thin-wall scaling, radiation domination and g*=10.75; radiative generation and the relic history are not solved",
            },
            "harmonic_audit": {
                "QCD_harmonic": 4,
                "landed_nonzero_VEV_PQ_breaking_harmonics": [10],
                "gcd": math.gcd(4, 10),
                "residual_degeneracy": 2,
                "P5_source_operators": ["P^5*Qc*Sbarc/Lambda^4", "P^5*H*Q*Sc/Lambda^5"],
                "P5_fields_with_zero_VEV_at_witness": ["Qc", "Q"],
                "coprime_phase_potential_demonstrated": False,
                "interpretation": "At the landed witness the P5 operators contain zero-VEV matter fields. Their absolute F squares are phase independent and integrating out a quadratic matter field produces an even P10 harmonic; no harmonic coprime to four is demonstrated. A discrete-gauge vacuum quotient or an additional bias sector must be supplied explicitly.",
            },
            "postinflation_thin_wall_diagnostic": {
                "wall_tension_GeV3": round(sigma_wall, 6),
                "H_decay_GeV": h_decay,
                "H_domination_GeV": h_domination,
                "T_decay_GeV": t_decay,
                "minimum_bias_for_decay_by_1MeV_GeV4": bias_for_bbn,
                "minimum_over_P10_bias": bias_for_bbn / bias,
                "P10_bias_alone_closes_postinflation_domain_walls": False,
            },
            "boundary": "The fPQ=4e10 timing/quality inequalities can overlap for order-one inputs, but P10 leaves gcd(4,10)=2 and no landed P5/coprime vacuum harmonic removes the last degeneracy. NDW=4 therefore still requires a specified pre-inflation history, a demonstrated discrete-gauge quotient, or a new bias sector.",
        },
        "neutrino": {
            "mechanism": "type-I_seesaw_from_(Sbarc*Qc)^2/Lambda",
            "MR_GeV": mr,
            "normal_ordering_input": {"m1_eV": m1, "Delta_m21_sq_eV2": dm21, "Delta_m31_sq_eV2": dm31},
            "mass_eigenvalues_eV": [round(x, 12) for x in masses],
            "Dirac_Yukawa_singular_values_for_vu_174GeV": [round(x, 12) for x in yukawa_singular],
            "perturbative_scale_witness": max(yukawa_singular) < 1,
            "interpretation": "The scale supports observed neutrino masses with perturbative Yukawas; mixing and charged-flavour textures are inputs, not predictions.",
        },
        "proton_and_relic_boundaries": {
            "source_minimal_RPV_lambdaL_order": 1.0e-29,
            "source_dimension4_baryon_coefficient_order": 1.0e-55,
            "physical_Wilson_matching_and_pole_lifetime_landed": False,
            "axino_saxion_neutralino_relic_likelihood_landed": False,
        },
    }


def gates() -> list[dict[str, Any]]:
    reasons = {
        "G1": "The published discrete selector and source operators are landed, but no complete all-order operator census or explicit Green--Schwarz UV sector is present.",
        "G2": "The 2x2 colored and PQ exotic ranks pass, but normalized full component tensors and pole thresholds are not landed.",
        "G3": "A zero-energy global-SUSY F=D=0 branch passes; the complete soft/Kahler potential, competing branches, and full Hessian remain open.",
        "G4": "Z4R protects the high-scale Higgs mass and permits mu~w0, but radiative EWSB and the complete soft hierarchy are not solved.",
        "G5": "The Z11,rP=2 selector has a narrow conditional P-only quality/timing arithmetic interval and the seesaw scale is viable; the required dynamical GS axion, physical wall-vacuum lattice/collapse, radiative PQ generation, and full axion/relic spectrum remain open.",
        "G6": "Exact one/two-loop gauge-only matrices and a finite cutoff witness are landed; Yukawa/soft running and physical matching are absent.",
        "G7": "Source-level proton-suppression estimates exist, but no physical pole spectrum or Wilson-coefficient evolution is computed.",
        "G8": "A perturbative neutrino-scale witness exists, but flavour and cosmology are fitted/assumed rather than predicted in a likelihood.",
    }
    return [{"gate": gate, "closed": False, "full_gate_claim": False, "state": "OPEN", "reason": reason} for gate, reason in reasons.items()]


def build_report() -> dict[str, Any]:
    z5_fields = ps_fields()
    fields = selected_z11_fields()
    ps_rg = ps_rg_coefficients(fields)
    sm_rg = sm_stage_matrices()
    running = running_witness(ps_rg)
    z5_selector = selector_and_anomalies()
    z11 = z11_rp2_repair_variant()
    vacuum = vacuum_and_ranks()
    phen = axion_neutrino_phenomenology()
    gate_rows = gates()
    checks = {
        "PS_b_is_1_5_9": ps_rg["b"] == [1, 5, 9],
        "PS_B_matrix_exact": ps_rg["B"] == [[108, 15, 21], [75, 53, 3], [105, 3, 81]],
        "complete_family_Delta_b_is_universal_4": sm_rg["one_complete_vectorlike_PS_family"]["Delta_b"] == [4, 4, 4],
        "alpha_inverse_threshold_matches": abs(running["alphaPS_inverse_at_vPS_after_complete_family"] - 15.204772813447) < 1e-11,
        "coupled_endpoint_matches": max(abs(x - y) for x, y in zip(running["coupled_two_loop_gauge_only"]["alpha_inverse_at_cutoff"], [13.860611822824, 10.985373107419, 7.747434876886])) < 2e-9,
        "coupled_reduced_Planck_endpoint_matches": max(abs(x - y) for x, y in zip(running["coupled_two_loop_gauge_only_reduced_Planck"]["alpha_inverse_at_reduced_Planck"], [13.580318662923, 10.154174281965, 6.252345458625])) < 2e-9,
        "no_Abelian_kinetic_mixing_interval": running["abelian_kinetic_mixing"]["present"] is False,
        "published_Z5_discrete_anomalies_are_universal_but_nonzero": z5_selector["mixed_discrete_anomalies"]["Z4R_universal"] and z5_selector["mixed_discrete_anomalies"]["Z5_universal"] and not z5_selector["mixed_discrete_anomalies"]["Z4R_zero"] and not z5_selector["mixed_discrete_anomalies"]["Z5_zero"],
        "published_Z5_leading_pure_P_W_is_power10": z5_selector["leading_pure_P_superpotential_power"] == 10,
        "global_SUSY_witness_is_zero_energy": vacuum["global_SUSY_energy_over_vPS4"] == 0 and vacuum["D_terms"]["all_zero"],
        "colored_and_exotic_ranks_are_two": vacuum["colored_rank"] == 2 and vacuum["PQ_exotic_pair_rank"] == 2,
        "neutrino_Yukawas_are_perturbative": phen["neutrino"]["perturbative_scale_witness"],
        "postinflation_domain_wall_claim_is_fail_closed": phen["axion"]["postinflation_thin_wall_diagnostic"]["P10_bias_alone_closes_postinflation_domain_walls"] is False,
        "fPQ_4e10_has_conditional_timing_quality_overlap": phen["axion"]["fPQ_scan"][-1]["timing_and_quality_inequalities_pass"] is True,
        "harmonic_gcd_blocks_domain_wall_promotion": phen["axion"]["harmonic_audit"]["gcd"] == 2 and phen["axion"]["harmonic_audit"]["coprime_phase_potential_demonstrated"] is False and phen["axion"]["conditional_timing_window"]["promoted_to_domain_wall_solution"] is False,
        "Z11_rP2_selector_is_anomaly_universal_and_P_only_gcd_is_one": z11["mixed_anomalies"]["universal_but_nonzero"] is True and z11["mixed_anomalies"]["dynamical_shifting_GS_axion_required"] is True and z11["harmonics"]["leading_superpotential_P_power"] == 11 and z11["harmonics"]["conditional_P_only_EFT_gcd"] == 1,
        "Z11_P_only_interval_arithmetic_is_nonempty_but_GS_wall_open": z11["conditional_P_only_EFT_interval_GeV"]["nonempty_P_only_arithmetic"] is True and all(z11["conditional_P_only_EFT_parameter_witness"][key] for key in ("P_only_quality_inequality_pass", "P_only_decay_by_1MeV_order_inequality_pass", "P_only_decay_before_domination_order_inequality_pass", "P_only_integer_gcd_is_one")) and z11["promotion_boundary"]["conditional_axion_field_theory_witness"] is False and z11["promotion_boundary"]["conditional_P_only_EFT_arithmetic_witness"] is True and z11["promotion_boundary"]["GS_inclusive_wall_vacuum_structure_attested"] is False and z11["promotion_boundary"]["GS_inclusive_wall_collapse_attested"] is False,
        "Z11_rP2_selected_gauge_endpoints_match": max(abs(x - y) for x, y in zip(z11["conditional_P_only_EFT_parameter_witness"]["coupled_gauge_only_alpha_inverse_at_1e18GeV"], [15.760581115599, 12.877672031649, 9.686379301220])) < 2e-9 and max(abs(x - y) for x, y in zip(z11["conditional_P_only_EFT_parameter_witness"]["coupled_gauge_only_alpha_inverse_at_reduced_Planck"], [15.501027745017, 12.063693017336, 8.231081080183])) < 2e-9,
        "Z11_37GHz_row_is_explicitly_P_only_and_fail_closed": 36.6 < z11["conditional_P_only_EFT_37GHz_benchmark"]["photon_frequency_GHz"] < 36.9 and z11["conditional_P_only_EFT_37GHz_benchmark"]["full_BBN_wall_axion_relic_calculation_closed"] is False and z11["conditional_P_only_EFT_37GHz_benchmark"]["GS_inclusive_wall_vacuum_and_collapse_closed"] is False,
        "all_full_G1_G8_claims_are_false": all(not row["full_gate_claim"] for row in gate_rows),
    }
    failures = [name for name, passed in checks.items() if not passed]
    report: dict[str, Any] = {
        "namespace": "active.susy_pati_salam_z4r_z11_rp2.v24.vacuum_rg_frontier",
        "status": "V24_PS_Z11_RP2_VACUUM_RG_FRONTIER_LANDED__P_ONLY_AXION_ARITHMETIC__GS_INCLUSIVE_WALL_OPEN__FULL_G1_G8_OPEN" if not failures else "V24_PS_Z11_RP2_VACUUM_RG_FRONTIER_AUDIT_FAILED",
        "primary_source": {
            "citation": "J. Kawamura and S. Raby, arXiv:2009.04582",
            "url": SOURCE_URL,
            "html": SOURCE_HTML,
            "source_items": ["Table 1", "Eqs. (2)-(3)", "Eq. (8)", "Eqs. (12)-(15)", "Eq. (46)", "Table 3", "Eqs. (47)-(48)"],
        },
        "architecture": "minimal SUSY SU(4)C x SU(2)L x SU(2)R with selected derived Z4R x Z11 (rP=2) selector and one KSVZ vectorlike PS family",
        "variant_provenance": "The gauge/vacuum architecture is source-based; Z4R x Z11 with rP=2 is a V24-derived selector variant, not a model claimed in arXiv:2009.04582.",
        "field_content": list(fields),
        "selector": z11,
        "published_Z5_control": {
            "role": "published minimal N=5 control, not the selected V24 selector",
            "field_content": list(z5_fields),
            "selector": z5_selector,
            "axion": phen["axion"],
        },
        "derived_Z11_rP2_GS_eligible_candidate": z11,
        "vacuum_and_mass_ranks": vacuum,
        "RG_above_PS": ps_rg,
        "RG_below_PS": sm_rg,
        "running_witness": running,
        "phenomenology_frontier": {
            "selected_Z11_axion_candidate": z11,
            "neutrino": phen["neutrino"],
            "proton_and_relic_boundaries": phen["proton_and_relic_boundaries"],
        },
        "G1_G8": gate_rows,
        "closure_counts": {"closed": sum(row["closed"] for row in gate_rows), "open": sum(not row["closed"] for row in gate_rows)},
        "checks": checks,
        "failures": failures,
        "route_verdict": {
            "selected_as_V24_primary_frontier": not failures,
            "complete_theory_claim": False,
            "preferred_selector_variant": "derived Z4R x Z11 with rP=2 as a GS-eligible candidate, subject to an explicit dynamical GS sector and complete operator audit",
            "reason": "This small-representation route has a concrete F=D=0 global-SUSY branch, full colored/exotic structural rank, anomaly-universal discrete charges, viable seesaw scale, and finite gauge-only running. Its narrow gcd/quality/timing interval is only P-only EFT arithmetic: the anomalous Z11 requires a shifting GS axion, so no physical wall-vacuum or collapse claim is made. The GS, soft, threshold, wall-network, flavour, proton, and relic completions are not supplied.",
        },
    }
    core = canonical_sha(report)
    report["core_sha256"] = core
    return report


def markdown(report: Mapping[str, Any]) -> str:
    run = report["running_witness"]
    endpoint = run["coupled_two_loop_gauge_only"]["alpha_inverse_at_cutoff"]
    planck_endpoint = run["coupled_two_loop_gauge_only_reduced_Planck"]["alpha_inverse_at_reduced_Planck"]
    vac = report["vacuum_and_mass_ranks"]
    axion = report["published_Z5_control"]["axion"]
    z11 = report["derived_Z11_rP2_GS_eligible_candidate"]
    z11_interval = z11["conditional_P_only_EFT_interval_GeV"]
    z11_witness = z11["conditional_P_only_EFT_parameter_witness"]
    target_37 = z11["conditional_P_only_EFT_37GHz_benchmark"]
    neutrino = report["phenomenology_frontier"]["neutrino"]
    anomaly = report["published_Z5_control"]["selector"]["mixed_discrete_anomalies"]
    return "\n".join(
        [
            "# SUSY V24 minimal Pati--Salam Z11 vacuum/RG frontier",
            "",
            f"- Status: `{report['status']}`",
            f"- Core: `{report['core_sha256']}`",
            f"- Gauge/vacuum source and published Z5 control: [Kawamura--Raby, arXiv:2009.04582]({SOURCE_URL}); the selected Z11 selector is a V24 derivation.",
            f"- Exact PS coefficients: `b={report['RG_above_PS']['b']}`, `B={report['RG_above_PS']['B']}`.",
            f"- Published-control `fPQ=1e10 GeV`: the complete vectorlike `Delta b=(4,4,4)` threshold lowers `alpha_G^-1` from `24` to `{run['alphaPS_inverse_at_vPS_after_complete_family']:.12f}`. Gauge-only inverse-coupling endpoints are `{endpoint}` at the source cutoff `10^18 GeV` (`mu/vPS=100`) and `{planck_endpoint}` at reduced Planck `2.435e18 GeV` (`mu/vPS=243.5`).",
            f"- Selected Z11 witness `fPQ={z11_witness['P_VEV_GeV']:.3g} GeV`: `alpha_PS^-1(vPS)={z11_witness['alphaPS_inverse_after_complete_family_threshold']:.9f}`. Its coupled gauge-only inverse-coupling endpoints are `{[round(x, 9) for x in z11_witness['coupled_gauge_only_alpha_inverse_at_1e18GeV']]}` at `10^18 GeV` and `{[round(x, 9) for x in z11_witness['coupled_gauge_only_alpha_inverse_at_reduced_Planck']]}` at reduced Planck; both remain finite, while precision thresholds/Yukawas are open.",
            f"- Exact global-SUSY witness: `F=D=0`, zero energy; colored rank `{vac['colored_rank']}/2`, PQ exotic rank `{vac['PQ_exotic_pair_rank']}/2`.",
            f"- Published Z5 control anomalies: `Z4R mod 2={list(anomaly['Z4R_mod2'].values())}`, `Z5 mod 5={list(anomaly['Z5_mod5'].values())}`. The selected Z11 residues are `{list(z11['mixed_anomalies']['Z11_mod11'].values())}`; both selectors are universal but nonzero, so the GS completion is open.",
            f"- Axion: source `N_DW={axion['NDW_source_convention']}`, `E/N={axion['E_over_N']}`, leading `P^10` quality. The `fPQ=4e10 GeV` scan point conditionally passes the quality/timing inequalities, but `gcd(4,10)={axion['harmonic_audit']['gcd']}` leaves an unremoved degeneracy, so it is not promoted to a domain-wall solution.",
            f"- Conditional P-only EFT arithmetic: `Z4R x Z11`, `rP=2`, leading `P^11`, and the formal integer `gcd(11,4)=1`. For unit coefficient and generic phase the P-only inequalities give `{z11_interval['effective_lower_bound']:.6g} < fPQ < {z11_interval['maximum_from_theta']:.6g} GeV`; the `{z11_witness['P_VEV_GeV']:.3g} GeV` row gives `Delta theta={z11_witness['Delta_theta_generic_harmonic_estimate']:.3g}` and `Tdec~{z11_witness['T_decay_GeV_order_estimate']:.3g} GeV`. This is not a physical wall-window claim.",
            "- GS wall boundary: the Z11 mixed anomalies are universal but nonzero. A shifting GS axion is required, and the P-only QCD cosine is not by itself the complete discrete-gauge potential. The GS-inclusive vacuum lattice, residual degeneracy, physical bias, and wall collapse are all uncomputed/open.",
            f"- Conditional P-only 37-GHz diagnostic: `fPQ={target_37['P_VEV_GeV']:.3g} GeV`, `fa={target_37['physical_fa_GeV_if_single_P_canonical']:.3g} GeV`, `ma~{target_37['axion_mass_micro_eV']:.3g} micro-eV`, `nu~{target_37['photon_frequency_GHz']:.3g} GHz`, worst-phase `Delta theta~{target_37['worst_phase_Delta_theta_11_over_4_epsilon_over_chi']:.3g}`, and P-only radiation-era `tdec~{target_37['radiation_era_decay_time_s']:.3g} s`. This row is phase/gap-factor dependent, overlaps BBN, and is neither a GS-inclusive wall result nor a closed relic calculation.",
            f"- Seesaw: `M_R={neutrino['MR_GeV']:.3g} GeV`; the normal-ordering mass witness needs perturbative Dirac singular values `{neutrino['Dirac_Yukawa_singular_values_for_vu_174GeV']}`.",
            "",
            "This is the selected V24 research frontier, not a complete G1--G8 theory. The Z11 candidate supplies only conditional P-only EFT arithmetic; it does not supply a consistent discrete-gauge wall witness without the dynamical Green--Schwarz axion and quotient. The complete discrete operator/GS sector, radiative PQ and soft/Kahler stabilization, physical stage thresholds, wall-network and relic evolution, full flavour fit, and proton Wilson matching are not landed. All eight full gates remain open.",
            "",
        ]
    )


def write_outputs(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    MD_PATH.write_text(markdown(report), encoding="utf-8", newline="\n")


def check_outputs(report: Mapping[str, Any]) -> bool:
    expected_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
    expected_md = markdown(report)
    return JSON_PATH.exists() and MD_PATH.exists() and JSON_PATH.read_text(encoding="utf-8") == expected_json and MD_PATH.read_text(encoding="utf-8") == expected_md


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        write_outputs(report)
    if args.check and not check_outputs(report):
        print("V24 PS vacuum/RG frontier artifacts are missing or stale")
        return 1
    print(report["status"])
    print(report["core_sha256"])
    return 0 if not report["failures"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
