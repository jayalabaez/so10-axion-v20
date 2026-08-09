import ast
import copy
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pytest
from scipy import sparse

import exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20 as subject


def test_source_hash_is_lf_crlf_and_cr_invariant(tmp_path):
    expected = hashlib.sha256(b"alpha\nbeta\n").hexdigest()
    paths = []
    for index, payload in enumerate(
        (b"alpha\nbeta\n", b"alpha\r\nbeta\r\n", b"alpha\rbeta\r")
    ):
        path = tmp_path / f"source-{index}.py"
        path.write_bytes(payload)
        paths.append(path)
    assert {subject._file_sha256(path) for path in paths} == {expected}


def _assemble(**overrides):
    evidence = {
        "companion_model_contract_id": subject.stabilizer.MODEL_CONTRACT_ID,
        "stabilizer_report": subject.stabilizer.build_report(),
        "intertwiner_report": subject.intertwiners.build_report(),
        "carrier_certificate": subject.intertwiners.exact_carrier_certificate(),
        "constraint_certificate": subject._constraint_certificate(),
        "matrices": subject._basis_data()[0],
    }
    evidence.update(overrides)
    return subject._build_report_from_evidence(**evidence)


def test_exact_weight_zero_system_has_rank_506_and_explicit_nullity_45():
    pairs = subject.cartan_weight_zero_pairs()
    constraints = subject._cartan_reduced_constraint_matrix()
    nullspace = subject.exact_exterior_nullspace()
    certificate = subject._constraint_certificate()

    assert len(pairs) == 551
    assert constraints.shape == (5952, 551)
    assert constraints.nnz == 13296
    assert subject._rank_mod_prime(constraints.toarray()) == 506
    assert nullspace.shape == (551, 45)
    assert subject._rank_mod_prime(nullspace.T) == 45
    assert set(np.unique(nullspace)).issubset({-1, 0, 1})
    assert not np.any(constraints @ nullspace)
    assert certificate["exact_rational_rank"] == 506
    assert certificate["exact_rational_nullity"] == 45
    assert certificate[
        "all_45_nullvectors_invariant_under_all_15_exterior_actions_exact"
    ]
    assert certificate["proof_grade"]
    assert subject._constraint_certificate_is_exact(certificate)


def test_45_canonical_real_symmetric_matrices_are_live_invariant_and_independent():
    matrices = subject.exact_invariant_quadratic_basis()
    actions = subject.stabilizer.exact_phi210_actions()
    certificate = subject._basis_certificate(matrices)

    assert len(matrices) == 45
    assert len(actions) == 15
    assert all(matrix.shape == (210, 210) for matrix in matrices)
    assert all(matrix.dtype == np.int64 for matrix in matrices)
    assert all((matrix != matrix.T).nnz == 0 for matrix in matrices)
    assert all(
        math.gcd(*(abs(int(entry)) for entry in matrix.data)) == 1
        for matrix in matrices
    )
    assert all(int(matrix.data[0]) > 0 for matrix in matrices)
    assert all(
        subject._sparse_is_zero(matrix @ action - action @ matrix)
        for matrix in matrices
        for action in actions
    )
    assert certificate["matrix_count"] == 45
    assert certificate["upper_triangle_column_rank_mod_prime"] == 45
    assert certificate["Gram_rank_mod_prime"] == 45
    assert certificate[
        "all_45_commute_with_all_15_live_Phi210_generators_exact"
    ]
    assert certificate["proof_grade"]


