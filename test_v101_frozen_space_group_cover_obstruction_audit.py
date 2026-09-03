import copy
from itertools import product
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import v101_frozen_space_group_cover_obstruction_audit as audit


class FrozenSpaceGroupCoverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()
        cls.rows = {row["name"]: row for row in cls.report["five_cover_all_lift_choices"]}

    def rehash(self, value):
        value["core_sha256"] = audit.canonical_sha(value)
        return value

    def test_canonical_frozen_lineage_and_roundtrip(self):
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))
        self.assertEqual(json.loads(json.dumps(self.report)), self.report)
        for key, (_, core) in audit.PARENTS.items():
            self.assertEqual(self.report["input_core_hashes"][key], core)
        audit.validate_certificate(self.report)

    def test_CRLF_portable_source_binding(self):
        path = audit.ROOT/"v100_modified_equivariant_cover_audit.py"
        raw = path.read_bytes().replace(b"\r\n", b"\n")
        expected = audit.portable_sha(path)
        with patch.object(Path, "read_bytes", return_value=raw.replace(b"\n", b"\r\n")):
            self.assertEqual(audit.portable_sha(path), expected)

    def test_source_binding_is_fresh_after_algebra_cache(self):
        with patch.object(audit, "portable_sha", return_value="0"*64):
            with self.assertRaisesRegex(RuntimeError, "source/test pin"):
                audit.build_certificate()

    def test_tampered_parent_fails_closed(self):
        original = Path.read_text
        def read(path, *args, **kwargs):
            value = original(path, *args, **kwargs)
            if path.name == audit.PARENTS["v100_master"][0]:
                data = json.loads(value)
                data["core_sha256"] = "0"*64
                return json.dumps(data)
            return value
        with patch.object(Path, "read_text", read):
            with self.assertRaisesRegex(RuntimeError, "immutable canonical V100"):
                audit.build_certificate()

    def test_all_five_intermediate_kernels_preserve_D(self):
        self.assertEqual(len(self.rows), 5)
        self.assertEqual(sorted(row["cover_degree"] for row in self.rows.values()), [1, 2, 2, 2, 4])
        for row in self.rows.values():
            kernel = list(map(tuple, row["kernel_Kprime"]))
            self.assertIn(audit.D, kernel)
            self.assertTrue(set(kernel) <= set(audit.lift.old_kernel()))
            for a, b in product(kernel, repeat=2):
                self.assertIn(tuple((x+y) % 2 for x, y in zip(a, b)), kernel)

    def test_explicit_cover_kernel_dictionary(self):
        self.assertEqual(self.rows["gauge_C_root"]["kernel_Kprime"], list(map(list, audit.lift.span((audit.D, audit.KT)))))
        self.assertEqual(self.rows["natural_Sigma"]["kernel_Kprime"], list(map(list, audit.lift.span((audit.D, audit.KS)))))
        diagonal = tuple((a+b) % 2 for a, b in zip(audit.KT, audit.KS))
        self.assertEqual(self.rows["diagonal"]["kernel_Kprime"], list(map(list, audit.lift.span((audit.D, diagonal)))))
        self.assertEqual(self.rows["combined"]["kernel_Kprime"], list(map(list, audit.lift.span((audit.D,)))))

    def test_saved_complete_relations_and_fixed_powers_are_rebound(self):
        data = self.report["bound_actual_frozen_data"]
        self.assertEqual(data["saved_smooth_relation_defects"], {
            "A4": [1, 1, 1, 1, 1, 0], "UVUinvVinv": [0]*6,
            "AUAinvVinv": [0]*6, "AVAinvU": [0, 1, 0, 0, 0, 1]})
        self.assertEqual(data["saved_finite_alpha_U_V"], [0, 2, 2])
        self.assertEqual(data["derived_deck_relation_defects"], {
            "A4": [1, 0], "UVUinvVinv": [0, 0], "AUAinvVinv": [0, 0], "AVAinvU": [0, 1]})
        self.assertEqual([s["old_power_deck_bits"] for s in data["saved_fixed_strata"]], [[1, 0], [1, 0], [1, 1], [1, 1]])

    def test_all64_universal_shift_formulas_match_actual_group_words(self):
        for a, u, v in product(audit.E, repeat=3):
            formula = audit.shifted_relators(a, u, v)
            self.assertEqual(formula, audit.actual_shifted_relators(a, u, v))
            self.assertEqual(formula["A4"], audit.T)
            self.assertEqual(audit.add(formula["AUAinvVinv"], formula["AVAinvU"]), audit.S)

    def test_exhaustive89_choices_have_no_proper_cover_lift(self):
        self.assertEqual([row["number_of_central_generator_choices"] for row in self.rows.values()], [1, 8, 8, 8, 64])
        self.assertEqual(sum(row["number_of_central_generator_choices"] for row in self.rows.values()), 89)
        for name, row in self.rows.items():
            passing = sum(c["all_relations_close"] for c in row["all_choices"])
            self.assertEqual(passing, int(name == "old_quotient"))
            self.assertEqual(row["frozen_representation_lifts"], name == "old_quotient")
        self.assertEqual(self.report["exact_obstruction_theorem"]["number_of_proper_covers_admitting_frozen_representation"], 0)

    def test_gauge_root_mixed_relators_cannot_both_close(self):
        row = self.rows["gauge_C_root"]
        for choice in row["all_choices"]:
            r = choice["relator_classes"]
            self.assertEqual(r["A4"], [0, 0])
            self.assertNotEqual(r["AUAinvVinv"], r["AVAinvU"])
            self.assertEqual(sum(r[key] == [0, 0] for key in ("AUAinvVinv", "AVAinvU")), 1)

    def test_other_proper_covers_reject_every_A_lift(self):
        for name in ("natural_Sigma", "diagonal", "combined"):
            for choice in self.rows[name]["all_choices"]:
                self.assertNotEqual(choice["relator_classes"]["A4"], [0, 0])

    def test_operator_descent_does_not_imply_equivariant_installation(self):
        self.assertTrue(self.rows["gauge_C_root"]["C_descends"])
        self.assertFalse(self.rows["gauge_C_root"]["Sigma_c_descends"])
        self.assertTrue(self.rows["natural_Sigma"]["Sigma_c_descends"])
        self.assertFalse(self.rows["natural_Sigma"]["C_descends"])
        self.assertFalse(self.rows["diagonal"]["C_descends"])
        self.assertFalse(self.rows["diagonal"]["Sigma_c_descends"])
        self.assertTrue(self.rows["combined"]["C_descends"])
        self.assertTrue(self.rows["combined"]["Sigma_c_descends"])
        self.assertFalse(self.rows["combined"]["frozen_representation_lifts"])

    def test_fixed_stratum_orders_for_every_central_choice(self):
        expected = [[4, 4, 2, 2], [4, 4, 4, 4], [8, 8, 4, 4], [8, 8, 2, 2], [8, 8, 4, 4]]
        rows = self.report["fixed_stratum_restriction_tests"]
        self.assertEqual([[s["lift_order"] for s in row["strata"]] for row in rows], expected)
        for row in rows:
            self.assertEqual(row["all_four_cyclic_restrictions_lift"], row["cover"] == "old_quotient")
            for stratum in row["strata"]:
                classes = stratum["old_order_power_classes"]
                self.assertEqual(len({tuple(value) for value in classes}), 1)

    def test_fixed_cyclic_detection_is_specific_not_full_H2(self):
        theorem = self.report["exact_obstruction_theorem"]
        self.assertIn("No general theorem", theorem["cyclic_detection_scope"])
        self.assertFalse(theorem["full_H2_group_computed"])
        self.assertEqual({audit.ZERO, audit.T, audit.TS, audit.add(audit.T, audit.TS)}, set(audit.E))

    def test_deck_epsilonT_is_not_old_fermion_parity(self):
        data = self.report["deck_versus_old_fermion_parity"]
        rows = {row["name"]: row for row in data["all_four_comparison_rows"]}
        self.assertEqual(rows["old_hyperino"]["epsT_epsS_sign_exponents"], [0, 0])
        self.assertEqual(rows["old_hyperscalar"]["epsT_epsS_sign_exponents"], [0, 0])
        self.assertEqual(rows["old_hyperino"]["tangent_2pi_sign_exponent"], 1)
        self.assertEqual(rows["old_hyperscalar"]["tangent_2pi_sign_exponent"], 0)
        self.assertEqual(rows["bare_Sigma_c"]["epsT_epsS_sign_exponents"], [1, 0])
        self.assertEqual(rows["gauge_root_C"]["epsT_epsS_sign_exponents"], [0, 1])
        self.assertFalse(data["epsT_is_unchanged_universal_fermion_parity"])

    def test_every_old_allowed_character_is_deck_trivial(self):
        old = audit.lift.old_kernel()
        chars = [c for c in product(range(2), repeat=7) if not any(audit.lift.character_descent(c, old))]
        self.assertEqual(len(chars), 16)
        self.assertEqual(sum(c[0] for c in chars), 8)
        for char in chars:
            self.assertEqual(audit.lift.dot(char, audit.KT), 0)
            self.assertEqual(audit.lift.dot(char, audit.KS), 0)
        self.assertNotIn((1, 0, 0, 0, 0, 0, 0), old)

    def test_checkerboard_section_projection_and_homomorphism(self):
        values = [(a, m, n) for a, m, n in product(range(4), range(-2, 3), range(-2, 3)) if (m+n) % 2 == 0]
        for value in values:
            section = audit.checkerboard_section(value)
            self.assertEqual(section[:3], value)
            self.assertEqual(audit.previous.C_exponent(section), 0)
        for left, right in product(values, repeat=2):
            target = audit.checkerboard_section(audit.old_multiply(left, right))
            source = audit.previous.multiply(audit.checkerboard_section(left), audit.checkerboard_section(right))
            self.assertEqual(audit.root_quotient(source), target)

    def test_checkerboard_equivariance_and_lattice_index(self):
        for m, n in product(range(-7, 8), repeat=2):
            if (m+n) % 2 == 0:
                e = ((m+n)//2) % 2
                self.assertEqual(((m-n)//2) % 2, (e+n) % 2)
        # The basis (1,1),(1,-1) has determinant -2.
        self.assertEqual(abs(1*(-1)-1*1), 2)
        data = self.report["explicit_changed_spatial_domains"]["checkerboard_gauge_root_lift"]
        self.assertEqual(data["index_in_frozen_S"], 2)
        self.assertEqual(data["smallest_index_spatial_subgroup_lifting_to_gauge_root_cover"], 2)
        self.assertFalse(data["is_lift_on_unchanged_frozen_S"])

    def test_checkerboard_generator_relations(self):
        mul, inv = audit.previous.multiply, audit.previous.inverse
        a = audit.checkerboard_section((1, 0, 0))
        b = audit.checkerboard_section((0, 1, 1))
        c = audit.checkerboard_section((0, 1, -1))
        self.assertEqual(audit.root_quotient(mul(mul(a, b), inv(a))), audit.root_quotient(inv(c)))
        self.assertEqual(audit.root_quotient(mul(mul(a, c), inv(a))), b)
        self.assertEqual(mul(b, c), mul(c, b))
        self.assertEqual(audit.root_quotient(audit.previous.power(a, 4)), audit.previous.IDENTITY)

    def test_translations_give_actual_combined_cover_section(self):
        values = [(0, m, n) for m, n in product(range(-3, 4), repeat=2)]
        for left, right in product(values, repeat=2):
            self.assertEqual(audit.translation_section(audit.old_multiply(left, right)),
                             audit.previous.multiply(audit.translation_section(left), audit.translation_section(right)))
        self.assertEqual(audit.translation_section((0, 1, 0)), audit.previous.U)
        self.assertEqual(audit.translation_section((0, 0, 1)), audit.previous.V)

    def test_every_rotational_element_obstructs_combined_lift(self):
        # All translations and all central choices occur in the analytic proof;
        # this independently checks a box without using its hardcoded witnesses.
        for a, m, n, t, s in product((1, 2, 3), range(-3, 4), range(-3, 4), range(2), range(2)):
            value = (a+4*t, m, n, s)
            r = 4 if a % 2 else 2
            power = audit.previous.power(value, r)
            self.assertEqual(power[1:3], (0, 0))
            self.assertEqual(audit.central_label(power)[0], 1)
        data = self.report["explicit_changed_spatial_domains"]["translation_combined_lift"]
        self.assertEqual(data["minimum_index_of_any_finite_index_subgroup_that_lifts_to_combined_cover"], 4)
        self.assertFalse(data["retains_old_rotational_fixed_strata"])

    def test_domain_changes_not_projector_or_spectrum_preservation(self):
        data = self.report["explicit_changed_spatial_domains"]
        self.assertIn("Neither construction preserves the old chiral projection", data["domain_change_cost"])
        for key in ("changed_compactification_or_subgroup_adopted", "new_projectors_twisted_sectors_or_spectrum_computed",
                    "ordinary_unramified_manifold_cover_asserted", "full_relative_inflow_obtained_from_subgroup_lift"):
            self.assertFalse(data[key])

    def test_no_full_category_or_relative_promotion(self):
        scope = self.report["scope"]
        self.assertTrue(scope["actual_saved_square_space_group_representation_is_tested"])
        self.assertTrue(scope["all_central_lift_choices_are_included"])
        self.assertFalse(scope["all_physical_Gammahat_backgrounds_identified"])
        self.assertFalse(scope["all_group_extensions_or_relative_theories_excluded"])
        self.assertFalse(scope["smooth_response_quantization_implies_frozen_equivariant_installation"])
        self.assertTrue(scope["old_genuine_representations_still_pull_back_to_every_cover"])
        self.assertFalse(scope["representation_pullback_implies_lift_of_the_fixed_S_bundle"])
        self.assertFalse(any(self.report["remaining_obligations"].values()))

    def test_strict_binary_and_subgroup_inputs(self):
        for bad in ((0, 2), (0,), (True, 0), (0.0, 1)):
            with self.assertRaises(ValueError): audit.bits2(bad)
        for bad in ((), ((1, 0),), ((0, 0), (1, 0), (0, 1))):
            with self.assertRaises(ValueError): audit.subgroup(bad)
        self.assertEqual(audit.subgroup((audit.T, audit.ZERO, audit.T)), (audit.ZERO, audit.T))

    def test_strict_old_group_and_section_inputs(self):
        for bad in ((4, 0, 0), (0, 0.5, 0), (False, 0, 0), (0, 0)):
            with self.assertRaises(ValueError): audit.old_element(bad)
        with self.assertRaises(ValueError): audit.checkerboard_section((0, 1, 0))
        with self.assertRaises(ValueError): audit.translation_section((1, 0, 0))
        with self.assertRaises(ValueError): audit.central_label(audit.previous.U)
        with self.assertRaises(ValueError): audit.central_label(audit.previous.A)

    def test_rehashed_false_lift_or_completion_is_rejected(self):
        changed = copy.deepcopy(self.report)
        changed["five_cover_all_lift_choices"][1]["frozen_representation_lifts"] = True
        with self.assertRaises(RuntimeError): audit.validate_certificate(self.rehash(changed))
        changed = copy.deepcopy(self.report)
        changed["scope"]["all_group_extensions_or_relative_theories_excluded"] = True
        with self.assertRaises(RuntimeError): audit.validate_certificate(self.rehash(changed))

    def test_pure_cache_does_not_expose_mutable_certificates(self):
        changed = audit.build_certificate()
        changed["five_cover_all_lift_choices"].clear()
        changed["explicit_changed_spatial_domains"]["translation_combined_lift"].clear()
        fresh = audit.build_certificate()
        self.assertEqual(len(fresh["five_cover_all_lift_choices"]), 5)
        self.assertEqual(fresh["explicit_changed_spatial_domains"]["translation_combined_lift"]["index_in_frozen_S"], 4)


if __name__ == "__main__":
    unittest.main()
