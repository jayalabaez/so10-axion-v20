from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT / "susy_v47_relative_eta_bordism_audit.py"
SPEC = importlib.util.spec_from_file_location("susy_v47_relative_eta_bordism_audit", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def report():
    return MODULE.build_report()


def test_gf2_rank_exact_examples():
    assert MODULE.gf2_rank([[1, 0, 0]]) == 1
    assert MODULE.gf2_rank([[1, 0], [0, 1]]) == 2
    assert MODULE.gf2_rank([[1, 1], [1, 1]]) == 1


def test_pure_ps_outgoing_matrix_and_rank():
    cert = MODULE.ahss_certificate(False)
    assert cert["d2_out_of_E2_4_1"]["matrix_rows_H2_columns_H4"] == [[1, 0, 0]]
    assert cert["d2_out_of_E2_4_1"]["rank"] == 1
    assert cert["d2_out_of_E2_4_1"]["kernel_dimension"] == 2


def test_pure_ps_incoming_image_fills_kernel():
    cert = MODULE.ahss_certificate(False)
    assert cert["d2_into_E2_4_1"]["image_generators_in_H4_dual_basis"] == [
        [0, 1, 0],
        [0, 0, 1],
    ]
    assert cert["d2_into_E2_4_1"]["rank"] == 2
    assert cert["d2_into_E2_4_1"]["image_equals_outgoing_kernel"]


def test_pure_ps_other_total_five_entries_die():
    other = MODULE.ahss_certificate(False)["other_total_degree_five_terms"]
    assert other["d2_5_0_rank"] == 1
    assert other["d2_5_1_rank"] == 1
    assert other["E3_5_0_dimension"] == 0
    assert other["E3_3_2_dimension"] == 0


def test_pure_ps_omega5_zero():
    cert = MODULE.ahss_certificate(False)
    assert cert["E3_4_1_dimension"] == 0
    assert cert["all_total_degree_five_E3_terms_zero"]
    assert cert["Omega5Spin"] == "0"
    assert not cert["higher_differential_or_extension_room"]


def test_product_outgoing_matrix_and_rank():
    cert = MODULE.ahss_certificate(True)
    assert cert["d2_out_of_E2_4_1"]["matrix_rows_H2_columns_H4"] == [
        [1, 0, 0, 0, 0],
        [0, 0, 1, 0, 0],
    ]
    assert cert["d2_out_of_E2_4_1"]["rank"] == 2
    assert cert["d2_out_of_E2_4_1"]["kernel_dimension"] == 3


def test_product_incoming_image_fills_kernel_and_kills_mixed_direction():
    cert = MODULE.ahss_certificate(True)
    assert cert["d2_into_E2_4_1"]["image_generators_in_H4_dual_basis"] == [
        [0, 1, 0, 0, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 0, 0, 1],
    ]
    assert cert["d2_into_E2_4_1"]["rank"] == 3
    assert cert["d2_into_E2_4_1"]["image_equals_outgoing_kernel"]
    assert cert["steenrod_operations"]["Sq2_on_H4_mod_annihilator"]["x*u"] == "x^2*u+x*u^2"


def test_product_omega5_zero():
    cert = MODULE.ahss_certificate(True)
    assert cert["all_total_degree_five_E3_terms_zero"]
    assert cert["Omega5Spin"] == "0"


def test_integral_h4_lattice_is_full_mod_two():
    cert = MODULE.ahss_certificate(False)["H4_integral_lattice_for_P"]
    assert cert["all_three_H4_mod2_classes_integrally_represented"]
    assert cert["mod2_reductions"] == ["x^2", "b", "a+b+x^2"]


def test_nonliftable_bundle_is_included_and_extends_to_spin10():
    geometry = report()["group_and_bundle_geometry"]
    assert "x!=0" in geometry["bundle_description"]
    assert "x+x=0" in geometry["embedding_into_Spin10"]


def test_apparent_x_sq1x_class_is_killed():
    row = report()["apparent_quotient_torsion"]
    assert row["identity"] == "x*y=Sq2(y) because w5(V6)=0"
    assert not row["new_pure_quotient_torsion_class_exists"]


def test_spin10_u1_groups():
    row = report()["Spin10xU1F"]
    assert row["Omega5Spin"] == "0"
    assert row["Omega6Spin"] == "Z^3"
    assert row["Omega6_torsion"] == "0"
    assert len(row["Omega6_free_generators"]) == 3


def test_relative_map_is_integrally_surjective():
    row = report()["standard_interval_relative_pair"]
    witness = row["surjectivity_witness"]
    assert witness["coefficient_gcd"] == 1
    assert witness["map_Omega6_is_surjective"]
    assert row["Omega6Spin_relative"] == "0"


def test_local_polynomials_cancel_on_both_walls():
    rows = report()["actual_V46_spectrum"]["ordinary_local_anomaly_ledgers_in_V45_units"]
    assert rows["both_walls_zero"]
    assert all(value == 0 for value in rows["PS_sum"].values())
    assert all(value == 0 for value in rows["Spin10_sum"].values())


def test_actual_torsion_homomorphism_has_zero_domain():
    row = report()["actual_V46_spectrum"]["torsion_anomaly_homomorphism"]
    assert row["domain_group"] == "0"
    assert row["number_of_surviving_generators_to_evaluate"] == 0
    assert row["actual_fermion_homomorphism"] == "the unique zero homomorphism"
    assert row["nonliftable_PS_bundles_included"]


def test_parity_free_levels_remain_quantized():
    row = report()["actual_V46_spectrum"]["five_dimensional_parity_levels"]
    assert row["every_individual_shift_in_closed_spin_U1_lattice"]
    assert row["common_orientation_net_zero"]
    assert all(value == 0 for value in row["common_orientation_totals"].values())


def test_residual_z6_is_zero_by_naturality_not_group_vanishing_claim():
    row = report()["residual_Z6_mixing"]
    assert row["all_Z6_bundles_extend_structure_group_to_PxU1F"]
    assert row["parent_continuous_anomaly_class"] == "0"
    assert row["pulled_back_Z6_class"] == "0"
    assert "does not claim Omega5Spin" in row["important_scope"]


def test_anomaly_class_closed_but_absolute_phase_not_computed():
    row = report()["APS_eta_conclusion"]
    assert row["gauge_anomaly_obstruction"] == "CANCELLED"
    assert row["existence_of_gauge_invariant_Dai_Freed_trivialization"]
    assert not row["absolute_exponentiated_eta_value_computed"]
    assert row["absolute_phase_not_an_anomaly"]


def test_g1_promoted_but_theory_not_complete():
    decision = report()["decision"]
    assert decision["G1_promoted"] and decision["G1_closed"]
    assert not decision["absolute_KK_eta_phase_required_for_gauge_consistency"]
    assert decision["G2_through_G8_open"]
    assert not decision["theory_complete"]


def test_v47_canonical_core_hash_excludes_only_self_field():
    fresh = report()
    assert fresh["core_sha256"] == MODULE.canonical_sha(fresh)
    same_body = dict(fresh)
    same_body["core_sha256"] = "0" * 64
    assert MODULE.canonical_sha(same_body) == fresh["core_sha256"]
    changed_body = dict(fresh)
    changed_body["status"] = fresh["status"] + "_TAMPERED"
    assert MODULE.canonical_sha(changed_body) != fresh["core_sha256"]


def test_all_four_upstream_embedded_core_hashes_validate():
    fresh = report()
    assert fresh["upstream_core_hashes_validated"]
    assert set(fresh["input_core_sha256"]) == set(MODULE.INPUTS)
    for name, path in MODULE.INPUTS.items():
        payload = MODULE.load_validated_json(path)
        assert payload["core_sha256"] == MODULE.canonical_sha(payload)
        assert fresh["input_core_sha256"][name] == payload["core_sha256"]


def test_written_json_matches_fresh_report():
    written = json.loads(MODULE.JSON_PATH.read_text(encoding="utf-8"))
    assert written == report()
    assert written["core_sha256"] == MODULE.canonical_sha(written)


def test_written_markdown_matches_fresh_render():
    fresh = report()
    assert MODULE.MD_PATH.read_text(encoding="utf-8") == MODULE.render_markdown(fresh)
