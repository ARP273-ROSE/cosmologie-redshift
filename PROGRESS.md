# Cosmology redshift → distances — progress log

*[Version française](PROGRESSION.md)*

**Origin**: program written in 2024-2025, LaTeX course written in May 2026.
**Repository created**: 2026-08-14 (the code had never been version-controlled).
**Remote**: `github.com/ARP273-ROSE/cosmologie-redshift` (private)

---

## Current status

| Deliverable | Status | Path |
|---|---|---|
| Cross-platform launchers | **✅ 2026-08-14** — venv + dependencies automatic | `launch.bat`, `launch.sh` |
| Qt6 application | **✅ up to date**: ± uncertainties, Ωk curvature, SH0ES comparison, 6 help pages, **bilingual FR/EN** | `programme/redshift_distance_gui.py` |
| Shared computation core | **✅ created 2026-08-14** (the physics is no longer duplicated) | `programme/cosmo_core.py` |
| Console version | **✅ rewritten**, bilingual, with `--omega-k` / `--no-shoes` / `--lang` | `programme/redshift_distance_calculator.py` |
| Course, French | **✅ 68 pp., no compilation error, no unresolved reference** | `cours/cours_distances_cosmologiques.pdf` |
| Course, English | **✅ 64 pp.** | `cours/course_cosmological_distances.pdf` |
| Audit report | **✅ 11 pp.** (French) | `audit/AUDIT_cosmologie.pdf` |
| SageMath verification | **✅ run**, 2×10⁻⁶ agreement on the distances | `verif_sage/` |
| Version control | **✅ done 2026-08-14** — this was the weak point | this repository |

---

## History

### 2026-08-21 (continued) — No prerequisite on any of the three systems

- **Standalone executables for Windows, macOS (Intel and Apple Silicon) and
  Linux**, built, smoke-tested and published by GitHub Actions on every new
  version. Python is no longer needed at all.
- **The launchers install Python themselves** when it is missing: winget then
  the official installer on Windows (looking for the interpreter in the
  standard locations, since the current process PATH is not refreshed yet);
  Homebrew on macOS, installed if needed; apt, dnf, pacman, zypper or apk on
  Linux. A missing `venv` module (Debian) is installed the same way. The user
  is asked for confirmation; `COSMO_AUTO_INSTALL=1` grants it in advance.
- On macOS, `find_python` checks that the interpreter really runs: the system
  ships a stub `python3` that only opens an installation dialog.
- The repository history was squashed to a single commit before publication,
  and the commit address replaced by the GitHub noreply one.

### 2026-08-21 — Publication

- Repository made **public**, first **v1.0.0 release**.
- `.github/workflows/release.yml`: builds the Windows executable (PyInstaller,
  ~107 MB, self-contained), smoke-tests it, creates the tag from the version in
  `programme/updates.py`, and publishes the release with a stable asset name
  plus both course PDFs. Build verified: successful.
- Permanent, version-independent link:
  `https://github.com/ARP273-ROSE/cosmologie-redshift/releases/latest/download/CosmologicalDistanceCalculator-windows.exe`
- Bilingual audit automated (`verif_sage/test_i18n.py`): 195 strings per
  language, identical key sets, no leakage between languages, console included.
- Start-up version check (anonymous, non-blocking, can be disabled).
- Pre-publication clean-up: no personal or private-environment references left;
  impersonal tone in both courses.

### 2026-08-14 (part 5) — Bilingual program and English documentation


- **`programme/i18n.py`**: every interface and console string, in both
  languages, with `t("key", **kw)`. Language selection order: *Language* menu,
  `--lang`, `COSMO_LANG`, system locale, French by default.
- **`programme/help_texts.py`**: the seven help dialogs in both languages, as
  `str.format` templates filled by `help_context()` so that no number is
  hard-coded.
- **Units follow the language**: `G al` / `Gly`, `M al` / `Mly`, and the
  decimal separator (comma in French, point in English) through the new
  `fmt_num()`.
- **English documents**: `README.en.md`, `MANUAL.md`, `PROGRESS.md`, and the
  full course `cours/course_cosmological_distances.tex` (64 pp.).
- The audit report stays in French: it is a dated snapshot of the audit, not
  a living document.

**Keyboard entry fixed at the same time.** The curvature field could only be
changed with the arrows: under a French locale Qt rejects the decimal *point*,
and every keystroke was triggering a full recomputation of the curves. The new
`NumberSpinBox` accepts both separators (locale C plus normalisation) and the
curvature field only applies its value on Enter / focus loss. Checked by
simulated keystrokes in the headless test: `0.02`, `0,015`, `-0.01`, `.03` all
accepted.

### 2026-08-14 (part 4) — Error bars, curvature, cache

Items 1, 3 and 4 of the « what is left » list.

#### 1. Error bars

Every quantity is now displayed as **value ± 1σ**, propagated from
σ(H₀) = 0.42 and σ(Ωm) = 0.0056 by centred numerical derivatives.

