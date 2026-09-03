"""F103: restricted parity anomalies, a mass patch and the R2 boundary.

The ordinary smooth Spin x C2 probes here are not asserted to be backgrounds
of the complete normal-split orbifold Gammahat theory. An anomalous global
symmetry is not thereby explicitly broken. No full vacuum or gate is closed.
"""
from __future__ import annotations

import copy
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
import json
from pathlib import Path

import sympy as sp
import v102_full_vev_finite_stabilizer_audit as previous

ROOT = Path(__file__).resolve().parent
PARENTS = {
    "v102_route": ("SUSY_V102_CUBIC_EXCLUSION_COMMON_TENSOR_TARGET_AUDIT.json", "3d3f664328d8e92b069ff75f2f9599287e65703fa37c565e998351e07ea6e79e"),
    "v102_master": ("SUSY_V102_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json", "6c9421c299c4e8976a62a1ba50382e0a88d7ac4c8f289a18b94811d46aff88e5"),
}
EARLIER = {
    "v71": ("SUSY_V71_SPIN11_NORMAL_BUNDLE_EQUIVARIANT_GS_AUDIT.json", "0162828ebd2b1e28d4fcbcf4ea1e6c61178d305cec79abd6d36a55719bb0f1ea"),
    "v91": ("SUSY_V91_SPINC_QUANTIZATION_TENSOR_CONE_FINITE_TORSION_AUDIT.json", "4a581af0dd4cfc6fd3f66ef1e3ea2801b9770c67822d984a02deb602865c0322"),
    "v92": ("SUSY_V92_PROJECTORS_LENS_WCS_COMPACT_DECK_ROOT_AUDIT.json", "3d4365681c9ebdbcbda6d9d57377a1046a6ab00b3a8b1b2290f2858a7ee4f4fb"),
}
FINITE_CORE = "156b8c4965b70a82660f3e18cdd79e69b7e9b8bf8005d52c6bd24bbb2c55b526"
SCHEMA = "v103_locked_parity_R2_mass_patch_Spin_C2_eta_and_even_U_boundary_v1"
canonical_sha, portable_sha = previous.canonical_sha, previous.portable_sha


def load_inputs():
    reports = {}
    for key, (name, core) in {**PARENTS, **EARLIER}.items():
        report = json.loads((ROOT/name).read_text(encoding="utf-8"))
        if report.get("core_sha256") != core or canonical_sha(report) != core:
            raise RuntimeError("noncanonical frozen parity parent: "+key)
        reports[key] = report
    route, master = reports["v102_route"], reports["v102_master"]
    if master["input_core_hashes"]["v102_route"] != PARENTS["v102_route"][1] or master["next_required_action"]["id"] != "F103_HIGHER_SECTION_HEIGHT_ATLAS_AND_GLOBAL_QUANTUM_VACUUM_COMPLETION":
        raise RuntimeError("V102 lineage or F103 obligation changed")
    for key, base in (("v102_route", "susy_v102_cubic_exclusion_common_tensor_target_audit"),
                      ("v102_master", "susy_v102_multipath_g1_frontier_master_audit"),
                      ("v71", "susy_v71_spin11_normal_bundle_equivariant_gs_audit"),
                      ("v91", "susy_v91_spinc_quantization_tensor_cone_finite_torsion_audit")):
        for name, pin in ((base+".py", "generator_sha256"), ("test_"+base+".py", "test_sha256")):
            if portable_sha(ROOT/name) != reports[key]["artifact_hashes"][pin]:
                raise RuntimeError("frozen source/test pin changed: "+name)
    for key, base in (("v102_route", "v102_full_vev_finite_stabilizer_audit"),
                      ("v102_route", "v102_driver_mass_background_audit"),
                      ("v92", "v92_c4_section_eta_certificate")):
        for name in (base+".py", "test_"+base+".py"):
            if portable_sha(ROOT/name) != reports[key]["artifact_hashes"][name]:
                raise RuntimeError("frozen helper source/test pin changed: "+name)
    finite = route["finite_VEV_stabilizer"]
    if finite.get("core_sha256") != FINITE_CORE or canonical_sha(finite) != FINITE_CORE or finite != previous.build_certificate():
        raise RuntimeError("the actual finite parity differs from fresh frozen matrices")
    old = previous.load_inputs()
    reports["R_mass"] = old["v93_R_lift"]["fixed_wall_selection"]
    reports["finite"] = finite
    return reports


