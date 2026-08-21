#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
CALCULATEUR DE DISTANCES COSMOLOGIQUES — version console (FR / EN)
COSMOLOGICAL DISTANCE CALCULATOR — console version (FR / EN)
================================================================================
Même contenu physique que l'interface graphique : tout vient de `cosmo_core.py`.
Same physics as the GUI: everything comes from `cosmo_core.py`.

Usage :
    python redshift_distance_calculator.py                      # interactif
    python redshift_distance_calculator.py 2.34                 # calcul direct
    python redshift_distance_calculator.py --table              # presets
    python redshift_distance_calculator.py 2.34 --omega-k 0.01  # univers ouvert
    python redshift_distance_calculator.py 2.34 --no-shoes      # sans comparaison
    python redshift_distance_calculator.py 2.34 --lang en       # in English

Les valeurs sont données avec leur incertitude 1σ, propagée depuis
σ(H₀) = 0,42 et σ(Ωm) = 0,0056 en tenant compte de leur corrélation.
================================================================================
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))   # importable de partout

# La sortie contient des caractères Unicode (•, ₀, ✓, accents). Sur une console
# Windows en cp1252 cela lèverait UnicodeEncodeError : on force UTF-8.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):     # flux redirigé ou non reconfigurable
        pass

from cosmo_core import (
    compute, format_distance, format_time, format_pm, fmt_num, PRESETS, PARAMS_TXT,
    C_KMS, T0_GYR, PARTICLE_HORIZON_GLYR, RHO_H0_OM,
)
from i18n import t, set_language
from updates import __version__, latest_version, is_newer, RELEASES_URL

SEP = "=" * 78


def show(z: float, Ok: float = 0.0, shoes: bool = True) -> None:
    d = compute(z, Ok=Ok, with_shoes=shoes)
    s = d["sigma"]
    curved = abs(Ok) > 1e-12

    def line(label: str, key: str, kind: str = "distance") -> None:
        txt = format_pm(d[key], s[key], kind)
        extra = ""
        if shoes and d[key]:
            v = d["shoes"][key]
            alt = format_distance(v) if kind == "distance" else format_time(v)
            extra = f"   SH0ES {alt} ({d['shoes']['ecart_pct'][key]:+.1f} %)"
        print(f"    • {label:<26}: {txt:>24}{extra}")

    print()
    print(SEP)
    print(t("cli_results_ok", z=z, ok=Ok) if curved else t("cli_results", z=z))
    print(SEP)
    print("\n" + t("cli_distances"))
    line(t("cli_d_comoving"), "comoving")
    if curved:
        line(t("cli_d_transverse"), "transverse")
    line(t("cli_d_luminosity"), "luminosity")
    line(t("cli_d_angular"), "angular_diameter")
    line(t("cli_d_lookback"), "lookback")

    print("\n" + t("cli_quantities"))
    line(t("cli_q_lookback"), "lookback_gyr", "time")
    line(t("cli_q_age"), "age_at_z", "time")
    print(f"    • {t('cli_q_t0'):<26}: {format_time(d['t0_model']):>24}")
    print(f"    • {t('cli_q_scale'):<26}: {fmt_num(d['a'], 5, thousands=False):>24}")
    print(f"    • {t('cli_q_E'):<26}: {fmt_num(d['E'], 4):>24}"
          f"   → H(z) = {fmt_num(d['H_z'], 1)} km/s/Mpc")

    print("\n" + t("cli_velocities"))
    for label, key in ((t("cli_v1"), "v_cz"), (t("cli_v2"), "v_sr"), (t("cli_v3"), "v_flrw")):
        print(f"    • {label:<26}: {fmt_num(d[key], 0):>13} km/s"
              f"  ({fmt_num(d[key] / C_KMS, 3, thousands=False)} c)")

    pc, pi = d["sigma_pct"]["comoving"], d["sigma_indep_pct"]["comoving"]
    if pc:
        print("\n" + t("cli_sigma", pct=pc, pct_indep=pi, rho=RHO_H0_OM))
    somme = d["lookback_gyr"] + d["age_at_z"]
    print(t("cli_check_time", sum=somme, t0=d["t0_model"]))
    if z > 0:
        print(t("cli_check_eth",
                eth=d["luminosity"] / ((1 + z) ** 2 * d["angular_diameter"])))
    print(SEP)


def table() -> None:
    print(SEP)
    print(t("cli_presets"))
    print(SEP)
    print(f"  {t('cli_col_object'):<14}{'z':>10}{'D_C':>12}{'D_L':>12}"
          f"{'D_A':>12}{t('cli_col_age'):>12}")
    print("  " + "-" * 70)
    for name, z, _key in PRESETS:
        d = compute(z, with_sigma=False, with_shoes=False)
        print(f"  {name:<14}{z:>10g}{d['comoving'] / 1e9:>12.4f}"
              f"{d['luminosity'] / 1e9:>12.4f}{d['angular_diameter'] / 1e9:>12.5f}"
              f"{format_time(d['age_at_z']):>12}")
    print("  " + "-" * 70)
    print(t("cli_horizon", ph=PARTICLE_HORIZON_GLYR, ct0=T0_GYR))
    print(SEP)


def main() -> None:
    args = list(sys.argv[1:])

    lang = None
    if "--lang" in args:
        i = args.index("--lang")
        lang = args[i + 1] if i + 1 < len(args) else None
        del args[i:i + 2]
    set_language(lang)

    if any(a in ("--version", "-V") for a in args):
        print(f"cosmologie-redshift {__version__}")
        remote = latest_version()
        if remote and is_newer(remote):
            print(t("update_available", remote=remote, local=__version__, url=RELEASES_URL))
        return

    if any(a in ("--help", "-h") for a in args):
        print(t("cli_usage"))
        return

    shoes = True
    if "--no-shoes" in args:
        shoes = False
        args.remove("--no-shoes")

    Ok = 0.0
    if "--omega-k" in args:
        i = args.index("--omega-k")
        try:
            Ok = float(args[i + 1].replace(",", "."))
        except (IndexError, ValueError):
            sys.exit("--omega-k : nombre attendu / a number is expected (e.g. 0.01)")
        del args[i:i + 2]
        if abs(Ok) > 0.05:
            sys.exit("|Ωk| ≤ 0.05 (Planck: 0.0007 ± 0.0019)")

    if args and args[0] in ("--table", "-t"):
        table()
        return

    if args:                       # calcul direct depuis la ligne de commande
        try:
            z = float(args[0].replace(",", "."))
        except ValueError:
            sys.exit(f"redshift ?  {args[0]!r}\n\n{t('cli_usage')}")
        if z < 0:
            sys.exit(t("cli_negative").strip())
        show(z, Ok=Ok, shoes=shoes)
        return

    print(SEP)
    print(t("cli_title"))
    print(SEP)
    print(f"  {PARAMS_TXT}")
    if abs(Ok) > 1e-12:
        print(t("cli_curvature", ok=Ok))
    print(t("cli_prompt"))

    while True:
        try:
            raw = input("\n  z = ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\n" + t("cli_bye"))
            return

        if raw in ("q", "quit", "exit"):
            print(t("cli_bye"))
            return
        if raw in ("table", "t", "presets"):
            table()
            continue
        if not raw:
            continue

        try:
            z = float(raw.replace(",", "."))
        except ValueError:
            print(t("cli_bad_input"))
            continue

        if z < 0:
            print(t("cli_negative"))
            continue
        if z > 1500:
            print(t("cli_opaque"))

        show(z, Ok=Ok, shoes=shoes)


if __name__ == "__main__":
    main()
