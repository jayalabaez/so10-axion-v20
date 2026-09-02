#!/usr/bin/env python3
"""F93: exact local anomaly target, smooth R extension and Jacobian checks."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import sympy as sp
import susy_v91_multipath_g1_frontier_master_audit as common
import v93_localized_singlet_anomaly as singlets
import v93_bulk_local_anomaly_polynomial as bulk
import v93_mass_sector_symmetry_descent as masses
import v93_geometric_spectrum_compatibility as geometry

ROOT=Path(__file__).resolve().parent
STEM="SUSY_V93_LOCALIZED_ANOMALY_R_LIFT_JACOBIAN_AUDIT"
OUT_JSON,OUT_MD=(ROOT/(STEM+ext) for ext in (".json",".md"))
TEST_PATH=ROOT/"test_susy_v93_localized_anomaly_r_lift_jacobian_audit.py"
PARENTS={
    "v92_route":("SUSY_V92_PROJECTORS_LENS_WCS_COMPACT_DECK_ROOT_AUDIT.json",
                 "3d4365681c9ebdbcbda6d9d57377a1046a6ab00b3a8b1b2290f2858a7ee4f4fb"),
    "v92_master":("SUSY_V92_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
                  "e38e8b58d4f86e00271402c9580919a092e024b737a4fc5290e4d20709b5aae8"),
}
HELPERS=("v93_localized_singlet_anomaly","v93_bulk_local_anomaly_polynomial",
         "v93_mass_sector_symmetry_descent","v93_geometric_spectrum_compatibility")
STATUS="V93_EXACT_LOCAL_ANOMALY_TARGET__SMOOTH_R_AND_WALL_MASS_CHARACTERS__JACOBIAN_B5_CHECK__QUANTIZED_RELATIVE_COMPLETION_OPEN"
NEXT_ID="F94_QUANTIZED_RELATIVE_WALL_COMPLETION_AND_MW_HEIGHT"
canonical_sha,file_sha=common.canonical_sha,common.file_sha


def content():
    old={key:common.load_bound(ROOT/name,core) for key,(name,core) in PARENTS.items()}
    if old["v92_master"]["next_required_action"]["id"]!="F93_LOCALIZED_ANOMALY_GAMMAHAT_AND_SPECTRUM_GLUE":
        raise RuntimeError("F93 lineage obligation changed")
    s,b,m,g=(singlets.build_certificate(),bulk.build_certificate(),masses.build_certificate(),geometry.build_certificate())
    monomials={"f3":bulk.f**3,"f_p1T4":bulk.f*bulk.p,"x_f2":bulk.x*bulk.f**2,
               "x2_f":bulk.x**2*bulk.f,"x3":bulk.x**3,"x_p1T4":bulk.x*bulk.p}
    cross=[]
    for point in bulk.POINTS:
        from_trace=sum(sp.Rational(s["coefficients_by_stratum"][point][key])*term for key,term in monomials.items())
        from_bulk=sp.sympify(b["calculation"]["per_stratum"][point]["singlet"])
        if sp.expand(from_trace-from_bulk)!=0:
            raise RuntimeError("independent singlet trace and bulk assembly disagree")
        cross.append({"stratum":point,"exact_difference":"0"})
    if [m["mass_anomaly_matching"][key] for key in ("TrQ","TrQ3")] != [s["zero_mode_cross_check"][key] for key in ("TrQ","TrQ3")]:
        raise RuntimeError("heavy mass matching does not bind selected singlet anomalies")
    if g["coefficient_payload_sha256"]!=old["v92_route"]["compact_deck_root_geometry"]["coefficient_payload_sha256"]:
        raise RuntimeError("Jacobian audit switched compact coefficient member")
    if g["conditional_Jacobian_nonlocal_matter"]["conditional_nonlocal_vector11_full_hypermultiplets"]!=3:
        raise RuntimeError("conditional Jacobian vector matter no longer matches three bulk 11s")
    sources={}
    for report in (s,b,m,g):
        for row in report["primary_sources"]:
            sources[row["url"]]={"url":row["url"],"use":row.get("use",row.get("role",""))}
    hashes={"generator_sha256":file_sha(Path(__file__)),"test_sha256":file_sha(TEST_PATH)}
    for stem in HELPERS:
        for filename in (stem+".py","test_"+stem+".py"):
            hashes[filename]=file_sha(ROOT/filename)
    return {
        "schema":"susy_v93_localized_anomaly_r_lift_jacobian_audit_v1",
        "version":"V93","status":STATUS,
        "input_core_hashes":{k:v[1] for k,v in PARENTS.items()},
        "scope":"separate SUSY/C8 completion branch; canonical V21 physical gate evidence unchanged",
        "singlet_shifted_character_anomaly":s,
        "bare_bulk_local_anomaly":b,
        "smooth_R_and_wall_mass_extension":m,
        "actual_member_Jacobian_and_torsor":g,
        "cross_certificate_checks":{
            "independent_singlet_trace_vs_bulk_assembly":cross,
            "heavy_mass_matching_moments_equal_selected_singlet_moments":True,
            "Jacobian_and_smooth_resolution_use_same_V91_coefficient_payload":True,
            "conditional_Jacobian_nonabelian_multiplicity_matches_three_bulk_11s":True,
            "checks_prove_same_action_quantum_gluing":False,
        },
        "supersession_boundary":{
            "V92_smooth_R_assignment_unconstructed_now_replaced_by_explicit_matrices":True,
            "V92_local_mass_isotropy_assumption_now_checked_at_all_four_cover_strata":True,
            "mass_module_is_derived_from_existing_global_action":False,
            "V92_compact_smoothness_or_four_closed_lens_results_retracted":False,
            "V92_four_lens_passes_imply_full_local_anomaly_cancellation":False,
            "V92_normal_alignment_implies_vanishing_normal_anomaly":False,
            "Jacobian_B5_implies_Spin11_global_form_or_required_U1":False,
            "torsor_no_section_implies_Jacobian_MW_rank_zero":False,
            "formal_two_axion_polynomial_identity_is_quantized_WCS":False,
        },
        "terminal_decision":{
            "selected_singlet_six_channel_local_anomaly_computed":True,
            "bare_bulk_gauge_normal_gravitational_Cartan_polynomial_computed":True,
            "ordinary_bulk_GS_alone_cancels_selected_bare_bulk":False,
            "independent_smooth_sector_R_action_constructed":True,
            "mass_cubic_passes_selected_fixed_wall_characters":True,
            "nine_massive_fields_anomaly_matching_retained":True,
            "actual_Jacobian_B5_codimension_one_test_passes":True,
            "conditional_Jacobian_nonlocal_vector11_hyper_count":3,
            "actual_torsor_period_and_index":[2,2],
            "Jacobian_MW_rank_height_and_full_matter_spectrum_computed":False,
            "full_Gammahat_wall_normal_representations_frozen":False,
            "quantized_relative_WCS_Dai_Freed_trivialization_constructed":False,
            "same_action_microscopic_parent_accepted":False,
            "all_F93_obligations_fully_completed":False,
            "theory_complete":False,"closed_gates":[],
        },
        "gate_ledger":{
            "G1":"OPEN: explicit bare local anomaly targets and smooth R matrices exist, but no quantized same-action boundary/relative completion connects them to the geometry.",
            "G2":"OPEN: all nine extra masses pass the selected R and wall-isotropy characters; full wall/frame tensor, global gauged Kähler action, SUSY breaking and physical mass scale are missing.",
            "G3":"OPEN: smooth-sector projectors and R action are explicit; localized family/rank/mediator normal charges and full tangential representations remain unfrozen.",
            "G4":"OPEN: a nonbulk-invariant local anomaly remains; ordinary bulk GS alone is insufficient, and formal axion descent identities are not globally quantized cancellation.",
            "G5":"OPEN: common BV/regulator, KK determinant, eta/Pfaffian orientation and the relative boundary complex are absent.",
            "G6":"OPEN: no accepted same-action physical spectrum has been propagated through thresholds and two-loop unification.",
            "G7":"OPEN: the heavy-singlet anomaly is matched, not erased; primitive C8 still breaks to C2, and full quantum selector/proton/decay/cosmology tests are incomplete.",
            "G8":"OPEN: the compact member and its Jacobian pass scoped tests, but the torsor has no section, the Jacobian MW rank/height and full spectrum are unknown, and the Omega-character-compatible diagonal bundle is absent.",
        },
        "next_required_action":{
            "id":NEXT_ID,"accepted":False,
            "primary":"Freeze the localized fields' normal/tangential representations and construct or rule out a quantized boundary completion of the displayed I6 polynomials, including the Phi-phase matching across zeros and defects; then evaluate one relative differential WCS/Dai-Freed theory on the full Gammahat structure.",
            "parallel":"Determine the actual Jacobian Mordell-Weil rank and height, audit torsor affine-component monodromy and codimension-two matter, and construct the same diagonal R/bundle action compatible with tau*Omega=i*Omega.",
            "not_a_valid_shortcut":"Neither formal factorization I6=x*A4+f*B4, a smooth-sector R matrix, nor a Jacobian B5 label establishes a globally consistent quantum action.",
        },
        "primary_sources":list(sources.values()),"artifact_hashes":hashes,
    }


def build_report():
    report=content()
    report["core_sha256"]=canonical_sha(report)
    validate_report(report)
    return report


def validate_report(report):
    if report.get("core_sha256")!=canonical_sha(report):
        raise RuntimeError("V93 core is noncanonical")
    body=copy.deepcopy(report)
    body.pop("core_sha256")
    if body!=content():
        raise RuntimeError("V93 arithmetic, lineage, hashes or scope changed")


def render_markdown(r):
    lines=["# SUSY V93: localized anomalies, R lift and actual Jacobian","",
        "Status: "+r["status"],"","Core SHA256: "+r["core_sha256"],"",
        "## Outcome","",
        "The selected V92 scout now has an exact bare-bulk localized anomaly target, an explicit smooth-sector R action compatible with the nine-singlet mass couplings, and actual-member Jacobian/section checks. Ordinary bulk Green-Schwarz inflow alone cannot cancel the displayed local polynomial. Full wall and relative quantum completion remain open; no gate is closed.","",
        "## Exact local anomaly target","",
        "The 267 singlets contribute (f^3, f*p, x*f^2, x^2*f, x^3, x*p) coefficients (54, -9/16, 37/2, -63/16, -121/192, -11/192) at each C4 corner. At each C2 cover point they contribute (18, -3/16, 0, -9/16, 0, 0). The two C2 cover points form one physical orbit and must be summed. Full shifted-character/SMW traces and independent spectral reconstruction agree.","",
        "Including the three charged 11s, Spin11/U1 gauginos and the inherited standard gravity/tensor lift, each C4 polynomial is:","",
        "I6 = f*h2 + 4*f^2*t - f*x*t + x*(t^2-h2)/4 + 377*f^3/3 + 39*f^2*x/2 - 47*f*p/48 - 87*f*x^2/16 - x*(p+x^2)/8.","",
        "Here h2=sum(e_i^2), t=sum(e_i), p=p1(T4), x is the normal root and f=F8/(2pi) in covering normalization. At z11 replace t by e1+e2-e3-e4-e5. This is the ordinary normal/gauge characteristic sector, not every composite-R or full tangential background.","",
        "The coefficient of x*e1*e2 is 1/2, whereas every ordinary bulk-invariant GS product has zero in that slot. Even a deliberately enlarged GS span has rank 9 while adding I6 raises the rank to 10. The C2 cover also has a nonzero anisotropic gauge coefficient difference of 2. Additional boundary physics or more general inflow is necessary; this is not a no-go for every completion.","",
        "A formal target I6=x*A4+f*B4 is saved at every stratum. The displayed axion descent identities do not construct periodic, globally quantized counterterms or a relative WCS theory.","",
        "In fact, the naive independently period-one normal axion fails a simple curvature-period test: on spin S4 with unit SU5 instanton number the required normal four-form has period 1/2. A unit axion-period shift changes its phase by -1. This excludes that ordinary isolated axion ansatz, not extended normal/tangential lifts, coupled GS data or added wall matter.","",
        "With the inherited visible fields and the eleven selected singlet modes, the ordinary 4D tensor is (-32,-24,-816,-576,-68,1408,96,384,96), ordered as (A3,A2,F*Y6^2,F*X^2,TrF,TrF^3,F^2*Y6,F^2*X,F*Y6*X). Direct Cartan restriction and the component census agree. This gauge-only result does not assign the unfrozen wall normal charges.","",
        "## Mass-sector symmetry and matching","",
        "A new element of Sp1_R times the smooth flavor centralizer gives theta phase i, all nine extra scalars R=1, and both Phi constants R=0. Explicit symplectic matrices commute with the frozen rotations, translations, continuous U1 and primitive k and preserve the known central-kernel descent. The same construction matches the inherited smooth charged-hyper R assignments.","",
        "The correct Phi_minus is the minus component of the q8,m3 line. It and every selected S field are invariant at all four cover strata; Phi_minus*(S2^T*S6+S4^T*S4/2) passes both wall-isotropy and independent-R tests. A nonzero localized coupling has nonzero constant-mode overlap. Full localized/frame tensor and gauged supergravity action remain unconstructed.","",
        "The nine massive Weyls carry TrQ=36 and TrQ^3=864. Their local low-energy matching phase is -phi_minus*(18*f^2-3*p/16), with delta(phi_minus)=-8*epsilon. Its variation reproduces the removed anomaly rather than erasing it. Curvature-period tests on ordinary spin four-manifolds pass for both integral U1 flux and the half-integral covering flux of Spin^c(11) gauge bundles. Torsion, Phi zeros/defects, supersymmetric completion and global gluing are still open.","",
        "## Actual geometry versus the desired spectrum","",
        "For the actual frozen quartic, the Jacobian has orders (2,3,8) along S, nonsplit I2* with Lie algebra B5. Its other generic discriminant components are reduced I1; the compact codimension-one cover is checked. This determines neither the Spin11 global form nor a continuous U1.","",
        "Conditionally in the standard Jacobian interpretation, eight simple branch points give a genus-three monodromy cover over S=P1. The exact adjoint decomposition 66=55+11 and the cover-genus difference predict three vector 11 hypermultiplets, matching the scout's nonabelian count. An independent intersection formula also gives three. Their U1 charges and the torsor's physical contraction have not been established.","",
        "The genus-one torsor has no rational section: a local valuation argument would force one of the two simple boundary quartics to be a square. Its bisection gives period=index=2. This does NOT imply the Jacobian has Mordell-Weil rank zero. The required non-torsion Jacobian section, height 148S+768F and full charged spectrum remain unproved; the target Hodge tuple (9,143,-268) is not an actual-member computation.","",
        "The two independent boundary quadratic extensions also warn against transferring Jacobian component/Hodge data directly to the torsor. The earlier smoothness and tau*Omega=i*Omega results remain intact.","",
        "## Next required action","",r["next_required_action"]["id"],"",
        r["next_required_action"]["primary"],"",r["next_required_action"]["parallel"],"",
        "All eight SUSY/C8 gates remain OPEN. Canonical V21 physical gate evidence is unchanged. No empirical validation or complete spectrum/unification/cosmology is claimed.","",
        "## Primary sources",""]
    lines.extend("- ["+row["use"]+"]("+row["url"]+")" for row in r["primary_sources"])
    return "\n".join(lines)+"\n"


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--write",action="store_true")
    args=parser.parse_args()
    r=build_report()
    if args.write:
        OUT_JSON.write_text(json.dumps(r,sort_keys=True,indent=2)+"\n",encoding="utf-8",newline="\n")
        OUT_MD.write_text(render_markdown(r),encoding="utf-8",newline="\n")
    print(json.dumps({"version":"V93","core_sha256":r["core_sha256"],"closed_gates":[],"next":NEXT_ID},indent=2))


if __name__=="__main__":
    main()
