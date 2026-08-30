#!/usr/bin/env python3
"""Adversarial closure audit for the V47 microscopic-boundary G2 gate.

This audit deliberately separates a finite-order Wilsonian boundary EFT from
an all-order UV completion.  It records what V47 proves, the data still needed
for G2, and the smallest no-new-field construction that could close the gate.
It does not modify or reinterpret the V45--V47 source artifacts.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V48_G2_ADVERSARIAL_CLOSURE_AUDIT.json"
MD_PATH = ROOT / "SUSY_V48_G2_ADVERSARIAL_CLOSURE_AUDIT.md"

INPUTS = {
    "v47_master": ROOT / "SUSY_V47_G1_CLOSURE_FRONTIER_AUDIT.json",
    "v47_global": ROOT / "SUSY_V47_RELATIVE_ETA_BORDISM_AUDIT.json",
    "v47_source": ROOT / "SUSY_V47_SOURCE_COMPLETION_ROUTE_AUDIT.json",
    "v47_KK": ROOT / "SUSY_V47_FOUR_SPINOR_MIXED_KK_AUDIT.json",
    "v48_resolved_wall": ROOT / "SUSY_V48_RESOLVED_SOURCE_WALL_AUDIT.json",
    "v48_operator_wilson": ROOT / "SUSY_V48_SOURCE_OPERATOR_WILSON_AUDIT.json",
}

SOURCE_FILES = (
    Path(__file__).name,
    "test_susy_v48_g2_adversarial_closure_audit.py",
    *(path.name for path in INPUTS.values()),
)

STATUS = (
    "V48_G2_ADVERSARIAL_REVIEW__RESOLVED_COLLAR_C2_PASS__"
    "PARITY_RESOLVED_OPERATOR_AND_COUNTERTERM_CENSUS_INCOMPLETE__"
    "REPRESENTATIVE_WILSON_IDENTITY_NOT_FULL_COMPONENT_MATCH__G2_OPEN"
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
        "utf-8"
    )


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"missing input: {path.name}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if canonical_sha(payload) != payload.get("core_sha256"):
        raise RuntimeError(f"bad input core hash: {path.name}")
    return payload


def source_manifest() -> list[dict[str, Any]]:
    return [
        {
            "path": name,
            "exists": (ROOT / name).is_file(),
            "sha256": sha256_file(ROOT / name) if (ROOT / name).is_file() else None,
        }
        for name in SOURCE_FILES
    ]


def closure_criteria() -> list[dict[str, Any]]:
    return [
        {
            "id": "C1",
            "name": "scope_power_counting_and_operator_completeness",
            "necessary_and_sufficient_output": (
                "Declare Lambda, matching scale, loop order and an expansion order; enumerate an "
                "independent bulk/PS-wall/source-wall operator basis through that order modulo "
                "integration by parts, supersymmetric field redefinitions and leading equations of motion."
            ),
            "V47_state": "partial",
            "V47_evidence": (
                "The renormalizable source superpotential and four holomorphic spinor portals are "
                "included, but the boundary Kahler, gauge-kinetic, normal-derivative and wrong-chirality "
                "basis is not enumerated and no truncation error is declared."
            ),
            "passes": False,
        },
        {
            "id": "C2",
            "name": "regulator_or_fundamental_interval_prescription",
            "necessary_and_sufficient_output": (
                "Either retain a finite-width/deconstructed wall, or define a one-sided interval action "
                "with normalized boundary traces and a named thin-defect subtraction scheme; derive the "
                "renormalized boundary kernel from that action."
            ),
            "V47_state": "open",
            "V47_evidence": (
                "V47 treats B as a finite renormalized extension parameter and explicitly declines to map "
                "the bare delta coefficients to B."
            ),
            "passes": False,
        },
        {
            "id": "C3",
            "name": "variational_domain_and_self_adjointness",
            "necessary_and_sufficient_output": (
                "Derive every boundary condition by varying the retained regulated action and prove that "
                "the complete, possibly generalized, KK operator is self-adjoint on that domain."
            ),
            "V47_state": "conditional",
            "V47_evidence": (
                "For an externally supplied constant Hermitian B, V47 proves cancellation of the boundary "
                "form and reality of signed eigenvalues.  It does not derive that B or the domain from a "
                "microscopic boundary action with induced operators."
            ),
            "passes": False,
        },
        {
            "id": "C4",
            "name": "positive_kinetic_form",
            "necessary_and_sufficient_output": (
                "Give the bulk plus boundary quadratic norm, including boundary kinetic mixing and any "
                "retained boundary fields, and certify positivity throughout the declared EFT domain."
            ),
            "V47_state": "open",
            "V47_evidence": (
                "No boundary Kahler/kinetic matrices or generalized norm are present; the no-tachyon theorem "
                "explicitly excludes negative boundary kinetic norms."
            ),
            "passes": False,
        },
        {
            "id": "C5",
            "name": "counterterm_and_renormalization_scheme",
            "necessary_and_sufficient_output": (
                "Name the regulator and subtraction prescription, list every counterterm at the retained "
                "order, give renormalization conditions at mu_star and show regulator/scale independence up "
                "to the declared remainder."
            ),
            "V47_state": "open",
            "V47_evidence": (
                "V47 normalizes same-domain spectral products but leaves absolute and cross-boundary constants "
                "to an unspecified brane regulator and local counterterm scheme."
            ),
            "passes": False,
        },
        {
            "id": "C6",
            "name": "symmetry_and_naturalness_policy",
            "necessary_and_sufficient_output": (
                "For every omitted allowed operator through the retained order, provide a symmetry/EOM reason; "
                "for every retained coefficient give a renormalized input or matching value and an NDA-sized "
                "domain.  Zero is not a symmetry argument."
            ),
            "V47_state": "partial",
            "V47_evidence": (
                "V47 correctly proves that neutral discrete sequestering cannot remove STheta Phi^2 and "
                "STheta Sigma barSigma, but it supplies no fixed-order policy for the infinite neutral dressings."
            ),
            "passes": False,
        },
        {
            "id": "C7",
            "name": "action_to_Wilson_matching",
            "necessary_and_sufficient_output": (
                "Integrate the regulated boundary layer and the four hypermultiplets with all declared wall "
                "currents, publish the matrix Schur-complement/Green-function Wilson kernel, and verify its "
                "low-energy expansion and remainder in the same scheme."
            ),
            "V47_state": "open",
            "V47_evidence": (
                "The exact homogeneous characteristic C(m) is known, but no inhomogeneous Green function, "
                "current map, Wilson coefficient or regulator-matching comparison is supplied."
            ),
            "passes": False,
        },
    ]


def parity_resolved_census() -> dict[str, Any]:
    """Operators exposed by the actual V45 parity and V47 symmetry data.

    Primitive U(1)F charges are used here (the V45 anomaly table uses charges
    three times larger).  Hc always denotes the conjugate 4D chiral in the
    same 5D hypermultiplet.
    """

    return {
        "PS_even_direct_traces": {
            "H": [
                "HLF_L=(4,2,1)_+1",
                "HLA_L=(bar4,2,1)_-4",
                "HRA_R=(bar4,1,2)_-1",
                "HRF_R=(4,1,2)_+4",
            ],
            "Hc": [
                "HLFc_R=(4,1,2)_-1",
                "HLAc_R=(bar4,1,2)_+4",
                "HRAc_L=(bar4,2,1)_+1",
                "HRFc_L=(4,2,1)_-4",
            ],
        },
        "PS_zero_derivative_superpotential": {
            "correct_spinor_cubic_count": 19,
            "cubic_breakdown": (
                "the 4x4 Q/HLF--Qc/HRA block (16), HLA-HRF (1), and the two "
                "complementary Hc cubics HRAc_L H HLFc_R and HRFc_L H HLAc_R"
            ),
            "additional_allowed_relevant_operator": (
                "mu_H epsilon_L epsilon_R H H; it is PS x U1F and matter-parity "
                "invariant and V47 explicitly withdrew inherited Z4R"
            ),
        },
        "PS_Kahler": {
            "required_blocks": [
                "arbitrary positive Hermitian 4x4 block on (Q1,Q2,Q3,HLF_L)",
                "arbitrary positive Hermitian 4x4 block on (Qc1,Qc2,Qc3,HRA_R)",
                "independent positive metrics for HLA_L, HRF_R, HLFc_R, HLAc_R, HRAc_L, HRFc_L and H",
            ],
            "status_in_operator_artifact": "included after adversarial repair",
        },
        "PS_normal_derivatives": {
            "universal_bulk_terms": [
                "int d2theta Hc^hat_r nabla5 H^hat_r+h.c. (Hebecker O7)",
                "int d2theta (nabla5 Hc^r) H^r+h.c. (Hebecker O8)",
            ],
            "allowed_brane_bulk_examples": [
                "Q_i (nabla5 HLFc)_L",
                "Qc_i (nabla5 HRAc)_R",
            ],
            "required_treatment": (
                "enumerate their independent coefficients through the retained order or "
                "show the IBP/EOM/field-redefinition quotient and every induced current shift"
            ),
            "status_in_operator_artifact": "absent",
        },
        "PS_gauge": {
            "included_allowed_terms": [
                "independent holomorphic W4^2, W2L^2, W2R^2 and WF^2",
                "the U1F FI coordinate",
                "int d4theta Tr Zhat^2 for the broken (6,2,2) gauge multiplet",
            ],
            "linear_Zhat_current_at_retained_order": (
                "forbidden at zero source insertion: Zhat connects PS-left and PS-right "
                "spinor components, but the even direct traces contain no such pair with equal U1F charge"
            ),
            "remaining_positive_norm_obligation": (
                "the Zhat coefficient and its mixing with the bulk gauge norm must satisfy an explicit no-ghost inequality"
            ),
        },
        "source_collar_Hc_test": {
            "fact": (
                "Hc(L)=0 at the outer endpoint, but Hc is a nonzero field inside the finite fundamental collar"
            ),
            "allowed_HcHc_portals": [
                "ThetaMinus HLFc HLAc",
                "ThetaPlus HRAc HRFc",
                "Sigma HLFc HRAc",
                "barSigma HLAc HRFc",
            ],
            "smooth_Dirichlet_scaling": (
                "for a nonsingular even profile, Hc(L-s)=O(s nabla5 Hc), so a normalized "
                "HcHc collar insertion starts at O(epsilon^2 E^2) and may be assigned to "
                "the O(E^2/Lambda^2) remainder only after this reduction is made explicit"
            ),
            "NLO_profile_problem": (
                "the one-sided slab states no reflection/profile rule excluding localized Hc H, "
                "S Hc H, Phi210 Hc H or mixed H--Hc Kahler responses; parity-compatible odd "
                "profiles can contribute at O(epsilon E), so they must be included or removed "
                "by an explicit symmetric-orbifold regulator and matching proof"
            ),
            "one_insertion_Kahler_witnesses": [
                "ThetaMinus HLF^dagger HLAc",
                "ThetaPlus HRA^dagger HRFc",
                "ThetaMinus HLA^dagger HLFc",
                "ThetaPlus HRF^dagger HRAc",
                "HLF^dagger Sigma HRAc and its independent barSigma partner",
            ],
        },
    }


def combined_v48_review() -> dict[str, Any]:
    rows = [
        {
            "id": "C1",
            "state": "fail",
            "passes": False,
            "reason": (
                "The parity-resolved fixed-order basis is incomplete: mu_H HH and PS normal-derivative "
                "operators are absent; the finite collar does not census Hc-dependent responses; and "
                "pure-source quartics at the same 1/Lambda order are assigned to G3 rather than parameterized."
            ),
        },
        {
            "id": "C2",
            "state": "pass",
            "passes": True,
            "reason": (
                "The finite positive square collar is retained as the fundamental problem, has normalized "
                "source modes, and uses the pole-free characteristic rather than discarding D-block poles."
            ),
        },
        {
            "id": "C3",
            "state": "partial",
            "passes": False,
            "reason": (
                "Self-adjointness is proved for the quadratic source collar, but not for the complete PS/source "
                "action after all allowed derivative and kinetic operators are included and varied."
            ),
        },
        {
            "id": "C4",
            "state": "partial",
            "passes": False,
            "reason": (
                "The collar and named matter metrics are positive, but no full Schur-complement/no-ghost test "
                "includes source-field Kahler responses, PS derivative mixing and the Zhat boundary term."
            ),
        },
        {
            "id": "C5",
            "state": "partial",
            "passes": False,
            "reason": (
                "A tree-level matching scale and one quadratic collar scheme are declared, but the complete "
                "retained-order counterterm basis, subtraction conditions and profile-rematching check are absent."
            ),
        },
        {
            "id": "C6",
            "state": "partial",
            "passes": False,
            "reason": (
                "The finite-order/no-selector policy is sound, but allowed omitted coefficients and the Hc "
                "profile zeros lack a symmetry, matching condition or demonstrated remainder assignment."
            ),
        },
        {
            "id": "C7",
            "state": "partial",
            "passes": False,
            "reason": (
                "G00=(Kreg+Nreg V0)^-1 Nreg and its source-projector derivatives are a useful structural "
                "advance, but the executable witness uses representative matrices.  It does not publish the "
                "physical component Clebsches/projectors and current matrices for all 19 PS vertices plus "
                "the derivative/Hc operators, so it is not a complete Wilson coefficient match."
            ),
        },
    ]
    return {
        "criteria": rows,
        "number_fully_passed": sum(row["passes"] for row in rows),
        "promotion": "REJECT",
        "G2_closed": False,
        "resolved_subgates": [
            "C2 finite source-wall regulator",
            "19-term zero-derivative PS spinor cubic census (but not the full PS superpotential)",
            "formal full-tower Green-function/Schur-complement structure",
        ],
        "not_G2_blockers": {
            "G3": "solve the coupled vacuum, FI D equation and branch selection after G2 parameterizes its coefficients",
            "G6": "numerical pole tower, thresholds, unification and RG evolution",
            "G7": "phenomenological baryon-decay running and likelihoods",
        },
    }


def build_report() -> dict[str, Any]:
    inputs = {key: load_json(path) for key, path in INPUTS.items()}
    v47 = inputs["v47_master"]
    kk = inputs["v47_KK"]
    source = inputs["v47_source"]
    criteria = closure_criteria()
    combined = combined_v48_review()

    report: dict[str, Any] = {
        "schema": "susy_v48_g2_adversarial_closure_audit/v1",
        "status": STATUS,
        "source_manifest": source_manifest(),
        "input_core_hashes": {key: value["core_sha256"] for key, value in inputs.items()},
        "gate_definition": {
            "qualified_scope": (
                "G2 is the Wilsonian microscopic boundary-action and source/portal-matching gate for the "
                "retained V47 interval architecture at a declared EFT order."
            ),
            "included": [
                "complete action basis at the declared order",
                "a regulator or fundamental interval prescription",
                "variational boundary conditions and self-adjointness",
                "positive bulk-plus-boundary kinetic form",
                "counterterms and renormalization conditions",
                "symmetry/naturalness treatment of coefficients",
                "action-to-boundary-kernel and tree/full-tower Wilson matching at that order",
            ],
            "excluded_and_owned_elsewhere": {
                "G3": "global vacuum selection and radion/Kahler/soft stabilization",
                "G6": "complete numerical pole tower, thresholds, unification and coupled RG evolution",
                "G7": "the full baryon-violating ring, hadronic running and decay-rate likelihoods",
                "G8": "three-family flavour and neutrino fit",
            },
            "closure_logic": "G2_closed iff C1 and C2 and C3 and C4 and C5 and C6 and C7",
        },
        "closure_criteria": criteria,
        "parity_resolved_operator_census": parity_resolved_census(),
        "combined_V48_adversarial_review": combined,
        "all_order_no_go": {
            "claim": (
                "The current exact symmetries cannot select a finite all-order boundary action.  They permit "
                "an infinite tower of neutral dressings, so all-order G2 closure without a UV completion is "
                "not a coherent acceptance criterion."
            ),
            "explicit_witness": {
                "neutral_invariant": "Y=ThetaPlus^dagger exp(2 q_Theta V_F) ThetaPlus",
                "primitive_U1F_charge": "-3+3=0",
                "R_charge": "0 for any unitary ordinary or R assignment",
                "tower": (
                    "if a D-term O_D is allowed, then O_D Y^n with the required powers of Lambda is "
                    "allowed for every n>=0; the holomorphic X=ThetaPlus ThetaMinus supplies additional "
                    "F-term dressings whenever its R charge permits"
                ),
                "additional_neutral_dressings": [
                    "Spin(10)-singlet contractions of Phi210^2 and Phi210^3",
                    "Sigma barSigma",
                    "STheta powers and neutral combinations already present in the source branch",
                ],
            },
            "consequence": (
                "A valid no-UV-completion closure must be Wilsonian: finite operator basis through a declared "
                "order plus an explicit power-counting remainder."
            ),
        },
        "smallest_legitimate_construction": {
            "name": "one-sided interval Wilsonian completion with no new propagating fields",
            "why_smallest": (
                "A genuine interval boundary action uses one-sided field traces and derives boundary conditions "
                "by variation.  It removes the orbifold-delta convention without adding a deconstruction/link sector."
            ),
            "accuracy_contract": {
                "matching_scale": "mu_star=Lambda",
                "recommended_order": "tree level through boundary dimension five, i.e. O(Lambda^-1)",
                "remainder": "O(E^2/Lambda^2) plus explicitly stated loop-order error",
                "warning": (
                    "Stopping at boundary dimension four cannot support an O(Lambda^-2) remainder because "
                    "brane kinetic and normal-derivative operators built from bulk traces first occur at dimension five."
                ),
            },
            "LO_source_superpotential": [
                "the complete V47 neutral 210+126+bar126+STheta+ThetaPlus+ThetaMinus source superpotential",
                "ThetaPlus HLF HLA",
                "ThetaMinus HRA HRF",
                "barSigma HLF HRA",
                "Sigma HLA HRF",
            ],
            "boundary_basis_through_dimension_five": [
                (
                    "the two U(1)F Fayet-Iliopoulos coefficients (or an exact symmetry/renormalization "
                    "condition fixing them), because local anomaly cancellation does not by itself forbid a finite FI term"
                ),
                (
                    "all marginal gauge terms: independent W^alpha W_alpha coefficients for every unbroken "
                    "factor and, on the PS wall, the allowed Z_hat Z_hat term for the broken (6,2,2) gauge multiplet"
                ),
                (
                    "all dimension-five gauge-kinetic functions, including STheta Tr(W10^2)/Lambda, "
                    "STheta W_F^2/Lambda and the allowed Phi210 W10 W10/Lambda contraction"
                ),
                "all symmetry-allowed boundary Kahler matrices for traces of bulk hypers and source/PS fields",
                (
                    "the half-integer-dimension PS-wall kinetic mixings Q_i^dagger HLF/sqrt(Lambda) and "
                    "Qc_i^dagger HRA/sqrt(Lambda), or the explicit field redefinition that removes them and "
                    "the induced shifts of every Yukawa/current coefficient"
                ),
                "covariant normal-derivative and wrong-chirality hypermultiplet operators modulo EOM and field redefinitions",
                "all source-field dressings and mixed kinetic terms allowed at dimension five",
            ],
            "variational_certificate": {
                "bulk_boundary_form": "[-f_psi^dagger g_phi+g_psi^dagger f_phi]_0^L",
                "LO_Nambu_condition": "g(L)+B_N f(L)=0 with B_N=B_N^dagger",
                "positive_norm": (
                    "<Psi,Psi>=integral_0^L Psi^dagger Z_bulk Psi + boundary traces contracted with Z_0/Lambda and Z_L/Lambda; require Z_bulk>0 and the full boundary Schur complements >=0"
                ),
                "NLO_rule": (
                    "If kinetic terms make the boundary kernel energy dependent, prove self-adjointness of the "
                    "generalized eigenvalue problem in this positive norm or retain the boundary regulator states."
                ),
            },
            "renormalization_certificate": {
                "allowed_choices": [
                    "finite smooth slab retained at epsilon=Lambda^-1",
                    "finite supersymmetric deconstruction",
                    "thin-brane analytical renormalization with declared one-sided interval normalization",
                ],
                "required": (
                    "Give all finite renormalized coefficients at mu_star, subtract every divergence into the "
                    "enumerated basis, and show two regulator/profile choices agree through O(E/Lambda)."
                ),
            },
            "Wilson_certificate": {
                "exact_structure": "Gamma_eff(p)=Gamma_LL(p)-Gamma_LH(p) Gamma_HH(p)^(-1) Gamma_HL(p)",
                "required_inputs": (
                    "the complete PS and source wall current matrices, the regulated bulk/boundary quadratic "
                    "operator and the same normalization/renormalization scheme"
                ),
                "checks": [
                    "all poles of Gamma_HH^-1 match the retained regulated characteristic",
                    "the p=0 mass kernel reproduces the V47 ker(B_EE) theorem",
                    "the low-energy coefficients are invariant under allowed field redefinitions",
                    "the difference between exact and truncated kernels obeys the declared remainder bound",
                ],
            },
        },
        "V47_retained_positive_results": {
            "G1_closed": v47["scientific_verdict"]["closed_gates"] == ["G1"],
            "all_relevant_neutral_source_terms_included": source["decision"][
                "cross_coupling_policy"
            ]
            == "include, do not sequester by assertion",
            "conditional_Hermitian_extension_self_adjoint": (
                "B=B^dagger"
                in kk["self_adjointness_and_stability"]["source_condition_is_self_adjoint_iff"]
            ),
            "constant_B_zero_mode_count": kk["V46_Theta_Sigma_zero_count"][
                "both_Theta_nonzero"
            ]["total_chiral_component_zero_modes"],
            "homogeneous_characteristic": kk["general_transfer_theorem"]["characteristic_matrix"],
        },
        "decision": {
            "G2_closed_from_V47": False,
            "G2_closed_after_combined_V48": combined["G2_closed"],
            "number_of_mandatory_criteria": len(criteria),
            "number_fully_passed_by_V47": sum(row["passes"] for row in criteria),
            "promotion_now": "REJECT",
            "reason": (
                "The resolved collar closes C2 and the operator artifact improves the PS/source response, "
                "but the parity-resolved NLO action, complete positive norm/counterterms and physical "
                "component Wilson-current match remain incomplete."
            ),
            "promotion_without_UV_completion_is_possible": True,
            "promotion_rule": (
                "Promote G2 only after one explicit fixed-order interval/slab artifact makes all C1--C7 true. "
                "Do not demand an all-order finite catalogue, and do not import G3/G6/G7 obligations into G2."
            ),
        },
        "primary_sources": [
            {
                "topic": "5D N=1 superfield bulk action",
                "url": "https://arxiv.org/abs/hep-th/0106256",
            },
            {
                "topic": "systematic gauge-covariant brane operator basis including normal derivatives",
                "url": "https://arxiv.org/abs/hep-ph/0112230",
            },
            {
                "topic": "interval variational boundary actions uniquely determine boundary conditions",
                "url": "https://arxiv.org/abs/hep-th/0411133",
            },
            {
                "topic": "thin-brane classical renormalization and fixed-order EFT",
                "url": "https://arxiv.org/abs/hep-ph/0601222",
            },
            {
                "topic": "brane kinetic terms, gauge identities and unitarity",
                "url": "https://arxiv.org/abs/hep-ph/0411258",
            },
            {
                "topic": "supersymmetric boundary Fayet-Iliopoulos operators in 5D",
                "url": "https://arxiv.org/abs/hep-ph/0205034",
            },
            {
                "topic": "noncommuting thin-wall and infinite-tower limits",
                "url": "https://arxiv.org/abs/1408.1852",
            },
        ],
    }

    report["integrity_checks"] = {
        "all_input_core_hashes_valid": True,
        "V47_does_not_close_G2": not report["decision"]["G2_closed_from_V47"],
        "closure_is_conjunction_of_seven": (
            report["decision"]["number_of_mandatory_criteria"] == 7
            and report["decision"]["number_fully_passed_by_V47"] == 0
        ),
        "all_order_no_go_has_explicit_neutral_witness": (
            report["all_order_no_go"]["explicit_witness"]["primitive_U1F_charge"] == "-3+3=0"
        ),
        "fixed_order_route_does_not_claim_UV_completion": report["decision"][
            "promotion_without_UV_completion_is_possible"
        ],
        "G2_scope_does_not_absorb_G3_G6_G7_G8": set(
            report["gate_definition"]["excluded_and_owned_elsewhere"]
        )
        == {"G3", "G6", "G7", "G8"},
        "dimension_five_boundary_terms_required": "dimension five"
        in report["smallest_legitimate_construction"]["accuracy_contract"]["recommended_order"],
        "self_adjointness_is_not_promoted_from_conditional_B": (
            next(row for row in criteria if row["id"] == "C3")["V47_state"] == "conditional"
            and not next(row for row in criteria if row["id"] == "C3")["passes"]
        ),
        "combined_V48_only_C2_fully_passes": (
            combined["number_fully_passed"] == 1
            and next(row for row in combined["criteria"] if row["id"] == "C2")["passes"]
        ),
        "PS_spinor_cubic_count_is_19_but_mu_H_is_additional": (
            report["parity_resolved_operator_census"]["PS_zero_derivative_superpotential"]
            ["correct_spinor_cubic_count"]
            == 19
            and "mu_H" in report["parity_resolved_operator_census"]
            ["PS_zero_derivative_superpotential"]["additional_allowed_relevant_operator"]
        ),
        "source_collar_Hc_mirrors_are_recorded": len(
            report["parity_resolved_operator_census"]["source_collar_Hc_test"]
            ["allowed_HcHc_portals"]
        )
        == 4,
    }
    report["n_failed_integrity_checks"] = sum(
        not value for value in report["integrity_checks"].values()
    )
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    criterion_rows = "\n".join(
        f"| {row['id']} | {row['name']} | {row['V47_state']} | {'pass' if row['passes'] else 'fail'} |"
        for row in report["closure_criteria"]
    )
    criterion_details = "\n\n".join(
        f"### {row['id']} — {row['name']}\n\n"
        f"Required: {row['necessary_and_sufficient_output']}\n\n"
        f"V47: {row['V47_evidence']}"
        for row in report["closure_criteria"]
    )
    nlo = "\n".join(
        f"- {item}"
        for item in report["smallest_legitimate_construction"]["boundary_basis_through_dimension_five"]
    )
    wilson_checks = "\n".join(
        f"- {item}" for item in report["smallest_legitimate_construction"]["Wilson_certificate"]["checks"]
    )
    sources = "\n".join(
        f"- [{item['topic']}]({item['url']})" for item in report["primary_sources"]
    )
    combined_rows = "\n".join(
        f"| {row['id']} | {row['state']} | {row['reason']} |"
        for row in report["combined_V48_adversarial_review"]["criteria"]
    )
    census = report["parity_resolved_operator_census"]
    hc_portals = "\n".join(
        f"- `{item}`" for item in census["source_collar_Hc_test"]["allowed_HcHc_portals"]
    )
    return f"""# V48 adversarial G2 closure audit

