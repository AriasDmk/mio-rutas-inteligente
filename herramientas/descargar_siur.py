#!/usr/bin/env python3
"""
Descarga las paradas y el recorrido de las líneas del MIO desde la API
pública del Buscarutas del SIUR y genera datos/rutas_siur.json.

  python herramientas/descargar_siur.py T31 T40 T47 T50 T57 T62 T12 E21 E37
  python herramientas/construir_base.py

Las paradas se ordenan proyectándolas sobre la polilínea del recorrido
(el punto más cercano) y midiendo la distancia acumulada hasta ese punto.
Requiere conexión a Internet (usa solo la biblioteca estándar).
"""

import json
import math
import os
import sys
import urllib.request
from datetime import date

API = "https://servicios.siur.com.co/buscarutas/api"
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, "datos", "rutas_siur.json")
PREFIJOS_CALLE = ("Cl ", "Kr ", "Av ", "Tv ", "Dg ")


def _get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", errors="replace"))


def haversine(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (*a, *b))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(h))


def descargar(linea):
    paradas = _get(f"{API}/paradas.php?linea={linea}")
    recorrido = [(float(p["latitud"]), float(p["longitud"])) for p in _get(f"{API}/recorrido.php?linea={linea}")]
    acumulado = [0.0]
    for p, q in zip(recorrido, recorrido[1:]):
        acumulado.append(acumulado[-1] + haversine(p, q))
    salida = []
    for p in paradas:
        if p["nombre"].startswith(PREFIJOS_CALLE):
            continue
        pos = (float(p["latitud"]), float(p["longitud"]))
        i = min(range(len(recorrido)), key=lambda k: haversine(pos, recorrido[k]))
        salida.append([p["nombre"], round(pos[0], 5), round(pos[1], 5), round(acumulado[i], 2)])
    salida.sort(key=lambda x: x[3])
    return {"longitud_km": round(acumulado[-1], 2), "paradas": salida}


def main(lineas):
    datos = {"fuente": "https://servicios.siur.com.co/buscarutas/ (api/paradas.php y api/recorrido.php)",
             "fecha_descarga": date.today().isoformat(),
             "nota": "Paradas ordenadas según su posición sobre el recorrido.",
             "lineas": {}}
    for linea in lineas:
        print(f"Descargando {linea}...")
        datos["lineas"][linea] = descargar(linea)
    with open(SALIDA, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
    print(f"Guardado en {SALIDA}")


if __name__ == "__main__":
    main(sys.argv[1:] or ["T31", "T40", "T47", "T50", "T57", "T62", "T12", "E21", "E37"])
