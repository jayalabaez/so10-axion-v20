#!/usr/bin/env python3
"""Fail-closed V43 repair audit for the V42 six-matter G7 witness.

V42 found that the V40 product selector permits

    ThetaPlus^2 (Qc)^6 (Sbc)^2 / M^7.

This audit asks a deliberately narrow question: can an *additional unbroken
ordinary additive selector* block that operator while leaving the V40
U(1)_F->Z9 source and its V41 Dirac messenger intact?

It finds the smallest charge-arithmetic answer, Z4_M.  The same calculation
then exposes a hard boundary: under the stated ordinary, no-GS, fully-massive
threshold assumptions, the three required NDirac fields leave a residual
gravitational anomaly.  Thus this is a useful targeted selector and no-go
theorem, not a new discrete-gauge completion and not a G7 closure.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from math import gcd
from pathlib import Path
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parent
OUTPUT_JSON = ROOT / "SUSY_V43_G7_Z4M_SELECTOR_REPAIR_AUDIT.json"
OUTPUT_MD = ROOT / "SUSY_V43_G7_Z4M_SELECTOR_REPAIR_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v43_g7_z4m_selector_repair.py"

Z9_ORDER = 9
M_ORDER = 4
R4_TARGET = 2
MAX_FRONTIER_DEGREE = 12
STATUS = (
    "V43_Z4M_TARGETED_G7_WITNESS_SELECTOR_ARITHMETIC_CERTIFIED__"
    "NO_DECOUPLING_ONLY_ORDINARY_DISCRETE_GAUGE_COMPLETION__G7_FAIL_CLOSED"
)
PS_GROUPS = ("SU4", "SU2L", "SU2R")


# ``m`` is an integer U(1)_M lift whose Z4 residue is the candidate selector.
# The V40 source/messenger terms force the orientation pattern once all visible
# VEVs are Z4_M neutral: Q/Psi/PsiCBar/F have +1 and their barred partners,
# together with NDirac, have -1.  The physical dimensions and doubled Dynkin
# coefficients are the same conventions used in the V40/V41 audits.
FIELDS: dict[str, dict[str, Any]] = {
    "H": {"dim": 4, "u1f": 0, "r4": 0, "m": 0, "ps": {"SU2L": 2, "SU2R": 2}},
    "Q": {"dim": 24, "u1f": 3, "r4": 1, "m": 1, "ps": {"SU4": 6, "SU2L": 12}},
    "Qc": {"dim": 24, "u1f": -3, "r4": 1, "m": -1, "ps": {"SU4": 6, "SU2R": 12}},
    "X": {"dim": 1, "u1f": 0, "r4": 2, "m": 0, "ps": {}},
    "Zp": {"dim": 1, "u1f": 0, "r4": 2, "m": 0, "ps": {}},
    "Sc": {"dim": 8, "u1f": 0, "r4": 0, "m": 0, "ps": {"SU4": 2, "SU2R": 4}},
    "Sbc": {"dim": 8, "u1f": 0, "r4": 0, "m": 0, "ps": {"SU4": 2, "SU2R": 4}},
    "SigC": {"dim": 6, "u1f": 0, "r4": 2, "m": 0, "ps": {"SU4": 2}},
    "SigBc": {"dim": 6, "u1f": 0, "r4": 2, "m": 0, "ps": {"SU4": 2}},
    "PsiBar": {"dim": 8, "u1f": -3, "r4": 3, "m": -1, "ps": {"SU4": 2, "SU2L": 4}},
    "Psi": {"dim": 8, "u1f": 3, "r4": 1, "m": 1, "ps": {"SU4": 2, "SU2L": 4}},
    "PsiC": {"dim": 8, "u1f": -3, "r4": 1, "m": -1, "ps": {"SU4": 2, "SU2R": 4}},
    "PsiCBar": {"dim": 8, "u1f": 3, "r4": 3, "m": 1, "ps": {"SU4": 2, "SU2R": 4}},
    "P": {"dim": 1, "u1f": 0, "r4": 2, "m": 0, "ps": {}},
    "Pb": {"dim": 1, "u1f": 0, "r4": 2, "m": 0, "ps": {}},
    "NDirac": {"dim": 3, "u1f": -3, "r4": 1, "m": -1, "ps": {}},
    "A2": {"dim": 1, "u1f": 3, "r4": 0, "m": 0, "ps": {}},
    "A32": {"dim": 1, "u1f": -3, "r4": 0, "m": 0, "ps": {}},
    "A15": {"dim": 1, "u1f": 0, "r4": 2, "m": 0, "ps": {}},
    "A17": {"dim": 1, "u1f": 0, "r4": 2, "m": 0, "ps": {}},
    "A16": {"dim": 1, "u1f": 0, "r4": 0, "m": 0, "ps": {}},
    "STheta": {"dim": 1, "u1f": 0, "r4": 2, "m": 0, "ps": {}},
    "ThetaPlus": {"dim": 1, "u1f": 9, "r4": 0, "m": 0, "ps": {}},
    "ThetaMinus": {"dim": 1, "u1f": -9, "r4": 0, "m": 0, "ps": {}},
    "L0": {"dim": 8, "u1f": 0, "r4": 1, "m": 0, "ps": {"SU2L": 4}},
    "Lminus9": {"dim": 8, "u1f": -9, "r4": 1, "m": 0, "ps": {"SU2L": 4}},
    "R0": {"dim": 8, "u1f": 0, "r4": 1, "m": 0, "ps": {"SU2R": 4}},
    "Rplus9": {"dim": 8, "u1f": 9, "r4": 1, "m": 0, "ps": {"SU2R": 4}},
    "E4": {"dim": 1, "u1f": 4, "r4": 1, "m": 0, "ps": {}},
    "E5": {"dim": 1, "u1f": 5, "r4": 1, "m": 0, "ps": {}},
    "E3": {"dim": 1, "u1f": 3, "r4": 1, "m": 0, "ps": {}},
    "E6": {"dim": 1, "u1f": 6, "r4": 1, "m": 0, "ps": {}},
    "Eminus2": {"dim": 1, "u1f": -2, "r4": 1, "m": 0, "ps": {}},
    "Eminus7": {"dim": 1, "u1f": -7, "r4": 1, "m": 0, "ps": {}},
    # V41's Dirac-messenger pair.
    "F": {"dim": 8, "u1f": 3, "r4": 1, "m": 1, "ps": {"SU4": 2, "SU2R": 4}},
    "Fc": {"dim": 8, "u1f": -3, "r4": 1, "m": -1, "ps": {"SU4": 2, "SU2R": 4}},
    # The prospective U(1)_M -> Z4_M Higgs/stabilizer sector.
    "SM": {"dim": 1, "u1f": 0, "r4": 2, "m": 0, "ps": {}},
    "PhiPlus": {"dim": 1, "u1f": 0, "r4": 0, "m": 4, "ps": {}},
    "PhiMinus": {"dim": 1, "u1f": 0, "r4": 0, "m": -4, "ps": {}},
    # A minimal *mixed-PS-anomaly* threshold repair.  Each row denotes three
    # copies, so its dimension and Dynkin row include that multiplicity.
    "LM0": {"dim": 6, "u1f": 0, "r4": 1, "m": 0, "ps": {"SU2L": 3}},
    "LMminus4": {"dim": 6, "u1f": 0, "r4": 1, "m": -4, "ps": {"SU2L": 3}},
    "RM0": {"dim": 6, "u1f": 0, "r4": 1, "m": 0, "ps": {"SU2R": 3}},
    "RMplus4": {"dim": 6, "u1f": 0, "r4": 1, "m": 4, "ps": {"SU2R": 3}},
}

VISIBLE_VEVS = ("Sc", "Sbc", "P", "Pb", "H", "ThetaPlus", "ThetaMinus", "PhiPlus", "PhiMinus")

# This reproduces every V40 term used in its term audit, together with the
# V41 renormalizable messenger and the candidate U(1)_M Higgs/threshold terms.
V40_TERMS: tuple[tuple[str, tuple[str, ...]], ...] = (
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
MESSENGER_TERMS = (
    ("Q_H_Fc", ("Q", "H", "Fc")),
    ("F_Sc_NDirac", ("F", "Sc", "NDirac")),
    ("M_F_Fc", ("F", "Fc")),
    ("Dirac_effective_Q_H_Sc_NDirac", ("Q", "H", "Sc", "NDirac")),
)
M_PARENT_TERMS = (
    ("SM_linear", ("SM",)),
    ("SM_PhiPlus_PhiMinus", ("SM", "PhiPlus", "PhiMinus")),
    ("PhiPlus_LM_mass", ("PhiPlus", "LM0", "LMminus4")),
    ("PhiMinus_RM_mass", ("PhiMinus", "RM0", "RMplus4")),
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def total(names: Iterable[str], key: str, modulus: int | None = None) -> int:
    value = sum(int(FIELDS[name][key]) for name in names)
    return value if modulus is None else value % modulus


def selector_charge(names: Iterable[str]) -> dict[str, int | bool]:
    fields = tuple(names)
    u1f = total(fields, "u1f")
    r4 = total(fields, "r4", 4)
    m = total(fields, "m")
    return {
        "U1F": u1f,
        "Z9": u1f % Z9_ORDER,
        "Z4R": r4,
        "U1M_lift": m,
        "Z4M": m % M_ORDER,
        "allowed_by_preexisting_V40_selectors": u1f == 0 and r4 == R4_TARGET,
        "allowed_by_new_Z4M": m % M_ORDER == 0,
    }


def term_audit() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for kind, terms in (("V40", V40_TERMS), ("V41_messenger", MESSENGER_TERMS), ("new_M_parent", M_PARENT_TERMS)):
        for label, fields in terms:
            row = selector_charge(fields)
            rows.append({"kind": kind, "label": label, "fields": list(fields), **row})
    return {
        "rows": rows,
        "V40_term_count": len(V40_TERMS),
        "messenger_and_effective_term_count": len(MESSENGER_TERMS),
        "all_U1F_neutral": all(row["U1F"] == 0 for row in rows),
        "all_Z9_neutral": all(row["Z9"] == 0 for row in rows),
        "all_Z4R_target_two": all(row["Z4R"] == R4_TARGET for row in rows),
        "all_Z4M_neutral": all(row["Z4M"] == 0 for row in rows),
        "meaning": (
            "The candidate is a product selector: it leaves the V40 U(1)_F/Z9 charges and the V41 "
            "Dirac messenger unchanged, while every listed required term is neutral under Z4_M."
        ),
    }


def low_operator_audit() -> list[dict[str, Any]]:
    definitions = (
        ("conventional_Q4_epsilon", ("Q",) * 4, "standard same-orientation four-matter source"),
        ("conventional_Qc4_epsilon", ("Qc",) * 4, "standard same-orientation four-matter source"),
        ("left_one_PS_VEV_precursor", ("ThetaMinus", "Q", "Q", "Q", "Sbc", "H"), "QQQH precursor on the Sbc branch"),
        ("right_one_PS_VEV_precursor", ("ThetaPlus", "Qc", "Qc", "Qc", "Sc"), "UDD precursor on the Sc branch"),
        ("delta_RPV_control", ("Q", "Q", "Qc", "Sc"), "LQD/LLE precursor"),
        ("bilinear_LH_control", ("Q", "H", "Sc"), "LH precursor"),
        ("required_Dirac_operator", ("Q", "H", "Sc", "NDirac"), "required V40 Dirac neutrino operator"),
        ("V42_six_matter_witness", ("ThetaPlus", "ThetaPlus") + ("Qc",) * 6 + ("Sbc",) * 2, "DeltaB=-1, DeltaL=-3 V42 witness"),
    )
    rows = []
    for label, fields, boundary in definitions:
        signature = selector_charge(fields)
        rows.append({
            "label": label,
            "fields": list(fields),
            "boundary": boundary,
            "selector_signature": signature,
            "blocked_by_union_of_old_and_new_selectors": (
                not signature["allowed_by_preexisting_V40_selectors"] or not signature["allowed_by_new_Z4M"]
            ),
        })
    return rows


def theta_completion(difference: int) -> tuple[str, ...] | None:
    if difference % 3:
        return None
    if difference > 0:
        return ("ThetaMinus",) * (difference // 3)
    if difference < 0:
        return ("ThetaPlus",) * ((-difference) // 3)
    return ()


def rank_one_su2r_possible(qc: int, sbc: int, sc: int, h: int) -> bool:
    free = qc + h
    return sc <= sbc + free and sbc <= sc + free


def bounded_v42_frontier() -> dict[str, Any]:
    """Repeat V42's stated degree-12 representation-count frontier independently."""
    rows: list[dict[str, Any]] = []
    representation_count_rows = 0
    for q, qc, sbc, sc, h in itertools.product(range(9), range(9), range(6), range(6), range(5)):
        matter = q + qc
        raw_degree = matter + sbc + sc + h
        net_su4 = q + sbc - qc - sc
        if raw_degree == 0 or raw_degree > MAX_FRONTIER_DEGREE or abs(net_su4) != 4:
            continue
        if (q + h) % 2 or (qc + sbc + sc + h) % 2:
            continue
        if not ((q >= 3 if net_su4 == 4 else qc >= 3) and rank_one_su2r_possible(qc, sbc, sc, h)):
            continue
        difference = q - qc
        theta = theta_completion(difference)
        if theta is None or matter % 4 != R4_TARGET:
            continue
        degree = raw_degree + len(theta)
        if degree > MAX_FRONTIER_DEGREE:
            continue
        representation_count_rows += 1
        mcharge = difference % M_ORDER
        rows.append({
            "counts": {"Q": q, "Qc": qc, "Sbc": sbc, "Sc": sc, "H": h},
            "matter_orientation_Q_minus_Qc": difference,
            "theta_completion": list(theta),
            "complete_field_degree": degree,
            "Z4M": mcharge,
            "blocked_by_Z4M": mcharge != 0,
            "boundary": (
                "A representation-count frontier only.  Rows with Z4M=0 are deliberately not called "
                "safe: their B/L component content and Wilson coefficients remain unclassified."
            ),
        })
    rows.sort(key=lambda row: (row["complete_field_degree"], json.dumps(row["counts"], sort_keys=True)))
    return {
        "domain": "V42 single-epsilon/rank-one-SU2R frontier through complete field degree 12",
        "representation_count_rows": representation_count_rows,
        "rows": rows,
        "blocked_rows": sum(row["blocked_by_Z4M"] for row in rows),
        "unblocked_orientation_neutral_rows": [row for row in rows if not row["blocked_by_Z4M"]],
        "witness_row_blocked": any(
            row["counts"] == {"Q": 0, "Qc": 6, "Sbc": 2, "Sc": 0, "H": 0} and row["blocked_by_Z4M"]
            for row in rows
        ),
    }


