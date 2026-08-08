"""Tests for the direct exact P+Delta_R rank audit."""
from __future__ import annotations

import os
import json
from fractions import Fraction

import pytest

import exact_gauged_u1x_g3_pd_rank_certificate_v20 as certificate


def test_qsqrt2_arithmetic_and_exact_signs() -> None:
    root_two = certificate.Qsqrt2(Fraction(0), Fraction(1))
    assert root_two * root_two == certificate.Qsqrt2(Fraction(2), Fraction(0))
    assert (certificate.Qsqrt2(3, -2)).sign() > 0
    assert (certificate.Qsqrt2(1, -1)).sign() < 0
    assert (certificate.Qsqrt2(-3, 2)).sign() < 0
    assert (certificate.Qsqrt2(-1, 1)).sign() > 0
    assert (root_two / root_two) == certificate.Qsqrt2(Fraction(1), Fraction(0))


def test_exact_singular_psd_and_zero_pivot_handling() -> None:
    one = certificate.Qsqrt2(1, 0)
    two = certificate.Qsqrt2(2, 0)
    root_two = certificate.Qsqrt2(0, 1)
    rank_one = certificate.exact_psd_rank(
        [[one, root_two], [root_two, two]]
    )
    assert rank_one["PSD"] is True
    assert rank_one["rank"] == 1

    indefinite_zero_diagonal = certificate.exact_psd_rank(
        [[certificate.ZERO_QSQRT2, one], [one, certificate.ZERO_QSQRT2]]
    )
    assert indefinite_zero_diagonal["PSD"] is False
    assert "zero diagonal" in indefinite_zero_diagonal["reason"]


def test_delta_numerator_is_derived_on_the_exact_gaussian_lattice() -> None:
    real, imag, metadata = certificate.exact_delta_numerator()
    assert metadata["normalisation"] == "Delta_R=(sqrt(2)/4)*d"
    assert metadata["unnormalised_kinetic_norm_squared"] == 8
    assert metadata["support"] == [75, 80, 81, 86, 95, 100, 101, 106]
    assert [(int(real[index]), int(imag[index])) for index in metadata["support"]] == [
        (1, 0),
        (1, 0),
        (0, 1),
        (0, 1),
        (0, 1),
        (0, 1),
        (-1, 0),
        (-1, 0),
    ]


def test_direct_mixed_square_builder_is_exact_and_overflow_guarded() -> None:
    rational, radical, denominator, metadata = certificate.direct_exact_mixed_hessian()
    assert denominator == 8
    assert rational.shape == (462, 462)
    assert radical.shape == (462, 462)
    assert (rational == rational.T).all()
    assert (radical == radical.T).all()
    assert metadata["maximum_abs_rational_numerator"] == 128
    assert metadata["maximum_abs_radical_numerator"] == 16
    preflight = metadata["int64_overflow_preflight"]
    assert max(
        value for key, value in preflight.items() if key != "int64_limit"
    ) < preflight["int64_limit"]


def test_recorded_certificate_is_internally_complete_and_scope_honest() -> None:
    report = certificate.build_report()
    assert report["n_failed"] == 0
    assert report["overall_state"] == "OPEN"
    direct = report["direct_P_plus_Delta_certificate"]
    ranks = report["direct_exact_ranks"]
    assert ranks["K"] == {"rank": 278, "nullity": 184, "PSD": True}
    assert ranks["H_Phi"] == {"rank": 186, "nullity": 276, "PSD": True}
    assert ranks["H_Phi_plus_K"] == {
        "rank": 429,
        "nullity": 33,
        "PSD": True,
    }
    assert direct["source_binding_exact"] is True
    assert report["flags"]["proof_grade_P_plus_Delta_PSD"] is True
    assert report["flags"]["proof_grade_full_rank_448"] is True
    assert report["flags"]["strict_transverse_Hessian_positive_certified"] is True
    assert report["flags"]["exact_stationarity_certified_here"] is False
    assert report["flags"]["global_BFB_certified_here"] is False
    assert report["flags"]["strict_local_minimum_certified_here"] is False
    assert report["flags"]["G3_closed"] is False


