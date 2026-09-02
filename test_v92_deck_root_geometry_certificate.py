import copy
import unittest
import sympy as sp

import v92_deck_root_geometry_certificate as audit


class TestV92DeckRootGeometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()

    def test_saved_parent_and_payload_are_bound(self):
        self.assertEqual(self.report["parent_V91_core_sha256"],audit.V91_CORE)
        self.assertEqual(self.report["coefficient_payload_sha256"],audit.PAYLOAD_SHA)
        self.assertEqual(audit.canonical_sha(audit.load_payload()),audit.PAYLOAD_SHA)

    def test_boundary_is_derived_and_good_at_prime_including_infinity(self):
        row = self.report["bundle_and_boundary"]
        self.assertEqual(row["boundary_restrictions_derived_from_payload"],
                         ["x**4 + x**3 + x + 2", "-x**4 + x**3 + x - 2"])
        self.assertEqual(row["boundary_degrees"],[4,4])
        self.assertEqual(row["leading_coefficients"],[1,-1])
        self.assertEqual(row["discriminants_over_Z"],[1129,1129])
        self.assertEqual(row["resultant_over_Z"],288)
        self.assertEqual(row["discriminants_mod_prime"],[18,18])
        self.assertEqual(row["resultant_mod_prime"],86)
        self.assertTrue(row["no_boundary_root_at_r1_zero"])

    def test_symmetry_compatible_singular_boundary_is_rejected(self):
        payload = audit.load_payload()
        payload["p1"] = "t**2*(r0**4+r1**4)+s**2*(r0**12+r1**12)"
        with self.assertRaisesRegex(RuntimeError,"simple/disjoint"):
            audit.bundle_and_boundary_certificate(payload)

    def test_bad_primes_are_rejected(self):
        for prime in (2,3,1129,100):
            with self.subTest(prime=prime), self.assertRaises(RuntimeError):
                audit.bundle_and_boundary_certificate(audit.load_payload(),prime)

    def test_all_four_exhaustive_away_strata_have_unit_bases(self):
        row = self.report["away_S_good_reduction_cover"]
        self.assertEqual([x["stratum"] for x in row["rows"]],[
            "r1_nonzero_V_nonzero","r1_zero_V_nonzero",
            "r1_nonzero_V_zero","r1_zero_V_zero"])
        self.assertEqual([x["closed_stratum_selectors"] for x in row["rows"]],
                         [[],["X"],["Z"],["X","Z"]])
        self.assertTrue(row["all_four_stratum_ideals_are_unit"])
        self.assertTrue(row["all_t_values_including_t_zero_retained"])
        self.assertTrue(all(x["all_three_ambient_partials_retained"] for x in row["rows"]))
        self.assertTrue(all(x["reduced_Groebner_basis"] == ["1"] for x in row["rows"]))
        self.assertEqual(row["aggregate_rows_sha256"],audit.canonical_sha(row["rows"]))

    def test_selectors_do_not_remove_normal_derivatives(self):
        x,y = sp.symbols("x y")
        # The restriction x=0 of Q=x+y^2 is a singular double point, but the
        # total hypersurface w^2-Q is smooth because its x derivative is -1.
        self.assertEqual(audit.jacobian_basis(x+y*y,(x,y),(x,)),["1"])
        # The helper must also detect a genuinely singular hypersurface.
        self.assertNotEqual(audit.jacobian_basis(x*x+y*y,(x,y)),["1"])

    def test_cover_cache_cannot_be_mutated_by_callers(self):
        before = audit.compute_modular_cover()
        before["rows"][0]["reduced_Groebner_basis"] = ["forged"]
        after = audit.compute_modular_cover()
        self.assertEqual(after["rows"][0]["reduced_Groebner_basis"],["1"])

    def test_near_S_branch_and_nonbranch_loci_are_covered(self):
        row = self.report["near_S_resolution"]
        by_name = {r["chart"]:r for r in row["branch_rows"]}
        self.assertEqual(by_name["B1_r"]["Jacobian_basis"],["w","a","r"])
        for name in ("B1_s","B1_w","B2_a","B2_w"):
            self.assertEqual(by_name[name]["Jacobian_basis"],["1"])
        self.assertTrue(row["nonbranch_q_not_treated_as_independent_coordinate"])
        self.assertEqual(row["nonbranch_first_s_witness_basis"],["1"])
        self.assertEqual(row["residual_w_exceptional_witness_basis"],["1"])
        self.assertTrue(row["both_C_plus_and_C_minus_covered"])

    def test_projective_relative_model_not_affine_modular_inference(self):
        model = self.report["integral_projective_model_and_lift"]
        self.assertTrue(model["ambient"]["projective_over_R"])
        self.assertTrue(model["blowups"]["Rees_algebras_commute_with_special_fibre"])
        self.assertEqual(model["blowups"]["relative_codimensions"],[3,3,2])
        self.assertEqual(model["blowups"]["multiplicities"],[2,2,1])
        self.assertEqual(model["blowups"]["discrepancies"],[0,0,0])
        self.assertTrue(model["strict_transform"]["proper_flat_finitely_presented_integral_model"])
        proof = self.report["proper_specialization"]
        self.assertTrue(proof["resolved_compact_member_geometrically_smooth_over_Q"])
        self.assertFalse(proof["literal_QQ_affine_Jacobian_unit_bases_computed"])
        self.assertFalse(proof["one_modular_affine_screen_promoted_without_proper_model"])
        self.assertFalse(proof["V90_old_member_smoothness_reused"])

    def test_symbolic_blowdown_and_order_four_lift(self):
        model = self.report["integral_projective_model_and_lift"]
        self.assertEqual(model["strict_transform"]["pullback_identity_residual"],"0")
        lift = model["order_four_lift"]
        self.assertEqual(lift["ambient_F_transformed_plus_F"],"0")
        self.assertEqual(lift["ambient_tau_squared"]["W"],"-W")
        self.assertEqual(lift["blowdown_commutation_residuals"],["0"]*4)
        self.assertEqual(lift["weak_transform_transformed_plus_itself"],"0")
        self.assertTrue(lift["first_centers_exchanged"])
        self.assertTrue(lift["residual_center_invariant"])
        self.assertTrue(lift["global_regular_lift_exists"])
        self.assertTrue(lift["lift_squared_is_deck"])
        self.assertEqual(lift["i_mod_101_witness"]**2 % 101,100)
        self.assertEqual(lift["holomorphic_three_form_character"],"I")
        self.assertEqual(lift["squared_three_form_character"],"-1")
        self.assertFalse(lift["preserves_holomorphic_three_form"])
        self.assertFalse(lift["standalone_volume_preserving_CY_quotient"])

    def test_incomplete_cover_or_proper_model_cannot_be_promoted(self):
        for section,path in (
            ("integral_projective_model_and_lift",("strict_transform","proper_flat_finitely_presented_integral_model")),
            ("integral_projective_model_and_lift",("blowups","Rees_algebras_commute_with_special_fibre")),
            ("away_S_good_reduction_cover",("all_four_stratum_ideals_are_unit",)),
            ("near_S_resolution",("complete_near_S_special_fibre_smoothness",)),
            ("bundle_and_boundary",("eight_simple_disjoint_geometric_branch_points_over_Fp",)),
        ):
            candidate = copy.deepcopy(self.report)
            target = candidate[section]
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = False
            with self.subTest(section=section,path=path), self.assertRaises(RuntimeError):
                audit.specialize_smoothness(
                    candidate["integral_projective_model_and_lift"],
                    candidate["away_S_good_reduction_cover"],
                    candidate["near_S_resolution"],candidate["bundle_and_boundary"])

    def test_geometry_does_not_close_physics_or_hodge_obligations(self):
        self.assertTrue(all(value is False for value in self.report["limitations"].values()))
        self.assertEqual(self.report["core_sha256"],audit.canonical_sha(self.report))

    def test_omitted_stratum_or_transverse_partial_is_rejected(self):
        mutations = (
            lambda row: row["rows"].pop(),
            lambda row: row["rows"][1].__setitem__("all_three_ambient_partials_retained",False),
            lambda row: row["rows"][2].__setitem__("closed_stratum_selectors",["X"]),
        )
        for mutate in mutations:
            away = copy.deepcopy(self.report["away_S_good_reduction_cover"])
            mutate(away)
            with self.assertRaisesRegex(RuntimeError,"stratum"):
                audit.specialize_smoothness(
                    self.report["integral_projective_model_and_lift"],away,
                    self.report["near_S_resolution"],self.report["bundle_and_boundary"])

    def test_validator_rejects_rehashed_geometry_and_scope_changes(self):
        for key in self.report["limitations"]:
            candidate = copy.deepcopy(self.report)
            candidate["limitations"][key] = True
            candidate["core_sha256"] = audit.canonical_sha(candidate)
            with self.subTest(key=key), self.assertRaises(RuntimeError):
                audit.validate_certificate(candidate)
        candidate = copy.deepcopy(self.report)
        candidate["away_S_good_reduction_cover"]["rows"][0]["ideal_generators"][0] = "1"
        candidate["core_sha256"] = audit.canonical_sha(candidate)
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(candidate)


if __name__ == "__main__":
    unittest.main()
