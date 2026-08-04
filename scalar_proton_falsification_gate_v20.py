#!/usr/bin/env python3
"""Fail-closed full-scalar/p→e+π0 gate for the SO(10)×Z17 v20 candidate.

The code never invents missing SO(10) tensors.  Missing invariant bases,
stationarity solutions, physical Hessians, Goldstones, competing vacua, X/Y
masses, or colour-triplet mixings are BLOCKED.  Explicit tachyons, a wrong
Goldstone count, a lower competing vacuum, or a certified proton lifetime below
the limit are FAIL.  Gauge and triplet proxy scans are reported as conditional.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data" / "scalar_proton_falsification_inputs_v20.json"
OUT_JSON = ROOT / "SCALAR_PROTON_FALSIFICATION_GATE_V20.json"
OUT_MD = ROOT / "SCALAR_PROTON_FALSIFICATION_GATE_V20.md"
HBAR_GEV_S = 6.582119569e-25
SEC_PER_YR = 365.25 * 24 * 3600
MP, MPI0 = 0.9382720813, 0.1349768


def finite(x):
    return isinstance(x, (int, float)) and math.isfinite(float(x))


def positive(x):
    return finite(x) and float(x) > 0


def sha(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def load_record(path=INPUT):
    r = json.loads(Path(path).read_text(encoding="utf-8"))
    for key in ("unification_anchor", "scalar_completion", "proton_decay"):
        if key not in r:
            raise ValueError(f"missing {key}")
    a = r["unification_anchor"]
    if not all(positive(a.get(k)) for k in ("M_I_GeV", "M_GUT_GeV", "alpha_inv_GUT")):
        raise ValueError("invalid unification anchor")
    if a["M_I_GeV"] >= a["M_GUT_GeV"]:
        raise ValueError("M_I must be below M_GUT")
    if not positive(r["proton_decay"].get("p_to_e_pi0_limit_years")):
        raise ValueError("invalid proton lifetime limit")
    return r


def scalar_gate(record):
    s = record["scalar_completion"]
    fail, block = [], []
    inv = s.get("declared_independent_invariants", [])
    expected = s.get("expected_independent_invariant_count")
    if not s.get("external_invariant_basis_reference"):
        block.append("external invariant-basis reference is missing")
    if not s.get("invariant_basis_sha256"):
        block.append("invariant-basis SHA-256 certificate is missing")
    if expected is None:
        block.append("externally certified invariant count is missing")
    elif not isinstance(expected, int) or expected <= 0 or len(inv) != expected:
        fail.append("declared invariant ledger does not match certified count")
    if not inv:
        block.append("independent invariant ledger is empty")
    elif len(set(map(str, inv))) != len(inv):
        fail.append("invariant ledger contains duplicates")
    elif s.get("invariant_basis_sha256") and sha(inv) != s["invariant_basis_sha256"]:
        fail.append("invariant ledger hash mismatch")

    residual, tol = s.get("stationarity_residual_inf"), s.get("stationarity_tolerance", 1e-10)
    if residual is None:
        block.append("vacuum stationarity equations have not been solved")
    elif not finite(residual) or residual < 0 or not positive(tol) or residual > tol:
        fail.append("stationarity residual fails tolerance")

    h = s.get("physical_hessian_eigenvalues_GeV2", [])
    if not h:
        block.append("full physical component Hessian is missing")
    elif not all(finite(x) and x > 0 for x in h):
        fail.append("physical Hessian contains a tachyon/non-finite eigenvalue")

    ge, gf = s.get("goldstone_count_expected"), s.get("goldstone_count_found")
    if ge is None or gf is None:
        block.append("Goldstone count has not been demonstrated")
    elif not isinstance(ge, int) or not isinstance(gf, int) or ge != gf:
        fail.append(f"Goldstone mismatch: expected {ge}, found {gf}")

    bounded = s.get("bounded_from_below_certificate")
    if bounded is None:
        block.append("bounded-from-below certificate is missing")
    elif bounded is not True:
        fail.append("potential is not certified bounded from below")

    target, competitors = s.get("target_vacuum_energy_GeV4"), s.get("competing_vacua_energies_GeV4", [])
    if target is None or not competitors:
        block.append("competing-vacuum comparison is missing")
    elif not finite(target) or not all(finite(x) for x in competitors):
        fail.append("vacuum energies are non-finite")
    elif target >= min(competitors):
        fail.append("desired vacuum is not below every supplied competitor")

    xy = s.get("xy_mass_eigenvalues_GeV", [])
    if not xy:
        block.append("physical X/Y gauge-boson masses are missing")
    elif not all(positive(x) for x in xy):
        fail.append("X/Y spectrum contains an invalid mass")

    triplets = s.get("color_triplet_states", [])
    if not triplets:
        block.append("physical colour-triplet mass/mixing spectrum is missing")
    elif any(not positive(t.get("mass_GeV")) or not finite(t.get("effective_yukawa")) for t in triplets):
        fail.append("colour-triplet spectrum has invalid mass/coupling entries")

    state = "FAIL" if fail else ("BLOCKED" if block else "PASS")
    return {"state": state, "failures": fail, "blockers": block, "claim_allowed": state == "PASS"}


def gauge_lifetime(mx, alpha_inv, ar, w, vud):
    if not all(positive(x) for x in (mx, alpha_inv, ar, w, vud)):
        raise ValueError("invalid gauge-decay input")
    alpha = 1 / alpha_inv
    kin = (1 - (MPI0 / MP) ** 2) ** 2
    c = 4 * math.pi * alpha / mx**2
    flavour = 1 + (1 + vud**2) ** 2
    width = MP / (32 * math.pi) * kin * c**2 * ar**2 * w**2 * flavour
    return HBAR_GEV_S / width / SEC_PER_YR


def proton_gate(record):
    a, p = record["unification_anchor"], record["proton_decay"]
    mg, ai, limit = a["M_GUT_GeV"], a["alpha_inv_GUT"], p["p_to_e_pi0_limit_years"]
    central = gauge_lifetime(mg, ai, p["central_A_R"], p["central_hadronic_W_GeV2"], p["V_ud"])
    grid = []
    for f in p["M_X_over_M_GUT_scan"]:
        for ar in p["A_R_scan"]:
            for w in p["hadronic_W_scan_GeV2"]:
                t = gauge_lifetime(mg * f, ai, ar, w, p["V_ud"])
                grid.append({"M_X_over_M_GUT": f, "A_R": ar, "W_GeV2": w, "lifetime_years": t, "passes": t >= limit})

    g = math.sqrt(4 * math.pi / ai)
    available = central / limit - 1
    kill = []
    excluded = 0
    for y in p["effective_yukawa_scan"]:
        mcrit = math.inf if available <= 0 else abs(y) / g * mg / available**0.25
        kill.append({"effective_yukawa": y, "minimum_triplet_mass_GeV_proxy": mcrit})
        for mt in p["triplet_mass_scan_GeV"]:
            ratio = (abs(y) / g * mg / mt) ** 4
            excluded += central / (1 + ratio) < limit

    exact_ok = bool(p.get("exact_operator_running_hadronic_matching"))
    exact_tau = p.get("exact_combined_channel_lifetime_years")
    exact_valid = exact_ok and positive(exact_tau)
    exact_fail = exact_valid and exact_tau < limit
    state = "FAIL" if exact_fail else ("PASS" if exact_valid else "BLOCKED")
    return {
        "state": state,
        "central": {"lifetime_years": central, "margin_over_limit": central / limit, "passes": central >= limit},
        "gauge_scan": {"points": len(grid), "minimum": min(grid, key=lambda x: x["lifetime_years"]), "all_pass": all(x["passes"] for x in grid)},
        "critical_M_X_over_M_GUT_central": (limit / central) ** 0.25,
        "triplet_kill_curve": kill,
        "conditional_triplet_points_excluded": int(excluded),
        "exact_lifetime_years": exact_tau,
        "exact_calculation_completed": exact_valid,
        "model_excluded": bool(exact_fail),
    }


def build_report(record):
    s, p = scalar_gate(record), proton_gate(record)
    overall = "FAIL" if "FAIL" in (s["state"], p["state"]) else ("BLOCKED" if "BLOCKED" in (s["state"], p["state"]) else "PASS")
    return {
        "status": "SCALAR_AND_PROTON_FALSIFICATION_GATE_EXECUTED",
        "input_sha256": sha(record),
        "overall_state": overall,
        "scalar_potential": s,
        "proton_decay": p,
        "hard_findings": {
            "full_scalar_potential_completed": s["state"] == "PASS",
            "central_gauge_benchmark_passes": p["central"]["passes"],
            "broad_gauge_scan_fully_passes": p["gauge_scan"]["all_pass"],
            "conditional_triplet_points_excluded": p["conditional_triplet_points_excluded"],
            "whole_model_excluded": p["model_excluded"] or s["state"] == "FAIL",
            "whole_model_validated": overall == "PASS",
        },
        "verdict": "Current v20 inputs do not close the complete SO(10) scalar potential or a unique proton-decay prediction. Conditional kill surfaces are computed; missing tensor-level inputs remain BLOCKED, not passed.",
    }


def markdown(r):
    s, p = r["scalar_potential"], r["proton_decay"]
    w = p["gauge_scan"]["minimum"]
    lines = [
        "# Scalar-potential and proton-decay falsification gate — v20", "",
        f"**Overall state:** `{r['overall_state']}`", "", "## Executed result", "",
        f"- Full scalar-potential closure: `{s['state']}`",
        f"- Exact proton-decay closure: `{p['state']}`",
        f"- Central M_X=M_GUT lifetime: `{p['central']['lifetime_years']:.6e}` yr",
        f"- Central margin over limit: `{p['central']['margin_over_limit']:.6g}`",
        f"- Worst scanned gauge lifetime: `{w['lifetime_years']:.6e}` yr",
        f"- Critical central M_X/M_GUT: `{p['critical_M_X_over_M_GUT_central']:.6g}`",
        f"- Conditional triplet points below limit: `{p['conditional_triplet_points_excluded']}`",
        "", "## Scalar blockers", "",
    ] + [f"- {x}" for x in s["blockers"]]
    if s["failures"]:
        lines += ["", "## Explicit failures", ""] + [f"- {x}" for x in s["failures"]]
    lines += ["", "## Interpretation", "", r["verdict"], "", "`BLOCKED` is not a pass.", ""]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=INPUT)
    ap.add_argument("--require-closure", action="store_true")
    args = ap.parse_args()
    r = build_report(load_record(args.input))
    OUT_JSON.write_text(json.dumps(r, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(markdown(r), encoding="utf-8")
    print(json.dumps(r, indent=2))
    if args.require_closure:
        return 2 if r["overall_state"] == "FAIL" else (3 if r["overall_state"] == "BLOCKED" else 0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
