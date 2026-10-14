#!/usr/bin/env python3
"""Compile les manuels PDF (format maison) depuis MANUEL.md et MANUAL.md.

    python3 docs/src/compiler.py          (depuis la racine du dépôt)

Chaîne : pandoc -> lualatex avec le préambule docs/src/entete.tex. Sorties :
docs/manuel-fr.pdf et docs/manuel-en.pdf, livrés avec le programme et ouverts
par Aide -> Manuel (PDF). Les captures (docs/captures/) sont refaites avant par
docs/captures.py. Après compilation, aucun fichier temporaire ne reste.

Contrôles après chaque PDF : aucun « $ » orphelin dans le texte extrait
(signe d'une formule mal lue), et aucun glyphe manquant signalé par LaTeX.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
SRC = Path(__file__).resolve().parent
# pandoc et lualatex doivent être dans le PATH ; à défaut, TEXLIVE_BIN donne
# le dossier des binaires de TeX Live.
if os.environ.get("TEXLIVE_BIN"):
    os.environ["PATH"] = os.environ["TEXLIVE_BIN"] + os.pathsep + os.environ.get("PATH", "")

MANUELS = {
    "fr": ("MANUEL.md", "Manuel d'utilisation", "Calculateur de distances cosmologiques",
           "Logiciel libre (licence MIT) \\textbar{} github.com/ARP273-ROSE/cosmologie-redshift",
           "french"),
    "en": ("MANUAL.md", "User manual", "Cosmological Distance Calculator",
           "Free software (MIT licence) \\textbar{} github.com/ARP273-ROSE/cosmologie-redshift",
           "english"),
}
MOIS_FR = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
           "septembre", "octobre", "novembre", "décembre"]


def compiler(langue: str) -> Path:
    source, titre, app, pied, babel = MANUELS[langue]
    version = (RACINE / "VERSION").read_text(encoding="utf-8").strip()
    j = date.today()
    quand = (f"Version {version} — {j.day} {MOIS_FR[j.month - 1]} {j.year}" if langue == "fr"
             else f"Version {version} — {j:%B} {j.day}, {j.year}")
    texte = (RACINE / source).read_text(encoding="utf-8")
    # La première ligne (titre) et le renvoi vers l'autre langue sont repris
    # par la page de garde : on les retire du corps.
    texte = re.sub(r"\A# .*\n+(\*\[[^\]]*\]\([^)]*\)\*\n+)?", "", texte)
    sortie = RACINE / "docs" / f"manuel-{langue}.pdf"
    with tempfile.TemporaryDirectory() as tmp:
        md = Path(tmp) / "manuel.md"
        md.write_text(texte, encoding="utf-8")
        entete = Path(tmp) / "entete.tex"
        entete.write_text(
            f"\\newcommand{{\\MANUELAPP}}{{{app}}}\n"
            f"\\newcommand{{\\MANUELTITRE}}{{{titre}}}\n"
            f"\\newcommand{{\\MANUELPIED}}{{{pied}}}\n"
            f"\\newcommand{{\\MANUELLOGO}}{{{(RACINE / 'programme' / 'logo_512.png').as_posix()}}}\n"
            + (SRC / "entete.tex").read_text(encoding="utf-8"), encoding="utf-8")
        cmd = ["pandoc", str(md), "-o", str(Path(tmp) / "manuel.pdf"),
               "--from", "markdown-yaml_metadata_block-implicit_figures+implicit_figures",
               "--pdf-engine=lualatex", "--toc", "--toc-depth=2", "--no-highlight",
               "--resource-path", str(RACINE), "-H", str(entete),
               "-M", f"title={titre}", "-M", f"date={quand}",
               "-V", "documentclass=article", "-V", "fontsize=11pt",
               "-V", "geometry:a4paper,margin=2cm,headheight=26pt,headsep=10pt",
               "-V", "colorlinks=true", "-V", "linkcolor=sky", "-V", "urlcolor=sky",
               "-V", f"lang={'fr' if langue == 'fr' else 'en'}",
               "--pdf-engine-opt=-interaction=nonstopmode"]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        if r.returncode != 0:
            print(r.stderr[-4000:])
            raise SystemExit(f"échec de la compilation ({langue})")
        manquants = re.findall(r"Missing character: There is no (.) ", r.stderr)
        if manquants:
            raise SystemExit(f"glyphes manquants ({langue}) : {sorted(set(manquants))}")
        shutil.copy2(Path(tmp) / "manuel.pdf", sortie)
    extrait = subprocess.run(["pdftotext", str(sortie), "-"], capture_output=True,
                             text=True).stdout if shutil.which("pdftotext") else ""
    if "$" in extrait:
        print(f"  attention : « $ » dans le texte de {sortie.name}")
    pages = subprocess.run(["pdfinfo", str(sortie)], capture_output=True, text=True).stdout \
        if shutil.which("pdfinfo") else ""
    n = re.search(r"Pages:\s+(\d+)", pages)
    print(f"  {sortie.relative_to(RACINE)} : {n.group(1) if n else '?'} pages")
    return sortie


if __name__ == "__main__":
    for lg in (sys.argv[1:] or ["fr", "en"]):
        compiler(lg)
