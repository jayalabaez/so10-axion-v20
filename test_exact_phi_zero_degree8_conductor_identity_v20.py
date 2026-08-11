from exact_phi_zero_degree8_conductor_identity_v20 import (
    EXPECTED_CORE_SHA256,
    certificate,
)


def test_frozen_exact_conductor_core():
    result = certificate(0)
    assert result["core_sha256"] == EXPECTED_CORE_SHA256
    assert result["O_even_degree8_dimension"] == 117
    assert result["unisolvent_rank"] == 117
    assert result["complement_solution_coordinates"] == ["0", "0"]


def test_delta_normalization_and_scope_are_fail_closed():
    result = certificate(0)
    assert result["table_target"] == "delta^2=25D^2"
    assert "delta=9N^2-5" in result["delta_definition"]
    assert "quantitative" in result["scope"]
    assert result["conclusion"].endswith("D=0 over Q/R/C")


def test_first_crt_prime_recomputes_live():
    result = certificate(1)
    assert result["live_primes_recomputed"] == 1
    assert result["core_sha256"] == EXPECTED_CORE_SHA256
