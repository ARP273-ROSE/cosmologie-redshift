#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère le logo du programme `redshift_distance_gui.py`.

Sortie :
- logo.svg            : version vectorielle (256×256)
- logo_256.png        : icône fenêtre / desktop
- logo_64.png         : icône taskbar
- logo_32.png         : icône système
- logo_16.png         : favicon

Design : carré arrondi sur fond cosmique, onde de chirp (longueur d'onde
croissant de gauche à droite) avec gradient bleu → rouge symbolisant le
redshift, un point « source » à gauche, un point « observateur » à droite,
et la lettre 𝑧 stylisée.
"""

import numpy as np
from pathlib import Path

from PyQt6.QtCore import QSize, QRectF, Qt
from PyQt6.QtGui import QImage, QPainter
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import QApplication
import sys


HERE = Path(__file__).resolve().parent


def build_svg() -> str:
    W = 256
    margin = 36
    y0 = W / 2
    x_left = margin
    x_right = W - margin

    # Chirp wave: wavelength grows exponentially from lambda_min to lambda_max
    N = 220
    xs = np.linspace(x_left, x_right, N)
    t = (xs - x_left) / (x_right - x_left)
    lambda_min = 22.0
    lambda_max = 82.0
    lam = lambda_min * (lambda_max / lambda_min) ** t  # geometric
    dx = np.diff(xs, prepend=xs[0])
    phase = np.cumsum(2 * np.pi * dx / lam)
    phase = phase - phase[0]
    amp = 30.0
    ys = y0 + amp * np.sin(phase)

    path = "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in zip(xs, ys))

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="256" height="256" viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1a2240"/>
      <stop offset="100%" stop-color="#080c16"/>
    </linearGradient>
    <linearGradient id="wave" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%"   stop-color="#4a8acb"/>
      <stop offset="30%"  stop-color="#9c93b8"/>
      <stop offset="65%"  stop-color="#cba87c"/>
      <stop offset="100%" stop-color="#c75c5c"/>
    </linearGradient>
    <radialGradient id="rim" cx="50%" cy="50%" r="55%">
      <stop offset="80%" stop-color="#94b8c8" stop-opacity="0"/>
      <stop offset="100%" stop-color="#94b8c8" stop-opacity="0.25"/>
    </radialGradient>
  </defs>

  <!-- Rounded square background -->
  <rect width="256" height="256" rx="40" ry="40" fill="url(#bg)"
        stroke="#94b8c8" stroke-width="1.5" stroke-opacity="0.55"/>
  <rect width="256" height="256" rx="40" ry="40" fill="url(#rim)"/>

  <!-- Subtle star field -->
  <circle cx="42"  cy="52"  r="0.9" fill="#c8ccd4" opacity="0.75"/>
  <circle cx="200" cy="40"  r="0.7" fill="#c8ccd4" opacity="0.55"/>
  <circle cx="218" cy="178" r="0.8" fill="#c8ccd4" opacity="0.45"/>
  <circle cx="52"  cy="208" r="0.6" fill="#c8ccd4" opacity="0.50"/>
  <circle cx="118" cy="58"  r="0.5" fill="#c8ccd4" opacity="0.40"/>
  <circle cx="178" cy="206" r="0.6" fill="#c8ccd4" opacity="0.50"/>
  <circle cx="84"  cy="78"  r="0.4" fill="#c8ccd4" opacity="0.35"/>
  <circle cx="160" cy="80"  r="0.4" fill="#c8ccd4" opacity="0.35"/>

  <!-- Glow behind wave -->
  <path d="{path}" fill="none" stroke="#5d9ad8" stroke-width="9"
        stroke-linecap="round" opacity="0.22" filter="blur(2px)"/>

  <!-- Chirp wave (redshift visualization) -->
  <path d="{path}" fill="none" stroke="url(#wave)" stroke-width="3.6"
        stroke-linecap="round"/>

  <!-- Source dot (emitting, blue) -->
  <circle cx="{x_left}" cy="{y0}" r="5.5" fill="#5d9ad8"
          stroke="#e8edf2" stroke-width="1.2"/>

  <!-- Observer dot (red shifted, observer side) -->
  <circle cx="{x_right}" cy="{y0}" r="4.5" fill="#c75c5c"
          stroke="#e8edf2" stroke-width="1.0"/>

  <!-- Italic z mark, bottom right -->
  <text x="206" y="232" font-family="Cambria, Georgia, 'Times New Roman', serif"
        font-size="48" font-weight="700" font-style="italic"
        fill="#a8c4d0" opacity="0.92">z</text>
</svg>
'''
    return svg


def render_png(svg_path: Path, out_path: Path, size: int) -> None:
    renderer = QSvgRenderer(str(svg_path))
    img = QImage(size, size, QImage.Format.Format_ARGB32)
    img.fill(0)  # transparent
    painter = QPainter(img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
    renderer.render(painter, QRectF(0, 0, size, size))
    painter.end()
    img.save(str(out_path), "PNG")


def main():
    app = QApplication(sys.argv)  # required even for offscreen rendering

    svg_path = HERE / "logo.svg"
    svg_path.write_text(build_svg(), encoding="utf-8")
    print(f"Written {svg_path}")

    for size in (16, 32, 64, 128, 256):
        out = HERE / f"logo_{size}.png"
        render_png(svg_path, out, size)
        print(f"Written {out} ({size}x{size})")


if __name__ == "__main__":
    main()
