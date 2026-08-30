#!/usr/bin/env python3
"""Regression tests for the pinned independent PyR@TE 3 gauge replay."""

from fractions import Fraction

import pyrate3_so10_u1x_gauge_beta_replay_v20 as mod


def test_canonical_model_has_full_parser_safe_inventory():
    model = mod.MODEL.read_text(encoding="utf-8")
    assert mod._sha256(mod.MODEL) == mod.EXPECTED_MODEL_SHA256
    assert mod._model_inventory_present(model)
    assert sum(mod.EXPECTED_FERMION_GENERATIONS.values()) == 19
    assert {"Pc", "Qc", "Rc"} <= set(mod.EXPECTED_FERMION_GENERATIONS)
    assert "    Pbar:" not in model
    assert "    Qbar:" not in model
    assert "    Rbar:" not in model


def test_frozen_external_provenance_is_commit_and_terminal_hash_bound():
    frozen = mod._load_json(mod.FROZEN)
    assert mod._sha256(mod.FROZEN) == mod.EXPECTED_FROZEN_SHA256
    assert frozen["tool"]["repository"] == mod.PYRATE_REPOSITORY
    assert frozen["tool"]["git_commit"] == mod.PYRATE_COMMIT
    assert (
        frozen["replay"]["terminal_log_sha256"]
        == mod.EXPECTED_TERMINAL_LOG_SHA256
    )
    assert (
        frozen["replay"]["generated_tex_sha256"]
        == mod.EXPECTED_GENERATED_TEX_SHA256
    )
    assert frozen["replay"]["gauge_invariance"] == "All OK"
    assert frozen["replay"]["completed"]
    assert frozen["replay"]["executed_model"] == "models/SO10U1XGaugeAudit.model"
    assert (
        frozen["replay"]["canonical_model"]
        == "models/SO10U1XGaugeAuditV20.model"
    )
    assert (
        frozen["replay"]["executed_model_sha256"]
        == frozen["replay"]["canonical_model_sha256"]
        == mod.EXPECTED_MODEL_SHA256
    )
    assert frozen["replay"][
        "canonical_model_is_byte_identical_rename_of_executed_input"
    ]


def test_all_four_gauge_polynomials_match_authoritative_report_exactly():
    frozen = mod._load_json(mod.FROZEN)
    authoritative = mod.authoritative.build_report()
    replay = mod.frozen_coefficients(frozen)
    expected = mod.authoritative_coefficients(authoritative)
    assert replay == expected
    assert replay == {
        "beta_g10_loop1": {"g10^3": Fraction(52, 3)},
        "beta_g10_loop2": {
            "g10^5": Fraction(25013, 6),
            "g10^3*gX^2": Fraction(4536),
        },
        "beta_gX_loop1": {"gX^3": Fraction(10843)},
        "beta_gX_loop2": {
            "g10^2*gX^3": Fraction(204120),
            "gX^5": Fraction(7242180),
        },
    }


def test_report_is_exactly_scoped_and_fail_closed_for_g7():
    report = mod.build_report()
    assert report["status"] == mod.STATUS
    assert report["n_failed"] == 0
    assert all(report["checks"].values())
    rename = report["executed_input_provenance"]
    assert rename["byte_identical_rename"] is True
    assert rename["executed_model_sha256"] == rename[
        "tracked_canonical_model_sha256"
    ]
    assert report["comparison"] == {
        "target": "exact_authoritative_so10_u1x_gauge_betas_v20.py/report",
        "arithmetic": "exact rational",
        "tolerance": "0",
        "all_coefficients_match": True,
    }
    assert report["scope"]["gauge_only"]
    assert report["scope"]["non_Yukawa"]
    assert not report["scope"]["complete_two_loop_model_RGE"]
    assert not report["scope"]["G6_physical_threshold_input"]
    assert not report["scope"]["G7_closure"]
    flags = report["classification"]
    assert flags["independent_gauge_polynomial_replay_closed"]
    assert flags["second_implementation_for_scoped_gauge_subtheorem"]
    assert not flags["full_two_loop_gauge_beta_closed"]
    assert not flags["physical_G6_threshold_matching_closed"]
    assert not flags["mathematical_G7_closed"]
    assert not flags["release_G7_verified"]


def test_normal_check_uses_frozen_data_without_external_replay():
    report = mod.build_report()
    assert report["normal_test_policy"]["execute_external_PyRATE"] is False
    assert report["normal_test_policy"]["verify_hash_bound_frozen_result"] is True
    mod.check_tracked_report(report)


def test_core_and_source_hashes_are_frozen():
    report = mod.build_report()
    assert report["core_sha256"] == mod.EXPECTED_CORE_SHA256
    assert report["source_sha256"] == mod._sha256(mod.Path(mod.__file__).resolve())
