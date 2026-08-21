"""Recherche d'un objet dans SIMBAD à partir de son nom.
Look up an object in SIMBAD by name.

Le but est qu'un nom tapé de mémoire suffise : « m31 », « M 31 », « ngc224 »,
« Andromeda », « 3c273 », « sombrero » désignent tous quelque chose de précis
pour SIMBAD, mais pas sous la même forme. Trois niveaux sont enchaînés, du
moins coûteux au plus large :

  1. la saisie est envoyée telle quelle au résolveur de noms de SIMBAD, qui
     absorbe déjà l'essentiel (casse, espaces, « messier » pour « M ») ;
  2. si cela ne donne rien, des variantes locales sont essayées : séparateurs
     ajoutés ou retirés, abréviations de catalogues développées, accents ôtés ;
  3. en dernier ressort, les identifiants sont fouillés par sous-chaîne, ce qui
     retrouve un objet dont le nom n'a été tapé qu'en partie.

Dès que le résultat est ambigu — plusieurs objets, ou un seul dont le nom ne
ressemble pas à ce qui a été demandé — tous les candidats sont renvoyés pour
que l'utilisateur tranche lui-même. Le piège est réel : SIMBAD résout « GNz11 »
en « Z 49-122 », une galaxie proche sans aucun rapport avec « GN-z11 ».

Aucune dépendance : uniquement la bibliothèque standard.
"""
from __future__ import annotations

import re
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field

SIMBAD_HOST = "https://simbad.u-strasbg.fr/simbad"
TIMEOUT = 25.0
MAX_CANDIDATES = 15
USER_AGENT = "CosmologicalDistanceCalculator (+https://github.com/ARP273-ROSE/cosmologie-redshift)"

# Longueur minimale avant d'autoriser la fouille par sous-chaîne : en deçà, le
# motif balaierait des millions d'identifiants pour un résultat inexploitable.
MIN_SUBSTRING_LEN = 5


class SimbadError(RuntimeError):
    """SIMBAD est injoignable ou répond de travers."""


@dataclass
class SimbadObject:
    """Un objet renvoyé par SIMBAD."""

    name: str
    otype: str = ""
    redshift: float | None = None
    ra: float | None = None
    dec: float | None = None
    matched: str = ""          # identifiant qui a effectivement répondu
    aliases: list[str] = field(default_factory=list)

    def label(self) -> str:
        bits = [self.name]
        if self.otype:
            bits.append(f"({self.otype})")
        if self.redshift is not None:
            bits.append(f"z = {self.redshift:g}")
        return "  ".join(bits)


# --------------------------------------------------------------------------
# Normalisation et variantes de noms
# --------------------------------------------------------------------------

# Abréviations couramment tapées, développées vers la forme attendue par SIMBAD.
_CATALOGUES = {
    "messier": "M", "m": "M",
    "ngc": "NGC", "ic": "IC", "ugc": "UGC", "ugca": "UGCA",
    "pgc": "PGC", "leda": "LEDA", "eso": "ESO", "arp": "Arp",
    "abell": "ACO", "aco": "ACO", "sh2": "SH2", "sh": "SH2",
    "ldn": "LDN", "lbn": "LBN", "barnard": "Barnard", "b": "Barnard",
    "caldwell": "C", "collinder": "Cr", "melotte": "Mel",
    "hd": "HD", "hip": "HIP", "hr": "HR", "gj": "GJ", "sao": "SAO",
    "3c": "3C", "4c": "4C", "pks": "PKS", "qso": "QSO",
    "sdss": "SDSS", "2mass": "2MASS", "wise": "WISE", "iras": "IRAS",
    "mrk": "Mrk", "markarian": "Mrk", "vv": "VV", "hcg": "HCG",
}

_ACCENTS = str.maketrans("", "", "̧̀́̂̃̈̊")


def _strip_accents(text: str) -> str:
    return unicodedata.normalize("NFD", text).translate(_ACCENTS)


def flatten(text: str) -> str:
    """Réduit un nom à ses lettres et chiffres, en minuscules.

    Sert à comparer deux noms sans se soucier de la casse ni des séparateurs :
    « M 31 », « m31 » et « M-31 » se ramènent tous à « m31 ».
    """
    return re.sub(r"[^a-z0-9]", "", _strip_accents(text).lower())


