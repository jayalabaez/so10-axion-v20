"""Collect the lowest point of every R2-A descent run (gate 52 + skeptic 8) into one competitor bank (Q, J, ids) for
the D3 lift test: an LP point of the v22 design must satisfy V_c(q*) <= V_c(q_k) - margin at every old deep endpoint.
For each run the 'lowest' point is taken w.r.t. the coupling vector c of the R2-A point that launched it (as in the
diagnosis deep_budget.py); in addition the global-lowest point of every bank under a few reference c is kept.
Reads the R2-A scratch banks read-only; writes deep_endpoints.npz into DCF_SCRATCH.
"""
from __future__ import annotations
import json, os
from pathlib import Path
import numpy as np

R2A = Path(r"C:\Users\jayal\Downloads\So10Theory2\So10Theory\_v22research\research\v21_kill_gates\round2\R2-A-vacuum-two-bidoublets")
SCR = Path(r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\wfV21R2\R2-A-vacuum-two-bidoublets")
OUT = Path(os.environ.get("DCF_SCRATCH", ".")) / "deep_endpoints.npz"

summ = json.load(open(R2A / "descent_summary.json", encoding="utf-8"))
Qs, Js, names = [], [], []
ids_ref = None
for rnd, R in summ.items():
    sol = np.load(SCR / R["sol"]); c = sol["c"]; ids = [str(x) for x in sol["ids"]]
    if ids_ref is None:
        ids_ref = ids
    assert ids == ids_ref
    for run in R["runs"]:
        bpath = SCR / f"descend_{run['name']}_bank.npz"
        if not bpath.exists():
            continue
        B = np.load(bpath); J = np.asarray(B["J"], float); Q = np.asarray(B["Q"], float)
        k = int(np.argmin(J @ c))
        Qs.append(Q[k]); Js.append(J[k]); names.append(f"{rnd}:{run['name']}")
# skeptic descents (sk_descend banks: DPB_*/DPD_*), if they carry J
sk = SCR / "skeptic"
for f in sorted(sk.glob("D*_*.npz")) if sk.exists() else []:
    try:
        B = np.load(f)
        if "J" in B.files and "Q" in B.files and "ids" in B.files and [str(x) for x in B["ids"]] == ids_ref:
            J = np.asarray(B["J"], float); Q = np.asarray(B["Q"], float)
            # lowest under the mean c of the gate rounds (proxy) -> keep 2 lowest distinct
            cbar = np.mean([np.load(SCR / R["sol"])["c"] for R in summ.values()], axis=0)
            for k in np.argsort(J @ cbar)[:2]:
                Qs.append(Q[k]); Js.append(J[k]); names.append(f"skeptic:{f.stem}:{k}")
    except Exception:
        continue
Qs = np.array(Qs); Js = np.array(Js)
nrm = np.linalg.norm(Qs, axis=1)
np.savez_compressed(OUT, Q=Qs, J=Js, ids=np.array(ids_ref), names=np.array(names))
print(f"{len(names)} deep endpoints -> {OUT}; |q| range {nrm.min():.2f}-{nrm.max():.2f}")
for n, q in zip(names[:5], nrm[:5]):
    print(n, round(float(q), 3))
