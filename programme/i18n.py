#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
BILINGUISME (français / anglais) — libellés de l'interface et de la console
================================================================================
Bilingual support (French / English) for the whole program.

Choix de la langue, par ordre de priorité :
  1. appel explicite  set_language("en")
  2. option de ligne de commande  --lang en   (traitée par les deux scripts)
  3. variable d'environnement  COSMO_LANG=en  (ou fr)
  4. langue du système : variables POSIX (LC_ALL, LC_MESSAGES, LANGUAGE, LANG),
     API Windows (GetUserDefaultUILanguage), réglages macOS (AppleLocale),
     puis le module locale de Python
  5. anglais par défaut

Language selection order: explicit call, --lang, COSMO_LANG, the system
language (POSIX variables, Windows API, macOS preferences, Python locale),
then English by default. A machine set to French gets French; anything else
gets English.

Usage :
    from i18n import t, set_language
    t("window_title")                      -> chaîne traduite
    t("age_vs_t0", t0=13.7869)             -> avec substitution
================================================================================
"""

from __future__ import annotations

import locale
import os
import sys

__all__ = ["t", "set_language", "current_language", "available_languages",
           "detect_system_language", "LANGUAGE_NAMES", "DEFAULT_LANGUAGE"]

LANGUAGE_NAMES = {"fr": "Français", "en": "English"}
DEFAULT_LANGUAGE = "en"          # repli quand la langue du système est autre

_LANG: str | None = None


def available_languages() -> list[str]:
    return list(LANGUAGE_NAMES)


def _normalise(tag: str) -> str:
    """« fr_FR.UTF-8 », « fr-CA », « French_France » -> « fr » (ou "")."""
    tag = (tag or "").strip()
    if not tag or tag.lower() in ("c", "posix", "c.utf-8", "c.utf8"):
        return ""
    tag = tag.split(":")[0].replace("-", "_").split(".")[0].split("@")[0]
    code = tag.split("_")[0].lower()
    if code in LANGUAGE_NAMES:
        return code
    # noms complets renvoyés par certaines API Windows
    return {"french": "fr", "francais": "fr", "français": "fr",
            "english": "en"}.get(code, "")


def _from_env() -> str:
    """Variables POSIX, présentes sous Linux et souvent sous macOS."""
    for var in ("LC_ALL", "LC_MESSAGES", "LANGUAGE", "LANG"):
        code = _normalise(os.environ.get(var, ""))
        if code:
            return code
        # une locale lisible mais d'une autre langue : décision prise, anglais
        raw = (os.environ.get(var) or "").strip()
        if raw and raw.lower() not in ("c", "posix", "c.utf-8", "c.utf8"):
            return DEFAULT_LANGUAGE
    return ""


def _from_windows() -> str:
    """Langue d'affichage de Windows, via l'API du système."""
    if not sys.platform.startswith("win"):
        return ""
    try:
        import ctypes
        lcid = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        tag = locale.windows_locale.get(lcid, "")
        return _normalise(tag) or (DEFAULT_LANGUAGE if tag else "")
    except Exception:
        return ""


def _from_macos() -> str:
    """Réglages de langue de macOS (les variables POSIX y sont souvent vides)."""
    if sys.platform != "darwin":
        return ""
    try:
        import subprocess
        for key in ("AppleLocale", "AppleLanguages"):
            out = subprocess.run(["defaults", "read", "-g", key],
                                 capture_output=True, text=True, timeout=3).stdout
            for token in out.replace("(", " ").replace(")", " ").replace('"', " ").split():
                code = _normalise(token)
                if code:
                    return code
                if len(token) >= 2 and token[:2].isalpha():
                    return DEFAULT_LANGUAGE
    except Exception:
        pass
    return ""


def _from_python_locale() -> str:
    """Dernier recours : le module locale (getdefaultlocale est déprécié)."""
    try:
        tag = locale.getlocale()[0] or ""
    except (ValueError, TypeError):
        tag = ""
    if not tag:
        try:                       # présent jusqu'à Python 3.12 au moins
            tag = (locale.getdefaultlocale()[0] or "")   # noqa: DEP005
        except (ValueError, TypeError, AttributeError):
            tag = ""
    code = _normalise(tag)
    return code or (DEFAULT_LANGUAGE if tag else "")


def detect_system_language() -> str:
    """Langue de la machine, ramenée à « fr » ou « en » (anglais par défaut)."""
    for source in (_from_env, _from_windows, _from_macos, _from_python_locale):
        code = source()
        if code in LANGUAGE_NAMES:
            return code
    return DEFAULT_LANGUAGE


def _detect() -> str:
    code = _normalise(os.environ.get("COSMO_LANG", ""))
    if code:
        return code
    return detect_system_language()


def set_language(lang: str | None) -> str:
    """Fixe la langue ('fr' ou 'en'). None = détection automatique."""
    global _LANG
    if lang:
        lang = lang.strip().lower()[:2]
    _LANG = lang if lang in LANGUAGE_NAMES else _detect()
    return _LANG


def current_language() -> str:
    global _LANG
    if _LANG is None:
        _LANG = _detect()
    return _LANG


def t(key: str, **kw) -> str:
    """Chaîne traduite ; les mots-clés sont substitués par str.format."""
    lang = current_language()
    table = STRINGS.get(lang, STRINGS[DEFAULT_LANGUAGE])
    s = table.get(key)
    if s is None:                      # repli : langue par défaut, puis la clé
        s = STRINGS[DEFAULT_LANGUAGE].get(key, key)
    return s.format(**kw) if kw else s


# ============================================================================
# CHAÎNES
# ============================================================================

STRINGS: dict[str, dict[str, str]] = {

# ---------------------------------------------------------------- FRANÇAIS --
"fr": {
    # --- fenêtre et en-tête
    "window_title":   "Calculateur de distances cosmologiques — Planck 2018",
    "header":         "Calculateur de distances cosmologiques",
    "subtitle":       ("Planck 2018 (TT,TE,EE+lowE+lensing+BAO) — H₀ = {h0:g} km/s/Mpc · "
                       "Ωm+Ων = {om:.5f} · ΩΛ = {ode:.5f} · Ωγ = {ogam:.3e} · t₀ = {t0:.4f} Gyr"),
    "subtitle_tip":   ("Le « Ωm = 0,3111 » du papier Planck se décompose en\n"
                       "Ω_(baryons+CDM) = {om0:.5f} et Ω_ν = {onu:.5f} (neutrinos,\n"
                       "non relativistes aujourd'hui). astropy porte les deux séparément.\n"
                       "Le rayonnement (photons + neutrinos relativistes) est inclus dans E(z) :\n"
                       "voir Aide → « Les quatre distances » (F1)."),

    # --- saisie
    "box_redshift":   "Redshift",
    "z_equals":       "z =",
    "z_tip":          ("Redshift cosmologique = (λ_obs − λ_em) / λ_em.\n"
                       "Sans dimension. Positif pour les objets cosmologiques en expansion.\n"
                       "Plage acceptée : 0 à 1500 (CMB ≈ 1089,8)."),
    "z_spin_tip":     ("Tapez ou utilisez les flèches pour modifier z.\n"
                       "Précision affichée : 5 décimales. Pas par défaut : 0,01."),
    "presets":        "Presets :",
    "presets_tip":    ("Objets-cibles présélectionnés. Voir menu Aide → « Les objets-cibles »\n"
                       "pour les détails de chaque objet."),

    # --- recherche d'un objet dans SIMBAD
    "object_label":   "Objet :",
    "object_tip":     ("Nom d'un objet du ciel, tapé librement : « m31 », « NGC 224 »,\n"
                       "« 3c273 », « Sombrero », « GN-z11 ». La casse, les espaces et les\n"
                       "tirets n'ont pas d'importance. Son redshift est demandé à SIMBAD\n"
                       "(base de données du CDS, Strasbourg) et reporté dans le champ z."),
    "object_hint":    "nom d'objet (m31, 3c273, GN-z11…)",
    "object_search":  "Chercher",
    "object_search_tip": ("Interroge SIMBAD et reporte le redshift trouvé.\n"
                          "La touche Entrée fait la même chose."),
    "object_working": "Recherche dans SIMBAD…",
    "object_found":   "{name} — {otype} — z = {z}",
    "object_none":    "Aucun objet de ce nom dans SIMBAD.",
    "object_offline": "SIMBAD est injoignable ({error}).",
    "object_no_z":    "{name} — {otype} : SIMBAD ne donne pas de redshift pour cet objet.",
    "object_neg_z":   ("{name} : z = {z}, décalage vers le bleu. L'objet s'approche ;\n"
                       "son mouvement propre l'emporte sur l'expansion, et les distances\n"
                       "cosmologiques n'ont pas de sens ici."),
    "object_near":    ("Attention : à z = {z}, le mouvement propre de l'objet dans son\n"
                       "amas domine encore l'expansion. La distance déduite du redshift\n"
                       "reste indicative en deçà de z ≈ 0,03."),
    "object_choose_title": "Plusieurs objets correspondent",
    "object_choose_text":  ("SIMBAD renvoie {n} objets pour « {query} ».\n"
                            "Le plus proche de la demande est en tête."),
    "object_col_name":     "Identifiant",
    "object_col_type":     "Type",
    "object_col_z":        "Redshift",
    "object_unknown_z":    "—",

    # --- modèle
    "box_model":      "Modèle",
    "curvature":      "Courbure Ωk =",
    "curvature_tip":  ("Courbure spatiale. Planck 2018 mesure Ωk = 0,0007 ± 0,0019,\n"
                       "compatible avec 0 : le modèle par défaut impose donc Ωk = 0.\n"
                       "Ωk > 0 : univers ouvert (hyperbolique) — D_M > D_C (sinh).\n"
                       "Ωk < 0 : univers fermé (sphérique)   — D_M < D_C (sin).\n"
                       "Dès que Ωk ≠ 0, la distance comobile TRANSVERSE D_M diffère de la\n"
                       "radiale D_C, et c'est D_M qui entre dans D_L et D_A.\n"
                       "Plage acceptée : −0,05 à +0,05. Ωk est une part de la densité totale,\n"
                       "pas une longueur : au-delà, le modèle n'aurait plus de sens physique."),
    "clamp_curvature": ("Ωk = {asked} n'est pas possible : Ωk n'est pas une longueur, mais la part\n"
                        "de la courbure dans le contenu de l'univers — toutes les parts réunies\n"
                        "font 1. Les observations la donnent quasi nulle (Planck 2018 :\n"
                        "0,0007 ± 0,0019). Le champ va de −0,05 à +0,05, déjà vingt-cinq fois\n"
                        "cette incertitude ; la valeur a été ramenée à {kept}."),
    "clamp_z":         ("z = {asked:g} dépasse la limite du programme. Au-delà de z ≈ 1090,\n"
                        "l'univers est opaque : la lumière n'y circule pas encore librement,\n"
                        "et il n'y a rien à observer plus loin. Valeur ramenée à {kept:g}."),
    "flat_button":    "plat (Ωk = 0)",
    "flat_tip":       "Revenir à l'univers plat de Planck 2018.",
    "compare_shoes":  "comparer avec SH0ES (H₀ = {h0})",
    "shoes_tip":      ("Affiche en regard les mêmes grandeurs calculées avec la mesure locale\n"
                       "de SH0ES (Riess et al. 2022) : H₀ = {h0} ± 1,04 km/s/Mpc,\n"
                       "en désaccord à ~5σ avec Planck (tension de Hubble).\n"
                       "Toutes les distances y sont plus courtes de ~7,4 % (elles varient en 1/H₀).\n"
                       "Voir menu Aide → « Incertitudes et tension de Hubble » (F6)."),

    # --- résultats
    "box_distances":  "Distances cosmologiques",
    "row_comoving":   "Distance comobile",
    "row_transverse": "Distance comobile transverse",
    "row_luminosity": "Distance de luminosité",
    "row_angular":    "Distance de diamètre angulaire",
    "row_lookback":   "Distance de trajet de la lumière",
    "tip_comoving":   ("Distance « immobile » dans le repère qui s'étend avec l'univers.\n"
                       "C'est la distance actuelle (t = t₀) de l'objet.\n"
                       "Sature à {horizon:.2f} G al (horizon des particules)."),
    "tip_transverse": ("D_M : distance comobile mesurée perpendiculairement à la ligne de visée.\n"
                       "Égale à D_C en univers plat ; c'est elle qui entre dans D_L et D_A.\n"
                       "Ωk > 0 : D_M = (D_H/√Ωk)·sinh(√Ωk·D_C/D_H)\n"
                       "Ωk < 0 : D_M = (D_H/√|Ωk|)·sin(√|Ωk|·D_C/D_H)"),
    "tip_luminosity": ("Distance à utiliser pour la photométrie : F = L / (4π D_L²).\n"
                       "Relie magnitude apparente et magnitude absolue. D_L = (1+z) × D_M."),
    "tip_angular":    ("Distance pour les tailles angulaires : θ = taille / D_A.\n"
                       "Maximum de {damax:.3f} G al à z = {zdamax:.4f}, puis décroît.\n"
                       "D_A = D_M / (1+z)."),
    "tip_lookback":   ("Temps de trajet de la lumière × c (lookback time × c).\n"
                       "Valeur « intuitive », bornée par c·t₀ = {t0:.3f} G al ;\n"
                       "physiquement la moins propre à grand z."),
    "shoes_prefix":   "SH0ES : {value}  ({pct:+.1f} %)",

    # --- informations
    "box_info":       "Informations cosmologiques",
    "lbl_lookback":   "Lookback time :",
    "tip_lb":         ("Durée écoulée depuis l'émission de la lumière reçue aujourd'hui.\n"
                       "t_L(z) = ∫₀^z dz' / [(1+z')·H(z')].\n"
                       "Borné par t₀ = {t0:.4f} Gyr."),
    "lbl_age":        "Âge de l'univers à z :",
    "tip_age":        ("Âge de l'univers au moment de l'émission.\n"
                       "t_em(z) = ∫_z^∞ dz' / [(1+z')·H(z')].\n"
                       "Contrôle : lookback + âge = t₀ = {t0:.4f} Gyr."),
    "lbl_scale":      "Facteur d'échelle a = 1/(1+z) :",
    "tip_scale":      ("Facteur d'échelle à l'émission, normalisé à a = 1 aujourd'hui.\n"
                       "L'univers était plus petit d'un facteur (1+z) dans chaque direction."),
    "scale_suffix":   "   (univers {factor:.4g}× plus petit)",
    "lbl_E":          "E(z) = H(z)/H₀ :",
    "tip_E":          ("Taux d'expansion relatif à l'époque de l'émission.\n"
                       "E(z)² = Ωr(z)(1+z)⁴ + Ωm(1+z)³ + ΩΛ (voir Aide F1)."),
    "lbl_v1":         "v récession — Doppler naïf (cz) :",
    "tip_v1":         ("Approximation v = cz : valable seulement pour z << 1.\n"
                       "Dépasse c dès z > 1, ce qui n'a pas de sens physique."),
    "lbl_v2":         "v récession — Doppler relativiste :",
    "tip_v2":         ("v/c = ((1+z)²−1)/((1+z)²+1). Bornée par c mais conceptuellement\n"
                       "inadaptée : elle suppose un espace-temps de Minkowski statique."),
    "lbl_v3":         "v récession — FLRW (H₀ × D_C) :",
    "tip_v3":         ("La seule définition correcte en cosmologie : v = H(t)·D_propre(t).\n"
                       "Non bornée par c — c'est l'espace qui s'étire, rien ne se propage.\n"
                       "Voir menu Aide → « Vitesses de récession » (F3)."),
    "age_t0_suffix":  "   (t₀ = {t0:.4f} Gyr)",

    # --- graphe
    "box_plot":       "Distances en fonction de z",
    "plot_tip":       ("Quatre distances tracées en fonction de z, échelle log-log.\n"
                       "• Confondues à petit z (toutes ≈ cz/H₀).\n"
                       "• Divergent à grand z : la verte (trajet lumière) plafonne à c·t₀,\n"
                       "  la violette (angulaire) redescend après z = 1,59,\n"
                       "  la cyan (comobile) sature à l'horizon, l'orange (luminosité) explose.\n"
                       "Voir menu Aide → « Les quatre distances »."),
    "axis_x":         "Redshift z  (échelle log)",
    "axis_y":         "Distance (G al, échelle log)",
    "curve_comoving": "Comobile",
    "curve_luminosity": "Luminosité",
    "curve_angular":  "Diamètre angulaire",
    "curve_lookback": "Trajet lumière",
    "curve_shoes":    "{name} (SH0ES)",
    "marker_damax":   "max D_A",
    "marker_horizon": "horizon",

    # --- menus
    "menu_help":      "&Aide",
    "menu_language":  "&Langue",
    "act_distances":  "Les quatre &distances cosmologiques",
    "act_planck":     "Comprendre &Planck 2018",
    "act_recession":  "Vitesses de &récession superluminiques",
    "act_presets":    "Les &objets-cibles présélectionnés",
    "act_simbad":     "Chercher un objet par son &nom",
    "act_verif":      "&Vérification des calculs (SageMath)",
    "act_sigma":      "&Incertitudes, courbure et tension de Hubble",
    "act_about":      "À &propos",
    "title_distances": "Les quatre distances cosmologiques",
    "title_planck":   "Cosmologie Planck 2018",
    "title_recession": "Vitesses de récession",
    "title_presets":  "Objets-cibles présélectionnés",
    "title_simbad":   "Chercher un objet par son nom",
    "title_verif":    "Vérification des calculs",
    "title_sigma":    "Incertitudes, courbure et tension de Hubble",
    "title_about":    "À propos",
    "lang_restart":   ("La langue a été changée. Certains libellés ne seront\n"
                       "entièrement mis à jour qu'au prochain démarrage."),

    # --- barre d'état
    "ready":          "Prêt — modifiez z ou cliquez sur un preset",
    "status":         ("z = {z:g}   ·   t_L + âge = {sum:.6f} Gyr (écart {dev:.2f} µGyr)"
                       "   ·   Etherington = {eth:.12f}"
                       "   ·   σ(D_C) = {pct:.2f} % ({pct_indep:.2f} % sans la corrélation H₀–Ωm)"),
    "status_ok":      "   ·   Ωk = {ok:+.4f}",

    # --- console
    "cli_title":      "      CALCULATEUR DE DISTANCES COSMOLOGIQUES",
    "cli_results":    "  RÉSULTATS POUR z = {z:g}",
    "cli_results_ok": "  RÉSULTATS POUR z = {z:g}   (Ωk = {ok:+.4f})",
    "cli_distances":  "  Distances cosmologiques      (valeur ± 1σ propagée de H₀ et Ωm)",
    "cli_quantities": "  Grandeurs cosmologiques",
    "cli_velocities": "  Vitesse de récession (trois définitions — cf. cours ch. « vitesses »)",
    "cli_d_comoving": "Comobile radiale D_C",
    "cli_d_transverse": "Comobile transverse D_M",
    "cli_d_luminosity": "Luminosité D_L",
    "cli_d_angular":  "Diamètre angulaire D_A",
    "cli_d_lookback": "Trajet de la lumière",
    "cli_q_lookback": "Lookback time",
    "cli_q_age":      "Âge de l'univers à z",
    "cli_q_t0":       "Âge actuel t₀",
    "cli_q_scale":    "Facteur d'échelle a",
    "cli_q_E":        "E(z) = H(z)/H₀",
    "cli_v1":         "Doppler naïf  v = cz",
    "cli_v2":         "Doppler relativiste",
    "cli_v3":         "FLRW  v = H₀ × D_C  ✓",
    "cli_sigma":      ("  Incertitude sur D_C : ±{pct:.2f} %  "
                       "(±{pct_indep:.2f} % si l'on ignore la corrélation H₀–Ωm, ρ = {rho})"),
    "cli_check_time": "  Contrôle : t_L + âge = {sum:.6f} Gyr  (t₀ = {t0:.6f} Gyr)",
    "cli_check_eth":  "  Contrôle : Etherington D_L/[(1+z)²D_A] = {eth:.12f}",
    "cli_presets":    "  PRESETS — cosmologie Planck 2018",
    "cli_col_object": "objet",
    "cli_col_age":    "âge à z",
    "cli_horizon":    "  horizon des particules : {ph:.3f} G al   ·   c·t₀ = {ct0:.3f} G al",
    "cli_prompt":     ("  Tapez un redshift, ou le nom d'un objet à chercher dans SIMBAD.\n"
                       "  'table' donne la liste des presets, 'q' quitte."),
    "cli_object_searching": "  Recherche de « {query} » dans SIMBAD…",
    "cli_object_choose":    "  {n} objets correspondent. Indiquez un numéro, ou Entrée pour renoncer :",
    "cli_object_prompt":    "  n° = ",
    "cli_curvature":  "  Courbure imposée : Ωk = {ok:+.4f}",
    "cli_bye":        "  Au revoir.",
    "cli_bad_input":  "  Entrée invalide : tapez un nombre, un nom d'objet, 'table' ou 'q'.",
    "cli_negative":   "  Le redshift ne peut pas être négatif.",
    "cli_opaque":     ("  Au-delà de z = 1500 l'univers est opaque (avant la recombinaison) :\n"
                       "  les « distances » n'y sont plus observables. Calcul quand même effectué."),
    "cli_usage": """usage : redshift_distance_calculator.py [z] [options]

  z                   redshift (interactif si absent)
  --table, -t         table des huit presets
  --omega-k VALEUR    courbure spatiale Ωk (défaut 0 = univers plat)
  --no-shoes          ne pas afficher la comparaison SH0ES
  --object NOM, -o    chercher le redshift d'un objet dans SIMBAD
  --lang fr|en        langue d'affichage
  --help, -h          cette aide
