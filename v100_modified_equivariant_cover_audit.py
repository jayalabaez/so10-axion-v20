"""F100: the minimal simultaneous operator cover and its smooth response.

The cover, pulled-back square-group relations and quantized inverse response
are explicit.  Neither the changed category nor its ineffective space-group
extension is adopted as a physical parent or a relative orbifold construction.
"""
from __future__ import annotations

import copy
from functools import lru_cache
import hashlib
from itertools import product
import json
from pathlib import Path
from typing import Mapping

import sympy as sp

import v99_determinant_root_descent_audit as previous


ROOT = Path(__file__).resolve().parent
PARENTS = {
    "v99_route": ("SUSY_V99_QUOTIENT_OBSTRUCTIONS_NORMAL_PAIR_SECTION_AUDIT.json",
                  "240bf71045bda94015027eccbaeebec93fc2caa8940a5dd100e914ad24330c4e"),
    "v99_master": ("SUSY_V99_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
                   "72c499490e86c3b9da3e436d95bc6d7b9907806f214ac491be1336b310e2fd39"),
}
PREVIOUS_CORE = "7e4e94ce9d566b9f54f56b17d9065759ec49707254612ef9d139fc0550de881c"
SCHEMA = "v100_minimal_combined_operator_cover_and_quantized_smooth_inverse_v1"
canonical_sha = previous.canonical_sha
lift = previous.lift_parent
D, KT, KN, KS = previous.DGEOM, previous.KT, previous.KN, previous.KS
CCHAR, SIGMA = previous.CCHAR, previous.SIGMA
c, x, p = sp.symbols("c x p")
IDENTITY = (0, 0, 0, 0)
A, U, V = (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0)
EPS_T, EPS_S = (4, 0, 0, 0), (0, 0, 0, 1)


def portable_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load_inputs() -> dict:
    reports = {}
    for key, (name, core) in PARENTS.items():
        data = json.loads((ROOT/name).read_text(encoding="utf-8"))
        if data.get("core_sha256") != core or canonical_sha(data) != core:
            raise RuntimeError("F100 requires immutable canonical V99 parents: " + key)
        reports[key] = data
    route, master = reports["v99_route"], reports["v99_master"]
    if master["input_core_hashes"]["v99_route"] != PARENTS["v99_route"][1]:
        raise RuntimeError("V99 master-to-route edge changed")
    if master["next_required_action"]["id"] != "F100_MODIFIED_EQUIVARIANT_ACTION_AND_ORIGINAL_SECTION_EXISTENCE":
        raise RuntimeError("the F100 obligation changed")
    saved = route["determinant_root_descent"]
    if saved.get("core_sha256") != PREVIOUS_CORE or canonical_sha(saved) != PREVIOUS_CORE:
        raise RuntimeError("the frozen V99 determinant-root helper changed")
    for name in ("v99_determinant_root_descent_audit.py", "test_v99_determinant_root_descent_audit.py"):
        if portable_sha(ROOT/name) != route["artifact_hashes"][name]:
            raise RuntimeError("frozen V99 source/test pin changed: " + name)
    if saved != previous.build_certificate():
        raise RuntimeError("V99 determinant-root certificate differs from fresh derivation")
    older = []
    for name, core in (("SUSY_V88_B_NEUTRAL_GAMMAHAT_CARTAN_ANOMALY_CORRECTION_AUDIT.json", lift.V88_CORE),
                       ("SUSY_V89_C8_LOCALIZED_BV_COMPACT_GLOBALIZATION_AUDIT.json", lift.V89_CORE)):
        data = json.loads((ROOT/name).read_text(encoding="utf-8"))
        if data.get("core_sha256") != core or canonical_sha(data) != core:
            raise RuntimeError("the actual saved square-group lift changed")
        older.append(data)
    reports["old_smooth_lift"] = older[0]["B_neutral_Gammahat_lift"]
    reports["old_finite_lift"] = older[1]["C8_space_group_enumeration"]
    return reports


def combined_kernel():
    return [k for k in lift.old_kernel() if lift.dot(CCHAR, k) == lift.dot(SIGMA, k) == 0]


def deck_bits(k):
    k = lift.bits(k, 7)
    if k not in lift.old_kernel():
        raise ValueError("deck labels require an element of the old kernel")
    return lift.dot(SIGMA, k), lift.dot(CCHAR, k)


