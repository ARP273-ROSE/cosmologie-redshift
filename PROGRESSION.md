# Cosmologie redshift → distances — progression

*[English version](PROGRESS.md)*

**Origine** : programme écrit en 2024-2025, cours LaTeX rédigé en mai 2026.
**Dépôt créé** : 2026-08-14 (le code n'avait jamais été versionné).
**Dépôt distant** : `github.com/ARP273-ROSE/cosmologie-redshift` (privé)

---

## État actuel

| Livrable | État | Chemin |
|---|---|---|
| Lanceurs multiplateformes | **✅ 14/08/26** — venv + dépendances automatiques | `launch.bat`, `launch.sh` |
| Application Qt6 | **✅ à jour** : ± incertitudes, courbure Ωk, comparaison SH0ES, 6 aides, **bilingue FR/EN** | `programme/redshift_distance_gui.py` |
| Noyau de calcul partagé | **✅ créé le 14/08/26** (la physique n'est plus dupliquée) | `programme/cosmo_core.py` |
| Version console | **✅ refondue** (3 modes : interactif, direct, `--table`) | `programme/redshift_distance_calculator.py` |
| Cours LaTeX (FR) | **✅ 68 p., 0 erreur de compilation, 0 référence non résolue** | `cours/cours_distances_cosmologiques.pdf` |
| Cours LaTeX (EN) | **✅ 64 p.** | `cours/course_cosmological_distances.pdf` |
| Rapport d'audit | **✅ 11 p.** | `audit/AUDIT_cosmologie.pdf` |
| Vérification SageMath | **✅ exécutée**, accord 2×10⁻⁶ sur les distances | `verif_sage/` |
| Versionnement git | **✅ fait le 14/08/26** — c'était le point noir | ce dépôt |

---

## Historique

### 2026-08-21 (suite) — Zéro prérequis sur les trois systèmes

- **Exécutables autonomes pour Windows, macOS (Intel et Apple Silicon) et
  Linux**, construits, testés au démarrage et publiés par GitHub Actions à
  chaque nouvelle version. Plus besoin de Python du tout.
- **Les lanceurs installent Python eux-mêmes** s'il est absent : winget puis
  l'installeur officiel sous Windows (avec recherche de l'exécutable aux
  emplacements standard, le PATH du processus courant n'étant pas encore à
  jour) ; Homebrew sous macOS, installé au besoin ; apt, dnf, pacman, zypper ou
  apk sous Linux. Le module `venv` manquant (Debian) est installé de la même
  façon. Une confirmation est demandée ; `COSMO_AUTO_INSTALL=1` la donne
  d'avance.
- Sous macOS, `find_python` vérifie que l'interpréteur s'exécute réellement :
  le système fournit un `python3` factice qui ne fait qu'ouvrir une fenêtre
  d'installation.
- Historique du dépôt réduit à un commit unique avant publication ; adresse de
  commit remplacée par l'adresse noreply GitHub.

### 2026-08-21 — Publication

- Dépôt rendu **public**, première **release v1.0.0**.
- `.github/workflows/release.yml` : construction de l'exécutable Windows
  (PyInstaller, ~107 Mo, autonome), test de démarrage, création du tag depuis
  la version lue dans `programme/updates.py`, publication de la release avec un
  nom d'asset stable et les deux cours en PDF. Build vérifié : réussi.
- Lien permanent, indépendant de la version :
  `https://github.com/ARP273-ROSE/cosmologie-redshift/releases/latest/download/CosmologicalDistanceCalculator-windows.exe`
- Vérification du bilinguisme automatisée (`verif_sage/test_i18n.py`) : 195
  textes par langue, mêmes clés des deux côtés, aucune fuite d'une langue dans
  l'autre, console comprise.
- Vérification de version au démarrage (anonyme, non bloquante, désactivable).
- Nettoyage avant publication : plus aucune référence personnelle ni à un
  environnement privé ; ton impersonnel dans les deux cours.

### 2026-08-14 (suite 5) — Programme bilingue et documentation anglaise

clavier ».

- **`programme/i18n.py`** : toutes les chaînes de l'interface et de la console,
  dans les deux langues, via `t("clé", **kw)`. Ordre de choix de la langue :
  menu *Langue*, `--lang`, `COSMO_LANG`, locale système, français par défaut.
- **`programme/help_texts.py`** : les sept boîtes d'aide dans les deux langues,
  sous forme de gabarits `str.format` remplis par `help_context()` — aucun
  nombre n'est écrit en dur.
- **Les unités suivent la langue** : `G al` / `Gly`, `M al` / `Mly`, et le
  séparateur décimal (virgule en français, point en anglais) via `fmt_num()`.
- **Documents anglais** : `README.en.md`, `MANUAL.md`, `PROGRESS.md`, et le
  cours complet `cours/course_cosmological_distances.tex` (**64 p.**).
- Le rapport d'audit reste en français : c'est un instantané daté, pas un
  document vivant.

**Saisie clavier corrigée au passage.** Le champ de courbure ne se modifiait
qu'avec les flèches : sous une locale française, Qt refuse le *point* décimal,
et chaque frappe relançait le calcul complet des courbes. Le nouveau
`NumberSpinBox` accepte les deux séparateurs (locale C + normalisation) et le
champ Ωk n'applique sa valeur qu'à Entrée / perte de focus. Vérifié par frappes
simulées dans le test headless : `0.02`, `0,015`, `-0.01`, `.03` tous acceptés.

### 2026-08-14 (suite 4) — Barres d'erreur, courbure, cache

Les chantiers 1, 3 et 4 de la liste « à faire » sont traités.

#### 1. Barres d'erreur

Toutes les grandeurs sont affichées **valeur ± 1σ**, propagée de
σ(H₀) = 0,42 et σ(Ωm) = 0,0056 par dérivées numériques centrées.

Le point important n'était pas la propagation mais le **terme croisé** : H₀ et
Ωm sont anticorrélés à ρ = −0,9763 dans l'ajustement Planck. Ce coefficient
n'est pas posé à la main, il est **déduit** de la contrainte sur ω_m = Ωm h²
(mesurée à 0,65 %, contre 1,8 % pour Ωm et 0,62 % pour h), par résolution
symbolique sous Sage.

| z | σ(D_C) avec ρ | sans ρ |
|---|---|---|
| 0,01 | 0,62 % | 0,62 % |
| 1 | 0,31 % | 0,70 % |
| 2,34 | **0,17 %** | 0,79 % |
| 5 | 0,13 % | 0,86 % |
| 1089,8 | 0,18 % | 0,95 % |

Deux enseignements : ignorer la corrélation surestime l'incertitude d'un
facteur 2 à 5 (l'estimation « ±0,6 % » du rapport d'audit était de cet ordre,
faute de terme croisé) ; et l'incertitude passe par un **minimum vers z ≈ 5**,
un redshift « pivot ».

**Comparaison SH0ES** : une case affiche en regard les mêmes grandeurs avec
H₀ = 73,04 et superpose les courbes en pointillé. Écart : −7,4 % sur tout, soit
~40 fois les barres d'erreur — l'incertitude dominante sur une distance
cosmologique est systématique, pas statistique.

#### 3. Courbure

Champ **Ωk** (±0,05). Dès que Ωk ≠ 0, la distance comobile **transverse** D_M
apparaît et remplace D_C dans D_L et D_A. Implémentée via
`comoving_transverse_distance` sur une `LambdaCDM` construite avec le contenu
radiatif de Planck (Ode0 = 1 − Om0 − Ωγ − Ων − Ωk).

Deux corrections induites : t₀ dépend de la courbure (13,744 Gyr à Ωk = +0,01),
donc le contrôle « t_L + âge = t₀ » se réfère au modèle courant ; et le repère
du maximum de D_A est maintenant lu sur la courbe, donc il suit Ωk.

Vérification croisée SageMath (modèle reconstruit à l'identique) : accord à
**cinq décimales** sur D_C, D_M, D_L et D_A pour Ωk = −0,01, 0, +0,01, aux
quatre redshifts testés.

#### 4. Cache du tracé

`curves()` écrit dans `programme/cache/curves_<hash>.npz`, la clé couvrant tous
les paramètres et la grille. Mesures réelles : **49 ms → 4 ms** pour 600
points. L'estimation « ~1 s » du rapport d'audit était pessimiste (astropy 8
vectorise mieux) ; le gain devient net si la grille s'étend (5 000 points :
390 ms). Repli automatique vers le dossier temporaire si le dépôt n'est pas
inscriptible — cas courant lorsque le dépôt est sur un partage réseau.

#### Documentation

Cours : nouvelle section « Incertitudes et corrélation entre paramètres »
(dérivation de ρ + tableau généré par script), encadré « Dans le programme »
sur D_M avec les valeurs vérifiées, trois sous-sections dans le chapitre
« interface ». Le cours passe de 66 à **68 pages**. Nouvelle aide **F6** dans
le programme. Ajout de `verif_sage/verif_courbure_sigma.sage` et
`verif_sage/gen_table_sigma.py`.

### 2026-08-14 (suite 3) — Dépôt sur un partage réseau

Le dépôt était cloné sur un lecteur réseau (partage SMB monté sous Windows).
**Windows refuse d'exécuter les binaires d'un venv situé sur un partage**
(WinError 5), quelle que soit l'option de création. `launch.bat` détecte
maintenant le lecteur réseau (fsutil, ou chemin UNC) et place le venv dans
`%LOCALAPPDATA%\cosmologie-redshift\venv` : le dépôt peut rester sur le partage.
`COSMO_VENV` permet de choisir un autre emplacement.

### 2026-08-14 (suite) — Lanceurs et portabilité


- **`launch.bat`** (Windows) et **`launch.sh`** (Linux/macOS), mêmes
  sous-commandes : *(rien)*, `console [z]`, `table`, `check`, `update`, `help`.
  Ils créent le venv, installent `requirements.txt`, posent un marqueur
  `.venv/.deps-ok` (lancements suivants ~0,6 s) et démarrent le programme.
  Windows utilise `pythonw.exe` pour éviter la console résiduelle ; le `.bat`
  est en **ASCII pur** et fait `chcp 65001`.
- **`requirements.txt`** : numpy, scipy, astropy, PyQt6, pyqtgraph — `scipy`
  n'étant pas optionnel (quadratures d'astropy).
