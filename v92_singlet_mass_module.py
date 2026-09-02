"""Conditional four-dimensional mass module for the selected F92 zero modes.

This is an explicit local superpotential ansatz, not a claim of a globally
allowed orbifold interaction or a derived Kähler potential/R-symmetry lift.
"""
from __future__ import annotations

import sympy as sp

import susy_v91_spinc_quantization_tensor_cone_finite_torsion_audit as parent


def local_mass_calculation():
    s2 = sp.symbols("S2_1:4")
    s4 = sp.symbols("S4_1:4")
    s6 = sp.symbols("S6_1:4")
    phi, v = sp.symbols("Phi_minus v")
    fields = s2+s4+s6
    W = phi*(sum(a*b for a,b in zip(s2,s6))+sum(z*z for z in s4)/2)
    origin = {z:0 for z in fields}
    M = sp.hessian(W,fields).subs(phi,v)
    residuals = [sp.diff(W,z).subs(origin) for z in fields+(phi,)]
    normalized = M/v
    if any(residuals) or normalized.T*normalized != sp.eye(9):
        raise RuntimeError("mass module failed its exact F-flatness or rank check")
    return {
        "fields": [str(z) for z in fields], "superpotential": str(W),
        "charges": [2]*3+[4]*3+[6]*3,
        "F_residuals_at_S_zero": [str(z) for z in residuals],
        "mass_matrix_over_v": [[int(z) for z in row] for row in normalized.tolist()],
        "mass_matrix_determinant": str(sp.factor(M.det())),
        "rank_for_v_nonzero": normalized.rank(),
        "rank_for_v_zero": M.subs(v,0).rank(),
        "M_dagger_M_over_abs_v_squared": [[int(z) for z in row] for row in (normalized.T*normalized).tolist()],
    }


def build_certificate(projector_report=None):
    import v92_singlet_projector_certificate as projectors
    if projector_report is None:
        projector_report = projectors.build_certificate()
    if projector_report.get("core_sha256") != projectors.canonical_sha(projector_report):
        raise RuntimeError("noncanonical supplied projector certificate")
    aligned = projector_report["eleven_mode_normal_aligned_witness"]
    expected = [-8,2,2,2,4,4,4,6,6,6,8]
    if aligned["constant_N1_signed_continuous_charges"] != expected:
        raise RuntimeError("mass ansatz requires the selected all-positive extra-mode witness")
    v90 = parent.load_bound(parent.ROOT / parent.PARENTS["v90"][0],parent.PARENTS["v90"][1])
    table = v90["charged_neutral_and_compensator_repair"]["continuous_charge_table"]
    phi = next(row for row in table if row["field"] == "Phi_-")
    if (phi["continuous_U1_8_charge"],phi["Z4R"],phi["U1_X_charge"]) != (-8,0,0):
        raise RuntimeError("retained Phi_minus quantum numbers changed")
    channels = []
    for q1,q2 in ((2,6),(4,4)):
        channels.append({"charges":[-8,q1,q2], "continuous_charge_sum":-8+q1+q2,
                         "finite_C8_sum_mod8":(-8+q1+q2)%8,
                         "assumed_R4_charges":[0,1,1],"R4_sum_mod4":2})
    return {
        "status":"EXACT_LOCAL_MASS_ANSATZ_WITH_NEW_R_ASSIGNMENT__GLOBAL_EXTENSION_OPEN",
        "selected_projector_core_sha256":projector_report["core_sha256"],
        "new_assumptions":[
            "independent Z4R charges of the nine extra N1 chiral fields are one",
            "the inherited Phi_minus has nonzero VEV v and charge(-8,R4=0)",
            "the local cubic superpotential descends from allowed fixed-wall interactions",
            "canonical local Kähler metric and unbroken N1 supersymmetry for the displayed mass spectrum",
        ],
        "R_assignment_was_previously_frozen":False,
        "orbifold_m_is_identified_with_independent_R4":False,
        "charge_checked_channels":channels,
        "calculation":local_mass_calculation(),
        "general_coupling_version":"W=Phi_minus*(S2^T lambda S6 + S4^T kappa S4/2), kappa symmetric",
        "general_full_rank_condition":"v!=0, det(lambda)!=0 and det(kappa)!=0",
        "explicit_dimensionless_couplings":"lambda=I3, kappa=I3",
        "nine_extra_multiplets_massive_in_this_local_ansatz":True,
        "preexisting_F_and_D_equations_unchanged_at_S_zero":True,
        "reason":"all new first derivatives vanish at S=0; new charge contributions to D vanish there",
        "residual_C8_preserved_by_these_mass_terms":True,
        "restores_primitive_C8_in_the_complete_V90_vacuum":False,
        "new_R4_action_descends_through_full_Gammahat_kernel":False,
        "all_localized_operator_representations_constructed":False,
        "full_gauged_Kahler_or_sugra_action_constructed":False,
        "new_sector_full_anomaly_cancelled":False,
        "integrating_out_chiral_fields_erases_anomaly_matching_obligations":False,
        "mass_terms_are_derived_from_the_existing_six_dimensional_action":False,
        "gate_closed":False,
    }
