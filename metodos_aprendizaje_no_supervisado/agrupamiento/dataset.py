"""
Dataset de demanda horaria por estación del MIO.

Las entradas (validaciones de ingreso) y salidas por estación y por hora no son
públicas. Se construye una muestra de prueba sobre la RED REAL del SIUR
(81 estaciones), en la que cada estación tiene un perfil de uso oculto que
depende de su ubicación y su función en la red:

  residencial  origen de viajes: mucha entrada en la mañana, mucha salida en la tarde
  destino      centro y zonas de empleo: lo contrario
  intercambio  terminales y estaciones de transbordo fuera del centro: dos picos simétricos
  estudio      universidades y colegios: llegadas a las 7 y a las 10, salidas en la tarde y la noche
  recreativo   escenarios deportivos: demanda moderada entre semana y alta el fin de semana

El perfil oculto se guarda aparte (datos/perfil_oculto.csv) y SOLO se usa para
evaluar si el agrupamiento lo recupera; los modelos nunca lo ven.
"""

import csv
import math
import os
from datetime import date, timedelta

import numpy as np

from .red import cargar_red

CARPETA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_DEMANDA = os.path.join(CARPETA, "datos", "demanda_horaria.csv")
RUTA_PERFIL = os.path.join(CARPETA, "datos", "perfil_oculto.csv")

HORAS = list(range(4, 24))
INICIO, DIAS = date(2026, 8, 31), 28                 # 4 semanas
FESTIVOS = {date(2026, 10, 12)}                       # (fuera del rango; se deja como ejemplo)
PERFILES = ["residencial", "destino", "intercambio", "estudio", "recreativo"]

ESTUDIO = {"Universidades", "Univalle", "Buitrera", "Melendez", "Santa Librada", "Manzana del Saber"}
RECREATIVO = {"Estadio", "Tequendama", "Unidad Deportiva", "Lido", "Pampalinda"}
DESTINO_EXTRA = {"Flora Industrial", "Salomia"}         # zonas industriales


def perfil_de(nombre: str, est: dict) -> str:
    """Regla documentada que asigna el perfil oculto a cada estación real."""
    if nombre in ESTUDIO:
        return "estudio"
    if nombre in RECREATIVO:
        return "recreativo"
    if est["zona"] == "centro" or nombre in DESTINO_EXTRA:
        return "destino"
    if est["tipo"] == "terminal" or est["tipo"] == "transbordo":
        return "intercambio"
    return "residencial"


def _g(h, mu, s):
    return math.exp(-0.5 * ((h - mu) / s) ** 2)


def curvas(perfil: str, desfase: float = 0.0):
    """Pesos relativos por hora: (entradas_laboral, salidas_laboral, entradas_finde, salidas_finde, factor_finde)."""
    d = desfase
    base = 0.06
    if perfil == "residencial":
        en = lambda h: 1.0 * _g(h, 6.5 + d, 1.0) + 0.22 * _g(h, 13, 3) + 0.18 * _g(h, 17.5, 2) + base
        sa = lambda h: 0.22 * _g(h, 7.5, 1.5) + 0.22 * _g(h, 13, 3) + 0.95 * _g(h, 18.3 + d, 1.2) + base
        ef = lambda h: 0.6 * _g(h, 10, 2.2) + 0.3 * _g(h, 16, 2) + base
        sf = lambda h: 0.3 * _g(h, 12, 2.5) + 0.6 * _g(h, 18, 2) + base
        finde = 0.55
    elif perfil == "destino":
        en = lambda h: 0.2 * _g(h, 7.5, 1.5) + 0.35 * _g(h, 12.5 + d, 1.5) + 1.0 * _g(h, 17.6 + d, 1.2) + base
        sa = lambda h: 1.0 * _g(h, 7.2 + d, 1.0) + 0.35 * _g(h, 12.5, 1.5) + 0.2 * _g(h, 18, 2) + base
        ef = lambda h: 0.6 * _g(h, 13, 2.5) + 0.5 * _g(h, 17, 2) + base
        sf = lambda h: 0.7 * _g(h, 11, 2.2) + 0.3 * _g(h, 15, 2) + base
        finde = 0.5
    elif perfil == "intercambio":
        en = lambda h: 0.85 * _g(h, 6.8 + d, 1.2) + 0.6 * _g(h, 12.5, 3) + 0.85 * _g(h, 17.8 + d, 1.3) + base
        sa = lambda h: 0.85 * _g(h, 7.0 + d, 1.2) + 0.6 * _g(h, 12.5, 3) + 0.85 * _g(h, 18.0 + d, 1.3) + base
        ef = lambda h: 0.5 * _g(h, 11, 3) + 0.5 * _g(h, 17, 3) + base
        sf = ef
        finde = 0.6
    elif perfil == "estudio":
        en = lambda h: 0.35 * _g(h, 12.5 + d, 1.0) + 0.6 * _g(h, 16, 1.2) + 0.75 * _g(h, 20.2, 1.1) + base
        sa = lambda h: 1.0 * _g(h, 6.8 + d, 0.8) + 0.55 * _g(h, 10, 1.0) + 0.3 * _g(h, 14, 1.2) + base
        ef = lambda h: 0.4 * _g(h, 12, 3) + base
        sf = lambda h: 0.4 * _g(h, 9, 2) + base
        finde = 0.2
    else:  # recreativo
        en = lambda h: 0.45 * _g(h, 6.8 + d, 1.2) + 0.35 * _g(h, 17.5, 1.5) + 0.45 * _g(h, 20, 1.3) + base
        sa = lambda h: 0.35 * _g(h, 7.5, 1.2) + 0.5 * _g(h, 17, 1.5) + 0.3 * _g(h, 19, 1.5) + base
        ef = lambda h: 0.6 * _g(h, 12.5, 1.8) + 0.9 * _g(h, 20.5, 1.2) + base
        sf = lambda h: 0.9 * _g(h, 10, 1.5) + 0.6 * _g(h, 16.5, 1.5) + base
        finde = 1.3
    return en, sa, ef, sf, finde


