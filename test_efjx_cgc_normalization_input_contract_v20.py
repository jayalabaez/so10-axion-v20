#!/usr/bin/env python3
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import efjx_cgc_physical_normalization_gate_v20 as gate


class EFJXNormalizationInputContractTests(unittest.TestCase):
    def test_bare_closure_flags_cannot_close_normalization(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidate.json"
            path.write_text(
                json.dumps({"closure_complete": True, "n_failed": 0}),
                encoding="utf-8",
            )
            with patch.object(gate, "NORMALIZATION_ARTIFACT", path):
                state = gate._load_normalization_artifact()
            self.assertTrue(state["exists"])
            self.assertFalse(state["accepted"])
            self.assertGreater(len(state["missing_fields"]), 0)

    def test_complete_evidence_contract_is_machine_accepted(self):
        data = {
            "schema_version": gate.SCHEMA_VERSION,
            "invariant": "Phi210_H10_Sigmabar126_S",
            "contraction": "Phi_abcd H_e Sigmabar_abcde S with declared factorial normalization",
            "field_normalizations": {
                "Phi210": {},
                "H10": {},
                "Sigmabar126": {},
                "S": {},
            },
            "singlet_vev_projection": {
                "p": 1.0,
                "a": 1.0,
                "omega": 1.0,
                "vS": 1.0,
                "hEW": 174.0,
            },
            "gamma_mapping": {"gamma_eff_over_lambda4": 1.0},
            "source_manifest": [{"source": "A"}, {"source": "B"}],
            "acceptance_evidence": {
                "canonical_kinetic_normalization": "artifact-a",
                "direct_tensor_contraction": "artifact-b",
                "independent_matrix_reconstruction": "artifact-c",
                "physical_EW_branch_reminimized": "artifact-d",
            },
            "closure_complete": True,
            "n_failed": 0,
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidate.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with patch.object(gate, "NORMALIZATION_ARTIFACT", path):
                state = gate._load_normalization_artifact()
            self.assertTrue(state["accepted"], state)
            self.assertEqual(state["gamma_eff_over_lambda4"], 1.0)
            self.assertEqual(len(state["sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