def name_variants(raw: str) -> list[str]:
    """Formes successives à essayer, de la plus fidèle à la plus retravaillée."""
    cleaned = _strip_accents(raw).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    if not cleaned:
        return []

    out: list[str] = [cleaned]

    def add(candidate: str) -> None:
        candidate = candidate.strip()
        if candidate and candidate not in out:
            out.append(candidate)

    # Séparateurs : ajoutés, retirés, uniformisés.
    add(cleaned.replace("-", " ").replace("_", " "))
    add(re.sub(r"[\s_]+", "", cleaned))
    add(re.sub(r"([A-Za-z])(\d)", r"\1 \2", cleaned))     # ngc224 -> ngc 224
    add(re.sub(r"([A-Za-z])[\s_-]+(\d)", r"\1\2", cleaned))  # ngc 224 -> ngc224

    # Préfixe de catalogue reconnu et développé. Certains commencent par un
    # chiffre (3C, 4C, 2MASX), d'où les deux formes acceptées.
    match = (re.match(r"^([A-Za-z][A-Za-z0-9]*)[\s_-]*(.*)$", cleaned)
             or re.match(r"^(\d+[A-Za-z]+)[\s_-]*(.*)$", cleaned))
    if match:
        head, tail = match.group(1).lower(), match.group(2).strip()
        expanded = _CATALOGUES.get(head)
        if expanded and tail:
            add(f"{expanded} {tail}")
            add(f"{expanded}{tail}")
    # Cas « m31 » : lettre et nombre collés, sans séparateur à couper.
    match = re.match(r"^([A-Za-z]+)(\d.*)$", re.sub(r"[\s_-]+", "", cleaned))
    if match:
        expanded = _CATALOGUES.get(match.group(1).lower())
        if expanded:
            add(f"{expanded} {match.group(2)}")

    add(cleaned.upper())
    return out[:10]


# --------------------------------------------------------------------------
# Accès réseau
# --------------------------------------------------------------------------

def _fetch(url: str, timeout: float) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        raise SimbadError(f"HTTP {exc.code}") from exc
    except Exception as exc:                       # réseau, DNS, délai dépassé
        raise SimbadError(str(exc)) from exc


