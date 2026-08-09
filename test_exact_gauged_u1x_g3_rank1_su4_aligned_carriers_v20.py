import ast
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
from scipy import sparse

import exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20 as subject


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


def test_exact_A3_chevalley_system_and_deterministic_hashes():
    certificate = subject.exact_chevalley_certificate()
    assert certificate["simple_root_pairs"] == ("12", "23", "34")
    assert certificate["A3_Cartan_matrix"].tolist() == [
        [2, -1, 0],
        [-1, 2, -1],
        [0, -1, 2],
    ]
    assert certificate["all_actions_integral_real"]
    assert certificate["all_9_EF_commutators_exact"]
    assert certificate["all_18_Cartan_weight_relations_exact"]
    assert certificate["all_12_Serre_relations_exact"]
    assert certificate["raising_sha256"] == (
        "76f1a49db62078f1ef430a110f79770939446fb773064a04c1754c38f68eae44"
    )
    assert certificate["lowering_sha256"] == (
        "24ecb258b738dd7107c560df8226620756313997659dd0c78b786affc260d158"
    )
    assert certificate["proof_grade"]

    # Negative control: replacing F1 by F2 destroys [E1,F1]=D1.
    actions = subject.chevalley_actions()
    wrong = (
        actions["raising"][0] @ actions["lowering"][1]
        - actions["lowering"][1] @ actions["raising"][0]
        - actions["cartan"][0]
    )
    assert not subject._sparse_is_zero(wrong)


def test_upstream_source_bytes_and_full_literal_certificates_are_pinned():
    source_contract = subject.upstream_source_contract_certificate()
    assert set(source_contract) == {
        "upstream_module",
        "upstream_module_sha256",
        "expected_upstream_module_sha256",
        "stabilizer_module",
        "stabilizer_module_sha256",
        "expected_stabilizer_module_sha256",
        "both_modules_resolve_to_repository_root_exact",
        "source_bytes_match_pinned_contract_exact",
        "proof_grade",
    }
    assert source_contract["upstream_module"] == subject.EXPECTED_UPSTREAM_MODULE
    assert source_contract["upstream_module_sha256"] == (
        subject.EXPECTED_UPSTREAM_SOURCE_SHA256
    )
    assert source_contract["stabilizer_module"] == (
        subject.EXPECTED_STABILIZER_MODULE
    )
    assert source_contract["stabilizer_module_sha256"] == (
        subject.EXPECTED_STABILIZER_SOURCE_SHA256
    )
    assert source_contract["proof_grade"]

    assert subject._canonical_json_sha256(subject.upstream.build_report()) == (
        subject.EXPECTED_UPSTREAM_REPORT_SHA256
    )
    assert subject._canonical_json_sha256(
        subject.upstream.exact_intertwiner_certificate()
    ) == subject.EXPECTED_UPSTREAM_INTERTWINER_SHA256
    assert subject._canonical_json_sha256(
        subject.upstream.exact_carrier_certificate()
    ) == subject.EXPECTED_UPSTREAM_CARRIERS_SHA256


