#!/usr/bin/env python3
"""Valeurs de référence astropy (backend réellement utilisé par le programme)
   -> JSON pour comparaison avec le recalcul indépendant SageMath."""
import json
import numpy as np
from astropy.cosmology import Planck18 as cosmo
from astropy import units as u, constants as const
from scipy.optimize import minimize_scalar

Z = [0.0, 0.00428, 0.01, 0.1, 0.158, 0.5, 1.0, 1.6, 2.34, 5.0, 7.085, 10.6, 20.0, 100.0, 1089.8, 1500.0]

out = {
    "astropy_version": __import__("astropy").__version__,
    "params": {
        "H0": cosmo.H0.value, "Om0": cosmo.Om0, "Ode0": cosmo.Ode0,
        "Ogamma0": cosmo.Ogamma0, "Onu0": cosmo.Onu0, "Ok0": cosmo.Ok0,
        "Tcmb0": cosmo.Tcmb0.value, "Tnu0": cosmo.Tnu0.value, "Neff": cosmo.Neff,
        "m_nu_eV": [float(m) for m in cosmo.m_nu.value],
        "Ob0": cosmo.Ob0,
        "nu_y": [float(y) for y in cosmo._nu_info.nu_y],
        "neff_per_nu": float(cosmo._nu_info.neff_per_nu),
        "n_massless_nu": float(cosmo._nu_info.n_massless_nu),
        "critical_density0_gcm3": cosmo.critical_density0.value,
        "hubble_distance_Mpc": cosmo.hubble_distance.value,
        "hubble_time_Gyr": cosmo.hubble_time.value,
        "Om_total_incl_nu": cosmo.Om0 + cosmo.Onu0,
    },
    "constants": {
        "c_m_s": const.c.value, "G": const.G.value, "k_B": const.k_B.value,
        "Mpc_m": (1 * u.Mpc).to_value(u.m), "lyr_m": (1 * u.lyr).to_value(u.m),
        "Gyr_s": (1 * u.Gyr).to_value(u.s),
    },
    "t0_Gyr": cosmo.age(0).to_value(u.Gyr),
    "rows": [],
}

for z in Z:
    row = {
        "z": z,
        "E": float(cosmo.efunc(z)),
        "H_km_s_Mpc": cosmo.H(z).value,
        "DC_Mpc": cosmo.comoving_distance(z).to_value(u.Mpc),
        "DC_Glyr": cosmo.comoving_distance(z).to_value(u.Glyr),
        "DL_Glyr": cosmo.luminosity_distance(z).to_value(u.Glyr),
        "DA_Glyr": cosmo.angular_diameter_distance(z).to_value(u.Glyr),
        "Dlt_Glyr": (cosmo.lookback_time(z) * const.c).to_value(u.Glyr),
        "tL_Gyr": cosmo.lookback_time(z).to_value(u.Gyr),
        "age_Gyr": cosmo.age(z).to_value(u.Gyr),
        "a": 1.0 / (1.0 + z),
        "nu_rel_density": float(cosmo.nu_relative_density(z)),
    }
    out["rows"].append(row)

# maximum de D_A
r = minimize_scalar(lambda z: -cosmo.angular_diameter_distance(z).to_value(u.Mpc),
                    bracket=(1.0, 1.6, 3.0), method="brent", options={"xtol": 1e-10})
out["DA_max"] = {"z": float(r.x), "DA_Glyr": float(-r.fun * (1 * u.Mpc).to_value(u.Glyr))}

