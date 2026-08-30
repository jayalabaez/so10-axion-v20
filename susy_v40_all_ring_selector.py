#!/usr/bin/env python3
"""Fail-closed V40 U(1)_F to Z9 baryon-selector rebuild.

V39's Z3 selector was broken by the Pati-Salam VEV.  V40 instead uses an
anomaly-free U(1)_F selector sector Higgsed by charge-nine fields, leaving an
unbroken Z9.  The construction protects the same-orientation Q4 and Qc4
source ring against every declared VEV dressing.  It deliberately does not
claim a full proton calculation, a flavour fit, or a UV completion of the
pre-existing Z5610 times Z4R selector product.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V40_ALL_RING_SELECTOR.json"
MD_PATH = ROOT / "SUSY_V40_ALL_RING_SELECTOR.md"
TEST_PATH = ROOT / "test_susy_v40_all_ring_selector.py"

ORDER = 9
STATUS = (
    "V40_U1F_TO_UNBROKEN_Z9_SAME_ORIENTATION_ALL_RING_SELECTOR_CERTIFIED__"
    "DIRAC_NEUTRINO_REBUILD_CONDITIONAL__FULL_GATES_FAIL_CLOSED"
)
PS_GROUPS = ("SU4", "SU2L", "SU2R")


# dim is the physical Weyl-component multiplicity.  Each PS coefficient is
# 2T(r), including all other gauge and family multiplicities.  u1f is an
# integer parent charge rather than only a residual Z9 representative.
FIELDS: dict[str, dict[str, Any]] = {
    "H": {"dim": 4, "u1f": 0, "z5610": 0, "r4": 0, "pq": 0, "ps": {"SU2L": 2, "SU2R": 2}},
    "Q": {"dim": 24, "u1f": 3, "z5610": 0, "r4": 1, "pq": 0, "ps": {"SU4": 6, "SU2L": 12}},
    "Qc": {"dim": 24, "u1f": -3, "z5610": 0, "r4": 1, "pq": 0, "ps": {"SU4": 6, "SU2R": 12}},
    "X": {"dim": 1, "u1f": 0, "z5610": 0, "r4": 2, "pq": 0, "ps": {}},
    "Sc": {"dim": 8, "u1f": 0, "z5610": 0, "r4": 0, "pq": 0, "ps": {"SU4": 2, "SU2R": 4}},
    "Sbc": {"dim": 8, "u1f": 0, "z5610": 0, "r4": 0, "pq": 0, "ps": {"SU4": 2, "SU2R": 4}},
    "SigC": {"dim": 6, "u1f": 0, "z5610": 0, "r4": 2, "pq": 0, "ps": {"SU4": 2}},
    "SigBc": {"dim": 6, "u1f": 0, "z5610": 0, "r4": 2, "pq": 0, "ps": {"SU4": 2}},
    "PsiBar": {"dim": 8, "u1f": -3, "z5610": 5440, "r4": 3, "pq": -170, "ps": {"SU4": 2, "SU2L": 4}},
    "Psi": {"dim": 8, "u1f": 3, "z5610": 0, "r4": 1, "pq": 0, "ps": {"SU4": 2, "SU2L": 4}},
    "PsiC": {"dim": 8, "u1f": -3, "z5610": 0, "r4": 1, "pq": 0, "ps": {"SU4": 2, "SU2R": 4}},
    "PsiCBar": {"dim": 8, "u1f": 3, "z5610": 5440, "r4": 3, "pq": -170, "ps": {"SU4": 2, "SU2R": 4}},
    "P": {"dim": 1, "u1f": 0, "z5610": 170, "r4": 2, "pq": 170, "ps": {}},
    "NDirac": {"dim": 3, "u1f": -3, "z5610": 0, "r4": 1, "pq": 0, "ps": {}},
    "Pb": {"dim": 1, "u1f": 0, "z5610": 5440, "r4": 2, "pq": -170, "ps": {}},
    "Zp": {"dim": 1, "u1f": 0, "z5610": 0, "r4": 2, "pq": 0, "ps": {}},
    "A2": {"dim": 1, "u1f": 3, "z5610": 3211, "r4": 0, "pq": -23, "ps": {}},
    "A32": {"dim": 1, "u1f": -3, "z5610": 2569, "r4": 0, "pq": 193, "ps": {}},
    "A15": {"dim": 1, "u1f": 0, "z5610": 4299, "r4": 2, "pq": -57, "ps": {}},
    "A17": {"dim": 1, "u1f": 0, "z5610": 1141, "r4": 2, "pq": -113, "ps": {}},
    "A16": {"dim": 1, "u1f": 0, "z5610": 5525, "r4": 0, "pq": -85, "ps": {}},
    "ThetaPlus": {"dim": 1, "u1f": 9, "z5610": 0, "r4": 0, "pq": 0, "ps": {}},
    "ThetaMinus": {"dim": 1, "u1f": -9, "z5610": 0, "r4": 0, "pq": 0, "ps": {}},
    "STheta": {"dim": 1, "u1f": 0, "z5610": 0, "r4": 2, "pq": 0, "ps": {}},
    # Each doublet row contains four copies.
    "L0": {"dim": 8, "u1f": 0, "z5610": 0, "r4": 1, "pq": 0, "ps": {"SU2L": 4}},
    "Lminus9": {"dim": 8, "u1f": -9, "z5610": 0, "r4": 1, "pq": 0, "ps": {"SU2L": 4}},
    "R0": {"dim": 8, "u1f": 0, "z5610": 0, "r4": 1, "pq": 0, "ps": {"SU2R": 4}},
    "Rplus9": {"dim": 8, "u1f": 9, "z5610": 0, "r4": 1, "pq": 0, "ps": {"SU2R": 4}},
    "E4": {"dim": 1, "u1f": 4, "z5610": 0, "r4": 1, "pq": 0, "ps": {}},
    "E5": {"dim": 1, "u1f": 5, "z5610": 0, "r4": 1, "pq": 0, "ps": {}},
    "E3": {"dim": 1, "u1f": 3, "z5610": 0, "r4": 1, "pq": 0, "ps": {}},
    "E6": {"dim": 1, "u1f": 6, "z5610": 0, "r4": 1, "pq": 0, "ps": {}},
    "Eminus2": {"dim": 1, "u1f": -2, "z5610": 0, "r4": 1, "pq": 0, "ps": {}},
    "Eminus7": {"dim": 1, "u1f": -7, "z5610": 0, "r4": 1, "pq": 0, "ps": {}},
}

VISIBLE_FIELDS = (
    "H", "Q", "Qc", "X", "Sc", "Sbc", "SigC", "SigBc", "PsiBar", "Psi",
    "PsiC", "PsiCBar", "P", "NDirac", "Pb", "Zp", "A2", "A32", "A15",
    "A17", "A16",
)
VEV_FIELDS = ("Sc", "Sbc", "P", "Pb", "ThetaPlus", "ThetaMinus")

# These are the primitive continuous lifts used only for a diagnostic
# countercheck against the older V38 U(1)_X times U(1)_H parent attempt.
# They are not a claimed parent of the V40 product symmetry.
V38_X_LIFT = {
    "PsiBar": -2,
    "PsiCBar": -2,
    "P": 2,
    "Pb": -2,
    "A2": -29,
    "A32": 31,
    "A15": -3,
    "A17": 1,
    "A16": -1,
}
V38_H_LIFT = {"A2": 1, "A32": -1, "A15": 69, "A17": -69}

# The V39 type-I terms Sbc Qc Nv, Sbc PsiC Nv, and Nv Nv are deliberately
# absent.  The V40 effective term is a Dirac-neutrino direction, not a fit.
RENORMALIZABLE_TERMS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("X_linear_PS", ("X",)), ("X_linear_PQ", ("X",)),
    ("Zp_linear_PS", ("Zp",)), ("Zp_linear_PQ", ("Zp",)),
    ("X_Sbc_Sc", ("X", "Sbc", "Sc")), ("X_P_Pb", ("X", "P", "Pb")),
    ("Zp_Sbc_Sc", ("Zp", "Sbc", "Sc")), ("Zp_P_Pb", ("Zp", "P", "Pb")),
    ("X_cubic", ("X", "X", "X")), ("XXZp", ("X", "X", "Zp")),
    ("XZpZp", ("X", "Zp", "Zp")), ("Zp_cubic", ("Zp", "Zp", "Zp")),
    ("X_HH", ("X", "H", "H")), ("X_SigC_SigBc", ("X", "SigC", "SigBc")),
    ("Zp_HH", ("Zp", "H", "H")), ("Zp_SigC_SigBc", ("Zp", "SigC", "SigBc")),
    ("ScScSigC", ("Sc", "Sc", "SigC")), ("SbcSbcSigBc", ("Sbc", "Sbc", "SigBc")),
    ("Q_H_Qc", ("Q", "H", "Qc")), ("Q_H_PsiC", ("Q", "H", "PsiC")),
    ("Psi_H_Qc", ("Psi", "H", "Qc")), ("Psi_H_PsiC", ("Psi", "H", "PsiC")),
    ("P_PsiBar_Q", ("P", "PsiBar", "Q")), ("P_PsiBar_Psi", ("P", "PsiBar", "Psi")),
    ("P_PsiCBar_Qc", ("P", "PsiCBar", "Qc")), ("P_PsiCBar_PsiC", ("P", "PsiCBar", "PsiC")),
    ("Pb_A2_A32", ("Pb", "A2", "A32")), ("P_A15_A17", ("P", "A15", "A17")),
    ("P_A16_A16", ("P", "A16", "A16")),
    ("STheta_linear", ("STheta",)), ("STheta_ThetaPlus_ThetaMinus", ("STheta", "ThetaPlus", "ThetaMinus")),
    ("ThetaPlus_L_mass", ("ThetaPlus", "L0", "Lminus9")),
    ("ThetaMinus_R_mass", ("ThetaMinus", "R0", "Rplus9")),
    ("ThetaMinus_E45_mass", ("ThetaMinus", "E4", "E5")),
    ("ThetaMinus_E36_mass", ("ThetaMinus", "E3", "E6")),
    ("ThetaPlus_Em2m7_mass", ("ThetaPlus", "Eminus2", "Eminus7")),
)
EFFECTIVE_TERMS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Dirac_neutrino_Q_H_Sc_NDirac_over_M", ("Q", "H", "Sc", "NDirac")),
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def charge(fields: Iterable[str], key: str, modulus: int | None = None) -> int:
    total = sum(int(FIELDS[name][key]) for name in fields)
    return total if modulus is None else total % modulus


def u1f_anomaly_audit() -> dict[str, Any]:
    mixed = {
        group: sum(int(row["u1f"]) * int(row["ps"].get(group, 0)) for row in FIELDS.values())
        for group in PS_GROUPS
    }
    grav = sum(int(row["dim"]) * int(row["u1f"]) for row in FIELDS.values())
    cubic = sum(int(row["dim"]) * int(row["u1f"]) ** 3 for row in FIELDS.values())
    doublets = {"SU2L": 30, "SU2R": 38}
    return {
        "mixed_U1F_PS_squared": mixed,
        "U1F_gravitational": grav,
        "U1F_cubic": cubic,
        "all_local_continuous_anomalies_cancel": (
            all(value == 0 for value in mixed.values()) and grav == 0 and cubic == 0
        ),
        "SU2_global_doublet_counts": doublets,
        "all_SU2_Witten_parities_even": all(value % 2 == 0 for value in doublets.values()),
        "cancellation_ledger": {
            "visible_before_completion": {"SU4": 0, "SU2L": 36, "SU2R": -36, "gravitational": -9, "cubic": -81},
            "four_L_pairs": {"SU2L": -36, "gravitational": -72, "cubic": -5832},
            "four_R_pairs": {"SU2R": 36, "gravitational": 72, "cubic": 5832},
            "singlet_pairs_45_36_minus2minus7": {"gravitational": 9, "cubic": 81},
        },
        "scope_limit": (
            "This closes local anomalies of PS times U(1)_F.  The unspecified continuous "
            "parent, if any, of Z5610 is not included, so product cross anomalies remain open."
        ),
    }


def finite_z9_audit() -> dict[str, Any]:
    reps = {name: int(row["u1f"]) % ORDER for name, row in FIELDS.items()}
    linear = sum(int(row["dim"]) * reps[name] for name, row in FIELDS.items())
    cubic = sum(int(row["dim"]) * reps[name] ** 3 for name, row in FIELDS.items())
    coefficient = ORDER * ORDER + 3 * ORDER + 2
    return {
        "convention": "same Hsieh/Dai-Freed arithmetic convention used in the V39 audit",
        "canonical_Z9_charges": reps,
        "Delta_s1_canonical": linear,
        "Delta_s3_canonical": cubic,
        "linear_condition_2Delta_s1_mod_9": (2 * linear) % ORDER,
        "cubic_condition_mod_54": (coefficient * cubic) % (6 * ORDER),
        "both_vanish": (2 * linear) % ORDER == 0 and (coefficient * cubic) % (6 * ORDER) == 0,
    }


def discrete_residue_audit() -> dict[str, Any]:
    mixed = {
        group: sum((int(row["u1f"]) % ORDER) * int(row["ps"].get(group, 0)) for row in FIELDS.values())
        for group in PS_GROUPS
    }
    carriers = [row for row in FIELDS.values() if int(row["z5610"]) != 0]
    cross_12 = sum(int(row["dim"]) * (int(row["u1f"]) % ORDER) * int(row["z5610"]) ** 2 for row in carriers)
    cross_21 = sum(int(row["dim"]) * (int(row["u1f"]) % ORDER) ** 2 * int(row["z5610"]) for row in carriers)
    return {
        "mixed_PS_Z9_raw": mixed,
        "mixed_PS_Z9_residues_mod_9": {group: value % ORDER for group, value in mixed.items()},
        "all_mixed_PS_Z9_residues_vanish": all(value % ORDER == 0 for value in mixed.values()),
        "necessary_Z9_Z5610_cross_residues": {
            "C_Z9_Z5610_squared_mod_9": cross_12 % ORDER,
            "C_Z9_squared_Z5610_mod_9": cross_21 % ORDER,
            "qualification": (
                "Residual modular rows are not a full continuous U(1)_F times parent(Z5610) "
                "anomaly cancellation or a product-bordism calculation."
            ),
        },
    }


def conditional_v38_parent_cross_anomaly_audit() -> dict[str, Any]:
    """Show why V40 cannot silently reuse the old continuous selector parent."""

    def lifted(name: str, table: Mapping[str, int]) -> int:
        return int(table.get(name, 0))

    fx2 = sum(
        int(row["dim"]) * int(row["u1f"]) * lifted(name, V38_X_LIFT) ** 2
        for name, row in FIELDS.items()
    )
    f2x = sum(
        int(row["dim"]) * int(row["u1f"]) ** 2 * lifted(name, V38_X_LIFT)
        for name, row in FIELDS.items()
    )
    fh2 = sum(
        int(row["dim"]) * int(row["u1f"]) * lifted(name, V38_H_LIFT) ** 2
        for name, row in FIELDS.items()
    )
    f2h = sum(
        int(row["dim"]) * int(row["u1f"]) ** 2 * lifted(name, V38_H_LIFT)
        for name, row in FIELDS.items()
    )
    fxh = sum(
        int(row["dim"]) * int(row["u1f"]) * lifted(name, V38_X_LIFT) * lifted(name, V38_H_LIFT)
        for name, row in FIELDS.items()
    )
    f2xh = sum(
        int(row["dim"]) * int(row["u1f"]) ** 2 * lifted(name, V38_X_LIFT) * lifted(name, V38_H_LIFT)
        for name, row in FIELDS.items()
    )
    rows = {
        "C_F_X_squared": fx2,
        "C_F_squared_X": f2x,
        "C_F_H_squared": fh2,
        "C_F_squared_H": f2h,
        "C_F_X_H": fxh,
        "C_F_squared_X_H": f2xh,
    }
    return {
        "scope": (
            "Raw continuous cross rows obtained if the primitive V38 U(1)_X and "
            "U(1)_H lifts are reused without additional V40 cross-anomalon or GS data."
        ),
        "rows": rows,
        "all_rows_vanish": all(value == 0 for value in rows.values()),
        "conclusion": (
            "The PS times U(1)_F sector is locally anomaly free, but V40 has not "
            "completed a common continuous parent for it and the old Z5610 selector."
        ),
    }


def term_audit() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for kind, source in (("renormalizable", RENORMALIZABLE_TERMS), ("effective", EFFECTIVE_TERMS)):
        for label, fields in source:
            rows.append({
                "kind": kind, "label": label, "fields": list(fields),
                "U1F": charge(fields, "u1f"), "Z9": charge(fields, "u1f", ORDER),
                "Z4R": charge(fields, "r4", 4), "Z5610": charge(fields, "z5610", 5610),
                "PQ_numerator_over_170": charge(fields, "pq"),
            })
    return {
        "terms": rows,
        "renormalizable_term_count": len(RENORMALIZABLE_TERMS),
        "effective_term_count": len(EFFECTIVE_TERMS),
        "all_listed_terms_U1F_neutral": all(row["U1F"] == 0 for row in rows),
        "all_listed_terms_Z9_neutral": all(row["Z9"] == 0 for row in rows),
        "all_listed_terms_Z4R_charge_two": all(row["Z4R"] == 2 for row in rows),
        "all_listed_terms_Z5610_neutral": all(row["Z5610"] == 0 for row in rows),
        "all_listed_terms_PQ_neutral": all(row["PQ_numerator_over_170"] == 0 for row in rows),
        "removed_V39_type_I_terms": ["Sbc Qc Nv", "Sbc PsiC Nv", "Nv Nv"],
        "replacement": "Q H Sc NDirac / M with an unspecified messenger and flavour sector",
    }


def ring_proof() -> dict[str, Any]:
    sources: list[dict[str, Any]] = []
    for driver in ("X", "Zp"):
        for matter in ("Q", "Qc"):
            fields = (driver,) + (matter,) * 4
            sources.append({
                "operator": " ".join(fields), "U1F": charge(fields, "u1f"),
                "Z9": charge(fields, "u1f", ORDER), "Z4R": charge(fields, "r4", 4),
                "forbidden": charge(fields, "u1f", ORDER) != 0,
            })
    plus = ("Q", "Psi", "PsiCBar")
    minus = ("Qc", "PsiBar", "PsiC")
    orientation = {
        "four_SU4_fundamental_matter": sorted({charge(combo, "u1f", ORDER) for combo in itertools.product(plus, repeat=4)}),
        "four_SU4_antifundamental_matter": sorted({charge(combo, "u1f", ORDER) for combo in itertools.product(minus, repeat=4)}),
    }
    vev_lifts = {name: int(FIELDS[name]["u1f"]) for name in VEV_FIELDS}
    mixed_fields = ("X", "Q", "Q", "Qc", "Qc")
    return {
        "unbroken_remnant": "Z9 from U(1)_F Higgs fields of charges +9 and -9",
        "VEV_field_U1F_lifts": vev_lifts,
        "VEV_field_Z9_residues": {name: value % ORDER for name, value in vev_lifts.items()},
        "all_declared_VEVs_preserve_Z9": all(value % ORDER == 0 for value in vev_lifts.values()),
        "local_driver_dressed_Q4_Qc4_sources": sources,
        "all_local_sources_forbidden": all(row["forbidden"] for row in sources),
        "same_orientation_four_matter_Z9_residues": orientation,
        "all_same_orientation_four_matter_tuples_forbidden": all(
            value != 0 for values in orientation.values() for value in values
        ),
        "all_declared_VEV_dressing_proof": {
            "fundamental": "4*(+3)+9*k = 12+9*k cannot vanish for integer k",
            "antifundamental": "4*(-3)+9*k = -12+9*k cannot vanish for integer k",
            "Kahler_and_soft_conjugates": "conjugate VEVs only replace 9*k by -9*k",
        },
        "all_order_same_orientation_Q4_Qc4_VEV_dressing_forbidden": True,
        "mixed_orientation_caveat": {
            "example": "X Q Q Qc Qc",
            "U1F": charge(mixed_fields, "u1f"),
            "Z9": charge(mixed_fields, "u1f", ORDER),
            "meaning": (
                "mixed-orientation four-matter structures are not ruled out by this selector. "
                "Their component baryon/lepton content must be classified separately."
            ),
        },
        "precise_scope": (
            "same-orientation Pati-Salam four-matter Q4/Qc4 source operators, including "
            "all holomorphic and conjugate declared-VEV dressings.  This does not establish "
            "a proton lifetime or classify every mixed-orientation operator."
        ),
    }


def majorana_to_dirac_contract() -> dict[str, Any]:
    return {
        "majorana_no_go": {
            "deduction": [
                "neutral Sbc plus Sbc Qc Nv gives q(Qc)+q(Nv)=0",
                "an allowed Majorana Nv Nv gives 2q(Nv)=0 in the unbroken remnant",
                "therefore 4q(Qc)=0 and Qc4 cannot be protected by an ordinary additive remnant",
            ],
            "conclusion": "the V39 neutral-VEV type-I block must be removed for this Z9 route",
        },
        "V40_direction": {
            "new_singlet": "three NDirac of U(1)_F charge -3",
            "effective_operator": "Q H Sc NDirac / M",
            "selector_check": "3 + 0 + 0 - 3 = 0",
            "still_required": [
                "renormalizable messenger completion",
                "Dirac-neutrino and charged-fermion flavour fit",
                "threshold-matched PMNS/CKM likelihood",
            ],
        },
    }


def gate_statuses() -> list[dict[str, Any]]:
    return [
        {"gate": "G1", "full_gate_closed": False, "landed": "PS times U(1)_F local anomaly-free selector parent", "still_required": "Z5610/Z4R product anomaly, mirror, and microscopic UV completion"},
        {"gate": "G2", "full_gate_closed": False, "landed": "explicit new field and charge architecture", "still_required": "stabilized vacuum, pole spectrum, and covariance"},
        {"gate": "G3", "full_gate_closed": False, "landed": "U(1)_F Higgsing source is explicit", "still_required": "Kahler/soft potential, branches, bounces, and thermal selection"},
        {"gate": "G4", "full_gate_closed": False, "landed": "no new mediation result", "still_required": "hidden mediation, singlet lifting, mu/Bmu, and EWSB"},
        {"gate": "G5", "full_gate_closed": False, "landed": "only future compatibility constraints", "still_required": "component dark/PQ cosmology"},
        {"gate": "G6", "full_gate_closed": False, "landed": "threshold field content is specified", "still_required": "physical threshold-matched RG evolution"},
        {"gate": "G7", "full_gate_closed": False, "landed": "same-orientation Q4/Qc4 all-declared-VEV selector subproblem is blocked", "still_required": "mixed operator classification, components, Wilsons, dressing, running, hadronic matrix elements"},
        {"gate": "G8", "full_gate_closed": False, "landed": "Dirac-neutrino route replaces the Majorana obstruction", "still_required": "messenger/flavour theory and global likelihood"},
    ]


def source_manifest() -> list[dict[str, Any]]:
    result = []
    for path in (Path(__file__), TEST_PATH):
        result.append({"path": path.name, "exists": path.is_file(), "sha256": sha256_file(path) if path.is_file() else None})
    return result


def build_report() -> dict[str, Any]:
    u1 = u1f_anomaly_audit()
    finite = finite_z9_audit()
    residues = discrete_residue_audit()
    parent_cross = conditional_v38_parent_cross_anomaly_audit()
    terms = term_audit()
    ring = ring_proof()
    gates = gate_statuses()
    report: dict[str, Any] = {
        "schema": "susy-v40-all-ring-selector-v1",
        "status": STATUS,
        "complete_theory_exists": False,
        "established_full_predictive_closed_count": 0,
        "selector_design": {
            "gauge_parent": "U(1)_F",
            "Higgsing": "ThetaPlus(+9), ThetaMinus(-9), STheta(ThetaPlus ThetaMinus-vF^2)",
            "exact_low_energy_remnant": "Z9",
            "visible_U1F_lifts": {name: int(FIELDS[name]["u1f"]) for name in VISIBLE_FIELDS},
            "heavy_anomaly_completion": [
                "four (1,2,1) pairs with charges (0,-9)",
                "four (1,1,2) pairs with charges (0,+9)",
                "singlet pairs (4,5), (3,6), and (-2,-7)",
            ],
        },
        "U1F_continuous_anomaly_audit": u1,
        "finite_Z9_anomaly_audit": finite,
        "mixed_and_cross_residue_audit": residues,
        "conditional_V38_parent_cross_anomaly_audit": parent_cross,
        "operator_and_charge_audit": terms,
        "same_orientation_baryon_ring_proof": ring,
        "Majorana_no_go_and_Dirac_rebuild": majorana_to_dirac_contract(),
        "gate_statuses": gates,
        "promotion_boundary": {
            "established": [
                "a local PS times U(1)_F anomaly-free parent",
                "an unbroken Z9 on the declared VEV branch",
                "all declared-VEV dressings of same-orientation Q4/Qc4 sources are forbidden",
            ],
            "not_established": [
                "a continuous parent or bordism completion for Z5610 times Z9 times Z4R",
                "a soft/Kahler vacuum, spectrum, cosmology, or flavour likelihood",
                "a full mixed operator ring or component proton-decay calculation",
            ],
        },
        "source_manifest": source_manifest(),
    }
    cross = residues["necessary_Z9_Z5610_cross_residues"]
    report["integrity_checks"] = {
        "all_local_U1F_anomalies_cancel": u1["all_local_continuous_anomalies_cancel"],
        "all_SU2_Witten_parities_even": u1["all_SU2_Witten_parities_even"],
        "finite_Z9_arithmetic_passes": finite["both_vanish"],
        "mixed_PS_Z9_residues_vanish": residues["all_mixed_PS_Z9_residues_vanish"],
        "listed_Z9_Z5610_cross_residues_vanish": cross["C_Z9_Z5610_squared_mod_9"] == 0 and cross["C_Z9_squared_Z5610_mod_9"] == 0,
        "common_continuous_parent_for_U1F_and_old_Z5610_is_not_claimed": not parent_cross["all_rows_vanish"],
        "all_listed_terms_U1F_neutral": terms["all_listed_terms_U1F_neutral"],
        "all_listed_terms_Z9_neutral": terms["all_listed_terms_Z9_neutral"],
        "all_listed_terms_Z4R_charge_two": terms["all_listed_terms_Z4R_charge_two"],
        "declared_VEVs_preserve_Z9": ring["all_declared_VEVs_preserve_Z9"],
        "all_driver_dressed_Q4_Qc4_sources_forbidden": ring["all_local_sources_forbidden"],
        "all_declared_VEV_dressings_of_same_orientation_Q4_Qc4_forbidden": ring["all_order_same_orientation_Q4_Qc4_VEV_dressing_forbidden"],
        "no_full_gate_promoted": all(not row["full_gate_closed"] for row in gates),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    u1 = report["U1F_continuous_anomaly_audit"]
    finite = report["finite_Z9_anomaly_audit"]
    ring = report["same_orientation_baryon_ring_proof"]
    terms = report["operator_and_charge_audit"]
    parent_cross = report["conditional_V38_parent_cross_anomaly_audit"]
    sources = "\n".join(
        f"| {row['operator']} | {row['Z9']} | {'yes' if row['forbidden'] else 'no'} |"
        for row in ring["local_driver_dressed_Q4_Qc4_sources"]
    )
    ledger = "\n".join(
        f"| {row['gate']} | {'closed' if row['full_gate_closed'] else 'open'} | {row['landed']} |"
        for row in report["gate_statuses"]
    )
    return f"""# V40 unbroken-Z9 selector audit

