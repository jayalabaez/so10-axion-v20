#!/usr/bin/env python3
"""Executable V54 reconstruction of the anomalous-U(1)_A low-index blueprint.

This audit does not import a literature claim as a completed repository theory.
It reconstructs the k=5 charge/parity ledger, the all-order holomorphic protection
argument, the published doublet/triplet matrix pattern, anomaly arithmetic, and
the one-loop Spin(10) inventory.  Missing full-field Hessian, GS-modulus,
flavour, threshold, and Wilson calculations remain explicitly fail-closed.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping

import sympy as sp


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V54_ANOMALOUS_U1A_BLUEPRINT_AUDIT.json"
MD_PATH = ROOT / "SUSY_V54_ANOMALOUS_U1A_BLUEPRINT_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v54_anomalous_u1a_blueprint_audit.py"
UPSTREAM = ROOT / "SUSY_V53_THEORY_COMPLETION_VERIFICATION_AUDIT.json"
EXPECTED_UPSTREAM_CORE = "620525de6b9a6ed2a63fe7e734caa18239dc26b4ef3e36b8eadbd4259d9e3cde"

STATUS = (
    "V54_ANOMALOUS_U1A_LOW_INDEX_BLUEPRINT__K5_CHARGE_AND_Z2_LEDGER_EXACT__"
    "ALL_ORDER_VACUUM_ACTIVE_HIGGS_MASS_ZERO_RECONSTRUCTED__DEGREE6_H2BARC4_"
    "OPERATOR_EXISTS_BUT_CANONICAL_VEV_COMPONENT_VANISHES__DOUBLETRANK3_"
    "TRIPLETRANK4_EXACT__VISIBLE_SPIN10_SUMT24_B0__GS_AND_FI_ASSUMED__"
    "PUBLISHED_FI_AND_Q4_CHARGE_BRANCHES_INCOMPATIBLE__MIXED_FAMILY_PROTON_"
    "CLASS_REQUIRES_UNAUDITED_Q4_COMPLETION__FULL179_"
    "HESSIAN_MATCHING_AND_FLAVOUR_OPEN__SELECTED_V54_BLUEPRINT_NOT_COMPLETE_THEORY"
)

FIELDS = ("A", "H", "Hp", "C", "barC", "Z", "S", "Cp", "barCp", "F12", "F3")


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def load_upstream() -> dict[str, Any]:
    value = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    if value.get("core_sha256") != canonical_sha(value):
        raise RuntimeError("stale V53 master core")
    if value["core_sha256"] != EXPECTED_UPSTREAM_CORE:
        raise RuntimeError("unexpected V53 master core")
    return value


def charges(k: int = 5) -> dict[str, Fraction]:
    # The first-two-family value below is the FI-trace benchmark stated with
    # the published Tr Q example.  The later Q4 flavour construction instead
    # uses -1/2-3/k; both branches are recorded explicitly in the report.
    return {
        "A": Fraction(0),
        "H": Fraction(1),
        "Hp": Fraction(-1),
        "C": Fraction(k + 4, 2 * k),
        "barC": Fraction(-1, 2),
        "Z": Fraction(2, k),
        "S": Fraction(2, k),
        "Cp": Fraction(k - 4, 2 * k),
        "barCp": Fraction(-(k + 8), 2 * k),
        "F12": Fraction(-1, 2) + Fraction(3, k),
        "F3": Fraction(-1, 2),
    }


def flavour_extension_charges(k: int = 5) -> dict[str, Fraction]:
    return {
        "F12": Fraction(-1, 2) - Fraction(3, k),
        "F3": Fraction(-1, 2),
        "X_Q4_doublet": Fraction(3, k),
        "Y_Q4_doublet": Fraction(7, k),
    }


def parities() -> dict[str, int | None]:
    return {
        "A": 1,
        "H": 0,
        "Hp": 1,
        "C": 0,
        "barC": 0,
        "Z": 1,
        "S": 0,
        "Cp": 0,
        "barCp": 0,
        # Table 1 denotes these P_1,2 and explicitly leaves them unspecified.
        "F12": None,
        "F3": 0,
    }


def term_ledger() -> list[dict[str, Any]]:
    q = charges()
    z2 = parities()
    terms = {
        "A2": {"A": 2},
        "A4": {"A": 4},
        "C_Z_A_barCp": {"C": 1, "Z": 1, "A": 1, "barCp": 1},
        "C_CbarC_barCp": {"C": 2, "barC": 1, "barCp": 1},
        "C_S_barCp": {"C": 1, "S": 1, "barCp": 1},
        "Cp_Z_A_barC": {"Cp": 1, "Z": 1, "A": 1, "barC": 1},
        "Cp_CbarC_barC": {"Cp": 1, "C": 1, "barC": 2},
        "Cp_S_barC": {"Cp": 1, "S": 1, "barC": 1},
        "H_A_Hp": {"H": 1, "A": 1, "Hp": 1},
        "S_Z4_Hp2": {"S": 1, "Z": 4, "Hp": 2},
        "S_Z2_Cp_barCp": {"S": 1, "Z": 2, "Cp": 1, "barCp": 1},
        "H_barC2": {"H": 1, "barC": 2},
        "A_Hp_C_Cp": {"A": 1, "Hp": 1, "C": 1, "Cp": 1},
        "F3_F3_H": {"F3": 2, "H": 1},
    }
    rows = []
    for name, powers in terms.items():
        total_q = sum(q[field] * power for field, power in powers.items())
        total_z2 = sum(z2[field] * power for field, power in powers.items()) % 2
        rows.append(
            {
                "term": name,
                "powers": powers,
                "U1A_charge": str(total_q),
                "Z2_parity": total_z2,
                "allowed": total_q == 0 and total_z2 == 0,
            }
        )
    return rows


def dt_matrices() -> dict[str, Any]:
    # Structural matrix of Babu-Pati-Tavartkiladze plus an exact unit witness.
    a, c, mhp, y1, y2, y, mcp = sp.symbols(
        "a c M_Hp Y1 Y2 Y M_Cp", nonzero=True
    )

    def block(eta: int, kappa: int) -> sp.Matrix:
        return sp.Matrix(
            [
                [0, eta * a, c, 0],
                [-eta * a, mhp, 0, 0],
                [0, 0, 0, kappa * y1],
                [0, y, kappa * y2, mcp],
            ]
        )

    doublet_symbolic = block(eta=0, kappa=3)
    triplet_symbolic = block(eta=1, kappa=2)
    unit_substitution = {symbol: sp.Integer(1) for symbol in (a, c, mhp, y1, y2, y, mcp)}
    doublet = doublet_symbolic.subs(unit_substitution)
    triplet = triplet_symbolic.subs(unit_substitution)
    doublet_rank_minor = -3 * c * mhp * y1
    triplet_determinant = sp.factor(triplet_symbolic.det())
    displayed_triplet_formula = 2 * y1 * a * (y * c - 2 * y2 * a)
    return {
        "ordering": ["H", "Hp", "C_or_barC", "Cp_or_barCp"],
        "unit_witness": {
            "a": 1,
            "c": 1,
            "M_Hp": 1,
            "Y1": 1,
            "Y2": 1,
            "Y": 1,
            "M_Cp": 1,
        },
        "doublet_matrix": [list(map(int, row)) for row in doublet.tolist()],
        "doublet_rank": int(doublet.rank()),
        "doublet_nullity": 4 - int(doublet.rank()),
        "doublet_right_nullspace": [
            [str(entry) for entry in vector] for vector in doublet.nullspace()
        ],
        "triplet_matrix": [list(map(int, row)) for row in triplet.tolist()],
        "triplet_rank": int(triplet.rank()),
        "triplet_nullity": 4 - int(triplet.rank()),
        "triplet_determinant": str(triplet.det()),
        "symbolic_doublet_determinant": str(sp.factor(doublet_symbolic.det())),
        "symbolic_doublet_rank3_minor": str(doublet_rank_minor),
        "symbolic_triplet_determinant": "2*Y1*a*(Y*c-2*Y2*a)",
        "symbolic_triplet_formula_verified": sp.simplify(
            triplet_determinant - displayed_triplet_formula
        )
        == 0,
        "rank_split_conditions": {
            "Clebsches": "eta_D=0, eta_T=1, kappa_D=3, kappa_T=2",
            "doublet_rank3_sufficient": "c*M_Hp*Y1 != 0",
            "triplet_rank4_necessary_and_sufficient": (
                "a*Y1*(c*Y-2*a*Y2) != 0 at eta_T=1, kappa_T=2"
            ),
        },
        "coefficient_equality_required": False,
    }


def all_order_higgs_protection() -> dict[str, Any]:
    q = charges()
    vev_invariant_charge = q["Z"]  # S, Z, and C barC all carry 2/k.
    assert q["S"] == vev_invariant_charge
    assert q["C"] + q["barC"] == vev_invariant_charge
    rows = []
    for insertions in range(0, 13):
        total = 2 * q["H"] + insertions * vev_invariant_charge
        rows.append(
            {
                "positive_VEV_invariant_insertions": insertions,
                "charge": str(total),
                "neutral": total == 0,
            }
        )
    return {
        "H_squared_charge": str(2 * q["H"]),
        "effective_VEV_singlet_generators": {
            "Z": str(q["Z"]),
            "S": str(q["S"]),
            "CbarC": str(q["C"] + q["barC"]),
        },
        "A_charge": str(q["A"]),
        "A_is_Z2_odd": parities()["A"] == 1,
        "bounded_rows": rows,
        "operator_level_stress_test": {
            "operator": "(H_m barC Gamma^m barC)^2",
            "schematic_class": "H^2 barC^4",
            "total_degree": 6,
            "U1A_charge": str(2 * q["H"] + 4 * q["barC"]),
            "Z2_parity": (2 * parities()["H"] + 4 * parities()["barC"]) % 2,
            "symmetry_allowed": 2 * q["H"] + 4 * q["barC"] == 0,
            "canonical_HuHd_mass_component": "absent",
            "component_reason": (
                "On the canonical SU(5)-singlet spinor vacuum, each barC VEV is the "
                "1_(+5) component while H contains 5_(+2)+bar5_(-2).  Four such VEVs "
                "carry U(1)_chi weight +20 whereas Hu Hd carries weight zero, so an "
                "SO(10)-invariant Hu Hd <barC>^4 component cannot occur."
            ),
        },
        "all_n_algebra": {
            "formula": "Q[Hu Hd dressing]=2+(2/5)*(n_CbarC+n_S+n_Z)",
            "domain": "n_CbarC,n_S,n_Z are arbitrary nonnegative integers",
            "spinor_weight_constraint": (
                "a nonzero Hu Hd insertion on the canonical SU(5)-singlet spinor vacuum "
                "has equal numbers of C_(1,-5) and barC_(1,+5) VEVs"
            ),
            "strictly_positive_for_all_n": (
                2 * q["H"] > 0 and vev_invariant_charge > 0
            ),
        },
        "all_order_argument": (
            "This is a statement about vacuum-active Hu Hd mass insertions, not the absence "
            "of every abstract H^2 operator.  A nonzero spinor-VEV monomial relevant to "
            "Hu Hd has equal C and barC counts and therefore is generated by nonnegative "
            "powers of charge +2/5 CbarC, together with S and Z. Neutral A cannot change "
            "that positive charge; Z2 only correlates the parity of A and Z insertions. "
            "H-Hp mixing at zero U1A charge requires an odd A insertion, whose odd power "
            "has the zero DW doublet Clebsch. The symmetry-allowed H^2 barC^4 stress test "
            "is recorded separately and has no Hu Hd component on the canonical singlet vacuum."
        ),
        "abstract_H_squared_operators_forbidden_to_all_orders": False,
        "vacuum_active_HuHd_mass_forbidden_to_all_holomorphic_orders": (
            2 * q["H"] > 0 and vev_invariant_charge > 0
        ),
    }


def proton_dressing_screen() -> dict[str, Any]:
    q = charges()
    flavour = flavour_extension_charges()
    dressing_species = {
        "Z_or_S_or_CbarC": q["Z"],
        "X_Q4_doublet": flavour["X_Q4_doublet"],
        "Y_Q4_doublet": flavour["Y_Q4_doublet"],
    }
    rows = []
    for n_third in range(5):
        n_light = 4 - n_third
        bare = n_light * flavour["F12"] + n_third * flavour["F3"]
        candidates = []
        for common, x_count, y_count in itertools.product(range(13), repeat=3):
            total = (
                bare
                + common * dressing_species["Z_or_S_or_CbarC"]
                + x_count * dressing_species["X_Q4_doublet"]
                + y_count * dressing_species["Y_Q4_doublet"]
            )
            if total == 0:
                candidates.append((common + x_count + y_count, common, x_count, y_count))
        first = min(candidates) if candidates else None
        rows.append(
            {
                "light_family_spinors": n_light,
                "third_family_spinors": n_third,
                "bare_U1A_charge": str(bare),
                "minimum_positive_VEV_dressings": None if first is None else first[0],
                "witness": None
                if first is None
                else {
                    "Z_or_S_or_CbarC": first[1],
                    "X_Q4_doublet": first[2],
                    "Y_Q4_doublet": first[3],
                },
                "total_degree_if_Q4_allows_contraction": None
                if first is None
                else 4 + first[0],
            }
        )
    return {
        "scope": (
            "U1A-charge-only screen for the later Q4 flavour-charge branch. The published "
            "P1,2 Z2 parities are unspecified here, and X/Y parities are not reconstructed. "
            "Whether the displayed flavon dressings have even Z2 parity, contain the required "
            "Q4 singlet, and possess a mediator completion is not decided in this audit."
        ),
        "FI_trace_benchmark_F12_charge": str(q["F12"]),
        "later_Q4_flavour_charges": {
            name: str(value) for name, value in flavour.items()
        },
        "branch_mismatch_exposed": q["F12"] != flavour["F12"],
        "Z2_and_Q4_tensor_census_complete": False,
        "rows": rows,
        "lowest_degree_charge_neutral_candidate": min(
            (row for row in rows if row["minimum_positive_VEV_dressings"] is not None),
            key=lambda row: row["total_degree_if_Q4_allows_contraction"],
        ),
        "decision": (
            "The later flavour-charge branch admits charge-neutral F^4 flavon dressings as "
            "early as degree six. Only the unconstructed Q4 tensor contraction can decide "
            "whether they exist. G7 remains open until the Q4 family action and Wilson "
            "matching are explicit."
        ),
    }


def anomaly_ledger() -> dict[str, Any]:
    q = charges()
    dimensions = {
        "A": 45,
        "H": 10,
        "Hp": 10,
        "C": 16,
        "barC": 16,
        "Z": 1,
        "S": 1,
        "Cp": 16,
        "barCp": 16,
        "F12": 32,
        "F3": 16,
    }
    indices = {
        "A": Fraction(8),
        "H": Fraction(1),
        "Hp": Fraction(1),
        "C": Fraction(2),
        "barC": Fraction(2),
        "Z": Fraction(0),
        "S": Fraction(0),
        "Cp": Fraction(2),
        "barCp": Fraction(2),
        "F12": Fraction(4),
        "F3": Fraction(2),
    }
    trace = sum(Fraction(dimensions[field]) * q[field] for field in FIELDS)
    cubic = sum(Fraction(dimensions[field]) * q[field] ** 3 for field in FIELDS)
    mixed = sum(indices[field] * q[field] for field in FIELDS)
    flavour = flavour_extension_charges()
    later_without_flavons_trace = (
        trace
        - Fraction(dimensions["F12"]) * q["F12"]
        + Fraction(dimensions["F12"]) * flavour["F12"]
    )
    later_without_flavons_mixed = (
        mixed
        - indices["F12"] * q["F12"]
        + indices["F12"] * flavour["F12"]
    )
    q4_flavon_trace = (
        2 * flavour["X_Q4_doublet"] + 2 * flavour["Y_Q4_doublet"]
    )
    return {
        "normalization": "T10=1, T16=2, T45=8",
        "FI_trace_benchmark_F12_charge": str(q["F12"]),
        "later_Q4_flavour_F12_charge": str(flavour_extension_charges()["F12"]),
        "charge_branch_scope": (
            "Tr Q reproduces the stated FI-trace benchmark q1,2=-1/2+3/k. The later "
            "Q4 Yukawa operator list uses q(F12)=-1/2-3/k and requires a separate full anomaly ledger."
        ),
        "Tr_Q": str(trace),
        "Tr_Q_expected_for_k5": "-84/5",
        "Tr_Q_cubed_visible": str(cubic),
        "SO10_squared_U1A": str(mixed),
        "later_Q4_branch_partial_ledger": {
            "scope": (
                "replace the two-family charge by -11/10; first exclude and then include "
                "the two-component X and Y flavons, but no other singlets or mediators"
            ),
            "Tr_Q_before_XY": str(later_without_flavons_trace),
            "SO10_squared_U1A_before_XY": str(later_without_flavons_mixed),
            "XY_trace_contribution": str(q4_flavon_trace),
            "Tr_Q_after_XY": str(later_without_flavons_trace + q4_flavon_trace),
            "ordinary_anomaly_free_after_XY": False,
        },
        "ordinary_anomaly_free": trace == 0 and cubic == 0 and mixed == 0,
        "required_completion": (
            "a Green-Schwarz axion/modulus and any additional string-scale singlets must be "
            "specified separately for the FI-trace and later Q4 charge branches; the cited "
            "model explicitly treats U1A as anomalous"
        ),
    }


def perturbativity() -> dict[str, Any]:
    source_higgs_t = 8 + 2 * 1 + 4 * 2
    family_t = 3 * 2
    total_t = source_higgs_t + family_t
    b_landau = total_t - 3 * 8
    return {
        "Higgs_T": source_higgs_t,
        "three_families_T": family_t,
        "total_T": total_t,
        "Spin10_one_loop_b_Landau": b_landau,
        "one_loop_behavior": "zero visible Spin(10) coefficient before flavour messengers",
        "pole_ratio": None,
        "scope": (
            "Q4 flavour messengers, GS/string states, SUSY thresholds, and two-loop running "
            "are not included"
        ),
    }


def build_report() -> dict[str, Any]:
    upstream = load_upstream()
    q = charges()
    terms = term_ledger()
    dt = dt_matrices()
    protection = all_order_higgs_protection()
    proton = proton_dressing_screen()
    anomalies = anomaly_ledger()
    running = perturbativity()

    integrity = {
        "V53_master_is_bound": upstream["core_sha256"] == EXPECTED_UPSTREAM_CORE,
        "all_declared_blueprint_terms_are_U1A_and_Z2_invariant": all(
            row["allowed"] for row in terms
        ),
        "k5_charges_are_exact": q
        == {
            "A": Fraction(0),
            "H": Fraction(1),
            "Hp": Fraction(-1),
            "C": Fraction(9, 10),
            "barC": Fraction(-1, 2),
            "Z": Fraction(2, 5),
            "S": Fraction(2, 5),
            "Cp": Fraction(1, 10),
            "barCp": Fraction(-13, 10),
            "F12": Fraction(1, 10),
            "F3": Fraction(-1, 2),
        },
        "doublet_rank3_triplet_rank4": (
            dt["doublet_rank"] == 3
            and dt["doublet_nullity"] == 1
            and dt["triplet_rank"] == 4
            and dt["triplet_nullity"] == 0
        ),
        "symbolic_DT_open_set_is_recorded": (
            dt["symbolic_doublet_determinant"] == "0"
            and dt["symbolic_triplet_formula_verified"]
        ),
        "vacuum_active_HuHd_zero_is_all_order_in_reconstructed_semigroup": protection[
            "vacuum_active_HuHd_mass_forbidden_to_all_holomorphic_orders"
        ],
        "abstract_H2_operator_is_not_overclaimed_absent": (
            not protection["abstract_H_squared_operators_forbidden_to_all_orders"]
            and protection["operator_level_stress_test"]["symmetry_allowed"]
            and protection["operator_level_stress_test"]["canonical_HuHd_mass_component"]
            == "absent"
        ),
        "published_visible_trace_is_reproduced": anomalies["Tr_Q"] == "-84/5",
        "visible_Spin10_one_loop_b_is_zero": running["Spin10_one_loop_b_Landau"] == 0,
        "published_family_charge_branches_are_not_silently_merged": proton[
            "branch_mismatch_exposed"
        ],
        "unspecified_F12_Z2_parity_is_not_invented": parities()["F12"] is None,
        "charge_neutral_flavon_dressed_proton_class_needs_Q4_test": proton[
            "lowest_degree_charge_neutral_candidate"
        ]["total_degree_if_Q4_allows_contraction"]
        == 6,
        "full_Hessian_is_not_claimed": True,
        "no_gate_is_promoted": True,
    }

    report: dict[str, Any] = {
        "schema": "susy-v54-anomalous-u1a-blueprint-audit-v1",
        "status": STATUS,
        "upstream": {"path": UPSTREAM.name, "core_sha256": upstream["core_sha256"]},
        "candidate": {
            "id": "V54_BPT_STYLE_ANOMALOUS_U1A_K5",
            "object_type": "selected architecture family, not yet one same-action charge assignment",
            "gauge_and_shaping": "Spin(10) x anomalous U(1)A x Z2, with Q4 required for flavour",
            "visible_fields": {
                "Higgs": "A45 + H10 + Hp10 + C16 + barCbar16 + Cp16 + barCpbar16 + S + Z",
                "matter": "two light-family 16s plus third-family 16",
            },
            "visible_complex_coordinates": 45 + 2 * 10 + 4 * 16 + 2 + 3 * 16,
            "elementary_renormalizable": False,
            "cutoff_EFT": True,
            "one_same_action_charge_ledger": False,
            "reason_selected": (
                "It changes the failed V53 topology, protects the vacuum-active Hu Hd mass "
                "on the canonical singlet vacuum, and has the smallest Spin(10) index among "
                "the serious V54 branches. DW alignment and a unified FI/Q4 charge branch "
                "still require a complete same-action proof."
            ),
        },
        "U1A_charges": {field: str(value) for field, value in q.items()},
        "Q4_flavour_extension_charges": {
            field: str(value) for field, value in flavour_extension_charges().items()
        },
        "Z2_parities": parities(),
        "required_term_ledger": terms,
        "all_order_DT_protection": protection,
        "exact_DT_mass_matrices": dt,
        "proton_operator_screen": proton,
        "anomaly_and_FI_scope": anomalies,
        "perturbativity": running,
        "same_action_open_items": [
            "choose one compatible FI/anomaly/Q4 charge branch rather than combine the published +1/10 and -11/10 first-two-family assignments",
            "differentiate the complete nonrenormalizable action and prove the 179-coordinate visible Hessian kernel equals 34 broken Spin10 x U1A directions plus 45 light matter components and four weak-Higgs components, with the three right-neutrino directions treated by the same Q4 seesaw action",
            "supply and stabilize the Green-Schwarz modulus and reproduce the FI term in the same Kähler/gauge action",
            "make the Q4 family sector, its flavon vacuum and all mediator fields explicit, then repeat the proton census",
            "reproduce and update the paper's threshold spectrum and one-loop matching inside this repository rather than use only structural 4x4 ranks",
            "fit charged fermions and neutrinos with uncertainties and reserve a withheld observable",
            "reproduce the paper's d=5 and d=6 analysis with an explicit same-action Wilson array and current inputs/lifetimes",
            "add SUSY breaking, mu/Bmu, radiative EWSB, global vacuum and cosmology",
        ],
        "gate_effect": {
            "G1": "OPEN_GS_MODULUS_AND_GLOBAL_QUOTIENT",
            "G2": "OPEN_FULL_SAME_ACTION_HESSIAN_AND_C1_C7",
            "G3": "OPEN_FULL_VACUUM_HESSIAN",
            "G4": "PARTIAL_ALL_ORDER_DT_AND_EXACT_REDUCED_RANKS",
            "G5": "OPEN",
            "G6": "PARTIAL_B0_VISIBLE_ONE_LOOP_ONLY",
            "G7": "OPEN_Q4_AND_WILSON_MATCHING",
            "G8": "OPEN_INCOMPATIBLE_CHARGE_BRANCH_AND_MODERN_FLAVOUR_REFIT",
            "promotions": [],
        },
        "verdict": {
            "selected_V54_blueprint": True,
            "complete_theory": False,
            "empirical_discovery": False,
            "statement": (
                "This V54 architecture family evades the structural V53 filter-driver "
                "obstruction for the reconstructed canonical-vacuum Higgs-mass semigroup. The "
                "symmetry does allow an abstract degree-six H^2 barC^4 contraction, whose "
                "canonical Hu Hd VEV component is absent by SU(5) x U(1)_chi weight. This is "
                "a saved, falsifiable architecture blueprint, not one completed candidate "
                "action, because the published FI and Q4 family charges are incompatible and "
                "its complete tensor census, full Hessian, GS sector, matching, flavour and "
                "observables remain unconstructed."
            ),
        },
        "primary_sources": [
            {
                "title": "Constraining Proton Lifetime in SO(10) with Stabilized Doublet-Triplet Splitting",
                "url": "https://arxiv.org/abs/1003.2625",
            },
            {
                "title": "A Complete Supersymmetric SO(10) Model",
                "url": "https://arxiv.org/abs/hep-ph/9501298",
            },
        ],
        "integrity_checks": integrity,
        "n_failed_integrity_checks": sum(not value for value in integrity.values()),
        "source_manifest": [
            {"path": Path(__file__).name, "sha256": sha256_file(Path(__file__))},
            {"path": TEST_PATH.name, "sha256": sha256_file(TEST_PATH)},
            {"path": UPSTREAM.name, "sha256": sha256_file(UPSTREAM)},
        ],
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report["status"] != STATUS or report["core_sha256"] != canonical_sha(report):
        raise RuntimeError("status or core drift")
    if report["n_failed_integrity_checks"] or not all(report["integrity_checks"].values()):
        raise RuntimeError("integrity failure")
    if report["verdict"]["complete_theory"] or report["gate_effect"]["promotions"]:
        raise RuntimeError("blueprint overpromoted")


def render_markdown(report: Mapping[str, Any]) -> str:
    dt = report["exact_DT_mass_matrices"]
    run = report["perturbativity"]
    anomaly = report["anomaly_and_FI_scope"]
    proton = report["proton_operator_screen"]["lowest_degree_charge_neutral_candidate"]
    return f"""# V54 anomalous-U(1)A low-index blueprint audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Outcome

