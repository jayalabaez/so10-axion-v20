#!/usr/bin/env python3
import json, tempfile, unittest
from pathlib import Path
from unittest import mock
import strict_rg_audit_v20 as strict

class StrictRGAuditTests(unittest.TestCase):
    def test_current_artifacts_pass_honesty_audit(self):
        r=strict.build_report(); self.assertEqual(r["status"],"PASS"); self.assertEqual(r["n_failed"],0); self.assertEqual(r["classification"]["full_two_loop_so10_210_yukawa_system"],"OPEN"); self.assertEqual(r["classification"]["channel_level_fcnc_formulae"],"IMPLEMENTED"); self.assertEqual(r["classification"]["pointwise_experimental_fcnc_likelihoods"],"OPEN")
    def _write_minimal_artifacts(self, root:Path, *, matrix_closed:bool=False, pointwise_likelihood:bool=False):
        (root/"PUSH_PHENOMENOLOGY_LIMITS_V20_VERDICT.json").write_text(json.dumps({"one_loop_matrix_yukawa_rge":{"flag":{"actual_one_loop_matrix_beta_system_solved":matrix_closed}}}))
        (root/"COMMON_SCALE_SO10_YUKAWA_V20_VERDICT.json").write_text(json.dumps({"flag":{}}))
        (root/"TWO_LOOP_SO10_210_V20_VERDICT.json").write_text(json.dumps({"flag":{},"fcnc_limits":{"flag":{}}}))
        (root/"CHANNEL_FCNC_RATES_V20_VERDICT.json").write_text(json.dumps({"flag":{"channel_level_amplitudes_implemented":True,"channel_level_branching_ratios_implemented":True,"left_right_mass_basis_rotations_implemented":True,"pointwise_experimental_likelihoods_implemented":pointwise_likelihood,"component_specific_uv_chiral_currents_derived":False,"finite_model_fcnc_absence_proved":False,"unconditional_model_exclusion_claimed":False}}))
    def test_rg_overclaim_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); self._write_minimal_artifacts(root,matrix_closed=True)
            with mock.patch.object(strict,"ROOT",root): r=strict.build_report()
            self.assertEqual(r["status"],"FAIL"); self.assertIn("matrix_rge_not_overclaimed",r["failures"])
    def test_pointwise_likelihood_overclaim_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); self._write_minimal_artifacts(root,pointwise_likelihood=True)
            with mock.patch.object(strict,"ROOT",root): r=strict.build_report()
            self.assertEqual(r["status"],"FAIL"); self.assertIn("pointwise_likelihood_not_overclaimed",r["failures"])

if __name__=="__main__": unittest.main()
