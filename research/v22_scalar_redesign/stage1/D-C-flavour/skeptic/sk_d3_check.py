"""SKEPTIC D3 check: re-evaluate the designer's fresh-descent endpoints with an independent VALUES-ONLY path.

The designer's descents (r2_descend.py) use the derivative adapters (target.parameter_rows: value+gradient+Hessian).
Here V is recomputed from the repo's live direction evaluator (potential.evaluate_directions -> coefficient_jacobian),
which is a separate code path (no derivative adapters), with the designer's LP coupling vectors c (read-only .npz).
For each descent: V(q*) [SM point, H = 0], V(qmin), the SO(10)-invariant norms, and V(qmin with H -> 0) (is the
energy gain carried by the SU(2)_L-breaking H10 vev or by the SM-singlet-blind rest?).  Also the gradient/Hessian
of V at q* from the designer's stored rows (stationarity and local minimum check of the SM point itself).
Output: sk_d3_check.json (this folder).
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np

REPO = r"C:\Users\jayal\Downloads\So10Theory2\So10Theory\_v22research"
sys.path.insert(0, REPO)
import live_g2_canonical_486_field_chart_v20 as chart  # noqa: E402
import live_g2_arbitrary_component_potential_values_v20 as potential  # noqa: E402

SCR = Path(r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\v22_DCflav_d3")
DES = Path(__file__).resolve().parent.parent / "d3" / "descents"
HERE = Path(__file__).resolve().parent


def V_values_only(q, c, ids):
    st = chart.unpack(np.asarray(q, float))
    jac = potential.coefficient_jacobian(potential.evaluate_directions(st))
    return float(sum(ci * jac[pid] for ci, pid in zip(c, ids))), st


def norms(q):
    return {"Phi210": float(np.linalg.norm(q[chart.PHI_SLICE])), "H10": float(np.linalg.norm(q[chart.H_SLICE])),
            "Sigma": float(np.linalg.norm(q[chart.SIGMA_SLICE])), "S": float(np.linalg.norm(q[chart.S_SLICE])),
            "Phi17": float(np.linalg.norm(q[chart.X_SLICE]))}


Z = np.load(SCR / "SMf_rows.npz")
qstar = Z["q"]; idsZ = [str(x) for x in Z["ids"]]
out = {"descents": {}}
t0 = time.time()
cache = {}
for jf in sorted(DES.glob("descend_*.json")):
    d = json.load(open(jf))
    tag = jf.stem.replace("descend_", "")
    sol = np.load(SCR / d["sol"]); c = sol["c"]; ids = [str(x) for x in sol["ids"]]
    assert ids == idsZ
    if d["sol"] not in cache:
        Vs, _ = V_values_only(qstar, c, ids)
        g = sum(c[i] * Z["grads"][i] for i in range(len(c)))
        H = sum(c[i] * Z["hess"][i] for i in range(len(c))); H = 0.5 * (H + H.T)
        w = np.linalg.eigvalsh(H)
        cache[d["sol"]] = {"V*_values_only": Vs, "V*_rows": float(c @ Z["values"]), "|grad V|(q*)": float(np.linalg.norm(g)),
                           "hess_min_eig(q*)": float(w[0]), "n_neg(q*) < -1e-6": int(np.sum(w < -1e-6)),
                           "n_zero(q*)": int(np.sum(np.abs(w) <= 1e-6))}
    npz = np.load(SCR / f"descend_{tag}.npz"); qmin = npz["qmin"]
    Vm, st = V_values_only(qmin, c, ids)
    q0 = qmin.copy(); q0[chart.H_SLICE] = 0.0
    V0, _ = V_values_only(q0, c, ids)
    rec = {"sol": d["sol"], "start": d["start"], **cache[d["sol"]], "V(qmin)_values_only": Vm,
           "DeltaV_values_only": Vm - cache[d["sol"]]["V*_values_only"], "DeltaV_designer": d["V_min_seen-V*"],
           "norms(qmin)": norms(qmin), "norms(q*)": norms(qstar), "DeltaV(qmin with H10->0)": V0 - cache[d["sol"]]["V*_values_only"]}
    out["descents"][tag] = rec
    print(f"{tag:18s} sol {d['sol']:22s} V* {rec['V*_values_only']:+.6f} (rows {rec['V*_rows']:+.6f}) dV = {rec['DeltaV_values_only']:+.4f}"
          f" (designer {d['V_min_seen-V*']:+.4f}); |H10| = {rec['norms(qmin)']['H10']:.3f}; dV(H->0) = {rec['DeltaV(qmin with H10->0)']:+.4f}"
          f"; |gradV(q*)| = {rec['|grad V|(q*)']:.2e} minEig(q*) = {rec['hess_min_eig(q*)']:.2e} ({time.time()-t0:.0f}s)", flush=True)
    json.dump(out, open(HERE / "sk_d3_check.json", "w"), indent=1)
print("done")
