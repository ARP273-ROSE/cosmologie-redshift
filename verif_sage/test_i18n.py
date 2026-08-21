"""Contrôle du bilinguisme : aucune chaîne oubliée dans l'interface.
Bilingual audit: no untranslated string anywhere in the interface.

Parcourt TOUS les widgets (libellés, boutons, cases, groupes, menus, actions)
et TOUTES les infobulles, dans les deux langues, et vérifie :
  1. que les deux dictionnaires de i18n.py ont exactement les mêmes clés ;
  2. que les sept textes d'aide existent et se formatent dans les deux langues ;
  3. qu'en anglais aucun texte visible ne contient de mot français, et
     réciproquement ;
  4. que rien n'est resté vide.

Usage (depuis la racine du dépôt) :
    .venv/bin/python verif_sage/test_i18n.py
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "programme"))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import (QApplication, QLabel, QPushButton, QCheckBox,
                             QGroupBox, QAbstractSpinBox, QWidget)
from PyQt6.QtGui import QAction

import i18n
from i18n import STRINGS, LANGUAGE_NAMES
from help_texts import HELP, HELP_KEYS, help_html
import redshift_distance_gui as G

failures = []


def check(cond, msg):
    print(("  OK   " if cond else "  ÉCHEC") + f"  {msg}")
    if not cond:
        failures.append(msg)


# ---------------------------------------------------------------- 1. clés
print("\n1. Clés de traduction")
keys = {lang: set(table) for lang, table in STRINGS.items()}
check(set(STRINGS) == set(LANGUAGE_NAMES),
      f"langues déclarées = langues traduites ({sorted(STRINGS)})")
ref = keys["fr"]
for lang, k in keys.items():
    missing, extra = ref - k, k - ref
    check(not missing, f"[{lang}] aucune clé manquante" + (f" (manque : {sorted(missing)})" if missing else ""))
    check(not extra, f"[{lang}] aucune clé en trop" + (f" (en trop : {sorted(extra)})" if extra else ""))
check(all(v.strip() for table in STRINGS.values() for v in table.values()),
      "aucune traduction vide")

# --------------------------------------------------------------- 2. aides
print("\n2. Textes d'aide")
for lang in STRINGS:
    check(set(HELP[lang]) == set(HELP_KEYS), f"[{lang}] les {len(HELP_KEYS)} aides sont présentes")

app = QApplication(sys.argv)
app.setStyle("Fusion")
G.apply_cosmic_theme(app)
w = G.MainWindow()
w.show()
app.processEvents()

for lang in STRINGS:
    i18n.set_language(lang)
    for key in HELP_KEYS:
        try:
            html = help_html(key, w.ctx)
            ok = len(html) > 400
        except KeyError as exc:
            ok, html = False, ""
            print(f"       (gabarit {key}/{lang} : champ manquant {exc})")
        check(ok, f"[{lang}] aide « {key} » : {len(html)} caractères")

# ------------------------------------------------- 3. textes de l'interface
FRENCH_WORDS = re.compile(
    r"\b(distance comobile|Courbure|Redshift cosmologique|comparer|Aide|Langue|"
    r"Modèle|univers|années?-lumière|vitesse|récession|naïf|Âge|plat|"
    r"Tapez|Objets?-cibles|Presets :|lumière|Grandeurs|Contrôle)\b", re.I)
ENGLISH_WORDS = re.compile(
    r"\b(Comoving distance|Curvature|Cosmological redshift|compare with|Help|Language|"
    r"Model|universe|light-?years?|velocity|recession|naive|Age of|flat|"
    r"Type a|targets|Presets:|light travel|quantities|Check)\b", re.I)

WIDGET_TYPES = (QLabel, QPushButton, QCheckBox, QGroupBox, QAbstractSpinBox, QWidget)


def collect(win) -> list[tuple[str, str]]:
    """(origine, texte) de tout ce que l'utilisateur peut lire."""
    out = [("windowTitle", win.windowTitle()),
           ("statusBar", win.statusBar().currentMessage())]
    for wid in win.findChildren(WIDGET_TYPES):
        for attr in ("text", "title"):
            if hasattr(wid, attr):
                try:
                    txt = getattr(wid, attr)()
                except TypeError:
                    continue
                if isinstance(txt, str) and txt.strip():
                    out.append((type(wid).__name__, txt))
        tip = wid.toolTip()
        if tip.strip():
            out.append((type(wid).__name__ + ".tooltip", tip))
    for act in win.findChildren(QAction):
        if act.text().strip():
            out.append(("QAction", act.text()))
        if act.toolTip().strip():
            out.append(("QAction.tooltip", act.toolTip()))
    return out


print("\n3. Textes de l'interface (widgets, menus, infobulles)")
for lang, forbidden, other in (("en", FRENCH_WORDS, "français"),
                               ("fr", ENGLISH_WORDS, "anglais")):
    w.set_lang(lang)
    app.processEvents()
    texts = collect(w)
    bad = [(src, t) for src, t in texts if forbidden.search(t)]
    # les noms propres et symboles ne comptent pas
    bad = [(s, t) for s, t in bad if not re.fullmatch(r"[\W\dA-Z_·°±×→≈]+", t)]
    check(not bad, f"[{lang}] {len(texts)} textes relevés, aucun mot {other}")
    for src, t in bad[:6]:
        print(f"        ← {src}: {t[:90]!r}")

# --------------------------------------------------- 4. rien d'oublié à vide
print("\n4. Complétude")
for lang in ("fr", "en"):
    w.set_lang(lang)
    app.processEvents()
    empty = [src for src, t in collect(w) if not t.strip()]
    check(not empty, f"[{lang}] aucun libellé vide")

# --------------------------------------------------------- 5. mode console
print("\n5. Version console")
import subprocess
for lang in ("fr", "en"):
    r = subprocess.run([sys.executable, str(ROOT / "programme" / "redshift_distance_calculator.py"),
                        "2.34", "--lang", lang],
                       capture_output=True, text=True, timeout=180)
    out = r.stdout
    forbidden = FRENCH_WORDS if lang == "en" else ENGLISH_WORDS
    hits = [l for l in out.splitlines() if forbidden.search(l)]
    check(r.returncode == 0 and out.strip(), f"[{lang}] la console répond")
    check(not hits, f"[{lang}] sortie console homogène"
          + (f" ({hits[0][:60]!r})" if hits else ""))

print("\n" + "=" * 70)
if failures:
    print(f"  {len(failures)} CONTRÔLE(S) EN ÉCHEC")
    for f in failures:
        print("   -", f)
    sys.exit(1)
print("  Tous les contrôles de bilinguisme passent.")
