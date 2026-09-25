#!/usr/bin/env python3
"""Tests for the G3 SM Pati-Salam gate readiness dry run (v20).

setUpClass builds one fresh report from the committed artifacts and compares
it with the committed readiness JSON.  The fail-closed tests inject mutated
copies of single artifacts (missing, failed, drifted or tampered) and require
the affected criterion to lose SATISFIED_EXACT and every readiness boolean to
go False.  Nothing here writes to the worktree.
"""
from __future__ import annotations

import ast
import contextlib
import copy
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any, Callable

import g3_sm_pati_salam_gate_readiness_v20 as readiness

QUOTIENT = "full_448_quotient_strictly_positive_exact"
RANK = "full_Hessian_rank_448_nullity_38_exact"
EQUALITY = "all_PD_equality_orbits_classified_exactly"
GAP = "beta_global_gap_and_unique_equality_exact"
SM_ALGEBRA = "target_unbroken_algebra_is_standard_model"
EXPECTED_EXACT = {
    "G1_G2_exact_scoped_calculations_complete",
    "full_candidate_exactly_stationary",
    "full_homogeneous_quartic_BFB_exact",
    SM_ALGEBRA,
    "target_symmetry_orbit_ranks_36_37_38_exact",
    "couplings_perturbative",
    EQUALITY,
    GAP,
    "authoritative_external_model_contract_executed",
    "G1_promoted_closed",
    "G2_promoted_closed",
}
ALLOWED_IMPORTS = {"__future__", "argparse", "hashlib", "json", "re", "fractions", "pathlib", "typing"}
EPS_BOOLEAN = "would_close_G3_mathematically_on_eps_member_if_SM_track_added"
S9 = "required_statement == theorem (wiring; S9)"


