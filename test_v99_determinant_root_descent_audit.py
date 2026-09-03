import copy
from itertools import product
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import sympy as sp

import v99_determinant_root_descent_audit as audit


class DeterminantRootDescentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=audit.build_certificate()
        cls.inputs=audit.load_inputs()

    def test_canonical_parent_pins_roundtrip_and_fresh_validation(self):
        self.assertEqual(self.report,json.loads(json.dumps(self.report)))
        self.assertEqual(self.report["core_sha256"],audit.canonical_sha(self.report))
        for key,value in audit.PARENTS.items():
            self.assertEqual(self.report["input_core_hashes"][key],value[1])
        audit.validate_certificate(self.report)

    def test_parent_core_mutation_rejected(self):
        original=Path.read_text
        def changed(path,*args,**kwargs):
            value=original(path,*args,**kwargs)
            if path.name==audit.PARENTS["v98_master"][0]:
                data=json.loads(value)
                data["status"]="ROOT_PROMOTED"
                data["core_sha256"]=audit.canonical_sha(data)
                return json.dumps(data)
            return value
        with patch.object(Path,"read_text",changed):
            with self.assertRaises(RuntimeError): audit.load_inputs()

    def test_source_hashes_fresh_even_after_pure_cache(self):
        audit.pure_algebra_json()
        with patch.object(audit,"portable_sha",return_value="0"*64):
            with self.assertRaisesRegex(RuntimeError,"source/test"):
                audit.build_certificate()

    def test_portable_LF_CRLF_source_hashes(self):
        expected=audit.hashlib.sha256(b"alpha\nbeta\n").hexdigest()
        for raw in (b"alpha\nbeta\n",b"alpha\r\nbeta\r\n"):
            with patch.object(Path,"read_bytes",return_value=raw):
                self.assertEqual(audit.portable_sha(Path("unused")),expected)

    def test_V98_quantized_response_is_retained_not_retracted(self):
        row=self.report["bound_V98_quantized_chosen_root_response"]
        c,x,p=audit.c,audit.x,audit.p
        J=lambda z:(z+x/2)**3/6-(z+x/2)*p/24
        self.assertEqual(sp.expand(J(2*c)-2*J(c)+J(0)+c**3),2*c**3+x*c*c/2)
        self.assertEqual(sp.sympify(row["polynomial"]),2*c**3+x*c*c/2)
        self.assertFalse(row["quantization_on_its_chosen_root_category_retracted"])

    def test_root_cover_removes_KS_but_not_geometric_D_or_KT(self):
        old,new=audit.lift_parent.old_kernel(),audit.root_kernel()
        self.assertEqual(len(old),8)
        self.assertEqual(len(new),4)
        self.assertEqual(new,audit.lift_parent.span((audit.DGEOM,audit.KT)))
        self.assertIn(audit.DGEOM,new)
        self.assertIn(audit.KT,new)
        self.assertNotIn(audit.KS,new)

    def test_bare_gauge_C_and_bare_natural_spinor_differ(self):
        dot=audit.lift_parent.dot
        self.assertEqual([dot(audit.CCHAR,k) for k in (audit.DGEOM,audit.KT,audit.KS)],[0,0,1])
        self.assertEqual([dot(audit.SIGMA,k) for k in (audit.DGEOM,audit.KT,audit.KS)],[0,1,0])

    def test_complete_internal_center_parity_for_eta_operators(self):
        for n in range(6):
            for s,r,h3,h267 in product(range(2),repeat=4):
                char=(1,1,s,r,h3,h267,n%2)
                actual=not any(audit.lift_parent.character_descent(char,audit.lift_parent.old_kernel()))
                self.assertEqual(actual,s==n%2 and (r+h3+h267)%2==(1+n)%2)
        for row in self.report["inherited_center_and_operator_descent"]["operator_rows"]:
            self.assertEqual(len(row["allowed_internal_bits_Spin11_R_H3_H267"]),4)
            self.assertTrue(any(row["root_cover_kernel_exponents"]))

    def test_natural_continuous_subgroup_intersection_and_induced_background(self):
        old=audit.lift_parent.old_kernel()
        expected=audit.lift_parent.span((audit.DGEOM,audit.KS))
        self.assertEqual([k for k in old if k[3:6]==(0,0,0)],expected)
        row=self.report["chosen_root_response_ambiguity"]
        self.assertIn("extension of structure group",row["geometric_and_gauge_subcategory"])
        self.assertIn("not a pure finite C8",row["not_finite_C8_only"])
        self.assertFalse(row["full_physical_Gammahat_tangential_category_identified"])

    def test_actual_C8_determinant_and_mixed_defect_rebound(self):
        row=self.report["frozen_square_space_group_root_obstruction"]
        self.assertEqual(row["bound_C8_lift_alpha_u_v"],[0,2,2])
        self.assertEqual(row["D_character_exponents_mod8_A_U_V"],[0,4,4])
        self.assertEqual(row["bound_C8_relation_defects"]["AVAinvU"],4)
        changed=copy.deepcopy(self.inputs["selected_C8"])
        changed["selected_representative_alpha_u_v"]=[0,0,0]
        with self.assertRaises(RuntimeError):
            audit.square_space_group(changed,self.inputs["frozen_geometry"])

    def test_abelianization_C4_C2_and_square_map(self):
        row=self.report["frozen_square_space_group_root_obstruction"]
        self.assertEqual(row["smith_diagonal"],[1,2,4])
        squares={(2*a%4,0) for a,b in product(range(4),range(2))}
        self.assertEqual(squares,{(0,0),(2,0)})
        self.assertNotIn((0,1),squares)

    def test_all_eight_root_lift_choices_fail_at_least_one_mixed_relation(self):
        rows=self.report["frozen_square_space_group_root_obstruction"]["all_eight_root_lift_attempts"]
        self.assertEqual(len(rows),8)
        for row in rows:
            a,u,v=row["C_lift_exponents_mod8_A_U_V"]
            self.assertEqual([2*a%8,2*u%8,2*v%8],[0,4,4])
            defects=row["relation_defects_mod8"]
            self.assertEqual({defects["AUAinvVinv"],defects["AVAinvU"]},{0,4})
            self.assertFalse(row["is_a_character_of_the_original_space_group"])

    def test_C2_stratum_already_obstructs_ordinary_equivariant_root(self):
        roots_of_D_minus_one={q for q in range(8) if 2*q%8==4}
        C2_characters={q for q in range(8) if 2*q%8==0}
        self.assertEqual(roots_of_D_minus_one,{2,6})
        self.assertTrue(roots_of_D_minus_one.isdisjoint(C2_characters))

    def test_alpha_is_order_four_group_automorphism(self):
        vectors=list(product(range(-1,2),range(-1,2),range(2)))
        for v in vectors:
            self.assertEqual(audit.alpha(v,4),v)
            for w in vectors:
                add=lambda a,b:(a[0]+b[0],a[1]+b[1],(a[2]+b[2])%2)
                self.assertEqual(audit.alpha(add(v,w)),add(audit.alpha(v),audit.alpha(w)))

    def test_changed_extension_group_associativity_and_inverse(self):
        elements=[(0,0,0,0),(1,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1),(3,-1,2,1)]
        mul=audit.extended_mul
        for a,b,c in product(elements,repeat=3):
            self.assertEqual(mul(mul(a,b),c),mul(a,mul(b,c)))
        for a in elements:
            self.assertEqual(mul(a,audit.extended_inverse(a)),(0,0,0,0))
            self.assertEqual(mul(audit.extended_inverse(a),a),(0,0,0,0))

    def test_explicit_extended_root_character_is_a_homomorphism(self):
        elements=list(product(range(4),range(-1,2),range(-1,2),range(2)))
        for a,b in product(elements,repeat=2):
            self.assertEqual(audit.C_phase_exponent(audit.extended_mul(a,b)),
                             (audit.C_phase_exponent(a)+audit.C_phase_exponent(b))%8)

    def test_central_extension_retains_changed_relation_and_minimal_order(self):
        row=self.report["frozen_square_space_group_root_obstruction"]["explicit_changed_central_extension"]
        self.assertEqual(row["relation_values"]["AVAinvU"],[0,0,0,1])
        for key in ("A4","UVUinvVinv","AUAinvVinv"):
            self.assertEqual(row["relation_values"][key],[0,0,0,0])
        self.assertEqual(row["minimum_central_kernel_order_for_this_root_lift"],2)
        self.assertFalse(row["central_extension_splits"])
        self.assertFalse(row["extension_installed_in_frozen_theory"])

    def test_all_fixed_stratum_lift_orders_match_old_KN_KS_defects(self):
        rows=self.report["frozen_square_space_group_root_obstruction"]["explicit_changed_central_extension"]["fixed_strata"]
        self.assertEqual([r["original_stabilizer_order"] for r in rows],[4,4,2,2])
        self.assertEqual([r["new_stabilizer_order"] for r in rows],[4,4,4,4])
        self.assertEqual([r["power_in_new_extension"] for r in rows],[[0,0,0,0],[0,0,0,0],[0,0,0,1],[0,0,0,1]])
        self.assertTrue(all("kspin" in r["old_cover_power"] for r in rows[2:]))

    def test_CP2_spin_c_index_and_actual_Dolbeault_kernels(self):
        h=sp.Symbol("h")
        for n in range(3):
            index=sp.expand((n*h+h/2)**2/2-3*h*h/24).coeff(h,2)
            self.assertEqual(index,audit.cp2_line_index(n))
        row=self.report["chosen_root_response_ambiguity"]
        self.assertEqual(row["CP2_kernel_plus_dimensions_C0_C1_C2"],[0,1,3])
        self.assertEqual(row["CP2_kernel_minus_dimensions_C0_C1_C2"],[0,0,0])

    def test_nonzero_product_spectrum_pairs_exactly(self):
        q,l,ev=sp.symbols("q l ev",real=True)
        matrix=sp.Matrix([[q,l],[l,-q]])
        self.assertEqual(matrix.trace(),0)
        self.assertEqual(matrix**2,(q*q+l*l)*sp.eye(2))
        self.assertEqual(matrix.charpoly().all_coeffs(),[1,0,-l*l-q*q])

    def test_reduced_eta_includes_kernel_and_is_not_halved_mod_one(self):
        for plus,minus in product(range(4),repeat=2):
            self.assertEqual(audit.product_xi(plus,minus,0),sp.Rational(plus+minus,2))
            self.assertEqual(audit.product_xi(plus,minus,sp.Rational(1,2)),0)
        self.assertEqual(audit.product_xi(3,0,0),sp.Rational(3,2))

    def test_root_change_compensates_full_quotient_gauge_holonomy(self):
        # Cover pair(S11 central bit,U1 eighth-root exponent), KS=(1,4).
        before=(0,0)
        after=(1,4)
        equivalence=lambda a,b: a==b or ((a[0]+1)%2,(a[1]+4)%8)==b
        self.assertTrue(equivalence(before,after))
        self.assertNotEqual(before,after)
        self.assertEqual(2*before[1]%8,2*after[1]%8)
        self.assertIn("not merely its determinant",self.report["chosen_root_response_ambiguity"]["same_full_original_gauge_background"])

    def test_flat_character_binomial_has_factor_three(self):
        c,l=sp.symbols("c l")
        delta=sp.expand((c+l)**3-c**3)
        reduced=sp.Poly(delta,l).nth(1)*l
        self.assertEqual(reduced,3*c*c*l)
        self.assertEqual(reduced.subs({c:1,l:sp.Rational(1,2)}),sp.Rational(3,2))

    def test_both_spin_structures_have_exact_combined_minus_sign(self):
        rows=self.report["chosen_root_response_ambiguity"]["both_circle_spin_structure_tests"]
        self.assertEqual([r["xi_before_C0_C1_C2"] for r in rows],[["0","1/2","3/2"],["0","0","0"]])
        self.assertEqual([r["xi_after_C0_C1_C2"] for r in rows],[["0","0","3/2"],["0","1/2","0"]])
        self.assertEqual([r["eta_combination_change"] for r in rows],["1","-1"])
        for row in rows:
            self.assertEqual(row["eta_relative_phase"],"+1")
            self.assertEqual(row["cup_change"],"3/2")
            self.assertEqual(row["combined_change_mod1"],"1/2")
            self.assertEqual(row["combined_relative_phase"],"-1")

    def test_CP2_family_sign_parity_and_synchronized_two_copy_scope(self):
        row=self.report["chosen_root_response_ambiguity"]
        for sample in row["CP2_integer_family_checks"]:
            expected="-1" if sample["C_degree"]%2 else "+1"
            self.assertEqual(sample["relative_phase"],expected)
        self.assertTrue(row["two_identical_synchronized_copies_pass_this_sign_test"])
        self.assertFalse(row["two_copies_have_full_root_independence_or_relative_gluing"])
        self.assertIn("not a proof of root independence",row["ordinary_spin4_subset"])

    def test_root_and_continuous_response_obstructions_are_distinct(self):
        root=self.report["frozen_square_space_group_root_obstruction"]
        response=self.report["chosen_root_response_ambiguity"]
        self.assertFalse(root["equivariant_square_root_on_unchanged_space_group_exists"])
        self.assertTrue(root["underlying_flat_torus_roots_exist_but_are_not_C4_equivariant"])
        self.assertFalse(response["specific_V98_response_descends_after_forgetting_root"])
        self.assertFalse(response["specific_V98_response_descends_to_known_continuous_central_quotient"])
        self.assertIn("non-flat",response["not_finite_C8_only"])

    def test_no_gate_or_full_quantum_action_promoted(self):
        self.assertTrue(all(v is False for v in self.report["remaining_obligations"].values()))
        row=self.report["chosen_root_response_ambiguity"]
        self.assertFalse(row["this_is_a_full_bordism_classification"])
        self.assertFalse(row["all_modified_inflow_or_extra_root_dependent_sectors_excluded"])
        self.assertFalse(self.report["inherited_center_and_operator_descent"]["individual_operator_failure_alone_proves_combined_response_failure"])

    def test_rehashed_root_response_promotion_rejected(self):
        changed=copy.deepcopy(self.report)
        changed["chosen_root_response_ambiguity"]["specific_V98_response_descends_after_forgetting_root"]=True
        changed["core_sha256"]=audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError): audit.validate_certificate(changed)

    def test_rehashed_finite_lift_promotion_rejected(self):
        changed=copy.deepcopy(self.report)
        changed["frozen_square_space_group_root_obstruction"]["equivariant_square_root_on_unchanged_space_group_exists"]=True
        changed["core_sha256"]=audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError): audit.validate_certificate(changed)

    def test_cached_algebra_is_immutable_to_callers(self):
        changed=json.loads(audit.pure_algebra_json())
        changed["chosen_root_response_ambiguity"]["both_circle_spin_structure_tests"].clear()
        self.assertEqual(len(json.loads(audit.pure_algebra_json())["chosen_root_response_ambiguity"]["both_circle_spin_structure_tests"]),2)

    def test_invalid_arguments_rejected(self):
        for args in ((1,0,sp.Rational(1,3)),(-1,0,0),(True,0,0)):
            with self.assertRaises(ValueError): audit.product_xi(*args)
        with self.assertRaises(ValueError): audit.cp2_line_index(sp.Rational(1,2))
        with self.assertRaises(ValueError): audit.alpha((0,0,2))
        with self.assertRaises(ValueError): audit.extended_mul((4,0,0,0),(0,0,0,0))


if __name__=="__main__":
    unittest.main()
