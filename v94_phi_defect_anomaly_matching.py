"""F94: conditional Phi-string index and its local curvature matching.

This concerns the nine-field 4D mass ansatz, not the full 6D orbifold operator.
The normal bundle below is normal to a string inside ordinary spin spacetime;
it is NOT the codimension-two orbifold normal bundle used in V93's wall audit.
No string solution, differential inflow action, or Pfaffian trivialization is
constructed by checking the characteristic-polynomial identity.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import sympy as sp

import v93_mass_sector_symmetry_descent as parent_mass


ROOT = Path(__file__).resolve().parent
V93_PATH = ROOT / "SUSY_V93_LOCALIZED_ANOMALY_R_LIFT_JACOBIAN_AUDIT.json"
V93_CORE = "4f81852d9e272d3fb12946ad41cb01d9f93462f75cef69123106a80b03f092f2"
MASS_CORE = "c4f752b27ae64d447689e96f1125fc34e6b0b94aeaee95a8ee80f0ed52e6cacf"
SCHEMA = "v94_phi_defect_index_and_curvature_matching_v1"
canonical_sha = parent_mass.projectors.canonical_sha


def portable_file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load_inputs() -> tuple[dict, dict]:
    """Fresh immutable parent and portable source checks on every build."""
    route = json.loads(V93_PATH.read_text(encoding="utf-8"))
    if route.get("core_sha256") != V93_CORE or canonical_sha(route) != V93_CORE:
        raise RuntimeError("F94 requires the canonical V93 route")
    mass = route["smooth_R_and_wall_mass_extension"]
    if mass.get("core_sha256") != MASS_CORE or canonical_sha(mass) != MASS_CORE:
        raise RuntimeError("the bound V93 mass certificate changed")
    for name in ("v93_mass_sector_symmetry_descent.py", "test_v93_mass_sector_symmetry_descent.py"):
        if portable_file_sha(ROOT / name) != route["artifact_hashes"][name]:
            raise RuntimeError("bound V93 source/test changed: " + name)
    if mass != parent_mass.build_certificate():
        raise RuntimeError("V93 mass data fail fresh reconstruction")
    return route, mass


def mass_matrix(phi, lam=None, kap=None) -> sp.Matrix:
    """Ordering S2[3], S4[3], S6[3]; coefficients are constant tensors."""
    lam = sp.eye(3) if lam is None else sp.Matrix(lam)
    kap = sp.eye(3) if kap is None else sp.Matrix(kap)
    if lam.shape != (3, 3) or kap.shape != (3, 3) or kap != kap.T:
        raise ValueError("lambda is 3x3 and kappa must be symmetric 3x3")
    z = sp.zeros(3)
    return phi * sp.BlockMatrix([[z, z, lam], [z, kap, z], [lam.T, z, z]]).as_explicit()


def winding_index(winding: int) -> dict:
    if type(winding) is not int:
        raise ValueError("mass winding must be an integer")
    return {
        "mass_winding": winding,
        "symmetric_mass_determinant_winding": 9*winding,
        "signed_complex_channel_index": 3*winding,
        "signed_real_Majorana_channel_index": 3*winding,
        "signed_total_real_index": 9*winding,
        "signed_chiral_central_charge": str(sp.Rational(9, 2)*winding),
        "signed_gravitational_I4_coefficient_p1T": str(-sp.Rational(3, 16)*winding),
    }


def mass_and_index(mass: Mapping[str, Any]) -> dict:
    phi = sp.symbols("Phi")
    charges = mass["mass_anomaly_matching"]["heavy_left_Weyl_charges"]
    if charges != [2]*3 + [4]*3 + [6]*3:
        raise RuntimeError("heavy charge ordering changed")
    M = mass_matrix(phi)
    allowed = [[charges[i]+charges[j]-8 for j in range(9) if M[i,j] != 0]
               for i in range(9)]
    if any(q != 0 for row in allowed for q in row) or M.det() != -phi**9:
        raise RuntimeError("frozen charge-neutral mass determinant failed")
    # Independent non-diagonal full-rank witness of the general block formula.
    lam = sp.Matrix([[1,2,0], [0,1,3], [1,0,1]])
    kap = sp.Matrix([[2,1,0], [1,3,1], [0,1,2]])
    generic_witness = mass_matrix(phi,lam,kap)
    expected = -phi**9*lam.det()**2*kap.det()
    if sp.expand(generic_witness.det()-expected) != 0:
        raise RuntimeError("general block determinant cross-check failed")
    return {
        "frozen_superpotential": "Phi*(S2^T S6 + S4^T S4/2)",
        "ordered_charges": list(charges),
        "matrix": [[str(x) for x in row] for row in M.tolist()],
        "rank_at_Phi_one": int(M.subs(phi,1).rank()),
        "rank_at_Phi_zero": int(M.subs(phi,0).rank()),
        "determinant": str(M.det()),
        "general_constant_tensor_determinant": "-Phi^9*det(lambda)^2*det(kappa)",
        "general_formula_reason": "Permute to (S2,S6,S4); the 6x6 off-diagonal block has determinant (-1)^3 det(lambda)^2, and the remaining block is kappa.",
        "non_diagonal_check": {"det_lambda":int(lam.det()), "det_kappa":int(kap.det()),
                               "exact_difference":"0"},
        "gapped_boundary_required": "Phi is nonzero on the linking circle and both constant tensors are nonsingular",
        "index_rule": "For the isolated standard vortex operator, det winding counts REAL chiral modes: one complex Dirac channel contributes two, one Majorana channel one.",
        "source_normalization": "Brax et al. section3: (3.29)-(3.30) count real solutions for a Majorana block; (3.41) counts twice the complex solutions for an off-diagonal block. Weinberg's Higgs-winding index supplies homotopy invariance.",
        "orientation_convention": "Positive mass winding defines positive transverse real index. The displayed I4 uses the positive Ahat-index chirality convention; reversing the defect orientation reverses signed anomaly/index data.",
        "winding_samples": [winding_index(n) for n in (-2,-1,0,1,2)],
        "net_index_not_absolute_kernel_count": True,
        "minimal_decoupled_unit_profile_channels": {"complex_chiral":3,"real_chiral":3,"total_real":9},
        "assumptions": [
            "four-dimensional nine-field quadratic ansatz with positive nonsingular kinetic metric and isolated straight string; no extra asymptotically gapless fields mixed into this operator",
            "a smooth vortex profile with nonzero asymptotic mass; regular normalizable modes, and the standard flat-space transverse Fredholm problem",
            "constant full-rank lambda,kappa; opposite-chirality accidental pairs may occur without changing the index",
        ],
        "full_SUGRA_gravitino_gaugino_or_KK_operator_index_computed": False,
        "dynamically_stable_vortex_or_cosmological_abundance_constructed": False,
    }


def topological_patch_constraints(mass: Mapping[str, Any]) -> dict:
    modes = mass["singlet_R_extension"]["constant_mode_R_assignments"]
    phi = next(row for row in modes if row["charge"] == -8)
    if phi["scalar_R"] != 0 or any(row["fermion_R"] != 0 for row in modes if row["charge"] in (2,4,6)):
        raise RuntimeError("selected independent R data changed")
    wall_rows = mass["fixed_wall_selection"]["rows"]
    if any(row["fields"]["Phi_minus"] != {"N1_side":"minus","phase":"1","invariant_projector_rank":1}
           for row in wall_rows):
        raise RuntimeError("the inherited Phi wall component changed")
    return {
        "setting": "ordinary spin spacetime M4, restricted Spin^c(11) gauge bundle, and the isolated V93 4D mass ansatz",
        "determinant_line": "D; d=c1(D)=2*f, where f is the covering U1 curvature",
        "field_line_powers_of_D": {"S2":1,"S4":2,"S6":3,"Phi_minus":-4},
        "no_independent_square_root_of_D_required": True,
        "global_nonvanishing_condition": "Phi_minus nowhere zero trivializes D^4, hence 4*d=0 in integral H2(M4;Z)",
        "nonzero_patch_does_not_cover_arbitrary_gauge_backgrounds": True,
        "torsion_or_discrete_flat_data_removed_by_deRham_f_zero": False,
        "oriented_simple_zero_surface": {
            "notation": "Sigma is an oriented smooth transverse zero; N is its real oriented rank2 normal bundle, viewed as a complex line",
            "Poincare_dual_class": "PD[Sigma]=-4*d",
            "normal_line": "N = D^-4 restricted to Sigma",
            "normal_Chern_root": "nu=-4*d restricted to Sigma",
            "normal_spin_root": "N^(1/2)=D^-2 restricted to Sigma",
            "induced_spin_surface": "Since M4 is spin and N has this spin lift, Sigma inherits a spin structure",
            "normal_is_six_dimensional_orbifold_normal": False,
            "proof": "The derivative of a transverse section identifies its oriented normal plane with the scalar line. Spin(TM4)|Sigma splits into spin(TSigma) and the chosen square root of N.",
        },
        "higher_multiplicity_boundary": "For an order-n zero with leading coefficient nowhere zero, N^n = D^-4|Sigma; the unit-zero normal formula must NOT be copied unchanged to a multiple zero.",
        "closed_spin4_total_zero_surface": {
            "self_intersection": "[Sigma]^2=16*integral(d^2)=32*l",
            "reason": "integral(d^2)=2*l by the even intersection form of a closed spin four-manifold",
            "component_by_component_self_intersection_multiple32_claimed": False,
        },
        "topological_witness": {
            "M4":"S2 x S2", "D":"line with d=a+b", "intersection_relations":"a^2=b^2=0, integral(a*b)=1",
            "integral_d_squared":2, "integral_p1T4":0,
            "PD_total_zero_coefficients_in_a_b":[-4,-4], "total_self_intersection":32,
            "Phi_phase_curvature_period":-9,
            "compatible_gauge_SO11_bundle":"underlying real D plus nine trivial real lines: w2=d mod2 and p1=d^2, admitting determinant D Spin^c lift",
            "holomorphic_or_BPS_section_asserted": False,
        },
        "inherited_R_and_wall_data": {
            "Phi_scalar_independent_R4_charge":0,
            "heavy_fermion_independent_R4_charges":[0]*9,
            "orbifold_wall_characters_of_selected_Phi":[row["fields"]["Phi_minus"]["phase"] for row in wall_rows],
            "new_defect_breaks_selected_independent_R_by_Phi_phase": False,
            "new_assignment_of_unfrozen_wall_normal_charges": False,
        },
    }


def unit_defect_curvature_matching(mass: Mapping[str, Any]) -> dict:
    d,nu,pT,f,pM,phi = sp.symbols("d nu pT f pM phi")
    source = sp.sympify(mass["mass_anomaly_matching"]["local_IR_matching_log_phase_over_2pi_i"])
    source = source.subs({sp.Symbol("x"):f,sp.Symbol("p1"):pM})
    B4 = sp.expand(source/phi)
    if B4 != -18*f*f+sp.Rational(3,16)*pM:
        raise RuntimeError("the V93 phase coefficient changed")
    # From S+(M)|Sigma=(S+(Sigma) S+(N))+(S-(Sigma) S-(N)).
    # The S2 component and conjugate S6 component both twist S+(Sigma) by D^-1.
    complex_twist = 1-2
    conjugate_twist = -3+2
    majorana_twist = 2-2
    if (complex_twist,conjugate_twist,majorana_twist) != (-1,-1,0):
        raise RuntimeError("spin-normal tensor-product weights failed")
    complex_I4 = d*d/2-pT/24
    real_I4 = -pT/48
    defect = sp.expand(3*complex_I4+3*real_I4)
    restricted = sp.expand(B4.subs({f:d/2,pM:pT+nu*nu}).subs(nu,-4*d))
    if sp.expand(restricted+defect) != 0:
        raise RuntimeError("unit-defect curvature matching failed")
    # Independent Euler-residue check of the full 4D anomaly polynomial.
    heavy = 144*f**3-sp.Rational(3,2)*f*pM
    heavy_restricted = sp.expand(heavy.subs({f:d/2,pM:pT+16*d*d}))
    euler_difference = sp.expand(heavy_restricted+(-4*d)*defect)
    if euler_difference != 0:
        raise RuntimeError("Euler-residue index identity failed")
    # A stronger character identity, avoiding division by d at d=0.
    t = sp.symbols("t", nonzero=True)
    ch_odd = sp.Rational(3,2)*sum(t**j-t**(-j) for j in (1,2,3))
    # Ahat(N)=(2*d)/sinh(2*d), and t=exp(d).
    rhs_character = 3*(t+1/t)/2+sp.Rational(3,2)
    char_identity = sp.factor(4*d*ch_odd/(t**2-t**(-2)) - 4*d*rhs_character)
    if char_identity != 0:
        raise RuntimeError("odd-character normal Ahat identity failed")
    return {
        "status":"EXACT_CONDITIONAL_UNIT_DEFECT_CURVATURE_IDENTITY__NOT_A_DIFFERENTIAL_ACTION",
        "spinor_bundle_derivation": {
            "complex_channels":3,"real_channels":3,
            "complex_coefficient_line":"D^-1 (its conjugate gives the same degree4 anomaly)",
            "S2_spin_normal_power":complex_twist,"conjugate_S6_spin_normal_power":conjugate_twist,
            "Majorana_coefficient_line":"real untwisted line in the chosen induced spin splitting",
            "S4_spin_normal_power":majorana_twist,
            "normal_connection_charge_for_complex_channel":"1/4 because -d=nu/4",
            "fractional_normal_charge_needs_mass_determined_fourth_root":True,
            "ordinary_SO2_normal_representations_with_no_extension_claimed":False,
        },
        "complex_chiral_I4":str(complex_I4), "real_chiral_I4":str(real_I4),
        "defect_I4":str(defect),
        "defect_I4_in_normal_root":"3*nu^2/32-3*p1(TSigma)/16",
        "V93_phase_coefficient_B4":str(B4),
        "Whitney_relation":"p1(TM4)|Sigma=p1(TSigma)+nu^2",
        "restricted_phase_coefficient":str(restricted),
        "restricted_B4_plus_defect_I4":"0",
        "Euler_residue_identity":"I6_heavy|Sigma + nu*I4_defect = 0 after nu=-4*d; formal characteristic polynomials, not integrating a6-form on a2-manifold",
        "Euler_residue_exact_difference":str(euler_difference),
        "odd_character_identity":"Ahat(N)*(ch(E)-ch(E*))/2 = -nu*(3*cosh(d)+3/2), E=3*(D+D^2+D^3), nu=-4*d",
        "odd_character_identity_verified":True,
        "tangent_and_defect_normal_curvature_coefficients_both_match":True,
        "pure_gravitational_matching_alone_used":False,
        "bump_form_profile_or_connection_level_transgression_constructed":False,
        "full_inflow_sign_and_Pfaffian_orientation_fixed_on_all_relative_backgrounds":False,
    }


def finite_lift_bookkeeping() -> dict:
    # Primitive k acts by exp(2pi i q/8).  The complex mode combines psi2 and
    # conjugate psi6; a real Majorana mode combines psi4 and conjugate psi4.
    pair = [2%8,(-6)%8]
    majorana = [4%8,(-4)%8]
    if pair != [2,2] or majorana != [4,4]:
        raise RuntimeError("C8 conjugate mode components disagree")
    return {
        "restricted_internal_C8_only":True,
        "complex_mode_component_exponents_mod8":pair,
        "real_mode_component_exponents_mod8":majorana,
        "complex_mode_multiplicity":3,"real_mode_multiplicity":3,
        "Majorana_mode_is_neutral_under_primitive_k":False,
        "kernel_k4_on_this_isolated_defect_sector":True,
        "k_squared_is_total_fermion_parity":False,
        "spin_split_bookkeeping_exponents_mod8": {
            "D":2,"N_D_minus4":0,"normal_spin_root_D_minus2":4,
            "induced_tangent_spin_compensator":4,
            "complex_coefficient_D_minus1":6,"real_coefficient":0,
            "total_complex_after_tangent_spin_compensator":(6+4)%8,
            "total_real_after_tangent_spin_compensator":(0+4)%8,
        },
        "reason":"For a pure internal k the ambient spinor has trivial geometric action. Choosing the equivariant normal spin root D^-2 gives phase -1 under k, so the induced tangent spin splitting carries the compensating -1. Treating the real coefficient line as a neutral physical Majorana would lose this sign.",
        "independent_R4_on_isolated_defect_fermions":0,
        "C8_or_Gammahat_eta_invariant_computed":False,
        "finite_Pfaffian_or_Arf_phase_trivialization_constructed":False,
        "V93_4D_pure_C8_screen_promoted_to_2D_defect_cancellation":False,
    }


def primary_sources() -> list[dict]:
    return [
        {"url":"https://journals.aps.org/prd/abstract/10.1103/PhysRevD.24.2669",
         "use":"Weinberg1981 vortex index relates the asymptotically massive transverse operator to Higgs winding; used only for the isolated standard defect problem."},
        {"url":"https://arxiv.org/abs/hep-th/0604198",
         "use":"Brax et al. section3, equations3.29-3.30 and3.41 distinguish real Majorana counts from complex off-diagonal blocks; section5 explains why gravitino/full-supergravity extensions cannot be inferred."},
        {"url":"https://arxiv.org/abs/hep-th/0509097",
         "use":"Harvey lectures, index-density normalization and axion-string section4; equations133-139 emphasize separate tangent/normal anomalies and the need for normal-bundle regularization."},
        {"url":"https://arxiv.org/abs/hep-th/0007037",
         "use":"Harvey-Ruchayskiy construct regulated bump-form inflow from zero-mode profiles; this additional differential construction is expressly absent here."},
        {"url":"https://stacks.math.columbia.edu/tag/0B3P",
         "use":"Regular divisor normal-line identity; its smooth transverse-section analogue follows directly from the derivative. No holomorphic/BPS string is inferred."},
        {"url":"https://arxiv.org/abs/1808.01334",
         "use":"Ordinary spin versus the gauge quotient and differential/Pfaffian anomaly distinctions; not a proof for the full Gammahat structure."},
    ]


def build_certificate() -> dict:
    _, mass = load_inputs()
    result = {
        "schema":SCHEMA,
        "status":"PASS_CONDITIONAL_PHI_DEFECT_INDEX_AND_TANGENT_NORMAL_CURVATURE_MATCH__GLOBAL_GLUE_OPEN",
        "input_core_hashes":{"v93_route":V93_CORE,"v93_mass":MASS_CORE},
        "mass_and_index":mass_and_index(mass),
        "topological_patch_constraints":topological_patch_constraints(mass),
        "unit_defect_curvature_matching":unit_defect_curvature_matching(mass),
        "finite_lift_bookkeeping":finite_lift_bookkeeping(),
        "limitations": {
            "actual_stable_string_solution_constructed":False,
            "nonspin_or_full_Gammahat_tangential_extension_constructed":False,
            "full_6D_fixed_wall_orbifold_normal_anomaly_cancelled":False,
            "all_KK_and_supergravity_mixing_included":False,
            "differential_action_across_all_Phi_zeroes_constructed":False,
            "torsion_eta_Pfaffian_orientation_or_Dai_Freed_completion_constructed":False,
            "supersymmetric_wall_frame_tensor_completion_constructed":False,
            "same_action_theory_or_any_gate_closed":False,
        },
        "primary_sources":primary_sources(),
    }
    result["core_sha256"] = canonical_sha(result)
    return result


def validate_certificate(report: Mapping[str, Any]) -> None:
    if report.get("core_sha256") != canonical_sha(report) or dict(report) != build_certificate():
        raise RuntimeError("F94 defect certificate differs from the bound fresh derivation")


if __name__ == "__main__":
    print(json.dumps(build_certificate(),indent=2,sort_keys=True))