def test_public_alignment_api_has_common_words_actions_and_full_direct_sum():
    data = subject.exact_aligned_carrier_data()
    assert data["rational_matrix_convention"] == (
        "(int64 numerator, positive common denominator)"
    )
    assert len(data["families"]) == 10
    assert len(data["carriers"]) == 25
    assert tuple(data["families"]) == tuple(subject.upstream.EXPECTED_BRANCHING)
    assert data["generator_labels"] == subject.upstream.stabilizer.SU4_LABELS

    observed = Counter()
    bases = []
    family_action_ids = {}
    for carrier in data["carriers"]:
        observed[carrier["irrep"]] += 1
        dimension = carrier["dimension"]
        assert carrier["exterior_basis"].shape == (210, dimension)
        assert carrier["canonical_basis_real"].shape == (210, dimension)
        assert carrier["canonical_basis_imaginary"].shape == (210, dimension)
        assert carrier["exterior_gram"].shape == (dimension, dimension)
        assert np.array_equal(
            carrier["exterior_gram"], carrier["exterior_gram"].T
        )
        assert len(carrier["lowering_words"]) == dimension
        assert len(carrier["source_actions"]) == 15
        assert carrier["lowering_words"] == data["families"][
            carrier["irrep"]
        ]["lowering_words"]
        family_action_ids.setdefault(
            carrier["irrep"], id(carrier["source_actions"])
        )
        assert id(carrier["source_actions"]) == family_action_ids[
            carrier["irrep"]
        ]
        for action in carrier["source_actions"]:
            assert action["label"] in data["generator_labels"]
            for part in ("real", "imaginary"):
                numerator, denominator = action[part]
                assert numerator.shape == (dimension, dimension)
                assert numerator.dtype == np.int64
                assert isinstance(denominator, int) and denominator > 0
        bases.append(carrier["exterior_basis"])
    assert observed == Counter(subject.upstream.EXPECTED_BRANCHING)
    complete = sparse.hstack(bases, format="csr")
    assert subject._rank_mod_prime(complete.toarray()) == 210

    certificate = subject.exact_aligned_carrier_certificate()
    assert certificate["concatenated_aligned_basis_sha256"] == (
        "f9fea5fffb98c36837e59f94bb12e0c89bec5b49c82a5ec5628d13223a358dbe"
    )


def test_every_copy_has_exact_common_and_live_canonical_intertwinings():
    certificate = subject.exact_aligned_carrier_certificate()
    assert certificate["family_count"] == 10
    assert certificate["carrier_count"] == 25
    assert certificate["upstream_carrier_order_exact"]
    assert certificate["all_family_word_counts_equal_dimensions"]
    assert certificate["all_25_carriers_exact"]
    assert certificate[
        "all_equivalent_copies_use_common_source_actions_exact"
    ]
    assert certificate[
        "all_25_physical_Gaussian_embeddings_intertwine_live_Phi210_exact"
    ]
    assert certificate["concatenated_aligned_basis_shape"] == (210, 210)
    assert certificate["concatenated_aligned_basis_rank_mod_prime"] == 210
    arithmetic = certificate[
        "exact_integer_and_rational_arithmetic_safety"
    ]
    assert arithmetic["Python_Fraction_Gauss_Jordan_solver_exact"]
    assert arithmetic["Python_integer_denominator_lcm_and_products_exact"]
    assert arithmetic["checked_products_have_Python_integer_fallback"]
    assert arithmetic["checked_results_reject_out_of_int64_range"]
    assert arithmetic["all_published_matrices_have_int64_dtype"]
    assert arithmetic["all_live_conservative_bounds_fit_int64"]
    assert arithmetic["proof_grade"]
    assert all(
        row["aligned_rank_mod_prime"] == row["dimension"]
        and row["highest_weight_primitive_and_raising_annihilated"]
        and row["natural_block_support_exact"]
        and row["C8_eigen_equation_exact"]
        and row["all_15_common_source_actions_intertwine_exact"]
        and row["all_15_live_canonical_Phi210_actions_intertwine_exact"]
        for row in certificate["carriers"]
    )
    assert certificate["proof_grade"]


