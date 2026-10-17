from pathlib import Path
p = Path("sk_phase1.py"); s = p.read_text(encoding="utf-8")
# more polishes + sphere quartic BFB check on each subspace
old = 'Vst = Vz(zstar); order = np.argsort(sc["Xs"] @ coef)[:12]; found = []'
new = 'Vst = Vz(zstar); order = np.argsort(sc["Xs"] @ coef)[:30]; found = []'
assert s.count(old) == 1; s = s.replace(old, new)
old2 = "        found.sort(key=lambda tt: tt[0]); k_ = 0\n"
new2 = """        # quartic (BFB) part on the unit sphere of the subspace: homogeneous degree-4 monomials only
        top = np.array([sum(a_ * d_ for a_, d_ in zip(pw, [1, 1, 1, 2, 2, 2] if sc["mode"] == "smsinglet" else [1, 1, 1, 2, 2, 2, 2])) == 4 for pw in sc["monos"]])
        V4z = lambda z: float((sc["X"](np.asarray(z)[None, :])[0] * top) @ coef)
        dirs = sc["dirs"]; v4s = (sc["Xd"] * top[None, :]) @ coef
        for j in np.argsort(v4s)[:6]:
            r = _minimize(lambda z: V4z(z / np.linalg.norm(z)), dirs[j], method="BFGS", options={"gtol": 1e-10, "maxiter": 300})
            zh = np.array(r.x) / np.linalg.norm(r.x)
            if sc["mode"] == "smsinglet": zh[4] = 0; zh /= np.linalg.norm(zh)
            if V4z(zh) < args.eps_bfb * 0.5:
                found.append((-1e30, zh * 1e3))   # treated as a runaway direction below
        found.sort(key=lambda tt: tt[0]); k_ = 0
"""
assert s.count(old2) == 1; s = s.replace(old2, new2)
old3 = '        SCREEN.append({"mode": _mode, "J": _J, "Pinv": np.linalg.pinv(_X(_Z)), "X": _X, "zs": _zs, "Xs": _X(_zs)})'
new3 = '''        _d = _rs.normal(size=(20000, 7))
        if _mode == "smsinglet": _d[:, 4] = 0
        _d /= np.linalg.norm(_d, axis=1)[:, None]
        SCREEN.append({"mode": _mode, "J": _J, "Pinv": np.linalg.pinv(_X(_Z)), "X": _X, "zs": _zs, "Xs": _X(_zs), "monos": _monos, "dirs": _d, "Xd": _X(_d)})'''
assert s.count(old3) == 1; s = s.replace(old3, new3)
p.write_text(s, encoding="utf-8"); compile(s, "sk_phase1.py", "exec"); print("ok")
