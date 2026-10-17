"""Build r2_lp6.py from r2_lp5.py (resumed R2-A run).  New options:
  --vev_light g3221|g3211   g3211 drops the forced-light (1,1)_|Y|=2 (Delta_R^{++} is not vev-light once SU(2)_R is
                            broken at M_U by an O(1) (15,1,3) vev)
  --ew_target <npz>         EW (SM Higgs) direction a* (5 complex slice coordinates of the (1,2)_{1/2} block; key 'a',
                            e.g. a cubic_<tag>_<label>.npz from r2_cubic_rows.py): imposes the EXACT eigen-equation
                            A_(1,2)(c) a* = ew_lambda a* (linear equalities in c) and removes a* from the light/heavy
                            compressions of that block (use '(1,2)_|Y|=1/2:sub3' for two light bidoublets)
  --ew_lambda <float>       eigenvalue of a* (default 1e-7 < eps_lo: the EW tuning then moves it to ~0)
  --random_obj <seed>       instead of max t: maximise a random linear functional of c (box-scaled) at t >= tmin
                            (realisable-spectrum sampling)
"""
from pathlib import Path

src = Path(__file__).with_name("r2_lp5.py").read_text(encoding="utf-8")
out = src


def rep(old, new, count=1):
    global out
    assert out.count(old) == count, (old[:80], out.count(old))
    out = out.replace(old, new)


rep('ap.add_argument("--stall", type=int, default=60)',
    'ap.add_argument("--stall", type=int, default=60)\n'
    'ap.add_argument("--ew_target", default=None)\n'
    'ap.add_argument("--ew_lambda", type=float, default=1.0e-7)\n'
    'ap.add_argument("--random_obj", type=int, default=None)')

rep('VEV = {"(1,1)_|Y|=0": "sub2", "(1,1)_|Y|=2": "sandwich"}',
    'VEV = {"(1,1)_|Y|=0": "sub2", "(1,1)_|Y|=2": "sandwich"}\n'
    'if args.vev_light == "g3211": VEV = {"(1,1)_|Y|=0": "sub2"}\n'
    'elif args.vev_light == "none": VEV = {}\n'
    'kd = kb["(1,2)_|Y|=1/2"]\n'
    'A_EW = None; EQ_A = None; EQ_b = None\n'
    'if args.ew_target:\n'
    '    _ze = np.load(K.SCRATCH / args.ew_target); A_EW = np.asarray(_ze["a"], complex); A_EW = A_EW / np.linalg.norm(A_EW)\n'
    '    Gold[kd] = np.column_stack([Gold[kd], A_EW]) if Gold[kd].shape[1] else A_EW[:, None]\n')

# initial U for the (1,2) block with an EW target (sub3 inside the complement of a*)
rep('        if nl == 4: U += [-math.sin(th) * e(hu) + math.cos(th) * e(su), -math.sin(th) * e(hd) + math.cos(th) * e(sd)]\n'
    '        return orth(U)[:, :nl]',
    '        if nl == 4: U += [-math.sin(th) * e(hu) + math.cos(th) * e(su), -math.sin(th) * e(hd) + math.cos(th) * e(sd)]\n'
    '        if A_EW is not None:\n'
    '            Pp = np.eye(m, dtype=complex) - np.outer(A_EW, A_EW.conj())\n'
    '            return orth([Pp @ e(hu), Pp @ e(hd), Pp @ e(su), Pp @ e(sd)])[:, :nl]\n'
    '        return orth(U)[:, :nl]')

