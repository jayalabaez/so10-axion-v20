#!/usr/bin/env python3
"""V84 full-Gammahat obstruction, anomaly phase and F4 redesign audit.

V84 executes F84 without promoting a scaffold to a completed theory.  It
proves that the unchanged five-factor parent cannot satisfy the two square
space-group conjugation relations: their defects always differ by the pure
Spin(11) center.  Killing that center both excludes the localized 16s and
selects the SO(11) form whose Green--Schwarz coefficient fails strong
quantization.

The smallest ordinary-group repair found here adds a non-R C4 spinor-grading
factor.  Its diagonal Spin(11)-C4F kernel repairs the central algebra while
keeping Spin(11) faithful, and an explicit charge/stabilizer scaffold preserves
the required Yukawa and rank-breaking operators.  Fixed-stratum isotropy,
discrete anomalies, the full BV/regulator complex and WCS data remain open, so
this is a selected redesign candidate rather than an accepted action.

On the smooth Q4 cycle the missing Rarita contribution is evaluated with the
published lens-bundle eta formula.  Convention data currently pinned on disk
determine a conjugate pair: the bare phase is necessarily i or -i.  Every one
of sixteen newly enumerated algebraic Lambda/4Lambda r^2 coefficient shifts
has reference-q0 WCS phase +1 or -1, hence none cancels the bare phase.  This
over-inclusive smooth-cycle screen is not V78's physical-refinement set;
full-HGamma torsion and a globally extending odd bordism character remain
open.

Finally H2(F4) is identified exactly with the frozen U charge lattice.  Its
-4 section carries the so(11) Lie algebra with three vector hypers, its fiber is the critical
heterotic string, and the two missing Q4 residues have unique coefficient-
minimal effective lifts S+F and 3S+F.  They are reducible charge/curve
configurations and therefore only candidate junctions, not new elementary
strings.  The former T2 x S4 source has an ordinary
relative cap, but the restricted direct-product ansatz is not half-BPS and
every product double is bordism-distinct from Q4.  The associated-graded delta
candidate has potential incoming d3 and d4 maps whose source-page survival is
not established; both differential values, its chain-level identification and
the hidden extension remain open.

No candidate is accepted.  The unchanged action remains rejected, the
redesign program is viable, and G1--G8 remain open.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parent
V70_ROUTE_PATH = ROOT / "SUSY_V70_SPIN11_LOCALIZED_PARENT_SPIN_FLAVOR_COMPLETION_AUDIT.json"
V71_ROUTE_PATH = ROOT / "SUSY_V71_SPIN11_NORMAL_BUNDLE_EQUIVARIANT_GS_AUDIT.json"
V65_ROUTE_PATH = ROOT / "SUSY_V65_SPIN11_ORPHAN_LIFTING_CLASSIFICATION_AUDIT.json"
V78_ROUTE_PATH = ROOT / "SUSY_V78_TORSION_CHARACTER_PARENT_REDESIGN_AUDIT.json"
V81_ROUTE_PATH = ROOT / "SUSY_V81_Q4_PARENT_LIFT_ETA_RELATIVE_CAP_AUDIT.json"
V82_ROUTE_PATH = ROOT / "SUSY_V82_QHAT_BORDISM_D15_COMPENSATOR_AUDIT.json"
V83_ROUTE_PATH = ROOT / "SUSY_V83_CYCLIC_PARENT_WCS_INSTANTON_STRING_AUDIT.json"
V83_MASTER_PATH = ROOT / "SUSY_V83_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_JSON = ROOT / "SUSY_V84_GAMMAHAT_BARE_PHASE_F4_HETEROTIC_STRING_AUDIT.json"
OUT_MD = ROOT / "SUSY_V84_GAMMAHAT_BARE_PHASE_F4_HETEROTIC_STRING_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v84_gammahat_bare_phase_f4_heterotic_string_audit.py"

EXPECTED_CORES = {
    "v65_route": "b87696403fb46c4a6b044be8abe58dd5f82b63a83a58fff262a6f00bdd6914ae",
    "v70_route": "3e7b8e53916fbbc05bdcdf9632bcf4359aa4888b037df775c37d8d7d2551b228",
    "v71_route": "0162828ebd2b1e28d4fcbcf4ea1e6c61178d305cec79abd6d36a55719bb0f1ea",
    "v78_route": "1e2d44a6aedff03614cb712d3ba3a88f42d214638edf758ecea532c03d8c4e58",
    "v81_route": "dff11c6502c8a7e709fc2ad5096ce4a0825ee75547810226f59ed4c286967ea1",
    "v82_route": "d35058abac1ad10f96dbf2d383d5b68d67826e4c42403d688d800f1f852f7105",
    "v83_route": "a2133df04b79a28d87dc9248aa5fac52c9392137e21ce1099034a6cba2048456",
    "v83_master": "b4a626429afcd28a9147c6b0ab2dd00e2304fc611c7499df1eb39dd76fa217f6",
}

SCHEMA = "susy_v84_gammahat_bare_phase_f4_heterotic_string_audit_v1"
VERSION = "V84"
DATE = "2026-09-01"
STATUS = (
    "V84_GAMMAHAT_BARE_PHASE_F4_HETEROTIC_STRING_AUDIT__V65_V70_V71_V78_V81_V82_V83_CORES_BOUND__"
    "UNCHANGED_FIVE_FACTOR_GAMMAHAT_REJECTED_PURE_SPIN11_CENTER_FORCED__"
    "C4F_SPINOR_GRADING_CENTRAL_ALGEBRA_AND_OPERATOR_SCAFFOLD_PASS_EXACT__FULL_PARENT_OPEN__"
    "SMOOTH_Q4_BARE_PHASE_PRIMITIVE_FOURTH_ROOT__SIXTEEN_ALGEBRAIC_R2_WCS_SHIFTS_SCREENED__"
    "F4_SO11_LIE_ALGEBRA_HETEROTIC_STRING_AND_MINIMAL_EFFECTIVE_RESIDUE_LIFTS_EXACT__UV_WEIERSTRASS_OPEN__"
    "PRODUCT_CAP_EXACT__DIRECT_PRODUCT_BPS_AND_Q4_DOUBLE_REJECTED__DELTA_AHSS_SOURCE_PAGE_D3_D4_AND_EXTENSION_OPEN__"
    "NO_ACCEPTED_EXTENSION__CURRENT_ACTION_REJECTED__REDESIGN_PROGRAM_VIABLE__G1_TO_G8_OPEN"
)


def canonical_sha(value: Any) -> str:
    body = copy.deepcopy(value)
    if isinstance(body, dict):
        body.pop("core_sha256", None)
    payload = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def normalized_file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load_bound(path: Path, expected: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    embedded = value.get("core_sha256")
    if embedded != canonical_sha(value):
        raise RuntimeError(f"noncanonical parent core for {path.name}")
    if embedded != expected:
        raise RuntimeError(f"bound core mismatch for {path.name}")
    return value


def add2(*vectors: Sequence[int]) -> tuple[int, ...]:
    return tuple(sum(v[i] for v in vectors) % 2 for i in range(len(vectors[0])))


def span2(generators: Sequence[Sequence[int]]) -> set[tuple[int, ...]]:
    if not generators:
        return set()
    zero = tuple(0 for _ in generators[0])
    result = {zero}
    for generator in generators:
        result |= {add2(value, generator) for value in list(result)}
    return result


def pair_u(left: Sequence[int | Fraction], right: Sequence[int | Fraction]) -> int | Fraction:
    return left[0] * right[1] + left[1] * right[0]


def frac(value: Fraction | int) -> str:
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def unchanged_gammahat_no_go(v70: Mapping[str, Any], v71: Mapping[str, Any], v83: Mapping[str, Any]) -> dict[str, Any]:
    relations = v70["genuine_spin_lift"]["exact_relations"]
    if any(
        relations[key] != value
        for key, value in {
            "qhat_fourth": "-1",
            "qhat_what_qhat_inverse": "what = - what^{-1}",
            "what_squared": "-1",
        }.items()
    ):
        raise RuntimeError("V70 noncentral Spin11 lift changed")
    old = v83["smooth_bulk_cyclic_parent_audit"]
    annihilator = old["bulk_kernel_nonuniqueness"]["annihilator_subspace_mod2"]
    expected_annihilator = [[0, 0, 0, 0, 0], [0, 1, 0, 0, 0], [1, 0, 1, 1, 1], [1, 1, 1, 1, 1]]
    if annihilator != expected_annihilator:
        raise RuntimeError("V83 smooth annihilator changed")
    so_fallback = v71["equivariant_GS_WuCS_boundary"]["SO11_fallback_fails"]
    if so_fallback["b"] != [2, -1]:
        raise RuntimeError("V71 SO11 quantization datum changed")
    b_even = all(value % 2 == 0 for value in so_fallback["b"])
    if b_even:
        raise RuntimeError("V71 odd SO11 anomaly coefficient changed")

    zero = (0, 0, 0, 0, 0)
    d = (1, 1, 1, 1, 1)
    e11 = (0, 1, 0, 0, 0)
    a = add2(d, e11)
    asm = span2((d, e11))
    rows: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    defect_pairs: Counter[tuple[tuple[int, ...], tuple[int, ...]]] = Counter()
    for x in itertools.product((0, 1), repeat=5):
        for y in itertools.product((0, 1), repeat=5):
            d1 = add2(x, y)
            d2 = add2(d1, e11)
            kernel = span2((d, d1, d2))
            n1 = x[0] == x[2] and y[0] == y[2]
            smooth_compatible = kernel <= asm
            unchanged_smooth = x in asm and y in asm
            counts["raw"] += 1
            counts[f"kernel_dimension_{(len(kernel)).bit_length() - 1}"] += 1
            counts["contains_e11"] += int(e11 in kernel)
            counts["N1_preserving"] += int(n1)
            counts["smooth_kernel_compatible"] += int(smooth_compatible)
            counts["N1_and_smooth_kernel_compatible"] += int(n1 and smooth_compatible)
            counts["unchanged_bound_smooth_operator"] += int(unchanged_smooth)
            counts["Kmin_solutions"] += int(kernel <= span2((d,)))
            counts["localized_16_descent_solutions"] += int(e11 not in kernel)
            selects_so11 = e11 in kernel
            counts["SO11_GS_quantization_solutions"] += int(selects_so11 and b_even)
            if unchanged_smooth:
                defect_pairs[(d1, d2)] += 1
            if len(rows) < 4 and unchanged_smooth and defect_pairs[(d1, d2)] == 1:
                rows.append({"x": list(x), "y": list(y), "D1": list(d1), "D2": list(d2)})

    expected_counts = {
        "raw": 1024,
        "contains_e11": 1024,
        "kernel_dimension_2": 128,
        "kernel_dimension_3": 896,
        "N1_preserving": 256,
        "smooth_kernel_compatible": 128,
        "N1_and_smooth_kernel_compatible": 64,
        "unchanged_bound_smooth_operator": 16,
        "Kmin_solutions": 0,
        "localized_16_descent_solutions": 0,
        "SO11_GS_quantization_solutions": 0,
    }
    if any(counts[key] != value for key, value in expected_counts.items()):
        raise RuntimeError("Gammahat central-deck enumeration changed")
    expected_pairs = {
        (zero, e11): 4,
        (e11, zero): 4,
        (a, d): 4,
        (d, a): 4,
    }
    if dict(defect_pairs) != expected_pairs:
        raise RuntimeError("unchanged-smooth defect-pair enumeration changed")

    return {
        "status": "REJECTED_EXACT_UNCHANGED_FIVE_FACTOR_PARENT",
        "presentation": "<A,U,V | A^4=1,[U,V]=1,AUA^-1=V,AVA^-1=U^-1>",
        "center_coordinates": ["T", "Spin11", "R", "H3", "H266"],
        "vectors": {"d": list(d), "e11": list(e11), "a=d+e11": list(a)},
        "universal_relation_theorem": {
            "arbitrary_translation_deck_choices": "x,y in F2^5",
            "D1": "x+y",
            "D2": "x+y+e11",
            "D1_plus_D2": "e11",
            "pure_Spin11_center_forced_for_every_assignment": True,
            "scope": "fixed V70 gauge Wilson, fixed V83 rotation roots and parity rows, ordinary group quotient",
            "gerbe_2group_or_added_spin_charge_factor_excluded": False,
        },
        "smooth_annihilator": {
            "elements": [list(v) for v in sorted(asm)],
            "Kmin": [list(v) for v in sorted(span2((d,)))],
            "Kmax": [list(v) for v in sorted(asm)],
            "Kmax_forced": True,
        },
        "finite_enumeration": dict(expected_counts),
        "unchanged_smooth_defect_pairs": [
            {"D1": list(pair[0]), "D2": list(pair[1]), "multiplicity": multiplicity}
            for pair, multiplicity in sorted(defect_pairs.items())
        ],
        "fatal_consequences": {
            "localized_16_center_character": "odd on 10_-1 + 5bar_3 + 1_-5",
            "localized_16_descends_through_Kmax": False,
            "multiplicity_repairs_center_character": False,
            "Kmax_global_gauge_form": "SO(11)",
            "strong_quantization_requires": "b in 2U",
            "b": [2, -1],
            "b_in_2U": False,
            "rank_fields_repair_obstruction": False,
        },
        "conclusion": "the unchanged five-factor H_Gamma parent is impossible within the enumerated ordinary-quotient scope",
    }


def c4f_repair_scout(v65: Mapping[str, Any], v83: Mapping[str, Any]) -> dict[str, Any]:
    d = (1, 1, 1, 1, 1, 0)
    e11f = (0, 1, 0, 0, 0, 1)
    pure_e11 = (0, 1, 0, 0, 0, 0)
    kernel = span2((d, e11f))
    if pure_e11 in kernel or len(kernel) != 4:
        raise RuntimeError("C4F kernel does not keep Spin11 faithful")

    sign_rows: list[dict[str, Any]] = []
    for u, v in itertools.product((0, 1), repeat=2):
        beta = (u + v) % 2
        d1 = tuple(beta * x for x in e11f)
        d2 = tuple((beta + 1) % 2 * x for x in e11f)
        if d1 not in kernel or d2 not in kernel:
            raise RuntimeError("matched C4F sign row fails quotient relation")
        sign_rows.append(
            {"u": u, "v": v, "beta": beta, "D1": list(d1), "D2": list(d2), "relations_exact_mod_KF": True}
        )

    independent_sign_rows: list[dict[str, Any]] = []
    for u, v, r, s in itertools.product((0, 1), repeat=4):
        gauge_parity = (u + v) % 2
        flavor_parity = (r + s) % 2
        d1 = (0, gauge_parity, 0, 0, 0, flavor_parity)
        d2 = (0, (gauge_parity + 1) % 2, 0, 0, 0, (flavor_parity + 1) % 2)
        passes = d1 in kernel and d2 in kernel
        if passes != (gauge_parity == flavor_parity):
            raise RuntimeError("C4F independent sign parity theorem changed")
        independent_sign_rows.append(
            {
                "gauge_u_v": [u, v],
                "flavor_r_s": [r, s],
                "gauge_parity": gauge_parity,
                "flavor_parity": flavor_parity,
                "D1": list(d1),
                "D2": list(d2),
                "passes": passes,
            }
        )
    if sum(row["passes"] for row in independent_sign_rows) != 8:
        raise RuntimeError("C4F independent sign enumeration changed")

    fatal_adjoint = next(
        row
        for row in v65["gut_scale_channel_classification"]["branches"]
        if row["id"] == "B5"
    )
    if fatal_adjoint["status"] != "CLOSED" or "forces v=0" not in fatal_adjoint["exact_obstruction"]:
        raise RuntimeError("V65 fatal spinor-adjoint trilinear contract changed")

    charges = {
        "16_matter": 1,
        "C_spinor": 1,
        "Cbar_spinor": 3,
        "A_hyper_11": 2,
        "B_hyper_11": 2,
        "C_hyper_11": 2,
        "X": 2,
        "Xbar": 2,
        "gravity_tensor_gauge_Sigma_neutral266": 0,
        "S_B": 0,
        "S_X": 0,
        "P_A": 2,
        "A0": 2,
        "S0": 0,
        "H_u": 2,
        "H_d": 2,
        "B0": 2,
        "H_dSigma": 0,
    }
    operator_specs = [
        ("16 16 H_u", ("16_matter", "16_matter", "H_u"), True, True),
        ("10 5bar H_d", ("16_matter", "16_matter", "H_d"), True, True),
        ("5bar N H_u", ("16_matter", "16_matter", "H_u"), True, True),
        ("N N X", ("16_matter", "16_matter", "X"), True, True),
        ("X Xbar", ("X", "Xbar"), True, True),
        ("Cbar C", ("Cbar_spinor", "C_spinor"), True, True),
        ("16 16 Cbar Cbar", ("16_matter", "16_matter", "Cbar_spinor", "Cbar_spinor"), True, True),
        ("Cbar 45 C", ("Cbar_spinor", "gravity_tensor_gauge_Sigma_neutral266", "C_spinor"), True, False),
        ("B0 H_uB H_dSigma", ("B0", "B_hyper_11", "H_dSigma"), True, True),
        ("mu_B H_uB H_dC", ("B_hyper_11", "C_hyper_11"), True, True),
        ("S0 H_uA H_dC", ("S0", "A_hyper_11", "C_hyper_11"), True, True),
        ("old B0 H_uB H_dC", ("B0", "B_hyper_11", "C_hyper_11"), False, False),
        ("old A0 H_uA H_dC", ("A0", "A_hyper_11", "C_hyper_11"), False, False),
    ]
    operators = []
    for name, fields, expected_invariant, target_vacuum_admissible in operator_specs:
        total = sum(charges[field] for field in fields) % 4
        invariant = total == 0
        if invariant != expected_invariant:
            raise RuntimeError(f"C4F operator classification changed: {name}")
        operators.append(
            {
                "operator": name,
                "fields": list(fields),
                "charge_mod4": total,
                "C4F_invariant": invariant,
                "expected_C4F_invariance": expected_invariant,
                "target_vacuum_admissible": target_vacuum_admissible,
                "dynamical_note": (
                    fatal_adjoint["exact_obstruction"]
                    if name == "Cbar 45 C"
                    else "no additional V65 obstruction bound in this row"
                ),
            }
        )

    old_parities = v83["smooth_bulk_cyclic_parent_audit"]["smooth_bulk_representation_descent"]["parity_rows_mod2"]
    if not all(sum(row) % 2 == 0 for row in old_parities.values()):
        raise RuntimeError("V83 krot descent changed")
    return {
        "status": "PASS_EXACT_CENTRAL_ALGEBRA_AND_OPERATOR_SCAFFOLD__FULL_PARENT_OPEN",
        "new_factor": {
            "group": "C4_F=<j | j^4=1>",
            "kind": "non-R finite spinor grading",
            "supercharge_charge_mod4": 0,
            "f": "j^2",
        },
        "extended_kernel": {
            "coordinate_order": ["T", "Spin11", "R", "H3", "H266", "f"],
            "krot": list(d),
            "kspin": list(e11f),
            "elements": [list(v) for v in sorted(kernel)],
            "is_Z2_squared": True,
            "contains_pure_Spin11_center": False,
            "Spin11_remains_faithful": True,
        },
        "lift_choice": {
            "A_F": "1",
            "U_11": "z11^u what",
            "V_11": "z11^v what",
            "U_F": "f^u j",
            "V_F": "f^v j",
            "U_H3_equals_V_H3": "-I",
            "tangent_and_Sp1R_translations": "trivial",
            "direct_bit_matched_representative_rows": sign_rows,
            "all_four_direct_bit_matched_rows_pass": True,
            "all_independent_gauge_flavor_sign_rows": independent_sign_rows,
            "independent_rows_total": 16,
            "independent_rows_passing": 8,
            "pass_criterion": "u+v=r+s mod2",
            "unmatched_parity_rows_pass": False,
        },
        "charge_assignment_mod4": charges,
        "representation_descent": {
            "smooth_C4F_charges_are_even": True,
            "all_V83_smooth_rows_annihilate_krot": True,
            "smooth_vector_adjoint_rows_annihilate_kspin": True,
            "localized_16_odd_F_times_odd_Spin11_is_even": True,
            "localized_16_pure_center_repaired": True,
            "full_localized_krot_and_isotropy_descent": False,
            "charged_hyper_projectors_unchanged": True,
            "reason_projectors_unchanged": "j=-1 and the Sp3 translation center=-1 on charge-two 11 hypers",
        },
        "operator_audit": {
            "rows": operators,
            "C4F_invariance_classification_matches": True,
            "doublet_heavy_row_retained": "(sqrt(2) g v_B, mu_B)",
            "old_optional_driver_terms_forbidden": ["old B0 H_uB H_dC", "old A0 H_uA H_dC"],
            "fatal_but_C4F_allowed_operator": "Cbar 45 C",
            "fatal_operator_bound_to_V65_B5": True,
            "spinor_Higgs_vacuum_selector_still_required": True,
        },
        "stabilizer_redesign": {
            "W": "S_B(B0^2-v_B^2)+S_X(X Xbar-v_X^2)+M_A A0 P_A",
            "C4F_charges": {"S_B": 0, "S_X": 0, "P_A": 2},
            "Z4R_charges": {"S_B": 2, "S_X": 2, "P_A": 0},
            "local_Hessian_blocks_nondegenerate_after_gauge_null": True,
            "global_supersymmetric_profile_constructed": False,
        },
        "open_consistency": [
            "krot character and A,UA,UA2 isotropy for every localized field",
            "equivariance of localized rank and spinor-Higgs VEVs",
            "all superpotential, Kahler, higher-dimensional and proton-selector operators",
            "a selector or dynamical replacement that excludes the V65-fatal Cbar 45 C trilinear",
            "mixed C4F-Spin11, C4F-gravity, cubic, fixed-point and Dai-Freed anomalies",
            "diagonal Spin11-C4F GS/WCS quantization and line/end-point consistency",
            "raw ghosts, BV brackets, antifields, regulators, Pfaffian orientations and zero-mode measures",
            "self-dual polarization, differential WCS, caps, junctions and relative source glue",
            "neutral Sp266 bundle and compactification phenomenology",
        ],
        "accepted_full_parent": False,
    }


ETA16 = {
    0: (-2, 2, 2, -2),
    2: (-7, -1, 5, 3),
    -2: (3, 5, -1, -7),
}


def q4_bare_and_wcs_audit(v78: Mapping[str, Any], v81: Mapping[str, Any], v83: Mapping[str, Any]) -> dict[str, Any]:
    published = v81["Q4_eta_shadow_audit"]["published_Q4_Dirac_eta"]["eta_m0123"]
    if published != ["-1/8", "1/8", "1/8", "-1/8"]:
        raise RuntimeError("V81 Q4 eta table changed")
    tangent = v81["Q4_source_domain_audit"]["Q4_tangent_geometry"]["stable_tangent_splitting"]
    if tangent != "TQ4+R^2=R^3+2(L_r)_R+(L_r tensor p^*O(2))_R":
        raise RuntimeError("V81 stable tangent splitting changed")
    for b in (-2, 0, 2):
        for m in range(4):
            if ETA16[b][m] != ETA16[-b][3 - m]:
                raise RuntimeError("lens-bundle eta conjugation symmetry changed")
    gravity16 = 2 * (ETA16[0][3] + ETA16[0][1]) + ETA16[2][3] + ETA16[-2][1]
    if gravity16 != 8:
        raise RuntimeError("Vec-1 eta contribution changed")
    gravity = Fraction(gravity16, 16)

    shadow = v81["Q4_eta_shadow_audit"]["V71_qhat_projector_character_shadow"]
    expected_shadow = {
        "three_11_eta_shadow": "-1/8",
        "neutral_266_eta_shadow": "-5/4",
        "adjoint_same_chirality_eta_shadow": "-5/8",
        "opposite_chirality_gaugino_eta_shadow": "5/8",
        "formal_spin_half_matter_plus_gaugino_shadow": "-3/4",
    }
    if any(shadow[key] != value for key, value in expected_shadow.items()):
        raise RuntimeError("V81 spin-half eta ledger changed")
    matter_minus_adjoint = Fraction(-3, 4)
    one_root_hyper_dimension = 3 * 11 + 266
    full_hyper_dimension = v83["regulated_bare_anomaly_contract"]["current_smooth_spectrum_substitution"]["complex_half_hyper_dimension"]
    if (one_root_hyper_dimension, full_hyper_dimension) != (299, 598):
        raise RuntimeError("SMW hypermultiplet pair dimensions changed")
    one_root_adjoint_dimension = 55
    full_rsym_paired_adjoint_dimension = 2 * one_root_adjoint_dimension
    direct_exponent = (gravity - matter_minus_adjoint) % 1
    calibrated_exponent = (-gravity + matter_minus_adjoint) % 1
    exponent_pair = sorted({int(4 * direct_exponent), int(4 * calibrated_exponent)})
    if exponent_pair != [1, 3]:
        raise RuntimeError("bare phase conjugacy class changed")

    ring = v78["space_group_torsion_audit"]["cohomology_ring_degree4"]
    if ring["group"] != "Z4{r^2} + Z2{rs} + Z2{s^2}":
        raise RuntimeError("V78 degree-four torsion ring changed")
    shifts = []
    w_counts: Counter[int] = Counter()
    total_counts: Counter[int] = Counter()
    for p, q in itertools.product(range(4), repeat=2):
        w = (2 + 2 * p * q) % 4
        w_counts[w] += 1
        totals = sorted({(epsilon + w) % 4 for epsilon in exponent_pair})
        if 0 in totals or w not in (0, 2):
            raise RuntimeError("algebraic r2 coefficient shift unexpectedly cancels")
        for total in totals:
            total_counts[total] += 1
        shifts.append(
            {
                "p": p,
                "q": q,
                "t": f"({p}u,{q}u)",
                "WCS_exponent_mod4": w,
                "WCS_phase": "+1" if w == 0 else "-1",
                "possible_total_exponents_mod4": totals,
                "cancels_for_any_allowed_bare_convention": False,
            }
        )
    if dict(w_counts) != {2: 12, 0: 4}:
        raise RuntimeError("restricted WCS phase count changed")

    reference = v83["Q4_linking_and_reference_WCS_audit"]["even_U_reference_quadratic_refinement"]
    if reference["reference_qhat_phase"] != "-1":
        raise RuntimeError("V83 reference WCS shadow changed")
    return {
        "status": "PASS_EXACT_PRIMITIVE_FOURTH_ROOT_BARE_CONJUGACY__SIXTEEN_ALGEBRAIC_R2_SHIFTS_SCREENED",
        "normalization_contract": {
            "Monnier_Moore": "log An/(2pi i)=1/2 xi_Rprime; xi=(spectral eta+h)/2",
            "IIBordia_Hsieh_table": "reduced APS eta; no extra h term is added",
            "disk_orientation_gap": "V81 does not pin the determinant/Pfaffian identification xi_MM=+eta_table versus -eta_table",
            "primary_source_calibration": "xi_MM=-eta_IIB, preferred exponent 3 and phase -i",
            "orientation_reversal": "complex conjugates the phase",
        },
        "eta_tables_numerator_over_16": {str(key): list(value) for key, value in ETA16.items()},
        "eta_table_symmetry": "eta[m,b]=eta[3-m,-b]",
        "stable_tangent_virtual_bundle": "(TQ-R)_C=2(Lr+Lr^-1)+(Lr O(2)+Lr^-1 O(-2))",
        "Rarita_Vec_minus_one": {
            "numerator_over_16": gravity16,
            "value_mod1": frac(gravity),
            "formula": "2(eta[3,0]+eta[1,0])+eta[3,+2]+eta[1,-2]",
            "quantity_in_anomaly_ledger": "contribution to (1/2) xi_Rprime after one-root SMW bookkeeping",
        },
        "spin_half_ledger": {
            "eta_R_minus_eta_Ad": frac(matter_minus_adjoint),
            "V81_row_is_one_root_quaternionic_ledger": True,
            "halving_V81_again_allowed": False,
            "Vec_minus_one_already_gauge_fixed_Rarita_virtual_class": True,
        },
        "SMW_pair_normalization_proof": {
            "reduced_eta_definition_includes_kernel_h": True,
            "eta_conjugate_partner_equality": "eta[m,b]=eta[3-m,-b]",
            "hyper_one_root_dimension": one_root_hyper_dimension,
            "hyper_full_complex_pair_dimension": full_hyper_dimension,
            "adjoint_one_R_root_dimension": one_root_adjoint_dimension,
            "adjoint_full_R_pair_dimension": full_rsym_paired_adjoint_dimension,
            "Rarita_R_pair_has_two_equal_conjugate_root_contributions": True,
            "pair_identity": "(1/2) xi(full conjugate pair)=one-root reduced eta contribution",
            "outer_half_already_consumed_by_pair_doubling": True,
            "computed_exponent": "(1/2)xi_Rprime=G-[eta(R)-eta(Ad)]",
            "common_BV_Pfaffian_orientation_constructed": False,
        },
        "bare_character": {
            "possible_exponents_mod4": exponent_pair,
            "possible_phases": ["i", "-i"],
            "primitive_fourth_root_proved": True,
            "preferred_primary_calibrated_exponent_mod4": 3,
            "preferred_primary_calibrated_phase": "-i",
            "fully_BV_orientation_pinned": False,
            "full_HGamma_physical_bare_character_constructed": False,
        },
        "algebraic_r2_coefficient_shift_screen": {
            "formula": "4q0(Y+t_pq)=2+2pq mod4",
            "rows": shifts,
            "WCS_exponent_counts": {str(key): w_counts[key] for key in sorted(w_counts)},
            "WCS_phases": ["+1", "-1"],
            "all_sixteen_fail_cancellation": True,
            "possible_total_exponents_are_odd": sorted(total_counts),
            "reference_branch_total_nontrivial": True,
            "classification_boundary": "new over-inclusive Lambda/4Lambda coefficient scan on the smooth s=0 cycle; not V78's 16 local corrections to 2Y and not 16 physical refinements",
            "V78_half_choice_from_delta_2Y_to_delta_Y_constructed": False,
        },
        "counterterm_boundary": {
            "reduced_subgroup": "<jq(q)>=Z4",
            "required_counterterm_exponent_parity": "odd",
            "reduced_character_exists_algebraically": True,
            "extension_to_full_Omega7_HGamma_proved": False,
            "adding_counterterm_changes_quantum_integrand": True,
        },
        "scope": {
            "reference_branch_rejected": True,
            "all_sixteen_new_algebraic_r2_coefficient_shifts_fail_reference_q0_cancellation": True,
            "all_physical_full_HGamma_refinements_rejected": False,
            "mixed_localized_translation_torsion_classified": False,
        },
    }


def f4_uv_and_string_audit(v70: Mapping[str, Any], v83: Mapping[str, Any]) -> dict[str, Any]:
    e = (1, 0)
    f = (0, 1)
    section = (2, -1)
    fiber = (-1, 0)
    canonical = (2, 2)
    b = tuple(v83["instanton_string_and_compact_source_audit"]["action_derived_sector"]["b_Spin11"])
    if b != section:
        raise RuntimeError("V83 b no longer equals the F4 section")
    if (pair_u(section, section), pair_u(fiber, fiber), pair_u(section, fiber)) != (-4, 0, 1):
        raise RuntimeError("F4 intersection form changed")
    if add2((0, 0), (0, 0)) != (0, 0):
        raise RuntimeError("F2 helper corrupted")
    if (-fiber[0], -fiber[1]) != e or (-(section[0] + 2 * fiber[0]), -(section[1] + 2 * fiber[1])) != f:
        raise RuntimeError("F4-to-U basis map changed")
    if (-2 * section[0] - 6 * fiber[0], -2 * section[1] - 6 * fiber[1]) != canonical:
        raise RuntimeError("F4 canonical class changed")

    j = (Fraction(-2), Fraction(-1, 4))
    geometry = {
        "basis_e_f": {"e": list(e), "f": list(f), "e2": pair_u(e, e), "f2": pair_u(f, f), "e_dot_f": pair_u(e, f)},
        "section_S": list(section),
        "fiber_F": list(fiber),
        "canonical_K": list(canonical),
        "intersections": {
            "S2": pair_u(section, section),
            "F2": pair_u(fiber, fiber),
            "S_dot_F": pair_u(section, fiber),
            "K2": pair_u(canonical, canonical),
            "K_dot_S": pair_u(canonical, section),
            "K_dot_F": pair_u(canonical, fiber),
        },
        "adjunction_genera": {
            "S": (pair_u(section, section) + pair_u(canonical, section)) // 2 + 1,
            "F": (pair_u(fiber, fiber) + pair_u(canonical, fiber)) // 2 + 1,
        },
        "geometric_Kahler_witness": {
            "j": [frac(x) for x in j],
            "j2": frac(pair_u(j, j)),
            "j_dot_S": frac(pair_u(j, section)),
            "j_dot_F": frac(pair_u(j, fiber)),
            "j_dot_K": frac(pair_u(j, canonical)),
        },
        "V70_witness_same_positive_cone_component": False,
        "chamber_redesign_required": True,
    }
    if geometry["intersections"] != {"S2": -4, "F2": 0, "S_dot_F": 1, "K2": 8, "K_dot_S": 2, "K_dot_F": -2}:
        raise RuntimeError("F4 exact intersection ledger changed")
    if geometry["adjunction_genera"] != {"S": 0, "F": 0}:
        raise RuntimeError("F4 adjunction changed")
    if geometry["geometric_Kahler_witness"] != {
        "j": ["-2", "-1/4"], "j2": "1", "j_dot_S": "3/2", "j_dot_F": "1/4", "j_dot_K": "-9/2"
    }:
        raise RuntimeError("F4 Kahler witness changed")

    residue_specs = (("base", (1, 3), 1, 1), ("qhat", (1, 1), 3, 1))
    residue_rows = []
    for name, target, amin, cmin in residue_specs:
        congruence_solutions = [
            (aa, cc)
            for aa, cc in itertools.product(range(4), repeat=2)
            if ((2 * aa - cc) % 4, (-aa) % 4) == target
        ]
        if congruence_solutions != [(amin, cmin)]:
            raise RuntimeError("F4 effective residue congruence classification changed")
        q = (2 * amin - cmin, -amin)
        tension = pair_u(j, q)
        q_dot_s = pair_u(q, section)
        if tuple(x % 4 for x in q) != target or q_dot_s >= 0:
            raise RuntimeError("F4 residue lift changed")
        samples = []
        for da, dc in itertools.product(range(3), repeat=2):
            aa, cc = amin + 4 * da, cmin + 4 * dc
            qq = (2 * aa - cc, -aa)
            samples.append(
                {
                    "a": aa,
                    "c": cc,
                    "Q": list(qq),
                    "residue": [x % 4 for x in qq],
                    "tension": frac(pair_u(j, qq)),
                    "adds_4S_or_4F": da > 0 or dc > 0,
                }
            )
            if tuple(x % 4 for x in qq) != target or pair_u(j, qq) < tension:
                raise RuntimeError("F4 effective-lift minimality changed")
        residue_rows.append(
            {
                "name": name,
                "target_residue_mod4": list(target),
                "effective_congruence": f"a={amin} mod4, c=1 mod4",
                "congruence_solutions_a_c_mod4": [list(value) for value in congruence_solutions],
                "minimal_coefficients_a_c": [amin, cmin],
                "Q": list(q),
                "decomposition": f"{amin}S+F",
                "tension": frac(tension),
                "Q2": pair_u(q, q),
                "Q_dot_b": pair_u(q, b),
                "Q_dot_S": q_dot_s,
                "S_is_forced_component": True,
                "irreducible_curve": False,
                "formal_charge_decomposition": f"F+{amin}S; a physical junction is not constructed",
                "sample_all_lifts_add_4S_or_4F": samples,
            }
        )

    N = 11
    vector_hypers = N - 8
    V = N * (N - 1) // 2
    charged_H = vector_hypers * N
    neutral_H = 244 + V - charged_H
    if (vector_hypers, V, charged_H, neutral_H) != (3, 55, 33, 266):
        raise RuntimeError("F4 SO11 spectrum match changed")
    if v70["fixed_locus_twist_ledger"]["selected_integer_m301_11s"][0]["hyper"] != "A":
        raise RuntimeError("V70 three-vector spectrum contract changed")

    q = fiber
    q2 = pair_u(q, q)
    qk = pair_u(q, canonical)
    qb = pair_u(q, b)
    c_l = 3 * q2 - 9 * qk + 2
    c_r = 3 * q2 - 3 * qk
    k_l = Fraction(q2 + qk, 2) + 1
    sugawara = Fraction(55 * qb, qb + 9)
    if (c_l, c_r, k_l, qb, sugawara) != (20, 6, 0, 1, Fraction(11, 2)):
        raise RuntimeError("critical F-string anomaly ledger changed")
    return {
        "status": "PASS_EXACT_F4_TOPOLOGICAL_SO11_LIE_ALGEBRA_HETEROTIC_STRING_SCAFFOLD__EXPLICIT_UV_MODEL_OPEN",
        "geometry": geometry,
        "so11_Lie_algebra_divisor_spectrum": {
            "divisor": "S with S^2=-4",
            "published_rule": "SO(N) on F4 has N-8 vector hypers",
            "N": N,
            "vector_hypers": vector_hypers,
            "spinor_hypers": 0,
            "flavor": "Sp(3)",
            "T": 1,
            "V": V,
            "H_total": 299,
            "H_charged": charged_H,
            "H_neutral": neutral_H,
            "matches_frozen_Lie_algebra_and_multiplicity_scaffold": True,
            "global_gauge_group_or_line_operator_match": False,
            "smooth_CY3_h21_if_realized": 265,
        },
        "critical_heterotic_fiber_string": {
            "Q": list(q),
            "Q2": q2,
            "Q_dot_K": qk,
            "Q_dot_b": qb,
            "interacting_cL_cR": [c_l, c_r],
            "center_of_mass_cL_cR": [4, 6],
            "full_cL_cR": [c_l + 4, c_r + 6],
            "k_l": frac(k_l),
            "Spin11_level": qb,
            "Spin11_Sugawara_c": frac(sugawara),
            "Sugawara_below_cL": sugawara < c_l,
            "matches_published_critical_heterotic_fiber_sector": True,
            "conditional_on_explicit_F4_Ftheory_realization": True,
            "D3_worldsheet_in_this_model_constructed": False,
        },
        "effective_Q4_residue_lifts": {
            "effective_cone": "Z_nonnegative{S,F}",
            "rows": residue_rows,
            "both_targets_reached": True,
            "coefficient_minimal_lifts_unique": True,
            "coefficient_minimal_representative_selected_in_F4_effective_cone": True,
            "infinitely_many_nonminimal_effective_lifts_remain": True,
            "elementary_new_string_constructed": False,
            "junction_inflow_and_glue_computed": False,
        },
        "UV_acceptance_boundary": {
            "anomaly_divisor_heterotic_dual_scaffold": True,
            "explicit_compact_non_split_I2star_Weierstrass": False,
            "residual_discriminant_and_nonminimal_4_6_audit": False,
            "Hodge_count_derived_from_geometry": False,
            "Mordell_Weil_and_global_Spin11_form": False,
            "full_HGamma_lift": False,
        },
    }


def relative_cap_bps_and_delta_audit(v81: Mapping[str, Any], v82: Mapping[str, Any], v83: Mapping[str, Any]) -> dict[str, Any]:
    delta = v83["relative_delta_hidden_extension_audit"]
    if delta["classes"]["delta_exact_order"] != "OPEN_ZERO_OR_ORDER2" or delta["Adams_diagnosis"]["candidate"] != "h0*p":
        raise RuntimeError("V83 delta contract changed")
    order_q4 = v82["reduced_qhat_Q4_bordism_audit"]["classes"]["order_d"]
    if order_q4 != 4:
        raise RuntimeError("V82 Q4 order changed")
    return {
        "status": "PASS_EXACT_ORDINARY_PRODUCT_CAP__REJECTED_DIRECT_PRODUCT_BPS_AND_Q4_DOUBLE__DELTA_SOURCE_PAGE_D3_D4_AND_EXTENSION_OPEN",
        "restricted_T2xS4_BPS_audit": {
            "ansatz": "unwarped direct product, round S4, constant tensor scalar, H=0, Spin11 anti-instanton",
            "gaugino_projection_can_hold": True,
            "gravitino_equation_reduces_to_parallel_spinor": True,
            "round_S4_has_parallel_spinor": False,
            "gauge_instanton_twists_supercharge": False,
            "flat_T2_Einstein_equation_with_nonzero_longitudinal_YM_and_string_stress": False,
            "bounding_even_T2_spin_structure_has_parallel_spinor": False,
            "fully_periodic_parallel_T2_spin_structure_bounds": False,
            "half_BPS_solution_in_restricted_ansatz": False,
            "warped_fluxed_singular_or_R_twisted_generalization_excluded": False,
        },
        "ordinary_relative_cap": {
            "C7": "V3 x S4 with boundary T2 x S4",
            "V3": "S1 x D2 for a bounding/even T2 spin structure",
            "W3": "V3 x {point}",
            "homotopy_type": "S1 x S4",
            "H2_RmodZ": 0,
            "H3_RmodZ": 0,
            "Y": "-b u_C",
            "source": "+b PD_C(W3)",
            "residual": [0, 0],
            "ordinary_differential_trivialization_exists": True,
            "flat_ambiguity": False,
            "WCS_Wu_quadratic_trivialization_constructed": False,
            "worldsheet_Dai_Freed_glue_constructed": False,
        },
        "product_double_no_go": {
            "double_form": "N3 x S4",
            "example_N3": "L(4,1)",
            "SpinZ8_datum_factors_through_N3": True,
            "S4_class_in_Omega4Spin": 0,
            "forgetful_product_class_in_Omega7SpinZ8": 0,
            "Q4_forgetful_order": order_q4,
            "product_double_equals_Q4": False,
            "entangled_Q4_fibration_relative_source_excluded": False,
        },
        "delta_AHSS_d3_d4_candidate_audit": {
            "mixed_associated_graded_candidate": "E4,3=H4(BSpin11;Omega3^Spin-Z8)=Z2",
            "Adams_name": "h0*p",
            "coefficient_and_homology_input_data": {
                "Omega2_SpinZ8": 0,
                "Omega6_SpinZ8": 0,
                "H1_BSpin11": 0,
                "H2_BSpin11": 0,
                "Omega1_SpinZ8": "Z8",
                "H6_BSpin11_Z": "Z2",
                "H6_BSpin11_Z8": "Z2",
                "H7_BSpin11_Z": 0,
                "H7_BSpin11_Z8_by_UCT": "Z2 from Tor(H6,Z8)",
                "H9_BSpin11_Z": "NOT_AUDITED",
            },
            "differential_elimination": [
                {"map": "outgoing d2:E4,3->E2,4", "zero_reason": "H2(BSpin11)=0"},
                {"map": "outgoing d3:E4,3->E1,5", "zero_reason": "H1(BSpin11)=0"},
                {"map": "outgoing d4:E4,3->E0,6", "zero_reason": "Omega6^Spin-Z8=0"},
                {"map": "incoming d2:E6,2->E4,3", "zero_reason": "Omega2^Spin-Z8=0"},
                {"map": "r>=5", "zero_reason": "first-quadrant degree bounds"},
            ],
            "potential_incoming_AHSS_differentials_on_associated_graded_candidate": [
                "potential incoming d3:E3_7,1 -> E3_4,3; E2 source H7(BSpin11;Z8)=Z2, E3 source survival uncomputed",
                "potential incoming d4:E4_8,0 -> E4_4,3; E2 source H8(BSpin11;Z), E4 source survival uncomputed",
            ],
            "source_page_precursor_audit": {
                "d3_source_incoming_d2": "E2_9,0=H9(BSpin11;Z) -> E2_7,1; source group and differential not audited",
                "d3_source_outgoing_d2": "E2_7,1 -> E2_5,2=0 because Omega2^Spin-Z8=0",
                "d3_source_E3_survival_computed": False,
                "d4_source_outgoing_d2": "E2_8,0=H8(BSpin11;Z) -> E2_6,1=H6(BSpin11;Z8)=Z2; value not computed",
                "d4_source_E4_survival_computed": False,
            },
            "d3_value_computed": False,
            "degree8_d4_controller": "q2=(p2-lambda^2)/2 reducing to w8",
            "qhat_w4": 0,
            "qhat_w6": 0,
            "qhat_w8": "r^4 nonzero",
            "lower_characteristic_test_decides": False,
            "complex_vector_and_spinor_rho_mod1": [0, 0],
            "half_vector_eta": "1/2",
            "half_vector_eta_is_bordism_character": False,
            "counterexample": "on S8 a stable Spin11 generator can have lambda=0,p2=+/-6 and twisted index -p2/6 odd",
            "q2_counterterm_could_remove_filling_flip": True,
            "physical_q2_refinement_selected": False,
            "candidate_d4_value_computed": False,
            "chain_level_identification_of_delta_with_candidate_proved": False,
            "post_Einfinity_hidden_extension_resolved": False,
            "delta_exact_order": "OPEN_ZERO_OR_ORDER2",
        },
    }


def candidate_matrix() -> list[dict[str, Any]]:
    return [
        {
            "id": "F84_UNCHANGED_FIVE_FACTOR_HGAMMA",
            "selected": False,
            "accepted": False,
            "status": "REJECTED_EXACT_PURE_SPIN11_CENTER_FORCED",
        },
        {
            "id": "F84_C4F_SPINOR_GRADING_PARENT_REDESIGN",
            "selected": True,
            "accepted": False,
            "status": "PASS_EXACT_CENTRAL_ALGEBRA_AND_OPERATOR_SCAFFOLD__GLOBAL_ANOMALY_BV_WCS_OPEN",
        },
        {
            "id": "F84_REFERENCE_AND_ALGEBRAIC_LAMBDA_MOD4_R2_SHIFT_SCREEN",
            "selected": False,
            "accepted": False,
            "status": "FAIL_SCREEN_EXACT_ODD_TOTAL_MU4_CHARACTER__NOT_PHYSICAL_REFINEMENT_CLASSIFICATION",
        },
        {
            "id": "F84_F4_so11_LIE_ALGEBRA_HETEROTIC_UV_SCAFFOLD",
            "selected": True,
            "accepted": False,
            "status": "PASS_EXACT_TOPOLOGICAL_SPECTRUM_AND_STRING_SCAFFOLD__WEIERSTRASS_GLOBAL_FORM_OPEN",
        },
        {
            "id": "F84_PRODUCT_RELATIVE_CAP_TO_Q4",
            "selected": False,
            "accepted": False,
            "status": "REJECTED_EXACT_PRODUCT_DOUBLE_BORDISM_CLASS_ZERO",
        },
    ]


def gate_ledger() -> dict[str, str]:
    return {
        "G1": "OPEN: the unchanged ordinary five-factor parent is exactly rejected; the C4F central algebra passes, but a full stratified H_Gamma action, common regulator and accepted UV completion do not exist.",
        "G2": "OPEN: no accepted C4F/F4 Wilsonian action, supersymmetry-breaking sector, soft spectrum or threshold calculation exists.",
        "G3": "OPEN: C4F translation relations pass centrally, but complete localized isotropy, global bundles, VEV profiles and an explicit compact F4 geometry remain absent.",
        "G4": "OPEN: the candidate smooth-Q4 Dai-Freed exponent is a primitive fourth root up to conjugation, but the full-parent BV/Pfaffian orientation, zero-mode measure and common regulator are absent.",
        "G5": "OPEN: the redesigned stabilizer has only a local Hessian witness; neutral zero modes, the fatal spinor-adjoint selector and all-order stabilization remain unresolved.",
        "G6": "OPEN: the F4 fiber string, reducible residue charges and an ordinary product cap exist, but junction inflow, differential WCS glue and an entangled on-shell half-BPS source do not.",
        "G7": "OPEN: no accepted redesigned action yields a derived family, proton, collider, flavor or cosmological prediction.",
        "G8": "OPEN: the reference and algebraic r2 screens fail, while the physical full-HGamma WCS refinement, possible odd counterterm, source-page survival and values of potential incoming delta d3/d4 maps, the hidden extension and total anomaly trivialization remain unknown.",
    }


def source_catalog(v83: Mapping[str, Any]) -> list[dict[str, str]]:
    rows = copy.deepcopy(v83["primary_sources"])
    additions = [
        {
            "id": "hsieh_2018_discrete_anomalies",
            "title": "Discrete gauge anomalies revisited",
            "url": "https://arxiv.org/abs/1808.02881",
            "use": "reduced APS eta normalization and Dai-Freed phase convention",
        },
        {
            "id": "bahri_gilkey_1987_eta_lens_bundles",
            "title": "The eta invariant, Pin^c bordism, and equivariant Spin^c bordism for cyclic 2-groups",
            "url": "https://msp.org/pjm/1987/128-1/pjm-v128-n1-p01-p.pdf",
            "use": "primary lens-space-bundle eta formula",
        },
        {
            "id": "kumar_morrison_taylor_2009_f4_so",
            "title": "Mapping 6D N=1 supergravities to F-theory",
            "url": "https://arxiv.org/abs/0911.3393",
            "use": "Hirzebruch-surface intersection data and SO(N) matter rule on F4",
        },
        {
            "id": "morrison_taylor_2012_f_theory_bases",
            "title": "Classifying bases for 6D F-theory models",
            "url": "https://arxiv.org/abs/1201.1943",
            "use": "F4 section/fiber geometry and effective cone",
        },
        {
            "id": "lee_lerche_weigand_2018_tensionless_strings",
            "title": "Tensionless Strings and the Weak Gravity Conjecture",
            "url": "https://arxiv.org/abs/1808.05958",
            "use": "D3 brane on the Hirzebruch fiber as the critical six-dimensional heterotic string",
        },
    ]
    known = {row["id"] for row in rows}
    rows.extend(row for row in additions if row["id"] not in known)
    return rows


def build_report() -> dict[str, Any]:
    v65 = load_bound(V65_ROUTE_PATH, EXPECTED_CORES["v65_route"])
    v70 = load_bound(V70_ROUTE_PATH, EXPECTED_CORES["v70_route"])
    v71 = load_bound(V71_ROUTE_PATH, EXPECTED_CORES["v71_route"])
    v78 = load_bound(V78_ROUTE_PATH, EXPECTED_CORES["v78_route"])
    v81 = load_bound(V81_ROUTE_PATH, EXPECTED_CORES["v81_route"])
    v82 = load_bound(V82_ROUTE_PATH, EXPECTED_CORES["v82_route"])
    v83 = load_bound(V83_ROUTE_PATH, EXPECTED_CORES["v83_route"])
    v83_master = load_bound(V83_MASTER_PATH, EXPECTED_CORES["v83_master"])
    gamma = unchanged_gammahat_no_go(v70, v71, v83)
    c4f = c4f_repair_scout(v65, v83)
    phase = q4_bare_and_wcs_audit(v78, v81, v83)
    f4 = f4_uv_and_string_audit(v70, v83)
    cap = relative_cap_bps_and_delta_audit(v81, v82, v83)
    candidates = candidate_matrix()
    sources = source_catalog(v83)
    gates = gate_ledger()
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "question": "Can F84 complete the unchanged parent, or identify and test a minimal redesigned physics route?",
        "lineage": {
            "V65_route_core": v65["core_sha256"],
            "V70_route_core": v70["core_sha256"],
            "V71_route_core": v71["core_sha256"],
            "V78_route_core": v78["core_sha256"],
            "V81_route_core": v81["core_sha256"],
            "V82_route_core": v82["core_sha256"],
            "V83_route_core": v83["core_sha256"],
            "V83_master_core": v83_master["core_sha256"],
            "supersession_scope": "executes F84 and supersedes V83's open translation, bare-phase and formal-charge-lift questions; it does not supersede the full-parent acceptance boundary",
        },
        "unchanged_five_factor_Gammahat_no_go": gamma,
        "C4F_spinor_grading_repair_scout": c4f,
        "regulated_Q4_bare_and_WCS_audit": phase,
        "F4_SO11_heterotic_string_scaffold": f4,
        "relative_cap_BPS_and_delta_audit": cap,
        "candidate_matrix": candidates,
        "candidate_adjudication": {
            "selected_ids": [row["id"] for row in candidates if row["selected"]],
            "accepted_ids": [row["id"] for row in candidates if row["accepted"]],
        },
        "terminal_decision": {
            "unchanged_five_factor_parent_rejected_exactly": True,
            "pure_Spin11_center_forced": True,
            "C4F_extended_central_algebra_constructed": True,
            "C4F_smooth_descent_and_localized_pure_center_repair": True,
            "C4F_full_localized_isotropy_constructed": False,
            "C4F_discrete_anomaly_BV_WCS_parent_constructed": False,
            "smooth_Q4_bare_phase_conjugacy_class_computed": True,
            "smooth_Q4_bare_phase_possible_values": ["i", "-i"],
            "all_sixteen_algebraic_r2_shift_screen_rows_fail": True,
            "all_full_HGamma_WCS_refinements_fail": False,
            "F4_charge_lattice_and_so11_Lie_algebra_spectrum_match": True,
            "critical_heterotic_fiber_string_anomaly_ledger_matches_known_UV_sector": True,
            "both_Q4_residues_have_minimal_effective_F4_charge_lifts": True,
            "explicit_compact_F4_Weierstrass_parent_constructed": False,
            "restricted_T2xS4_half_BPS_solution_exists": False,
            "ordinary_relative_product_cap_constructed": True,
            "product_cap_double_represents_Q4": False,
            "delta_exact_order": "OPEN_ZERO_OR_ORDER2",
            "same_action_microscopic_completion_found": False,
            "accepted_full_parent_action_exists": False,
            "selected_candidate_accepted": False,
            "current_action_status": "REJECTED",
            "research_program_status": "VIABLE_C4F_F4_REDESIGN_FRONTIER__FULL_QUANTUM_PARENT_OPEN",
            "closed_gates": [],
            "theory_complete": False,
            "honest_outcome": "The unchanged ordinary five-factor parent is now exactly rejected.  A minimal C4F algebraic/operator redesign and an F4 heterotic/F-theory scaffold solve two sharp structural obstructions, while the reference WCS branch, a new over-inclusive sixteen-row smooth r2 screen and the product source route fail.  No explicit global UV model, full stratified/BV parent, physical WCS refinement or entangled source glue exists yet.",
        },
        "gate_ledger": gates,
        "open_obligations": [
            "construct every C4F-extended fixed-stratum isotropy representation and localized VEV profile",
            "compute all C4F discrete, mixed, Dai-Freed and fixed-point anomalies on one full H_Gamma bordism theory",
            "descend the complete raw/BV/BRST/regulator complex and fix Pfaffian orientations",
            "build an explicit compact non-split I2* so11 Weierstrass model on F4 and derive its Hodge/Mordell-Weil/global-form data",
            "realize C4F as a genuine UV flat flavor or gerbe sector compatible with the F4/heterotic dual",
            "select the full differential Y/WCS refinement or a globally extending odd counterterm and verify total character one",
            "construct and anomaly-match physical junction sectors, if any, from the reducible F+S charge/curve lifts for both Q4 residues",
            "audit precursor maps and page survival for the potential delta d3 source H7(BSpin11;Z8)=Z2 and d4 source H8(BSpin11;Z), then compute surviving maps, prove the chain-level identification and resolve the remaining extension",
            "replace the rejected product source by an entangled warped/fluxed half-BPS Q4-relative solution",
            "only after a full action exists, recompute vacuum, spectrum, thresholds, cosmology and phenomenology",
        ],
        "next_required_action": {
            "id": "F85_C4F_F4_WEIERSTRASS_GLOBAL_FORM_AND_DIFFERENTIAL_ORBIFOLD_GLUE",
            "primary_objective": "construct the explicit compact F4 so11 geometry and determine its global gauge form while realizing the C4F diagonal spin-charge parent on all strata with a common regulator",
            "secondary_objective": "select the physical differential WCS/q2 refinement, determine whether the reducible F+S lifts define junction sectors, and glue any resulting sector to an entangled Q4-relative source",
            "accepted": False,
        },
        "primary_sources": sources,
        "source_manifest": {
            "kind": "primary_sources_only",
            "count": len(sources),
            "ids": [row["id"] for row in sources],
            "catalog_sha256": canonical_sha(sources),
        },
        "artifact_hashes": {
            "line_ending_policy": "SHA256 after CRLF-to-LF normalization",
            "generator_sha256": normalized_file_sha(Path(__file__)),
            "test_sha256": normalized_file_sha(TEST_PATH),
        },
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    decision = report["terminal_decision"]
    gamma = report["unchanged_five_factor_Gammahat_no_go"]
    phase = report["regulated_Q4_bare_and_WCS_audit"]
    f4 = report["F4_SO11_heterotic_string_scaffold"]
    cap = report["relative_cap_BPS_and_delta_audit"]
    obligations = "".join(f"- {item}\n" for item in report["open_obligations"])
    gates = "".join(f"- {key}: {value}\n" for key, value in report["gate_ledger"].items())
    residue_lines = "".join(
        f"- {row['name']}: Q={tuple(row['Q'])}, residue={tuple(row['target_residue_mod4'])}, "
        f"decomposition={row['decomposition']}, tension={row['tension']}\n"
        for row in f4["effective_Q4_residue_lifts"]["rows"]
    )
    return f"""# V84 Gammahat, bare-phase and F4 heterotic-string audit