def test_physical_conjugation_pairs_and_real_structures_are_exact():
    data = subject.exact_aligned_carrier_data()
    certificate = subject.exact_aligned_carrier_certificate()
    conjugation = data["exterior_conjugation"]
    assert conjugation.shape == (210, 210)
    assert conjugation.nnz == 210
    assert subject._sparse_is_zero(
        conjugation @ conjugation
        - sparse.identity(210, dtype=np.int64, format="csr")
    )
    assert certificate["exterior_conjugation_signed_permutation_exact"]
    assert certificate["exterior_conjugation_square_equals_identity_exact"]
    assert certificate["Gaussian_basis_conjugation_is_physical_exact"]
    assert certificate["conjugation_compatible_with_all_15_generators_exact"]
    assert certificate["all_25_conjugate_carrier_maps_exact"]
    assert certificate["all_25_conjugate_maps_involutive_exact"]
    assert certificate["self_conjugate_real_type_carrier_count"] == 11
    assert certificate["complex_type_carrier_count"] == 14

    by_name = {record["name"]: record for record in data["carriers"]}
    for carrier in data["carriers"]:
        partner = by_name[carrier["conjugate_carrier_name"]]
        assert partner["conjugate_carrier_name"] == carrier["name"]
        assert partner["irrep"] == subject.CONJUGATE_IRREP[carrier["irrep"]]
        assert subject._rational_is_identity(
            subject._rational_product(
                partner["conjugation_map"], carrier["conjugation_map"]
            )
        )
        if carrier["irrep"] in subject.SELF_CONJUGATE_IRREPS:
            assert carrier["reality_kind"] == "self_conjugate_real_type"
        else:
            assert carrier["reality_kind"] == "complex_type_conjugate_pair"

    # Negative control: a 4 carrier cannot be physically paired with a 4
    # carrier; conjugation reverses its highest-weight type to 4bar.
    fundamental = next(
        record for record in data["carriers"] if record["irrep"] == "4"
    )
    wrong = next(
        record
        for record in data["carriers"]
        if record["irrep"] == "4" and record["name"] != fundamental["name"]
    )
    image = conjugation @ fundamental["exterior_basis"]
    joined = sparse.hstack((wrong["exterior_basis"], image), format="csr")
    assert subject._rank_mod_prime(joined.toarray()) > wrong["dimension"]


def test_report_is_reproducible_and_fail_closed_about_theory_scope():
    report = subject.build_report()
    assert report["n_failed"] == 0
    assert report["model_contract_id"] == "gauged_u1x_phi17_v20"
    assert report["status"] == (
        "EXACT_RANK1_SU4_ALIGNED_CARRIER_INFRASTRUCTURE_CERTIFIED"
    )
    assert report["overall_state"] == (
        "SU4_ALIGNED_CARRIERS_CLOSED__INVARIANT_BASIS_SDP_AND_G3_OPEN"
    )
    assert report["upstream_provenance"]["all_required_provenance_exact"]
    assert report["upstream_provenance"]["source_contract_exact"]
    assert report["upstream_provenance"]["full_schema_and_literals_exact"]
    assert report["alignment_provenance"]["full_schema_and_literals_exact"]
    assert report["scope"]["H_fixed_to_h_minus"]
    assert report["scope"]["Sigma_fixed_to_q_over_4"]
    assert report["scope"]["rank1_endpoint_SU4_stabilizer_used"]
    assert report["scope"]["aligned_complexified_Phi210_carriers_constructed"]
    assert report["scope"][
        "physical_real_structure_and_Gaussian_embeddings_constructed"
    ]
    assert report["scope"][
        "SU4_invariant_quadratic_form_basis_constructed"
    ] is False
    assert report["scope"]["Schur_SOS_SDP_constructed"] is False
    assert report["scope"]["arbitrary_real_Phi_lower_bound_proved"] is False
    assert report["scope"]["arbitrary_rank1_Phi_proved"] is False
    assert report["scope"]["G3_closed"] is False
    assert report["scope"]["whole_model_excluded"] is False

    expected_json = json.dumps(
        subject._jsonable(report), indent=2, sort_keys=True
    ) + "\n"
    assert subject.OUT_JSON.read_text(encoding="utf-8") == expected_json
    assert subject.OUT_MD.read_text(encoding="utf-8") == subject.render_markdown(
        report
    )
    assert subject.OUT_JSON.read_bytes() == expected_json.encode("utf-8")
    assert subject.OUT_MD.read_bytes() == subject.render_markdown(report).encode(
        "utf-8"
    )
    assert b"\r\n" not in subject.OUT_JSON.read_bytes()
    assert b"\r\n" not in subject.OUT_MD.read_bytes()


