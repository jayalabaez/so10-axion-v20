import ast
from collections import Counter
import copy
import json
from pathlib import Path

import numpy as np
from scipy import sparse

import exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20 as subject


def test_gaussian_exterior_basis_has_exact_kinetic_normalization():
    one_real, one_imaginary = subject.gaussian_one_form_basis()
    assert np.array_equal(
        one_real.T @ one_real + one_imaginary.T @ one_imaginary,
        2 * np.eye(10, dtype=np.int64),
    )
    assert not np.any(
        one_real.T @ one_imaginary - one_imaginary.T @ one_real
    )

    certificate = subject.exact_intertwiner_certificate()
    assert certificate["exterior_basis_shape"] == (210, 210)
    assert certificate["exterior_basis_Bdagger_B_equals_16I_exact"]
    assert len(certificate["exterior_basis_sha256"]) == 64
    assert certificate["proof_grade"]


def test_all_live_stabilizer_actions_intertwine_and_cartans_give_weights():
    certificate = subject.exact_intertwiner_certificate()
    assert certificate["intertwining_convention"] == "G_Phi B = B G_Lambda4"
    assert certificate["intertwining_count"] == 15
    assert [row["generator"] for row in certificate["intertwinings"]] == [
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
    ]
    assert all(row["exact"] for row in certificate["intertwinings"])
    assert certificate["all_15_intertwinings_exact"]
    assert certificate["Cartan_weight_diagonalization_exact"]
    assert certificate["n_distinct_Cartan_weights"] == 65
    assert certificate["zero_weight_multiplicity"] == 12

    # Negative control: the H1 exterior action cannot intertwine the H2 live
    # action through the invertible Gaussian basis.
    basis = subject.gaussian_exterior_basis()
    wrong_phi = subject.stabilizer.exact_phi210_actions()[1]
    h1 = subject.su4_exterior_actions()[0]
    left = (wrong_phi @ basis[0], wrong_phi @ basis[1])
    right = subject._gaussian_matmul(basis, h1)
    residual = (left[0] - right[0], left[1] - right[1])
    assert not (
        subject._sparse_is_zero(residual[0])
        and subject._sparse_is_zero(residual[1])
    )


def test_ssyt_character_identity_derives_the_full_branching_census():
    certificate = subject.exact_character_certificate()
    assert certificate["exterior_dimension"] == 210
    assert certificate["exterior_distinct_weight_count"] == 65
    assert certificate["exterior_zero_weight_multiplicity"] == 12
    assert certificate["exterior_weight_multiplicity_histogram"] == {
        1: 14,
        2: 24,
        3: 12,
        6: 6,
        8: 8,
        12: 1,
    }
    assert certificate["SSYT_reconstructed_dimension"] == 210
    assert certificate["all_SSYT_dimensions_exact"]
    assert certificate["SSYT_character_identity_exact"]
    assert certificate["branching_multiplicities"] == {
        "1": 4,
        "4": 4,
        "4bar": 4,
        "6": 4,
        "15": 2,
        "10": 1,
        "10bar": 1,
        "20": 2,
        "20bar": 2,
        "20prime": 1,
    }
    assert certificate["proof_grade"]


def test_integral_c8_has_exact_spectrum_and_split_minimal_polynomial():
    c8_real, c8_imaginary = subject.integral_c8()
    assert sparse.isspmatrix_csr(c8_real)
    assert c8_real.dtype == np.int64
    assert subject._sparse_is_zero(c8_imaginary)

    certificate = subject.exact_c8_certificate()
    assert certificate["symmetric_exact"]
    assert certificate["exterior_basis_nonzero_entry_count"] == 388
    assert certificate["canonical_Phi210_nonzero_entry_count"] == 750
    assert certificate["canonical_Phi210_symmetric_exact"]
    assert certificate["canonical_to_exterior_C8_intertwining_exact"]
    assert certificate["commutes_with_all_15_generators_exact"]
    assert certificate["minimal_polynomial_roots"] == (
        0,
        15,
        20,
        32,
        36,
        39,
        48,
    )
    assert certificate["minimal_polynomial_coefficients_ascending"] == (
        0,
        646_963_200,
        -143_735_040,
        12_801_744,
        -586_920,
        14_665,
        -190,
        1,
    )
    assert certificate["minimal_polynomial_annihilates_exact"]
    assert certificate["int64_arithmetic_safe"]
    assert certificate["modular_eigenspace_nullities"] == {
        0: 4,
        15: 32,
        20: 24,
        32: 30,
        36: 20,
        39: 80,
        48: 20,
    }
    assert certificate["modular_nullities_sum"] == 210
    assert certificate["spectrum_exact_over_Q"]
    assert certificate["minimal_polynomial_exact"]
    assert certificate["proof_grade"]