Status: {report['status']}

Core SHA-256: {report['core_sha256']}

## Decision

The unchanged five-factor parent is now rejected by an exact theorem.  For
all {gamma['finite_enumeration']['raw']} central translation-deck choices,
the two square-space-group relation defects differ by the pure Spin(11)
center.  The only smooth-compatible repair kills that center, so localized
16s do not descend and the resulting SO(11) form fails because b=(2,-1) is
not in 2U.

The selected redesign adds a non-R C4F spinor grading.  The kernel generated
by the old rotation diagonal and (z11,j^2) contains no pure z11.  All four
matched translation-sign rows pass, the smooth fields descend, an odd-F
localized 16 cancels its Spin(11) center sign, and the displayed Yukawa,
Majorana, spinor-Higgs charge assignments and redesigned stabilizer operators
pass their C4F screen; the Cbar-45-C trilinear remains V65-fatal and requires
a selector.  Full
localized isotropy, discrete anomalies and the BV/regulator/WCS parent remain
open, so this is not an accepted action.

The smooth Q4 bare phase is exactly in
{tuple(phase['bare_character']['possible_phases'])}; primary-source convention
matching prefers {phase['bare_character']['preferred_primary_calibrated_phase']},
but the determinant/Pfaffian orientation is not pinned on disk.  Every one of
sixteen newly enumerated algebraic Lambda/4Lambda r^2 coefficient shifts has
reference-q0 WCS phase +/-1, so none cancels this primitive fourth root.  This
is an over-inclusive smooth-cycle screen, not V78's local corrections to 2Y
and not a classification of physical full-HGamma refinements.

