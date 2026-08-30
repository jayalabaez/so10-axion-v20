#!/usr/bin/env python3
"""Fail-closed V39 audit of the split-six baryon-operator repair.

V37 has one PS six.  Any added ordinary additive selector that preserves its
displayed driver, Yukawa and seesaw terms leaves the X/Zp-dressed Q^4 sources
neutral.  V39 changes precisely that structural premise: it splits the six
into SigC and SigBc, then uses a minimal Z3 selector.  This program checks the
charge arithmetic, necessary finite-anomaly residues, and the narrow claims
that actually follow.  It deliberately does not convert a source-level
selection rule into a proton lifetime or flavour fit.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parent
MODEL_NAME = "PSZ4RZ5610Z3SUSYV39"
MODEL_DIR = ROOT / "models" / MODEL_NAME
MODEL = MODEL_DIR / f"{MODEL_NAME}.m"
PARAMETERS = MODEL_DIR / "parameters.m"
PARTICLES = MODEL_DIR / "particles.m"
README = MODEL_DIR / "README.md"
VALIDATOR = ROOT / "tools" / "validate-susy-v39-baryon-repair.wls"
TEST = ROOT / "test_susy_v39_g7_g8_architecture.py"
OUTPUT_JSON = ROOT / "SUSY_V39_G7_G8_ARCHITECTURE.json"
OUTPUT_MD = ROOT / "SUSY_V39_G7_G8_ARCHITECTURE.md"

STATUS = (
    "V39_SPLIT_SIX_Z3_LOCAL_SOURCE_BLOCK_VALIDATED__DEGREE9_QC4_VEV_"
    "DRESSING_EXPLICIT__G7_AND_G8_OPEN"
)

# Physical Weyl-component multiplicity, plus the V37 Z5610 and V39 selector
# charge representatives.  The doubled Dynkin coefficients below already
# include family and spectator dimensions, so keep them separately.
FIELDS: dict[str, dict[str, int]] = {
    "H": {"dim": 4, "z3": 0, "z5610": 0, "r4": 0, "pq": 0},
    "Q": {"dim": 24, "z3": 1, "z5610": 0, "r4": 1, "pq": 0},
    "Qc": {"dim": 24, "z3": 2, "z5610": 0, "r4": 1, "pq": 0},
    "X": {"dim": 1, "z3": 0, "z5610": 0, "r4": 2, "pq": 0},
    "Sc": {"dim": 8, "z3": 2, "z5610": 0, "r4": 0, "pq": 0},
    "Sbc": {"dim": 8, "z3": 1, "z5610": 0, "r4": 0, "pq": 0},
    "SigC": {"dim": 6, "z3": 2, "z5610": 0, "r4": 2, "pq": 0},
    "SigBc": {"dim": 6, "z3": 1, "z5610": 0, "r4": 2, "pq": 0},
    "PsiBar": {"dim": 8, "z3": 2, "z5610": 5440, "r4": 3, "pq": -170},
    "Psi": {"dim": 8, "z3": 1, "z5610": 0, "r4": 1, "pq": 0},
    "PsiC": {"dim": 8, "z3": 2, "z5610": 0, "r4": 1, "pq": 0},
    "PsiCBar": {"dim": 8, "z3": 1, "z5610": 5440, "r4": 3, "pq": -170},
    "P": {"dim": 1, "z3": 0, "z5610": 170, "r4": 2, "pq": 170},
    "Nv": {"dim": 3, "z3": 0, "z5610": 0, "r4": 1, "pq": 0},
    "Pb": {"dim": 1, "z3": 0, "z5610": 5440, "r4": 2, "pq": -170},
    "Zp": {"dim": 1, "z3": 0, "z5610": 0, "r4": 2, "pq": 0},
    "A2": {"dim": 1, "z3": 1, "z5610": 3211, "r4": 0, "pq": -23},
    "A32": {"dim": 1, "z3": 2, "z5610": 2569, "r4": 0, "pq": 193},
    "A15": {"dim": 1, "z3": 0, "z5610": 4299, "r4": 2, "pq": -57},
    "A17": {"dim": 1, "z3": 0, "z5610": 1141, "r4": 2, "pq": -113},
    "A16": {"dim": 1, "z3": 0, "z5610": 5525, "r4": 0, "pq": -85},
}

# Coefficients are 2 T(r) times all other gauge and family multiplicities.
PS_DOUBLED_DYNKIN: dict[str, dict[str, int]] = {
    "SU4": {
        "Q": 6, "Qc": 6, "Sc": 2, "Sbc": 2, "SigC": 2, "SigBc": 2,
        "PsiBar": 2, "Psi": 2, "PsiC": 2, "PsiCBar": 2,
    },
    "SU2L": {"Q": 12, "H": 2, "PsiBar": 4, "Psi": 4},
    "SU2R": {"Qc": 12, "H": 2, "Sc": 4, "Sbc": 4, "PsiC": 4, "PsiCBar": 4},
}

TERMS: tuple[tuple[str, ...], ...] = (
    ("X",), ("X",), ("Zp",), ("Zp",),
    ("X", "Sbc", "Sc"), ("X", "P", "Pb"),
    ("Zp", "Sbc", "Sc"), ("Zp", "P", "Pb"),
    ("X", "X", "X"), ("X", "X", "Zp"), ("X", "Zp", "Zp"), ("Zp", "Zp", "Zp"),
    ("X", "H", "H"), ("X", "SigC", "SigBc"),
    ("Zp", "H", "H"), ("Zp", "SigC", "SigBc"),
    ("Sc", "Sc", "SigC"), ("Sbc", "Sbc", "SigBc"),
    ("Q", "H", "Qc"), ("Q", "H", "PsiC"),
    ("Psi", "H", "Qc"), ("Psi", "H", "PsiC"),
    ("P", "PsiBar", "Q"), ("P", "PsiBar", "Psi"),
    ("P", "PsiCBar", "Qc"), ("P", "PsiCBar", "PsiC"),
    ("Sbc", "Qc", "Nv"), ("Sbc", "PsiC", "Nv"), ("Nv", "Nv"),
    ("Pb", "A2", "A32"), ("P", "A15", "A17"), ("P", "A16", "A16"),
)

LOCAL_DANGEROUS = (
    ("X", "Q", "Q", "Q", "Q"),
    ("X", "Qc", "Qc", "Qc", "Qc"),
    ("Zp", "Q", "Q", "Q", "Q"),
    ("Zp", "Qc", "Qc", "Qc", "Qc"),
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(payload: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(payload))
    body.pop("core_sha256", None)
    data = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def q(term: Iterable[str], key: str, modulus: int) -> int:
    return sum(FIELDS[name][key] for name in term) % modulus


def hsieh_audit(order: int) -> dict[str, int | bool]:
    linear = sum(row["dim"] * row["z3"] for row in FIELDS.values())
    cubic = sum(row["dim"] * row["z3"] ** 3 for row in FIELDS.values())
    coefficient = order * order + 3 * order + 2
    return {
        "order": order,
        "Delta_s1_canonical": linear,
        "Delta_s3_canonical": cubic,
        "linear_condition_2Delta_s1_mod_n": (2 * linear) % order,
        "cubic_condition_mod_6n": (coefficient * cubic) % (6 * order),
        "both_vanish": (2 * linear) % order == 0 and (coefficient * cubic) % (6 * order) == 0,
    }


def source_contract() -> dict[str, Any]:
    text = MODEL.read_text(encoding="utf-8")
    required = {
        "two_globals": "Global[[2]] = {Z[3], V39BaryonSelector};",
        "split_six_fields": "{SigC," in text and "{SigBc," in text,
        "split_driver_terms": "lambdaXSig*X.SigC.SigBc" in text and "lambdaZSig*Zp.SigC.SigBc" in text,
        "split_PS_terms": "lambdaSc/2*Sc.Sc.SigC" in text and "lambdaSbc/2*Sbc.Sbc.SigBc" in text,
        "seesaw_source": "yNQ*Sbc.Qc.Nv" in text and "MN/2*Nv.Nv" in text,
        "all_soft_flags_disabled": all(
            token in text
            for token in ("AddSoftTerms = False;", "AddSoftScalarMasses = False;", "AddSoftGauginoMasses = False;")
        ),
    }
    absent_old = all(token not in text for token in ("Sig6.Sig6", "Sc.Sc.Sig6", "Sbc.Sbc.Sig6"))
    return {
        "model_name": MODEL_NAME,
        "field_count": len(FIELDS),
        "declared_W_term_count": len(TERMS),
        "required_source_fragments_present": required,
        "old_single_six_W_fragments_absent": absent_old,
        "all_static_checks_pass": all(required.values()) and absent_old,
        "SARAH_runtime_validator": {
            "path": VALIDATOR.relative_to(ROOT).as_posix(),
            "command": (
                "wolframscript -file tools/validate-susy-v39-baryon-repair.wls "
                "--repo-root . --sarah-root <SARAH-4.15.3-root>"
            ),
            "scope": (
                "parses and loads the model, checks its 32-term structural multiset, both selector charges, "
                "the four local forbidden sources, and continuous gauge anomalies"
            ),
        },
    }


def old_single_six_no_go() -> dict[str, Any]:
    return {
        "scope": (
            "any additional ordinary additive Abelian selector preserving the displayed V37 terms; "
            "the linear driver parameters are neutral spurions"
        ),
        "variables": {"s": "q(Sc)", "sb": "q(Sbc)", "sigma": "q(Sig6)", "h": "q(H)", "n": "q(Nv)"},
        "input_equations": [
            "q(X)=q(Zp)=0 from their linear driver terms",
            "sb+s=0 from X Sbc Sc",
            "2s+sigma=0 from Sc^2 Sig6",
            "2sb+sigma=0 from Sbc^2 Sig6",
            "2h=0 from X H^2; 2n=0 from Nv^2",
            "sb+q(Qc)+n=0 from Sbc Qc Nv",
            "q(Q)+h+q(Qc)=0 from Q H Qc",
        ],
        "deduction": [
            "sigma=-2s=2s, hence 4s=0",
            "q(Qc)=s-n and q(Q)=-h-s+n",
            "4q(Q)=4q(Qc)=0 using 2h=2n=4s=0",
            "therefore X Q^4, X Qc^4, Zp Q^4, and Zp Qc^4 are selector-neutral",
        ],
        "conclusion": (
            "A new ordinary additive selector alone cannot repair the unsplit V37 architecture. "
            "The V39 split removes the equation that forced 4s=0."
        ),
    }


def minimal_selector_search() -> dict[str, Any]:
    """Enumerate all odd orders through 99 under retained-term relations.

    With q=q(Q), p=q(P), the retained terms fix the other core charges.  The
    displayed PS mixed-anomaly cancellation congruences are imposed directly.
    This is an exact finite search, not an assertion about UV anomaly inflow.
    """

    solutions: list[dict[str, int]] = []
    for order in range(3, 100, 2):
        for charge_q in range(1, order):
            for charge_p in range(order):
                charges = {
                    "Q": charge_q,
                    "Qc": -charge_q,
                    "Sc": -charge_q,
                    "Sbc": charge_q,
                    "SigC": 2 * charge_q,
                    "SigBc": -2 * charge_q,
                    "PsiBar": -charge_p - charge_q,
                    "Psi": charge_q,
                    "PsiC": -charge_q,
                    "PsiCBar": -charge_p + charge_q,
                    "P": charge_p,
                    "Pb": -charge_p,
                }
                residues = {
                    group: sum(PS_DOUBLED_DYNKIN[group].get(name, 0) * value for name, value in charges.items()) % order
                    for group in PS_DOUBLED_DYNKIN
                }
                if any(residues.values()):
                    continue
                direct = (4 * charge_q) % order
                if direct == 0:
                    continue
                solutions.append({"order": order, "q_Q": charge_q, "q_P": charge_p, "direct_charge": direct})
    minimum = min(row["order"] for row in solutions)
    return {
        "assumptions": "odd-order ordinary selector; all retained core terms; vanishing standard PS mixed residues modulo N",
        "searched_odd_orders": [3, 99],
        "solution_count": len(solutions),
        "minimum_order": minimum,
        "minimum_solutions": [row for row in solutions if row["order"] == minimum],
        "analytic_reduction": (
            "The mixed residues are A4=-4p, AL=4(3q-p), AR=-4(3q+p). "
            "For odd N this gives p=0 and 3q=0. A nonzero q with 4q!=0 first occurs at N=3."
        ),
    }


def selector_and_anomaly_audit() -> dict[str, Any]:
    ps_raw = {
        group: sum(PS_DOUBLED_DYNKIN[group].get(name, 0) * row["z3"] for name, row in FIELDS.items())
        for group in PS_DOUBLED_DYNKIN
    }
    cross_rows = [row for row in FIELDS.values() if row["z5610"]]
    cross_z3_z5610_squared = sum(row["dim"] * row["z3"] * row["z5610"] ** 2 for row in cross_rows)
    cross_z3_squared_z5610 = sum(row["dim"] * row["z3"] ** 2 * row["z5610"] for row in cross_rows)
    term_charges = [
        {"term": list(term), "Z3": q(term, "z3", 3), "Z4R": q(term, "r4", 4)}
        for term in TERMS
    ]
    local = [
        {"operator": " ".join(term), "Z3": q(term, "z3", 3), "Z4R": q(term, "r4", 4)}
        for term in LOCAL_DANGEROUS
    ]
    return {
        "V39_Z3_charge_table": {name: row["z3"] for name, row in FIELDS.items()},
        "all_displayed_W_terms_Z3_neutral": all(row["Z3"] == 0 for row in term_charges),
        "all_displayed_W_terms_external_Z4R_charge_two": all(row["Z4R"] == 2 for row in term_charges),
        "dangerous_local_sources": local,
        "all_four_local_sources_forbidden": all(row["Z3"] != 0 for row in local),
        "pure_Z3_Hsieh_Dai_Freed_convention": hsieh_audit(3),
        "mixed_PS_Z3_standard_doubled_Dynkin": {
            "raw_nonnegative_representative_sums": ps_raw,
            "residues_mod_3": {group: value % 3 for group, value in ps_raw.items()},
            "all_vanish_mod_3": all(value % 3 == 0 for value in ps_raw.values()),
        },
        "necessary_Z3_Z5610_cross_residues": {
            "C_Z3_Z5610_squared_raw": cross_z3_z5610_squared,
            "C_Z3_Z5610_squared_mod_3": cross_z3_z5610_squared % 3,
            "C_Z3_squared_Z5610_raw": cross_z3_squared_z5610,
            "C_Z3_squared_Z5610_mod_3": cross_z3_squared_z5610 % 3,
            "qualification": (
                "These two raw residues are necessary consistency checks, not a complete classification of "
                "Z5610 x Z3 product bordism, discrete-R, heavy-threshold, or Green--Schwarz data."
            ),
        },
        "anomalon_choice_reason": (
            "A2,A32=(1,2) and A15,A17=(0,0) preserve the three V37 anomalon mass terms while setting both listed cross residues to zero modulo 3."
        ),
    }


def canonical_branch_and_quality() -> dict[str, Any]:
    w_quality = state_space_first_PQ_breaking(kahler=False, max_degree=33)
    k_quality = state_space_first_PQ_breaking(kahler=True, max_degree=33)
    attainment = quality_attainment_witnesses()
    return {
        "canonical_global_SUSY_scope": "same canonical global-N=1 truncation as V37; no Kähler/soft completion",
        "generic_driver_solution": ["<Sbc Sc>=vPS^2", "<P Pb>=fPQ^2"],
        "representative": ["<X>=<Zp>=<SigC>=<SigBc>=0", "<Sc>,<Sbc> are equal-conjugate PS breaking VEVs", "<P>,<Pb> are PQ VEVs"],
        "why_split_six_F_terms_vanish_on_that_representative": (
            "The F_SigC and F_SigBc contractions contain the same two-identical-PS-spinor 6 projection that vanishes on the rank-one equal-conjugate VEV representative; the driver-sigma terms vanish because X=Zp=0."
        ),
        "not_a_full_vacuum_proof": ["Kähler metric", "soft terms", "competing branches", "tunnelling", "cosmological selection"],
        "fresh_V39_charge_lattice_enumeration": {
            "tracked_constraints": ["Z5610", "Z4R", "Z3", "PQ numerator / 170"],
            "superpotential": w_quality,
            "Kahler": k_quality,
            "gauge_singlet_attainment_witnesses": attainment,
            "exact_W33_K32_equalities_established": (
                w_quality["first_breaking_degree"] == 33
                and k_quality["first_breaking_degree"] == 32
                and attainment["both_are_exact_breaking_gauge_singlets"]
            ),
            "result": (
                f"fresh active-V39 enumeration gives first W breaking degree {w_quality['first_breaking_degree']} "
                f"and first Kahler breaking degree {k_quality['first_breaking_degree']}"
            ),
            "qualification": (
                "This is a gauge-contraction-independent charge-lattice lower bound. It is not a full "
                "quantum-gravity quality proof or a classification of every non-polynomial effect."
            ),
        },
    }


def quality_attainment_witnesses() -> dict[str, Any]:
    """Exhibit gauge-singlet monomials attaining the lattice lower bounds."""

    def audit(multiplicities: Mapping[str, int], *, kahler: bool) -> dict[str, Any]:
        totals = {"Z5610": 0, "Z4R": 0, "Z3": 0, "PQ": 0}
        degree = 0
        for label, multiplicity in multiplicities.items():
            dagger = label.endswith("dag")
            name = label[:-3] if dagger else label
            sign = -1 if dagger else 1
            row = FIELDS[name]
            degree += multiplicity
            totals["Z5610"] += sign * multiplicity * row["z5610"]
            totals["Z4R"] += sign * multiplicity * row["r4"]
            totals["Z3"] += sign * multiplicity * row["z3"]
            totals["PQ"] += sign * multiplicity * row["pq"]
        residues = {
            "Z5610": totals["Z5610"] % 5610,
            "Z4R": totals["Z4R"] % 4,
            "Z3": totals["Z3"] % 3,
            "PQ_numerator_over_170": totals["PQ"],
        }
        target_r4 = 0 if kahler else 2
        return {
            "multiplicities": dict(multiplicities),
            "degree": degree,
            "residues": residues,
            "all_fields_are_PS_singlets": all(
                (label[:-3] if label.endswith("dag") else label)
                in {"X", "P", "Nv", "Pb", "Zp", "A2", "A32", "A15", "A17", "A16"}
                for label in multiplicities
            ),
            "is_exact_PQ_breaking_invariant": (
                residues["Z5610"] == 0
                and residues["Z4R"] == target_r4
                and residues["Z3"] == 0
                and residues["PQ_numerator_over_170"] != 0
            ),
        }

    w = audit({"P": 33}, kahler=False)
    k = audit({"P": 6, "A32": 21, "A16dag": 1, "A17dag": 4}, kahler=True)
    return {
        "W_degree_33": w,
        "Kahler_degree_32": k,
        "both_are_exact_breaking_gauge_singlets": (
            w["degree"] == 33
            and k["degree"] == 32
            and w["all_fields_are_PS_singlets"]
            and k["all_fields_are_PS_singlets"]
            and w["is_exact_PQ_breaking_invariant"]
            and k["is_exact_PQ_breaking_invariant"]
        ),
    }


@lru_cache(maxsize=4)
def state_space_first_PQ_breaking(*, kahler: bool, max_degree: int) -> dict[str, Any]:
    """Enumerate the active V39 exact-charge lattice through ``max_degree``.

    The split sixes cannot inherit the V37 proof by deletion because their Z3
    and R charges are nontrivial.  This dynamic program therefore includes the
    actual Z3 charge in every state and produces a reproducible witness.
    Gauge invariance is deliberately not imposed, so the result is a
    conservative lower bound: adding gauge constraints cannot lower it.
    """

    base = [
        (name, row["z5610"] % 5610, row["r4"] % 4, row["z3"] % 3, row["pq"])
        for name, row in FIELDS.items()
    ]
    unique: list[tuple[str, int, int, int, int]] = []
    seen: set[tuple[int, int, int, int]] = set()
    for item in base:
        signature = item[1:]
        if signature not in seen:
            seen.add(signature)
            unique.append(item)
    items = list(unique)
    if kahler:
        items.extend(
            (
                f"{name}dag",
                (-z5610) % 5610,
                (-r4) % 4,
                (-z3) % 3,
                -pq,
            )
            for name, z5610, r4, z3, pq in unique
        )

    states: dict[tuple[int, int, int, int], tuple[int, ...]] = {
        (0, 0, 0, 0): (0,) * len(items)
    }
    target_r4 = 0 if kahler else 2
    state_counts: list[int] = []
    for degree in range(1, max_degree + 1):
        next_states: dict[tuple[int, int, int, int], tuple[int, ...]] = {}
        for (z5610, r4, z3, pq), counts in states.items():
            for index, (_name, iz5610, ir4, iz3, ipq) in enumerate(items):
                state = (
                    (z5610 + iz5610) % 5610,
                    (r4 + ir4) % 4,
                    (z3 + iz3) % 3,
                    pq + ipq,
                )
                if state not in next_states:
                    updated = list(counts)
                    updated[index] += 1
                    next_states[state] = tuple(updated)
        states = next_states
        state_counts.append(len(states))
        for (z5610, r4, z3, pq), counts in states.items():
            if z5610 == 0 and r4 == target_r4 and z3 == 0 and pq != 0:
                return {
                    "search_max_degree": max_degree,
                    "first_breaking_degree": degree,
                    "witness_multiplicities": {
                        items[index][0]: count for index, count in enumerate(counts) if count
                    },
                    "witness_PQ_charge_numerator_over_170": pq,
                    "reachable_state_counts": state_counts,
                }
    return {
        "search_max_degree": max_degree,
        "first_breaking_degree": None,
        "witness_multiplicities": None,
        "witness_PQ_charge_numerator_over_170": None,
        "reachable_state_counts": state_counts,
    }


def restricted_q4_dressing_result() -> dict[str, Any]:
    return {
        "scope": (
            "holomorphic operators with exactly four Q fields, arbitrary canonical-branch Sc/Sbc/P/Pb insertions, "
            "and rank-one Sc/Sbc PS VEVs; it excludes Qc, other heavy fields, conjugates/Kahler terms, and deformed soft vacua"
        ),
        "SU4_counting": "For a=n(Sc), b=n(Sbc), SU(4) invariance requires Delta=4+b-a=4k.",
        "Z3_counting": "q_Z3(X Q^4 Sc^a Sbc^b)=1-a+b=Delta-3=4k-3. Neutrality requires k=0 mod 3.",
        "rank_one_consequence": (
            "For k=0 mod 3, a-b=4-4k is never zero (k=1 would be required). After opposite-type SU(2)_R pairings, a nonzero even surplus of identical Sc or Sbc VEVs remains. Every such pair contains epsilon(v,v)=0, so the VEV insertion vanishes."
        ),
        "result": "No such canonical-branch holomorphic PS-VEV dressing generates X Q^4; replacing X by Zp changes no selector charge.",
        "mirror_limit": (
            "The analogous Qc^4 statement is not claimed: Qc itself carries SU(2)_R indices and can absorb VEV indices, so a separate component/ring calculation is required."
        ),
    }


def explicit_qc4_dressing_witness() -> dict[str, Any]:
    """Return an allowed canonical-VEV dressing missed by the local-source test.

    Qc and Sbc carry conjugate SU(4) representations and are both SU(2)R
    doublets, so their delta/epsilon contraction is a PS singlet.  This is a
    ring counterexample, not by itself a proton-decay matrix element: the
    standard rank-one Sbc VEV selects a particular Qc component.
    """

    pair = ("Qc", "Sbc")
    operator_x = ("X",) + pair * 4
    operator_zp = ("Zp",) + pair * 4
    rows = [
        {
            "operator": "X [epsilon_SU2R delta_SU4 (Qc Sbc)]^4 / M^6",
            "chiral_degree": len(operator_x),
            "Z3": q(operator_x, "z3", 3),
            "Z4R": q(operator_x, "r4", 4),
            "Z5610": q(operator_x, "z5610", 5610),
            "PQ": sum(FIELDS[name]["pq"] for name in operator_x),
        },
        {
            "operator": "Zp [epsilon_SU2R delta_SU4 (Qc Sbc)]^4 / M^6",
            "chiral_degree": len(operator_zp),
            "Z3": q(operator_zp, "z3", 3),
            "Z4R": q(operator_zp, "r4", 4),
            "Z5610": q(operator_zp, "z5610", 5610),
            "PQ": sum(FIELDS[name]["pq"] for name in operator_zp),
        },
    ]
    return {
        "PS_singlet_pair": "B = epsilon^(alpha beta) (Qc)_(i alpha) (Sbc)^(i)_(beta)",
        "why_gauge_invariant": "Qc x Sbc contracts with the SU4 delta and SU2R epsilon; B is a PS singlet.",
        "operators": rows,
        "both_selectors_allow_both_operators": all(
            row["Z3"] == 0 and row["Z4R"] == 2 and row["Z5610"] == 0 and row["PQ"] == 0
            for row in rows
        ),
        "after_canonical_PSVev": (
            "Replacing four Sbc fields by the rank-one PS-breaking VEV generically gives X Qc^4 or Zp Qc^4. "
            "Each VEV is paired with a dynamical Qc, so no epsilon(v,v)=0 identity removes it."
        ),
        "qualification": (
            "The standard SM-singlet Sbc VEV selects a particular Qc component. This disproves an all-ring "
            "algebraic protection claim but does not alone establish a proton-decay amplitude; component, flavour, "
            "SUSY-dressing, and hadronic matching remain required."
        ),
        "conclusion": "The Z3 blocks the four local degree-five sources but is spontaneously broken by the PS VEV and does not protect the full Qc^4 operator ring.",
    }


def gate_statuses() -> list[dict[str, Any]]:
    return [
        {
            "gate": "G7",
            "full_gate_closed": False,
            "landed": [
                "all four local X/Zp Q^4/Qc^4 source monomials are Z3-forbidden",
                "a narrow all-order canonical-branch holomorphic Q^4 PS-VEV-dressing result",
                "an explicit allowed degree-nine X/Zp (Qc Sbc)^4 canonical-VEV dressing that proves the full ring remains open",
            ],
            "still_required": [
                "full Qc^4 and mixed heavy-field operator ring", "Kahler/soft spurion operators and the deformed vacuum", "component spectrum, Wilson matching, SUSY dressing and RG", "flavour tensors and hadronic matrix elements",
            ],
        },
        {
            "gate": "G8",
            "full_gate_closed": False,
            "landed": [
                "YQQ Q H Qc and vectorlike-mixing source terms remain allowed",
                "Sbc Qc Nv plus MN Nv^2 remains allowed, retaining type-I seesaw capacity",
            ],
            "still_required": [
                "a derived flavour texture or UV flavour sector", "charged-fermion and neutrino fit", "threshold/RG evolution with a spectrum", "versioned joint likelihood and covariance",
            ],
            "nonidentifiability_witness": "YQQ=0 and YQQ=y Identity_3 are both selector-allowed but give inequivalent observables.",
        },
        {
            "gate": "G1",
            "full_gate_closed": False,
            "landed": "necessary pure-Z3, mixed-PS-Z3, and two raw Z3-Z5610 residue checks pass for the chosen charges",
            "still_required": "complete Z5610 x Z3 x Z4R product-bordism/discrete-R/UV anomaly treatment",
        },
    ]


def source_manifest() -> list[dict[str, Any]]:
    paths = (MODEL, PARAMETERS, PARTICLES, README, VALIDATOR, Path(__file__).resolve(), TEST)
    return [
        {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256_file(path)}
        for path in paths
    ]


def build_report() -> dict[str, Any]:
    source = source_contract()
    selector = selector_and_anomaly_audit()
    qc4_witness = explicit_qc4_dressing_witness()
    report: dict[str, Any] = {
        "schema": "susy-v39-g7-g8-split-six-architecture-v1",
        "status": STATUS,
        "source_contract": source,
        "V37_unsplit_additive_selector_no_go": old_single_six_no_go(),
        "minimal_split_six_selector_search": minimal_selector_search(),
        "V39_selector_and_necessary_anomaly_audit": selector,
        "canonical_branch_and_PQ_quality_scope": canonical_branch_and_quality(),
        "restricted_Q4_PSVev_dressing_result": restricted_q4_dressing_result(),
        "explicit_Qc4_PSVev_dressing_witness": qc4_witness,
        "gate_statuses": gate_statuses(),
        "established_full_predictive_closed_count": 0,
        "complete_theory_exists": False,
        "source_manifest": source_manifest(),
    }
    if not source["all_static_checks_pass"]:
        raise RuntimeError("V39 source no longer matches the audited split-six contract")
    if not selector["all_displayed_W_terms_Z3_neutral"]:
        raise RuntimeError("a displayed V39 superpotential term violates Z3")
    if not selector["all_four_local_sources_forbidden"]:
        raise RuntimeError("a dangerous local driver-dressed source is allowed")
    if not qc4_witness["both_selectors_allow_both_operators"]:
        raise RuntimeError("the explicit degree-nine Qc4 dressing witness no longer verifies")
    if not report["canonical_branch_and_PQ_quality_scope"]["fresh_V39_charge_lattice_enumeration"]["exact_W33_K32_equalities_established"]:
        raise RuntimeError("the fresh V39 W33/K32 quality equalities no longer verify")
    if not selector["mixed_PS_Z3_standard_doubled_Dynkin"]["all_vanish_mod_3"]:
        raise RuntimeError("the claimed PS-Z3 residues do not vanish")
    if any(value != 0 for key, value in selector["necessary_Z3_Z5610_cross_residues"].items() if key.endswith("mod_3")):
        raise RuntimeError("the chosen anomalon charges do not cancel the listed cross residues")
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    selector = report["V39_selector_and_necessary_anomaly_audit"]
    search = report["minimal_split_six_selector_search"]
    g7, g8, _g1 = report["gate_statuses"]
    residues = selector["mixed_PS_Z3_standard_doubled_Dynkin"]
    cross = selector["necessary_Z3_Z5610_cross_residues"]
    qc4 = report["explicit_Qc4_PSVev_dressing_witness"]
    return f"""# V39 split-six baryon-operator audit

