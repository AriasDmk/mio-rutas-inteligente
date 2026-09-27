"""
Sistema inteligente: une la base de conocimiento (reglas lógicas) con la
búsqueda heurística.

Flujo:
  1. Se carga la base de conocimiento (.pl) en el motor lógico.
  2. Se agregan hechos de contexto (estaciones cerradas, rutas suspendidas).
  3. El motor infiere el conocimiento derivado (disponible/4, espera/2, ...).
  4. Con esos hechos se construye la red (grafo) sobre la que se busca.
  5. El algoritmo elegido encuentra la mejor ruta de A a B.
"""

from __future__ import annotations

import os
import unicodedata
from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Set, Tuple

from .busqueda import ALGORITMOS, ProblemaRuta, Resultado, haversine_km
from .logica import BaseConocimiento

RUTA_BC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "conocimiento", "base_conocimiento.pl")


def _normalizar(texto: str) -> str:
    sin_tildes = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return "".join(c for c in sin_tildes.lower() if c.isalnum())


class Red:
    """Grafo construido exclusivamente a partir de hechos inferidos."""

    def __init__(self, bc: BaseConocimiento):
        self.nombres: Dict[str, str] = {h[1]: h[2] for h in bc.hechos_de("estacion", 2)}
        self.nombres_ruta: Dict[str, str] = {h[1]: h[2] for h in bc.hechos_de("ruta", 3)}
        self.coord: Dict[str, Tuple[float, float]] = {h[1]: (h[2], h[3]) for h in bc.hechos_de("coordenada", 3)}
        self.espera: Dict[str, float] = {h[1]: h[2] for h in bc.hechos_de("espera", 2)}
        self.costo_transbordo: Dict[str, float] = {h[1]: h[2] for h in bc.hechos_de("costo_transbordo", 2)}
        self._ady: Dict[Tuple[str, str], List[Tuple[str, float]]] = defaultdict(list)
        self._rutas: Dict[str, Set[str]] = defaultdict(set)
        for _, r, a, b, t in sorted(bc.hechos_de("disponible", 4)):
            self._ady[(a, r)].append((b, t))
        for _, r, e in bc.hechos_de("opera_en", 2):
            self._rutas[e].add(r)
        self.v_max_kmh = self._velocidad_maxima(bc)

    def _velocidad_maxima(self, bc) -> float:
        v = 1.0
        for _, r, a, b, t in bc.hechos_de("tramo", 4):
            if a in self.coord and b in self.coord and t > 0:
                v = max(v, haversine_km(*self.coord[a], *self.coord[b]) / (t / 60))
        return v

    def adyacentes(self, estacion: str, ruta: str) -> List[Tuple[str, float]]:
        return self._ady.get((estacion, ruta), [])

    def rutas_en(self, estacion: str) -> Set[str]:
        return self._rutas.get(estacion, set())

    def minutos_linea_recta(self, a: str, b: str) -> float:
        if a == b or a not in self.coord or b not in self.coord:
            return 0.0
        return haversine_km(*self.coord[a], *self.coord[b]) / self.v_max_kmh * 60


class SistemaMIO:
    def __init__(self, ruta_bc: str = RUTA_BC, cerradas: Iterable[str] = (),
                 suspendidas: Iterable[str] = ()):
        self.bc = BaseConocimiento()
        self.bc.cargar_archivo(ruta_bc)
        for e in cerradas:
            self.bc.agregar_hecho("cerrada", self.resolver_estacion(e))
        for r in suspendidas:
            self.bc.agregar_hecho("suspendida", self.resolver_ruta(r))
        self.bc.inferir()
        self.red = Red(self.bc)

    # ---- resolución de nombres escritos por el usuario --------------------
    def _estaciones_base(self) -> Dict[str, str]:
        return {h[1]: h[2] for h in self.bc.base if h[0] == "estacion"}

    def resolver_estacion(self, texto: str) -> str:
        estaciones = self._estaciones_base()
        clave = _normalizar(texto)
        exactas = [e for e, n in estaciones.items()
                   if clave in (_normalizar(e), _normalizar(n), _normalizar(n.replace("Terminal", "")))]
        if exactas:
            return exactas[0]
        parciales = [e for e, n in estaciones.items() if clave and clave in _normalizar(n)]
        if len(parciales) == 1:
            return parciales[0]
        sugerencia = f" ¿Quiso decir: {', '.join(estaciones[p] for p in parciales)}?" if parciales else ""
        raise ValueError(f"Estación desconocida: '{texto}'.{sugerencia}")

    def resolver_ruta(self, texto: str) -> str:
        rutas = {h[1] for h in self.bc.base if h[0] == "ruta"}
        if texto.lower() in rutas:
            return texto.lower()
        raise ValueError(f"Ruta desconocida: '{texto}'. Rutas: {', '.join(sorted(rutas))}")

    # ---- búsqueda --------------------------------------------------------
    def buscar(self, origen: str, destino: str, algoritmo: str = "astar",
               criterio: str = "tiempo") -> Resultado:
        o, d = self.resolver_estacion(origen), self.resolver_estacion(destino)
        if algoritmo not in ALGORITMOS:
            raise ValueError(f"Algoritmo desconocido: {algoritmo}. Opciones: {', '.join(ALGORITMOS)}")
        return ALGORITMOS[algoritmo](ProblemaRuta(self.red, o, d, criterio))

    def comparar(self, origen: str, destino: str, criterio: str = "tiempo") -> List[Resultado]:
        return [self.buscar(origen, destino, a, criterio) for a in ALGORITMOS]

    # ---- presentación ----------------------------------------------------
    def itinerario(self, res: Resultado) -> List[str]:
        """Convierte los pasos en instrucciones legibles, agrupando por tramo de bus."""
        if not res.encontrado:
            return ["No existe ruta entre las estaciones indicadas con las condiciones actuales."]
        if not res.pasos:
            return ["El origen y el destino son la misma estación: no necesita viajar."]
        n, nr = self.red.nombres, self.red.nombres_ruta
        lineas, i, k = [], 0, 1
        pasos = res.pasos
        while i < len(pasos):
            p = pasos[i]
            if p.accion in ("abordar", "transbordo"):
                ruta = p.hacia[1]
                espera = p.costo
                verbo = "Aborde" if p.accion == "abordar" else "Haga transbordo a"
                j, minutos, paradas = i + 1, 0.0, []
                while j < len(pasos) and pasos[j].accion == "viajar":
                    minutos += pasos[j].costo
                    paradas.append(n[pasos[j].hacia[0]])
                    j += 1
                if paradas:
                    lineas.append(
                        f"{k}. En {n[p.desde[0]]}: {verbo} la ruta {nr[ruta]} "
                        f"(espera/transbordo {espera:g} min). Viaje {len(paradas)} parada(s) "
                        f"hasta {paradas[-1]} ({minutos:g} min)."
                    )
                    if len(paradas) > 1:
                        lineas.append(f"     Paradas: {' -> '.join(paradas)}")
                    k += 1
                i = j
            else:
                i += 1
        lineas.append(f"Tiempo total estimado: {res.minutos:g} min | "
                      f"Transbordos: {res.transbordos} | Paradas recorridas: {res.paradas}")
        return lineas

    def listar_estaciones(self) -> List[Tuple[str, str, List[str]]]:
        return [(e, nombre, sorted(self.red.rutas_en(e)))
                for e, nombre in sorted(self.red.nombres.items(), key=lambda kv: kv[1])]