def cover_certificate() -> dict:
    old, combined = lift.old_kernel(), combined_kernel()
    if combined != lift.span((D,)) or len(combined) != 2:
        raise RuntimeError("the simultaneous operator kernel changed")
    c_kernel = [k for k in old if lift.dot(CCHAR, k) == 0]
    sigma_kernel = [k for k in old if lift.dot(SIGMA, k) == 0]
    if c_kernel != lift.span((D, KT)) or sigma_kernel != lift.span((D, KS)):
        raise RuntimeError("the two independent double-cover kernels changed")
    candidates = {tuple(lift.span((D,)+tuple(k for k, keep in zip(old, mask) if keep)))
                  for mask in product(range(2), repeat=len(old))}
    intermediate = []
    for kernel in sorted(candidates, key=lambda row: (len(row), row)):
        intermediate.append({"kernel": [list(k) for k in kernel], "cover_degree": len(old)//len(kernel),
                             "C_descends": not any(lift.character_descent(CCHAR, kernel)),
                             "Sigma_c_descends": not any(lift.character_descent(SIGMA, kernel))})
    simultaneous = [row for row in intermediate if row["C_descends"] and row["Sigma_c_descends"]]
    if len(intermediate) != 5 or len(simultaneous) != 1 or simultaneous[0]["cover_degree"] != 4:
        raise RuntimeError("minimal intermediate-cover classification failed")
    old_chars = [a for a in product(range(2), repeat=7) if not any(lift.character_descent(a, old))]
    if len(old_chars) != 16 or any(any(lift.character_descent(a, combined)) for a in old_chars):
        raise RuntimeError("an old representation failed pullback")
    operators = []
    for n in range(3):
        char = tuple((a+n*b) % 2 for a, b in zip(SIGMA, CCHAR))
        operators.append({"C_power": n, "character": list(char),
                          "combined_kernel_exponents": lift.character_descent(char, combined),
                          "deck_exponents_epsT_epsS": [lift.dot(char, KT), lift.dot(char, KS)]})
    return {
        "coordinate_order": lift.OLD_COORDINATES,
        "old_kernel_generators": {"D_geom": list(D), "KT": list(KT), "KN": list(KN), "KS": list(KS)},
        "old_kernel": [list(k) for k in old], "C_only_kernel": [list(k) for k in c_kernel],
        "Sigma_only_kernel": [list(k) for k in sigma_kernel], "combined_kernel": [list(k) for k in combined],
        "all_five_intermediate_covers_preserving_D_geom": intermediate,
        "minimum_simultaneous_operator_cover_degree": 4,
        "minimality_scope": "Intermediate central covers of the fixed product cover, retaining the stated individual C and Sigma_c representations and the literal geometric identity D. This is not minimality among every possible combined response, extra representation or different tangential construction.",
        "deck_group": "K/<D_geom> = C2_T x C2_S",
        "old_kernel_to_deck_labels": [{"old_kernel_element": list(k), "epsT_epsS": list(deck_bits(k))} for k in old],
        "deck_representatives": {"epsT": list(KT), "epsS": list(KS)},
        "KN_equals_KT_mod_D": tuple((a+b) % 2 for a, b in zip(KN, KT)) == D,
        "new_group": "Gamma_combined=Ccover/<D_geom>, with projection to Gamma_known=Ccover/<D_geom,KT,KS>",
        "continuous_restriction_isomorphism": "Spin^c(T;N) x Spin11 x Sp1_R x H3 x H267 x U1_C; here Spin^c(T;N)=(Spin(T) x Spin2_N)/<(-1,-1)> and N is the normal determinant line",
        "finite_restriction_isomorphism": "Replace U1_C by C8. C=rho1 is now a genuine line and D_gauge=C^2=rho2. This is a cover of the known finite quotient, not an extra independent gauge factor beside it.",
        "anomaly_dimension_stabilization": "Use Spin^c(5) for the closed5 eta response and Spin^c(6) for its index periods. The physical normal reduction starts with Spin4_T x Spin2_N; no full unknown physical Gammahat category is identified by this stabilization.",
        "C_character": list(CCHAR), "Sigma_c_character": list(SIGMA),
        "bare_eta_operator_rows": operators,
        "all_old_16_center_characters": [list(a) for a in old_chars],
        "all_genuine_old_representations_pull_back": True,
        "pullback_proof": "For any actual old representation rho, rho_new=rho composed with the surjective projection. Its matrices, dimensions, old R/flavor representations, invariant bilinears and SMW reality operator are unchanged; both deck generators act trivially. The center enumeration checks all16 allowed parity characters independently.",
        "every_old_background_bundle_lifts_to_this_cover": False,
        "background_lift_scope": "Representation pullback is automatic, but a given old principal bundle need not lift. Local lifts of its transition functions have triple-overlap defects in the central C2_T x C2_S; a combined lift requires that obstruction cocycle to be trivialized. The changed category retains such a lift, not just the old quotient connection.",
        "previously_unconstructed_old_field_representations_promoted": False,
        "new_eta_levels_are_positive_particle_multiplicities_or_SMW_halves": False,
        "M_half_normal_line_now_genuine": not any(lift.character_descent((0,1,0,0,0,0,0), combined)),
        "literal_geometric_D_preserved": True,
        "old_group_or_action_modified_in_place": False,
        "new_category_adopted_as_physical_parent": False,
    }


