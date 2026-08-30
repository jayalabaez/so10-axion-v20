from __future__ import annotations

import json
import math
import subprocess
import sys
from fractions import Fraction

import susy_v37_new_physics_routes as v37


REPORT = v37.build_report()
QUALITY = REPORT["quality"]
GATES = REPORT["gate_ledger"]
MODEL_SOURCE = (
    v37.ROOT / "models" / v37.MODEL_NAME / f"{v37.MODEL_NAME}.m"
).read_text(encoding="utf-8")


def determinant(matrix: list[list[Fraction]]) -> Fraction:
    work = [row[:] for row in matrix]
    result = Fraction(1)
    for column in range(len(work)):
        pivot = next(row for row in range(column, len(work)) if work[row][column])
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result *= -1
        value = work[column][column]
        result *= value
        work[column] = [entry / value for entry in work[column]]
        for row in range(column + 1, len(work)):
            factor = work[row][column]
            work[row] = [
                left - factor * right
                for left, right in zip(work[row], work[column], strict=True)
            ]
    return result


def test_z5610_combines_z66_and_z85_with_frozen_field_charges() -> None:
    assert math.gcd(v37.N66, v37.N85) == 1
    assert v37.N5610 == v37.N66 * v37.N85 == 5610
    expected = {
        "X": 0,
        "Zp": 0,
        "P": 170,
        "Pbar": 5440,
        "Nv": 0,
        "A2": 3211,
        "A32": 2569,
        "A15": 4299,
        "A17": 1141,
        "A16": 5525,
    }
    assert {
        name: v37.combined_charge(q66, h85)
        for name, (q66, _r4, h85, _pq170) in v37.SINGLET_FIELDS.items()
    } == expected

    for term in v37.RETAINED_ANOMALON_TERMS:
        assert sum(expected[name] for name in term) % v37.N5610 == 0
        assert v37.term_charge(term, 1) % 4 == 2
        assert v37.term_charge(term, 3) == 0


def test_exact_combined_finite_anomalies_and_spectator_checks_pass() -> None:
    selector = QUALITY["selector"]
    breaking = selector["spontaneous_breaking_by_P_and_Pbar"]
    assert breaking["P_q5610"] == 170
    assert breaking["Pbar_q5610"] == 5440
    assert breaking["unbroken_subgroup_order"] == 170
    assert breaking["unbroken_subgroup"] == "Z170 ~= Z2 x Z85"
    assert selector["Z85_linear_sum"] == 0
    assert selector["Z85_cubic_sum"] == 0
    assert selector["69_squared_mod85"] == 1
    assert selector["mixed_Z4R_Z85_squared_integer"] == 9520
    assert selector["mixed_Z4R_Z85_squared_mod85"] == 0

    finite = selector["combined_Hsieh_Dai_Freed"]
    assert finite["order"] == 5610
    assert finite["Delta_s1_canonical"] == 109395
    assert finite["Delta_s3_canonical"] == 3036473977185
    assert finite["linear_condition_2Delta_s1_mod_n"] == 0
    assert finite["cubic_condition_mod_6n"] == 0
    assert finite["both_vanish"] is True


def test_complete_renormalizable_singlet_census_preserves_pq() -> None:
    census = QUALITY["renormalizable_census"]
    assert census["scope"] == "all gauge-singlet monomials of superfield degree <=3"
    assert census["allowed_count"] == 12
    assert {tuple(term) for term in census["allowed"]} == {
        ("X",),
        ("Zp",),
        ("Nv", "Nv"),
        ("X", "X", "X"),
        ("X", "X", "Zp"),
        ("X", "Zp", "Zp"),
        ("X", "P", "Pbar"),
        ("Zp", "Zp", "Zp"),
        ("Zp", "P", "Pbar"),
        ("P", "A15", "A17"),
        ("P", "A16", "A16"),
        ("Pbar", "A2", "A32"),
    }
    assert census["all_preserve_optimized_PQ"] is True
    assert census["retained_anomalon_terms_present"] is True
    assert census["removed_v36_terms_forbidden"] is True
    assert ["A17", "A16"] not in census["allowed"]
    assert census["dangerous_P_A32_forbidden"] is True


