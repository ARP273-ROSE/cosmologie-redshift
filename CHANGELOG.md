# Changelog

*[Version française](CHANGELOG.fr.md)*

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/), and the
project uses [semantic versioning](https://semver.org/).

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
