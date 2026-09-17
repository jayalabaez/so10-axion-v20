"""Impact of the contaminated v20 flavour basis on the downstream modules.

`physical_cf_matching_v20.flavour_mass_bases` and
`push_phenomenology_limits_v20.flavour_sector_bases` diagonalise the
nuisance-rotated *target* `M_u`, not the predicted one. Nine modules consume
those bases. This rebuilds the same dictionaries from a v21 witness, where the
quark rotations come from the predicted `M_u`, and re-runs the affected
reports both ways.

Run:  python downstream_impact.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import flavour_general_yukawa_v21 as G  # noqa: E402

WITNESSES = Path(__file__).resolve().parent.parent / "FLAVOUR_GENERAL_YUKAWA_V21_WITNESSES.json"


def v21_bases(tan_beta: float = 10.0) -> dict:
    """Same keys as the v20 bases, built from the v21 witness with PREDICTED mixing."""
    wit = json.loads(WITNESSES.read_text(encoding="utf-8"))
    entry = [w for w in wit["benchmark_fits"]
             if w["tan_beta"] == tan_beta and w["label"] == "Ymax=1"][0]
    st = G.Stratum(tan_beta, entry["v_R"], **entry.get("config", {}))
    p = np.asarray(entry["x"])
    b = st.build(p)
    _s_nu, u_nu = G._takagi(b["mnu"])
    _s_e, u_e = G._takagi(b["me"])
    u_u, _su, vh_u = np.linalg.svd(np.asarray(b["mu"], dtype=complex), full_matrices=True)
    u_d, _sd, vh_d = np.linalg.svd(np.asarray(b["md"], dtype=complex), full_matrices=True)
    chi2 = st.chi2_parts(p)["chi2_fermion"]
    return {
        "tan_beta": float(tan_beta), "v_r_GeV": float(entry["v_R"]), "chi2": float(chi2),
        "U_e": u_e, "U_nu": u_nu, "U_uL": u_u, "U_uR": vh_u.conj().T,
        "U_dL": u_d, "U_dR": vh_d.conj().T,
        "H": np.asarray(b["H"]) / st.vd, "F": np.asarray(b["F"]) / st.vd,
        "v_u": st.vu, "v_d": st.vd,
        "m_u": [float(x) for x in _su], "m_d": [float(x) for x in _sd],
        "natural_scale_viable": bool(chi2 < 30.0),
        "fit_note": "v21 general Yukawa witness; quark rotations from the PREDICTED M_u.",
    }


def ckm_of(bases: dict) -> dict:
    """|U_uL^dag U_dL| in the SVD (descending-mass) ordering the bases use.

    numpy's SVD orders singular values descending, so row/column 0 is the third
    generation. In that convention the entries below are |V_ts|, |V_cd|, |V_td|
    (measured 0.0413, 0.2245, 0.0086), NOT |V_us|, |V_cb|, |V_ub|.
    """
    v = np.asarray(bases["U_uL"]).conj().T @ np.asarray(bases["U_dL"])
    return {"V_ts": float(abs(v[0, 1])), "V_cd": float(abs(v[1, 2])), "V_td": float(abs(v[0, 2]))}


def main() -> None:
    import channel_fcnc_rates_v20 as fcnc
    import physical_cf_matching_v20 as physical

    v20 = physical.flavour_mass_bases()
    v21 = v21_bases(10.0)
    print("=== the basis each layer actually uses ===")
    print(f"   v20 quark mixing |U_uL^dag U_dL| : {ckm_of(v20)}")
    print(f"   v21 quark mixing (predicted)     : {ckm_of(v21)}")
    print("   measured (same ordering)         : {'V_ts': 0.04130, 'V_cd': 0.22452, 'V_td': 0.00857}")
    print(f"   v20 tan_beta={v20['tan_beta']:.3f} v_R={v20['v_r_GeV']:.2e} | "
          f"v21 tan_beta={v21['tan_beta']:.1f} v_R={v21['v_r_GeV']:.2e}")

    rows = []
    for label, bases in (("v20 (contaminated)", v20), ("v21 (predicted)", v21)):
        original = physical.flavour_mass_bases
        physical.flavour_mass_bases = lambda b=bases: b
        try:
            report = fcnc.build_report()
        finally:
            physical.flavour_mass_bases = original
        rows.append((label, report))

    print("\n=== FCNC branching ratios ===")
    scen = ("aligned_limit", "hierarchical_benchmark", "generation_dependent_counterexample")
    chan = ("mu_to_e_a", "K_to_pi_a")
    print(f"{'scenario':>36} {'channel':>10} {'v20':>13} {'v21':>13} {'ratio':>10}")
    out = {}
    for s in scen:
        for c in chan:
            a = rows[0][1][s][c]["branching_ratio"]
            b = rows[1][1][s][c]["branching_ratio"]
            ratio = (b / a) if a else float("inf")
            out[f"{s}/{c}"] = {"v20": a, "v21": b, "ratio": ratio}
            print(f"{s:>36} {c:>10} {a:13.4e} {b:13.4e} {ratio:10.3g}")
    for label, report in rows:
        print(f"   {label:>22}: n_failed={report['n_failed']} status={report['status'][:52]}")
    json.dump(out, open(Path(__file__).resolve().parent / "downstream_impact.json", "w"), indent=2)


if __name__ == "__main__":
    main()