def anomaly_rows(names: Iterable[str]) -> dict[str, int]:
    selected = tuple(names)
    result = {
        group: sum(int(FIELDS[name]["m"]) * int(FIELDS[name]["ps"].get(group, 0)) for name in selected)
        for group in PS_GROUPS
    }
    result["gravity"] = sum(int(FIELDS[name]["m"]) * int(FIELDS[name]["dim"]) for name in selected)
    result["cubic"] = sum(int(FIELDS[name]["m"]) ** 3 * int(FIELDS[name]["dim"]) for name in selected)
    return result


def continuous_parent_audit() -> dict[str, Any]:
    base = tuple(name for name in FIELDS if name not in {"SM", "PhiPlus", "PhiMinus", "LM0", "LMminus4", "RM0", "RMplus4"})
    threshold = ("LM0", "LMminus4", "RM0", "RMplus4")
    base_rows = anomaly_rows(base)
    threshold_rows = anomaly_rows(threshold)
    full_rows = {key: base_rows[key] + threshold_rows[key] for key in base_rows}
    cross_u1m_u1f = {
        "C_M_U1F_squared": sum(
            int(FIELDS[name]["dim"]) * int(FIELDS[name]["m"]) * int(FIELDS[name]["u1f"]) ** 2
            for name in base
        ),
        "C_M_squared_U1F": sum(
            int(FIELDS[name]["dim"]) * int(FIELDS[name]["m"]) ** 2 * int(FIELDS[name]["u1f"])
            for name in base
        ),
    }
    eta = M_ORDER // 2
    return {
        "convention": (
            "Mixed rows use the doubled Dynkin coefficients recorded in the field table.  The non-R even-Z_N "
            "low-energy congruence screen uses eta=N/2; it is a necessary ordinary no-GS screen, not a full "
            "Spin-bordism or GS analysis."
        ),
        "U1M_base_rows_before_new_threshold": base_rows,
        "three_pair_mixed_PS_anomalon_threshold": {
            "terms": ["PhiPlus LM0 LMminus4", "PhiMinus RM0 RMplus4"],
            "increment": threshold_rows,
            "rank_witness": "three-by-three identity mass matrices after <PhiPlus>, <PhiMinus> are nonzero",
            "all_massed_fields_Z4M_neutral": True,
        },
        "rows_after_minimal_mixed_PS_repair": full_rows,
        "mixed_PS_rows_cancel": all(full_rows[group] == 0 for group in PS_GROUPS),
        "continuous_gravity_and_cubic_still_nonzero": full_rows["gravity"] != 0 and full_rows["cubic"] != 0,
        "U1M_U1F_product_cross_rows": {
            "rows": cross_u1m_u1f,
            "all_vanish": all(value == 0 for value in cross_u1m_u1f.values()),
            "meaning": (
                "The proposed ordinary selector also cannot silently be combined with the V40 U(1)_F parent: "
                "these continuous product rows require additional UV data even before the old Z5610 product is considered."
            ),
        },
        "Z4M_low_energy_necessary_screen": {
            "eta": eta,
            "mixed_residues_mod_eta": {group: base_rows[group] % eta for group in PS_GROUPS},
            "gravity_residue_mod_eta": base_rows["gravity"] % eta,
            "mixed_pass": all(base_rows[group] % eta == 0 for group in PS_GROUPS),
            "gravity_pass": base_rows["gravity"] % eta == 0,
            "result": "fails because the three NDirac fields give A_gravity=-3=1 mod 2",
        },
    }


