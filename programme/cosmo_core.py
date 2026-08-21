#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
NOYAU DE CALCUL COSMOLOGIQUE — partagé par la GUI et la version console
================================================================================
Tout le contenu physique du programme est ici ; l'interface graphique
(`redshift_distance_gui.py`) et la version console
(`redshift_distance_calculator.py`) ne font que l'afficher.

Backend : astropy.cosmology (réalisation Planck18, ou LambdaCDM construite).

--------------------------------------------------------------------------
CE QUE Planck18 CONTIENT RÉELLEMENT (cf. cours, ch. « ΛCDM ») :

    E(z)^2 = Or(z)(1+z)^4 + Om0 (1+z)^3 + Ok0 (1+z)^2 + Ode0

    Om0     = 0.30966   <- baryons + matière noire SEULEMENT
    Onu0    = 0.0014397 <- neutrinos, NON relativistes aujourd'hui
    Om0 + Onu0 = 0.31110  <- c'est LE « Omega_m = 0,3111 » du papier Planck 2018
    Ogamma0 = 5.402e-5  <- photons du CMB (fixé par T0 = 2,7255 K)
    Ode0    = 0.68885
    Or(z)   = Ogamma0 * [1 + rho_nu(z)/rho_gamma(z)]  <- dépend de z

La formule simplifiée E(z) = sqrt(Om (1+z)^3 + OL) sous-estime E de 12,8 % à
z = 1089,8 et donne un âge au CMB de 479 kyr au lieu de 372 kyr. Elle reste
exacte à mieux que 0,04 % pour z <= 2,5.

--------------------------------------------------------------------------
INCERTITUDES (ajoutées en août 2026)

Propagation de sigma(H0) = 0,42 km/s/Mpc et sigma(Omega_m) = 0,0056 par
dérivées partielles numériques :

    sigma_G^2 = A^2 sH0^2 + B^2 sOm^2 + 2 rho A B sH0 sOm

Le terme croisé n'est PAS optionnel : H0 et Omega_m sont fortement
anticorrélés dans l'ajustement Planck (dégénérescence géométrique). Le
coefficient rho = -0,976 n'est pas posé arbitrairement, il se déduit de la
contrainte sur omega_m = Omega_m h^2, bien mieux mesurée (0,65 %) que Omega_m
(1,8 %) et h (0,62 %) séparément :

    (s_wm/wm)^2 = (s_Om/Om)^2 + 4 (s_h/h)^2 + 4 rho (s_Om/Om)(s_h/h)

Négliger rho surestimerait l'incertitude d'un facteur ~3. Voir
`verif_sage/verif_incertitudes.sage`.

--------------------------------------------------------------------------
COURBURE

Ok != 0 est accepté. La distance comobile TRANSVERSE diffère alors de la
radiale (cours, éq. 7.4) :

    Ok > 0 : D_M = D_H/sqrt(Ok)  sinh(sqrt(Ok)  D_C/D_H)     (ouvert)
    Ok = 0 : D_M = D_C
    Ok < 0 : D_M = D_H/sqrt(|Ok|) sin(sqrt(|Ok|) D_C/D_H)    (fermé)

et ce sont D_L = (1+z) D_M et D_A = D_M/(1+z) qui s'en déduisent.

