#!/usr/bin/env python3
"""F92 integration of explicit, separately scoped mathematical certificates."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import susy_v91_spinc_quantization_tensor_cone_finite_torsion_audit as common
import v92_singlet_projector_certificate as projectors
import v92_singlet_mass_module as masses
import v92_c4_section_eta_certificate as finite
import v92_deck_root_geometry_certificate as geometry
import v92_geometric_spectrum_target as spectrum


ROOT = Path(__file__).resolve().parent
STEM = "SUSY_V92_PROJECTORS_LENS_WCS_COMPACT_DECK_ROOT_AUDIT"
OUT_JSON, OUT_MD = (ROOT/(STEM+suffix) for suffix in (".json",".md"))
TEST_PATH = ROOT/"test_susy_v92_projectors_lens_wcs_compact_deck_root_audit.py"
PARENTS = {
    "v91_route":("SUSY_V91_SPINC_QUANTIZATION_TENSOR_CONE_FINITE_TORSION_AUDIT.json",
                  "4a581af0dd4cfc6fd3f66ef1e3ea2801b9770c67822d984a02deb602865c0322"),
    "v91_master":("SUSY_V91_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
                   "f21fb9db8839a6cd3ceb3372abb1b4fb8ecf600ebe500aa33b31f45e890d07ae"),
}
HELPERS = ("v92_singlet_projector_certificate", "v92_singlet_mass_module",
           "v92_c4_section_eta_certificate", "v92_deck_root_geometry_certificate",
           "v92_geometric_spectrum_target")
STATUS = "V92_EXPLICIT_SINGLET_PROJECTORS__FOUR_LENS_WCS_SCREEN_PASSED__COMPACT_DECK_ROOT_SMOOTH__SAME_ACTION_GLUE_OPEN"
NEXT_ID = "F93_LOCALIZED_ANOMALY_GAMMAHAT_AND_SPECTRUM_GLUE"
canonical_sha, file_sha = common.canonical_sha, common.file_sha


def content():
    old = {key:common.load_bound(ROOT/name,core) for key,(name,core) in PARENTS.items()}
    if old["v91_master"]["next_required_action"]["id"] != "F92_QUANTIZED_SCOUT_PROJECTORS_RELATIVE_WCS_AND_DECK_ROOT":
        raise RuntimeError("F92 obligation lineage changed")
    p = projectors.build_certificate()
    mass = masses.build_certificate(p)
    eta = finite.build_certificate()
    geom = geometry.build_certificate()
    target = spectrum.build_certificate()
    selected = eta["torsion_refinement_lens_screen"]["V91_selected_label"]
    lift = geom["integral_projective_model_and_lift"]["order_four_lift"]
    if not selected["passes_both_lens_spin_lifts_in_both_embeddings"]:
        raise RuntimeError("selected scout fails the computed ordinary lens screen")
    if not geom["proper_specialization"]["resolved_compact_member_geometrically_smooth_over_Q"]:
        raise RuntimeError("compact smoothness certificate incomplete")
    if not lift["global_regular_lift_exists"] or lift["holomorphic_three_form_character"] != "I":
        raise RuntimeError("global deck-root or its residue character changed")
    sources = []
    for certificate in (p,eta,geom):
        sources.extend(copy.deepcopy(certificate["primary_sources"]))
    sources.extend([
        {"url":"https://arxiv.org/abs/math/0005196", "use":"full-Cartan neutral/charged hyper census and conditional geometric anomaly dictionary; section 3"},
        {"url":"https://arxiv.org/abs/math/0112259", "use":"Shioda-Tate-Wazir divisor-rank formula; section 4"},
    ])
    unique_sources = {row["url"]:row for row in sources}
    hashes = {"generator_sha256":file_sha(Path(__file__)),"test_sha256":file_sha(TEST_PATH)}
    for stem in HELPERS:
        hashes[stem+".py"] = file_sha(ROOT/(stem+".py"))
        hashes["test_"+stem+".py"] = file_sha(ROOT/("test_"+stem+".py"))
    return {
        "schema":"susy_v92_projectors_lens_wcs_compact_deck_root_audit_v1",
        "version":"V92", "status":STATUS,
        "input_core_hashes":{key:core for key,(_,core) in PARENTS.items()},
        "scope":"separate SUSY/C8 completion branch; canonical V21 gate evidence unchanged",
        "smooth_singlet_projectors":p,
        "conditional_extra_singlet_mass_module":mass,
        "ordinary_closed_lens_anomaly_screen":eta,
        "compact_deck_root_geometry":geom,
        "conditional_spectrum_geometry_target":target,
        "integration_boundary": {
            "six_dimensional_bulk_scout_unchanged_from_V91":True,
            "chosen_projectors_are_unique_or_forced":False,
            "projectors_are_at_symmetric_zero_flux_origin":True,
            "normal_channel_alignment_is_total_local_anomaly_cancellation":False,
            "mass_module_is_a_new_conditional_local_ansatz":True,
            "mass_module_R_assignment_and_global_wall_embedding_certified":False,
            "four_closed_lens_ratios_equal_full_relative_Dai_Freed_functor":False,
            "V71_MMP_global_source_convention_dictionary_reconciled":False,
            "geometry_and_projectors_are_one_diagonal_orbibundle":False,
            "compact_smoothness_proves_required_Mordell_Weil_rank_or_spectrum":False,
            "old_V90_geometry_certificate_retracted":False,
            "V91_arithmetic_scout_rejected":False,
        },
        "terminal_decision": {
            "explicit_267_singlet_smooth_sector_projectors_constructed":True,
            "conditional_normal_aligned_witness_zero_modes":p["eleven_mode_normal_aligned_witness"]["constant_N1_chiral_count"],
            "nine_extra_modes_lift_in_conditional_local_mass_ansatz":True,
            "selected_ordinary_four_lens_WCS_screen_passed":True,
            "torsion_labels_passing_this_screen":eta["torsion_refinement_lens_screen"]["labels_passing_this_screen"],
            "compact_geometrically_smooth_member_certified":True,
            "global_regular_order_four_deck_root_certified":True,
            "standalone_volume_preserving_CY_quotient":False,
            "full_Gammahat_tangential_structure_and_wall_representations_frozen":False,
            "full_relative_anomaly_cancelled":False,
            "same_action_microscopic_parent_accepted":False,
            "all_F92_obligations_fully_completed":False,
            "theory_complete":False, "closed_gates":[],
        },
        "gate_ledger": {
            "G1":"OPEN: explicit singlet projectors, four ordinary lens ratios and a compact smooth deck-root member are separate constructions; the global gauged action and diagonal orbibundle are absent.",
            "G2":"OPEN: nine singlet masses have a conditional local ansatz, but its global R lift, Kähler data, SUSY breaking and complete physical spectrum are not derived.",
            "G3":"OPEN: all 267 singlet smooth-sector matrix projectors are explicit; wall representations, full tangential group and nonzero-VEV background remain unconstructed.",
            "G4":"OPEN: selected ordinary C4/C8 lens ratios pass with WCS; full BG8/Gammahat bordism character, local gauge-normal anomaly and relative fixed-wall trivialization are uncomputed.",
            "G5":"OPEN: no common KK determinant, regulator, Pfaffian orientation or junction/cap complex has been constructed.",
            "G6":"OPEN: no accepted same-action spectrum has been propagated through thresholds and two-loop running.",
            "G7":"OPEN: the visible vacuum still breaks primitive C8 to C2; all-order selection rules, decay/proton safety, cosmology and empirical likelihood are not established.",
            "G8":"OPEN: compact smooth geometry and its order-four automorphism are proved, but tau acts by i on Omega and requires a compatible diagonal R/bundle action; the required spectrum and quantum theory are not realized.",
        },
        "next_required_action": {
            "id":NEXT_ID, "accepted":False,
            "primary":"Compute the complete localized U1, mixed gauge-normal and gravitational anomaly tensors using the selected 267 projectors; freeze every wall representation and the full Gammahat tangential kernel before constructing one relative differential WCS/Dai-Freed trivialization.",
            "parallel":"Construct the independent R action and fixed-wall embedding of the nine-singlet mass module, and glue the smooth order-four geometry to that same bundle while checking its Omega character, Mordell-Weil rank/height and actual six-dimensional spectrum.",
            "not_a_valid_shortcut":"Neither four closed-lens tests nor compact smoothness can replace the same-action relative anomaly and spectrum realization.",
        },
        "primary_sources":list(unique_sources.values()),
        "artifact_hashes":hashes,
    }


def build_report():
    report = content()
    report["core_sha256"] = canonical_sha(report)
    validate_report(report)
    return report


def validate_report(report):
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("noncanonical V92 report")
    body = copy.deepcopy(report)
    body.pop("core_sha256")
    if body != content():
        raise RuntimeError("V92 certificate, source hashes, lineage or non-promotion changed")


def render_markdown(r):
    p = r["smooth_singlet_projectors"]
    eta = r["ordinary_closed_lens_anomaly_screen"]
    mode = p["eleven_mode_normal_aligned_witness"]
    lines = [
        "# SUSY V92: projectors, lens-space WCS and compact deck root", "",
        "Status: "+r["status"], "", "Core SHA256: "+r["core_sha256"], "",
        "## Outcome", "",
        "F92 produces explicit 267-hyper smooth-sector projector witnesses, an ordinary finite-symmetry lens test with its tensor counterterm, and a compact smooth crepant geometric member with a global order-four deck root. These are not yet one same-action quantum completion. All eight SUSY/C8 gates remain OPEN.", "",
        "## Actual projectors and extra modes", "",
        "The compressed direct sum fully specifies all 267 hypermultiplets and their plus/minus/SMW matrices and projectors at all four strata. Symplectic reality, central-kernel descent, charge-preserving translations and constant-mode joint kernels are checked exactly. Continuous charges are not replaced by their residues modulo eight.",
        "With the explicitly chosen ordinary untwisted new U1 gaugino lift, the normal-channel base changes from (86,-14) to (97,-13), in units of 1/192. Equal-corner alignment with x*p1(T6) requires Delta=-11 and at least eleven chiral constant modes under the stated assumptions.",
        "The selected witness has signed charges "+str(mode["constant_N1_signed_continuous_charges"])+"; TrQ=36 and TrQ^3=864. Its normal polynomial is -x*p1(T6)/8, not zero. Another witness with the same six-dimensional counts has only the +8/-8 pair but fails that normal-channel alignment. Thus V91 did not uniquely determine the projectors.", "",
        "## Conditional mass repair", "",
        "A new local ansatz W=Phi_-8*(S2^T S6 + S4^T S4/2) lifts the nine additional fields at nonzero <Phi_->=v. The exact 9x9 fermion mass determinant is -v^9 and M-dagger*M=|v|^2 I. All new F and D contributions vanish at S=0.",
        "This requires a NEW independent R4=1 assignment for the nine fields, canonical local kinetic terms and an allowed fixed-wall interaction. Their full R/kernel descent and global action are not constructed. Giving masses does not erase anomaly matching obligations, and the complete retained vacuum still reduces primitive C8 to C2.", "",
        "## Four ordinary lens tests, with WCS", "",
        "The noncentral C4 section has hyper/vector character counts (236,4,30,30)/(38,9,0,9). Both spin lifts of L7_4 give trivial reduced bare fermion phase. On central L7_8, both give phase -1 (exponents 153/2 and -135/2 in the stated chirality convention). This bare sign is not by itself a rejection.",
        "For the even U lattice, the quadratic refinement vanishes on both null axes and polarization gives q_U(x,y)=link(x,y). Retaining lambda_T=2u^2 yields the gravitational cross term: Delta S=(g1*g2+2*g1+2*g2)/n. The WCS ratio cancels the central -1 for the selected frozen source.",
        "Exactly "+str(eta["torsion_refinement_lens_screen"]["labels_passing_this_screen"])+" of 16 torsion labels pass all four tests, including V91 tau=(0,2). Both linking orientation signs have the same pass set. This is not the full BG8 or Gammahat bordism character, an orbifold determinant, or a relative fixed-wall trivialization.", "",
        "## Compact geometry", "",
        "The V91 coefficient member has a complete smoothness proof by good reduction at 101: four exhaustive away-S strata retain every ambient derivative; branch/nonbranch exceptional charts cover S; the projective relative Cartier model and coordinate-center Rees algebras justify specialization to characteristic zero. A single modular affine check is not used as a characteristic-zero proof.",
        "The disjoint first centers are exchanged and the residual center is invariant, so the Rees construction gives a global regular order-four lift whose square is deck. Blowdown and weak-transform equivariance are checked symbolically.",
        "However tau*Omega=i*Omega. It is not a standalone volume-form-preserving Calabi-Yau quotient; a compatible diagonal R/bundle action remains necessary.", "",
        "## Spectrum must match the geometry", "",
        "If the continuous V91 scout is realized by a smooth flat elliptic Calabi-Yau over F4 with exactly B5 plus one U1 and no extra sectors, its necessary Hodge tuple is (h11,h21,Euler)=(9,143,-268). The three zero Spin11 weights are U1-charged and are not neutral hypers. The older Spin11-only tuple (8,268,-520) cannot be reused.",
        "The conditional height class is 148S+768F. No actual height pairing, Mordell-Weil rank, Hodge numbers or matter spectrum of the new member have been computed. The necessary target is not a realization proof.", "",
        "## Next obligation", "", r["next_required_action"]["id"], "",
        r["next_required_action"]["primary"], "", r["next_required_action"]["parallel"], "",
        "Canonical V21 gate evidence is unchanged. No empirical confirmation, SUSY-breaking spectrum, unification or cosmological completion is claimed.", "",
        "## Primary sources", "",
    ]
    lines.extend("- ["+row["use"]+"]("+row["url"]+")" for row in r["primary_sources"])
    return "\n".join(lines)+"\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write",action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        OUT_JSON.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8",newline="\n")
        OUT_MD.write_text(render_markdown(report),encoding="utf-8",newline="\n")
    print(json.dumps({"version":"V92","core_sha256":report["core_sha256"],
                      "closed_gates":[],"next":NEXT_ID},indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
