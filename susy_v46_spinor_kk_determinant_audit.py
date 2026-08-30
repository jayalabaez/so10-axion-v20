#!/usr/bin/env python3
"""V46 KK-spectrum audit for the two V45 conjugate bulk-spinor pairs.

The calculation is deliberately formulated as an interval self-adjoint
extension.  A delta-function coefficient at an orbifold endpoint is not, by
itself, a regulator-independent number.  ``b`` below is the *renormalized
boundary-extension parameter* obtained after choosing a one-sided interval
trace (or an equivalent resolved-brane prescription).  In the explicit
one-sided convention used here, b = |lambda <Theta>|.

For each Spin(10) pair there is an H=(+,+) Pati--Salam half and an
H=(-,+) half.  The source wall is y=L and every H is even there.  The two
exact characteristic functions derived below retain the complete KK tower,
whereas the overlap mass is only the projected zero-mode result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Callable, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V46_SPINOR_KK_DETERMINANT_AUDIT.json"
MD_PATH = ROOT / "SUSY_V46_SPINOR_KK_DETERMINANT_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v46_spinor_kk_determinant_audit.py"

STATUS = (
    "V46_SELF_ADJOINT_KK_CHARACTERISTICS_DERIVED__"
    "FINITE_NONZERO_FULL_RANK_BOUNDARY_EXTENSION_LIFTS_ALL_ZERO_MODES__"
    "NO_TACHYONS_IN_THE_SUPERSYMMETRIC_DOMAIN__"
    "PROJECTED_RANK_AND_FULL_TOWER_DETERMINANTS_SEPARATED__"
    "BARE_DELTA_TO_EXTENSION_MATCHING_AND_GLOBAL_GATES_OPEN"
)

V45_INPUTS = (
    ROOT / "SUSY_V45_S0_GROUP_ZERO_MODE_AUDIT.json",
    ROOT / "SUSY_V45_RECONCILED_BULK_SPINOR_AUDIT.json",
)

PAIR_SPECS = (
    {
        "name": "left_pair",
        "hypers": ("16_+3", "bar16_-12"),
        "theta": "ThetaPlus_+9",
        "bare_coefficient": "mu_L=lambda_L<ThetaPlus>",
        "extension_parameter": "b_L=|B_R(mu_L)|",
        "selected_PS_halves": ("LF=(4,2,1)_+3", "LA=(bar4,2,1)_-12"),
        "unselected_PS_halves": ("(bar4,1,2)_+3", "(4,1,2)_-12"),
        "intrinsic_parities": ((1, 1), (1, 1)),
    },
    {
        "name": "right_pair",
        "hypers": ("16_-3", "bar16_+12"),
        "theta": "ThetaMinus_-9",
        "bare_coefficient": "mu_R=lambda_R<ThetaMinus>",
        "extension_parameter": "b_R=|B_R(mu_R)|",
        "selected_PS_halves": ("RA=(bar4,1,2)_-3", "RF=(4,1,2)_+12"),
        "unselected_PS_halves": ("(4,2,1)_-3", "(bar4,2,1)_+12"),
        "intrinsic_parities": ((-1, 1), (-1, 1)),
    },
)

PRIMARY_SOURCES = (
    {
        "url": "https://arxiv.org/abs/hep-th/0106256",
        "citation": "Marti and Pomarol, Phys. Rev. D64 (2001) 105025",
        "use": "5D hypermultiplets as two 4D N=1 chirals and the first-order superfield bulk operator",
    },
    {
        "url": "https://arxiv.org/abs/hep-ph/0112230",
        "citation": "Hebecker, Nucl. Phys. B632 (2002) 101",
        "use": "5D superspace on an orbifold and local brane operators",
    },
    {
        "url": "https://arxiv.org/abs/hep-ph/0603086",
        "citation": "Alciati et al., JHEP 07 (2006) 061",
        "use": "the SO(10) interval L=pi R/2, parity spectra, and boundary-mass shifts of KK conditions",
    },
    {
        "url": "https://arxiv.org/abs/1408.1852",
        "citation": "Barcelo, Mitra and Moreau, Eur. Phys. J. C75 (2015) 527",
        "use": "non-commuting brane-width and infinite-KK limits; a bare delta coupling needs a declared prescription",
    },
    {
        "url": "https://arxiv.org/abs/1703.07329",
        "citation": "Falco, Fedorenko and Gruzberg, J. Phys. A50 (2017) 485201",
        "use": "matrix functional determinants with removed zero modes in the Gel'fand--Yaglom framework",
    },
)


def _sinc_kernel(q: float, length: float) -> float:
    """Return sin(sqrt(q)L)/sqrt(q), analytically continued for q<0."""

    scale = max(1.0, abs(q) * length * length)
    if abs(q) * length * length < 1.0e-12 * scale:
        # L - q L^3/6 + q^2 L^5/120 is smooth through q=0.
        return length * (
            1.0 - q * length * length / 6.0 + q * q * length**4 / 120.0
        )
    if q > 0.0:
        root = math.sqrt(q)
        return math.sin(root * length) / root
    root = math.sqrt(-q)
    return math.sinh(root * length) / root


def _cos_kernel(q: float, length: float) -> float:
    """Return cos(sqrt(q)L), analytically continued for q<0."""

    if abs(q) * length * length < 1.0e-12:
        return 1.0 - q * length * length / 2.0 + q * q * length**4 / 24.0
    if q > 0.0:
        return math.cos(math.sqrt(q) * length)
    return math.cosh(math.sqrt(-q) * length)


def s_function(z: float, bulk_mass: float, length: float) -> float:
    """S(z)=sin(sqrt(z-M^2)L)/sqrt(z-M^2), an entire function of z."""

    return _sinc_kernel(z - bulk_mass * bulk_mass, length)


def f_function(z: float, bulk_mass: float, length: float) -> float:
    """F(z)=cos(kL)-M S(z), the (+) initial-condition solution at y=L."""

    q = z - bulk_mass * bulk_mass
    return _cos_kernel(q, length) - bulk_mass * _sinc_kernel(q, length)


def g_function(z: float, bulk_mass: float, length: float) -> float:
    """G(z)=cos(kL)+M S(z), used for the (-,+) sector."""

    q = z - bulk_mass * bulk_mass
    return _cos_kernel(q, length) + bulk_mass * _sinc_kernel(q, length)


def d_plus_plus(
    z: float, bulk_mass_1: float, bulk_mass_2: float, length: float, b: float
) -> float:
    """Complete (++/++) characteristic determinant in z=m_4^2."""

    s1 = s_function(z, bulk_mass_1, length)
    s2 = s_function(z, bulk_mass_2, length)
    f1 = f_function(z, bulk_mass_1, length)
    f2 = f_function(z, bulk_mass_2, length)
    return z * s1 * s2 - b * b * f1 * f2


def d_minus_plus(
    z: float, bulk_mass_1: float, bulk_mass_2: float, length: float, b: float
) -> float:
    """Complete (-,+)/(-,+) characteristic determinant in z=m_4^2."""

    s1 = s_function(z, bulk_mass_1, length)
    s2 = s_function(z, bulk_mass_2, length)
    g1 = g_function(z, bulk_mass_1, length)
    g2 = g_function(z, bulk_mass_2, length)
    return g1 * g2 - z * b * b * s1 * s2


def zero_mode_norm_integral(bulk_mass: float, length: float) -> float:
    """Integral of exp(-2 M y) over the interval."""

    x = 2.0 * bulk_mass * length
    if abs(x) < 1.0e-10:
        return length * (1.0 - x / 2.0 + x * x / 6.0)
    return -math.expm1(-x) / (2.0 * bulk_mass)


def projected_mass_squared(
    bulk_mass_1: float, bulk_mass_2: float, length: float, b: float
) -> float:
    """Squared mass from projecting only onto the two unperturbed zero modes."""

    z1 = zero_mode_norm_integral(bulk_mass_1, length)
    z2 = zero_mode_norm_integral(bulk_mass_2, length)
    return b * b * math.exp(-2.0 * (bulk_mass_1 + bulk_mass_2) * length) / (z1 * z2)


def determinant_ratios(
    bulk_mass_1: float, bulk_mass_2: float, length: float, b: float
) -> dict[str, float]:
    """Canonical cross-domain zeta ratios with unit-normalized boundary rows.

    The ++ denominator has its single zero *Dirac singular value* removed.
    Multiplying both boundary equations by arbitrary constants would change a
    raw Evans determinant, so the rows (g+b sigma_1 f)/sqrt(1+b^2)=0 are used.
    """

    s10 = s_function(0.0, bulk_mass_1, length)
    s20 = s_function(0.0, bulk_mass_2, length)
    localization = math.exp(-(bulk_mass_1 + bulk_mass_2) * length)
    normalization = 1.0 + b * b
    selected = b * b * localization / (s10 * s20 * normalization)
    unselected = 1.0 / normalization
    return {
        "selected_vs_zero_removed": selected,
        "unselected_vs_b0": unselected,
        "one_component_full_pair": selected * unselected,
        "spin10_pair_power_8": (selected * unselected) ** 8,
    }


def flat_exact_spectra(length: float, b: float, levels: int = 3) -> dict[str, Any]:
    """Closed flat-bulk spectra for b>0."""

    if b <= 0.0:
        raise ValueError("flat_exact_spectra uses b>0")
    alpha = math.atan(b)
    beta = math.pi / 2.0 - alpha
    pp_a = [(n * math.pi + alpha) / length for n in range(levels)]
    pp_b = [((n + 1) * math.pi - alpha) / length for n in range(levels)]
    mp_a = [(n * math.pi + beta) / length for n in range(levels)]
    mp_b = [((n + 1) * math.pi - beta) / length for n in range(levels)]
    return {
        "alpha": alpha,
        "beta": beta,
        "plus_plus_branches": [pp_a, pp_b],
        "minus_plus_branches": [mp_a, mp_b],
        "lightest_plus_plus": alpha / length,
        "lightest_minus_plus": beta / length,
    }


def _bisect(function: Callable[[float], float], low: float, high: float) -> float:
    f_low = function(low)
    f_high = function(high)
    if f_low == 0.0:
        return low
    if f_high == 0.0:
        return high
    if f_low * f_high > 0.0:
        raise ValueError("bisection interval does not bracket a root")
    for _ in range(100):
        mid = (low + high) / 2.0
        f_mid = function(mid)
        if f_mid == 0.0 or high - low < 1.0e-13 * max(1.0, mid):
            return mid
        if f_low * f_mid < 0.0:
            high = mid
            f_high = f_mid
        else:
            low = mid
            f_low = f_mid
    return (low + high) / 2.0


def first_positive_mass(
    characteristic: Callable[[float], float], maximum_mass: float, steps: int = 40000
) -> float:
    """Find the first simple positive root of D(m^2) by scan and bisection."""

    previous_m = 0.0
    previous_value = characteristic(0.0)
    for step in range(1, steps + 1):
        mass = maximum_mass * step / steps
        value = characteristic(mass * mass)
        if value == 0.0:
            return mass
        if previous_value * value < 0.0:
            return _bisect(lambda trial: characteristic(trial * trial), previous_m, mass)
        previous_m = mass
        previous_value = value
    raise RuntimeError("no simple positive root found in scan window")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: Mapping[str, Any]) -> str:
    payload = dict(value)
    payload.pop("core_sha256", None)
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _round(value: float) -> float:
    return round(value, 14)


def build_report() -> dict[str, Any]:
    length = 1.0
    m1 = 0.7
    m2 = -0.4
    b = 0.3
    pp = lambda z: d_plus_plus(z, m1, m2, length, b)
    mp = lambda z: d_minus_plus(z, m1, m2, length, b)
    first_pp = first_positive_mass(pp, 8.0)
    first_mp = first_positive_mass(mp, 8.0)
    projected_sq = projected_mass_squared(m1, m2, length, b)
    det_ratios = determinant_ratios(m1, m2, length, b)
    flat = flat_exact_spectra(1.0, 0.3)

    negative_samples = []
    for kappa in (0.05, 0.2, 0.8, 2.0, 5.0):
        z = -kappa * kappa
        negative_samples.append(
            {
                "kappa": kappa,
                "D_plus_plus": _round(pp(z)),
                "D_minus_plus": _round(mp(z)),
            }
        )

    report: dict[str, Any] = {
        "schema": "susy-v46-spinor-kk-determinant-audit-v1",
        "status": STATUS,
        "scope": {
            "interval": "0<=y<=L with L=pi R/2; PS wall at y=0 and full-Spin(10) source wall at y=L",
            "retained_bulk_hypers": [
                "16_+3",
                "bar16_-12",
                "16_-3",
                "bar16_+12",
            ],
            "source_superpotentials": [
                "delta(y-L) lambda_L ThetaPlus HLF HLA",
                "delta(y-L) lambda_R ThetaMinus HRA HRF",
            ],
            "spin10_pairs": [dict(pair) for pair in PAIR_SPECS],
            "separate_Bplus_Bminus_hypers": False,
            "not_in_scope": [
                "126+bar126-induced mixing",
                "supersymmetry-breaking boundary scalar operators",
                "eta/global anomalies",
                "a UV derivation of the thin-brane matching map B_R",
            ],
        },
        "declared_boundary_prescription": {
            "fundamental_description": "self-adjoint interval boundary condition, not an unqualified orbifold delta distribution",
            "bulk_action": "int d2theta H_i^c (partial_y+M_i) H_i + h.c., with real odd kink mass M_i epsilon(y)",
            "interior_mass": "M_i is the signed constant value on 0<y<L",
            "first_order_equations": [
                "(partial_y+M_i) f_i = m g_i",
                "(-partial_y+M_i) g_i = m f_i",
            ],
            "source_boundary_condition": "g(L)+b sigma_1 f(L)=0 after rephasing b>=0",
            "normalized_boundary_rows": "[g+b sigma_1 f]/sqrt(1+b^2)=0",
            "one_sided_matching": "B_R(mu)=mu, so b=|lambda<Theta>|, only in the explicit one-sided interval convention",
            "regulator_warning": "a symmetric orbifold delta, shifted-brane regulator, or finite-width profile can change B_R and finite-b KK phases",
            "invariant_statement": "all formulas below are exact in b; a nonzero bare mu is sufficient only after proving B_R(mu) is finite and nonzero",
        },
        "bulk_basis": {
            "z": "m_4^2",
            "k_i_squared": "z-M_i^2",
            "S_i": "sin(k_i L)/k_i, entire in z with hyperbolic continuation",
            "F_i": "cos(k_i L)-M_i S_i",
            "G_i": "cos(k_i L)+M_i S_i",
            "zero_values": {
                "S_i_0": "sinh(M_i L)/M_i (continuous value L at M_i=0)",
                "F_i_0": "exp(-M_i L)",
                "G_i_0": "exp(+M_i L)",
            },
        },
        "exact_characteristics": {
            "selected_plus_plus": {
                "PS_boundary": "g_i(0)=0, equivalently (partial_y+M_i)f_i(0)=0",
                "basis_profile": "f_i(y)=A_i[cos(k_i y)-M_i sin(k_i y)/k_i]",
                "boundary_matrix": "[[-m S_1, b F_2],[b F_1,-m S_2]]",
                "D": "D_++(z)=z S_1 S_2-b^2 F_1 F_2",
                "zero_value": "D_++(0)=-b^2 exp[-(M_1+M_2)L]",
            },
            "unselected_minus_plus": {
                "PS_boundary": "f_i(0)=0",
                "basis_profile": "f_i(y)=A_i sin(k_i y)/k_i",
                "boundary_matrix_after_multiplying_rows_by_m": "[[G_1,m b S_2],[m b S_1,G_2]]",
                "D": "D_-+(z)=G_1 G_2-z b^2 S_1 S_2",
                "zero_value": "D_-+(0)=exp[+(M_1+M_2)L]",
            },
            "root_rule": "the nonnegative real zeros z=m_n^2, with multiplicity, are the full KK singular-value spectrum",
            "full_spin10_pair_factor": "[D_++(z) D_-+(z)]^8",
            "two_pair_factor": "product over a=L,R of [D_++,a(z) D_-+,a(z)]^8",
        },
        "zero_mode_and_tachyon_theorems": {
            "finite_nonzero_b": {
                "selected_zero_modes_remaining_per_pair": 0,
                "unselected_zero_modes_per_pair": 0,
                "proof": "D_++(0) is nonzero for b!=0 and finite real M_i,L; D_-+(0) is nonzero for every finite b",
            },
            "massless_exceptions": [
                "b=0: Theta VEV/coupling vanishes, or the regulator map B_R(mu) vanishes",
                "a multi-copy boundary matrix is rank deficient",
                "a parity error makes a purported source field Dirichlet so the local operator is zero",
                "b=infinity is a different self-adjoint endpoint: an unselected (-,+) mode becomes exactly massless",
                "new boundary degrees of freedom in a resolved-brane UV completion can add independent zero modes",
            ],
            "multi_copy_rank_rule": "for n_1+n_2 selected chiral zero modes coupled by a boundary matrix mu of rank r, finite nonzero boundary profiles leave n_1+n_2-2r chiral zero modes",
            "tachyon_result": "none for real M_i, finite L, and hermitian b sigma_1",
            "tachyon_proof": [
                "for z=-kappa^2, rho_i=sqrt(kappa^2+M_i^2)>|M_i|",
                "S_i=sinh(rho_i L)/rho_i>0 and F_i,G_i>0",
                "D_++=-kappa^2 S_1S_2-b^2F_1F_2<0 for b!=0",
                "D_-+=G_1G_2+kappa^2b^2S_1S_2>0",
            ],
            "outside_theorem": "non-hermitian boundary matching, wrong-sign boundary kinetic/scalar terms, or SUSY breaking require a new stability audit",
        },
        "regulated_determinants": {
            "same_domain_hadamard_products": {
                "b_nonzero_plus_plus": "P_++(z;b)=D_++(z;b)/D_++(0;b)=product_n(1-z/m_n^2)",
                "b_zero_plus_plus_zero_removed": "P'_++(z;0)=D_++(z;0)/[z partial_z D_++(0;0)]",
                "minus_plus": "P_-+(z;b)=D_-+(z;b)/D_-+(0;b)",
                "convergence": "genus-zero products converge because m_n^2 grows as n^2",
            },
            "canonical_cross_domain_zeta_ratios": {
                "boundary_row_convention": "divide each two-channel boundary determinant by 1+b^2",
                "selected": "det_zeta O_++,b / det'_zeta O_++,0 = b^2 exp[-(M_1+M_2)L]/[(1+b^2)S_1(0)S_2(0)]",
                "unselected": "det_zeta O_-+,b / det_zeta O_-+,0 = 1/(1+b^2)",
                "one_component_full_pair": "b^2 exp[-(M_1+M_2)L]/[(1+b^2)^2 S_1(0)S_2(0)]",
                "scheme_warning": "absolute determinants and cross-domain constants can be shifted by local boundary counterterms; zeros and same-domain P(z;b) are invariant",
            },
            "flat_hurwitz_zeta_check": {
                "alpha": "atan(b)",
                "selected_masses": "(n pi+alpha)/L and ((n+1)pi-alpha)/L",
                "unselected_masses": "(n pi+pi/2-alpha)/L and ((n+1)pi-pi/2+alpha)/L",
                "selected_ratio": "b^2/[L^2(1+b^2)]",
                "unselected_ratio": "1/(1+b^2)",
            },
        },
        "projected_4D_vs_full_KK": {
            "zero_profile": "f_i^0(y)=N_i exp(-M_i y)",
            "normalization": "N_i^-2=Z_i=(1-exp(-2M_iL))/(2M_i)=exp(-M_iL)S_i(0)",
            "projected_mass": "m_proj=b N_1N_2 exp[-(M_1+M_2)L]",
            "projected_mass_squared": "b^2 exp[-(M_1+M_2)L]/[S_1(0)S_2(0)]",
            "small_b_relation": "m_light^2=m_proj^2+O(b^4)",
            "not_exact_at_finite_b": True,
            "flat_example": "m_light,++=atan(b)/L, while m_proj=b/L",
            "strong_boundary_spectral_flow": "as b->infinity, m_light,-+^2=exp[(M_1+M_2)L]/[b^2 S_1(0)S_2(0)]+O(b^-4)",
            "rank_statement": "each nonzero b gives a rank-2 chiral mass block per PS multiplet pair; b_L,b_R nonzero give rank 4 in (LF,LA,RA,RF)",
            "full_tower_statement": "rank 4 does not prove a parametrically heavy spectrum; at very large b the unselected tower contains a parametrically light state",
        },
        "numerical_certificate": {
            "general_point": {
                "L": length,
                "M_1": m1,
                "M_2": m2,
                "b": b,
                "D_plus_plus_0": _round(pp(0.0)),
                "expected_D_plus_plus_0": _round(-b * b * math.exp(-(m1 + m2) * length)),
                "D_minus_plus_0": _round(mp(0.0)),
                "expected_D_minus_plus_0": _round(math.exp((m1 + m2) * length)),
                "first_plus_plus_mass": _round(first_pp),
                "first_minus_plus_mass": _round(first_mp),
                "projected_mass": _round(math.sqrt(projected_sq)),
                "canonical_determinant_ratios": {key: _round(value) for key, value in det_ratios.items()},
                "negative_z_sign_samples": negative_samples,
            },
            "flat_point": {
                "L": 1.0,
                "b": 0.3,
                "alpha": _round(flat["alpha"]),
                "lightest_plus_plus": _round(flat["lightest_plus_plus"]),
                "lightest_minus_plus": _round(flat["lightest_minus_plus"]),
                "D_at_first_plus_plus_root": _round(d_plus_plus(flat["lightest_plus_plus"] ** 2, 0.0, 0.0, 1.0, 0.3)),
                "D_at_first_minus_plus_root": _round(d_minus_plus(flat["lightest_minus_plus"] ** 2, 0.0, 0.0, 1.0, 0.3)),
            },
        },
        "V45_consequence": {
            "projected_exotic_rank_if_bL_bR_nonzero": 4,
            "exact_massless_KK_modes_if_bL_bR_finite_nonzero": 0,
            "selected_mass_subproblem": "closed only in the declared free-flat-bulk self-adjoint two-hyper system",
            "omitted_allowed_source_terms": [
                "barSigma HLF HRA",
                "Sigma HLA HRF",
            ],
            "operator_obligation": "include both allowed Sigma-spinor terms in one enlarged coupled transfer matrix, or forbid both with an exact selector, before S2 can close",
            "gates_promoted": [],
            "complete_theory": False,
            "remaining_kill_tests": [
                "derive B_R from a specified resolved source-wall UV action and compare regulator prescriptions",
                "include barSigma HLF HRA, Sigma HLA HRF, and all boundary kinetic operators in the KK matrix",
                "bound b_L and b_R away from both zero and the strong-coupling spectral-flow regime",
                "complete the eta/global anomaly and compact charge-lattice audit",
                "recompute thresholds and cross-wall Wilson coefficients with the shifted towers",
            ],
        },
        "primary_sources": [dict(source) for source in PRIMARY_SOURCES],
        "provenance": {
            "generator": Path(__file__).name,
            "tests": TEST_PATH.name,
            "V45_inputs_sha256": {
                path.name: sha256_file(path) if path.exists() else None for path in V45_INPUTS
            },
            "V45_files_modified": False,
        },
    }
    # Normalize tuples and other JSON-compatible containers before hashing so
    # the in-memory object is byte-for-byte comparable to the committed JSON.
    report = json.loads(json.dumps(report, ensure_ascii=True))
    report["core_sha256"] = canonical_sha(report)
    validate(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report["status"] != STATUS:
        raise RuntimeError("status drifted")
    if canonical_sha(report) != report["core_sha256"]:
        raise RuntimeError("stale core hash")
    theorem = report["zero_mode_and_tachyon_theorems"]
    if theorem["finite_nonzero_b"]["selected_zero_modes_remaining_per_pair"] != 0:
        raise RuntimeError("nonzero full-rank extension did not lift selected zero modes")
    if theorem["tachyon_result"] != "none for real M_i, finite L, and hermitian b sigma_1":
        raise RuntimeError("tachyon verdict drifted")
    if report["V45_consequence"]["gates_promoted"]:
        raise RuntimeError("this subaudit cannot promote a G gate")
    point = report["numerical_certificate"]["general_point"]
    if abs(point["D_plus_plus_0"] - point["expected_D_plus_plus_0"]) > 1.0e-12:
        raise RuntimeError("D++ zero-value identity failed")
    if abs(point["D_minus_plus_0"] - point["expected_D_minus_plus_0"]) > 1.0e-12:
        raise RuntimeError("D-+ zero-value identity failed")
    for row in point["negative_z_sign_samples"]:
        if not row["D_plus_plus"] < 0.0 or not row["D_minus_plus"] > 0.0:
            raise RuntimeError("tachyon sign certificate failed")


def render_markdown(data: Mapping[str, Any]) -> str:
    point = data["numerical_certificate"]["general_point"]
    flat = data["numerical_certificate"]["flat_point"]
    hashes = data["provenance"]["V45_inputs_sha256"]
    return f"""# V46 bulk-spinor KK determinant audit

