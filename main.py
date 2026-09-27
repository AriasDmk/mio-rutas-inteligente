#!/usr/bin/env python3
"""
Sistema inteligente de rutas para el MIO (Cali) basado en reglas lógicas
y búsqueda heurística.

Ejemplos:
  python main.py estaciones
  python main.py ruta "Andres Sanin" Universidades
  python main.py ruta menga capri --algoritmo bfs
  python main.py ruta andres_sanin universidades --cerrar "San Pascual"
  python main.py ruta aguablanca univalle --criterio transbordos
  python main.py comparar canaverales popular
  python main.py consultar "transbordo(centro, t31, R)"
  python main.py explicar "costo_transbordo(unidad_deportiva, C)"
  python main.py reglas
"""

import argparse
import sys

from mio.busqueda import ALGORITMOS
from mio.logica import ErrorSintaxis, formatear_hecho
from mio.sistema import SistemaMIO

# Permite imprimir tildes en consolas de Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def _sistema(args) -> SistemaMIO:
    return SistemaMIO(cerradas=getattr(args, "cerrar", None) or [],
                      suspendidas=getattr(args, "suspender", None) or [])


def cmd_estaciones(args):
    s = _sistema(args)
    print(f"{'ID':<18} {'ESTACIÓN':<30} RUTAS")
    print("-" * 64)
    for e, nombre, rutas in s.listar_estaciones():
        print(f"{e:<18} {nombre:<30} {', '.join(r.upper() for r in rutas) or '(sin servicio)'}")
    print("\nRutas:")
    for r, nombre in sorted(s.red.nombres_ruta.items()):
        print(f"  {r.upper():<4} {nombre}  (espera promedio {s.red.espera[r]:g} min)")


def cmd_ruta(args):
    s = _sistema(args)
    res = s.buscar(args.origen, args.destino, args.algoritmo, args.criterio)
    o, d = s.resolver_estacion(args.origen), s.resolver_estacion(args.destino)
    print(f"\nMejor ruta de {s.red.nombres[o]} a {s.red.nombres[d]}")
    print(f"Algoritmo: {res.algoritmo} | Criterio: {args.criterio}")
    if args.cerrar:
        print(f"Estaciones cerradas: {', '.join(args.cerrar)}")
    if args.suspender:
        print(f"Rutas suspendidas: {', '.join(args.suspender)}")
    print("-" * 70)
    for linea in s.itinerario(res):
        print(linea)
    print(f"Nodos expandidos: {res.nodos_expandidos} | generados: {res.nodos_generados} "
          f"| {res.milisegundos:.2f} ms")
    if args.detalle and res.encontrado:
        print("\nSecuencia de estados (estación, ruta):")
        for p in res.pasos:
            print(f"  {p.accion:<11} {p.desde} -> {p.hacia}  (+{p.costo:g} min)")


def cmd_comparar(args):
    s = _sistema(args)
    resultados = s.comparar(args.origen, args.destino, args.criterio)
    o, d = s.resolver_estacion(args.origen), s.resolver_estacion(args.destino)
    print(f"\nComparación de estrategias: {s.red.nombres[o]} -> {s.red.nombres[d]}\n")
    print(f"{'Algoritmo':<17}{'Minutos':>8}{'Transb.':>9}{'Paradas':>9}{'Expand.':>9}{'Gener.':>8}{'ms':>8}")
    print("-" * 68)
    optimo = min((r.minutos for r in resultados if r.encontrado), default=None)
    for r in resultados:
        marca = " *" if r.encontrado and r.minutos == optimo else ""
        print(f"{r.algoritmo:<17}{r.minutos:>8g}{r.transbordos:>9}{r.paradas:>9}"
              f"{r.nodos_expandidos:>9}{r.nodos_generados:>8}{r.milisegundos:>8.2f}{marca}")
    print("\n* = menor tiempo encontrado. A* y costo uniforme siempre son óptimos;")
    print("  A* expande menos nodos gracias a la heurística admisible.")


def cmd_consultar(args):
    s = _sistema(args)
    respuestas = s.bc.consultar(args.consulta)
    if not respuestas:
        print("false.")
    for r in respuestas:
        print(", ".join(f"{k} = {v}" for k, v in r.items()) if r else "true.")
    print(f"\n({len(respuestas)} respuesta(s))")


def cmd_explicar(args):
    print(_sistema(args).bc.explicar(args.consulta))


def cmd_reglas(args):
    s = _sistema(args)
    print("Reglas de la base de conocimiento:\n")
    for r in s.bc.reglas:
        print(f"  R{r.numero:<3} {r}")
    res = s.bc.resumen()
    print(f"\nHechos base: {res['hechos_base']} | Reglas: {res['reglas']} | "
          f"Hechos derivados: {res['hechos_derivados']} | Total: {res['hechos_totales']}")


def construir_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Rutas inteligentes MIO: reglas lógicas + búsqueda heurística")
    sub = p.add_subparsers(dest="comando", required=True)

    def contexto(sp):
        sp.add_argument("--cerrar", nargs="*", metavar="ESTACION", help="estaciones cerradas")
        sp.add_argument("--suspender", nargs="*", metavar="RUTA", help="rutas suspendidas")

    sp = sub.add_parser("estaciones", help="lista estaciones y rutas")
    contexto(sp)
    sp.set_defaults(func=cmd_estaciones)

    sp = sub.add_parser("ruta", help="calcula la mejor ruta de A a B")
    sp.add_argument("origen")
    sp.add_argument("destino")
    sp.add_argument("--algoritmo", choices=list(ALGORITMOS), default="astar")
    sp.add_argument("--criterio", choices=["tiempo", "transbordos"], default="tiempo")
    sp.add_argument("--detalle", action="store_true", help="muestra la secuencia de estados")
    contexto(sp)
    sp.set_defaults(func=cmd_ruta)

    sp = sub.add_parser("comparar", help="compara A*, UCS, voraz y BFS")
    sp.add_argument("origen")
    sp.add_argument("destino")
    sp.add_argument("--criterio", choices=["tiempo", "transbordos"], default="tiempo")
    contexto(sp)
    sp.set_defaults(func=cmd_comparar)

    sp = sub.add_parser("consultar", help="consulta lógica, p. ej. \"sirve(R, centro)\"")
    sp.add_argument("consulta")
    contexto(sp)
    sp.set_defaults(func=cmd_consultar)

    sp = sub.add_parser("explicar", help="árbol de prueba de un hecho derivado")
    sp.add_argument("consulta")
    contexto(sp)
    sp.set_defaults(func=cmd_explicar)

    sp = sub.add_parser("reglas", help="muestra las reglas y estadísticas de inferencia")
    sp.set_defaults(func=cmd_reglas)
    return p


def main(argv=None) -> int:
    args = construir_parser().parse_args(argv)
    try:
        args.func(args)
    except (ValueError, ErrorSintaxis) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