def test_three_anomalon_mass_terms_have_full_rank_determinant() -> None:
    mass = QUALITY["minimal_anomalon_mass"]
    assert mass["retained_terms"] == [
        ["Pbar", "A2", "A32"],
        ["P", "A15", "A17"],
        ["P", "A16", "A16"],
    ]
    assert mass["removed_redundant_v36_terms"] == [
        ["Pbar", "A17", "A17"],
        ["A16", "A17"],
    ]
    assert mass["field_order"] == ["A2", "A32", "A15", "A17", "A16"]
    assert mass["determinant"] == "a^2*b^2*c"
    assert mass["full_rank_condition"] == "a*b*c != 0"

    a, b, c = map(Fraction, (2, 3, 5))
    matrix = [
        [0, a, 0, 0, 0],
        [a, 0, 0, 0, 0],
        [0, 0, 0, b, 0],
        [0, 0, b, 0, 0],
        [0, 0, 0, 0, c],
    ]
    assert determinant([[Fraction(value) for value in row] for row in matrix]) == a**2 * b**2 * c


def test_complete_w_ring_first_breaks_pq_at_degree_33() -> None:
    ring = QUALITY["complete_superpotential_ring"]
    assert ring["search_max_degree"] == 33
    assert ring["first_breaking_degree"] == 33
    assert ring["witness_multiplicities"] == {"P": 33}
    assert ring["witness_PQ_charge"] == "5610/170"
    assert len(ring["reachable_state_counts"]) == 33

    benchmark = QUALITY["benchmark_unit_coefficient_W_degree33"]
    assert benchmark["passes_abs_theta_below_1e-10"] is True
    assert benchmark["log10_abs_theta"] < -160


def test_conservative_kahler_ring_first_breaks_pq_at_degree_32() -> None:
    ring = QUALITY["conservative_kahler_ring"]
    assert ring["search_max_degree"] == 33
    assert ring["first_breaking_degree"] == 32
    assert ring["witness_multiplicities"] == {
        "P": 6,
        "A32": 21,
        "A17dag": 4,
        "A16dag": 1,
    }
    assert ring["witness_PQ_charge"] == "5610/170"
    assert len(ring["reachable_state_counts"]) == 32
    assert QUALITY["promotion_boundary"]["quality_gate_closed"] is False


def test_all_twenty_chiral_charge_lattice_has_no_lower_degree_loophole() -> None:
    audit = QUALITY["all_chiral_charge_lattice_lower_bound"]
    assert "all 20 chiral species" in audit["scope"]
    assert audit["superpotential"]["first_breaking_degree"] == 33
    assert audit["kahler_with_conjugates"]["first_breaking_degree"] == 32
    assert audit["same_first_degrees_as_singlet_witnesses"] is True
    assert audit["analytic_PQ_congruence_holds_for_all_fields"] is True
    assert set(audit["analytic_PQ_congruence_residues"]) == set(v37.ALL_CHIRAL_FIELDS)
    assert set(audit["analytic_PQ_congruence_residues"].values()) == {0}


def test_pq_neutral_b_route_is_rejected_by_fatal_allowed_operator() -> None:
    route = REPORT["rejected_PQ_neutral_anomaly_higgs"]
    assert route["finite_increment"]["both_vanish"] is True
    assert route["mixed_PS_squared_Z66_increment_half_normalized"] == [4, 4, 4]
    assert route["cancels_v36_mixed_residue"] is True
    assert route["QCD_PQ_anomaly_unchanged_at_renormalizable_level"] is True
    assert route["Delta_b_4_L_R"] == [4, 4, 4]
    assert min(route["pole_ratios"]) > 100

    fatal = route["fatal_allowed_operator"]
    assert fatal["operator"] == "Pbar^2 * Bbar * F16 * F16bar / M^2"
    assert fatal["superfield_degree"] == 5
    assert fatal["Z66_charge_mod66"] == 0
    assert fatal["Z4R_charge_mod4"] == 2
    assert fatal["PQ_charge_QP_equals_1"] == -2
    assert fatal["log10_abs_theta_at_v36_benchmark"] > 20
    assert fatal["log10_abs_theta_if_vB_equals_vPS"] > fatal["log10_abs_theta_at_v36_benchmark"]
    assert route["verdict"].startswith("rejected")

    origin = REPORT["alternative_routes"]["gauged_U1H_to_Z85_origin"]
    assert origin["continuous_gravitational_and_cubic_anomalies_pairwise_zero"] is True
    assert origin["continuous_Z4R_U1H_squared_residue_before_heavy_UV_completion"] == 9520
    assert origin["large_charge_sum_q_squared_including_Higgs_pair"] == 23974
    assert "needs" in origin["status"]


