# -*- coding: utf-8 -*-
"""Bilinguisme : aucun texte d'interface en dur, aucune clé manquante.

Complète verif_sage/test_i18n.py (mêmes clés dans les deux langues, aides,
détection de la langue du système) par une analyse du code de l'interface :

  - un texte passé tel quel à un widget (setText, QLabel, QMessageBox...)
    s'afficherait dans une seule langue ; seules les unités et les sigles
    sont admis ;
  - toute clé t("...") employée existe en français ET en anglais ;
  - la partie anglaise ne contient pas de lettres accentuées françaises.

    python -m pytest -q tests/test_i18n_textes.py
"""
import ast
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / 'programme'))

import i18n  # noqa: E402

SOURCES = [RACINE / 'programme' / 'redshift_distance_gui.py']
METHODES = {'setText', 'setWindowTitle', 'setToolTip', 'setPlaceholderText',
            'addAction', 'addMenu', 'setTitle', 'showMessage', 'setStatusTip',
            'addTab', 'setLabelText', 'addItem', 'setInformativeText',
            'setDetailedText', 'setWhatsThis', 'setTabText'}
CONSTRUCTEURS = {'QLabel', 'QPushButton', 'QCheckBox', 'QGroupBox', 'QAction',
                 'QRadioButton', 'QMenu', 'QToolButton', 'QProgressDialog'}
BOITES = {'information', 'warning', 'critical', 'question', 'about'}
#: unités, sigles et symboles, identiques dans les deux langues
TECHNIQUES = {'km', 'mpc', 'gpc', 'kpc', 'al', 'ly', 'gyr', 'ga', 'myr', 'ma',
              'simbad', 'planck', 'shoes', 'lcdm', 'flrw', 'cmb', 'sr',
              'cz', 'ok', 'om', 'ode', 'english', 'français'}
BALISE = re.compile(r'<[^>]*>|&[a-z]+;|&#\d+;')
MOT = re.compile(r"[A-Za-zÀ-ÿ]{2,}")
ACCENTS = re.compile(r"[éèàçêôûùîïœ]")  # les guillemets « » sont un choix typographique, admis


def _litteraux(n):
    if isinstance(n, ast.Constant) and isinstance(n.value, str):
        return [n.value]
    if isinstance(n, ast.JoinedStr):
        return [v.value for v in n.values
                if isinstance(v, ast.Constant) and isinstance(v.value, str)]
    return []


def _nom(appel):
    f = appel.func
    return f.attr if isinstance(f, ast.Attribute) else getattr(f, 'id', '')


def _appels():
    for fichier in SOURCES:
        for n in ast.walk(ast.parse(fichier.read_text(encoding='utf-8'))):
            if isinstance(n, ast.Call):
                yield fichier, n


def test_aucun_texte_en_dur():
    fautes = []
    for fichier, n in _appels():
        nom = _nom(n)
        if nom in METHODES or nom in CONSTRUCTEURS:
            args = n.args[:1]
        elif nom in BOITES and getattr(getattr(n.func, 'value', None), 'id', '') == 'QMessageBox':
            args = n.args[1:3]
        else:
            continue
        for a in args:
            mots = [m for t in _litteraux(a) for m in MOT.findall(BALISE.sub(' ', t))
                    if m.lower() not in TECHNIQUES]
            if mots:
                fautes.append(f"{fichier.name}:{n.lineno} {nom} -> {' '.join(mots)}")
    assert not fautes, "Textes affichés sans traduction :\n  " + "\n  ".join(fautes)


def test_cles_presentes_dans_les_deux_langues():
    manquantes = []
    for fichier, n in _appels():
        if _nom(n) == 't' and n.args and isinstance(n.args[0], ast.Constant):
            cle = n.args[0].value
            for langue in ('fr', 'en'):
                if cle not in i18n.STRINGS[langue]:
                    manquantes.append(f"{fichier.name}:{n.lineno} {cle} ({langue})")
    assert not manquantes, "Clés absentes :\n  " + "\n  ".join(manquantes)


def test_anglais_sans_accents_francais():
    fautes = [f"{k} : {v[:50]!r}" for k, v in i18n.STRINGS['en'].items()
              if ACCENTS.search(v) and k not in ('lang_fr',)]
    assert not fautes, "Français dans l'interface anglaise :\n  " + "\n  ".join(fautes)
