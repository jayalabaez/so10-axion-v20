#!/usr/bin/env python3
"""V49 fixed-profile, strictly 4D source regulator audit.

V48's exact H/Hc square-collar transfer is retained.  The tentative idea of
promoting every V47 source chiral to an independent y-dependent collar field
is not retained: a Kähler normal derivative alone is not a spectral mass
operator.  Instead, the V47 source multiplets remain strictly four
dimensional at y=L.  Their interaction with the resolved H/Hc collar is
smeared by a fixed normalized kernel and made gauge covariant with the unique
short normal Wilson line.  Therefore no new source KK tower exists.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import susy_v47_four_spinor_mixed_kk_audit as v47
import susy_v48_resolved_source_wall_audit as v48


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V49_FIXED_PROFILE_SOURCE_REGULATOR_AUDIT.json"
MD_PATH = ROOT / "SUSY_V49_FIXED_PROFILE_SOURCE_REGULATOR_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v49_fixed_profile_source_regulator_audit.py"

STATUS = (
    "V49_STRICTLY_4D_SOURCE_MULTIPLETS_WITH_GAUGE_COVARIANT_FIXED_COLLAR_PROFILE_DEFINED__"
    "NO_SOURCE_KK_TOWER__EXACT_V48_TREE_PENCIL_RETAINED_AT_ZERO_COUNTERTERM_POINT__"
    "STRONG_COLLAR_HC_AND_ODD_PROFILE_TERMS_UNSUPPRESSED__"
    "GAUGE_COVARIANT_BILOCAL_FINITE_RESOLUTION_PRESCRIPTION_ONLY__"
    "FULL_G2_BOUNDARY_EFT_NOT_CLAIMED"
)

SOURCE_FIELDS = (
    "Phi_210",
    "Sigma_126",
    "barSigma_bar126",
    "S",
    "ThetaPlus",
    "ThetaMinus",
)

UPSTREAM_INPUTS = (
    ROOT / "SUSY_V47_SOURCE_COMPLETION_ROUTE_AUDIT.json",
    ROOT / "SUSY_V47_FOUR_SPINOR_MIXED_KK_AUDIT.json",
    ROOT / "SUSY_V48_RESOLVED_SOURCE_WALL_AUDIT.json",
)

PRIMARY_SOURCES = (
    {
        "url": "https://arxiv.org/abs/hep-th/0106256",
        "use": "5D hypermultiplets in manifest 4D N=1 superspace",
    },
    {
        "url": "https://arxiv.org/abs/hep-ph/0112230",
        "use": "gauge-covariant fifth-direction superspace operators and boundary interactions",
    },
    {
        "url": "https://arxiv.org/abs/1408.1852",
        "use": "fixed finite-width square profiles and the correct thin-wall order of limits",
    },
)


def normalized_square_profile(y: float, total_length: float, epsilon: float) -> float:
    """One-sided physical-interval profile for parity-even operators."""

    if epsilon <= 0.0 or epsilon >= total_length:
        raise ValueError("epsilon must lie strictly between zero and L")
    return 1.0 / epsilon if total_length - epsilon < y < total_length else 0.0


def doubled_orbifold_profile(signed_distance: float, epsilon: float) -> float:
    """Even unit-normalized profile on the endpoint's doubled cover."""

    if epsilon <= 0.0:
        raise ValueError("epsilon must be positive")
    return 1.0 / (2.0 * epsilon) if abs(signed_distance) < epsilon else 0.0


def square_profile_moment(epsilon: float, power: int, *, doubled_orbifold: bool = False) -> float:
    """Profile moments on the physical half or the even doubled cover."""

    if epsilon <= 0.0:
        raise ValueError("epsilon must be positive")
    if power < 0:
        raise ValueError("power must be nonnegative")
    if doubled_orbifold and power % 2:
        return 0.0
    return epsilon**power / (power + 1)