# equality rows (after the variables are defined: nz known) -> insert right after 'kd = kb["(1,2)_|Y|=1/2"]' in the variables section
rep('# doublet subspace (lifted) for exclusion from light-cubic constraints\nkd = kb["(1,2)_|Y|=1/2"]',
    '# doublet subspace (lifted) for exclusion from light-cubic constraints\nkd = kb["(1,2)_|Y|=1/2"]\n'
    'EW_INFO = {}\n'
    'if A_EW is not None:\n'
    '    Mv = np.einsum("ajk,k->aj", Ay[kd], A_EW)   # ny x 5 (complex)\n'
    '    E = np.vstack([np.real(Mv).T, np.imag(Mv).T]); rhs = args.ew_lambda * np.concatenate([np.real(A_EW), np.imag(A_EW)])\n'
    '    uE, sE, vE = np.linalg.svd(E, full_matrices=False); kE = int(np.sum(sE > 1e-10 * sE[0]))\n'
    '    proj = uE[:, :kE].T @ rhs; resid_rhs = float(np.linalg.norm(rhs - uE[:, :kE] @ proj))\n'
    '    EQ_A = np.zeros((kE, nz)); EQ_A[:, :ny] = vE[:kE]; EQ_b = proj / sE[:kE]\n'
    '    EW_INFO = {"rank_eq": kE, "n_eq": int(E.shape[0]), "rhs_out_of_range": resid_rhs, "sv": sE.tolist()}\n'
    '    log(f"EW target {args.ew_target}: {E.shape[0]} real eigen-equations, rank {kE}; rhs outside range {resid_rhs:.2e}")\n')

# pass equalities to linprog
rep('        res = linprog(obj, A_ub=Aub, b_ub=bub, bounds=bounds, method=method, options=opts)',
    '        res = linprog(obj, A_ub=Aub, b_ub=bub, A_eq=EQ_A, b_eq=EQ_b, bounds=bounds, method=method, options=opts)')

# random objective (stage A only)
rep('    else:\n        obj[T_IDX] = -1.0; bounds = [(None, None)] * ny + [(0.0, None)]',
    '    elif args.random_obj is not None:\n'
    '        _rg = np.random.default_rng(args.random_obj); _w = _rg.normal(size=n_par) / boxes\n'
    '        obj[:ny] = Nmat.T @ _w; bounds = [(None, None)] * ny + [(args.tmin, None)]\n'
    '    else:\n        obj[T_IDX] = -1.0; bounds = [(None, None)] * ny + [(0.0, None)]')

# light-cubic exclusion must include the EW direction itself
rep('    D_lift = lift_real(kd, Ucur[kd]) if kd in Ucur else np.zeros((K.TOTAL, 0))',
    '    D_lift = lift_real(kd, (np.column_stack([Ucur[kd], A_EW]) if A_EW is not None else Ucur[kd])) if kd in Ucur else np.zeros((K.TOTAL, 0))')

# random objective: the outer loop must not stop on the t-gain criterion; keep it simple: one outer pass + U updates
rep('    if changed < 1e-10 or (outer >= 1 and gain < 1e-4): break',
    '    if changed < 1e-10 or (outer >= 1 and gain < 1e-4 and args.random_obj is None): break')

# report: EW composition at the solution
rep('    np.savez(K.SCRATCH / f"{out}.npz", c=c, t=t, z=z, ids=np.array(ids), **{f"U{k}": U_cur[k] for k in sub_blocks})',
    '    if A_EW is not None:\n'
    '        import r2_compose as _RC\n'
    '        _Ac = np.einsum("p,pij->ij", c, A[kd]); _Ac = 0.5 * (_Ac + _Ac.conj().T); _w, _V = np.linalg.eigh(_Ac)\n'
    '        _res = float(np.linalg.norm(_Ac @ A_EW - args.ew_lambda * A_EW)); _ov = float(abs(np.vdot(_V[:, 0], A_EW)))\n'
    '        _nt = _RC.Neutral(args.tag); _cm = _nt.comp_of_a(_V[:, 0])\n'
    '        report["ew"] = dict(EW_INFO, eig_residual=_res, lowest_eig=float(_w[0]), next_eig=float(_w[1]), overlap_lowest_with_target=_ov,\n'
    '                            r_abs=float(abs(_cm["r"])), s=[float(np.real(_cm["s"])), float(np.imag(_cm["s"]))], frac=_cm["frac"])\n'
    '        log(f"EW direction: |A a* - lam a*| = {_res:.2e}; lowest eig {_w[0]:.3e} (next {_w[1]:.3e}); overlap {_ov:.12f}; |r| = {abs(_cm[\'r\']):.5g}, s = {_cm[\'s\']:.5g}; frac {_cm[\'frac\']}")\n'
    '        json.dump(report, open(K.SCRATCH / f"{out}.json", "w", encoding="utf-8"), indent=1, default=float)\n'
    '    np.savez(K.SCRATCH / f"{out}.npz", c=c, t=t, z=z, ids=np.array(ids), **{f"U{k}": U_cur[k] for k in sub_blocks})')