Status: `{data['status']}`

## Verdict

For each of the two V45 conjugate Spin(10) hypermultiplet pairs, a **finite,
nonzero, full-rank self-adjoint source-wall mixing parameter** removes every
exact KK zero mode.  There is no tachyonic root for real odd bulk masses and a
Hermitian supersymmetric boundary condition.  This closes the idealized
two-hyper KK mass subproblem, not a G gate and not the complete 5D theory.

The qualification about the boundary parameter is essential.  The bare symbol
`mu=lambda<Theta>` multiplying an endpoint delta function does not define a
unique spectrum until the delta convention or resolved-brane regulator is
specified.  This audit chooses the one-sided interval prescription and calls
the resulting renormalized extension parameter `b>=0`; in that convention
`b=|mu|`.  All exact equations below are equations in `b`.  Other prescriptions
can change the map `b=|B_R(mu)|` and hence finite-coupling KK phases.

## Retained V45 pairs and parities

The source wall is `y=L`, the PS wall is `y=0`, and `L=pi R/2`.

- `ThetaPlus 16_+3 bar16_-12` pairs `LF=(4,2,1)_+3` with
  `LA=(bar4,2,1)_-12`.
- `ThetaMinus 16_-3 bar16_+12` pairs `RA=(bar4,1,2)_-3` with
  `RF=(4,1,2)_+12`.

