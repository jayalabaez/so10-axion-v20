import pathlib
p = pathlib.Path(__file__).resolve().parent / "k3_lp4.py"; s = p.read_text(encoding="utf-8")
n0 = len(s)
rep = [
 ("        if n_new == 0 or (worst < 1e-12 and it > 5): break\n    return result, res, last_search",
  "        if n_new == 0 or (worst < 1e-9 and it > 5 and n_comp_added_this == 0): break\n"
  "    Aall = np.array(fixed_A + cuts_A); ball = np.array(fixed_b + cuts_b); clsall = fixed_cls + cuts_cls\n"
  "    slack = ball - Aall @ z; active = {}\n"
  "    for cl, sl_ in zip(clsall, slack):\n"
  "        if abs(sl_) < 1e-9: active[cl] = active.get(cl, 0) + 1\n"
  "    log(f\"  active constraints at optimum: {active} (of {len(clsall)})\")\n"
  "    return result, res, last_search"),
 ("        z = res.x; y = z[:ny]; t = z[T_IDX]; worst = 0.0; n_new = 0; c = Nmat @ y",
  "        z = res.x; y = z[:ny]; t = z[T_IDX]; worst = 0.0; n_new = 0; c = Nmat @ y; n_comp_added_this = 0"),
 ("                        n_new += 1; n_comp_added += 1; worst = max(worst, Vst - Vm)",
  "                        n_new += 1; n_comp_added += 1; n_comp_added_this += 1; worst = max(worst, Vst - Vm)"),
 ("    fixed_A, fixed_b = [], []\n    def add_fixed(row, rhs): fixed_A.append(row); fixed_b.append(rhs)",
  "    fixed_A, fixed_b, fixed_cls = [], [], []\n    def add_fixed(row, rhs, cls='other'): fixed_A.append(row); fixed_b.append(rhs); fixed_cls.append(cls)"),
 ("row[:ny] = Nmat[i]; add_fixed(row.copy(), boxes[i]); add_fixed(-row, boxes[i])",
  "row[:ny] = Nmat[i]; add_fixed(row.copy(), boxes[i], 'box'); add_fixed(-row, boxes[i], 'box')"),
 ("                        add_fixed(row.copy(), delta); add_fixed(-row, delta)",
  "                        add_fixed(row.copy(), delta, 'invariance'); add_fixed(-row, delta, 'invariance')"),
 ("row[:ny] = (VAL0 - row_J) @ Nmat; row[T_IDX] = args.mu; add_fixed(row, 0.0)",
  "row[:ny] = (VAL0 - row_J) @ Nmat; row[T_IDX] = args.mu; add_fixed(row, 0.0, 'competitor')"),
 ("row[:ny] = -(row_J @ Nmat); add_fixed(row, -args.eps_bfb)",
  "row[:ny] = -(row_J @ Nmat); add_fixed(row, -args.eps_bfb, 'bfb')"),
 ("row[:ny] = V4y / 6; add_fixed(row, args.lam_direct_max)", "row[:ny] = V4y / 6; add_fixed(row, args.lam_direct_max, 'lamdir')"),
 ("row[:ny] = -V4y / 6; add_fixed(row, -args.lam_direct_min)", "row[:ny] = -V4y / 6; add_fixed(row, -args.lam_direct_min, 'lamdir')"),
 ("    cuts_A, cuts_b = [], []\n    rng2 = np.random.default_rng(1)", "    cuts_A, cuts_b, cuts_cls = [], [], []\n    rng2 = np.random.default_rng(1)"),
 ("            if kind == \"sandwich\": cuts_A.append(-row); cuts_b.append(-eps_lo); cuts_A.append(row.copy()); cuts_b.append(eps_hi)\n            else: row[T_IDX] = -1.0; cuts_A.append(-row); cuts_b.append(0.0)\n        if kind.startswith(\"sub\"):\n            U = Ucur[k]\n            for l in range(U.shape[1]):\n                row = rayleigh_row(k, U[:, l]); cuts_A.append(-row); cuts_b.append(-eps_lo); cuts_A.append(row.copy()); cuts_b.append(eps_hi)",
  "            if kind == \"sandwich\": cuts_A.append(-row); cuts_b.append(-eps_lo); cuts_A.append(row.copy()); cuts_b.append(eps_hi); cuts_cls += ['light', 'light']\n            else: row[T_IDX] = -1.0; cuts_A.append(-row); cuts_b.append(0.0); cuts_cls.append('heavy')\n        if kind.startswith(\"sub\"):\n            U = Ucur[k]\n            for l in range(U.shape[1]):\n                row = rayleigh_row(k, U[:, l]); cuts_A.append(-row); cuts_b.append(-eps_lo); cuts_A.append(row.copy()); cuts_b.append(eps_hi); cuts_cls += ['light', 'light']"),
 ("                row = np.zeros(nz); row[:ny] = sgn * UNIT[:, j, j]; cuts_A.append(row); cuts_b.append(UNIT_BOUND)",
  "                row = np.zeros(nz); row[:ny] = sgn * UNIT[:, j, j]; cuts_A.append(row); cuts_b.append(UNIT_BOUND); cuts_cls.append('unitarity')"),
 ("                    if w[j] < eps_lo - 1e-13: cuts_A.append(-row); cuts_b.append(-eps_lo); n_new += 1; worst = max(worst, eps_lo - w[j])\n                    if w[j] > eps_hi + 1e-13: cuts_A.append(row.copy()); cuts_b.append(eps_hi); n_new += 1; worst = max(worst, w[j] - eps_hi)\n            else:",
  "                    if w[j] < eps_lo - 1e-13: cuts_A.append(-row); cuts_b.append(-eps_lo); cuts_cls.append('light'); n_new += 1; worst = max(worst, eps_lo - w[j])\n                    if w[j] > eps_hi + 1e-13: cuts_A.append(row.copy()); cuts_b.append(eps_hi); cuts_cls.append('light'); n_new += 1; worst = max(worst, w[j] - eps_hi)\n            else:"),
 ("                            row = rayleigh_row(k, Q @ v[:, j]); row[T_IDX] = -1.0; cuts_A.append(-row); cuts_b.append(0.0); n_new += 1; worst = max(worst, t - w[j])",
  "                            row = rayleigh_row(k, Q @ v[:, j]); row[T_IDX] = -1.0; cuts_A.append(-row); cuts_b.append(0.0); cuts_cls.append('heavy'); n_new += 1; worst = max(worst, t - w[j])"),
 ("                        if w[j] < eps_lo - 1e-13: cuts_A.append(-row); cuts_b.append(-eps_lo); n_new += 1; worst = max(worst, eps_lo - w[j])\n                        if w[j] > eps_hi + 1e-13: cuts_A.append(row.copy()); cuts_b.append(eps_hi); n_new += 1; worst = max(worst, w[j] - eps_hi)\n        if UNIT is not None:",
  "                        if w[j] < eps_lo - 1e-13: cuts_A.append(-row); cuts_b.append(-eps_lo); cuts_cls.append('light'); n_new += 1; worst = max(worst, eps_lo - w[j])\n                        if w[j] > eps_hi + 1e-13: cuts_A.append(row.copy()); cuts_b.append(eps_hi); cuts_cls.append('light'); n_new += 1; worst = max(worst, w[j] - eps_hi)\n        if UNIT is not None:"),
 ("                    cuts_A.append(row); cuts_b.append(UNIT_BOUND); n_new += 1; worst = max(worst, abs(w[j]) - UNIT_BOUND)",
  "                    cuts_A.append(row); cuts_b.append(UNIT_BOUND); cuts_cls.append('unitarity'); n_new += 1; worst = max(worst, abs(w[j]) - UNIT_BOUND)"),
 ("                    row = np.zeros(nz); row[:ny] = np.sign(val) * (by @ v); cuts_A.append(row); cuts_b.append(args.delta_b); n_new += 1; n_lightb += 1",
  "                    row = np.zeros(nz); row[:ny] = np.sign(val) * (by @ v); cuts_A.append(row); cuts_b.append(args.delta_b); cuts_cls.append('lightb'); n_new += 1; n_lightb += 1"),
 ("                row = np.zeros(nz); row[:ny] = gR; row[R_IDX] = -1.0; cuts_A.append(row); cuts_b.append(float(gR @ y - R)); n_new += 1; worst = max(worst, R - rho)",
  "                row = np.zeros(nz); row[:ny] = gR; row[R_IDX] = -1.0; cuts_A.append(row); cuts_b.append(float(gR @ y - R)); cuts_cls.append('kelley'); n_new += 1; worst = max(worst, R - rho)"),
 ("row = np.zeros(nz); row[:ny] = -(BFB_J_row @ Nmat); fixed_A.append(row); fixed_b.append(-args.eps_bfb); n_new += 1; n_bfb_added += 1",
  "row = np.zeros(nz); row[:ny] = -(BFB_J_row @ Nmat); fixed_A.append(row); fixed_b.append(-args.eps_bfb); fixed_cls.append('bfb'); n_new += 1; n_bfb_added += 1"),
 ("row = np.zeros(nz); row[:ny] = (VAL0 - Jq) @ Nmat; row[T_IDX] = args.mu; fixed_A.append(row); fixed_b.append(0.0)\n                        n_new += 1; n_comp_added += 1",
  "row = np.zeros(nz); row[:ny] = (VAL0 - Jq) @ Nmat; row[T_IDX] = args.mu; fixed_A.append(row); fixed_b.append(0.0); fixed_cls.append('competitor')\n                        n_new += 1; n_comp_added += 1"),
]
missing = []
for a, b in rep:
    if a not in s: missing.append(a[:70])
    s = s.replace(a, b)
p.write_text(s, encoding="utf-8")
print("patched; missing:", missing, "| cls appends:", s.count("cuts_cls.append"), s.count("fixed_cls.append"))
