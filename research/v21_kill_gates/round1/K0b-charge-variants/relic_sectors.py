"""K0b: relic structure of a candidate - for every accidental fermion-number generator f_k, the lowest-dimension
genuine SO(10)-singlet X-neutral operator with f_k = +-1 and all OTHER f's zero (any fermion species allowed, <= 4
fermions), i.e. the operator through which the lightest state of that sector decays; lifetime estimate (EST) at
M = 1e13 (S-scale sectors) or 1e17 (Phi17-scale sectors).  R-parity classification included.
Usage: relic_sectors.py <spec.json> <out_tag>
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

from k0b_engine import Model, jsonable, label, MPL

HERE = Path(__file__).resolve().parent
VEV = {"S": 3.0e13, "Phi17": 1.0e17, "Delta": 2.6e13, "Phi210": 2.1e16, "H10": 174.0}
HBAR = 6.582e-25
T_UNIVERSE = 4.35e17


def lifetime(counts, dim, nf, M):
    vevs = 1.0
    for lab, mult in counts.items():
        base = lab.rstrip("^")
        if base in VEV:
            vevs *= VEV[base] ** mult
    K = float(dim) - 4
    if nf == 2:
        m_mix = vevs / MPL ** K
        theta = m_mix / M
        gamma = theta ** 2 * (1 / 25.0) * M
    else:
        gamma = (vevs / MPL ** K) ** 2 * M ** 5 / (192 * math.pi ** 3)
    return gamma, (HBAR / gamma if gamma > 0 else float("inf"))


def main():
    spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    tag = sys.argv[2]
    m = Model([tuple(f) for f in spec["fermions"]], spec.get("label", tag))
    k = m.compute_kernel()
    out = {"label": m.label, "R_parity": m.r_parity(), "sectors": []}
    nq = len(m.field_table()[0]["q"])
    for i, v in enumerate(k["fonly"]):
        members = [n for j, n in enumerate(m.fnames) if v[j] != 0]
        # mass scale: Phi17-type if a member has a Phi17 Yukawa mass
        phi_scale = any(("Phi17" in t["scalar"]) and any(f in members for f in t["fermions"]) for t in m.renormalizable_terms())
        M = 1.0e17 if phi_scale else 1.0e13
        sec = {"generator": "f%d" % (i + 1), "members": members, "charges": {n: int(v[j]) for j, n in enumerate(m.fnames) if v[j] != 0},
               "mass_scale_GeV": M, "R_odd": all(n in out["R_parity"]["R_odd_fermions"] for n in members), "operators": {}}
        for sign in (+1, -1):
            for nf in (2, 4):
                target = [None] * nq
                for jj in range(1, nq):
                    target[jj] = 0
                target[i + 1] = sign
                best = None
                extra = []
                for _try in range(10):
                    r = m.min_operator(target, forbid=tuple(extra), exact_fermions=nf, dim_max=40)
                    if r is None:
                        break
                    dim, counts, parity = r
                    ns = m.is_singlet(counts)
                    if ns > 0:
                        best = (dim, counts, parity, ns)
                        break
                    extra.append(min(counts, key=lambda kk: counts[kk]))
                key = "f=%+d,nf=%d" % (sign, nf)
                if best is None:
                    sec["operators"][key] = None
                    continue
                dim, counts, parity, ns = best
                gamma, tau = lifetime(counts, dim, nf, M)
                sec["operators"][key] = {"dimension": str(dim), "operator": label(counts), "singlets": ns, "Gamma_GeV": gamma,
                                         "tau_s": tau, "tau_over_age": tau / T_UNIVERSE, "heuristic_forbids": extra}
        out["sectors"].append(sec)
        print(sec["generator"], members, "M=%.0e" % M, "R_odd" if sec["R_odd"] else "R_even")
        for kk, vv in sec["operators"].items():
            print("   ", kk, None if vv is None else "%s dim %s tau=%.1e s (%.1e ages)" % (vv["operator"], vv["dimension"], vv["tau_s"], vv["tau_over_age"]))
    (HERE / ("relics_%s.json" % tag)).write_text(json.dumps(jsonable(out), indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
