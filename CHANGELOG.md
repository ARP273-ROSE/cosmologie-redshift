# Changelog

*[Version française](CHANGELOG.fr.md)*

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/), and the
project uses [semantic versioning](https://semver.org/).

---

## [1.4.2] — 2026-11-24

- Sécurité : Python embarqué 3.14.10 (la 3.12.10 ne recevait plus de correctifs de sécurité sous Windows) ; l'interpréteur téléchargé à la construction est vérifié par son empreinte SHA-256. Rapports d'incident : plus de faux avertissement « vigie sans battement » au démarrage.
- Security: bundled Python 3.14.10 (3.12.10 no longer received security fixes on Windows); the interpreter downloaded at build time is checked against its SHA-256. Incident reports: no more false “watchdog without heartbeat” warning at start-up.

## [1.4.1] — 2026-11-18

### Security
- **Signed updates**: each release publishes a manifest (version number and SHA-256 of every
  archive) signed with an Ed25519 key that is not on GitHub; the application installs an update
  only if its archive is listed in it. A stolen GitHub access can no longer push code to
  installed copies.
- **Common kit brought to its current level**: SHA256SUMS and archive checks before extraction,
  address checked after redirects, Linux distribution certificates, up-to-date problem reports.

## [1.4.0] — 2026-10-14

### Added
- **Installers for the three systems**, built by a single workflow (`release.yml`,
  triggered by a `vX.Y.Z` tag): Windows installer (embedded Python, no PyInstaller),
  `.dmg` for Apple Silicon and Intel, `.tar.gz` for Linux x86_64 and ARM64 with
  `installer.sh`; permanent link `releases/latest/download/CosmologicalDistanceCalculator-Setup.exe`.
- **Automatic update** on all three systems (shared kit `updater.py`): GitHub-only
  addresses, release notes in the interface language; from the sources, the
  download page opens.
- **Problem reports**: consent asked at first launch, *Help → Report a problem…*,
  *Send problem reports automatically*; data outside the installation folder.
- **PDF manual** (French and English, house format, real screenshots), opened by
  *Help → User manual (PDF)* (Shift+F1); rebuilt by `docs/captures.py` and
  `docs/src/compiler.py`.
- **Fixed look**: Fusion style, complete palette, embedded Source Sans 3 font —
  independent of the system's light/dark theme and fonts.
- Logo: one SVG source rendered to PNG 16–512, `.ico` and `.icns`; shown in *About*.
- `--check` (used by the package build); tests: hard-coded texts, kit consistency,
  kit wiring under Xvfb, all run by `tests.yml` with the existing checks.

### Changed
- `reporting.py` and `updater.py` were not importable from the Windows package
  (they live one level above `programme/`): problem reports never left an installed
  copy. Fixed.
- The curve cache no longer goes into the installation folder.
- `macos-intel.yml`, the PyInstaller `release.yml` and `release-windows.yml` are
  replaced by the single `release.yml`; the old single-file executables are no
  longer published (the 1.3.3 links already returned 404).
- Removal of personal mentions; installer publisher and the header of
  `reporting.py` now read ARP273-ROSE. The settings location (`QSettings`
  organisation `cosmologie-redshift`) is unchanged.
- Privacy guard `tests/test_confidentialite.py` (files, PDF text, PNG,
  binaries), run by CI.

---

## 1.3.2 — 2026-08-21

### Changed

- **A value typed outside the allowed range is now explained, not silently
  clamped.** Entering Ωk = 12 brought the field back to 0.05 without a word.
  The reason now appears next to the field: Ωk is not a length but the share of
  curvature in the content of the universe, and all the shares add up to 1, so
  Ωk = 12 would require the others to sum to −11. Same treatment for a redshift
  beyond 1500, where the universe is opaque and there is nothing left to
  observe.
- The explanation follows the interface language and clears itself as soon as a
  usable value is entered.
- The curvature tooltip now states the accepted range and why it is that narrow.

---

## 1.3.1 — 2026-08-21

### Fixed

- **The numeric fields can really be typed into.** Entering a value by keyboard
  in the curvature field — and, to a lesser extent, in the `z` field — was
  practically impossible: the field already showed all its decimals
  (`0.0000`), so Qt rejected any further character, and the narrow range
  [−0.05, 0.05] made almost every intermediate value invalid, since `0` has to
  be typed before `0.01`. Every keystroke was refused and the field looked as
  if it only worked with the arrows.
- Validation now accepts anything that looks like a number in progress, and the
  value is only brought into range when it is committed. A value outside the
  bounds is clamped to the nearest one instead of being discarded: typing 9 in
  the curvature field gives 0.05.
- The content is selected when the field takes the focus, so typing replaces it
  instead of being inserted in the middle of the current value.
- The headless test now reproduces the real gesture — focus, then type, without
  selecting anything first. The previous version called `selectAll()`
  beforehand, which no user does, and that is precisely why the defect went
  unnoticed.

---

## 1.3.0 — 2026-08-21

### Added

- **Object lookup by name.** A new `Object` field turns a name into a redshift:
  `m31`, `M 31`, `ngc224`, `Messier 31`, `3c273`, `Sombrero`, `GN-z11` all
  work. The query goes to [SIMBAD](https://simbad.u-strasbg.fr/), the database
  of the Strasbourg astronomical Data Center, and runs in a separate thread, so
  the interface never freezes.
- Case, spaces, hyphens, underscores and leading zeros are ignored, and the
  usual catalogue abbreviations are expanded (`abell` → `ACO`, `messier` → `M`).
  When SIMBAD does not recognise a name as typed, local variants are tried,
  then the identifiers are searched by substring — which is how `gn-z11` finds
  `[OBV2016] GN-z11`.
- **A list to choose from whenever the answer is a guess.** Names that SIMBAD
  itself resolves are applied directly; names found only by searching are
  offered as a list of candidates, closest match first.
- The console version gains `--object NAME`, and at the interactive prompt
  anything that is not a number is taken to be an object name.
- New help entry, *Looking up an object by name* (F7), in both languages.
- Objects without a usable redshift are explained rather than silently applied:
  no redshift in SIMBAD, blueshift (M 31 is approaching), or z < 0.03, where
  peculiar motion inside a cluster still outweighs the expansion.
- `verif_sage/test_simbad.py` checks name normalisation, generated variants,
  match ranking and search patterns offline, then resolves a set of real names
  whose expected answer is known. The network part is skipped, without failing,
  when SIMBAD cannot be reached.

### Note

SIMBAD answers exactly what it is asked, and homonyms exist: `GN-z11` is the
distant galaxy at z = 10.6, while `GNz11` without the hyphen is object no. 11
of the GNZ catalogue, at z = 0.053. The identifier that answered is always
displayed next to the field.

---

## 1.2.0 — 2026-08-21

### Changed

- **The program now starts in the language of the machine**, English by
  default. The system language is read from the POSIX variables (`LC_ALL`,
  `LC_MESSAGES`, `LANGUAGE`, `LANG`), then from the Windows API
  (`GetUserDefaultUILanguage`), then from the macOS preferences
  (`AppleLocale`), then from Python's `locale` module. A French system gets
  French; any other language, or no readable locale, gets English.
- **The language chosen in the *Language* menu is remembered** between
  sessions, so automatic detection no longer overrides a deliberate choice.
  `--lang` and `COSMO_LANG` still take precedence.
- English `README.md` is now the front page, with a link to `README.fr.md`.
- The development log is replaced by this changelog.

### Removed

- The audit report and every reference to it. The verification scripts
  (`verif_sage/`) and the verification appendix of the course remain.

### Fixed

- Language detection relied on `getdefaultlocale()`, which is deprecated and
  often empty on Windows and macOS; the program then fell back to French.

---

## 1.1.0 — 2026-08-21

First public release.

### The program

- Converts a redshift `z` (0 to 1500) into the four cosmological distances of
  ΛCDM with the Planck 2018 parameters: comoving, luminosity, angular
  diameter, light-travel — plus the transverse comoving distance when the
  universe is not flat.
- **1σ error bars** on every value, propagated from σ(H₀) = 0.42 and
  σ(Ωm) = 0.0056 **taking their correlation into account** (ρ = −0.9763,
  derived from the constraint on ω_m = Ωm h²). At z = 2.34 this gives ±0.17 %,
  against ±0.79 % when the cross term is ignored; the status bar shows both.
- **Adjustable spatial curvature** Ωk (±0.05). The transverse comoving distance
  D_M then appears and replaces D_C in D_L and D_A.
- **SH0ES comparison**: a checkbox recomputes everything with H₀ = 73.04 and
  overlays the corresponding curves — every distance shrinks by 7.4 %.
- Lookback time, age of the universe at `z`, scale factor, `E(z)` and `H(z)`.
- Three definitions of the recession velocity side by side (naive Doppler,
  relativistic Doppler, FLRW), since two of them are approximations.
- Log-log plot of the four distances with adaptive zoom, markers for the
  maximum of D_A, GN-z11 and the CMB, and the `c·t₀` and particle-horizon
  asymptotes. Results are cached on disk.
- Two consistency checks displayed permanently: `t_L + t_em = t₀` and the
  Etherington identity `D_L = (1+z)²D_A`.
- Eight presets, from M 87 to the CMB, each with its own fact sheet.
- Console version with `--omega-k`, `--no-shoes`, `--lang`, `--table` and
  `--version`.

### Languages

- Complete **English / French** interface: menus, tooltips, seven help pages,
  status bar and console. The units follow the language (`Gly` / `G al`) and so
  does the decimal separator.
- The program starts in the language of the machine (POSIX variables, Windows
  API, macOS preferences), **English by default** for any language other than
  French. The *Language* menu switches immediately and the choice is remembered
  for the next start; `--lang` and `COSMO_LANG` override it.

### Installation

- **Standalone executables** for Windows, macOS (Apple Silicon) and Linux,
  built, smoke-tested and published automatically by GitHub Actions. No Python
  needed. A macOS Intel build is added as soon as a runner is available.
- Launchers for the three systems that **install Python themselves** when it is
  missing (winget or python.org, Homebrew, or the Linux package manager), then
  create the virtual environment and install the dependencies.
- Discreet update check at start-up (anonymous, non-blocking, disabled with
  `COSMO_NO_UPDATE_CHECK=1`).

### Documentation and verification

- A course in three reading levels — plain language, undergraduate, graduate —
  in French (68 pages) and English (64 pages), from the Friedmann equations to
  the cosmological distances.
- Every number recomputed independently in **SageMath**, without astropy:
  densities rebuilt from the CODATA 2022 constants, exact Fermi-Dirac integral
  for massive neutrinos, 25-digit quadrature. Agreement to 2×10⁻⁶ on the
  distances and 1.5×10⁻⁵ on the ages; the series expansions and the closed form
  of the age were re-derived with computer algebra.
- Automated bilingual audit of the interface (195 strings per language) and a
  headless test of the graphical interface.
