from __future__ import annotations

import json
import subprocess
import sys
from fractions import Fraction

import numpy as np

import susy_v35_component_betay_campaign as v35


BASIS_PAYLOAD = v35.read_json(v35.BASIS_JSON)
MODEL = v35.ComponentModel(BASIS_PAYLOAD)
REPORT, EVIDENCE = v35.build_bundle()
G6 = EVIDENCE[v35.G6_JSON.name]
FORENSIC = EVIDENCE[v35.FORENSIC_JSON.name]
GATES = EVIDENCE[v35.GATES_JSON.name]


def parse_fraction(value: int | str) -> Fraction:
    return Fraction(value)


def test_live_sarah_tensor_capture_is_complete_and_hashed() -> None:
    assert BASIS_PAYLOAD["engine"].startswith("15.0.1")
    assert BASIS_PAYLOAD["tool"] == "SARAH 4.15.3"
    assert BASIS_PAYLOAD["model"] == "PSZ4RZ33SUSYV33"
    assert BASIS_PAYLOAD["extraction_passed"] is True
    assert BASIS_PAYLOAD["extraction_errors"] == []
    assert BASIS_PAYLOAD["visible_complex_chiral_component_count"] == 111
    assert BASIS_PAYLOAD["dimensionless_coupling_component_count"] == 42
    assert BASIS_PAYLOAD["sparse_tensor_entry_count"] == 2719
    assert BASIS_PAYLOAD["listWtriOne_count"] == 16
    assert BASIS_PAYLOAD["listWtri_count"] == 79
    assert all(
        len(BASIS_PAYLOAD[key]) == 64
        for key in (
            "Yijk_downvalues_sha256",
            "InvMat_subvalues_sha256",
            "epsTensor_downvalues_sha256",
            "listWtriOne_sha256",
            "listWtri_sha256",
        )
    )
    assert "InvMat[1]" in BASIS_PAYLOAD["SA_NonZeroEntries_input_form"]
    assert "InvMat[2]" in BASIS_PAYLOAD["SA_NonZeroEntries_input_form"]
    assert "InvMat[3]" in BASIS_PAYLOAD["SA_NonZeroEntries_input_form"]
    assert BASIS_PAYLOAD["InvMat3_6x6_input_form"]


def test_sparse_basis_is_symmetric_orthogonal_and_rank_42() -> None:
    coordinates = list(zip(MODEL.i, MODEL.j, MODEL.k, strict=True))
    assert len(coordinates) == len(set(coordinates)) == 2719
    gram = MODEL.full_gram()
    assert gram.shape == (42, 42)
    assert np.max(np.abs(gram - np.diag(np.diag(gram)))) == 0.0
    assert np.linalg.matrix_rank(gram) == 42
    assert np.linalg.cond(gram) == 24.0
    assert np.allclose(np.diag(gram).real, MODEL.gram_diagonal, rtol=0.0, atol=1e-13)

    values = np.asarray(
        [0.01 * (index + 1) + 0.002j * (index % 4) for index in range(42)]
    )
    y = MODEL.dense_y(values)
    for permutation in (
        (0, 1, 2),
        (0, 2, 1),
        (1, 0, 2),
        (1, 2, 0),
        (2, 0, 1),
        (2, 1, 0),
    ):
        assert np.max(np.abs(y - y.transpose(permutation))) == 0.0
    assert np.allclose(MODEL.project(y), values, rtol=0.0, atol=3e-15)


def test_component_casimirs_reconstruct_group_metadata() -> None:
    metadata = G6["group_metadata"]
    assert metadata["group_order"] == ["SU4", "SU2L", "SU2R"]
    assert metadata["adjoint_Casimirs"] == [4, 2, 2]
    assert metadata["Dynkin_sums_reconstructed_from_111_components"] == [13, 11, 15]
    assert metadata["match"] is True
    assert metadata["component_Casimir_reference"]["Q"] == ["15/8", "3/4", 0]
    assert metadata["component_Casimir_reference"]["Sig6"] == ["5/2", 0, 0]
    assert metadata["component_Casimir_reference"]["H"] == [0, "3/4", "3/4"]


