"""F99: exact obstructions to frozen repairs and a scoped normal-pair response."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import sympy as sp
import susy_v91_multipath_g1_frontier_master_audit as common
import v99_determinant_root_descent_audit as finite
import v99_spectator_replacement_anomaly_audit as matter
import v99_normal_half_period_pairing_audit as normal
import v99_original_section_elimination_audit as geometry

ROOT = Path(__file__).resolve().parent
STEM = "SUSY_V99_QUOTIENT_OBSTRUCTIONS_NORMAL_PAIR_SECTION_AUDIT"
OUT_JSON, OUT_MD = (ROOT/(STEM+extension) for extension in (".json", ".md"))
TEST_PATH = ROOT/"test_susy_v99_quotient_obstructions_normal_pair_section_audit.py"
PARENTS = copy.deepcopy(normal.PARENTS)
KEYS = ("determinant_root_descent", "spectator_replacement_anomaly", "normal_half_period_pairing", "original_section_elimination")
MODULES = (finite, matter, normal, geometry)
NEXT_ID = "F100_MODIFIED_EQUIVARIANT_ACTION_AND_ORIGINAL_SECTION_EXISTENCE"
STATUS = "V99_FROZEN_ROOT_AND_MINIMAL_REPLACEMENTS_REJECTED__SHARED_NORMAL_PAIR_QUANTIZED__NO_ACCEPTED_PARENT"
canonical_sha, file_sha = common.canonical_sha, common.file_sha


def crosscheck(parents, f, m, n, g):
    for certificate in (f, m, n, g):
        for parent, (_, core) in PARENTS.items():
            if certificate["input_core_hashes"][parent] != core:
                raise RuntimeError("F99 helpers disagree on their frozen V98 parents")
    operator = f["inherited_center_and_operator_descent"]
    pair = n["shared_reflected_U5_pair"]
    if operator["bare_natural_Spin_c_spinor_character"] != pair["bare_eta_center_bits"]:
        raise RuntimeError("independent bare eta center calculations disagree")
    quarter = f["bound_V98_quantized_chosen_root_response"]["polynomial"]
    if sp.expand(sp.sympify(quarter)-sp.sympify(n["separate_obstructions_retained"]["V98_gauge_quarter_response"])) != 0:
        raise RuntimeError("the distinct normal and gauge calculations lost the frozen gauge target")
    old_modes = parents["v98_route"]["transport_physical_realization"]["positive_hyper_constant_spectrum"]["N1_chiral_multiplet_count"]
    if old_modes != m["full_independent_flavor_replacement"]["new_constant_modes_added"]:
        raise RuntimeError("the actual replacement reused a different carrier spectrum")
    old_geometry = parents["v98_route"]["original_square_section"]
    for key in ("coefficient_payload_sha256", "original_equation_list_sha256", "preserved_frontier"):
        if g[key] != old_geometry[key]:
            raise RuntimeError("the original member, equations or rank frontier changed")
    return {
        "spectator_particle_and_determinant_root_response_are_distinct_options": True,
        "frozen_space_group_rejection_is_independent_of_bulk_particle_count": True,
        "independent_bare_eta_center_checks_agree": True,
        "gauge_target_bound_identically_in_distinct_normal_analysis": True,
        "actual_replacement_keeps_V98_eight_new_free_chirals": True,
        "original_member_equations_and_rank_frontier_preserved": True,
        "response_eta_levels_are_new_particle_multiplicities": False,
        "normal_pair_closed5_response_proves_independent_endpoint_gluing": False,
        "same_action_full_parent_or_experimental_confirmation_claimed": False,
        "old_V97_Dirac_gap_applied_to_new_particles": False,
        "original_section_member_and_rational_function_field_changed": False,
    }


def content():
    parents = {key: common.load_bound(ROOT/name, core) for key, (name, core) in PARENTS.items()}
    if parents["v98_master"]["input_core_hashes"]["v98_route"] != PARENTS["v98_route"][1]:
        raise RuntimeError("V98 lineage changed")
    certificates = [module.build_certificate() for module in MODULES]
    for key, certificate in zip(KEYS, certificates):
        if certificate.get("core_sha256") != canonical_sha(certificate):
            raise RuntimeError("noncanonical F99 helper: "+key)
    sources = {}
    for certificate in certificates:
        for row in certificate["primary_sources"]:
            if row["url"] not in sources:
                sources[row["url"]] = copy.deepcopy(row)
            elif row["use"] not in sources[row["url"]]["use"]:
                sources[row["url"]]["use"] += " "+row["use"]
    hashes = {"generator_sha256": file_sha(Path(__file__)), "test_sha256": file_sha(TEST_PATH)}
    for module in MODULES:
        for name in (module.__name__+".py", "test_"+module.__name__+".py"):
            hashes[name] = file_sha(ROOT/name)
    return {
        "schema": "susy_v99_quotient_obstructions_normal_pair_section_v1", "version": "V99", "status": STATUS,
        "input_core_hashes": {key: value[1] for key, value in PARENTS.items()},
        "scope": "Continuation of the separate SUSY/C8 branch. The canonical V21 physical evidence and all historical route records are unchanged.",
        **dict(zip(KEYS, certificates)),
        "cross_sector_scope_checks": crosscheck(parents, *certificates),
        "supersession_boundary": {
            "V98_chosen_determinant_root_is_compatible_with_frozen_space_group": False,
            "V98_quantization_on_explicit_changed_Spin_c_cover_retracted": False,
            "V98_hypothetical_neutral_replacement_now_tested_against_actual_slots": True,
            "V98_minimal_16_hyper_ansatz_with_frozen_other_matter_is_accepted": False,
            "single_normal_half_period_removed": False,
            "shared_reflected_normal_pair_quantized_on_stated_Spin_c_category": True,
            "shared_normal_pair_is_an_independent_wall_repair": False,
            "full_theory_no_go_over_all_possible_redesigns_claimed": False,
        },
        "terminal_decision": {
            "frozen_determinant_root_lift_rejected": True,
            "minimal_fixed_spectrum_particle_replacement_rejected": True,
            "normal_obstruction_exact_order_and_shared_pair_response_computed": True,
            "original_exceptional_repeated_root_subchart_excluded": True,
            "original_quadratic_trace_and_height_constructed_conditionally": True,
            "original_section_system_solved": False,
            "same_action_full_SMW_SUSY_spectrum_and_bulk_anomalies_completed": False,
            "common_quantized_relative_bulk_wall_defect_action_constructed": False,
            "full_Gammahat_Dai_Freed_and_regulator_completed": False,
            "same_action_microscopic_parent_accepted": False,
            "all_F99_obligations_fully_completed": False,
            "theory_complete": False, "closed_gates": [],
        },
        "gate_ledger": {
            "G1": "OPEN: exact obstructions reject the frozen determinant-root lift and minimal replacement; no complete common microscopic action is accepted.",
            "G2": "OPEN: the conditional spectator sector has additional free chirals, and its minimal fixed-spectrum replacement fails anomaly balance; no new complete mass spectrum is accepted.",
            "G3": "OPEN: the frozen translation character has no equivariant determinant square root. A different lift or correlated relative construction would be a new action requiring verification.",
            "G4": "OPEN: bulk replacement and quotient-response obstructions remain. A shared normal-pair response is quantized only on its stated Spin-c category.",
            "G5": "OPEN: root-choice dependence and individual eta-operator descent are checked, but full relative Dai-Freed, defect/corner gluing and a regulator are absent.",
            "G6": "OPEN: there is no newly accepted same-action spectrum, threshold calculation or complete soft/unification solution.",
            "G7": "OPEN: full spectator/flavor anomaly balance, a globally coupled inflow action and cosmology remain incomplete.",
            "G8": "OPEN: the original section existence equations remain unsolved, with torsion1 and free rank bounded by0..11.",
        },
        "next_required_action": {
            "id": NEXT_ID, "accepted": False,
            "primary": "A further physical repair must change an assumption now excluded: construct an explicit modified equivariant/relative action with its determinant-root descent and bulk-wall-defect gluing, or a larger genuinely equivariant positive spectrum satisfying the frozen quotient and full gauge/flavor anomaly equations. Do not install an unverified replacement. Retain the normal order-two obstruction and the distinction between shared and independent endpoints.",
            "parallel": "Continue the original-field z,H existence problem using the exact saved equations and all pivots. Any new section must be substituted into the original Jacobian and its rational-function descent and height checked. Neither a specialized affine unit ideal nor a conditional section formula proves existence.",
            "not_a_valid_shortcut": "Do not forget root-choice data, identify common-background cancellation with independent gluing, treat virtual eta coefficients as particles, discard spectator curvature, or promote a conditional section to a rank lower bound.",
        },
        "primary_sources": list(sources.values()), "artifact_hashes": hashes,
    }


def build_report():
    report = content()
    report["core_sha256"] = canonical_sha(report)
    return report


def validate_report(report):
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("V99 route core is noncanonical")
    body = copy.deepcopy(report)
    body.pop("core_sha256")
    if body != content():
        raise RuntimeError("V99 route arithmetic, lineage or scope changed")


def render_markdown(report):
    paragraphs = [
        "# SUSY V99: quotient obstructions, normal pairing and original sections",
        "Status: "+report["status"], "Core SHA256: "+report["core_sha256"],
        "V99 tests the two V98 redesign options against constraints they did not yet satisfy. It produces exact rejection results and a quantized shared normal response, not an accepted complete theory. All G1-G8 remain OPEN.",
        "## The determinant-root option fails the frozen lift",
        "The frozen determinant character has D(A)=1 and D(U)=D(V)=-1. A line square root would require C(U),C(V)=+/-i. But the square-space-group relations require C(U)=C(V)=C(U)^(-1), hence C(U)^2=1. No such equivariant root exists for the unchanged lift. The bare natural Spin-c eta operators also fail an internal/tangential central relation; quantization on the chosen Spin-c cover never established their full quotient descent.",
        "A separate continuous-gauge root-choice test compares C and C tensor a flat order-two line on CP2 x S1, with a compensating Spin11 central lift. The two choices project to the same continuous quotient gauge connection but the V98 eta-plus-cup response changes sign. This is a restricted continuous-background test, not a replacement for the finite space-group proof or a full classification of all possible relative countertheories.",
        "## Actual replacement slots do not solve the anomaly equations",
        "Actual neutral orbit blocks can supply sixteen count slots. Nevertheless, every allowed sixteen-for-sixteen singlet removal fails even rational smooth Green-Schwarz factorization when the old tensor lattice, vectors and nonabelian matter are fixed. The certificate gives an analytic moment obstruction and independently checks all 2,956 removal vectors. This is a no-go for that specified minimal spectator ansatz, not for every changed spectrum or tensor sector. All additional spectator/flavor curvature, quantum numbers and free zero modes remain part of the accounting.",
        "The three regular-character 20-hyper extensions also fail rational factorization. Among six 24-hyper extensions, one rational scout remains: add regular copies at D powers1 and2, remove19 neutral and5 charge-eight hypers, and obtain c'=(-464,-144). It fails the frozen quotient source (c'+4b)/8=(-57,-37/2). Independently, an equivariant removal from the actual neutral module has even hyper count, so19 is impossible. This bounded scan does not exclude larger additions or different carriers.",
        "Full independent flavor terms are retained. The new SU4 multiplicity block contributes primitive c4 and z*c3 terms that ordinary Green-Schwarz products cannot remove. A genuine global flavor 't Hooft anomaly is not automatically an inconsistency; the obstruction applies when those backgrounds must be trivialized or that symmetry is gauged. A proper sixteen-hyper selection is not a representation of the entire unchanged Sp267 fundamental, although smaller commuting subgroups can select actual orbit copies.",
        "## An exact order-two normal obstruction and a shared response",
        "Write x=c1(N), with N the Spin-c determinant normal line, and T=-x*c2(E)/2+x^3/8+x*p1/8. For J_x(z)=[Ahat*exp(x/2+z)]6, the exact identity 2T=J_x(x)-15J_x(0)-x*c2(E) gives an integer eta-plus-cup response on closed5, including nonbounding manifolds. Every T period is half-integral, and CP2 x CP1 with x=h+2j gives3/2, so the minimum quantized positive stack is exactly two on this category.",
        "Its closed6 sign obstruction is (-1)^(index_c(N)-15*index_c(1)-integral(x*c2(E))). Since integral(x^3)/2=index_c(N)-3*index_c(1), the same parity is integral(x^3)/2-integral(x*c2(E)). This is a genuine order-two obstruction, not an ordinary integral universal class x^3/2 or a canceled anomaly.",
        "For one shared Spin-c background with E0=A+B and E1=A+B*, c2(E0)+c2(E1)=2(c2(A)+c2(B)). Their summed normal target is therefore represented by xi_c(N)-15xi_c(1) minus the integral cup holonomy x*(c2(A)+c2(B)). The single-wall obstruction persists on independent endpoint data. No factorization into two absolute wall responses, full Gammahat descent, SUSY completion or relative gluing is inferred; the separate R and finite-defect data remain.",
        "## Original section frontier",
        "The exceptional all-linear-remainders-zero chart retains six explicit equations in z,H, with z=r^2 nonzero and 2H-alpha nonzero. Taking the group-law sum of the two quadratic K-root points gives original-field coordinates with T-degrees (4,6), leading terms 36T^4/z and -216T^6/r^3. A square K discriminant is unnecessary for this trace; a square z remains necessary. No z,H solution has been found.",
        "The inherited generic K3 has only one reducible fiber, I2*. Its affine D6 multiplicities allow maximum height correction 3/2, so every nonzero geometric section has height at least 5/2. The conditional trace has height 4 and is primitive. A repeated K root would make it twice a point of height 1, which is impossible: this exceptional subchart is now rigorously excluded. The remaining two cubic points, if realized, are independent over the constant field containing their roots. Original rank at least two follows only if the chart exists and both z and the K discriminant are squares in C(X).",
        "A realized original trace of height 4 and a realized target of height 37 or 148 would also be independent, because their height ratios are not rational squares. None of these existence hypotheses has been proved. The original rank stays 0..11, torsion stays 1, and no threefold height divisor or physical U1 normalization is supplied.",
        "## Next obligation", report["next_required_action"]["id"],
        report["next_required_action"]["primary"], report["next_required_action"]["parallel"],
        "## Primary sources",
    ]
    return "\n\n".join(paragraphs)+"\n\n"+"\n".join("- ["+row["use"]+"]("+row["url"]+")" for row in report["primary_sources"])+"\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate_report(report)
    if args.write:
        OUT_JSON.write_text(json.dumps(report, sort_keys=True, indent=2)+"\n", encoding="utf-8", newline="\n")
        OUT_MD.write_text(render_markdown(report), encoding="utf-8", newline="\n")
    print(json.dumps({"version": "V99", "core_sha256": report["core_sha256"], "closed_gates": [], "next": NEXT_ID}, indent=2))


if __name__ == "__main__":
    main()
