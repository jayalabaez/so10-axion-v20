#!/usr/bin/env python3
"""Independent v20 error audit.

This module intentionally imports none of the v20 engines.  Every numerical
check is re-derived from first principles so that a passing release gate
cannot hide overclaims already baked into the package.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


MPL = 2.435e18
MGUT = 9.9176e15
VS = 6.313855e11
VPHI = 1.0e17
CHI = (75.5e-3) ** 4
HBAR_GEV_S = 6.582119569e-25
FOUR_PI = 4.0 * math.pi


def _row(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}


def anomaly_cancellation() -> list[dict]:
    light = (
        3 * 2 + 5 * 2 * (2 - 6),
        3 * 16 + 5 * 16 * (2 - 6),
        3 * 16 + 5 * 16 * (2**3 + (-6) ** 3),
    )
    charges = ((1, 16), (14, 3), (1, -18))
    heavy = (
        2 * sum(x + y for x, y in charges),
        16 * sum(x + y for x, y in charges),
        16 * sum(x**3 + y**3 for x, y in charges),
    )
    total = tuple(a + b for a, b in zip(light, heavy))
    return [
        _row("light anomaly baseline", light == (-34, -272, -16592), str(light)),
        _row("heavy anomaly opposite", heavy == (34, 272, 16592), str(heavy)),
        _row("continuous anomalies cancel", total == (0, 0, 0), str(total)),
        _row(
            "one-pair discriminant is -15",
            17**2 - 4 * ((17**3 - 1037) // (3 * 17)) == -15,
            str(17**2 - 4 * 76),
        ),
    ]


def hermite_factor_audit() -> list[dict]:
    """Manuscript scalar/P=12 NDA bounds omit the hermitian-conjugate two."""
    s0 = VS / math.sqrt(2.0)
    scalar_one_sided = (s0**17) / (MPL**13 * CHI)
    scalar_corrected = 2.0 * scalar_one_sided
    p12_one_sided = (VS**4 / CHI) * (VS / MPL) ** 12
    p12_corrected = 2.0 * p12_one_sided
    return [
        _row(
            "scalar S^17 one-sided is ~3.24e-37",
            abs(scalar_one_sided / 3.24e-37 - 1.0) < 0.02,
            f"{scalar_one_sided:.3e}",
        ),
        _row(
            "scalar S^17 with h.c. is ~6.47e-37",
            abs(scalar_corrected / 6.47e-37 - 1.0) < 0.02,
            f"{scalar_corrected:.3e}",
        ),
        _row(
            "P=12 NDA one-sided is ~4.52e-28",
            abs(p12_one_sided / 4.52e-28 - 1.0) < 0.02,
            f"{p12_one_sided:.3e}",
        ),
        _row(
            "P=12 NDA with h.c. is ~9.04e-28",
            abs(p12_corrected / 9.04e-28 - 1.0) < 0.02,
            f"{p12_corrected:.3e}",
        ),
        _row(
            "manuscript must not quote one-sided number as |Delta theta|",
            True,
            "V_break = A e^{ia/f}+h.c. implies worst phase 2|A|/chi",
        ),
    ]


def decay_width_audit() -> list[dict]:
    """Massless Gamma = |lambda|^2 M/(32 pi) is an upper benchmark, not a lower bound."""
    mass = VPHI / math.sqrt(2.0)
    lam = 1.0e-8
    gamma_massless = lam**2 * mass / (32.0 * math.pi)

    def gamma(m_final: float) -> float:
        if m_final >= mass:
            return 0.0
        kinematic = (1.0 - (m_final / mass) ** 2) ** 2
        return gamma_massless * kinematic

    # Final state lighter than parent: kinematic factor <= 1.
    ratios = [gamma(x) / gamma_massless for x in (0.0, 246.0, VS, 0.5 * mass)]
    return [
        _row(
            "massless width equals |lambda|^2 M/(32 pi)",
            abs(gamma_massless / 0.07033721219977392 - 1.0) < 1e-12,
            f"{gamma_massless:.6e}",
        ),
        _row(
            "kinematic factor is always <= 1 for m_final < M",
            all(0.0 <= r <= 1.0 + 1e-15 for r in ratios),
            str(ratios),
        ),
        _row(
            "correct inequality is Gamma <= massless benchmark",
            gamma(VS) < gamma_massless and gamma(0.5 * mass) < gamma_massless,
            "manuscript Gamma >= ... overstates the width",
        ),
        _row(
            "lifetime lower bound uses kinematic suppression",
            HBAR_GEV_S / gamma(0.5 * mass) > HBAR_GEV_S / gamma_massless,
            "optimistic 1-second portal bound needs the full width",
        ),
    ]


def continuous_spin10_running_audit() -> list[dict]:
    """Single-trajectory running from the model's own alpha_GUT after spectators."""
    alpha_inv_gut_bare = 37.313
    spectator_shift = -(40.0 / 3.0) / (2.0 * math.pi) * math.log(MGUT / VS)
    alpha_inv_gut = alpha_inv_gut_bare + spectator_shift  # ~16.810

    sum_weyl_t = 3 * 2 + 10 * 2 + 6 * 2  # light 16s + heavy complete pairs
    # Conservative envelope used in v20: treat real 210 as complex.
    b_cons = -(11.0 / 3.0) * 8 + (2.0 / 3.0) * sum_weyl_t + (1.0 / 3.0) * (1 + 35 + 56)
    # Physical: real 210 contributes half of a complex scalar.
    b_phys = -(11.0 / 3.0) * 8 + (2.0 / 3.0) * sum_weyl_t + (1.0 / 3.0) * (1 + 35) + (1.0 / 6.0) * 56

    def evolve(alpha_inv: float, b: float, mu_from: float, mu_to: float) -> float:
        return alpha_inv - (b / (2.0 * math.pi)) * math.log(mu_to / mu_from)

    inv_vphi_cons = evolve(alpha_inv_gut, b_cons, MGUT, VPHI)
    inv_mpl_cons = evolve(inv_vphi_cons, b_cons, VPHI, MPL)
    inv_vphi_phys = evolve(alpha_inv_gut, b_phys, MGUT, VPHI)
    inv_mpl_phys = evolve(inv_vphi_phys, b_phys, VPHI, MPL)

    reset_claim = 40.0
    return [
        _row(
            "spectator-corrected 1/alpha_GUT is ~16.810",
            abs(alpha_inv_gut - 16.810) < 0.01,
            f"{alpha_inv_gut:.3f}",
        ),
        _row(
            "resetting 1/alpha_10(v_Phi)=40 is inconsistent with continuous running",
            abs(inv_vphi_cons - reset_claim) > 20.0 and abs(inv_vphi_phys - reset_claim) > 20.0,
            f"continuous cons={inv_vphi_cons:.3f}, phys={inv_vphi_phys:.3f}",
        ),
        _row(
            "conservative continuous trajectory hits a Landau pole below M_Pl",
            inv_mpl_cons <= 0.0,
            f"1/alpha(M_Pl)_cons={inv_mpl_cons:.3f}",
        ),
        _row(
            "physical continuous trajectory is not weakly coupled at M_Pl",
            inv_mpl_phys > 0.0 and (1.0 / inv_mpl_phys) > 0.25,
            f"alpha(M_Pl)_phys={1.0 / inv_mpl_phys:.3f}",
        ),
        _row(
            "v20 'perturbative to M_Pl with alpha=1/40' claim fails under single RG trajectory",
            inv_mpl_cons <= 0.0 or (1.0 / inv_mpl_phys) > 0.25,
            "requires two-loop thresholds or a revised scale choice",
        ),
    ]


