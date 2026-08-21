# Manual — Cosmological Distance Calculator

*[Version française](MANUEL.md)*

Everything needed to install, use, modify, rebuild and verify the program.
For an overview see [`README.en.md`](README.en.md); for the current status,
[`PROGRESS.md`](PROGRESS.md).

---

## 1. Installation and start-up

**No prerequisite.** Either download the standalone executable (Windows, macOS,
Linux: see the README), or start from the sources and **the launcher installs
Python itself if it is missing** — winget or the python.org installer on
Windows, Homebrew on macOS, the package manager on Linux. It asks for
confirmation; `COSMO_AUTO_INSTALL=1` grants it in advance.

Then the launchers do the rest: they
create the `.venv/` environment on first run, install `requirements.txt`, drop
a `.venv/.deps-ok` marker and start the program. Subsequent starts are
immediate (~0.6 s).

### 1.1 Windows — `launch.bat`

Double-click for the graphical interface, or from the command line:

| Command | Effect |
|---|---|
| `launch.bat` | graphical interface (through `pythonw.exe`, no leftover console) |
| `launch.bat console` | console version, interactive |
| `launch.bat console 2.34` | direct calculation for z = 2.34 |
| `launch.bat table` | table of the eight presets |
| `launch.bat check` | self-test of the computation core |
| `launch.bat update` | reinstall / update the dependencies |
| `launch.bat reset` | delete the venv and start over |
| `launch.bat system` | work without a venv (`pip install --user`) |
| `launch.bat doctor` | full diagnostics — see §10 |
| `launch.bat help` | command reminder |

The script looks for Python through `py -3` then `python`, and prints a clear
message if it finds none. It forces `chcp 65001` and `PYTHONUTF8=1` so that
accented characters and symbols (`Ω`, `₀`, `•`) display correctly in `cmd.exe`.

**Network drive**: Windows refuses to execute the binaries of a venv located on
an SMB share. If the repository sits on a mapped network drive, `launch.bat`
detects it and places the venv in `%LOCALAPPDATA%\cosmologie-redshift\venv`
instead. `COSMO_VENV` overrides that location.

### 1.2 Linux / macOS — `launch.sh`

```bash
./launch.sh                 # graphical interface
./launch.sh console 2.34    # direct calculation
./launch.sh table           # preset table
./launch.sh check           # self-test
./launch.sh update          # update dependencies
./launch.sh reset           # delete the venv and start over
./launch.sh system          # work without a venv (pip install --user)
./launch.sh doctor          # full diagnostics — see §10
./launch.sh help            # help
```

The script detects a missing display server (`DISPLAY` and `WAYLAND_DISPLAY`
both empty) and says so, instead of letting Qt fail with an obscure message.
It works from any current directory.

**Reuse an existing venv**: `COSMO_VENV=~/work/venv ./launch.sh check`.

If `python3 -m venv` fails on Debian/Ubuntu: `sudo apt install python3-venv`.

### 1.3 Choosing the language

The program is bilingual. In order of priority:

1. the *Language* menu inside the GUI (switches immediately);
2. `--lang en` / `--lang fr` on the command line;
3. the `COSMO_LANG=en` environment variable;
4. the system locale;
5. French by default.

```bash
COSMO_LANG=en ./launch.sh
./launch.sh console 2.34 --lang en
```

### 1.4 Manual installation (no launcher)

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt        # Windows: .venv\Scripts\pip.exe
.venv/bin/python programme/redshift_distance_gui.py
```

`scipy` is not optional: `astropy.cosmology` needs it for the quadratures
(`comoving_distance`, `age`, `lookback_time`). Without it the import succeeds
but every calculation fails.

### 1.5 Special case: a minimal Docker image

On a minimal Python image (a Jupyter container, say), the system libraries Qt
needs are missing. Install them once:

```bash
apt-get update && apt-get install -y libegl1 libgl1 libxkbcommon-x11-0 \
  libdbus-1-3 libxcb-cursor0 libxcb-icccm4 libxcb-keysyms1 libxcb-shape0
