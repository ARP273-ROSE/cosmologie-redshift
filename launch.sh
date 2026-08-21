#!/usr/bin/env bash
# ============================================================================
#  Calculateur de distances cosmologiques — lanceur Linux / macOS
#
#    ./launch.sh                 lance l'interface graphique
#    ./launch.sh console         version console, mode interactif
#    ./launch.sh console 2.34    calcul direct pour z = 2.34
#    ./launch.sh table           table des huit presets
#    ./launch.sh check           auto-test du noyau de calcul
#    ./launch.sh update          met à jour les dépendances du venv
#
#  Crée le venv et installe les dépendances au premier lancement.
#  Équivalent Windows : launch.bat
#
#  Si Python 3 est absent, le lanceur propose de l'installer (Homebrew sous
#  macOS, gestionnaire de paquets sous Linux). COSMO_AUTO_INSTALL=1 accepte
#  sans poser de question.
#
#  Variable utile : COSMO_VENV=/chemin/venv  pour réutiliser un venv existant
#  (ex. : COSMO_VENV=~/venvs/cosmo ./launch.sh check).
# ============================================================================
set -euo pipefail

cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}" 2>/dev/null || echo "${BASH_SOURCE[0]}")")"

VENV="${COSMO_VENV:-.venv}"
PY="$VENV/bin/python"
STAMP="$VENV/.deps-ok"
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8

find_python() {
    for candidate in python3 python; do
        if command -v "$candidate" >/dev/null 2>&1; then
            # macOS fournit un « python3 » factice qui ne fait qu'ouvrir une
            # fenêtre d'installation : on vérifie qu'il s'exécute vraiment.
            if "$candidate" -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" \
                 >/dev/null 2>&1; then
                echo "$candidate"; return 0
            fi
        fi
    done
    return 1
}

confirm() {
    # Renvoie 0 si l'utilisateur accepte. COSMO_AUTO_INSTALL=1 accepte d'office.
    [ "${COSMO_AUTO_INSTALL:-}" = "1" ] && return 0
    printf "  %s [O/n] " "$1"
    read -r answer </dev/tty 2>/dev/null || return 1
    case "$answer" in [nN]*) return 1 ;; *) return 0 ;; esac
}

install_python() {
    # Installe Python 3 avec le gestionnaire de paquets du système.
    local os cmd
    os=$(uname -s)

    if [ "$os" = "Darwin" ]; then
        if command -v brew >/dev/null 2>&1; then
            cmd="brew install python"
        else
            echo "  Homebrew n'est pas installé ; il sert à installer Python proprement."
            confirm "Installer Homebrew puis Python ?" || return 1
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" || return 1
            for brewbin in /opt/homebrew/bin/brew /usr/local/bin/brew; do
                [ -x "$brewbin" ] && eval "$($brewbin shellenv)" && break
            done
            cmd="brew install python"
        fi
    elif command -v apt-get >/dev/null 2>&1; then
        cmd="sudo apt-get update && sudo apt-get install -y python3 python3-venv python3-pip"
    elif command -v dnf >/dev/null 2>&1; then
        cmd="sudo dnf install -y python3 python3-pip"
    elif command -v pacman >/dev/null 2>&1; then
        cmd="sudo pacman -Sy --noconfirm python python-pip"
    elif command -v zypper >/dev/null 2>&1; then
        cmd="sudo zypper install -y python3 python3-pip"
    elif command -v apk >/dev/null 2>&1; then
        cmd="sudo apk add python3 py3-pip"
    else
        echo "  [ERREUR] Gestionnaire de paquets non reconnu." >&2
        echo "  Installez Python 3.9+ depuis https://www.python.org/downloads/" >&2
        return 1
    fi

    echo
    echo "  Python 3 est absent. Commande d'installation prévue :"
    echo "      $cmd"
    confirm "Lancer cette installation maintenant ?" || {
        echo "  Installation annulée. Python 3.9+ reste nécessaire."
        return 1
    }
    echo "  Installation en cours (le mot de passe administrateur peut être demandé)..."
    eval "$cmd" || return 1
    hash -r 2>/dev/null || true
    return 0
}

ensure_python() {
    # Renvoie sur stdout un interpréteur utilisable, en l'installant au besoin.
    local py
    if py=$(find_python); then echo "$py"; return 0; fi
    install_python >&2 || return 1
    if py=$(find_python); then echo "$py"; return 0; fi
    echo "  [ERREUR] Python reste introuvable après installation." >&2
    return 1
}