--------------------------------------------------------------------------
Vérification : valeurs recalculées indépendamment sous SageMath (mpmath 25
chiffres, intégrale de Fermi-Dirac exacte) — accord à 2e-6 sur les distances,
1,5e-5 sur les âges. Voir les scripts de `verif_sage/`.
================================================================================
"""

from __future__ import annotations

import hashlib
import os
import sys
import tempfile
from pathlib import Path

import numpy as np

# Sortie UTF-8 même sur une console Windows en cp1252 (auto-test ci-dessous).
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

try:
    from astropy.cosmology import Planck18, LambdaCDM
    from astropy import units as u, constants as const
except ImportError as exc:  # message utile plutôt qu'une trace obscure
    raise SystemExit(
        "astropy est requis :  pip install astropy scipy\n"
        f"(erreur d'import d'origine : {exc})"
    )

__all__ = [
    "cosmo", "compute", "curves", "format_distance", "format_time", "fmt_num", "help_context",
    "format_pm", "make_cosmology", "PRESETS", "PARAMS_TXT",
    "C_KMS", "T0_GYR", "D_H_GLYR", "PARTICLE_HORIZON_GLYR", "EVENT_HORIZON_GLYR",
    "Z_DA_MAX", "DA_MAX_GLYR", "H0_PLANCK", "OM_PLANCK", "H0_SHOES",
    "SIGMA_H0", "SIGMA_OM", "RHO_H0_OM", "QUANTITIES",
]

# ============================================================================
# PARAMÈTRES ET CONSTANTES
# ============================================================================

cosmo = Planck18                 # cosmologie de référence, inchangée
C_KMS = const.c.to_value(u.km / u.s)              # 299 792,458 km/s

H0_PLANCK = 67.66                # km/s/Mpc  (Planck 2018)
OM_PLANCK = 0.31110              # Omega_m TOTAL (matière + neutrinos)
H0_SHOES  = 73.04                # km/s/Mpc  (SH0ES, Riess et al. 2022)

SIGMA_H0  = 0.42                 # incertitudes Planck 2018
SIGMA_OM  = 0.0056
RHO_H0_OM = -0.9763              # corrélation, déduite de omega_m (cf. en-tête)

# --- grandeurs de référence, calculées une fois (et vérifiées sous SageMath) --
T0_GYR   = float(cosmo.age(0).to_value(u.Gyr))            # 13,786885 Gyr
D_H_GLYR = float((const.c / cosmo.H0).to_value(u.Glyr))   # 14,451555 G al
PARTICLE_HORIZON_GLYR = 46.2005     # distance comobile à l'horizon des particules
EVENT_HORIZON_GLYR    = 16.5808     # horizon des événements (comobile)
Z_DA_MAX     = 1.59213              # maximum de la distance de diamètre angulaire
DA_MAX_GLYR  = 5.84629

PARAMS_TXT = (
    f"Planck 2018 — H₀ = {H0_PLANCK:g} ± {SIGMA_H0} km/s/Mpc · "
    f"Ωm = {OM_PLANCK:.5f} ± {SIGMA_OM} (dont Ω_ν = {cosmo.Onu0:.5f}) · "
    f"ΩΛ = {cosmo.Ode0:.5f} · Ωγ = {cosmo.Ogamma0:.3e} · T₀ = {cosmo.Tcmb0.value} K"
)

# (étiquette du bouton, z, clé d'infobulle traduite dans i18n.py)
# Ages recomputed in Planck 2018.
PRESETS = [
    ("M 87",         0.00428, "preset_m87"),
    ("3C 273",       0.158,   "preset_3c273"),
    ("z = 1",        1.0,     "preset_z1"),
    ("z = 2.34",     2.34,    "preset_z234"),
    ("ULAS J1120",   7.085,   "preset_ulas"),
    ("GN-z11",       10.6,    "preset_gnz11"),
    ("Reionisation", 20.0,    "preset_reion"),
    ("CMB",          1089.8,  "preset_cmb"),
]


def help_context() -> dict:
    """Valeurs numériques injectées dans les textes d'aide (aucun nombre en dur)."""
    import astropy
    return {
        "astropy_version": astropy.__version__,
        "h0": H0_PLANCK, "h0_shoes": H0_SHOES,
        "sigma_h0": SIGMA_H0, "sigma_om": SIGMA_OM, "rho": RHO_H0_OM,
        "om0": cosmo.Om0, "onu0": cosmo.Onu0, "om_total": OM_PLANCK,
        "ode0": cosmo.Ode0, "ogamma": cosmo.Ogamma0,
        "tcmb": cosmo.Tcmb0.value, "neff": cosmo.Neff,
        "t0": T0_GYR, "d_h": D_H_GLYR,
        "horizon": PARTICLE_HORIZON_GLYR, "event_horizon": EVENT_HORIZON_GLYR,
        "z_da_max": Z_DA_MAX, "da_max": DA_MAX_GLYR,
    }

# grandeurs calculées : clé -> (libellé, unité)
QUANTITIES = {
    "comoving":         ("Distance comobile radiale D_C", "al"),
    "transverse":       ("Distance comobile transverse D_M", "al"),
    "luminosity":       ("Distance de luminosité D_L", "al"),
    "angular_diameter": ("Distance de diamètre angulaire D_A", "al"),
    "lookback":         ("Distance de trajet de la lumière", "al"),
    "lookback_gyr":     ("Lookback time", "Gyr"),
    "age_at_z":         ("Âge de l'univers à z", "Gyr"),
}


# ============================================================================
# CONSTRUCTION D'UNE COSMOLOGIE
# ============================================================================

_cosmo_cache: dict = {}


