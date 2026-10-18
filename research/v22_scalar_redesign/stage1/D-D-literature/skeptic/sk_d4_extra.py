#!/usr/bin/env python3
"""SKEPTIC D4 extra variants (imports the skeptic's own sk_d4.py): forced down-type doublet mass scan and combinations."""
import json, math
from pathlib import Path
import sk_d4 as K
HERE = Path(__file__).resolve().parent
a1 = 0.6 * 127.930 * (1 - 0.23129); a2 = 127.930 * 0.23129
rows = {}
def rec(name, **kw):
    r = K.point(**kw)
    rows[name] = r
    print(f"{name:62s} M2nd {r['M_second']:.3g} M_U {r['M_U']:.4g} aU^-1 {r['aU_inv']:.3f} tau {r['tau_lat_yr']:.3g} L2L/MPl {r['L2_over_MPl']:.3f}", flush=True)
for md in (3e15, 5e15, 7e15, 1e16):
    rec(f"designer inputs + 2 doublets at {md:.0e}, M8=1e3", M8=1e3, extra_light=(("Hd2", md),))
for m8 in (1e3, 2e3):
    for md in (3e15, 7e15):
        rec(f"PDG24 a_s=0.1180, Y-consistent, M8={m8:.0e}, doublets {md:.0e}", M8=m8, a0=(a1, a2, 1/0.1180),
            Y126_tr2=0.006, c_u10=0.91, extra_light=(("Hd2", md),))
rec("PDG24, Y-consistent, M8=2e3, a_s=0.1171", M8=2e3, a0=(a1, a2, 1/0.1171), Y126_tr2=0.006, c_u10=0.91)
rec("PDG24, Y-consistent, M8=2e3, a_s=0.1189", M8=2e3, a0=(a1, a2, 1/0.1189), Y126_tr2=0.006, c_u10=0.91)
rec("PDG24, Y-consistent, M8=2e3, M_s=9e12", M8=2e3, a0=(a1, a2, 1/0.1180), Y126_tr2=0.006, c_u10=0.91, M_s=9e12)
rec("PDG24, Y-consistent, M8=2e3, M_s=1.21e13 y_s=0.368", M8=2e3, a0=(a1, a2, 1/0.1180), Y126_tr2=0.006, c_u10=0.91, M_s=1.21e13, y_s=0.368)
(HERE / "sk_d4_extra.json").write_text(json.dumps(rows, indent=1, default=str), encoding="utf-8")
