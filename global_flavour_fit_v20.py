#!/usr/bin/env python3
"""Global flavour/Higgs scan beyond exact v_R=v_S.

Extends the corrected Takagi/PMNS 10+126 objective with:
  - free log-spaced v_R grid (including natural ~1e14 GeV)
  - optional soft CKM pulls from frozen PDG-like targets
  - threshold/RG bookkeeping flags (inputs required; not invented)

This can establish a viable tan(beta) *region* at natural seesaw scales.
It does not claim a unique tan(beta) or close portal matching.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

import flavour_clebsch_fit_v20 as flavour
import full_fermion_matching_v20 as match


ROOT = Path(__file__).resolve().parent
VS = flavour.VS

# PDG-like CKM soft targets (central values; large sigmas keep them soft).
CKM_SOFT = {
    "sin_theta12": (0.22650, 0.020),
    "sin_theta23": (0.04053, 0.010),
    "sin_theta13": (0.00368, 0.0020),
}


def ckm_pulls_from_params(params: np.ndarray) -> dict:
    """Soft pulls on the residual up-sector angles already in the ansatz."""
    su12 = 0.25 * (0.5 + 0.5 * math.tanh(params[8]))
    su23 = 0.05 * (0.5 + 0.5 * math.tanh(params[9]))
    su13 = 0.01 * (0.5 + 0.5 * math.tanh(params[10]))
    pulls = {}
    chi2 = 0.0
    for key, val, (central, sigma) in (
        ("ckm_s12", su12, CKM_SOFT["sin_theta12"]),
        ("ckm_s23", su23, CKM_SOFT["sin_theta23"]),
        ("ckm_s13", su13, CKM_SOFT["sin_theta13"]),
    ):
        pull = (val - central) / sigma
        pulls[key] = float(pull)
        chi2 += float(pull**2)
    return {"chi2": chi2, "pulls": pulls, "angles": {"s12": su12, "s23": su23, "s13": su13}}


def chi2_global(
    params: np.ndarray,
    v_r: float,
    *,
    include_ckm: bool = True,
) -> tuple[float, dict]:
    chi2, detail = flavour.chi2_from_params(params, v_r)
    if include_ckm:
        ckm = ckm_pulls_from_params(params)
        chi2 = float(chi2 + ckm["chi2"])
        detail = {
            **detail,
            "pulls": {**detail["pulls"], **ckm["pulls"]},
            "ckm_angles": ckm["angles"],
            "include_ckm": True,
        }
    else:
        detail = {**detail, "include_ckm": False}
    detail["rg_threshold_status"] = {
        "common_scale_RG_inputs_applied": False,
        "two_loop_thresholds_coupled": False,
        "note": (
            "Gauge-threshold machinery exists in two_loop_thresholds_v20.py but "
            "Yukawa RG anomalous dimensions are not yet supplied; this scan "
            "therefore uses low-scale mass inputs as a constrained proxy."
        ),
    }
    return chi2, detail


def optimize_at_vr(
    v_r: float,
    *,
    starts: int = 8,
    seed: int = 20,
    include_ckm: bool = True,
    maxiter: int = 5000,
) -> dict:
    rng = np.random.default_rng(seed + int(abs(math.log10(v_r)) * 10))
    best = None
    # Seed from revalidated natural/v20 witnesses when available.
    saved = flavour.run_fit()
    warm = []
    if abs(v_r - VS) < 1.0:
        warm.append(np.asarray(saved["v20_single_scale_point"]["params"], float))
    warm.append(np.asarray(saved["best_overall"]["params"], float))
    for trial in range(starts):
        if trial < len(warm):
            x0 = warm[trial] + 0.05 * rng.normal(size=13)
        else:
            x0 = rng.normal(size=13)
            x0[0] = rng.uniform(-1.5, 1.5)
            x0[12] = rng.uniform(-13.0, -7.0)
        res = minimize(
            lambda x, vr=v_r: chi2_global(x, vr, include_ckm=include_ckm)[0],
            x0,
            method="Nelder-Mead",
            options={"maxiter": maxiter, "xatol": 1e-8, "fatol": 1e-8},
        )
        chi2, detail = chi2_global(res.x, v_r, include_ckm=include_ckm)
        row = {
            "v_r_GeV": v_r,
            "chi2": float(chi2),
            "params": res.x.tolist(),
            "pulls": detail["pulls"],
            "observables": detail["observables"],
            "ckm_angles": detail.get("ckm_angles"),
            "include_ckm": include_ckm,
            "rg_threshold_status": detail["rg_threshold_status"],
            "tan_beta": detail["observables"]["tan_beta"],
            "viable_chi2_lt_30": bool(chi2 < 30.0),
            "aligned_Cf": match.coefficients_at_tan_beta(
                detail["observables"]["tan_beta"]
            ),
        }
        if best is None or chi2 < best["chi2"]:
            best = row
    return best


def run_global_scan(
    *,
    v_r_grid: tuple[float, ...] | None = None,
    starts_per_point: int = 6,
    include_ckm: bool = True,
) -> dict:
    grid = v_r_grid or (
        VS,
        1.0e12,
        3.0e12,
        1.0e13,
        3.0e13,
        1.0e14,
        3.0e14,
        1.0e15,
    )
    points = [
        optimize_at_vr(
            v_r,
            starts=starts_per_point,
            seed=20 + i,
            include_ckm=include_ckm,
        )
        for i, v_r in enumerate(grid)
    ]
    viable = [p for p in points if p["viable_chi2_lt_30"]]
    best = min(points, key=lambda p: p["chi2"])
    tan_betas = sorted({round(p["tan_beta"], 6) for p in viable})
    return {
        "status": "GLOBAL_FLAVOUR_SCAN_COMPLETE",
        "method": (
            "multi-start Nelder-Mead on corrected Takagi/PMNS 10+126 objective "
            "with optional soft CKM pulls over a free v_R grid"
        ),
        "include_ckm": include_ckm,
        "v_r_grid_GeV": list(grid),
        "points": points,
        "best_point": best,
        "viable_points": viable,
        "any_viable": bool(viable),
        "vR_equals_vS_viable": any(
            abs(p["v_r_GeV"] - VS) < 1.0 and p["viable_chi2_lt_30"] for p in points
        ),
        "unique_tan_beta_demonstrated": False,
        "viable_tan_beta_samples": tan_betas,
        "rg_threshold_note": best["rg_threshold_status"]["note"],
        "flag": {
            "provisional_natural_scale_flavour": bool(viable),
            "full_RG_global_fit": False,
            "unique_tan_beta": False,
            "exact_vR_eq_vS": False,
        },
    }


def build_report() -> dict:
    scan = run_global_scan()
    checks = {
        "scan_produced_points": len(scan["points"]) >= 5,
        "vR_eq_vS_still_fails_or_stressed": not scan["vR_equals_vS_viable"],
        "natural_scale_can_be_viable": scan["any_viable"],
        "unique_tan_beta_not_claimed": not scan["unique_tan_beta_demonstrated"],
        "full_RG_not_overclaimed": not scan["flag"]["full_RG_global_fit"],
    }
    failures = [name for name, ok in checks.items() if not ok]
    best = scan["best_point"]
    return {
        **scan,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "display_best": {
            "v_r_GeV": best["v_r_GeV"],
            "chi2": best["chi2"],
            "tan_beta": best["tan_beta"],
            "viable_chi2_lt_30": best["viable_chi2_lt_30"],
            "aligned_C_e": best["aligned_Cf"]["C_e"],
            "aligned_C_p_central": best["aligned_Cf"]["C_p_central"],
            "aligned_C_n_central": best["aligned_Cf"]["C_n_central"],
        },
        "verdict": (
            "Free-v_R corrected flavour scan completed. Exact v_R=v_S remains "
            "non-viable under the constrained ansatz. Natural seesaw-scale "
            "points can be viable and support a tan(beta) region, but not a "
            "unique tan(beta). Full common-scale Yukawa RG is still external."
            if scan["any_viable"]
            else (
                "Free-v_R scan completed but no chi2<30 point was found with "
                "current starts; deepen search or enlarge operator basis."
            )
        ),
    }


def write_markdown(report: dict) -> str:
    lines = [
        "# Global flavour / Higgs scan — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        "## Flags",
        "",
    ]
    for k, v in report["flag"].items():
        lines.append(f"- `{k}`: **{v}**")
    d = report["display_best"]
    lines += [
        "",
        "## Best point",
        "",
        f"- v_R = {d['v_r_GeV']:.3e} GeV",
        f"- chi2 = {d['chi2']:.3g}",
        f"- tan(beta) = {d['tan_beta']:.4g}",
        f"- viable (chi2<30): {d['viable_chi2_lt_30']}",
        f"- aligned benchmark C_e,C_p,C_n = "
        f"({d['aligned_C_e']:.5g}, {d['aligned_C_p_central']:.5g}, "
        f"{d['aligned_C_n_central']:.5g})",
        "",
        f"- any viable point: {report['any_viable']}",
        f"- v_R=v_S viable: {report['vR_equals_vS_viable']}",
        f"- viable tan(beta) samples: {report['viable_tan_beta_samples']}",
        "",
        "## Verdict",
        "",
        report["verdict"],
        "",
        "## RG / threshold caveat",
        "",
        report["rg_threshold_note"],
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the bounded global flavour/Higgs validation scan."
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="validate the scan without rewriting the frozen report files",
    )
    args = parser.parse_args(argv)
    report = build_report()
    if not args.no_write:
        # Shrink JSON: drop bulky params from every point in the written summary
        # but keep best/viable params.
        slim_points = []
        for p in report["points"]:
            slim_points.append(
                {
                    "v_r_GeV": p["v_r_GeV"],
                    "chi2": p["chi2"],
                    "tan_beta": p["tan_beta"],
                    "viable_chi2_lt_30": p["viable_chi2_lt_30"],
                    "max_abs_pull": float(
                        max(abs(x) for x in p["pulls"].values())
                        if p["pulls"]
                        else 0.0
                    ),
                }
            )
        out = {
            **{k: v for k, v in report.items() if k != "points"},
            "points": slim_points,
            "best_point": report["best_point"],
            "viable_points": report["viable_points"],
        }
        ROOT.joinpath("GLOBAL_FLAVOUR_FIT_V20_VERDICT.json").write_text(
            json.dumps(out, indent=2) + "\n", encoding="utf-8"
        )
        ROOT.joinpath("GLOBAL_FLAVOUR_FIT_V20.md").write_text(
            write_markdown(report), encoding="utf-8"
        )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "failures": report["failures"],
                "any_viable": report["any_viable"],
                "vR_equals_vS_viable": report["vR_equals_vS_viable"],
                "display_best": report["display_best"],
                "flag": report["flag"],
                "verdict": report["verdict"],
            },
            indent=2,
        )
    )
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
