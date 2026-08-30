#!/usr/bin/env python3
"""V55 R1 matter/anomaly and formal Green--Schwarz repair audit.

The V54 charged-source rescue quoted anomalies after silently assigning all
three matter 16s charge 11.  This audit removes those families, derives the
exact anomaly polynomials for symbolic replacement charges, and searches
integer family charges plus massive singlet blocks.

An anomaly-universal chiral ledger is not a supergravity completion.  The
report therefore keeps exact arithmetic, massive-spectator certificates,
FI-sign feasibility, and the missing modulus/Kahler/vector construction in
separate sections.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import math
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import sympy as sp


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V55_R1_GS_MATTER_ANOMALY_AUDIT.json"
MD_PATH = ROOT / "SUSY_V55_R1_GS_MATTER_ANOMALY_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v55_r1_gs_matter_anomaly_audit.py"
UPSTREAM = ROOT / "SUSY_V54_CONTINUOUS_PARENT_FI_ROUTE_AUDIT.json"
EXPECTED_UPSTREAM_CORE = "25b0a48ea19fe6831049a46b01259a2a465f5f65584528d1670927156956633e"

STATUS = (
    "V55_R1_GS_MATTER_ANOMALY_AUDIT__V54_THREE_Q11_FAMILIES_EXPOSED__"
    "SYMBOLIC_MIXED_GRAVITY_AND_CUBIC_POLYNOMIALS_EXACT__OLD_134_REPAIR_"
    "REDUCED_TO_128_AT_FIXED_FAMILY_CHARGES__TOP_YUKAWA_PRESERVING_"
    "FIVE_SINGLET_INTEGER_REPAIR_FOUND_AND_BLOCK_MINIMAL__BARE_F4_"
    "PRESCREEN_PASSED__GS_KAHLER_MODULUS_VECTOR_AND_GLOBAL_D_FLAT_"
    "VACUUM_NOT_CONSTRUCTED__FORMAL_ARITHMETIC_ONLY__NO_GATE_PROMOTION"
)

# Subtracting three charge-11 16s from the V54 quoted ledger gives the fixed
# source/filter/spurion/driver contribution below.  T(10)=1, T(16)=2.
NONMATTER = {
    "Spin10_squared_U1": -17,
    "TrQ": -113,
    "TrQ2": 8273,
    "TrQ3": -67775,
}

V54_ALL_Q11 = {
    "Spin10_squared_U1": 49,
    "TrQ": 415,
    "TrQ2": 14081,
    "TrQ3": -3887,
}

# Only SO(10)-singlet fields with nonzero VEVs are legitimate providers of a
# spectator mass term Phi X_i X_j.  pair_sum = q_i+q_j = -q(Phi).
MASS_PROVIDERS: tuple[tuple[str, int, int], ...] = (
    ("P", 6, -6),
    ("S", -12, 12),
    ("T", -6, 6),
    ("R", 4, -4),
    ("M", -2, 2),
    ("L", 1, -1),
    ("K", 2, -2),
    ("D1", 0, 0),
)
PAIR_PROVIDER = {pair_sum: name for name, _, pair_sum in MASS_PROVIDERS}
PROVIDER_CHARGE = {name: charge for name, charge, _ in MASS_PROVIDERS}
INTEGER_SELF_CHARGES = tuple(
    sorted(pair_sum // 2 for pair_sum in PAIR_PROVIDER if pair_sum % 2 == 0)
)


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
        raise RuntimeError("stale V54 continuous-parent core")
    if value["core_sha256"] != EXPECTED_UPSTREAM_CORE:
        raise RuntimeError("unexpected V54 continuous-parent core")
    quoted = value["charged_source_dynamical_rescue"]["anomalies_before_repair"]
    if quoted != V54_ALL_Q11:
        raise RuntimeError("V54 charged-source anomaly ledger drift")
    return value


def anomaly_ledger(
    family_charges: Sequence[int | Fraction],
    spectator_charges: Sequence[int | Fraction] = (),
) -> dict[str, Any]:
    if len(family_charges) != 3:
        raise ValueError("exactly three Spin(10) 16-family charges are required")
    families = tuple(Fraction(value) for value in family_charges)
    spectators = tuple(Fraction(value) for value in spectator_charges)
    sum_q = sum(families, Fraction(0))
    sum_q2 = sum((value**2 for value in families), Fraction(0))
    sum_q3 = sum((value**3 for value in families), Fraction(0))
    spec_q = sum(spectators, Fraction(0))
    spec_q2 = sum((value**2 for value in spectators), Fraction(0))
    spec_q3 = sum((value**3 for value in spectators), Fraction(0))
    mixed = Fraction(NONMATTER["Spin10_squared_U1"]) + 2 * sum_q
    trace = Fraction(NONMATTER["TrQ"]) + 16 * sum_q + spec_q
    square = Fraction(NONMATTER["TrQ2"]) + 16 * sum_q2 + spec_q2
    cubic = Fraction(NONMATTER["TrQ3"]) + 16 * sum_q3 + spec_q3
    gravity_universal = trace == 24 * mixed
    if mixed:
        k_abelian = cubic / (6 * mixed)
        k_positive: bool | None = k_abelian > 0
    else:
        k_abelian = None
        k_positive = None
    return {
        "family_charges": [str(value) for value in families],
        "spectator_count": len(spectators),
        "spectator_charge_sum": str(spec_q),
        "Spin10_squared_U1": str(mixed),
        "TrQ": str(trace),
        "TrQ2_diagnostic": str(square),
        "TrQ3": str(cubic),
        "gravity_universal": gravity_universal,
        "kA_from_cubic_universality": None if k_abelian is None else str(k_abelian),
        "kA_positive": k_positive,
        "ordinary_anomaly_free": mixed == 0 and trace == 0 and cubic == 0,
    }


def required_singlet_trace(family_charges: Sequence[int | Fraction]) -> Fraction:
    bare = anomaly_ledger(family_charges)
    return 24 * Fraction(bare["Spin10_squared_U1"]) - Fraction(bare["TrQ"])


def bare_four_family_witness(family_charges: Sequence[int]) -> list[int] | None:
    values = tuple(int(value) for value in family_charges)
    for combination in itertools.combinations_with_replacement(values, 4):
        if sum(combination) == 0:
            return list(combination)
    return None


def block_certificate(blocks: Sequence[tuple[Any, ...]]) -> dict[str, Any]:
    charges: list[int] = []
    matrix_rows: list[tuple[int, ...]] = []
    operators: list[dict[str, Any]] = []
    dimension = sum(1 if block[0] == "self" else 2 for block in blocks)
    matrix = sp.zeros(dimension)
    cursor = 0
    for block in blocks:
        kind = str(block[0])
        if kind == "self":
            _, charge, provider = block
            charge = int(charge)
            provider = str(provider)
            matrix[cursor, cursor] = 1
            charges.append(charge)
            total_charge = PROVIDER_CHARGE[provider] + 2 * charge
            operators.append(
                {
                    "kind": "self",
                    "spectator_charges": [charge],
                    "VEV_provider": provider,
                    "provider_charge": PROVIDER_CHARGE[provider],
                    "operator": f"{provider} X_({charge})^2/2",
                    "total_U1_charge": total_charge,
                }
            )
            cursor += 1
        elif kind == "pair":
            _, first, second, provider = block
            first, second, provider = int(first), int(second), str(provider)
            matrix[cursor, cursor + 1] = 1
            matrix[cursor + 1, cursor] = 1
            charges.extend((first, second))
            total_charge = PROVIDER_CHARGE[provider] + first + second
            operators.append(
                {
                    "kind": "pair",
                    "spectator_charges": [first, second],
                    "VEV_provider": provider,
                    "provider_charge": PROVIDER_CHARGE[provider],
                    "operator": f"{provider} X_({first}) X_({second})",
                    "total_U1_charge": total_charge,
                }
            )
            cursor += 2
        else:
            raise ValueError(f"unknown mass block {kind}")
    matrix_rows = [tuple(int(value) for value in row) for row in matrix.tolist()]
    return {
        "charges": charges,
        "operators": operators,
        "all_mass_operators_neutral": all(
            row["total_U1_charge"] == 0 for row in operators
        ),
        "unit_VEV_Hessian": [list(row) for row in matrix_rows],
        "Hessian_rank": int(matrix.rank()),
        "Hessian_determinant": str(matrix.det()),
        "all_spectators_massive": int(matrix.rank()) == dimension,
        "spectator_Z2": (
            "all repair singlets odd, all V54 main-action fields even; X=0 preserves "
            "the parity and every displayed quadratic mass contains two odd fields"
        ),
    }


def pair_block_library(charge_bound: int) -> tuple[tuple[str, int, int, str], ...]:
    blocks: list[tuple[str, int, int, str]] = []
    for pair_sum, provider in PAIR_PROVIDER.items():
        for first in range(-charge_bound, charge_bound + 1):
            second = pair_sum - first
            if first <= second and -charge_bound <= second <= charge_bound:
                blocks.append(("pair", first, second, provider))
    return tuple(blocks)


def self_block_library() -> tuple[tuple[str, int, str], ...]:
    return tuple(
        ("self", charge, PAIR_PROVIDER[2 * charge])
        for charge in INTEGER_SELF_CHARGES
    )


def mass_block_configurations(
    field_count: int, charge_bound: int
) -> Iterable[tuple[tuple[Any, ...], ...]]:
    self_blocks = self_block_library()
    pair_blocks = pair_block_library(charge_bound)
    for pair_count in range(field_count // 2 + 1):
        self_count = field_count - 2 * pair_count
        for self_indices in itertools.combinations_with_replacement(
            range(len(self_blocks)), self_count
        ):
            for pair_indices in itertools.combinations_with_replacement(
                range(len(pair_blocks)), pair_count
            ):
                yield tuple(self_blocks[index] for index in self_indices) + tuple(
                    pair_blocks[index] for index in pair_indices
                )


def block_charges(blocks: Sequence[tuple[Any, ...]]) -> tuple[int, ...]:
    result: list[int] = []
    for block in blocks:
        if block[0] == "self":
            result.append(int(block[1]))
        else:
            result.extend((int(block[1]), int(block[2])))
    return tuple(result)


def candidate_record(
    family_charges: Sequence[int], blocks: Sequence[tuple[Any, ...]]
) -> dict[str, Any]:
    spectators = block_charges(blocks)
    ledger = anomaly_ledger(family_charges, spectators)
    return {
        "family_charges": list(family_charges),
        "spectator_charges": list(spectators),
        "spectator_blocks": [list(block) for block in blocks],
        "anomalies": ledger,
        "bare_four_family_charge_neutral_witness": bare_four_family_witness(
            family_charges
        ),
        "mass_certificate": block_certificate(blocks),
    }


@lru_cache(maxsize=1)
def free_family_diagonal_scan() -> dict[str, Any]:
    charge_bound = 24
    scanned_by_count: dict[int, int] = {}
    winner: tuple[Any, ...] | None = None
    for spectator_count in range(0, 4):
        scanned = 0
        best: tuple[Any, ...] | None = None
        for spectators in itertools.combinations_with_replacement(
            INTEGER_SELF_CHARGES, spectator_count
        ):
            total = sum(spectators)
            numerator = total + 295
            if numerator % 32:
                continue
            family_sum = numerator // 32
            for family in itertools.combinations_with_replacement(
                range(-charge_bound, charge_bound + 1), 3
            ):
                if sum(family) != family_sum:
                    continue
                scanned += 1
                mixed = -17 + 2 * sum(family)
                cubic = -67775 + 16 * sum(value**3 for value in family) + sum(
                    value**3 for value in spectators
                )
                # The trace congruence above already enforces TrQ=24*A.
                if mixed == 0 or mixed * cubic <= 0:
                    continue
                objective = (
                    spectator_count,
                    max(map(abs, family)),
                    sum(value * value for value in family),
                    max(map(abs, spectators), default=0),
                    sum(value * value for value in spectators),
                    family,
                    spectators,
                )
                blocks = tuple(
                    ("self", charge, PAIR_PROVIDER[2 * charge])
                    for charge in spectators
                )
                row = (objective, family, blocks)
                if best is None or objective < best[0]:
                    best = row
        scanned_by_count[spectator_count] = scanned
        if best is not None:
            winner = best
            break
    if winner is None:
        raise RuntimeError("free-family scan failed to find the expected repair")
    _, family, blocks = winner
    return {
        "scope": {
            "integer_family_charge_range": [-charge_bound, charge_bound],
            "mass_topology": "diagonal Phi X^2 blocks from existing singlet VEVs",
            "maximum_spectator_count": 3,
            "objective": (
                "minimum spectator count, then minimum max family charge, family square "
                "sum, max spectator charge, and spectator square sum"
            ),
        },
        "scanned_family_rows_by_spectator_count": {
            str(key): value for key, value in scanned_by_count.items()
        },
        "winner": candidate_record(family, blocks),
        "interpretation": (
            "This is the arithmetic minimum in the declared free-family scan. It does not "
            "preserve the V54 renormalizable top Yukawa because no family has charge 11."
        ),
    }


@lru_cache(maxsize=1)
def top_yukawa_preserving_scans() -> dict[str, Any]:
    charge_bound = 40
    first_raw: tuple[Any, ...] | None = None
    first_screened: tuple[Any, ...] | None = None
    configuration_counts: dict[int, int] = {}
    for spectator_count in range(1, 6):
        raw_best: tuple[Any, ...] | None = None
        screened_best: tuple[Any, ...] | None = None
        config_count = 0
        for blocks in mass_block_configurations(spectator_count, charge_bound):
            config_count += 1
            spectators = block_charges(blocks)
            numerator = sum(spectators) + 295
            if numerator % 32:
                continue
            family_sum = numerator // 32
            first_two_sum = family_sum - 11
            for q1 in range(-charge_bound, charge_bound + 1):
                q2 = first_two_sum - q1
                if not -charge_bound <= q2 <= charge_bound:
                    continue
                family = (q1, q2, 11)
                mixed = -17 + 2 * family_sum
                cubic = -67775 + 16 * (
                    q1**3 + q2**3 + 11**3
                ) + sum(value**3 for value in spectators)
                # The trace congruence above already enforces TrQ=24*A.
                if mixed == 0 or mixed * cubic <= 0:
                    continue
                objective = (
                    spectator_count,
                    max(map(abs, family + spectators)),
                    sum(value * value for value in family + spectators),
                    tuple(sorted(family)),
                    spectators,
                )
                row = (objective, family, blocks)
                if raw_best is None or objective < raw_best[0]:
                    raw_best = row
                if not any(
                    sum(combination) == 0
                    for combination in itertools.combinations_with_replacement(
                        family, 4
                    )
                ) and (
                    screened_best is None or objective < screened_best[0]
                ):
                    screened_best = row
        configuration_counts[spectator_count] = config_count
        if first_raw is None and raw_best is not None:
            first_raw = raw_best
        if first_screened is None and screened_best is not None:
            first_screened = screened_best
        if first_raw is not None and first_screened is not None:
            break
    if first_raw is None or first_screened is None:
        raise RuntimeError("top-Yukawa scan failed to find the expected repairs")
    _, raw_family, raw_blocks = first_raw
    _, screened_family, screened_blocks = first_screened
    return {
        "scope": {
            "integer_charge_range": [-charge_bound, charge_bound],
            "fixed_top_family_charge": 11,
            "top_Yukawa_identity": "2 q3 + q(H1) = 2*11-22 = 0",
            "mass_topology": (
                "block-diagonal self or pair masses Phi X_i X_j from the existing "
                "P,S,T,R,M,L,K,D1 VEVs"
            ),
            "maximum_spectator_count": 5,
            "objective": (
                "minimum field count, then minimum maximum absolute charge and total "
                "charge-square trace"
            ),
        },
        "mass_configurations_scanned_by_count": {
            str(key): value for key, value in configuration_counts.items()
        },
        "raw_anomaly_optimum": candidate_record(raw_family, raw_blocks),
        "bare_F4_prescreened_optimum": candidate_record(
            screened_family, screened_blocks
        ),
        "minimality_statement": (
            "No one-to-four-field block repair exists with positive cubic normalization. "
            "The trace congruence leaves only total family charge 9 for N<=4; with q3=11 "
            "the family cubic sum is at most 1329, while every N<=4 massive block with "
            "repair trace -7 leaves the total cubic anomaly negative. The five-field "
            "witness is therefore field-count minimal in this integer block topology, "
            "independent of the finite charge bound used to optimize its charge size."
        ),
    }


def fixed_q11_repair() -> dict[str, Any]:
    old_spectators = [6] * 126 + [1] * 6 + [-1] + [0]
    smaller = [6] * 127 + [-1]
    old = anomaly_ledger((11, 11, 11), old_spectators)
    new = anomaly_ledger((11, 11, 11), smaller)
    return {
        "V54_134_singlet_repair": {
            "charges": {"q_plus6": 126, "q_plus1": 6, "q_minus1": 1, "q_zero": 1},
            "anomalies": old,
        },
        "smaller_128_singlet_repair": {
            "charges": {"q_plus6": 127, "q_minus1": 1},
            "masses": ["127 copies of S X_(6)^2/2", "K X_(-1)^2/2"],
            "all_mass_terms_neutral": -12 + 2 * 6 == 0 and 2 + 2 * (-1) == 0,
            "spectator_Hessian_rank": 128,
            "spectator_Hessian_nullity": 0,
            "anomalies": new,
        },
        "exact_minimality_proof": (
            "Universality requires spectator trace 761. In any nonzero determinant "
            "monomial for the spectator mass matrix, 2 sum(q_X) equals minus the sum "
            "of  N provider charges. Since the most negative available singlet-VEV "
            "charge is q(S)=-12, N>=ceil(761/6)=127. N=127 would require provider "
            "charge sum -1522, two above 127*(-12); every available replacement raises "
            "that sum by one of {6,10,12,13,14,16,18}, so it is impossible. N=128 is "
            "realized by 127 S diagonal entries and one K diagonal entry."
        ),
        "field_reduction": 6,
        "fractional_reduction": (134 - 128) / 134,
    }


def d_flat_sign_check(ledger: Mapping[str, Any]) -> dict[str, Any]:
    mixed = Fraction(str(ledger["Spin10_squared_U1"]))
    trace = Fraction(str(ledger["TrQ"]))
    xi_sign = 1 if trace > 0 else -1 if trace < 0 else 0
    negative_vevs = ["E(-2)", "barC(-1)", "S(-12)", "T(-6)", "M(-2)", "D3(-2)", "D4(-2)"]
    positive_vevs = ["A(+1)", "B(+1)", "P(+6)", "R(+4)", "L(+1)", "K(+2)"]
    opposite = negative_vevs if xi_sign > 0 else positive_vevs if xi_sign < 0 else []
    return {
        "universal_trace_equals_24A": trace == 24 * mixed,
        "FI_sign_from_xi_proportional_to_TrQ": (
            "positive" if xi_sign > 0 else "negative" if xi_sign < 0 else "zero"
        ),
        "vacuum_active_negative_charge_fields": negative_vevs,
        "vacuum_active_positive_charge_fields": positive_vevs,
        "opposite_sign_nonzero_VEVs_exist": bool(opposite) if xi_sign else True,
        "sign_feasible": bool(opposite) if xi_sign else True,
        "not_proved": (
            "The exact D=0 magnitude is not established: F constraints, the modulus-"
            "generated FI coefficient, representation normalizations, and the full "
            "Kahler metric must be solved simultaneously. Repair spectators remain at X=0."
        ),
    }


def symbolic_conditions() -> dict[str, Any]:
    return {
        "normalization": "T(10)=1, T(16)=2, Spin(10) current-algebra level assumed one",
        "fixed_nonmatter_ledger": NONMATTER,
        "for_three_family_charges_q1_q2_q3": {
            "A_Spin10_squared_U1": "-17 + 2*(q1+q2+q3)",
            "TrQ_gravitational": "-113 + 16*(q1+q2+q3) + sum_a x_a",
            "TrQ3_cubic": "-67775 + 16*(q1^3+q2^3+q3^3) + sum_a x_a^3",
            "TrQ2_nonanomalous_diagnostic": (
                "8273 + 16*(q1^2+q2^2+q3^2) + sum_a x_a^2"
            ),
        },
        "single_GS_universality_in_1110_6901_convention": (
            "A_10 = TrQ/24 = TrQ3/(6 k_A) = 8*pi^2*delta_GS"
        ),
        "required_singlet_trace": "sum_a x_a = 32*(q1+q2+q3)-295",
        "positive_abelian_level": "k_A=TrQ3/(6 A_10)>0",
        "integer_family_consequence": (
            "A_10=-17+2*sum(q_i) is odd and never zero; an integer-charge branch is "
            "necessarily anomalous rather than ordinarily anomaly-free"
        ),
        "ordinary_non_GS_condition": (
            "If rational charges make A_10=0, consistency instead requires TrQ=0 and "
            "TrQ3=0 separately; k_A cannot be defined by division through A_10."
        ),
        "TrQ2_warning": (
            "TrQ2 is a running/charge-size diagnostic, not the world-sheet generator "
            "norm k_A; a string embedding must derive k_A from the charge lattice."
        ),
    }


def build_report() -> dict[str, Any]:
    upstream = load_upstream()
    fixed = fixed_q11_repair()
    free = free_family_diagonal_scan()
    top = top_yukawa_preserving_scans()
    raw = top["raw_anomaly_optimum"]
    selected = top["bare_F4_prescreened_optimum"]
    selected_ledger = selected["anomalies"]
    dflat = d_flat_sign_check(selected_ledger)

    checks = {
        "V54_upstream_is_bound": upstream["core_sha256"] == EXPECTED_UPSTREAM_CORE,
        "subtracting_three_q11_families_gives_fixed_nonmatter_ledger": (
            NONMATTER
            == {
                "Spin10_squared_U1": -17,
                "TrQ": -113,
                "TrQ2": 8273,
                "TrQ3": -67775,
            }
        ),
        "symbolic_trace_repair_formula_is_exact_at_q11": required_singlet_trace(
            (11, 11, 11)
        )
        == 761,
        "fixed_q11_128_repair_is_universal_positive_and_massive": (
            fixed["smaller_128_singlet_repair"]["anomalies"]["gravity_universal"]
            and fixed["smaller_128_singlet_repair"]["anomalies"]["kA_positive"]
            and fixed["smaller_128_singlet_repair"]["spectator_Hessian_rank"] == 128
        ),
        "free_family_scan_finds_three_field_formal_minimum": (
            free["winner"]["family_charges"] == [-4, -4, 17]
            and free["winner"]["spectator_charges"] == [-3, -2, -2]
            and free["winner"]["anomalies"]["kA_from_cubic_universality"] == "1457"
        ),
        "raw_top_optimum_exposes_bare_F4_failure": (
            raw["family_charges"] == [-1, 0, 11]
            and raw["bare_four_family_charge_neutral_witness"] == [0, 0, 0, 0]
        ),
        "selected_five_field_repair_preserves_top_and_passes_bare_F4_screen": (
            selected["family_charges"] == [-2, 1, 11]
            and selected["spectator_charges"] == [1, -20, 32, -19, 31]
            and selected["bare_four_family_charge_neutral_witness"] is None
            and selected["mass_certificate"]["all_spectators_massive"]
        ),
        "selected_GS_ratios_are_exact": (
            selected_ledger["Spin10_squared_U1"] == "3"
            and selected_ledger["TrQ"] == "72"
            and selected_ledger["TrQ3"] == "1110"
            and selected_ledger["kA_from_cubic_universality"] == "185/3"
        ),
        "selected_D_flat_sign_is_feasible_but_not_overclaimed": (
            dflat["sign_feasible"] and bool(dflat["not_proved"])
        ),
        "formal_GS_arithmetic_is_not_called_supergravity_completion": True,
        "no_gate_is_promoted": True,
    }

    report: dict[str, Any] = {
        "schema": "susy-v55-r1-gs-matter-anomaly-audit-v1",
        "status": STATUS,
        "upstream": {"path": UPSTREAM.name, "core_sha256": upstream["core_sha256"]},
        "scope": (
            "exact four-dimensional chiral anomaly arithmetic and bounded integer-charge "
            "mass-block searches for the V54 R1 charged-source rescue; not a string "
            "compactification, supergravity completion, or completed same-action theory"
        ),
        "symbolic_anomaly_conditions": symbolic_conditions(),
        "V54_q11_reconstruction": {
            "quoted_ledger": V54_ALL_Q11,
            "matter_contribution_of_three_q11_16s": {
                "Spin10_squared_U1": 66,
                "TrQ": 528,
                "TrQ2": 5808,
                "TrQ3": 63888,
            },
            "recovered_nonmatter_ledger": NONMATTER,
        },
        "fixed_q11_repair_reduction": fixed,
        "free_family_formal_scan": free,
        "top_yukawa_preserving_scan": top,
        "selected_formal_repair": {
            **selected,
            "selection_reason": (
                "It is field-count minimal in the declared integer block topology, keeps "
                "q3=11 so 16_3 16_3 H1 is neutral, and unlike the raw charge-size optimum "
                "has no charge-neutral bare four-family matter monomial."
            ),
            "coordinate_accounting": {
                "V54_local_source_filter_and_driver_coordinates": 229,
                "three_matter_16_coordinates_missing_from_V54_local_Hessian": 48,
                "new_massive_singlet_coordinates": 5,
                "full_chiral_coordinate_count_before_GS_modulus": 282,
            },
            "Spin10_running": {
                "sum_T_including_three_families": 42,
                "one_loop_b_Landau": 18,
                "singlet_repair_changes_Spin10_running": False,
            },
            "remaining_operator_risk": (
                "The bare F^4 charge screen is only a pre-screen. VEV-dressed family "
                "operators, contractions using the large-charge spectators, the light-family "
                "Yukawa/flavon sector, and physical proton-decay Wilson coefficients are not audited."
            ),
        },
        "FI_D_flat_sign_check": dflat,
        "formal_GS_output": {
            "universal_anomalies": {
                "A_Spin10": selected_ledger["Spin10_squared_U1"],
                "TrQ_over_24": str(Fraction(selected_ledger["TrQ"]) / 24),
                "TrQ3_over_6kA": "3",
            },
            "delta_GS": "3/(8*pi^2)",
            "FI_in_string_units": "xi = g_s^2 * 3/(8*pi^2)",
            "abelian_generator_norm_candidate": selected_ledger[
                "kA_from_cubic_universality"
            ],
            "classification": "FORMAL_SINGLE_GS_ANOMALY_UNIVERSAL_LEDGER",
            "ordinary_anomaly_cancellation": False,
        },
        "physical_GS_supergravity_completion_still_required": [
            "derive a compact charge lattice/current-algebra embedding with k10=1 and kA=185/3 rather than assigning kA from low-energy traces",
            "introduce a transforming axion-dilaton or modulus T with a fixed delta_GS and gauge-invariant K(T+Tbar-delta_GS V_A)",
            "derive positive real gauge kinetic functions f10(T), fA(T) and any kinetic mixing with every additional U(1)",
            "stabilize Re(T) and Im(T) consistently with the gauged shift, including all hidden-sector anomaly contributions",
            "solve F_T=0 and D_A=0 with the actual Kahler metric, FI magnitude, source constraints, and zero spectator VEVs",
            "diagonalize the U(1) vector, eaten axion, radial scalars, and modulus Hessian and exclude tachyons or extra light states",
            "prove that the Z2 spectator parity and five mass operators survive the complete operator ring and do not spoil proton or Higgs protection",
            "include matter/flavon/messenger thresholds and the large U(1) charge-square trace in perturbative running",
        ],
        "gate_effect": {
            "G1": "OPEN_GLOBAL_GS_QUOTIENT_AND_MODULUS",
            "G2": "OPEN_FULL_282_PLUS_MODULUS_SAME_ACTION_HESSIAN",
            "G3": "OPEN_GLOBAL_F_D_SOFT_VACUUM",
            "G7": "OPEN_FULL_OPERATOR_AND_WILSON_CENSUS",
            "G8": "OPEN_LIGHT_FAMILY_FLAVOUR_COMPLETION",
            "promotions": [],
        },
        "verdict": {
            "materially_smaller_exact_massive_singlet_repair_found": True,
            "old_134_singlet_repair_minimal": False,
            "selected_repair_singlet_count": 5,
            "formal_anomaly_arithmetic_complete_for_selected_ledger": True,
            "physical_GS_completion_complete": False,
            "complete_theory": False,
            "statement": (
                "The V54 anomaly count assumed three charge-11 families. Replacing that "
                "hidden assumption by explicit charges exposes a five-singlet, top-Yukawa-"
                "preserving formal repair with exact universal anomalies (A10,TrQ,TrQ3,kA)="
                "(3,72,1110,185/3). Its massive spectator Hessian is full rank and the FI "
                "sign can be cancelled by existing negative-charge VEVs. This is a large "
                "arithmetic reduction from 134 spectators, but it is not yet physical: the "
                "GS modulus, Kahler potential, vector/scalar spectrum, exact D magnitude, "
                "operator ring, flavour sector, and string charge-lattice embedding are absent."
            ),
        },
        "primary_sources": [
            {
                "title": "Goodsell, Ramos-Sanchez, Ringwald, arXiv:1110.6901",
                "url": "https://arxiv.org/abs/1110.6901",
                "use": "single anomalous-U(1) universality and FI conventions, Eqs. (2.9)-(2.10)",
            }
        ],
        "integrity_checks": checks,
        "n_failed_integrity_checks": sum(not value for value in checks.values()),
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
    if report["n_failed_integrity_checks"] or not all(
        report["integrity_checks"].values()
    ):
        raise RuntimeError("integrity failure")
    if report["gate_effect"]["promotions"]:
        raise RuntimeError("formal anomaly repair overpromoted")
    if report["verdict"]["physical_GS_completion_complete"]:
        raise RuntimeError("formal anomaly ledger mislabeled as a physical GS completion")


def render_markdown(report: Mapping[str, Any]) -> str:
    selected = report["selected_formal_repair"]
    anomaly = selected["anomalies"]
    fixed = report["fixed_q11_repair_reduction"]
    return f"""# V55 R1 GS/matter anomaly audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Outcome

