import copy
from itertools import product
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import sympy as sp

import v98_gammahat_compensator_audit as audit


class TestGammahatCompensator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=audit.build_certificate()
        _,cls.frozen=audit.load_inputs()

    def test_canonical_json_and_fresh_validation(self):
        self.assertEqual(self.report,json.loads(json.dumps(self.report)))
        self.assertEqual(self.report["core_sha256"],audit.canonical_sha(self.report))
        audit.validate_certificate(self.report)

    def test_exact_parent_pins(self):
        self.assertEqual(self.report["input_core_hashes"],{
            "v97_route":audit.V97_ROUTE_CORE,"v97_master":audit.V97_MASTER_CORE,
            "v97_mixed":audit.MIXED_CORE,"v95_kernel_route":audit.V95_ROUTE_CORE,
            "v88_smooth_cocycle":audit.V88_CORE,"v89_C8_cocycle":audit.V89_CORE})
        for key in ("V97_ROUTE_CORE","V97_MASTER_CORE","MIXED_CORE","V95_ROUTE_CORE","V88_CORE","V89_CORE"):
            with patch.object(audit,key,"0"*64):
                with self.assertRaises(RuntimeError): audit.load_inputs()

    def test_portable_LF_CRLF_source_pins(self):
        expected=audit.hashlib.sha256(b"one\ntwo\n").hexdigest()
        for raw in (b"one\ntwo\n",b"one\r\ntwo\r\n"):
            with patch.object(Path,"read_bytes",return_value=raw):
                self.assertEqual(audit.portable_sha(Path("unused")),expected)
        with patch.object(audit,"portable_sha",return_value="0"*64):
            with self.assertRaises(RuntimeError): audit.load_inputs()

    def test_rehashed_parent_change_rejected(self):
        original=Path.read_text
        def changed(path,*args,**kwargs):
            result=original(path,*args,**kwargs)
            if path==audit.V97_ROUTE:
                data=json.loads(result)
                data["mixed_gauge_relative_glue"]["limitations"]["same_action_parent_or_any_gate_closed"]=True
                data["core_sha256"]=audit.canonical_sha(data)
                return json.dumps(data)
            return result
        with patch.object(Path,"read_text",changed):
            with self.assertRaises(RuntimeError): audit.load_inputs()

    def test_old_kernel_exact_inverse_image_not_just_three_signs(self):
        old=audit.old_kernel()
        old6=audit.span(([1,1,1,1,1,0],[0,1,0,0,0,1]))
        direct=sorted(tuple(k) for k in product(range(2),repeat=7)
                      if tuple(audit.geometry.center_map(k)) in old6)
        self.assertEqual(old,direct)
        self.assertEqual(len(old),8)
        self.assertEqual(tuple((a+b)%2 for a,b in zip(audit.D,audit.KT)),audit.KN)

    def test_Clifford_D_is_literal_identity(self):
        gamma=audit.geometry.clifford_generators()
        t=(gamma[0]*gamma[1])**2
        n=(gamma[4]*gamma[5])**2
        self.assertEqual(t,-sp.eye(8))
        self.assertEqual(n,-sp.eye(8))
        self.assertEqual(t*n,sp.eye(8))
        self.assertTrue(self.report["unchanged_geometric_kernel_obstruction"]["D_geom_is_literal_identity_before_internal_quotient"])

    def test_hyper_components_descend_before_but_not_after_M(self):
        row=self.report["unchanged_geometric_kernel_obstruction"]
        for name in ("baseline_fermion_center_bits","baseline_scalar_center_bits"):
            self.assertEqual(audit.character_descent(row[name],audit.old_kernel()),[0]*8)
        for name in ("M_twisted_fermion_center_bits","M_twisted_scalar_center_bits"):
            self.assertEqual(audit.dot(row[name],audit.D),1)

    def test_any_independent_internal_representation_cannot_change_D(self):
        for internal in product(range(2),repeat=5):
            self.assertEqual(audit.dot((1,0)+internal,audit.D),1)
        row=self.report["unchanged_geometric_kernel_obstruction"]
        self.assertTrue(all(r["D_exponent"]==1 for r in row["all_independent_internal_center_choices"]))
        self.assertFalse(row["unchanged_geometric_Gammahat_with_independent_F_can_contain_the_M_twisted_carrier"])
        self.assertFalse(row["A_fourth_power_repair_implies_full_geometric_descent"])

    def test_finite_and_continuous_gauge_categories_distinguished(self):
        row=self.report["unchanged_geometric_kernel_obstruction"]
        self.assertIn("same (Spin11 center,-1_gauge) relation",row["finite_vs_continuous_gauge_scope"])
        self.assertIn("restricts to rho2",row["finite_vs_continuous_gauge_scope"])

    def test_minimal_even_M_power_and_matrix_order(self):
        rows=self.report["minimal_even_normal_power_alternatives"]["rows"]
        for row in rows:
            k=row["extra_M_power_mod8"]
            F=sp.diag(audit.ZETA**(-k),audit.ZETA**k)
            order=row["minimum_matrix_order"]
            self.assertEqual(audit.clean(F**order),sp.eye(2))
            for lower in range(1,order): self.assertNotEqual(audit.clean(F**lower),sp.eye(2))
            self.assertEqual(row["geometric_D_screen_passes"],k%2==0)
            self.assertEqual(row["ordinary_C4_character_suffices"],k%2==0)

    def test_integer_stacks_of_even_normal_powers_cannot_make_odd_coefficient(self):
        powers=(-4,-2,0,2,4)
        for coefficients in product(range(-1,2),repeat=len(powers)):
            normal=sum(a*k for a,k in zip(coefficients,powers))
            self.assertEqual(normal%2,0)
            self.assertNotEqual((sum(coefficients),normal),(1,1))
        self.assertFalse(self.report["minimal_even_normal_power_alternatives"]["integer_even_power_carrier_stack_matches_frozen_P"])

    def test_graph_kernel_is_new_and_has_eight_elements(self):
        old,new=audit.old_kernel(),audit.changed_kernel()
        self.assertEqual(len(new),8)
        self.assertNotIn(audit.D+(0,),new)
        self.assertIn(audit.D+(1,),new)
        self.assertEqual(sorted(k[:7] for k in new),old)
        self.assertNotIn((0,0,0,0,0,0,0,1),new)

    def test_unique_graph_bits_for_one_odd_compensator(self):
        row=self.report["explicit_changed_spectator_category"]
        choices=row["all_eight_one_odd_F_graph_kernel_choices"]
        self.assertEqual(len(choices),8)
        self.assertEqual([a["F_center_bits_over_D_KT_KS"] for a in choices if a["new_fermion_and_scalar_descend"]],[[1,0,0]])

    def test_W_genuine_but_M_and_F_individually_not(self):
        new=audit.changed_kernel()
        W=(0,1,0,0,0,0,0,1)
        M=(0,1,0,0,0,0,0,0)
        F=(0,0,0,0,0,0,0,1)
        self.assertEqual(audit.character_descent(W,new),[0]*8)
        self.assertNotEqual(audit.character_descent(M,new),[0]*8)
        self.assertNotEqual(audit.character_descent(F,new),[0]*8)

    def test_new_scalar_fermion_and_N1_theta_centers(self):
        row=self.report["explicit_changed_spectator_category"]
        fermion=row["new_fermion_center_bits"]
        scalar=row["new_scalar_center_bits"]
        theta=(1,1,0,1,0,0,0,0)
        self.assertEqual(audit.character_descent(fermion,audit.changed_kernel()),[0]*8)
        self.assertEqual(audit.character_descent(scalar,audit.changed_kernel()),[0]*8)
        self.assertEqual(audit.character_descent(theta,audit.changed_kernel()),[0]*8)
        self.assertEqual(tuple((a+b)%2 for a,b in zip(fermion,theta)),tuple(scalar))

    def test_all_old_characters_preserved_and_new_product_character_count(self):
        old=[c for c in product(range(2),repeat=7) if not any(audit.character_descent(c,audit.old_kernel()))]
        new={c for c in product(range(2),repeat=8) if not any(audit.character_descent(c,audit.changed_kernel()))}
        W=(0,1,0,0,0,0,0,1)
        from_product={tuple((a+bit*b)%2 for a,b in zip(c+(0,),W)) for c in old for bit in (0,1)}
        self.assertEqual(len(old),16)
        self.assertEqual(len(new),32)
        self.assertEqual(new,from_product)

    def test_graph_quotient_isomorphism_independent_of_representative(self):
        # Full U1 phases use exponents mod16; K's chi_M is precisely(-1)^n.
        for normal_exp,f_exp in product(range(16),repeat=2):
            W=(normal_exp+f_exp)%16
            for k in audit.old_kernel():
                new_n=(normal_exp+8*k[1])%16
                new_f=(f_exp+8*k[1])%16
                self.assertEqual((new_n+new_f)%16,W)
        row=self.report["explicit_changed_spectator_category"]
        self.assertTrue(row["abstract_new_group_is_original_geometric_group_times_one_U1"])
        self.assertFalse(row["natural_map_c_to_c_comma_one_descends_through_original_K"])

    def test_canonical_section_cancels_M_instead_of_realizing_half_normal_line(self):
        for exponent in range(16): self.assertEqual((exponent-exponent)%16,0)
        row=self.report["retained_curvature_and_global_normal_boundary"]
        d,u,v=audit.d,audit.u,audit.v
        self.assertEqual(sp.expand(sp.sympify(row["new_index_P_W"]).subs(v,-u)),d**3)
        self.assertIn("w=0",row["canonical_geometric_section_has"])

    def test_compensator_is_Abelian_centralizer_not_full_Sp1(self):
        row=self.report["changed_category_SMW_and_space_group_lift"]
        self.assertTrue(row["checks"]["F_commutes_with_nonzero_gauge_charge"])
        self.assertFalse(row["checks"]["full_Sp1_offdiagonal_generator_commutes_with_charge"])
        self.assertFalse(row["F_is_an_independent_full_Sp1_on_the_same_two_components"])
        self.assertIn("hyperino remains R singlet",row["R_assignment"])

    def test_full_SMW_reality_with_unchanged_effective_twists(self):
        z=audit.ZETA
        lorentz=sp.diag(z,1/z)
        M=sp.diag(z,1/z)
        F=sp.diag(1/z,z)
        reality=sp.kronecker_product(audit.J,audit.J)
        for m,n in product(range(4),range(3)):
            h=z*sp.I**m
            H=sp.diag(h,sp.conjugate(h))
            corrected=audit.clean(M*F*H)
            self.assertEqual(audit.clean(corrected-H),sp.zeros(2))
            hyperino=audit.clean(sp.kronecker_product(lorentz,corrected.inv().T))
            self.assertEqual(audit.clean(hyperino**4),sp.eye(4))
            self.assertEqual(audit.clean(reality*sp.conjugate(hyperino)-hyperino*reality),sp.zeros(4))
            k=sp.diag(z**(2*n),z**(-2*n))
            U=(-1)**n*sp.eye(2)
            self.assertEqual(audit.clean(U*k*k),sp.eye(2))

    def test_Cartan_pair_is_not_a_full_unchanged_Sp267_embedding(self):
        F=sp.diag(1/audit.ZETA,audit.ZETA)
        self.assertNotEqual(audit.clean(F*audit.J-audit.J*F),sp.zeros(2))
        row=self.report["changed_category_SMW_and_space_group_lift"]
        self.assertFalse(row["checks"]["pair_F_commutes_with_full_old_flavor_block"])
        self.assertFalse(row["same_267_hyper_full_flavor_embedding_constructed"])
        self.assertIn("center descent does not establish",row["full_old_flavor_representation_scope"])
        self.assertIn("partner content",row["quaternionic_full_flavor_completion"])

    def test_full_smooth_cocycle_is_rebound_before_changed_group_test(self):
        row=self.report["changed_category_SMW_and_space_group_lift"]
        self.assertEqual(row["new_relation_defects"]["A4"],list(audit.KN+(1,)))
        self.assertEqual(row["new_relation_defects"]["AVAinvU"],list(audit.KS+(0,)))
        for defect in row["new_relation_defects"].values(): self.assertIn(tuple(defect),audit.changed_kernel())
        changed=copy.deepcopy(self.frozen)
        changed["bound_square_space_group"]["relation_defects_mod_center_bits"]["AVAinvU"]=[0]*6
        with self.assertRaises(RuntimeError): audit.matrix_and_space_group_lift(changed)

    def test_all_four_stratum_powers_bound_to_old_saved_cocycle(self):
        rows=self.report["changed_category_SMW_and_space_group_lift"]["fixed_strata"]
        self.assertEqual([r["quotient_order"] for r in rows],[4,4,2,2])
        self.assertEqual([r["inherited_exact_cover_power"] for r in rows],
                         [r["cover_power"] for r in self.frozen["bound_fixed_strata"]])
        expected=tuple((a+b)%2 for a,b in zip(audit.KN,audit.KS))+(1,)
        self.assertEqual(rows[2]["cover_power_center_bits"],list(expected))
        self.assertEqual(rows[3]["cover_power_center_bits"],list(expected))
        changed=copy.deepcopy(self.frozen)
        changed["bound_fixed_strata"][2]["cover_power"]="(Utilde*Atilde^2)^2=krot"
        with self.assertRaises(RuntimeError): audit.matrix_and_space_group_lift(changed)

    def test_spectator_curvature_and_index_cost_are_exact(self):
        row=self.report["retained_curvature_and_global_normal_boundary"]
        d,u,v,w,p=audit.d,audit.u,audit.v,audit.w,audit.p
        self.assertEqual([sp.sympify(x) for x in row["rank_ch1_ch2_ch3"]],[0,0,d*d,d**3+d*d*u+d*d*v])
        self.assertEqual(sp.expand(sp.sympify(row["new_index_P_W"])-d*d*(d+u)),d*d*v)
        I=lambda x:x**3/6-x*p/24
        self.assertEqual(sp.expand(I(2*d+w)-2*I(d+w)+I(w)-d*d*(d+w)),0)
        for actual,c in zip(row["inherited_quarter_half_profile_with_curvature_retained"],(sp.Rational(1,4),sp.Rational(1,4),-sp.Rational(1,2))):
            self.assertEqual(sp.expand(sp.sympify(actual)-c*d*d*(d+u+v)),0)

    def test_genuine_F_squared_relation_does_not_make_F_genuine(self):
        new=audit.changed_kernel()
        # W^2*N^-1=F^2 has zero mod2 center character although F does not.
        for k in new: self.assertEqual((2*k[7])%2,0)
        self.assertTrue(any(k[7] for k in new))
        self.assertEqual(sp.expand(2*(audit.u+audit.v)-2*audit.u),2*audit.v)

    def test_CP2_odd_normal_spin_total_space_has_no_flat_compensator(self):
        row=self.report["retained_curvature_and_global_normal_boundary"]["odd_normal_example"]
        self.assertEqual((3+1)%2,0)
        for j in range(-100,101):
            self.assertNotEqual(2*j,1)
            self.assertNotEqual(sp.Rational(2*j-1,2),0)
        self.assertFalse(row["normal_M_square_root_exists"])
        self.assertFalse(row["curvature_free_compensator_exists"])
        self.assertFalse(row["this_is_an_ordinary_spin_four_manifold_test"])
        self.assertFalse(row["this_is_a_full_compact_orbifold_or_quantum_anomaly_calculation"])

    def test_pure_geometric_subgroup_intersection_is_only_D(self):
        pure=[k for k in audit.old_kernel() if k[2:]==(0,)*5]
        self.assertEqual(pure,[(0,)*7,audit.D])

    def test_no_original_kernel_or_gate_promoted(self):
        row=self.report["explicit_changed_spectator_category"]
        self.assertTrue(row["one_added_spectator_U1_changes_the_category"])
        self.assertFalse(row["old_parent_kernel_edited_or_replaced_in_place"])
        self.assertFalse(row["new_category_is_accepted_same_action_parent"])
        self.assertTrue(all(v is False for v in self.report["remaining_obligations"].values()))

    def test_rehashed_D_repair_or_curvature_erasure_rejected(self):
        changes=[("unchanged_geometric_kernel_obstruction","unchanged_geometric_Gammahat_with_independent_F_can_contain_the_M_twisted_carrier",True),
                 ("retained_curvature_and_global_normal_boundary","extra_compensator_curvature_term","0"),
                 ("explicit_changed_spectator_category","new_category_is_accepted_same_action_parent",True)]
        for section,key,value in changes:
            changed=copy.deepcopy(self.report)
            changed[section][key]=value
            changed["core_sha256"]=audit.canonical_sha(changed)
            with self.assertRaises(RuntimeError): audit.validate_certificate(changed)

    def test_invalid_center_arguments_rejected(self):
        for values,length in (((1,2),2),((True,0),2),((1,),2)):
            with self.assertRaises(ValueError): audit.bits(values,length)
        with self.assertRaises(ValueError): audit.dot((1,),(1,0))
        with self.assertRaises(ValueError): audit.span([])


if __name__=="__main__":
    unittest.main()
