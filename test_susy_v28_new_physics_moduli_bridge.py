from __future__ import annotations

import json
import subprocess
import sys

import susy_v28_new_physics_moduli_bridge as bridge


def test_upstream_pins_and_cores_match() -> None:
    report = bridge.build_report()
    assert report["checks"]["all_raw_source_pins_match"] is True
    assert report["checks"]["V26_core_matches"] is True
    assert report["checks"]["V27_core_matches"] is True


def test_microscopic_target_exposes_exact_moduli_gap() -> None:
    target = bridge.build_report()["microscopic_target"]
    assert target["Hodge_numbers"] == {"h11": 51, "h21": 3}
    assert target["closed_complex_moduli_total"] == 55
    assert target["G3_tree_level_stabilized_complex_moduli"] == 4
    assert target["ambient_Kahler_sector_h11"] == 51
    assert target["explicit_untwisted_N1_Kahler_chiral_multiplets"] == 3
    assert target["complete_twisted_N1_orientifold_parity_inventory_published"] is False
    assert target["G3_tree_level_unstabilized_Kahler_sector_envelope"] == 51
    assert target["conservative_V26_to_ambient_h11_dimension_gap"] == 50
    assert target["direct_one_field_bijection_to_ambient_h11_possible"] is False


def test_double_root_racetrack_identity_is_exact() -> None:
    scaffold = bridge.build_report()["exact_51_modulus_racetrack_scaffold"]
    assert scaffold["polynomial_coefficients"] == [1, -2, 1]
    assert scaffold["polynomial_powers"] == [1, 3, 5]
    assert scaffold["p_at_y1"] == 0
    assert scaffold["Euler_p_at_y1"] == 0
    assert scaffold["Euler_squared_p_at_y1"] == 8
    assert scaffold["W_at_stationary_point"] == 0


def test_all_51_complex_and_102_real_modulus_directions_are_locally_massive() -> None:
    scaffold = bridge.build_report()["exact_51_modulus_racetrack_scaffold"]
    assert scaffold["number_of_complex_moduli"] == 51
    assert scaffold["exponential_terms_required"] == 153
    assert scaffold["W_ii_over_pi2_Ciqi5"] == 3872
    assert scaffold["holomorphic_Hessian_rank"] == 51
    assert scaffold["real_scalar_Hessian_rank"] == 102
    assert scaffold["all_102_real_modulus_components_locally_massive"] is True


def test_v26_is_exactly_recovered_as_one_field_special_case() -> None:
    recovery = bridge.build_report()["exact_51_modulus_racetrack_scaffold"][
        "recovers_V26_at_q_half_and_C_32M3"
    ]
    assert recovery["three_coefficients_in_M3_units"] == [2, -16, 32]
    assert recovery["term_values_at_stationary_point_in_M3_units"] == [1, -2, 1]
    assert recovery["W_TT_over_pi2_M3"] == 3872


def test_new_physics_is_qualified_without_false_microscopic_promotion() -> None:
    report = bridge.build_report()
    result = report["new_physics_result"]
    assert result["local_51_complex_modulus_stabilization_problem_solved"] is True
    assert result["microscopic_divisor_and_instanton_realization_derived"] is False
    assert result["direct_match_to_2026_rigid_brane_model"] is False
    assert report["G1_gate"]["qualified_local_multimodulus_subgate_closed"] is True
    assert report["G1_gate"]["closed"] is False
    assert report["G1_gate"]["full_gate_claim"] is False
    requirements = report["microscopic_bridge_requirements"]
    assert len(requirements) == len({row["id"] for row in requirements}) == 7


def test_bridge_schema_and_frozen_outputs() -> None:
    report = bridge.build_report()
    schema = bridge.bridge_schema()
    inventory = schema["properties"]["moduli_inventory"]
    assert inventory["minItems"] == inventory["maxItems"] == 51
    assert "orientifold_parity_split_sha256" in schema["required"]
    hessian = schema["properties"]["vacuum_hessian"]["properties"]
    assert hessian["complex_rank"]["const"] == 51
    assert hessian["real_rank"]["const"] == 102
    assert report["n_failed"] == 0, report["failures"]
    assert bridge.canonical_sha(report) == report["core_sha256"]
    assert bridge.check_outputs(report) is True
    frozen_schema = json.loads(bridge.SCHEMA_PATH.read_text(encoding="utf-8"))
    assert frozen_schema == schema
    completed = subprocess.run(
        [sys.executable, "-B", str(bridge.ROOT / "susy_v28_new_physics_moduli_bridge.py"), "--check"],
        cwd=bridge.ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
