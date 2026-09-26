#!/usr/bin/env python3
"""Tests for the Route C flavour no-go of the SM Pati-Salam G3 witness branch (G8, v20).

setUpClass builds one fresh report (census, exact Hessians at eight r0 values, spinor algebra, one-loop running,
the five H-linear portals on the full H block with exact Schur data at five r0 values, seesaw scan; one to two
minutes) and compares it with the committed artifact: exact leaves must match exactly, the float diagnostics (data
comparison, O28 and portal-set repository bounds, eigenvalue-based colour radii, seesaw scan) only within declared
tolerances.  The mutation tests call the section functions with one changed input each (model text, benchmark
coefficients, census rows, doublet vev, data, repository scales, vectorlike couplings, upstream reports, pinned
closed form, portal couplings, triplet couplings, hypercharge sources, Yukawa content, colour bracket) and require
the corresponding checks to fail closed.
"""
from __future__ import annotations

import copy
import json
import math
import unittest
from fractions import Fraction
from typing import Any
from unittest import mock

import sympy

import g3_candidate_physical_target_audit_v20 as target
import g8_sm_pati_salam_flavour_nogo_v20 as nogo

TIMING_KEYS = {"runtime_seconds"}
O28_RE = "re::O28_B01_unique_Hdag_Sigma2_Sigmadag"
O15 = "O15_B01_Phi_Hdag_Sigma"
O28 = "O28_B01_unique_Hdag_Sigma2_Sigmadag"
O38 = "O38_B01_Phi_Hdag_Sigmadag"
O45_B01 = "O45_B01_Phi2_Hdag_Sigma_210_1050"
O45_B02 = "O45_B02_Phi2_Hdag_Sigma_210_1050"
TWO_HDM = "candidate_PS_content_with_2HDM_below_M_I"
# Per-direction row entries computed with a float eigensolver (compared within tolerance, not exactly).
EIGEN_FLOAT_KEYS = (
    "colour_radius",
    "colour_radius_outer_bound_any_combination",
    "colour_radius_with_O06_compensation_upper",
    "doublet_compensation_eps_at_abs_c_4pi",
)


def _strip_timing(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _strip_timing(item) for key, item in value.items() if key not in TIMING_KEYS}
    if isinstance(value, list):
        return [_strip_timing(item) for item in value]
    return value


