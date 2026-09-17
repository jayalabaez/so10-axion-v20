#!/usr/bin/env python3
import json
import math
import unittest

import numpy as np

import flavour_clebsch_fit_v20 as flavour
import flavour_general_yukawa_v21 as general


class RunningValidationTests(unittest.TestCase):
    def test_sm_running_matches_huang_zhou_multiloop_table(self):
        r = general.rg_validation()
        self.assertLess(r["max_abs_quark_deviation"], 0.02)
        self.assertLess(r["max_abs_lepton_deviation"], 0.02)
        self.assertLess(r["max_abs_gauge_deviation"], 0.01)


class V20StructuralAuditTests(unittest.TestCase):
    def setUp(self):
        self.audit = general.v20_release_ansatz_audit()

    def test_v20_up_matrix_is_diagonal_so_ckm_is_identity(self):
        self.assertLess(self.audit["max_relative_offdiagonal_of_predicted_M_u"], 1e-12)
        self.assertEqual(self.audit["predicted_V_CKM"], "identity")

    def test_v20_forces_equal_up_down_mass_ratios(self):
        self.assertLess(self.audit["max_relative_violation_of_mass_ratio_identity"], 1e-9)

    def test_v20_mismatch_metric_sees_only_the_top_entry(self):
        m = self.audit["mismatch_metric_at_tan_beta_20"]
        self.assertAlmostEqual(m["total"], m["top_entry_only"], places=3)

    def test_v20_global_ckm_pulls_pass_while_model_predicts_no_mixing(self):
        self.assertLess(self.audit["global_flavour_fit_v20_ckm_pull_chi2_at_nuisance_match"], 1e-9)
        self.assertLess(max(self.audit["model_ckm_at_same_point"].values()), 1e-12)


class GeneralModelTests(unittest.TestCase):
    def test_degenerate_limit_reproduces_v20_up_matrix(self):
        st = general.Stratum(10.0, general.BENCHMARK_VR)
        p = np.random.default_rng(7).normal(size=17)
        p[10] = p[9]
        p[11] = 0.0
        b = st.build(p)
        self.assertLess(np.linalg.norm(b["mu"] - b["rH"] * b["md"]), 1e-12)

    def test_inverted_ordering_extraction_round_trip(self):
        m3 = 0.004
        m2 = math.sqrt(m3 ** 2 + 2.484e-3)
        m1 = math.sqrt(m2 ** 2 - 7.49e-5)
        u = flavour._rotation(math.sqrt(0.308), math.sqrt(0.550), math.sqrt(0.02231), math.radians(274.0))
        mnu = (u @ np.diag([m1, m2, m3]) @ u.T * 1e-9).astype(complex)
        lep = general.pmns_inverted(mnu, np.diag([1e-3, 0.1, 1.7]).astype(complex))
        self.assertAlmostEqual(lep["sin2_th23"], 0.550, places=9)
        self.assertAlmostEqual(lep["dm31_eV2"], -2.484e-3, places=12)
        self.assertAlmostEqual(lep["delta_cp_deg"], 274.0, places=6)


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = general.build_report()

    def test_all_checks_pass(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])

    def test_benchmark_witnesses_fit_with_sum_rules_and_no_penalty(self):
        rows = [w for w in self.report["witnesses"]["benchmark"]
                if abs(w["v_R"] - general.BENCHMARK_VR) / general.BENCHMARK_VR < 1e-6]
        good = [w for w in rows if w["chi2_fermion"] < 0.05 and w["penalty"] < 1e-6]
        self.assertGreaterEqual(len(good), 3)
        self.assertTrue(all(w["sum_rule_margin"] >= 0 for w in good))
        self.assertTrue(any(w["config"].get("y_max") == 1.0 for w in good))
        self.assertTrue(any(w["config"].get("floor") == 0.0 for w in good))

    def test_high_seesaw_scale_breaks_the_doublet_sum_rule(self):
        self.assertLess(self.report["witnesses"]["high_vR"]["sum_rule_margin"], 0.0)

    def test_sum_mnu_window_is_bounded_on_both_sides(self):
        pred = self.report["predictions"]
        lo, hi = pred["sum_mnu_window_eV"]
        self.assertLess(pred["sum_mnu_excluded_below_eV"], lo)
        self.assertGreater(pred["sum_mnu_excluded_above_eV"], hi)
        self.assertLess(hi, general.DESI_SUM_MNU)
        self.assertLess(pred["m_bb_eV_range"][1], 1e-3)

    def test_inverted_ordering_fails_real_data(self):
        self.assertGreater(self.report["predictions"]["inverted_ordering_best_chi2_fermion"], 100.0)

    def test_normal_ordering_required_with_closure_backed_confidence(self):
        pred = self.report["predictions"]
        self.assertTrue(pred["normal_ordering_required"])
        self.assertGreaterEqual(len(pred["inverted_ordering_tan_beta_strata"]), 3)
        self.assertGreaterEqual(pred["inverted_ordering_closure_success_rate"], 0.02)
        self.assertLess(pred["inverted_ordering_miss_probability_worst_stratum"], 0.01)
        self.assertLess(pred["inverted_ordering_miss_probability_all_strata"], 1e-6)

    def test_claim_boundary_is_fail_closed(self):
        flag = self.report["flag"]
        self.assertFalse(flag["v20_flavour_witness_valid"])
        self.assertTrue(flag["v20_release_ansatz_predicts_identity_ckm"])
        self.assertFalse(flag["unique_fit"])
        self.assertFalse(flag["global_minimum_proved"])
        self.assertFalse(flag["whole_model_validated"])
        self.assertFalse(flag["two_loop_thresholds_coupled"])
        self.assertFalse(flag["right_handed_neutrino_thresholds_included_in_frozen_witnesses"])
        self.assertTrue(flag["right_handed_neutrino_thresholds_applied_in_stability_study"])