def make_cosmology(H0: float = H0_PLANCK, Om: float = OM_PLANCK, Ok: float = 0.0):
    """Cosmologie ΛCDM avec le contenu radiatif de Planck 2018.

    `Om` est la densité de matière TOTALE au sens du papier Planck (matière
    noire + baryons + neutrinos). astropy sépare les neutrinos, d'où
    `Om0 = Om - Onu0` — et comme Onu0 dépend de H0 (via la densité critique),
    on itère une fois.

    Si les paramètres sont exactement ceux de Planck 2018 sans courbure, on
    renvoie la réalisation `Planck18` elle-même : les valeurs restent
    rigoureusement identiques aux valeurs de référence vérifiées.
    """
    key = (round(H0, 6), round(Om, 8), round(Ok, 8))
    if key in _cosmo_cache:
        return _cosmo_cache[key]

    if key == (H0_PLANCK, round(OM_PLANCK, 8), 0.0):
        _cosmo_cache[key] = Planck18
        return Planck18

    kw = dict(Tcmb0=cosmo.Tcmb0, Neff=cosmo.Neff, m_nu=cosmo.m_nu, Ob0=cosmo.Ob0)
    onu = cosmo.Onu0
    for _ in range(2):                      # deux passes suffisent largement
        om0 = Om - onu
        c = LambdaCDM(H0=H0, Om0=om0, Ode0=1.0, **kw)   # Ode0 provisoire
        onu = c.Onu0
    om0 = Om - onu
    ode0 = 1.0 - om0 - c.Ogamma0 - onu - Ok
    out = LambdaCDM(H0=H0, Om0=om0, Ode0=ode0, **kw)
    _cosmo_cache[key] = out
    return out


def _raw(model, z: float) -> dict:
    """Grandeurs brutes pour une cosmologie donnée (sans incertitudes)."""
    z = float(z)
    dc = model.comoving_distance(z)
    dm = model.comoving_transverse_distance(z)
    tl = model.lookback_time(z)
    return {
        "comoving":         dc.to_value(u.lyr),
        "transverse":       dm.to_value(u.lyr),
        "luminosity":       model.luminosity_distance(z).to_value(u.lyr),
        "angular_diameter": model.angular_diameter_distance(z).to_value(u.lyr),
        "lookback":         (tl * const.c).to_value(u.lyr),
        "lookback_gyr":     tl.to_value(u.Gyr),
        "age_at_z":         model.age(z).to_value(u.Gyr),
        "E":                float(model.efunc(z)),
        "H_z":              model.H(z).value,
        "a":                1.0 / (1.0 + z),
    }


# ============================================================================
# INCERTITUDES
# ============================================================================

_STEP_H0 = 0.10      # km/s/Mpc, pas des dérivées numériques
_STEP_OM = 0.0015


def _sigmas(z: float, H0: float, Om: float, Ok: float) -> dict:
    """Incertitude 1σ de chaque grandeur, propagée depuis (H0, Ωm) corrélés.

    Dérivées centrées ; le terme croisé 2ρAB σ_H0 σ_Om est indispensable
    (voir l'en-tête du module).
    """
    hp = _raw(make_cosmology(H0 + _STEP_H0, Om, Ok), z)
    hm = _raw(make_cosmology(H0 - _STEP_H0, Om, Ok), z)
    op = _raw(make_cosmology(H0, Om + _STEP_OM, Ok), z)
    om = _raw(make_cosmology(H0, Om - _STEP_OM, Ok), z)

    out, indep = {}, {}
    for k in QUANTITIES:
        A = (hp[k] - hm[k]) / (2 * _STEP_H0)          # dG/dH0
        B = (op[k] - om[k]) / (2 * _STEP_OM)          # dG/dOm
        v_indep = (A * SIGMA_H0) ** 2 + (B * SIGMA_OM) ** 2
        var = v_indep + 2 * RHO_H0_OM * A * B * SIGMA_H0 * SIGMA_OM
        out[k] = float(np.sqrt(max(var, 0.0)))
        indep[k] = float(np.sqrt(max(v_indep, 0.0)))
    return out, indep


# ============================================================================
# API PRINCIPALE
# ============================================================================

