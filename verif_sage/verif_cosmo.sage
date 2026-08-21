#!/usr/bin/env sage
# =============================================================================
#  Vérification INDÉPENDANTE des calculs de redshift_distance_gui.py sous SageMath
#  Aucun appel à astropy : tout est reconstruit depuis les constantes CODATA
#  et les équations de Friedmann, en précision étendue (mpmath).
#  La fonction de Fermi-Dirac des neutrinos massifs est calculée EXACTEMENT
#  (intégrale), tabulée puis interpolée, pour tester l'ajustement Komatsu
#  utilisé par astropy.
# =============================================================================
import json
from mpmath import (mp, mpf, sqrt as msqrt, exp as mexp, log as mlog, quad, inf,
                    pi as mpi, findroot, asinh as masinh, polyval, taylor)

mp.dps = 25

# ---------------------------------------------------------------- constantes
c_ms   = mpf('299792458')                 # m/s (exact, SI)
G      = mpf('6.6743e-11')                # m^3 kg^-1 s^-2 (CODATA 2022)
k_B    = mpf('1.380649e-23')              # J/K (exact, SI)
hbar   = mpf('1.054571817e-34')           # J.s
eV     = mpf('1.602176634e-19')           # J (exact)
Mpc_m  = mpf('3.0856775814913673e22')     # m
lyr_m  = mpf('9460730472580800')          # m (exact : 365.25 j x c)
Gyr_s  = mpf('1e9') * mpf('365.25') * 86400

# ---------------------------------------------------- paramètres Planck 2018
H0_kms_Mpc = mpf('67.66')
Om0        = mpf('0.30966')       # baryons + CDM (PAS les neutrinos)
Ob0        = mpf('0.04897')
Tcmb0      = mpf('2.7255')
Neff       = mpf('3.046')
m_nu_eV    = [mpf('0'), mpf('0'), mpf('0.06')]
Ok0        = mpf('0')

H0  = H0_kms_Mpc * mpf('1000') / Mpc_m
D_H = c_ms / H0
t_H = 1 / H0

rho_crit0  = 3 * H0**2 / (8 * mpi * G)
a_B        = mpi**2 * k_B**4 / (15 * hbar**3 * c_ms**3)
rho_gamma0 = a_B * Tcmb0**4 / c_ms**2
Ogamma0    = rho_gamma0 / rho_crit0

T_nu0 = (mpf(4) / 11)**(mpf(1) / 3) * Tcmb0
FD    = mpf(7) / 8 * (mpf(4) / 11)**(mpf(4) / 3)
neff_per_nu = Neff / len(m_nu_eV)
nu_y   = [m * eV / (k_B * T_nu0) for m in m_nu_eV]
massive = [y for y in nu_y if y > 0]
n_massless = len(nu_y) - len(massive)

# --------- f(y) exacte : (120/7pi^4) int_0^inf x^2 sqrt(x^2+y^2)/(e^x+1) dx
def f_exact_raw(y):
    y = mpf(y)
    return (120 / (7 * mpi**4)) * quad(lambda x: x**2 * msqrt(x**2 + y**2) / (mexp(x) + 1),
                                       [0, 5, 15, 40, inf])

# tabulation en log(y) + interpolation de Lagrange locale (ordre 8)
LY = [mpf(-14) + mpf(20) * mpf(i) / 400 for i in range(401)]   # log(y) de -14 a 6
FT = [f_exact_raw(mexp(l)) for l in LY]
_dl = LY[1] - LY[0]

def f_exact(y):
    y = mpf(y)
    if y <= 0:
        return mpf(1)
    l = mlog(y)
    if l <= LY[0]:
        return mpf(1)
    if l >= LY[-1]:                      # regime ultra non-relativiste : f ~ (7pi^4/120)... lineaire en y
        return f_exact_raw(y)
    i = int((l - LY[0]) / _dl)
    i = max(0, min(len(LY) - 9, i - 4))
    xs, ys = LY[i:i + 9], FT[i:i + 9]
    # Lagrange
    s = mpf(0)
    for j in range(9):
        term = ys[j]
        for k in range(9):
            if k != j:
                term *= (l - xs[k]) / (xs[j] - xs[k])
        s += term
    return s

K_K, K_P = mpf('0.3173'), mpf('1.83')
def f_komatsu(y):
    return (1 + (K_K * mpf(y))**K_P)**(1 / K_P)