For either Spin(10) pair, the selected PS halves have `H=(+,+)` and the other
eight components have `H=(-,+)`.  The conjugate chiral `Hc` always has the
opposite parities.  Because both `H` fields are even at the full-Spin(10) wall,
the source superpotential pairs the complete representations.  Per conjugate
Spin(10) pair the full characteristic factor is

`[D_++(z) D_-+(z)]^8`, with `z=m_4^2`.

## Declared self-adjoint boundary problem

On `0<y<L`, use the Marti--Pomarol hypermultiplet convention

`int d2theta H_i^c (partial_y+M_i) H_i + h.c.`

with real odd kink mass `M_i epsilon(y)`.  The mode equations are

`(partial_y+M_i)f_i=m g_i`,  `(-partial_y+M_i)g_i=m f_i`.

After rephasing the holomorphic mass, the source boundary condition is

`g(L)+b sigma_1 f(L)=0`,  `b>=0`.

It is self-adjoint because `b sigma_1` is Hermitian.  For cross-boundary
determinant comparisons the two boundary rows are normalized by
`sqrt(1+b^2)`; otherwise an arbitrary rescaling of a boundary equation would
spuriously rescale the functional determinant.

Define the entire functions

`S_i(z)=sin(k_i L)/k_i`,  `F_i(z)=cos(k_i L)-M_i S_i(z)`,
`G_i(z)=cos(k_i L)+M_i S_i(z)`,  `k_i^2=z-M_i^2`.