""",

    # --- mises à jour
    "act_update":     "Vérifier les &mises à jour",
    "update_title":   "Mises à jour",
    "update_checking": "Vérification en cours…",
    "update_current": "Version {local} — c'est la plus récente.",
    "update_available": ("Version {remote} disponible (vous utilisez la {local}).\n\n"
                         "Téléchargement : {url}"),
    "update_offline": ("Impossible de contacter GitHub.\n"
                       "Vérifiez la connexion, ou consultez {url}"),
    "update_banner":  "Version {remote} disponible — voir Aide → Vérifier les mises à jour",
    "about_version":  "Version {local}",

    # --- infobulles des presets
    "preset_m87":     ("Galaxie elliptique géante de l'amas de la Vierge.\n"
                       "Trou noir supermassif imagé par l'Event Horizon Telescope (2019).\n"
                       "z donne D_C = 62 M al, mais les mesures directes donnent ~55 M al :\n"
                       "l'écart est dû à la vitesse propre de M 87 dans l'amas."),
    "preset_3c273":   ("Premier quasar identifié comme tel (Maarten Schmidt, 1963).\n"
                       "Quasar le plus brillant vu de la Terre (mv ≈ 12,9).\n"
                       "D_C = 2,20 G al mais D_L = 2,54 G al : l'écart devient visible."),
    "preset_z1":      ("Repère pédagogique. L'univers avait 5,85 Gyr et était deux fois\n"
                       "plus petit qu'aujourd'hui (a = 0,5)."),
    "preset_z234":    ("« Cosmic noon » : pic d'activité quasar et de formation stellaire.\n"
                       "Tranche-clé des relevés BAO (BOSS / eBOSS / forêt Lyman-α)."),
    "preset_ulas":    ("Quasar découvert en 2011 (Mortlock et al.). Trou noir 2×10⁹ M☉.\n"
                       "Univers âgé de 749 Myr en Planck 2018 (l'article annonçait 770 Myr,\n"
                       "calculés en cosmologie WMAP7)."),
    "preset_gnz11":   ("L'une des galaxies les plus lointaines confirmées (JWST 2022/23).\n"
                       "L'univers avait 435 Myr en Planck 2018."),
    "preset_reion":   ("Pas un objet mais une époque : les premières étoiles ré-ionisent\n"
                       "l'hydrogène intergalactique neutre. Plage typique 6 < z < 30."),
    "preset_cmb":     ("Surface de dernière diffusion. Lumière la plus ancienne captable,\n"
                       "émise quand l'univers avait 372 000 ans et devint transparent."),
},

# ----------------------------------------------------------------- ENGLISH --
"en": {
    "window_title":   "Cosmological Distance Calculator — Planck 2018",
    "header":         "Cosmological Distance Calculator",
    "subtitle":       ("Planck 2018 (TT,TE,EE+lowE+lensing+BAO) — H₀ = {h0:g} km/s/Mpc · "
                       "Ωm+Ων = {om:.5f} · ΩΛ = {ode:.5f} · Ωγ = {ogam:.3e} · t₀ = {t0:.4f} Gyr"),
    "subtitle_tip":   ("The « Ωm = 0.3111 » of the Planck paper splits into\n"
                       "Ω_(baryons+CDM) = {om0:.5f} and Ω_ν = {onu:.5f} (neutrinos, which are\n"
                       "non-relativistic today). astropy keeps the two separate.\n"
                       "Radiation (photons + relativistic neutrinos) is included in E(z):\n"
                       "see Help → « The four distances » (F1)."),

    "box_redshift":   "Redshift",
    "z_equals":       "z =",
    "z_tip":          ("Cosmological redshift = (λ_obs − λ_em) / λ_em.\n"
                       "Dimensionless. Positive for cosmological objects in an expanding universe.\n"
                       "Accepted range: 0 to 1500 (CMB ≈ 1089.8)."),
    "z_spin_tip":     ("Type a value or use the arrows to change z.\n"
                       "Displayed precision: 5 decimals. Default step: 0.01."),
    "presets":        "Presets:",
    "presets_tip":    ("Preselected targets. See Help → « The preselected targets »\n"
                       "for details on each one."),

    # --- SIMBAD object lookup
    "object_label":   "Object:",
    "object_tip":     ("Name of a sky object, typed freely: \"m31\", \"NGC 224\",\n"
                       "\"3c273\", \"Sombrero\", \"GN-z11\". Case, spaces and hyphens do not\n"
                       "matter. Its redshift is requested from SIMBAD (the CDS database\n"
                       "in Strasbourg) and copied into the z field."),
    "object_hint":    "object name (m31, 3c273, GN-z11…)",
    "object_search":  "Look up",
    "object_search_tip": ("Queries SIMBAD and copies the redshift it returns.\n"
                          "Pressing Enter does the same."),
    "object_working": "Querying SIMBAD…",
    "object_found":   "{name} — {otype} — z = {z}",
    "object_none":    "No object of that name in SIMBAD.",
    "object_offline": "SIMBAD cannot be reached ({error}).",
    "object_no_z":    "{name} — {otype}: SIMBAD lists no redshift for this object.",
    "object_neg_z":   ("{name}: z = {z}, a blueshift. The object is approaching; its own\n"
                       "motion outweighs the expansion, and cosmological distances are\n"
                       "meaningless here."),
    "object_near":    ("Careful: at z = {z} the object's own motion inside its cluster\n"
                       "still dominates the expansion. A distance derived from redshift\n"
                       "remains indicative below z ≈ 0.03."),
    "object_choose_title": "Several objects match",
    "object_choose_text":  ("SIMBAD returns {n} objects for \"{query}\".\n"
                            "The closest match to the request comes first."),
    "object_col_name":     "Identifier",
    "object_col_type":     "Type",
    "object_col_z":        "Redshift",
    "object_unknown_z":    "—",

    "box_model":      "Model",
    "curvature":      "Curvature Ωk =",
    "curvature_tip":  ("Spatial curvature. Planck 2018 measures Ωk = 0.0007 ± 0.0019,\n"
                       "consistent with 0, hence the default flat model Ωk = 0.\n"
                       "Ωk > 0: open (hyperbolic) universe — D_M > D_C (sinh).\n"
                       "Ωk < 0: closed (spherical) universe — D_M < D_C (sin).\n"
                       "As soon as Ωk ≠ 0, the TRANSVERSE comoving distance D_M differs from\n"
                       "the radial D_C, and it is D_M that enters D_L and D_A.\n"
                       "Accepted range: −0.05 to +0.05. Ωk is a share of the total density, not\n"
                       "a length: beyond that the model would have no physical meaning."),
    "clamp_curvature": ("Ωk = {asked} is not possible: Ωk is not a length but the share of\n"
                        "curvature in the content of the universe — all the shares together\n"
                        "add up to 1. Observations make it nearly zero (Planck 2018:\n"
                        "0.0007 ± 0.0019). The field runs from −0.05 to +0.05, already\n"
                        "twenty-five times that uncertainty; the value was brought to {kept}."),
    "clamp_z":         ("z = {asked:g} is beyond the program's limit. Past z ≈ 1090 the\n"
                        "universe is opaque: light does not travel freely yet, and there is\n"
                        "nothing to observe further out. Value brought to {kept:g}."),
    "flat_button":    "flat (Ωk = 0)",
    "flat_tip":       "Back to the flat Planck 2018 universe.",
    "compare_shoes":  "compare with SH0ES (H₀ = {h0})",
    "shoes_tip":      ("Shows alongside the same quantities computed with the local SH0ES\n"
                       "measurement (Riess et al. 2022): H₀ = {h0} ± 1.04 km/s/Mpc,\n"
                       "in ~5σ disagreement with Planck (Hubble tension).\n"
                       "All distances shrink by ~7.4 % (they scale as 1/H₀).\n"
                       "See Help → « Uncertainties and the Hubble tension » (F6)."),

    "box_distances":  "Cosmological distances",
    "row_comoving":   "Comoving distance",
    "row_transverse": "Transverse comoving distance",
    "row_luminosity": "Luminosity distance",
    "row_angular":    "Angular diameter distance",
    "row_lookback":   "Light-travel distance",
    "tip_comoving":   ("Distance that stays fixed in the frame expanding with the universe.\n"
                       "This is the object's present-day distance (t = t₀).\n"
                       "Saturates at {horizon:.2f} Gly (particle horizon)."),
    "tip_transverse": ("D_M: comoving distance measured perpendicular to the line of sight.\n"
                       "Equal to D_C in a flat universe; it is the one entering D_L and D_A.\n"
                       "Ωk > 0: D_M = (D_H/√Ωk)·sinh(√Ωk·D_C/D_H)\n"
                       "Ωk < 0: D_M = (D_H/√|Ωk|)·sin(√|Ωk|·D_C/D_H)"),
    "tip_luminosity": ("The distance to use for photometry: F = L / (4π D_L²).\n"
                       "Links apparent and absolute magnitude. D_L = (1+z) × D_M."),
    "tip_angular":    ("The distance for angular sizes: θ = size / D_A.\n"
                       "Peaks at {damax:.3f} Gly for z = {zdamax:.4f}, then decreases.\n"
                       "D_A = D_M / (1+z)."),
    "tip_lookback":   ("Light travel time × c (lookback time × c).\n"
                       "The « intuitive » value, bounded by c·t₀ = {t0:.3f} Gly;\n"
                       "physically the least meaningful one at high z."),
    "shoes_prefix":   "SH0ES: {value}  ({pct:+.1f} %)",

    "box_info":       "Cosmological quantities",
    "lbl_lookback":   "Lookback time:",
    "tip_lb":         ("Time elapsed since the light received today was emitted.\n"
                       "t_L(z) = ∫₀^z dz' / [(1+z')·H(z')].\n"
                       "Bounded by t₀ = {t0:.4f} Gyr."),
    "lbl_age":        "Age of the universe at z:",
    "tip_age":        ("Age of the universe when the light was emitted.\n"
                       "t_em(z) = ∫_z^∞ dz' / [(1+z')·H(z')].\n"
                       "Check: lookback + age = t₀ = {t0:.4f} Gyr."),
    "lbl_scale":      "Scale factor a = 1/(1+z):",
    "tip_scale":      ("Scale factor at emission, normalised to a = 1 today.\n"
                       "The universe was smaller by a factor (1+z) in every direction."),
    "scale_suffix":   "   (universe {factor:.4g}× smaller)",
    "lbl_E":          "E(z) = H(z)/H₀:",
    "tip_E":          ("Expansion rate at emission, relative to today.\n"
                       "E(z)² = Ωr(z)(1+z)⁴ + Ωm(1+z)³ + ΩΛ (see Help F1)."),
    "lbl_v1":         "recession v — naive Doppler (cz):",
    "tip_v1":         ("The approximation v = cz: valid only for z << 1.\n"
                       "Exceeds c as soon as z > 1, which is physically meaningless."),
    "lbl_v2":         "recession v — relativistic Doppler:",
    "tip_v2":         ("v/c = ((1+z)²−1)/((1+z)²+1). Bounded by c but conceptually\n"
                       "inappropriate: it assumes a static Minkowski spacetime."),
    "lbl_v3":         "recession v — FLRW (H₀ × D_C):",
    "tip_v3":         ("The only correct definition in cosmology: v = H(t)·D_proper(t).\n"
                       "Not bounded by c — space stretches, nothing propagates.\n"
                       "See Help → « Recession velocities » (F3)."),
    "age_t0_suffix":  "   (t₀ = {t0:.4f} Gyr)",

    "box_plot":       "Distances as a function of z",
    "plot_tip":       ("The four distances against z, log-log scale.\n"
                       "• Indistinguishable at low z (all ≈ cz/H₀).\n"
                       "• They diverge at high z: green (light travel) saturates at c·t₀,\n"
                       "  purple (angular) turns over after z = 1.59,\n"
                       "  cyan (comoving) reaches the horizon, orange (luminosity) blows up.\n"
                       "See Help → « The four distances »."),
    "axis_x":         "Redshift z  (log scale)",
    "axis_y":         "Distance (Gly, log scale)",
    "curve_comoving": "Comoving",
    "curve_luminosity": "Luminosity",
    "curve_angular":  "Angular diameter",
    "curve_lookback": "Light travel",
    "curve_shoes":    "{name} (SH0ES)",
    "marker_damax":   "max D_A",
    "marker_horizon": "horizon",

    "menu_help":      "&Help",
    "menu_language":  "&Language",
    "act_distances":  "The four cosmological &distances",
    "act_planck":     "Understanding &Planck 2018",
    "act_recession":  "Superluminal &recession velocities",
    "act_presets":    "The preselected &targets",
    "act_simbad":     "Looking up an object by &name",
    "act_verif":      "&Verification of the calculations (SageMath)",
    "act_sigma":      "&Uncertainties, curvature and the Hubble tension",
    "act_about":      "&About",
    "title_distances": "The four cosmological distances",
    "title_planck":   "Planck 2018 cosmology",
    "title_recession": "Recession velocities",
    "title_presets":  "Preselected targets",
    "title_simbad":   "Looking up an object by name",
    "title_verif":    "Verification of the calculations",
    "title_sigma":    "Uncertainties, curvature and the Hubble tension",
    "title_about":    "About",
    "lang_restart":   ("The language has been changed. A few labels will only be\n"
                       "fully updated on the next start."),

    "ready":          "Ready — change z or click a preset",
    "status":         ("z = {z:g}   ·   t_L + age = {sum:.6f} Gyr (deviation {dev:.2f} µGyr)"
                       "   ·   Etherington = {eth:.12f}"
                       "   ·   σ(D_C) = {pct:.2f} % ({pct_indep:.2f} % without the H₀–Ωm correlation)"),
    "status_ok":      "   ·   Ωk = {ok:+.4f}",

    "cli_title":      "      COSMOLOGICAL DISTANCE CALCULATOR",
    "cli_results":    "  RESULTS FOR z = {z:g}",
    "cli_results_ok": "  RESULTS FOR z = {z:g}   (Ωk = {ok:+.4f})",
    "cli_distances":  "  Cosmological distances       (value ± 1σ propagated from H₀ and Ωm)",
    "cli_quantities": "  Cosmological quantities",
    "cli_velocities": "  Recession velocity (three definitions — see course, « velocities »)",
    "cli_d_comoving": "Radial comoving D_C",
    "cli_d_transverse": "Transverse comoving D_M",
    "cli_d_luminosity": "Luminosity D_L",
    "cli_d_angular":  "Angular diameter D_A",
    "cli_d_lookback": "Light travel",
    "cli_q_lookback": "Lookback time",
    "cli_q_age":      "Age of the universe at z",
    "cli_q_t0":       "Present age t₀",
    "cli_q_scale":    "Scale factor a",
    "cli_q_E":        "E(z) = H(z)/H₀",
    "cli_v1":         "Naive Doppler  v = cz",
    "cli_v2":         "Relativistic Doppler",
    "cli_v3":         "FLRW  v = H₀ × D_C  ✓",
    "cli_sigma":      ("  Uncertainty on D_C: ±{pct:.2f} %  "
                       "(±{pct_indep:.2f} % if the H₀–Ωm correlation is ignored, ρ = {rho})"),
    "cli_check_time": "  Check: t_L + age = {sum:.6f} Gyr  (t₀ = {t0:.6f} Gyr)",
    "cli_check_eth":  "  Check: Etherington D_L/[(1+z)²D_A] = {eth:.12f}",
    "cli_presets":    "  PRESETS — Planck 2018 cosmology",
    "cli_col_object": "object",
    "cli_col_age":    "age at z",
    "cli_horizon":    "  particle horizon: {ph:.3f} Gly   ·   c·t₀ = {ct0:.3f} Gly",
    "cli_prompt":     ("  Type a redshift, or the name of an object to look up in SIMBAD.\n"
                       "  'table' lists the presets, 'q' quits."),
    "cli_object_searching": "  Looking up \"{query}\" in SIMBAD…",
    "cli_object_choose":    "  {n} objects match. Give a number, or press Enter to give up:",
    "cli_object_prompt":    "  no. = ",
    "cli_curvature":  "  Imposed curvature: Ωk = {ok:+.4f}",
    "cli_bye":        "  Goodbye.",
    "cli_bad_input":  "  Invalid input: type a number, an object name, 'table' or 'q'.",
    "cli_negative":   "  The redshift cannot be negative.",
    "cli_opaque":     ("  Beyond z = 1500 the universe is opaque (before recombination):\n"
                       "  « distances » there are not observable. Computing anyway."),
    "cli_usage": """usage: redshift_distance_calculator.py [z] [options]

  z                   redshift (interactive if omitted)
  --table, -t         table of the eight presets
  --omega-k VALUE     spatial curvature Ωk (default 0 = flat universe)
  --no-shoes          do not show the SH0ES comparison
  --object NAME, -o   look up an object's redshift in SIMBAD
  --lang fr|en        display language
  --help, -h          this help
