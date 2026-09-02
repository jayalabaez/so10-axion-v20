"""F97: an explicit conditional Dirac operator for the frozen mass witness.

The compact equivariant index, the isolated linear-core problem, and a
small-mass compact gap are different statements.  None is an accepted SMW,
supersymmetric, or full Gammahat action.  In particular winding/4 is never
used as a physical multiplicity and the conjugate charge blocks are not
counted as independent SMW fermions.
"""
from __future__ import annotations

import copy
from functools import lru_cache
import hashlib
import json
from pathlib import Path

import sympy as sp

import v96_local_transport_quantization_audit as parent


ROOT = Path(__file__).resolve().parent
PARENTS = {
    "v96_route": ("SUSY_V96_QUANTIZED_RESPONSES_AND_SECTION_FRONTIER_AUDIT.json", "2c1575f64d2aa3414e6b504d72c20a9a76160825aac7389259ac26402ab8f215"),
    "v96_master": ("SUSY_V96_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json", "d8328579f5162e59a855336aa66bff8ca180f1d7062bb066ee241bbed99503b2"),
}
TRANSPORT_CORE = "021441b42d70fa012933e6b213c236822ed3e3424676c55278afcb08ce41c8df"
ZETA = (1+sp.I)/sp.sqrt(2)
I2 = sp.eye(2)
S1 = sp.Matrix([[0, 1], [1, 0]])
S2 = sp.Matrix([[0, -sp.I], [sp.I, 0]])
S3 = sp.diag(1, -1)
m, mb, dp, dm = sp.symbols("m mbar dplus dminus")
xx, yy = sp.symbols("xx yy", real=True)
alpha = sp.Symbol("alpha", positive=True)


def canonical_sha(value):
    body = copy.deepcopy(value)
    body.pop("core_sha256", None)
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def clean(matrix):
    return matrix.applyfunc(sp.simplify)


def matrix_json(matrix):
    return [[str(sp.simplify(v)) for v in row] for row in matrix.tolist()]


