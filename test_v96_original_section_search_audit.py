import copy
import json
import unittest
from unittest.mock import patch

import sympy as sp

import v96_original_section_search_audit as audit


class OriginalSectionSearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()
        cls.model = audit.previous.generic_ruling_model(cls.report["coefficient_payload"])

    def test_canonical_lineage_roundtrip(self):
        r = self.report
        self.assertEqual(r["core_sha256"],audit.canonical_sha(r))
        self.assertEqual(r,json.loads(json.dumps(r)))
        self.assertEqual(r["input_core_hashes"],{"v95_route":audit.V95_ROUTE_CORE,
            "v95_master":audit.V95_MASTER_CORE,"v95_geometry":audit.V95_GEOMETRY_CORE})
        audit.validate_certificate(r)

    def test_independent_j_polynomial_division(self):
        T,X,_ = self.model["symbols"]
        A,D = (self.model["affine"][name] for name in ("A","Delta"))
        domain = sp.QQ.frac_field(X)
        numerator = sp.Poly(-1728*(4*A)**3,T,domain=domain)
        denominator = sp.Poly(D,T,domain=domain)
        quotient,remainder = numerator.div(denominator)
        saved = self.report["actual_K3_moduli_variation"]["j_polynomial_part_at_T_infinity"]
        for degree in (2,1,0):
            self.assertEqual(sp.cancel(quotient.nth(degree)-sp.sympify(saved["j"+str(degree)])),0)
        self.assertLess(remainder.degree(),denominator.degree())
        self.assertEqual([numerator.degree(),denominator.degree()],[18,16])

    def test_laurent_helper_handles_small_denominator_and_rejects_wrong_pole(self):
        t = sp.symbols("t")
        r = audit.quadratic_pole_laurent(t**3,t+1,t)
        self.assertEqual([r[k] for k in ("j2","j1","j0")],[1,-1,1])
        self.assertEqual(r["invariant"],sp.Rational(3,4))
        with self.assertRaises(ValueError):
            audit.quadratic_pole_laurent(t**2,t+1,t)

    def test_exact_centered_invariant_and_derivative(self):
        r = self.report["actual_K3_moduli_variation"]
        X = sp.Symbol("X")
        j2,j1,j0 = (sp.sympify(r["j_polynomial_part_at_T_infinity"][k]) for k in ("j2","j1","j0"))
        invariant = sp.sympify(r["centered_affine_invariant"])
        self.assertEqual(sp.cancel(invariant-j0+j1*j1/(4*j2)),0)
        self.assertEqual(invariant.subs(X,1),-sp.Rational(303952,125))
        self.assertEqual(sp.diff(invariant,X).subs(X,1),-sp.Rational(5869312,625))
        self.assertEqual(invariant.subs(X,2),sp.Rational(28999709,10976))

    def test_affine_coordinate_invariance_is_symbolic(self):
        a,b,c,k,l = sp.symbols("a b c k l",nonzero=True)
        transformed = (a*k*k,k*(2*a*l+b),a*l*l+b*l+c)
        self.assertEqual(sp.cancel(transformed[2]-transformed[1]**2/(4*transformed[0])-c+b*b/(4*a)),0)
        self.assertEqual(audit.affine_invariance_identity()["exact_invariance_residual"],"0")

    def test_actual_j_affine_change_preserves_invariant(self):
        T,X,_ = self.model["symbols"]
        # Fixed good X=1, then a nontrivial affine reparametrization of T.
        A,D = [self.model["affine"][name].subs(X,1) for name in ("A","Delta")]
        before = audit.quadratic_pole_laurent(-1728*(4*A)**3,D,T)
        after = audit.quadratic_pole_laurent((-1728*(4*A)**3).subs(T,3*T-7),D.subs(T,3*T-7),T)
        self.assertEqual(before["invariant"],after["invariant"])

    def test_X_one_inside_actual_good_family(self):
        T,X,_ = self.model["symbols"]
        A,B,D = [sp.Poly(self.model["affine"][name].subs(X,1),T,domain=sp.QQ) for name in ("A","B","Delta")]
        self.assertEqual([q.degree() for q in (A,B,D)],[6,9,16])
        self.assertEqual(D.LC(),-10883911680)
        self.assertEqual(sp.gcd(D,D.diff()).degree(),0)
        self.assertEqual(sp.gcd(A,D).degree(),0)
        self.assertEqual(sp.gcd(B,D).degree(),0)
        self.assertFalse(self.report["actual_K3_moduli_variation"]["good_parameter_witness"]["rank_of_this_fixed_slice_computed_or_used_as_bound"])

    def test_generic_ruling_still_has_unique_double_j_pole(self):
        inherited = audit.previous.derive_member_certificate(self.report["coefficient_payload"])
        k3 = inherited["generic_ruling_K3"]
        self.assertEqual(k3["finite_geometric_fibers"],{"I1_count":16,"other_singular_fibers":0})
        self.assertEqual(k3["infinity_orders_A_B_Delta"],[2,3,8])
        self.assertEqual(k3["exact_QQ_T_X_gcds"]["A_and_Delta"],"1")
        self.assertEqual(8-3*2,2)

    def test_nonconstant_moduli_strengthens_only_upper_bound(self):
        r = self.report["stronger_original_MW_rank_bound"]
        self.assertEqual(r["dimension_of_NL20"],20-r["excluded_generic_Picard_rank"])
        self.assertGreater(r["actual_moduli_image_dimension"],r["dimension_of_NL20"])
        self.assertEqual(r["generic_Picard_rank_upper_bound"],19)
        self.assertEqual(r["original_rank_upper_bound"],19-r["trivial_lattice_rank"])
        self.assertLess(r["original_rank_upper_bound"],r["previous_original_rank_upper_bound"])
        self.assertEqual(r["original_rank_lower_bound"],0)
        for key in ("fixed_specialization_rank_injectivity_assumed","generic_Picard_rank_equals19_claimed",
                    "original_rank_zero_or_one_proved","nonzero_original_section_constructed",
                    "parameter_count_alone_used_to_assert_rank_zero"):
            self.assertFalse(r[key])

    def test_degree_two_obstruction_has_arbitrary_C_X_coefficients(self):
        T,X,_ = self.model["symbols"]
        c0,c1,c2 = sp.symbols("c0 c1 c2")
        x = c0+c1*T+c2*T*T
        A,B = (self.model["affine"][name] for name in ("A","B"))
        rhs = sp.Poly(sp.expand(x**3+A*x+B),T)
        self.assertEqual(rhs.degree(),9)
        self.assertEqual(rhs.LC(),3456)
        r = self.report["polynomial_section_search_frontier"]["degree_at_most_two"]
        self.assertFalse(r["nonzero_section_with_this_ansatz_exists"])
        self.assertTrue(r["also_excluded_after_algebraic_constant_extension"])

    def test_degree_three_leading_roots_are_exhaustive(self):
        T,X,_ = self.model["symbols"]
        l,c2,c1,c0 = sp.symbols("l c2 c1 c0")
        x = l*T**3+c2*T*T+c1*T+c0
        A,B = (self.model["affine"][name] for name in ("A","B"))
        rhs = sp.Poly(sp.expand(x**3+A*x+B),T)
        self.assertEqual(sp.factor(rhs.nth(9)),(l-12)**2*(l+24))
        self.assertEqual(set(sp.solve(rhs.nth(9),l)),{12,-24})

    def test_leading_twelve_branch_nonsquare_discriminant(self):
        T,X,_ = self.model["symbols"]
        c2,c1,c0 = sp.symbols("c2 c1 c0")
        x = 12*T**3+c2*T*T+c1*T+c0
        A,B = (self.model["affine"][name] for name in ("A","B"))
        rhs = sp.Poly(sp.expand(x**3+A*x+B),T)
        self.assertEqual(rhs.degree(),7)
        equation = rhs.nth(7)
        plus = X**4+X**3+X+2
        minus = -X**4+X**3+X-2
        self.assertEqual(sp.expand(sp.discriminant(equation,c2)-324**2*plus*minus),0)
        self.assertEqual(sp.discriminant(plus,X),1129)
        self.assertEqual(sp.discriminant(minus,X),1129)
        self.assertEqual(sp.resultant(plus,minus,X),288)
        self.assertEqual(sp.degree(sp.gcd(plus*minus,sp.diff(plus*minus,X)),X),0)

    def test_far_branch_exclusion_does_not_claim_algebraic_extension_exclusion(self):
        r = self.report["polynomial_section_search_frontier"]["leading_twelve_branch"]
        self.assertTrue(r["squareclass_is_nontrivial_in_C_X"])
        self.assertFalse(r["original_field_cubic_section_on_this_branch_exists"])
        self.assertFalse(r["exclusion_claimed_after_adjoining_the_monodromy_square_root"])

    def test_remaining_cubic_system_reconstructs_full_curve_identity(self):
        p = audit.cubic_section_system(self.report["coefficient_payload"])
        T = p["T"]
        A,B = (self.model["affine"][name] for name in ("A","B"))
        reconstructed = sum(q*T**degree for q,degree in zip(p["equations"],range(8,-1,-1)))
        expected = p["y_section"]**2-p["x_section"]**3-A*p["x_section"]-B
        self.assertEqual(sp.expand(reconstructed-expected),0)
        self.assertEqual(len(p["unknowns"]),8)
        self.assertEqual(len(p["equations"]),9)
        self.assertEqual(self.report["polynomial_section_search_frontier"]["remaining_leading_minus_twenty_four_system"]["equation_list_sha256"],
                         audit.canonical_sha([str(q) for q in p["equations"]]))

    def test_linear_elimination_preserves_every_remaining_equation(self):
        p = audit.cubic_section_system(self.report["coefficient_payload"])
        a2 = p["unknowns"][0]
        self.assertEqual(sp.expand(p["equations"][0].subs(a2,p["solved_a2"])),0)
        self.assertEqual(len(p["reduced_equations"]),8)
        for raw,reduced in zip(p["equations"][1:],p["reduced_equations"]):
            self.assertEqual(sp.expand(raw.subs(a2,p["solved_a2"])-reduced),0)
            self.assertNotIn(a2,reduced.free_symbols)

    def test_no_false_full_section_or_height_exclusion(self):
        p = self.report["polynomial_section_search_frontier"]
        self.assertTrue(all(value is False for value in p["scope"].values()))
        near = p["remaining_leading_minus_twenty_four_system"]
        self.assertFalse(near["existence_or_nonexistence_solved"])
        self.assertTrue(near["is_complete_for_original_field_degree_three_polynomial_x_ansatz"])
        self.assertTrue(near["solution_over_an_extension_would_require_Galois_descent"])

    def test_physical_charge_normalization_preserved(self):
        r = self.report["charge_normalization_and_descent_preserved"]
        self.assertEqual([4*x for x in r["doubled_charge_section_height_S_F"]],r["displayed_scout_height_S_F"])
        self.assertEqual(r["doubled_charge_required_P_dot_O_divisor_S_F"],[17,90])
        self.assertEqual(r["doubled_charge_required_component"],1)
        self.assertFalse(r["actual_charge_unit_or_target_section_proved"])
        self.assertFalse(r["V94_anti_invariant_section_non_descent_retracted"])

    def test_changed_payload_not_given_frozen_result(self):
        p = copy.deepcopy(self.report["coefficient_payload"])
        p["p0"] = "0"
        with self.assertRaises(RuntimeError):
            audit.derive_member_certificate(p)
        p = copy.deepcopy(self.report["coefficient_payload"])
        p["p3"] = "t**2*r1**4"
        with self.assertRaises(RuntimeError):
            audit.derive_member_certificate(p)

    def test_lineage_and_source_checks_fresh_after_cache(self):
        for key in ("V95_ROUTE_CORE","V95_MASTER_CORE","V95_GEOMETRY_CORE"):
            with patch.object(audit,key,"0"*64):
                with self.assertRaises(RuntimeError):
                    audit.build_certificate()
        with patch.object(audit,"portable_sha",return_value="0"*64):
            with self.assertRaises(RuntimeError):
                audit.build_certificate()

    def test_source_pin_portable_LF_CRLF(self):
        for raw in (b"a\nb\n",b"a\r\nb\r\n"):
            with patch.object(audit.Path,"read_bytes",return_value=raw):
                self.assertEqual(audit.portable_sha(audit.Path("unused")),audit.hashlib.sha256(b"a\nb\n").hexdigest())

    def test_immutable_pure_cache(self):
        first = audit.derive_member_certificate(self.report["coefficient_payload"])
        first["stronger_original_MW_rank_bound"]["original_rank_upper_bound"] = 0
        second = audit.derive_member_certificate(self.report["coefficient_payload"])
        self.assertEqual(second["stronger_original_MW_rank_bound"]["original_rank_upper_bound"],11)

    def test_rehashed_rank_ansatz_or_normalization_promotions_rejected(self):
        for key in ("rank","ansatz","normalization"):
            r = copy.deepcopy(self.report)
            if key == "rank":
                r["stronger_original_MW_rank_bound"]["original_rank_zero_or_one_proved"] = True
            elif key == "ansatz":
                r["polynomial_section_search_frontier"]["scope"]["all_rational_sections_excluded"] = True
            else:
                r["charge_normalization_and_descent_preserved"]["doubled_charge_section_height_S_F"] = [148,768]
            r["core_sha256"] = audit.canonical_sha(r)
            with self.assertRaises(RuntimeError):
                audit.validate_certificate(r)


if __name__ == "__main__":
    unittest.main()