def test_polynomial_and_rational_reconstruction_apis_are_exact():
    matrices = subject.exact_invariant_quadratic_basis()
    primitive_rows, scale_factors = (
        subject.primitive_quadratic_polynomial_basis()
    )
    assert primitive_rows.shape == (45, 22155)
    assert subject._rank_mod_prime(primitive_rows) == 45
    assert len(scale_factors) == 45

    for index in (0, 7, 20, 40, 44):
        encoded = subject.quadratic_matrix_to_polynomial_coefficients(
            matrices[index]
        )
        numerator, denominator = (
            subject.quadratic_polynomial_coefficients_to_matrix(encoded)
        )
        assert denominator == 1
        assert subject._sparse_is_zero(numerator - matrices[index])
        assert np.array_equal(
            encoded, scale_factors[index] * primitive_rows[index]
        )

    coefficients = [Fraction(0) for _ in range(45)]
    coefficients[0] = Fraction(1, 2)
    coefficients[1] = Fraction(-3, 5)
    numerator, denominator = subject.reconstruct_quadratic_form(coefficients)
    expected_times_ten = 5 * matrices[0] - 6 * matrices[1]
    assert denominator > 0
    assert subject._sparse_is_zero(
        10 * numerator - denominator * expected_times_ten
    )

    gram = subject.quadratic_basis_gram_matrix()
    assert gram.shape == (45, 45)
    assert np.array_equal(gram, gram.T)
    assert subject._rank_mod_prime(gram) == 45


def test_public_exact_arithmetic_rejects_overflow_and_evaluates_large_phi_exactly():
    phi = [np.int64(0) for _ in range(210)]
    phi[1] = np.int64(10_000_000_000)
    values = subject.evaluate_invariant_quadratics(phi)
    assert values[2] == 10**20
    assert values[7] == -(10**20)
    assert max(abs(value) for value in values) > np.iinfo(np.int64).max
    assert all(isinstance(value, int) for value in values)

    limit = int(np.iinfo(np.int64).max)
    unsafe = sparse.csr_matrix(
        ([limit, limit], ([0, 1], [1, 0])),
        shape=(210, 210),
        dtype=np.int64,
    )
    with pytest.raises(OverflowError, match="encoding exceeds exact int64"):
        subject.quadratic_matrix_to_polynomial_coefficients(unsafe)

    safe_entry = limit // 2
    safe = sparse.csr_matrix(
        ([safe_entry, safe_entry], ([0, 1], [1, 0])),
        shape=(210, 210),
        dtype=np.int64,
    )
    encoded = subject.quadratic_matrix_to_polynomial_coefficients(safe)
    assert int(encoded[1]) == 2 * safe_entry
    roundtrip, denominator = (
        subject.quadratic_polynomial_coefficients_to_matrix(encoded)
    )
    assert denominator == 1
    assert subject._sparse_is_zero(roundtrip - safe)

    with pytest.raises(TypeError, match="exact integers"):
        subject.evaluate_invariant_quadratics([False] + [0] * 209)


def test_completeness_is_bound_to_the_live_branching_and_endpoint_provenance():
    report = subject.build_report()
    census = report["real_form_completeness"]
    provenance = report["source_provenance"]
    live_maximum = max(
        abs(int(entry))
        for matrix in subject.exact_invariant_quadratic_basis()
        for entry in matrix.data
    )

    assert report["status"] == subject.STATUS
    assert report["overall_state"] == subject.OVERALL_STATE
    assert report["n_failed"] == 0
    assert all(report["checks"].values())
    assert census["branching_exact"]
    assert census["self_conjugate_symmetric_pairing_dimension"] == 24
    assert census["complex_Hermitian_real_dimension"] == 21
    assert census[
        "total_real_symmetric_invariant_dimension_upper_bound"
    ] == 45
    assert census["proof_grade"]
    assert provenance["stabilizer_report_equals_live_report_exact"]
    assert provenance["intertwiner_report_equals_live_report_exact"]
    assert provenance[
        "carrier_certificate_equals_embedded_and_live_exact"
    ]
    assert provenance["all_required_live_provenance_exact"]
    assert report["reconstruction_api"]["exact_arithmetic_contract"][
        "live_basis_maximum_absolute_entry"
    ] == live_maximum