def test_twenty_five_exact_carriers_are_complete_and_give_45_pairings():
    certificate = subject.exact_carrier_certificate()
    assert certificate["natural_exterior_block_count"] == 16
    assert certificate["all_15_generators_preserve_natural_blocks_exact"]
    assert certificate["carrier_count"] == 25
    assert len(certificate["carriers"]) == 25
    assert all(
        row["exact_modular_rank"] == row["expected_dimension"]
        and row["C8_eigen_equation_exact"]
        and row["SSYT_character_exact"]
        for row in certificate["carriers"]
    )
    assert Counter(
        row["irrep"] for row in certificate["carriers"]
    ) == Counter(subject.EXPECTED_BRANCHING)
    assert certificate["concatenated_carrier_shape"] == (210, 210)
    assert certificate["concatenated_carrier_rank_mod_prime"] == 210
    assert certificate["symmetric_self_conjugate_pairings"] == 24
    assert certificate["complex_conjugate_pairings"] == 21
    assert certificate["Sym2_Phi210_SU4_singlet_dimension"] == 45
    assert certificate["SU4_invariant_quadratic_multiplicity_sector_dimension"] == 45
    assert certificate["proof_grade"]


def test_implementation_has_no_float_spectral_or_quarantined_dependency():
    source_path = Path(subject.__file__).resolve()
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
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
    assert (
        "exact_gauged_u1x_g3_su5_max_negative_sigma35_orbits_v20"
        not in imported_modules
    )
    assert "fractions" not in imported_modules
    assert "np.linalg.eig" not in source
    assert "np.linalg.eigh" not in source
    assert "np.linalg.svd" not in source


def test_report_is_reproducible_and_fail_closed_about_g3_scope():
    report = subject.build_report()
    assert report["n_failed"] == 0
    assert report["model_contract_id"] == "gauged_u1x_phi17_v20"
    assert subject.MODEL_CONTRACT_ID == subject.stabilizer.MODEL_CONTRACT_ID
    assert report["status"] == (
        "EXACT_RANK1_SU4_PHI210_INTERTWINER_INFRASTRUCTURE_CERTIFIED"
    )
    assert report["overall_state"] == (
        "SU4_SCHUR_INFRASTRUCTURE_CLOSED__SDP_AND_G3_OPEN"
    )
    assert report["scope"]["deterministic_irreducible_carriers_complete"]
    assert report["scope"]["Sym2_SU4_invariant_dimension_45_proved"]
    assert report["scope"]["H_fixed_to_h_minus"]
    assert report["scope"]["Sigma_fixed_to_q_over_4"]
    assert report["scope"]["rank1_endpoint_SU4_stabilizer_used"]
    assert report["scope"]["companion_stabilizer_provenance_exact"]
    provenance = report["companion_stabilizer_provenance"]
    assert provenance["model_contract_id"] == subject.MODEL_CONTRACT_ID
    assert provenance["tangent_proof_grade"]
    assert provenance["Phi210_action_proof_grade"]
    assert provenance["all_required_provenance_exact"]
    assert report["scope"]["SU4_invariant_quadratic_form_basis_constructed"] is False
    assert report["scope"]["Schur_SOS_SDP_constructed"] is False
    assert report["scope"]["arbitrary_real_Phi_lower_bound_proved"] is False
    assert report["scope"]["arbitrary_rank1_Phi_proved"] is False
    assert report["scope"]["G3_closed"] is False
    assert report["scope"]["whole_model_excluded"] is False
    assert report["checks"]["G3_closed"] is False

    expected_json = json.dumps(
        subject._jsonable(report), indent=2, sort_keys=True
    ) + "\n"
    assert subject.OUT_JSON.read_text(encoding="utf-8") == expected_json
    assert subject.OUT_MD.read_text(encoding="utf-8") == subject.render_markdown(
        report
    )


