import ast, sys
fn = sys.argv[1]; pref = sys.argv[2]
for line in open(fn):
    if not line.startswith(pref + ' Ms'): continue
    head, d = line.split(' {',1); d=ast.literal_eval('{'+d)
    key=head.split(' ',1)[1]
    if '|1L' in key:
        print(key, 'vR',d.get('v_R'),'MU',d.get('M_U'),'tau',d.get('tau_p')); continue
    L = '2' if '|2L' in key else '3'
    print(key, 'vR',d.get('v_R'),'MU',d.get('M_U'),'aU',d.get('alpha_U_inv'),'tau',d.get('tau_p'), f'L{L}@MU/3e16/1e17/1.25e17:', d.get(f'L{L}@1'), d.get(f'L{L}@3e+16'), d.get(f'L{L}@1e+17'), d.get(f'L{L}@1.25e+17'), 'a10MPl(ax=1)@1e17:', d.get(f'L{L}x1@1e+17_a10MPl'), 'a10MPl@1e17:', d.get(f'L{L}@1e+17_a10MPl'))
