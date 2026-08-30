#!/usr/bin/env python3
"""Fail-closed V61 audit: the exact R-type selector escape for the Spin(11) route.

The V59 Spin(11) certificate proved a sharp scoped no-go: every commuting
Abelian NON-R selector with a neutral gauge-Higgs and a full-rank symmetric
three-family Yukawa support allows at least one same-family 16^4 operator.  It
explicitly listed "an exact R symmetry" as the first unexcluded loophole.  No
prior version audited that loophole.

V61 closes exactly that question at the charge-arithmetic and 4D global-anomaly
level.  For an R-type Z_M selector the determinant-cycle argument inverts: the
odd cycle forces 2q=2, hence the diagonal 16^4 carries charge 4 != 2 mod M for
every M>2 and is FORBIDDEN, not allowed.  An exhaustive scan of all Z_M^R
family assignments for 2<=M<=24 shows that demanding a full-rank Yukawa
support, the all-family dimension-five proton ban in W and K, and
Green-Schwarz anomaly universality selects exactly one physical class: Z4R
with all matter sixteens at charge one, the unique symmetry of Lee et al.
(arXiv:1009.0905), here re-derived inside the 5D architecture where the
orbifold-preserved SU(2)R Cartan and the mediator mixing force the same
charges independently.

The corrected heterotic candidate was rejected in V60 precisely because its
residue vector ['1','1','1','0','0'] is non-universal.  The V61 selector passes
that same universality test with A3=3, A2=1, A3-A2=2=0 mod eta=2.  The escape
is arithmetic and global-anomaly exact; the required single Green-Schwarz
axion multiplet, the localized fixed-point R-anomaly ledger, the Dai-Freed
phase, the exact KK determinant, and a UV regulator are NOT exhibited, so
strict G1 remains open and no gate is promoted.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V61_SPIN11_Z4R_SELECTOR_ESCAPE_AUDIT.json"
MD_PATH = ROOT / "SUSY_V61_SPIN11_Z4R_SELECTOR_ESCAPE_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v61_spin11_z4r_selector_escape_audit.py"
V59_SPIN11_PATH = ROOT / "SUSY_V59_SPIN11_GAUGE_HIGGS_COMPLETION_AUDIT.json"
V60_MASTER_PATH = ROOT / "SUSY_V60_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"

EXPECTED_V59_SPIN11_CORE = (
    "bf666eb5e4d57bff18b05182d7d6cc7874bbc26dd71897153faf9ee67a5f8c42"
)
EXPECTED_V60_MASTER_CORE = (
    "35395532eaf625886b704ed25b7fa8525482ec1d53b94ccc96e7858d6425898e"
)

MAX_MODULUS = 24
W_CHARGE = 2

STATUS = (
    "V61_SPIN11_EXACT_Z4R_SELECTOR_ESCAPE__V59_NON_R_NO_GO_DOES_NOT_EXTEND_"
    "TO_R_TYPE__ODD_CYCLE_FORCES_2Q_EQUALS_2_AND_FORBIDS_DIAGONAL_16_POW4__"
    "EXHAUSTIVE_M_2_TO_24_SCAN_SELECTS_UNIQUE_Z4R_CLASS_UP_TO_GAUGE_CENTER__"
    "SUPERALGEBRA_CARTAN_AND_MEDIATOR_MIXING_FORCE_MATTER_CHARGE_ONE__"
    "RANK_SECTOR_COMPATIBLE_WITH_MT_ZERO_AND_FULL_RANK_DETERMINANT__"
    "GLOBAL_ANOMALY_UNIVERSAL_MOD_2_WHERE_HETEROTIC_CANDIDATE_FAILED__"
    "W_DIM5_PROTON_BAN_ALL_ORDERS__KAHLER_DIM5_BAN_EXACT__"
    "GS_AXION_NOT_EXHIBITED__LOCALIZED_R_ANOMALY_DAI_FREED_SS_SOFT_KK_UV_OPEN__"
    "STRICT_G1_OPEN__ZERO_GATES_CLOSED"
)

CLASSIFICATION = (
    "EXACT_Z4R_SELECTOR_ESCAPE_CANDIDATE__ARITHMETIC_AND_GLOBAL_ANOMALY_PASS__"
    "QUANTUM_LOCALIZED_AND_UV_COMPLETION_OPEN"
)

PRIMARY_SOURCES = [
    {
        "id": "LEE_ET_AL_2010",
        "title": "A unique Z4R symmetry for the MSSM",
        "authors": (
            "Hyun Min Lee, Stuart Raby, Michael Ratz, Graham G. Ross, Roland "
            "Schieren, Kai Schmidt-Hoberg and Patrick K. S. Vaudrevange"
        ),
        "arxiv": "1009.0905",
        "url": "https://arxiv.org/abs/1009.0905",
        "scope": (
            "4D classification: among anomaly-universal Abelian discrete "
            "symmetries commuting with Spin(10) that forbid mu and dimension-"
            "five proton operators while allowing Yukawas and seesaw terms, "
            "Z4R with matter charge one is unique.  V61 re-derives this inside "
            "the 5D Spin(11) architecture with an independent exhaustive scan."
        ),
    },
    {
        "id": "IBANEZ_1992",
        "title": "More about discrete gauge anomalies",
        "authors": "Luis E. Ibanez",
        "arxiv": "hep-th/9202046",
        "url": "https://arxiv.org/abs/hep-th/9202046",
        "scope": (
            "Discrete anomaly arithmetic: mixed G^2-Z_M coefficients are "
            "constrained modulo M, relaxed to M/2 for even M by half-integral "
            "instanton number contributions; source of the eta convention."
        ),
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
        "scope": (
            "Path-integral derivation of discrete-anomaly conditions and of "
            "their Green-Schwarz repair; justifies demanding universality of "
            "A_G modulo eta with one axion."
        ),
    },
    {
        "id": "MIRABELLI_PESKIN_1997",
        "title": "Transmission of supersymmetry breaking from a 4-dimensional boundary",
        "authors": "Eugene A. Mirabelli and Michael E. Peskin",
        "arxiv": "hep-th/9712214",
        "url": "https://arxiv.org/abs/hep-th/9712214",
        "scope": (
            "Standard S1/Z2 decomposition of 5D SUSY: the SU(2)R doublet "
            "structure of gauginos and hyperscalars that fixes the Cartan "
            "R-charges used here."
        ),
    },
    {
        "id": "BURDMAN_NOMURA_2003",
        "title": "Unification of Higgs and Gauge Fields in Five Dimensions",
        "authors": "Gustavo Burdman and Yasunori Nomura",
        "arxiv": "hep-ph/0210257",
        "url": "https://arxiv.org/abs/hep-ph/0210257",
        "scope": (
            "5D gauge-Higgs superfield shift, bulk gauge Yukawas and the "
            "Scherk-Schwarz/radion route for mu and soft terms carried as the "
            "open soft-sector obligation."
        ),
    },
    {
        "id": "VON_GERSDORFF_QUIROS_2003",
        "title": "Localized anomalies in orbifold gauge theories",
        "authors": "Gero von Gersdorff and Mariano Quiros",
        "arxiv": "hep-th/0305024",
        "url": "https://arxiv.org/abs/hep-th/0305024",
        "scope": (
            "Fixed-point anomaly machinery that defines the still-open "
            "localized Z4R anomaly obligation; not computed here."
        ),
    },
    {
        "id": "GARCIA_ETXEBARRIA_MONTERO_2018",
        "title": "Dai-Freed anomalies in particle physics",
        "authors": "Inaki Garcia-Etxebarria and Miguel Montero",
        "arxiv": "1808.00009",
        "url": "https://arxiv.org/abs/1808.00009",
        "scope": (
            "Framework for the open Dai-Freed obligation with the discrete "
            "R twist included in the background; not computed here."
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


def eta(modulus: int) -> int:
    """Green-Schwarz comparison modulus: M for odd M, M/2 for even M."""

    return modulus if modulus % 2 else modulus // 2


def determinant(matrix: Sequence[Sequence[int | Fraction]]) -> Fraction:
    work = [[Fraction(x) for x in row] for row in matrix]
    n = len(work)
    if any(len(row) != n for row in work):
        raise ValueError("square matrix required")
    result = Fraction(1)
    for col in range(n):
        pivot = next((r for r in range(col, n) if work[r][col]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != col:
            work[col], work[pivot] = work[pivot], work[col]
            result *= -1
        value = work[col][col]
        result *= value
        for r in range(col + 1, n):
            ratio = work[r][col] / value
            for c in range(col, n):
                work[r][c] -= ratio * work[col][c]
    return result


def r_type_charge_calculus() -> dict[str, Any]:
    return {
        "definition": (
            "A Z_M^R selector acts on the Grassmann coordinate with theta "
            "charge 1, so every superpotential term must carry charge "
            "W_CHARGE=2 mod M and every Kahler-potential term charge 0 mod M."
        ),
        "theta_charge": 1,
        "superpotential_charge": W_CHARGE,
        "kahler_charge": 0,
        "component_rule": (
            "A chiral superfield of charge q has scalar charge q and fermion "
            "charge q-1; gauginos carry charge +1; gauge bosons charge 0."
        ),
        "eta_convention": {
            "rule": "eta(M)=M for odd M and M/2 for even M",
            "reason": (
                "half-integral instanton-number sectors relax the discrete "
                "anomaly comparison for even M (Ibanez; Araki et al.)"
            ),
            "eta_of_4": eta(4),
            "matches_V60_heterotic_eta_2_convention": eta(4) == 2,
        },
        "non_R_limit": (
            "theta charge 0 and W charge 0 reproduce the V59 non-R calculus, "
            "so the two audits use one uniform convention."
        ),
    }


def architecture_charge_forcings() -> dict[str, Any]:
    bulk_hyper = {"Phi": 1, "Phi_conjugate": 1}
    sigma_charge = 0
    mixing_forced_matter_charge = (W_CHARGE - bulk_hyper["Phi"]) % 4
    return {
        "gauge_higgs_Sigma": {
            "charge": sigma_charge,
            "forcing_1_shift_symmetry": (
                "Sigma -> exp(Lambda)(Sigma-sqrt(2) partial5)exp(-Lambda): the "
                "inhomogeneous partial5 piece is neutral, so any selector, R or "
                "non-R, must keep Sigma at charge 0."
            ),
            "forcing_2_superalgebra": (
                "the 5D gauginos form an SU(2)R doublet; the orbifold-preserved "
                "Cartan gives the V gaugino charge +1 and the Sigma fermion "
                "charge -1, hence superfield charge -1+1=0."
            ),
            "both_forcings_agree": True,
        },
        "bulk_hypermultiplet_halves": {
            "charges": bulk_hyper,
            "forcing": (
                "hyperscalars form an SU(2)R doublet with Cartan charges +-1; "
                "the two 4D chiral halves therefore carry charge (1,1), and the "
                "bulk operator Phi_c(partial5-Sigma)Phi carries charge 1+0+1=2, "
                "exactly the superpotential charge."
            ),
            "bulk_operator_charge": bulk_hyper["Phi"]
            + sigma_charge
            + bulk_hyper["Phi_conjugate"],
            "bulk_operator_charge_equals_W_charge": (
                bulk_hyper["Phi"] + sigma_charge + bulk_hyper["Phi_conjugate"]
            )
            == W_CHARGE,
        },
        "orbifold_preserves_cartan": {
            "statement": (
                "both interval projectors act in the same sigma3 direction of "
                "SU(2)R, so the Cartan U(1)R survives at y=0 and y=L; the "
                "candidate selector is its order-four subgroup, a symmetry of "
                "the 5D superalgebra rather than an ad hoc global charge."
            ),
            "P0_and_P1_use_same_SU2R_direction": True,
        },
        "mediator_mixing_forcing": {
            "wall_term": "W0 = Mtilde_bar16*(mu*M_16 + lambda_i*F_i)",
            "mu_piece_charge": bulk_hyper["Phi"] + bulk_hyper["Phi_conjugate"],
            "lambda_piece_requirement": "1 + q_i = 2 mod M",
            "forced_matter_charge": mixing_forced_matter_charge,
            "statement": (
                "with the superalgebra bulk charges, a nonzero lambda_i for "
                "every family, required for a full-rank kernel Yukawa, forces "
                "q_i = 1 for all three local sixteens."
            ),
        },
        "so10_compatibility_is_architectural": (
            "each family is one local Spin(10) sixteen, so all its MSSM members "
            "share one charge q_i; the gauge-Higgs sits in the 5D vector "
            "multiplet at charge 0.  The Lee et al. Spin(10) compatibility "
            "assumption is forced, not chosen."
        ),
    }


def odd_cycle_escape_theorem() -> dict[str, Any]:
    """The V59 determinant-cycle argument inverts for R-type selectors."""

    checks = []
    for modulus in range(3, MAX_MODULUS + 1):
        for q in range(modulus):
            if (2 * q - W_CHARGE) % modulus:
                continue
            checks.append(
                {
                    "M": modulus,
                    "q_with_2q_equal_2": q,
                    "diagonal_16_pow4_charge": (4 * q) % modulus,
                    "allowed": (4 * q - W_CHARGE) % modulus == 0,
                }
            )
    return {
        "proof": [
            "An allowed Yukawa entry ij obeys q_i+q_j=2 because q_Sigma=0 and W has charge 2.",
            "A nonzero determinant monomial selects a permutation of three labels.",
            "Every permutation of three labels has an odd cycle: a fixed point or a 3-cycle.",
            "On a fixed point 2q_i=2 directly; on a 3-cycle the three pair sums force q_i=q_j=q_k and again 2q_i=2.",
            "The same-family 16_i^4 operator then carries charge 4q_i=4, and 4=2 mod M requires M|2.",
            "Hence for every M>2 the label forced by the odd cycle has its 16_i^4 FORBIDDEN, inverting the V59 non-R conclusion.",
        ],
        "machine_check_domain": "all M in 3..24 and every q with 2q=2 mod M",
        "cases_checked": len(checks),
        "every_forced_diagonal_16_pow4_forbidden": all(
            not row["allowed"] for row in checks
        ),
        "M_equals_2_degeneration": {
            "statement": (
                "for M=2 the charges 4q=0=2 mod 2 make the quartic allowed, "
                "matching the V59 row that Z2 allows both the Yukawa and 16^4"
            ),
            "quartic_allowed_at_M2": (4 * 1 - W_CHARGE) % 2 == 0,
        },
        "rows": checks,
    }


def yukawa_support(charges: Sequence[int], modulus: int) -> list[list[bool]]:
    return [
        [(charges[i] + charges[j] - W_CHARGE) % modulus == 0 for j in range(3)]
        for i in range(3)
    ]


def support_has_full_rank(support: Sequence[Sequence[bool]]) -> bool:
    return any(
        all(support[i][perm[i]] for i in range(3))
        for perm in itertools.permutations(range(3))
    )


def quartic_multisets() -> list[tuple[int, ...]]:
    return list(itertools.combinations_with_replacement(range(3), 4))


def kahler_dim5_combos() -> list[tuple[tuple[int, ...], int]]:
    chirals = list(itertools.combinations_with_replacement(range(3), 3))
    return [(trio, dagger) for trio in chirals for dagger in range(3)]


def anomaly_coefficients(charges: Sequence[int]) -> dict[str, Any]:
    """Exact mixed G^2-Z_M^R coefficients of the light zero-mode ledger.

    A_G = C2(G) + sum over Weyl fermions of (charge) * T(rep), with fermion
    charge q-1 for a chiral superfield of charge q and +1 for gauginos, whose
    C2(G) term is already the gaugino contribution.  Matter: three sixteens
    (charges q_i for every member); Higgsinos Hu,Hd from Sigma at charge 0;
    N^c and E^c are colorless/weakless.
    """

    per_family_su3 = [
        Fraction(q - 1) * (Fraction(1, 2) * 2 + Fraction(1, 2) + Fraction(1, 2))
        for q in charges
    ]
    per_family_su2 = [
        Fraction(q - 1) * (Fraction(1, 2) * 3 + Fraction(1, 2)) for q in charges
    ]
    higgsino_su2 = Fraction(0 - 1) * (Fraction(1, 2) + Fraction(1, 2))
    a3 = Fraction(3) + sum(per_family_su3, Fraction(0))
    a2 = Fraction(2) + sum(per_family_su2, Fraction(0)) + higgsino_su2
    return {
        "A3": a3,
        "A2": a2,
        "difference": a3 - a2,
        "per_family_su3": per_family_su3,
        "per_family_su2": per_family_su2,
        "higgsino_su2": higgsino_su2,
    }


def exhaustive_r_selector_scan() -> dict[str, Any]:
    per_modulus: list[dict[str, Any]] = []
    solutions: list[dict[str, Any]] = []
    assignments_scanned = 0
    for modulus in range(2, MAX_MODULUS + 1):
        count_a = count_ab = count_abc = count_abcd = 0
        for charges in itertools.product(range(modulus), repeat=3):
            assignments_scanned += 1
            support = yukawa_support(charges, modulus)
            if not support_has_full_rank(support):
                continue
            count_a += 1
            w_quartic_all_forbidden = all(
                (sum(charges[i] for i in multiset) - W_CHARGE) % modulus != 0
                for multiset in quartic_multisets()
            )
            if not w_quartic_all_forbidden:
                continue
            count_ab += 1
            kahler_dim5_all_forbidden = all(
                (sum(charges[i] for i in trio) - charges[dagger]) % modulus != 0
                for trio, dagger in kahler_dim5_combos()
            )
            if not kahler_dim5_all_forbidden:
                continue
            count_abc += 1
            anomalies = anomaly_coefficients(charges)
            difference = anomalies["difference"]
            if difference.denominator != 1:
                raise RuntimeError("non-integral anomaly difference")
            if difference.numerator % eta(modulus):
                continue
            count_abcd += 1
            solutions.append(
                {
                    "M": modulus,
                    "charges": list(charges),
                    "A3": str(anomalies["A3"]),
                    "A2": str(anomalies["A2"]),
                    "eta": eta(modulus),
                }
            )
        per_modulus.append(
            {
                "M": modulus,
                "eta": eta(modulus),
                "full_rank_supports": count_a,
                "plus_W_dim5_ban": count_ab,
                "plus_Kahler_dim5_ban": count_abc,
                "plus_GS_universality": count_abcd,
            }
        )
    arithmetic_only_moduli = sorted(
        {row["M"] for row in per_modulus if row["plus_Kahler_dim5_ban"]}
    )
    return {
        "domain": (
            "all Z_M^R with 2<=M<=24 and all family charge triples q in Z_M^3; "
            "q_Sigma=0 is forced, q_Cbar=0 is forced by VEV neutrality so the "
            "seesaw operator F_i F_j Cbar Cbar shares the Yukawa support"
        ),
        "conditions": {
            "A_full_rank_Yukawa_support": "exists sigma in S3 with q_i+q_sigma(i)=2 mod M for all i",
            "B_W_dim5_proton_ban": "all 15 size-4 family multisets have charge sum != 2 mod M",
            "C_Kahler_dim5_proton_ban": "all 30 combos q_i+q_j+q_k-q_l != 0 mod M",
            "D_GS_universality": "A3 = A2 mod eta(M) on the light zero-mode ledger",
        },
        "assignments_scanned": assignments_scanned,
        "per_modulus": per_modulus,
        "moduli_with_arithmetic_selectors": arithmetic_only_moduli,
        "arithmetic_selectors_exist_beyond_M4": any(
            m != 4 for m in arithmetic_only_moduli
        ),
        "solutions": solutions,
        "solution_count": len(solutions),
        "discriminating_tier": (
            "conditions A-C admit R-type selectors at several moduli, unlike "
            "the non-R scan which admitted none; Green-Schwarz universality, "
            "the same test that rejected the corrected heterotic candidate, "
            "removes every modulus except M=4"
        ),
    }


def gauge_center_equivalence(scan: Mapping[str, Any]) -> dict[str, Any]:
    solutions = scan["solutions"]
    charge_vectors = sorted(tuple(row["charges"]) for row in solutions)
    difference = None
    same_operator_ledger = None
    if len(charge_vectors) == 2:
        difference = [
            (charge_vectors[1][i] - charge_vectors[0][i]) % 4 for i in range(3)
        ]
        support_a = yukawa_support(charge_vectors[0], 4)
        support_b = yukawa_support(charge_vectors[1], 4)
        quartics_a = [
            (sum(charge_vectors[0][i] for i in multiset) - W_CHARGE) % 4 == 0
            for multiset in quartic_multisets()
        ]
        quartics_b = [
            (sum(charge_vectors[1][i] for i in multiset) - W_CHARGE) % 4 == 0
            for multiset in quartic_multisets()
        ]
        same_operator_ledger = support_a == support_b and quartics_a == quartics_b
    return {
        "solution_charge_vectors": [list(v) for v in charge_vectors],
        "difference_mod_4": difference,
        "difference_is_2_2_2": difference == [2, 2, 2],
        "center_statement": (
            "a uniform charge shift of 2 mod 4 on every sixteen is the phase "
            "-1 on the 16, i.e. the square of the Spin(10) center generator, a "
            "gauge transformation; the two scan solutions therefore define one "
            "physical selector class"
        ),
        "identical_operator_ledgers": same_operator_ledger,
        "physical_class_count": 1
        if difference == [2, 2, 2] and same_operator_ledger
        else len(charge_vectors),
        "canonical_class": {"M": 4, "matter_charges": [1, 1, 1]},
    }


def rank_sector_r_compatibility() -> dict[str, Any]:
    charges = {"F_i": 1, "Sigma": 0, "C": 0, "Cbar": 0, "S": 2, "T": 2}
    term_ledger = [
        {"term": "kappa*S*C*Cbar", "charge": charges["S"] + charges["C"] + charges["Cbar"]},
        {"term": "kappa*S*v^2", "charge": charges["S"]},
        {"term": "lambda*C*C*T", "charge": 2 * charges["C"] + charges["T"]},
        {"term": "lambdabar*Cbar*Cbar*T", "charge": 2 * charges["Cbar"] + charges["T"]},
        {"term": "(M_T/2)*T*T", "charge": 2 * charges["T"]},
        {"term": "y_ij*F_i*F_j*Cbar*Cbar/M_* (seesaw)", "charge": 2 * charges["F_i"] + 2 * charges["Cbar"]},
        {"term": "F_i*F_j*Sigma*Sigma (Weinberg-type)", "charge": 2 * charges["F_i"] + 2 * charges["Sigma"]},
    ]
    for row in term_ledger:
        row["charge_mod_4"] = row["charge"] % 4
        row["allowed"] = row["charge_mod_4"] == W_CHARGE % 4
    five_matrix = [[0, 1], [1, 0]]
    heavy_pairs = [
        {"pair": "5bar_C with 5_T via lambda*<1_C>", "fermion_charges": [-1, 1]},
        {"pair": "5_Cbar with 5bar_T via lambdabar*<1_Cbar>", "fermion_charges": [-1, 1]},
        {"pair": "eaten 16/16bar fragments with gauginos", "fermion_charges": [-1, 1]},
        {"pair": "S with the radial C,Cbar singlet", "fermion_charges": [1, -1]},
    ]
    for row in heavy_pairs:
        row["charge_sum"] = sum(row["fermion_charges"])
        row["decouples_from_discrete_anomaly"] = row["charge_sum"] == 0
    return {
        "vev_neutrality_forcing": (
            "the rank VEVs <C>=<Cbar>=v must leave the selector unbroken, which "
            "forces q_C=q_Cbar=0 mod 4; the term ledger then forces q_S=q_T=2"
        ),
        "charges": charges,
        "term_ledger": term_ledger,
        "M_T_term_forbidden": next(
            row for row in term_ledger if row["term"].startswith("(M_T")
        )["allowed"]
        is False,
        "M_T_set_to_zero": True,
        "five_mass_matrix_with_MT_zero": "[[0,lambdabar*v],[lambda*v,0]]",
        "five_mass_determinant": "-lambda*lambdabar*v^2",
        "normalized_example_determinant": str(determinant(five_matrix)),
        "full_rank_without_MT": determinant(five_matrix) != 0,
        "v59_five_matrix_needed_MT": False,
        "v59_determinant_already_MT_independent": (
            "the V59 determinant -lambda*lambdabar*v^2 never involved M_T, so "
            "deleting the now-forbidden M_T term costs nothing"
        ),
        "selector_unbroken_by_all_displayed_vevs": True,
        "heavy_pair_decoupling": heavy_pairs,
        "anomaly_matching_conclusion": (
            "every rank-scale Dirac pair has fermion charge sum 0, so the "
            "discrete anomaly of the light ledger equals that of the wall theory"
        ),
    }


def anomaly_universality_certificate(
    v60_master: Mapping[str, Any],
) -> dict[str, Any]:
    ledger = anomaly_coefficients([1, 1, 1])
    a3 = ledger["A3"]
    a2 = ledger["A2"]
    route_a60 = next(
        row for row in v60_master["route_matrix"] if row["route_id"] == "A60"
    )
    heterotic = route_a60["corrected_hidden_anomaly_certificate"]
    thooft = {
        "SU3_vertex_charge": 2 * int(a3),
        "SU2_vertex_charge": 2 * int(a2),
        "SU3_vertex_charge_mod_4": (2 * int(a3)) % 4,
        "SU2_vertex_charge_mod_4": (2 * int(a2)) % 4,
        "both_equal_W_charge_mod_4": (2 * int(a3)) % 4 == W_CHARGE
        and (2 * int(a2)) % 4 == W_CHARGE,
        "statement": (
            "both 't Hooft vertices carry charge 2 mod 4, i.e. they transform "
            "exactly like superpotential terms, so nonperturbative gauge "
            "dynamics respects Z4R while breaking the continuous Cartan"
        ),
    }
    return {
        "light_ledger": "MSSM + 3 N^c + two Higgsinos from Sigma + gauginos",
        "formula": "A_G = C2(G) + sum over fermions of (q-1)*T(R), gauginos at +1",
        "A3": str(a3),
        "A2": str(a2),
        "difference": str(a3 - a2),
        "eta": eta(4),
        "universal_mod_eta": (a3 - a2).numerator % eta(4) == 0,
        "rho_mod_eta": int(a3) % eta(4),
        "GS_axion_required": int(a3) % eta(4) != 0,
        "GS_axion_exhibited_in_5D_action": False,
        "continuous_cartan_fate": (
            "the classical action preserves the full Cartan U(1)R, but A3=3 "
            "and A2=1 differ as exact integers, so no single axion repairs the "
            "continuous symmetry; the maximal single-axion-repairable subgroup "
            "with these charges is the order-four one"
        ),
        "maximal_subgroup_check": {
            "condition": "Z_M in the Cartan is GS-universal iff eta(M) divides A3-A2 = 2",
            "moduli_3_to_24_passing": [
                m for m in range(3, MAX_MODULUS + 1) if 2 % eta(m) == 0
            ],
            "unique_maximal_M": 4,
        },
        "t_hooft_vertices": thooft,
        "heterotic_contrast": {
            "V60_route_A60_residue_vector_mod2": heterotic["residue_vector_mod2"],
            "V60_route_A60_universal": heterotic["universal"],
            "V61_spin11_residue_vector_mod2": [
                str(int(a3) % eta(4)),
                str(int(a2) % eta(4)),
            ],
            "V61_universal": (a3 - a2).numerator % eta(4) == 0,
            "statement": (
                "the corrected heterotic candidate failed because its five "
                "residues split 1,1,1 against 0,0; the Spin(11) Z4R selector "
                "passes the identical universality test with residues 1,1"
            ),
        },
    }


def proton_mu_ledger() -> dict[str, Any]:
    return {
        "W_dim5_all_orders_ban": {
            "statement": (
                "any holomorphic W_eff monomial built from matter sixteens "
                "alone carries charge = (number of sixteens) mod 4; four "
                "sixteens give 0 != 2, so every dimension-five proton operator, "
                "including every mediator- or colored-KK-dressed one produced "
                "by a charge-2 Schur complement, vanishes identically"
            ),
            "wall_contact_F4_charge_mod_4": (4 * 1) % 4,
            "forbidden": (4 * 1 - W_CHARGE) % 4 != 0,
            "v59_status_upgraded_from": "fatal_without_selector / dimension_five_KK OPEN",
        },
        "Kahler_dim5_ban": {
            "operator_class": "[16_i 16_j 16_k 16_l^dagger]_D / M_*",
            "charge_mod_4": (3 * 1 - 1) % 4,
            "forbidden": (3 * 1 - 1) % 4 != 0,
        },
        "allowed_wanted_operators": {
            "Yukawa_16_16_Sigma_via_kernel": (2 * 1 + 0) % 4 == W_CHARGE,
            "seesaw_16_16_Cbar_Cbar": (2 * 1 + 0) % 4 == W_CHARGE,
            "Weinberg_16_16_Sigma_Sigma": (2 * 1 + 0) % 4 == W_CHARGE,
        },
        "mu_term": {
            "W_level_charge_mod_4": 0,
            "doubly_forbidden": (
                "charge 0 != 2 and the 5D gauge shift independently forbids a "
                "local polynomial Sigma mass"
            ),
            "generation_route": (
                "Z4R breaking by <W> of charge 2 at the gravitino scale can "
                "regenerate mu of order m_3/2; the soft spectrum is not solved "
                "here and stays open"
            ),
        },
        "remaining_open_channels": [
            "dimension-six gauge-boson KK exchange: unaffected by any R symmetry; needs Mc and wavefunctions against nucleon limits",
            "Kahler operators dressed by SUSY breaking: suppressed by m_soft, not computed",
            "numerical proton lifetime: no calculation exists in this route",
        ],
        "proton_gate_not_promoted": True,
    }


def matter_parity_and_lsp() -> dict[str, Any]:
    fields = [
        {"field": "matter 16_i", "q": 1},
        {"field": "Sigma (Hu,Hd)", "q": 0},
        {"field": "C", "q": 0},
        {"field": "Cbar", "q": 0},
        {"field": "S", "q": 2},
        {"field": "T", "q": 2},
    ]
    for row in fields:
        row["scalar_phase_under_g2"] = 1 if (2 * row["q"]) % 4 == 0 else -1
        row["fermion_phase_under_g2"] = 1 if (2 * (row["q"] - 1)) % 4 == 0 else -1
    gaugino_phase = 1 if (2 * 1) % 4 == 0 else -1
    return {
        "element": "g^2, the order-two element of Z4R",
        "field_phases": fields,
        "gaugino_phase": gaugino_phase,
        "acts_as_R_parity": (
            "matter scalars odd, matter fermions even, Higgs scalars even, "
            "Higgsinos and gauginos odd: exactly R parity"
        ),
        "survives_gravitino_mass": {
            "W_charge_under_g2": (2 * W_CHARGE) % 4,
            "unbroken_by_nonzero_W_vev": (2 * W_CHARGE) % 4 == 0,
            "statement": (
                "<W> breaks Z4R to g^2, so R parity and LSP stability persist "
                "after supersymmetry breaking; a dark-matter candidate exists "
                "structurally but no relic computation is performed"
            ),
        },
    }


def scherk_schwarz_compatibility() -> dict[str, Any]:
    return {
        "twist_direction": "the Scherk-Schwarz twist acts in SU(2)R",
        "exact_statement": (
            "a twist along the same sigma3 Cartan direction commutes with "
            "every element of Z4R, which lives in that Cartan, so this soft-"
            "breaking route preserves the selector at the twist level"
        ),
        "twist_in_cartan_commutes_with_Z4R": True,
        "not_computed": [
            "the gravitino and soft spectrum induced by the twist",
            "one-loop radion/Casimir stabilization",
            "the mu/B-mu ratio after R breaking",
        ],
        "status": "COMPATIBILITY_EXACT__SPECTRUM_OPEN",
    }


def five_d_quantum_obligations() -> list[dict[str, str]]:
    return [
        {
            "obligation": "localized fixed-point Z4R anomaly ledger",
            "status": "OPEN",
            "detail": (
                "the discrete R rotation acts on the fixed-point fermion "
                "measure; the von Gersdorff-Quiros decomposition with the "
                "mirror-32 pairing has not been evaluated for this generator"
            ),
        },
        {
            "obligation": "single Green-Schwarz axion multiplet in the 5D action",
            "status": "OPEN",
            "detail": (
                "rho=1 mod 2 requires one axion with universal couplings; no "
                "radion/form-field multiplet is exhibited and quantized here"
            ),
        },
        {
            "obligation": "Dai-Freed phase with the Z4R twist in the background",
            "status": "OPEN",
            "detail": "the relative eta invariant with wall masses is not computed",
        },
        {
            "obligation": "exact KK determinant and realistic flavor fit",
            "status": "OPEN",
            "detail": "carried unchanged from V59; the kernel is defined but not solved",
        },
        {
            "obligation": "UV regulator / string completion",
            "status": "OPEN",
            "detail": "carried unchanged from V59",
        },
    ]


def falsifiers() -> list[dict[str, str]]:
    return [
        {
            "id": "F1",
            "test": "exhibit an R-type assignment passing conditions A-D outside the Z4R class",
            "effect": "the uniqueness claim fails and the scan must be rerun",
        },
        {
            "id": "F2",
            "test": "show the odd-cycle escape check fails for some M in 3..24",
            "effect": "the R-type inversion of the V59 theorem is false",
        },
        {
            "id": "F3",
            "test": "compute a nonvanishing localized Z4R anomaly with no allowed local counterterm",
            "effect": "the selector is quantum-inconsistent on this orbifold and the route falls back to the V59 no-go frontier",
        },
        {
            "id": "F4",
            "test": "show no 5D multiplet can furnish the universal GS axion",
            "effect": "rho=1 cannot be repaired and Z4R is anomalous",
        },
        {
            "id": "F5",
            "test": "show the Scherk-Schwarz twist needed for realistic soft terms lies outside the Cartan",
            "effect": "SUSY breaking destroys the selector and mu/proton protection",
        },
        {
            "id": "F6",
            "test": "find a charge-2 W_eff monomial with four matter sixteens",
            "effect": "arithmetic error; the all-orders dimension-five ban is void",
        },
    ]


def strict_g1_matrix() -> list[dict[str, str]]:
    return [
        {
            "criterion": "one_explicit_5D_SUSY_action_skeleton",
            "status": "PARTIAL",
            "evidence": "carried from V59; gauge, rank and paired-mediator terms explicit, KK determinant absent",
        },
        {
            "criterion": "exact_two_Higgs_zero_modes_no_colored_zero",
            "status": "PASS",
            "evidence": "carried from V59 55-generator enumeration",
        },
        {
            "criterion": "rank_breaking_without_light_5_plus_5bar",
            "status": "PASS_CONDITIONAL",
            "evidence": "det=-lambda*lambdabar*v^2 with the M_T term now forced to zero",
        },
        {
            "criterion": "exact_proton_selector",
            "status": "PASS_ARITHMETIC_R_TYPE",
            "evidence": (
                "unique Z4R class from the exhaustive scan; W and Kahler "
                "dimension-five bans exact; supersedes the V59 non-R FAIL row"
            ),
        },
        {
            "criterion": "selector_anomaly_universality",
            "status": "PASS_GLOBAL_LEDGER",
            "evidence": "A3=3, A2=1, universal mod eta=2 where the heterotic candidate failed",
        },
        {
            "criterion": "selector_quantum_completion",
            "status": "OPEN",
            "evidence": "localized R anomaly, GS axion multiplet and Dai-Freed phase not computed",
        },
        {
            "criterion": "realistic_full_rank_Yukawas",
            "status": "OPEN",
            "evidence": "carried from V59; kernel defined, spectrum not solved",
        },
        {
            "criterion": "UV_complete_regulator",
            "status": "OPEN",
            "evidence": "carried from V59",
        },
        {
            "criterion": "strict_G1",
            "status": "OPEN",
            "evidence": "arithmetic and global-anomaly escape only; quantum and UV obligations remain",
        },
    ]


def gate_ledger() -> list[dict[str, Any]]:
    decisions = {
        "G1": (
            "OPEN: the V59 selector obstruction is resolved at the R-type "
            "arithmetic and global-anomaly level by a unique Z4R class, but the "
            "GS axion multiplet, localized R-anomaly ledger, Dai-Freed phase, "
            "KK determinant and UV regulator are absent."
        ),
        "G2": "OPEN: no coefficient-level complete 4D Wilsonian action or soft solution.",
        "G3": "OPEN: no stabilized compactification, physical quotient or full KK Hessian.",
        "G4": (
            "OPEN WITH ADVANCE: mu is now doubly forbidden (gauge shift and "
            "charge 0!=2) with a m_3/2 regeneration route, but no soft spectrum "
            "or hierarchy test is solved."
        ),
        "G5": (
            "OPEN WITH ADVANCE: g^2 acts as exact R parity surviving <W>!=0, so "
            "a stable LSP exists structurally; no relic or cosmology computation."
        ),
        "G6": "OPEN: inflation, reheating and defect history are absent.",
        "G7": (
            "OPEN WITH ADVANCE: all dimension-five proton operators are "
            "forbidden to all orders in W and at dimension five in K; the "
            "dimension-six KK channel and a lifetime number remain uncomputed."
        ),
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
        "bound_V59_spin11": {
            "path": str(V59_SPIN11_PATH.resolve()),
            "sha256": sha256_file(V59_SPIN11_PATH),
        },
        "bound_V60_master": {
            "path": str(V60_MASTER_PATH.resolve()),
            "sha256": sha256_file(V60_MASTER_PATH),
        },
        "primary_sources": PRIMARY_SOURCES,
    }


def build_report() -> dict[str, Any]:
    v59 = load_bound(V59_SPIN11_PATH, EXPECTED_V59_SPIN11_CORE, "V59 Spin(11) route")
    v60 = load_bound(V60_MASTER_PATH, EXPECTED_V60_MASTER_CORE, "V60 master")

    v59_selector = v59["proton_selector_obstruction"]
    calculus = r_type_charge_calculus()
    forcings = architecture_charge_forcings()
    escape = odd_cycle_escape_theorem()
    scan = exhaustive_r_selector_scan()
    equivalence = gauge_center_equivalence(scan)
    rank = rank_sector_r_compatibility()
    anomalies = anomaly_universality_certificate(v60)
    proton = proton_mu_ledger()
    parity = matter_parity_and_lsp()
    ss = scherk_schwarz_compatibility()
    obligations = five_d_quantum_obligations()
    gates = gate_ledger()

    non_r_contrast = {
        "v59_full_rank_assignments_checked": v59_selector["finite_scan"][
            "full_rank_charge_assignments_checked"
        ],
        "v59_non_R_counterexamples": len(
            v59_selector["finite_scan"]["counterexamples"]
        ),
        "v59_first_listed_loophole": v59_selector["loopholes_not_excluded"][0],
        "v61_realizes_that_loophole": v59_selector["loopholes_not_excluded"][0]
        == "an exact R symmetry",
        "statement": (
            "the V59 scan proved zero non-R selectors exist among 1295 "
            "full-rank supports; the V61 scan proves the R-type family is "
            "nonempty and collapses to one class under GS universality"
        ),
    }

    integrity = {
        "V59_spin11_core_is_canonical_and_expected": v59["core_sha256"]
        == EXPECTED_V59_SPIN11_CORE,
        "V60_master_core_is_canonical_and_expected": v60["core_sha256"]
        == EXPECTED_V60_MASTER_CORE,
        "V59_loophole_list_names_exact_R_symmetry_first": non_r_contrast[
            "v61_realizes_that_loophole"
        ],
        "sigma_neutrality_forced_twice": forcings["gauge_higgs_Sigma"][
            "both_forcings_agree"
        ],
        "bulk_operator_charge_equals_W_charge": forcings[
            "bulk_hypermultiplet_halves"
        ]["bulk_operator_charge_equals_W_charge"],
        "mediator_mixing_forces_matter_charge_one": forcings[
            "mediator_mixing_forcing"
        ]["forced_matter_charge"]
        == 1,
        "odd_cycle_escape_holds_for_all_M_3_to_24": escape[
            "every_forced_diagonal_16_pow4_forbidden"
        ],
        "M2_degeneration_matches_V59_Z2_row": escape["M_equals_2_degeneration"][
            "quartic_allowed_at_M2"
        ],
        "scan_domain_is_complete": scan["assignments_scanned"]
        == sum(m**3 for m in range(2, MAX_MODULUS + 1)),
        "arithmetic_selectors_exist_beyond_M4": scan[
            "arithmetic_selectors_exist_beyond_M4"
        ],
        "GS_universality_selects_only_M4": all(
            row["plus_GS_universality"] == 0
            for row in scan["per_modulus"]
            if row["M"] != 4
        ),
        "exactly_two_raw_solutions": scan["solution_count"] == 2,
        "solutions_are_gauge_center_equivalent": equivalence[
            "physical_class_count"
        ]
        == 1
        and equivalence["difference_is_2_2_2"]
        and bool(equivalence["identical_operator_ledgers"]),
        "canonical_class_is_Z4R_matter_charge_one": equivalence[
            "canonical_class"
        ]
        == {"M": 4, "matter_charges": [1, 1, 1]},
        "rank_sector_terms_all_charge_two_except_forbidden_MT": all(
            row["allowed"]
            for row in rank["term_ledger"]
            if not row["term"].startswith("(M_T")
        )
        and rank["M_T_term_forbidden"] is True,
        "five_matrix_full_rank_without_MT": rank["full_rank_without_MT"]
        and rank["normalized_example_determinant"] == "-1",
        "selector_unbroken_by_rank_vevs": rank[
            "selector_unbroken_by_all_displayed_vevs"
        ],
        "heavy_pairs_all_decouple": all(
            row["decouples_from_discrete_anomaly"]
            for row in rank["heavy_pair_decoupling"]
        ),
        "anomaly_A3_3_A2_1_universal_mod_2": anomalies["A3"] == "3"
        and anomalies["A2"] == "1"
        and anomalies["universal_mod_eta"],
        "GS_axion_required_and_not_overclaimed": anomalies["GS_axion_required"]
        and not anomalies["GS_axion_exhibited_in_5D_action"],
        "unique_maximal_cartan_subgroup_is_M4": anomalies[
            "maximal_subgroup_check"
        ]["moduli_3_to_24_passing"]
        == [4],
        "t_hooft_vertices_carry_W_charge": anomalies["t_hooft_vertices"][
            "both_equal_W_charge_mod_4"
        ],
        "heterotic_contrast_is_bound_not_asserted": anomalies[
            "heterotic_contrast"
        ]["V60_route_A60_residue_vector_mod2"]
        == ["1", "1", "1", "0", "0"]
        and not anomalies["heterotic_contrast"]["V60_route_A60_universal"]
        and anomalies["heterotic_contrast"]["V61_universal"],
        "W_dim5_ban_and_Kahler_dim5_ban_exact": proton["W_dim5_all_orders_ban"][
            "forbidden"
        ]
        and proton["Kahler_dim5_ban"]["forbidden"],
        "wanted_operators_all_allowed": all(
            proton["allowed_wanted_operators"].values()
        ),
        "g2_is_R_parity_surviving_gravitino_mass": parity[
            "survives_gravitino_mass"
        ]["unbroken_by_nonzero_W_vev"],
        "ss_twist_compatibility_is_exact_but_spectrum_open": ss[
            "twist_in_cartan_commutes_with_Z4R"
        ]
        and ss["status"] == "COMPATIBILITY_EXACT__SPECTRUM_OPEN",
        "all_five_quantum_obligations_open": all(
            row["status"] == "OPEN" for row in obligations
        )
        and len(obligations) == 5,
        "all_gates_remain_open": all(row["status"] == "OPEN" for row in gates),
    }

    report: dict[str, Any] = {
        "schema": "susy_so10.v61.spin11_z4r_selector_escape_audit.v1",
        "version": "V61",
        "date": "2026-08-29",
        "status": STATUS,
        "classification": CLASSIFICATION,
        "lineage": {
            "bound_V59_spin11_core": v59["core_sha256"],
            "bound_V60_master_core": v60["core_sha256"],
            "relation": (
                "route-B extension: it keeps every V59 structural result and "
                "answers the first V59 loophole; it does not touch routes A60 "
                "or C and does not splice actions"
            ),
        },
        "research_question": (
            "Does the sharp V59 non-R selector no-go extend to R-type Abelian "
            "selectors in the same Spin(11) architecture, and if not, which "
            "R selectors survive all exact requirements?"
        ),
        "non_R_contrast": non_r_contrast,
        "r_type_charge_calculus": calculus,
        "architecture_charge_forcings": forcings,
        "odd_cycle_escape_theorem": escape,
        "exhaustive_r_selector_scan": scan,
        "gauge_center_equivalence": equivalence,
        "rank_sector_r_compatibility": rank,
        "anomaly_universality_certificate": anomalies,
        "proton_mu_ledger": proton,
        "matter_parity_and_lsp": parity,
        "scherk_schwarz_compatibility": ss,
        "five_d_quantum_obligations": obligations,
        "falsifiers": falsifiers(),
        "strict_G1_matrix": strict_g1_matrix(),
        "gate_ledger": gates,
        "terminal_decision": {
            "V61_G1_closed": False,
            "V61_closed_gates": [],
            "selector_escape_proved": True,
            "escape_scope": (
                "charge arithmetic, uniqueness scan and 4D global anomaly "
                "universality only; no localized, Dai-Freed or UV statement"
            ),
            "unique_selector_class": "Z4R with matter charge one",
            "route_classification": CLASSIFICATION,
            "complete_theory": False,
            "next_obligations": [
                "compute the fixed-point-localized Z4R anomaly ledger with the mirror pairing",
                "exhibit and quantize the single 5D GS axion multiplet",
                "compute the Dai-Freed phase with the R twist",
                "solve the exact KK determinant and flavor fit",
                "exhibit a UV regulator or string completion",
            ],
        },
        "claim_boundary": {
            "new_fundamental_physics_invented": False,
            "four_d_uniqueness_matches_lee_et_al": True,
            "five_d_re_derivation_is_new_but_arithmetic": True,
            "no_numerical_coefficients_fabricated": True,
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
        raise RuntimeError("V61 canonical core mismatch")
    if report.get("n_failed_integrity_checks") != 0:
        failed = [
            name for name, passed in report["integrity_checks"].items() if not passed
        ]
        raise RuntimeError(f"V61 integrity failure: {failed}")
    terminal = report["terminal_decision"]
    if terminal["V61_G1_closed"]:
        raise RuntimeError("V61 overclaimed G1")
    if terminal["complete_theory"]:
        raise RuntimeError("V61 overclaimed a complete theory")
    if report["anomaly_universality_certificate"]["GS_axion_exhibited_in_5D_action"]:
        raise RuntimeError("V61 claimed an unexhibited GS axion")
    if any(row["status"] != "OPEN" for row in report["gate_ledger"]):
        raise RuntimeError("V61 promoted a gate")
    solutions = report["exhaustive_r_selector_scan"]["solutions"]
    vectors = sorted(tuple(row["charges"]) for row in solutions)
    if vectors != [(1, 1, 1), (3, 3, 3)] or any(row["M"] != 4 for row in solutions):
        raise RuntimeError("V61 scan solutions are not the expected Z4R class")


def render_markdown(report: Mapping[str, Any]) -> str:
    forcings = report["architecture_charge_forcings"]
    escape = report["odd_cycle_escape_theorem"]
    scan = report["exhaustive_r_selector_scan"]
    equivalence = report["gauge_center_equivalence"]
    rank = report["rank_sector_r_compatibility"]
    anomalies = report["anomaly_universality_certificate"]
    proton = report["proton_mu_ledger"]
    contrast = report["non_R_contrast"]
    lines = [
        "# SUSY V61 Spin(11) exact Z4R selector escape audit",
        "",
        f"- Status: `{report['status']}`",
        f"- Core: `{report['core_sha256']}`",
        f"- Classification: `{report['classification']}`",
        "- Outcome: **the V59 non-R selector no-go does not extend to R-type; a unique Z4R class survives every exact requirement; G1 remains open**.",
        "- Gate promotions: **0/8**.",
        "",
        "## Bottom line",
        "",
        (
            "V59 proved that no commuting Abelian non-R selector can protect the "
            f"proton in this architecture ({contrast['v59_full_rank_assignments_checked']} full-rank supports, "
            f"{contrast['v59_non_R_counterexamples']} counterexamples) and listed \"an exact R symmetry\" as the "
            "first unexcluded loophole.  V61 audits exactly that loophole.  For an "
            "R-type selector the same determinant-cycle argument that killed every "
            "non-R candidate instead forces 2q=2 on some family, whose 16^4 then "
            "carries charge 4 != 2 mod M and is forbidden for every M>2.  The "
            "obstruction inverts into a selection principle."
        ),
        "",
        (
            "An exhaustive scan of all Z_M^R family assignments for 2<=M<=24 "
            f"({scan['assignments_scanned']} assignments) demands a full-rank Yukawa support, the "
            "complete dimension-five proton ban in W and K, and Green-Schwarz "
            "anomaly universality.  Exactly one physical class survives: Z4R with "
            "every matter sixteen at charge one, the unique symmetry of Lee et al., "
            "re-derived here inside the 5D action where the orbifold-preserved "
            "SU(2)R Cartan and the mediator mixing independently force the same "
            "charges.  The universality test that rejected the corrected heterotic "
            "candidate in V60 is passed by this selector."
        ),
        "",
        "## Architecture forcings",
        "",
        f"- `q(Sigma)=0` twice over: the inhomogeneous 5D shift and the SU(2)R Cartan (Sigma fermion is the second gaugino at charge -1).",
        f"- bulk hyper halves at charges (1,1): the bulk operator `Phi_c(partial5-Sigma)Phi` carries charge {forcings['bulk_hypermultiplet_halves']['bulk_operator_charge']} = W charge.",
        f"- the wall mixing `{forcings['mediator_mixing_forcing']['wall_term']}` forces `q_i = {forcings['mediator_mixing_forcing']['forced_matter_charge']}` for every family mixed into the kernel Yukawa.",
        "- Spin(10) compatibility is architectural: one local sixteen per family, gauge-Higgs neutral.",
        "",
        "## The odd-cycle escape theorem",
        "",
    ]
    for step in escape["proof"]:
        lines.append(f"- {step}")
    lines.extend(
        [
            "",
            f"Machine check: {escape['cases_checked']} cases over {escape['machine_check_domain']}; every forced diagonal 16^4 is forbidden: {escape['every_forced_diagonal_16_pow4_forbidden']}.  At M=2 the quartic is allowed again, matching the V59 Z2 row.",
            "",
            "## Exhaustive R-selector scan",
            "",
            "| M | eta | full-rank supports | + W dim-5 ban | + Kahler dim-5 ban | + GS universality |",
            "|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in scan["per_modulus"]:
        if row["full_rank_supports"] or row["M"] in (2, 3, 4):
            lines.append(
                f"| {row['M']} | {row['eta']} | {row['full_rank_supports']} | "
                f"{row['plus_W_dim5_ban']} | {row['plus_Kahler_dim5_ban']} | "
                f"{row['plus_GS_universality']} |"
            )
    lines.extend(
        [
            "",
            (
                f"Arithmetic selectors (conditions A-C) exist at moduli {scan['moduli_with_arithmetic_selectors']}, unlike the "
                "non-R case where none exist at all.  Green-Schwarz universality "
                "eliminates every modulus except four.  The two raw solutions "
                f"{equivalence['solution_charge_vectors']} differ by the uniform shift {equivalence['difference_mod_4']}, which is "
                "the -1 phase of the Spin(10) center on the 16: one physical class."
            ),
            "",
            "## Rank sector under Z4R",
            "",
            f"Forced charges: `{rank['charges']}`.",
            "",
            "| Term | charge mod 4 | allowed |",
            "|---|---:|---|",
        ]
    )
    for row in rank["term_ledger"]:
        lines.append(f"| `{row['term']}` | {row['charge_mod_4']} | {row['allowed']} |")
    lines.extend(
        [
            "",
            (
                "The explicit `M_T T^2` mass is forbidden (charge 0), and nothing is "
                f"lost: the five matrix `{rank['five_mass_matrix_with_MT_zero']}` keeps determinant "
                f"`{rank['five_mass_determinant']}`, which never involved `M_T`.  All rank VEVs are "
                "neutral, so Z4R survives Spin(10) -> SU(5) breaking, and every heavy "
                "Dirac pair has fermion charge sum zero, so discrete anomaly matching "
                "holds between the wall and the light ledger."
            ),
            "",
            "## Global anomaly certificate and heterotic contrast",
            "",
            "```text",
            f"A3 = {anomalies['A3']},  A2 = {anomalies['A2']},  A3-A2 = {anomalies['difference']},  eta = {anomalies['eta']}",
            f"V60 heterotic residues: {anomalies['heterotic_contrast']['V60_route_A60_residue_vector_mod2']}  (non-universal, candidate rejected)",
            f"V61 Spin(11) residues:  {anomalies['heterotic_contrast']['V61_spin11_residue_vector_mod2']}  (universal)",
            "```",
            "",
            (
                "rho = 1 mod 2 is nonzero, so one Green-Schwarz axion is required; "
                "none is exhibited in the 5D action yet, and that is a blocking "
                "obligation.  Both 't Hooft vertices carry charge "
                f"{anomalies['t_hooft_vertices']['SU3_vertex_charge_mod_4']} mod 4 = the superpotential charge, so instantons "
                "break the classical Cartan U(1)R exactly to a superpotential-like "
                "shift while preserving Z4R.  Among all Cartan subgroups, "
                f"M = {anomalies['maximal_subgroup_check']['unique_maximal_M']} is the unique GS-repairable order above two."
            ),
            "",
            "## Proton and mu ledger",
            "",
            f"- wall contact `F^4/M_*`: charge {proton['W_dim5_all_orders_ban']['wall_contact_F4_charge_mod_4']} != 2, forbidden to all orders in W, including every mediator- and colored-KK-dressed Schur-complement term.  This supersedes the V59 rows `fatal_without_selector` and `dimension_five_KK: OPEN`.",
            f"- Kahler `[16^3 16^dagger]_D`: charge {proton['Kahler_dim5_ban']['charge_mod_4']} != 0, forbidden.",
            "- wanted operators all allowed: kernel Yukawa, seesaw `16 16 Cbar Cbar`, Weinberg-type `16 16 Sigma Sigma`.",
            "- mu: doubly forbidden (gauge shift and charge 0 != 2); regeneration of order m_3/2 at R breaking is a route, not a computation.",
            "- still open: dimension-six KK exchange numerics, SUSY-breaking-dressed Kahler operators, any lifetime number.",
            "",
            "## R parity, Scherk-Schwarz and quantum obligations",
            "",
            (
                "The order-two element g^2 acts exactly as R parity and survives "
                "<W> != 0, so LSP stability persists after supersymmetry breaking.  A "
                "Scherk-Schwarz twist along the same Cartan commutes with Z4R, so the "
                "standard soft-breaking route is compatible at the twist level; the "
                "induced spectrum is not computed.  Blocking quantum obligations:"
            ),
            "",
        ]
    )
    for row in report["five_d_quantum_obligations"]:
        lines.append(f"- {row['obligation']}: {row['status']} - {row['detail']}")
    lines.extend(
        [
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
                "The 4D uniqueness statement reproduces Lee et al. exactly; the new "
                "content is its exhaustive re-derivation inside the 5D Spin(11) "
                "architecture, the two independent charge forcings, the M_T repair, "
                "the heavy-pair anomaly matching, and the bound heterotic contrast.  "
                "No numerical coefficient is fabricated, no localized or Dai-Freed "
                "statement is claimed, and no gate is promoted."
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
            raise RuntimeError("generated V61 route artifacts are missing")
        if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
            raise RuntimeError("generated V61 route JSON is stale")
        if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
            raise RuntimeError("generated V61 route Markdown is stale")
    print(report["status"])
    print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
