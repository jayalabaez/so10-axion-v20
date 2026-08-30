from __future__ import annotations

import json
import math
from pathlib import Path

import susy_v46_spinor_kk_determinant_audit as audit


ROOT = Path(__file__).resolve().parent


def test_entire_basis_values_at_zero_and_threshold() -> None:
    for mass in (-1.2, -0.3, 0.0, 0.7, 1.5):
        length = 0.83
        assert math.isclose(
            audit.f_function(0.0, mass, length),
            math.exp(-mass * length),
            rel_tol=2.0e-13,
            abs_tol=2.0e-13,
        )
        assert math.isclose(
            audit.g_function(0.0, mass, length),
            math.exp(+mass * length),
            rel_tol=2.0e-13,
            abs_tol=2.0e-13,
        )
        # k^2=0 must be evaluated by analytic continuation, not as 0/0.
        assert math.isclose(
            audit.s_function(mass * mass, mass, length), length, rel_tol=1.0e-13
        )


def test_exact_zero_mode_criteria_for_general_kink_masses() -> None:
    length = 1.17
    for mass_1, mass_2 in ((0.0, 0.0), (0.8, -0.2), (-1.1, -0.4)):
        for b in (0.03, 0.4, 7.0):
            expected_pp = -b * b * math.exp(-(mass_1 + mass_2) * length)
            expected_mp = math.exp((mass_1 + mass_2) * length)
            assert math.isclose(
                audit.d_plus_plus(0.0, mass_1, mass_2, length, b),
                expected_pp,
                rel_tol=2.0e-13,
                abs_tol=2.0e-13,
            )
            assert math.isclose(
                audit.d_minus_plus(0.0, mass_1, mass_2, length, b),
                expected_mp,
                rel_tol=2.0e-13,
                abs_tol=2.0e-13,
            )
        assert audit.d_plus_plus(0.0, mass_1, mass_2, length, 0.0) == 0.0


def test_flat_closed_form_roots() -> None:
    length = 1.31
    b = 0.37
    spectrum = audit.flat_exact_spectra(length, b, levels=5)
    for branch in spectrum["plus_plus_branches"]:
        for mass in branch:
            assert abs(audit.d_plus_plus(mass * mass, 0.0, 0.0, length, b)) < 2.0e-12
    for branch in spectrum["minus_plus_branches"]:
        for mass in branch:
            assert abs(audit.d_minus_plus(mass * mass, 0.0, 0.0, length, b)) < 2.0e-12


def test_no_tachyon_signs_over_parameter_grid() -> None:
    for mass_1 in (-1.4, -0.1, 0.0, 0.9):
        for mass_2 in (-0.8, 0.0, 0.5, 1.7):
            for b in (0.0, 0.02, 0.8, 11.0):
                for kappa in (1.0e-3, 0.1, 1.0, 4.0):
                    z = -kappa * kappa
                    assert audit.d_plus_plus(z, mass_1, mass_2, 0.71, b) < 0.0
                    assert audit.d_minus_plus(z, mass_1, mass_2, 0.71, b) > 0.0


def test_projected_mass_is_small_b_pole_not_exact_finite_b_mass() -> None:
    mass_1, mass_2, length = 0.6, -0.25, 0.9
    tiny_b = 1.0e-3
    exact = audit.first_positive_mass(
        lambda z: audit.d_plus_plus(z, mass_1, mass_2, length, tiny_b),
        maximum_mass=2.0,
        steps=20000,
    )
    projected = math.sqrt(
        audit.projected_mass_squared(mass_1, mass_2, length, tiny_b)
    )
    assert math.isclose(exact, projected, rel_tol=2.0e-6)

    finite_b = 1.0
    exact_flat = math.atan(finite_b) / length
    projected_flat = finite_b / length
    assert not math.isclose(exact_flat, projected_flat, rel_tol=0.1)


def test_canonical_determinant_normalization_and_flat_zeta_result() -> None:
    length = 1.4
    b = 0.62
    ratios = audit.determinant_ratios(0.0, 0.0, length, b)
    assert math.isclose(
        ratios["selected_vs_zero_removed"],
        b * b / (length * length * (1.0 + b * b)),
        rel_tol=2.0e-13,
    )
    assert math.isclose(
        ratios["unselected_vs_b0"], 1.0 / (1.0 + b * b), rel_tol=2.0e-13
    )
    assert math.isclose(
        ratios["spin10_pair_power_8"],
        ratios["one_component_full_pair"] ** 8,
        rel_tol=2.0e-13,
    )


def test_strong_boundary_spectral_flow_is_light_but_not_zero_at_finite_b() -> None:
    length = 0.8
    for b in (100.0, 1000.0, 10000.0):
        exact_flat = (math.pi / 2.0 - math.atan(b)) / length
        asymptotic = 1.0 / (b * length)
        assert exact_flat > 0.0
        assert math.isclose(exact_flat, asymptotic, rel_tol=2.0e-4)
        assert audit.d_minus_plus(0.0, 0.0, 0.0, length, b) == 1.0


def test_report_is_fail_closed_and_uses_only_the_four_bulk_spinors() -> None:
    report = audit.build_report()
    assert not report["scope"]["separate_Bplus_Bminus_hypers"]
    assert report["V45_consequence"]["projected_exotic_rank_if_bL_bR_nonzero"] == 4
    assert report["V45_consequence"]["exact_massless_KK_modes_if_bL_bR_finite_nonzero"] == 0
    assert "n_1+n_2-2r" in report["zero_mode_and_tachyon_theorems"]["multi_copy_rank_rule"]
    assert report["V45_consequence"]["gates_promoted"] == []
    assert not report["V45_consequence"]["complete_theory"]
    assert report["V45_consequence"]["omitted_allowed_source_terms"] == [
        "barSigma HLF HRA",
        "Sigma HLA HRF",
    ]
    assert "before S2 can close" in report["V45_consequence"]["operator_obligation"]
    assert "regulator" in report["declared_boundary_prescription"]["regulator_warning"]


def test_committed_artifacts_are_current() -> None:
    report = audit.build_report()
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == report
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(report)
    for name, digest in report["provenance"]["V45_inputs_sha256"].items():
        assert digest == audit.sha256_file(ROOT / name)
