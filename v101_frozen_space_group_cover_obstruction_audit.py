"""F101: exhaustive central lifts of the actual frozen square-space group.

No proper intermediate cover retaining D_geom admits this fixed representation.
Explicit lifts on changed spatial subgroups are supplied, not adopted as a new
compactification or promoted to a relative anomaly cancellation theorem.
"""
from __future__ import annotations

import copy
from functools import lru_cache
import hashlib
from itertools import product
import json
from pathlib import Path
from typing import Mapping

import v100_modified_equivariant_cover_audit as previous


ROOT = Path(__file__).resolve().parent
PARENTS = {
    "v100_route": ("SUSY_V100_CORRELATED_QUANTIZATION_MODIFIED_ACTION_SECTION_AUDIT.json",
                   "804242337e0681fe39a84891badd9545447b7f980794366da6a45d4f3277018a"),
    "v100_master": ("SUSY_V100_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
                    "5727d33c6678cdf23539387e20b2a3cae2ab92095723adfb2a368c7fd2d75a24"),
}
PREVIOUS_CORE = "0d9a6e0549b988edb636b69cf32c3cea2636e5b9cbf5d5378e62bd67f2209104"
SCHEMA = "v101_frozen_square_group_all_intermediate_central_cover_obstructions_v1"
canonical_sha = previous.canonical_sha
lift = previous.lift
D, KT, KN, KS = previous.D, previous.KT, previous.KN, previous.KS
ZERO, T, S, TS = (0, 0), (1, 0), (0, 1), (1, 1)
E = tuple(product(range(2), repeat=2))
COVERS = (
    ("old_quotient", E),
    ("gauge_C_root", (ZERO, T)),
    ("natural_Sigma", (ZERO, S)),
    ("diagonal", (ZERO, TS)),
    ("combined", (ZERO,)),
)
RELATORS = ("A4", "UVUinvVinv", "AUAinvVinv", "AVAinvU")


def portable_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load_inputs() -> dict:
    reports = {}
    for key, (name, core) in PARENTS.items():
        data = json.loads((ROOT/name).read_text(encoding="utf-8"))
        if data.get("core_sha256") != core or canonical_sha(data) != core:
            raise RuntimeError("F101 requires immutable canonical V100 parents: " + key)
        reports[key] = data
    route, master = reports["v100_route"], reports["v100_master"]
    if master["input_core_hashes"]["v100_route"] != PARENTS["v100_route"][1]:
        raise RuntimeError("V100 master-to-route edge changed")
    if master["next_required_action"]["id"] != "F101_PHYSICAL_BACKGROUND_RESTRICTION_RELATIVE_ACTION_AND_SECTION_SOLVABILITY":
        raise RuntimeError("the F101 obligation changed")
    saved = route["modified_equivariant_cover"]
    if saved.get("core_sha256") != PREVIOUS_CORE or canonical_sha(saved) != PREVIOUS_CORE:
        raise RuntimeError("the frozen V100 combined-cover helper changed")
    for name in ("v100_modified_equivariant_cover_audit.py", "test_v100_modified_equivariant_cover_audit.py"):
        if portable_sha(ROOT/name) != route["artifact_hashes"][name]:
            raise RuntimeError("frozen V100 source/test pin changed: " + name)
    if saved != previous.build_certificate():
        raise RuntimeError("V100 combined-cover certificate differs from fresh derivation")
    # V100's fresh reconstruction rechecks all the older source/test edges.
    name, core = previous.previous.PARENTS["v98_route"]
    older = json.loads((ROOT/name).read_text(encoding="utf-8"))
    if older.get("core_sha256") != core or canonical_sha(older) != core:
        raise RuntimeError("the actual saved V98 hypermultiplet characters changed")
    reports["old_components"] = older["gammahat_compensator"]["unchanged_geometric_kernel_obstruction"]
    return reports


