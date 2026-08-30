#!/usr/bin/env python3
"""Exact V53 selector no-go and Spin(10) invariant census for the V52 R1 repair.

The declared field classes are E(54), A(45), C(16), B(bar16), H(10),
three matter F(16), and four singlets N.  We enumerate the exact holomorphic
Spin(10)-singlet polynomial through degree four with D5 weight characters and
solve every cyclic non-R and conventional Z_N^R charge system for 2<=N<=64.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import g1_exact_declared_symmetry_character_census_v20 as d5


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V53_PROTON_SAFE_SELECTOR_NO_GO_AUDIT.json"
MD_PATH = ROOT / "SUSY_V53_PROTON_SAFE_SELECTOR_NO_GO_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v53_proton_safe_selector_no_go_audit.py"
UPSTREAM = ROOT / "SUSY_V52_MINIMAL_SEESAW_DT_REPAIR_AUDIT.json"
EXPECTED_UPSTREAM_CORE = "f4dadf941dbfe6e540347aa720687b2cc8e08201edc8325cea6fabb8b6b4a723"

FIELDS = ("E54", "A45", "C16H", "Bbar16H", "H10", "F16x3", "Nx4")
SHORT = ("E", "A", "C", "B", "H", "F", "N")
STATUS = (
    "V53_EXACT_DEGREE4_SPIN10_INVARIANT_CENSUS__CYCLIC_AND_PRODUCT_"
    "SELECTOR_NO_GO__REQUIRED_HIGGS_YUKAWA_AND_DOUBLE_SEESAW_TERMS_FORCE_"
    "F16_POWER4_ALLOWED__R_SYMMETRY_SOURCE_MASS_CUBIC_CONFLICT__SEARCH_"
    "N2_TO64_EMPTY__PROTON_SAFE_SELECTOR_REQUIRES_ACTION_CHANGE__NO_GATE_PROMOTION"
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def load_hashed(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("core_sha256") != canonical_sha(value):
        raise RuntimeError(f"stale canonical input: {path.name}")
    return value


def _scaled(character: Mapping[tuple[int, ...], int], copies: int) -> Counter:
    return Counter({weight: copies * multiplicity for weight, multiplicity in character.items()})


@lru_cache(None)
def representation_characters() -> dict[str, Counter]:
    vector = d5.vector()
    spinor = d5.spinor()
    barspinor = Counter({tuple(-x for x in weight): mult for weight, mult in spinor.items()})
    adjoint = d5.exterior(list(vector.elements()), 2)
    symmetric = d5.sym(vector, 2)
    symmetric[d5.ZERO] -= 1
    symmetric = d5.clean(symmetric)
    return {
        "E": symmetric,
        "A": adjoint,
        "C": spinor,
        "B": barspinor,
        "H": vector,
        "F": _scaled(spinor, 3),
        "N": Counter({d5.ZERO: 4}),
    }


def compositions(total: int, length: int):
    if length == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for tail in compositions(total - first, length - 1):
            yield (first,) + tail


@lru_cache(None)
def species_symmetric_character(species: str, degree: int) -> Counter:
    return d5.sym(representation_characters()[species], degree)


@lru_cache(None)
def monomial_character(counts: tuple[int, ...]) -> Counter:
    factors = [
        species_symmetric_character(species, degree)
        for species, degree in zip(SHORT, counts)
        if degree
    ]
    if not factors:
        return Counter({d5.ZERO: 1})
    factors.sort(key=len)
    result = factors[0]
    for factor in factors[1:]:
        result = d5.tensor(result, factor)
    return result


def monomial_label(counts: tuple[int, ...]) -> str:
    terms = []
    for field, count in zip(FIELDS, counts):
        if count:
            terms.append(field if count == 1 else f"{field}^{count}")
    return " ".join(terms)


def exact_invariant_census() -> list[dict[str, Any]]:
    rows = []
    tags = {
        (0, 0, 0, 0, 0, 4, 0): "fatal_proton_F4",
        (0, 0, 0, 0, 1, 2, 0): "required_Yukawa_FFH",
        (0, 0, 0, 1, 0, 1, 1): "required_seesaw_FBN",
        (0, 0, 0, 0, 0, 0, 2): "required_singlet_mass_NN",
        (0, 0, 0, 0, 2, 0, 0): "required_Higgs_mass_HH",
        (1, 0, 0, 0, 2, 0, 0): "required_DT_EHH",
        (0, 0, 0, 1, 0, 1, 0): "dangerous_matter_Higgs_bilinear_FB",
    }
    for degree in range(1, 5):
        for counts in compositions(degree, len(SHORT)):
            multiplicity = d5.singlet(monomial_character(counts))
            if multiplicity:
                rows.append(
                    {
                        "degree": degree,
                        "counts": dict(zip(SHORT, counts)),
                        "monomial": monomial_label(counts),
                        "Spin10_singlet_multiplicity": multiplicity,
                        "selector_tag": tags.get(counts, "census_other"),
                    }
                )
    return rows


def required_congruences(charges: Mapping[str, int], modulus: int, w: int) -> dict[str, bool]:
    q = charges
    return {
        "E2": 2 * q["E"] % modulus == w,
        "E3": 3 * q["E"] % modulus == w,
        "A2": 2 * q["A"] % modulus == w,
        "EA2": (q["E"] + 2 * q["A"]) % modulus == w,
        "BC": (q["B"] + q["C"]) % modulus == w,
        "BAC": (q["B"] + q["A"] + q["C"]) % modulus == w,
        "H2": 2 * q["H"] % modulus == w,
        "EH2": (q["E"] + 2 * q["H"]) % modulus == w,
        "FFH": (2 * q["F"] + q["H"]) % modulus == w,
        "FBN": (q["F"] + q["B"] + q["N"]) % modulus == w,
        "NN": 2 * q["N"] % modulus == w,
    }


def cyclic_solutions(modulus: int, is_r: bool) -> list[dict[str, int]]:
    w = 2 % modulus if is_r else 0
    solutions = []
    e_values = [e for e in range(modulus) if 2 * e % modulus == w and 3 * e % modulus == w]
    for e in e_values:
        a_values = [a for a in range(modulus) if 2 * a % modulus == w and (e + 2 * a) % modulus == w]
        h_values = [h for h in range(modulus) if 2 * h % modulus == w and (e + 2 * h) % modulus == w]
        for a, h in itertools.product(a_values, h_values):
            f_values = [f for f in range(modulus) if (2 * f + h) % modulus == w]
            n_values = [n for n in range(modulus) if 2 * n % modulus == w]
            for f, n, c in itertools.product(f_values, n_values, range(modulus)):
                b = (w - c) % modulus
                charges = dict(E=e, A=a, C=c, B=b, H=h, F=f, N=n)
                if all(required_congruences(charges, modulus, w).values()):
                    solutions.append(charges)
    return solutions


def bounded_search(max_modulus: int = 64) -> dict[str, Any]:
    rows = []
    proton_safe = []
    for modulus in range(2, max_modulus + 1):
        for is_r in (False, True):
            w = 2 % modulus if is_r else 0
            solutions = cyclic_solutions(modulus, is_r)
            safe = [q for q in solutions if 4 * q["F"] % modulus != w]
            rows.append(
                {
                    "modulus": modulus,
                    "type": "R" if is_r else "non_R",
                    "solutions_to_required_terms": len(solutions),
                    "solutions_forbidding_F4": len(safe),
                }
            )
            proton_safe.extend((modulus, is_r, q) for q in safe)
    return {"maximum_modulus": max_modulus, "rows": rows, "proton_safe_solutions": proton_safe}


def build_report() -> dict[str, Any]:
    upstream = load_hashed(UPSTREAM)
    census = exact_invariant_census()
    search = bounded_search()
    degree_counts = {
        str(degree): {
            "multidegrees": sum(row["degree"] == degree for row in census),
            "invariant_multiplicity": sum(
                row["Spin10_singlet_multiplicity"] for row in census if row["degree"] == degree
            ),
        }
        for degree in range(1, 5)
    }
    f4 = next(row for row in census if row["selector_tag"] == "fatal_proton_F4")
    symbolic = {
        "non_R": (
            "Required FFH gives 2qF+qH=0 and required H2 gives 2qH=0; "
            "doubling the first equation yields 4qF=0, exactly the FFFF charge. "
            "Independently, if the barC VEV preserves the remnant, FBN plus NN also gives 2qF=0."
        ),
        "R": (
            "With qW=2, simultaneous E2 and E3 imply qE=0 and qW=0 mod N; "
            "therefore N divides 2 and the putative R selector reduces to the Z2/non-R case."
        ),
        "product_groups": (
            "The congruences hold componentwise in every finite Abelian product factor, so taking products cannot evade either proof."
        ),
    }
    integrity = {
        "upstream_is_bound": upstream["core_sha256"] == EXPECTED_UPSTREAM_CORE,
        "representation_dimensions_are_54_45_16_16_10_48_4": tuple(
            d5.cdim(representation_characters()[name]) for name in SHORT
        ) == (54, 45, 16, 16, 10, 48, 4),
        "F4_exists_with_six_family_invariants": f4["Spin10_singlet_multiplicity"] == 6,
        "all_required_anchor_classes_exist": all(
            any(row["selector_tag"] == tag for row in census)
            for tag in (
                "required_Yukawa_FFH",
                "required_seesaw_FBN",
                "required_singlet_mass_NN",
                "required_Higgs_mass_HH",
                "required_DT_EHH",
            )
        ),
        "bounded_search_has_no_proton_safe_solution": not search["proton_safe_solutions"],
        "every_required_solution_allows_F4": all(
            row["solutions_forbidding_F4"] == 0 for row in search["rows"]
        ),
        "no_gate_is_promoted": True,
    }
    failures = [name for name, passed in integrity.items() if not passed]
    if failures:
        raise RuntimeError("V53 selector audit failed: " + ", ".join(failures))
    report: dict[str, Any] = {
        "schema": "susy-v53-proton-safe-selector-no-go-audit-v1",
        "status": STATUS,
        "verdict": {
            "proton_safe_selector_on_declared_action_exists": False,
            "cyclic_search_range": "Z_N and conventional Z_N^R, 2<=N<=64",
            "finite_Abelian_product_escape": False,
            "reason": (
                "The exact Spin(10) census contains six independent family-dressed F16^4 invariants, "
                "and the required V52 terms force their selector charge to equal the superpotential charge."
            ),
        },
        "declared_field_contract": {
            "fields": dict(zip(SHORT, FIELDS)),
            "required_terms": list(required_congruences({name: 0 for name in SHORT}, 2, 0)),
            "scope": "holomorphic superpotential monomials through degree four; family copies are included in the characters",
        },
        "exact_D5_invariant_census": {
            "method": "exact D5 weight characters, symmetric powers, and Weyl-denominator singlet extraction",
            "degree_counts": degree_counts,
            "total_multidegrees": len(census),
            "total_invariant_multiplicity": sum(row["Spin10_singlet_multiplicity"] for row in census),
            "rows_sha256": hashlib.sha256(canonical_bytes(census)).hexdigest(),
            "rows": census,
            "fatal_F4_row": f4,
        },
        "exact_modular_no_go": symbolic,
        "bounded_cyclic_search": search,
        "anomaly_and_parent_assessment": {
            "status": "NO_CANDIDATE_REACHES_ANOMALY_SCREEN",
            "statement": (
                "Because the operator congruences already exclude every candidate, Green-Schwarz universality or discrete-gauge anomaly conditions cannot rescue this unchanged action."
            ),
            "primary_source_context": (
                "The known SO(10)-compatible MSSM Z4R forbids the perturbative mu term and is broken to matter parity; "
                "the four-dimensional simple-GUT R-symmetry no-go independently warns against an exact unbroken R completion."
            ),
        },
        "smallest_escape": {
            "required_action_changes": [
                "replace both H2/EH2 tuned DT mass terms by a natural DT sector that need not allow H10 squared",
                "replace the Majorana NN block by at least three Dirac singlet pairs N+Nc (six singlets total, two more than V52)",
                "add an anomaly-canceling parent/spectator sector or a calculable Green-Schwarz completion",
            ],
            "illustrative_operator_level_Z5_non_R_charges_not_yet_anomaly_complete": {
                "E": 0,
                "A": 0,
                "C": 0,
                "B": 0,
                "F": 1,
                "H": 3,
                "N": 4,
                "Nc": 1,
            },
            "decision": (
                "This Z5 assignment allows FFH, FBN and N*Nc while forbidding F4, but deliberately fails closed as a model: "
                "the old H2/EH2 and NN terms are removed and anomaly-canceling spectators are not constructed."
            ),
        },
        "gate_effect": {
            "G2": "OPEN",
            "G7": "OPEN",
            "G8": "OPEN: the V52 external Z2 is proved insufficient for dimension-five proton safety",
            "clauses_promoted": [],
        },
        "primary_sources": [
            {"title": "A unique Z4R symmetry for the MSSM", "url": "https://arxiv.org/abs/1009.0905"},
            {"title": "No-go theorems for R symmetries in four-dimensional GUTs", "url": "https://arxiv.org/abs/1109.4797"},
            {"title": "Note on discrete gauge anomalies", "url": "https://arxiv.org/abs/hep-th/9109045"},
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
    counts = report["exact_D5_invariant_census"]["degree_counts"]
    return f"""# V53 proton-safe selector audit

