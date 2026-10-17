import pathlib
here = pathlib.Path(__file__).resolve().parent
p = here / "k3_eval_points.py"; s = p.read_text(encoding="utf-8")
a = 'elif mode.startswith("file:"):'
b = '''elif mode == "hsrays":
    # random rays in the H10 (+) Sigma126bar subspace with random relative weight (the runaway direction family),
    # plus H+Sigma+Phi and H+Sigma+S mixtures
    plan = [(("H10", "Sigma126bar"), 90), (("H10", "Sigma126bar", "Phi210"), 40), (("H10", "Sigma126bar", "S"), 10), (("H10", "Sigma126bar", "Phi210", "S"), 10)]
    for blocks_, cnt in plan:
        for _ in range(cnt):
            v = np.zeros(chart.TOTAL_DIM); wts = rng.uniform(0.2, 1.0, len(blocks_))
            for bname, wt in zip(blocks_, wts):
                sl = K.BLOCKS[bname]; w = rng.normal(size=sl.stop - sl.start); v[sl] = wt * w / np.linalg.norm(w)
            v /= np.linalg.norm(v); Q.append(chart.pack(chart.unpack(v).validated()))
elif mode.startswith("file:"):'''
assert a in s; s = s.replace(a, b); p.write_text(s, encoding="utf-8"); print("eval_points: hsrays added")
p = here / "k3_lp4.py"; s = p.read_text(encoding="utf-8")
a = '    for fn in ("rays_pts.npz", "blockrays_pts.npz", "tripletrays_pts.npz"):'
b = '    for fn in ("rays_pts.npz", "blockrays_pts.npz", "tripletrays_pts.npz", "hsrays_pts.npz"):'
assert a in s; s = s.replace(a, b); p.write_text(s, encoding="utf-8"); print("lp4: hsrays in BFB bank")
p = here / "k3_verify.py"; s = p.read_text(encoding="utf-8")
a = '        for fn in ("rays_pts.npz", "blockrays_pts.npz", "tripletrays_pts.npz"):'
b = '        for fn in ("rays_pts.npz", "blockrays_pts.npz", "tripletrays_pts.npz", "hsrays_pts.npz"):'
assert a in s; s = s.replace(a, b)
# also let verify accept extra banks through an environment variable (comma-separated npz names)
a = "        bfb.append((V4_up * deg4 / 24.0)[None, :])\n        _banks = (np.array(comp), np.vstack(bfb))"
b = ("        bfb.append((V4_up * deg4 / 24.0)[None, :])\n"
     "        import os\n"
     "        for fn in [x for x in os.environ.get('K3_EXTRA_BANKS', '').split(',') if x]:\n"
     "            eb = np.load(K.SCRATCH / fn); Je = J_from_values(eb['values'], [str(x) for x in eb['ids']]); ne = np.linalg.norm(eb['Q'], axis=1)\n"
     "            for row, qq in zip(Je, eb['Q']):\n"
     "                if np.linalg.norm(qq - q0) > 1e-6: comp.append(row)\n"
     "            bfb.append((Je * deg4[None, :]) / ne[:, None] ** 4)\n"
     "        _banks = (np.array(comp), np.vstack(bfb))")
assert a in s; s = s.replace(a, b); p.write_text(s, encoding="utf-8"); print("verify: hsrays + K3_EXTRA_BANKS")