def bits2(value):
    value = tuple(value)
    if len(value) != 2 or any(type(q) is not int or q not in (0, 1) for q in value):
        raise ValueError("two strict binary central coordinates required")
    return value


def add(left, right):
    return tuple((a+b) % 2 for a, b in zip(bits2(left), bits2(right)))


def subgroup(value):
    value = tuple(sorted(set(bits2(row) for row in value)))
    if ZERO not in value or any(add(a, b) not in value for a, b in product(value, repeat=2)):
        raise ValueError("a subgroup of the binary deck group is required")
    return value


def quotient(value, retained):
    value, retained = bits2(value), subgroup(retained)
    return min(add(value, h) for h in retained)


def deck_element(value):
    t, s = bits2(value)
    return 4*t, 0, 0, s


def central_label(value):
    a, m, n, e = previous.element(value)
    if m or n or a not in (0, 4):
        raise ValueError("this group element is not central deck data")
    return a//4, e


def shifted_relators(a, u, v):
    bits2(a)
    uv = add(u, v)
    return dict(zip(RELATORS, (T, ZERO, uv, add(S, uv))))


def actual_shifted_relators(a, u, v):
    mul, inv = previous.multiply, previous.inverse
    aa, uu, vv = (mul(g, deck_element(z)) for g, z in zip((previous.A, previous.U, previous.V), (a, u, v)))
    rows = (previous.power(aa, 4), mul(mul(mul(uu, vv), inv(uu)), inv(vv)),
            mul(mul(mul(aa, uu), inv(aa)), inv(vv)), mul(mul(mul(aa, vv), inv(aa)), uu))
    return {key: central_label(row) for key, row in zip(RELATORS, rows)}


def exhaustive_cover_rows() -> list:
    generated = {tuple(lift.span((D,)+tuple(k for k, keep in zip(lift.old_kernel(), mask) if keep)))
                 for mask in product(range(2), repeat=8)}
    rows = []
    for name, retained in COVERS:
        retained = subgroup(retained)
        kernel = [k for k in lift.old_kernel() if previous.deck_bits(k) in retained]
        cosets = sorted({quotient(e, retained) for e in E})
        choices = []
        for a, u, v in product(cosets, repeat=3):
            formula = shifted_relators(a, u, v)
            if formula != actual_shifted_relators(a, u, v):
                raise RuntimeError("the all-lift symbolic formula differs from exact group multiplication")
            reduced = {key: quotient(z, retained) for key, z in formula.items()}
            choices.append({"central_changes_A_U_V": [list(a), list(u), list(v)],
                            "relator_classes": {key: list(z) for key, z in reduced.items()},
                            "all_relations_close": all(z == ZERO for z in reduced.values())})
        valid = sum(row["all_relations_close"] for row in choices)
        if valid != int(name == "old_quotient"):
            raise RuntimeError("unexpected lift of the frozen square-group representation")
        rows.append({"name": name, "retained_deck_subgroup_H": [list(h) for h in retained],
                     "kernel_Kprime": [list(k) for k in kernel], "cover_degree": len(cosets),
                     "number_of_central_generator_choices": len(choices), "number_of_lifts": valid,
                     "C_descends": not any(lift.character_descent(previous.CCHAR, kernel)),
                     "Sigma_c_descends": not any(lift.character_descent(previous.SIGMA, kernel)),
                     "frozen_representation_lifts": bool(valid), "all_choices": choices})
    if {tuple(map(tuple, row["kernel_Kprime"])) for row in rows} != generated or len(generated) != 5:
        raise RuntimeError("the enumeration did not exhaust all intermediate covers retaining D_geom")
    return rows


