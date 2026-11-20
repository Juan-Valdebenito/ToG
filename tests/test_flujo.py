"""Pruebas del algoritmo de flujo máximo y corte mínimo.

Ejecutar desde la raíz del repositorio:  python -m unittest discover tests
"""
import json
import os
import unittest

from simulador.flujo import (arcos_activos, edmonds_karp, ford_fulkerson_dfs,
                             max_flow, verificar)

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def cargar(nombre):
    with open(os.path.join(RAIZ, "datos", nombre), encoding="utf-8") as f:
        return json.load(f)


class TestFlujo(unittest.TestCase):
    def comprobar(self, grafo, esperado):
        s, t = grafo["origen"], grafo["destino"]
        valor, x, S, T, corte = max_flow(grafo, s, t)
        self.assertEqual(valor, esperado)
        self.assertIn(s, S)
        self.assertIn(t, T)
        self.assertTrue(verificar(grafo, s, t, valor, x, corte)["ok"])
        return S, T, corte

    def test_ejemplo_enunciado(self):
        self.comprobar(cargar("red_ejemplo_enunciado.json"), 14)

    def test_red_principal(self):
        S, T, corte = self.comprobar(cargar("red_principal.json"), 22)
        self.assertEqual(sorted(T), ["G", "H", "T"])
        self.assertEqual(sorted((u, v) for u, v, _ in corte),
                         [("C", "G"), ("D", "H"), ("E", "H"), ("F", "G")])

    def test_configuraciones(self):
        for nombre, esperado in [("red_principal.json", 22),
                                 ("config_2_sin_DH.json", 15),
                                 ("config_3_nueva_ET.json", 25)]:
            with self.subTest(nombre=nombre):
                self.comprobar(cargar(nombre), esperado)

    def test_caso_manual(self):
        """Caso de verificación del apartado 5: resuelto a mano en docs/caso_manual.md."""
        g = cargar("caso_manual.json")
        S, T, corte = self.comprobar(g, 11)
        self.assertEqual(S, ["O", "A", "B"])
        self.assertEqual(T, ["C", "T"])
        self.assertEqual(corte, [("A", "C", 4), ("B", "C", 2), ("B", "T", 5)])

    def test_arco_desactivado_se_ignora(self):
        g = cargar("red_ejemplo_enunciado.json")
        for a in g["arcos"]:
            if (a["u"], a["v"]) == ("C", "T"):
                a["activo"] = False
        self.comprobar(g, 9)  # solo queda llegar a T por D -> T (9)

    def test_dfs_y_bfs_dan_el_mismo_valor(self):
        for nombre in ["red_ejemplo_enunciado.json", "red_principal.json",
                       "config_2_sin_DH.json", "config_3_nueva_ET.json"]:
            with self.subTest(nombre=nombre):
                g = cargar(nombre)
                V, E = [v["id"] for v in g["vertices"]], arcos_activos(g)
                self.assertEqual(ford_fulkerson_dfs(V, E, "O", "T")[0],
                                 edmonds_karp(V, E, "O", "T")[0])

    def test_sin_camino(self):
        g = {"vertices": [{"id": "s"}, {"id": "a"}, {"id": "t"}],
             "arcos": [{"u": "s", "v": "a", "cap": 5, "activo": True}]}
        valor, x, S, T, corte = max_flow(g, "s", "t")
        self.assertEqual(valor, 0)
        self.assertEqual(corte, [])


if __name__ == "__main__":
    unittest.main()