# --- modes spéciaux (avant toute création de venv) --------------------------
case "${1:-}" in
    reset)
        echo "  Suppression de $VENV ..."
        rm -rf "$VENV"
        echo "  Fait. Relancez ./launch.sh pour tout réinstaller."
        exit 0
        ;;
    system)
        BOOTSTRAP=$(ensure_python) || exit 1
        echo "  Mode SANS venv : installation pour l'utilisateur courant."
        "$BOOTSTRAP" -m pip install --user -r requirements.txt || {
            echo "  [ERREUR] Installation impossible même en --user." >&2
            echo "  (distributions récentes : environnement « externally managed » —" >&2
            echo "   utilisez plutôt le venv, ou pipx, ou --break-system-packages)" >&2
            exit 1
        }
        exec "$BOOTSTRAP" programme/redshift_distance_gui.py
        ;;
    doctor)
        echo "==========================================================================="
        echo "  DIAGNOSTIC"
        echo "==========================================================================="
        echo "  Dossier courant : $PWD"
        echo "  Système         : $(uname -srm)"
        printf "  Écriture ici    : "
        if touch .__write_test.tmp 2>/dev/null; then echo "OK"; rm -f .__write_test.tmp
        else echo "REFUSÉE  <-- dossier protégé ou montage en lecture seule"; fi
        echo
        echo "  --- Python système ---"
        for c in python3 python; do
            command -v "$c" >/dev/null 2>&1 && echo "  $c -> $(command -v $c) ($($c --version 2>&1))"
        done
        echo
        echo "  --- venv ($VENV) ---"
        if [ -x "$PY" ]; then
            echo "  python du venv : $("$PY" --version 2>&1)"
            "$PY" -c "import numpy, scipy, astropy, PyQt6, pyqtgraph; print('  dépendances : toutes présentes')" \
                2>/dev/null || echo "  dépendances : incomplètes"
        else
            echo "  absent ou non exécutable"
        fi
        echo
        echo "  --- affichage ---"
        echo "  DISPLAY='${DISPLAY:-}'  WAYLAND_DISPLAY='${WAYLAND_DISPLAY:-}'  QT_QPA_PLATFORM='${QT_QPA_PLATFORM:-}'"
        echo "==========================================================================="
        exit 0
        ;;
esac

# --- 1. venv ----------------------------------------------------------------
if [ ! -x "$PY" ]; then
    BOOTSTRAP=$(ensure_python) || exit 1
    echo "  Création de l'environnement virtuel dans $VENV ..."
    if ! "$BOOTSTRAP" -m venv "$VENV" >/dev/null 2>&1; then
        echo "  Le module venv est absent ; tentative d'installation..."
        if command -v apt-get >/dev/null 2>&1; then
            PYV=$("$BOOTSTRAP" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
            confirm "Installer python3-venv ?" && \
                sudo apt-get install -y "python${PYV}-venv" python3-venv 2>/dev/null || true
        fi
        "$BOOTSTRAP" -m venv "$VENV" || {
            echo "  [ERREUR] Création du venv impossible." >&2
            echo "  Debian/Ubuntu : sudo apt install python3-venv" >&2
            exit 1
        }
    fi
fi

# le venv existe : vérifier qu'il s'exécute réellement
if ! "$PY" -c "import sys" >/dev/null 2>&1; then
    echo "  [ERREUR] Le python de $VENV refuse de s'exécuter." >&2
    echo "  Essayez : ./launch.sh reset   puis relancez  (ou ./launch.sh doctor)" >&2
    exit 1
fi

# --- 2. dépendances ---------------------------------------------------------
[ "${1:-}" = "update" ] && rm -f "$STAMP"
if [ ! -f "$STAMP" ]; then
    echo "  Installation des dépendances (quelques minutes la première fois) ..."
    "$PY" -m pip install --upgrade pip --quiet
    "$PY" -m pip install -r requirements.txt || {
        echo "  [ERREUR] Installation des dépendances impossible." >&2
        exit 1
    }
    touch "$STAMP"
fi
if [ "${1:-}" = "update" ]; then
    echo "  Dépendances à jour."
    exit 0
fi

# --- 3. lancement -----------------------------------------------------------
case "${1:-gui}" in
    console) shift; exec "$PY" programme/redshift_distance_calculator.py "$@" ;;
    table)   exec "$PY" programme/redshift_distance_calculator.py --table ;;
    check)   exec "$PY" programme/cosmo_core.py ;;
    gui)
        # Sans serveur d'affichage, Qt échoue avec un message obscur : on prévient.
        if [ -z "${DISPLAY:-}" ] && [ -z "${WAYLAND_DISPLAY:-}" ] \
           && [ "$(uname -s)" != "Darwin" ] && [ -z "${QT_QPA_PLATFORM:-}" ]; then
            echo "  [INFO] Aucun serveur d'affichage détecté (DISPLAY vide)."
            echo "         Utilisez './launch.sh console' ou définissez"
            echo "         QT_QPA_PLATFORM=offscreen pour un test sans écran."
            exit 1
        fi
        exec "$PY" programme/redshift_distance_gui.py
        ;;
    help|-h|--help)
        cat <<'USAGE'
  Usage :
    ./launch.sh                 interface graphique
    ./launch.sh console [z]     version console (interactif si z absent)
    ./launch.sh table           table des huit presets
    ./launch.sh check           auto-test du noyau de calcul
    ./launch.sh update          met à jour les dépendances
    ./launch.sh reset           supprime le venv et repart de zéro
    ./launch.sh system          se passe du venv (pip install --user)
    ./launch.sh doctor          diagnostic complet

  COSMO_VENV=/chemin/venv       réutilise un venv existant au lieu de ./.venv\n  COSMO_AUTO_INSTALL=1          installe Python sans rien demander
USAGE
        ;;
    *)
        echo "  Commande inconnue : $1  (voir ./launch.sh help)" >&2
        exit 2
        ;;
esac
