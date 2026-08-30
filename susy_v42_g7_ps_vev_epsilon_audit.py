#!/usr/bin/env python3
"""Fail-closed V42 G7 audit of Pati--Salam VEV-dressed epsilon operators.

V41 correctly separated the matter-only ``4^2 bar4^2`` delta class from the
usual epsilon_SU4 proton-source classes.  That result did not settle what
happens when the fundamental PS-breaking fields Sc=(bar4,1,2) and
Sbc=(4,1,2) are inserted into an invariant.  This executable audit does four
limited things:

* gives explicit low-degree SU(4)xSU(2)_LxSU(2)_R contractions;
* proves the V40 Z9 / residual R-parity protection for the familiar four- and
  three-matter epsilon families under *arbitrary declared VEV dressings*;
* performs a bounded representation-count scan through total field degree 12;
* records an explicit, fully V40-selector-neutral six-matter Delta-B=-1,
  Delta-L=-3 witness at degree ten.

The witness is an EFT operator which the displayed symmetries allow.  It is
not an assertion that an unspecified UV completion generates a nonzero Wilson
coefficient, and it is not a proton-lifetime calculation.
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
OUTPUT_JSON = ROOT / "SUSY_V42_G7_PS_VEV_EPSILON_AUDIT.json"
OUTPUT_MD = ROOT / "SUSY_V42_G7_PS_VEV_EPSILON_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v42_g7_ps_vev_epsilon_audit.py"

ORDER = 9
W_TARGET = 2
K_TARGET = 0
MAX_COMPLETE_FIELD_DEGREE = 12
STATUS = (
    "V42_G7_PS_PQ_EW_VEV_EPSILON_AUDIT__LOW_DEGREE_PROTECTION_EXACT__"
    "SELECTOR_ALLOWED_SIX_MATTER_DELTA_B_MINUS_ONE_WITNESS__G7_FAIL_CLOSED"
)


# These are the V40 charges relevant to this audit.  Sc/Sbc notation follows
# the V40 table: Sc is a bar4 and Sbc is a 4.  P/Pb may break PQ/Z5610, so the
# report never uses either one as a proton-stability selection rule.
FIELDS: dict[str, dict[str, int | str]] = {
    "Q": {"ps": "(4,2,1)", "u1f": 3, "r4": 1, "z5610": 0, "pq": 0},
    "Qc": {"ps": "(bar4,1,2)", "u1f": -3, "r4": 1, "z5610": 0, "pq": 0},
    "Sc": {"ps": "(bar4,1,2)", "u1f": 0, "r4": 0, "z5610": 0, "pq": 0},
    "Sbc": {"ps": "(4,1,2)", "u1f": 0, "r4": 0, "z5610": 0, "pq": 0},
    "H": {"ps": "(1,2,2)", "u1f": 0, "r4": 0, "z5610": 0, "pq": 0},
    "P": {"ps": "(1,1,1)", "u1f": 0, "r4": 2, "z5610": 170, "pq": 170},
    "Pb": {"ps": "(1,1,1)", "u1f": 0, "r4": 2, "z5610": 5440, "pq": -170},
    "ThetaPlus": {"ps": "(1,1,1)", "u1f": 9, "r4": 0, "z5610": 0, "pq": 0},
    "ThetaMinus": {"ps": "(1,1,1)", "u1f": -9, "r4": 0, "z5610": 0, "pq": 0},
}

VEV_FIELDS = ("Sc", "Sbc", "P", "Pb", "H", "ThetaPlus", "ThetaMinus")


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def charge(fields: Iterable[str], key: str, modulus: int | None = None) -> int:
    value = sum(int(FIELDS[name][key]) for name in fields)
    return value if modulus is None else value % modulus


def selector_signature(fields: Iterable[str]) -> dict[str, int | bool]:
    names = tuple(fields)
    u1f = charge(names, "u1f")
    r4 = charge(names, "r4", 4)
    z5610 = charge(names, "z5610", 5610)
    pq = charge(names, "pq")
    return {
        "U1F": u1f,
        "Z9": u1f % ORDER,
        "Z4R": r4,
        "Z5610": z5610,
        "PQ_numerator_over_170": pq,
        "W_allowed_by_listed_selectors": u1f == 0 and r4 == W_TARGET and z5610 == 0 and pq == 0,
        "Kahler_allowed_by_listed_selectors": u1f == 0 and r4 == K_TARGET and z5610 == 0 and pq == 0,
    }


def vev_ring_theorem() -> dict[str, Any]:
    rows = []
    for name in VEV_FIELDS:
        row = FIELDS[name]
        rows.append({
            "field": name,
            "PS": row["ps"],
            "U1F": int(row["u1f"]),
            "Z9": int(row["u1f"]) % ORDER,
            "Z4R": int(row["r4"]) % 4,
            "Z4R_even": int(row["r4"]) % 2 == 0,
        })
    return {
        "canonical_nonzero_visible_VEVs": list(VEV_FIELDS),
        "generator_rows": rows,
        "all_VEV_generators_Z9_neutral": all(row["Z9"] == 0 for row in rows),
        "all_VEV_generators_R_even": all(row["Z4R_even"] for row in rows),
        "conjugate_statement": (
            "A conjugate changes the integer U(1)_F and Z4R lift sign, but remains Z9-neutral "
            "and R-even.  The two conclusions therefore apply to holomorphic, Kahler, soft, "
            "and mixed VEV monomials made only from the declared generators."
        ),
        "all_order_charge_formula": {
            "Z9": "q_Z9(D)=0 for every declared-VEV dressing D.",
            "Z4R_parity": (
                "q_R(D)=2(n_P+n_Pb+n_Pdag+n_Pbdag) mod 4, hence q_R(D) is even."
            ),
            "residual_statement": (
                "P/Pb carry R charge two, so their VEVs can reduce Z4R to its Z2 subgroup; "
                "all Q/Qc matter remains odd under that subgroup."
            ),
        },
        "PS_rank_one_branch_statement": (
            "On the canonical PS branch Sc and Sbc each point in one SU(4) lepton direction and "
            "opposite SU(2)R spinor directions.  A single SU(4) epsilon cannot contain two copies "
            "of the same oriented PS VEV; spectator PS VEV factors can instead occur in delta-paired "
            "Sc.Sbc dressings."
        ),
        "PQ_boundary": (
            "P/Pb can break the old PQ/Z5610 selector.  This audit does not use PQ or Z5610 as a "
            "post-PQ proton-stability rule; their inclusion above only makes clear that the clean "
            "six-matter witness does not need either field."
        ),
    }


def source_rows() -> list[dict[str, Any]]:
    """Low-degree contractions with their physical interpretation boundary."""

    definitions: tuple[dict[str, Any], ...] = (
        {
            "label": "conventional_left_same_orientation_epsilon",
            "fields": ("Q", "Q", "Q", "Q"),
            "SU4_tensor": "epsilon_abcd Q^(a i) Q^(b j) Q^(c k) Q^(d l)",
            "SU2_tensor": "epsilon_ij epsilon_kl (generic flavour tensor understood)",
            "after_declared_VEVs": "Contains the usual QQQL component before any PS VEV substitution.",
            "B_L_class": "actual MSSM-like DeltaB=+1, DeltaL=+1 four-matter epsilon source",
            "precise_status": "Z9 blocks it: theta fields shift U1F only by multiples of nine, not by twelve.",
        },
        {
            "label": "conventional_right_same_orientation_epsilon",
            "fields": ("Qc", "Qc", "Qc", "Qc"),
            "SU4_tensor": "epsilon^abcd Qc_(a alpha) Qc_(b beta) Qc_(c gamma) Qc_(d delta)",
            "SU2_tensor": "epsilon^alpha_beta epsilon^gamma_delta (one of the SU2R singlet pairings)",
            "after_declared_VEVs": "Contains u^c u^c d^c e^c / nu^c-type components.",
            "B_L_class": "actual MSSM-like DeltaB=-1, DeltaL=-1 four-matter epsilon source",
            "precise_status": "Z9 blocks it: theta fields shift U1F only by multiples of nine, not by minus twelve.",
        },
        {
            "label": "left_epsilon_one_PS_VEV_precursor",
            "fields": ("ThetaMinus", "Q", "Q", "Q", "Sbc", "H"),
            "SU4_tensor": "ThetaMinus epsilon_abcd Q^(a i) Q^(b j) Q^(c k) Sbc^(d alpha)",
            "SU2_tensor": "epsilon_ij epsilon_kl epsilon_alpha_beta H^(l beta)",
            "after_declared_VEVs": (
                "At <Sbc^(4 alpha)>=v_PS, this becomes epsilon_rgb Q^r Q^g Q^b H: the "
                "unbroken-SM QQQH baryon-violating class.  A later electroweak H VEV would turn it "
                "into a broken-phase three-matter interaction."
            ),
            "B_L_class": "genuine PS-VEV precursor to a DeltaB=+1 source; not a rate calculation",
            "precise_status": "Z9 is neutral after ThetaMinus, but Z4R=3 blocks both W and Kahler families under every declared VEV dressing.",
        },
        {
            "label": "right_epsilon_one_PS_VEV_precursor",
            "fields": ("ThetaPlus", "Qc", "Qc", "Qc", "Sc"),
            "SU4_tensor": "ThetaPlus epsilon^abcd Qc_(a alpha) Qc_(b beta) Qc_(c gamma) Sc_(d delta)",
            "SU2_tensor": "epsilon^alpha_beta epsilon^gamma_delta",
            "after_declared_VEVs": (
                "At <Sc_(4 delta)>=v_PS, the color part contains epsilon^rgb u^c_r d^c_g d^c_b, "
                "the UDD-type DeltaB=-1 class."
            ),
            "B_L_class": "genuine PS-VEV precursor to a DeltaB=-1 UDD source; not a rate calculation",
            "precise_status": "Z9 is neutral after ThetaPlus, but Z4R=3 blocks both W and Kahler families under every declared VEV dressing.",
        },
        {
            "label": "delta_left_lepton_RPV_control",
            "fields": ("Q", "Q", "Qc", "Sc"),
            "SU4_tensor": "delta^a_c delta^b_d Q^(a i) Q^(b j) Qc_(c alpha) Sc_(d beta)",
            "SU2_tensor": "epsilon_ij epsilon^alpha_beta",
            "after_declared_VEVs": (
                "At the Sc lepton-direction VEV it has L Q D^c and L L E^c component classes. "
                "It is a delta contraction, not a single-epsilon SU4 source."
            ),
            "B_L_class": "genuine DeltaL=+1 PS-VEV RPV control class",
            "precise_status": "It has Z9=3 (and Z4R=3), so it is blocked already by the V40 selector.",
        },
        {
            "label": "delta_bilinear_LH_control",
            "fields": ("Q", "H", "Sc"),
            "SU4_tensor": "delta^a_b Q^(a i) Sc_(b alpha)",
            "SU2_tensor": "epsilon^alpha_beta H_(i beta)",
            "after_declared_VEVs": "At <Sc> it is an LH bilinear precursor.",
            "B_L_class": "DeltaL=+1 bilinear control; distinct from V40's allowed Q H Sc NDirac term",
            "precise_status": "It has Z9=3 and odd R parity, so it is blocked by the listed selector.",
        },
    )
    rows = []
    for entry in definitions:
        fields = tuple(entry["fields"])
        rows.append({
            **entry,
            "fields": list(fields),
            "selector_signature": selector_signature(fields),
            "matter_field_count_Q_plus_Qc": sum(name in {"Q", "Qc"} for name in fields),
        })
    return rows


def minimal_theta_completion(matter_difference: int) -> tuple[str, ...] | None:
    """Theta completion exists exactly when 3*(q-qc) is a multiple of nine."""

    if matter_difference % 3 != 0:
        return None
    if matter_difference > 0:
        return ("ThetaMinus",) * (matter_difference // 3)
    if matter_difference < 0:
        return ("ThetaPlus",) * ((-matter_difference) // 3)
    return ()


def su2r_rank_one_pairing_possible(qc: int, sbc: int, sc: int, h: int) -> bool:
    """Necessary pairing test after fixed Sc/Sbc spinor directions are inserted.

    Qc and a non-substituted H have free SU(2)R components.  Every fixed Sc
    (respectively Sbc) spinor must be paired either with an oppositely oriented
    Sbc (respectively Sc) VEV or with one of those free doublets; otherwise an
    antisymmetric epsilon pairs identical spinors and vanishes.
    """

    free = qc + h
    return sc <= sbc + free and sbc <= sc + free


def bounded_single_epsilon_scan() -> dict[str, Any]:
    """A finite field-count frontier, not a Hilbert-series completeness proof."""

    all_group_count_rows = 0
    rank_one_rows = 0
    theta_lift_rows = 0
    clean_rows: list[dict[str, Any]] = []
    for q, qc, sbc, sc, h in itertools.product(range(9), range(9), range(6), range(6), range(5)):
        matter = q + qc
        raw_degree = matter + sbc + sc + h
        net_su4 = q + sbc - qc - sc
        if raw_degree == 0 or raw_degree > MAX_COMPLETE_FIELD_DEGREE or abs(net_su4) != 4:
            continue
        # SU(2) singlet existence at representation-count level.
        if (q + h) % 2 != 0 or (qc + sbc + sc + h) % 2 != 0:
            continue
        all_group_count_rows += 1
        # One epsilon can contain at most one rank-one PS VEV of its orientation.
        epsilon_rank_one_possible = q >= 3 if net_su4 == 4 else qc >= 3
        su2r_possible = su2r_rank_one_pairing_possible(qc, sbc, sc, h)
        if not (epsilon_rank_one_possible and su2r_possible):
            continue
        rank_one_rows += 1
        difference = q - qc
        theta = minimal_theta_completion(difference)
        if theta is None:
            continue
        theta_lift_rows += 1
        # With no P/Pb insertion, Z5610/PQ remain clean.  N=2 mod4 is exactly
        # the Z4R W selection rule.  N=0 mod4 would need an R=2 P/Pb VEV and is
        # intentionally not called clean because PQ/Z5610 are then broken.
        if matter % 4 != W_TARGET:
            continue
        complete_degree = raw_degree + len(theta)
        if complete_degree > MAX_COMPLETE_FIELD_DEGREE:
            continue
        clean_rows.append({
            "counts": {"Q": q, "Qc": qc, "Sbc": sbc, "Sc": sc, "H": h},
            "net_SU4_fundamental_number": net_su4,
            "matter_difference_Q_minus_Qc": difference,
            "raw_field_degree_without_theta": raw_degree,
            "minimal_U1F_theta_completion": list(theta),
            "complete_field_degree": complete_degree,
            "Z9": (3 * difference) % ORDER,
            "Z4R_from_matter": matter % 4,
            "selector_clean_without_P_or_Pb": True,
            "qualification": (
                "Representation-count and rank-one-VEV pairing conditions pass.  This is not by itself "
                "a full flavour-tensor or component matching calculation."
            ),
        })
    clean_rows.sort(key=lambda row: (row["complete_field_degree"], json.dumps(row["counts"], sort_keys=True)))
    earliest = clean_rows[0] if clean_rows else None
    return {
        "scan_domain": {
            "maximum_complete_field_degree": MAX_COMPLETE_FIELD_DEGREE,
            "q_Q_and_q_Qc_each_scanned_through": 8,
            "q_Sbc_and_q_Sc_each_scanned_through": 5,
            "q_H_scanned_through": 4,
            "single_epsilon_condition": "|n_4-n_bar4|=4; all remaining SU4 indices are delta-paired",
        },
        "group_representation_count_rows": all_group_count_rows,
        "rows_after_rank_one_PS_and_SU2R_pairing_filters": rank_one_rows,
        "rows_with_a_minimal_continuous_U1F_theta_lift": theta_lift_rows,
        "clean_W_selector_rows": clean_rows,
        "earliest_clean_W_selector_row": earliest,
        "no_clean_W_selector_row_below_degree_ten": all(row["complete_field_degree"] >= 10 for row in clean_rows),
        "scope_limit": (
            "The scan is an exact finite count/charge frontier under its stated bounds, not a complete Hilbert basis, "
            "a proof of nonzero Wilson coefficients, or a component-spectrum calculation."
        ),
    }


def high_degree_witness() -> dict[str, Any]:
    fields = ("ThetaPlus", "ThetaPlus") + ("Qc",) * 6 + ("Sbc",) * 2
    signature = selector_signature(fields)
    return {
        "operator": "ThetaPlus^2 (Qc)^6 (Sbc)^2 / M^7",
        "fields": list(fields),
        "field_degree": len(fields),
        "superpotential_suppression": "1/M^7 for ten chiral superfields",
        "selector_signature": signature,
        "SU4_contraction": (
            "epsilon^abcd Qc_(a alpha i) Qc_(b beta j) Qc_(c gamma k) Qc_(d delta l) "
            "times (Sbc^(e rho) Qc_(e sigma m) epsilon_rho_sigma) "
            "times (Sbc^(f mu) Qc_(f nu n) epsilon_mu_nu), with two independent SU2R epsilon "
            "pairings among the first four Qc fields."
        ),
        "SU4_and_SU2R_nonzero_component_witness": (
            "Set <Sbc^(4,+)>=v_PS.  The two delta factors select Qc_(4,- m) and Qc_(4,- n). "
            "In the epsilon take (a,b,c,d)=(r,g,b,4) and alternating SU2R components for the four Qc fields. "
            "For generic distinct flavour labels this gives a nonzero color-epsilon product of three colored Qc "
            "components and three SU4-leptonic Qc components."
        ),
        "post_PS_component_class": (
            "epsilon_rgb (u^c_r d^c_g d^c_b) (ell^c ell^c ell^c), where each ell^c is an e^c or nu^c "
            "component fixed by the chosen SU2R convention."
        ),
        "Delta_B": -1,
        "Delta_L": -3,
        "why_this_is_an_actual_B_L_witness": (
            "The displayed index assignment is nonzero on the canonical rank-one Sbc branch and contains three "
            "anti-quark and three anti-lepton chiral matter components.  It is therefore not merely a PS-level "
            "representation precursor."
        ),
        "why_it_is_not_a_proton_lifetime_claim": [
            "No UV matching has supplied a nonzero Wilson coefficient for this allowed operator.",
            "No flavour tensor, SUSY dressing, threshold matching, RG evolution, hadronic/nuclear matrix element, or decay calculation is performed.",
            "A six-matter DeltaB=-1, DeltaL=-3 interaction is not automatically a standard single-nucleon decay amplitude.",
        ],
        "full_listed_selector_clean": signature["W_allowed_by_listed_selectors"],
    }


def all_order_conclusion(sources: list[Mapping[str, Any]], witness: Mapping[str, Any]) -> dict[str, Any]:
    by_label = {str(row["label"]): row for row in sources}
    left4 = by_label["conventional_left_same_orientation_epsilon"]["selector_signature"]
    right4 = by_label["conventional_right_same_orientation_epsilon"]["selector_signature"]
    left3 = by_label["left_epsilon_one_PS_VEV_precursor"]["selector_signature"]
    right3 = by_label["right_epsilon_one_PS_VEV_precursor"]["selector_signature"]
    return {
        "four_matter_same_orientation_theorem": {
            "left_Q4_Z9": left4["Z9"],
            "right_Qc4_Z9": right4["Z9"],
            "proof": (
                "Every declared VEV dressing has Z9 charge zero.  Therefore Q4 remains charge three and Qc4 "
                "remains charge six modulo nine at every order in that ring, including conjugate/Kahler dressings."
            ),
            "exact_under_declared_VEV_ring": left4["Z9"] != 0 and right4["Z9"] != 0,
        },
        "one_PS_VEV_epsilon_theorem": {
            "left_Q3_Sbc_H_Z4R": left3["Z4R"],
            "right_Qc3_Sc_Z4R": right3["Z4R"],
            "proof": (
                "Each primitive has three R-odd matter fields, hence odd Z4R parity.  Every declared VEV and "
                "its conjugate is R-even.  Such a dressing can never have W charge two or Kahler charge zero."
            ),
            "exact_under_declared_VEV_ring": left3["Z4R"] % 2 == 1 and right3["Z4R"] % 2 == 1,
        },
        "scope_boundary": (
            "These are all-order theorems only for the named low-matter primitive families and the declared VEV ring. "
            "They do not forbid even-matter multi-epsilon/delta-decorated classes.  The explicit six-matter witness "
            "is a counterexample to promoting the low-degree statements into a full G7 proof."
        ),
        "counterexample_is_selector_clean": bool(witness["full_listed_selector_clean"]),
    }


def source_manifest() -> list[dict[str, Any]]:
    return [
        {
            "path": path.name,
            "exists": path.is_file(),
            "sha256": sha256_file(path) if path.is_file() else None,
        }
        for path in (Path(__file__), TEST_PATH)
    ]


def build_report() -> dict[str, Any]:
    ring = vev_ring_theorem()
    sources = source_rows()
    scan = bounded_single_epsilon_scan()
    witness = high_degree_witness()
    conclusion = all_order_conclusion(sources, witness)
    report: dict[str, Any] = {
        "schema": "susy-v42-g7-ps-vev-epsilon-audit-v1",
        "status": STATUS,
        "complete_theory_exists": False,
        "scope": (
            "A fail-closed operator/charge audit in the V40 U(1)_F-to-Z9 route.  It is not a complete PS invariant "
            "ring, UV completion, vacuum/spectrum calculation, or proton-decay calculation."
        ),
        "V40_relevant_field_charges": FIELDS,
        "declared_VEV_ring_theorem": ring,
        "explicit_low_degree_contraction_classification": sources,
        "bounded_single_epsilon_frontier": scan,
        "selector_allowed_six_matter_witness": witness,
        "all_order_limited_conclusion": conclusion,
        "literature_context": [
            {
                "reference": "M.-C. Chen et al., R parity violation from discrete R symmetries",
                "url": "https://mediatum.ub.tum.de/doc/1349870/document.pdf",
                "relevance": "Discusses PS breaking by (4,1,2)+(bar4,1,2) VEVs and the appearance of effective UDD/LLE classes; this audit supplies its own contractions and charge arithmetic.",
            },
            {
                "reference": "Dutka and Gargalionis, Dimension-5 baryon-number violation in low-scale Pati-Salam",
                "url": "https://arxiv.org/abs/2211.02054",
                "relevance": "Independent context that fundamental PS-breaking sectors can expose baryon-violating higher-dimensional structures; no numerical result from that paper is imported here.",
            },
        ],
        "gate_boundary": {
            "G7_closed": False,
            "landed": [
                "all-order declared-VEV-ring protection of the conventional Q4/Qc4 epsilon source families by Z9",
                "all-order residual-R-parity protection of the one-PS-VEV Q3SbcH/Qc3Sc precursor families",
                "an explicit selector-clean high-degree B/L-violating EFT witness that prevents overclaiming G7",
            ],
            "still_required": [
                "complete holomorphic and nonholomorphic PS invariant-ring/Hilbert-basis enumeration",
                "UV matching or a UV symmetry proving the six-matter Wilson coefficient vanishes",
                "flavour tensors, PS/PQ/EW vacuum alignment, spectrum, SUSY dressing, RG running, and physical decay calculations",
            ],
            "proton_lifetime_reported": False,
        },
        "decision": {
            "low_degree_same_orientation_protection_is_exact_in_stated_ring": True,
            "one_PS_VEV_UDD_or_QQQH_precursor_is_allowed_by_Z9": True,
            "one_PS_VEV_UDD_or_QQQH_precursor_is_blocked_by_residual_R_parity": True,
            "fully_listed_selector_clean_six_matter_B_L_witness_exists": True,
            "full_G7_closed": False,
            "gates_promoted": [],
        },
        "source_manifest": source_manifest(),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    ring = report["declared_VEV_ring_theorem"]
    sources = report["explicit_low_degree_contraction_classification"]
    scan = report["bounded_single_epsilon_frontier"]
    witness = report["selector_allowed_six_matter_witness"]
    rows = "\n".join(
        "| {label} | {z9} | {r4} | {kind} |".format(
            label=row["label"], z9=row["selector_signature"]["Z9"], r4=row["selector_signature"]["Z4R"], kind=row["B_L_class"]
        )
        for row in sources
    )
    return f"""# V42 G7 Pati--Salam VEV epsilon audit