Status: `{report['status']}`

## Verdict

**The combined V48 artifacts do not close G2.**  The resolved source collar is
a genuine C2 advance, and the operator artifact correctly adds the two
complementary-even-`Hc` PS cubics and improves the Green-function identity.
Only `{report['combined_V48_adversarial_review']['number_fully_passed']}` of the
seven clauses now passes completely.  The retained-order parity-resolved
operator basis, full positive norm/counterterm scheme, and physical component
Wilson-current match are still incomplete.

This is not a demand for a fundamental UV completion.  The smallest legitimate
closure is a one-sided interval Wilsonian EFT, with no new propagating fields,
defined and matched through `O(Lambda^-1)` with a declared
`O(E^2/Lambda^2)` plus loop-order remainder.

## G2 scope

{report['gate_definition']['qualified_scope']}

G2 should not absorb global vacuum selection (G3), the complete numerical KK
threshold/RG problem (G6), baryon-decay matching and likelihoods (G7), or the
flavour/neutrino fit (G8).  Its closure predicate is exactly

`{report['gate_definition']['closure_logic']}`.

## Mandatory clauses

| ID | Clause | V47 state | Closure pass |
|---|---|---|---|
{criterion_rows}

{criterion_details}

## Post-V48 clause review

| ID | State | Adversarial finding |
|---|---|---|
{combined_rows}

