"""
Estrategias de búsqueda sobre el espacio de estados del sistema MIO.

Espacio de estados
------------------
Un estado es la pareja (estación, ruta en la que voy montado).
  * Estado inicial: (origen, None) -> todavía no he abordado ningún bus.
  * Acciones:
      - ABORDAR   (origen, None) -> (origen, R)     costo = espera(R)
      - VIAJAR    (A, R)         -> (B, R)          costo = minutos del tramo
      - TRANSBORDO(E, R1)        -> (E, R2)         costo = costo_transbordo(E) + espera(R2)
  * Estado meta: cualquier (destino, R).

Todos los costos se obtienen de hechos derivados por el motor de
inferencia (reglas disponible/4, espera/2, costo_transbordo/2).

Algoritmos
----------
  * astar  : A*  f(n) = g(n) + h(n)   (óptimo, heurística admisible)
  * ucs    : costo uniforme (Dijkstra)  f(n) = g(n)   (óptimo, sin heurística)
  * voraz  : primero el mejor (greedy) f(n) = h(n)   (rápido, no garantiza óptimo)
  * bfs    : amplitud; minimiza el número de acciones, no el tiempo

Heurística
----------
h(n) = distancia_en_línea_recta(estación, destino) / V_MAX * 60   [minutos]
donde V_MAX es la mayor velocidad observada en cualquier tramo de la red.
Como ningún recorrido puede ser más corto que la línea recta ni más rápido
que V_MAX, h(n) nunca sobreestima el costo real -> es ADMISIBLE y además
CONSISTENTE (por la desigualdad triangular), así que A* es óptimo.
"""

from __future__ import annotations

import heapq
import math
import time
from collections import deque
from dataclasses import dataclass, field
from itertools import count
from typing import Callable, Dict, List, Optional, Tuple

Estado = Tuple[str, Optional[str]]          # (estacion, ruta)

PENALIDAD_TRANSBORDO_CRITERIO = 1000.0      # para el criterio "menos transbordos"


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


@dataclass
class Paso:
    accion: str            # 'abordar' | 'viajar' | 'transbordo'
    desde: Estado
    hacia: Estado
    costo: float           # minutos reales


@dataclass
class Resultado:
    algoritmo: str
    encontrado: bool
    pasos: List[Paso] = field(default_factory=list)
    minutos: float = 0.0
    transbordos: int = 0
    paradas: int = 0
    nodos_expandidos: int = 0
    nodos_generados: int = 0
    milisegundos: float = 0.0


class ProblemaRuta:
    """Define el problema de búsqueda a partir de la red (grafo) inferida."""

    def __init__(self, red, origen: str, destino: str, criterio: str = "tiempo"):
        if criterio not in ("tiempo", "transbordos"):
            raise ValueError("criterio debe ser 'tiempo' o 'transbordos'")
        self.red, self.origen, self.destino, self.criterio = red, origen, destino, criterio
        self.inicial: Estado = (origen, None)

    def es_meta(self, estado: Estado) -> bool:
        return estado[0] == self.destino

    def sucesores(self, estado: Estado) -> List[Tuple[str, Estado, float, float]]:
        """Lista de (accion, nuevo_estado, costo_real, costo_para_busqueda)."""
        estacion, ruta = estado
        red, resultado = self.red, []
        if ruta is None:
            for r in sorted(red.rutas_en(estacion)):
                w = red.espera[r]
                resultado.append(("abordar", (estacion, r), w, w))
            return resultado
        for destino, minutos in red.adyacentes(estacion, ruta):
            resultado.append(("viajar", (destino, ruta), minutos, minutos))
        for r2 in sorted(red.rutas_en(estacion)):
            if r2 != ruta:
                c = red.costo_transbordo.get(estacion, 6) + red.espera[r2]
                extra = PENALIDAD_TRANSBORDO_CRITERIO if self.criterio == "transbordos" else 0.0
                resultado.append(("transbordo", (estacion, r2), c, c + extra))
        return resultado

    def heuristica(self, estado: Estado) -> float:
        return self.red.minutos_linea_recta(estado[0], self.destino)