# horizons
out["horizons"] = {
    "particle_horizon_Glyr": cosmo.comoving_distance(1e7).to_value(u.Glyr),
    "hubble_sphere_Glyr": (const.c / cosmo.H0).to(u.Glyr).value,
    "ct0_Glyr": (const.c * cosmo.age(0)).to_value(u.Glyr),
}
# horizon des événements : integral_t0^inf c dt/a = D_C(z=-1 ...) -> via quad sur z de -1..0 impossible ;
# on l'obtient par integrale sur a de 1 a inf : c/H0 * int_0^1 da/(a^2 E(1/a-1))
from scipy.integrate import quad
DH = cosmo.hubble_distance.to_value(u.Glyr)
f = lambda a: 1.0 / (a * a * cosmo.efunc(1.0 / a - 1.0))
val, err = quad(f, 1e-8, 1.0, limit=400)
out["horizons"]["event_horizon_Glyr"] = DH * val

# erreur de la formule simplifiée E = sqrt(Om(1+z)^3 + OL) telle qu'affichée dans l'aide F1
def E_simple(z, Om=0.3111, OL=0.6889):
    return np.sqrt(Om * (1 + z) ** 3 + OL)
out["E_simple_vs_full"] = [
    {"z": z, "E_full": float(cosmo.efunc(z)), "E_simple_0.3111": float(E_simple(z)),
     "rel_err_pct": float(100 * (E_simple(z) / cosmo.efunc(z) - 1))}
    for z in Z
]

# distances avec le modele simplifie (sans rayonnement) pour quantifier l'ecart sur D_C, t_L
from astropy.cosmology import FlatLambdaCDM
simple = FlatLambdaCDM(H0=67.66, Om0=0.3111, Tcmb0=0.0)
out["simple_model"] = [
    {"z": z,
     "DC_Glyr": simple.comoving_distance(z).to_value(u.Glyr),
     "DC_rel_err_pct": float(100 * (simple.comoving_distance(z).to_value(u.Glyr) /
                                    cosmo.comoving_distance(z).to_value(u.Glyr) - 1)) if z > 0 else 0.0,
     "age_Gyr": simple.age(z).to_value(u.Gyr),
     "tL_Gyr": simple.lookback_time(z).to_value(u.Gyr)}
    for z in Z
]
out["simple_model_t0_Gyr"] = simple.age(0).to_value(u.Gyr)

# verification Etherington DL = (1+z)^2 DA
out["etherington_max_rel_dev"] = max(
    abs(cosmo.luminosity_distance(z).value / ((1 + z) ** 2 * cosmo.angular_diameter_distance(z).value) - 1)
    for z in Z if z > 0)

# somme lookback + age = t0
out["age_plus_lookback_max_dev_Gyr"] = max(
    abs(cosmo.age(z).to_value(u.Gyr) + cosmo.lookback_time(z).to_value(u.Gyr) - out["t0_Gyr"]) for z in Z)

from pathlib import Path
out_path = Path(__file__).resolve().parent / "ref_astropy.json"
with open(out_path, "w") as fh:
    json.dump(out, fh, indent=1)
print(json.dumps({k: out[k] for k in ("t0_Gyr", "DA_max", "horizons", "etherington_max_rel_dev",
                                      "age_plus_lookback_max_dev_Gyr", "simple_model_t0_Gyr")}, indent=1))
for r in out["rows"]:
    print(f"z={r['z']:>9} DC={r['DC_Glyr']:9.4f} DL={r['DL_Glyr']:11.4f} DA={r['DA_Glyr']:8.4f} "
          f"Dlt={r['Dlt_Glyr']:8.4f} tL={r['tL_Gyr']:8.4f} age={r['age_Gyr']:9.6f} E={r['E']:.6g}")
print("\nE simplifie vs complet :")
for r in out["E_simple_vs_full"]:
    print(f"  z={r['z']:>9}  E_full={r['E_full']:12.5f}  E_simple={r['E_simple_0.3111']:12.5f}  ecart={r['rel_err_pct']:+8.4f} %")
print("\nModele simplifie (Om=0.3111, sans rayonnement) :")
for r in out["simple_model"]:
    print(f"  z={r['z']:>9}  DC={r['DC_Glyr']:9.4f} ({r['DC_rel_err_pct']:+7.4f} %)  age={r['age_Gyr']:.6f} Gyr")
