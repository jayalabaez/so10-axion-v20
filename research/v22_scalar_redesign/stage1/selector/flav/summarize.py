"""Selector: summary of the exact-structure refits (D-D code, unedited) + translation of the designer's c5 to the
Gamma-tensor convention of sel_clebsch.py (unit-norm vev forms; |Clebsch| relative to the 10 channel).
c5 := max(|A_1|, |A_15|)/(kappa c10_allow) (D-D definition).  a1 = |A_1|/(kappa c10) = c5/max(1,|rho|).
Exact channel: A_1 = c kappa c10 C_1 v_1, A_15 = c kappa c10 C_15 v_15 with v_1^2 + v_15^2 <= 1 (unit vev form):
   c >= a1 sqrt(1/C_1^2 + rho^2/C_15^2).   45: (C_1, C_15) = (0.7071, 0.5774)  [T3R, B-L];  210: (1.0, 0.4082)  [P, omega].
EST: assumes kappa(45) = kappa(210) = 0.01 and that the up-sector channel normalisation follows the same pattern."""
import json, glob, math
CL = {"45": (1 / math.sqrt(2), 1 / math.sqrt(3)), "210": (1.0, 1 / math.sqrt(6))}
rows = []
for f in sorted(glob.glob('d2c_L2x*.json')):
    d = json.load(open(f)); w = d['with_d5']; dr = w['derived']
    ch = "45" if d['opts']['eta1'] < 0 else "210"
    c5 = dr.get('c5_needed'); rho = w['rho']
    a1 = c5 / max(1.0, abs(rho)); C1, C15 = CL[ch]
    cG = a1 * math.sqrt(1 / C1 ** 2 + rho ** 2 / C15 ** 2)
    rows.append(dict(label=d['label'], channel=ch, eta1=d['opts']['eta1'], eps=w['eps'], c5max=d['opts']['c5_max'],
                     chi2=w['chi2_obs'], penalty=w['penalty2'], npull3=w['n_pulls_gt3'],
                     maxpull=max(abs(v) for v in w['pulls'].values()), rho=rho, c5_needed=c5, c_Gamma_kappa0p01=cG,
                     r=w['r'], s=w['s'], vR_window=[dr.get('sigma_min'), dr.get('sigma_max')], ms_md_MU=w['ms_over_md_MU'],
                     m_nu_eV=w['m_nu_eV'], c10_allow=dr.get('c10_allow'), c126_max=dr.get('c126_max')))
for r in rows:
    print(f"{r['label']:12s} ch {r['channel']:3s} c5max {r['c5max']:<4} chi2 {r['chi2']:.2e} maxpull {r['maxpull']:.3f} "
          f"rho {r['rho']:+.3f} c5 {r['c5_needed']:.3f} c_Gamma {r['c_Gamma_kappa0p01']:.3f} r {r['r']:.1f} "
          f"s {r['s'][0]:+.3f}{r['s'][1]:+.3f}i vR [{r['vR_window'][0]:.2e},{r['vR_window'][1]:.2e}] ms/md {r['ms_md_MU']:.2f}")
json.dump(rows, open('exact_refits_summary.json', 'w'), indent=1)