def test_exact_one_loop_gauge_coefficients_for_all_parameter_classes() -> None:
    grouped = G6["exact_gauge_coefficients"]["grouped_by_parameter"]
    expected = {
        "lambdaPX": ["-15/2", -3, 0],
        "lambdaPQ": ["-15/2", -3, 0],
        "lambdaPcX": ["-15/2", 0, -3],
        "lambdaPcQ": ["-15/2", 0, -3],
        "yNX": ["-15/2", 0, -3],
        "yNQ": ["-15/2", 0, -3],
        "kappaPS": ["-15/2", 0, -3],
        "YXX": ["-15/2", -3, -3],
        "YXQ": ["-15/2", -3, -3],
        "YQX": ["-15/2", -3, -3],
        "YQQ": ["-15/2", -3, -3],
        "lambdaSb": ["-25/2", 0, -3],
        "lambdaS": ["-25/2", 0, -3],
        "lambdaH": [0, -3, -3],
        "lambdaSigma": [-10, 0, 0],
        "kappaX": [0, 0, 0],
    }
    assert set(grouped) == set(expected)
    for parameter, coefficients in expected.items():
        assert grouped[parameter]["one_loop_g_squared_4_L_R"] == coefficients

    values, gauges = v35.deterministic_complex_point(MODEL)
    y = MODEL.dense_y(values)
    gamma_g, _, _ = v35.anomalous_dimensions(y, gauges, MODEL.casimirs)
    gamma_0, _, _ = v35.anomalous_dimensions(y, (0.0, 0.0, 0.0), MODEL.casimirs)
    numeric = MODEL.project(v35.beta_tensor(y, gamma_g - gamma_0))
    expected_numeric = np.asarray(
        [
            values[index]
            * sum(
                float(parse_fraction(coefficient)) * gauge**2
                for coefficient, gauge in zip(
                    grouped[row["parameter"]]["one_loop_g_squared_4_L_R"],
                    gauges,
                    strict=True,
                )
            )
            for index, row in enumerate(MODEL.basis_rows)
        ]
    )
    assert np.allclose(numeric, expected_numeric, rtol=2e-14, atol=2e-15)


def test_exact_two_loop_pure_gauge_polynomials_replay_component_tensor() -> None:
    values, gauges = v35.deterministic_complex_point(MODEL)
    y = MODEL.dense_y(values)
    zero_y = np.zeros_like(y)
    _, _, pieces = v35.anomalous_dimensions(zero_y, gauges, MODEL.casimirs)
    pure_tensor = v35.beta_tensor(y, np.diag(pieces["pure_gauge_diagonal"]))
    numeric = MODEL.project(pure_tensor)
    grouped = G6["exact_gauge_coefficients"]["grouped_by_parameter"]
    monomial_values = {
        "g4^4": gauges[0] ** 4,
        "gL^4": gauges[1] ** 4,
        "gR^4": gauges[2] ** 4,
        "g4^2*gL^2": gauges[0] ** 2 * gauges[1] ** 2,
        "g4^2*gR^2": gauges[0] ** 2 * gauges[2] ** 2,
        "gL^2*gR^2": gauges[1] ** 2 * gauges[2] ** 2,
    }
    expected = []
    for index, row in enumerate(MODEL.basis_rows):
        polynomial = grouped[row["parameter"]]["two_loop_pure_gauge"]
        expected.append(
            values[index]
            * sum(
                float(parse_fraction(polynomial[monomial])) * value
                for monomial, value in monomial_values.items()
            )
        )
    assert np.allclose(numeric, expected, rtol=2e-14, atol=2e-15)


def test_component_gauge_beta_recovers_all_v34_yukawa_vectors() -> None:
    gauge = G6["component_gauge_beta"]
    grouped = gauge["Yukawa_subtraction_coefficients"]["grouped_by_parameter"]
    expected = {
        "kappaPS": [4, 0, 8], "lambdaH": [0, 2, 2],
        "lambdaSigma": [2, 0, 0], "lambdaS": [5, 0, 6],
        "lambdaSb": [5, 0, 6], "YQQ": [8, 16, 16],
        "YQX": [8, 16, 16], "YXQ": [8, 16, 16],
        "YXX": [8, 16, 16], "lambdaPQ": [4, 8, 0],
        "lambdaPX": [4, 8, 0], "lambdaPcQ": [4, 0, 8],
        "lambdaPcX": [4, 0, 8], "yNQ": [4, 0, 8],
        "yNX": [4, 0, 8], "kappaX": [0, 0, 0],
    }
    assert {key: value["coefficient_4_L_R"] for key, value in grouped.items()} == expected
    assert gauge["one_loop_b"] == [1, 5, 9]
    assert gauge["two_loop_B"] == [[108, 15, 21], [75, 53, 3], [105, 3, 81]]
    assert gauge["coefficient_replay_residual"] < 1e-12
    assert np.allclose(
        gauge["audit_point_Yukawa_subtraction_4_L_R"],
        gauge["audit_point_coefficient_replay_4_L_R"],
        rtol=0.0,
        atol=1e-12,
    )


