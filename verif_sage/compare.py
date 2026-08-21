import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE

A = json.load(open(SRC / "ref_astropy.json"))
S = json.load(open(SRC / "verif_sage.json"))
keys = ["E", "DC_Glyr", "DL_Glyr", "DA_Glyr", "Dlt_Glyr", "tL_Gyr", "age_Gyr"]
print(f'{"z":>9} ' + " ".join(f"{k:>11}" for k in keys))
worst = {k: 0.0 for k in keys}
for a, s in zip(A["rows"], S["rows"]):
    line = f'{a["z"]:>9} '
    for k in keys:
        if a[k] == 0:
            line += f'{"---":>11} '
            continue
        d = abs(s[k] / a[k] - 1)
        worst[k] = max(worst[k], d)
        line += f"{d:11.2e} "
    print(line)
print("\nEcart relatif MAX Sage vs astropy :")
for k, v in worst.items():
    print(f"  {k:10s} {v:.3e}")
print("\nt0  astropy=%.9f  sage=%.9f  rel=%.2e" % (A["t0_Gyr"], S["t0_Gyr"], abs(S["t0_Gyr"]/A["t0_Gyr"]-1)))
print("DA max  astropy:", A["DA_max"], "\n        sage   :", S["DA_max"])
print("horizons astropy:", A["horizons"])
print("horizons sage   :", S["horizons"])
print("\nOde0 sage:", S["derived_params"]["Ode0"], " astropy:", A["params"]["Ode0"])
print("Ogamma0 sage:", S["derived_params"]["Ogamma0"], " astropy:", A["params"]["Ogamma0"])
print("Onu0 sage(exact FD):", S["derived_params"]["Onu0_exact_FD"], " astropy(Komatsu):", A["params"]["Onu0"])
print("Om0+Onu0 =", S["derived_params"]["Om0_plus_Onu0"], "  (etiquette du programme : 0.3111)")
