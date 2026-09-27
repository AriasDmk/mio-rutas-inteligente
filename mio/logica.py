"""
Motor de inferencia lógica (encadenamiento hacia adelante).

Lee una base de conocimiento escrita en cláusulas de Horn con sintaxis
tipo Prolog, y deriva todos los hechos que se pueden concluir aplicando
las reglas hasta llegar a un punto fijo.

Soporta:
  * hechos:         tramo(t1, menga, chiminangos, 3).
  * reglas:         sirve(R, E) :- conecta(R, E, _, _).
  * negación por fallo:  \\+ cerrada(A)   (con estratificación automática)
  * predicados incorporados: distinto/2, igual/2, menor/2, mitad/2, suma/3
  * explicación: para cada hecho derivado se guarda qué regla y qué
    hechos lo produjeron, y se puede imprimir el árbol de prueba.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from itertools import count
from typing import Dict, Iterator, List, Optional, Set, Tuple


# ---------------------------------------------------------------------------
# Representación de términos
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Var:
    """Variable lógica (p. ej. X, Ruta, _G3)."""
    nombre: str

    def __repr__(self) -> str:
        return "_" if self.nombre.startswith("_G") else self.nombre


@dataclass(frozen=True)
class Literal:
    """Átomo lógico: predicado(arg1, ..., argN), opcionalmente negado."""
    predicado: str
    args: Tuple
    negado: bool = False

    @property
    def clave(self) -> Tuple[str, int]:
        return (self.predicado, len(self.args))

    def __repr__(self) -> str:
        txt = f"{self.predicado}({', '.join(_fmt(a) for a in self.args)})"
        return ("\\+ " + txt) if self.negado else txt


@dataclass(frozen=True)
class Regla:
    cabeza: Literal
    cuerpo: Tuple[Literal, ...]
    numero: int = 0

    def __repr__(self) -> str:
        return f"{self.cabeza} :- {', '.join(map(repr, self.cuerpo))}."


# Un hecho "aterrizado" se guarda como tupla: ('tramo', 't1', 'menga', 'chiminangos', 3)
Hecho = Tuple


def _fmt(valor) -> str:
    if isinstance(valor, str) and not re.fullmatch(r"[a-z][a-zA-Z0-9_]*", valor):
        return f"'{valor}'"
    return str(valor)


def formatear_hecho(hecho: Hecho) -> str:
    return f"{hecho[0]}({', '.join(_fmt(a) for a in hecho[1:])})"


# ---------------------------------------------------------------------------
# Analizador léxico y sintáctico
# ---------------------------------------------------------------------------

class ErrorSintaxis(Exception):
    pass


_TOKEN = re.compile(
    r"""
    (?P<espacio>\s+|%[^\n]*)            |
    (?P<si>:-)                          |
    (?P<neg>\\\+)                       |
    (?P<num>-?\d+(?:\.\d+)?)            |
    (?P<cadena>'[^']*')                 |
    (?P<nombre>[A-Za-z_][A-Za-z0-9_]*)  |
    (?P<simbolo>[(),.])
    """,
    re.VERBOSE,
)


def _tokenizar(texto: str) -> List[Tuple[str, str]]:
    tokens, pos = [], 0
    while pos < len(texto):
        m = _TOKEN.match(texto, pos)
        if not m:
            linea = texto.count("\n", 0, pos) + 1
            raise ErrorSintaxis(f"Carácter inesperado {texto[pos]!r} en la línea {linea}")
        tipo = m.lastgroup
        if tipo != "espacio":
            tokens.append((tipo, m.group()))
        pos = m.end()
    return tokens


class _Parser:
    def __init__(self, texto: str):
        self.tokens = _tokenizar(texto)
        self.i = 0
        self._anonimas = count()

    def _ver(self):
        return self.tokens[self.i] if self.i < len(self.tokens) else (None, None)

    def _esperar(self, valor: str):
        tipo, v = self._ver()
        if v != valor:
            raise ErrorSintaxis(f"Se esperaba '{valor}' y se encontró '{v}' (token {self.i})")
        self.i += 1

    def _termino(self):
        tipo, v = self._ver()
        self.i += 1
        if tipo == "num":
            return float(v) if "." in v else int(v)
        if tipo == "cadena":
            return v[1:-1]
        if tipo == "nombre":
            if v == "_":
                return Var(f"_G{next(self._anonimas)}")
            if v[0].isupper() or v[0] == "_":
                return Var(v)
            return v
        raise ErrorSintaxis(f"Término inválido: '{v}'")

    def _literal(self) -> Literal:
        negado = False
        if self._ver()[0] == "neg":
            negado = True
            self.i += 1
        tipo, nombre = self._ver()
        if tipo != "nombre" or not nombre[0].islower():
            raise ErrorSintaxis(f"Se esperaba un predicado y se encontró '{nombre}'")
        self.i += 1
        args = []
        if self._ver()[1] == "(":
            self.i += 1
            args.append(self._termino())
            while self._ver()[1] == ",":
                self.i += 1
                args.append(self._termino())
            self._esperar(")")
        return Literal(nombre, tuple(args), negado)

    def clausulas(self):
        while self.i < len(self.tokens):
            cabeza = self._literal()
            cuerpo: List[Literal] = []
            if self._ver()[0] == "si":
                self.i += 1
                cuerpo.append(self._literal())
                while self._ver()[1] == ",":
                    self.i += 1
                    cuerpo.append(self._literal())
            self._esperar(".")
            yield cabeza, tuple(cuerpo)

    def consulta(self) -> Tuple[Literal, ...]:
        lits = [self._literal()]
        while self._ver()[1] == ",":
            self.i += 1
            lits.append(self._literal())
        if self._ver()[1] == ".":
            self.i += 1
        if self.i != len(self.tokens):
            raise ErrorSintaxis("Texto sobrante al final de la consulta")
        return tuple(lits)


# ---------------------------------------------------------------------------
# Unificación
# ---------------------------------------------------------------------------

Sustitucion = Dict[Var, object]


def _resolver(t, s: Sustitucion):
    while isinstance(t, Var) and t in s:
        t = s[t]
    return t


def unificar(patron: Tuple, hecho: Tuple, s: Sustitucion) -> Optional[Sustitucion]:
    """Unifica los argumentos de un literal con los de un hecho aterrizado."""
    nueva = dict(s)
    for p, h in zip(patron, hecho):
        p = _resolver(p, nueva)
        if isinstance(p, Var):
            nueva[p] = h
        elif p != h:
            return None
    return nueva


def aplicar(args: Tuple, s: Sustitucion) -> Tuple:
    return tuple(_resolver(a, s) for a in args)


# ---------------------------------------------------------------------------
# Predicados incorporados
# ---------------------------------------------------------------------------

def _b_distinto(args, s):
    a, b = aplicar(args, s)
    if not isinstance(a, Var) and not isinstance(b, Var) and a != b:
        yield s


def _b_igual(args, s):
    r = unificar(args[:1], aplicar(args[1:], s), s)
    if r is not None:
        yield r


def _b_menor(args, s):
    a, b = aplicar(args, s)
    if not isinstance(a, Var) and not isinstance(b, Var) and a < b:
        yield s


def _b_mitad(args, s):
    a, b = aplicar(args, s)
    if isinstance(a, Var):
        return
    valor = a / 2
    r = unificar((b,), (valor,), s)
    if r is not None:
        yield r


def _b_suma(args, s):
    a, b, c = aplicar(args, s)
    if isinstance(a, Var) or isinstance(b, Var):
        return
    r = unificar((c,), (round(a + b, 6),), s)
    if r is not None:
        yield r


INCORPORADOS = {
    ("distinto", 2): _b_distinto,
    ("igual", 2): _b_igual,
    ("menor", 2): _b_menor,
    ("mitad", 2): _b_mitad,
    ("suma", 3): _b_suma,
}


# ---------------------------------------------------------------------------
# Base de conocimiento + motor de inferencia
# ---------------------------------------------------------------------------

class BaseConocimiento:
    """Almacena hechos y reglas; deriva conocimiento por encadenamiento hacia adelante."""

    def __init__(self):
        self.hechos: Dict[Tuple[str, int], Set[Hecho]] = {}
        self.base: Set[Hecho] = set()           # hechos escritos explícitamente
        self.reglas: List[Regla] = []
        self.origen: Dict[Hecho, Tuple[Regla, Tuple[Hecho, ...]]] = {}
        self._indice: Dict = {}
        self.inferido = False

    # ---- carga -----------------------------------------------------------
    def cargar_texto(self, texto: str) -> None:
        for cabeza, cuerpo in _Parser(texto).clausulas():
            if cuerpo:
                self.reglas.append(Regla(cabeza, cuerpo, len(self.reglas) + 1))
            else:
                self.agregar_hecho(cabeza.predicado, *cabeza.args)
        self.inferido = False

    def cargar_archivo(self, ruta: str) -> None:
        with open(ruta, encoding="utf-8") as f:
            self.cargar_texto(f.read())

    def agregar_hecho(self, predicado: str, *args) -> None:
        if any(isinstance(a, Var) for a in args):
            raise ValueError("Un hecho no puede contener variables")
        hecho = (predicado, *args)
        self.hechos.setdefault((predicado, len(args)), set()).add(hecho)
        self.base.add(hecho)
        self.inferido = False

    # ---- estratificación (necesaria por la negación) ---------------------
    def _estratos(self) -> List[List[Regla]]:
        predicados = {r.cabeza.clave for r in self.reglas}
        nivel = {p: 0 for p in predicados}
        for _ in range(len(predicados) + 1):
            cambio = False
            for r in self.reglas:
                h = r.cabeza.clave
                for lit in r.cuerpo:
                    if lit.clave in nivel:
                        requerido = nivel[lit.clave] + (1 if lit.negado else 0)
                        if nivel[h] < requerido:
                            nivel[h] = requerido
                            cambio = True
            if not cambio:
                break
        else:
            raise ValueError("La base de conocimiento no es estratificable (negación cíclica)")
        n = max(nivel.values(), default=0) + 1
        estratos: List[List[Regla]] = [[] for _ in range(n)]
        for r in self.reglas:
            estratos[nivel[r.cabeza.clave]].append(r)
        return estratos

    # ---- índices -----------------------------------------------------------
    @staticmethod
    def _indexar(conjuntos: Dict[Tuple[str, int], Set[Hecho]]):
        """Índice por el primer argumento: {clave: {valor_arg0: [hechos]}}."""
        indice: Dict[Tuple[str, int], Dict[object, List[Hecho]]] = {}
        for clave, hechos in conjuntos.items():
            d = indice.setdefault(clave, {})
            for h in hechos:
                if len(h) > 1:
                    d.setdefault(h[1], []).append(h)
        return indice

    def _candidatos(self, lit: Literal, s: Sustitucion, conjuntos, indice):
        if lit.args:
            primero = _resolver(lit.args[0], s)
            if not isinstance(primero, Var):
                return indice.get(lit.clave, {}).get(primero, ())
        return conjuntos.get(lit.clave, ())

    # ---- evaluación del cuerpo de una regla -------------------------------
    def _evaluar(self, cuerpo, s: Sustitucion, usados: Tuple[Hecho, ...],
                 pos: int = 0, delta=None, pos_delta: int = -1) -> Iterator:
        """Recorre los literales del cuerpo. Si pos_delta >= 0, el literal en esa
        posición solo se une con los hechos NUEVOS de la iteración anterior
        (evaluación semi-ingenua), lo que evita recalcular lo ya conocido."""
        if not cuerpo:
            yield s, usados
            return
        lit, resto = cuerpo[0], cuerpo[1:]
        if lit.clave in INCORPORADOS:
            for s2 in INCORPORADOS[lit.clave](lit.args, s):
                yield from self._evaluar(resto, s2, usados, pos + 1, delta, pos_delta)
        elif lit.negado:
            args = aplicar(lit.args, s)
            if any(isinstance(a, Var) for a in args):
                # negación con variables libres: "no existe ningún hecho que unifique"
                existe = any(unificar(args, h[1:], {}) is not None
                             for h in self.hechos.get(lit.clave, ()))
            else:
                existe = (lit.predicado, *args) in self.hechos.get(lit.clave, ())
            if not existe:
                yield from self._evaluar(resto, s, usados, pos + 1, delta, pos_delta)
        else:
            if pos == pos_delta:
                fuente = self._candidatos(lit, s, delta[0], delta[1])
            else:
                fuente = self._candidatos(lit, s, self.hechos, self._indice)
            for hecho in list(fuente):
                s2 = unificar(lit.args, hecho[1:], s)
                if s2 is not None:
                    yield from self._evaluar(resto, s2, usados + (hecho,), pos + 1, delta, pos_delta)

    def inferir(self) -> int:
        """Aplica todas las reglas hasta el punto fijo (evaluación semi-ingenua).
        Devuelve el número de hechos nuevos."""
        # se descartan derivaciones previas (por si cambiaron los hechos base)
        self.hechos = {}
        for h in self.base:
            self.hechos.setdefault((h[0], len(h) - 1), set()).add(h)
        self._indice = self._indexar(self.hechos)
        self.origen = {}
        nuevos_total = 0
        for estrato in self._estratos():
            primera = True
            delta_conj: Dict[Tuple[str, int], Set[Hecho]] = {}
            while True:
                nuevos = []
                for regla in estrato:
                    if primera:
                        variantes = [-1]            # primera pasada: todos los hechos
                    else:
                        variantes = [i for i, l in enumerate(regla.cuerpo)
                                     if not l.negado and l.clave not in INCORPORADOS
                                     and l.clave in delta_conj]
                    for pd in variantes:
                        delta = (delta_conj, delta_idx) if pd >= 0 else None
                        for s, usados in self._evaluar(regla.cuerpo, {}, (), 0, delta, pd):
                            args = aplicar(regla.cabeza.args, s)
                            if any(isinstance(a, Var) for a in args):
                                raise ValueError(f"Regla insegura (variable sin ligar en la cabeza): {regla}")
                            hecho = (regla.cabeza.predicado, *args)
                            if hecho not in self.hechos.get(regla.cabeza.clave, ()) and hecho not in self.origen:
                                self.origen[hecho] = (regla, usados)
                                nuevos.append((regla.cabeza.clave, hecho))
                primera = False
                if not nuevos:
                    break
                delta_conj = {}
                for clave, hecho in nuevos:
                    self.hechos.setdefault(clave, set()).add(hecho)
                    self._indice.setdefault(clave, {}).setdefault(hecho[1], []).append(hecho)
                    delta_conj.setdefault(clave, set()).add(hecho)
                delta_idx = self._indexar(delta_conj)
                nuevos_total += len(nuevos)
        self.inferido = True
        return nuevos_total

    # ---- consultas -------------------------------------------------------
    def _asegurar(self):
        if not self.inferido:
            self.inferir()

    def consultar(self, texto: str) -> List[Dict[str, object]]:
        """Consulta tipo Prolog, p. ej. "transbordo(centro, R1, R2)". Devuelve las ligaduras."""
        self._asegurar()
        literales = _Parser(texto).consulta()
        resultados, vistos = [], set()
        for s, _ in self._evaluar(literales, {}, ()):
            ligaduras = {v.nombre: _resolver(v, s) for v in s if not v.nombre.startswith("_")}
            clave = tuple(sorted(ligaduras.items(), key=lambda kv: kv[0]))
            if clave not in vistos:
                vistos.add(clave)
                resultados.append(ligaduras)
        return resultados

    def es_verdad(self, texto: str) -> bool:
        return bool(self.consultar(texto))

    def hechos_de(self, predicado: str, aridad: int) -> Set[Hecho]:
        self._asegurar()
        return set(self.hechos.get((predicado, aridad), set()))

    # ---- explicación -----------------------------------------------------
    def explicar(self, texto: str, profundidad_max: int = 6) -> str:
        """Árbol de prueba del primer hecho que satisface la consulta."""
        self._asegurar()
        lit = _Parser(texto).consulta()[0]
        for hecho in sorted(self.hechos.get(lit.clave, ()), key=str):
            if unificar(lit.args, hecho[1:], {}) is not None:
                lineas: List[str] = []
                self._arbol(hecho, 0, profundidad_max, lineas)
                return "\n".join(lineas)
        return f"No se puede demostrar: {texto}"

    def _arbol(self, hecho, nivel, maximo, lineas):
        sangria = "   " * nivel
        if hecho in self.origen:
            regla, usados = self.origen[hecho]
            lineas.append(f"{sangria}{formatear_hecho(hecho)}   <- R{regla.numero}: {regla}")
            if nivel < maximo:
                for u in usados:
                    self._arbol(u, nivel + 1, maximo, lineas)
        else:
            lineas.append(f"{sangria}{formatear_hecho(hecho)}   [hecho]")

    # ---- estadísticas ----------------------------------------------------
    def resumen(self) -> Dict[str, int]:
        self._asegurar()
        total = sum(len(v) for v in self.hechos.values())
        return {"hechos_base": len(self.base), "reglas": len(self.reglas),
                "hechos_derivados": total - len(self.base), "hechos_totales": total}