The important point was not the propagation but the **cross term**: H₀ and Ωm
are anti-correlated at ρ = −0.9763 in the Planck fit. That coefficient is not
put in by hand, it is **derived** from the constraint on ω_m = Ωm h² (measured
to 0.65 %, against 1.8 % for Ωm and 0.62 % for h), by symbolic solution in Sage.

| z | σ(D_C) with ρ | without ρ |
|---|---|---|
| 0.01 | 0.62 % | 0.62 % |
| 1 | 0.31 % | 0.70 % |
| 2.34 | **0.17 %** | 0.79 % |
| 5 | 0.13 % | 0.86 % |
| 1089.8 | 0.18 % | 0.95 % |

Two lessons: ignoring the correlation overestimates the uncertainty by a
factor of 2 to 5 (the « ±0.6 % » estimate of the audit report was of that
order, lacking the cross term); and the uncertainty goes through a **minimum
near z ≈ 5**, a « pivot » redshift.

**SH0ES comparison**: a checkbox shows the same quantities with H₀ = 73.04 and
overlays dotted curves. Difference: −7.4 % across the board, i.e. ~40 times the
error bars — the dominant uncertainty on a cosmological distance is systematic,
not statistical.

#### 3. Curvature

An **Ωk** field (±0.05). Beyond zero, the **transverse** comoving distance D_M
appears and replaces D_C in D_L and D_A. Implemented through
`comoving_transverse_distance` on a `LambdaCDM` built with the Planck radiation
content (Ode0 = 1 − Om0 − Ωγ − Ων − Ωk).

Two induced fixes: t₀ depends on curvature (13.744 Gyr at Ωk = +0.01), so the
« t_L + age = t₀ » check now refers to the current model; and the maximum of
D_A is read off the curve, so its marker follows Ωk.

Cross-check in SageMath (model rebuilt identically): agreement to **five
decimals** on D_C, D_M, D_L and D_A for Ωk = −0.01, 0, +0.01 at the four
redshifts tested.

#### 4. Plot cache

`curves()` writes to `programme/cache/curves_<hash>.npz`, the key covering all
parameters and the grid. Real measurements: **49 ms → 4 ms** for 600 points.
The « ~1 s » estimate in the audit report was pessimistic (astropy 8
vectorises better); the gain becomes significant when the grid grows
(5 000 points: 390 ms). Automatic fallback to the temporary folder when the
repository is not writable — a common case on a network share.

### 2026-08-14 (part 3) — Repository on a network share

The repository was cloned on a network drive (an SMB share mounted under Windows). **Windows refuses to execute the binaries of a venv located on
a share** (WinError 5), whatever the creation option. `launch.bat` now detects
the network drive (fsutil, or a UNC path) and places the venv in
`%LOCALAPPDATA%\cosmologie-redshift\venv`: the repository can stay on the share.
`COSMO_VENV` selects another location.

### 2026-08-14 (part 2) — « Access denied » on the first Windows run

First real run of `launch.bat` under Windows: the venv is created, then both `pip`
commands fail with **« Access denied »** — and the error message wrongly blamed
the network connection while hiding pip's output.

It is not pip refusing: `cmd.exe` cannot execute `.venv\Scripts\python.exe`.
Cause number 1: **Python installed from the Microsoft Store**, whose venvs
contain a `python.exe` that is merely a link to the execution alias, unusable
elsewhere. Next causes: antivirus, or a repository placed on a network drive /
synchronised folder.

Fixes applied to both launchers: automatic detection of the Store Python,
verification that the venv's python actually runs, pip output no longer hidden,
and three rescue commands (`doctor`, `reset`, `system`).

### 2026-08-14 (part 1) — Launchers and portability

- **`launch.bat`** (Windows) and **`launch.sh`** (Linux/macOS), same
  sub-commands. They create the venv, install `requirements.txt`, drop a
  `.deps-ok` marker and start the program.
- **`requirements.txt`**: numpy, scipy, astropy, PyQt6, pyqtgraph.
- **`.gitattributes`**: `*.bat` in CRLF, `*.sh` in LF, PDF/PNG binary.
- **Code portability**: font fallbacks for the three platforms, `sys.path`
  completed with the script folder, `stdout`/`stderr` forced to UTF-8 (without
  which a cp1252 Windows console raises `UnicodeEncodeError` on `•`, `₀`, `Ω`).

### 2026-08-14 — Full audit and repository creation

Request: find the program (missing, no git repository), audit it together with
its course, verify the calculations in SageMath.

**Found** in `_docs/physique/antikythera_and_old/Physique/` — a catch-all
folder unrelated to the Antikythera mechanism; the course was elsewhere. A git
repository existed but **with no commit and no remote**.

**Audit verdict**: the computation engine is correct, its documentation was not.

#### Verification (3 independent chains)

1. astropy 8.0.1 + scipy (the backend under audit);
2. full recomputation in SageMath **without astropy**: densities rebuilt from
   CODATA 2022, **exact** Fermi-Dirac integral for the massive neutrinos
   (astropy uses the Komatsu 2011 fit), mpmath at 25 digits;
3. symbolic algebra for the series expansions and the closed form of the age.