## Parity-resolved omissions

At the PS wall the eight non-derivative even bulk traces are the four selected
`H` traces and the four complementary `Hc` traces.  The 19 spinor cubic terms
in the operator artifact are the correct exhaustive cubic count.  They are not
the complete renormalizable PS superpotential: `mu_H epsilon_L epsilon_R H H`
is allowed by PS, `U(1)F`, and matter parity after V47 explicitly withdrew the
inherited `Z4R` selector.

The PS action must also include or explicitly reduce the covariant
normal-derivative `O7/O8` structures and the allowed brane--bulk mixings such
as `Q_i (nabla5 HLFc)_L` and `Qc_i (nabla5 HRAc)_R`.  The source collar does
not replace independent PS-wall counterterms.

The finite collar makes `Hc` nonzero in its interior.  Exact symmetries allow
the conjugate portals

{hc_portals}

For a nonsingular symmetric profile and outer Dirichlet condition these
`Hc Hc` terms begin at `O(epsilon^2 E^2)` and can consistently enter the
declared remainder, but that scaling and the profile symmetry must be part of
the action contract.  A merely one-sided slab does not by itself forbid
localized/source-dependent `Hc H` and mixed `H--Hc` Kähler responses, which
can enter already at `O(epsilon E)`.

## Exact all-order sparsity no-go