```

Without a screen, run with `QT_QPA_PLATFORM=offscreen` (see §6.3).


---

## 2. Console mode

```bash
./launch.sh console          # or  launch.bat console
```

Options:

```bash
./launch.sh console 2.34                  # direct calculation
./launch.sh console 2.34 --omega-k 0.01   # with curvature
./launch.sh console 2.34 --no-shoes       # without the SH0ES comparison
./launch.sh console 2.34 --lang en        # in English
./launch.sh console --help                # option reminder
```

Interactively: type a number, `table` for the preset list, `q` to quit. Both
decimal separators are accepted (`2,34` as well as `2.34`). Beyond z = 1500 the
program warns that the universe was opaque, then computes anyway.

---

## 3. Reading the interface

### 3.1 Subtitle line

```
Planck 2018 (TT,TE,EE+lowE+lensing+BAO) — H₀ = 67.66 km/s/Mpc ·
Ωm+Ων = 0.31110 · ΩΛ = 0.68885 · Ωγ = 5.402e-05 · t₀ = 13.7869 Gyr
```

It states exactly which model is in use. `TT,TE,EE+lowE+lensing+BAO` is the
combination of Planck data sets that produced these parameters (help **F2**
decodes each acronym).

### 3.2 The `z` field and the presets

`z` ranges from 0 to 1500, with 5 decimals and a 0.01 step. Both `.` and `,`
work as decimal separator. The eight buttons load an object or an epoch; each
carries a fact sheet as a tooltip.

| Preset | z | Age of the universe at z |
|---|---|---|
| M 87 | 0.00428 | 13.725 Gyr |
| 3C 273 | 0.158 | 11.745 Gyr |
| z = 1 | 1.0 | 5.851 Gyr |
| z = 2.34 | 2.34 | 2.799 Gyr |
| ULAS J1120 | 7.085 | 749 Myr |
| GN-z11 | 10.6 | 435 Myr |
| Reionisation | 20 | 178 Myr |
| CMB | 1089.8 | 372 kyr |

These ages are computed **in Planck 2018**. They sometimes differ from the
values in the discovery papers, which used the cosmologies of their time
(ULAS J1120: 770 Myr in the paper, 749 here).

### 3.3 The « Model » panel: curvature and SH0ES comparison

| Control | Effect |
|---|---|
| **Curvature Ωk** | range ±0.05, default 0. As soon as Ωk ≠ 0 a fifth row appears: the **transverse** comoving distance D_M, which replaces D_C in D_L and D_A |
| **flat (Ωk = 0)** | back to Planck 2018 |
| **compare with SH0ES** | adds, under each value, the one obtained with H₀ = 73.04, the relative difference, and overlays dotted curves |

Ωk > 0 = open universe (D_M > D_C, sinh); Ωk < 0 = closed (D_M < D_C, sin).
Planck 2018 + BAO measures Ωk = 0.0007 ± 0.0019, hence the default of zero.

Note: the present age t₀ also depends on curvature (13.744 Gyr for
Ωk = +0.01); the « t_L + age = t₀ » check refers to the current model.

### 3.4 Error bars

Every value is given with its 1σ uncertainty, propagated from
σ(H₀) = 0.42 km/s/Mpc and σ(Ωm) = 0.0056 by numerical derivatives:

```
σ_G² = A²σ_H₀² + B²σ_Ωm² + 2ρ·A·B·σ_H₀·σ_Ωm      A = ∂G/∂H₀, B = ∂G/∂Ωm
```

**The cross term is not optional.** H₀ and Ωm are anti-correlated at
ρ = −0.9763 in the Planck fit. That coefficient is *derived*, not assumed:
ω_m = Ωm h² is measured to 0.65 % while Ωm is known to 1.8 % and h to 0.62 %,
which forces the correlation (derivation in
`verif_sage/verif_courbure_sigma.sage`).

| z | σ(D_C) with ρ | without ρ |
|---|---|---|
| 0.01 | 0.62 % | 0.62 % |
| 1 | 0.31 % | 0.70 % |
| 2.34 | **0.17 %** | 0.79 % |
| 5 | 0.13 % | 0.86 % |
| 1089.8 | 0.18 % | 0.95 % |

The status bar shows both. Worth remembering: the relative uncertainty goes
through a **minimum near z ≈ 5** — a « pivot » redshift where the model
predicts distances better than it knows its own parameters. And above all: the
Hubble tension shifts everything by 7.4 %, i.e. 40 times the error bars.

### 3.5 The four distances

| Display | Formula | What it is for |
|---|---|---|
| Comoving distance | `D_C = D_H ∫₀^z dz'/E(z')` | the **present-day** distance of the object |
| Luminosity distance | `D_L = (1+z)·D_M` | photometry: `F = L/(4πD_L²)` |
| Angular diameter distance | `D_A = D_M/(1+z)` | angular sizes: `θ = ℓ/D_A` |
| Light-travel distance | `D_lt = c·t_L` | the « intuitive » value, bounded by `c·t₀` |

`D_A` peaks at 5.846 Gly for z = 1.5921 and then decreases: an identical object
looks larger at z = 5 than at z = 1. It is the most counter-intuitive feature
of the set, and it is marked on the plot.

### 3.6 Cosmological quantities

- **Lookback time** `t_L(z) = ∫₀^z dz'/[(1+z')H(z')]` — light travel time.
- **Age of the universe at z** `t_em(z) = ∫_z^∞ dz'/[(1+z')H(z')]` — switches
  automatically between Gyr, Myr and kyr.
- **Scale factor** `a = 1/(1+z)`, with the size ratio of the universe.
- **E(z) = H(z)/H₀** and `H(z)`: the function that is integrated in every
  distance, displayed so that the origin of the numbers is visible.

### 3.7 The three recession velocities

See help **F3** for the full discussion. In short: only the third one
(`v = H₀·D_C`) is correct in cosmology; it exceeds c beyond z ≈ 1.48 and that
is perfectly legitimate — it is not a propagation speed through space but the
stretching rate of space itself.

### 3.8 Status bar — the permanent checks

```
z = 2.34 · t_L + age = 13.786885 Gyr (deviation 0.00 µGyr)
         · Etherington = 1.000000000000 · σ(D_C) = 0.17 % (0.79 % without the H₀–Ωm correlation)
```

Both identities must hold whatever z. If one of them drifts, astropy has
changed version or default cosmology: do not ignore it.

### 3.9 The plot

Log-log scale, adaptive zoom over `[z/30, 8z]`. Vertical markers: `z=1`,
maximum of `D_A` (which follows Ωk), GN-z11, CMB. Horizontal asymptotes:
`c·t₀` (which the green curve never crosses) and the particle horizon (which
the cyan one approaches).

### 3.10 Help menu

| Key | Contents |
|---|---|
| **F1** | The four distances + the `E(z)` actually computed |
| **F2** | Planck 2018, decoding `TT,TE,EE+lowE+lensing+BAO`, the Hubble tension |
| **F3** | Recession velocities and the superluminal universe |
| **F4** | The eight preselected targets |
| **F5** | How the calculations were verified (SageMath) |
| **F6** | Uncertainties, curvature and the Hubble tension |

---

## 4. Code layout

```
programme/
├── cosmo_core.py                     ALL the physics
├── i18n.py                           interface strings (FR / EN)
├── help_texts.py                     help dialog contents (FR / EN)
├── redshift_distance_gui.py          Qt6 interface (display only)
├── redshift_distance_calculator.py   console version (display only)
├── make_logo.py                      logo generation
└── _ancien/                          leftovers from the PyCharm template, non-functional
```

**Rule**: no formula in the GUI or in the console version. Any change to the
physics goes into `cosmo_core.py`, which exposes:

| Object | Role |
|---|---|
| `compute(z, Ok=0, with_sigma=True, with_shoes=True)` | full dict: distances (ly), times (Gyr), velocities (km/s), `E`, `H_z`, `t0_model`, plus `sigma`, `sigma_pct`, `sigma_indep_pct` and `shoes` |
| `make_cosmology(H0, Om, Ok)` | builds the cosmology (returns `Planck18` itself for the default parameters) |
| `curves(z_grid, Ok=0, H0=…)` | the four distances (Gly) over a grid, **with a disk cache** |
| `format_distance()`, `format_time()`, `format_pm()`, `fmt_num()` | formatting, language-aware (`Gly` vs `G al`, decimal point vs comma) |
| `PRESETS` | the eight targets, with the key of their translated tooltip |
| `help_context()` | the numbers injected into the help texts |

### Adding a language

1. copy an entry of `STRINGS` in `i18n.py` and translate the values;
2. do the same for `HELP` in `help_texts.py`;
3. add the code to `LANGUAGE_NAMES`.

Nothing else: the menu, the tooltips and the units follow automatically.

### Changing cosmology

In `cosmo_core.py`, replace the import:

```python
from astropy.cosmology import Planck18 as cosmo        # current
# from astropy.cosmology import WMAP9 as cosmo         # comparison
```

Everything else follows. Beware: the hard-coded values
`PARTICLE_HORIZON_GLYR`, `EVENT_HORIZON_GLYR`, `Z_DA_MAX` and `DA_MAX_GLYR`
are specific to Planck 2018 — recompute them with `verif_sage/` if the model
changes.

### The plot cache

`curves()` writes into `programme/cache/curves_<hash>.npz` (or into the system
temporary folder if that is not writable). The hash key covers every
cosmological parameter *and* the grid, so changing Ωk, H₀ or the number of
points invalidates the entry automatically.

Real measurements (astropy 8): 600 points in **49 ms** without cache, **4 ms**
with. The gain matters when the grid grows: 5 000 points take 390 ms.
To disable: `COSMO_NO_CACHE=1`, or `curves(..., use_cache=False)`.

---

## 5. The logo

```bash
python programme/make_logo.py
```

Produces `logo.svg` and `logo_{16,32,64,128,256}.png`.

---

## 6. Verifying the calculations

### 6.1 Independent recomputation in SageMath

The scripts do not depend on astropy: they rebuild everything from the
CODATA 2022 constants and the Friedmann equations. With a local SageMath
installation:

```bash
sage verif_sage/verif_cosmo.sage            # full recomputation (~50 s)
sage verif_sage/verif_DL_symbolique.sage    # series expansions, computer algebra
sage verif_sage/verif_courbure_sigma.sage   # correlation and curvature
```

With the official Docker image:

```bash
docker run --rm -v "$PWD:/home/sage/work" sagemath/sagemath \
  sage /home/sage/work/verif_sage/verif_cosmo.sage
```

The scripts write their results as JSON next to themselves; adjust the output
path at the top of each script if the folder is not writable.

### 6.2 astropy reference values and comparison

```bash
.venv/bin/python verif_sage/ref_astropy.py   # reference values -> JSON
.venv/bin/python verif_sage/compare.py       # comparison of the two chains
```

`gen_tables.py` and `gen_table_sigma.py` regenerate the LaTeX tables of the
courses, so that no number is ever copied by hand.

### 6.3 Testing the interface without a screen

```bash
.venv/bin/python verif_sage/test_gui_headless.py            # Linux / macOS
.venv\Scripts\python.exe verif_sage\test_gui_headless.py    # Windows
```

The script forces `QT_QPA_PLATFORM=offscreen` itself. It sweeps 8 values of `z`
(including the limits 0 and 1500), prints the consistency checks, exercises
**both languages** and all seven help dialogs, checks that the numeric fields
accept typed input with either decimal separator, and rewrites the screenshots
in `audit/captures/`. **This is the test to re-run after any change to the
GUI.**

---

## 7. Rebuilding the LaTeX documents

TeX Live must be available on the `PATH` (`texlive-full` on Linux, MacTeX on
macOS, MiKTeX on Windows):

```bash
cd cours
pdflatex -interaction=nonstopmode cours_distances_cosmologiques.tex   # French
pdflatex -interaction=nonstopmode cours_distances_cosmologiques.tex
pdflatex -interaction=nonstopmode course_cosmological_distances.tex   # English
pdflatex -interaction=nonstopmode course_cosmological_distances.tex

cd ../audit
pdflatex -interaction=nonstopmode AUDIT_cosmologie.tex
pdflatex -interaction=nonstopmode AUDIT_cosmologie.tex

rm -f *.aux *.log *.out *.toc
```

**Two passes are mandatory** (table of contents and cross-references).

Checks after building:

```bash
grep -E "^! |Reference.*undefined" *.log     # must be empty
pdfinfo cours_distances_cosmologiques.pdf | grep Pages    # 68
pdfinfo course_cosmological_distances.pdf | grep Pages    # 64
```

The courses include `table_reference.tex` / `table_sigma.tex` (French) and
`table_reference_en.tex` / `table_sigma_en.tex` (English), generated by the
scripts in `verif_sage/`: do not edit them by hand.

---

## 8. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `[ERREUR] Python 3 est introuvable` | Python missing or not in `PATH` | reinstall ticking « Add python.exe to PATH » |
| `ModuleNotFoundError: astropy` | incomplete venv | `launch.bat update` / `./launch.sh update` |
| The app starts then freezes on the first calculation | `scipy` missing | same (`update`) |
| venv creation fails on Debian/Ubuntu | `python3-venv` package missing | `sudo apt install python3-venv` |
| `ImportError: libEGL.so.1` (Linux) | Qt system libraries missing | §1.5 |
| `qt.qpa.plugin: could not load the Qt platform plugin "xcb"` | no display server | `./launch.sh console`, or `QT_QPA_PLATFORM=offscreen` |
| Garbled characters in the Windows console (`Ã©`, `?`) | non-UTF-8 code page | use `launch.bat` (it runs `chcp 65001`) |
| `AttributeError: module 'astropy.units' has no attribute 'Gly'` | the unit is spelled `Glyr` | use `u.Glyr` and `u.lyr` |
| A black console stays open (Windows) | started with `python.exe` | use `launch.bat` (which uses `pythonw.exe`) |
| Status bar: Etherington ≠ 1 or a non-zero µGyr deviation | astropy changed version or cosmology | re-run `verif_sage/` before trusting the numbers |
| The plot is empty at z = 0 | normal: all distances are 0, and log(0) is discarded | use z > 0 |

---


---

## 10. When the installation fails

Both launchers provide three rescue commands:

| Command | Effect |
|---|---|
| `doctor` | diagnostics: Python found and its path, write permissions, venv state, dependencies, display |
| `reset` | delete `.venv/` and start over |
| `system` | skip the venv: `pip install --user`, then run the program |

### « Access denied » while installing the dependencies (Windows)

This is not a network problem: Windows is refusing to execute
`.venv\Scripts\python.exe`. Three causes, by decreasing frequency:

1. **Python comes from the Microsoft Store.** That version creates venvs whose
   `python.exe` is only a link to the Store execution alias, unusable
   elsewhere. `launch.bat` now detects it (path containing `WindowsApps`).
   **Fix**: install Python from [python.org](https://www.python.org/downloads/)
   ticking « Add python.exe to PATH », then *Settings > Apps > App execution
   aliases* and untick `python.exe` / `python3.exe`. Finally `launch.bat reset`.
2. **The repository is on a network drive** (SMB share). Handled
   automatically: the venv is placed in `%LOCALAPPDATA%`. If the message
   persists, copy the repository to `C:` or set `COSMO_VENV`.
3. **The antivirus blocks** the freshly copied executable in `.venv\Scripts\`.
   Add an exception for the repository folder.

Meanwhile, `launch.bat system` installs the dependencies for the current user
and runs the program without a venv.

### `externally-managed-environment` error (recent Linux)

Debian 12+, Ubuntu 24.04+ and Fedora refuse `pip install --user`. Stay with the
venv (plain `./launch.sh`), which is unaffected.
