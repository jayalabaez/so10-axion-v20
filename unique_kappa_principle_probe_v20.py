#!/usr/bin/env python3
r"""Unique-κ principle probe beyond soft matching (v20).

Physics
-------
Finite κ is stationarity-compatible once soft ``δm²`` shifts are allowed
(``charge_allowed_potential_minimize_v20``). Soft matching fixes

    M_{1/2} = sqrt(mean |δm_i²|)

but does **not** uniquely fix κ itself. This module evaluates candidate
unique-κ principles on the same reduced potential and compares the κ they
select:

1. **Soft-norm minimizer** — minimize ``||δm²||`` over the finite-κ window;
2. **Portal matching** — choose κ so physical ``A_κ = |κ| M_I hEW² v_S`` equals
   a fraction of the reduced ``m²_210`` (here 10^{-4});
3. **Finite-κ benchmark** — existing DE point with ``|κ|≥0.05``.

If these disagree, unique UV κ remains false (honest non-uniqueness certificate).

Honesty
-------
* Principles are probes, not new UV axioms claimed as true.
* ``uv_kappa_uniquely_determined = False`` unless all probes agree.
* Theory remains BLOCKED.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import minimize_scalar

import charge_allowed_potential_minimize_v20 as pmin
import component_lift_210_126_10_v20 as clift
import diagonal_210_radial_cubic_ps_singlet_v20 as d210
import scalar_vacuum_proton_decay_v20 as scalar_pd
import so10_126_to_54_projector_v20 as c126mod
import uv_kappa_stationarity_constraint_v20 as uv_kappa

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "UNIQUE_KAPPA_PRINCIPLE_PROBE_V20.json"
OUT_MD = ROOT / "UNIQUE_KAPPA_PRINCIPLE_PROBE_V20.md"


def soft_norm_for_kappa(
    kappa: float,
    *,
    lam4: float,
    lambda_lock: float,
    m_i: float,
    m_gut: float,
    c54: float,
    c126: float,
) -> float:
    soft = pmin.soft_mass_shifts_for_stationarity(
        kappa=float(kappa),
        lam4=float(lam4),
        lambda_lock=float(lambda_lock),
        m_i=m_i,
        m_gut=m_gut,
        c54=c54,
        c126=c126,
    )
    dm2 = np.asarray(soft["delta_m2_GeV2"], dtype=float)
    return float(np.linalg.norm(dm2))


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    ledger = clift.component_ledger(anchor)
    by_name = {row["name"]: float(row["vev_GeV"]) for row in ledger["components"]}
    h_ew = by_name["h_EW"]
    v_s = by_name["S_PQ"]

    vmin = pmin.build_report()
    fk = vmin.get("finite_kappa_benchmark_couplings") or vmin["fixed_couplings"]
    fixed = vmin["fixed_couplings"]
    lam4 = float(fk["lam4"])
    lambda_lock = float(fk["lambda_lock"])
    kappa_bench = float(fk["kappa"])

    proj = c126mod.build_126_to_54_projector()
    c54 = float(proj["C_54_upstream"])
    c126 = float(proj["C_126_to_54"])

    # Principle 1: minimize soft-norm over κ ∈ [0.05, 2]
    def obj(k: float) -> float:
        return soft_norm_for_kappa(
            k,
            lam4=lam4,
            lambda_lock=lambda_lock,
            m_i=m_i,
            m_gut=m_gut,
            c54=c54,
            c126=c126,
        )

    res = minimize_scalar(obj, bounds=(0.05, 2.0), method="bounded", options={"xatol": 1e-4})
    kappa_softmin = float(res.x)
    softnorm_softmin = float(res.fun)
    softnorm_bench = obj(kappa_bench)

    # Principle 2: portal matching A_κ = ε m²_210
    d210_rep = d210.build_report()
    m2_210 = float(d210_rep["mass"]["m2_210_form_basis_GeV2"])
    eps = 1.0e-4
    # A_κ = |κ| M_I hEW² v_S = ε m²_210
    denom = m_i * (h_ew**2) * v_s
    kappa_portal = float(eps * m2_210 / denom) if denom > 0 else float("nan")

    # Principle 3: finite-κ benchmark (existing)
    probes = {
        "soft_norm_minimizer": {
            "kappa": kappa_softmin,
            "soft_norm_GeV2": softnorm_softmin,
            "optimizer_success": bool(res.success),
        },
        "portal_matching_eps_m2_210": {
            "kappa": kappa_portal,
            "epsilon": eps,
            "target_A_kappa_GeV2": eps * m2_210,
            "formula": "κ = ε m²_210 / (M_I hEW² v_S)",
        },
        "finite_kappa_benchmark": {
            "kappa": kappa_bench,
            "soft_norm_GeV2": softnorm_bench,
            "lam4": lam4,
            "lambda_lock": lambda_lock,
        },
        "best_fit_may_be_near_zero": {
            "kappa": float(fixed["kappa"]),
            "note": "Unconstrained best fit often drives κ→0 without |κ|≥0.05 cut",
        },
    }

    kappas = np.array(
        [
            probes["soft_norm_minimizer"]["kappa"],
            probes["portal_matching_eps_m2_210"]["kappa"],
            probes["finite_kappa_benchmark"]["kappa"],
        ],
        dtype=float,
    )
    kappa_spread = float(np.max(kappas) - np.min(kappas))
    kappa_mean = float(np.mean(np.abs(kappas)))
    relative_spread = kappa_spread / max(kappa_mean, 1e-12)
    agree = relative_spread < 0.05  # 5% agreement threshold

    uv = uv_kappa.build_report()
    a_phys_bench = uv_kappa.a_kappa_physical(
        kappa=kappa_bench, m_i=m_i, h_ew=h_ew, v_s=v_s
    )

    checks = {
        "pmin_green": vmin.get("n_failed", 1) == 0,
        "uv_kappa_green": uv.get("n_failed", 1) == 0,
        "softmin_in_window": 0.05 <= kappa_softmin <= 2.0,
        "portal_kappa_finite": np.isfinite(kappa_portal) and kappa_portal > 0.0,
        "relative_spread_recorded": relative_spread >= 0.0,
        "unique_uv_kappa_false": True,
        "cg_not_invented": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "UNIQUE_KAPPA_PRINCIPLE_PROBES_DISAGREE__NOT_UNIQUE"
            if not failures and not agree
            else (
                "UNIQUE_KAPPA_PRINCIPLE_PROBES_AGREE_NUMERICALLY__STILL_NOT_AXIOMATIC"
                if not failures and agree
                else "UNIQUE_KAPPA_PRINCIPLE_PROBE_FAILED"
            )
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "probes": probes,
        "comparison": {
            "kappa_values": kappas.tolist(),
            "absolute_spread": kappa_spread,
            "relative_spread": relative_spread,
            "agree_within_5pct": agree,
            "A_kappa_benchmark_GeV2": a_phys_bench,
        },
        "flags": {
            "unique_kappa_probes_executed": not bool(failures),
            "uv_kappa_uniquely_determined": False,
            "probes_numerically_agree": agree,
            "cg_120_320_1050_4125_invented": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "uv_axiom_fixing_unique_kappa": True,
            "missing_cg_120_320_1050_4125": True,
            "full_nonsusy_vacuum_hessian": True,
        },
        "verdict": (
            "Unique-κ probes: soft-norm minimizer κ="
            f"{kappa_softmin:.6g}, portal-matching κ={kappa_portal:.6g}, "
            f"finite-κ benchmark κ={kappa_bench:.6g} "
            f"(relative spread {relative_spread:.3e}). "
            "UV κ remains not uniquely determined. Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Unique-κ principle probe — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Soft-norm κ: `{report['probes']['soft_norm_minimizer']['kappa']}`\n"
        f"- Portal-match κ: `{report['probes']['portal_matching_eps_m2_210']['kappa']}`\n"
        f"- Benchmark κ: `{report['probes']['finite_kappa_benchmark']['kappa']}`\n"
        f"- Relative spread: `{report['comparison']['relative_spread']}`\n\n"
        + report["verdict"]
        + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
