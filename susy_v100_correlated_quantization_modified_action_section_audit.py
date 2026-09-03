"""F100: exact response levels, changed-cover scope, and section alternatives."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import sympy as sp
import susy_v91_multipath_g1_frontier_master_audit as common
import v100_modified_equivariant_cover_audit as finite
import v100_spectator_GS_obstruction_audit as matter
import v100_correlated_quotient_period_audit as periods
import v100_original_section_existence_audit as geometry

ROOT = Path(__file__).resolve().parent
STEM = "SUSY_V100_CORRELATED_QUANTIZATION_MODIFIED_ACTION_SECTION_AUDIT"
OUT_JSON, OUT_MD = (ROOT/(STEM+extension) for extension in (".json", ".md"))
TEST_PATH = ROOT/"test_susy_v100_correlated_quantization_modified_action_section_audit.py"
PARENTS = copy.deepcopy(periods.PARENTS)
KEYS = ("modified_equivariant_cover", "spectator_GS_obstruction", "correlated_quotient_period", "original_section_existence")
MODULES = (finite, matter, periods, geometry)
NEXT_ID = "F101_PHYSICAL_BACKGROUND_RESTRICTION_RELATIVE_ACTION_AND_SECTION_SOLVABILITY"
STATUS = "V100_QUANTIZED_RESPONSES_ON_EXPLICIT_CATEGORIES__REGULAR_SPECTATOR_GS_OBSTRUCTION__CONDITIONAL_SECTION_LATTICE__NO_ACCEPTED_PARENT"
canonical_sha, file_sha = common.canonical_sha, common.file_sha


def crosscheck(parents, f, m, q, g):
    for certificate in (f, m, q, g):
        for parent, (_, core) in PARENTS.items():
            if certificate["input_core_hashes"][parent] != core:
                raise RuntimeError("F100 helpers disagree on the immutable V99 parents")
    cover = f["minimal_combined_operator_cover"]
    if cover["old_kernel"] != q["genuine_Clifford_module"]["kernel"]:
        raise RuntimeError("new cover and old quotient used different center kernels")
    if cover["Sigma_c_character"] != q["genuine_Clifford_module"]["bare_Sigma_bits"]:
        raise RuntimeError("the two operator constructions use different spinor characters")
    d, x, c = sp.symbols("d x c")
    old_target = sp.sympify(q["exact_quantization"]["target_Q"])
    covered_target = sp.sympify(f["quantized_smooth_inverse_response"]["positive_response_curvature"])
    if sp.expand(old_target.subs(d, 2*c)-covered_target) != 0:
        raise RuntimeError("the different categories lost the common target polynomial")
    old_geometry = parents["v99_route"]["original_section_elimination"]
    for key in ("coefficient_payload_sha256", "original_equation_list_sha256", "preserved_frontier"):
        if g[key] != old_geometry[key]:
            raise RuntimeError("the original member or rank frontier changed")
    if q["exact_quantization"]["minimum_positive_stack"] != 8 or cover["minimum_simultaneous_operator_cover_degree"] != 4:
        raise RuntimeError("cover degree and response multiplicity were confused")
    spectator = m["independent_W_GS_obstruction"]
    scout = m["gauge_only_regular_replacement_search"]
    if spectator["pure_W_allowed_N"] != [0, 108] or spectator["strict_budget_gap"] != 1223:
        raise RuntimeError("spectator normalization or exact budget contradiction changed")
    if scout["minimum_N"] != 40 or scout["minimum_scout"]["c_prime"] != ["-456", "-140"]:
        raise RuntimeError("the bounded replacement scout changed")
    if m["minimum_scout_actual_projector_cost"]["conditional_total_free_chiral_count"] != 27:
        raise RuntimeError("the actual replacement projector cost changed")
    lattice = g["conditional_rank_two_lattice"]
    if lattice["Gram_P1_P2"] != [[3, -1], [-1, 3]] or lattice["Gram_S_A"] != [[4, 0], [0, 8]]:
        raise RuntimeError("the conditional section lattice changed")
    if g["existence_search_boundary"]["actual_rational_z_H_solution_found"]:
        raise RuntimeError("V100 has no actual original section candidate")
    return {
        "all_helpers_bind_identical_V99_route_and_master": True,
        "old_and_changed_categories_share_exact_frozen_center_data": True,
        "P_over4_target_matches_under_D_equals_C_squared": True,
        "cover_degree_four_is_not_response_stack_eight": True,
        "closed5_responses_are_not_positive_matter_spectra": True,
        "global_spectator_anomaly_is_not_automatic_inconsistency": True,
        "original_coefficients_equations_and_rank_frontier_preserved": True,
        "physical_Gammahat_identification_or_relative_gluing_inferred": False,
        "gauge_only_replacement_promoted_to_full_mass_action": False,
        "conditional_lattice_promoted_to_actual_original_sections": False,
        "any_full_theory_or_empirical_confirmation_claimed": False,
    }


def content():
    parents = {key: common.load_bound(ROOT/name, core) for key, (name, core) in PARENTS.items()}
    if parents["v99_master"]["input_core_hashes"]["v99_route"] != PARENTS["v99_route"][1]:
        raise RuntimeError("V99 lineage changed")
    certificates = [module.build_certificate() for module in MODULES]
    for key, certificate in zip(KEYS, certificates):
        if certificate.get("core_sha256") != canonical_sha(certificate):
            raise RuntimeError("noncanonical F100 helper: "+key)
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
        "schema": "susy_v100_correlated_quantization_modified_action_section_v1", "version": "V100", "status": STATUS,
        "input_core_hashes": {key: value[1] for key, value in PARENTS.items()},
        "scope": "Separate SUSY/C8 completion branch; canonical V21 physical evidence and historical routes are unchanged.",
        **dict(zip(KEYS, certificates)),
        "cross_sector_scope_checks": crosscheck(parents, *certificates),
        "supersession_boundary": {
            "V99_old_equivariant_root_and_root_choice_obstructions_retained": True,
            "new_degree4_cover_constructed_but_not_installed": True,
            "V98_chosen_cover_quantization_retracted": False,
            "V99_natural_normal_order_two_retracted": False,
            "same_target_requires_eightfold_stack_on_larger_stated_smooth_scout": True,
            "larger_regular_particle_replacements_tested_beyond_V99_bound": True,
            "pure_W_equations_alone_exclude_every_regular_extension": False,
            "conditional_difference_descent_is_not_individual_cubic_descent": True,
            "all_possible_redesigns_or_relative_theories_excluded": False,
        },
        "terminal_decision": {
            "explicit_combined_operator_cover_and_closed5_inverse_constructed": True,
            "exact_eightfold_period_lattice_on_stated_quotient_scout_computed": True,
            "independent_W_frozen_tensor_regular_family_obstruction_computed": True,
            "conditional_original_section_lattice_and_difference_constructed": True,
            "original_section_system_solved": False,
            "same_action_full_SMW_SUSY_spectrum_and_bulk_anomalies_completed": False,
            "common_quantized_relative_bulk_wall_defect_action_constructed": False,
            "full_Gammahat_Dai_Freed_and_regulator_completed": False,
            "same_action_microscopic_parent_accepted": False,
            "all_F100_obligations_fully_completed": False,
            "theory_complete": False, "closed_gates": [],
        },
        "gate_ledger": {
            "G1": "OPEN: exact scoped responses and obstructions are not a complete same-action microscopic parent.",
            "G2": "OPEN: the larger gauge-only replacement changes the light fields and loses the frozen Phi-driven mass module; no complete new mass action exists.",
            "G3": "OPEN: a degree-four combined cover lifts the stated operators, but its ineffective square-group kernel needs an actual equivariant Dirac and field realization.",
            "G4": "OPEN: the single P/4 response fails the stated correlated smooth quotient period test; eight copies are quantized. Required independent-W tensor factorization obstructs the regular particle family.",
            "G5": "OPEN: closed5 eta responses are explicit, but physical background identification, independent boundary/corner trivializations and a regulator are absent.",
            "G6": "OPEN: no newly accepted common soft spectrum, threshold or unification solution is provided.",
            "G7": "OPEN: global spectator anomalies must be distinguished from required gauge/background trivialization; no complete common quantum or cosmological sector is constructed.",
            "G8": "OPEN: exact conditional section lattices and square-class descent do not establish a solution of the original section equations or a physical height divisor.",
        },
        "next_required_action": {
            "id": NEXT_ID,
            "primary": "Identify the actual physical background and orbifold Dirac category from one common action. Test whether the new smooth quotient witness is admissible and construct the necessary relative response and boundary/corner data, or an explicit admissible restriction. Do not change the symmetry category silently or replace a single target by eight copies.",
            "parallel": "Solve or rigorously exclude the remaining original section charts, including the difference route with z times the K discriminant square. If retaining particle replacement, change explicitly the assumptions behind the independent-W obstruction and rebuild the lost Phi mass sector, all anomalies and projectors from that action.",
        },
        "artifact_hashes": hashes, "primary_sources": list(sources.values()),
    }


def build_report():
    report = content()
    report["core_sha256"] = canonical_sha(report)
    return report


def validate_report(report):
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("V100 route core is noncanonical")
    body = copy.deepcopy(report)
    body.pop("core_sha256")
    if body != content():
        raise RuntimeError("V100 route arithmetic, lineage or scope changed")


def render_markdown(report):
    paragraphs = [
        "# SUSY V100: quantified response options and remaining action constraints",
        "Status: "+report["status"], "Core SHA256: "+report["core_sha256"],
        "V100 executes the next research step without accepting a complete theory. It gives explicit response constructions on named background categories, a stronger fixed-family particle obstruction, and new conditional original-section formulas. All eight SUSY/C8 branch gates remain OPEN; canonical V21 evidence is unchanged.",
        "## A response on the unchanged continuous quotient scout",
        "Write x=c1(N), d=c1(D), P=d^3+x*d^2/2. The bare natural Spin-c operator fails the old kernel, but the total module E_n=Sigma_T tensor normal-half tensor R_fund tensor D^n descends. The normal-half and R factors need not exist separately. Its exact integer index difference index(E_2)-2index(E_1)+index(E_0)=2P has no remaining R-curvature or p1 terms. Integer reduced-eta levels therefore define a closed5 response for 2P, including nonbounding backgrounds.",
        "This is sharp on the explicitly stated stable continuous central-quotient scout: spin CP3 with N=D=O(1), and correlated projective R/flavor bundles from a cocharacter ending at KN+KS, has P/4 period3/8. The genuine total module splits there as the spinor tensor (O(n+1)+O(n)), with indices0,1,5. Thus the minimal positive quantized stack of P/4 is exactly eight. This construction is not an ordinary SU2 bundle with fractional Chern class, a natural Spin-c determinant N, or a claimed physical orbifold background. Whether the full physical action admits this witness remains an obligation. A relative anomalous theory or a justified restriction is not excluded.",
        "## A changed cover repairs the individual operators, not the full orbifold",
        "The smallest intermediate central cover admitting both the gauge root C and the bare natural Spin-c spinor keeps only <D_geom> in the kernel: its degree is four, with deck group C2_T x C2_S. Old representations pull back unchanged. On this explicitly changed smooth category, the inverse of exp[2*pi*i*(xi_c(C^2)-2xi_c(C)+xi_c(1)+hol(c_hat^3))] is a genuine closed5 response of curvature -P/4. No normal square-root line M is made genuine.",
        "The saved square-group lift pulls back to (Z^2 x C2_S) semidirect C8, with A^4=epsilon_T and AVA^-1=epsilon_S U^-1. Lifted stabilizer orders are8,8,4,4, not the original4,4,2,2. Both deck generators act trivially on the geometric base; a naive ordinary deck-invariant projection of the new bare operator fibers vanishes. This warns against treating the algebraic cover as an installed orbifold Dirac theory. On the exact CP2 x S1 test, the response sees each independent deck choice by a sign. Smooth quantization is established; relative gluing, twisted sectors and physical anomaly cancellation are not.",
        "## Larger replacements: gauge-only progress, full spectator obstruction",
        "The regular-character family first passes the specified gauge-only count, rational-factorization, quotient-integrality and even-neutral-removal screens at40 hyper units. Its regular additions are(t0,t1,t2)=(0,2,4), with removals(q0,q2,q4,q6,q8)=(28,0,2,0,10). It gives c'=(-456,-140) and integral quotient half-source(-56,-18). This is not an accepted physical spectrum: it removes the Phi charge-eight pair and two charge-four light lines, losing the old Phi-driven mass module. The resulting restricted free-field count is27 before new interactions.",
        "The independent spectator W must not be discarded. With frozen U tensor lattice, a=(2,2), b=(2,-1), all new W charges+1, old removals W-neutral and no new Spin11-charged W matter, the pure-W equations require N=108 and c_WW=(-6,-3). They do NOT alone exclude the regular family. The mixed Q^2 W^2 equation then bounds A between-1728 and-1242, forcing removed fourth moment at least25461, whereas the entire actual old singlet inventory supplies only24238. This excludes every such regular extension if independent-W anomalies must be trivialized using those same tensors, even before integrality. An anomalous genuine global spectator is not automatically inconsistent; altered W assignments, nonabelian matter, tensor data or a relative sector lie outside this theorem.",
        "## Original geometry: exact lattice and a second descent route",
        "The local resolution identifies both conditional cubic points with the vector outer component of the I2* fiber, giving height3 each and pairing-1. Their Gram matrix is[[3,-1],[-1,3]], determinant8; the trace and difference are orthogonal with heights4 and8. The lattice is saturated in its geometric rational span: a hidden overlattice point would reduce to height at most2, below the inherited minimum5/2. These are conditional statements about points arising from an actual solution of the exceptional equations, not a proof that those points exist.",
        "The difference has explicit rational x-coordinate and a y-coordinate controlled by sqrt(z*Delta_K). It can descend to the original field when z*Delta_K is square, even if z and Delta_K are individually nonsquares. The trace still needs z square; an individual cubic point still needs both square conditions. This opens a distinct search route on the unchanged original Jacobian. No actual z,H solution or controlled generic elimination certificate has been obtained; exploratory incomplete computations are not evidence of exclusion. Original rank remains0..11, torsion1, and no physical threefold height divisor is established.",
        "## Next obligation", report["next_required_action"]["id"], report["next_required_action"]["primary"], report["next_required_action"]["parallel"],
        "## Primary sources",
    ]
    return "\n\n".join(paragraphs)+"\n\n"+"\n".join("- ["+r["use"]+"]("+r["url"]+")" for r in report["primary_sources"])+"\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate_report(report)
    if args.write:
        OUT_JSON.write_text(json.dumps(report, sort_keys=True, indent=2)+"\n", encoding="utf-8", newline="\n")
        OUT_MD.write_text(render_markdown(report), encoding="utf-8", newline="\n")
    print(json.dumps({"version": "V100", "core_sha256": report["core_sha256"], "closed_gates": [], "next": NEXT_ID}, indent=2))


if __name__ == "__main__":
    main()