""",

    # --- updates
    "act_update":     "Check for &updates",
    "update_title":   "Updates",
    "update_checking": "Checking…",
    "update_current": "Version {local} — this is the latest one.",
    "update_available": ("Version {remote} is available (this is {local}).\n\n"
                         "Download: {url}"),
    "update_offline": ("GitHub could not be reached.\n"
                       "Check the connection, or see {url}"),
    "update_banner":  "Version {remote} available — see Help → Check for updates",
    "about_version":  "Version {local}",

    # --- preset tooltips
    "preset_m87":     ("Giant elliptical galaxy in the Virgo cluster.\n"
                       "Supermassive black hole imaged by the Event Horizon Telescope (2019).\n"
                       "z gives D_C = 62 Mly, while direct measurements give ~55 Mly:\n"
                       "the difference is M 87's peculiar velocity within the cluster."),
    "preset_3c273":   ("The first object identified as a quasar (Maarten Schmidt, 1963).\n"
                       "Brightest quasar seen from Earth (mv ≈ 12.9).\n"
                       "D_C = 2.20 Gly but D_L = 2.54 Gly: the difference becomes visible."),
    "preset_z1":      ("A teaching landmark. The universe was 5.85 Gyr old and half\n"
                       "its present size (a = 0.5)."),
    "preset_z234":    ("« Cosmic noon »: peak of quasar activity and star formation.\n"
                       "A key slice of the BAO surveys (BOSS / eBOSS / Lyman-α forest)."),
    "preset_ulas":    ("Quasar discovered in 2011 (Mortlock et al.). 2×10⁹ M☉ black hole.\n"
                       "The universe was 749 Myr old in Planck 2018 (the paper quoted\n"
                       "770 Myr, computed in WMAP7 cosmology)."),
    "preset_gnz11":   ("One of the most distant confirmed galaxies (JWST 2022/23).\n"
                       "The universe was 435 Myr old in Planck 2018."),
    "preset_reion":   ("Not an object but an epoch: the first stars reionise the neutral\n"
                       "intergalactic hydrogen. Typical range 6 < z < 30."),
    "preset_cmb":     ("The last-scattering surface. The oldest light we can detect,\n"
                       "emitted when the universe was 372 000 years old and became transparent."),
},
}