| Quantity | astropy ↔ SageMath difference |
|---|---|
| E(z) | 1.79 × 10⁻⁵ |
| D_C, D_L, D_A | 2.10 × 10⁻⁶ |
| lookback time | 4.58 × 10⁻⁷ |
| age | 1.50 × 10⁻⁵ |

Internal checks: Etherington to 2×10⁻¹⁶, `t_L + age = t₀` to 2×10⁻¹⁰ Gyr,
maximum of D_A at z = 1.592133 by both methods.

#### Program fixes (14 findings)

- **Major** — help F1 displayed `E(z) = √(Ωm(1+z)³+ΩΛ)`, which is not the
  formula in use (−12.8 % on E at the CMB; an age of 479 kyr instead of 372).
- **Major** — « Ωm = 0.3111 » shown while `Planck18.Om0 = 0.30966`; the
  difference is the neutrinos.
- Only one recession velocity displayed (`cz`, the worst one) → all three.
- Reference age 13.787 hard-coded → read from the backend.
- Age at high z shown as « 0.0004 Gyr » → Gyr/Myr/kyr switching.
- Outdated preset ages: GN-z11 420 → **435 Myr**, ULAS J1120 770 → **749 Myr**,
  CMB 380 000 → **372 000 years**.
- M 87: « ~55 Mly » without explaining that z gives 62 Mly (peculiar velocity).
- GUI/console duplication → `cosmo_core.py`.
- Console: the warning « z > 10: less accurate results » is false.
- PyCharm leftovers `main.py`/`test.py` (one of which crashes) → `_ancien/`.
- Additions: E(z) and H(z) displayed, help « verification », two permanent
  consistency checks in the status bar, D_A maximum marker and asymptotes.

#### Course fixes (17 errors)

The four major ones:

1. `D_H = c/H₀` given as **4.431 Gly instead of 14.4516** (Mpc ↔ ly confusion,
   factor 3.26) — the error propagated into a table and contradicted the text
   two chapters later;
2. the « numerical calculation » table mixed **Gpc and Gly** in the same column;
3. **three of the four series expansions were wrong** (D_C carried the
   coefficient of D_L: 10 % error at z = 0.1);
4. the « closed form of ∫dz/E » is in fact that of the **age**, with a
   prefactor wrong by a factor of 3 — and the distance integral has no
   elementary closed form.

Then: q₀ = −0.527 → −0.5334; M 87 « 19 Mly » → 18.96 Mpc = 61.8 Mly; 3C 273,
z = 1, z = 10.6 and the CMB recomputed; particle horizon 46.28 → 46.2005;
high-z asymptotes corrected; v_rec(CMB) 3.16 c → 3.134 c; « 380 000 years » vs
« 372 kyr » (internal contradiction) harmonised; Ω_r 9.24 → 9.139 × 10⁻⁵ with
Ω_γ / Ω_ν separated; `u.Gly` (which does not exist) → `u.Glyr`; event horizon
16 → 16.5808 Gly.

**Additions**: a section « The E(z) actually computed » and an appendix
« Independent verification of the calculations (SageMath) ». The course went
from 58 to 66 pages.

What was correct: the z = 2.34 case (the running example, the only one actually
computed), all the FLRW derivations, Etherington, the treatment of redshift,
recombination, and the bibliography.

---

## What is left to do

| # | Topic | Details |
|---|---|---|
| 1 | **Multi-cosmology comparator** | the SH0ES comparison is done; WMAP9 / a free cosmology (editable H₀ and Ωm) on the same plot is not |
| 2 | **Export** | a « copy results » button or CSV export over a range of z |
| 3 | **Uncertainty on Ωk** | the ± only propagate σ(H₀) and σ(Ωm); add σ(Ωk) = 0.0019 when curvature is enabled |
| 4 | **Validate `launch.bat` on Windows** | partly validated (the diagnostics did identify the network drive); a complete run after the fix remains to be confirmed |
| 5 | **Translate the audit report** | `AUDIT_cosmologie.pdf` is still French only |

---

## Traps not to reintroduce

- `Planck18.Om0 = 0.30966`, **never 0.3111**: the latter is `Om0 + Onu0`.
- The astropy units are `u.Glyr` and `u.lyr` — `u.Gly` and `u.ly` do not exist.
- `1 Mpc = 3.2616 × 10⁶ ly`: `D_H = 4430.87 Mpc` is **14.45** Gly, not 4.43.
- The two-term `E(z)` formula is fine for **distances** up to z ~ 10, wrong for
  **ages** at high z (the age integral is dominated by the radiation era).
- Never copy a number by hand into the course: go through the generators in
  `verif_sage/`.
- After any GUI change, re-run the headless test (MANUAL §6.3).
- The error bars **must** keep the cross term: without it σ(D_C) is
  overestimated by a factor of 2 to 5 (ρ = −0.9763, not 0).
- The « t_L + age = t₀ » check compares against `d["t0_model"]`, never against
  the constant `T0_GYR`: t₀ changes with curvature.
- `curves()` must tolerate a non-writable folder (repository on a network
  share): the cache is a bonus, never a requirement.
- Any new interface string goes into `i18n.py`, in **both** languages.
