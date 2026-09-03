import copy
from itertools import product
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import sympy as sp

import v100_modified_equivariant_cover_audit as audit


class ModifiedEquivariantCoverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()
        cls.cover = cls.report["minimal_combined_operator_cover"]
        cls.group = cls.report["pulled_back_square_space_group"]
        cls.response = cls.report["quantized_smooth_inverse_response"]

    def rehash(self, value):
        value["core_sha256"] = audit.canonical_sha(value)
        return value

    def test_canonical_frozen_lineage_and_roundtrip(self):
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))
        self.assertEqual(json.loads(json.dumps(self.report)), self.report)
        for key, (_, core) in audit.PARENTS.items():
            self.assertEqual(self.report["input_core_hashes"][key], core)
        audit.validate_certificate(self.report)

    def test_source_hashes_are_CRLF_portable(self):
        path = audit.ROOT/"v99_determinant_root_descent_audit.py"
        raw = path.read_bytes().replace(b"\r\n", b"\n")
        expected = audit.portable_sha(path)
        with patch.object(Path, "read_bytes", return_value=raw.replace(b"\n", b"\r\n")):
            self.assertEqual(audit.portable_sha(path), expected)

    def test_source_binding_stays_fresh_after_algebra_cache(self):
        with patch.object(audit, "portable_sha", return_value="0"*64):
            with self.assertRaisesRegex(RuntimeError, "source/test pin"):
                audit.build_certificate()

    def test_parent_core_tampering_fails_closed(self):
        original = Path.read_text
        def read(path, *args, **kwargs):
            value = original(path, *args, **kwargs)
            if path.name == audit.PARENTS["v99_master"][0]:
                data = json.loads(value)
                data["core_sha256"] = "0"*64
                return json.dumps(data)
            return value
        with patch.object(Path, "read_text", read):
            with self.assertRaisesRegex(RuntimeError, "immutable canonical V99"):
                audit.build_certificate()

    def test_two_kernel_conditions_have_exact_intersection_D(self):
        old = audit.lift.old_kernel()
        expected = [value for value in old
                    if sum(a*b for a,b in zip(value,audit.CCHAR)) % 2 == 0
                    and sum(a*b for a,b in zip(value,audit.SIGMA)) % 2 == 0]
        self.assertEqual(expected, audit.lift.span((audit.D,)))
        self.assertEqual(expected, audit.combined_kernel())
        self.assertEqual(len(old)//len(expected), 4)

    def test_all_intermediate_covers_and_minimality_scope(self):
        rows = self.cover["all_five_intermediate_covers_preserving_D_geom"]
        self.assertEqual(sorted(row["cover_degree"] for row in rows), [1,2,2,2,4])
        passing = [row for row in rows if row["C_descends"] and row["Sigma_c_descends"]]
        self.assertEqual([row["cover_degree"] for row in passing], [4])
        self.assertIn("individual C and Sigma_c", self.cover["minimality_scope"])
        self.assertIn("not minimality", self.cover["minimality_scope"])

    def test_deck_map_kernel_and_surjectivity(self):
        old = audit.lift.old_kernel()
        self.assertEqual({audit.deck_bits(k) for k in old}, set(product(range(2),repeat=2)))
        self.assertEqual([k for k in old if audit.deck_bits(k)==(0,0)], audit.combined_kernel())
        self.assertEqual(audit.deck_bits(audit.KT), (1,0))
        self.assertEqual(audit.deck_bits(audit.KS), (0,1))
        self.assertEqual(audit.deck_bits(audit.KN), (1,0))
        for left,right in product(old,repeat=2):
            summed = tuple((a+b)%2 for a,b in zip(left,right))
            self.assertEqual(audit.deck_bits(summed), tuple((a+b)%2 for a,b in zip(audit.deck_bits(left),audit.deck_bits(right))))

    def test_all_old_representation_characters_pull_back(self):
        old = self.cover["all_old_16_center_characters"]
        self.assertEqual(len(old),16)
        for char in old:
            self.assertFalse(any(audit.lift.character_descent(char,audit.combined_kernel())))
            self.assertEqual([audit.lift.dot(char,k) for k in (audit.KT,audit.KS)], [0,0])
        self.assertTrue(self.cover["all_genuine_old_representations_pull_back"])
        self.assertFalse(self.cover["every_old_background_bundle_lifts_to_this_cover"])
        self.assertIn("triple-overlap defects",self.cover["background_lift_scope"])
        self.assertFalse(self.cover["previously_unconstructed_old_field_representations_promoted"])

    def test_bare_operators_descend_but_normal_M_does_not(self):
        for row in self.cover["bare_eta_operator_rows"]:
            self.assertEqual(row["combined_kernel_exponents"], [0,0])
            self.assertEqual(row["deck_exponents_epsT_epsS"], [1,row["C_power"]%2])
        self.assertFalse(self.cover["M_half_normal_line_now_genuine"])
        self.assertTrue(self.cover["literal_geometric_D_preserved"])

    def test_alpha_is_additive_order_four(self):
        vectors = [(m,n,e) for m,n,e in product(range(-1,2),range(-1,2),range(2))]
        for value in vectors:
            self.assertEqual(audit.previous.alpha(value,4), value)
        for left,right in product(vectors,repeat=2):
            summed = (left[0]+right[0],left[1]+right[1],(left[2]+right[2])%2)
            a,b = audit.previous.alpha(left),audit.previous.alpha(right)
            self.assertEqual(audit.previous.alpha(summed), (a[0]+b[0],a[1]+b[1],(a[2]+b[2])%2))

    def test_group_associativity_inverses_and_negative_powers(self):
        points = [audit.IDENTITY,audit.A,audit.U,audit.V,audit.EPS_T,audit.EPS_S,
                  (7,-2,1,1),(3,1,-1,0)]
        for a,b,c in product(points,repeat=3):
            self.assertEqual(audit.multiply(a,audit.multiply(b,c)),audit.multiply(audit.multiply(a,b),c))
        for a in points:
            self.assertEqual(audit.multiply(a,audit.inverse(a)),audit.IDENTITY)
            self.assertEqual(audit.multiply(audit.inverse(a),a),audit.IDENTITY)
            self.assertEqual(audit.power(a,-3),audit.power(audit.inverse(a),3))

    def test_projection_is_old_square_group_homomorphism(self):
        points = [(a,m,n,e) for a,m,n,e in product((0,1,4,7),(-1,1),(0,2),(0,1))]
        for left,right in product(points,repeat=2):
            expected = audit.previous.extended_mul((left[0]%4,left[1],left[2],0),
                                                   (right[0]%4,right[1],right[2],0))
            value = audit.multiply(left,right)
            self.assertEqual((value[0]%4,value[1],value[2]),expected[:3])

    def test_independent_central_deck_generators(self):
        deck = [audit.IDENTITY,audit.EPS_T,audit.EPS_S,audit.multiply(audit.EPS_T,audit.EPS_S)]
        self.assertEqual(len(set(deck)),4)
        for value in deck:
            self.assertEqual(audit.power(value,2),audit.IDENTITY)
            for generator in (audit.A,audit.U,audit.V):
                self.assertEqual(audit.multiply(value,generator),audit.multiply(generator,value))
        self.assertTrue(self.group["kernel_is_C2_times_C2"])

    def test_actual_saved_relation_defects_are_rebound(self):
        self.assertEqual(self.group["derived_deck_relation_defects"],
                         {"A4":[1,0],"UVUinvVinv":[0,0],"AUAinvVinv":[0,0],"AVAinvU":[0,1]})
        self.assertEqual(self.group["bound_primitive_C8_alpha_u_v"],[0,2,2])
        self.assertEqual(self.group["relation_values"]["A4"],list(audit.EPS_T))
        self.assertEqual(self.group["relation_values"]["AVAinvU"],list(audit.EPS_S))

    def test_rotation_subgroup_alone_prevents_splitting(self):
        rows = self.group["all_four_rotation_lifts_fourth_powers"]
        self.assertEqual(rows,[list(audit.EPS_T)]*4)
        self.assertNotEqual(audit.EPS_T,audit.IDENTITY)
        self.assertFalse(self.group["pullback_extension_splits"])

    def test_C_and_normal_Sigma_are_actual_characters_of_extension(self):
        values = [(a,m,n,e) for a,m,n,e in product((0,1,4,7),(-1,1),(0,2),(0,1))]
        for left,right in product(values,repeat=2):
            for character in (audit.C_exponent,audit.Sigma_exponent):
                self.assertEqual(character(audit.multiply(left,right)),(character(left)+character(right))%8)
        self.assertEqual([audit.C_exponent(g) for g in (audit.A,audit.U,audit.V,audit.EPS_T,audit.EPS_S)], [0,2,2,0,4])
        self.assertEqual([audit.Sigma_exponent(g) for g in (audit.A,audit.U,audit.V,audit.EPS_T,audit.EPS_S)], [1,0,0,4,0])

    def test_four_stabilizer_orders_and_phases(self):
        rows = self.group["fixed_strata"]
        self.assertEqual([row["original_order"] for row in rows],[4,4,2,2])
        self.assertEqual([row["actual_lift_order"] for row in rows],[8,8,4,4])
        self.assertEqual([row["old_power_deck_bits"] for row in rows],[[1,0],[1,0],[1,1],[1,1]])
        self.assertEqual([row["C_exponent_mod8"] for row in rows],[0,2,2,2])
        self.assertEqual([row["Sigma_C0_C1_C2_exponents_mod8"] for row in rows],[[1,1,1],[1,3,5],[2,4,6],[2,4,6]])

    def test_naive_ineffective_projection_is_not_operator_descent(self):
        for row in self.group["bare_operator_ordinary_deck_projectors"]:
            self.assertEqual(row["ordinary_deck_average"],"0")
        self.assertEqual(sp.Rational(sum(1 for _ in product(range(2),repeat=2)),4),1)
        self.assertFalse(self.group["orbifold_Dirac_domain_or_twisted_sectors_constructed"])
        self.assertIn("no general prohibition",self.group["naive_ineffective_orbifold_projection_warning"])
        self.assertFalse(self.group["new_stabilizer_orders_are_old_projector_denominators"])

    def test_genuine_virtual_bundle_index_identity(self):
        c,x,p = audit.c,audit.x,audit.p
        q = sp.Symbol("q")
        ch = sum(level*sp.exp(n*c*q) for n,level in ((2,1),(1,-2),(0,1)))
        coefficient = sp.expand(sp.series(ch*sp.exp(x*q/2)*(1-p*q*q/24),q,0,4).removeO()).coeff(q,3)
        self.assertEqual(coefficient,c**3+x*c*c/2)
        self.assertEqual(sp.expand(coefficient+c**3-(2*c)**2*(2*c+x/2)/4),0)
        self.assertEqual(self.response["rank_ch1_ch2_ch3"],["0","0","c**2","c**3"])

    def test_nonspin_period_example_has_no_normal_root(self):
        row = self.response["CP2_times_CP1_test"]
        self.assertEqual(row["Spin_c_indices_C0_C1_C2"],["0","1","6"])
        self.assertEqual(row["integral_Q"],"7")
        self.assertTrue(row["normal_determinant_has_no_square_root"])

    def test_integral_index_family_on_CP2_times_CP1(self):
        h,j,r,t,m,n = sp.symbols("h j r t m n",integer=True)
        z = m*h+n*j
        expression = ((z+((2*r+1)*h+2*t*j)/2)**3/6
                      -(z+((2*r+1)*h+2*t*j)/2)*3*h*h/24)
        period = sp.expand(expression).coeff(h,2).coeff(j,1)
        for rr,tt,mm,nn in product(range(-1,2),repeat=4):
            value = period.subs({r:rr,t:tt,m:mm,n:nn})
            self.assertTrue(value.is_Integer)

    def test_response_and_inverse_have_opposite_curvature(self):
        self.assertEqual(sp.expand(sp.sympify(self.response["positive_response_curvature"])
                                   +sp.sympify(self.response["inverse_response_curvature"])),0)
        self.assertTrue(self.response["genuine_quantized_closed5_inverse_defined"])
        self.assertFalse(self.response["definition_requires_a_six_manifold_filling"])
        self.assertFalse(self.response["local_curvature_alone_used_to_infer_global_phase"])
        self.assertEqual(self.response["eta_integer_levels"],{"C^2":1,"C":-2,"1":1})

    def test_shared_exact_stack_is_not_independent_gluing(self):
        stack = self.response["shared_background_stack"]
        self.assertEqual(sum(stack["integer_response_powers"]),0)
        self.assertEqual(sp.expand(sum(map(sp.sympify,stack["curvatures"]))),0)
        self.assertTrue(stack["valid_for_all_same_covered_backgrounds_including_torsion"])
        self.assertFalse(stack["is_a_recomputed_bulk_equivariant_localization_profile"])
        self.assertFalse(stack["proves_cancellation_for_independent_endpoint_data"])

    def test_joint_deck_exact_spectral_values(self):
        rows = self.report["exact_joint_deck_product_tests"]["eight_exact_tests"]
        self.assertEqual(len(rows),8)
        expected = {(0,0):["0","1/2","3/2"],(0,1):["0","0","3/2"],
                    (1,0):["0","0","0"],(1,1):["0","1/2","0"]}
        for row in rows:
            t,s = row["deck_twist_epsT_epsS"]
            self.assertEqual(row["relative_phase"],"-1" if (t+s)%2 else "+1")
            if row["initial_circle_spin"]=="periodic":
                self.assertEqual(row["xi_C0_C1_C2"],expected[t,s])
        self.assertFalse(self.report["exact_joint_deck_product_tests"]["response_descends_through_diagonal_deck_subgroup_proved"])

    def test_invalid_group_or_character_inputs_fail(self):
        for value in ((8,0,0,0),(0,0,0,2),(0,0.5,0,0),(False,0,0,0),(0,0,0)):
            with self.assertRaises(ValueError):
                audit.element(value)
        with self.assertRaises(ValueError): audit.power(audit.A,0.5)
        with self.assertRaises(ValueError): audit.operator_exponent(audit.A,0.5)
        with self.assertRaises(ValueError): audit.deck_bits((0,1,0,0,0,0,0))

    def test_no_parent_adoption_or_physical_completion(self):
        self.assertFalse(self.cover["new_category_adopted_as_physical_parent"])
        self.assertFalse(self.cover["old_group_or_action_modified_in_place"])
        self.assertFalse(self.response["inverse_of_the_known_full_physical_anomaly_identified"])
        self.assertFalse(self.response["full_boundary_transgression_trivialization_or_corner_gluing_supplied"])
        self.assertFalse(any(self.report["remaining_obligations"].values()))

    def test_rehashed_cover_or_gluing_overclaim_is_rejected(self):
        for section,key,value in (("minimal_combined_operator_cover","minimum_simultaneous_operator_cover_degree",2),
                                  ("quantized_smooth_inverse_response","inverse_of_the_known_full_physical_anomaly_identified",True)):
            changed = copy.deepcopy(self.report)
            changed[section][key] = value
            with self.assertRaises(RuntimeError):
                audit.validate_certificate(self.rehash(changed))

    def test_pure_cache_does_not_expose_mutable_certificates(self):
        report = audit.build_certificate()
        report["minimal_combined_operator_cover"]["old_kernel"].clear()
        report["quantized_smooth_inverse_response"]["eta_integer_levels"].clear()
        fresh = audit.build_certificate()
        self.assertEqual(len(fresh["minimal_combined_operator_cover"]["old_kernel"]),8)
        self.assertEqual(fresh["quantized_smooth_inverse_response"]["eta_integer_levels"],{"C^2":1,"C":-2,"1":1})


if __name__ == "__main__":
    unittest.main()
