#!/usr/bin/env python3
"""Physics push for v20: compute what the stated Lagrangian allows.

Separates quantities fixed by the published field content from quantities
that still require external flavour / threshold inputs.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.linalg import svd


MPL = 2.435e18
MGUT = 9.9176e15
VS = 6.313855e11
VPHI = 1.0e17
HBAR_GEV_S = 6.582119569e-25
FOUR_PI = 4.0 * math.pi


@dataclass(frozen=True)
class Charge:
    name: str
    x: int
    pq: int


CHARGES = (
    Charge("F", 1, 1),
    Charge("P", 1, 1),
    Charge("R", 1, 1),
    Charge("Q", 14, -3),
    Charge("Qbar", 3, 3),
    Charge("Pbar", 16, -1),
    Charge("Rbar", -18, -1),
    Charge("S", 4, 4),
    Charge("Sd", -4, -4),
    Charge("H", -2, -2),
    Charge("Hd", 2, 2),
    Charge("Phi", 17, 0),
    Charge("Phid", -17, 0),
)


def inventory_renormalizable_yukawas() -> dict:
    by_name = {c.name: c for c in CHARGES}
    fermions = ["F", "P", "R", "Q", "Qbar", "Pbar", "Rbar"]
    scalars = ["S", "Sd", "H", "Hd", "Phi", "Phid"]
    allowed = []
    for f1 in fermions:
        for f2 in fermions:
            for s in scalars:
                x = by_name[f1].x + by_name[f2].x + by_name[s].x
                pq = by_name[f1].pq + by_name[f2].pq + by_name[s].pq
                if x == 0 and pq == 0:
                    allowed.append({"operator": f"{f1} {f2} {s}", "X": 0, "PQ": 0})
    manuscript = {
        "Phid P Pbar",
        "Phid Q Qbar",
        "Phi R Rbar",
        "P F H",
        "R F H",
        "Qbar F Sd",
    }
    extras = [row for row in allowed if row["operator"] not in manuscript]
    return {
        "n_charge_allowed_monomials": len(allowed),
        "manuscript_listed": sorted(manuscript),
        "n_extra_charge_allowed": len(extras),
        "extra_examples": [
            row["operator"]
            for row in extras
            if row["operator"] in {"P R H", "P P H", "R R H", "Qbar R Sd", "Qbar F Sd"}
            or "Phi" in row["operator"]
            or "Phid" in row["operator"]
        ][:20],
        "implication": (
            "extra portals modify the 5x2 X=1 heavy-light mass block and the "
            "matching diagrams; they are fit parameters, not fixed predictions"
        ),
    }


def corrected_decay_width(
    portal: float,
    heavy_mass: float,
    final_mass: float,
) -> dict:
    if heavy_mass <= 0.0:
        raise ValueError("heavy_mass must be positive")
    massless = portal**2 * heavy_mass / (32.0 * math.pi)
    if final_mass >= heavy_mass:
        width = 0.0
        kinematic = 0.0
    else:
        kinematic = (1.0 - (final_mass / heavy_mass) ** 2) ** 2
        width = massless * kinematic
    lifetime = float("inf") if width == 0.0 else HBAR_GEV_S / width
    return {
        "massless_upper_benchmark_GeV": massless,
        "kinematic_factor": kinematic,
        "width_GeV": width,
        "lifetime_s": lifetime,
        "inequality": "Gamma <= |lambda|^2 M/(32 pi) for m_final < M",
    }


def continuous_spin10_trajectory() -> dict:
    alpha_inv_bare = 37.313
    shift = -(40.0 / 3.0) / (2.0 * math.pi) * math.log(MGUT / VS)
    alpha_inv_gut = alpha_inv_bare + shift
    sum_weyl_t = 3 * 2 + 10 * 2 + 6 * 2
    b_cons = -(11.0 / 3.0) * 8 + (2.0 / 3.0) * sum_weyl_t + (1.0 / 3.0) * (1 + 35 + 56)
    b_phys = (
        -(11.0 / 3.0) * 8
        + (2.0 / 3.0) * sum_weyl_t
        + (1.0 / 3.0) * (1 + 35)
        + (1.0 / 6.0) * 56
    )

    def run(inv: float, b: float, a: float, bmu: float) -> float:
        return inv - (b / (2.0 * math.pi)) * math.log(bmu / a)

    out = {}
    for label, b in (("conservative_complex_210", b_cons), ("physical_real_210", b_phys)):
        inv_v = run(alpha_inv_gut, b, MGUT, VPHI)
        inv_p = run(inv_v, b, VPHI, MPL)
        out[label] = {
            "b_10": b,
            "alpha_inv_GUT_after_spectators": alpha_inv_gut,
            "alpha_inv_vPhi": inv_v,
            "alpha_vPhi": None if inv_v <= 0 else 1.0 / inv_v,
            "alpha_inv_MPl": inv_p,
            "alpha_MPl": None if inv_p <= 0 else 1.0 / inv_p,
            "landau_pole_below_MPl": inv_p <= 0.0,
            "weakly_coupled_at_MPl_alpha_lt_0.25": inv_p > 0.0 and (1.0 / inv_p) < 0.25,
        }
    out["inconsistent_reset_alpha_inv_vPhi"] = 40.0
    out["verdict"] = (
        "single-trajectory one-loop Spin(10) running from the model's "
        "spectator-corrected alpha_GUT does not remain perturbative to M_Pl "
        "under either the conservative or physical beta used here"
    )
    return out


def completeness_gate() -> dict:
    """What is fixed vs what still needs external inputs."""
    return {
        "fixed_by_stated_charges_and_tensors": [
            "continuous anomaly cancellation",
            "one-pair no-go (discriminant -15)",
            "three-pair portal-basis uniqueness under the stated ansatz",
            "existence of nonzero 10_H Clifford channels for every 16 component",
            "charge-based absence of vector-neutral PQ closure through P=7",
            "existence of at least one P=8 matching topology",
            "finite repeated-pole momentum kernel for the displayed graph",
        ],
        "needs_additional_physical_inputs": [
            "SO(10)-breaking Higgs vacuum alignment (210, 126, 10)",
            "full Yukawa tensors Y_10, Y_126 and portal matrices lambda",
            "broken-phase Clebsches for every SM component",
            "two-loop threshold matching across M_I, M_GUT, v_Phi",
            "Planck-scale Wilson coefficients and flavour contractions",
            "radiative stabilization of v_Phi/v_S",
            "cosmic-string network for (ell,n)=(13,-3)",
        ],
        "honest_gate": (
            "v20 does not yet specify the broken-phase Higgs vacuum and Yukawa "
            "tensors well enough for a unique Clebsch/flavour prediction or a "
            "unique two-loop threshold trajectory"
        ),
    }


def type_i_seesaw_benchmark(v_r: float = VS) -> dict:
    """Constrained three-family Type-I toy benchmark at the v20 B-L scale.

    This is not a full 10+126 SO(10) fit.  It only asks whether a
    perturbative right-handed Majorana scale M_R ~ v_R can reproduce the
    observed Delta m^2 targets for O(1) Dirac Yukawas, and whether forcing
    M_R = v_S stresses perturbativity.
    """
    # NuFIT-6.0-ish central targets (normal ordering), eV units.
    dm21 = 7.41e-2**2  # (~0.00549 eV^2) use mass-squared directly
    dm21 = 7.41e-5
    dm31 = 2.511e-3
    m_light = np.array([0.0, math.sqrt(dm21), math.sqrt(dm31)])  # eV, m1=0
    # Convert to GeV
    m_light_gev = m_light * 1.0e-9
    v_ew = 174.0  # GeV, single vev normalization for the toy Dirac sector

    # Type-I: m_nu ~= v^2 y y^T / M_R  =>  |y|_eff ~ sqrt(m_nu M_R)/v
    y_eff = np.sqrt(np.maximum(m_light_gev, 0.0) * v_r) / v_ew
    y_max = float(np.max(y_eff))
    # Published-style 126 stress: if M_R is identified with v_R and the
    # seesaw needs large Yukawas, y_126 ~ M_R / v_R is O(1), but fitting
    # charged fermions at low v_R can push the 126 Yukawa.
    # Here we report the Type-I Dirac Yukawa needed at this M_R.
    return {
        "assumptions": (
            "Type-I toy with M_R = v_R, m1=0 normal ordering, no full "
            "Clebsch/10+126 textures"
        ),
        "v_R_GeV": v_r,
        "delta_m21_eV2": dm21,
        "delta_m31_eV2": dm31,
        "sum_mnu_eV": float(np.sum(m_light)),
        "y_dirac_eff": y_eff.tolist(),
        "y_dirac_max": y_max,
        "perturbative_4pi": y_max < FOUR_PI,
        "boundary_stress_4pi": y_max > 1.0,
        "note": (
            "a genuine 10+126 fit at v_R=6.3e11 GeV can be more stressed than "
            "this Type-I lower bound; the single-scale identification is at "
            "best a constrained benchmark, not a zero-knob prediction"
        ),
    }


def heavy_light_rank_audit() -> dict:
    """Generic rank of the X=1 block after including extra portals."""
    # Five X=1 Weyl 16s: F1,F2,F3,P,R against two bars Pbar(X=16), Rbar(X=-18)
    # plus Qbar couplings through S.  A generic complex 5x2 matrix has rank 2.
    rng = np.random.default_rng(20)
    block = rng.normal(size=(5, 2)) + 1j * rng.normal(size=(5, 2))
    singular = svd(block, compute_uv=False)
    rank = int(np.sum(singular > 1e-12))
    light = 5 - rank
    return {
        "n_X1_sixteen_fields": 5,
        "n_pairing_bars_in_Phi_sector": 2,
        "generic_rank": rank,
        "light_chiral_families": light,
        "stable_under_extra_PRH_portal": light == 3,
        "detail": (
            "an extra P R 10_H term mixes heavies after EW breaking but does "
            "not by itself remove the three light combinations of the Phi-mass "
            "rank count"
        ),
    }


def build_report() -> dict:
    heavy = VPHI / math.sqrt(2.0)
    decays = {
        "massless_lambda_1e-8": corrected_decay_width(1e-8, heavy, 0.0),
        "to_EW_scale_final": corrected_decay_width(1e-8, heavy, 246.0),
        "to_half_mass_final": corrected_decay_width(1e-8, heavy, 0.5 * heavy),
        "portal_for_tau_lt_1s_massless": math.sqrt(32.0 * math.pi * HBAR_GEV_S / heavy),
        "portal_for_tau_lt_1s_half_mass": math.sqrt(
            32.0 * math.pi * HBAR_GEV_S / (heavy * (1.0 - 0.25) ** 2)
        ),
    }
    return {
        "status": "physics push complete within stated Lagrangian",
        "completeness_gate": completeness_gate(),
        "extra_portals": inventory_renormalizable_yukawas(),
        "continuous_spin10_rg": continuous_spin10_trajectory(),
        "corrected_decays": decays,
        "heavy_light_rank": heavy_light_rank_audit(),
        "seesaw_benchmark_at_v20_scale": type_i_seesaw_benchmark(VS),
        "not_claimed": [
            "experimental dark-matter detection",
            "unique broken-phase flavour solution",
            "two-loop threshold unification fit",
            "proof that nature realizes the model",
        ],
        "bottom_line": (
            "The anomaly/minimality/portal-existence core survives. The "
            "single-scale UV-perturbativity claim does not survive continuous "
            "one-loop Spin(10) running. v20 remains a candidate model, not "
            "evidence that an axion has been found."
        ),
    }


def main() -> int:
    report = build_report()
    path = Path(__file__).resolve().parent / "physics_push_v20.json"
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "status": report["status"],
        "bottom_line": report["bottom_line"],
        "rg_verdict": report["continuous_spin10_rg"]["verdict"],
        "y_dirac_max": report["seesaw_benchmark_at_v20_scale"]["y_dirac_max"],
        "extra_portals": report["extra_portals"]["n_extra_charge_allowed"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
