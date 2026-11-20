"""
flujo.py - Flujo máximo (Edmonds–Karp) y corte mínimo, implementados con código propio.

Solo usa estructuras básicas de Python (dict, list, set y collections.deque como cola).
No se usa ninguna biblioteca que calcule flujos.

Formato de la red: el mismo JSON de datos/ (ver docs/tarea1_red_principal.md):
    {"vertices": [{"id": "O", ...}, ...],
     "arcos":    [{"u": "O", "v": "A", "cap": 10, "activo": true}, ...]}
Los arcos con "activo": false se ignoran en el cálculo.

Referencias:
- Edmonds, J. & Karp, R. M. (1972). Theoretical improvements in algorithmic efficiency
  for network flow problems. Journal of the ACM, 19(2), 248–264.
- Cormen, T. H., Leiserson, C. E., Rivest, R. L. & Stein, C. (2022). Introduction to
  Algorithms (4.ª ed.), cap. 24 "Maximum Flow". MIT Press.
- Ford, L. R. & Fulkerson, D. R. (1956). Maximal flow through a network.
  Canadian Journal of Mathematics, 8, 399–404.
"""
from collections import deque


def arcos_activos(grafo):
    """Entrada: red en formato JSON del proyecto.
    Resultado: lista de tuplas (u, v, cap) solo con los arcos activos."""
    return [(a["u"], a["v"], a["cap"]) for a in grafo["arcos"] if a.get("activo", True)]


def construir_residual(vertices, arcos):
    """Entrada: lista de ids de vértices y lista de arcos (u, v, cap).
    Resultado: diccionario residual[u][v] = capacidad residual de u hacia v.
    Al inicio residual[u][v] = c(u, v) y el arco inverso residual[v][u] = 0
    (el inverso permite "devolver" flujo en iteraciones posteriores).
    Como la red no tiene arcos recíprocos, el inverso nunca choca con un arco original."""
    residual = {v: {} for v in vertices}
    for u, v, cap in arcos:
        residual[u][v] = residual[u].get(v, 0) + cap
        residual[v].setdefault(u, 0)
    return residual


def bfs_camino_aumentante(residual, s, t):
    """Entrada: grafo residual, origen s y destino t.
    Resultado: diccionario padre (vértice -> predecesor en el árbol BFS) si existe
    un camino s -> t con capacidad residual positiva; None si no existe.
    La búsqueda en anchura encuentra el camino aumentante con menos arcos,
    lo que caracteriza a Edmonds–Karp y acota las iteraciones a O(|V|·|E|)."""
    padre = {s: None}
    cola = deque([s])
    while cola:
        u = cola.popleft()
        for v, cap in residual[u].items():
            if cap > 0 and v not in padre:
                padre[v] = u
                if v == t:
                    return padre
                cola.append(v)
    return None


def dfs_camino_aumentante(residual, s, t):
    """Entrada: grafo residual, origen s y destino t.
    Resultado: diccionario padre del camino encontrado, o None si no hay camino.
    Búsqueda en profundidad (pila explícita): devuelve el primer camino s -> t que
    encuentra, sin importar su largo. Es la variante clásica de Ford–Fulkerson y
    se usa solo para comparar con Edmonds–Karp (ver scripts/comparar_algoritmos.py)."""
    padre = {}
    pila = [(s, None)]
    while pila:
        u, p = pila.pop()
        if u in padre:
            continue
        padre[u] = p
        if u == t:
            return padre
        # se apilan en orden inverso para visitar los sucesores en su orden original
        for v, cap in reversed(list(residual[u].items())):
            if cap > 0 and v not in padre:
                pila.append((v, u))
    return None


def reconstruir_camino(padre, t):
    """Entrada: diccionario padre del BFS y el destino t.
    Resultado: lista de vértices del camino [s, ..., t]."""
    camino = [t]
    while padre[camino[-1]] is not None:
        camino.append(padre[camino[-1]])
    return camino[::-1]


def edmonds_karp(vertices, arcos, s, t):
    """Entrada: vértices, arcos activos (u, v, cap), origen s y destino t.
    Resultado: (valor, residual, iteraciones)
      valor       -> valor del flujo máximo |x|
      residual    -> grafo residual final (sirve para el flujo por arco y el corte)
      iteraciones -> lista de (camino, cuello_de_botella) de cada aumento, en orden.
    Es el método de Ford–Fulkerson eligiendo cada camino aumentante con BFS."""
    return caminos_aumentantes(vertices, arcos, s, t, bfs_camino_aumentante)


def ford_fulkerson_dfs(vertices, arcos, s, t):
    """Igual que edmonds_karp, pero eligiendo los caminos con DFS.
    Solo se usa para la comparación empírica entre ambas estrategias."""
    return caminos_aumentantes(vertices, arcos, s, t, dfs_camino_aumentante)


