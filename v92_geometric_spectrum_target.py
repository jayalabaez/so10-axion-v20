"""Necessary geometric targets of the V91 spectrum, not a realization proof."""
from __future__ import annotations

from fractions import Fraction

import susy_v91_spinc_quantization_tensor_cone_finite_torsion_audit as parent


V91_CORE = "4a581af0dd4cfc6fd3f66ef1e3ea2801b9770c67822d984a02deb602865c0322"
V86_CORE = "799af690205811d97df663ab53dab639c79262a6aac60a37da4394b961a691ad"


def spin11_vector_weights():
    return [[0]*5] + [
        [sign*int(i == j) for j in range(5)]
        for i in range(5) for sign in (-1, 1)
    ]


def weight_census(counts, vector_charges):
    """Count weights neutral under the FULL B5 x U1 Cartan, not B5 alone."""
    if len(counts) != 5 or any(type(n) is not int or n < 0 for n in counts):
        raise ValueError("five nonnegative integer singlet multiplicities required")
    weights = spin11_vector_weights()
    zero_full = sum(not any(w) and q == 0 for q in vector_charges for w in weights)
    total = sum(counts) + len(vector_charges)*len(weights)
    neutral = counts[0] + zero_full
    return {
        "Spin11_vector_weights": weights,
        "vector_hyper_charge_magnitudes": list(vector_charges),
        "Spin11_only_zero_weight_count": len(vector_charges),
        "full_B5_U1_zero_weight_count_from_vectors": zero_full,
        "neutral_under_full_Cartan": neutral,
        "charged_under_full_Cartan": total-neutral,
        "total_H": total,
    }


def build_certificate():
    v91 = parent.load_bound(parent.OUT_JSON, V91_CORE)
    v86 = parent.load_bound(parent.ROOT / "SUSY_V86_SPIN11_HODGE_C4F_U1_PARENT_AHSS_D3_AUDIT.json", V86_CORE)
    scout = v91["quantized_scout"]
    census = weight_census(scout["singlet_counts_by_q0_q2_q4_q6_q8"],
                          scout["bulk_vector_charge_magnitudes"])
    H, V, T = scout["H_V_T"]
    h11_base, rank_b5, rank_mw = T+1, 5, 1
    h11 = h11_base+1+rank_b5+rank_mw
    h21 = census["neutral_under_full_Cartan"]-1
    old = v86["V85_Hodge_retraction_and_Grassi_Morrison_correction"]["conditional_topological_invariants"]
    c = [Fraction(x) for x in scout["c"]]
    height = [int(x) for x in parent.f4_class(c)]
    K = [-2,-6]
    height2 = parent.f4_dot(height,height)
    Kheight = parent.f4_dot(K,height)
    genus = 1+Fraction(height2+Kheight,2)
    if (H, V, T, census["total_H"], H-V+29*T) != (300,56,1,300,273):
        raise RuntimeError("frozen smooth-bulk gravitational ledger changed")
    return {
        "status": "NECESSARY_CONDITIONAL_F_THEORY_TARGET__NO_GEOMETRIC_REALIZATION_CLAIM",
        "input_core_hashes": {"v91":V91_CORE, "v86":V86_CORE},
        "assumptions": [
            "smooth projective crepant Calabi-Yau threefold with flat elliptic fibration over F4",
            "exactly B5 plus one continuous U1, with Mordell-Weil rank one",
            "no additional tensor, vector, SCFT, flux or massless matter sectors",
            "V91 smooth six-dimensional spectrum before finite Higgsing or four-dimensional orbifold projection",
        ],
        "weight_census": census,
        "Shioda_Tate_Wazir_terms": {"base_h11":h11_base, "zero_section":1,
                                   "B5_rank":rank_b5, "Mordell_Weil_rank":rank_mw},
        "necessary_hodge_tuple": {"h11":h11, "h21":h21, "Euler":2*(h11-h21)},
        "neutral_hyper_relation": "h21+1=H_neutral_on_full_Cartan",
        "gravitational_check": H-V+29*T,
        "older_Spin11_only_conditional_hodge_tuple": old,
        "older_tuple_cannot_be_reused_for_this_spectrum": old != {"h11":h11,"h21":h21,"Euler":2*(h11-h21)},
        "conditional_height_class": {
            "convention": "V91 map e1=-F, e2=-(S+2F), with c identified as abelian height only conditionally",
            "class_in_S_F": height, "self_intersection":height2,
            "K_intersection":Kheight, "S_intersection":parent.f4_dot([1,0],height),
            "arithmetic_genus":str(genus),
            "actual_height_pairing_constructed":False,
            "arithmetic_genus_claims_a_smooth_irreducible_height_curve":False,
        },
        "V91_symmetry_member_Mordell_Weil_rank_verified":False,
        "V91_symmetry_member_Hodge_numbers_computed":False,
        "V91_symmetry_member_realizes_scout_spectrum":False,
        "geometric_target_is_existence_or_nonexistence_proof":False,
    }