Status: {report['status']}

V40 is an architecture change.  It uses a local-anomaly-free PS times U(1)_F
sector Higgsed by charge-nine fields to an unbroken Z9.  The old type-I
Majorana source is replaced by a conditional Dirac-neutrino operator.

## Exact results

- Continuous anomalies: {u1['mixed_U1F_PS_squared']}; gravity
  {u1['U1F_gravitational']}; cubic {u1['U1F_cubic']}.
- SU(2) doublet counts: {u1['SU2_global_doublet_counts']}.
- Finite Z9 arithmetic passes: {finite['both_vanish']}.
- Listed U(1)_F, Z9, and Z4R term checks:
  {terms['all_listed_terms_U1F_neutral']},
  {terms['all_listed_terms_Z9_neutral']},
  {terms['all_listed_terms_Z4R_charge_two']}.
- Reusing the old V38 continuous Z5610 parent is not valid without new
  cross-anomaly data: {parent_cross['rows']}.

| Source | Z9 charge | Forbidden |
|---|---:|---|
{sources}

Every declared PS/PQ/U(1)_F VEV is zero modulo nine.  Therefore a
same-orientation four-fundamental source has 12 = 3 modulo nine and a
four-antifundamental source has -12 = 6 modulo nine after any declared VEV
or conjugate-VEV dressing.  That exact selector obstruction repairs the V39
Qc4 loophole.

The audit does not claim that mixed-orientation structures are absent:
X Q Q Qc Qc is selector neutral.  Whether those structures generate baryon
violation is a separate component/operator calculation.

## Gate ledger

| Gate | Status | Advance |
|---|---|---|
{ledger}

The result is not a complete theory.  The Z5610 times Z9 times Z4R product
origin, a soft/Kahler vacuum, spectrum, cosmology, and flavour likelihood
remain required.

Core SHA-256: {report['core_sha256']}
"""


def write_artifacts() -> dict[str, Any]:
    report = build_report()
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")
    return report


def check_artifacts() -> None:
    report = build_report()
    if not JSON_PATH.is_file() or JSON_PATH.read_text(encoding="utf-8") != json.dumps(report, indent=2, sort_keys=True) + "\n":
        raise RuntimeError("V40 selector JSON is missing or stale; run with --write")
    if not MD_PATH.is_file() or MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError("V40 selector Markdown is missing or stale; run with --write")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        print(write_artifacts()["status"])
    if args.check:
        check_artifacts()
        print("V40_ALL_RING_SELECTOR_ARTIFACTS_CHECK_PASS")
    if not args.write and not args.check:
        print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