def smeared_near_endpoint_bilinears(
    epsilon: float,
    h0: complex,
    h2: complex,
    hc1: complex,
) -> dict[str, complex]:
    """Kinematic doubled-orbifold moments at a fixed input slope hc1.

    These moments do not determine physical strong-collar power counting:
    the exact V48 solution has hc1 proportional to 1/epsilon.  Use
    ``strong_collar_leading_bilinears`` for that dynamical scaling.
    """

    m0 = square_profile_moment(epsilon, 0, doubled_orbifold=True)
    m2 = square_profile_moment(epsilon, 2, doubled_orbifold=True)
    m4 = square_profile_moment(epsilon, 4, doubled_orbifold=True)
    return {
        "HH": h0 * h0 * m0 + 2.0 * h0 * h2 * m2 + h2 * h2 * m4,
        "H_Hc": 0.0j,
        "Hc_Hc": hc1 * hc1 * m2,
        "leading_HH": h0 * h0,
        "leading_H_Hc": 0.0j,
        "leading_Hc_Hc": hc1 * hc1 * epsilon * epsilon / 3.0,
    }


def odd_profile_mixed_bilinear(epsilon: float, h0: complex, hc1: complex) -> complex:
    """Kinematic average of rho_o H Hc at fixed hc1.

    Although H Hc is odd, rho_o is also odd, so their product is orbifold
    even.  In the exact strong collar hc1 is proportional to 1/epsilon, so
    this finite-profile normal-derivative counterterm is O(1).
    """

    if epsilon <= 0.0:
        raise ValueError("epsilon must be positive")
    return h0 * hc1 * epsilon / 3.0


def strong_collar_leading_bilinears(
    epsilon: float,
    h0: complex,
    source_eigenvalue: complex,
) -> dict[str, complex]:
    """Exact m=0 leading bilinears inside the V48 Lambda/epsilon wall.

    The collar equations give H(s)=h0 and
    Hc(s)=-(s/epsilon) source_eigenvalue*h0.  The inverse epsilon in this
    solution cancels the naive profile moments, so allowed Hc terms are not
    higher-order remainders.
    """

    if epsilon <= 0.0:
        raise ValueError("epsilon must be positive")
    hchc_even = (source_eigenvalue * h0) ** 2 / 3.0
    hhc_odd_sign = -(h0 * h0 * source_eigenvalue) / 2.0
    hhc_odd_linear = -(h0 * h0 * source_eigenvalue) / 3.0
    return {
        "Hc_Hc_even_profile": hchc_even,
        "H_Hc_odd_sign_profile": hhc_odd_sign,
        "H_Hc_odd_linear_profile": hhc_odd_linear,
    }


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(report: Mapping[str, Any]) -> str:
    payload = {key: value for key, value in report.items() if key != "core_sha256"}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _real_matrix(matrix: Sequence[Sequence[complex]], tolerance: float = 1.0e-12) -> list[list[float]]:
    result: list[list[float]] = []
    for row in matrix:
        converted: list[float] = []
        for value in row:
            item = complex(value)
            if abs(item.imag) > tolerance:
                raise ValueError("certificate matrix is not real")
            converted.append(float(item.real))
        result.append(converted)
    return result


