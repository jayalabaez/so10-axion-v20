#!/usr/bin/env python3
"""Tests for the G8 structural-obstruction record (v20; evidence only, no gate status change).

setUpClass computes the sections once (exact Weyl-element lemmas, contract corollaries, the 120_H X-parity census and
tensor checks, the s-structure and real-type lemma in sympy, the off-q0 selection polynomials with one live-compiler
binding pass, the (15,2,2) mass binding and the research record; well under the 150 s budget) and compares the
assembled report with the committed artifact: exact leaves must match exactly, float leaves (compiler binding
deviation, rational-point residual, the NUM research-consistency deviation) within 1e-9 relative / 1e-12 absolute.  The
fail-closed mutation tests recompute one section with one changed input each (a 45 B-L vev in the charged-sector vev
set, a 120_H with X = -3, conjugate mixing at tan beta != 1 in the claimed point set, a lattice-bound coefficient
perturbed by 1/L, a corrupted G6 level, a tampered research sha256, an extra check, an uncorrected G8 v2 Route B text)
and require the named check to fail, the status to drop to INCOMPLETE and main --write to refuse without writing.
"""
from __future__ import annotations

import contextlib
import copy
import io
import json
import math
import tempfile
import time
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

import g8_sm_pati_salam_flavour_nogo_v20 as g8_v2
import g8_sm_pati_salam_structural_obstruction_v20 as obstruction

TIMING_KEYS = {"runtime_seconds"}
FLOAT_REL = 1.0e-9
FLOAT_ABS = 1.0e-12
SETUP_BUDGET_SECONDS = 150.0
EXPECTED_STATUS = "G8_SM_PATI_SALAM_STRUCTURAL_OBSTRUCTION__SOS_CERTIFIED_FAMILY_FLAVOUR_DEAD__RECORDED__NO_GATE_CHANGE"
EXPECTED_INCOMPLETE = "G8_SM_PATI_SALAM_STRUCTURAL_OBSTRUCTION_INCOMPLETE__NO_GATE_CHANGE"
EXPECTED_OVERALL = "CERTIFIED_WITNESS_FAMILY_FLAVOUR_DEAD_EXACT__OFF_ORIENTATION_SPLITTERS_RESEARCH_RECORDED"
EXPECTED_N_CHECKS = 78
TRUE_FLAGS = ("certified_family_flavour_dead_exact", "L1_portal_robust", "off_orientation_splitters_research_recorded", "evidence_only")
NEVER_TRUE = (
    "G8_closed",
    "gate_status_changed",
    "wired_into_gate_ledger",
    "report_closes_G8_by_itself",
    "falsifies_so10_contract",
    "falsifies_G3_G5_certificates",
    "route_B_reduced_to_120H_among_all_extensions",
    "loop_level_flavour_analysed",
    "off_orientation_splitters_rederived_here",
)
EXPECTED_FACTORS = {
    "O15|H+": "a + w",
    "O15|H-": "a - w",
    "O38|H+": "a - w",
    "O38|H-": "a + w",
    "O45_B01|H+": "a**2 + 2*a*w + p*w + 2*w**2",
    "O45_B01|H-": "-a**2 + 2*a*w + p*w - 2*w**2",
    "O45_B02|H+": "-a**2 - 2*a*w + 2*p*w + w**2",
    "O45_B02|H-": "a**2 - 2*a*w + 2*p*w - w**2",
}
# The research sha256 table of the spec (section 7, M1) plus C/c6_landau_cost.json (second 126bar Landau record),
# C/c8_second126_portals.json (portal census) and critic/c1_f17_light1522_scan.json (light (15,2,2) no-root row).
EXPECTED_RESEARCH_SHA = {
    "C/c1_spinor.py": "5fd049bbdcafb843dfd870bf28eac6328ed5b10d6a18ff0ae1ffe11c58919b9d",
    "C/c2_weyl_lemmas.py": "3c2f838e6ee4513027bbef97e56ef25fba7f53818e0bfa461188e39c9b7c1473",
    "C/c2_weyl_lemmas.json": "0004d434d35daddfbcfd8e09b1a0e01bc2a86011afc4305fe9bacfaa2857d3a0",
    "C/verify-feasibility/v3_45_scalar_portal.json": "f19529928b77c65194f648efd8646731a5d0bddcece16602dfc90b64a54024f8",
    "C/verify-physics/v1_spinor_indep.json": "9316dc7d66d37f01d7a11eca7645cf0f19930d85bfa07c2b14cf384b95e3d0bb",
    "C/c6_landau_cost.json": "78cc4eb01879dae36a6aeeee96339ec1772c7409621ba237479fa4464afbb1a4",
    "C/c8_second126_portals.json": "294d5c0552ee5fae3f5b5f1efa8ac1938a23d2374d0566cac8cdc11dd0a24a1f",
    "B/verify-feasibility/xparity.json": "aa4b4c4cd5dfbc9f520a3027db955d6b2aa6d70e9be180fa00fcfddb7d1e48fd",
    "B/selection120.json": "3362628b29e5078a716221bebe6413e7cf935bd12624d58c3a74e81b6787621c",
    "critic/c1_f17_light1522_scan.json": "4481ba5df0ee232dec1a04c39439fcfda59a423312d9b84239bb52488b139d3d",
    "B/sos120.json": "526d4551a529c3e7ceb3de61411374de9d89f749092ec44847fe81f7839378f9",
    "B/fitB_pure10_120_1.27e+09_21.json": "c3def7c804fcaa8a2240bef012869af916d902ae6022a9ef5e7f1c7425a60a15",
    "B/fitB_pure10_120_1e+13_22.json": "868b822b0497782c1a3bce914accee6d45ea37d9fb58ffe3fd4a5fd832ccea85",
    "A/a1_selection_offq0.json": "236d57400052c7420995b76a0303241cf2a9c70ed72026a40a5ed606b57b967c",
    "A/a2_s_structure.json": "138cde03a608ad8d48e2dd90d9b5e176678f77d14b29f019a6b0c874f66bf1c3",
    "A/a3_portal_polynomials.json": "78300c431e63d976a3bc6f7a1c5a7f3dbfd8d0cf637bebdcf0f9e20ab71cc359",
    "routes_and_verdicts.json": "c20dff1098e95288b4b66a7060e3571dce3ed4f5eb56fd62c7cb938fe22f6434",
}


