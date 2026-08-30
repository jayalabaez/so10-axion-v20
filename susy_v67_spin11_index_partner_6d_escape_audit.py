#!/usr/bin/env python3
"""V67 fail-closed audit of the minimal index-changing Spin(11) repair.

V64 proved that a brane chiral field mixed only with a vectorlike KK tower
leaves one normalizable chiral zero mode.  V67 asks the next exact question:
what is the smallest field addition that changes the rectangular Fredholm
index, and can it live in the bound five-dimensional action?

The answer has two sides.  A q_R=2 conjugate partner adds the missing row and
removes the exact kernel.  However, the light singular value obeys a nontrivial
transcendental equation and can remain overlap-suppressed, and an isolated
Q-type partner cannot be localized on either wall of the current interval.
A six-dimensional G_3211 fixed point is a literature-backed escape geometry,
but it is a new action whose local anomaly polynomial and Spin(11) embedding
have not been constructed.  Consequently this audit advances G1/G4 without
closing a gate.
"""

from __future__ import annotations

import argparse
import copy
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V67_SPIN11_INDEX_PARTNER_6D_ESCAPE_AUDIT.json"
MD_PATH = ROOT / "SUSY_V67_SPIN11_INDEX_PARTNER_6D_ESCAPE_AUDIT.md"

INPUTS = {
    "v66_route": ROOT / "SUSY_V66_SPIN11_GM_OVERLAP_UNIFICATION_REPAIR_AUDIT.json",
    "v66_master": ROOT / "SUSY_V66_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
    "v65_route": ROOT / "SUSY_V65_SPIN11_ORPHAN_LIFTING_CLASSIFICATION_AUDIT.json",
    "v64_route": ROOT / "SUSY_V64_SPIN11_AB_TOWER_NULL_MODE_RETRACTION_AUDIT.json",
    "v62_route": ROOT / "SUSY_V62_SPIN11_LOCALIZED_Z4R_ANOMALY_GS_AUDIT.json",
    "v59_route": ROOT / "SUSY_V59_SPIN11_GAUGE_HIGGS_COMPLETION_AUDIT.json",
}

EXPECTED_CORES = {
    "v66_route": "07593002755158c96647701da7453b1942114424a5d3aff5318ebb891a2964ae",
    "v66_master": "499382834b9b63a23e10dbc16106dfb1db0f2bfeae17163862afd4f1467e9fa4",
    "v65_route": "b87696403fb46c4a6b044be8abe58dd5f82b63a83a58fff262a6f00bdd6914ae",
    "v64_route": "fe36b2f6f0e1786253827183bf7f8dc2dd9e15a94b7f036d5e9e6e0739717a1d",
    "v62_route": "f99b9e09bc6d528480e2ac09cf1f2dd9e2feb5383fda25b3aa3cac436758142e",
    "v59_route": "bf666eb5e4d57bff18b05182d7d6cc7874bbc26dd71897153faf9ee67a5f8c42",
}

STATUS = (
    "V67_SPIN11_INDEX_PARTNER_6D_ESCAPE__V64_NULL_MODE_REBOUND__"
    "Q_R2_CONJUGATE_PARTNER_CHANGES_INDEX__FINITE_KK_DETERMINANT_NONZERO__"
    "INHERITED_5D_OPERATOR_KERNEL_TRIVIAL__INHERITED_5D_LIGHT_ROOT_EQUATION_DERIVED__"
    "OVERLAP_CAN_STILL_SUPPRESS_MASS__Z4R_AND_MINIMAL_TREE_SCHUR_CHANNEL_PRESERVED__"
    "GLOBAL_MIXED_R_ANOMALY_CANCELS_REP_BY_REP__FORMAL_V62_5D_GS_DIAGNOSTIC_SU2_RESIDUE_2__"
    "NO_Q_ONLY_FIELD_ON_EXISTING_5D_WALLS__5D_SPLIT_BULK_UNCLASSIFIED__"
    "6D_G3211_FIXED_POINT_LOCAL_CANDIDATE__"
    "NEW_ACTION_NOT_CONSTRUCTED__G1_TO_G8_OPEN_ZERO_PROMOTIONS"
)

