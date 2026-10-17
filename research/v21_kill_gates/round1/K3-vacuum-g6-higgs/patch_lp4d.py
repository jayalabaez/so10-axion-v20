import pathlib
p = pathlib.Path(__file__).resolve().parent / "k3_lp4.py"; s = p.read_text(encoding="utf-8")
rep = [
 # normalise Kelley cut rows
 ("                row = np.zeros(nz); row[:ny] = gR; row[R_IDX] = -1.0; cuts_A.append(row); cuts_b.append(float(gR @ y - R)); cuts_cls.append('kelley'); n_new += 1; worst = max(worst, R - rho)",
  "                row = np.zeros(nz); row[:ny] = gR; row[R_IDX] = -1.0; rhs = float(gR @ y - R); sc = max(1.0, float(np.max(np.abs(row))))\n"
  "                cuts_A.append(row / sc); cuts_b.append(rhs / sc); cuts_cls.append('kelley'); n_new += 1; worst = max(worst, R - rho)"),
 # checkpoint every 10 iterations + looser stop in stage B
 ("        result = (z, t)\n        if n_new == 0 or (worst < 1e-9 and it > 5 and n_comp_added_this == 0): break",
  "        result = (z, t)\n        if it % 10 == 0:\n            np.savez(K.SCRATCH / f\"{out}_iter.npz\", c=c, t=t, z=z, ids=np.array(ids), it=it, **{f\"U{k}\": Ucur[k] for k in sub_blocks})\n"
  "        tol_stop = 1e-6 if STAGE_B else 1e-9\n        if n_new == 0 or (worst < tol_stop and it > 5 and n_comp_added_this == 0): break"),
]
missing = [a[:60] for a, b in rep if a not in s]
for a, b in rep: s = s.replace(a, b)
p.write_text(s, encoding="utf-8"); print("patched; missing:", missing)
