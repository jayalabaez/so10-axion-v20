#!/usr/bin/env python3
"""SKEPTIC D1: anomalies of the (unchanged) B63 fermions, PQ anomaly N, and an exhaustive check that the new real
45_H (X = 0) has no renormalisable coupling to fermions (needs a fermion bilinear with X = 0 containing a 45:
16(x) x 16bar(-x), 10 x 10 antisymmetric with X = 0)."""
from fractions import Fraction as Fr
import itertools, json
from pathlib import Path
# (name, rep, dim, T, X, mult) ; T(10)=1, T(16)=2
FER = [("F","16",16,2,1,3),("V1","16",16,2,-35,2),("Vb1","16b",16,2,39,1),("V2","16",16,2,-28,1),("Vb2","16b",16,2,32,1),
       ("V3","16",16,2,34,1),("Vb3","16b",16,2,-30,1),("T","10",10,1,2,2),("Pb","16b",16,2,18,1),
       ("N1","1",1,0,-63,1),("N1b","1",1,0,59,1),("N2","1",1,0,-58,1),("N2b","1",1,0,54,1),("N3","1",1,0,-57,1),
       ("N3b","1",1,0,61,1),("NMm","1",1,0,-2,2)]
G2 = {"V1":-1,"Vb1":1}   # round-1 kernel basis: G2 nonzero on V1, Vb1 (and Phi17); note V1 x2 (one of them pairs with Pb)
out = {}
out["SO10^2 X"] = str(sum(Fr(T*X*m) for _,_,d,T,X,m in FER))
out["X^3"] = str(sum(Fr(d*X**3*m) for _,_,d,T,X,m in FER))
out["grav X"] = str(sum(Fr(d*X*m) for _,_,d,T,X,m in FER))
# 45 couplings: bilinears psi_i psi_j containing a 45 with X_i + X_j = 0
hits = []
for (a,ra,_,_,xa,ma),(b,rb,_,_,xb,mb) in itertools.combinations_with_replacement(FER,2):
    if xa + xb != 0: continue
    pair = {ra, rb}
    has45 = (pair == {"16","16b"}) or (ra == rb == "10" and (a != b or ma > 1))
    if has45: hits.append((a,b))
out["fermion bilinears with X=0 containing a 45 (A45 Yukawa)"] = hits
print(json.dumps(out, indent=1))
(Path(__file__).resolve().parent / "sk_d1_anom.json").write_text(json.dumps(out, indent=1))
