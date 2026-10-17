"""Evaluate the 64 direction values of the live compiler at a list of chart points (value only, ~17 s each).

usage: python -B k3_eval_points.py <mode> <out.npz> [n]
modes:
  smsinglet  : random points in the 6-dim SM-singlet subspace (p, a, omega, r, s, x), phases 0
  deltar     : 7-dim: (p, a, omega, r_std, r_deltaR(Y=-1), s, x)
  rays       : random unit directions in the full 486 chart (for the quartic part)
  file:<npz> : points given as array 'Q' (n x 486) in the npz
Saves Q (n x 486), values (n x 64 complex), direction ids.
"""
from __future__ import annotations
import sys, time, numpy as np
import k3_common as K

mode, out = sys.argv[1], sys.argv[2]
n = int(sys.argv[3]) if len(sys.argv) > 3 else 100
rng = np.random.default_rng(12345)
chart = K.chart
basis = K.direct.singlet_basis()
sig_std = K.candidate.sigma_std_unit_coordinates()
dr_form = K.direct.delta_r()
dr_coords = chart.sigma_coordinates(dr_form); dr_coords = dr_coords / np.linalg.norm(dr_coords)

def state_of(p, a, om, r1, r2, s, x):
    phi = K.phi_form(p, a, om)
    sigma = chart.sigma_from_coordinates(r1 * sig_std + r2 * dr_coords)
    return K.potential.FieldState(phi=phi, h=np.zeros(10, complex), sigma=sigma, s=complex(s), x=complex(x)).validated()

Q = []
if mode == "smsinglet":
    for _ in range(n):
        p, a, om = rng.uniform(-1, 1, 3); r = rng.uniform(0, 1); s = rng.uniform(0, 1); x = rng.uniform(0, 4)
        Q.append(chart.pack(state_of(p, a, om, r, 0.0, s, x)))
elif mode == "deltar":
    for _ in range(n):
        p, a, om = rng.uniform(-1, 1, 3); r1, r2 = rng.uniform(0, 1, 2); s = rng.uniform(0, 1); x = rng.uniform(0, 4)
        Q.append(chart.pack(state_of(p, a, om, r1, r2, s, x)))
elif mode == "rays":
    for _ in range(n):
        v = rng.normal(size=chart.TOTAL_DIM); v /= np.linalg.norm(v)
        st = chart.unpack(v)  # unpack enforces the -i Hodge projection? use pack(unpack) to be safe
        Q.append(chart.pack(st.validated()))
elif mode == "blockrays":
    names = list(K.BLOCKS); slices = [K.BLOCKS[b] for b in names]
    plan = [("Phi210",), ("Sigma126bar",), ("H10",), ("Phi210", "Sigma126bar"), ("Phi210", "H10"), ("Sigma126bar", "H10"), ("H10", "S"), ("Sigma126bar", "S"), ("Phi210", "Phi17"), ("H10", "Phi17"), ("Sigma126bar", "Phi17")]
    counts = [50, 60, 30, 15, 10, 10, 5, 5, 5, 5, 5]
    for blocks_, cnt in zip(plan, counts):
        for _ in range(cnt):
            v = np.zeros(chart.TOTAL_DIM)
            for bname in blocks_:
                sl = K.BLOCKS[bname]; w = rng.normal(size=sl.stop - sl.start); v[sl] = w / np.linalg.norm(w)
            v /= np.linalg.norm(v); Q.append(chart.pack(chart.unpack(v).validated()))
elif mode == "tripletrays":
    su2r = [0.5 * K.candidate.chart_generator(v) for v in K.hypercharge.SU2R_INTEGER]
    Sv = chart.pack(K.potential.FieldState(phi={}, h=np.zeros(10, complex), sigma=chart.sigma_from_coordinates(sig_std), s=0j, x=0j))
    vecs = [Sv]
    for g in su2r:
        for _ in range(2):
            w = g @ vecs[-1] if len(vecs) < 3 else None
            if w is not None and np.linalg.norm(w) > 1e-9: vecs.append(w / np.linalg.norm(w))
    # orthonormal real basis of the span of {T_a^k Sv} (the triplet's 6 real dims)
    span = [Sv]
    for g in su2r:
        for v in list(span):
            w = g @ v
            if np.linalg.norm(w) > 1e-9: span.append(w / np.linalg.norm(w))
    M = np.column_stack(span); uu, ss, _ = np.linalg.svd(M, full_matrices=False); Bt = uu[:, ss > 1e-8]
    print("triplet real dimension:", Bt.shape[1])
    # include the three weight directions explicitly plus random rays
    for j in range(Bt.shape[1]): Q.append(chart.pack(chart.unpack(Bt[:, j]).validated()))
    for _ in range(n):
        w = rng.normal(size=Bt.shape[1]); v = Bt @ (w / np.linalg.norm(w)); Q.append(chart.pack(chart.unpack(v).validated()))
elif mode == "hsrays":
    # random rays in the H10 (+) Sigma126bar subspace with random relative weight (the runaway direction family),
    # plus H+Sigma+Phi and H+Sigma+S mixtures
    plan = [(("H10", "Sigma126bar"), 90), (("H10", "Sigma126bar", "Phi210"), 40), (("H10", "Sigma126bar", "S"), 10), (("H10", "Sigma126bar", "Phi210", "S"), 10)]
    for blocks_, cnt in plan:
        for _ in range(cnt):
            v = np.zeros(chart.TOTAL_DIM); wts = rng.uniform(0.2, 1.0, len(blocks_))
            for bname, wt in zip(blocks_, wts):
                sl = K.BLOCKS[bname]; w = rng.normal(size=sl.stop - sl.start); v[sl] = wt * w / np.linalg.norm(w)
            v /= np.linalg.norm(v); Q.append(chart.pack(chart.unpack(v).validated()))
elif mode.startswith("file:"):
    Q = list(np.load(mode[5:])["Q"])
else:
    raise SystemExit("mode")
Q = np.array(Q)
vals = []
ids = None
t0 = time.time()
for i, q in enumerate(Q):
    st = chart.unpack(q)
    dirs = K.potential.evaluate_directions(st)
    if ids is None: ids = [d.direction_id for d in dirs]
    vals.append([d.value for d in dirs])
    if i % 10 == 0:
        print(f"{i+1}/{len(Q)} done, {time.time()-t0:.0f}s", flush=True)
        np.savez_compressed(K.SCRATCH / out, Q=Q[:i + 1], values=np.array(vals), ids=np.array(ids))
np.savez_compressed(K.SCRATCH / out, Q=Q, values=np.array(vals), ids=np.array(ids))
print("saved", out, time.time() - t0)
