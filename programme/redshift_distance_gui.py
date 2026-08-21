#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
CALCULATEUR DE DISTANCES COSMOLOGIQUES — interface graphique (FR / EN)
COSMOLOGICAL DISTANCE CALCULATOR — graphical interface (FR / EN)
================================================================================
Convertit un redshift z en quatre distances cosmologiques et en grandeurs
cinématiques associées, dans le cadre ΛCDM contraint par Planck 2018.

Converts a redshift z into the four cosmological distances and the associated
kinematic quantities, in ΛCDM constrained by Planck 2018.

Tout le calcul physique est dans `cosmo_core.py`, les libellés dans `i18n.py`
et les textes d'aide dans `help_texts.py`. Ce fichier ne contient que
l'interface : PyQt6 + pyqtgraph, thème « cosmic ».

Langue : menu « Langue / Language », ou variable COSMO_LANG=en, ou --lang en.
================================================================================
"""

import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:      # importable quel que soit le dossier courant
    sys.path.insert(0, str(HERE))

import numpy as np

from PyQt6.QtCore import (Qt, QLocale, QThread, pyqtSignal, QObject, QSettings,
                          QTimer)
from PyQt6.QtGui import (QFont, QPalette, QColor, QAction, QIcon, QPixmap,
                         QActionGroup, QValidator)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QDoubleSpinBox, QPushButton, QGroupBox, QFrame, QSizePolicy,
    QDialog, QTextBrowser, QDialogButtonBox, QCheckBox, QMessageBox,
    QLineEdit, QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView,
)

import pyqtgraph as pg

from cosmo_core import (
    cosmo, compute, curves, format_distance, format_time, format_pm,
    help_context, PRESETS,
    fmt_num, C_KMS, T0_GYR, D_H_GLYR, PARTICLE_HORIZON_GLYR, EVENT_HORIZON_GLYR,
    Z_DA_MAX, DA_MAX_GLYR, H0_PLANCK, OM_PLANCK, H0_SHOES,
)
from i18n import (t, set_language, current_language, detect_system_language,
                  LANGUAGE_NAMES)
from help_texts import help_html
import simbad
from updates import (__version__, RELEASES_URL, DOWNLOAD_URL,
                     latest_version, is_newer, check_enabled)

# --- polices : listes de repli couvrant Windows, Linux et macOS -------------
FONT_UI = ('"Segoe UI", "Inter", "Helvetica Neue", "Ubuntu", "Cantarell", '
           '"Noto Sans", "DejaVu Sans", sans-serif')
FONT_MONO = ["Cascadia Mono", "Cascadia Code", "Consolas",          # Windows
             "SF Mono", "Menlo", "Monaco",                          # macOS
             "DejaVu Sans Mono", "Liberation Mono", "Noto Sans Mono",  # Linux
             "monospace"]


def mono_font(size: int) -> QFont:
    """Police à chasse fixe, avec repli sur les trois plateformes."""
    f = QFont(FONT_MONO[0], size)
    f.setFamilies(FONT_MONO)
    f.setBold(True)
    f.setStyleHint(QFont.StyleHint.Monospace)
    return f


# Vector rendering via QPainter — crisp at any DPI / window size.
pg.setConfigOption('antialias', True)
pg.setConfigOption('useOpenGL', False)


# ============================================================================
# COSMIC COLOR PALETTE (aligned with astromanager/gui/theme.py)
# ============================================================================

COLORS = {
    'bg_darkest':     '#080c16',
    'bg_dark':        '#0a0e1a',
    'bg_medium':      '#141828',
    'bg_light':       '#1e2438',
    'bg_lighter':     '#2a3248',
    'bg_input':       '#161c30',
    'bg_hover':       '#252d45',
    'bg_selected':    '#1a3050',

    'accent_cyan':    '#94b8c8',
    'accent_purple':  '#a8a0c0',
    'accent_pink':    '#c0a0ac',
    'accent_orange':  '#c0b098',
    'accent_yellow':  '#b8b090',

    'success':        '#88b098',
    'warning':        '#b8a880',
    'error':          '#b89090',
    'info':           '#90a8b8',

    'text_primary':   '#c8ccd4',
    'text_secondary': '#7a8498',
    'text_disabled':  '#4a5270',
    'text_accent':    '#94b8c8',

    'border':         '#2d3550',
    'border_light':   '#3d4663',
    'border_focus':   '#94b8c8',
}


def get_cosmic_stylesheet() -> str:
    c = COLORS
    return f"""
    QMainWindow {{ background-color: {c['bg_dark']}; color: {c['text_primary']}; }}
    QWidget {{
        background-color: {c['bg_dark']};
        color: {c['text_primary']};
        font-family: {FONT_UI};
        font-size: 9pt;
    }}
    QLabel {{ color: {c['text_primary']}; background: transparent; padding: 1px; }}
    QLabel[heading="true"] {{
        font-size: 14pt; font-weight: bold; color: {c['accent_cyan']}; padding: 4px 2px;
    }}
    QLabel[sub="true"] {{ color: {c['text_secondary']}; font-size: 9pt; }}

    QPushButton {{
        background-color: {c['bg_lighter']};
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        border-radius: 5px;
        padding: 5px 12px;
        font-weight: 500;
        min-height: 22px;
    }}
    QPushButton:hover {{
        background-color: {c['bg_hover']};
        border-color: {c['accent_cyan']};
    }}
    QPushButton:pressed {{ background-color: {c['bg_selected']}; }}
    QPushButton[accent="true"] {{
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #244858, stop:1 #1c3a48);
        border: 1px solid {c['accent_cyan']};
        font-weight: bold;
    }}

    QDoubleSpinBox, QSpinBox, QLineEdit {{
        background-color: {c['bg_input']};
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 4px 8px;
        selection-background-color: {c['accent_cyan']};
        selection-color: {c['bg_dark']};
    }}
    QDoubleSpinBox:focus, QSpinBox:focus, QLineEdit:focus {{ border-color: {c['border_focus']}; }}

    QCheckBox {{ spacing: 6px; }}

    QGroupBox {{
        background-color: {c['bg_medium']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        margin-top: 12px;
        padding: 14px 8px 6px 8px;
        font-weight: bold;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 2px 8px;
        color: {c['accent_cyan']};
        background-color: {c['bg_medium']};
        border-radius: 3px;
        font-size: 9pt;
    }}

    QToolTip {{
        background-color: {c['bg_light']};
        color: {c['text_primary']};
        border: 1px solid {c['accent_cyan']};
        border-radius: 4px;
        padding: 6px;
        font-size: 9pt;
    }}

    QStatusBar {{
        background-color: {c['bg_darkest']};
        color: {c['text_secondary']};
        border-top: 1px solid {c['border']};
        padding: 4px;
    }}
    """


def apply_cosmic_theme(app: QApplication):
    app.setStyleSheet(get_cosmic_stylesheet())
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(COLORS['bg_dark']))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(COLORS['text_primary']))
    palette.setColor(QPalette.ColorRole.Base, QColor(COLORS['bg_input']))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(COLORS['bg_medium']))
    palette.setColor(QPalette.ColorRole.Text, QColor(COLORS['text_primary']))
    palette.setColor(QPalette.ColorRole.Button, QColor(COLORS['bg_lighter']))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(COLORS['text_primary']))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(COLORS['accent_cyan']))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(COLORS['bg_dark']))
    app.setPalette(palette)


# ============================================================================
# WIDGETS
# ============================================================================

class NumberSpinBox(QDoubleSpinBox):
    """QDoubleSpinBox où la saisie au clavier fonctionne vraiment.

    Trois obstacles rendaient ces champs quasi impossibles à remplir à la main,
    au point qu'ils semblaient réservés aux flèches :

    * sous une locale française, Qt refusait le point décimal ;
    * le champ affichant déjà toutes ses décimales (« 0.0000 » pour la
      courbure), toute frappe supplémentaire en dépassait le nombre autorisé
      et se voyait rejetée ;
    * un intervalle étroit comme [-0,05 ; 0,05] rend invalide presque toute
      valeur intermédiaire — il faut bien taper « 0 » avant « 0,01 » — et Qt
      refusait la frappe au lieu d'attendre la suite.

    D'où : les deux séparateurs décimaux acceptés, une validation qui laisse
    taper tant que le texte est un nombre plausible (la valeur n'est ramenée
    dans les bornes qu'à la validation), et le contenu sélectionné quand le
    champ prend le focus, pour que la frappe remplace au lieu de s'insérer au
    milieu.

    `live=False` n'émet valueChanged qu'à la validation (Entrée / perte de
    focus), ce qui évite de recalculer les courbes à chaque frappe.
    """

    # Un nombre en cours de frappe : signe, chiffres, un seul séparateur.
    _PARTIAL = re.compile(r"^[+-]?\d*\.?\d*$")

    def __init__(self, live: bool = True, parent=None):
        super().__init__(parent)
        self.setLocale(QLocale(QLocale.Language.C))    # point décimal
        self.setKeyboardTracking(live)
        self.setAlignment(Qt.AlignmentFlag.AlignRight)

    @staticmethod
    def _norm(text: str) -> str:
        return text.replace(",", ".").replace(" ", "").replace(" ", "")

    def validate(self, text, pos):                     # noqa: N802 (API Qt)
        normalised = self._norm(text)
        state, fixed, pos = super().validate(normalised, pos)
        if state == QValidator.State.Invalid and self._PARTIAL.match(normalised):
            # Saisie encore incomplète ou momentanément hors bornes : on laisse
            # taper. La valeur sera ramenée dans l'intervalle à la validation.
            return QValidator.State.Intermediate, normalised, pos
        return state, fixed, pos

    def fixup(self, text: str) -> str:                 # noqa: N802 (API Qt)
        """Rend présentable une saisie restée incomplète à la validation.

        Qt appelle cette méthode lorsque le texte est jugé intermédiaire : sans
        elle, une valeur hors bornes serait purement et simplement abandonnée.
        Elle est ici ramenée à la borne la plus proche — taper 9 dans la
        courbure donne 0,05.
        """
        try:
            value = float(self._norm(text) or 0.0)
        except ValueError:
            value = self.value()
        return self.textFromValue(max(self.minimum(), min(self.maximum(), value)))

    def focusInEvent(self, event):                     # noqa: N802 (API Qt)
        super().focusInEvent(event)
        # Le clic place le curseur après cet événement : on sélectionne au
        # tour de boucle suivant, sinon la sélection serait aussitôt défaite.
        QTimer.singleShot(0, self.selectAll)

    def valueFromText(self, text) -> float:            # noqa: N802 (API Qt)
        try:
            value = float(self._norm(text) or 0.0)
        except ValueError:
            return self.value()
        # Une valeur hors domaine est ramenée à la borne la plus proche, plutôt
        # qu'ignorée en silence : taper 9 dans la courbure donne 0,05.
        return max(self.minimum(), min(self.maximum(), value))

    def textFromValue(self, value: float) -> str:      # noqa: N802 (API Qt)
        return f"{value:.{self.decimals()}f}"


class UpdateWorker(QObject):
    """Interroge GitHub dans un fil séparé ; ne bloque jamais l'interface."""
    done = pyqtSignal(object)          # str (version) ou None

    def run(self):
        self.done.emit(latest_version())




class SimbadWorker(QObject):
    """Interroge SIMBAD dans un fil séparé ; ne bloque jamais l'interface."""
    done = pyqtSignal(object)          # (candidats, erreur ou None)

    def __init__(self, query: str):
        super().__init__()
        self.query = query

    def run(self):
        try:
            objects, _ = simbad.resolve(self.query)
            self.done.emit((objects, None))
        except simbad.SimbadError as exc:
            self.done.emit(([], str(exc)))
        except Exception as exc:                       # pare-fou : jamais de plantage
            self.done.emit(([], str(exc)))


class ObjectChoiceDialog(QDialog):
    """Liste les objets renvoyés par SIMBAD quand le nom demandé est ambigu."""

    def __init__(self, parent, query: str, objects: list):
        super().__init__(parent)
        self.objects = objects
        self.setWindowTitle(t("object_choose_title"))
        self.resize(620, 380)
        self.setStyleSheet(f"QDialog {{ background-color: {COLORS['bg_dark']}; }}")

        layout = QVBoxLayout(self)
        intro = QLabel(t("object_choose_text", n=len(objects), query=query))
        intro.setWordWrap(True)
        layout.addWidget(intro)

        self.table = QTableWidget(len(objects), 3)
        self.table.setHorizontalHeaderLabels(
            [t("object_col_name"), t("object_col_type"), t("object_col_z")])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setStyleSheet(
            f"QTableWidget {{ background-color: {COLORS['bg_medium']};"
            f" color: {COLORS['text_primary']}; gridline-color: {COLORS['border']};"
            f" border: 1px solid {COLORS['border']}; border-radius: 6px; }}"
            f"QHeaderView::section {{ background-color: {COLORS['bg_dark']};"
            f" color: {COLORS['text_secondary']}; border: 0px; padding: 6px; }}")
        for row, obj in enumerate(objects):
            z = t("object_unknown_z") if obj.redshift is None else fmt_num(obj.redshift, 6)
            for col, text in enumerate((obj.name, obj.otype, z)):
                item = QTableWidgetItem(text)
                if col == 2:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight
                                          | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row, col, item)
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch)
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch)
        self.table.selectRow(0)
        self.table.doubleClicked.connect(self.accept)
        layout.addWidget(self.table)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok
                                   | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def chosen(self):
        rows = self.table.selectionModel().selectedRows()
        return self.objects[rows[0].row()] if rows else None