def element(value):
    value = tuple(value)
    if len(value) != 4 or any(type(q) is not int for q in value) or value[0] not in range(8) or value[3] not in (0, 1):
        raise ValueError("canonical C8 rotation, integral translations and binary epsS required")
    return value


def multiply(left, right):
    a, m, n, e = element(left)
    b, r, s, f = element(right)
    r, s, f = previous.alpha((r, s, f), a)
    return (a+b) % 8, m+r, n+s, (e+f) % 2


def inverse(value):
    a, m, n, e = element(value)
    r, s, f = previous.alpha((-m, -n, e), -a)
    return (-a) % 8, r, s, f


def power(value, n):
    value = element(value)
    if type(n) is not int:
        raise ValueError("integer group power required")
    if n < 0:
        return power(inverse(value), -n)
    result = IDENTITY
    while n:
        if n % 2:
            result = multiply(result, value)
        value, n = multiply(value, value), n//2
    return result


def C_exponent(value):
    _, m, n, e = element(value)
    return (2*(m+n)+4*e) % 8


def Sigma_exponent(value):
    return element(value)[0]


def operator_exponent(value, n):
    if type(n) is not int:
        raise ValueError("integral C power required")
    return (Sigma_exponent(value)+n*C_exponent(value)) % 8


def space_group_certificate(smooth: Mapping, finite: Mapping) -> dict:
    expected = {"A4": [1,1,1,1,1,0], "UVUinvVinv": [0]*6,
                "AUAinvVinv": [0]*6, "AVAinvU": [0,1,0,0,0,1]}
    old = smooth["square_space_group"]["relation_defects_mod_center_bits"]
    if old != expected or finite["selected_representative_alpha_u_v"] != [0,2,2]:
        raise RuntimeError("the actual old full square-group defects changed")
    if finite["selected_relation_C8_exponents"] != {"A4":0,"UVUinvVinv":0,"AUAinvVinv":0,"AVAinvU":4}:
        raise RuntimeError("the actual old external C8 lift changed")
    lifted = {key: (0,)+tuple(value) for key, value in old.items()}
    labels = {key: deck_bits(value) for key, value in lifted.items()}
    if labels != {"A4":(1,0),"UVUinvVinv":(0,0),"AUAinvVinv":(0,0),"AVAinvU":(0,1)}:
        raise RuntimeError("the old smooth defects do not give the proposed pullback")
    mul, inv = multiply, inverse
    relations = {"A4":power(A,4), "UVUinvVinv":mul(mul(mul(U,V),inv(U)),inv(V)),
                 "AUAinvVinv":mul(mul(mul(A,U),inv(A)),inv(V)),
                 "AVAinvU":mul(mul(mul(A,V),inv(A)),U)}
    if relations != {"A4":EPS_T,"UVUinvVinv":IDENTITY,"AUAinvVinv":IDENTITY,"AVAinvU":EPS_S}:
        raise RuntimeError("the explicit combined extension failed")
    words = [A, mul(U,A), mul(U,power(A,2)), mul(V,power(A,2))]
    expected_powers = ["Atilde^4=krot", "(Utilde*Atilde)^4=krot",
                       "(Utilde*Atilde^2)^2=krot*kspin", "(Vtilde*Atilde^2)^2=krot*kspin"]
    if [row["cover_power"] for row in smooth["fixed_strata"]] != expected_powers:
        raise RuntimeError("the actual saved fixed-stratum powers changed")
    strata = []
    for old_row, word, order in zip(smooth["fixed_strata"], words, (4,4,2,2)):
        old_power = power(word, order)
        actual_order = next(n for n in range(1,9) if power(word,n) == IDENTITY)
        inherited_bits = KN if order == 4 else tuple((a+b) % 2 for a,b in zip(KN,KS))
        if old_power != (EPS_T if order == 4 else multiply(EPS_T,EPS_S)):
            raise RuntimeError("the combined fixed-stratum power changed")
        strata.append({"point":old_row["point"],"word":old_row["stabilizer"],
                       "saved_cover_power":old_row["cover_power"],"original_order":order,
                       "actual_lift_order":actual_order,"old_power_in_extension":list(old_power),
                       "old_power_deck_bits":list(deck_bits(inherited_bits)),
                       "C_exponent_mod8":C_exponent(word),"Sigma_exponent_mod8":Sigma_exponent(word),
                       "Sigma_C0_C1_C2_exponents_mod8":[operator_exponent(word,n) for n in range(3)],
                       "normal_N_exponent_mod8":2*Sigma_exponent(word) % 8})
    if [row["actual_lift_order"] for row in strata] != [8,8,4,4]:
        raise RuntimeError("the lifted stabilizer orders changed")
    projectors = []
    for n in range(3):
        value = sp.Rational(sum((-1)**(t+n*s) for t,s in product(range(2),repeat=2)),4)
        if value != 0:
            raise RuntimeError("the naive deck-invariant projector no longer detects Sigma")
        projectors.append({"C_power":n,"deck_character_exponents":[1,n%2],"ordinary_deck_average":str(value)})
    return {
        "bound_old_smooth_relation_defects":copy.deepcopy(old),
        "bound_primitive_C8_alpha_u_v":copy.deepcopy(finite["selected_representative_alpha_u_v"]),
        "bound_defects_in_expanded_center_coordinates":{key:list(value) for key,value in lifted.items()},
        "derived_deck_relation_defects":{key:list(value) for key,value in labels.items()},
        "new_group":"S_combined=(Z^2 x C2_epsS) semidirect C8_A",
        "canonical_element":"(a,m,n,e), a mod8, m,n integral, e mod2; normal form U^m V^n epsS^e A^a",
        "automorphism":"alpha(m,n,e)=(-n,m,e+n mod2), alpha^4=1",
        "presentation":"A^8=1, epsT=A^4, epsT^2=epsS^2=1, epsT and epsS central, [U,V]=1, AUA^-1=V, AVA^-1=epsS*U^-1",
        "relation_values":{key:list(value) for key,value in relations.items()},
        "projection_to_old_space_group":"(a,m,n,e)->(a mod4,m,n)",
        "projection_kernel":[list(IDENTITY),list(EPS_T),list(EPS_S),list(multiply(EPS_T,EPS_S))],
        "kernel_order":4,"kernel_is_C2_times_C2":True,
        "geometric_action_on_square_base_unchanged":True,
        "central_kernel_acts_trivially_on_geometric_base":True,
        "pullback_extension_splits":False,
        "nonsplitting_proof":"Every lift A*epsT^t*epsS^s of the original quarter rotation has fourth power epsT!=1. Hence even its C4 rotation subgroup has no section; the independent epsS defect also retains V99's root-character obstruction.",
        "all_four_rotation_lifts_fourth_powers":[list(power(multiply(A,multiply(power(EPS_T,t),power(EPS_S,s))),4)) for t,s in product(range(2),repeat=2)],
        "genuine_characters":{
            "C":"C(a,m,n,e)=zeta^(2m+2n+4e), so C(A)=1, C(U)=C(V)=i, C(epsT)=1, C(epsS)=-1",
            "Sigma_normal_factor":"Sigma_c(a,m,n,e)=zeta^a for the chosen lift with trivial tangent rotation; Sigma(A)=zeta, Sigma(U)=Sigma(V)=1, Sigma(epsT)=-1, Sigma(epsS)=1",
            "Sigma_scope":"This scalar is the normal Spin2 factor of the Spin-c spinor along the specified normal rotation, not a one-dimensional representation of the full tangent spin group.",
            "N":"N=Sigma_normal_factor^2, N(A)=i, N(U)=N(V)=1; no square-root line M is made genuine on the full combined group",
            "zeta":"exp(i*pi/4)",
        },
        "fixed_strata":strata,
        "old_fields":"Actual old representations are trivial on epsT and epsS, so their pulled-back space-group action factors through the original group. This preserves their old matrices and ordinary invariant subspaces, without creating any missing field representation.",
        "bare_operator_ordinary_deck_projectors":projectors,
        "naive_ineffective_orbifold_projection_warning":"If one simply gauges the deck kernel as an ordinary ineffective action and demands invariant operator fibers/untwisted sections on the same geometric base, the displayed averages vanish. A fermionic extension, spin-frame interpretation or additional sectors requires its own construction; no general prohibition of charged fields or spin structures is inferred from this elementary projector.",
        "orbifold_Dirac_domain_or_twisted_sectors_constructed":False,
        "new_stabilizer_orders_are_old_projector_denominators":False,
        "space_group_lift_installed_in_frozen_theory":False,
    }