def nu_rel_density(z, exact=True):
    zp1 = 1 + mpf(z)
    ff = f_exact if exact else f_komatsu
    return FD * neff_per_nu * (sum(ff(y / zp1) for y in massive) + n_massless)

Onu0_exact   = Ogamma0 * nu_rel_density(0, True)
Onu0_komatsu = Ogamma0 * nu_rel_density(0, False)
Ode0 = 1 - Om0 - Ogamma0 - Onu0_exact - Ok0

def E(z, exact=True):
    zp1 = 1 + mpf(z)
    Or = Ogamma0 * (1 + nu_rel_density(z, exact))
    return msqrt(Or * zp1**4 + Om0 * zp1**3 + Ok0 * zp1**2 + Ode0)

# formule affichée par le programme (aide F1) et par le cours
Om_label, OL_label = mpf('0.3111'), mpf('0.6889')
def E_label(z):
    return msqrt(Om_label * (1 + mpf(z))**3 + OL_label)

# ------------------------------------------------------------- intégrales
def D_C(z, exact=True):
    z = mpf(z)
    if z == 0: return mpf(0)
    return D_H * quad(lambda zz: 1 / E(zz, exact), [0, min(z, 1), z] if z > 1 else [0, z])

def t_L(z, exact=True):
    z = mpf(z)
    if z == 0: return mpf(0)
    return t_H * quad(lambda zz: 1 / ((1 + zz) * E(zz, exact)), [0, min(z, 1), z] if z > 1 else [0, z])

def age(z, exact=True):
    z = mpf(z)
    # u = 1/(1+z') : int_z^inf dz'/((1+z')E) = int_0^{1/(1+z)} du/(u E)
    hi = 1 / (1 + z)
    return t_H * quad(lambda u: 1 / (u * E(1 / u - 1, exact)), [mpf('1e-14'), hi / 100, hi])

# âge analytique (LCDM pur, sans rayonnement) : forme fermée en arcsinh
def age_analytic(z, Om=Om_label, OL=OL_label):
    return t_H * 2 / (3 * msqrt(OL)) * masinh(msqrt(OL / Om) * (1 + mpf(z))**mpf('-1.5'))

to_Glyr = lambda d: d / lyr_m / mpf('1e9')
to_Gyr  = lambda t: t / Gyr_s

Z = [mpf(s) for s in ['0', '0.00428', '0.01', '0.1', '0.158', '0.5', '1.0', '1.6',
                      '2.34', '5.0', '7.085', '10.6', '20.0', '100.0', '1089.8', '1500.0']]

rows = []
for z in Z:
    dc, tl, ag = D_C(z), t_L(z), age(z)
    rows.append({
        "z": float(z), "E": float(E(z)), "E_label_formula": float(E_label(z)),
        "DC_Mpc": float(dc / Mpc_m),
        "DC_Glyr": float(to_Glyr(dc)),
        "DL_Glyr": float(to_Glyr(dc * (1 + z))),
        "DA_Glyr": float(to_Glyr(dc / (1 + z))),
        "Dlt_Glyr": float(to_Glyr(c_ms * tl)),
        "tL_Gyr": float(to_Gyr(tl)),
        "age_Gyr": float(to_Gyr(ag)),
        "age_plus_tL_Gyr": float(to_Gyr(ag + tl)),
        "v_rec_c_H0DC": float(H0 * dc / c_ms),          # v_rec(t0)/c = H0 D_C/c
        "v_doppler_SR_c": float(((1 + z)**2 - 1) / ((1 + z)**2 + 1)),
    })

t0 = age(0)

def dDA(z):
    z = mpf(z)
    return (1 + z) / E(z) - D_C(z) / D_H
z_DAmax = findroot(dDA, mpf('1.6'))
DA_max  = to_Glyr(D_C(z_DAmax) / (1 + z_DAmax))

particle_horizon = D_H * quad(lambda zz: 1 / E(zz), [0, 1, 100, mpf('1e4'), mpf('1e6'), mpf('1e9')])
event_horizon    = D_H * quad(lambda a: 1 / (a * a * E(1 / a - 1)), [1, 10, 1000, inf])

