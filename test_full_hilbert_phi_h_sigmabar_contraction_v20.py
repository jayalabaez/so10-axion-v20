#!/usr/bin/env python3
import unittest

import full_hilbert_phi_h_sigmabar_contraction_v20 as mod


class FullHilbertContractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertFalse(self.report["flag"]["physical_CGC_normalization_derived"])
        self.assertFalse(self.report["flag"]["whole_model_validated"])
        self.assertFalse(self.report["flag"]["whole_model_excluded"])
        self.assertTrue(
            self.report["flag"]["so10_axion_direction_not_declared_unsolvable"]
        )

    def test_forms_built_and_orthogonal(self):
        basis = self.report["form_basis"]
        self.assertGreater(basis["norms"]["p"], 0.0)
        self.assertGreater(basis["norms"]["a"], 0.0)
        self.assertGreater(basis["norms"]["omega"], 0.0)
        self.assertTrue(basis["approximately_orthogonal"])

    def test_all_singlet_tadpoles_vanish(self):
        ch = self.report["channels"]
        self.assertFalse(ch["p_only"]["nonzero"])
        self.assertFalse(ch["a_only"]["nonzero"])
        self.assertFalse(ch["omega_only"]["nonzero"])
        self.assertFalse(self.report["hilbert_projection"].get("nonzero", True))
        self.assertTrue(self.report["flag"]["ps_singlet_tadpole_into_10_vanishes"])

    def test_dictionary_is_ordinary_not_1e30(self):
        scale = self.report["algebraic_convention_dictionary"][
            "algebraic_scale_from_factorials_only"
        ]
        self.assertLess(scale, 1.0e6)
        self.assertTrue(self.report["flag"]["current_lambda4_natural_rescue_still_disfavored"])


if __name__ == "__main__":
    unittest.main()
