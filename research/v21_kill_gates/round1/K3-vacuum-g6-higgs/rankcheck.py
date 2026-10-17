import json, numpy as np, k3_common as K
for tag in ["A20", "A45", "A70", "Am45", "W45"]:
    p = K.SCRATCH / f"{tag}_sumrules_phi.json"
    S = json.load(open(p)) if p.exists() else json.load(open(K.SCRATCH / f"{tag}_sumrules.json"))
    worst = max(v["residual"] for v in S["relations"].values())
    print(tag, "phi rank", S["rank"], "max residual of fitted linear relations:", f"{worst:.2e}")