def spinc_index(z):
    return sp.expand((z+x/2)**3/6-(z+x/2)*p/24)


def response_certificate() -> dict:
    ch = [sp.expand(sum(level*(n*c)**j/sp.factorial(j) for n,level in ((2,1),(1,-2),(0,1)))) for j in range(4)]
    eta_density = sp.expand(spinc_index(2*c)-2*spinc_index(c)+spinc_index(0))
    response = sp.expand(eta_density+c**3)
    if ch != [0,0,c*c,c**3] or eta_density != c**3+x*c*c/2 or response != 2*c**3+x*c*c/2:
        raise RuntimeError("the genuine changed-category response identity failed")
    h,j = sp.symbols("h j")
    substitution = {x:h,c:h+j,p:3*h*h}
    periods = [sp.expand(spinc_index(n*c).subs(substitution)).coeff(h,2).coeff(j,1) for n in range(3)]
    cup = sp.expand((h+j)**3).coeff(h,2).coeff(j,1)
    if periods != [0,1,6] or cup != 3:
        raise RuntimeError("the nonspin covered period test changed")
    return {
        "category":"Closed Riemannian Spin-c five-manifolds Y with specified normal determinant N and connection, a genuine gauge line C with connection, and the other pulled-back internal bundles. Use the stable continuous combined cover, not an unconstructed orbifold Dirac domain.",
        "associated_Dirac_operators":"D_{Y,N} twisted by C^2, C and 1; all three Sigma_c*C^n representations descend through <D_geom> and are trivial under the spectator internal factors",
        "eta_definition":"xi=(eta+dim kernel)/2, with the full complex Dirac kernel retained",
        "virtual_bundle":"C^2 - 2*C + 1",
        "rank_ch1_ch2_ch3":[str(value) for value in ch],
        "eta_integer_levels":{"C^2":1,"C":-2,"1":1},
        "additional_integral_differential_cup":"c_hat^3, c_hat=c1_hat(C)",
        "positive_response":"Z_Q(Y)=exp(2*pi*i*(xi_c(C^2)-2*xi_c(C)+xi_c(1)+hol_Y(c_hat^3)))",
        "explicit_inverse_response":"Z_Q_inverse(Y)=exp(-2*pi*i*(xi_c(C^2)-2*xi_c(C)+xi_c(1)+hol_Y(c_hat^3)))",
        "eta_index_density":str(eta_density),"positive_response_curvature":str(response),
        "inverse_response_curvature":str(-response),
        "frozen_target_dictionary":"d=c1(D_gauge)=2c, u=x/2, so P/4=d^2*(d+u)/4=2c^3+x*c^2/2",
        "quantization_proof":"On every closed covered Spin-c six-manifold, integral(Q)=index_c(C^2)-2*index_c(C)+index_c(1)+integral(c^3) is an integer. Integer eta levels and differential-character holonomy define the closed5 phase directly, including nonbounding manifolds. On a bounding background APS gives the same phase as exp(2*pi*i*integral Q), independently of the chosen filling.",
        "genuine_quantized_closed5_inverse_defined":True,
        "definition_requires_a_six_manifold_filling":False,
        "local_curvature_alone_used_to_infer_global_phase":False,
        "cover_data_can_be_forgotten":False,
        "CP2_times_CP1_test":{
            "data":"integral h^2*j=1, h^3=j^2=0; x=h, c=h+j, p1=3h^2",
            "Spin_c_indices_C0_C1_C2":[str(value) for value in periods],
            "integral_c_cubed":str(cup),"integral_Q":str(periods[2]-2*periods[1]+periods[0]+cup),
            "normal_determinant_has_no_square_root":True,
        },
        "shared_background_stack":{
            "integer_response_powers":[1,1,-2],"curvatures":[str(response),str(response),str(-2*response)],
            "exact_closed5_phase_product":"Z_Q(Y)*Z_Q(Y)*Z_Q(Y)^(-2)=1",
            "valid_for_all_same_covered_backgrounds_including_torsion":True,
            "is_a_recomputed_bulk_equivariant_localization_profile":False,
            "proves_cancellation_for_independent_endpoint_data":False,
        },
        "eta_factor_boundary_information":"For a smooth5 manifold with boundary, each Dai-Freed eta factor is valued in the inverse determinant line of the boundary Dirac operator. The eta product lies in L(C^2)^(-1) tensor L(C)^2 tensor L(1)^(-1). It is not a canonical scalar boundary trivialization; the cup term additionally requires its differential-cohomology boundary transgression.",
        "full_boundary_transgression_trivialization_or_corner_gluing_supplied":False,
        "inverse_of_the_known_full_physical_anomaly_identified":False,
        "response_is_a_microscopic_positive_spectrum_or_SUSY_action":False,
        "old_bulk_R_flavor_or_normal_anomaly_terms_removed":False,
        "old_finite_defect_CS_ABK_response_glued_here":False,
        "old_normal_half_period_or_M_line_obstruction_repaired":False,
    }