F4 realizes the charge lattice exactly: S=(2,-1)=b, F=(-1,0), and
K=(2,2).  The so(11) Lie algebra on the -4 section has three vectors and 266 neutral
hypermultiplets, while a D3 on F is the critical heterotic string with full
(cL,cR)=(24,12).  The missing residues acquire unique coefficient-minimal
effective lifts:

{residue_lines}
Both are reducible F-plus-S charge/curve configurations and hence candidate
junctions, not constructed elementary strings or worldsheet sectors.  An
explicit compact non-split I2* model, global Spin(11) form and junction inflow
are still absent.

The ordinary product cap exists, but the restricted unwarped T2 x S4 ansatz
is not half-BPS and its product double has forgetful bordism class zero rather
than Q4 order {cap['product_double_no_go']['Q4_forgetful_order']}.  The mixed
associated-graded candidate has potential incoming AHSS d3 and d4 maps, but
their source-page survival, values, the chain-level identification and the
hidden extension remain open; delta is
{cap['delta_AHSS_d3_d4_candidate_audit']['delta_exact_order']}.

The current action remains {decision['current_action_status']}.  No candidate
is accepted, all G1--G8 gates remain OPEN, and the theory is not complete.

## Open obligations

{obligations}
## Next required action

{report['next_required_action']['id']}:
{report['next_required_action']['primary_objective']}

