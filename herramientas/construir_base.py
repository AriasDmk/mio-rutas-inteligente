#!/usr/bin/env python3
"""
Construye conocimiento/base_conocimiento.pl a partir de los datos reales
del MIO descargados del SIUR (datos/rutas_siur.json).

  python herramientas/construir_base.py

Transformaciones:
  * Cada paradero "Centro A1", "Centro A2"... pertenece a la estación "Centro".
  * Las paradas vienen ordenadas según el recorrido real de cada línea
    (el recorrido es un circuito cerrado: ida y regreso). Cada par de
    estaciones consecutivas genera un hecho  tramo(Ruta, A, B, Minutos)
    DIRIGIDO, en el sentido en que circula el bus.
  * Minutos = distancia sobre el recorrido / velocidad comercial.

Supuestos (no publicados por el SIUR y por eso parametrizados aquí):
  velocidad comercial troncal 20 km/h, expreso 24 km/h;
  frecuencia troncal 8 min, expreso 10 min.
"""

import json
import os
import re
import unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRADA = os.path.join(RAIZ, "datos", "rutas_siur.json")
SALIDA = os.path.join(RAIZ, "conocimiento", "base_conocimiento.pl")

VELOCIDAD_KMH = {"troncal": 20.0, "expreso": 24.0}
FRECUENCIA_MIN = {"troncal": 8, "expreso": 10}
TERMINALES = {"Menga", "Paso del Comercio", "Andres Sanin", "Universidades",
              "Aguablanca", "Simon Bolivar"}

# nombres con tildes (el SIUR los publica sin tildes)
TILDES = {
    "Fatima": "Fátima", "Melendez": "Meléndez", "Andres Sanin": "Andrés Sanín",
    "San Nicolas": "San Nicolás", "Belalcazar": "Belalcázar", "Santa Monica": "Santa Mónica",
    "Simon Bolivar": "Simón Bolívar", "Los Alcazares": "Los Alcázares",
    "Jorge Eliecer Gaitan": "Jorge Eliécer Gaitán", "Alfonso Lopez": "Alfonso López",
    "Republica de Israel": "República de Israel", "Las Americas": "Las Américas",
    "Rio Cali": "Río Cali", "Alamos": "Álamos", "El Trebol": "El Trébol",
}

REGLAS = r"""
% ---------------------------------------------------------------------
% REGLAS (conocimiento derivado)
% ---------------------------------------------------------------------

% R1. Un bus conecta A con B si recorre el tramo en ese sentido.
conecta(R, A, B, T) :- tramo(R, A, B, T).

% R2. Una ruta sirve a una estación si alguno de sus tramos sale de ella.
sirve(R, E) :- conecta(R, E, _, _).

% R3. Un tramo está disponible si ninguna de sus estaciones está cerrada
%     y la ruta no está suspendida (hechos que se agregan en tiempo de ejecución).
disponible(R, A, B, T) :- conecta(R, A, B, T), \+ cerrada(A), \+ cerrada(B), \+ suspendida(R).

% R4. Si una estación B está cerrada, el bus pasa sin detenerse:
%     el tramo A -> C queda disponible con la suma de los tiempos.
disponible(R, A, C, T) :- conecta(R, A, B, T1), cerrada(B), conecta(R, B, C, T2), distinto(A, C), \+ cerrada(A), \+ cerrada(C), \+ suspendida(R), suma(T1, T2, T).

% R5. Una ruta está operando en una estación si tiene tramos disponibles desde ella.
opera_en(R, E) :- disponible(R, E, _, _).

% R6. Hay transbordo en E entre R1 y R2 si ambas rutas operan allí.
transbordo(E, R1, R2) :- opera_en(R1, E), opera_en(R2, E), distinto(R1, R2).

% R7. Una estación de transbordo es la que tiene al menos un transbordo.
estacion_transbordo(E) :- transbordo(E, _, _).

% R8-R9. Costo (min) de cambiar de bus: menor en terminales.
costo_transbordo(E, 3) :- estacion_transbordo(E), terminal(E).
costo_transbordo(E, 5) :- estacion_transbordo(E), \+ terminal(E).

% R10. Espera promedio al abordar = la mitad de la frecuencia de la ruta.
espera(R, W) :- frecuencia(R, F), mitad(F, W).

% R11. Dos estaciones son vecinas si una ruta disponible va de una a la otra.
vecinas(A, B) :- disponible(_, A, B, _).

% R12-R13. Alcanzabilidad (regla recursiva): B es alcanzable desde A.
alcanzable(A, B) :- vecinas(A, B).
alcanzable(A, C) :- vecinas(A, B), alcanzable(B, C).
"""