def test_dimensionful_MN_and_linear_betas_close_their_declared_support() -> None:
    sector = G6["dimensionful_MN_and_linear_sector"]
    assert sector["MN_independent_complex_component_count"] == 6
    assert len(sector["MN_symmetric_component_rows"]) == 6
    assert sector["component_projection_complete"] is True
    assert sector["MN_beta1_outside_support"] == 0.0
    assert sector["MN_beta2_outside_support"] == 0.0
    assert sector["xi_beta1_outside_support"] == 0.0
    assert sector["xi_beta2_outside_support"] == 0.0
    assert sector["linear_parameter_definition"].startswith("xi_X=-kappaPS*vPS2")


def test_coupled_dimensionless_engine_replays_and_zero_yukawa_limit() -> None:
    integration = G6["conditional_coupled_dimensionless_integration"]
    assert integration["is_physical_boundary"] is False
    assert integration["state_dimension"] == 45
    assert integration["real_gauge_components"] == 3
    assert integration["complex_trilinear_components"] == 42
    assert integration["scale_ratio"] == 10.0
    assert integration["RK4_steps"] == 4
    assert integration["forward_then_backward_maximum_residual"] < 1e-10
    assert integration["replay_passes_1e-10"] is True
    assert integration["conditional_dimensionless_ODE_integration_complete"] is True

    gauges = np.asarray([0.52, 0.41, 0.39])
    state = np.concatenate([gauges.astype(complex), np.zeros(42, dtype=complex)])
    rhs = v35.coupled_dimensionless_rhs(MODEL, state)
    loop = 16.0 * np.pi**2
    expected_gauge = (
        gauges**3 * v35.GAUGE_B / loop
        + gauges**3 * (v35.GAUGE_B2 @ (gauges * gauges)) / loop**2
    )
    assert np.allclose(rhs[:3], expected_gauge, rtol=2e-14, atol=2e-15)
    assert np.max(np.abs(rhs[3:])) == 0.0


def test_exact_kappaX_one_and_two_loop_anchors() -> None:
    anchors = G6["exact_kappaX_anchors"]
    assert anchors["all_match_1e-13"] is True
    assert anchors["kappaX_only_numeric_beta1"] == anchors["kappaX_only_expected_beta1"]
    assert anchors["kappaX_only_numeric_beta2"] == anchors["kappaX_only_expected_beta2"]
    assert anchors["general_numeric_beta1"] == anchors["general_expected_beta1"]
    assert anchors["one_loop_formula"] == "6*kappaX*|kappaX|^2"
    assert anchors["two_loop_kappaX_only_formula"] == "-24*kappaX*|kappaX|^4"


def test_full_complex_two_loop_projection_and_tensor_properties() -> None:
    values, gauges = v35.deterministic_complex_point(MODEL)
    evaluated = v35.evaluate_component_betas(MODEL, values, gauges)
    assert evaluated["absolute_residual1"] < 1e-11
    assert evaluated["absolute_residual2"] < 1e-11
    assert evaluated["relative_residual1"] < 1e-11
    assert evaluated["relative_residual2"] < 1e-11
    assert np.max(
        np.abs(evaluated["gamma1"] - evaluated["gamma1"].conjugate().T)
    ) < 1e-12
    assert np.max(
        np.abs(evaluated["gamma2"] - evaluated["gamma2"].conjugate().T)
    ) < 1e-12
    for tensor in (evaluated["tensor1"], evaluated["tensor2"]):
        assert np.max(np.abs(tensor - tensor.transpose(1, 0, 2))) < 1e-12
        assert np.max(np.abs(tensor - tensor.transpose(2, 1, 0))) < 1e-12


def test_optimized_quartic_contraction_matches_literal_formula() -> None:
    rng = np.random.default_rng(35042)
    raw = rng.normal(size=(3, 3, 3)) + 1j * rng.normal(size=(3, 3, 3))
    y = sum(raw.transpose(permutation) for permutation in (
        (0, 1, 2), (0, 2, 1), (1, 0, 2),
        (1, 2, 0), (2, 0, 1), (2, 1, 0),
    )) / 6.0
    _, _, pieces = v35.anomalous_dimensions(
        y, (0.0,), np.zeros((3, 1)), total_dynkin=(0.0,), adjoint_casimirs=(0.0,)
    )
    literal = -0.5 * np.einsum(
        "iwx,xyz,yzr,wrj->ij",
        y.conjugate(),
        y,
        y.conjugate(),
        y,
        optimize=True,
    )
    assert np.allclose(pieces["quartic"], literal, rtol=2e-14, atol=2e-14)


