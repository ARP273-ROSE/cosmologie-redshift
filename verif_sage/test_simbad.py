"""Contrôle de la recherche d'objets dans SIMBAD.
Audit of the SIMBAD object lookup.

Deux parties :
  1. hors ligne — normalisation des noms, variantes engendrées, classement des
     correspondances, motifs de recherche ; rien n'y dépend du réseau ;
  2. en ligne — une série de noms réels, écrits comme on les tape vraiment, dont
     le résultat attendu est connu. Cette partie est ignorée, sans faire échouer
     le contrôle, quand SIMBAD est injoignable.

Usage (depuis la racine du dépôt) :
    .venv/bin/python verif_sage/test_simbad.py
"""
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "programme"))

import simbad
from simbad import SimbadObject

failures = []
skipped = []


def check(cond, msg):
    print(("  OK   " if cond else "  ÉCHEC") + f"  {msg}")
    if not cond:
        failures.append(msg)


# ------------------------------------------------------------ 1. hors ligne
print("\n1. Normalisation des noms")
for raw, expected in (("M 31", "m31"), ("m-31", "m31"), ("  NGC  224 ", "ngc224"),
                      ("GN-z11", "gnz11"), ("Cygnus A", "cygnusa")):
    got = simbad.flatten(raw)
    check(got == expected, f"flatten({raw!r}) -> {got!r}")

print("\n2. Variantes engendrées")
CASES = {
    "m31": "M 31",            # abréviation de catalogue développée
    "ngc224": "NGC 224",      # séparateur rétabli
    "3c273": "3C 273",         # catalogue commençant par un chiffre
    "abell 2218": "ACO 2218",
}
for raw, expected in CASES.items():
    variants = simbad.name_variants(raw)
    check(expected in variants, f"{raw!r} engendre {expected!r} ({len(variants)} formes)")
check(simbad.name_variants("")==[], "un nom vide n'engendre aucune variante")
check(simbad.name_variants("m31")[0] == "m31", "la saisie est toujours essayée en premier")

print("\n3. Classement des correspondances")
m31 = SimbadObject("M  31", "AGN", -0.001, aliases=["NGC  224", "NAME Andromeda Galaxy"])
check(simbad._match_rank("ngc 224", m31) == 0, "un identifiant exact vaut certitude")
check(simbad._match_rank("andromeda", m31) == 2, "un fragment de nom laisse le doute")
check(simbad._match_rank("3c273", m31) == 3, "un nom étranger ne correspond pas")
check(simbad._match_rank("ngc  224", m31) < simbad._match_rank("ngc", m31)
      < simbad._match_rank("3c273", m31),
      "le classement va de l'identifiant exact au nom étranger")

print("\n4. Motifs de recherche par sous-chaîne")
patterns = simbad._like_patterns("gn-z11")
check(all("%" in p[1:-1] for p in patterns) and len(patterns) >= 2,
      f"séparateurs et casse deviennent des jokers : {patterns}")
check(all(p.startswith("%") and p.endswith("%") for p in patterns),
      "les motifs cherchent partout dans l'identifiant")
check(simbad._tap_search("m31", 5) == [],
      "un nom trop court ne déclenche pas la fouille intégrale")

# -------------------------------------------------------------- 2. en ligne
print("\n5. Résolution réelle (SIMBAD)")
EXPECTED = [
    # saisie,          identifiant attendu,   redshift attendu (ou None)
    ("m31",            "M  31",               -0.001),
    ("MESSIER 31",     "M  31",               -0.001),
    ("ngc224",         "M  31",               -0.001),
    ("3c273",          "3C 273",              0.157568),
    ("3C  273",        "3C 273",              0.157568),
    ("m87",            "M  87",               0.0042),
    ("abell2218",      "ACO  2218",           0.1745),
    ("gn-z11",         "[OBV2016] GN-z11",    10.6044),
    ("GNz11",          "Z  49-122",           0.0531),   # homonyme : catalogue GNZ
]
try:
    simbad.resolve("m31", timeout=20)
except simbad.SimbadError as exc:
    skipped.append(f"SIMBAD injoignable ({exc})")
    print(f"  IGNORÉ  SIMBAD est injoignable : {exc}")
else:
    for query, name, z in EXPECTED:
        start = time.time()
        try:
            objects, _ = simbad.resolve(query, timeout=30)
        except simbad.SimbadError as exc:
            skipped.append(f"{query} ({exc})")
            print(f"  IGNORÉ  {query} : {exc}")
            continue
        first = objects[0] if objects else None
        ok = first is not None and first.name == name
        if ok and z is not None and first.redshift is not None:
            ok = abs(first.redshift - z) < 1e-3
        got = f"{first.name} z={first.redshift}" if first else "rien"
        check(ok, f"{query!r:<16} -> {got}  ({len(objects)} candidat(s), "
                  f"{time.time() - start:.1f} s)")

    print("\n6. Cas particuliers")
    objects, _ = simbad.resolve("sombrero", timeout=30)
    check(objects and objects[0].name == "M 104",
          f"un nom commun donne d'abord l'objet attendu ({objects[0].name if objects else '-'})")
    objects, _ = simbad.resolve("andromeda", timeout=40)
    check(objects and objects[0].name == "M  31",
          f"un nom commun reconnu par SIMBAD ne demande pas de choisir "
          f"({len(objects)} candidat(s))")
    objects, _ = simbad.resolve("ulas j1120", timeout=60)
    check(len(objects) > 1,
          f"un nom que SIMBAD ne reconnaît pas fait proposer une liste "
          f"({len(objects)} candidats)")
    objects, _ = simbad.resolve("zzqqxx99", timeout=40)
    check(objects == [], "un nom inexistant ne renvoie rien")

print("\n" + "=" * 70)
if skipped:
    print(f"  {len(skipped)} contrôle(s) ignoré(s) faute de réseau.")
if failures:
    print(f"  {len(failures)} CONTRÔLE(S) EN ÉCHEC")
    for f in failures:
        print("   -", f)
    sys.exit(1)
print("  Tous les contrôles de la recherche SIMBAD passent.")
