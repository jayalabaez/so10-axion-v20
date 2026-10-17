from pathlib import Path
p = Path("r2a_lift_lp.py"); s = p.read_text(encoding="utf-8")
def rep(a, b):
    global s
    assert s.count(a) == 1, a[:60]; s = s.replace(a, b)
rep('ap.add_argument("--no_unitarity", action="store_true")',
    'ap.add_argument("--no_unitarity", action="store_true")\n'
    'ap.add_argument("--bfb", action="store_true", help="add the BFB ray bank (V4 >= 1e-4) as in r2_lp5/6")\n'
    'ap.add_argument("--comp", default="", help="comma-separated competitor banks (V(q) >= V*, no margin); \'sub\' = SM-singlet bank points")\n'
    'ap.add_argument("--heavy_floor", type=float, default=0.0, help="Goldstone-complement floor for blocks without light content")\n'
    'ap.add_argument("--maxit", type=int, default=400)')
rep('def rq(k, v):', '''def Jrows(npzname):
    bb = np.load(K.SCRATCH / npzname)
    if "J" in bb.files: return np.asarray(bb["J"], float), bb["Q"]
    dids = [str(x) for x in bb["ids"]]; di = {d: j for j, d in enumerate(dids)}; vals = bb["values"]; JJ = np.zeros((vals.shape[0], n_par))
    for i, pid in enumerate(ids):
        comp, did = pid.split("::"); j = di[did]
        JJ[:, i] = vals[:, j].real if comp == "lambda" else (2 * vals[:, j].real if comp == "re" else -2 * vals[:, j].imag)
    return JJ, bb["Q"]


deg4 = deg == 4; q0 = Z["q"]
EXTRA_ROWS = []   # (row over y, rhs) for A_ub
if args.bfb:
    for fn in ("rays_pts.npz", "blockrays_pts.npz", "tripletrays_pts.npz", "hsrays_pts.npz", "smsinglet_pts.npz", "deltar_pts.npz"):
        JJ, QQ = Jrows(fn); nr = np.linalg.norm(QQ, axis=1)
        for row in (JJ * deg4[None, :]) / nr[:, None] ** 4: EXTRA_ROWS.append((-(row @ N), -1e-4))
    print(f"BFB rays: {len(EXTRA_ROWS)}")
ncomp = 0
for fn in [x for x in args.comp.split(",") if x]:
    if fn == "sub":
        for f2 in ("smsinglet_pts.npz", "deltar_pts.npz"):
            JJ, QQ = Jrows(f2)
            for row, qq in zip(JJ, QQ):
                if np.linalg.norm(qq - q0) > 0.05: r_ = (VAL0 - row) @ N; EXTRA_ROWS.append((r_ / max(1.0, np.max(np.abs(r_))), 0.0)); ncomp += 1
        continue
    JJ, QQ = Jrows(fn)
    for row, qq in zip(JJ, QQ):
        if np.linalg.norm(qq - q0) > 1e-6: r_ = (VAL0 - row) @ N; EXTRA_ROWS.append((r_ / max(1.0, np.max(np.abs(r_))), 0.0)); ncomp += 1
print(f"competitor rows: {ncomp}")


def rq(k, v):''')
rep('''            lo = args.eps_lo if (k == kd and A_EW is not None) else 0.0
            Aub.append(-rq(k, Qc[k][:, j])); bub.append(-lo)''', '''            lo = args.eps_lo if (k == kd and A_EW is not None) else floor_of(k)
            Aub.append(-rq(k, Qc[k][:, j])); bub.append(-lo)
    for r_, b_ in EXTRA_ROWS: Aub.append(r_); bub.append(b_)''')
rep('''            lo = args.eps_lo if (k == kd and A_EW is not None) else 0.0
            for j in range(len(w)):''', '''            lo = args.eps_lo if (k == kd and A_EW is not None) else floor_of(k)
            for j in range(len(w)):''')
rep('def solve_for(obj_vec):', '''SUBLIGHT = {"(1,1)_|Y|=0", "(1,2)_|Y|=1/2"}
def floor_of(k):
    lab = labels[k]
    if lab in LIGHT or lab in SUBLIGHT: return 0.0
    return args.heavy_floor


def solve_for(obj_vec):''')
rep('    for it in range(400):', '    for it in range(args.maxit):')
rep('''        res = linprog(-obj_vec, A_ub=np.array(Aub), b_ub=np.array(bub), A_eq=EQ_A, b_eq=EQ_b, bounds=[(None, None)] * ny, method="highs")
        if res.status != 0: return None, res, it''', '''        res = linprog(-obj_vec, A_ub=np.array(Aub), b_ub=np.array(bub), A_eq=EQ_A, b_eq=EQ_b, bounds=[(None, None)] * ny, method="highs")
        if res.status != 0:
            res = linprog(-obj_vec, A_ub=np.array(Aub), b_ub=np.array(bub), A_eq=EQ_A, b_eq=EQ_b, bounds=[(None, None)] * ny, method="highs-ipm")
        if res.status != 0: return None, res, it''')
p.write_text(s, encoding="utf-8"); print("patched")
