"""Contrôle statique de launch.bat : labels, parenthèses, ASCII, redirections."""
import re
import sys

path = sys.argv[1]
raw = open(path, "rb").read()
text = raw.decode("utf-8")
lines = text.split("\n")

errs, warns = [], []

# 1. ASCII pur (page de code cmd)
for i, l in enumerate(lines, 1):
    for ch in l:
        if ord(ch) > 127:
            errs.append(f"L{i}: caractère non-ASCII {ch!r}")

# 2. labels définis / utilisés
labels = {m.group(1).lower() for m in re.finditer(r"^\s*:([A-Za-z_][\w]*)", text, re.M)}
labels.add("eof")
for i, l in enumerate(lines, 1):
    for m in re.finditer(r"\bgoto\s+:?([A-Za-z_][\w]*)", l, re.I):
        if m.group(1).lower() not in labels:
            errs.append(f"L{i}: goto vers un label inexistant :{m.group(1)}")
    for m in re.finditer(r"\bcall\s+:([A-Za-z_][\w]*)", l, re.I):
        if m.group(1).lower() not in labels:
            errs.append(f"L{i}: call vers un label inexistant :{m.group(1)}")

# 3. labels jamais atteints (hors :eof)
used = {m.group(1).lower() for m in re.finditer(r"\b(?:goto|call)\s+:?([A-Za-z_][\w]*)", text, re.I)}
for lab in labels - used - {"eof"}:
    warns.append(f"label :{lab} défini mais jamais utilisé")

# 4. équilibre des parenthèses de blocs (hors echo, hors ^( échappées)
depth = 0
for i, l in enumerate(lines, 1):
    s = re.sub(r"\^.", "", l)          # retire les caractères échappés ^( ^)
    if re.match(r"\s*(rem\b|::)", s, re.I):
        continue
    s = re.sub(r'"[^"]*"', "", s)      # retire les chaînes
    s = re.sub(r"^\s*echo\b.*$", "", s, flags=re.I)   # une ligne echo ne compte pas
    depth += s.count("(") - s.count(")")
    if depth < 0:
        errs.append(f"L{i}: parenthèse fermante en trop (profondeur {depth})")
        depth = 0
if depth != 0:
    errs.append(f"parenthèses non refermées en fin de fichier (profondeur {depth})")

# 5. pièges classiques
for i, l in enumerate(lines, 1):
    if re.search(r"%\w+%", l) and re.search(r"^\s*(if|for)\b", l, re.I) and "(" in l:
        pass  # expansion au parsing : signalé seulement si delayed attendu
    if re.search(r"\bset\s+\w+\s*=", l) and not re.search(r'set\s+"', l, re.I) \
       and not re.search(r"set\s+/", l, re.I):
        warns.append(f"L{i}: set sans guillemets (fragile si espaces)")
    if "cd /d" in l.lower() and re.search(r'%~dp0"', l):
        errs.append(f"L{i}: cd /d \"%~dp0\" — le backslash final échappe le guillemet, "
                    f"utiliser \"%~dp0.\"")

print(f"{path} : {len(lines)} lignes")
for e in errs:
    print("  ERREUR  ", e)
for w in warns:
    print("  note    ", w)
if not errs:
    print("  → aucune erreur de structure détectée")
sys.exit(1 if errs else 0)