For imaginary `k_i`, the trigonometric functions are analytically continued to
hyperbolic functions.  At zero,

`S_i(0)=sinh(M_i L)/M_i`, `F_i(0)=exp(-M_i L)`, and
`G_i(0)=exp(+M_i L)`.

## Exact KK eigenvalue conditions

For the selected `(+,+)` halves, `g_i(0)=0`.  The source-wall coefficient
matrix is

`[[-m S_1, b F_2], [b F_1, -m S_2]]`,

so the exact full-tower condition is

`D_++(z) = z S_1(z)S_2(z) - b^2 F_1(z)F_2(z) = 0`.

For the unselected `(-,+)` halves, `f_i(0)=0`.  Multiplying the two source rows
by `m` gives

`[[G_1, m b S_2], [m b S_1, G_2]]`,

and therefore

`D_-+(z) = G_1(z)G_2(z) - z b^2 S_1(z)S_2(z) = 0`.

These are entire in `z`; no division by `m`, `k_i`, or a trigonometric
function is used in the root test, so threshold roots are not lost.

`D` counts nonnegative Dirac/Takagi singular masses.  At `b=0`, the two
selected chiral zero modes of one conjugate PS pair make one zero singular mass
per gauge component, so `D_++` has one factor of `z`; the determinant of the
signed `2x2` chiral mass matrix contains the corresponding square.