{report['verdict']['statement']}

The selected architecture family changes the V53 action to `A45 + H10 + H'10 +
2(16+bar16) + S + Z`, supplemented by anomalous `U(1)A x Z2` and a still
required Q4 family sector. At `k=5`, every displayed Higgs/source term and the
third-family Yukawa term has exactly zero U(1)A charge and even Z2 parity. The
paper leaves the first-two-family Z2 parities unspecified.

## Exact advances

- The reconstructed doublet matrix has rank `{dt['doublet_rank']}` and nullity
  `{dt['doublet_nullity']}`; the triplet matrix has rank `{dt['triplet_rank']}`
  and determinant `{dt['triplet_determinant']}` at an exact unit witness. The
  symbolic triplet determinant is `{dt['symbolic_triplet_determinant']}`, so the
  rank-four statement includes its non-cancellation condition.
- `H^2` has U(1)A charge `+2`. Every reconstructed *vacuum-active* Hu-Hd
  dressing generator has charge `+2/5`, while neutral `A` is Z2 odd. Therefore
  no such dressing generates a Hu-Hd mass at any holomorphic order, and odd-A
  mixing has the zero DW doublet Clebsch.
- This does **not** mean every abstract `H^2` operator is absent. The symmetry
  permits `(H_m barC Gamma^m barC)^2 ~ H^2 barC^4` at degree six. Its Hu-Hd
  component with four canonical singlet `barC` VEVs is absent by the displayed
  SU(5) x U(1)-chi weight test. A complete SO(10) tensor census remains open.
