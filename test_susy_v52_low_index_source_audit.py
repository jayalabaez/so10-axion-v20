from __future__ import annotations

import json

import numpy as np

import susy_v52_low_index_source_audit as audit


def test_tensor_coordinate_bases_are_exact() -> None:
    symmetric = audit.symmetric_traceless_basis()
    antisymmetric = audit.antisymmetric_basis()
    assert len(symmetric) == 54
    assert len(antisymmetric) == 45
    assert all(np.array_equal(item, item.T) and np.trace(item) == 0 for item in symmetric)
    assert all(np.array_equal(item, -item.T) for item in antisymmetric)


def test_spin_generators_are_locked_chiral_clifford_generators() -> None:
    generators = audit.spin_generators()
    assert len(generators) == 45
    assert all(item.shape == (16, 16) for item in generators)
    assert all(np.array_equal(2 * item, audit._gaussian_integer(2 * item, label="2T")) for item in generators)


def test_rational_witness_parameters_and_order_parameters() -> None:
    witness = audit.witness()
    assert witness["mE"] == 9 / 5
    assert witness["mA"] == 11
    assert witness["eta"] == -3j / 10
    assert witness["mC"] == 27 / 20
    assert np.diag(witness["S0"]).tolist() == [2] * 6 + [-3] * 4
    assert [witness["A0"][a, b] for a, b in ((0, 1), (2, 3), (4, 5), (6, 7), (8, 9))] == [1, 1, 1, 3, 3]
    assert witness["C0"][15] == witness["barC0"][15] == 10


def test_all_131_f_terms_vanish_exactly() -> None:
    terms = audit.f_term_numerators()
    assert {name: value.size for name, value in terms.items()} == {
        "S_F_x400": 54,
        "A_F_x400": 45,
        "C_F_x400": 16,
        "barC_F_x400": 16,
    }
    assert sum(np.count_nonzero(value) for value in terms.values()) == 0


def test_all_compact_d_moments_vanish_exactly() -> None:
    moments = audit.d_moment_numerator()
    assert moments.shape == (45,)
    assert np.count_nonzero(moments) == 0


def test_full_hessian_is_exact_complex_symmetric() -> None:
    hessian = audit.hessian_numerator()
    assert hessian.shape == (131, 131)
    assert np.array_equal(hessian, hessian.T)
    assert np.array_equal(hessian, audit._gaussian_integer(hessian, label="H"))
    assert np.count_nonzero(hessian) > 500


def test_orbit_and_hessian_modular_ranks() -> None:
    orbit = audit.orbit_numerator()
    hessian = audit.hessian_numerator()
    assert orbit.shape == (131, 45)
    assert audit.modular_rank(audit._modular_matrix(orbit)) == 33
    assert audit.modular_rank(audit._modular_matrix(hessian)) == 98


def test_exact_ward_product_and_kernel_saturation() -> None:
    orbit = audit.orbit_numerator()
    hessian = audit.hessian_numerator()
    assert np.count_nonzero(hessian @ orbit) == 0
    assert 33 + 98 == 131


def test_report_certifies_SM_stabilizer_and_no_extra_source_modulus() -> None:
    report = audit.build_report()
    geometry = report["exact_local_geometry"]
    assert geometry["stabilizer_dimension"] == 12
    assert geometry["unbroken_group"].startswith("SU(3)c x SU(2)L")
    assert geometry["E54_orbit_rank"] == 24
    assert geometry["spinor_pair_orbit_rank"] == 21
    assert geometry["E54_plus_spinor_pair_orbit_rank"] == 33
    assert "intersection SU(5)" in geometry["intersection_identification"]
    assert geometry["kernel_equals_broken_gauge_orbit"] is True
    assert "lower-bound" in geometry["exact_rank_lemma"]
    assert audit.MODULAR_I**2 % audit.MODULAR_PRIME == audit.MODULAR_PRIME - 1


def test_dynkin_reduction_and_landau_window_are_scoped_correctly() -> None:
    data = audit.build_report()["perturbativity"]
    assert data["source_sum_T"] == 24
    assert data["v51_Higgs_source_T"] == 126
    assert data["Higgs_source_reduction_factor_vs_v51"] == 5.25
    assert data["one_loop_b_source_only"] == 0
    assert data["one_loop_b_with_three_16_families_and_one_10H"] == 7
    assert data["landau_pole_over_matching_scale_if_b_positive"] > 1.0e9
    assert "link" in data["scope_caveat"]


def test_optional_vectorlike_U1F_anomalies_cancel() -> None:
    ledger = audit.build_report()["anomaly_ledger"]
    assert ledger["optional_U1F_Spin10_squared"] == 0
    assert ledger["optional_gravity_squared_U1F"] == 0
    assert ledger["optional_U1F_cubed"] == 0
    assert "diagonal" in ledger["integration_caveat"]


def test_seesaw_parity_and_doublet_triplet_are_fail_closed() -> None:
    report = audit.build_report()
    physics = report["phenomenology_fail_closed"]
    assert physics["renormalizable_type_I_seesaw"] == "absent"
    assert "not automatic" in physics["matter_parity"]
    assert "not supplied" in physics["missing_partner"]
    assert report["gate_effect"]["G2"] == "OPEN"
    assert report["gate_effect"]["clause_promotions"] == []


def test_hash_is_deterministic_and_valid() -> None:
    first = audit.build_report()
    second = audit.build_report()
    assert first["core_sha256"] == second["core_sha256"]
    assert audit.canonical_sha(first) == first["core_sha256"]
    audit.validate_report(first)


def test_generated_artifacts_are_current() -> None:
    report = audit.check_artifacts()
    disk = json.loads(audit.JSON_PATH.read_text(encoding="utf-8"))
    assert disk["core_sha256"] == report["core_sha256"]
    assert report["core_sha256"] in audit.MD_PATH.read_text(encoding="utf-8")