For `M_1=M_2=0`, writing `alpha=atan(b)`, the selected masses are

`(n pi+alpha)/L` and `((n+1)pi-alpha)/L`,

while the unselected masses are

`(n pi+pi/2-alpha)/L` and `((n+1)pi-pi/2+alpha)/L`.

## Zero modes, tachyons, and strong-boundary spectral flow

At `z=0`,

`D_++(0)=-b^2 exp[-(M_1+M_2)L]`,

`D_-+(0)= exp[+(M_1+M_2)L]`.

Thus every finite `b!=0` removes both selected chiral zero modes (the one
vectorlike singular pair) and cannot create an unselected zero mode.  More
generally, if `n_1+n_2` selected chirals are coupled by a boundary matrix of
rank `r`, the exact residual chiral nullity is `n_1+n_2-2r`, since finite kink
profiles are nonzero at the source.  The exceptions are `b=0`, deficient flavor
rank, a parity/locality mistake, extra boundary fields, or the distinct endpoint
`b=infinity`.  A nonzero *bare* `mu` is not by itself a proof unless the chosen
UV prescription establishes `B_R(mu)!=0`.

There are no tachyons in the declared problem.  For `z=-kappa^2`, define
`rho_i=sqrt(kappa^2+M_i^2)>|M_i|`.  Then `S_i`, `F_i`, and `G_i` are positive,
so