def compute(z: float, Ok: float = 0.0, with_sigma: bool = True,
            with_shoes: bool = True) -> dict:
    """Toutes les grandeurs affichées, pour un redshift z.

    Distances en années-lumière, temps en Gyr, vitesses en km/s.
    - `Ok` : courbure spatiale (0 = plat).
    - `with_sigma` : ajoute `sigma` (dict) et `sigma_pct` (dict).
    - `with_shoes` : ajoute `shoes` (mêmes clés, avec H0 = 73,04).
    """
    z = float(z)
    model = make_cosmology(H0_PLANCK, OM_PLANCK, Ok)
    d = _raw(model, z)
    d["z"] = z
    d["Ok"] = float(Ok)
    # âge actuel DU MODÈLE COURANT : t0 change avec la courbure, et le contrôle
    # « t_L + âge = t0 » doit se faire sur celui-là, pas sur la valeur plate.
    d["t0_model"] = float(model.age(0).to_value(u.Gyr))

    # --- trois définitions de la « vitesse de récession » (cf. aide F3) ------
    d["v_cz"] = C_KMS * z                                   # Doppler naïf
    zp1sq = (1.0 + z) ** 2
    d["v_sr"] = C_KMS * (zp1sq - 1.0) / (zp1sq + 1.0)       # Doppler relativiste
    # FLRW : v = H0 * D_propre(t0) = H0 * D_C  (radiale, pas transverse)
    d["v_flrw"] = model.H0.value * model.comoving_distance(z).to_value(u.Mpc)

    if with_sigma:
        sig, sig_indep = _sigmas(z, H0_PLANCK, OM_PLANCK, Ok)
        d["sigma"] = sig
        d["sigma_indep"] = sig_indep       # sans la corrélation : à titre de comparaison
        d["sigma_pct"] = {k: (100.0 * s / d[k] if d[k] else 0.0)
                          for k, s in sig.items()}
        d["sigma_indep_pct"] = {k: (100.0 * s / d[k] if d[k] else 0.0)
                                for k, s in sig_indep.items()}

    if with_shoes:
        sh = _raw(make_cosmology(H0_SHOES, OM_PLANCK, Ok), z)
        sh["ecart_pct"] = {k: (100.0 * (sh[k] / d[k] - 1.0) if d[k] else 0.0)
                           for k in QUANTITIES}
        d["shoes"] = sh

    return d


# ============================================================================
# MISE EN FORME
# ============================================================================

def format_distance(ly: float) -> str:
    """Distance en années-lumière -> chaîne lisible, dans la langue courante."""
    for lim, unit, scale in _dist_units():
        if ly >= lim:
            return f"{fmt_num(ly / scale, 3)} {unit}"
    return f"{fmt_num(ly, 3)} {_dist_units()[-1][1]}"


def format_time(gyr: float) -> str:
    """Durée en Gyr -> chaîne lisible (bascule en Myr puis kyr)."""
    if gyr >= 1.0:
        return f"{fmt_num(gyr, 4, thousands=False)} Gyr"
    if gyr >= 1e-3:
        return f"{fmt_num(gyr * 1e3, 1, thousands=False)} Myr"
    if gyr >= 1e-6:
        return f"{fmt_num(gyr * 1e6, 0, thousands=False)} kyr"
    return f"{fmt_num(gyr * 1e9, 0, thousands=False)} yr"


# Unités selon la langue : « G al » en français, « Gly » en anglais.
_DIST_UNITS_FR = ((1e9, "G al", 1e9), (1e6, "M al", 1e6), (1e3, "k al", 1e3), (0.0, "al", 1.0))
_DIST_UNITS_EN = ((1e9, "Gly", 1e9), (1e6, "Mly", 1e6), (1e3, "kly", 1e3), (0.0, "ly", 1.0))
_TIME_UNITS = ((1.0, "Gyr", 1.0), (1e-3, "Myr", 1e-3), (1e-6, "kyr", 1e-6), (0.0, "yr", 1e-9))

NBSP = " "        # espace fine insécable, séparateur des milliers


def _dist_units():
    from i18n import current_language
    return _DIST_UNITS_EN if current_language() == "en" else _DIST_UNITS_FR


def fmt_num(x: float, dec: int = 3, thousands: bool = True) -> str:
    """Nombre formaté selon la langue : virgule décimale en français."""
    from i18n import current_language
    s = f"{x:,.{dec}f}" if thousands else f"{x:.{dec}f}"
    s = s.replace(",", NBSP)
    if current_language() == "fr":
        s = s.replace(".", ",")
    return s


def _decimals(sigma_scaled: float) -> int:
    """Nombre de décimales : deux chiffres significatifs sur l'incertitude,
    borné à [2, 4] pour rester lisible."""
    if sigma_scaled <= 0:
        return 3
    d = 1 - int(np.floor(np.log10(sigma_scaled)))
    return int(min(max(d, 2), 4))


