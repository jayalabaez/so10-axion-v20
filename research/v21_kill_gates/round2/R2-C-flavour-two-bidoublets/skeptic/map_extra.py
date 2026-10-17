"""Map the researcher's litera (2018-era data) and nufit32 best points into my W-param (their code used read-only)."""
import sys, os, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "theirs")); os.chdir(os.path.join(HERE, "theirs"))
import lib_r2c as L, model_r2c as M
sys.path.insert(0, HERE)
import skchain as S, skopt as O
d = L.data_set("nufit60_sk", 0.01)
setup = M.make_setup(1e13, d, content="R622", MU=1.9e16); tg = setup["targets"]
lay = M.Layout(typeII=False, free=True)
out = []
for f in ["litera_1e+13_R622_I.json", "nufit32_1e+13_R622_I.json"]:
    J = json.load(open(f))
    r = J["exact_results"][0]; z = np.array(r["z"])
    G = M.gut_matrices(z[None, :-1], lay, tg.sd0, tg.se0)
    X = O.gut_to_w(G["H"], G["F"], G["r"], G["s"], np.array([10**z[-1]]))[0]
    out.append({"vR": 1e13, "x": X.tolist(), "src": f, "chi2_theirs": r["chi2"], "data": J["data"]})
    print(f, r["chi2"])
json.dump(out, open(os.path.join(HERE, "their_extra.json"), "w"), indent=1)
