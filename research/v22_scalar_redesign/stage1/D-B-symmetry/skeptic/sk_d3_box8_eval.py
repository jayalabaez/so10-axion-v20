"""SKEPTIC: independent re-evaluation (sk_d3_eval machinery, own code) of the box-8 round-3 slice point SK_R3_box8_o0 and
the two deepest fresh-descent endpoints from it (private scratch copy).  Writes sk_d3_box8_eval.json."""
import json, os, sys, time
from pathlib import Path
os.environ["DB_LPDIR"] = r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\v22_DB_skeptic\lp"
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import sk_d3_eval as E  # noqa: E402  (own module)
E.CASES = [("SK8_bankA", "SK_R3_box8_o0.npz", "descend_SK8_bankA"), ("SK8_p831", "SK_R3_box8_o0.npz", "descend_SK8_p831")]
_orig_dump = E.json.dump
def _dump(obj, fh, **kw):
    fh.close(); return _orig_dump(obj, open(HERE / "sk_d3_box8_eval.json", "w"), **kw)
E.json.dump = _dump
E.main()