Status: `{report['status']}`

## Outcome

The V40 `Z9` selector still proves an all-order statement for the conventional
same-orientation `Q4` and `Qc4` epsilon source families: every declared PS,
PQ, electroweak, Theta, or conjugate VEV dressing has `Z9=0`, while the two
sources have residues `3` and `6`.  PS breaking does introduce genuine
low-degree precursors, `ThetaMinus Q3 Sbc H` and `ThetaPlus Qc3 Sc`, but each
has three R-odd matter fields and `Z4R=3`.  Since every declared VEV is
R-even, neither can become a W-charge-two or Kahler-charge-zero operator.

| Low-degree class | Z9 | Z4R | Component boundary |
|---|---:|---:|---|
{rows}

## Exact limitation found

The protection cannot be promoted to all of G7.  The field operator

`{witness['operator']}`

has selector signature `{witness['selector_signature']}`.  Its explicit
SU(4)-epsilon plus delta contraction is nonzero on the canonical `Sbc` branch
and contains a six-matter component of the form
`epsilon_rgb (u^c_r d^c_g d^c_b) (ell^c ell^c ell^c)`, so it carries
`DeltaB={witness['Delta_B']}`, `DeltaL={witness['Delta_L']}`.  This is an
allowed EFT witness, not a claim that an unspecified UV completion produces
its coefficient and not a proton-lifetime result.

