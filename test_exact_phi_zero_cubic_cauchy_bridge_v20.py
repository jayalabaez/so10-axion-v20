from __future__ import annotations

import exact_phi_zero_cubic_cauchy_bridge_v20 as source


def test_exact_cubic_cauchy_bridge() -> None:
    report = source.build_report()
    assert report["n_failed"] == 0
    assert all(report["source_binding"]["dependency_checks"].values())
    assert report["source_binding"]["core_hash_matches"]
    identities = report["global_identities"]
    assert identities["Schur_norm_identity"] == "||U||^2=90*p210"
    assert identities["Cauchy_inequality"] == "I3^2<=90*N*p210"
    assert identities["common_zero_inequality"] == (
        "I3^2<=(18/5)*N^3+6*N*D"
    )


def test_channel_identity_is_exact_in_complete_quartic_basis() -> None:
    report = source.build_report()
    assert report["quartic_unisolvence"]["invariant_dimension"] == 4
    assert report["quartic_unisolvence"]["evaluation_determinant"] != 0
    assert report["channel_identity_coefficients"]["coefficientwise_residual"] == (
        source.Fraction(0),
    ) * 4


def test_degree_eight_conductor_remains_fail_closed() -> None:
    scope = source.build_report()["scope"]
    assert scope["global_cubic_Cauchy_bound_proved"]
    assert not scope["D_zero_proved"]
    assert not scope["global_zero_locus_classified"]
    assert not scope["G3_closed"]
    assert not scope["G4_closed"]