Status: `{report['status']}`

V39 makes one minimal architectural change to V37: the single PS six becomes
`SigC + SigBc`, and a new ordinary `Z3` is imposed. The intended scope is a
source-level repair of the direct driver-dressed four-matter operators; it is
not a claimed complete theory.

## Exact selector result

The unsplit V37 terms force `4 q(Q)=4 q(Qc)=0` for every extra ordinary
additive selector. The split six removes that implication. The retained-term,
mixed-PS-residue search through odd orders 3--99 finds its first solution at
`N={search['minimum_order']}`. V39 uses
`q(Q,Qc,Sc,Sbc,SigC,SigBc)=(1,2,2,1,2,1)`.

Thus the local source charges are `{[(row['operator'], row['Z3']) for row in selector['dangerous_local_sources']]}`:
none is neutral. Every one of the 32 displayed superpotential terms is `Z3`
neutral and has external `Z4R` charge two.

The pure finite convention passes, the mixed PS residues are
`{residues['raw_nonnegative_representative_sums']}` modulo 3, and the two
listed raw cross residues are both zero modulo 3. These are necessary checks,
not a product-bordism or discrete-R completion.

The active 21-field `(Z5610,Z4R,Z3,PQ)` lattice is re-enumerated rather than
inherited by deletion.  It has exact first-breaking equalities W degree 33
and Kähler degree 32; the gauge-singlet attainment witnesses are `P^33` and
`P^6 A32^21 A16dag (A17dag)^4`.