def build_report() -> dict[str, Any]:
    length = 1.0
    epsilon = 0.05
    signed_mass = 0.37
    bulk_masses = (0.2, -0.4, 0.8, -0.1)
    source = v48.source_matrix(0.4, 0.6, 0.2, -0.15, su5_singlet=True)
    non_singlet = v48.source_matrix(0.4, 0.6, 0.0, 0.0, su5_singlet=False)
    wall = v48.wall_transfer(signed_mass, epsilon, source)
    boundary = v48.boundary_map(signed_mass, epsilon, source)
    resolved = v48.resolved_characteristic_matrix(
        signed_mass, bulk_masses, length, epsilon, source, v47.E_RIGHT
    )
    effective = v48.effective_characteristic_matrix(
        signed_mass, bulk_masses, length, epsilon, source, v47.E_RIGHT
    )
    factor_residual = v48.max_difference(resolved, v48.matrix_multiply(wall["D"], effective))
    moments = {str(power): square_profile_moment(epsilon, power) for power in range(5)}
    doubled_moments = {
        str(power): square_profile_moment(epsilon, power, doubled_orbifold=True)
        for power in range(5)
    }
    bilinears = smeared_near_endpoint_bilinears(epsilon, 1.2, -0.3, 0.7)
    odd_profile_mixed = odd_profile_mixed_bilinear(epsilon, 1.2, 0.7)
    strong_collar_bilinears = strong_collar_leading_bilinears(epsilon, 1.2, 0.4)
    zero_count = (
        8 * v47.zero_mode_nullity(non_singlet, v47.E_LEFT)
        + 7 * v47.zero_mode_nullity(non_singlet, v47.E_RIGHT)
        + v47.zero_mode_nullity(source, v47.E_RIGHT)
    )

    report: dict[str, Any] = {
        "schema_version": "susy-spin10-v49-fixed-profile-source-regulator-v1",
        "status": STATUS,
        "scope": {
            "question": "Can the V48 H/Hc collar be sourced by the dynamical V47 wall fields without inventing an uncontrolled source KK continuum?",
            "answer": "yes: keep the V47 fields strictly four-dimensional and smear only their gauge-covariant interaction kernel",
            "V48_repair": "the y-dependent source-field collar and its transverse-mass claim are superseded; the exact H/Hc square-collar transfer remains valid",
        },
        "strictly_4D_source_action": {
            "fields": list(SOURCE_FIELDS),
            "location": "four-dimensional N=1 source theory at y=L",
            "action": "integral d4x [integral d4theta K_V47(X,Xdagger,V(L)) + integral d2theta W_source,V47(X)+h.c.]",
            "normalization": "no y integration occurs in the source kinetic action; the V47 canonical normalization, dimension-one VEVs, F/D equations and 443-mode physical Hessian are unchanged",
            "no_source_KK_tower": "X_A depends on x and theta only, not y; rho_epsilon belongs solely to the interaction kernel",
            "source_spectrum": "exactly the already-audited V47 four-dimensional source spectrum; no transverse source label or source-wall KK determinant exists",
        },
        "gauge_covariant_fixed_smearing": {
            "profile": "on the doubled endpoint cover use the even rho_double(s)=1/(2epsilon) for |s|<epsilon, integral one; its quotient physical-half density for parity-even operators is rho_physical=1/epsilon on 0<s<epsilon, also integral one",
            "one_sided_normalization": "for every orbifold-even integrand F, integral_-epsilon^epsilon rho_double F = integral_0^epsilon rho_physical F; this is the convention used by the physical H/Hc transfer",
            "parallel_transporter": "U_R(L,y)=P exp[-integral_y^L Phi_R(y')dy']",
            "transported_bulk_chiral": "Hhat_R(y)=U_R(L,y) H_R(y)",
            "gauge_law": "U_R(L,y)->g_R(L)U_R(L,y)g_R(y)^(-1), hence Hhat_R(y)->g_R(L)Hhat_R(y)",
            "interaction": "integral_[L-epsilon,L] dy rho_epsilon [kappa_L ThetaPlus Hhat_LF Hhat_LA/Mstar + kappa_R ThetaMinus Hhat_RA Hhat_RF/Mstar + kappa_16 barSigma Hhat_LF Hhat_RA/Mstar + kappa_bar16 Sigma Hhat_LA Hhat_RF/Mstar]",
            "local_gauge_statement": "each transported bilinear and its source field transform at y=L, so every contraction is Spin(10)xU(1)F invariant",
            "axial_gauge_certificate": "on the simply connected collar choose the trivial supersymmetric Wilson-line background and Phi_5=0; then U=I and the H/Hc quadratic operator is exactly V48's square source Lambda/epsilon",
            "nonlocality_scope": "the shortest normal Wilson line is part of the declared finite-resolution kernel; it is not evidence for point-local five-dimensional UV completion",
        },
        "variation_and_quadratic_reduction": {
            "delta_source_fields": "delta W/dX_A equals the V47 source F-term plus the normalized integral of the corresponding transported H bilinear",
            "vacuum": "at H=0 the second term vanishes, so the exact V47 F-flat/D-flat source branch and Hessian remain unchanged",
            "delta_H": "variation gives rho_epsilon U_R(L,y)^T times the symmetric source mass acting on transported H",
            "delta_Wilson_line": "variations of U contain at least two H fields and one gauge fluctuation, hence are cubic and absent from the quadratic H/Hc spectral pencil about H=0",
            "axial_gauge_mode_equations": ["f'=m g", "g'=(Lambda/epsilon-m I)f"],
            "outer_domain": "g(L)=0",
        },
        "exact_finite_epsilon_boundary_pencil": {
            "definitions": {
                "delta": "m epsilon",
                "X": "delta(Lambda-delta I)",
                "D": "cosh(sqrt(X))",
                "Hfun": "sinh(sqrt(X))/sqrt(X)",
                "C": "(Lambda-delta I)Hfun",
                "U": "delta Hfun",
            },
            "wall_transfer": "T_wall=[[D,U],[C,D]]",
            "meromorphic_map": "B_epsilon(m)=D^(-1)C where D is invertible",
            "pole_free_characteristic": "K_res=(CF-mDS)E+(mCS+DG)O",
            "factorization": "K_res=D K_eff where D is invertible",
            "zero_energy": "B_epsilon(0)=Lambda exactly, so tau_L,tau_R nonzero leave zero exotic modes",
            "thin_wall": "after solving the full collar, epsilon->0 gives the V47 K(m)",
            "self_adjointness": "the V48 Hermitian Lambda, canonical H/Hc norm, g(L)=0 and J-unitary transfer proof apply unchanged",
        },
        "Hc_and_mixed_operator_power_counting": {
            "endpoint_parity": "on the doubled cover H is even and Hc is odd, but the exact strong wall has Hc slope proportional to Lambda/epsilon",
            "normalized_profile_moments": "integral rho_double s^(2n+1) ds=0 and integral rho_double s^(2n) ds=epsilon^(2n)/(2n+1)",
            "exact_m0_strong_collar": {
                "solution": "H(s)=h0, Hc(s)=-(s/epsilon)Lambda h0",
                "general_quadratic_generator": "d(f,g)/dy=[[-rho A^T,mI-rho Xi],[rho Lambda-mI,rho A]](f,g), up to the fixed orientation convention",
                "even_profile_H_Hc": "zero by oddness for rho_even",
                "even_profile_Hc_Hc": "(1/3) h0^T Lambda^T Xi Lambda h0 = O(1)",
                "odd_sign_profile_H_Hc": "-(1/2) h0^T A Lambda h0 = O(1)",
                "odd_linear_profile_H_Hc": "-(1/3) h0^T A Lambda h0 = O(1)",
            },
            "naive_smooth_profile_warning": "holding hc1 fixed while epsilon tends to zero gives apparent O(epsilon) and O(epsilon^2) suppression, but that assumption is inconsistent with the exact Lambda/epsilon wall, where hc1=-Lambda h0/epsilon",
            "candidate_matching_input": "the displayed V48 transfer is the zero-finite-part point for Hc-Hc and odd-profile H-Hc/O7/O8 coefficients; zero is not symmetry-enforced, the complete EFT must retain and renormalize them, and generic values change the wall generator already at O(1)",
            "radiative_statement": "orbifold parity kills only the even-profile H-Hc average; symmetry-respecting matching or loops may generate odd-profile and Hc-Hc coefficients, which cannot be assigned to the O(E^2/Lambda^2) remainder in the strong collar",
            "excluded_singular_scalings": "Hc-Hc coefficients growing as 1/epsilon^2 lie outside the declared O(1) Wilsonian domain and define a different singular regulator",
            "finite_epsilon_scope": "generic O(1) Hc-Hc or odd-profile coefficients modify the full finite-epsilon wall generator; the displayed exact V48 transfer is therefore not a stable complete-action pencil",
        },
        "counterterm_and_gate_scope": {
            "quadratic_H_sector_inputs": "independent H Kahler, normal-derivative, H-Hc and Hc-Hc finite counterterms are specified at the matching scale; the certificate point selects their finite parts to zero",
            "not_enumerated_here": [
                "U(1)F Fayet-Iliopoulos terms",
                "gauge and source-dependent gauge kinetic functions",
                "Pati-Salam boundary/bulk kinetic mixing",
                "all interacting higher-dimensional source operators",
            ],
            "G2_statement": "this closes the regulator microscopic-candidate condition only; G2 requires the independent complete boundary-EFT operator and Wilson-matching verdict",
            "G6_statement": "full KK root and threshold sums are G6 work, not a G2 regulator condition",
        },
        "numerical_certificate": {
            "parameters": {
                "L": length,
                "epsilon": epsilon,
                "Mstar": 1.0 / epsilon,
                "signed_mass": signed_mass,
                "bulk_masses": list(bulk_masses),
                "tau_L": 0.4,
                "tau_R": 0.6,
                "s_16": 0.2,
                "s_bar16": -0.15,
            },
            "profile_moments_n0_to_n4": moments,
            "doubled_orbifold_profile_moments_n0_to_n4": doubled_moments,
            "sample_smeared_bilinears": {key: float(complex(value).real) for key, value in bilinears.items()},
            "sample_odd_profile_H_Hc": float(complex(odd_profile_mixed).real),
            "sample_strong_collar_bilinears": {
                key: float(complex(value).real) for key, value in strong_collar_bilinears.items()
            },
            "Lambda": _real_matrix(source),
            "B_epsilon_at_sample_mass": _real_matrix(boundary),
            "wall_J_unitarity_residual": v48.j_unitarity_residual(wall["T"]),
            "K_res_minus_D_K_eff_residual": factor_residual,
            "total_exotic_chiral_zero_modes": zero_count,
            "source_field_count_with_y_dependence": 0,
            "source_KK_tower_present": False,
            "fixed_profile_integral": square_profile_moment(epsilon, 0),
        },
        "decision": {
            "strictly_4D_source_regulator_defined": True,
            "gauge_covariant_smearing_defined": True,
            "extra_source_KK_tower_absent": True,
            "explicit_finite_resolution_tree_prescription_defined": True,
            "exact_finite_epsilon_H_boundary_pencil_retained_only_at_zero_counterterm_point": True,
            "strong_collar_Hc_terms_unsuppressed": True,
            "odd_profile_normal_derivative_counterterm_required": True,
            "regulator_microscopic_candidate_condition_closed": False,
            "point_local_5D_regulator_defined": False,
            "point_local_5D_UV_completion_proved": False,
            "complete_boundary_EFT_basis_proved_here": False,
            "G2_closed_by_this_subaudit": False,
            "gates_promoted": [],
        },
        "primary_sources": list(PRIMARY_SOURCES),
        "provenance": {
            "upstream_sha256": {path.name: sha256_file(path) for path in UPSTREAM_INPUTS},
            "V45_to_V48_files_modified": False,
        },
    }
    report = json.loads(json.dumps(report, ensure_ascii=True))
    report["core_sha256"] = canonical_sha(report)
    validate(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report["status"] != STATUS:
        raise RuntimeError("status drifted")
    if report["core_sha256"] != canonical_sha(report):
        raise RuntimeError("core hash is stale")
    certificate = report["numerical_certificate"]
    if certificate["fixed_profile_integral"] != 1.0:
        raise RuntimeError("fixed source profile is not normalized")
    if certificate["source_field_count_with_y_dependence"] != 0 or certificate["source_KK_tower_present"]:
        raise RuntimeError("an unintended source KK tower was introduced")
    if certificate["wall_J_unitarity_residual"] > 2.0e-12:
        raise RuntimeError("H/Hc wall transfer lost J-unitarity")
    if certificate["K_res_minus_D_K_eff_residual"] > 2.0e-12:
        raise RuntimeError("pole-free and reduced pencils disagree")
    if certificate["total_exotic_chiral_zero_modes"] != 0:
        raise RuntimeError("fixed-profile regulator restored an exotic zero")
    moments = certificate["profile_moments_n0_to_n4"]
    doubled_moments = certificate["doubled_orbifold_profile_moments_n0_to_n4"]
    epsilon = certificate["parameters"]["epsilon"]
    for power in range(5):
        if abs(moments[str(power)] - epsilon**power / (power + 1)) > 1.0e-15:
            raise RuntimeError("profile moment drifted")
        expected_doubled = 0.0 if power % 2 else epsilon**power / (power + 1)
        if abs(doubled_moments[str(power)] - expected_doubled) > 1.0e-15:
            raise RuntimeError("doubled-orbifold profile moment drifted")
    decision = report["decision"]
    if decision["regulator_microscopic_candidate_condition_closed"]:
        raise RuntimeError("the bilocal tree prescription was overpromoted to a microscopic regulator")
    if not decision["strong_collar_Hc_terms_unsuppressed"]:
        raise RuntimeError("the exact strong-collar Hc scaling was lost")
    if decision["point_local_5D_regulator_defined"]:
        raise RuntimeError("the normal Wilson-line kernel is bilocal over epsilon")
    if decision["point_local_5D_UV_completion_proved"]:
        raise RuntimeError("normal Wilson-line smearing is not a point-local 5D UV completion")
    if decision["complete_boundary_EFT_basis_proved_here"] or decision["G2_closed_by_this_subaudit"]:
        raise RuntimeError("this regulator subaudit cannot close the full G2 gate")
    if decision["gates_promoted"]:
        raise RuntimeError("this subaudit cannot promote a gate")


def render_markdown(data: Mapping[str, Any]) -> str:
    cert = data["numerical_certificate"]
    return f"""# V49 fixed-profile source regulator audit

Status: `{data['status']}`

## Verdict

The V48 source-field collar has been replaced by a spectrally unambiguous
construction.  The V47 source multiplets remain **strictly four-dimensional**
at `y=L`; only their interaction with the bulk hypermultiplets is spread over
the width `epsilon`.  There is therefore no source coordinate, no source
transverse eigenproblem and no additional source KK tower.

The exact V48 `H/Hc` square-collar transfer survives for the restricted tree
action whose additional `Hc-Hc` and odd-profile `H-Hc` finite parts are set to
zero.  A strong-collar check shows that those allowed terms are generically
`O(1)`, so this is a matching point rather than a stable complete regulator.
The prescription removes the spurious source tower, but it does not close a
local microscopic regulator candidate or the complete G2 boundary EFT.

## Strictly four-dimensional source theory

Use the original V47 action

```text
S_source = integral d4x [
  integral d4theta K_V47(X,Xdagger,V(L))
  + integral d2theta W_source,V47(X) + h.c.],
```

for
`X=(Phi_210,Sigma_126,barSigma_bar126,S,ThetaPlus,ThetaMinus)`.
The fields depend only on `(x,theta)`, never on `y`.  Hence their canonical
normalization, dimension-one VEVs, F/D equations and V47 physical Hessian are
unchanged exactly.  In particular, there is no source KK tower to stabilize.

## Gauge-covariant fixed smearing

On the doubled endpoint cover use the orbifold-even profile
`rho_double(s)=1/(2 epsilon)` for `|s|<epsilon`, with unit integral.  Its
physical-interval quotient for parity-even operators is
`rho_physical=1/epsilon` on `0<s<epsilon`, also with unit integral.  Thus for
every even integrand the doubled average equals the physical one-sided
average; the latter is the convention used in the exact transfer matrix.

A source field at `L` cannot be multiplied directly by a bulk field at `y` in a
gauge-covariant expression.  Define instead the shortest normal chiral Wilson
line

`U_R(L,y)=P exp[-integral_y^L Phi_R(y')dy']`

and `Hhat_R(y)=U_R(L,y)H_R(y)`.  Since

```text
U_R(L,y) -> g_R(L) U_R(L,y) g_R(y)^(-1),
Hhat_R(y) -> g_R(L) Hhat_R(y),
```

the smeared interaction is gauge invariant:

```text
integral dy rho_epsilon [
  kappa_L ThetaPlus Hhat_LF Hhat_LA/Mstar
 +kappa_R ThetaMinus Hhat_RA Hhat_RF/Mstar
 +kappa_16 barSigma Hhat_LF Hhat_RA/Mstar
 +kappa_bar16 Sigma Hhat_LA Hhat_RF/Mstar].
```

On the simply connected collar, the certificate chooses the trivial
supersymmetric Wilson-line background and axial gauge, so `U=I`.  The
quadratic H/Hc source is then exactly `rho_epsilon Lambda`.  Wilson-line
variations contain a gauge fluctuation and two H fields, and are cubic about
`H=0`; they do not modify the quadratic spectrum.  Source variations add a
normalized H bilinear to the V47 F-equations, which vanishes at `H=0`.

This Wilson line is part of the declared finite-resolution kernel.  It makes
the smearing gauge covariant, but the interaction remains bilocal over
`epsilon`; it is not a point-local microscopic 5D action or UV completion.

## Exact finite-width H/Hc pencil

With `delta=m epsilon` and `X=delta(Lambda-delta I)`, define

```text
D = cosh(sqrt(X)),
Hfun = sinh(sqrt(X))/sqrt(X),
C = (Lambda-delta I) Hfun,
U = delta Hfun.
```

Then

```text
T_wall = [[D,U],[C,D]],
B_epsilon(m) = D^(-1) C,
K_res = (C F-m D S)E+(m C S+D G)O.
```

`K_res` is the fundamental pole-free characteristic.  Where `D` is
invertible it equals `D K_eff`.  The numerical residual is
`{cert['K_res_minus_D_K_eff_residual']:.3g}`, while the wall J-unitarity
residual is `{cert['wall_J_unitarity_residual']:.3g}`.  At zero energy
`B_epsilon(0)=Lambda`, leaving
`{cert['total_exotic_chiral_zero_modes']}` exotic chiral zero modes.

## Hc and mixed-collar operators

Endpoint parity makes `H` even and `Hc` odd.  The exact even-profile moments
are

```text
integral rho_double s^(2n+1) ds = 0,
integral rho_double s^(2n) ds = epsilon^(2n)/(2n+1).
```

Naive Taylor counting with a fixed `Hc` slope is not valid in the retained
strong wall.  At `m=0`, the exact collar equations instead give

```text
H(s)=h0,
Hc(s)=-(s/epsilon) Lambda h0.
```

Therefore

```text
<Hc^T Xi Hc>_rho = (1/3) h0^T Lambda^T Xi Lambda h0,
<rho_odd H^T A Hc> = -(1/2 or 1/3) h0^T A Lambda h0,
```

where the second numerical factor depends on the normalized odd profile.
Both are `O(1)`, independent of `epsilon`.  Only the even-profile `H-Hc`
average vanishes by oddness.  Thus every allowed `Hc-Hc` and odd-profile
`H-Hc/O7/O8` coefficient is a leading regulator coordinate and must enter the
fundamental path-ordered generator.  The displayed V48 transfer is the
zero-finite-part point for those coefficients; zero is not symmetry-enforced.

## Gate scope

This artifact defines a gauge-covariant finite-resolution tree prescription,
removes an unintended source KK tower, and preserves the restricted V48
quadratic pencil.  It also proves why that pencil is not yet the complete
regulator: leading `Hc` and normal-derivative counterterms must be added and
the resulting path-ordered transfer recomputed.  FI terms, gauge and
source-dependent gauge kinetic functions, Pati--Salam boundary/bulk kinetic
mixing, and the full interacting higher-dimensional source basis also remain.
Therefore G2 stays open.  Full roots and thresholds remain separate G6 work.

Primary references: [Marti--Pomarol](https://arxiv.org/abs/hep-th/0106256),
[Hebecker](https://arxiv.org/abs/hep-ph/0112230), and
[Barcelo--Mitra--Moreau](https://arxiv.org/abs/1408.1852).

Core SHA-256: `{data['core_sha256']}`
"""


def write_artifacts(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def check_artifacts(report: Mapping[str, Any]) -> None:
    if not JSON_PATH.exists() or not MD_PATH.exists():
        raise RuntimeError("V49 artifacts are missing; run --write")
    if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
        raise RuntimeError("V49 JSON is stale; run --write")
    if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError("V49 Markdown is stale; run --write")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--print-json", action="store_true")
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
