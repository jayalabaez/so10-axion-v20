import sys
import json
SK=2.4e34; R=4.53
for line in open(sys.argv[1]):
    if '{' not in line or 'coherent' in line: continue
    name, js = line.split(' {',1)
    try: d=json.loads('{'+js)
    except Exception: continue
    f=lambda k: ['%.3g'%x for x in d.get(k,[])]
    print(name, 'tau',f('tau_p_min_p05_med_p95_max'),'vR',f('v_R_min_p05_med_p95_max'),'L2',f('L2_min_p05_med_p95_max')[:2],'L3',f('L3_min_p05_med_p95_max')[:3],'fSK',d['frac_tau_gt_SK'],'fpass',d['frac_pass2L(tau>SK & L2>1)'],'fL3',d['frac_L3_gt_1'],'fvR',d['frac_vR_1e11_1e14'],'fall',d['frac_all(tau>SK & L2>1 & vR in [1e11,1e14])'])
for line in open(sys.argv[1]):
    if 'coherent' in line: print(line[:240].rstrip())
