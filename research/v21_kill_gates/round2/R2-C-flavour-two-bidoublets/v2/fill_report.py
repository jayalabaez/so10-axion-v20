import io
R = "../REPORT.txt"
s = open(R, encoding="utf-8").read()
tab = open("tables.txt", encoding="utf-8").read()
tab = tab.split("  f-bound variant")[0]
tab = tab.replace("  v_R = 1e+11  R813 M_U = 2.40e+16: chi2 = 3110.20", "  v_R = 1e+11  R813 M_U = 2.40e+16 [first run, old 1e3 fallback; exact DE+CMA+BH in the physical region]: chi2 = 3110.20", 1)
tab = tab.replace("  v_R = 1e+11  R813 M_U = 2.40e+16: chi2 = 3958.70", "  v_R = 1e+11  R813 M_U = 2.40e+16 [rerun 'mainfix', corrected fallback]: chi2 = 3958.70", 1)
tab = tab.replace("  v_R = 2e+12  R813 M_U = 2.40e+16: chi2 = 124.61", "  v_R = 2e+12  R813 M_U = 2.40e+16 [main campaign; the continuation scan below finds 109.75 at the same v_R]: chi2 = 124.61", 1)
tab += ("  Majorana-bound variants (vscan from the same starts):\n"
        "     f <= 2 sqrt(4 pi): v_R = 1e12: 176.3 (scalar DOP853; batched RK4 157.5 -- f(M_U) = 7.1, step too coarse), 2e12: 102.25 (f(M_U) = 4.6,\n"
        "                        DOP853 = RK4), 3e12: 121.27 (unchanged)\n"
        "     no f bound:          v_R = 1e12: batched 136.2 but DOP853 1.06e5 (f(M_U) ~ 10: non-perturbative, numerically unreliable -> discarded),\n"
        "                        2e12: 102.25 (same point as with f <= 2 sqrt(4 pi))\n"
        "  theta23-FREE continuation (sigma(sin^2 th23) = 10; chi2 of the other 17): 3e12: 25.5 (full DIAG campaign), 2e12: 64.1, 1e12: 198.5\n")
rep = {
 "{{H2E12}}": "109.7 (c)  164 (**)  75.2            0.382 (-5.9)       f at its bound (f(M_U) = sqrt(4 pi)); main campaign 124.6",
 "{{GMIN}}": "109.7",
 "{{F02E12}}": "164 (main-campaign point, 124.6 at floor 1 %)",
 "{{COMP2E12}}": "r = 54.7, s = 0.386 - 0.113i, c_d126 = 0.0036; (|c_u10|, |c_u126|, |c_d10|, |c_d126|) = (0.997, 0.079, 0.0182, 0.0036)",
 "{{TABLE}}": tab.rstrip("\n"),
}
for k, v in rep.items():
    assert k in s, k
    s = s.replace(k, v)
s = s.replace("   (*) best of two independent exact searches (3110 and 3959); (c) exact continuation scan from the main-run minima.",
              "   (*) best of two independent exact searches (3110 and 3959); (c) exact continuation scan from the main-run minima;\n"
              "   (**) floor-0 value at the main-campaign 2e12 point (the 109.7 continuation point was not floor-0 polished).")
s = s.replace("then PREDICTS sin^2 th23 = 0.314 (10.4 sigma below NuFIT 6.0).",
              "then PREDICTS sin^2 th23 = 0.314 (10.4 sigma below NuFIT 6.0); at 2e12 / 1e12 even chi2_17 = 64.1 / 198.5.")
s = s.replace("(sigma -> 10, v_R = 3e12): chi2_17 = 25.5 (all pulls < 2.3) and the model PREDICTS sin^2 th23 = 0.314.",
              "(sigma -> 10, v_R = 3e12): chi2_17 = 25.5 (all pulls < 2.3) and the model PREDICTS sin^2 th23 = 0.314;\n"
              "    continuation of the same theta23-free fit: chi2_17 = 64.1 at 2e12 and 198.5 at 1e12.  Since chi2_18 >= chi2_17,\n"
              "    no value of theta23 data could bring the 18-observable chi2 below ~25 in this model at v_R <= 3e12 [NUM, search-limited].")
s = s.replace("|dchi2| <= 0.2 at every reported point (<= 0.05 for chi2 < 300);",
              "|dchi2| <= 0.2 at every reported point with f(M_U) <~ 5 (<= 0.1 for chi2 < 300); for f(M_U) >= 7 the fixed-step RK4 fails\n"
              "  (1e12 variants in 6.5) and only DOP853 values are quoted;")
s = s.replace("    bound): f <= 2 sqrt(4 pi): 157.5 (1e12), 102.2 (2e12), 121.3 (3e12); no f bound at all (only |Y126_act| <= 1.5):\n"
              "    136.2 (1e12, f(M_U) ~ 10, non-perturbative), 102.2 (2e12).  The window edge moves, the minimum does not approach 25.",
              "    bound): f <= 2 sqrt(4 pi): 176.3 (1e12, DOP853), 102.2 (2e12), 121.3 (3e12); no f bound at all (only |Y126_act| <= 1.5):\n"
              "    2e12 unchanged (102.2); at 1e12 the optimiser runs into f(M_U) ~ 10 where the one-loop RG is meaningless (discarded).\n"
              "    The window edge moves, the minimum does not approach 25 (lowest value anywhere: 102.2).")
s = s.replace("|c_u|/|c_d| ~ 50-60, a \"tan beta\" ~ 55", "|c_u|/|c_d| ~ 30-60")
open(R, "w", encoding="utf-8").write(s)
left = [x for x in ("{{",) if x in s]
print("placeholders left:", s.count("{{"))