def test_frozen_v33_payload_is_rejected_by_exact_forensics() -> None:
    assert FORENSIC["sector_boundaries"] == {
        "trilinear": 16,
        "bilinear": 1,
        "linear": 1,
        "total": 18,
    }
    assert FORENSIC["unresolved_epsTensor_counts"] == {
        "one_loop": 447,
        "two_loop": 9416,
        "total": 9863,
    }
    assert FORENSIC["distinct_epsTensor_argument_patterns_independent_audit"] == 14
    assert FORENSIC["duplicate_parameter_heads_without_sector_key"] == ["kappaPS"]
    assert FORENSIC["PrepareRGEs_remaining_epsTensor_count"] == 32945
    assert FORENSIC["one_loop_Casimir_support_failure_count"] == 13
    assert set(FORENSIC["one_loop_Casimir_support_failures"]) == {
        "lambdaPX", "lambdaPQ", "lambdaPcX", "lambdaPcQ", "YXX",
        "YXQ", "YQX", "YQQ", "yNX", "yNQ", "lambdaSb", "lambdaS",
        "kappaPS",
    }
    assert FORENSIC["linear_projection_can_create_absent_monomials"] is False
    assert FORENSIC["frozen_rows_accepted_as_ODE_system"] is False


def test_live_prepare_probe_is_diagnostic_not_false_closure() -> None:
    probe = v35.read_json(v35.PROBE_JSON)
    assert probe["BetaYijk_count"] == 16
    assert probe["prepared_equation_count"] == 42
    assert probe["PrepareRGEs_succeeded"] is True
    assert probe["raw_superpotential_sector_boundaries"] == {
        "trilinear": 16,
        "bilinear": 1,
        "linear": 1,
    }
    assert probe["raw_superpotential_unresolved_epsTensor_counts"] == {
        "one_loop": 447,
        "two_loop": 9416,
        "total": 9863,
    }
    assert probe["unresolved_symbol_counts"]["epsTensor"] == 32945
    assert probe["unresolved_symbol_counts"]["InvMat"] == 0
    assert probe["parameter_dimensions"] == {
        "lambdaPX": [1], "lambdaPcX": [1], "YXX": [1],
        "lambdaSb": [1], "lambdaS": [1], "lambdaH": [1],
        "kappaPS": [1], "lambdaSigma": [1], "kappaX": [1],
        "lambdaPQ": [3], "lambdaPcQ": [3], "YXQ": [3],
        "YQX": [3], "yNX": [3], "YQQ": [3, 3], "yNQ": [3, 3],
    }


def test_strict_gate_ledger_does_not_overclaim_completion() -> None:
    assert G6["literal_component_BetaY_projection_complete"] is True
    assert G6["all_42_dimensionless_beta_components_numerically_callable"] is True
    assert G6["component_gauge_beta_complete"] is True
    assert G6["dimensionful_MN_and_linear_beta_complete"] is True
    assert G6["conditional_coupled_gauge_Yukawa_integration_complete"] is True
    assert G6["source_derived_PS_boundary_present"] is False
    assert G6["coupled_gauge_Yukawa_soft_integration_complete"] is False
    assert G6["G6_full_predictive_closed"] is False
    assert GATES["materially_updated_frontiers"] == ["G6"]
    assert GATES["materially_updated_frontier_count"] == 1
    assert GATES["established_full_predictive_closed_count"] == 0
    assert GATES["complete_theory_exists"] is False
    assert len(GATES["gates"]) == 8
    assert all(not row["established_full_predictive_closed"] for row in GATES["gates"])
    assert REPORT["summary"]["safe_to_claim_new_fundamental_law"] is False


def test_campaign_hashes_manifests_and_frozen_outputs_replay() -> None:
    assert REPORT["core_sha256"] == v35.canonical_sha(REPORT)
    assert REPORT["upstream_V34_core_sha256"] == v35.UPSTREAM_V34_CORE
    assert all(row["exists"] and len(row["sha256"]) == 64 for row in REPORT["source_manifest"])
    for name, payload in EVIDENCE.items():
        expected = v35.hashlib.sha256(
            (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
        ).hexdigest()
        assert REPORT["evidence_sha256"][name] == expected
    assert v35.check_outputs(REPORT, EVIDENCE)


def test_cli_check_passes() -> None:
    completed = subprocess.run(
        [sys.executable, "-B", str(v35.ROOT / "susy_v35_component_betay_campaign.py"), "--check"],
        cwd=v35.ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert REPORT["core_sha256"] in completed.stdout
