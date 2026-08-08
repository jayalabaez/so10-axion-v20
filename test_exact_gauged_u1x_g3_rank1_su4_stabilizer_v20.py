import ast
import copy
import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np

import exact_gauged_u1x_g3_rank1_su4_stabilizer_v20 as subject


def test_shifted_su4_generator_definitions_are_exact_and_ordered():
    definitions = subject.su4_generator_definitions()
    assert subject.COMPLEX_PLANES == ((2, 3), (4, 5), (6, 7), (8, 9))
    assert tuple(row["label"] for row in definitions) == (
        "H1",
        "H2",
        "H3",
        "X12",
        "Y12",
        "X13",
        "Y13",
        "X14",
        "Y14",
        "X23",
        "Y23",
        "X24",
        "Y24",
        "X34",
        "Y34",
    )
    assert definitions[0]["so10_coefficients"] == {(2, 3): 1, (4, 5): -1}
    assert definitions[1]["so10_coefficients"] == {(4, 5): 1, (6, 7): -1}
    assert definitions[2]["so10_coefficients"] == {(6, 7): 1, (8, 9): -1}
    assert definitions[3]["so10_coefficients"] == {(2, 4): 1, (3, 5): 1}
    assert definitions[4]["so10_coefficients"] == {(2, 5): 1, (3, 4): -1}
    assert definitions[-2]["so10_coefficients"] == {(6, 8): 1, (7, 9): 1}
    assert definitions[-1]["so10_coefficients"] == {(6, 9): 1, (7, 8): -1}
    assert all(
        first >= 2
        for row in definitions
        for first, _ in row["so10_coefficients"]
    )
    certificate = subject.exact_generator_definition_certificate()
    assert certificate["coefficient_matrix_shape"] == (45, 15)
    assert certificate["coefficient_rank_mod_prime"] == 15
    assert certificate["proof_grade"]


def test_joint_endpoint_tangent_kernel_is_exactly_the_displayed_su4():
    certificate = subject.exact_stabilizer_tangent_certificate()
    endpoint = certificate["fixed_endpoint"]
    assert endpoint["H"] == "h_-=(e0-i e1)/sqrt(2)"
    assert endpoint["Sigma"] == "q/4"
    assert endpoint["H_numerator_norm_squared"] == 2
    assert endpoint["q_coordinate_norm_squared"] == 16
    assert endpoint["endpoint_binding_exact"]
    assert certificate["joint_tangent_shape"] == (272, 45)
    assert certificate["joint_tangent_rank_mod_prime"] == 30
    assert certificate["rank_lower_bound_over_Q_R"] == 30
    assert certificate["displayed_kernel_shape"] == (45, 15)
    assert certificate["displayed_kernel_rank_mod_prime"] == 15
    assert certificate["displayed_kernel_residual_max_abs"] == 0
    assert certificate["kernel_upper_bound_on_tangent_rank"] == 30
    assert certificate["exact_tangent_rank_over_Q_R"] == 30
    assert certificate["exact_tangent_nullity"] == 15
    assert certificate["explicit_kernel_is_complete"]
    assert certificate["source_actions"][
        "ordered_generator_labels_match_exactly"
    ]
    negative = certificate["wrong_offset_zero_SU4_negative_control"]
    assert negative["complex_planes"] == ((0, 1), (2, 3), (4, 5), (6, 7))
    assert negative["H_tangent_residual_max_abs"] > 0
    assert negative["joint_tangent_residual_max_abs"] > 0
    assert negative["does_not_stabilize_fixed_h_minus"]
    assert negative["wrong_embedding_rejected_exactly"]
    assert certificate["proof_grade"]


def test_integral_lie_structure_closes_and_obeys_jacobi_exactly():
    certificate = subject.exact_lie_algebra_certificate()
    assert certificate["Lie_algebra_dimension"] == 15
    assert certificate["coordinate_block_unimodular"]
    assert certificate["structure_constants_integral"]
    assert certificate["maximum_abs_structure_constant"] == 2
    assert certificate["nonzero_unordered_bracket_count"] == 84
    assert certificate["nonzero_structure_constant_count"] == 88
    assert certificate["coefficient_commutator_reconstruction_max_abs"] == 0
    assert certificate["vector_commutator_reconstruction_max_abs"] == 0
    assert certificate["Cartan_commutator_max_abs"] == 0
    assert certificate["antisymmetry_max_abs_residual"] == 0
    assert certificate["Jacobi_max_abs_residual"] == 0
    assert certificate["proof_grade"]


