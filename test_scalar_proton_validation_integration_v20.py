#!/usr/bin/env python3
import json
import tempfile
import unittest
from pathlib import Path

import scalar_vacuum_proton_decay_v20 as scalar_proton
import theory_validation_matrix_v20 as matrix


class ScalarProtonValidationIntegrationTests(unittest.TestCase):
    def test_generated_proton_artifact_is_conditional_not_complete(self):
        _vacuum, proton, _combined = scalar_proton.build_reports()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            root.joinpath("PROTON_DECAY_V20_VERDICT.json").write_text(
                json.dumps(proton), encoding="utf-8"
            )
            gate = matrix._proton_gate({}, root)
        self.assertEqual(gate["state"], "CONDITIONAL")
        self.assertTrue(gate["evidence"]["artifact_present"])
        self.assertFalse(
            proton["flag"]["complete_operator_running_and_hadronic_matching"]
        )
        self.assertFalse(proton["flag"]["model_point_excluded"])
        self.assertTrue(proton["flag"]["conditional_parameter_points_excluded"])

    def test_no_artifact_remains_open(self):
        with tempfile.TemporaryDirectory() as tmp:
            gate = matrix._proton_gate({}, Path(tmp))
        self.assertEqual(gate["state"], "OPEN")
        self.assertFalse(gate["evidence"]["artifact_present"])


if __name__ == "__main__":
    unittest.main()
