#!/usr/bin/env python3
import json, tempfile, unittest
from pathlib import Path
from unittest import mock
import channel_fcnc_rates_v20 as channel
import na62_pointwise_limit_v20 as na62
import strict_rg_audit_v20 as strict

class StrictRGAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        channel_report=channel.build_report()
        channel.ROOT.joinpath("CHANNEL_FCNC_RATES_V20_VERDICT.json").write_text(json.dumps(channel_report,indent=2)+"\n",encoding="utf-8")
        na62_report=na62.build_report()
        na62.ROOT.joinpath("NA62_POINTWISE_LIMIT_V20_VERDICT.json").write_text(json.dumps(na62_report,indent=2)+"\n",encoding="utf-8")
    def test_current_artifacts_pass_honesty_audit(self):
        r=strict.build_report(); self.assertEqual(r["status"],"PASS"); self.assertEqual(r["n_failed"],0); self.assertEqual(r["classification"]["full_two_loop_so10_210_yukawa_system"],"OPEN"); self.assertEqual(r["classification"]["channel_level_fcnc_formulae"],"IMPLEMENTED"); self.assertEqual(r["classification"]["na62_pointwise_observed_upper_limit"],"IMPLEMENTED"); self.assertEqual(r["classification"]["whole_model_exclusion"],"NOT_ESTABLISHED")
    def _write_minimal_artifacts(self, root:Path, *, matrix_closed:bool=False, whole_model_excluded:bool=False, correlated_likelihood:bool=False):
        (root/"PUSH_PHENOMENOLOGY_LIMITS_V20_VERDICT.json").write_text(json.dumps({"one_loop_matrix_yukawa_rge":{"flag":{"actual_one_loop_matrix_beta_system_solved":matrix_closed}}}))
        (root/"COMMON_SCALE_SO10_YUKAWA_V20_VERDICT.json").write_text(json.dumps({"flag":{}}))
        (root/"TWO_LOOP_SO10_210_V20_VERDICT.json").write_text(json.dumps({"flag":{},"fcnc_limits":{"flag":{}}}))
        (root/"CHANNEL_FCNC_RATES_V20_VERDICT.json").write_text(json.dumps({"flag":{"channel_level_amplitudes_implemented":True,"channel_level_branching_ratios_implemented":True,"left_right_mass_basis_rotations_implemented":True,"component_specific_uv_chiral_currents_derived":False,"finite_model_fcnc_absence_proved":False,"unconditional_model_exclusion_claimed":False}}))
        (root/"NA62_POINTWISE_LIMIT_V20_VERDICT.json").write_text(json.dumps({"flag":{"official_pointwise_observed_limit_ingested":True,"offline_provenance_hash_verified":True,"generation_dependent_portal_point_excluded":True,"whole_v20_model_excluded":whole_model_excluded,"all_portal_parameter_space_excluded":False,"full_correlated_experimental_likelihood_implemented":correlated_likelihood,"component_specific_uv_chiral_currents_derived":False}}))
    def test_rg_overclaim_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); self._write_minimal_artifacts(root,matrix_closed=True)
            with mock.patch.object(strict,"ROOT",root): r=strict.build_report()
            self.assertEqual(r["status"],"FAIL"); self.assertIn("matrix_rge_open",r["failures"])
    def test_whole_model_exclusion_overclaim_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); self._write_minimal_artifacts(root,whole_model_excluded=True)
            with mock.patch.object(strict,"ROOT",root): r=strict.build_report()
            self.assertEqual(r["status"],"FAIL"); self.assertIn("whole_model_not_rejected",r["failures"])
    def test_correlated_likelihood_overclaim_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); self._write_minimal_artifacts(root,correlated_likelihood=True)
            with mock.patch.object(strict,"ROOT",root): r=strict.build_report()
            self.assertEqual(r["status"],"FAIL"); self.assertIn("correlated_likelihood_open",r["failures"])

if __name__=="__main__": unittest.main()
