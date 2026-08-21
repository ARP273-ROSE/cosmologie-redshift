"""Génère les tableaux LaTeX des cours (FR et EN) depuis les JSON de référence.

Generates the LaTeX tables of both courses from the reference JSON files.

Produit / produces :
    cours/table_reference.tex     (français : virgule décimale, « G al »)
    cours/table_reference_en.tex  (English: decimal point, « Gly »)

Usage :
    python verif_sage/gen_tables.py            # cherche les JSON dans verif_sage/
    python verif_sage/gen_tables.py <dossier>  # ou dans le dossier indiqué
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "verif_sage"

A = json.load(open(SRC / "ref_astropy.json"))
S = json.load(open(SRC / "verif_sage.json"))


def num(x, dec=4, lang="fr", thousands=True):
    """Nombre au format LaTeX de la langue voulue."""
    s = f"{x:,.{dec}f}" if thousands else f"{x:.{dec}f}"
    s = s.replace(",", r"\,")
    if lang == "fr":
        s = s.replace(".", "{,}")
    return s


def age_str(age, lang):
    if age >= 1:
        return num(age, 4, lang, False) + r"~Gyr"
    if age >= 1e-3:
        return num(age * 1e3, 1, lang, False) + r"~Myr"
    return num(age * 1e6, 0, lang, False) + r"~kyr"


def build(lang: str) -> str:
    unit = "G\\,al" if lang == "fr" else "Gly"
    head_z = "$z$"
    head_age = r"$t_{\text{em}}$"
    out = [r"""\begin{center}
\footnotesize
\renewcommand{\arraystretch}{1.15}
\begin{tabular}{rrrrrrr}
\toprule
%s & $E(z)$ & $D_{C}$ (%s) & $D_{L}$ (%s) & $D_{A}$ (%s)
& $t_{L}$ (Gyr) & %s \\
\midrule""" % (head_z, unit, unit, unit, head_age)]

    for r in A["rows"]:
        z_txt = f"{r['z']:,g}".replace(",", r"\,")
        if lang == "fr":
            z_txt = z_txt.replace(".", "{,}")
        e = num(r["E"], 4, lang) if r["E"] < 1e4 else num(r["E"], 0, lang)
        out.append(f"{z_txt} & {e} & {num(r['DC_Glyr'], 4, lang)} & "
                   f"{num(r['DL_Glyr'], 3, lang)} & {num(r['DA_Glyr'], 5, lang)} & "
                   f"{num(r['tL_Gyr'], 4, lang)} & {age_str(r['age_Gyr'], lang)} \\\\")
    out.append(r"""\bottomrule
\end{tabular}
\end{center}""")

    # écarts maximaux
    keys = [("E", "$E(z)$"), ("DC_Glyr", "$D_{C}$"), ("DL_Glyr", "$D_{L}$"),
            ("DA_Glyr", "$D_{A}$"), ("tL_Gyr", "$t_{L}$"),
            ("age_Gyr", r"$t_{\text{em}}$")]
    worst = {k: 0.0 for k, _ in keys}
    for a, s in zip(A["rows"], S["rows"]):
        for k, _ in keys:
            if a[k]:
                worst[k] = max(worst[k], abs(s[k] / a[k] - 1))
    header = (r"\textbf{Grandeur} & \textbf{écart relatif maximal (16 valeurs de $z$)}"
              if lang == "fr" else
              r"\textbf{Quantity} & \textbf{largest relative difference (16 values of $z$)}")
    out.append(r"""
\begin{center}
\renewcommand{\arraystretch}{1.25}
\begin{tabular}{lr}
\toprule
%s \\
\midrule""" % header)
    for k, lbl in keys:
        mant, exp = f"{worst[k]:.2e}".split("e")
        if lang == "fr":
            mant = mant.replace(".", "{,}")
        out.append(f"{lbl} & ${mant} \\times 10^{{{int(exp)}}}$ \\\\")
    out.append(r"""\bottomrule
\end{tabular}
\end{center}""")
    return "\n".join(out) + "\n"


for lang, name in (("fr", "table_reference.tex"), ("en", "table_reference_en.tex")):
    text = build(lang)
    (ROOT / "cours" / name).write_text(text, encoding="utf-8")
    print(f"écrit : cours/{name}  ({len(text.splitlines())} lignes)")