def _as_float(text: str) -> float | None:
    text = text.strip()
    if not text or text in {"~", "--"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


# -- 1 et 2. résolution de noms (sim-script) --------------------------------

_COLUMNS = "%IDLIST(1)\t%OTYPE(V)\t%RV(Z)\t%COO(d;A)\t%COO(d;D)"
# %IDLIST[%*,] déroule tous les identifiants connus de l'objet, séparés par des
# virgules : c'est ce qui permet de reconnaître que « ngc 224 » désigne bien
# M 31. La liste est longue, donc réservée à la résolution d'un seul nom.
_SCRIPT_FORMAT = 'format object f1 "%s"\n' % _COLUMNS
_SCRIPT_FORMAT_FULL = 'format object f1 "%s\t%%IDLIST[%%*,]"\n' % _COLUMNS


def _parse_script(payload: str) -> list[SimbadObject]:
    """Lit la section de données d'une réponse sim-script."""
    marker = payload.find("::data:")
    if marker < 0:
        return []                      # aucun objet : SIMBAD n'a listé que les erreurs
    body = payload[marker:].split("\n", 1)[-1]

    found: list[SimbadObject] = []
    for line in body.splitlines():
        line = line.rstrip()
        if not line.strip() or line.startswith(":") or "\t" not in line:
            continue
        if line.lstrip().startswith(("format ", "query ", "!!", "error")):
            continue                   # écho du script, pas un résultat
        cells = (line.split("\t") + [""] * 6)[:6]
        name = cells[0].strip()
        if not name:
            continue
        found.append(SimbadObject(
            name=name,
            otype=cells[1].strip(),
            redshift=_as_float(cells[2]),
            ra=_as_float(cells[3]),
            dec=_as_float(cells[4]),
            matched=name,
            aliases=[a.strip() for a in cells[5].split(",") if a.strip()],
        ))
    return found


def _query_ids(identifiers: list[str], timeout: float) -> list[SimbadObject]:
    """Résout une liste d'identifiants en un seul appel."""
    identifiers = [i for i in identifiers if i.strip()]
    if not identifiers:
        return []
    header = _SCRIPT_FORMAT_FULL if len(identifiers) == 1 else _SCRIPT_FORMAT
    script = header + "".join(f"query id {i}\n" for i in identifiers)
    url = f"{SIMBAD_HOST}/sim-script?" + urllib.parse.urlencode({"script": script})
    return _parse_script(_fetch(url, timeout))


# -- 3. joker sur les identifiants (sim-id) ---------------------------------

_OBJECT_LINE = re.compile(r"^Object\s+(.+?)\s+---", re.M)
_TABLE_LINE = re.compile(r"^\s*\d+\s*\|\s*(\S[^|]*?)\s*\|", re.M)


def _wildcard_ids(name: str, timeout: float) -> list[str]:
    """Identifiants contenant le nom demandé, casse indifférente.

    Le joker de SIMBAD ignore la casse, ce que le langage TAP ne sait pas
    faire : c'est lui qui retrouve « [OBV2016] GN-z11 » à partir de « gn-z11 ».
    Il refuse en revanche les désignations de coordonnées tronquées, d'où la
    fouille TAP qui prend le relais juste après.
    """
    if len(flatten(name)) < MIN_SUBSTRING_LEN:
        return []
    url = f"{SIMBAD_HOST}/sim-id?" + urllib.parse.urlencode({
        "Ident": f"*{name}*", "NbIdent": "wild",
        "output.format": "ASCII", "output.max": str(MAX_CANDIDATES)})
    payload = _fetch(url, timeout)
    ids = _OBJECT_LINE.findall(payload) or _TABLE_LINE.findall(payload)
    return [i.strip() for i in ids[:MAX_CANDIDATES] if i.strip()]


# -- 4. fouille des identifiants par sous-chaîne (TAP / ADQL) ----------------

_TAP_QUERY = (
    "SELECT TOP {n} b.main_id, o.otype_longname, b.rvz_redshift, b.ra, b.dec, i.id "
    "FROM ident AS i JOIN basic AS b ON i.oidref = b.oid "
    "LEFT JOIN otypedef AS o ON b.otype = o.otype "
    "WHERE {where}"
)


def _like_patterns(name: str) -> list[str]:
    """Motifs LIKE couvrant la casse, que le langage TAP de SIMBAD ignore.

    ADQL n'offre ici ni ILIKE ni LOWER(), et LIKE distingue les majuscules. Les
    trois casses usuelles sont donc essayées telles quelles ; remplacer les
    lettres par le joker « _ » couvrirait toutes les casses d'un coup mais
    rendrait le motif si peu sélectif que la réponse, tronquée, ne contiendrait
    plus l'objet cherché. Les séparateurs, eux, deviennent « % » : « ulas
    j1120 » retrouve « ULAS J112001.48+064124.3 ».
    """
    core = re.sub(r"[\s_-]+", "%", name.strip())
    # Un séparateur peut aussi manquer là où SIMBAD en met un : « GNz11 » doit
    # atteindre « GNZ 11 » comme « GN-z11 ». Les frontières lettre/chiffre et
    # minuscule/majuscule deviennent donc des jokers elles aussi.
    core = re.sub(r"(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])|(?<=[a-z])(?=[A-Z])",
                  "%", core).replace("%%", "%")
    forms: list[str] = []
    for form in (core, core.upper(), core.title()):
        if form and form not in forms:
            forms.append(form)
    return ["%" + f + "%" for f in forms[:3]]


def _tap_search(name: str, timeout: float) -> list[SimbadObject]:
    """Cherche le nom comme sous-chaîne de n'importe quel identifiant."""
    if len(flatten(name)) < MIN_SUBSTRING_LEN:
        return []                      # trop court : la fouille serait sans fin
    patterns = _like_patterns(name)
    where = " OR ".join("i.id LIKE '%s'" % p.replace("'", "''") for p in patterns)
    query = _TAP_QUERY.format(n=MAX_CANDIDATES * 2, where="(%s)" % where)
    url = f"{SIMBAD_HOST}/sim-tap/sync?" + urllib.parse.urlencode({
        "request": "doQuery", "lang": "adql", "format": "text",
        "maxrec": str(MAX_CANDIDATES * 2), "query": query})
    payload = _fetch(url, timeout)

    target = flatten(name)
    found: list[SimbadObject] = []
    for line in payload.splitlines()[2:]:          # 2 lignes d'en-tête
        cells = [c.strip().strip('"') for c in line.split("|")]
        if len(cells) < 6 or not cells[0]:
            continue
        # Le joker « _ » élargit le motif : on revérifie ici que l'identifiant
        # trouvé contient bien ce qui a été demandé.
        if target not in flatten(cells[5]):
            continue
        found.append(SimbadObject(
            name=cells[0], otype=cells[1],
            redshift=_as_float(cells[2]),
            ra=_as_float(cells[3]), dec=_as_float(cells[4]),
            matched=cells[5],
        ))
    return found


# --------------------------------------------------------------------------
# Résolution
# --------------------------------------------------------------------------

def _merge(*groups: list[SimbadObject]) -> list[SimbadObject]:
    """Fusionne des listes en gardant l'ordre et un seul objet par nom."""
    out: dict[str, SimbadObject] = {}
    for group in groups:
        for obj in group:
            existing = out.get(obj.name)
            if existing is None:
                out[obj.name] = obj
            elif obj.matched and obj.matched not in existing.aliases:
                existing.aliases.append(obj.matched)
    return list(out.values())[:MAX_CANDIDATES]


def _match_rank(query: str, obj: SimbadObject) -> int:
    """0 si un identifiant de l'objet est exactement le nom demandé, 1 s'il le
    prolonge, 2 s'il le contient, 3 sinon. Sert à présenter d'abord, dans une
    liste de candidats, ceux qui collent le mieux à ce qui a été tapé."""
    asked = flatten(query)
    if not asked:
        return 3
    best = 3
    for known in (obj.name, obj.matched, *obj.aliases):
        flat = flatten(known)
        if not flat:
            continue
        if flat == asked:
            return 0
        if flat.startswith(asked):
            best = min(best, 1)
        elif asked in flat or flat in asked:
            best = min(best, 2)
    return best


def resolve(query: str, timeout: float = TIMEOUT) -> tuple[list[SimbadObject], str]:
    """Cherche un objet dans SIMBAD à partir d'un nom saisi librement.

    Renvoie (candidats, forme retenue) : aucune entrée si l'objet est
    introuvable, une seule quand la réponse est certaine, plusieurs quand il
    revient à l'utilisateur de choisir. Lève SimbadError si SIMBAD est
    injoignable.

    Qu'un nom soit reconnu par le résolveur de SIMBAD vaut certitude, même si
    l'identifiant renvoyé ne lui ressemble pas : « abell2218 » donne « ACO
    2218 », qui n'expose aucun identifiant « Abell ». La liste de candidats est
    donc réservée aux noms que SIMBAD ne reconnaît pas — ceux, précisément, où
    le doute est réel.
    """
    variants = name_variants(query)
    if not variants:
        return [], ""
    exact = variants[0]

    # 1. la saisie telle quelle : c'est SIMBAD qui fait le gros du travail.
    direct = _merge(_query_ids([exact], timeout))
    if direct:
        return direct, exact

    # 2. variantes locales, toutes en un seul aller-retour ; les réponses
    #    arrivent dans l'ordre des requêtes, donc de la plus fidèle à la plus
    #    retravaillée.
    found = _merge(_query_ids(variants[1:], timeout))
    if found:
        return found, exact

    # 3. joker sur les identifiants, insensible à la casse.
    try:
        ids = _wildcard_ids(exact, timeout)
        found = _merge(_query_ids(ids, timeout) if ids else [])
    except SimbadError:
        found = []

    # 4. fouille par sous-chaîne : lente, donc réservée au dernier recours.
    if not found:
        found = _merge(_tap_search(exact, timeout))

    found.sort(key=lambda o: _match_rank(exact, o))
    return found, exact


if __name__ == "__main__":                          # essai en ligne de commande
    import sys
    for arg in sys.argv[1:] or ["m31", "3c273", "gn-z11", "sombrero"]:
        try:
            objects, used = resolve(arg)
        except SimbadError as exc:
            print(f"{arg:<20} -> SIMBAD injoignable ({exc})")
            continue
        if not objects:
            print(f"{arg:<20} -> introuvable")
        elif len(objects) == 1:
            print(f"{arg:<20} -> {objects[0].label()}")
        else:
            print(f"{arg:<20} -> {len(objects)} candidats :")
            for obj in objects[:8]:
                print(f"{'':<24}{obj.label()}")
