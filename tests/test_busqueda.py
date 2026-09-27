"""Pruebas de las estrategias de búsqueda y del sistema completo (red real del MIO)."""
import io
import os
import sys
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import main  # noqa: E402
from mio.busqueda import ProblemaRuta  # noqa: E402
from mio.sistema import SistemaMIO  # noqa: E402


class TestBusqueda(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = SistemaMIO()
        cls.estaciones = sorted(cls.s.red.nombres)
        # se resuelven una sola vez todos los pares origen-destino
        cls.pares = {}
        for o in cls.estaciones:
            for d in cls.estaciones:
                if o != d:
                    cls.pares[(o, d)] = (cls.s.buscar(o, d, "astar"), cls.s.buscar(o, d, "ucs"))

    def test_ruta_andres_sanin_universidades(self):
        """A* encuentra T40 hasta San Pascual + transbordo al expreso E21 (58.3 min)."""
        r = self.s.buscar("Andres Sanin", "Universidades", "astar")
        self.assertTrue(r.encontrado)
        self.assertAlmostEqual(r.minutos, 58.3)
        self.assertEqual(r.transbordos, 1)
        rutas = [p.hacia[1] for p in r.pasos if p.accion in ("abordar", "transbordo")]
        self.assertEqual(rutas, ["t40", "e21"])

    def test_red_conectada(self):
        """Existe ruta entre todos los pares de las 81 estaciones (6480 pares)."""
        self.assertEqual(len(self.pares), 81 * 80)
        self.assertTrue(all(a.encontrado for a, _ in self.pares.values()))

    def test_astar_optimo_en_todos_los_pares(self):
        """A* obtiene el mismo tiempo óptimo que costo uniforme en los 6480 pares."""
        for (o, d), (a, u) in self.pares.items():
            with self.subTest(origen=o, destino=d):
                self.assertAlmostEqual(a.minutos, u.minutos)

    def test_astar_expande_menos_nodos(self):
        """En total, A* expande al menos 25 % menos nodos que costo uniforme."""
        total_a = sum(a.nodos_expandidos for a, _ in self.pares.values())
        total_u = sum(u.nodos_expandidos for _, u in self.pares.values())
        self.assertLess(total_a, 0.75 * total_u)

    def test_heuristica_admisible(self):
        """h(n) nunca sobreestima el costo real (comparado con el óptimo de costo uniforme)."""
        for (o, d), (_, u) in self.pares.items():
            h = ProblemaRuta(self.s.red, o, d).heuristica((o, None))
            with self.subTest(origen=o, destino=d):
                self.assertLessEqual(h, u.minutos + 1e-9)

    def test_voraz_y_bfs_no_garantizan_optimo(self):
        """Cañaverales -> Popular: voraz (88.4) y BFS (82.1) son mucho más lentas que A* (51.3)."""
        a = self.s.buscar("canaverales", "popular", "astar")
        v = self.s.buscar("canaverales", "popular", "voraz")
        b = self.s.buscar("canaverales", "popular", "bfs")
        self.assertAlmostEqual(a.minutos, 51.3)
        self.assertGreater(v.minutos, a.minutos)
        self.assertGreater(b.minutos, a.minutos)

    def test_misma_estacion(self):
        """Si origen y destino coinciden, la ruta tiene 0 pasos y 0 minutos."""
        r = self.s.buscar("centro", "centro")
        self.assertTrue(r.encontrado)
        self.assertEqual((r.minutos, len(r.pasos)), (0, 0))

    def test_estacion_desconocida(self):
        """Una estación inexistente produce un error claro."""
        with self.assertRaises(ValueError):
            self.s.buscar("Marte", "centro")

    def test_criterio_menos_transbordos(self):
        """Aguablanca -> Univalle: por tiempo 57.6 min con 2 transbordos; por transbordos 63.1 min con 1."""
        t = self.s.buscar("aguablanca", "univalle", "astar", "tiempo")
        m = self.s.buscar("aguablanca", "univalle", "astar", "transbordos")
        self.assertEqual((round(t.minutos, 1), t.transbordos), (57.6, 2))
        self.assertEqual((round(m.minutos, 1), m.transbordos), (63.1, 1))


class TestContexto(unittest.TestCase):
    def test_estacion_cerrada_cambia_ruta(self):
        """Con San Pascual cerrada, el sistema cambia el transbordo a San Bosco (T47 + E21)."""
        s = SistemaMIO(cerradas=["San Pascual"])
        r = s.buscar("andres_sanin", "universidades")
        self.assertTrue(r.encontrado)
        self.assertNotIn("san_pascual", {p.hacia[0] for p in r.pasos})
        self.assertGreaterEqual(r.minutos, 58.3)

    def test_ruta_suspendida(self):
        """Si se suspenden T40 y T47, Andrés Sanín queda sin servicio y no hay ruta."""
        s = SistemaMIO(suspendidas=["t40", "t47"])
        self.assertFalse(s.buscar("andres_sanin", "centro").encontrado)


class TestCLI(unittest.TestCase):
    def _ejecutar(self, *args):
        buf = io.StringIO()
        with redirect_stdout(buf):
            codigo = main(list(args))
        return codigo, buf.getvalue()

    def test_cli_ruta(self):
        """El comando 'ruta' imprime el itinerario y el tiempo total."""
        codigo, salida = self._ejecutar("ruta", "andres_sanin", "universidades")
        self.assertEqual(codigo, 0)
        self.assertIn("Tiempo total estimado: 58.3 min", salida)

    def test_cli_comparar(self):
        """El comando 'comparar' muestra los cuatro algoritmos."""
        codigo, salida = self._ejecutar("comparar", "canaverales", "popular")
        self.assertEqual(codigo, 0)
        for nombre in ("A*", "Costo uniforme", "Voraz", "Amplitud"):
            self.assertIn(nombre, salida)

    def test_cli_consultar(self):
        """El comando 'consultar' responde consultas lógicas."""
        codigo, salida = self._ejecutar("consultar", "sirve(R, centro)")
        self.assertEqual(codigo, 0)
        self.assertIn("(6 respuesta(s))", salida)


if __name__ == "__main__":
    unittest.main(verbosity=2)
