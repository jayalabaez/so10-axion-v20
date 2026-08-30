from __future__ import annotations

import copy
import json
import unittest

import verify_canonical_g2_full_component_projection_dim6_v21 as verifier


class TrustedCanonicalG2VerifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact = verifier.load(verifier.EXPECTED_ARTIFACT)
        cls.basis = verifier.load("CANONICAL_G2_EXACT_CONTRACTION_BASIS_V21.json")
        cls.g1 = verifier.load("CANONICAL_G1_SUSYNO_CHANNEL_BASIS_V21.json")
        cls.ancestry = verifier.load("EXACT_G6_SM_PROVENANCE_FEASIBILITY_V20.json")
        cls.branch = verifier.load("EXACT_PHYSICAL_G7_COMPONENT_THRESHOLD_CONTRACT_V20.json")

    def test_live_source_manifest_and_exact_proofs_pass(self):
        self.assertTrue(verifier.source_manifest_valid(self.artifact))
        self.assertTrue(all(verifier.basis_audit(self.basis, self.g1).values()))
        self.assertTrue(
            all(
                verifier.projection_audit(
                    self.artifact, self.basis, self.g1, self.ancestry, self.branch
                ).values()
            )
        )

    def test_forged_projection_catalog_is_rejected(self):
        forged = copy.deepcopy(self.artifact)
        forged["projection_catalog"][0]["direction_id"] = "forged"
        forged["proof_summary"]["projection_catalog_sha256"] = verifier.sha(
            forged["projection_catalog"]
        )
        self.assertFalse(
            verifier.projection_audit(
                forged, self.basis, self.g1, self.ancestry, self.branch
            )["catalog"]
        )

    def test_forged_nonsingular_claim_is_rejected(self):
        forged = copy.deepcopy(self.basis)
        row = next(value for value in forged["sectors"] if value["target_multiplicity"] > 1)
        row["minor"][0] = [0] * row["target_multiplicity"]
        row["minor_sha256"] = verifier.sha(row["minor"])
        body = dict(forged)
        body.pop("core_sha256", None)
        forged["core_sha256"] = verifier.sha(body)
        self.assertFalse(verifier.basis_audit(forged, self.g1)["minors"])

    def test_lambda4_or_lock_formula_mutation_is_rejected(self):
        for key in ("lambda4", "dimension_six_lock"):
            forged = copy.deepcopy(self.artifact)
            forged["explicit_required_coefficients"][key]["formula"] += " forged"
            self.assertFalse(
                verifier.projection_audit(
                    forged, self.basis, self.g1, self.ancestry, self.branch
                )["coefficients"]
            )

    def test_wrong_source_pin_is_rejected(self):
        forged = copy.deepcopy(self.artifact)
        forged["source_manifest"][0]["sha256"] = "0" * 64
        self.assertFalse(verifier.source_manifest_valid(forged))


if __name__ == "__main__":
    unittest.main()
