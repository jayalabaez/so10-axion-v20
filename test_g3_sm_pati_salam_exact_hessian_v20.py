#!/usr/bin/env python3
"""Tests for the exact full Hessian of the SM Pati-Salam G3 candidate (v20).

setUpClass builds one fresh report (the live compiler rows, about one minute,
plus the exact certificates, about twenty seconds) and compares it with the
committed artifact through target.report_mismatches: exact leaves must match
exactly, the float64 binding sections only within a loose tolerance.  The
mutation tests reuse the lru_cached live rows and exact source tensors, change
one input each and require the report or certificate to fail closed; the eps
family (O06 = 2|kappa| r0 + eps) is mutated through eps_family_section's
injection keywords (tangents, doublet, Hess N_H, equality report).
"""
from __future__ import annotations

import copy
import json
import unittest
from fractions import Fraction
from typing import Any
from unittest import mock

import numpy as np

import g3_candidate_physical_target_audit_v20 as target
import g3_sm_pati_salam_candidate_v20 as candidate
import g3_sm_pati_salam_exact_hessian_v20 as hessian

TIMING_KEYS = {"seconds", "runtime_seconds"}
EPS_FLAGS = (
    "eps_family_theorem_claimed",
    "eps_family_equality_set_unchanged",
    "eps_family_kernel_equals_symmetry_orbit",
    "eps_family_strictly_positive_on_symmetry_quotient_for_all_eps_positive",
    "doublet_mass_squared_equals_eps",
)
SECTION_FLAGS = EPS_FLAGS[1:]
L2_FLAGS = (
    "eps_family_kernel_equals_symmetry_orbit",
    "eps_family_strictly_positive_on_symmetry_quotient_for_all_eps_positive",
)


def _strip_timing(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _strip_timing(item) for key, item in value.items() if key not in TIMING_KEYS}
    if isinstance(value, list):
        return [_strip_timing(item) for item in value]
    return value


class SmPatiSalamExactHessianTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.committed = json.loads(hessian.OUT_JSON.read_text(encoding="utf-8"))
        cls.fresh = hessian.json_roundtrip(hessian.build_report())

    # ------------------------------------------------------------------
    # The theorem and its checks.
    # ------------------------------------------------------------------

    def test_all_checks_pass_and_theorem_is_claimed(self) -> None:
        for report in (self.committed, self.fresh):
            self.assertEqual(report["n_failed"], 0, report["failures"])
            self.assertEqual(report["n_checks"], len(report["checks"]))
            self.assertTrue(all(report["checks"].values()))
            self.assertEqual(report["status"], hessian.STATUS_CERTIFIED)
            self.assertEqual(report["overall_state"], hessian.OVERALL_STATE_CERTIFIED)
            self.assertEqual(report["overall_state"], "EXACT_LOCAL_HESSIAN_KERNEL_ORBIT_PLUS_TUNED_DOUBLET_CERTIFIED")
            # Not the chiral module's state: that one means kernel = symmetry tangents, no local blocker left.
            self.assertNotEqual(report["overall_state"], "CLOSED_FULL_LOCAL_HESSIAN_SUBPROBLEM")
            self.assertEqual(report["model_contract_id"], candidate.MODEL_CONTRACT_ID)
            self.assertTrue(report["theorem_claimed"])
            self.assertEqual(report["theorem"], hessian.THEOREM)
            for name in (
                "theorem_claimed",
                "proof_grade",
                "source_binding_exact",
                "exact_gradient_zero",
                "exact_PSD",
                "exact_rank_447",
                "exact_nullity_39",
                "kernel_equals_35_symmetry_tangents_plus_4_light_doublet",
                "positive_definite_on_complement_of_39_dim_kernel",
                "smallest_nonzero_eigenvalue_r0_squared_over_96_exact",
                "raised_O06_exact_rank_451_nullity_35",
                "raised_O06_kernel_equals_35_symmetry_tangents",
                "raised_O06_strict_quotient_positive",
                "raised_O06_strictly_positive_on_symmetry_quotient",
                *EPS_FLAGS,
            ):
                self.assertIs(report["flags"][name], True, name)
            for name in (
                # The repository's meaning of these flags (kernel = symmetry tangents) is false at the tuned benchmark.
                "strict_quotient_positive",
                "strictly_positive_on_symmetry_quotient",
                "all_zero_modes_are_symmetry_tangents",
                "other_r0_x0_kappa_certified",
                "candidate_wired_into_g3_gate",
                "G3_closed",
            ):
                self.assertIs(report["flags"][name], False, name)
            self.assertIs(report["G3_closed"], False)

    def test_status_strings(self) -> None:
        self.assertTrue(hessian.STATUS_CERTIFIED.endswith("__G3_OPEN"))
        self.assertTrue(hessian.STATUS_INCOMPLETE.endswith("__OPEN"))
        self.assertFalse(hessian.STATUS_INCOMPLETE.endswith("__G3_OPEN"))

    def test_committed_artifact_matches_fresh_report(self) -> None:
        committed = _strip_timing(self.committed)
        fresh = _strip_timing(self.fresh)
        committed_float = {key: committed.pop(key) for key in hessian.FLOAT_EVIDENCE_SECTIONS}
        fresh_float = {key: fresh.pop(key) for key in hessian.FLOAT_EVIDENCE_SECTIONS}
        self.assertEqual(target.report_mismatches(committed, fresh), [])
        # float64 comparisons with the live compiler: booleans and integers exact, round-off loosely.
        self.assertEqual(
            target.report_mismatches(committed_float, fresh_float, "float_evidence", rel_tol=1.0e-6, abs_tol=1.0e-5), []
        )

    def test_markdown_artifact_states_the_status(self) -> None:
        text = hessian.OUT_MD.read_text(encoding="utf-8")
        self.assertIn(self.committed["status"], text)
        self.assertIn("Sylvester", text)
        self.assertIn("447/39/0", text)
        self.assertIn("451/35/0", text)
        self.assertIn("## eps family: O06 = 2|kappa| r0 + eps", text)
        self.assertIn("`1/1000000`", text)

    def test_scope_and_verdict_state_the_float64_binding_and_open_g3(self) -> None:
        for report in (self.committed, self.fresh):
            self.assertIn("float64 binding", report["verdict"])
            self.assertIn("G3 stays open", report["verdict"])
            self.assertIn("float64 end to end", report["theorem"])
            self.assertTrue(any("compiler = exact operators" in row for row in report["scope"]["float64_evidence_only"]))
            self.assertTrue(any("G3 closure" in row for row in report["scope"]["not_proved_or_out_of_scope"]))
            # The eps family: literal Hessian criteria met for eps > 0, the tuned limit is not strict, no EWSB.
            self.assertIn("For the whole family O06 = 2|kappa| r0 + eps", report["verdict"])
            self.assertIn("electroweak symmetry is still not broken", report["verdict"])
            self.assertIn("the tuned eps = 0 limit is not a strict minimum", report["verdict"])
            self.assertTrue(any("electroweak symmetry breaking on the eps family" in row
                                for row in report["scope"]["not_proved_or_out_of_scope"]))
            self.assertTrue(any(row.startswith("eps_family L1 only: the equality-set theorem")
                                for row in report["scope"]["exact_premises_reused"]))

    # ------------------------------------------------------------------
    # Exact numbers.
    # ------------------------------------------------------------------

    def test_congruence_is_radical_free_and_invertible(self) -> None:
        squared = hessian.congruence_scale_squared()
        self.assertEqual(sum(1 for value in squared if value == 1), 210)
        self.assertEqual(sum(1 for value in squared if value == 2), 276)
        self.assertTrue(all(squared[index] == 1 for index in range(210)))
        rng = np.random.default_rng(7)
        matrix = rng.normal(size=(486, 486))
        matrix = matrix + matrix.T
        self.assertLess(float(np.max(np.abs(hessian.u_to_chart_hessian(hessian.chart_to_u_hessian(matrix)) - matrix))), 1.0e-12)
        congruence = self.fresh["congruence"]
        self.assertEqual(congruence["D"], "diag(1^210, sqrt(2)^276)")
        self.assertEqual((congruence["D_squared_entries_equal_one"], congruence["D_squared_entries_equal_two"]), (210, 276))

    def test_exact_certificate_numbers(self) -> None:
        cert = self.fresh["exact_certificate"]
        self.assertEqual(cert["variant"], "benchmark")
        self.assertEqual(cert["O06"], "1/50")
        self.assertEqual(cert["denominator"], 2016000)
        self.assertEqual(cert["denominator_factorization"], {"2": 8, "3": 2, "5": 3, "7": 1})
        self.assertTrue(cert["exactly_symmetric"])
        self.assertTrue(cert["gradient_exactly_zero"])
        self.assertEqual(cert["nonzero_entries"], 5358)
        inertia = cert["inertia"]
        self.assertEqual((inertia["positive"], inertia["zero"], inertia["negative"]), (447, 39, 0))
        self.assertEqual(inertia["two_by_two_pivots"], 0)
        self.assertEqual(inertia["components"], 65)
        self.assertEqual(max(inertia["component_sizes"]), 16)
        self.assertEqual(sum(inertia["component_sizes"]), 486)
        self.assertEqual((cert["exact_rank"], cert["exact_nullity"]), (447, 39))
        self.assertTrue(cert["symmetry_tangents_in_kernel_exact"])
        self.assertTrue(cert["doublet_directions_in_kernel_exact"])
        self.assertEqual(cert["kernel_spanning_rank_exact"], 39)
        self.assertTrue(cert["kernel_equals_expected_span"])
        self.assertEqual((cert["symmetry_orbit_dimension"], cert["zero_modes_beyond_symmetry_orbit"]), (35, 4))
        self.assertFalse(cert["strictly_positive_on_symmetry_quotient"])
        complement = cert["positive_pivot_complement"]
        self.assertEqual(complement["dimension"], 447)
        self.assertEqual(complement["principal_submatrix_positive_pivots"], 447)
        self.assertTrue(complement["principal_submatrix_positive_definite"])
        self.assertEqual(complement["kernel_rank_on_non_pivot_rows"], 39)
        self.assertTrue(complement["is_complement_of_kernel"])
        gap = cert["spectral_gap"]
        self.assertEqual((gap["lambda"], gap["lambda_over_r0_squared"]), ("1/2400", "1/96"))
        self.assertEqual((gap["negative"], gap["zero"], gap["positive"]), (39, 14, 433))
        self.assertTrue(gap["lambda_is_smallest_nonzero_eigenvalue"])

    def test_raised_O06_certificate_numbers(self) -> None:
        cert = self.fresh["exact_certificate_raised_O06"]
        self.assertEqual(cert["O06"], "51/2500")
        self.assertEqual(cert["O06_offset"], "1/2500")
        self.assertEqual(cert["denominator"], 10080000)
        self.assertTrue(cert["gradient_exactly_zero"])
        self.assertEqual((cert["inertia"]["positive"], cert["inertia"]["zero"], cert["inertia"]["negative"]), (451, 35, 0))
        self.assertEqual((cert["exact_rank"], cert["exact_nullity"]), (451, 35))
        self.assertTrue(cert["symmetry_tangents_in_kernel_exact"])
        self.assertFalse(cert["doublet_directions_in_kernel_exact"])
        self.assertEqual(cert["kernel_spanning_rank_exact"], 35)
        self.assertTrue(cert["kernel_equals_expected_span"])
        self.assertTrue(cert["strictly_positive_on_kernel_complement"])
        self.assertEqual((cert["symmetry_orbit_dimension"], cert["zero_modes_beyond_symmetry_orbit"]), (35, 0))
        self.assertTrue(cert["strictly_positive_on_symmetry_quotient"])
        gap = cert["spectral_gap"]
        self.assertEqual((gap["lambda_over_r0_squared"], gap["negative"], gap["zero"]), ("1/100", 35, 4))
        self.assertTrue(gap["lambda_is_smallest_nonzero_eigenvalue"])
        self.assertEqual(hessian.O06_RAISE, candidate.R0 * candidate.R0 / 100)

    def test_symmetry_tangents_are_the_equality_module_matrix(self) -> None:
        tangents = self.fresh["symmetry_tangents"]
        self.assertEqual(tangents["exact_ranks"], {"so10": 33, "so10_plus_X": 34, "so10_plus_X_plus_PQ": 35, "scaled_T_u": 35})
        self.assertTrue(tangents["matches_equality_module_ranks"])
        self.assertEqual(tangents["equality_module_ranks"]["kernel_dimension"], 12)
        self.assertEqual(tangents["spanning_rank_exact"], 39)
        self.assertEqual(tangents["common_denominator"], 20)
        self.assertTrue(tangents["H_rows_of_tangent_vanish"])
        self.assertEqual(self.fresh["light_doublet_directions"]["chart_indices"], list(candidate.DOUBLET_REAL_X))

    # ------------------------------------------------------------------
    # The eps family V_eps = V + eps N_H (O06 = 2|kappa| r0 + eps).
    # ------------------------------------------------------------------

    def test_eps_family_section(self) -> None:
        for report in (self.committed, self.fresh):
            eps = report["eps_family"]
            self.assertIs(eps["theorem_claimed"], True)
            self.assertEqual(eps["theorem"], hessian.EPS_THEOREM)
            self.assertEqual((eps["n_failed"], eps["failures"]), (0, []))
            self.assertEqual(eps["n_checks"], len(eps["checks"]))
            self.assertEqual(eps["n_checks"], 30)
            self.assertTrue(all(eps["checks"].values()), eps["checks"])
            self.assertEqual(set(eps["flags"]), set(SECTION_FLAGS))
            self.assertTrue(all(value is True for value in eps["flags"].values()))
            for name in SECTION_FLAGS:
                self.assertIs(report["flags"][name], eps["flags"][name], name)
            self.assertIn("not broken", eps["physical_reading"])
            self.assertIn("447/39", eps["physical_reading"])

    def test_eps_family_L1_premises(self) -> None:
        l1 = self.fresh["eps_family"]["L1_equality_set"]
        self.assertEqual(l1["relies_on"]["required_status"], hessian.equality.STATUS_PROVED)
        self.assertTrue(all(l1["relies_on"]["premises"].values()), l1["relies_on"]["premises"])
        operator = l1["O06_operator"]
        self.assertEqual(operator["field_counts"], {"H": 1, "Hb": 1})
        self.assertEqual(operator["singlet_dressing_counts"], {"S": 0, "Sb": 0, "X": 0, "Xb": 0})
        self.assertEqual((operator["base_family"], operator["base_basis"], operator["base_normalization"]),
                         ("Hdag_H_norm", ["Hdag_i H_i"], "unit delta_ij contraction"))
        self.assertEqual(operator["operator_dictionary_symbol"], "N_H")
        symbolic = l1["N_H_symbolic"]
        for key in ("N_H_in_chart_exact", "N_H_in_u_is_sum_of_squares", "hessian_q_is_identity_on_H",
                    "hessian_u_is_2_identity_on_H", "homogeneous_of_degree_2", "value_and_gradient_vanish_at_H_0"):
            self.assertIs(symbolic[key], True, key)
        shift = l1["coefficient_shift"]
        self.assertEqual(shift["symbolic_difference"], {hessian.O06_ID: "eps"})
        self.assertEqual(shift["parameters_compared"], 27)
        invariance = l1["G_invariance"]
        self.assertEqual(invariance["generators_checked"], 47)
        self.assertEqual(invariance["H10_charges"], {"X": -2, "PQ": -2})
        self.assertTrue(invariance["H_block_actions_antisymmetric"])
        self.assertEqual(l1["domain"], {"kappa_squared": "1/400", "8_r0_squared": "8/25", "kappa_squared_below_8_r0_squared": True})

    def test_eps_family_L2_and_doublet_numbers(self) -> None:
        eps = self.fresh["eps_family"]
        l2 = eps["L2_hessian"]
        self.assertEqual(l2["ranks"], {"T35": 35, "D4": 4, "T35_plus_D4": 39, "B_times_(T35_plus_D4)": 4})
        self.assertEqual(l2["dim_ker_H0_cap_ker_B"], 35)
        self.assertIs(l2["B_equals_2_P_H"], True)
        self.assertEqual(l2["linearity_in_eps_exact"], {"raised_O06": True, "tiny_eps": True})
        self.assertEqual(
            l2["for_every_eps_positive"],
            {"PSD": True, "rank": 451, "nullity": 35, "kernel": "span(T35), the SO(10) x U(1)_X x U(1)_PQ orbit tangent space",
             "strictly_positive_on_symmetry_quotient_dimension": 451},
        )
        doublet = eps["doublet"]
        self.assertEqual(doublet["H_block_chart_curvatures"], {"0": 4, "1/25": 4, "1": 6, "26/25": 6})
        self.assertEqual(doublet["H_block_chart_curvatures_over_r0_squared"], {"0": 4, "1": 4, "25": 6, "26": 6})
        self.assertEqual(doublet["doublet_chart_indices"], list(candidate.DOUBLET_REAL_X))
        self.assertEqual(
            doublet["rest_block_from_benchmark_certificate"],
            {"nullity": 35, "eigenvalues_below_r0_squared_over_96": 35, "eigenvalue_r0_squared_over_96_multiplicity": 14},
        )
        certificates = eps["consistency_certificates"]
        self.assertEqual(set(certificates), {"raised_O06", "tiny_eps"})
        for variant, (value, o06) in {"raised_O06": ("1/2500", "51/2500"), "tiny_eps": ("1/25000000", "500001/25000000")}.items():
            row = certificates[variant]
            self.assertEqual((row["eps"], row["O06"]), (value, o06), variant)
            self.assertEqual(row["inertia_positive_zero_negative"], "451/35/0", variant)
            self.assertEqual((row["exact_rank"], row["exact_nullity"]), (451, 35), variant)
            self.assertTrue(row["kernel_equals_symmetry_tangents"], variant)
            self.assertTrue(row["strictly_positive_on_symmetry_quotient"], variant)
            # The doublet mass^2 is eps, the lightest level with multiplicity 4 (eps < r0^2/96).
            self.assertEqual((row["smallest_nonzero_eigenvalue"], row["smallest_nonzero_eigenvalue_multiplicity"]), (value, 4))
        self.assertEqual(certificates["tiny_eps"]["eps_over_r0_squared"], "1/1000000")
        self.assertEqual(hessian.O06_TINY, candidate.R0 * candidate.R0 / 10**6)

    def test_psd_kernel_intersection_lemma_on_small_matrices(self) -> None:
        # ker(A + eps B) = ker A cap ker B for PSD A, B and eps > 0: nullity 1 here for every tiny eps.
        a = [[1, 0, 0], [0, 0, 0], [0, 0, 0]]
        b = [[0, 0, 0], [0, 1, 1], [0, 1, 1]]
        for eps in (Fraction(1, 10**9), Fraction(1, 3), Fraction(7)):
            block = [[Fraction(a[i][j]) + eps * b[i][j] for j in range(3)] for i in range(3)]
            row = hessian.exact_inertia(block)
            self.assertEqual((row["positive"], row["zero"], row["negative"]), (2, 1, 0))

    def _section(self, **kwargs: Any) -> dict[str, Any]:
        return hessian.json_roundtrip(hessian.eps_family_section(**kwargs))

    def test_eps_family_T35_with_nonzero_H_component_fails_closed(self) -> None:
        corrupted = hessian.integer_tangent_matrix().copy()
        corrupted[hessian.HB.start, 0] = 1
        section = self._section(tangent_matrix=corrupted)
        self.assertFalse(section["checks"]["L2_T35_vanishes_on_H_block"])
        self.assertFalse(section["checks"]["L2_H0_kernel_is_span_T35_plus_D4"])
        self.assertFalse(section["checks"]["L2_hess_N_H_annihilates_T35_and_doubles_D4"])
        for name in L2_FLAGS:
            self.assertIs(section["flags"][name], False, name)
        self.assertIs(section["theorem_claimed"], False)
        self.assertTrue(section["theorem"].startswith("NOT CLAIMED"))
        # L1 does not use the tangents.
        self.assertIs(section["flags"]["eps_family_equality_set_unchanged"], True)

    def test_eps_family_D4_outside_H_block_fails_closed(self) -> None:
        moved = hessian.doublet_matrix().copy()
        moved[hessian.DOUBLET_REAL_X[0], 0] = 0
        moved[hessian.SG.start, 0] = 1
        section = self._section(doublet=moved)
        self.assertFalse(section["checks"]["L2_D4_inside_H_block"])
        self.assertFalse(section["checks"]["L2_H0_kernel_is_span_T35_plus_D4"])
        self.assertFalse(section["checks"]["doublet_Re_H6_9_exact_eigenvectors_with_eigenvalue_eps_at_raised_and_tiny"])
        for name in (*L2_FLAGS, "doublet_mass_squared_equals_eps"):
            self.assertIs(section["flags"][name], False, name)
        self.assertIs(section["theorem_claimed"], False)

    def test_eps_family_wrong_hess_N_H_fails_closed(self) -> None:
        # Hess N_H = P_H is the chart form; in u it must be 2 P_H.  The chart form in u-units is wrong.
        wrong = (hessian._diag_block(hessian.HB, [1] * hessian.chart.H_REAL_DIM), 1)
        section = self._section(n_h_hessian_u=wrong)
        for name in ("L1_O06_unit_hessian_is_hess_u_N_H_equal_2_P_H", "L2_hess_u_N_H_is_2_P_H_hence_PSD_with_kernel_H_equal_0",
                     "L2_hess_N_H_annihilates_T35_and_doubles_D4", "L2_raised_minus_benchmark_equals_eps_hess_N_H_exact",
                     "L2_tiny_minus_benchmark_equals_eps_hess_N_H_exact"):
            self.assertFalse(section["checks"][name], name)
        for name in SECTION_FLAGS:
            self.assertIs(section["flags"][name], False, name)
        # An off-block entry (H-Sigma coupling) is caught as well.
        leaky = hessian._two_p_h().copy()
        leaky[hessian.HB.start, hessian.SG.start] = leaky[hessian.SG.start, hessian.HB.start] = 1
        section = self._section(n_h_hessian_u=(leaky, 1))
        self.assertFalse(section["checks"]["L2_hess_u_N_H_is_2_P_H_hence_PSD_with_kernel_H_equal_0"])
        self.assertIs(section["flags"]["eps_family_kernel_equals_symmetry_orbit"], False)

    def test_eps_family_failed_equality_report_fails_L1_closed(self) -> None:
        committed = hessian.load_equality_report()
        self.assertTrue(all(hessian.equality_premises(committed).values()))
        failed = copy.deepcopy(committed)
        failed["n_failed"] = 1
        failed["failures"] = ["P2_self_weights_force_sigma_purity"]
        report = hessian.json_roundtrip(hessian.build_report(equality_report=failed))
        # The benchmark certificate does not depend on the equality report; the eps-family L1 does.
        self.assertEqual(report["n_failed"], 0, report["failures"])
        self.assertEqual(report["status"], hessian.STATUS_CERTIFIED)
        eps = report["eps_family"]
        self.assertFalse(eps["checks"]["L1_equality_report_proved_status_and_premises"])
        self.assertIs(report["flags"]["eps_family_equality_set_unchanged"], False)
        self.assertIs(report["flags"]["eps_family_theorem_claimed"], False)
        self.assertIs(report["flags"]["eps_family_kernel_equals_symmetry_orbit"], True)
        self.assertIn("The eps-family extension is NOT claimed", report["verdict"])
        for mutate in (
            lambda value: value.update(status=hessian.equality.STATUS_NOT_PROVED),
            lambda value: value["equality_conditions"].update(conditions=["|Phi17| = x0"]),
            lambda value: value["sos_decomposition"]["eight_term_operator_expansion"]["operator_dictionary"].update(
                {hessian.O06_ID: "2*N_H"}
            ),
        ):
            tampered = copy.deepcopy(committed)
            mutate(tampered)
            self.assertFalse(all(hessian.equality_premises(tampered).values()))
            self.assertIs(self._section(equality_report=tampered)["flags"]["eps_family_equality_set_unchanged"], False)
        missing = self._section(equality_report={})
        self.assertIs(missing["flags"]["eps_family_equality_set_unchanged"], False)
        self.assertIs(missing["flags"]["eps_family_kernel_equals_symmetry_orbit"], True)

    def test_eps_family_requires_the_benchmark_report(self) -> None:
        section = self._section(ok=False)
        self.assertTrue(all(section["checks"].values()))
        self.assertIs(section["theorem_claimed"], False)
        for name in SECTION_FLAGS:
            self.assertIs(section["flags"][name], False, name)

    def test_upstream_source_identities(self) -> None:
        upstream = self.fresh["upstream_identities"]
        self.assertTrue(all(upstream["checks"].values()), upstream["checks"])
        self.assertEqual(upstream["phi_pair_casimir"]["values_at_p"], [1, 24, 192, 3552])
        self.assertEqual(upstream["sigma_pair_casimir"]["sigma_std_pair_eigenvalue"], "-5")
        self.assertEqual(
            upstream["sigma_pair_casimir"]["projector_value_on_sigma_std_pair"],
            {"54": "0", "1050bar": "0", "2772bar": "1", "4125": "0"},
        )
        tensors = upstream["source_tensors"]
        self.assertEqual(tensors["sigma_std_raw_norm_squared"], 16)
        self.assertTrue(tensors["M_exactly_hermitian"])
        self.assertTrue(all(self.fresh["coefficient_identities"].values()))

    def test_units_cover_every_benchmark_parameter_once(self) -> None:
        coverage = self.fresh["exact_certificate"]["coverage"]
        self.assertTrue(coverage["unit_names_unique"])
        self.assertTrue(coverage["coefficients_proportional_to_unit_weights"])
        self.assertEqual(coverage["uncovered_nonzero_parameters"], [])
        self.assertEqual(coverage["units_parameters_not_in_benchmark"], [])
        units = hessian.exact_unit_matrices()
        covered = [parameter for unit in units for parameter in unit["weights"]]
        self.assertEqual(sorted(covered), sorted(hessian.benchmark_coefficients()))
        self.assertEqual(len(covered), len(set(covered)))
        self.assertEqual(len(covered), candidate.EXPECTED_NONZERO)

    # ------------------------------------------------------------------
    # Live compiler binding (float64).
    # ------------------------------------------------------------------

    def test_live_compiler_binding(self) -> None:
        for key in ("live_binding", "live_binding_raised_O06"):
            live = self.fresh[key]
            self.assertLessEqual(live["max_abs_exact_minus_live_chart_hessian"], 1.0e-12)
            self.assertLessEqual(live["max_abs_exact_minus_live_gradient"], 1.0e-12)
            self.assertTrue(live["within_tolerance"])
            self.assertTrue(live["lattice"]["rounded_live_equals_exact_numerator"])
            self.assertGreater(live["lattice"]["half_lattice_margin"], 0.49)
            self.assertLess(abs(live["V_minus_V0"]), 1.0e-12)
        inertia = self.fresh["live_binding"]["numerical_inertia"]
        self.assertEqual(
            (inertia["negative_below_minus_1e_minus_10"], inertia["zero_at_1e_minus_10"], inertia["positive_above_1e_minus_10"]),
            (0, 39, 447),
        )
        units = self.fresh["unit_binding"]
        self.assertTrue(units["all_units_bound"])
        self.assertEqual(units["unit_count"], 21)
        for name, row in units["units"].items():
            self.assertTrue(row["bound"], name)
            self.assertLess(row["relative_hessian_difference"], 1.0e-11, name)
        self.assertTrue(self.fresh["float_tangent_binding"]["consistent"])
        self.assertTrue(self.fresh["candidate_float64_claims"]["all_claims_present_and_consistent"])

    def test_compare_live_detects_a_perturbed_compiler_hessian(self) -> None:
        exact = hessian.exact_hessian()
        hessian_q = hessian.u_to_chart_hessian(hessian.exact_to_float(*exact["hessian"]))
        gradient_q = np.zeros(486)
        clean = hessian.compare_live(hessian_q, gradient_q, exact["hessian"], exact["gradient"])
        self.assertTrue(clean["within_tolerance"])
        self.assertTrue(clean["lattice"]["passes"])
        small = hessian_q.copy()
        small[3, 5] += 1.0e-9
        small[5, 3] += 1.0e-9
        row = hessian.compare_live(small, gradient_q, exact["hessian"], exact["gradient"])
        self.assertFalse(row["within_tolerance"])
        large = hessian_q.copy()
        large[300, 301] += 1.0e-5
        large[301, 300] += 1.0e-5
        row = hessian.compare_live(large, gradient_q, exact["hessian"], exact["gradient"])
        self.assertFalse(row["within_tolerance"])
        self.assertFalse(row["lattice"]["passes"])
        moved = np.zeros(486)
        moved[0] = 1.0e-9
        self.assertFalse(hessian.compare_live(hessian_q, moved, exact["hessian"], exact["gradient"])["within_tolerance"])

    # ------------------------------------------------------------------
    # Exact linear algebra and fail-closed mutations.
    # ------------------------------------------------------------------

    def test_exact_inertia_on_small_matrices(self) -> None:
        def inertia(rows: list[list[int]]) -> tuple[int, int, int, int]:
            row = hessian.exact_inertia([[Fraction(value) for value in line] for line in rows])
            return row["positive"], row["zero"], row["negative"], row["two_by_two_pivots"]

        self.assertEqual(inertia([[1, 2], [2, 1]]), (1, 0, 1, 0))
        self.assertEqual(inertia([[0, 1], [1, 0]]), (1, 0, 1, 1))
        self.assertEqual(inertia([[1, 1], [1, 1]]), (1, 1, 0, 0))
        self.assertEqual(inertia([[0, 0], [0, 0]]), (0, 2, 0, 0))
        self.assertEqual(inertia([[2, 1, 0], [1, 2, 1], [0, 1, 2]]), (3, 0, 0, 0))
        self.assertEqual(inertia([[0, 0, 1], [0, 0, 0], [1, 0, 0]]), (1, 1, 1, 1))
        self.assertEqual(inertia([[-1, 0], [0, 3]]), (1, 0, 1, 0))

    def _assert_fails_closed(self, report: dict[str, Any], *expected: str) -> None:
        self.assertGreater(report["n_failed"], 0)
        for name in expected:
            self.assertIn(name, report["failures"])
        self.assertEqual(report["status"], hessian.STATUS_INCOMPLETE)
        self.assertEqual(report["overall_state"], hessian.OVERALL_STATE_OPEN)
        self.assertEqual(report["overall_state"], "G3_SM_EXACT_LOCAL_TEST_OPEN")
        self.assertFalse(report["theorem_claimed"])
        self.assertTrue(report["theorem"].startswith("NOT CLAIMED"))
        for flag in (
            "theorem_claimed",
            "proof_grade",
            "exact_rank_447",
            "exact_nullity_39",
            "positive_definite_on_complement_of_39_dim_kernel",
            "strict_quotient_positive",
            "strictly_positive_on_symmetry_quotient",
            *EPS_FLAGS,
        ):
            self.assertFalse(report["flags"][flag], flag)
        self.assertFalse(report["eps_family"]["theorem_claimed"])

    def test_detuned_O06_fails_closed(self) -> None:
        # O06 below 2|kappa| r0 turns the four light-doublet modes negative (a saddle).
        lowered = 2 * abs(hessian.KAPPA) * hessian.R0 - hessian.O06_RAISE
        report = hessian.build_report(coefficient_overrides={hessian.O06_ID: lowered})
        self._assert_fails_closed(
            report,
            "exact_PSD",
            "exact_rank_447",
            "exact_nullity_39",
            "kernel_equals_symmetry_tangents_plus_light_doublet",
            "coefficients_O06_equals_2_abs_kappa_r0",
            "live_numerical_inertia_0_39_447",
        )
        cert = report["exact_certificate"]
        self.assertEqual((cert["inertia"]["positive"], cert["inertia"]["negative"], cert["inertia"]["zero"]), (447, 4, 35))
        # The exact certificate and the live compiler still agree: the binding is not what failed.
        self.assertTrue(report["checks"]["live_compiler_hessian_matches_exact_to_1e_minus_12"])

    def test_broken_A_plus_C_ratio_fails_closed(self) -> None:
        report = hessian.build_report(coefficient_overrides={hessian.O44_IDS[0]: Fraction(42, 8)})
        self._assert_fails_closed(
            report,
            "every_benchmark_parameter_in_exactly_one_unit",
            "coefficients_O44_coefficients_equal_one_eighth_A_plus_C",
        )
        self.assertFalse(report["exact_certificate"]["coverage"]["coefficients_proportional_to_unit_weights"])

    def test_corrupted_symmetry_tangent_fails_closed(self) -> None:
        original = hessian.integer_tangent_matrix()
        corrupted = original.copy()
        corrupted[hessian.chart.PHI_SLICE.start, 0] += 1

        def clear() -> None:
            hessian.tangent_data.cache_clear()
            hessian._exact_certificate_cached.cache_clear()

        clear()
        try:
            with mock.patch.object(hessian, "integer_tangent_matrix", return_value=corrupted):
                cert = hessian.exact_certificate()
        finally:
            clear()
        self.assertFalse(cert["symmetry_tangents_in_kernel_exact"])
        self.assertFalse(cert["kernel_equals_expected_span"])
        self.assertFalse(cert["strictly_positive_on_kernel_complement"])
        self.assertTrue(hessian.exact_certificate()["kernel_equals_expected_span"])

    def test_sub_tolerance_exact_perturbation_fails_closed_through_the_report(self) -> None:
        # An exact error far below the 1e-12 float tolerance (eps ~ 5e-19 on a doublet diagonal of H_u) must not
        # abort the run on an integer-size heuristic: it must reach the checks, where the exact-lattice rounding
        # (the only guard below the tolerance) and the exact inertia catch it.
        original = hessian._exact_hessian_cached
        eps = Fraction(1, 2016000 * 2**20)
        index = hessian.DOUBLET_REAL_X[0]
        bump = np.zeros((hessian.TOTAL_DIM, hessian.TOTAL_DIM), dtype=np.int64)
        bump[index, index] = 1

        def perturbed(variant: str, overrides: Any) -> dict[str, Any]:
            row = original(variant, overrides)
            numerator, denominator = row["hessian"]
            shifted = hessian.combine(((Fraction(1, denominator), numerator), (eps, bump)), (hessian.TOTAL_DIM, hessian.TOTAL_DIM))
            return {**row, "hessian": shifted}

        def clear() -> None:
            hessian._exact_certificate_cached.cache_clear()
            hessian._live_binding_cached.cache_clear()

        clear()
        try:
            with mock.patch.object(hessian, "_exact_hessian_cached", side_effect=perturbed):
                report = hessian.build_report()
        finally:
            clear()
        self._assert_fails_closed(
            report,
            "live_compiler_hessian_rounds_to_exact_lattice",
            "exact_rank_447",
            "exact_nullity_39",
            "exact_hessian_annihilates_4_doublet_directions",
        )
        self.assertEqual(report["status"], hessian.STATUS_INCOMPLETE)
        # The float comparison alone cannot see it: it is below the 1e-12 tolerance.
        self.assertTrue(report["checks"]["live_compiler_hessian_matches_exact_to_1e_minus_12"])
        self.assertFalse(report["live_binding"]["lattice"]["rounded_live_equals_exact_numerator"])
        self.assertEqual(report["exact_certificate"]["denominator"], 2016000 * 2**20)
        cert = report["exact_certificate"]
        self.assertEqual((cert["inertia"]["positive"], cert["inertia"]["zero"], cert["inertia"]["negative"]), (448, 38, 0))

    def test_exact_helpers_handle_large_integers(self) -> None:
        big = 3 * 2**60 + 1
        values = hessian.exact_to_float(np.asarray([[big, -big], [1, 0]], dtype=object), 3)
        self.assertEqual(values.tolist(), [[big / 3, -big / 3], [1 / 3, 0.0]])
        numerator = np.asarray([[big, 0], [0, 2]], dtype=object)
        product = hessian._exact_matmul(numerator, np.asarray([[1, 2], [3, 4]], dtype=np.int64))
        self.assertEqual(product.tolist(), [[big, 2 * big], [6, 8]])
        self.assertFalse(hessian._all_zero(product))
        self.assertTrue(hessian._all_zero(np.zeros((2, 2), dtype=object)))

    def test_missing_candidate_claims_fail_closed(self) -> None:
        self.assertFalse(hessian.candidate_claims_section({})["all_claims_present_and_consistent"])
        report = json.loads(candidate.OUT_JSON.read_text(encoding="utf-8"))
        report["compiler"][str(candidate.R0)]["projected_hessian"]["n_zero"] = 0
        self.assertFalse(hessian.candidate_claims_section(report)["all_claims_present_and_consistent"])


if __name__ == "__main__":
    unittest.main()
