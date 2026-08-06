#!/usr/bin/env python3
from __future__ import annotations

import exact_phisigma_bose_channel_census_v20 as census


def test_recorded_D5_dimensions() -> None:
    for name, data in census.IRREPS.items():
        if data["label"] is not None:
            assert census.weyl_dimension(data["label"]) == data["dimension"], name


def test_symmetric_and_antisymmetric_dimensions() -> None:
    assert census._weighted_dimension(census.FULL_210_PRODUCT) == 210**2
    assert census._weighted_dimension(census.SYMMETRIC_210_PRODUCT) == 210 * 211 // 2
    assert census._weighted_dimension(census.ANTISYMMETRIC_210_PRODUCT) == 210 * 209 // 2
    for name, multiplicity in census.FULL_210_PRODUCT.items():
        assert (
            census.SYMMETRIC_210_PRODUCT.get(name, 0)
            + census.ANTISYMMETRIC_210_PRODUCT.get(name, 0)
            == multiplicity
        )


def test_common_quartic_channels_are_exactly_six() -> None:
    assert census.COMMON_QUARTIC_CHANNELS == {
        "1": 1,
        "45": 1,
        "210": 1,
        "770": 1,
        "5940": 1,
        "8910": 1,
    }


def test_authoritative_census_and_fail_closed_scope() -> None:
    report = census.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert report["channel_accounting"][
        "total_independent_Hermitian_PhiSigma_quartics"
    ] == 6
    assert report["channel_accounting"]["exact_independent_span_dimension"] == 3
    assert report["channel_accounting"]["remaining_independent_span_dimension"] == 3
    assert report["flag"]["exact_PhiSigma_channel_census_complete"] is True
    assert report["flag"]["all_PhiSigma_quartic_component_Clebsches_complete"] is False
    assert report["flag"]["complete_component_potential"] is False
    assert report["flag"]["physical_triplet_spectrum_complete"] is False
    assert report["flag"]["exact_unique_proton_lifetime"] is False
    assert report["flag"]["whole_model_validated"] is False
    assert report["flag"]["empirical_discovery"] is False
