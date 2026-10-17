import json, time, math, sys, numpy as np, fit
from scipy.optimize import differential_evolution
inp=json.load(open("inputs_mz.json")); R=fit.Runner(inp,2.6e13,2.13e16,"T2"); T=fit.build_targets(inp,0.01)
type2 = len(sys.argv)>1 and sys.argv[1]=="II"
P=fit.Proxy2(R,T,type2=type2)
seed=int(sys.argv[2]) if len(sys.argv)>2 else 0
FS=3e-3
def unpack(q):
    p=np.zeros(P.n); p[0:12]=q[0:12]*FS
    p[12]=10**q[12]; p[13]=q[13]; p[14]=10**q[14]; p[15]=q[15]; p[16]=q[16]
    if type2: p[17]=q[17]; p[18]=q[18]
    return p
def obj(q):
    r=P.residuals(unpack(q))[0]
    return float(np.sum(r**2))
bounds=[(-2,2)]*12+[(1.0,2.6),(-math.pi,math.pi),(-2.0,1.5),(-math.pi,math.pi),(-4.0,-1.5)]
if type2: bounds+=[(-12.5,-8.5),(-math.pi,math.pi)]
t0=time.time()
de=differential_evolution(obj,bounds,seed=seed,popsize=25,maxiter=1500,tol=1e-12,mutation=(0.5,1.0),recombination=0.9,init="latinhypercube",polish=False)
print("DE chi2", de.fun, "nfev", de.nfev, "t", round(time.time()-t0), flush=True)
r=fit.fit_proxy(P,unpack(de.x),max_nfev=4000,method="lm")
print("LM polish chi2", r["chi2"], "pen", r["penalty"], "y10", r["ymax10_act"], "y126", r["ymax126_act"], "cd126", r["cd126"])
print("pulls", {k: round(v,2) for k,v in r["pulls"].items()})
json.dump(r, open(f"de_{'II' if type2 else 'I'}_{seed}.json","w"), indent=1)
