"""
Generación del dataset de ocupación de buses del MIO.

La ocupación por bus y por estación del MIO NO es un dato público. Por eso,
se construye un dataset de prueba sobre la RED
REAL (81 estaciones y 9 líneas descargadas del SIUR), siguiendo patrones
conocidos de la movilidad en Cali y documentados aquí:

  * Horas pico: en la mañana (6-8 h) los buses van llenos HACIA el centro;
    en la tarde (17-19 h) van llenos HACIA la periferia.
  * Sábados hay menos demanda; domingos y festivos, mucho menos.
  * Las estaciones de transbordo, las terminales y el centro tienen más gente.
  * La lluvia aumenta la ocupación (la gente deja la bici, la moto o el caminar).
  * En días de quincena hay más viajes.
  * Un partido en el Estadio Pascual Guerrero llena las estaciones cercanas
    al final de la tarde y en la noche.
  * Los expresos van un poco más llenos que las troncales.

A cada registro se le suma ruido gaussiano y además un porcentaje de etiquetas
se cambia a una clase vecina, para que el problema no sea trivial (en la
realidad hay factores que no medimos).

Todo es reproducible con la semilla.
"""

import csv
import os
import random
from datetime import date, timedelta

from .red import cargar_red, sentido_en

CARPETA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_DATASET = os.path.join(CARPETA, "datos", "dataset_ocupacion.csv")

DIAS = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
INICIO, FIN = date(2026, 8, 3), date(2026, 9, 27)          # 8 semanas
FESTIVOS = {date(2026, 8, 7), date(2026, 8, 17)}           # Batalla de Boyacá, Asunción
PARTIDOS = {date(2026, 8, 9), date(2026, 8, 19), date(2026, 8, 30),
            date(2026, 9, 6), date(2026, 9, 16), date(2026, 9, 26)}

# Pesos de muestreo por hora (más servicios en hora pico)
PESO_HORA = {4: 1, 5: 3, 6: 7, 7: 8, 8: 6, 9: 4, 10: 3, 11: 3, 12: 4, 13: 4, 14: 3,
             15: 3, 16: 4, 17: 7, 18: 8, 19: 6, 20: 4, 21: 3, 22: 2, 23: 1}

COLUMNAS = ["id", "fecha", "dia_semana", "tipo_dia", "hora", "franja", "linea", "tipo_linea",
            "estacion", "tipo_estacion", "zona", "sentido", "lluvia", "quincena",
            "evento_estadio", "nivel_ocupacion"]

UMBRAL_MEDIA, UMBRAL_ALTA = 0.40, 0.66
RUIDO_SD, PROB_CAMBIO_ETIQUETA = 0.08, 0.08


def franja_de(hora: int) -> str:
    if hora <= 5:
        return "madrugada"
    if hora <= 8:
        return "pico_am"
    if hora <= 16:
        return "valle"
    if hora <= 19:
        return "pico_pm"
    return "noche"


def tipo_dia_de(fecha: date) -> str:
    if fecha in FESTIVOS or fecha.weekday() == 6:
        return "domingo_festivo"
    if fecha.weekday() == 5:
        return "sabado"
    return "laboral"


def es_quincena(fecha: date) -> bool:
    ultimo = (fecha.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    return fecha.day in (1, 15, 16) or fecha.day >= ultimo.day - 1


def puntaje_ocupacion(r: dict, est: dict) -> float:
    """Ocupación esperada (0 a 1) SIN ruido: las reglas del generador."""
    base = {"madrugada": 0.18, "valle": 0.38, "noche": 0.24}.get(r["franja"])
    if r["franja"] == "pico_am":
        base = 0.74 if r["sentido"] == "hacia_centro" else 0.42
    elif r["franja"] == "pico_pm":
        base = 0.74 if r["sentido"] == "hacia_periferia" else 0.44
    base += {"laboral": 0.0, "sabado": -0.12, "domingo_festivo": -0.24}[r["tipo_dia"]]
    base += {"terminal": 0.06, "transbordo": 0.10, "sencilla": 0.0}[r["tipo_estacion"]]
    base += 0.06 if r["zona"] == "centro" else 0.0
    base += 0.11 if r["lluvia"] == "si" else 0.0
    base += 0.05 if r["quincena"] == "si" else 0.0
    base += 0.04 if r["tipo_linea"] == "expreso" else 0.0
    if r["evento_estadio"] == "si" and est["cerca_estadio"] and r["franja"] in ("pico_pm", "noche"):
        base += 0.35
    return base


def nivel(p: float) -> str:
    return "Alta" if p >= UMBRAL_ALTA else ("Media" if p >= UMBRAL_MEDIA else "Baja")


def generar(n: int = 8000, semilla: int = 42, ruta: str = RUTA_DATASET):
    rnd = random.Random(semilla)
    estaciones, lineas = cargar_red()
    codigos = sorted(lineas)
    dias = [INICIO + timedelta(days=i) for i in range((FIN - INICIO).days + 1)]
    horas, pesos = zip(*PESO_HORA.items())
    lluvia_cache = {}
    filas = []
    for i in range(1, n + 1):
        fecha = rnd.choice(dias)
        hora = rnd.choices(horas, pesos)[0]
        codigo = rnd.choice(codigos)
        linea = lineas[codigo]
        pos = rnd.randrange(len(linea["secuencia"]))
        estacion = linea["secuencia"][pos][0]
        est = estaciones[estacion]
        clave_lluvia = (fecha, franja_de(hora))
        if clave_lluvia not in lluvia_cache:
            lluvia_cache[clave_lluvia] = rnd.random() < 0.28
        r = {
            "id": i, "fecha": fecha.isoformat(), "dia_semana": DIAS[fecha.weekday()],
            "tipo_dia": tipo_dia_de(fecha), "hora": hora, "franja": franja_de(hora),
            "linea": codigo, "tipo_linea": linea["tipo"], "estacion": estacion,
            "tipo_estacion": est["tipo"], "zona": est["zona"],
            "sentido": sentido_en(linea, estacion, pos),
            "lluvia": "si" if lluvia_cache[clave_lluvia] else "no",
            "quincena": "si" if es_quincena(fecha) else "no",
            "evento_estadio": "si" if fecha in PARTIDOS else "no",
        }
        p = puntaje_ocupacion(r, est) + rnd.gauss(0, RUIDO_SD)
        etiqueta = nivel(p)
        if rnd.random() < PROB_CAMBIO_ETIQUETA:          # ruido de etiqueta
            orden = ["Baja", "Media", "Alta"]
            k = orden.index(etiqueta)
            etiqueta = orden[max(0, k - 1)] if k == 2 or (k == 1 and rnd.random() < 0.5) else orden[k + 1]
        r["nivel_ocupacion"] = etiqueta
        filas.append(r)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNAS)
        w.writeheader()
        w.writerows(filas)
    return ruta, len(filas)
