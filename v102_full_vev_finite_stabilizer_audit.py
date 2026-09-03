"""F102: an exact finite stabilizer and a locked flavor parity, with scope.

The stabilizer is exhaustive INSIDE the specified known subgroup <f,k,Rtilde>.
Additional continuous/flavor lockings and missing localized representations can
change the full physical stabilizer. Neither a nonlinear vacuum nor quantum
anomaly cancellation is inferred from this algebraic action calculation.
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

import v101_higgs_background_restriction_audit as previous
import v93_mass_sector_symmetry_descent as mass


ROOT = Path(__file__).resolve().parent
PARENTS = {
    "v101_route": ("SUSY_V101_COVER_LIFT_HIGGS_SECTION_SOLVABILITY_AUDIT.json",
                   "a2c321a1889b312305dca187fda511892a2d0e9b3e9e9b18fbcd0a2b9cba42b6"),
    "v101_master": ("SUSY_V101_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
                    "f9ce5079b759b615190564bd41b6e9783e6244889bb3e7237e63132cb23f5300"),
}
PREVIOUS_CORE = "0bb2dc688f660d85e2d20dc1d1075251209d749a86497bd7b0ff4b67bcbe805b"
SCHEMA = "v102_specified_finite_VEV_stabilizer_and_locked_265_hyper_flavor_parity_v1"
canonical_sha = previous.canonical_sha
MODULI = (2, 2, 2, 4, 4, 4, 4, 4, 8)
COORDINATES = ["T_center", "N_center", "Spin11_center", "R_Cartan_mod4", "H3_Cartan_mod4",
               "H267_rho0_mod4", "H267_rho1_mod4", "H267_rho3_mod4", "k_mod8"]
ZERO = (0,)*9
DGEOM = (1, 1, 0, 0, 0, 0, 0, 0, 0)
KT = (1, 0, 1, 2, 2, 2, 2, 2, 0)
KS = (0, 0, 1, 0, 0, 0, 0, 0, 4)
FERMION = (1, 0, 0, 0, 0, 0, 0, 0, 0)
KGEN = (0, 0, 0, 0, 0, 0, 0, 0, 1)
RTILDE = (0, 0, 0, 1, 3, 0, 1, 3, 0)
P265 = (0, 0, 0, 0, 0, 2, 0, 0, 0)
VEVS = ("Phi_+", "Phi_-", "B0", "X", "Xbar")


def portable_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load_inputs() -> dict:
    reports = {}
    for key, (name, core) in PARENTS.items():
        value = json.loads((ROOT/name).read_text(encoding="utf-8"))
        if value.get("core_sha256") != core or canonical_sha(value) != core:
            raise RuntimeError("F102 requires immutable canonical V101 parents: "+key)
        reports[key] = value
    route, master = reports["v101_route"], reports["v101_master"]
    if master["input_core_hashes"]["v101_route"] != PARENTS["v101_route"][1]:
        raise RuntimeError("V101 route/master edge changed")
    if master["next_required_action"]["id"] != "F102_NONZERO_PIVOT_SECTION_CHARTS_AND_COMMON_ACTION_BACKGROUND_RECONSTRUCTION":
        raise RuntimeError("the F102 obligation changed")
    for report, base in ((route, "susy_v101_cover_lift_higgs_section_solvability_audit"),
                         (master, "susy_v101_multipath_g1_frontier_master_audit")):
        for name, key in ((base+".py", "generator_sha256"), ("test_"+base+".py", "test_sha256")):
            if portable_sha(ROOT/name) != report["artifact_hashes"][key]:
                raise RuntimeError("frozen V101 source/test pin changed: "+name)
    saved = route["Higgs_background_restriction"]
    if saved.get("core_sha256") != PREVIOUS_CORE or canonical_sha(saved) != PREVIOUS_CORE:
        raise RuntimeError("the V101 Higgs background helper changed")
    for name in ("v101_higgs_background_restriction_audit.py", "test_v101_higgs_background_restriction_audit.py"):
        if portable_sha(ROOT/name) != route["artifact_hashes"][name]:
            raise RuntimeError("frozen V101 source/test pin changed: "+name)
    if saved != previous.build_certificate():
        raise RuntimeError("V101 Higgs certificate differs from fresh derivation")
    actual_kernel = route["frozen_space_group_cover_obstruction"]["bound_actual_frozen_data"]["old_kernel_generators"]
    for name, expected in (("D_geom", DGEOM), ("KT", KT), ("KS", KS)):
        t, n, g, r, h3, h267, k = actual_kernel[name]
        expanded = (t, n, g, 2*r, 2*h3, 2*h267, 2*h267, 2*h267, 4*k)
        if expanded != expected:
            raise RuntimeError("the finite torus kernel differs from the actual V101 kernel")
    old = previous.load_inputs()  # Rechecks the V90/V92/V93 source contracts.
    v90_base = "susy_v90_external_c8_quotient_daifreed_rees_equivariance_audit"
    for name, key in ((v90_base+".py", "generator_sha256"), ("test_"+v90_base+".py", "test_sha256")):
        if portable_sha(ROOT/name) != old["v90"]["artifact_hashes"][key]:
            raise RuntimeError("frozen V90 action source/test pin changed: "+name)
    rlift = old["v93_route"]["smooth_R_and_wall_mass_extension"]
    if rlift != mass.build_certificate():
        raise RuntimeError("the actual V93 R-flavor extension differs from fresh matrices")
    reports["v90_action"] = old["v90"]["charged_neutral_and_compensator_repair"]
    reports["v92_projectors"] = old["v92_route"]["smooth_singlet_projectors"]
    reports["v93_R_lift"] = rlift
    reports["old_core_hashes"] = {"v90": old["v90"]["core_sha256"],
                                 "v92_projectors": old["v92_route"]["smooth_singlet_projectors"]["core_sha256"],
                                 "v93_R_lift": rlift["core_sha256"]}
    return reports


def torus_element(value):
    value = tuple(value)
    if len(value) != 9 or any(type(a) is not int or a not in range(n) for a, n in zip(value, MODULI)):
        raise ValueError("canonical finite torus coordinates are required")
    return value


def torus_add(left, right):
    return tuple((a+b) % n for a, b, n in zip(torus_element(left), torus_element(right), MODULI))


def torus_scale(value, power):
    value = torus_element(value)
    if type(power) is not int:
        raise ValueError("integer torus power required")
    return tuple(power*a % n for a, n in zip(value, MODULI))


def old_kernel():
    return sorted({torus_add(torus_add(torus_scale(DGEOM, d), torus_scale(KT, t)), torus_scale(KS, s))
                   for d, t, s in product(range(2), repeat=3)})


def quotient(value):
    return min(torus_add(value, k) for k in old_kernel())


def generator_element(value):
    value = tuple(value)
    if len(value) != 3 or any(type(a) is not int or a not in range(n) for a, n in zip(value, (2, 8, 4))):
        raise ValueError("canonical (fermion bit,k exponent,R exponent) required")
    return value


def lift_element(value):
    f, k, r = generator_element(value)
    return torus_add(torus_add(torus_scale(FERMION, f), torus_scale(KGEN, k)), torus_scale(RTILDE, r))


def theta_exponent(value):
    f, _, r = generator_element(value)
    return (4*f+2*r) % 8


def component_exponent(value, charge, scalar_R, fermion=False):
    f, k, r = generator_element(value)
    if type(charge) is not int or type(scalar_R) is not int or scalar_R not in range(4) or type(fermion) is not bool:
        raise ValueError("integer charge, canonical scalar R and Boolean component type required")
    return (charge*k+2*r*(scalar_R-int(fermion))+4*f*int(fermion)) % 8


def subgroup_certificate() -> dict:
    all_elements = list(product(range(2), range(8), range(4)))
    images = [quotient(lift_element(value)) for value in all_elements]
    if len(set(images)) != 64 or len(old_kernel()) != 8:
        raise RuntimeError("the specified finite subgroup does not embed in the unchanged quotient")
    if quotient(torus_scale(KGEN, 4)) != quotient((0, 0, 1, 0, 0, 0, 0, 0, 0)):
        raise RuntimeError("k^4 is not the retained Spin11 central element")
    locked = lift_element((1, 4, 2))
    if torus_add(locked, P265) != torus_add(KT, KS) or quotient(locked) != quotient(P265):
        raise RuntimeError("the exact locked flavor parity identity failed")
    return {
        "finite_coordinate_order": COORDINATES, "coordinate_moduli": list(MODULI),
        "coordinate_scope": "The R and H3 entries are their fixed common symplectic Cartans. The three H267 entries distinguish the actual rho0,rho1,rho3 blocks of dimensions265,1,1; this is not a new independent full nonabelian flavor product after gauging.",
        "unchanged_kernel_generators": {"D_geom": list(DGEOM), "KT": list(KT), "KS": list(KS)},
        "unchanged_kernel": [list(k) for k in old_kernel()],
        "generators": {"f_tangent_2pi": list(FERMION), "k": list(KGEN), "Rtilde": list(RTILDE)},
        "specified_subgroup": "H=<f,k,Rtilde> is C2_f x C8_k x C4_Rtilde inside the known quotient",
        "order": 64, "all_generator_lift_cosets": [list(row) for row in images],
        "all_64_cosets_distinct": True,
        "Rtilde_not_a_pure_R_rotation": "Its H3 Cartan is diag(-i I3,+i I3); H267 has rho3 on Phi_plus, rho1 on Phi_minus and rho0 on the other265 hypers.",
        "k_fourth_equals_Spin11_center": True,
        "surviving_g_is_independent_external_disconnected_component": False,
        "literal_geometric_D_preserved": True,
        "P265_coordinates": list(P265),
        "exact_quotient_identity": "P265=Rtilde^2 * k^4 * f",
        "identity_difference_in_old_kernel": list(torus_add(KT, KS)),
        "P265_is_old_universal_fermion_parity": False,
        "epsilonT_relabelled_as_fermion_parity": False,
        "full_global_or_localized_quantum_symmetry_proved": False,
    }


def action_certificate(action: Mapping, rlift: Mapping) -> dict:
    registry = copy.deepcopy(action["operator_charge_registry"])
    if any((registry[name]["U1_8"], registry[name]["Z4R"]) != pair
           for name, pair in zip(VEVS, ((8, 0), (-8, 0), (4, 0), (6, 0), (-6, 0)))):
        raise RuntimeError("the five actual proposed VEV charges changed")
    for q in (2, 4, 6):
        registry["extra_S"+str(q)] = {"U1_8": q, "U1_X": 0, "Z4R": 1}
    if not rlift["singlet_R_extension"]["all_nine_extras_scalar_R1_fermion_R0"]:
        raise RuntimeError("the extra zero-mode R assignment changed")
    operators = action["corrected_compensator"]["operator_ledger"]
    # Obtain the exact source ledger shape, not a newly chosen superpotential.
    written = [row for row in operators if row["selection_rule_allowed"]]
    if len(written) != 13:
        raise RuntimeError("the number of written V90 W and Kahler monomials changed")
    extra = [{"operator": "linear "+name+" times fixed nonzero driver constant", "factors": [name], "operator_kind": "superpotential"}
             for name in ("S8", "SB", "SX")]
    extra += [{"operator": "Phi_minus S2_i S6_i", "factors": ["Phi_-", "extra_S2", "extra_S6"], "operator_kind": "superpotential"},
              {"operator": "Phi_minus S4_i squared", "factors": ["Phi_-", "extra_S4", "extra_S4"], "operator_kind": "superpotential"}]
    all_group = list(product(range(2), range(8), range(4)))
    checked = []
    for row in written+extra:
        residuals = []
        for value in all_group:
            phase = sum(component_exponent(value, registry[name]["U1_8"], registry[name]["Z4R"])
                        for name in row["factors"])
            measure = -2*theta_exponent(value) if row["operator_kind"] == "superpotential" else 0
            residuals.append((phase+measure) % 8)
        if any(residuals):
            raise RuntimeError("a written constant tensor fails the specified finite symmetry")
        checked.append({"operator": row["operator"], "factors": list(row["factors"]),
                        "operator_kind": row["operator_kind"], "all_64_action_residuals_mod8": residuals})
    strata = []
    for value in all_group:
        phases = [component_exponent(value, registry[name]["U1_8"], registry[name]["Z4R"]) for name in VEVS]
        strata.append({"f_k_R": list(value), "VEV_phase_exponents_mod8": phases, "fixes_all_VEVs": not any(phases)})
    preserved = [row["f_k_R"] for row in strata if row["fixes_all_VEVs"]]
    if len(preserved) != 16 or any(row[1] not in (0, 4) for row in preserved):
        raise RuntimeError("the full five-VEV stabilizer in H changed")
    forbidden = []
    for row in operators:
        if not row["selection_rule_allowed"]:
            phase = sum(component_exponent((0, 0, 1), registry[name]["U1_8"], registry[name]["Z4R"])
                        for name in row["factors"])-2*theta_exponent((0, 0, 1))
            forbidden.append({"operator": row["operator"], "Rtilde_action_residual_mod8": phase % 8})
    if len(forbidden) != 4 or any(row["Rtilde_action_residual_mod8"] != 4 for row in forbidden):
        raise RuntimeError("the frozen forbidden operator selector changed")
    return {
        "bound_V90_operator_registry": copy.deepcopy(action["operator_charge_registry"]),
        "component_rule": "scalar phase=zeta^(q*k+2*r*Rscalar); Weyl phase=zeta^(q*k+2*r*(Rscalar-1)+4*f); theta phase=zeta^(2*r+4*f)",
        "written_action_checks": checked,
        "source_V90_allowed_operator_count": len(written),
        "driver_constants_are_fixed_neutral_numbers": True,
        "V93_mass_channels_copies": 3,
        "VEV_order": list(VEVS), "all_64_VEV_tests": strata,
        "exact_stabilizer_in_specified_H": "H_VEV=<f,g=k^4,Rtilde> = C2_f x C2_g x C4_Rtilde",
        "stabilizer_order": 16, "all_stabilizer_elements_f_k_R": preserved,
        "bosonic_quotient_by_f_order": 8,
        "exhaustiveness_scope": "Every element of the specified H, with its actual R/flavor locking, has been tested. No unknown flavor rotation is assumed absent from the full stabilizer; this is not an exhaustive classification of the physical gauge/flavor group.",
        "Rtilde_preserved_by_all_five_proposed_VEVs": True,
        "four_forbidden_V90_operators_remain_R_forbidden": forbidden,
        "full_nonlinear_VEV_or_localized_representation_constructed": False,
    }


def block_parity_certificate(projectors: Mapping, rlift: Mapping) -> dict:
    source = projectors["eleven_mode_normal_aligned_witness"]["direct_sum_blocks"]
    rrows = rlift["singlet_R_extension"]["compressed_direct_sum_blocks"]
    if len(source) != len(rrows) or rlift["singlet_R_extension"]["complex_half_flavor_phase_multiplicities_rho0123"] != [265, 1, 0, 1]:
        raise RuntimeError("the actual H267 flavor support changed")
    records, odd_hypers, odd_zero_modes, even_zero_modes = [], 0, 0, 0
    for item, ritem in zip(source, rrows):
        block, rc = item["certificate"], ritem["certificate"]
        copies, n = item["copies"], block["hyper_count"]
        if copies != ritem["copies"] or (block["kind"], block["q_magnitude"], block["m"]) != (rc["kind"], rc["q_magnitude"], rc["m"]):
            raise RuntimeError("R and orbifold block alignment changed")
        rho = rc["flavor_rho_mod4"]
        RF = mass.matrix(rc["R_flavor"])
        P = mass.clean(-RF**2)
        sign = -1 if rho == 0 else 1
        if P != sign*sp.eye(2*n):
            raise RuntimeError("the locked parity has the wrong block sign")
        J = mass.projectors.symplectic_form(n)
        charge = sp.diag(*block["continuous_symplectic_charge_diagonal"])
        twists = {key: mass.matrix(row) for key, row in block["underlying_flavor"].items()
                  if key in ("A", "U", "V", "external_k")}
        checks = {"order_divides_two": P**2 == sp.eye(2*n),
                  "unitary": P.conjugate().T*P == sp.eye(2*n),
                  "symplectic": P.T*J*P == J,
                  "quaternionic_reality": J*sp.conjugate(P) == P*J,
                  "commutes_with_gauged_charge": P*charge == charge*P}
        checks.update({"commutes_"+key: P*value == value*P for key, value in twists.items()})
        for point, row in block["strata"].items():
            for side in ("plus", "minus"):
                projector = mass.matrix(row[side+"_projector"])
                half = sign*sp.eye(n)
                checks["commutes_"+point+"_"+side+"_projector"] = half*projector == projector*half
        if not all(checks.values()):
            raise RuntimeError("the locked parity fails a frozen reality or projector condition")
        modes = copies*(block["constant_modes"]["plus"]+block["constant_modes"]["minus"])
        if sign == -1:
            odd_hypers += copies*n
            odd_zero_modes += modes
        else:
            even_zero_modes += modes
        records.append({"kind": block["kind"], "q_magnitude": block["q_magnitude"], "m": block["m"],
                        "copies": copies, "hypers_per_copy": n, "flavor_rho_mod4": rho,
                        "P265_sign": sign, "P265_matrix": mass.matrix_json(P),
                        "constant_mode_count": modes, "checks": checks})
    if (odd_hypers, odd_zero_modes, even_zero_modes) != (265, 9, 2):
        raise RuntimeError("the parity census no longer matches the frozen projectors")
    H3 = mass.matrix(rlift["old_smooth_bulk_R_extension"]["flavor_D_H3"])
    if H3 != sp.diag(-sp.I, -sp.I, -sp.I, sp.I, sp.I, sp.I) or H3**2 != -sp.eye(6):
        raise RuntimeError("the actual H3 R-flavor square changed")
    return {
        "actual_H3_R_flavor_square": "-I6", "bound_H3_R_flavor_matrix": mass.matrix_json(H3),
        "actual_H267_R_flavor_rho0123_census": [265, 1, 0, 1],
        "block_identity": "P265=-D_H267^2; multiplying Rtilde^2*k^4*f by KT+KS gives exactly this H267 element",
        "compressed_blocks": records,
        "odd_full_hypers": odd_hypers, "odd_selected_N1_zero_modes": odd_zero_modes,
        "even_selected_Phi_zero_modes": even_zero_modes,
        "P265_on_other_old_smooth_sectors": "identity on H3 vector hypers and the gauge sector; the full H267 action is the displayed involution, not merely a sign on nine arbitrarily added fields",
        "preserves_all_saved_orbifold_projectors_and_SMW_pairing": True,
        "is_center_of_entire_unreduced_Sp267": False,
        "is_in_the_saved_matrix_and_gauged_charge_centralizer": True,
        "missing_localized_H267_representations_completed": False,
    }


def character_and_selection_certificate(action: Mapping) -> dict:
    registry = action["operator_charge_registry"]
    visible = {name: row for name, row in registry.items() if name != "B0_dag"}
    if any((row["Z4R"]-row["U1_8"]) % 2 for row in visible.values()):
        raise RuntimeError("the visible-only scalar parity relation changed")
    extras = {"S"+str(q)+"_"+str(i): {"U1_8": q, "Z4R": 1} for q in (2, 4, 6) for i in range(1, 4)}
    subgroup = [(f, k, r) for f, k, r in product(range(2), (0, 4), range(4))]
    def signature(value, fields):
        phases = [theta_exponent(value)]
        phases += [component_exponent(value, row["U1_8"], row["Z4R"], fermion)
                   for row in fields.values() for fermion in (False, True)]
        return tuple(phases)
    old_kernel = [value for value in subgroup if not any(signature(value, visible))]
    full_kernel = [value for value in subgroup if not any(signature(value, {**visible, **extras}))]
    if old_kernel != [(0, 0, 0), (1, 4, 2)] or full_kernel != [(0, 0, 0)]:
        raise RuntimeError("the visible-only parity quotient or its failure on extra fields changed")
    rows = []
    for name, row in {**visible, **extras}.items():
        phases = [component_exponent((1, 4, 2), row["U1_8"], row["Z4R"], f) for f in (False, True)]
        expected = [4, 4] if name in extras else [0, 0]
        if phases != expected:
            raise RuntimeError("the component-level P265 character changed")
        rows.append({"field": name, "q8_continuous": row["U1_8"], "scalar_R4": row["Z4R"],
                     "P265_scalar_and_Weyl_exponents_mod8": phases, "is_extra_selected_mode": name in extras})
    return {
        "field_character_rows": rows,
        "visible_only_action_kernel_f_k_R": [list(value) for value in old_kernel],
        "visible_plus_nine_extras_action_kernel_f_k_R": [list(value) for value in full_kernel],
        "visible_only_faithful_image_order": 8, "with_nine_extras_faithful_image_order": 16,
        "visible_only_relation": "Rtilde^2*g=f on the V90 visible component table, including theta; this is a representation kernel, not an imposed quotient of the known Gammahat group",
        "relation_valid_on_nine_extras": False,
        "full_known_group_relation_instead": "Rtilde^2*g*f=P265, with P265 nontrivial on 265 actual hypers and nine selected zero modes",
        "all_order_selection_rule": "For any monomial in the displayed chiral fields and their conjugates, gauge g invariance forces the number of visible factors with odd q8 to be even. Rtilde invariance of W (R=2) or K (R=0) forces the total scalar R parity even. Their difference is precisely the parity of the number of extra factors, so that number is even. Inserting the five R-neutral, even-charge VEVs cannot change this result.",
        "equivalent_component_rule": "P265 is an internal flavor sign acting equally on a scalar and its Weyl partner. Conservation forbids any P-odd initial state from decaying into only P-even final states.",
        "conditional_lightest_odd_state_stability": "If g and Rtilde, hence P265, remain exact unbroken symmetries of the FULL quantum action including anomalies and nonperturbative effects, the assumed vacuum exists, and no lighter P-odd state outside the displayed sector is present, the lightest P-odd state is stable. These hypotheses have not been established for the full theory.",
        "extra_sector_identity": "The nine V93 S2,S4,S6 singlet zero modes are not the earlier V65 vectorlike orphan quark pair. No conclusion about that separate pair is derived here.",
        "any_odd_extra_decay_to_only_listed_even_visible_fields_preserving_g_and_Rtilde": False,
        "cosmological_viability_mass_or_abundance_computed": False,
        "full_P265_quantum_anomaly_freedom_proved": False,
        "stable_particle_prediction_of_an_accepted_theory": False,
    }


@lru_cache(maxsize=2)
def derived_json(action_json, projectors_json, rlift_json):
    action, projectors, rlift = map(json.loads, (action_json, projectors_json, rlift_json))
    return json.dumps({"known_finite_subgroup": subgroup_certificate(),
                       "written_action_and_full_VEV_stabilizer": action_certificate(action, rlift),
                       "locked_flavor_parity_and_frozen_projectors": block_parity_certificate(projectors, rlift),
                       "component_characters_and_selection_rule": character_and_selection_certificate(action)},
                      sort_keys=True, separators=(",", ":"))


def build_certificate() -> dict:
    inputs = load_inputs()
    result = {
        "schema": SCHEMA,
        "status": "EXACT_SPECIFIED_FINITE_STABILIZER_AND_265_HYPER_PARITY__FULL_RESIDUAL_GROUP_AND_QUANTUM_VACUUM_OPEN",
        "input_core_hashes": {**{key: value[1] for key, value in PARENTS.items()},
                              "v101_Higgs_background": PREVIOUS_CORE, **inputs["old_core_hashes"]},
        **json.loads(derived_json(*(json.dumps(inputs[key], sort_keys=True) for key in ("v90_action", "v92_projectors", "v93_R_lift")))),
        "full_stabilizer_boundary": {
            "exact_stabilizer_only_inside_named_H": True,
            "full_unbroken_continuous_and_finite_group_classified": False,
            "additional_R_flavor_lockings_excluded": False,
            "known_smooth_R_flavor_lift_and_projector_constraints_checked": True,
            "localized_Fi_PA_X_Xbar_S8_SB_SX_mediator_Gammahat_representations_constructed": False,
            "why_gcd_is_not_full_answer": "g=k^4 is locked to the Spin11 center, Rtilde already includes nontrivial H3/H267 rotations, and their product with f is the nontrivial P265 flavor symmetry. Further continuous or discrete stabilizers of the complete fixed coupling tensors require the missing localized representations and global gauged QK action.",
            "relation_to_component_line_network": "The written operator checks retain fixed driver constants, the GM Kahler tensor and the V93 mass terms. They establish the stated finite characters, not an extension of every formal Cartan line solution to a full Gammahat representation.",
            "old_central_kernel_or_frozen_space_group_changed": False,
            "new_finite_symmetry_or_background_adopted": False,
        },
        "remaining_obligations": {
            "nonlinear_same_action_F_D_flat_vacuum_constructed": False,
            "all_localized_representations_and_full_tensor_stabilizer_completed": False,
            "residual_finite_global_anomaly_and_relative_Dai_Freed_gluing_computed": False,
            "defects_R_breaking_soft_sector_and_odd_sector_cosmology_completed": False,
            "same_action_parent_accepted": False, "any_gate_closed": False,
        },
        "primary_sources": [
            {"url": "https://arxiv.org/pdf/hep-ph/9709356", "use": "Martin, A Supersymmetry Primer, Section4.11 gives theta charge1, fermion charge Rscalar-1 and W charge2. Section6.2 explains conservation of an exact multiplicative parity and conditional stability of its lightest odd state. The present P265 is derived from the frozen kernel and flavor matrices, not identified with ordinary MSSM R-parity or claimed anomaly-free."},
            {"url": "https://arxiv.org/pdf/1009.0905", "use": "Lee et al. distinguish a Z4 R symmetry, its action on superspace and forbidden superpotential operators. The actual charge table, surviving g, and additional even-gauge-charge R-odd singlets here are source-bound and rederived; no anomaly-cancellation theorem for this different spectrum is imported."},
            {"url": "https://arxiv.org/pdf/2307.14658v3", "use": "Central-extension pullbacks and kernels distinguish a faithful representation image from an imposed group quotient. All64 finite cosets and the16-element VEV stabilizer are computed explicitly with the unchanged known kernel."},
        ],
    }
    result["core_sha256"] = canonical_sha(result)
    return result


def validate_certificate(report: Mapping) -> None:
    if report.get("core_sha256") != canonical_sha(report) or dict(report) != build_certificate():
        raise RuntimeError("F102 finite-VEV stabilizer certificate differs from fresh bound derivation")


if __name__ == "__main__":
    print(json.dumps(build_certificate(), sort_keys=True, indent=2))
