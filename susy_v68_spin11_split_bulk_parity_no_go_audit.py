#!/usr/bin/env python3
"""V68 fail-closed audit of the inherited Spin(11) split-bulk escape.

V67 left a precise question open: can an ordinary five-dimensional bulk
hypermultiplet furnish the q_R=2 Q/Qbar rows that remove the V64 chiral
kernel?  V68 answers that question without assuming a particular KK cutoff.

There are two independent obstructions.  First, the geometric Z4R selected in
V61 fixes both four-dimensional chiral halves of every conventional 5D hyper
to q_R=1.  An orphan-hyper bilinear therefore has charge 1, not the
superpotential charge 2, for every representation and every parity.  Second,
the common projector group is Pati-Salam, so a pure orbifold kernel is a
Pati-Salam module and can never be Q-only.

A diagonal R x hyper-number redesign can algebraically change the hyper
charges to (2,0).  It is a genuinely new action.  Its lowest 32 and 55/65
spectra contain compulsory companions, and the V67 Q-only anomaly and beta
ledgers cannot be imported.  SM-selective two-wall boundary mixing remains a
representation-level loophole, not a constructed determinant.  No gate is
closed.
"""

from __future__ import annotations

import argparse
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V68_SPIN11_SPLIT_BULK_PARITY_NO_GO_AUDIT.json"
MD_PATH = ROOT / "SUSY_V68_SPIN11_SPLIT_BULK_PARITY_NO_GO_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v68_spin11_split_bulk_parity_no_go_audit.py"

INPUTS = {
    "v59_route": ROOT / "SUSY_V59_SPIN11_GAUGE_HIGGS_COMPLETION_AUDIT.json",
    "v61_route": ROOT / "SUSY_V61_SPIN11_Z4R_SELECTOR_ESCAPE_AUDIT.json",
    "v65_route": ROOT / "SUSY_V65_SPIN11_ORPHAN_LIFTING_CLASSIFICATION_AUDIT.json",
    "v67_route": ROOT / "SUSY_V67_SPIN11_INDEX_PARTNER_6D_ESCAPE_AUDIT.json",
    "v67_master": ROOT / "SUSY_V67_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
}

EXPECTED_CORES = {
    "v59_route": "bf666eb5e4d57bff18b05182d7d6cc7874bbc26dd71897153faf9ee67a5f8c42",
    "v61_route": "6d6107dea91e18e7d34e4560ad8003cd8c38eef5c788b2ebd148bb3795b2c33a",
    "v65_route": "b87696403fb46c4a6b044be8abe58dd5f82b63a83a58fff262a6f00bdd6914ae",
    "v67_route": "5927f64eec6bc27d68b7d429eab11ee1f0efc9709041064f47baaabc25f0eebb",
    "v67_master": "328c5e0abc86b7ad72b8112d6d6fa6b7fd1d4435ce199541a6ae3d947914408c",
}

STATUS = (
    "V68_SPIN11_SPLIT_BULK_PARITY_NO_GO__V59_V61_V65_V67_CORES_BOUND__"
    "INHERITED_GEOMETRIC_Z4R_FORCES_EVERY_CONVENTIONAL_HYPER_HALF_QR1__"
    "ORPHAN_QR0_NEEDS_QR2_ROW__NEUTRAL_VEV_DRESSING_CANNOT_REPAIR_CHARGE__"
    "PURE_PARITY_KERNEL_IS_A_PATI_SALAM_MODULE_FOR_EVERY_REPRESENTATION__"
    "Q_ONLY_AND_QBAR_ONLY_PARITY_SPECTRA_IMPOSSIBLE__11_32_55_65_ENUMERATED__"
    "DIAGONAL_R_X_HYPER_FLAVOR_REDESIGN_IS_NEW_ACTION__32_HAS_20_COMPANIONS__"
    "55_AND_65_HAVE_18_COMPANIONS__V67_Q_ONLY_ANOMALY_AND_BETA_NOT_IMPORTED__"
    "TWO_WALL_SM_FILTER_REPRESENTATION_LEVEL_ONLY__FULL_KK_DETERMINANT_AND_"
    "FIXED_POINT_ANOMALIES_OPEN__INHERITED_5D_SPLIT_BULK_ROUTE_CLOSED__"
    "CURRENT_ACTION_REJECTED__G1_TO_G8_OPEN_ZERO_PROMOTIONS"
)