def eta(order: int) -> int:
    return order if order % 2 else order // 2


def ordinary_selector_no_go() -> dict[str, Any]:
    scan = []
    for order in range(2, 97):
        residual_eta = eta(order)
        blocks = (-6) % order != 0
        mixed_pass = (12 % residual_eta == 0) and (-12 % residual_eta == 0)
        gravity_pass = (-3) % residual_eta == 0
        scan.append({
            "N": order,
            "eta": residual_eta,
            "blocks_V42_witness_for_primitive_q": blocks,
            "mixed_PS_necessary_screen_pass": mixed_pass,
            "gravity_necessary_screen_pass": gravity_pass,
            "ordinary_no_GS_screen_pass": mixed_pass and gravity_pass,
        })
    accepted = [row["N"] for row in scan if row["ordinary_no_GS_screen_pass"]]
    intersection = [row["N"] for row in scan if row["ordinary_no_GS_screen_pass"] and row["blocks_V42_witness_for_primitive_q"]]
    return {
        "assumptions": [
            "an ordinary non-R Z_N selector remains unbroken on the PS/PQ/EW/Theta branch",
            "Q has a primitive selector charge q while H, Sc, Sbc and the Theta VEVs are neutral modulo N",
            "the V40 Yukawa and V41 Dirac terms are present, so q(Qc)=q(NDirac)=-q",
            "all additional anomaly-repair fermions have residual-preserving full-rank masses",
            "no Green--Schwarz/inflow/topological sector and no unpaired light chiral anomaly carrier is postulated",
        ],
        "charge_reduction": [
            "Q H Qc=0 gives q(Qc)=-q(Q) because q(H)=0.",
            "Q H Sc NDirac=0 gives q(NDirac)=-q(Q) because q(Sc)=0.",
            "All other charged V40/vectorlike/messenger contributions pair and cancel in the linear gravitational row.",
            "Thus A_gravity=-3q from the three NDirac fields, while the V42 witness has charge -6q.",
        ],
        "analytic_proof": (
            "For primitive q, the necessary no-GS gravitational congruence is eta(N) divides 3.  For odd N this "
            "permits N=3 (besides the trivial order one); for even N it permits N=2 or N=6.  Every permitted "
            "order divides six, so -6q is zero and cannot block the V42 witness.  If q is nonprimitive, replace N "
            "by its faithful action order N/gcd(N,q); the same argument applies."
        ),
        "scan_N_2_to_96": scan,
        "ordinary_no_GS_orders_passing_necessary_screen": accepted,
        "orders_that_both_pass_and_block_witness": intersection,
        "no_decoupling_only_ordinary_discrete_gauge_repair_found": not intersection,
        "scope_boundary": (
            "This is not a theorem against a specified GS/inflow construction, a symmetry extension, a strongly "
            "coupled topological sector, or an explicitly retained massless anomaly carrier.  Each would require "
            "new quantized UV and spectrum data."
        ),
    }


