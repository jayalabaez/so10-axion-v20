import copy
import json
import unittest
from unittest.mock import patch

import sympy as sp

import v93_geometric_spectrum_compatibility as audit


class GeometrySpectrumCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()

    def test_lineage_and_roundtrip(self):
        r = self.report
        self.assertEqual(r["core_sha256"],audit.canonical_sha(r))
        self.assertEqual(r,json.loads(json.dumps(r)))
        self.assertEqual(r["input_core_hashes"]["v92"],audit.V92_CORE)
        self.assertEqual(r["coefficient_payload_sha256"],audit.geometry.PAYLOAD_SHA)

    def test_universal_factorization(self):
        a = audit.universal_algebra()
        z = a["symbols"][0]
        self.assertEqual(sp.expand(a["D"]-27*z**8*a["E"]*a["R"]),0)
        self.assertEqual([audit.order_at(a[n],z) for n in ("I","J","D")],[2,3,8])

    def test_invariants_against_polynomial_discriminant(self):
        u = sp.symbols("u")
        # Ordinary polynomial discriminant differs from Fisher's curve discriminant.
        for coefficients in ((1,2,3,4,5),(3,0,-2,0,7),(1,0,0,1,1)):
            I,J,D = audit.quartic_invariants(*coefficients)
            polynomial = sum(c*u**(4-i) for i,c in enumerate(coefficients))
            self.assertEqual(sp.expand(D-27*sp.discriminant(polynomial,u)),0)

    def test_tate_reconstruction(self):
        a = audit.universal_algebra()
        z,ell,p0,p1,p4 = a["symbols"]
        self.assertEqual(sp.expand(a["monodromy"]-324**2*ell**2*(p0-p1+p4)*(p0+p1+p4)),0)
        B2 = 4*z*a["A2"]
        B4 = 2*z**3*a["A4"]
        B6 = 4*z**5*a["A6"]
        self.assertEqual(sp.expand(B2**2-24*B4-1296*a["I"]),0)
        self.assertEqual(sp.expand(-B2**3+36*B2*B4-216*B6-23328*a["J"]),0)

    def test_actual_boundary_not_inherited(self):
        r = self.report["S_Jacobian_fiber"]["boundary_squareclasses"]
        self.assertEqual(r["P_plus"],"x**4 + x**3 + x + 2")
        self.assertEqual(r["P_minus"],"-x**4 + x**3 + x - 2")
        self.assertEqual(r["discriminants"],[1129,1129])
        self.assertEqual(r["resultant"],288)
        self.assertEqual(r["squareclass_rank_over_C_x"],2)

    def test_boundary_mutation_rejects_shared_or_repeated_roots(self):
        payload = copy.deepcopy(self.report["coefficient_payload"])
        payload["p1"] = "0"
        with self.assertRaises(RuntimeError):
            audit.boundary_squareclasses(payload)
        payload["p0"] = "t**2*(r0**2+r1**2)**2"
        with self.assertRaises(RuntimeError):
            audit.boundary_squareclasses(payload)

    def test_p2_scope_mutation_rejected(self):
        payload = copy.deepcopy(self.report["coefficient_payload"])
        payload["p2"] = "t**2*r1**4"
        with self.assertRaises(RuntimeError):
            audit.derive_member_certificate(payload)

    def test_global_divisor_classes(self):
        r = self.report["global_discriminant"]
        self.assertEqual(r["divisor_classes_in_S_F"],
                         {"I":[8,24],"J":[12,36],"D":[24,72],"E":[3,12],"R":[13,60]})
        self.assertEqual(r["E_affine"],"T**3 + 2*X**11 + 3*X")

    def test_reduced_affine_discriminant_and_generic_I1(self):
        r = self.report["global_discriminant"]
        self.assertEqual(r["Q_factor_multiplicities"],[1,1])
        self.assertTrue(all(v=="1" for v in r["normalized_polynomial_gcds"].values()))
        self.assertEqual(r["all_off_S_generic_orders_f_g_D"],[0,0,1])
        self.assertFalse(r["additional_off_S_nonabelian_discriminant_divisor"])
        self.assertFalse(r["Q_irreducibility_claims_geometric_irreducibility"])

    def test_compact_codim_one_boundaries(self):
        r = self.report["global_discriminant"]
        self.assertTrue(r["codimension_one_cover_complete"])
        self.assertFalse(r["r1_zero_is_discriminant_divisor"])
        self.assertNotEqual(r["r1_zero_restriction_r0_one"],"0")
        self.assertEqual(self.report["S_Jacobian_fiber"]["actual_orders_I_J_D"],[2,3,8])

    def test_jacobian_algebra_not_global_group(self):
        r = self.report["S_Jacobian_fiber"]
        self.assertEqual(r["Tate_gauge_algebra"],"B5 = so(11)")
        self.assertFalse(r["global_gauge_group_proved"])

    def test_torsor_period_index_without_section(self):
        r = self.report["torsor_section_obstruction"]
        self.assertFalse(r["rational_section_exists"])
        self.assertEqual((r["period"],r["index"],r["bisection_degree"]),(2,2,2))
        self.assertEqual(r["bisection_rhs_order_at_S"],1)
        self.assertTrue(r["Jacobian_has_zero_section"])
        self.assertFalse(r["no_torsor_section_implies_Jacobian_MW_rank_zero"])

    def test_spectrum_target_not_promoted(self):
        r = self.report["spectrum_compatibility"]
        self.assertEqual(r["conditional_target_hodge_tuple"],{"h11":9,"h21":143,"Euler":-268})
        self.assertEqual(r["conditional_target_height_class_in_S_F"],[148,768])
        self.assertIsNone(r["Jacobian_Mordell_Weil_rank"])
        for key in ("Jacobian_Mordell_Weil_rank_computed","non_torsion_Jacobian_section_constructed",
                    "actual_height_pairing_constructed","conditional_targets_are_actual_member_invariants",
                    "actual_member_realizes_V91_scout","same_action_physical_completion"):
            self.assertFalse(r[key])

    def test_riemann_hurwitz_and_connectedness(self):
        self.assertEqual(audit.double_cover_genus(0,8),3)
        self.assertEqual(audit.double_cover_genus(1,0),1)
        self.assertEqual(audit.double_cover_genus(2,4),5)
        for values in ((0,0),(0,3),(-1,8),(0,-2)):
            with self.assertRaises(ValueError):
                audit.double_cover_genus(*values)

    def test_exact_orthogonal_branching_action(self):
        self.assertEqual(audit.orthogonal_adjoint_branching(11),(66,55,11,True,True))
        self.assertEqual(audit.orthogonal_adjoint_branching(5),(15,10,5,True,True))

    def test_conditional_nonlocal_three_vector_hypers(self):
        r = self.report["conditional_Jacobian_nonlocal_matter"]
        self.assertEqual((r["base_genus"],r["simple_branch_point_count"],r["cover_genus"]),(0,8,3))
        self.assertEqual(r["Riemann_Hurwitz"],
                         {"lhs_2g_cover_minus_2":4,"rhs_2_times_2g_base_minus_2_plus_branch":4})
        self.assertEqual(r["conditional_nonlocal_vector11_full_hypermultiplets"],3)
        self.assertEqual(r["intersection_crosscheck"]["value"],3)
        self.assertTrue(r["matches_nonabelian_multiplicity_only"])
        for key in ("additional_codimension_two_matter_excluded","U1_charges_determined",
                    "actual_torsor_physical_contraction_verified","Jacobian_MW_rank_or_height_determined",
                    "full_V91_spectrum_realized"):
            self.assertFalse(r[key])

    def test_nonlocal_count_rejects_repeated_branch_mutation(self):
        boundary = copy.deepcopy(self.report["S_Jacobian_fiber"]["boundary_squareclasses"])
        boundary["P_minus"] = boundary["P_plus"]
        with self.assertRaises(RuntimeError):
            audit.conditional_nonlocal_matter(boundary,3)
        with self.assertRaises(RuntimeError):
            audit.conditional_nonlocal_matter(self.report["S_Jacobian_fiber"]["boundary_squareclasses"],4)

    def test_report_mutation_rejected_after_rehash(self):
        report = copy.deepcopy(self.report)
        report["spectrum_compatibility"]["Jacobian_Mordell_Weil_rank"] = 1
        report["core_sha256"] = audit.canonical_sha(report)
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(report)

    def test_cache_does_not_share_mutable_reports(self):
        first = audit.derive_member_certificate(self.report["coefficient_payload"])
        first["global_discriminant"]["S_multiplicity"] = 99
        second = audit.derive_member_certificate(self.report["coefficient_payload"])
        self.assertEqual(second["global_discriminant"]["S_multiplicity"],8)

    def test_parent_checks_stay_fresh_when_cache_warm(self):
        with patch.object(audit,"V92_CORE","0"*64):
            with self.assertRaises(RuntimeError):
                audit.build_certificate()


if __name__ == "__main__":
    unittest.main()