## Narrow VEV result and remaining boundary

For exactly four left-handed `Q` fields and only canonical PS/PQ VEV
insertions, the SU(4) and `Z3` count forces a surplus of identical rank-one
PS VEVs; their SU(2)_R epsilon contraction vanishes. This proves a narrow
holomorphic `X/Zp Q^4` dressing result on that branch. The mirror `Qc^4`
ring fails explicitly because `Qc` itself carries SU(2)_R.

The concrete allowed counterexample is
`X [epsilon_SU2R delta_SU4 (Qc Sbc)]^4/M^6`, and likewise with `Zp`.
Both degree-nine operators have `Z3=0`, `Z5610=0`, `PQ=0`, and `Z4R=2`.
After four `Sbc` insertions take their canonical PS-breaking VEV, the operator
is generically nonzero.  This is an operator-ring counterexample, not by itself
a proton-decay amplitude: {qc4['qualification']}

G7 remains open: `{'; '.join(g7['still_required'])}`.

G8 retains the Yukawa and type-I-seesaw source terms but remains open:
`{'; '.join(g8['still_required'])}`.

The model has an executable SARAH validator at
`{report['source_contract']['SARAH_runtime_validator']['path']}`. It must be
run with SARAH 4.15.3 before any downstream RGE or spectrum statement.

Core SHA-256: `{report['core_sha256']}`
"""


def write_outputs(report: Mapping[str, Any]) -> None:
    OUTPUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(render_markdown(report), encoding="utf-8")


def check_outputs(report: Mapping[str, Any]) -> bool:
    if not OUTPUT_JSON.is_file() or not OUTPUT_MD.is_file():
        return False
    stored = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
    return stored == report and stored["core_sha256"] == canonical_sha(stored) and stored["core_sha256"] in OUTPUT_MD.read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        write_outputs(report)
        print(f"WROTE {OUTPUT_JSON.name} {OUTPUT_MD.name}")
    if args.check:
        ok = check_outputs(report)
        print("V39_G7_G8_ARCHITECTURE_CHECK " + ("PASS" if ok else "FAIL"))
        return 0 if ok else 1
    if not args.write and not args.check:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