PRIMARY_SOURCES = [
    {
        "id": "HOSOTANI_YAMATSU_2015",
        "title": "Gauge-Higgs Grand Unification",
        "url": "https://arxiv.org/abs/1504.03817",
        "scope": (
            "Primary source for the SO(11) vector and spinor projectors, the "
            "SO(10) and SO(4)xSO(7) walls, and a 32 containing one SM family."
        ),
    },
    {
        "id": "FURUI_HOSOTANI_YAMATSU_2016",
        "title": "Toward Realistic Gauge-Higgs Grand Unification",
        "url": "https://arxiv.org/abs/1606.07222",
        "scope": (
            "Provides the explicit 5D component parity table and SO(10)-invariant "
            "brane interactions; its model is non-supersymmetric and does not "
            "establish the V61 Z4R action."
        ),
    },
    {
        "id": "HOSOTANI_YAMATSU_2018",
        "title": "Electroweak Symmetry Breaking and Mass Spectra in Six-Dimensional Gauge-Higgs Grand Unification",
        "url": "https://arxiv.org/abs/1710.04811",
        "scope": (
            "Displays the SO(11) spinor branching/parity organization and reports "
            "that the six-dimensional redesign avoids the light exotics of the "
            "authors' earlier non-supersymmetric 5D model."
        ),
    },
    {
        "id": "VON_GERSDORFF_QUIROS_2003",
        "title": "Localized anomalies in orbifold gauge theories",
        "url": "https://arxiv.org/abs/hep-th/0305024",
        "scope": (
            "Shows that integrated anomaly cancellation is weaker than fixed-point "
            "cancellation and classifies restricted Green-Schwarz/CS remedies."
        ),
    },
]


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def file_sha(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def load_bound(path: Path, expected: str, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"missing {label}: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    actual = canonical_sha(value)
    if value.get("core_sha256") != actual:
        raise RuntimeError(f"stale canonical core: {label}")
    if actual != expected:
        raise RuntimeError(f"unexpected canonical core: {label}")
    return value


def fstr(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else str(value)


def fraction_map(values: Mapping[str, Fraction]) -> dict[str, str]:
    return {key: fstr(value) for key, value in values.items()}


def add_maps(*values: Mapping[str, Fraction]) -> dict[str, Fraction]:
    keys = tuple(values[0]) if values else ()
    return {key: sum((value[key] for value in values), Fraction(0)) for key in keys}


def scale_map(value: Mapping[str, Fraction], factor: int) -> dict[str, Fraction]:
    return {key: factor * item for key, item in value.items()}


# The entries are for one left-chiral superfield.  Conjugate fields have the
# same beta and quadratic-index values, so vectorlike pairs multiply by two.
SM_FIELDS: dict[str, dict[str, Any]] = {
    "Q": {"d3": 3, "d2": 2, "Y": Fraction(1, 6)},
    "L": {"d3": 1, "d2": 2, "Y": Fraction(1, 2)},
    "U": {"d3": 3, "d2": 1, "Y": Fraction(2, 3)},
    "D": {"d3": 3, "d2": 1, "Y": Fraction(1, 3)},
    "E": {"d3": 1, "d2": 1, "Y": Fraction(1, 1)},
    "N": {"d3": 1, "d2": 1, "Y": Fraction(0, 1)},
    "X56": {"d3": 3, "d2": 2, "Y": Fraction(5, 6)},
}


def one_chiral_indices(name: str) -> dict[str, Fraction]:
    row = SM_FIELDS[name]
    d3, d2, hypercharge = row["d3"], row["d2"], row["Y"]
    return {
        "b1_GUT": Fraction(3, 5) * hypercharge * hypercharge * d3 * d2,
        "b2": Fraction(d3, 2) if d2 == 2 else Fraction(0),
        "b3": Fraction(d2, 2) if d3 == 3 else Fraction(0),
        "A2": Fraction(d3, 2) if d2 == 2 else Fraction(0),
        "A3": Fraction(d2, 2) if d3 == 3 else Fraction(0),
        "dimension": Fraction(d3 * d2),
    }


def vectorlike_indices(name: str, fermion_r: int) -> dict[str, Fraction]:
    base = one_chiral_indices(name)
    return {
        "b1_GUT": 2 * base["b1_GUT"],
        "b2": 2 * base["b2"],
        "b3": 2 * base["b3"],
        "A2": 2 * fermion_r * base["A2"],
        "A3": 2 * fermion_r * base["A3"],
        "dimension": 2 * base["dimension"],
    }


SECTOR_TABLES: dict[str, dict[str, list[str]]] = {
    "11": {
        "++": ["(2,2,1)"],
        "+-": ["(1,1,6)"],
        "-+": [],
        "--": ["(1,1,1)"],
    },
    "32": {
        "++": ["(2,1,4)"],
        "+-": ["(1,2,4bar)"],
        "-+": ["(2,1,4bar)"],
        "--": ["(1,2,4)"],
    },
    "55": {
        "++": ["(3,1,1)", "(1,3,1)", "(1,1,15)"],
        "+-": ["(2,2,6)"],
        "-+": ["(1,1,6)"],
        "--": ["(2,2,1)"],
    },
    "65": {
        "++": ["(3,3,1)", "(1,1,20prime)", "2x(1,1,1)"],
        "+-": ["(2,2,6)"],
        "-+": ["(1,1,6)"],
        "--": ["(2,2,1)"],
    },
}

REP_DIMS = {
    "(2,2,1)": 4,
    "(1,1,6)": 6,
    "(1,1,1)": 1,
    "(2,1,4)": 8,
    "(1,2,4bar)": 8,
    "(2,1,4bar)": 8,
    "(1,2,4)": 8,
    "(3,1,1)": 3,
    "(1,3,1)": 3,
    "(1,1,15)": 15,
    "(2,2,6)": 24,
    "(3,3,1)": 9,
    "(1,1,20prime)": 20,
    "2x(1,1,1)": 2,
}

CONJUGATE_REP = {
    "(2,1,4)": "(2,1,4bar)",
    "(2,1,4bar)": "(2,1,4)",
    "(1,2,4)": "(1,2,4bar)",
    "(1,2,4bar)": "(1,2,4)",
}


def sector_dimension(reps: Sequence[str]) -> int:
    return sum(REP_DIMS[rep] for rep in reps)


def conjugate_reps(reps: Sequence[str]) -> list[str]:
    return [CONJUGATE_REP.get(rep, rep) for rep in reps]


def sign_key(eta0: int, eta1: int) -> str:
    return ("+" if eta0 == 1 else "-") + ("+" if eta1 == 1 else "-")


def multiply_signatures(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    return left[0] * right[0], left[1] * right[1]


def derive_tensor_sector_counts() -> dict[str, dict[str, int]]:
    """Derive 11, antisymmetric 55 and symmetric-traceless 65 multiplicities.

    The vector has four A coordinates with (++), six B coordinates with (+-),
    and the eleventh coordinate c with (--).  Antisymmetric pairs give the 55;
    symmetric pairs including the diagonal give 66, from which the invariant
    trace in the (++) sector is removed to obtain the 65.
    """

    vectors = [(1, 1)] * 4 + [(1, -1)] * 6 + [(-1, -1)]

    def empty() -> dict[str, int]:
        return {"++": 0, "+-": 0, "-+": 0, "--": 0}

    vector_counts = empty()
    for signature in vectors:
        vector_counts[sign_key(*signature)] += 1

    antisymmetric = empty()
    for i in range(len(vectors)):
        for j in range(i + 1, len(vectors)):
            antisymmetric[sign_key(*multiply_signatures(vectors[i], vectors[j]))] += 1

    symmetric_traceless = empty()
    for i in range(len(vectors)):
        for j in range(i, len(vectors)):
            symmetric_traceless[
                sign_key(*multiply_signatures(vectors[i], vectors[j]))
            ] += 1
    symmetric_traceless["++"] -= 1
    return {"11": vector_counts, "55": antisymmetric, "65": symmetric_traceless}


def hyper_zero_sectors(rep: str, eta0: int, eta1: int) -> dict[str, Any]:
    table = SECTOR_TABLES[rep]
    h_key = sign_key(eta0, eta1)
    hc_key = sign_key(-eta0, -eta1)
    h = list(table[h_key])
    hc = conjugate_reps(table[hc_key])
    return {
        "eta": h_key,
        "H_joint_sector": h_key,
        "H_zero_reps": h,
        "H_zero_dimension": sector_dimension(h),
        "Hc_joint_sector_before_4D_conjugation": hc_key,
        "Hc_left_chiral_zero_reps": hc,
        "Hc_zero_dimension": sector_dimension(hc),
        "total_zero_dimension": sector_dimension(h) + sector_dimension(hc),
    }


def representation_and_parity_audit(v59: Mapping[str, Any]) -> dict[str, Any]:
    expected_dimensions = {"11": 11, "32": 32, "55": 55, "65": 65}
    dimension_checks = {
        rep: sum(sector_dimension(rows) for rows in table.values())
        for rep, table in SECTOR_TABLES.items()
    }
    table_sector_counts = {
        rep: {key: sector_dimension(rows) for key, rows in table.items()}
        for rep, table in SECTOR_TABLES.items()
    }
    derived_tensor_counts = derive_tensor_sector_counts()
    v59_spinor_counts = {
        sign_key(int(row["P0sp"]), int(row["P1sp"])): int(row["dimension"])
        for row in v59["spinor_mediator_parities"]["simultaneous_eigenspaces"]
    }
    spinor_scan = [
        hyper_zero_sectors("32", eta0, eta1)
        for eta0 in (1, -1)
        for eta1 in (1, -1)
    ]
    spinor_identification = {
        "++": "16 = (2,1,4) + (1,2,4bar)",
        "+-": "16 = (1,2,4bar) + (2,1,4)",
        "-+": "16bar = (2,1,4bar) + (1,2,4)",
        "--": "16bar = (1,2,4) + (2,1,4bar)",
    }
    for row in spinor_scan:
        row["4D_left_chiral_identification"] = spinor_identification[row["eta"]]

    tensor55 = hyper_zero_sectors("55", 1, -1)
    tensor65 = hyper_zero_sectors("65", 1, -1)
    sm_tensor_content = [
        "Q=(3,2,+1/6)",
        "Qbar=(3bar,2,-1/6)",
        "X56=(3,2,-5/6)",
        "X56bar=(3bar,2,+5/6)",
        "D=(3,1,-1/3)",
        "Dbar=(3bar,1,+1/3)",
    ]
    return {
        "projector_groups": {
            "y0": "Spin(10)",
            "yL": "Spin(4)xSpin(7)",
            "common_group": "Spin(4)xSpin(6) ~= SU(2)L x SU(2)R x SU(4), global quotient unresolved",
        },
        "theorem": {
            "zero_space": "Z_R=ker(eta0 P0^R-1) intersect ker(eta1 P1^R-1)",
            "proof": (
                "every common-group generator commutes with P0^R and P1^R, "
                "so Z_R is a common-group module; flavor-space parity matrices "
                "on multiple copies do not change this conclusion"
            ),
            "Q_branching": "(2,1,4) -> Q(3,2,+1/6) + L(1,2,-1/2)",
            "Qbar_branching": "(2,1,4bar) -> Qbar(3bar,2,-1/6) + Lbar(1,2,+1/2)",
            "pure_parity_Q_only_possible": False,
            "scope": (
                "all bulk representations and intrinsic/flavor parity matrices "
                "with the fixed P0/P1 walls; SM-breaking boundary mass matrices "
                "are outside the theorem"
            ),
        },
        "joint_sector_tables": copy.deepcopy(SECTOR_TABLES),
        "joint_sector_multiplicities": table_sector_counts,
        "independent_tensor_multiplicity_derivation": {
            "vector_coordinate_signatures": {"++": 4, "+-": 6, "-+": 0, "--": 1},
            "derived": derived_tensor_counts,
            "matches_11_55_65_tables": all(
                derived_tensor_counts[rep] == table_sector_counts[rep]
                for rep in ("11", "55", "65")
            ),
        },
        "V59_spinor_joint_multiplicity_binding": {
            "source_counts": v59_spinor_counts,
            "table_counts": table_sector_counts["32"],
            "matches": v59_spinor_counts == table_sector_counts["32"],
            "branching_labels_use": (
                "the primary-source convention P1=+ for SU(2)L; simultaneous "
                "16/16bar relabeling does not alter the complete-multiplet theorem"
            ),
        },
        "sector_dimension_sums": dimension_checks,
        "expected_representation_dimensions": expected_dimensions,
        "all_sector_dimensions_exact": dimension_checks == expected_dimensions,
        "fundamental_11": {
            "contains_Q_type_sector": False,
            "decision": "CLOSED_AS_Q_PARTNER_REPRESENTATION",
        },
        "spinor_32_intrinsic_scan": spinor_scan,
        "every_32_hyper_is_16_or_16bar": all(
            row["total_zero_dimension"] == 16
            and row["4D_left_chiral_identification"].startswith(("16 ", "16bar "))
            for row in spinor_scan
        ),
        "two_32s_for_Q_and_Qbar": {
            "zero_spectrum": "one 16 plus one 16bar",
            "desired_Q_Qbar_complex_components": 12,
            "compulsory_other_complex_components": 20,
            "parity_only_Q_pair_isolated": False,
        },
        "tensor_55_eta_plus_minus": {
            **tensor55,
            "SM_content": sm_tensor_content,
            "desired_Q_Qbar_complex_components": 12,
            "compulsory_other_complex_components": 18,
            "natural_rank_coupling": "Cbar 45_2 C",
            "V65_branch": "B5",
            "Spin10_SU5_X_note": (
                "the Q/Qbar rows lie in 45 -> 10_(+4)+10bar_(-4)+24_0+1_0, "
                "not the V67 spinor-partner X charges -1/+1"
            ),
        },
        "symmetric_tensor_65_eta_plus_minus": {
            **tensor65,
            "SM_content": sm_tensor_content,
            "desired_Q_Qbar_complex_components": 12,
            "compulsory_other_complex_components": 18,
            "renormalizable_Cbar_54_C_singlet": False,
            "Spin10_SU5_X_note": (
                "the Q/Qbar rows lie in the 54 SU5 15_(+4)+15bar_(-4) sectors, "
                "not the V67 spinor-partner X charges -1/+1"
            ),
        },
    }


def inherited_charge_no_go(v61: Mapping[str, Any], v65: Mapping[str, Any]) -> dict[str, Any]:
    forcing = v61["architecture_charge_forcings"]
    halves = forcing["bulk_hypermultiplet_halves"]
    rank = v61["rank_sector_r_compatibility"]
    branches = {
        row["id"]: row for row in v65["gut_scale_channel_classification"]["branches"]
    }
    charges = halves["charges"]
    q_phi = int(charges["Phi"])
    q_phic = int(charges["Phi_conjugate"])
    q_orphan, q_w = 0, 2
    neutral_vevs = {"C": 0, "Cbar": 0, "Sigma": 0}
    zero_vevs = {"S": 2, "T": 2}
    dressing_scan = []
    for n_charge_two in range(9):
        dressed = (q_orphan + q_phi + 2 * n_charge_two) % 4
        dressing_scan.append(
            {
                "number_of_charge_two_insertions": n_charge_two,
                "dressed_charge_mod4": dressed,
                "superpotential_allowed": dressed == q_w,
                "Kahler_neutral": dressed == 0,
            }
        )
    return {
        "inherited_selector": "order-four subgroup of the orbifold-preserved 5D SU(2)R Cartan",
        "bulk_hyper_charges": {"Phi": q_phi, "Phi_conjugate": q_phic},
        "bulk_operator": halves["forcing"],
        "bulk_operator_charge": int(halves["bulk_operator_charge"]),
        "orphan_superfield_charge": q_orphan,
        "required_opposite_chirality_partner_charge": q_w - q_orphan,
        "orphan_Phi_bilinear_charge_mod4": (q_orphan + q_phi) % 4,
        "orphan_Phic_bilinear_charge_mod4": (q_orphan + q_phic) % 4,
        "superpotential_charge_mod4": q_w,
        "ordinary_hyper_bilinear_allowed": False,
        "representation_or_parity_dependence": "NONE",
        "neutral_nonzero_vevs": neutral_vevs,
        "charge_two_fields_with_zero_supersymmetric_vev": zero_vevs,
        "neutral_vev_dressing_changes_charge": False,
        "all_orders_even_background_dressing": {
            "background_charge_set_mod4": [0, 2],
            "theorem": (
                "1 plus any sum of inherited even background charges is 1 or 3 mod4, "
                "never the W charge2 and never the Kahler charge0"
            ),
            "finite_residue_scan": dressing_scan,
            "all_superpotential_channels_forbidden": not any(
                row["superpotential_allowed"] for row in dressing_scan
            ),
            "all_Kahler_channels_forbidden": not any(
                row["Kahler_neutral"] for row in dressing_scan
            ),
            "only_charge_escape": "a qR=1 or qR=3 background expectation value",
            "odd_charge_vev_preserves_residual_g_squared_matter_parity": False,
            "matter_parity_scope": (
                "bare order-two g^2 subgroup of the inherited geometric Z4R; "
                "no compensating gauge-center locking is classified here"
            ),
        },
        "charge_two_vev_escape": {
            "status": branches["B6"]["status"],
            "obstruction": branches["B6"]["exact_obstruction"],
        },
        "mass_hessian_selection": (
            "with unbroken Z4R, a quadratic W Hessian entry is nonzero only "
            "when qi+qj=2 mod4; q0 rows pair only q2 columns, while q1 bulk "
            "states pair q1 states and cannot change the q0 orphan index"
        ),
        "GM_boundary": (
            "the inherited q0 orphan bilinear can receive the V65 GM mass, "
            "but a q0-q1 bilinear has charge1 and is not in the neutral Kahler class"
        ),
        "V65_B3_rebound": {
            "status": branches["B3"]["status"],
            "obstruction": branches["B3"]["exact_obstruction"],
            "V68_strengthening": "valid for every conventional hyper representation and every intrinsic parity",
        },
        "rank_charge_binding_exact": rank["charges"]
        == {"F_i": 1, "Sigma": 0, "C": 0, "Cbar": 0, "S": 2, "T": 2},
        "inherited_conventional_5D_split_bulk_status": "CLOSED",
    }


def candidate_spectrum_audit() -> dict[str, Any]:
    q_pair = vectorlike_indices("Q", +1)
    l_pair = vectorlike_indices("L", +1)
    u_pair = vectorlike_indices("U", -1)
    d_pair_minus = vectorlike_indices("D", -1)
    e_pair = vectorlike_indices("E", -1)
    n_pair = vectorlike_indices("N", -1)
    x_pair = vectorlike_indices("X56", +1)

    full32 = add_maps(q_pair, l_pair, u_pair, d_pair_minus, e_pair, n_pair)
    companions32 = add_maps(l_pair, u_pair, d_pair_minus, e_pair, n_pair)
    full55 = add_maps(q_pair, x_pair, d_pair_minus)
    companions55 = add_maps(x_pair, d_pair_minus)

    beta_anomaly_keys = ("b1_GUT", "b2", "b3", "A2", "A3", "dimension")
    assert tuple(full32) == beta_anomaly_keys
    return {
        "diagonal_selector_definition": {
            "new_symmetry": "Z4Rprime subset of Z4R_Cartan x Z4F_hyper",
            "hyper_flavor_charges": {"Phi": 1, "Phi_conjugate": -1},
            "new_R_charges": {"Phi": 2, "Phi_conjugate": 0},
            "bulk_term_still_has_charge_mod4": (2 + 0) % 4,
            "status": "CANDIDATE_NEW_ACTION_NOT_INHERITED",
            "required_new_data": [
                "an exact or gauged hyper-number symmetry and its UV origin",
                "all allowed boundary operators under the diagonal selector",
                "fixed-point continuous and discrete anomaly traces",
                "the supersymmetric BPS/jump boundary vacuum",
                "the full KK boundary-condition determinant",
            ],
        },
        "two_spinor_32_candidate": {
            "qR2_zero_modes": ["Q", "Qbar", "L", "Lbar"],
            "qR0_zero_modes": ["U", "Ubar", "D", "Dbar", "E", "Ebar", "N", "Nbar"],
            "desired_Q_pair": fraction_map(q_pair),
            "full_new_zero_spectrum": fraction_map(full32),
            "companions_after_pairing_Q_with_V64_orphans": fraction_map(companions32),
            "full_beta_is_complete_family_universal": (
                full32["b1_GUT"] == full32["b2"] == full32["b3"] == 4
            ),
            "desired_complex_components": int(q_pair["dimension"]),
            "companion_complex_components": int(companions32["dimension"]),
            "companion_mixed_R_anomaly": {
                "A3": fstr(companions32["A3"]),
                "A2": fstr(companions32["A2"]),
            },
            "X_charge_match_to_V67_partner_rows": True,
            "post_pairing_ledger_status": "CONDITIONAL_ON_A_FULL_RANK_LOCAL_BOUNDARY_DETERMINANT",
            "V65_lowest_UV_channel": "B4 scoped full-spinor wall coupling fails; a bulk boundary determinant is not thereby exhaustively excluded",
        },
        "adjoint_55_candidate": {
            "qR2_zero_modes": ["Q", "Qbar", "X56", "X56bar"],
            "qR0_zero_modes": ["D", "Dbar"],
            "desired_Q_pair": fraction_map(q_pair),
            "full_new_zero_spectrum": fraction_map(full55),
            "companions_after_pairing_Q_with_V64_orphans": fraction_map(companions55),
            "desired_complex_components": int(q_pair["dimension"]),
            "companion_complex_components": int(companions55["dimension"]),
            "companion_mixed_R_anomaly": {
                "A3": fstr(companions55["A3"]),
                "A2": fstr(companions55["A2"]),
            },
            "X_charge_match_to_V67_partner_rows": False,
            "X_charges": {
                "V67_spinor_partner_Q_Qbar": [-1, 1],
                "55_Q_Qbar": [4, -4],
            },
            "pairing_requirement": (
                "an X-changing rank-VEV insertion is required; the displayed "
                "Cbar 45_2 C invariant supplies it but is rejected by B5"
            ),
            "post_pairing_ledger_status": "CONDITIONAL_ON_THE_REJECTED_OR_REPLACED_X_CHANGING_BOUNDARY_OPERATOR",
            "V65_natural_UV_channel": "B5 Cbar 45_2 C forces v=0 through its adjoint F term",
        },
        "symmetric_65_candidate": {
            "same_zero_spectrum_as_55_for_eta_plus_minus": True,
            "full_new_zero_spectrum": fraction_map(full55),
            "companions_after_pairing_Q_with_V64_orphans": fraction_map(companions55),
            "renormalizable_Cbar_54_C_singlet": False,
            "X_charge_match_to_V67_partner_rows": False,
            "X_charges": {
                "V67_spinor_partner_Q_Qbar": [-1, 1],
                "65_Q_Qbar": [4, -4],
            },
            "pairing_requirement": (
                "an X-changing rank-VEV boundary operator beyond the absent "
                "renormalizable Cbar 54 C invariant is required"
            ),
            "post_pairing_ledger_status": "CONDITIONAL_ON_AN_UNCONSTRUCTED_HIGHER_OPERATOR",
        },
        "nonimport_rule": {
            "V67_Q_only_partner_beta": fraction_map(
                {key: q_pair[key] for key in ("b1_GUT", "b2", "b3")}
            ),
            "V67_Q_only_partner_mixed_R": {
                "A3": fstr(q_pair["A3"]),
                "A2": fstr(q_pair["A2"]),
            },
            "can_be_used_as_bulk_completion_ledger": False,
            "reason": (
                "a full hyper contributes both H and Hc zero sectors and "
                "localized projector anomalies; companions change both running "
                "and the discrete anomaly ledger"
            ),
        },
    }


def boundary_filter_and_frontier(v65: Mapping[str, Any]) -> dict[str, Any]:
    branches = {
        row["id"]: row for row in v65["gut_scale_channel_classification"]["branches"]
    }
    z_values = {"10": 1, "5bar": -3, "1": 5}
    zbar_values = {"10bar": -1, "5": 3, "1": -5}

    def pi10(z: int) -> Fraction:
        return -Fraction((z + 3) * (z - 5), 16)

    projector_values = {name: fstr(pi10(value)) for name, value in z_values.items()}

    def pi10bar(z: int) -> Fraction:
        return -Fraction((z - 3) * (z + 5), 16)

    conjugate_projector_values = {
        name: fstr(pi10bar(value)) for name, value in zbar_values.items()
    }
    return {
        "two_wall_projector_target": {
            "status": "REPRESENTATION_LEVEL_CANDIDATE_ONLY",
            "charge_convention": "Z used here equals minus the V65 X convention",
            "UV_SU5_projector": "Pi10(Z)=-(Z+3)(Z-5)/16",
            "UV_projector_values": projector_values,
            "UV_conjugate_SU5_projector": "Pi10bar(Z)=Pi10(-Z)=-(Z-3)(Z+5)/16",
            "UV_conjugate_projector_values": conjugate_projector_values,
            "IR_left_projector": "PiL=(1+P1spinor)/2",
            "intersection_16": "Pi10 PiL (16) = Q",
            "intersection_16bar": "Pi10bar PiL (16bar) = Qbar",
            "why_it_evades_pure_parity_theorem": (
                "the UV rank VEV and an IR boundary matrix jointly preserve only "
                "the SM; this is not a pure P0/P1 kernel"
            ),
            "not_a_local_operator": (
                "Pi10 PiL is not a local UV operator but a zero-mode design target; P1 is not a local UV "
                "spurion, so separate SO(10)- and Spin(4)xSpin(7)-invariant wall "
                "fields and boundary conditions must realize it"
            ),
        },
        "lowest_channel_obstructions": {
            "spinor_B4": {
                "status": branches["B4"]["status"],
                "obstruction": branches["B4"]["exact_obstruction"],
                "scope": "displayed wall-spinor mechanism, not every new two-wall bulk determinant",
            },
            "adjoint_B5": {
                "status": branches["B5"]["status"],
                "obstruction": branches["B5"]["exact_obstruction"],
            },
        },
        "surviving_5D_research_branch": {
            "status": "NEW_ACTION_NOT_CONSTRUCTED",
            "minimum_requirements": [
                "define the diagonal R x hyper-flavor symmetry",
                "give complete UV and IR local representations and superpotentials",
                "solve F/D/BPS jump conditions with the rank VEV",
                "derive the regulated infinite-dimensional KK determinant in every SM sector",
                "show no brane-tower null mode or companion exotic survives",
                "cancel anomalies independently at both fixed points",
                "redo beta thresholds, proton operators, soft terms and cosmology",
            ],
        },
        "six_dimensional_frontier": {
            "status": "REMAINS_THE_MINIMAL_LOCAL_Q_ONLY_BLUEPRINT_FROM_V67",
            "reason": (
                "a reduced G3211 fixed locus admits Q/Qbar themselves as local "
                "representations and avoids the inherited conventional-hyper charge/parity route"
            ),
            "accepted_action": False,
        },
    }


def gate_ledger() -> list[dict[str, Any]]:
    decisions = {
        "G1": "OPEN: the inherited conventional-5D-hyper split-bulk escape is now closed, but no diagonal-selector two-wall action or 6D completion is constructed.",
        "G2": "OPEN: no coefficient-level action, flavor determinant, soft spectrum or physical pole thresholds exist for a surviving branch.",
        "G3": "OPEN: the redesigned compactification, BPS boundary vacuum, moduli and full Hessian are absent.",
        "G4": "OPEN WITH EXACT ADVANCE: V67 identifies the needed qR2 row; V68 proves an ordinary inherited hyper cannot supply it.",
        "G5": "OPEN: the hypothetical 32 and 55/65 bulk spectra have 20 and 18 compulsory companion components before boundary mixing.",
        "G6": "OPEN: no accepted spectrum, reheating, defect, relic or moduli history exists.",
        "G7": "OPEN: new two-wall fields and the diagonal selector require a complete local operator and proton audit.",
        "G8": "OPEN: fixed-point anomalies, Dai-Freed data, a UV regulator and predictivity remain unconstructed.",
    }
    return [
        {"gate": f"G{i}", "status": "OPEN", "V68_closed": False, "decision": decisions[f"G{i}"]}
        for i in range(1, 9)
    ]


def source_manifest() -> dict[str, Any]:
    return {
        "local_files": [
            {"id": label, "path": path.name, "exists": path.is_file(), "sha256": file_sha(path)}
            for label, path in INPUTS.items()
        ],
        "primary_sources": copy.deepcopy(PRIMARY_SOURCES),
    }


def _body() -> dict[str, Any]:
    inputs = {
        label: load_bound(path, EXPECTED_CORES[label], label)
        for label, path in INPUTS.items()
    }
    charges = inherited_charge_no_go(inputs["v61_route"], inputs["v65_route"])
    parity = representation_and_parity_audit(inputs["v59_route"])
    candidates = candidate_spectrum_audit()
    frontier = boundary_filter_and_frontier(inputs["v65_route"])
    gates = gate_ledger()
    v59 = inputs["v59_route"]
    v67 = inputs["v67_route"]
    q_partner = candidates["two_spinor_32_candidate"]["desired_Q_pair"]
    checks = {
        "all_bound_cores_exact": all(
            inputs[label]["core_sha256"] == EXPECTED_CORES[label] for label in INPUTS
        ),
        "V59_projectors_bound": v59["gauge_and_zero_mode_audit"]["P0_vector"] == [1] * 10 + [-1]
        and v59["gauge_and_zero_mode_audit"]["P1_vector"] == [1] * 4 + [-1] * 7,
        "V61_hyper_halves_q1_q1": charges["bulk_hyper_charges"] == {"Phi": 1, "Phi_conjugate": 1},
        "orphan_hyper_bilinear_forbidden": charges["orphan_Phi_bilinear_charge_mod4"] == 1
        and charges["superpotential_charge_mod4"] == 2
        and not charges["ordinary_hyper_bilinear_allowed"],
        "neutral_vevs_do_not_repair_charge": not charges["neutral_vev_dressing_changes_charge"],
        "all_orders_even_dressing_no_go": charges["all_orders_even_background_dressing"]["all_superpotential_channels_forbidden"]
        and charges["all_orders_even_background_dressing"]["all_Kahler_channels_forbidden"]
        and not charges["all_orders_even_background_dressing"]["odd_charge_vev_preserves_residual_g_squared_matter_parity"],
        "charge_two_vev_escape_rejected": charges["charge_two_vev_escape"]["status"] == "CLOSED",
        "inherited_split_bulk_closed": charges["inherited_conventional_5D_split_bulk_status"] == "CLOSED",
        "all_joint_sector_dimensions_exact": parity["all_sector_dimensions_exact"],
        "tensor_multiplicities_derived_from_vector_projectors": parity["independent_tensor_multiplicity_derivation"]["matches_11_55_65_tables"],
        "spinor_multiplicities_bound_to_V59": parity["V59_spinor_joint_multiplicity_binding"]["matches"],
        "pure_parity_Q_only_no_go": parity["theorem"]["pure_parity_Q_only_possible"] is False,
        "all_32_hypers_are_complete_spinors": parity["every_32_hyper_is_16_or_16bar"],
        "32_requires_20_companions": parity["two_32s_for_Q_and_Qbar"]["compulsory_other_complex_components"] == 20,
        "55_and_65_require_18_companions": parity["tensor_55_eta_plus_minus"]["compulsory_other_complex_components"] == 18
        and parity["symmetric_tensor_65_eta_plus_minus"]["compulsory_other_complex_components"] == 18,
        "32_beta_complete_family_crosscheck": candidates["two_spinor_32_candidate"]["full_beta_is_complete_family_universal"],
        "32_companion_beta_exact": candidates["two_spinor_32_candidate"]["companions_after_pairing_Q_with_V64_orphans"]
        | {} == candidates["two_spinor_32_candidate"]["companions_after_pairing_Q_with_V64_orphans"]
        and candidates["two_spinor_32_candidate"]["companions_after_pairing_Q_with_V64_orphans"]["b1_GUT"] == "19/5"
        and candidates["two_spinor_32_candidate"]["companions_after_pairing_Q_with_V64_orphans"]["b2"] == "1"
        and candidates["two_spinor_32_candidate"]["companions_after_pairing_Q_with_V64_orphans"]["b3"] == "2",
        "55_companion_beta_exact": candidates["adjoint_55_candidate"]["companions_after_pairing_Q_with_V64_orphans"]["b1_GUT"] == "27/5"
        and candidates["adjoint_55_candidate"]["companions_after_pairing_Q_with_V64_orphans"]["b2"] == "3"
        and candidates["adjoint_55_candidate"]["companions_after_pairing_Q_with_V64_orphans"]["b3"] == "3",
        "55_65_X_mismatch_explicit": candidates["adjoint_55_candidate"]["X_charge_match_to_V67_partner_rows"] is False
        and candidates["symmetric_65_candidate"]["X_charge_match_to_V67_partner_rows"] is False
        and candidates["adjoint_55_candidate"]["X_charges"]["55_Q_Qbar"] == [4, -4]
        and "X-changing" in candidates["adjoint_55_candidate"]["pairing_requirement"],
        "V67_Q_partner_indices_reproduced": q_partner["b1_GUT"] == "1/5"
        and q_partner["b2"] == "3"
        and q_partner["b3"] == "2"
        and q_partner["A3"] == "2"
        and q_partner["A2"] == "3",
        "V67_Q_only_ledger_not_imported": candidates["nonimport_rule"]["can_be_used_as_bulk_completion_ledger"] is False,
        "two_wall_projectors_exact": frontier["two_wall_projector_target"]["UV_projector_values"] == {"10": "1", "5bar": "0", "1": "0"},
        "two_wall_conjugate_projector_exact": frontier["two_wall_projector_target"]["UV_conjugate_projector_values"] == {"10bar": "1", "5": "0", "1": "0"}
        and frontier["two_wall_projector_target"]["charge_convention"] == "Z used here equals minus the V65 X convention",
        "two_wall_filter_not_overclaimed": frontier["two_wall_projector_target"]["status"] == "REPRESENTATION_LEVEL_CANDIDATE_ONLY"
        and frontier["surviving_5D_research_branch"]["status"] == "NEW_ACTION_NOT_CONSTRUCTED",
        "V67_current_action_rejection_preserved": v67["terminal_decision"]["current_bound_Spin11_action"] == "REJECTED",
        "all_gates_open": all(row["status"] == "OPEN" and not row["V68_closed"] for row in gates),
    }
    return {
        "schema": "susy_v68_spin11_split_bulk_parity_no_go_audit/v1",
        "version": "V68",
        "date": "2026-08-30",
        "status": STATUS,
        "question": "Can the inherited 5D Spin(11) split-bulk route furnish the V67 qR=2 Q/Qbar index partners?",
        "classification": (
            "INHERITED_CONVENTIONAL_5D_HYPER_ROUTE_CLOSED__PURE_PARITY_Q_ONLY_"
            "ROUTE_CLOSED__DIAGONAL_R_X_FLAVOR_TWO_WALL_ROUTE_IS_NEW_ACTION_ONLY"
        ),
        "lineage": {
            "bound_input_cores": copy.deepcopy(EXPECTED_CORES),
            "relation": (
                "V68 resolves the V67 5D split-bulk classification; no prior artifact "
                "is modified and no candidate evidence is promoted into the bound action"
            ),
        },
        "inherited_Z4R_charge_no_go": charges,
        "representation_and_parity_audit": parity,
        "diagonal_selector_candidate_spectra": candidates,
        "boundary_filter_and_frontier": frontier,
        "gate_ledger": gates,
        "falsifiers": [
            {
                "id": "F1",
                "test": "exhibit a conventional V61 hyper zero mode with qR=2 without an added flavor rotation",
                "effect": "falsifies the inherited charge no-go",
            },
            {
                "id": "F2",
                "test": "exhibit a pure P0/P1 zero kernel that is not invariant under the common Pati-Salam group",
                "effect": "falsifies the parity theorem",
            },
            {
                "id": "F3",
                "test": "construct the diagonal selector, local two-wall fields and a full-rank KK determinant with no companions",
                "effect": "promotes the surviving 5D research branch for a new same-action audit",
            },
            {
                "id": "F4",
                "test": "find a nonzero fixed-point anomaly class in any proposed redesign",
                "effect": "rejects that redesign even if its integrated spectrum is vectorlike",
            },
        ],
        "terminal_decision": {
            "current_bound_Spin11_action": "REJECTED",
            "inherited_conventional_5D_split_bulk_route": "CLOSED",
            "pure_parity_Q_only_route_all_representations": "CLOSED",
            "diagonal_R_x_hyper_flavor_route": "CANDIDATE_NEW_ACTION_NOT_CONSTRUCTED",
            "SM_selective_two_wall_filter": "REPRESENTATION_LEVEL_ONLY",
            "D67_6D_route": "CANDIDATE_NEW_ACTION_NOT_CONSTRUCTED",
            "physical_colored_mass_certified": False,
            "same_action_microscopic_completion_found": False,
            "V68_G1_closed": False,
            "V68_G4_closed": False,
            "closed_gates": [],
            "complete_theory": False,
            "honest_outcome": (
                "V68 closes the inherited conventional-hyper split-bulk escape and "
                "the entire pure-parity Q-only class.  Only a redesigned diagonal "
                "selector with SM-selective boundary determinants, or a higher-dimensional "
                "action, remains; neither is constructed, so the current action stays rejected."
            ),
        },
        "claim_boundary": {
            "exact_new_result": (
                "representation-independent Z4R charge no-go plus common-group parity theorem"
            ),
            "new_physics_candidate": (
                "diagonal geometric-R x hyper-number selector and a two-wall missing-partner filter"
            ),
            "not_claimed": [
                "a no-go for every possible 5D boundary-mixing action",
                "an accepted diagonal selector",
                "a full KK determinant",
                "fixed-point anomaly cancellation",
                "a physical exotic mass",
                "gate closure",
            ],
        },
        "source_manifest": source_manifest(),
        "integrity_checks": checks,
        "n_integrity_checks": len(checks),
        "n_failed_integrity_checks": sum(not value for value in checks.values()),
    }


def build_report() -> dict[str, Any]:
    report = _body()
    report["core_sha256"] = canonical_sha(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("V68 canonical core mismatch")
    expected = build_report()
    if canonical_bytes(report) != canonical_bytes(expected):
        raise RuntimeError("V68 recomputation mismatch")
    if report.get("n_failed_integrity_checks") != 0:
        failed = [name for name, ok in report["integrity_checks"].items() if not ok]
        raise RuntimeError(f"V68 integrity checks failed: {failed}")
    terminal = report["terminal_decision"]
    if terminal["closed_gates"] or terminal["complete_theory"]:
        raise RuntimeError("V68 overclaimed gate closure")


def render_markdown(report: Mapping[str, Any]) -> str:
    charge = report["inherited_Z4R_charge_no_go"]
    parity = report["representation_and_parity_audit"]
    candidates = report["diagonal_selector_candidate_spectra"]
    frontier = report["boundary_filter_and_frontier"]
    spinor_rows = "\n".join(
        f"| {row['eta']} | {', '.join(row['H_zero_reps'])} | "
        f"{', '.join(row['Hc_left_chiral_zero_reps'])} | "
        f"{row['4D_left_chiral_identification']} |"
        for row in parity["spinor_32_intrinsic_scan"]
    )
    gate_rows = "\n".join(
        f"| {row['gate']} | {row['status']} | {row['decision']} |"
        for row in report["gate_ledger"]
    )
    sources = "\n".join(
        f"- [{row['title']}]({row['url']}): {row['scope']}"
        for row in report["source_manifest"]["primary_sources"]
    )
    requirements = "\n".join(
        f"- {item}"
        for item in frontier["surviving_5D_research_branch"]["minimum_requirements"]
    )
    return f"""# V68 Spin(11) split-bulk parity no-go audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Result

The inherited conventional 5D split-bulk repair is **closed**.  V61 fixes
both chiral halves of every ordinary hypermultiplet to
`{charge['bulk_hyper_charges']}` under the geometric `Z4R`.  The V64 orphan
has charge 0, so either orphan-hyper bilinear has charge
`{charge['orphan_Phi_bilinear_charge_mod4']}`, not the superpotential charge
`{charge['superpotential_charge_mod4']}`.  This is independent of the Spin(11)
representation and intrinsic parity.  Dressing by the nonzero neutral rank
VEVs does not change the charge.  More strongly, any number of inherited
charge-zero or charge-two background insertions leaves charge 1 or 3, never a
superpotential charge 2 or a neutral Kahler operator.  A charge-one or
charge-three VEV would break the residual matter parity, while a charge-two
VEV is the rejected V65 B6 route.  The odd-VEV statement concerns the bare
geometric `g^2` subgroup; no compensating gauge-center locking is assumed.

This closes the item V67 had labelled `5D split-bulk unclassified` for the
**inherited V61 action**.  It does not close a redesigned R symmetry or a new
boundary-mixing action.

## Independent parity theorem

The common projector group is
`{parity['projector_groups']['common_group']}`.  Since every common-group
generator commutes with both projectors, every pure zero-mode kernel is a
complete common-group module.  In particular,

```text
{parity['theorem']['Q_branching']}
{parity['theorem']['Qbar_branching']}
```

Therefore no pure parity can retain Q without L, or Qbar without Lbar.  This
statement covers every Spin(11) representation and also flavor-space parity
matrices on multiple copies.  SM-breaking boundary mass matrices are outside
its scope.

For the 32 the exhaustive intrinsic-sign scan is:

| eta | H zero sector | Hc left-chiral zero sector | Total |
|---|---|---|---|
{spinor_rows}

Every 32 hyper gives a complete 16 or 16bar.  Two 32s supplying Q and Qbar
therefore bring {parity['two_32s_for_Q_and_Qbar']['compulsory_other_complex_components']}
other complex components.  The closest 55/65 choice gives `(2,2,6)` plus
`(1,1,6)`: Q/Qbar, a vectorlike `Y=+-5/6` doublet, and a vectorlike D pair,
leaving {parity['tensor_55_eta_plus_minus']['compulsory_other_complex_components']}
companions.  The natural 55 coupling is exactly V65 B5 and its adjoint F-term
forces the rank VEV to zero.

## New diagonal-selector candidate

One can algebraically define
`{candidates['diagonal_selector_definition']['new_symmetry']}` by giving the
two hyper halves opposite flavor charges.  Their new R charges become
`{candidates['diagonal_selector_definition']['new_R_charges']}`, while the
bulk kinetic superpotential still has charge 2.  This is **new physics**, not
the inherited selector: its flavor symmetry, wall terms, BPS conditions and
fixed-point anomalies have not been constructed.

It also cannot reuse the V67 Q-only ledgers.  For two 32s, after the qR=2 Q
pair marries the V64 orphans, the compulsory spectrum has

```text
Delta b = ({candidates['two_spinor_32_candidate']['companions_after_pairing_Q_with_V64_orphans']['b1_GUT']},
           {candidates['two_spinor_32_candidate']['companions_after_pairing_Q_with_V64_orphans']['b2']},
           {candidates['two_spinor_32_candidate']['companions_after_pairing_Q_with_V64_orphans']['b3']})
         in (b1_GUT,b2,b3),
Delta(A3,A2) = ({candidates['two_spinor_32_candidate']['companion_mixed_R_anomaly']['A3']},
                {candidates['two_spinor_32_candidate']['companion_mixed_R_anomaly']['A2']}).
```

For the 55/65 candidate the companion shift is
`({candidates['adjoint_55_candidate']['companions_after_pairing_Q_with_V64_orphans']['b1_GUT']},
{candidates['adjoint_55_candidate']['companions_after_pairing_Q_with_V64_orphans']['b2']},
{candidates['adjoint_55_candidate']['companions_after_pairing_Q_with_V64_orphans']['b3']})`.
This post-pairing ledger is conditional: the tensor Q/Qbar rows have
`X=(+4,-4)`, not the V67 spinor partners' `X=(-1,+1)`, and need an X-changing
rank-VEV boundary operator.  For the 55 that operator is the rejected B5
coupling; for the 65 it begins beyond the absent renormalizable
`Cbar*54*C` invariant.  These are not the V67 Q-only threshold or anomaly
results.

## Only surviving 5D loophole

At the representation level a two-wall filter can target

```text
{frontier['two_wall_projector_target']['UV_SU5_projector']}
{frontier['two_wall_projector_target']['UV_conjugate_SU5_projector']}
{frontier['two_wall_projector_target']['IR_left_projector']}
{frontier['two_wall_projector_target']['intersection_16']}
{frontier['two_wall_projector_target']['intersection_16bar']}
```

Here `Z=-X_V65`.  The two polynomials are exactly one on the SU(5) 10 and
10bar respectively, and zero on their 5/singlet complements.  Combined with
the opposite wall's left projector, their intersections are Q and Qbar.  But
this product is not a local UV operator: separate local fields and boundary
matrices must realize it.  The lowest displayed spinor and adjoint channels
are already the scoped V65 B4/B5 failures.

A credible new 5D attempt must:

{requirements}

Until then, the six-dimensional reduced-symmetry fixed-locus route remains the
minimal local Q-only blueprint, not an accepted theory.

## Gate ledger

| Gate | Status | Decision |
|---|---|---|
{gate_rows}

## Primary sources

{sources}

## Decision

{report['terminal_decision']['honest_outcome']}  G1-G8 remain OPEN.
"""


def write_outputs(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--emit-json", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate(report)
    if args.write:
        write_outputs(report)
    if args.check:
        if not JSON_PATH.is_file() or not MD_PATH.is_file():
            raise RuntimeError("V68 generated artifacts are missing")
        if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
            raise RuntimeError("V68 JSON artifact is stale")
        if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
            raise RuntimeError("V68 markdown artifact is stale")
    if args.emit_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(report["status"])
        print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
