# Texte de présentation pour AstroBin / AstroBin announcement text

Deux versions, anglaise puis française. À coller telle quelle dans un post de
forum, une description d'image ou un commentaire.

---

## English (AstroBin forum / image description)

**Where are the objects we photograph, really? A small free tool for redshift → distance**

Most of us note the redshift of a galaxy or a quasar we have imaged without
thinking much further. But turning that number into a distance is less
straightforward than it looks — and the result can be surprising.

I put together a small open-source program that does it properly. You type a
redshift, and it gives the four distances that cosmologists actually use, in
ΛCDM with the Planck 2018 parameters:

- **comoving distance** — where the object is *now*;
- **luminosity distance** — the one that goes into flux and magnitude;
- **angular diameter distance** — the one that sets the apparent size;
- **light-travel distance** — the "intuitive" one, c × travel time.

At small redshift they all agree. Beyond that they part company, and this is
where it gets interesting for imagers:

- **3C 273** (z = 0.158, an easy target for a small scope): 2.20, 2.54 and
  1.90 Gly depending on which distance you mean — already a 34 % spread.
- **The angular diameter distance peaks at z = 1.59, then decreases.** An
  identical galaxy looks *larger* at z = 5 than at z = 1. The universe works as
  a gravitational magnifying glass at high redshift.
- For the CMB, the four "distances" span **six orders of magnitude**, from
  41 Mly to 49 000 Gly.
- **M 87**: its redshift gives 62 Mly, while direct measurements give ~55 Mly.
  Neither is wrong — the difference is the galaxy's own motion inside the Virgo
  cluster. Redshift only becomes a reliable distance beyond z ≈ 0.03.

You do not even need to look the redshift up: type the name of your target —
`m31`, `ngc224`, `3c273`, `Sombrero`, `GN-z11`, whatever spelling comes to
hand — and it is fetched from SIMBAD.

The program also shows the age of the universe when the light left (435 Myr for
GN-z11, 372 000 years for the CMB), 1σ error bars, and a comparison with the
SH0ES value of H₀ — which shortens every distance by 7.4 %, forty times more
than the error bars. That is the Hubble tension, seen from the eyepiece so to
speak.

Free, open source, and nothing to install: a single file to download for
Windows, macOS or Linux. The interface is bilingual (English / French). A 64-page
course comes with it, written at three levels, from plain language to the FLRW
derivations — with every number verified independently in SageMath.

Download and source: https://github.com/ARP273-ROSE/cosmologie-redshift

---

## Français (forum ou description d'image)

**Où sont vraiment les objets que nous photographions ? Un petit outil libre redshift → distance**

On note le redshift d'une galaxie ou d'un quasar qu'on vient d'imager sans
toujours aller plus loin. Or convertir ce nombre en distance est moins simple
qu'il n'y paraît — et le résultat peut surprendre.

J'ai mis au point un petit programme libre qui le fait proprement. On entre un
redshift, il donne les quatre distances réellement employées en cosmologie,
dans le modèle ΛCDM avec les paramètres Planck 2018 :

- **distance comobile** — où l'objet se trouve *aujourd'hui* ;
- **distance de luminosité** — celle qui entre dans le flux et la magnitude ;
- **distance de diamètre angulaire** — celle qui fixe la taille apparente ;
- **distance de trajet de la lumière** — la valeur « intuitive », c × le temps
  de trajet.

À petit redshift, elles coïncident. Au-delà, elles divergent, et c'est là que
ça devient intéressant pour nous :

- **3C 273** (z = 0,158, accessible à une petite lunette) : 2,20, 2,54 ou
  1,90 G al selon la distance dont on parle — 34 % d'écart déjà.
- **La distance de diamètre angulaire passe par un maximum à z = 1,59 puis
  décroît.** Une galaxie identique paraît *plus grande* à z = 5 qu'à z = 1.
  L'univers se comporte comme une loupe à grand redshift.
- Pour le fond diffus, les quatre « distances » s'étalent sur **six ordres de
  grandeur**, de 41 M al à 49 000 G al.
- **M 87** : son redshift donne 62 M al, alors que les mesures directes donnent
  ~55 M al. Aucune des deux n'est fausse — l'écart vient du mouvement propre de
  la galaxie dans l'amas de la Vierge. Le redshift ne devient une distance
  fiable qu'au-delà de z ≈ 0,03.

Nul besoin de connaître le redshift : il suffit de taper le nom de la cible —
`m31`, `ngc224`, `3c273`, `Sombrero`, `GN-z11`, dans à peu près n'importe
quelle orthographe — et il est cherché dans SIMBAD.

Le programme affiche aussi l'âge de l'univers au moment de l'émission (435 Myr
pour GN-z11, 372 000 ans pour le CMB), les barres d'erreur à 1σ, et une
comparaison avec la valeur SH0ES de H₀ — qui raccourcit toutes les distances de
7,4 %, quarante fois plus que les barres d'erreur. C'est la tension de Hubble,
vue depuis l'oculaire en quelque sorte.

Gratuit, libre, et rien à installer : un seul fichier à télécharger, pour
Windows, macOS ou Linux. Interface bilingue français / anglais. Un cours de
68 pages l'accompagne, écrit à trois niveaux, de la vulgarisation aux
dérivations FLRW — avec tous les nombres vérifiés indépendamment sous SageMath.

Téléchargement et sources : https://github.com/ARP273-ROSE/cosmologie-redshift

---

## Version courte (commentaire sous une image / short comment)

> Nice capture. If you are curious about where this object actually sits: I made
> a small free tool that converts a redshift — or just the object's name, looked
> up in SIMBAD — into the four cosmological distances (Planck 2018). The
> surprise is that beyond z ≈ 1.6 the angular
> diameter distance *decreases* — an identical galaxy looks bigger at z = 5 than
> at z = 1. One file for Windows, macOS or Linux, bilingual, with a course
> explaining the physics: https://github.com/ARP273-ROSE/cosmologie-redshift

> Belle image. Si tu es curieux de savoir où se trouve vraiment cet objet : j'ai
> fait un petit outil libre qui convertit un redshift — ou simplement le nom de
> l'objet, cherché dans SIMBAD — en quatre distances cosmologiques
> (Planck 2018). La surprise, c'est qu'au-delà de z ≈ 1,6 la
> distance de diamètre angulaire *diminue* — une galaxie identique paraît plus
> grande à z = 5 qu'à z = 1. Un fichier pour Windows, macOS ou Linux, bilingue, avec un cours
> qui explique la physique :
> https://github.com/ARP273-ROSE/cosmologie-redshift