VOLUMEN = {"residencial": 2800, "destino": 4400, "intercambio": 8000, "estudio": 4800, "recreativo": 2800}


def generar(semilla: int = 7, ruta: str = RUTA_DEMANDA, ruta_perfil: str = RUTA_PERFIL, dias: int = DIAS):
    rng = np.random.default_rng(semilla)
    estaciones, _ = cargar_red()
    filas, perfiles = [], []
    for nombre in sorted(estaciones):
        est = estaciones[nombre]
        perfil = perfil_de(nombre, est)
        perfiles.append({"estacion": nombre, "perfil_oculto": perfil})
        desfase = float(rng.normal(0, 0.25))
        volumen = VOLUMEN[perfil] * (1 + 0.15 * (len(est["lineas"]) - 1)) * float(rng.lognormal(0, 0.25))
        en, sa, ef, sf, finde = curvas(perfil, desfase)
        # mezcla: ninguna estación es "pura"; toma una parte de otro perfil elegido al azar
        segundo = str(rng.choice([q for q in PERFILES if q != perfil]))
        mezcla = float(rng.uniform(0.0, 0.4))
        ren, rsa, ref_, rsf, _ = curvas(segundo, desfase)
        for k in range(dias):
            fecha = INICIO + timedelta(days=k)
            laboral = fecha.weekday() < 5 and fecha not in FESTIVOS
            tipo_dia = "laboral" if laboral else ("sabado" if fecha.weekday() == 5 else "domingo_festivo")
            factor_dia = 1.0 if laboral else finde * (1.0 if tipo_dia == "sabado" else 0.8)
            fe, fs = (en, sa) if laboral else (ef, sf)
            re_, rs_ = (ren, rsa) if laboral else (ref_, rsf)
            ruido_dia = float(rng.normal(1, 0.08))
            for h in HORAS:
                lam_e = volumen / 6 * factor_dia * ruido_dia * ((1 - mezcla) * fe(h) + mezcla * re_(h))
                lam_s = volumen / 6 * factor_dia * ruido_dia * ((1 - mezcla) * fs(h) + mezcla * rs_(h))
                filas.append({"estacion": nombre, "fecha": fecha.isoformat(), "tipo_dia": tipo_dia, "hora": h,
                              "entradas": int(rng.poisson(max(lam_e, 0.1))),
                              "salidas": int(rng.poisson(max(lam_s, 0.1)))})
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["estacion", "fecha", "tipo_dia", "hora", "entradas", "salidas"])
        w.writeheader()
        w.writerows(filas)
    with open(ruta_perfil, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["estacion", "perfil_oculto"])
        w.writeheader()
        w.writerows(perfiles)
    return ruta, len(filas)