## Bounded frontier

The representation-count scan tests one-epsilon classes through complete
field degree `{scan['scan_domain']['maximum_complete_field_degree']}`.  It
finds `{len(scan['clean_W_selector_rows'])}` selector-clean rows and no clean
row below degree ten: `{scan['no_clean_W_selector_row_below_degree_ten']}`.
The earliest row is `{scan['earliest_clean_W_selector_row']}`.  The scan is a
finite consistency check, not a complete invariant-ring enumeration.

## Boundary

G7 remains open.  A UV construction would need either to prove the witness
coefficient absent or to analyze it together with the complete PS/Kahler/soft
operator basis, flavour, thresholds, dressing, running, and physical decay
observables.

For context on PS fundamental-breaking-induced B/L structures, see
[Chen et al.](https://mediatum.ub.tum.de/doc/1349870/document.pdf) and
[Dutka--Gargalionis](https://arxiv.org/abs/2211.02054).

Core SHA-256: `{report['core_sha256']}`
"""


def validate(report: Mapping[str, Any]) -> None:
    if report.get("status") != STATUS or canonical_sha(report) != report.get("core_sha256"):
        raise RuntimeError("stale or invalid V42 G7 PS-VEV report")
    ring = report["declared_VEV_ring_theorem"]
    if not ring["all_VEV_generators_Z9_neutral"] or not ring["all_VEV_generators_R_even"]:
        raise RuntimeError("declared VEV ring no longer proves the charge theorem")
    rows = {row["label"]: row for row in report["explicit_low_degree_contraction_classification"]}
    if rows["conventional_left_same_orientation_epsilon"]["selector_signature"]["Z9"] != 3:
        raise RuntimeError("left Q4 Z9 residue regressed")
    if rows["conventional_right_same_orientation_epsilon"]["selector_signature"]["Z9"] != 6:
        raise RuntimeError("right Qc4 Z9 residue regressed")
    for label in ("left_epsilon_one_PS_VEV_precursor", "right_epsilon_one_PS_VEV_precursor"):
        signature = rows[label]["selector_signature"]
        if signature["Z9"] != 0 or signature["Z4R"] != 3:
            raise RuntimeError("one-PS-VEV source theorem regressed")
    if rows["delta_left_lepton_RPV_control"]["selector_signature"]["Z9"] != 3:
        raise RuntimeError("delta L-violating control lost its Z9 block")
    witness = report["selector_allowed_six_matter_witness"]
    signature = witness["selector_signature"]
    if not witness["full_listed_selector_clean"] or not all(
        signature[key] == expected
        for key, expected in (("U1F", 0), ("Z9", 0), ("Z4R", 2), ("Z5610", 0), ("PQ_numerator_over_170", 0))
    ):
        raise RuntimeError("six-matter selector-clean witness failed")
    if (witness["Delta_B"], witness["Delta_L"]) != (-1, -3):
        raise RuntimeError("six-matter B/L witness changed")
    scan = report["bounded_single_epsilon_frontier"]
    earliest = scan["earliest_clean_W_selector_row"]
    if earliest is None or earliest["complete_field_degree"] != 10:
        raise RuntimeError("bounded scan no longer identifies the degree-ten frontier")
    if earliest["counts"] != {"Q": 0, "Qc": 6, "Sbc": 2, "Sc": 0, "H": 0}:
        raise RuntimeError("unexpected earliest selector-clean count row")
    if not scan["no_clean_W_selector_row_below_degree_ten"]:
        raise RuntimeError("low-degree selector-clean row requires a new audit")
    if report["gate_boundary"]["G7_closed"] or report["decision"]["full_G7_closed"] or report["decision"]["gates_promoted"]:
        raise RuntimeError("fail-closed G7 boundary was violated")


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
        print("SUSY V42 G7 PS-VEV epsilon audit: wrote certificates")
    if args.check:
        if not OUTPUT_JSON.is_file() or not OUTPUT_MD.is_file():
            raise SystemExit("generated V42 G7 certificates missing; run --write")
        if OUTPUT_JSON.read_text(encoding="utf-8") != expected_json:
            raise SystemExit("generated V42 G7 JSON is stale; run --write")
        if OUTPUT_MD.read_text(encoding="utf-8") != expected_md:
            raise SystemExit("generated V42 G7 Markdown is stale; run --write")
        print("SUSY_V42_G7_PS_VEV_EPSILON_AUDIT_CHECK_PASS")
    if not args.write and not args.check:
        print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
