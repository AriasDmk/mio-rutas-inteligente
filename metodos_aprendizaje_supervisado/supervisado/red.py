"""
Información de la red real del MIO (estaciones, líneas, zona, tipo de estación),
leída de los datos del SIUR descargados por el sistema de rutas
(../datos/rutas_siur.json).
"""

import json
import os
import re
import unicodedata
from functools import lru_cache

CARPETA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAIZ_REPO = os.path.dirname(CARPETA)
RUTAS_SIUR = os.path.join(RAIZ_REPO, "datos", "rutas_siur.json")

TERMINALES = {"Menga", "Paso del Comercio", "Andres Sanin", "Universidades",
              "Aguablanca", "Simon Bolivar"}
ESTADIO = {"Estadio", "Manzana del Saber", "Tequendama", "Santa Librada"}
CENTRO = (3.4527, -76.5310)        # Plaza de Cayzedo aprox.


def _estacion_de(paradero: str) -> str:
    return re.sub(r"\s+[A-Z]\d+$", "", paradero.strip())


def normalizar(texto: str) -> str:
    s = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", s)


def _zona(lat: float, lon: float) -> str:
    if abs(lat - CENTRO[0]) < 0.012 and abs(lon - CENTRO[1]) < 0.012:
        return "centro"
    if lat > 3.462:
        return "norte"
    if lon > -76.512:
        return "oriente"
    return "sur"


@lru_cache(maxsize=1)
def cargar_red():
    """Devuelve (estaciones, lineas).
    estaciones: {nombre: {lat, lon, lineas:set, zona, tipo, cerca_estadio}}
    lineas: {codigo: {'tipo': 'troncal'|'expreso', 'secuencia': [(estacion, km)]}}
    """
    with open(RUTAS_SIUR, encoding="utf-8") as f:
        datos = json.load(f)
    estaciones, lineas = {}, {}
    for codigo, linea in datos["lineas"].items():
        secuencia = []
        for paradero, lat, lon, km in linea["paradas"]:
            nombre = _estacion_de(paradero)
            e = estaciones.setdefault(nombre, {"lat": lat, "lon": lon, "lineas": set()})
            e["lineas"].add(codigo)
            if not secuencia or secuencia[-1][0] != nombre:
                secuencia.append((nombre, km))
        lineas[codigo] = {"tipo": "expreso" if codigo.startswith("E") else "troncal",
                          "secuencia": secuencia, "longitud_km": linea["longitud_km"]}
    for nombre, e in estaciones.items():
        e["zona"] = _zona(e["lat"], e["lon"])
        if nombre in TERMINALES:
            e["tipo"] = "terminal"
        elif len(e["lineas"]) >= 3:
            e["tipo"] = "transbordo"
        else:
            e["tipo"] = "sencilla"
        e["cerca_estadio"] = nombre in ESTADIO
    return estaciones, lineas


def sentido_en(linea: dict, estacion: str, posicion: int) -> str:
    """Sentido del bus en la posición `posicion` de la secuencia de la línea:
    'hacia_centro' si la siguiente parada está más cerca del Centro que esta."""
    estaciones, _ = cargar_red()
    seq = linea["secuencia"]
    sig = seq[(posicion + 1) % len(seq)][0]

    def d(n):
        e = estaciones[n]
        return (e["lat"] - CENTRO[0]) ** 2 + (e["lon"] - CENTRO[1]) ** 2

    return "hacia_centro" if d(sig) < d(estacion) else "hacia_periferia"


def buscar_estacion(texto: str) -> str:
    estaciones, _ = cargar_red()
    clave = normalizar(texto)
    for n in estaciones:
        if normalizar(n) == clave:
            return n
    parciales = [n for n in estaciones if clave and clave in normalizar(n)]
    if len(parciales) == 1:
        return parciales[0]
    sugerencia = f" Opciones: {', '.join(sorted(parciales))}" if parciales else ""
    raise ValueError(f"Estación desconocida: '{texto}'.{sugerencia}")
