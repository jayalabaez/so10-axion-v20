import copy
import itertools
import json
import unittest
from fractions import Fraction as F

import sympy as sp

import susy_v91_spinc_quantization_tensor_cone_finite_torsion_audit as audit


class TestV91QuantizationTensorConeFiniteTorsion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report()

    def test_canonical_parent_bindings(self):
        self.assertEqual(self.report["input_core_hashes"],
                         {key:core for key,(_,core) in audit.PARENTS.items()})
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))

    def test_positive_sheet_is_excluded_for_every_positive_t(self):
        for t in (F(1,100), F(1,2), F(1), F(2), F(100)):
            self.assertLess(audit.dot([t,1/(2*t)],[-480,-152]),0)
            self.assertLess(audit.dot([t,1/(2*t)],[-472,-148]),0)
        theorem = self.report["tensor_cone"]["universal_positive_sheet_no_go"]
        self.assertTrue(theorem["covers_arbitrary_charged_singlet_reassignments"])
        self.assertFalse(theorem["covers_other_tensor_lattices_or_R_gauging"])

    def test_negative_sheet_gauge_chamber_and_boundary(self):
        for t in (F(1,2),F(1),F(3,2),F(2),F(17)):
            j = [-t,-1/(2*t)]
            self.assertEqual(audit.dot(j,j),1)
            self.assertEqual(audit.dot(j,[2,-1]) > 0,t > 1)
            self.assertGreater(audit.dot(j,[-472,-148]),0)

    def test_F4_map_and_effective_tensions(self):
        self.assertEqual(audit.f4_class([2,2]),[-2,-6])
        self.assertEqual(audit.f4_class([2,-1]),[1,0])
        self.assertEqual(audit.f4_class([-472,-148]),[148,768])
        self.assertEqual(audit.f4_dot([148,768],[1,0]),176)
        for m,n in itertools.product(range(4),repeat=2):
            if m or n:
                self.assertGreater(audit.f4_dot([F(1,4),F(5,2)],[m,n]),0)

    def test_tensor_metric_positive_definite(self):
        row = self.report["tensor_cone"]
        self.assertEqual(row["tensor_metric_determinant"],"1")
        t = sp.symbols("t",positive=True)
        matrix = sp.Matrix([[sp.sympify(x,locals={"t":t}) for x in r]
                            for r in row["tensor_metric"]])
        self.assertEqual(sp.simplify(matrix.det()),1)
        self.assertTrue(matrix[0,0].is_positive)
        self.assertFalse(row["tensor_modulus_stabilized"])

    def test_old_quotient_obstruction_has_exact_order_two(self):
        for sign,expected in ((1,[-59,F(-39,2)]),(-1,[-61,F(-37,2)])):
            value = audit.quotient_quadratic([-480,-152],sign=sign)
            self.assertEqual(value,expected)
            self.assertFalse(audit.integral(value))
            self.assertTrue(audit.integral([2*x for x in value]))
        self.assertEqual(self.report["old_quotient_obstruction"]["residue_mod_U_for_either_convention"],["0","1/2"])

    def test_CP3_witness_and_convention_labels(self):
        row = self.report["old_quotient_obstruction"]["CP3_witness"]
        self.assertEqual(row["standard_MMP_full_Y_period"],["-57","-35/2"])
        self.assertEqual(row["frozen_V71_full_Y_period"],["-59","-33/2"])
        self.assertTrue(row["spin"])
        self.assertFalse(row["CP2_itself_required_to_be_spin"])
        self.assertFalse(row["gravity_or_Wu_shift_repairs_this_half_integral_residue"])
        self.assertFalse(self.report["old_quotient_obstruction"]["conventions_fully_reconciled_at_local_action_level"])

    def test_old_product_quantization_is_not_enough(self):
        self.assertTrue(audit.integral([F(-480,2),F(-152,2)]))
        old = audit.cocharacter_certificate([-480,-152])
        self.assertTrue(old["gram_entries_integral"])
        self.assertFalse(old["gram_diagonal_even_in_U"])
        self.assertFalse(old["all_cocharacters_quantized"])

    def test_new_moments_and_anomaly_equations(self):
        row = self.report["quantized_scout"]
        self.assertEqual(row["singlet_counts_by_q0_q2_q4_q6_q8"],[144,3,19,11,90])
        self.assertEqual(row["moments"],{"bulk_D2":968,"bulk_D4":31328,
            "singlet_D2":6472,"singlet_D4":387808,"D2":7440,"D4":419136,"P":88})
        self.assertEqual(row["H_V_T"],[300,56,1])
        self.assertTrue(all(row["checks"].values()))

    def test_complete_cocharacter_basis_gram(self):
        row = self.report["quantized_scout"]["complete_cocharacter_certificate"]
        self.assertEqual(row["gram"][0][0],["-116","-38"])
        self.assertEqual(row["gram"][0][1],["-118","-37"])
        self.assertEqual(row["gram"][0][5],["-236","-74"])
        self.assertEqual(row["gram"][5][5],["-472","-148"])
        self.assertTrue(row["all_cocharacters_quantized"])

    def test_integer_combination_quantization_independently(self):
        c,b = [-472,-148],[2,-1]
        for v in itertools.product((-1,0,1),repeat=5):
            for shift in (-1,0,1):
                s = F(sum(v),2)+shift
                k = sum(x*x for x in v)
                self.assertTrue(audit.integral([F(b[i]*k,2)+F(c[i],2)*s*s for i in range(2)]))

    def test_fixed_moment_enumeration_and_unique_minimum(self):
        row = self.report["quantized_scout"]["fixed_target_moment_search"]
        self.assertEqual(row["count"],23)
        self.assertEqual(row["minimizer_count"],1)
        self.assertEqual(row["minimum_L1_count_change"],24)
        self.assertEqual(row["minimum_hyper_charge_reassignments"],12)
        for solution in row["solutions"]:
            counts = solution["counts_q0_q2_q4_q6_q8"]
            self.assertGreaterEqual(min(counts),0)
            self.assertEqual(sum(counts),267)
            self.assertEqual(sum(n*q*q for n,q in zip(counts,(0,2,4,6,8))),6472)
            self.assertEqual(sum(n*q**4 for n,q in zip(counts,(0,2,4,6,8))),387808)
        self.assertFalse(row["global_optimum_over_all_c_or_all_charge_sets_claimed"])

    def test_H4_and_noncentral_section_scope(self):
        row = self.report["finite_G8_topology"]
        self.assertEqual(row["integral_H4"]["group"],"Z{lambda_c} direct_sum Z/4{x^2}")
        section = row["noncentral_component_section"]
        self.assertTrue(section["ordinary_spin_bordism_BC4_is_retract"])
        self.assertFalse(section["section_is_central"])
        self.assertFalse(section["SO11_x_C4_double_cover_extension_trivialized"])
        self.assertFalse(section["G8_is_direct_product_Spin11_x_C4"])

    def test_all_torsion_choices_and_restrictions(self):
        row = self.report["finite_G8_topology"]
        self.assertEqual(row["topological_refinement_count_before_WCS_compatibility"],16)
        self.assertEqual(row["distinct_central_C8_images"],[[0,2],[0,6],[4,2],[4,6]])
        self.assertEqual(row["preimages_per_central_C8_image"],[4]*4)
        self.assertEqual(row["new_scout_frozen_tau"],["-60","-18"])
        self.assertEqual(row["new_scout_tau_mod4"],[0,2])
        self.assertEqual(row["new_scout_central_C8_image_mod8"],[4,6])

    def test_finite_source_is_not_anomaly_character(self):
        row = self.report["finite_G8_topology"]
        for key in ("nonzero_Y_class_is_by_itself_an_anomaly_failure",
                    "torsion_source_choices_are_anomaly_free_actions",
                    "ordinary_OmegaSpin7_BG8_computed",
                    "full_Gammahat_tangential_structure_frozen",
                    "ordinary_spin_bordism_is_full_physical_problem",
                    "relative_fixed_wall_WCS_trivialization_constructed"):
            self.assertFalse(row[key])

    def test_exact_generic_fiber_no_identity_base_root(self):
        row = self.report["geometry"]["generic_fiber"]
        self.assertEqual(row["quartic_coefficients"],[-1,1,-2,0,3])
        self.assertEqual((row["I"],row["J"],row["four_I_cubed_minus_J_squared"]),(-32,367,-265761))
        self.assertEqual(F(row["j"]),F(8388608,9843))
        self.assertTrue(row["all_deck_roots_over_identity_F4_base_excluded"])
        self.assertFalse(row["nonidentity_base_or_nonfibration_preserving_roots_excluded"])

    def test_norm_reduction_does_not_exclude_all_complex_roots(self):
        row = self.report["geometry"]["quadratic_extension_norm_reduction"]
        self.assertEqual(row["manifest_sigma_f_minus_f"],"0")
        self.assertTrue(row["all_lifts_of_manifest_sigma_excluded"])
        self.assertFalse(row["all_complex_roots_excluded"])

    def test_new_symmetry_member_boundary_data(self):
        row = self.report["geometry"]["new_symmetry_only_member"]
        self.assertEqual(row["Q_transformed_plus_Q"],"0")
        self.assertTrue(row["tau_squared_is_deck"])
        self.assertEqual(row["boundary_discriminants"],[1129,1129])
        self.assertEqual(row["boundary_resultant"],288)
        self.assertTrue(row["simple_disjoint_boundary_roots"])
        self.assertTrue(row["boundary_restrictions_derived_from_coefficient_payload"])
        self.assertEqual(row["mechanical_bidegrees"]["p0"],[[2,12]])
        self.assertFalse(row["V90_smoothness_certificate_transfers_to_new_coefficients"])

    def test_symmetry_preserving_bad_boundary_payload_rejected(self):
        payload = copy.deepcopy(self.report["geometry"]["new_symmetry_only_member"]["coefficient_payload"])
        s,t,r0,r1,U,V = sp.symbols("s t r0 r1 U V")
        payload["p1"] = t**2*(r0**4+r1**4)+s**2*(r0**12+r1**12)
        local = {str(z):z for z in (s,t,r0,r1,U,V)}
        p = {key:sp.sympify(value,locals=local) for key,value in payload.items()}
        Q = sp.expand(s*p["L"]*(U**2-V**2)**2+s**2*sum(
            p["p"+str(i)]*U**(4-i)*V**i for i in range(5)))
        self.assertEqual(sp.expand(Q.subs({s:-s,r0:-r0,U:-U},simultaneous=True)+Q),0)
        with self.assertRaisesRegex(RuntimeError,"boundary is not simple and disjoint"):
            audit.symmetry_member_boundary(payload)

    def test_symmetry_scout_not_promoted_to_smooth_geometry(self):
        row = self.report["geometry"]["new_symmetry_only_member"]
        for key in ("compact_away_S_Jacobian_cover_computed",
                    "full_crepant_resolution_and_equivariant_lift_certified",
                    "accepted_geometry_or_diagonal_orbibundle"):
            self.assertFalse(row[key])

    def test_visible_vacuum_and_projector_boundaries(self):
        row = self.report["quantized_scout"]
        self.assertEqual(row["retained_visible_VEV_charge_gcd"],2)
        self.assertEqual(row["retained_visible_VEV_charge_magnitudes"],[8,4,6])
        self.assertFalse(row["primitive_C8_survives_complete_V90_visible_vacuum"])
        for key in ("267_SMW_Gammahat_projectors_constructed",
                    "zero_mode_counts_determined_by_bulk_multiplicities_alone",
                    "localized_continuous_inflow_constructed",
                    "global_anomaly_cancelled","complete_action_accepted"):
            self.assertFalse(row[key])

    def test_all_gates_remain_open_and_next_is_F92(self):
        self.assertEqual(self.report["terminal_decision"]["closed_gates"],[])
        self.assertTrue(all(x.startswith("OPEN:") for x in self.report["gate_ledger"].values()))
        self.assertEqual(self.report["next_required_action"]["id"],audit.NEXT_ID)
        self.assertFalse(self.report["next_required_action"]["accepted"])

    def test_validator_rejects_rehashed_numeric_and_scope_mutations(self):
        paths = [
            ("quantized_scout","c"),
            ("quantized_scout","267_SMW_Gammahat_projectors_constructed"),
            ("quantized_scout","complete_action_accepted"),
            ("finite_G8_topology","ordinary_OmegaSpin7_BG8_computed"),
            ("finite_G8_topology","torsion_source_choices_are_anomaly_free_actions"),
            ("terminal_decision","theory_complete"),
            ("terminal_decision","closed_gates"),
            ("tensor_cone","elliptic_height_realization_constructed"),
        ]
        for section,key in paths:
            candidate = copy.deepcopy(self.report)
            original = candidate[section][key]
            candidate[section][key] = True if isinstance(original,bool) else ["forged"]
            candidate["core_sha256"] = audit.canonical_sha(candidate)
            with self.assertRaises(RuntimeError):
                audit.validate_report(candidate)

    def test_primary_sources_and_source_hashes_bound(self):
        self.assertEqual(len(self.report["primary_sources"]),7)
        self.assertEqual(self.report["artifact_hashes"]["test_sha256"],audit.file_sha(audit.TEST_PATH))

    def test_artifacts_current(self):
        self.assertEqual(json.loads(audit.OUT_JSON.read_text(encoding="utf-8")),self.report)
        self.assertEqual(audit.OUT_MD.read_text(encoding="utf-8"),audit.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