def _by_name(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {c["final_gate_criterion"]: c for c in report["criteria"]["science"] + report["criteria"]["release"]}


def _eps_by_name(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {c["final_gate_criterion"]: c for c in report["eps_member"]["criteria"]["science"] + report["criteria"]["release"]}


def _sha(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


class GateReadinessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.committed = json.loads(readiness.OUT_JSON.read_text(encoding="utf-8"))
        cls.fresh = json.loads(json.dumps(readiness.build_report()))
        cls.reports, _ = readiness.load_reports()

    # ------------------------------------------------------------------
    # Helpers.
    # ------------------------------------------------------------------

    def _build(self, key: str, *, replace: Any = None, mutate: Callable[[dict[str, Any]], None] | None = None) -> dict:
        reports = dict(self.reports)
        if mutate is None:
            reports[key] = {} if replace is None else replace
        else:
            # The ledger is ~10 MB: mutate a shallow copy and replace nested dicts, never edit them in place.
            value = dict(self.reports[key]) if key == "ledger" else copy.deepcopy(self.reports[key])
            mutate(value)
            reports[key] = value
        return readiness.build_report(reports=reports)

    def assertFailClosed(self, report: dict[str, Any]) -> None:
        self.assertIs(report["would_close_G3_mathematically_if_SM_track_added"], False)
        self.assertIs(report["readiness_booleans"]["would_close_G3_mathematically_if_SM_track_added"], False)
        self.assertIs(report["readiness_booleans"]["with_planner_S11_replacement_criterion"], False)
        self.assertIs(report["readiness_booleans"]["on_O06_raised_member"], False)
        self.assertEpsFalse(report)

    def assertEpsFalse(self, report: dict[str, Any]) -> None:
        self.assertIs(report[EPS_BOOLEAN], False)
        self.assertIs(report["readiness_booleans"][EPS_BOOLEAN], False)
        self.assertIs(report["eps_member"][EPS_BOOLEAN], False)
        self.assertIs(report["readiness_booleans"]["on_O06_raised_member"], False)
        self.assertTrue(report["eps_member"]["blocking_criteria"] or report["n_failed"])
        self.assertEqual(report["status"], readiness.STATUS)
        self.assertIs(report["gate_status_changed"], False)
        self.assertIs(report["G3_closed"], False)
        self.assertTrue(report["verdict"].startswith("DRY RUN ONLY -- this is not a G3 closure."))

    # ------------------------------------------------------------------
    # The committed report.
    # ------------------------------------------------------------------

    def test_committed_report_matches_fresh_build(self) -> None:
        self.assertEqual(self.committed, self.fresh)

    def test_dry_run_changes_no_gate_status(self) -> None:
        for report in (self.committed, self.fresh):
            self.assertEqual(report["status"], "G3_SM_TARGET_READINESS_DRY_RUN__NO_GATE_STATUS_CHANGED")
            self.assertIs(report["dry_run"], True)
            self.assertIs(report["gate_status_changed"], False)
            self.assertIs(report["G3_closed"], False)
            self.assertTrue(report["verdict"].startswith("DRY RUN ONLY -- this is not a G3 closure."))
            self.assertEqual(report["n_failed"], 0, report["failures"])
            self.assertEqual(report["n_checks"], len(report["integrity_checks"]))
            self.assertTrue(all(report["integrity_checks"].values()))
            self.assertEqual(report["missing_artifacts"], [])
            baseline = report["baseline_state"]
            self.assertEqual(baseline["final_gate_overall_state"], "OPEN")
            self.assertIs(baseline["final_gate_G3_closed"], False)
            self.assertEqual(baseline["ledger_gate_statuses"]["G3"], "OPEN")
            self.assertEqual(baseline["this_module_writes_only"], [readiness.OUT_JSON.name, readiness.OUT_MD.name])

    def test_every_final_gate_criterion_is_classified(self) -> None:
        gate = self.reports["final_gate"]
        names = set(gate["science_criteria"]) | set(gate["release_criteria"])
        records = _by_name(self.fresh)
        self.assertEqual(set(records), names)
        self.assertEqual(len(self.fresh["criterion_table"]), len(names))
        for name, record in records.items():
            self.assertIn(record["classification"], readiness.CLASSIFICATIONS, name)
            self.assertTrue(record["pati_salam_analogue"]["statement"], name)
            grade = record["pati_salam_analogue"]["grade"]
            self.assertTrue(grade in ("exact", "float64", "n/a (route-specific)") or grade.startswith("exact ("), name)
            if grade.startswith("exact ("):
                # A qualified exact grade must name the pending decision it presumes.
                for decision in record["conditional_on_decisions"]:
                    self.assertIn(decision, grade, name)
            self.assertTrue(record["justification"], name)
            self.assertIsInstance(record["value"], bool, name)
            self.assertIs(record["present_in_final_gate_report"], True, name)
            kind = "science" if name in gate["science_criteria"] else "release"
            self.assertEqual(record["chiral_H_track_value"], gate[f"{kind}_criteria"][name], name)
            self.assertTrue(record["evidence_exact"], name)
            for item in record["evidence_exact"] + record["evidence_float64"]:
                self.assertTrue({"artifact", "key", "expected", "actual", "ok"} <= set(item), name)

    def test_expected_classifications(self) -> None:
        records = _by_name(self.fresh)
        for name in EXPECTED_EXACT:
            self.assertEqual(records[name]["classification"], readiness.SATISFIED_EXACT, name)
            self.assertIs(records[name]["value"], True, name)
        for name in readiness.ROUTE_SPECIFIC_CRITERIA:
            self.assertEqual(records[name]["classification"], readiness.ROUTE_SPECIFIC, name)
            self.assertIs(records[name]["value"], True, name)
        # Both Hessian criteria fail under their literal analogues (451/35, kernel = the 35-dimensional orbit).
        for name in (RANK, QUOTIENT):
            self.assertEqual(records[name]["classification"], readiness.FAILED, name)
            self.assertIs(records[name]["value"], False, name)
            self.assertTrue(records[name]["justification"].startswith("Exactly false at the tuned benchmark"), name)
        self.assertEqual(records[RANK]["pati_salam_analogue"]["name"], "sm_full_Hessian_rank_451_nullity_35_exact")
        self.assertIn("447/39", records[RANK]["justification"])
        self.assertIn("451/35", records[RANK]["justification"])
        self.assertEqual(
            self.fresh["classification_counts"],
            {readiness.SATISFIED_EXACT: 11, readiness.SATISFIED_FLOAT_ONLY: 0, readiness.FAILED: 2,
             readiness.ROUTE_SPECIFIC: 7},
        )
        self.assertEqual(self.fresh["blocking_criteria"], [RANK, QUOTIENT])
        self.assertEqual(self.fresh["n_non_route_specific"], 13)
        self.assertEqual(self.fresh["n_non_route_specific_satisfied_exact"], 11)
        self.assertIn("satisfies 11 exactly", self.fresh["verdict"])
        self.assertIn("Both Hessian criteria are exactly false", self.fresh["verdict"])

    def test_cited_theorem_criteria_are_conditional_on_D6(self) -> None:
        records = _by_name(self.fresh)
        for name in (EQUALITY, GAP):
            self.assertEqual(records[name]["classification"], readiness.SATISFIED_EXACT, name)
            self.assertEqual(records[name]["conditional_on_decisions"], ["D6"], name)
            self.assertEqual(records[name]["pati_salam_analogue"]["grade"],
                             "exact (cited classical theorems + 6 hand-argued steps; D6)", name)
        self.assertIn("Cauchy-Schwarz", records[GAP]["justification"])
        self.assertEqual(self.fresh["satisfied_exact_conditional_on_decisions"], {EQUALITY: ["D6"], GAP: ["D6"]})
        self.assertEqual(self.fresh["readiness_booleans"]["decisions_presumed"], ["D6"])
        self.assertIn("subject to decisions D2 and D6", self.fresh["verdict"])
        self.assertIn("D6", self.fresh["readiness_booleans"]["with_planner_S11_replacement_criterion_note"])

    def test_s9_is_a_conjunct_of_the_gap_criterion_not_a_new_criterion(self) -> None:
        gap = _by_name(self.fresh)[GAP]
        self.assertEqual(gap["literal_conjuncts_not_evaluated"], ["required_statement == theorem (wiring; S9)"])
        self.assertEqual(self.fresh["literal_conjuncts_not_evaluated"], {GAP: ["required_statement == theorem (wiring; S9)"]})
        self.assertFalse(any(key.startswith("S9") for key in self.fresh["proposed_additional_criteria"]))
        self.assertIn("mathematical analogue", self.fresh["readiness_booleans"]["definition"])
        self.assertIn("S9", self.fresh["readiness_booleans"]["definition"])
        self.assertTrue(any("(S9)" in gap_row["item"] for gap_row in self.fresh["integration_gaps"]))

    def test_readiness_booleans(self) -> None:
        flags = self.fresh["readiness_booleans"]
        self.assertIs(self.fresh["would_close_G3_mathematically_if_SM_track_added"], False)
        self.assertIs(flags["would_close_G3_mathematically_if_SM_track_added"], False)
        self.assertIs(flags["science_criteria_all_satisfied_exact"], False)
        self.assertIs(flags["release_criteria_all_satisfied_exact"], True)
        self.assertIs(flags["integrity_checks_all_pass"], True)
        self.assertIs(flags["with_planner_S11_replacement_criterion"], True)
        self.assertEqual(flags["with_planner_S11_replacement_criterion_decisions_presumed"], ["D2", "D6"])
        # The raised member is the eps = r0^2/100 member of the eps family, which the eps evaluation covers.
        self.assertIs(flags["on_O06_raised_member"], True)
        self.assertIs(flags[EPS_BOOLEAN], True)
        self.assertIs(self.fresh[EPS_BOOLEAN], True)
        # D2: taking an eps > 0 member as the G3 witness is itself a pending decision (as S11 is for the tuned point).
        self.assertEqual(flags[EPS_BOOLEAN + "_decisions_presumed"], ["D2", "D6"])
        self.assertEqual(flags[EPS_BOOLEAN + "_wiring_conjuncts_not_evaluated"], [S9])
        self.assertIn("second option of D2", flags[EPS_BOOLEAN + "_note"])
        self.assertIn("electroweak symmetry is not broken", flags[EPS_BOOLEAN + "_note"])
        alternatives = _by_name(self.fresh)[QUOTIENT]["alternative_analogues"]
        s12 = alternatives["S12_O06_raised_member_rank_451_nullity_35_exact"]
        self.assertIs(s12["value"], True)
        self.assertIs(s12["raised_member_inside_certified_27_parameter_family"], False)
        self.assertIs(s12["global_minimum_and_equality_set_artifacts_cover_raised_member"], False)
        self.assertIs(s12["covered_by_exact_hessian_eps_family_L1_L2"], True)
        s11 = alternatives["S11_kernel_is_orbit_plus_tuned_light_doublet_exact"]
        self.assertIs(s11["value"], True)
        self.assertEqual(s11["replaces_criteria"], [RANK, QUOTIENT])

    def test_eps_member_meets_the_literal_criteria_exactly(self) -> None:
        for report in (self.committed, self.fresh):
            eps = report["eps_member"]
            self.assertEqual(eps["member"], "SM track witness family: O06 = 2|kappa| r0 + eps, eps > 0")
            records = _eps_by_name(report)
            gate = self.reports["final_gate"]
            self.assertEqual(set(records), set(gate["science_criteria"]) | set(gate["release_criteria"]))
            for name, record in records.items():
                self.assertTrue(record["evidence_exact"], name)
                if name in readiness.ROUTE_SPECIFIC_CRITERIA:
                    self.assertEqual(record["classification"], readiness.ROUTE_SPECIFIC, name)
                    continue
                self.assertEqual(record["classification"], readiness.SATISFIED_EXACT, name)
                self.assertIs(record["value"], True, name)
                self.assertTrue(all(item["ok"] for item in record["evidence_exact"]), name)
            # Both literal Hessian criteria hold on the eps member (451/35, kernel = orbit, for every eps > 0).
            self.assertEqual(records[RANK]["pati_salam_analogue"]["name"], "eps_member_full_Hessian_rank_451_nullity_35_exact")
            self.assertEqual(records[QUOTIENT]["pati_salam_analogue"]["name"],
                             "eps_member_full_451_quotient_strictly_positive_exact")
            for name in (RANK, QUOTIENT):
                keys = {item["key"] for item in records[name]["evidence_exact"]}
                self.assertIn("eps_family.L2_hessian.for_every_eps_positive.nullity", keys, name)
                self.assertIn("eps_family.checks.L2_dim_ker_H0_cap_ker_hess_N_H_equals_35", keys, name)
                self.assertIn("eps_family.consistency_certificates.tiny_eps.inertia_positive_zero_negative", keys, name)
            # The equality-set and global-gap criteria go through L1 and still presume D6; S9 is not evaluated.
            for name in (EQUALITY, GAP):
                self.assertEqual(records[name]["conditional_on_decisions"], ["D6"], name)
                keys = {item["key"] for item in records[name]["evidence_exact"]}
                self.assertIn("flags.eps_family_equality_set_unchanged", keys, name)
                self.assertIn("eps_family.checks.L1_equality_report_proved_status_and_premises", keys, name)
            self.assertIn("V_PS,eps(q)-V_PS,eps(q0)>=0", records[GAP]["pati_salam_analogue"]["statement"])
            self.assertEqual(records[GAP]["literal_conjuncts_not_evaluated"], [S9])
            self.assertEqual(
                eps["classification_counts"],
                {readiness.SATISFIED_EXACT: 13, readiness.SATISFIED_FLOAT_ONLY: 0, readiness.FAILED: 0,
                 readiness.ROUTE_SPECIFIC: 7},
            )
            self.assertEqual((eps["n_non_route_specific"], eps["n_non_route_specific_satisfied_exact"]), (13, 13))
            self.assertEqual(eps["blocking_criteria"], [])
            self.assertEqual(eps["satisfied_exact_conditional_on_decisions"], {EQUALITY: ["D6"], GAP: ["D6"]})
            self.assertEqual(eps["literal_conjuncts_not_evaluated"], {GAP: [S9]})
            self.assertIs(eps[EPS_BOOLEAN], True)
            self.assertEqual(
                eps["eps_window"],
                {"lower": "0 (exclusive): eps = 0 is the tuned benchmark (447/39, not strictly positive on the quotient)",
                 "upper_perturbative": "599/50", "upper_meaning": "O06_eps = 2|kappa| r0 + eps < 12 < 4 pi",
                 "raised_member_eps": "1/2500", "tiny_member_eps": "1/25000000"},
            )
            self.assertIn("electroweak symmetry is not broken", eps["physics"])
            # The tuned benchmark booleans are unchanged (literal: False).
            self.assertIs(report["would_close_G3_mathematically_if_SM_track_added"], False)
            self.assertIs(report["readiness_booleans"]["science_criteria_all_satisfied_exact"], False)
            verdict = report["verdict"]
            self.assertIn("the literal criteria are met exactly", verdict)
            self.assertIn(EPS_BOOLEAN + " = True, presuming decision(s) D2, D6 with the wiring conjunct S9 not evaluated",
                          verdict)
            # The all-criteria claim is scoped to the perturbative window; L1/L2 hold for every eps > 0.
            self.assertIn("inside the perturbative window 0 < eps < 599/50 (O06_eps = 2|kappa| r0 + eps < 12 < 4 pi; "
                          "couplings_perturbative is certified only there, while L1 and L2 hold for every eps > 0)",
                          verdict)
            self.assertIn("This module changed no gate status, gate report, ledger entry, workflow or checksum", verdict)
            # The tuned-doublet kernel is a G3 item (D2), consistent with caveat_gate_assignment.
            self.assertIn("the tuned-doublet Hessian kernel (resolved by D2", verdict)
            self.assertNotIn("and the tuned-doublet kernel, the coloured remnants", verdict)
            self.assertIn("tuned_light_doublet_hessian_zero_modes", report["caveat_gate_assignment"]["G3"])
            for row in report["integration_gaps"]:
                self.assertNotIn("not yet in CI workflows", row["detail"], row["item"])
            self.assertIn("The tuned eps = 0 limit is not a strict minimum", verdict)
            self.assertIn("light for eps << r0^2, but electroweak symmetry is not broken", verdict)
            self.assertIn("Under the planner's proposed routing (decision D5, pending", verdict)
            self.assertTrue(any(row["item"].startswith("eps-family extension") and row["state"] == "DONE"
                                for row in report["integration_gaps"]))
            self.assertIs(report["integrity_checks"]["sm_exact_hessian_eps_family_executes"], True)

    def test_eps_couplings_criterion_is_exact(self) -> None:
        record = _eps_by_name(self.fresh)["couplings_perturbative"]
        self.assertEqual(record["pati_salam_analogue"]["name"], "eps_member_couplings_perturbative_exact")
        items = {item["key"]: item for item in record["evidence_exact"]}
        self.assertEqual(items["raised_O06_coupling_perturbative"]["actual"], ["51/2500", "1/2500"])
        self.assertEqual(items["tiny_eps_coupling_perturbative"]["actual"], ["500001/25000000", "1/25000000"])
        self.assertEqual(items["perturbative_eps_window_is_0_to_12_minus_O06_base"]["actual"], "599/50")
        self.assertEqual(items["other_26_couplings_below_12"]["actual"], "73/8")

    def test_decisive_theorem_comparison(self) -> None:
        theorem = self.fresh["decisive_theorem"]
        self.assertEqual(theorem["final_theorem_pinned"], readiness.FINAL_THEOREM)
        self.assertIs(theorem["gate_report_theorem_equals_pinned"], True)
        self.assertEqual(readiness.SM_FINAL_THEOREM, readiness.FINAL_THEOREM.replace("V_beta", "V_PS"))
        self.assertIs(theorem["sm_final_theorem_is_final_theorem_with_V_beta_replaced_by_V_PS"], True)
        self.assertIs(theorem["exact_textual_agreement"], False)
        self.assertIs(theorem["equality_module_emits_required_statement"], False)
        self.assertIs(theorem["semantic_agreement"], True)
        self.assertTrue(all(theorem["semantic_components"].values()))
        self.assertEqual(theorem["gate_symmetry_group_normalised"], "SO(10)xU(1)_XxPQ")
        self.assertEqual(theorem["equality_module_symmetry_group_normalised"], "SO(10)xU(1)_XxPQ")

    def test_caveats_are_assigned_to_gates(self) -> None:
        caveats = {row["id"]: row for row in self.fresh["physics_caveats"]}
        for row in caveats.values():
            self.assertIn(row["assigned_gate"], {"G3", "G4", "G5", "G6", "G7", "G8", "OUTSIDE_G1_G8"}, row["id"])
            self.assertIs(row["evidence_present"], True, row["id"])
        self.assertEqual(
            set(self.fresh["caveat_gate_assignment"]["G3"]),
            {
                "uniqueness_uses_accidental_U1_PQ",
                "tuned_light_doublet_hessian_zero_modes",
                "exact_hessian_certified_at_one_benchmark_only",
                "compiler_equals_SOS_end_to_end_float64_only",
                "cited_theorems_and_elementary_steps_not_machine_checked",
                "benchmark_family_only",
            },
        )
        downstream = {
            "doublet_triplet_splitting_tuned": "OUTSIDE_G1_G8",
            "coloured_126bar_remnants_below_M_I": "G6",
            "no_electroweak_symmetry_breaking": "G6",
            "rg_anchor_field_content_not_reproduced": "G7",
            "higgs_quartic_too_large_at_benchmark": "G7",
            "no_realistic_yukawa_sector": "G8",
            "phi17_not_at_canonical_scale": "G6",
            "G5_certified_on_a_different_coupling_vector": "G5",
            "symmetry_ranks_differ_from_G4_spec": "G4",
        }
        for cid, gate in downstream.items():
            self.assertEqual(caveats[cid]["assigned_gate"], gate, cid)

    def test_caveat_routing_is_marked_as_the_pending_proposal_D5(self) -> None:
        status = "PROPOSED_UNDER_D5__NOT_CURRENT_REPO_DEFINITION"
        for report in (self.committed, self.fresh):
            self.assertEqual(report["caveat_routing_status"], status)
            self.assertEqual(report["caveat_gate_assignment_status"], status)
            self.assertEqual(report["wave3_clause_reading"]["status"], status)
            self.assertIn("Under the planner's proposed routing (decision D5, pending", report["verdict"])
            self.assertIn("otherwise these caveats remain G3-wave requirements", report["verdict"])
            self.assertNotIn("routed by the gates' definitions", report["verdict"])
            for row in report["physics_caveats"]:
                self.assertEqual(row["assignment_status"], status, row["id"])
                if row["model_level_caveat"]:
                    self.assertTrue(row["under_current_repo_text"].startswith("G3-wave requirement"), row["id"])
        # The wave-3 clause quoted is the ledger's current text.
        ledger_wave3 = self.reports["ledger"]["closure_waves"][3]["deliverable"]
        self.assertIn(readiness.WAVE3_CLAUSE, ledger_wave3)
        self.assertIn("sm_model_level_caveats_disclosed", self.fresh["integrity_checks"])
        self.assertNotIn("sm_model_level_caveats_disclosed_not_required", self.fresh["integrity_checks"])

    def test_caveat_bases_cite_existing_repository_text(self) -> None:
        caveats = {row["id"]: row for row in self.fresh["physics_caveats"]}
        self.assertTrue(caveats["phi17_not_at_canonical_scale"]["basis"].startswith("roadmap W4-G6 acceptance"))
        self.assertTrue(caveats["no_realistic_yukawa_sector"]["basis"].startswith("roadmap W6-G8 acceptance"))
        self.assertIn("full_448_quotient_strictly_positive_exact (exact_PSD, strict_quotient_positive",
                      caveats["tuned_light_doublet_hessian_zero_modes"]["basis"])
        self.assertTrue(caveats["benchmark_family_only"]["basis"].startswith("proposed closure-scope wording"))
        self.assertIn("not in repo", caveats["doublet_triplet_splitting_tuned"]["effect_on_G3"])
        text = json.dumps(self.fresh)
        for fabricated in ("final gate: 'exact full Hessian rank/nullity certificate'", "closure scope: 'exact SM",
                           "ledger G6: 'all eigenmasses", "ledger G8: 'one authoritative vacuum"):
            self.assertNotIn(fabricated, text)

    def test_g5_coupling_vector_mismatch_is_detected(self) -> None:
        g5 = self.fresh["proposed_additional_criteria"]["G5_BFB_evidence_covers_closing_coupling_vector"]
        self.assertIs(g5["value"], False)
        self.assertEqual(
            set(g5["comparison"]["constant_entries_that_differ"]),
            {"lambda::O27_B03_126bar_self_projectors", "lambda::O27_B04_126bar_self_projectors"},
        )

    def test_planner_analysis_summarised(self) -> None:
        analysis = self.fresh["planner_option_analysis"]
        self.assertEqual(analysis["recommendation"], "i_prime_hybrid")
        self.assertEqual(set(analysis["decisions_needed"]), {"D1", "D2", "D3", "D4", "D5", "D6"})
        self.assertEqual(
            set(analysis["options"]),
            {"i_either_track_closes", "ii_retarget_entirely", "iii_separate_SM_gate", "i_prime_hybrid"},
        )

    # ------------------------------------------------------------------
    # Fail-closed behaviour.
    # ------------------------------------------------------------------

    def test_injected_unmodified_reports_reproduce_the_classifications(self) -> None:
        report = readiness.build_report(reports=self.reports)
        self.assertEqual(report["criterion_table"], self.fresh["criterion_table"])
        self.assertEqual(report["readiness_booleans"], self.fresh["readiness_booleans"])

    def test_missing_exact_hessian_fails_closed(self) -> None:
        report = self._build("exact_hessian")
        records = _by_name(report)
        self.assertIs(report["integrity_checks"]["sm_exact_hessian_report_executes"], False)
        self.assertIn(readiness.ARTIFACT_FILES["exact_hessian"], report["missing_artifacts"])
        self.assertGreater(report["n_failed"], 0)
        for name in (RANK, QUOTIENT):
            # The float64 analogue (no projected zero mode) is false too, so nothing holds: fail closed.
            self.assertEqual(records[name]["classification"], readiness.FAILED, name)
            self.assertIs(records[name]["value"], False, name)
            self.assertTrue(records[name]["justification"].startswith("Fail closed"), name)
            self.assertIn("sm_exact_hessian_report_executes", records[name]["failed_preconditions"], name)
        self.assertFailClosed(report)

    def test_injected_non_psd_hessian_fails_both_hessian_criteria(self) -> None:
        # A loaded, executing exact Hessian report whose certificate refutes positivity must give FAILED, never
        # SATISFIED_EXACT or SATISFIED_FLOAT_ONLY, even when the tampered counts look like the literal 35.
        def mutate_hessian(value: dict[str, Any]) -> None:
            cert = value["exact_certificate"]
            cert["exact_nullity"] = 35
            cert["kernel_spanning_set"] = "35 symmetry tangents"
            cert["exact_PSD"] = False
            cert["strictly_positive_on_kernel_complement"] = False
            cert["inertia"]["negative"] = 4

        def mutate_candidate(value: dict[str, Any]) -> None:
            value["flags"]["hessian_psd_kernel_is_symmetry"] = True

        reports = dict(self.reports)
        hess = copy.deepcopy(self.reports["exact_hessian"])
        mutate_hessian(hess)
        cand = copy.deepcopy(self.reports["candidate"])
        mutate_candidate(cand)
        reports["exact_hessian"] = hess
        reports["candidate"] = cand
        report = readiness.build_report(reports=reports)
        records = _by_name(report)
        self.assertEqual(report["n_failed"], 0, report["failures"])  # integrity checks do not see these fields
        for name in (RANK, QUOTIENT):
            self.assertEqual(records[name]["classification"], readiness.FAILED, name)
            self.assertIs(records[name]["value"], False, name)
            self.assertIn("false exact evidence", records[name]["justification"], name)
        self.assertEqual(report["classification_counts"][readiness.SATISFIED_FLOAT_ONLY], 0)
        self.assertFailClosed(report)

    def test_injected_symmetry_only_psd_kernel_would_satisfy_the_literal_hessian_criteria(self) -> None:
        # Control: a consistent certificate with kernel = orbit (the raised member's shape) satisfies both literal
        # criteria, so the FAILED classification above is data-driven, not hard-coded.
        def mutate(value: dict[str, Any]) -> None:
            raised = copy.deepcopy(value["exact_certificate_raised_O06"])
            value["exact_certificate"] = raised
            value["flags"] = {**value["flags"], "strict_quotient_positive": True,
                              "strictly_positive_on_symmetry_quotient": True,
                              "all_zero_modes_are_symmetry_tangents": True}

        report = self._build("exact_hessian", mutate=mutate)
        records = _by_name(report)
        for name in (RANK, QUOTIENT):
            self.assertEqual(records[name]["classification"], readiness.SATISFIED_EXACT, name)

    def test_failed_equality_set_fails_closed(self) -> None:
        def mutate(value: dict[str, Any]) -> None:
            value["n_failed"] = 1
            value["failures"] = ["P2_self_weights_force_sigma_purity"]

        report = self._build("equality_set", mutate=mutate)
        records = _by_name(report)
        eps_records = _eps_by_name(report)
        self.assertIs(report["integrity_checks"]["sm_equality_set_report_executes"], False)
        for name in (EQUALITY, GAP):
            self.assertNotEqual(records[name]["classification"], readiness.SATISFIED_EXACT, name)
            self.assertIs(records[name]["value"], False, name)
            # The eps member's equality/gap criteria rest on the same equality report (L1): they fail closed too.
            self.assertNotEqual(eps_records[name]["classification"], readiness.SATISFIED_EXACT, name)
            self.assertIs(eps_records[name]["value"], False, name)
        self.assertIn(EQUALITY, report["eps_member"]["blocking_criteria"])
        self.assertFailClosed(report)

    # ------------------------------------------------------------------
    # Fail-closed behaviour of the eps member.
    # ------------------------------------------------------------------

    def _hessian_with(self, mutate: Callable[[dict[str, Any]], None]) -> dict[str, Any]:
        return self._build("exact_hessian", mutate=mutate)

    def test_eps_kernel_flag_false_fails_the_eps_rank_criterion_only(self) -> None:
        def mutate(value: dict[str, Any]) -> None:
            value["flags"]["eps_family_kernel_equals_symmetry_orbit"] = False

        report = self._hessian_with(mutate)
        self.assertEqual(report["n_failed"], 0, report["failures"])
        eps_records = _eps_by_name(report)
        self.assertEqual(eps_records[RANK]["classification"], readiness.FAILED)
        self.assertIn("false exact evidence", eps_records[RANK]["justification"])
        self.assertIn(RANK, report["eps_member"]["blocking_criteria"])
        self.assertEpsFalse(report)
        # The tuned-benchmark evaluation is untouched.
        self.assertEqual(report["criterion_table"], self.fresh["criterion_table"])
        self.assertIs(report["readiness_booleans"]["with_planner_S11_replacement_criterion"], True)
        # S12's eps-family coverage needs every eps flag.
        s12 = _by_name(report)[QUOTIENT]["alternative_analogues"]["S12_O06_raised_member_rank_451_nullity_35_exact"]
        self.assertIs(s12["covered_by_exact_hessian_eps_family_L1_L2"], False)

    def test_eps_equality_flag_false_fails_the_eps_vacuum_criteria(self) -> None:
        def mutate(value: dict[str, Any]) -> None:
            value["flags"]["eps_family_equality_set_unchanged"] = False

        report = self._hessian_with(mutate)
        self.assertEqual(report["n_failed"], 0, report["failures"])
        eps_records = _eps_by_name(report)
        for name in (EQUALITY, GAP, "full_candidate_exactly_stationary", SM_ALGEBRA):
            self.assertEqual(eps_records[name]["classification"], readiness.FAILED, name)
        self.assertEpsFalse(report)
        # The benchmark's own equality-set and gap criteria do not depend on L1.
        records = _by_name(report)
        for name in (EQUALITY, GAP):
            self.assertEqual(records[name]["classification"], readiness.SATISFIED_EXACT, name)

    def test_failed_eps_family_section_fails_closed(self) -> None:
        def mutate(value: dict[str, Any]) -> None:
            eps = copy.deepcopy(value["eps_family"])
            eps["n_failed"] = 1
            eps["failures"] = ["L2_T35_vanishes_on_H_block"]
            eps["checks"]["L2_T35_vanishes_on_H_block"] = False
            value["eps_family"] = eps

        report = self._hessian_with(mutate)
        self.assertIs(report["integrity_checks"]["sm_exact_hessian_eps_family_executes"], False)
        self.assertIn("sm_exact_hessian_eps_family_executes", report["failures"])
        for name in (RANK, QUOTIENT):
            record = _eps_by_name(report)[name]
            self.assertNotEqual(record["classification"], readiness.SATISFIED_EXACT, name)
            self.assertIn("sm_exact_hessian_eps_family_executes", record["failed_preconditions"], name)
        self.assertTrue(any(row["item"].startswith("eps-family extension") and row["state"] == "OPEN"
                            for row in report["integration_gaps"]))
        self.assertFailClosed(report)

    def test_missing_eps_family_section_fails_closed(self) -> None:
        def mutate(value: dict[str, Any]) -> None:
            del value["eps_family"]

        report = self._hessian_with(mutate)
        self.assertIs(report["integrity_checks"]["sm_exact_hessian_eps_family_executes"], False)
        self.assertFailClosed(report)

    def test_non_perturbative_raised_O06_fails_the_eps_couplings_criterion(self) -> None:
        def mutate(value: dict[str, Any]) -> None:
            value["benchmark"]["O06_raised"] = "13"

        report = self._hessian_with(mutate)
        self.assertEqual(report["n_failed"], 0, report["failures"])
        record = _eps_by_name(report)["couplings_perturbative"]
        self.assertEqual(record["classification"], readiness.FAILED)
        self.assertIn("raised_O06_coupling_perturbative", record["justification"])
        self.assertEqual(_by_name(report)["couplings_perturbative"]["classification"], readiness.SATISFIED_EXACT)
        self.assertEpsFalse(report)

    def test_bool_n_failed_is_not_accepted(self) -> None:
        def mutate(value: dict[str, Any]) -> None:
            value["n_failed"] = False

        report = self._build("candidate", mutate=mutate)
        self.assertIs(report["integrity_checks"]["sm_candidate_report_executes"], False)
        self.assertNotEqual(_by_name(report)[SM_ALGEBRA]["classification"], readiness.SATISFIED_EXACT)
        self.assertFailClosed(report)

    def test_missing_candidate_fails_closed(self) -> None:
        report = self._build("candidate")
        records = _by_name(report)
        self.assertEqual(records[SM_ALGEBRA]["classification"], readiness.FAILED)
        self.assertEqual(records["couplings_perturbative"]["classification"], readiness.FAILED)
        self.assertIs(records["full_fixed_F_offkernel_gap_and_equality_exact"]["value"], False)
        self.assertEqual(
            records["full_fixed_F_offkernel_gap_and_equality_exact"]["classification"], readiness.ROUTE_SPECIFIC
        )
        self.assertFailClosed(report)

    def test_missing_ledger_fails_release_criteria(self) -> None:
        report = self._build("ledger")
        records = _by_name(report)
        for name in ("G1_G2_exact_scoped_calculations_complete", "authoritative_external_model_contract_executed",
                     "G1_promoted_closed", "G2_promoted_closed"):
            self.assertEqual(records[name]["classification"], readiness.FAILED, name)
        self.assertIs(report["readiness_booleans"]["release_criteria_all_satisfied_exact"], False)
        self.assertFailClosed(report)

    def test_ledger_gate_not_closed_fails_release_criterion(self) -> None:
        def mutate(value: dict[str, Any]) -> None:
            value["gates"] = {**value["gates"], "G2": {**value["gates"]["G2"], "status": "OPEN"}}

        report = self._build("ledger", mutate=mutate)
        self.assertEqual(_by_name(report)["G2_promoted_closed"]["classification"], readiness.FAILED)
        self.assertEqual(report["n_failed"], 0)
        self.assertFailClosed(report)

    def test_missing_final_gate_fails_closed(self) -> None:
        report = self._build("final_gate")
        self.assertIs(report["integrity_checks"]["final_gate_report_executes"], False)
        self.assertIs(report["integrity_checks"]["final_gate_criteria_match_readiness_map"], False)
        self.assertEqual(len(report["criterion_table"]), 20)
        self.assertTrue(all(row["chiral_H_value"] is None for row in report["criterion_table"]))
        self.assertFailClosed(report)

    def test_unknown_final_gate_criterion_fails_closed(self) -> None:
        def mutate(value: dict[str, Any]) -> None:
            value["science_criteria"]["new_unmapped_criterion"] = True

        report = self._build("final_gate", mutate=mutate)
        record = _by_name(report)["new_unmapped_criterion"]
        self.assertEqual(record["classification"], readiness.FAILED)
        self.assertTrue(record["justification"].startswith("Fail closed"))
        self.assertIs(report["integrity_checks"]["final_gate_criteria_match_readiness_map"], False)
        self.assertFailClosed(report)

    def test_drifted_final_theorem_fails_closed(self) -> None:
        def mutate(value: dict[str, Any]) -> None:
            value["decisive_theorem"] = value["decisive_theorem"].replace("exactly", "only")

        report = self._build("final_gate", mutate=mutate)
        self.assertIs(report["integrity_checks"]["final_gate_report_executes"], False)
        self.assertFailClosed(report)

    def test_new_cited_theorem_fails_closed(self) -> None:
        def mutate(value: dict[str, Any]) -> None:
            value["scope"]["cited_not_machine_checked"].append("an extra unverified classical theorem")

        report = self._build("equality_set", mutate=mutate)
        self.assertIs(report["integrity_checks"]["sm_unchecked_proof_inputs_pinned"], False)
        # The exact claim is withdrawn; only the float64 corroboration is left.
        record = _by_name(report)[EQUALITY]
        self.assertEqual(record["classification"], readiness.SATISFIED_FLOAT_ONLY)
        self.assertIs(record["value"], False)
        self.assertIn("sm_unchecked_proof_inputs_pinned", record["failed_preconditions"])
        self.assertFailClosed(report)

    def test_caveat_flag_type_drift_fails_closed(self) -> None:
        def mutate(value: dict[str, Any]) -> None:
            value["flags"]["higgs_mass_compatible"] = "no"

        report = self._build("candidate", mutate=mutate)
        self.assertIs(report["integrity_checks"]["sm_model_level_caveats_disclosed"], False)
        self.assertFailClosed(report)

    def test_tampered_hessian_coupling_vector_fails_closed(self) -> None:
        def mutate(value: dict[str, Any]) -> None:
            value["benchmark"]["exact_coefficients"]["lambda::O06_B01_Hdag_H_norm"] = "51/2500"

        report = self._build("exact_hessian", mutate=mutate)
        self.assertIs(report["integrity_checks"]["sm_candidate_equality_set_hessian_cross_bound"], False)
        self.assertNotEqual(_by_name(report)[RANK]["classification"], readiness.SATISFIED_EXACT)
        self.assertFailClosed(report)

    def test_symmetry_group_drift_breaks_semantic_agreement(self) -> None:
        def mutate(value: dict[str, Any]) -> None:
            value["theorem"] = value["theorem"].replace("G = SO(10) x U(1)_X x U(1)_PQ,", "G = SO(10) x U(1)_X,")

        report = self._build("equality_set", mutate=mutate)
        self.assertIs(report["decisive_theorem"]["semantic_components"]["same_symmetry_group_G"], False)
        self.assertIs(report["decisive_theorem"]["semantic_agreement"], False)
        # The loaded, executing equality report proves a different theorem: the exact evidence refutes the
        # criterion (FAILED), it is not merely unavailable (which would leave SATISFIED_FLOAT_ONLY).
        record = _by_name(report)[GAP]
        self.assertEqual(record["classification"], readiness.FAILED)
        self.assertIs(record["value"], False)
        self.assertIn("decisive_theorem_semantic_agreement", record["justification"])
        self.assertFailClosed(report)

    def test_loader_fails_closed_on_disk(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "bad.json").write_text("{not json", encoding="utf-8")
            (root / "list.json").write_text("[1, 2]", encoding="utf-8")
            (root / "empty.json").write_text("{}", encoding="utf-8")
            self.assertEqual(readiness.load_artifact(root / "nope.json")[:2], ({}, "missing"))
            self.assertEqual(readiness.load_artifact(root / "bad.json")[:2], ({}, "unparseable JSON"))
            self.assertEqual(readiness.load_artifact(root / "list.json")[:2], ({}, "not a JSON object"))
            self.assertEqual(readiness.load_artifact(root / "empty.json")[:2], ({}, "empty JSON object"))
            report = readiness.build_report(paths={"exact_hessian": root / "nope.json"})
            meta = report["artifacts"]["exact_hessian"]
            self.assertIs(meta["loaded"], False)
            self.assertEqual(meta["error"], "missing")
            self.assertIn(readiness.ARTIFACT_FILES["exact_hessian"], report["missing_artifacts"])
            self.assertFailClosed(report)

    # ------------------------------------------------------------------
    # Hygiene.
    # ------------------------------------------------------------------

    def test_module_imports_only_light_standard_library(self) -> None:
        tree = ast.parse(Path(readiness.__file__).read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.add((node.module or "").split(".")[0])
        self.assertLessEqual(imported, ALLOWED_IMPORTS)

    def test_main_without_write_touches_nothing(self) -> None:
        watched = [readiness.ROOT / name for name in readiness.ARTIFACT_FILES.values()]
        watched += [readiness.OUT_JSON, readiness.OUT_MD]
        before = {path.name: _sha(path) for path in watched}
        with contextlib.redirect_stdout(io.StringIO()):
            code = readiness.main([])
        self.assertEqual(code, 0)
        self.assertEqual({path.name: _sha(path) for path in watched}, before)


if __name__ == "__main__":
    unittest.main()
