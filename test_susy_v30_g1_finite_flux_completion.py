from __future__ import annotations

import json
import subprocess
import sys
from fractions import Fraction

import susy_v30_g1_finite_flux_completion as v30


def test_upstream_sources_and_core_pins_match() -> None:
    report, _evidence = v30.build_bundle()
    assert report["checks"]["all_raw_source_pins_match"] is True
    assert report["checks"]["upstream_cores_match"] is True


def test_single_modulus_polynomial_has_unique_finite_minkowski_root() -> None:
    # w=x-4x^2+4x^3=4x(x-1/2)^2 and w'=1-8x+12x^2.
    # The roots of w are 0 and 1/2; x=exp(-2*pi*T) cannot be zero at finite T.
    # Of those roots, only 1/2 is also a root of w'.
    def w(x: Fraction) -> Fraction:
        return x - 4 * x * x + 4 * x * x * x

    def dw(x: Fraction) -> Fraction:
        return 1 - 8 * x + 12 * x * x

    assert w(Fraction(0)) == 0
    assert dw(Fraction(0)) != 0
    assert w(Fraction(1, 2)) == 0
    assert dw(Fraction(1, 2)) == 0
    # d2w/dx2=24x-8=4 at x=1/2.  Chain rule with dx/dT=-2*pi*x
    # gives d2w/dT2=(2*pi)^2*x^2*4=4*pi^2.
    assert (2**2) * Fraction(1, 2) ** 2 * 4 == 4


def test_primitive_instanton_frame_is_exact_identity_basis() -> None:
    contract = v30.moduli_and_hidden_contract()
    rows = contract["instanton_inventory"]
    assert len(rows) == 51
    for index, row in enumerate(rows):
        vector = row["primitive_charge_vector"]
        assert len(vector) == 51
        assert vector[index] == 1
        assert sum(vector) == 1
        assert row["harmonic_charges"] == [1, 2, 3]
        assert row["four_form_coefficients"] == [1, -4, 4]
    matrix = contract["primitive_charge_matrix"]
    assert matrix["rank"] == 51
    assert matrix["determinant"] == 1


def test_combined_moduli_hessian_is_full_rank_and_positive() -> None:
    contract = v30.moduli_and_hidden_contract()
    assert contract["Kahler_superpotential"]["complex_rank"] == 51
    assert contract["flux_superpotential"]["complex_rank"] == 4
    full = contract["full_moduli_Hessian"]
    assert full["complex_dimension"] == 55
    assert full["complex_rank"] == 55
    assert full["real_rank"] == 110
    assert full["positive_physical_spectrum_for_regular_positive_Kahler_metric"] is True
    assert full["supersymmetric_Minkowski"] is True


def test_discrete_anomaly_congruences_close_inside_ffcc() -> None:
    v24 = json.loads(
        (v30.ROOT / "SUSY_V24_PS_SOURCE_CONTRACT.json").read_text(encoding="utf-8")
    )
    manifest = v30.field_and_selector_manifest(v24)
    levels = manifest["anomaly_and_level_matrix"]["T01_integer_topological_levels"]
    assert (1 - levels["SU4"]) % 2 == 0
    assert (1 - levels["SU2L"]) % 2 == 0
    assert (1 - levels["SU2R"]) % 2 == 0
    assert (9 - 9 * levels["SU4"]) % 11 == 0
    assert (7 - 9 * levels["Z11_gravity"]) % 11 == 0
    assert (7 - 9 * levels["Z11_cubic"]) % 11 == 0
    assert ((20 - 51) - levels["Z4R_gravity_after_51_modulini"]) % 2 == 0


def test_finite_projector_matches_exact_18_term_visible_source() -> None:
    v24 = json.loads((v30.ROOT / "SUSY_V24_PS_SOURCE_CONTRACT.json").read_text(encoding="utf-8"))
    contract = v30.operator_and_matching_contract(v24)
    source_keys = [row["key"] for row in v24["symmetry_complete_renormalizable_operator_ledger"]]
    projected = contract["finite_chiral_projection"]
    assert projected["retained_visible_channels"] == 18
    assert projected["retained_operator_keys"] == source_keys
    assert projected["all_other_holomorphic_visible_Wilson_coefficients"] == 0
    assert projected["driver_tower_X_odd_A_n_for_n_gt_1"] == 0
    assert contract["soft_contract"]["all_soft_terms"] == 0


def test_v27_submission_bundle_is_complete_and_hash_bound() -> None:
    _report, evidence = v30.build_bundle()
    submission = evidence[v30.SUBMISSION_JSON.name]
    assert v30.submission_has_v27_shape(submission) is True
    by_name = {row["path_or_url"]: row for row in submission["evidence_manifest"]}
    for name in (v30.FIELD_JSON.name, v30.OPERATOR_JSON.name, v30.MODULI_JSON.name):
        assert by_name[name]["sha256_or_version"] == v30.evidence_hash(evidence[name])
    assert submission["all_acceptance_checks_pass"] is True


def test_conditional_closure_is_not_misreported_as_established_physics() -> None:
    report, evidence = v30.build_bundle()
    assert report["internal_G1_acceptance"]["conditional_closed"] is True
    assert report["internal_G1_acceptance"]["passed"] == 6
    assert report["scientific_evidence_grade"]["established_microscopic_G1_closed"] is False
    fields = evidence[v30.FIELD_JSON.name]
    axiom = fields["selector"]["finite_chiral_functional_axiom"]
    assert axiom["microscopic_origin_known"] is False
    assert axiom["local_superspace_realization_known"] is False
    assert report["n_failed"] == 0, report["failures"]


def test_frozen_outputs_and_cli() -> None:
    report, evidence = v30.build_bundle()
    assert v30.canonical_sha(report) == report["core_sha256"]
    assert v30.check_outputs(report, evidence) is True
    completed = subprocess.run(
        [sys.executable, "-B", str(v30.ROOT / "susy_v30_g1_finite_flux_completion.py"), "--check"],
        cwd=v30.ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
