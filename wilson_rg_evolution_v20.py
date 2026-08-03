#!/usr/bin/env python3
"""Wilson-tensor RG evolution for the leading v20 PQ-breaking operators.

Evolves schematic dimensionless coefficients for the dimension-5 portal
O5 ~ (S†)^2 (16_14 16bar_s) / M_Pl and the dimension-8 spurion
O8 ~ (S†)^2 [(ss)_10]^2 / M_Pl^4 from M_Pl down through v_Phi, M_GUT and v_S.

This is a one-loop anomalous-dimension envelope, not a full operator-basis
mixing calculation.  It converts 'unknown O(1) at M_Pl' into a tracked
running band for falsification against the quality bound.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


MPL = 2.435e18
VPHI = 1.0e17
MGUT = 9.9176e15
VS = 6.313855e11
MZ = 91.1876
CHI = (75.5e-3) ** 4


def alpha_inv_piecewise(mu: float) -> float:
    """Rough continuous alpha^{-1}(mu) using the package's one-loop anchors."""
    # Below MI: SM-ish; between MI and MGUT: PS-ish; above: Spin(10)-ish.
    # Use a simple log interpolation anchored at known points.
    anchors = [
        (MZ, 30.0),          # rough mean of SM couplings
        (VS, 35.0),
        (MGUT, 37.313),
        (VPHI, 16.65),       # spectator-corrected continuous value
        (MPL, 8.0),          # illustrative physical running endpoint
    ]
    if mu <= anchors[0][0]:
        return anchors[0][1]
    if mu >= anchors[-1][0]:
        return anchors[-1][1]
    for (m0, a0), (m1, a1) in zip(anchors, anchors[1:]):
        if m0 <= mu <= m1:
            t = math.log(mu / m0) / math.log(m1 / m0)
            return a0 + t * (a1 - a0)
    return anchors[-1][1]


def run_wilson(
    c_planck: float,
    gamma0: float,
    mu_from: float,
    mu_to: float,
    n_steps: int = 200,
) -> float:
    """One-loop: dC / dln mu = (gamma0 / 16pi^2) g^2 C, with g^2=4pi/alpha_inv."""
    c = c_planck
    logs = np_linspace_log(mu_from, mu_to, n_steps)
    for i in range(len(logs) - 1):
        mu_a, mu_b = logs[i], logs[i + 1]
        mu_mid = math.sqrt(mu_a * mu_b)
        ainv = alpha_inv_piecewise(mu_mid)
        g2 = 4.0 * math.pi / max(ainv, 1e-6)
        dln = math.log(mu_b / mu_a)
        c *= math.exp((gamma0 * g2 / (16.0 * math.pi**2)) * dln)
    return c


def np_linspace_log(a: float, b: float, n: int) -> list[float]:
    return [math.exp(math.log(a) + (math.log(b) - math.log(a)) * i / (n - 1)) for i in range(n)]


def quality_shift_from_p8(c8_at_vs: float) -> dict:
    """Map a running C8 into the unit-kernel shift scaled by |C8|."""
    unit = 6.043043168794402e-47
    shift = abs(c8_at_vs) * unit
    return {
        "worst_phase": shift,
        "safe_below_1e-10": shift < 1e-10,
        "max_abs_C8_for_quality": 1e-10 / unit,
    }


def build_report() -> dict:
    # Anomalous-dimension envelopes (order-of-magnitude):
    # large positive gamma => grows in IR; negative => shrinks in IR.
    scenarios = {
        "NDA_O1_at_MPl_mild_shrink": {"c_pl": 1.0, "gamma5": -1.0, "gamma8": -2.0},
        "NDA_O1_at_MPl_mild_grow": {"c_pl": 1.0, "gamma5": 1.0, "gamma8": 2.0},
        "large_Wilson_1e6_at_MPl": {"c_pl": 1.0e6, "gamma5": 1.0, "gamma8": 2.0},
    }
    out = {}
    for name, sc in scenarios.items():
        c5_vphi = run_wilson(sc["c_pl"], sc["gamma5"], MPL, VPHI)
        c5_vs = run_wilson(c5_vphi, sc["gamma5"], VPHI, VS)
        c8_vphi = run_wilson(sc["c_pl"], sc["gamma8"], MPL, VPHI)
        c8_vs = run_wilson(c8_vphi, sc["gamma8"], VPHI, VS)
        # P=8 uses four O5 and one O8 => schematic C8_eff ~ c5^4 * c8
        c8_eff = (c5_vs**4) * c8_vs
        q = quality_shift_from_p8(c8_eff)
        out[name] = {
            "C5_at_vS": c5_vs,
            "C8_at_vS": c8_vs,
            "C8_eff_schematic": c8_eff,
            "quality": q,
        }

    # Direct dim-21 scalar Phi^4 (S†)^17 / M_Pl^17 with running of its Wilson c21
    s0 = VS / math.sqrt(2.0)
    phi0 = VPHI / math.sqrt(2.0)
    # Evaluate in logs to avoid float overflow: A = phi^4 s^17 / M^17
    log_a21_unit = 4.0 * math.log(phi0) + 17.0 * math.log(s0) - 17.0 * math.log(MPL)
    a21_unit = math.exp(log_a21_unit)
    direct = {}
    for name, sc in scenarios.items():
        c21 = run_wilson(sc["c_pl"], 3.0 if "grow" in name or "1e6" in name else -1.0, MPL, VS)
        shift = 2.0 * abs(c21) * a21_unit / CHI
        direct[name] = {
            "C21_at_vS": c21,
            "worst_phase": shift,
            "safe_below_1e-10": shift < 1e-10,
        }

    return {
        "status": "Wilson RG envelope report",
        "method": "one-loop anomalous-dimension envelope on schematic coefficients",
        "scales_GeV": {"M_Pl": MPL, "v_Phi": VPHI, "M_GUT": MGUT, "v_S": VS},
        "operator_running": out,
        "direct_scalar_dimension21": direct,
        "quality_bound": 1e-10,
        "falsification_rule": (
            "If a UV completion forces |C8_eff| above ~1e10/unit or |C21| above "
            "the direct-scalar ceiling, axion quality is falsified."
        ),
        "verdict": (
            "O(1) Planck Wilson coefficients remain safe after this envelope. "
            "A forced |C|≳1e6 at M_Pl with IR growth can threaten quality — "
            "that is a UV-completion constraint, not a prediction of v20."
        ),
        "honest_limitation": (
            "Full operator mixing, gauge thresholds, and flavour tensors are "
            "not included; replace gamma envelopes with a complete basis for "
            "referee-grade numbers."
        ),
    }


def main() -> int:
    report = build_report()
    Path(__file__).resolve().parent.joinpath("wilson_rg_evolution_v20.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    mild = report["operator_running"]["NDA_O1_at_MPl_mild_shrink"]
    print(
        json.dumps(
            {
                "C8_eff_mild": mild["C8_eff_schematic"],
                "safe_mild": mild["quality"]["safe_below_1e-10"],
                "max_C8": mild["quality"]["max_abs_C8_for_quality"],
                "verdict": report["verdict"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
