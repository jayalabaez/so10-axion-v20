from __future__ import annotations

import copy
import math

import pytest

import susy_v67_spin11_t66_baryon_proton_stress_audit as audit


@pytest.fixture(scope="module")
def report() -> dict:
    return audit.build_report()


def _rehash(value: dict) -> dict:
    value["core_sha256"] = audit.canonical_sha(value)
    return value


def test_exact_v66_lineage_is_bound(report: dict) -> None:
    assert report["lineage"]["V66_route"]["core_sha256"] == audit.EXPECTED_V66_ROUTE_CORE
    assert report["lineage"]["V66_master"]["core_sha256"] == audit.EXPECTED_V66_MASTER_CORE
    assert report["lineage"]["V55_proton_comparison"]["core_sha256"] == audit.EXPECTED_V55_CORE
    frozen = report["lineage"]["frozen_proton_sources"]
    assert frozen["scalar_raw_sha256"] == audit.EXPECTED_SCALAR_SOURCE_RAW


def test_u_portal_schur_complement_and_half_convention(report: dict) -> None:
    portal = report["t66_u_portal_schur_complement"]
    assert portal["normalized_determinant"] == -1
    assert portal["matrix_times_inverse"] == [[1, 0], [0, 1]]
    assert portal["family_convention"]["lambda_symmetry"] == "lambda_ij=-lambda_ji"
    assert portal["family_convention"]["full_ordered_family_sum_prefactor"] == "1/2"
    assert "2 M10" in portal["effective_superpotential_ordered_sum"]


def test_schur_operator_has_exact_global_numbers(report: dict) -> None:
    numbers = report["t66_u_portal_schur_complement"]["global_numbers"]
    assert numbers["Delta_B"] == -1
    assert numbers["Delta_L"] == -1
    assert numbers["Delta_B_minus_L"] == 0
    matched = report["t66_u_portal_schur_complement"]["heavy_N_matching"]
    assert "sum_m (M_N^-1)_{l m}" in matched["mixing_tensor"]
    assert "sum_l rho_{k l}" in matched["after_EWSB"]
    post = matched["post_Majorana_field_numbers"]
    assert post["Delta_B"] == -1
    assert post["Delta_L"] == 1
    assert post["Delta_B_minus_L"] == -2


def test_unified_one_sided_selector_no_go_is_family_dependent_and_factorwise(
    report: dict,
) -> None:
    no_go = report["unified_selector_one_sided_no_go"]
    assert no_go["result"] == (
        "NO_SCOPED_FAMILY_DEPENDENT_UNIFIED_ABELIAN_SELECTOR_CAN_FORBID_"
        "ALL_CONJUGATE_PORTALS"
    )
    scan = no_go["family_dependent_scan"]
    assert scan["charge_assignment_count"] == 179998
    assert scan["structurally_full_rank_assignment_count"] == 2590
    assert scan["wanted_portal_case_count"] == 7770
    assert scan["counterexample_count"] == 0
    assert scan["counterexamples"] == []
    assert scan["sample_determinant_witnesses"]
    assert "same sigma" in no_go["extension_to_products"]


def test_selector_determinant_witnesses_replay_exactly(report: dict) -> None:
    witnesses = report["unified_selector_one_sided_no_go"][
        "family_dependent_scan"
    ]["sample_determinant_witnesses"]
    for row in witnesses:
        n = row["modulus"]
        w = 0 if row["type"] == "ordinary" else 2 % n
        f = row["family_charges"]
        sigma = row["determinant_permutation"]
        i, j = row["wanted_pair"]
        k, ell = row["guaranteed_conjugate_pair"]
        assert all((f[a] + f[sigma[a]] - w) % n == 0 for a in range(3))
        assert (row["wanted_companion_charge_c"] + f[i] + f[j] - w) % n == 0
        assert (row["GM_partner_charge_cbar"] + f[k] + f[ell] - w) % n == 0