Status: `{report['status']}`

## Verdict

No cyclic non-R or conventional discrete-R selector can make the unchanged V52
`54+45+16+bar16+10+4N+3(16F)` action proton-safe while retaining every declared
source, DT, Yukawa and double-seesaw term.  This is an exact operator-congruence
no-go, not a failed guess at charges.

The exact D5 census through superpotential degree four contains
`{report['exact_D5_invariant_census']['total_multidegrees']}` nonzero
multidegrees and `{report['exact_D5_invariant_census']['total_invariant_multiplicity']}`
invariant directions.  Degree-four `F16^4` alone has multiplicity
`{report['exact_D5_invariant_census']['fatal_F4_row']['Spin10_singlet_multiplicity']}`
after the three family copies are included.  Degree counts are `{counts}`.

## Exact obstruction

- Non-R: `FFH` and `H2` imply `4 qF=0`, exactly the `F^4` charge.  With an
  unbroken spinor-Higgs VEV, `F barC N` and `NN` independently force the same result.
- R: `E2` and `E3` require `qE=0` and `qW=0`; a conventional `qW=2` symmetry
  therefore has only the `N|2` cases and reduces to the non-R obstruction.
- Product groups do not help because both statements hold factor by factor.

The exhaustive check over every `Z_N` and `Z_N^R` for `2<=N<=64` finds zero
assignments that allow the required terms and forbid `F16^4`.  No candidate
survives long enough for anomaly cancellation to rescue it.

## Smallest honest escape

The action must change: replace the tuned `H2/EH2` DT block, replace four
Majorana singlets by at least three Dirac pairs, and construct an anomaly-safe
parent/spectator sector.  The report includes a `Z5` operator-level illustration,
but explicitly does not call it anomaly complete.

No G2, G7 or G8 gate is promoted.

Core SHA-256: `{report['core_sha256']}`
"""


def validate(report: Mapping[str, Any]) -> None:
    if report["status"] != STATUS or report["core_sha256"] != canonical_sha(report):
        raise RuntimeError("status/hash drift")
    if report["n_failed_integrity_checks"] or not all(report["integrity_checks"].values()):
        raise RuntimeError("integrity failure")
    if report["verdict"]["proton_safe_selector_on_declared_action_exists"]:
        raise RuntimeError("no-go was overruled")


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
        print("V53_PROTON_SAFE_SELECTOR_NO_GO_AUDIT_CHECK_PASS")
    if not args.write and not args.check:
        print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
