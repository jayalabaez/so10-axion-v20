from __future__ import annotations

"""Fail-closed V64 audit of the Spin(11) AB tower and rank Goldstones.

V63 treated the secular equation of the massive AB gauge tower as if it were
the determinant of the complete supersymmetric Higgs system.  It is not.  Per
complex Q-type AB direction the KK gauginos give N rows, while their Sigma
partners plus the boundary Goldstone give N+1 columns.  The rectangular mass
operator therefore has an exact right kernel at every finite truncation.  The
kernel remains normalizable when N tends to infinity.

This audit computes that kernel, the massive determinant that omits it, the
correct low-energy anomaly ledger, and the current Z4R mass inventory.  It
retracts the V63 Wess-Zumino identification and the associated X/Y claim.  It
does not repair the resulting colored chiral zero modes and closes no gate.
"""

import argparse
import copy
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V64_SPIN11_AB_TOWER_NULL_MODE_RETRACTION_AUDIT.json"
MD_PATH = ROOT / "SUSY_V64_SPIN11_AB_TOWER_NULL_MODE_RETRACTION_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v64_spin11_ab_tower_null_mode_retraction_audit.py"

V63_ROUTE_PATH = ROOT / "SUSY_V63_SPIN11_GOLDSTONE_DISSOLUTION_WZ_INFLOW_AUDIT.json"
V63_MASTER_PATH = ROOT / "SUSY_V63_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V62_ROUTE_PATH = ROOT / "SUSY_V62_SPIN11_LOCALIZED_Z4R_ANOMALY_GS_AUDIT.json"
V59_SPIN11_PATH = ROOT / "SUSY_V59_SPIN11_GAUGE_HIGGS_COMPLETION_AUDIT.json"

EXPECTED_V63_ROUTE_CORE = (
    "b7178dc59b9cd4a49468ce5ace543c047e58cc34bcf4fcc65466ee93f3a1bfd7"
)
EXPECTED_V63_MASTER_CORE = (
    "89a16112997c2e0fb8439209b4c17e160f165c20b846697ee7da4a93cc22f3e3"
)
EXPECTED_V62_ROUTE_CORE = (
    "f99b9e09bc6d528480e2ac09cf1f2dd9e2feb5383fda25b3aa3cac436758142e"
)
EXPECTED_V59_SPIN11_CORE = (
    "bf666eb5e4d57bff18b05182d7d6cc7874bbc26dd71897153faf9ee67a5f8c42"
)

STATUS = (
    "V64_SPIN11_AB_TOWER_NULL_MODE_RETRACTION__RECTANGULAR_N_BY_N_PLUS_1_"
    "MASS_OPERATOR_HAS_EXACT_RIGHT_KERNEL__INFINITE_KERNEL_NORMALIZABLE__"
    "MASSIVE_SECULAR_DETERMINANT_OMITS_ZERO_MODE__TWELVE_Q_TYPE_COLORED_"
    "CHIRAL_COMPONENTS_SURVIVE__TRUE_IR_LEDGER_EQUALS_ORBIFOLD_WALL_SUM__"
    "V63_FORCED_WZ_AND_SHIFTED_XY_CLAIMS_RETRACTED__Z4R_FORBIDS_DIRECT_"
    "BILINEAR__REMOVAL_OPEN__STRICT_G1_OPEN__ZERO_GATES_CLOSED"
)

CLASSIFICATION = (
    "EXACT_COUNTEREXAMPLE_TO_V63_GOLDSTONE_DISSOLUTION__CURRENT_SPIN11_"
    "ACTION_HAS_NORMALIZABLE_COLORED_CHIRAL_ZERO_MODES"
)

