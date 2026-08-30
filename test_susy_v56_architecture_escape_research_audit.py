from __future__ import annotations

import json

import susy_v56_architecture_escape_research_audit as audit


def report() -> dict:
    value = audit.build_report()
    audit.validate(value)
    return value


def blueprint(value: dict, blueprint_id: str) -> dict:
    return next(row for row in value["blueprints"] if row["id"] == blueprint_id)


def route(value: dict, route_id: str) -> dict:
    return next(row for row in value["route_audit"] if row["id"] == route_id)


def test_bound_v55_core_and_v56_core_are_canonical() -> None:
    value = report()
    binding = value["V55_input_binding"]
    assert binding["expected_core_sha256"] == audit.EXPECTED_V55_CORE
    assert binding["actual_core_sha256"] == audit.EXPECTED_V55_CORE
    assert value["core_sha256"] == audit.canonical_sha(value)


def test_all_requested_route_classes_are_audited_but_only_two_selected() -> None:
    value = report()
    classes = {item for row in value["route_audit"] for item in row["classes"]}
    assert {
        "missing_partner",
        "product_group",
        "deconstruction",
        "locality",
        "non_Abelian_selection",
        "discrete_R",
        "mediator",
    }.issubset(classes)
    assert [row["id"] for row in value["route_audit"] if row["selected"]] == [
        "R1_MISSING_PARTNER",
        "R2_ORBIFOLD_LOCALITY",
    ]
    assert value["selection"]["selected_count"] == 2
    assert value["selection"]["maximum_allowed"] == 2


def test_missing_partner_structural_rank_certificate_is_exact() -> None:
    cert = audit.missing_partner_rank_certificate()
    assert cert["triplet_shape"] == [6, 6]
    assert (cert["triplet_rank"], cert["triplet_right_nullity"]) == (6, 0)
    assert cert["doublet_shape"] == [5, 5]
    assert (cert["doublet_rank"], cert["doublet_right_nullity"]) == (4, 1)
    assert audit.exact_rank(cert["triplet_matrix"]) == 6
    assert audit.exact_rank(cert["doublet_matrix"]) == 4


def test_missing_partner_field_and_term_obligations_are_explicit() -> None:
    bp = blueprint(report(), "BP1_4D_SO10_126_MISSING_PARTNER")
    reps = {(row["field"], row["SO10_rep"]) for row in bp["field_obligations_case_a"]}
    assert {
        ("H", "10"),
        ("Sigma", "120"),
        ("Delta", "126"),
        ("barDelta", "126bar"),
        ("Phi", "210"),
        ("C", "16"),
        ("barC", "16bar"),
    }.issubset(reps)
    terms = bp["term_obligations"]
    assert terms["DT_required"] == [
        "Phi Delta H",
        "Phi Delta Sigma",
        "Phi barDelta H",
        "Phi barDelta Sigma",
        "X barDelta Delta",
    ]
    assert {"H^2", "Sigma^2", "Phi H Sigma"}.issubset(
        terms["must_be_absent_to_all_relevant_orders"]
    )
    assert any("Delta_1=0" in item for item in bp["vacuum_obligations"])


def test_missing_partner_one_loop_uv_pressure_matches_paper_scale() -> None:
    uv = audit.missing_partner_uv_pressure()
    assert uv["sum_chiral_indices"] == 165
    assert uv["one_loop_b"] == 141
    assert 1.7 < uv["one_loop_pole_over_M_SO10"] < 1.8
    assert abs(uv["one_loop_pole_GeV"] / 1.0e17 - 1.7) < 0.1


def test_orbifold_component_formula_has_expected_single_zero_for_each_10() -> None:
    first = audit.parity_components(1, -1)
    second = audit.parity_components(-1, 1)
    assert [name for name, parity in first.items() if parity == [1, 1]] == ["h2"]
    assert [name for name, parity in second.items() if parity == [1, 1]] == ["bar_h2"]


def test_orbifold_pair_has_hu_hd_and_no_colored_zero_mode() -> None:
    cert = audit.orbifold_zero_mode_certificate()
    assert cert["zero_modes"] == ["H10:h2", "H10_prime:bar_h2"]
    assert cert["weak_doublet_zero_mode_count"] == 2
    assert cert["color_triplet_zero_mode_count"] == 0
    assert all(
        row["SM_kind"] == "weak_doublet"
        for row in cert["component_ledger"]
        if row["has_massless_zero_mode"]
    )


def test_orbifold_blueprint_preserves_full_anomaly_and_boundary_obligations() -> None:
    bp = blueprint(report(), "BP2_6D_SO10_T2_OVER_Z2_LOCALITY")
    obligations = bp["field_and_boundary_obligations"]
    assert any("brane mass" in item for item in obligations)
    assert "irreducible gauge anomaly" in bp["anomaly_obligations"][
        "paper_level_result"
    ]
    pending = " ".join(bp["anomaly_obligations"]["still_required"])
    assert "gravitational" in pending
    assert "Green-Schwarz" in pending
    assert "localized" in pending
    assert any("KK quadratic operator" in item for item in bp["quadratic_operator_obligations"])


def test_both_blueprints_genuinely_change_the_v55_topology() -> None:
    value = report()
    assert all(row["escape_from_V55"]["changes_fixed_topology"] for row in value["blueprints"])
    missing = blueprint(value, "BP1_4D_SO10_126_MISSING_PARTNER")
    orbifold = blueprint(value, "BP2_6D_SO10_T2_OVER_Z2_LOCALITY")
    assert "rectangular rank" in missing["escape_from_V55"]["reason"]
    assert "boundary-condition/locality" in orbifold["escape_from_V55"]["reason"]


def test_deconstruction_r_symmetry_and_mediator_routes_are_not_overclaimed() -> None:
    value = report()
    assert not route(value, "R3_PRODUCT_GROUP_DECONSTRUCTION")["selected"]
    r_route = route(value, "R4_NONABELIAN_OR_DISCRETE_R")
    assert not r_route["selected"]
    assert "published no-go theorem" in r_route["decision"]
    assert "outside" in r_route["decision"]
    mediator = route(value, "R5_MEDIATOR_UV_COMPLETION")
    assert not mediator["selected"]
    assert "not by itself a selection rule" in mediator["decision"]


def test_only_primary_external_literature_is_used() -> None:
    sources = report()["primary_sources"]
    assert {row["arxiv"] for row in sources} == {
        "hep-ph/0612315",
        "hep-ph/0108071",
        "hep-ph/0201018",
        "1109.4797",
        "1504.01850",
    }
    assert all(row["source_kind"] == "primary_author_manuscript" for row in sources)
    assert all(row["url"].startswith("https://arxiv.org/abs/") for row in sources)


def test_mechanisms_are_not_one_action_completions_and_promote_no_gate() -> None:
    value = report()
    assert all(not row["one_action_completion"] for row in value["blueprints"])
    assert all(row["gate_promotions"] == [] for row in value["blueprints"])
    assert not value["decision"]["one_action_completion_found"]
    assert not value["decision"]["complete_theory"]
    assert value["decision"]["G1_to_G8_promotions"] == []


def test_integrity_checks_and_generated_artifacts_are_current() -> None:
    value = report()
    assert value["n_failed_integrity_checks"] == 0
    assert all(value["integrity_checks"].values())
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == value
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(value)
