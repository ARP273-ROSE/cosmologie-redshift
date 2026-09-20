#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
VERSION ET VÉRIFICATION DES MISES À JOUR / VERSION AND UPDATE CHECK
================================================================================
Le programme interroge l'API publique des releases GitHub pour savoir si une
version plus récente existe. La requête :

  * est faite UNE fois par démarrage, dans un fil séparé, avec un délai
    d'expiration court : elle ne bloque jamais l'interface ;
  * échoue silencieusement s'il n'y a pas de réseau ;
  * n'envoie aucune donnée personnelle (simple GET anonyme) ;
  * peut être désactivée avec la variable d'environnement
    COSMO_NO_UPDATE_CHECK=1.

The check runs once per start, in a background thread, with a short timeout;
it fails silently offline, sends no personal data, and can be disabled with
COSMO_NO_UPDATE_CHECK=1.
================================================================================
"""

from __future__ import annotations

import json
import os
import re
import urllib.request

__all__ = ["__version__", "VERSION", "GITHUB_REPO", "RELEASES_URL", "DOWNLOAD_URL",
           "latest_version", "is_newer", "check_enabled"]

def _read_version() -> str:
    """Lit le fichier VERSION, à la racine du dépôt : une seule source.

    Écrire le numéro à deux endroits finit toujours par les faire diverger, et
    une application qui se croit en retard sur elle-même propose une mise à
    jour à chaque démarrage, sans fin.

    Reads the VERSION file at the repository root: a single source of truth.
    """
    from pathlib import Path as _Path
    here = _Path(__file__).resolve().parent
    for base in (here.parent, here):
        try:
            text = (base / "VERSION").read_text(encoding="utf-8").strip()
            if text:
                return text
        except OSError:
            continue
    return ""


__version__ = _read_version()
VERSION = __version__

GITHUB_REPO = "ARP273-ROSE/cosmologie-redshift"
API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
RELEASES_URL = f"https://github.com/{GITHUB_REPO}/releases"
# Lien permanent vers l'exécutable Windows, quelle que soit la version.
DOWNLOAD_URL = (f"https://github.com/{GITHUB_REPO}/releases/latest/download/"
                "CosmologicalDistanceCalculator-windows.exe")

_TIMEOUT = 4.0


def check_enabled() -> bool:
    return os.environ.get("COSMO_NO_UPDATE_CHECK", "").strip() not in ("1", "true", "yes")


def _parse(tag: str) -> tuple:
    """« v1.2.3 » -> (1, 2, 3). Les suffixes (-beta…) sont ignorés pour l'ordre."""
    nums = re.findall(r"\d+", tag or "")
    return tuple(int(n) for n in nums[:3]) or (0,)


def is_newer(remote: str, local: str = __version__) -> bool:
    return _parse(remote) > _parse(local)


def latest_version(timeout: float = _TIMEOUT) -> str | None:
    """Dernier tag publié, ou None si indisponible (hors ligne, quota, etc.)."""
    if not check_enabled():
        return None
    req = urllib.request.Request(
        API_URL,
        headers={"Accept": "application/vnd.github+json",
                 "User-Agent": f"cosmologie-redshift/{__version__}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return (data.get("tag_name") or "").lstrip("vV") or None
    except Exception:                      # réseau, DNS, quota, JSON… : sans bruit
        return None


if __name__ == "__main__":
    print(f"version locale / local version : {__version__}")
    remote = latest_version()
    if remote is None:
        print("dernière version : indisponible (hors ligne ?)")
    else:
        print(f"dernière version publiée / latest release : {remote}")
        print("mise à jour disponible" if is_newer(remote) else "à jour / up to date")
