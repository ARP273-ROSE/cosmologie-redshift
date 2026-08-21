# Journal des versions

*[English version](CHANGELOG.md)*

Ce fichier recense les changements notables du projet. Le format suit
[Keep a Changelog](https://keepachangelog.com/) et la numérotation respecte le
[versionnement sémantique](https://semver.org/).

---

## 1.3.2 — 21 août 2026

### Modifié

- **Une valeur hors domaine est désormais expliquée, non plafonnée en
  silence.** Saisir Ωk = 12 ramenait le champ à 0,05 sans un mot. La raison
  s'affiche maintenant à côté du champ : Ωk n'est pas une longueur mais la part
  de la courbure dans le contenu de l'univers, et toutes les parts réunies font
  1 — Ωk = 12 supposerait donc que les autres valent −11 en somme. Même
  traitement pour un redshift au-delà de 1500, où l'univers est opaque et où il
  n'y a plus rien à observer.
- L'explication suit la langue de l'interface et s'efface dès qu'une valeur
  recevable est saisie.
- L'infobulle de la courbure indique la plage acceptée et pourquoi elle est si
  étroite.

---

## 1.3.1 — 21 août 2026

### Corrigé

- **Les champs numériques acceptent enfin la frappe.** Saisir une valeur au
  clavier dans le champ de courbure — et, dans une moindre mesure, dans le
  champ `z` — était pratiquement impossible : le champ affichant déjà toutes
  ses décimales (`0,0000`), Qt refusait tout caractère supplémentaire, et
  l'intervalle étroit [−0,05 ; 0,05] rendait invalide presque toute valeur
  intermédiaire, puisqu'il faut bien taper `0` avant `0,01`. Chaque frappe
  était rejetée et le champ semblait réservé aux flèches.
- La validation accepte désormais tout ce qui ressemble à un nombre en cours de
  frappe, la valeur n'étant ramenée dans les bornes qu'à la validation. Une
  valeur hors domaine est ramenée à la limite la plus proche au lieu d'être
  abandonnée : taper 9 dans la courbure donne 0,05.
- Le contenu est sélectionné quand le champ prend le focus, de sorte que la
  frappe le remplace au lieu de s'insérer au milieu de la valeur courante.
- Le test sans écran reproduit maintenant le geste réel — donner le focus, puis
  taper, sans rien sélectionner au préalable. La version précédente appelait
  `selectAll()` d'abord, ce qu'aucun utilisateur ne fait, et c'est exactement
  pour cela que le défaut était passé inaperçu.

---

## 1.3.0 — 21 août 2026

### Ajouté

- **Recherche d'un objet par son nom.** Un champ `Objet` convertit un nom en
  redshift : `m31`, `M 31`, `ngc224`, `Messier 31`, `3c273`, `Sombrero`,
  `GN-z11` fonctionnent tous. La question est posée à
  [SIMBAD](https://simbad.u-strasbg.fr/), la base du Centre de données
  astronomiques de Strasbourg, dans un fil séparé : l'interface ne se fige
  jamais.
- Casse, espaces, tirets, soulignés et zéros de tête sont ignorés, et les
  abréviations de catalogues usuelles sont développées (`abell` → `ACO`,
  `messier` → `M`). Quand SIMBAD ne reconnaît pas le nom tel quel, des
  variantes locales sont essayées, puis les identifiants sont fouillés par
  sous-chaîne — c'est ainsi que `gn-z11` retrouve `[OBV2016] GN-z11`.
- **Une liste de choix dès que la réponse relève de la conjecture.** Les noms
  que SIMBAD résout lui-même sont appliqués directement ; ceux qui ne sont
  trouvés qu'en cherchant sont présentés en liste de candidats, le plus proche
  de la demande en tête.
- La version console reçoit `--object NOM`, et à l'invite interactive tout ce
  qui n'est pas un nombre est pris pour un nom d'objet.
- Nouvelle entrée d'aide, *Chercher un objet par son nom* (F7), dans les deux
  langues.
- Les objets sans redshift utilisable sont expliqués au lieu d'être appliqués
  en silence : absence de redshift dans SIMBAD, décalage vers le bleu (M 31
  s'approche), ou z < 0,03, où le mouvement propre dans l'amas l'emporte encore
  sur l'expansion.
- `verif_sage/test_simbad.py` contrôle hors ligne la normalisation des noms,
  les variantes engendrées, le classement des correspondances et les motifs de
  recherche, puis résout une série de noms réels dont la réponse est connue. La
  partie réseau est ignorée, sans faire échouer le contrôle, quand SIMBAD est
  injoignable.

### À savoir

SIMBAD répond exactement à ce qui est demandé, et les homonymes existent :
`GN-z11` est la galaxie lointaine à z = 10,6, tandis que `GNz11` sans tiret est
l'objet n° 11 du catalogue GNZ, à z = 0,053. L'identifiant qui a répondu est
toujours affiché à côté du champ.

---

## 1.2.0 — 21 août 2026

### Modifié

- **Le programme démarre désormais dans la langue de la machine**, anglais par
  défaut. La langue du système est lue dans les variables POSIX (`LC_ALL`,
  `LC_MESSAGES`, `LANGUAGE`, `LANG`), puis via l'API Windows
  (`GetUserDefaultUILanguage`), puis dans les réglages macOS (`AppleLocale`),
  puis dans le module `locale` de Python. Un système français donne du
  français ; toute autre langue, ou aucune locale lisible, donne de l'anglais.
- **La langue choisie dans le menu *Langue* est mémorisée** d'une session à
  l'autre : la détection automatique n'écrase plus un choix délibéré.
  `--lang` et `COSMO_LANG` restent prioritaires.
- Le `README.md` anglais devient la page d'accueil, avec un lien vers
  `README.fr.md`.
- Le journal de développement laisse place à ce journal des versions.

### Retiré

- Le rapport d'audit et toutes ses mentions. Les scripts de vérification
  (`verif_sage/`) et l'annexe de vérification du cours restent en place.

### Corrigé

- La détection de langue reposait sur `getdefaultlocale()`, déprécié et souvent
  vide sous Windows et macOS ; le programme retombait alors sur le français.

---

## 1.1.0 — 21 août 2026

Première version publique.

### Le programme

- Convertit un redshift `z` (0 à 1500) en quatre distances cosmologiques du
  modèle ΛCDM avec les paramètres Planck 2018 : comobile, de luminosité, de
  diamètre angulaire, de trajet de la lumière — plus la distance comobile
  transverse lorsque l'univers n'est pas plat.
- **Barres d'erreur à 1σ** sur chaque valeur, propagées de σ(H₀) = 0,42 et
  σ(Ωm) = 0,0056 **en tenant compte de leur corrélation** (ρ = −0,9763, déduite
  de la contrainte sur ω_m = Ωm h²). À z = 2,34 cela donne ±0,17 %, contre
  ±0,79 % si l'on ignore le terme croisé ; la barre d'état affiche les deux.
- **Courbure spatiale Ωk réglable** (±0,05). La distance comobile transverse
  D_M apparaît alors et remplace D_C dans D_L et D_A.
- **Comparaison SH0ES** : une case recalcule tout avec H₀ = 73,04 et superpose
  les courbes correspondantes — toutes les distances raccourcissent de 7,4 %.
- Lookback time, âge de l'univers à `z`, facteur d'échelle, `E(z)` et `H(z)`.
- Trois définitions de la vitesse de récession côte à côte (Doppler naïf,
  Doppler relativiste, FLRW), puisque deux d'entre elles sont des
  approximations.
- Tracé log-log des quatre distances avec zoom adaptatif, repères au maximum de
  D_A, à GN-z11 et au CMB, asymptotes `c·t₀` et horizon des particules. Les
  résultats sont mis en cache sur disque.
- Deux contrôles de cohérence affichés en permanence : `t_L + t_em = t₀` et
  l'identité d'Etherington `D_L = (1+z)²D_A`.
- Huit presets, de M 87 au CMB, chacun avec sa fiche d'identité.
- Version console avec `--omega-k`, `--no-shoes`, `--lang`, `--table` et
  `--version`.

### Langues

- Interface **française / anglaise** complète : menus, infobulles, sept pages
  d'aide, barre d'état et console. Les unités suivent la langue (`G al` /
  `Gly`), le séparateur décimal aussi.
- Le programme démarre dans la langue de la machine (variables POSIX, API
  Windows, réglages macOS), **anglais par défaut** pour toute langue autre que
  le français. Le menu *Langue* bascule immédiatement et le choix est mémorisé
  pour les fois suivantes ; `--lang` et `COSMO_LANG` priment.

### Installation

- **Exécutables autonomes** pour Windows, macOS (Apple Silicon) et Linux,
  construits, testés au démarrage et publiés automatiquement par GitHub
  Actions. Aucun Python nécessaire. Une version macOS Intel s'ajoute dès qu'un
  runner est disponible.
- Lanceurs pour les trois systèmes qui **installent Python eux-mêmes** s'il est
  absent (winget ou python.org, Homebrew, ou le gestionnaire de paquets Linux),
  puis créent l'environnement virtuel et installent les dépendances.
- Vérification discrète des mises à jour au démarrage (anonyme, non bloquante,
  désactivable par `COSMO_NO_UPDATE_CHECK=1`).

### Documentation et vérification

- Un cours en trois niveaux de lecture — vulgarisation, math spé, bac+5 — en
  français (68 pages) et en anglais (64 pages), des équations de Friedmann aux
  distances cosmologiques.
- Tous les nombres recalculés indépendamment sous **SageMath**, sans astropy :
  densités reconstruites depuis les constantes CODATA 2022, intégrale de
  Fermi-Dirac exacte pour les neutrinos massifs, quadrature à 25 chiffres.
  Accord à 2×10⁻⁶ sur les distances et 1,5×10⁻⁵ sur les âges ; les
  développements limités et la forme fermée de l'âge ont été redémontrés en
  calcul formel.
- Contrôle automatisé du bilinguisme de l'interface (195 textes par langue) et
  test de l'interface graphique sans écran.
