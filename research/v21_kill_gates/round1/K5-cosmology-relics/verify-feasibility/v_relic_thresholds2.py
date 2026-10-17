"""Re-bracketed thresholds using v_relic_independent.omega (hi = M/8 instead of the instant-reheating cap)."""
import json, sys
sys.path.insert(0, r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\wfV21\K5-cosmology-relics\verify-feasibility")
import numpy as np
from v_relic_independent import omega, MP, GS

OUT = r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\wfV21\K5-cosmology-relics\verify-feasibility\v_relic_thresholds2.json"


def threshold(M, HI, target=0.12, lo=1e8):
    cap = np.sqrt(HI * MP / np.sqrt(np.pi ** 2 * GS / 90.0))
    hi = min(cap, M / 8.0)
    olo, ohi = omega(M, lo, HI)["Omega_h2"], omega(M, hi, HI)["Omega_h2"]
    print(f"  bracket M={M:.0e} HI={HI:.0e}: Omega(lo={lo:.1e})={olo:.3e} Omega(hi={hi:.3e})={ohi:.3e}", flush=True)
    if olo > target:
        return None, "above at lo"
    if ohi <= target:
        return hi, "below at hi"
    while hi / lo > 1.02:
        mid = np.sqrt(lo * hi)
        if omega(M, mid, HI)["Omega_h2"] <= target:
            lo = mid
        else:
            hi = mid
    return float(np.sqrt(lo * hi)), "ok"


rows = []
for (M, HI) in ((1e13, 3e7), (3e12, 3e7), (1e13, 1e7), (3e12, 1e6), (1e13, 1e9), (3e12, 1e9), (1e13, 1e5), (3e12, 1e5)):
    th, note = threshold(M, HI)
    rows.append(dict(M=M, HI=HI, TRH_max=th, note=note))
    print(f"threshold M={M:.0e} HI={HI:.0e}: TRH_max={th} ({note})", flush=True)
json.dump(rows, open(OUT, "w"), indent=1)