def test_report_assembler_rejects_critical_provenance_and_certificate_mutations():
    stabilizer_report = subject.stabilizer.build_report()
    intertwiner_report = subject.intertwiners.build_report()
    carriers = subject.intertwiners.exact_carrier_certificate()
    constraints = subject._constraint_certificate()

    bad_inputs = [
        {"companion_model_contract_id": "wrong_contract"},
    ]
    for field, value in (
        ("model_contract_id", "wrong_contract"),
        ("status", "EXECUTION_FAILED"),
    ):
        bad = copy.deepcopy(stabilizer_report)
        bad[field] = value
        bad_inputs.append({"stabilizer_report": bad})
    bad = copy.deepcopy(stabilizer_report)
    bad["scope"][
        "exact_Phi210_SU4_action_available_for_next_stage"
    ] = False
    bad_inputs.append({"stabilizer_report": bad})

    for field, value in (
        ("model_contract_id", "wrong_contract"),
        ("status", "EXECUTION_FAILED"),
    ):
        bad = copy.deepcopy(intertwiner_report)
        bad[field] = value
        bad_inputs.append({"intertwiner_report": bad})

    for field, value in (
        ("carrier_count", 24),
        ("concatenated_carrier_rank_mod_prime", 209),
    ):
        bad = copy.deepcopy(carriers)
        bad[field] = value
        bad_inputs.append({"carrier_certificate": bad})

    bad = copy.deepcopy(intertwiner_report)
    bad["carriers"]["carrier_count"] = 24
    bad_inputs.append({"intertwiner_report": bad})

    for field, value in (
        ("reduced_constraint_rank_mod_prime", 505),
        ("integer_nullspace_residual_zero_exact", False),
    ):
        bad = copy.deepcopy(constraints)
        bad[field] = value
        bad_inputs.append({"constraint_certificate": bad})

    duplicate_basis = list(subject._basis_data()[0])
    duplicate_basis[-1] = duplicate_basis[0]
    bad_inputs.append({"matrices": tuple(duplicate_basis)})

    for mutation in bad_inputs:
        report = _assemble(**mutation)
        assert report["n_failed"] > 0
        assert report["status"] == (
            "RANK1_SU4_PHI210_QUADRATIC_BASIS_EXECUTION_FAILED"
        )
        assert report["overall_state"] == "EXECUTION_FAIL"
        assert report["scope"][
            "SU4_invariant_quadratic_form_basis_constructed"
        ] is False
        assert report["scope"]["G3_closed"] is False
        assert report["scope"]["whole_model_validated"] is False
        assert report["scope"]["whole_model_excluded"] is False


def test_generated_artifacts_match_exact_live_bytes_and_keep_g3_open():
    report = subject.build_report()
    expected_json = json.dumps(
        subject._jsonable(report), indent=2, sort_keys=True
    ) + "\n"
    assert subject.OUT_JSON.read_text(encoding="utf-8") == expected_json
    assert subject.OUT_MD.read_text(encoding="utf-8") == subject.render_markdown(
        report
    )

    stored = json.loads(subject.OUT_JSON.read_text(encoding="utf-8"))
    assert stored["status"] == subject.STATUS
    assert stored["n_failed"] == 0
    assert stored["scope"]["augmented_homogeneous_Schur_SOS_SDP_constructed"] is False
    assert stored["scope"]["arbitrary_real_Phi_lower_bound_proved"] is False
    assert stored["scope"]["G3_closed"] is False
    assert stored["scope"]["whole_model_validated"] is False
    assert stored["scope"]["whole_model_excluded"] is False
    markdown = subject.OUT_MD.read_text(encoding="utf-8")
    assert "full augmented Schur/SOS SDP: `OPEN`" in markdown
    assert "G3: `OPEN`" in markdown


def test_source_is_exact_isolated_and_uses_live_arithmetic_bounds():
    source = Path(subject.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported.update(
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    )
    assert (
        "exact_gauged_u1x_g3_su5_max_negative_sigma35_orbits_v20"
        not in imported
    )
    assert "np.linalg" not in source
    assert '"maximum_absolute_entry": 8' not in source
    assert "np.max(np.abs(matrix.data), initial=0)" in source
    assert "vector[int(row)] * vector[int(column)]" in source