def fixed_stratum_rows() -> list:
    mul, power = previous.multiply, previous.power
    words = (previous.A, mul(previous.U, previous.A), mul(previous.U, power(previous.A, 2)),
             mul(previous.V, power(previous.A, 2)))
    rows = []
    for name, retained in COVERS:
        strata = []
        cosets = sorted({quotient(e, retained) for e in E})
        for point, word, order in zip(("z00", "z11", "z10", "z01"), words, (4, 4, 2, 2)):
            classes, orders = [], []
            for change in cosets:
                changed = mul(word, deck_element(change))
                obstruction = quotient(central_label(power(changed, order)), retained)
                classes.append(list(obstruction))
                orders.append(order if obstruction == ZERO else 2*order)
                if quotient(central_label(power(changed, orders[-1])), retained) != ZERO:
                    raise RuntimeError("incorrect quotient stabilizer order")
            if len(set(orders)) != 1 or len({tuple(z) for z in classes}) != 1:
                raise RuntimeError("even-order cyclic lift obstruction changed under a central twist")
            strata.append({"point": point, "original_order": order, "lift_order": orders[0],
                           "all_central_changes": [list(z) for z in cosets],
                           "old_order_power_classes": classes, "cyclic_representation_lifts": orders[0] == order})
        rows.append({"cover": name, "strata": strata,
                     "all_four_cyclic_restrictions_lift": all(row["cyclic_representation_lifts"] for row in strata)})
    expected = [[4, 4, 2, 2], [4, 4, 4, 4], [8, 8, 4, 4], [8, 8, 2, 2], [8, 8, 4, 4]]
    if [[s["lift_order"] for s in row["strata"]] for row in rows] != expected:
        raise RuntimeError("the five-cover fixed-stratum order table changed")
    return rows


def old_element(value):
    value = tuple(value)
    if len(value) != 3 or any(type(q) is not int for q in value) or value[0] not in range(4):
        raise ValueError("old square-group normal form (a mod4,m,n) required")
    return value


def old_multiply(left, right):
    a, m, n = old_element(left)
    b, r, s = old_element(right)
    r, s, _ = previous.previous.alpha((r, s, 0), a)
    return (a+b) % 4, m+r, n+s