def phase_order(value):
    return F(value).denominator


def rp7_complex_xi(charge, spin_shift=0):
    """MM F.1 on round RP7; actual rational xi, before any mod1 or halving."""
    if type(charge) is not int or type(spin_shift) is not int or spin_shift not in (0, 1):
        raise ValueError("integer charge and one of the two spin lifts required")
    # |C2|=2, det(tau(-1)-I)=16, sqrt(det tau)=(-1)^spin_shift.
    return F((-1)**((charge+spin_shift) % 2), 32)


def rp7_hyper_ratio(count, spin_shift=0, orientation=1):
    if type(count) is not int or count < 0 or type(orientation) is not int or orientation not in (-1, 1):
        raise ValueError("nonnegative full-hyper count and orientation sign required")
    paired = 2*count*(rp7_complex_xi(1, spin_shift)-rp7_complex_xi(0, spin_shift))
    # MM 2.18 and2.25: negative chirality hyper, full symplectic pair, then1/2.
    bare = -orientation*paired/2
    return {"full_hyper_count": count, "spin_shift": spin_shift, "orientation": orientation,
            "paired_twisted_minus_trivial_xi_unreduced": str(orientation*paired),
            "negative_chirality_SMW_exponent_unreduced": str(bare),
            "exponent_mod1": str(bare % 1), "phase_order": phase_order(bare)}


def soft_breaking(finite, network):
    before = [tuple(row) for row in finite["written_action_and_full_VEV_stabilizer"]["all_stabilizer_elements_f_k_R"]]
    after = [value for value in before if previous.component_exponent(value, 0, 2) == 0]
    if len(before) != 16 or len(after) != 8 or set(after) != set(product(range(2), (0, 4), (0, 2))):
        raise RuntimeError("the neutral R2 condensate stabilizer changed")
    P = (1, 4, 2)
    if P not in after or previous.component_exponent(P, 0, 2) != 0:
        raise RuntimeError("the R2 condensate lost the locked parity")
    registry = finite["written_action_and_full_VEV_stabilizer"]["bound_V90_operator_registry"]
    forbidden = []
    for row in network[:17]:
        if row["include_in_constant_tensor_system"]:
            continue
        q = sum(registry[name]["U1_8"] for name in row["factors"])
        X = sum(registry[name]["U1_X"] for name in row["factors"])
        R = sum(registry[name]["Z4R"] for name in row["factors"]) % 4
        residues = [(sum(previous.component_exponent(value, registry[name]["U1_8"], registry[name]["Z4R"])
                         for name in row["factors"])-2*previous.theta_exponent(value)) % 8 for value in after]
        if q % 2 != 0 or X != 0 or R != 0 or any(residues):
            raise RuntimeError("an old R-forbidden operator has unexpected residual charges")
        forbidden.append({"operator": row["operator"], "factors": row["factors"], "q8_sum": q,
                          "qX_sum": X, "continuously_gauge_neutral_as_written": q == 0 and X == 0,
                          "scalar_R_sum_mod4": R, "all_eight_residual_action_phases_mod8": residues,
                          "one_neutral_R2_W0_factor_restores_formal_Z4R_covariance": True,
                          "that_factor_alone_restores_continuous_gauge_invariance": q == 0 and X == 0})
    fields = finite["component_characters_and_selection_rule"]["field_character_rows"]
    signatures = []
    for value in after:
        signatures.append((previous.theta_exponent(value), *[previous.component_exponent(value, row["q8_continuous"], row["scalar_R4"], fermion)
                          for row in fields for fermion in (False, True)]))
    if len(set(signatures)) != 8 or len(forbidden) != 4:
        raise RuntimeError("the surviving component action changed")
    return {
        "condensate_assumption": "A Lorentz scalar with continuous gauge charge0 and actual Rtilde charge2 acquires a nonzero value, as in a candidate W0/gaugino-condensate order parameter. Its full normal/flavor tensor representation and hidden dynamics are NOT constructed.",
        "specified_stabilizer_before_order": 16, "specified_stabilizer_after_order": 8,
        "after_elements_f_k_R": [list(value) for value in after],
        "after_group": "<f,g=k^4,Rtilde^2> = C2 x C2 x C2 inside the named H",
        "quotient_by_f_order": 4, "full_selected_character_image_order": 8,
        "P265_survives_this_R2_breaking": True, "P265_f_k_R": list(P),
        "all_order_selection": "Within the displayed selected chiral-field algebra, the surviving g and Rtilde^2 impose q8 parity and scalar R parity separately. The visible fields have equal parities, whereas each extra singlet has even q8 and odd scalar R. Thus any invariant W/K monomial and conjugates in this algebra contain an even number of extra factors. Every insertion of the five VEVs or this neutral R2 order parameter leaves that result unchanged. In the full tower, other P-odd fields count toward total P parity; an even number of these nine selected factors alone is not required when other odd fields occur.",
        "four_previously_forbidden_visible_operators": forbidden,
        "continuous_gauge_caveat": "The bare H_uA H_dC row has q8=12: a neutral W0 insertion alone does not make it continuously gauge invariant. The already-written Phi_minus^2 B0 dressing has total q8=0. Only the residual finite characters, not coefficients or amplitudes, are compared here.",
        "parity_survival_preserves_all_Z4R_proton_and_mu_selectors": False,
        "allowed_operators_are_proved_generated_or_numerically_safe": False,
        "all_soft_terms_or_hidden_sector_realized": False,
        "new_order_parameter_or_operator_adopted": False,
    }