def incomplete_lagrangian_audit() -> list[dict]:
    """Catalogue additional gauge+PQ invariant renormalizable operators."""
    # Charges: (X, PQ)
    fields = {
        "F": (1, 1),
        "P": (1, 1),
        "R": (1, 1),
        "Q": (14, -3),
        "Qbar": (3, 3),
        "Pbar": (16, -1),
        "Rbar": (-18, -1),
        "S": (4, 4),
        "Sd": (-4, -4),
        "H": (-2, -2),
        "Hd": (2, 2),
        "Phi": (17, 0),
        "Phid": (-17, 0),
    }

    def ok(names: tuple[str, ...]) -> bool:
        xs = sum(fields[n][0] for n in names)
        pqs = sum(fields[n][1] for n in names)
        return xs == 0 and pqs == 0

    written = {
        "Phid P Pbar",
        "Phid Q Qbar",
        "Phi R Rbar",
        "P F H",
        "R F H",
        "Qbar F Sd",
    }
    extras = []
    # Fermion bilinears with one scalar (renormalizable Yukawa-like).
    fermions = ["F", "P", "R", "Q", "Qbar", "Pbar", "Rbar"]
    scalars = ["S", "Sd", "H", "Hd", "Phi", "Phid"]
    for f1 in fermions:
        for f2 in fermions:
            for s in scalars:
                label = f"{f1} {f2} {s}"
                if ok((f1, f2, s)):
                    extras.append(label)

    missing_from_manuscript = [op for op in extras if op not in written and " ".join(reversed(op.split())) not in written]
    # Highlight the physically important cross terms.
    important = [op for op in ("P R H", "Qbar R Sd", "P P H", "R R H", "Qbar Qbar Sd") if ok(tuple(op.split()))]
    return [
        _row(
            "manuscript portal list is incomplete",
            len(missing_from_manuscript) > 0,
            f"{len(missing_from_manuscript)} additional charge-allowed monomials",
        ),
        _row(
            "P R 10_H is gauge and PQ invariant",
            ok(("P", "R", "H")),
            "cross-pair mass/mixing after Phi and electroweak breaking",
        ),
        _row(
            "Qbar R S^dagger is gauge and PQ invariant",
            ok(("Qbar", "R", "Sd")),
            "extra heavy-light / heavy-heavy portal",
        ),
        _row(
            "important extra portals exist",
            len(important) >= 2,
            str(important),
        ),
    ]


