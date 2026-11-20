"""
comparar_algoritmos.py - Comparación empírica de Ford–Fulkerson (DFS) y Edmonds–Karp (BFS).

Uso (desde la raíz del repositorio):  python scripts/comparar_algoritmos.py

1. Ejecuta ambas variantes sobre las redes de datos/ y muestra, para cada una,
   el valor del flujo, el número de caminos aumentantes y su largo promedio.
2. Repite la comparación sobre redes aleatorias más grandes (semilla fija, reproducible)
   con capacidades hasta 100, donde se nota la diferencia en el número de iteraciones.
Ambas variantes deben dar siempre el mismo valor máximo.
"""
import glob
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simulador.flujo import arcos_activos, edmonds_karp, ford_fulkerson_dfs  # noqa: E402


def medir(algoritmo, vertices, arcos, s, t):
    """Resultado: (valor, n.º de caminos aumentantes, largo promedio en arcos, tiempo en ms)."""
    inicio = time.perf_counter()
    valor, _, iteraciones = algoritmo(vertices, arcos, s, t)
    ms = (time.perf_counter() - inicio) * 1000
    largo = sum(len(c) - 1 for c, _ in iteraciones) / max(len(iteraciones), 1)
    return valor, len(iteraciones), largo, ms


def red_aleatoria(n, m, cap_max, semilla):
    """Resultado: (vertices, arcos) de una red dirigida aleatoria sin lazos,
    sin arcos repetidos ni recíprocos, con s = 0 y t = n - 1."""
    rnd = random.Random(semilla)
    arcos, usados = [], set()
    while len(arcos) < m:
        u, v = rnd.sample(range(n), 2)
        if v == 0 or u == n - 1 or (u, v) in usados or (v, u) in usados:
            continue
        usados.add((u, v))
        arcos.append((u, v, rnd.randint(1, cap_max)))
    return list(range(n)), arcos


def main():
    print("Redes del proyecto")
    print(f"{'red':32} {'algoritmo':10} {'valor':>5} {'caminos':>7} {'largo prom.':>11}")
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for ruta in sorted(glob.glob(os.path.join(raiz, "datos", "*.json"))):
        with open(ruta, encoding="utf-8") as f:
            g = json.load(f)
        vertices, arcos = [v["id"] for v in g["vertices"]], arcos_activos(g)
        for nombre, alg in (("FF-DFS", ford_fulkerson_dfs), ("EK-BFS", edmonds_karp)):
            valor, k, largo, _ = medir(alg, vertices, arcos, g["origen"], g["destino"])
            print(f"{os.path.basename(ruta):32} {nombre:10} {valor:5} {k:7} {largo:11.2f}")

    print("\nRedes aleatorias: 50 redes por tamaño, capacidades 1..100")
    print(f"{'|V|':>4} {'|E|':>4} {'algoritmo':10} {'caminos prom.':>13} {'caminos máx.':>12} {'ms prom.':>8}")
    for n, m in ((12, 30), (30, 120), (60, 300)):
        res = {"FF-DFS": [], "EK-BFS": []}
        for semilla in range(50):
            vertices, arcos = red_aleatoria(n, m, 100, semilla)
            v1 = medir(ford_fulkerson_dfs, vertices, arcos, 0, n - 1)
            v2 = medir(edmonds_karp, vertices, arcos, 0, n - 1)
            assert v1[0] == v2[0], "ambas variantes deben dar el mismo flujo máximo"
            res["FF-DFS"].append(v1)
            res["EK-BFS"].append(v2)
        for nombre, filas in res.items():
            ks = [r[1] for r in filas]
            ms = sum(r[3] for r in filas) / len(filas)
            print(f"{n:4} {m:4} {nombre:10} {sum(ks) / len(ks):13.1f} {max(ks):12} {ms:8.2f}")


if __name__ == "__main__":
    main()
