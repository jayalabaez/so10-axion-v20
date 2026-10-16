#!/usr/bin/env python3
"""Tests for the status-neutral perturbative-unitarity record of the G3 SM Pati-Salam witness (v20).

setUpClass builds one fresh report (numerical=False, about 20 s: the exact binding units, the per-term and member
Hessians and the sympy lemmas) and compares it with the committed artifact: exact leaves exactly, float (NUM) leaves
within the relative tolerance of g3_candidate_physical_target_audit_v20.report_mismatches; the FLOAT64 compiler
corroboration is checked on the committed artifact only.  The fail-closed mutations are the seven of the spec (a
T_Phi-only member claimed perturbative, an O48-only scaling claimed SOS-preserving, s = 1/40, alpha_Phi -> 1000,
n_Sigma = 126, O07 classified as quartic, the check count); each makes its named check False and main --write
refuses the mutated report.
"""
from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import unittest
from fractions import Fraction
from pathlib import Path
from typing import Any
from unittest import mock

import g3_candidate_physical_target_audit_v20 as target
import g3_sm_pati_salam_exact_hessian_v20 as hessian
import g3_sm_pati_salam_witness_unitarity_v20 as unitarity

FLOAT_KEYS = ("runtime_seconds", "float_evidence", "float_verdict")
FLOAT_FLAGS = ("float_evidence_run", "float_evidence_consistent")
GATE_FILES = (
    "G1_G8_GATE_LEDGER_V20.json",
    "LIVE_G1_G8_GATE_LEDGER_V20.json",
    "FINAL_G3_ACCEPTANCE_GATE_V20.json",
    "G1_G8_EXECUTION_ROADMAP_V20.json",
    "G3_SM_PATI_SALAM_GATE_READINESS_V20.json",
    "G4_SM_PATI_SALAM_PHYSICAL_QUOTIENT_V20.json",
    "g1_g8_gate_ledger_v20.py",
    "final_g3_acceptance_gate_v20.py",
)
EXPECTED_GATES = {"G1": "CLOSED", "G2": "CLOSED", "G3": "CLOSED", "G4": "CLOSED", "G5": "CLOSED", "G6": "OPEN", "G7": "BLOCKED", "G8": "BLOCKED"}
EXPECTED_RESEARCH_SHA = {
    "wfRESCUE/D-G6-certification/s03_unitarity.py": "1abb418aef9e32a5dc099c4db518af71a54073504adec02dfb3cfa81ecb0196a",
    "wfRESCUE/D-G6-certification/s03_unitarity.json": "3e0d46fdf37a49482ba0dcc7204cddac822a35709088d9e0047643c6d49e31ed",
    "wfRESCUE/D-G6-certification/VERIFY_physics.md": "7a979d737afaa8d75a2a0538f31e3ef45dd18b1b4982e1a78c1cd8ed49503242",
}


def strip(report: dict[str, Any]) -> dict[str, Any]:
    output = {key: value for key, value in report.items() if key not in FLOAT_KEYS}
    output["flags"] = {key: value for key, value in report["flags"].items() if key not in FLOAT_FLAGS}
    return output


def mutated(**keywords: Any) -> dict[str, Any]:
    return unitarity.json_roundtrip(unitarity.build_report(numerical=False, **keywords))


def F(text: str) -> Fraction:
    return Fraction(text)


class WitnessUnitarityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.committed = json.loads(unitarity.OUT_JSON.read_text(encoding="utf-8"))
        cls.fresh = unitarity.json_roundtrip(unitarity.build_report(numerical=False))

    def assertFailsClosed(self, report: dict[str, Any], *expected: str) -> None:
        self.assertEqual(report["status"], unitarity.STATUS_INCOMPLETE)
        self.assertEqual(report["overall_state"], unitarity.OVERALL_STATE_OPEN)
        self.assertGreater(report["n_failed"], 0)
        self.assertIs(report["record_claimed"], False)
        self.assertTrue(report["theorem"].startswith("NOT CLAIMED"))
        self.assertTrue(report["verdict"].startswith("FAIL-CLOSED"))
        self.assertIs(report["G3_witness_unchanged"], True)
        for name in unitarity.NEVER_TRUE_FLAGS:
            self.assertIs(report["flags"][name], False, name)
        for name in expected:
            self.assertIn(name, report["failures"])
            if name != unitarity.CHECK_COUNT_FAILURE:
                self.assertIs(report["checks"][name], False, name)
        self.assertFalse(unitarity.report_passes(report))
        self.assertMainRefuses(report)

    def assertMainRefuses(self, report: dict[str, Any]) -> None:
        with mock.patch.object(unitarity, "build_report", return_value=report), mock.patch.object(
            unitarity, "write_report"
        ) as writer, mock.patch("builtins.print"):
            self.assertEqual(unitarity.main(["--write"]), 1)
            writer.assert_not_called()

    # -- committed and fresh reports ------------------------------------------------------------------------------

    def test_status_checks_and_flags(self) -> None:
        for report in (self.committed, self.fresh):
            self.assertEqual(report["module"], unitarity.MODULE)
            self.assertEqual(report["model_contract_id"], unitarity.MODEL_CONTRACT_ID)
            self.assertEqual(report["status"], unitarity.STATUS_CERTIFIED)
            self.assertEqual(
                report["status"],
                "SM_PATI_SALAM_WITNESS_UNITARITY__COMMITTED_NONPERTURBATIVE__RESCALED_MEMBER_SINGLET_CHANNEL_PERTURBATIVE_EXACT"
                "__STATUS_NEUTRAL",
            )
            self.assertEqual(report["overall_state"], unitarity.OVERALL_STATE_CERTIFIED)
            self.assertEqual(report["n_failed"], 0, report["failures"])
            self.assertEqual(report["n_checks"], unitarity.EXPECTED_N_CHECKS)
            self.assertEqual(unitarity.EXPECTED_N_CHECKS, 57)
            self.assertEqual(len(report["checks"]), unitarity.EXPECTED_N_CHECKS)
            self.assertTrue(all(report["checks"].values()))
            self.assertIs(report["record_claimed"], True)
            self.assertEqual(report["theorem"], unitarity.THEOREM)
            self.assertIs(report["G3_witness_unchanged"], True)
            self.assertEqual(
                set(unitarity.NEVER_TRUE_FLAGS),
                {
                    "gate_status_changed",
                    "G3_witness_replaced",
                    "wired_into_gate_ledger",
                    "non_singlet_channels_computed",
                    "thresholds_recomputed",
                    "benchmark_chosen",
                    "report_closes_g3_by_itself",
                    "report_closes_g6_by_itself",
                },
            )
            for name in unitarity.NEVER_TRUE_FLAGS:
                self.assertIs(report["flags"][name], False, name)
            for name in (
                "record_claimed",
                "committed_witness_singlet_channel_nonperturbative",
                "overall_one_fiftieth_member_perturbative_in_computed_channel",
                "rescaling_lemma_whole_sos_terms_exact",
                "phi_block_only_rescaling_insufficient",
                "s_max_bracketed_1_over_44_to_1_over_43",
            ):
                self.assertIs(report["flags"][name], True, name)
            self.assertEqual(set(report["check_labels"]), set(report["checks"]))
            self.assertEqual(
                {label for label in report["check_labels"].values()}, {"EXACT", "NUM", "RESEARCH_RECORD consistency"}
            )
        self.assertTrue(unitarity.report_passes(self.committed))
        self.assertIs(self.fresh["flags"]["float_evidence_run"], False)
        self.assertIs(self.committed["flags"]["float_evidence_run"], True)
        self.assertIs(self.committed["flags"]["float_evidence_consistent"], True)

    def test_fresh_equals_committed(self) -> None:
        self.assertEqual(target.report_mismatches(strip(self.committed), strip(self.fresh)), [])

    def test_committed_witness_exact_values(self) -> None:
        witness = self.fresh["witness"]
        self.assertEqual(witness["alpha"], {"Phi": "1084", "H": "44", "Sigma": "16645/448", "S": "4", "Phi17": "1/8"})
        self.assertEqual(witness["beta"], {"Phi|Sigma": "205/4", "Sigma|Phi": "123/2", "H|Phi": "12", "Phi|H": "126"})
        self.assertEqual(witness["beta_measured_at_q0"], {"Phi|Sigma": "205/4", "Sigma|Phi": "123/2", "H|Phi": "12"})
        self.assertEqual(witness["phi_sigma_consistency"], {"n_Sigma_beta_Phi_Sigma": "12915", "n_Phi_beta_Sigma_Phi": "12915"})
        self.assertEqual(
            witness["minus_4_Ninv_E"],
            [
                ["-1084", "-12", "-123/2", "0", "0"],
                ["-126", "-44", "0", "0", "0"],
                ["-205/4", "0", "-16645/448", "0", "0"],
                ["0", "0", "0", "-4", "0"],
                ["0", "0", "0", "0", "-1/8"],
            ],
        )
        self.assertEqual(witness["characteristic_polynomial"]["cubic_Phi_H_Sigma"], unitarity.EXPECTED_CUBIC)
        self.assertEqual(witness["characteristic_polynomial"]["decoupled_roots"], {"S": "-4", "Phi17": "-1/8"})
        low, high = (F(value) for value in witness["max_abs_eigenvalue_interval"])
        self.assertLess(high - low, Fraction(1, 10**9) + Fraction(1, 10**12))
        self.assertLess(Fraction(10884457, 10**4), low)
        self.assertLess(high, Fraction(10884458, 10**4))
        a0_low, a0_high = (F(value) for value in witness["a0_max_exact_enclosure"])
        self.assertLess(Fraction(21), a0_low)
        self.assertLess(a0_high, Fraction(22))
        self.assertLess(a0_low, a0_high)
        self.assertEqual(witness["mixing_entries_squared"], {"Phi-Sigma": "25215/8", "Phi-H": "1512"})
        # 16 pi a0 values: every self entry of Phi, H, Sigma exceeds 8 pi, S and Phi17 do not.
        self.assertAlmostEqual(witness["a0_max_float"], 21.6539402771, delta=1.0e-8)
        self.assertAlmostEqual(witness["per_block_self_a0"]["Phi"], 21.565494789, delta=1.0e-8)
        self.assertAlmostEqual(witness["per_block_self_a0"]["H"], 0.875352187005, delta=1.0e-10)
        self.assertAlmostEqual(witness["per_block_self_a0"]["Sigma"], 0.739155699711, delta=1.0e-10)
        self.assertAlmostEqual(witness["per_block_self_a0"]["S"], 0.0795774715459, delta=1.0e-11)
        self.assertAlmostEqual(witness["per_block_self_a0"]["Phi17"], 0.00248679598581, delta=1.0e-12)
        for got, expected in zip(sorted(witness["eigenvalues_float"]), (-1088.44575513, -43.0408352699, -33.6674274524, -4.0, -0.125)):
            self.assertAlmostEqual(got, expected, delta=1.0e-7)
        method = self.fresh["method"]
        self.assertEqual(method["H_self_quartic"]["alpha_by_channel"], {"I_1": "2/5", "I_54": "108/5", "N_H^2": "22"})
        self.assertIs(method["H_self_quartic"]["identity_I1_plus_I54_equals_NH_squared"], True)
        self.assertEqual(method["lee_quigg_thacker_calibration"]["a0"], "3*lambda/(8*pi)")
        self.assertEqual(method["V0_from_Euler_values"], "-20661/20000")
        self.assertEqual(
            {name: row["vev_chart_norm_squared"] for name, row in method["blocks"].items()},
            {"Phi": "1", "H": "0", "Sigma": "2/25", "S": "2/25", "Phi17": "2"},
        )
        classification = method["unit_classification"]
        self.assertEqual(set(classification), set(unitarity.UNIT_TABLE))
        zero_gradient = {name for name, row in classification.items() if not row["gradient_nonzero"]}
        self.assertEqual(
            zero_gradient,
            {
                "O27 I_54",
                "O27 I_1050bar",
                "O27 I_4125",
                "O06 N_H",
                "re::O12 2 Re[conj(H.H) conj(S)]",
                "O36 I_1(H) (quartic in H)",
                "O36 I_54(H) (quartic in H)",
                "O46 (3/5) I_1 - I_54 = H^dag(|Phi|^2 - C(Phi))H",
            },
        )
        self.assertEqual(classification["O27 I_54"]["vev_scaling_exponent"], 2)
        self.assertEqual(classification["re::O12 2 Re[conj(H.H) conj(S)]"]["vev_scaling_exponent"], 1)
        self.assertEqual(classification["O46 (3/5) I_1 - I_54 = H^dag(|Phi|^2 - C(Phi))H"]["vev_scaling_exponent"], 0)

    def test_rescaling_lemma_values(self) -> None:
        lemma = self.fresh["rescaling_lemma"]
        self.assertEqual(set(lemma["terms"]), set(unitarity.TERM_NAMES))
        self.assertIs(lemma["symbolic_partition_residuals_zero"], True)
        self.assertEqual(lemma["parameters_compared"], 27)
        self.assertEqual(lemma["linear_identity_residual"], "0")
        self.assertEqual(lemma["V0_at_s_equal_1_residual"], "0")
        self.assertIs(lemma["kappa_margin"]["scale_invariant"], True)
        groups = lemma["unit_computable_groups"]
        self.assertEqual(set(groups), {"T_Phi", "A_square+C_square", "W", "T_HS", "T_HPhi", "T_X"})
        expected_values = {"T_Phi": "-1", "A_square+C_square": "0", "W": "-1/5000", "T_HS": "-1/625", "T_HPhi": "0", "T_X": "-1/32"}
        for name, row in groups.items():
            self.assertIs(row["gradient_exactly_zero_at_q0"], True, name)
            self.assertEqual(row["hessian_inertia_positive_negative_zero"][1], 0, name)
            self.assertEqual(row["value_at_q0"], expected_values[name], name)
        self.assertEqual(groups["T_HS"]["hessian_inertia_positive_negative_zero"], [11, 0, 475])
        self.assertEqual(groups["T_HPhi"]["hessian_inertia_positive_negative_zero"], [12, 0, 474])
        self.assertIn("-49/3125", lemma["proper_subset_counterexamples"]["O27_only_x1/50"])
        blockwise = self.fresh["blockwise_test_member"]
        self.assertEqual(blockwise["certificate_benchmark"]["inertia_positive_zero_negative"], "447/39/0")
        self.assertIs(blockwise["certificate_benchmark"]["kernel_equals_expected_span"], True)
        self.assertAlmostEqual(blockwise["a0_max_float"], 0.461413199946, delta=1.0e-9)

    def test_perturbative_member_values(self) -> None:
        member = self.fresh["perturbative_member"]
        self.assertEqual(member["common_scale"], "1/50")
        self.assertIs(member["hessian"]["numerators_identical_to_witness"], True)
        self.assertEqual(member["hessian"]["witness_denominator"], 2016000)
        self.assertEqual(member["hessian"]["denominator"], 100800000)
        self.assertEqual(member["certificate_benchmark"]["inertia_positive_zero_negative"], "447/39/0")
        self.assertEqual(member["certificate_raised_O06"]["inertia_positive_zero_negative"], "451/35/0")
        self.assertEqual(member["certificate_benchmark"]["kernel_spanning_set"], "35 symmetry tangents + 4 real light-doublet directions")
        self.assertEqual(member["certificate_raised_O06"]["kernel_spanning_set"], "35 symmetry tangents")
        self.assertEqual(member["certificate_benchmark"]["O06"], "1/2500")
        self.assertEqual(member["certificate_raised_O06"]["O06"], "1/1250")
        self.assertEqual(member["certificate_raised_O06"]["O06_offset"], "1/2500")
        # The certificate's own gap flag assumes the committed normalisation; the module re-checks it.
        self.assertIs(member["certificate_benchmark"]["certificate_gap_flag"], False)
        self.assertEqual(member["gap_recheck"]["lambda"], "1/120000")
        self.assertEqual(member["gap_recheck"]["lambda_over_r0_squared"], "1/4800")
        self.assertEqual(member["gap_recheck"]["benchmark_negative_zero_positive"], [39, 14, 433])
        self.assertEqual(member["gap_recheck"]["raised_O06_negative_zero_positive"], [35, 14, 437])
        self.assertEqual(member["V0"], "-20661/1000000")
        self.assertEqual(member["lambda_eff"], "127/3200")
        self.assertEqual(member["alpha"], {"Phi": "542/25", "H": "22/25", "Sigma": "3329/4480", "S": "2/25", "Phi17": "1/400"})
        self.assertAlmostEqual(member["a0_max_float"], 0.433078805543, delta=1.0e-10)
        negative = self.fresh["negative_results"]
        self.assertEqual(negative["s_max"]["bracket"], ["1/44", "1/43"])
        self.assertAlmostEqual(negative["s_max"]["a0_at_bracket_float"][0], 0.492135006299, delta=1.0e-10)
        self.assertAlmostEqual(negative["s_max"]["a0_at_bracket_float"][1], 0.503580006445, delta=1.0e-10)
        self.assertAlmostEqual(negative["overall_1_over_40"]["a0_max_float"], 0.541348506928, delta=1.0e-10)
        self.assertAlmostEqual(negative["T_Phi_only_1_over_50"]["a0_max_float"], 1.97929795251, delta=1.0e-9)
        changes = self.fresh["what_changes"]
        self.assertEqual(changes["lambda_eff"], {"witness": "127/64", "member": "127/3200"})
        self.assertEqual(changes["eps_windows"]["witness_perturbative_box"], "599/50")
        self.assertEqual(changes["eps_windows"]["member_perturbative_box"], "29999/2500")
        self.assertEqual(changes["eps_windows"]["member_doublet_is_lightest_for_eps_below"], "1/120000")
        self.assertAlmostEqual(changes["masses_factor_float"], 0.141421356237, delta=1.0e-12)
        committed = self.fresh["committed_artifacts"]["fresh_witness_certificates_vs_committed"]
        for variant in ("benchmark", "raised_O06"):
            for name, (left, right) in committed[variant].items():
                self.assertEqual(left, right, (variant, name))

    def test_research_record_provenance(self) -> None:
        research = self.fresh["research_record"]
        self.assertEqual(research["kind"], "RESEARCH_RECORD")
        self.assertEqual(research["provenance_note"], unitarity.RESEARCH_PROVENANCE_NOTE)
        self.assertEqual(research["problems"], [])
        self.assertEqual(research["research_files_digest"], unitarity.RESEARCH_FILES_DIGEST)
        for name, sha in EXPECTED_RESEARCH_SHA.items():
            self.assertEqual(research["research_files"][name]["sha256"], sha, name)
        for name, entry in research["entries"].items():
            self.assertIs(entry["reproducible_from_repository"], False, name)
            self.assertEqual(entry["label"], "RESEARCH_RECORD", name)
        self.assertLess(research["consistency"]["max_abs_deviation_in_sigma_units"], 3.0)
        self.assertAlmostEqual(research["entries"]["mc_a0_max"]["value"], 21.650366748967063, delta=1.0e-9)
        self.assertEqual(research["entries"]["synthesis_pr4_rescale_line"]["value"], "Rescale the 210 block by 0.02 or less.")
        # The module never reads scratch research paths at runtime.
        source = Path(unitarity.__file__).read_text(encoding="utf-8")
        for fragment in ("AppData", "scratchpad", "wfREC", "Temp"):
            self.assertNotIn(fragment, source, fragment)

    def test_committed_float_evidence(self) -> None:
        evidence = self.committed["float_evidence"]
        self.assertIs(evidence["run"], True)
        self.assertIn("FLOAT64", evidence["label"])
        self.assertEqual(evidence["n_checks"], unitarity.EXPECTED_N_FLOAT_CHECKS)
        self.assertEqual(evidence["n_failed"], 0, evidence["failures"])
        self.assertEqual(sorted(evidence["checks"]), sorted(unitarity.FLOAT_CHECK_NAMES))
        self.assertLessEqual(evidence["F1_max_abs_deviation"], unitarity.FLOAT_TOLERANCE)
        self.assertAlmostEqual(evidence["F2_Q_at_p"], 1.0, delta=unitarity.FLOAT_TOLERANCE)
        self.assertAlmostEqual(evidence["F2_T_Phi_at_p"], -1.0, delta=unitarity.FLOAT_TOLERANCE)
        self.assertEqual(self.fresh["float_evidence"]["run"], False)

    def test_markdown_and_scope(self) -> None:
        markdown = unitarity.OUT_MD.read_text(encoding="utf-8")
        self.assertIn(f"`{unitarity.STATUS_CERTIFIED}`", markdown)
        self.assertIn(f"Checks: {unitarity.EXPECTED_N_CHECKS}/{unitarity.EXPECTED_N_CHECKS} passed.", markdown)
        self.assertIn("FLOAT64", markdown)
        self.assertIn("Rescale the 210 block by 0.02 or less", json.dumps(self.fresh["research_record"]))
        self.assertIn("| `H\\|Phi` | `12` |", markdown)
        scope = self.fresh["scope"]
        self.assertTrue(any("non-singlet two-particle channels are not computed" in row for row in scope["not_claimed"]))
        self.assertTrue(any("D12 GUT thresholds" in row for row in scope["not_claimed"]))
        self.assertTrue(any("committed witness remains the G3 closing instance" in row for row in scope["not_claimed"]))
        self.assertIn("status-neutral", scope["status_neutrality"])
        # Only the singlet channel is computed: the labels say so, and nothing claims a non-singlet recomputation.
        self.assertIn("SINGLET_CHANNEL_PERTURBATIVE", unitarity.STATUS_CERTIFIED)
        self.assertIn("non-singlet channels are not computed and the D12 thresholds are not recomputed", self.fresh["verdict"])
        self.assertNotIn("non-singlet channels and the D12 thresholds are not recomputed", self.fresh["verdict"])
        self.assertIn("need not keep it", unitarity.__doc__)
        self.assertNotIn("parameters does not: O48 alone", unitarity.__doc__)

    def test_no_gate_wiring(self) -> None:
        for name in GATE_FILES:
            path = unitarity.ROOT / name
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            self.assertNotIn(unitarity.MODULE, text, name)
            self.assertNotIn(unitarity.OUT_JSON.name, text, name)
        ledger = json.loads((unitarity.ROOT / "G1_G8_GATE_LEDGER_V20.json").read_text(encoding="utf-8"))
        self.assertEqual({gate: ledger["gates"][gate]["status"] for gate in ledger["gates"]}, EXPECTED_GATES)

    def test_import_has_no_side_effects(self) -> None:
        before = {path: path.stat().st_mtime_ns for path in (unitarity.OUT_JSON, unitarity.OUT_MD)}
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        completed = subprocess.run(
            [sys.executable, "-B", "-c", "import g3_sm_pati_salam_witness_unitarity_v20"],
            cwd=str(unitarity.ROOT),
            env=environment,
            capture_output=True,
            text=True,
            timeout=300,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout, "")
        self.assertEqual({path: path.stat().st_mtime_ns for path in before}, before)

    # -- fail-closed mutations (spec M4) --------------------------------------------------------------------------

    def test_mutation_T_Phi_only_member_claimed_perturbative(self) -> None:
        report = mutated(member_scales=dict(unitarity.PHI_ONLY_SCALES))
        self.assertFailsClosed(report, "member_a0_below_half_exact", "member_is_whole_term_scaling_with_positive_factors")
        # A whole-term scaling keeps the certificate: the failure is perturbativity, not the SOS structure.
        self.assertIs(report["checks"]["member_benchmark_inertia_447_39_0_kernel_T35_plus_doublets"], True)
        self.assertGreater(report["perturbative_member"]["a0_max_float"], 1.9)

    def test_mutation_O48_only_scaling_claimed_sos_preserving(self) -> None:
        terms = unitarity.sos_terms()
        split = {"T_Phi_O07": {unitarity.O07_ID: terms["T_Phi"][unitarity.O07_ID]}}
        split["T_Phi_O48"] = {key: value for key, value in terms["T_Phi"].items() if key in unitarity.O48_IDS}
        split.update({name: term for name, term in terms.items() if name != "T_Phi"})
        report = mutated(terms=split, member_scales={name: (Fraction(1, 50) if name == "T_Phi_O48" else Fraction(1)) for name in split})
        self.assertFailsClosed(
            report,
            "every_unit_computable_term_group_stationary_at_q0_exact",
            "member_gradient_exactly_zero",
        )
        groups = report["rescaling_lemma"]["unit_computable_groups"]
        self.assertIs(groups["T_Phi_O07"]["gradient_exactly_zero_at_q0"], False)
        self.assertIs(groups["T_Phi_O48"]["gradient_exactly_zero_at_q0"], False)

    def test_mutation_overall_one_fortieth(self) -> None:
        report = mutated(member_scales={name: Fraction(1, 40) for name in unitarity.TERM_NAMES})
        self.assertFailsClosed(report, "member_a0_below_half_exact", "member_lambda_eff_equals_127_over_3200")
        self.assertIs(report["checks"]["member_hessian_equals_s_times_witness_hessian_exact"], True)
        self.assertIs(report["checks"]["member_benchmark_inertia_447_39_0_kernel_T35_plus_doublets"], True)
        self.assertAlmostEqual(report["perturbative_member"]["a0_max_float"], 0.541348506928, delta=1.0e-10)

    def test_mutation_alpha_phi_1000(self) -> None:
        report = mutated(alpha_overrides={"Phi": Fraction(1000)})
        self.assertFailsClosed(report, "singlet_alphas_equal_pinned_exact_values", "research_MC_matrix_within_3_sigma_of_exact")

    def test_mutation_n_sigma_126(self) -> None:
        report = mutated(block_dims={"Sigma": 126})
        self.assertFailsClosed(
            report,
            "phi_sigma_consistency_n_Sigma_beta_equals_n_Phi_beta_equals_12915",
            "block_dimensions_and_congruence_factors_match_chart",
        )

    def test_mutation_O07_classified_as_quartic(self) -> None:
        report = mutated(unit_table={"O07 |Phi|^2": (4, "self", ("Phi",))})
        self.assertFailsClosed(report, "euler_degree_matches_table_for_every_unit_with_nonzero_gradient")
        self.assertIs(report["method"]["unit_classification"]["O07 |Phi|^2"]["degree_certified"], False)

    def test_check_count_is_enforced(self) -> None:
        report = mutated(expected_n_checks=10**6)
        self.assertFailsClosed(report, unitarity.CHECK_COUNT_FAILURE)
        self.assertEqual(report["failures"], [unitarity.CHECK_COUNT_FAILURE])
        self.assertNotIn(unitarity.CHECK_COUNT_FAILURE, report["checks"])
        for mutate in (
            lambda data: data.update(n_checks=unitarity.EXPECTED_N_CHECKS - 1),
            lambda data: data["checks"].pop(next(iter(data["checks"]))),
            lambda data: data["flags"].update(gate_status_changed=True),
        ):
            changed = copy.deepcopy(self.committed)
            mutate(changed)
            self.assertFalse(unitarity.report_passes(changed))
            self.assertMainRefuses(changed)

    def test_research_digest_tamper_fails_closed(self) -> None:
        files = dict(unitarity.RESEARCH_FILES)
        name = "wfRESCUE/D-G6-certification/s03_unitarity.json"
        files[name] = (files[name][0], "0" * 64)
        report = mutated(research_files=files)
        self.assertFailsClosed(report, "research_entries_labelled_with_provenance_and_pinned_digest")

    def test_main_writes_only_on_success(self) -> None:
        report = copy.deepcopy(self.committed)
        with mock.patch.object(unitarity, "build_report", return_value=report) as builder, mock.patch.object(
            unitarity, "write_report"
        ) as writer, mock.patch("builtins.print"):
            self.assertEqual(unitarity.main(["--write"]), 0)
            writer.assert_called_once_with(report)
            builder.assert_called_once_with(numerical=True)
        with mock.patch.object(unitarity, "build_report", return_value=report) as builder, mock.patch.object(
            unitarity, "write_report"
        ) as writer, mock.patch("builtins.print"):
            self.assertEqual(unitarity.main(["--no-numerics"]), 0)
            writer.assert_not_called()
            builder.assert_called_once_with(numerical=False)
        failed = copy.deepcopy(report)
        failed["n_failed"] = 1
        failed["status"] = unitarity.STATUS_INCOMPLETE
        self.assertMainRefuses(failed)

    def test_committed_hessian_modules_untouched_by_overrides(self) -> None:
        # The overrides keyword is used read-only: the default witness certificate is unchanged after the build.
        certificate = hessian.exact_certificate("benchmark")
        self.assertEqual((certificate["exact_rank"], certificate["exact_nullity"]), (447, 39))
        self.assertIs(certificate["spectral_gap"]["lambda_is_smallest_nonzero_eigenvalue"], True)


if __name__ == "__main__":
    unittest.main()