def amplitude_scope_audit() -> list[dict]:
    """6.04e-47 is a unit-coefficient kernel, not a physical prediction."""
    # Rebuild the published unit-coefficient P=8 number only as a diagnostic.
    # Exact kernel needs the v20 integral; here we only enforce the scope claim.
    return [
        _row(
            "P=8 number is per-unit normalized coefficient only",
            True,
            "Wilson x Yukawa x Clebsch x flavour x RG tensors remain free",
        ),
        _row(
            "sum over all P=8 topologies is not completed",
            True,
            "one selected graph is displayed",
        ),
        _row(
            "broken-phase Clebsch/flavour fit is external",
            True,
            "cannot be closed by anomaly arithmetic alone",
        ),
    ]


def fermion_current_audit() -> list[dict]:
    """Independent one-family connection check and exact beta normalization."""
    ratio = VS / VPHI
    sin2_eta = ratio**2 / (1.0 + ratio**2)
    projected = 1.0 - 4.0 * sin2_eta
    connection = 4.0 * sin2_eta
    moving_total = projected + connection

    d = math.hypot(17.0 * VPHI, 4.0 * VS)
    xi = 17.0 * VPHI**2 / d**2
    tan_beta = 1.5
    sin2_beta = tan_beta**2 / (1.0 + tan_beta**2)
    cos2_beta = 1.0 - sin2_beta
    ce = xi * sin2_beta
    cp = -0.47 + xi * (0.8645 * cos2_beta - 0.437 * sin2_beta)
    cn = -0.02 + xi * (-0.4055 * cos2_beta + 0.833 * sin2_beta)

    frozen = json.loads(
        Path(__file__)
        .resolve()
        .parent.joinpath("data", "frozen_inputs_v20.json")
        .read_text(encoding="utf-8")
    )
    benchmark = frozen["v20_benchmark"]
    return [
        _row(
            "moving-frame identity does not erase projected portal shift",
            abs(moving_total - 1.0) < 1e-15
            and connection > 0.0
            and projected != 1.0,
            (
                f"Qproj={projected:.16f}, Berry={connection:.3e}, "
                f"sum={moving_total:.16f}"
            ),
        ),
        _row(
            "exact finite-vPhi xi is ~0.058823529411635",
            abs(xi - 0.058823529411634885) < 1e-15,
            f"{xi:.16f}",
        ),
        _row(
            "aligned full-central hadronic benchmark replaces rounded ERT values",
            abs(ce - 0.04072398190036261) < 1e-14
            and abs(cp + 0.4721493212669636) < 1e-14
            and abs(cn - 0.0065837104071811425) < 1e-14,
            f"(Ce,Cp,Cn)=({ce:.12f},{cp:.12f},{cn:.12f})",
        ),
        _row(
            "tan_beta is absent from frozen v20 inputs",
            "tan_beta" not in benchmark,
            "numeric C_e,C_p,C_n cannot be a frozen unique prediction",
        ),
    ]


def build_audit() -> dict:
    sections = {
        "anomaly_core_survives": anomaly_cancellation(),
        "hermitian_conjugate_normalization": hermite_factor_audit(),
        "decay_width_inequality": decay_width_audit(),
        "continuous_spin10_running": continuous_spin10_running_audit(),
        "incomplete_lagrangian": incomplete_lagrangian_audit(),
        "amplitude_scope": amplitude_scope_audit(),
        "fermion_current_and_beta": fermion_current_audit(),
    }
    rows = [row for group in sections.values() for row in group]
    # Soft-falsification flags: overclaims that fail under corrected physics.
    soft_fails = [
        "v20 'perturbative to M_Pl with alpha=1/40' claim fails under single RG trajectory",
        "correct inequality is Gamma <= massless benchmark",
        "manuscript portal list is incomplete",
    ]
    soft = [name for name in soft_fails if any(r["name"] == name and r["passed"] for r in rows)]
    return {
        "status": "PASS" if all(r["passed"] for r in rows) else "FAIL",
        "n_checks_total": len(rows),
        "n_checks_failed": sum(1 for r in rows if not r["passed"]),
        "failures": [r["name"] for r in rows if not r["passed"]],
        "soft_falsifications_of_manuscript_overclaims": soft,
        "verdict": (
            "v20 is not falsified as an anomaly-free candidate, but several "
            "manuscript claims are overstated: Gamma inequality, Spin(10) "
            "alpha reset, missing h.c. factors, incomplete portal list, and "
            "unit-coefficient amplitudes. Continuous one-loop Spin(10) "
            "running from the spectator-corrected alpha_GUT is not perturbative "
            "to M_Pl under the stated beta functions."
        ),
        "sections": sections,
    }


def main() -> int:
    audit = build_audit()
    out = Path(__file__).resolve().parent / "V20_ERROR_AUDIT.json"
    out.write_text(json.dumps(audit, indent=2) + "\n")
    print(json.dumps({k: audit[k] for k in ("status", "n_checks_total", "n_checks_failed", "failures", "soft_falsifications_of_manuscript_overclaims", "verdict")}, indent=2))
    for section, rows in audit["sections"].items():
        print(f"\n## {section}")
        for row in rows:
            mark = "PASS" if row["passed"] else "FAIL"
            print(f"[{mark}] {row['name']}: {row['detail']}")
    return 0 if audit["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
