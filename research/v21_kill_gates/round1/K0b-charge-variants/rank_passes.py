"""Rank the certified PASS candidates of the scan_full runs and write spec files for the dossier."""
from __future__ import annotations

import glob
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    passes = []
    seen = set()
    for f in glob.glob(str(HERE / "scan_full_*.json")):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        for p in d.get("pass", []):
            key = (tuple(p["a"]), p["c"], p["p"], tuple((x, g) for _n, _r, x, g in p["singlets"]))
            if key in seen:
                continue
            seen.add(key)
            p["source"] = Path(f).name
            passes.append(p)
    for p in passes:
        n_sing = sum(g for _n, _r, _x, g in p["singlets"])
        p["n_singlets"] = n_sing
        p["score"] = (len(p["family_exotic_yukawas"]) > 0, p["max_abs_charge"], n_sing, float(eval(p["b_X"])))
    passes.sort(key=lambda p: p["score"])
    print("certified PASS candidates:", len(passes))
    for i, p in enumerate(passes[:40]):
        print("%2d a=%s c=%d p=%d singlets=%s |X|max=%d nsing=%d FX=%s fonly=%d bX=%.0f src=%s" % (
            i, p["a"], p["c"], p["p"], [(x, g) for _n, _r, x, g in p["singlets"]], p["max_abs_charge"], p["n_singlets"],
            p["family_exotic_yukawas"], p["n_fonly"], float(eval(p["b_X"])), p["source"]))
    (HERE / "passes_ranked.json").write_text(json.dumps(passes, indent=1), encoding="utf-8")
    for i, p in enumerate(passes[:5]):
        spec = {"label": "K0b_cand%d_a%s_c%d_p%d" % (i, "_".join(str(x) for x in p["a"]), p["c"], p["p"]), "fermions": p["content"],
                "sector": {n: ("Phi" if n in ("P", "Pb") else "S") for n, _r, _x, _g in p["content"] if n != "F"}}
        (HERE / ("cand%d.json" % i)).write_text(json.dumps(spec, indent=1), encoding="utf-8")
        print("wrote cand%d.json" % i, spec["label"])


if __name__ == "__main__":
    main()
