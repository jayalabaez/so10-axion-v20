import copy
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import sympy as sp
import v103_locked_parity_quantum_boundary_audit as audit


class LockedParityQuantumBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = audit.build_certificate()
        cls.r = cls.c["R2_condensate_and_surviving_selection"]
        cls.t = cls.c["full_SMW_parity_trace_census"]
        cls.m = cls.c["reduced_4D_parity_mass_patch"]
        cls.e = cls.c["reduced_6D_RP7_eta_character"]
        cls.w = cls.c["ordinary_even_U_WCS_boundary"]

    def test_canonical_lineage_roundtrip_and_validation(self):
        self.assertEqual(audit.canonical_sha(self.c), self.c["core_sha256"])
        self.assertEqual(json.loads(json.dumps(self.c)), self.c)
        for name, (_, core) in {**audit.PARENTS, **audit.EARLIER}.items():
            self.assertEqual(self.c["input_core_hashes"][name], core)
        audit.validate_certificate(self.c)

    def test_portable_CRLF_source_hash(self):
        path = audit.ROOT/"v102_full_vev_finite_stabilizer_audit.py"
        raw = path.read_bytes().replace(b"\r\n", b"\n")
        expected = audit.portable_sha(path)
        with patch.object(Path, "read_bytes", return_value=raw.replace(b"\n", b"\r\n")):
            self.assertEqual(audit.portable_sha(path), expected)

    def test_source_pins_remain_fresh_after_pure_cache(self):
        original = audit.portable_sha
        for name in ("susy_v102_cubic_exclusion_common_tensor_target_audit.py",
                     "test_susy_v102_multipath_g1_frontier_master_audit.py",
                     "v102_full_vev_finite_stabilizer_audit.py",
                     "test_v92_c4_section_eta_certificate.py"):
            with patch.object(audit, "portable_sha", side_effect=lambda p: "0"*64 if p.name == name else original(p)):
                with self.assertRaisesRegex(RuntimeError, "source/test pin"):
                    audit.build_certificate()

    def test_noncanonical_parent_fails_closed(self):
        original = Path.read_text
        def read(path, *args, **kwargs):
            text = original(path, *args, **kwargs)
            if path.name == audit.PARENTS["v102_master"][0]:
                data = json.loads(text)
                data["core_sha256"] = "0"*64
                return json.dumps(data)
            return text
        with patch.object(Path, "read_text", read):
            with self.assertRaisesRegex(RuntimeError, "noncanonical frozen parity parent"):
                audit.build_certificate()

    def test_rehashed_derived_claim_is_rejected(self):
        value = copy.deepcopy(self.c)
        value["ordinary_even_U_WCS_boundary"]["number_of_passing_refinement_labels"] = 1
        value["core_sha256"] = audit.canonical_sha(value)
        with self.assertRaisesRegex(RuntimeError, "fresh bound derivation"):
            audit.validate_certificate(value)

    def test_fresh_finite_matrix_rebinding_not_only_saved_claim(self):
        original = audit.previous.build_certificate
        def changed():
            value = original()
            value["status"] = "invented"
            return value
        with patch.object(audit.previous, "build_certificate", changed):
            with self.assertRaisesRegex(RuntimeError, "fresh frozen matrices"):
                audit.build_certificate()

    def test_neutral_R2_condensate_stabilizer_exactly_eight(self):
        expected = set(product(range(2), (0, 4), (0, 2)))
        self.assertEqual({tuple(v) for v in self.r["after_elements_f_k_R"]}, expected)
        self.assertEqual(self.r["specified_stabilizer_before_order"], 16)
        self.assertEqual(self.r["full_selected_character_image_order"], 8)
        for v in expected:
            self.assertEqual(audit.previous.component_exponent(v, 0, 2), 0)

    def test_locked_parity_survives_and_is_not_fermion_center(self):
        self.assertIn([1, 4, 2], self.r["after_elements_f_k_R"])
        self.assertTrue(self.r["P265_survives_this_R2_breaking"])
        self.assertEqual(len({tuple(x) for x in self.e["four_center_cosets_f_P"]}), 4)
        self.assertTrue(self.e["P_and_fermion_center_distinct_in_known_kernel"])

    def test_all_four_old_R_forbidden_rows_pass_residual_characters(self):
        rows = self.r["four_previously_forbidden_visible_operators"]
        self.assertEqual(len(rows), 4)
        for row in rows:
            self.assertEqual(row["scalar_R_sum_mod4"], 0)
            self.assertEqual(row["all_eight_residual_action_phases_mod8"], [0]*8)
            self.assertTrue(row["one_neutral_R2_W0_factor_restores_formal_Z4R_covariance"])
        self.assertFalse(self.r["allowed_operators_are_proved_generated_or_numerically_safe"])

    def test_bare_mu_continuous_charge_requires_its_dressing(self):
        rows = {x["operator"]: x for x in self.r["four_previously_forbidden_visible_operators"]}
        self.assertEqual(rows["H_uA H_dC"]["q8_sum"], 12)
        self.assertFalse(rows["H_uA H_dC"]["that_factor_alone_restores_continuous_gauge_invariance"])
        self.assertEqual(rows["Phi-^2 B0 H_uA H_dC"]["q8_sum"], 0)
        self.assertTrue(rows["Phi-^2 B0 H_uA H_dC"]["continuously_gauge_neutral_as_written"])

    def test_all_order_parity_arithmetic_including_conjugation(self):
        # Any visible monomial has matching q8/R parities; extras change R only.
        # Signed multiplicities model both fields and conjugates; mod2 is exact.
        for q_visible, n_extra, n_vev, n_W0 in product(range(-4, 5), repeat=4):
            q_parity = q_visible % 2
            R_parity = (q_visible+n_extra+2*n_W0) % 2
            if q_parity == R_parity == 0:
                self.assertEqual(n_extra % 2, 0)
        self.assertIn("other P-odd fields count toward total P parity", self.r["all_order_selection"])

    def test_full_singlet_and_odd_census(self):
        self.assertEqual(self.t["all_hyper_counts"], [144, 3, 19, 11, 90])
        self.assertEqual(self.t["SMW_total_moments_0_2_4"], [267, 6472, 387808])
        odd = [144, 3, 19, 11, 88]
        self.assertEqual([sum(n*q**j for n, q in zip(odd, (0, 2, 4, 6, 8))) for j in (0, 2, 4)],
                         self.t["SMW_P_odd_moments_0_2_4"])

    def test_full_symplectic_trace_before_half(self):
        signed_counts = [-144, -3, -19, -11, -86]
        expected = [sum(n*(q**j+(-q)**j) for n, q in zip(signed_counts, (0, 2, 4, 6, 8))) for j in range(5)]
        self.assertEqual(expected, [-526, 0, -12432, 0, -742848])
        self.assertEqual(expected, self.t["full_paired_P_inserted_traces_powers_0_through_4"])
        self.assertEqual([expected[j]//2 for j in (0, 2, 4)], self.t["SMW_P_inserted_moments_0_2_4"])

    def test_odd_continuous_index_density_exact(self):
        f, p1, p2 = sp.symbols("f p1 p2")
        expected = sp.Rational(379616, 24)*f**4-sp.Rational(6344, 48)*p1*f**2+sp.Rational(265, 5760)*(7*p1**2-4*p2)
        self.assertEqual(sp.expand(expected-sp.sympify(self.t["positive_index_density_of_full_odd_hyper_representation"])), 0)
        self.assertEqual(sp.expand(expected+sp.sympify(self.t["MM_negative_chirality_anomaly_density"])), 0)

    def test_projected_out_bulk_fields_not_discarded(self):
        self.assertEqual(self.t["odd_hypers_without_selected_constant_zero_modes"], 256)
        self.assertEqual(self.t["selected_odd_zero_modes"], 9)
        self.assertFalse(self.t["projected_out_modes_can_be_discarded_from_6D_anomaly"])
        self.assertFalse(self.t["accidental_265_minus9_multiple16_is_dimensional_anomaly_matching"])

    def test_mass_matrix_has_actual_charge_selected_channels(self):
        M = audit.previous.mass.matrix(self.m["normalized_symmetric_mass_matrix"])
        charges = [2]*3+[4]*3+[6]*3
        self.assertEqual(M, M.T)
        for i, j in product(range(9), repeat=2):
            if M[i, j]:
                self.assertEqual(charges[i]+charges[j]-8, 0)
        self.assertEqual((-sp.eye(9)).T*M*(-sp.eye(9)), M)

    def test_majorana_mass_witness_is_rank_nine(self):
        M = audit.previous.mass.matrix(self.m["normalized_symmetric_mass_matrix"])
        self.assertEqual(M**2, sp.eye(9))
        self.assertEqual(M.det(), -1)
        self.assertEqual(M.rank(), 9)
        self.assertEqual(M.eigenvals(), {sp.Integer(1): 6, sp.Integer(-1): 3})
        self.assertEqual(self.m["determinant"], "-phi**9")

    def test_mass_is_only_flat_normal_quadratic_patch(self):
        self.assertIn("flat-normal", self.m["category"])
        self.assertIn("normal/tensor completion", self.m["independent_normal_covariance"])
        for key in ("Phi_zeros_or_defect_matching_completed", "interacting_scalar_soft_spectrum_or_QK_vacuum_gapped",
                    "quantum_parity_of_full_compactification_proved"):
            self.assertFalse(self.m[key])

    def test_Hsieh_n2_pair_is_integral_for_arbitrary_Weyl_counts(self):
        for count in range(33):
            n = 2
            alpha = (F(n*n+3*n+2, 6*n)*count, F(2, n)*count)
            self.assertEqual(tuple(v % 1 for v in alpha), (0, 0))
        reduced = self.m["reduced_quantum_test"]
        self.assertEqual(reduced["ordinary_OmegaSpin5_BC2"], "0")
        self.assertEqual(reduced["Pin_minus_degree4"], "0")
        self.assertEqual(reduced["Hsieh_n2_pair_mod1"], ["0", "0"])

    def test_mapping_torus_parity_on_even_spin4_index(self):
        for signature_over16 in range(-8, 9):
            index = -2*signature_over16
            self.assertEqual((9*index) % 2, 0)
        self.assertFalse(self.m["reduced_quantum_test"]["SpinZ4_or_full_Gammahat_anomaly_inferred"])

    def test_continuous_mass_anomaly_does_not_disappear(self):
        charges = [2]*3+[4]*3+[6]*3
        self.assertEqual([sum(charges), sum(q**3 for q in charges)], [36, 864])
        self.assertEqual(self.m["continuous_parent_TrQ_TrQ3"], [36, 864])
        self.assertFalse(self.m["continuous_parent_anomaly_erased_by_the_mass"])

    def test_Donnelly_complex_RP7_formula_both_spin_lifts(self):
        tangent = -sp.eye(4)
        denominator = 2*(tangent-sp.eye(4)).det()
        self.assertEqual(denominator, 32)
        for q, spin in product(range(-3, 4), (0, 1)):
            expected = sp.Rational((-1)**((q+spin) % 2), denominator)
            self.assertEqual(sp.Rational(audit.rp7_complex_xi(q, spin)), expected)
        self.assertEqual(self.e["complex_xi_charge0_charge1_by_spin"], [["1/32", "-1/32"], ["-1/32", "1/32"]])

    def test_negative_chirality_SMW_is_half_actual_paired_xi(self):
        row = audit.rp7_hyper_ratio(1)
        self.assertEqual(F(row["paired_twisted_minus_trivial_xi_unreduced"]), F(-1, 8))
        self.assertEqual(F(row["negative_chirality_SMW_exponent_unreduced"]), F(1, 16))
        row265 = audit.rp7_hyper_ratio(265)
        self.assertEqual(F(row265["negative_chirality_SMW_exponent_unreduced"]), F(265, 16))

    def test_halving_a_residue_would_give_wrong_Pfaffian(self):
        paired = F(265, 8)  # Opposite orientation; its discarded integer is odd.
        correct = (-paired/2) % 1
        incorrect = (-(paired % 1)/2) % 1
        self.assertEqual(correct, F(7, 16))
        self.assertEqual(incorrect, F(15, 16))
        self.assertNotEqual(correct, incorrect)

    def test_both_spin_choices_and_orientation_conjugate(self):
        rows = {(r["spin_shift"], r["orientation"]): F(r["exponent_mod1"]) for r in self.e["all_265_full_hyper_tests"]}
        self.assertEqual(rows[(0, 1)], F(9, 16))
        self.assertEqual(rows[(1, 1)], F(7, 16))
        for spin in (0, 1):
            self.assertEqual((rows[(spin, 1)]+rows[(spin, -1)]) % 1, 0)

    def test_primitive_RP7_and_full_bare_character_orders(self):
        self.assertEqual(self.e["ordinary_OmegaSpin7_BC2"], "Z/16")
        self.assertEqual(audit.phase_order(F(1, 16)), 16)
        self.assertEqual(self.e["bare_character_class_in_canonical_MM_convention_mod16"], 9)
        self.assertEqual(self.e["necessary_inverse_character_class_mod16"], 7)
        for row in self.e["all_265_full_hyper_tests"]:
            self.assertEqual(row["phase_order"], 16)
        self.assertFalse(self.e["inverse_eta_is_a_constructed_same_action_inflow"])

    def test_relative_subtraction_is_not_new_physical_particles(self):
        self.assertIn("reference, not new particles", self.e["same_manifold_ratio"])
        self.assertIn("twisted-minus-trivial", self.e["formula"])
        self.assertFalse(self.e["projection_to_nine_modes_replaces_6D_eta"])
        self.assertFalse(self.e["full_normal_split_Gammahat_background_admissibility_proved"])

    def test_lambda_RP7_both_spin_lifts_via_lifted_torus_weights(self):
        values = []
        for weights in ((1, 1, 1, 1), (3, 1, 1, 1)):
            self.assertEqual(sum(weights) % 2, 0)
            values.append((sum(q*q for q in weights)//2) % 2)
        self.assertEqual(values, [0, 0])
        self.assertEqual(self.w["tangent_lambda_both_spin_lifts_mod2"], values)

    def test_even_U_quadratic_null_axes_and_polarization(self):
        q = lambda a, b: F(a*b, 2) % 1
        for a, b, c, d in product(range(2), repeat=4):
            self.assertEqual(q(a, 0), 0)
            self.assertEqual(q(0, b), 0)
            self.assertEqual((q(a+c, b+d)-q(a, b)-q(c, d)) % 1, F(a*d+b*c, 2) % 1)
        self.assertEqual(self.w["available_counterterm_exponents_mod1"], ["0", "1/2"])

    def test_all_sixteen_spin_orientation_refinement_tests_fail(self):
        rows = self.w["all_spin_orientation_and_refinement_tests"]
        self.assertEqual(len(rows), 16)
        self.assertEqual({tuple(r["torsion_label"]) for r in rows}, set(product(range(2), repeat=2)))
        for row in rows:
            self.assertNotEqual(F(row["combined_exponent_mod1"]), 0)
        self.assertEqual(self.w["all_combined_exponents_mod1"], ["1/16", "7/16", "9/16", "15/16"])

    def test_residual_character_modulo_ordinary_U_has_order_eight(self):
        subgroup = {0, 8}
        first = next(n for n in range(1, 17) if 9*n % 16 in subgroup)
        self.assertEqual(first, 8)
        self.assertEqual(self.w["bare_character_order_modulo_this_counterterm_subgroup"], first)
        self.assertFalse(self.w["all_generalized_Gammahat_GS_extensions_excluded"])

    def test_no_explicit_breaking_stability_or_gate_promotion(self):
        scope = self.c["physical_scope_and_quantum_interpretation"]
        self.assertFalse(scope["global_tHooft_anomaly_is_explicit_parity_breaking"])
        self.assertFalse(scope["full_anomaly_cancellation_or_nonconservation_claimed"])
        self.assertFalse(scope["full_P_finite_background_extension_to_normal_split_orbifold_Gammahat_proved"])
        self.assertFalse(scope["nine_V93_extra_singlets_are_V65_orphan_quarks"])
        self.assertFalse(scope["new_particles_condensates_counterterms_or_domain_adopted"])
        self.assertTrue(scope["four_and_six_dimensional_tests_are_not_interchangeable"])
        self.assertTrue(all(value is False for value in self.c["remaining_obligations"].values()))

    def test_primary_source_domains_and_convention_markers(self):
        self.assertEqual({row["url"] for row in self.c["primary_sources"]}, {
            "https://arxiv.org/pdf/1808.00009", "https://arxiv.org/pdf/1808.02881",
            "https://arxiv.org/pdf/1808.01334", "https://arxiv.org/pdf/1009.0905"})
        self.assertIn("4.15", self.w["quadratic_derivation"])
        self.assertIn("BEFORE mod1", self.e["formula"])
        self.assertFalse(self.w["old_V91_gauge_source_sign_dictionary_silently_reconciled"])

    def test_eta_input_validation(self):
        for q, spin in ((True, 0), (1.0, 0), (1, 2), (1, False)):
            with self.assertRaises(ValueError):
                audit.rp7_complex_xi(q, spin)
        for count, orientation in ((-1, 1), (True, 1), (1, 0), (1, True)):
            with self.assertRaises(ValueError):
                audit.rp7_hyper_ratio(count, orientation=orientation)


if __name__ == "__main__":
    unittest.main()
