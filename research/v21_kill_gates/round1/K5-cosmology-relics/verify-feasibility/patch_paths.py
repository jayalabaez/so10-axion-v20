import os
V = r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\wfV21\K5-cosmology-relics\verify-feasibility"
K = r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\wfV21\K5-cosmology-relics"
for src, old in (("k5_rodd_sector.py", "k5_rodd_sector.json"), ("k5_splitting.py", "k5_splitting.json")):
    s = open(os.path.join(K, src), encoding="utf-8").read()
    new_out = os.path.join(V, "v_" + old[3:])
    s2 = s.replace('OUT = r"' + os.path.join(K, old) + '"', 'OUT = r"' + new_out + '"')
    assert s2 != s, src
    open(os.path.join(V, "v_" + src[3:]), "w", encoding="utf-8").write(s2)
    print("patched", src, "->", new_out)