rep("abs(t_hist[-1] - t_hist[-1 - args.stall]) <= 1e-7 * max(abs(t), 1e-12) and not STAGE_B:",
    "abs(t_hist[-1] - t_hist[-1 - args.stall]) <= 1e-7 * max(abs(t), 1e-12) and not STAGE_B and args.random_obj is None:")

# competitor margin for SM-singlet-subspace points: D-parity (an SO(10) element) maps (p, a, r=0) -> (-p, a, r=0), so the
# chart distance overstates how far a valley point (r -> 0, s shifted) is from z*; use a D-image-aware distance
rep('def margin_factor(q): d = float(np.linalg.norm(q - q0)); return min(1.0, (d / args.d0) ** 4)',
    'def margin_factor(q): d = float(np.linalg.norm(q - q0)); return min(1.0, (d / args.d0) ** 4)\n'
    'def margin_z(z):\n'
    '    z = np.asarray(z, float)\n'
    '    d = float(np.linalg.norm([abs(z[0]) - abs(zstar[0]), z[1] - zstar[1], z[2] - zstar[2], math.hypot(z[3], z[4]) - abs(zstar[3]), abs(z[5]) - abs(zstar[5]), z[6] - zstar[6]]))\n'
    '    return min(1.0, (d / args.d0) ** 4)')
rep('        if not in_g3221_orbit(z): COMP_J.append(row); COMP_M.append(margin_factor(qq))',
    '        if not in_g3221_orbit(z): COMP_J.append(row); COMP_M.append(margin_z(z))')
rep('                    qm = chart.pack(state_of_z(zm)); mf = margin_factor(qm)',
    '                    qm = chart.pack(state_of_z(zm)); mf = margin_z(zm)')

# row scaling of competitor cuts (deep competitor points have |J| ~ 1e3-1e4: HiGHS reported 'Unknown/primal infeasible')
rep("        row = np.zeros(nz); row[:ny] = (VAL0 - row_J) @ Nmat; row[T_IDX] = args.mu * mf; add_fixed(row, 0.0, 'competitor')",
    "        row = np.zeros(nz); row[:ny] = (VAL0 - row_J) @ Nmat; row[T_IDX] = args.mu * mf; row = row / max(1.0, float(np.max(np.abs(row)))); add_fixed(row, 0.0, 'competitor')")
rep("row = np.zeros(nz); row[:ny] = (VAL0 - Jq) @ Nmat; row[T_IDX] = args.mu * mf; fixed_A.append(row);",
    "row = np.zeros(nz); row[:ny] = (VAL0 - Jq) @ Nmat; row[T_IDX] = args.mu * mf; row = row / max(1.0, float(np.max(np.abs(row)))); fixed_A.append(row);")

rep('def J_at_state(state):',
    'OBJ_J = None\n'
    'def _load_obj_J():\n'
    '    global OBJ_J\n'
    '    _f, _k = args.obj_point.rsplit(":", 1); _bb = np.load(K.SCRATCH / _f)\n'
    '    OBJ_J = np.asarray(_bb["J"], float)[int(_k)] if "J" in _bb.files else J_from_values(_bb["values"], [str(x) for x in _bb["ids"]])[int(_k)]\n'
    'if args.obj_point is not None: _load_obj_J()\n\n\n'
    'def J_at_state(state):')
# --obj_point <npz>:<idx>: maximise V_c(q_k) - V_c(q*) for a banked point (how far can it be lifted?) at t >= tmin
rep('ap.add_argument("--random_obj", type=int, default=None)',
    'ap.add_argument("--random_obj", type=int, default=None)\n'
    'ap.add_argument("--obj_point", default=None)')
rep('    elif args.random_obj is not None:\n',
    '    elif args.obj_point is not None:\n'
    '        obj[:ny] = -((OBJ_J - VAL0) @ Nmat); bounds = [(None, None)] * ny + [(args.tmin, None)]\n'
    '    elif args.random_obj is not None:\n')
