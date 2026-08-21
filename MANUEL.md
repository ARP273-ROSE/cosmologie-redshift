# Manuel — calculateur de distances cosmologiques

*[English version](MANUAL.md)*

Tout ce qu'il faut pour installer, utiliser, modifier, recompiler et vérifier.
Pour l'aperçu du projet, voir [`README.fr.md`](README.fr.md) ; pour l'état d'avancement,
[`PROGRESSION.md`](PROGRESSION.md).

---

## 1. Installation et lancement

**Aucun prérequis.** Soit on télécharge l'exécutable autonome (Windows, macOS,
Linux : voir le README), soit on part des sources et **le lanceur installe
Python lui-même s'il est absent** — winget ou l'installeur python.org sous
Windows, Homebrew sous macOS, le gestionnaire de paquets sous Linux. Une
confirmation est demandée ; `COSMO_AUTO_INSTALL=1` l'accorde d'avance.

Ensuite, les lanceurs s'occupent du reste :
ils créent le venv `.venv/` au premier appel, y installent `requirements.txt`,
posent un marqueur `.venv/.deps-ok` et démarrent le programme. Les lancements
suivants sont immédiats (~0,6 s).

### 1.1 Windows — `launch.bat`

Double-clic pour l'interface graphique, ou en ligne de commande :

| Commande | Effet |
|---|---|
| `launch.bat` | interface graphique (via `pythonw.exe`, sans console résiduelle) |
| `launch.bat console` | version console, mode interactif |
| `launch.bat console 2.34` | calcul direct pour z = 2,34 |
| `launch.bat table` | table des huit presets |
| `launch.bat check` | auto-test du noyau de calcul |
| `launch.bat update` | réinstalle / met à jour les dépendances |
| `launch.bat reset` | supprime `.venv/` et repart de zéro |
| `launch.bat system` | se passe du venv (`pip install --user`) |
| `launch.bat doctor` | diagnostic complet — voir §10 |
| `launch.bat help` | rappel des commandes |

Le script cherche Python via `py -3` puis `python`, et affiche un message clair
s'il ne trouve rien (avec le rappel de cocher « Add python.exe to PATH » à
l'installation). Il force `chcp 65001` et `PYTHONUTF8=1` pour que les caractères
accentués et les symboles (`Ω`, `₀`, `•`) s'affichent correctement dans `cmd.exe`.

### 1.2 Linux / macOS — `launch.sh`

```bash
./launch.sh                 # interface graphique
./launch.sh console 2.34    # calcul direct
./launch.sh table           # table des presets
./launch.sh check           # auto-test
./launch.sh update          # mise à jour des dépendances
./launch.sh reset           # supprime le venv et repart de zéro
./launch.sh system          # se passe du venv (pip install --user)
./launch.sh doctor          # diagnostic complet — voir §10
./launch.sh help            # aide
```

Le script détecte l'absence de serveur d'affichage (`DISPLAY` et
`WAYLAND_DISPLAY` vides) et le dit, au lieu de laisser Qt échouer sur un message
obscur. Il fonctionne depuis n'importe quel dossier courant.

**Réutiliser un venv existant** (utile si un venv complet existe déjà) :

```bash
COSMO_VENV=~/work/venv ./launch.sh check
```

Si `python3 -m venv` échoue sous Debian/Ubuntu : `sudo apt install python3-venv`.

### 1.3 Installation manuelle (sans lanceur)

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt        # Windows : .venv\Scripts\pip.exe
.venv/bin/python programme/redshift_distance_gui.py
```

`scipy` n'est pas optionnel : `astropy.cosmology` s'en sert pour les quadratures
(`comoving_distance`, `age`, `lookback_time`). Sans lui, l'import passe mais tout
calcul échoue.

### 1.4 Cas particulier : une image Docker minimale

Sur une image Python minimale (par exemple un conteneur Jupyter), les
bibliothèques système dont Qt a besoin sont absentes. À installer une fois :

```bash
apt-get update && apt-get install -y libegl1 libgl1 libxkbcommon-x11-0 \
  libdbus-1-3 libxcb-cursor0 libxcb-icccm4 libxcb-keysyms1 libxcb-shape0