def test_phi210_actions_are_exact_integral_skew_and_represent_the_lie_algebra():
    actions = subject.exact_phi210_actions()
    assert len(actions) == 15
    assert all(matrix.shape == (210, 210) for matrix in actions)
    assert all(np.issubdtype(matrix.dtype, np.integer) for matrix in actions)
    assert all((matrix + matrix.T).nnz == 0 for matrix in actions)
    certificate = subject.exact_phi210_action_certificate()
    assert certificate["total_nonzero_entries"] == 3360
    assert certificate["maximum_abs_action_entry"] == 1
    assert certificate["skew_transpose_max_abs_residual"] == 0
    assert certificate["flattened_action_rank_mod_prime"] == 15
    assert certificate["Lie_commutator_reconstruction_max_abs"] == 0
    assert certificate["proof_grade"]


def test_report_closes_only_stabilizer_infrastructure():
    report = subject.build_report()
    assert report["status"] == subject.STATUS
    assert report["overall_state"] == subject.OVERALL_STATE
    assert report["model_contract_id"] == "gauged_u1x_phi17_v20"
    assert report["n_failed"] == 0
    assert all(report["checks"].values())
    assert report["scope"]["infrastructure_only"] is True
    assert report["scope"]["H_fixed_to_h_minus"] is True
    assert report["scope"][
        "Sigma_fixed_to_normalized_explicit_decomposable_pure_spinor_q_over_4"
    ] is True
    assert report["scope"]["common_continuous_stabilizer_identified_as_SU4"]
    assert report["scope"]["exact_Phi210_SU4_action_available_for_next_stage"]
    assert report["scope"]["arbitrary_Phi_Schur_SOS_SDP_constructed"] is False
    assert report["scope"]["arbitrary_Phi_Schur_SOS_SDP_feasible"] is False
    assert report["scope"]["arbitrary_rank1_Phi_bound_proved"] is False
    assert report["scope"]["arbitrary_max_negative_Sigma_proved"] is False
    assert report["scope"]["G3_closed"] is False
    assert report["scope"]["whole_model_excluded"] is False


def test_critical_certificate_mutations_fail_closed():
    base = {
        "generators": subject.exact_generator_definition_certificate(),
        "tangent": subject.exact_stabilizer_tangent_certificate(),
        "lie": subject.exact_lie_algebra_certificate(),
        "phi210": subject.exact_phi210_action_certificate(),
    }
    mutations = (
        ("generators", "coefficient_rank_mod_prime", 14),
        ("tangent", "joint_tangent_rank_mod_prime", 29),
        ("tangent", "displayed_kernel_residual_max_abs", 1),
        ("lie", "Jacobi_max_abs_residual", 1),
        ("phi210", "skew_transpose_max_abs_residual", 1),
    )
    for section, field, forged_value in mutations:
        forged = copy.deepcopy(base)
        forged[section][field] = forged_value
        report = subject._build_report_from_certificates(**forged)
        assert report["overall_state"] == "EXECUTION_FAIL"
        assert report["n_failed"] >= 1
        assert report["scope"]["G3_closed"] is False
        assert report["scope"]["whole_model_excluded"] is False


def test_source_builds_without_quarantined_sigma35_dependency():
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
    blocked = "exact_gauged_u1x_g3_su5_max_negative_sigma35_orbits_v20"
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
import exact_gauged_u1x_g3_rank1_su4_stabilizer_v20 as audit
report = audit.build_report()
assert report["n_failed"] == 0
assert report["scope"]["G3_closed"] is False
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


def test_generated_artifacts_match_the_live_report():
    report = subject.build_report()
    stored = json.loads(subject.OUT_JSON.read_text(encoding="utf-8"))
    assert stored == subject._jsonable(report)
    markdown = subject.OUT_MD.read_text(encoding="utf-8")
    assert markdown == subject.render_markdown(report)
    assert "arbitrary-Phi Schur/SOS SDP: **OPEN**" in markdown
    assert "G3: **OPEN**" in markdown
