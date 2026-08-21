#!/usr/bin/env sage
# =============================================================================
#  Vérification SageMath des deux ajouts d'août 2026 :
#    1. corrélation rho(H0, Omega_m), déduite de la contrainte sur omega_m ;
#    2. distance comobile transverse D_M pour Ok != 0.
#
#  Le modèle est reconstruit à l'identique de celui d'astropy (photons +
#  neutrinos avec l'ajustement de Komatsu 2011) pour que la comparaison porte
#  sur les VALEURS ABSOLUES, pas seulement sur les rapports.
#
#  Lancement :
#    sage verif_sage/verif_courbure_sigma.sage
# =============================================================================
import json
from mpmath import (mp, mpf, sqrt as msqrt, sinh as msinh, sin as msin,
                    quad, pi as mpi)

mp.dps = 25

# ------------------------------------------------------- 1. corrélation H0-Om
Om, h, wm = var('Om h wm')
sOm, sh, swm, rho = var('sOm sh swm rho')

rel = (swm / wm)^2 == (sOm / Om)^2 + 4 * (sh / h)^2 + 4 * rho * (sOm / Om) * (sh / h)
rho_expr = solve(rel, rho)[0].rhs()

wm_val  = 0.11933 + 0.02242 + 0.06 / 93.14       # Oc h^2 + Ob h^2 + omega_nu
swm_val = sqrt(0.00091^2 + 0.00014^2)
vals = {Om: 0.3111, sOm: 0.0056, h: 0.6766, sh: 0.0042, wm: wm_val, swm: swm_val}
rho_val = float(rho_expr.subs(vals))

print("=== 1. Corrélation H0 - Omega_m ===")
print(f"  omega_m = {wm_val:.5f} +- {swm_val:.5f}    (Om h^2 = {0.3111*0.6766^2:.5f})")
print(f"  rho     = {rho_val:.4f}")
print("  -> le programme utilise RHO_H0_OM = -0.9763")
assert abs(rho_val + 0.9763) < 5e-4, "rho ne correspond plus a la valeur du programme"

# ---------------------------------------------------------- 2. modèle complet
c_ms  = mpf('299792458')
Mpc_m = mpf('3.0856775814913673e22')
lyr_m = mpf('9460730472580800')
k_B   = mpf('1.380649e-23')
eV    = mpf('1.602176634e-19')

Om0_astropy = mpf('0.30966')      # baryons + CDM (convention astropy)
Tcmb0 = mpf('2.7255')
Neff  = mpf('3.046')
m_nu  = mpf('0.06')               # eV, une seule espèce massive

def build(H0_kms, Ok):
    """Reconstruit E(z) et D_H pour (H0, Ok), avec le meme contenu qu'astropy."""
    H0 = mpf(H0_kms) * 1000 / Mpc_m
    D_H = c_ms / H0
    G      = mpf('6.6743e-11')
    hbar   = mpf('1.054571817e-34')
    rho_c  = 3 * H0**2 / (8 * mpi * G)
    a_B    = mpi**2 * k_B**4 / (15 * hbar**3 * c_ms**3)
    Ogam   = a_B * Tcmb0**4 / c_ms**2 / rho_c
    T_nu0  = (mpf(4) / 11)**(mpf(1) / 3) * Tcmb0
    FD     = mpf(7) / 8 * (mpf(4) / 11)**(mpf(4) / 3)
    nu_y   = m_nu * eV / (k_B * T_nu0)
    K, P   = mpf('0.3173'), mpf('1.83')

    def nu_rel(z):                      # ajustement Komatsu 2011, comme astropy
        y = nu_y / (1 + mpf(z))
        return FD * (Neff / 3) * ((1 + (K * y)**P)**(1 / P) + 2)

    Onu0 = Ogam * nu_rel(0)
    Ode0 = 1 - Om0_astropy - Ogam - Onu0 - mpf(Ok)

    def E(z):
        zp1 = 1 + mpf(z)
        Or = Ogam * (1 + nu_rel(z))
        return msqrt(Or * zp1**4 + Om0_astropy * zp1**3 + mpf(Ok) * zp1**2 + Ode0)

    return E, D_H

def D_C(E, D_H, z):
    z = mpf(z)
    pts = [0, mpf(1), z] if z > 1 else [0, z]
    return D_H * quad(lambda zz: 1 / E(zz), pts)

def D_M(E, D_H, z, Ok):
    Ok = mpf(Ok)
    dc = D_C(E, D_H, z)
    if Ok > 0:
        return D_H / msqrt(Ok) * msinh(msqrt(Ok) * dc / D_H)
    if Ok < 0:
        return D_H / msqrt(-Ok) * msin(msqrt(-Ok) * dc / D_H)
    return dc

to_Glyr = lambda d: float(d / lyr_m / 1e9)

print("\n=== 2. Distances avec courbure (Sage, modele identique a astropy) ===")
print(f"  {'z':>8} {'Ok':>8} {'D_C (Gal)':>12} {'D_M (Gal)':>12} {'D_L (Gal)':>12} {'D_A (Gal)':>11}")
rows = []
for Ok in ['-0.01', '0', '0.01']:
    E, D_H = build('67.66', Ok)
    for z in ['0.5', '2.34', '10.6', '1089.8']:
        dc, dm = D_C(E, D_H, z), D_M(E, D_H, z, Ok)
        zz = mpf(z)
        row = {"z": float(z), "Ok": float(Ok), "DC_Glyr": to_Glyr(dc), "DM_Glyr": to_Glyr(dm),
               "DL_Glyr": to_Glyr(dm * (1 + zz)), "DA_Glyr": to_Glyr(dm / (1 + zz))}
        rows.append(row)
        print(f"  {row['z']:>8} {row['Ok']:>8} {row['DC_Glyr']:>12.4f} {row['DM_Glyr']:>12.4f}"
              f" {row['DL_Glyr']:>12.4f} {row['DA_Glyr']:>11.5f}")

# ------------------------------------------------- 3. distances en SH0ES
print("\n=== 3. Effet de H0 (tension de Hubble) a z = 2.34, Ok = 0 ===")
for H0 in ['67.66', '73.04']:
    E, D_H = build(H0, 0)
    dc = D_C(E, D_H, '2.34')
    print(f"  H0 = {H0:>6} -> D_C = {to_Glyr(dc):.4f} G al")
E1, DH1 = build('67.66', 0); E2, DH2 = build('73.04', 0)
r = to_Glyr(D_C(E2, DH2, '2.34')) / to_Glyr(D_C(E1, DH1, '2.34')) - 1
print(f"  ecart = {100*r:+.2f} %   (attendu ~ -7.4 %, les distances varient en 1/H0)")

out = {"rho_H0_Om": rho_val, "rows": rows, "shoes_shift_pct": 100 * r}
import os
out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'verif_courbure_sigma.json')
with open(out_path, 'w') as fh:
    json.dump(out, fh, indent=1)
print("\nJSON ecrit : verif_courbure_sigma.json")
