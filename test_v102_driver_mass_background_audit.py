import copy
import unittest
from unittest.mock import patch

import sympy as sp

import v102_driver_mass_background_audit as audit


class TestV102DriverMassBackground(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()
        cls.parents = audit.load_inputs()
        cls.network = audit.coupling_network(cls.parents)

    def test_canonical_parents_and_fresh_validation(self):
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))
        self.assertEqual(self.report["input_core_hashes"], {k: v[1] for k, v in audit.PARENTS.items()})
        audit.validate_certificate(self.report)

    def test_actual_operator_and_parent_sources_are_freshly_bound(self):
        original = audit.file_sha
        for name in ("susy_v101_multipath_g1_frontier_master_audit.py", "test_v101_higgs_background_restriction_audit.py",
                     "susy_v90_external_c8_quotient_daifreed_rees_equivariance_audit.py",
                     "test_susy_v70_spin11_localized_parent_spin_flavor_completion_audit.py"):
            with patch.object(audit, "file_sha", side_effect=lambda p: "0"*64 if p.name == name else original(p)):
                with self.assertRaises(RuntimeError):
                    audit.load_inputs()

    def test_inherited_matrix_and_mass_chain_is_not_bypassed(self):
        original = audit.previous.file_sha
        for name in ("v93_mass_sector_symmetry_descent.py", "v92_singlet_projector_certificate.py", "v95_wall_symmetry_lift_audit.py"):
            with patch.object(audit.previous, "file_sha", side_effect=lambda p: "0"*64 if p.name == name else original(p)):
                with self.assertRaises(RuntimeError):
                    audit.load_inputs()

    def test_every_actual_V90_ledger_row_is_preserved(self):
        old = self.parents["v90"]["charged_neutral_and_compensator_repair"]["corrected_compensator"]["operator_ledger"]
        copied = self.report["source_bound_operator_network"][:17]
        self.assertEqual(len(old), 17)
        for source, row in zip(old, copied):
            self.assertEqual({k: row[k] for k in source}, source)
        self.assertEqual(sum(r["include_in_constant_tensor_system"] for r in copied), 13)

    def test_continuous_and_discrete_charge_sums_recomputed(self):
        registry = self.parents["v90"]["charged_neutral_and_compensator_repair"]["operator_charge_registry"]
        for row in self.network[:17]:
            values = [registry[f] for f in row["factors"]]
            self.assertEqual(sum(r["U1_8"] for r in values), row["U1_8_sum"])
            self.assertEqual(sum(r["U1_X"] for r in values), row["U1_X_sum"])
            self.assertEqual(sum(r["Z4R"] for r in values) % 4, row["Z4R_sum_mod4"])

    def test_each_fixed_nonzero_driver_constant_is_a_separate_constraint(self):
        rows = {row["id"]: row for row in self.network}
        for driver, constant, factors in audit.DRIVERS:
            row = rows["V90_constant_"+driver]
            self.assertEqual(row["factors"], [driver])
            self.assertEqual(row["fixed_nonzero_neutral_constant"], constant)
            self.assertEqual(sp.sympify(row["required_coefficient_line_c1"]), audit.W-audit.FIELDS[driver])
        self.assertEqual(len(self.network), 22)

    def test_V93_mass_terms_counted_once_not_as_new_particles(self):
        rows = [row for row in self.network if row["id"].startswith("V93_")]
        self.assertEqual([row["factors"] for row in rows], [["Phi_-", "S2", "S6"], ["Phi_-", "S4", "S4"]])
        self.assertEqual([row["operator_kind"] for row in rows], ["superpotential"]*2)

    def test_line_sum_handles_conjugate_B_not_an_extra_field(self):
        values = {k: v for k, v in audit.FIELDS.items()}
        self.assertEqual(audit.line_sum(["Phi_-", "B0_dag", "H_uA", "H_dC"], values),
                         values["Phi_-"]-values["B0"]+values["H_uA"]+values["H_dC"])
        self.assertNotIn("B0_dag", audit.FIELD_NAMES)

    def test_integer_network_matrix_and_rank_are_derived(self):
        equations = [z for _, z in audit.equations(self.network)]
        M, rhs = sp.linear_eq_to_matrix(equations, [audit.FIELDS[k] for k in audit.FIELD_NAMES])
        report = self.report["common_component_line_system"]
        self.assertEqual(M.shape, (26, 22))
        self.assertEqual(M, sp.Matrix(report["integer_coefficient_matrix"]))
        self.assertEqual(M.rank(), 20)
        self.assertEqual(M.row_join(rhs).rank(), 20)
        self.assertEqual(len(M.nullspace()), 2)

    def test_complete_rational_solution_and_kernel_directions(self):
        solution = audit.general_solution()
        substitutions = {audit.FIELDS[k]: v for k, v in solution.items()}
        for name, equation in audit.equations(self.network):
            self.assertEqual(sp.expand(equation.subs(substitutions, simultaneous=True)), 0, name)
        report = self.report["common_component_line_system"]
        matrix = sp.Matrix(report["integer_coefficient_matrix"])
        directions = sp.Matrix([[sp.sympify(z) for z in row] for row in report["nullspace_parameter_directions"]])
        self.assertEqual(directions.rank(), 2)
        self.assertEqual(matrix*directions, sp.zeros(26, 2))

    def test_GM_adds_a_real_independent_constraint(self):
        variables = [audit.FIELDS[k] for k in audit.FIELD_NAMES]
        full, _ = sp.linear_eq_to_matrix([z for _, z in audit.equations(self.network)], variables)
        reduced, _ = sp.linear_eq_to_matrix([z for _, z in audit.equations(self.network, False)], variables)
        self.assertEqual((reduced.rank(), full.rank()), (19, 20))
        sol = audit.general_solution()
        self.assertEqual(sp.expand(sol["H_uA"]+sol["H_dC"]), 0)

    def test_V101_actual_B0_weight_fails_fixed_driver(self):
        B = audit.previous.scalar_line(sp.Rational(1, 2), sp.Rational(1, 2), 1, 4, "plus")
        self.assertEqual(B, 3)
        diag = self.report["V101_unretuned_H3_obstruction"]
        self.assertEqual(diag["B0_degree"], B)
        self.assertEqual(diag["SB_Phi_minus_B0_squared_product_degree_with_SB2"], 2+2*B)
        self.assertEqual(diag["hypothetical_vB_squared_spurion_degree_to_avoid_conflict"], 6)
        self.assertFalse(diag["spurions_or_charged_constants_installed"])

    def test_B_only_retuning_still_fails_constant_GM(self):
        diag = self.report["V101_unretuned_H3_obstruction"]["B_only_retuning"]
        self.assertEqual(audit.previous.scalar_line(sp.Rational(1, 2), sp.Rational(-5, 2), 1, 4, "plus"), 0)
        self.assertEqual(diag["GM_product_degree_if_A_C_unchanged"], 8)
        self.assertEqual(diag["required_GM_coefficient_line_degree"], -8)
        self.assertFalse(diag["all_written_constant_tensors_preserved"])

    def test_actual_H3_roots_recover_all_five_bulk_scalar_weights(self):
        roots = {"A": audit.h-audit.r-3*audit.d, "B": -audit.r-2*audit.d, "C": -audit.h-audit.r-3*audit.d}
        values = audit.general_solution()
        for field, hyper, q, side in (("H_uA", "A", 6, "plus"), ("A0", "A", 6, "minus"),
                                       ("B0", "B", 4, "plus"), ("H_uB", "B", 4, "minus"),
                                       ("H_dC", "C", 6, "plus")):
            self.assertEqual(audit.previous.scalar_line(audit.r, roots[hyper], audit.d, q, side), sp.expand(values[field]))

    def test_bulk_Sigma_derivative_character_retained(self):
        values = audit.general_solution()
        self.assertEqual(values["H_dSigma"], audit.x)
        self.assertEqual(sp.expand(values["B0"]+values["H_uB"]+values["H_dSigma"]), audit.W)
        self.assertIn("not a newly installed arbitrary local Sigma polynomial", self.report["common_component_line_system"]["bulk_Sigma_boundary"])

    def test_all_CP3_integer_family_members_pass_tensor_equations(self):
        for k in range(-5, 6):
            for sd in (-2, 0, 1, 3):
                values = audit.cp3_values(k, sd)
                self.assertTrue(all(value.q == 1 for value in values.values()))
                for row in self.network:
                    if row["include_in_constant_tensor_system"]:
                        target = 2 if row["operator_kind"] == "superpotential" else 0
                        self.assertEqual(audit.line_sum(row["factors"], values), target)
                self.assertTrue(all(values[field] == 0 for field in audit.VEVS))

    def test_CP3_even_h_condition_is_necessary_for_genuine_matter_line(self):
        for h0 in range(-7, 8):
            ten = (2-sp.Integer(h0))/2
            self.assertEqual(ten.q == 1, h0 % 2 == 0)
        self.assertEqual(audit.cp3_values(0)["10"], 1)

    def test_k0_small_degree_assignment_is_explicit(self):
        row = self.report["CP3_common_tensor_witness_k0"]
        v = row["selected_component_degrees"]
        self.assertTrue(all(v[field] == 0 for field in audit.VEVS))
        self.assertEqual([v[f] for f in ("10", "5bar", "1", "A0", "P_A", "H_uB", "H_dSigma", "S2", "S4", "S6")], [1]*10)
        self.assertEqual([v[f] for f in ("Dbar", "S8", "SB", "SX")], [2]*4)
        self.assertEqual([v[f] for f in ("H_uA", "H_dC", "D")], [0]*3)

    def test_k2_leaves_A_flavor_root_unchanged(self):
        row = self.report["CP3_common_tensor_witness_k2"]
        roots = list(map(sp.sympify, row["old_H3_matrix_certificate"]["positive_roots"]))
        self.assertEqual(roots, [sp.Rational(1, 2), sp.Rational(-5, 2), sp.Rational(-15, 2)])
        self.assertEqual([row["selected_component_degrees"][f] for f in ("H_uA", "H_dC", "10", "5bar", "1")], [4, -4, -1, 7, -9])

    def test_full_H3_generator_commutes_with_source_twists_R_charge(self):
        for key in ("CP3_common_tensor_witness_k0", "CP3_common_tensor_witness_k2"):
            row = self.report[key]["old_H3_matrix_certificate"]
            H = audit.matrix(row["paired_generator"])
            for name in ("actual_A3", "actual_H_AC", "actual_Rtilde", "continuous_charge_matrix"):
                M = audit.matrix(row[name])
                self.assertEqual(H*M, M*H)
            self.assertTrue(all(row["checks"].values()))

    def test_H3_symplectic_and_full_scalar_reality_not_doubled(self):
        row = self.report["CP3_common_tensor_witness_k0"]["old_H3_matrix_certificate"]
        H, full = audit.matrix(row["paired_generator"]), audit.matrix(row["full_scalar_weight_generator"])
        J = audit.previous.projectors.symplectic_form(3)
        B = sp.kronecker_product(audit.previous.projectors.symplectic_form(1), J)
        self.assertEqual(H.T*J+J*H, sp.zeros(6))
        self.assertEqual(B*sp.conjugate(B), sp.eye(12))
        self.assertEqual(B*sp.conjugate(full)+full*B, sp.zeros(12))
        self.assertEqual(row["existing_H3_hyper_count"], 3)
        self.assertFalse(row["new_H3_matter_installed"])

    def test_H3_endpoint_and_known_Gamma_cocycle_unchanged(self):
        for k in range(-4, 5):
            values = [2*k-sp.Rational(7, 2), -sp.Rational(5, 2), -2*k-sp.Rational(7, 2)]
            self.assertTrue(all(sp.simplify(sp.exp(2*sp.pi*sp.I*z)) == -1 for z in values))
        endpoint = tuple(self.report["CP3_common_tensor_witness_k0"]["full_known_cocharacter_endpoint"])
        self.assertIn(endpoint, audit.previous.center.old_kernel())
        self.assertEqual(endpoint, (0, 1, 0, 1, 1, 1, 1))

    def test_fixed_mass_and_mixing_coefficient_lines_are_the_same(self):
        values = audit.general_solution()
        self.assertEqual(sp.expand(values["D"]-values["H_uA"]), 0)
        self.assertEqual(sp.expand(values["D"]+values["Dbar"]), audit.W)
        self.assertEqual(sp.expand(values["H_uA"]+values["Dbar"]), audit.W)
        self.assertEqual(values["Phi_-"]+values["B0"], 0)

    def test_one_sided_tree_elimination_remains_local_algebra(self):
        D, Db, Hu, Am, M, mu = sp.symbols("D Db Hu Am M mu", nonzero=True)
        W = M*D*Db+mu*Hu*Db+D*Am
        effective = sp.expand(W.subs({D: -mu*Hu/M, Db: -Am/M}, simultaneous=True))
        self.assertEqual(effective, -mu*Hu*Am/M)
        self.assertEqual(sp.diff(effective, Am, 2), 0)
        self.assertFalse(self.report["F_D_and_spectrum_boundary"]["mass_gap_of_entire_background_proved"])

    def test_optional_legacy_Majorana_selects_k0_not_silently_installed(self):
        row = self.report["legacy_and_forbidden_boundary"]["optional_V70_Majorana"]
        self.assertEqual(row["V90_charge_X_R_totals"], [0, 0, 2])
        self.assertEqual(sp.sympify(row["additional_constant_tensor_residual"]), -5*audit.h)
        self.assertEqual(2*audit.cp3_values(0)["1"]+audit.cp3_values(0)["X"], 2)
        self.assertNotEqual(2*audit.cp3_values(2)["1"]+audit.cp3_values(2)["X"], 2)
        self.assertFalse(row["explicitly_reinstalled_in_V90_operator_ledger"])
        self.assertFalse(row["adopted_as_new_action_term"])

    def test_no_forbidden_or_superseded_terms_imported(self):
        row = self.report["legacy_and_forbidden_boundary"]
        self.assertEqual(len(row["V90_forbidden_rows_retained_not_added"]), 4)
        self.assertEqual(row["nonimportable_legacy_terms_continuous_charge_sums"], {"A0 H_uA H_dC": 6, "H_uB H_dC": 2})
        self.assertFalse(row["forbidden_operators_promoted_by_Chern_class_coincidence"])
        self.assertTrue(all(r["Z4R_sum_mod4"] == 0 for r in row["V90_forbidden_rows_retained_not_added"]))

    def test_P_target_unchanged_but_other_flavor_anomalies_not_discarded(self):
        H = sp.Symbol("H")
        Q = (H**3+H*H**2/2)/4
        self.assertEqual(Q.coeff(H, 3), sp.Rational(3, 8))
        for key in ("CP3_common_tensor_witness_k0", "CP3_common_tensor_witness_k2"):
            self.assertEqual(self.report[key]["P_over4_period"], "3/8")
            self.assertTrue(self.report[key]["normal_R_gauge_curvatures_unchanged"])
            self.assertFalse(self.report[key]["full_new_background_anomaly_recomputed"])
            self.assertFalse(self.report[key]["D4_trivial"])

    def test_linear_parallel_sections_not_promoted_to_QK_vacuum(self):
        row = self.report["CP3_common_tensor_witness_k0"]
        self.assertTrue(row["linear_associated_weight_zero_sections_can_be_parallel"])
        self.assertFalse(row["unbroken_supercharge_or_SUSY_vacuum_constructed"])
        self.assertFalse(row["full_same_action_physical_background_proved"])
        self.assertFalse(row["localized_component_line_weights_are_full_representations"])

    def test_UV_zeros_finite_stabilizer_and_N40_boundaries_remain(self):
        row = self.report["F_D_and_spectrum_boundary"]
        self.assertEqual(row["external_gauge_only_VEV_charge_gcd"], 2)
        self.assertFalse(row["gcd2_is_full_internal_R_flavor_stabilizer"])
        self.assertFalse(row["finite_residual_anomaly_computed"])
        self.assertFalse(row["old_N40_replacement_can_borrow_this_Phi_sector"])
        self.assertTrue(row["drivers_are_not_assumed_to_have_nonzero_VEVs"])
        self.assertTrue(row["linear_driver_terms_still_impose_tensor_constraints_at_zero_driver_VEV"])

    def test_invalid_integral_parameter_inputs_rejected(self):
        for value in (True, 0.0, sp.Rational(1, 2)):
            with self.assertRaises(ValueError):
                audit.cp3_values(value)
            with self.assertRaises(ValueError):
                audit.cp3_values(0, value)
            with self.assertRaises(ValueError):
                audit.H3_matrix_certificate(self.parents, value)

    def test_rehashed_false_background_or_field_degree_rejected(self):
        for key, value in (("full_same_action_physical_background_proved", True), ("P_over4_period", "0")):
            out = copy.deepcopy(self.report)
            out["CP3_common_tensor_witness_k0"][key] = value
            out["core_sha256"] = audit.canonical_sha(out)
            with self.assertRaises(RuntimeError):
                audit.validate_certificate(out)

    def test_all_gates_and_full_representation_obligations_open(self):
        row = self.report["terminal_decision"]
        self.assertEqual(row["closed_gates"], [])
        for key in ("all_localized_Gammahat_representations_constructed", "all_global_QK_and_constant_tensor_stabilizers_constructed",
                    "full_spectrum_vacuum_or_anomaly_completion", "same_action_microscopic_parent_accepted", "theory_complete"):
            self.assertFalse(row[key])
        self.assertTrue(row["written_constant_tensor_network_reconstructed"])
        self.assertTrue(row["restricted_CP3_common_tensor_weights_constructed"])


if __name__ == "__main__":
    unittest.main()
