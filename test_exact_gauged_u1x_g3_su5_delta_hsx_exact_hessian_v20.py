#!/usr/bin/env python3
from __future__ import annotations

import exact_gauged_u1x_g3_su5_delta_hsx_exact_hessian_v20 as certificate
import final_g3_acceptance_gate_v20 as final_gate


def test_fixed_raw_lattice_is_derived_from_exact_sources():
    source = certificate.exact_source_lattice_derivation_certificate()
    numerator, lattice = certificate.exact_raw_numerator()
    assert source["prime_factorization"] == {"2": 7, "3": 2, "5": 5, "7": 1}
    assert source["factor_product"] == certificate.RAW_HESSIAN_DENOMINATOR
    assert source["source_binding_exact"]
    assert lattice["denominator"] == 25_200_000
    assert lattice["float_compiler_crosscheck_maximum_scaled_residual"] < 1e-5
    assert lattice["float_compiler_crosscheck_half_lattice_margin"] > 0.49
    assert lattice["numerator_symmetric"]
    assert numerator.shape == (486, 486)


def test_exact_integer_kernel_and_block_ldl_close_local_hessian():
    row = certificate.exact_inertia_certificate()
    assert row["symmetry_tangents"]["exact_rank"] == 38
    assert row["integer_Hessian_times_symmetry_tangent_max_abs"] == 0
    assert row["support_component_count"] == 39
    assert max(row["support_component_sizes"]) == 24
    assert row["exact_negative_witnesses"] == 0
    assert row["exact_positive_pivots"] == 448
    assert row["exact_zero_pivots"] == 38
    assert row["exact_PSD"]
    assert row["exact_rank_448"]
    assert row["exact_nullity_38"]
    assert row["kernel_equals_38_symmetry_tangents"]
    assert row["strict_quotient_positive"]
    assert row["source_binding_exact"]
    assert row["proof_grade"]


def test_report_exposes_final_gate_aliases_without_closing_global_g3():
    report = certificate.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert report["status"] == "EXACT_FULL_HESSIAN_RANK_448_NULLITY_38_CERTIFIED"
    assert report["overall_state"] == "CLOSED_FULL_LOCAL_HESSIAN_SUBPROBLEM"
    for name in (
        "exact_rank_448",
        "exact_nullity_38",
        "exact_PSD",
        "strict_quotient_positive",
        "kernel_equals_38_symmetry_tangents",
        "proof_grade",
        "source_binding_exact",
    ):
        assert report["flags"][name], name
    assert report["G3_closed"] is False


def test_final_g3_gate_accepts_real_exact_hessian_but_remains_open_globally():
    exact = certificate.build_report()
    report = final_gate.build_report(exact_hessian_report=exact)
    assert report["n_failed"] == 0, report["failures"]
    assert report["science_criteria"][
        "full_Hessian_rank_448_nullity_38_exact"
    ] is True
    assert report["science_criteria"][
        "full_448_quotient_strictly_positive_exact"
    ] is True
    assert report["science_criteria"][
        "beta_global_gap_and_unique_equality_exact"
    ] is False
    assert report["classification"]["mathematical_G3_closed"] is False
    assert report["classification"]["G3_closed"] is False
    assert report["overall_state"] == "OPEN"
