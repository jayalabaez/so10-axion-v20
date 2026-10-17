import pathlib
here = pathlib.Path(__file__).resolve().parent
# ---- k3_descend.py: store every evaluated point's direction values as a bank (Q, values, ids) for LP feedback
p = here / "k3_descend.py"; s = p.read_text(encoding="utf-8")
rep = [
 ("def value_at(q):\n    dirs = K.potential.evaluate_directions(chart.unpack(q)); jac = K.potential.coefficient_jacobian(dirs)\n    return float(sum(c[i] * jac[pid] for i, pid in enumerate(ids)))",
  "BANK_Q, BANK_V, BANK_IDS = [], [], None\ndef value_at(q):\n    global BANK_IDS\n    dirs = K.potential.evaluate_directions(chart.unpack(q)); jac = K.potential.coefficient_jacobian(dirs)\n"
  "    if BANK_IDS is None: BANK_IDS = [d.direction_id for d in dirs]\n    BANK_Q.append(np.array(q)); BANK_V.append([d.value for d in dirs])\n"
  "    np.savez_compressed(K.SCRATCH / f\"descend_{tag}_bank.npz\", Q=np.array(BANK_Q), values=np.array(BANK_V), ids=np.array(BANK_IDS))\n"
  "    return float(sum(c[i] * jac[pid] for i, pid in enumerate(ids)))"),
]
missing = [a[:50] for a, b in rep if a not in s]
for a, b in rep: s = s.replace(a, b)
p.write_text(s, encoding="utf-8"); print("descend patched; missing:", missing)
# ---- k3_lp4.py: --extra_comp bank files (competitor + BFB rays)
p = here / "k3_lp4.py"; s = p.read_text(encoding="utf-8")
rep = [
 ("ap.add_argument(\"--seed\", type=int, default=1)", "ap.add_argument(\"--seed\", type=int, default=1)\nap.add_argument(\"--extra_comp\", default=\"\", help=\"comma-separated npz banks (Q, values, ids) added as competitor points and BFB rays\")"),
 ("COMP_J = np.array(COMP_J) if COMP_J else np.zeros((0, n_par)); COMP_M = np.array(COMP_M)",
  "EXTRA_BFB = []\nfor fn in [x for x in args.extra_comp.split(\",\") if x]:\n    eb = np.load(K.SCRATCH / fn); Je = J_from_values(eb[\"values\"], [str(x) for x in eb[\"ids\"]]); ne = np.linalg.norm(eb[\"Q\"], axis=1)\n"
  "    for row, qq in zip(Je, eb[\"Q\"]):\n        if np.linalg.norm(qq - q0) > 1e-6: COMP_J.append(row); COMP_M.append(margin_factor(qq))\n"
  "    EXTRA_BFB.append((Je * deg4[None, :]) / ne[:, None] ** 4)\n    log(f\"extra bank {fn}: {len(ne)} points\")\n"
  "COMP_J = np.array(COMP_J) if COMP_J else np.zeros((0, n_par)); COMP_M = np.array(COMP_M)"),
 ("    BFB_J.append((V4_up * deg4 / 24.0)[None, :])\nBFB_J = np.vstack(BFB_J) if BFB_J else np.zeros((0, n_par))",
  "    BFB_J.append((V4_up * deg4 / 24.0)[None, :])\n    BFB_J += EXTRA_BFB\nBFB_J = np.vstack(BFB_J) if BFB_J else np.zeros((0, n_par))"),
]
missing = [a[:50] for a, b in rep if a not in s]
for a, b in rep: s = s.replace(a, b)
p.write_text(s, encoding="utf-8"); print("lp4 patched; missing:", missing)