```

Sans écran, lancer avec `QT_QPA_PLATFORM=offscreen` (voir §6.3).


---

## 2. Mode console

```bash
./launch.sh console          # ou  launch.bat console
```

Options :

```bash
./launch.sh console 2.34                  # calcul direct
./launch.sh console 2.34 --omega-k 0.01  # avec courbure
./launch.sh console 2.34 --no-shoes      # sans la comparaison SH0ES
./launch.sh console --help               # rappel des options
```

En interactif : taper un nombre, `table` pour la liste des presets, `q` pour quitter. La virgule
décimale est acceptée (`2,34` comme `2.34`). Au-delà de z = 1500, le programme
prévient que l'univers était opaque, puis calcule quand même.

---

## 3. Lire l'interface

### 3.1 Ligne de sous-titre

```
Planck 2018 (TT,TE,EE+lowE+lensing+BAO) — H₀ = 67.66 km/s/Mpc ·
Ωm+Ων = 0.31110 · ΩΛ = 0.68885 · Ωγ = 5.402e-05 · t₀ = 13.7869 Gyr
```

Elle déclare exactement le modèle utilisé. `TT,TE,EE+lowE+lensing+BAO` est la
combinaison de jeux de données Planck qui a produit ces paramètres (aide **F2**
pour le décodage sigle par sigle).

### 3.2 Champ `z` et presets

`z` va de 0 à 1500, avec 5 décimales et un pas de 0,01. Les huit boutons chargent
un objet ou une époque ; chacun porte une fiche en infobulle.

| Preset | z | Âge de l'univers à z |
|---|---|---|
| M 87 | 0,00428 | 13,725 Gyr |
| 3C 273 | 0,158 | 11,745 Gyr |
| z = 1 | 1,0 | 5,851 Gyr |
| z = 2,34 | 2,34 | 2,799 Gyr |
| ULAS J1120 | 7,085 | 749 Myr |
| GN-z11 | 10,6 | 435 Myr |
| Réionisation | 20 | 178 Myr |
| CMB | 1089,8 | 372 kyr |

Ces âges sont ceux calculés **en Planck 2018**. Ils diffèrent parfois des valeurs
des articles d'origine, qui utilisaient les cosmologies WMAP de leur époque
(ULAS J1120 : 770 Myr dans l'article, 749 ici).

### 3.3 Le panneau « Modèle » : courbure et comparaison SH0ES

| Contrôle | Effet |
|---|---|
| **Courbure Ωk** | plage ±0,05, défaut 0. Dès que Ωk ≠ 0, une cinquième ligne apparaît : la distance comobile **transverse** D_M, qui remplace D_C dans D_L et D_A |
| **plat (Ωk = 0)** | revient à Planck 2018 |
| **comparer avec SH0ES** | ajoute sous chaque valeur celle obtenue avec H₀ = 73,04, l'écart en %, et superpose les courbes en pointillé |

Ωk > 0 = univers ouvert (D_M > D_C, sinh) ; Ωk < 0 = fermé (D_M < D_C, sin).
Planck 2018 + BAO mesure Ωk = 0,0007 ± 0,0019, d'où le défaut à zéro.

Attention : l'âge actuel t₀ dépend lui aussi de la courbure (13,744 Gyr pour
Ωk = +0,01) ; le contrôle « t_L + âge = t₀ » se réfère au modèle courant.

### 3.4 Les barres d'erreur

Chaque valeur est donnée avec son incertitude 1σ, propagée de
σ(H₀) = 0,42 km/s/Mpc et σ(Ωm) = 0,0056 par dérivées numériques :

```
σ_G² = A²σ_H₀² + B²σ_Ωm² + 2ρ·A·B·σ_H₀·σ_Ωm      A = ∂G/∂H₀, B = ∂G/∂Ωm
```

**Le terme croisé n'est pas optionnel.** H₀ et Ωm sont anticorrélés à
ρ = −0,9763 dans l'ajustement Planck. Ce coefficient est *déduit*, pas posé :
ω_m = Ωm h² est mesuré à 0,65 % alors que Ωm l'est à 1,8 % et h à 0,62 %, ce
qui impose la corrélation (dérivation dans `verif_sage/verif_courbure_sigma.sage`).

| z | σ(D_C) avec ρ | sans ρ |
|---|---|---|
| 0,01 | 0,62 % | 0,62 % |
| 1 | 0,31 % | 0,70 % |
| 2,34 | **0,17 %** | 0,79 % |
| 5 | 0,13 % | 0,86 % |
| 1089,8 | 0,18 % | 0,95 % |

La barre d'état affiche les deux. À retenir : l'incertitude relative passe par
un **minimum vers z ≈ 5** — un redshift « pivot » où le modèle prédit les
distances mieux qu'il ne connaît ses propres paramètres. Et surtout : la
tension de Hubble déplace tout de 7,4 %, soit 40 fois les barres d'erreur.

### 3.5 Les quatre distances

| Affichage | Formule | À quoi ça sert |
|---|---|---|
| Distance comobile | `D_C = D_H ∫₀^z dz'/E(z')` | la distance **actuelle** de l'objet |
| Distance de luminosité | `D_L = (1+z)·D_C` | photométrie : `F = L/(4πD_L²)` |
| Distance de diamètre angulaire | `D_A = D_C/(1+z)` | tailles angulaires : `θ = ℓ/D_A` |
| Distance de trajet de la lumière | `D_lt = c·t_L` | la valeur « intuitive », bornée par `c·t₀` |

`D_A` passe par un **maximum** de 5,846 G al à z = 1,5921 puis décroît : un objet
identique paraît plus grand à z = 5 qu'à z = 1. C'est le point le plus
contre-intuitif du lot, et il est repéré sur le graphe.

### 3.6 Grandeurs cosmologiques

- **Lookback time** `t_L(z) = ∫₀^z dz'/[(1+z')H(z')]` — durée du trajet de la lumière.
- **Âge de l'univers à z** `t_em(z) = ∫_z^∞ dz'/[(1+z')H(z')]` — bascule
  automatiquement en Gyr, Myr ou kyr.
- **Facteur d'échelle** `a = 1/(1+z)`, avec le rapport de taille de l'univers.
- **E(z) = H(z)/H₀** et `H(z)` : c'est la fonction intégrée dans toutes les
  distances, affichée pour qu'on voie d'où viennent les nombres.

### 3.7 Les trois vitesses de récession

Aide **F3** pour la discussion complète. En résumé : seule la troisième
(`v = H₀·D_C`) est correcte en cosmologie ; elle dépasse `c` au-delà de
z ≈ 1,48 et c'est parfaitement licite — ce n'est pas une vitesse de propagation
dans l'espace mais un taux d'étirement de l'espace.

### 3.8 Barre d'état — les contrôles permanents

```
z = 2.34 · contrôle : t_L + âge = 13.786885 Gyr (t₀ = 13.786885 Gyr, écart 0.00 µGyr)
         · Etherington : D_L/(1+z)²D_A = 1.000000000000
```

Ces deux identités doivent rester vraies quelle que soit `z`. Si l'une s'écarte,
c'est qu'astropy a changé de version ou de cosmologie par défaut : ne pas
ignorer.

### 3.9 Le graphe

Échelle log-log, zoom adaptatif sur `[z/30, 8z]`. Repères verticaux : `z=1`,
maximum de `D_A`, GN-z11, CMB. Asymptotes horizontales : `c·t₀` (que la courbe
verte ne franchit jamais) et l'horizon des particules (que la cyan approche).

### 3.10 Menu Aide

| Touche | Contenu |
|---|---|
| **F1** | Les quatre distances + le `E(z)` réellement calculé |
| **F2** | Planck 2018, décodage de `TT,TE,EE+lowE+lensing+BAO`, tension de Hubble |
| **F3** | Vitesses de récession et univers superluminique |
| **F4** | Les huit objets-cibles |
| **F5** | Comment les calculs ont été vérifiés (SageMath) |

---

## 4. Organisation du code

```
programme/
├── cosmo_core.py                     TOUTE la physique
├── redshift_distance_gui.py          interface Qt6 (affichage seul)
├── redshift_distance_calculator.py   version console (affichage seul)
├── make_logo.py                      génération du logo
└── _ancien/                          résidus de gabarit PyCharm, non fonctionnels
```

**Règle** : aucune formule dans la GUI ni dans la console. Toute modification
physique se fait dans `cosmo_core.py`, qui expose :

| Objet | Rôle |
|---|---|
| `compute(z, Ok=0, with_sigma=True, with_shoes=True)` | dict complet : distances (al), temps (Gyr), vitesses (km/s), `E`, `H_z`, `t0_model`, plus `sigma`, `sigma_pct`, `sigma_indep_pct` et `shoes` |
| `make_cosmology(H0, Om, Ok)` | construit la cosmologie (renvoie `Planck18` lui-même si les paramètres sont ceux par défaut) |
| `curves(z_grid, Ok=0, H0=…)` | les quatre distances (G al) sur une grille, **avec cache disque** |

### Le cache du tracé

`curves()` écrit ses résultats dans `programme/cache/curves_<hash>.npz` (à
défaut, dans le dossier temporaire du système). La clé de hachage couvre tous
les paramètres cosmologiques *et* la grille : changer Ωk, H₀ ou le nombre de
points invalide automatiquement l'entrée, il n'y a jamais de valeur périmée.

Mesures réelles (astropy 8) : 600 points en **49 ms** sans cache, **4 ms**
avec. Le gain
devient réel quand la grille s'étend : 5 000 points prennent 390 ms.

Le dossier `cache/` est ignoré par git. Pour désactiver : variable
d'environnement `COSMO_NO_CACHE=1`, ou `curves(..., use_cache=False)`.
| `format_distance()`, `format_time()` | mise en forme (al/kal/Mal/Gal, Gyr/Myr/kyr) |
| `PRESETS` | les huit objets, avec leurs infobulles |
| `T0_GYR`, `D_H_GLYR`, `PARTICLE_HORIZON_GLYR`, `EVENT_HORIZON_GLYR`, `Z_DA_MAX`, `DA_MAX_GLYR` | constantes dérivées |

### Changer de cosmologie

Dans `cosmo_core.py`, remplacer l'import :

```python
from astropy.cosmology import Planck18 as cosmo        # actuel
# from astropy.cosmology import WMAP9 as cosmo         # comparaison
# from astropy.cosmology import FlatLambdaCDM
# cosmo = FlatLambdaCDM(H0=73.04, Om0=0.30966, Tcmb0=2.7255)   # SH0ES
```

Tout le reste suit automatiquement : sous-titre, aides, constantes dérivées.
Attention : les valeurs codées en dur `PARTICLE_HORIZON_GLYR`, `EVENT_HORIZON_GLYR`,
`Z_DA_MAX` et `DA_MAX_GLYR` sont propres à Planck 2018 — les recalculer avec
`verif_sage/` si l'on change de modèle.

---

## 5. Le logo

```bash
python programme/make_logo.py
```

Produit `logo.svg` et `logo_{16,32,64,128,256}.png`. Les PNG servent d'icône de
fenêtre (Windows choisit la taille) et `cours/logo.png` de couverture au cours.

---

## 6. Vérifier les calculs

### 6.1 Recalcul indépendant sous SageMath

Les scripts ne dépendent pas d'astropy : ils reconstruisent tout depuis les
constantes CODATA 2022 et les équations de Friedmann. Avec une installation
SageMath locale :

```bash
sage verif_sage/verif_cosmo.sage            # recalcul complet (~50 s)
sage verif_sage/verif_DL_symbolique.sage    # développements limités, calcul formel
sage verif_sage/verif_courbure_sigma.sage   # corrélation et courbure
```

Avec l'image Docker officielle :

```bash
docker run --rm -v "$PWD:/home/sage/work" sagemath/sagemath \
  sage /home/sage/work/verif_sage/verif_cosmo.sage
```

Les scripts écrivent leurs résultats en JSON à côté d'eux ; adapter le chemin
de sortie en tête de script si le dossier n'est pas inscriptible.

### 6.2 Valeurs de référence astropy et comparaison

```bash
.venv/bin/python verif_sage/ref_astropy.py   # valeurs de référence -> JSON
.venv/bin/python verif_sage/compare.py       # comparaison des deux chaînes
```

`gen_tables.py` et `gen_table_sigma.py` régénèrent les tableaux LaTeX des
cours, pour ne jamais recopier un nombre à la main.

### 6.3 Test de l'interface sans écran

Depuis la racine du dépôt, sur n'importe quelle plateforme :

```bash
.venv/bin/python verif_sage/test_gui_headless.py            # Linux / macOS
.venv\Scripts\python.exe verif_sage\test_gui_headless.py    # Windows
```

Le script force lui-même `QT_QPA_PLATFORM=offscreen`. Il balaye 8 valeurs de `z`
(dont les cas limites 0 et 1500), imprime les contrôles de cohérence, ouvre les
six boîtes d'aide et réécrit les captures de `captures/`.
**C'est le test à relancer après toute modification de la GUI.**

---

## 7. Recompiler les documents LaTeX

TeX Live doit être disponible dans le `PATH` (paquet `texlive-full` sous Linux,
MacTeX sous macOS, MiKTeX sous Windows) :

```bash
cd cours
pdflatex -interaction=nonstopmode cours_distances_cosmologiques.tex   # français
pdflatex -interaction=nonstopmode cours_distances_cosmologiques.tex
pdflatex -interaction=nonstopmode course_cosmological_distances.tex   # anglais
pdflatex -interaction=nonstopmode course_cosmological_distances.tex

rm -f *.aux *.log *.out *.toc
```

**Deux passes obligatoires** (table des matières et références croisées). Le
`.gitignore` exclut déjà les fichiers temporaires, mais autant ne pas les laisser
traîner.

Contrôles après compilation :

```bash
grep -E "^! |Reference.*undefined" *.log     # doit être vide
pdfinfo cours_distances_cosmologiques.pdf | grep Pages    # 66
```

Le cours inclut `table_reference.tex`, généré par `verif_sage/gen_tables.py` : ne
pas l'éditer à la main.

---

## 8. Dépannage

| Symptôme | Cause | Solution |
|---|---|---|
| `[ERREUR] Python 3 est introuvable` | Python absent ou hors du `PATH` | réinstaller en cochant « Add python.exe to PATH » |
| `ModuleNotFoundError: astropy` | venv incomplet | `launch.bat update` / `./launch.sh update` |
| L'appli démarre puis se fige au premier calcul | `scipy` absent | idem (`update`) |
| Échec de création du venv sous Debian/Ubuntu | paquet `python3-venv` absent | `sudo apt install python3-venv` |
| `ImportError: libEGL.so.1` (Linux) | bibliothèques Qt système absentes | §1.4 |
| `qt.qpa.plugin: could not load the Qt platform plugin "xcb"` | pas de serveur d'affichage | `./launch.sh console`, ou `QT_QPA_PLATFORM=offscreen` |
| Caractères bizarres dans la console Windows (`Ã©`, `?`) | page de code non-UTF-8 | passer par `launch.bat` (fait `chcp 65001`) |
| `AttributeError: module 'astropy.units' has no attribute 'Gly'` | l'unité s'écrit `Glyr` | utiliser `u.Glyr` et `u.lyr` |
| Une console noire reste ouverte (Windows) | lancé avec `python.exe` | passer par `launch.bat` (utilise `pythonw.exe`) |
| Barre d'état : Etherington ≠ 1 ou écart en µGyr non nul | astropy a changé de version/cosmologie | relancer `verif_sage/` avant de se fier aux nombres |
| Le graphe est vide à z = 0 | normal : toutes les distances valent 0, log(0) est écarté | mettre z > 0 |

---


---

## 10. Quand l'installation échoue

Les deux lanceurs ont trois commandes de secours :

| Commande | Effet |
|---|---|
| `doctor` | diagnostic : Python détecté et son chemin, droits d'écriture, état du venv, dépendances, affichage |
| `reset` | supprime `.venv/` et repart de zéro |
| `system` | se passe du venv : `pip install --user`, puis lance le programme |

### « Accès refusé » pendant l'installation des dépendances (Windows)

Ce n'est pas un problème de réseau : c'est `.venv\Scripts\python.exe` que Windows
refuse d'exécuter. Trois causes, par ordre de fréquence :

1. **Python vient du Microsoft Store.** C'est le cas le plus courant. Cette
   version crée des venv dont le `python.exe` est un lien vers l'alias du Store,
   inexécutable ailleurs. `launch.bat` le détecte maintenant tout seul (chemin
   contenant `WindowsApps`) et le dit avant de perdre du temps.
   **Correction** : installer Python depuis
   [python.org](https://www.python.org/downloads/) en cochant « Add python.exe to
   PATH », puis *Paramètres > Applications > Alias d'exécution d'application* et
   décocher `python.exe` / `python3.exe`. Enfin `launch.bat reset`.
2. **L'antivirus bloque** l'exécutable fraîchement copié dans `.venv\Scripts\`.
   Ajouter une exception sur le dossier du dépôt.
3. **Le dépôt est sur un lecteur réseau, une clé USB ou un dossier synchronisé**
   (OneDrive, Proton Drive). Le copier sur `C:`.

En attendant, `launch.bat system` installe les dépendances pour l'utilisateur
courant et lance le programme sans venv.

### Erreur `externally-managed-environment` (Linux récent)

Debian 12+, Ubuntu 24.04+ et Fedora refusent `pip install --user`. Rester sur le
venv (`./launch.sh` normal), qui n'est pas concerné.
