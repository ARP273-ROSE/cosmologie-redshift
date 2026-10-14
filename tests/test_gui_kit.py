# -*- coding: utf-8 -*-
"""Interface sous Xvfb : le kit commun (mise à jour, rapports, accord) est
branché dans la fenêtre, dans les deux langues. L'interface elle-même (saisie,
calculs, captures) est vérifiée par verif_sage/test_gui_headless.py.

    xvfb-run -a python -m pytest -q tests/test_gui_kit.py
"""
import os
import sys
import tempfile
from pathlib import Path

_TMP = tempfile.mkdtemp(prefix='cosmo-test-')
os.environ['HOME'] = _TMP
os.environ['XDG_CONFIG_HOME'] = os.path.join(_TMP, 'config')
os.environ['COSMO_NO_UPDATE_CHECK'] = '1'      # pas de réseau au démarrage
os.environ.setdefault('QT_QPA_PLATFORM', 'xcb' if os.environ.get('DISPLAY') else 'offscreen')

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / 'programme'))

import pytest  # noqa: E402

pytest.importorskip('PyQt6')
from PyQt6.QtWidgets import QApplication, QMessageBox  # noqa: E402

APP = QApplication.instance() or QApplication([])

import redshift_distance_gui as gui  # noqa: E402
from i18n import set_language  # noqa: E402


def _menu_aide(win):
    return [a.text() for a in win.help_menu.actions() if a.text()]


@pytest.mark.parametrize('lang,attendu', [('en', '&Report a problem…'),
                                          ('fr', '&Signaler un problème…')])
def test_menu_aide(lang, attendu):
    set_language(lang)
    win = gui.MainWindow()
    win.show()
    APP.processEvents()
    assert attendu in _menu_aide(win)
    assert win.act_autoreport.isCheckable()
    win.close()


def test_mise_a_jour_passe_par_le_kit(monkeypatch):
    import updater
    appels, vus = [], []
    monkeypatch.setattr(updater, 'check', lambda v: appels.append(v) or None)
    monkeypatch.setattr(QMessageBox, 'information', lambda *a, **k: vus.append(a[2]))
    set_language('en')
    win = gui.MainWindow()
    win.check_updates(manual=True)
    win._update_thread.join(5)
    for _ in range(20):
        APP.processEvents()
    assert appels == [gui.__version__]
    assert vus and 'latest' in vus[0]
    win.close()


def test_accord_rapports(monkeypatch):
    import reporting
    reporting.init(Path(_TMP) / 'donnees', application='cosmo-test', version='0')
    reporting.definir_consentement(False)
    monkeypatch.setattr(reporting, 'signaler_demarrage', lambda **k: None)
    win = gui.MainWindow()
    win.ask_report_consent()                  # déjà répondu : aucune boîte
    win.act_autoreport.setChecked(True)
    assert reporting.consentement() is True
    win.act_autoreport.setChecked(False)
    assert reporting.consentement() is False
    win.close()


def test_check_en_ligne_de_commande():
    import subprocess
    r = subprocess.run([sys.executable, '-B', str(RACINE / 'programme' / 'redshift_distance_gui.py'),
                        '--check'], capture_output=True, text=True, timeout=180,
                       env={**os.environ, 'QT_QPA_PLATFORM': 'offscreen'})
    assert r.returncode == 0, r.stdout + r.stderr


def test_le_programme_demarre_vraiment():
    """Lance le vrai point d'entrée quelques secondes : main() entier (style,
    verrou, accord différé, vigie) doit tourner sans exception."""
    import subprocess
    env = {**os.environ, 'HOME': _TMP, 'COSMO_NO_UPDATE_CHECK': '1'}
    try:
        r = subprocess.run([sys.executable, '-B',
                            str(RACINE / 'programme' / 'redshift_distance_gui.py')],
                           capture_output=True, text=True, timeout=8, env=env)
        sortie = r.stdout + r.stderr
        assert r.returncode == 0, sortie
    except subprocess.TimeoutExpired as e:
        sortie = (e.stdout or b'').decode() + (e.stderr or b'').decode()
    assert 'Traceback' not in sortie, sortie
