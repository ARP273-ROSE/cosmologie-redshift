# Journal des versions

*[English version](CHANGELOG.md)*

Ce fichier recense les changements notables du projet. Le format suit
[Keep a Changelog](https://keepachangelog.com/) et la numérotation respecte le
[versionnement sémantique](https://semver.org/).

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
- Langue choisie par le menu *Langue*, `--lang`, `COSMO_LANG`, ou la locale du
  système.

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
