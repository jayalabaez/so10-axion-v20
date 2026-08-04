#!/usr/bin/env python3
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import efjx_cgc_physical_normalization_gate_v20 as gate


class EFJXNormalizationInputContractTests(unittest.TestCase):
    @staticmethod
    def _write_evidence(base: Path, relative_paths: list[str]) -> dict[str, str]:
        hashes: dict[str, str] = {}
        for rel in relative_paths:
            path = base / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"artifact": rel, "verified": True}), encoding="utf-8")
            hashes[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
        return hashes

    @staticmethod
    def _complete_candidate(base: Path) -> dict:
        artifacts = [
            "evidence/phi210_basis.json",
            "evidence/h10_basis.json",
            "evidence/sigmabar126_basis.json",
            "evidence/s_basis.json",
            "evidence/vev_projection.json",
            "evidence/gamma_mapping.json",
            "evidence/tensor_contraction.json",
            "evidence/E_slot_match.json",
            "evidence/F_slot_match.json",
            "evidence/J_slot_match.json",
            "evidence/X_slot_match.json",
            "evidence/physical_EW_reminimization.json",
        ]
        hashes = EFJXNormalizationInputContractTests._write_evidence(base, artifacts)
        criteria = gate.EVIDENCE_CRITERIA
        return {
            "schema_version": gate.SCHEMA_VERSION,
            "invariant": "Phi210_H10_Sigmabar126_S",
            "contraction": (
                "Phi_abcd H_e Sigmabar_abcde S / (4! 5!) with declared "
                "antisymmetry, epsilon and duality normalization"
            ),
            "field_normalizations": {
                "Phi210": {
                    "kinetic_convention": "Lkin=(1/4!) dPhi* dPhi",
                    "antisymmetry_convention": "unit-weight total antisymmetrization",
                    "state_basis_artifact": "evidence/phi210_basis.json",
                },
                "H10": {
                    "kinetic_convention": "Lkin=dH* dH",
                    "state_basis_artifact": "evidence/h10_basis.json",
                },
                "Sigmabar126": {
                    "kinetic_convention": "Lkin=(1/5!) dSigma* dSigma",
                    "duality_convention": "anti-self-dual with declared i sign",
                    "epsilon_convention": "epsilon_12345678910=+1",
                    "state_basis_artifact": "evidence/sigmabar126_basis.json",
                },
                "S": {
                    "kinetic_convention": "Lkin=dS* dS",
                    "real_or_complex_convention": "complex singlet, unit canonical norm",
                    "state_basis_artifact": "evidence/s_basis.json",
                },
            },
            "singlet_vev_projection": {
                "p": 2.0e16,
                "a": 1.0e16,
                "omega": 5.0e15,
                "vS": 1.0e12,
                "hEW": 174.0,
                "units": "GeV",
                "projection_artifact": "evidence/vev_projection.json",
            },
            "gamma_mapping": {
                "gamma_eff_over_lambda4": -2.0,
                "sign": -1,
                "phase_convention": "all VEVs real; minus sign assigned to gamma",
                "mapping_artifact": "evidence/gamma_mapping.json",
            },
            "source_manifest": [
                {
                    "citation": "Chen, Zhang and Bai, arXiv:1707.00580",
                    "use": "normalized SO(10) states",
                    "locator": "state-normalization tables and appendices",
                },
                {
                    "citation": "Fukuyama et al., arXiv:hep-ph/0405300",
                    "use": "independent G422 Clebsch cross-check",
                    "locator": "component tables",
                },
            ],
            "artifact_hashes": hashes,
            "acceptance_evidence": {
                "canonical_kinetic_normalization": {
                    "criterion": criteria["canonical_kinetic_normalization"],
                    "passed": True,
                    "artifacts": [
                        "evidence/phi210_basis.json",
                        "evidence/h10_basis.json",
                        "evidence/sigmabar126_basis.json",
                        "evidence/s_basis.json",
                    ],
                },
                "direct_tensor_contraction": {
                    "criterion": criteria["direct_tensor_contraction"],
                    "passed": True,
                    "artifacts": ["evidence/tensor_contraction.json"],
                },
                "independent_matrix_reconstruction": {
                    "criterion": criteria["independent_matrix_reconstruction"],
                    "passed": True,
                    "artifacts": [
                        "evidence/E_slot_match.json",
                        "evidence/F_slot_match.json",
                        "evidence/J_slot_match.json",
                        "evidence/X_slot_match.json",
                    ],
                },
                "physical_EW_branch_reminimized": {
                    "criterion": criteria["physical_EW_branch_reminimized"],
                    "passed": True,
                    "artifacts": ["evidence/physical_EW_reminimization.json"],
                },
                "non_goldstone_spectrum_positive": {
                    "criterion": criteria["non_goldstone_spectrum_positive"],
                    "passed": True,
                    "artifacts": ["evidence/physical_EW_reminimization.json"],
                },
            },
            "efjx_slot_match": {
                block: {
                    "max_abs_residual_GeV": 0.0,
                    "tolerance_GeV": 1.0e-6,
                    "passed": True,
                    "artifact": f"evidence/{block}_slot_match.json",
                }
                for block in ("E", "F", "J", "X")
            },
            "physical_EW_reminimization": {
                "hEW_GeV": 174.0,
                "stationarity_residual_GeV3": 0.0,
                "stationarity_tolerance_GeV3": 1.0,
                "gauge_goldstone_count": 33,
                "min_non_goldstone_eigenvalue_GeV2": 1.0,
                "efjx_thresholds_passed": True,
                "competing_extrema_checked": True,
                "boundedness_checked": True,
                "artifact": "evidence/physical_EW_reminimization.json",
            },
            "closure_complete": True,
            "n_failed": 0,
        }

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

    def test_old_truthy_string_contract_is_rejected(self):
        data = {
            "schema_version": gate.SCHEMA_VERSION,
            "invariant": "Phi210_H10_Sigmabar126_S",
            "contraction": "Phi_abcd H_e Sigmabar_abcde S with vague normalization text",
            "field_normalizations": {
                "Phi210": {},
                "H10": {},
                "Sigmabar126": {},
                "S": {},
            },
            "singlet_vev_projection": {
                "p": None,
                "a": None,
                "omega": None,
                "vS": None,
                "hEW": 174.0,
            },
            "gamma_mapping": {"gamma_eff_over_lambda4": 1.0},
            "source_manifest": [{"source": "A"}, {"source": "B"}],
            "acceptance_evidence": {
                key: "artifact-string" for key in gate.EVIDENCE_CRITERIA
            },
            "artifact_hashes": {},
            "efjx_slot_match": {},
            "physical_EW_reminimization": {},
            "closure_complete": True,
            "n_failed": 0,
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidate.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with patch.object(gate, "NORMALIZATION_ARTIFACT", path):
                state = gate._load_normalization_artifact()
            self.assertFalse(state["accepted"])
            self.assertIn("Phi210_kinetic_convention_missing", state["validation_errors"])
            self.assertIn("vev_p_not_finite", state["validation_errors"])
            self.assertIn(
                "canonical_kinetic_normalization_evidence_missing",
                state["validation_errors"],
            )

    def test_complete_hashed_evidence_contract_is_machine_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            data = self._complete_candidate(base)
            path = base / "candidate.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with patch.object(gate, "NORMALIZATION_ARTIFACT", path):
                state = gate._load_normalization_artifact()
            self.assertTrue(state["accepted"], state)
            self.assertEqual(state["gamma_eff_over_lambda4"], -2.0)
            self.assertEqual(len(state["sha256"]), 64)
            self.assertEqual(state["validation_errors"], [])

    def test_tampered_evidence_hash_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            data = self._complete_candidate(base)
            data["artifact_hashes"]["evidence/E_slot_match.json"] = "0" * 64
            path = base / "candidate.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with patch.object(gate, "NORMALIZATION_ARTIFACT", path):
                state = gate._load_normalization_artifact()
            self.assertFalse(state["accepted"])
            self.assertTrue(
                any("E_slot_match_sha256_mismatch" in err for err in state["validation_errors"]),
                state,
            )

    def test_wrong_goldstone_count_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            data = self._complete_candidate(base)
            data["physical_EW_reminimization"]["gauge_goldstone_count"] = 32
            path = base / "candidate.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with patch.object(gate, "NORMALIZATION_ARTIFACT", path):
                state = gate._load_normalization_artifact()
            self.assertFalse(state["accepted"])
            self.assertIn("gauge_goldstone_count_not_33", state["validation_errors"])

    def test_nonpositive_non_goldstone_mass_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            data = self._complete_candidate(base)
            data["physical_EW_reminimization"][
                "min_non_goldstone_eigenvalue_GeV2"
            ] = -1.0
            path = base / "candidate.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with patch.object(gate, "NORMALIZATION_ARTIFACT", path):
                state = gate._load_normalization_artifact()
            self.assertFalse(state["accepted"])
            self.assertIn(
                "non_goldstone_spectrum_not_positive", state["validation_errors"]
            )

    def test_schema_v1_placeholder_is_rejected(self):
        data = {
            "schema_version": "efjx-cgc-normalization-v1",
            "invariant": "Phi210_H10_Sigmabar126_S",
            "contraction": "x" * 50,
            "field_normalizations": {
                "Phi210": {},
                "H10": {},
                "Sigmabar126": {},
                "S": {},
            },
            "singlet_vev_projection": {
                "p": None,
                "a": None,
                "omega": None,
                "vS": None,
                "hEW": 174.0,
            },
            "gamma_mapping": {"gamma_eff_over_lambda4": 1.0},
            "source_manifest": [{"source": "A"}, {"source": "B"}],
            "acceptance_evidence": {
                "canonical_kinetic_normalization": "a",
                "direct_tensor_contraction": "b",
                "independent_matrix_reconstruction": "c",
                "physical_EW_branch_reminimized": "d",
            },
            "closure_complete": True,
            "n_failed": 0,
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidate.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with patch.object(gate, "NORMALIZATION_ARTIFACT", path):
                state = gate._load_normalization_artifact()
            self.assertFalse(state["accepted"])
            self.assertIn("schema_version_mismatch", state["validation_errors"])


if __name__ == "__main__":
    unittest.main()