- **`.gitattributes`** : `*.bat` en CRLF (sinon `cmd.exe` peut mal lire les
  blocs `if`/`goto`), `*.sh` en LF, PDF/PNG en binaire.
- **Portabilité du code** :
  - polices avec repli sur les trois plateformes (Cascadia/Consolas →
    SF Mono/Menlo → DejaVu/Liberation → `monospace`), via `mono_font()` et
    `FONT_UI` ; plus aucune police codée en dur ;
  - `sys.path` complété avec le dossier du script → les trois modules
    s'importent depuis n'importe quel dossier courant ;
  - `stdout`/`stderr` reconfigurés en UTF-8 : sans cela, la console Windows en
    cp1252 lèverait `UnicodeEncodeError` sur `•`, `₀`, `Ω`, `✓` ;
  - `verif_sage/test_gui_headless.py` : plus de chemins absolus en dur, il force
    lui-même `QT_QPA_PLATFORM=offscreen` et écrit dans `audit/captures/`.

**Testé pour de vrai** sous Linux, venv créé de zéro : installation des cinq
dépendances, puis `check`, `console 2.34`, `table`, `help`, appel depuis un
autre dossier, détection de l'absence de `DISPLAY`, et test headless complet
(8 valeurs de z + 6 boîtes d'aide + captures). ⚠️ **`launch.bat` n'a pas pu être
exécuté** — pas de Windows ici : il a été relu ligne à ligne (expansion
retardée, `if defined`, `errorlevel`, `cd /d "%~dp0."`) mais son premier
lancement réel reste à faire côté PC.

### 2026-08-14 (suite 2) — « Accès refusé » au premier lancement sous Windows

Premier essai réel de `launch.bat` sous Windows : le venv se crée, puis les deux
commandes `pip` échouent sur **« Accès refusé »** — et mon message d'erreur
parlait à tort de connexion réseau, en masquant la sortie de pip.

Ce n'est pas pip qui refuse : c'est `cmd.exe` qui ne peut pas exécuter
`.venv\Scripts\python.exe`. Cause n° 1 : **Python installé depuis le Microsoft
Store**, dont les venv contiennent un `python.exe` qui n'est qu'un lien vers
l'alias d'exécution, inexécutable ailleurs. Causes suivantes : antivirus, ou
dépôt placé sur un lecteur réseau / dossier synchronisé.

Corrections apportées aux deux lanceurs :

- **détection automatique du Python du Store** (chemin contenant
  `WindowsApps`) avec la marche à suivre complète, *avant* de créer le venv ;
- **vérification que le python du venv s'exécute** (`-c "import sys"`) avant
  toute installation, avec un message qui liste les trois causes ;
- **la sortie de pip n'est plus masquée** (`--quiet` retiré) : la cause exacte
  s'affiche ;
- trois commandes de secours, symétriques Windows/Linux :
  `doctor` (Python détecté et son chemin, droits d'écriture, état du venv et
  des dépendances, affichage), `reset` (supprime le venv), `system`
  (contournement sans venv, `pip install --user`) ;
- `MANUEL.md` §10 « Quand l'installation échoue ».

Vérifications : `launch.sh` testé en réel sous Linux (`doctor` sans venv, puis
`check` qui crée tout, `doctor` avec venv, `reset`). `launch.bat` reste non
exécuté faute de Windows, mais il passe un **contrôle statique** écrit pour
l'occasion (`verif_sage/check_bat.py`) : labels de `goto`/`call` tous définis,
parenthèses de blocs équilibrées, fichier en ASCII pur, pas de
`cd /d "%~dp0"` (le backslash final échapperait le guillemet).

### 2026-08-14 — Audit complet + création du dépôt

Demande : retrouver le programme (introuvable, aucun dépôt git), l'auditer avec
son cours, vérifier les calculs sous SageMath.

**Retrouvé** dans `_docs/physique/antikythera_and_old/Physique/` — dossier
fourre-tout sans rapport avec l'Anticythère ; le cours était ailleurs, dans
`_docs/physique/cosmologie_cours/`. Un dépôt git existait mais **sans aucun
commit et sans remote**.

**Verdict de l'audit** : le moteur de calcul est juste, la documentation ne
l'était pas.

#### Vérification (3 chaînes indépendantes)

1. astropy 8.0.1 + scipy (le backend à auditer) ;
2. recalcul complet sous SageMath **sans astropy** : densités reconstruites
   depuis CODATA 2022, intégrale de Fermi-Dirac **exacte** pour les neutrinos
   massifs (astropy utilise l'ajustement de Komatsu 2011), mpmath 25 chiffres ;
3. calcul formel Sage pour les développements limités et la forme fermée de l'âge.

| Grandeur | Écart astropy ↔ SageMath |
|---|---|
| E(z) | 1,79 × 10⁻⁵ |
| D_C, D_L, D_A | 2,10 × 10⁻⁶ |
| lookback time | 4,58 × 10⁻⁷ |
| âge | 1,50 × 10⁻⁵ |

Contrôles internes : Etherington à 2×10⁻¹⁶, `t_L + t_em = t₀` à 2×10⁻¹⁰ Gyr,
maximum de D_A en z = 1,592133 par les deux méthodes.

#### Corrections du programme (14 constats)

- **Majeur** — l'aide F1 affichait `E(z) = √(Ωm(1+z)³+ΩΛ)`, qui n'est pas la
  formule utilisée (−12,8 % sur E au CMB ; âge de 479 kyr au lieu de 372).
- **Majeur** — « Ωm = 0,3111 » affiché alors que `Planck18.Om0 = 0,30966` ; la
  différence, ce sont les neutrinos.
- Une seule vitesse de récession affichée (`cz`, la moins bonne) → les trois.
- Âge de référence 13,787 codé en dur → lu du backend.
- Âge à grand z affiché « 0,0004 Gyr » → bascule Gyr/Myr/kyr.
- Âges des presets périmés : GN-z11 420 → **435 Myr**, ULAS J1120 770 → **749 Myr**,
  CMB 380 000 → **372 000 ans**.
- M 87 : « ~55 Mly » sans expliquer que z donne 62 Mly (vitesse propre dans l'amas).
- Duplication GUI/console → `cosmo_core.py`.
- Console : avertissement « z > 10 : résultats moins précis » (faux) remplacé.
- Résidus PyCharm `main.py`/`test.py` (dont un qui plante) → `programme/_ancien/`.
- Ajouts : E(z) et H(z) affichés, aide F5 « vérification », deux contrôles
  permanents en barre d'état, repère du maximum de D_A et asymptotes sur le graphe.

#### Corrections du cours (17 erreurs)

Les quatre majeures :

1. `D_H = c/H₀` donnée à **4,431 G al au lieu de 14,4516** (confusion Mpc ↔ al,
   facteur 3,26) — l'erreur se propageait dans un tableau et contredisait le
   texte deux chapitres plus loin ;
2. le tableau « calcul numérique » mélangeait des **Gpc et des G al** dans la
   même colonne ;
3. **trois développements limités sur quatre étaient faux** (D_C portait le
   coefficient de D_L : 10 % d'erreur à z = 0,1) ;
4. la « forme fermée de ∫dz/E » est en réalité celle de l'**âge**, avec un
   préfacteur faux d'un facteur 3 — et l'intégrale de distance n'a pas de forme
   élémentaire.

Puis : q₀ = −0,527 → −0,5334 ; M 87 « 19 Mly » → 18,96 Mpc = 61,8 Mly ;
3C 273, z = 1, z = 10,6, CMB recalculés ; horizon des particules 46,28 → 46,2005 ;
asymptotes à grand z corrigées ; v_rec(CMB) 3,16 c → 3,134 c ; « 380 000 ans » vs
« 372 kyr » (contradiction interne) harmonisé ; Ω_r 9,24 → 9,139 × 10⁻⁵ avec
distinction Ω_γ / Ω_ν ; `u.Gly` (inexistant) → `u.Glyr` ; horizon des événements
16 → 16,5808 G al.

**Ajouts** : section « Le E(z) réellement calculé » (§6.3) et annexe B
« Vérification indépendante des calculs (SageMath) ». Le cours passe de 58 à 66 p.

Était juste : le cas z = 2,34 (fil rouge du cours, seul cas réellement calculé),
toutes les dérivations FLRW, Etherington, le traitement du redshift, la
recombinaison et la bibliographie.

#### Réorganisation

Programme, cours, audit et scripts regroupés dans ce dépôt ; une note
`DEPLACE.md` reste aux deux anciens emplacements.

---

## Ce qui reste à faire

| # | Sujet | Détail |
|---|---|---|
| 1 | **Comparateur multi-cosmologies** | la comparaison SH0ES est faite ; reste WMAP9 / cosmologie libre (H₀ et Ωm éditables) sur le même graphe |
| 2 | **Export** | bouton « copier les résultats » ou export CSV sur une plage de z |
| 3 | **Incertitude sur Ωk** | les ± ne propagent que σ(H₀) et σ(Ωm) ; ajouter σ(Ωk) = 0,0019 quand la courbure est activée |
| 4 | **Valider `launch.bat` sous Windows** | partiellement validé (le diagnostic a bien identifié le lecteur réseau) ; reste à confirmer un lancement complet après le correctif |

---

## Pièges à ne pas réintroduire

- `Planck18.Om0 = 0,30966`, **jamais 0,3111** : ce dernier vaut `Om0 + Onu0`.
- L'unité astropy est `u.Glyr` et `u.lyr` — `u.Gly` et `u.ly` n'existent pas.
- `1 Mpc = 3,2616 × 10⁶ al` : `D_H = 4430,87 Mpc` fait **14,45** G al, pas 4,43.
- La formule `E(z)` à deux termes est bonne pour les **distances** jusqu'à
  z ~ 10, mauvaise pour les **âges** à grand z (l'intégrale de l'âge est dominée
  par l'ère radiative).
- Ne jamais recopier un nombre à la main dans le cours : passer par
  `verif_sage/gen_tables.py`.
- Après toute modification de la GUI, relancer le test headless (MANUEL §6.3).
- Les barres d'erreur **doivent** garder le terme croisé : sans lui, σ(D_C) est
  surestimée d'un facteur 2 à 5 (ρ = −0,9763, pas 0).
- Le contrôle « t_L + âge = t₀ » se compare à `d["t0_model"]`, jamais à la
  constante `T0_GYR` : t₀ change avec la courbure.
- `curves()` doit rester tolérante à un dossier non inscriptible (dépôt sur
  partage réseau) : le cache est un bonus, jamais une condition.
- Toute nouvelle chaîne d'interface va dans `i18n.py`, dans **les deux** langues.
