"""SKEPTIC (D-B-symmetry, D3): independent re-evaluation of the designer's V1 slice vacuum claims.

Own code; read-only imports of the committed v20 repo modules (chart, potential evaluator); the designer's scratch
files (LP solutions c, descent endpoints q_min) are only READ.
For each case:
  1. rebuild q* from Am45_rows_meta.json with the repo chart and compare with the stored q;
  2. evaluate the 51 operator values J via potential.evaluate_directions + coefficient_jacobian (NOT the
     parameter_rows path that produced the designer's banks) at q* and at q_min;
  3. V_c(q_min) - V_c(q*), with per-operator budget (top negative contributions);
  4. stationarity at q*: central finite differences of V_c along random directions;
  5. gauge invariance of V_c at q_min: |dV/ds| along the symmetry tangents (should be ~0);
  6. SU(2)_L-breaking measure at q_min: q.C2L.q (C2L = SU(2)_L Casimir in the chart, from Am45_rows.npz);
  7. at q*: Hessian from the stored exact rows with c -> eigenvalue census, and composition of the light
     (non-Goldstone) eigenvectors by block (H10 vs Sigma vs Phi), to test 'one light H1-dominated bidoublet'.
Writes sk_d3_eval.json next to this script.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = r"C:\Users\jayal\Downloads\So10Theory2\So10Theory\_v22research"
LP = Path(os.environ.get("DB_LPDIR", r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\v22_DB\lp"))
sys.path.insert(0, REPO)
import live_g2_canonical_486_field_chart_v20 as chart  # noqa: E402
import live_g2_arbitrary_component_potential_values_v20 as potential  # noqa: E402
import direct_phi_h_sigmabar_tensor_v20 as direct  # noqa: E402
import g3_sm_pati_salam_candidate_v20 as candidate  # noqa: E402

BLOCKS = {"Phi210": chart.PHI_SLICE, "H10": chart.H_SLICE, "Sigma126bar": chart.SIGMA_SLICE, "S": chart.S_SLICE,
          "Phi17": chart.X_SLICE}


def J_at(q, ids):
    st = chart.unpack(np.asarray(q, float)).validated()
    jac = potential.coefficient_jacobian(potential.evaluate_directions(st))
    return np.array([float(jac[pid]) for pid in ids])


def qstar_rebuild(meta):
    basis = direct.singlet_basis()
    phi = direct.add_forms(direct.scale_form(basis["p"], meta["p"]), direct.scale_form(basis["a"], meta["a"]),
                           direct.scale_form(basis["omega"], meta["omega"]))
    sigma = chart.sigma_from_coordinates(float(meta["r"]) * candidate.sigma_std_unit_coordinates())
    st = potential.FieldState(phi=phi, h=np.zeros(chart.H_COMPLEX_DIM, dtype=complex), sigma=sigma,
                              s=complex(meta["s"]), x=complex(meta["x"])).validated()
    return chart.pack(st)


CASES = [("V1A_bankA", "V1s_D2_lb.npz", "descend_V1A_bankA"),
         ("V1A_hs32", "V1s_D2_lb.npz", "descend_V1A_hs32"),
         ("V1A_rnd33", "V1s_D2_lb.npz", "descend_V1A_rnd33"),
         ("V1B_p831", "V1s_D2_lb_box4_R2.npz", "descend_V1B_p831"),
         ("V1B_hs41", "V1s_D2_lb_box4_R2.npz", "descend_V1B_hs41")]


def hessian_census(Z, c, ids):
    assert [str(x) for x in Z["ids"]] == ids
    H = np.einsum("i,ijk->jk", c, Z["hess"]); H = 0.5 * (H + H.T)
    g = c @ Z["grads"]
    w, U = np.linalg.eigh(H)
    T = np.asarray(Z["tangents"], float)
    # project out gauge/global symmetry tangents to separate Goldstones
    Qt, _ = np.linalg.qr(T)
    rank_T = int(np.linalg.matrix_rank(T, tol=1e-9))
    P = np.eye(H.shape[0]) - Qt[:, :rank_T] @ Qt[:, :rank_T].T
    Hp = P @ H @ P; Hp = 0.5 * (Hp + Hp.T)
    wp, Up = np.linalg.eigh(Hp)
    # census on the projected Hessian: zero modes include the rank_T tangents
    tiny = 1e-9
    nz = int(np.sum(np.abs(wp) < tiny)); nneg = int(np.sum(wp < -tiny))
    pos = wp[wp > tiny]
    out = {"|grad|": float(np.linalg.norm(g)), "rank_tangents": rank_T, "n_zero(<1e-9)": nz, "n_neg": nneg,
           "min_eig": float(wp.min()), "smallest_positive_eigs": [float(x) for x in np.sort(pos)[:20]]}
    # light non-Goldstone modes: 1e-9 < m^2 < 1e-5 (heavy gap t ~ 1e-3)
    light = [k for k in range(len(wp)) if tiny < wp[k] < 1e-5]
    comp = []
    for k in light:
        v = Up[:, k]
        comp.append({"m2": float(wp[k]), **{name: float(np.sum(v[sl] ** 2)) for name, sl in BLOCKS.items()}})
    out["n_light(1e-9..1e-5)"] = len(light)
    out["light_mode_block_weights"] = comp
    # all eigenvalues in [1e-5, 2e-3] (around the heavy gap)
    out["n_in_[1e-5,2e-3]"] = int(np.sum((wp > 1e-5) & (wp < 2e-3)))
    return out


def main():
    t0 = time.time()
    meta = json.load(open(LP / "Am45_rows_meta.json"))["point"]
    Z = np.load(LP / "Am45_rows.npz")
    qstar_stored = Z["q"]
    qstar = qstar_rebuild(meta)
    C2L = np.asarray(Z["C2L"], float)
    out = {"meta_point": meta, "qstar_rebuilt_vs_stored_maxdiff": float(np.max(np.abs(qstar - qstar_stored)))}
    print("q* rebuild diff", out["qstar_rebuilt_vs_stored_maxdiff"], flush=True)
    sols = {}
    for label, solf, dname in CASES:
        sol = np.load(LP / solf); c = np.asarray(sol["c"], float); ids = [str(x) for x in sol["ids"]]
        if solf not in sols:
            Jstar = J_at(qstar, ids)
            rng = np.random.default_rng(11)
            fd = []
            for _ in range(3):
                d = rng.normal(size=qstar.size); d /= np.linalg.norm(d); h = 1e-4
                fd.append((float(c @ J_at(qstar + h * d, ids)) - float(c @ J_at(qstar - h * d, ids))) / (2 * h))
            hc = hessian_census(Z, c, ids)
            sols[solf] = {"Jstar": Jstar, "V_star": float(c @ Jstar), "fd_grad_qstar": fd,
                          "Jstar_vs_stored_maxdiff": float(np.max(np.abs(Jstar - Z["values"]))), "hessian": hc}
            print(solf, "V*", sols[solf]["V_star"], "fd", fd, "J diff", sols[solf]["Jstar_vs_stored_maxdiff"], flush=True)
            print("   hessian census", json.dumps({k: v for k, v in hc.items() if k != "light_mode_block_weights"}), flush=True)
            for row in hc["light_mode_block_weights"]:
                print("   light", json.dumps({k: round(v, 6) for k, v in row.items()}), flush=True)
        S = sols[solf]
        dj = json.load(open(LP / f"{dname}.json"))
        assert dj["sol"] == solf
        qmin = np.load(LP / f"{dname}.npz")["qmin"]
        Jmin = J_at(qmin, ids)
        Vmin = float(c @ Jmin)
        contrib = c * (Jmin - S["Jstar"])
        order = np.argsort(contrib)
        top = [(ids[i], round(float(contrib[i]), 3)) for i in order[:7]]
        # gauge invariance along symmetry tangents at qmin
        full, _ = candidate.symmetry_matrix(chart.unpack(qmin).validated())
        T = np.asarray(full, float)
        if T.shape[0] != qmin.size:
            T = T.T
        inv = []
        for a in range(T.shape[1]):
            v = T[:, a]; nv = np.linalg.norm(v)
            if nv < 1e-12:
                continue
            v = v / nv; h = 1e-4
            inv.append(abs(float(c @ J_at(qmin + h * v, ids)) - float(c @ J_at(qmin - h * v, ids))) / (2 * h))
        rec = {"solution": solf, "descent": dname, "start": dj["start"], "V_star_indep": S["V_star"],
               "V_star_reported": dj["V_star"], "V_min_indep": Vmin, "dV_indep": Vmin - S["V_star"],
               "dV_reported": dj["V_min_seen-V*"], "top_negative_budget": top,
               "gauge_tangent_max_|dV/ds|": max(inv) if inv else None, "n_tangents": len(inv),
               "qmin_blocks": {n: float(np.linalg.norm(qmin[sl])) for n, sl in BLOCKS.items()},
               "qmin_C2L_measure": float(qmin @ C2L @ qmin), "qstar_C2L_measure": float(qstar @ C2L @ qstar),
               "seconds": time.time() - t0}
        out[label] = rec
        print(label, json.dumps(rec, default=float), flush=True)
        out["solutions"] = {k: {kk: vv for kk, vv in v.items() if kk != "Jstar"} for k, v in sols.items()}
        json.dump(out, open(HERE / "sk_d3_eval.json", "w"), indent=1, default=float)
    print("done", time.time() - t0, flush=True)


if __name__ == "__main__":
    main()
