import numpy as np, json
for f in ["D400_blocks.npz","D400_rows.npz","ew_D400_K2.npz","S5_D400_C2.npz","G16_D400_C2_K2_noc.npz","rays_pts.npz","smsinglet_pts.npz","descend_R1_bankA_bank.npz","descend_P831_r1s_bank.npz"]:
    try:
        z=np.load(f)
        print(f, {k:(z[k].shape, z[k].dtype) for k in z.files if not k.startswith(("A","G","W")) or len(k)<2 or not k[1:].isdigit()})
    except Exception as e: print(f, "ERR", e)
z=np.load("D400_blocks.npz"); print("A0", z["A0"].shape, z["A0"].dtype, "G0", z["G0"].shape, "W0", z["W0"].shape, "m", z["m"], "T", z["T"].shape, "stat_rows", z["stat_rows"].shape)
tr=json.load(open("unit_rows_traces.json")); print(tr.keys()); print(list(tr["blocks"].keys())); b=list(tr["blocks"].values())[0]; print(b.keys()); 
