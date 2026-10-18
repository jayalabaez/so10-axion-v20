"""SKEPTIC: A = 0 reduction and v20-row embedding against a DIRECT repo call at fresh points (seeds not used by the
builder), plus the optional fast backend v20poly at the same fresh points.

  point 1: repo deterministic_state(777) + random A != 0
  point 2: my own Gaussian q486 (seed 99) + random A
For each: repo target.parameter_rows(chart.unpack(q486)) vs chart531.parameter_rows(q531) (51 v20 rows: value,
gradient, Hessian; A blocks must be zero); chart531 v20 rows at A != 0 vs A = 0 (must be identical); v20poly backend vs
repo (value / gradient / Hessian, relative to row scale).
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sk_common as C  # noqa: E402
import chart531 as CH  # noqa: E402
import g3_candidate_physical_target_audit_v20 as target  # noqa: E402
import live_g2_arbitrary_component_potential_values_v20 as potential  # noqa: E402

LOG = open(C.HERE / "sk_a0_repo.log", "w", encoding="utf-8")
OUT = C.HERE / "sk_a0_repo.json"


def main():
    t0 = time.time()
    rng = np.random.default_rng(99)
    pts = {"deterministic_state(777)": C.rchart.pack(potential.deterministic_state(777)),
           "gaussian_seed99": rng.normal(size=C.N486) * 0.7}
    res = {}
    for name, q486 in pts.items():
        qa = rng.normal(size=45)
        q531 = np.concatenate([q486, qa])
        q531_0 = np.concatenate([q486, np.zeros(45)])
        t1 = time.time()
        repo = target.parameter_rows(C.rchart.unpack(q486))
        t_repo = time.time() - t1
        ch = CH.parameter_rows(q531)
        CH._V20_CACHE.clear()
        ch0 = CH.parameter_rows(q531_0)
        t2 = time.time()
        poly = CH.parameter_rows(q531, v20_backend="poly")
        t_poly = time.time() - t2
        d = {"value": 0.0, "grad486": 0.0, "hess486": 0.0, "A_blocks": 0.0, "A_vs_A0": 0.0}
        dp = {"value": 0.0, "grad": 0.0, "hess": 0.0}
        worst_poly_row = None
        for pid, r in repo.items():
            c, c0, pr = ch[pid], ch0[pid], poly[pid]
            g = np.asarray(r.gradient, float)
            h = np.asarray(r.hessian, float)
            d["value"] = max(d["value"], abs(c.value - float(r.value)))
            d["grad486"] = max(d["grad486"], float(np.max(np.abs(c.gradient[:C.N486] - g))))
            d["hess486"] = max(d["hess486"], float(np.max(np.abs(c.hessian[:C.N486, :C.N486] - h))))
            d["A_blocks"] = max(d["A_blocks"], float(np.max(np.abs(c.gradient[C.N486:]))),
                                float(np.max(np.abs(c.hessian[C.N486:, :]))), float(np.max(np.abs(c.hessian[:, C.N486:]))))
            d["A_vs_A0"] = max(d["A_vs_A0"], abs(c.value - c0.value), float(np.max(np.abs(c.gradient - c0.gradient))),
                               float(np.max(np.abs(c.hessian - c0.hessian))))
            sv = max(abs(float(r.value)), 1e-300)
            sg = max(float(np.max(np.abs(g))), 1e-300)
            sh = max(float(np.max(np.abs(h))), 1e-300)
            pv = abs(pr.value - float(r.value)) / max(sv, 1e-12 * sg)
            pg = float(np.max(np.abs(pr.gradient[:C.N486] - g))) / sg
            ph = float(np.max(np.abs(pr.hessian[:C.N486, :C.N486] - h))) / sh
            if worst_poly_row is None or max(pv, pg, ph) > worst_poly_row[1]:
                worst_poly_row = (pid, max(pv, pg, ph))
            dp["value"] = max(dp["value"], pv)
            dp["grad"] = max(dp["grad"], pg)
            dp["hess"] = max(dp["hess"], ph)
        new_ids = [k for k in ch0 if k not in repo]
        new0 = max(abs(ch0[k].value) for k in new_ids)
        res[name] = {"n_v20_rows": len(repo), "n_new_rows": len(new_ids),
                     "chart531_v20_vs_direct_repo_maxabs": d, "new_rows_max_abs_value_at_A0": new0,
                     "poly_backend_vs_repo_max_rel": dp, "poly_worst_row": worst_poly_row,
                     "time_repo_s": t_repo, "time_poly_s": t_poly}
        C.log(f"{name}: {res[name]}", LOG)
    res["total_time_s"] = time.time() - t0
    C.json_dump(res, OUT)
    C.log(f"wrote {OUT}", LOG)


if __name__ == "__main__":
    main()