class HelpDialog(QDialog):
    """Rich-text dialog used by every Help-menu entry."""
    def __init__(self, parent, title: str, html: str):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(780, 620)
        self.setStyleSheet(f"QDialog {{ background-color: {COLORS['bg_dark']}; }}")
        layout = QVBoxLayout(self)
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setStyleSheet(
            f"QTextBrowser {{"
            f"background-color: {COLORS['bg_medium']};"
            f"color: {COLORS['text_primary']};"
            f"border: 1px solid {COLORS['border']};"
            f"border-radius: 6px;"
            f"padding: 14px;"
            f"font-family: {FONT_UI};"
            f"font-size: 10pt;"
            f"}}"
        )
        browser.setHtml(html)
        layout.addWidget(browser)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class ResultRow(QFrame):
    """Bandeau distance : valeur ± incertitude, et valeur SH0ES en regard."""
    def __init__(self, label: str, tooltip: str, accent: str):
        super().__init__()
        self.setStyleSheet(
            f"QFrame {{ background-color: {COLORS['bg_light']}; border-left: 3px solid {accent}; "
            f"border-radius: 4px; padding: 2px; }}"
        )
        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 5, 10, 5)

        self.name = QLabel(label)
        self.name.setToolTip(tooltip)
        name_font = QFont()
        name_font.setBold(True)
        self.name.setFont(name_font)
        self.name.setMinimumWidth(230)

        right = QVBoxLayout()
        right.setSpacing(0)
        self.value = QLabel("—")
        self.value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.value.setFont(mono_font(11))
        self.value.setStyleSheet(f"color: {accent};")
        self.alt = QLabel("")
        self.alt.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        alt_font = mono_font(8)
        alt_font.setBold(False)
        self.alt.setFont(alt_font)
        self.alt.setStyleSheet(f"color: {COLORS['text_secondary']};")
        self.alt.setVisible(False)
        right.addWidget(self.value)
        right.addWidget(self.alt)

        lay.addWidget(self.name)
        lay.addStretch()
        lay.addLayout(right)

    def set_label(self, label: str, tooltip: str):
        self.name.setText(label)
        self.name.setToolTip(tooltip)

    def set_value(self, text: str, alt: str | None = None):
        self.value.setText(text)
        if alt:
            self.alt.setText(alt)
            self.alt.setVisible(True)
        else:
            self.alt.setVisible(False)


