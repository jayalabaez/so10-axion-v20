"""sk2: multisets of n tight two-fermion operators (sk2_tight2.json) whose accidental charges sum to (4,0,0,0,0,0)
and whose dimensions give K = sum(d-4) = 17 (necessary condition for a K = 17 one-loop ring; line connectivity not
checked here).  Also flags members with an explicit H10/Delta leg (needs an EW/v_R vev at one loop)."""
import json, itertools
from pathlib import Path
ops = json.loads(Path(__file__).with_name("sk2_tight2.json").read_text())["ops"]
res = {}
for n in range(2, 6):
    hits = []
    for comb in itertools.combinations_with_replacement(range(len(ops)), n):
        q = [sum(ops[i]["q"][k] for i in comb) for k in range(6)]
        K = sum(ops[i]["d"] - 4 for i in comb)
        if q == [4, 0, 0, 0, 0, 0]:
            hits.append({"ops": [ops[i]["op"] for i in comb], "K": K,
                         "has_Hleg": any((" H10" in ops[i]["op"] or "Delta" in ops[i]["op"]) for i in comb)})
    res[n] = {"n_q_compatible": len(hits), "n_without_Hleg": sum(1 for h in hits if not h["has_Hleg"]), "list": hits}
    print(n, res[n]["n_q_compatible"], res[n]["n_without_Hleg"], set(h["K"] for h in hits))
Path(__file__).with_name("sk2_ringq.json").write_text(json.dumps(res, indent=1))
