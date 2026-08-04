#!/usr/bin/env python3
import unittest

import so10_cubic_operator_signed_audit_v20 as mod


class SignedCubicOperatorAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_report_executes(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])

    def test_vector_product_forbids_210_coupling(self):
        product = self.report["vector_tensor_product"]
        self.assertEqual(product["dimension_sum"], 100)
        self.assertFalse(product["contains_210"])
        corrections = {row["operator"]: row for row in self.report["corrections"]}
        self.assertEqual(
            corrections["210_H 10_H^dag 10_H"]["signed_floor_multiplicity"],
            0,
        )

    def test_conservative_cubic_subtotal(self):
        counts = self.report["counts"]
        self.assertEqual(counts["historical_subtotal"], 5)
        self.assertEqual(counts["signed_floor_subtotal"], 2)
        self.assertEqual(counts["net_reduction"], 3)

    def test_scope(self):
        flags = self.report["flag"]
        self.assertTrue(flags["forbidden_210_10dag10_proved"])
        self.assertTrue(flags["one_210_cubic_guaranteed"])
        self.assertTrue(flags["one_210_126dag126_guaranteed"])
        self.assertFalse(flags["complete_cubic_multiplicities"])
        self.assertFalse(flags["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