def format_pm(value: float, sigma: float, kind: str = "distance") -> str:
    """« 18,824 ± 0,033 G al » / « 18.824 ± 0.033 Gly » selon la langue."""
    if not value:
        return format_distance(value) if kind == "distance" else format_time(value)
    table = _dist_units() if kind == "distance" else _TIME_UNITS
    for lim, unit, scale in table:
        if value >= lim:
            break
    v, s = value / scale, (sigma or 0.0) / scale
    if not sigma:
        return (format_distance(value) if kind == "distance" else format_time(value))
    dec = _decimals(s)
    return f"{fmt_num(v, dec)} ± {fmt_num(s, dec)} {unit}"


# ============================================================================
# COURBES POUR LE TRACÉ (avec cache disque)
# ============================================================================

def _cache_dir() -> Path | None:
    """Dossier de cache : à côté du programme, sinon dans le dossier temporaire."""
    for candidate in (Path(__file__).resolve().parent / "cache",
                      Path(tempfile.gettempdir()) / "cosmologie-redshift-cache"):
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            probe = candidate / ".w"
            probe.write_text("ok")
            probe.unlink()
            return candidate
        except OSError:
            continue
    return None


def _cache_key(model, z_grid: np.ndarray) -> str:
    sig = (f"{model.H0.value:.6f}|{model.Om0:.8f}|{model.Ode0:.8f}|{model.Ok0:.8f}|"
           f"{model.Tcmb0.value}|{model.Neff}|{list(model.m_nu.value)}|"
           f"{z_grid[0]:.8g}|{z_grid[-1]:.8g}|{len(z_grid)}|v2")
    return hashlib.sha256(sig.encode()).hexdigest()[:16]


def curves(z_grid: np.ndarray, Ok: float = 0.0, H0: float = H0_PLANCK,
           use_cache: bool = True) -> dict:
    """Les quatre distances (en G al) sur une grille de z, pour le tracé.

    Le calcul (600 points × 4 courbes) prend ~1 s ; il est mis en cache sur
    disque, la relecture est instantanée. Le cache est invalidé
    automatiquement si un paramètre cosmologique ou la grille change.
    """
    model = make_cosmology(H0, OM_PLANCK, Ok)
    z_grid = np.asarray(z_grid, dtype=float)

    path = None
    if use_cache and os.environ.get("COSMO_NO_CACHE") != "1":
        d = _cache_dir()
        if d is not None:
            path = d / f"curves_{_cache_key(model, z_grid)}.npz"
            if path.exists():
                try:
                    with np.load(path) as f:
                        return {k: f[k] for k in
                                ("comoving", "luminosity", "angular_diameter", "lookback")}
                except (OSError, ValueError, KeyError):
                    pass          # cache illisible : on recalcule

    out = {
        "comoving":         model.comoving_distance(z_grid).to_value(u.Glyr),
        "luminosity":       model.luminosity_distance(z_grid).to_value(u.Glyr),
        "angular_diameter": model.angular_diameter_distance(z_grid).to_value(u.Glyr),
        "lookback":         (model.lookback_time(z_grid) * const.c).to_value(u.Glyr),
    }
    if path is not None:
        try:
            np.savez_compressed(path, **out)
        except OSError:
            pass                  # cache non écrit : sans conséquence
    return out


# ============================================================================
# AUTO-TEST
# ============================================================================

if __name__ == "__main__":
    print(PARAMS_TXT)
    print()
    for zz in (0.0, 1.0, 2.34, 1089.8):
        d = compute(zz)
        s = d["sigma"]
        print(f"z={zz:<8} D_C={format_pm(d['comoving'], s['comoving']):>24}"
              f"  ({d['sigma_pct']['comoving']:.2f} %)"
              f"  âge={format_time(d['age_at_z']):>10}"
              f"  SH0ES {d['shoes']['ecart_pct']['comoving']:+.1f} %")
    print()
    for ok in (-0.01, 0.0, 0.01):
        d = compute(2.34, Ok=ok)
        print(f"Ok={ok:+.2f}  D_C={d['comoving']/1e9:8.4f}  D_M={d['transverse']/1e9:8.4f}"
              f"  D_L={d['luminosity']/1e9:8.4f}  D_A={d['angular_diameter']/1e9:7.4f} G al")
    import time
    t0 = time.perf_counter()
    g = np.logspace(-3, np.log10(1500), 600)
    curves(g)
    t1 = time.perf_counter()
    curves(g)
    t2 = time.perf_counter()
    print(f"\ncourbes : {t1 - t0:.2f} s au premier appel, {t2 - t1:.3f} s depuis le cache")