def test_b3_operator_table_is_the_required_one_sided_escape(report: dict) -> None:
    b3 = report["conditional_b3_ir_escape"]
    charges = b3["operator_charges_mod3"]
    assert charges["rho_QbarX_Q_Nc"] == 0
    assert charges["rho_EX_Ec_Nc"] == 0
    assert charges["rho_UX_Uc_Nc"] != 0
    assert all(b3["wanted_and_safe_checks"].values())


def test_b3_anomaly_sums_and_minimality_are_exact(report: dict) -> None:
    b3 = report["conditional_b3_ir_escape"]
    assert b3["anomaly_sums"] == {
        "A3_2T": 12,
        "A2_2T": 9,
        "Agrav": 63,
        "AYY_6Y_integer": 954,
        "AYZZ_6Y_integer": -90,
        "AZZZ": 207,
    }
    standard = b3["standard_discrete_anomaly_checks"]
    assert set(standard["linear_residues_mod3"].values()) == {0}
    assert standard["integer_parent_cubic_AZZZ_residue_mod9"] == 0
    assert standard["pass"] is True
    assert b3["extra_representative_abelian_congruences"][
        "not_universal_low_energy_constraints"
    ] is True
    scan = b3["minimality_scan"]
    assert scan["minimal_modulus_within_scan"] == 3
    assert scan["solution_counts"]["2"] == 0
    assert scan["solution_counts"]["3"] == 6
    assert scan["not_a_complete_discrete_symmetry_classification"] is True
    assert scan["N3_orbit_equals_all_minimal_rows"] is True


def test_b3_supplements_inherited_matter_parity(report: dict) -> None:
    stack = report["conditional_b3_ir_escape"]["symmetry_stack"]
    assert stack["B3_is_not_a_replacement_for_matter_parity"] is True
    assert stack["retained_inherited_remnant"] == "Z4R -> Z2 matter parity"
    assert set(stack["operator_charges_mod3"].values()) == {0}
    assert stack["B3_alone_allows"] == ["L L Ec", "L Q Dc"]


def test_b3_is_not_misrepresented_as_a_5d_repair(report: dict) -> None:
    compatibility = report["conditional_b3_ir_escape"]["current_action_compatibility"]
    assert compatibility["accepted"] is False
    assert compatibility["IR_anomaly_pass_is_not_a_5D_embedding"] is True
    assert "Dai-Freed" in compatibility["required_new_physics"]


def test_dimension_five_comparison_is_conditional_and_tiny(report: dict) -> None:
    stress = report["dimension_five_portal_stress"]
    point = stress["illustrative_common_T66_threshold"]
    assert math.isclose(point["M10_GeV"], 1.3839052519326706e4, rel_tol=1e-13)
    assert math.isclose(point["required_Meff_GeV"], 5.488346121307085e19, rel_tol=2e-13)
    assert math.isclose(
        point["maximum_abs_lambda_rho_thetaN_D"], 2.521534213303378e-16, rel_tol=2e-13
    )
    assert stress["O1_unprotected_portals_pass_comparison"] is False
    assert stress["claim_boundary"] == "CONDITIONAL_FEASIBILITY_BOUND_NOT_A_LIFETIME"


def test_h66_proxy_fails_only_the_central_identification(report: dict) -> None:
    rows = {row["branch"]: row for row in report["dimension_six_proton_proxy"]["rows"]}
    h = rows["H66"]
    assert math.isclose(h["central_proxy_lifetime_years"], 1.5597289442481415e33, rel_tol=2e-13)
    assert h["central_proxy_passes"] is False
    assert h["branch_globally_decided"] is False
    assert math.isclose(h["required_MX_over_MG"], 1.980571509992, rel_tol=2e-13)
    assert math.isclose(h["required_MX_GeV"], 4.688170168087496e15, rel_tol=2e-13)