def caminos_aumentantes(vertices, arcos, s, t, buscar_camino):
    """Método de Ford–Fulkerson genérico.
    Entrada: vértices, arcos (u, v, cap), s, t y la función que busca un camino
    aumentante en el residual (BFS -> Edmonds–Karp, DFS -> Ford–Fulkerson clásico).
    Resultado: (valor, residual, iteraciones), como en edmonds_karp.
    Repite: buscar camino aumentante, calcular su cuello de botella,
    restar esa cantidad en los arcos del camino y sumarla en los inversos.
    Termina porque las capacidades son enteras: cada aumento suma al menos 1."""
    residual = construir_residual(vertices, arcos)
    valor = 0
    iteraciones = []
    while True:
        padre = buscar_camino(residual, s, t)
        if padre is None:
            break
        camino = reconstruir_camino(padre, t)
        cuello = min(residual[u][v] for u, v in zip(camino, camino[1:]))
        for u, v in zip(camino, camino[1:]):
            residual[u][v] -= cuello
            residual[v][u] += cuello
        valor += cuello
        iteraciones.append((camino, cuello))
    return valor, residual, iteraciones


def flujo_por_arco(arcos, residual):
    """Entrada: arcos originales (u, v, cap) y grafo residual final.
    Resultado: diccionario {(u, v): x(u, v)}.
    En un arco original el flujo es lo que se consumió de su capacidad:
    x(u, v) = c(u, v) - residual[u][v]."""
    return {(u, v): cap - residual[u][v] for u, v, cap in arcos}


def corte_minimo(vertices, arcos, residual, s):
    """Entrada: vértices, arcos originales, residual final y origen s.
    Resultado: (S, T, arcos_corte)
      S -> vértices alcanzables desde s en el residual (arcos con capacidad > 0)
      T -> el resto de los vértices
      arcos_corte -> arcos originales (u, v, cap) con u en S y v en T.
    Por el teorema de flujo máximo–corte mínimo, c(S, T) = valor del flujo máximo."""
    S = {s}
    cola = deque([s])
    while cola:
        u = cola.popleft()
        for v, cap in residual[u].items():
            if cap > 0 and v not in S:
                S.add(v)
                cola.append(v)
    T = [v for v in vertices if v not in S]
    S = [v for v in vertices if v in S]  # conserva el orden original
    corte = [(u, v, cap) for u, v, cap in arcos if u in S and v not in S]
    return S, T, corte


def max_flow(grafo, s, t):
    """Función principal (firma acordada en docs/tarea1_red_principal.md).
    Entrada: red en formato JSON del proyecto, origen s y destino t.
    Resultado: (valor, flujo_por_arco, S, T, arcos_corte)
      valor          -> flujo máximo
      flujo_por_arco -> {(u, v): x(u, v)} para cada arco activo
      S, T           -> partición de un corte mínimo
      arcos_corte    -> arcos (u, v, cap) que van de S a T"""
    vertices = [v["id"] for v in grafo["vertices"]]
    arcos = arcos_activos(grafo)
    valor, residual, _ = edmonds_karp(vertices, arcos, s, t)
    x = flujo_por_arco(arcos, residual)
    S, T, corte = corte_minimo(vertices, arcos, residual, s)
    return valor, x, S, T, corte


def verificar(grafo, s, t, valor, x, corte):
    """Entrada: red, s, t y los resultados de max_flow (valor, flujo x, arcos del corte).
    Resultado: diccionario con las comprobaciones del apartado 5 del enunciado:
      "capacidad"    -> lista de arcos que violan 0 <= x <= c (vacía si todo bien)
      "conservacion" -> {v: (entra, sale)} de los vértices intermedios que no conservan
      "valor_neto"   -> |x| = sale de s - entra a s
      "cap_corte"    -> c(S, T)
      "ok"           -> True si todo se cumple y valor = |x| = c(S, T)."""
    arcos = arcos_activos(grafo)
    fallos_cap = [(u, v) for u, v, c in arcos if not 0 <= x[(u, v)] <= c]

    entra, sale = {}, {}
    for (u, v), f in x.items():
        sale[u] = sale.get(u, 0) + f
        entra[v] = entra.get(v, 0) + f
    fallos_cons = {}
    for vert in (a["id"] for a in grafo["vertices"]):
        if vert in (s, t):
            continue
        if entra.get(vert, 0) != sale.get(vert, 0):
            fallos_cons[vert] = (entra.get(vert, 0), sale.get(vert, 0))

    valor_neto = sale.get(s, 0) - entra.get(s, 0)
    cap_corte = sum(c for _, _, c in corte)
    ok = not fallos_cap and not fallos_cons and valor == valor_neto == cap_corte
    return {"capacidad": fallos_cap, "conservacion": fallos_cons,
            "valor_neto": valor_neto, "cap_corte": cap_corte, "ok": ok}
