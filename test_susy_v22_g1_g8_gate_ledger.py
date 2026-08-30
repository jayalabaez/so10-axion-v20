from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import susy_v22_g1_g8_gate_ledger as ledger


class SusyV22G1G8GateLedgerTests(unittest.TestCase):
    def test_V22_is_active_and_V21_is_not_inherited(self) -> None:
        report = ledger.build_report()
        self.assertEqual(report["n_failed"], 0, report["failures"])
        self.assertEqual(report["active_model"], "SUSY SO(10) x U(1)_X V22")
        self.assertFalse(report["superseded_model_role"]["can_close_V22_gate"])
        self.assertFalse(report["claim_boundary"]["V21_G1_G3_inherited"])

    def test_all_full_gates_remain_honestly_open(self) -> None:
        report = ledger.build_report()
        self.assertEqual(report["closure_counts"], {"closed": 0, "open": 8})
        self.assertEqual([gate["gate"] for gate in report["gates"]], [f"G{i}" for i in range(1, 9)])
        self.assertTrue(all(gate["closed"] is False for gate in report["gates"]))
        self.assertFalse(report["claim_boundary"]["all_V22_full_gates_closed"])

    def test_exact_V22_progress_is_preserved(self) -> None:
        report = ledger.build_report()
        self.assertTrue(report["checks"]["V22_continuous_anomalies_cancel"])
        self.assertTrue(report["checks"]["missing_partner_rank_architecture_is_10_over_1_and_13_over_0"])
        self.assertTrue(report["checks"]["EW_endpoint_is_exactly_174_GeV"])
        self.assertTrue(report["checks"]["local_F_D_flat_slice_has_one_axion_modulus_but_not_globality"])
        self.assertTrue(report["checks"]["G4_scoped_frontier_is_closed_but_full_gate_is_open"])
        self.assertTrue(report["checks"]["G5_one_phase_subproblem_is_closed_but_full_gate_is_open"])

    def test_G1_exact_census_obstruction_is_active(self) -> None:
        report = ledger.build_report()
        self.assertTrue(report["checks"]["degree_le_4_holomorphic_census_proves_catalogue_incomplete"])
        self.assertTrue(report["checks"]["neutral_coefficient_Abelian_shaping_patch_is_exactly_excluded"])
        self.assertEqual(report["gates"][0]["state"], "CONSTRUCTIVE_108_SECTOR_COMPLETION_FOUND__MODEL_ACCEPTANCE_OPEN")
        self.assertFalse(report["claim_boundary"]["current_declared_superpotential_catalogue_complete"])
        self.assertTrue(report["claim_boundary"]["G2_blocked_by_G1_operator_basis"])
        self.assertTrue(report["claim_boundary"]["sparse_29_sector_Abelian_repair_excluded"])
        self.assertTrue(report["claim_boundary"]["no_new_field_108_sector_completion_candidate_exists"])
        self.assertFalse(report["claim_boundary"]["candidate_explicitly_accepted_as_active_model"])
        self.assertFalse(report["claim_boundary"]["full_V22_repair_found"])

    def test_current_SARAH_state_fails_closed(self) -> None:
        report = ledger.build_report()
        self.assertEqual(report["sarah_attestation"]["state"], "NOT_FROZEN")
        self.assertFalse(report["sarah_attestation"]["valid"])
        self.assertFalse(report["gates"][0]["closed"])

    def test_every_required_source_is_raw_hash_pinned(self) -> None:
        report = ledger.build_report()
        self.assertTrue(report["checks"]["all_pinned_V22_sources_match"])
        self.assertEqual(len(report["source_manifest"]), len(ledger.SOURCE_PINS))
        for row in report["source_manifest"]:
            self.assertEqual(row["sha256"], row["expected_sha256"])

    def test_mutated_evidence_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in ledger.SOURCE_PINS:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ledger.ROOT / relative).read_bytes())
            target = root / "SUSY_V22_G5_PHASE_COUNT.json"
            payload = json.loads(target.read_text(encoding="utf-8"))
            payload["status"] = "forged"
            target.write_text(json.dumps(payload), encoding="utf-8")
            report = ledger.build_report(root)
        self.assertEqual(report["status"], "V22_GATE_LEDGER_SOURCE_FAILURE")
        self.assertGreater(report["n_failed"], 0)

    def test_core_hash_covers_semantics(self) -> None:
        report = ledger.build_report()
        changed = copy.deepcopy(report)
        changed["gates"][0]["closed"] = True
        self.assertNotEqual(ledger.core_sha(report), ledger.core_sha(changed))

    def test_rendered_summary_names_the_actual_frontier(self) -> None:
        text = ledger.markdown(ledger.build_report())
        self.assertIn("V22 is the active physics model", text)
        self.assertIn("a no-new-field 108-sector completion now exists", text)
        self.assertIn("1,016 are omitted", text)
        self.assertIn("Smith minimum of 108 sectors", text)
        self.assertIn("No full V22 gate is yet closed", text)


if __name__ == "__main__":
    unittest.main()