`D_++=-kappa^2 S_1S_2-b^2F_1F_2<0`,

`D_-+=G_1G_2+kappa^2b^2S_1S_2>0`.

There is nevertheless an important non-uniform limit.  As `b->infinity`, the
lowest unselected state becomes light:

`m_light,-+^2 = exp[(M_1+M_2)L]/[b^2 S_1(0)S_2(0)] + O(b^-4)`.

At exactly infinite `b`, the endpoint is a different self-adjoint extension and
this mode is massless.  “Larger boundary mass” therefore does not mean that the
whole Spin(10) tower becomes monotonically heavier.

## Regulated determinants

The regulator-independent spectral objects at fixed `b` are the convergent
genus-zero Hadamard products

`P_++(z;b)=D_++(z;b)/D_++(0;b)` for `b!=0`,

`P'_++(z;0)=D_++(z;0)/[z partial_z D_++(0;0)]` with its zero removed, and

`P_-+(z;b)=D_-+(z;b)/D_-+(0;b)`.

Each equals `product_n(1-z/m_n^2)`.  For the declared unit-normalized boundary
rows, the cross-domain zeta ratios are

`det_zeta O_++,b / det'_zeta O_++,0`
`= b^2 exp[-(M_1+M_2)L]/[(1+b^2)S_1(0)S_2(0)]`,