class FineTuningAndThresholdTests(unittest.TestCase):
    """The fit works only through a large cancellation; the prediction survives anyway."""

    @classmethod
    def setUpClass(cls):
        cls.report = general.build_report()

    def test_fine_tuning_is_computed_live_and_is_large(self):
        st = general.Stratum(10.0, general.BENCHMARK_VR, y_max=1.0)
        entry = [w for w in json.loads(general.WITNESSES.read_text(encoding="utf-8"))["benchmark_fits"]
                 if w["label"] == "Ymax=1" and w["tan_beta"] == 10.0][0]
        tune, masses = general.fine_tuning(st, np.asarray(entry["x"]))
        self.assertGreater(tune, 20.0)
        self.assertEqual(len(masses), 3)

    def test_no_acceptable_fit_without_the_cancellation(self):
        capped = self.report["fine_tuning"]["best_chi2_fermion_when_cancellation_is_capped"]
        self.assertTrue(capped)
        self.assertGreater(min(capped.values()), 100.0)

    def test_sum_mnu_window_survives_right_handed_neutrino_thresholds(self):
        pred = self.report["predictions"]
        lo, hi = pred["sum_mnu_window_eV_threshold_aware"]
        self.assertGreater(lo, 0.060)
        self.assertLess(hi, 0.076)
        self.assertTrue(self.report["flag"]["sum_mnu_prediction_survives_thresholds"])
        self.assertTrue(self.report["flag"]["right_handed_neutrino_threshold_stability_checked"])

    def test_threshold_code_was_validated_against_the_baseline(self):
        v = self.report["threshold_study"]["validation"]
        self.assertLess(v["reduces_to_baseline_when_all_N_integrated_out_at_M_I"], 1e-5)
        self.assertLess(v["null_test_zero_effect_when_type_I_part_forced_to_run_like_kappa"], 1e-6)

    def test_inverted_ordering_fails_with_thresholds_too(self):
        io = self.report["threshold_study"]["inverted_ordering_refits"]
        self.assertGreaterEqual(len(io), 3)
        self.assertGreater(min(d["chi2_fermion"] for d in io), 100.0)


class DownstreamContaminationTests(unittest.TestCase):
    """The v20 witness still feeds tan(beta) and a quark-mixing basis downstream."""

    @classmethod
    def setUpClass(cls):
        cls.c = general.v20_downstream_contamination()

    def test_downstream_basis_uses_the_nuisance_rotation_not_the_prediction(self):
        self.assertLess(max(self.c["model_predicted_quark_mixing"].values()), 1e-12)
        self.assertGreater(self.c["downstream_quark_mixing"]["V_us"], 1e-3)

    def test_downstream_mixing_matches_neither_prediction_nor_data(self):
        down = self.c["downstream_quark_mixing"]["V_us"]
        self.assertGreater(abs(down - self.c["measured_quark_mixing"]["V_us"]), 0.05)

    def test_consumers_are_listed_for_recomputation(self):
        self.assertIn("yukawa_rge_2loop_v20.py", self.c["consumers"])
        self.assertIn("channel_fcnc_rates_v20.py", self.c["consumers"])
        self.assertGreaterEqual(len(self.c["consumers"]), 5)

    def test_tan_beta_is_not_fixed_by_the_fermion_data(self):
        report = general.build_report()
        self.assertFalse(report["flag"]["tan_beta_fixed_by_fermion_data"])
        self.assertTrue(report["checks"]["tan_beta_not_determined_by_fermion_data"])


class ValidationMatrixFlavourGateTests(unittest.TestCase):
    """The matrix must never credit the v20 proxy with a viable flavour fit."""

    @staticmethod
    def _gate(reports):
        import theory_validation_matrix_v20 as matrix
        return matrix._flavour_gate(reports)

    @staticmethod
    def _legacy():
        return {"best_point": {"chi2": 4.95, "viable_chi2_lt_30": True}, "any_viable": True}

    def test_legacy_proxy_alone_is_open_not_viable(self):
        gate = self._gate({"global_flavour": self._legacy()})
        self.assertEqual(gate["state"], "OPEN")
        self.assertFalse(gate["evidence"]["general_v21_witness_viable"])
        self.assertFalse(gate["evidence"]["v20_proxy_valid"])

    def test_viable_general_sector_is_conditional_while_thresholds_are_open(self):
        report = general.build_report()
        gate = self._gate({"global_flavour": self._legacy(), "general_flavour": report})
        self.assertEqual(gate["state"], "CONDITIONAL")
        self.assertTrue(gate["evidence"]["general_v21_witness_viable"])
        self.assertTrue(gate["evidence"]["v20_proxy_predicts_identity_ckm"])
        self.assertTrue(gate["evidence"]["normal_ordering_required"])

    def test_failing_general_report_fails_the_gate(self):
        broken = {"n_failed": 1, "flag": {
            "general_yukawa_sector_fits_all_fermion_observables_at_benchmark": False,
            "ckm_is_a_model_prediction_not_a_nuisance": True}}
        self.assertEqual(self._gate({"general_flavour": broken})["state"], "FAIL")


if __name__ == "__main__":
    unittest.main()
