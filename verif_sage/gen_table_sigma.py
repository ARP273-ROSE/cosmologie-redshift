"""Génère cours/table_sigma.tex et table_sigma_en.tex : incertitudes propagées,
avec et sans la corrélation H0-Om.

Generates the uncertainty tables of both courses.

Usage (depuis la racine du dépôt / from the repository root) :
    .venv/bin/python verif_sage/gen_table_sigma.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "programme"))

from cosmo_core import compute, RHO_H0_OM      # noqa: E402

Z = [0.01, 0.1, 0.5, 1.0, 2.34, 5.0, 10.6, 100.0, 1089.8]


def build(lang: str) -> str:
    def fr(x, d=2):
        s = f"{x:.{d}f}"
        return s.replace(".", "{,}") if lang == "fr" else s

    with_rho = "avec $\\rho$" if lang == "fr" else "with $\\rho$"
    without = "sans $\\rho$" if lang == "fr" else "without $\\rho$"
    out = [r"""\begin{center}
\renewcommand{\arraystretch}{1.2}
\begin{tabular}{rrrrr}
\toprule
& \multicolumn{2}{c}{$\sigma(D_{C})/D_{C}$} & \multicolumn{2}{c}{$\sigma(t_{\text{em}})/t_{\text{em}}$} \\
\cmidrule(lr){2-3}\cmidrule(lr){4-5}
$z$ & %s & %s & %s & %s \\
\midrule""" % (with_rho, without, with_rho, without)]
    for z in Z:
        d = compute(z, with_shoes=False)
        zt = fr(z, 5 if z < 0.1 else (2 if z < 100 else 1))
        out.append(
            f"{zt} & {fr(d['sigma_pct']['comoving'])}~\\% & "
            f"{fr(d['sigma_indep_pct']['comoving'])}~\\% & "
            f"{fr(d['sigma_pct']['age_at_z'])}~\\% & "
            f"{fr(d['sigma_indep_pct']['age_at_z'])}~\\% \\\\")
    out.append(r"""\bottomrule
\end{tabular}
\end{center}""")
    return "\n".join(out) + "\n"


for lang, name in (("fr", "table_sigma.tex"), ("en", "table_sigma_en.tex")):
    import i18n
    i18n.set_language(lang)
    text = build(lang)
    (ROOT / "cours" / name).write_text(text, encoding="utf-8")
    print(f"écrit : cours/{name}")
print(f"rho = {RHO_H0_OM}")