def file_sha(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load_parents():
    reports = {}
    for key, (filename, expected) in PARENTS.items():
        value = json.loads((ROOT/filename).read_text(encoding="utf-8"))
        if value.get("core_sha256") != expected or canonical_sha(value) != expected:
            raise RuntimeError("changed or noncanonical F97 index parent: "+key)
        reports[key] = value
    route, master = reports["v96_route"], reports["v96_master"]
    if master["input_core_hashes"]["v96_route"] != PARENTS["v96_route"][1]:
        raise RuntimeError("V96 master-route edge changed")
    if master["next_required_action"]["id"] != "F97_EQUIVARIANT_MASS_DEFECT_INDEX_AND_FULL_RELATIVE_GLUE":
        raise RuntimeError("F97 obligation changed")
    frozen = route["local_transport_quantization"]
    if frozen.get("core_sha256") != TRANSPORT_CORE or canonical_sha(frozen) != TRANSPORT_CORE:
        raise RuntimeError("frozen V96 transport certificate changed")
    for name in ("v96_local_transport_quantization_audit.py", "test_v96_local_transport_quantization_audit.py"):
        if file_sha(ROOT/name) != route["artifact_hashes"][name]:
            raise RuntimeError("frozen transport source or test changed: "+name)
    if parent.build_certificate() != frozen:
        raise RuntimeError("transport generator does not reproduce its bound parent")
    return reports


def projector(rotation, order):
    if order < 1 or clean(rotation**order) != sp.eye(rotation.rows):
        raise ValueError("a finite-order square representation matrix is required")
    return clean(sum((rotation**j for j in range(order)), sp.zeros(rotation.rows))/order)


def index_characters(left, right, order=4):
    return [sp.simplify(sp.trace(left**j)-sp.trace(right**j)) for j in range(order)]


def character_multiplicities(characters):
    if len(characters) != 4:
        raise ValueError("four C4 character values are required")
    values = [sp.simplify(sum(characters[j]*sp.I**(-k*j) for j in range(4))/4) for k in range(4)]
    if any(not v.is_Integer for v in values):
        raise ValueError("these values are not an integral virtual C4 character")
    return [int(v) for v in values]


def charge_block(q):
    if q not in (2, -2):
        raise ValueError("only the bound determinant-line charge pair is in scope")
    h1, h2 = (ZETA**3, ZETA**5) if q == 2 else (ZETA**5, ZETA**3)
    mu, muc, eta = (mb, m, -sp.I) if q == 2 else (m, mb, sp.I)
    left = clean(sp.diag(h1/ZETA, ZETA*h2))
    right = clean(sp.diag(ZETA*h1, h2/ZETA))
    D = sp.Matrix([[dp, mu], [muc, dm]])
    Dag = sp.Matrix([[-dm, mu], [muc, -dp]])
    return {"q": q, "h1": sp.simplify(h1), "h2": sp.simplify(h2),
            "mu": mu, "muc": muc, "eta": eta,
            "left": left, "right": right, "D": D, "Ddag": Dag}


def apply_D(vector, mu, adjoint=False):
    """Actual differential operator, not multiplication of derivative symbols."""
    plus = lambda f: sp.diff(f, xx)+sp.I*sp.diff(f, yy)
    minus = lambda f: sp.diff(f, xx)-sp.I*sp.diff(f, yy)
    if adjoint:
        result = [-minus(vector[0])+mu*vector[1], sp.conjugate(mu)*vector[0]-plus(vector[1])]
    else:
        result = [plus(vector[0])+mu*vector[1], sp.conjugate(mu)*vector[0]+minus(vector[1])]
    return sp.Matrix([sp.simplify(sp.expand(v)) for v in result])


def operator_certificate():
    ax = sp.kronecker_product(S2, I2)
    ay = -sp.kronecker_product(S1, S3)
    br = sp.kronecker_product(S1, S1)
    bi = -sp.kronecker_product(S1, S2)
    grading = sp.kronecker_product(S3, I2)
    normal = -sp.kronecker_product(S3, S3)/2
    gamma6 = sp.kronecker_product(I2, S3)
    clifford = [ax, ay, br, bi]
    checks = {
        "four_Hermitian_Clifford_matrices": all(A.conjugate().T == A and A*A == sp.eye(4) for A in clifford),
        "pairwise_anticommutation": all(A*B+B*A == sp.zeros(4) for i, A in enumerate(clifford) for B in clifford[i+1:]),
        "four_dimensional_chiral_grading": all(grading*A+A*grading == sp.zeros(4) for A in clifford),
        "normal_generator_from_Clifford": normal == sp.I*ax*ay/2,
        "six_dimensional_chirality_relation": gamma6 == (-grading)*(2*normal),
    }
    rows = []
    for q in (2, -2):
        b = charge_block(q)
        transformed = b["D"].subs({dp: sp.I*dp, dm: -sp.I*dm, m: sp.I*m, mb: -sp.I*mb}, simultaneous=True)
        covariance = clean(transformed*b["left"]-b["right"]*b["D"])
        principal = sp.diag(dp, dm)
        kinetic = clean(principal.subs({dp: sp.I*dp, dm: -sp.I*dm}, simultaneous=True)*b["left"]-b["right"]*principal)
        row_checks = {
            "full_jet_covariance": covariance == sp.zeros(2),
            "kinetic_covariance_separately": kinetic == sp.zeros(2),
            "left_and_right_effective_C4": clean(b["left"]**4) == I2 and clean(b["right"]**4) == I2,
            "internal_half_angle_lifts_fourth_minus_one": sp.simplify(b["h1"]**4) == -1 and sp.simplify(b["h2"]**4) == -1,
            "left_constant_projector_zero": projector(b["left"], 4) == sp.zeros(2),
            "right_constant_projector_zero": projector(b["right"], 4) == sp.zeros(2),
        }
        rows.append({"charge": q, "mu": str(b["mu"]), "mass_character": str(b["eta"]),
                     "six_dimensional_plus_internal_H1": str(b["h1"]), "six_dimensional_minus_internal_H2": str(b["h2"]),
                     "left_domain_rotation": matrix_json(b["left"]), "right_codomain_rotation": matrix_json(b["right"]),
                     "D_formal": matrix_json(b["D"]), "D_adjoint_formal": matrix_json(b["Ddag"]), "checks": row_checks})
    if not all(checks.values()) or not all(all(row["checks"].values()) for row in rows):
        raise RuntimeError("conditional Dirac operator or rotation covariance failed")
    return {
        "status": "EXPLICIT_CONDITIONAL_COMPLEX_DIRAC_KINETIC_COMPLETION_NOT_A_FROZEN_MICROSCOPIC_SECTOR",
        "new_assumptions": [
            "Flat square cover torus with side length L, periodic cover spin structure, effective U=V=1 and no transverse gauge or flavor connection.",
            "Promote the V96 virtual plus and minus terms to opposite-six-dimensional-chirality kinetic fields; use H1 on Gamma6=+1 and H2 on Gamma6=-1. This is a proposed quadratic completion, not an inherited six-dimensional supersymmetric multiplet.",
            "Use the ordinary local Dirac principal symbol below and a real mass scale lambda multiplying the frozen smooth M; no extra localized kinetic terms or self-adjoint defect extensions.",
        ],
        "coordinates": "z=s+it; A:z->i*z; dplus=partial_s+i*partial_t=2*partial_bar_z, dminus=partial_s-i*partial_t=2*partial_z",
        "section_convention": "Psi(Az)=R*Psi(z); active action T_A Psi(z)=R*Psi(A^-1 z). Physical sections have T_A=1.",
        "operator": "D_mu=[[dplus,lambda*mu],[lambda*conj(mu),dminus]]: E_L->E_R; Ddag=[[-dminus,lambda*mu],[lambda*conj(mu),-dplus]]",
        "quadratic_action": "L4=i*bar(Psi_L)*slash_partial4*Psi_L+i*bar(Psi_R)*slash_partial4*Psi_R-[bar(Psi_R)*D_mu*Psi_L+h.c.], integrated over the smooth cover and projected to invariant fields",
        "four_dimensional_chiralities": "ker D carries gamma5=-1 (left), ker Ddag carries gamma5=+1 (right); index=left minus right. Reversing this named convention reverses every signed index together.",
        "component_order": "domain(L,+6,N=-1/2 ; L,-6,N=+1/2), codomain(R,+6,N=+1/2 ; R,-6,N=-1/2)",
        "spin_factors": {"domain": ["zeta^-1", "zeta"], "codomain": ["zeta", "zeta^-1"], "zeta": "exp(i*pi/4)"},
        "self_adjoint_transverse_H": "H=[[0,Ddag],[D,0]], H0=alpha_s*k_s+alpha_t*k_t; mass=beta_Re*Re(lambda*mu)+beta_Im*Im(lambda*mu)",
        "Clifford_matrices": {"alpha_s": matrix_json(ax), "alpha_t": matrix_json(ay), "beta_Re": matrix_json(br), "beta_Im": matrix_json(bi), "chiral_grading_left_positive": matrix_json(grading), "normal_generator": matrix_json(normal), "Gamma6": matrix_json(gamma6)},
        "Clifford_checks": checks, "charge_blocks": rows,
        "gauge_representation": "Spin11 singlet in genuine gauge Spin^c11 determinant line D, charge+2; its conjugate charge-2 is required for the V96 symplectic packaging",
        "independent_R_and_flavor_connections_included": False,
        "full_Gammahat_kernel_and_SMW_action_constructed": False,
        "N1_or_6D_supersymmetric_completion_constructed": False,
    }


@lru_cache(maxsize=1)
def local_oscillator_math():
    generic = sp.Matrix([sp.Function("a")(xx, yy), sp.Function("b")(xx, yy)])
    osc = sp.Matrix([-sp.diff(v, xx, 2)-sp.diff(v, yy, 2)+alpha**2*(xx**2+yy**2)*v for v in generic])
    gaussian = sp.exp(-alpha*(xx**2+yy**2)/2)
    rows = []
    for winding in (1, -1):
        mu = alpha*(xx+sp.I*winding*yy)
        DD = apply_D(apply_D(generic, mu), mu, adjoint=True)
        DDag = apply_D(apply_D(generic, mu, adjoint=True), mu)
        target_DD = osc-2*alpha*S1*generic if winding == 1 else osc
        target_DDag = osc if winding == 1 else osc+2*alpha*S1*generic
        zero = gaussian*sp.Matrix([1, winding])
        checks = {
            "DdagD_oscillator_identity": clean(DD-target_DD) == sp.zeros(2, 1),
            "DDdag_oscillator_identity": clean(DDag-target_DDag) == sp.zeros(2, 1),
            "explicit_Gaussian_zero_mode": apply_D(zero, mu, adjoint=winding == -1) == sp.zeros(2, 1),
        }
        if not all(checks.values()):
            raise RuntimeError("linear core differential identities failed")
        rows.append({"mass_winding": winding, "mu": str(mu), "kernel": "D" if winding == 1 else "Ddag",
                     "zero_mode_unnormalized": [str(v) for v in zero], "normalization_factor": "sqrt(alpha/(2*pi))",
                     "DdagD": "Hosc*I-2*alpha*sigma1" if winding == 1 else "Hosc*I",
                     "DDdag": "Hosc*I" if winding == 1 else "Hosc*I+2*alpha*sigma1",
                     "complex_kernel_dimensions_D_Ddag": [1, 0] if winding == 1 else [0, 1], "checks": checks})
    return rows


def localized_index_certificate():
    # A exchanges the two C2 points. In a chosen local-mode basis, A^2=-1
    # is represented by this induced two-dimensional C4 matrix.
    induced = sp.Matrix([[0, -1], [1, 0]])
    rows = []
    for q in (2, -2):
        b = charge_block(q)
        for point, order, wm in (("z00", 4, 1), ("z11", 4, 1), ("z10", 2, -1), ("z01", 2, -1)):
            wmu = -wm if q == 2 else wm
            action = b["left"] if wmu == 1 else b["right"]
            stabilizer = clean(action**(4//order))
            zero_vector = sp.Matrix([1, wmu])
            image = clean(stabilizer*zero_vector)
            phase = sp.simplify(image[0])
            if image != phase*zero_vector or phase != -1:
                raise RuntimeError("core zero mode is not the frozen odd stabilizer character")
            P = projector(sp.Matrix([[phase]]), order)
            rows.append({"cover_point": point, "stabilizer_order": order, "continuous_charge": q,
                         "winding_of_m": wm, "winding_of_this_mu": wmu,
                         "four_dimensional_chirality": "left" if wmu == 1 else "right",
                         "complex_core_index_before_projection": wmu,
                         "stabilizer_phase_on_Gaussian_mode": str(phase), "local_projector": matrix_json(P),
                         "linear_core_invariant_kernel_dimension": int(P.rank())})
    return {
        "status": "EXACT_ISOLATED_LINEAR_CORE_INDEX_AND_PROJECTORS_NOT_AN_EXACT_COMPACT_SPECTRUM",
        "local_linearization": "The bound simple zeros and poles of g give m=a*z+O(|z|^2) or m=conj(a*z)+O(|z|^2), a!=0. A constant component rephasing and rescaling give mu=alpha*z or alpha*bar(z), alpha>0.",
        "oscillator_definition": "Hosc=-partial_s^2-partial_t^2+alpha^2*(s^2+t^2), eigenvalues 2*alpha*(n_s+n_t+1)",
        "unique_kernel_proof": "The oscillator ground state is unique. Exactly one sigma1 eigenspace cancels its energy in DdagD or DDdag; the opposite square has strictly positive spectrum. This proves one complex core mode before projection for the stated linear operator, not for an unspecified fermion-vortex action.",
        "linear_core_calculations": local_oscillator_math(), "per_cover_charge_block": rows,
        "physical_C2_orbit_representation": {"generator_A": matrix_json(induced), "A_squared": matrix_json(induced**2),
                                               "character": [str(sp.trace(induced**j)) for j in range(4)],
                                               "decomposition": "chi1+chi3=Ind_C2^C4(sign)", "projector": matrix_json(projector(induced, 4)), "invariant_dimension": 0},
        "number_of_invariant_protected_linear_core_modes": 0,
        "cover_winding_divided_by_stabilizer_or_cover_degree_used_as_multiplicity": False,
        "linear_core_models_are_exact_solutions_of_frozen_global_profile": False,
        "large_mass_localization_requires_additional_spectral_control": True,
        "absence_of_any_accidental_compact_paired_zero_modes_at_arbitrary_mass_proved": False,
    }


def compact_index_certificate():
    rows = []
    induced = sp.Matrix([[0, -1], [1, 0]])
    for q in (2, -2):
        b = charge_block(q)
        chars = index_characters(b["left"], b["right"])
        local_chars = [sp.simplify((1 if q == 2 else -1)*(sp.trace(induced**j)-2*(-1)**j)) for j in range(4)]
        mult = character_multiplicities(chars)
        if chars != local_chars or mult[0] != 0:
            raise RuntimeError("compact Fourier index and localized induced character disagree")
        rows.append({"charge": q, "characters_identity_A_A2_A3": [str(v) for v in chars],
                     "multiplicities_chi0_chi1_chi2_chi3": mult,
                     "cover_signed_index": int(chars[0]), "invariant_signed_index": mult[0],
                     "local_induced_character_matches_all_four_elements": True,
                     "minimum_cover_kernel_dimensions_left_right_from_character": [sum(max(v, 0) for v in mult), sum(max(-v, 0) for v in mult)]})
    return {
        "status": "EXACT_COMPACT_EQUIVARIANT_INDEX_FOR_THE_CONDITIONAL_OPERATOR_AT_EVERY_FINITE_MASS",
        "zero_mass_proof": "On the periodic flat cover, each dplus or dminus has only constant functions in its kernel and cokernel. The constant fibers carry the displayed left and right matrices, so Ind_C4(D0)=[R_left]-[R_right] exactly; nonzero Fourier modes cancel equivariantly.",
        "homotopy_proof": "D_lambda:H1(T2,E_L)->L2(T2,E_R) is elliptic and C4-equivariant with fixed principal symbol. Smooth mass multiplication is a compact lower-order perturbation in this map, so its index in R(C4) is constant along finite lambda.",
        "orbifold_index_formula": "index(D_lambda on invariants)=(1/4)*sum_j trace(A^j on virtual kernel); this is an integer representation multiplicity, not the identity-sector contribution alone",
        "charge_block_results": rows,
        "selected_orbifold_chiral_index": 0,
        "zero_index_proves_zero_total_kernel": False,
        "charge_plus_cover_protected_character": "chi1+chi3-2*chi2",
        "charge_minus_cover_protected_character": "2*chi2-chi1-chi3",
        "same_conclusion_for_arbitrary_smooth_equivariant_mass_with_same_symbol_and_bundles": True,
        "same_conclusion_for_unfrozen_fluxes_or_boundary_domains": False,
    }


def reality_certificate():
    plus, minus = charge_block(2), charge_block(-2)
    conjugation = {dp: dm, dm: dp, m: mb, mb: m}
    conjugated_D = plus["D"].subs(conjugation, simultaneous=True)
    conjugated_Ddag = plus["Ddag"].subs(conjugation, simultaneous=True)
    checks = {
        "D_minus_dag_sigma3_equals_minus_sigma3_conjugate_D_plus": minus["Ddag"]*S3 == -S3*conjugated_D,
        "D_minus_sigma3_equals_minus_sigma3_conjugate_D_plus_dag": minus["D"]*S3 == -S3*conjugated_Ddag,
        "left_plus_conjugates_to_right_minus_rotation": clean(minus["right"]*S3-S3*sp.conjugate(plus["left"])) == sp.zeros(2),
        "right_plus_conjugates_to_left_minus_rotation": clean(minus["left"]*S3-S3*sp.conjugate(plus["right"])) == sp.zeros(2),
        "index_characters_are_negative_conjugates": all(sp.simplify(a+sp.conjugate(b)) == 0 for a, b in zip(index_characters(minus["left"], minus["right"]), index_characters(plus["left"], plus["right"]))),
    }
    if not all(checks.values()):
        raise RuntimeError("charge-conjugate transverse kernel relations failed")
    return {
        "status": "EXACT_TRANSVERSE_ANTILINEAR_KERNEL_PAIRING_NOT_A_FULL_SIX_DIMENSIONAL_SMW_CONSTRUCTION",
        "zero_mode_map": "C_perp(v)=sigma3*conj(v): ker D_plus -> ker D_minus_dag and ker D_plus_dag -> ker D_minus; it reverses charge and four-dimensional chirality",
        "checks": checks,
        "independent_physical_Weyl_multiplicity_is_sum_of_two_complex_charge_tables": False,
        "SMW_scope": "V96 supplies J*conj(M)=M*J in flavor space. The transverse map verifies the necessary conjugate pairing including rotation phases. The Lorentz charge-conjugation matrix, symplectic reality condition, kinetic measure and Pfaffian regulator of a new opposite-6D-chirality sector are still required; no additional factor or physical multiplicity is asserted from this complex calculation.",
        "conjugate_charge_block_must_not_be_counted_twice": True,
    }


def gap_certificate():
    s = sp.Symbol("s", nonnegative=True)
    difference = sp.factor(sp.Rational(1, 2)-s/(1+s*s))
    if sp.cancel(difference-(s-1)**2/(2*(s*s+1))) != 0:
        raise RuntimeError("uniform regularized mass bound failed")
    return {
        "status": "EXACT_NONZERO_MASS_COMPACT_GAP_IN_AN_EXPLICIT_PARAMETER_RANGE",
        "mass_modulus": "|m|=s/(1+s^2), s=|g|", "half_minus_modulus": str(difference), "uniform_bound": "|m|<=1/2, including its zero extension at poles",
        "zero_mass_projected_singular_gap": "2*pi/L",
        "gap_proof": "All invariant domain and codomain sections have zero constant Fourier coefficient because their constant C4 projectors vanish. Every nonconstant momentum has |k|>=2*pi/L. Hence ||D0*v||>=2*pi/L*||v||, with the same estimate for D0dag; its invariant inverse exists. The off-diagonal mass multiplication has norm<=|lambda|/2.",
        "lower_bound_on_projected_singular_gap": "2*pi/L-|lambda|/2",
        "strict_invertibility_condition": "|lambda|*L<4*pi",
        "left_and_right_projected_kernel_dimensions_in_that_range": [0, 0],
        "nonzero_mass_example": "lambda=2*pi/L gives lower bound pi/L>0 although M vanishes at all four frozen cover points",
        "Neumann_inverse": "D_lambda^-1=(1+D0^-1*B_lambda)^-1*D0^-1 when ||D0^-1*B_lambda||<=|lambda|*L/(4*pi)<1",
        "bound_is_for_selected_smooth_domain_and_no_transverse_connections": True,
        "gap_at_every_mass_or_with_extra_backgrounds_established": False,
        "forced_mass_zeros_alone_force_physical_massless_fields": False,
        "absence_of_massless_modes_cancels_local_anomalies": False,
    }


def alternate_character_certificate():
    rows = []
    for s in range(4):
        b = charge_block(2)
        twist = sp.I**s
        chars = index_characters(twist*b["left"], twist*b["right"])
        index = character_multiplicities(chars)[0]
        c4_phase, c2_phase = -twist, -twist**2
        local = -2*int(projector(sp.Matrix([[c4_phase]]), 4).rank())+int(projector(sp.Matrix([[c2_phase]]), 2).rank())
        if index != local:
            raise RuntimeError("common character counterfactual violates index integrality")
        rows.append({"neutral_common_C4_weight": s, "plus_charge_invariant_index": index,
                     "local_C4_phase": str(c4_phase), "local_C2_phase": str(c2_phase),
                     "mass_intertwiner_ratio_unchanged": True, "is_the_frozen_absolute_lift": s == 0})
    return {
        "status": "COUNTERFACTUAL_UNDERDETERMINATION_TEST_NOT_AN_ADOPTED_NEW_TWIST",
        "operation": "Multiply both H1 and H2 on charge+2 by i^s and both conjugate entries by i^-s; M and its divisor are unchanged, but absolute rotation lifts change unless s=0.",
        "rows": rows,
        "same_mass_function_determines_unique_projected_index_without_absolute_lifts": False,
        "nonzero_common_twists_preserve_frozen_V96_twists": False,
        "these_alternative_twists_are_accepted_Gammahat_or_R_flavor_extensions": False,
        "new_curvatures_and_global_anomalies_of_alternatives_computed": False,
    }


def certificate_content():
    load_parents()
    return {
        "schema": "v97_equivariant_mass_defect_index_v1",
        "input_core_hashes": {k: v[1] for k, v in PARENTS.items()},
        "embedded_v96_transport_core": TRANSPORT_CORE,
        "scope": "An explicit conditional kinetic completion: exact isolated linear-core projectors, compact equivariant index, conjugate kernel pairing, and a rigorous small-mass compact gap. No full orbifold relative anomaly cancellation or new accepted matter sector.",
        "conditional_Dirac_operator": operator_certificate(),
        "isolated_core_index_and_projection": localized_index_certificate(),
        "compact_equivariant_index": compact_index_certificate(),
        "charge_reality_and_counting": reality_certificate(),
        "small_mass_compact_gap": gap_certificate(),
        "common_character_counterfactual": alternate_character_certificate(),
        "remaining_action_data": [
            "A full Gammahat-compatible opposite-six-dimensional-chirality field content, actual SMW kinetic/Pfaffian reality, and supersymmetric interactions if required.",
            "The mass scale, torus metric and transverse gauge/R/flavor backgrounds of the same action, plus any allowed localized terms and global domain.",
            "If arbitrary-mass kernel multiplicities are wanted, a compact spectral calculation or a stronger vanishing theorem; index zero alone is insufficient.",
            "The anomaly of the selected dynamical sector with all normal/R/flavor curvatures, its finite/global determinant phase and a common quantized relative inflow/gluing; a gap does not establish any of these.",
        ],
        "terminal_decision": {
            "conditional_kinetic_covariance_and_compact_index_computed": True,
            "frozen_lift_invariant_chiral_index": 0,
            "protected_isolated_linear_core_modes_surviving_projection": 0,
            "exact_no_zero_modes_for_abs_lambda_L_less_than_4pi": True,
            "all_mass_scales_compact_spectrum_determined": False,
            "full_SMW_Gammahat_same_action_sector_constructed": False,
            "mixed_gauge_or_finite_relative_anomaly_canceled_by_this_calculation": False,
            "all_possible_defect_completions_excluded": False,
            "accepted_extensions": 0, "closed_gates": [], "same_action_parent_accepted": False,
        },
        "primary_sources": [
            {"url": "https://arxiv.org/abs/1609.01413", "use": "Equations2.12-2.22 distinguish 4D, normal and 6D chirality and show that an ordinary 6D mass couples opposite 6D chiralities. The selected torus operator and lifts here are derived explicitly, not taken from that paper's rectangle boundary conditions."},
            {"url": "https://journals.aps.org/prd/abstract/10.1103/PhysRevD.24.2669", "use": "Weinberg's first-order fermion-vortex index problem relates Higgs topology to an operator index. It does not by itself specify the present compact orbifold action or physical field count."},
            {"url": "https://arxiv.org/abs/2303.03425", "use": "Equations2.13-2.17 exhibit chiral transverse derivative/Yukawa equations and angular mode constraints. Our simple-core Gaussian and oscillator identities are independently computed for the stated operator, not inferred from a Majorana zero-mode count in a different model."},
            {"url": "https://arxiv.org/abs/1908.05165", "use": "Equivariant elliptic indices are integer representation multiplicities; finite-group projectors and Fredholm domains. The present character is computed directly from periodic Fourier zero modes."},
            {"url": "https://arxiv.org/abs/math/0701768", "use": "Orbifold index from equivariant data includes nonidentity stabilizers; supports the distinction from dividing a cover contribution alone by four."},
        ],
    }


def build_certificate():
    result = certificate_content()
    result["core_sha256"] = canonical_sha(result)
    return result


def validate_certificate(result):
    if result.get("core_sha256") != canonical_sha(result) or result != build_certificate():
        raise RuntimeError("F97 mass index arithmetic, lineage, assumptions or scope changed")


if __name__ == "__main__":
    print(json.dumps(build_certificate(), indent=2, sort_keys=True))
