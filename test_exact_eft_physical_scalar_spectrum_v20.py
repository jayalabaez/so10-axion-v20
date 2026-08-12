from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest

import exact_eft_physical_scalar_spectrum_v20 as spectrum


ROOT = Path(__file__).resolve().parent


class ExactEFTPhysicalScalarSpectrumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = spectrum.build_report()

    def test_frozen_core_and_exact_census(self) -> None:
        report = self.report
        self.assertEqual(report["core_sha256"], spectrum.EXPECTED_CORE_SHA256)
        factor = report["exact_factorization"]
        self.assertEqual(factor["total_algebraic_degree"], 486)
        self.assertEqual(factor["zero_multiplicity"], 38)
        self.assertEqual(factor["positive_massive_multiplicity"], 448)
        self.assertEqual(factor["primitive_factor_count"], 45)
        self.assertEqual(factor["distinct_mass_squared_root_count_including_zero"], 61)
        self.assertTrue(factor["all_nonzero_roots_strictly_positive"])

    def test_exact_provenance_and_mixing(self) -> None:
        provenance = self.report["stabilizer_provenance"]
        self.assertEqual(provenance["casimir12_eigenvalues"], [0, 16, 36, 40])
        self.assertEqual(provenance["charge_squared_eigenvalues"], [0, 1])
        self.assertEqual(
            sum(row["full_real_dimension"] for row in provenance["sector_reports"].values()),
            486,
        )
        self.assertTrue(
            self.report["mixing_classification"][
                "projector_traces_reproduce_every_sector_factor_exponent"
            ]
        )

    def test_physical_axion_is_not_discarded(self) -> None:
        quotient = self.report["physical_quotient"]
        self.assertEqual(quotient["gauged_tangent_dimension"], 37)
        self.assertEqual(quotient["physical_PQ_axion_count"], 1)
        self.assertEqual(quotient["gauge_quotient_dimension"], 449)
        self.assertFalse(quotient["all_38_zero_modes_are_unphysical"])

    def test_scope_is_fail_closed(self) -> None:
        classification = self.report["classification"]
        self.assertTrue(classification["EFT_dimension6_tree_level_mathematical_G6_closed"])
        self.assertFalse(classification["EFT_release_G6_verified"])
        self.assertFalse(classification["renormalizable_authoritative_G6_closed"])
        uncertainty = self.report["uncertainty_scope"]
        self.assertFalse(uncertainty["loop_and_pole_mass_corrections_complete"])
        self.assertFalse(uncertainty["physical_threshold_uncertainties_complete"])

    def test_cli_and_frozen_json(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-B", str(ROOT / spectrum.__file__.split("\\")[-1])],
            cwd=ROOT,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        committed = json.loads(spectrum.OUT_JSON.read_text())
        self.assertEqual(committed, self.report)


if __name__ == "__main__":
    unittest.main()
