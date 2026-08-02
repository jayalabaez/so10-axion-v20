#!/usr/bin/env python3
"""Broken-phase SO(10) 10+126 Clebsch/flavour fit at the v20 B-L scale.

Uses the standard down-diagonal Clebsch reconstruction:

    M_d = v_d (H + F),   M_e = v_d (H - 3 F)
 => H = (3 M_d + M_e)/(4 v_d),  F = (M_d - M_e)/(4 v_d)

then M_u = v_u (H + F), M_D = v_u (H - 3 F), M_R = v_R F, plus a small
Type-II piece, and fits residual basis freedoms to NuFIT-6.0 + quark data.

This is a constrained benchmark, not a uniqueness proof.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import minimize


FOUR_PI = 4.0 * math.pi
VS = 6.313855e11
VEV = 174.104

# Masses in GeV at low scale (fit targets)
QUARK_LEPTON = {
    "m_u": 2.16e-3,
    "m_c": 1.27,
    "m_t": 172.69,
    "m_d": 4.67e-3,
    "m_s": 93e-3,
    "m_b": 4.18,
    "m_e": 5.110e-4,
    "m_mu": 0.10566,
    "m_tau": 1.777,
}
# CKM (approximate PDG)
CKM_S12, CKM_S23, CKM_S13, CKM_D = 0.2250, 0.0418, 0.00369, 1.196
# NuFIT-6.0 NO with atm
NUFIT = {
    "sin2_th12": (0.308, 0.012),
    "sin2_th23": (0.470, 0.015),
    "sin2_th13": (0.02215, 0.00060),
    "dm21": (7.49e-5, 0.20e-5),
    "dm31": (2.513e-3, 0.025e-3),
    "delta_deg": (212.0, 35.0),
}


def _rotation(s12, s23, s13, delta):
    c12, c23, c13 = math.sqrt(1 - s12**2), math.sqrt(1 - s23**2), math.sqrt(1 - s13**2)
    d = np.exp(1j * delta)
    return np.array(
        [
            [c12 * c13, s12 * c13, s13 * np.conj(d)],
            [
                -s12 * c23 - c12 * s23 * s13 * d,
                c12 * c23 - s12 * s23 * s13 * d,
                s23 * c13,
            ],
            [
                s12 * s23 - c12 * c23 * s13 * d,
                -c12 * s23 - s12 * c23 * s13 * d,
                c23 * c13,
            ],
        ],
        dtype=complex,
    )


def _diag(a, b, c):
    return np.diag([a, b, c]).astype(complex)


def _pmns_from_mnu(mnu: np.ndarray) -> dict:
    evals, vecs = np.linalg.eigh(mnu)
    order = np.argsort(np.abs(evals))
    evals = np.real(evals[order])
    vecs = vecs[:, order]
    # normal-ordering masses
    masses = np.abs(evals) * 1e9  # GeV -> eV
    u = vecs
    s13 = abs(u[0, 2])
    c13 = math.sqrt(max(1e-30, 1 - s13**2))
    s12 = min(1.0, abs(u[0, 1]) / c13)
    s23 = min(1.0, abs(u[1, 2]) / c13)
    jarl = np.imag(np.conj(u[0, 0]) * u[0, 2] * np.conj(u[2, 2]) * u[2, 0])
    denom = (
        s12
        * s23
        * s13
        * c13
        * math.sqrt(max(0.0, 1 - s12**2))
        * math.sqrt(max(0.0, 1 - s23**2))
    )
    sind = 0.0 if denom < 1e-30 else float(np.clip(jarl / denom, -1, 1))
    delta = math.degrees(math.asin(sind)) % 360.0
    return {
        "mnu_eV": masses.tolist(),
        "sum_mnu_eV": float(np.sum(masses)),
        "dm21_eV2": float(masses[1] ** 2 - masses[0] ** 2),
        "dm31_eV2": float(masses[2] ** 2 - masses[0] ** 2),
        "sin2_th12": s12**2,
        "sin2_th23": s23**2,
        "sin2_th13": s13**2,
        "delta_cp_deg": delta,
    }


def build_matrices(params: np.ndarray, v_r: float) -> dict:
    """params: tanβ, phases/angles for charged-lepton vs down misalignment, Type-II, ..."""
    tan_beta = 1.5 + 48.5 / (1.0 + math.exp(-params[0]))
    v_u = VEV * math.sin(math.atan(tan_beta))
    v_d = VEV * math.cos(math.atan(tan_beta))

    # unitary freedom relating M_e eigenbasis to M_d eigenbasis
    s12 = 0.5 * (1 + math.tanh(params[1]))
    s23 = 0.5 * (1 + math.tanh(params[2]))
    s13 = 0.15 * (0.5 + 0.5 * math.tanh(params[3]))
    delta = (params[4] % (2 * math.pi))
    u_e = _rotation(s12, s23, s13, delta)

    # relative phases on charged-lepton eigenvalues
    pe = np.exp(1j * params[5:8])
    # up-sector CKM-like left rotation residual vs down
    su12 = 0.25 * (0.5 + 0.5 * math.tanh(params[8]))
    su23 = 0.05 * (0.5 + 0.5 * math.tanh(params[9]))
    su13 = 0.01 * (0.5 + 0.5 * math.tanh(params[10]))
    du = params[11] % (2 * math.pi)
    u_u = _rotation(su12, su23, su13, du)

    md = _diag(QUARK_LEPTON["m_d"], QUARK_LEPTON["m_s"], QUARK_LEPTON["m_b"])
    me = u_e @ _diag(
        QUARK_LEPTON["m_e"] * pe[0],
        QUARK_LEPTON["m_mu"] * pe[1],
        QUARK_LEPTON["m_tau"] * pe[2],
    ) @ u_e.T
    # Reconstruct H,F in the down basis
    h = (3.0 * md + me) / (4.0 * v_d)
    f = (md - me) / (4.0 * v_d)

    mu = u_u @ _diag(QUARK_LEPTON["m_u"], QUARK_LEPTON["m_c"], QUARK_LEPTON["m_t"]) @ u_u.T
    # Enforce Clebsch consistency soft target: mu ~ v_u (h+f)
    mu_pred = v_u * (h + f)
    mdnu = v_u * (h - 3.0 * f)
    mr = v_r * f
    r_ii = 10.0 ** float(np.clip(params[12], -14.0, -6.0))  # Type-II v_L/v_d
    ml = r_ii * v_d * f
    try:
        inv = np.linalg.inv(mr)
    except np.linalg.LinAlgError:
        inv = np.linalg.pinv(mr)
    mnu = ml - mdnu @ inv @ mdnu.T
    # Symmetrize numerically
    mnu = 0.5 * (mnu + mnu.T)
    if not np.all(np.isfinite(mnu)):
        mnu = np.eye(3, dtype=complex) * 1e-20

    y10_max = float(np.max(np.abs(h)))
    y126_max = float(np.max(np.abs(f)))
    return {
        "tan_beta": tan_beta,
        "v_u": v_u,
        "v_d": v_d,
        "v_r": v_r,
        "H": h,
        "F": f,
        "M_u_target": mu,
        "M_u_pred": mu_pred,
        "M_d": md,
        "M_e": me,
        "M_D": mdnu,
        "M_R": mr,
        "M_nu": mnu,
        "y10_max": y10_max,
        "y126_max": y126_max,
        "u_mismatch": float(np.linalg.norm(mu - mu_pred) / max(np.linalg.norm(mu), 1e-30)),
    }


def chi2_from_params(params: np.ndarray, v_r: float) -> tuple[float, dict]:
    try:
        data = build_matrices(params, v_r)
        lep = _pmns_from_mnu(data["M_nu"])
    except Exception:
        return 1.0e9, {"pulls": {}, "observables": {}, "data": {}}
    pulls = {}
    chi2 = 0.0
    # Neutrino observables
    for key, (obs_key, scale) in (
        ("sin2_th12", ("sin2_th12", 1)),
        ("sin2_th23", ("sin2_th23", 1)),
        ("sin2_th13", ("sin2_th13", 1)),
        ("dm21", ("dm21_eV2", 1)),
        ("dm31", ("dm31_eV2", 1)),
        ("delta_deg", ("delta_cp_deg", 1)),
    ):
        central, sigma = NUFIT[key]
        val = lep[obs_key]
        # CP phase: circular distance
        if key == "delta_deg":
            diff = abs((val - central + 180) % 360 - 180)
            pull = diff / sigma
        else:
            pull = (val - central) / sigma
        pulls[key] = float(pull)
        chi2 += float(pull**2)

    # Charged-fermion masses are inputs by construction; penalize up-Clebsch mismatch
    mismatch = data["u_mismatch"]
    pulls["up_clebsch_mismatch"] = float(mismatch / 0.35)
    chi2 += float((mismatch / 0.35) ** 2)

    # Prefer hierarchical neutrinos sum < 0.12 eV
    pulls["sum_mnu"] = float((lep["sum_mnu_eV"] - 0.06) / 0.04)
    chi2 += float(pulls["sum_mnu"] ** 2)

    # Perturbativity
    y_max = max(data["y10_max"], data["y126_max"])
    if y_max > FOUR_PI:
        penalty = 50.0 * (y_max - FOUR_PI) ** 2
        pulls["nonperturbative"] = float(math.sqrt(penalty))
        chi2 += penalty

    obs = {
        **lep,
        "tan_beta": data["tan_beta"],
        "y10_max": data["y10_max"],
        "y126_max": data["y126_max"],
        "up_clebsch_mismatch": data["u_mismatch"],
        "perturbative_4pi": y_max < FOUR_PI,
    }
    return chi2, {"pulls": pulls, "observables": obs, "data": data}


def run_fit(seed: int = 20) -> dict:
    rng = np.random.default_rng(seed)
    best = None
    for trial in range(24):
        x0 = rng.normal(size=13)
        x0[0] = rng.uniform(-1, 1)  # tan beta
        x0[12] = rng.uniform(-12, -8)  # Type-II
        for v_r, tag in ((VS, "v20_scale"), (1e14, "natural_1e14"), (1e13, "natural_1e13")):
            res = minimize(
                lambda x, vr=v_r: chi2_from_params(x, vr)[0],
                x0,
                method="Nelder-Mead",
                options={"maxiter": 6000, "xatol": 1e-8, "fatol": 1e-8},
            )
            chi2, detail = chi2_from_params(res.x, v_r)
            row = {
                "tag": tag,
                "v_r_GeV": v_r,
                "chi2": chi2,
                "x": res.x.tolist(),
                "pulls": detail["pulls"],
                "observables": detail["observables"],
                "max_abs_pull": float(max(abs(p) for p in detail["pulls"].values())),
                "y126_max": detail["observables"]["y126_max"],
                "perturbative_4pi": detail["observables"]["perturbative_4pi"],
            }
            if best is None or chi2 < best["chi2"]:
                best = row

    # Dedicated multi-start polish at exact v20 scale
    best_v20 = None
    for trial in range(40):
        x0 = rng.normal(size=13)
        x0[0] = rng.uniform(-1.5, 1.5)
        x0[12] = rng.uniform(-13.0, -7.0)
        res = minimize(
            lambda x: chi2_from_params(x, VS)[0],
            x0,
            method="Nelder-Mead",
            options={"maxiter": 8000, "xatol": 1e-10, "fatol": 1e-10},
        )
        chi2, detail = chi2_from_params(res.x, VS)
        if best_v20 is None or chi2 < best_v20[0]:
            best_v20 = (chi2, res.x, detail)
    # Also polish from the natural-scale best seed
    res_seed = minimize(
        lambda x: chi2_from_params(x, VS)[0],
        np.array(best["x"], dtype=float),
        method="Nelder-Mead",
        options={"maxiter": 12000, "xatol": 1e-10, "fatol": 1e-10},
    )
    chi2_seed, detail_seed = chi2_from_params(res_seed.x, VS)
    if chi2_seed < best_v20[0]:
        best_v20 = (chi2_seed, res_seed.x, detail_seed)

    chi2_v20, _, detail_v20 = best_v20[0], best_v20[1], best_v20[2]
    v20 = {
        "v_r_GeV": VS,
        "chi2": chi2_v20,
        "pulls": detail_v20["pulls"],
        "observables": detail_v20["observables"],
        "max_abs_pull": float(max(abs(p) for p in detail_v20["pulls"].values()))
        if detail_v20["pulls"]
        else 1e9,
        "y10_max": detail_v20["observables"].get("y10_max"),
        "y126_max": detail_v20["observables"].get("y126_max"),
        "perturbative_4pi": detail_v20["observables"].get("perturbative_4pi"),
        "boundary_stress": bool(
            detail_v20["observables"].get("y126_max", 0) > 1.0
            or chi2_v20 > 50.0
        ),
        "single_scale_viable": bool(chi2_v20 < 30.0 and detail_v20["observables"].get("perturbative_4pi")),
        "note": (
            "exact identification M_R scale = v_S; large chi2 means the "
            "single-scale claim is stressed or falsified inside this Clebsch ansatz"
        ),
    }

    # Also report best natural-scale point
    return {
        "status": "constrained 10+126 Clebsch/flavour benchmark",
        "method": "down-diagonal Clebsch reconstruction + Type-I+II seesaw",
        "clebsch_relations": {
            "H": "(3 M_d + M_e)/(4 v_d)",
            "F": "(M_d - M_e)/(4 v_d)",
            "M_u": "v_u (H + F)  [soft target]",
            "M_D": "v_u (H - 3 F)",
            "M_R": "v_R F",
            "m_nu": "M_L - M_D M_R^{-1} M_D^T",
        },
        "n_observables_in_chi2": 8,
        "best_overall": {
            "tag": best["tag"],
            "v_r_GeV": best["v_r_GeV"],
            "chi2": best["chi2"],
            "max_abs_pull": best["max_abs_pull"],
            "pulls": best["pulls"],
            "observables": best["observables"],
            "y126_max": best["y126_max"],
            "perturbative_4pi": best["perturbative_4pi"],
        },
        "v20_single_scale_point": v20,
        "scope": (
            "Fits the renormalizable 10+126 Clebsch sector. Does not uniquely fix "
            "anomalon portal flavour matrices or the full 210-breaking vacuum."
        ),
    }


def main() -> int:
    report = run_fit(seed=20)
    Path(__file__).resolve().parent.joinpath("flavour_clebsch_fit_v20.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    ss = report["v20_single_scale_point"]
    bo = report["best_overall"]
    print(
        json.dumps(
            {
                "best_tag": bo["tag"],
                "chi2_best": bo["chi2"],
                "chi2_v20": ss["chi2"],
                "y126_v20": ss["y126_max"],
                "pert_v20": ss["perturbative_4pi"],
                "sum_mnu": ss["observables"]["sum_mnu_eV"],
                "s13": ss["observables"]["sin2_th13"],
                "maxpull_v20": ss["max_abs_pull"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