`det_zeta O_-+,b / det_zeta O_-+,0 = 1/(1+b^2)`.

The `1/(1+b^2)` factors are required: a raw characteristic determinant has
high-Euclidean-momentum normalization `1+b^2`.  In the flat case a direct
Hurwitz-zeta product gives `b^2/[L^2(1+b^2)]` and `1/(1+b^2)`, respectively.
Absolute determinant constants remain adjustable by local boundary
counterterms; the roots and the same-domain products above do not.

## Projected 4D rank is not the full tower

The unperturbed normalized zero profile is

`f_i^0(y)=N_i exp(-M_i y)`,

`N_i^-2=(1-exp(-2M_iL))/(2M_i)=exp(-M_iL)S_i(0)`.

Projection gives

`m_proj=b N_1N_2 exp[-(M_1+M_2)L]`.

It is the leading small-`b` pole, `m_light^2=m_proj^2+O(b^4)`, not an exact
finite-`b` eigenvalue.  In the flat example, `m_proj=b/L` whereas the exact
selected light mass is `atan(b)/L`.  Both V45 boundary blocks nonzero therefore
give exact projected multiplet rank four and no exact finite-`b` KK zero, but
rank alone neither fixes the spectrum nor excludes the strong-`b` light
unselected state.

## Executable certificate

