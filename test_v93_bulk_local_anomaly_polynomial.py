import copy
import unittest
import sympy as sp

import v93_bulk_local_anomaly_polynomial as audit


class TestV93BulkLocalPolynomial(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=audit.build_certificate()
        cls.calc=cls.report["calculation"]

    def polynomial(self,point,sector="total"):
        return sp.sympify(self.calc["per_stratum"][point][sector])

    def test_lineage_canonical(self):
        self.assertEqual(self.report["input_core_hashes"],{k:v[1] for k,v in audit.PINS.items()})

    def test_vector_and_adjoint_census(self):
        self.assertEqual(len(audit.vector_weights()),11)
        adj=audit.adjoint_weights()
        self.assertEqual(len(adj),55)
        self.assertEqual([sum(r["Q"]==m for r in adj) for m in range(4)],[25,5,20,5])
        self.assertEqual(sum(r["weight"]==0 for r in adj),5)

    def test_gauge_only_integrated_index(self):
        row=self.calc["zero_mode_index_crosscheck"]
        self.assertEqual(row["exact_difference"],"0")
        self.assertEqual(row["integrated_fixed_gauge_polynomial"],row["independently_projected_zero_mode_polynomial"])

    def test_C4_compact_formula(self):
        f,x,p,E=audit.f,audit.x,audit.p,audit.E
        h2=sum(e*e for e in E)
        for point,t in (("z00",sum(E)),("z11",sum(E[:2])-sum(E[2:]))):
            expected=(f*h2+4*f*f*t-f*x*t+x*(t*t-h2)/4+sp.Rational(377,3)*f**3
                      +sp.Rational(39,2)*f*f*x-sp.Rational(47,48)*f*p
                      -sp.Rational(87,16)*f*x*x-x*(p+x*x)/8)
            self.assertEqual(sp.expand(self.polynomial(point)-expected),0)

    def test_C2_cover_formula(self):
        f,x,p,E=audit.f,audit.x,audit.p,audit.E
        expected=f*(sum(e*e for e in E[:2])-sum(e*e for e in E[2:]))-5*f**3-f*p/16-3*f*x*x/16
        for point in ("z10","z01"):
            self.assertEqual(sp.expand(self.polynomial(point)-expected),0)

    def test_V92_normal_alignment_reproduced(self):
        for point in ("z00","z11"):
            poly=self.polynomial(point).subs({e:0 for e in audit.E}).subs(audit.f,0)
            self.assertEqual(sp.expand(poly+audit.x*(audit.p+audit.x**2)/8),0)

    def test_normal_off_diagonal_GS_obstruction(self):
        row=self.calc["ordinary_bulk_GS_obstruction"]
        self.assertEqual(row["bare_bulk_value"],"1/2")
        self.assertEqual(row["at_z00"]["basis_rank"],9)
        self.assertEqual(row["at_z00"]["augmented_rank"],10)
        monomial=audit.x*audit.E[0]*audit.E[1]
        self.assertTrue(all(sp.Poly(sp.sympify(z),*audit.VARIABLES).coeff_monomial(monomial)==0 for z in row["at_z00"]["basis"]))

    def test_C2_anisotropic_gauge_obstruction(self):
        poly=sp.Poly(self.polynomial("z10"),*audit.VARIABLES)
        self.assertEqual(poly.coeff_monomial(audit.f*audit.E[0]**2)-poly.coeff_monomial(audit.f*audit.E[2]**2),2)
        self.assertFalse(audit.generalized_bulk_GS_span(poly.as_expr())["in_generous_bulk_invariant_product_span"])

    def test_independent_normal_axion_has_half_integral_instanton_period(self):
        row=self.calc["ordinary_bulk_GS_obstruction"]["independent_normal_axion_period_screen"]
        self.assertEqual(row["period_shift_one_phase"],"-1")
        self.assertFalse(row["standalone_period_one_normal_axion_works"])
        self.assertFalse(row["all_extended_tangential_or_coupled_GS_completions_excluded"])
        target=self.calc["per_stratum"]["z00"]["formal_local_axion_target"]
        A=sp.sympify(target["normal_shift_four_form_A"]).subs({audit.f:0,audit.x:0,audit.p:0})
        u=sp.Symbol("u")
        self.assertEqual(sp.expand(A.subs(dict(zip(audit.E,(u,-u,0,0,0))))),-u*u/2)

    def test_formal_axion_identity_not_action(self):
        for point in audit.POINTS:
            row=self.calc["per_stratum"][point]["formal_local_axion_target"]
            self.assertEqual(sp.expand(self.polynomial(point)-audit.x*sp.sympify(row["normal_shift_four_form_A"])-audit.f*sp.sympify(row["U1_shift_four_form_B"])),0)
            self.assertFalse(row["quantum_counterterm_accepted"])
            self.assertFalse(row["periodicity_integrality_or_relative_differential_completion_constructed"])

    def test_full_visible_tensor_and_pullback(self):
        row=self.calc["conditional_visible_gauge_slice"]
        self.assertEqual(row["visible_tensor"],[-32,-24,-816,-576,-68,1408,96,384,96])
        self.assertTrue(row["component_pullback_verified"])
        self.assertFalse(row["full_localized_normal_polynomial_constructed"])

    def test_no_pure_Spin11_cubic_gauge_anomaly(self):
        for point in audit.POINTS:
            self.assertEqual(self.polynomial(point).subs({audit.x:0,audit.f:0}),0)

    def test_sparse_output_exact(self):
        for point in audit.POINTS:
            rebuilt=sum(sp.Rational(row["coefficient"])*sp.prod(z**n for z,n in zip(audit.VARIABLES,row["powers"])) for row in self.calc["per_stratum"][point]["total_sparse_coefficients"])
            self.assertEqual(sp.expand(rebuilt-self.polynomial(point)),0)

    def test_mutations_rejected(self):
        for key in self.report["boundary"]:
            changed=copy.deepcopy(self.report)
            changed["boundary"][key]=True
            with self.assertRaises(RuntimeError):
                audit.validate_certificate(changed)
        changed=copy.deepcopy(self.report)
        changed["calculation"]["ordinary_bulk_GS_obstruction"]["bare_bulk_value"]="0"
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(changed)


if __name__=="__main__":
    unittest.main()