def test_report_assembler_rejects_upstream_and_alignment_mutations():
    source_contract = subject.upstream_source_contract_certificate()
    upstream_report = subject.upstream.build_report()
    intertwiner = subject.upstream.exact_intertwiner_certificate()
    carriers = subject.upstream.exact_carrier_certificate()
    alignment = subject.exact_aligned_carrier_certificate()

    def assemble(
        *,
        contract=subject.upstream.MODEL_CONTRACT_ID,
        source=source_contract,
        report=upstream_report,
        intertwiner_certificate=intertwiner,
        carrier_certificate=carriers,
        alignment_certificate=alignment,
    ):
        return subject._build_report_from_certificates(
            upstream_model_contract_id=contract,
            upstream_source_contract=source,
            upstream_report=report,
            upstream_intertwiner=intertwiner_certificate,
            upstream_carriers=carrier_certificate,
            alignment=alignment_certificate,
        )

    mutations = [assemble(contract="wrong_model_contract")]

    bad_source = copy.deepcopy(source_contract)
    bad_source["upstream_module_sha256"] = "0" * 64
    mutations.append(assemble(source=bad_source))

    bad_source_schema = copy.deepcopy(source_contract)
    bad_source_schema["unrecognized_claim"] = True
    mutations.append(assemble(source=bad_source_schema))

    bad_report = copy.deepcopy(upstream_report)
    bad_report["scope"]["companion_stabilizer_provenance_exact"] = False
    mutations.append(assemble(report=bad_report))

    bad_report_schema = copy.deepcopy(upstream_report)
    bad_report_schema["unrecognized_claim"] = True
    mutations.append(assemble(report=bad_report_schema))

    bad_intertwiner = copy.deepcopy(intertwiner)
    bad_intertwiner["all_15_intertwinings_exact"] = False
    mutations.append(assemble(intertwiner_certificate=bad_intertwiner))

    bad_intertwiner_schema = copy.deepcopy(intertwiner)
    bad_intertwiner_schema["unrecognized_claim"] = True
    mutations.append(
        assemble(intertwiner_certificate=bad_intertwiner_schema)
    )

    bad_carriers = copy.deepcopy(carriers)
    bad_carriers["concatenated_carrier_rank_mod_prime"] = 209
    mutations.append(assemble(carrier_certificate=bad_carriers))

    bad_carriers_schema = copy.deepcopy(carriers)
    bad_carriers_schema["unrecognized_claim"] = True
    mutations.append(assemble(carrier_certificate=bad_carriers_schema))

    for key in (
        "proof_grade",
        "all_equivalent_copies_use_common_source_actions_exact",
        "all_25_physical_Gaussian_embeddings_intertwine_live_Phi210_exact",
        "all_25_conjugate_maps_involutive_exact",
    ):
        bad_alignment = copy.deepcopy(alignment)
        bad_alignment[key] = False
        mutations.append(assemble(alignment_certificate=bad_alignment))

    bad_arithmetic = copy.deepcopy(alignment)
    bad_arithmetic[
        "exact_integer_and_rational_arithmetic_safety"
    ]["proof_grade"] = False
    mutations.append(assemble(alignment_certificate=bad_arithmetic))

    bad_alignment_schema = copy.deepcopy(alignment)
    bad_alignment_schema["unrecognized_claim"] = True
    mutations.append(assemble(alignment_certificate=bad_alignment_schema))

    for mutated in mutations:
        assert mutated["n_failed"] > 0
        assert mutated["overall_state"] == "EXECUTION_FAIL"
        assert mutated["scope"]["G3_closed"] is False
        assert mutated["scope"]["Schur_SOS_SDP_constructed"] is False