def _split_float_sections(report: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    report = copy.deepcopy(_strip_timing(report))
    data = report.pop("data")
    seesaw = report.pop("seesaw")
    bounds = report["O28_fix"].pop("repository_r0_bounds")
    portals = report["H_linear_portals"]
    portal_bounds = portals.pop("repository_r0_bounds")
    portal_theta = portals.pop("theta_up_type_max_box_at_physical_r0")
    eigen = {
        direction: [{key: row.pop(key) for key in EIGEN_FLOAT_KEYS} for row in rows]
        for direction, rows in portals["per_direction"].items()
    }
    report.pop("verdict")  # formats float minima; checked separately
    return (
        report,
        {"data": data, "bounds": bounds, "portal_bounds": portal_bounds, "portal_theta": portal_theta, "eigen": eigen},
        {"seesaw": seesaw},
    )


class G8FlavourNogoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.committed = json.loads(nogo.OUT_JSON.read_text(encoding="utf-8"))
        cls.fresh = nogo.json_roundtrip(nogo.build_report())

    # ------------------------------------------------------------------
    # Status, checks and flags.
    # ------------------------------------------------------------------

    def test_all_checks_pass_and_route_c_is_recorded(self) -> None:
        for report in (self.committed, self.fresh):
            self.assertEqual(report["n_failed"], 0, report["failures"])
            self.assertEqual(report["n_checks"], len(report["checks"]))
            self.assertTrue(all(report["checks"].values()))
            self.assertEqual(report["status"], nogo.STATUS_RECORDED)
            self.assertEqual(report["overall_state"], nogo.OVERALL_STATE_RECORDED)
            self.assertEqual(report["G8_status"], "OPEN")
            self.assertEqual(report["model_contract_id"], "gauged_u1x_phi17_v20")
            flags = report["flags"]
            for name in (
                "witness_branch_flavour_excluded_at_renormalizable_tree_level",
                "light_doublet_pure_10H_exact",
                "no_induced_heavy_doublet_vev_at_tree_level",
                "flavour_relations_exact",
                "data_exclusion_many_sigma",
                "O28_alone_fix_excluded",
                "O28_portal_breaks_SOS27_certificate",
                "every_doublet_coupled_portal_breaks_SOS27_certificate",
                "colour_stable_region_computed_on_full_H_block",
                "O28_colour_radius_below_4pi_at_some_repository_r0",
                "O15_frees_tan_beta_only_beyond_its_colour_radius",
                "O45_B02_frees_tan_beta_inside_colour_stable_region",
                "portal_induced_126bar_vev_up_type_only_exact",
                "M_e_equals_phase_M_d_transpose_for_every_portal_combination",
                "H_linear_portal_fix_excluded_at_anchor_chain_r0",
                "H_linear_portal_fix_excluded_at_every_repository_r0",
                "seesaw_generic_nonperturbative_if_MD_equals_Mu_data",
                "route_C_recorded",
            ):
                self.assertIs(flags[name], True, name)
            for name in (
                "G8_closed",
                "falsifies_G3_G5_scalar_vacuum_certificates",
                "falsifies_so10_contract",
                "seesaw_load_bearing",
                # Findings the portal-set analysis does NOT support (recorded, not claimed).
                "O28_alone_t_b_bound_survives_other_portals",
                "O28_alone_b_tau_repairable",
            ):
                self.assertIs(flags[name], False, name)
            for name in ("O28_in_contract_fix_excluded", "seesaw_generic_nonperturbative"):
                self.assertNotIn(name, flags)
            self.assertEqual(report["n_checks"], 103)
            self.assertEqual(set(report["routes"]), {"A", "B", "C"})
            self.assertIn("DOWN-type", report["routes"]["A"])

    def test_status_strings(self) -> None:
        self.assertTrue(nogo.STATUS_RECORDED.endswith("__G8_OPEN"))
        self.assertTrue(nogo.STATUS_INCOMPLETE.endswith("__G8_OPEN"))
        self.assertNotEqual(nogo.STATUS_RECORDED, nogo.STATUS_INCOMPLETE)

    def test_committed_artifact_matches_fresh_report(self) -> None:
        committed_exact, committed_float, committed_scan = _split_float_sections(self.committed)
        fresh_exact, fresh_float, fresh_scan = _split_float_sections(self.fresh)
        self.assertEqual(target.report_mismatches(committed_exact, fresh_exact), [])
        self.assertEqual(target.report_mismatches(committed_float, fresh_float, "float", rel_tol=1.0e-6, abs_tol=1.0e-9), [])
        self.assertEqual(target.report_mismatches(committed_scan, fresh_scan, "scan", rel_tol=5.0e-2, abs_tol=1.0e-6), [])

    def test_committed_markdown_regenerates(self) -> None:
        expected = nogo._markdown(self.committed).replace("\r\n", "\n")
        self.assertEqual(nogo.OUT_MD.read_text(encoding="utf-8").replace("\r\n", "\n"), expected)

    def test_tampered_artifact_is_detected(self) -> None:
        tampered = copy.deepcopy(self.committed)
        tampered["checks"]["light_doublet.H_block_decoupled_at_every_r0"] = False
        committed_exact, _, _ = _split_float_sections(self.committed)
        tampered_exact, _, _ = _split_float_sections(tampered)
        self.assertNotEqual(target.report_mismatches(committed_exact, tampered_exact), [])

    # ------------------------------------------------------------------
    # Exact content.
    # ------------------------------------------------------------------

    def test_light_doublet_is_pure_10h(self) -> None:
        section = self.fresh["light_doublet"]
        self.assertEqual(tuple(section["H_linear_directions"]), nogo.EXPECTED_H_LINEAR_DIRECTIONS)
        self.assertEqual(len(section["H_linear_parameters"]), 10)
        self.assertEqual(tuple(section["nonzero_H_quadratic_parameters"]), nogo.EXPECTED_NONZERO_H_QUADRATIC)
        self.assertEqual(len(section["exact_hessian_audits"]), 4)
        for audit in section["exact_hessian_audits"]:
            for key in ("gradient_zero", "H_rows_vanish_outside_H_block", "H_block_matches_exact_formula", "Re_H_6_9_exact_null_vectors"):
                self.assertIs(audit[key], True, (audit["r0"], key))
        self.assertIn(str(nogo.physical_r0()), [audit["r0"] for audit in section["exact_hessian_audits"]])

    def test_spinor_clebsches(self) -> None:
        spinor = self.fresh["spinor"]
        self.assertEqual(len(spinor["clebsch_at_vev"]), 8)
        self.assertEqual(set(spinor["clebsch_moduli"].values()), {"a**2 + b**2"})
        self.assertEqual(spinor["sigma_std_bilinear_entries"], [["nuc[---]", "nuc[---]", [0, 32]]])
        for row in spinor["fifteen_two_two"].values():
            self.assertEqual(row["lepton_over_quark_relative_clebsch"], "-3")
        self.assertTrue(spinor["tensor_products"]["decomposition_proved"])
        blocks = spinor["tensor_products"]["blocks"]
        self.assertEqual([blocks["16x16"][str(k)]["rank_lower_bound_GFp"] for k in range(6)], [0, 10, 0, 120, 0, 126])
        self.assertEqual([blocks["16x16bar"][str(k)]["rank_lower_bound_GFp"] for k in range(6)], [1, 0, 45, 0, 210, 0])

    def test_contract_enumeration(self) -> None:
        contract = self.fresh["contract"]
        self.assertEqual(contract["conj_H10_yukawas"], [])
        self.assertEqual(set(contract["X1_sixteens"]), {"F", "P", "R"})
        self.assertIn("H10.F.F", contract["H10_yukawas"])
        self.assertIn("Delta126bar.F.F", contract["Delta126bar_yukawas"])
        self.assertTrue(all("Phi17" in row or "S" in row.split(".")[0] for row in contract["vectorlike_mass_couplings"]))
        self.assertEqual(contract["sixteenbar_pair_couplings"], ["conj[Delta126bar].Pbar.Rbar", "conj[H10].Pbar.Rbar"])
        self.assertEqual(contract["chirality"], {"n16": 11, "n16bar": 8, "net": 3})

    def test_o28_exact_closed_form(self) -> None:
        o28 = self.fresh["O28_fix"]
        closed = o28["closed_form"]
        self.assertEqual(closed["R_theta_sigma_squared_over_c2_r4"], "7962624*(13*r**2 + 6)**2/(13*r**4 + 12*r**2 + 36)**2")
        self.assertEqual(closed["light_mass_shift_over_c2_r4"], "-663552*(13*r**2 + 6)/(13*r**4 + 12*r**2 + 36)")
        self.assertEqual(closed["R_at_zero"], "221184")
        first = o28["exact_rows"][0]
        self.assertEqual(first["r0"], "1/5")
        self.assertEqual(first["theta_sigma_squared_over_c2_r0_4"], "132224348160000/520432969")
        self.assertEqual(first["light_mass_shift_over_c2_r0_4"], "-2703974400/22813")
        for row in o28["exact_rows"]:
            self.assertTrue(row["closed_form_matches"])
            self.assertTrue(row["saddle_for_every_c_nonzero"])
        self.assertLess(o28["theta_max_at_anchor_abs_c_4pi"], 3.0e-5)
        # JSON keeps 12 significant digits, so ratios of stored floats agree to ~1e-11.
        self.assertAlmostEqual(o28["theta_max_at_anchor_abs_c_4pi_any_tan_beta"] / o28["theta_max_at_anchor_abs_c_4pi"], math.sqrt(2.0), places=9)
        self.assertEqual(set(o28["repository_r0_bounds"]), set(nogo.EXPECTED_REPOSITORY_SCALES))
        self.assertEqual(len(o28["exact_rows"]), 8)
        for key, row in o28["repository_r0_bounds"].items():
            self.assertGreater(row["t_b_split_requires_Y_F_at_least"], nogo.PORTAL_BOX)
            self.assertNotIn("t_b_split_requires_Y126_at_least", row)
            self.assertNotIn("b_tau_split_requires_Y_F_at_least", row)  # alpha_d = 0 exactly: no b-tau requirement
            self.assertIs(row["induced_126bar_vev_up_type_only"], True)
            self.assertLessEqual(row["abs_c_max_colour_stable"], nogo.PORTAL_BOX + 1.0e-9)  # JSON keeps 12 digits
            self.assertAlmostEqual(row["abs_c_max_colour_stable"], min(nogo.PORTAL_BOX, row["colour_radius"]), places=9, msg=key)
        two_hdm = o28["repository_r0_bounds"][TWO_HDM]
        self.assertLess(two_hdm["colour_radius"], nogo.PORTAL_BOX)  # |c_O28| = 4 pi lies beyond the colour-stable range
        self.assertAlmostEqual(two_hdm["colour_radius"], 4.537, delta=0.01)
        self.assertEqual(o28["findings"]["colour_radius_below_4pi_at"], [TWO_HDM])
        self.assertIs(o28["findings"]["b_tau_repairable_by_O28"], False)
        self.assertIn("Y_F", o28["mirsky_argument"])
        self.assertIn("alpha_d = 0", o28["mirsky_argument"])
        self.assertIn("conservative for the no-go", o28["coefficient_box_note"])
        self.assertIn("O(c^2)", o28["sos27_statement"])

    def test_all_h_linear_portals(self) -> None:
        portals = self.fresh["H_linear_portals"]
        self.assertTrue(all(portals["checks"].values()))
        patterns = portals["lattice_binding"]["patterns"]
        expected = {
            O15: ("Phi210", 1, ["-1/2", "1/2"], {"Phi210": 1, "Sigma126bar": 0}, "+"),
            O28: ("Sigma126bar", 2, ["-192", "192"], {"Sigma126bar": 2}, "+"),
            O38: ("Phi210", 2, ["-1/2", "1/2"], {"Phi210": 2, "Sigma126bar": 1}, "-"),
            O45_B01: ([], 0, [], {"Phi210": 1}, None),
            O45_B02: ("Phi210", 1, ["-1", "1"], {"Phi210": 1}, "+"),
        }
        for direction, (block, power, entries, triplets, source) in expected.items():
            for prefix in ("re", "im"):
                row = patterns[f"{prefix}::{direction}"]
                self.assertEqual((row["doublet_column_block"], row["r0_power"], row["doublet_column_entries"]), (block, power, entries))
                self.assertEqual({name: value["r0_power"] for name, value in row["triplet_column_blocks"].items()}, triplets)
                self.assertEqual(row["doublet_source_hypercharge"], source)
                self.assertIs(row["H_by_H_and_nonH_by_nonH_blocks_zero"], True)
                self.assertIs(row["bound"], True)
        self.assertEqual(patterns[f"re::{O15}"]["triplet_column_blocks"]["Sigma126bar"]["entries"], ["-2", "2"])
        per_direction = portals["per_direction"]
        self.assertEqual(set(per_direction), set(nogo.EXPECTED_H_LINEAR_DIRECTIONS))
        for direction, rows in per_direction.items():
            self.assertEqual(len(rows), 5)  # physical member + the four repository r0
            self.assertEqual(rows[0]["r0"], str(nogo.physical_r0()))
            for row in rows:
                self.assertIs(row["colour_triplet_coupling"], True)
                self.assertIs(row["colour_radius_exact_bracket"], True)
                self.assertEqual(row["triplet_heavy_component_sizes"], [14])
                self.assertIs(row["triplet_schur_phase_independent"], True)
                self.assertIs(row["doublet_schur_phase_independent"], True)
                self.assertIs(row["sigma_admixture_gram_equals_2_theta2_times_source_projector"], True)
                if direction == O45_B01:
                    self.assertIs(row["doublet_coupling"], False)
                    self.assertEqual(row["theta_sigma_squared_per_unit_c"], "0")
                    continue
                self.assertIs(row["saddle_for_every_c_nonzero"], True)
                self.assertEqual(row["heavy_component_sizes"], [14])
                self.assertIs(row["induced_126bar_vev_up_type_only"], True)
                self.assertIs(row["induced_lepton_over_quark_modulus_3"], True)
                self.assertEqual(row["induced_126bar_yukawa_pairs"], ["d-uc", "e-nuc", "nu-nuc", "u-uc"])
                self.assertAlmostEqual(
                    row["theta_sigma_max_over_tan_beta_per_unit_c_float"] / row["theta_sigma_per_unit_c_float"], math.sqrt(2.0), places=9
                )
                self.assertGreaterEqual(row["colour_radius_outer_bound_any_combination"], row["colour_radius"])
        anchor = {direction: rows[0] for direction, rows in per_direction.items()}
        self.assertAlmostEqual(anchor[O28]["theta_sigma_over_c_r0_2_float"], 470.302, places=3)
        self.assertAlmostEqual(anchor[O15]["theta_sigma_over_c_r0_2_float"], 1.63299, places=4)
        self.assertAlmostEqual(anchor[O45_B02]["theta_sigma_over_c_r0_2_float"], 3.26599, places=4)
        r0 = float(Fraction(anchor[O38]["r0"]))
        self.assertAlmostEqual(anchor[O38]["theta_sigma_over_c_r0_2_float"] / r0, 1.63299, places=4)
        for rows in (per_direction[O15],):
            for row in rows:
                self.assertAlmostEqual(row["colour_radius"], math.sqrt(5.0 / 8.0), delta=1.0e-5)  # r0-independent
        bounds = portals["repository_r0_bounds"]
        self.assertEqual(set(bounds), set(nogo.EXPECTED_REPOSITORY_SCALES))
        for key, row in bounds.items():
            self.assertLess(row["theta_up_type_max_box_triangle_bound"], nogo.PORTAL_THETA_THRESHOLD)
            self.assertLessEqual(row["theta_up_type_max_colour_stable_triangle_bound"], row["theta_up_type_max_box_triangle_bound"])
            self.assertGreater(row["O28_share_of_box_bound"], 0.98)
            self.assertEqual(row["tan_beta_reaches_m_t_over_m_b_in_box_with"], [O15, O45_B02], key)
            self.assertEqual(row["tan_beta_reaches_m_t_over_m_b_colour_stable_with"], [O45_B02], key)
            self.assertLess(row["tan_beta_scan_colour_stable"][O15]["tan_beta_max_over_scan"], row["m_t_over_m_b_at_M_I"])
            self.assertLess(row["tan_beta_scan_box"][O28]["tan_beta_max_over_scan"], 4.0)
            self.assertIs(row["induced_126bar_vev_up_type_only_every_direction"], True)
            self.assertGreaterEqual(row["portal_immune_tests_min_pull_conservative_sigma"], nogo.NOGO_PULL_THRESHOLD)
            self.assertIs(row["portal_fix_excluded"], True)
            self.assertLess(row["colour_radius"][O15], 1.0)
            for direction in (O38, O45_B01, O45_B02):
                self.assertGreater(row["colour_radius"][direction], nogo.PORTAL_BOX)
        self.assertLess(bounds[TWO_HDM]["colour_radius"][O28], nogo.PORTAL_BOX)
        findings = portals["findings"]
        self.assertIs(findings["portal_fix_excluded_at_anchor_chain_r0"], True)
        self.assertIs(findings["portal_fix_excluded_at_every_repository_r0"], True)
        self.assertEqual(findings["portal_fix_not_excluded_at"], [])
        self.assertIs(findings["down_type_and_charged_lepton_masses_untouched_by_every_portal_combination"], True)
        self.assertIs(findings["t_b_bound_survives_portal_set_at_every_repository_r0"], False)
        self.assertIs(findings["O15_frees_tan_beta_only_beyond_its_colour_radius"], True)
        self.assertNotIn("NOT excluded", self.fresh["verdict"])
        self.assertIn("no in-contract H-linear portal repair of the flavour sector survives at any repository r0", self.fresh["verdict"])
        self.assertIn("O(c^2)", portals["scope_note"])
        self.assertIn("Haynsworth", portals["scope_note"])
        self.assertIn("new G3 certificate", portals["colour_stable_region"]["compensation"])

    def test_induced_vev_lemma_and_vectorlike_rank(self) -> None:
        section = self.fresh["light_doublet"]
        self.assertEqual(section["H_degree_histogram"], {"0": 27, "1": 5, "2": 10, "4": 2})
        self.assertIs(section["checks"]["no_H_degree_3_live_direction"], True)
        self.assertIs(section["checks"]["potential_even_in_H_on_the_witness"], True)
        certificate = self.fresh["contract"]["vectorlike_rank_certificate"]
        self.assertEqual(certificate["rank_at_integer_couplings"], 8)
        self.assertEqual(certificate["kernel_dimension"], 3)
        self.assertEqual(certificate["kernel_support_fields"], ["F", "P", "Q", "R"])
        self.assertIs(self.fresh["contract"]["checks"]["vectorlike_pattern_generic_rank_8"], True)
        proved = " ".join(self.fresh["scope"]["proved_exactly"])
        self.assertIn("no heavy doublet", proved)
        self.assertIn("generic rank 8", proved)
        self.assertIn("matched exactly by the first-order solve at 8 r0 values", proved)
        self.assertIn("M_e = phase x M_d^T for every portal combination", proved)
        self.assertNotIn("exact at five r0 values", proved)

    def test_seesaw_premise_is_labelled(self) -> None:
        seesaw = self.fresh["seesaw"]
        self.assertIn("M_D = M_u(data) is the generic SO(10) premise", seesaw["assumptions"])
        for row in seesaw["rows"].values():
            self.assertLess(row["generic_Y_R_if_MD_has_charged_lepton_singular_values"], row["generic_Y_R"] / 1000.0)
        at_1e12 = seesaw["rows"]["1e+12 GeV"]["generic_Y_R_if_MD_has_charged_lepton_singular_values"]
        self.assertAlmostEqual(at_1e12, 0.063, delta=0.01)

    def test_data_exclusion(self) -> None:
        data = self.fresh["data"]
        self.assertGreaterEqual(data["minimum_load_bearing_pull_raw_sigma"], nogo.NOGO_PULL_THRESHOLD)
        self.assertGreaterEqual(data["minimum_load_bearing_pull_conservative_sigma"], nogo.NOGO_PULL_THRESHOLD)
        vus = next(row for row in data["tests_scale_free"] if row["test"] == "|V_us|")
        self.assertAlmostEqual(vus["pull_raw_sigma"], 0.2243 / 0.0008, places=6)

    # ------------------------------------------------------------------
    # Fail-closed mutations.
    # ------------------------------------------------------------------

    def _model_text(self) -> str:
        return nogo.MODEL_FILE.read_text(encoding="utf-8")

    def test_mutation_conjugate_10h_yukawa_is_rejected(self) -> None:
        text = self._model_text().replace("Y10 F.F.H10", "Y10 F.F.conj[H10]")
        checks = nogo.contract_section(text)["checks"]
        self.assertFalse(checks["declared_terms_U1X_neutral"])
        self.assertFalse(checks["declared_yukawas_subset_of_allowed"])

    def test_mutation_second_10h_breaks_the_premise(self) -> None:
        extra = "ScalarFields[[6]] = {H10b,         1, h10b,          10,   2, Exp[2*Pi*I*2/17]};\n"
        text = self._model_text().replace("(* The 210 is a real SO(10) representation. *)", extra + "(* The 210 is a real SO(10) representation. *)")
        section = nogo.contract_section(text)
        self.assertIn("conj[H10b].F.F", {row["coupling"] for row in section["allowed_renormalizable_fermion_couplings"]})
        self.assertFalse(section["checks"]["sixteen_sixteen_scalars_only_H10_and_Delta126bar"])
        self.assertFalse(section["checks"]["model_fields_parsed"])

    def test_mutation_120h_breaks_the_premise(self) -> None:
        extra = "ScalarFields[[6]] = {Sigma120,     1, sig120,       120,  -2, Exp[2*Pi*I*15/17]};\n"
        text = self._model_text().replace("(* The 210 is a real SO(10) representation. *)", extra + "(* The 210 is a real SO(10) representation. *)")
        checks = nogo.contract_section(text)["checks"]
        self.assertFalse(checks["no_120_scalar_in_contract"])
        self.assertFalse(checks["sixteen_sixteen_scalars_only_H10_and_Delta126bar"])

    def test_mutation_portal_on_fails_closed(self) -> None:
        checks = nogo.portal_section({O28_RE: Fraction(1)}, r0_values=[Fraction(1, 5)])["checks"]
        self.assertFalse(checks["H_linear_parameters_zero_in_benchmark"])
        self.assertFalse(checks["H_linear_parameters_zero_for_all_r0_x0_symbolic"])
        self.assertFalse(checks["binding_unit_coverage_complete_at_every_r0"])

    def test_mutation_o06_retune_breaks_the_exact_h_block(self) -> None:
        o06 = "lambda::O06_B01_Hdag_H_norm"
        value = nogo.candidate.candidate_coefficients()[o06] + Fraction(1, 2500)
        checks = nogo.portal_section({o06: value}, r0_values=[Fraction(1, 5)])["checks"]
        self.assertFalse(checks["H_block_equals_exact_formula_at_every_r0"])
        self.assertFalse(checks["Re_H_6_9_exact_null_vectors_at_every_r0"])
        self.assertFalse(checks["my_exact_hessian_reproduces_certified_benchmark_hessian"])

    def test_mutation_non_real_doublet_breaks_tan_beta_one(self) -> None:
        vev = {8: nogo.A_SYMBOL, 9: sympy.I * nogo.B_SYMBOL}
        spinor = nogo.spinor_section(vev)
        self.assertFalse(spinor["checks"]["equal_5_5bar_components_tan_beta_one"])
        self.assertFalse(spinor["checks"]["clebsch_moduli_equal_a2_plus_b2"])
        structure = nogo.flavour_structure_section(spinor)
        self.assertFalse(structure["checks"]["MuMu_dagger_equals_MdMd_dagger"])

    def test_mutation_data_without_mixing_fails_closed(self) -> None:
        data = copy.deepcopy(nogo.DATA)
        for key in ("V_us", "V_cb", "V_ub"):
            data["ckm_moduli"][key]["value"] = 1.0e-4
        checks = nogo.data_section(data)["checks"]
        self.assertFalse(checks["every_load_bearing_test_excluded_raw_at_threshold"])
        self.assertFalse(checks["every_load_bearing_test_excluded_conservative_at_threshold"])

    def test_mutation_down_lepton_data_breaks_the_portal_no_go(self) -> None:
        """If the down-quark and charged-lepton ratios agreed with M_e = phase x M_d^T, the portal no-go must not hold."""
        comparison = copy.deepcopy(self.fresh["data"])
        for row in comparison["tests_scale_free"]:
            if row["test"] == "(m_s/m_d)/(m_mu/m_e)":
                row["pull_raw_sigma"] = row["pull_conservative_sigma"] = 0.5
        section = nogo.portals_section(nogo.DATA, comparison=comparison)
        self.assertFalse(section["checks"]["portal_immune_tests_excluded_at_every_repository_r0"])
        self.assertFalse(section["findings"]["portal_fix_excluded_at_every_repository_r0"])
        self.assertEqual(section["findings"]["portal_fix_not_excluded_at"], sorted(nogo.EXPECTED_REPOSITORY_SCALES))

    def test_mutation_upstream_reports_fail_closed(self) -> None:
        cand = json.loads(nogo.CANDIDATE_JSON.read_text(encoding="utf-8"))
        hess = json.loads(nogo.EXACT_HESSIAN_JSON.read_text(encoding="utf-8"))
        cand["checks"]["H_linear_portals_are_zero"] = False
        hess["n_failed"] = 1
        checks = nogo.upstream_section(cand, hess)["checks"]
        self.assertFalse(checks["candidate_H_linear_portals_are_zero"])
        self.assertFalse(checks["exact_hessian_certified"])

    def test_mutation_pinned_closed_form_fails_closed(self) -> None:
        lattice = nogo.o28_lattice_binding()["_integer"]
        with mock.patch.object(nogo, "O28_R_NUMERATOR", "7962624*(13*r**2 + 7)**2"):
            closed = nogo.o28_closed_form(lattice)
        self.assertFalse(closed["matches_pinned_closed_form"])

    def test_mutation_missing_repository_scales_fail_closed(self) -> None:
        """Without the candidate's one-loop RG solutions every 'every repository r0' check must fail by name, never pass
        over an empty set or crash."""
        self.assertEqual(nogo.repository_scales({}), {})
        self.assertEqual(nogo.run_sm_masses([]), {})
        partial = dict(list(nogo.repository_scales().items())[:3])
        for scales in ({}, partial):
            data_checks = nogo.data_section(nogo.DATA, scales)["checks"]
            self.assertFalse(data_checks["repository_M_I_rows_present"])
            o28_checks = nogo.o28_section(nogo.DATA, scales)["checks"]
            self.assertFalse(o28_checks["repository_scales_present"])
            portal_checks = nogo.portals_section(nogo.DATA, scales)["checks"]
            self.assertFalse(portal_checks["repository_scales_present"])
            self.assertFalse(portal_checks["general_solver_reproduces_O28_alone_exactly"])  # no O28 section passed
        empty_o28 = nogo.o28_section(nogo.DATA, {})["checks"]
        self.assertFalse(empty_o28["theta_max_small_at_every_repository_r0"])
        self.assertFalse(empty_o28["t_b_repair_nonperturbative_at_every_repository_r0"])
        self.assertFalse(empty_o28["admixture_up_type_only_at_every_repository_r0"])
        empty_portals = nogo.portals_section(nogo.DATA, {})
        self.assertFalse(empty_portals["checks"]["every_H_linear_portal_theta_below_1e-3_at_every_repository_r0"])
        self.assertFalse(empty_portals["checks"]["portal_immune_tests_excluded_at_every_repository_r0"])
        self.assertFalse(empty_portals["findings"]["portal_fix_excluded_at_every_repository_r0"])

    def test_mutation_vectorlike_pattern_rank_drop_is_detected(self) -> None:
        fields = nogo.parse_model(self._model_text())["fields"]
        couplings = [
            {"fermions": row.split(".")[1:]} for row in self.fresh["contract"]["vectorlike_mass_couplings"]
        ]
        full = nogo.vectorlike_rank_certificate(fields, couplings)
        self.assertEqual(full["rank_at_integer_couplings"], 8)
        without_spectators = [row for row in couplings if "SpecB" not in row["fermions"]]
        self.assertEqual(nogo.vectorlike_rank_certificate(fields, without_spectators)["rank_at_integer_couplings"], 3)
        only_pbar = [row for row in couplings if "Pbar" in row["fermions"] or "SpecB" in row["fermions"]]
        self.assertEqual(nogo.vectorlike_rank_certificate(fields, only_pbar)["rank_at_integer_couplings"], 6)

    def test_mutation_h_degree_three_direction_breaks_the_even_potential(self) -> None:
        rows = nogo.census_rows()
        fake = dict(rows[0], direction_id="O99_B01_fake_H3", H_degree=3, parameters=["re::O99_B01_fake_H3"])
        with mock.patch.object(nogo, "census_rows", return_value=(*rows, fake)):
            checks = nogo.portal_section(r0_values=[Fraction(1, 5)])["checks"]
        self.assertFalse(checks["no_H_degree_3_live_direction"])
        self.assertFalse(checks["potential_even_in_H_on_the_witness"])

    def test_mutation_portal_pins_fail_closed(self) -> None:
        pinned = dict(nogo.PORTAL_DOUBLET_COUPLING)
        pinned[O15] = ("Phi210", 2)  # wrong r0 power
        with mock.patch.object(nogo, "PORTAL_DOUBLET_COUPLING", pinned):
            binding = nogo.portal_lattice_binding()
        self.assertFalse(binding["bound"])
        self.assertFalse(binding["patterns"][f"re::{O15}"]["bound"])
        pinned = dict(nogo.PORTAL_DOUBLET_COUPLING)
        pinned[O45_B01] = ("Phi210", 1)  # claims a doublet coupling that is absent
        with mock.patch.object(nogo, "PORTAL_DOUBLET_COUPLING", pinned):
            self.assertFalse(nogo.portal_lattice_binding()["bound"])

    def test_mutation_triplet_pins_and_hypercharge_sources_fail_closed(self) -> None:
        triplets = dict(nogo.PORTAL_TRIPLET_COUPLING)
        triplets[O15] = (("Phi210", 1),)  # hides the O(1) coupling to the 126bar (6,1,1)
        with mock.patch.object(nogo, "PORTAL_TRIPLET_COUPLING", triplets):
            binding = nogo.portal_lattice_binding()
        self.assertFalse(binding["bound"])
        self.assertFalse(binding["patterns"][f"re::{O15}"]["bound"])
        triplets = dict(nogo.PORTAL_TRIPLET_COUPLING)
        triplets[O28] = (("Sigma126bar", 1),)  # wrong r0 power
        with mock.patch.object(nogo, "PORTAL_TRIPLET_COUPLING", triplets):
            self.assertFalse(nogo.portal_lattice_binding()["patterns"][f"im::{O28}"]["bound"])
        sources = dict(nogo.PORTAL_DOUBLET_SOURCE)
        sources[O38] = "+"  # O38 acts on the Y = -1/2 component
        with mock.patch.object(nogo, "PORTAL_DOUBLET_SOURCE", sources):
            binding = nogo.portal_lattice_binding()
        self.assertFalse(binding["bound"])
        self.assertEqual(binding["patterns"][f"re::{O38}"]["doublet_source_hypercharge"], "-")

    def test_mutation_down_type_sigma_vev_is_detected(self) -> None:
        """A Sigma vector with a generic (15,2,2) component has down-type 16.16 entries: the selection-rule check fails."""
        start = nogo.SIGMA_SLICE.start
        down = nogo.induced_yukawa_content({start + 2 * 4: Fraction(1)})
        self.assertIn("d-dc", down["pairs"])
        self.assertIn("e-ec", down["pairs"])
        self.assertIs(down["up_type_only"], False)
        self.assertIs(nogo.induced_yukawa_content({})["up_type_only"], False)  # an empty response proves nothing
        sigma_std = nogo.candidate.sigma_std_raw_coordinates()
        response = {
            start + 2 * index + part: Fraction(int(value))
            for index, (re_value, im_value) in enumerate(zip(*sigma_std, strict=True))
            for part, value in ((0, re_value), (1, im_value))
            if value
        }
        self.assertEqual(nogo.induced_yukawa_content(response)["pairs"], ["nuc-nuc"])

    def test_mutation_colour_bracket_fails_closed(self) -> None:
        gram = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1, 4)]]
        h = [Fraction(2), Fraction(2)]
        result = nogo.colour_radius(gram, h)
        self.assertAlmostEqual(result["radius"], math.sqrt(2.0), places=12)
        self.assertIs(result["exact_bracket"], True)
        self.assertEqual(result["negative_modes_just_beyond"], 1)
        with mock.patch.object(nogo, "COLOUR_BRACKET_RELATIVE", -1.0e-3):  # brackets on the wrong side
            self.assertIs(nogo.colour_radius(gram, h)["exact_bracket"], False)
        self.assertIsNone(nogo.colour_radius([[Fraction(0)]], [Fraction(2)])["radius"])

    def test_failed_check_changes_status(self) -> None:
        report = copy.deepcopy(self.fresh)
        report["n_failed"] = 1
        report["failures"] = ["light_doublet.H_block_decoupled_at_every_r0"]
        self.assertIn("NOT recorded", nogo._verdict(report))


if __name__ == "__main__":
    unittest.main()