def test_gate_ledger_remains_honest_zero_of_eight() -> None:
    assert GATES["complete_theory_exists"] is False
    assert GATES["established_full_predictive_closed_count"] == 0
    assert GATES["materially_updated_frontiers"] == ["G1", "G5"]
    assert [row["gate"] for row in GATES["gates"]] == [f"G{i}" for i in range(1, 9)]
    assert all(row["closed"] is False for row in GATES["gates"])
    g1 = GATES["gates"][0]
    g5 = GATES["gates"][4]
    assert "UV_OPEN" in g1["state"]
    assert "DEGREE33" in g5["state"] and "DEGREE32" in g5["state"]


def test_sarah_source_contains_only_the_retained_anomalon_mass_terms() -> None:
    assert 'Model`Name = "PSZ4RZ5610SUSYV37";' in MODEL_SOURCE
    assert "Global[[1]] = {Z[5610], Z5610Selector};" in MODEL_SOURCE
    assert MODEL_SOURCE.count("SuperFields[[") == 20
    for symbol, charge in {
        "P": 170,
        "Pb": 5440,
        "A2": 3211,
        "A32": 2569,
        "A15": 4299,
        "A17": 1141,
        "A16": 5525,
    }.items():
        assert f"SuperFields" in MODEL_SOURCE
        assert f"Z5610q{charge}" in MODEL_SOURCE

    assert "+ yAbar*Pb.A2.A32" in MODEL_SOURCE
    assert "+ yA15*P.A15.A17" in MODEL_SOURCE
    assert "+ yA16/2*P.A16.A16" in MODEL_SOURCE
    assert "yA17" not in MODEL_SOURCE
    assert "MA*A16.A17" not in MODEL_SOURCE
    assert "AddSoftTerms = False;" in MODEL_SOURCE


def test_live_sarah_two_loop_rge_attestation_is_current() -> None:
    rge = REPORT["live_SARAH_RGE_attestation"]
    assert rge is not None
    assert rge["model"] == v37.MODEL_NAME
    assert rge["tool"] == "SARAH 4.15.3"
    assert rge["model_initialized"] is True
    assert rge["two_loop_RGE_calculation_succeeded"] is True
    assert rge["source_soft_terms_enabled"] is False
    assert rge["beta_counts"] == {
        "gauge": 3,
        "trilinear_superpotential": 27,
        "bilinear_superpotential": 1,
        "linear_superpotential": 3,
        "soft_trilinear": 0,
        "soft_bilinear": 0,
        "soft_linear": 0,
        "soft_scalar_mass": 0,
        "gaugino_mass": 0,
    }
    assert len(rge["beta_gauge_input_form"]) == 3
    assert len(rge["beta_superpotential_input_form"]) == 31


def test_report_core_hash_and_generated_outputs_are_self_consistent() -> None:
    assert len(REPORT["core_sha256"]) == 64
    assert REPORT["core_sha256"] == v37.canonical_sha(REPORT)
    assert REPORT["required_sources_all_present"] is True
    assert REPORT["required_sources_missing"] == []
    assert all(row["exists"] and len(row["sha256"]) == 64 for row in REPORT["source_manifest"])

    if v37.REPORT_JSON.is_file():
        stored = json.loads(v37.REPORT_JSON.read_text(encoding="utf-8"))
        assert stored["core_sha256"] == v37.canonical_sha(stored)
        assert stored["schema"] == REPORT["schema"]
        assert stored["model"] == REPORT["model"]
        assert json.loads(v37.QUALITY_JSON.read_text(encoding="utf-8")) == stored["quality"]
        assert json.loads(v37.GATES_JSON.read_text(encoding="utf-8")) == stored["gate_ledger"]
        assert stored["core_sha256"] in v37.REPORT_MD.read_text(encoding="utf-8")


def test_generated_campaign_replays_exactly() -> None:
    result = subprocess.run(
        [sys.executable, "-B", str(v37.ROOT / "susy_v37_new_physics_routes.py"), "--check"],
        cwd=v37.ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "V37_NEW_PHYSICS_CHECK PASS" in result.stdout