def test_report_assembler_fails_closed_under_companion_mutations():
    companion_report = subject.stabilizer.build_report()
    tangent = subject.stabilizer.exact_stabilizer_tangent_certificate()
    phi210 = subject.stabilizer.exact_phi210_action_certificate()

    def assemble(
        *,
        contract=subject.stabilizer.MODEL_CONTRACT_ID,
        report=companion_report,
        tangent_certificate=tangent,
        phi210_certificate=phi210,
        intertwiner_certificate=subject.exact_intertwiner_certificate(),
    ):
        return subject._build_report_from_certificates(
            companion_model_contract_id=contract,
            companion_report=report,
            companion_tangent=tangent_certificate,
            companion_phi210=phi210_certificate,
            intertwiner=intertwiner_certificate,
            character=subject.exact_character_certificate(),
            c8=subject.exact_c8_certificate(),
            carriers=subject.exact_carrier_certificate(),
        )

    companion_mutations = []
    companion_mutations.append(assemble(contract="wrong_model_contract"))

    bad_report = copy.deepcopy(companion_report)
    bad_report["scope"]["H_fixed_to_h_minus"] = False
    companion_mutations.append(assemble(report=bad_report))

    bad_report = copy.deepcopy(companion_report)
    bad_report["scope"][
        "Sigma_fixed_to_normalized_explicit_decomposable_pure_spinor_q_over_4"
    ] = False
    companion_mutations.append(assemble(report=bad_report))

    bad_tangent = copy.deepcopy(tangent)
    bad_tangent["proof_grade"] = False
    companion_mutations.append(assemble(tangent_certificate=bad_tangent))

    bad_tangent = copy.deepcopy(tangent)
    bad_tangent["fixed_endpoint"]["endpoint_binding_exact"] = False
    companion_mutations.append(assemble(tangent_certificate=bad_tangent))

    bad_phi210 = copy.deepcopy(phi210)
    bad_phi210["proof_grade"] = False
    companion_mutations.append(assemble(phi210_certificate=bad_phi210))

    intertwiner_mutations = []
    bad_intertwiner = copy.deepcopy(subject.exact_intertwiner_certificate())
    bad_intertwiner["proof_grade"] = False
    intertwiner_mutations.append(assemble(intertwiner_certificate=bad_intertwiner))

    bad_intertwiner = copy.deepcopy(subject.exact_intertwiner_certificate())
    bad_intertwiner["intertwining_count"] = 14
    intertwiner_mutations.append(assemble(intertwiner_certificate=bad_intertwiner))

    bad_intertwiner = copy.deepcopy(subject.exact_intertwiner_certificate())
    bad_intertwiner["intertwinings"] = []
    intertwiner_mutations.append(assemble(intertwiner_certificate=bad_intertwiner))

    for mutated in companion_mutations + intertwiner_mutations:
        assert mutated["n_failed"] > 0
        assert mutated["overall_state"] == "EXECUTION_FAIL"
        assert mutated["scope"]["G3_closed"] is False

    for mutated in companion_mutations:
        assert mutated["companion_stabilizer_provenance"][
            "all_required_provenance_exact"
        ] is False
        assert mutated["scope"]["H_fixed_to_h_minus"] is False
        assert mutated["scope"]["Sigma_fixed_to_q_over_4"] is False
        assert mutated["scope"]["rank1_endpoint_SU4_stabilizer_used"] is False
        assert mutated["scope"]["companion_stabilizer_provenance_exact"] is False

    for mutated in intertwiner_mutations:
        assert mutated["checks"]["all_15_live_SU4_intertwinings_exact"] is False
        assert mutated["scope"]["Phi210_complexified_representation_resolved"] is False