For `L={point['L']}`, `M_1={point['M_1']}`, `M_2={point['M_2']}`, `b={point['b']}`:

- `D_++(0)={point['D_plus_plus_0']}` and `D_-+(0)={point['D_minus_plus_0']}`;
- first selected mass `{point['first_plus_plus_mass']}`;
- first unselected mass `{point['first_minus_plus_mass']}`;
- projected mass `{point['projected_mass']}`.

At the flat check point `b={flat['b']}`, the exact lowest masses are
`{flat['lightest_plus_plus']}` and `{flat['lightest_minus_plus']}` and both
characteristics vanish to the recorded numerical precision.

Run:

`python susy_v46_spinor_kk_determinant_audit.py --check`

`python -m pytest -q test_susy_v46_spinor_kk_determinant_audit.py`

## Fail-closed boundary

No G gate is promoted.  The next mandatory step is to specify a resolved
source-wall UV action, derive `B_R(mu)` (including any induced boundary kinetic
terms), then redo this transfer matrix with the separately allowed source terms
`barSigma HLF HRA` and `Sigma HLA HRF`.  Those terms mix the nominal left and
right spinor pairs with source-even KK states, so the factorized determinant in
this audit is not the final source-wall determinant.  They must be included in
one enlarged coupled transfer matrix or forbidden by an exact selector before
S2 can close.  Threshold matching and cross-wall Wilson coefficients must use
the shifted full tower.

Primary references: [Marti--Pomarol](https://arxiv.org/abs/hep-th/0106256),
[Hebecker](https://arxiv.org/abs/hep-ph/0112230),
[Alciati et al.](https://arxiv.org/abs/hep-ph/0603086),
[Barcelo--Mitra--Moreau](https://arxiv.org/abs/1408.1852), and
[Falco--Fedorenko--Gruzberg](https://arxiv.org/abs/1703.07329).

V45 input SHA-256:

- `SUSY_V45_S0_GROUP_ZERO_MODE_AUDIT.json`: `{hashes['SUSY_V45_S0_GROUP_ZERO_MODE_AUDIT.json']}`
- `SUSY_V45_RECONCILED_BULK_SPINOR_AUDIT.json`: `{hashes['SUSY_V45_RECONCILED_BULK_SPINOR_AUDIT.json']}`

V46 core SHA-256: `{data['core_sha256']}`
"""


def write_artifacts(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def check_artifacts(report: Mapping[str, Any]) -> None:
    if not JSON_PATH.exists() or not MD_PATH.exists():
        raise RuntimeError("committed V46 artifacts are missing; run --write")
    stored = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    if stored != report:
        raise RuntimeError("committed JSON is stale; run --write")
    if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError("committed Markdown is stale; run --write")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write JSON and Markdown artifacts")
    parser.add_argument("--check", action="store_true", help="verify committed artifacts")
    parser.add_argument("--print-json", action="store_true", help="print generated JSON")
    args = parser.parse_args()

    report = build_report()
    if args.write:
        write_artifacts(report)
    if args.check:
        check_artifacts(report)
    if args.print_json or (not args.write and not args.check):
        print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
