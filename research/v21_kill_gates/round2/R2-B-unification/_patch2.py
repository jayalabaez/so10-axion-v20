p='r2b_scan.py'
s=open(p,encoding='utf-8').read()
s=s.replace('''        for L, xo in landau_cfg:
            p.alpha_x_inv_mpl = xo''','''        for L, xo in landau_cfg:
            if xo is not None and len(mphis) > 1 and mphi != 1e17:
                continue  # U(1)_X shooting only at the nominal Phi-pair mass (speed)
            p.alpha_x_inv_mpl = xo''')
open(p,'w',encoding='utf-8').write(s)
print('ok')
