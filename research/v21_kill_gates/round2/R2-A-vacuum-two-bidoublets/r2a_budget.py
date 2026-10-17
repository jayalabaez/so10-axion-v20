"""Per-operator energy budget c_i (J_i(q) - J_i(q*)) of a banked descent point (default: the deepest point of the bank)."""
import sys, numpy as np, json
tag, solp, bank = sys.argv[1], sys.argv[2], sys.argv[3]
c = np.load(solp)["c"]; Z = np.load(f"{tag}_rows.npz"); ids = [str(x) for x in Z["ids"]]; V0 = Z["values"]
b = np.load(bank); J = b["J"]; k = int(sys.argv[4]) if len(sys.argv) > 4 else int(np.argmin(J @ c))
d = c * (J[k] - V0); order = np.argsort(d)
print(f"point {k}: V - V* = {d.sum():+.4f}")
print("most negative:", [(ids[i], round(float(c[i]), 4), round(float(d[i]), 3)) for i in order[:8]])
print("most positive:", [(ids[i], round(float(c[i]), 4), round(float(d[i]), 3)) for i in order[::-1][:6]])
