#!/usr/bin/env python3
"""V53 filter-action selector candidate with exact bounded charge/anomaly audit."""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

import g1_exact_declared_symmetry_character_census_v20 as d5


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V53_FILTER_SELECTOR_CANDIDATE_AUDIT.json"
MD_PATH = ROOT / "SUSY_V53_FILTER_SELECTOR_CANDIDATE_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v53_filter_selector_candidate_audit.py"
UPSTREAM = ROOT / "SUSY_V53_PROTON_SAFE_SELECTOR_NO_GO_AUDIT.json"
EXPECTED_UPSTREAM = "3ad9373cb18224f72bfcedc0457378c996966cc5cbef5e4e3f4f3772e592e58b"

STATUS = (
    "V53_FILTER_ACTION_Z9xMATTER_PARITY_SELECTOR_CANDIDATE__ALL_SOURCE_FILTER_"
    "YUKAWA_AND_INVERSE_SEESAW_TERMS_ALLOWED__ODD_MATTER_FORBIDDEN_ALL_ORDERS_"
    "F16_POWER4_AND_ALL_ZERO_ONE_TWO_VEV_DRESSINGS_FORBIDDEN_THROUGH_DEGREE6_"
    "DISCRETE_ANOMALIES_REPAIRED_BY_TWO_VECTOR10_PAIRS_AND_FOUR_SINGLET_PAIRS_"
    "POLE_RATIO841__FIRST_EXACT_DANGEROUS_DRESSING_AT_DEGREE8__FULL_MATCHING_"
    "OPEN__NO_GATE_PROMOTION"
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def load_upstream() -> dict[str, Any]:
    value = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    if value.get("core_sha256") != canonical_sha(value):
        raise RuntimeError("stale V53 no-go input")
    return value


def candidate_charges(modulus: int, c: int, d: int, h2: int, f: int) -> dict[str, int]:
    """Solve all linear required-term equations from four free charges."""
    x = (-c) % modulus
    h = (-d - h2) % modulus
    hb = (d + h2) % modulus
    p = (2 * f - d - h2) % modulus
    h1 = (-p - hb) % modulus
    n = (c - f) % modulus
    nc = (-n) % modulus
    return {
        "E54": 0,
        "A45": 0,
        "C16H": c,
        "Bbar16H": x,
        "D45_missingVEV": d,
        "H1_10": h1,
        "H2_10": h2,
        "h_10": h,
        "barh_10": hb,
        "P_filter": p,
        "F16": f,
        "N": n,
        "Nc": nc,
    }


def required_terms(q: Mapping[str, int], modulus: int) -> dict[str, bool]:
    terms = {
        "E2": 2 * q["E54"],
        "E3": 3 * q["E54"],
        "A2": 2 * q["A45"],
        "EA2": q["E54"] + 2 * q["A45"],
        "barC_C": q["Bbar16H"] + q["C16H"],
        "barC_A_C": q["Bbar16H"] + q["A45"] + q["C16H"],
        "D45_squared": 2 * q["D45_missingVEV"],
        "H1_P_barh": q["H1_10"] + q["P_filter"] + q["barh_10"],
        "barh_h": q["barh_10"] + q["h_10"],
        "h_D45_H2": q["h_10"] + q["D45_missingVEV"] + q["H2_10"],
        "H2_squared": 2 * q["H2_10"],
        "F_F_H1": 2 * q["F16"] + q["H1_10"],
        "F_barC_N": q["F16"] + q["Bbar16H"] + q["N"],
        "N_Nc": q["N"] + q["Nc"],
        "Nc_Nc_inverse_mu": 2 * q["Nc"],
    }
    return {name: charge % modulus == 0 for name, charge in terms.items()}


def vev_dressing_rows(q: Mapping[str, int], modulus: int, max_insertions: int = 2) -> list[dict[str, Any]]:
    vevs = ("E54", "A45", "C16H", "Bbar16H", "D45_missingVEV", "P_filter")
    rows = []
    for degree in range(max_insertions + 1):
        for dressing in itertools.combinations_with_replacement(vevs, degree):
            charge = (4 * q["F16"] + sum(q[name] for name in dressing)) % modulus
            rows.append(
                {
                    "total_superpotential_degree": 4 + degree,
                    "dressing": list(dressing),
                    "Z9_charge": charge,
                    "forbidden": charge != 0,
                }
            )
    return rows


def bounded_base_search(max_modulus: int = 32) -> dict[str, Any]:
    rows = []
    candidates = []
    for modulus in range(3, max_modulus + 1):
        count = safe = 0
        for c in range(modulus):
            for d in range(modulus):
                if 2 * d % modulus:
                    continue
                for h2 in range(modulus):
                    if 2 * h2 % modulus:
                        continue
                    for f in range(modulus):
                        q = candidate_charges(modulus, c, d, h2, f)
                        if not all(required_terms(q, modulus).values()):
                            continue
                        count += 1
                        dresses = vev_dressing_rows(q, modulus)
                        if all(row["forbidden"] for row in dresses):
                            safe += 1
                            candidates.append({"modulus": modulus, "charges": q})
        rows.append({"modulus": modulus, "required_solutions": count, "degree6_safe": safe})
    return {"maximum_modulus": max_modulus, "rows": rows, "candidates": candidates}


def anomaly_ledger(q: Mapping[str, int], modulus: int) -> dict[str, Any]:
    # T(10)=1,T(16)=2,T(45)=8,T(54)=12. Multiplicities are dimensions for gravity/cubic.
    charged = [
        ("C16H", 16, 2, 1),
        ("Bbar16H", 16, 2, 1),
        ("H1_10", 10, 1, 1),
        ("H2_10", 10, 1, 1),
        ("h_10", 10, 1, 1),
        ("barh_10", 10, 1, 1),
        ("F16", 16, 2, 3),
        ("N", 1, 0, 3),
        ("Nc", 1, 0, 3),
        ("P_filter", 1, 0, 1),
    ]
    gauge = sum(index * copies * q[name] for name, _dim, index, copies in charged) % modulus
    gravity = sum(dim * copies * q[name] for name, dim, _index, copies in charged) % modulus
    cubic = sum(dim * copies * q[name] ** 3 for name, dim, _index, copies in charged) % modulus
    return {"Spin10_squared_Z9": gauge, "gravity_squared_Z9": gravity, "Z9_cubed": cubic}


def spectator_repair(q: Mapping[str, int], modulus: int) -> dict[str, Any]:
    # Two vectorlike 10 pairs and four singlet pairs, all massive through P X Xbar.
    vector_pairs = [[1, 6], [1, 6]]
    singlet_pairs = [[1, 6] for _ in range(4)]
    p = q["P_filter"]
    assert all((p + x + y) % modulus == 0 for x, y in vector_pairs + singlet_pairs)
    base = anomaly_ledger(q, modulus)
    vector = {
        "Spin10_squared_Z9": sum(x + y for x, y in vector_pairs) % modulus,
        "gravity_squared_Z9": sum(10 * (x + y) for x, y in vector_pairs) % modulus,
        "Z9_cubed": sum(10 * (x**3 + y**3) for x, y in vector_pairs) % modulus,
    }
    singlet = {
        "Spin10_squared_Z9": 0,
        "gravity_squared_Z9": sum(x + y for x, y in singlet_pairs) % modulus,
        "Z9_cubed": sum(x**3 + y**3 for x, y in singlet_pairs) % modulus,
    }
    total = {name: (base[name] + vector[name] + singlet[name]) % modulus for name in base}
    return {
        "base": base,
        "vector10_pairs": vector_pairs,
        "singlet_pairs": singlet_pairs,
        "vector_contribution": vector,
        "singlet_contribution": singlet,
        "total_mod9": total,
        "all_spectator_masses_generated_by_P": True,
        "FF_spectator10_Yukawas_forbidden": all(
            (2 * q["F16"] + charge) % modulus != 0
            for pair in vector_pairs
            for charge in pair
        ),
        "spectator_singlet_linear_and_direct_seesaw_mixings_forbidden": all(
            charge % modulus != 0
            and (q["F16"] + q["Bbar16H"] + charge) % modulus != 0
            for pair in singlet_pairs
            for charge in pair
        ),
    }


def first_exact_gauge_invariant_F4_dressing(q: Mapping[str, int], modulus: int) -> dict[str, Any]:
    """Find the first charge-neutral Spin(10) invariant using C/barC/P VEVs."""
    spinor = d5.spinor()
    barspinor = Counter({tuple(-x for x in weight): mult for weight, mult in spinor.items()})
    family_spinor = Counter({weight: 3 * mult for weight, mult in spinor.items()})
    f4 = d5.sym(family_spinor, 4)
    for insertions in range(0, 9):
        for n_c in range(insertions + 1):
            for n_bar in range(insertions - n_c + 1):
                n_p = insertions - n_c - n_bar
                charge = (
                    4 * q["F16"]
                    + n_c * q["C16H"]
                    + n_bar * q["Bbar16H"]
                    + n_p * q["P_filter"]
                ) % modulus
                if charge:
                    continue
                character = f4
                if n_c:
                    character = d5.tensor(character, d5.sym(spinor, n_c))
                if n_bar:
                    character = d5.tensor(character, d5.sym(barspinor, n_bar))
                multiplicity = d5.singlet(character)
                if multiplicity:
                    return {
                        "operator": f"F16^4 C16H^{n_c} Bbar16H^{n_bar} P^{n_p}",
                        "VEV_insertions": insertions,
                        "total_degree": 4 + insertions,
                        "Z9_charge": charge,
                        "Spin10_singlet_multiplicity": multiplicity,
                    }
    raise RuntimeError("no exact dangerous dressing found in search range")


def build_report() -> dict[str, Any]:
    upstream = load_upstream()
    search = bounded_base_search()
    q = candidate_charges(9, c=1, d=0, h2=0, f=1)
    terms = required_terms(q, 9)
    dressings = vev_dressing_rows(q, 9)
    repair = spectator_repair(q, 9)
    parity = {
        "odd": ["three F16", "three N", "three Nc"],
        "even": ["all source/filter Higgs", "P", "all anomaly spectators"],
        "all_declared_VEVs_even": True,
        "odd_matter_monomials_forbidden_all_orders": True,
        "conservative_mod2_ledgers": {
            "odd_Weyl_components": 48 + 3 + 3,
            "odd_Weyl_components_mod2": (48 + 3 + 3) % 2,
            "Spin10_index": 3 * 2,
            "Spin10_index_mod2": (3 * 2) % 2,
            "cubic_charge_sum_mod2": (48 + 3 + 3) % 2,
        },
    }
    first_unsafe = first_exact_gauge_invariant_F4_dressing(q, 9)
    source_T = 12 + 8 + 2 + 2 + 8 + 4 * 1
    matter_T = 3 * 2
    spectator_T = 4 * 1
    total_T = source_T + matter_T + spectator_T
    b_landau = total_T - 3 * 8
    pole = math.exp(8 * math.pi**2 / (b_landau * 0.73**2))
    integrity = {
        "upstream_bound": upstream["core_sha256"] == EXPECTED_UPSTREAM,
        "candidate_is_smallest_modulus_in_search": min(
            row["modulus"] for row in search["candidates"]
        ) == 9,
        "all_required_terms_allowed": all(terms.values()),
        "all_F4_dressings_through_degree6_forbidden": all(row["forbidden"] for row in dressings),
        "first_exact_dangerous_dressing_is_degree8": (
            first_unsafe["Z9_charge"] == 0
            and first_unsafe["total_degree"] == 8
            and first_unsafe["Spin10_singlet_multiplicity"] == 72
        ),
        "all_Z9_anomalies_cancel_after_spectators": all(value == 0 for value in repair["total_mod9"].values()),
        "spectator_masses_and_matter_isolation_pass": (
            repair["all_spectator_masses_generated_by_P"]
            and repair["FF_spectator10_Yukawas_forbidden"]
            and repair["spectator_singlet_linear_and_direct_seesaw_mixings_forbidden"]
        ),
        "matter_parity_exact_and_conservatively_anomaly_even": parity["all_declared_VEVs_even"] and all(
            parity["conservative_mod2_ledgers"][name] == 0
            for name in ("odd_Weyl_components_mod2", "Spin10_index_mod2", "cubic_charge_sum_mod2")
        ),
        "beta_cost_is_exact": (source_T, matter_T, spectator_T, total_T, b_landau) == (36, 6, 4, 46, 22),
        "no_gate_promoted": True,
    }
    failures = [name for name, passed in integrity.items() if not passed]
    if failures:
        raise RuntimeError("V53 filter selector integrity failure: " + ", ".join(failures))
    report: dict[str, Any] = {
        "schema": "susy-v53-filter-selector-candidate-audit-v1",
        "status": STATUS,
        "verdict": {
            "explicit_candidate_exists": True,
            "candidate": "Z9 proton factor times exact Z2 matter parity",
            "scope": "proton-safe against direct F16^4 and every zero/one/two-VEV dressing through total degree six",
            "complete_theory": False,
            "limitation": "the Z9 is fully Higgsed and the first exact Spin(10)-invariant dangerous VEV dressing occurs at degree eight",
        },
        "field_contract": {
            "source": "E54+A45+C16H+Bbar16H",
            "filter": "D45 missing-VEV + H1,H2,h,barh tens + P",
            "matter": "three F16",
            "inverse_seesaw": "three N plus three Nc",
        },
        "bounded_search": search,
        "Z9_charges": q,
        "required_operator_checks": terms,
        "matter_parity": parity,
        "complete_F4_VEV_dressing_census_through_degree6": {
            "VEV_species": ["E54", "A45", "C16H", "Bbar16H", "D45_missingVEV", "P_filter"],
            "rows": dressings,
            "row_count": len(dressings),
            "rows_sha256": hashlib.sha256(canonical_bytes(dressings)).hexdigest(),
            "all_forbidden": True,
            "conservative_scope": "all VEV multisets are screened whether or not a separate Spin10 contraction exists",
        },
        "first_exposed_higher_degree_class": first_unsafe,
        "discrete_anomaly_repair": repair,
        "residual_group": {
            "Z9_gcd_with_VEV_charges": math.gcd(9, q["C16H"], q["Bbar16H"], q["D45_missingVEV"], q["P_filter"]),
            "Z9_remnant": "trivial",
            "Z2_matter_parity_remnant": "exact",
        },
        "perturbativity": {
            "T_convention": "T10=1,T16=2,T45=8,T54=12; b_L=sumT-3C2",
            "filter_source_T": source_T,
            "three_matter16_T": matter_T,
            "two_vector10_spectator_pairs_T": spectator_T,
            "total_T": total_T,
            "b_Landau": b_landau,
            "pole_over_matching_scale_at_g0p73": pole,
            "screen": "passes 100x but fails 1000x",
        },
        "fail_closed_open_items": [
            "degree-eight F16^4 Bbar16H^4 contains 72 selector-allowed Spin(10) invariants after symmetry breaking",
            "the allowed bare Nc*Nc inverse-seesaw parameter is not made naturally small by Z9 x matter parity",
            "the missing-VEV/filter vacuum and full enlarged Hessian are not recomputed here",
            "spectator thresholds, unification, full invariant census and proton amplitudes are absent",
            "a continuous U(1) parent or Green-Schwarz realization of the repaired Z9 is not constructed",
        ],
        "gate_effect": {"G2": "OPEN", "G6": "OPEN", "G7": "OPEN", "G8": "PARTIAL_SELECTOR_CANDIDATE_ONLY", "promotions": []},
        "primary_sources": [
            {"title": "A New Doublet-Triplet Splitting Mechanism for Supersymmetric SO(10)", "url": "https://arxiv.org/abs/hep-ph/9810315"},
            {"title": "TeV Scale Inverse Seesaw in SO(10)", "url": "https://arxiv.org/abs/0910.3924"},
            {"title": "Note on Discrete Gauge Anomalies", "url": "https://arxiv.org/abs/hep-th/9109045"},
        ],
        "upstream": {"path": UPSTREAM.name, "core_sha256": upstream["core_sha256"]},
        "integrity_checks": integrity,
        "n_failed_integrity_checks": 0,
        "source_manifest": [
            {"path": Path(__file__).name, "sha256": sha256_file(Path(__file__))},
            {"path": TEST_PATH.name, "sha256": sha256_file(TEST_PATH)},
            {"path": UPSTREAM.name, "sha256": sha256_file(UPSTREAM)},
            {"path": "g1_exact_declared_symmetry_character_census_v20.py", "sha256": sha256_file(ROOT / "g1_exact_declared_symmetry_character_census_v20.py")},
        ],
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    p = report["perturbativity"]
    return f"""# V53 filter selector candidate audit

Status: `{report['status']}`

## Outcome

Changing the action as required by the V53 no-go produces a bounded-order
candidate: `Z9 x Z2_matter`.  The exact Z2 forbids every odd-matter monomial at
all orders.  Z9 allows the complete declared source, filter-chain, Yukawa and
inverse-seesaw terms while forbidding direct `16F^4` and every dressing by zero,
one or two declared VEV insertions, i.e. every such class through total degree six.

The bounded search through `Z32` finds `Z9` is the smallest modulus satisfying
these conditions.  Z9 charges are `{report['Z9_charges']}`.

## Anomalies and cost

Two vectorlike 10 pairs of charges `(1,6)` and four singlet pairs `(1,6)`, all
massive through the charge-2 filter VEV `P`, cancel the mixed Spin(10), gravity
and cubic Z9 residues exactly.  Matter parity has 54 odd Weyl components and
Spin(10) index 6, both even in the conservative ledger.

The complete inventory has `sum T={p['total_T']}`, `b_L={p['b_Landau']}` and
`Lambda_pole/M={p['pole_over_matching_scale_at_g0p73']:.6g}` at `g=0.73`: it
passes a 100x window but not 1000x.

## Fail-closed boundary

Z9 is fully broken by the VEVs.  The first exact exposed Spin(10) class is
`F16^4 Bbar16H^4` at degree eight, with 72 family-dressed invariant directions.
No full filter vacuum/Hessian, continuous
parent, threshold match or proton lifetime is claimed.  This is therefore a
useful selector candidate, not G8 or theory closure.

Core SHA-256: `{report['core_sha256']}`
"""


def validate(report: Mapping[str, Any]) -> None:
    if report["status"] != STATUS or report["core_sha256"] != canonical_sha(report):
        raise RuntimeError("status/hash drift")
    if report["n_failed_integrity_checks"] or not all(report["integrity_checks"].values()):
        raise RuntimeError("integrity failure")
    if report["verdict"]["complete_theory"] or report["gate_effect"]["promotions"]:
        raise RuntimeError("candidate overpromoted")


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
        print("V53_FILTER_SELECTOR_CANDIDATE_AUDIT_CHECK_PASS")
    if not args.write and not args.check:
        print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