The current symmetries do not select a finite boundary action at all orders.
The explicit neutral Kähler invariant

`Y = ThetaPlus^dagger exp(2 q_Theta V_F) ThetaPlus`, with
`q_F(Y)=-3+3=0` and zero R charge,

dresses every allowed D-term by arbitrary powers.  The holomorphic
`X=ThetaPlus ThetaMinus` supplies additional F-term dressings whenever its R
charge permits.  Neutral contractions of `Phi210`, `Sigma barSigma` and
`STheta` give further towers.  Therefore an
all-order finite catalogue cannot be required or claimed without a UV
completion.  The scientifically meaningful non-UV gate is a finite-order
Wilsonian basis with an explicit truncation error.

## Smallest construction that can close G2

Use a genuine interval action with one-sided boundary traces.  Keep the V47
bulk and source fields and its four source spinor superpotential portals.  At
the source and PS walls, add the complete independent boundary basis through
dimension five:

{nlo}

Boundary dimension four alone is not enough for an `O(Lambda^-2)` claim: the
localized kinetic and normal-derivative operators built from 5D hypermultiplet
traces first occur at dimension five and are `O(Lambda^-1)`.

Vary this action rather than inserting an orbifold delta by convention.  At LO
the Nambu boundary condition is `g+B_N f=0`, with `B_N=B_N^dagger`.  At NLO,
use the positive generalized norm

