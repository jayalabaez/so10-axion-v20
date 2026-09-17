"""Evaluate right-handed-neutrino threshold effects at the frozen witnesses."""
import json, sys
import numpy as np
import so10fit as S
import thresholds as T


def fermion_chi2(st, p, lep):
    o = st.observables(p)
    r = [(o["up"][k] - st.m[k]) / st.sig_up[k] for k in ("u", "c", "t")]
    r += [(o["ckm"][k] - st.ckm[k]) / st.sig_ckm[k] for k in ("s12", "s23", "s13", "J")]
    for key, obs in (("sin2_th12", "sin2_th12"), ("sin2_th23", "sin2_th23"), ("sin2_th13", "sin2_th13"),
                     ("dm21", "dm21_eV2"), ("dm31", "dm31_eV2")):
        c, s = S.NUFIT[key]
        r.append((lep[obs] - c) / s)
    c, s = S.NUFIT["delta_deg"]
    r.append(((lep["delta_cp_deg"] - c + 180) % 360 - 180) / s)
    return float(np.dot(r, r)), [round(float(v), 3) for v in r[7:]]


def main():
    lam2 = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5
    rows = []
    for d in json.load(open("robust.json")):
        kw = {k: d[k] for k in ("y_max", "floor", "s12_floor") if k in d}
        rows.append((d["case"], d["tan_beta"], d["v_R"], kw, d["x"]))
    for d in json.load(open("predict.json")):
        if d["target"] in (0.066, 0.069):
            rows.append((f"window {d['target']}", 25.0, 6.313855e11, {"planck": False}, d["x"]))
    print(f"lam2 = {lam2}")
    print(f"{'witness':>16} {'tanb':>4} {'chi2 base':>9} {'chi2 thr':>9} {'Smnu base':>9} {'Smnu thr':>9}"
          f" {'dSmnu%':>7} {'dm_tau%':>7}  thresholds (GeV)   nu pulls with thresholds")
    for label, tb, vr, kw, x in rows:
        st = S.Stratum(tb, vr, **kw)
        p = np.array(x)
        base = st.observables(p)["lep"]
        c0, _ = fermion_chi2(st, p, base)
        lep, out = T.observables_with_thresholds(st, p, lam2=lam2)
        c1, pulls = fermion_chi2(st, p, lep)
        dtau = 100 * (out["charged_lepton_masses_Z"][2] - S.rg.MASS_MZ["tau"]) / S.rg.MASS_MZ["tau"]
        ds = 100 * (lep["sum_mnu_eV"] - base["sum_mnu_eV"]) / base["sum_mnu_eV"]
        thr = ", ".join(f"{v:.2e}" for v in out["thresholds_GeV"])
        print(f"{label:>16} {tb:4.0f} {c0:9.3f} {c1:9.3f} {base['sum_mnu_eV']:9.5f} {lep['sum_mnu_eV']:9.5f}"
              f" {ds:7.2f} {dtau:7.3f}  [{thr}]  {pulls}")


if __name__ == "__main__":
    main()