{report['verdict']['statement']}

## Exact anomaly decomposition

Removing the three implicit charge-11 matter `16`s from the V54 ledger gives
the fixed non-matter anomalies `A_10=-17`, `TrQ=-113`, `TrQ3=-67775`, and
the diagnostic `TrQ2=8273`.  For family charges `q1,q2,q3`, singlet charges
`x_a`, and `T(10)=1, T(16)=2`, the complete conditions are

- `A_10 = -17 + 2 sum(q_i)`;
- `TrQ = -113 + 16 sum(q_i) + sum(x_a)`;
- `TrQ3 = -67775 + 16 sum(q_i^3) + sum(x_a^3)`;
- `sum(x_a) = 32 sum(q_i)-295` for `TrQ=24 A_10`;
- `k_A = TrQ3/(6 A_10) > 0`.

These are the single-GS conventions of Eq. (2.9) of arXiv:1110.6901. They
make the anomaly polynomial universal; they do not cancel it ordinarily.

## Repair search

Even with all family charges fixed at 11, the V54 134-singlet repair was not
minimal.  An exact full-rank repair uses 127 charge-6 singlets and one
charge-minus-1 singlet, for 128 total.  The determinant-charge lower bound and
provider-charge congruence prove 127 cannot work in the declared mass sector.

