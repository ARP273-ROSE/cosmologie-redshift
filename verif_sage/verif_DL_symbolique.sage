#!/usr/bin/env sage
# Vérification SYMBOLIQUE des développements limités au 2e ordre du cours
# (chapitre "Pourquoi elles se confondent à petit z")
z, q0, Om, OL = var('z q0 Om OL')

# E(z) pour LCDM plat sans rayonnement
E = sqrt(Om * (1 + z)^3 + (1 - Om))
# parametre de deceleration : q0 = Om/2 - OL  (OL = 1 - Om ici)
q0_expr = Om / 2 - (1 - Om)

print("=== E(z) au 2e ordre ===")
Eser = E.series(z, 3)
print(Eser)
print("verif : E = 1 + (1+q0) z + ... ->  coeff z :", Eser.coefficient(z, 1).simplify_full(),
      "  vs 1+q0 =", (1 + q0_expr).simplify_full())

# D_C / D_H = int_0^z dz'/E
f = 1 / E
ser = f.series(z, 3).truncate()
DC = integrate(ser, z, 0, z).expand()
print("\n=== D_C/D_H ===")
print(DC)
c2_DC = DC.coefficient(z, 2).simplify_full()
print("coeff z^2 :", c2_DC, " ; -(1+q0)/2 =", (-(1 + q0_expr) / 2).simplify_full(),
      " ; egal ?", bool((c2_DC - (-(1 + q0_expr) / 2)).simplify_full() == 0))

DL = ((1 + z) * DC).expand()
DA = (DC / (1 + z)).series(z, 3).truncate().expand()
print("\n=== D_L/D_H ===", DL.coefficient(z, 2).simplify_full(),
      " ; (1-q0)/2 =", ((1 - q0_expr) / 2).simplify_full(),
      " ; egal ?", bool((DL.coefficient(z, 2) - (1 - q0_expr) / 2).simplify_full() == 0))
print("=== D_A/D_H ===", DA.coefficient(z, 2).simplify_full(),
      " ; -(3+q0)/2 =", (-(3 + q0_expr) / 2).simplify_full(),
      " ; egal ?", bool((DA.coefficient(z, 2) - (-(3 + q0_expr) / 2)).simplify_full() == 0))

g = 1 / ((1 + z) * E)
Dlt = integrate(g.series(z, 3).truncate(), z, 0, z).expand()
print("=== D_lt/D_H ===", Dlt.coefficient(z, 2).simplify_full(),
      " ; -(2+q0)/2 =", (-(2 + q0_expr) / 2).simplify_full(),
      " ; egal ?", bool((Dlt.coefficient(z, 2) - (-(2 + q0_expr) / 2)).simplify_full() == 0))

print("\n=== Application numerique Om=0.3111 ===")
sub = {Om: 0.3111}
print("q0 =", q0_expr.subs(sub))
for nom, expr in [("D_C", DC), ("D_L", DL), ("D_A", DA), ("D_lt", Dlt)]:
    print(f"  {nom}/D_H = z + ({float(expr.coefficient(z,2).subs(sub)):.5f}) z^2")

print("\n=== Test numerique du DL a z=0.1 (D_H = 14.4516 Gly, valeur exacte 1.41077 Gly) ===")
DH = 14.451555153425794
for nom, expr in [("D_C", DC), ("D_L", DL), ("D_A", DA), ("D_lt", Dlt)]:
    v = DH * expr.subs(sub).subs(z=0.1)
    print(f"  {nom}(0.1) DL2 = {float(v):.5f} Gly")
print("  (exact : D_C=1.41077  D_L=1.55185  D_A=1.28258  D_lt=1.34524)")

print("\n=== Forme fermee de l'age en LCDM plat sans rayonnement ===")
t = var('t')
age_expr = 2 / (3 * sqrt(OL)) * arcsinh(sqrt(OL / Om) * (1 + z)^(-3/2))
# verification : d/dz [ -age ] doit valoir 1/((1+z) E)
d = diff(age_expr.subs(OL == 1 - Om), z)
check = (-d - 1 / ((1 + z) * E)).simplify_full()
print("d(age)/dz + 1/((1+z)E) =", check, "  -> nul ?", bool(check == 0))