def source_manifest() -> list[dict[str, Any]]:
    return [
        {"path": path.name, "exists": path.is_file(), "sha256": sha256_file(path) if path.is_file() else None}
        for path in (Path(__file__), TEST_PATH)
    ]


def build_report() -> dict[str, Any]:
    terms = term_audit()
    controls = low_operator_audit()
    frontier = bounded_v42_frontier()
    parent = continuous_parent_audit()
    no_go = ordinary_selector_no_go()
    controls_by_name = {row["label"]: row for row in controls}
    report: dict[str, Any] = {
        "schema": "susy-v43-g7-z4m-selector-repair-audit-v1",
        "status": STATUS,
        "complete_theory_exists": False,
        "scope": (
            "A target-specific discrete-selector and anomaly-boundary audit.  It does not constitute a complete "
            "Pati--Salam invariant ring, a product-symmetry UV completion, a spectrum/vacuum calculation, or a "
            "proton-decay prediction."
        ),
        "candidate": {
            "name": "Z4_M orientation selector",
            "prospective_parent": "U(1)_M Higgsed by PhiPlus(+4), PhiMinus(-4), with SM(PhiPlus PhiMinus-v_M^2)",
            "unbroken_branch": "All PS/PQ/EW/Theta/Phi VEVs have Z4_M residue zero.",
            "charge_assignment": {name: int(row["m"]) % M_ORDER for name, row in FIELDS.items() if int(row["m"]) % M_ORDER != 0},
            "smallest_order_that_blocks_six_Qc_witness": M_ORDER,
            "why_Z2_and_Z3_fail": {"Z2_witness_charge": (-6) % 2, "Z3_witness_charge": (-6) % 3},
        },
        "required_term_audit": terms,
        "named_B_L_and_required_operator_audit": controls,
        "independent_V42_degree12_frontier": frontier,
        "continuous_parent_and_discrete_anomaly_boundary": parent,
        "ordinary_unbroken_selector_no_go": no_go,
        "literature_context": [
            {
                "reference": "L. Ibanez, More About Discrete Gauge Anomalies",
                "url": "https://arxiv.org/abs/hep-ph/9210211",
                "relevance": "Heavy thresholds and a discrete GS sector can change what a low-energy anomaly screen establishes.",
            },
            {
                "reference": "C.-T. Hsieh, Discrete gauge anomalies revisited",
                "url": "https://arxiv.org/abs/1808.02881",
                "relevance": "A complete discrete-gauge claim requires the global symmetry structure, beyond the necessary congruence screen used here.",
            },
        ],
        "decision": {
            "all_V40_and_V41_required_terms_preserved": terms["all_U1F_neutral"] and terms["all_Z9_neutral"] and terms["all_Z4R_target_two"] and terms["all_Z4M_neutral"],
            "V42_witness_blocked_by_Z4M": not controls_by_name["V42_six_matter_witness"]["selector_signature"]["allowed_by_new_Z4M"],
            "named_lower_B_L_controls_are_still_blocked_by_at_least_one_selector": all(
                controls_by_name[label]["blocked_by_union_of_old_and_new_selectors"]
                for label in ("conventional_Q4_epsilon", "conventional_Qc4_epsilon", "left_one_PS_VEV_precursor", "right_one_PS_VEV_precursor", "delta_RPV_control", "bilinear_LH_control")
            ),
            "required_Dirac_operator_remains_allowed": controls_by_name["required_Dirac_operator"]["selector_signature"]["allowed_by_new_Z4M"],
            "candidate_is_anomaly_complete_discrete_gauge_symmetry": False,
            "no_decoupling_only_ordinary_gauge_repair_exists_under_stated_assumptions": no_go["no_decoupling_only_ordinary_discrete_gauge_repair_found"],
            "G7_closed": False,
            "gates_promoted": [],
        },
        "source_manifest": source_manifest(),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    candidate = report["candidate"]
    terms = report["required_term_audit"]
    controls = {row["label"]: row for row in report["named_B_L_and_required_operator_audit"]}
    frontier = report["independent_V42_degree12_frontier"]
    parent = report["continuous_parent_and_discrete_anomaly_boundary"]
    no_go = report["ordinary_unbroken_selector_no_go"]
    return "\n".join([
        "# V43 targeted Z4M repair audit for the V42 G7 witness",
        "",
        f"Status: `{report['status']}`",
        "",
        "## Outcome",
        "",
        "There is a smallest **charge-arithmetic** repair: an extra unbroken ordinary `Z4_M`.  Give `Q`, `Psi`, `PsiCBar`, and the Dirac messenger `F` charge `+1`; give `Qc`, `PsiBar`, `PsiC`, `Fc`, and `NDirac` charge `-1`; keep every displayed PS/PQ/EW/Theta VEV and all drivers neutral.  The full V40 term list plus the V41 messenger remains neutral.  The V42 operator has `Z4_M=2`, so it is forbidden.",
        "",
        f"The required-term checks are U1F-neutral `{terms['all_U1F_neutral']}`, Z9-neutral `{terms['all_Z9_neutral']}`, Z4R-target-two `{terms['all_Z4R_target_two']}`, and Z4M-neutral `{terms['all_Z4M_neutral']}`.",
        "",
        f"The witness signature is `{controls['V42_six_matter_witness']['selector_signature']}`.  The familiar four-matter and one-PS-VEV controls remain blocked by the union of the old selectors and Z4M, while the required Dirac operator stays allowed: `{controls['required_Dirac_operator']['selector_signature']}`.",
        "",
        "## Exact limitation",
        "",
        "This does **not** create an anomaly-complete new gauge symmetry.  The prospective U(1)_M parent has base rows `SU4=0`, `SU2L=12`, `SU2R=-12`, `gravity=-3`, `cubic=-3`.  Three residual-preserving left/right doublet pairs can cancel the mixed PS rows, but leave gravity and cubic rows at `-3`; its displayed U(1)_M-U(1)_F cross rows are nonzero as well.  At the Z4M level the necessary even-order screen has `eta=2` and gravitational residue `1`, so the ordinary no-GS screen fails.",
        "",
        f"The general primitive-charge scan through N=96 finds ordinary no-GS necessary-screen orders `{no_go['ordinary_no_GS_orders_passing_necessary_screen']}` and orders that also block the witness `{no_go['orders_that_both_pass_and_block_witness']}`.  The analytic reason is that the three required `NDirac` fields force `A_gravity=-3q`, whereas the witness has charge `-6q`.",
        "",
        "## Bounded operator check",
        "",
        f"Reproducing the V42 stated degree-12 single-epsilon frontier gives `{len(frontier['rows'])}` rows.  Z4M blocks `{frontier['blocked_rows']}` including the degree-ten witness.  The remaining orientation-neutral rows are intentionally not called safe; a full invariant-ring and component analysis is still required.",
        "",
        "A viable escape would have to supply one of the missing UV ingredients explicitly: a quantized GS/inflow or topological sector, an anomaly-carrying light sector with a physical spectrum, or a different nonminimal symmetry realization.  It cannot be inferred from this charge table.  Heavy thresholds and global discrete data matter for that distinction; see [Ibanez](https://arxiv.org/abs/hep-ph/9210211) and [Hsieh](https://arxiv.org/abs/1808.02881).",
        "",
        "G7 remains open.",
        "",
        f"Core SHA-256: `{report['core_sha256']}`",
        "",
    ])


def validate(report: Mapping[str, Any]) -> None:
    if report.get("status") != STATUS or canonical_sha(report) != report.get("core_sha256"):
        raise RuntimeError("stale or invalid V43 Z4M report")
    terms = report["required_term_audit"]
    if not (terms["all_U1F_neutral"] and terms["all_Z9_neutral"] and terms["all_Z4R_target_two"] and terms["all_Z4M_neutral"]):
        raise RuntimeError("required V40/V41 term lost under Z4M")
    rows = {row["label"]: row for row in report["named_B_L_and_required_operator_audit"]}
    if rows["V42_six_matter_witness"]["selector_signature"]["Z4M"] != 2:
        raise RuntimeError("V42 witness is not blocked by the proposed Z4M")
    if not rows["required_Dirac_operator"]["selector_signature"]["allowed_by_new_Z4M"]:
        raise RuntimeError("required Dirac operator was accidentally removed")
    for label in ("left_one_PS_VEV_precursor", "right_one_PS_VEV_precursor", "delta_RPV_control", "bilinear_LH_control"):
        if rows[label]["selector_signature"]["Z4M"] == 0:
            raise RuntimeError(f"lower B/L control {label} was not blocked by Z4M")
    frontier = report["independent_V42_degree12_frontier"]
    if not frontier["witness_row_blocked"] or len(frontier["rows"]) != 6 or frontier["blocked_rows"] != 4:
        raise RuntimeError("V42 frontier reconstruction regressed")
    anomaly = report["continuous_parent_and_discrete_anomaly_boundary"]
    if not anomaly["mixed_PS_rows_cancel"] or not anomaly["continuous_gravity_and_cubic_still_nonzero"]:
        raise RuntimeError("continuous anomaly boundary regression")
    if anomaly["U1M_U1F_product_cross_rows"]["all_vanish"]:
        raise RuntimeError("unjustified product-anomaly completion")
    if anomaly["U1M_U1F_product_cross_rows"]["rows"] != {"C_M_U1F_squared": -27, "C_M_squared_U1F": -9}:
        raise RuntimeError("U1M/U1F cross-row regression")
    low = anomaly["Z4M_low_energy_necessary_screen"]
    if not low["mixed_pass"] or low["gravity_pass"] or low["gravity_residue_mod_eta"] != 1:
        raise RuntimeError("Z4M gravitational no-go regression")
    no_go = report["ordinary_unbroken_selector_no_go"]
    if no_go["ordinary_no_GS_orders_passing_necessary_screen"] != [2, 3, 6] or no_go["orders_that_both_pass_and_block_witness"]:
        raise RuntimeError("ordinary-selector no-go enumeration regressed")
    decision = report["decision"]
    if decision["candidate_is_anomaly_complete_discrete_gauge_symmetry"] or decision["G7_closed"] or decision["gates_promoted"]:
        raise RuntimeError("fail-closed gate boundary violated")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate(report)
    expected_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
    expected_md = render_markdown(report)
    if args.write:
        OUTPUT_JSON.write_text(expected_json, encoding="utf-8")
        OUTPUT_MD.write_text(expected_md, encoding="utf-8")
        print("SUSY V43 Z4M selector repair audit: wrote certificates")
    if args.check:
        if not OUTPUT_JSON.is_file() or not OUTPUT_MD.is_file():
            raise SystemExit("generated certificates missing; run --write")
        if OUTPUT_JSON.read_text(encoding="utf-8") != expected_json or OUTPUT_MD.read_text(encoding="utf-8") != expected_md:
            raise SystemExit("generated certificates stale; run --write")
        print("SUSY V43 Z4M selector repair audit: PASS")
    if not args.write and not args.check:
        print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
