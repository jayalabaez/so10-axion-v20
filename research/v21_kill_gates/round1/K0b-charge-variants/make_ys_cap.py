"""Create ys_cap_k0b.py from K0's k0_ys_cap.py with SUM_D, b_X and the output tag taken from argv
(the gauge environment is identical for every Type-I candidate: same multiplet structure as F17 below M_Pl)."""
from pathlib import Path

SRC = Path(r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\wfV21\K0-contract\k0_ys_cap.py")
DST = Path(__file__).resolve().parent / "ys_cap_k0b.py"
text = SRC.read_text(encoding="utf-8")
old_sum = 'SUM_D = 60.0       # sum_i d_i (58 Dirac components + 2 singlet pairs)'
assert old_sum in text
text = text.replace(old_sum, 'SUM_D = float(sys.argv[1]) if len(sys.argv) > 1 else 60.0\nBX_ARG = sys.argv[2] if len(sys.argv) > 2 else "12865/3"\nTAG = sys.argv[3] if len(sys.argv) > 3 else "k0b"')
old_bx = """    sys.path.insert(0, str(HERE))
    from k0_couplings import FERMIONS, SCALARS
    dim = {1: 1, 10: 10, 16: 16, 126: 126, 210: 210}
    bx = sum(Fr(2, 3) * g * dim[abs(r)] * x * x for _n, r, x, g in FERMIONS)
    bx += sum(Fr(1, 3) * dim[abs(r)] * x * x for _n, r, x, real in SCALARS if not real)
"""
assert old_bx in text
text = text.replace(old_bx, "    bx = Fr(BX_ARG)\n")
old_out = '(HERE / "k0_ys_cap.json")'
assert old_out in text
text = text.replace(old_out, '(HERE / ("ys_cap_%s.json" % TAG))')
# K0 read its NDA P from k0_quality_relics.json; not present here -> p_nda stays None (try/except already there)
DST.write_text(text, encoding="utf-8")
print("wrote", DST, len(text))