def _mismatches(committed: Any, fresh: Any, path: str = "") -> list[str]:
    if isinstance(committed, dict) and isinstance(fresh, dict):
        output: list[str] = []
        for key in sorted((set(committed) | set(fresh)) - TIMING_KEYS):
            if key not in committed or key not in fresh:
                output.append(f"{path}.{key}: missing")
                continue
            output += _mismatches(committed[key], fresh[key], f"{path}.{key}")
        return output
    if isinstance(committed, list) and isinstance(fresh, list):
        if len(committed) != len(fresh):
            return [f"{path}: length {len(committed)} != {len(fresh)}"]
        output = []
        for index, (left, right) in enumerate(zip(committed, fresh)):
            output += _mismatches(left, right, f"{path}[{index}]")
        return output
    if isinstance(committed, bool) or isinstance(fresh, bool):
        return [] if committed is fresh else [f"{path}: {committed!r} != {fresh!r}"]
    if isinstance(committed, float) or isinstance(fresh, float):
        try:
            same = math.isclose(float(committed), float(fresh), rel_tol=FLOAT_REL, abs_tol=FLOAT_ABS)
        except (TypeError, ValueError):
            same = False
        return [] if same else [f"{path}: {committed!r} != {fresh!r}"]
    return [] if committed == fresh else [f"{path}: {committed!r} != {fresh!r}"]


