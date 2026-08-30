#!/usr/bin/env python3
"""Fail-closed V62 audit: the localized Z4R anomaly ledger and its GS sector.

V61 proved the unique Z4R selector class for the Spin(11) route and left one
blocking obligation sharply defined: the fixed-point-localized Z4R anomaly
ledger and the unexhibited Green-Schwarz axion.  V62 computes that ledger
exactly and constructs the new sector that cancels it.

Exact results certified here:

1. Per-wall mixed Z4R-gauge^2 anomaly ledger.  Bulk fermions localize half of
   their locally-even trace at each wall (Arkani-Hamed-Cohen-Georgi; von
   Gersdorff-Quiros).  With the V61 charges the matter sixteens and the
   mirror-32 mediators drop out entirely (fermion charge zero), so the ledger
   is carried by the V gauginos (+1), the Sigma fermions (-1) and the y=0 rank
   sector.  The result is A(Spin10)|_0 = 1/2 and, at the Spin(4)xSpin(7) wall,
   A = (-5/2, -5/2, +1/2) for (SU2_L, SU2_R, Spin7).

2. Three independent integrated-matching validations: the wall sums restricted
   to SU(2)_L, SU(2)_R and SU(4) equal the direct 4D zero-mode ledgers of the
   pre-rank-breaking orbifold theory.

3. A matter-free nonuniversality theorem at y=L: the SU(2) and Spin(7)
   coefficients differ by exactly -3, an odd amount fixed purely by dual
   Coxeter numbers against coset indices, so no single wall-universal axion
   coupling can cancel the wall phases.  This is the same disease that killed
   the corrected heterotic candidate in V60 -- but here wall locality permits
   independent per-factor couplings, so it is curable inside the EFT.

4. The quantized GS sector.  Demanding that one axion with Z4R shift s/4 of a
   period cancels every wall phase gives the congruence c*s = -2A mod 4 per
   wall factor.  The system is solvable iff s is odd (the axion must shift by
   a faithful quarter period), and then the four couplings are unique mod 4:
   (c_Spin10, c_SU2L, c_SU2R, c_SO7) = (3,1,1,3) for s=1.  This sector is the
   new action content of route B62.

Not certified: the post-rank-breaking inflow rearrangement (the wall-Higgsed
KK towers must carry exact flow deficits -2 for SU(3) and -3 for SU(2), which
zero-mode matching alone cannot fix), saxion stabilization, the Dai-Freed
phase, the KK determinant and a UV regulator.  Strict G1 stays open and no
gate is promoted.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V62_SPIN11_LOCALIZED_Z4R_ANOMALY_GS_AUDIT.json"
MD_PATH = ROOT / "SUSY_V62_SPIN11_LOCALIZED_Z4R_ANOMALY_GS_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v62_spin11_localized_z4r_anomaly_gs_audit.py"
V61_ROUTE_PATH = ROOT / "SUSY_V61_SPIN11_Z4R_SELECTOR_ESCAPE_AUDIT.json"
V61_MASTER_PATH = ROOT / "SUSY_V61_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"

EXPECTED_V61_ROUTE_CORE = (
    "6d6107dea91e18e7d34e4560ad8003cd8c38eef5c788b2ebd148bb3795b2c33a"
)
EXPECTED_V61_MASTER_CORE = (
    "a230fda5699b3bd81552317b94733a9f537b0e9ae2a6c35f644830511fa7a810"
)

MODULUS = 4

STATUS = (
    "V62_SPIN11_LOCALIZED_Z4R_LEDGER_AND_QUANTIZED_GS_SECTOR__EXACT_PER_WALL_"
    "ANOMALY_LEDGER_COMPUTED__MATTER_AND_MIRROR_MEDIATORS_DROP_OUT_AT_CHARGE_"
    "ONE__THREE_INTEGRATED_MATCHING_CHECKS_PASS__SPIN4_SPIN7_WALL_"
    "NONUNIVERSAL_BY_MINUS_THREE_FROM_PURE_GROUP_THEORY__SINGLE_UNIVERSAL_"
    "WALL_COUPLING_IMPOSSIBLE__PER_FACTOR_QUANTIZED_COUPLINGS_EXIST_UNIQUE_"
    "MOD_4__AXION_SHIFT_MUST_BE_FAITHFUL_ODD_QUARTER_PERIOD__CANDIDATE_GS_"
    "SECTOR_EXHIBITED__POST_VEV_INFLOW_DEFICITS_MINUS_2_AND_MINUS_3_OPEN__"
    "SAXION_STABILIZATION_DAI_FREED_KK_UV_OPEN__STRICT_G1_OPEN__ZERO_GATES_"
    "CLOSED"
)

CLASSIFICATION = (
    "EXACT_Z4R_SELECTOR_WITH_EXACT_LOCALIZED_LEDGER_AND_UNIQUE_QUANTIZED_GS_"
    "COUPLINGS__POST_VEV_INFLOW_AND_SUSY_COMPLETION_OPEN"
)

PRIMARY_SOURCES = [
    {
        "id": "ARKANI_HAMED_COHEN_GEORGI_2001",
        "title": "Anomalies on orbifolds",
        "authors": "Nima Arkani-Hamed, Andrew G. Cohen and Howard Georgi",
        "arxiv": "hep-th/0103135",
        "url": "https://arxiv.org/abs/hep-th/0103135",
        "scope": (
            "The bulk-fermion anomaly on S1/Z2 localizes half of the zero-mode "
            "anomaly at each fixed point; source of the 1/2 weights used here."
        ),
    },
    {
        "id": "SCRUCCA_SERONE_SILVESTRINI_ZWIRNER_2001",
        "title": "Anomalies in orbifold field theories",
        "authors": "C. A. Scrucca, M. Serone, L. Silvestrini and F. Zwirner",
        "arxiv": "hep-th/0110073",
        "url": "https://arxiv.org/abs/hep-th/0110073",
        "scope": (
            "Localized anomalies exist even without anomalous zero modes; "
            "justifies auditing the per-wall ledger and not only the 4D one."
        ),
    },
    {
        "id": "VON_GERSDORFF_QUIROS_2003",
        "title": "Localized anomalies in orbifold gauge theories",
        "authors": "Gero von Gersdorff and Mariano Quiros",
        "arxiv": "hep-th/0305024",
        "url": "https://arxiv.org/abs/hep-th/0305024",
        "scope": (
            "Fixed-point anomaly decomposition and the bulk-exchange conditions "
            "that define the still-open post-VEV inflow obligation."
        ),
    },
    {
        "id": "IBANEZ_1992",
        "title": "More about discrete gauge anomalies",
        "authors": "Luis E. Ibanez",
        "arxiv": "hep-th/9202046",
        "url": "https://arxiv.org/abs/hep-th/9202046",
        "scope": "Discrete anomaly phases per instanton number; congruence conventions.",
    },
    {
        "id": "ARAKI_ET_AL_2008",
        "title": "(Non-)Abelian discrete anomalies",
        "authors": (
            "Takeshi Araki, Tatsuo Kobayashi, Jisuke Kubo, Saul Ramos-Sanchez, "
            "Michael Ratz and Patrick K. S. Vaudrevange"
        ),
        "arxiv": "0805.0207",
        "url": "https://arxiv.org/abs/0805.0207",
        "scope": "Path-integral discrete anomaly and its Green-Schwarz repair by an axion shift.",
    },
    {
        "id": "LEE_ET_AL_2010",
        "title": "A unique Z4R symmetry for the MSSM",
        "authors": "Hyun Min Lee et al.",
        "arxiv": "1009.0905",
        "url": "https://arxiv.org/abs/1009.0905",
        "scope": "The 4D Z4R selector whose 5D localized completion is audited here.",
    },
    {
        "id": "GARCIA_ETXEBARRIA_MONTERO_2018",
        "title": "Dai-Freed anomalies in particle physics",
        "authors": "Inaki Garcia-Etxebarria and Miguel Montero",
        "arxiv": "1808.00009",
        "url": "https://arxiv.org/abs/1808.00009",
        "scope": "Framework for the still-open Dai-Freed obligation with the R twist.",
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


def sha256_file(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def load_bound(path: Path, expected: str, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"missing {label}: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    actual = canonical_sha(value)
    if value.get("core_sha256") != actual:
        raise RuntimeError(f"{label} canonical core is stale")
    if actual != expected:
        raise RuntimeError(f"unexpected {label} canonical core")
    return value


def conventions() -> dict[str, Any]:
    return {
        "measure_phase": (
            "under one Z4R generator in an instanton-n background of factor G "
            "the fermion measure produces exp(2 pi i n Ahat_G / 4) with "
            "Ahat_G = sum over Weyl fermions of r_f * 2 T(R_f), r_f the fermion "
            "R charge and T(fund SU(N)) = 1/2, T(vector SO(N)) = 1"
        ),
        "doubled_integer_ledger": "Ahat = 2A is used so every entry is an integer",
        "bulk_localization_weight": (
            "a bulk fermion contributes 1/2 of its locally-even trace at each "
            "wall (Arkani-Hamed-Cohen-Georgi; von Gersdorff-Quiros)"
        ),
        "wall_fields_weight": "wall-localized 4D fermions contribute with weight 1",
        "fermion_charges": {
            "V_gauginos": 1,
            "Sigma_fermions": -1,
            "matter_16_fermions": 0,
            "mirror_32_fermions": 0,
            "C_and_Cbar_fermions": -1,
            "S_and_T_fermions": 1,
        },
        "charge_zero_dropout": (
            "the three matter sixteens and every mirror-32 mediator carry "
            "fermion charge zero and drop out of the entire localized ledger; "
            "this is special to the unique V61 charge assignment"
        ),
    }


def projector_block_audit() -> dict[str, Any]:
    """Recompute the Spin(11) adjoint blocks from the V59 parity vectors."""

    p0 = [1] * 10 + [-1]
    p1 = [1] * 4 + [-1] * 7
    blocks: dict[str, dict[str, Any]] = {}
    for i, j in itertools.combinations(range(11), 2):
        v_parity = (p0[i] * p0[j], p1[i] * p1[j])
        if i < 4 and j < 4:
            name = "AA"
        elif 4 <= i < 10 and 4 <= j < 10:
            name = "BB"
        elif i < 4 and 4 <= j < 10:
            name = "AB"
        elif i < 4 and j == 10:
            name = "Ac"
        else:
            name = "Bc"
        entry = blocks.setdefault(
            name,
            {
                "multiplicity": 0,
                "V_parity": list(v_parity),
                "Sigma_parity": [-v_parity[0], -v_parity[1]],
            },
        )
        entry["multiplicity"] += 1
    v_even_0 = sum(
        b["multiplicity"] for b in blocks.values() if b["V_parity"][0] == 1
    )
    sigma_even_0 = sum(
        b["multiplicity"] for b in blocks.values() if b["Sigma_parity"][0] == 1
    )
    v_even_l = sum(
        b["multiplicity"] for b in blocks.values() if b["V_parity"][1] == 1
    )
    sigma_even_l = sum(
        b["multiplicity"] for b in blocks.values() if b["Sigma_parity"][1] == 1
    )
    return {
        "blocks": blocks,
        "total_generators": sum(b["multiplicity"] for b in blocks.values()),
        "V_even_at_y0": v_even_0,
        "Sigma_even_at_y0": sigma_even_0,
        "V_even_at_yL": v_even_l,
        "Sigma_even_at_yL": sigma_even_l,
        "identifications": {
            "V_even_y0": "adjoint 45 of Spin(10)",
            "Sigma_even_y0": "vector 10 of Spin(10)",
            "V_even_yL": "adjoint 6+21 of Spin(4)xSpin(7)",
            "Sigma_even_yL": "coset (4,7) = ((2,2),7)",
        },
        "matches_V59_projector_data": (
            {name: blocks[name]["multiplicity"] for name in blocks}
            == {"AA": 6, "BB": 15, "AB": 24, "Ac": 4, "Bc": 6}
            and v_even_0 == 45
            and sigma_even_0 == 10
            and v_even_l == 27
            and sigma_even_l == 28
        ),
    }


def index_tables() -> dict[str, Any]:
    """Exact Dynkin indices used by the ledger.

    Normalization: T(fund SU(N)) = 1/2, T(vector SO(N)) = 1.  Then
    T(16 of SO(10)) = 2, T(45) = h_dual(SO(10)) = 8, T(adj SO(7)) = 5,
    T(adj SU(2)) = 2, T(adj SU(4)) = 4, T(6 of SU(4)) = 1.
    Restrictions used for matching (all embeddings have index one):
    16 -> (2,1,4)+(1,2,4bar), 10 -> (2,2,1)+(1,1,6), 45 -> adjoints + (2,2,6),
    7 of SO(7) -> 6+1 of SU(4), 21 of SO(7) -> 15+6, (2,2,7) -> four 7s.
    """

    return {
        "SO10": {"16": 2, "10": 1, "45": 8},
        "SU2_from_SO10": {"16": 2, "10": 1, "45": 8},
        "SU4_from_SO10": {"16": 2, "10": 1, "45": 8},
        "yL_factors": {
            "V_even": {"SU2_L": 2, "SU2_R": 2, "SO7": 5},
            "Sigma_even_coset_227": {"SU2_L": 7, "SU2_R": 7, "SO7": 4},
        },
        "SU4_from_SO7": {"adj_21": 5, "coset_227": 4},
        "PS_zero_modes": {
            "SU2_L": {"PS_gauginos": 2, "Sigma_zero_122": 1, "16": 2, "10": 1},
            "SU2_R": {"PS_gauginos": 2, "Sigma_zero_122": 1, "16": 2, "10": 1},
            "SU4": {"PS_gauginos": 4, "Sigma_zero_122": 0, "16": 2, "10": 1},
        },
    }


def wall_ledgers(tables: Mapping[str, Any]) -> dict[str, Any]:
    half = Fraction(1, 2)

    def y0_ledger(t16: int, t10: int, t45: int) -> tuple[list[dict[str, Any]], Fraction]:
        rows = [
            {"field": "3 x matter 16", "weight": "1", "r": 0, "T": t16, "contribution": "0"},
            {"field": "C (16)", "weight": "1", "r": -1, "T": t16, "contribution": str(-t16)},
            {"field": "Cbar (16bar)", "weight": "1", "r": -1, "T": t16, "contribution": str(-t16)},
            {"field": "T (10)", "weight": "1", "r": 1, "T": t10, "contribution": str(t10)},
            {"field": "S (1)", "weight": "1", "r": 1, "T": 0, "contribution": "0"},
            {"field": "bulk V gauginos (45-even)", "weight": "1/2", "r": 1, "T": t45, "contribution": str(half * t45)},
            {"field": "bulk Sigma fermions (10-even)", "weight": "1/2", "r": -1, "T": t10, "contribution": str(-half * t10)},
            {"field": "mirror-32 mediators", "weight": "1/2", "r": 0, "T": "any", "contribution": "0"},
        ]
        total = -t16 - t16 + t10 + half * t45 - half * t10
        return rows, total

    so10_rows, a0_so10 = y0_ledger(**{
        "t16": tables["SO10"]["16"],
        "t10": tables["SO10"]["10"],
        "t45": tables["SO10"]["45"],
    })

    yl = tables["yL_factors"]
    yl_totals = {}
    yl_rows = []
    for factor in ("SU2_L", "SU2_R", "SO7"):
        v_contrib = half * yl["V_even"][factor]
        s_contrib = -half * yl["Sigma_even_coset_227"][factor]
        yl_rows.append(
            {
                "factor": factor,
                "V_even_T": yl["V_even"][factor],
                "V_contribution": str(v_contrib),
                "Sigma_coset_T": yl["Sigma_even_coset_227"][factor],
                "Sigma_contribution": str(s_contrib),
                "wall_matter": 0,
                "total": str(v_contrib + s_contrib),
            }
        )
        yl_totals[factor] = v_contrib + s_contrib

    return {
        "y0_rows": so10_rows,
        "A_y0_Spin10": str(a0_so10),
        "Ahat_y0_Spin10": int(2 * a0_so10),
        "yL_rows": yl_rows,
        "A_yL": {name: str(value) for name, value in yl_totals.items()},
        "Ahat_yL": {name: int(2 * value) for name, value in yl_totals.items()},
        "left_right_symmetric": yl_totals["SU2_L"] == yl_totals["SU2_R"],
        "_A_y0_fraction": a0_so10,
        "_A_yL_fractions": yl_totals,
    }


def integrated_matching(
    tables: Mapping[str, Any], ledgers: Mapping[str, Any]
) -> dict[str, Any]:
    """Wall sums must equal the direct 4D zero-mode ledgers (index-1 embeddings)."""

    half = Fraction(1, 2)
    a0 = ledgers["_A_y0_fraction"]
    checks = []
    for factor in ("SU2_L", "SU2_R", "SU4"):
        if factor == "SU4":
            a_l = half * tables["SU4_from_SO7"]["adj_21"] - half * tables[
                "SU4_from_SO7"
            ]["coset_227"]
        else:
            a_l = ledgers["_A_yL_fractions"][factor]
        zero = tables["PS_zero_modes"][factor]
        direct = (
            Fraction(zero["PS_gauginos"])
            + Fraction(-1) * zero["Sigma_zero_122"]
            + Fraction(-1) * zero["16"] * 2
            + Fraction(1) * zero["10"]
        )
        checks.append(
            {
                "factor": factor,
                "wall_sum": str(a0 + a_l),
                "direct_4D_zero_mode_ledger": str(direct),
                "match": a0 + a_l == direct,
                "direct_composition": (
                    "PS gauginos(+1) + Sigma zero modes(-1) + C(-1) + Cbar(-1) "
                    "+ T(10)(+1); matter and S contribute zero"
                ),
            }
        )
    return {
        "statement": (
            "for every unbroken 4D factor the sum of the two wall ledgers must "
            "reproduce the direct zero-mode ledger of the orbifold theory "
            "before rank breaking; three independent factors are checked"
        ),
        "checks": checks,
        "all_match": all(row["match"] for row in checks),
    }


def nonuniversality_theorem(ledgers: Mapping[str, Any]) -> dict[str, Any]:
    su2 = ledgers["_A_yL_fractions"]["SU2_L"]
    so7 = ledgers["_A_yL_fractions"]["SO7"]
    difference = su2 - so7
    group_theory = {
        "V_part": "(1/2)[T(adj SU2) - T(adj SO7)] = (1/2)(2-5) = -3/2",
        "Sigma_part": "-(1/2)[T_SU2(2,2,7) - T_SO7(2,2,7)] = -(1/2)(7-4) = -3/2",
        "sum": "-3",
    }
    return {
        "statement": (
            "at the Spin(4)xSpin(7) wall the SU(2) and Spin(7) Z4R anomaly "
            "coefficients differ by exactly -3; the wall hosts no matter, so "
            "the difference is fixed purely by dual Coxeter numbers against "
            "coset indices and cannot be changed without new wall fields or a "
            "different projector"
        ),
        "difference_A": str(difference),
        "difference_Ahat": int(2 * difference),
        "difference_is_odd_integer": difference.denominator == 1
        and difference.numerator % 2 == 1,
        "matter_free_group_theory_origin": group_theory,
        "heterotic_parallel": (
            "the corrected heterotic candidate died of residue nonuniversality "
            "with no repair basis; here the same disease appears localized at "
            "one wall, but wall-localized couplings may be factor-dependent, "
            "so the EFT admits a cure that the modular-locked string basis did "
            "not"
        ),
    }


def gs_congruence_system(ledgers: Mapping[str, Any]) -> dict[str, Any]:
    """Solve c_G * s = -Ahat_G mod 4 for one axion with shift s/4 of a period.

    The axion a has period 2 pi f and Z4R shift a -> a + 2 pi f s/4.  A wall
    coupling (c_G a / f) tr(F Fdual)/(8 pi^2) then shifts every theta_G by
    2 pi c_G s / 4, cancelling the measure phase exp(2 pi i n Ahat_G/4) iff
    c_G s + Ahat_G = 0 mod 4.
    """

    ahat = {
        "Spin10@y0": ledgers["Ahat_y0_Spin10"],
        "SU2_L@yL": ledgers["Ahat_yL"]["SU2_L"],
        "SU2_R@yL": ledgers["Ahat_yL"]["SU2_R"],
        "SO7@yL": ledgers["Ahat_yL"]["SO7"],
    }
    shift_rows = []
    for s in range(MODULUS):
        solutions = {
            name: [c for c in range(MODULUS) if (c * s + a) % MODULUS == 0]
            for name, a in ahat.items()
        }
        solvable = all(bool(v) for v in solutions.values())
        unique = all(len(v) == 1 for v in solutions.values())
        shift_rows.append(
            {
                "s": s,
                "solvable": solvable,
                "unique": unique,
                "couplings_mod_4": {k: v[0] for k, v in solutions.items()}
                if solvable and unique
                else None,
            }
        )
    universal_yl = {
        s: [
            c
            for c in range(MODULUS)
            if all((c * s + ahat[k]) % MODULUS == 0 for k in ahat if "@yL" in k)
        ]
        for s in (1, 3)
    }
    chosen = next(row for row in shift_rows if row["s"] == 1)
    return {
        "Ahat_targets": ahat,
        "congruence": "c_G * s + Ahat_G = 0 mod 4, one axion, per-wall-factor couplings",
        "shift_scan": shift_rows,
        "solvable_shifts": [row["s"] for row in shift_rows if row["solvable"]],
        "even_shift_impossible": all(
            not row["solvable"] for row in shift_rows if row["s"] % 2 == 0
        ),
        "faithful_odd_quarter_period_theorem": (
            "the congruences have odd right-hand sides, so an even axion shift "
            "cannot cancel them: the axion must transform under the full Z4R, "
            "not merely its Z2 subgroup"
        ),
        "universal_yL_coupling_solutions": {
            str(s): v for s, v in universal_yl.items()
        },
        "universal_yL_coupling_impossible": all(
            not v for v in universal_yl.values()
        ),
        "selected_sector_s1": chosen["couplings_mod_4"],
        "s3_sector_is_inverse_relabel": next(
            row for row in shift_rows if row["s"] == 3
        )["couplings_mod_4"],
        "verification_all_phases_cancel": all(
            (chosen["couplings_mod_4"][name] * 1 + ahat[name]) % MODULUS == 0
            for name in ahat
        ),
    }


def exhibited_gs_sector(congruences: Mapping[str, Any]) -> dict[str, Any]:
    c = congruences["selected_sector_s1"]
    return {
        "new_action_content": (
            "one axion chiral multiplet Saxion with a nonlinearly realized Z4R "
            "shift and four wall-localized gauge-kinetic couplings; this is new "
            "route-B62 action content, declared as such, not a splice"
        ),
        "multiplet": {
            "name": "Saxion = (saxion + i axion, axino, F)",
            "Z4R_transformation": "Saxion -> Saxion + i (pi/2) f  (s=1: one quarter period)",
            "R_charge_of_superfield": 0,
            "shift_is_nonlinear": True,
        },
        "superpotential_couplings": {
            "form": (
                "W_GS = (1/4) Saxion/f * [ c0 W^a W^a |Spin10,y=0 "
                "+ cL W^a W^a |SU2L,y=L + cR W^a W^a |SU2R,y=L "
                "+ c7 W^a W^a |SO7,y=L ]"
            ),
            "couplings_mod_4": c,
            "W_charge_check": (
                "W^a W^a carries R charge 2 and Saxion carries 0, so W_GS has "
                "charge 2; the anomalous variation comes from the shift, "
                "exactly the 4D GS mechanism at each wall"
            ),
        },
        "cancellation_certificate": {
            "all_four_wall_phases_cancel": congruences[
                "verification_all_phases_cancel"
            ],
            "coupling_uniqueness": "unique mod 4 once s is fixed; s=3 gives the relabeled inverse sector",
        },
        "what_is_not_exhibited": [
            "the saxion Kahler potential and stabilization (runaway direction not excluded)",
            "the microscopic origin of Saxion (bulk hyper, radion partner, or string modulus)",
            "the axino mass and its cosmology",
            "the post-VEV inflow matching described in the deficit section",
        ],
    }


def post_vev_inflow_deficit(
    ledgers: Mapping[str, Any], v61_route: Mapping[str, Any]
) -> dict[str, Any]:
    a0 = ledgers["_A_y0_fraction"]
    al_su2 = ledgers["_A_yL_fractions"]["SU2_L"]
    ir = v61_route["anomaly_universality_certificate"]
    a3_ir = Fraction(ir["A3"])
    a2_ir = Fraction(ir["A2"])
    # SU(3) and SU(4)/SO(7) restrictions coincide at index one; the SU(4)
    # wall sums were computed in integrated_matching.
    su3_wall_sum = a0 + Fraction(1, 2)  # A0(SU4)=1/2 and AL(SU4)=1/2
    su2_wall_sum = a0 + al_su2
    return {
        "statement": (
            "after <C>=<Cbar>=v the wall Higgsing marries wall fermions to "
            "boundary-condition-shifted KK towers; zero-mode counting alone "
            "then fails to reproduce the IR ledger, which is the classic "
            "situation requiring explicit anomaly inflow (Scrucca et al.; von "
            "Gersdorff-Quiros).  The exact deficits that the inflow must carry "
            "are displayed here and remain OPEN obligations"
        ),
        "IR_ledger_from_V61": {"A3": str(a3_ir), "A2": str(a2_ir)},
        "orbifold_wall_sums": {
            "SU3_via_SU4": str(su3_wall_sum),
            "SU2_L": str(su2_wall_sum),
        },
        "required_inflow": {
            "SU3": str(su3_wall_sum - a3_ir),
            "SU2_L": str(su2_wall_sum - a2_ir),
        },
        "carrier_candidates": (
            "the <C>-dependent jump of the Saxion wall couplings and/or a bulk "
            "Chern-Simons-type exchange; neither is computed here"
        ),
        "status": "OPEN",
    }


def obligations() -> list[dict[str, str]]:
    return [
        {
            "obligation": "saxion Kahler potential, stabilization and axino sector",
            "status": "OPEN",
            "detail": "the exhibited GS multiplet has no computed potential; a runaway is not excluded",
        },
        {
            "obligation": "post-VEV inflow matching",
            "status": "OPEN",
            "detail": "the exact deficits -2 (SU3) and -3 (SU2) must be carried by computed inflow, not assumed",
        },
        {
            "obligation": "Dai-Freed phase with the Z4R twist",
            "status": "OPEN",
            "detail": "the relative eta invariant with wall masses and the new GS sector is not computed",
        },
        {
            "obligation": "exact KK determinant and realistic flavor fit",
            "status": "OPEN",
            "detail": "carried unchanged from V59/V61",
        },
        {
            "obligation": "UV regulator / string completion",
            "status": "OPEN",
            "detail": "carried unchanged; the wall-coupling quantization ultimately needs a UV derivation",
        },
    ]


def falsifiers() -> list[dict[str, str]]:
    return [
        {
            "id": "F1",
            "test": "recompute any wall ledger entry and find a different exact value",
            "effect": "the ledger and the GS couplings are void",
        },
        {
            "id": "F2",
            "test": "find an integrated-matching factor where wall sums differ from the 4D ledger",
            "effect": "the localization weights are wrong for this orbifold",
        },
        {
            "id": "F3",
            "test": "exhibit a matter-free universal cancellation at the Spin(4)xSpin(7) wall",
            "effect": "the nonuniversality theorem fails",
        },
        {
            "id": "F4",
            "test": "show boundary theta terms are quantized in units incompatible with c mod 4",
            "effect": "the exhibited GS sector is inconsistent and the route falls back to V61",
        },
        {
            "id": "F5",
            "test": "compute the post-VEV inflow and find it cannot carry (-2,-3)",
            "effect": "the Z4R selector is quantum-obstructed after rank breaking",
        },
        {
            "id": "F6",
            "test": "show the saxion cannot be stabilized without breaking Z4R",
            "effect": "the GS sector destroys the selector it was built to save",
        },
    ]


def strict_g1_matrix() -> list[dict[str, str]]:
    return [
        {
            "criterion": "exact_proton_selector",
            "status": "PASS_ARITHMETIC_R_TYPE",
            "evidence": "carried from V61: unique Z4R class",
        },
        {
            "criterion": "selector_anomaly_universality",
            "status": "PASS_GLOBAL_LEDGER",
            "evidence": "carried from V61: A3=3, A2=1 universal mod 2",
        },
        {
            "criterion": "localized_R_anomaly_ledger",
            "status": "PASS_EXACT_ORBIFOLD_LEDGER",
            "evidence": (
                "per-wall ledger computed exactly with three integrated-"
                "matching validations; supersedes the V61 OPEN row"
            ),
        },
        {
            "criterion": "GS_axion_sector",
            "status": "EXHIBITED_QUANTIZED_CANDIDATE",
            "evidence": (
                "one axion, faithful quarter-period shift, unique couplings "
                "(3,1,1,3) mod 4; stabilization and origin not computed"
            ),
        },
        {
            "criterion": "post_VEV_inflow_matching",
            "status": "OPEN",
            "evidence": "exact deficits -2 (SU3) and -3 (SU2) displayed, carrier not computed",
        },
        {
            "criterion": "relative_5D_Dai_Freed_trivialization",
            "status": "OPEN",
            "evidence": "not computed with the R twist and the new GS sector",
        },
        {
            "criterion": "realistic_full_rank_Yukawas",
            "status": "OPEN",
            "evidence": "carried from V59/V61",
        },
        {
            "criterion": "UV_complete_regulator",
            "status": "OPEN",
            "evidence": "carried from V59/V61",
        },
        {
            "criterion": "strict_G1",
            "status": "OPEN",
            "evidence": "ledger and GS arithmetic closed; inflow, stabilization, Dai-Freed, KK and UV remain",
        },
    ]


def gate_ledger() -> list[dict[str, Any]]:
    decisions = {
        "G1": (
            "OPEN: the localized Z4R ledger is exact and a unique quantized GS "
            "sector is exhibited, but post-VEV inflow, saxion stabilization, "
            "Dai-Freed, the KK determinant and a UV regulator remain."
        ),
        "G2": "OPEN: no coefficient-level complete 4D Wilsonian action or soft solution.",
        "G3": "OPEN: no stabilized compactification; the saxion adds an unstabilized modulus.",
        "G4": "OPEN WITH ADVANCE: carried from V61; mu protection intact under the new sector.",
        "G5": (
            "OPEN WITH ADVANCE: R parity carried from V61; the axino is a new "
            "dark-sector candidate but has no computed mass or relic abundance."
        ),
        "G6": "OPEN: inflation, reheating and defect history are absent.",
        "G7": "OPEN WITH ADVANCE: carried from V61; dimension-six numerics still absent.",
        "G8": "OPEN: no microscopic UV completion or quantified predictivity score.",
    }
    return [
        {"gate": f"G{i}", "status": "OPEN", "decision": decisions[f"G{i}"]}
        for i in range(1, 9)
    ]


def source_manifest() -> dict[str, Any]:
    return {
        "audit_script": {
            "path": str(Path(__file__).resolve()),
            "sha256": sha256_file(Path(__file__).resolve()),
        },
        "pytest": {"path": str(TEST_PATH.resolve()), "sha256": sha256_file(TEST_PATH)},
        "bound_V61_route": {
            "path": str(V61_ROUTE_PATH.resolve()),
            "sha256": sha256_file(V61_ROUTE_PATH),
        },
        "bound_V61_master": {
            "path": str(V61_MASTER_PATH.resolve()),
            "sha256": sha256_file(V61_MASTER_PATH),
        },
        "primary_sources": PRIMARY_SOURCES,
    }


def build_report() -> dict[str, Any]:
    v61_route = load_bound(V61_ROUTE_PATH, EXPECTED_V61_ROUTE_CORE, "V61 route")
    v61_master = load_bound(V61_MASTER_PATH, EXPECTED_V61_MASTER_CORE, "V61 master")

    convention = conventions()
    projector = projector_block_audit()
    tables = index_tables()
    ledgers = wall_ledgers(tables)
    matching = integrated_matching(tables, ledgers)
    nonuniversal = nonuniversality_theorem(ledgers)
    congruences = gs_congruence_system(ledgers)
    sector = exhibited_gs_sector(congruences)
    inflow = post_vev_inflow_deficit(ledgers, v61_route)
    duty = obligations()
    gates = gate_ledger()

    v61_obligation_answered = next(
        row
        for row in v61_route["five_d_quantum_obligations"]
        if "localized" in row["obligation"]
    )

    integrity = {
        "V61_route_core_is_canonical_and_expected": v61_route["core_sha256"]
        == EXPECTED_V61_ROUTE_CORE,
        "V61_master_core_is_canonical_and_expected": v61_master["core_sha256"]
        == EXPECTED_V61_MASTER_CORE,
        "V61_localized_ledger_obligation_was_open": v61_obligation_answered[
            "status"
        ]
        == "OPEN",
        "projector_blocks_match_V59": projector["matches_V59_projector_data"],
        "all_55_generators_covered": projector["total_generators"] == 55,
        "matter_and_mediators_drop_out": (
            convention["fermion_charges"]["matter_16_fermions"] == 0
            and convention["fermion_charges"]["mirror_32_fermions"] == 0
        ),
        "y0_ledger_is_one_half": ledgers["A_y0_Spin10"] == "1/2"
        and ledgers["Ahat_y0_Spin10"] == 1,
        "yL_ledger_is_minus_five_halves_twice_and_one_half": (
            ledgers["A_yL"]
            == {"SU2_L": "-5/2", "SU2_R": "-5/2", "SO7": "1/2"}
            and ledgers["Ahat_yL"] == {"SU2_L": -5, "SU2_R": -5, "SO7": 1}
        ),
        "left_right_symmetry_of_wall_ledger": ledgers["left_right_symmetric"],
        "three_integrated_matching_checks_pass": matching["all_match"]
        and len(matching["checks"]) == 3,
        "yL_nonuniversality_is_exactly_minus_three": nonuniversal[
            "difference_A"
        ]
        == "-3"
        and nonuniversal["difference_is_odd_integer"],
        "even_axion_shift_impossible": congruences["even_shift_impossible"],
        "odd_shifts_solvable_and_unique": congruences["solvable_shifts"]
        == [1, 3],
        "universal_yL_coupling_impossible": congruences[
            "universal_yL_coupling_impossible"
        ],
        "selected_couplings_are_3_1_1_3": congruences["selected_sector_s1"]
        == {"Spin10@y0": 3, "SU2_L@yL": 1, "SU2_R@yL": 1, "SO7@yL": 3},
        "all_four_wall_phases_cancel": congruences[
            "verification_all_phases_cancel"
        ],
        "gs_sector_carries_W_charge_2": "charge 2" in sector[
            "superpotential_couplings"
        ]["W_charge_check"],
        "gs_sector_gaps_declared": len(sector["what_is_not_exhibited"]) == 4,
        "inflow_deficits_are_minus_2_and_minus_3": inflow["required_inflow"]
        == {"SU3": "-2", "SU2_L": "-3"}
        and inflow["status"] == "OPEN",
        "five_obligations_remain_open": len(duty) == 5
        and all(row["status"] == "OPEN" for row in duty),
        "all_gates_remain_open": all(row["status"] == "OPEN" for row in gates),
    }

    report: dict[str, Any] = {
        "schema": "susy_so10.v62.spin11_localized_z4r_anomaly_gs_audit.v1",
        "version": "V62",
        "date": "2026-08-29",
        "status": STATUS,
        "classification": CLASSIFICATION,
        "lineage": {
            "bound_V61_route_core": v61_route["core_sha256"],
            "bound_V61_master_core": v61_master["core_sha256"],
            "relation": (
                "route-B62 extension: it answers the first V61 quantum "
                "obligation (the localized ledger) and adds the GS axion as "
                "explicitly declared new action content; routes A60 and C are "
                "untouched"
            ),
        },
        "research_question": (
            "What is the exact fixed-point-localized Z4R anomaly ledger of the "
            "Spin(11) route, and does a consistent quantized Green-Schwarz "
            "sector exist for it?"
        ),
        "conventions": convention,
        "projector_block_audit": projector,
        "index_tables": {
            key: value for key, value in tables.items()
        },
        "wall_ledgers": {
            key: value
            for key, value in ledgers.items()
            if not key.startswith("_")
        },
        "integrated_matching": matching,
        "nonuniversality_theorem": nonuniversal,
        "gs_congruence_system": congruences,
        "exhibited_gs_sector": sector,
        "post_vev_inflow_deficit": inflow,
        "five_d_quantum_obligations": duty,
        "falsifiers": falsifiers(),
        "strict_G1_matrix": strict_g1_matrix(),
        "gate_ledger": gates,
        "terminal_decision": {
            "V62_G1_closed": False,
            "V62_closed_gates": [],
            "localized_ledger_computed": True,
            "gs_sector_exhibited": True,
            "gs_sector_scope": (
                "arithmetic cancellation of all four wall phases with unique "
                "quantized couplings; no stabilization, inflow, Dai-Freed or "
                "UV statement"
            ),
            "complete_theory": False,
            "next_obligations": [
                "compute the post-VEV inflow carrying the displayed (-2,-3) deficits",
                "stabilize the saxion without breaking Z4R",
                "compute the Dai-Freed phase with the R twist and the GS sector",
                "solve the exact KK determinant and flavor fit",
                "exhibit a UV regulator or string completion",
            ],
        },
        "claim_boundary": {
            "new_fundamental_physics_invented": True,
            "new_physics_scope": (
                "the GS axion sector is new, explicitly declared action "
                "content with quantized couplings forced by the computed "
                "ledger; it is a candidate, not a discovery"
            ),
            "no_numerical_coefficients_fabricated": True,
            "half_integer_wall_ledgers_reported_exactly": True,
            "no_gate_promotion": True,
        },
        "integrity_checks": integrity,
        "n_integrity_checks": len(integrity),
        "n_failed_integrity_checks": sum(
            not value for value in integrity.values()
        ),
        "source_manifest": source_manifest(),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("V62 canonical core mismatch")
    if report.get("n_failed_integrity_checks") != 0:
        failed = [
            name for name, passed in report["integrity_checks"].items() if not passed
        ]
        raise RuntimeError(f"V62 integrity failure: {failed}")
    terminal = report["terminal_decision"]
    if terminal["V62_G1_closed"]:
        raise RuntimeError("V62 overclaimed G1")
    if terminal["complete_theory"]:
        raise RuntimeError("V62 overclaimed a complete theory")
    if report["post_vev_inflow_deficit"]["status"] != "OPEN":
        raise RuntimeError("V62 overclaimed the inflow matching")
    if not report["integrated_matching"]["all_match"]:
        raise RuntimeError("V62 wall ledgers fail integrated matching")
    if any(row["status"] != "OPEN" for row in report["gate_ledger"]):
        raise RuntimeError("V62 promoted a gate")


def render_markdown(report: Mapping[str, Any]) -> str:
    ledgers = report["wall_ledgers"]
    matching = report["integrated_matching"]
    nonuniversal = report["nonuniversality_theorem"]
    congruences = report["gs_congruence_system"]
    sector = report["exhibited_gs_sector"]
    inflow = report["post_vev_inflow_deficit"]
    lines = [
        "# SUSY V62 Spin(11) localized Z4R anomaly ledger and GS sector audit",
        "",
        f"- Status: `{report['status']}`",
        f"- Core: `{report['core_sha256']}`",
        f"- Classification: `{report['classification']}`",
        "- Outcome: **the localized Z4R ledger is computed exactly, a unique quantized GS sector is exhibited, and the remaining quantum deficits are displayed as open numbers; G1 remains open**.",
        "- Gate promotions: **0/8**.",
        "",
        "## Bottom line",
        "",
        (
            "V61 left one blocking obligation sharply defined: the fixed-point-"
            "localized Z4R anomaly ledger and the missing Green-Schwarz axion.  "
            "V62 computes the ledger exactly.  With the unique V61 charges the "
            "matter sixteens and every mirror-32 mediator carry fermion charge "
            "zero and drop out entirely; the ledger is pure gauge-sector plus "
            "rank-sector data."
        ),
        "",
        "## The exact per-wall ledger",
        "",
        "y = 0 wall, local group Spin(10):",
        "",
        "| Field | weight | r | T | contribution |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in ledgers["y0_rows"]:
        lines.append(
            f"| {row['field']} | {row['weight']} | {row['r']} | {row['T']} | {row['contribution']} |"
        )
    lines.extend(
        [
            "",
            f"Total: `A(Spin10)|_0 = {ledgers['A_y0_Spin10']}`.",
            "",
            "y = L wall, local group SU(2)_L x SU(2)_R x Spin(7), no wall matter:",
            "",
            "| Factor | T(V-even) | V contrib | T(Sigma coset) | Sigma contrib | total |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in ledgers["yL_rows"]:
        lines.append(
            f"| {row['factor']} | {row['V_even_T']} | {row['V_contribution']} | "
            f"{row['Sigma_coset_T']} | {row['Sigma_contribution']} | {row['total']} |"
        )
    lines.extend(
        [
            "",
            "## Three integrated-matching validations",
            "",
            "| Factor | wall sum | direct 4D zero-mode ledger | match |",
            "|---|---:|---:|---|",
        ]
    )
    for row in matching["checks"]:
        lines.append(
            f"| {row['factor']} | {row['wall_sum']} | {row['direct_4D_zero_mode_ledger']} | {row['match']} |"
        )
    lines.extend(
        [
            "",
            "## Matter-free nonuniversality theorem at y = L",
            "",
            (
                f"The SU(2) and Spin(7) coefficients differ by `{nonuniversal['difference_A']}`: "
                f"`{nonuniversal['matter_free_group_theory_origin']['V_part']}` plus "
                f"`{nonuniversal['matter_free_group_theory_origin']['Sigma_part']}`.  The wall hosts no matter, "
                "so this is pure group theory: dual Coxeter numbers against coset "
                "indices.  A single wall-universal axion coupling therefore cannot "
                "cancel the wall phases -- the same universality disease that "
                "killed the corrected heterotic candidate, now localized at one "
                "wall.  Unlike the modular-locked heterotic basis, wall locality "
                "permits per-factor couplings, so the EFT admits a cure."
            ),
            "",
            "## The quantized GS sector",
            "",
            "```text",
            f"congruence:  c_G * s + Ahat_G = 0 mod 4,   Ahat = {congruences['Ahat_targets']}",
            f"even shifts: impossible ({congruences['faithful_odd_quarter_period_theorem'][:40]}...)",
            f"s = 1:       couplings {congruences['selected_sector_s1']}",
            f"s = 3:       couplings {congruences['s3_sector_is_inverse_relabel']} (inverse relabel)",
            f"universal y=L coupling: {congruences['universal_yL_coupling_solutions']} -> impossible",
            "```",
            "",
            (
                "The exhibited new action content is one axion chiral multiplet "
                "with a faithful quarter-period Z4R shift and the four wall "
                f"couplings above: `{sector['superpotential_couplings']['form']}`.  "
                "All four wall phases cancel exactly.  Not exhibited: the saxion "
                "potential and stabilization, the multiplet's microscopic origin, "
                "the axino sector, and the post-VEV inflow."
            ),
            "",
            "## Post-VEV inflow deficits (OPEN)",
            "",
            "```text",
            f"IR ledger (V61):   A3 = {inflow['IR_ledger_from_V61']['A3']}, A2 = {inflow['IR_ledger_from_V61']['A2']}",
            f"orbifold wall sums: SU3 via SU4 = {inflow['orbifold_wall_sums']['SU3_via_SU4']}, SU2_L = {inflow['orbifold_wall_sums']['SU2_L']}",
            f"required inflow:    SU3 = {inflow['required_inflow']['SU3']}, SU2_L = {inflow['required_inflow']['SU2_L']}",
            "```",
            "",
            (
                "After the rank VEVs, wall fermions marry boundary-condition-"
                "shifted KK towers; zero-mode counting alone cannot reproduce the "
                "IR ledger, and the displayed deficits must be carried by "
                "explicit inflow.  This is the sharpest remaining quantum "
                "obligation and it is left OPEN, not assumed."
            ),
            "",
            "## Strict G1 matrix",
            "",
            "| Criterion | Status | Evidence |",
            "|---|---|---|",
        ]
    )
    for row in report["strict_G1_matrix"]:
        lines.append(f"| {row['criterion']} | {row['status']} | {row['evidence']} |")
    lines.extend(
        ["", "## G1--G8 ledger", "", "| Gate | Status | Decision |", "|---|---|---|"]
    )
    for row in report["gate_ledger"]:
        lines.append(f"| {row['gate']} | {row['status']} | {row['decision']} |")
    lines.extend(
        [
            "",
            "## Primary sources",
            "",
        ]
    )
    for source in PRIMARY_SOURCES:
        lines.append(
            f"- [{source['authors'].split(',')[0].strip()} et al., {source['title']}]({source['url']}): {source['scope']}"
        )
    lines.extend(
        [
            "",
            "## Claim boundary",
            "",
            (
                "The GS axion sector is genuinely new physics content: a new field "
                "with quantized couplings forced by the computed ledger.  It is "
                "declared as candidate action content of route B62, not as a "
                "discovery.  The half-integer wall ledgers are reported exactly, "
                "the inflow deficits are displayed rather than resolved, and no "
                "gate is promoted."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write JSON and Markdown")
    parser.add_argument("--check", action="store_true", help="verify generated artifacts")
    args = parser.parse_args()
    report = build_report()
    validate(report)
    if args.write:
        write_outputs(report)
    if args.check:
        if not JSON_PATH.is_file() or not MD_PATH.is_file():
            raise RuntimeError("generated V62 route artifacts are missing")
        if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
            raise RuntimeError("generated V62 route JSON is stale")
        if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
            raise RuntimeError("generated V62 route Markdown is stale")
    print(report["status"])
    print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
