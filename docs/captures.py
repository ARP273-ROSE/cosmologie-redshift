"""Captures RÉELLES de la fenêtre pour le manuel, dans les deux langues.

    QT_QPA_PLATFORM=offscreen python docs/captures.py      (depuis la racine)

Même fenêtre, même style figé que le programme livré (interface_kit) ; les
images vont dans docs/captures/{fr,en}-*.png, reprises par MANUEL.md,
MANUAL.md et donc par les manuels PDF (docs/src/compiler.py).
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["COSMO_NO_UPDATE_CHECK"] = "1"
RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "programme"))
SORTIE = RACINE / "docs" / "captures"

from PyQt6.QtWidgets import QApplication  # noqa: E402

import redshift_distance_gui as G  # noqa: E402
from i18n import set_language  # noqa: E402


def main():
    SORTIE.mkdir(parents=True, exist_ok=True)
    app = QApplication(sys.argv)
    G.apply_fixed_style(app)
    for langue in ("fr", "en"):
        set_language(langue)
        w = G.MainWindow()
        w.resize(1180, 780)
        w.show()
        w.z_spin.setValue(2.34)
        app.processEvents()
        w.grab().save(str(SORTIE / f"{langue}-principal.png"))
        w.chk_shoes.setChecked(True)
        w.ok_spin.setValue(0.01)
        app.processEvents()
        w.grab().save(str(SORTIE / f"{langue}-shoes.png"))
        w.close()
    print(f"captures écrites dans {SORTIE}")


if __name__ == "__main__":
    main()