`<Psi,Psi> = integral Psi^dagger Z_bulk Psi + boundary/Lambda`,

and either prove the energy-dependent boundary pencil self-adjoint in that norm
or retain the finite regulator states.  A smooth slab with
`epsilon=Lambda^-1`, finite supersymmetric deconstruction, or a declared
thin-brane analytical subtraction scheme is sufficient; string or other UV
completion is not required.

The matching output is the matrix Schur complement

`{report['smallest_legitimate_construction']['Wilson_certificate']['exact_structure']}`.

It must pass:

{wilson_checks}

## Promotion decision

Current promotion: **{report['decision']['promotion_now']}**.

{report['decision']['reason']}

Promotion remains possible once one explicit V48 interval/slab artifact makes
all C1--C7 true.  It would close only G2; it would not establish a stabilized
vacuum, a full threshold/unification solution, proton stability, flavour or
phenomenological validity.

## Primary sources

{sources}

Core SHA-256: `{report['core_sha256']}`
"""


def write_artifacts() -> dict[str, Any]:
    report = build_report()
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")
    return report


def check_artifacts() -> None:
    report = build_report()
    expected_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
    expected_md = render_markdown(report)
    if not JSON_PATH.is_file() or JSON_PATH.read_text(encoding="utf-8") != expected_json:
        raise RuntimeError("V48 G2 adversarial JSON is missing or stale; run --write")
    if not MD_PATH.is_file() or MD_PATH.read_text(encoding="utf-8") != expected_md:
        raise RuntimeError("V48 G2 adversarial Markdown is missing or stale; run --write")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        print(write_artifacts()["status"])
    if args.check:
        check_artifacts()
        print("V48_G2_ADVERSARIAL_CLOSURE_AUDIT_CHECK_PASS")
    if not args.write and not args.check:
        print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
