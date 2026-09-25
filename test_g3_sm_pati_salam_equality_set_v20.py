#!/usr/bin/env python3
"""Tests for the exact equality set of the SM Pati-Salam G3 candidate (v20).

setUpClass builds one fresh report: the exact certificates plus the float64
corroboration, about one minute.  It is compared with the committed artifact
through target.report_mismatches.  Exact leaves (strings, integers, booleans)
must match exactly; the float64 corroboration only has to match within a loose
tolerance.  The mutation tests rebuild the exact sections, which are
lru_cached, from one corrupted input each and require the report to fail
closed: status ending in __OPEN and no theorem claimed.
"""
from __future__ import annotations

import json
import unittest
from fractions import Fraction
from typing import Any
from unittest import mock

import numpy as np
import sympy
from scipy import sparse

import g3_candidate_physical_target_audit_v20 as target
import g3_sm_pati_salam_candidate_v20 as candidate
import g3_sm_pati_salam_equality_set_v20 as equality

TIMING_KEYS = {"seconds", "runtime_seconds"}


def _strip_timing(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _strip_timing(item) for key, item in value.items() if key not in TIMING_KEYS}
    if isinstance(value, list):
        return [_strip_timing(item) for item in value]
    return value


class SmPatiSalamEqualitySetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.committed = json.loads(equality.OUT_JSON.read_text(encoding="utf-8"))
        cls.fresh = equality.json_roundtrip(equality.build_report())

    # ------------------------------------------------------------------
    # The theorem and its checks.
    # ------------------------------------------------------------------

    def test_all_checks_pass_and_theorem_is_claimed(self) -> None:
        for report in (self.committed, self.fresh):
            self.assertEqual(report["n_failed"], 0, report["failures"])
            self.assertEqual(report["n_checks"], len(report["checks"]))
            self.assertTrue(all(report["checks"].values()))
            self.assertEqual(report["status"], equality.STATUS_PROVED)
            self.assertTrue(report["theorem_claimed"])
            self.assertEqual(report["theorem"], equality.THEOREM)
            self.assertTrue(report["flags"]["equality_set_unique_modulo_symmetry_certified"])
            self.assertTrue(report["flags"]["exact_210_uniqueness_of_global_orbit_certified"])
            self.assertTrue(report["corollary_exact_210"]["uniqueness_of_global_orbit"])
            self.assertTrue(report["flags"]["uniqueness_is_modulo_G_including_accidental_U1_PQ"])
            for name in (
                "unique_modulo_SO10_x_U1X_alone",
                "kappa_squared_equal_8_r0_squared_claimed",
                "candidate_wired_into_g3_gate",
                "g3_closed",
                "whole_model_validated",
                "whole_model_excluded",
            ):
                self.assertFalse(report["flags"][name], name)

    def test_theorem_claimed_only_when_no_check_fails(self) -> None:
        for report in (self.committed, self.fresh):
            self.assertEqual(report["theorem_claimed"], report["n_failed"] == 0)
            self.assertEqual(report["flags"]["theorem_claimed"], report["n_failed"] == 0)
            self.assertEqual(report["status"] == equality.STATUS_PROVED, report["n_failed"] == 0)

    def test_status_strings(self) -> None:
        # Proved: G3 itself stays open.  Not proved: the status ends in __OPEN (fail closed).
        self.assertTrue(equality.STATUS_PROVED.endswith("__G3_OPEN"))
        self.assertFalse(equality.STATUS_PROVED.endswith("__OPEN"))
        self.assertTrue(equality.STATUS_NOT_PROVED.endswith("__OPEN"))
        self.assertFalse(equality.STATUS_NOT_PROVED.endswith("__G3_OPEN"))

    def test_committed_artifact_matches_fresh_report(self) -> None:
        committed = _strip_timing(self.committed)
        fresh = _strip_timing(self.fresh)
        committed_numerics = committed.pop("numerical_corroboration")
        fresh_numerics = fresh.pop("numerical_corroboration")
        self.assertEqual(target.report_mismatches(committed, fresh), [])
        # float64 L-BFGS endpoints: booleans and integers exact, residuals within a loose tolerance.
        self.assertEqual(
            target.report_mismatches(
                committed_numerics, fresh_numerics, "numerical_corroboration", rel_tol=1.0e-6, abs_tol=1.0e-4
            ),
            [],
        )

    def test_markdown_artifact_states_the_status(self) -> None:
        text = equality.OUT_MD.read_text(encoding="utf-8")
        self.assertIn(self.committed["status"], text)
        self.assertIn("Cited classical theorems", text)
        self.assertIn("circle of orbits", text)

    def test_theorem_states_its_qualifiers(self) -> None:
        # Scope of the flag: modulo G including the accidental U(1)_PQ; SOS form; 25 parameters at kappa = 0.
        for text in (equality.THEOREM, self.fresh["verdict"], self.fresh["scope"]["proved_exactly"][0]):
            self.assertIn("adapted SOS form", text)
            self.assertIn("float64 end to end", text)
        for text in (equality.THEOREM, self.fresh["verdict"]):
            self.assertIn("circle of orbits", text)
            self.assertIn("accidental", text)
            self.assertIn("25 nonzero", text)
        self.assertTrue(
            any("circle of orbits" in item and "U(1)_PQ" in item for item in self.fresh["scope"]["not_proved_or_out_of_scope"])
        )

    def test_verdict_names_every_cited_theorem(self) -> None:
        # The verdict's cited-theorem list is rendered from CITED_THEOREMS, so it cannot omit a cited result.
        used = [row for row in equality.CITED_THEOREMS if not row["used_in"].startswith("NOT")]
        self.assertEqual(equality.cited_theorem_short_names(), [row["short_name"] for row in used])
        self.assertTrue(any("Humphreys" in name for name in equality.cited_theorem_short_names()))
        for report in (self.committed, self.fresh):
            for name in equality.cited_theorem_short_names():
                self.assertIn(name, report["verdict"])
            self.assertNotIn("U(5)-invariant 4-forms", report["verdict"])
            self.assertEqual(report["scope"]["cited_not_machine_checked"], [row["result"] for row in used])
            self.assertEqual(len(report["scope"]["cited_not_machine_checked"]), 6)

    def test_sos_dependency_does_not_read_this_report(self) -> None:
        # The candidate is built with equality_report={}: it must not read this module's own committed report.  A
        # self-reading build would embed the candidate's bound "exact: ..." text instead of its unbound "open ..." text.
        unbound = candidate.equality_set_section({})["unique_modulo_symmetry"]
        self.assertTrue(unbound.startswith("open"))
        for report in (self.committed, self.fresh):
            p0 = report["sos_decomposition"]
            self.assertNotIn("candidate_recorded_unique_modulo_symmetry", p0)
            self.assertEqual(p0["candidate_unbound_unique_modulo_symmetry"], unbound)
            self.assertIn("before binding to this report", p0["candidate_unbound_unique_modulo_symmetry_note"])

    def test_elementary_steps_are_all_listed(self) -> None:
        # Several elementary steps are argued in the text, not computed; the report and docstring must not claim one.
        docstring = " ".join(equality.__doc__.split())
        self.assertIn("elementary steps argued in the text (not machine-checked)", docstring)
        self.assertNotIn("The one elementary step", docstring)
        for report in (self.committed, self.fresh):
            first = report["scope"]["proved_exactly"][0]
            self.assertIn("elementary steps argued in the text (not machine-checked)", first)
            self.assertNotIn("only non-machine-checked", first)
            self.assertIn("elementary steps argued in the text (not machine-checked)", report["verdict"])
            steps = report["scope"]["elementary_not_machine_checked"]
            self.assertEqual(steps, list(equality.ELEMENTARY_STEPS))
            for needle in ("|H.H| <= N_H", "sign argument", "Gram-Schmidt", "connected groups", "U(5)", "Iwasawa"):
                self.assertTrue(any(needle in step for step in steps), needle)
            # The invariance of D is machine-checked now (P1_pluecker_tensors_intertwine_natural_actions).
            self.assertFalse(any("O(10)" in step.replace("SO(10)", "") or "Hilbert-Schmidt" in step for step in steps))
            self.assertTrue(report["checks"]["P1_pluecker_tensors_intertwine_natural_actions"])

    # ------------------------------------------------------------------
    # Exact numbers on the proof path.
    # ------------------------------------------------------------------

    def test_p0_projectors_are_orthogonal_and_complete(self) -> None:
        p0 = self.fresh["sos_decomposition"]
        self.assertTrue(p0["phi_sym2"]["minimal_polynomial"]["vanishes_on_sym2"])
        self.assertEqual(p0["phi_sym2"]["minimal_polynomial"]["sym2_basis_columns"], 22155)
        self.assertEqual(p0["phi_sym2"]["nodes"], [-4, 0, 2, 6, 12, 14, 16, 24])
        self.assertTrue(p0["sigma_sym2"]["minimal_polynomial"]["vanishes_on_sym2"])
        self.assertEqual(p0["sigma_sym2"]["minimal_polynomial"]["sym2_basis_columns"], 8001)
        self.assertEqual(
            p0["sigma_sym2"]["channel_dimensions_from_traces"],
            {"54": "54", "1050bar": "1050", "4125": "4125", "2772bar": "2772"},
        )
        self.assertEqual(p0["sigma_sym2"]["sym2_traces_tr_K^j_j=0..3"], ["8001", "-1575", "137025", "200025"])
        expansion = p0["eight_term_operator_expansion"]
        self.assertTrue(expansion["passes"])
        self.assertEqual(
            {sign: row["operators_compared"] for sign, row in expansion["by_kappa_sign"].items()},
            {"negative": 27, "positive": 27, "zero": 25},
        )
        for row in expansion["by_kappa_sign"].values():
            self.assertEqual(row["mismatched_operators"], {})
            self.assertEqual(row["unmapped_candidate_operators"], [])
            self.assertEqual(row["constant_plus_V0"], "0")
        self.assertEqual(
            expansion["W_prime_minus_N2_coefficients"],
            {"54": "1", "1050bar": "1", "2772bar": "0", "4125": "1/16"},
        )

    def test_p1_exact_numbers(self) -> None:
        p1 = self.fresh["P1_phi"]
        action = p1["chart_210_action"]
        self.assertTrue(action["chart_210_generators_equal_natural_Lambda4_action"])
        self.assertTrue(action["chart_basis_is_lexicographic_sorted_4_sets"])
        self.assertTrue(action["self210_moment_generators_equal_chart_generators"])
        self.assertEqual((action["generators_compared"], action["mismatched_generators"]), (45, []))
        self.assertEqual(p1["fit_points"], list(equality.FIT_POINTS))
        self.assertNotEqual(p1["fit_determinant_J0_J2_J3_J4"], "0")
        self.assertEqual(p1["racah_speiser_dim_Sym4_210_SO10_invariants"], 4)
        system = p1["equality_system"]
        self.assertTrue(system["square_4x4"])
        self.assertEqual(system["determinant"], "-1/258048000")
        self.assertEqual(system["solution_for_J0=1_I45=I210=I5940=0"], ["1", "24", "192", "3552"])
        self.assertEqual(system["J_at_p"], ["1", "24", "192", "3552"])
        self.assertEqual(
            system["matrix"][1:],
            [
                ["-117/1400", "51/22400", "-29/22400", "1/12800"],
                ["-19/100", "293/14400", "-3/1600", "1/57600"],
                ["-291/350", "353/5600", "-117/5600", "3/3200"],
            ],
        )
        defect = p1["pluecker_defect"]
        self.assertEqual(defect["coefficients_J0_J2_J3_J4"], ["-42/5", "33/40", "-7/40", "1/160"])
        self.assertEqual(defect["in_channel_basis_J0_I45_I210_I5940"], ["0", "-20", "18", "8"])
        self.assertEqual(defect["validation_failures"], [])
        self.assertGreaterEqual(defect["validation_points"], 8)
        invariance = defect["SO10_invariance_certificate"]
        self.assertTrue(invariance["D_is_SO10_invariant_under_the_natural_Lambda4_action"])
        self.assertEqual(invariance["generators_checked"], 45)
        self.assertEqual(invariance["tensor_nonzeros_iota_wedge"], [840, 1260])
        self.assertEqual(invariance["antisymmetric_lambda1_lambda3_lambda4_lambda5"], [True, True, True, True])
        self.assertEqual((invariance["iota_intertwining_failures"], invariance["wedge_intertwining_failures"]), ([], []))
        self.assertTrue(invariance["lambda1_action_is_the_vector_representation"])
        self.assertTrue(invariance["lambda4_action_is_natural_lambda4_generators"])
        named = p1["named_forms"]
        self.assertEqual(named["p = e6789"]["D_exact"], 0)
        self.assertEqual(named["(e0+e4)^(e1+e5)^e2^e3 (decomposable)"]["D_exact"], 0)
        self.assertEqual(named["e0123 + e4567"]["D_exact"], 8)
        self.assertEqual(named["(e01+e23+e45)^(e67+e89)"]["D_exact"], 84)
        self.assertEqual(p1["moments_M0_to_M7_at_p"], [1, 0, 24, 192, 3552, 61824, 1242240, 26397696])
        self.assertEqual(p1["stabilizer_of_p"]["dimension"], 21)
        self.assertEqual(
            p1["crossing_identities_M5_M6_M7_in_J_basis"]["M6"], ["408960", "-12360", "-3624", "514"]
        )

    def test_p2_exact_numbers(self) -> None:
        p2 = self.fresh["P2_sigma"]
        highest = p2["highest_weight"]
        self.assertEqual(highest["weyl_dimension_lambda"], "126")
        self.assertEqual(highest["weyl_dimension_2lambda"], "2772")
        self.assertTrue(highest["all_20_positive_root_vectors_annihilate_sigma_std"])
        self.assertEqual(p2["sym2_126bar"]["cartan_channel_kappa"], "-5")
        self.assertTrue(p2["sym2_126bar"]["K_sigma_sigma_equals_kappa_2772bar_sigma_sigma"])
        kahler = p2["kahler_identity_and_wirtinger"]
        self.assertEqual(kahler["constant_2_norm2"], "32")
        self.assertEqual(kahler["raw_sigma_norm_squared"], 16)
        self.assertEqual(kahler["p_dot_Omega"], 1)
        self.assertEqual(len(kahler["Omega_support_omega^2/2"]), 10)
        self.assertEqual(kahler["pfaffian_examples"]["e1023 (reversed orientation)"], -1)
        unitary = p2["unitary_line_stabiliser"]
        self.assertEqual(unitary["centraliser_of_J0_dimension"], 25)
        self.assertEqual(unitary["line_stabiliser_dimension"], 25)
        self.assertEqual(p2["equivariance"]["max_abs_integer_residual_M"], 0)
        self.assertEqual(p2["equivariance"]["max_abs_integer_residual_C"], 0)
        self.assertEqual(p2["M_p_spectrum"]["multiplicities_+2_-2_0"], ["30", "30", "66"])
        self.assertEqual(p2["equality_forces"], ["I_54 = 0", "I_1050bar = 0", "I_4125 = 0"])

    def test_p3_exact_numbers(self) -> None:
        p3 = self.fresh["P3_H_S_Phi17_phases"]
        charges = p3["charges"]
        self.assertEqual(charges["S_Phi17_charge_matrix_rows_X_PQ"], [[4, 17], [4, 0]])
        self.assertEqual(charges["determinant"], -68)
        self.assertEqual(
            charges["explicit_element_to_(p, r0 sigma_std, 0, r0 e^{ia}, x0 e^{ib})"],
            {"L01_angle": "a/2", "X_angle": "b/17", "PQ_angle": "a/4 - b/17"},
        )
        tangent = p3["tangent_rank"]
        self.assertEqual(
            (tangent["rank_so10"], tangent["rank_so10_plus_X"], tangent["rank_so10_plus_X_plus_PQ"], tangent["kernel_dimension"]),
            (33, 34, 35, 12),
        )
        self.assertEqual(p3["operators"]["count"], 27)
        self.assertEqual(p3["operators"]["count_at_kappa_0"], 25)
        self.assertEqual(
            p3["operators"]["vanishing_at_kappa_0"], ["lambda::O06_B01_Hdag_H_norm", "re::O12_B01_Hdag_Hdag_pair"]
        )
        self.assertEqual(p3["operators"]["phase_dependent_at_H0"], [])
        self.assertEqual(p3["HS_bracket_algebra"]["completed_square_residual"], "0")
        without = charges["without_PQ"]
        self.assertEqual(
            (without["X_invariant_phase_monomial"], without["X_charge"], without["PQ_charge"]), ("Phi17^4 conj(S)^17", 0, -68)
        )
        self.assertTrue(without["uniqueness_needs_PQ"])

    def test_numerical_corroboration_is_labelled_evidence(self) -> None:
        numerics = self.fresh["numerical_corroboration"]
        self.assertIn("evidence only", numerics["label"])
        self.assertTrue(numerics["consistent"])
        self.assertTrue(all(row["on_SO10_orbit_of_p"] for row in numerics["V_Phi_minimisations"]["runs"] if row["reached_minus_1"]))
        self.assertTrue(numerics["pure_elements_of_eig_2_at_p"]["control_fails_orbit_test"])
        self.assertLessEqual(numerics["wirtinger_sampling"]["random_max_<xi,omega^2/2>"], 1.0)
        self.assertIn("float64_evidence_only", self.fresh["scope"])

    # ------------------------------------------------------------------
    # Fail-closed mutations.
    # ------------------------------------------------------------------

    def _assert_fails_closed(self, report: dict[str, Any], *expected: str) -> None:
        self.assertGreater(report["n_failed"], 0)
        for name in expected:
            self.assertIn(name, report["failures"])
        self.assertFalse(report["theorem_claimed"])
        self.assertEqual(report["status"], equality.STATUS_NOT_PROVED)
        self.assertTrue(report["status"].endswith("__OPEN"))
        self.assertTrue(report["theorem"].startswith("NOT CLAIMED"))
        for flag in ("theorem_claimed", "equality_set_unique_modulo_symmetry_certified", "exact_210_uniqueness_of_global_orbit_certified"):
            self.assertFalse(report["flags"][flag], flag)

    def test_exact_only_build_with_recorded_inputs_claims_the_theorem(self) -> None:
        report = equality.build_report(d_coefficients=equality.RECORDED_D_COEFFICIENTS, numerical=False)
        self.assertEqual(report["n_failed"], 0, report["failures"])
        self.assertTrue(report["theorem_claimed"])

    def test_historical_self_weights_fail_closed(self) -> None:
        report = equality.build_report(self_weights=candidate.HISTORICAL_SELF_WEIGHTS, numerical=False)
        self._assert_fails_closed(
            report,
            "P0_eight_terms_expand_to_the_candidate_operator_map_with_constant_minus_V0",
            "P2_self_weights_force_sigma_purity",
            "P2_coefficient_map_uses_these_self_weights",
        )
        # The operator-level expansion sees the swap exactly on O27_B03 / O27_B04 (the 2772bar and 4125 weights).
        for row in report["sos_decomposition"]["eight_term_operator_expansion"]["by_kappa_sign"].values():
            self.assertEqual(
                set(row["mismatched_operators"]),
                {candidate.SELF_IDS["2772bar"], candidate.SELF_IDS["4125"]},
            )
        # W' - N^2 = I54 + I1050bar + I2772bar/16 + 0 * I4125: equality no longer forces I_4125 = 0.
        self.assertEqual(
            equality.json_roundtrip(report["P2_sigma"]["W_prime_minus_N2"]),
            {"54": "1", "1050bar": "1", "2772bar": "1/16", "4125": "0"},
        )
        self.assertNotIn("I_4125 = 0", report["P2_sigma"]["equality_forces"])

    def test_corrupted_pluecker_coefficient_fails_closed(self) -> None:
        corrupted = list(equality.RECORDED_D_COEFFICIENTS)
        corrupted[3] += Fraction(1, 1000)
        report = equality.build_report(d_coefficients=corrupted, numerical=False)
        self._assert_fails_closed(
            report, "P1_pluecker_defect_exact_J_combination_validated", "P1_pluecker_defect_vanishes_on_equality_set"
        )
        self.assertFalse(report["corollary_exact_210"]["uniqueness_of_global_orbit"])
        corrupted = list(equality.RECORDED_D_COEFFICIENTS)
        corrupted[0] += Fraction(1)
        report = equality.build_report(d_coefficients=corrupted, numerical=False)
        self._assert_fails_closed(report, "P1_pluecker_defect_exact_J_combination_validated")

    def test_kappa_outside_the_domain_fails_closed(self) -> None:
        r0 = Fraction(1, 5)
        # kappa^2 = 9 r0^2 > 8 r0^2.
        report = equality.build_report(hs_points=[(r0, -3 * r0)], numerical=False)
        self._assert_fails_closed(report, "P3_HS_domain_holds_strictly_at_sample_points")
        # The boundary kappa^2 = 8 r0^2 (kappa = 2 sqrt(2) r0, exact sympy) is not strict either.
        boundary = sympy.Rational(1, 5)
        report = equality.build_report(hs_points=[(boundary, -2 * sympy.sqrt(2) * boundary)], numerical=False)
        self._assert_fails_closed(report, "P3_HS_domain_holds_strictly_at_sample_points")
        # Inside the domain (kappa^2 = 4 r0^2) the step holds.
        report = equality.build_report(hs_points=[(r0, -2 * r0), (r0, 2 * r0)], numerical=False)
        self.assertEqual(report["n_failed"], 0, report["failures"])

    def test_non_natural_chart_210_action_fails_closed(self) -> None:
        # Conjugating by a sign flip of one basis 4-form keeps a representation with the same brackets, antisymmetry and
        # Casimir, so only the exact identification check can see it.
        signs = np.ones(210, dtype=np.int64)
        signs[equality.FOUR_INDEX[(0, 1, 2, 3)]] = -1
        flip = sparse.diags(signs, dtype=np.int64).tocsr()
        original = equality._phi_generators()
        conjugated = tuple((flip @ generator @ flip).tocsr() for generator in original)
        for first, second in ((0, 1), (3, 17), (20, 44)):
            lhs = conjugated[first] @ conjugated[second] - conjugated[second] @ conjugated[first]
            rhs = flip @ (original[first] @ original[second] - original[second] @ original[first]) @ flip
            self.assertTrue(equality._sparse_is_zero(lhs - rhs))
        data = equality.chart_210_action_data(conjugated)
        self.assertFalse(data["chart_210_generators_equal_natural_Lambda4_action"])
        self.assertGreater(len(data["mismatched_generators"]), 0)
        report = equality.build_report(chart_210_generators=conjugated, numerical=False)
        self._assert_fails_closed(
            report,
            "P1_chart_210_action_is_natural_on_Lambda4",
            "P1_pluecker_defect_exact_J_combination_validated",
            "P2_wirtinger_pfaffian_identity",
        )
        self.assertFalse(report["corollary_exact_210"]["uniqueness_of_global_orbit"])

    def test_corrupted_lambda5_action_fails_closed(self) -> None:
        # Negating the Lambda^5 action of L01 keeps it antisymmetric and integral, so only the wedge intertwining
        # identity can see it; the invariance of D, and with it the J-combination of D, is then not certified.
        natural = equality.natural_exterior_generators(5)
        corrupted = (-natural[0],) + tuple(natural[1:])
        data = equality.pluecker_intertwining_data({5: corrupted})
        self.assertFalse(data["D_is_SO10_invariant_under_the_natural_Lambda4_action"])
        self.assertEqual(data["antisymmetric_lambda1_lambda3_lambda4_lambda5"], [True, True, True, True])
        self.assertEqual((data["iota_intertwining_failures"], data["wedge_intertwining_failures"]), ([], ["L01"]))
        report = equality.build_report(pluecker_action_generators={5: corrupted}, numerical=False)
        self._assert_fails_closed(
            report, "P1_pluecker_tensors_intertwine_natural_actions", "P1_pluecker_defect_exact_J_combination_validated"
        )
        self.assertEqual(
            set(report["failures"]),
            {"P1_pluecker_tensors_intertwine_natural_actions", "P1_pluecker_defect_exact_J_combination_validated"},
        )
        self.assertFalse(report["corollary_exact_210"]["uniqueness_of_global_orbit"])
        self.assertEqual(report["parameters"]["pluecker_action_generators_override"], [5])
        # The cached natural actions are untouched by the mutation.
        self.assertTrue(equality.pluecker_intertwining_data()["D_is_SO10_invariant_under_the_natural_Lambda4_action"])

    def test_non_antisymmetric_or_malformed_pluecker_actions_fail_closed(self) -> None:
        # A symmetric corruption of one Lambda^3 generator breaks antisymmetry (and the iota identity).
        three = [matrix.copy() for matrix in equality.natural_exterior_generators(3)]
        three[5][0, 1] += 1
        three[5][1, 0] += 1
        data = equality.pluecker_intertwining_data({3: three})
        self.assertFalse(data["D_is_SO10_invariant_under_the_natural_Lambda4_action"])
        self.assertEqual(data["antisymmetric_lambda1_lambda3_lambda4_lambda5"], [True, False, True, True])
        self.assertGreater(len(data["iota_intertwining_failures"]), 0)
        # A missing generator or a non-natural Lambda^4 action fails closed without exceptions.
        short = equality.pluecker_intertwining_data({5: equality.natural_exterior_generators(5)[:44]})
        self.assertFalse(short["D_is_SO10_invariant_under_the_natural_Lambda4_action"])
        self.assertFalse(short["shapes_ok"])
        self.assertEqual(short["generators_checked"], 0)
        four = list(equality.natural_lambda4_generators())
        four[0], four[1] = four[1], four[0]
        swapped = equality.pluecker_intertwining_data({4: four})
        self.assertFalse(swapped["lambda4_action_is_natural_lambda4_generators"])
        self.assertFalse(swapped["D_is_SO10_invariant_under_the_natural_Lambda4_action"])

    def test_corollary_needs_the_sym2_210_certificate(self) -> None:
        p0_checks = {name: value for name, value in self.fresh["checks"].items() if name.startswith("P0_")}
        p1_checks = {name: value for name, value in self.fresh["checks"].items() if name.startswith("P1_")}
        self.assertTrue(equality.corollary_section(p0_checks, p1_checks)["uniqueness_of_global_orbit"])
        for name in equality.COROLLARY_P0_DEPENDENCIES:
            broken = dict(p0_checks, **{name: False})
            self.assertFalse(equality.corollary_section(broken, p1_checks)["uniqueness_of_global_orbit"], name)
        self.assertFalse(equality.corollary_section({}, p1_checks)["uniqueness_of_global_orbit"])
        self.assertFalse(equality.corollary_section(p0_checks, {})["uniqueness_of_global_orbit"])

    def test_fewer_forced_channels_fail_closed_without_exceptions(self) -> None:
        # Dropping 5940 from the forced channels makes the equality system 3x4: a clean failure, not an IndexError.
        with mock.patch.object(equality, "EXTRA_CHANNELS", ("45", "210")):
            section, checks = equality.p1_section()
            self.assertFalse(checks["P1_equality_system_square_4x4_and_nonsingular"])
            self.assertFalse(checks["P1_equality_set_J_vector_equals_J_at_p"])
            self.assertFalse(checks["P1_pluecker_defect_vanishes_on_equality_set"])
            self.assertFalse(section["equality_system"]["square_4x4"])
            self.assertIsNone(section["equality_system"]["determinant"])
            report = equality.build_report(numerical=False)
        self._assert_fails_closed(report, "P1_equality_system_square_4x4_and_nonsingular")
        self.assertFalse(report["corollary_exact_210"]["uniqueness_of_global_orbit"])

    def test_singular_declared_fit_points_fail_closed(self) -> None:
        with mock.patch.object(equality, "FIT_POINTS", ("p = e6789", "p = e6789", "random_sparse_0", "random_sparse_1")):
            section, checks = equality.p1_section()
        self.assertFalse(checks["P1_J0_J2_J3_J4_independent_at_declared_fit_points"])
        self.assertFalse(checks["P1_pluecker_defect_exact_J_combination_validated"])
        self.assertEqual(section["fit_determinant_J0_J2_J3_J4"], Fraction(0))
        self.assertIsNone(section["crossing_identities_M5_M6_M7_in_J_basis"])

    def test_exact_linear_algebra_rejects_non_square_input(self) -> None:
        with self.assertRaises(ValueError):
            equality.exact_det([[1, 2, 3, 4], [0, 1, 0, 0], [0, 0, 1, 0]])
        with self.assertRaises(ValueError):
            equality.exact_solve([[1, 0], [0, 1]], [1, 2, 3])
        with self.assertRaises(ValueError):
            equality.exact_solve([[1, 0, 0], [0, 1, 0]], [1, 2])
        with self.assertRaises(ValueError):
            equality.exact_inverse([[1, 2, 3]])
        self.assertEqual(equality.exact_det([[2, 1], [1, 1]]), Fraction(1))


if __name__ == "__main__":
    unittest.main()