# ---------------------------------------------------------------------------
# Búsqueda genérica "primero el mejor" (A*, UCS y voraz son casos particulares)
# ---------------------------------------------------------------------------

def _primero_el_mejor(problema: ProblemaRuta, nombre: str,
                      f: Callable[[float, float], float]) -> Resultado:
    t0 = time.perf_counter()
    inicial = problema.inicial
    desempate = count()
    frontera = [(f(0.0, problema.heuristica(inicial)), next(desempate), 0.0, inicial)]
    mejor_g: Dict[Estado, float] = {inicial: 0.0}
    padre: Dict[Estado, Tuple[Estado, str, float]] = {}
    cerrados = set()
    expandidos, generados = 0, 1

    while frontera:
        _, _, g, estado = heapq.heappop(frontera)
        if estado in cerrados:
            continue
        cerrados.add(estado)
        if problema.es_meta(estado):
            return _construir(nombre, problema, padre, estado, expandidos, generados, t0)
        expandidos += 1
        for accion, nuevo, costo_real, costo_busq in problema.sucesores(estado):
            g2 = g + costo_busq
            if nuevo not in cerrados and g2 < mejor_g.get(nuevo, math.inf):
                mejor_g[nuevo] = g2
                padre[nuevo] = (estado, accion, costo_real)
                heapq.heappush(frontera, (f(g2, problema.heuristica(nuevo)),
                                          next(desempate), g2, nuevo))
                generados += 1
    return Resultado(nombre, False, nodos_expandidos=expandidos, nodos_generados=generados,
                     milisegundos=(time.perf_counter() - t0) * 1000)


def a_estrella(problema: ProblemaRuta) -> Resultado:
    return _primero_el_mejor(problema, "A*", lambda g, h: g + h)


def costo_uniforme(problema: ProblemaRuta) -> Resultado:
    return _primero_el_mejor(problema, "Costo uniforme", lambda g, h: g)


def voraz(problema: ProblemaRuta) -> Resultado:
    return _primero_el_mejor(problema, "Voraz (greedy)", lambda g, h: h)


def amplitud(problema: ProblemaRuta) -> Resultado:
    """Búsqueda en amplitud: encuentra el camino con menos acciones."""
    t0 = time.perf_counter()
    inicial = problema.inicial
    frontera = deque([inicial])
    padre: Dict[Estado, Tuple[Estado, str, float]] = {}
    visitados = {inicial}
    expandidos, generados = 0, 1
    while frontera:
        estado = frontera.popleft()
        if problema.es_meta(estado):
            return _construir("Amplitud (BFS)", problema, padre, estado, expandidos, generados, t0)
        expandidos += 1
        for accion, nuevo, costo_real, _ in problema.sucesores(estado):
            if nuevo not in visitados:
                visitados.add(nuevo)
                padre[nuevo] = (estado, accion, costo_real)
                frontera.append(nuevo)
                generados += 1
    return Resultado("Amplitud (BFS)", False, nodos_expandidos=expandidos,
                     nodos_generados=generados, milisegundos=(time.perf_counter() - t0) * 1000)


def _construir(nombre, problema, padre, meta, expandidos, generados, t0) -> Resultado:
    pasos: List[Paso] = []
    estado = meta
    while estado in padre:
        anterior, accion, costo = padre[estado]
        pasos.append(Paso(accion, anterior, estado, costo))
        estado = anterior
    pasos.reverse()
    return Resultado(
        algoritmo=nombre, encontrado=True, pasos=pasos,
        minutos=sum(p.costo for p in pasos),
        transbordos=sum(p.accion == "transbordo" for p in pasos),
        paradas=sum(p.accion == "viajar" for p in pasos),
        nodos_expandidos=expandidos, nodos_generados=generados,
        milisegundos=(time.perf_counter() - t0) * 1000,
    )


ALGORITMOS = {
    "astar": a_estrella,
    "ucs": costo_uniforme,
    "voraz": voraz,
    "bfs": amplitud,
}