# ============================================================================
# MAIN WINDOW
# ============================================================================

class MainWindow(QMainWindow):

    DISTANCE_COLORS = {
        'comoving':         COLORS['accent_cyan'],
        'luminosity':       COLORS['accent_orange'],
        'angular_diameter': COLORS['accent_purple'],
        'lookback':         COLORS['success'],
    }

    def __init__(self):
        super().__init__()
        self.ctx = help_context()
        self.resize(1180, 800)

        icon = QIcon()
        for size in (16, 32, 64, 128, 256):
            png = HERE / f"logo_{size}.png"
            if png.exists():
                icon.addPixmap(QPixmap(str(png)))
        if not icon.isNull():
            self.setWindowIcon(icon)
            QApplication.instance().setWindowIcon(icon)

        self._build_menu()

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(14, 12, 14, 10)
        root.setSpacing(10)

        # ---- Header ----
        self.header = QLabel()
        self.header.setProperty("heading", True)
        self.sub = QLabel()
        self.sub.setProperty("sub", True)
        root.addWidget(self.header)
        root.addWidget(self.sub)

        # ---- Redshift ----
        self.input_box = QGroupBox()
        in_outer = QVBoxLayout(self.input_box)
        in_lay = QHBoxLayout()
        in_outer.addLayout(in_lay)
        self.z_label = QLabel()
        in_lay.addWidget(self.z_label)
        self.z_spin = NumberSpinBox(live=True)
        self.z_spin.setDecimals(5)
        self.z_spin.setRange(0.0, 1500.0)      # CMB ≈ 1089,8
        self.z_spin.setSingleStep(0.01)
        self.z_spin.setValue(2.34)
        self.z_spin.setMinimumWidth(170)
        self.z_spin.valueChanged.connect(self.recompute)
        in_lay.addWidget(self.z_spin)

        in_lay.addSpacing(16)
        self.presets_label = QLabel()
        in_lay.addWidget(self.presets_label)
        self.preset_buttons = []
        for name, z, tip_key in PRESETS:
            btn = QPushButton(name)
            btn.setProperty("accent", True)
            btn.clicked.connect(lambda _=False, val=z: self.z_spin.setValue(val))
            in_lay.addWidget(btn)
            self.preset_buttons.append((btn, tip_key))
        in_lay.addStretch()

        # ---- Recherche d'un objet par son nom (SIMBAD) ----
        obj_lay = QHBoxLayout()
        in_outer.addLayout(obj_lay)
        self.obj_label = QLabel()
        obj_lay.addWidget(self.obj_label)
        self.obj_edit = QLineEdit()
        self.obj_edit.setMinimumWidth(240)
        self.obj_edit.returnPressed.connect(self.lookup_object)
        obj_lay.addWidget(self.obj_edit)
        self.obj_button = QPushButton()
        self.obj_button.setProperty("accent", True)
        self.obj_button.clicked.connect(self.lookup_object)
        obj_lay.addWidget(self.obj_button)
        self.obj_status = QLabel()
        self.obj_status.setProperty("sub", True)
        self.obj_status.setWordWrap(True)
        obj_lay.addWidget(self.obj_status, 1)

        root.addWidget(self.input_box)

        # ---- Modèle : courbure et comparaison SH0ES ----
        self.model_box = QGroupBox()
        m_lay = QHBoxLayout(self.model_box)
        self.ok_label = QLabel()
        m_lay.addWidget(self.ok_label)
        # live=False : la valeur n'est appliquée qu'à Entrée / perte de focus,
        # sinon chaque frappe relancerait le calcul des courbes.
        self.ok_spin = NumberSpinBox(live=False)
        self.ok_spin.setDecimals(4)
        self.ok_spin.setRange(-0.05, 0.05)
        self.ok_spin.setSingleStep(0.001)
        self.ok_spin.setValue(0.0)
        self.ok_spin.setMinimumWidth(120)
        self.ok_spin.valueChanged.connect(self.on_curvature_changed)
        m_lay.addWidget(self.ok_spin)

        self.btn_flat = QPushButton()
        self.btn_flat.clicked.connect(lambda: self.ok_spin.setValue(0.0))
        m_lay.addWidget(self.btn_flat)

        m_lay.addSpacing(24)
        self.chk_shoes = QCheckBox()
        self.chk_shoes.toggled.connect(self.on_shoes_toggled)
        m_lay.addWidget(self.chk_shoes)
        m_lay.addStretch()
        root.addWidget(self.model_box)

        # ---- Body ----
        body = QHBoxLayout()
        body.setSpacing(10)
        root.addLayout(body, 1)

        left_col = QVBoxLayout()
        left_col.setSpacing(8)

        self.results_box = QGroupBox()
        rlay = QVBoxLayout(self.results_box)
        rlay.setSpacing(6)

        self.row_comov = ResultRow("", "", self.DISTANCE_COLORS['comoving'])
        self.row_trans = ResultRow("", "", COLORS['accent_yellow'])
        self.row_trans.setVisible(False)          # affichée seulement si Ωk ≠ 0
        self.row_lum = ResultRow("", "", self.DISTANCE_COLORS['luminosity'])
        self.row_ang = ResultRow("", "", self.DISTANCE_COLORS['angular_diameter'])
        self.row_look = ResultRow("", "", self.DISTANCE_COLORS['lookback'])
        for r in (self.row_comov, self.row_trans, self.row_lum,
                  self.row_ang, self.row_look):
            rlay.addWidget(r)
        left_col.addWidget(self.results_box)

        self.info_box = QGroupBox()
        ilay = QGridLayout(self.info_box)
        ilay.setVerticalSpacing(7)
        ilay.setHorizontalSpacing(14)
        mono = mono_font(10)

        self.info_labels = {}

        def add_row(row: int, key: str) -> QLabel:
            lbl = QLabel()
            ilay.addWidget(lbl, row, 0)
            val = QLabel("—")
            val.setFont(mono)
            ilay.addWidget(val, row, 1)
            self.info_labels[key] = (lbl, val)
            return val

        self.lbl_lookback = add_row(0, "lookback")
        self.lbl_age      = add_row(1, "age")
        self.lbl_a        = add_row(2, "scale")
        self.lbl_E        = add_row(3, "E")
        self.lbl_v1       = add_row(4, "v1")
        self.lbl_v2       = add_row(5, "v2")
        self.lbl_v3       = add_row(6, "v3")

        left_col.addWidget(self.info_box)
        left_col.addStretch()

        left_widget = QWidget()
        left_widget.setLayout(left_col)
        left_widget.setMinimumWidth(520)
        body.addWidget(left_widget)

        self.plot_box = QGroupBox()
        plot_lay = QVBoxLayout(self.plot_box)
        pg.setConfigOption('background', COLORS['bg_dark'])
        pg.setConfigOption('foreground', COLORS['text_primary'])
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.plot_widget.setMinimumHeight(380)
        plot_lay.addWidget(self.plot_widget)
        body.addWidget(self.plot_box, 1)

        self._build_plot()
        self.retranslate()
        self.recompute()
        self._update_thread = None
        self.check_updates()          # silencieuse, en tâche de fond

    # ------------------------------------------------------------------ menus

    def _build_menu(self):
        self.menuBar().setStyleSheet(
            f"QMenuBar {{ background-color: {COLORS['bg_darkest']};"
            f" color: {COLORS['text_primary']}; padding: 4px; }}"
            f"QMenuBar::item:selected {{ background-color: {COLORS['bg_hover']};"
            f" color: {COLORS['accent_cyan']}; }}"
            f"QMenu {{ background-color: {COLORS['bg_medium']};"
            f" color: {COLORS['text_primary']}; border: 1px solid {COLORS['border']}; }}"
            f"QMenu::item:selected {{ background-color: {COLORS['bg_selected']};"
            f" color: {COLORS['accent_cyan']}; }}"
        )

        self.help_menu = self.menuBar().addMenu("")
        self.help_actions = []
        entries = [("F1", "act_distances", "title_distances", "distances"),
                   ("F2", "act_planck",    "title_planck",    "planck"),
                   ("F3", "act_recession", "title_recession", "recession"),
                   ("F4", "act_presets",   "title_presets",   "presets"),
                   ("F7", "act_simbad",    "title_simbad",    "simbad"),
                   ("F5", "act_verif",     "title_verif",     "verif"),
                   ("F6", "act_sigma",     "title_sigma",     "sigma")]
        for shortcut, act_key, title_key, help_key in entries:
            act = QAction("", self)
            act.setShortcut(shortcut)
            act.triggered.connect(
                lambda _=False, tk=title_key, hk=help_key:
                HelpDialog(self, t(tk), help_html(hk, self.ctx)).exec())
            self.help_menu.addAction(act)
            self.help_actions.append((act, act_key))

        self.help_menu.addSeparator()
        self.act_update = QAction("", self)
        self.act_update.triggered.connect(lambda: self.check_updates(manual=True))
        self.help_menu.addAction(self.act_update)

        self.act_about = QAction("", self)
        self.act_about.triggered.connect(
            lambda: HelpDialog(self, t("title_about"), help_html("about", self.ctx)).exec())
        self.help_menu.addAction(self.act_about)

        # --- menu Langue / Language
        self.lang_menu = self.menuBar().addMenu("")
        group = QActionGroup(self)
        group.setExclusive(True)
        self.lang_actions = {}
        for code, name in LANGUAGE_NAMES.items():
            act = QAction(name, self)
            act.setCheckable(True)
            act.setChecked(code == current_language())
            act.triggered.connect(lambda _=False, c=code: self.set_lang(c))
            group.addAction(act)
            self.lang_menu.addAction(act)
            self.lang_actions[code] = act

    # ------------------------------------------------------ mises à jour

    # ------------------------------------------------------------------
    # Recherche d'un objet dans SIMBAD
    # ------------------------------------------------------------------
    def _object_status(self) -> str:
        """Dernier message de recherche, reformulé dans la langue courante."""
        key, kwargs = getattr(self, "_obj_message", (None, {}))
        if not key:
            return ""
        # Le redshift est gardé brut : sa mise en forme suit la langue, qui
        # peut changer après coup (virgule en français, point en anglais).
        shown = {k: (fmt_num(v, 6) if k == "z" and isinstance(v, float) else v)
                 for k, v in kwargs.items()}
        return t(key, **shown)

    def _set_object_status(self, key: str | None, **kwargs):
        self._obj_message = (key, kwargs) if key else (None, {})
        self.obj_status.setText(self._object_status())

    def lookup_object(self):
        """Demande à SIMBAD le redshift de l'objet dont le nom a été saisi."""
        query = self.obj_edit.text().strip()
        if not query or getattr(self, "_simbad_thread", None) is not None:
            return
        self.obj_button.setEnabled(False)
        self._set_object_status("object_working")
        self._simbad_query = query
        self._simbad_thread = QThread(self)
        self._simbad_worker = SimbadWorker(query)
        self._simbad_worker.moveToThread(self._simbad_thread)
        self._simbad_thread.started.connect(self._simbad_worker.run)
        self._simbad_worker.done.connect(self._on_simbad_done)
        self._simbad_worker.done.connect(self._simbad_thread.quit)
        self._simbad_thread.finished.connect(self._clear_simbad_thread)
        self._simbad_thread.start()

    def _clear_simbad_thread(self):
        self._simbad_thread = None
        self._simbad_worker = None
        self.obj_button.setEnabled(True)

    def _on_simbad_done(self, result):
        objects, error = result
        if error:
            self._set_object_status("object_offline", error=error)
            return
        if not objects:
            self._set_object_status("object_none")
            return
        if len(objects) == 1:
            self._apply_object(objects[0])
            return
        dialog = ObjectChoiceDialog(self, self._simbad_query, objects)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            chosen = dialog.chosen()
            if chosen is not None:
                self._apply_object(chosen)

    def _apply_object(self, obj):
        """Reporte le redshift de l'objet choisi, ou explique pourquoi non."""
        otype = obj.otype or "?"
        if obj.redshift is None:
            self._set_object_status("object_no_z", name=obj.name, otype=otype)
            return
        if obj.redshift <= 0.0:
            self._set_object_status("object_neg_z", name=obj.name, z=obj.redshift)
            return
        z = min(obj.redshift, self.z_spin.maximum())
        self.z_spin.setValue(z)
        if obj.redshift < 0.03:
            self._set_object_status("object_near", z=obj.redshift)
        else:
            self._set_object_status("object_found", name=obj.name, otype=otype,
                                    z=obj.redshift)

    def check_updates(self, manual: bool = False):
        """Vérifie la dernière version publiée, sans bloquer l'interface."""
        if not manual and not check_enabled():
            return
        if getattr(self, "_update_thread", None) is not None:
            return
        if manual:
            self.statusBar().showMessage(t("update_checking"), 4000)
        self._update_thread = QThread(self)
        self._update_worker = UpdateWorker()
        self._update_worker.moveToThread(self._update_thread)
        self._update_thread.started.connect(self._update_worker.run)
        self._update_worker.done.connect(
            lambda remote, m=manual: self._on_update_checked(remote, m))
        self._update_worker.done.connect(self._update_thread.quit)
        self._update_thread.finished.connect(self._clear_update_thread)
        self._update_thread.start()

    def _clear_update_thread(self):
        self._update_thread = None
        self._update_worker = None

    def _on_update_checked(self, remote, manual: bool):
        if remote and is_newer(remote):
            if manual:
                QMessageBox.information(
                    self, t("update_title"),
                    t("update_available", remote=remote, local=__version__,
                      url=DOWNLOAD_URL))
            else:
                self.statusBar().showMessage(t("update_banner", remote=remote), 15000)
        elif manual:
            if remote:
                QMessageBox.information(self, t("update_title"),
                                        t("update_current", local=__version__))
            else:
                QMessageBox.warning(self, t("update_title"),
                                    t("update_offline", url=RELEASES_URL))

    def set_lang(self, code: str):
        set_language(code)
        _save_language(code)          # le choix survit au redémarrage
        for c, act in self.lang_actions.items():
            act.setChecked(c == code)
        self.retranslate()
        self.recompute()

    # ---------------------------------------------------------- traductions

    def retranslate(self):
        """Applique la langue courante à tous les libellés."""
        c = self.ctx
        self.setWindowTitle(f'{t("window_title")}  —  v{__version__}')
        self.header.setText(t("header"))
        self.sub.setText(t("subtitle", h0=H0_PLANCK, om=OM_PLANCK, ode=cosmo.Ode0,
                            ogam=cosmo.Ogamma0, t0=T0_GYR))
        self.sub.setToolTip(t("subtitle_tip", om0=cosmo.Om0, onu=cosmo.Onu0))

        self.input_box.setTitle(t("box_redshift"))
        self.z_label.setText(t("z_equals"))
        self.z_label.setToolTip(t("z_tip"))
        self.z_spin.setToolTip(t("z_spin_tip"))
        self.presets_label.setText(t("presets"))
        self.presets_label.setToolTip(t("presets_tip"))
        for btn, tip_key in self.preset_buttons:
            btn.setToolTip(t(tip_key))

        self.obj_label.setText(t("object_label"))
        self.obj_label.setToolTip(t("object_tip"))
        self.obj_edit.setPlaceholderText(t("object_hint"))
        self.obj_edit.setToolTip(t("object_tip"))
        self.obj_button.setText(t("object_search"))
        self.obj_button.setToolTip(t("object_search_tip"))
        self.obj_status.setText(self._object_status())

        self.model_box.setTitle(t("box_model"))
        self.ok_label.setText(t("curvature"))
        self.ok_label.setToolTip(t("curvature_tip"))
        self.ok_spin.setToolTip(t("curvature_tip"))
        self.btn_flat.setText(t("flat_button"))
        self.btn_flat.setToolTip(t("flat_tip"))
        self.chk_shoes.setText(t("compare_shoes", h0=H0_SHOES))
        self.chk_shoes.setToolTip(t("shoes_tip", h0=H0_SHOES))

        self.results_box.setTitle(t("box_distances"))
        self.row_comov.set_label(t("row_comoving"), t("tip_comoving", horizon=PARTICLE_HORIZON_GLYR))
        self.row_trans.set_label(t("row_transverse"), t("tip_transverse"))
        self.row_lum.set_label(t("row_luminosity"), t("tip_luminosity"))
        self.row_ang.set_label(t("row_angular"), t("tip_angular",
                                                   damax=DA_MAX_GLYR, zdamax=Z_DA_MAX))
        self.row_look.set_label(t("row_lookback"), t("tip_lookback", t0=T0_GYR))

        self.info_box.setTitle(t("box_info"))
        for key, label_key, tip_key, kw in (
                ("lookback", "lbl_lookback", "tip_lb",   {"t0": T0_GYR}),
                ("age",      "lbl_age",      "tip_age",  {"t0": T0_GYR}),
                ("scale",    "lbl_scale",    "tip_scale", {}),
                ("E",        "lbl_E",        "tip_E",    {}),
                ("v1",       "lbl_v1",       "tip_v1",   {}),
                ("v2",       "lbl_v2",       "tip_v2",   {}),
                ("v3",       "lbl_v3",       "tip_v3",   {})):
            lbl, val = self.info_labels[key]
            lbl.setText(t(label_key))
            tip = t(tip_key, **kw)
            lbl.setToolTip(tip)
            val.setToolTip(tip)

        self.plot_box.setTitle(t("box_plot"))
        self.plot_widget.setToolTip(t("plot_tip"))
        self.plot_widget.setLabel('bottom', t("axis_x"), color=COLORS['text_primary'])
        self.plot_widget.setLabel('left', t("axis_y"), color=COLORS['text_primary'])

        self.help_menu.setTitle(t("menu_help"))
        self.lang_menu.setTitle(t("menu_language"))
        for act, key in self.help_actions:
            act.setText(t(key))
        self.act_update.setText(t("act_update"))
        self.act_about.setText(t("act_about"))

        # légende et repères du graphe
        self._retranslate_plot()

    def _retranslate_plot(self):
        labels = {'comoving': t("curve_comoving"), 'luminosity': t("curve_luminosity"),
                  'angular_diameter': t("curve_angular"), 'lookback': t("curve_lookback")}
        if getattr(self, "legend", None) is not None:
            self.plot_widget.plotItem.legend.clear()
            for key, item in self.curve_items.items():
                self.legend.addItem(item, labels[key])
            self.legend.addItem(self.shoes_items['comoving'],
                                t("curve_shoes", name=labels['comoving']))
        if getattr(self, "line_damax", None) is not None:
            self.line_damax.label.setFormat(t("marker_damax"))
        if getattr(self, "line_horizon", None) is not None:
            self.line_horizon.label.setFormat(t("marker_horizon"))

    # -------------------------------------------------------------- graphique

    def _build_plot(self):
        pw = self.plot_widget
        pw.setLogMode(x=True, y=True)
        pw.showGrid(x=True, y=True, alpha=0.25)

        for axis_name in ('left', 'bottom'):
            ax = pw.getAxis(axis_name)
            ax.setPen(pg.mkPen(COLORS['border_light']))
            ax.setTextPen(COLORS['text_secondary'])

        self.z_grid = np.logspace(-3, np.log10(1500), 600)
        self.curves = curves(self.z_grid)

        self.curve_items = {}
        self.legend = pw.addLegend(offset=(10, 10),
                                   labelTextColor=COLORS['text_primary'],
                                   brush=pg.mkBrush(COLORS['bg_medium']))
        for key in ('comoving', 'luminosity', 'angular_diameter', 'lookback'):
            pen = pg.mkPen(QColor(self.DISTANCE_COLORS[key]), width=2.2)
            self.curve_items[key] = pw.plot(self.z_grid, self.curves[key], pen=pen)

        # mêmes courbes en cosmologie SH0ES (pointillé), masquées par défaut
        self.shoes_items = {}
        self._shoes_key = None
        for key in ('comoving', 'luminosity', 'angular_diameter', 'lookback'):
            pen = pg.mkPen(QColor(self.DISTANCE_COLORS[key]), width=1.4,
                           style=Qt.PenStyle.DotLine)
            item = pw.plot([], [], pen=pen)
            item.setVisible(False)
            self.shoes_items[key] = item

        for z_ref, lbl in [(1.0, "z=1"), (10.6, "GN-z11"), (1089.8, "CMB")]:
            line = pg.InfiniteLine(pos=np.log10(z_ref), angle=90,
                                   pen=pg.mkPen(COLORS['border_light'], width=1,
                                                style=Qt.PenStyle.DotLine),
                                   label=lbl,
                                   labelOpts={'color': COLORS['text_secondary'],
                                              'fill': (0, 0, 0, 0), 'position': 0.97})
            pw.addItem(line)

        # repère du maximum de D_A — recalculé depuis les courbes, il suit Ωk
        self.line_damax = pg.InfiniteLine(
            pos=np.log10(Z_DA_MAX), angle=90,
            pen=pg.mkPen(COLORS['accent_purple'], width=1, style=Qt.PenStyle.DotLine),
            label="max D_A", labelOpts={'color': COLORS['accent_purple'],
                                        'fill': (0, 0, 0, 0), 'position': 0.80})
        pw.addItem(self.line_damax)
        self._update_damax_marker()

        # asymptotes horizontales
        self.line_ct0 = pg.InfiniteLine(
            pos=np.log10(T0_GYR), angle=0,
            pen=pg.mkPen(COLORS['success'], width=1, style=Qt.PenStyle.DashDotLine),
            label="c·t₀", labelOpts={'color': COLORS['success'],
                                     'fill': (0, 0, 0, 0), 'position': 0.05})
        pw.addItem(self.line_ct0)
        self.line_horizon = pg.InfiniteLine(
            pos=np.log10(PARTICLE_HORIZON_GLYR), angle=0,
            pen=pg.mkPen(COLORS['accent_cyan'], width=1, style=Qt.PenStyle.DashDotLine),
            label="horizon", labelOpts={'color': COLORS['accent_cyan'],
                                        'fill': (0, 0, 0, 0), 'position': 0.05})
        pw.addItem(self.line_horizon)

        self.marker_v = pg.InfiniteLine(pos=np.log10(2.34), angle=90,
                                        pen=pg.mkPen(QColor(COLORS['accent_pink']),
                                                     width=1.6, style=Qt.PenStyle.DashLine))
        pw.addItem(self.marker_v)

        self.marker_pts = {}
        for key in ('comoving', 'luminosity', 'angular_diameter', 'lookback'):
            scatter = pg.ScatterPlotItem(
                size=11, brush=pg.mkBrush(QColor(self.DISTANCE_COLORS[key])),
                pen=pg.mkPen(QColor(COLORS['text_primary']), width=1.2), symbol='o')
            pw.addItem(scatter)
            self.marker_pts[key] = scatter

    def _update_damax_marker(self) -> float:
        """Position du maximum de D_A, lue sur la courbe courante (suit Ωk)."""
        z_max = float(self.z_grid[int(np.argmax(self.curves["angular_diameter"]))])
        self.line_damax.setPos(np.log10(z_max))
        return z_max

    def _adapt_axes(self, z: float):
        """Zoom the X window around current z; Y set from the visible curves."""
        if z <= 0:
            x_lo, x_hi = 0.001, 5.0
        else:
            x_lo = max(0.001, z / 30.0)
            x_hi = min(1500.0, max(z * 8.0, x_lo * 50.0))
        self.plot_widget.setXRange(np.log10(x_lo), np.log10(x_hi), padding=0.02)

        mask = (self.z_grid >= x_lo) & (self.z_grid <= x_hi)
        if mask.any():
            visible = np.concatenate([c[mask] for c in self.curves.values()])
            visible = visible[visible > 0]
            if visible.size:
                self.plot_widget.setYRange(np.log10(visible.min() * 0.6),
                                           np.log10(visible.max() * 1.7), padding=0.0)

    # ------------------------------------------------- réactions aux contrôles

    def on_curvature_changed(self):
        ok = self.ok_spin.value()
        self.curves = curves(self.z_grid, Ok=ok)
        for key, item in self.curve_items.items():
            item.setData(self.z_grid, self.curves[key])
        self._update_damax_marker()
        self.row_trans.setVisible(abs(ok) > 1e-12)
        if self.chk_shoes.isChecked():
            self._ensure_shoes_curves()
        self.recompute()

    def on_shoes_toggled(self, checked: bool):
        if checked:
            self._ensure_shoes_curves()
        for item in self.shoes_items.values():
            item.setVisible(checked)
        self.recompute()

    def _ensure_shoes_curves(self):
        ok = self.ok_spin.value()
        key = round(ok, 6)
        if self._shoes_key == key:
            return
        data = curves(self.z_grid, Ok=ok, H0=H0_SHOES)
        for k, item in self.shoes_items.items():
            item.setData(self.z_grid, data[k])
        self._shoes_key = key

    # ------------------------------------------------------ calcul et affichage

    def recompute(self):
        z = self.z_spin.value()
        ok = self.ok_spin.value()
        shoes = self.chk_shoes.isChecked()
        d = compute(z, Ok=ok, with_shoes=shoes)
        s = d["sigma"]

        def alt(key: str, kind: str = "distance") -> str | None:
            if not shoes or not d[key]:
                return None
            v = d["shoes"][key]
            txt = format_distance(v) if kind == "distance" else format_time(v)
            return t("shoes_prefix", value=txt, pct=d["shoes"]["ecart_pct"][key])

        self.row_comov.set_value(format_pm(d["comoving"], s["comoving"]), alt("comoving"))
        self.row_trans.set_value(format_pm(d["transverse"], s["transverse"]), alt("transverse"))
        self.row_lum.set_value(format_pm(d["luminosity"], s["luminosity"]), alt("luminosity"))
        self.row_ang.set_value(format_pm(d["angular_diameter"], s["angular_diameter"]),
                               alt("angular_diameter"))
        self.row_look.set_value(format_pm(d["lookback"], s["lookback"]), alt("lookback"))

        self.lbl_lookback.setText(
            format_pm(d["lookback_gyr"], s["lookback_gyr"], "time")
            + (f"   ·  SH0ES {format_time(d['shoes']['lookback_gyr'])}" if shoes else ""))
        self.lbl_age.setText(
            format_pm(d["age_at_z"], s["age_at_z"], "time")
            + t("age_t0_suffix", t0=d["t0_model"])
            + (f"  ·  SH0ES {format_time(d['shoes']['age_at_z'])}" if shoes else ""))
        self.lbl_a.setText(fmt_num(d["a"], 5, thousands=False) + t("scale_suffix", factor=1 + z))
        self.lbl_E.setText(f"{fmt_num(d['E'], 4)}   →  H(z) = {fmt_num(d['H_z'], 1)} km/s/Mpc")

        self.lbl_v1.setText(f"{fmt_num(d['v_cz'], 0)} km/s   ({fmt_num(d['v_cz'] / C_KMS, 3, thousands=False)} c)")
        self.lbl_v2.setText(f"{fmt_num(d['v_sr'], 0)} km/s   ({fmt_num(d['v_sr'] / C_KMS, 3, thousands=False)} c)")
        self.lbl_v3.setText(f"{fmt_num(d['v_flrw'], 0)} km/s   ({fmt_num(d['v_flrw'] / C_KMS, 3, thousands=False)} c)")

        somme = d["lookback_gyr"] + d["age_at_z"]
        eth = (d["luminosity"] / ((1 + z) ** 2 * d["angular_diameter"])
               if z > 0 and d["angular_diameter"] > 0 else 1.0)
        msg = t("status", z=z, sum=somme, dev=abs(somme - d["t0_model"]) * 1e6, eth=eth,
                pct=d["sigma_pct"]["comoving"], pct_indep=d["sigma_indep_pct"]["comoving"])
        if abs(ok) > 1e-12:
            msg += t("status_ok", ok=ok)
        self.statusBar().showMessage(msg)

        log_z = np.log10(max(z, 1e-6))
        self.marker_v.setPos(log_z)
        for key, scatter in self.marker_pts.items():
            val_glyr = d[key] / 1e9
            if val_glyr > 0:
                scatter.setData([log_z], [np.log10(val_glyr)])
            else:
                scatter.setData([], [])

        self._adapt_axes(z)


# ============================================================================
# ENTRY POINT
# ============================================================================

SETTINGS_ORG, SETTINGS_APP = "cosmologie-redshift", "CosmologicalDistanceCalculator"


def _saved_language() -> str | None:
    """Langue choisie lors d'une session précédente, si elle a été mémorisée."""
    value = QSettings(SETTINGS_ORG, SETTINGS_APP).value("language")
    return value if value in LANGUAGE_NAMES else None


def _save_language(code: str) -> None:
    QSettings(SETTINGS_ORG, SETTINGS_APP).setValue("language", code)


def main():
    argv = list(sys.argv)
    lang = None
    if "--lang" in argv:
        i = argv.index("--lang")
        if i + 1 < len(argv):
            lang = argv[i + 1]
            del argv[i:i + 2]

    # Priorité : --lang, puis COSMO_LANG, puis le choix mémorisé, puis la
    # langue du système (anglais si elle n'est ni française ni détectable).
    if lang is None and not os.environ.get("COSMO_LANG"):
        lang = _saved_language()
    set_language(lang)

    app = QApplication(argv)
    app.setStyle("Fusion")
    apply_cosmic_theme(app)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
