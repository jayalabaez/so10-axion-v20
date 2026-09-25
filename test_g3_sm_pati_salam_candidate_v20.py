#!/usr/bin/env python3
"""Tests for the SM Pati-Salam G3 candidate (v20).

The exact sections and the live-compiler audit at r0 = 1/5 are recomputed and
compared with the committed artifact through target.report_mismatches; the
multi-r0 scan and the numerical global search are too slow for a unit test and
are checked as committed evidence.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

import g3_candidate_physical_target_audit_v20 as target
import g3_sm_pati_salam_candidate_v20 as candidate
import live_g2_canonical_486_field_chart_v20 as chart


def _strip_timing(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _strip_timing(item) for key, item in value.items() if key != "seconds"}
    if isinstance(value, list):
        return [_strip_timing(item) for item in value]
    return value


class SmPatiSalamCandidateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.committed = json.loads(candidate.OUT_JSON.read_text(encoding="utf-8"))
        physical_states = cls.committed["compiler"]["M_I/M_GUT"]["light_spectrum"]["states"]
        cls.fresh = {
            "candidate": candidate.json_roundtrip(candidate.candidate_section()),
            "sm_embedding": candidate.json_roundtrip(candidate.sm_embedding_section()),
            "exact_certificate": candidate.json_roundtrip(candidate.exact_certificate_section()),
            "exact_slice": candidate.json_roundtrip(candidate.exact_slice_section()),
            # Derived from the committed physical-benchmark light spectrum (the M_I/M_GUT compiler point is slow).
            "hierarchy": candidate.json_roundtrip(candidate.hierarchy_section(physical_states)),
            "rg_anchor_consistency": candidate.json_roundtrip(candidate.rg_anchor_section(physical_states)),
            "light_doublet_quartic": candidate.json_roundtrip(candidate.light_doublet_quartic_section()),
        }
        cls.compiler = candidate.json_roundtrip(candidate.compiler_point_audit(candidate.R0, spectrum=True))

    def _flag_inputs(self) -> dict[str, Any]:
        report = self.committed
        points = list(report["compiler"].values())
        coloured = [
            label
            for row in points
            for state in row["light_spectrum"]["states"]
            for label in state["sm_content_real"]
            if not label.startswith("(1,")
        ]
        return {
            "embedding": report["sm_embedding"],
            "certificate": report["exact_certificate"],
            "checks": report["checks"],
            "points": points,
            "splitting": report["compiler"]["1/5"]["h10"]["doublet_triplet_splitting"],
            "coloured_light": coloured,
            "rg": report["rg_anchor_consistency"],
            "hierarchy": report["hierarchy"],
            "quartic": report["light_doublet_quartic"],
            "equality_set": report["exact_certificate"]["equality_set"]["equality_set_certificate"],
        }

    def test_status_and_fail_closed_flags(self) -> None:
        report = self.committed
        self.assertEqual(report["n_failed"], 0, report["failures"])
        self.assertEqual(
            report["status"],
            "SM_PATI_SALAM_G3_CANDIDATE__EXACT_GLOBAL_MINIMUM_OF_BENCHMARK_POTENTIAL__SM_UNBROKEN__G3_OPEN",
        )
        flags = report["flags"]
        for name in (
            "candidate_is_sm_vacuum",
            "target_unbroken_algebra_is_standard_model",
            "exactly_stationary",
            "hessian_psd_exact",
            "hessian_psd_kernel_is_symmetry_plus_tuned_light_doublet",
            "hessian_kernel_is_symmetry_when_O06_raised",
            "hessian_kernel_count_is_float64",
            "bfb_certified",
            "global_minimum_certified",
            # Bound to the committed G3_SM_PATI_SALAM_EQUALITY_SET_V20.json (modulo SO(10) x U(1)_X x U(1)_PQ).
            "equality_set_unique_modulo_symmetry_certified",
            "breaking_route_matches_rg_anchor",
        ):
            self.assertTrue(flags[name], name)
        for name in (
            # Literal: the kernel is symmetry + the tuned doublet, not symmetry alone.
            "hessian_psd_kernel_is_symmetry",
            "doublet_triplet_splitting_natural",
            "coloured_scalars_only_at_M_GUT",
            "rg_anchor_field_content_reproduced",
            "physical_benchmark_uses_canonical_phi17_scale",
            "higgs_mass_compatible",
            "electroweak_symmetry_breaking_realized",
            "realistic_yukawa_sector",
            "g3_closed",
            "whole_model_validated",
            "whole_model_excluded",
        ):
            self.assertFalse(flags[name], name)
        self.assertTrue(all(report["checks"].values()))
        self.assertEqual(report["n_checks"], len(report["checks"]))

    def test_flags_are_fail_closed(self) -> None:
        inputs = self._flag_inputs()
        self.assertEqual(candidate.report_flags(True, **inputs), self.committed["flags"])
        failed = candidate.report_flags(False, **inputs)
        self.assertEqual(
            {name for name, value in failed.items() if value},
            {"hessian_kernel_count_is_float64"},  # a descriptive limitation, not a claim
        )

    def test_equality_set_uniqueness_is_bound_to_the_committed_equality_report(self) -> None:
        loaded = candidate.load_equality_set_report()
        self.assertEqual(loaded["status"], candidate.EQUALITY_SET_PROVED_STATUS)
        self.assertEqual(loaded["n_failed"], 0)
        self.assertTrue(candidate.equality_set_certified(loaded))
        section = self.committed["exact_certificate"]["equality_set"]
        self.assertTrue(section["unique_modulo_symmetry_certified"])
        self.assertEqual(
            section["equality_set_certificate"],
            {
                "source": "g3_sm_pati_salam_equality_set_v20 (committed G3_SM_PATI_SALAM_EQUALITY_SET_V20.json)",
                "status": loaded["status"],
                "n_failed": 0,
            },
        )
        for text in ("SO(10) x U(1)_X x U(1)_PQ", "g3_sm_pati_salam_equality_set_v20", "accidental", "circle of orbits"):
            self.assertIn(text, section["unique_modulo_symmetry"])
        self.assertNotIn("uniqueness of the equality set", " ".join(self.committed["scope"]["open"]))
        self.assertIn("SO(10) x U(1)_X x U(1)_PQ", self.committed["verdict"])
        # The flag note names both unchecked parts of the equality-set proof.
        note = self.committed["flag_notes"]["equality_set_unique_modulo_symmetry_certified"]
        self.assertIn("classical theorems it cites are not machine-checked", note)
        self.assertIn("scope.elementary_not_machine_checked", note)
        self.assertIn("elementary_not_machine_checked", loaded["scope"])

    def test_exact_hessian_open_item_is_bound_to_the_committed_hessian_report(self) -> None:
        loaded = candidate.load_exact_hessian_report()
        self.assertTrue(candidate.exact_hessian_certified(loaded))
        proved, still_open = candidate.exact_hessian_scope_items(loaded)
        self.assertEqual(still_open, [])
        self.assertIn("447/39/0", proved[0])
        self.assertIn(proved[0], self.committed["scope"]["proved_exactly"])
        self.assertNotIn("exact (non-float) Hessian kernel/rank certificate", self.committed["scope"]["open"])
        # Fail closed: a missing or failed report keeps the item open and claims nothing.
        for report in ({}, {**loaded, "n_failed": 1}, {**loaded, "n_failed": False}, {**loaded, "status": "X"}):
            self.assertEqual(
                candidate.exact_hessian_scope_items(report), ([], ["exact (non-float) Hessian kernel/rank certificate"])
            )

    def test_equality_set_flag_is_false_when_the_equality_report_is_absent_or_failed(self) -> None:
        inputs = self._flag_inputs()
        proved = dict(inputs["equality_set"])
        self.assertTrue(candidate.report_flags(True, **inputs)["equality_set_unique_modulo_symmetry_certified"])
        for equality_report in (
            {},
            {**proved, "n_failed": 1},
            {**proved, "n_failed": None},
            {**proved, "n_failed": False},
            {**proved, "status": "G3_SM_PATI_SALAM_EQUALITY_SET_AUDIT_FAILED"},
            {"n_failed": 0},
        ):
            self.assertFalse(candidate.equality_set_certified(equality_report), equality_report)
            flags = candidate.report_flags(True, **{**inputs, "equality_set": equality_report})
            self.assertFalse(flags["equality_set_unique_modulo_symmetry_certified"], equality_report)
            section = candidate.equality_set_section(equality_report)
            self.assertFalse(section["unique_modulo_symmetry_certified"])
            self.assertEqual(section["unique_modulo_symmetry"], "open (numerical evidence in numerical_global_search)")
            self.assertEqual(section["conditions"], self.committed["exact_certificate"]["equality_set"]["conditions"])
        missing = candidate.load_equality_set_report(candidate.ROOT / "NO_SUCH_EQUALITY_SET_REPORT.json")
        self.assertEqual(missing, {})
        self.assertFalse(candidate.equality_set_certified(missing))

    def test_equality_set_loader_is_fail_closed_on_unreadable_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            for name, content in (
                ("not_utf8.json", b"\xff"),
                ("not_json.json", b"{not json"),
                ("not_a_dict.json", b"[1, 2]"),
            ):
                path = Path(directory) / name
                path.write_bytes(content)
                loaded = candidate.load_equality_set_report(path)
                self.assertEqual(loaded, {}, name)
                self.assertFalse(candidate.equality_set_certified(loaded), name)

    def test_coefficient_map_is_the_historical_map_with_the_stated_changes(self) -> None:
        exact = candidate.candidate_coefficients()
        self.assertEqual(len(exact), 27)
        self.assertTrue(all(isinstance(value, Fraction) for value in exact.values()))
        self.assertEqual(exact, candidate.expanded_sos_coefficient_map())
        self.assertEqual(exact["lambda::O27_B03_126bar_self_projectors"], Fraction(1, 8))
        self.assertEqual(exact["lambda::O27_B04_126bar_self_projectors"], Fraction(17, 128))
        self.assertEqual(exact["lambda::O05_B01_126bar_norm"], Fraction(1, 8) * (4 - 2 * Fraction(1, 25)))
        self.assertEqual(exact["lambda::O06_B01_Hdag_H_norm"], Fraction(1, 50))
        self.assertEqual(exact["re::O12_B01_Hdag_Hdag_pair"], Fraction(-1, 20))
        section = self.fresh["candidate"]
        self.assertEqual(
            [row["parameter"] for row in section["changes_from_historical_h0"]],
            [
                "lambda::O05_B01_126bar_norm",
                "lambda::O06_B01_Hdag_H_norm",
                "lambda::O27_B03_126bar_self_projectors",
                "lambda::O27_B04_126bar_self_projectors",
                "re::O12_B01_Hdag_Hdag_pair",
            ],
        )
        self.assertTrue(section["historical_parse_matches_exact_sos_laurent_map"])
        self.assertTrue(section["historical_parse_matches_float_evaluation"])
        self.assertTrue(section["H_linear_portals_zero"])
        self.assertTrue(section["all_parameters_in_exact_X_contract"])
        other = candidate.candidate_coefficients(Fraction(1, 100), Fraction(3), Fraction(-1, 300))
        self.assertEqual(other["lambda::O06_B01_Hdag_H_norm"], Fraction(2, 30000))
        self.assertEqual(other, candidate.expanded_sos_coefficient_map(Fraction(1, 100), Fraction(3), Fraction(-1, 300)))

    def test_unbroken_algebra_is_exactly_the_standard_model(self) -> None:
        embedding = self.fresh["sm_embedding"]
        self.assertTrue(embedding["binding"]["bound"])
        self.assertTrue(embedding["candidate_is_sm_vacuum"])
        self.assertTrue(embedding["target_unbroken_algebra_is_standard_model"])
        pair = embedding["heavy_pair_stabilizer"]
        self.assertEqual(pair["stabilizer_dimension"], 12)
        self.assertEqual(pair["centre_dimension"], 1)
        self.assertEqual(pair["derived_algebra_dimension"], 11)
        self.assertEqual(pair["centre_proportional_to"], ["Y_standard"])
        self.assertEqual(pair["centre_spectrum_on_vector_10"]["colour_block_0_5"], {"1/3": 6})
        self.assertEqual(pair["centre_spectrum_on_vector_10"]["weak_block_6_9"], {"1/2": 4})
        self.assertEqual(embedding["phi_p_alone"]["stabilizer_dimension"], 21)
        self.assertEqual(embedding["sigma_std_alone"]["label"], "SU(5)")
        self.assertFalse(embedding["old_orientation_p_delta_r"]["is_sm_type"])
        self.assertEqual(embedding["sigma_std_exact_charges"]["Y"], "0")
        self.assertEqual(embedding["sigma_std_exact_charges"]["T3R"], "1")
        self.assertLess(embedding["sigma_std_equals_minus_conj_hsigma_delta_r_form"]["alignment_defect"], 1.0e-12)
        self.assertTrue(embedding["full_state_stabilizer_so10_plus_u1x"]["u1x_broken"])

    def test_exact_sos_certificate_gives_the_global_minimum(self) -> None:
        certificate = self.fresh["exact_certificate"]
        self.assertTrue(all(certificate["checks"].values()), certificate["checks"])
        self.assertTrue(certificate["bfb_certified"])
        self.assertTrue(certificate["global_minimum_certified"])
        self.assertTrue(certificate["symbolic_identity"]["all_residuals_zero"])
        self.assertTrue(all(certificate["rational_point_identity"].values()))
        sigma = certificate["exact_sigma_std"]
        self.assertEqual(sigma["projector_fractions"], {"54": "0", "1050bar": "0", "2772bar": "1", "4125": "0"})
        self.assertEqual(sigma["raw_norm_squared"], 16)
        self.assertEqual(sigma["M_p_sigma_minus_2_sigma_max_abs"], 0)
        self.assertEqual(sigma["C_p_sigma_max_abs"], 0)
        self.assertEqual(
            sigma["weighted_self_quartic_over_N2"],
            {"sigma_std_swapped": "1", "sigma_std_historical": "17/16", "delta_r_swapped": "49/48", "delta_r_historical": "25/24"},
        )
        self.assertEqual(certificate["lower_bound"]["V0_at_default"], "-20661/20000")
        self.assertEqual(candidate.lower_bound_v0(), Fraction(-20661, 20000))
        self.assertEqual(certificate["exact_quartic_bound"]["constant"], "1/167")
        for row in certificate["exact_HS_sector"].values():
            self.assertTrue(row["condition_holds_strictly"])

    def test_hs_sector_boundary_is_lambda_eff_zero(self) -> None:
        r0 = Fraction(1, 5)
        # Sharp bound: k^2 < 8 r0^2, i.e. lambda_eff = 2 - k^2/(4 r0^2) > 0.
        self.assertTrue(candidate.exact_hs_certificate(r0, -2 * r0)["condition_holds_strictly"])
        self.assertFalse(candidate.exact_hs_certificate(r0, -3 * r0)["condition_holds_strictly"])
        default = candidate.exact_hs_certificate(r0)
        self.assertEqual(default["margin_4r0_squared_minus_kappa_squared_over_2"], Fraction(127, 800))  # 4/25 - 1/800
        self.assertTrue(default["square_completion_identity_exact"])

    def test_exact_slice_is_stationary_at_the_vacuum(self) -> None:
        slice_section = self.fresh["exact_slice"]
        self.assertTrue(slice_section["gradient_vanishes_exactly"])
        self.assertTrue(slice_section["equals_V0"])
        self.assertEqual(slice_section["value_at_vacuum"], "-20661/20000")
        self.assertEqual(slice_section["slice_hessian_eigenvalues"], ["1/25", "1/4", "8/25", "201/25"])

    def test_compiler_point_at_r0_one_fifth(self) -> None:
        row = self.compiler
        self.assertLess(row["gradient_max_abs"], 1.0e-12)
        self.assertLess(abs(row["V_minus_V0"]), 1.0e-12)
        self.assertEqual(
            row["symmetry_ranks"],
            {"so10_orbit_rank": 33, "so10_plus_u1x_rank": 34, "so10_plus_u1x_plus_pq_rank": 35},
        )
        projected = row["projected_hessian"]
        self.assertEqual(projected["dimension"], 451)
        self.assertEqual(projected["n_negative"], 0)
        self.assertEqual(projected["n_zero"], 4)
        self.assertAlmostEqual(projected["zero_modes_weight_in_light_doublet_real_directions"], 1.0, places=10)
        self.assertAlmostEqual(projected["min_massive_over_r0_squared"], 1 / 96, places=10)
        self.assertEqual(row["all_massive_variant"]["n_zero"], 0)
        self.assertTrue(row["kernel_is_symmetry_plus_light_doublet"])
        self.assertLess(row["sm_generators_annihilate_vacuum"], 1.0e-12)
        spectrum = row["labelled_spectrum"]
        self.assertEqual(
            spectrum["symmetry_tangents"]["sm_content_real"],
            {"(1,1)_|Y|=0": 3, "(1,1)_|Y|=1": 2, "(3,1)_|Y|=2/3": 6, "(3,2)_|Y|=1/6": 12, "(3,2)_|Y|=5/6": 12},
        )
        self.assertEqual(sum(cluster["real_multiplicity"] for cluster in spectrum["clusters"]), 451)
        lightest = spectrum["clusters"][0]
        self.assertEqual(lightest["sm_content_real"], {"(1,2)_|Y|=1/2": 4})
        self.assertEqual(lightest["field_weights"], {"H10": 1.0})
        h10 = row["h10"]
        eigenvalues = {key: [(g["mass_squared"], g["real_multiplicity"]) for g in value] for key, value in h10["real_block_eigenvalues"].items()}
        np.testing.assert_allclose([value for value, _ in eigenvalues["colour_x"]], [1.0], atol=1.0e-12)
        np.testing.assert_allclose([value for value, _ in eigenvalues["colour_y"]], [1.04], atol=1.0e-12)
        np.testing.assert_allclose([value for value, _ in eigenvalues["weak_x"]], [0.0], atol=1.0e-12)
        np.testing.assert_allclose([value for value, _ in eigenvalues["weak_y"]], [0.04], atol=1.0e-12)
        self.assertEqual([count for _, count in eigenvalues["colour_x"]], [6])
        self.assertEqual([count for _, count in eigenvalues["weak_x"]], [4])
        self.assertLess(h10["H_block_decoupled_from_other_fields"], 1.0e-12)
        self.assertLess(h10["wedge_combination_(3/5)O46_1-O46_54"]["hermitian_matrix_minus_diag_1x6_0x4"], 1.0e-12)

    def test_doublet_triplet_splitting_is_tuned_and_10H_only(self) -> None:
        splitting = self.compiler["h10"]["doublet_triplet_splitting"]
        self.assertFalse(splitting["natural"])
        self.assertIn("not automatic", splitting["mechanism"])
        self.assertLess(splitting["per_unit_max_deviation_from_exact"], 1.0e-12)
        exact_unit = {
            candidate.O46_1_ID: {"colour": Fraction(1), "weak": Fraction(1)},
            candidate.O46_54_ID: {"colour": Fraction(-2, 5), "weak": Fraction(3, 5)},
        }
        self.assertEqual(
            splitting["phi_induced_mass_per_unit_coefficient_exact"],
            candidate.json_roundtrip(exact_unit),
        )
        coefficients = candidate.candidate_coefficients()

        def doublet_mass(values: dict[str, Fraction]) -> Fraction:
            return sum(values[key] * exact_unit[key]["weak"] for key in exact_unit)

        self.assertEqual(doublet_mass(coefficients), 0)
        detuned = dict(coefficients)
        detuned[candidate.O46_1_ID] += Fraction(1, 1000)
        self.assertEqual(doublet_mass(detuned), Fraction(1, 1000))  # a generic ratio gives GUT-scale doublets
        self.assertEqual(splitting["doublet_phi_induced_mass_squared"]["value_at_candidate"], "0")
        self.assertEqual(splitting["triplet_phi_induced_mass_squared"]["value_at_candidate"], "1")
        self.assertEqual(len(splitting["tuned_relations"]), 3)
        self.assertAlmostEqual(splitting["doublet_composition"]["light_doublet_weight_in_span_z4_z5"], 0.5, places=12)
        self.assertTrue(any("doublet-triplet splitting is tuned" in item for item in self.committed["scope"]["open"]))

    def test_light_spectrum_and_sub_M_I_coloured_states(self) -> None:
        light = self.compiler["light_spectrum"]
        self.assertEqual(light["real_dimension"], 60)
        self.assertEqual(light["states"][0]["mass_over_r0_M_GUT"], 0.0)  # tuned doublet, noise floored
        content: dict[str, int] = {}
        for state in light["states"]:
            for label, count in state["sm_content_real"].items():
                content[label] = content.get(label, 0) + count
        self.assertEqual(
            content,
            {
                "(1,1)_|Y|=0": 2,
                "(1,1)_|Y|=2": 2,
                "(1,2)_|Y|=1/2": 8,
                "(3,1)_|Y|=1/3": 6,
                "(3,1)_|Y|=4/3": 6,
                "(6,1)_|Y|=1/3": 12,
                "(6,1)_|Y|=2/3": 12,
                "(6,1)_|Y|=4/3": 12,
            },
        )
        phi17 = self.compiler["Phi17_block"]
        self.assertLess(phi17["coupling_to_other_fields_max_abs"], 1.0e-12)
        self.assertEqual(phi17["exact_radial_mass_squared_x0_squared_over_8"], "1/8")
        masses = self.committed["hierarchy"]["tree_masses_GeV_at_physical_r0"]
        self.assertIn("H10_colour_triplets", masses)
        self.assertNotIn("colour_triplets", masses)
        below = self.committed["hierarchy"]["coloured_states_below_M_I"]
        labels = {label for row in below for label in row["sm_content_real"]}
        self.assertEqual(labels, {"(3,1)_|Y|=1/3", "(3,1)_|Y|=4/3", "(6,1)_|Y|=1/3", "(6,1)_|Y|=2/3", "(6,1)_|Y|=4/3"})
        self.assertTrue(all(row["mass_over_M_I"] < 0.35 for row in below))
        self.assertIn("ILLUSTRATIVE", self.committed["hierarchy"]["status"])
        self.assertFalse(self.committed["hierarchy"]["benchmark_uses_canonical_phi17_scale"])

    def test_light_state_order_ignores_float_noise_within_a_mass_level(self) -> None:
        def state(value_over_r2: float, content: dict[str, int], r2: float = 4.0e-9) -> dict[str, Any]:
            return {
                "mass_squared": value_over_r2 * r2,
                "mass_squared_over_r0_squared": value_over_r2,
                "sm_content_real": content,
            }

        doublet = state(-1.1e-16, {"(1,2)_|Y|=1/2": 4})
        sextet = {"(6,1)_|Y|=4/3": 12}
        singlet = {"(1,1)_|Y|=2": 2}
        expected_labels = [{"(1,2)_|Y|=1/2": 4}, singlet, sextet, {"(3,1)_|Y|=1/3": 6}, {"(1,1)_|Y|=0": 1}]
        # Degenerate noise of either sign (up to ~1e-5 in m^2/r0^2 at the physical r0) and any input order.
        for noise in (-8.4e-10, 8.4e-10, -1.0e-5, 1.0e-5):
            rows = [
                state(0.5, {"(1,1)_|Y|=0": 1}),
                state(1 / 96 + noise, singlet),
                state(0.059, {"(3,1)_|Y|=1/3": 6}),
                state(1 / 96, sextet),
                doublet,
            ]
            for ordering in (rows, rows[::-1]):
                ordered = candidate.order_light_states(ordering)
                self.assertEqual([row["sm_content_real"] for row in ordered], expected_labels, noise)
                self.assertIs(ordered[0], doublet)

    def test_endpoint_classification_is_convergence_aware(self) -> None:
        exact = {
            "Phi_norm_squared": 1.0,
            "V_Phi_plus_1": 0.0,
            "N_Sigma": 0.0025,
            "Sigma_purity_defect": 0.0,
            "A_shift_norm": 0.0,
            "C_norm": 0.0,
            "S_abs": 0.05,
            "Phi17_abs": 1.0,
            "N_H": 0.0,
        }
        sm_stabilizer = {"largest_kernel_singular_value": 0.0, "stabilizer_dimension": 12, "hypercharge_type_centre": True}
        test = candidate.endpoint_orbit_test(0.0, exact, sm_stabilizer, 0.05, 1.0)
        self.assertEqual(test["classification"], "on_orbit")
        # The run-dependent r0 = 1/20 endpoint of a fresh rebuild: gap 1.58e-12, purity defect 2.4e-5, kernel
        # singular value 6.2e-4 = 0.0124 r0 (above the old fixed 1e-2 r0 cut), consistent with its soft-mode
        # displacement eps = sqrt(96 gap)/r0^2 ~ 4.9e-3.
        fresh = {**exact, "Sigma_purity_defect": 2.4e-5, "N_H": 5.0e-7, "N_Sigma": 0.0025 * (1 + 1.0e-4)}
        noisy_stabilizer = {**sm_stabilizer, "largest_kernel_singular_value": 6.2e-4}
        test = candidate.endpoint_orbit_test(1.58e-12, fresh, noisy_stabilizer, 0.05, 1.0)
        self.assertEqual(test["classification"], "on_orbit")
        self.assertAlmostEqual(test["soft_relative_displacement"], (96 * 1.58e-12) ** 0.5 / 0.05**2, places=12)
        # Not converged enough: inconclusive, never a failure, whatever the residuals.
        for r0, gap in ((0.2, 2.0e-11), (0.05, 7.0e-12)):
            test = candidate.endpoint_orbit_test(gap, {**exact, "N_Sigma": r0**2, "S_abs": r0}, sm_stabilizer, r0, 1.0)
            self.assertFalse(test["reached"])
            self.assertEqual(test["classification"], "inconclusive")
        # Converged but far outside the soft-mode tolerance, or with a non-SM stabilizer: off_orbit.
        for invariants, stabilizer in (
            ({**exact, "Sigma_purity_defect": 0.3}, sm_stabilizer),
            ({**exact, "A_shift_norm": 0.01}, sm_stabilizer),
            (exact, {**sm_stabilizer, "stabilizer_dimension": 15}),
            (exact, {**sm_stabilizer, "hypercharge_type_centre": False}),
        ):
            self.assertEqual(candidate.endpoint_orbit_test(1.0e-13, invariants, stabilizer, 0.05, 1.0)["classification"], "off_orbit")
        self.assertEqual(
            candidate.classification_summary(
                [{"orbit_classification": name} for name in ("on_orbit", "inconclusive", "on_orbit")]
            ),
            {
                "endpoint_classification_counts": {"on_orbit": 2, "inconclusive": 1, "off_orbit": 0},
                "all_converged_endpoints_on_sm_vacuum_orbit": True,
            },
        )
        for rows in ([{"orbit_classification": "inconclusive"}], [{"orbit_classification": "off_orbit"}]):
            self.assertFalse(candidate.classification_summary(rows)["all_converged_endpoints_on_sm_vacuum_orbit"])
        # The exact vacuum through the full endpoint pipeline.
        fast = candidate.fast_potential()
        vacuum = chart.pack(candidate.candidate_state())
        gap = fast.value(vacuum) - float(candidate.lower_bound_v0())
        endpoint = candidate.classify_endpoint(fast, vacuum, 0.2, 1.0, gap=gap)
        self.assertEqual(endpoint["orbit_classification"], "on_orbit")
        self.assertTrue(endpoint["orbit_test"]["stabilizer_sm_type"])

    def test_rg_anchor_field_content_is_not_reproduced(self) -> None:
        rg = self.fresh["rg_anchor_consistency"]
        self.assertTrue(rg["anchor_betas_reproduced_from_field_content"])
        self.assertTrue(rg["anchor_reproduced_by_local_chain"])
        self.assertEqual(candidate.ps_one_loop_b(candidate.ANCHOR_PS_SCALARS), (Fraction(-7, 3), Fraction(2), Fraction(26, 3)))
        self.assertEqual(candidate.sm_one_loop_b(2), (Fraction(21, 5), Fraction(-3), Fraction(-7)))
        self.assertEqual(candidate.ps_one_loop_b(candidate.CANDIDATE_PS_SCALARS), (Fraction(-23, 3), Fraction(-3), Fraction(11, 3)))
        self.assertEqual(candidate.sm_one_loop_b(1), (Fraction(41, 10), Fraction(-19, 6), Fraction(-7)))
        self.assertFalse(rg["field_content_reproduced"])
        self.assertEqual(len(rg["sub_M_I_thresholds"]), 6)
        anchor_ratio = self.committed["hierarchy"]["anchor"]["ratio_float"]
        solution = rg["one_loop_solutions"]["candidate_content_with_1HDM_and_sub_M_I_remnants"]
        self.assertTrue(solution["solved"])
        self.assertLess(solution["M_I_over_M_GUT"], anchor_ratio / 10.0)

    def test_light_doublet_quartic(self) -> None:
        for label, r0 in candidate.benchmark_r0_values().items():
            self.assertEqual(candidate.exact_light_doublet_quartic(r0)["lambda_eff"], Fraction(127, 64), label)
        compiler = self.compiler["light_doublet_quartic"]
        for row in compiler["directions"].values():
            self.assertAlmostEqual(row["lambda_direct"], 2.0, places=9)
            self.assertAlmostEqual(row["lambda_eff"], 127 / 64, places=9)
            self.assertLess(row["coupling_outside_Re_S_max_abs"], 1.0e-12)
        quartic = self.fresh["light_doublet_quartic"]
        running = quartic["conditional_sm_running"]
        self.assertLess(running["lambda_M_I_required_for_sm_two_loop"], 0.0)
        self.assertGreater(running["predictions"]["lambda_eff_127_over_64"]["m_h_tree_GeV"], 180.0)
        self.assertFalse(quartic["higgs_mass_compatible"])

    def test_fast_sos_evaluator_matches_the_compiler_at_the_vacuum(self) -> None:
        fast = candidate.fast_potential()
        vacuum = chart.pack(candidate.candidate_state())
        value, gradient = fast.value_grad(vacuum)
        v0 = float(candidate.lower_bound_v0())
        self.assertLess(abs(value - v0), 1.0e-13)
        self.assertLess(float(np.max(np.abs(gradient))), 1.0e-12)
        self.assertLess(abs(value - self.compiler["V_compiler"]), 1.0e-12)
        rng = np.random.default_rng(7)
        start = vacuum + 1.0e-2 * rng.normal(size=chart.TOTAL_DIM)
        end, _ = candidate.local_minimize(fast, start, maxiter=4000)
        self.assertGreater(fast.value(end) - v0, -1.0e-12)
        self.assertLess(fast.value(end) - v0, 1.0e-9)

    def test_committed_heavy_sections_are_consistent(self) -> None:
        report = self.committed
        self.assertEqual(sorted(report["compiler"]), sorted(["1/5", "1/100", "1/1000", "M_I/M_GUT"]))
        for label, row in report["compiler"].items():
            self.assertLess(row["gradient_max_abs"], 1.0e-12, label)
            self.assertEqual(row["symmetry_ranks"]["so10_plus_u1x_plus_pq_rank"], 35, label)
            self.assertEqual(row["projected_hessian"]["n_negative"], 0, label)
            self.assertEqual(row["projected_hessian"]["n_zero"], 4, label)
            self.assertEqual(row["all_massive_variant"]["n_zero"], 0, label)
            self.assertLess(row["projected_hessian"]["min_massive_absolute_deviation"], 1.0e-12, label)
            self.assertTrue(row["kernel_is_symmetry_plus_light_doublet"], label)
            self.assertEqual(row["light_spectrum"]["real_dimension"], 60, label)
            # The tuned doublet's float-noise eigenvalue is floored to an exact zero mass, not sqrt-amplified.
            states = row["light_spectrum"]["states"]
            doublet = states[0]
            self.assertEqual(doublet["sm_content_real"], {"(1,2)_|Y|=1/2": 4}, label)
            self.assertLess(abs(doublet["mass_squared"]), candidate.NUMERICAL_ZERO_EIGENVALUE, label)
            self.assertEqual(doublet["mass_over_r0_M_GUT"], 0.0, label)
            # Run-independent order: the exactly degenerate r0^2/96 level is ordered by SM label, not float noise.
            self.assertEqual(candidate.order_light_states(states), states, label)
            self.assertEqual(
                [state["sm_content_real"] for state in states[1:3]],
                [{"(1,1)_|Y|=2": 2}, {"(6,1)_|Y|=4/3": 12}],
                label,
            )
            self.assertLess(row["Phi17_block"]["coupling_to_other_fields_max_abs"], 1.0e-12, label)
            self.assertLess(row["Phi17_block"]["radial_deviation_from_exact"], 1.0e-12, label)
        self.assertAlmostEqual(
            report["compiler"]["M_I/M_GUT"]["r0_float"], report["hierarchy"]["anchor"]["ratio_float"], places=15
        )
        search = report["numerical_global_search"]
        self.assertTrue(search["nothing_found_below_V0"])
        self.assertGreater(search["lowest_gap_found_any_method"], -1.0e-10)
        self.assertLess(search["fast_evaluator_validation"]["max_relative_value_difference"], 1.0e-11)
        self.assertLess(search["fast_evaluator_validation"]["compiler_gradient_check"]["gradient_max_abs_difference"], 1.0e-8)
        self.assertTrue(search["quartic_directions"]["lowest_at_or_above_exact_bound"])
        for run in search["random_start_local_minimization"].values():
            self.assertGreater(run["lowest_final_gap"], -1.0e-10)
        competitors = search["structured_competitors_r0_1_5"]
        # Convergence-aware endpoint classification: no converged endpoint off the SM vacuum orbit, and every
        # recorded class follows from the recorded gap, invariants and stabilizer.
        runs = search["random_start_local_minimization"]
        endpoints = [(float(Fraction(label.split("=", 1)[1])), row) for label, run in runs.items() for row in run["starts"]]
        endpoints += [(0.2, row["local_minimization_from_perturbed_optimum"]) for row in competitors.values()]
        for r0, row in endpoints:
            test = candidate.endpoint_orbit_test(row["final_gap"], row["invariants"], row["heavy_pair_stabilizer"], r0, 1.0)
            self.assertEqual(test["classification"], row["orbit_classification"])
            self.assertIn(row["orbit_classification"], candidate.ORBIT_CLASSES)
        for label, run in runs.items():
            counts = run["endpoint_classification_counts"]
            self.assertEqual(sum(counts.values()), len(run["starts"]), label)
            self.assertEqual(counts["off_orbit"], 0, label)
            self.assertTrue(run["all_converged_endpoints_on_sm_vacuum_orbit"], label)
            self.assertTrue(run["no_endpoint_below_V0"], label)
        classification = search["endpoint_classification"]
        self.assertEqual(sum(classification["endpoint_classification_counts"].values()), len(endpoints))
        self.assertEqual(classification["endpoint_classification_counts"]["off_orbit"], 0)
        self.assertTrue(classification["all_converged_endpoints_on_sm_vacuum_orbit"])
        self.assertTrue(classification["no_endpoint_below_V0"])
        self.assertAlmostEqual(competitors["p|delta_R"]["compiler_gap"], 0.2**4 / 392, delta=1.0e-12)
        self.assertAlmostEqual(competitors["p|Sigma=0"]["compiler_gap"], 0.2**4 / 8, delta=1.0e-12)
        self.assertAlmostEqual(competitors["p|flipped"]["compiler_gap"], 0.0, delta=1.0e-12)
        for row in search["exact_slice_vs_compiler"]:
            self.assertLess(abs(row["compiler_minus_exact"]), 1.0e-12)

    def test_committed_artifact_matches_fresh_report(self) -> None:
        for key, fresh in self.fresh.items():
            self.assertEqual(target.report_mismatches(self.committed[key], fresh, key), [])
        committed = _strip_timing(self.committed["compiler"]["1/5"])
        fresh = _strip_timing(self.compiler)
        self.assertEqual(target.report_mismatches(committed, fresh, "compiler.1/5", abs_tol=1.0e-11), [])


if __name__ == "__main__":
    unittest.main()