def test_t66_proxy_pass_does_not_close_g7(report: dict) -> None:
    rows = {row["branch"]: row for row in report["dimension_six_proton_proxy"]["rows"]}
    t = rows["T66"]
    assert math.isclose(t["central_proxy_lifetime_years"], 1.4369016400754121e35, rel_tol=2e-13)
    assert t["central_proxy_passes"] is True
    assert t["branch_globally_decided"] is False
    assert math.isclose(t["required_MX_over_MG"], 0.6392872608832292, rel_tol=2e-13)
    assert report["gate_decision"]["status"] == "OPEN_WITH_MATERIAL_ADVANCE"
    assert report["gate_decision"]["V67_master_gate_promotion"] is False


def test_all_gates_and_terminal_decision_fail_closed(report: dict) -> None:
    assert all(row["status"] == "OPEN" for row in report["G2_G8_closability_ranking"])
    terminal = report["terminal_decision"]
    assert terminal["current_Spin11_action_status"] == "REJECTED"
    assert terminal["G7_closed"] is False
    assert terminal["closed_gates"] == []
    assert terminal["complete_theory"] is False
    assert report["claim_boundary"]["proton_lifetime_predicted"] is False
    assert report["claim_boundary"]["any_gate_closed"] is False
    assert "displayed T66 U-channel" in report["gate_decision"]["advance"]
    assert "unique T66 U-channel" not in report["gate_decision"]["advance"]


def test_primary_sources_are_explicit(report: dict) -> None:
    urls = {row["url"] for row in report["primary_sources"]}
    assert "https://arxiv.org/abs/hep-ph/0512163" in urls
    assert "https://arxiv.org/abs/2010.16098" in urls
    assert "https://arxiv.org/abs/1003.2625" in urls
    assert "https://arxiv.org/abs/1408.1195" in urls


def test_source_manifest_binds_all_local_inputs(report: dict) -> None:
    manifest = report["source_manifest"]
    assert isinstance(manifest, list)
    assert len(manifest) == 8
    assert all(row["exists"] for row in manifest)
    by_path = {row["path"]: row["raw_sha256"] for row in manifest}
    assert by_path[audit.SCALAR_SOURCE_PATH.name] == audit.file_sha(
        audit.SCALAR_SOURCE_PATH
    )
    assert by_path[audit.TEST_PATH.name] == audit.file_sha(audit.TEST_PATH)


def test_integrity_count_and_canonical_core(report: dict) -> None:
    assert report["n_integrity_checks"] == len(report["integrity_checks"])
    assert report["n_failed_integrity_checks"] == 0
    assert all(report["integrity_checks"].values())
    assert audit.canonical_sha(report) == report["core_sha256"]


@pytest.mark.parametrize(
    "mutator",
    [
        lambda r: r["lineage"]["V66_route"].update(core_sha256="0" * 64),
        lambda r: r["t66_u_portal_schur_complement"]["global_numbers"].update(Delta_B=0),
        lambda r: r["t66_u_portal_schur_complement"]["heavy_N_matching"][
            "post_Majorana_field_numbers"
        ].update(Delta_L=-1),
        lambda r: r["unified_selector_one_sided_no_go"]["family_dependent_scan"].update(
            counterexample_count=1
        ),
        lambda r: r["conditional_b3_ir_escape"]["charges"].update(UX=0),
        lambda r: r["conditional_b3_ir_escape"]["anomaly_sums"].update(AZZZ=208),
        lambda r: r["dimension_six_proton_proxy"]["rows"][0].update(
            central_proxy_lifetime_years=2.4e34
        ),
        lambda r: r["terminal_decision"].update(G7_closed=True),
    ],
)
def test_semantic_mutations_are_rejected_even_after_rehash(report: dict, mutator) -> None:
    changed = copy.deepcopy(report)
    mutator(changed)
    _rehash(changed)
    with pytest.raises(RuntimeError):
        audit.validate_report(changed)


def test_persisted_outputs_match_live_recomputation() -> None:
    checked = audit.check_outputs()
    assert checked["core_sha256"] == audit.build_report()["core_sha256"]