class G8StructuralObstructionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.committed = json.loads(obstruction.OUT_JSON.read_text(encoding="utf-8"))
        started = time.time()
        cls.sections = obstruction.compute_sections()
        cls.report = obstruction.assemble_report(cls.sections, started=started)
        cls.fresh = obstruction.json_roundtrip(cls.report)
        cls.setup_seconds = time.time() - started

    # ------------------------------------------------------------------ helpers

    def _mutated(self, **replacements: Any) -> dict[str, Any]:
        sections = {**self.sections, **replacements}
        return obstruction.assemble_report(sections)

    def _assert_fails_closed(self, report: dict[str, Any], check: str) -> None:
        self.assertIs(report["checks"].get(check), False, check)
        self.assertIn(check, report["failures"])
        self.assertEqual(report["status"], EXPECTED_INCOMPLETE)
        self.assertEqual(report["overall_state"], obstruction.OVERALL_STATE_OPEN)
        self.assertFalse(obstruction.report_passes(report))
        self.assertIs(report["flags"]["certified_family_flavour_dead_exact"], False)
        self.assertTrue(report["verdict"].startswith("FAIL-CLOSED"))
        self._assert_write_refused(report)

    def _assert_write_refused(self, report: dict[str, Any]) -> None:
        with tempfile.TemporaryDirectory() as directory:
            out_json = Path(directory) / "refused.json"
            out_md = Path(directory) / "refused.md"
            with mock.patch.object(obstruction, "OUT_JSON", out_json), mock.patch.object(obstruction, "OUT_MD", out_md), \
                    mock.patch.object(obstruction, "build_report", return_value=report), contextlib.redirect_stdout(io.StringIO()):
                code = obstruction.main(["--write"])
            self.assertNotEqual(code, 0)
            self.assertFalse(out_json.exists())
            self.assertFalse(out_md.exists())

    # ------------------------------------------------------------------ status, counts, flags, artifact

    def test_status_checks_and_flags(self) -> None:
        for report in (self.committed, self.fresh):
            self.assertEqual(report["module"], "g8_sm_pati_salam_structural_obstruction_v20")
            self.assertEqual(report["model_contract_id"], "gauged_u1x_phi17_v20")
            self.assertEqual(report["status"], EXPECTED_STATUS)
            self.assertEqual(report["overall_state"], EXPECTED_OVERALL)
            self.assertEqual(report["n_failed"], 0, report["failures"])
            self.assertEqual(report["n_checks"], EXPECTED_N_CHECKS)
            self.assertEqual(len(report["checks"]), EXPECTED_N_CHECKS)
            self.assertTrue(all(report["checks"].values()))
            counts: dict[str, int] = {}
            for key in report["checks"]:
                counts[key.split(".")[0]] = counts.get(key.split(".")[0], 0) + 1
            self.assertEqual(counts, obstruction.EXPECTED_SECTION_COUNTS)
            for name in TRUE_FLAGS:
                self.assertIs(report["flags"][name], True, name)
            for name in NEVER_TRUE:
                self.assertIs(report["flags"][name], False, name)
        self.assertEqual(obstruction.STATUS_RECORDED, EXPECTED_STATUS)
        self.assertEqual(obstruction.STATUS_INCOMPLETE, EXPECTED_INCOMPLETE)
        self.assertEqual(obstruction.OVERALL_STATE_RECORDED, EXPECTED_OVERALL)
        self.assertEqual(obstruction.EXPECTED_N_CHECKS, EXPECTED_N_CHECKS)
        self.assertEqual(tuple(obstruction.NEVER_TRUE_FLAGS), NEVER_TRUE)
        self.assertTrue(obstruction.report_passes(self.report))

    def test_committed_artifact_matches_fresh_report(self) -> None:
        self.assertEqual(_mismatches(self.committed, self.fresh), [])

    def test_committed_markdown_regenerates(self) -> None:
        expected = obstruction._markdown(self.committed).replace("\r\n", "\n")
        self.assertEqual(obstruction.OUT_MD.read_text(encoding="utf-8").replace("\r\n", "\n"), expected)

    def test_runtime_budget(self) -> None:
        self.assertLess(self.setup_seconds, SETUP_BUDGET_SECONDS)

    # ------------------------------------------------------------------ exact content

    def test_weyl_element_lemmas(self) -> None:
        weyl = self.fresh["weyl_lemmas"]
        de, cust = weyl["elements"]["g_de"], weyl["elements"]["g_cust"]
        self.assertEqual(de["lift"], "Gamma_3 Gamma_5")
        self.assertEqual(cust["lift"], "Gamma_7 Gamma_9")
        for source, target_state in (("d[+--]", "e[+++]"), ("e[+++]", "d[+--]"), ("dc[-++]", "ec[---]"), ("u[+--]", "nu[+++]")):
            self.assertEqual(de["state_map_16"][source], target_state)
        for source, target_state in (("u[+--]", "d[+--]"), ("uc[-++]", "dc[-++]"), ("e[+++]", "nu[+++]"), ("ec[---]", "nuc[---]")):
            self.assertEqual(cust["state_map_16"][source], target_state)
        self.assertEqual(de["vev_table"], obstruction.EXPECTED_VEV_TABLE["g_de"])
        self.assertEqual(cust["vev_table"], obstruction.EXPECTED_VEV_TABLE["g_cust"])
        self.assertEqual(len(de["vev_table"]), 10)
        self.assertEqual(weyl["sigma_std_16x16_entries"], [["nuc[---]", "nuc[---]", [0, 32]]])
        self.assertEqual(weyl["torus_reduction"]["determinant"], "1")
        for key in ("L1_composed_spec_Md_equals_spec_Me", "L2_composed_tan_beta_one_spec_Mu_equals_spec_Md_and_dim4_CKM_one"):
            self.assertIs(weyl["checks"][key], True)
        self.assertIn("spec(M_d) = spec(M_e)", weyl["lemma_L1"])
        self.assertIn("CKM = 1 exactly at the level of the light (dimension-4) Yukawa matrices", weyl["lemma_L2"])
        self.assertIn("K = U_d^dag P_{16bar SU(2)_L-singlet} U_d = O(v^2/M_V^2)", weyl["lemma_L2"])
        self.assertNotIn("is a diagonal phase matrix", weyl["lemma_L2"])

    def test_contract_corollaries(self) -> None:
        corollaries = self.fresh["corollaries"]
        self.assertEqual(corollaries["generation_expanded_count"], 74)
        self.assertEqual(len(corollaries["field_level_couplings"]), 26)
        self.assertEqual(corollaries["X_neutral_16bar_16_pairs"], [])
        self.assertNotIn("Phi210", corollaries["scalars_used"])
        self.assertIn("Phi210", corollaries["vectorlike_pair"]["new_scalars"])
        self.assertIn("Phi210.F.Vvbar", corollaries["vectorlike_pair"]["new_couplings"])
        self.assertIs(corollaries["vectorlike_pair"]["bare_mass_allowed"], True)

    def test_xparity_of_an_added_120(self) -> None:
        xparity = self.fresh["xparity_120"]
        sets = xparity["census"]["sigma_numbers_up_to_degree"]
        self.assertEqual(sets["4"], [0, 2])
        self.assertEqual(sets["5"], [0, 2])
        self.assertEqual(sets["6"], [0, 2, 4])
        self.assertEqual(sets["7"], [0, 2, 4])
        self.assertEqual(sets["8"], [0, 2, 4, 6])
        self.assertTrue(all(value % 2 == 0 for value in sets["11"]))
        self.assertIn(1, sets["12"])
        self.assertEqual(xparity["census"]["min_odd_sigma_degree"], 12)
        for example in xparity["census"]["odd_examples_at_min_degree"]:
            self.assertEqual(sum(int(part.split("^")[1]) if "^" in part else 1 for part in example.split()), 12)
        self.assertEqual(xparity["sm_cartan_kernel_on_120"]["rank_GFp"], 120)
        self.assertTrue(all(value == 0 for value in xparity["t_linear_covariants_nonzero_components"].values()))
        self.assertEqual(xparity["p_only_operators"]["max_abs_122_to_1522"], 0)
        self.assertGreater(xparity["p_only_operators"]["control_max_H_to_122_120"], 0)

    def test_s_structure_and_real_type(self) -> None:
        section = self.fresh["s_structure"]
        self.assertEqual(section["s_at_control_point"], "1/2")
        self.assertTrue(all(value == "1" for value in section["s_at_claimed_points"]))
        self.assertEqual(section["commutant_dimension"], 1)
        self.assertEqual(section["invariant_two_copy_form_dimension"], 3)
        self.assertIn("s = 1 iff e = 0", section["lemma"])

    def test_offq0_selection_polynomials(self) -> None:
        section = self.fresh["offq0_selection"]
        self.assertEqual(section["factors_f"], EXPECTED_FACTORS)
        self.assertLessEqual(section["compiler_binding"]["max_abs_deviation"], 1.0e-12)
        self.assertEqual(section["compiler_binding"]["rS"], "1/2")
        for key, value in section["source_types"].items():
            direction = key.split("::")[1].split("|")[0]
            sign = key.split("|H")[1]
            self.assertEqual(value, obstruction.EXPECTED_SOURCE_TYPE[(direction, sign)], key)
        for row in section["parameters"].values():
            self.assertGreaterEqual(row["min_margin"], obstruction.LATTICE_MARGIN_REQUIRED)
        self.assertEqual(section["O28_pair_types"]["re"]["-"], [])
        self.assertTrue(section["research_a3_consistency"]["consistent"])
        self.assertIn("a != 0 or w != 0", section["statement"])

    def test_fifteen_two_two_mass(self) -> None:
        section = self.fresh["fifteen_two_two_mass"]
        self.assertEqual(section["one_half_branch_real_dimension"], 120)
        self.assertEqual(section["octet_doublet_states_in_spectrum"], 64)
        self.assertIn("exactly one (15,2,2), the 126bar's", section["identification"])
        self.assertEqual(len(section["factors"]), 5)
        self.assertTrue(all("1/2" in row["roots_at_r0_0"] for row in section["factors"]))
        self.assertEqual(section["rS_dependent_units"], sorted(obstruction.RS_DEPENDENT_UNITS))

    def test_research_record_provenance(self) -> None:
        research = self.fresh["research_record"]
        self.assertEqual({name: row["sha256"] for name, row in research["files"].items()}, EXPECTED_RESEARCH_SHA)
        self.assertEqual(research["files_digest"], obstruction.RESEARCH_FILES_DIGEST)
        self.assertEqual(research["provenance_note"], obstruction.RESEARCH_PROVENANCE_NOTE)
        for entry in research["entries"].values():
            self.assertIs(entry["reproducible_from_repository"], False)
            self.assertEqual(entry["label"], "RESEARCH_RECORD")
            self.assertEqual(entry["source_json_sha256"], EXPECTED_RESEARCH_SHA[entry["source_json"]])
        entries = research["entries"]
        # The artifact rounds floats to 12 significant digits; compare the research values at that precision.
        for value, expected in (
            (entries["second_126bar_landau"]["value"]["two_loop_alpha_eq_1_GeV"], 8.124031146123272e17),
            (entries["vectorlike_reoriented_210_landau"]["value"]["one_VL_pair_at_mu_G_two_loop_alpha_eq_1_GeV"], 2.6935e18),
            (entries["forty_five_scalar_portal"]["value"]["A=BL,H=e8(tanb=1)"]["e-ec"], 6.0),
            (entries["pure_10_120_fit_vR_1p27e9"]["value"]["chi2"], 38.53685442291748),
            (entries["pure_10_120_fit_vR_1e13"]["value"]["chi2"], 43.33632992490345),
            (entries["selection120_admixture_slope"]["value"], 2.0000000429673563),
            (entries["selection120_tuned_light_1522"]["value"]["M15_over_vR_and_median_amplitude"][-1][1], 0.6543360819899953),
            (entries["portal_ckm_caveat"]["value"]["CKM_max_offdiag"]["A' witness generic H + up-type (15,2,2)"], 0.3028018114634229),
        ):
            self.assertTrue(math.isclose(value, expected, rel_tol=1.0e-11), (value, expected))
        self.assertEqual(len(research["off_orientation_splitters"]), 3)
        self.assertEqual(entries["portal_ckm_caveat"]["source_json"], "C/verify-physics/v1_spinor_indep.json")
        self.assertEqual(entries["selection120_tuned_light_1522"]["key"], "C4_tuned_15")
        self.assertEqual(entries["light_1522_no_perturbative_two_loop_root"]["value"]["v20_rho1e3_with_120H_one_complex_1522_at_10vR"]["n_roots"], 0)
        self.assertNotIn("omits the 16bar doublet currents", entries["c2_spectral_cases"]["meaning"])

    def test_headline_scope_and_verdict_texts(self) -> None:
        headline = self.fresh["headline"]
        for text in ("flavour-dead", "M_e = phase x M_d^T", "CKM = 1", "the r_S family", "O36 lambda_H member",
                     "g3_sm_pati_salam_higgs_quartic_member_v20",
                     "at the level of the light (dimension-4) Yukawa matrices",
                     "(iv) a 120 added as SOS squares with a GUT-scale (15,2,2)_120 (M15 ~ M_GUT), up to an O(r0^2)",
                     "every doublet-coupled portal (O15, O28, O38, O45_B02) makes q0 a saddle",
                     "O45_B01 has no doublet coupling (flavour-inert)",
                     "non-unitary at O(v^2/M_V^2) (dimension 6)",
                     "a tuned-light (15,2,2)_120 is outside (iv)"):
            self.assertIn(text, headline["theorem"])
        self.assertNotIn("a portal != 0 leaves the certified family because q0 becomes a saddle", headline["theorem"])
        self.assertIs(headline["checks"]["o36_quartic_member_committed_certified_0_failed"], True)
        self.assertIn("RESEARCH_RECORD", headline["caveat"])
        not_claimed = " ".join(self.fresh["scope"]["not_claimed"])
        for text in ("no loop-level flavour", "Phi-sector-only degree-2 SOS no-go", "no exclusion of the SO(10) contract",
                     "research-recorded, not re-derived here", "no gate status changes"):
            self.assertIn(text, not_claimed)
        for text in ("also split d from e", "off the certified orientation", "Landau-excluded at BM-DA1", "no gate status changes",
                     "O((v_R/M15)^2) = O(r0^2)", "a tuned-light (15,2,2)_120, which SOS squares allow, gives O(1) splitting",
                     "The 126bar's (15,2,2) (not the 120's) has m^2 = p^2/2", "(dimension-6 non-unitarity",
                     "O45_B01 has no doublet coupling (flavour-inert)"):
            self.assertIn(text, self.fresh["verdict"])
        self.assertNotIn("a 120_H added as SOS squares up to O(r0^2)", self.fresh["verdict"])
        for text in ("a tuned-light (15,2,2)_120, which SOS squares allow", "dimension-6 non-unitarity"):
            self.assertIn(text, not_claimed)

    # ------------------------------------------------------------------ fail-closed mutations

    def test_mutation_45_BL_vev_in_charged_sector_breaks_L1(self) -> None:
        vevs = {**obstruction.default_charged_sector_vevs(), "45_B-L": dict(obstruction.FORTY_FIVE_BL)}
        report = self._mutated(weyl_lemmas=obstruction.weyl_section(vevs))
        self._assert_fails_closed(report, "weyl_lemmas.g_de_fixes_every_charged_sector_vev_bilinear_exactly")
        self.assertIs(report["checks"]["weyl_lemmas.L1_composed_spec_Md_equals_spec_Me"], False)
        vevs = {**obstruction.default_charged_sector_vevs(), "210_(15,1,1)": dict(obstruction.PHI_A)}
        report = self._mutated(weyl_lemmas=obstruction.weyl_section(vevs))
        self._assert_fails_closed(report, "weyl_lemmas.g_de_fixes_every_charged_sector_vev_bilinear_exactly")

    def test_mutation_120_with_X_minus_3_breaks_xparity_pins(self) -> None:
        report = self._mutated(xparity_120=obstruction.xparity_section(t_charge=-3))
        self._assert_fails_closed(report, "xparity_120.F_F_120_allowed_only_for_X_minus_2_Z17_15")
        for check in ("Z17_equals_X_mod_17_for_T", "sigma_numbers_pinned_degrees_4_to_8", "minimal_odd_sigma_degree_is_12",
                      "research_xparity_sets_reproduced"):
            # The census and comparator themselves fail, not only the charge arithmetic.
            self.assertIs(report["checks"][f"xparity_120.{check}"], False, check)

    def test_mutation_conjugate_mixing_at_tan_beta_ne_1_breaks_s_equals_1(self) -> None:
        points = list(obstruction.DEFAULT_S_POINTS) + [obstruction.CONTROL_S_POINT]
        report = self._mutated(s_structure=obstruction.s_structure_section(points))
        self._assert_fails_closed(report, "s_structure.s_equals_one_on_the_claimed_point_set")

    def test_mutation_lattice_coefficient_perturbed_breaks_identity(self) -> None:
        section = obstruction.offq0_section(lattice_perturbation=("re::O15_B01_Phi_Hdag_Sigma", 1))
        report = self._mutated(offq0_selection=section)
        self._assert_fails_closed(report, "offq0_selection.polynomial_identity_verified_at_extra_points")

    def test_mutation_corrupted_g6_level_breaks_binding(self) -> None:
        g6 = json.loads(obstruction.G6_TREE_JSON.read_text(encoding="utf-8"))
        corrupted = copy.deepcopy(g6)
        for row in corrupted["parametric_spectrum"]["factors"]:
            if row["polynomial"] == "lam - (1/2)":
                row["polynomial"] = "lam - (1/3)"
        report = self._mutated(fifteen_two_two_mass=obstruction.mass_section(corrupted))
        self._assert_fails_closed(report, "fifteen_two_two_mass.fifteen_two_two_levels_bound_to_committed_g6_factors")

    def test_mutation_tampered_research_sha_breaks_provenance(self) -> None:
        tampered = dict(obstruction.RESEARCH_FILES)
        script, sha = tampered["C/c2_weyl_lemmas.json"]
        tampered["C/c2_weyl_lemmas.json"] = (script, ("0" if sha[0] != "0" else "1") + sha[1:])
        report = self._mutated(research_record=obstruction.research_section(tampered))
        self._assert_fails_closed(report, "research_record.research_files_digest_pinned")
        self.assertIs(report["checks"]["research_record.research_entries_labelled_with_provenance"], False)

    def test_mutation_check_count_is_enforced(self) -> None:
        extra = copy.deepcopy(self.sections["s_structure"])
        extra["checks"]["an_unpinned_extra_check"] = True
        report = self._mutated(s_structure=extra)
        self.assertEqual(report["n_checks"], EXPECTED_N_CHECKS + 1)
        self.assertEqual(report["status"], EXPECTED_INCOMPLETE)
        self.assertIn(f"check_count_{EXPECTED_N_CHECKS + 1}_expected_{EXPECTED_N_CHECKS}", report["failures"])
        self.assertFalse(obstruction.report_passes(report))
        self._assert_write_refused(report)
        fewer = copy.deepcopy(self.sections["s_structure"])
        fewer["checks"].pop("so4_commutant_on_real_22_is_one_dimensional")
        report = self._mutated(s_structure=fewer)
        self.assertEqual(report["n_checks"], EXPECTED_N_CHECKS - 1)
        self.assertFalse(obstruction.report_passes(report))
        self._assert_write_refused(report)

    def test_mutation_failed_quartic_member_report_breaks_headline(self) -> None:
        committed = json.loads(obstruction.QUARTIC_MEMBER_JSON.read_text(encoding="utf-8"))
        self.assertEqual(committed["status"], obstruction.QUARTIC_MEMBER_STATUS)
        failed = copy.deepcopy(committed)
        failed["n_failed"] = 1
        failed["flags"]["member_theorem_claimed"] = False
        report = obstruction.assemble_report(self.sections, quartic_report=failed)
        self._assert_fails_closed(report, "headline.o36_quartic_member_committed_certified_0_failed")
        report = obstruction.assemble_report(self.sections, quartic_report={})
        self._assert_fails_closed(report, "headline.o36_quartic_member_committed_certified_0_failed")

    def test_mutation_g8_v2_text_regression(self) -> None:
        # The committed G8 v2 artifact carries the corrected Route B line; status and 157 checks are unchanged.
        committed = json.loads(g8_v2.OUT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(committed["status"], g8_v2.STATUS_RECORDED)
        self.assertEqual(committed["n_checks"], 157)
        self.assertEqual(committed["n_failed"], 0)
        self.assertEqual(committed["G8_status"], "OPEN")
        texts = (committed["routes"]["B"], committed["verdict"], " ".join(committed["scope"]["not_claimed"]), g8_v2.__doc__)
        for text in texts:
            self.assertNotIn("vectorlike matter were not analysed", text)
            self.assertIn("also split d from e", text)
            self.assertIn("off the certified orientation", text)
            self.assertIn("g8_sm_pati_salam_structural_obstruction_v20", text)
        # An uncorrected G8 v2 report makes the headline binding fail closed.
        regressed = copy.deepcopy(committed)
        regressed["routes"]["B"] = regressed["routes"]["B"].replace(
            "also split d from e", "were not analysed"
        ) + " a second 126bar_H, a new B-L-breaking scalar vev and vectorlike matter were not analysed"
        report = obstruction.assemble_report(self.sections, g8_report=regressed)
        self._assert_fails_closed(report, "headline.g8_v2_route_b_text_corrected")


if __name__ == "__main__":
    unittest.main()
