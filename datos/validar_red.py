"""
validar_red.py - Comprueba que una red cumple las reglas del enunciado.

Uso:  python datos/validar_red.py datos/red_principal.json

No calcula flujos (eso lo hace el algoritmo del proyecto); solo revisa la
estructura del grafo. Usa unicamente la biblioteca estandar de Python.
"""
import json
import sys


def cargar_red(ruta):
    """Entrada: ruta a un archivo JSON con el formato del proyecto.
    Resultado: (lista de ids de vertices, lista de arcos activos, origen, destino)."""
    with open(ruta, encoding="utf-8") as f:
        datos = json.load(f)
    vertices = [v["id"] for v in datos["vertices"]]
    arcos = [a for a in datos["arcos"] if a.get("activo", True)]
    return vertices, arcos, datos["origen"], datos["destino"]


def contar_caminos(arcos, s, t):
    """Entrada: arcos activos, origen s y destino t.
    Resultado: numero de caminos dirigidos simples distintos de s a t (DFS)."""
    sucesores = {}
    for a in arcos:
        sucesores.setdefault(a["u"], []).append(a["v"])

    def dfs(u, visitados):
        if u == t:
            return 1
        return sum(dfs(v, visitados | {v})
                   for v in sucesores.get(u, []) if v not in visitados)

    return dfs(s, {s})


def validar(vertices, arcos, s, t, inicial=True):
    """Entrada: vertices, arcos activos, s, t y si es la configuracion inicial
    (en ella se exigen 10-12 vertices y 15-20 arcos).
    Resultado: lista de errores encontrados (vacia si la red es valida)."""
    errores = []
    n, m = len(vertices), len(arcos)
    if inicial and not 10 <= n <= 12:
        errores.append(f"|V| = {n}, debe estar entre 10 y 12")
    if inicial and not 15 <= m <= 20:
        errores.append(f"|E| = {m}, debe estar entre 15 y 20")

    vistos = set()
    for a in arcos:
        u, v, c = a["u"], a["v"], a["cap"]
        if u not in vertices or v not in vertices:
            errores.append(f"Arco {u}->{v} usa un vertice inexistente")
        if u == v:
            errores.append(f"Lazo en {u}")
        if (u, v) in vistos:
            errores.append(f"Arco repetido {u}->{v}")
        if (v, u) in vistos:
            errores.append(f"Arcos reciprocos {u}<->{v}")
        if not (isinstance(c, int) and 1 <= c <= 12):
            errores.append(f"Capacidad invalida en {u}->{v}: {c}")
        vistos.add((u, v))

    usados = {a["u"] for a in arcos} | {a["v"] for a in arcos}
    for v in vertices:
        if v not in usados:
            errores.append(f"Vertice aislado: {v}")

    if s == t:
        errores.append("El origen y el destino deben ser distintos")
    elif contar_caminos(arcos, s, t) < 2:
        errores.append("Debe haber al menos 2 caminos dirigidos distintos de s a t")
    return errores


if __name__ == "__main__":
    ruta = sys.argv[1] if len(sys.argv) > 1 else "datos/red_principal.json"
    V, E, s, t = cargar_red(ruta)
    errores = validar(V, E, s, t)
    print(f"|V| = {len(V)}   |E| = {len(E)}   s = {s}   t = {t}")
    print(f"Caminos dirigidos simples de {s} a {t}: {contar_caminos(E, s, t)}")
    if errores:
        print("RED INVALIDA:")
        for e in errores:
            print("  -", e)
        sys.exit(1)
    print("Red valida: cumple todas las reglas del enunciado.")
