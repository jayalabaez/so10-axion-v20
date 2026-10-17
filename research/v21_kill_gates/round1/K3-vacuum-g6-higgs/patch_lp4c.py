import pathlib
here = pathlib.Path(__file__).resolve().parent
# ---- k3_lp4.py: competitor cuts only for strictly lower points; triplet rays in the BFB bank
p = here / "k3_lp4.py"; s = p.read_text(encoding="utf-8")
rep = [
 ("                    if Vm < Vst + args.mu * t * mf - 1e-12:",
  "                    if Vm < Vst - 1e-10 * max(1.0, abs(Vst)):   # strictly lower only; near-degenerate higher points are reported, not cut"),
 ("    for fn in (\"rays_pts.npz\", \"blockrays_pts.npz\"):", "    for fn in (\"rays_pts.npz\", \"blockrays_pts.npz\", \"tripletrays_pts.npz\"):"),
 ("            if lowest_total is not None: log(f\"  it {it}: competitor lower by {-lowest_total[0]:.4g} at z = {np.round(lowest_total[1], 4)} [{lowest_total[2]}]\")",
  "            if lowest_total is not None: log(f\"  it {it}: competitor lower by {-lowest_total[0]:.4g} at z = {np.round(lowest_total[1], 4)} [{lowest_total[2]}]\")\n"
  "            elif last_search is not None and it % 50 == 49: log(f\"  it {it}: subspace min - V* = {last_search['V_min'] - last_search['V_star']:.3e} [{last_search['mode']}]\")"),
]
missing = [a[:60] for a, b in rep if a not in s]
for a, b in rep: s = s.replace(a, b)
p.write_text(s, encoding="utf-8"); print("lp4 patched; missing:", missing)
# ---- k3_verify.py banks: include block and triplet rays
p = here / "k3_verify.py"; s = p.read_text(encoding="utf-8")
a = "        rp = np.load(K.SCRATCH / \"rays_pts.npz\"); Jr = J_from_values(rp[\"values\"], [str(x) for x in rp[\"ids\"]]); nr = np.linalg.norm(rp[\"Q\"], axis=1)\n        bfb.append((Jr * deg4[None, :]) / nr[:, None] ** 4); bfb.append((V4_up * deg4 / 24.0)[None, :])"
b = "        for fn in (\"rays_pts.npz\", \"blockrays_pts.npz\", \"tripletrays_pts.npz\"):\n            rp = np.load(K.SCRATCH / fn); Jr = J_from_values(rp[\"values\"], [str(x) for x in rp[\"ids\"]]); nr = np.linalg.norm(rp[\"Q\"], axis=1)\n            bfb.append((Jr * deg4[None, :]) / nr[:, None] ** 4)\n        bfb.append((V4_up * deg4 / 24.0)[None, :])"
assert a in s; s = s.replace(a, b); p.write_text(s, encoding="utf-8"); print("verify patched")
# ---- k3_eval_points.py: tripletrays mode (random rays inside the complex (1,1,3) triplet of Sigma: sig_std, T- sig_std, T+ sig_std)
p = here / "k3_eval_points.py"; s = p.read_text(encoding="utf-8")
a = 'elif mode.startswith("file:"):'
b = '''elif mode == "tripletrays":
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
elif mode.startswith("file:"):'''
assert a in s; s = s.replace(a, b); p.write_text(s, encoding="utf-8"); print("eval_points patched")