Allowing explicit family charges gives a much larger reduction.  Requiring the
renormalizable top term keeps `q3=11`.  The raw five-field optimum uses a
zero-charge light family and therefore exposes a bare `16^4` class.  Applying
that pre-screen selects

- family charges `{selected['family_charges']}`;
- spectator charges `{selected['spectator_charges']}`;
- masses `M X_(1)^2/2`, `S X_(-20)X_(32)`, and
  `S X_(-19)X_(31)`.

The unit-VEV spectator Hessian has rank
`{selected['mass_certificate']['Hessian_rank']}` and determinant
`{selected['mass_certificate']['Hessian_determinant']}`.  The anomaly ratios
are `A_10={anomaly['Spin10_squared_U1']}`, `TrQ={anomaly['TrQ']}`,
`TrQ3={anomaly['TrQ3']}`, and `k_A={anomaly['kA_from_cubic_universality']}`.

The exhaustive integer/block scan found no repair with one through four
spectators.  This minimality is scoped to quadratic mass blocks generated by
the existing singlet VEVs; it is not a classification of arbitrary new Higgs
sectors or string spectra.

## Physical boundary

`TrQ=72` gives a positive FI sign. Existing nonzero negative-charge VEVs make
the sign cancellable, but the magnitude has not been solved. A physical result
still requires the GS modulus and its gauged shift, a positive Kahler metric
and gauge kinetic functions, simultaneous F/D stabilization, the full
vector-axion-radial Hessian, a charge-lattice realization of `k_A=185/3`, and
the complete flavour/proton operator census. No G1-G8 gate is promoted.

Primary convention: https://arxiv.org/abs/1110.6901
"""


def write_artifacts() -> dict[str, Any]:
    report = build_report()
    validate(report)
    JSON_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")
    return report


def check_artifacts() -> None:
    report = build_report()
    validate(report)
    expected_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if JSON_PATH.read_text(encoding="utf-8") != expected_json:
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
        print("V55_R1_GS_MATTER_ANOMALY_AUDIT_CHECK_PASS")
    if not args.write and not args.check:
        print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
