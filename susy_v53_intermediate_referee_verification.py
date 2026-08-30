#!/usr/bin/env python3
"""Independent exact checks for the two V53 intermediate audits."""

from __future__ import annotations

import json
import math

import numpy as np
import sympy as sp

import susy_v53_natural_dt_filter_audit as dt
import susy_v53_proton_safe_selector_no_go_audit as proton
import susy_v52_low_index_source_audit as v52


def exact_gaussian_rank(matrix: np.ndarray) -> int:
    exact = sp.Matrix(
        [[sp.Integer(round(z.real)) + sp.I * sp.Integer(round(z.imag)) for z in row] for row in matrix]
    )
    return int(exact.rank())


def modular_rank(matrix: np.ndarray, prime: int, image_i: int) -> int:
    rows = [
        [(int(round(z.real)) + image_i * int(round(z.imag))) % prime for z in row]
        for row in matrix
    ]
    rank = 0
    columns = len(rows[0])
    for column in range(columns):
        pivot = next((r for r in range(rank, len(rows)) if rows[r][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inverse = pow(rows[rank][column], prime - 2, prime)
        rows[rank] = [(x * inverse) % prime for x in rows[rank]]
        for r in range(len(rows)):
            if r != rank and rows[r][column]:
                factor = rows[r][column]
                rows[r] = [(x - factor * y) % prime for x, y in zip(rows[r], rows[rank])]
        rank += 1
        if rank == len(rows):
            break
    return rank


def main() -> int:
    h_full = dt.hessian_numerator(cross_coupled=True)
    h_control = dt.hessian_numerator(cross_coupled=False)
    q = dt.orbit_numerator()
    prime_images = ((37, 6), (41, 9), (73, 27))
    modular = {
        str(p): {
            "i_squared_is_minus_one": (ii * ii + 1) % p == 0,
            "full_hessian_rank": modular_rank(h_full, p, ii),
            "control_hessian_rank": modular_rank(h_control, p, ii),
            "orbit_rank": modular_rank(q, p, ii),
        }
        for p, ii in prime_images
    }
    dt_block = dt.dt_cartesian_hessian()
    f_control = dt.f_term_numerators()  # Cross witness; control flatness is checked by its exact Hessian Ward identity.

    # Independent congruence check of the short non-R proof through a wider range.
    non_r_counterexamples = []
    r_e_solutions = {}
    for n in range(2, 257):
        for qf in range(n):
            for qh in range(n):
                if (2 * qh) % n == 0 and (2 * qf + qh) % n == 0 and (4 * qf) % n != 0:
                    non_r_counterexamples.append((n, qf, qh))
        r_e_solutions[n] = [qe for qe in range(n) if (2 * qe - 2) % n == 0 and (3 * qe - 2) % n == 0]

    source_t = 24
    sum_t = source_t + 8 + 2 + 6
    b_landau = sum_t - 3 * 8
    pole_ratio = math.exp(8 * math.pi**2 / (b_landau * 0.73**2))
    family_f4_multiplicity = 3**2 * (3**2 - 1) // 12  # dim S_(2,2)(C^3)

    result = {
        "full_exact_rank": exact_gaussian_rank(h_full),
        "control_exact_rank": exact_gaussian_rank(h_control),
        "orbit_exact_rank": exact_gaussian_rank(q),
        "full_ward_zero": bool(np.count_nonzero(h_full @ q) == 0),
        "control_ward_zero": bool(np.count_nonzero(h_control @ q) == 0),
        "modular_cross_checks": modular,
        "dt_rank": exact_gaussian_rank(dt_block),
        "dt_nullity": 20 - exact_gaussian_rank(dt_block),
        "combined_source_plus_dt_rank": exact_gaussian_rank(h_full) + exact_gaussian_rank(dt_block),
        "combined_source_plus_dt_nullity": 196 - exact_gaussian_rank(h_full) - exact_gaussian_rank(dt_block),
        "non_r_counterexamples_through_256": non_r_counterexamples,
        "r_E2_E3_possible_moduli_through_256": [n for n, values in r_e_solutions.items() if values],
        "F4_family_multiplicity_independent": family_f4_multiplicity,
        "sum_Dynkin_T": sum_t,
        "b_Landau_sumT_minus_3C2": b_landau,
        "b_AF_3C2_minus_sumT": -b_landau,
        "one_loop_pole_ratio_at_g_0p73": pole_ratio,
        "audit_reports_validate": True,
        "unused_cross_F_shapes": {key: list(value.shape) for key, value in f_control.items()},
    }
    proton.validate(proton.build_report())
    dt.validate_report(dt.build_report())
    assert result["full_exact_rank"] == 143
    assert result["control_exact_rank"] == 137
    assert result["orbit_exact_rank"] == 33
    assert result["full_ward_zero"] and result["control_ward_zero"]
    assert result["dt_rank"] == 16 and result["dt_nullity"] == 4
    assert not non_r_counterexamples
    assert result["r_E2_E3_possible_moduli_through_256"] == [2]
    assert family_f4_multiplicity == 6
    assert all(row == {"i_squared_is_minus_one": True, "full_hessian_rank": 143,
                       "control_hessian_rank": 137, "orbit_rank": 33}
               for row in modular.values())
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
