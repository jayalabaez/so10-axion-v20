from exact_phi_self_zero_global_signed_kaehler_classification_v20 import (
    EXPECTED_CORE_SHA256,
    certificate,
)


def test_frozen_global_signed_zero_locus():
    result = certificate()
    assert result["core_sha256"] == EXPECTED_CORE_SHA256
    assert result["norm10_zero_locus"] == "SO(10).F union SO(10).(-F)"
    assert result["scope"]["global_real_zero_locus_classified"] is True


def test_exact_representative_and_stabilizer_data():
    result = certificate()
    representative = result["representative"]
    assert representative["norm_squared"] == 10
    assert (representative["I3_plus"], representative["I3_minus"]) == (60, -60)
    assert representative["orbit_Gram_rank"] == 20
    assert representative["orbit_Gram_spectrum"] == "0^25,12^20"
    assert result["subgroup_rigidity"]["unitary_maximal"] == {
        "name": "U(5)",
        "dimension": 25,
    }


def test_quantitative_scope_remains_fail_closed():
    result = certificate()
    assert result["scope"]["signed_zero_boundary_operator_safe"] is True
    assert result["scope"]["quantitative_orbit_distance_bound"] is False
    assert result["scope"]["G3_closed"] is False
    assert result["scope"]["G4_closed"] is False
    warning = result["quantitative_warning"]
    assert warning["transverse_quadratic_kernel_dimension"] == 10
    assert warning["required_local_exponent"] == "quartic in the ten conductor directions"
