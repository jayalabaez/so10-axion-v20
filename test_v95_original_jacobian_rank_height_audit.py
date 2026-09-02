import copy
import json
import unittest
from unittest.mock import patch

import sympy as sp

import v95_original_jacobian_rank_height_audit as audit


class OriginalJacobianRankHeightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()

    def test_canonical_roundtrip_and_lineage(self):
        r = self.report
        self.assertEqual(r["core_sha256"],audit.canonical_sha(r))
        self.assertEqual(r,json.loads(json.dumps(r)))
        self.assertEqual(r["input_core_hashes"]["v94_route"],audit.V94_CORE)
        self.assertEqual(r["input_core_hashes"]["v94_master"],audit.V94_MASTER_CORE)
        self.assertEqual(r["input_core_hashes"]["v94_geometry"],audit.V94_GEOMETRY_CORE)
        self.assertEqual(r["coefficient_payload_sha256"],audit.previous.previous.geometry.PAYLOAD_SHA)
        audit.validate_certificate(r)

    def test_independent_quartic_reconstruction_on_generic_ruling(self):
        m = audit.generic_ruling_model(self.report["coefficient_payload"])
        T,X,_ = m["symbols"]
        a = T**3+T**2*X*(X**2+1)+X*(X**10+2)
        b = T**2*(X**4+2)+X**12+1
        c = -2*T**3
        e = T**3+X*(2*X**10+3)
        I = 12*a*e+c*c
        J = 72*a*c*e-27*b*b*e-2*c**3
        A,B = -27*I,-27*J
        self.assertEqual(sp.expand(m["affine"]["A"]-A),0)
        self.assertEqual(sp.expand(m["affine"]["B"]-B),0)
        self.assertEqual(sp.expand(m["affine"]["Delta"]+16*(4*A**3+27*B**2)),0)

    def test_exact_degrees_and_squarefree_generic_discriminant(self):
        m = audit.generic_ruling_model(self.report["coefficient_payload"])
        T,X,_ = m["symbols"]
        A,B,D = [sp.Poly(m["affine"][name],T,X,domain=sp.QQ) for name in ("A","B","Delta")]
        self.assertEqual([v.degree(T) for v in (A,B,D)],[6,9,16])
        self.assertEqual(sp.gcd(D,D.diff(T)),sp.Poly(1,T,X,domain=sp.QQ))
        self.assertEqual(sp.gcd(A,D),sp.Poly(1,T,X,domain=sp.QQ))
        self.assertEqual(sp.gcd(B,D),sp.Poly(1,T,X,domain=sp.QQ))
        self.assertEqual(set(self.report["generic_ruling_K3"]["exact_QQ_T_X_gcds"].values()),{"1"})

    def test_infinity_chart_is_full_minimal_ruling_model(self):
        m = audit.generic_ruling_model(self.report["coefficient_payload"])
        T,X,u = m["symbols"]
        for name,weight,order in (("A",8,2),("B",12,3),("Delta",24,8)):
            transformed = sp.expand(u**weight*m["affine"][name].subs(T,1/u))
            self.assertTrue(transformed.is_polynomial(u,X))
            self.assertEqual(transformed,m["infinity"][name])
            self.assertEqual(audit.previous.previous.order_at(transformed,u),order)
        self.assertEqual(sp.Poly(m["infinity"]["A"],u).nth(2),-432)
        self.assertEqual(sp.Poly(m["infinity"]["B"],u).nth(3),3456)

    def test_discriminant_leading_term_reconstructs_boundary_cover(self):
        m = audit.generic_ruling_model(self.report["coefficient_payload"])
        T,X,_ = m["symbols"]
        plus = X**4+X**3+X+2
        minus = -X**4+X**3+X-2
        coefficient = sp.Poly(m["affine"]["Delta"],T).LC()
        self.assertEqual(sp.expand(coefficient-2176782336*plus*minus),0)
        self.assertEqual(sp.discriminant(plus,X),1129)
        self.assertEqual(sp.discriminant(minus,X),1129)
        self.assertEqual(sp.resultant(plus,minus,X),288)

    def test_euler_K3_and_Shioda_Tate_bound_not_rank_equality(self):
        k = self.report["generic_ruling_K3"]
        r = self.report["original_free_MW_rank_bound"]
        self.assertEqual(k["finite_geometric_fibers"]["I1_count"]+k["infinity_orders_A_B_Delta"][-1],24)
        self.assertEqual(k["Euler_number"]//12,2)
        self.assertEqual(2*k["base_genus"]-2+k["holomorphic_Euler_characteristic"],0)
        self.assertTrue(k["minimal_resolved_generic_surface_is_K3"])
        self.assertEqual(r["trivial_lattice_rank"],2+6)
        self.assertEqual(r["original_field_rank_upper_bound"],20-2-6)
        self.assertEqual(r["original_field_rank_lower_bound"],0)
        for key in ("exact_free_rank_computed","original_nonzero_section_constructed",
                    "geometric_rank_transferred_as_equality","rank_zero_or_rank_one_conclusion"):
            self.assertFalse(r[key])
        self.assertFalse(k["fixed_X_specialization_used_for_rank_bound"])

    def test_nonconstant_j_and_original_curve_not_twist(self):
        m = audit.generic_ruling_model(self.report["coefficient_payload"])
        _,_,u = m["symbols"]
        oa,od = [audit.previous.previous.order_at(m["infinity"][name],u) for name in ("A","Delta")]
        self.assertEqual(od-3*oa,2)
        self.assertTrue(self.report["generic_ruling_K3"]["j_is_nonconstant_in_T"])
        self.assertEqual(self.report["generic_ruling_K3"]["infinity_geometric_fiber"],"I2* with D6 root lattice")

    def test_D6_inverse_and_folding_independently(self):
        C = 2*sp.eye(6)
        for i,j in ((0,1),(1,2),(2,3),(3,4),(3,5)):
            C[i,j] = C[j,i] = -1
        saved = self.report["original_field_height_restrictions"]
        inverse = sp.Matrix([[sp.Rational(v) for v in row] for row in saved["D6_inverse_Cartan_matrix"]])
        self.assertEqual(C*inverse,sp.eye(6))
        self.assertEqual([inverse[i,i] for i in (0,4,5)],[1,sp.Rational(3,2),sp.Rational(3,2)])
        self.assertEqual(list(inverse.row(0)),[1,1,1,1,sp.Rational(1,2),sp.Rational(1,2)])
        self.assertTrue(saved["near_row_is_folding_invariant"])

    def test_only_fixed_simple_components_allow_original_sections(self):
        h = self.report["original_field_height_restrictions"]
        fixed = [i for i,m in enumerate(h["affine_D6_marks"])
                 if m == 1 and h["nonsplit_B5_monodromy_permutation"][i] == i]
        self.assertEqual(fixed,[0,1])
        self.assertEqual(h["height_correction_by_simple_node"],{"0":"0","1":"1","5":"3/2","6":"3/2"})
        self.assertTrue(h["every_nonzero_original_field_section_has_integral_height"])
        self.assertFalse(h["claims_geometric_Kprime_sections_all_have_integral_height"])
        with self.assertRaises(ValueError):
            audit.height_case(5,5)

    def test_height_lower_bound_and_parity(self):
        for h in (0,1,2):
            self.assertFalse(any(audit.height_case(h,n)["passes_necessary_integer_nonnegative_intersection_test"] for n in (0,1)))
        for h in range(3,35):
            passing = [n for n in (0,1) if audit.height_case(h,n)["passes_necessary_integer_nonnegative_intersection_test"]]
            self.assertEqual(passing,[h % 2])
        self.assertFalse(audit.height_case(sp.Rational(7,2),1)["passes_necessary_integer_nonnegative_intersection_test"])

    def test_target_freshly_bound_to_actual_scout(self):
        s = self.report["scout_height_binding"]
        c0,c1 = map(sp.Rational,s["c_in_V91_U_basis"])
        self.assertEqual([-c1,-c0-2*c1],[148,768])
        self.assertEqual(s["bulk_vector_displayed_charge_magnitudes"],[6,4,6])
        self.assertTrue(s["this_is_a_necessary_anomaly_target_not_an_actual_height"])

    def test_unit_charge_branch_requires_identity(self):
        r = self.report["conditional_target_height_normalizations"]["branches"][0]
        self.assertEqual(r["q_displayed_over_q_section_Sh"],1)
        self.assertEqual(r["required_section_height_class_S_F"],["148","768"])
        self.assertEqual(r["surviving_nodes"],[0])
        self.assertEqual(r["component_candidates"][0]["required_P_dot_O_divisor_S_F"],["72","378"])
        self.assertFalse(r["component_candidates"][1]["passes_both_necessary_tests"])

    def test_doubled_charge_branch_requires_near_node(self):
        r = self.report["conditional_target_height_normalizations"]["branches"][1]
        self.assertEqual(r["q_displayed_over_q_section_Sh"],2)
        self.assertEqual(r["height_scale"],4)
        self.assertEqual(r["required_section_height_class_S_F"],["37","192"])
        self.assertEqual(r["surviving_nodes"],[1])
        self.assertEqual(r["component_candidates"][1]["required_P_dot_O_divisor_S_F"],["17","90"])
        self.assertFalse(r["component_candidates"][0]["passes_both_necessary_tests"])

    def test_global_height_equations_reconstruct_without_rounding(self):
        for branch in self.report["conditional_target_height_normalizations"]["branches"]:
            b = list(map(sp.Rational,branch["required_section_height_class_S_F"]))
            for row in branch["component_candidates"]:
                D = list(map(sp.Rational,row["required_P_dot_O_divisor_S_F"]))
                self.assertEqual([4+2*D[0]-row["node"],12+2*D[1]],b)
            self.assertEqual([v*branch["height_scale"] for v in b],[148,768])

    def test_necessary_divisibility_screen_complete_bound(self):
        self.assertEqual(audit.possible_divisibilities(148),[1,2])
        self.assertEqual(audit.possible_divisibilities(37),[1])
        self.assertEqual(audit.possible_divisibilities(12),[1,2])
        self.assertEqual(audit.possible_divisibilities(2),[])
        self.assertEqual(audit.possible_divisibilities(27),[1,3])
        for bad in (0,-1,sp.Rational(7,2)):
            with self.assertRaises(ValueError):
                audit.possible_divisibilities(bad)

    def test_central_character_and_charge_parity(self):
        r = self.report["central_charge_normalization"]
        self.assertEqual(r["pairings_with_B5_simple_roots"],["1","0","0","0","0"])
        self.assertEqual(r["vector_weight_count"],11)
        self.assertEqual(r["spinor_weight_count"],32)
        self.assertEqual(r["vector_weight_pairing_values"],["-1","0","1"])
        self.assertEqual(r["spinor_weight_pairing_values"],["-1/2","1/2"])
        self.assertEqual(r["if_q_displayed_equals_two_q_Sh_parities"],{"singlet":"even","vector11":"even","spinor32":"odd"})
        self.assertFalse(r["actual_global_gauge_group_or_charge_unit_proved"])
        self.assertFalse(r["actual_spinor_matter_claimed"])

    def test_no_height_existence_or_gate_promotion(self):
        h = self.report["conditional_target_height_normalizations"]
        self.assertTrue(h["global_divisor_computation_is_conditional"])
        self.assertTrue(h["neither_branch_is_an_existence_proof"])
        self.assertFalse(h["branch_choice_or_actual_section_constructed"])
        self.assertFalse(h["rank_one_or_primitive_global_U1_generator_proved"])
        self.assertFalse(self.report["original_field_height_restrictions"]["actual_height_of_a_nonzero_section_computed"])

    def test_changed_boundary_payload_rejected(self):
        payload = copy.deepcopy(self.report["coefficient_payload"])
        payload["p0"] = "0"
        with self.assertRaises(RuntimeError):
            audit.derive_member_certificate(payload)
        payload = copy.deepcopy(self.report["coefficient_payload"])
        payload["p3"] = "t**2*r1**4"
        with self.assertRaises(RuntimeError):
            audit.derive_member_certificate(payload)

    def test_parent_hash_checks_remain_fresh_after_cache(self):
        for key in ("V94_CORE","V94_MASTER_CORE","V94_GEOMETRY_CORE"):
            with patch.object(audit,key,"0"*64):
                with self.assertRaises(RuntimeError):
                    audit.build_certificate()

    def test_parent_geometry_source_pin_checked_after_cache(self):
        with patch.object(audit.Path,"read_bytes",return_value=b"changed source"):
            with self.assertRaises(RuntimeError):
                audit.build_certificate()

    def test_parent_geometry_source_pin_is_CRLF_portable(self):
        original = audit.Path.read_bytes
        def crlf(path):
            return original(path).replace(b"\r\n",b"\n").replace(b"\n",b"\r\n")
        with patch.object(audit.Path,"read_bytes",crlf):
            self.assertEqual(audit.build_certificate(),self.report)

    def test_cached_payload_is_immutable(self):
        first = audit.derive_member_certificate(self.report["coefficient_payload"])
        first["original_free_MW_rank_bound"]["original_field_rank_upper_bound"] = 0
        second = audit.derive_member_certificate(self.report["coefficient_payload"])
        self.assertEqual(second["original_free_MW_rank_bound"]["original_field_rank_upper_bound"],12)

    def test_rehashed_rank_or_charge_normalization_mutation_rejected(self):
        for changed in ("rank","normalization","lineage"):
            r = copy.deepcopy(self.report)
            if changed == "rank":
                r["original_free_MW_rank_bound"]["exact_free_rank_computed"] = True
            elif changed == "normalization":
                r["conditional_target_height_normalizations"]["branches"][1]["height_scale"] = 2
            else:
                r["input_core_hashes"]["v94_geometry"] = "0"*64
            r["core_sha256"] = audit.canonical_sha(r)
            with self.assertRaises(RuntimeError):
                audit.validate_certificate(r)


if __name__ == "__main__":
    unittest.main()