def estacion_de(paradero: str) -> str:
    """'Centro A1' -> 'Centro'."""
    return re.sub(r"\s+[A-Z]\d+$", "", paradero.strip())


def slug(nombre: str) -> str:
    s = unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s if s[0].isalpha() else "e_" + s


def construir():
    with open(ENTRADA, encoding="utf-8") as f:
        datos = json.load(f)

    estaciones = {}            # id -> (nombre, lat, lon)
    rutas, tramos = [], []
    for codigo, linea in datos["lineas"].items():
        tipo = "expreso" if codigo.startswith("E") else "troncal"
        rid = codigo.lower()
        rutas.append((rid, codigo, tipo))
        secuencia = []         # [(id, km)]
        for paradero, lat, lon, km in linea["paradas"]:
            nombre = estacion_de(paradero)
            eid = slug(nombre)
            estaciones.setdefault(eid, (TILDES.get(nombre, nombre), lat, lon, nombre))
            if not secuencia or secuencia[-1][0] != eid:
                secuencia.append((eid, km))
        # circuito cerrado: la última estación vuelve a la primera
        if secuencia[-1][0] != secuencia[0][0]:
            secuencia.append((secuencia[0][0], linea["longitud_km"] + secuencia[0][1]))
        vistos = set()
        for (a, ka), (b, kb) in zip(secuencia, secuencia[1:]):
            minutos = max(0.5, round((kb - ka) / VELOCIDAD_KMH[tipo] * 60, 1))
            if (a, b) not in vistos:
                vistos.add((a, b))
                tramos.append((rid, a, b, minutos))

    L = []
    L.append("% =====================================================================")
    L.append("%  BASE DE CONOCIMIENTO - Sistema de transporte masivo MIO (Cali)")
    L.append("%  GENERADA por herramientas/construir_base.py a partir de datos reales")
    L.append(f"%  del SIUR: {datos['fuente']}")
    L.append(f"%  Fecha de descarga: {datos['fecha_descarga']}")
    L.append("%  Supuestos: velocidad troncal 20 km/h, expreso 24 km/h;")
    L.append("%             frecuencia troncal 8 min, expreso 10 min.")
    L.append("%")
    L.append("%  Sintaxis tipo Prolog (cláusulas de Horn). Variables en mayúscula.")
    L.append("%  \\+ = negación por fallo.")
    L.append("% =====================================================================")
    L.append("")
    L.append(f"% ---- HECHOS: estaciones ({len(estaciones)})  estacion(Id, 'Nombre') ----")
    for eid, (nombre, *_r) in sorted(estaciones.items()):
        L.append(f"estacion({eid}, '{nombre}').")
    L.append("")
    L.append("% ---- HECHOS: terminales (transbordo integrado, más rápido) ----")
    for eid, (_n, _la, _lo, base) in sorted(estaciones.items()):
        if base in TERMINALES:
            L.append(f"terminal({eid}).")
    L.append("")
    L.append("% ---- HECHOS: coordenadas  coordenada(Id, Latitud, Longitud) ----")
    for eid, (_n, lat, lon, _b) in sorted(estaciones.items()):
        L.append(f"coordenada({eid}, {lat}, {lon}).")
    L.append("")
    L.append("% ---- HECHOS: rutas  ruta(Id, 'Código', Tipo)  y frecuencia(Id, Min) ----")
    for rid, codigo, tipo in rutas:
        L.append(f"ruta({rid}, '{codigo}', {tipo}).")
    for rid, _c, tipo in rutas:
        L.append(f"frecuencia({rid}, {FRECUENCIA_MIN[tipo]}).")
    L.append("")
    L.append(f"% ---- HECHOS: tramos dirigidos ({len(tramos)})  tramo(Ruta, Desde, Hasta, Minutos) ----")
    actual = None
    for rid, a, b, m in tramos:
        if rid != actual:
            L.append(f"% {rid.upper()}")
            actual = rid
        L.append(f"tramo({rid}, {a}, {b}, {m}).")
    L.append(REGLAS)

    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print(f"{len(estaciones)} estaciones, {len(rutas)} rutas, {len(tramos)} tramos -> {SALIDA}")


if __name__ == "__main__":
    construir()
