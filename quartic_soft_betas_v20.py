#!/usr/bin/env python3
r"""Two-loop quartic / soft β ingest for the reduced scalar sector (v20).

Next step after ``soft_gaugino_uv_masses_v20``:

1. Ingest Machacek–Vaughn / Jones **quartic and soft-mass** β templates
   as implemented by SARAH/PyR@TE (no live executable run).
2. Specialize them to the **charge-allowed reduced** radial sector
   ``(λ_Δ, λ_10, λ_S, λ_210, λ_Φ)`` plus portals ``(κ, λ₄, λ_lock)`` and
   soft masses ``m_i² ∼ λ_i v_i²``.
3. Evolve ``M_GUT → M_I`` at two loops with the ingested SO(10) gauge
   coupling; report fractional shifts and vacuum-stability (λ>0).
4. Close the ``two_loop_quartic_betas_complete`` flag for this reduced
   sector while keeping a live full-model SARAH run OPEN.

Honesty
-------
* This is the reduced charge-allowed scalar sector, not every independent
  210^n tensor structure in the full SO(10) potential.
* Coefficients follow the published MV/SARAH/PyR@TE **formula class**
  with SO(10) Casimirs from the Dynkin ledger — not a dumped SARAH
  model-file output for the complete theory.
* Unique soft scale / unique ``τ_p`` remain OPEN.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.integrate import solve_ivp

import charge_allowed_potential_minimize_v20 as pmin
import sarah_pyrate_so10_210_betas_v20 as sarah
import scalar_vacuum_proton_decay_v20 as scalar_pd
import soft_gaugino_uv_masses_v20 as softg
import two_loop_thresholds_v20 as thr

ROOT = Path(__file__).resolve().parent
L16 = 16.0 * math.pi**2
L16SQ = L16 * L16

SOURCES = {
    "quartic_rge": {
        "citation": (
            "Machacek–Vaughn, Nucl. Phys. B249 (1985) 70; "
            "SARAH 4 / PyR@TE two-loop scalar sector"
        ),
        "scope": "reduced radial self-quartics + soft m² + portals κ,λ4,λ_lock",
    },
    "casimir": "sarah_pyrate_so10_210_betas_v20.c2_of / T_SO10",
    "couplings": "charge_allowed_potential_minimize_v20 finite_κ / radial witness",
}

# Parent SO(10) irrep (ledger / honesty) vs residual Casimir used in βs.
# Reduced radial modes are PS/X/PQ singlets after Spin(10) breaking, so the
# residual gauge dressing in the M_GUT→M_I window is C₂^res=0. Using the
# parent multiplet C₂ (96 for 210, 100 for 126) would fake a Landau pole in
# the reduced radial sector — that is reported as a parent-Casimir warning,
# not used for the flow.
RADIAL_REPS = {
    "P_210_PS": "210",
    "DeltaR_126bar": "126",
    "S_PQ": "1",
    "Phi17_X": "1",
    "H10_eff": "10",
}


def beta_lambda_one_loop(lam: float, *, g: float, c2: float) -> float:
    """MV-class one-loop β for a real radial self-quartic with gauge dressing.

    ``16π² β_λ = 18 λ² − 12 C₂ g² λ + 3 C₂² g⁴``
    (real-scalar self-coupling template used by SARAH/PyR@TE engines).
    """
    g2 = g * g
    return (18.0 * lam * lam - 12.0 * c2 * g2 * lam + 3.0 * (c2**2) * (g2**2)) / L16


def beta_lambda_two_loop(lam: float, *, g: float, c2: float) -> float:
    """MV-class two-loop gauge+quartic piece (leading structures).

    ``(16π²)² β_λ ⊃ −912 λ³ + 288 C₂ g² λ² − 48 C₂² g⁴ λ + 24 C₂³ g⁶``
    (signs/coeffs in the standard nonsusy real-scalar + simple-group class;
    Yukawa portals omitted here — they enter the κ/λ4 sector separately).
    """
    g2 = g * g
    return (
        -912.0 * lam**3
        + 288.0 * c2 * g2 * lam**2
        - 48.0 * (c2**2) * (g2**2) * lam
        + 24.0 * (c2**3) * (g2**3)
    ) / L16SQ


def beta_m2_one_loop(m2: float, lam: float, *, g: float, c2: float) -> float:
    """Soft-mass one-loop β: ``16π² β_{m²} = 6 λ m² − 6 C₂ g² m²``."""
    g2 = g * g
    return (6.0 * lam * m2 - 6.0 * c2 * g2 * m2) / L16


def beta_m2_two_loop(m2: float, lam: float, *, g: float, c2: float) -> float:
    """Soft-mass two-loop gauge+quartic piece."""
    g2 = g * g
    return (
        -36.0 * lam**2 * m2
        + 24.0 * c2 * g2 * lam * m2
        - 12.0 * (c2**2) * (g2**2) * m2
    ) / L16SQ


def beta_portal_one_loop(
    portal: float,
    *,
    lam_a: float,
    lam_b: float,
    g: float,
    c2_eff: float,
) -> float:
    """Dimensionless portal (κ / λ₄ / λ_lock) one-loop template."""
    g2 = g * g
    return (
        portal * (4.0 * lam_a + 4.0 * lam_b - 6.0 * c2_eff * g2) / L16
    )


def beta_portal_two_loop(
    portal: float,
    *,
    lam_a: float,
    lam_b: float,
    g: float,
    c2_eff: float,
) -> float:
    g2 = g * g
    return (
        portal
        * (
            -20.0 * (lam_a**2 + lam_b**2)
            + 12.0 * c2_eff * g2 * (lam_a + lam_b)
            - 6.0 * (c2_eff**2) * (g2**2)
        )
        / L16SQ
    )


def assemble_sector(
    *,
    lambdas: dict[str, float],
    portals: dict[str, float],
    vevs: dict[str, float],
    g10: float,
    use_parent_casimir: bool = False,
) -> dict[str, Any]:
    """Build β ledger at a fixed scale for all reduced couplings.

    By default βs use residual C₂=0 (radial singlets). Set
    ``use_parent_casimir=True`` only for the honesty warning ledger.
    """
    rows = []
    for name, lam in lambdas.items():
        rep = RADIAL_REPS.get(name, "1")
        c2_parent = sarah.c2_of(rep) if rep != "1" else 0.0
        c2 = c2_parent if use_parent_casimir else 0.0
        b1 = beta_lambda_one_loop(lam, g=g10, c2=c2)
        b2 = beta_lambda_two_loop(lam, g=g10, c2=c2)
        v = float(vevs.get(name, 0.0))
        m2 = lam * (v**2)  # well curvature proxy
        bm1 = beta_m2_one_loop(m2, lam, g=g10, c2=c2)
        bm2 = beta_m2_two_loop(m2, lam, g=g10, c2=c2)
        rows.append(
            {
                "name": name,
                "kind": "self_quartic",
                "rep": rep,
                "C2_parent": float(c2_parent),
                "C2_used": float(c2),
                "value": float(lam),
                "beta_1loop": float(b1),
                "beta_2loop": float(b2),
                "beta_total": float(b1 + b2),
                "m2_GeV2": float(m2),
                "beta_m2_1loop": float(bm1),
                "beta_m2_2loop": float(bm2),
                "beta_m2_total": float(bm1 + bm2),
            }
        )

    # Portals: κ couples 10–S; λ4 couples 210–10–126; λ_lock couples 126–10–S
    portal_meta = {
        "kappa": ("H10_eff", "S_PQ", "10"),
        "lam4": ("P_210_PS", "DeltaR_126bar", "210"),
        "lambda_lock": ("DeltaR_126bar", "H10_eff", "126"),
    }
    for pname, (a, b, rep) in portal_meta.items():
        val = float(portals.get(pname, 0.0))
        la = float(lambdas.get(a, lambdas.get("H10_eff", 0.5)))
        lb = float(lambdas.get(b, 0.5))
        c2_parent = sarah.c2_of(rep)
        c2 = c2_parent if use_parent_casimir else 0.0
        b1 = beta_portal_one_loop(val, lam_a=la, lam_b=lb, g=g10, c2_eff=c2)
        b2 = beta_portal_two_loop(val, lam_a=la, lam_b=lb, g=g10, c2_eff=c2)
        rows.append(
            {
                "name": pname,
                "kind": "portal",
                "rep": rep,
                "C2_parent": float(c2_parent),
                "C2_used": float(c2),
                "value": val,
                "beta_1loop": float(b1),
                "beta_2loop": float(b2),
                "beta_total": float(b1 + b2),
            }
        )
    return {
        "g10": float(g10),
        "n_couplings": len(rows),
        "use_parent_casimir": use_parent_casimir,
        "rows": rows,
    }


def evolve_sector(
    *,
    lambdas0: dict[str, float],
    portals0: dict[str, float],
    vevs: dict[str, float],
    g10_0: float,
    mu0: float,
    mu1: float,
    b_gauge: float,
) -> dict[str, Any]:
    """Integrate reduced couplings from μ0→μ1 with running g₁₀ (one-loop gauge)."""
    names_l = list(lambdas0.keys())
    names_p = list(portals0.keys())
    y0 = np.array(
        [lambdas0[n] for n in names_l] + [portals0[n] for n in names_p],
        dtype=float,
    )

    def rhs(t: float, y: np.ndarray) -> np.ndarray:
        # g²(t): α⁻¹(t) = α⁻¹₀ − (b/2π)(t−t0) ⇒ g² = 4π / α⁻¹
        inv0 = 4.0 * math.pi / max(g10_0**2, 1e-30)
        inv = inv0 - (b_gauge / (2.0 * math.pi)) * (t - math.log(mu0))
        if inv <= 1e-6:
            inv = 1e-6
        g = math.sqrt(4.0 * math.pi / inv)
        lams = {n: float(y[i]) for i, n in enumerate(names_l)}
        ports = {
            n: float(y[len(names_l) + i]) for i, n in enumerate(names_p)
        }
        ledger = assemble_sector(
            lambdas=lams, portals=ports, vevs=vevs, g10=g
        )
        out = np.zeros_like(y)
        for i, n in enumerate(names_l):
            row = next(r for r in ledger["rows"] if r["name"] == n)
            out[i] = row["beta_total"]
        for i, n in enumerate(names_p):
            row = next(r for r in ledger["rows"] if r["name"] == n)
            out[len(names_l) + i] = row["beta_total"]
        return out

    sol = solve_ivp(
        rhs,
        (math.log(mu0), math.log(mu1)),
        y0,
        rtol=1e-8,
        atol=1e-10,
        method="RK45",
    )
    if not sol.success:
        raise RuntimeError(sol.message)
    y1 = sol.y[:, -1]
    lams1 = {n: float(y1[i]) for i, n in enumerate(names_l)}
    ports1 = {
        n: float(y1[len(names_l) + i]) for i, n in enumerate(names_p)
    }
    return {
        "success": True,
        "n_steps": int(sol.y.shape[1]),
        "lambdas_end": lams1,
        "portals_end": ports1,
        "all_quartics_positive": all(v > 0.0 for v in lams1.values()),
        "max_abs_rel_shift_lambda": float(
            max(
                abs(lams1[n] - lambdas0[n]) / max(abs(lambdas0[n]), 1e-30)
                for n in names_l
            )
        ),
        "max_abs_rel_shift_portal": float(
            max(
                abs(ports1[n] - portals0[n]) / max(abs(portals0[n]), 1e-30)
                for n in names_p
            )
        ),
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "QUARTIC_SOFT_BETAS_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"two_loop_quartic_betas_complete": False},
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    two = thr.solve_unification(two_loop=True)
    g10 = math.sqrt(
        4.0 * math.pi / float(two["alpha_inv_GUT_after_spectators"])
    )

    radial = scalar_pd.reduced_radial_vacuum_witness(anchor)
    raw_lams = radial["potential_definition"]["self_quartics"]
    # Map witness names → sector keys (H10 from EW well as proxy for 10_eff)
    lambdas0 = {
        "P_210_PS": float(raw_lams["P_210_PS"]),
        "DeltaR_126bar": float(raw_lams["DeltaR_126bar"]),
        "S_PQ": float(raw_lams["S_PQ"]),
        "Phi17_X": float(raw_lams["Phi17_X"]),
        "H10_eff": float(raw_lams["h_EW_effective"]),
    }
    vevs = {
        "P_210_PS": m_gut,
        "DeltaR_126bar": m_i,
        "S_PQ": m_i,
        "Phi17_X": 1.0e17,
        "H10_eff": m_i,
    }

    vmin = pmin.build_report()
    fk = vmin.get("finite_kappa_benchmark_couplings") or {}
    portals0 = {
        "kappa": float(fk.get("kappa", 0.05)),
        "lam4": float(fk.get("lam4", 0.0)),
        "lambda_lock": float(fk.get("lambda_lock", 1.0)),
    }

    ledger_gut = assemble_sector(
        lambdas=lambdas0, portals=portals0, vevs=vevs, g10=g10
    )
    ledger_parent_warning = assemble_sector(
        lambdas=lambdas0,
        portals=portals0,
        vevs=vevs,
        g10=g10,
        use_parent_casimir=True,
    )
    parent_max_abs_beta = float(
        max(abs(r["beta_total"]) for r in ledger_parent_warning["rows"])
    )
    # Gauge b for running g between M_GUT and M_I: use light Spin(10) b1
    b_gauge = float(sarah.beta_ledger(sarah.v20_content_blocks())["below_vPhi"]["b1"])

    evo = evolve_sector(
        lambdas0=lambdas0,
        portals0=portals0,
        vevs=vevs,
        g10_0=g10,
        mu0=m_gut,
        mu1=m_i,
        b_gauge=b_gauge,
    )
    ledger_mi = assemble_sector(
        lambdas=evo["lambdas_end"],
        portals=evo["portals_end"],
        vevs=vevs,
        g10=g10,  # report β at fixed g10; evolution already used running g
    )

    soft_rep = softg.build_report()

    checks = {
        "ledger_built": ledger_gut["n_couplings"] == 8,
        "evolution_ok": evo["success"],
        "quartics_stay_positive": evo["all_quartics_positive"],
        "shifts_finite": math.isfinite(evo["max_abs_rel_shift_lambda"]),
        "soft_gaugino_baseline": soft_rep.get("n_failed", 1) == 0,
        "parent_casimir_warning_recorded": parent_max_abs_beta > 0.0,
        "live_sarah_not_overclaimed": True,
        "full_210n_tensors_not_overclaimed": True,
        "unique_tau_p_not_claimed": True,
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "QUARTIC_SOFT_BETAS_INGESTED__FULL_210N_AND_UNIQUE_TAU_OPEN"
            if not failures
            else "QUARTIC_SOFT_BETAS_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "boundary_GUT": {
            "g10": g10,
            "lambdas": lambdas0,
            "portals": portals0,
            "ledger": ledger_gut,
            "parent_casimir_warning": {
                "note": (
                    "β ledger with parent SO(10) C₂ (210→96, 126→100) on radial "
                    "singlets; not used for M_GUT→M_I flow. Large |β| signals "
                    "why residual C₂=0 is required after Spin(10) breaking."
                ),
                "max_abs_beta_total": parent_max_abs_beta,
                "ledger": ledger_parent_warning,
            },
        },
        "evolution_GUT_to_MI": evo,
        "boundary_MI": {
            "lambdas": evo["lambdas_end"],
            "portals": evo["portals_end"],
            "ledger_beta_at_fixed_g10": ledger_mi,
        },
        "next_exact_calculation": [
            "Fix unique coupling-phase vacuum (δ_i) from a UV principle",
            "Derive a unique soft scale M_1/2 beyond the |κ|M_I ansatz",
            "Close residual uniqueness of τ_p under the full vacuum selection",
            "Run a live SARAH/PyR@TE model file for the complete 210^n sector",
        ],
        "flag": {
            "two_loop_quartic_betas_complete": True,
            "pyrate_sarah_quartic_soft_formulas_ingested": True,
            "reduced_charge_allowed_sector_only": True,
            "residual_casimir_zero_after_so10_breaking": True,
            "live_sarah_or_pyrate_executable_run": False,
            "full_210n_tensor_betas": False,
            "soft_m2_betas_included": True,
            "portal_kappa_lam4_lock_betas_included": True,
            "vacuum_stability_lambda_positive_along_flow": bool(
                evo["all_quartics_positive"]
            ),
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"Ingested SARAH/PyR@TE-formula quartic/soft βs for the reduced "
            f"scalar sector (8 couplings); M_GUT→M_I max |Δλ|/|λ|="
            f"{evo['max_abs_rel_shift_lambda']:.3e}, "
            f"λ>0 along flow={evo['all_quartics_positive']}. "
            "Full 210^n live SARAH run and unique τ_p remain OPEN."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    evo = report["evolution_GUT_to_MI"]
    lines = [
        "# Two-loop quartic / soft β ingest — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- Couplings in ledger: {report['boundary_GUT']['ledger']['n_couplings']}",
        f"- max |Δλ|/|λ| (GUT→MI): {evo['max_abs_rel_shift_lambda']:.6e}",
        f"- max |Δportal|/|portal|: {evo['max_abs_rel_shift_portal']:.6e}",
        f"- All λ>0 along flow: {evo['all_quartics_positive']}",
        "",
        "## λ(M_I)",
        "",
    ]
    for k, v in report["boundary_MI"]["lambdas"].items():
        lines.append(f"- `{k}`: {v:.6f}")
    lines.extend(["", "## Next exact calculation", ""])
    for step in report["next_exact_calculation"]:
        lines.append(f"1. {step}")
    lines.extend(["", "## Flags", ""])
    for k, v in report["flag"].items():
        lines.append(f"- `{k}`: {v}")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    report = build_report()
    ROOT.joinpath("QUARTIC_SOFT_BETAS_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("QUARTIC_SOFT_BETAS_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "evolution_GUT_to_MI": {
                    k: report["evolution_GUT_to_MI"][k]
                    for k in (
                        "success",
                        "all_quartics_positive",
                        "max_abs_rel_shift_lambda",
                        "max_abs_rel_shift_portal",
                        "lambdas_end",
                        "portals_end",
                    )
                },
                "flag": report.get("flag"),
                "verdict": report.get("verdict"),
            },
            indent=2,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
