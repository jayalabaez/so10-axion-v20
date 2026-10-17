import pathlib
p = pathlib.Path(__file__).resolve().parent / "k3_lp4.py"; s = p.read_text(encoding="utf-8")
rep = [
 # distance-scaled competitor margin: margin_k = mu * t * min(1, (d_k/d0)^4), d_k = chart distance from q*
 ("ap.add_argument(\"--mu\", type=float, default=0.1, help=\"competitor margin in units of t\")",
  "ap.add_argument(\"--mu\", type=float, default=0.1, help=\"competitor margin in units of t\")\nap.add_argument(\"--d0\", type=float, default=0.5, help=\"competitor margin scale: margin = mu t min(1,(d/d0)^4)\")"),
 ("COMP_J = []\nfor f in fits:\n    coords = np.array([[float(q @ d) / float(d @ d) for d in SUBDIRS] for q in f.Q])\n    for row, z in zip(f.J, coords):\n        if not in_g3221_orbit(z): COMP_J.append(row)\nCOMP_J = np.array(COMP_J) if COMP_J else np.zeros((0, n_par))",
  "COMP_J = []; COMP_M = []\ndef margin_factor(q): d = float(np.linalg.norm(q - q0)); return min(1.0, (d / args.d0) ** 4)\nfor f in fits:\n    coords = np.array([[float(q @ d) / float(d @ d) for d in SUBDIRS] for q in f.Q])\n    for row, z, qq in zip(f.J, coords, f.Q):\n        if not in_g3221_orbit(z): COMP_J.append(row); COMP_M.append(margin_factor(qq))\nCOMP_J = np.array(COMP_J) if COMP_J else np.zeros((0, n_par)); COMP_M = np.array(COMP_M)"),
 ("    for row_J in COMP_J:\n        row = np.zeros(nz); row[:ny] = (VAL0 - row_J) @ Nmat; row[T_IDX] = args.mu; add_fixed(row, 0.0, 'competitor')",
  "    for row_J, mf in zip(COMP_J, COMP_M):\n        row = np.zeros(nz); row[:ny] = (VAL0 - row_J) @ Nmat; row[T_IDX] = args.mu * mf; add_fixed(row, 0.0, 'competitor')"),
 ("                    if Vm < Vst + args.mu * t - 1e-9:\n                        Jq = J_at_state(state_of_z(zm)); COMP_J = np.vstack([COMP_J, Jq[None, :]])\n                        row = np.zeros(nz); row[:ny] = (VAL0 - Jq) @ Nmat; row[T_IDX] = args.mu; fixed_A.append(row); fixed_b.append(0.0); fixed_cls.append('competitor')",
  "                    qm = chart.pack(state_of_z(zm)); mf = margin_factor(qm)\n                    if Vm < Vst + args.mu * t * mf - 1e-12:\n                        Jq = J_at_state(state_of_z(zm)); COMP_J = np.vstack([COMP_J, Jq[None, :]]); COMP_M = np.append(COMP_M, mf)\n                        row = np.zeros(nz); row[:ny] = (VAL0 - Jq) @ Nmat; row[T_IDX] = args.mu * mf; fixed_A.append(row); fixed_b.append(0.0); fixed_cls.append('competitor')"),
 ("    global COMP_J, BFB_J\n", "    global COMP_J, BFB_J, COMP_M\n"),
 ("                        if lowest_total is None or Vm - Vst < lowest_total[0]: lowest_total = (Vm - Vst, zm.tolist(), f.mode)",
  "                        if lowest_total is None or Vm - Vst < lowest_total[0]: lowest_total = (Vm - Vst, zm.tolist(), f.mode + f\" d={np.linalg.norm(qm - q0):.3f} mf={mf:.2e}\")"),
 # block rays bank
 ("    try:\n        rp = np.load(K.SCRATCH / \"rays_pts.npz\"); Jr = J_from_values(rp[\"values\"], [str(x) for x in rp[\"ids\"]])\n        nr = np.linalg.norm(rp[\"Q\"], axis=1); BFB_J.append((Jr * deg4[None, :]) / nr[:, None] ** 4)\n        log(f\"BFB: {len(nr)} random rays loaded\")\n    except FileNotFoundError:\n        log(\"BFB: rays_pts.npz not found (random-ray cuts skipped)\")",
  "    for fn in (\"rays_pts.npz\", \"blockrays_pts.npz\"):\n        try:\n            rp = np.load(K.SCRATCH / fn); Jr = J_from_values(rp[\"values\"], [str(x) for x in rp[\"ids\"]])\n            nr = np.linalg.norm(rp[\"Q\"], axis=1); BFB_J.append((Jr * deg4[None, :]) / nr[:, None] ** 4)\n            log(f\"BFB: {len(nr)} rays loaded from {fn}\")\n        except FileNotFoundError:\n            log(f\"BFB: {fn} not found (skipped)\")"),
 ("    comp, bfb = banks()\n    out[\"bfb_bank_min_V4\"] = float(np.min(bfb @ c)); out[\"competitor_bank_min_gap\"] = float(np.min(comp @ c - VAL0 @ c))", "XX"),
]
missing = []
for a, b in rep:
    if b == "XX": continue
    if a not in s: missing.append(a[:80])
    s = s.replace(a, b)
p.write_text(s, encoding="utf-8"); print("lp4 patched; missing:", missing)
# k3_eval_points: add blockrays mode
p2 = pathlib.Path(__file__).resolve().parent / "k3_eval_points.py"; s2 = p2.read_text(encoding="utf-8")
a = 'elif mode.startswith("file:"):'
b = '''elif mode == "blockrays":
    names = list(K.BLOCKS); slices = [K.BLOCKS[b] for b in names]
    plan = [("Phi210",), ("Sigma126bar",), ("H10",), ("Phi210", "Sigma126bar"), ("Phi210", "H10"), ("Sigma126bar", "H10"), ("H10", "S"), ("Sigma126bar", "S"), ("Phi210", "Phi17"), ("H10", "Phi17"), ("Sigma126bar", "Phi17")]
    counts = [50, 60, 30, 15, 10, 10, 5, 5, 5, 5, 5]
    for blocks_, cnt in zip(plan, counts):
        for _ in range(cnt):
            v = np.zeros(chart.TOTAL_DIM)
            for bname in blocks_:
                sl = K.BLOCKS[bname]; w = rng.normal(size=sl.stop - sl.start); v[sl] = w / np.linalg.norm(w)
            v /= np.linalg.norm(v); Q.append(chart.pack(chart.unpack(v).validated()))
elif mode.startswith("file:"):'''
assert a in s2; s2 = s2.replace(a, b); p2.write_text(s2, encoding="utf-8"); print("eval_points patched")
