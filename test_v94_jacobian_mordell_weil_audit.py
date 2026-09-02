import copy
import json
import unittest
from unittest.mock import patch

import sympy as sp

import v94_jacobian_mordell_weil_audit as audit


class JacobianMordellWeilTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()

    def test_canonical_lineage_and_roundtrip(self):
        r = self.report
        self.assertEqual(r["core_sha256"],audit.canonical_sha(r))
        self.assertEqual(r,json.loads(json.dumps(r)))
        self.assertEqual(r["input_core_hashes"]["v93"],audit.V93_CORE)
        self.assertEqual(r["coefficient_payload_sha256"],audit.previous.geometry.PAYLOAD_SHA)

    def test_direct_specialized_cubic_reconstruction(self):
        m = audit.member_model(self.report["coefficient_payload"])
        sym = m["symbols"]
        T,x = sp.symbols("T x")
        chart = {sym["s"]:1,sym["r0"]:1,sym["t"]:T,sym["r1"]:0}
        cubic = sp.expand(x**3+m["A"].subs(chart)*x+m["B"].subs(chart))
        self.assertEqual(sp.expand(cubic-(x**3-432*T**6*x+3456*T**9+729*T**3*(T*T+1)**2)),0)
        self.assertEqual(cubic.subs(T,0),x**3)

    def test_normalized_complete_root_degree_bound(self):
        z,T = sp.symbols("z T")
        f = z**3-48*T**4*z+128*T**6+27*(T*T+1)**2
        r = audit.polynomial_root_obstruction(f,z,T)
        self.assertEqual(r["all_polynomial_roots_have_degree_at_most"],2)
        self.assertEqual(r["coefficient_degrees_linear_constant"],[4,6])
        self.assertEqual(r["Groebner_basis"],["1"])
        for n in range(3,10):
            self.assertGreater(3*n,max(n+4,6))

    def test_independent_groebner_from_all_coefficients(self):
        a,b,c,T = sp.symbols("a b c T")
        p = a*T*T+b*T+c
        equations = sp.Poly(sp.expand(p**3-48*T**4*p+128*T**6+27*(T*T+1)**2),T).all_coeffs()
        basis = sp.groebner(equations,a,b,c,domain=sp.QQ)
        self.assertEqual([q.as_expr() for q in basis.polys],[1])

    def test_elementary_coefficient_contradiction(self):
        c = sp.symbols("c",nonzero=True)
        t4 = 3*(-18/c**2)**2*c-48*c+27
        remainder = sp.rem(sp.together(t4+9+48*c).as_numer_denom()[0],c**3+27,c)
        self.assertEqual(remainder,0)
        self.assertEqual(sp.Rational(-3,16)**3+27,sp.Rational(110565,4096))

    def test_root_search_with_solution_not_falsely_certified(self):
        z,T = sp.symbols("z T")
        # z=T^2 is an exact root, while degrees still meet the same exhaustive bound.
        with self.assertRaises(RuntimeError):
            audit.polynomial_root_obstruction(z**3-T**4*z,z,T)
        with self.assertRaises(RuntimeError):
            audit.polynomial_root_obstruction(z**3+T**4*z-2*T**6,z,T)

    def test_no_two_torsion_over_complex_function_field(self):
        r = self.report["actual_two_torsion_exclusion"]
        self.assertFalse(r["nonzero_two_torsion_over_C_F4_exists"])
        self.assertTrue(r["monic_cubic_irreducible_over_C_F4"])
        self.assertEqual(r["normalized_root_proof"]["excludes_coefficients_over"],"C, not just Q")
        self.assertFalse(r["uses_number_field_rank_specialization_injectivity"])

    def test_d6_component_group_computed(self):
        r = audit.d6_component_group()
        self.assertEqual(sp.Matrix(r["D6_Cartan_matrix"]).det(),4)
        self.assertEqual(r["Smith_diagonal_absolute"],[1,1,1,1,2,2])
        self.assertEqual(r["exponent"],2)

    def test_full_torsion_not_free_rank(self):
        r = self.report["actual_full_torsion_theorem"]
        self.assertEqual(r["actual_orders_f_g_Delta_at_S"],[2,3,8])
        self.assertEqual(r["torsion_order"],1)
        self.assertFalse(r["free_Mordell_Weil_rank_computed"])
        self.assertIsNone(r["free_Mordell_Weil_rank"])
        self.assertFalse(r["torsion_triviality_proves_rank_zero"])

    def test_generic_quartic_point_identity_independent(self):
        a,b,c,e = sp.symbols("a b c e")
        I = 12*a*e+c*c
        J = 72*a*c*e-27*b*b*e-2*c**3
        self.assertEqual(sp.expand((-6*c)**3-27*I*(-6*c)-27*J-(27*b)**2*e),0)

    def test_quadratic_extension_and_non_descent_scope(self):
        r = self.report["quadratic_extension_point"]
        self.assertEqual(r["radicand_order_at_S"],1)
        self.assertEqual(r["extension_degree"],2)
        self.assertTrue(r["point_is_non_torsion"])
        self.assertFalse(r["point_is_K_rational"])
        self.assertTrue(r["no_nonzero_integer_multiple_descends_to_K"])
        self.assertFalse(r["new_point_proves_original_Jacobian_rank_positive"])

    def test_exact_good_reduction_counts(self):
        self.assertEqual(audit.finite_curve_count(-432,6372,5)["point_count_including_infinity"],5)
        self.assertEqual(audit.finite_curve_count(-432,6372,11)["point_count_including_infinity"],16)
        # Independent enumerator includes all pairs, not a Legendre-symbol assumption.
        for p in (5,11):
            count = 1+sum((y*y-x*x*x+432*x-6372)%p==0 for x in range(p) for y in range(p))
            self.assertEqual(count,audit.finite_curve_count(-432,6372,p)["point_count_including_infinity"])
        for p in (2,4,7,13):
            with self.assertRaises(ValueError):
                audit.finite_curve_count(-432,6372,p)

    def test_specialized_point_and_non_integral_multiple(self):
        r = self.report["non_torsion_specialization_proof"]
        self.assertEqual(r["point"],[12,54])
        self.assertEqual(r["Weierstrass_discriminant"],-12380449536)
        self.assertEqual(r["first_five_multiples"][-1]["x"],"84/25")
        self.assertEqual(audit.add_rational_points((12,54),(12,-54),-432),None)
        self.assertFalse(r["claims_specialization_is_injective_on_free_MW_group"])

    def test_twist_section_and_forced_gauge_change(self):
        r = self.report["quadratic_twist_redesign"]
        self.assertTrue(r["section_identity_verified"])
        self.assertTrue(r["section_is_non_torsion"])
        self.assertEqual(r["free_rank_lower_bound_for_twist_only"],1)
        self.assertEqual(r["raw_S_orders_f_g_Delta"],[4,6,14])
        self.assertEqual(r["minimal_S_orders_f_g_Delta"],[0,0,2])
        self.assertEqual(r["S_gauge_algebra"],"A1 = su(2)")
        for key in ("preserves_required_S_B5_algebra","accepted_as_same_Spin11_U1_completion",
                    "new_compact_Calabi_Yau_or_matter_spectrum_constructed","actual_height_pairing_computed"):
            self.assertFalse(r[key])

    def test_changed_payload_not_given_frozen_conclusion(self):
        payload = copy.deepcopy(self.report["coefficient_payload"])
        payload["p1"] = "0"
        with self.assertRaises(RuntimeError):
            audit.derive_member_certificate(payload)
        payload = copy.deepcopy(self.report["coefficient_payload"])
        payload["p3"] = "t**2*r1**4"
        with self.assertRaises(RuntimeError):
            audit.derive_member_certificate(payload)

    def test_parent_checks_fresh_when_cached(self):
        with patch.object(audit,"V93_CORE","0"*64):
            with self.assertRaises(RuntimeError):
                audit.build_certificate()

    def test_immutable_cache_report_isolation(self):
        first = audit.derive_member_certificate(self.report["coefficient_payload"])
        first["actual_full_torsion_theorem"]["torsion_order"] = 4
        second = audit.derive_member_certificate(self.report["coefficient_payload"])
        self.assertEqual(second["actual_full_torsion_theorem"]["torsion_order"],1)

    def test_rehashed_rank_promotion_rejected(self):
        r = copy.deepcopy(self.report)
        r["actual_full_torsion_theorem"]["free_Mordell_Weil_rank"] = 0
        r["core_sha256"] = audit.canonical_sha(r)
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(r)


if __name__ == "__main__":
    unittest.main()
