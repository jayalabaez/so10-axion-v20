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
import argparse
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
# The bounded up-sector rotation below is a nuisance parametrization, not a
# CKM fit.  CKM observables are not included in this benchmark objective.
# NuFIT-6.0 NO with atm
NUFIT = {
    "sin2_th12": (0.308, 0.012),
    "sin2_th23": (0.470, 0.015),
    "sin2_th13": (0.02215, 0.00060),
    "dm21": (7.49e-5, 0.20e-5),
    "dm31": (2.513e-3, 0.025e-3),
    "delta_deg": (212.0, 35.0),
}

def tan_beta_coordinate(tan_beta: float) -> float:
    """Inverse of the constrained 1.5+48.5*sigmoid coordinate."""
    if not 1.5 < tan_beta < 50.0:
        raise ValueError("tan_beta must lie inside the fitter interval (1.5,50)")
    fraction = (tan_beta - 1.5) / 48.5
    return math.log(fraction / (1.0 - fraction))


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


def takagi(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Autonne-Takagi factorization M=U diag(s) U^T.

    The real-block construction is stable for the 3x3 complex-symmetric
    Majorana and charged-lepton matrices used here.
    """
    matrix = np.asarray(matrix, dtype=complex)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("Takagi input must be square")
    if not np.allclose(matrix, matrix.T, rtol=1e-9, atol=1e-15):
        raise ValueError("Takagi input must be complex symmetric")
    n = matrix.shape[0]
    block = np.block(
        [
            [-matrix.real, matrix.imag],
            [matrix.imag, matrix.real],
        ]
    )
    eigenvalues, eigenvectors = np.linalg.eigh(block)
    positive = np.argsort(eigenvalues)[-n:]
    singular = eigenvalues[positive]
    unitary = (
        eigenvectors[n:, positive] + 1.0j * eigenvectors[:n, positive]
    )
    order = np.argsort(singular)
    singular = np.real(singular[order])
    unitary = unitary[:, order]
    reconstruction = unitary @ np.diag(singular) @ unitary.T
    relative_error = np.linalg.norm(matrix - reconstruction) / max(
        np.linalg.norm(matrix), 1e-30
    )
    if relative_error > 1e-8:
        raise ValueError(f"Takagi reconstruction failed: {relative_error}")
    return singular, unitary


def _pmns_from_matrices(mnu: np.ndarray, me: np.ndarray) -> dict:
    neutrino_singular, u_nu = takagi(mnu)
    _charged_singular, u_e = takagi(me)
    # Normal ordering and charged-lepton mass ordering are already ascending.
    masses = neutrino_singular * 1e9  # GeV -> eV
    u = u_e.conj().T @ u_nu
    s13 = abs(u[0, 2])
    c13 = math.sqrt(max(1e-30, 1 - s13**2))
    s12 = min(1.0, abs(u[0, 1]) / c13)
    s23 = min(1.0, abs(u[1, 2]) / c13)
    c12 = math.sqrt(max(0.0, 1.0 - s12**2))
    c23 = math.sqrt(max(0.0, 1.0 - s23**2))
    jarl = np.imag(u[0, 0] * u[1, 1] * np.conj(u[0, 1]) * np.conj(u[1, 0]))
    sin_denom = c12 * c23 * c13**2 * s12 * s23 * s13
    sin_delta = (
        0.0
        if sin_denom < 1e-30
        else float(np.clip(jarl / sin_denom, -1.0, 1.0))
    )
    cos_denom = 2.0 * s12 * c12 * c23 * s23 * s13
    cos_numer = (
        abs(u[1, 0]) ** 2
        - s12**2 * c23**2
        - c12**2 * s23**2 * s13**2
    )
    cos_delta = (
        1.0
        if cos_denom < 1e-30
        else float(np.clip(cos_numer / cos_denom, -1.0, 1.0))
    )
    delta = math.degrees(math.atan2(sin_delta, cos_delta)) % 360.0
    return {
        "mnu_eV": masses.tolist(),
        "sum_mnu_eV": float(np.sum(masses)),
        "dm21_eV2": float(masses[1] ** 2 - masses[0] ** 2),
        "dm31_eV2": float(masses[2] ** 2 - masses[0] ** 2),
        "sin2_th12": s12**2,
        "sin2_th23": s23**2,
        "sin2_th13": s13**2,
        "delta_cp_deg": delta,
        "takagi_reconstruction": True,
        "charged_lepton_basis_included": True,
    }


def build_matrices(
    params: np.ndarray,
    v_r: float,
    *,
    mass_targets: dict[str, float] | None = None,
) -> dict:
    """Build the constrained benchmark matrices.

    ``params[0]`` is not a prediction: it maps by construction to
    ``1.5 < tan(beta) < 50``.  A fit at either endpoint is therefore a
    boundary stress, not a uniquely derived Higgs-sector value.

    Optional ``mass_targets`` replaces the default low-scale quark/lepton
    masses (used for common-scale RG re-fits).
    """
    targets = {**QUARK_LEPTON, **(mass_targets or {})}
    x0 = float(np.clip(params[0], -60.0, 60.0))
    tan_beta = 1.5 + 48.5 / (1.0 + math.exp(-x0))
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

    md = _diag(targets["m_d"], targets["m_s"], targets["m_b"])
    me = u_e @ _diag(
        targets["m_e"] * pe[0],
        targets["m_mu"] * pe[1],
        targets["m_tau"] * pe[2],
    ) @ u_e.T
    # Reconstruct H,F in the down basis
    h = (3.0 * md + me) / (4.0 * v_d)
    f = (md - me) / (4.0 * v_d)

    mu = u_u @ _diag(targets["m_u"], targets["m_c"], targets["m_t"]) @ u_u.T
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


def chi2_from_params(
    params: np.ndarray,
    v_r: float,
    *,
    mass_targets: dict[str, float] | None = None,
) -> tuple[float, dict]:
    try:
        data = build_matrices(params, v_r, mass_targets=mass_targets)
        lep = _pmns_from_matrices(data["M_nu"], data["M_e"])
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


def _load_revalidated_saved_report() -> dict | None:
    """Load saved witnesses only after recomputing their objective values."""
    path = Path(__file__).resolve().parent / "flavour_clebsch_fit_v20.json"
    if not path.exists():
        return None
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
        best = report["best_overall"]
        v20 = report["v20_single_scale_point"]
        best_params = np.asarray(best["params"], dtype=float)
        v20_params = np.asarray(v20["params"], dtype=float)
        best_chi2, _ = chi2_from_params(best_params, best["v_r_GeV"])
        v20_chi2, _ = chi2_from_params(v20_params, VS)
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None
    if (
        abs(best_chi2 - best["chi2"]) > 1e-7
        or abs(v20_chi2 - v20["chi2"]) > 1e-7
        or not report.get("fit_validity", {}).get(
            "Takagi_Majorana_diagonalization", False
        )
    ):
        return None
    report.pop("v20_lower_boundary_benchmark", None)
    report["saved_witnesses_revalidated"] = True
    return report


def run_fit(seed: int = 20, *, full_search: bool = False) -> dict:
    if not full_search:
        saved = _load_revalidated_saved_report()
        if saved is not None:
            return saved
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

    chi2_v20, params_v20, detail_v20 = best_v20[0], best_v20[1], best_v20[2]
    tan_beta_v20 = detail_v20["observables"].get("tan_beta")
    tan_beta_at_boundary = bool(
        tan_beta_v20 is not None
        and (
            abs(tan_beta_v20 - 1.5) < 1.0e-6
            or abs(tan_beta_v20 - 50.0) < 1.0e-6
        )
    )
    v20 = {
        "v_r_GeV": VS,
        "chi2": chi2_v20,
        "params": params_v20.tolist(),
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
            or tan_beta_at_boundary
        ),
        "tan_beta_parameterization": "1.5 + 48.5 sigmoid(x0)",
        "tan_beta_allowed_interval": [1.5, 50.0],
        "tan_beta_at_parameter_boundary": tan_beta_at_boundary,
        "tan_beta_unique": False,
        "fermion_coupling_numeric_point_unique": False,
        "single_scale_viable": bool(chi2_v20 < 30.0 and detail_v20["observables"].get("perturbative_4pi")),
        "note": (
            "Exact identification M_R scale = v_S. With corrected Takagi "
            "diagonalization and U_PMNS=U_e^dagger U_nu, the current multistart "
            "point is strongly disfavoured. This benchmark does not establish "
            "a unique/global tan(beta) or a unique numerical C_e,C_p,C_n."
        ),
    }

    # Also report best natural-scale point
    return {
        "status": (
            "corrected Takagi/charged-lepton-basis constrained 10+126 "
            "Clebsch benchmark"
        ),
        "method": (
            "down-diagonal Clebsch reconstruction + Type-I+II seesaw + "
            "Takagi(Mnu,Me) + U_PMNS=Ue^dagger Unu"
        ),
        "clebsch_relations": {
            "H": "(3 M_d + M_e)/(4 v_d)",
            "F": "(M_d - M_e)/(4 v_d)",
            "M_u": "v_u (H + F)  [soft target]",
            "M_D": "v_u (H - 3 F)",
            "M_R": "v_R F",
            "m_nu": "M_L - M_D M_R^{-1} M_D^T",
        },
        "n_observables_in_chi2": 8,
        "saved_witnesses_revalidated": False,
        "best_overall": {
            "tag": best["tag"],
            "v_r_GeV": best["v_r_GeV"],
            "chi2": best["chi2"],
            "max_abs_pull": best["max_abs_pull"],
            "pulls": best["pulls"],
            "observables": best["observables"],
            "y126_max": best["y126_max"],
            "perturbative_4pi": best["perturbative_4pi"],
            "params": best["x"],
        },
        "v20_single_scale_point": v20,
        "tan_beta_status": {
            "parameterized_interval": [1.5, 50.0],
            "unique_prediction": False,
            "profile_module": "tan_beta_profile_v20.py",
            "best_known_fixed_vR_tan_beta": v20["observables"].get("tan_beta"),
            "best_known_fixed_vR_chi2": v20["chi2"],
            "implication": (
                "The corrected flavour objective does not uniquely fix "
                "tan(beta); portal-dependent currents add a separate ambiguity."
            ),
        },
        "fit_validity": {
            "Takagi_Majorana_diagonalization": True,
            "charged_lepton_basis_in_PMNS": True,
            "CP_phase_uses_atan2": True,
            "CKM_in_chi2": False,
            "common_scale_RG_inputs": False,
            "parameters": 13,
            "observables_in_chi2": 8,
            "precision_global_fit": False,
        },
        "scope": (
            "Fits a constrained 10+126 Clebsch benchmark using low-scale mass "
            "inputs. Correct matrix diagonalization is now used, but CKM pulls "
            "and common-scale RG inputs are absent and the objective is "
            "underconstrained. It does not prove a global minimum, uniquely fix "
            "tan(beta), or constitute a precision high-scale flavour fit."
        ),
    }


def main(*, full_search: bool = False) -> int:
    report = run_fit(seed=20, full_search=full_search)
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
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--full-search",
        action="store_true",
        help="rerun the expensive multistart search instead of revalidating saved witnesses",
    )
    raise SystemExit(main(full_search=parser.parse_args().full_search))
