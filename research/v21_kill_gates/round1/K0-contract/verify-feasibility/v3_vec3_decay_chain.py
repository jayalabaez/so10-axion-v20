"""Vec3-pair lifetime via SEQUENTIAL lower-dimension operators (EST, c = 1), correcting the single-operator
(dim-10) picture used by the researcher.  All operators SO(10) x U(1)_X invariant (checked in verify_k0_v2.py).
"""
import json, math
MPL = 2.435e18; GEV_S = 6.582e-25
sig, phi, M = 1e13 / 0.304, 1e17, 1e13
# dim-5: Vec1 Vec3 conj[H10] S / M_Pl  -> Yukawa y_eff Vec1 Vec3 H*  (16.16.10), f = (+1,-1,0)
y_eff = sig / MPL
# dim-7: F Vec1bar S^3 conj[Phi17] / M_Pl^3 -> Dirac mass m F Vec1bar -> Vec1 contains the light F with angle m/(y1 <S>)
m17 = sig ** 3 * phi / MPL ** 3
theta_1F = m17 / M
g = y_eff * theta_1F                       # Vec3 -> F + H* (H* = tuned light doublet, massless at tree level)
Gam = g ** 2 * M / (16 * math.pi)
# dim-8 direct mixing Vec2bar Vec3 S^4 conj[Phi17] / M_Pl^4 (16bar.16): mass m8; Vec2 pair decays promptly (dim-5 F Vec2bar S*^2: angle 4e-5)
m8 = sig ** 4 * phi / MPL ** 4
theta_32 = m8 / (0.1 * M)                  # non-degenerate pairs (|y2 - y3| ~ 0.1 y): conservative
theta_2F = (sig ** 2 / MPL) / M
Gam8 = (theta_32 * theta_2F) ** 2 * (1 / 137.0) * M / (8 * math.pi)
# researcher-type single dim-10 operator F Vec3 conj[H10] S^5 conj[Phi17] / M_Pl^6
g10 = sig ** 5 * phi / MPL ** 6
Gam10 = g10 ** 2 * M / (16 * math.pi)
out = {"dim5_Yukawa_y_eff": y_eff, "dim7_F_Vec1bar_mixing_mass_GeV": m17, "theta_Vec1_F": theta_1F,
       "Vec3->F+H_coupling": g, "Gamma_GeV_chain_dim5xdim7": Gam, "tau_s_chain_dim5xdim7": GEV_S / Gam,
       "dim8_Vec2bar_Vec3_mixing_mass_GeV": m8, "theta_Vec3_Vec2bar(conservative)": theta_32,
       "tau_s_dim8_route": GEV_S / Gam8, "tau_s_single_dim10_operator": GEV_S / Gam10,
       "conclusion": "tau(Vec3 pair) ~ 1e-5 s (c = 1; prompt if M_3 > M_1 via on-shell Vec1 + H): NOT a long-lived relic; "
                     "the researcher's 'second long-lived relic, tau ~ 1e15-1e16 s' is refuted (that is the single-operator rate only)"}
print(json.dumps(out, indent=1)); open("v3_vec3_decay_chain.json", "w").write(json.dumps(out, indent=1))
