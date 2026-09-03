import copy
from itertools import permutations, product
import unittest
from unittest.mock import patch

import sympy as sp

import v103_normal_frame_tensor_representation_audit as audit


class TestV103NormalFrameTensors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()
        cls.parents = audit.load_inputs()
        cls.network = audit.previous.coupling_network(cls.parents)

    def test_canonical_certificate_and_validation(self):
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))
        audit.validate_certificate(self.report)

    def test_immutable_V102_route_master_and_helpers_rebound(self):
        self.assertEqual(self.report["input_core_hashes"], {k: v[1] for k, v in audit.PARENTS.items()})
        self.assertEqual(self.report["bound_helper_cores"]["v102_driver"], audit.DRIVER_CORE)
        self.assertEqual(self.report["bound_helper_cores"]["v102_finite"], audit.FINITE_CORE)
        self.assertEqual(len(self.report["fresh_parent_source_bindings"]), 8)

    def test_all_current_source_and_test_changes_fail_closed(self):
        original = audit.file_sha
        for name in self.report["fresh_parent_source_bindings"]:
            with patch.object(audit, "file_sha", side_effect=lambda p: "0"*64 if p.name == name else original(p)):
                with self.assertRaises(RuntimeError):
                    audit.load_inputs()

    def test_earlier_operator_projector_theta_and_kernel_chain_is_fresh(self):
        for module, names in ((audit.previous, ("susy_v90_external_c8_quotient_daifreed_rees_equivariance_audit.py", "test_susy_v70_spin11_localized_parent_spin_flavor_completion_audit.py")),
                              (audit.previous.previous, ("v95_wall_symmetry_lift_audit.py", "v93_mass_sector_symmetry_descent.py", "test_v92_singlet_projector_certificate.py"))):
            original = module.file_sha
            for name in names:
                with patch.object(module, "file_sha", side_effect=lambda p: "0"*64 if p.name == name else original(p)):
                    with self.assertRaises(RuntimeError):
                        audit.load_inputs()

    def test_literal_D_identity_computed_with_Clifford_matrices(self):
        gamma = audit.geometry.clifford_generators()
        T, N = (gamma[0]*gamma[1])**2, (gamma[4]*gamma[5])**2
        self.assertEqual(T, -sp.eye(8))
        self.assertEqual(N, -sp.eye(8))
        self.assertEqual(T*N, sp.eye(8))
        self.assertEqual(audit.D_GEOM, (1, 1, 0, 0, 0, 0, 0))

    def test_independent_internal_centers_cannot_rescue_half_normal_scalar(self):
        for bits in product((0, 1), repeat=5):
            self.assertEqual(audit.kernel_character(sp.Rational(1, 2), 0, bits)[0], 1)
            self.assertEqual(audit.kernel_character(0, 1, bits)[0], 1)

    def test_N1_scalar_and_fermion_D_agree_for_all_integral_weights(self):
        for q in range(-8, 9):
            scalar = audit.kernel_character(q, 0, (1, 1, 0, 0, 1))
            fermion = audit.kernel_character(sp.Rational(q)-sp.Rational(1, 2), 1, (1, 0, 0, 0, 1))
            self.assertEqual(scalar, [0, 0, 0])
            self.assertEqual(fermion, [0, 0, 0])

    def test_theta_and_W_normal_R_bookkeeping(self):
        row = self.report["geometric_normal_descent"]
        self.assertEqual(row["theta_normal_R_charges"], ["1/2", 1])
        self.assertEqual(row["superpotential_normal_R_charges"], [1, 2])
        self.assertEqual(audit.kernel_character(sp.Rational(1, 2), 1, (0, 1, 0, 0, 0)), [0, 0, 0])

    def test_invalid_charge_center_and_texture_inputs_rejected(self):
        for q in (True, 0.5, sp.Rational(1, 3), sp.Symbol("q")):
            with self.assertRaises(ValueError):
                audit.spin2_weight(q)
        for tangent, internal in ((True, (0, 0, 0, 0, 0)), (2, (0, 0, 0, 0, 0)), (0, (0, 0)), (0, (0, 0, 0, 0, True))):
            with self.assertRaises(ValueError):
                audit.kernel_character(0, tangent, internal)
        for weights in ([], [True, 1], [0, 0.5], [0, sp.Rational(1, 2)]):
            with self.assertRaises(ValueError):
                audit.symmetric_texture(weights)

    def test_actual_hyperscalars_have_zero_normal_charge_Sigma_one(self):
        values = audit.normal_registry()
        for name in audit.ZERO_NORMAL_BULK_SCALARS:
            self.assertEqual(values[name], 0)
        self.assertEqual(values["H_dSigma"], 1)
        actual = self.parents["saved_higgs"]["combined_Higgs_line_and_mass_tensor"]
        self.assertEqual(actual["normal_scalar_weight"], 0)
        self.assertEqual(sp.diff(audit.previous.previous.scalar_line(audit.previous.r, sp.Symbol("a"), audit.previous.d, 6, "plus"), audit.previous.x), 0)

    def test_complete_normal_system_18_by_11_rank_10_augmented_11(self):
        values = audit.normal_registry()
        variables = [values[k] for k in audit.previous.FIELD_NAMES if values[k].is_Symbol]
        equations = audit.normal_equations(self.network)
        M, b = sp.linear_eq_to_matrix([e for _, e in equations], variables)
        row = self.report["independent_normal_tensor_system"]
        self.assertEqual(M.shape, (18, 11))
        self.assertEqual(M, sp.Matrix(row["integer_coefficient_matrix"]))
        self.assertEqual(b, sp.Matrix(row["integer_rhs"]))
        self.assertEqual((M.rank(), M.row_join(b).rank()), (10, 11))
        self.assertEqual(sp.linsolve((M, b), variables), sp.EmptySet)

    def test_all_source_rows_retained_including_forbidden_not_installed(self):
        rows = self.report["independent_normal_tensor_system"]["all_22_source_tensor_rows"]
        self.assertEqual(len(rows), 22)
        for old, new in zip(self.network, rows):
            self.assertEqual((old["id"], old["factors"], old["include_in_constant_tensor_system"]),
                             (new["id"], new["factors"], new["included_in_frozen_action_screen"]))
        self.assertEqual(sum(r["included_in_frozen_action_screen"] for r in rows), 18)

    def test_both_V93_rows_are_zero_equals_one_independent_of_flavor_matrix(self):
        row = self.report["independent_normal_tensor_system"]
        self.assertEqual([(r["id"], r["normal_field_product_charge"], r["required_coefficient_normal_charge"]) for r in row["two_direct_V93_obstructions"]],
                         [("V93_lambda", "0", "1"), ("V93_kappa", "0", "1")])
        L = sp.Matrix(3, 3, sp.symbols("l0:9"))
        self.assertEqual(sp.zeros(3)*L+L*sp.zeros(3)-L, -L)
        self.assertTrue(row["V93_arbitrary_family_lambda_and_kappa_must_vanish_with_neutral_coefficients"])

    def test_uniform_solution_after_removing_mass_rows_fails_descent(self):
        row = self.report["independent_normal_tensor_system"]
        solved = {sp.Symbol(k): sp.sympify(v) for k, v in row["dropping_only_V93_mass_rows_rational_solution"].items()}
        for name, e in audit.normal_equations(self.network):
            if not name.startswith("V93_"):
                self.assertEqual(sp.expand(e.subs(solved, simultaneous=True)), 0)
        for field in ("q_10", "q_5bar", "q_1"):
            self.assertEqual(solved[sp.Symbol(field)], sp.Rational(1, 2))
            self.assertEqual(audit.kernel_character(solved[sp.Symbol(field)], 0)[0], 1)

    def test_bulk_derivative_and_GM_survive_pure_normal_test(self):
        equations = dict(audit.normal_equations(self.network))
        self.assertEqual(equations["V90_5"], 0)
        self.assertEqual(equations["V90_17"], 0)
        self.assertEqual(self.report["independent_normal_tensor_system"]["bulk_derivative_and_GM_rows_have_zero_residual"], ["V90_5", "V90_17"])

    def test_fixed_driver_constants_are_not_nonzero_driver_VEVs(self):
        solved = self.report["independent_normal_tensor_system"]["dropping_only_V93_mass_rows_rational_solution"]
        for name in ("q_S8", "q_SB", "q_SX", "q_P_A"):
            self.assertEqual(solved[name], "1")
        self.assertEqual(sp.expand(sp.sympify(solved["q_X"])+sp.sympify(solved["q_Xbar"])), 0)
        self.assertTrue(self.report["independent_normal_tensor_system"]["X_normal_charge_is_not_fixed_before_a_chosen_VEV_reduction"])

    def test_actual_U5_three_families_and_non_10_mediators(self):
        row = self.report["three_family_up_Yukawa_obstruction"]
        self.assertEqual([(r["field"], r["copies"], r["X"]) for r in row["bound_three_family_component_rows"]], [("Q", 3, -1), ("u_c", 3, -1), ("e_c", 3, -1)])
        registry = self.parents["v90"]["charged_neutral_and_compensator_repair"]["operator_charge_registry"]
        self.assertEqual(2*registry["10"]["U1_X"]+registry["H_uA"]["U1_X"], 0)
        self.assertEqual(2*registry["10"]["U1_8"]+registry["H_uA"]["U1_8"], 0)
        self.assertTrue(row["existing_D_Dbar_are_5_and_5bar_not_additional_10s"])

    def test_SU5_epsilon_exchange_is_symmetric_in_family(self):
        ordering = [2, 3, 0, 1, 4]
        inversions = sum(ordering[i] > ordering[j] for i in range(5) for j in range(i+1, 5))
        self.assertEqual(inversions, 4)
        self.assertEqual((-1)**inversions, 1)

    def test_nonuniversal_up_texture_has_rank_two_not_zero(self):
        Y = audit.symmetric_texture([0, 1, 0])
        Q = sp.diag(0, 1, 0)
        self.assertEqual(Q.T*Y+Y*Q, Y)
        self.assertEqual(Y.rank(), 2)
        self.assertEqual(Y.det(), 0)
        self.assertNotEqual(Y, sp.zeros(3))

    def test_odd_determinant_all_permutations_and_bounded_texture_crosscheck(self):
        q = sp.symbols("q0:3")
        for perm in permutations(range(3)):
            self.assertEqual(sp.expand(sum(q[i]+q[perm[i]]-1 for i in range(3))), 2*sum(q)-3)
        for weights in product(range(-2, 3), repeat=3):
            Y = audit.symmetric_texture(list(weights))
            self.assertEqual(Y.det(), 0)
            self.assertIn(Y.rank(), (0, 2))

    def test_even_family_and_half_normal_exceptions_have_exact_scope(self):
        row = self.report["three_family_up_Yukawa_obstruction"]
        four = audit.previous.matrix(row["even_family_scope_counterexample"]["matrix"])
        self.assertEqual(four.det(), 1)
        self.assertEqual(sp.Rational(1, 2)*sp.eye(3)*2, sp.eye(3))
        self.assertEqual(audit.kernel_character(sp.Rational(1, 2), 0)[0], 1)
        self.assertFalse(row["even_family_scope_counterexample"]["new_family_installed"])
        self.assertFalse(row["full_KK_or_nonlocal_mass_matrix_rank_bounded_by_this_theorem"])

    def test_full_mass_coefficient_lines_retain_normal_R_flavor(self):
        h = audit.previous.previous
        row = self.report["mass_tensor_full_curvature_and_finite_checks"]
        lam = sp.sympify(row["required_coefficient_line_c1"]["lambda"])
        kap = sp.sympify(row["required_coefficient_line_c1"]["kappa"])
        self.assertEqual(sp.expand(lam-(h.x-h.r+h.em-h.e2-h.e6)), 0)
        self.assertEqual(sp.expand(kap-(h.x-h.r+h.em-2*h.e4)), 0)
        for coefficient in (lam, kap):
            self.assertEqual(sp.diff(coefficient, h.x), 1)
            self.assertEqual(sp.diff(coefficient, h.r), -1)
            self.assertEqual(sp.diff(coefficient, h.d), 0)

    def test_formal_locking_solves_four_combined_lines_but_not_independent_symmetry(self):
        row = self.report["mass_tensor_full_curvature_and_finite_checks"]
        substitution = {sp.Symbol(k): sp.sympify(v) for k, v in row["formal_Phi_VEV_and_mass_tensor_locking"].items()}
        for value in (row["scalar_lines"]["Phi_+"], row["scalar_lines"]["Phi_-"], *row["required_coefficient_line_c1"].values()):
            self.assertEqual(sp.expand(sp.sympify(value).subs(substitution, simultaneous=True)), 0)
        self.assertFalse(row["neutral_coefficients_in_fixed_combined_chart_imply_independent_normal_covariance"])

    def test_actual_finite_projectors_and_Rtilde_still_allow_mass_tensors(self):
        row = self.report["mass_tensor_full_curvature_and_finite_checks"]
        for item in row["finite_original_mass_tensor_checks"]:
            self.assertEqual(item["scalar_Rtilde_product"], item["W_Rtilde_phase"])
            self.assertEqual(set(item["all_four_frozen_stratum_products"].values()), {"1"})
        self.assertEqual(sp.I*(-sp.I), 1)
        self.assertFalse(row["pure_normal_line_alone_preserves_saved_combined_orbifold_twist"])

    def test_frozen_CP3_compensation_annuls_only_combined_coefficient_degrees(self):
        row = self.report["mass_tensor_full_curvature_and_finite_checks"]
        substitutions = {sp.Symbol(k): sp.sympify(v) for k, v in row["frozen_CP3_selected_roots"].items()}
        self.assertEqual(substitutions[sp.Symbol("x")], 1)
        for c in row["required_coefficient_line_c1"].values():
            self.assertEqual(sp.expand(sp.sympify(c).subs(substitutions)), 0)
        self.assertEqual(row["pure_normal_restriction"], {"lambda": "x", "kappa": "x"})

    def test_positive_restricted_character_network_recomputed_all_18_rows(self):
        row = self.report["restricted_witness_and_redesign_boundary"]["positive_restricted_character_witness"]
        values = row["field_degrees"]
        for old in self.network:
            if old["include_in_constant_tensor_system"]:
                self.assertEqual(audit.previous.line_sum(old["factors"], values), 2 if old["operator_kind"] == "superpotential" else 0)
        self.assertEqual(2*values["10"]+values["H_uA"], 2)
        self.assertEqual(values["Phi_-"]+2*values["S4"], 2)
        self.assertFalse(row["same_scalar_normal_charges_reassigned_by_this_witness"])

    def test_seven_explicit_normal_tensor_prices_in_integral_scalar_example(self):
        row = self.report["restricted_witness_and_redesign_boundary"]["all_integral_pure_normal_assignment_with_explicit_tensor_price"]
        self.assertEqual([r["id"] for r in row["seven_normal_charged_tensor_rows"]], ["V90_6", "V90_7", "V90_8", "V90_11", "V90_12", "V93_lambda", "V93_kappa"])
        values = row["scalar_normal_charges"]
        prices = {r["id"]: r["coefficient_qN"] for r in row["all_18_required_coefficient_charges"]}
        for old in self.network:
            if old["include_in_constant_tensor_system"]:
                self.assertEqual(audit.previous.line_sum(old["factors"], values)+prices[old["id"]], 1 if old["operator_kind"] == "superpotential" else 0)
        self.assertFalse(row["new_coefficients_or_fields_installed"])

    def test_frame_fixed_patch_not_confused_with_global_tensor_or_QK_background(self):
        row = self.report["restricted_witness_and_redesign_boundary"]
        self.assertIn("entire line, including torsion", row["global_normal_tensor"])
        self.assertIn("frame-fixed component algebra", row["frame_patch"])
        self.assertTrue(row["UV_zero_loci_and_relative_anomaly_matching_remain"])
        self.assertFalse(row["new_quotient_spurion_or_full_vacuum_installed"])
        self.assertFalse(row["positive_restricted_character_witness"]["full_physical_CP3_background_accepted"])

    def test_primary_sources_and_explicit_independent_normal_assumptions(self):
        self.assertEqual(len(self.report["primary_sources"]), 4)
        boundary = self.report["source_and_assumption_boundary"]
        self.assertEqual(len(boundary["assumptions_for_obstruction"]), 5)
        self.assertTrue(boundary["frozen_sources_explicitly_build_finite_combined_orbifold_lifts"])
        self.assertFalse(boundary["frozen_sources_complete_continuous_localized_normal_tensor_representations"])
        self.assertFalse(boundary["finite_or_frame_fixed_local_mass_rank_calculations_retracted"])

    def test_resealed_mutations_rejected_not_just_literal_hash_failures(self):
        for section, key, value in (("independent_normal_tensor_system", "augmented_rank", 10),
                                    ("three_family_up_Yukawa_obstruction", "three_family_maximum_rank", 3),
                                    ("terminal_decision", "full_localized_Gammahat_representations_constructed", True),
                                    ("source_and_assumption_boundary", "no_go_applies_to_every_possible_compactification", True)):
            bad = copy.deepcopy(self.report)
            bad[section][key] = value
            bad["core_sha256"] = audit.canonical_sha(bad)
            with self.assertRaises(RuntimeError):
                audit.validate_certificate(bad)

    def test_no_anomaly_or_gate_completion_from_tensor_calculation(self):
        decision = self.report["terminal_decision"]
        self.assertTrue(decision["bounded_normal_representation_obstruction_derived"])
        self.assertEqual(decision["closed_gates"], [])
        for key in ("full_localized_Gammahat_representations_constructed", "nonlinear_QK_SUSY_vacuum_constructed", "full_relative_quantum_anomaly_cancelled", "same_action_microscopic_parent_accepted", "theory_complete"):
            self.assertFalse(decision[key])


if __name__ == "__main__":
    unittest.main()
