#!/usr/bin/env python3
import unittest

import triplet_proxy_contamination_audit_v20 as mod


class TripletProxyContaminationAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_report_executes(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])

    def test_critical_legacy_chain_detected(self):
        expected = set(self.report["critical_expected_modules"])
        detected = set(self.report["critical_detected_modules"])
        contaminated = set(self.report["scan"]["contaminated_modules"])
        self.assertEqual(detected, expected)
        self.assertTrue(expected.issubset(contaminated))
        self.assertGreater(len(contaminated), len(expected))

    def test_canonical_replacements_execute(self):
        replacements = self.report["canonical_replacements"]
        self.assertIn("COMPLETE", replacements["operator_filter"])
        self.assertIn("SIGNED_MT2_PROXY_BUILT", replacements["triplet_mass_squared_proxy"])
        self.assertIn("LAMBDA4_CG_OPEN", replacements["kronecker_audit"])

    def test_physical_legacy_chain_invalidated(self):
        invalidation = self.report["invalidation"]
        flags = self.report["flag"]
        self.assertFalse(invalidation["legacy_triplet_spectra_physical"])
        self.assertFalse(invalidation["legacy_thresholds_physical"])
        self.assertFalse(invalidation["legacy_scalar_proton_lifetimes_unique"])
        self.assertTrue(flags["legacy_triplet_dependency_graph_scanned"])
        self.assertTrue(flags["legacy_physical_triplet_chain_invalidated"])
        self.assertTrue(flags["canonical_signed_mt2_path_available"])
        self.assertFalse(flags["physical_component_CG_complete"])
        self.assertFalse(flags["physical_triplet_spectrum_complete"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