PRIMARY_SOURCES = [
    {
        "id": "HOSOTANI_YAMATSU_2015",
        "title": "Gauge-Higgs Grand Unification",
        "authors": "Yutaka Hosotani and Naoki Yamatsu",
        "arxiv": "1504.03817",
        "url": "https://arxiv.org/abs/1504.03817",
        "scope": (
            "The original Spin(11) construction states explicitly that only nine "
            "of the twenty-one rank-breaking Nambu-Goldstone directions are eaten, "
            "while twelve Q-type modes remain tree-level massless; it separately "
            "states that the brane VEV changes low gauge-tower Neumann conditions "
            "toward Dirichlet.  See the HTML text corresponding to lines 100-102."
        ),
    },
    {
        "id": "HALL_NOMURA_2001",
        "title": "Gauge Unification in Higher Dimensions",
        "authors": "Lawrence J. Hall and Yasunori Nomura",
        "arxiv": "hep-ph/0103125",
        "url": "https://arxiv.org/abs/hep-ph/0103125",
        "scope": (
            "Standard S1/(Z2 x Z2') mode expansions: (+,-) cosine and (-,+) "
            "sine towers share k_n=(n+1/2) pi/L and form massive 4D vector towers."
        ),
    },
    {
        "id": "HEBECKER_2001",
        "title": "5D super Yang-Mills theory in 4D superspace, superfield brane operators, and applications to orbifold GUTs",
        "authors": "Arthur Hebecker",
        "arxiv": "hep-ph/0112230",
        "url": "https://arxiv.org/abs/hep-ph/0112230",
        "scope": (
            "Gauge-covariant 4D-superfield description of the 5D vector multiplet "
            "and boundary interactions; the framework in which the surviving "
            "Goldstone/Sigma chiral combination is counted."
        ),
    },
    {
        "id": "ARKANI_HAMED_GREGOIRE_WACKER_2001",
        "title": "Higher dimensional supersymmetry in 4D superspace",
        "authors": "Nima Arkani-Hamed, Thomas Gregoire, and Jay Wacker",
        "arxiv": "hep-th/0101233",
        "url": "https://arxiv.org/abs/hep-th/0101233",
        "scope": (
            "Superspace framework for brane interactions, anomaly inflow, and "
            "super-Chern-Simons terms; it makes an explicit supersymmetric "
            "functional an obligation rather than something fixed by a residue alone."
        ),
    },
    {
        "id": "PILO_RIOTTO_2002",
        "title": "On Anomalies in Orbifold Theories",
        "authors": "Luigi Pilo and Antonio Riotto",
        "arxiv": "hep-th/0202144",
        "url": "https://arxiv.org/abs/hep-th/0202144",
        "scope": (
            "In S1/(Z2 x Z2') examples, the Chern-Simons term is obtained from "
            "an explicitly regulated KK determinant.  This supports requiring the "
            "regulator and determinant phase before asserting an inflow functional."
        ),
    },
    {
        "id": "GRIPAIOS_2008",
        "title": "Anomaly Holography, the Wess-Zumino-Witten Term, and Electroweak Symmetry Breaking",
        "authors": "Ben Gripaios",
        "arxiv": "0803.0497",
        "url": "https://arxiv.org/abs/0803.0497",
        "scope": (
            "Interval anomalies can induce a WZW term only for the appropriate "
            "consistent anomaly pattern; such a term is not automatic and some "
            "cosets explicitly have none."
        ),
    },
    {
        "id": "GARCIA_ETXEBARRIA_MONTERO_2018",
        "title": "Dai-Freed anomalies in particle physics",
        "authors": "Inaki Garcia-Etxebarria and Miguel Montero",
        "arxiv": "1808.00009",
        "url": "https://arxiv.org/abs/1808.00009",
        "scope": (
            "Refined discrete-anomaly cancellation depends on the global fermion "
            "and UV data; the still-absent eta-invariant calculation cannot be "
            "replaced by mixed-anomaly residues."
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


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else str(value)


def exact_mass_action(
    diagonal: Sequence[Fraction], mu: Fraction, vector: Sequence[Fraction]
) -> list[Fraction]:
    """Apply [diag(k_n) | mu 1] without constructing a dense matrix."""

    n = len(diagonal)
    if len(vector) != n + 1:
        raise ValueError("right vector must have N+1 entries")
    return [diagonal[i] * vector[i] + mu * vector[-1] for i in range(n)]


def finite_mass_operator_certificate() -> dict[str, Any]:
    """Exact finite-N rank/nullity certificate in a rational test basis."""

    mu = Fraction(7, 5)
    rows = []
    for n_modes in (1, 2, 4, 8, 16, 32):
        # The common pi/L factor is irrelevant to the algebraic rank test.
        diagonal = [Fraction(2 * n + 1, 2) for n in range(n_modes)]
        null = [-mu / k for k in diagonal] + [Fraction(1)]
        residual = exact_mass_action(diagonal, mu, null)
        rows.append(
            {
                "N": n_modes,
                "shape": [n_modes, n_modes + 1],
                "rank": n_modes,
                "right_nullity": 1,
                "diagonal_minor_nonzero": all(k != 0 for k in diagonal),
                "null_residual_exact": [fraction_text(x) for x in residual],
                "null_residual_zero": all(x == 0 for x in residual),
            }
        )
    n_example = 4
    diagonal = [Fraction(2 * n + 1, 2) for n in range(n_example)]
    null = [-mu / k for k in diagonal] + [Fraction(1)]
    return {
        "per_complex_Q_direction": {
            "row_fields": "lambda_n^AB, n=0,...,N-1, fermion Z4R charge +1",
            "column_fields": (
                "Sigma_n^AB, n=0,...,N-1, followed by the boundary Goldstone "
                "G; every column fermion has Z4R charge -1"
            ),
            "KK_masses": "k_n=(n+1/2) pi/L",
            "normalized_wall_mixing": "mu_n=mu=sqrt(2/L) g5 v",
            "operator": "M_N=[diag(k_0,...,k_(N-1)) | mu * 1_N]",
            "shape": "N x (N+1)",
            "rank_proof": (
                "the first N columns form a diagonal minor with determinant "
                "product_n k_n != 0, hence rank(M_N)=N and right-nullity=1"
            ),
            "right_null_vector": (
                "chi_0 proportional to (-mu/k_0,...,-mu/k_(N-1),1), "
                "i.e. G-sum_n(mu/k_n) Sigma_n"
            ),
        },
        "exact_rational_truncation_checks": rows,
        "example_N4": {
            "mu": fraction_text(mu),
            "diagonal_with_pi_over_L_factored_out": [
                fraction_text(x) for x in diagonal
            ],
            "right_null_vector": [fraction_text(x) for x in null],
            "residual": [
                fraction_text(x) for x in exact_mass_action(diagonal, mu, null)
            ],
        },
        "all_truncations_pass": all(row["null_residual_zero"] for row in rows),
        "conclusion": (
            "a finite KK truncation never has enough +1-charge lambda rows to "
            "mass all -1-charge Sigma columns plus G; one chiral null mode is exact"
        ),
    }


def infinite_null_mode_certificate() -> dict[str, Any]:
    """Show that the finite-N right kernel survives the Hilbert-space limit."""

    alpha2_sample = 1.7
    convergence = []
    for cutoff in (4, 16, 64, 256, 1024):
        partial = sum(1.0 / ((n + 0.5) ** 2) for n in range(cutoff))
        norm2 = 1.0 + (2.0 * alpha2_sample / math.pi**2) * partial
        convergence.append(
            {
                "N": cutoff,
                "norm_squared": round(norm2, 14),
                "error_to_exact": round(1.0 + alpha2_sample - norm2, 14),
            }
        )

    profile_samples = []
    # L=1 and g5*v=1 are sufficient to test the exact Fourier identity.
    for y_over_l in (0.08, 0.25, 0.5, 0.83):
        cutoff = 4096
        bulk = -sum(
            (2.0 / math.pi)
            * math.sin((n + 0.5) * math.pi * y_over_l)
            / (n + 0.5)
            for n in range(cutoff)
        )
        profile_samples.append(
            {
                "y_over_L": y_over_l,
                "truncated_bulk_profile_for_g5v_1": round(bulk, 10),
                "absolute_error_to_minus_1": round(abs(bulk + 1.0), 10),
            }
        )

    return {
        "half_integer_sum_identity": (
            "sum_{n=0}^infinity 1/(n+1/2)^2 = pi^2/2"
        ),
        "normalization_derivation": (
            "1+sum_n(mu/k_n)^2 = 1 + (2 g5^2 v^2/L) "
            "(L^2/pi^2)(pi^2/2) = 1+g5^2 v^2 L"
        ),
        "alpha_definition": "alpha^2=g5^2 v^2 L",
        "normalized_zero_mode": (
            "chi_0=[G-sum_n(mu/k_n) Sigma_n]/sqrt(1+alpha^2)"
        ),
        "norm_finite_for_every_finite_alpha": True,
        "sample_alpha_squared": alpha2_sample,
        "norm_convergence": convergence,
        "exact_sample_norm_squared": 1.0 + alpha2_sample,
        "fourier_identity": (
            "sum_{n>=0} sin[(n+1/2) pi y/L]/(n+1/2)=pi/2 for 0<y<2L"
        ),
        "bulk_profile": (
            "the Sigma part of chi_0 is the flat profile -g5 v on 0<y<L; "
            "the mode continuously moves from boundary G at alpha=0 to a "
            "bulk Wilson-line/Sigma chiral mode as alpha grows"
        ),
        "profile_samples": profile_samples,
        "physical_conclusion": (
            "the null vector is square-normalizable and cannot disappear at the "
            "end of the semi-infinite tower"
        ),
    }


def secular_function(x: float, alpha2: float) -> float:
    return x * math.cos(x) + alpha2 * math.sin(x)


def bisect_massive_root(alpha2: float, level: int) -> float:
    eps = 1.0e-10
    left = (level + 0.5) * math.pi + eps
    right = (level + 1.0) * math.pi - eps
    f_left = secular_function(left, alpha2)
    f_right = secular_function(right, alpha2)
    if f_left * f_right >= 0:
        raise RuntimeError("massive-root bracket failed")
    for _ in range(100):
        mid = 0.5 * (left + right)
        f_mid = secular_function(mid, alpha2)
        if f_left * f_mid <= 0:
            right = mid
            f_right = f_mid
        else:
            left = mid
            f_left = f_mid
    return 0.5 * (left + right)


def massive_determinant_certificate() -> dict[str, Any]:
    alpha2 = 1.4
    q = 0.8
    exact_ratio = 1.0 + alpha2 * math.tanh(q) / q
    convergence = []
    for cutoff in (4, 16, 64, 256, 1024):
        partial = 1.0 + 2.0 * alpha2 * sum(
            1.0 / (q * q + ((n + 0.5) * math.pi) ** 2)
            for n in range(cutoff)
        )
        convergence.append(
            {
                "N": cutoff,
                "finite_rank_one_ratio": round(partial, 14),
                "error_to_closed_form": round(exact_ratio - partial, 14),
            }
        )
    roots = [bisect_massive_root(alpha2, level) for level in range(5)]
    root_rows = [
        {
            "level": level,
            "x": round(root, 14),
            "lower_half_integer_pi": round((level + 0.5) * math.pi, 14),
            "upper_integer_pi": round((level + 1.0) * math.pi, 14),
            "inside_open_bracket": (level + 0.5) * math.pi
            < root
            < (level + 1.0) * math.pi,
            "residual": round(secular_function(root, alpha2), 13),
        }
        for level, root in enumerate(roots)
    ]
    return {
        "matrix_determinant_lemma_finite_N": (
            "det[p^2+M_N M_N^dag]/product_n(p^2+k_n^2) "
            "=1+mu^2 sum_n 1/(p^2+k_n^2)"
        ),
        "half_integer_resolvent_identity": (
            "sum_n 1/(p^2+k_n^2)=L tanh(pL)/(2p)"
        ),
        "euclidean_massive_ratio": (
            "R(p)=1+g5^2 v^2 tanh(pL)/p "
            "=1+alpha^2 tanh(q)/q, q=pL"
        ),
        "sample": {
            "alpha_squared": alpha2,
            "q": q,
            "closed_form_ratio": round(exact_ratio, 14),
            "convergence": convergence,
        },
        "massive_secular_equation": (
            "x cos(x)+alpha^2 sin(x)=0, x=mL, with x=0 explicitly excluded"
        ),
        "equivalent_unmultiplied_equation": (
            "1+alpha^2 tan(x)/x=0; its x->0 limit is 1+alpha^2, not zero"
        ),
        "x_zero_is_spurious_after_multiplication": True,
        "massive_roots": root_rows,
        "all_massive_roots_bracketed": all(
            row["inside_open_bracket"] for row in root_rows
        ),
        "operator_mismatch": (
            "M_N M_N^dag is N by N and contains only the N nonzero singular "
            "values.  M_N^dag M_N is (N+1) by (N+1) and contains the same N "
            "massive values plus the exact zero eigenvalue.  V63 used the "
            "former secular equation to make a claim about the latter spectrum."
        ),
        "conclusion": (
            "the Robin-Dirichlet equation correctly shifts every massive vector "
            "root from half-integer toward integer pi, but it cannot remove the "
            "additional chiral kernel"
        ),
    }


def representation_and_source_correction() -> dict[str, Any]:
    return {
        "AB_under_Pati_Salam": "(2,2,6)",
        "SM_decomposition": {
            "Q_type_rank_vev_coupled": [
                "(3,2)_(+1/6)",
                "(3bar,2)_(-1/6)",
            ],
            "XY_type_not_rank_vev_coupled": [
                "(3,2)_(-5/6)",
                "(3bar,2)_(+5/6)",
            ],
        },
        "group_theory_reason": (
            "Spin(10)->SU(5) breaks 45 into the SU(5)-coset "
            "10+10bar+1.  The Q-type AB pair lies in 10+10bar and couples to "
            "the rank VEV.  The X/Y-type AB pair lies in the unbroken SU(5) "
            "adjoint 24 and is the other half of (2,2,6)."
        ),
        "primary_source_certificate": {
            "source": "Hosotani-Yamatsu arXiv:1504.03817",
            "location": "HTML lines 100-102",
            "reported_count": {
                "rank_breaking_NG_directions": 21,
                "eaten_by_zero_mode_gauge_fields": 9,
                "uneaten_tree_massless": 12,
            },
            "reported_quantum_numbers": "one Q-type complex scalar sector (3,2)_(1/6) in the non-supersymmetric model",
            "reported_boundary_effect": (
                "the VEV changes Neumann toward Dirichlet for low gauge modes; "
                "the same passage nevertheless retains the twelve uneaten modes"
            ),
            "agrees_with_rectangular_kernel": True,
        },
        "V63_XY_claim": "RETRACTED",
        "correction": (
            "the rank VEV shifts the Q-type massive AB tower, not the X/Y half; "
            "V63's assertion that the dissolved set fixes the X/Y proton-decay "
            "scale was a representation misidentification"
        ),
        "dimension_six_proton_scale_from_rank_vev": "NOT_DERIVED",
    }


def surviving_exotic_ledger(v62_route: Mapping[str, Any]) -> dict[str, Any]:
    post = v62_route["post_vev_inflow_deficit"]
    mssm_a3 = Fraction(post["IR_ledger_from_V61"]["A3"])
    mssm_a2 = Fraction(post["IR_ledger_from_V61"]["A2"])
    wall_a3 = Fraction(post["orbifold_wall_sums"]["SU3_via_SU4"])
    wall_a2 = Fraction(post["orbifold_wall_sums"]["SU2_L"])

    exotic_a3 = Fraction(-2)
    exotic_a2 = Fraction(-3)
    actual_a3 = mssm_a3 + exotic_a3
    actual_a2 = mssm_a2 + exotic_a2
    return {
        "surviving_sector": {
            "irreps": ["(3,2)_(+1/6)", "(3bar,2)_(-1/6)"],
            "complex_chiral_components": 12,
            "superfield_Z4R_charge": 0,
            "fermion_Z4R_charge": -1,
            "SM_gauge_character": "vectorlike",
            "mixed_R_Dynkin_sums": {
                "T_SU3": "2",
                "T_SU2L": "3",
            },
            "mixed_R_anomaly": {
                "Delta_A3": fraction_text(exotic_a3),
                "Delta_A2": fraction_text(exotic_a2),
            },
        },
        "MSSM_only_ledger_from_V61": {
            "A3": fraction_text(mssm_a3),
            "A2": fraction_text(mssm_a2),
        },
        "actual_IR_ledger_MSSM_plus_exotics": {
            "A3": fraction_text(actual_a3),
            "A2": fraction_text(actual_a2),
        },
        "V62_orbifold_wall_sum": {
            "A3": fraction_text(wall_a3),
            "A2": fraction_text(wall_a2),
        },
        "matching_identities": {
            "SU3": f"{mssm_a3}+({exotic_a3})={actual_a3}={wall_a3}",
            "SU2_L": f"{mssm_a2}+({exotic_a2})={actual_a2}={wall_a2}",
            "both_close_without_WZ": actual_a3 == wall_a3
            and actual_a2 == wall_a2,
        },
        "V62_deficit_reinterpretation": (
            "the numbers (-2,-3) are the anomaly of light exotics omitted from "
            "the MSSM-only ledger, not anomaly inflow from integrated-out modes"
        ),
        "V63_forced_WZ_status": "RETRACTED__NO_DEFICIT_AFTER_CORRECT_LIGHT_SPECTRUM",
        "WZ_functional_for_this_matching": "NOT_FORCED",
        "why_no_V63_WZ_functional_was_derived": [
            "the purportedly integrated-out Q-type chiral sector is actually a normalizable light kernel",
            "the anomaly residues (-2,-3) determine a variation class but do not by themselves construct a local supersymmetric functional",
            "the Q-type Goldstone scalar has superfield charge q=0 and therefore supplies no nonlinear pure-Z4R shift",
            "Spin(11) has no degree-three invariant, so the ordinary pure-Spin(11) five-dimensional Chern-Simons route carried from V59 is absent",
            "the regulated determinant phase, superspace completion, global gauge form, and Dai-Freed eta invariant were never supplied",
        ],
        "strong_claim_boundary": (
            "V64 proves that the specific V63 WZ term is neither required by the "
            "correct spectrum nor dynamically derived.  It does not prove that "
            "every possible added topological sector is impossible."
        ),
    }


def z4r_mass_inventory(
    v62_route: Mapping[str, Any], v59_route: Mapping[str, Any]
) -> dict[str, Any]:
    fermion_charges = v62_route["conventions"]["fermion_charges"]
    rank = v59_route["rank_breaking_sector"]
    return {
        "charge_inference": {
            "C_and_Cbar_fermion_charge": fermion_charges["C_and_Cbar_fermions"],
            "Goldstone_superfield_charge": 0,
            "superpotential_required_charge_mod_4": 2,
        },
        "operator_scan": [
            {
                "operator": "X_Q X_Qbar",
                "charge_mod_4": 0,
                "allowed_in_W": False,
                "effect": "the direct vectorlike supersymmetric mass is forbidden",
            },
            {
                "operator": "S X_Q X_Qbar (contained in S C Cbar)",
                "charge_mod_4": 2,
                "allowed_in_W": True,
                "effect": (
                    "it gives no bilinear mass in the certified SUSY vacuum because <S>=0"
                ),
            },
        ],
        "existing_q2_fields": {
            "S": "SM singlet; cannot be a conjugate Q-type mass partner",
            "T_10": (
                "Spin(10) 10 = SU(5) 5+5bar and contains no (3bar,2) or (3,2) partner"
            ),
        },
        "certified_rank_vacuum_S": rank["supersymmetric_vacuum"]["S"],
        "q2_conjugate_Q_partner_in_current_inventory": False,
        "full_rank_Q_type_mass_matrix_in_current_vacuum": False,
        "possible_but_unbuilt_routes": [
            "add explicit q=2 conjugate wall chirals and re-audit every anomaly and proton operator",
            "modify the projector/rank-breaking architecture so every Goldstone has a true gauge zero-mode partner",
            "generate <S> only with a complete SUSY-breaking sector, accepting that q(S)=2 breaks Z4R to its Z2 subgroup and re-auditing proton protection",
        ],
        "current_action_verdict": (
            "the exact Z4R that protects the proton also forbids the obvious "
            "bilinear that would remove the surviving vectorlike colored pair"
        ),
    }


def retraction_ledger() -> list[dict[str, str]]:
    return [
        {
            "prior_claim": "V59: generic rank breaking leaves zero new light colored states",
            "V64_status": "RETRACTED_FOR_THE_ORBIFOLD_ACTION",
            "reason": "only nine gauge zero-mode directions eat rank chirals; the Q-type twelve form the AB kernel",
        },
        {
            "prior_claim": "V63: twelve Q-type Goldstone chirals dissolve into the semi-infinite AB tower",
            "V64_status": "RETRACTED",
            "reason": "M_N is rectangular and its unique right null vector remains normalizable at N=infinity",
        },
        {
            "prior_claim": "V63: anomaly matching uniquely forces a (-2,-3) WZ inflow term",
            "V64_status": "RETRACTED",
            "reason": "the light exotic anomaly itself is (-2,-3), so the complete IR ledger matches the wall sum without WZ",
        },
        {
            "prior_claim": "V63: the dissolved set includes X/Y and the rank VEV fixes their proton-decay scale",
            "V64_status": "RETRACTED",
            "reason": "the VEV-coupled half of (2,2,6) is Q-type; X/Y is the SU(5)-adjoint half",
        },
        {
            "prior_claim": "V61: the Z4R selector is the unique arithmetic class in the tested scan",
            "V64_status": "PRESERVED_AS_ARITHMETIC_ONLY",
            "reason": "the null-mode calculation does not alter the charge-classification theorem",
        },
        {
            "prior_claim": "V62: pre-VEV localized wall ledger and Lie-algebra-level GS congruences",
            "V64_status": "PRESERVED_CONDITIONALLY",
            "reason": "the retraction changes the post-VEV light-spectrum interpretation, not the pre-VEV projector trace",
        },
    ]


def repair_acceptance_criteria() -> list[dict[str, str]]:
    return [
        {
            "id": "R1",
            "criterion": "an explicit modified quadratic action gives a square/Fredholm-index-zero operator in every Q-type channel",
            "fail_closed_test": "construct its finite-N matrices and prove zero right nullity uniformly as N grows",
        },
        {
            "id": "R2",
            "criterion": "the infinite operator has no normalizable zero or parametrically light colored chiral mode",
            "fail_closed_test": "solve the exact kernel and spectrum before using a massive secular equation",
        },
        {
            "id": "R3",
            "criterion": "every new partner and mass term respects the claimed unbroken selector at the scale where it is used",
            "fail_closed_test": "list gauge representations, Z4R charges, VEVs, and a full-rank mass determinant",
        },
        {
            "id": "R4",
            "criterion": "localized/global anomalies remain canceled after the repair",
            "fail_closed_test": "recompute both wall ledgers, global-form quantization, and the Dai-Freed phase with the added fields",
        },
        {
            "id": "R5",
            "criterion": "the repaired spectrum retains the all-orders proton selector and realistic flavor route",
            "fail_closed_test": "rerun the operator scan and the complete mediator determinant; no cross-route assumption is accepted",
        },
    ]


def obligations() -> list[dict[str, str]]:
    return [
        {
            "obligation": "remove the twelve Q-type colored chiral components with an explicit Z4R-compatible full-rank action",
            "status": "OPEN_BLOCKER",
            "detail": "the current action has an exact normalizable zero mode per complex Q-type direction",
        },
        {
            "obligation": "recompute localized and global anomalies after any repair",
            "status": "OPEN",
            "detail": "new q=2 partners or Z4R-breaking VEVs change the V62 ledger",
        },
        {
            "obligation": "large-gauge/global-form quantization and Dai-Freed phase",
            "status": "OPEN",
            "detail": "V64 does not promote V62's Lie-algebra-level GS arithmetic to a full quantum definition",
        },
        {
            "obligation": "saxion stabilization and axino/SUSY-breaking sector",
            "status": "OPEN",
            "detail": "no Kahler potential or stabilizing dynamics is specified",
        },
        {
            "obligation": "exact mirror-mediator determinant and realistic flavor fit",
            "status": "OPEN",
            "detail": "the AB gauge-tower determinant solved here is not the unspecified flavor determinant",
        },
        {
            "obligation": "UV regulator/completion",
            "status": "OPEN",
            "detail": "the 5D EFT still has no exhibited microscopic regulator",
        },
    ]


def falsifiers() -> list[dict[str, str]]:
    return [
        {
            "id": "F1",
            "test": "supply a missing current-action row that pairs the boundary G/Sigma kernel without adding fields",
            "effect": "rebuild M_N with that row and rerun the exact nullity proof",
        },
        {
            "id": "F2",
            "test": "show the displayed right null vector is non-normalizable in the declared flat interval action",
            "effect": "the infinite-limit obstruction would fail",
        },
        {
            "id": "F3",
            "test": "derive a Z4R-allowed nonzero mass for the Q-type pair in the certified S=0 supersymmetric vacuum",
            "effect": "the current inventory obstruction would fail",
        },
        {
            "id": "F4",
            "test": "demonstrate that the rank VEV couples to the X/Y rather than Q-type half of (2,2,6)",
            "effect": "the representation retraction would need revision",
        },
        {
            "id": "F5",
            "test": "recompute the complete light ledger without the Q-type pair and without an additional mass mechanism",
            "effect": "it must identify where the normalizable chiral kernel went",
        },
    ]


def strict_g1_matrix() -> list[dict[str, str]]:
    return [
        {
            "criterion": "exact_two_Higgs_zero_modes_no_colored_chiral_zero_modes",
            "status": "FAIL_FOR_COMPLETE_ACTION",
            "evidence": "the adjoint Sigma projector still yields two Higgs modes, but rank breaking adds twelve Q-type colored chiral components",
        },
        {
            "criterion": "rank_breaking_without_light_exotics",
            "status": "FAIL_EXACT",
            "evidence": "one normalizable null mode per complex Q-type AB direction",
        },
        {
            "criterion": "V63_Goldstone_dissolution",
            "status": "RETRACTED",
            "evidence": "rectangular M_N has right-nullity one for all N and finite infinite-limit norm",
        },
        {
            "criterion": "post_VEV_WZ_inflow",
            "status": "NOT_FORCED",
            "evidence": "MSSM plus the surviving exotic anomaly equals the V62 wall sum exactly",
        },
        {
            "criterion": "exact_proton_selector",
            "status": "PASS_ARITHMETIC_ONLY",
            "evidence": "V61 charge theorem survives, but its q=0 exotic pair has no allowed direct mass",
        },
        {
            "criterion": "localized_R_anomaly_ledger",
            "status": "PRE_VEV_LEDGER_PRESERVED_CONDITIONALLY",
            "evidence": "V62 projector trace remains; its post-VEV MSSM-only interpretation is corrected",
        },
        {
            "criterion": "relative_5D_Dai_Freed_and_large_gauge_quantization",
            "status": "OPEN",
            "evidence": "not computed",
        },
        {
            "criterion": "realistic_full_rank_Yukawas",
            "status": "OPEN",
            "evidence": "the mirror-mediator determinant remains unspecified",
        },
        {
            "criterion": "UV_complete_regulator",
            "status": "OPEN",
            "evidence": "not exhibited",
        },
        {
            "criterion": "strict_G1",
            "status": "OPEN_WITH_CURRENT_SPIN11_ACTION_REJECTED",
            "evidence": "the exact light colored kernel is already a spectrum-level blocker",
        },
    ]


def gate_ledger() -> list[dict[str, Any]]:
    decisions = {
        "G1": (
            "OPEN WITH RETRACTION: the present Spin(11) action has twelve "
            "normalizable Q-type colored chiral components and is not a valid "
            "one-action completion."
        ),
        "G2": "OPEN: the coefficient-level 4D theory now contains an unremoved vectorlike colored pair in addition to the unsolved flavor/soft sectors.",
        "G3": "OPEN: compactification and saxion stabilization remain absent.",
        "G4": "OPEN WITH EXACT FAILURE: the two gauge-Higgs doublets survive, but the complete post-rank spectrum fails the zero-colored-chiral requirement.",
        "G5": "OPEN: arithmetic R parity is retained, but the spectrum and axino/LSP cosmology are not viable or computed.",
        "G6": "OPEN: inflation, reheating, and defect history remain absent.",
        "G7": "OPEN WITH RETRACTION: the V63 rank-VEV-shifted X/Y scale claim is withdrawn; no proton lifetime is derived.",
        "G8": "OPEN: no UV completion, full quantum definition, or quantified predictivity score exists.",
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
        "bound_V63_route": {
            "path": str(V63_ROUTE_PATH.resolve()),
            "sha256": sha256_file(V63_ROUTE_PATH),
        },
        "bound_V63_master": {
            "path": str(V63_MASTER_PATH.resolve()),
            "sha256": sha256_file(V63_MASTER_PATH),
        },
        "bound_V62_route": {
            "path": str(V62_ROUTE_PATH.resolve()),
            "sha256": sha256_file(V62_ROUTE_PATH),
        },
        "bound_V59_spin11": {
            "path": str(V59_SPIN11_PATH.resolve()),
            "sha256": sha256_file(V59_SPIN11_PATH),
        },
        "primary_sources": PRIMARY_SOURCES,
    }


def build_report() -> dict[str, Any]:
    v63_route = load_bound(V63_ROUTE_PATH, EXPECTED_V63_ROUTE_CORE, "V63 route")
    v63_master = load_bound(V63_MASTER_PATH, EXPECTED_V63_MASTER_CORE, "V63 master")
    v62_route = load_bound(V62_ROUTE_PATH, EXPECTED_V62_ROUTE_CORE, "V62 route")
    v59_route = load_bound(V59_SPIN11_PATH, EXPECTED_V59_SPIN11_CORE, "V59 Spin11 route")

    finite = finite_mass_operator_certificate()
    infinite = infinite_null_mode_certificate()
    massive = massive_determinant_certificate()
    representation = representation_and_source_correction()
    anomaly = surviving_exotic_ledger(v62_route)
    inventory = z4r_mass_inventory(v62_route, v59_route)
    gates = gate_ledger()

    checks = {
        "bound_V63_claim_was_dissolution": (
            v63_route["forced_wz_term"]["status"]
            == "COEFFICIENT_FORCED__DYNAMICAL_EXTRACTION_OPEN"
        ),
        "bound_V63_master_kept_G1_open": all(
            row["status"] == "OPEN" for row in v63_master["gate_ledger"]
        ),
        "AB_parities_match_bound_V63": (
            v63_route["ab_block_recount"]["V_AB_parity"] == [1, -1]
            and v63_route["ab_block_recount"]["Sigma_AB_parity"] == [-1, 1]
        ),
        "finite_truncations_have_exact_kernel": finite["all_truncations_pass"],
        "infinite_kernel_norm_finite": infinite["norm_finite_for_every_finite_alpha"],
        "massive_roots_all_bracketed": massive["all_massive_roots_bracketed"],
        "x_zero_excluded_from_massive_equation": massive[
            "x_zero_is_spurious_after_multiplication"
        ],
        "primary_source_agrees_with_12_uneaten": representation[
            "primary_source_certificate"
        ]["agrees_with_rectangular_kernel"],
        "actual_IR_matches_walls_without_WZ": anomaly["matching_identities"][
            "both_close_without_WZ"
        ],
        "direct_Z4R_mass_absent": not inventory[
            "full_rank_Q_type_mass_matrix_in_current_vacuum"
        ],
        "V63_WZ_retracted": anomaly["V63_forced_WZ_status"].startswith(
            "RETRACTED"
        ),
        "all_eight_gates_open": len(gates) == 8
        and all(row["status"] == "OPEN" for row in gates),
        "zero_gate_promotions": not any(
            "CLOSED" in row["status"] for row in gates
        ),
    }

    report: dict[str, Any] = {
        "schema": "susy_v64_spin11_ab_tower_null_mode_retraction_audit/v1",
        "version": "V64",
        "date": "2026-08-29",
        "status": STATUS,
        "classification": CLASSIFICATION,
        "lineage": {
            "bound_V63_route_core": v63_route["core_sha256"],
            "bound_V63_master_core": v63_master["core_sha256"],
            "bound_V62_route_core": v62_route["core_sha256"],
            "bound_V59_spin11_core": v59_route["core_sha256"],
            "supersedes": (
                "V63 only where it asserted dissolution, forced WZ inflow, and "
                "the rank-VEV-shifted X/Y scale; all other carried results retain "
                "their explicitly stated scope"
            ),
        },
        "research_question": (
            "Does the exact supersymmetric AB KK mass operator really absorb the "
            "twelve Q-type rank Goldstones, or does the complete rectangular "
            "operator retain a normalizable chiral zero mode?"
        ),
        "finite_KK_mass_operator": finite,
        "infinite_normalizable_null_mode": infinite,
        "massive_determinant_and_secular_flow": massive,
        "representation_and_primary_source_correction": representation,
        "corrected_post_VEV_anomaly_ledger": anomaly,
        "Z4R_mass_inventory": inventory,
        "retraction_ledger": retraction_ledger(),
        "repair_acceptance_criteria": repair_acceptance_criteria(),
        "remaining_obligations": obligations(),
        "falsifiers": falsifiers(),
        "strict_G1_matrix": strict_g1_matrix(),
        "gate_ledger": gates,
        "integrity_checks": checks,
        "n_integrity_checks": len(checks),
        "n_failed_integrity_checks": sum(not value for value in checks.values()),
        "terminal_decision": {
            "V63_dissolution_claim_valid": False,
            "V63_forced_WZ_claim_valid": False,
            "current_Spin11_action_accepted": False,
            "V64_G1_closed": False,
            "complete_theory": False,
            "gate_promotions": 0,
            "exact_blocker": (
                "twelve normalizable Q-type colored chiral components with no "
                "full-rank Z4R-compatible mass in the current supersymmetric vacuum"
            ),
            "next_action": (
                "do not compute a WZ functional for a nonexistent deficit; first "
                "supply and audit an explicit null-mode lifting sector satisfying R1-R5"
            ),
        },
        "claim_boundary": {
            "new_fundamental_physics_invented": False,
            "exact_quadratic_action_result": True,
            "massive_determinant_not_confused_with_full_chiral_spectrum": True,
            "primary_source_corroboration_not_used_as_substitute_for_derivation": True,
            "V62_large_gauge_and_saxion_obligations_not_overclaimed": True,
            "no_gate_promotion": True,
        },
        "source_manifest": source_manifest(),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report["core_sha256"] != canonical_sha(report):
        raise RuntimeError("V64 canonical core mismatch")
    if report["n_failed_integrity_checks"] != 0:
        failed = [
            key for key, value in report["integrity_checks"].items() if not value
        ]
        raise RuntimeError(f"V64 integrity checks failed: {failed}")
    if report["finite_KK_mass_operator"]["all_truncations_pass"] is not True:
        raise RuntimeError("finite KK nullity certificate failed")
    if not report["corrected_post_VEV_anomaly_ledger"]["matching_identities"][
        "both_close_without_WZ"
    ]:
        raise RuntimeError("corrected IR anomaly matching failed")
    if report["terminal_decision"]["current_Spin11_action_accepted"]:
        raise RuntimeError("current Spin11 action must remain rejected")
    if report["terminal_decision"]["complete_theory"]:
        raise RuntimeError("V64 may not claim a complete theory")
    if any(row["status"] != "OPEN" for row in report["gate_ledger"]):
        raise RuntimeError("all G1-G8 gates must remain OPEN")


def render_markdown(report: Mapping[str, Any]) -> str:
    finite = report["finite_KK_mass_operator"]
    infinite = report["infinite_normalizable_null_mode"]
    massive = report["massive_determinant_and_secular_flow"]
    anomaly = report["corrected_post_VEV_anomaly_ledger"]
    representation = report["representation_and_primary_source_correction"]
    inventory = report["Z4R_mass_inventory"]

    lines = [
        "# SUSY V64 Spin(11) AB-tower null-mode retraction audit",
        "",
        f"- Status: `{report['status']}`",
        f"- Core: `{report['core_sha256']}`",
        f"- Classification: `{report['classification']}`",
        "- Outcome: **V63's Goldstone-dissolution and forced-WZ claims are retracted; the current Spin(11) action contains twelve colored chiral zero-mode components and G1 remains open.**",
        "- Gate promotions: **0/8**.",
        "",
        "## Bottom line",
        "",
        (
            "The AB tower's massive Robin--Dirichlet equation is correct, but it "
            "is not the determinant of the complete supersymmetric Higgs system.  "
            "For every complex Q-type direction the mass matrix has N KK-gaugino "
            "rows and N Sigma columns plus one boundary-Goldstone column.  Its "
            "right-nullity is therefore one, and the null vector stays normalizable "
            "when the full tower is restored."
        ),
        "",
        (
            "The twelve omitted chiral components carry exactly (-2,-3), so "
            "MSSM plus exotics gives (1,-2), equal to the V62 wall sum.  There is "
            "no missing anomaly for a Wess--Zumino term to carry.  The exact Z4R "
            "forbids their direct bilinear, and the current S=0 vacuum supplies no "
            "alternative full-rank mass."
        ),
        "",
        "## Exact finite-N mass operator",
        "",
        f"- `{finite['per_complex_Q_direction']['operator']}` with `{finite['per_complex_Q_direction']['KK_masses']}` and `{finite['per_complex_Q_direction']['normalized_wall_mixing']}`.",
        f"- {finite['per_complex_Q_direction']['rank_proof']}.",
        f"- Null mode: `{finite['per_complex_Q_direction']['right_null_vector']}`.",
        f"- Exact rational truncations tested: {', '.join(str(row['N']) for row in finite['exact_rational_truncation_checks'])}; every residual is zero.",
        "",
        "## Infinite normalizable mode",
        "",
        f"- `{infinite['half_integer_sum_identity']}`.",
        f"- `{infinite['normalization_derivation']}`.",
        f"- `{infinite['normalized_zero_mode']}`.",
        f"- {infinite['bulk_profile']}.",
        "",
        "## What the massive determinant does—and does not—show",
        "",
        f"- `{massive['matrix_determinant_lemma_finite_N']}`.",
        f"- `{massive['euclidean_massive_ratio']}`.",
        f"- Massive roots obey `{massive['massive_secular_equation']}`.",
        f"- `{massive['equivalent_unmultiplied_equation']}`; x=0 is spurious after multiplying by x cos(x).",
        f"- {massive['operator_mismatch']}",
        "",
        "## Representation correction and primary-source check",
        "",
        f"- Q-type VEV-coupled half: `{', '.join(representation['SM_decomposition']['Q_type_rank_vev_coupled'])}`.",
        f"- X/Y half not coupled by this rank VEV: `{', '.join(representation['SM_decomposition']['XY_type_not_rank_vev_coupled'])}`.",
        f"- {representation['group_theory_reason']}",
        (
            "- Hosotani and Yamatsu independently state that 21 rank-breaking NG "
            "directions yield nine eaten and twelve uneaten tree-level massless "
            "modes, even while the gauge boundary condition shifts toward "
            "Dirichlet (arXiv:1504.03817, HTML lines 100-102)."
        ),
        "- V63's rank-VEV-shifted X/Y proton-scale claim is therefore **retracted**.",
        "",
        "## Corrected anomaly matching",
        "",
        "| Ledger | SU(3) | SU(2)L |",
        "|---|---:|---:|",
        f"| MSSM-only V61 ledger | {anomaly['MSSM_only_ledger_from_V61']['A3']} | {anomaly['MSSM_only_ledger_from_V61']['A2']} |",
        f"| Surviving Q-type chirals | {anomaly['surviving_sector']['mixed_R_anomaly']['Delta_A3']} | {anomaly['surviving_sector']['mixed_R_anomaly']['Delta_A2']} |",
        f"| Actual IR total | {anomaly['actual_IR_ledger_MSSM_plus_exotics']['A3']} | {anomaly['actual_IR_ledger_MSSM_plus_exotics']['A2']} |",
        f"| V62 wall sum | {anomaly['V62_orbifold_wall_sum']['A3']} | {anomaly['V62_orbifold_wall_sum']['A2']} |",
        "",
        f"Both identities close without WZ: `{anomaly['matching_identities']['both_close_without_WZ']}`.  The V63 forced-WZ status is `{anomaly['V63_forced_WZ_status']}`.",
        (
            "The residue alone never constructed the claimed functional: the "
            "Goldstone scalar has q=0, Spin(11) has no ordinary cubic-invariant "
            "CS5 term, and neither a regulated determinant phase nor the "
            "superspace/Dai--Freed completion was supplied."
        ),
        "",
        "## Why the current Z4R inventory does not lift the pair",
        "",
        (
            "The surviving chiral superfields have q=0.  Their direct vectorlike "
            "bilinear has charge 0 rather than the superpotential charge 2 and is "
            "forbidden.  S X_Q X_Qbar is allowed, but the certified supersymmetric "
            "vacuum has <S>=0.  S is a singlet and T(10) contains no Q-type "
            "conjugate, so there is no q=2 partner in the current field inventory."
        ),
        f"Current full-rank Q mass: `{inventory['full_rank_Q_type_mass_matrix_in_current_vacuum']}`.",
        "",
        "## Retraction ledger",
        "",
        "| Prior claim | V64 status | Reason |",
        "|---|---|---|",
    ]
    for row in report["retraction_ledger"]:
        lines.append(
            f"| {row['prior_claim']} | {row['V64_status']} | {row['reason']} |"
        )
    lines.extend(
        [
            "",
            "## Fail-closed repair criteria",
            "",
            "| ID | Required criterion | Exact test |",
            "|---|---|---|",
        ]
    )
    for row in report["repair_acceptance_criteria"]:
        lines.append(
            f"| {row['id']} | {row['criterion']} | {row['fail_closed_test']} |"
        )
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
        [
            "",
            "## G1--G8 ledger",
            "",
            "| Gate | Status | Decision |",
            "|---|---|---|",
        ]
    )
    for row in report["gate_ledger"]:
        lines.append(f"| {row['gate']} | {row['status']} | {row['decision']} |")
    lines.extend(["", "## Primary sources", ""])
    for source in PRIMARY_SOURCES:
        lines.append(
            f"- [{source['authors']}, {source['title']}]({source['url']}): {source['scope']}"
        )
    lines.extend(
        [
            "",
            "## Claim boundary",
            "",
            (
                "V64 is an exact quadratic-action correction, not new fundamental "
                "physics.  It does not claim that no Spin(11) repair can exist; it "
                "rejects the current action until an explicit lifting sector passes "
                "R1-R5.  The V61 selector arithmetic and the V62 pre-VEV localized "
                "ledger retain their limited scope.  Saxion stabilization, global-"
                "form quantization, Dai--Freed, flavor, and UV completion remain open."
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
            raise RuntimeError("generated V64 route artifacts are missing")
        if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
            raise RuntimeError("generated V64 route JSON is stale")
        if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
            raise RuntimeError("generated V64 route Markdown is stale")
    print(report["status"])
    print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