PRIMARY_SOURCES = [
    {
        "id": "DIENES_DUDAS_GHERGHETTA_1999",
        "title": "Light Neutrinos without Heavy Mass Scales: A Higher-Dimensional Seesaw Mechanism",
        "arxiv": "hep-ph/9811428",
        "url": "https://arxiv.org/abs/hep-ph/9811428",
        "scope": "Provides a specific KK-neutrino/Scherk-Schwarz example with an exact normalized massless eigenstate for its structured universal mixing; it is an analogy, not a theorem for arbitrary towers.",
    },
    {
        "id": "HALL_NOMURA_OKUI_SMITH_2002",
        "title": "SO(10) Unified Theories in Six Dimensions",
        "arxiv": "hep-ph/0108071",
        "url": "https://arxiv.org/abs/hep-ph/0108071",
        "scope": "Two extra dimensions permit intersecting GUT projections and a G3211 fixed point on which incomplete SM multiplets may live.",
    },
    {
        "id": "CSAKI_GROJEAN_HUBISZ_SHIRMAN_TERNING_2004",
        "title": "Fermions on an interval: quark and lepton masses without a Higgs",
        "arxiv": "hep-ph/0310355",
        "url": "https://arxiv.org/abs/hep-ph/0310355",
        "scope": "Derives interval fermion boundary conditions and shows how boundary fermions and localized mass or mixing terms alter them.",
    },
    {
        "id": "ARKANI_HAMED_COHEN_GEORGI_2001",
        "title": "Anomalies on orbifolds",
        "arxiv": "hep-th/0103135",
        "url": "https://arxiv.org/abs/hep-th/0103135",
        "scope": "Shows fixed-plane localization for an S1/Z2 anomaly and, for that setup, that anomaly-free four-dimensional zero modes suffice for cancellation.",
    },
    {
        "id": "VON_GERSDORFF_QUIROS_2003",
        "title": "Localized anomalies in orbifold gauge theories",
        "arxiv": "hep-th/0305024",
        "url": "https://arxiv.org/abs/hep-th/0305024",
        "scope": "Treats localized anomalies and Green-Schwarz cancellation in general five- and six-dimensional orbifold gauge theories, where integrated cancellation need not settle the fixed-locus ledger.",
    },
    {
        "id": "GARCIA_ETXEBARRIA_MONTERO_2019",
        "title": "Dai-Freed anomalies in particle physics",
        "arxiv": "1808.00009",
        "url": "https://arxiv.org/abs/1808.00009",
        "scope": "Uses the Dai-Freed framework to refine perturbative anomaly-cancellation conditions and derive possible extra fermion-spectrum constraints.",
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


def determinant(matrix: Sequence[Sequence[Fraction]]) -> Fraction:
    work = [list(row) for row in matrix]
    n = len(work)
    if any(len(row) != n for row in work):
        raise ValueError("determinant requires a square matrix")
    sign = 1
    out = Fraction(1)
    for col in range(n):
        pivot = next((row for row in range(col, n) if work[row][col]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != col:
            work[col], work[pivot] = work[pivot], work[col]
            sign *= -1
        value = work[col][col]
        out *= value
        for j in range(col, n):
            work[col][j] /= value
        for row in range(col + 1, n):
            ratio = work[row][col]
            if ratio:
                for j in range(col, n):
                    work[row][j] -= ratio * work[col][j]
    return sign * out


def augmented_matrix(
    kk: Sequence[Fraction], mixing: Fraction, partner_mass: Fraction
) -> list[list[Fraction]]:
    n = len(kk)
    rows: list[list[Fraction]] = []
    for i, value in enumerate(kk):
        row = [Fraction(0)] * (n + 1)
        row[i] = value
        row[-1] = mixing
        rows.append(row)
    rows.append([Fraction(0)] * n + [partner_mass])
    return rows


def light_root(alpha2: float, ml_partner: float) -> float:
    """Solve the inherited-5D secular equation below its first KK pole.

    For zero mixing there is a below-pole secular root only when ``ML<pi/2``;
    above that value the lowest singular state is the unmixed first KK mode.
    Positive mixing gives a unique mathematical root below the pole, but a
    root closer to the pole than binary64 can resolve is rejected rather than
    returned with a false residual.
    """

    if (
        not math.isfinite(alpha2)
        or not math.isfinite(ml_partner)
        or alpha2 < 0.0
        or ml_partner <= 0.0
    ):
        raise ValueError("alpha2 and ML must be finite, with alpha2 nonnegative and ML positive")
    k0 = math.pi / 2.0
    if alpha2 == 0.0:
        if ml_partner < k0:
            return ml_partner
        raise ValueError(
            "alpha2=0 has no secular root below the first KK pole when ML>=pi/2"
        )
    lo, hi = 0.0, math.nextafter(k0, 0.0)

    def residual(x: float) -> float:
        factor = 1.0 + alpha2 * (math.tan(x) / x if x else 1.0)
        return x * x * factor - ml_partner * ml_partner

    if residual(lo) >= 0.0 or residual(hi) <= 0.0:
        raise ArithmeticError(
            "below-pole root is not bracketed at binary64 precision"
        )
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if residual(mid) > 0.0:
            hi = mid
        else:
            lo = mid
        if math.nextafter(lo, hi) == hi:
            break
    return (lo + hi) / 2.0


def finite_secular_root(
    kk: Sequence[float], mixing: float, partner_mass: float
) -> float:
    """Solve the finite-cutoff singular-value secular equation below k0."""

    if not kk or min(kk) <= 0.0 or mixing <= 0.0 or partner_mass <= 0.0:
        raise ValueError("positive KK masses, mixing and partner mass are required")
    lo, hi = 0.0, math.nextafter(min(kk), 0.0)

    def residual(x: float) -> float:
        tower = sum(1.0 / (value * value - x * x) for value in kk)
        return x * x * (1.0 + mixing * mixing * tower) - partner_mass * partner_mass

    if residual(lo) >= 0.0 or residual(hi) <= 0.0:
        raise ArithmeticError("finite secular root is not bracketed")
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if residual(mid) > 0.0:
            hi = mid
        else:
            lo = mid
        if math.nextafter(lo, hi) == hi:
            break
    return (lo + hi) / 2.0


def gram_matrix(matrix: Sequence[Sequence[float]]) -> list[list[float]]:
    """Return A^T A for a rectangular real matrix without external packages."""

    if not matrix or not matrix[0]:
        raise ValueError("matrix must be nonempty")
    ncols = len(matrix[0])
    if any(len(row) != ncols for row in matrix):
        raise ValueError("matrix rows must have one common length")
    return [
        [sum(row[i] * row[j] for row in matrix) for j in range(ncols)]
        for i in range(ncols)
    ]


def jacobi_eigenvalues(
    matrix: Sequence[Sequence[float]], *, tolerance: float = 1.0e-13
) -> list[float]:
    """Compute eigenvalues of a small real symmetric matrix by Jacobi rotations."""

    work = [list(row) for row in matrix]
    n = len(work)
    if n == 0 or any(len(row) != n for row in work):
        raise ValueError("Jacobi diagonalization requires a square matrix")
    for i in range(n):
        for j in range(i):
            if abs(work[i][j] - work[j][i]) > tolerance:
                raise ValueError("Jacobi diagonalization requires a symmetric matrix")

    for _ in range(max(1, 100 * n * n)):
        p, q = 0, 0
        offdiag = 0.0
        for i in range(n):
            for j in range(i + 1, n):
                if abs(work[i][j]) > offdiag:
                    p, q, offdiag = i, j, abs(work[i][j])
        if offdiag <= tolerance:
            return sorted(work[i][i] for i in range(n))

        apq = work[p][q]
        tau = (work[q][q] - work[p][p]) / (2.0 * apq)
        tangent = math.copysign(1.0, tau) / (
            abs(tau) + math.sqrt(1.0 + tau * tau)
        )
        cosine = 1.0 / math.sqrt(1.0 + tangent * tangent)
        sine = tangent * cosine
        app, aqq = work[p][p], work[q][q]
        work[p][p] = app - tangent * apq
        work[q][q] = aqq + tangent * apq
        work[p][q] = work[q][p] = 0.0
        for k in range(n):
            if k in (p, q):
                continue
            akp, akq = work[k][p], work[k][q]
            work[k][p] = work[p][k] = cosine * akp - sine * akq
            work[k][q] = work[q][k] = sine * akp + cosine * akq
    raise ArithmeticError("Jacobi diagonalization did not converge")


def smallest_singular_value(matrix: Sequence[Sequence[float]]) -> float:
    """Return the smallest singular value through an independent A^T A audit."""

    smallest = jacobi_eigenvalues(gram_matrix(matrix))[0]
    if smallest < -1.0e-10:
        raise ArithmeticError("Gram matrix acquired a negative eigenvalue")
    return math.sqrt(max(0.0, smallest))


def spectral_index_repair(v64: Mapping[str, Any]) -> dict[str, Any]:
    sample_rows = []
    for n in range(1, 9):
        kk = [Fraction(2 * i + 1, 2) for i in range(n)]
        mixing, mass = Fraction(3, 5), Fraction(7, 3)
        matrix = augmented_matrix(kk, mixing, mass)
        expected = mass
        for value in kk:
            expected *= value
        sample_rows.append(
            {
                "N": n,
                "determinant": str(determinant(matrix)),
                "expected_M_product_k": str(expected),
                "matches": determinant(matrix) == expected,
            }
        )

    roots = []
    # For alpha=0 the secular branch is m=M only while M<k0; above k0 the
    # lowest state is instead the unmixed first KK mode.  Positive alpha
    # drives a root below the first pole for every M, so those cases also
    # test the large-M limit without conflating the two branches.
    root_cases = [(0.0, 0.1), (0.0, 1.0)] + [
        (alpha2, ml_partner)
        for alpha2 in (1.0, 9.0, 100.0)
        for ml_partner in (0.1, 1.0, 10.0)
    ]
    for alpha2, ml_partner in root_cases:
        root = light_root(alpha2, ml_partner)
        residual = root * root * (
            1.0 + alpha2 * math.tan(root) / root
        ) - ml_partner * ml_partner
        roots.append(
            {
                "alpha_squared": alpha2,
                "M_times_L": ml_partner,
                "m_times_L": root,
                "m_over_k0": root / (math.pi / 2.0),
                "equation_residual": residual,
            }
        )

    # This is independent of the closed-form tangent identity: diagonalize
    # A_N^T A_N directly and compare its lowest eigenvalue with the finite
    # rational-tower secular sum before taking N to infinity.
    finite_singular_checks = []
    alpha2_crosscheck = 1.0
    mixing_crosscheck = math.sqrt(2.0 * alpha2_crosscheck)
    mass_crosscheck = 1.3
    infinite_crosscheck = light_root(alpha2_crosscheck, mass_crosscheck)
    for n in (2, 4, 8, 12):
        kk_float = [(i + 0.5) * math.pi for i in range(n)]
        matrix_float: list[list[float]] = []
        for i, value in enumerate(kk_float):
            row = [0.0] * (n + 1)
            row[i] = value
            row[-1] = mixing_crosscheck
            matrix_float.append(row)
        matrix_float.append([0.0] * n + [mass_crosscheck])
        singular = smallest_singular_value(matrix_float)
        secular = finite_secular_root(
            kk_float, mixing_crosscheck, mass_crosscheck
        )
        finite_singular_checks.append(
            {
                "N": n,
                "smallest_singular_from_ATA_Jacobi": singular,
                "finite_sum_secular_root": secular,
                "absolute_difference": abs(singular - secular),
                "infinite_5D_tan_root": infinite_crosscheck,
                "finite_root_minus_infinite_root": secular - infinite_crosscheck,
                "matches_below_1e_9": abs(singular - secular) < 1.0e-9,
            }
        )

    finite_old = v64["finite_KK_mass_operator"]
    infinite_old = v64["infinite_normalizable_null_mode"]
    return {
        "bound_V64_operator": {
            "finite_shape": finite_old["per_complex_Q_direction"]["shape"],
            "right_kernel_dimension": 1,
            "normalizable_infinite_kernel": infinite_old[
                "norm_finite_for_every_finite_alpha"
            ],
        },
        "minimal_index_change": {
            "per_complex_Q_direction": "add one opposite-chirality q_R=2 partner row",
            "minimality_scope": "minimal rank/index addition to the displayed mass operator; no claim of a unique or minimal microscopic representation/locality completion",
            "old_operator": "A_N=[diag(k_n) | mu 1_N], shape N x (N+1)",
            "new_operator": "A'_N=[[diag(k_n),mu 1_N],[0...0,M]], shape (N+1) x (N+1)",
            "finite_determinant": "det A'_N = M product_n k_n",
            "inverse": "A'^(-1)=[[K^(-1),-K^(-1)mu/M],[0,1/M]]",
            "kernel_trivial_if": "M != 0 and k_0=pi/(2L)>0",
            "finite_exact_checks": sample_rows,
            "all_finite_checks_pass": all(row["matches"] for row in sample_rows),
        },
        "inherited_5D_infinite_tower": {
            "KK_masses": "k_n=(n+1/2)pi/L",
            "wall_mixing": "mu=sqrt(2/L) g5 v",
            "sum_identity": "sum_n mu^2/k_n^2 = g5^2 v^2 L = alpha^2",
            "bounded_inverse_estimate": "||A'^(-1)|| <= 2L/pi + sqrt(1+alpha^2)/|M|",
            "exact_zero_removed": True,
            "Dai_Freed_or_GS_changes_index": False,
            "scope": "exact only for the inherited one-dimensional V64 half-integer tower and its wall mixing",
        },
        "light_singular_value": {
            "exact_equation_for_inherited_5D_operator_below_first_KK_pole": "M^2=m^2[1+alpha^2 tan(mL)/(mL)], 0<mL<pi/2",
            "small_M_limit": "m approximately M/sqrt(1+alpha^2)",
            "large_M_limit_for_positive_alpha": "for alpha^2>0, m approaches k0=pi/(2L) from below",
            "alpha_zero_branch": {
                "below_pole": "m=M for ML<pi/2",
                "at_or_above_pole": "there is no secular root below k0; the lowest singular value is the unmixed k0 mode",
                "solver_behavior": "raises ValueError instead of returning the pole as a false root",
            },
            "trial_vector_upper_bound": "s_min <= |M|/sqrt(1+alpha^2)",
            "mass_floor_condition": "M^2 >= m_min^2[1+alpha^2 tan(m_min L)/(m_min L)], with m_min<pi/(2L)",
            "numerical_dimensionless_checks": roots,
            "all_root_residuals_below_1e_10": all(
                abs(row["equation_residual"]) < 1.0e-10 for row in roots
            ),
            "independent_finite_N_ATA_checks": finite_singular_checks,
            "all_independent_finite_N_checks_pass": all(
                row["matches_below_1e_9"] for row in finite_singular_checks
            ),
            "finite_roots_converge_from_above_in_sample": all(
                row["finite_root_minus_infinite_root"] > 0.0
                for row in finite_singular_checks
            )
            and all(
                finite_singular_checks[i + 1]["finite_sum_secular_root"]
                < finite_singular_checks[i]["finite_sum_secular_root"]
                for i in range(len(finite_singular_checks) - 1)
            ),
            "no_parametrically_light_mode_proved_without_parameters": False,
        },
        "six_dimensional_nonimport": {
            "status": "OPEN_NOT_THE_INHERITED_5D_TAN_EQUATION",
            "point_local_double_KK_asymptotic": "sum_(m,n) |mu_mn|^2/k_mn^2 grows logarithmically with the 6D KK cutoff for unsuppressed point-local overlaps",
            "consequence": "the 5D alpha identity, bounded-inverse estimate and tangent secular equation cannot be imported into D67",
            "allowed_resolution_paths": [
                "localize the complete orphan/partner mixing sector on one 5D fixed line and derive its endpoint spectrum",
                "or regulate and renormalize the genuine 2D lattice Green function and derive the cutoff-dependent singular root",
            ],
        },
        "corrected_conclusion": (
            "the partner changes the index and removes the exact null state in the inherited "
            "5D operator, but V64 R2 remains conditional until alpha, L, M, the cutoff and "
            "a physical colored-mass floor are supplied; a D67 spectrum must be rederived"
        ),
    }


def charge_anomaly_and_proton_audit(
    v64: Mapping[str, Any], v62: Mapping[str, Any]
) -> dict[str, Any]:
    fields = [
        {"field": "X_Q", "SM": "(3,2,+1/6)", "X": -1, "qR": 0, "fermion_r": -1},
        {"field": "P_Qbar", "SM": "(3bar,2,-1/6)", "X": 1, "qR": 2, "fermion_r": 1},
        {"field": "X_Qbar", "SM": "(3bar,2,-1/6)", "X": 1, "qR": 0, "fermion_r": -1},
        {"field": "P_Q", "SM": "(3,2,+1/6)", "X": -1, "qR": 2, "fermion_r": 1},
    ]
    operators = [
        {"operator": "M_Q X_Q P_Qbar", "qR": 2, "allowed_W": True, "role": "index-changing mass"},
        {"operator": "M_Qbar X_Qbar P_Q", "qR": 2, "allowed_W": True, "role": "index-changing mass"},
        {"operator": "X_Q F_i F_j", "qR": 2, "allowed_W": True, "role": "V65 baryon-safe decay source"},
        {"operator": "P_Qbar F_i F_j", "qR": 0, "allowed_W": False, "role": "conjugate source required for a tree Schur operator"},
        {"operator": "X_Qbar F_i F_j", "qR": 2, "allowed_W": True, "role": "V65 conjugate decay source after the required VEV insertion"},
        {"operator": "P_Q F_i F_j", "qR": 0, "allowed_W": False, "role": "second conjugate source"},
    ]
    orphan = v64["corrected_post_VEV_anomaly_ledger"]["surviving_sector"]
    partner_delta = {"Delta_A3": 2, "Delta_A2": 3}
    partner_abelian_rows = [
        (6, Fraction(-1, 6), Fraction(1), 1),
        (6, Fraction(1, 6), Fraction(-1), 1),
    ]
    partner_abelian = {
        "Delta_AYY_unnormalized": sum(
            r * dimension * hypercharge * hypercharge
            for dimension, hypercharge, _xcharge, r in partner_abelian_rows
        ),
        "Delta_AYY_GUT_normalized": Fraction(3, 5)
        * sum(
            r * dimension * hypercharge * hypercharge
            for dimension, hypercharge, _xcharge, r in partner_abelian_rows
        ),
        "Delta_AXX": sum(
            r * dimension * xcharge * xcharge
            for dimension, _hypercharge, xcharge, r in partner_abelian_rows
        ),
        "Delta_AYX": sum(
            r * dimension * hypercharge * xcharge
            for dimension, hypercharge, xcharge, r in partner_abelian_rows
        ),
        "Delta_Agravity": sum(
            r * dimension
            for dimension, _hypercharge, _xcharge, r in partner_abelian_rows
        ),
    }
    orphan_abelian = {key: -value for key, value in partner_abelian.items()}
    abelian_sum = {
        key: partner_abelian[key] + orphan_abelian[key]
        for key in partner_abelian
    }

    def rational_strings(values: Mapping[str, Fraction]) -> dict[str, str]:
        return {key: str(value) for key, value in values.items()}

    mssm = v64["corrected_post_VEV_anomaly_ledger"]["MSSM_only_ledger_from_V61"]
    couplings = v62["gs_congruence_system"]["selected_sector_s1"]
    c3_old = couplings["Spin10@y0"] + couplings["SO7@yL"]
    c2_old = couplings["Spin10@y0"] + couplings["SU2_L@yL"]
    a3, a2 = int(mssm["A3"]), int(mssm["A2"])
    residual_old = {"SU3": (c3_old + 2 * a3) % 4, "SU2": (c2_old + 2 * a2) % 4}
    delta_c = {"SU3": (-residual_old["SU3"]) % 4, "SU2": (-residual_old["SU2"]) % 4}
    residual_new = {
        "SU3": (c3_old + delta_c["SU3"] + 2 * a3) % 4,
        "SU2": (c2_old + delta_c["SU2"] + 2 * a2) % 4,
    }
    return {
        "field_inventory": fields,
        "mass_terms_preserve_Z4R_without_q2_VEV": all(
            row["qR"] == 2 and row["allowed_W"] for row in operators[:2]
        ),
        "F_flatness_boundary": "the Q-type fields have zero vacuum expectation value, so adding bilinear partner masses does not alter the certified singlet/rank F equations",
        "operator_ledger": operators,
        "tree_level_Schur_theorem": {
            "status": "PASS_MINIMAL_ONE_SIDED_HOLOMORPHIC_CHANNEL_ONLY",
            "general_form": "W=M X P + lambda X A + lambdatilde P B",
            "eliminated": "W_eff=-(lambda*lambdatilde/M) A B",
            "candidate_value": "lambdatilde=0 exactly by Z4R",
            "induced_four_matter_superpotential": "0",
            "scope": "only the displayed one-sided tree-level holomorphic partner exchange",
            "not_a_complete_selector_proof": "the complete G3211-local operator basis, Kähler/GM partner masses, KK gauge exchange and nonperturbative Z4R breaking remain open",
        },
        "global_mixed_R_anomaly": {
            "orphan_delta_from_V64": orphan["mixed_R_anomaly"],
            "qR2_partner_delta": partner_delta,
            "sum": {
                "Delta_A3": int(orphan["mixed_R_anomaly"]["Delta_A3"]) + partner_delta["Delta_A3"],
                "Delta_A2": int(orphan["mixed_R_anomaly"]["Delta_A2"]) + partner_delta["Delta_A2"],
            },
            "representation_by_representation_cancellation": True,
            "continuous_gauge_anomaly": "each q0-q2 mass pair is vectorlike under GSM x U1X",
            "integrated_abelian_and_gravity": {
                "convention": "sum fermion_R_charge times multiplicity times Y^2, X^2, YX, or 1; AYY_GUT=(3/5)AYY",
                "qR2_partner_delta": rational_strings(partner_abelian),
                "qR0_orphan_delta": rational_strings(orphan_abelian),
                "sum": rational_strings(abelian_sum),
                "all_cancel": all(value == 0 for value in abelian_sum.values()),
                "scope": "integrated arithmetic only; fixed-locus distribution and the full discrete/global anomaly problem remain open",
            },
            "IR_after_lift": {"A3": a3, "A2": a2},
        },
        "formal_V62_5D_integrated_GS_diagnostic": {
            "status": "FORMAL_5D_BOOKKEEPING_NOT_A_DERIVED_6D_LOCAL_COUPLING",
            "inherited_5D_effective_c": {"SU3": c3_old, "SU2": c2_old},
            "doubled_MSSM_anomaly": {"Ahat3": 2 * a3, "Ahat2": 2 * a2},
            "residue_if_V62_5D_convention_is_carried_mod4": residual_old,
            "formal_delta_c_diagnostic_mod4": delta_c,
            "residue_after_formal_diagnostic_mod4": residual_new,
            "formal_5D_congruence_arithmetic_closes": residual_new == {"SU3": 0, "SU2": 0},
            "not_a_6D_local_completion": (
                "U1Y, U1X, gravity, the distribution of the delocalized orphan determinant, "
                "6D levels and tensor/axion content, the 6D anomaly polynomial and Dai-Freed phase are not computed"
            ),
        },
    }


def geometry_escape_audit(v59: Mapping[str, Any], v65: Mapping[str, Any]) -> dict[str, Any]:
    walls = v59["gauge_and_zero_mode_audit"]["wall_groups"]
    b4 = next(
        row
        for row in v65["gut_scale_channel_classification"]["branches"]
        if row["id"] == "B4"
    )
    return {
        "current_5D_action": {
            "wall_groups": walls,
            "Q_only_qR2_local_field_allowed_at_y0": False,
            "Q_only_qR2_local_field_allowed_at_yL": False,
            "reason": (
                "an isolated GSM Q or Qbar is not a representation of Spin(10) at y0 or "
                "Spin(4)xSpin(7) at yL; a fundamental wall field must fill a local-group representation"
            ),
            "full_Spin10_partner_attempt": {
                "V65_channel": b4["channel"],
                "status": b4["status"],
                "obstruction": b4["exact_obstruction"],
                "scope_boundary": "this rejects the displayed full-16 implementation, not every split-bulk or higher-dimensional embedding",
            },
            "wall_local_Q_only_patch_exists": False,
            "split_bulk_5D_status": "UNCLASSIFIED__NO_EXHAUSTIVE_SPIN11_PARITY_OR_REPRESENTATION_NO_GO",
            "same_action_patch_status": "NO_WALL_LOCAL_PATCH_PROVED__SPLIT_BULK_UNRESOLVED",
        },
        "D67_6D_escape_candidate": {
            "status": "CANDIDATE_NEW_ACTION_NOT_CONSTRUCTED",
            "literature_geometry": "T2/(Z2 x Z2') SO(10) orbifold with a G3211 fixed point",
            "local_group": "SU3C x SU2L x U1Y x U1X",
            "why_partner_is_local_rep": "P_Q and P_Qbar are honest G3211 representations with X charges -1 and +1",
            "index_strategy": "place qR=2 conjugate partners on the reduced-symmetry locus and couple them to the nonzero orphan wavefunction",
            "alternative_strategy": "remove the brane-spinor rank sector entirely and break the GUT group geometrically, so the Goldstone orphan source never appears",
            "not_imported_from_literature": [
                "an explicit 6D Spin(11), rather than SO(10), parity representation",
                "a supersymmetric action retaining exactly the desired gauge-Higgs doublets",
                "the partner/orphan wavefunction overlap and physical singular mass",
                "complete 6D irreducible and reducible anomaly cancellation",
                "localized Z4R, U1Y, U1X, gravity and Dai-Freed cancellation",
                "KK thresholds, proton tensor, flavor, soft sector and compactification stabilization",
            ],
        },
        "forced_decision": (
            "the minimal rank/index repair cannot be a Q-only wall-local patch in the present 5D action; "
            "a 5D split-bulk realization remains unclassified, while D67 is one new six-dimensional research branch"
        ),
    }


def acceptance_matrix() -> list[dict[str, str]]:
    return [
        {"id": "R1", "status": "PASS_MATHEMATICAL", "requirement": "minimal rank/index addition squares the inherited 5D Q-sector mass operator with an explicit opposite chirality"},
        {"id": "R2", "status": "OPEN_PARAMETER_BOUND", "requirement": "light singular root above the physical colored-exotic floor below the cutoff"},
        {"id": "R3", "status": "PASS_MINIMAL_SCHUR_ARITHMETIC", "requirement": "preserve Z4R/R parity and null the displayed one-sided tree holomorphic Schur channel without a qR=2 VEV"},
        {"id": "R4", "status": "OPEN_6D_LOCAL", "requirement": "complete local/global anomaly and GS/Dai-Freed cancellation in the new geometry"},
        {"id": "R5", "status": "OPEN_FULL_PROTON", "requirement": "complete KK/Kähler proton matching and a lifetime, beyond the zero tree Schur term"},
        {"id": "R6", "status": "OPEN_ACTION", "requirement": "classify a 5D split-bulk realization or construct explicit Spin(11) 6D parities, fields, boundary action and UV regulator"},
    ]


def gate_ledger() -> list[dict[str, Any]]:
    decisions = {
        "G1": "OPEN: the inherited 5D operator index can be changed, but the 5D split-bulk route is unclassified and D67 is not a complete microscopic action.",
        "G2": "OPEN: no complete coefficient-level 4D Wilsonian action, flavor determinant or soft spectrum.",
        "G3": "OPEN: the 6D compactification, moduli/saxion stabilization and full Hessian are absent.",
        "G4": "OPEN WITH EXACT ADVANCE: the exact zero is removable by a qR=2 partner, but its physical mass and local embedding are unproved.",
        "G5": "OPEN: D67 can remove the colored relic only conditionally; decays, pole ordering and cosmology remain absent.",
        "G6": "OPEN: no inflation, reheating, defect or moduli history is constructed.",
        "G7": "OPEN WITH EXACT ADVANCE: the displayed one-sided partner exchange induces zero tree holomorphic four-matter term, but the full local operator basis, Kähler/KK and lifetime matching remain open.",
        "G8": "OPEN: no 6D UV regulator, full Dai-Freed phase or predictivity score exists.",
    }
    return [
        {
            "gate": f"G{i}",
            "status": "OPEN",
            "decision": decisions[f"G{i}"],
            "V67_closed": False,
        }
        for i in range(1, 9)
    ]


def source_manifest() -> dict[str, Any]:
    local = []
    for label, path in INPUTS.items():
        local.append(
            {
                "id": label,
                "path": str(path),
                "exists": path.is_file(),
                "sha256": sha256_file(path),
            }
        )
    return {"local_files": local, "primary_sources": copy.deepcopy(PRIMARY_SOURCES)}


def _body() -> dict[str, Any]:
    inputs = {
        label: load_bound(path, EXPECTED_CORES[label], label)
        for label, path in INPUTS.items()
    }
    spectral = spectral_index_repair(inputs["v64_route"])
    charge = charge_anomaly_and_proton_audit(
        inputs["v64_route"], inputs["v62_route"]
    )
    geometry = geometry_escape_audit(inputs["v59_route"], inputs["v65_route"])
    criteria = acceptance_matrix()
    gates = gate_ledger()
    checks = {
        "all_bound_cores_exact": all(
            inputs[label]["core_sha256"] == EXPECTED_CORES[label]
            for label in INPUTS
        ),
        "V66_current_action_rejected": inputs["v66_route"]["terminal_decision"]["current_bound_action_status"] == "REJECTED",
        "V64_exact_null_rebound": spectral["bound_V64_operator"]["normalizable_infinite_kernel"] is True,
        "finite_augmented_determinants_exact": spectral["minimal_index_change"]["all_finite_checks_pass"],
        "inherited_5D_infinite_exact_zero_removed": spectral["inherited_5D_infinite_tower"]["exact_zero_removed"],
        "light_root_not_overclaimed": spectral["light_singular_value"]["no_parametrically_light_mode_proved_without_parameters"] is False,
        "root_equations_numeric": spectral["light_singular_value"]["all_root_residuals_below_1e_10"],
        "finite_N_ATA_independent_crosscheck": spectral["light_singular_value"]["all_independent_finite_N_checks_pass"] and spectral["light_singular_value"]["finite_roots_converge_from_above_in_sample"],
        "D67_does_not_import_5D_tan_equation": spectral["six_dimensional_nonimport"]["status"] == "OPEN_NOT_THE_INHERITED_5D_TAN_EQUATION",
        "Z4R_mass_and_minimal_tree_Schur_arithmetic": charge["mass_terms_preserve_Z4R_without_q2_VEV"] and charge["tree_level_Schur_theorem"]["induced_four_matter_superpotential"] == "0",
        "global_orphan_partner_anomaly_cancels": charge["global_mixed_R_anomaly"]["sum"] == {"Delta_A3": 0, "Delta_A2": 0} and charge["global_mixed_R_anomaly"]["integrated_abelian_and_gravity"]["all_cancel"],
        "formal_V62_5D_GS_diagnostic_not_6D_completion": charge["formal_V62_5D_integrated_GS_diagnostic"]["formal_delta_c_diagnostic_mod4"] == {"SU3": 0, "SU2": 2} and charge["formal_V62_5D_integrated_GS_diagnostic"]["formal_5D_congruence_arithmetic_closes"],
        "current_5D_wall_local_embedding_rejected_only": geometry["current_5D_action"]["wall_local_Q_only_patch_exists"] is False and geometry["current_5D_action"]["split_bulk_5D_status"].startswith("UNCLASSIFIED"),
        "D67_new_action_only": geometry["D67_6D_escape_candidate"]["status"] == "CANDIDATE_NEW_ACTION_NOT_CONSTRUCTED",
        "acceptance_fail_closed": any(row["status"].startswith("OPEN") for row in criteria),
        "all_gates_open": all(row["status"] == "OPEN" and not row["V67_closed"] for row in gates),
    }
    return {
        "schema": "susy_v67_spin11_index_partner_6d_escape_audit/v1",
        "version": "V67",
        "date": "2026-08-30",
        "status": STATUS,
        "question": "Can an index-changing partner or a 6D redesign repair the V64 orphan and close G1/G4?",
        "classification": "EXACT_INHERITED_5D_INDEX_CHANGING_SPECTRAL_REPAIR__5D_SPLIT_BULK_UNCLASSIFIED__6D_LOCAL_EMBEDDING_CANDIDATE",
        "lineage": {
            "bound_input_cores": dict(EXPECTED_CORES),
            "relation": "new route after V66; no prior artifact is modified and no cross-route evidence is spliced",
        },
        "spectral_index_repair": spectral,
        "charge_anomaly_and_proton_audit": charge,
        "geometry_and_6D_escape": geometry,
        "acceptance_matrix": criteria,
        "gate_ledger": gates,
        "falsifiers": [
            {"id": "F1", "test": "M=0 or a missing partner component", "effect": "the exact V64 kernel returns"},
            {"id": "F2", "test": "the root equation places m below the physical colored bound", "effect": "reject the benchmark even though det is nonzero"},
            {"id": "F3", "test": "no G3211-local Spin(11) realization couples to the orphan wavefunction", "effect": "reject D67"},
            {"id": "F4", "test": "the complete 6D local/global anomaly ledger has an uncancelled class", "effect": "reject D67"},
            {"id": "F5", "test": "KK/Kähler exchange violates proton limits", "effect": "reject the proton sector"},
        ],
        "terminal_decision": {
            "current_bound_Spin11_action": "REJECTED",
            "D67_status": "CANDIDATE_NEW_ACTION_NOT_CONSTRUCTED",
            "exact_null_mode_removed_in_inherited_5D_candidate_operator": True,
            "physical_colored_mass_certified": False,
            "same_action_microscopic_completion_found": False,
            "V67_G1_closed": False,
            "V67_G4_closed": False,
            "closed_gates": [],
            "complete_theory": False,
            "WZ_term_for_bound_5D_V64_matching": "NONE_FORCED_IN_V64__D67_COUNTERTERMS_AND_GS_OPEN",
            "honest_outcome": (
                "V67 finds the minimal rank/index repair for the inherited 5D operator and one 6D local-geometry candidate, "
                "but 5D split-bulk locality, the D67 spectrum, local anomaly completion and the new action remain open; no gate is promoted"
            ),
        },
        "claim_boundary": {
            "new_physics_created": "qR=2 index-partner plus 6D G3211-local blueprint",
            "mathematical_result": "exact zero removed and light-root equation derived for the inherited 5D operator only",
            "not_claimed": ["accepted 6D action", "physical exotic mass", "proton lifetime", "UV completion", "gate closure"],
        },
        "source_manifest": source_manifest(),
        "integrity_checks": checks,
        "n_integrity_checks": len(checks),
        "n_failed_integrity_checks": sum(not value for value in checks.values()),
    }


def build_report() -> dict[str, Any]:
    report = _body()
    report["core_sha256"] = canonical_sha(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("V67 canonical core mismatch")
    expected = build_report()
    if canonical_bytes(report) != canonical_bytes(expected):
        raise RuntimeError("V67 recomputation mismatch")
    if report.get("n_failed_integrity_checks") != 0:
        raise RuntimeError("V67 integrity checks failed")
    terminal = report["terminal_decision"]
    if terminal["closed_gates"] or terminal["complete_theory"]:
        raise RuntimeError("V67 overclaimed gate closure")


def render_markdown(report: Mapping[str, Any]) -> str:
    spec = report["spectral_index_repair"]
    charge = report["charge_anomaly_and_proton_audit"]
    geom = report["geometry_and_6D_escape"]
    criteria = "\n".join(
        f"| {row['id']} | {row['status']} | {row['requirement']} |"
        for row in report["acceptance_matrix"]
    )
    gates = "\n".join(
        f"| {row['gate']} | {row['status']} | {row['decision']} |"
        for row in report["gate_ledger"]
    )
    sources = "\n".join(
        f"- [{row['title']}]({row['url']}): {row['scope']}"
        for row in report["source_manifest"]["primary_sources"]
    )
    return f"""# V67 Spin(11) index-partner and 6D escape audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Result

V67 finds the minimal rank/index repair of the displayed V64 operator, but
**does not close a gate**.  For every complex orphan direction, a conjugate
`qR=2` partner adds the missing row:

```text
A_N  = [diag(k_n) | mu 1_N]
A'_N = [[diag(k_n), mu 1_N], [0 ... 0, M]]
det A'_N = M product_n k_n
```

Thus the exact chiral kernel disappears for nonzero `M`.  For the inherited
one-dimensional V64 tower only, the infinite inverse is controlled because
`{spec['inherited_5D_infinite_tower']['sum_identity']}`.  This is minimal in
operator rank, not a claim of a unique or minimal microscopic embedding.

## Adversarial mass correction

A nonzero determinant is not a physical mass certificate.  In the inherited
5D operator, the light singular root satisfies exactly

```text
{spec['light_singular_value']['exact_equation_for_inherited_5D_operator_below_first_KK_pole']}
```

For small `M`, `{spec['light_singular_value']['small_M_limit']}`;
`{spec['light_singular_value']['large_M_limit_for_positive_alpha']}`.  Direct
finite-matrix `A^T A` diagonalization independently matches the truncated
secular equation in every stored sample.  Therefore alpha, L, M, the cutoff
and a phenomenological colored-mass floor are mandatory.

A genuine point-local 6D tower instead has a logarithmically cutoff-sensitive
double-KK sum.  The 5D tangent equation is **not** a D67 spectrum: D67 must
either localize this whole mixing sector on one fixed line or derive and
renormalize the two-dimensional lattice Green function.

## Z4R, anomalies and proton structure

The masses `X_Q P_Qbar` and `X_Qbar P_Q` have charge `0+2=2`; no charge-two
VEV is used.  Partner fermions have charge `+1` and cancel the orphan charge
`-1` representation by representation.  The net mixed shift is
`{charge['global_mixed_R_anomaly']['sum']}`.

For the displayed minimal channel, `W=M X P+lambda X A+lambdatilde P B` gives
`W_eff=-(lambda*lambdatilde/M)AB`; `lambdatilde=0` by Z4R, so this partner
exchange generates no holomorphic four-matter operator.  This is not a proof
of the complete G3211-local selector or a KK/Kähler proton-lifetime calculation.

The integrated `U1Y^2-Z4R`, `U1X^2-Z4R`, `U1Y-U1X-Z4R` and gravitational
partner shifts also cancel their orphan opposites exactly.  Their fixed-locus
distribution and the full discrete/global anomaly problem remain open.

As a bookkeeping diagnostic only, carrying the V62 5D convention to the MSSM
ledger leaves residue
`{charge['formal_V62_5D_integrated_GS_diagnostic']['residue_if_V62_5D_convention_is_carried_mod4']}`
and the formal compensating value is
`{charge['formal_V62_5D_integrated_GS_diagnostic']['formal_delta_c_diagnostic_mod4']}`.
This is not a derived 6D fixed-point coupling.  The 6D levels, tensor/axion
content, local determinant, anomaly polynomial and Dai-Freed phase remain open.

## Why this is new physics, not a patch

The current walls are `{geom['current_5D_action']['wall_groups']}`.  A Q-only
field is not a representation of either local group.  The full-Spin(10)
partner attempt is the specifically scoped V65 B4 failure.  A 5D split-bulk
hypermultiplet/parity realization has not been classified, so 6D is not proved
to be the only escape.  A literature-backed
`T2/(Z2 x Z2')` geometry has a `G3211` fixed point where incomplete SM
multiplets may live, but an explicit 6D Spin(11) action has not been built.

## Acceptance matrix

| ID | Status | Requirement |
|---|---|---|
{criteria}

## Established gate ledger

| Gate | Status | Decision |
|---|---|---|
{gates}

## Primary sources

{sources}

## Decision

The exact-zero obstruction is solved for the inherited 5D candidate operator
and its next physical equation is known.  The 5D split-bulk route remains
unclassified and D67 remains a candidate new action; G1-G8 stay OPEN.
"""


def write_outputs(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate(report)
    if args.check:
        if not JSON_PATH.is_file() or not MD_PATH.is_file():
            raise RuntimeError("V67 generated artifacts are missing")
        if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
            raise RuntimeError("V67 JSON artifact is stale")
        if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
            raise RuntimeError("V67 markdown artifact is stale")
    else:
        write_outputs(report)
    print(report["status"])
    print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