# développements limités (coefficients exacts) --------------------------------
q0_label   = Om_label / 2 - OL_label
q0_full    = Om0 / 2 + Ogamma0 * (1 + nu_rel_density(0)) - Ode0   # Om/2 + Or - OL
# coefficients numeriques du DL : D(z)/D_H = z + c2 z^2 + ...
def series_coeff(fun, n=3, h=mpf('1e-4')):
    return taylor(fun, 0, n, h=h, method='quad') if False else None

out = {
    "method": "mpmath dps=%d, Fermi-Dirac exacte tabulee+interpolee" % mp.dps,
    "derived_params": {
        "hubble_distance_Mpc": float(D_H / Mpc_m),
        "hubble_distance_Glyr": float(to_Glyr(D_H)),
        "hubble_time_Gyr": float(to_Gyr(t_H)),
        "rho_crit0_g_cm3": float(rho_crit0 / 1000),
        "Ogamma0": float(Ogamma0),
        "T_nu0_K": float(T_nu0),
        "nu_y_massive": [float(y) for y in massive],
        "Onu0_exact_FD": float(Onu0_exact),
        "Onu0_komatsu": float(Onu0_komatsu),
        "komatsu_rel_err_pct_z0": float(100 * (Onu0_komatsu / Onu0_exact - 1)),
        "Ode0": float(Ode0),
        "Om0_plus_Onu0": float(Om0 + Onu0_exact),
        "Or0_relativiste_equiv": float(Ogamma0 * (1 + FD * Neff)),
        "Otot0": float(Om0 + Ogamma0 + Onu0_exact + Ode0),
        "q0_label_formula": float(q0_label),
        "q0_full": float(q0_full),
    },
    "t0_Gyr": float(to_Gyr(t0)),
    "t0_analytic_noRad_Gyr": float(to_Gyr(age_analytic(0))),
    "rows": rows,
    "DA_max": {"z": float(z_DAmax), "DA_Glyr": float(DA_max)},
    "horizons": {
        "particle_horizon_Glyr": float(to_Glyr(particle_horizon)),
        "hubble_sphere_Glyr": float(to_Glyr(D_H)),
        "event_horizon_Glyr": float(to_Glyr(event_horizon)),
        "ct0_Glyr": float(to_Glyr(c_ms * t0)),
    },
    "komatsu_check": [
        {"z": float(z), "f_exact": float(nu_rel_density(z, True)),
         "f_komatsu": float(nu_rel_density(z, False)),
         "rel_err_pct": float(100 * (nu_rel_density(z, False) / nu_rel_density(z, True) - 1))}
        for z in [mpf(0), mpf(1), mpf(10), mpf(100), mpf('1089.8')]
    ],
    "age_analytic_check": [
        {"z": float(z), "analytic_noRad_Gyr": float(to_Gyr(age_analytic(z)))}
        for z in [mpf(0), mpf(1), mpf('2.34'), mpf('10.6'), mpf('1089.8')]
    ],
}

import os
out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'verif_sage.json')
with open(out_path, 'w') as fh:
    json.dump(out, fh, indent=1)

print("=== Paramètres reconstruits (sans astropy) ===")
for k, v in out["derived_params"].items():
    print(f"  {k:26s} {v}")
print(f"  t0 (numerique)          {out['t0_Gyr']}")
print(f"  t0 (analytique sans ray){out['t0_analytic_noRad_Gyr']}")
print("\n=== Table ===")
for r in rows:
    print(f"z={r['z']:>9} DC={r['DC_Glyr']:9.4f} DL={r['DL_Glyr']:11.4f} DA={r['DA_Glyr']:8.5f} "
          f"Dlt={r['Dlt_Glyr']:8.4f} tL={r['tL_Gyr']:8.4f} age={r['age_Gyr']:.6f} "
          f"sum={r['age_plus_tL_Gyr']:.6f} vrec/c={r['v_rec_c_H0DC']:.4f}")
print("\nDA max :", out["DA_max"])
print("Horizons :", out["horizons"])
print("\nKomatsu vs Fermi-Dirac exacte :")
for r in out["komatsu_check"]:
    print(f"  z={r['z']:>8}  exact={r['f_exact']:.9f}  komatsu={r['f_komatsu']:.9f}  {r['rel_err_pct']:+.5f} %")
print("\nAge analytique (sans rayonnement) :", out["age_analytic_check"])
