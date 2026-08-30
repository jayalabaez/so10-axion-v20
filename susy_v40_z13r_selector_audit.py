#!/usr/bin/env python3
"""Fail-closed V40 Z13^R high-scale selector audit."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent
OUTPUT_JSON = ROOT / "SUSY_V40_Z13R_SELECTOR_AUDIT.json"
OUTPUT_MD = ROOT / "SUSY_V40_Z13R_SELECTOR_AUDIT.md"
N = 13
W_R = 2
STATUS = "V40_Z13R_HIGH_SCALE_PS_PQ_VEV_RING_BLOCK_AND_TYPE_I_SOURCE_VALIDATED__EW_VEV_DRESSINGS_AND_GS_PRODUCT_UV_OPEN__NO_GATE_PROMOTED"

# dim is the physical Weyl-component multiplicity; z/pq retain the V39
# Z5610/PQ lattice conventions.
FIELDS: dict[str, dict[str, int]] = {
    "H": {"dim": 4, "r": 5, "z": 0, "pq": 0},
    "Q": {"dim": 24, "r": 9, "z": 0, "pq": 0},
    "Qc": {"dim": 24, "r": 1, "z": 0, "pq": 0},
    "X": {"dim": 1, "r": 2, "z": 0, "pq": 0},
    "Zp": {"dim": 1, "r": 2, "z": 0, "pq": 0},
    "Sc": {"dim": 8, "r": 0, "z": 0, "pq": 0},
    "Sbc": {"dim": 8, "r": 0, "z": 0, "pq": 0},
    "SigC": {"dim": 6, "r": 2, "z": 0, "pq": 0},
    "SigBc": {"dim": 6, "r": 2, "z": 0, "pq": 0},
    "PsiBar": {"dim": 8, "r": 6, "z": 5440, "pq": -170},
    "Psi": {"dim": 8, "r": 9, "z": 0, "pq": 0},
    "PsiC": {"dim": 8, "r": 1, "z": 0, "pq": 0},
    "PsiCBar": {"dim": 8, "r": 1, "z": 5440, "pq": -170},
    "P": {"dim": 1, "r": 0, "z": 170, "pq": 170},
    "Pb": {"dim": 1, "r": 0, "z": 5440, "pq": -170},
    "Nv": {"dim": 3, "r": 1, "z": 0, "pq": 0},
    "A2": {"dim": 1, "r": 0, "z": 3211, "pq": -23},
    "A32": {"dim": 1, "r": 2, "z": 2569, "pq": 193},
    "A15": {"dim": 1, "r": 0, "z": 4299, "pq": -57},
    "A17": {"dim": 1, "r": 2, "z": 1141, "pq": -113},
    "A16": {"dim": 1, "r": 1, "z": 5525, "pq": -85},
}
PS_INDEX = {
    "SU4": {"Q": 6, "Qc": 6, "Sc": 2, "Sbc": 2, "SigC": 2, "SigBc": 2, "PsiBar": 2, "Psi": 2, "PsiC": 2, "PsiCBar": 2},
    "SU2L": {"Q": 12, "H": 2, "PsiBar": 4, "Psi": 4},
    "SU2R": {"Qc": 12, "H": 2, "Sc": 4, "Sbc": 4, "PsiC": 4, "PsiCBar": 4},
}
GAUGINO = {"SU4": 8, "SU2L": 4, "SU2R": 4}

RETAINED = (
    ("X",), ("X",), ("Zp",), ("Zp",), ("X", "Sbc", "Sc"), ("X", "P", "Pb"),
    ("Zp", "Sbc", "Sc"), ("Zp", "P", "Pb"), ("Sc", "Sc", "SigC"), ("Sbc", "Sbc", "SigBc"),
    ("Q", "H", "Qc"), ("Q", "H", "PsiC"), ("Psi", "H", "Qc"), ("Psi", "H", "PsiC"),
    ("P", "PsiBar", "Q"), ("P", "PsiBar", "Psi"), ("P", "PsiCBar", "Qc"), ("P", "PsiCBar", "PsiC"),
    ("Sbc", "Qc", "Nv"), ("Sbc", "PsiC", "Nv"), ("Nv", "Nv"),
    ("Pb", "A2", "A32"), ("P", "A15", "A17"), ("P", "A16", "A16"),
)
REMOVED = (
    ("X", "X", "X"), ("X", "X", "Zp"), ("X", "Zp", "Zp"), ("Zp", "Zp", "Zp"),
    ("X", "H", "H"), ("Zp", "H", "H"), ("X", "SigC", "SigBc"), ("Zp", "SigC", "SigBc"),
)


def charge(term: tuple[str, ...]) -> int:
    return sum(FIELDS[item]["r"] for item in term) % N


def sha(payload: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(payload))
    body.pop("core_sha256", None)
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def term_audit() -> dict[str, Any]:
    retained = [{"term": list(t), "R13": charge(t)} for t in RETAINED]
    removed = [{"term": list(t), "R13": charge(t)} for t in REMOVED]
    return {
        "W_target": W_R,
        "retained_term_count": len(RETAINED),
        "retained": retained,
        "removed_V39": removed,
        "all_retained_allowed": all(x["R13"] == W_R for x in retained),
        "all_removed_forbidden": all(x["R13"] != W_R for x in removed),
        "rebuild_required": "R13 forbids the V39 driver self-cubics, X/Zp H^2 and X/Zp SigC SigBc. A new W/K/vacuum and electroweak-doublet source is required.",
    }


def ring_audit() -> dict[str, Any]:
    rows = []
    for driver in ("X", "Zp"):
        for matter in ("Q", "Qc"):
            r = charge((driver, matter, matter, matter, matter))
            rows.append({"operator": f"{driver} {matter}^4", "R13": r, "forbidden": r != W_R})
    qc_witness = charge(("X", "Qc", "Sbc", "Qc", "Sbc", "Qc", "Sbc", "Qc", "Sbc"))
    ew = [
        {"operator": "X Q^4 (H.H)^12 / M^25", "R13": (charge(("X", "Q", "Q", "Q", "Q")) + 12 * charge(("H", "H"))) % N, "EWSB_factor": "(v/M)^24"},
        {"operator": "X Qc^4 (H.H)^10 / M^21", "R13": (charge(("X", "Qc", "Qc", "Qc", "Qc")) + 10 * charge(("H", "H"))) % N, "EWSB_factor": "(v/M)^20"},
    ]
    return {
        "high_scale_VEV_branch": {"nonzero": ["Sc", "Sbc", "P", "Pb"], "zero": ["X", "Zp", "SigC", "SigBc", "H"], "R13_nonzero_VEVs": {x: FIELDS[x]["r"] for x in ("Sc", "Sbc", "P", "Pb")}},
        "proof": "All high-scale VEV insertions have R13=0, so they cannot change a holomorphic operator charge.",
        "pure_same_orientation_classes": rows,
        "all_four_blocked_on_high_scale_branch": all(x["forbidden"] for x in rows),
        "V39_Qc4_dressing_retested": {"operator": "X [epsilon_SU2R delta_SU4 (Qc Sbc)]^4 / M^6", "R13": qc_witness, "forbidden": qc_witness != W_R},
        "EW_VEV_counterexamples": ew,
        "literal_all_VEV_ring_block": False,
        "scope": "The proof covers PS/PQ high-scale VEV dressings. R13(H)=5 means EWSB breaks the selector; the displayed H.H dressings are allowed and preclude a literal all-VEV/G7 closure.",
    }


def anomaly_audit() -> dict[str, Any]:
    chiral = {g: sum(PS_INDEX[g].get(name, 0) * (row["r"] - 1) for name, row in FIELDS.items()) for g in PS_INDEX}
    doubled = {g: chiral[g] + GAUGINO[g] for g in chiral}
    standard = {g: doubled[g] // 2 for g in doubled}
    rho = next(iter(standard.values())) % N
    gravity = sum(row["dim"] * (row["r"] - 1) for row in FIELDS.values()) + 21 - 21
    return {
        "formula": "A_G^R=sum T(R_i)(r_i-1)+T(adj); doubled=2 A_G. A_grav=sum dim(R_i)(r_i-1)+21-21 in PS-only N=1 bookkeeping.",
        "doubled_total": doubled,
        "standard_A": standard,
        "standard_A_mod13": {g: x % N for g, x in standard.items()},
        "GS_rho_mod13": rho,
        "mixed_GS_universal": len({x % N for x in standard.values()}) == 1,
        "gravity_A": gravity,
        "gravity_A_mod13": gravity % N,
        "24rho_mod13": (24 * rho) % N,
        "gravity_GS_relation": gravity % N == (24 * rho) % N,
        "Witten_doublets": {"SU2L": 22, "SU2R": 30},
        "UV_boundary": "This is necessary discrete-R/GS arithmetic only. A quantized axion period and Wess-Zumino action, full Spin^Z13R x G_PS x Z5610 bordism, heavy thresholds, and a microscopic origin remain absent.",
    }


@lru_cache(maxsize=2)
def quality_bound(kahler: bool) -> int | None:
    """Exact (Z5610,R13,PQ) lower-bound search; gauge contractions omitted."""
    unique: list[tuple[str, int, int, int]] = []
    seen: set[tuple[int, int, int]] = set()
    for name, row in FIELDS.items():
        item = (name, row["z"] % 5610, row["r"] % N, row["pq"])
        if item[1:] not in seen:
            seen.add(item[1:])
            unique.append(item)
    items = list(unique)
    if kahler:
        items += [(name + "dag", (-z) % 5610, (-r) % N, -pq) for name, z, r, pq in unique]
    target = 0 if kahler else W_R
    states: set[tuple[int, int, int]] = {(0, 0, 0)}
    for degree in range(1, 34):
        next_states: set[tuple[int, int, int]] = set()
        for z, r, pq in states:
            for _, iz, ir, ipq in items:
                next_states.add(((z + iz) % 5610, (r + ir) % N, pq + ipq))
        states = next_states
        if any(z == 0 and r == target and pq != 0 for z, r, pq in states):
            return degree
    return None


def quality_audit() -> dict[str, Any]:
    return {
        "W_charge_lattice_lower_bound": quality_bound(False),
        "Kahler_charge_lattice_lower_bound": quality_bound(True),
        "gauge_singlet_W_upper_witness": {"operator": "X P^33", "degree": 34, "Z5610": 0, "R13": 2, "PQ_numerator_over_170": 5610},
        "scope": "No state below the quoted degree exists even before imposing gauge contractions, hence the bounds are conservative. They are not a complete gravitational/PQ-quality proof.",
    }


def comparison() -> dict[str, Any]:
    return {
        "U1F_to_Z9": "A U1F parent can block the pure same-orientation ring after every residual-neutral VEV insertion, but q(ND)=-3 gives 2q(ND)+9k=0 with no integer k: it is Dirac-neutrino only without a material neutrino rebuild.",
        "Z13R": "Sbc Qc Nv and Nv^2 both have R13=2, evading that ordinary-additive type-I obstruction on the high-scale neutral-VEV branch. Its H charge creates explicit EWSB-dressed counterexamples and it still lacks a GS/product-bordism/source completion.",
        "result": "Neither route closes G1 or G7; the two routes expose complementary design constraints.",
    }


def build_report() -> dict[str, Any]:
    report: dict[str, Any] = {
        "status": STATUS,
        "scope": "Conditional PS x Z5610 x Z13R source boundary; no active SARAH model, K/W/f solution, spectrum, or likelihood.",
        "R13_charges": {name: row["r"] for name, row in FIELDS.items()},
        "terms": term_audit(),
        "ring": ring_audit(),
        "necessary_R_anomalies": anomaly_audit(),
        "PQ_quality": quality_audit(),
        "comparison_to_U1F_Z9": comparison(),
        "decision": {"high_scale_pure_Q4_Qc4_block": True, "type_I_source_present": True, "all_VEV_ring_block": False, "quantized_GS_product_bordism_complete": False, "complete_V40_source": False, "gates_promoted": []},
    }
    report["core_sha256"] = sha(report)
    return report


def markdown(data: Mapping[str, Any]) -> str:
    ring = data["ring"]
    anomaly = data["necessary_R_anomalies"]
    quality = data["PQ_quality"]
    lines = [
        "# V40 Z13R high-scale selector audit", "", f"Status: `{data['status']}`", "",
        "This is a conditional 4D source-boundary result, not a complete theory or active spectrum source.", "",
        "## High-scale result", "",
        "All retained driver, Pati--Salam, Yukawa, vectorlike-mixing, type-I seesaw and anomalon terms have R13=2. The V39 driver self-cubics, X/Zp H^2 and X/Zp SigC SigBc terms are R-forbidden, so a new source/vacuum is mandatory.", "",
        f"On the canonical high-scale branch Sc, Sbc, P and Pb have R13=0. The pure classes are `{[(x['operator'], x['R13']) for x in ring['pure_same_orientation_classes']]}`; none has W charge two. The former V39 Qc4 VEV witness has R13={ring['V39_Qc4_dressing_retested']['R13']} and is forbidden.", "",
        "## Fail-closed boundary", "",
        f"H has R13=5, so EWSB breaks the selector. Allowed counterexamples are `{[x['operator'] for x in ring['EW_VEV_counterexamples']]}`. Their EWSB factors are `{[x['EWSB_factor'] for x in ring['EW_VEV_counterexamples']]}`. Therefore no literal all-VEV operator-ring or G7 closure is claimed.", "",
        "## Necessary anomaly and PQ arithmetic", "",
        f"The conventional mixed rows are A_G={anomaly['standard_A']}, universal rho={anomaly['GS_rho_mod13']} mod 13. The displayed gravity relation is {anomaly['gravity_A_mod13']}=24 rho mod 13. This is only necessary Green--Schwarz arithmetic; its quantized realization and product bordism are not supplied.", "",
        f"Conservative charge-lattice PQ lower bounds are W degree {quality['W_charge_lattice_lower_bound']} and Kahler degree {quality['Kahler_charge_lattice_lower_bound']}.", "",
        "For discrete-R/Green--Schwarz context: [Araki et al.](https://arxiv.org/abs/0705.3075), [Dine--Monteux](https://arxiv.org/abs/1212.4371).", "",
        f"Core SHA-256: `{data['core_sha256']}`",
    ]
    return "\n".join(lines) + "\n"


def validate(data: Mapping[str, Any]) -> None:
    if data.get("status") != STATUS or sha(data) != data.get("core_sha256"):
        raise RuntimeError("stale report")
    if not data["terms"]["all_retained_allowed"] or not data["terms"]["all_removed_forbidden"]:
        raise RuntimeError("term charge failure")
    ring = data["ring"]
    if not ring["all_four_blocked_on_high_scale_branch"] or not ring["V39_Qc4_dressing_retested"]["forbidden"]:
        raise RuntimeError("high-scale ring failure")
    if not all(x["R13"] == W_R for x in ring["EW_VEV_counterexamples"]):
        raise RuntimeError("EW counterexample missing")
    anomaly = data["necessary_R_anomalies"]
    if not anomaly["mixed_GS_universal"] or not anomaly["gravity_GS_relation"]:
        raise RuntimeError("necessary GS arithmetic failure")
    if data["PQ_quality"]["W_charge_lattice_lower_bound"] != 33 or data["PQ_quality"]["Kahler_charge_lattice_lower_bound"] != 32:
        raise RuntimeError("quality lower-bound regression")
    if data["decision"]["all_VEV_ring_block"] or data["decision"]["quantized_GS_product_bordism_complete"]:
        raise RuntimeError("fail-closed status promoted")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = build_report()
    validate(data)
    text = markdown(data)
    if args.write:
        OUTPUT_JSON.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        OUTPUT_MD.write_text(text, encoding="utf-8")
        print("SUSY V40 Z13R selector audit: wrote certificates")
    if args.check:
        if not OUTPUT_JSON.exists() or not OUTPUT_MD.exists():
            raise SystemExit("generated certificates missing; run --write")
        if OUTPUT_JSON.read_text(encoding="utf-8") != json.dumps(data, indent=2, sort_keys=True) + "\n" or OUTPUT_MD.read_text(encoding="utf-8") != text:
            raise SystemExit("generated certificates stale; run --write")
        print("SUSY V40 Z13R selector audit: PASS")


if __name__ == "__main__":
    main()
