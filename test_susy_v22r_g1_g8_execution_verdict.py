from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import susy_v22r_g1_g8_execution_verdict as verdict


class SusyV22RG1G8ExecutionVerdictTests(unittest.TestCase):
    def test_V22R_is_active_and_all_full_gates_remain_open(self) -> None:
        report = verdict.build_report()
        self.assertEqual(report["n_failed"], 0, report["failures"])
        self.assertIn("V22R", report["active_model"])
        self.assertEqual(report["closure_counts"], {"closed": 0, "open": 8})
        self.assertEqual([gate["gate"] for gate in report["gates"]], [f"G{i}" for i in range(1, 9)])
        self.assertTrue(all(gate["closed"] is False for gate in report["gates"]))

    def test_executed_degree_four_source_scope(self) -> None:
        summary = verdict.build_report()["execution_summary"]
        self.assertTrue(summary["source_model_landed"])
        self.assertEqual(summary["base_sectors_landed"], 108)
        self.assertEqual(summary["counted_invariant_components"], 265)
        self.assertEqual(summary["normalized_tensor_realizations_landed"], 0)
        self.assertEqual(summary["first_audited_XMP_spurion_leakage_degree_five_sectors"], 67)

    def test_G2_G3_and_G5_boundaries_are_propagated(self) -> None:
        report = verdict.build_report()
        self.assertIn("ABSTRACT_RANK", report["gates"][1]["state"])
        self.assertIn("REGULAR_INVARIANT_COORDINATE_BRANCH", report["gates"][2]["state"])
        self.assertIn("THREE_MASSLESS_SPECTATORS", report["gates"][4]["state"])
        self.assertEqual(
            report["execution_summary"]["massless_spectator_chiral_multiplets_through_first_audited_XMP_spurion_layer"],
            3,
        )

    def test_terminal_verdict_is_honest(self) -> None:
        terminal = verdict.build_report()["terminal_verdict"]
        self.assertTrue(terminal["degree_four_EFT_is_mathematically_reproducible"])
        self.assertFalse(terminal["complete_G1_G8_solution_exists_in_this_repository"])
        self.assertFalse(terminal["safe_to_claim_a_complete_predictive_theory"])
        self.assertTrue(terminal["stop_current_execution"])

    def test_every_required_source_is_hash_pinned(self) -> None:
        report = verdict.build_report()
        self.assertEqual(len(report["source_manifest"]), len(verdict.SOURCE_PINS))
        self.assertTrue(all(row["matches"] for row in report["source_manifest"]))

    def test_raw_pinned_v22r_chain_is_forced_to_lf(self) -> None:
        attribute_lines = {
            line.strip()
            for line in (verdict.ROOT / ".gitattributes").read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }
        required_lf_rules = {
            "susy_v22r_*.py text eol=lf",
            "test_susy_v22r_*.py text eol=lf",
            "SUSY_V22R_*.json text eol=lf",
            "susy_so10x17_v22r_contract.py text eol=lf",
            "test_susy_so10x17_v22r_contract.py text eol=lf",
            "SUSY_SO10X17_V22R_CONTRACT.json text eol=lf",
            "models/SO10X17SUSYV22R/SO10X17SUSYV22R.m text eol=lf",
        }
        self.assertEqual(required_lf_rules - attribute_lines, set())

    def test_mutated_evidence_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in verdict.SOURCE_PINS:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((verdict.ROOT / relative).read_bytes())
            target = root / "SUSY_V22R_SPECTATOR_MASS_FRONTIER.json"
            payload = json.loads(target.read_text(encoding="utf-8"))
            payload["status"] = "forged"
            target.write_text(json.dumps(payload), encoding="utf-8")
            report = verdict.build_report(root)
        self.assertEqual(report["status"], "V22R_G1_G8_LEDGER_SOURCE_FAILURE")
        self.assertEqual(report["closure_counts"], {"closed": 0, "open": 8})

    def test_core_hash_covers_semantics(self) -> None:
        report = verdict.build_report()
        changed = copy.deepcopy(report)
        changed["terminal_verdict"]["safe_to_claim_a_complete_predictive_theory"] = True
        self.assertNotEqual(verdict.core_sha(report), verdict.core_sha(changed))

    def test_outputs_are_frozen(self) -> None:
        report = verdict.build_report()
        self.assertEqual(json.loads(verdict.OUT_JSON.read_text(encoding="utf-8")), report)
        self.assertEqual(verdict.OUT_MD.read_text(encoding="utf-8"), verdict.markdown(report))


if __name__ == "__main__":
    unittest.main()
