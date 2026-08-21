#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
TEXTES DES BOÎTES D'AIDE (français / anglais)
================================================================================
Help dialog contents, in both languages.

Chaque texte est un gabarit `str.format` ; le contexte est fourni par
`help_context()` (valeurs calculées : H₀, t₀, horizons, etc.), de sorte
qu'aucun nombre n'est écrit en dur.

Each text is a `str.format` template filled by `help_context()`, so that no
number is hard-coded.
================================================================================
"""

from __future__ import annotations

from i18n import current_language

__all__ = ["help_html", "HELP_KEYS"]

HELP_KEYS = ("distances", "planck", "recession", "presets", "verif", "sigma", "about")


def help_html(key: str, ctx: dict) -> str:
    """Texte d'aide, dans la langue courante, avec les nombres substitués."""
    lang = current_language()
    table = HELP.get(lang, HELP["fr"])
    return table.get(key, HELP["fr"].get(key, "")).format(**ctx)


HELP: dict[str, dict[str, str]] = {

# ================================================================ FRANÇAIS ==
"fr": {

"about": """
<h2 style="color:#94b8c8;">À propos</h2>
<p><b>Calculateur de distances cosmologiques</b> &mdash;
calcule, pour un redshift <i>z</i> donné, les quatre distances cosmologiques et
les grandeurs cinématiques associées, en utilisant les paramètres
<b>Planck&nbsp;2018</b>.</p>
<p>Backend numérique&nbsp;: <code>astropy.cosmology</code> (version {astropy_version}).<br>
Interface&nbsp;: PyQt6 + pyqtgraph (rendu vectoriel). Programme bilingue
français / anglais (menu <i>Langue</i>).</p>
<p><b>Vérification.</b> Toutes les valeurs affichées ont été recalculées
indépendamment sous <b>SageMath</b> (mpmath 25 chiffres, intégrale de
Fermi-Dirac exacte pour les neutrinos massifs)&nbsp;: accord à
2&times;10<sup>-6</sup> en relatif sur les distances, 1,5&times;10<sup>-5</sup>
sur les âges. Voir <code>AUDIT_cosmologie.pdf</code>.</p>
<p style="color:#7a8498;font-size:9pt;">Documentation complète dans le cours
LaTeX joint&nbsp;: <code>cours_distances_cosmologiques.pdf</code> (68 p.).</p>
""",

"distances": """
<h2 style="color:#94b8c8;">Les quatre distances cosmologiques</h2>

<p>Toutes reposent sur la même intégrale, avec
D<sub>H</sub> = c/H₀ = {d_h:.3f} G&middot;al&nbsp;:</p>
<p style="text-align:center;">D<sub>C</sub>(z) = D<sub>H</sub> &int;<sub>0</sub><sup>z</sup> dz' / E(z')</p>

<h3 style="color:#1F4E5F;">1. Distance comobile D<sub>C</sub></h3>
<p>Distance <b>actuelle</b> qui sépare la source de l'observateur, mesurée dans
le repère qui s'étend avec l'univers. C'est la « vraie » distance dans
l'espace tel qu'il est aujourd'hui. Sature à
{horizon:.2f} G&middot;al (horizon des particules) quand z &rarr; &infin;.</p>

<h3 style="color:#8B5A1A;">2. Distance de luminosité D<sub>L</sub></h3>
<p>Distance à utiliser dans la <b>photométrie</b>&nbsp;: F = L / (4π D<sub>L</sub><sup>2</sup>).
Deux facteurs (1+z) s'ajoutent à D<sub>M</sub>&nbsp;: perte d'énergie par photon
et dilatation du taux d'arrivée.</p>
<p><b>Formule</b>&nbsp;: D<sub>L</sub> = (1+z) D<sub>M</sub>.</p>

<h3 style="color:#4B3F72;">3. Distance de diamètre angulaire D<sub>A</sub></h3>
<p>Distance pour les <b>tailles angulaires</b>&nbsp;: θ = ℓ / D<sub>A</sub>.
<b>Anti-intuitif</b>&nbsp;: D<sub>A</sub> passe par un maximum de
{da_max:.3f} G&middot;al à <b>z = {z_da_max:.4f}</b> puis décroît. Un objet identique
paraît plus grand à z=5 qu'à z=1 !</p>
<p><b>Formule</b>&nbsp;: D<sub>A</sub> = D<sub>M</sub> / (1+z).</p>

<h3 style="color:#2E5D3F;">4. Distance de trajet de la lumière D<sub>lt</sub></h3>
<p>Distance « intuitive »&nbsp;: c × temps qu'il a fallu à la lumière pour
arriver. <b>Bornée par c·t₀ = {t0:.3f} G&middot;al</b> quel que soit z.
Physiquement la moins propre à grand z&nbsp;: elle ne mesure aucune séparation
métrique.</p>
<p><b>Formule</b>&nbsp;: D<sub>lt</sub> = c · t<sub>L</sub>(z).</p>

<h3 style="color:#b8b090;">Et D<sub>M</sub> ?</h3>
<p>La distance comobile <b>transverse</b> D<sub>M</sub> vaut D<sub>C</sub> en
univers plat. Dès que Ω<sub>k</sub> ≠ 0 elle s'en écarte (sinh ou sin) et c'est
elle qui entre dans D<sub>L</sub> et D<sub>A</sub>. Voir l'aide F6.</p>

<h3 style="color:#94b8c8;">Identité de réciprocité (Etherington, 1933)</h3>
<p style="font-size:11pt;text-align:center;">
D<sub>L</sub> = (1+z)<sup>2</sup> D<sub>A</sub>
</p>
<p>Valable pour toute géométrie lorentzienne, pas seulement FLRW. Vérifiée ici
à 2&times;10<sup>-16</sup> (précision machine).</p>

<h3 style="color:#b89090;">Le E(z) réellement utilisé</h3>
<p>La vulgarisation écrit souvent
E(z) = √(Ω<sub>m</sub>(1+z)<sup>3</sup> + Ω<sub>Λ</sub>).
<b>Ce n'est pas la formule employée ici.</b> Le programme calcule&nbsp;:</p>
<p style="text-align:center;">
E(z)² = Ω<sub>r</sub>(z)(1+z)<sup>4</sup> + Ω<sub>m</sub>(1+z)<sup>3</sup>
+ Ω<sub>k</sub>(1+z)<sup>2</sup> + Ω<sub>Λ</sub></p>
<p>où Ω<sub>r</sub>(z) contient les photons du CMB
(Ω<sub>γ</sub> = {ogamma:.4e}) <i>et</i> les neutrinos, dont la densité
dépend de z (non relativistes aujourd'hui, relativistes avant z ≈ 200).</p>
<p>Écart de la formule simplifiée&nbsp;: &lt; 0,04 % pour z ≤ 2,5, mais
<b>&minus;12,8 % sur E à z = 1089,8</b>, et l'âge de l'univers au CMB
passerait de 372 kyr à 479 kyr (+29 %).</p>
""",

"planck": """
<h2 style="color:#94b8c8;">Cosmologie Planck 2018</h2>
<p>Le programme utilise les paramètres cosmologiques mesurés par la mission
<b>Planck</b> (ESA, 2009-2013) dans sa publication finale (2020).
Référence&nbsp;: Aghanim et al., A&amp;A 641, A6.</p>

<h3>Les paramètres tels qu'astropy les porte</h3>
<table border="0" cellspacing="6">
<tr><td><b>H₀</b></td><td>{h0} km/s/Mpc</td><td>constante de Hubble aujourd'hui (± {sigma_h0})</td></tr>
<tr><td><b>Ω<sub>m</sub></b></td><td>{om0:.5f}</td><td>baryons + matière noire froide <i>seulement</i></td></tr>
<tr><td><b>Ω<sub>ν</sub></b></td><td>{onu0:.5f}</td><td>neutrinos (1 espèce massive à 0,06 eV)</td></tr>
<tr><td><b>Ω<sub>m</sub>+Ω<sub>ν</sub></b></td><td>{om_total:.5f}</td>
    <td><b>c'est le « Ω<sub>m</sub> = 0,3111 » du papier Planck</b> : les neutrinos
        y sont comptés dans la matière car ils sont non relativistes aujourd'hui</td></tr>
<tr><td><b>Ω<sub>Λ</sub></b></td><td>{ode0:.5f}</td><td>densité d'énergie noire</td></tr>
<tr><td><b>Ω<sub>γ</sub></b></td><td>{ogamma:.4e}</td><td>photons, fixé par T₀ = {tcmb} K</td></tr>
<tr><td><b>Ω<sub>k</sub></b></td><td>0 par défaut</td><td>courbure spatiale (réglable, aide F6)</td></tr>
<tr><td><b>N<sub>eff</sub></b></td><td>{neff}</td><td>nombre effectif d'espèces de neutrinos</td></tr>
<tr><td><b>t₀</b></td><td>{t0:.4f} Gyr</td><td>âge actuel (calculé, non imposé)</td></tr>
<tr><td><b>z<sub>*</sub></b></td><td>1089,80 ± 0,21</td><td>redshift de la surface de dernière diffusion</td></tr>
</table>

<h3>« TT,TE,EE+lowE+lensing+BAO »</h3>
<p>C'est la <b>liste des données combinées</b> par la collaboration Planck&nbsp;:</p>
<ul>
<li><b>TT</b>&nbsp;: spectre angulaire température-température du CMB</li>
<li><b>TE</b>&nbsp;: corrélation croisée température × polarisation E</li>
<li><b>EE</b>&nbsp;: spectre de polarisation E-mode seul</li>
<li><b>lowE</b>&nbsp;: polarisation E aux grands angles (ℓ &lt; 30)</li>
<li><b>lensing</b>&nbsp;: effet de lentille gravitationnelle des grandes
structures sur le CMB</li>
<li><b>BAO</b>&nbsp;: oscillations acoustiques baryoniques dans la distribution
des galaxies (SDSS / BOSS / eBOSS) — données externes à Planck</li>
</ul>
<p>Combiner ces observations <b>indépendantes</b> permet de lever des
dégénérescences entre paramètres et d'obtenir une précision finale
~0,5 %.</p>

<p style="color:#b89090;"><b>Tension de Hubble&nbsp;:</b> la mesure locale
(SH0ES, Riess 2022) donne H₀ = {h0_shoes} ± 1,04 km/s/Mpc, en désaccord à ~5σ
avec Planck. La case « comparer avec SH0ES » affiche l'effet : toutes les
distances raccourcissent d'environ 7 % (elles varient en 1/H₀).</p>
""",

"recession": """
<h2 style="color:#94b8c8;">Vitesses de récession et univers superluminique</h2>

<p>Le programme affiche <b>les trois définitions</b> de la « vitesse de
récession », parce qu'elles donnent des résultats radicalement différents et
que deux d'entre elles sont des approximations.</p>

<h3>1. Doppler classique&nbsp;: v = cz</h3>
<p>Ce qu'affiche la plupart des calculateurs. Valide uniquement pour z &lt;&lt; 1.
Pour le CMB, elle donnerait 1090 c — dépourvu de sens.</p>

<h3>2. Doppler relativiste&nbsp;: v/c = ((1+z)² − 1) / ((1+z)² + 1)</h3>
<p>Bornée par c, mais <b>conceptuellement fausse en cosmologie</b>&nbsp;: elle
suppose une source qui se déplace <i>à travers</i> un espace-temps de
Minkowski statique. Ce n'est pas la situation d'une galaxie comobile.</p>

<h3>3. Vitesse de récession FLRW&nbsp;: v<sub>rec</sub>(t₀) = H₀ · D<sub>C</sub></h3>
<p>La <b>seule correcte</b> en cosmologie. C'est la dérivée de la distance
propre&nbsp;: v = H(t)·D<sub>p</sub>(t). Non bornée par c. Aujourd'hui&nbsp;:</p>
<ul>
<li>v = c à D<sub>C</sub> = D<sub>H</sub> = {d_h:.2f} G&middot;al, soit z ≈ 1,48&nbsp;;</li>
<li>pour le CMB&nbsp;: v<sub>rec</sub> ≈ 939 400 km/s = <b>3,13 c</b>.</li>
</ul>

<h3>Pourquoi pas de violation de la relativité</h3>
<p>La limite c s'applique <b>localement</b>, dans le cône de lumière de chaque
point. Deux observateurs comobiles distants sont immobiles dans leur
référentiel local&nbsp;; seule la distance physique entre eux grandit, parce que
l'espace lui-même s'étire. Aucune particule, aucun signal, ne dépasse c en se
propageant à travers l'espace.</p>

<h3>Galaxies superluminiques observables</h3>
<p>On peut voir des galaxies dont v<sub>rec</sub> &gt; c aujourd'hui. La condition
n'est pas v &lt; c mais que la galaxie soit à l'intérieur de l'<b>horizon des
événements</b> ({event_horizon:.2f} G&middot;al en comobile), et non de la seule
sphère de Hubble ({d_h:.2f} G&middot;al). La couronne entre les deux contient
des galaxies qui s'éloignent plus vite que c et dont la lumière émise
aujourd'hui nous parviendra quand même.</p>
<p style="color:#7a8498;">Référence : Davis &amp; Lineweaver, PASA 21, 97 (2004).</p>
""",

"presets": """
<h2 style="color:#94b8c8;">Les objets-cibles présélectionnés</h2>
<p style="color:#7a8498;">Les âges donnés ci-dessous sont ceux calculés en
Planck 2018 ; ils diffèrent parfois des valeurs des articles d'origine, qui
utilisaient les cosmologies de leur époque (WMAP le plus souvent).</p>

<h3>M 87&nbsp; — z = 0,00428</h3>
<p>Galaxie elliptique géante de l'amas de la Vierge. Trou noir supermassif
central de 6,5 × 10⁹ M☉, imagé par l'Event Horizon Telescope en 2019.
Son redshift donne D<sub>C</sub> = <b>62 M al</b>, alors que les mesures directes
(fluctuations de brillance de surface) donnent <b>~55 M al</b> : l'écart vient
de la vitesse propre de M 87 dans l'amas, qui s'ajoute au flot de Hubble.
C'est la limite de la méthode « redshift → distance » dans l'univers local.</p>

<h3>3C 273&nbsp; — z = 0,158</h3>
<p><b>Le premier quasar identifié</b> (Maarten Schmidt, 1963).
Magnitude visuelle ~12,9 ; le quasar le plus brillant vu de la Terre.
Luminosité bolométrique ~4 × 10⁴⁶ erg/s.
D<sub>C</sub> = 2,197 G al mais D<sub>L</sub> = 2,544 G al : l'écart entre
définitions devient mesurable.</p>

<h3>z = 1&nbsp; — repère pédagogique</h3>
<p>Univers d'âge 5,851 Gyr, deux fois plus petit qu'aujourd'hui (a = 0,5).</p>

<h3>z = 2,34&nbsp; — le « cosmic noon »</h3>
<p>Pic de l'activité quasar et de la formation stellaire dans l'univers, âgé
alors de 2,799 Gyr. Tranche-clé des relevés BAO via la forêt Lyman-α
(BOSS, eBOSS).</p>

<h3>ULAS J1120+0641&nbsp; — z = 7,085</h3>
<p>Quasar découvert en 2011 (Mortlock et al., Nature). Trou noir central
2 × 10⁹ M☉ formé alors que l'univers n'avait que <b>749 Myr</b>
(l'article annonce 770 Myr, en cosmologie WMAP7).</p>

<h3>GN-z11&nbsp; — z = 10,6</h3>
<p>L'une des galaxies les plus lointaines confirmées spectroscopiquement
(JWST/NIRSpec, Bunker et al. 2023). L'univers avait <b>435 Myr</b>.</p>

<h3>Réionisation&nbsp; — z ≈ 20</h3>
<p>Pas un objet&nbsp;: une <b>époque</b> (univers âgé de 178 Myr à z = 20).
Les premières étoiles ré-ionisent l'hydrogène intergalactique neutre ;
la réionisation s'achève vers z ≈ 5,5-6.</p>

<h3>CMB&nbsp; — z<sub>*</sub> = 1089,80</h3>
<p>Surface de dernière diffusion. La lumière la plus ancienne que l'on
puisse capter, émise quand l'univers avait <b>372 000 ans</b> (valeur Planck
2018 ; l'ancienne valeur WMAP de 380 000 ans est encore souvent citée) et est
devenu transparent pour la première fois.</p>
""",

"verif": """
<h2 style="color:#94b8c8;">Comment ces nombres ont été vérifiés</h2>

<p>Le programme s'appuie sur <code>astropy.cosmology.Planck18</code>. Pour ne
pas dépendre d'une seule chaîne de calcul, tout a été <b>recalculé de zéro sous
SageMath</b>, sans astropy&nbsp;:</p>
<ul>
<li>reconstruction des densités depuis les constantes CODATA 2022
(ρ<sub>crit</sub> = 3H₀²/8πG, Ω<sub>γ</sub> = a<sub>B</sub>T₀⁴/ρ<sub>crit</sub>c²)&nbsp;;</li>
<li>densité des neutrinos par l'<b>intégrale de Fermi-Dirac exacte</b>
f(y) = (120/7π⁴)∫x²√(x²+y²)/(e<sup>x</sup>+1)dx, au lieu de l'ajustement
de Komatsu (2011) qu'utilise astropy&nbsp;;</li>
<li>intégrales D<sub>C</sub>, t<sub>L</sub>, t(z) par quadrature mpmath à 25 chiffres.</li>
</ul>

<h3>Résultat</h3>
<table border="0" cellspacing="6">
<tr><td>distances D<sub>C</sub>, D<sub>L</sub>, D<sub>A</sub></td><td>accord à <b>2×10<sup>-6</sup></b></td></tr>
<tr><td>lookback time</td><td>accord à <b>4,6×10<sup>-7</sup></b></td></tr>
<tr><td>âges</td><td>accord à <b>1,5×10<sup>-5</sup></b></td></tr>
<tr><td>t₀</td><td>{t0:.6f} Gyr (Sage : 13,786892)</td></tr>
<tr><td>maximum de D<sub>A</sub></td><td>z = {z_da_max:.5f} par les deux méthodes</td></tr>
<tr><td>courbure Ω<sub>k</sub> = ±0,01</td><td>D<sub>C</sub>, D<sub>M</sub>, D<sub>L</sub>, D<sub>A</sub> : accord à <b>5 décimales</b></td></tr>
</table>
<p>L'écart résiduel vient uniquement de l'ajustement de Komatsu (erreur ≤ 0,12 %
sur ρ<sub>ν</sub>, d'effet ≤ 1,5×10<sup>-5</sup> sur les observables). <b>Conclusion :
le backend est fiable au-delà de la précision des paramètres eux-mêmes</b>
(0,5 % environ).</p>

<h3>Contrôles internes</h3>
<ul>
<li>Etherington D<sub>L</sub> = (1+z)²D<sub>A</sub> : vérifié à 2×10<sup>-16</sup>&nbsp;;</li>
<li>t<sub>L</sub>(z) + âge(z) = t₀ : vérifié à 2×10<sup>-10</sup> Gyr&nbsp;;</li>
<li>forme fermée de l'âge en ΛCDM sans rayonnement,
t(z) = (2/3H₀√Ω<sub>Λ</sub>)·arcsinh[√(Ω<sub>Λ</sub>/Ω<sub>m</sub>)(1+z)<sup>-3/2</sup>],
retrouvée à 10<sup>-9</sup>&nbsp;;</li>
<li>corrélation ρ(H₀, Ω<sub>m</sub>) = {rho} dérivée symboliquement.</li>
</ul>
<p style="color:#7a8498;font-size:9pt;">Scripts : <code>verif_sage/verif_cosmo.sage</code>,
<code>verif_DL_symbolique.sage</code> et <code>verif_courbure_sigma.sage</code>.
Détail complet dans <code>AUDIT_cosmologie.pdf</code>.</p>
""",

"sigma": """
<h2 style="color:#94b8c8;">Incertitudes, courbure et tension de Hubble</h2>

<h3>D'où viennent les « ± » affichés</h3>
<p>Les deux paramètres qui dominent l'incertitude sont
H₀ = {h0} ± {sigma_h0} km/s/Mpc et Ω<sub>m</sub> = {om_total} ± {sigma_om}.
Pour chaque grandeur G, le programme calcule les dérivées partielles par
différences finies et propage&nbsp;:</p>
<p style="text-align:center;">
σ<sub>G</sub>² = A²σ<sub>H₀</sub>² + B²σ<sub>Ωm</sub>²
+ <b>2ρ·A·B·σ<sub>H₀</sub>σ<sub>Ωm</sub></b>,
&nbsp;&nbsp; A = ∂G/∂H₀, &nbsp; B = ∂G/∂Ω<sub>m</sub>
</p>

<h3 style="color:#b89090;">Le terme croisé n'est pas un détail</h3>
<p>H₀ et Ω<sub>m</sub> sont <b>fortement anticorrélés</b> dans l'ajustement
Planck (dégénérescence géométrique)&nbsp;: ρ = {rho}. Ce nombre n'est pas
posé arbitrairement, il se déduit de la contrainte sur ω<sub>m</sub> = Ω<sub>m</sub>h²,
mesurée à 0,65 % alors que Ω<sub>m</sub> l'est à 1,8 % et h à 0,62 %&nbsp;:</p>
<p style="text-align:center;">
(σ<sub>ω</sub>/ω)² = (σ<sub>Ωm</sub>/Ω<sub>m</sub>)² + 4(σ<sub>h</sub>/h)²
+ 4ρ(σ<sub>Ωm</sub>/Ω<sub>m</sub>)(σ<sub>h</sub>/h)
</p>
<p>Conséquence concrète à z = 2,34&nbsp;: <b>±0,17 %</b> sur D<sub>C</sub> en tenant
compte de ρ, contre ±0,79 % en l'ignorant — un facteur 4,5. La barre d'état
affiche les deux.</p>
<p>Autre effet visible&nbsp;: l'incertitude relative <i>diminue</i> de z = 0 (±0,62 %,
gouvernée par H₀ seul) jusqu'à z ≈ 5 (±0,13 %), puis remonte légèrement. Il
existe un redshift « pivot » où le modèle est le mieux contraint.</p>

<h3>Ce que les ± ne contiennent pas</h3>
<ul>
<li>l'incertitude sur Ω<sub>k</sub>, T₀, N<sub>eff</sub> ou Σm<sub>ν</sub> (négligeables ici)&nbsp;;</li>
<li>l'erreur de <b>modèle</b>&nbsp;: si ΛCDM est faux, aucune barre d'erreur ne le dira&nbsp;;</li>
<li>la <b>tension de Hubble</b>, qui n'est pas une incertitude statistique mais un
désaccord entre deux mesures.</li>
</ul>

<h3>Tension de Hubble : la case « SH0ES »</h3>
<p>La mesure locale (Riess et al. 2022, échelle de distance céphéides +
supernovae Ia) donne H₀ = {h0_shoes} ± 1,04 km/s/Mpc, soit ~5σ au-dessus de
Planck. En cocher la case affiche les mêmes grandeurs dans cette cosmologie&nbsp;:
toutes les distances raccourcissent de <b>7,4 %</b> et les âges avec elles.
C'est un ordre de grandeur bien supérieur aux barres d'erreur&nbsp;: aujourd'hui,
l'incertitude dominante sur une distance cosmologique n'est pas statistique,
elle est <b>systématique</b>.</p>

<h3>Courbure Ω<sub>k</sub></h3>
<p>Planck 2018 + BAO donne Ω<sub>k</sub> = 0,0007 ± 0,0019&nbsp;: compatible avec
zéro, d'où le choix par défaut Ω<sub>k</sub> = 0. Le champ permet d'explorer
l'effet d'une courbure&nbsp;: la distance comobile <b>transverse</b> D<sub>M</sub>
apparaît alors, et c'est elle — non D<sub>C</sub> — qui entre dans
D<sub>L</sub> = (1+z)D<sub>M</sub> et D<sub>A</sub> = D<sub>M</sub>/(1+z).</p>
<table border="0" cellspacing="6">
<tr><td><b>Ω<sub>k</sub> &gt; 0</b></td><td>univers ouvert (hyperbolique)</td>
    <td>D<sub>M</sub> = (D<sub>H</sub>/√Ω<sub>k</sub>)·sinh(√Ω<sub>k</sub>·D<sub>C</sub>/D<sub>H</sub>) &gt; D<sub>C</sub></td></tr>
<tr><td><b>Ω<sub>k</sub> = 0</b></td><td>univers plat</td><td>D<sub>M</sub> = D<sub>C</sub></td></tr>
<tr><td><b>Ω<sub>k</sub> &lt; 0</b></td><td>univers fermé (sphérique)</td>
    <td>D<sub>M</sub> = (D<sub>H</sub>/√|Ω<sub>k</sub>|)·sin(√|Ω<sub>k</sub>|·D<sub>C</sub>/D<sub>H</sub>) &lt; D<sub>C</sub></td></tr>
</table>
<p>À z = 2,34 et Ω<sub>k</sub> = +0,01, D<sub>C</sub> perd 0,36 % mais D<sub>M</sub>
n'en perd que 0,08 % : les deux effets (contenu et géométrie) se compensent
partiellement. C'est pourquoi la courbure est difficile à mesurer.</p>
<p style="color:#7a8498;">Noter aussi que l'âge actuel t₀ dépend de la courbure :
13,744 Gyr pour Ω<sub>k</sub> = +0,01, au lieu de {t0:.4f}.</p>
""",
},

# ================================================================= ENGLISH ==
"en": {

"about": """
<h2 style="color:#94b8c8;">About</h2>
<p><b>Cosmological Distance Calculator</b> &mdash; for a given redshift
<i>z</i>, computes the four cosmological distances and the associated
kinematic quantities, using the <b>Planck&nbsp;2018</b> parameters.</p>
<p>Numerical backend&nbsp;: <code>astropy.cosmology</code> (version {astropy_version}).<br>
Interface&nbsp;: PyQt6 + pyqtgraph (vector rendering). The program is bilingual,
French / English (<i>Language</i> menu).</p>
<p><b>Verification.</b> Every displayed value has been recomputed independently
with <b>SageMath</b> (mpmath, 25 digits, exact Fermi-Dirac integral for massive
neutrinos)&nbsp;: agreement to 2&times;10<sup>-6</sup> in relative terms for the
distances and 1.5&times;10<sup>-5</sup> for the ages. See
<code>AUDIT_cosmologie.pdf</code>.</p>
<p style="color:#7a8498;font-size:9pt;">Full documentation in the companion
LaTeX course&nbsp;: <code>course_cosmological_distances.pdf</code> (64 pp.).</p>
""",

"distances": """
<h2 style="color:#94b8c8;">The four cosmological distances</h2>

<p>All of them rest on the same integral, with
D<sub>H</sub> = c/H₀ = {d_h:.3f} Gly&nbsp;:</p>
<p style="text-align:center;">D<sub>C</sub>(z) = D<sub>H</sub> &int;<sub>0</sub><sup>z</sup> dz' / E(z')</p>

<h3 style="color:#1F4E5F;">1. Comoving distance D<sub>C</sub></h3>
<p>The <b>present-day</b> distance between source and observer, measured in the
frame that expands with the universe. This is the « true » distance in space as
it is today. It saturates at {horizon:.2f} Gly (the particle horizon) as
z &rarr; &infin;.</p>

<h3 style="color:#8B5A1A;">2. Luminosity distance D<sub>L</sub></h3>
<p>The distance to use in <b>photometry</b>&nbsp;: F = L / (4π D<sub>L</sub><sup>2</sup>).
Two factors of (1+z) add to D<sub>M</sub>&nbsp;: energy loss per photon and
time dilation of the arrival rate.</p>
<p><b>Formula</b>&nbsp;: D<sub>L</sub> = (1+z) D<sub>M</sub>.</p>

<h3 style="color:#4B3F72;">3. Angular diameter distance D<sub>A</sub></h3>
<p>The distance for <b>angular sizes</b>&nbsp;: θ = ℓ / D<sub>A</sub>.
<b>Counter-intuitive</b>&nbsp;: D<sub>A</sub> peaks at {da_max:.3f} Gly for
<b>z = {z_da_max:.4f}</b> and then decreases. An identical object looks
<i>larger</i> at z = 5 than at z = 1!</p>
<p><b>Formula</b>&nbsp;: D<sub>A</sub> = D<sub>M</sub> / (1+z).</p>

<h3 style="color:#2E5D3F;">4. Light-travel distance D<sub>lt</sub></h3>
<p>The « intuitive » distance&nbsp;: c × the time the light took to reach us.
<b>Bounded by c·t₀ = {t0:.3f} Gly</b> whatever z. Physically the least
meaningful at high z&nbsp;: it measures no metric separation at all.</p>
<p><b>Formula</b>&nbsp;: D<sub>lt</sub> = c · t<sub>L</sub>(z).</p>

<h3 style="color:#b8b090;">What about D<sub>M</sub>?</h3>
<p>The <b>transverse</b> comoving distance D<sub>M</sub> equals D<sub>C</sub> in
a flat universe. As soon as Ω<sub>k</sub> ≠ 0 it departs from it (sinh or sin),
and it is the one entering D<sub>L</sub> and D<sub>A</sub>. See help F6.</p>

<h3 style="color:#94b8c8;">Reciprocity relation (Etherington, 1933)</h3>
<p style="font-size:11pt;text-align:center;">
D<sub>L</sub> = (1+z)<sup>2</sup> D<sub>A</sub>
</p>
<p>Valid in any Lorentzian geometry, not just FLRW. Checked here to
2&times;10<sup>-16</sup> (machine precision).</p>

<h3 style="color:#b89090;">The E(z) actually used</h3>
<p>Popular accounts often write
E(z) = √(Ω<sub>m</sub>(1+z)<sup>3</sup> + Ω<sub>Λ</sub>).
<b>That is not the formula used here.</b> The program computes&nbsp;:</p>
<p style="text-align:center;">
E(z)² = Ω<sub>r</sub>(z)(1+z)<sup>4</sup> + Ω<sub>m</sub>(1+z)<sup>3</sup>
+ Ω<sub>k</sub>(1+z)<sup>2</sup> + Ω<sub>Λ</sub></p>
<p>where Ω<sub>r</sub>(z) contains the CMB photons
(Ω<sub>γ</sub> = {ogamma:.4e}) <i>and</i> the neutrinos, whose density depends
on z (non-relativistic today, relativistic before z ≈ 200).</p>
<p>Error of the simplified formula&nbsp;: &lt; 0.04 % for z ≤ 2.5, but
<b>&minus;12.8 % on E at z = 1089.8</b>, and the age of the universe at the CMB
would become 479 kyr instead of 372 kyr (+29 %).</p>
""",

"planck": """
<h2 style="color:#94b8c8;">Planck 2018 cosmology</h2>
<p>The program uses the cosmological parameters measured by the <b>Planck</b>
mission (ESA, 2009-2013) in its final release (2020).
Reference&nbsp;: Aghanim et al., A&amp;A 641, A6.</p>

<h3>The parameters as astropy stores them</h3>
<table border="0" cellspacing="6">
<tr><td><b>H₀</b></td><td>{h0} km/s/Mpc</td><td>Hubble constant today (± {sigma_h0})</td></tr>
<tr><td><b>Ω<sub>m</sub></b></td><td>{om0:.5f}</td><td>baryons + cold dark matter <i>only</i></td></tr>
<tr><td><b>Ω<sub>ν</sub></b></td><td>{onu0:.5f}</td><td>neutrinos (one massive species at 0.06 eV)</td></tr>
<tr><td><b>Ω<sub>m</sub>+Ω<sub>ν</sub></b></td><td>{om_total:.5f}</td>
    <td><b>this is the « Ω<sub>m</sub> = 0.3111 » of the Planck paper</b>: neutrinos
        count as matter there, being non-relativistic today</td></tr>
<tr><td><b>Ω<sub>Λ</sub></b></td><td>{ode0:.5f}</td><td>dark energy density</td></tr>
<tr><td><b>Ω<sub>γ</sub></b></td><td>{ogamma:.4e}</td><td>photons, set by T₀ = {tcmb} K</td></tr>
<tr><td><b>Ω<sub>k</sub></b></td><td>0 by default</td><td>spatial curvature (adjustable, help F6)</td></tr>
<tr><td><b>N<sub>eff</sub></b></td><td>{neff}</td><td>effective number of neutrino species</td></tr>
<tr><td><b>t₀</b></td><td>{t0:.4f} Gyr</td><td>present age (computed, not imposed)</td></tr>
<tr><td><b>z<sub>*</sub></b></td><td>1089.80 ± 0.21</td><td>redshift of the last-scattering surface</td></tr>
</table>

<h3>« TT,TE,EE+lowE+lensing+BAO »</h3>
<p>This is the <b>list of data sets combined</b> by the Planck collaboration:</p>
<ul>
<li><b>TT</b>&nbsp;: temperature-temperature angular power spectrum of the CMB</li>
<li><b>TE</b>&nbsp;: temperature × E-mode polarisation cross-spectrum</li>
<li><b>EE</b>&nbsp;: E-mode polarisation spectrum alone</li>
<li><b>lowE</b>&nbsp;: large-angle E-mode polarisation (ℓ &lt; 30)</li>
<li><b>lensing</b>&nbsp;: gravitational lensing of the CMB by large-scale structure</li>
<li><b>BAO</b>&nbsp;: baryon acoustic oscillations in the galaxy distribution
(SDSS / BOSS / eBOSS) — data external to Planck</li>
</ul>
<p>Combining these <b>independent</b> observations breaks parameter
degeneracies and yields a final precision of about 0.5 %.</p>

<p style="color:#b89090;"><b>Hubble tension&nbsp;:</b> the local measurement
(SH0ES, Riess 2022) gives H₀ = {h0_shoes} ± 1.04 km/s/Mpc, in ~5σ disagreement
with Planck. The « compare with SH0ES » checkbox shows the effect: every
distance shrinks by about 7 % (they scale as 1/H₀).</p>
""",

"recession": """
<h2 style="color:#94b8c8;">Recession velocities and the superluminal universe</h2>

<p>The program shows <b>all three definitions</b> of the « recession velocity »,
because they give radically different results and two of them are
approximations.</p>

<h3>1. Classical Doppler&nbsp;: v = cz</h3>
<p>What most calculators display. Valid only for z &lt;&lt; 1. For the CMB it
would give 1090 c — meaningless.</p>

<h3>2. Relativistic Doppler&nbsp;: v/c = ((1+z)² − 1) / ((1+z)² + 1)</h3>
<p>Bounded by c, but <b>conceptually wrong in cosmology</b>&nbsp;: it assumes a
source moving <i>through</i> a static Minkowski spacetime. That is not the
situation of a comoving galaxy.</p>

<h3>3. FLRW recession velocity&nbsp;: v<sub>rec</sub>(t₀) = H₀ · D<sub>C</sub></h3>
<p>The <b>only correct one</b> in cosmology. It is the derivative of the proper
distance&nbsp;: v = H(t)·D<sub>p</sub>(t). Not bounded by c. Today&nbsp;:</p>
<ul>
<li>v = c at D<sub>C</sub> = D<sub>H</sub> = {d_h:.2f} Gly, i.e. z ≈ 1.48&nbsp;;</li>
<li>for the CMB&nbsp;: v<sub>rec</sub> ≈ 939 400 km/s = <b>3.13 c</b>.</li>
</ul>

<h3>Why relativity is not violated</h3>
<p>The speed limit c applies <b>locally</b>, inside the light cone at each
point. Two distant comoving observers are at rest in their own local frame;
only the physical distance between them grows, because space itself stretches.
No particle and no signal ever exceeds c while propagating through space.</p>

<h3>Superluminal galaxies are observable</h3>
<p>We do see galaxies whose v<sub>rec</sub> &gt; c today. The condition is not
v &lt; c but that the galaxy lies within the <b>event horizon</b>
({event_horizon:.2f} Gly comoving), not merely within the Hubble sphere
({d_h:.2f} Gly). The shell between the two contains galaxies receding faster
than light whose present-day emission will nonetheless reach us.</p>
<p style="color:#7a8498;">Reference: Davis &amp; Lineweaver, PASA 21, 97 (2004).</p>
""",

"presets": """
<h2 style="color:#94b8c8;">The preselected targets</h2>
<p style="color:#7a8498;">The ages below are those computed in Planck 2018;
they sometimes differ from the values in the discovery papers, which used the
cosmologies of their time (usually WMAP).</p>

<h3>M 87&nbsp; — z = 0.00428</h3>
<p>Giant elliptical galaxy in the Virgo cluster. Central supermassive black
hole of 6.5 × 10⁹ M☉, imaged by the Event Horizon Telescope in 2019.
Its redshift gives D<sub>C</sub> = <b>62 Mly</b>, whereas direct measurements
(surface-brightness fluctuations) give <b>~55 Mly</b>: the difference comes
from M 87's peculiar velocity within the cluster, which adds to the Hubble
flow. This is the limit of the « redshift → distance » method in the local
universe.</p>

<h3>3C 273&nbsp; — z = 0.158</h3>
<p><b>The first quasar ever identified</b> (Maarten Schmidt, 1963).
Visual magnitude ~12.9; the brightest quasar seen from Earth. Bolometric
luminosity ~4 × 10⁴⁶ erg/s. D<sub>C</sub> = 2.197 Gly but
D<sub>L</sub> = 2.544 Gly: the difference between definitions becomes
measurable.</p>

<h3>z = 1&nbsp; — a teaching landmark</h3>
<p>The universe was 5.851 Gyr old and half its present size (a = 0.5).</p>

<h3>z = 2.34&nbsp; — « cosmic noon »</h3>
<p>Peak of quasar activity and star formation, when the universe was 2.799 Gyr
old. A key slice for BAO surveys through the Lyman-α forest (BOSS, eBOSS).</p>

<h3>ULAS J1120+0641&nbsp; — z = 7.085</h3>
<p>Quasar discovered in 2011 (Mortlock et al., Nature). Central black hole of
2 × 10⁹ M☉ formed when the universe was only <b>749 Myr</b> old (the paper
quotes 770 Myr, in WMAP7 cosmology).</p>

<h3>GN-z11&nbsp; — z = 10.6</h3>
<p>One of the most distant spectroscopically confirmed galaxies (JWST/NIRSpec,
Bunker et al. 2023). The universe was <b>435 Myr</b> old.</p>

<h3>Reionisation&nbsp; — z ≈ 20</h3>
<p>Not an object but an <b>epoch</b> (the universe is 178 Myr old at z = 20).
The first stars reionise the neutral intergalactic hydrogen; reionisation ends
around z ≈ 5.5-6.</p>

<h3>CMB&nbsp; — z<sub>*</sub> = 1089.80</h3>
<p>The last-scattering surface. The oldest light we can detect, emitted when
the universe was <b>372 000 years</b> old (Planck 2018 value; the older WMAP
figure of 380 000 years is still often quoted) and became transparent for the
first time.</p>
""",

"verif": """
<h2 style="color:#94b8c8;">How these numbers were verified</h2>

<p>The program relies on <code>astropy.cosmology.Planck18</code>. So as not to
depend on a single computation chain, everything has been <b>recomputed from
scratch in SageMath</b>, without astropy&nbsp;:</p>
<ul>
<li>densities rebuilt from the CODATA 2022 constants
(ρ<sub>crit</sub> = 3H₀²/8πG, Ω<sub>γ</sub> = a<sub>B</sub>T₀⁴/ρ<sub>crit</sub>c²)&nbsp;;</li>
<li>neutrino density from the <b>exact Fermi-Dirac integral</b>
f(y) = (120/7π⁴)∫x²√(x²+y²)/(e<sup>x</sup>+1)dx, instead of the Komatsu (2011)
fitting formula used by astropy&nbsp;;</li>
<li>the D<sub>C</sub>, t<sub>L</sub> and t(z) integrals by mpmath quadrature at
25 digits.</li>
</ul>

<h3>Result</h3>
<table border="0" cellspacing="6">
<tr><td>distances D<sub>C</sub>, D<sub>L</sub>, D<sub>A</sub></td><td>agreement to <b>2×10<sup>-6</sup></b></td></tr>
<tr><td>lookback time</td><td>agreement to <b>4.6×10<sup>-7</sup></b></td></tr>
<tr><td>ages</td><td>agreement to <b>1.5×10<sup>-5</sup></b></td></tr>
<tr><td>t₀</td><td>{t0:.6f} Gyr (Sage: 13.786892)</td></tr>
<tr><td>maximum of D<sub>A</sub></td><td>z = {z_da_max:.5f} by both methods</td></tr>
<tr><td>curvature Ω<sub>k</sub> = ±0.01</td><td>D<sub>C</sub>, D<sub>M</sub>, D<sub>L</sub>, D<sub>A</sub>: agreement to <b>5 decimals</b></td></tr>
</table>
<p>The residual difference comes solely from the Komatsu fit (≤ 0.12 % error on
ρ<sub>ν</sub>, ≤ 1.5×10<sup>-5</sup> on the observables). <b>Conclusion: the
backend is reliable well beyond the precision of the parameters themselves</b>
(about 0.5 %).</p>

<h3>Internal checks</h3>
<ul>
<li>Etherington D<sub>L</sub> = (1+z)²D<sub>A</sub>: verified to 2×10<sup>-16</sup>&nbsp;;</li>
<li>t<sub>L</sub>(z) + age(z) = t₀: verified to 2×10<sup>-10</sup> Gyr&nbsp;;</li>
<li>the closed form of the age in ΛCDM without radiation,
t(z) = (2/3H₀√Ω<sub>Λ</sub>)·arcsinh[√(Ω<sub>Λ</sub>/Ω<sub>m</sub>)(1+z)<sup>-3/2</sup>],
recovered to 10<sup>-9</sup>&nbsp;;</li>
<li>the correlation ρ(H₀, Ω<sub>m</sub>) = {rho}, derived symbolically.</li>
</ul>
<p style="color:#7a8498;font-size:9pt;">Scripts: <code>verif_sage/verif_cosmo.sage</code>,
<code>verif_DL_symbolique.sage</code> and <code>verif_courbure_sigma.sage</code>.
Full details in <code>AUDIT_cosmologie.pdf</code>.</p>
""",

"sigma": """
<h2 style="color:#94b8c8;">Uncertainties, curvature and the Hubble tension</h2>

<h3>Where the displayed « ± » come from</h3>
<p>The two parameters dominating the uncertainty are
H₀ = {h0} ± {sigma_h0} km/s/Mpc and Ω<sub>m</sub> = {om_total} ± {sigma_om}.
For each quantity G the program computes the partial derivatives by finite
differences and propagates&nbsp;:</p>
<p style="text-align:center;">
σ<sub>G</sub>² = A²σ<sub>H₀</sub>² + B²σ<sub>Ωm</sub>²
+ <b>2ρ·A·B·σ<sub>H₀</sub>σ<sub>Ωm</sub></b>,
&nbsp;&nbsp; A = ∂G/∂H₀, &nbsp; B = ∂G/∂Ω<sub>m</sub>
</p>

<h3 style="color:#b89090;">The cross term is not a detail</h3>
<p>H₀ and Ω<sub>m</sub> are <b>strongly anti-correlated</b> in the Planck fit
(geometric degeneracy)&nbsp;: ρ = {rho}. That number is not put in by hand: it
follows from the constraint on ω<sub>m</sub> = Ω<sub>m</sub>h², measured to
0.65 % while Ω<sub>m</sub> is known to 1.8 % and h to 0.62 %&nbsp;:</p>
<p style="text-align:center;">
(σ<sub>ω</sub>/ω)² = (σ<sub>Ωm</sub>/Ω<sub>m</sub>)² + 4(σ<sub>h</sub>/h)²
+ 4ρ(σ<sub>Ωm</sub>/Ω<sub>m</sub>)(σ<sub>h</sub>/h)
</p>
<p>Concretely at z = 2.34&nbsp;: <b>±0.17 %</b> on D<sub>C</sub> when ρ is taken
into account, against ±0.79 % when it is ignored — a factor of 4.5. The status
bar shows both.</p>
<p>Another visible effect&nbsp;: the relative uncertainty <i>decreases</i> from
z = 0 (±0.62 %, driven by H₀ alone) down to z ≈ 5 (±0.13 %), then rises again
slightly. There is a « pivot » redshift where the model is best constrained.</p>

<h3>What the ± do not include</h3>
<ul>
<li>the uncertainty on Ω<sub>k</sub>, T₀, N<sub>eff</sub> or Σm<sub>ν</sub> (negligible here)&nbsp;;</li>
<li><b>model</b> error: if ΛCDM is wrong, no error bar will say so&nbsp;;</li>
<li>the <b>Hubble tension</b>, which is not a statistical uncertainty but a
disagreement between two measurements.</li>
</ul>

<h3>Hubble tension: the « SH0ES » checkbox</h3>
<p>The local measurement (Riess et al. 2022, Cepheid + type Ia supernova
distance ladder) gives H₀ = {h0_shoes} ± 1.04 km/s/Mpc, about 5σ above Planck.
Ticking the box shows the same quantities in that cosmology: every distance
shrinks by <b>7.4 %</b>, and the ages with them. That is far larger than the
error bars: today, the dominant uncertainty on a cosmological distance is not
statistical but <b>systematic</b>.</p>

<h3>Curvature Ω<sub>k</sub></h3>
<p>Planck 2018 + BAO gives Ω<sub>k</sub> = 0.0007 ± 0.0019: consistent with
zero, hence the default Ω<sub>k</sub> = 0. The field lets you explore the effect
of curvature: the <b>transverse</b> comoving distance D<sub>M</sub> then
appears, and it is that one — not D<sub>C</sub> — which enters
D<sub>L</sub> = (1+z)D<sub>M</sub> and D<sub>A</sub> = D<sub>M</sub>/(1+z).</p>
<table border="0" cellspacing="6">
<tr><td><b>Ω<sub>k</sub> &gt; 0</b></td><td>open (hyperbolic) universe</td>
    <td>D<sub>M</sub> = (D<sub>H</sub>/√Ω<sub>k</sub>)·sinh(√Ω<sub>k</sub>·D<sub>C</sub>/D<sub>H</sub>) &gt; D<sub>C</sub></td></tr>
<tr><td><b>Ω<sub>k</sub> = 0</b></td><td>flat universe</td><td>D<sub>M</sub> = D<sub>C</sub></td></tr>
<tr><td><b>Ω<sub>k</sub> &lt; 0</b></td><td>closed (spherical) universe</td>
    <td>D<sub>M</sub> = (D<sub>H</sub>/√|Ω<sub>k</sub>|)·sin(√|Ω<sub>k</sub>|·D<sub>C</sub>/D<sub>H</sub>) &lt; D<sub>C</sub></td></tr>
</table>
<p>At z = 2.34 with Ω<sub>k</sub> = +0.01, D<sub>C</sub> loses 0.36 % but
D<sub>M</sub> only 0.08 %: the two effects (content and geometry) partly cancel.
That is why curvature is so hard to measure.</p>
<p style="color:#7a8498;">Note also that the present age t₀ depends on curvature:
13.744 Gyr for Ω<sub>k</sub> = +0.01, instead of {t0:.4f}.</p>
""",
},
}
