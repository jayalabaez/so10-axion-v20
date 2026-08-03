#!/usr/bin/env python3
import json, tempfile, unittest
from pathlib import Path
from unittest import mock
import strict_rg_audit_v20 as strict

class StrictRGAuditTests(unittest.TestCase):
    def test_current_artifacts_pass_honesty_audit(self):
        r=strict.build_report(); self.assertEqual(r["status"],"PASS"); self.assertEqual(r["n_failed"],0); self.assertEqual(r["classification"]["full_two_loop_so10_210_yukawa_system"],"OPEN")
    def test_overclaim_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/"PUSH_PHENOMENOLOGY_LIMITS_V20_VERDICT.json").write_text(json.dumps({"one_loop_matrix_yukawa_rge":{"flag":{"actual_one_loop_matrix_beta_system_solved":True}}}))
            (root/"COMMON_SCALE_SO10_YUKAWA_V20_VERDICT.json").write_text(json.dumps({"flag":{}}))
            (root/"TWO_LOOP_SO10_210_V20_VERDICT.json").write_text(json.dumps({"flag":{},"fcnc_limits":{"flag":{}}}))
            with mock.patch.object(strict,"ROOT",root): r=strict.build_report()
            self.assertEqual(r["status"],"FAIL"); self.assertIn("matrix_rge_not_overclaimed",r["failures"])

if __name__=="__main__": unittest.main()
