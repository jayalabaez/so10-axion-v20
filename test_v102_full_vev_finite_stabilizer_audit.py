import copy
from itertools import product
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import sympy as sp

import v102_full_vev_finite_stabilizer_audit as audit


class FullVEVFiniteStabilizerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()
        cls.group = cls.report["known_finite_subgroup"]
        cls.action = cls.report["written_action_and_full_VEV_stabilizer"]
        cls.parity = cls.report["locked_flavor_parity_and_frozen_projectors"]
        cls.characters = cls.report["component_characters_and_selection_rule"]

    def rehash(self, report):
        report["core_sha256"] = audit.canonical_sha(report)
        return report

    def test_canonical_lineage_and_roundtrip(self):
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))
        self.assertEqual(json.loads(json.dumps(self.report)), self.report)
        for key, (_, core) in audit.PARENTS.items():
            self.assertEqual(self.report["input_core_hashes"][key], core)
        audit.validate_certificate(self.report)

    def test_CRLF_portable_source_pins(self):
        path = audit.ROOT/"v101_higgs_background_restriction_audit.py"
        raw = path.read_bytes().replace(b"\r\n", b"\n")
        expected = audit.portable_sha(path)
        with patch.object(Path, "read_bytes", return_value=raw.replace(b"\n", b"\r\n")):
            self.assertEqual(audit.portable_sha(path), expected)

    def test_source_pins_fresh_after_pure_cache(self):
        original = audit.portable_sha
        for name in ("susy_v101_cover_lift_higgs_section_solvability_audit.py",
                     "test_susy_v101_multipath_g1_frontier_master_audit.py",
                     "v101_higgs_background_restriction_audit.py",
                     "test_susy_v90_external_c8_quotient_daifreed_rees_equivariance_audit.py"):
            with patch.object(audit, "portable_sha", side_effect=lambda p: "0"*64 if p.name == name else original(p)):
                with self.assertRaisesRegex(RuntimeError, "source/test pin"):
                    audit.build_certificate()

    def test_changed_parent_rejected(self):
        original = Path.read_text
        def read(path, *args, **kwargs):
            value = original(path, *args, **kwargs)
            if path.name == audit.PARENTS["v101_master"][0]:
                data = json.loads(value)
                data["core_sha256"] = "0"*64
                return json.dumps(data)
            return value
        with patch.object(Path, "read_text", read):
            with self.assertRaisesRegex(RuntimeError, "canonical V101"):
                audit.build_certificate()

    def test_actual_old_kernel_expands_to_nine_coordinates(self):
        data = json.loads((audit.ROOT/audit.PARENTS["v101_route"][0]).read_text(encoding="utf-8"))
        source = data["frozen_space_group_cover_obstruction"]["bound_actual_frozen_data"]["old_kernel_generators"]
        for name, expected in (("D_geom", audit.DGEOM), ("KT", audit.KT), ("KS", audit.KS)):
            t, n, g, r, h3, h267, k = source[name]
            self.assertEqual((t, n, g, 2*r, 2*h3, 2*h267, 2*h267, 2*h267, 4*k), expected)

    def test_unchanged_kernel_order_and_closure(self):
        kernel = audit.old_kernel()
        self.assertEqual(len(kernel), 8)
        for a, b in product(kernel, repeat=2):
            self.assertIn(audit.torus_add(a, b), kernel)
        for a in kernel:
            self.assertEqual(audit.torus_scale(a, 2), audit.ZERO)

    def test_all64_subgroup_cosets_are_distinct(self):
        points = list(product(range(2), range(8), range(4)))
        self.assertEqual(len({audit.quotient(audit.lift_element(x)) for x in points}), 64)
        for a, b in product(points, repeat=2):
            summed = ((a[0]+b[0]) % 2, (a[1]+b[1]) % 8, (a[2]+b[2]) % 4)
            self.assertEqual(audit.lift_element(summed), audit.torus_add(audit.lift_element(a), audit.lift_element(b)))

    def test_k_fourth_is_Spin11_center_not_identity(self):
        g = audit.torus_scale(audit.KGEN, 4)
        spin = (0, 0, 1, 0, 0, 0, 0, 0, 0)
        self.assertEqual(audit.torus_add(g, spin), audit.KS)
        self.assertEqual(audit.quotient(g), audit.quotient(spin))
        self.assertNotEqual(audit.quotient(g), audit.quotient(audit.ZERO))
        self.assertFalse(self.group["surviving_g_is_independent_external_disconnected_component"])

    def test_exact_R_squared_g_f_equals_P265_mod_KT_KS(self):
        difference = audit.torus_add(audit.lift_element((1, 4, 2)), audit.P265)
        self.assertEqual(difference, audit.torus_add(audit.KT, audit.KS))
        self.assertIn(difference, audit.old_kernel())
        self.assertEqual(audit.quotient(audit.lift_element((1, 4, 2))), audit.quotient(audit.P265))
        self.assertNotEqual(audit.quotient(audit.P265), audit.quotient(audit.ZERO))

    def test_R_flavor_locking_is_not_pure_R(self):
        r = audit.RTILDE
        self.assertEqual(r[3:8], (1, 3, 0, 1, 3))
        pure_R = (0, 0, 0, 1, 0, 0, 0, 0, 0)
        self.assertNotEqual(audit.quotient(r), audit.quotient(pure_R))
        self.assertEqual(self.parity["actual_H267_R_flavor_rho0123_census"], [265, 1, 0, 1])

    def test_P265_is_not_fermion_parity_or_epsilonT(self):
        self.assertNotEqual(audit.quotient(audit.P265), audit.quotient(audit.FERMION))
        self.assertFalse(self.group["P265_is_old_universal_fermion_parity"])
        self.assertFalse(self.group["epsilonT_relabelled_as_fermion_parity"])
        self.assertFalse(self.parity["is_center_of_entire_unreduced_Sp267"])

    def test_component_rule_follows_superspace_partner(self):
        for value in product(range(2), range(8), range(4)):
            for q, r in product(range(-4, 5), range(4)):
                scalar = audit.component_exponent(value, q, r)
                fermion = audit.component_exponent(value, q, r, True)
                self.assertEqual((scalar-audit.theta_exponent(value)) % 8, fermion)

    def test_all_written_W_Kahler_and_driver_constants_are_invariant(self):
        rows = self.action["written_action_checks"]
        self.assertEqual(len(rows), 18)
        self.assertEqual(self.action["source_V90_allowed_operator_count"], 13)
        self.assertEqual(sum(row["operator_kind"] == "Kahler" for row in rows), 1)
        for row in rows:
            self.assertEqual(row["all_64_action_residuals_mod8"], [0]*64)
        self.assertEqual(sum(row["operator"].startswith("linear ") for row in rows), 3)

    def test_source_ledger_factors_are_bound_not_new_couplings(self):
        source = json.loads((audit.ROOT/"SUSY_V90_EXTERNAL_C8_QUOTIENT_DAIFREED_REES_EQUIVARIANCE_AUDIT.json").read_text(encoding="utf-8"))
        source = source["charged_neutral_and_compensator_repair"]["corrected_compensator"]["operator_ledger"]
        expected = [(r["operator"], r["factors"]) for r in source if r["selection_rule_allowed"]]
        self.assertEqual([(r["operator"], r["factors"]) for r in self.action["written_action_checks"][:13]], expected)

    def test_all_five_VEVs_fix_exactly16_elements(self):
        rows = self.action["all_64_VEV_tests"]
        self.assertEqual(len(rows), 64)
        passing = [tuple(r["f_k_R"]) for r in rows if r["fixes_all_VEVs"]]
        self.assertEqual(passing, list(product(range(2), (0, 4), range(4))))
        self.assertEqual(self.action["stabilizer_order"], 16)
        self.assertEqual(self.action["bosonic_quotient_by_f_order"], 8)

    def test_independent_VEV_phase_equations(self):
        charges = (8, -8, 4, 6, -6)
        for row in self.action["all_64_VEV_tests"]:
            _, k, _ = row["f_k_R"]
            phases = [q*k % 8 for q in charges]
            self.assertEqual(phases, row["VEV_phase_exponents_mod8"])
            self.assertEqual(not any(phases), k in (0, 4))

    def test_R4_selector_survives_VEVs(self):
        self.assertTrue(self.action["Rtilde_preserved_by_all_five_proposed_VEVs"])
        forbidden = self.action["four_forbidden_V90_operators_remain_R_forbidden"]
        self.assertEqual(len(forbidden), 4)
        self.assertTrue(all(row["Rtilde_action_residual_mod8"] == 4 for row in forbidden))

    def test_P265_exact_block_matrices_and_census(self):
        rows = self.parity["compressed_blocks"]
        self.assertEqual(sum(row["copies"]*row["hypers_per_copy"] for row in rows), 267)
        self.assertEqual(sum(row["copies"]*row["hypers_per_copy"] for row in rows if row["P265_sign"] == -1), 265)
        for row in rows:
            P = audit.mass.matrix(row["P265_matrix"])
            self.assertEqual(P, row["P265_sign"]*sp.eye(2*row["hypers_per_copy"]))
            self.assertTrue(all(row["checks"].values()))
        self.assertEqual((self.parity["odd_selected_N1_zero_modes"], self.parity["even_selected_Phi_zero_modes"]), (9, 2))

    def test_P265_uses_same_frozen_R_and_projector_blocks(self):
        p = audit.previous.load_inputs()
        rrows = p["v93_route"]["smooth_R_and_wall_mass_extension"]["singlet_R_extension"]["compressed_direct_sum_blocks"]
        for result, saved in zip(self.parity["compressed_blocks"], rrows):
            RF = audit.mass.matrix(saved["certificate"]["R_flavor"])
            self.assertEqual(audit.mass.clean(-RF**2), audit.mass.matrix(result["P265_matrix"]))
            self.assertEqual(result["copies"], saved["copies"])

    def test_visible_only_kernel_cannot_be_promoted_to_all_fields(self):
        self.assertEqual(self.characters["visible_only_action_kernel_f_k_R"], [[0, 0, 0], [1, 4, 2]])
        self.assertEqual(self.characters["visible_plus_nine_extras_action_kernel_f_k_R"], [[0, 0, 0]])
        self.assertEqual(self.characters["visible_only_faithful_image_order"], 8)
        self.assertEqual(self.characters["with_nine_extras_faithful_image_order"], 16)
        self.assertFalse(self.characters["relation_valid_on_nine_extras"])

    def test_extra_parity_same_on_scalar_and_fermion(self):
        extras = [r for r in self.characters["field_character_rows"] if r["is_extra_selected_mode"]]
        visible = [r for r in self.characters["field_character_rows"] if not r["is_extra_selected_mode"]]
        self.assertEqual(len(extras), 9)
        self.assertTrue(all(r["P265_scalar_and_Weyl_exponents_mod8"] == [4, 4] for r in extras))
        self.assertTrue(all(r["P265_scalar_and_Weyl_exponents_mod8"] == [0, 0] for r in visible))

    def test_all_order_mod2_selection_rule_algebra(self):
        self.assertIn("visible factors with odd q8", self.characters["all_order_selection_rule"])
        # Conjugation does not change either mod2 charge. The categories are
        # ordinary visible matter(qodd,Rodd), visible other(qeven,Reven), and
        # extra singlets(qeven,Rodd). This proof is independent of operator degree.
        for n_matter, n_other, n_extra in product(range(8), repeat=3):
            gauge_even = n_matter % 2 == 0
            R_even = (n_matter+n_extra) % 2 == 0
            if gauge_even and R_even:
                self.assertEqual(n_extra % 2, 0)
        self.assertFalse(self.characters["any_odd_extra_decay_to_only_listed_even_visible_fields_preserving_g_and_Rtilde"])

    def test_stability_is_quantum_and_spectrum_conditional(self):
        text = self.characters["conditional_lightest_odd_state_stability"]
        for phrase in ("FULL quantum action", "anomalies and nonperturbative", "no lighter P-odd state", "not been established"):
            self.assertIn(phrase, text)
        self.assertFalse(self.characters["stable_particle_prediction_of_an_accepted_theory"])
        self.assertFalse(self.characters["full_P265_quantum_anomaly_freedom_proved"])
        self.assertFalse(self.characters["cosmological_viability_mass_or_abundance_computed"])

    def test_V93_singlets_not_V65_orphan_quark_pair(self):
        self.assertIn("nine V93", self.characters["extra_sector_identity"])
        self.assertIn("not the earlier V65", self.characters["extra_sector_identity"])

    def test_full_stabilizer_and_nonlinear_vacuum_are_not_promoted(self):
        scope = self.report["full_stabilizer_boundary"]
        self.assertTrue(scope["exact_stabilizer_only_inside_named_H"])
        self.assertFalse(scope["full_unbroken_continuous_and_finite_group_classified"])
        self.assertFalse(scope["additional_R_flavor_lockings_excluded"])
        self.assertFalse(scope["localized_Fi_PA_X_Xbar_S8_SB_SX_mediator_Gammahat_representations_constructed"])
        self.assertFalse(scope["old_central_kernel_or_frozen_space_group_changed"])
        self.assertFalse(scope["new_finite_symmetry_or_background_adopted"])
        self.assertFalse(any(self.report["remaining_obligations"].values()))

    def test_invalid_inputs_rejected(self):
        for bad in ((0,)*8, (2,)+(0,)*8, (False,)+(0,)*8, (0,)*8+(8,)):
            with self.assertRaises(ValueError): audit.torus_element(bad)
        for bad in ((2, 0, 0), (0, 8, 0), (0, 0, 4), (False, 0, 0), (0, 0)):
            with self.assertRaises(ValueError): audit.generator_element(bad)
        with self.assertRaises(ValueError): audit.torus_scale(audit.RTILDE, 0.5)
        with self.assertRaises(ValueError): audit.component_exponent((0, 0, 0), 1.5, 0)
        with self.assertRaises(ValueError): audit.component_exponent((0, 0, 0), 2, 4)
        with self.assertRaises(ValueError): audit.component_exponent((0, 0, 0), 2, 0, 1)

    def test_rehashed_group_or_quantum_overclaim_rejected(self):
        changed = copy.deepcopy(self.report)
        changed["written_action_and_full_VEV_stabilizer"]["stabilizer_order"] = 64
        with self.assertRaises(RuntimeError): audit.validate_certificate(self.rehash(changed))
        changed = copy.deepcopy(self.report)
        changed["component_characters_and_selection_rule"]["full_P265_quantum_anomaly_freedom_proved"] = True
        with self.assertRaises(RuntimeError): audit.validate_certificate(self.rehash(changed))

    def test_returned_mutation_does_not_poison_cache(self):
        changed = audit.build_certificate()
        changed["known_finite_subgroup"]["unchanged_kernel"].clear()
        changed["locked_flavor_parity_and_frozen_projectors"]["compressed_blocks"].clear()
        fresh = audit.build_certificate()
        self.assertEqual(len(fresh["known_finite_subgroup"]["unchanged_kernel"]), 8)
        self.assertTrue(fresh["locked_flavor_parity_and_frozen_projectors"]["compressed_blocks"])


if __name__ == "__main__":
    unittest.main()