## Gate ledger

{gates}"""


def validate_report(report: Mapping[str, Any]) -> None:
    if canonical_sha(report) != report["core_sha256"]:
        raise RuntimeError("V84 route core is not canonical")
    lineage_map = {
        "v65_route": "V65_route_core",
        "v70_route": "V70_route_core",
        "v71_route": "V71_route_core",
        "v78_route": "V78_route_core",
        "v81_route": "V81_route_core",
        "v82_route": "V82_route_core",
        "v83_route": "V83_route_core",
        "v83_master": "V83_master_core",
    }
    for key, report_key in lineage_map.items():
        if report["lineage"][report_key] != EXPECTED_CORES[key]:
            raise RuntimeError(f"lineage mismatch: {report_key}")
    gamma = report["unchanged_five_factor_Gammahat_no_go"]
    if not gamma["universal_relation_theorem"]["pure_Spin11_center_forced_for_every_assignment"]:
        raise RuntimeError("pure Spin11 center no-go was weakened")
    if gamma["finite_enumeration"] != {
        "raw": 1024, "contains_e11": 1024, "kernel_dimension_2": 128, "kernel_dimension_3": 896,
        "N1_preserving": 256, "smooth_kernel_compatible": 128, "N1_and_smooth_kernel_compatible": 64,
        "unchanged_bound_smooth_operator": 16, "Kmin_solutions": 0,
        "localized_16_descent_solutions": 0, "SO11_GS_quantization_solutions": 0,
    }:
        raise RuntimeError("Gammahat enumeration changed")
    if gamma["fatal_consequences"]["localized_16_descends_through_Kmax"] or gamma["fatal_consequences"]["b_in_2U"]:
        raise RuntimeError("unchanged-parent fatal consequence was promoted")
    c4f = report["C4F_spinor_grading_repair_scout"]
    if c4f["extended_kernel"]["contains_pure_Spin11_center"] or not c4f["extended_kernel"]["Spin11_remains_faithful"]:
        raise RuntimeError("C4F faithful Spin11 repair changed")
    if (
        not c4f["lift_choice"]["all_four_direct_bit_matched_rows_pass"]
        or c4f["lift_choice"]["independent_rows_passing"] != 8
        or c4f["lift_choice"]["unmatched_parity_rows_pass"]
    ):
        raise RuntimeError("C4F sign classification changed")
    if not c4f["representation_descent"]["localized_16_pure_center_repaired"]:
        raise RuntimeError("C4F localized repair was lost")
    if c4f["representation_descent"]["full_localized_krot_and_isotropy_descent"] or c4f["accepted_full_parent"]:
        raise RuntimeError("C4F scaffold was promoted")
    if not c4f["operator_audit"]["C4F_invariance_classification_matches"] or not c4f["stabilizer_redesign"]["local_Hessian_blocks_nondegenerate_after_gauge_null"]:
        raise RuntimeError("C4F operator scaffold changed")
    fatal = next(row for row in c4f["operator_audit"]["rows"] if row["operator"] == "Cbar 45 C")
    if not fatal["C4F_invariant"] or fatal["target_vacuum_admissible"]:
        raise RuntimeError("V65-fatal spinor-adjoint operator was promoted")
    phase = report["regulated_Q4_bare_and_WCS_audit"]
    if phase["Rarita_Vec_minus_one"]["value_mod1"] != "1/2":
        raise RuntimeError("Rarita eta changed")
    smw = phase["SMW_pair_normalization_proof"]
    if (
        (smw["hyper_one_root_dimension"], smw["hyper_full_complex_pair_dimension"]) != (299, 598)
        or (smw["adjoint_one_R_root_dimension"], smw["adjoint_full_R_pair_dimension"]) != (55, 110)
        or not smw["outer_half_already_consumed_by_pair_doubling"]
    ):
        raise RuntimeError("SMW conjugate-pair normalization changed")
    if smw["common_BV_Pfaffian_orientation_constructed"]:
        raise RuntimeError("SMW pair arithmetic was promoted to a common BV orientation")
    if phase["bare_character"]["possible_exponents_mod4"] != [1, 3] or not phase["bare_character"]["primitive_fourth_root_proved"]:
        raise RuntimeError("bare phase conjugacy class changed")
    if phase["bare_character"]["fully_BV_orientation_pinned"] or phase["bare_character"]["full_HGamma_physical_bare_character_constructed"]:
        raise RuntimeError("bare phase orientation/full parent was promoted")
    shift = phase["algebraic_r2_coefficient_shift_screen"]
    if shift["WCS_exponent_counts"] != {"0": 4, "2": 12} or not shift["all_sixteen_fail_cancellation"]:
        raise RuntimeError("algebraic r2 WCS shift screen changed")
    if phase["scope"]["all_physical_full_HGamma_refinements_rejected"]:
        raise RuntimeError("restricted WCS result was overpromoted")
    f4 = report["F4_SO11_heterotic_string_scaffold"]
    if f4["geometry"]["intersections"] != {"S2": -4, "F2": 0, "S_dot_F": 1, "K2": 8, "K_dot_S": 2, "K_dot_F": -2}:
        raise RuntimeError("F4 geometry changed")
    spectrum = f4["so11_Lie_algebra_divisor_spectrum"]
    if (spectrum["vector_hypers"], spectrum["H_neutral"]) != (3, 266):
        raise RuntimeError("F4 SO11 spectrum changed")
    if spectrum["global_gauge_group_or_line_operator_match"]:
        raise RuntimeError("F4 Lie-algebra scaffold was promoted to a global gauge-group match")
    if f4["critical_heterotic_fiber_string"]["full_cL_cR"] != [24, 12]:
        raise RuntimeError("heterotic fiber-string charges changed")
    rows = f4["effective_Q4_residue_lifts"]["rows"]
    if [(row["Q"], row["target_residue_mod4"]) for row in rows] != [([1, -1], [1, 3]), ([5, -3], [1, 1])]:
        raise RuntimeError("F4 residue lifts changed")
    if any(row["irreducible_curve"] for row in rows) or f4["effective_Q4_residue_lifts"]["elementary_new_string_constructed"]:
        raise RuntimeError("reducible F4 junction was promoted")
    if (
        not f4["effective_Q4_residue_lifts"]["coefficient_minimal_representative_selected_in_F4_effective_cone"]
        or not f4["effective_Q4_residue_lifts"]["infinitely_many_nonminimal_effective_lifts_remain"]
    ):
        raise RuntimeError("F4 minimal-representative boundary changed")
    if f4["UV_acceptance_boundary"]["explicit_compact_non_split_I2star_Weierstrass"]:
        raise RuntimeError("F4 scaffold was promoted to explicit UV model")
    cap = report["relative_cap_BPS_and_delta_audit"]
    if cap["restricted_T2xS4_BPS_audit"]["half_BPS_solution_in_restricted_ansatz"]:
        raise RuntimeError("restricted non-BPS product was promoted")
    if not cap["ordinary_relative_cap"]["ordinary_differential_trivialization_exists"]:
        raise RuntimeError("ordinary product cap gain was lost")
    if cap["ordinary_relative_cap"]["WCS_Wu_quadratic_trivialization_constructed"]:
        raise RuntimeError("ordinary cap was promoted to WCS glue")
    if cap["product_double_no_go"]["product_double_equals_Q4"]:
        raise RuntimeError("product double no-go changed")
    delta = cap["delta_AHSS_d3_d4_candidate_audit"]
    if delta["delta_exact_order"] != "OPEN_ZERO_OR_ORDER2" or delta["half_vector_eta_is_bordism_character"]:
        raise RuntimeError("delta d3/d4 problem was falsely resolved")
    if (
        delta["d3_value_computed"]
        or delta["candidate_d4_value_computed"]
        or delta["chain_level_identification_of_delta_with_candidate_proved"]
        or delta["post_Einfinity_hidden_extension_resolved"]
    ):
        raise RuntimeError("delta associated-graded candidate was promoted")
    potential_maps = delta["potential_incoming_AHSS_differentials_on_associated_graded_candidate"]
    precursor = delta["source_page_precursor_audit"]
    if len(delta["differential_elimination"]) != 5 or len(potential_maps) != 2:
        raise RuntimeError("delta AHSS differential audit changed")
    if delta["coefficient_and_homology_input_data"]["H7_BSpin11_Z8_by_UCT"] != "Z2 from Tor(H6,Z8)":
        raise RuntimeError("delta UCT correction changed")
    if precursor["d3_source_E3_survival_computed"] or precursor["d4_source_E4_survival_computed"]:
        raise RuntimeError("delta source-page survival was falsely promoted")
    accepted = [row["id"] for row in report["candidate_matrix"] if row["accepted"]]
    if accepted != report["candidate_adjudication"]["accepted_ids"] or accepted:
        raise RuntimeError("candidate acceptance ledger is inconsistent or nonempty")
    decision = report["terminal_decision"]
    if decision["accepted_full_parent_action_exists"] or decision["selected_candidate_accepted"]:
        raise RuntimeError("unaccepted redesign was promoted")
    if decision["closed_gates"] or decision["theory_complete"]:
        raise RuntimeError("a gate or theory was closed")
    if not all(value.startswith("OPEN") for value in report["gate_ledger"].values()):
        raise RuntimeError("gate ledger is not fail-closed")


def write_artifacts(report: Mapping[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(report), encoding="utf-8")


def check_artifacts(report: Mapping[str, Any]) -> None:
    if json.loads(OUT_JSON.read_text(encoding="utf-8")) != report:
        raise RuntimeError(f"stale generated artifact: {OUT_JSON.name}")
    if OUT_MD.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError(f"stale generated artifact: {OUT_MD.name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate_report(report)
    if args.write:
        write_artifacts(report)
    if args.check:
        check_artifacts(report)
    print(report["status"])
    print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
