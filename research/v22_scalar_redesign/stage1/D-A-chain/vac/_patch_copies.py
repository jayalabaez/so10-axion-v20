"""Patch the copied R2-A vacuum scripts for the D-A-chain SM-direct screen (copies only; originals untouched).
 - k3_common: REPO -> this worktree (read-only imports), BANKDIR -> R2-A scratch folder (read-only npz banks)
 - r2_lp6 -> lp_sm.py: banks read from BANKDIR when not present locally; orbit test generalised to the SM-direct point
   (same (|p|, a, omega, |Sigma|, |s|, x) within 2e-2); VEV-light spec 'sm' = only the S radial mode light.
 - r2_descend: banks / starts read from BANKDIR when not present locally.
"""
from pathlib import Path
HERE = Path(__file__).resolve().parent

src = (HERE / "k3_common.py").read_text(encoding="utf-8")
old = 'REPO = r"C:\\Users\\jayal\\Downloads\\So10Theory2\\So10Theory\\_g6_nogo"'
assert old in src
src = src.replace(old, 'REPO = r"C:\\Users\\jayal\\Downloads\\So10Theory2\\So10Theory\\_v22research"\n'
                  'BANKDIR = Path(r"C:\\Users\\jayal\\AppData\\Local\\Temp\\claude\\c--Users-jayal-Downloads-So10Theory2-So10Theory'
                  '\\d4b271a0-faef-4f94-bc1d-6399a3649e86\\scratchpad\\wfV21R2\\R2-A-vacuum-two-bidoublets")\n\n\n'
                  'def find(fn):\n    p = SCRATCH / fn\n    return p if p.exists() else BANKDIR / fn\n')
(HERE / "k3_common.py").write_text(src, encoding="utf-8")

lp = (HERE / "r2_lp6.py").read_text(encoding="utf-8")
reps = [
    ('pts = np.load(K.SCRATCH / npz); self.mode = mode', 'pts = np.load(K.find(npz)); self.mode = mode'),
    ('    eb = np.load(K.SCRATCH / fn)\n', '    eb = np.load(K.find(fn))\n'),
    ('rp = np.load(K.SCRATCH / fn); Jr', 'rp = np.load(K.find(fn)); Jr'),
    ('_f, _k = args.obj_point.rsplit(":", 1); _bb = np.load(K.SCRATCH / _f)', '_f, _k = args.obj_point.rsplit(":", 1); _bb = np.load(K.find(_f))'),
    ('''def in_g3221_orbit(z):
    """gauge copies of z* inside the subspace: same |p|,|a|, om = 0, x = x*, and (essentially) no Sigma vev."""
    return (abs(abs(z[0]) - abs(zstar[0])) < 2e-3 and abs(abs(z[1]) - abs(zstar[1])) < 2e-3 and abs(z[2]) < 2e-3
            and abs(z[6] - zstar[6]) < 2e-2 and math.hypot(z[3], z[4]) < 0.02)''',
     '''def in_g3221_orbit(z):
    """D-A-chain: copies of the SM-direct point z* inside the subspace (|p|, a, omega, |Sigma|, |s|, x within 2e-2)."""
    return (abs(abs(z[0]) - abs(zstar[0])) < 2e-2 and abs(z[1] - zstar[1]) < 2e-2 and abs(abs(z[2]) - abs(zstar[2])) < 2e-2
            and abs(z[6] - zstar[6]) < 2e-2 and abs(math.hypot(z[3], z[4]) - abs(zstar[3])) < 2e-2 and abs(abs(z[5]) - abs(zstar[5])) < 2e-2)'''),
    ('''elif args.vev_light == "none": VEV = {}''', '''elif args.vev_light == "none": VEV = {}
elif args.vev_light == "sm": VEV = {"(1,1)_|Y|=0": "sub1"}'''),
    ('''    if lab == "(1,1)_|Y|=0":
        js = [j for j, c in enumerate(cols) if c["block"] == "Sigma126bar"][:1] + [j for j, c in enumerate(cols) if c["block"] == "S"][:1]''',
     '''    if lab == "(1,1)_|Y|=0":
        js = ([j for j, c in enumerate(cols) if c["block"] == "Sigma126bar"][:1] if nl >= 2 else []) + [j for j, c in enumerate(cols) if c["block"] == "S"][:1]'''),
]
for a, b in reps:
    assert a in lp, a[:80]
    lp = lp.replace(a, b)
(HERE / "lp_sm.py").write_text(lp, encoding="utf-8")

de = (HERE / "r2_descend.py").read_text(encoding="utf-8")
a = 'parts = start[4:].split(":"); arr = np.load(K.SCRATCH / parts[0])'
assert a in de
de = de.replace(a, 'parts = start[4:].split(":"); arr = np.load(K.find(parts[0]))')
(HERE / "r2_descend.py").write_text(de, encoding="utf-8")
print("patched")