def checkerboard_section(value):
    a, m, n = old_element(value)
    if (m+n) % 2:
        raise ValueError("checkerboard translations require m+n even")
    return a, m, n, ((m+n)//2) % 2


def root_quotient(value):
    a, m, n, e = previous.element(value)
    return a % 4, m, n, e


def translation_section(value):
    a, m, n = old_element(value)
    if a:
        raise ValueError("the combined-cover translation section excludes nonidentity rotations")
    return 0, m, n, 0


def changed_domain_certificate() -> dict:
    mul, inv = previous.multiply, previous.inverse
    b, c = checkerboard_section((0, 1, 1)), checkerboard_section((0, 1, -1))
    rotation = checkerboard_section((1, 0, 0))
    if root_quotient(mul(mul(rotation, b), inv(rotation))) != root_quotient(inv(c)):
        raise RuntimeError("checkerboard B rotation relation failed")
    if root_quotient(mul(mul(rotation, c), inv(rotation))) != b:
        raise RuntimeError("checkerboard C rotation relation failed")
    if previous.C_exponent(b) or previous.C_exponent(c) or previous.C_exponent(rotation):
        raise RuntimeError("the changed-domain C character was not trivial")
    rotation_powers = [{"rotation_exponent_a_mod4": a, "old_order": 4 if a % 2 else 2,
                        "epsT_coordinate_of_lift_power": (a*(4 if a % 2 else 2) % 8)//4}
                       for a in (1, 2, 3)]
    if any(row["epsT_coordinate_of_lift_power"] != 1 for row in rotation_powers):
        raise RuntimeError("a nonidentity rotation lost the combined epsilonT obstruction")
    return {
        "checkerboard_gauge_root_lift": {
            "old_subgroup": "S_check={(a,m,n):m+n even}=Lambda_check semidirect C4_A",
            "translation_generators": [[1, 1], [1, -1]], "index_in_frozen_S": 2,
            "lift_section_into_Scombined_mod_epsT": "s(a,m,n)=(a,m,n,(m+n)/2 mod2)",
            "exact_equivariance_identity": "e(-n,m)=e(m,n)+n mod2; e=(m+n)/2 is additive on Lambda_check",
            "lifted_B_and_C": [list(b), list(c)],
            "lifted_rotation_relations": "A B A^-1=C^-1, A C A^-1=B, [B,C]=1, A^4=1 in the gauge-root cover",
            "C_exponent_on_entire_subgroup": 0,
            "C_triviality_proof": "m+n=2q gives 2(m+n)+4e=4q+4q=0 mod8",
            "smallest_index_spatial_subgroup_lifting_to_gauge_root_cover": 2,
            "minimality_scope": "Among finite-index subgroups of this fixed S. Index1 is the excluded full S and the displayed index2 subgroup splits. No uniqueness or all-redesign minimality is claimed.",
            "homomorphism_and_projection_section_proved": True,
            "is_lift_on_unchanged_frozen_S": False,
        },
        "translation_combined_lift": {
            "old_subgroup": "Z^2 generated by the original commuting U,V",
            "index_in_frozen_S": 4, "lift_section": "s(0,m,n)=(0,m,n,0)",
            "homomorphism_and_projection_section_proved": True,
            "rotation_power_epsT_witnesses": rotation_powers,
            "minimum_index_of_any_finite_index_subgroup_that_lifts_to_combined_cover": 4,
            "minimality_proof": "In S=Z^2 semidirect C4, every element with nonzero rotation has finite order r=4 or2 because 1+R+...+R^(r-1)=0. Any combined lift has a*r=4 mod8, regardless of its translations or central changes. Its order-r power has epsilonT coordinate1. A splitting subgroup therefore lies in Z^2, so has index at least4; the displayed Z^2 section attains4.",
            "C_on_U_and_V_exponents_mod8": [2, 2],
            "Sigma_on_U_and_V_exponents_mod8": [0, 0],
            "retains_old_rotational_fixed_strata": False,
        },
        "domain_change_cost": "These are restrictions to different spatial/orbifold groups, not repairs of the frozen representation. The index2 subgroup changes translation identifications and fixed-stratum data; the index4 translation subgroup removes all rotations and rotational fixed strata. Neither construction preserves the old chiral projection by declaration. New spectra, projectors, geometry, supersymmetry and anomalies require recomputation.",
        "changed_compactification_or_subgroup_adopted": False,
        "new_projectors_twisted_sectors_or_spectrum_computed": False,
        "ordinary_unramified_manifold_cover_asserted": False,
        "full_relative_inflow_obtained_from_subgroup_lift": False,
    }


def fermion_parity_certificate(old_components: Mapping) -> dict:
    fermion = tuple(old_components["baseline_fermion_center_bits"])
    scalar = tuple(old_components["baseline_scalar_center_bits"])
    if fermion != (1, 1, 0, 0, 0, 1, 0) or scalar != (0, 0, 0, 1, 0, 1, 0):
        raise RuntimeError("actual old hypermultiplet center characters changed")
    lorentz = (1, 0, 0, 0, 0, 0, 0)
    old_chars = [char for char in product(range(2), repeat=7) if not any(lift.character_descent(char, lift.old_kernel()))]
    rows = []
    for name, char in (("old_hyperino", fermion), ("old_hyperscalar", scalar),
                       ("bare_Sigma_c", previous.SIGMA), ("gauge_root_C", previous.CCHAR)):
        rows.append({"name": name, "center_character": list(char),
                     "epsT_epsS_sign_exponents": [lift.dot(char, KT), lift.dot(char, KS)],
                     "tangent_2pi_sign_exponent": lift.dot(char, lorentz)})
    if any(lift.dot(char, KT) or lift.dot(char, KS) for char in old_chars) or lorentz in lift.old_kernel():
        raise RuntimeError("old fermion parity was confused with a deck kernel")
    return {
        "bound_actual_hyper_and_scalar_characters": rows[:2], "all_four_comparison_rows": rows,
        "old_allowed_center_character_count": len(old_chars),
        "old_fermionic_center_character_count": sum(lift.dot(char, lorentz) for char in old_chars),
        "both_deck_generators_trivial_on_every_old_genuine_representation": True,
        "tangent_2pi_representative": list(lorentz),
        "tangent_2pi_is_old_identity": False,
        "epsT_is_unchanged_universal_fermion_parity": False,
        "proof": "epsT is represented by KT, a kernel element in the old group. Every genuine old field is therefore deck-trivial, including the displayed hyperino. The genuine tangent2pi class acts by -1 on this hyperino and +1 on its scalar. Bare Sigma_c is epsT-odd, but this does not turn epsT into the old universal fermion parity. KT includes the compensating Spin11,R,H3,H267 internal centers.",
        "unchanged_representations_repaired_by_relabeling_epsT_as_fermion_parity": False,
        "all_new_fermionic_extensions_spin_frames_or_relative_theories_excluded": False,
    }


@lru_cache(maxsize=1)
def pure_algebra_json():
    return json.dumps({"five_cover_all_lift_choices": exhaustive_cover_rows(),
                       "fixed_stratum_restriction_tests": fixed_stratum_rows(),
                       "explicit_changed_spatial_domains": changed_domain_certificate()},
                      sort_keys=True, separators=(",", ":"))


def build_certificate() -> dict:
    inputs = load_inputs()
    saved = inputs["v100_route"]["modified_equivariant_cover"]
    group = saved["pulled_back_square_space_group"]
    expected = {"A4": [1, 0], "UVUinvVinv": [0, 0], "AUAinvVinv": [0, 0], "AVAinvU": [0, 1]}
    if group["derived_deck_relation_defects"] != expected:
        raise RuntimeError("the actual saved complete space-group cocycle changed")
    if [row["old_power_deck_bits"] for row in group["fixed_strata"]] != [[1, 0], [1, 0], [1, 1], [1, 1]]:
        raise RuntimeError("the actual saved fixed-stratum restrictions changed")
    algebra = json.loads(pure_algebra_json())
    result = {
        "schema": SCHEMA,
        "status": "FROZEN_SPACE_GROUP_HAS_NO_LIFT_TO_ANY_PROPER_INTERMEDIATE_COVER__CHANGED_SUBGROUP_LIFTS_EXPLICIT",
        "input_core_hashes": {**{key: value[1] for key, value in PARENTS.items()},
                              "v100_modified_equivariant_cover": PREVIOUS_CORE,
                              "v88_smooth_lift": lift.V88_CORE, "v89_finite_lift": lift.V89_CORE},
        "bound_actual_frozen_data": {
            "space_group": "S=<A,U,V | A^4=1,[U,V]=1,AUA^-1=V,AVA^-1=U^-1>",
            "coordinate_order": lift.OLD_COORDINATES,
            "old_kernel_generators": {"D_geom": list(D), "KT": list(KT), "KN": list(KN), "KS": list(KS)},
            "retained_literal_geometric_identity": list(D),
            "saved_smooth_relation_defects": copy.deepcopy(group["bound_old_smooth_relation_defects"]),
            "saved_finite_alpha_U_V": copy.deepcopy(group["bound_primitive_C8_alpha_u_v"]),
            "derived_deck_relation_defects": copy.deepcopy(group["derived_deck_relation_defects"]),
            "saved_fixed_strata": copy.deepcopy(group["fixed_strata"]),
            "pullback_extension": "S_combined=(Z^2 x C2_epsS) semidirect C8_A, alpha(m,n,e)=(-n,m,e+n)",
            "pullback_identification": "The saved lifted A,U,V and the two independent central deck elements obey the displayed extension presentation. Both this group and the actual representation pullback project onto S with faithful kernel E=K/<D>=C2_T x C2_S. The generator map is surjective and identity on kernel and quotient, hence an isomorphism. Intermediate pullbacks are S_combined/H.",
        },
        "exact_obstruction_theorem": {
            "central_shift_formula": "For A'=aA,U'=uU,V'=vV with a,u,v in E/H: A'^4=T, [U',V']=0, A'U'A'^-1V'^-1=u+v, A'V'A'^-1U'=S+u+v.",
            "lift_invariant_defects": {"fourth_power": list(T), "sum_of_two_mixed_relators": list(S)},
            "criterion": "A lift of the fixed representation exists iff both T and S vanish in E/H, equivalently H=E.",
            "number_of_intermediate_covers_including_old": 5,
            "number_of_central_generator_choices_checked": sum(row["number_of_central_generator_choices"] for row in algebra["five_cover_all_lift_choices"]),
            "number_of_proper_covers_admitting_frozen_representation": 0,
            "proof_of_exhaustive_lift_scope": "Any preimage of each fixed old generator differs from the saved preimage by an element of the central deck kernel. Enumerating all three deck choices therefore includes every homomorphism lift, not only the saved generators. A simultaneous conjugation cannot change existence, since conjugators lift through the surjective cover. The two central invariants give the symbolic all-choice proof, independently of the finite enumeration.",
            "cyclic_detection_scope": "For this particular pulled-back extension the fixed C4 and C2 powers T and T+S span E, so its cyclic restrictions also detect every proper quotient. No general theorem that cyclic tests determine all H2 classes is asserted.",
            "full_H2_group_computed": False,
        },
        **algebra,
        "deck_versus_old_fermion_parity": fermion_parity_certificate(inputs["old_components"]),
        "scope": {
            "actual_saved_square_space_group_representation_is_tested": True,
            "all_central_lift_choices_are_included": True,
            "old_geometric_identity_D_and_quotient_are_preserved": True,
            "all_physical_Gammahat_backgrounds_identified": False,
            "all_group_extensions_or_relative_theories_excluded": False,
            "smooth_response_quantization_implies_frozen_equivariant_installation": False,
            "changed_S_representation_same_action_or_boundary_gluing_constructed": False,
            "old_genuine_representations_still_pull_back_to_every_cover": True,
            "representation_pullback_implies_lift_of_the_fixed_S_bundle": False,
        },
        "remaining_obligations": {
            "new_spatial_or_symmetry_category_adopted": False,
            "actual_global_physical_background_and_Dirac_category_identified": False,
            "new_projectors_SUSY_spectrum_and_positive_multiplicity_action_rebuilt": False,
            "same_action_relative_wall_defect_corner_gluing_and_regulator": False,
            "full_Gammahat_Dai_Freed_WCS_completion": False,
            "any_gate_closed": False,
        },
        "primary_sources": [
            {"url": "https://arxiv.org/pdf/2307.14658v3", "use": "Jain-Joshi-Spallone, Theorem1.2 and Proposition3.5: lifting a homomorphism through a central extension is equivalent to splitting its pullback. Section3.1 defines pullback/pushout and Corollary3.4.1 controls inner conjugation. The exact two-defect obstruction, all89 choices and changed-subgroup sections are derived here from the saved action; no full cohomology classification is borrowed."},
            {"url": "https://web.math.ucsb.edu/~dai/book.pdf", "use": "Sections1.3 and2.3 distinguish the Lorentz spin-cover central sign from the Spin-c determinant and spinor characters. The actual old hypermultiplet parity rows and correlated kernel are rebound from the immutable V98-V100 chain; an internal deck element is not relabeled as universal fermion parity."},
        ],
    }
    result["core_sha256"] = canonical_sha(result)
    return result


def validate_certificate(report: Mapping) -> None:
    if report.get("core_sha256") != canonical_sha(report) or dict(report) != build_certificate():
        raise RuntimeError("F101 frozen-space-group cover certificate differs from fresh bound derivation")


if __name__ == "__main__":
    print(json.dumps(build_certificate(), indent=2, sort_keys=True))