def test_cached_proof_objects_are_mutation_isolated_at_every_public_accessor():
    baseline_data = subject.exact_aligned_carrier_data()
    baseline_basis_hash = subject._matrix_sha256(
        baseline_data["carriers"][0]["exterior_basis"]
    )
    baseline_gram = baseline_data["carriers"][0]["exterior_gram"].copy()
    baseline_rational = baseline_data["carriers"][0]["source_actions"][0][
        "real"
    ][0].copy()
    baseline_certificate = subject.exact_aligned_carrier_certificate()
    baseline_report = subject.build_report()
    baseline_certificate_hash = subject._canonical_json_sha256(
        baseline_certificate
    )
    baseline_report_hash = subject._canonical_json_sha256(baseline_report)
    baseline_singlet_multiplicity = baseline_data["families"]["1"][
        "multiplicity"
    ]

    poisoned_data = subject.exact_aligned_carrier_data()
    poisoned_data["carriers"][0]["exterior_basis"].data[0] += 123
    poisoned_data["carriers"][0]["exterior_gram"][0, 0] += 123
    poisoned_data["carriers"][0]["source_actions"][0]["real"][0][0, 0] += 123
    poisoned_data["carriers"][0]["irrep"] = "poisoned"
    poisoned_data["families"]["1"]["multiplicity"] = -1
    poisoned_data["exterior_conjugation"].data[0] = 0

    poisoned_chevalley = subject.chevalley_actions()
    poisoned_chevalley["raising"][0].data[0] += 123
    poisoned_conjugation = subject.exterior_conjugation()
    poisoned_conjugation.data[0] = 0

    poisoned_certificate = subject.exact_aligned_carrier_certificate()
    poisoned_certificate["proof_grade"] = False
    poisoned_certificate["simple_Chevalley_system"]["A3_Cartan_matrix"][0, 0] = 0
    poisoned_certificate["carriers"][0]["irrep"] = "poisoned"
    poisoned_report = subject.build_report()
    poisoned_report["n_failed"] = 999
    poisoned_report["alignment"]["proof_grade"] = False
    poisoned_report["scope"]["G3_closed"] = True

    fresh_data = subject.exact_aligned_carrier_data()
    assert subject._matrix_sha256(
        fresh_data["carriers"][0]["exterior_basis"]
    ) == baseline_basis_hash
    assert np.array_equal(
        fresh_data["carriers"][0]["exterior_gram"], baseline_gram
    )
    assert np.array_equal(
        fresh_data["carriers"][0]["source_actions"][0]["real"][0],
        baseline_rational,
    )
    assert fresh_data["carriers"][0]["irrep"] != "poisoned"
    assert fresh_data["families"]["1"]["multiplicity"] == (
        baseline_singlet_multiplicity
    )
    assert np.all(np.abs(fresh_data["exterior_conjugation"].data) == 1)

    assert subject.exact_chevalley_certificate()["proof_grade"]
    assert np.all(np.abs(subject.exterior_conjugation().data) == 1)
    assert subject._canonical_json_sha256(
        subject.exact_aligned_carrier_certificate()
    ) == baseline_certificate_hash
    assert subject._canonical_json_sha256(
        subject.build_report()
    ) == baseline_report_hash


def test_checked_integer_arithmetic_uses_exact_fallback_and_rejects_overflow():
    cancellation = subject._checked_dense_matmul(
        np.asarray([[subject.INT64_MAX, subject.INT64_MAX]], dtype=np.int64),
        np.asarray([[1], [-1]], dtype=np.int64),
        "overflow-fallback cancellation control",
    )
    assert cancellation.dtype == np.int64
    assert cancellation.tolist() == [[0]]

    with pytest.raises(ArithmeticError, match="exceeds signed-int64"):
        subject._checked_dense_matmul(
            np.asarray([[subject.INT64_MAX]], dtype=np.int64),
            np.asarray([[2]], dtype=np.int64),
            "overflow rejection control",
        )


def test_implementation_has_no_float_solver_or_quarantined_dependency():
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
    assert "np.linalg.solve" not in source
    assert "np.linalg.eig" not in source
    assert "np.linalg.eigh" not in source
    assert "np.linalg.svd" not in source