rep("if changed < 1e-10 or (outer >= 1 and gain < 1e-4 and args.random_obj is None): break",
    "if changed < 1e-10 or (outer >= 1 and gain < 1e-4 and args.random_obj is None and args.obj_point is None): break")
rep("and not STAGE_B and args.random_obj is None:", "and not STAGE_B and args.random_obj is None and args.obj_point is None:")
rep('    log(f"saved {out}: t = {t:.6g};',
    '    if args.obj_point is not None: log(f"objective: max V(q_k) - V* = {float((OBJ_J - VAL0) @ c):.6g}")\n'
    '    log(f"saved {out}: t = {t:.6g};')

# bug fix: without a cubic file V4_up = 0 and the 'pure doublet ray' BFB row reads 0 >= eps_bfb (spurious infeasibility)
rep("    BFB_J.append((V4_up * deg4 / 24.0)[None, :])",
    "    if cubfile is not None: BFB_J.append((V4_up * deg4 / 24.0)[None, :])")

# stage B: optionally include the light (v_R-scale, non-Goldstone) exchange R_light = sum_s (v_s.b)^2 / (v_s.H v_s) with the
# light eigenvectors v_s frozen at c_ref (quadratic-over-linear: convex in y) -> lambda_eff_all = V4/6 - (R_h + R_l)/2
rep('ap.add_argument("--obj_point", default=None)',
    'ap.add_argument("--obj_point", default=None)\n'
    'ap.add_argument("--leff_light", action="store_true")')
rep('    beta_a = by @ P_heavy  # ny x nh\n',
    '    beta_a = by @ P_heavy  # ny x nh\n'
    '    global V_l, Hl_a, bl_a\n'
    '    if args.leff_light:\n'
    '        # exact total response R = b^T P (P^T H P)^-1 P^T b on the complement of the Goldstones and the lifted light doublets\n'
    '        Dd = lift_real(kd, (np.column_stack([U_cur[kd], A_EW]) if A_EW is not None else U_cur[kd]))\n'
    '        Gt = np.linalg.svd(Tgold, full_matrices=False)[0][:, :35] if Tgold.shape[1] >= 35 else Tgold\n'
    '        Sx = np.column_stack([Gt, Dd]); uu_, ss_, _ = np.linalg.svd(Sx, full_matrices=True); rr_ = int(np.sum(ss_ > 1e-8)); P_heavy = uu_[:, rr_:]\n'
    '        tmp2 = np.tensordot(Nmat.T, HESS, axes=(1, 0)); M_a = np.array([P_heavy.T @ tmp2[a] @ P_heavy for a in range(ny)]); del tmp2\n'
    '        beta_a = by @ P_heavy; V_l = None\n'
    '        log(f"response setup (leff_light): exact total response on {P_heavy.shape[1]} dims (complement of {rr_} Goldstone+light-doublet dims)")\n')
rep('    grad = 2 * beta_a @ Mi_b - np.einsum("i,aij,j->a", Mi_b, M_a, Mi_b)\n'
    '    return R, grad, float(np.linalg.eigvalsh(M)[0])',
    '    grad = 2 * beta_a @ Mi_b - np.einsum("i,aij,j->a", Mi_b, M_a, Mi_b)\n'
    '    if args.leff_light and V_l is not None:\n'
    '        Ml = np.einsum("a,aij->ij", y, Hl_a); bl = y @ bl_a; Mib = np.linalg.solve(Ml, bl)\n'
    '        R = R + float(bl @ Mib); grad = grad + 2 * bl_a @ Mib - np.einsum("i,aij,j->a", Mib, Hl_a, Mib)\n'
    '    return R, grad, float(np.linalg.eigvalsh(M)[0])')
rep('P_heavy = None; M_a = None; beta_a = None', 'P_heavy = None; M_a = None; beta_a = None; V_l = None; Hl_a = None; bl_a = None')

out = out.replace('"""R2-A cutting-plane LP v5', '"""R2-A cutting-plane LP v6 (= v5 + --vev_light g3211, --ew_target, --random_obj; built by _make_lp6.py)\nv5:', 1)
Path(__file__).with_name("r2_lp6.py").write_text(out, encoding="utf-8")
print("r2_lp6.py written")
