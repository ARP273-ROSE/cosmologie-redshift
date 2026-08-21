"""Test de l'interface sans écran : instancie la fenêtre, balaye des z, capture.

Usage (depuis la racine du dépôt) :
    QT_QPA_PLATFORM=offscreen .venv/bin/python verif_sage/test_gui_headless.py
    set QT_QPA_PLATFORM=offscreen && .venv\\Scripts\\python.exe verif_sage\\test_gui_headless.py

Les captures sont écrites dans captures/. C'est le test à relancer après
toute modification de la GUI.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "programme"))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication
import redshift_distance_gui as G

OUT = ROOT / "captures"
OUT.mkdir(parents=True, exist_ok=True)

app = QApplication(sys.argv)
app.setStyle("Fusion")
G.apply_cosmic_theme(app)
w = G.MainWindow()
w.resize(1180, 780)
w.show()
app.processEvents()

for z in (0.0, 0.00428, 1.0, 1.59213, 2.34, 10.6, 1089.8, 1500.0):
    w.z_spin.setValue(z)
    app.processEvents()
    print(f"z={z:<10} DC={w.row_comov.value.text():>14} DL={w.row_lum.value.text():>16} "
          f"DA={w.row_ang.value.text():>14} Dlt={w.row_look.value.text():>14}")
    print(f"           age={w.lbl_age.text():<34} E={w.lbl_E.text()}")
    print(f"           v1={w.lbl_v1.text():<28} v3={w.lbl_v3.text()}")
    print("           " + w.statusBar().currentMessage())

# --- comparaison SH0ES ------------------------------------------------------
w.z_spin.setValue(2.34)
w.chk_shoes.setChecked(True)
app.processEvents()
print("\nSH0ES coché :")
print("   ", w.row_comov.value.text(), "|", w.row_comov.alt.text())
print("   ", w.row_ang.value.text(), "|", w.row_ang.alt.text())
assert w.row_comov.alt.isVisible(), "la ligne SH0ES devrait être visible"
assert all(i.isVisible() for i in w.shoes_items.values()), "courbes SH0ES invisibles"

# --- courbure ---------------------------------------------------------------
print("\nCourbure :")
for ok in (-0.02, 0.0, 0.02):
    w.ok_spin.setValue(ok)
    app.processEvents()
    print(f"    Ωk={ok:+.2f}  D_C={w.row_comov.value.text():>22}"
          f"  D_M={w.row_trans.value.text():>22}  (D_M affichée : {w.row_trans.isVisible()})")
    assert w.row_trans.isVisible() == (abs(ok) > 1e-12), "visibilité de D_M incorrecte"
w.ok_spin.setValue(0.0)
w.chk_shoes.setChecked(False)
app.processEvents()

# --- bilinguisme : les deux langues, toutes les aides ----------------------
from help_texts import help_html, HELP_KEYS      # noqa: E402
from i18n import set_language                    # noqa: E402

for lang in ("fr", "en"):
    w.set_lang(lang)
    app.processEvents()
    print(f"\nLangue « {lang} » :")
    print("    titre    :", w.windowTitle())
    print("    D_C      :", w.row_comov.name.text(), "->", w.row_comov.value.text())
    print("    courbure :", w.ok_label.text())
    for key in HELP_KEYS:
        html = help_html(key, w.ctx)
        assert len(html) > 400, f"aide {key} vide en {lang}"
        d = G.HelpDialog(w, key, html)
        d.show()
        app.processEvents()
        d.close()
    print(f"    {len(HELP_KEYS)} boîtes d'aide OK")

# --- saisie clavier des champs numériques (point ET virgule) ---------------
# Sous une locale française, Qt refuse le point décimal par défaut : on vérifie
# ici que les deux séparateurs passent, avec de vraies frappes simulées.
from PyQt6.QtTest import QTest              # noqa: E402
from PyQt6.QtCore import Qt as _Qt          # noqa: E402

print("\nSaisie clavier :")
# Deux gestes sont éprouvés, ceux que l'utilisateur fait réellement.
#
# A. le champ prend le focus, puis on tape : le contenu doit être remplacé ;
# B. le champ a déjà le focus, curseur en fin de ligne : la frappe doit au
#    moins être acceptée.
#
# La version précédente de ce test appelait selectAll() avant de taper, ce qu'un
# utilisateur ne fait jamais, et laissait ainsi passer un défaut où plus aucune
# frappe n'était acceptée : le champ affichant déjà toutes ses décimales, Qt
# rejetait tout caractère supplémentaire, et l'intervalle étroit de la courbure
# rendait invalide chaque valeur intermédiaire.
w.activateWindow()
app.processEvents()

print("  A. le champ reçoit le focus, puis on tape")
for spin, name, cases in (
        (w.ok_spin, "Ωk", (("0.02", 0.02), ("0,015", 0.015), ("-0.01", -0.01),
                           (".03", 0.03), ("0", 0.0), ("-0,05", -0.05),
                           ("9", 0.05))),          # hors bornes : ramené à 0,05
        (w.z_spin,  "z",  (("3.5", 3.5), ("2,34", 2.34), ("1089.8", 1089.8),
                           ("0", 0.0)))):
    other = w.z_spin if spin is w.ok_spin else w.ok_spin
    for typed, expected in cases:
        other.setFocus()                    # le focus vient d'ailleurs…
        app.processEvents()
        spin.setFocus()                     # … puis arrive sur le champ visé
        app.processEvents()
        assert spin.lineEdit().selectedText(), \
            f"{name} : le contenu n'est pas sélectionné à la prise de focus"
        QTest.keyClicks(spin.lineEdit(), typed)
        QTest.keyClick(spin, _Qt.Key.Key_Return)
        app.processEvents()
        got = spin.value()
        ok = abs(got - expected) < 1e-9
        print(f"    {name:>3} : frappe « {typed:>7} » -> {got:+.5f}   {'OK' if ok else 'ÉCHEC'}")
        assert ok, f"saisie « {typed} » non reconnue (valeur lue : {got}, attendue : {expected})"

print("  B. le champ a déjà le focus, curseur en fin de ligne")
for spin, name, typed in ((w.ok_spin, "Ωk", "5"), (w.z_spin, "z", "7")):
    line = spin.lineEdit()
    spin.setFocus()
    app.processEvents()
    line.deselect()
    line.setCursorPosition(len(line.text()))
    before = line.text()
    QTest.keyClicks(line, typed)
    app.processEvents()
    print(f"    {name:>3} : {before!r} + « {typed} » -> {line.text()!r}")
    assert line.text() != before, \
        f"{name} : la frappe « {typed} » a été refusée (champ resté à {before!r})"
    QTest.keyClick(spin, _Qt.Key.Key_Return)
    app.processEvents()
w.ok_spin.setValue(0.0)
w.z_spin.setValue(2.34)
app.processEvents()

# --- recherche d'un objet : le champ, puis le traitement de la réponse ------
# SIMBAD n'est pas interrogé ici : la réponse est fournie telle qu'elle
# arriverait du réseau, pour que le contrôle reste valable hors ligne.
import simbad                                  # noqa: E402

print("\nRecherche d'un objet :")
w.obj_edit.clear()
QTest.keyClicks(w.obj_edit, "3c273")
print(f"    frappe « 3c273 » -> champ = {w.obj_edit.text()!r}")
assert w.obj_edit.text() == "3c273"

w._simbad_query = "3c273"
for label, answer, expect_z in (
        ("objet trouvé",  ([simbad.SimbadObject("3C 273", "Quasar", 0.157568)], None), 0.157568),
        ("objet proche",  ([simbad.SimbadObject("M  87", "AGN", 0.0042)], None), 0.0042),
        ("sans redshift", ([simbad.SimbadObject("LBN 110", "HII Region", None)], None), None),
        ("blueshift",     ([simbad.SimbadObject("M  31", "AGN", -0.001)], None), None),
        ("introuvable",   ([], None), None),
        ("hors ligne",    ([], "timed out"), None)):
    before = w.z_spin.value()
    w._on_simbad_done(answer)
    app.processEvents()
    got = w.z_spin.value()
    ok = abs(got - expect_z) < 1e-5 if expect_z is not None else abs(got - before) < 1e-12
    status = w.obj_status.text().splitlines()[0]
    print(f"    {label:<14} z = {got:<10.6f} {status[:52]}   {'OK' if ok else 'ÉCHEC'}")
    assert ok, f"{label} : z attendu {expect_z}, obtenu {got}"
    assert status.strip(), f"{label} : aucun message affiché"

w.obj_edit.clear()
w._set_object_status(None)          # les captures ne doivent pas garder ce message
w.z_spin.setValue(2.34)
app.processEvents()

w.z_spin.setValue(2.34)
app.processEvents()
w.grab().save(str(OUT / "gui_z2.34.png"))
w.z_spin.setValue(1089.8)
app.processEvents()
w.grab().save(str(OUT / "gui_cmb.png"))

# capture du mode comparaison + courbure
w.z_spin.setValue(2.34)
w.chk_shoes.setChecked(True)
w.ok_spin.setValue(0.01)
app.processEvents()
w.grab().save(str(OUT / "gui_shoes_courbure.png"))
w.chk_shoes.setChecked(False)
w.ok_spin.setValue(0.0)
print(f"captures écrites dans {OUT}")

# capture en anglais
w.set_lang("en")
w.z_spin.setValue(2.34)
app.processEvents()
w.grab().save(str(OUT / "gui_english.png"))
w.set_lang("fr")
print("capture anglaise écrite")
