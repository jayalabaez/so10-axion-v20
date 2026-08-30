from __future__ import annotations

import copy
import json

import numpy as np
import pytest

import susy_v51_degree4_cartesian_factor_audit as audit


def test_exact_spinor_character_decompositions() -> None:
    assert audit.exact_spinor_product_decompositions() == {
        "16x16": True,
        "16xbar16": True,
        "bar16x16": True,
        "bar16xbar16": True,
    }


def test_all_120_rows_resolve_to_76_zero_44_nonempty_72_directions() -> None:
    certificate = audit.degree_four_certificate()
    assert certificate["total_rows"] == 120
    assert certificate["zero_rows"] == 76
    assert certificate["nonempty_rows"] == 44
    assert certificate["total_invariant_directions"] == 72
    assert certificate["multiplicity_histogram"] == {
        "0": 76, "1": 28, "2": 4, "3": 12
    }
    assert certificate["all_nonzero_copy_multiplicities_one"]


def test_sector_and_channel_direction_counts() -> None:
    certificate = audit.degree_four_certificate()
    assert certificate["by_sector"]["HH"] == {
        "rows": 30, "zero_rows": 20, "nonempty_rows": 10,
        "invariant_directions": 16,
    }
    assert certificate["by_sector"]["HcHc"] == {
        "rows": 30, "zero_rows": 20, "nonempty_rows": 10,
        "invariant_directions": 16,
    }
    assert certificate["by_sector"]["HcH"] == {
        "rows": 60, "zero_rows": 36, "nonempty_rows": 24,
        "invariant_directions": 40,
    }
    assert certificate["direction_channel_histogram"] == {
        "1": 20, "10": 8, "120": 8, "126": 6,
        "210": 16, "45": 8, "bar126": 6,
    }


def test_every_row_is_resolved_and_every_zero_has_exact_reason() -> None:
    rows = audit.degree_four_certificate()["rows"]
    assert len({row["id"] for row in rows}) == 120
    assert all(row["U1F_charge"] == 0 for row in rows)
    for row in rows:
        assert row["instantiation_status"].startswith("RESOLVED_")
        assert row["invariant_multiplicity"] == len(row["directions"])
        if row["invariant_multiplicity"] == 0:
            assert row["zero_reason"]
            assert not any(row["spinor_channel_intersection_multiplicities"].values())
        else:
            assert row["zero_reason"] is None


def test_all_16_source_factor_arrays_have_certified_gram_and_covariance() -> None:
    registry = audit.normalized_source_factor_registry()
    assert len(registry) == 16
    # Conjugate identity maps and conjugate maps into the real 10 can have the
    # same component array.  Their representation-orientation IDs remain
    # distinct even when their raw hashes coincide.
    assert all(len(row["raw_array_sha256"]) == 64 for row in registry.values())
    assert len({row["raw_array_sha256"] for row in registry.values()}) == 14
    for row in registry.values():
        assert row["raw_gram_isotropy_residual"] < 1.0e-12
        assert row["normalized_gram_residual"] < 1.0e-12
        assert row["covariance_seed_output_norm"] > 1.0e-12
        assert row["all_45_generator_seed_covariance_residual"] < 1.0e-9
        assert row["output_rank_from_positive_gram"] == audit.DIMENSION[
            row["output_representation"]
        ]
        if row["bosonic_exchange_symmetry_residual"] is not None:
            assert row["bosonic_exchange_symmetry_residual"] < 1.0e-12


def test_raw_factor_scale_constants_are_locked() -> None:
    registry = audit.normalized_source_factor_registry()
    expected = {
        "SRC_PHIxPHI_TO_1": 210,
        "SRC_PHIxPHI_TO_45": 70,
        "SRC_PHIxPHI_TO_210": 90,
        "SRC_SIGMAxBARSIGMA_TO_1": 504,
        "SRC_SIGMAxBARSIGMA_TO_45": 280,
        "SRC_SIGMAxBARSIGMA_TO_210": 240,
        "SRC_PHIxSIGMA_TO_10": 126,
        "SRC_PHIxSIGMA_TO_120": 105,
        "SRC_PHIxSIGMA_TO_126": 100,
        "SRC_PHIxBARSIGMA_TO_10": 126,
        "SRC_PHIxBARSIGMA_TO_120": 105,
        "SRC_PHIxBARSIGMA_TO_bar126": 100,
    }
    assert {key: registry[key]["raw_gram_scale"] for key in expected} == expected


def test_all_spin_factors_are_normalized_and_all_72_directions_resolve() -> None:
    source = audit.normalized_source_factor_registry()
    spin = audit.normalized_spin_factor_registry()
    assert len(spin) == 12
    assert max(row["normalized_gram_residual"] for row in spin.values()) < 1.0e-12
    directions = [
        direction
        for row in audit.degree_four_certificate()["rows"]
        for direction in row["directions"]
    ]
    assert len(directions) == 72
    assert len({row["direction_id"] for row in directions}) == 72
    for direction in directions:
        assert direction["channel_copy_index"] == 1
        assert direction["spin_factor_tensor_id"] in spin
        assert direction["source_factor_tensor_id"] in source
        assert direction["normalized_composite_formula"].startswith("(1/sqrt(")


def test_phi_phi_bosonic_symmetry_kill_detects_overcount() -> None:
    certificate = audit.bosonic_symmetry_kill_certificate()
    assert certificate["correct_channel_multiplicities"] == {
        "1": 1, "45": 1, "210": 1
    }
    assert certificate["incorrect_ordered_tensor_square_multiplicities"] == {
        "1": 1, "45": 2, "210": 2
    }
    assert certificate["correct_total"] == 3
    assert certificate["incorrect_total"] == 5
    assert certificate["overcount_if_bosonic_quotient_is_dropped"] == 2


def test_explicit_phi_phi_arrays_are_symmetric() -> None:
    for identifier in (
        "SRC_PHIxPHI_TO_1", "SRC_PHIxPHI_TO_45", "SRC_PHIxPHI_TO_210"
    ):
        tensor = audit.source_factor_array(identifier)
        assert np.max(np.abs(tensor - tensor.swapaxes(1, 2))) < 1.0e-12
        audit.source_factor_array.cache_clear()


def test_upstream_core_is_the_repaired_v51_core() -> None:
    report = audit.build_report()
    assert report["upstream"]["V51_cartesian_mediator_C5_C7"]["core_sha256"] == (
        "cce7c67c44e1a0f164bd226cbf7307054cd16b20604202b5d95e1083983a5da0"
    )


def test_degree4_pass_does_not_overpromote_C7_or_G2() -> None:
    report = audit.build_report()
    assert report["C7_decision"]["degree_four_factor_copy_clause"] == "PASS_V51"
    assert report["C7_decision"]["closed"] is False
    assert report["C7_decision"]["G2_closed"] is False
    assert report["C7_decision"]["gates_promoted"] == []
    assert report["n_failed_integrity_checks"] == 0
    assert all(report["integrity_checks"].values())


def test_validation_rejects_count_tamper() -> None:
    report = audit.build_report()
    tampered = copy.deepcopy(report)
    tampered["degree_four_certificate"]["zero_rows"] = 75
    tampered["core_sha256"] = audit.canonical_sha(tampered)
    with pytest.raises(RuntimeError, match="zero_rows"):
        audit.validate(tampered)


def test_hash_and_checked_artifacts_are_current() -> None:
    report = audit.build_report()
    assert report["core_sha256"] == audit.canonical_sha(report)
    audit.validate(report)
    audit.check_artifacts(report)
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == report
