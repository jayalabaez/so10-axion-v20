from __future__ import annotations

import json
import subprocess
import sys
from fractions import Fraction

import susy_v37_nonanomaly_gate_audit as audit


REPORT = audit.build_report()


def test_source_is_intentionally_not_a_soft_pole_spectrum_model() -> None:
    source = REPORT["source_static_contract"]
    assert source["only_gauge_basis_state_declared"] is True
    assert source["source_soft_terms_disabled"] is True
    assert source["SPheno_m_present"] is False
    assert source["spectrum_generator_or_boundary_file_present"] is False
    assert source["parameter_file_contains_only_scale_definitions"] is True


def test_anomalon_holomorphic_mass_block_is_exactly_full_rank_generically() -> None:
    mass = REPORT["G2_tree_mass_rank"]
    assert mass["determinant"] == "a^2*b^2*c"
    assert mass["generic_full_rank_condition"] == "a*b*c != 0"
    assert mass["exact_rational_witness_abc"] == [2, 3, 5]
    assert mass["exact_rational_witness_rank"] == 5
    assert mass["exact_rational_witness_determinant"] == "180"


def test_canonical_global_susy_branch_is_exact_but_scoped() -> None:
    vacuum = REPORT["G3_canonical_global_SUSY_branch"]
    assert vacuum["solution_when_Delta_nonzero"] == ["U=vPS^2", "V=fPQ^2"]
    assert vacuum["F_terms_vanish_on_representative"] is True
    assert vacuum["D_terms_vanish_on_equal_conjugate_PS_VEVs"] is True
    assert vacuum["zero_energy_branch_is_global_minimum_of_that_truncation"] is True
    radial = vacuum["radial_holomorphic_hessian"]
    assert radial["generic_rank"] == 4
    assert radial["exact_rational_witness_rank"] == 4
    assert radial["exact_rational_witness_determinant"] == "1"
    assert "soft terms and SUSY-breaking tadpoles" in vacuum["not_established"]


def test_mu_protection_is_not_a_radiative_ewsb_solution() -> None:
    ewsb = REPORT["G4_electroweak_boundary"]
    assert ewsb["all_expected_H_bilinear_terms_present"] is True
    assert ewsb["bare_H_squared_source_term_present"] is False
    assert ewsb["tree_mu_on_canonical_global_SUSY_branch"].endswith("=0")
    assert ewsb["source_soft_terms_enabled"] is False
    assert ewsb["derived_Bmu_or_Higgs_soft_masses_present"] is False


def test_live_rges_do_not_create_a_physical_running_solution() -> None:
    rge = REPORT["G6_running_and_matching_boundary"]
    live = rge["live_SARAH_two_loop_RGE_attestation"]
    assert live["model_initialized"] is True
    assert live["two_loop_RGE_calculation_succeeded"] is True
    assert live["one_loop_gauge_b_4_L_R"] == [1, 5, 9]
    assert live["source_soft_terms_enabled"] is False
    assert all(value == 0 for value in rge["absent_physical_inputs"]["soft_beta_rows"].values())
    assert rge["structural_matching_results_retained_from_V36_visible_sector"]["complete_vectorlike_threshold_sum_Delta_b_1_2_3"] == [4, 4, 4]


def test_driver_dressed_baryon_operators_are_allowed_and_prevent_a_lifetime_claim() -> None:
    proton = REPORT["G7_proton_and_flavour_boundary"]
    selection = proton["selection_rule_result"]
    assert selection["bare_Q4_or_Qc4_is_forbidden_in_W"] is True
    allowed = selection["driver_dressed_degree5_sources_are_permitted"]
    assert [row["source_monomial"] for row in allowed] == [
        "X*Q^4/M^2",
        "X*Qc^4/M^2",
        "Zp*Q^4/M^2",
        "Zp*Qc^4/M^2",
    ]
    assert all(row["Z5610_charge"] == 0 for row in allowed)
    assert all(row["external_Z4R_charge_mod4"] == 2 for row in allowed)
    assert all(row["branch_value_if_X_and_Zp_zero"] == 0 for row in allowed)
    assert selection["exact_Q4_two_family_contraction_witness"] == 4
    assert len(proton["why_no_lifetime_can_be_inferred"]) == 3


def test_flavour_is_nonidentifiable_without_an_origin_or_likelihood() -> None:
    flavour = REPORT["G7_proton_and_flavour_boundary"]["flavour_nonidentifiability"]
    assert "YQQ (3x3)" in flavour["unfixed_matrix_couplings"]
    assert "yNQ (3x3)" in flavour["unfixed_matrix_couplings"]
    assert flavour["symmetry_allowed_counterexamples"] == ["YQQ=0", "YQQ=y*Identity_3 for arbitrary complex y"]
    assert "not predictions" in flavour["consequence"]


def test_all_audited_full_gates_remain_open() -> None:
    gates = REPORT["G2_G4_G6_G8_gate_conclusions"]
    assert [row["gate"] for row in gates] == ["G2", "G3", "G4", "G6", "G7", "G8"]
    assert all(row["full_gate_closed"] is False for row in gates)
    assert REPORT["established_full_predictive_closed_count"] == 0
    assert REPORT["complete_theory_exists"] is False
    assert REPORT["minimal_honest_extension_contract"]["not_implemented_as_ad_hoc_new_physics"] is True


def test_exact_small_block_helpers() -> None:
    matrix = [[Fraction(2), Fraction(3)], [Fraction(5), Fraction(7)]]
    assert audit.determinant(matrix) == Fraction(-1)
    assert audit.rank(matrix) == 2


def test_report_hash_and_generated_outputs_replay() -> None:
    assert REPORT["core_sha256"] == audit.canonical_sha(REPORT)
    assert all(len(row["sha256"]) == 64 for row in REPORT["source_manifest"])

    if audit.OUTPUT_JSON.is_file() and audit.OUTPUT_MD.is_file():
        stored = json.loads(audit.OUTPUT_JSON.read_text(encoding="utf-8"))
        assert stored == REPORT
        assert stored["core_sha256"] in audit.OUTPUT_MD.read_text(encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-B", str(audit.ROOT / "susy_v37_nonanomaly_gate_audit.py"), "--check"],
        cwd=audit.ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "V37_NONANOMALY_AUDIT_CHECK PASS" in result.stdout
