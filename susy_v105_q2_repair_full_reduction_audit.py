"""F105: retract corrupted V104 Q2 evidence and bind the corrected full reduction."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import susy_v91_multipath_g1_frontier_master_audit as common
import v105_q2_repair_and_full_reduction_audit as helper

ROOT = Path(__file__).resolve().parent
STEM = "SUSY_V105_Q2_REPAIR_FULL_REDUCTION_AUDIT"
OUT_JSON, OUT_MD = (ROOT/(STEM+extension) for extension in (".json", ".md"))
TEST_PATH = ROOT/"test_susy_v105_q2_repair_full_reduction_audit.py"
PARENTS = copy.deepcopy(helper.PARENTS)
NEXT_ID = "F106_Q2_RECONSTRUCTION_CHARTS_Q1_TARGETS_AND_COVARIANT_ACTION_REPAIR"
STATUS = "V105_V104_CORE_EVIDENCE_RETRACTED__CORRECTED_Q2_CONFINEMENT_AND_FULL_RECONSTRUCTION_ATLAS__ALL_GATES_OPEN"
canonical_sha, file_sha = common.canonical_sha, common.file_sha


def crosscheck(inputs, certificate):
    old = inputs["v104_route"]
    geometry = inputs["v103_route"]["original_quartic_sections"]
    if old["input_core_hashes"]["v103_route"] != PARENTS["v103_route"][1]:
        raise RuntimeError("V104 does not bind the intended V103 member")
    if certificate["input_core_hashes"] != {k: v[1] for k, v in PARENTS.items()}:
        raise RuntimeError("F105 helper parent mismatch")
    if certificate["bound_reduced_equations_sha256"] != geometry["quartic_reduced_equations_sha256"] or certificate["preserved_frontier"] != geometry["preserved_frontier"]:
        raise RuntimeError("the repair changed the original curve or frontier")
    replacement = certificate["retraction_and_replacement"]
    if replacement["V104_derived_cores_and_28_97_91_witnesses_accepted_as_original_Q2_evidence"]:
        raise RuntimeError("corrupted V104 residual evidence cannot remain active")
    if replacement["corrected_witnesses_mod101"] != [81, 14, 16] or replacement["corrected_fixed_Sylvester_size"] != 7:
        raise RuntimeError("the corrected fixed-degree resultant certificate changed")
    if not replacement["Q2_confinement_reestablished_by_new_valid_proof"]:
        raise RuntimeError("confinement requires the new proof, not the retracted snapshots")
    theorem = certificate["common_root_reconstruction_theorem"]
    if len(theorem["disjoint_regular_charts"]) != 5 or theorem["zero_slope_and_repeated_roots_discarded"]:
        raise RuntimeError("all regular and zero-slope cases are required")
    if theorem["all_fifteen_conditions_alone_sufficient_over_C_X_on_zero_slope_chart"] or theorem["full_Q2_solvability_decided"]:
        raise RuntimeError("the rational square condition or open solvability was lost")
    if [r["T_degree"] for r in certificate["corrected_reduction"]["rows"]] != [4, 3, 2, 1, 0]:
        raise RuntimeError("all five source residuals must be reconstructed")
    for key in ("Q2_solved", "Q2_excluded", "actual_nonzero_original_section_constructed", "theory_complete"):
        if certificate["terminal_decision"][key]:
            raise RuntimeError("unsupported section or theory promotion")
    return {"identical_original_member_and_rank_torsion_frontier": True,
            "V104_history_preserved_but_corrupted_core_evidence_explicitly_retracted": True,
            "V104_unaffected_leading_quadratic_facts_retained": True,
            "corrected_confinement_has_new_source_identity_and_fixed_degree_certificate": True,
            "all_five_residuals_and_all_zero_pivot_cases_retained": True,
            "regular_chart_rational_q_reconstruction_does_not_solve_t_p_h": True,
            "new_physical_fields_action_or_global_anomaly_cancellation_installed": False,
            "same_action_parent_or_any_gate_accepted": False}


def content():
    inputs = helper.load_inputs()
    certificate = helper.build_certificate()
    if certificate.get("core_sha256") != canonical_sha(certificate):
        raise RuntimeError("noncanonical F105 helper")
    gates = copy.deepcopy(inputs["v104_route"]["gate_ledger"])
    gates["G8"] = "OPEN: V104's misconverted residual cores and witnesses are retracted. Corrected source identities and fixed determinant values81,14,16 mod101 reestablish Q2 confinement. All five residuals are reduced with a complete regular/zero-slope root atlas, but Q2, Q1, target37/148 tails and exact rank remain unsolved."
    return {
        "schema": "susy_v105_q2_repair_full_reduction_route_v1", "version": "V105", "status": STATUS,
        "input_core_hashes": {k: v[1] for k, v in PARENTS.items()},
        "scope": "Separate SUSY/C8 branch. Canonical V21 physical evidence, frozen historical files and all open gates are preserved. Correctness is not inferred from canonical hashes or self-consistent snapshots.",
        "parent_obligation": helper.PARENT_OBLIGATION,
        "q2_repair_full_reduction": certificate,
        "cross_sector_scope_checks": crosscheck(inputs, certificate),
        "supersession_boundary": {
            "V104_corrupted_cores_and_28_97_91_witnesses_retracted_as_original_Q2_evidence": True,
            "V104_hash_pinned_files_and_route_row_rewritten": False,
            "V104_A2_identity_and_h_independent_discriminant_retracted": False,
            "confinement_reestablished_using_corrected_V105_data": True,
            "all_five_residuals_equivalently_reduced_not_solved": True,
            "complete_theory_or_new_physical_law_established": False,
        },
        "terminal_decision": copy.deepcopy(certificate["terminal_decision"]),
        "gate_ledger": gates,
        "next_required_action": {
            "id": NEXT_ID,
            "primary": "Work on the corrected Q2 reconstruction atlas: for each first nonzero ell_i, solve R_i=0 and the four C_ij=0 over C(X), then reconstruct q=-mu_i/ell_i. Separately solve the all-ell=all-mu=0 locus with its Delta-square condition. Alternatively advance Q1 or a certified rank method. Retain fixed degrees and all valuation/pivot boundaries in any generic exclusion; no isolated modular no-point search or equation count certifies it.",
            "parallel": "The full physics obligation remains unchanged: construct actual globally normal-covariant tensors or a lifted diagonal structure, then a same-action QK/F/D vacuum, full Gammahat anomaly/inflow and Higgs-zero matching. Solve the height37/148 global tails with primitivity and complete the soft spectrum, unification and cosmology. A formal tensor line or inverse eta character is not a constructed physical repair.",
        },
        "artifact_hashes": {"generator_sha256": file_sha(Path(__file__)), "test_sha256": file_sha(TEST_PATH),
                            "v105_q2_repair_and_full_reduction_audit.py": file_sha(ROOT/"v105_q2_repair_and_full_reduction_audit.py"),
                            "test_v105_q2_repair_and_full_reduction_audit.py": file_sha(ROOT/"test_v105_q2_repair_and_full_reduction_audit.py")},
        "primary_sources": copy.deepcopy(certificate["primary_sources"]),
    }


def build_report():
    out = content()
    out["core_sha256"] = canonical_sha(out)
    return out


def validate_report(out):
    if out.get("core_sha256") != canonical_sha(out):
        raise RuntimeError("noncanonical V105 route")
    body = copy.deepcopy(out)
    body.pop("core_sha256")
    if body != content():
        raise RuntimeError("V105 route differs from its fresh derivation")


def render_markdown(out):
    sections = [
        "# SUSY V105: Q2 evidence repair and complete residual reduction",
        "Status: "+out["status"], "Core SHA256: "+out["core_sha256"],
        "All G1-G8 remain OPEN. This checkpoint repairs a concrete error in V104 and advances the exact Q2 reduction; it does not solve Q2, construct a physical target, establish new physics or complete the theory. Historical files remain frozen, but the invalid evidence is explicitly superseded.",
        "## What failed in V104",
        "The original variable order is (t,p,q,h,alpha,beta,gamma,delta,epsilon). V104's manual converter reads powers[4] for h and powers[5:] for parameters. Executing that exact source maps h to 1, alpha to h, beta to alpha, gamma to beta, delta to gamma and epsilon to delta. In particular it sends the nonzero polynomial h-1 to zero. All five actual residual polynomials fail round-trip comparison. This is not a harmless change of notation: the leading quadratic used a different, correct conversion, so incompatible systems were mixed.",
        "The derived V104 cores and determinant values 28,97,91 are therefore retracted as evidence about the original Q2 chart. The independently calculated A2=-1296 t^6 M identity and the h-independent discriminant remain correct. Hashes and the old snapshot tests only establish self-consistency; they did not test the missing source-polynomial identity.",
        "## Correct conversion and five exact identities",
        "V105 delegates symbol ordering to the polynomial ring and checks every basis symbol, mixed monomials, and each original residual. Write F=A2 q^2+A1 q+A0, where M=-alpha t^2+4pt+64, and reconstruct r from L=0. All five remaining source numerators N4,...,N0 obey exact universal polynomial identities A2^s_i N_i=Q_i F+t^k_i(ell_i q+mu_i). The pairs (s_i,k_i) are (2,12),(2,12),(3,18),(3,18),(4,24). Since t and M are nonzero on Q2, these identities are equivalent to the original residual equations once F=0.",
        "The ell/mu h-degrees are respectively (1,2),(1,2),(2,2),(2,2),(2,3). The full coefficient expressions and quotient hashes are saved in the JSON certificate. Independent dense polynomial division starts again from the V103 residuals at rational and finite-field specializations, rather than comparing the new converter with itself. Parent cores and source pins are rechecked even after the pure calculation cache is warm; returned reports are not mutable cached state.",
        "## Corrected confinement is reestablished",
        "Set R_i=A2 mu_i^2-A1 ell_i mu_i+A0 ell_i^2 and C_ij=ell_i mu_j-ell_j mu_i. Every Q2 point satisfies all five R_i and all ten C_ij. The corrected leading cores retain exact removable factors t^6 M^2 and t^3 M^2, but now have h-degrees 4 and 3 and contain 1815 and 930 terms. Their explicitly assembled 7-by-7 Sylvester determinants are 81,14,16 modulo 101 at X=1 and (t,p)=(2,1),(3,1),(2,3). All fixed degrees are preserved and M is nonzero at each witness.",
        "Thus the determinant polynomial in X,t,p is not identically zero. Every common h root makes it vanish, including degenerate leading coefficients. The projection of Q2 is confined to this proper zero locus by a new valid proof, not by V104's corrupted cores. No pole bound on rational t(X),p(X), no modular affine-emptiness inference and no rank specialization is used. The nonzero polynomial does not exclude its own zero locus and therefore does not exclude Q2.",
        "The independently committed V105 index correction (commit 3cf518b) is preserved and source-bound. Its four N4/N3 linear coefficients agree identically with this reduction. Its raw determinant values 65,52,20 differ only by normalization: Res_h(R4,C43)=t^30 M^14 Res_h(R4core,C43core). All three residues match this exact scaling law. The two corrected audits therefore agree; neither restores V104's invalid 28,97,91 evidence.",
        "## A complete common-root case split",
        "For any index i with ell_i nonzero, the five conditions R_i=0 and C_ij=0 for the other four indices are necessary and sufficient for a common original-field root, reconstructed uniquely as q=-mu_i/ell_i. The exact identities are ell_i^2 F(-mu_i/ell_i)=R_i and ell_i(ell_j q+mu_j)=C_ij. The discriminant square is automatic here: Delta=(A1-2 A2 mu_i/ell_i)^2. There are five disjoint regular charts, choosing the first nonzero ell in order 4,3,2,1,0.",
        "If all five ell_i vanish, the five norm conditions force all five mu_i to vanish because A2 is nonzero in a field. The quadratic then has a root over C(X) precisely when Delta is a square in C(X), including zero. This sixth, zero-slope case is retained, as are repeated roots. All fifteen polynomial conditions suffice over the algebraic closure, but not over C(X) on this exceptional case without its square condition. Pairwise norms alone are insufficient: q-1 and q+1 each meet q^2-1 but have no common root with each other.",
        "This is a point-set equivalence over a field, not an equality of scheme ideals and not a solution for t,p,h. Only the leading two cores are expanded; the other thirteen conditions are saved exactly in factored form using the complete ell/mu coefficients. No regular chart or exceptional locus is proved empty or populated.",
        "## Unchanged physics and next obligation",
        "Q1, both height-37/148 global target systems, original rank bounds 0..11, torsion order 1, and the normal-covariance/anomaly obstructions retain their previous scope. No original nonzero section, new particle sector, vacuum, inflow or complete microscopic parent is constructed. The physics repair remains an obligation, not an assumption.",
        out["next_required_action"]["id"], out["next_required_action"]["primary"], out["next_required_action"]["parallel"], "## Primary sources",
    ]
    return "\n\n".join(sections)+"\n\n"+"\n".join("- ["+r["use"]+"]("+r["url"]+")" for r in out["primary_sources"])+"\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    out = build_report()
    validate_report(out)
    if args.write:
        OUT_JSON.write_text(json.dumps(out, sort_keys=True, indent=2)+"\n", encoding="utf-8", newline="\n")
        OUT_MD.write_text(render_markdown(out), encoding="utf-8", newline="\n")
    print(json.dumps({"version": "V105", "core_sha256": out["core_sha256"], "closed_gates": [], "next": NEXT_ID}, indent=2))


if __name__ == "__main__":
    main()