def product_deck_tests() -> dict:
    kernels = [0,1,3]
    rows = []
    for initial in (sp.Integer(0),sp.Rational(1,2)):
        base = [previous.product_xi(h,0,initial) for h in kernels]
        base_eta = base[2]-2*base[1]+base[0]
        for t,s in product(range(2),repeat=2):
            values = [previous.product_xi(h,0,initial+sp.Rational(t+n*s,2)) for n,h in enumerate(kernels)]
            eta = values[2]-2*values[1]+values[0]
            cup_change = sp.Rational(3*s,2)
            relative = (eta-base_eta+cup_change) % 1
            if relative != sp.Rational((t+s)%2,2):
                raise RuntimeError("the two deck-character product tests changed")
            rows.append({"initial_circle_spin":"periodic" if initial==0 else "antiperiodic",
                         "deck_twist_epsT_epsS":[t,s],"xi_C0_C1_C2":[str(value) for value in values],
                         "eta_combination":str(eta),"cup_change":str(cup_change),
                         "response_change_mod1":str(relative),"relative_phase":"-1" if relative else "+1"})
    return {
        "manifold_and_data":"Y=CP2 x S1, N=O(1), C=O(1) from CP2. The three CP2 Spin-c Dirac kernels have positive dimensions0,1,3 and no negative kernels, as freshly bound from V99.",
        "continuous_not_pure_finite_background":True,
        "deck_twists":"epsT changes the Spin-c lift around S1, with the correlated Spin11/R/H3/H267 central lifts KT; epsS changes C by the flat order2 line with the correlated Spin11 central lift KS. Their products project to the same known continuous quotient connection, but are distinct combined-cover structures.",
        "spectral_derivation":"For these periodic or antiperiodic products all nonzero Dirac modes pair with opposite eigenvalues, so eta=0 and xi=h/2 precisely when the total circle shift is integral. No reduced-residue or real-Pfaffian halving is used.",
        "flat_cup_derivation":"The order2 gauge-root twist ell_hat is pulled back from S1, so ell_hat^2=0 and the cup change is3*ell_hat*c_hat^2=3*s/2 mod1.",
        "eight_exact_tests":rows,
        "relative_character_on_this_product_family":"(-1)^(t+s)",
        "each_independent_cover_choice_is_visible_to_this_response":True,
        "diagonal_twist_passes_this_test_only":True,
        "response_descends_through_diagonal_deck_subgroup_proved":False,
        "degree4_minimal_for_every_possible_response_proved":False,
        "full_physical_Gammahat_background_category_or_bordism_classification_identified":False,
    }


