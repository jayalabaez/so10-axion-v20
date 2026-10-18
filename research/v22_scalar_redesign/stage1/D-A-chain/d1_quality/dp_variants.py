"""D1 for the next-minimal variants (EXACT, integer DP of R2-V dual_dp.py, imported unedited from this folder's copy):
re-run the K_min certificate with an extra real scalar 45_H (X = 0, centre class 0) or 54_H (X = 0, centre 0), each with
accidental charge q = 0 (it can have no phase-sensitive renormalizable coupling that involves Phi17 or the f_k fermions).
The DP item list is extended explicitly (not just argued as a duplicate)."""
import json
import dual_dp as D

out = {}
base_scalars = list(D.SCALARS)
for label, extra in (("base(A1)", []), ("+45_H", [("H45", 45, 0, True)]), ("+54_H", [("H54", 54, 0, True)]),
                     ("+45_H+54_H", [("H45", 45, 0, True), ("H54", 54, 0, True)])):
    D.SCALARS = base_scalars + extra
    for n, r, x, real in extra:
        D.ZC[r] = 0
        D.Q[n] = (0,) * 6
    c = D.certificate(24, True, label)
    out[label] = {"max_excess_x4_d<=20": c["max_excess_x4_over_5<=d<=20"], "holds_d<=20": c["certificate_holds_d<=20"],
                  "max_to_d24": c["max_excess_x4_over_all_d<=24"], "argmax": str(c["monomial"]), "n_items": len(D.items())}
    print(label, out[label], flush=True)
D.SCALARS = base_scalars
json.dump(out, open("dp_variants.json", "w"), indent=1)
