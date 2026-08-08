import ast
from fractions import Fraction
import os
from pathlib import Path
import subprocess
import sys

import numpy as np

import exact_gauged_u1x_g3_su5_max_negative_rank1_su3_slice_v20 as subject


def test_rank1_residual_source_is_exact_and_normalized():
    source = subject.exact_rank1_residual_source()
    assert source["source_binding_exact"]
    assert source["sigma_integer_norm_squared"] == 16
    assert source["mixed_shape"] == (272, 210)
    assert source["chiral_shape"] == (504, 210)
    assert source["target_norm_squared"] == 1024
    assert source["mixed_particular_residual"] == 0
    assert source["chiral_particular_residual"] == 0
    endpoint = source["endpoint_binding"]
    assert endpoint["proof_grade"]
    assert endpoint["decomposable_five_form_by_construction"]
    assert endpoint["coordinate_reconstruction_residual"] == 0.0
    assert endpoint["anti_self_dual_hodge_residual"] == 0.0
    assert endpoint["raw_kinetic_norm_squared"] == 16
    assert endpoint["canonical_normalization"] == "Sigma=q/4"
    assert endpoint["normalized_kinetic_norm_squared"] == 1
    assert endpoint["K_plus_identity_action_max_abs_residual"] == 0
    assert endpoint["raw_H_norm_squared"] == 2
    assert endpoint["raw_current"] == -32
    assert endpoint["current_rationalization_residual"] == 0.0
    assert endpoint["normalized_I45"] == -1
    assert endpoint["normalized_self_projector_quartics"] == {
        "54": Fraction(0),
        "1050bar": Fraction(0),
        "4125": Fraction(0),
        "2772bar": Fraction(1),
    }
    assert endpoint["self_projector_completeness_exact"]


def test_source_imports_and_builds_with_sigma35_dependency_blocked():
    source_path = Path(subject.__file__).resolve()
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    imported_modules = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported_modules.update(
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    )
    blocked = (
        "exact_gauged_u1x_g3_su5_max_negative_sigma35_orbits_v20"
    )
    assert blocked not in imported_modules

    code = f"""
import importlib.abc
import sys

class BlockSigma35(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == {blocked!r}:
            raise ModuleNotFoundError(fullname)
        return None

sys.meta_path.insert(0, BlockSigma35())
import exact_gauged_u1x_g3_su5_max_negative_rank1_su3_slice_v20 as audit
report = audit.build_report()
assert report["n_failed"] == 0
assert report["checks"]["explicit_endpoint_current_and_self_projectors_exactly"]
"""
    environment = os.environ.copy()
    environment.update(
        {
            "OPENBLAS_NUM_THREADS": "1",
            "OMP_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "NUMEXPR_NUM_THREADS": "1",
        }
    )
    completed = subprocess.run(
        [sys.executable, "-c", code],
        cwd=subject.ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_live_pair_casimir_reconstructs_expected_anchor_polynomial():
    assert (
        subject.exact_anchor_polynomial()
        == subject.EXPECTED_ANCHOR_POLYNOMIAL
    )
    angular = subject.exact_angular_gram()
    assert angular["symmetric_exact"]
    preflight = angular["int64_overflow_preflight"]
    assert preflight["proof_grade"]
    assert preflight["observed_response_absolute_maximum"] <= preflight[
        "response_accumulation_absolute_bound"
    ]
    assert preflight["observed_Gram_absolute_maximum"] <= preflight[
        "Gram_absolute_bound"
    ]
    assert preflight["Gram_absolute_bound"] <= preflight["int64_limit"]


def test_common_affine_kernel_is_exactly_50_dimensional_and_integral():
    certificate = subject.exact_affine_kernel_certificate()
    assert certificate["combined_matrix_shape"] == (776, 210)
    assert certificate["exact_rank"] == 160
    assert certificate["exact_nullity"] == 50
    assert certificate["integral_kernel_basis_shape"] == (210, 50)
    assert certificate["maximum_basis_denominator"] == 1
    assert certificate["basis_residual_max_abs"] == 0
    assert certificate["kernel_column_plane_count_census"] == {
        "no_0_or_1_index": 35,
        "exactly_one_of_0_or_1": 0,
        "both_0_and_1": 15,
    }
    assert certificate["particular_solution_norm_squared"] == 4
    assert certificate["particular_solution_dot_kernel_max_abs"] == 0
    assert certificate["minimum_physical_N_Phi"] == Fraction(2, 5)
    assert certificate["proof_grade"]


def test_rational_gram_identity_and_exact_positive_ldl():
    certificate = subject.exact_sos_certificate()
    assert certificate["Gram_shape"] == (15, 15)
    assert certificate["Gram_symmetric_exact"]
    assert certificate["Gram_polynomial_identity_exact"]
    assert certificate["LDL_pivot_count"] == 15
    assert certificate["LDL_all_pivots_strictly_positive"]
    assert certificate["strict_anchor_lower_bound"] == Fraction(3, 200)
    assert certificate["proof_grade"]


def test_radial_threshold_is_exactly_sufficient():
    certificate = subject.exact_radial_patch_certificate()
    assert certificate["live_source_binding"][
        "HSX_PD_coefficients_proof_grade"
    ]
    assert certificate["live_source_binding"]["rank1_endpoint_proof_grade"]
    assert certificate["small_v_polynomial_identity_exact"]
    assert certificate["small_v_coefficient_domination"]["proof_grade"]
    assert certificate["large_v_coefficient_domination"]["proof_grade"]
    assert certificate["small_v_linear_coefficient"] == 0
    assert certificate["small_v_quadratic_coefficient"] == Fraction(199, 1600)
    assert certificate["large_v_margin_above_1_over_5000"] > 0
    assert certificate["low_u_margin_above_1_over_5000"] > 0
    assert certificate["restricted_global_minimum"] == Fraction(1, 5000)
    witness = certificate["attaining_slice_point"]
    assert witness["proof_grade"]
    assert witness["N_Phi"] == 1
    assert witness["P"] == 0
    assert witness["Q_chi"] == 0
    assert witness["R_rank1"] == Fraction(8, 5)
    assert witness["full_gap"] == Fraction(1, 5000)
    assert certificate["proof_grade"]


def test_report_is_fail_closed_about_scope():
    report = subject.build_report()
    assert report["status"] == subject.STATUS
    assert report["overall_state"] == subject.OVERALL_STATE
    assert report["model_contract_id"] == "gauged_u1x_phi17_v20"
    assert report["n_failed"] == 0
    assert report["scope"]["H_fixed_to_h_minus"] is True
    assert report["scope"][
        "Sigma_fixed_to_normalized_explicit_decomposable_pure_spinor"
    ]
    assert report["scope"]["Phi_restricted_to_four_real_SU3_fixed_variables"]
    assert report["scope"]["Phi_slice_real_dimension"] == 4
    assert report["scope"]["full_SU3_fixed_space_real_dimension"] == 16
    assert report["scope"]["full_SU3_fixed_space_proved"] is False
    assert report["scope"]["u_v_arbitrary_nonnegative"]
    assert report["scope"]["arbitrary_real_Phi"] is False
    assert report["scope"]["arbitrary_max_negative_Sigma"] is False
    assert report["scope"]["G3_closed"] is False
    assert report["scope"]["whole_model_excluded"] is False
    assert report["checks"]["arbitrary_rank1_Phi_proved"] is False
    assert report["checks"]["arbitrary_Sigma35_proved"] is False
    assert report["checks"]["G3_closed"] is False
    assert report["checks"][
        "explicit_endpoint_current_and_self_projectors_exactly"
    ]