@lru_cache(maxsize=1)
def pure_algebra_json():
    return json.dumps({"minimal_combined_operator_cover":cover_certificate(),
                       "quantized_smooth_inverse_response":response_certificate(),
                       "exact_joint_deck_product_tests":product_deck_tests()},sort_keys=True,separators=(",",":"))


def build_certificate() -> dict:
    inputs = load_inputs()
    previous_response = inputs["v99_route"]["determinant_root_descent"]["bound_V98_quantized_chosen_root_response"]
    algebra = json.loads(pure_algebra_json())
    if sp.expand(sp.sympify(previous_response["polynomial"])-sp.sympify(algebra["quantized_smooth_inverse_response"]["positive_response_curvature"])) != 0:
        raise RuntimeError("the changed cover lost the exact frozen response polynomial")
    result = {
        "schema":SCHEMA,
        "status":"EXPLICIT_DEGREE4_OPERATOR_COVER_AND_QUANTIZED_SMOOTH_INVERSE__ORBIFOLD_RELATIVE_REALIZATION_OPEN",
        "input_core_hashes":{**{key:value[1] for key,value in PARENTS.items()},"v99_determinant_root":PREVIOUS_CORE,
                             "v88_smooth_lift":lift.V88_CORE,"v89_C8_lift":lift.V89_CORE},
        **algebra,
        "pulled_back_square_space_group":space_group_certificate(inputs["old_smooth_lift"],inputs["old_finite_lift"]),
        "remaining_obligations":{
            "changed_category_adopted_by_user_or_frozen_parent":False,
            "full_equivariant_Dirac_domain_projectors_and_twisted_sectors":False,
            "same_action_bulk_wall_defect_gluing_and_corner_trivializations":False,
            "new_positive_multiplicity_SUSY_action_and_bulk_anomaly_balance":False,
            "old_normal_half_period_Witten_and_finite_defect_sectors_completed":False,
            "full_Gammahat_Dai_Freed_WCS_and_regulator_completed":False,
            "same_action_parent_accepted":False,"any_gate_closed":False,
        },
        "primary_sources":[
            {"url":"https://web.math.ucsb.edu/~dai/book.pdf","use":"Sections1.3,2.3 and3.3 give the spin/Spin-c determinant and spinor representation and integral Spin-c Dirac index. The intermediate-cover lattice and actual saved square-group pullback are computed here; the degree4 statement is restricted to the stated individual operators."},
            {"url":"https://arxiv.org/pdf/hep-th/9405012","use":"The opening definition retains xi=(eta+kernel dimension)/2; footnote5 explicitly permits Spin-c and twisted Dirac operators. Proposition2.15 and Theorem2.20 give the inverse determinant-line interpretation and smooth gluing law. These justify the changed-category smooth eta factors, not an orbifold domain, physical anomaly identification or boundary trivialization."},
            {"url":"https://math.mit.edu/juvitop/pastseminars/notes_2019_Fall/cheeger-simons.pdf","use":"Theorem1.11 and Eq1.14 supply integral differential-character multiplication and its flat-factor rule. They define the closed5 c_hat^3 holonomy and the exact3/2 flat-root shift; a relative boundary/corner construction is not inferred from a closed holonomy."},
            {"url":"https://stacks.math.columbia.edu/tag/01XS","use":"Lemma30.8.1 supplies the projective-space line cohomology used for the inherited CP2 Dirac kernel dimensions0,1,3. The new joint deck tests retain these exact kernels, rather than halving eta residues."},
        ],
    }
    result["core_sha256"] = canonical_sha(result)
    return result


def validate_certificate(report: Mapping) -> None:
    if report.get("core_sha256") != canonical_sha(report) or dict(report) != build_certificate():
        raise RuntimeError("F100 combined-cover certificate differs from fresh bound derivation")


if __name__ == "__main__":
    print(json.dumps(build_certificate(),indent=2,sort_keys=True))