def test_exact_extension_kernel_count_and_explicit_rank_19_jacobian() -> None:
    extension = certificate.extension_kernel_argument()
    assert extension["exact_P_plus_Delta_gauge_orbit"]["exact_orbit_rank"] == 33
    assert extension["kernel_after_adjoining_free_H_S_Phi17_coordinates"] == 57
    assert extension["added_exact_rank"] == 19
    assert extension["explicit_quotient_constraint_Jacobian"]["shape"] == [26, 24]
    assert extension["explicit_quotient_constraint_Jacobian"]["exact_rational_rank"] == 19
    assert extension["explicit_quotient_constraint_Jacobian"][
        "incremental_exact_ranks"
    ] == {
        "H_wedge_Phi_rows": 12,
        "plus_complex_H_Gram_rows": 15,
        "plus_three_radial_rows": 18,
        "plus_two_H_S_phase_lock_rows": 19,
    }
    assert extension["remaining_kernel_dimension"] == 38
    assert extension["exact_full_Hessian_rank"] == 448
    assert extension["source_binding_exact"] is True
    assert extension["proof_grade"] is True


def test_exposed_cli_dispatch_modes(monkeypatch, capsys, tmp_path) -> None:
    calls: list[bool] = []

    def fake_recompute(*, compare_live: bool = False):
        calls.append(compare_live)
        return {"sentinel": compare_live}

    fake_report = {
        "n_failed": 0,
        "direct_exact_ranks": {
            "K": {"rank": 278, "nullity": 184},
            "H_Phi": {"rank": 186, "nullity": 276},
            "H_Phi_plus_K": {"rank": 429, "nullity": 33},
        },
        "status": "TEST",
    }
    monkeypatch.setattr(certificate, "recompute_direct_certificate", fake_recompute)
    monkeypatch.setattr(certificate, "build_report", lambda _value=None: fake_report)
    monkeypatch.setattr(certificate, "write_markdown", lambda _report: "test\n")
    monkeypatch.setattr(certificate, "OUT_JSON", tmp_path / "report.json")
    monkeypatch.setattr(certificate, "OUT_MD", tmp_path / "report.md")

    assert certificate.main([]) == 0
    assert certificate.main(["--recompute-heavy"]) == 0
    assert certificate.main(["--compare-live"]) == 0
    assert certificate.main(["--write"]) == 0
    assert calls == [False, True]
    assert json.loads((tmp_path / "report.json").read_text())["status"] == "TEST"
    assert (tmp_path / "report.md").read_text() == "test\n"
    capsys.readouterr()


@pytest.mark.skipif(
    os.environ.get("SO10_RUN_HEAVY_G3_PD_CERTIFICATE") != "1",
    reason="set SO10_RUN_HEAVY_G3_PD_CERTIFICATE=1 for direct exact/live rebuilds",
)
def test_direct_exact_qsqrt2_component_ldl_and_live_regression() -> None:
    recomputed = certificate.recompute_direct_certificate(compare_live=True)
    assert recomputed["K"]["exact_PSD"] is True
    assert recomputed["K"]["exact_rank"] == 278
    assert recomputed["H_Phi"]["exact_rank"] == 186
    assert recomputed["H_Phi_plus_K"]["exact_PSD"] is True
    assert recomputed["H_Phi_plus_K"]["exact_rank"] == 429
    assert recomputed["source_binding_exact"] is True
    assert recomputed["proof_grade"] is True
    assert recomputed["nonproof_live_regression_pass"] is True
    assert max(recomputed["nonproof_live_regression_max_abs_residuals"].values()) < 2.0e-11
    for sector in ("mixed", "self", "Phi"):
        preflight = recomputed["construction"][sector]["int64_overflow_preflight"]
        assert max(
            value for key, value in preflight.items() if key != "int64_limit"
        ) < preflight["int64_limit"]
