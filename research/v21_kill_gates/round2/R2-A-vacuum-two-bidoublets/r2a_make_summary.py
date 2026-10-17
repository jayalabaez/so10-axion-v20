"""Collect the key R2-A numbers into r2a_summary.json (reads the result files of this folder)."""
import json, os
D = os.path.dirname(os.path.abspath(__file__)); J = lambda f: json.load(open(os.path.join(D, f)))
g7 = J("G7_D470_C1622_K2.json"); ds = J("descent_summary.json")
out = {"verdict": "FAIL",
       "local_scan_clean_windows_deg": {"C2": [-85.5, -8.5], "C1": [-71.5, -22.5], "C1p": [-85.5, -8.5], "C1+813": None, "C1+622": [-50.5, -44.5]},
       "G3211_omega_ne_0": "27/27 LPs collapse (t <= 8.5e-8) at 9 orientations",
       "composition_targets_realised": "20/20 (C1+622 at D470, C2 at Am45)",
       "G7_D470_C1622_K2": {"t": g7["t"], "full_hessian": {k: g7["full_hessian"][k] for k in ("n_zero(<1e-9)", "n_negative(<-1e-9)", "n_light(<10 eps_hi)", "n_heavy")},
                            "a0": g7["singlet_channel_a0"], "lambda": {k: v for k, v in g7["lambda"].items() if k != "light_terms_sorted"}, "ew": g7.get("ew"),
                            "screens_n_lower": [s["n_lower_non_orbit"] for s in g7["subspace_screen"]]},
       "descents": {rd: {"point": v["sol"], "n": v["n"], "n_lower": v["n_lower"], "Vmin-V*_range": [v["min"], v["max"]], "V*": v["V_star"]} for rd, v in ds.items()},
       "feedback": {"round1_maxlift_deepest_R1_point_lightcubic_1e-5": -46.8, "round2_maxlift_R2rnd28_given_R1": -4.54,
                    "round3_EW_cells_infeasible": "Am45 (C2 fSigma 0.1/0.5/0.9, C1+622 0.9) + D190,D295,D400,D575,D680,D785 (C2, 12/12)",
                    "controls_feasible_with_R1R2_cuts_Am45": {"V0": 0.0312, "C0": 0.0328, "C2_noEW": 0.0127}},
       "lambda_eff": {"tree_max_on_lifting_family": -0.089, "G8d1": -0.93, "one_loop_CW_at_B13": {"heavy_scalars_mu_Phi": -1.36, "heavy_scalars_mu_0.3Phi": -0.74, "heavy_gauge": 0.054, "light": -0.0024}},
       "thresholds": {"C1+622": {"v_R": [3.6e12, 1.1e13], "M_U": [8.9e15, 3.6e16], "tau_repo": [2.8e35, 5.8e37], "tau_dir": [6.1e34, 1.3e37], "L2": [0.69, 1.34], "L3": [0.31, 0.60]},
                      "C2_G7_Am45": {"v_R": 8.3e10, "M_U": 7.9e15, "tau_repo": 2.43e35, "tau_dir": 5.36e34, "L2": 3.59, "L3": 1.43},
                      "C1_max_tau": 5.19e33, "C1p_max_tau": 5.22e33},
       "checkouts": {"_g6_nogo": "54a2cd1, 0 status lines", "_record": "8707fda, 0 status lines"}}
json.dump(out, open(os.path.join(D, "r2a_summary.json"), "w"), indent=1, default=float); print("ok")
