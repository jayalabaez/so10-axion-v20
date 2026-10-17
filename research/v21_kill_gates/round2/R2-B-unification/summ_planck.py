import ast, sys
rows={}
for line in open('planck.out'):
    if '{' not in line or line.startswith('done'): continue
    head, d = line.split(' {',1)
    cont, key = head.split(' ',1)
    d = ast.literal_eval('{'+d)
    rows.setdefault(cont,{})[key]=d
SK=2.4e34
for cont, rr in rows.items():
    for s in ('s+1','s-1'):
        for L in ('2L','3L'):
            taus=[];Ls=[];vrs=[];fails=[];nos=[]
            for ci in range(-10,11):
                k=f'{s}|{L}|c{ci/10:.1f}'
                r=rr.get(k)
                if not r: continue
                if r.get('ok') in (True,'True'):
                    t=float(r['tau_p']); taus.append((ci/10,t)); Ls.append(float(r.get('L'+L[0]) or 0)); vrs.append(float(r['v_R']))
                    if t<SK: fails.append(ci/10)
                else: nos.append(ci/10)
            if not taus: continue
            tmin=min(taus,key=lambda x:x[1]); tmax=max(taus,key=lambda x:x[1])
            print(f"{cont:7s} {s} {L}: tau min {tmin[1]:.2e} (c={tmin[0]:+.1f}) max {tmax[1]:.2e} (c={tmax[0]:+.1f}); L{L[0]} min {min(Ls):.2f}; v_R {min(vrs):.2e}-{max(vrs):.2e}; tau<SK at c={fails if len(fails)<8 else str(len(fails))+' values'}; no-solution c={nos}")
