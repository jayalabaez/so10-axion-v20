from __future__ import annotations

import exact_phi_self_zero_global_sextic_syzygy_v20 as source


def test_exact_global_sextic_identity_certificate() -> None:
    report = source.build_report()
    assert report["n_failed"] == 0
    assert all(report["source_binding"]["dependency_checks"].values())
    assert report["source_binding"]["core_hash_matches"]
    assert report["degree_six_invariant_census"]["trivial_multiplicity"] == 18
    assert set(
        report["unisolvent_CRT_certificate"]["all_evaluation_ranks"]
    ) == {18}
    assert set(
        report["unisolvent_CRT_certificate"][
            "all_maximum_relation_residuals"
        ]
    ) == {0}
    assert report["integer_height_certificate"][
        "prime_product_exceeds_twice_bound"
    ]


def test_common_zero_reduction_has_the_frozen_coefficients() -> None:
    identity = source.build_report()["identity"]
    assert identity["N_D_coefficient"] == source.Fraction(1405, 64)
    assert identity["S_coefficient"] == source.Fraction(35, 1536)
    assert identity["common_zero_reduction"] == (
        "5*I3^2-18*N^3=(1405/64)*N*D+(35/1536)*S"
    )
    assert len(identity["ideal_terms"]) == 15
    assert all(
        row["feature"][0] in {"54", "4125"}
        for row in identity["ideal_terms"]
    )


def test_global_classification_is_not_overclaimed() -> None:
    scope = source.build_report()["scope"]
    assert scope["global_polynomial_identity_proved"]
    assert scope["common_zero_sextic_reduction_proved"]
    assert not scope["D_zero_on_common_zero_set_proved"]
    assert not scope["global_common_zero_locus_classified"]
    assert not scope["G3_closed"]
    assert not scope["G4_closed"]
