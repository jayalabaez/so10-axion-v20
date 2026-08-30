import json

import exact_eft_g6_g7_parameterized_matching_v20 as theorem


def test_parameterized_matching_core_and_census():
    report = theorem.build_report()
    assert report["core_sha256"] == theorem.EXPECTED_CORE_SHA256
    threshold = report["exact_residual_scalar_thresholds"]
    assert threshold["exact_parameterized_result"]["B3"] == "41/2"
    assert threshold["exact_parameterized_result"]["B89"] == "40"
    assert sum(row["massive_real_dimension"] for row in threshold["sector_data"]) == 448
    assert sum(row["zero_real_dimension_excluded"] for row in threshold["sector_data"]) == 38


def test_vieta_and_companion_root_implementations_agree():
    comparison = theorem.build_report()["exact_residual_scalar_thresholds"][
        "independent_implementation_comparison"
    ]
    assert comparison["agreement"]
    assert comparison["maximum_sector_log_determinant_difference"] < 1.0e-12


def test_scale_wilson_degeneracy_and_pole_boundary_are_explicit():
    report = theorem.build_report()
    nonidentifiability = report["dimensionful_EFT_family"]["nonidentifiability_proof"]
    assert not nonidentifiability["M0_solvable_from_frozen_G6"]
    assert not nonidentifiability["Wilson_coefficient_or_cutoff_separately_solvable"]
    assert report["dimensionful_EFT_family"]["dimension_six_matching"][
        "frozen_dimensionless_coefficient"
    ] == "C6*M0^2=1/20"
    assert not report["loop_and_pole_mass_boundary"]["pole_masses_identified"]
    assert not report["classification"]["positive_G7_closed"]


def test_frozen_electromagnetic_label_is_exactly_refuted():
    report = theorem.build_report()
    audit = report["physical_stabilizer_audit"]
    assert audit["actual_source_generator"] == "G_(8,9)"
    assert not audit["G89_equals_standard_electromagnetism"]
    assert audit["bare_G89_exact_vacuum_action"]["Delta_R"][
        "nonzero_integer_coordinates"
    ] == 0
    assert audit["three_Q_standard"] == "3 Q_std=3 G67-(G01+G23+G45)"
    assert audit["three_Q_standard_exact_vacuum_action"]["H"] == {
        "nonzero_integer_coordinates": 2,
        "integer_squared_norm": 18,
    }
    assert audit["three_Q_standard_exact_vacuum_action"]["Delta_R"] == {
        "nonzero_integer_coordinates": 8,
        "integer_squared_norm": 72,
    }
    assert audit["selected_full_target_tangent"] == {
        "nonzero_integer_coordinates": 10,
        "integer_squared_norm": 90,
    }
    assert not audit["physical_U1em_sector_labels_valid"]
    threshold = report["exact_residual_scalar_thresholds"]
    assert threshold["interpretation_guard"]["abelian_generator"] == "G_(8,9)"
    assert not threshold["interpretation_guard"][
        "physical_electromagnetic_interpretation_allowed"
    ]
    assert "L89(mu)" in threshold["exact_parameterized_result"]
    assert "Lem(mu)" not in threshold["exact_parameterized_result"]


def test_rendered_reports_are_frozen():
    report = theorem.build_report()
    assert json.loads(theorem.OUT_JSON.read_text(encoding="utf-8")) == report
    assert theorem.OUT_MD.read_text(encoding="utf-8") == theorem.render_markdown(report)
    assert theorem._raw_sha256(theorem.OUT_JSON) == theorem.EXPECTED_REPORT_RAW_SHA256["json"]
    assert theorem._raw_sha256(theorem.OUT_MD) == theorem.EXPECTED_REPORT_RAW_SHA256["md"]
