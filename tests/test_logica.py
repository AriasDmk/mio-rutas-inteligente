"""Pruebas del motor de inferencia lógica."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mio.logica import BaseConocimiento, ErrorSintaxis  # noqa: E402
from mio.sistema import RUTA_BC  # noqa: E402


class TestParser(unittest.TestCase):
    def test_hechos_y_reglas(self):
        """El analizador distingue hechos de reglas y reconoce números, cadenas y comentarios."""
        bc = BaseConocimiento()
        bc.cargar_texto("""
            % comentario
            padre(juan, ana).  edad(ana, 12).  nombre(ana, 'Ana María').
            abuelo(X, Z) :- padre(X, Y), padre(Y, Z).
        """)
        self.assertEqual(len(bc.base), 3)
        self.assertEqual(len(bc.reglas), 1)
        self.assertIn(("edad", "ana", 12), bc.base)
        self.assertIn(("nombre", "ana", "Ana María"), bc.base)

    def test_error_sintaxis(self):
        """Una cláusula mal escrita produce ErrorSintaxis."""
        with self.assertRaises(ErrorSintaxis):
            BaseConocimiento().cargar_texto("padre(juan, ana")


class TestInferencia(unittest.TestCase):
    def test_encadenamiento_hacia_adelante(self):
        """Se derivan hechos nuevos aplicando reglas encadenadas y recursivas."""
        bc = BaseConocimiento()
        bc.cargar_texto("""
            arista(a, b). arista(b, c). arista(c, d).
            camino(X, Y) :- arista(X, Y).
            camino(X, Z) :- arista(X, Y), camino(Y, Z).
        """)
        bc.inferir()
        self.assertTrue(bc.es_verdad("camino(a, d)"))
        self.assertFalse(bc.es_verdad("camino(d, a)"))
        self.assertEqual(len(bc.consultar("camino(a, X)")), 3)

    def test_negacion_por_fallo(self):
        """La negación (\\+) se evalúa después de completar el estrato del que depende."""
        bc = BaseConocimiento()
        bc.cargar_texto("""
            ave(piolin). ave(pingu). pinguino(pingu).
            no_vuela(X) :- pinguino(X).
            vuela(X) :- ave(X), \\+ no_vuela(X).
        """)
        self.assertTrue(bc.es_verdad("vuela(piolin)"))
        self.assertFalse(bc.es_verdad("vuela(pingu)"))

    def test_incorporados(self):
        """Los predicados incorporados distinto/2 y mitad/2 funcionan dentro de reglas."""
        bc = BaseConocimiento()
        bc.cargar_texto("""
            n(a). n(b). f(r, 10).
            par(X, Y) :- n(X), n(Y), distinto(X, Y).
            m(R, W) :- f(R, F), mitad(F, W).
        """)
        self.assertEqual(len(bc.consultar("par(X, Y)")), 2)
        self.assertEqual(bc.consultar("m(r, W)")[0]["W"], 5)


class TestBaseMIO(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bc = BaseConocimiento()
        cls.bc.cargar_archivo(RUTA_BC)
        cls.bc.inferir()

    def test_tramos_dirigidos(self):
        """Regla R1: los tramos son dirigidos, en el sentido real del recorrido (T40 va de Centro a La Ermita, no al revés)."""
        self.assertTrue(self.bc.es_verdad("conecta(t40, centro, la_ermita, T)"))
        self.assertFalse(self.bc.es_verdad("conecta(t40, la_ermita, centro, T)"))

    def test_datos_reales(self):
        """La base generada desde el SIUR contiene 81 estaciones y 9 rutas reales del MIO."""
        self.assertEqual(len(self.bc.consultar("estacion(E, N)")), 81)
        rutas = {r["C"] for r in self.bc.consultar("ruta(R, C, T)")}
        self.assertEqual(rutas, {"T31", "T40", "T47", "T50", "T57", "T62", "T12", "E21", "E37"})

    def test_transbordos_en_centro(self):
        """Regla R6: en Centro se puede transbordar entre las 6 rutas que lo sirven."""
        rutas = {r["R"] for r in self.bc.consultar("sirve(R, centro)")}
        self.assertEqual(rutas, {"t31", "t40", "t50", "t62", "e21", "e37"})
        self.assertEqual(len(self.bc.consultar("transbordo(centro, A, B)")), 30)

    def test_costo_transbordo_terminal(self):
        """Reglas R8-R9: transbordar en una terminal cuesta menos que en una estación."""
        self.assertEqual(self.bc.consultar("costo_transbordo(menga, C)")[0]["C"], 3)
        self.assertEqual(self.bc.consultar("costo_transbordo(centro, C)")[0]["C"], 5)

    def test_espera(self):
        """Regla R10: la espera promedio es la mitad de la frecuencia."""
        self.assertEqual(self.bc.consultar("espera(t31, W)")[0]["W"], 4)
        self.assertEqual(self.bc.consultar("espera(e21, W)")[0]["W"], 5)

    def test_alcanzabilidad_recursiva(self):
        """Reglas R12-R13: toda estación de la red es alcanzable desde Menga."""
        alcanzables = {r["X"] for r in self.bc.consultar("alcanzable(menga, X)")}
        estaciones = {r["E"] for r in self.bc.consultar("estacion(E, N)")}
        self.assertEqual(alcanzables, estaciones)

    def test_explicacion(self):
        """El sistema muestra el árbol de prueba de un hecho derivado."""
        arbol = self.bc.explicar("costo_transbordo(unidad_deportiva, C)")
        self.assertIn("R9", arbol)
        self.assertIn("[hecho]", arbol)

    def test_estacion_cerrada(self):
        """Reglas R3-R4: con Centro cerrada el T40 no se detiene allí, pero pasa de largo (San Pascual -> La Ermita)."""
        bc = BaseConocimiento()
        bc.cargar_archivo(RUTA_BC)
        bc.agregar_hecho("cerrada", "centro")
        self.assertFalse(bc.es_verdad("disponible(t40, san_pascual, centro, T)"))
        self.assertFalse(bc.es_verdad("estacion_transbordo(centro)"))
        r = bc.consultar("disponible(t40, san_pascual, la_ermita, T)")
        self.assertEqual(len(r), 1)
        self.assertAlmostEqual(r[0]["T"], 4.1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