- The visible Spin(10) inventory has `sum T={run['total_T']}` and one-loop
  `b_L={run['Spin10_one_loop_b_Landau']}` before Q4/GS states.
- The visible charge trace is `{anomaly['Tr_Q']}`, reproducing the anomalous-FI
  example rather than pretending the U(1) is ordinarily anomaly free. The later
  Q4 branch instead has partial trace
  `{anomaly['later_Q4_branch_partial_ledger']['Tr_Q_after_XY']}` after X/Y and
  still requires its own GS/singlet completion.

## Fail-closed boundary

The published FI-trace example and later Q4 flavour list use different
first-two-family charge branches.  In the later flavour branch, U1A charge alone
permits an `F^4` flavon dressing at total degree
`{proton['total_degree_if_Q4_allows_contraction']}`; only a complete Q4 tensor
census **and** the unspecified Z2 parities can decide whether the contraction
exists. The complete 179-coordinate Hessian (including 45 intended light-matter
directions rather than only gauge and Higgs directions),
Green-Schwarz modulus, thresholds, Wilson coefficients, flavour likelihood,
soft vacuum, EWSB and cosmology are also absent from this executable repository
audit. The source paper contains historical threshold, proton-decay and soft-mu
analyses; they have not been reproduced here with a completed action and current
inputs. No G1-G8 gate is promoted.

Primary construction: https://arxiv.org/abs/1003.2625
"""


def write_artifacts() -> dict[str, Any]:
    report = build_report()
    validate(report)
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")
    return report


def check_artifacts() -> None:
    report = build_report()
    validate(report)
    if JSON_PATH.read_text(encoding="utf-8") != json.dumps(report, indent=2, sort_keys=True) + "\n":
        raise RuntimeError("stale JSON")
    if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError("stale Markdown")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        report = write_artifacts()
        print(report["status"])
        print(report["core_sha256"])
    if args.check:
        check_artifacts()
        print("V54_ANOMALOUS_U1A_BLUEPRINT_AUDIT_CHECK_PASS")
    if not args.write and not args.check:
        print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