def census(finite, scout):
    blocks = finite["locked_flavor_parity_and_frozen_projectors"]["compressed_blocks"]
    powers = (0, 2, 4)
    total, odd, inserted = ([0]*3 for _ in range(3))
    rows, counts = [], {q: 0 for q in (0, 2, 4, 6, 8)}
    paired_traces = {j: 0 for j in range(5)}
    zero_modes, projected = 0, 0
    for row in blocks:
        n, copies, q, sign = (row[k] for k in ("hypers_per_copy", "copies", "q_magnitude", "P265_sign"))
        P = previous.mass.matrix(row["P265_matrix"])
        Q = sp.diag(*([q]*n+[-q]*n))
        N = copies*n
        counts[q] += N
        local = []
        for j in powers:
            raw = copies*sp.trace(P*Q**j)
            if raw != 2*sign*N*q**j:
                raise RuntimeError("paired SMW insertion trace changed")
            local.append(int(raw/2))
        for j in range(5):
            paired_traces[j] += int(copies*sp.trace(P*Q**j))
        for index, power in enumerate(powers):
            total[index] += N*q**power
            odd[index] += ((1-sign)//2)*N*q**power
            inserted[index] += sign*N*q**power
        if sign == -1:
            zero_modes += row["constant_mode_count"]
            projected += N-row["constant_mode_count"]
        rows.append({"kind": row["kind"], "charge_magnitude": q, "copies": copies,
                     "full_hypers": N, "P_sign": sign, "SMW_half_inserted_moments_0_2_4": local})
    if list(counts.values()) != scout["singlet_counts_by_q0_q2_q4_q6_q8"] or total != [267, 6472, 387808]:
        raise RuntimeError("the actual V91 bulk scout differs from parity blocks")
    if odd != [265, 6344, 379616] or inserted != [-263, -6216, -371424] or (zero_modes, projected) != (9, 256):
        raise RuntimeError("the full parity insertion census changed")
    f, p1, p2 = sp.symbols("f p1 p2")
    index8 = sp.expand(odd[2]*f**4/24-odd[1]*p1*f**2/48+odd[0]*(7*p1*p1-4*p2)/5760)
    return {"block_rows": rows, "charge_order": list(counts), "all_hyper_counts": list(counts.values()),
            "SMW_total_moments_0_2_4": total, "SMW_P_odd_moments_0_2_4": odd,
            "SMW_P_inserted_moments_0_2_4": inserted,
            "full_paired_P_inserted_traces_powers_0_through_4": [paired_traces[j] for j in range(5)],
            "reality_normalization": "Trace over the full conjugate symplectic representation first, then divide by2 once. Every odd charge moment cancels between the paired weights.",
            "odd_hypers_without_selected_constant_zero_modes": projected,
            "selected_odd_zero_modes": zero_modes,
            "positive_index_density_of_full_odd_hyper_representation": str(index8),
            "MM_negative_chirality_anomaly_density": str(-index8),
            "density_scope": "An ordinary continuous-U1 index density for the odd subrepresentation, not the finite-P anomaly or the complete normal/R/flavor anomaly. A flat-P anomaly can survive even when its twisted-minus-trivial local density is zero.",
            "projected_out_modes_can_be_discarded_from_6D_anomaly": False,
            "accidental_265_minus9_multiple16_is_dimensional_anomaly_matching": False}


def mass_patch(R_mass, finite):
    if R_mass["new_wall_tensor"] != "Phi_minus*(S2^T lambda S6 + S4^T kappa S4/2), with lambda=I3,kappa=I3 as a witness":
        raise RuntimeError("the actual nine-mode mass tensor changed")
    phi = sp.Symbol("phi", nonzero=True)
    zero, eye = sp.zeros(3), sp.eye(3)
    unit = sp.BlockMatrix([[zero, zero, eye], [zero, eye, zero], [eye, zero, zero]]).as_explicit()
    M = phi*unit
    P = -sp.eye(9)
    if unit.T != unit or unit**2 != sp.eye(9) or M.det() != -phi**9 or P.T*M*P != M:
        raise RuntimeError("the explicit parity-preserving Majorana mass witness failed")
    extras = [row for row in finite["component_characters_and_selection_rule"]["field_character_rows"] if row["is_extra_selected_mode"]]
    if sorted(row["q8_continuous"] for row in extras) != [2]*3+[4]*3+[6]*3:
        raise RuntimeError("the selected signed charge census changed")
    tr1 = sum(row["q8_continuous"] for row in extras)
    tr3 = sum(row["q8_continuous"]**3 for row in extras)
    return {
        "category": "Selected four-dimensional flat-normal local mass patch with Phi_minus=phi nonzero; continuous parent gauge/normal/flavor backgrounds are not being classified.",
        "field_order": ["S"+str(q)+"_"+str(i) for q in (2, 4, 6) for i in (1, 2, 3)],
        "normalized_symmetric_mass_matrix": previous.mass.matrix_json(unit),
        "determinant": str(M.det()), "rank_for_nonzero_phi": M.rank(),
        "normalized_eigenvalue_multiplicities": {str(k): v for k, v in unit.eigenvals().items()},
        "Takagi_singular_values": ["abs(phi)"]*9,
        "fermion_gap_exists_in_this_quadratic_patch": True,
        "parity_mass_invariance": "(-I9)^T M (-I9)=M; three S2/S6 pairs and three S4 self-masses are all P-even. Nine odd Weyl fermions need not be paired into an even count to gain Majorana masses.",
        "reduced_quantum_test": {
            "ordinary_OmegaSpin5_BC2": "0", "ordinary_OmegaSpin5_point": "0", "Pin_minus_degree4": "0",
            "Smith_identity": "OmegaSpin_d(BC2)=OmegaPin_minus_(d-1)(pt) direct_sum OmegaSpin_d(pt)",
            "Hsieh_n2_raw_cubic_linear_pair": [9, 9], "Hsieh_n2_pair_mod1": ["0", "0"],
            "pure_4D_Spin_times_P_global_anomaly": "trivial",
            "degree6_local_density_with_only_flat_P": "0",
            "mapping_torus_crosscheck": "A constant P transformation gives(-1)^(9 index D4); on a closed spin4 manifold index D4=-signature/8 is even, so the phase is+1. This subset check is not substituted for the full Smith/bordism result.",
            "SpinZ4_or_full_Gammahat_anomaly_inferred": False,
        },
        "continuous_parent_TrQ_TrQ3": [tr1, tr3],
        "continuous_parent_anomaly_erased_by_the_mass": False,
        "independent_normal_covariance": "The actual bulk hyperscalars have no independent normal line while W has the normal character. A globally fixed coefficient needs its normal/tensor completion; the existing local identity does not construct it. The V102 locked cocharacter is not an independent-normal representation.",
        "Phi_zeros_or_defect_matching_completed": False,
        "interacting_scalar_soft_spectrum_or_QK_vacuum_gapped": False,
        "quantum_parity_of_full_compactification_proved": False,
    }


def eta_certificate(trace):
    count = trace["SMW_P_odd_moments_0_2_4"][0]
    rows = [rp7_hyper_ratio(count, spin, orientation) for spin, orientation in product((0, 1), (1, -1))]
    if {row["exponent_mod1"] for row in rows} != {"9/16", "7/16"} or any(row["phase_order"] != 16 for row in rows):
        raise RuntimeError("the reduced six-dimensional parity character changed")
    pair = [previous.quotient(previous.torus_add(previous.torus_scale(previous.FERMION, f), previous.torus_scale(previous.P265, p)))
            for f, p in product(range(2), repeat=2)]
    if len(set(pair)) != 4:
        raise RuntimeError("P was incorrectly identified with fermion parity")
    return {
        "category": "Ordinary smooth six-dimensional bare-fermion scout with spin tangent structure and an independent flat internal C2_P bundle. All other gauge/R/normal backgrounds are trivial. This is a restricted anomaly calculation, not a claim that RP7 is a complete normal-split orbifold background.",
        "P_and_fermion_center_distinct_in_known_kernel": True,
        "four_center_cosets_f_P": [list(row) for row in pair],
        "ordinary_OmegaSpin7_BC2": "Z/16", "ordinary_OmegaSpin7_point": "0",
        "relative_virtual_full_quaternionic_representation": "265*((rho1+rho_minus1)-(rho0+rho0))",
        "same_manifold_ratio": "P-twisted divided by P-trivial at the same metric/spin structure; P-even hyper, vector, tensor and gravity contributions cancel. Subtraction is a reference, not new particles or physical cancellation of the pure gravitational anomaly.",
        "RP7_geometry": "S7/<-I4 on C4>, round metric; stable tangent=4*(complex sign line)_real. Positive scalar curvature and flat unitary twisting imply h=0.",
        "spin_lifts": ["product_i exp(pi*e_(2i-1)e_(2i)/2), i=1..4, with square+1 and sqrt(det tau)=+1", "the first lift multiplied by central-1, sqrt(det tau)=-1"],
        "complex_xi_charge0_charge1_by_spin": [[str(rp7_complex_xi(q, s)) for q in (0, 1)] for s in (0, 1)],
        "formula": "xi_complex(rho_q)=(-1)^(q+spin_shift)/32; negative-hyper anomaly exponent=-1/2 times paired twisted-minus-trivial xi, evaluated as a rational number BEFORE mod1.",
        "one_full_hyper_generator_test": rp7_hyper_ratio(1),
        "all_265_full_hyper_tests": rows,
        "RP7_with_nontrivial_P_is_a_generator": True,
        "generator_proof": "The literature gives a group of order16. The rank-zero virtual eta is a bordism character and evaluates to a primitive16th root for one full hyper, forcing this RP7 class to have order16.",
        "bare_character_class_in_canonical_MM_convention_mod16": count % 16,
        "bare_character_order": 16,
        "necessary_inverse_character_class_mod16": (-count) % 16,
        "inverse_eta_character_is_mathematically_defined": True,
        "inverse_eta_is_a_constructed_same_action_inflow": False,
        "projection_to_nine_modes_replaces_6D_eta": False,
        "full_normal_split_Gammahat_background_admissibility_proved": False,
    }


def wcs_certificate(eta, gs, old_lens):
    imported = gs["smooth_parent_imported_from_V70"]
    if imported["a"] != [2, 2] or imported["b"] != [2, -1] or imported["lattice"] != "U with Omega=[[0,1],[1,0]]":
        raise RuntimeError("the frozen tensor source data changed")
    derivation = old_lens["WCS_derivation"]
    if derivation["polarization"] != "MM4.7: q_U(x*e1+y*e2)=link(x,y)":
        raise RuntimeError("the already derived even-U quadratic convention changed")
    rows = []
    for spin, orientation, t1, t2 in product((0, 1), (1, -1), range(2), range(2)):
        weights = [1+2*spin, 1, 1, 1]
        lam = sum(v*v for v in weights)//2 % 2
        action = orientation*F(t1*t2, 2)
        bare = F(rp7_hyper_ratio(265, spin, orientation)["negative_chirality_SMW_exponent_unreduced"])
        combined = (bare-action) % 1
        if lam != 0 or combined == 0:
            raise RuntimeError("the ordinary even-U parity refinement boundary failed")
        rows.append({"spin_shift": spin, "orientation": orientation, "torsion_label": [t1, t2],
                     "lambda_tangent_mod2": lam, "WCS_action_difference_mod1": str(action % 1),
                     "GS_counterterm_exponent_mod1": str((-action) % 1), "combined_exponent_mod1": str(combined)})
    return {
        "assumptions": ["same ordinary smooth Spin x P scout as the bare eta test", "fixed tensor lattice U and characteristic a=(2,2)",
                        "P acts trivially on the tensor lattice and all nonflavor gauge/R backgrounds are trivial",
                        "only an ordinary degree4 differential-cohomology source refinement is added; no independent eta/TQFT/relative sector is included"],
        "frozen_data": copy.deepcopy(imported),
        "integral_H4_BP_U": "U/2U=(Z/2)^2", "torsion_generator": "u^2, with u=c1(complex sign line)",
        "all_refinement_labels": [[a, b] for a, b in product(range(2), repeat=2)],
        "RP7_linking": "link(u^2,u^2)=+/-1/2; either sign agrees mod1",
        "tangent_lambda_both_spin_lifts_mod2": [0, 0],
        "gravity_cross_term": "Ygrav=(a/2)*lambda_T has zero characteristic here; its cup product with a flat torsion refinement vanishes. The gravity differential cocycle need not be assumed flat.",
        "quadratic_derivation": "MM4.15 makes each null U-axis quadratic zero; polarization4.7 therefore gives q_U(t1u^2 e1+t2u^2 e2)=t1*t2/2. Wu variation4.23 vanishes since U is even and gamma=0. The same-manifold Arf term cancels. MM shifted-source5.2 and conjugate-WCS5.3 retain the counterterm exponent -q.",
        "all_spin_orientation_and_refinement_tests": rows,
        "available_counterterm_exponents_mod1": ["0", "1/2"],
        "all_combined_exponents_mod1": sorted({row["combined_exponent_mod1"] for row in rows}, key=F),
        "number_of_passing_refinement_labels": 0,
        "frozen_parity_independent_source_cancels": False,
        "any_ordinary_even_U_degree4_refinement_cancels": False,
        "ordinary_U_counterterm_character_subgroup_mod16": [0, 8],
        "bare_character_order_modulo_this_counterterm_subgroup": 8,
        "scope_of_rejection": "Only the explicitly stated smooth parity + ordinary even-U WCS cancellation ansatz is rejected. This is not a no-go for extra inflow, different categories, full spin-flavor refinements, localized/relative sectors or a complete microscopic action.",
        "old_V91_gauge_source_sign_dictionary_silently_reconciled": False,
        "all_generalized_Gammahat_GS_extensions_excluded": False,
    }


@lru_cache(maxsize=2)
def derived_json(compact_json):
    p = json.loads(compact_json)
    f = p["finite"]
    trace = census(f, p["scout"])
    eta = eta_certificate(trace)
    return json.dumps({"R2_condensate_and_surviving_selection": soft_breaking(f, p["network"]),
                       "full_SMW_parity_trace_census": trace,
                       "reduced_4D_parity_mass_patch": mass_patch(p["R_mass"], f),
                       "reduced_6D_RP7_eta_character": eta,
                       "ordinary_even_U_WCS_boundary": wcs_certificate(eta, p["GS"], p["old_lens"])}, sort_keys=True)


def build_certificate():
    p = load_inputs()
    compact = {"finite": p["finite"], "network": p["v102_route"]["driver_mass_background"]["source_bound_operator_network"],
               "R_mass": p["R_mass"], "scout": p["v91"]["quantized_scout"],
               "GS": p["v71"]["equivariant_GS_WuCS_boundary"], "old_lens": p["v92"]["ordinary_closed_lens_anomaly_screen"]}
    result = {
        "schema": SCHEMA,
        "status": "RESTRICTED_4D_PARITY_UNOBSTRUCTED__6D_BARE_CHARACTER_9_MOD16__ORDINARY_EVEN_U_REFINEMENT_INSUFFICIENT__FULL_QUANTUM_ACTION_OPEN",
        "input_core_hashes": {**{key: value[1] for key, value in {**PARENTS, **EARLIER}.items()}, "v102_finite": FINITE_CORE},
        **json.loads(derived_json(json.dumps(compact, sort_keys=True))),
        "physical_scope_and_quantum_interpretation": {
            "global_tHooft_anomaly_is_explicit_parity_breaking": False,
            "interpretation": "A nontrivial restricted 't Hooft anomaly obstructs gauging/trivializing that symmetry without further inflow or sectors; it does NOT by itself imply that an exact global symmetry is explicitly broken or that a P-odd particle can decay to P-even states. Mixed ABJ effects on dynamical gauge backgrounds and the full physical status of P require separate analysis.",
            "four_and_six_dimensional_tests_are_not_interchangeable": True,
            "full_P_finite_background_extension_to_normal_split_orbifold_Gammahat_proved": False,
            "unknown_localized_representations_or_flavor_curvatures_discarded": False,
            "full_anomaly_cancellation_or_nonconservation_claimed": False,
            "nonlinear_vacuum_supersymmetry_soft_spectrum_or_cosmology_constructed": False,
            "nine_V93_extra_singlets_are_V65_orphan_quarks": False,
            "new_particles_condensates_counterterms_or_domain_adopted": False,
        },
        "remaining_obligations": {
            "full_Gammahat_P_background_admissibility_and_relative_Dai_Freed": False,
            "full_flavor_GS_and_additional_inflow_completed": False,
            "independent_normal_mass_tensor_and_localized_representations_completed": False,
            "QK_F_D_vacuum_Higgs_zeros_and_soft_R_breaking_completed": False,
            "actual_odd_spectrum_proton_operator_suppression_and_cosmology_completed": False,
            "same_action_parent_accepted": False, "any_gate_closed": False,
        },
        "primary_sources": [
            {"url": "https://arxiv.org/pdf/1808.00009", "use": "Garcia-Etxebarria--MonteroC.17--18: Smith decomposition and ordinary Spin bordism of BC2, with degree5=0 and degree7=Z16. Section2.1 distinguishes a global 't Hooft anomaly from inconsistency of gauging. These are restricted groups, not the full orbifold Gammahat classification."},
            {"url": "https://arxiv.org/pdf/1808.02881", "use": "Hsieh2.16--19 and2.31--32 independently give zero Spin x C2 anomaly for four-dimensional Weyl fermions; Majorana masses are allowed for real one-dimensional parity characters. No SpinZ4 result is substituted for Spin x C2."},
            {"url": "https://arxiv.org/pdf/1808.01334", "use": "Monnier--Moore2.14/2.18/2.25 fix kernel-inclusive xi, SMW factor1/2 and hyperino chirality; F.1--F.9 and7.4 give the exact RP7 eta sum. Equations4.7,4.15,4.19,4.23 and5.2--5.3 give the even-U same-manifold WCS ratio. AppendixB.9 permits torsion source corrections but does not supply the missing spin-flavor/relative completion."},
            {"url": "https://arxiv.org/pdf/1009.0905", "use": "SectionIII discusses R-charge2 order parameters and Z4R to Z2 breaking. Here only the algebraic residual characters are imported; that paper's hidden-sector dynamics, proton suppression and cosmology are not predictions for this incomplete model."},
        ],
    }
    result["core_sha256"] = canonical_sha(result)
    return result


def validate_certificate(report):
    if report.get("core_sha256") != canonical_sha(report) or report != build_certificate():
        raise RuntimeError("F103 parity certificate differs from fresh bound derivation")


if __name__ == "__main__":
    print(json.dumps(build_certificate(), sort_keys=True, indent=2))
