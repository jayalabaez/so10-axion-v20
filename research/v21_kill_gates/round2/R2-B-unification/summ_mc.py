import json,sys
for line in open('mc.out'):
    if '{' not in line or 'coherent' in line: continue
    name, js = line.split(' {',1)
    try: d=json.loads('{'+js)
    except Exception: continue
    f=lambda k: ['%.3g'%x for x in d.get(k,[])]
    print(name, 'tau',f('tau_p_min_p05_med_p95_max'),'MU',f('M_U_min_p05_med_p95_max')[2],'vR',f('v_R_min_p05_med_p95_max'),'L2min',f('L2_min_p05_med_p95_max')[:1],'L3',f('L3_min_p05_med_p95_max')[:3],'fSK',d['frac_tau_gt_SK'],'fHK',d['frac_tau_gt_HK'],'fpass',d['frac_pass2L(tau>SK & L2>1)'],'fall',d['frac_all(tau>SK & L2>1 & vR in [1e11,1e14])'])
for line in open('mc.out'):
    if 'coherent' in line: print(line[:260].rstrip())
