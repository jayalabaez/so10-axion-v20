import re
p='r2b_lib.py'
s=open(p,encoding='utf-8').read()
s=s.replace('''                landau_event: bool = False, alpha_stop: float = 1.0) -> tuple[np.ndarray, float, bool]:''','''                landau_event: bool = False, alpha_stop: float = 1.0, event_index=None) -> tuple[np.ndarray, float, bool]:''')
s=s.replace('''        def ev(t, y):
            return float(np.min(y) - 1.0 / alpha_stop)''','''        def ev(t, y):
            if event_index is not None:
                return float(y[event_index] - 1.0 / alpha_stop)
            return float(np.min(y) - 1.0 / alpha_stop)''')
open(p,'w',encoding='utf-8').write(s)
p='r2b_model.py'
s=open(p,encoding='utf-8').read()
s=s.replace('''        def run_full(y0, t_stop, event=True):
            y, t, hit = run_segment(seg_lo, y0, tu, min(tphi, t_stop), landau_event=event)
            if (not hit) and t_stop > tphi:
                y, t, hit = run_segment(seg_hi, y, tphi, t_stop, landau_event=event)
            return y, t, hit''','''        def run_full(y0, t_stop, event=True, idx=None):
            y, t, hit = run_segment(seg_lo, y0, tu, min(tphi, t_stop), landau_event=event, event_index=idx)
            if (not hit) and t_stop > tphi:
                y, t, hit = run_segment(seg_hi, y, tphi, t_stop, landau_event=event, event_index=idx)
            return y, t, hit''')
s=s.replace('''        yy, _, h = run_full(y0.copy(), tpl, event=True)
        a_mpl = float(yy[0]) if not h else None''','''        yy, _, h = run_full(y0.copy(), tpl, event=True, idx=0)
        a_mpl = float(yy[0]) if not h else None''')
s=s.replace('''            out[key + "_first"] = lm["first_to_alpha1"]
            if xo is not None:
                out[key + "_axMU"] = lm["alphaX_inv_MU"]''','''            out[key + "_first"] = lm["first_to_alpha1"]
            out[key + "_a10inv_MPl"] = lm["alpha_inv_MPl"]
            if xo is not None:
                out[key + "_axMU"] = lm["alphaX_inv_MU"]''')
open(p,'w',encoding='utf-8').write(s)
print('ok')
